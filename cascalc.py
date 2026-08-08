# cascalc.py - integration + equation solving for the CAS.
# Symbolic integration (linearity, power rule, table, linear-argument sub) with
# a numeric solver (grid scan + bisection) as the general fallback. Uses
# caseng.evalf for all numeric work. Imported by cas.py.
import caseng

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

def integ(n, var='x'):
    t = n[0]
    if t == 'n':
        return ('*', n, ('v', var))
    if t == 'v':
        if n[1] == var:
            return ('/', ('^', ('v', var), ('n', 2)), ('n', 2))
        return ('*', n, ('v', var))
    if t == '+':
        a = integ(n[1], var); b = integ(n[2], var)
        return ('+', a, b) if a is not None and b is not None else None
    if t == '-':
        a = integ(n[1], var); b = integ(n[2], var)
        return ('-', a, b) if a is not None and b is not None else None
    if t == 'neg':
        a = integ(n[1], var)
        return ('neg', a) if a is not None else None
    if t == '*':
        a = n[1]; b = n[2]
        if not has_var(a, var):
            ib = integ(b, var)
            return ('*', a, ib) if ib is not None else None
        if not has_var(b, var):
            ia = integ(a, var)
            return ('*', b, ia) if ia is not None else None
        return None
    if t == '/':
        a = n[1]; b = n[2]
        if not has_var(b, var):
            ia = integ(a, var)
            return ('/', ia, b) if ia is not None else None
        # c / (px+q) -> c ln(px+q) / p  (covers 1/x, 3/x, 1/(2x+1), ...)
        if not has_var(a, var):
            lc = linear_coeff(b, var)
            if lc is not None and lc[0] != 0:
                F = ('*', a, ('ln', b))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
        return None
    if t == '^':
        a = n[1]; b = n[2]
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
        return None
    return F if lc[0] == 1 else ('/', F, ('n', lc[0]))

def defint(tree, a, b, deg=False, n=200):
    # numeric definite integral by composite Simpson's rule; None on domain error
    if n % 2:
        n += 1
    h = (b - a) / n
    try:
        s = caseng.evalf(tree, a, deg) + caseng.evalf(tree, b, deg)
        i = 1
        while i < n:
            v = caseng.evalf(tree, a + i * h, deg)
            s += (4 if (i % 2) else 2) * v
            i += 1
    except:
        return None
    r = s * h / 3.0
    if r != r or r > 1.7e308 or r < -1.7e308:
        return None  # singularity inside a..b - report it rather than print junk
    return r

def _bisect(tree, a, b, deg=False):
    try:
        fa = caseng.evalf(tree, a, deg)
        fb = caseng.evalf(tree, b, deg)
    except:
        return None
    if (fa < 0 and fb < 0) or (fa > 0 and fb > 0):
        return None
    i = 0
    while i < 60:
        m = (a + b) / 2
        try:
            fm = caseng.evalf(tree, m, deg)
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

def _touch(tree, lo, hi, deg):
    # ternary search for the minimum of |f| on [lo, hi]; used to catch roots the
    # curve only touches (x^2, (x-1)^2), which never produce a sign change.
    i = 0
    while i < 60 and (hi - lo) > 1e-9:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        try:
            f1 = caseng.evalf(tree, m1, deg)
            f2 = caseng.evalf(tree, m2, deg)
        except:
            return None
        if (f1 if f1 >= 0 else -f1) <= (f2 if f2 >= 0 else -f2):
            hi = m2
        else:
            lo = m1
        i += 1
    m = (lo + hi) / 2.0
    try:
        fm = caseng.evalf(tree, m, deg)
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
            ys.append(caseng.evalf(tree, -hi + i * step, deg))
        except:
            ys.append(None)
        i += 1
    i = 1
    while i <= SAMPLES and len(roots) < MAXROOTS:
        y = ys[i]
        p = ys[i - 1]
        if y is not None and p is not None:
            if (p <= 0 and y >= 0) or (p >= 0 and y <= 0):
                _add(roots, _bisect(tree, -hi + (i - 1) * step, -hi + i * step, deg))
            elif i + 1 <= SAMPLES and ys[i + 1] is not None:
                # same sign either side but a local minimum of |f| - a possible
                # tangential root, e.g. x^2 or (x-1)^2
                ay = y if y >= 0 else -y
                ap = p if p >= 0 else -p
                an = ys[i + 1] if ys[i + 1] >= 0 else -ys[i + 1]
                if ay < ap and ay < an:
                    _add(roots, _touch(tree, -hi + (i - 1) * step, -hi + (i + 1) * step, deg))
        i += 1
    roots.sort()
    return roots
