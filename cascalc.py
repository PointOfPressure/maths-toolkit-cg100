# cascalc.py - integration + equation solving for the CAS.
# Symbolic integration (linearity, power rule, table, linear-argument sub) with
# a numeric solver (grid scan + bisection) as the general fallback. Uses
# caseng.evalf for all numeric work. Imported by cas.py.
import caseng
import caspoly

def has_var(n, var):
    t = n[0]
    if t == 'n':
        return False
    if t == 'v':
        return n[1] == var
    if len(n) == 2:
        return has_var(n[1], var)
    return has_var(n[1], var) or has_var(n[2], var)

def _const(n, var):
    # numeric value of a subtree that does not involve var, else None
    if has_var(n, var):
        return None
    try:
        v = caseng.evalf(n, 0.0)
    except:
        return None  # symbolic constant, or a domain error - not usable here
    return v

def _lin(n, var):
    # structural (a, b) for n == a*var + b, else None
    t = n[0]
    if t == 'v' and n[1] == var:
        return (1, 0)
    if t == 'neg':
        r = _lin(n[1], var)
        return None if r is None else (-r[0], -r[1])
    if t == '+' or t == '-':
        p = _lin(n[1], var)
        if p is None:
            return None
        q = _lin(n[2], var)
        if q is None:
            return None
        if t == '+':
            return (p[0] + q[0], p[1] + q[1])
        return (p[0] - q[0], p[1] - q[1])
    if t == '*':
        p = _lin(n[1], var)
        q = _lin(n[2], var)
        if p is None or q is None:
            return None
        if p[0] != 0 and q[0] != 0:
            return None  # var*var is quadratic, not linear
        if p[0] == 0:
            return (p[1] * q[0], p[1] * q[1])
        return (q[1] * p[0], q[1] * p[1])
    if t == '/':
        p = _lin(n[1], var)
        if p is None:
            return None
        d = _const(n[2], var)
        if d is None or d == 0:
            return None
        return (p[0] / d, p[1] / d)
    if t == '^':
        e = _const(n[2], var)
        if e == 1:
            return _lin(n[1], var)
        c = _const(n, var)
        return None if c is None else (0, c)
    c = _const(n, var)
    return None if c is None else (0, c)

def _ratio(n):
    # exponent as an exact fraction (p, q), else None. Keeps the power rule
    # exact for x^(2/3) instead of degrading to x^1.666667/1.666667.
    t = n[0]
    if t == 'n' and isinstance(n[1], int):
        return (n[1], 1)
    if t == 'neg':
        r = _ratio(n[1])
        return None if r is None else (-r[0], r[1])
    if t == '/' and n[1][0] == 'n' and n[2][0] == 'n':
        p = n[1][1]
        q = n[2][1]
        if isinstance(p, int) and isinstance(q, int) and q != 0:
            return (p, q) if q > 0 else (-p, -q)
    return None

def _powrule(a, p, q, coef):
    # int (a)^(p/q) d(var) with a = coef*var + c, coef != 0 and p/q != -1:
    #   = q * a^((p+q)/q) / ((p+q) * coef)
    num = p + q
    return ('/', ('*', ('n', q), ('^', a, ('/', ('n', num), ('n', q)))),
            ('n', num * coef))

def linear_coeff(arg, var):
    # returns (a, b) if arg == a*var + b (a, b constant), else None.
    # Decided structurally: sampling at x = 0, 1, 2 used to accept cubics such
    # as x^3-3x^2+3x (which agrees with y=x at all three points), and every
    # integral built on that substitution came out silently wrong.
    r = _lin(arg, var)
    if r is None:
        return None
    a, b = r
    ai = round(a)
    bi = round(b)
    if abs(ai - a) < 1e-9:
        a = int(ai)
    if abs(bi - b) < 1e-9:
        b = int(bi)
    return (a, b)

# --- integration by parts -------------------------------------------------
# int u dv = u v - int v du. The handheld's call stack is the binding limit
# here, not the algebra: integ already recurses on tree depth and each by-parts
# level nests another integ inside it, so the depth is capped. Three levels
# covers x^3 f(x), which is past anything the specification asks for.
BYPARTS_MAX = 3

def _liate(n, var):
    # LIATE ordering - the lower score becomes u, the factor we differentiate.
    # Logs and inverse trig simplify when differentiated, polynomials drop a
    # degree, and trig/exponentials are the ones worth integrating instead.
    t = n[0]
    if t in ('ln', 'log', 'logb'):
        return 0
    if t in ('asin', 'acos', 'atan', 'asinh', 'acosh', 'atanh'):
        return 1
    if t == 'n' or t == 'v':
        return 2
    if t == '^':
        return 2 if not has_var(n[2], var) else 6
    if t in ('sin', 'cos', 'tan'):
        return 3
    if t in ('exp', 'sinh', 'cosh'):
        return 4
    return 6  # not a factor we know how to split

def _cyclic(a, b, var):
    # int e^(px+q) sin(rx+s) dx and the cos form. Repeated by-parts cycles here
    # forever and never closes, so use the standard closed form:
    #   int e^(px) sin(rx) dx = e^(px)(p sin rx - r cos rx) / (p^2 + r^2)
    #   int e^(px) cos(rx) dx = e^(px)(p cos rx + r sin rx) / (p^2 + r^2)
    for E, T in ((a, b), (b, a)):
        if E[0] != 'exp' or T[0] not in ('sin', 'cos'):
            continue
        le = linear_coeff(E[1], var)
        lt = linear_coeff(T[1], var)
        if le is None or lt is None or le[0] == 0 or lt[0] == 0:
            continue
        p = le[0]
        r = lt[0]
        den = p * p + r * r
        if T[0] == 'sin':
            inner = ('-', ('*', ('n', p), ('sin', T[1])), ('*', ('n', r), ('cos', T[1])))
        else:
            inner = ('+', ('*', ('n', p), ('cos', T[1])), ('*', ('n', r), ('sin', T[1])))
        return ('/', ('*', E, inner), ('n', den))
    return None

def _flatten(n, out):
    # flatten a product/negation chain into a factor list, returning the sign
    if n[0] == '*':
        return _flatten(n[1], out) * _flatten(n[2], out)
    if n[0] == 'neg':
        return -_flatten(n[1], out)
    out.append(n)
    return 1

def _prod(v, du):
    # v * du gathered into a single quotient. Left as a plain product, an
    # intermediate like (x^2/2) * (1/x) never meets the rule that would cancel
    # it, and by parts stalls one step short of closing.
    nums = []
    dens = []
    for part in (v, du):
        p = part
        while p[0] == '/':
            dens.append(p[2])
            p = p[1]
        nums.append(p)
    node = ('*', nums[0], nums[1])
    den = None
    for d in dens:
        den = d if den is None else ('*', den, d)
    if den is not None:
        node = ('/', node, den)
    return caseng.simplify(node)

def _byparts(a, b, var, depth):
    if depth >= BYPARTS_MAX:
        return None
    u, dv = (a, b) if _liate(a, var) <= _liate(b, var) else (b, a)
    if _liate(u, var) >= 6:
        return None
    v = integ(dv, var, depth + 1)
    if v is None:
        return None
    try:
        du = caseng.simplify(caseng.diff(u, var))
        rest = _prod(v, du)
    except:
        return None
    if rest == ('n', 0):
        return ('*', u, v)
    # If what is left is a constant multiple of the integrand we started with,
    # by parts will cycle forever. Solve for it instead: I = uv - kI, so
    # I = uv/(1+k). This is what closes int sin(x)cos(x) dx.
    try:
        k = caseng.simplify(('/', rest, ('*', a, b)))
        if not has_var(k, var):
            den = caseng.simplify(('+', ('n', 1), k))
            if den != ('n', 0):
                return ('/', ('*', u, v), den)
    except:
        pass
    w = integ(rest, var, depth + 1)
    if w is None:
        return None
    return ('-', ('*', u, v), w)

# --- rational functions, via partial fractions ----------------------------
def _int_piece(top, fac, power, var):
    # integrate one partial-fraction term: numerator / factor^power, where the
    # factor is monic and either linear or an irreducible quadratic
    f = caspoly.poly(fac, var)
    if f is None:
        return None
    if len(f) == 2:
        # c / (x - r)^k
        c = caspoly.ratof(top)
        if c is None:
            return None
        if power == 1:
            return caseng.simplify(('*', caspoly.ratnode(c), ('ln', ('abs', fac))))
        # c/(x-r)^k integrates to -c / ((k-1)(x-r)^(k-1)); written as one
        # quotient it reads as -8/(3(x-1)) instead of 8/3*-(x-1)^(-1)
        cc = caspoly.rdiv(caspoly.rneg(c), (power - 1, 1))
        if cc is None:
            return None
        den = ('^', fac, ('n', power - 1))
        if cc[1] != 1:
            den = ('*', ('n', cc[1]), den)
        return caseng.simplify(('/', ('n', cc[0]), den))
    if len(f) == 3 and power == 1:
        # (Bx + C) / (x^2 + px + q) with q - p^2/4 > 0
        p = f[1]
        q = f[0]
        num = caspoly.poly(top, var)
        if num is None or len(num) > 2:
            return None
        C = num[0] if len(num) > 0 else caspoly.R0
        B = num[1] if len(num) > 1 else caspoly.R0
        half = (1, 2)
        k = caspoly.rsub(q, caspoly.rmul(caspoly.rmul(p, p), (1, 4)))
        if k is None or k[0] <= 0:
            return None      # not irreducible after all; a real factorisation exists
        # (B/2) ln(x^2+px+q)
        out = None
        if not caspoly.rzero(B):
            out = ('*', caspoly.ratnode(caspoly.rmul(B, half)), ('ln', fac))
        # (C - Bp/2) / sqrt(k) * atan((x + p/2)/sqrt(k))
        rest = caspoly.rsub(C, caspoly.rmul(caspoly.rmul(B, p), half))
        if not caspoly.rzero(rest):
            root = ('sqrt', caspoly.ratnode(k))
            shift = ('v', var)
            hp = caspoly.rmul(p, half)
            if not caspoly.rzero(hp):
                shift = ('+', shift, caspoly.ratnode(hp))
            piece = ('/', ('*', caspoly.ratnode(rest), ('atan', ('/', shift, root))), root)
            out = piece if out is None else ('+', out, piece)
        if out is None:
            return ('n', 0)
        return caseng.simplify(out)
    return None

def integ_rational(a, b, var, depth):
    # N(x)/D(x): split into a polynomial part plus partial fractions and
    # integrate each piece. This is what makes proper rational integrands work
    # at all - x/((x+1)(x-2)), 1/(x^2-1), 1/(1+x^2) - and it is also the step
    # that lets integration by parts finish x atan(x).
    res = caspoly.partial(a, b, var)
    if res is None:
        return None
    quot, terms = res
    out = None
    if quot is not None:
        F = integ(quot, var, depth)
        if F is None:
            return None
        out = F
    for top, fac, power in terms:
        F = _int_piece(top, fac, power, var)
        if F is None:
            return None
        out = F if out is None else ('+', out, F)
    return tidy(out)

def tidy(node):
    # Presentation pass for an answer that is about to be shown: cancel common
    # factors out of a quotient, fold constants, then gather like terms so a
    # negative coefficient prints as a subtraction. Kept out of integ itself,
    # which recurses - this runs once, at the end.
    try:
        return caspoly.collect(caspoly.cancel(caseng.simplify(node)))
    except:
        return caseng.simplify(node)

def integ(n, var='x', depth=0):
    t = n[0]
    if t == 'n':
        return ('*', n, ('v', var))
    if t == 'v':
        if n[1] == var:
            return ('/', ('^', ('v', var), ('n', 2)), ('n', 2))
        return ('*', n, ('v', var))
    if t == '+':
        a = integ(n[1], var, depth); b = integ(n[2], var, depth)
        return ('+', a, b) if a is not None and b is not None else None
    if t == '-':
        a = integ(n[1], var, depth); b = integ(n[2], var, depth)
        return ('-', a, b) if a is not None and b is not None else None
    if t == 'neg':
        a = integ(n[1], var, depth)
        return ('neg', a) if a is not None else None
    if t == '*':
        # Flatten first: after one round of by parts an integrand looks like
        # -cos(x) * (2*x), where neither side is constant but only two of the
        # three factors actually involve the variable.
        parts = []
        sign = _flatten(n, parts)
        consts = []
        moving = []
        for p in parts:
            (consts if not has_var(p, var) else moving).append(p)
        if len(moving) == 0:
            return None      # wholly constant; handled by the 'n'/'v' cases
        if len(moving) == 1:
            F = integ(moving[0], var, depth)
        elif len(moving) == 2:
            if moving[0] == moving[1]:
                # sin(x)*sin(x) is sin(x)^2; typing it either way has to give
                # the same answer, so hand it to the power branch
                F = integ(('^', moving[0], ('n', 2)), var, depth)
            else:
                F = None
            if F is None:
                F = _cyclic(moving[0], moving[1], var)
            if F is None:
                F = _byparts(moving[0], moving[1], var, depth)
        else:
            return None
        if F is None:
            return None
        k = ('n', sign)
        for c in consts:
            k = ('*', k, c)
        return F if k == ('n', 1) else ('*', k, F)
    if t == '/':
        a = n[1]; b = n[2]
        if not has_var(b, var):
            ia = integ(a, var, depth)
            return ('/', ia, b) if ia is not None else None
        # c / (px+q) -> c ln(px+q) / p  (covers 1/x, 3/x, 1/(2x+1), ...)
        if not has_var(a, var):
            lc = linear_coeff(b, var)
            if lc is not None and lc[0] != 0:
                # c/(p*var) is (c/p) ln(var), not (c/p) ln(p*var): the two
                # differ by a constant, but only the first is the answer a
                # student writes down
                inner = ('v', var) if lc[1] == 0 else b
                F = ('*', a, ('ln', inner))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
        # k f'(x) / f(x) -> k ln f(x). Tested by dividing the numerator by the
        # derivative of the denominator and asking whether the variable is gone.
        try:
            db = caseng.simplify(caseng.diff(b, var))
            if db != ('n', 0):
                k = caseng.simplify(('/', a, db))
                if not has_var(k, var):
                    F = ('ln', b)
                    return F if k == ('n', 1) else ('*', k, F)
        except:
            pass
        return integ_rational(a, b, var, depth)
    if t == '^':
        a = n[1]; b = n[2]
        # sin^2 and cos^2 have no elementary antiderivative term by term; the
        # double-angle form is how the specification asks for them:
        #   sin^2 u = (1 - cos 2u)/2 and cos^2 u = (1 + cos 2u)/2.
        # tan^2 u = sec^2 u - 1 integrates to tan(u)/k - x the same way.
        if b == ('n', 2) and a[0] in ('sin', 'cos', 'tan'):
            lc = linear_coeff(a[1], var)
            if lc is not None and lc[0] != 0:
                k = lc[0]
                dbl = ('+', ('*', ('n', 2 * k), ('v', var)), ('n', 2 * lc[1]))
                if a[0] == 'tan':
                    return ('-', ('/', ('tan', a[1]), ('n', k)), ('v', var))
                half = ('/', ('v', var), ('n', 2))
                wob = ('/', ('sin', dbl), ('n', 4 * k))
                return ('-', half, wob) if a[0] == 'sin' else ('+', half, wob)
        # read the exponent through _const so x^-1, x^(2/3) and x^pi all work
        # (the exponent tree is ('neg', ('n', 1)) here, not ('n', -1))
        e = _const(b, var)
        if e is not None:
            lc = linear_coeff(a, var)
            if lc is not None and lc[0] != 0:
                if e == -1:
                    # power rule breaks at -1: the integral is a logarithm
                    F = ('ln', a)
                    return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
                fr = _ratio(b)
                if fr is not None:
                    return _powrule(a, fr[0], fr[1], lc[0])
                p = e + 1
                return ('/', ('^', a, ('n', p)), ('n', p * lc[0]))
            # a negative power of something that is not linear, e.g.
            # (x^2+1)^-1, is a rational function - try partial fractions
            if e < 0 and e == int(e):
                return integ_rational(('n', 1), ('^', a, ('n', int(-e))), var, depth)
        return None
    arg = n[1]
    lc = linear_coeff(arg, var)
    if lc is None or lc[0] == 0:
        return None
    if t == 'sin':
        F = ('neg', ('cos', arg))
    elif t == 'cos':
        F = ('sin', arg)
    elif t == 'exp':
        F = ('exp', arg)
    elif t == 'sinh':
        F = ('cosh', arg)
    elif t == 'cosh':
        F = ('sinh', arg)
    elif t == 'tan':
        F = ('neg', ('ln', ('cos', arg)))
    elif t == 'sqrt':
        return _powrule(arg, 1, 2, lc[0])  # sqrt(u) is u^(1/2)
    elif t == 'ln':
        # int ln u du = u ln u - u
        F = ('-', ('*', arg, ('ln', arg)), arg)
    else:
        # a lone log or inverse-trig function integrates by parts against dv = 1,
        # which is how int atan(x) dx reaches x atan(x) - ln(1+x^2)/2
        if _liate(n, var) <= 1:
            return _byparts(n, ('n', 1), var, depth)
        return None
    return F if lc[0] == 1 else ('/', F, ('n', lc[0]))

def _at(tree, val, deg, var):
    # evaluate with `val` bound to `var`. evalf's positional argument is always
    # x, so anything solved or integrated in another letter has to go through
    # the env - without this, solve(v, 't') sampled a tree that mentions t with
    # only x bound, every sample raised, and it reported no roots at all.
    if var == 'x':
        return caseng.evalf(tree, val, deg)
    return caseng.evalf(tree, val, deg, {var: val})

def defint(tree, a, b, deg=False, n=200, var='x'):
    # numeric definite integral by composite Simpson's rule; None on domain error
    if n % 2:
        n += 1
    h = (b - a) / n
    try:
        s = _at(tree, a, deg, var) + _at(tree, b, deg, var)
        i = 1
        while i < n:
            v = _at(tree, a + i * h, deg, var)
            s += (4 if (i % 2) else 2) * v
            i += 1
    except:
        return None
    r = s * h / 3.0
    if r != r or r > 1.7e308 or r < -1.7e308:
        return None  # singularity inside a..b - report it rather than print junk
    return r

def _bisect(tree, a, b, deg=False, var='x'):
    try:
        fa = _at(tree, a, deg, var)
        fb = _at(tree, b, deg, var)
    except:
        return None
    if (fa < 0 and fb < 0) or (fa > 0 and fb > 0):
        return None
    i = 0
    while i < 60:
        m = (a + b) / 2
        try:
            fm = _at(tree, m, deg, var)
        except:
            return None
        if fm == 0 or (b - a) < 1e-7:
            return m
        if (fa < 0 and fm < 0) or (fa > 0 and fm > 0):
            a = m; fa = fm
        else:
            b = m; fb = fm
        i += 1
    return (a + b) / 2

MAXROOTS = 24
SAMPLES = 800

def _touch(tree, lo, hi, deg, var='x'):
    # ternary search for the minimum of |f| on [lo, hi]; used to catch roots the
    # curve only touches (x^2, (x-1)^2), which never produce a sign change.
    i = 0
    while i < 60 and (hi - lo) > 1e-9:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        try:
            f1 = _at(tree, m1, deg, var)
            f2 = _at(tree, m2, deg, var)
        except:
            return None
        if (f1 if f1 >= 0 else -f1) <= (f2 if f2 >= 0 else -f2):
            hi = m2
        else:
            lo = m1
        i += 1
    m = (lo + hi) / 2.0
    try:
        fm = _at(tree, m, deg, var)
    except:
        return None
    return m if -1e-9 < fm < 1e-9 else None

def _add(roots, r):
    if r is None:
        return
    for rr in roots:
        if abs(rr - r) < 1e-4:
            return
    roots.append(r)

def solve(tree, var='x', deg=False):
    # numeric roots of tree == 0; degrees needs a wider window (trig period 360)
    roots = []
    if not has_var(tree, var):
        return roots  # a constant is zero everywhere or nowhere - no isolated roots
    hi = 360.0 if deg else 20.0
    step = 2.0 * hi / SAMPLES
    # sample on a computed grid: repeated "x += 0.1" accumulated enough error
    # that x never landed exactly on 0, so touching roots were missed twice over
    ys = []
    i = 0
    while i <= SAMPLES:
        try:
            ys.append(_at(tree, -hi + i * step, deg, var))
        except:
            ys.append(None)
        i += 1
    i = 1
    while i <= SAMPLES and len(roots) < MAXROOTS:
        y = ys[i]
        p = ys[i - 1]
        if y is not None and p is not None:
            if (p <= 0 and y >= 0) or (p >= 0 and y <= 0):
                _add(roots, _bisect(tree, -hi + (i - 1) * step, -hi + i * step, deg, var))
            elif i + 1 <= SAMPLES and ys[i + 1] is not None:
                # same sign either side but a local minimum of |f| - a possible
                # tangential root, e.g. x^2 or (x-1)^2
                ay = y if y >= 0 else -y
                ap = p if p >= 0 else -p
                an = ys[i + 1] if ys[i + 1] >= 0 else -ys[i + 1]
                if ay < ap and ay < an:
                    _add(roots, _touch(tree, -hi + (i - 1) * step, -hi + (i + 1) * step, deg, var))
        i += 1
    roots.sort()
    return roots
