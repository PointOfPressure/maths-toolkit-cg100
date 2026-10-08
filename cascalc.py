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

def _symlin(arg, var):
    # the coefficient A of var in a linear arg holding other letters (a x + b)
    import casalg
    try:
        r = casalg.linin(caseng.simplify(arg), var)
    except Exception:
        return None
    if r is None or has_var(r[0], var) or r[0] == ('n', 0):
        return None
    return caseng.simplify(r[0])

def _over(F, k):
    # F / k where k is a number or a letter coefficient tree
    if isinstance(k, tuple):
        return F if k == ('n', 1) else ('/', F, k)
    return F if k == 1 else ('/', F, ('n', k))

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

_SYMOK = ('sin', 'cos', 'exp', 'sinh', 'cosh', 'tan', 'cot', 'sec', 'cosec',
          'tanh', 'sech', 'coth', 'ln')

def _monom(b, var):
    # b = c * var^k (k rational) -> (c tree, k rational pair), else None
    if b == ('v', var):
        return (('n', 1), (1, 1))
    r = caspoly.term_of(caseng.simplify(b))
    if r is None:
        return None
    c, facs = r
    k = None
    rest = []
    for key, base, e in facs:
        if base == ('v', var):
            k = (e, 1)
        elif base[0] == 'sqrt' and base[1] == ('v', var):
            k = (e, 2)
        elif base[0] == '^' and base[1] == ('v', var) and caseng._ratval(base[2]) is not None:
            q = caseng._ratval(base[2])
            k = caspoly.rmul(q, (e, 1))
        elif has_var(base, var):
            return None
        else:
            rest.append((key, base, e))
    if k is None:
        return None
    return (caspoly.term_node(c, rest), k)

def _xpow(k, var):
    return ('^', ('v', var), caspoly.ratnode(k))

def _mono(n, var):
    # x/e^x, ln x/x^2, (1+x)/sqrt x, sqrt(16x^3) -> sums of products with
    # var^k factors, the forms the rules below match
    t = n[0]
    if t in ('+', '-'):
        return (t, _mono(n[1], var), _mono(n[2], var))
    if t == 'neg':
        return ('neg', _mono(n[1], var))
    if t == '*':
        return ('*', _mono(n[1], var), _mono(n[2], var))
    if t == '/':
        b = n[2]
        if b[0] == 'exp':
            return _mono(('*', n[1], ('exp', ('neg', b[1]))), var)
        m = _monom(b, var) if has_var(b, var) else None
        if m is not None:
            inv = ('*', ('/', ('n', 1), m[0]), _xpow((-m[1][0], m[1][1]), var))
            a = n[1]
            if a[0] in ('+', '-'):
                return (a[0], _mono(('*', a[1], inv), var), _mono(('*', a[2], inv), var))
            return ('*', _mono(a, var), inv)
        return ('/', _mono(n[1], var), n[2])
    if t == 'sqrt' or (t == '^' and caseng._ratval(n[2]) is not None):
        p = (1, 2) if t == 'sqrt' else caseng._ratval(n[2])
        m = _monom(n[1], var) if has_var(n[1], var) else None
        if m is not None:
            return ('*', ('^', m[0], caspoly.ratnode(p)), _xpow(caspoly.rmul(m[1], p), var))
    return n

def _alts(n, var):
    # other forms of an integrand the rules may match
    out = []
    s = caseng.simplify(n)
    for f in (s, caspoly.expand(s)):
        if f != n and f not in out:
            out.append(f)
        g = _mono(f, var)
        if g != f and g not in out:
            out.append(g)
    return out

def _quadsurd(n, var):
    # P(x)/sqrt(A x^2 + B x + C) (P of degree <= 2) and sqrt(A x^2 + B x + C):
    # complete the square, u = x + B/2A, and use
    #   int 1/sqrt(q) = arsinh / arcosh / arcsin,  int u/sqrt(q) = sqrt(q)/A,
    #   int u^2/sqrt(q) = (u sqrt(q) - K int 1/sqrt(q))/(2A),
    #   int sqrt(q) = (u sqrt(q) + K int 1/sqrt(q))/2,  q = A u^2 + K
    t = caseng.simplify(n)
    coef, fl, cxc, out = caseng._termparts([(t, 1)])
    if fl is not None or cxc is not None:
        return None
    q = None
    pw = None
    rest = []
    for b, e in out:
        r = caseng._ratval(e)
        if b[0] == 'sqrt' and has_var(b, var):
            if q is not None or r is None or r[1] != 1 or abs(r[0]) != 1:
                return None
            q = b[1]
            pw = r[0]
        elif r is not None and r[1] == 2 and abs(r[0]) == 1 and has_var(b, var):
            if q is not None:
                return None
            q = b
            pw = r[0]
        else:
            rest.append([b, e])
    if q is None:
        return None
    Q = caspoly.poly(caseng.simplify(q), var)
    if Q is None or len(Q) != 3:
        return None
    Pt = caseng._termnode(coef, None, None, rest)
    P = caspoly.poly(Pt, var)
    if P is None or len(P) > 3 or (pw > 0 and len(P) > 1):
        return None
    C, B, A = Q
    rm = caspoly.rmul
    h = caspoly.rdiv(B, rm((2, 1), A))
    K = caspoly.rsub(C, rm(rm(h, h), A))
    if caspoly.rzero(K):
        return None
    x = ('v', var)
    u = ('+', x, caspoly.ratnode(h)) if not caspoly.rzero(h) else x
    sq = ('sqrt', q)
    root = lambda r: caseng._pow(caspoly.ratnode(r), ('/', ('n', 1), ('n', 2)))
    # I0 = int 1/sqrt(q) du
    if A[0] > 0 and K[0] > 0:
        I0 = ('/', ('asinh', ('*', u, root(caspoly.rdiv(A, K)))), root(A))
    elif A[0] > 0:
        I0 = ('/', ('acosh', ('*', u, root(caspoly.rdiv(A, caspoly.rneg(K))))), root(A))
    elif K[0] > 0:
        I0 = ('/', ('asin', ('*', u, root(caspoly.rdiv(caspoly.rneg(A), K)))), root(caspoly.rneg(A)))
    else:
        return None
    Kn = caspoly.ratnode(K)
    An = caspoly.ratnode(A)
    if pw > 0:
        c0 = caspoly.ratnode(P[0]) if P else ('n', 0)
        F = ('*', c0, ('/', ('+', ('*', u, sq), ('*', Kn, I0)), ('n', 2)))
        return caseng.simplify(F)
    # P(x) in powers of u: x = u - h
    while len(P) < 3:
        P = P + [caspoly.R0]
    p2 = P[2]
    p1 = caspoly.rsub(P[1], rm((2, 1), rm(P[2], h)))
    p0 = caspoly.radd(caspoly.rsub(P[0], rm(P[1], h)), rm(P[2], rm(h, h)))
    I1 = ('/', sq, An)
    I2 = ('/', ('-', ('*', u, sq), ('*', Kn, I0)), ('*', ('n', 2), An))
    F = ('+', ('+', ('*', caspoly.ratnode(p0), I0), ('*', caspoly.ratnode(p1), I1)),
         ('*', caspoly.ratnode(p2), I2))
    return caseng.simplify(F)

_ALT = [False]     # only the outermost integ() tries the other forms

def _sumfactor(n, var):
    # a product with a bracketed sum in var among its factors
    if n[0] != '*':
        return False
    parts = []
    _flatten(n, parts)
    moving = [p for p in parts if has_var(p, var)]
    sums = [p for p in moving if p[0] in ('+', '-')]
    rest = [p for p in moving if p[0] not in ('+', '-')]
    if len(sums) != 1 or not rest:
        return False
    for p in rest:
        if p[0] not in ('exp', 'sin', 'cos', 'sinh', 'cosh'):
            return False
    return True

def integ(n, var='x', depth=0):
    if _ALT[0]:
        return _integ(n, var, depth)
    _ALT[0] = True
    try:
        if _sumfactor(n, var):
            # (x-1)e^x: multiplied out first, by-parts on the bracket is slow
            r = _integ(caspoly.expand(caseng.simplify(n)), var, depth)
            if r is not None:
                return r
        r = _integ(n, var, depth)
        if r is not None:
            return r
        try:
            r = _quadsurd(n, var)
        except Exception:
            r = None
        if r is not None:
            return r
        for f in _alts(n, var):
            try:
                r = _integ(f, var, depth)
            except Exception:
                r = None
            if r is not None:
                return r
    finally:
        _ALT[0] = False
    return None

def _integ(n, var='x', depth=0):
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
                F = _factorform(moving[0], moving[1], var, depth)
            if F is None:
                F = _cyclic(moving[0], moving[1], var)
            if F is None:
                F = _usub(n, var, depth)
            if F is None:
                F = _byparts(moving[0], moving[1], var, depth)
            if F is None:
                return None
            return F if sign > 0 and not consts else _scaled(F, sign, consts)
        else:
            F = _usub(n, var, depth)
            return F
        if F is None:
            return None
        k = ('n', sign)
        for c in consts:
            k = ('*', k, c)
        return F if k == ('n', 1) else ('*', k, F)
    if t == '/':
        a = n[1]; b = n[2]
        if b[0] == '*' and not has_var(b[1], var):
            return integ(('/', ('/', a, b[1]), b[2]), var, depth)
        if b[0] == '*' and not has_var(b[2], var):
            return integ(('/', ('/', a, b[2]), b[1]), var, depth)
        if not has_var(b, var):
            ia = integ(a, var, depth)
            return ('/', ia, b) if ia is not None else None
        if not has_var(a, var):
            lc = linear_coeff(b, var)
            if lc is not None and lc[0] != 0:
                inner = ('v', var) if lc[1] == 0 else b
                F = ('*', a, ('ln', ('abs', inner)))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
            if lc is None:
                k = _symlin(b, var)
                if k is not None:
                    return _over(('*', a, ('ln', ('abs', b))), k)
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
                F = _invroot(a, b[1], var)
                if F is not None:
                    return F
                return integ(('*', a, ('^', b[1], ('/', ('n', -1), ('n', 2)))),
                             var, depth)
            if b[0] == '^':
                e = _const(b[2], var)
                if e is not None and e != 0:
                    return integ(('*', a, ('^', b[1], _negexp(b[2]))), var, depth)
        F = integ_rational(a, b, var, depth)
        if F is None:
            F = _usub(n, var, depth)
        return F
    if t == '^':
        a = n[1]; b = n[2]
        if not has_var(a, var) and has_var(b, var):
            lc = linear_coeff(b, var)
            if lc is not None and lc[0] != 0 and a != ('n', 0):
                F = ('/', n, ('ln', a))
                return F if lc[0] == 1 else ('/', F, ('n', lc[0]))
            if lc is None and a != ('n', 0):
                k = _symlin(b, var)
                if k is not None:
                    return _over(('/', n, ('ln', a)), k)
        if a[0] in ('sin', 'cos') and b[0] == 'n' and isinstance(b[1], int) \
                and b[1] >= 3 and b[1] % 2:
            F = _oddtrigpow(a, b[1], var, depth)
            if F is not None:
                return F
        if a[0] in ('tan', 'cot') and b[0] == 'n' and isinstance(b[1], int) \
                and b[1] >= 3:
            F = _tanpow(a, b[1], var, depth)
            if F is not None:
                return F
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
                F = _quadpow(a, int(-e), var)
                if F is not None:
                    return F
                F = integ_rational(('n', 1), ('^', a, ('n', int(-e))), var, depth)
                if F is not None:
                    return F
        return _usub(n, var, depth)
    arg = n[1]
    lc = linear_coeff(arg, var)
    if lc is None and t in _SYMOK:
        k = _symlin(arg, var)
        if k is not None:
            lc = (k, None)
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
    elif t == 'tanh':
        F = ('ln', ('cosh', arg))
    elif t == 'sech':
        F = ('*', ('n', 2), ('atan', ('exp', arg)))
    elif t == 'coth':
        F = ('ln', ('abs', ('sinh', arg)))
    elif t == 'sqrt' and not isinstance(lc[0], tuple):
        return _powrule(arg, 1, 2, lc[0])
    elif t == 'ln':
        F = ('-', ('*', arg, ('ln', arg)), arg)
    else:
        if _liate(n, var) <= 1:
            return _byparts(n, ('n', 1), var, depth)
        return _usub(n, var, depth)
    return _over(F, lc[0])

def _at(tree, val, deg, var):
    # evalf's positional arg is always x
    if var == 'x':
        return caseng.evalf(tree, val, deg)
    return caseng.evalf(tree, val, deg, {var: val})

def _rv(tree, val, deg, var):
    # a real sample for the root scans: complex or undefined raises
    v = _at(tree, val, deg, var)
    if isinstance(v, complex):
        if -1e-12 < v.imag < 1e-12:
            return v.real
        raise ValueError('complex')
    if v != v:
        raise ValueError('undefined')
    return v

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
        fa = _rv(tree, a, deg, var)
        fb = _rv(tree, b, deg, var)
    except:
        return None
    if (fa < 0 and fb < 0) or (fa > 0 and fb > 0):
        return None
    i = 0
    while i < 60:
        m = (a + b) / 2
        try:
            fm = _rv(tree, m, deg, var)
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
            f1 = _rv(tree, m1, deg, var)
            f2 = _rv(tree, m2, deg, var)
        except:
            return None
        if (f1 if f1 >= 0 else -f1) <= (f2 if f2 >= 0 else -f2):
            hi = m2
        else:
            lo = m1
        i += 1
    m = (lo + hi) / 2.0
    try:
        fm = _rv(tree, m, deg, var)
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

WIDE = 1e6         # the wide search reaches |x| = WIDE ...
OUTER = 100        # ... with this many log-spaced samples each side beyond 20
RANGE = [-20.0, 20.0]   # the interval the last solve() searched
_TRIG = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot')

def periodic(n, var='x'):
    # a trig function of var anywhere in the tree
    t = n[0]
    if t == 'n' or t == 'v':
        return False
    if t in _TRIG and has_var(n[1], var):
        return True
    if len(n) == 2:
        return periodic(n[1], var)
    return periodic(n[1], var) or periodic(n[2], var)

def _isroot(tree, r, fa, fb, deg, var):
    # a bisected sign change is a root, not a pole or a jump
    try:
        fr = _rv(tree, r, deg, var)
    except:
        return False
    big = fa if fa >= 0 else -fa
    nb = fb if fb >= 0 else -fb
    if nb > big:
        big = nb
    afr = fr if fr >= 0 else -fr
    return afr <= 1e-6 or afr <= 1e-6 * big

def _outer(tree, var, roots):
    # log-spaced scan of 20 < |x| < WIDE for sign changes
    ratio = (WIDE / 20.0) ** (1.0 / OUTER)
    for side in (1.0, -1.0):
        px = side * 20.0
        try:
            py = _rv(tree, px, False, var)
        except:
            py = None
        k = 1
        while k <= OUTER and len(roots) < MAXROOTS:
            x = side * 20.0 * ratio ** k
            try:
                y = _rv(tree, x, False, var)
            except:
                y = None
            # strict: where f underflows to 0 there is no root
            if y is not None and py is not None and ((py < 0 < y) or (py > 0 > y)):
                lo, hi = (px, x) if px < x else (x, px)
                r = _bisect(tree, lo, hi, False, var)
                if r is not None and _isroot(tree, r, py, y, False, var):
                    _add(roots, r)
            px = x
            py = y
            k += 1

def solve(tree, var='x', deg=False, wide=False):
    # sign-change scan of -20..20 (or +-360 degrees); wide also scans out to
    # +-WIDE when f has no trig function of x or nothing was found inside
    roots = []
    RANGE[0] = -360.0 if deg else -20.0
    RANGE[1] = -RANGE[0]
    if not has_var(tree, var):
        return roots
    roots = _inner(tree, var, deg)
    if wide and not deg and len(roots) < MAXROOTS and (not roots or not periodic(tree, var)):
        _outer(tree, var, roots)
        RANGE[0] = -WIDE
        RANGE[1] = WIDE
    i = 0
    while i < len(roots):
        roots[i] = _snap(tree, roots[i], deg, var)
        i += 1
    roots.sort()
    return roots

def _snap(tree, r, deg, var):
    # -4.77e-8 -> 0 when f is no further from 0 there
    try:
        fr = _rv(tree, r, deg, var)
        fr = fr if fr >= 0 else -fr
        for c in (0.0,):
            if c != r and -1e-6 < c - r < 1e-6:
                fc = _rv(tree, c, deg, var)
                if (fc if fc >= 0 else -fc) <= fr:
                    return c
    except:
        pass
    return r

def range_str(var='x'):
    # 'searched -20 <= x <= 20' for the last solve()
    if RANGE[1] == WIDE:
        return 'searched -10^6 <= ' + var + ' <= 10^6'
    return ('searched ' + str(int(RANGE[0])) + ' <= ' + var + ' <= ' +
            str(int(RANGE[1])))

def _inner(tree, var, deg):
    roots = []
    hi = 360.0 if deg else 20.0
    step = 2.0 * hi / SAMPLES
    ys = []
    i = 0
    while i <= SAMPLES:
        try:
            ys.append(_rv(tree, -hi + i * step, deg, var))
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


# ---- extra standard forms -------------------------------------------------

MAXSUB = 8         # candidate substitutions tried
SUBDEPTH = 2       # nesting allowed for substitution
BIG = 1e6          # probe used to spot a divergent improper integral

def _scaled(F, sign, consts):
    k = ('n', sign)
    for c in consts:
        k = ('*', k, c)
    return F if k == ('n', 1) else ('*', k, F)

def _oddtrigpow(a, m, var, depth):
    # sin^(2k+1) u = sin u (1 - cos^2 u)^k   (and the cos mirror)
    other = 'cos' if a[0] == 'sin' else 'sin'
    k = (m - 1) // 2
    body = ('-', ('n', 1), ('^', (other, a[1]), ('n', 2)))
    node = ('*', a, ('^', body, ('n', k)))
    try:
        node = caspoly.expand(node)
    except Exception:
        return None
    return integ(node, var, depth + 1)

def _tanpow(a, m, var, depth):
    # tan^m u = tan^(m-2) u (sec^2 u - 1)
    other = 'cosec' if a[0] == 'cot' else 'sec'
    sgn = -1 if a[0] == 'cot' else 1
    body = ('-', ('^', (other, a[1]), ('n', 2)), ('n', 1))
    node = ('*', ('^', a, ('n', m - 2)), body)
    if sgn < 0:
        node = ('neg', node)
    try:
        node = caspoly.expand(node)
    except Exception:
        return None
    return integ(node, var, depth + 1)

_FF = {('sin', 'cos'): (1, 1), ('cos', 'sin'): (1, -1),
       ('sin', 'sin'): (-1, 0), ('cos', 'cos'): (1, 0)}

def _factorform(a, b, var, depth):
    # sin ax cos bx etc. through the factor formulae
    if a[0] not in ('sin', 'cos') or b[0] not in ('sin', 'cos'):
        return None
    la = linear_coeff(a[1], var)
    lb = linear_coeff(b[1], var)
    if la is None or lb is None or la[0] == 0 or lb[0] == 0:
        return None
    S = ('+', a[1], b[1])
    D = ('-', a[1], b[1])
    h = ('n', 2)
    if a[0] == 'sin' and b[0] == 'cos':
        node = ('+', ('/', ('sin', S), h), ('/', ('sin', D), h))
    elif a[0] == 'cos' and b[0] == 'sin':
        node = ('-', ('/', ('sin', S), h), ('/', ('sin', D), h))
    elif a[0] == 'cos':
        node = ('+', ('/', ('cos', S), h), ('/', ('cos', D), h))
    else:
        node = ('-', ('/', ('cos', D), h), ('/', ('cos', S), h))
    return integ(caseng.simplify(node), var, depth + 1)

def _quadco(q, var):
    p = caspoly.poly(caseng.simplify(q), var)
    if p is None or len(p) != 3 or not caspoly.rzero(p[1]):
        return None
    return (p[2], p[0])

def _invroot(c, q, var):
    # c / sqrt(A x^2 + C) -> arcsin / arsinh / arcosh form
    co = _quadco(q, var)
    if co is None:
        return None
    A, C = co
    if caspoly.rzero(A):
        return None
    root = lambda r: caseng.simplify(('sqrt', caspoly.ratnode(r)))
    k = root(A if A[0] > 0 else caspoly.rneg(A))
    x = ('v', var)
    if A[0] < 0 and C[0] > 0:
        a = root(caspoly.rdiv(C, caspoly.rneg(A)))
        F = ('asin', ('/', x, a))
    elif A[0] > 0 and C[0] > 0:
        a = root(caspoly.rdiv(C, A))
        F = ('asinh', ('/', x, a))
    elif A[0] > 0 and C[0] < 0:
        a = root(caspoly.rdiv(caspoly.rneg(C), A))
        F = ('acosh', ('/', x, a))
    else:
        return None
    return caseng.simplify(('/', ('*', c, F), k))

def _cands(n, var, out):
    # every sub-expression holding var, innermost first
    t = n[0]
    if t == 'n' or t == 'v':
        return out
    if len(n) >= 2:
        _cands(n[1], var, out)
    if len(n) >= 3:
        _cands(n[2], var, out)
    if has_var(n, var) and n not in out:
        out.append(n)
    return out

def _usub(n, var, depth):
    # integral of g'(x) h(g(x)) by substituting u = g(x)
    if depth >= SUBDEPTH:
        return None
    whole = caseng.simplify(n)
    cands = _cands(whole, var, [])
    i = 0
    tried = 0
    while i < len(cands) and tried < MAXSUB:
        u = cands[i]
        i += 1
        if u == whole or u == ('v', var):
            continue
        tried += 1
        try:
            du = caseng.simplify(caseng.diff(u, var))
            if du == ('n', 0):
                continue
            k = caseng.simplify(('/', whole, du))
        except Exception:
            continue
        k2 = caseng.subst_tree(k, u, ('v', '_u'))
        if has_var(k2, var):
            continue
        F = integ(k2, '_u', depth + 1)
        if F is None:
            continue
        try:
            return caseng.simplify(caseng.subst(F, '_u', u))
        except Exception:
            continue
    return None

# ---- exact definite integrals --------------------------------------------

def _limval(F, var, a):
    try:
        return caseng.simplify(caseng.subst(F, var, caseng.simplify(a)))
    except Exception:
        return None

def _atinf(F, var, sgn):
    import casalg
    r = casalg.limit(F, var, None, sgn)
    if r is not None:
        return r
    probe = BIG * sgn
    try:
        v = caseng.evalf(F, probe, False, {var: probe})
    except Exception:
        return None
    if isinstance(v, complex) or v != v:
        return None
    try:
        v2 = caseng.evalf(F, probe * 10.0, False, {var: probe * 10.0})
    except Exception:
        return None
    if abs(v2) > abs(v) + 1e-3 and abs(v2) > 1.0:
        return 'div'
    if abs(v2 - v) > 1e-4 * (1.0 + abs(v)):
        return None
    ex = caseng.exactstr(v2, 1e-6)
    if ex is None:
        return ('n', v2)
    import caslex
    return caseng.simplify(caslex.parse(ex))

def defint_exact(tree, a, b, var='x'):
    # exact value of the definite integral, None when it cannot be done.
    # a or b may be the strings 'inf' / '-inf'.
    F = integ(tree, var)
    if F is None:
        return None
    F = tidy(F)
    vals = []
    for end, sgn in ((a, 1), (b, 1)):
        if end == 'inf':
            v = _atinf(F, var, 1)
        elif end == '-inf':
            v = _atinf(F, var, -1)
        else:
            v = _limval(F, var, end)
            if v is not None and caseng.vars_in(v):
                v = None
            if v is not None:
                try:
                    caseng.evalf(v, 0.0)
                except Exception:
                    import casalg
                    v = casalg.limit(F, var, caseng.simplify(end))
        if v == 'div':
            raise ValueError('the integral diverges')
        if v is None:
            return None
        vals.append(v)
    return tidy(('-', vals[1], vals[0]))

def volume(f, a, b, var='x'):
    return defint_exact(caseng.simplify(('*', ('v', 'pi'), ('^', f, ('n', 2)))),
                        a, b, var)

def meanvalue(f, a, b, var='x'):
    v = defint_exact(f, a, b, var)
    if v is None:
        return None
    return tidy(('/', v, ('-', caseng.simplify(b), caseng.simplify(a))))

def arclength(f, a, b, var='x'):
    d = caseng.simplify(caseng.diff(f, var))
    g = caseng.simplify(('sqrt', ('+', ('n', 1), ('^', d, ('n', 2)))))
    return defint_exact(g, a, b, var)

# ---- implicit and parametric differentiation ------------------------------

def diff_implicit(lhs, rhs, xv='x', yv='y'):
    F = caseng.simplify(('-', lhs, rhs))
    fx = caseng.simplify(caseng.diff(F, xv))
    fy = caseng.simplify(caseng.diff(F, yv))
    if fy == ('n', 0):
        return None
    return tidy(('neg', ('/', fx, fy)))

def diff_param(xt, yt, tv='t'):
    dx = caseng.simplify(caseng.diff(xt, tv))
    if dx == ('n', 0):
        return None
    return tidy(('/', caseng.diff(yt, tv), dx))


MAXRED = 6         # reduction-formula depth for 1/(A x^2 + C)^n

def _quadpow(q, n, var):
    # int dx / (A x^2 + C)^n by the standard reduction formula
    if n < 1 or n > MAXRED:
        return None
    co = _quadco(q, var)
    if co is None:
        return None
    A, C = co
    if A[0] <= 0 or C[0] <= 0:
        return None
    a2 = caspoly.rdiv(C, A)
    root = caseng.simplify(('sqrt', caspoly.ratnode(a2)))
    x = ('v', var)
    base = ('+', ('^', x, ('n', 2)), caspoly.ratnode(a2))
    F = ('/', ('atan', ('/', x, root)), root)
    k = 2
    while k <= n:
        c1 = caspoly.rdiv(caspoly.R1, caspoly.rmul((2 * (k - 1), 1), a2))
        c2 = caspoly.rmul(caspoly.rdiv((2 * k - 3, 1), (2 * (k - 1), 1)),
                          caspoly.rdiv(caspoly.R1, a2))
        F = ('+', ('*', caspoly.ratnode(c1),
                   ('/', x, ('^', base, ('n', k - 1)))),
             ('*', caspoly.ratnode(c2), F))
        k += 1
    scale = caspoly.rdiv(caspoly.R1, (A[0] ** n, A[1] ** n))
    if scale is None:
        return None
    return tidy(('*', caspoly.ratnode(scale), F))
