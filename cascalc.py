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
    if has_var(n, var):
        return None
    try:
        v = caseng.evalf(n, 0.0)
    except:
        return None
    return v

def _lin(n, var):
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
            return None
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

def _negexp(n):
    if n[0] == 'n':
        return ('n', -n[1])
    if n[0] == 'neg':
        return n[1]
    if n[0] == '/' and n[1][0] == 'n' and n[2][0] == 'n':
        return ('/', ('n', -n[1][1]), n[2])
    return ('neg', n)

def _powrule(a, p, q, coef):
    num = p + q
    return ('/', ('*', ('n', q), ('^', a, ('/', ('n', num), ('n', q)))),
            ('n', num * coef))

def linear_coeff(arg, var):
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

BYPARTS_MAX = 3

def _liate(n, var):
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
    return 6

def _cyclic(a, b, var):
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
    if n[0] == '*':
        return _flatten(n[1], out) * _flatten(n[2], out)
    if n[0] == 'neg':
        return -_flatten(n[1], out)
    out.append(n)
    return 1

def _prod(v, du):
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

def _int_piece(top, fac, power, var):
    f = caspoly.poly(fac, var)
    if f is None:
        return None
    if len(f) == 2:
        c = caspoly.ratof(top)
        if c is None:
            return None
        if power == 1:
            return caseng.simplify(('*', caspoly.ratnode(c), ('ln', ('abs', fac))))
        cc = caspoly.rdiv(caspoly.rneg(c), (power - 1, 1))
        if cc is None:
            return None
        den = ('^', fac, ('n', power - 1))
        if cc[1] != 1:
            den = ('*', ('n', cc[1]), den)
        return caseng.simplify(('/', ('n', cc[0]), den))
    if len(f) == 3 and power == 1:
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
            return None
        out = None
        if not caspoly.rzero(B):
            out = ('*', caspoly.ratnode(caspoly.rmul(B, half)), ('ln', fac))
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
        parts = []
        sign = _flatten(n, parts)
        consts = []
        moving = []
        for p in parts:
            (consts if not has_var(p, var) else moving).append(p)
        if len(moving) == 0:
            return None
        if len(moving) == 1:
            F = integ(moving[0], var, depth)
        elif len(moving) == 2:
            if moving[0] == moving[1]:
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
        if not has_var(a, var):
            lc = linear_coeff(b, var)
            if lc is not None and lc[0] != 0:
                inner = ('v', var) if lc[1] == 0 else b
                F = ('*', a, ('ln', ('abs', inner)))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
        try:
            db = caseng.simplify(caseng.diff(b, var))
            if db != ('n', 0):
                k = caseng.simplify(('/', a, db))
                if not has_var(k, var):
                    F = ('ln', ('abs', b))
                    return F if k == ('n', 1) else ('*', k, F)
        except:
            pass
        if not has_var(a, var):
            if b[0] == 'sqrt':
                return integ(('*', a, ('^', b[1], ('/', ('n', -1), ('n', 2)))),
                             var, depth)
            if b[0] == '^':
                e = _const(b[2], var)
                if e is not None and e != 0:
                    return integ(('*', a, ('^', b[1], _negexp(b[2]))), var, depth)
        return integ_rational(a, b, var, depth)
    if t == '^':
        a = n[1]; b = n[2]
        if b == ('n', 2) and a[0] in ('sec', 'cosec', 'sech'):
            lc = linear_coeff(a[1], var)
            if lc is not None and lc[0] != 0:
                if a[0] == 'sec':
                    F = ('tan', a[1])
                elif a[0] == 'sech':
                    F = ('tanh', a[1])
                else:
                    F = ('neg', ('cot', a[1]))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
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
        e = _const(b, var)
        if e is not None:
            lc = linear_coeff(a, var)
            if lc is not None and lc[0] != 0:
                if e == -1:
                    F = ('ln', ('abs', a))
                    return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
                fr = _ratio(b)
                if fr is not None:
                    return _powrule(a, fr[0], fr[1], lc[0])
                p = e + 1
                return ('/', ('^', a, ('n', p)), ('n', p * lc[0]))
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
        F = ('neg', ('ln', ('abs', ('cos', arg))))
    elif t == 'cot':
        F = ('ln', ('abs', ('sin', arg)))
    elif t == 'sec':
        F = ('ln', ('abs', ('+', ('sec', arg), ('tan', arg))))
    elif t == 'cosec':
        F = ('neg', ('ln', ('abs', ('+', ('cosec', arg), ('cot', arg)))))
    elif t == 'sech':
        F = ('*', ('n', 2), ('atan', ('exp', arg)))
    elif t == 'coth':
        F = ('ln', ('abs', ('sinh', arg)))
    elif t == 'sqrt':
        return _powrule(arg, 1, 2, lc[0])
    elif t == 'ln':
        F = ('-', ('*', arg, ('ln', arg)), arg)
    else:
        if _liate(n, var) <= 1:
            return _byparts(n, ('n', 1), var, depth)
        return None
    return F if lc[0] == 1 else ('/', F, ('n', lc[0]))

def _at(tree, val, deg, var):
    # evalf's positional arg is always x
    if var == 'x':
        return caseng.evalf(tree, val, deg)
    return caseng.evalf(tree, val, deg, {var: val})

def defint(tree, a, b, deg=False, n=200, var='x'):
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
        return None
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
    roots = []
    if not has_var(tree, var):
        return roots
    hi = 360.0 if deg else 20.0
    step = 2.0 * hi / SAMPLES
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
                ay = y if y >= 0 else -y
                ap = p if p >= 0 else -p
                an = ys[i + 1] if ys[i + 1] >= 0 else -ys[i + 1]
                if ay < ap and ay < an:
                    _add(roots, _touch(tree, -hi + (i - 1) * step, -hi + (i + 1) * step, deg, var))
        i += 1
    roots.sort()
    return roots
