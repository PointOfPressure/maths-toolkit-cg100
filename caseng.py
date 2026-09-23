import math

UFUNCS = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot',
          'ln', 'log', 'exp', 'sqrt', 'asin', 'acos', 'atan',
          'sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth',
          'asinh', 'acosh', 'atanh', 'abs', 'arg', 'conj', 're', 'im')
BFUNCS = ('ncr', 'npr', 'logb')

PI = 3.141592653589793
E = 2.718281828459045
ANS = 0.0

# ---- bounded-search constants (every loop below states its cap) -----------
MAXDEN = 1000      # decimal -> exact fraction only up to this denominator
MAXCF = 40         # continued-fraction steps for that conversion
MAXPOWER = 256     # integer exponents folded exactly
MAXTRIAL = 1000    # trial division cap when extracting n-th roots
MAXLOGPOW = 64     # ln(a)/ln(b): search b^j only to this j
MAXFACTGAP = 8     # n!/(n-k)! expanded only for k up to this
MAXNCR = 8         # nCr(n,k) expanded symbolically only for k up to this

# ---- complex helpers (the device has complex but no cmath) ----------------

def _cx(v):
    return isinstance(v, complex)

def _neg(v):
    return not _cx(v) and v < 0

def _cabs(z):
    return math.sqrt(z.real * z.real + z.imag * z.imag)

def _carg(z):
    return math.atan2(z.imag, z.real)

def _csqrt(z):
    r = _cabs(z)
    re = math.sqrt((r + z.real) / 2.0)
    im = math.sqrt((r - z.real) / 2.0)
    if z.imag < 0:
        im = -im
    return complex(re, im)

def _cexp(z):
    m = math.exp(z.real)
    return complex(m * math.cos(z.imag), m * math.sin(z.imag))

def _cln(z):
    if z == 0:
        raise ValueError("ln 0")
    return complex(math.log(_cabs(z)), _carg(z))

def _sh(x):
    return (math.exp(x) - math.exp(-x)) / 2.0

def _ch(x):
    return (math.exp(x) + math.exp(-x)) / 2.0

def _csin(z):
    return complex(math.sin(z.real) * _ch(z.imag), math.cos(z.real) * _sh(z.imag))

def _ccos(z):
    return complex(math.cos(z.real) * _ch(z.imag), -math.sin(z.real) * _sh(z.imag))

def _cpow(b, e):
    if not _cx(e) and float(e) == int(e) and -64 <= e <= 64:
        n = int(e)
        if n < 0:
            if b == 0:
                raise ValueError("0 to a negative power")
            b = 1 / b
            n = -n
        r = 1
        while n:
            if n & 1:
                r = r * b
            b = b * b
            n >>= 1
        return r
    if b == 0:
        return 0.0
    return _cexp(e * _cln(complex(b)))

def cstr(z, f=None):
    if f is None:
        f = _numstr
    re = z.real
    im = z.imag
    if im == 0:
        return f(re)
    if im == 1:
        ims = 'i'
    elif im == -1:
        ims = '-i'
    else:
        ims = _imstr(f(im))
    if re == 0:
        return ims
    if ims[0] == '-':
        return f(re) + '-' + ims[1:]
    return f(re) + '+' + ims

def _imstr(s):
    # '5/2' -> '5i/2' so the i never looks like part of the denominator
    cut = s.find('/')
    if cut < 0:
        return s + 'i'
    num = s[:cut]
    if num == '1' or num == '-1':
        num = num[:-1]
    return num + 'i' + s[cut:]

# ---- integers and exact rationals -----------------------------------------

def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def _rq(p, q):
    if q < 0:
        p = -p
        q = -q
    g = gcd(p, q)
    if g > 1:
        p = p // g
        q = q // g
    return (p, q)

def _radd(a, b):
    return _rq(a[0] * b[1] + b[0] * a[1], a[1] * b[1])

def _rmul(a, b):
    return _rq(a[0] * b[0], a[1] * b[1])

def _rneg(a):
    return (-a[0], a[1])

def _fltrat(v):
    # float -> exact (p, q) with q <= MAXDEN, else None.  Continued fractions,
    # at most MAXCF steps.
    if v != v:
        return None
    av = v if v >= 0 else -v
    if av > 1e15:
        return None
    if v == int(v):
        return (int(v), 1)
    tol = 1e-11 * (av if av > 1.0 else 1.0)
    x = v
    hp = 1
    kp = 0
    h = int(math.floor(x))
    k = 1
    i = 0
    while i < MAXCF:
        if k > MAXDEN:
            return None
        if abs(h / float(k) - v) <= tol:
            return _rq(h, k)
        fr = x - math.floor(x)
        if fr <= 0.0:
            return None
        x = 1.0 / fr
        a = int(math.floor(x))
        hp, h = h, a * h + hp
        kp, k = k, a * k + kp
        i += 1
    return None

def _ratval(n):
    # exact rational value of a canonical numeric node, else None
    t = n[0]
    if t == 'n':
        v = n[1]
        if isinstance(v, bool):
            return None
        if isinstance(v, int):
            return (v, 1)
        if isinstance(v, float):
            return _fltrat(v)
        return None
    if t == 'neg':
        r = _ratval(n[1])
        return None if r is None else (-r[0], r[1])
    if t == '/':
        a = _ratval(n[1])
        b = _ratval(n[2])
        if a is None or b is None or b[0] == 0:
            return None
        return _rq(a[0] * b[1], a[1] * b[0])
    if t == '*':
        a = _ratval(n[1])
        b = _ratval(n[2])
        if a is None or b is None:
            return None
        return _rmul(a, b)
    return None

def _ratnode(r):
    if r[1] == 1:
        return ('n', r[0])
    return ('/', ('n', r[0]), ('n', r[1]))

def _numnode(v):
    if isinstance(v, complex):
        if v.imag == 0:
            return _numnode(v.real)
        return ('n', v)
    if isinstance(v, int):
        return ('n', v)
    if isinstance(v, float):
        r = _fltrat(v)
        if r is not None:
            return _ratnode(r)
    return ('n', v)

def _sqrt_split(v):
    a = 1
    b = v
    d = 2
    while d * d <= b and d <= MAXTRIAL:
        while b % (d * d) == 0:
            b //= d * d
            a *= d
        d += 1 if d == 2 else 2
    return (a, b)

def _rootsplit(m, q):
    # m = out**q * inside, inside q-th-power free.  Trial division to MAXTRIAL.
    out = 1
    inside = m
    d = 2
    while d <= MAXTRIAL and d ** q <= inside:
        dq = d ** q
        while inside % dq == 0:
            inside //= dq
            out *= d
        d += 1 if d == 2 else 2
    return (out, inside)

def _introot(m, q):
    # exact integer q-th root of m, else None
    if m < 0:
        return None
    if m < 2:
        return m
    lo = 1
    hi = 2
    while hi ** q <= m and hi < 1 << 24:
        hi *= 2
    i = 0
    while lo < hi and i < 64:
        mid = (lo + hi + 1) // 2
        if mid ** q <= m:
            lo = mid
        else:
            hi = mid - 1
        i += 1
    return lo if lo ** q == m else None

def _factorial(k):
    if k < 0:
        raise ValueError("factorial of negative")
    if k > 2000:
        raise ValueError("factorial too large")
    r = 1
    i = 2
    while i <= k:
        r *= i
        i += 1
    return r

def _ncr(n, k):
    if n < 0 or k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    if k > 2000:
        raise ValueError("nCr too large")
    num = 1
    den = 1
    i = 1
    while i <= k:
        num *= (n - k + i)
        den *= i
        i += 1
    return num // den

def _npr(n, k):
    if n < 0 or k < 0 or k > n:
        return 0
    if k > 2000:
        raise ValueError("nPr too large")
    r = 1
    i = 0
    while i < k:
        r *= (n - i)
        i += 1
    return r

def _isnum(v):
    if isinstance(v, complex):
        return False
    if not isinstance(v, (int, float)):
        return False
    if isinstance(v, float):
        if v != v:
            return False
        av = v if v >= 0 else -v
        if av > 1.7e308:
            return False
    return True

def exactstr(v, tol=1e-12):
    # float -> 'p/q', 'sqrt(b)', '2sqrt(3)/5', 'pi', '2pi/3'; None if nothing close
    if v == 0:
        return '0'
    neg = v < 0
    av = -v if neg else v
    if av >= 1e6 or av < 1e-6:
        return None
    sgn = '-' if neg else ''
    t = tol * (av if av > 1 else 1.0)
    q = 1
    while q <= 64:
        p = int(round(av * q))
        if p and abs(p - av * q) < t * q:
            return sgn + (str(p) if q == 1 else str(p) + '/' + str(q))
        q += 1
    r = av / PI
    tr = tol * (r if r > 1 else 1.0)
    q = 1
    while q <= 12:
        p = int(round(r * q))
        if p and abs(p - r * q) < tr * q:
            num = 'pi' if p == 1 else str(p) + 'pi'
            return sgn + num + ('' if q == 1 else '/' + str(q))
        q += 1
    sq = av * av
    ts = tol * (sq if sq > 1 else 1.0) * 4
    q = 1
    while q <= 16:
        p = int(round(sq * q))
        if p and abs(p - sq * q) < ts * q:
            a, b = _sqrt_split(p * q)
            if b != 1:
                g = gcd(a, q)
                a //= g
                qq = q // g
                num = ('' if a == 1 else str(a)) + 'sqrt(' + str(b) + ')'
                return sgn + num + ('' if qq == 1 else '/' + str(qq))
        q += 1
    return None

# ==========================================================================
#  canonical simplifier
# ==========================================================================

def simplify(node):
    return _s(node)

def _flatadd(n, sgn, out):
    stack = [(n, sgn)]
    while stack:
        x, s = stack.pop()
        t = x[0]
        if t == '+':
            stack.append((x[2], s))
            stack.append((x[1], s))
        elif t == '-':
            stack.append((x[2], -s))
            stack.append((x[1], s))
        elif t == 'neg':
            stack.append((x[1], -s))
        else:
            out.append((x, s))

def _flatmul(n, sgn, out):
    stack = [(n, sgn)]
    while stack:
        x, s = stack.pop()
        t = x[0]
        if t == '*':
            stack.append((x[2], s))
            stack.append((x[1], s))
        elif t == '/':
            stack.append((x[2], -s))
            stack.append((x[1], s))
        elif t == 'neg':
            out.append((('n', -1), 1))
            stack.append((x[1], s))
        else:
            out.append((x, s))

PIMAXP = 64        # k*pi recognised from a float only for |k| up to this ...
PIMAXQ = 24        # ... and denominator up to this

def _pifrac(v):
    r = _fltrat(v / PI)
    if r is None or r[1] > PIMAXQ or abs(r[0]) > PIMAXP:
        return None
    av = v if v >= 0 else -v
    if abs(r[0] * PI / r[1] - v) > 1e-11 * (av if av > 1.0 else 1.0):
        return None
    return r

def _sconst(v):
    # a literal in the tree: keep exactness, and keep pi symbolic
    if isinstance(v, float):
        r = _fltrat(v)
        if r is not None:
            return _ratnode(r)
        r = _pifrac(v)
        if r is not None:
            return _mulf([(_ratnode(r), 1), (('v', 'pi'), 1)])
        return ('n', v)
    return _numnode(v)

def _s(n):
    t = n[0]
    if t == 'n':
        return _sconst(n[1])
    if t == 'v':
        return n
    if t == 'neg':
        return _mulf([(('n', -1), 1), (_s(n[1]), 1)])
    if t == '+' or t == '-':
        raw = []
        _flatadd(n, 1, raw)
        return _addf([(_s(x), sg) for x, sg in raw])
    if t == '*' or t == '/':
        raw = []
        _flatmul(n, 1, raw)
        return _mulf([(_s(x), sg) for x, sg in raw])
    if t == '^':
        return _pow(_s(n[1]), _s(n[2]))
    if t == 'fact':
        return _sfact(_s(n[1]))
    if t in BFUNCS:
        return _sbin(t, _s(n[1]), _s(n[2]))
    if t in UFUNCS:
        return _sfn(t, _s(n[1]))
    return n

def _add(nodes):
    return _addf([(x, 1) for x in nodes])

def _mul(nodes):
    return _mulf([(x, 1) for x in nodes])

def _negx(e):
    r = _ratval(e)
    if r is not None:
        return _ratnode((-r[0], r[1]))
    if e[0] == 'neg':
        return e[1]
    return _mulf([(('n', -1), 1), (e, 1)])

_RECIPOF = {'sec': 'cos', 'cosec': 'sin', 'cot': 'tan',
            'sech': 'cosh', 'cosech': 'sinh', 'coth': 'tanh'}

def _baseexp(n):
    t = n[0]
    if t == '^':
        b = n[1]
        e = n[2]
    elif t == 'sqrt':
        b = n[1]
        e = ('/', ('n', 1), ('n', 2))
    elif t == 'exp':
        return (('v', 'e'), n[1])
    else:
        b = n
        e = ('n', 1)
    inv = _RECIPOF.get(b[0])
    if inv is not None:
        return ((inv, b[1]), _negx(e))
    return (b, e)

def _numpow(m, r):
    # integer base m to the exact rational power r.
    # -> (rational coefficient, complex unit or None, radicand, leftover factor)
    p, q = r
    if m == 0:
        return ((0, 1), None, 1, None) if p > 0 else None
    if q == 1:
        if p >= 0:
            if p > MAXPOWER and m != 1 and m != -1:
                return None
            return ((m ** p, 1), None, 1, None)
        if -p > MAXPOWER and m != 1 and m != -1:
            return None
        return (_rq(1, m ** (-p)), None, 1, None)
    cxf = None
    sgn = 1
    if m < 0:
        if q == 2:
            cxf = _cpow(1j, p)
            m = -m
        elif q % 2:
            if p % 2:
                sgn = -1
            m = -m
        else:
            return None
    a = p // q
    b = p - a * q
    if a > MAXPOWER or -a > MAXPOWER:
        return None
    if a > 0:
        co = (m ** a, 1)
    elif a < 0:
        co = _rq(1, m ** (-a))
    else:
        co = (1, 1)
    if sgn < 0:
        co = (-co[0], co[1])
    if b == 0:
        return (co, cxf, 1, None)
    if q == 2:
        return (co, cxf, m, None)
    outp, inside = _rootsplit(m, q)
    if outp != 1:
        co = _rmul(co, (outp ** b, 1))
    if inside == 1:
        return (co, cxf, 1, None)
    return (co, cxf, 1, [('n', inside), _ratnode((b, q))])

def _termparts(items):
    coef = (1, 1)
    fl = None
    cxc = None
    facs = {}
    order = []
    raw = []
    for node, s in items:
        _flatmul(node, s, raw)
    for node, s in raw:
        if node[0] == 'n' and isinstance(node[1], complex):
            v = node[1]
            if s > 0:
                cxc = v if cxc is None else cxc * v
            elif v != 0:
                cxc = (1.0 / v) if cxc is None else cxc / v
            continue
        r = _ratval(node)
        if r is not None:
            if s > 0:
                coef = _rmul(coef, r)
                continue
            if r[0] != 0:
                coef = _rmul(coef, (r[1], r[0]))
                continue
            b = ('n', 0)
            e = ('n', -1)
        elif node[0] == 'n':
            v = node[1]
            if s > 0:
                fl = v if fl is None else fl * v
            elif v != 0:
                fl = (1.0 / v) if fl is None else fl / v
            continue
        else:
            b, e = _baseexp(node)
            if s < 0:
                e = _negx(e)
        k = tostr(b)
        if k in facs:
            facs[k][1].append(e)
        else:
            facs[k] = [b, [e]]
            order.append(k)
    out = []
    rad = 1
    for k in order:
        b, elist = facs[k]
        e = elist[0] if len(elist) == 1 else _add(elist)
        r = _ratval(e)
        if r is not None and r[0] == 0:
            continue
        if b[0] == 'n' and isinstance(b[1], int) and r is not None:
            res = _numpow(b[1], r)
            if res is not None:
                coef = _rmul(coef, res[0])
                if res[1] is not None:
                    cxc = res[1] if cxc is None else cxc * res[1]
                rad *= res[2]
                if res[3] is not None:
                    out.append(res[3])
                continue
        out.append([b, e])
    if rad != 1:
        a, b2 = _sqrt_split(rad)
        if a != 1:
            coef = _rmul(coef, (a, 1))
        if b2 != 1:
            out.append([('sqrt', ('n', b2)), ('n', 1)])
    return (coef, fl, cxc, out)

# ---- multiplicative identity passes --------------------------------------

def _findbase(out, name, arg):
    i = 0
    while i < len(out):
        b = out[i][0]
        if b[0] == name and b[1] == arg:
            return i
        i += 1
    return -1

def _pairs(coef, out):
    # sin/cos -> tan, sinh/cosh -> tanh, ln a / ln b, n!/(n-k)!, 2 sin cos
    for a, b, res in (('sin', 'cos', 'tan'), ('sinh', 'cosh', 'tanh')):
        i = 0
        while i < len(out):
            base = out[i][0]
            if base[0] != a:
                i += 1
                continue
            ea = _ratval(out[i][1])
            j = _findbase(out, b, base[1])
            if ea is None or j < 0:
                i += 1
                continue
            eb = _ratval(out[j][1])
            if eb is None or _radd(ea, eb) != (0, 1):
                i += 1
                continue
            out[i] = [(res, base[1]), _ratnode(ea)]
            out.pop(j)
            i += 1
    coef = _lnpair(coef, out)
    coef, out = _factpair(coef, out)
    coef, out = _doubleangle(coef, out)
    return (coef, out)

def _lnpair(coef, out):
    i = 0
    while i < len(out):
        bi = out[i][0]
        if bi[0] != 'ln' or bi[1][0] != 'n' or _ratval(out[i][1]) != (1, 1):
            i += 1
            continue
        j = 0
        hit = -1
        while j < len(out):
            bj = out[j][0]
            if j != i and bj[0] == 'ln' and bj[1][0] == 'n' and _ratval(out[j][1]) == (-1, 1):
                hit = j
                break
            j += 1
        if hit < 0:
            i += 1
            continue
        m = bi[1][1]
        k = out[hit][0][1][1]
        j2 = _logpow(m, k)
        if j2 is None:
            i += 1
            continue
        coef = _rmul(coef, (j2, 1))
        if hit > i:
            out.pop(hit)
            out.pop(i)
        else:
            out.pop(i)
            out.pop(hit)
    return coef

def _logpow(m, k):
    # j with k**j == m, |j| <= MAXLOGPOW, else None
    if not isinstance(m, int) or not isinstance(k, int):
        return None
    if k <= 1 or m <= 0:
        return None
    v = 1
    j = 0
    while j <= MAXLOGPOW:
        if v == m:
            return j
        v *= k
        if v > m:
            return None
        j += 1
    return None

def _intdiff(a, b):
    d = _addf([(a, 1), (b, -1)])
    r = _ratval(d)
    if r is None or r[1] != 1:
        return None
    return r[0]

def _factpair(coef, out):
    i = 0
    while i < len(out):
        bi = out[i][0]
        if bi[0] != 'fact' or _ratval(out[i][1]) != (1, 1):
            i += 1
            continue
        j = 0
        hit = -1
        while j < len(out):
            bj = out[j][0]
            if j != i and bj[0] == 'fact' and _ratval(out[j][1]) == (-1, 1):
                hit = j
                break
            j += 1
        if hit < 0:
            i += 1
            continue
        d = _intdiff(bi[1], out[hit][0][1])
        if d is None or d <= 0 or d > MAXFACTGAP:
            i += 1
            continue
        low = out[hit][0][1]
        if hit > i:
            out.pop(hit)
            out.pop(i)
        else:
            out.pop(i)
            out.pop(hit)
        t = 1
        while t <= d:
            out.append([_addf([(low, 1), (('n', t), 1)]), ('n', 1)])
            t += 1
        i = 0
    return (coef, out)

def _doubleangle(coef, out):
    if not FOLD[0] or coef[0] % 2 or len(out) != 2:
        return (coef, out)
    i = _findbase(out, 'sin', out[0][0][1] if out[0][0][0] == 'sin' else
                  (out[1][0][1] if out[1][0][0] == 'sin' else None))
    if i < 0:
        return (coef, out)
    u = out[i][0][1]
    j = _findbase(out, 'cos', u)
    if j < 0 or _ratval(out[i][1]) != (1, 1) or _ratval(out[j][1]) != (1, 1):
        return (coef, out)
    return (_rq(coef[0] // 2, coef[1]),
            [[('sin', _mulf([(('n', 2), 1), (u, 1)])), ('n', 1)]])

# ---- building a canonical term -------------------------------------------

_RECIP = {'cos': 'sec', 'sin': 'cosec', 'tan': 'cot',
          'cosh': 'sech', 'sinh': 'cosech', 'tanh': 'coth'}

def _powform(b, p, q):
    if q == 1:
        return b if p == 1 else ('^', b, ('n', p))
    if q == 2:
        k = p // 2
        if p - 2 * k == 0:
            return b if k == 1 else ('^', b, ('n', k))
        rt = ('sqrt', b)
        if k == 0:
            return rt
        return ('*', b if k == 1 else ('^', b, ('n', k)), rt)
    return ('^', b, ('/', ('n', p), ('n', q)))

def _chain(items):
    node = None
    for f in items:
        node = f if node is None else ('*', node, f)
    return node

def _negify(n):
    if n[0] == 'n':
        return ('n', -n[1])
    if n[0] == '*' and n[1][0] == 'n' and not isinstance(n[1][1], complex):
        return ('*', ('n', -n[1][1]), n[2])
    return ('neg', n)

def _termnode(coef, fl, cxc, out):
    num = []
    den = []
    for b, e in out:
        r = _ratval(e)
        if r is None:
            num.append(('exp', e) if b == ('v', 'e') else ('^', b, e))
            continue
        p, q = r
        if p < 0:
            flip = _RECIP.get(b[0])
            if flip is not None:
                num.append(_powform((flip, b[1]), -p, q))
            else:
                den.append(_powform(b, -p, q))
        else:
            num.append(_powform(b, p, q))
    num.sort(key=tostr)
    den.sort(key=tostr)
    numnode = _chain(num)
    dennode = _chain(den)
    if cxc is not None or fl is not None:
        v = float(coef[0]) / coef[1]
        if fl is not None:
            v = v * fl
        if cxc is not None:
            v = v * cxc
            if isinstance(v, complex) and v.imag == 0:
                v = v.real
        cn = _numnode(v)
        if numnode is None:
            numnode = cn
        elif cn != ('n', 1):
            numnode = ('*', cn, numnode)
        if dennode is None:
            return numnode
        return ('/', numnode, dennode)
    p, q = coef
    if p == 0:
        return ('/', ('n', 0), dennode) if dennode is not None else ('n', 0)
    ap = -p if p < 0 else p
    if numnode is None:
        numnode = ('n', ap)
    elif ap != 1:
        numnode = ('*', ('n', ap), numnode)
    if p < 0:
        if (q != 1 or den) and len(num) == 1 \
                and (num[0][0] == '+' or num[0][0] == '-') and ap == 1:
            numnode = _negnode(numnode)
        else:
            numnode = _negify(numnode)
    if q != 1:
        dennode = ('n', q) if dennode is None else ('*', ('n', q), dennode)
    if dennode is None:
        return numnode
    return ('/', numnode, dennode)

MAXSURD = 64       # terms allowed when multiplying surd brackets out
MAXSURDPOW = 6     # (a+sqrt b)^k expanded only to this k
MAXRATPASS = 3     # rationalising passes over one product

def _hassqrt(n):
    t = n[0]
    if t == 'sqrt':
        return True
    if t == '^':
        r = _ratval(n[2])
        return r is not None and r[1] != 1
    if t == 'n' or t == 'v':
        return False
    if len(n) == 2:
        return _hassqrt(n[1])
    if len(n) == 3:
        return _hassqrt(n[1]) or _hassqrt(n[2])
    return False

def _constsurd(b):
    return (b[0] == '+' or b[0] == '-') and not vars_in(b) and _hassqrt(b)

def _surdconj(b):
    raw = []
    _flatadd(b, 1, raw)
    rat = []
    surd = []
    for node, s in raw:
        if _hassqrt(node):
            surd.append((node, -s))
        else:
            rat.append((node, s))
    if not surd or not rat or len(surd) > 1:
        return None
    c = _addf(rat + surd)
    if _isneg(c):
        return _negnode(c)
    return c

def _surdexp(nodes):
    terms = [(('n', 1), 1)]
    for f in nodes:
        raw = []
        _flatadd(f, 1, raw)
        nxt = []
        for a, sa in terms:
            for b, sb in raw:
                nxt.append((_mulf([(a, 1), (b, 1)]), sa * sb))
        if len(nxt) > MAXSURD:
            return None
        terms = nxt
    return _addf(terms)

def _surdmerge(out):
    ix = []
    i = 0
    while i < len(out):
        r = _ratval(out[i][1])
        if r is not None and r[1] == 2 and (r[0] == 1 or r[0] == -1) \
                and out[i][0][0] != 'n':
            ix.append(i)
        i += 1
    if len(ix) < 2:
        return out
    items = []
    for i in ix:
        r = _ratval(out[i][1])
        items.append((out[i][0], 1 if r[0] > 0 else -1))
    inner = _mulf(items)
    rest = []
    i = 0
    while i < len(out):
        if i not in ix:
            rest.append(out[i])
        i += 1
    rest.append([inner, ('/', ('n', 1), ('n', 2))])
    return rest

def _surdwork(coef, fl, cxc, out):
    hit = False
    guard = 0
    while guard < MAXRATPASS:
        guard += 1
        again = False
        i = 0
        while i < len(out):
            b, e = out[i]
            r = _ratval(e)
            if r is not None and r[1] == 1 and r[0] < 0 and _constsurd(b):
                conj = _surdconj(b)
                d = None if conj is None else _surdexp([b, conj])
                rd = None if d is None else _ratval(d)
                if rd is not None and rd[0] != 0:
                    k = -r[0]
                    out[i] = [conj, ('n', k)]
                    coef = _rmul(coef, _rq(rd[1] ** k, rd[0] ** k))
                    hit = True
                    again = True
                    break
            i += 1
        if not again:
            break
    nodes = []
    rest = []
    for b, e in out:
        r = _ratval(e)
        if r is not None and r[1] == 1 and 0 < r[0] <= MAXSURDPOW and _constsurd(b):
            j = 0
            while j < r[0]:
                nodes.append(b)
                j += 1
        else:
            rest.append([b, e])
    if len(nodes) >= 2:
        s = _surdexp(nodes)
        if s is not None:
            return _mulf([(_termnode(coef, fl, cxc, rest), 1), (s, 1)])
    if len(nodes) == 1 and not rest and fl is None and cxc is None \
            and coef[1] == 1 and coef != (1, 1):
        raw = []
        _flatadd(nodes[0], 1, raw)
        return _addf([(_mulf([(('n', coef[0]), 1), (tn, 1)]), sg) for tn, sg in raw])
    if hit:
        return _termnode(coef, fl, cxc, out)
    return None

def _content(b):
    # rational gcd of the term coefficients of a sum
    raw = []
    _flatadd(b, 1, raw)
    gn = 0
    gd = 1
    for t, s in raw:
        c, fl, cxc, out = _termparts([(t, 1)])
        if fl is not None or cxc is not None:
            return (1, 1)
        gn = gcd(gn, c[0])
        gd = gd // gcd(gd, c[1]) * c[1]
    if gn == 0:
        return (1, 1)
    return _rq(gn, gd)

def _contentpull(coef, out):
    if coef[1] == 1:
        return (coef, out)
    i = 0
    while i < len(out):
        b, e = out[i]
        if (b[0] == '+' or b[0] == '-') and _ratval(e) == (1, 1):
            c = _content(b)
            k = gcd(c[0], coef[1])
            if k > 1:
                raw = []
                _flatadd(b, 1, raw)
                out[i] = [_addf([(_mulf([(('n', k), -1), (t, 1)]), s)
                                 for t, s in raw]), e]
                coef = _rmul(coef, (k, 1))
                return (coef, out)
        i += 1
    return (coef, out)

def _mulf(items):
    coef, fl, cxc, out = _termparts(items)
    coef, out = _pairs(coef, out)
    coef, out = _contentpull(coef, out)
    out = _surdmerge(out)
    sw = _surdwork(coef, fl, cxc, out)
    if sw is not None:
        return sw
    node = _termnode(coef, fl, cxc, out)
    if node[0] == '/':
        r = _ratfix(node)
        if r is not None:
            return r
    return node

# ---- sums -----------------------------------------------------------------

def _basedeg(b):
    t = b[0]
    if t == 'n':
        return 0.0
    if t == 'v':
        return 0.0 if (b[1] == 'pi' or b[1] == 'e') else 1.0
    if t == '+' or t == '-':
        d1 = _basedeg(b[1])
        d2 = _basedeg(b[2])
        return d1 if d1 > d2 else d2
    if t == 'neg':
        return _basedeg(b[1])
    if t == '*':
        return _basedeg(b[1]) + _basedeg(b[2])
    if t == '/':
        return _basedeg(b[1]) - _basedeg(b[2])
    if t == '^':
        r = _ratval(b[2])
        if r is None:
            return _basedeg(b[1])
        return _basedeg(b[1]) * (float(r[0]) / r[1])
    if t == 'sqrt':
        return 0.5 * _basedeg(b[1])
    return 1.0

def _degsig(out):
    d = 0.0
    sig = []
    for b, e in out:
        r = _ratval(e)
        if r is None:
            d += 1.0
            sig.append((tostr(b), -1.0))
            continue
        ev = float(r[0]) / r[1]
        w = _basedeg(b) * ev
        if ev < 0 and b[0] in _RECIP:
            w = -w          # 1/cos prints as sec: it ranks as degree +1
        d += w
        sig.append((tostr(b), -ev))
    sig.sort()
    return (d, tuple(sig))

def _cval(coef, fl, cxc):
    v = float(coef[0]) / coef[1]
    if fl is not None:
        v = v * fl
    if cxc is not None:
        v = v * cxc
    return v

def _centry(e1, e2):
    if e1[1] is None and e1[2] is None and e2[1] is None and e2[2] is None:
        return (_radd(e1[0], e2[0]), None, None)
    v = _cval(e1[0], e1[1], e1[2]) + _cval(e2[0], e2[1], e2[2])
    if isinstance(v, complex):
        if v.imag == 0:
            v = v.real
        else:
            return ((1, 1), None, v)
    return ((1, 1), v, None)

def _czero(e):
    if e[1] is None and e[2] is None:
        return e[0][0] == 0
    return _cval(e[0], e[1], e[2]) == 0

def _cnegative(e):
    if e[1] is None and e[2] is None:
        return e[0][0] < 0
    v = _cval(e[0], e[1], e[2])
    return (not isinstance(v, complex)) and v < 0

def _cflip(e):
    return ((-e[0][0], e[0][1]), None if e[1] is None else -e[1], e[2])

def _negnode(n):
    raw = []
    _flatadd(n, -1, raw)
    return _addf(raw)

def _addf(items):
    num = ((0, 1), None, None)
    bag = {}
    order = []
    raw0 = []
    for node, s in items:
        _flatadd(node, s, raw0)
    for node, s in raw0:
        coef, fl, cxc, out = _termparts([(node, 1)])
        if s < 0:
            coef = (-coef[0], coef[1])
        ent = (coef, fl, cxc)
        if not out:
            num = _centry(num, ent)
            continue
        rest = _termnode((1, 1), None, None, out)
        k = tostr(rest)
        if k in bag:
            bag[k][0] = _centry(bag[k][0], ent)
        else:
            bag[k] = [ent, out]
            order.append(k)
    keep = []
    ix = 0
    for k in order:
        ent, out = bag[k]
        ix += 1
        if _czero(ent):
            continue
        d, sig = _degsig(out)
        keep.append([k, ent, out, d, sig, ix])
    num, keep = _sumident(num, keep)
    keep.sort(key=lambda it: (-it[3], it[4] if it[3] > 0 else (), it[5]))
    if not _czero(num):
        keep.append(['', num, [], 0.0, (), 1 << 20])
    if not keep:
        return ('n', 0)
    node = None
    for k, ent, out, d, sig, ix in keep:
        if node is None:
            node = _termnode(ent[0], ent[1], ent[2], out)
        elif _cnegative(ent):
            f = _cflip(ent)
            node = ('-', node, _termnode(f[0], f[1], f[2], out))
        else:
            node = ('+', node, _termnode(ent[0], ent[1], ent[2], out))
    if node[0] == '+' or node[0] == '-':
        r = _ratfix(node)
        if r is not None:
            return r
    return node

def _sq(out, name):
    # entry factor list is exactly one squared trig/hyperbolic term -> its arg
    if len(out) != 1:
        return None
    b, e = out[0]
    if b[0] == name and _ratval(e) == (2, 1):
        return b[1]
    return None

def _findsq(keep, name, arg):
    i = 0
    while i < len(keep):
        u = _sq(keep[i][2], name)
        if u is not None and u == arg:
            return i
        i += 1
    return -1

FOLD = [True]      # expand() turns the double-angle folds off while it works

def _sumident(num, keep):
    # cosh^2-sinh^2 = 1, cos^2-sin^2 = cos 2u, sin^2+cos^2 = 1, 1+tan^2 = sec^2
    if not FOLD[0]:
        return (num, keep)
    i = 0
    while i < len(keep):
        u = _sq(keep[i][2], 'cosh')
        if u is None:
            i += 1
            continue
        j = _findsq(keep, 'sinh', u)
        if j < 0 or keep[j][1] != _cflip(keep[i][1]):
            i += 1
            continue
        num = _centry(num, keep[i][1])
        keep.pop(j if j > i else i)
        keep.pop(i if j > i else j)
        i = 0
    i = 0
    while i < len(keep):
        u = _sq(keep[i][2], 'cos')
        if u is None:
            i += 1
            continue
        j = _findsq(keep, 'sin', u)
        if j < 0:
            i += 1
            continue
        if keep[j][1] == _cflip(keep[i][1]):
            ent = keep[i][1]
            out = [[('cos', _mulf([(('n', 2), 1), (u, 1)])), ('n', 1)]]
            keep.pop(j if j > i else i)
            keep.pop(i if j > i else j)
            d, sig = _degsig(out)
            keep.append([tostr(_termnode((1, 1), None, None, out)), ent, out, d, sig,
                         1 << 19])
            i = 0
            continue
        if keep[j][1] == keep[i][1]:
            num = _centry(num, keep[i][1])
            keep.pop(j if j > i else i)
            keep.pop(i if j > i else j)
            i = 0
            continue
        i += 1
    for nm, res in (('tan', 'sec'), ('sinh', 'cosh')):
        i = 0
        while i < len(keep):
            u = _sq(keep[i][2], nm)
            if u is None or num != keep[i][1] or _czero(num):
                i += 1
                continue
            ent = keep[i][1]
            out = [[(res, u), ('n', 2)]]
            keep.pop(i)
            num = ((0, 1), None, None)
            d, sig = _degsig(out)
            keep.append([tostr(_termnode((1, 1), None, None, out)), ent, out, d, sig,
                         1 << 19])
            i = 0
    i = 0
    while i < len(keep):
        u = _sq(keep[i][2], '_none')
        if u is None:
            i += 1
            continue
        if num != keep[i][1] or _czero(num):
            i += 1
            continue
        ent = keep[i][1]
        out = [[('sec', u), ('n', 2)]]
        keep.pop(i)
        num = ((0, 1), None, None)
        d, sig = _degsig(out)
        keep.append([tostr(_termnode((1, 1), None, None, out)), ent, out, d, sig,
                     1 << 19])
        i = 0
    return (num, keep)

# ---- rational-function normalisation --------------------------------------

def _hasden(n):
    t = n[0]
    if t == 'n' or t == 'v':
        return False
    if t == '/':
        return len(vars_in(n[2])) > 0 or _hasden(n[1])
    if len(n) == 2:
        return _hasden(n[1])
    if len(n) == 3:
        return _hasden(n[1]) or _hasden(n[2])
    return False

def _ratfix(node):
    if not _hasden(node):
        return None
    vs = vars_in(node)
    if len(vs) != 1:
        return None
    if node[0] == '/' and _basedeg(node[1]) < 1.0:
        return None
    import caspoly
    if node[0] == '+' or node[0] == '-':
        try:
            if not caspoly.ratshare(node, vs[0]):
                return None
        except Exception:
            return None
    try:
        r = caspoly.ratnorm(node, vs[0])
    except Exception:
        return None
    if r is None or r == node:
        return None
    return r

# ---- powers ---------------------------------------------------------------

def _pow(a, b):
    rb = _ratval(b)
    if rb is not None:
        if rb == (0, 1):
            return ('n', 1)
        if rb == (1, 1):
            return a
    if a == ('v', 'e'):
        return _sfn('exp', b)
    if a[0] == 'exp':
        return _sfn('exp', _mulf([(a[1], 1), (b, 1)]))
    ra = _ratval(a)
    if ra is not None and rb is not None:
        r = _ratpow(ra, rb)
        if r is not None:
            return r
        return ('^', _ratnode(ra), _ratnode(rb))
    if a[0] == 'n' and not _cx(a[1]) and rb is not None and rb[1] == 1 \
            and -MAXPOWER <= rb[0] <= MAXPOWER:
        try:
            return _numnode(float(a[1]) ** rb[0])
        except Exception:
            return ('^', a, b)
    if a[0] == 'n' and isinstance(a[1], complex) and rb is not None and rb[1] == 1:
        try:
            return _numnode(_cpow(a[1], rb[0]))
        except Exception:
            return ('^', a, b)
    if rb is not None and rb[1] == 2 and a[0] == '^':
        re = _ratval(a[2])
        if re is not None and re[1] == 1 and re[0] % 2 == 0:
            return _pow(_sfn('abs', a[1]), _ratnode(_rmul((re[0], 1), rb)))
    if rb is not None and rb[1] == 1:
        if a[0] == '*' or a[0] == '/' or a[0] == 'neg':
            raw = []
            _flatmul(a, 1, raw)
            return _mulf([(_pow(x, b) if sg > 0 else _pow(x, _negx(b)), 1)
                          for x, sg in raw])
        if a[0] == 'abs' and rb[0] % 2 == 0:
            return _pow(a[1], b)
    ba, ea = _baseexp(a)
    if ba != a:
        if rb is not None and rb[1] == 1:
            return _mulf([(('^', ba, _mulf([(ea, 1), (b, 1)])), 1)])
        re = _ratval(ea)
        if re is not None and re[1] == 1 and re[0] % 2 and rb is not None:
            return _mulf([(('^', ba, _mulf([(ea, 1), (b, 1)])), 1)])
    if rb is not None:
        if rb[1] == 1 and 1 < rb[0] <= MAXSURDPOW and _constsurd(a):
            s = _surdexp([a] * rb[0])
            if s is not None:
                return s
        return _termnode((1, 1), None, None, [[a, b]])
    return ('^', a, b)

def _ratpow(ra, rb):
    r1 = _numpow(ra[0], rb)
    r2 = _numpow(ra[1], (-rb[0], rb[1]))
    if r1 is None or r2 is None:
        return None
    coef = _rmul(r1[0], r2[0])
    cxc = None
    for rr in (r1, r2):
        if rr[1] is not None:
            cxc = rr[1] if cxc is None else cxc * rr[1]
    rad = r1[2] * r2[2]
    out = []
    for rr in (r1, r2):
        if rr[3] is not None:
            out.append(rr[3])
    if rad != 1:
        a, b2 = _sqrt_split(rad)
        if a != 1:
            coef = _rmul(coef, (a, 1))
        if b2 != 1:
            out.append([('sqrt', ('n', b2)), ('n', 1)])
    return _termnode(coef, None, cxc, out)

# ---- exact trigonometry ---------------------------------------------------

_SIN12 = {0: ('n', 0), 2: ('/', ('n', 1), ('n', 2)),
          3: ('/', ('sqrt', ('n', 2)), ('n', 2)),
          4: ('/', ('sqrt', ('n', 3)), ('n', 2)), 6: ('n', 1)}
_TAN12 = {0: ('n', 0), 2: ('/', ('sqrt', ('n', 3)), ('n', 3)),
          3: ('n', 1), 4: ('sqrt', ('n', 3))}

def _exact_trig(t, k):
    # k is the exact rational multiple of pi
    if (12 * k[0]) % k[1]:
        return None
    n = (12 * k[0]) // k[1]
    if t == 'tan':
        n %= 12
        neg = n > 6
        if neg:
            n = 12 - n
        v = _TAN12.get(n)
    else:
        if t == 'cos':
            n += 6
        n %= 24
        neg = n >= 12
        if neg:
            n -= 12
        if n > 6:
            n = 12 - n
        v = _SIN12.get(n)
    if v is None:
        return None
    if neg and v != ('n', 0):
        return _mulf([(('n', -1), 1), (v, 1)])
    return v

def _pimult(node):
    coef, fl, cxc, out = _termparts([(node, 1)])
    if fl is not None or cxc is not None:
        return None
    if not out:
        return (0, 1) if coef == (0, 1) else None
    if len(out) != 1:
        return None
    if out[0][0] != ('v', 'pi') or _ratval(out[0][1]) != (1, 1):
        return None
    return coef

def _piparts(a):
    raw = []
    _flatadd(a, 1, raw)
    k = (0, 1)
    rest = []
    for node, s in raw:
        r = _pimult(node)
        if r is not None:
            k = _radd(k, r if s > 0 else (-r[0], r[1]))
        else:
            rest.append((node, s))
    if not rest:
        return (k, None)
    return (k, _addf(rest))

def _rmod(k, per):
    n = k[0] * per[1]
    d = k[1] * per[0]
    w = n // d
    return _radd(k, (-w * per[0], per[1]))

_SHIFT = {(0, 1): {'sin': ('sin', 1), 'cos': ('cos', 1), 'tan': ('tan', 1)},
          (1, 2): {'sin': ('cos', 1), 'cos': ('sin', -1), 'tan': ('cot', -1)},
          (1, 1): {'sin': ('sin', -1), 'cos': ('cos', -1), 'tan': ('tan', 1)},
          (3, 2): {'sin': ('cos', -1), 'cos': ('sin', 1), 'tan': ('cot', -1)}}

_ODD = ('sin', 'tan', 'cot', 'cosec', 'sinh', 'tanh', 'coth', 'cosech',
        'asin', 'atan', 'asinh', 'atanh')

def _isneg(n):
    t = n[0]
    if t == 'n':
        v = n[1]
        return (not isinstance(v, complex)) and v < 0
    if t == 'neg':
        return True
    if t == '*' or t == '/':
        return _isneg(n[1])
    if t == '+' or t == '-':
        return _isneg(n[1])
    return False

def _trigfn(t, a):
    k, rest = _piparts(a)
    if rest is None:
        ex = _exact_trig(t, k)
        if ex is not None:
            return ex
        return (t, a)
    per = (1, 1) if t == 'tan' else (2, 1)
    kk = _rmod(k, per)
    row = _SHIFT.get(kk)
    sign = 1
    if row is not None:
        t2, sign = row[t]
        arg = rest
    else:
        t2 = t
        arg = _addf([(rest, 1), (_mulf([(_ratnode(kk), 1), (('v', 'pi'), 1)]), 1)])
    if _isneg(arg):
        arg = _negnode(arg)
        if t2 in _ODD:
            sign = -sign
    node = (t2, arg)
    if sign < 0:
        return _mulf([(('n', -1), 1), (node, 1)])
    return node

_ASIN = {'0': (0, 1), '1/2': (1, 6), 'sqrt(2)/2': (1, 4),
         'sqrt(3)/2': (1, 3), '1': (1, 2)}
_ATAN = {'0': (0, 1), 'sqrt(3)/3': (1, 6), '1': (1, 4), 'sqrt(3)': (1, 3)}

def _invtrig(t, a):
    s = tostr(a)
    neg = s[0] == '-'
    if neg:
        s = s[1:]
    tbl = _ATAN if t == 'atan' else _ASIN
    k = tbl.get(s)
    if k is None:
        return None
    if t == 'acos':
        k = _radd((1, 2), (-k[0], k[1]) if not neg else k)
        return _mulf([(_ratnode(k), 1), (('v', 'pi'), 1)])
    if neg:
        k = (-k[0], k[1])
    return _mulf([(_ratnode(k), 1), (('v', 'pi'), 1)])

# ---- unary function rules -------------------------------------------------

def _sfn(t, a):
    if t == 'sin' or t == 'cos' or t == 'tan':
        return _trigfn(t, a)
    if t in _RECIP.values():
        for k in _RECIP:
            if _RECIP[k] == t:
                inner = _sfn(k, a)
                break
        return _mulf([(inner, -1)])
    if t == 'exp':
        return _sexp(a)
    if t == 'ln':
        return _sln(a)
    if t == 'log':
        return _slog(a)
    if t == 'sqrt':
        return _pow(a, ('/', ('n', 1), ('n', 2)))
    if t == 'abs':
        return _sabs(a)
    ra = _ratval(a)
    if t == 'asin' or t == 'acos' or t == 'atan':
        r = _invtrig(t, a)
        if r is not None:
            return r
        if t != 'acos' and _isneg(a):
            return _mulf([(('n', -1), 1), ((t, _negnode(a)), 1)])
        return (t, a)
    if t == 'sinh' or t == 'tanh':
        if ra == (0, 1):
            return ('n', 0)
        if _isneg(a):
            return _mulf([(('n', -1), 1), ((t, _negnode(a)), 1)])
        return (t, a)
    if t == 'cosh':
        if ra == (0, 1):
            return ('n', 1)
        if _isneg(a):
            return ('cosh', _negnode(a))
        return (t, a)
    if t == 'asinh' or t == 'atanh':
        if ra == (0, 1):
            return ('n', 0)
        if _isneg(a):
            return _mulf([(('n', -1), 1), ((t, _negnode(a)), 1)])
        return (t, a)
    if t == 'acosh' and ra == (1, 1):
        return ('n', 0)
    if a[0] == 'n':
        v = a[1]
        if t == 'arg':
            r = _argexact(v)
            if r is not None:
                return r
        if t == 'conj':
            return _numnode(complex(v.real, -v.imag) if _cx(v) else v)
        if t == 're':
            return _numnode(v.real if _cx(v) else v)
        if t == 'im':
            return _numnode(v.imag if _cx(v) else 0)
    return (t, a)

def _argexact(v):
    if not _cx(v):
        if v == 0:
            return None
        return ('n', 0) if v > 0 else ('v', 'pi')
    re = _fltrat(v.real)
    im = _fltrat(v.imag)
    if re is None or im is None:
        return None
    ang = math.atan2(v.imag, v.real) / PI
    r = _fltrat(ang)
    if r is None or r[1] > 12:
        return None
    return _mulf([(_ratnode(r), 1), (('v', 'pi'), 1)])

def _sexp(a):
    r = _ratval(a)
    if r == (0, 1):
        return ('n', 1)
    if a[0] == 'ln':
        return a[1]
    coef, fl, cxc, out = _termparts([(a, 1)])
    if len(out) == 1 and out[0][0][0] == 'ln' and _ratval(out[0][1]) == (1, 1) \
            and fl is None and cxc is None:
        return _pow(out[0][0][1], _ratnode(coef))
    if cxc is not None and fl is None and cxc.real == 0 and len(out) == 1 \
            and out[0][0] == ('v', 'pi') and _ratval(out[0][1]) == (1, 1):
        im = _fltrat(cxc.imag)
        if im is not None:
            th = _rmul(coef, im)
            c = _exact_trig('cos', th)
            s = _exact_trig('sin', th)
            if c is not None and s is not None:
                return _addf([(c, 1), (_mulf([(('n', 1j), 1), (s, 1)]), 1)])
    return ('exp', a)

def _sln(a):
    r = _ratval(a)
    if r == (1, 1):
        return ('n', 0)
    if a == ('v', 'e'):
        return ('n', 1)
    if a[0] == 'exp':
        return a[1]
    if a[0] == 'sqrt':
        return _mulf([(_sln(a[1]), 1), (('n', 2), -1)])
    if r is not None and r[0] > 0 and r[1] != 1 and r[0] == 1:
        return _mulf([(('n', -1), 1), (('ln', ('n', r[1])), 1)])
    return ('ln', a)

def _slog(a):
    r = _ratval(a)
    if r is not None and r[1] == 1 and r[0] > 0:
        j = _logpow(r[0], 10)
        if j is not None:
            return ('n', j)
    if r == (1, 1):
        return ('n', 0)
    return ('log', a)

def _sabs(a):
    r = _ratval(a)
    if r is not None:
        return _ratnode((-r[0], r[1]) if r[0] < 0 else r)
    if a[0] == 'n':
        v = a[1]
        if _cx(v):
            re = _fltrat(v.real)
            im = _fltrat(v.imag)
            if re is not None and im is not None:
                sq = _radd(_rmul(re, re), _rmul(im, im))
                return _pow(_ratnode(sq), ('/', ('n', 1), ('n', 2)))
        return _numnode(abs(v))
    if a[0] == 'abs':
        return a
    if a[0] == 'neg':
        return _sabs(a[1])
    coef, fl, cxc, out = _termparts([(a, 1)])
    if cxc is None and out:
        pos = True
        for b, e in out:
            re = _ratval(e)
            if re is not None and re[1] == 1 and re[0] % 2 == 0:
                continue
            if b[0] in ('abs', 'exp', 'cosh'):
                continue
            pos = False
            break
        if pos and (fl is None or fl > 0) and coef[0] > 0:
            return a
        if coef[0] < 0 or (fl is not None and fl < 0):
            inner = _termnode((abs(coef[0]), coef[1]),
                              None if fl is None else abs(fl), None, out)
            return _sabs(inner) if not pos else inner
        if len(out) == 1 and coef == (1, 1) and fl is None:
            return ('abs', a)
        rest = _termnode((1, 1), None, None, out)
        if coef != (1, 1) or fl is not None:
            return _mulf([(_termnode(coef, fl, None, []), 1), (('abs', rest), 1)])
    return ('abs', a)

def _sfact(a):
    r = _ratval(a)
    if r is not None and r[1] == 1 and 0 <= r[0] <= 170:
        return ('n', _factorial(r[0]))
    return ('fact', a)

def _sbin(t, a, b):
    ra = _ratval(a)
    rb = _ratval(b)
    if ra is not None and rb is not None and ra[1] == 1 and rb[1] == 1:
        try:
            if t == 'ncr':
                return ('n', _ncr(ra[0], rb[0]))
            if t == 'npr':
                return ('n', _npr(ra[0], rb[0]))
        except Exception:
            pass
    if t == 'logb':
        if ra is not None and rb is not None and ra[1] == 1 and rb[1] == 1:
            j = _logpow(rb[0], ra[0])
            if j is not None:
                return ('n', j)
            try:
                return ('n', math.log(rb[0]) / math.log(ra[0]))
            except Exception:
                pass
        return ('logb', a, b)
    if rb is not None and rb[1] == 1 and 0 <= rb[0] <= MAXNCR:
        k = rb[0]
        items = []
        i = 0
        while i < k:
            items.append((_addf([(a, 1), (('n', -i), 1)]), 1))
            i += 1
        if t == 'ncr':
            items.append((('n', _factorial(k)), -1))
        if not items:
            return ('n', 1)
        return _mulf(items)
    return (t, a, b)

# ==========================================================================
#  differentiation
# ==========================================================================

def diff(node, var='x'):
    return _d(node, var)

def _d(n, var):
    t = n[0]
    if t == 'n':
        return ('n', 0)
    if t == 'v':
        return ('n', 1) if n[1] == var else ('n', 0)
    if t == '+':
        return ('+', _d(n[1], var), _d(n[2], var))
    if t == '-':
        return ('-', _d(n[1], var), _d(n[2], var))
    if t == 'neg':
        return ('neg', _d(n[1], var))
    if t == '*':
        a = n[1]; b = n[2]
        return ('+', ('*', _d(a, var), b), ('*', a, _d(b, var)))
    if t == '/':
        a = n[1]; b = n[2]
        return ('/', ('-', ('*', _d(a, var), b), ('*', a, _d(b, var))), ('^', b, ('n', 2)))
    if t == '^':
        a = n[1]; b = n[2]
        if a == ('v', 'e'):
            return ('*', ('exp', b), _d(b, var))
        if b[0] == 'n':
            return ('*', ('*', b, ('^', a, ('n', b[1] - 1))), _d(a, var))
        if not _hasvar(b, var):
            return ('*', ('*', b, ('^', a, ('-', b, ('n', 1)))), _d(a, var))
        if not _hasvar(a, var):
            return ('*', ('*', ('^', a, b), ('ln', a)), _d(b, var))
        return ('*', ('^', a, b), ('+', ('*', _d(b, var), ('ln', a)), ('/', ('*', b, _d(a, var)), a)))
    if t == 'sin':
        return ('*', ('cos', n[1]), _d(n[1], var))
    if t == 'cos':
        return ('neg', ('*', ('sin', n[1]), _d(n[1], var)))
    if t == 'tan':
        return ('*', ('^', ('sec', n[1]), ('n', 2)), _d(n[1], var))
    if t == 'sec':
        return ('*', ('*', ('sec', n[1]), ('tan', n[1])), _d(n[1], var))
    if t == 'cosec':
        return ('neg', ('*', ('*', ('cosec', n[1]), ('cot', n[1])), _d(n[1], var)))
    if t == 'cot':
        return ('neg', ('*', ('^', ('cosec', n[1]), ('n', 2)), _d(n[1], var)))
    if t == 'sech':
        return ('neg', ('*', ('*', ('sech', n[1]), ('tanh', n[1])), _d(n[1], var)))
    if t == 'cosech':
        return ('neg', ('*', ('*', ('cosech', n[1]), ('coth', n[1])), _d(n[1], var)))
    if t == 'coth':
        return ('neg', ('*', ('^', ('cosech', n[1]), ('n', 2)), _d(n[1], var)))
    if t == 'exp':
        return ('*', ('exp', n[1]), _d(n[1], var))
    if t == 'ln':
        return ('/', _d(n[1], var), n[1])
    if t == 'log':
        return ('/', _d(n[1], var), ('*', n[1], ('ln', ('n', 10))))
    if t == 'sqrt':
        return ('/', _d(n[1], var), ('*', ('n', 2), ('sqrt', n[1])))
    if t == 'asin':
        return ('/', _d(n[1], var), ('sqrt', ('-', ('n', 1), ('^', n[1], ('n', 2)))))
    if t == 'acos':
        return ('neg', ('/', _d(n[1], var), ('sqrt', ('-', ('n', 1), ('^', n[1], ('n', 2))))))
    if t == 'atan':
        return ('/', _d(n[1], var), ('+', ('n', 1), ('^', n[1], ('n', 2))))
    if t == 'sinh':
        return ('*', ('cosh', n[1]), _d(n[1], var))
    if t == 'cosh':
        return ('*', ('sinh', n[1]), _d(n[1], var))
    if t == 'tanh':
        return ('*', ('^', ('sech', n[1]), ('n', 2)), _d(n[1], var))
    if t == 'asinh':
        return ('/', _d(n[1], var), ('sqrt', ('+', ('^', n[1], ('n', 2)), ('n', 1))))
    if t == 'acosh':
        return ('/', _d(n[1], var), ('sqrt', ('-', ('^', n[1], ('n', 2)), ('n', 1))))
    if t == 'atanh':
        return ('/', _d(n[1], var), ('-', ('n', 1), ('^', n[1], ('n', 2))))
    if t == 'abs':
        return ('*', ('/', n[1], ('abs', n[1])), _d(n[1], var))
    if t == 'logb':
        return ('/', _d(n[2], var), ('*', n[2], ('ln', n[1])))
    if t in ('fact', 'ncr', 'npr', 'arg', 'conj', 're', 'im'):
        if _hasvar(n, var):
            raise ValueError("cannot differentiate " + t)
        return ('n', 0)
    return ('n', 0)

# ==========================================================================
#  tree utilities
# ==========================================================================

def subst(n, var, repl):
    t = n[0]
    if t == 'v':
        return repl if n[1] == var else n
    if t == 'n':
        return n
    if len(n) == 2:
        return (t, subst(n[1], var, repl))
    if len(n) == 3:
        return (t, subst(n[1], var, repl), subst(n[2], var, repl))
    return n

def subst_tree(n, target, repl):
    if n == target:
        return repl
    t = n[0]
    if t == 'n' or t == 'v':
        return n
    if len(n) == 2:
        return (t, subst_tree(n[1], target, repl))
    if len(n) == 3:
        return (t, subst_tree(n[1], target, repl), subst_tree(n[2], target, repl))
    return n

def strip_abs(n):
    t = n[0]
    if t == 'abs':
        return strip_abs(n[1])
    if t == 'n' or t == 'v':
        return n
    if len(n) == 2:
        return (t, strip_abs(n[1]))
    if len(n) == 3:
        return (t, strip_abs(n[1]), strip_abs(n[2]))
    return n

def count_var(n, var):
    t = n[0]
    if t == 'n':
        return 0
    if t == 'v':
        return 1 if n[1] == var else 0
    if len(n) == 2:
        return count_var(n[1], var)
    if len(n) == 3:
        return count_var(n[1], var) + count_var(n[2], var)
    return 0

def vars_in(n, out=None):
    if out is None:
        out = []
    t = n[0]
    if t == 'v':
        if n[1] not in out and n[1] != 'pi' and n[1] != 'e':
            out.append(n[1])
        return out
    if t == 'n':
        return out
    if len(n) >= 2:
        vars_in(n[1], out)
    if len(n) >= 3:
        vars_in(n[2], out)
    return out

def _hasvar(n, var):
    t = n[0]
    if t == 'n':
        return False
    if t == 'v':
        return n[1] == var
    if len(n) == 2:
        return _hasvar(n[1], var)
    return _hasvar(n[1], var) or _hasvar(n[2], var)

_INVFN = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan', 'asin': 'sin',
          'acos': 'cos', 'atan': 'tan', 'exp': 'ln', 'ln': 'exp',
          'sinh': 'asinh', 'cosh': 'acosh', 'tanh': 'atanh',
          'asinh': 'sinh', 'acosh': 'cosh', 'atanh': 'tanh'}

def invert(f, var='x', yname='y'):
    if count_var(f, var) != 1:
        return None
    lhs = f
    rhs = ('v', yname)
    guard = 0
    while guard < 40:
        guard += 1
        t = lhs[0]
        if t == 'v':
            return simplify(rhs) if lhs[1] == var else None
        if t == 'neg':
            lhs = lhs[1]
            rhs = ('neg', rhs)
            continue
        if t in _INVFN:
            rhs = (_INVFN[t], rhs)
            lhs = lhs[1]
            continue
        if t == 'sqrt':
            rhs = ('^', rhs, ('n', 2))
            lhs = lhs[1]
            continue
        if t == 'log':
            rhs = ('^', ('n', 10), rhs)
            lhs = lhs[1]
            continue
        if t == 'abs':
            return None
        if t in ('+', '-', '*', '/', '^'):
            a = lhs[1]
            b = lhs[2]
            ax = _hasvar(a, var)
            if ax and _hasvar(b, var):
                return None
            if ax:
                if t == '+':
                    rhs = ('-', rhs, b)
                elif t == '-':
                    rhs = ('+', rhs, b)
                elif t == '*':
                    rhs = ('/', rhs, b)
                elif t == '/':
                    rhs = ('*', rhs, b)
                else:
                    if b[0] != 'n':
                        return None
                    e = b[1]
                    if e == 0:
                        return None
                    rhs = ('^', rhs, ('/', ('n', 1), ('n', e)))
                lhs = a
                continue
            if t == '+':
                rhs = ('-', rhs, a)
            elif t == '-':
                rhs = ('-', a, rhs)
            elif t == '*':
                rhs = ('/', rhs, a)
            elif t == '/':
                rhs = ('/', a, rhs)
            else:
                rhs = ('/', ('ln', rhs), ('ln', a))
            lhs = b
            continue
        return None
    return None

# ==========================================================================
#  numeric evaluation
# ==========================================================================

def _torad(a, deg):
    return a * PI / 180.0 if deg else a

def _fromrad(a, deg):
    return a * 180.0 / PI if deg else a

def evalf(n, x, deg=False, env=None):
    t = n[0]
    if t == 'n':
        return n[1]
    if t == 'v':
        if env is not None and n[1] in env:
            return env[n[1]]
        if n[1] == 'x':
            return x
        if n[1] == 'pi':
            return PI
        if n[1] == 'e':
            return E
        if n[1] == 'ans':
            return ANS
        raise ValueError("unknown variable " + n[1])
    if t == 'neg':
        return -evalf(n[1], x, deg, env)
    if t == '+':
        return evalf(n[1], x, deg, env) + evalf(n[2], x, deg, env)
    if t == '-':
        return evalf(n[1], x, deg, env) - evalf(n[2], x, deg, env)
    if t == '*':
        return evalf(n[1], x, deg, env) * evalf(n[2], x, deg, env)
    if t == '/':
        return evalf(n[1], x, deg, env) / evalf(n[2], x, deg, env)
    if t == '^':
        base = evalf(n[1], x, deg, env)
        expo = evalf(n[2], x, deg, env)
        if _cx(base) or _cx(expo):
            return _cpow(base, expo)
        if base < 0 and float(expo) != int(expo):
            return _cpow(complex(base), expo)
        if isinstance(base, int) and isinstance(expo, int) and expo > 64 \
                and base not in (0, 1, -1):
            # an exact bigint power (x^x at x=1e6) takes seconds; floats overflow cleanly
            return float(base) ** expo
        return base ** expo
    if t == 'fact':
        return _factorial(int(round(evalf(n[1], x, deg, env))))
    if t == 'ncr':
        return _ncr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'npr':
        return _npr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'logb':
        return math.log(evalf(n[2], x, deg, env)) / math.log(evalf(n[1], x, deg, env))
    a = evalf(n[1], x, deg, env)
    if t == 'arg':
        return _carg(a) if _cx(a) else (0.0 if a >= 0 else PI)
    if t == 'conj':
        return complex(a.real, -a.imag) if _cx(a) else a
    if t == 're':
        return a.real if _cx(a) else a
    if t == 'im':
        return a.imag if _cx(a) else 0
    if _cx(a):
        if t == 'sqrt':
            return _csqrt(a)
        if t == 'exp':
            return _cexp(a)
        if t == 'ln':
            return _cln(a)
        if t == 'abs':
            return _cabs(a)
        if t == 'sin':
            return _csin(a)
        if t == 'cos':
            return _ccos(a)
        if t == 'tan':
            return _csin(a) / _ccos(a)
        if t == 'sinh':
            return (_cexp(a) - _cexp(-a)) / 2
        if t == 'cosh':
            return (_cexp(a) + _cexp(-a)) / 2
        raise ValueError(t + " of a complex number")
    if t == 'sin':
        return math.sin(_torad(a, deg))
    if t == 'cos':
        return math.cos(_torad(a, deg))
    if t == 'tan':
        return math.tan(_torad(a, deg))
    if t == 'sec':
        c = math.cos(_torad(a, deg))
        if -1e-12 < c < 1e-12:
            raise ValueError("sec undefined here")
        return 1.0 / c
    if t == 'cosec':
        s = math.sin(_torad(a, deg))
        if -1e-12 < s < 1e-12:
            raise ValueError("cosec undefined here")
        return 1.0 / s
    if t == 'cot':
        r = _torad(a, deg)
        s = math.sin(r)
        if -1e-12 < s < 1e-12:
            raise ValueError("cot undefined here")
        return math.cos(r) / s
    if t == 'asin':
        return _fromrad(math.asin(a), deg)
    if t == 'acos':
        return _fromrad(math.acos(a), deg)
    if t == 'atan':
        return _fromrad(math.atan(a), deg)
    if t == 'exp':
        return math.exp(a)
    if t == 'ln':
        return math.log(a)
    if t == 'log':
        return math.log(a) / math.log(10)
    if t == 'sqrt':
        if a < 0:
            return complex(0, math.sqrt(-a))
        return math.sqrt(a)
    if t == 'abs':
        return abs(a)
    if t == 'sinh':
        return (math.exp(a) - math.exp(-a)) / 2.0
    if t == 'cosh':
        return (math.exp(a) + math.exp(-a)) / 2.0
    if t == 'tanh':
        if a > 350.0:
            return 1.0
        if a < -350.0:
            return -1.0
        e2 = math.exp(2.0 * a)
        return (e2 - 1.0) / (e2 + 1.0)
    if t == 'sech':
        return 2.0 / (math.exp(a) + math.exp(-a))
    if t == 'cosech':
        d = math.exp(a) - math.exp(-a)
        if -1e-12 < d < 1e-12:
            raise ValueError("cosech undefined at 0")
        return 2.0 / d
    if t == 'coth':
        d = math.exp(a) - math.exp(-a)
        if -1e-12 < d < 1e-12:
            raise ValueError("coth undefined at 0")
        return (math.exp(a) + math.exp(-a)) / d
    if t == 'asinh':
        sgn = -1.0 if a < 0 else 1.0
        aa = a if a >= 0 else -a
        return sgn * math.log(aa + math.sqrt(aa * aa + 1.0))
    if t == 'acosh':
        return math.log(a + math.sqrt(a * a - 1.0))
    if t == 'atanh':
        return 0.5 * math.log((1.0 + a) / (1.0 - a))
    return 0.0

# ==========================================================================
#  printing
# ==========================================================================

OPPREC = {'+': 1, '-': 1, '*': 2, '/': 2, 'neg': 3, '^': 4}

def _numstr(v):
    if isinstance(v, int):
        return str(v)
    if _cx(v):
        return cstr(v)
    if not _isnum(v):
        if v != v:
            return "undefined"
        return "inf" if v > 0 else "-inf"
    ex = exactstr(v)
    if ex is not None:
        return ex
    r = round(v, 6)
    if r == int(r):
        return str(int(r))
    return str(r)

def tostr(n):
    return _str(n, 0, False)

def _str(n, parent, right):
    t = n[0]
    if t == 'n':
        s = _numstr(n[1])
        if (right or parent >= 3) and not (s.replace('.', '').isdigit() or s == 'pi'):
            return "(" + s + ")"
        return s
    if t == 'v':
        return n[1]
    if t == 'exp':
        return "e^(" + _str(n[1], 0, False) + ")"
    if t == 'abs':
        return "|" + _str(n[1], 0, False) + "|"
    if t in UFUNCS:
        return t + "(" + _str(n[1], 0, False) + ")"
    if t == 'neg':
        s = "-" + _str(n[1], 2, False)
        return "(" + s + ")" if parent > 3 else s
    if t == 'fact':
        return _str(n[1], 5, False) + "!"
    if t in BFUNCS:
        nm = 'nCr' if t == 'ncr' else ('nPr' if t == 'npr' else 'logb')
        return nm + "(" + _str(n[1], 0, False) + "," + _str(n[2], 0, False) + ")"
    p = OPPREC[t]
    if p < parent:
        right = False       # about to be wrapped in brackets: no "+ -" risk
    if t == '^':
        ls = _str(n[1], p + 1, False)
        rs = _str(n[2], p, True)
    elif t == '-' or t == '/':
        ls = _str(n[1], p, right)
        rs = _str(n[2], p + 1, True)
    else:
        ls = _str(n[1], p, right)
        rs = _str(n[2], p, True)
    s = ls + t + rs
    return "(" + s + ")" if p < parent else s
