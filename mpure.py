# AQA 7357 sections A-F: proof, algebra and functions, coordinate geometry,
# sequences and series, trigonometry, exponentials and logarithms.
import math
import caslex
import caseng
import cascalc
import caspoly
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


def _roots(tree, lo, hi, deg=False, var='x', n=600):
    step = (hi - lo) / float(n)
    ys = []
    i = 0
    while i <= n:
        ys.append(_val(tree, lo + step * i, deg, var))
        i += 1
    out = []
    i = 1
    while i <= n and len(out) < 24:
        y = ys[i]
        p = ys[i - 1]
        if y is not None and p is not None:
            ay = y if y >= 0 else -y
            ap = p if p >= 0 else -p
            sc = ap if ap > ay else ay
            if (p <= 0 and y >= 0) or (p >= 0 and y <= 0):
                r = _bis(tree, lo + step * (i - 1), lo + step * i, deg, var)
                if _ok_root(tree, r, sc, deg, var):
                    cascalc._add(out, r)
            elif i + 1 <= n and ys[i + 1] is not None and \
                    (y < 0) == (p < 0) and (y < 0) == (ys[i + 1] < 0):
                an = ys[i + 1] if ys[i + 1] >= 0 else -ys[i + 1]
                if ay < ap and ay < an:
                    r = _snap(cascalc._touch(
                        tree, lo + step * (i - 1), lo + step * (i + 1), deg,
                        var))
                    if _ok_root(tree, r, sc, deg, var):
                        cascalc._add(out, r)
        i += 1
    out.sort()
    return out


def _scan(tree, lo, hi, deg, var='x'):
    span = hi - lo
    if span <= 0:
        raise ValueError('hi must be more than lo')
    n = int(span * (2.0 if deg else 60.0))
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


def t_surdexpr(f):
    t = caseng.simplify(f)
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
        for x in xs:
            lines.append('(' + fmt(x) + ', ' + fmt(m0 * x + c0) + ')')
    lines.append(w('ax^2 + (b-m)x + (k-c) = 0'))
    lines.append(w(_quadstr(A, B, C) + ' = 0'))
    lines.append(w('disc = ' + fmt(D)))
    return lines


def t_meet(f, g):
    d = ('-', f, g)
    rs = _roots(d, -20.0, 20.0, False, 'x', 800)
    if not rs:
        return ['no crossing in -20..20',
                warn('only -20 <= x <= 20 is searched')]
    lines = []
    for r in rs[:8]:
        y = _snap(_val(f, r))
        if y is None:
            lines.append('x = ' + fmt(r))
        else:
            lines.append('(' + fmt(r) + ', ' + fmt(y) + ')')
    lines.append(w('solving f(x) - g(x) = 0'))
    lines.append(w(str(len(rs)) + ' crossing(s) in -20..20'))
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


def t_expand(f):
    t = caspoly.collect(caspoly.expand(f))
    return [m(t), w(caseng.tostr(t))]


def t_factorise(f):
    t = caspoly.factor(f)
    if t is None:
        s = caseng.simplify(f)
        return [m(s), warn('no rational factorisation found')]
    return [m(t), w(caseng.tostr(t))]


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
    v = _need(p, float(a))
    br = 'x - ' + fmt(a) if a >= 0 else 'x + ' + fmt(-a)
    lines = ['p(' + fmt(a) + ') = ' + fmt(v)]
    if v == 0:
        lines.append('(' + br + ') is a factor')
    else:
        lines.append('(' + br + ') is not a factor')
        lines.append('remainder = ' + fmt(v))
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


def t_partial(f, g):
    res = caspoly.partial(f, g, 'x')
    if res is None:
        raise ValueError('cannot split that into partial fractions')
    quot, terms = res
    node = quot
    for top, ft, i in terms:
        den = ft if i == 1 else ('^', ft, ('n', i))
        piece = ('/', top, den)
        node = piece if node is None else ('+', node, piece)
    if node is None:
        node = ('n', 0)
    lines = [m(node)]
    for top, ft, i in terms:
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


def t_inverse(f):
    inv = caseng.invert(f, 'x', 'y')
    if inv is None:
        return ['no inverse formula found',
                warn('f must use x once and be one-to-one'),
                w('f(x) = ' + caseng.tostr(caseng.simplify(f)))]
    t = caseng.simplify(caseng.subst(inv, 'y', ('v', 'x')))
    lines = [m(t), 'f-1(x) = ' + caseng.tostr(t)]
    a = _val(f, 2.0)
    if a is not None:
        b = _val(t, a)
        if b is not None:
            lines.append(w('check f(2) = ' + fmt(a) + ', f-1 of that = ' +
                           fmt(b)))
    lines.append(w('domain of f-1 = range of f'))
    return lines


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


def t_circle_gen(D, E, F):
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
    return lines


def _circstr(a, b, r2):
    xs = 'x^2' if a == 0 else ('(x - ' + fmt(a) + ')^2' if a > 0
                               else '(x + ' + fmt(-a) + ')^2')
    ys = 'y^2' if b == 0 else ('(y - ' + fmt(b) + ')^2' if b > 0
                               else '(y + ' + fmt(-b) + ')^2')
    return xs + ' + ' + ys + ' = ' + fmt(r2)


def t_circle_cr(a, b, r):
    _pos(r, 'r')
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


def t_geo(a, r, n):
    ni = _whole(n, 'n')
    if ni < 1:
        raise ValueError('n must be at least 1')
    un = a * math.pow(float(r), ni - 1)
    if r == 1:
        sn = a * ni
    else:
        sn = a * (1.0 - math.pow(float(r), ni)) / (1.0 - r)
    lines = ['u(' + str(ni) + ') = ' + fmt(un),
             'S(' + str(ni) + ') = ' + fmt(sn)]
    ar = r if r >= 0 else -r
    if ar < 1:
        lines.append('S(inf) = ' + fmt(a / (1.0 - r)))
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
    while k < 5:
        if k > 0:
            c = c * (n - k + 1) / k
        lines.append('x^' + str(k) + ': ' + fmt(an * c * math.pow(u, k)))
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


def t_sigma(f, a, b):
    lo, hi = _span(a, b, 5000)
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
    if ni < 2 or ni > 30:
        raise ValueError('n must be 2 to 30')
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
    for j in range(len(terms)):
        out.append('u(' + str(j + 1) + ') = ' + fmt(terms[j]))
    return out + _behave(terms) + lines + \
        [w('u(n+1) = ' + caseng.tostr(caseng.simplify(f)))]


def t_uterm(u, n1, count):
    a = _whole(n1, 'n1')
    c = _whole(count, 'count')
    if c < 1 or c > 30:
        raise ValueError('count must be 1 to 30')
    terms = []
    out = []
    i = 0
    while i < c:
        v = _val(u, float(a + i), False, 'n')
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


def _arc(r, th):
    arc = r * th
    area = 0.5 * r * r * th
    chord = 2.0 * r * math.sin(th / 2.0)
    seg = 0.5 * r * r * (th - math.sin(th))
    return ['arc = ' + fmt(arc), 'sector area = ' + fmt(area),
            'chord = ' + fmt(chord), 'segment area = ' + fmt(seg),
            'sector perimeter = ' + fmt(arc + 2.0 * r),
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


def _eqn_lines(f, lo, hi, deg):
    rs = _scan(f, lo, hi, deg)
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


def t_identity(f, g):
    bad = None
    tested = 0
    i = 0
    while i < 40:
        x = 0.17 + i * 0.13
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
                w(str(tested) + ' values of x in 0.17 to 5.2 rad'),
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


def t_logeval(f):
    t = caseng.simplify(f)
    lines = [m(t)]
    if not caseng.vars_in(t):
        v = casutil.ev(t)
        lines.append('= ' + fmt(v))
        lines.append('decimal = ' + sf3(v))
    lines.append(w('log xy = log x + log y, log(x/y) = log x - log y'))
    lines.append(w('log x^k = k log x'))
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
            w('gradient = ' + sf3(g))]


def _halflife(k):
    if k == 0:
        return None
    return math.log(2.0) / (k if k > 0 else -k)


def t_expmodel(t1, N1, t2, N2):
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
        ('Quadratic', 'a,b,c', t_quadratic),
        ('Quadratic in f(x)', 'a,b,c,f(x)', t_quad_in),
        ('Simultaneous 2 linear', 'a1,b1,c1,a2,b2,c2', t_simul2),
        ('Line meets quadratic', 'm,c,a,b,k', t_linquad),
        ('Solve f(x)=g(x)', 'f(x),g(x)', t_meet),
        ('Linear inequality', 'a,b', t_lin_ineq),
        ('Quadratic inequality', 'a,b,c', t_quad_ineq),
        ('Expand', 'f(x)', t_expand),
        ('Factorise', 'f(x)', t_factorise),
        ('Divide p(x) by d(x)', 'p(x),d(x)', t_pdiv),
        ('Factor theorem', 'p(x),a', t_factor_thm),
        ('Simplify f(x)/g(x)', 'f(x),g(x)', t_ratsimp),
        ('Partial fractions', 'f(x),g(x)', t_partial),
        ('Composite fg and gf', 'f(x),g(x),x?', t_comp),
        ('Inverse function', 'f(x)', t_inverse),
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
        ('Circle from general', 'D,E,F', t_circle_gen),
        ('Circle centre+radius', 'a,b,r', t_circle_cr),
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
        ('AP: n for Sn > k', 'a,d,k', t_ap_n),
        ('GP: n for Sn > k', 'a,r,k', t_gp_n),
        ('Binomial (a+bx)^n', 'a,b,n', t_binom_int),
        ('Binomial rational n', 'a,b,n', t_binom_rat),
        ('Sigma sum f(r) a..b', 'f(r),a,b', t_sigma),
        ('Recurrence u(n+1)', 'f(u),u1,n', t_recur),
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
        ('Identity check (rad)', 'f(x),g(x)', t_identity),
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
        ('N = A e^(kt) 2 pts', 't1,N1,t2,N2', t_expmodel),
        ('Evaluate A e^(kt)', 'A,k,t', t_expeval),
        ('Compound interest', 'P,r,n', t_compound_int),
    ]),
]
