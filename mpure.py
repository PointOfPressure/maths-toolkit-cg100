# AQA 7357 sections A-F: proof, algebra and functions, coordinate geometry,
# sequences and series, trigonometry, exponentials and logarithms.
import math
import caslex
import caseng
import cascalc
import caspoly
import casalg
import casutil

fmt = casutil.fmt
sf3 = casutil.sf3
w = casutil.w
warn = casutil.warn
m = casutil.m

# ---------------------------------------------------------------- numbers --

def _isint(v):
    if isinstance(v, bool) or isinstance(v, complex):
        return False
    if isinstance(v, int):
        return True
    return v == int(v) and -1e12 < v < 1e12


def _whole(v, name):
    if isinstance(v, complex):
        raise ValueError(name + ' must be real')
    f = float(v)
    if f > 1e12 or f < -1e12:
        raise ValueError(name + ' is too large')
    n = int(f)
    if f - n >= 0.5:
        n += 1
    elif n - f >= 0.5:
        n -= 1
    d = f - n
    if d > 1e-9 or d < -1e-9:
        raise ValueError(name + ' must be a whole number')
    return n


def _pos(v, name):
    if v <= 0:
        raise ValueError(name + ' must be positive')
    return v


def _span(lo, hi, cap):
    a = _whole(lo, 'lo')
    b = _whole(hi, 'hi')
    if b < a:
        raise ValueError('hi must be at least lo')
    if b - a > cap:
        raise ValueError('range is too wide')
    return (a, b)


def _sqsplit(n):
    # n = a*a*b, b square free as far as factors up to 4096 can tell; n >= 0
    a = 1
    b = int(n)
    d = 2
    while d <= 4096 and d * d <= b:
        while b % (d * d) == 0:
            b //= d * d
            a *= d
        d += 1 if d == 2 else 2
    return (a, b)


def _iroot(a, q):
    # exact integer q-th root of a, or None
    if q <= 0 or q > 64:
        return None
    if a < 0:
        if q % 2 == 0:
            return None
        r = _iroot(-a, q)
        return None if r is None else -r
    if a == 0:
        return 0
    r = int(a ** (1.0 / q) + 0.5)
    for k in (r - 1, r, r + 1):
        if k >= 0 and k ** q == a:
            return k
    return None


def _isprime(n):
    # True, False, or None when n is too big to trial divide here
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        if d > 200000:
            return None
        d += 2
    return True


def _smallfactor(n):
    d = 2
    while d * d <= n:
        if n % d == 0:
            return d
        d += 1
    return n

# ------------------------------------------------------- exact surd sums --
# A surd sum is a list of (num, den, rad): sum of num/den * sqrt(rad),
# rad a square-free positive integer, den > 0, num != 0, rads distinct.


def _mk(n, d, r):
    if n == 0 or d == 0:
        return None
    a, b = _sqsplit(r)
    n = n * a
    if d < 0:
        n = -n
        d = -d
    g = casutil.gcd(n, d)
    if g:
        n //= g
        d //= g
    return (n, d, b)


def _ss(n, d, r):
    t = _mk(n, d, r)
    return [] if t is None else [t]


def _ssnorm(terms):
    out = []
    for t in terms:
        if t is None or t[0] == 0:
            continue
        hit = -1
        for i in range(len(out)):
            if out[i][2] == t[2]:
                hit = i
                break
        if hit < 0:
            out.append(t)
        else:
            o = out[hit]
            n = o[0] * t[1] + t[0] * o[1]
            d = o[1] * t[1]
            g = casutil.gcd(n, d)
            if g:
                n //= g
                d //= g
            if n == 0:
                out.pop(hit)
            else:
                out[hit] = (n, d, o[2])
    out.sort()
    return out


def _ssadd(a, b):
    return _ssnorm(list(a) + list(b))


def _ssneg(a):
    return [(-t[0], t[1], t[2]) for t in a]


def _ssmul(a, b):
    out = []
    for p in a:
        for q in b:
            out.append(_mk(p[0] * q[0], p[1] * q[1], p[2] * q[2]))
    return _ssnorm(out)


def _ssdiv(a, b):
    b = _ssnorm(b)
    if not b:
        return None
    if len(b) == 1:
        n2, d2, r2 = b[0]
        out = []
        for n1, d1, r1 in a:
            out.append(_mk(n1 * d2, d1 * n2 * r2, r1 * r2))
        return _ssnorm(out)
    if len(b) == 2:
        conj = [b[0], (-b[1][0], b[1][1], b[1][2])]
        return _ssdiv(_ssmul(a, conj), _ssmul(b, conj))
    return None


def _ssval(a):
    v = 0.0
    for n, d, r in a:
        v += n / float(d) * math.sqrt(r)
    return v


def _ssrat(a):
    # exact rational (n, d) when the sum has no surd part, else None
    if not a:
        return (0, 1)
    if len(a) == 1 and a[0][2] == 1:
        return (a[0][0], a[0][1])
    return None


def _sterm(n, r):
    if r == 1:
        return ('n', n)
    if n == 1:
        return ('sqrt', ('n', r))
    return ('*', ('n', n), ('sqrt', ('n', r)))


def _sstree(a):
    if not a:
        return ('n', 0)
    lcm = 1
    for t in a:
        lcm = casutil.lcm(lcm, t[1])
    nums = [(t[0] * (lcm // t[1]), t[2]) for t in a]
    g = lcm
    for n, r in nums:
        g = casutil.gcd(g, n)
    if g > 1:
        lcm //= g
        nums = [(n // g, r) for n, r in nums]
    order = [p for p in nums if p[0] > 0] + [p for p in nums if p[0] < 0]
    node = None
    for n, r in order:
        an = n if n > 0 else -n
        piece = _sterm(an, r)
        if node is None:
            node = piece if n > 0 else ('neg', piece)
        else:
            node = ('+', node, piece) if n > 0 else ('-', node, piece)
    if lcm != 1:
        node = ('/', node, ('n', lcm))
    return node


def _ssstr(a):
    r = _ssrat(a)
    if r is not None:
        return str(r[0]) if r[1] == 1 else str(r[0]) + '/' + str(r[1])
    return caseng.tostr(_sstree(a))


def _cxstr(re, im, sgn):
    istr = _ssstr(im)
    part = 'i' if istr == '1' else istr + 'i'
    rs = _ssstr(re)
    if rs == '0':
        return part if sgn > 0 else '-' + part
    return rs + ('+' if sgn > 0 else '-') + part

# ---------------------------------------------------------- tree helpers --


def _ratnode(n, d):
    r = caspoly.rmake(n, d)
    if r is None:
        raise ValueError('division by zero')
    return caspoly.ratnode(r)


def _numnode(v):
    if _isint(v):
        return ('n', int(v))
    return ('n', float(v))


def _val(tree, x, deg=False, var='x'):
    try:
        env = None if var == 'x' else {var: x}
        v = caseng.evalf(tree, x, deg, env)
    except Exception:
        return None
    if isinstance(v, complex):
        return None
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v


def _snap(v):
    if v is not None and v < 1e-10 and v > -1e-10:
        return 0.0
    return v

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
        if var == 'xy' and t[1] in ('x', 'y'):
            j = 0 if t[1] == 'x' else 1
            return lambda x: x[j]
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


def _fbis(g, a, b, fa):
    # Illinois false position, bisecting when it stalls
    fb = g(b)
    if fb is None:
        return None
    if fb == 0:
        return b
    side = 0
    c = (a + b) / 2.0
    k = 0
    while k < 80:
        if k % 8 == 7 or fb == fa:
            c = (a + b) / 2.0
        else:
            c = (a * fb - b * fa) / (fb - fa)
            if not (min(a, b) <= c <= max(a, b)):
                c = (a + b) / 2.0
        if c == a or c == b:
            return c
        fc = g(c)
        if fc is None:
            return None
        if fc == 0 or abs(b - a) <= 1e-15 * (1.0 + abs(c)):
            return c
        if (fc < 0) == (fb < 0):
            b = c
            fb = fc
            if side == -1:
                fa = fa / 2.0
            side = -1
        else:
            a = c
            fa = fc
            if side == 1:
                fb = fb / 2.0
            side = 1
        k += 1
    return c


def _fmin(g, a, b, sgn):
    # ternary search for the least sgn * g on [a, b]
    k = 0
    while k < 50:
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        v1 = g(m1)
        v2 = g(m2)
        if v1 is None or v2 is None:
            return None
        if sgn * v1 <= sgn * v2:
            b = m2
        else:
            a = m1
        k += 1
    return (a + b) / 2.0


def _nice(x, g=None):
    # snap x to a near whole number or simple fraction when g agrees
    for d in (1, 2, 3, 4, 6, 12):
        r = round(x * d) / float(d)
        if abs(r - x) < 1e-7 * (1.0 + abs(x)):
            if g is None:
                return r
            u = g(r)
            v = g(x)
            if u is not None and v is not None and \
                    abs(u - v) <= 1e-9 * (1.0 + abs(v)):
                return r
    return x


def _vertex(p, y, q):
    # does the parabola through three samples dip to about 0?
    c = p - 2.0 * y + q
    if c == 0:
        return False
    v = y - (q - p) * (q - p) / (8.0 * c)
    return abs(v) < 0.05 * (abs(p) + abs(q)) or (v < 0) != (y < 0)


def _froots(g, xs, ys=None):
    # roots of g (a fast function) between the sorted sample points xs:
    # sign changes, and touching zeros of |g| at local minima
    if ys is None:
        ys = [g(x) for x in xs]
    out = []
    n = len(xs)
    p = ys[0]
    q = None
    i = 1
    while i < n:
        y = ys[i]
        if y is None or p is None:
            q = None
        elif p == 0:
            if abs(y) > 1e-100 or (i > 1 and abs(ys[i - 2] or 0) > 1e-100):
                cascalc._add(out, xs[i - 1])
            q = None
        elif (p < 0) != (y < 0):
            if y != 0:
                r = _fbis(g, xs[i - 1], xs[i], p)
                if r is not None:
                    v = g(r)
                    if v is not None and \
                            abs(v) <= 1e-6 * (1.0 + min(abs(p), abs(y))):
                        cascalc._add(out, _snap(_nice(r)))
            q = None
        else:
            if q is not None and (y > p if p > 0 else y < p) and \
                    (p < q if p > 0 else p > q) and _vertex(q, p, y):
                r = _fmin(g, xs[i - 2], xs[i], 1 if p > 0 else -1)
                v = None if r is None else g(r)
                if v is not None and abs(v) <= 1e-9 * (1.0 + abs(q)):
                    cascalc._add(out, _snap(_nice(r)))
                elif v is not None and (v < 0) != (p < 0):
                    for a, b, fa in ((xs[i - 2], r, q), (r, xs[i], v)):
                        z = _fbis(g, a, b, fa)
                        gz = None if z is None else g(z)
                        if gz is not None and \
                                abs(gz) <= 1e-6 * (1.0 + min(abs(q), abs(v))):
                            cascalc._add(out, _snap(_nice(z)))
            q = p
        p = y
        i += 1
    if n > 1 and ys[n - 1] == 0 and abs(ys[n - 2] or 0) > 1e-100:
        cascalc._add(out, xs[n - 1])
    out.sort()
    return out


def _grid(lo, hi, n):
    h = (hi - lo) / n
    out = [lo]
    x = lo
    i = 1
    while i < n:
        x += h
        out.append(x)
        i += 1
    out.append(hi)
    return out


def _farxs(lo, hi, top, n):
    # log-spaced points from |lo| or |hi| out to +-top
    out = []
    if hi < top:
        a = hi if hi > 1.0 else 1.0
        r = math.pow(top / a, 1.0 / n)
        out.append([a * r ** i for i in range(n + 1)])
    if lo > -top:
        a = -lo if lo < -1.0 else 1.0
        r = math.pow(top / a, 1.0 / n)
        pts = [-a * r ** i for i in range(n + 1)]
        pts.reverse()
        out.append(pts)
    return out


def _fast(tree, var='x', deg=False):
    # f(x) -> float or None; falls back to _val for anything unusual.
    # var 'xy' makes f take the pair (x, y).
    g = _comp(tree, var, deg)
    if g is None:
        if var == 'xy':
            return lambda p: _val(caseng.subst(tree, 'y', ('n', p[1])), p[0])
        return lambda x: _val(tree, x, deg, var)

    def f(x):
        try:
            v = g(x)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        if isinstance(v, complex) or v != v or v > 1e300 or v < -1e300:
            return None
        return v
    return f


def _need(tree, x, deg=False, var='x'):
    v = _val(tree, x, deg, var)
    if v is None:
        raise ValueError('cannot evaluate there')
    return v


def _bis(tree, a, b, deg, var):
    fa = _val(tree, a, deg, var)
    fb = _val(tree, b, deg, var)
    if fa is None or fb is None:
        return None
    if fa == 0.0:
        return _snap(a)
    if fb == 0.0:
        return _snap(b)
    if (fa < 0) == (fb < 0):
        return None
    i = 0
    while i < 80:
        mid = (a + b) / 2.0
        if mid == a or mid == b:
            break
        fm = _val(tree, mid, deg, var)
        if fm is None:
            return None
        if fm == 0.0:
            return _snap(mid)
        if (fa < 0) == (fm < 0):
            a = mid
            fa = fm
        else:
            b = mid
        i += 1
    return _snap((a + b) / 2.0)


def _ok_root(tree, r, scale, deg, var):
    # a sign change across a pole is not a root: check f is really ~0 there
    if r is None:
        return False
    v = _val(tree, r, deg, var)
    if v is None:
        return False
    av = v if v >= 0 else -v
    return av <= 1e-6 * (1.0 + scale)


def _roots(tree, lo, hi, deg=False, var='x', n=600, ys=None):
    return _froots(_fast(tree, var, deg), _grid(lo, hi, n), ys)


def _scan(tree, lo, hi, deg, var='x'):
    span = hi - lo
    if span <= 0:
        raise ValueError('hi must be more than lo')
    n = int(span * (1.0 if deg else 60.0))
    if n < 240:
        n = 240
    if n > 1440:
        n = 1440
    return _roots(tree, lo, hi, deg, var, n)


def _polyof(tree, name):
    p = caspoly.poly(tree, 'x')
    if p is None:
        raise ValueError(name + ' is not a polynomial in x')
    return p


def _pgcd(a, b):
    a = caspoly.ptrim(list(a))
    b = caspoly.ptrim(list(b))
    guard = 0
    while b and guard < 24:
        guard += 1
        qr = caspoly.pdivmod(a, b)
        if qr is None:
            return [caspoly.R1]
        a = b
        b = caspoly.ptrim(qr[1])
    if not a:
        return [caspoly.R1]
    lead = a[-1]
    return [caspoly.rdiv(c, lead) for c in a]

# -------------------------------------------------------------- monomials --
# (coef, items): coef an exact (p, q), items [[base, exp tree]]. Letters are
# taken as positive, so sqrt(a^2 b) = a sqrt(b).

_ONE = ('n', 1)


def _qsplit(n, q):
    # n = a^q * b with b free of q-th powers (trial division to 400)
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
    k = t[0]
    if k == 'n':
        r = caseng._ratval(t)
        if r is not None:
            return (r, [])
        return ((1, 1), [[t, _ONE, caseng.tostr(t)]])
    if k == 'neg':
        a = _mono(t[1])
        return ((-a[0][0], a[0][1]), a[1])
    if k == '*' or k == '/':
        a = _mono(t[1])
        b = _mono(t[2])
        if k == '/':
            if b[0][0] == 0:
                raise ValueError('division by zero')
            b = _mpow(b, (-1, 1))
        c = caspoly.rmul(a[0], b[0])
        items = [[x[0], x[1], x[2]] for x in a[1]]
        for x in b[1]:
            _mput(items, x[0], x[1])
        return (c, items)
    if k == 'sqrt':
        return _mpow(_mono(t[1]), (1, 2))
    if k == 'exp':
        return ((1, 1), [[('v', 'e'), t[1], 'e']])
    if k == '^':
        r = caseng._ratval(t[2])
        a = _mono(t[1])
        if r is not None:
            return _mpow(a, r)
        return _mpow(a, t[2])
    return ((1, 1), [[t, _ONE, caseng.tostr(t)]])


def _mpow(a, r):
    # a^r, r an exact (p, q) or an exponent tree
    c, items = a
    out = []
    if isinstance(r, tuple) and len(r) == 2 and isinstance(r[0], int):
        p, q = r
        e = caspoly.ratnode(caspoly.rmake(p, q))
        for b, x, key in items:
            _mput(out, b, caseng.simplify(('*', x, e)))
        num = c[0]
        den = c[1]
        if num == 0:
            return ((0, 1), [])
        if num < 0 and q % 2 == 0:
            _mput(out, ('n', -1), e)
            num = -num
        sg = -1 if num < 0 else 1
        num = num * sg
        if q % 2 == 0:
            sg = 1
        a1, b1 = _qsplit(num, q)
        a2, b2 = _qsplit(den, q)
        if b1 != 1:
            _mput(out, ('n', b1), e)
        if b2 != 1:
            _mput(out, ('n', b2), caseng.simplify(('neg', e)))
        if p >= 0:
            cc = caspoly.rmake(sg * a1 ** p, a2 ** p)
        else:
            cc = caspoly.rmake(sg * a2 ** (-p), a1 ** (-p))
        return (cc, out)
    for b, x, key in items:
        _mput(out, b, caseng.simplify(('*', x, r)))
    if c != (1, 1):
        if c[0] < 0:
            raise ValueError('negative base')
        if c[0] != 1:
            _mput(out, ('n', c[0]), r)
        if c[1] != 1:
            _mput(out, ('n', c[1]), caseng.simplify(('neg', r)))
    return ((1, 1), out)


def _mtree(a):
    c, items = a
    parts = []
    for b, e, key in items:
        if e == ('n', 0):
            continue
        parts.append(b if e == _ONE else ('^', b, e))
    node = None
    for p in parts:
        node = p if node is None else ('*', node, p)
    cn = caspoly.ratnode(c)
    if node is None:
        return cn
    if c != (1, 1):
        node = ('*', cn, node)
    return caseng.simplify(node)


def _msqrt(t):
    return _mtree(_mpow(_mono(caseng.simplify(t)), (1, 2)))

# ------------------------------------------------------- linear text bits --


def _term(v, name, first):
    if v == 0:
        return ''
    av = -v if v < 0 else v
    body = '' if (name != '' and av == 1) else fmt(av)
    if name != '' and body.find('/') >= 0:
        body = '(' + body + ')'
    txt = body + name
    if first:
        return ('-' if v < 0 else '') + txt
    return (' - ' if v < 0 else ' + ') + txt


def _linstr(coeffs, names):
    s = ''
    for i in range(len(coeffs)):
        piece = _term(coeffs[i], names[i], s == '')
        s += piece
    return s if s else '0'


def _quadstr(a, b, c):
    return _linstr([a, b, c], ['x^2', 'x', ''])


def _lineeq(m0, c0):
    return 'y = ' + _linstr([m0, c0], ['x', ''])


def _whole_scale(vals):
    k = 1
    while k <= 60:
        ok = True
        for v in vals:
            u = v * k
            d = u - int(u + 0.5 if u >= 0 else u - 0.5)
            if d > 1e-9 or d < -1e-9:
                ok = False
                break
        if ok:
            return k
        k += 1
    return 0


def _general(A, B, C):
    # A x + B y + C = 0, scaled to whole numbers when possible
    k = _whole_scale([A, B, C])
    if k:
        A = A * k
        B = B * k
        C = C * k
    if _isint(A) and _isint(B) and _isint(C):
        A = int(A)
        B = int(B)
        C = int(C)
        g = casutil.gcd(casutil.gcd(A, B), C)
        if g > 1:
            A //= g
            B //= g
            C //= g
        if A < 0 or (A == 0 and B < 0):
            A = -A
            B = -B
            C = -C
    return _linstr([A, B, C], ['x', 'y', '']) + ' = 0'

# =========================================================== A  Proof ======


def _nval(tree, n):
    return _val(tree, float(n), False, 'n')


def _cex_hit(f, n, detail, a, b):
    return ['counterexample n = ' + str(n), detail,
            w('f(n) = ' + caseng.tostr(caseng.simplify(f))),
            w('searched n = ' + str(a) + ' to ' + str(b))]


def _cex_miss(f, a, b):
    return ['no counterexample found',
            warn('n = ' + str(a) + ' to ' + str(b) + ' only: not a proof'),
            w('f(n) = ' + caseng.tostr(caseng.simplify(f)))]


def t_cex_pos(f, lo, hi):
    a, b = _span(lo, hi, 2000)
    n = a
    while n <= b:
        v = _nval(f, n)
        if v is None:
            return _cex_hit(f, n, 'f(' + str(n) + ') is undefined', a, b)
        if v <= 0:
            return _cex_hit(f, n, 'f(' + str(n) + ') = ' + fmt(v), a, b)
        n += 1
    return _cex_miss(f, a, b)


def t_cex_prime(f, lo, hi):
    a, b = _span(lo, hi, 2000)
    n = a
    while n <= b:
        v = _nval(f, n)
        if v is None:
            return _cex_hit(f, n, 'f(' + str(n) + ') is undefined', a, b)
        k = int(v + 0.5) if v >= 0 else int(v - 0.5)
        if v - k > 1e-6 or k - v > 1e-6:
            return _cex_hit(f, n, 'f(' + str(n) + ') = ' + fmt(v) +
                            ' not whole', a, b)
        pr = _isprime(k)
        if pr is None:
            return _cex_hit(f, n, 'f(' + str(n) + ') is too big to test',
                            a, b)
        if not pr:
            d = _smallfactor(k) if k > 1 else 0
            if k > 1:
                det = 'f(' + str(n) + ') = ' + str(d) + ' x ' + str(k // d)
            else:
                det = 'f(' + str(n) + ') = ' + str(k) + ' is not prime'
            return _cex_hit(f, n, det, a, b)
        n += 1
    return _cex_miss(f, a, b)


def t_cex_div(f, d, lo, hi):
    di = _whole(d, 'd')
    if di == 0:
        raise ValueError('d must not be 0')
    a, b = _span(lo, hi, 2000)
    n = a
    while n <= b:
        v = _nval(f, n)
        if v is None:
            return _cex_hit(f, n, 'f(' + str(n) + ') is undefined', a, b)
        k = int(v + 0.5) if v >= 0 else int(v - 0.5)
        if v - k > 1e-6 or k - v > 1e-6:
            return _cex_hit(f, n, 'f(' + str(n) + ') = ' + fmt(v) +
                            ' not whole', a, b)
        if k % di != 0:
            return _cex_hit(f, n, 'f(' + str(n) + ') = ' + str(k) + ', rem ' +
                            str(k % di), a, b)
        n += 1
    return _cex_miss(f, a, b)


def t_cex_eq(f, g, lo, hi):
    a, b = _span(lo, hi, 2000)
    n = a
    while n <= b:
        u = _nval(f, n)
        v = _nval(g, n)
        if u is None or v is None:
            return _cex_hit(f, n, 'one side is undefined', a, b)
        gap = u - v
        tol = 1e-7 * (1.0 + (u if u >= 0 else -u))
        if gap > tol or gap < -tol:
            return _cex_hit(f, n, 'f = ' + fmt(u) + ', g = ' + fmt(v), a, b)
        n += 1
    return ['no counterexample found',
            warn('n = ' + str(a) + ' to ' + str(b) + ' only: not a proof'),
            w('f(n) = ' + caseng.tostr(caseng.simplify(f))),
            w('g(n) = ' + caseng.tostr(caseng.simplify(g)))]

# ============================================ B  Algebra and functions =====


def t_index(a, p, q):
    qi = _whole(q, 'q')
    pi = _whole(p, 'p')
    if qi == 0:
        raise ValueError('q must not be 0')
    if qi > 64 or qi < -64 or pi > 200 or pi < -200:
        raise ValueError('keep p within 200 and q within 64')
    if qi < 0:
        qi = -qi
        pi = -pi
    lines = []
    if _isint(a):
        ai = int(a)
        r = _iroot(ai, qi)
        if r is not None:
            if pi >= 0:
                lines.append('= ' + str(r ** pi))
            else:
                lines.append('= ' + _ssstr(_ss(1, r ** (-pi), 1)))
            lines.append(w('root ' + str(qi) + ' of ' + str(ai) + ' = ' +
                           str(r)))
    if a < 0 and qi % 2 == 0:
        return lines + [warn('even root of a negative: not real')]
    if a >= 0:
        v = math.pow(float(a), pi / float(qi))
    else:
        v = math.pow(-float(a), pi / float(qi))
        if pi % 2:
            v = -v
    if not lines:
        lines.append('= ' + fmt(v))
    lines.append('decimal = ' + sf3(v))
    lines.append(w(fmt(a) + '^(' + str(pi) + '/' + str(qi) + ')'))
    return lines


def t_surd(n):
    ni = _whole(n, 'n')
    t = caseng.simplify(('sqrt', ('n', ni)))
    lines = [m(t), 'sqrt(' + str(ni) + ') = ' + caseng.tostr(t)]
    if ni >= 0:
        a, b = _sqsplit(ni)
        if b != 1 and a != 1:
            lines.append(w('sqrt(' + str(a * a) + ' x ' + str(b) + ') = ' +
                           str(a) + 'sqrt(' + str(b) + ')'))
        lines.append('decimal = ' + sf3(math.sqrt(ni)))
    else:
        lines.append(warn('negative: the root is imaginary'))
    return lines


def _sqfree(r):
    # square-free part of a positive rational (p, q) as an int
    a, b = _sqsplit(r[0] * r[1])
    return b


def _halfx(t, ks):
    # collect the k in each sqrt(k x) / x^(n/2); False if another x root
    k = t[0]
    if k == 'n' or k == 'v':
        return True
    if k == 'sqrt' or (k == '^' and caseng._ratval(t[2]) is not None and
                       caseng._ratval(t[2])[1] == 2):
        inner = t[1]
        if 'x' in caseng.vars_in(inner):
            mo = _mono(caseng.simplify(inner))
            if len(mo[1]) != 1 or mo[1][0][0] != ('v', 'x') or \
                    mo[1][0][1] != _ONE or mo[0][0] <= 0:
                return False
            ks.append(_sqfree(mo[0]))
            return True
    if k == '^' and 'x' in caseng.vars_in(t[1]):
        r = caseng._ratval(t[2])
        if r is None or r[1] != 1:
            return False
    if len(t) == 3:
        return _halfx(t[1], ks) and _halfx(t[2], ks)
    return _halfx(t[1], ks)


def _roots_u(t, var='u'):
    # sqrt(c u^2) -> u sqrt(c), (u^2)^(n/2) -> u^n with u > 0
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if len(t) == 3:
        t = (k, _roots_u(t[1], var), _roots_u(t[2], var))
    else:
        t = (k, _roots_u(t[1], var))
    if k == 'sqrt' and var in caseng.vars_in(t[1]):
        return _mtree(_mpow(_mono(caseng.simplify(t[1])), (1, 2)))
    if k == '^' and var in caseng.vars_in(t[1]):
        r = caseng._ratval(t[2])
        if r is not None and r[1] > 1:
            return _mtree(_mpow(_mono(caseng.simplify(t[1])), r))
    return t


def _evenodd(p):
    # p(u) = E(u^2) + u O(u^2)
    E = []
    O = []
    i = 0
    while i < len(p):
        if i % 2 == 0:
            E.append(p[i])
        else:
            O.append(p[i])
        i += 1
    return (caspoly.ptrim(E), caspoly.ptrim(O))


def _xpoly(p, s):
    # q(u^2) with u^2 = s x -> polynomial in x
    return [caspoly.rmul(p[i], (s ** i, 1)) for i in range(len(p))]


def _surdx(f):
    # f in sqrt(s x): cancelled and rationalised, or None
    ks = []
    if caseng.vars_in(f) != ['x'] or not _halfx(f, ks) or not ks:
        return None
    s = ks[0]
    for k in ks:
        if k != s:
            return None
    U = ('v', 'u')
    g = caseng.subst(f, 'x', ('/', ('^', U, ('n', 2)), ('n', s)))
    g = caseng.simplify(_roots_u(g))
    pf = caspoly.polyfrac(g, 'u')
    if pf is None:
        return None
    N = caspoly.ptrim(list(pf[0]))
    D = caspoly.ptrim(list(pf[1])) if pf[1] else [caspoly.R1]
    if not N:
        return (('n', 0), s)
    gg = _pgcd(N, D)
    if len(gg) > 1:
        N = caspoly.pdivmod(N, gg)[0]
        D = caspoly.pdivmod(D, gg)[0]
    De, Do = _evenodd(D)
    if Do:
        conj = [c if i % 2 == 0 else caspoly.rneg(c) for i, c in
                enumerate(D)]
        N = caspoly.pmul(N, conj)
        D = caspoly.pmul(D, conj)
        De, Do = _evenodd(D)
    E, O = _evenodd(N)
    Ex = _xpoly(E, s)
    Ox = _xpoly(O, s)
    Dx = _xpoly(De, s)
    L = 1
    for c in Ex + Ox + Dx:
        L = casutil.lcm(L, c[1])
    lead = Dx[len(Dx) - 1]
    sc = (L, 1) if lead[0] > 0 else (-L, 1)
    Ex = [caspoly.rmul(c, sc) for c in Ex]
    Ox = [caspoly.rmul(c, sc) for c in Ox]
    Dx = [caspoly.rmul(c, sc) for c in Dx]
    g2 = 0
    for c in Ex + Ox + Dx:
        g2 = casutil.gcd(g2, c[0])
    if g2 > 1:
        Ex = [(c[0] // g2, 1) for c in Ex]
        Ox = [(c[0] // g2, 1) for c in Ox]
        Dx = [(c[0] // g2, 1) for c in Dx]
    X = ('v', 'x')
    root = ('sqrt', X if s == 1 else ('*', ('n', s), X))
    top = caspoly.ptree(Ex, 'x') if caspoly.ptrim(list(Ex)) else None
    if caspoly.ptrim(list(Ox)):
        ot = caspoly.ptree(Ox, 'x')
        piece = root if ot == _ONE else ('*', ot, root)
        if ot == ('n', -1):
            piece = ('neg', root)
        top = piece if top is None else ('+', top, piece)
    if top is None:
        top = ('n', 0)
    if caspoly.ptrim(list(Dx)) == [caspoly.R1]:
        return (top, s)
    return (('/', top, caspoly.ptree(Dx, 'x')), s)


def t_surdexpr(f):
    try:
        sx = _surdx(f)
    except (ValueError, TypeError, ZeroDivisionError):
        sx = None
    if sx is not None:
        t, s = sx
        u = 'sqrt(x)' if s == 1 else 'sqrt(' + str(s) + 'x)'
        return [m(t), '= ' + caseng.tostr(t),
                w('u = ' + u + ': simplified as a fraction in u'),
                w('surds cleared from the denominator')]
    t = caseng.simplify(f)
    if caseng.vars_in(t) == ['x']:
        t2 = caseng.simplify(_roots_u(t, 'x'))
        if caseng.tostr(t2) != caseng.tostr(t):
            return [m(t2), '= ' + caseng.tostr(t2), w('x > 0 assumed')]
    lines = [m(t)]
    if not caseng.vars_in(t):
        v = casutil.ev(t)
        lines.append('= ' + fmt(v))
        lines.append('decimal = ' + sf3(v))
    return lines


def t_rationalise(a, b, c, d, e, f):
    ci = _whole(c, 'c')
    fi = _whole(f, 'f')
    if ci < 0 or fi < 0:
        raise ValueError('c and f must not be negative')
    for v, nm in ((a, 'a'), (b, 'b'), (d, 'd'), (e, 'e')):
        if not _isint(v):
            raise ValueError(nm + ' must be a whole number')
    top = _ssadd(_ss(int(a), 1, 1), _ss(int(b), 1, ci))
    bot = _ssadd(_ss(int(d), 1, 1), _ss(int(e), 1, fi))
    if not bot:
        raise ValueError('the denominator is 0')
    res = _ssdiv(top, bot)
    if res is None:
        raise ValueError('cannot rationalise that')
    k = int(d) * int(d) - int(e) * int(e) * fi
    return [m(_sstree(res)), '= ' + _ssstr(res),
            w('x (' + _linstr([int(d), -int(e)], ['', 'sqrt(' + str(fi) +
                                                     ')']) + ') top and bottom'),
            w('d^2 - e^2 f = ' + str(k)),
            'decimal = ' + sf3(_ssval(res))]


def _csq_tree(a, b, c):
    if _isint(a) and _isint(b) and _isint(c):
        ai = int(a)
        bi = int(b)
        ci = int(c)
        hr = caspoly.rmake(bi, 2 * ai)
        kr = caspoly.rmake(4 * ai * ci - bi * bi, 4 * ai)
    else:
        hr = (b / (2.0 * a), 1)
        kr = (c - b * b / (4.0 * a), 1)
    hv = hr[0] / float(hr[1])
    kv = kr[0] / float(kr[1])
    if hv == 0:
        inner = ('v', 'x')
    elif hv > 0:
        inner = ('+', ('v', 'x'), _ratnode(hr[0], hr[1]))
    else:
        inner = ('-', ('v', 'x'), _ratnode(-hr[0], hr[1]))
    node = ('^', inner, ('n', 2))
    if a == -1:
        node = ('neg', node)
    elif a != 1:
        node = ('*', _numnode(a), node)
    if kv > 0:
        node = ('+', node, _ratnode(kr[0], kr[1]))
    elif kv < 0:
        node = ('-', node, _ratnode(-kr[0], kr[1]))
    return (node, -hv, kv)


def t_quadratic(a, b, c):
    nums = _consts((a, b, c), ('a', 'b', 'c'))
    if nums is None:
        return _quad_sym(a, b, c)
    return _quadratic(nums[0], nums[1], nums[2])


def _quad_sym(a, b, c):
    # a x^2 + b x + c with letters: exact roots when the discriminant
    # is a perfect square in the letters
    S = caseng.simplify
    X = ('v', 'x')
    D = S(caspoly.expand(('-', ('^', b, ('n', 2)), ('*', ('n', 4), ('*', a, c)))))
    lines = []
    rs = _symroots(('+', ('+', ('*', a, ('^', X, ('n', 2))), ('*', b, X)), c))
    if rs:
        for r in rs:
            lines.append('x = ' + caseng.tostr(r))
    else:
        lines.append('x = (-b +- sqrt(D))/2a')
    lines.append('disc = ' + caseng.tostr(D))
    vx = S(('/', ('neg', b), ('*', ('n', 2), a)))
    vy = S(('-', c, ('/', ('^', b, ('n', 2)), ('*', ('n', 4), a))))
    lines.append('vertex (' + caseng.tostr(vx) + ', ' + caseng.tostr(vy) + ')')
    lines.append(w('letters are constants, taken as positive'))
    return lines


def _quadratic(a, b, c):
    if a == 0:
        if b == 0:
            raise ValueError('a and b are both 0')
        return ['x = ' + fmt(-c / float(b)),
                warn('a = 0: this is linear, not quadratic'),
                w('bx + c = 0, x = -c/b')]
    D = b * b - 4.0 * a * c
    lines = []
    if _isint(a) and _isint(b) and _isint(c):
        ai = int(a)
        bi = int(b)
        ci = int(c)
        Di = bi * bi - 4 * ai * ci
        if Di > 0:
            r1 = _ssdiv(_ssadd(_ss(-bi, 1, 1), _ss(1, 1, Di)), _ss(2 * ai, 1, 1))
            r2 = _ssdiv(_ssadd(_ss(-bi, 1, 1), _ss(-1, 1, Di)), _ss(2 * ai, 1, 1))
            if _ssval(r1) > _ssval(r2):
                r1, r2 = r2, r1
            lines.append('x = ' + _ssstr(r1))
            lines.append('x = ' + _ssstr(r2))
            if _ssrat(r1) is None:
                lines.append(w('= ' + sf3(_ssval(r1)) + ' and ' +
                               sf3(_ssval(r2))))
        elif Di == 0:
            r1 = _ssdiv(_ss(-bi, 1, 1), _ss(2 * ai, 1, 1))
            lines.append('x = ' + _ssstr(r1) + ' (repeated)')
        else:
            re = _ssdiv(_ss(-bi, 1, 1), _ss(2 * ai, 1, 1))
            im = _ssdiv(_ss(1, 1, -Di), _ss(2 * ai, 1, 1))
            if _ssval(im) < 0:
                im = _ssneg(im)
            lines.append('x = ' + _cxstr(re, im, 1))
            lines.append('x = ' + _cxstr(re, im, -1))
    elif D >= 0:
        rt = math.sqrt(D)
        x1 = (-b - rt) / (2.0 * a)
        x2 = (-b + rt) / (2.0 * a)
        if x1 > x2:
            x1, x2 = x2, x1
        lines.append('x = ' + fmt(x1))
        if D > 0:
            lines.append('x = ' + fmt(x2))
    else:
        rt = math.sqrt(-D)
        lines.append('x = ' + fmt(complex(-b / (2.0 * a), rt / (2.0 * a))))
        lines.append('x = ' + fmt(complex(-b / (2.0 * a), -rt / (2.0 * a))))
    lines.append('disc = ' + fmt(D))
    node, hx, kv = _csq_tree(a, b, c)
    lines.append('vertex (' + fmt(hx) + ', ' + fmt(kv) + ')')
    lines.append(m(node))
    lines.append(w('D = b^2-4ac = ' + fmt(b * b) + ' - ' + fmt(4.0 * a * c) +
                   ' = ' + fmt(D)))
    lines.append(w('x = (-b +- sqrt(D)) / 2a'))
    if D < 0:
        lines.append(warn('no real roots: D < 0'))
    elif D == 0:
        lines.append(warn('repeated root: D = 0'))
    return lines


def t_quad_in(a, b, c, f):
    if a == 0:
        raise ValueError('a must not be 0')
    D = b * b - 4.0 * a * c
    if D < 0:
        return ['no real u', warn('u^2 disc = ' + fmt(D) + ' < 0'),
                w('a u^2 + b u + c = 0 where u = f(x)')]
    rt = math.sqrt(D)
    us = [(-b - rt) / (2.0 * a)]
    if D > 0:
        us.append((-b + rt) / (2.0 * a))
    lines = []
    for u in us:
        lines.append('u = f(x) = ' + fmt(u))
        rs = _roots(('-', f, _numnode(u)), -20.0, 20.0, False, 'x', 800)
        if not rs:
            lines.append(warn('f(x) = ' + fmt(u) + ' has no root in -20..20'))
        for r in rs[:4]:
            lines.append('  x = ' + fmt(r))
    lines.append(w('u = (-b +- sqrt(' + fmt(D) + '))/2a'))
    lines.append(w('x searched over -20 to 20 only'))
    return lines


def t_simul2(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    if det == 0:
        if a1 * c2 - a2 * c1 == 0 and b1 * c2 - b2 * c1 == 0:
            return ['infinitely many solutions',
                    warn('the two equations are the same line'),
                    w('det = a1b2 - a2b1 = 0')]
        return ['no solution', warn('the lines are parallel'),
                w('det = a1b2 - a2b1 = 0')]
    x = (c1 * b2 - c2 * b1) / float(det)
    y = (a1 * c2 - a2 * c1) / float(det)
    return ['x = ' + fmt(x), 'y = ' + fmt(y),
            w('det = a1b2 - a2b1 = ' + fmt(det)),
            w('x = (c1b2 - c2b1)/det, y = (a1c2 - a2c1)/det')]


def _solvefor(e, var, step):
    # var = tree from e = 0: step 0 linear as typed, 1 linear after
    # expanding, 2 var used once (inverted)
    S = caseng.simplify
    if step < 2:
        t = e if step == 0 else caspoly.expand(S(e))
        r = casalg.linin(t, var)
        if r is not None and r[0] != ('n', 0) and \
                var not in caseng.vars_in(r[0]):
            return (S(('neg', ('/', r[1], r[0]))), r[0])
    elif caseng.count_var(e, var) == 1:
        inv = caseng.invert(e, var, 'z')
        if inv is not None:
            return (S(caseng.subst(inv, 'z', ('n', 0))), None)
    return None


def _evenroot(t):
    # does t take an even root (a branch could be lost)?
    k = t[0]
    if k == 'sqrt':
        return True
    if k == '^':
        r = caseng._ratval(t[2])
        if r is not None and r[1] % 2 == 0:
            return True
    if k == 'n' or k == 'v':
        return False
    if len(t) == 3:
        return _evenroot(t[1]) or _evenroot(t[2])
    return _evenroot(t[1])


def _nr2d(F, G, x, y):
    # Newton for F = G = 0 with numeric slopes; F, G take (x, y)
    k = 0
    while k < 20:
        f = F((x, y))
        g = G((x, y))
        if f is None or g is None:
            return None
        if abs(f) + abs(g) < 1e-13:
            return (x, y)
        h = 1e-6 * (1.0 + abs(x) + abs(y))
        fx = F((x + h, y))
        fy = F((x, y + h))
        gx = G((x + h, y))
        gy = G((x, y + h))
        if None in (fx, fy, gx, gy):
            return None
        a = (fx - f) / h
        b = (fy - f) / h
        c = (gx - g) / h
        d = (gy - g) / h
        det = a * d - b * c
        if det == 0:
            return None
        dx = (f * d - g * b) / det
        dy = (a * g - c * f) / det
        x -= dx
        y -= dy
        if abs(x) > 1e6 or abs(y) > 1e6:
            return None
        k += 1
    f = F((x, y))
    g = G((x, y))
    if f is None or g is None or abs(f) + abs(g) > 1e-8:
        return None
    return (x, y)


def t_simulnl(f, g):
    for t, nm in ((f, 'f'), (g, 'g')):
        for v in caseng.vars_in(t):
            if v != 'x' and v != 'y':
                raise ValueError(nm + ': use x and y only')
    S = caseng.simplify
    pick = None
    for step in (0, 1, 2):
        for e, o, en in ((f, g, 'f'), (g, f, 'g')):
            for var, u in (('y', 'x'), ('x', 'y')):
                r = _solvefor(e, var, step)
                if r is not None and not (step == 2 and _evenroot(r[0])):
                    pick = (var, u, r[0], r[1], o, en)
                    break
            if pick is not None:
                break
        if pick is not None:
            break
    sols = []
    wk = []
    if pick is not None:
        var, u, ex, A, other, en = pick
        h = caseng.subst(other, var, ex)
        wk.append(w(var + ' = ' + caseng.tostr(ex) + ' from ' + en + ' = 0'))
        wk.append(w('so ' + caseng.tostr(h) + ' = 0'))
        pf = None
        if u not in caseng.vars_in(h):
            pf = None
        else:
            try:
                pf = caspoly.polyfrac(h, u)
            except Exception:
                pf = None
        roots = []
        if pf is not None and len(caspoly.ptrim(list(pf[0]))) > 1:
            for txt, v in _prootsx(pf[0], u):
                roots.append((v, txt))
        else:
            H = _fast(h, u)
            roots = [(r, None) for r in _wideroots(H, None)]
            if len(roots) == 1 and caseng.count_var(h, u) == 1:
                inv = caseng.invert(h, u, 'z')
                if inv is not None:
                    try:
                        et = S(caseng.subst(inv, 'z', ('n', 0)))
                        if abs(casutil.ev(et) - roots[0][0]) < 1e-9 * \
                                (1 + abs(roots[0][0])):
                            roots = [(roots[0][0], caseng.tostr(et))]
                    except ValueError:
                        pass
        E = _fast(ex, u)
        for uv, txt in roots:
            vv = E(uv)
            if vv is None:
                continue
            if A is not None and caseng.vars_in(A):
                av = _fast(A, u)(uv)
                if av is None or abs(av) < 1e-12:
                    continue
            vt = fmt(vv)
            ut = txt if txt is not None else fmt(uv)
            if txt is not None:
                try:
                    et = S(caseng.subst(ex, u, caslex.parse(txt)))
                    if not caseng.vars_in(et) and \
                            abs(casutil.ev(et) - vv) < 1e-9 * (1 + abs(vv)):
                        vt = caseng.tostr(et)
                except Exception:
                    vt = fmt(vv)
            if [1 for q in sols if abs(q[0] - (uv if u == 'x' else vv)) +
                    abs(q[1] - (vv if u == 'x' else uv)) < 1e-9]:
                continue
            sols.append((uv, vv, ut, vt) if u == 'x' else (vv, uv, vt, ut))
    else:
        Ff = _fast(f, 'xy')
        Gg = _fast(g, 'xy')
        for sx in (-2.9, 0.3, 3.1):
            for sy in (-3.3, -0.4, 2.7):
                p = _nr2d(Ff, Gg, sx, sy)
                if p is not None and not [1 for q in sols if
                                          abs(q[0] - p[0]) + abs(q[1] - p[1])
                                          < 1e-7]:
                    sols.append((p[0], p[1], fmt(_snap(p[0])),
                                 fmt(_snap(p[1]))))
        wk.append(warn('Newton from 9 starts in -3..3: may miss some'))
    sols.sort()
    out = []
    for x, y, xt, yt in sols[:8]:
        out.append('(x, y) = (' + xt + ', ' + yt + ')')
        if xt != fmt(x) or yt != fmt(y) or xt.find('sqrt') >= 0 or \
                yt.find('sqrt') >= 0:
            out.append(w('= (' + sf3(x) + ', ' + sf3(y) + ')'))
    if not out:
        out.append('no real solution found')
    return out + wk


def t_linquad(m0, c0, a, b, k):
    if a == 0:
        if b - m0 == 0:
            return ['no solution' if k - c0 != 0 else 'every x',
                    warn('both are straight lines')]
        x = (c0 - k) / float(b - m0)
        return ['x = ' + fmt(x), 'y = ' + fmt(m0 * x + c0),
                warn('a = 0: both are straight lines')]
    A = a
    B = b - m0
    C = k - c0
    D = B * B - 4.0 * A * C
    lines = []
    if D < 0:
        lines.append('no intersection')
        lines.append(warn('disc = ' + fmt(D) + ' < 0'))
    else:
        rt = math.sqrt(D)
        xs = [(-B - rt) / (2.0 * A)]
        if D > 0:
            xs.append((-B + rt) / (2.0 * A))
        else:
            lines.append('tangent: one point')
        xs.sort()
        ex = None
        if _isint(A) and _isint(B) and _isint(C) and _isint(m0) and \
                _isint(c0) and D > 0:
            ex = _qexact(int(A), int(B), int(C))
        for i in range(len(xs)):
            x = xs[i]
            if ex is not None and len(ex) == len(xs):
                xr = _ssdiv(_ssadd(_ss(-int(B), 1, 1),
                                   _ss(1 if i else -1, 1, int(D))),
                            _ss(2 * int(A), 1, 1))
                if (A < 0) != (i == 0):
                    pass
                if abs(_ssval(xr) - x) > 1e-9 * (1 + abs(x)):
                    xr = _ssdiv(_ssadd(_ss(-int(B), 1, 1),
                                       _ss(-1 if i else 1, 1, int(D))),
                                _ss(2 * int(A), 1, 1))
                yr = _ssadd(_ssmul(_ss(int(m0), 1, 1), xr), _ss(int(c0), 1, 1))
                lines.append('(' + _ssstr(xr) + ', ' + _ssstr(yr) + ')')
            else:
                lines.append('(' + fmt(x) + ', ' + fmt(m0 * x + c0) + ')')
    lines.append(w('ax^2 + (b-m)x + (k-c) = 0'))
    lines.append(w(_quadstr(A, B, C) + ' = 0'))
    lines.append(w('disc = ' + fmt(D)))
    return lines


def _window(lo, hi):
    if lo is None and hi is None:
        return None
    if lo is None or hi is None:
        raise ValueError('give both lo and hi, or neither')
    if hi <= lo:
        raise ValueError('hi must be more than lo')
    return (float(lo), float(hi))


def _wideroots(D, win, n=150):
    # roots of fast D on win, or on -20..20 plus a log scan to +-10000
    if win is not None:
        return _froots(D, _grid(win[0], win[1], n))
    rs = _froots(D, _grid(-20.0, 20.0, n))
    for xs in _farxs(-20.0, 20.0, 1e4, 50):
        for r in _froots(D, xs):
            cascalc._add(rs, r)
    rs.sort()
    return rs


def _xtexts(d, rs):
    # exact text for each root when d is a polynomial
    p = caspoly.poly(d, 'x')
    ex = []
    if p is not None and len(p) > 1:
        try:
            ex = _prootsx(p, 'x')
        except Exception:
            ex = []
    out = []
    for r in rs:
        s = fmt(r)
        for t, v in ex:
            if abs(v - r) < 1e-7 * (1.0 + abs(r)):
                s = t
        out.append(s)
    return out


def t_meet(f, g, lo, hi):
    win = _window(lo, hi)
    d = ('-', f, g)
    p = caspoly.poly(d, 'x')
    if p is not None and len(p) > 1:
        rs = [r[1] for r in _prootsx(p, 'x')
              if win is None or win[0] <= r[1] <= win[1]]
    else:
        rs = _wideroots(_fast(d), win)
    where = '-10000..10000' if win is None else fmt(lo) + '..' + fmt(hi)
    if not rs:
        return ['no crossing in ' + where,
                warn('only ' + where + ' is searched')]
    lines = []
    tx = _xtexts(d, rs)
    for i in range(min(len(rs), 8)):
        y = _snap(_val(f, rs[i]))
        if y is None:
            lines.append('x = ' + tx[i])
        else:
            lines.append('(' + tx[i] + ', ' + fmt(y) + ')')
        if tx[i] != sf3(rs[i]):
            lines.append(w('x = ' + sf3(rs[i])))
    lines.append(w('solving f(x) - g(x) = 0'))
    lines.append(w(str(len(rs)) + ' crossing(s) in ' + where))
    return lines


def t_lin_ineq(a, b):
    if a == 0:
        if b > 0:
            return ['ax+b > 0: every x', 'ax+b < 0: no x', w('a = 0, b > 0')]
        if b < 0:
            return ['ax+b > 0: no x', 'ax+b < 0: every x', w('a = 0, b < 0')]
        return ['ax+b = 0 for every x', warn('a = 0 and b = 0')]
    r = -b / float(a)
    if a > 0:
        hi = 'x > ' + fmt(r)
        lo = 'x < ' + fmt(r)
    else:
        hi = 'x < ' + fmt(r)
        lo = 'x > ' + fmt(r)
    return [_linstr([a, b], ['x', '']) + ' > 0: ' + hi,
            _linstr([a, b], ['x', '']) + ' < 0: ' + lo,
            'f = 0 at x = ' + fmt(r),
            w('{x : ' + hi + '}  and  {x : ' + lo + '}'),
            w('divide by a = ' + fmt(a) +
              (' and flip the sign' if a < 0 else ''))]


def t_quad_ineq(a, b, c):
    if a == 0:
        return t_lin_ineq(b, c) + [warn('a = 0: read f as bx + c')]
    D = b * b - 4.0 * a * c
    lines = [w('f = ' + _quadstr(a, b, c)), w('disc = ' + fmt(D))]
    if D < 0:
        if a > 0:
            out = ['f > 0: every x', 'f < 0: no x']
        else:
            out = ['f > 0: no x', 'f < 0: every x']
        return out + [warn('no real roots: f never reaches 0')] + lines
    rt = math.sqrt(D)
    r1 = (-b - rt) / (2.0 * a)
    r2 = (-b + rt) / (2.0 * a)
    if r1 > r2:
        r1, r2 = r2, r1
    s1 = fmt(r1)
    s2 = fmt(r2)
    if D == 0:
        if a > 0:
            out = ['f > 0: x != ' + s1, 'f < 0: no x']
        else:
            out = ['f > 0: no x', 'f < 0: x != ' + s1]
        return out + ['f = 0: x = ' + s1,
                      warn('repeated root: the curve touches the axis')] + lines
    outside = 'x < ' + s1 + ' or x > ' + s2
    inside = s1 + ' < x < ' + s2
    if a > 0:
        out = ['f > 0: ' + outside, 'f < 0: ' + inside]
    else:
        out = ['f > 0: ' + inside, 'f < 0: ' + outside]
    return out + ['f = 0: x = ' + s1 + ', ' + s2,
                  w('{x : ' + inside + '}')] + lines


def _qexact(A, B, C):
    # real roots of A t^2 + B t + C (whole numbers, A != 0) as (text, value)
    Di = B * B - 4 * A * C
    if Di < 0:
        return []
    if Di == 0:
        r = _ssdiv(_ss(-B, 1, 1), _ss(2 * A, 1, 1))
        return [(_ssstr(r), _ssval(r))]
    r1 = _ssdiv(_ssadd(_ss(-B, 1, 1), _ss(1, 1, Di)), _ss(2 * A, 1, 1))
    r2 = _ssdiv(_ssadd(_ss(-B, 1, 1), _ss(-1, 1, Di)), _ss(2 * A, 1, 1))
    out = [(_ssstr(r1), _ssval(r1)), (_ssstr(r2), _ssval(r2))]
    if out[0][1] > out[1][1]:
        out.reverse()
    return out


def _pval(p, x):
    v = 0.0
    i = len(p) - 1
    while i >= 0:
        v = v * x + p[i][0] / float(p[i][1])
        i -= 1
    return v


def _prootsx(p, var):
    # real roots of a rational polynomial: exact up to degree 2
    if len(p) <= 1:
        return []
    L = 1
    for c in p:
        L = casutil.lcm(L, c[1])
    ci = [c[0] * (L // c[1]) for c in p]
    if len(p) == 2:
        return [(fmt(-ci[0] / float(ci[1])), -ci[0] / float(ci[1]))]
    if len(p) == 3:
        return _qexact(ci[2], ci[1], ci[0])
    out = []
    rp = caspoly.ptrim(list(p))
    for r in caspoly.roots_rational(p):
        qr = caspoly.pdivmod(rp, [caspoly.rneg(r), caspoly.R1])
        if qr is not None and not qr[1]:
            rp = qr[0]
        v = r[0] / float(r[1])
        out.append((fmt(v), v))
    if len(rp) == 3 or len(rp) == 2:
        rest = _prootsx(rp, var)
    elif len(rp) > 3:
        rest = [(fmt(r), r) for r in _pnum(rp, -50.0, 50.0, 500)]
    else:
        rest = []
    for r in rest:
        if not [1 for q in out if abs(q[1] - r[1]) < 1e-9]:
            out.append(r)
    out.sort(key=lambda q: q[1])
    return out


def _hv(c, x):
    v = 0.0
    i = len(c) - 1
    while i >= 0:
        v = v * x + c[i]
        i -= 1
    return v


def _pnum(p, lo, hi, n):
    # real roots of a rational polynomial by sampling with Horner
    c = [q[0] / float(q[1]) for q in p]
    step = (hi - lo) / float(n)
    ys = [_hv(c, lo + step * i) for i in range(n + 1)]
    out = []
    for i in range(1, n + 1):
        a = lo + step * (i - 1)
        b = a + step
        fa = ys[i - 1]
        fb = ys[i]
        if fa == 0.0:
            cascalc._add(out, a)
        elif (fa < 0) != (fb < 0) and fb != 0.0:
            k = 0
            while k < 56:
                mid = (a + b) / 2.0
                fm = _hv(c, mid)
                if (fm < 0) == (fa < 0):
                    a = mid
                    fa = fm
                else:
                    b = mid
                k += 1
            cascalc._add(out, _snap((a + b) / 2.0))
        elif i < n and abs(fb) < abs(fa) and abs(fb) < abs(ys[i + 1]) and \
                (fb < 0) == (ys[i + 1] < 0):
            u = a
            v = b + step
            k = 0
            while k < 50:
                m1 = u + (v - u) / 3.0
                m2 = v - (v - u) / 3.0
                if abs(_hv(c, m1)) <= abs(_hv(c, m2)):
                    v = m2
                else:
                    u = m1
                k += 1
            r = (u + v) / 2.0
            if abs(_hv(c, r)) < 1e-9 * (1.0 + abs(c[len(c) - 1])):
                cascalc._add(out, _snap(r))
    out.sort()
    return out

def _ivstr(var, lo, hi, closed):
    lt = ' <= ' if closed else ' < '
    gt = ' >= ' if closed else ' > '
    if lo is None and hi is None:
        return 'every ' + var
    if lo is None:
        return var + lt + hi[0]
    if hi is None:
        return var + gt + lo[0]
    return lo[0] + lt + var + lt + hi[0]


def _region(var, rs, sg, want, closed):
    # rs sorted roots (text, value), sg the sign on each of the len(rs)+1 gaps
    n = len(sg)
    pieces = []
    i = 0
    while i < n:
        if sg[i] == want:
            j = i
            if closed:
                while j + 1 < n and sg[j + 1] == want:
                    j += 1
            lo = rs[i - 1] if i > 0 else None
            hi = rs[j] if j < n - 1 else None
            pieces.append((lo[1] if lo else -1e300, _ivstr(var, lo, hi, closed)))
            i = j + 1
        else:
            i += 1
    if closed:
        k = 0
        while k < len(rs):
            if sg[k] != want and sg[k + 1] != want:
                pieces.append((rs[k][1], var + ' = ' + rs[k][0]))
            k += 1
    pieces.sort()
    if not pieces:
        return 'no ' + var
    return ' or '.join([p[1] for p in pieces])


def _gapsigns(rs, val):
    # sign of val(t) on each gap between the sorted roots
    sg = []
    i = 0
    while i <= len(rs):
        if not rs:
            t = 0.0
        elif i == 0:
            t = rs[0][1] - 1.0
        elif i == len(rs):
            t = rs[i - 1][1] + 1.0
        else:
            t = (rs[i - 1][1] + rs[i][1]) / 2.0
        v = val(t)
        sg.append(0 if v is None or v == 0 else (1 if v > 0 else -1))
        i += 1
    return sg


def t_disck(a, b, c):
    pa = caspoly.poly(a, 'k')
    pb = caspoly.poly(b, 'k')
    pc = caspoly.poly(c, 'k')
    if pa is None or pb is None or pc is None:
        raise ValueError('a, b, c must be polynomials in k')
    if not pa:
        raise ValueError('a(k) is 0: not a quadratic')
    D = caspoly.psub(caspoly.pmul(pb, pb),
                     caspoly.pscale(caspoly.pmul(pa, pc), (4, 1)))
    Dt = caspoly.ptree(D, 'k')
    fac = caspoly.factor(Dt, 'k') if len(D) > 2 else None
    wk = [w('D = b^2 - 4ac'), m(Dt)]
    if fac is not None and caseng.tostr(fac) != caseng.tostr(Dt):
        wk.append(m(fac))
    if len(D) <= 1:
        dv = _pval(D, 0.0)
        if dv > 0:
            out = ['distinct real roots for every k']
        elif dv < 0:
            out = ['no real roots for any k']
        else:
            out = ['equal roots for every k']
        return out + [w('D = ' + fmt(dv) + ' does not depend on k')] + wk
    rs = _prootsx(D, 'k')
    sg = _gapsigns(rs, lambda t: _pval(D, t))
    eq = ', '.join([r[0] for r in rs]) if rs else 'no k'
    out = ['equal roots: ' + ('k = ' + eq if rs else eq),
           'real roots: ' + _region('k', rs, sg, 1, True),
           'distinct: ' + _region('k', rs, sg, 1, False),
           'no real roots: ' + _region('k', rs, sg, -1, False)]
    if [r for r in rs if r[0].find('sqrt') >= 0]:
        wk.append(w('k = ' + ', '.join([sf3(r[1]) for r in rs])))
    if len(pa) > 1:
        for r in _prootsx(pa, 'k'):
            wk.append(warn('k = ' + r[0] + ' makes a = 0: not quadratic'))
    return out + wk


def _cuts(d, lo, hi, n):
    # roots, poles and domain edges of d on [lo, hi], sorted
    step = (hi - lo) / float(n)
    ys = [_val(d, lo + step * i) for i in range(n + 1)]
    rs = _roots(d, lo, hi, False, 'x', n, ys)
    pts = [(r, 'r') for r in rs]
    i = 1
    while i <= n:
        p = ys[i - 1]
        y = ys[i]
        x0 = lo + step * (i - 1)
        x1 = x0 + step
        if (p is None) != (y is None):
            a = x0
            b = x1
            k = 0
            while k < 40:
                mid = (a + b) / 2.0
                if (_val(d, mid) is None) == (p is None):
                    a = mid
                else:
                    b = mid
                k += 1
            pts.append((_snap((a + b) / 2.0), 'e'))
        elif p is not None and ((p < 0 < y) or (p > 0 > y)):
            hit = False
            for r in rs:
                if x0 - 1e-9 <= r <= x1 + 1e-9:
                    hit = True
            if not hit:
                r = _bis(d, x0, x1, False, 'x')
                if r is not None:
                    pts.append((r, 'p'))
        i += 1
    pts.sort()
    out = []
    for x, k in pts:
        if out and abs(out[len(out) - 1][0] - x) < 1e-7:
            if k == 'e' and out[len(out) - 1][1] == 'e':
                out[len(out) - 1] = (out[len(out) - 1][0], 'p')
            continue
        out.append((x, k))
    return out


def _ratcuts(d):
    # (rs, kinds, sign function) for a rational d, else None
    pf = caspoly.polyfrac(d, 'x')
    if pf is None or not pf[1]:
        return None
    N = pf[0]
    D = pf[1]
    pr = _prootsx(D, 'x')
    nr = [r for r in _prootsx(N, 'x')
          if not [1 for q in pr if abs(q[1] - r[1]) < 1e-9]]
    cuts = [(r[1], r, 'r') for r in nr] + [(r[1], r, 'p') for r in pr]
    cuts.sort()
    cn = [q[0] / float(q[1]) for q in N]
    cd = [q[0] / float(q[1]) for q in D]

    def val(x):
        dv = _hv(cd, x)
        return None if dv == 0 else _hv(cn, x) / dv
    return ([c[1] for c in cuts], [c[2] for c in cuts], val,
            len(N) > 3 or len(D) > 3)


def _fcuts(D, xs):
    # roots ('r'), poles ('p') and domain edges ('e') of fast D between xs
    ys = [D(x) for x in xs]
    pts = [(r, 'r') for r in _froots(D, xs, ys)]
    i = 1
    while i < len(xs):
        p = ys[i - 1]
        y = ys[i]
        if (p is None) != (y is None):
            a = xs[i - 1]
            b = xs[i]
            k = 0
            while k < 40:
                mid = (a + b) / 2.0
                if (D(mid) is None) == (p is None):
                    a = mid
                else:
                    b = mid
                k += 1
            pts.append((_snap(_nice((a + b) / 2.0)), 'e'))
        elif p is not None and y != 0 and p != 0 and (p < 0) != (y < 0):
            hit = False
            for r, k in pts:
                if k == 'r' and xs[i - 1] - 1e-9 <= r <= xs[i] + 1e-9:
                    hit = True
            if not hit:
                r = _fbis(D, xs[i - 1], xs[i], p)
                if r is not None:
                    pts.append((_snap(_nice(r)), 'p'))
        i += 1
    pts.sort()
    out = []
    for x, k in pts:
        if out and abs(out[len(out) - 1][0] - x) < 1e-7 * (1.0 + abs(x)):
            if k == 'e' and out[len(out) - 1][1] == 'e':
                out[len(out) - 1] = (out[len(out) - 1][0], 'p')
            continue
        out.append((x, k))
    return out


def t_ineq(f, g, lo, hi):
    win = _window(lo, hi)
    d = ('-', f, g)
    rc = _ratcuts(d) if win is None else None
    if rc is not None:
        rs, kinds, val, wide = rc
        sg = _gapsigns(rs, val)
    else:
        D = _fast(d)
        a0, b0 = win if win is not None else (-12.0, 12.0)
        cuts = _fcuts(D, _grid(a0, b0, 160))
        if win is None:
            for xs in _farxs(a0, b0, 1e4, 50):
                for c in _fcuts(D, xs):
                    if c[0] < a0 - 1e-9 or c[0] > b0 + 1e-9:
                        cuts.append(c)
            cuts.sort()
        rs = [(fmt(x), x) for x, k in cuts]
        kinds = [k for x, k in cuts]
        sg = []
        i = 0
        while i <= len(cuts):
            a = a0 if i == 0 else cuts[i - 1][0]
            b = b0 if i == len(cuts) else cuts[i][0]
            if win is None and i == 0 and cuts and cuts[0][0] < a0:
                a = cuts[0][0] - 1.0
            if win is None and i == len(cuts) and cuts and cuts[i - 1][0] > b0:
                b = cuts[i - 1][0] + 1.0
            v = D((a + b) / 2.0)
            sg.append(0 if v is None or abs(v) < 1e-12 else (1 if v > 0 else -1))
            i += 1
    if len(rs) > 12:
        raise ValueError('too many crossings to list')
    eq = [rs[i] for i in range(len(rs)) if kinds[i] == 'r']
    poles = [rs[i] for i in range(len(rs)) if kinds[i] == 'p']
    if win is None:
        out = ['f > g: ' + _region('x', rs, sg, 1, False),
               'f < g: ' + _region('x', rs, sg, -1, False)]
    else:
        ends = [(fmt(lo), lo)] + rs + [(fmt(hi), hi)]
        sg2 = [0] + sg + [0]
        out = ['f > g: ' + _region('x', ends, sg2, 1, False).replace(
                   'no x', 'none here'),
               'f < g: ' + _region('x', ends, sg2, -1, False).replace(
                   'no x', 'none here')]
    if eq:
        out.append('f = g at x = ' + ', '.join([r[0] for r in eq]))
    for r in poles:
        out.append('undefined at x = ' + r[0])
    out.append(w('sign of f - g between the critical values'))
    for r in rs:
        if r[0].find('sqrt') >= 0:
            out.append(w(r[0] + ' = ' + sf3(r[1])))
    if win is not None:
        out.append(w('only ' + fmt(lo) + ' < x < ' + fmt(hi)))
    elif rc is None:
        out.append(warn('searched -10000 < x < 10000'))
    elif wide:
        out.append(warn('roots past degree 2 searched in -50..50'))
    return out


def t_expand(f):
    t = caspoly.collect(caspoly.expand(f))
    return [m(t), w(caseng.tostr(t))]


def _factors_of(t, out):
    k = t[0]
    if k == '*':
        _factors_of(t[1], out)
        _factors_of(t[2], out)
    elif k == 'neg':
        _factors_of(t[1], out)
    elif k == '^' and t[2][0] == 'n' and _isint(t[2][1]) and t[2][1] > 0:
        _factors_of(t[1], out)
    else:
        out.append(t)


def _linroots(t):
    # roots in x of a product of factors, when each x factor is linear
    fs = []
    _factors_of(t, fs)
    out = []
    for fc in fs:
        if 'x' not in caseng.vars_in(fc):
            continue
        r = casalg.linin(caseng.simplify(fc), 'x')
        if r is None or r[0] == ('n', 0):
            return []
        s = caseng.tostr(caseng.simplify(('neg', ('/', r[1], r[0]))))
        if s not in out:
            out.append(s)
    return out


def _xcoeffs(f, var='x', top=4):
    # polynomial coefficients in var (other letters allowed), or None
    try:
        raw = casalg._terms(caspoly.expand(caseng.simplify(f)))
    except Exception:
        return _xcoeffs_d(f, var, top)
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
        c = (mo[0] if sg > 0 else (-mo[0][0], mo[0][1]), rest)
        ct = _mtree(c)
        co[k] = ct if k not in co else caseng.simplify(('+', co[k], ct))
        if k > hi:
            hi = k
    out = [co.get(k, ('n', 0)) for k in range(hi + 1)]
    while len(out) > 1 and out[len(out) - 1] == ('n', 0):
        out.pop()
    return out


def _xcoeffs_d(f, var='x', top=4):
    g = caseng.simplify(f)
    out = []
    fact = 1
    k = 0
    while k <= top:
        c = caseng.simplify(caseng.subst(g, var, ('n', 0)))
        out.append(caseng.simplify(('/', c, ('n', fact))))
        g = caseng.simplify(caseng.diff(g, var))
        k += 1
        fact *= k
        if g == ('n', 0):
            while len(out) > 1 and out[len(out) - 1] == ('n', 0):
                out.pop()
            return out
    return None


def _surdfree(t):
    s = caseng.tostr(t)
    return s.find('sqrt') < 0 and s.find('^(1/') < 0 and s.find('i') < 0


def _symroots(f, var='x'):
    # exact roots of a degree 1 or 2 polynomial in var with letters, or None
    try:
        co = _xcoeffs(f, var, 3)
    except Exception:
        return None
    if co is None or len(co) < 2 or len(co) > 3:
        return None
    if len(co) == 2:
        return [caseng.simplify(('neg', ('/', co[0], co[1])))]
    C, B, A = co
    if C == ('n', 0):
        return [('n', 0), caseng.simplify(('neg', ('/', B, A)))]
    D = caseng.simplify(caspoly.expand(
        ('-', ('^', B, ('n', 2)), ('*', ('n', 4), ('*', A, C)))))
    if B == ('n', 0):
        q = caseng.simplify(('neg', ('/', C, A)))
        if caseng._isneg(q):
            return []
        s = _msqrt(q)
        if not _surdfree(s) and caseng.vars_in(q):
            return None
        return [caseng.simplify(('neg', s)), s]
    if caseng._isneg(D):
        return []
    s = _msqrt(D)
    if not _surdfree(s) and caseng.vars_in(D):
        return None
    two = ('*', ('n', 2), A)
    return [caseng.simplify(('/', ('-', ('neg', B), s), two)),
            caseng.simplify(('/', ('+', ('neg', B), s), two))]


def t_factorise(f):
    t = caspoly.factor(f)
    vs = caseng.vars_in(f)
    if t is None and 'x' in vs and len(vs) > 1:
        rs = _symroots(f)
        co = _xcoeffs(f, 'x', 3)
        if rs and co is not None and len(co) == 3:
            X = ('v', 'x')
            lead = caseng._ratval(co[2])
            fs = []
            for r in (rs[0], rs[len(rs) - 1]):
                d = 1
                try:
                    mo = _mono(r)
                    if mo[0][1] > 1 and lead is not None and \
                            lead[0] % mo[0][1] == 0:
                        d = mo[0][1]
                except ValueError:
                    pass
                dX = X
                if d > 1:
                    lead = (lead[0] // d, lead[1])
                    dX = ('*', ('n', d), X)
                dr = caseng.simplify(('*', ('n', d), r))
                if dr == ('n', 0):
                    fs.append(dX)
                elif caseng._isneg(dr):
                    fs.append(('+', dX, caseng.simplify(caseng._negnode(dr))))
                else:
                    fs.append(('-', dX, dr))
            if caseng.tostr(rs[0]) == caseng.tostr(rs[len(rs) - 1]):
                t = ('^', fs[0], ('n', 2))
            else:
                t = ('*', fs[0], fs[1])
            k = co[2] if lead is None else caspoly.ratnode(lead)
            if k != _ONE:
                t = ('*', k, t)
    if t is None:
        t = casalg.factorise(f)
    if t is None:
        s = caseng.simplify(f)
        return [m(s), warn('no rational factorisation found')]
    lines = [m(t), w(caseng.tostr(t))]
    rs = _linroots(t)
    if rs:
        lines.insert(1, '= 0 at x = ' + ', '.join(rs))
    return lines


def t_pdiv(p, d):
    pp = _polyof(p, 'p')
    dd = _polyof(d, 'd')
    if len(dd) < 2:
        raise ValueError('d(x) must contain x')
    qr = caspoly.pdivmod(pp, dd)
    if qr is None:
        raise ValueError('cannot divide those')
    q, r = qr
    qt = caspoly.ptree(q, 'x')
    rt = caspoly.ptree(r, 'x')
    if r:
        lines = [m(('+', qt, ('/', rt, caspoly.ptree(dd, 'x'))))]
        lines.append('remainder = ' + caseng.tostr(rt))
    else:
        lines = [m(qt), 'remainder = 0']
    lines.append('quotient = ' + caseng.tostr(qt))
    if not r and len(dd) == 2:
        lines.append('(' + caseng.tostr(caspoly.ptree(dd, 'x')) +
                     ') is a factor')
    lines.append(w('p = d x q + r'))
    return lines


def t_factor_thm(p, a):
    pp = caspoly.poly(p, 'x')
    if pp is None:
        pp = caspoly.poly(caseng.simplify(p), 'x')
    ra = caseng._fltrat(float(a))
    if pp is not None and ra is not None:
        r = caspoly.peval(pp, ra)
        v = r[0] if r[1] == 1 else r[0] / float(r[1])
    else:
        v = _need(p, float(a))
    br = 'x - ' + fmt(a) if a >= 0 else 'x + ' + fmt(-a)
    lines = ['p(' + fmt(a) + ') = ' + fmt(v)]
    if v == 0:
        lines.append('(' + br + ') is a factor')
        if ra is not None and ra[1] != 1:
            lines.append('(' + str(ra[1]) + 'x ' + ('- ' if ra[0] > 0 else '+ ') +
                         str(abs(ra[0])) + ') is a factor')
    else:
        lines.append('(' + br + ') is not a factor')
        lines.append('remainder = ' + fmt(v))
    if pp is not None and ra is not None:
        lines.append(w('worked in exact fractions'))
    lines.append(w('factor theorem: p(a) = 0 iff (x-a) | p'))
    return lines


def t_ratsimp(f, g):
    pf = _polyof(f, 'f')
    pg = _polyof(g, 'g')
    if not pg:
        raise ValueError('g(x) is 0')
    gg = _pgcd(pf, pg)
    if len(gg) < 2:
        t = ('/', caspoly.ptree(pf, 'x'), caspoly.ptree(pg, 'x'))
        return [m(t), warn('no common factor to cancel')]
    a = caspoly.pdivmod(pf, gg)
    b = caspoly.pdivmod(pg, gg)
    if a is None or b is None:
        raise ValueError('cannot cancel')
    na = caspoly.ptree(a[0], 'x')
    nb = caspoly.ptree(b[0], 'x')
    t = na if b[0] == [caspoly.R1] else ('/', na, nb)
    lines = [m(caseng.simplify(t))]
    lines.append(w('cancelled ' + caseng.tostr(caspoly.ptree(gg, 'x'))))
    bad = caspoly.roots_rational(gg)
    for r in bad[:3]:
        lines.append(warn('x != ' + fmt(r[0] / float(r[1])) +
                          ': it was cancelled'))
    return lines


def _userfac(ft, ufs):
    # (factor, k) with factor = k * ft: the user's own factor, else ft
    # scaled to whole coefficients with the top kept positive
    pf = caspoly.poly(ft, 'x')
    if pf is None:
        return (ft, (1, 1), False)
    for u in ufs:
        pu = caspoly.poly(u, 'x')
        if pu is None or len(pu) != len(pf):
            continue
        k = caspoly.rdiv(pu[len(pu) - 1], pf[len(pf) - 1])
        if k is not None and [caspoly.rmul(c, k) for c in pf] == pu:
            return (u, k, True)
    L = 1
    for c in pf:
        L = casutil.lcm(L, c[1])
    k = (L, 1)
    return (caspoly.ptree([caspoly.rmul(c, k) for c in pf], 'x'), k, False)


def t_partial(f, g):
    res = caspoly.partial(f, g, 'x')
    if res is None:
        raise ValueError('cannot split that into partial fractions')
    quot, terms = res
    ufs = []
    _factors_of(g, ufs)
    ufs = [u for u in ufs if 'x' in caseng.vars_in(u)]
    shown = []
    for top, ft, i in terms:
        uf, k, own = _userfac(ft, ufs)
        top = caseng.simplify(('*', top, caspoly.ratnode((k[0] ** i, k[1] ** i))))
        pu = caspoly.poly(uf, 'x')
        if not own and caseng._isneg(top) and i % 2 == 1 and pu is not None \
                and len(pu) == 2 and pu[0][0] < 0:
            # -A/(kx - c) is written A/(c - kx)
            uf = ('-', caspoly.ratnode(caspoly.rneg(pu[0])),
                  caspoly.ptree([caspoly.R0, pu[1]], 'x'))
            top = caseng.simplify(caseng._negnode(top))
        shown.append((top, uf, i))
    node = quot
    for top, ft, i in shown:
        den = ft if i == 1 else ('^', ft, ('n', i))
        if caseng._isneg(top):
            piece = ('/', caseng.simplify(caseng._negnode(top)), den)
            node = ('neg', piece) if node is None else ('-', node, piece)
        else:
            piece = ('/', top, den)
            node = piece if node is None else ('+', node, piece)
    if node is None:
        node = ('n', 0)
    lines = [m(node), '= ' + caseng.tostr(node)]
    for top, ft, i in shown:
        den = '(' + caseng.tostr(ft) + ')'
        if i != 1:
            den = den + '^' + str(i)
        num = caseng.tostr(top)
        if num.find('/') >= 0:
            num = '(' + num + ')'
        lines.append(num + ' / ' + den)
    if quot is not None:
        lines.append('polynomial part ' + caseng.tostr(quot))
    lines.append(w('cover-up / equate coefficients'))
    return lines


def t_comp(f, g, x):
    fg = caspoly.collect(caspoly.expand(caseng.subst(f, 'x', g)))
    gf = caspoly.collect(caspoly.expand(caseng.subst(g, 'x', f)))
    lines = ['fg(x) = f(g(x)):', m(fg), 'gf(x) = g(f(x)):', m(gf)]
    if x is not None:
        u = _val(fg, float(x))
        v = _val(gf, float(x))
        lines.append('fg(' + fmt(x) + ') = ' + (fmt(u) if u is not None
                                                else 'undefined'))
        lines.append('gf(' + fmt(x) + ') = ' + (fmt(v) if v is not None
                                                else 'undefined'))
    lines.append(w('fg means g first, then f'))
    return lines


def _pieces(f, lo, hi, n):
    # monotone runs of f sampled on [lo, hi]: [[x0, x1, y0, y1]]
    xs = _grid(lo, hi, n)
    ys = [f(x) for x in xs]
    out = []
    cur = None
    dirn = 0
    i = 0
    while i <= n:
        y = ys[i]
        if y is None:
            cur = None
            i += 1
            continue
        if cur is None:
            cur = [xs[i], xs[i], y, y]
            out.append(cur)
            dirn = 0
            i += 1
            continue
        d = y - cur[3]
        if d == 0 and f((cur[1] + xs[i]) / 2.0) == y:
            return (out, (cur[1], xs[i]))
        s = 1 if d > 0 else -1
        jump = False
        if abs(d) > 2.0 * (abs(y) + abs(cur[3])) / n + 1e-9:
            mid = f((xs[i] + cur[1]) / 2.0)
            jump = mid is None or (mid - cur[3]) * (y - mid) < 0
        if jump or (dirn != 0 and s != dirn):
            cur = [xs[i - 1], xs[i], cur[3], y] if not jump else \
                [xs[i], xs[i], y, y]
            out.append(cur)
            dirn = 0 if jump else s
        else:
            cur[1] = xs[i]
            cur[3] = y
            dirn = s
        i += 1
    return (out, None)


def _hit(f, p, y):
    # x in run p = [x0, x1, y0, y1] with f(x) = y, by bisection
    a = p[0]
    b = p[1]
    up = p[3] > p[2]
    k = 0
    while k < 60:
        mid = (a + b) / 2.0
        v = f(mid)
        if v is None:
            return None
        if (v < y) == up:
            a = mid
        else:
            b = mid
        k += 1
    return _snap((a + b) / 2.0)


def _turn(f, t, h):
    # refine a turning point near t by ternary search on |f - f(t - h)|
    a = t - h
    b = t + h
    ya = f(a)
    if ya is None or f(b) is None:
        return t
    up = f(t) > ya
    k = 0
    while k < 60:
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        v1 = f(m1)
        v2 = f(m2)
        if v1 is None or v2 is None:
            return t
        if (v1 < v2) == up:
            a = m1
        else:
            b = m2
        k += 1
    r = (a + b) / 2.0
    n = int(r + 0.5) if r >= 0 else -int(0.5 - r)
    for c in (n, n + 0.5, n - 0.5):
        if abs(r - c) < 1e-6:
            return c
    return r


def _nicepts(p):
    # whole numbers inside run p, nearest its end first
    a = min(p[0], p[1])
    b = max(p[0], p[1])
    out = []
    n = int(math.floor(b))
    while n > a and len(out) < 3:
        if n < b:
            out.append(float(n))
        n -= 1
    if p[0] > p[1]:
        out.reverse()
    return out


def _manyone(f, lo, hi):
    # (x1, x2, y) with f(x1) = f(x2), x1 != x2, or None
    f = _fast(f)
    runs, flat = _pieces(f, lo, hi, 240)
    if flat is not None:
        return (flat[0], flat[1], f(flat[0]))
    i = 0
    while i < len(runs):
        j = i + 1
        while j < len(runs):
            p = runs[i]
            q = runs[j]
            plo = min(p[2], p[3])
            phi = max(p[2], p[3])
            qlo = min(q[2], q[3])
            qhi = max(q[2], q[3])
            a = max(plo, qlo)
            b = min(phi, qhi)
            if b - a > 1e-9 * (1.0 + abs(a) + abs(b)):
                t = _turn(f, p[1], (hi - lo) / 240.0) if j == i + 1 else p[1]
                for h in (1, 2, 0.5, 3, 1.5):
                    u = f(t - h)
                    v = f(t + h)
                    if u is not None and v is not None and lo <= t - h and \
                            t + h <= hi and abs(u - v) < 1e-9 * (1 + abs(u)):
                        return (_snap(t - h), _snap(t + h), u)
                for x1 in _nicepts(p):
                    y = f(x1)
                    if y is not None and a < y < b:
                        x2 = _hit(f, q, y)
                        if x2 is not None:
                            return (x1, x2, y)
                y = (a + b) / 2.0
                x1 = _hit(f, p, y)
                x2 = _hit(f, q, y)
                if x1 is not None and x2 is not None:
                    return (x1, x2, y)
            j += 1
        i += 1
    return None


def _fits(f, g, lo, hi):
    f = _fast(f)
    g = _fast(g)
    tried = 0
    for k in range(1, 8):
        x0 = lo + (hi - lo) * k / 8.0
        y = f(x0)
        if y is None:
            continue
        v = g(y)
        if v is None or abs(v - x0) > 1e-6 * (1 + abs(x0)):
            return False
        tried += 1
    return tried > 0


def _mobius(f):
    # (ax + b)/(cx + d) -> (dy - b)/(a - cy), else None
    try:
        pf = caspoly.polyfrac(f, 'x')
    except Exception:
        return None
    if pf is None or len(pf[0]) > 2 or len(pf[1]) != 2:
        return None
    N = pf[0] + [caspoly.R0, caspoly.R0]
    b, a = N[0], N[1]
    d, c = pf[1][0], pf[1][1]
    Y = ('v', 'y')
    top = ('-', ('*', caspoly.ratnode(d), Y), caspoly.ratnode(b))
    bot = ('-', caspoly.ratnode(a), ('*', caspoly.ratnode(c), Y))
    return caseng.simplify(('/', top, bot))


def _conds(t, out):
    # (tree, rule) pairs that limit the domain
    k = t[0]
    if k == 'n' or k == 'v':
        return
    if k == 'sqrt':
        out.append((t[1], ' >= 0'))
    elif k == 'ln' or k == 'log':
        out.append((t[1], ' > 0'))
    elif k == 'logb':
        out.append((t[2], ' > 0'))
    elif k == '/':
        out.append((t[2], ' != 0'))
    elif k == '^':
        r = caseng._ratval(t[2])
        if r is not None and r[1] % 2 == 0:
            out.append((t[1], ' >= 0' if r[0] > 0 else ' > 0'))
        elif r is not None and r[0] < 0:
            out.append((t[1], ' != 0'))
    elif k == 'tan' or k == 'sec':
        out.append((('cos', t[1]), ' != 0'))
    elif k == 'cot' or k == 'cosec':
        out.append((('sin', t[1]), ' != 0'))
    elif k == 'asin' or k == 'acos':
        out.append((('-', ('n', 1), ('^', t[1], ('n', 2))), ' >= 0'))
    _conds(t[1], out)
    if len(t) == 3:
        _conds(t[2], out)


def t_domain(f):
    for v in caseng.vars_in(f):
        if v != 'x':
            raise ValueError('use x only')
    conds = []
    _conds(f, conds)
    F = _fast(f)
    pts = []
    wk = []
    seen = []
    for u, rule in conds:
        key = caseng.tostr(u)
        if 'x' not in caseng.vars_in(u) or key + rule in seen:
            continue
        seen.append(key + rule)
        wk.append(w(key + rule))
        p = caspoly.poly(u, 'x')
        if p is not None and len(p) > 1:
            rs = _prootsx(p, 'x')
        else:
            rs = [(fmt(r), r) for r in _wideroots(_fast(u), None)]
        for t, v in rs:
            if not [1 for q in pts if abs(q[1] - v) < 1e-9 * (1 + abs(v))]:
                pts.append((t, v))
    pts.sort(key=lambda q: q[1])
    if len(pts) > 10:
        raise ValueError('too many excluded points to list')
    gaps = []
    i = 0
    while i <= len(pts):
        if not pts:
            t = 0.37
        elif i == 0:
            t = pts[0][1] - 1.0
        elif i == len(pts):
            t = pts[i - 1][1] + 1.0
        else:
            t = (pts[i - 1][1] + pts[i][1]) / 2.0
        gaps.append(F(t) is not None)
        i += 1
    ins = [F(v) is not None for t, v in pts]
    # runs of defined gaps joined through defined or excluded points
    ivs = []
    cur = None
    i = 0
    while i <= len(pts):
        if gaps[i]:
            if cur is None:
                lo = None if i == 0 else (pts[i - 1][0], not ins[i - 1])
                cur = [lo, None, []]
                ivs.append(cur)
            if i < len(pts):
                if gaps[i + 1]:
                    if not ins[i]:
                        cur[2].append(pts[i][0])
                else:
                    cur[1] = (pts[i][0], not ins[i])
                    cur = None
        else:
            if i < len(pts) and ins[i] and not gaps[i + 1]:
                ivs.append([(pts[i][0], False), (pts[i][0], False), []])
            cur = None
        i += 1
    if not ivs:
        return ['no real x'] + wk
    parts = []
    for lo, hi, ex in ivs:
        s = _ivtext(lo, hi, 'x')
        if s == 'all real values':
            s = '' if ex else 'all real x'
        if ex:
            s = (s + ', ' if s else '') + 'x != ' + ', '.join(ex)
        parts.append(s)
    out = ['domain: ' + ' or '.join(parts)]
    if len(ivs) == 1 and ivs[0][2]:
        out.append('{x : ' + parts[0] + '}')
    return out + wk


def _negsqrt(t):
    k = t[0]
    if k == 'sqrt':
        return ('neg', t)
    if k == 'n' or k == 'v':
        return t
    if len(t) == 2:
        return (k, _negsqrt(t[1]))
    return (k, _negsqrt(t[1]), _negsqrt(t[2]))


def t_inverse(f, a, b):
    if a is not None and b is not None and b <= a:
        raise ValueError('need a < b')
    lo = a if a is not None else (b - 40.0 if b is not None else -20.0)
    hi = b if b is not None else (a + 40.0 if a is not None else 20.0)
    dom = _ivstr('x', None if a is None else (fmt(a), a),
                 None if b is None else (fmt(b), b), True)
    dom = 'all real x' if dom == 'every x' else dom
    mo = _manyone(f, lo, hi)
    if mo is not None:
        x1, x2, y = mo
        return ['many-to-one: no inverse',
                'f(' + fmt(x1) + ') = f(' + fmt(x2) + ') = ' + fmt(y),
                w('domain ' + dom),
                w('restrict the domain to make f one-to-one')]
    inv = caseng.invert(f, 'x', 'y')
    if inv is None:
        inv = _mobius(f)
    if inv is None:
        try:
            inv = casalg.rearrange(f, 'x', 'y')
        except Exception:
            inv = None
    if inv is None:
        return ['no inverse formula found',
                warn('f is one-to-one here, but x cannot be made the subject'),
                w('f(x) = ' + caseng.tostr(caseng.simplify(f)))]
    t = caseng.simplify(caseng.subst(inv, 'y', ('v', 'x')))
    if not _fits(f, t, lo, hi):
        t2 = caseng.simplify(_negsqrt(t))
        if t2 != t and _fits(f, t2, lo, hi):
            t = t2
    lines = [m(t), 'f-1(x) = ' + caseng.tostr(t)]
    try:
        rg = t_frange(f, a, b)[0]
        if rg.startswith('range: '):
            lines.append('domain of f-1: ' + rg[7:].replace('f(x)', 'x'))
    except ValueError:
        pass
    x0 = lo + (hi - lo) * 0.37
    y0 = _val(f, x0)
    if y0 is not None:
        v = _val(t, y0)
        if v is not None:
            lines.append(w('check f(' + sf3(x0) + ') = ' + sf3(y0) +
                           ', f-1 of that = ' + sf3(v)))
    lines.append(w('f is one-to-one on ' + dom))
    lines.append(w('domain of f-1 = range of f'))
    return lines


def _danger(t, out):
    # sub-expressions whose zeros can make f blow up or stop
    k = t[0]
    if k == 'n' or k == 'v':
        return
    if k == '/':
        out.append(t[2])
    elif k == '^':
        r = caseng._ratval(t[2])
        if r is None or r[0] < 0:
            out.append(t[1])
    elif k == 'ln' or k == 'log':
        out.append(t[1])
    elif k == 'logb':
        out.append(t[2])
    elif k == 'tan' or k == 'sec':
        out.append(('cos', t[1]))
    elif k == 'cot' or k == 'cosec':
        out.append(('sin', t[1]))
    _danger(t[1], out)
    if len(t) == 3:
        _danger(t[2], out)


def _sspoly(p, r):
    # rational polynomial p at the surd sum r
    acc = []
    i = len(p) - 1
    while i >= 0:
        acc = _ssadd(_ssmul(acc, r), _ss(p[i][0], p[i][1], 1))
        i -= 1
    return acc


def _ssroots(p):
    # exact real roots of a rational polynomial: rational ones, then a
    # quadratic remainder; the rest are left out
    rp = caspoly.ptrim(list(p))
    out = []
    for r in caspoly.roots_rational(rp):
        qr = caspoly.pdivmod(rp, [caspoly.rneg(r), caspoly.R1])
        if qr is not None and not qr[1]:
            rp = qr[0]
        out.append(_ss(r[0], r[1], 1))
    if len(rp) == 3:
        L = 1
        for c in rp:
            L = casutil.lcm(L, c[1])
        C, B, A = [c[0] * (L // c[1]) for c in rp]
        Di = B * B - 4 * A * C
        if Di > 0:
            for sg in (1, -1):
                out.append(_ssdiv(_ssadd(_ss(-B, 1, 1), _ss(sg, 1, Di)),
                                  _ss(2 * A, 1, 1)))
    return out


def _trend(vals, big):
    # (value, 0), (None, +-1) for a blow-up, or None when it oscillates
    n = len(vals)
    a = vals[n - 2]
    b = vals[n - 1]
    if abs(b) > 1e12:
        return (None, 1 if b > 0 else -1)
    d = [vals[i + 1] - vals[i] for i in range(n - 1)]
    run = 0
    i = len(d) - 1
    while i > 0 and d[i] != 0 and (d[i] > 0) == (d[i - 1] > 0) and \
            0.4 * abs(d[i - 1]) < abs(d[i]) < 40.0 * abs(d[i - 1]):
        run += 1
        i -= 1
    if run >= 4 or (run >= 2 and abs(b) > big):
        return (None, 1 if b > a else -1)
    if abs(b - a) <= 1e-9 * (1.0 + abs(b)):
        return (_snap(b), 0)
    if n >= 4:
        d1 = d[n - 3]
        d2 = d[n - 2]
        if abs(d2) < 0.5 * abs(d1) and abs(d1) < 0.5 * abs(d[n - 4]) and \
                (d1 > 0) == (d2 > 0):
            r = d2 / d1
            L = b + d2 * r / (1.0 - r)
            if abs(L) < 1e-5 and abs(b) < 1e-5:
                L = 0.0
            return (_snap(L), 0)
    return None


def _flim(F, x0, s, big):
    # f as x -> s * inf: (value, 0), (None, +-1), or None if it oscillates
    vals = []
    sc = abs(x0) if abs(x0) > 1.0 else 1.0
    for k in (1, 2, 3, 4, 5, 6):
        v = F(s * sc * 10.0 ** k)
        if v is None:
            break
        vals.append(v)
    if len(vals) < 3:
        if vals and abs(vals[len(vals) - 1]) > big:
            return (None, 1 if vals[len(vals) - 1] > 0 else -1)
        raise ValueError('f does not evaluate far out')
    return _trend(vals, big)


def _near(F, c, s, big):
    # f as x -> c from side s: (value, closed?, blow-up sign) or None
    v = F(c)
    if v is not None and abs(v) <= 1e12:
        return (v, True, 0)
    vals = []
    for d in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7):
        u = F(c + s * d * (1.0 + abs(c)))
        if u is not None:
            vals.append(u)
    if len(vals) < 3:
        return None
    t = _trend(vals, big)
    if t is None:
        return None
    return (t[0], False, t[1])


def _gmin(F, a, b, sgn):
    # golden section for the least sgn * F on [a, b]
    g = 0.6180339887498949
    c = b - g * (b - a)
    d = a + g * (b - a)
    fc = F(c)
    fd = F(d)
    k = 0
    while k < 48:
        if fc is None or fd is None:
            return None
        if sgn * fc <= sgn * fd:
            b = d
            d = c
            fd = fc
            c = b - g * (b - a)
            fc = F(c)
        else:
            a = c
            c = d
            fc = fd
            d = a + g * (b - a)
            fd = F(d)
        k += 1
    return (a + b) / 2.0


def _ivtext(lo, hi, var):
    # lo, hi = (text, strict) or None for -inf / inf
    if lo is None and hi is None:
        return 'all real values'
    if lo is None:
        return var + (' < ' if hi[1] else ' <= ') + hi[0]
    if hi is None:
        return var + (' > ' if lo[1] else ' >= ') + lo[0]
    if lo[0] == hi[0]:
        return var + ' = ' + lo[0]
    return lo[0] + (' < ' if lo[1] else ' <= ') + var + \
        (' < ' if hi[1] else ' <= ') + hi[0]


def _rcuts(f, F, xs, ys):
    # break points of f in xs, and exact stationary points for a rational f
    exact = []
    cuts = []
    pf = None
    try:
        pf = caspoly.polyfrac(f, 'x')
    except Exception:
        pf = None
    if pf is not None:
        N = pf[0]
        D = pf[1] if pf[1] else [caspoly.R1]
        if len(D) > 1:
            for r in _prootsx(D, 'x'):
                cuts.append(r[1])
        dN = caspoly.psub(caspoly.pmul(caspoly.pderiv(N), D),
                          caspoly.pmul(N, caspoly.pderiv(D)))
        if len(caspoly.ptrim(list(dN))) > 1:
            for r in _ssroots(dN):
                dv = _sspoly(D, r)
                if dv:
                    exact.append((_ssval(r), _ssstr(r),
                                  _ssstr(_ssdiv(_sspoly(N, r), dv))))
    else:
        ds = []
        _danger(f, ds)
        seen = []
        for dz in ds:
            key = caseng.tostr(dz)
            if 'x' in caseng.vars_in(dz) and key not in seen:
                seen.append(key)
                for r in _froots(_fast(dz), xs):
                    cuts.append(r)
    i = 1
    while i < len(xs):
        if (ys[i - 1] is None) != (ys[i] is None):
            u = xs[i - 1]
            v = xs[i]
            k = 0
            while k < 40:
                mid = (u + v) / 2.0
                if (F(mid) is None) == (ys[i - 1] is None):
                    u = mid
                else:
                    v = mid
                k += 1
            cuts.append(_snap(_nice((u + v) / 2.0)))
        i += 1
    cuts.sort()
    return (cuts, exact, pf is not None)


def _piece(f, F, p, q, ends, xs, ys, exact, rat, wk):
    # candidate values of f on (p, q): (value, strict, blow-up sign)
    cand = []
    big = 1.0
    for y in ys:
        if y is not None and big < abs(y) < 1e9:
            big = abs(y)
    big = 2.0 * big
    for end, s, kind in ((p, 1, ends[0]), (q, -1, ends[1])):
        if kind == 'inf':
            r = _flim(F, end, -s, big)
            if r is None:
                msg = warn('f oscillates far out: values from ' +
                           fmt(xs[0]) + '..' + fmt(xs[len(xs) - 1]))
                if msg not in wk:
                    wk.append(msg)
                continue
            L, blow = r
            cand.append((L, True, blow))
            wk.append(w('x -> ' + ('-' if s > 0 else '') + 'inf: f -> ' +
                        (fmt(L) if blow == 0 else
                         ('inf' if blow > 0 else '-inf'))))
            continue
        r = _near(F, end, s, big)
        if r is None:
            continue
        v, closed, blow = r
        cand.append((v, not closed, blow))
        if closed:
            wk.append(w('f(' + fmt(end) + ') = ' + fmt(v)))
        else:
            wk.append(w('x -> ' + fmt(end) + ': f -> ' +
                        (fmt(v) if blow == 0 else
                         ('inf' if blow > 0 else '-inf'))))
    for xv, xt, vt in exact:
        if p < xv < q:
            v = F(xv)
            if v is not None:
                cand.append((v, False, 0))
                wk.append(w("f' = 0 at x = " + xt + ', f = ' + vt))
    if not rat:
        j = 1
        while j < len(xs) - 1:
            y0 = ys[j - 1]
            y1 = ys[j]
            y2 = ys[j + 1]
            if p < xs[j] < q and y0 is not None and y1 is not None and \
                    y2 is not None and (y1 - y0) * (y2 - y1) <= 0 and \
                    y1 != y0:
                sg = 1 if y1 < y0 else -1
                xm = _gmin(F, xs[j - 1], xs[j + 1], sg)
                if xm is not None:
                    xm = _snap(_nice(xm, F))
                    vm = F(xm)
                    if vm is not None:
                        cand.append((vm, False, 0))
                        if len(wk) < 8:
                            wk.append(w(('min' if sg > 0 else 'max') +
                                        ' at x = ' + fmt(xm) + ', f = ' +
                                        fmt(vm)))
            j += 1
    return cand


def _span2(cand):
    # (low, high) ends from candidates: (value, strict) or None for inf
    mn = None
    mx = None
    dn = False
    up = False
    for v, strict, blow in cand:
        if blow < 0:
            dn = True
        elif blow > 0:
            up = True
    for v, strict, blow in cand:
        if blow != 0:
            continue
        if not dn and (mn is None or v < mn[0] - 1e-12 or
                       (abs(v - mn[0]) <= 1e-12 and not strict)):
            mn = (v, strict)
        if not up and (mx is None or v > mx[0] + 1e-12 or
                       (abs(v - mx[0]) <= 1e-12 and not strict)):
            mx = (v, strict)
    return [None if dn else mn, None if up else mx]


def _union(ivs):
    ivs.sort(key=lambda t: -1e300 if t[0] is None else t[0][0])
    merged = [ivs[0]]
    for iv in ivs[1:]:
        last = merged[len(merged) - 1]
        top = last[1]
        if top is None:
            continue
        if iv[0] is None or iv[0][0] < top[0] or \
                (iv[0][0] == top[0] and not (iv[0][1] and top[1])):
            if iv[1] is None or iv[1][0] > top[0] or \
                    (iv[1][0] == top[0] and not iv[1][1]):
                last[1] = iv[1]
        else:
            merged.append(iv)
    return merged


def t_frange(f, a, b):
    if a is not None and b is not None and b <= a:
        raise ValueError('need a < b')
    lo = a if a is not None else (b if b is not None else 0.0) - 20.0
    hi = b if b is not None else (a if a is not None else 0.0) + 20.0
    if a is None and b is None:
        lo = -20.0
        hi = 20.0
    F = _fast(f)
    xs = _grid(lo, hi, 120)
    ys = [F(x) for x in xs]
    wk = []
    cuts, exact, rat = _rcuts(f, F, xs, ys)
    pts = [lo]
    for c in cuts:
        if lo + 1e-9 < c < hi - 1e-9 and abs(c - pts[len(pts) - 1]) > 1e-9:
            pts.append(c)
    pts.append(hi)
    ivs = []
    i = 0
    while i < len(pts) - 1:
        p = pts[i]
        q = pts[i + 1]
        i += 1
        if F((p + q) / 2.0) is None:
            continue
        ends = ['inf' if (p == lo and a is None) else
                ('end' if p == lo else 'cut'),
                'inf' if (q == hi and b is None) else
                ('end' if q == hi else 'cut')]
        cand = _piece(f, F, p, q, ends, xs, ys, exact, rat, wk)
        if cand:
            ivs.append(_span2(cand))
    if not ivs:
        raise ValueError('f is undefined on that interval')

    def txt(e):
        if e is None:
            return None
        s = fmt(e[0])
        for xv, xt, vt in exact:
            v = F(xv)
            if v is not None and abs(e[0] - v) < 1e-9 * (1 + abs(v)):
                s = vt
        return (s, e[1])
    parts = [_ivtext(txt(u), txt(v), 'f(x)') for u, v in _union(ivs)]
    return ['range: ' + ' or '.join(parts)] + wk


def t_transform(f, a, b, c, d):
    if b == 0:
        raise ValueError('b must not be 0')
    inner = caseng.simplify(('+', ('*', _numnode(b), ('v', 'x')), _numnode(c)))
    body = caseng.subst(f, 'x', inner)
    node = body if a == 1 else (('neg', body) if a == -1
                                else ('*', _numnode(a), body))
    if d > 0:
        node = ('+', node, _numnode(d))
    elif d < 0:
        node = ('-', node, _numnode(-d))
    t = caspoly.collect(caspoly.expand(caseng.simplify(node)))
    return [m(t), w('x -> ' + caseng.tostr(inner)),
            w('stretch y by ' + fmt(a) + ', shift y by ' + fmt(d)),
            w('stretch x by ' + fmt(1.0 / b) + ', shift x by ' +
              fmt(-c / float(b)))]


def t_modeq(a, b, c, d):
    lines = []
    got = []
    for sgn in (1, -1):
        den = sgn * a - c
        if den == 0:
            if d - sgn * b == 0:
                return ['every x with cx + d >= 0',
                        warn('the two sides are the same line'),
                        w('ax+b = ' + ('' if sgn > 0 else '-') + '(cx+d)')]
            continue
        x = (d - sgn * b) / float(den)
        rhs = c * x + d
        if rhs < -1e-9:
            continue
        lhs = a * x + b
        if lhs < 0:
            lhs = -lhs
        if lhs - rhs > 1e-7 or rhs - lhs > 1e-7:
            continue
        dup = False
        for e in got:
            if e - x < 1e-9 and x - e < 1e-9:
                dup = True
        if not dup:
            got.append(x)
    got.sort()
    for x in got:
        lines.append('x = ' + fmt(x))
    if not lines:
        lines.append('no solution')
        lines.append(warn('both branches fail the check cx + d >= 0'))
    lines.append(w('ax+b = cx+d  or  ax+b = -(cx+d)'))
    lines.append(w('keep only roots with cx + d >= 0'))
    return lines


def t_prop(n, x, y):
    if x == 0:
        raise ValueError('x must not be 0')
    if x < 0 and not _isint(n):
        raise ValueError('x must be positive for a fractional power')
    p = math.pow(float(x), float(n)) if x > 0 else \
        (float(x) ** int(n))
    if p == 0:
        raise ValueError('x^n is 0')
    k = y / p
    node = ('*', _numnode(k), ('^', ('v', 'x'), _numnode(n)))
    if n == 1:
        node = ('*', _numnode(k), ('v', 'x'))
    elif n == -1:
        node = ('/', _numnode(k), ('v', 'x'))
    return ['k = ' + fmt(k), m(caseng.simplify(node)),
            w('k = y / x^n = ' + fmt(y) + ' / ' + fmt(p)),
            w('direct n = 1, inverse n = -1')]


def t_plot(f, xlo, xhi):
    lo = -6.0 if xlo is None else float(xlo)
    hi = 6.0 if xhi is None else float(xhi)
    if hi <= lo:
        raise ValueError('xhi must be more than xlo')
    import plot
    plot.run([f], lo, hi, 'y', 'y = f(x)')
    lines = []
    y0 = _val(f, 0.0)
    if lo <= 0.0 <= hi and y0 is not None:
        lines.append('y(0) = ' + fmt(y0))
    rs = _roots(f, lo, hi, False, 'x', 600)
    if rs:
        for r in rs[:5]:
            lines.append('root x = ' + fmt(r))
    else:
        lines.append('no root in that window')
    lines.append(w('window ' + fmt(lo) + ' to ' + fmt(hi)))
    return lines

# =========================================== C  Coordinate geometry ========


def t_line2(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        raise ValueError('the two points are the same')
    d = math.sqrt(dx * dx + dy * dy)
    mid = '(' + fmt((x1 + x2) / 2.0) + ', ' + fmt((y1 + y2) / 2.0) + ')'
    if dx == 0:
        return ['x = ' + fmt(x1), 'gradient undefined (vertical)',
                'midpoint ' + mid, 'length = ' + fmt(d),
                w('x2 - x1 = 0, so the line is vertical')]
    g = dy / float(dx)
    c0 = y1 - g * x1
    return [_lineeq(g, c0), _general(dy, -dx, dx * y1 - dy * x1),
            'gradient m = ' + fmt(g), 'midpoint ' + mid,
            'length = ' + fmt(d),
            w('m = (y2-y1)/(x2-x1) = ' + fmt(dy) + '/' + fmt(dx)),
            w('length^2 = ' + fmt(dx * dx + dy * dy)),
            w('perpendicular gradient ' +
              (fmt(-1.0 / g) if g != 0 else 'undefined'))]


def t_perpbis(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        raise ValueError('the two points are the same')
    mx = (x1 + x2) / 2.0
    my = (y1 + y2) / 2.0
    lines = ['midpoint (' + fmt(mx) + ', ' + fmt(my) + ')']
    if dy == 0:
        lines.append('x = ' + fmt(mx))
        lines.append(w('the chord is horizontal, so the bisector is vertical'))
        return lines
    if dx == 0:
        lines.append('y = ' + fmt(my))
        lines.append(w('the chord is vertical, so the bisector is horizontal'))
        return lines
    g = dy / float(dx)
    p = -1.0 / g
    lines.insert(0, _lineeq(p, my - p * mx))
    lines.insert(1, _general(p, -1, my - p * mx))
    lines.append('gradient = ' + fmt(p))
    lines.append(w('chord gradient ' + fmt(g) + ', times ' + fmt(p) + ' = -1'))
    return lines


def t_parallel(g, x1, y1):
    c0 = y1 - g * x1
    return [_lineeq(g, c0), _general(g, -1, c0),
            w('same gradient m = ' + fmt(g)),
            w('c = y1 - m x1 = ' + fmt(y1) + ' - ' + fmt(g * x1))]


def t_perpthru(g, x1, y1):
    if g == 0:
        return ['x = ' + fmt(x1),
                w('the given line is horizontal, so this one is vertical')]
    p = -1.0 / g
    c0 = y1 - p * x1
    return [_lineeq(p, c0), _general(p, -1, c0), 'gradient = ' + fmt(p),
            w('m1 m2 = -1, so m2 = -1/' + fmt(g))]


def t_lineint(m1, c1, m2, c2):
    if m1 == m2:
        if c1 == c2:
            return ['the same line', warn('infinitely many points')]
        return ['no intersection', warn('parallel: equal gradients'),
                w('m1 = m2 = ' + fmt(m1))]
    x = (c2 - c1) / float(m1 - m2)
    y = m1 * x + c1
    lines = ['(' + fmt(x) + ', ' + fmt(y) + ')',
             w('m1 x + c1 = m2 x + c2'),
             w('x = (c2-c1)/(m1-m2) = ' + fmt(c2 - c1) + '/' + fmt(m1 - m2))]
    if m1 * m2 == -1:
        lines.append('the lines are perpendicular')
    return lines


def t_tri3(x1, y1, x2, y2, x3, y3):
    P = ((x1, y1), (x2, y2), (x3, y3))
    cr = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if cr == 0:
        raise ValueError('the points are collinear')
    sq = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        dx = P[j][0] - P[i][0]
        dy = P[j][1] - P[i][1]
        sq.append(dx * dx + dy * dy)
    out = ['area = ' + fmt(abs(cr) / 2.0),
           'AB = ' + fmt(math.sqrt(sq[0])) + ', BC = ' + fmt(math.sqrt(sq[1])) +
           ', CA = ' + fmt(math.sqrt(sq[2]))]
    names = 'ABC'
    angs = []
    rads = []
    for i in range(3):
        a = P[i]
        b = P[(i + 1) % 3]
        c = P[(i + 2) % 3]
        u = (b[0] - a[0], b[1] - a[1])
        v = (c[0] - a[0], c[1] - a[1])
        dot = u[0] * v[0] + u[1] * v[1]
        if abs(dot) < 1e-12 * (1.0 + sq[0] + sq[1] + sq[2]):
            out.append('right angle at ' + names[i])
        ang = casutil.acos_safe(dot / math.sqrt((u[0] * u[0] + u[1] * u[1]) *
                                                (v[0] * v[0] + v[1] * v[1])))
        angs.append(names[i] + ' = ' + sf3(casutil.deg(ang)))
        rads.append(names[i] + ' = ' + fmt(ang))
    out.append('angles ' + ', '.join(angs) + ' deg')
    out.append('in rad: ' + ', '.join(rads))
    if sq[0] == sq[1] or sq[1] == sq[2] or sq[0] == sq[2]:
        out.append('isosceles')
    out.append(w('area = |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|/2'))
    out.append(w('AB^2 = ' + fmt(sq[0]) + ', BC^2 = ' + fmt(sq[1]) +
                 ', CA^2 = ' + fmt(sq[2])))
    out.append(w('right angle where two sides have m1 m2 = -1'))
    return out

def _consts(trees, names):
    # numbers when no tree has a letter, else None; x never allowed
    vals = []
    sym = False
    for t, nm in zip(trees, names):
        vs = caseng.vars_in(t)
        if 'x' in vs or 'y' in vs:
            raise ValueError(nm + ' must not contain x or y')
        if vs:
            sym = True
        else:
            vals.append(casutil.real(casutil.ev(t)))
    return None if sym else vals


def _sympt(a, b):
    return '(' + caseng.tostr(a) + ', ' + caseng.tostr(b) + ')'


def t_footperp(a, b, c, px, py):
    n2 = a * a + b * b
    if n2 == 0:
        raise ValueError('a and b are both 0')
    k = c - a * px - b * py
    t = k / float(n2)
    fx = px + a * t
    fy = py + b * t
    allint = True
    for v in (a, b, c, px, py):
        if not _isint(v):
            allint = False
    if allint:
        ki = int(k) if k >= 0 else -int(k)
        d = _ssstr(_ssdiv(_ss(ki, 1, 1), _ss(1, 1, int(n2)))) if ki else '0'
    else:
        d = fmt(abs(k) / math.sqrt(n2))
    out = ['foot (' + fmt(_snap(fx)) + ', ' + fmt(_snap(fy)) + ')',
           'distance = ' + d,
           'reflection of P (' + fmt(_snap(px + 2 * a * t)) + ', ' +
           fmt(_snap(py + 2 * b * t)) + ')']
    if d.find('sqrt') >= 0:
        out.append(w('distance = ' + sf3(abs(k) / math.sqrt(n2))))
    out.append(w('normal through P: (x, y) = P + t(a, b)'))
    out.append(w('t = (c - a px - b py)/(a^2 + b^2) = ' + fmt(t)))
    out.append(w('distance = |a px + b py - c| / sqrt(a^2 + b^2)'))
    return out


def t_circle_gen(D, E, F):
    nums = _consts((D, E, F), ('D', 'E', 'F'))
    if nums is None:
        S = caseng.simplify
        cx = S(('/', ('neg', D), ('n', 2)))
        cy = S(('/', ('neg', E), ('n', 2)))
        r2 = S(('-', ('+', ('^', cx, ('n', 2)), ('^', cy, ('n', 2))), F))
        r = _msqrt(r2)
        xs = S(('^', ('-', ('v', 'x'), cx), ('n', 2)))
        ys = S(('^', ('-', ('v', 'y'), cy), ('n', 2)))
        return ['centre ' + _sympt(cx, cy), 'radius = ' + caseng.tostr(r),
                'r^2 = ' + caseng.tostr(r2),
                w(caseng.tostr(xs) + ' + ' + caseng.tostr(ys) + ' = ' +
                  caseng.tostr(r2)),
                w('a real circle needs ' + caseng.tostr(r2) + ' > 0')
                if caseng.vars_in(r2) else w('r^2 > 0: a real circle'),
                w('centre (-D/2, -E/2), r^2 = D^2/4 + E^2/4 - F')]
    D, E, F = nums
    cx = -D / 2.0
    cy = -E / 2.0
    r2 = cx * cx + cy * cy - F
    lines = ['centre (' + fmt(cx) + ', ' + fmt(cy) + ')']
    if r2 < 0:
        lines.append('r^2 = ' + fmt(r2))
        lines.append(warn('r^2 < 0: not a real circle'))
        return lines
    if r2 == 0:
        lines.append('radius = 0')
        lines.append(warn('a single point, not a circle'))
        return lines
    lines.append('radius = ' + fmt(math.sqrt(r2)))
    lines.append('r^2 = ' + fmt(r2))
    lines.append(_circstr(cx, cy, r2))
    lines.append(w('centre (-D/2, -E/2), r^2 = D^2/4 + E^2/4 - F'))
    return lines + _axes(cx, cy, r2)


def _circstr(a, b, r2):
    xs = 'x^2' if a == 0 else ('(x - ' + fmt(a) + ')^2' if a > 0
                               else '(x + ' + fmt(-a) + ')^2')
    ys = 'y^2' if b == 0 else ('(y - ' + fmt(b) + ')^2' if b > 0
                               else '(y + ' + fmt(-b) + ')^2')
    return xs + ' + ' + ys + ' = ' + fmt(r2)


def _axes(a, b, r2):
    # where (x-a)^2 + (y-b)^2 = r2 meets the axes, exact for whole numbers
    out = []
    for c, nm, o in ((b, 'x', a), (a, 'y', b)):
        k = r2 - c * c
        if abs(k - round(k)) < 1e-9 * (1 + abs(k)):
            k = int(round(k))
        if k < 0:
            out.append(w('misses the ' + nm + ' axis'))
            continue
        if _isint(k) and _isint(o):
            ss = _ss(1, 1, int(k))
            pts = [_ssstr(_ssadd(_ss(int(o), 1, 1), _ssneg(ss))),
                   _ssstr(_ssadd(_ss(int(o), 1, 1), ss))] if k else [fmt(o)]
        else:
            rt = math.sqrt(k)
            pts = [fmt(o - rt), fmt(o + rt)] if k else [fmt(o)]
        out.append(w('meets the ' + nm + ' axis at ' + nm + ' = ' +
                     ', '.join(pts)))
    return out


def t_circle_cr(a, b, r):
    _pos(r, 'r')
    lines = _circle_cr(a, b, r)
    return lines + ['area = ' + fmt(math.pi * r * r) + ', circumference = ' +
                    fmt(2 * math.pi * r)] + _axes(a, b, r * r)


def t_circpt(a, b, r, px, py):
    _pos(r, 'r')
    d2 = (px - a) ** 2 + (py - b) ** 2
    d = math.sqrt(d2)
    if abs(d - r) < 1e-9 * (1 + r):
        where = 'on the circle'
    elif d < r:
        where = 'inside the circle'
    else:
        where = 'outside the circle'
    return [where, 'distance from centre = ' + fmt(d),
            w('compare d^2 = ' + fmt(d2) + ' with r^2 = ' + fmt(r * r))]


def t_circline(x1, y1, x2, y2, a, b, c):
    # circle through two points with its centre on ax + by = c
    a1 = 2.0 * (x2 - x1)
    b1 = 2.0 * (y2 - y1)
    c1 = x2 * x2 - x1 * x1 + y2 * y2 - y1 * y1
    det = a1 * b - a * b1
    if det == 0:
        raise ValueError('the line is parallel to the bisector')
    cx = (c1 * b - c * b1) / det
    cy = (a1 * c - a * c1) / det
    r2 = (x1 - cx) ** 2 + (y1 - cy) ** 2
    return ['centre (' + fmt(cx) + ', ' + fmt(cy) + ')',
            'radius = ' + fmt(math.sqrt(r2)), _circstr(cx, cy, r2),
            w('centre on the perpendicular bisector of the two points'),
            w('and on ' + _linstr([a, b], ['x', 'y']) + ' = ' + fmt(c))] + \
        _axes(cx, cy, r2)


def _circle_cr(a, b, r):
    D = -2.0 * a
    E = -2.0 * b
    F = a * a + b * b - r * r
    return [_circstr(a, b, r * r),
            _linstr([1, 1, D, E, F], ['x^2', 'y^2', 'x', 'y', '']) + ' = 0',
            w('D = -2a, E = -2b, F = a^2 + b^2 - r^2'),
            w('F = ' + fmt(F))]


def t_circle3(x1, y1, x2, y2, x3, y3):
    a1 = 2.0 * (x2 - x1)
    b1 = 2.0 * (y2 - y1)
    c1 = x2 * x2 - x1 * x1 + y2 * y2 - y1 * y1
    a2 = 2.0 * (x3 - x1)
    b2 = 2.0 * (y3 - y1)
    c2 = x3 * x3 - x1 * x1 + y3 * y3 - y1 * y1
    det = a1 * b2 - a2 * b1
    if det == 0:
        return ['no circle', warn('the three points are collinear'),
                w('the perpendicular bisectors are parallel')]
    cx = (c1 * b2 - c2 * b1) / det
    cy = (a1 * c2 - a2 * c1) / det
    r = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
    lines = ['centre (' + fmt(cx) + ', ' + fmt(cy) + ')',
             'radius = ' + fmt(r), _circstr(cx, cy, r * r)]
    pts = [(x1, y1), (x2, y2), (x3, y3)]
    for i in range(3):
        j = (i + 1) % 3
        ddx = pts[i][0] - pts[j][0]
        ddy = pts[i][1] - pts[j][1]
        s = math.sqrt(ddx * ddx + ddy * ddy)
        if s - 2.0 * r > -1e-9 and 2.0 * r - s > -1e-9:
            lines.append('one chord is a diameter')
            lines.append(w('angle in a semicircle = 90 degrees'))
            break
    lines.append(w('centre is where two perpendicular bisectors meet'))
    lines += _axes(cx, cy, r * r)
    return lines


def t_linecircle(m0, c0, a, b, r):
    _pos(r, 'r')
    A = 1.0 + m0 * m0
    B = 2.0 * (m0 * (c0 - b) - a)
    C = a * a + (c0 - b) ** 2 - r * r
    D = B * B - 4.0 * A * C
    dist = (m0 * a - b + c0)
    if dist < 0:
        dist = -dist
    dist = dist / math.sqrt(A)
    lines = []
    if D < 0:
        lines.append('no intersection')
        lines.append(warn('distance ' + fmt(dist) + ' > r = ' + fmt(r)))
    elif D == 0:
        x = -B / (2.0 * A)
        lines.append('tangent at (' + fmt(x) + ', ' + fmt(m0 * x + c0) + ')')
    else:
        rt = math.sqrt(D)
        for x in ((-B - rt) / (2.0 * A), (-B + rt) / (2.0 * A)):
            lines.append('(' + fmt(x) + ', ' + fmt(m0 * x + c0) + ')')
    lines.append('distance from centre = ' + fmt(dist))
    lines.append(w('sub y = mx + c into the circle'))
    lines.append(w(_quadstr(A, B, C) + ' = 0, disc = ' + fmt(D)))
    return lines


def t_tangent(a, b, px, py):
    dx = px - a
    dy = py - b
    r = math.sqrt(dx * dx + dy * dy)
    if r == 0:
        raise ValueError('the point is the centre')
    lines = []
    if dx == 0:
        lines.append('y = ' + fmt(py))
        lines.append(w('the radius is vertical, so the tangent is level'))
    elif dy == 0:
        lines.append('x = ' + fmt(px))
        lines.append(w('the radius is level, so the tangent is vertical'))
    else:
        mr = dy / dx
        mt = -1.0 / mr
        lines.append(_lineeq(mt, py - mt * px))
        lines.append(_general(mt, -1, py - mt * px))
        lines.append('gradient = ' + fmt(mt))
        lines.append(w('radius gradient ' + fmt(mr) + ', tangent = -1/that'))
    lines.append('radius = ' + fmt(r))
    lines.append(w('the tangent is perpendicular to the radius'))
    return lines


def _lin_in(tree, fn):
    # tree = a + b fn(t), with no other t: return (a, b) else None
    u = caseng.subst_tree(tree, (fn, ('v', 't')), ('v', 'u'))
    if 't' in caseng.vars_in(u):
        return None
    pu = caspoly.poly(u, 'u')
    if pu is None or len(pu) != 2:
        return None
    return (pu[0][0] / float(pu[0][1]), pu[1][0] / float(pu[1][1]))


def t_param_cart(xt, yt):
    pair = None
    cx = _lin_in(xt, 'cos')
    sy = _lin_in(yt, 'sin')
    if cx is not None and sy is not None:
        pair = (cx, sy)
    else:
        sx = _lin_in(xt, 'sin')
        cy = _lin_in(yt, 'cos')
        if sx is not None and cy is not None:
            pair = (sx, cy)
    if pair is not None:
        a = pair[0][0]
        p = pair[0][1]
        b = pair[1][0]
        q = pair[1][1]
        if p != 0 and q != 0:
            if p == q or p == -q:
                return [_circstr(a, b, p * p),
                        w('cos^2 t + sin^2 t = 1'),
                        w('a circle, centre (' + fmt(a) + ', ' + fmt(b) +
                          '), radius ' + fmt(p if p > 0 else -p))]
            return ['((x - ' + fmt(a) + ')/' + fmt(p) + ')^2 +',
                    '((y - ' + fmt(b) + ')/' + fmt(q) + ')^2 = 1',
                    w('cos^2 t + sin^2 t = 1'), w('an ellipse')]
    inv = caseng.invert(xt, 't', 'x')
    if inv is None:
        return ['cannot eliminate t',
                warn('x(t) must use t once and be one-to-one'),
                w('x(t) = ' + caseng.tostr(caseng.simplify(xt)))]
    res = caseng.simplify(caseng.subst(yt, 't', inv))
    res = caspoly.collect(caspoly.expand(res))
    return [m(res), 'y = ' + caseng.tostr(res),
            w('t = ' + caseng.tostr(caseng.simplify(inv)) + ' from x(t)')]


def t_param_pt(xt, yt, t):
    tv = float(t)
    x = _snap(_need(xt, tv, False, 't'))
    y = _snap(_need(yt, tv, False, 't'))
    dx = caseng.diff(xt, 't')
    dy = caseng.diff(yt, 't')
    vx = _snap(_val(cascalc.tidy(dx), tv, False, 't'))
    vy = _snap(_val(cascalc.tidy(dy), tv, False, 't'))
    lines = ['(' + fmt(x) + ', ' + fmt(y) + ')']
    if vx is None or vy is None:
        lines.append(warn('cannot differentiate at that t'))
        return lines
    lines.append('dx/dt = ' + fmt(vx))
    lines.append('dy/dt = ' + fmt(vy))
    if vx == 0:
        lines.append('dy/dx undefined (vertical)')
    else:
        g = vy / vx
        lines.append('dy/dx = ' + fmt(g))
        lines.append(_lineeq(g, y - g * x))
    lines.append(w('dy/dx = (dy/dt) / (dx/dt)'))
    return lines


def t_param_plot(xt, yt, tlo, thi):
    lo = float(tlo)
    hi = float(thi)
    if hi <= lo:
        raise ValueError('thi must be more than tlo')
    import plot
    plot.run([(xt, yt, lo, hi)], lo, hi, 'param', 'parametric')
    xs = []
    ys = []
    i = 0
    while i <= 100:
        tv = lo + (hi - lo) * i / 100.0
        a = _val(xt, tv, False, 't')
        b = _val(yt, tv, False, 't')
        if a is not None and b is not None:
            xs.append(a)
            ys.append(b)
        i += 1
    if not xs:
        raise ValueError('the curve has no points there')
    xs.sort()
    ys.sort()
    return ['start (' + fmt(_snap(_need(xt, lo, False, 't'))) + ', ' +
            fmt(_snap(_need(yt, lo, False, 't'))) + ')',
            'end (' + fmt(_snap(_need(xt, hi, False, 't'))) + ', ' +
            fmt(_snap(_need(yt, hi, False, 't'))) + ')',
            'x from ' + sf3(xs[0]) + ' to ' + sf3(xs[len(xs) - 1]),
            'y from ' + sf3(ys[0]) + ' to ' + sf3(ys[len(ys) - 1]),
            w('t from ' + fmt(lo) + ' to ' + fmt(hi))]

# ============================================ D  Sequences and series =====


def t_arith(a, d, n):
    ni = _whole(n, 'n')
    if ni < 1:
        raise ValueError('n must be at least 1')
    un = a + (ni - 1) * d
    sn = ni / 2.0 * (2.0 * a + (ni - 1) * d)
    return ['u(' + str(ni) + ') = ' + fmt(un),
            'S(' + str(ni) + ') = ' + fmt(sn),
            'u(1) = ' + fmt(a) + ', d = ' + fmt(d),
            w('u(n) = a + (n-1)d = ' + fmt(a) + ' + ' + fmt(ni - 1) + ' x ' +
              fmt(d)),
            w('S(n) = n/2 (2a + (n-1)d)'),
            w('also S(n) = n/2 (a + last) = ' + fmt(ni / 2.0 * (a + un)))]


def _exsurd(node, v):
    # rationalised, collected exact form of node when it is clean
    best = fmt(v)
    try:
        ex = caseng.simplify(casalg.rationalise(caseng.simplify(node)))
        cands = [ex]
        try:
            cands.append(caspoly.collect(caspoly.expand(ex)))
        except Exception:
            pass
        for c in cands:
            cs = caseng.tostr(c)
            if cs.find('.') < 0 and not caseng.vars_in(c) and \
                    abs(casutil.ev(c) - v) < 1e-9 * (1 + abs(v)) and \
                    (best.find('.') >= 0 or len(cs) < len(best)):
                best = cs
    except Exception:
        pass
    return best


def t_apfl(n, a, l):
    ni = _whole(n, 'n')
    if ni < 1:
        raise ValueError('n must be at least 1')
    sn = ni / 2.0 * (a + l)
    out = ['S(' + str(ni) + ') = ' + fmt(sn)]
    if ni > 1:
        out.append('d = ' + fmt((l - a) / (ni - 1.0)))
    return out + [w('S(n) = n/2 (first + last)')]


def t_geo(a, r, n):
    ni = _whole(n, 'n')
    if ni < 1:
        raise ValueError('n must be at least 1')
    un = a * math.pow(float(r), ni - 1)
    if r == 1:
        sn = a * ni
    else:
        sn = a * (1.0 - math.pow(float(r), ni)) / (1.0 - r)
    st = fmt(sn)
    A = _exn(a)
    R = _exn(r)
    if st.find('.') >= 0 and r != 1 and ni <= 60:
        st = _exsurd(('/', ('*', A, ('-', ('n', 1), ('^', R, ('n', ni)))),
                      ('-', ('n', 1), R)), sn)
    lines = ['u(' + str(ni) + ') = ' + fmt(un),
             'S(' + str(ni) + ') = ' + st]
    if st != fmt(sn):
        lines.append(w('S(' + str(ni) + ') = ' + sf3(sn)))
    ar = r if r >= 0 else -r
    if ar < 1:
        si = a / (1.0 - r)
        sit = fmt(si) if fmt(si).find('.') < 0 else \
            _exsurd(('/', A, ('-', ('n', 1), R)), si)
        lines.append('S(inf) = ' + sit)
        if sit != fmt(si):
            lines.append(w('S(inf) = ' + sf3(si)))
        lines.append(w('|r| < 1 so it converges to a/(1-r)'))
    else:
        lines.append(warn('|r| >= 1: no sum to infinity'))
    lines.append(w('u(n) = a r^(n-1), S(n) = a(1-r^n)/(1-r)'))
    return lines


def t_ap_n(a, d, k):
    s = 0.0
    n = 0
    while n < 5000:
        n += 1
        s = n / 2.0 * (2.0 * a + (n - 1) * d)
        if s > k:
            return ['n = ' + str(n), 'S(' + str(n) + ') = ' + fmt(s),
                    w('smallest n with S(n) > ' + fmt(k)),
                    w('S(n) = n/2 (2a + (n-1)d)')]
    return ['no n up to 5000', warn('S(n) never passes ' + fmt(k) + ' there'),
            w('S(5000) = ' + fmt(s))]


def t_gp_n(a, r, k):
    ar = r if r >= 0 else -r
    if ar < 1:
        lim = a / (1.0 - r)
        if lim <= k:
            return ['no such n', warn('S(inf) = ' + fmt(lim) + ' <= ' + fmt(k)),
                    w('|r| < 1, so the sum never passes that')]
    s = 0.0
    term = a
    n = 0
    while n < 5000:
        n += 1
        s += term
        term *= r
        if s > k:
            return ['n = ' + str(n), 'S(' + str(n) + ') = ' + fmt(s),
                    w('smallest n with S(n) > ' + fmt(k)),
                    w('S(n) = a(1-r^n)/(1-r)')]
        if term > 1e300 or term < -1e300:
            break
    return ['no n up to ' + str(n), warn('S(n) never passes ' + fmt(k)),
            w('S(' + str(n) + ') = ' + fmt(s))]


def _pq(p, q):
    pi = _whole(p, 'p')
    qi = _whole(q, 'q')
    if pi < 1 or qi < 1:
        raise ValueError('term numbers start at 1')
    if pi == qi:
        raise ValueError('p and q must differ')
    return (pi, qi)


def _aplines(a, d):
    return ['a = ' + fmt(a), 'd = ' + fmt(d),
            'u(n) = ' + _linstr([d, a - d], ['n', '']),
            'S(n) = ' + _linstr([d / 2.0, a - d / 2.0], ['n^2', 'n'])]


def t_ap2(p, up, q, uq):
    pi, qi = _pq(p, q)
    d = (uq - up) / float(qi - pi)
    a = up - (pi - 1) * d
    return _aplines(a, d) + [
        w('a + ' + str(pi - 1) + 'd = ' + fmt(up)),
        w('a + ' + str(qi - 1) + 'd = ' + fmt(uq)),
        w('subtract: ' + str(qi - pi) + 'd = ' + fmt(uq - up))]


def t_apsum(p, up, q, sq):
    pi, qi = _pq(p, q)
    c2 = qi * (qi - 1) / 2.0
    det = c2 - (pi - 1) * qi
    if det == 0:
        raise ValueError('these two facts do not fix a and d')
    d = (sq - qi * up) / det
    a = up - (pi - 1) * d
    return _aplines(a, d) + [
        w('a + ' + str(pi - 1) + 'd = ' + fmt(up)),
        w('S(' + str(qi) + ') = ' + str(qi) + '/2 (2a + ' + str(qi - 1) +
          'd) = ' + fmt(sq)),
        w(str(qi) + 'a + ' + fmt(c2) + 'd = ' + fmt(sq))]


def t_gp2(p, up, q, uq):
    pi, qi = _pq(p, q)
    if up == 0 or uq == 0:
        raise ValueError('a GP term cannot be 0')
    k = qi - pi
    ratio = uq / float(up)
    ak = k if k > 0 else -k
    if k < 0:
        ratio = 1.0 / ratio
    if ratio < 0 and ak % 2 == 0:
        raise ValueError('no real r: r^' + str(ak) + ' < 0')
    mag = math.pow(abs(ratio), 1.0 / ak)
    rs = [mag if ratio > 0 else -mag]
    if ak % 2 == 0:
        rs = [mag, -mag]
    out = []
    for r in rs:
        a = up / math.pow(r, pi - 1)
        s = 'r = ' + fmt(r) + ', a = ' + fmt(a)
        if abs(r) < 1:
            s += ', S(inf) = ' + fmt(a / (1.0 - r))
        out.append(s)
    out.append(w('r^' + str(ak) + ' = ' + fmt(ratio)))
    out.append(w('a = u(' + str(pi) + ')/r^' + str(pi - 1)))
    if len(rs) == 2:
        out.append(warn('even power: r can take either sign'))
    return out

def t_binom_int(a, b, n):
    ni = _whole(n, 'n')
    if ni < 0 or ni > 20:
        raise ValueError('n must be 0 to 20')
    exact = _isint(a) and _isint(b)
    coeffs = []
    k = 0
    while k <= ni:
        c = casutil.ncr(ni, k)
        if exact:
            v = c * (int(a) ** (ni - k)) * (int(b) ** k)
        else:
            v = c * math.pow(float(a), ni - k) * math.pow(float(b), k)
        coeffs.append(v)
        k += 1
    lines = []
    if exact and ni <= 12:
        rat = [caspoly.rmake(int(v), 1) for v in coeffs]
        lines.append(m(caspoly.ptree(rat, 'x')))
    k = 0
    while k <= ni:
        lines.append('x^' + str(k) + ': ' + fmt(coeffs[k]))
        k += 1
    lines.append(w('term k = C(n,k) a^(n-k) b^k'))
    lines.append(w('C(' + str(ni) + ',1) = ' + str(casutil.ncr(ni, 1))))
    return lines


def t_binom_rat(a, b, n):
    if a == 0:
        raise ValueError('a must not be 0')
    if b == 0:
        raise ValueError('b must not be 0')
    if a < 0 and not _isint(n):
        raise ValueError('a must be positive for a fractional power')
    an = math.pow(float(a), float(n)) if a > 0 else float(a) ** int(n)
    u = b / float(a)
    lines = []
    c = 1.0
    k = 0
    ex = caseng._fltrat(float(n)) is not None and \
        caseng._fltrat(float(a)) is not None and \
        caseng._fltrat(float(b)) is not None
    while k < 5:
        if k > 0:
            c = c * (n - k + 1) / k
        v = an * c * math.pow(u, k)
        txt = fmt(v)
        if ex and txt.find('.') >= 0:
            # exact: a^n C(n,k) (b/a)^k with a^n kept as a power
            node = ('*', ('^', _exn(a), _exn(n)),
                    ('*', _exn(c), ('^', _exn(u), ('n', k))))
            et = caseng.simplify(node)
            if caseng.tostr(et).find('.') < 0 and \
                    abs(casutil.ev(et) - v) < 1e-9 * (1 + abs(v)):
                txt = caseng.tostr(et)
        lines.append('x^' + str(k) + ': ' + txt)
        k += 1
    lim = a / float(b)
    if lim < 0:
        lim = -lim
    lines.append('valid for |x| < ' + fmt(lim))
    lines.append(w('(a+bx)^n = a^n (1 + (b/a)x)^n'))
    lines.append(w('C(n,k) = n(n-1)...(n-k+1)/k!'))
    if _isint(n) and n >= 0:
        lines.append(warn('n is a positive integer: the series stops'))
    return lines


def _sigsym(f, lo, hi):
    # sum of f(r) with letters kept: sum of r^k by formula, so wide ranges
    # cost nothing
    co = _xcoeffs(f, 'r', 3)
    if co is None:
        if hi - lo > 60:
            raise ValueError('with letters, at most 61 terms')
        node = None
        r = lo
        while r <= hi:
            t = caseng.subst(f, 'r', ('n', r))
            node = t if node is None else ('+', node, t)
            r += 1
        return caseng.simplify(caspoly.expand(node))
    pw = []
    for k in range(len(co)):
        tot = 0
        r = lo
        if hi - lo <= 2000:
            while r <= hi:
                tot += r ** k
                r += 1
        else:
            raise ValueError('range is too wide')
        pw.append(tot)
    node = None
    for k in range(len(co)):
        if co[k] == ('n', 0):
            continue
        t = ('*', ('n', pw[k]), co[k])
        node = t if node is None else ('+', node, t)
    if node is None:
        return ('n', 0)
    return caseng.simplify(caspoly.expand(node))


def t_sigma(f, a, b):
    lo, hi = _span(a, b, 5000)
    if [v for v in caseng.vars_in(f) if v != 'r']:
        t = _sigsym(f, lo, hi)
        return [m(t), 'sum = ' + caseng.tostr(t),
                str(hi - lo + 1) + ' terms, r = ' + str(lo) + ' to ' + str(hi),
                w('letters other than r are constants')]
    total = 0.0
    itotal = 0
    allint = True
    r = lo
    first = []
    while r <= hi:
        v = _val(f, float(r), False, 'r')
        if v is None:
            raise ValueError('f(r) is undefined at r = ' + str(r))
        total += v
        if allint and _isint(v):
            itotal += int(v)
        else:
            allint = False
        if len(first) < 4:
            first.append(fmt(v))
        r += 1
    val = itotal if allint else total
    return ['sum = ' + fmt(val),
            str(hi - lo + 1) + ' terms, r = ' + str(lo) + ' to ' + str(hi),
            w('f(r) = ' + caseng.tostr(caseng.simplify(f))),
            w('terms: ' + ', '.join(first) + (' ...' if hi - lo >= 4 else ''))]


def t_recur(f, u1, n):
    ni = _whole(n, 'n')
    if ni < 2 or ni > 1000:
        raise ValueError('n must be 2 to 1000')
    terms = [float(u1)]
    i = 1
    lines = []
    while i < ni:
        v = _val(f, terms[i - 1], False, 'u')
        if v is None:
            lines.append(warn('u(' + str(i + 1) + ') is undefined'))
            break
        terms.append(v)
        i += 1
    out = []
    show = range(len(terms)) if len(terms) <= 12 else \
        list(range(6)) + [len(terms) - 2, len(terms) - 1]
    for j in show:
        out.append('u(' + str(j + 1) + ') = ' + fmt(terms[j]))
    beh = _behave(terms)
    lim = _fixpt(f, terms)
    if lim is not None:
        beh = ['converges to L = ' + fmt(lim)] + \
            [b for b in beh if not b.startswith('converging')]
        lines.append(w('L = f(L) at the limit'))
    return out + beh + lines + \
        [w('u(n+1) = ' + caseng.tostr(caseng.simplify(f)))]


def _fixpt(f, terms):
    # the limit when the terms settle (run on to 200 terms to see)
    t = list(terms)
    while len(t) < 200:
        v = _val(f, t[len(t) - 1], False, 'u')
        if v is None or abs(v) > 1e12:
            return None
        t.append(v)
    a = t[len(t) - 1]
    b = t[len(t) - 2]
    if abs(a - b) > 1e-9 * (1.0 + abs(a)):
        return None
    g = _val(f, a, False, 'u')
    if g is None or abs(g - a) > 1e-9 * (1.0 + abs(a)):
        return None
    return _snap(a)


def t_recsum(f, u1, N):
    ni = _whole(N, 'N')
    if ni < 1 or ni > 1000000:
        raise ValueError('N must be 1 to 1000000')
    m = ni if ni < 40 else 40
    terms = [float(u1)]
    while len(terms) < m:
        v = _val(f, terms[len(terms) - 1], False, 'u')
        if v is None:
            raise ValueError('u(' + str(len(terms) + 1) + ') is undefined')
        terms.append(v)
    beh = _behave(terms)
    per = 0
    if beh and beh[0].startswith('periodic'):
        per = int(beh[0].split(' ')[2])
    out = []
    if ni <= m:
        tot = 0.0
        for t in terms:
            tot += t
        out.append('sum u(1..' + str(ni) + ') = ' + fmt(tot))
    elif per:
        cyc = 0.0
        for t in terms[:per]:
            cyc += t
        q = ni // per
        r = ni % per
        part = 0.0
        for t in terms[:r]:
            part += t
        out.append('sum u(1..' + str(ni) + ') = ' + fmt(q * cyc + part))
        out.append(w('period ' + str(per) + ', one cycle sums to ' + fmt(cyc)))
        out.append(w(str(ni) + ' = ' + str(q) + ' x ' + str(per) + ' + ' + str(r)))
        out.append(w(str(q) + ' x ' + fmt(cyc) + ' + ' + fmt(part)))
    else:
        if ni > 200:
            raise ValueError('not periodic: N up to 200')
        tot = 0.0
        last = terms[0]
        k = 1
        tot = last
        while k < ni:
            last = _val(f, last, False, 'u')
            if last is None:
                raise ValueError('u(' + str(k + 1) + ') is undefined')
            tot += last
            k += 1
        out.append('sum u(1..' + str(ni) + ') = ' + fmt(tot))
        out.append('u(' + str(ni) + ') = ' + fmt(last))
    out.append(w('u(1..4) = ' + ', '.join([fmt(t) for t in terms[:4]])))
    return out + beh

def t_uterm(u, n1, count):
    a = _whole(n1, 'n1')
    c = _whole(count, 'count')
    if c < 1 or c > 30:
        raise ValueError('count must be 1 to 30')
    terms = []
    out = []
    i = 0
    while i < c:
        v = _snap(_val(u, float(a + i), False, 'n'))
        if v is None:
            out.append(warn('u(' + str(a + i) + ') is undefined'))
            break
        terms.append(v)
        out.append('u(' + str(a + i) + ') = ' + fmt(v))
        i += 1
    return out + _behave(terms) + \
        [w('u(n) = ' + caseng.tostr(caseng.simplify(u)))]


def _behave(terms):
    if len(terms) < 2:
        return []
    up = True
    down = True
    i = 1
    while i < len(terms):
        if terms[i] <= terms[i - 1]:
            up = False
        if terms[i] >= terms[i - 1]:
            down = False
        i += 1
    period = 0
    i = 1
    while i < len(terms) and not period:
        d = terms[i] - terms[0]
        if d < 1e-9 and d > -1e-9:
            ok = True
            j = 0
            while j + i < len(terms):
                e = terms[j + i] - terms[j]
                if e > 1e-9 or e < -1e-9:
                    ok = False
                    break
                j += 1
            if ok and j > 0:
                period = i
        i += 1
    if period:
        return ['periodic, period ' + str(period)]
    if up:
        return ['increasing']
    if down:
        return ['decreasing']
    last = terms[len(terms) - 1]
    d1 = last - terms[len(terms) - 2]
    if d1 < 1e-7 * (1.0 + (last if last >= 0 else -last)) and \
            d1 > -1e-7 * (1.0 + (last if last >= 0 else -last)):
        return ['converging to about ' + sf3(last)]
    return ['neither increasing nor decreasing']


def t_ncrnpr(n, r):
    ni = _whole(n, 'n')
    ri = _whole(r, 'r')
    if ni < 0 or ri < 0:
        raise ValueError('n and r must not be negative')
    if ni > 300:
        raise ValueError('n must be 300 or less')
    if ri > ni:
        return ['nCr = 0', 'nPr = 0', warn('r > n')]
    fn = casutil.fact(ni)
    return ['nCr = ' + str(casutil.ncr(ni, ri)),
            'nPr = ' + str(casutil.npr(ni, ri)),
            'n! = ' + (str(fn) if fn is not None else 'too large'),
            w('nCr = n! / (r! (n-r)!)'), w('nPr = n! / (n-r)!')]

# =================================================== E  Trigonometry ======

_SIN15 = [[], [(1, 4, 6), (-1, 4, 2)], [(1, 2, 1)], [(1, 2, 2)],
          [(1, 2, 3)], [(1, 4, 6), (1, 4, 2)], [(1, 1, 1)]]


def _exact_sin(d):
    # exact sin of d degrees as a surd sum, or None
    d = d % 360
    if d % 15:
        return None
    if d <= 90:
        return _SIN15[d // 15]
    if d <= 180:
        return _SIN15[(180 - d) // 15]
    if d <= 270:
        return _ssneg(_SIN15[(d - 180) // 15])
    return _ssneg(_SIN15[(360 - d) // 15])


def _exact_cos(d):
    return _exact_sin(90 - d % 360)


def _exact_tan(d):
    s = _exact_sin(d)
    c = _exact_cos(d)
    if s is None or c is None or not c:
        return None
    return _ssdiv(s, c)


def _trigline(name, d, ss, val):
    if ss is not None:
        return name + ' ' + fmt(d) + ' = ' + _ssstr(ss)
    return name + ' ' + fmt(d) + ' = ' + sf3(val)


def t_exact_deg(x):
    d = _whole(x, 'x')
    rd = casutil.rad(d)
    lines = [_trigline('sin', d, _exact_sin(d), math.sin(rd)),
             _trigline('cos', d, _exact_cos(d), math.cos(rd))]
    c = _exact_cos(d)
    if c is not None and not c:
        lines.append('tan ' + str(d) + ' is undefined')
    else:
        lines.append(_trigline('tan', d, _exact_tan(d), math.tan(rd)))
    lines.append(w(str(d) + ' deg = ' + fmt(rd) + ' rad'))
    if d % 15:
        lines.append(warn('not a standard angle: decimals only'))
    return lines


def _tri_lines(a, b, c, A, B, C):
    area = 0.5 * a * b * math.sin(casutil.rad(C))
    return ['a = ' + fmt(a) + '  A = ' + fmt(A) + ' deg',
            'b = ' + fmt(b) + '  B = ' + fmt(B) + ' deg',
            'c = ' + fmt(c) + '  C = ' + fmt(C) + ' deg',
            'area = ' + fmt(area),
            'perimeter = ' + fmt(a + b + c),
            w('in rad: A = ' + fmt(casutil.rad(A)) + ', B = ' +
              fmt(casutil.rad(B)) + ', C = ' + fmt(casutil.rad(C))),
            w('area = (1/2) a b sin C')]


def t_sss(a, b, c):
    for v, nm in ((a, 'a'), (b, 'b'), (c, 'c')):
        _pos(v, nm)
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError('those three sides cannot make a triangle')
    A = casutil.deg(casutil.acos_safe((b * b + c * c - a * a) / (2.0 * b * c)))
    B = casutil.deg(casutil.acos_safe((a * a + c * c - b * b) / (2.0 * a * c)))
    C = 180.0 - A - B
    return _tri_lines(a, b, c, A, B, C) + \
        [w('cos A = (b^2 + c^2 - a^2) / 2bc')]


def t_sas(b, c, A):
    _pos(b, 'b')
    _pos(c, 'c')
    if A <= 0 or A >= 180:
        raise ValueError('A must be between 0 and 180')
    a = math.sqrt(b * b + c * c - 2.0 * b * c * math.cos(casutil.rad(A)))
    B = casutil.deg(casutil.acos_safe((a * a + c * c - b * b) / (2.0 * a * c)))
    C = 180.0 - A - B
    return _tri_lines(a, b, c, A, B, C) + \
        [w('a^2 = b^2 + c^2 - 2bc cos A = ' + fmt(a * a))]


def t_asa(A, B, a):
    _pos(a, 'a')
    if A <= 0 or B <= 0 or A + B >= 180:
        raise ValueError('need A > 0, B > 0 and A + B < 180')
    C = 180.0 - A - B
    k = a / math.sin(casutil.rad(A))
    b = k * math.sin(casutil.rad(B))
    c = k * math.sin(casutil.rad(C))
    return _tri_lines(a, b, c, A, B, C) + \
        [w('a/sin A = b/sin B = c/sin C = ' + fmt(k))]


def t_ssa(a, b, A):
    _pos(a, 'a')
    _pos(b, 'b')
    if A <= 0 or A >= 180:
        raise ValueError('A must be between 0 and 180')
    s = b * math.sin(casutil.rad(A)) / a
    if s > 1.0 + 1e-12:
        return ['no triangle', warn('sin B would be ' + fmt(s) + ' > 1'),
                w('sin B = b sin A / a')]
    if s > 1.0:
        s = 1.0
    B = casutil.deg(math.asin(s))
    C = 180.0 - A - B
    c = a * math.sin(casutil.rad(C)) / math.sin(casutil.rad(A))
    lines = _tri_lines(a, b, c, A, B, C)
    B2 = 180.0 - B
    if a < b and A + B2 < 180.0 and B2 - B > 1e-9:
        C2 = 180.0 - A - B2
        c2 = a * math.sin(casutil.rad(C2)) / math.sin(casutil.rad(A))
        lines.append(warn('ambiguous: B = ' + fmt(B2) + ' also works'))
        lines.append(warn('then C = ' + fmt(C2) + ', c = ' + fmt(c2)))
    lines.append(w('sin B = b sin A / a = ' + fmt(s)))
    return lines


def t_tri_area(a, b, C):
    _pos(a, 'a')
    _pos(b, 'b')
    area = 0.5 * a * b * math.sin(casutil.rad(C))
    if area < 0:
        area = -area
    return ['area = ' + fmt(area),
            w('area = (1/2) a b sin C'),
            w('sin ' + fmt(C) + ' = ' + sf3(math.sin(casutil.rad(C))))]


def _exv(tree, v):
    # exact text for tree when it is clean and matches v, else fmt(v)
    try:
        t = caseng.simplify(tree)
        try:
            t2 = caspoly.collect(caspoly.expand(t))
            if len(caseng.tostr(t2)) <= len(caseng.tostr(t)):
                t = t2
        except Exception:
            pass
        s = caseng.tostr(t)
        if s.find('.') < 0 and not caseng.vars_in(t) and \
                abs(casutil.ev(t) - v) < 1e-9 * (1 + abs(v)):
            return s
    except Exception:
        pass
    return fmt(v)


def _arc(r, th):
    arc = r * th
    area = 0.5 * r * r * th
    chord = 2.0 * r * math.sin(th / 2.0)
    seg = 0.5 * r * r * (th - math.sin(th))
    R = _exn(r)
    T = _exn(th)
    half = ('*', ('/', ('n', 1), ('n', 2)), ('^', R, ('n', 2)))
    segt = fmt(seg)
    chdt = fmt(chord)
    if caseng.tostr(T).find('pi') >= 0:
        segt = _exv(('*', half, ('-', T, ('sin', T))), seg)
        chdt = _exv(('*', ('*', ('n', 2), R), ('sin', ('/', T, ('n', 2)))), chord)
    return ['arc = ' + fmt(arc), 'sector area = ' + fmt(area),
            'chord = ' + chdt, 'segment area = ' + segt,
            'sector perimeter = ' + (fmt(arc + 2.0 * r) if segt == fmt(seg) else
                                     _exv(('+', ('*', R, T), ('*', ('n', 2), R)),
                                          arc + 2.0 * r)),
            w('arc = r th, area = (1/2) r^2 th, th in rad'),
            w('th = ' + fmt(th) + ' rad = ' + fmt(casutil.deg(th)) + ' deg')]


def t_arc_rad(r, th):
    _pos(r, 'r')
    return _arc(r, float(th))


def t_arc_deg(r, th):
    _pos(r, 'r')
    return _arc(r, casutil.rad(float(th)))


def t_d2r(x):
    v = casutil.rad(float(x))
    return [fmt(x) + ' deg = ' + fmt(v) + ' rad', 'decimal = ' + sf3(v),
            w('rad = deg x pi / 180')]


def t_r2d(x):
    v = casutil.deg(float(x))
    return [fmt(x) + ' rad = ' + fmt(v) + ' deg', 'decimal = ' + sf3(v),
            w('deg = rad x 180 / pi')]


def _defined(f, x, deg):
    # f really defined at x: no denominator (or cos under tan) near 0
    ds = []
    _danger(f, ds)
    for d in ds:
        v = _val(d, x, deg)
        if v is not None and abs(v) < 1e-9:
            return False
    return True


def _eqn_lines(f, lo, hi, deg):
    rs = [r for r in _scan(f, lo, hi, deg) if _defined(f, r, deg)]
    unit = ' deg' if deg else ''
    lines = []
    if not rs:
        lines.append('no solution in that interval')
    for r in rs[:12]:
        lines.append('x = ' + fmt(r) + unit)
    lines.append(w('f(x) = ' + caseng.tostr(caseng.simplify(f))))
    lines.append(w(str(len(rs)) + ' root(s) in ' + fmt(lo) + ' to ' + fmt(hi)))
    if len(rs) >= 12:
        lines.append(warn('only the first 12 are listed'))
    return lines


def t_trigeq_deg(f, lo, hi):
    return _eqn_lines(f, float(lo), float(hi), True)


def t_trigeq_rad(f, lo, hi):
    return _eqn_lines(f, float(lo), float(hi), False)


def _angles(kind, k, lo, hi):
    out = []
    if hi - lo > 72000.0:
        raise ValueError('the interval is too wide')
    if kind == 't':
        base = casutil.deg(math.atan(k))
        partners = [base]
        period = 180.0
    else:
        if k > 1.0 or k < -1.0:
            return None
        if kind == 's':
            base = casutil.deg(math.asin(k))
            partners = [base, 180.0 - base]
        else:
            base = casutil.deg(math.acos(k))
            partners = [base, -base]
        period = 360.0
    for p in partners:
        n = int((lo - p) / period) - 2
        while n <= int((hi - p) / period) + 2:
            x = p + n * period
            if lo - 1e-9 <= x <= hi + 1e-9:
                dup = False
                for e in out:
                    if e - x < 1e-7 and x - e < 1e-7:
                        dup = True
                if not dup:
                    out.append(x)
            n += 1
    out.sort()
    return out


def _quadtrig(kind, name, a, b, c, lo, hi):
    if a == 0 and b == 0:
        raise ValueError('a and b are both 0')
    lo = float(lo)
    hi = float(hi)
    if hi <= lo:
        raise ValueError('hi must be more than lo')
    if a == 0:
        vs = [-c / float(b)]
    else:
        D = b * b - 4.0 * a * c
        if D < 0:
            return ['no solution', warn('disc = ' + fmt(D) + ' < 0'),
                    w('let s = ' + name + ' x, then a s^2 + b s + c = 0')]
        rt = math.sqrt(D)
        vs = [(-b - rt) / (2.0 * a)]
        if D > 0:
            vs.append((-b + rt) / (2.0 * a))
    lines = []
    any_root = False
    for v in vs:
        lines.append(name + ' x = ' + fmt(v))
        xs = _angles(kind, v, lo, hi)
        if xs is None:
            lines.append(warn('|' + name + ' x| > 1: no solution'))
            continue
        if not xs:
            lines.append(warn('none in ' + fmt(lo) + ' to ' + fmt(hi)))
            continue
        any_root = True
        for x in xs[:8]:
            lines.append('  x = ' + fmt(x) + ' deg')
    if not any_root:
        lines.insert(0, 'no solution in that interval')
    lines.append(w('let s = ' + name + ' x, solve a s^2 + b s + c = 0'))
    return lines


def t_quadsin(a, b, c, lo, hi):
    return _quadtrig('s', 'sin', a, b, c, lo, hi)


def t_quadcos(a, b, c, lo, hi):
    return _quadtrig('c', 'cos', a, b, c, lo, hi)


def t_quadtan(a, b, c, lo, hi):
    return _quadtrig('t', 'tan', a, b, c, lo, hi)


def t_rform(a, b):
    if a == 0 and b == 0:
        raise ValueError('a and b are both 0')
    R = math.sqrt(a * a + b * b)
    al = casutil.deg(math.atan2(b, a))
    be = casutil.deg(math.atan2(a, b))
    return ['R = ' + fmt(R),
            'a sin x + b cos x = R sin(x + al)',
            'al = ' + fmt(al) + ' deg = ' + fmt(casutil.rad(al)) + ' rad',
            '= R cos(x - be), be = ' + fmt(be) + ' deg',
            'max ' + fmt(R) + ' at x = ' + fmt(90.0 - al) + ' deg',
            'min ' + fmt(-R) + ' at x = ' + fmt(270.0 - al) + ' deg',
            w('R = sqrt(a^2 + b^2) = sqrt(' + fmt(a * a + b * b) + ')'),
            w('tan al = b/a, tan be = a/b')]


def t_small(x):
    v = float(x)
    av = v if v >= 0 else -v
    lines = ['sin: approx ' + sf3(v) + ', exact ' + sf3(math.sin(v)),
             'cos: approx ' + sf3(1.0 - v * v / 2.0) + ', exact ' +
             sf3(math.cos(v)),
             'tan: approx ' + sf3(v) + ', exact ' + sf3(math.tan(v)),
             w('sin x ~ x, cos x ~ 1 - x^2/2, tan x ~ x'),
             w('x = ' + fmt(v) + ' rad = ' + fmt(casutil.deg(v)) + ' deg')]
    if av > 0.5:
        lines.append(warn('x is not small: the approximation is poor'))
    return lines


def _compound(A, B):
    sa = _exact_sin(A)
    ca = _exact_cos(A)
    sb = _exact_sin(B)
    cb = _exact_cos(B)
    if sa is None or ca is None or sb is None or cb is None:
        return None
    sp = _ssadd(_ssmul(sa, cb), _ssmul(ca, sb))
    sm = _ssadd(_ssmul(sa, cb), _ssneg(_ssmul(ca, sb)))
    cp = _ssadd(_ssmul(ca, cb), _ssneg(_ssmul(sa, sb)))
    cm = _ssadd(_ssmul(ca, cb), _ssmul(sa, sb))
    return (sp, sm, cp, cm)


def t_compound(A, B):
    a = _whole(A, 'A')
    b = _whole(B, 'B')
    r = _compound(a, b)
    if r is None:
        raise ValueError('A and B must be multiples of 15 degrees')
    sp, sm, cp, cm = r
    lines = ['sin(' + str(a) + '+' + str(b) + ') = ' + _ssstr(sp),
             'cos(' + str(a) + '+' + str(b) + ') = ' + _ssstr(cp),
             'sin(' + str(a) + '-' + str(b) + ') = ' + _ssstr(sm),
             'cos(' + str(a) + '-' + str(b) + ') = ' + _ssstr(cm)]
    tp = _ssdiv(sp, cp)
    if tp is not None:
        lines.append('tan(' + str(a) + '+' + str(b) + ') = ' + _ssstr(tp))
    elif not cp:
        lines.append('tan(' + str(a) + '+' + str(b) + ') is undefined')
    lines.append(m(_sstree(sp)))
    lines.append(w('sin(A+B) = sinA cosB + cosA sinB'))
    lines.append(w('cos(A+B) = cosA cosB - sinA sinB'))
    lines.append(w('decimal ' + sf3(_ssval(sp))))
    return lines


def t_double(A):
    a = _whole(A, 'A')
    sa = _exact_sin(a)
    ca = _exact_cos(a)
    if sa is None or ca is None:
        raise ValueError('A must be a multiple of 15 degrees')
    s2 = _ssmul(_ss(2, 1, 1), _ssmul(sa, ca))
    c2 = _ssadd(_ssmul(ca, ca), _ssneg(_ssmul(sa, sa)))
    lines = ['sin ' + str(2 * a) + ' = ' + _ssstr(s2),
             'cos ' + str(2 * a) + ' = ' + _ssstr(c2)]
    t2 = _ssdiv(s2, c2)
    if t2 is not None:
        lines.append('tan ' + str(2 * a) + ' = ' + _ssstr(t2))
    elif not c2:
        lines.append('tan ' + str(2 * a) + ' is undefined')
    lines.append(w('sin 2A = 2 sinA cosA'))
    lines.append(w('cos 2A = cos^2 A - sin^2 A'))
    lines.append(w('decimal sin ' + sf3(_ssval(s2))))
    return lines


def t_recip(x):
    rd = casutil.rad(float(x))
    s = math.sin(rd)
    c = math.cos(rd)
    lines = []
    if c > 1e-12 or c < -1e-12:
        lines.append('sec = 1/cos = ' + fmt(1.0 / c))
    else:
        lines.append('sec is undefined (cos = 0)')
    if s > 1e-12 or s < -1e-12:
        lines.append('cosec = 1/sin = ' + fmt(1.0 / s))
        lines.append('cot = cos/sin = ' + fmt(c / s))
    else:
        lines.append('cosec and cot are undefined')
    lines.append(w('sin = ' + sf3(s) + ', cos = ' + sf3(c)))
    lines.append(w('sec^2 = 1 + tan^2, cosec^2 = 1 + cot^2'))
    return lines


def t_ratios(sv, cv, tv, quad):
    # every ratio exactly from one rational ratio and the quadrant
    q = _whole(quad, 'quadrant')
    if q < 1 or q > 4:
        raise ValueError('quadrant is 1 to 4')
    given = [x for x in (sv, cv, tv) if x is not None]
    if len(given) != 1:
        raise ValueError('give one of sin, cos, tan')
    r = caseng._fltrat(float(given[0]))
    if r is None:
        raise ValueError('give the ratio as a fraction')
    p, d = r
    ssg = 1 if q in (1, 2) else -1
    csg = 1 if q in (1, 4) else -1
    if sv is not None:
        if abs(p) > d:
            raise ValueError('|sin| must be at most 1')
        S = _ss(p, d, 1)
        C = _ss(csg, d, d * d - p * p)
    elif cv is not None:
        if abs(p) > d:
            raise ValueError('|cos| must be at most 1')
        C = _ss(p, d, 1)
        S = _ss(ssg, d, d * d - p * p)
    else:
        h = p * p + d * d
        C = _ss(csg * d, 1, 1)
        C = _ssdiv(C, _ss(1, 1, h))
        S = _ssdiv(_ss(ssg * abs(p), 1, 1), _ss(1, 1, h))
    if (S and (_ssval(S) > 0) != (ssg > 0)) or (C and (_ssval(C) > 0) != (csg > 0)):
        raise ValueError('that sign does not fit quadrant ' + str(q))
    out = ['sin x = ' + _ssstr(S), 'cos x = ' + _ssstr(C)]
    if C:
        out.append('tan x = ' + _ssstr(_ssdiv(S, C)))
        out.append(w('sec x = ' + _ssstr(_ssdiv(_ss(1, 1, 1), C))))
    else:
        out.append('tan x is undefined')
    if S:
        out.append(w('cosec x = ' + _ssstr(_ssdiv(_ss(1, 1, 1), S))))
        if C:
            out.append(w('cot x = ' + _ssstr(_ssdiv(C, S))))
    ang = casutil.deg(math.atan2(_ssval(S), _ssval(C)))
    if ang < 0:
        ang += 360.0
    out.append(w('x = ' + sf3(ang) + ' deg in quadrant ' + str(q)))
    out.append(w('sin^2 x + cos^2 x = 1'))
    return out


def t_arcs(v):
    x = float(v)
    lines = []
    if x > 1.0 or x < -1.0:
        lines.append(warn('|v| > 1: arcsin and arccos are undefined'))
    else:
        a = math.asin(x)
        b = math.acos(x)
        lines.append('arcsin = ' + fmt(casutil.deg(a)) + ' deg')
        lines.append('arccos = ' + fmt(casutil.deg(b)) + ' deg')
        lines.append(w('arcsin = ' + fmt(a) + ' rad, arccos = ' + fmt(b) +
                       ' rad'))
    t = math.atan(x)
    lines.append('arctan = ' + fmt(casutil.deg(t)) + ' deg')
    lines.append(w('arctan = ' + fmt(t) + ' rad'))
    lines.append(w('arcsin -90..90, arccos 0..180 deg'))
    return lines


def t_identity(f, g, a, b):
    bad = None
    tested = 0
    if (a is None) != (b is None):
        raise ValueError('give both a and b, or neither')
    if a is not None and b <= a:
        raise ValueError('need a < b')
    i = 0
    while i < 40:
        x = 0.17 + i * 0.13 if a is None else a + (b - a) * (i + 0.5) / 40.0
        u = _val(f, x)
        v = _val(g, x)
        i += 1
        if u is None or v is None:
            continue
        tested += 1
        d = u - v
        tol = 1e-7 * (1.0 + (u if u >= 0 else -u))
        if d > tol or d < -tol:
            bad = (x, u, v)
            break
    if tested == 0:
        raise ValueError('neither side could be evaluated')
    if bad is None:
        return ['holds at every x tested',
                w(str(tested) + ' values of x in ' +
                  ('0.17 to 5.2' if a is None else fmt(a) + ' to ' + fmt(b)) +
                  ' rad'),
                warn('testing is not a proof')]
    return ['not an identity', 'x = ' + sf3(bad[0]) + ' rad',
            'f = ' + sf3(bad[1]) + ', g = ' + sf3(bad[2]),
            w('one counterexample is enough')]

# ================================= F  Exponentials and logarithms =========


def t_ax_b(a, b):
    if a <= 0 or a == 1:
        raise ValueError('a must be positive and not 1')
    if b <= 0:
        return ['no real solution', warn('a^x is always positive'),
                w('b = ' + fmt(b) + ' is not positive')]
    x = math.log(b) / math.log(a)
    n = int(x + 0.5) if x >= 0 else int(x - 0.5)
    lines = []
    if math.pow(float(a), n) - b < 1e-9 and b - math.pow(float(a), n) < 1e-9:
        lines.append('x = ' + str(n))
    else:
        lines.append('x = ' + sf3(x))
    lines.append(w('x = ln b / ln a = ' + sf3(math.log(b)) + ' / ' +
                   sf3(math.log(a))))
    lines.append(w('take logs of both sides'))
    return lines


def t_logsolve(a, c):
    if a <= 0 or a == 1:
        raise ValueError('a must be positive and not 1')
    x = math.pow(float(a), float(c))
    lines = ['x = ' + fmt(x)]
    if fmt(x) != sf3(x):
        lines.append('decimal = ' + sf3(x))
    return lines + [w('log_a x = c means x = a^c'),
                    w('a = ' + fmt(a) + ', c = ' + fmt(c))]


def t_logb(a, x):
    if a <= 0 or a == 1:
        raise ValueError('a must be positive and not 1')
    if x <= 0:
        raise ValueError('x must be positive')
    v = math.log(x) / math.log(a)
    n = int(v + 0.5) if v >= 0 else int(v - 0.5)
    lines = []
    if math.pow(float(a), n) - x < 1e-9 and x - math.pow(float(a), n) < 1e-9:
        lines.append('log_' + fmt(a) + ' ' + fmt(x) + ' = ' + str(n))
    else:
        lines.append('log_' + fmt(a) + ' ' + fmt(x) + ' = ' + sf3(v))
    lines.append('ln x = ' + sf3(math.log(x)))
    lines.append('log10 x = ' + sf3(math.log10(x)))
    lines.append(w('change of base: log_a x = ln x / ln a'))
    return lines


def _haslog(t):
    k = t[0]
    if k == 'ln' or k == 'log' or k == 'logb':
        return True
    if k == 'n' or k == 'v':
        return False
    if len(t) == 3:
        return _haslog(t[1]) or _haslog(t[2])
    return _haslog(t[1])


def _lsplit(t, c, logs, rest):
    # t * c as log terms [(coef, base, arg)] plus log-free rest [tree]
    k = t[0]
    if k == '+' or k == '-':
        _lsplit(t[1], c, logs, rest)
        _lsplit(t[2], c if k == '+' else ('neg', c), logs, rest)
        return
    if k == 'neg':
        _lsplit(t[1], ('neg', c), logs, rest)
        return
    if k == '*':
        a = _haslog(t[1])
        b = _haslog(t[2])
        if a and not b:
            _lsplit(t[1], ('*', c, t[2]), logs, rest)
            return
        if b and not a:
            _lsplit(t[2], ('*', c, t[1]), logs, rest)
            return
    if k == '/' and not _haslog(t[2]):
        _lsplit(t[1], ('/', c, t[2]), logs, rest)
        return
    if k == 'ln':
        logs.append((c, ('v', 'e'), t[1]))
    elif k == 'log':
        logs.append((c, ('n', 10), t[1]))
    elif k == 'logb':
        logs.append((c, caseng.simplify(t[1]), t[2]))
    elif _haslog(t):
        raise ValueError('cannot separate the logs')
    else:
        rest.append(('*', c, t))


def _lnode(b, u):
    if b == ('v', 'e'):
        return ('ln', u)
    if b == ('n', 10):
        return ('log', u)
    return ('logb', b, u)


def _lpieces(arg):
    # arg as [[base, exp]]: whole numbers split into prime powers
    mo = _mono(caseng.simplify(arg))
    out = []
    for n, sg in ((mo[0][0], 1), (mo[0][1], -1)):
        if n < 0:
            raise ValueError('log of a negative number')
        if n > 1:
            b = n
            e = 1
            k = 2
            while k <= 40:
                r = _iroot(n, k)
                if r is not None and r > 1:
                    b = r
                    e = k
                k += 1
            out.append([('n', b), ('n', e * sg)])
    for b, e, key in mo[1]:
        out.append([b, e])
    return out


def _exn(v):
    # exact node for a typed number: fractions, multiples of pi, surds
    if isinstance(v, int):
        return ('n', v)
    r = caseng._fltrat(float(v))
    if r is not None:
        return caseng._ratnode(r)
    q = caseng._fltrat(v / math.pi)
    if q is not None and q[1] <= 12 and abs(q[0]) <= 48:
        return caseng.simplify(('*', caseng._ratnode(q), ('v', 'pi')))
    q = caseng._fltrat(v * v)
    if q is not None and q[1] <= 64 and q[0] <= 4096:
        t = caseng.simplify(('sqrt', caseng._ratnode(q)))
        return t if v > 0 else caseng.simplify(('neg', t))
    return ('n', v)


def _sumtree(items):
    node = None
    for t in items:
        if t is None or t == ('n', 0):
            continue
        if node is None:
            node = t
        elif t[0] == 'neg':
            node = ('-', node, t[1])
        else:
            node = ('+', node, t)
    return node if node is not None else ('n', 0)


def _cterm(c, lg):
    # c * log, c simplified on its own so numeric logs stay exact
    c = caseng.simplify(c)
    if c == ('n', 0):
        return None
    if caseng._isneg(c):
        r = _cterm(caseng.simplify(caseng._negnode(c)), lg)
        return None if r is None else ('neg', r)
    if c == _ONE:
        return lg
    return ('*', c, lg)


def _kterm(K):
    if caseng._isneg(K):
        return ('neg', caseng.simplify(caseng._negnode(K)))
    return K


def _logforms(f):
    # -> (expanded tree, groups [(base, arg)], constant K) for f
    logs = []
    rest = []
    _lsplit(f, _ONE, logs, rest)
    if not logs:
        return None
    K = [_sumtree(rest)]
    groups = []
    for c, b, arg in logs:
        bk = caseng.tostr(b)
        grp = None
        for g in groups:
            if g[0] == bk:
                grp = g
        if grp is None:
            grp = [bk, b, []]
            groups.append(grp)
        for pb, pe in _lpieces(arg):
            k = caseng.simplify(('*', c, pe))
            if caseng.tostr(caseng.simplify(pb)) == bk:
                K.append(k)
                continue
            _mput(grp[2], pb, k)
    Kt = caseng.simplify(_sumtree(K))
    ex = []
    out = []
    for bk, b, items in groups:
        c = (1, 1)
        merged = []
        big = False
        for pb, k, key in items:
            if k == ('n', 0):
                continue
            ex.append(_cterm(k, _lnode(b, pb)))
            mo = _mono(caseng.simplify(('^', pb, k)))
            c = caspoly.rmul(c, mo[0])
            if c[0] > 10 ** 6 or c[0] < -10 ** 6 or c[1] > 10 ** 6:
                big = True
            for x in mo[1]:
                _mput(merged, x[0], x[1])
        if big:
            return (_sumtree(ex + [_kterm(Kt)]), [], None)
        arg = _mtree((c, merged))
        if arg != _ONE:
            out.append((b, arg))
    if Kt != ('n', 0) and caseng.vars_in(Kt):
        ex.insert(0, Kt)
    else:
        ex.append(_kterm(Kt))
    return (_sumtree(ex), out, Kt)


def _logsolve(b, arg, K):
    # log_b(arg) + K = 0 for x, arg a monomial with one power of x
    mo = _mono(arg)
    e = None
    rest = []
    for it in mo[1]:
        if it[0] == ('v', 'x'):
            e = caseng._ratval(it[1])
        elif 'x' in caseng.vars_in(it[0]):
            return None
        else:
            rest.append(it)
    if e is None or e[0] == 0:
        return None
    rhs = _mono(caseng.simplify(('^', b, ('neg', K))))
    rhs = (caspoly.rdiv(rhs[0], mo[0]), rhs[1])
    for x in rest:
        _mput(rhs[1], x[0], caseng.simplify(('neg', x[1])))
    return _mtree(_mpow(rhs, (e[1], e[0])))


def t_logeval(f):
    t = caseng.simplify(f)
    lines = []
    lf = None
    if _haslog(f):
        try:
            lf = _logforms(f)
        except ValueError:
            lf = None
    if lf is not None:
        ex, groups, K = lf
        one = None
        if K is None:
            one = ex
        elif len(groups) == 1:
            b, arg = groups[0]
            if K != ('n', 0) and b[0] == 'v' and b[1] != 'e':
                fold = _mtree(_mono(caseng.simplify(('*', arg, ('^', b, K)))))
                one = _lnode(b, fold)
            else:
                one = _sumtree([_lnode(b, arg), _kterm(K)])
        elif not groups:
            one = K
        if one is not None:
            lines.append(m(one))
            lines.append('= ' + caseng.tostr(one))
        if caseng.tostr(ex) != caseng.tostr(one):
            lines.append('= ' + caseng.tostr(ex))
        if len(groups) == 1 and 'x' in caseng.vars_in(groups[0][1]):
            sol = _logsolve(groups[0][0], groups[0][1], K)
            if sol is not None:
                lines.append('f = 0: x = ' + caseng.tostr(sol))
                lines.append(w(caseng.tostr(groups[0][1]) + ' = ' +
                               caseng.tostr(caseng.simplify(
                                   ('^', groups[0][0], ('neg', K))))))
    else:
        lines.append(m(t))
    if not caseng.vars_in(t):
        v = casutil.ev(t)
        lines.append('= ' + fmt(v))
        lines.append('decimal = ' + sf3(v))
    lines.append(w('log xy = log x + log y, log(x/y) = log x - log y'))
    lines.append(w('log x^k = k log x, log_a a = 1'))
    return lines


def t_powerlaw(x1, y1, x2, y2):
    for v, nm in ((x1, 'x1'), (y1, 'y1'), (x2, 'x2'), (y2, 'y2')):
        _pos(v, nm)
    if x1 == x2:
        raise ValueError('x1 and x2 must differ')
    n = (math.log(y2) - math.log(y1)) / (math.log(x2) - math.log(x1))
    a = y1 / math.pow(float(x1), n)
    node = ('*', _numnode(a), ('^', ('v', 'x'), _numnode(n)))
    return ['n = ' + fmt(n), 'a = ' + fmt(a), m(caseng.simplify(node)),
            w('log y = log a + n log x'),
            w('n = (log y2 - log y1) / (log x2 - log x1)')]


def t_expolaw(x1, y1, x2, y2):
    _pos(y1, 'y1')
    _pos(y2, 'y2')
    if x1 == x2:
        raise ValueError('x1 and x2 must differ')
    b = math.pow(y2 / y1, 1.0 / (x2 - x1))
    k = y1 / math.pow(b, float(x1))
    node = ('*', _numnode(k), ('^', _numnode(b), ('v', 'x')))
    return ['b = ' + fmt(b), 'k = ' + fmt(k), m(caseng.simplify(node)),
            w('log y = log k + x log b'),
            w('b = (y2/y1)^(1/(x2-x1))')]


def _pairs(data):
    if len(data) < 4 or len(data) % 2:
        raise ValueError('give an even number of values, at least 2 pairs')
    out = []
    i = 0
    while i < len(data):
        out.append((data[i], data[i + 1]))
        i += 2
    return out


def _fit(xs, ys):
    n = float(len(xs))
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for i in range(len(xs)):
        sx += xs[i]
        sy += ys[i]
        sxx += xs[i] * xs[i]
        sxy += xs[i] * ys[i]
    den = n * sxx - sx * sx
    if den == 0:
        raise ValueError('all the x values are the same')
    g = (n * sxy - sx * sy) / den
    c = (sy - g * sx) / n
    return (g, c)


def t_loglog(data):
    ps = _pairs(data)
    xs = []
    ys = []
    for x, y in ps:
        if x <= 0 or y <= 0:
            raise ValueError('all x and y must be positive')
        xs.append(math.log(x))
        ys.append(math.log(y))
    n, c = _fit(xs, ys)
    a = math.exp(c)
    node = ('*', _numnode(a), ('^', ('v', 'x'), _numnode(n)))
    return ['n = ' + sf3(n), 'a = ' + sf3(a), m(caseng.simplify(node)),
            str(len(ps)) + ' points',
            w('log y vs log x: gradient n, intercept log a'),
            w('intercept = ' + sf3(c))]


def t_loglin(data):
    ps = _pairs(data)
    xs = []
    ys = []
    for x, y in ps:
        if y <= 0:
            raise ValueError('all y must be positive')
        xs.append(x)
        ys.append(math.log(y))
    g, c = _fit(xs, ys)
    b = math.exp(g)
    k = math.exp(c)
    node = ('*', _numnode(k), ('^', _numnode(b), ('v', 'x')))
    return ['b = ' + sf3(b), 'k = ' + sf3(k), m(caseng.simplify(node)),
            str(len(ps)) + ' points',
            w('log y vs x: gradient log b, intercept log k'),
            w('gradient = ' + sf3(g)),
            'log10: gradient = ' + sf3(g / math.log(10.0)) +
            ', intercept = ' + sf3(c / math.log(10.0))]


def _halflife(k):
    if k == 0:
        return None
    return math.log(2.0) / (k if k > 0 else -k)


def t_expmodel(t1, N1, t2, N2, t, N):
    lines = _expmodel(t1, N1, t2, N2)
    k = (math.log(N2) - math.log(N1)) / (t2 - t1)
    A = N1 / math.exp(k * t1)
    if t is not None:
        lines.insert(2, 'N(' + fmt(t) + ') = ' + sf3(A * math.exp(k * t)))
    if N is not None:
        if N <= 0 or (A > 0) != (N > 0) or k == 0:
            lines.insert(2, warn('N never reaches ' + fmt(N)))
        else:
            lines.insert(2, 'N = ' + fmt(N) + ' at t = ' +
                         sf3(math.log(N / A) / k))
    return lines


def _expmodel(t1, N1, t2, N2):
    _pos(N1, 'N1')
    _pos(N2, 'N2')
    if t1 == t2:
        raise ValueError('t1 and t2 must differ')
    k = (math.log(N2) - math.log(N1)) / (t2 - t1)
    A = N1 / math.exp(k * t1)
    lines = ['A = ' + sf3(A), 'k = ' + sf3(k),
             m(('*', _numnode(A), ('exp', ('*', _numnode(k), ('v', 't')))))]
    h = _halflife(k)
    if h is not None:
        lines.append(('half-life = ' if k < 0 else 'doubling time = ') + sf3(h))
    lines.append(w('k = ln(N2/N1) / (t2 - t1)'))
    lines.append(w('A = N1 / e^(k t1)'))
    return lines


def t_expeval(A, k, t):
    v = A * math.exp(k * float(t))
    lines = ['N = ' + sf3(v), 'N = A e^(kt)']
    h = _halflife(k)
    if h is not None:
        lines.append(('half-life = ' if k < 0 else 'doubling time = ') + sf3(h))
    lines.append(w('kt = ' + sf3(k * t) + ', e^(kt) = ' +
                   sf3(math.exp(k * float(t)))))
    lines.append(w('dN/dt = kN = ' + sf3(k * v)))
    return lines


def t_compound_int(P, r, n):
    if n < 0:
        raise ValueError('n must not be negative')
    f = 1.0 + r / 100.0
    if f <= 0:
        raise ValueError('r must be more than -100')
    A = P * math.pow(f, float(n))
    cont = P * math.exp(r / 100.0 * float(n))
    return ['A = ' + fmt(A, 6), 'interest = ' + fmt(A - P, 6),
            'continuous = ' + fmt(cont, 6),
            w('A = P(1 + r/100)^n, multiplier ' + fmt(f, 6)),
            w('continuous: A = P e^(rn/100)')]


SECTIONS = [
    ('A', 'Proof', [
        ('Counterexample f>0', 'f(n),lo,hi', t_cex_pos),
        ('Counterexample prime', 'f(n),lo,hi', t_cex_prime),
        ('Counterexample d|f(n)', 'f(n),d,lo,hi', t_cex_div),
        ('Counterexample f=g', 'f(n),g(n),lo,hi', t_cex_eq),
    ]),
    ('B', 'Algebra and functions', [
        ('Index a^(p/q)', 'a,p,q', t_index),
        ('Simplify sqrt(n)', 'n', t_surd),
        ('Simplify surd expr', 'f(x)', t_surdexpr),
        ('Rationalise', 'a,b,c,d,e,f', t_rationalise),
        ('Quadratic', 'a(k),b(k),c(k)', t_quadratic),
        ('Quadratic in f(x)', 'a,b,c,f(x)', t_quad_in),
        ('Simultaneous 2 linear', 'a1,b1,c1,a2,b2,c2', t_simul2),
        ('Simultaneous non-linear', 'f(x,y),g(x,y)', t_simulnl),
        ('Line meets quadratic', 'm,c,a,b,k', t_linquad),
        ('Solve f(x)=g(x)', 'f(x),g(x),lo?,hi?', t_meet),
        ('Linear inequality', 'a,b', t_lin_ineq),
        ('Quadratic inequality', 'a,b,c', t_quad_ineq),
        ('Inequality f(x) > g(x)', 'f(x),g(x),lo?,hi?', t_ineq),
        ('Discriminant in k', 'a(k),b(k),c(k)', t_disck),
        ('Expand', 'f(x)', t_expand),
        ('Factorise', 'f(x)', t_factorise),
        ('Divide p(x) by d(x)', 'p(x),d(x)', t_pdiv),
        ('Factor theorem', 'p(x),a', t_factor_thm),
        ('Simplify f(x)/g(x)', 'f(x),g(x)', t_ratsimp),
        ('Partial fractions', 'f(x),g(x)', t_partial),
        ('Composite fg and gf', 'f(x),g(x),x?', t_comp),
        ('Inverse function', 'f(x),a?,b?', t_inverse),
        ('Domain of f(x)', 'f(x)', t_domain),
        ('Range of f on [a,b]', 'f(x),a,b', t_frange),
        ('Transform af(bx+c)+d', 'f(x),a,b,c,d', t_transform),
        ('Solve |ax+b|=cx+d', 'a,b,c,d', t_modeq),
        ('Proportion y=kx^n', 'n,x,y', t_prop),
        ('Plot f(x)', 'f(x),xlo?,xhi?', t_plot),
    ]),
    ('C', 'Coordinate geometry', [
        ('Line through 2 points', 'x1,y1,x2,y2', t_line2),
        ('Perpendicular bisect', 'x1,y1,x2,y2', t_perpbis),
        ('Parallel through pt', 'm,x1,y1', t_parallel),
        ('Perpendicular thru pt', 'm,x1,y1', t_perpthru),
        ('Intersect y=mx+c', 'm1,c1,m2,c2', t_lineint),
        ('Triangle 3 vertices', 'x1,y1,x2,y2,x3,y3', t_tri3),
        ('Foot of perpendicular', 'a,b,c,px,py', t_footperp),
        ('Circle from general', 'D(k),E(k),F(k)', t_circle_gen),
        ('Circle centre+radius', 'a,b,r', t_circle_cr),
        ('Point and circle', 'a,b,r,px,py', t_circpt),
        ('Circle, centre on line', 'x1,y1,x2,y2,a,b,c', t_circline),
        ('Circle through 3 pts', 'x1,y1,x2,y2,x3,y3', t_circle3),
        ('Line meets circle', 'm,c,a,b,r', t_linecircle),
        ('Tangent to circle', 'a,b,px,py', t_tangent),
        ('Param to Cartesian', 'x(t),y(t)', t_param_cart),
        ('Param point at t', 'x(t),y(t),t', t_param_pt),
        ('Plot parametric', 'x(t),y(t),tlo,thi', t_param_plot),
    ]),
    ('D', 'Sequences and series', [
        ('Arithmetic a,d,n', 'a,d,n', t_arith),
        ('Geometric a,r,n', 'a,r,n', t_geo),
        ('AP sum, first and last', 'n,first,last', t_apfl),
        ('AP: n for Sn > k', 'a,d,k', t_ap_n),
        ('GP: n for Sn > k', 'a,r,k', t_gp_n),
        ('AP from 2 terms', 'p,up,q,uq', t_ap2),
        ('AP from term and sum', 'p,up,q,Sq', t_apsum),
        ('GP from 2 terms', 'p,up,q,uq', t_gp2),
        ('Binomial (a+bx)^n', 'a,b,n', t_binom_int),
        ('Binomial rational n', 'a,b,n', t_binom_rat),
        ('Sigma sum f(r) a..b', 'f(r),a,b', t_sigma),
        ('Recurrence u(n+1)', 'f(u),u1,n', t_recur),
        ('Recurrence sum to N', 'f(u),u1,N', t_recsum),
        ('Terms of u(n)', 'u(n),n1,count', t_uterm),
        ('nCr and nPr', 'n,r', t_ncrnpr),
    ]),
    ('E', 'Trigonometry', [
        ('Exact trig at x deg', 'x', t_exact_deg),
        ('Triangle SSS', 'a,b,c', t_sss),
        ('Triangle SAS', 'b,c,A', t_sas),
        ('Triangle ASA', 'A,B,a', t_asa),
        ('Triangle SSA', 'a,b,A', t_ssa),
        ('Area (1/2)ab sinC', 'a,b,C', t_tri_area),
        ('Arc and sector (rad)', 'r,th', t_arc_rad),
        ('Arc and sector (deg)', 'r,th', t_arc_deg),
        ('Degrees to radians', 'x', t_d2r),
        ('Radians to degrees', 'x', t_r2d),
        ('Solve trig eqn (deg)', 'f(x),lo,hi', t_trigeq_deg),
        ('Solve trig eqn (rad)', 'f(x),lo,hi', t_trigeq_rad),
        ('Quad in sin x (deg)', 'a,b,c,lo,hi', t_quadsin),
        ('Quad in cos x (deg)', 'a,b,c,lo,hi', t_quadcos),
        ('Quad in tan x (deg)', 'a,b,c,lo,hi', t_quadtan),
        ('R form a sin + b cos', 'a,b', t_rform),
        ('Small angle (rad)', 'x', t_small),
        ('Compound angle (deg)', 'A,B', t_compound),
        ('Double angle (deg)', 'A', t_double),
        ('sec cosec cot (deg)', 'x', t_recip),
        ('arcsin arccos arctan', 'v', t_arcs),
        ('Exact ratios from one', 'sin,cos,tan,quadrant', t_ratios),
        ('Identity check (rad)', 'f(x),g(x),a?,b?', t_identity),
    ]),
    ('F', 'Exponentials and logs', [
        ('Solve a^x = b', 'a,b', t_ax_b),
        ('Solve log_a x = c', 'a,c', t_logsolve),
        ('log base a of x', 'a,x', t_logb),
        ('Evaluate log expr', 'f(x)', t_logeval),
        ('y = a x^n from 2 pts', 'x1,y1,x2,y2', t_powerlaw),
        ('y = k b^x from 2 pts', 'x1,y1,x2,y2', t_expolaw),
        ('Log-log fit y=ax^n', 'data*', t_loglog),
        ('Log-lin fit y=kb^x', 'data*', t_loglin),
        ('N = A e^(kt) 2 pts', 't1,N1,t2,N2,t?,N?', t_expmodel),
        ('Evaluate A e^(kt)', 'A,k,t', t_expeval),
        ('Compound interest', 'P,r,n', t_compound_int),
    ]),
]
