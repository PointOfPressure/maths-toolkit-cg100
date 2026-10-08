# AQA 7357 sections G-J: differentiation, integration, numerical methods and
# vectors. Each tool takes the parsed fields and returns result lines.
import math
import caseng
import cascalc
import caspoly
import casalg
import casutil

X = ('v', 'x')
LO = -20.0        # cascalc.solve only searches this window
HI = 20.0

_w = casutil.w
_warn = casutil.warn
_m = casutil.m
_mw = casutil.mw
_f = casutil.fmt
_ts = caseng.tostr

# ---- shared helpers ---------------------------------------------------------

def _g(v):
    # 8 s.f. plain decimal: iteration tables need more than 3 s.f.
    return casutil.fmt(v, 8)

def _chk(t, allowed):
    for v in caseng.vars_in(t):
        if v not in allowed:
            raise ValueError('unexpected ' + v)
    return t

def _diff(t, var='x'):
    # the engine's derivative, checked against a numeric one: when its
    # tidied form is off, the quotient-rule form or the raw form is used
    plain = var == 'x' and caseng.vars_in(t) in ([], ['x'])
    if plain:
        try:
            q = _qrule(t)
        except Exception:
            q = None
        if q is not None and _isderiv(q, t):
            return q
    raw = caseng.diff(t, var)
    d = cascalc.tidy(raw)
    if not plain or _isderiv(d, t):
        return d
    if _isderiv(raw, t):
        return raw
    return d

def _val(t, xv, env=None):
    return casutil.real(casutil.ev(t, xv, env))

def _z(v):
    if -1e-12 < v < 1e-12:
        return 0.0
    return v

def _lin(mg, c):
    return cascalc.tidy(('+', ('*', ('n', _z(mg)), X), ('n', _z(c))))

def _pt(x, y):
    return '(' + _f(x) + ', ' + _f(y) + ')'

def _near(r):
    n = int(r + 0.5) if r >= 0 else -int(0.5 - r)
    if -1e-8 < r - n < 1e-8:
        return n * 1.0
    return r

def _polish(f, df, r):
    # solve() bisects to ~1e-7; Newton steps give fmt enough digits to be exact
    i = 0
    while i < 5:
        fv = casutil.evx(f, r)
        dv = casutil.evx(df, r)
        if fv is None or dv is None or dv == 0:
            break
        s = fv / dv
        if s > 1.0 or s < -1.0:
            break
        r = r - s
        i += 1
    return _near(r)

def _bis(f, a, b):
    fa = casutil.evx(f, a)
    if fa is None:
        return (a + b) / 2.0
    i = 0
    while i < 50 and b - a > 1e-12:
        mid = (a + b) / 2.0
        fm = casutil.evx(f, mid)
        if fm is None:
            break
        if fm == 0:
            return mid
        if (fa < 0 and fm < 0) or (fa > 0 and fm > 0):
            a = mid
            fa = fm
        else:
            b = mid
        i += 1
    return (a + b) / 2.0

def _scan(f, a, b, n):
    # sign-change roots inside [a, b]; evx skips complex and undefined samples
    out = []
    h = (b - a) / n
    prev = casutil.evx(f, a)
    i = 1
    while i <= n:
        x = a + i * h
        cur = casutil.evx(f, x)
        if cur == 0:
            out.append(x)
        elif prev is not None and cur is not None:
            if (prev < 0 < cur) or (cur < 0 < prev):
                out.append(_bis(f, x - h, x))
        prev = cur
        i += 1
    return out

def _hv(c, x):
    v = 0.0
    i = len(c) - 1
    while i >= 0:
        v = v * x + c[i]
        i -= 1
    return v

def _proots(p, lo, hi):
    # real roots of a rational polynomial in [lo, hi]: rational ones
    # exactly, the rest by a Horner scan and bisection
    p = caspoly.ptrim(list(p))
    out = []
    for r in caspoly.roots_rational(p):
        v = r[0] / float(r[1])
        if -1e4 <= v <= 1e4:
            out.append(v)
        qr = caspoly.pdivmod(p, [caspoly.rneg(r), caspoly.R1])
        if qr is not None and not qr[1]:
            p = caspoly.ptrim(qr[0])
    if len(p) < 2:
        return out
    c = [q[0] / float(q[1]) for q in p]
    n = 400
    h = (hi - lo) / n
    xs = [lo + i * h for i in range(n + 1)]
    # and out to +-10000 on a log scale
    far = [hi * math.pow(500.0, i / 60.0) for i in range(1, 61)]
    xs = [-x for x in reversed(far)] + xs + far if hi > 0 and lo < 0 else xs
    prev = _hv(c, xs[0])
    i = 1
    while i < len(xs):
        x = xs[i]
        h = x - xs[i - 1]
        cur = _hv(c, x)
        if cur == 0:
            out.append(x)
        elif (prev < 0) != (cur < 0) and prev != 0:
            a = x - h
            b = x
            fa = prev
            k = 0
            while k < 60:
                m = (a + b) / 2.0
                fm = _hv(c, m)
                if (fm < 0) == (fa < 0):
                    a = m
                    fa = fm
                else:
                    b = m
                k += 1
            out.append((a + b) / 2.0)
        prev = cur
        i += 1
    return out

def _roots(f, lo=None, hi=None):
    df = caseng.diff(f, 'x')
    pf = None
    if lo is None and caseng.vars_in(f) == ['x']:
        try:
            pf = caspoly.polyfrac(f, 'x')
        except Exception:
            pf = None
    fac = None
    if pf is None and lo is None and caseng.vars_in(f) == ['x']:
        try:
            fac = _pfac(f)
        except Exception:
            fac = None
    if pf is not None and len(caspoly.ptrim(list(pf[0]))) > 1:
        D = [q[0] / float(q[1]) for q in pf[1]] if pf[1] else [1.0]
        rs = [r for r in _proots(pf[0], LO, HI) if abs(_hv(D, r)) > 1e-12]
    elif fac is not None:
        # a product of powers of polynomials: zeros of the top factors
        rs = []
        for p, e in fac[1]:
            if e[0] > 0:
                for r in _proots(p, LO, HI):
                    v = casutil.evx(f, r)
                    if v is not None and abs(v) < 1e-9:
                        rs.append(r)
    elif lo is None:
        try:
            rs = cascalc.solve(f)
        except Exception:
            rs = _scan(f, LO, HI, 800)
    else:
        rs = _scan(f, lo, hi, 160)
    out = []
    for r in rs:
        r = _polish(f, df, r)
        if lo is not None and (r < lo - 1e-7 or r > hi + 1e-7):
            continue
        dup = False
        for q in out:
            if -1e-7 < q - r < 1e-7:
                dup = True
        if not dup:
            out.append(r)
    out.sort()
    return out

def _sign_on(t, a, b):
    i = 1
    while i <= 5:
        v = casutil.evx(t, a + (b - a) * i / 6.0)
        if v is not None and (v > 1e-12 or v < -1e-12):
            return 1 if v > 0 else -1
        i += 1
    return 0

def _segments(t, roots):
    pts = [LO]
    for r in roots:
        if LO + 1e-6 < r < HI - 1e-6:
            pts.append(r)
    pts.append(HI)
    segs = []
    i = 0
    while i < len(pts) - 1:
        s = _sign_on(t, pts[i], pts[i + 1])
        if segs and segs[len(segs) - 1][2] == s:
            segs[len(segs) - 1][1] = pts[i + 1]
        else:
            segs.append([pts[i], pts[i + 1], s])
        i += 1
    return segs

def _ivl(segs, pos, neg):
    out = []
    for a, b, s in segs:
        if s == 0:
            continue
        nm = pos if s > 0 else neg
        if a <= LO and b >= HI:
            dom = 'all x'
        elif a <= LO:
            dom = 'x < ' + _f(b)
        elif b >= HI:
            dom = 'x > ' + _f(a)
        else:
            dom = _f(a) + ' < x < ' + _f(b)
        out.append(nm + ' for ' + dom)
    return out

def _agrees(d, f):
    for xv in (0.43, 1.31, 2.17):
        a = casutil.evx(d, xv)
        b = casutil.evx(f, xv)
        if a is None or b is None:
            continue
        ab = b if b >= 0 else -b
        if not (-1e-6 * (1.0 + ab) < a - b < 1e-6 * (1.0 + ab)):
            return False
    return True

def _posint(v, dflt, hi=200, nm='n'):
    if v is None:
        return dflt
    n = int(v)
    if n != v or n < 1 or n > hi:
        raise ValueError(nm + ' must be 1 to ' + str(hi))
    return n

def _dpstr(v, dp):
    a = v if v >= 0 else -v
    if a < 1e-12:
        return '0'
    sf = int(math.floor(math.log10(a))) + 1 + dp
    if sf < 1:
        return '0'
    return casutil.fmt(v, sf)

def _anti(f):
    return _integ(f, 'x')

def _piece(f, F, a, b):
    if F is not None:
        va = casutil.evx(F, a)
        vb = casutil.evx(F, b)
        if va is not None and vb is not None:
            return vb - va
    return cascalc.defint(f, a, b)

# ---- letters, exact constants, tidy forms -----------------------------------

_ONE = ('n', 1)
_ZERO = ('n', 0)

def _params(t, own):
    # letters other than the variables in own (pi and e excluded)
    out = []
    for v in caseng.vars_in(t):
        if v not in own:
            out.append(v)
    return out

def _penv(names):
    # a generic positive value for each letter (letters taken as positive)
    env = {}
    k = 0
    for v in names:
        env[v] = 1.37 + 0.61 * k
        k += 1
    return env

def _exnode(v):
    # exact node for a typed number: fractions, multiples of pi and e
    if isinstance(v, int):
        return ('n', v)
    r = caseng._fltrat(v)
    if r is not None:
        return caseng._ratnode(r)
    for c in (('v', 'pi'), ('v', 'e')):
        q = caseng._fltrat(v / casutil.ev(c))
        if q is not None and q[1] <= 12 and abs(q[0]) <= 48:
            return caseng.simplify(('*', caseng._ratnode(q), c))
    if -30 < v < 30:
        q = caseng._fltrat(math.exp(v))
        if q is not None and q[1] <= 12 and 0 < q[0] <= 1000:
            return ('ln', caseng._ratnode(q))
    q = caseng._fltrat(v * v)
    if q is not None and q[1] <= 12 and q[0] <= 1000:
        t = caseng.simplify(('sqrt', caseng._ratnode(q)))
        return t if v > 0 else caseng.simplify(('neg', t))
    return ('n', v)

def _exactdef(F, a, b, val):
    # F(b) - F(a) kept exact, or None when it is no better than a decimal
    try:
        S = caseng.simplify
        t = S(('-', caseng.subst(F, 'x', _exnode(b)),
               caseng.subst(F, 'x', _exnode(a))))
        t = _lncollect(caspoly.expand(t))
        t = S(t) if _ts(S(t)).count('ln(') <= _ts(t).count('ln(') else t
    except Exception:
        return None
    s = _ts(t)
    if caseng.vars_in(t) or s.find('.') >= 0 or s.find('|') >= 0:
        return None
    v = casutil.evx(t, 0.0)
    if v is None or abs(v - val) > 1e-7 * (1.0 + abs(val)) or s == _f(val):
        return None
    return t

def _qsplit(n, q):
    # n = a^q * b, trial division to 400
    a = 1
    b = n
    d = 2
    while d <= 400 and d ** q <= b:
        while b % (d ** q) == 0:
            b //= d ** q
            a *= d
        d += 1
    return (a, b)

def _mput(items, base, e):
    key = caseng.tostr(base)
    for it in items:
        if it[2] == key:
            it[1] = caseng.simplify(('+', it[1], e))
            return
    items.append([base, e, key])

def _mono(t):
    # (exact coef, [[base, exp, key]]) with letters taken as positive
    k = t[0]
    if k == 'n':
        r = caseng._ratval(t)
        if r is not None:
            return (r, [])
    elif k == 'neg':
        a = _mono(t[1])
        return ((-a[0][0], a[0][1]), a[1])
    elif k == '*' or k == '/':
        a = _mono(t[1])
        b = _mono(t[2])
        if k == '/':
            if b[0][0] == 0:
                raise ValueError('division by zero')
            b = _mpow(b, (-1, 1))
        items = [[x[0], x[1], x[2]] for x in a[1]]
        for x in b[1]:
            _mput(items, x[0], x[1])
        return (caspoly.rmul(a[0], b[0]), items)
    elif k == 'sqrt':
        return _mpow(_mono(t[1]), (1, 2))
    elif k == '^':
        r = caseng._ratval(t[2])
        if r is not None:
            return _mpow(_mono(t[1]), r)
    return ((1, 1), [[t, _ONE, caseng.tostr(t)]])

def _mpow(a, r):
    # a^r for an exact r = (p, q)
    c, items = a
    p, q = r
    e = caspoly.ratnode(caspoly.rmake(p, q))
    out = []
    for b, x, key in items:
        _mput(out, b, caseng.simplify(('*', x, e)))
    num = c[0]
    if num == 0:
        return ((0, 1), [])
    if num < 0 and q % 2 == 0:
        raise ValueError('even root of a negative')
    sg = -1 if num < 0 else 1
    a1, b1 = _qsplit(num * sg, q)
    a2, b2 = _qsplit(c[1], q)
    if b1 != 1:
        _mput(out, ('n', b1), e)
    if b2 != 1:
        _mput(out, ('n', b2), caseng.simplify(('neg', e)))
    if p >= 0:
        return (caspoly.rmake(sg * a1 ** p, a2 ** p), out)
    return (caspoly.rmake(sg * a2 ** (-p), a1 ** (-p)), out)

def _mtree(a):
    c, items = a
    node = None
    for b, e, key in items:
        if e == _ZERO:
            continue
        p = b if e == _ONE else ('^', b, e)
        node = p if node is None else ('*', node, p)
    cn = caspoly.ratnode(c)
    if node is None:
        return cn
    if c != (1, 1):
        node = ('*', cn, node)
    return caseng.simplify(node)

def _msqrt(t):
    return _mtree(_mpow(_mono(caseng.simplify(t)), (1, 2)))

def _xco(f, var='x', top=3):
    # coefficients of f as a polynomial in var (letters allowed), or None
    try:
        raw = []
        caseng._flatadd(caspoly.expand(caseng.simplify(f)), 1, raw)
    except Exception:
        return None
    co = {}
    hi = 0
    for node, sg in raw:
        mo = _mono(node)
        k = 0
        rest = []
        for it in mo[1]:
            if it[0] == ('v', var):
                r = caseng._ratval(it[1])
                if r is None or r[1] != 1 or r[0] < 0:
                    return None
                k = r[0]
            elif var in caseng.vars_in(it[0]):
                return None
            else:
                rest.append(it)
        if k > top:
            return None
        ct = _mtree((mo[0] if sg > 0 else (-mo[0][0], mo[0][1]), rest))
        co[k] = ct if k not in co else caseng.simplify(('+', co[k], ct))
        if k > hi:
            hi = k
    out = [co.get(k, _ZERO) for k in range(hi + 1)]
    while len(out) > 1 and out[len(out) - 1] == _ZERO:
        out.pop()
    return out

def _symroots(f, var='x'):
    # exact roots of a degree 1 or 2 polynomial in var with letters, or None
    co = _xco(f, var, 2)
    if co is None or len(co) < 2:
        return None
    S = caseng.simplify
    if len(co) == 2:
        return [S(('neg', ('/', co[0], co[1])))]
    C, B, A = co
    if C == _ZERO:
        return [_ZERO, S(('neg', ('/', B, A)))]
    try:
        if B == _ZERO:
            q = S(('neg', ('/', C, A)))
            if caseng._isneg(q):
                return []
            s = _msqrt(q)
            return [S(('neg', s)), s]
        D = S(('-', ('^', B, ('n', 2)), ('*', ('n', 4), ('*', A, C))))
        if caseng._isneg(D):
            return []
        s = _msqrt(D)
    except ValueError:
        return None
    two = ('*', ('n', 2), A)
    return [S(('/', ('-', ('neg', B), s), two)), S(('/', ('+', ('neg', B), s), two))]

def _expfold(t):
    # e^(a + k ln u) -> u^k e^a, so a constant c = ln 125 shows as 125
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if len(t) == 3:
        t = (k, _expfold(t[1]), _expfold(t[2]))
    else:
        t = (k, _expfold(t[1]))
    arg = None
    if k == 'exp':
        arg = t[1]
    elif k == '^' and t[1] == ('v', 'e'):
        arg = t[2]
    if arg is None:
        return t
    raw = []
    try:
        arg = caspoly.expand(caseng.simplify(arg))
    except Exception:
        pass
    caseng._flatadd(caseng.simplify(arg), 1, raw)
    keep = []
    pulled = []
    for node, sg in raw:
        coef, fl, cxc, out = caseng._termparts([(node, 1)])
        if fl is None and cxc is None and len(out) == 1 and \
                out[0][0][0] == 'ln' and caseng._ratval(out[0][1]) == (1, 1):
            c = coef if sg > 0 else (-coef[0], coef[1])
            pulled.append(('^', out[0][0][1], caseng._ratnode(c)))
        else:
            keep.append((node, sg))
    if not pulled:
        return t
    node = None
    for p in pulled:
        node = p if node is None else ('*', node, p)
    if keep:
        rest = caseng._addf(keep)
        node = ('*', node, ('exp', rest))
    return caseng.simplify(caseng.strip_abs(node))

def _lncollect(t):
    # k ln u + k ln v + ... -> k ln(u v ...) with k the common factor
    raw = []
    caseng._flatadd(caseng.simplify(t), 1, raw)
    lns = []
    rest = []
    for node, sg in raw:
        coef, fl, cxc, out = caseng._termparts([(node, 1)])
        if fl is None and cxc is None and len(out) == 1 and \
                out[0][0][0] == 'ln' and caseng._ratval(out[0][1]) == (1, 1):
            lns.append(((coef[0] * sg, coef[1]), out[0][0][1]))
        else:
            rest.append((node, sg))
    if len(lns) < 2:
        return t
    g = 0
    L = 1
    for c, u in lns:
        g = caseng.gcd(g, c[0])
        L = L * c[1] // caseng.gcd(L, c[1])
    k = (g, L)
    arg = None
    for c, u in lns:
        e = caspoly.rdiv(c, k)
        p = u if e == (1, 1) else ('^', u, caspoly.ratnode(e))
        arg = p if arg is None else ('*', arg, p)
    arg = caseng.simplify(arg)
    r = caseng._ratval(arg)
    if r is not None and 0 < r[0] < r[1]:
        # ln(1/35) -> -ln(35)
        arg = caspoly.ratnode((r[1], r[0]))
        k = (-k[0], k[1])
    lg = ('ln', arg)
    if k[0] < 0:
        lg = ('neg', _kln((-k[0], k[1]), lg))
    else:
        lg = _kln(k, lg)
    if rest:
        if caseng._isneg(lg):
            return ('-', caseng._addf(rest), lg[1])
        return ('+', lg, caseng._addf(rest))
    return lg

def _kln(k, lg):
    # k ln u as (p ln u)/q
    if k[0] != 1:
        lg = ('*', ('n', k[0]), lg)
    if k[1] != 1:
        lg = ('/', lg, ('n', k[1]))
    return lg

def _pfac(t):
    # t = c * prod p_i^e_i * prod e^(u_k), p_i and u_k' polynomials in x:
    # (c, [(poly, e)], [u]) or None
    k = t[0]
    if k == 'n':
        r = caseng._ratval(t)
        return None if r is None else (r, [], [])
    if k == 'neg':
        a = _pfac(t[1])
        return None if a is None else ((-a[0][0], a[0][1]), a[1], a[2])
    if k == '*' or k == '/':
        a = _pfac(t[1])
        b = _pfac(t[2])
        if a is None or b is None:
            return None
        if k == '/':
            if b[0][0] == 0:
                return None
            b = ((b[0][1], b[0][0]), [(p, (-e[0], e[1])) for p, e in b[1]],
                 [('neg', u) for u in b[2]])
        return (caspoly.rmul(a[0], b[0]), a[1] + b[1], a[2] + b[2])
    if k == 'exp' or (k == '^' and t[1] == ('v', 'e')):
        u = t[1] if k == 'exp' else t[2]
        if caspoly.poly(caseng.diff(u, 'x'), 'x') is None:
            return None
        return ((1, 1), [], [u])
    if k == 'sqrt' or k == '^':
        e = (1, 2) if k == 'sqrt' else caseng._ratval(t[2])
        if e is None:
            return None
        a = _pfac(t[1])
        if a is None or a[2]:
            return None
        if a[0] != (1, 1) and e[1] != 1:
            return None
        c = a[0]
        if e[1] == 1:
            c = caspoly.rmake(c[0] ** e[0], c[1] ** e[0]) if e[0] >= 0 else \
                caspoly.rmake(c[1] ** (-e[0]), c[0] ** (-e[0]))
        return (c, [(p, caspoly.rmul(x, e)) for p, x in a[1]], [])
    p = caspoly.poly(t, 'x')
    if p is None or len(caspoly.ptrim(list(p))) < 2:
        return None
    return ((1, 1), [(caspoly.ptrim(list(p)), (1, 1))], [])

def _ptree(p, e):
    b = caspoly.ptree(p, 'x')
    if e == (1, 1):
        return b
    if e == (1, 2):
        return ('sqrt', b)
    return ('^', b, caspoly.ratnode(e))

def _qrule(f):
    # f' as one fraction when f is a product of powers of polynomials
    # and exponentials: f' = f * sum e_i p_i'/p_i + f * sum u_k'
    pf = _pfac(f)
    if pf is None or not (pf[1] or pf[2]):
        return None
    c, fs, us = pf
    M = [caspoly.R0]
    i = 0
    while i < len(fs):
        term = caspoly.pscale(caspoly.pderiv(fs[i][0]), fs[i][1])
        j = 0
        while j < len(fs):
            if j != i:
                term = caspoly.pmul(term, fs[j][0])
            j += 1
        M = caspoly.padd(M, term)
        i += 1
    for u in us:
        du = caspoly.poly(caseng.diff(u, 'x'), 'x')
        for p, e in fs:
            du = caspoly.pmul(du, p)
        M = caspoly.padd(M, du)
    M = caspoly.ptrim([caspoly.rmul(x, c) for x in M])
    if not M:
        return _ZERO
    node = caspoly.ptree(M, 'x')
    if us:
        ex = us[0]
        for u in us[1:]:
            ex = ('+', ex, u)
        node = ('*', node, ('exp', caseng.simplify(ex)))
    den = None
    for p, e in fs:
        e1 = caspoly.rsub(e, (1, 1))
        if e1[0] > 0:
            node = ('*', node, _ptree(p, e1))
        elif e1[0] < 0:
            q = _ptree(p, (-e1[0], e1[1]))
            den = q if den is None else ('*', den, q)
    return node if den is None else ('/', node, den)

def _numd(f, xv):
    h = 1e-5 * (1.0 + abs(xv))
    a = casutil.evx(f, xv + h)
    b = casutil.evx(f, xv - h)
    if a is None or b is None:
        return None
    return (a - b) / (2.0 * h)

def _isderiv(c, f):
    # does c match a numeric derivative of f?
    hit = 0
    for xv in (0.43, 1.31, 2.17, 3.4, -0.77):
        a = casutil.evx(c, xv)
        b = _numd(f, xv)
        if a is None or b is None:
            continue
        if abs(a - b) > 1e-4 * (1.0 + abs(b)):
            return False
        hit += 1
    return hit > 0

def _dshow(f, d):
    # the tidiest correct form of f' (d is the engine's f')
    try:
        q = _qrule(f)
    except Exception:
        q = None
    if q is not None and _isderiv(q, f):
        return q
    best = d
    try:
        c = caspoly.collect(caspoly.expand(d))
        if _agrees(c, d) and len(_ts(c)) < len(_ts(best)):
            best = c
    except Exception:
        pass
    return best
# A tree compiled to nested closures: real values only, about 4 times
# faster than caseng.evalf for the long scans below.

_F1 = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'exp': math.exp,
       'ln': math.log, 'sqrt': math.sqrt, 'abs': abs, 'asin': math.asin,
       'acos': math.acos, 'atan': math.atan}


def _cpow(a, b):
    def f(x):
        u = a(x)
        v = b(x)
        if u < 0 and v != int(v):
            raise ValueError('complex')
        return u ** v
    return f


def _cfn(k, a, deg):
    g = _F1.get(k)
    if k in ('sin', 'cos', 'tan') and deg:
        return lambda x: g(a(x) * math.pi / 180.0)
    if k in ('asin', 'acos', 'atan') and deg:
        return lambda x: g(a(x)) * 180.0 / math.pi
    if g is not None:
        return lambda x: g(a(x))
    if k == 'log':
        return lambda x: math.log(a(x)) / math.log(10.0)
    if k == 'sec':
        return lambda x: 1.0 / math.cos(a(x) * (math.pi / 180.0 if deg else 1.0))
    if k == 'cosec':
        return lambda x: 1.0 / math.sin(a(x) * (math.pi / 180.0 if deg else 1.0))
    if k == 'cot':
        return lambda x: 1.0 / math.tan(a(x) * (math.pi / 180.0 if deg else 1.0))
    return None


def _comp(t, var, deg):
    k = t[0]
    if k == 'n':
        c = t[1]
        if isinstance(c, complex):
            return None
        return lambda x: c
    if k == 'v':
        if t[1] == var:
            return lambda x: x
        if t[1] == 'pi':
            return lambda x: math.pi
        if t[1] == 'e':
            return lambda x: math.e
        return None
    a = _comp(t[1], var, deg)
    if a is None:
        return None
    if k == 'neg':
        return lambda x: -a(x)
    if len(t) == 2:
        return _cfn(k, a, deg)
    b = _comp(t[2], var, deg)
    if b is None:
        return None
    if k == '+':
        return lambda x: a(x) + b(x)
    if k == '-':
        return lambda x: a(x) - b(x)
    if k == '*':
        return lambda x: a(x) * b(x)
    if k == '/':
        return lambda x: a(x) / b(x)
    if k == '^':
        return _cpow(a, b)
    if k == 'logb':
        return lambda x: math.log(b(x)) / math.log(a(x))
    return None

def _fast(tree, var='x', deg=False):
    # f(x) -> float or None; falls back to _val for anything unusual.
    # var 'xy' makes f take the pair (x, y).
    g = _comp(tree, var, deg)
    if g is None:
        if var == 'x':
            return lambda x: casutil.evx(tree, x)
        return lambda x: casutil.evx(tree, x, {var: x})

    def f(x):
        try:
            v = g(x)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        if isinstance(v, complex) or v != v or v > 1e300 or v < -1e300:
            return None
        return v
    return f

# ---- G differentiation -------------------------------------------------------

def _xonly(f):
    # x is the variable; other letters are constants (y is refused)
    if 'y' in caseng.vars_in(f) or 't' in caseng.vars_in(f):
        raise ValueError('use x as the variable')
    return _params(f, ('x',))

def t_deriv(f):
    _xonly(f)
    d1 = _dshow(f, _diff(f))
    d2 = _dshow(d1, _diff(d1))
    return ["f'(x) =", _m(d1), "f''(x) =", _m(d2),
            _w("f'(x) = " + _ts(d1)), _w("f''(x) = " + _ts(d2))]

def t_tangent(f, a):
    _chk(f, ('x',))
    d1 = _diff(f)
    y0 = _val(f, a)
    gr = _val(d1, a)
    out = ['tangent y =', _m(_lin(gr, y0 - gr * a))]
    if _z(gr) == 0:
        out.append('normal x = ' + _f(a))
    else:
        out.append('normal y =')
        out.append(_m(_lin(-1.0 / gr, y0 + a / gr)))
    out.append(_w('point ' + _pt(a, y0)))
    out.append(_w("f'(x) = " + _ts(d1)))
    out.append(_w("f'(" + _f(a) + ') = ' + _f(gr)))
    return out

def _nature(d1, d2, r):
    s = casutil.evx(d2, r)
    if s is not None and (s > 1e-9 or s < -1e-9):
        return 'min' if s > 0 else 'max'
    h = 0.001 * (1.0 + (r if r >= 0 else -r))
    a = casutil.evx(d1, r - h)
    b = casutil.evx(d1, r + h)
    if a is None or b is None:
        return 'stationary'
    if a < 0 and b > 0:
        return 'min'
    if a > 0 and b < 0:
        return 'max'
    return 'inflection'

def _exactpt(f, d1, r):
    # exact (x, y) text at a stationary point r of a rational f, or None
    pf = caspoly.polyfrac(f, 'x')
    if pf is None:
        return None
    D = caspoly.ptrim(list(pf[1])) if pf[1] else [caspoly.R1]
    N = caspoly.ptrim(caspoly.psub(caspoly.pmul(caspoly.pderiv(pf[0]), D),
                                   caspoly.pmul(pf[0], caspoly.pderiv(D))))
    if len(N) != 3:
        return None
    L = 1
    for q in N:
        L = L * q[1] // caseng.gcd(L, q[1])
    C, B, A = [q[0] * (L // q[1]) for q in N]
    Di = B * B - 4 * A * C
    if Di <= 0:
        return None
    rs = [caseng.simplify(('/', (op, ('n', -B), ('sqrt', ('n', Di))), ('n', 2 * A)))
          for op in ('-', '+')]
    for xr in rs:
        if abs(casutil.ev(xr) - r) < 1e-7 * (1 + abs(r)):
            if len(D) == 2:
                # at a stationary point f = N'/D', a polynomial when D is linear
                y = caspoly.ptree(caspoly.pscale(caspoly.pderiv(pf[0]),
                                                 caspoly.rdiv(caspoly.R1, D[1])), 'x')
            elif len(D) == 1:
                # f = q N + r with N(x) = 0 there, so f = r
                qr = caspoly.pdivmod(caspoly.pscale(pf[0], caspoly.rdiv(
                    caspoly.R1, D[0])), N)
                y = caspoly.ptree(qr[1], 'x') if qr is not None else f
            else:
                y = f
            yv = caseng.simplify(caseng.subst(y, 'x', xr))
            if not caseng.vars_in(yv) and \
                    abs(casutil.ev(yv) - casutil.ev(caseng.subst(f, 'x', xr))) < 1e-7:
                return '(' + _ts(xr) + ', ' + _ts(yv) + ')'
    return None

def _stat_sym(f, params):
    d1 = _diff(f)
    d2 = _diff(d1)
    rs = _symroots(d1)
    if rs is None:
        raise ValueError("cannot solve f'(x) = 0 with letters")
    env = _penv(params)
    out = []
    for r in rs:
        y = caseng.simplify(caseng.subst(f, 'x', r))
        rv = casutil.evx(r, 0.0, env)
        s = None if rv is None else casutil.evx(d2, rv, env)
        nat = 'stationary'
        if s is not None and s > 1e-12:
            nat = 'min'
        elif s is not None and s < -1e-12:
            nat = 'max'
        out.append(nat + ' at (' + _ts(r) + ', ' + _ts(y) + ')')
    if not out:
        out.append("f'(x) = 0 has no real root")
    out.append(_w("f'(x) = " + _ts(_dshow(f, d1))))
    out.append(_w("f''(x) = " + _ts(d2)))
    out.append(_w(', '.join(params) + ' taken as positive'))
    return out

def t_stationary(f):
    params = _xonly(f)
    if params:
        return _stat_sym(f, params)
    d1 = _diff(f)
    d2 = _diff(d1)
    rs = _roots(d1)
    out = []
    for r in rs[:8]:
        y = casutil.evx(f, r)
        ex = None
        if y is not None and (_f(r).find('.') >= 0 or
                              caseng._fltrat(y) is None):
            try:
                ex = _exactpt(f, d1, r)
            except Exception:
                ex = None
            if ex is None and _f(r).find('.') < 0:
                try:
                    yt = caseng.simplify(caseng.subst(f, 'x', _exnode(r)))
                    if _ts(yt).find('.') < 0 and not caseng.vars_in(yt) and \
                            abs(casutil.ev(yt) - y) < 1e-9 * (1 + abs(y)):
                        ex = '(' + _f(r) + ', ' + _ts(yt) + ')'
                except Exception:
                    ex = None
        pt = _pt(r, y) if y is not None else '(' + _f(r) + ', ?)'
        out.append(_nature(d1, d2, r) + ' at ' + (ex if ex else pt))
        if ex:
            out.append(_w('= ' + pt))
    if not out:
        out.append('none in -20 <= x <= 20')
    out.append(_w("f'(x) = " + _ts(_dshow(f, d1))))
    out.append(_w("f''(x) = " + _ts(_dshow(d1, d2))))
    if len(rs) > 8:
        out.append(_warn('only the first 8 shown'))
    return out

def _edge(f, d, a, b, aok):
    # x where f (or d) stops being defined, between a and b (fast f, d)
    k = 0
    while k < 40:
        mid = (a + b) / 2.0
        ok = f(mid) is not None and d(mid) is not None
        if ok == aok:
            a = mid
        else:
            b = mid
        k += 1
    return _near((a + b) / 2.0)

def _dsegs(f, d):
    # [lo, hi, sign, lo kind, hi kind] where f and d are defined; kinds:
    # 'e' a domain edge or pole, 'r' a root of d, 'w' the window end
    n = 200
    xs = [LO + (HI - LO) * i / n for i in range(n + 1)]
    F = _fast(f, 'x', casutil.DEG)
    G = _fast(d, 'x', casutil.DEG)
    ok = []
    ds = []
    for x in xs:
        a = F(x)
        b = G(x)
        ok.append(a is not None and b is not None)
        ds.append(b)
    cuts = []
    for r in _roots(d):
        if LO < r < HI:
            cuts.append((r, 'r'))
    i = 1
    while i <= n:
        if ok[i] != ok[i - 1]:
            cuts.append((_edge(F, G, xs[i - 1], xs[i], ok[i - 1]), 'e'))
        elif ok[i] and (ds[i - 1] < 0 < ds[i] or ds[i] < 0 < ds[i - 1]):
            hit = False
            for c, k in cuts:
                if xs[i - 1] - 1e-9 <= c <= xs[i] + 1e-9:
                    hit = True
            if not hit:
                cuts.append((_bis(d, xs[i - 1], xs[i]), 'e'))
        i += 1
    cuts.sort()
    pts = [(LO, 'w')]
    for c, k in cuts:
        if c - pts[len(pts) - 1][0] > 1e-7:
            pts.append((c, k))
        elif k == 'e':
            pts[len(pts) - 1] = (pts[len(pts) - 1][0], 'e')
    pts.append((HI, 'w'))
    segs = []
    i = 0
    while i < len(pts) - 1:
        a, ka = pts[i]
        b, kb = pts[i + 1]
        i += 1
        mid = (a + b) / 2.0
        if F(mid) is None or G(mid) is None:
            continue
        s = 0
        for j in (1, 2, 3, 4, 5):
            v = G(a + (b - a) * j / 6.0)
            if v is not None and (v > 1e-12 or v < -1e-12):
                s = 1 if v > 0 else -1
                break
        last = segs[len(segs) - 1] if segs else None
        if last is not None and last[1] == a and last[2] == s and ka == 'r':
            last[1] = b
            last[4] = kb
        else:
            segs.append([a, b, s, ka, kb])
    return segs

def _ivl2(segs, pos, neg):
    out = []
    for a, b, s, ka, kb in segs:
        if s == 0:
            continue
        nm = pos if s > 0 else neg
        if ka == 'w' and kb == 'w':
            dom = 'all x'
        elif ka == 'w':
            dom = 'x < ' + _f(b)
        elif kb == 'w':
            dom = 'x > ' + _f(a)
        else:
            dom = _f(a) + ' < x < ' + _f(b)
        out.append(nm + ' for ' + dom)
    return out

def t_inflect(f):
    _xonly(f)
    d1 = _dshow(f, _diff(f))
    d2 = _dshow(d1, _diff(d1))
    segs = _dsegs(f, d2)
    out = []
    i = 0
    while i < len(segs) - 1:
        r = segs[i][1]
        if segs[i][4] == 'r' and segs[i + 1][0] == r and \
                segs[i][2] != segs[i + 1][2]:
            y = casutil.evx(f, r)
            out.append('inflection at ' +
                       (_pt(r, y) if y is not None else '(' + _f(r) + ', ?)'))
        i += 1
    if not out:
        out.append('no inflection point')
    for ln in _ivl2(segs, 'convex', 'concave'):
        out.append(ln)
    out.append(_w("f''(x) = " + _ts(d2)))
    out.append(_w("convex means f''(x) > 0"))
    return out

def t_incdec(f):
    _xonly(f)
    d1 = _dshow(f, _diff(f))
    out = _ivl2(_dsegs(f, d1), 'increasing', 'decreasing')
    if not out:
        out = ['constant in -20 <= x <= 20']
    out.append(_w("f'(x) = " + _ts(d1)))
    return out

def _fpsym(f):
    # (f(x+h) - f(x))/h with the h cancelled, for a polynomial f
    H = ('v', 'h')
    num = caseng.simplify(('-', caseng.subst(f, 'x', ('+', X, H)), f))
    co = _xco(num, 'h', 6)
    if co is None or len(co) < 2 or co[0] != _ZERO:
        return None
    q = None
    k = len(co) - 1
    while k >= 1:
        if co[k] != _ZERO:
            term = co[k] if k == 1 else ('*', co[k], ('^', H, ('n', k - 1)))
            q = term if q is None else ('+', q, term)
        k -= 1
    return (caseng.simplify(q), co[1])

def t_firstprin(f, a):
    _chk(f, ('x',))
    fa = _val(f, a)
    ex = _val(_diff(f), a)
    out = ["f'(" + _f(a) + ') = ' + _f(ex)]
    try:
        fp = _fpsym(f)
    except Exception:
        fp = None
    if fp is not None:
        q, lim = fp
        qa = caseng.simplify(caseng.subst(q, 'x', _exnode(a)))
        out.append('(f(x+h) - f(x))/h = ' + _ts(q))
        out.append('at x = ' + _f(a) + ': ' + _ts(qa))
        out.append("h -> 0: f'(x) = " + _ts(lim))
    out.append(_w('(f(x+h) - f(x))/h at x = ' + _f(a)))
    for hs, h in (('0.1', 0.1), ('0.01', 0.01), ('0.001', 0.001)):
        v = casutil.evx(f, a + h)
        if v is None:
            out.append(_warn('f undefined at x = ' + _f(a + h)))
        else:
            out.append(_w('h = ' + hs + '   grad = ' + _g((v - fa) / h)))
    return out

def t_param(xt, yt, tv):
    _chk(xt, ('t',))
    _chk(yt, ('t',))
    dx = _diff(xt, 't')
    dy = _diff(yt, 't')
    if dx == ('n', 0):
        raise ValueError('dx/dt = 0')
    gr = cascalc.tidy(('/', dy, dx))
    out = ['dy/dx =', _m(gr),
           _w('dx/dt = ' + _ts(dx)), _w('dy/dt = ' + _ts(dy)),
           _w('dy/dx = (dy/dt) / (dx/dt)')]
    if tv is not None:
        env = {'t': tv}
        gv = _val(gr, 0.0, env)
        xv = _val(xt, 0.0, env)
        yv = _val(yt, 0.0, env)
        out.insert(0, 'at t = ' + _f(tv) + ': dy/dx = ' + _f(gv))
        out.append(_w('point ' + _pt(xv, yv)))
    return out

def t_implicit(F, xv, yv):
    _chk(F, ('x', 'y'))
    Fx = _diff(F, 'x')
    Fy = _diff(F, 'y')
    if Fy == ('n', 0):
        raise ValueError('no y in F')
    gr = cascalc.tidy(('neg', ('/', Fx, Fy)))
    out = ['dy/dx =', _m(gr),
           _w('dF/dx = ' + _ts(Fx)), _w('dF/dy = ' + _ts(Fy)),
           _w('dy/dx = -(dF/dx) / (dF/dy)')]
    if xv is None and yv is None:
        return out
    if xv is None or yv is None:
        out.append(_warn('give both x and y'))
        return out
    env = {'x': xv, 'y': yv}
    gv = _val(gr, xv, env)
    head = ['at ' + _pt(xv, yv) + ': dy/dx = ' + _f(gv)]
    fv = casutil.evx(F, xv, env)
    if fv is not None and (fv > 1e-6 or fv < -1e-6):
        out.append(_warn('F = ' + _f(fv) + ': not on the curve'))
        return head + out
    c = yv - gv * xv
    head.append('tangent y = ' + _ts(_lin(gv, c)))
    if _z(gv) != 0:
        head.append(_w('tangent meets y = 0 at x = ' + _f(xv - yv / gv)))
        head.append('normal y = ' + _ts(_lin(-1.0 / gv, yv + xv / gv)))
        head.append(_w('normal meets y = 0 at x = ' + _f(xv + yv * gv)))
    else:
        head.append('normal x = ' + _f(xv))
    head.append(_w('tangent meets x = 0 at y = ' + _f(c)))
    return head + out

def _ev2(t, x, y):
    return casutil.evx(t, x, {'x': x, 'y': y})

def _nr2(F, gi, J, x, y):
    # 2-D Newton on F = 0 and J[gi] = 0, J = (Fx, Fy, Gx, Gy)
    i = 0
    while i < 14:
        f = _ev2(F, x, y)
        js = [_ev2(t, x, y) for t in J]
        if f is None or None in js:
            return None
        g = js[gi]
        det = js[0] * js[3] - js[1] * js[2]
        if det == 0:
            return None
        dx = (f * js[3] - g * js[1]) / det
        dy = (js[0] * g - js[2] * f) / det
        st = abs(dx) + abs(dy)
        if st > 4.0:
            dx = dx * 4.0 / st
            dy = dy * 4.0 / st
        x -= dx
        y -= dy
        if abs(x) > 50 or abs(y) > 50:
            return None
        if abs(dx) + abs(dy) < 1e-10 * (1 + abs(x) + abs(y)):
            f = _ev2(F, x, y)
            g = _ev2(J[gi], x, y)
            if f is None or g is None or abs(f) > 1e-8 or abs(g) > 1e-8:
                return None
            return (_near(x), _near(y))
        i += 1
    return None

def _tanpts(F, gi, J):
    found = []
    for sx, sy in ((-2.9, -3.1), (2.7, 3.2), (-3.2, 2.8), (3.1, -2.6), (0.2, 0.1)):
        p = _nr2(F, gi, J, sx, sy)
        if p is None:
            continue
        dup = False
        for q in found:
            if abs(q[0] - p[0]) < 1e-6 * (1 + abs(p[0])) and \
                    abs(q[1] - p[1]) < 1e-6 * (1 + abs(p[1])):
                dup = True
        if not dup and len(found) < 6:
            found.append(p)
    found.sort()
    return found

def _implicit_k(F, x0, ks):
    # dy/dx = 0 at x = x0 with one unknown constant: Fx = 0 gives y,
    # then F = 0 gives the constant
    if len(ks) != 1:
        raise ValueError('one unknown letter only')
    k = ks[0]
    if x0 is None:
        raise ValueError('give x where dy/dx = 0')
    S = caseng.simplify
    Fx = _diff(F, 'x')
    if k in caseng.vars_in(Fx):
        raise ValueError(k + ' must not appear in dF/dx')
    g = S(caseng.subst(caseng.subst(Fx, 'x', _exnode(x0)), 'y', X))
    try:
        lin = casalg.linin(S(F), k)
    except Exception:
        lin = None
    if lin is None or lin[0] == _ZERO:
        raise ValueError('F must be linear in ' + k)
    out = []
    for yv in _roots(g):
        kt = S(('neg', ('/', lin[1], lin[0])))
        kv = casutil.evx(kt, x0, {'x': x0, 'y': yv})
        if kv is None:
            continue
        out.append('y = ' + _f(yv) + ', ' + k + ' = ' + _f(kv))
    if not out:
        out.append('no y with dF/dx = 0 at x = ' + _f(x0))
    out.append(_w('dF/dx = ' + _ts(Fx) + ' = 0 at x = ' + _f(x0)))
    out.append(_w('then F = 0 gives ' + k))
    return out

def t_implicit0(F, x0):
    ks = _params(F, ('x', 'y'))
    if ks:
        return _implicit_k(F, x0, ks)
    Fx = _diff(F, 'x')
    Fy = _diff(F, 'y')
    Fxx = _diff(Fx, 'x')
    Fxy = _diff(Fx, 'y')
    Fyy = _diff(Fy, 'y')
    hor = _tanpts(F, 0, (Fx, Fy, Fxx, Fxy))
    ver = _tanpts(F, 1, (Fx, Fy, Fxy, Fyy))
    out = []
    for x, y in hor:
        v = _ev2(Fy, x, y)
        out.append('dy/dx = 0 at ' + _pt(x, y) +
                   ('' if v is None or abs(v) > 1e-9 else ' (singular)'))
    for x, y in ver:
        v = _ev2(Fx, x, y)
        if v is None or abs(v) > 1e-9:
            out.append('vertical tangent at ' + _pt(x, y))
    if not hor:
        out.append('no point with dy/dx = 0 found')
    out.append(_w('dF/dx = ' + _ts(Fx) + ' = 0 with F = 0'))
    out.append(_w('vertical: dF/dy = ' + _ts(Fy) + ' = 0 with F = 0'))
    out.append(_w('Newton from starts in -4..4, |x|,|y| <= 50'))
    return out

def t_connected(y, xv, dxdt):
    _chk(y, ('x',))
    dydx = _val(_diff(y), xv)
    dydt = dydx * dxdt
    return ['dy/dt = ' + _f(dydt),
            _w('dy/dx at x = ' + _f(xv) + ' is ' + _f(dydx)),
            _w('dy/dt = dy/dx * dx/dt'),
            _w('     = ' + _f(dydx) + ' * ' + _f(dxdt) + ' = ' + _f(dydt))]

def t_invderiv(f, a):
    _chk(f, ('x',))
    b = _val(f, a)
    gr = _val(_diff(f), a)
    if _z(gr) == 0:
        raise ValueError("f'(a) = 0: no inverse here")
    return ["(f^-1)'(" + _f(b) + ') = ' + _f(1.0 / gr),
            _w('f(' + _f(a) + ') = ' + _f(b)),
            _w("f'(" + _f(a) + ') = ' + _f(gr)),
            _w("(f^-1)'(b) = 1 / f'(a)")]

def t_valat(f, a):
    _chk(f, ('x',))
    d1 = _diff(f)
    d2 = _diff(d1)
    return ['f(' + _f(a) + ') = ' + _f(_z(_val(f, a))),
            "f'(" + _f(a) + ') = ' + _f(_z(_val(d1, a))),
            "f''(" + _f(a) + ') = ' + _f(_z(_val(d2, a))),
            _w("f'(x) = " + _ts(d1)),
            _w("f''(x) = " + _ts(d2))]

# ---- H integration -----------------------------------------------------------

def t_indef(f):
    _chk(f, ('x',))
    F = _anti(f)
    if F is None:
        raise ValueError('no standard integral')
    return ['int f(x) dx =', _m(('+', F, ('v', 'c'))),
            _w('d/dx of the answer: ' +
               ('agrees' if _agrees(_diff(F), f) else 'DISAGREES'))]

def t_defint(f, a, b):
    _chk(f, ('x',))
    F = _anti(f)
    val = None
    va = None
    vb = None
    if F is not None:
        va = casutil.evx(F, a)
        vb = casutil.evx(F, b)
        if va is not None and vb is not None:
            val = vb - va
    num = cascalc.defint(f, a, b)
    out = []
    if val is None:
        if num is None:
            raise ValueError('cannot integrate')
        out.append('integral = ' + _f(num))
        out.append(_warn('numerical estimate only'))
        return out
    ex = _exactdef(F, a, b, val)
    out.append('integral = ' + (_ts(ex) + ' = ' if ex is not None else '') +
               _f(val))
    out.append(_w('F(x) = ' + _ts(F)))
    out.append(_w('F(' + _f(b) + ') - F(' + _f(a) + ') = ' +
                  _f(vb) + ' - ' + _f(va)))
    if num is None:
        out[0] = 'f breaks inside a..b'
        out.append(_warn('F(b) - F(a) = ' + _f(val) + ' is not valid'))
    else:
        d = num - val
        if d < 0:
            d = -d
        va2 = val if val >= 0 else -val
        if d > 1e-4 * (1.0 + va2):
            out.append(_warn('numeric check gives ' + _f(num)))
            out.append(_warn('a discontinuity lies in a..b'))
    return out

def _area_lines(f, a, b, name):
    num = cascalc.defint(f, a, b)
    if num is None:
        raise ValueError('f breaks in a..b')
    F = _anti(f)
    cuts = [a]
    for r in _roots(f, a, b):
        if a + 1e-9 < r < b - 1e-9:
            cuts.append(r)
    cuts.append(b)
    total = 0.0
    signed = 0.0
    out = []
    i = 0
    while i < len(cuts) - 1:
        v = _piece(f, F, cuts[i], cuts[i + 1])
        if v is None:
            raise ValueError('cannot integrate')
        signed += v
        total += v if v >= 0 else -v
        out.append(_w(_f(cuts[i]) + ' to ' + _f(cuts[i + 1]) + ': ' + _f(v)))
        i += 1
    ex = None
    if F is not None and len(cuts) == 2:
        ex = _exactdef(F, a, b, signed)
        if ex is not None and signed < 0:
            ex = caseng.simplify(caseng._negnode(ex))
    head = [name + ' = ' + (_ts(ex) + ' = ' if ex is not None else '') +
            _f(total), _w('signed integral = ' + _f(signed))]
    if len(cuts) > 2:
        head.append(_warn('sign change: parts added as |area|'))
    gap = num - signed
    if gap < 0:
        gap = -gap
    asg = 1.0 + (signed if signed >= 0 else -signed)
    if gap > 0.1 * asg:
        raise ValueError('f breaks in a..b')
    if gap > 1e-3 * asg:
        head.append(_warn('numeric check ' + _f(num) + ': f may break'))
    return head + out

def t_area(f, a, b):
    _chk(f, ('x',))
    if b <= a:
        raise ValueError('need a < b')
    return _area_lines(f, a, b, 'area')

def t_between(f, g, a, b):
    _chk(f, ('x',))
    _chk(g, ('x',))
    h = cascalc.tidy(('-', f, g))
    out = []
    if a is None or b is None:
        rs = _roots(h)
        if len(rs) < 2:
            raise ValueError('give a and b: no 2 crossings')
        a = rs[0]
        b = rs[len(rs) - 1]
        out.append(_w('f = g at ' + _f(a) + ' and ' + _f(b)))
        if len(rs) > 2:
            out.append(_warn(str(len(rs)) + ' crossings: outer pair used'))
    if b <= a:
        raise ValueError('need a < b')
    return _area_lines(h, a, b, 'area') + out

def _xofu(us):
    # x in terms of u from u = us(x), or None
    inv = caseng.invert(us, 'x', 'u')
    if inv is None:
        try:
            pf = caspoly.polyfrac(us, 'x')
        except Exception:
            pf = None
        if pf is not None and len(pf[0]) <= 2 and len(pf[1]) == 2:
            N = pf[0] + [caspoly.R0, caspoly.R0]
            b, a = N[0], N[1]
            d, c = pf[1][0], pf[1][1]
            U = ('v', 'u')
            inv = ('/', ('-', ('*', caspoly.ratnode(d), U), caspoly.ratnode(b)),
                   ('-', caspoly.ratnode(a), ('*', caspoly.ratnode(c), U)))
    return None if inv is None else caseng.simplify(inv)

def _uform(t):
    # an integrand in u, expanded so the power rule can see each term
    try:
        e = caspoly.collect(caspoly.expand(t))
        if 'x' not in caseng.vars_in(e):
            return e
    except Exception:
        pass
    return t

def t_subst(f, u, a, b):
    _chk(f, ('x',))
    if caseng.vars_in(u) == ['u']:
        return _subst_rev(f, u, a, b)
    _chk(u, ('x',))
    du = _diff(u)
    if du == ('n', 0):
        raise ValueError('du/dx = 0')
    us = caseng.simplify(u)
    h = caspoly.cancel(caseng.simplify(('/', f, du)))
    inu = caspoly.cancel(caseng.subst_tree(h, us, ('v', 'u')))
    out = [_w('u = ' + _ts(us) + ',  du/dx = ' + _ts(du)),
           _w('f(x)/(du/dx) = ' + _ts(h))]
    if caseng.count_var(inu, 'x'):
        xu = _xofu(us)
        if xu is not None:
            inu = caseng.simplify(caseng.subst(inu, 'x', xu))
            out.append(_w('x = ' + _ts(xu)))
        if xu is None or caseng.count_var(inu, 'x'):
            return [_warn('x remains: try another u')] + out
    inu = _uform(inu)
    head = ['in u: int ' + _ts(inu) + ' du']
    G = _integ(inu, 'u')
    if G is None:
        return [_warn('the u integral is not standard')] + head + out
    back = cascalc.tidy(caseng.subst(G, 'u', us))
    res = ['int f(x) dx =', _m(('+', back, ('v', 'c')))] + head + \
        [_w('in u: int ' + _ts(inu) + ' du = ' + _ts(G))]
    if a is not None and b is not None:
        S = caseng.simplify
        ua = S(caseng.subst(us, 'x', _exnode(a)))
        ub = S(caseng.subst(us, 'x', _exnode(b)))
        val = S(('-', caseng.subst(G, 'u', ub), caseng.subst(G, 'u', ua)))
        vv = casutil.evx(val, 0.0)
        res.insert(0, 'u from ' + _ts(ua) + ' to ' + _ts(ub))
        res.insert(1, 'integral = ' + _ts(val) +
                   ('' if vv is None or _ts(val) == _f(vv) else ' = ' + _f(vv)))
    return res + out + \
        [_w('d/dx of the answer: ' +
            ('agrees' if _agrees(_diff(back), f) else 'DISAGREES'))]

_PYTH = ((('cosec', 'cot'), 1), (('sec', 'tan'), 1), (('sin', 'cos'), -1),
         (('cos', 'sin'), -1))

def _pyth(t):
    # sqrt(k(cosec^2 u - 1)) -> sqrt(k) cot u and the like, u in range
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if len(t) == 3:
        t = (k, _pyth(t[1]), _pyth(t[2]))
    else:
        t = (k, _pyth(t[1]))
    if k != 'sqrt':
        return t
    for (a, b), sg in _PYTH:
        U = ('v', 'u')
        rep = ('+', ('n', 1), ('*', ('n', sg), ('^', (b, U), ('n', 2))))
        e = caseng.subst_tree(caseng.simplify(t[1]), ('^', (a, U), ('n', 2)),
                              rep)
        try:
            e = caseng.simplify(caspoly.expand(e))
        except Exception:
            continue
        raw = []
        caseng._flatadd(e, 1, raw)
        if len(raw) == 1 and e != caseng.simplify(t[1]):
            try:
                return _msqrt(e)
            except ValueError:
                pass
    return t

def _subst_rev(f, g, a, b):
    # x = g(u): int f(g(u)) g'(u) du
    dg = _diff(g, 'u')
    inu = _pyth(caseng.simplify(('*', caseng.subst(f, 'x', g), dg)))
    inu = _uform(caseng.simplify(inu))
    out = ['in u: int ' + _ts(inu) + ' du',
           _w('x = ' + _ts(g) + ',  dx/du = ' + _ts(dg))]
    G = _integ(inu, 'u')
    if G is not None:
        out.insert(0, 'int du = ' + _ts(G) + ' + c')
    else:
        out.append(_warn('the u integral is not standard'))
    if a is not None and b is not None:
        out.append(_w('give the u limits: x = g(u) at x = ' + _f(a) +
                      ' and ' + _f(b)))
    return out

def t_byparts(u, dv):
    _chk(u, ('x',))
    _chk(dv, ('x',))
    v = cascalc.integ(dv)
    if v is None:
        raise ValueError('cannot integrate dv')
    v = cascalc.tidy(v)
    du = _diff(u)
    rest = cascalc.integ(cascalc.tidy(('*', v, du)))
    work = [_w('u = ' + _ts(u) + ',  du/dx = ' + _ts(du)),
            _w('v = int dv dx = ' + _ts(v)),
            _w('int u dv = uv - int v du')]
    if rest is None:
        return [_warn('int v du is not standard'),
                _w('uv = ' + _ts(cascalc.tidy(('*', u, v))))] + work
    res = cascalc.tidy(('-', ('*', u, v), cascalc.tidy(rest)))
    return ['int u dv dx =', _m(('+', res, ('v', 'c')))] + work

def t_riemann(f, a, b):
    _chk(f, ('x',))
    if b <= a:
        raise ValueError('need a < b')
    F = _anti(f)
    ex = _piece(f, F, a, b)
    out = []
    if ex is None:
        out.append(_warn('exact value unavailable'))
    else:
        out.append('integral = ' + _f(ex))
    out.append(_w('left rectangles, width (b-a)/n'))
    for n in (10, 100, 1000):
        h = (b - a) / n
        s = 0.0
        i = 0
        bad = False
        while i < n:
            v = casutil.evx(f, a + i * h)
            if v is None:
                bad = True
                break
            s += v
            i += 1
        if bad:
            out.append(_warn('f undefined in a..b'))
            break
        s = s * h
        ln = 'n = ' + str(n) + '   sum = ' + _g(s)
        if ex is not None:
            ln = ln + '  err ' + _f(s - ex, 2)
        out.append(_w(ln))
    return out

def _negpow(t, var):
    # a / v^n -> a * v^-n, so the power and parts rules can see it
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if len(t) == 3:
        t = (k, _negpow(t[1], var), _negpow(t[2], var))
    else:
        return (k, _negpow(t[1], var))
    if k == '/':
        d = t[2]
        if d == ('v', var):
            return ('*', t[1], ('^', d, ('n', -1)))
        if d[0] == '^' and d[1] == ('v', var) and d[2][0] == 'n':
            return ('*', t[1], ('^', d[1], ('n', -d[2][1])))
    return t

def _integ(f, var):
    # the engine's integral, retried on the expanded form and with
    # 1/x^n written as x^-n
    F = cascalc.integ(f, var)
    k = 0
    while F is None and k < 3:
        try:
            if k == 0:
                g = caspoly.expand(caseng.simplify(f))
            elif k == 1:
                g = _negpow(f, var)
            else:
                # sqrt(16x^3) -> 4x^(3/2), x taken as positive
                g = _mtree(_mono(caseng.simplify(f)))
            F = cascalc.integ(g, var)
        except Exception:
            F = None
        k += 1
    return None if F is None else cascalc.tidy(F)

def _sep(f, g):
    if 'y' in caseng.vars_in(f):
        raise ValueError('f(x) must not contain y')
    if 'x' in caseng.vars_in(g):
        raise ValueError('g(y) must not contain x')
    A = _integ(caseng.simplify(('/', ('n', 1), g)), 'y')
    B = _integ(f, 'x')
    if A is None or B is None:
        raise ValueError('no standard integral')
    return A, B

def _unabs(t, var, v, env):
    # |u| -> u or -u by the sign of u at var = v
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if k == 'abs':
        u = _unabs(t[1], var, v, env)
        e = dict(env)
        e[var] = v
        s = casutil.evx(u, 0.0, e)
        if s is not None and s < 0:
            return caseng.simplify(caseng._negnode(caspoly.expand(u)))
        return u
    if len(t) == 3:
        return (k, _unabs(t[1], var, v, env), _unabs(t[2], var, v, env))
    return (k, _unabs(t[1], var, v, env))

def _eqtxt(L, R, c):
    if c == _ZERO:
        return _ts(L) + ' = ' + _ts(R)
    if caseng._isneg(c):
        return _ts(L) + ' = ' + _ts(R) + ' - ' + _ts(caseng.simplify(('neg', c)))
    return _ts(L) + ' = ' + _ts(R) + ' + ' + _ts(c)

def t_separable(f, g):
    A, B = _sep(f, g)
    return [_ts(A) + ' = ' + _ts(B) + ' + c',
            _w('dy/dx = f(x) g(y)'),
            _w('int 1/g(y) dy = int f(x) dx'),
            _w('int 1/g(y) dy = ' + _ts(A)),
            _w('int f(x) dx = ' + _ts(B))]

def _solved(inv, rhs):
    ex = caseng.simplify(_expfold(cascalc.tidy(caseng.subst(inv, 'u', rhs))))
    try:
        ex2 = caseng.simplify(caspoly.collect(caspoly.expand(ex)))
        if len(_ts(ex2)) < len(_ts(ex)):
            ex = ex2
    except Exception:
        pass
    return ex

def t_separable_pt(f, g, x0, y0):
    A, B = _sep(f, g)
    params = _params(f, ('x',)) + _params(g, ('y',))
    env = _penv(params)
    A = _unabs(A, 'y', y0, env)
    B = _unabs(B, 'x', x0, env)
    S = caseng.simplify
    a0 = S(caseng.subst(A, 'y', _exnode(y0)))
    b0 = S(caseng.subst(B, 'x', _exnode(x0)))
    c = _lncollect(S(('-', a0, b0)))
    cv = casutil.evx(c, 0.0, env)
    rhs = _lncollect(S(('+', B, c)))
    one = _ts(A) + ' = ' + _ts(rhs)
    eqn = _eqtxt(A, B, c)
    out = [eqn, _w('c = ' + _ts(c) +
                                ('' if params or _ts(c) == _f(cv) or cv is None
                                 else ' = ' + _f(cv)))]
    inv = caseng.invert(A, 'y', 'u')
    if inv is not None:
        ex = _solved(inv, S(('+', B, c)))
        e2 = dict(env)
        e2['x'] = x0
        yv = casutil.evx(ex, x0, e2)
        y0v = y0 if not params else y0
        out.insert(0, 'y =')
        out.insert(1, _m(ex))
        out.insert(2, _w('y = ' + _ts(ex)))
        if yv is not None and not (-1e-6 < yv - y0v < 1e-6):
            k = (y0v - yv) / math.pi
            if abs(k - int(round(k))) < 1e-9:
                ex = S(('+', ex, ('*', ('n', int(round(k))), ('v', 'pi'))))
                out[1] = _m(ex)
                out[2] = _w('y = ' + _ts(ex))
                yv = y0v
        if yv is None or not (-1e-6 < yv - y0v < 1e-6):
            out.append(_warn('explicit form misses the point'))
    invb = caseng.invert(B, 'x', 'u')
    if invb is not None and _params(B, ('x',)) == [] and \
            caseng.count_var(B, 'x') == 1:
        xs = S(caseng.subst(invb, 'u', S(('-', A, c))))
        try:
            xs = _lncollect(caspoly.expand(xs))
        except Exception:
            pass
        out.append('x = ' + _ts(xs))
    if one.count('ln(') < eqn.count('ln('):
        out.append(one)
    out.append(_w('int 1/g(y) dy = ' + _ts(A) + ', int f(x) dx = ' + _ts(B)))
    if params:
        out.append(_w(', '.join(params) + ' taken as positive'))
    return out

def t_ftc(f, a):
    _chk(f, ('x',))
    F = _anti(f)
    if F is None:
        raise ValueError('no standard integral')
    A = cascalc.tidy(('-', F, ('n', _val(F, a))))
    return ['A(x) = int a..x f(t) dt', 'A(x) =', _m(A),
            "A'(x) =", _m(_diff(A)),
            _w('A(' + _f(a) + ') = 0, A\'(x) = f(x)'),
            _w('F(x) = ' + _ts(F))]

# ---- I numerical methods ------------------------------------------------------

def t_signchange(f, a, b, n):
    _chk(f, ('x',))
    if b <= a:
        raise ValueError('need a < b')
    n = _posint(n, 10, 50)
    h = (b - a) / n
    xs = []
    ys = []
    i = 0
    while i <= n:
        xv = a + i * h
        xs.append(xv)
        ys.append(casutil.evx(f, xv))
        i += 1
    out = []
    work = []
    i = 0
    while i <= n:
        if ys[i] is None:
            work.append(_warn('f undefined at x = ' + _g(xs[i])))
        else:
            work.append(_w('x = ' + _g(xs[i]) + '   f = ' + _g(ys[i])))
        i += 1
    last = -1
    i = 0
    while i <= n:
        q = ys[i]
        if q is None:
            i += 1
            continue
        if last >= 0:
            p = ys[last]
            if (p < 0 < q) or (q < 0 < p):
                out.append('sign change ' + _g(xs[last]) + ' to ' + _g(xs[i]))
                if last != i - 1:
                    out.append(_warn('f breaks between: not a root'))
                else:
                    mv = casutil.evx(f, (xs[last] + xs[i]) / 2.0)
                    ap = p if p >= 0 else -p
                    aq = q if q >= 0 else -q
                    big = ap if ap > aq else aq
                    if mv is None or (mv > 10 * big or mv < -10 * big):
                        out.append(_warn('may be an asymptote, not a root'))
        last = i
        i += 1
    if not out:
        out.append('no sign change found')
        out.append(_warn('a root may still hide between points'))
    return out + work

def t_newton(f, x0, n):
    _chk(f, ('x',))
    n = _posint(n, 6, 30)
    d = _diff(f)
    x = x0
    out = []
    work = [_w("f'(x) = " + _ts(d)), _w('x(n+1) = x(n) - f(x)/f\'(x)')]
    ok = True
    i = 1
    while i <= n:
        fv = casutil.evx(f, x)
        dv = casutil.evx(d, x)
        if fv is None or dv is None:
            work.append(_warn('cannot evaluate at x = ' + _f(x)))
            ok = False
            break
        if -1e-12 < dv < 1e-12:
            work.append(_warn("f'(x) = 0: Newton-Raphson fails"))
            ok = False
            break
        x = x - fv / dv
        work.append(_w('x' + str(i) + ' = ' + _g(x)))
        i += 1
    if ok:
        out.append('x = ' + _g(x))
        fv = casutil.evx(f, x)
        if fv is None or (fv > 1e-6 or fv < -1e-6):
            out.append(_warn('f(x) = ' + _f(fv) + ': not converged'))
    else:
        out.append('Newton-Raphson failed')
        out.append(_w('last x = ' + _g(x)))
    return out + work

def t_fixed(g, x0, n, k0):
    _chk(g, ('x',))
    n = _posint(n, 8, 30)
    k0 = 0 if k0 is None else _posint(k0 + 1, 1, 10, 'start') - 1
    xs = [x0]
    x = x0
    work = []
    i = 1
    while i <= n:
        v = casutil.evx(g, x)
        if v is None:
            work.append(_warn('g undefined at x = ' + _f(x)))
            break
        x = v
        xs.append(x)
        work.append(_w('x' + str(i + k0) + ' = ' + _g(x)))
        if x > 1e12 or x < -1e12:
            work.append(_warn('diverging'))
            break
        i += 1
    gone = x > 1e6 or x < -1e6
    if len(xs) > 2:
        s1 = xs[len(xs) - 1] - xs[len(xs) - 2]
        s0 = xs[len(xs) - 2] - xs[len(xs) - 3]
        if (s1 if s1 >= 0 else -s1) > (s0 if s0 >= 0 else -s0):
            gone = True
    out = ['the iteration diverges'] if gone else ['x = ' + _g(x)]
    at = x0 if gone else x
    h = 1e-4 * (1.0 + (at if at >= 0 else -at))
    p = casutil.evx(g, at + h)
    q = casutil.evx(g, at - h)
    if p is not None and q is not None:
        gd = (p - q) / (2 * h)
        agd = gd if gd >= 0 else -gd
        out.append(_w("g'(" + _f(at) + ') = ' + _f(gd)))
        if agd < 1:
            out.append(_w("|g'| < 1 so the iteration converges"))
        else:
            out.append(_warn("|g'| >= 1: it will not converge"))
    lo, hi = casutil.nice_range(xs, 0.5)
    import plot
    plot.run([g, X], lo, hi, 'y', 'x = g(x) cobweb')
    return out + work

def t_bisect(f, a, b, n):
    _chk(f, ('x',))
    if b <= a:
        raise ValueError('need a < b')
    n = _posint(n, 8, 40)
    fa = casutil.evx(f, a)
    fb = casutil.evx(f, b)
    if fa is None or fb is None:
        raise ValueError('f undefined at an end')
    if (fa > 0 and fb > 0) or (fa < 0 and fb < 0):
        return ['no sign change in [a, b]',
                _warn('bisection needs f(a), f(b) opposite'),
                _w('f(' + _f(a) + ') = ' + _g(fa)),
                _w('f(' + _f(b) + ') = ' + _g(fb))]
    work = []
    mid = (a + b) / 2.0
    i = 1
    while i <= n:
        mid = (a + b) / 2.0
        fm = casutil.evx(f, mid)
        if fm is None:
            work.append(_warn('f undefined at x = ' + _f(mid)))
            break
        work.append(_w('n' + str(i) + '  m = ' + _g(mid) +
                       '  f = ' + _f(fm, 2)))
        if fm == 0:
            a = mid
            b = mid
            break
        if (fa < 0 and fm < 0) or (fa > 0 and fm > 0):
            a = mid
            fa = fm
        else:
            b = mid
            fb = fm
        i += 1
    return ['x = ' + _g((a + b) / 2.0),
            'root in [' + _g(a) + ', ' + _g(b) + ']',
            _w('max error = ' + _f((b - a) / 2.0, 2))] + work

def t_trapezium(f, a, b, n):
    _chk(f, ('x',))
    if b <= a:
        raise ValueError('need a < b')
    n = _posint(n, 4, 200)
    h = (b - a) / n
    ys = []
    i = 0
    while i <= n:
        v = casutil.evx(f, a + i * h)
        if v is None:
            raise ValueError('f undefined at x = ' + _f(a + i * h))
        ys.append(v)
        i += 1
    s = ys[0] + ys[n]
    i = 1
    while i < n:
        s += 2 * ys[i]
        i += 1
    T = h / 2.0 * s
    out = ['T = ' + _f(T), _w('T = ' + _g(T)), _w('h = (b-a)/n = ' + _f(h)),
           _w('T = h/2 * (y0 + yn + 2*rest)')]
    d2 = _diff(_diff(f))
    sg = _sign_on(d2, a, b)
    if sg > 0:
        out.append('convex: T is an over-estimate')
    elif sg < 0:
        out.append('concave: T is an under-estimate')
    ex = _piece(f, _anti(f), a, b)
    if ex is not None:
        out.append(_w('exact = ' + _f(ex) + ', error = ' + _f(T - ex, 2)))
    if n <= 12:
        i = 0
        while i <= n:
            out.append(_w('y' + str(i) + ' = ' + _g(ys[i])))
            i += 1
    return out

def t_trapdata(h, ys):
    if h <= 0:
        raise ValueError('h must be > 0')
    if len(ys) < 2:
        raise ValueError('give at least two y values')
    n = len(ys) - 1
    s = ys[0] + ys[n]
    i = 1
    while i < n:
        s += 2 * ys[i]
        i += 1
    T = h / 2.0 * s
    return ['T = ' + _f(T), _w('T = ' + _g(T)),
            _w(str(n) + ' strips of width h = ' + _f(h)),
            _w('T = h/2 * (y0 + yn + 2*rest)'),
            _w('y0 + yn = ' + _g(ys[0] + ys[n]) + ', rest = ' +
               _g((s - ys[0] - ys[n]) / 2.0))]

def t_toaccuracy(g, x0, dp):
    _chk(g, ('x',))
    dp = _posint(dp, 3, 8, 'dp')
    tol = 0.5 * math.pow(10.0, -dp)
    x = x0
    work = []
    out = []
    i = 1
    while i <= 50:
        v = casutil.evx(g, x)
        if v is None:
            work.append(_warn('g undefined at x = ' + _g(x)))
            break
        if i <= 12:
            work.append(_w('x' + str(i) + ' = ' + _g(v)))
        d = v - x
        if d < 0:
            d = -d
        same = _dpstr(v, dp) == _dpstr(x, dp)
        x = v
        if d < tol and same:
            out.append('x = ' + _dpstr(x, dp) + ' to ' + str(dp) + ' dp')
            out.append(_w(str(i) + ' iterations, step < ' + _f(tol, 2)))
            break
        i += 1
    if not out:
        out.append('no answer to ' + str(dp) + ' dp')
        out.append(_warn('50 iterations were not enough'))
        out.append(_w('last x = ' + _g(x)))
    return out + work

# ---- J vectors ----------------------------------------------------------------

def _mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def _add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

def _scale(k, a):
    return [k * a[0], k * a[1], k * a[2]]

def _fv(v):
    return casutil.fmtv(v)

def t_vmag(v):
    mg = _mag(v)
    if mg == 0:
        raise ValueError('zero vector')
    out = ['|v| = ' + _f(mg)]
    if v[2] == 0:
        th = casutil.deg(math.atan2(v[1], v[0]))
        out.append('angle from i = ' + _f(th) + ' deg')
        out.append(_w('tan th = ' + _f(v[1]) + ' / ' + _f(v[0])))
        out.append(_w('th = ' + _f(math.atan2(v[1], v[0])) + ' rad'))
    else:
        out.append(_w('angles to i, j, k in degrees:'))
        for i in (0, 1, 2):
            out.append(_w('  ' + 'ijk'[i] + ': ' +
                          _f(casutil.deg(casutil.acos_safe(v[i] / mg)))))
    out.append(_w('|v|^2 = ' + _f(mg * mg)))
    return out

def t_comp(r, th):
    if r < 0:
        raise ValueError('r must be >= 0')
    a = casutil.rad(th)
    x = r * math.cos(a)
    y = r * math.sin(a)
    return ['v = ' + _fv([x, y]),
            _w('th is measured from i in degrees'),
            _w('x = r cos th = ' + _f(r) + ' cos ' + _f(th)),
            _w('y = r sin th = ' + _f(r) + ' sin ' + _f(th))]

def t_vsum(a, b):
    s = _add(a, b)
    d = _sub(a, b)
    return ['a + b = ' + _fv(s), 'a - b = ' + _fv(d),
            _w('|a + b| = ' + _f(_mag(s))),
            _w('|a - b| = ' + _f(_mag(d))),
            _w('|a| = ' + _f(_mag(a)) + ', |b| = ' + _f(_mag(b)))]

def t_vscale(k, a):
    s = _scale(k, a)
    return ['k a = ' + _fv(s), '|k a| = ' + _f(_mag(s)),
            _w('|k| |a| = ' + _f(k if k >= 0 else -k) + ' * ' + _f(_mag(a)))]

def t_unit(v):
    mg = _mag(v)
    if mg == 0:
        raise ValueError('zero vector')
    return ['unit = ' + _fv(_scale(1.0 / mg, v)),
            _w('|v| = ' + _f(mg)),
            _w('each part divided by |v|')]

def t_dist(a, b):
    d = _sub(b, a)
    return ['|AB| = ' + _f(_mag(d)), 'AB = ' + _fv(d),
            _w('AB = b - a'),
            _w('|AB|^2 = ' + _f(_dot(d, d)))]

def t_mid(a, b, mr, nr):
    out = ['midpoint = ' + _fv(_scale(0.5, _add(a, b)))]
    if mr is None and nr is None:
        out.append(_w('midpoint = (a + b)/2'))
        return out
    if mr is None or nr is None:
        out.append(_warn('give both m and n'))
        return out
    if mr + nr == 0:
        raise ValueError('m + n must not be 0')
    p = _scale(1.0 / (mr + nr), _add(_scale(nr, a), _scale(mr, b)))
    out.insert(0, 'm:n point = ' + _fv(p))
    out.append(_w('p = (n a + m b) / (m + n)'))
    out.append(_w('m:n = ' + _f(mr) + ':' + _f(nr)))
    return out

def t_parallel(a, b):
    ma = _mag(a)
    mb = _mag(b)
    if ma == 0 or mb == 0:
        raise ValueError('zero vector')
    cx = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]]
    mc = _mag(cx)
    if mc > 1e-9 * ma * mb:
        return ['not parallel', _w('b is not a multiple of a'),
                _w('|a| = ' + _f(ma) + ', |b| = ' + _f(mb)),
                _w('angle = ' + _f(casutil.deg(casutil.acos_safe(
                    _dot(a, b) / (ma * mb)))) + ' deg')]
    i = 0
    j = 0
    while i < 3:
        if (a[i] if a[i] >= 0 else -a[i]) > (a[j] if a[j] >= 0 else -a[j]):
            j = i
        i += 1
    k = b[j] / a[j]
    return ['parallel: b = ' + _f(k) + ' a',
            'same direction' if k > 0 else 'opposite direction',
            _w('|b| / |a| = ' + _f(mb / ma))]

def t_resultant(xy):
    if len(xy) < 2 or len(xy) % 2:
        raise ValueError('give x,y for each force')
    sx = 0.0
    sy = 0.0
    work = []
    i = 0
    while i < len(xy):
        sx += xy[i]
        sy += xy[i + 1]
        work.append(_w('F' + str(i // 2 + 1) + ' = ' +
                       _fv([xy[i], xy[i + 1]])))
        i += 2
    mg = math.sqrt(sx * sx + sy * sy)
    out = ['R = ' + _fv([sx, sy]), '|R| = ' + _f(mg)]
    if mg > 0:
        out.append('angle = ' + _f(casutil.deg(math.atan2(sy, sx))) + ' deg')
    else:
        out.append('equilibrium: R = 0')
    return out + work

def t_position(r0, v, t):
    r = _add(r0, _scale(t, v))
    return ['r = ' + _fv(r), '|r| = ' + _f(_mag(r)),
            _w('r = r0 + v t'),
            _w('v t = ' + _fv(_scale(t, v))),
            _w('speed |v| = ' + _f(_mag(v)))]

def t_quad4(a, b, c, d):
    P = (a, b, c, d)
    nm = 'ABCD'
    sides = []
    out = []
    for i in range(4):
        v = _sub(P[(i + 1) % 4], P[i])
        sides.append(v)
        out.append(nm[i] + nm[(i + 1) % 4] + ' = ' + _fv(v) + ', |' +
                   nm[i] + nm[(i + 1) % 4] + '| = ' + _f(_mag(v)))
    ln = [_mag(v) for v in sides]
    if min(ln) == 0:
        raise ValueError('two points are the same')

    def par(u, v):
        cx = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0]]
        return _mag(cx) <= 1e-9 * _mag(u) * _mag(v)
    p1 = par(sides[0], sides[2])
    p2 = par(sides[1], sides[3])
    same = abs(ln[0] - ln[1]) < 1e-9 * ln[0] and \
        abs(ln[1] - ln[2]) < 1e-9 * ln[0] and abs(ln[2] - ln[3]) < 1e-9 * ln[0]
    right = abs(_dot(sides[0], sides[1])) < 1e-9 * ln[0] * ln[1]
    if p1 and p2:
        kind = 'square' if same and right else ('rhombus' if same else
                                                 ('rectangle' if right else
                                                  'parallelogram'))
    elif p1 or p2:
        kind = 'trapezium'
    elif abs(ln[0] - ln[1]) < 1e-9 * ln[0] and abs(ln[2] - ln[3]) < 1e-9 * ln[2] or \
            abs(ln[1] - ln[2]) < 1e-9 * ln[1] and abs(ln[3] - ln[0]) < 1e-9 * ln[3]:
        kind = 'kite'
    else:
        kind = 'no special name'
    head = [kind]
    if p1:
        k = -_dot(sides[2], sides[0]) / (ln[0] * ln[0])
        head.append('AB parallel to DC, DC = ' + _f(k) + ' AB')
    if p2:
        head.append('BC parallel to AD')
    return head + out + [_w('a quadrilateral ABCD, in order round it')]

def t_vangle(a, b):
    ma = _mag(a)
    mb = _mag(b)
    if ma == 0 or mb == 0:
        raise ValueError('zero vector')
    dp = _dot(a, b)
    c = dp / (ma * mb)
    ang = casutil.acos_safe(c)
    return ['angle = ' + _f(casutil.deg(ang)) + ' deg',
            '      = ' + _f(ang) + ' rad',
            _w('a.b = ' + _f(dp)),
            _w('cos = a.b / (|a||b|) = ' + _f(c)),
            _w('|a| = ' + _f(ma) + ', |b| = ' + _f(mb))]

SECTIONS = [
    ('G', 'Differentiation', [
        ("Derivative f' and f''", 'f(x)', t_deriv),
        ('Tangent and normal', 'f(x),a', t_tangent),
        ('Stationary points', 'f(x)', t_stationary),
        ('Inflection points', 'f(x)', t_inflect),
        ('Increasing/decreasing', 'f(x)', t_incdec),
        ('First principles', 'f(x),a', t_firstprin),
        ('Parametric dy/dx', 'x(t),y(t),t?', t_param),
        ('Implicit dy/dx', 'F(xy),x?,y?', t_implicit),
        ('Implicit dy/dx = 0', 'F(xy),x?', t_implicit0),
        ('Connected rates', 'y(x),x,dx/dt', t_connected),
        ('Inverse derivative', 'f(x),a', t_invderiv),
        ("f, f' and f'' at a", 'f(x),a', t_valat),
    ]),
    ('H', 'Integration', [
        ('Indefinite integral', 'f(x)', t_indef),
        ('Definite integral', 'f(x),a,b', t_defint),
        ('Area under curve', 'f(x),a,b', t_area),
        ('Area between curves', 'f(x),g(x),a?,b?', t_between),
        ('Substitution u=g(x)', 'f(x),u(x),a?,b?', t_subst),
        ('Integration by parts', 'u(x),dv(x)', t_byparts),
        ('Riemann sum table', 'f(x),a,b', t_riemann),
        ('Separable DE', 'f(x),g(y)', t_separable),
        ('Separable DE at point', 'f(x),g(y),x0,y0', t_separable_pt),
        ('d/dx of an integral', 'f(x),a', t_ftc),
    ]),
    ('I', 'Numerical methods', [
        ('Sign change table', 'f(x),a,b,n?', t_signchange),
        ('Newton-Raphson', 'f(x),x0,n?', t_newton),
        ('Fixed point x=g(x)', 'g(x),x0,n?,i0?', t_fixed),
        ('Bisection', 'f(x),a,b,n?', t_bisect),
        ('Trapezium rule', 'f(x),a,b,n', t_trapezium),
        ('Trapezium from y values', 'h,y values*', t_trapdata),
        ('Iterate to n dp', 'g(x),x0,dp', t_toaccuracy),
    ]),
    ('J', 'Vectors', [
        ('Magnitude and angle', 'v[3]', t_vmag),
        ('Components from r,th', 'r,thdeg', t_comp),
        ('Sum and difference', 'a[3],b[3]', t_vsum),
        ('Scalar multiple k a', 'k,a[3]', t_vscale),
        ('Unit vector', 'v[3]', t_unit),
        ('Distance A to B', 'a[3],b[3]', t_dist),
        ('Midpoint and ratio', 'a[3],b[3],m?,n?', t_mid),
        ('Parallel test', 'a[3],b[3]', t_parallel),
        ('Resultant of forces', 'xy*', t_resultant),
        ('Position r0 + v t', 'r0[3],v[3],t', t_position),
        ('Angle between vectors', 'a[3],b[3]', t_vangle),
        ('Quadrilateral ABCD', 'a[3],b[3],c[3],d[3]', t_quad4),
    ]),
]
