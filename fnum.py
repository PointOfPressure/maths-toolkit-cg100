# OCR B (MEI) Further Maths H645, Numerical Methods (Y434): errors, solving
# equations, numerical differentiation and integration, approximating
# functions and improved estimates. Each tool takes the parsed fields and
# returns result lines. Use of technology (NQ1, Q2) needs no tool.
import math
import caseng
import cascalc
import casutil

X = ('v', 'x')
TOL = 1e-8        # default stopping tolerance for the iterations
MAXIT = 100       # iteration cap
ROWS = 24         # table rows shown before the middle is elided

_f = casutil.fmt
_w = casutil.w
_wn = casutil.warn
_m = casutil.m

# ---- shared helpers ---------------------------------------------------------

def _g(v):
    # numerical methods need more than 3 s.f.: 8 s.f. (10 at full precision)
    return _f(v, 10 if casutil.FULL else 8)

def _g7(v):
    return _f(v, 7)

def _e(v):
    # errors, differences and ratios: plain 3 s.f., never an exact form
    return _f(v, 3)

def _chk(t, name='f'):
    for v in caseng.vars_in(t):
        if v != 'x':
            raise ValueError(name + ': use x, not ' + v)
    return t

def _at(t, x):
    # real value of t at x (radians), or None
    try:
        v = caseng.evalf(t, x, False)
    except Exception:
        return None
    v = casutil.clean(v)
    if isinstance(v, complex):
        return None
    v = float(v)
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

def _fx(t, x, name='f'):
    v = _at(t, x)
    if v is None:
        raise ValueError(name + ' undefined at x = ' + _g(x))
    return v

def _deriv(t):
    try:
        return cascalc.tidy(caseng.diff(t, 'x'))
    except Exception:
        return None

def _dval(t, d, x):
    # f'(x) from the CAS derivative, else a central difference
    if d is not None:
        v = _at(d, x)
        if v is not None:
            return v
    h = 1e-5 * (1.0 + abs(x))
    p = _at(t, x + h)
    q = _at(t, x - h)
    if p is None or q is None:
        return None
    return (p - q) / (2.0 * h)

def _gd(t, x):
    # g'(x) with rounding noise near 0 snapped to 0
    v = _dval(t, _deriv(t), x)
    if v is not None and abs(v) < 1e-12:
        return 0.0
    return v

def _tol(t):
    if t is None:
        return TOL
    if t <= 0:
        raise ValueError('tol must be > 0')
    return t if t > 1e-13 else 1e-13

def _int_in(v, lo, hi, name):
    k = int(round(v))
    if k < lo or k > hi:
        raise ValueError(name + ' from ' + str(lo) + ' to ' + str(hi))
    return k

def _elide(rows):
    if len(rows) <= ROWS:
        return rows
    keep = ROWS - 5
    return (rows[:4] + [_w('  ... ' + str(len(rows) - 4 - keep) + ' rows ...')] +
            rows[len(rows) - keep:])

def _diffs(xs):
    return [xs[i] - xs[i - 1] for i in range(1, len(xs))]

def _ratio(d1, d0):
    # MEI ratio of differences d(n+1)/d(n)
    if d0 == 0:
        return None
    return d1 / d0

def _itrows(xs, tag='x'):
    # x(r), difference from x(r-1), ratio of differences
    rows = []
    d = _diffs(xs)
    i = 0
    while i < len(xs):
        s = tag + str(i) + ' = ' + _g(xs[i])
        if i >= 1:
            s += '  d = ' + _e(d[i - 1])
        if i >= 2:
            r = _ratio(d[i - 1], d[i - 2])
            if r is not None:
                s += '  r = ' + _e(r)
        rows.append(_w(s))
        i += 1
    return _elide(rows)

def _last_ratio(xs):
    # last ratio of differences whose differences are above rounding noise
    d = _diffs(xs)
    i = len(d) - 1
    while i >= 1:
        big = 1e-12 * (1.0 + abs(xs[i + 1]))
        if abs(d[i]) > big and abs(d[i - 1]) > big:
            return d[i] / d[i - 1]
        i -= 1
    return None

def _order(xs):
    # p from three successive differences: |d2/d1| = |d1/d0|^p
    d = _diffs(xs)
    i = len(d) - 1
    while i >= 2:
        big = 1e-12 * (1.0 + abs(xs[i + 1]))
        a = abs(d[i - 2])
        b = abs(d[i - 1])
        c = abs(d[i])
        if a > big and b > big and c > big and a != b:
            lo = math.log(b / a)
            if lo != 0:
                return math.log(c / b) / lo
        i -= 1
    return None

def _order_lines(xs):
    out = []
    r = _last_ratio(xs)
    if r is not None:
        out.append(_w('ratio of differences -> ' + _e(r)))
    p = _order(xs)
    if p is not None:
        out.append(_w('order of convergence ~ ' + _f(p, 3)))
    return out

# decimal rounding and chopping, done on the scaled integer so the answer
# prints exactly (no float noise such as 0.29 -> 0.28999)

def _chop_int(s):
    r = int(math.floor(s + 0.5))
    if abs(s - r) < 1e-9 * (abs(s) if abs(s) > 1.0 else 1.0):
        return r
    return int(math.floor(s)) if s >= 0 else int(math.ceil(s))

def _round_int(s):
    a = abs(s)
    fl = math.floor(a)
    fr = a - fl
    if abs(fr - 0.5) < 1e-9 * (a if a > 1.0 else 1.0):
        r = int(fl) + 1
    else:
        r = int(math.floor(a + 0.5))
    return -r if s < 0 else r

def _dpstr(n, d):
    # integer n / 10^d as a fixed decimal string (d may be negative)
    neg = n < 0
    s = str(-n if neg else n)
    if d <= 0:
        s = s + '0' * (-d) if n != 0 else '0'
    else:
        while len(s) < d + 1:
            s = '0' + s
        s = s[:len(s) - d] + '.' + s[len(s) - d:]
    return '-' + s if neg else s

def _scaled(x, p):
    s = x * (10.0 ** p)
    if abs(s) > 1e15:
        raise ValueError('too many digits for this value')
    return s

def _exp10(x):
    # e with 10^e <= |x| < 10^(e+1)
    a = abs(x)
    e = int(math.floor(math.log10(a)))
    if a >= 10.0 ** (e + 1):
        e += 1
    elif a < 10.0 ** e:
        e -= 1
    return e

def _rk(v, k):
    # v rounded to k significant figures (half away from zero)
    if v == 0:
        return 0.0
    p = k - 1 - _exp10(v)
    n = _round_int(v * (10.0 ** p))
    return n / (10.0 ** p) if p >= 0 else n * (10.0 ** (-p))

# ---- U errors ---------------------------------------------------------------
# NU1 sums/differences/products/quotients, U2 error in f(x), U3/U5 how the
# arrangement of a calculation matters (nearly equal numbers), U4 finite
# precision, U6 rounding and chopping with maximum and average errors.

def t_error(ap, ex):
    e = ap - ex
    out = ['error = ' + _e(e)]
    if ex == 0:
        out.append(_wn('exact value 0: no relative error'))
    else:
        r = e / ex
        out.append('relative error = ' + _e(r))
        out.append('percentage error = ' + _e(100.0 * r) + '%')
    out.append(_w('error = approximation - exact'))
    out.append(_w('relative error = error / exact'))
    out.append(_w('|error| = ' + _e(abs(e))))
    return out

def t_sumdiff(a, ea, b, eb):
    E = abs(ea) + abs(eb)
    out = ['a+b = ' + _g(a + b) + ' +/- ' + _e(E),
           'a-b = ' + _g(a - b) + ' +/- ' + _e(E)]
    for tag, v in (('a+b', a + b), ('a-b', a - b)):
        if v != 0:
            out.append('rel error ' + tag + ' <= ' + _e(E / abs(v)))
        else:
            out.append(_wn(tag + ' = 0: relative error unbounded'))
    out.append(_w('absolute errors add: |ea| + |eb| = ' + _e(E)))
    out.append(_w('signed: e(a+b) = ea+eb = ' + _e(ea + eb)))
    out.append(_w('signed: e(a-b) = ea-eb = ' + _e(ea - eb)))
    if E > 0 and abs(a - b) < 10.0 * E:
        out.append(_wn('a-b subtracts nearly equal numbers:'))
        out.append(_wn('large relative error, so rearrange'))
    return out

def _corners(fn, a, ea, b, eb):
    vals = []
    for p in (a - ea, a + ea):
        for q in (b - eb, b + eb):
            vals.append(fn(p, q))
    return (min(vals), max(vals))

def t_prodquot(a, ea, b, eb):
    if a == 0 or b == 0:
        raise ValueError('a and b must be non-zero')
    ra = ea / a
    rb = eb / b
    R = abs(ra) + abs(rb)
    P = a * b
    Q = a / b
    out = ['a*b = ' + _g(P) + ' +/- ' + _e(abs(P) * R),
           'a/b = ' + _g(Q) + ' +/- ' + _e(abs(Q) * R),
           'rel error <= ' + _e(R) + ' (both)']
    out.append(_w('relative errors add: |ra| + |rb|'))
    out.append(_w('ra = ea/a = ' + _e(ra) + ', rb = eb/b = ' + _e(rb)))
    out.append(_w('signed: r(ab) ~ ra+rb = ' + _e(ra + rb)))
    out.append(_w('signed: r(a/b) ~ ra-rb = ' + _e(ra - rb)))
    lo, hi = _corners(lambda p, q: p * q, a, abs(ea), b, abs(eb))
    out.append(_w('a*b lies in ' + _g(lo) + ' to ' + _g(hi)))
    if abs(eb) < abs(b):
        lo, hi = _corners(lambda p, q: p / q, a, abs(ea), b, abs(eb))
        out.append(_w('a/b lies in ' + _g(lo) + ' to ' + _g(hi)))
    else:
        out.append(_wn('b +/- eb includes 0: a/b unbounded'))
    out.append(_w('first order: the ra*rb term is ignored'))
    return out

def t_errfx(f, x, dx):
    _chk(f)
    fv = _fx(f, x)
    d = _deriv(f)
    gp = _dval(f, d, x)
    if gp is None:
        raise ValueError("f'(x) cannot be found")
    ef = gp * dx
    out = ['f(x) = ' + _g(fv), 'error in f ~ ' + _e(ef)]
    if fv != 0:
        out.append('relative error ~ ' + _e(ef / fv))
    out.append(_w("error in f ~ f'(x) * error in x"))
    if d is not None:
        out.append(_w("f'(x) = " + caseng.tostr(d)))
    out.append(_w("f'(" + _g(x) + ') = ' + _g(gp)))
    hi = _at(f, x + dx)
    if hi is not None:
        out.append(_w('actual f(x+dx) - f(x) = ' + _e(hi - fv)))
    if x != 0 and fv != 0:
        out.append(_w('rel error in x = ' + _e(dx / x) + ', magnified by ' +
                      _e(x * gp / fv)))
    return out

def _chop_lines(x, nc, nr, p, u):
    ch = nc / (10.0 ** p) if p >= 0 else nc * (10.0 ** (-p))
    rd = nr / (10.0 ** p) if p >= 0 else nr * (10.0 ** (-p))
    return ['chopped = ' + _dpstr(nc, p),
            'rounded = ' + _dpstr(nr, p),
            'chop error = ' + _e(ch - x),
            'round error = ' + _e(rd - x),
            _w('error = stored value - true value'),
            _w('unit u = ' + _e(u))]

def t_chop_dp(x, d):
    d = _int_in(d, 0, 12, 'd')
    u = 10.0 ** (-d)
    s = _scaled(x, d)
    out = _chop_lines(x, _chop_int(s), _round_int(s), d, u)
    out.append('chop: max error ' + _e(u) + ', mean ' + _e(u / 2.0))
    out.append('round: max error ' + _e(u / 2.0) + ', mean 0')
    out.append(_w('chop errors all have one sign: the'))
    out.append(_w('average |error| is u/2 and they build'))
    out.append(_w('up in a sum; rounding errors average 0'))
    out.append(_w('(mean |error| u/4) and tend to cancel'))
    return out

def t_chop_sf(x, k):
    k = _int_in(k, 1, 12, 'k')
    if x == 0:
        raise ValueError('x must be non-zero')
    p = k - 1 - _exp10(x)
    s = _scaled(x, p)
    nc = _chop_int(s)
    nr = _round_int(s)
    pr = p
    if abs(nr) >= 10 ** k:
        nr = _round_int(nr / 10.0)
        pr = p - 1
    u = 10.0 ** (-p)
    out = _chop_lines(x, nc, nr, p, u)
    if pr != p:
        out[1] = 'rounded = ' + _dpstr(nr, pr)
        rd = nr / (10.0 ** pr) if pr >= 0 else nr * (10.0 ** (-pr))
        out[3] = 'round error = ' + _e(rd - x)
    out.append('chop: rel error < ' + _e(10.0 ** (1 - k)))
    out.append('round: rel error <= ' + _e(5.0 * 10.0 ** (-k)))
    out.append(_w('relative error bounds for k s.f.:'))
    out.append(_w('chop 10^(1-k), round 0.5*10^(1-k)'))
    return out

_OPS = ('+', '-', '*', '/', '^')

def _keval(t, x, k, steps):
    # evaluate t with every intermediate result rounded to k s.f.
    tag = t[0]
    if tag == 'n' or tag == 'v':
        v = caseng.evalf(t, x, False)
        if isinstance(v, complex):
            raise ValueError('value is not real')
        return _rk(float(v), k)
    kids = []
    new = [tag]
    for c in t[1:]:
        if isinstance(c, tuple):
            cv = _keval(c, x, k, steps)
            kids.append(cv)
            new.append(('n', cv))
        else:
            new.append(c)
    try:
        v = caseng.evalf(tuple(new), x, False)
    except Exception:
        raise ValueError('cannot evaluate ' + tag)
    v = casutil.clean(v)
    if isinstance(v, complex):
        raise ValueError('value is not real')
    r = _rk(float(v), k)
    ks = [_f(c, k) for c in kids]
    if tag in _OPS and len(ks) == 2:
        desc = ks[0] + ' ' + tag + ' ' + ks[1]
    elif tag == 'neg':
        desc = '-' + ks[0]
    else:
        desc = tag + '(' + ', '.join(ks) + ')'
    steps.append(_w(desc + ' -> ' + _f(r, k)))
    return r

def _kvalue(f, x, k):
    steps = []
    xr = _rk(x, k)
    v = _keval(f, xr, k, steps)
    return (v, steps)

def t_ksf(f, x, k):
    _chk(f)
    k = _int_in(k, 1, 12, 'k')
    v, steps = _kvalue(f, x, k)
    tv = _fx(f, x)
    out = [str(k) + ' s.f. arithmetic: ' + _f(v, k), 'true value = ' + _g(tv),
           'error = ' + _e(v - tv)]
    if tv != 0:
        out.append('relative error = ' + _e((v - tv) / tv))
    out.append(_w('x stored as ' + _f(_rk(x, k), k) +
                  ', each step rounded:'))
    return out + _elide(steps)

def t_twoforms(f, g, x, k):
    _chk(f)
    _chk(g, 'g')
    k = _int_in(k, 1, 12, 'k')
    v1, s1 = _kvalue(f, x, k)
    v2, s2 = _kvalue(g, x, k)
    tv = _fx(f, x)
    t2 = _fx(g, x, 'g')
    out = ['form 1: ' + _f(v1, k), 'form 2: ' + _f(v2, k), 'true value = ' + _g(tv)]
    e1 = abs(v1 - tv)
    e2 = abs(v2 - tv)
    if tv != 0:
        out.append('rel errors ' + _e(e1 / abs(tv)) + ', ' + _e(e2 / abs(tv)))
    if e1 < e2:
        out.append('form 1 is more accurate')
    elif e2 < e1:
        out.append('form 2 is more accurate')
    else:
        out.append('equally accurate')
    if abs(tv - t2) > 1e-9 * (1.0 + abs(tv)):
        out.append(_wn('the forms differ: true g = ' + _g(t2)))
    out.append(_w('subtracting nearly equal numbers loses'))
    out.append(_w('significant figures; rearrange to avoid'))
    out.append(_w('-- form 1 steps --'))
    out += _elide(s1)
    out.append(_w('-- form 2 steps --'))
    return out + _elide(s2)

# ---- E solving equations ----------------------------------------------------
# e2 any required accuracy and justify it, e3 relative efficiency, e4 fixed
# point iteration is first order / failure, e5 relaxation, NU7 convergence and
# order of convergence, Ne1 staircase and cobweb diagrams.

def _bracket(f, a, b):
    _chk(f)
    if a == b:
        raise ValueError('a and b must differ')
    if a > b:
        a, b = b, a
    return (a, b, _fx(f, a), _fx(f, b))

def _nosign(f, a, b, fa, fb):
    return ['no sign change in [a, b]',
            _wn('the method needs f(a), f(b) of opposite sign'),
            _w('f(' + _g(a) + ') = ' + _g(fa)),
            _w('f(' + _g(b) + ') = ' + _g(fb))]

def _bis(f, a, b, fa, fb, tol, rows):
    steps = 0
    evals = 2
    if fa == 0:
        return (a, 0.0, 0, evals)
    if fb == 0:
        return (b, 0.0, 0, evals)
    while (b - a) / 2.0 > tol and steps < 200:
        m = (a + b) / 2.0
        if m == a or m == b:
            break
        fm = _fx(f, m)
        evals += 1
        steps += 1
        if rows is not None:
            rows.append(_w(str(steps) + '  ' + _g7(a) + '  ' + _g7(b) + '  ' +
                           _g7(m) + '  ' + _e(fm)))
        if fm == 0:
            a = m
            b = m
            break
        if (fa < 0) == (fm < 0):
            a = m
            fa = fm
        else:
            b = m
    return ((a + b) / 2.0, (b - a) / 2.0, steps, evals)

def _jump(f, x, fa, fb):
    v = _at(f, x)
    big = abs(fa) if abs(fa) > abs(fb) else abs(fb)
    return v is None or abs(v) > big

def t_bisect(f, a, b, tol):
    a, b, fa, fb = _bracket(f, a, b)
    tol = _tol(tol)
    if fa * fb > 0:
        return _nosign(f, a, b, fa, fb)
    rows = [_w('r  a  b  mid  f(mid)')]
    x, err, n, ev = _bis(f, a, b, fa, fb, tol, rows)
    out = ['x = ' + _g(x), 'max error = ' + _e(err), 'steps = ' + str(n)]
    if _jump(f, x, fa, fb):
        out.append(_wn('f is not small there: a discontinuity?'))
    out.append(_w('interval halves each step: first order,'))
    out.append(_w('ratio of errors 1/2'))
    return out + _elide(rows)

def _fpos(f, a, b, fa, fb, tol, rows):
    xs = []
    evals = 2
    ok = False
    stuck = 0
    side = 0
    x = a
    while len(xs) < MAXIT:
        den = fb - fa
        if den == 0:
            break
        x = (a * fb - b * fa) / den
        fx = _fx(f, x)
        evals += 1
        xs.append(x)
        if rows is not None:
            rows.append(_w(str(len(xs)) + '  ' + _g7(a) + '  ' + _g7(b) + '  ' +
                           _g7(x) + '  ' + _e(fx)))
        if fx == 0 or (len(xs) > 1 and abs(x - xs[len(xs) - 2]) < tol):
            ok = True
            break
        if (fa < 0) == (fx < 0):
            a = x
            fa = fx
            now = -1
        else:
            b = x
            fb = fx
            now = 1
        stuck = stuck + 1 if now == side else 0
        side = now
    return (x, xs, ok, evals, stuck)

def t_falsepos(f, a, b, tol):
    a, b, fa, fb = _bracket(f, a, b)
    tol = _tol(tol)
    if fa * fb > 0:
        return _nosign(f, a, b, fa, fb)
    rows = [_w('r  a  b  x  f(x)')]
    x, xs, ok, ev, stuck = _fpos(f, a, b, fa, fb, tol, rows)
    out = ['x = ' + _g(x) if ok else 'x ~ ' + _g(x), 'steps = ' + str(len(xs))]
    if not ok:
        out.append(_wn('not converged in ' + str(MAXIT) + ' steps'))
    if _jump(f, x, fa, fb):
        out.append(_wn('f is not small there: a discontinuity?'))
    out.append(_w('x = (a f(b) - b f(a)) / (f(b) - f(a))'))
    if stuck >= 3:
        out.append(_w('one end stayed fixed for the last ' + str(stuck + 1) +
                      ' steps'))
    out += _order_lines(xs)
    out.append(_w('false position is first order'))
    return out + _elide(rows)

def _sec(f, x0, x1, tol):
    xs = [x0, x1]
    f0 = _at(f, x0)
    f1 = _at(f, x1)
    if f0 is None or f1 is None:
        return (xs, 'f undefined at a start value', 2)
    evals = 2
    while len(xs) < MAXIT + 2:
        if f1 == f0:
            return (xs, 'f(x(r)) = f(x(r-1)): secant fails', evals)
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        xs.append(x2)
        if abs(x2 - x1) < tol:
            return (xs, None, evals)
        if abs(x2) > 1e12:
            return (xs, 'the iterates run away', evals)
        f2 = _at(f, x2)
        evals += 1
        if f2 is None:
            return (xs, 'f undefined at x = ' + _g(x2), evals)
        x0, f0, x1, f1 = x1, f1, x2, f2
    return (xs, 'not converged in ' + str(MAXIT) + ' steps', evals)

def _conv_out(xs, err, name, steps):
    x = xs[len(xs) - 1]
    if err is None:
        out = ['x = ' + _g(x), 'steps = ' + str(steps)]
    else:
        out = [name + ' failed', _wn(err)]
    return out

def t_secant(f, x0, x1, tol):
    _chk(f)
    tol = _tol(tol)
    if x0 == x1:
        raise ValueError('x0 and x1 must differ')
    xs, err, ev = _sec(f, x0, x1, tol)
    out = _conv_out(xs, err, 'secant', len(xs) - 2)
    out.append(_w('x(r+1) = x(r) - f(x(r))(x(r)-x(r-1))'))
    out.append(_w('         / (f(x(r)) - f(x(r-1)))'))
    out += _order_lines(xs)
    out.append(_w('secant order is about 1.62'))
    return out + _itrows(xs)

def _nr(f, d, x0, tol):
    xs = [x0]
    x = x0
    evals = 0
    while len(xs) <= MAXIT:
        fv = _at(f, x)
        dv = _dval(f, d, x)
        evals += 2
        if fv is None or dv is None:
            return (xs, 'f undefined at x = ' + _g(x), evals)
        if dv == 0:
            return (xs, "f'(x) = 0 at x = " + _g(x), evals)
        nx = x - fv / dv
        xs.append(nx)
        if abs(nx - x) < tol:
            return (xs, None, evals)
        if abs(nx) > 1e12:
            return (xs, 'the iterates run away', evals)
        x = nx
    return (xs, 'not converged in ' + str(MAXIT) + ' steps', evals)

def t_newton(f, x0, tol):
    _chk(f)
    tol = _tol(tol)
    d = _deriv(f)
    xs, err, ev = _nr(f, d, x0, tol)
    out = _conv_out(xs, err, 'Newton-Raphson', len(xs) - 1)
    if d is not None:
        out.append(_w("f'(x) = " + caseng.tostr(d)))
    else:
        out.append(_w("f'(x) by central difference"))
    out.append(_w("x(r+1) = x(r) - f(x(r)) / f'(x(r))"))
    out += _order_lines(xs)
    out.append(_w('Newton-Raphson is second order'))
    return out + _itrows(xs)

def _fpi(g, x0, tol, lam=1.0):
    xs = [x0]
    x = x0
    while len(xs) <= MAXIT:
        gv = _at(g, x)
        if gv is None:
            return (xs, 'g undefined at x = ' + _g(x))
        nx = x + lam * (gv - x)
        xs.append(nx)
        if abs(nx - x) < tol:
            return (xs, None)
        if abs(nx) > 1e12:
            return (xs, 'the iteration diverges')
        x = nx
    return (xs, 'not converged in ' + str(MAXIT) + ' steps')

def _improved(xs):
    # x + d r/(1-r) using the last ratio of differences (U8)
    r = _last_ratio(xs)
    if r is None or abs(r) >= 1.0 or len(xs) < 2:
        return None
    n = len(xs) - 1
    return xs[n] + (xs[n] - xs[n - 1]) * r / (1.0 - r)

def t_fixed(g, x0, tol):
    _chk(g, 'g')
    tol = _tol(tol)
    xs, err = _fpi(g, x0, tol)
    x = xs[len(xs) - 1]
    out = ['x = ' + _g(x)] if err is None else [err]
    at = x if err is None else x0
    gp = _gd(g, at)
    if gp is not None:
        out.append("g'(" + _g7(at) + ') = ' + _g(gp))
        if abs(gp) < 1.0:
            out.append("|g'| < 1: converges")
            if abs(gp) < 1e-6:
                out.append("g' = 0: second order (or more)")
            else:
                out.append("first order, ratio -> g'")
        else:
            out.append(_wn("|g'| >= 1: diverges from the root"))
            out.append(_wn('rearrange x = g(x) or use relaxation'))
    if err is None and len(xs) > 3:
        imp = _improved(xs)
        if imp is not None:
            out.append(_w('improved x + d r/(1-r) = ' + _g(imp)))
    out += _order_lines(xs)
    return out + _itrows(xs)

def t_relax(g, x0, lam, tol):
    _chk(g, 'g')
    tol = _tol(tol)
    if lam == 0:
        raise ValueError('lambda must be non-zero')
    xs, err = _fpi(g, x0, tol, lam)
    x = xs[len(xs) - 1]
    out = ['x = ' + _g(x)] if err is None else [err]
    at = x if err is None else x0
    gp = _gd(g, at)
    if gp is not None:
        G = 1.0 + lam * (gp - 1.0)
        out.append("g' = " + _g(gp) + ", G' = " + _g(G))
        if abs(G) < 1.0:
            out.append("|G'| < 1: this lambda converges")
        else:
            out.append(_wn("|G'| >= 1: this lambda fails"))
        if gp != 1.0:
            out.append('best lambda = ' + _g(1.0 / (1.0 - gp)))
            out.append(_w("best lambda = 1/(1 - g') makes G' = 0"))
        else:
            out.append(_wn("g' = 1: no lambda helps"))
    out.append(_w('x(r+1) = (1-lambda) x(r) + lambda g(x(r))'))
    out.append(_w("G'(x) = 1 + lambda(g'(x) - 1)"))
    out += _order_lines(xs)
    return out + _itrows(xs)

def _balanced(terms):
    # sum of terms as a balanced '+' tree (depth log n, not n)
    while len(terms) > 1:
        nxt = []
        i = 0
        while i + 1 < len(terms):
            nxt.append(('+', terms[i], terms[i + 1]))
            i += 2
        if i < len(terms):
            nxt.append(terms[i])
        terms = nxt
    return terms[0]

def _sampled(t, lo, hi):
    # polyline of y = t(x) over [lo, hi]; None breaks where t is undefined
    pts = []
    i = 0
    while i <= 120:
        x = lo + (hi - lo) * i / 120.0
        y = _at(t, x)
        pts.append(None if y is None or abs(y) > 1e6 else (x, y))
        i += 1
    return pts

def t_cobweb(g, x0, n):
    _chk(g, 'g')
    n = 8 if n is None else _int_in(n, 1, 20, 'n')
    xs = [x0]
    x = x0
    i = 0
    while i < n:
        v = _at(g, x)
        if v is None or abs(v) > 1e6:
            break
        xs.append(v)
        x = v
        i += 1
    if len(xs) < 2:
        raise ValueError('g undefined at x0')
    pts = [(xs[0], xs[0])]
    i = 0
    while i + 1 < len(xs):
        pts.append((xs[i], xs[i + 1]))
        pts.append((xs[i + 1], xs[i + 1]))
        i += 1
    lo, hi = casutil.nice_range(xs, 0.3)
    import plot
    plot.run([_sampled(g, lo, hi), [(lo, lo), (hi, hi)], pts], lo, hi, 'lines',
             'y=g(x), y=x, path')
    last = xs[len(xs) - 1]
    gp = _gd(g, last)
    out = []
    if gp is None:
        out.append(_wn("g' unavailable: shape not named"))
    else:
        if gp > 0:
            out.append("staircase: g' > 0")
        elif gp < 0:
            out.append("cobweb: g' < 0")
        else:
            out.append("g' = 0 at the last point")
        out.append("g'(" + _g7(last) + ') = ' + _g(gp))
        if abs(gp) < 1.0:
            out.append("|g'| < 1: path closes in")
        else:
            out.append(_wn("|g'| > 1: path moves away (diverges)"))
    out.append(_w('blue y=g(x), red y=x, green the path'))
    return out + _itrows(xs)

def t_order(xs):
    if len(xs) < 3:
        raise ValueError('need at least 3 iterates')
    out = []
    r = _last_ratio(xs)
    if r is None:
        out.append(_wn('no usable ratio of differences'))
    else:
        out.append('ratio of differences = ' + _e(r))
        if abs(r) >= 1.0:
            out.append(_wn('|r| >= 1: the sequence diverges'))
    p = _order(xs)
    if p is None:
        out.append(_wn('order: need 4 or more iterates'))
    else:
        out.append('order p ~ ' + _f(p, 3))
        if p > 1.5:
            out.append('second order (or more)')
        elif r is not None and abs(r) < 1.0:
            out.append("first order: error x r per step")
    out.append(_w('d(r) = x(r) - x(r-1), r = d(r+1)/d(r)'))
    out.append(_w('|d(r+1)| ~ C |d(r)|^p'))
    imp = _improved(xs)
    if imp is not None:
        out.append(_w('improved x + d r/(1-r) = ' + _g(imp)))
    return out + _itrows(xs)

def t_compare(f, a, b, tol):
    a, b, fa, fb = _bracket(f, a, b)
    tol = _tol(tol)
    out = []
    work = []
    if fa * fb <= 0:
        x, err, n, ev = _bis(f, a, b, fa, fb, tol, None)
        out.append('bisection: ' + str(n) + ' steps')
        work.append(_w('bisection x = ' + _g(x) + ', ' + str(ev) + ' f evals'))
        x, xs, ok, ev, st = _fpos(f, a, b, fa, fb, tol, None)
        out.append('false position: ' + str(len(xs)) + ' steps')
        work.append(_w('false pos x = ' + _g(x) + ', ' + str(ev) + ' f evals'))
        if not ok:
            work.append(_wn('false position did not converge'))
    else:
        out.append(_wn('no sign change: no bisection or false pos'))
    xs, err, ev = _sec(f, a, b, tol)
    if err is None:
        out.append('secant: ' + str(len(xs) - 2) + ' steps')
        work.append(_w('secant x = ' + _g(xs[len(xs) - 1]) + ', ' + str(ev) +
                       ' f evals'))
    else:
        out.append(_wn('secant from a, b: ' + err))
    m = (a + b) / 2.0
    xs, err, ev = _nr(f, _deriv(f), m, tol)
    if err is None:
        out.append('Newton-Raphson: ' + str(len(xs) - 1) + ' steps')
        work.append(_w('N-R x = ' + _g(xs[len(xs) - 1]) + ', ' + str(ev) +
                       " f and f' evals"))
    else:
        out.append(_wn('Newton from midpoint: ' + err))
    work.append(_w('tolerance ' + _e(tol) + '; N-R starts at ' + _g7(m)))
    work.append(_w('orders: bisection 1 (ratio 1/2), false pos 1,'))
    work.append(_w('secant 1.62, Newton-Raphson 2'))
    work.append(_w('N-R needs f\' too: 2 evaluations a step'))
    return out + work

def t_justify(f, x, d):
    _chk(f)
    d = _int_in(d, 0, 12, 'd')
    n = _round_int(_scaled(x, d))
    X0 = n / (10.0 ** d)
    h = 0.5 * 10.0 ** (-d)
    lo = _fx(f, X0 - h)
    hi = _fx(f, X0 + h)
    xs = _dpstr(n, d)
    out = []
    if lo * hi < 0:
        out.append('sign change: root = ' + xs)
        out.append('correct to ' + str(d) + ' d.p.')
    elif lo == 0 or hi == 0:
        out.append('f = 0 at a bound: check again')
    else:
        out.append('no sign change: not shown')
        out.append(_wn('root not ' + xs + ' to ' + str(d) + ' d.p.,'))
        out.append(_wn('or a repeated root (touches the axis)'))
    out.append(_w('f(' + _g(X0 - h) + ') = ' + _e(lo)))
    out.append(_w('f(' + _g(X0 + h) + ') = ' + _e(hi)))
    return out

# ---- D numerical differentiation --------------------------------------------
# Nc1 forward and central differences with a sequence of h, c2 the error:
# empirical (tables, ratios) and graphical (error against h).

def _fwd(f, x, h):
    return (_fx(f, x + h) - _fx(f, x)) / h

def _cen(f, x, h):
    return (_fx(f, x + h) - _fx(f, x - h)) / (2.0 * h)

def _exact_d(f, x):
    d = _deriv(f)
    if d is None:
        return None
    return _at(d, x)

def t_fdiff(f, x, h):
    _chk(f)
    if h == 0:
        raise ValueError('h must be non-zero')
    fw = _fwd(f, x, h)
    ce = _cen(f, x, h)
    out = ['forward = ' + _g(fw), 'central = ' + _g(ce)]
    ex = _exact_d(f, x)
    if ex is not None:
        out.append("exact f'(x) = " + _g(ex))
        out.append(_w('errors: forward ' + _e(fw - ex) + ', central ' +
                      _e(ce - ex)))
    out.append(_w('forward (f(x+h) - f(x)) / h, error ~ h'))
    out.append(_w('central (f(x+h) - f(x-h)) / 2h, error ~ h^2'))
    return out

def _table(labels, vals):
    # rows: label value difference ratio(d(n+1)/d(n))
    rows = []
    i = 0
    while i < len(vals):
        s = labels[i] + '  ' + _g(vals[i])
        if i >= 1:
            s += '  d ' + _e(vals[i] - vals[i - 1])
        if i >= 2:
            r = _ratio(vals[i] - vals[i - 1], vals[i - 1] - vals[i - 2])
            if r is not None:
                s += '  r ' + _e(r)
        rows.append(_w(s))
        i += 1
    return rows

def _lastr(vals):
    n = len(vals)
    if n < 3:
        return None
    return _ratio(vals[n - 1] - vals[n - 2], vals[n - 2] - vals[n - 3])

def _good_ratio(vals):
    # last ratio of differences in (0, 1), and whether it is the final row
    i = len(vals) - 1
    while i >= 2:
        r = _ratio(vals[i] - vals[i - 1], vals[i - 1] - vals[i - 2])
        if r is not None and 0 < r < 1:
            return (r, i == len(vals) - 1)
        i -= 1
    return (None, len(vals) < 3)

def t_dtable(f, x, h, k):
    _chk(f)
    h = 0.1 if h is None else h
    k = 2.0 if k is None else k
    if h == 0:
        raise ValueError('h must be non-zero')
    if k <= 1 or k > 100:
        raise ValueError('k from 1 to 100 (h divides by k)')
    fws = []
    ces = []
    labs = []
    i = 0
    while i < 6:
        fws.append(_fwd(f, x, h))
        ces.append(_cen(f, x, h))
        labs.append('h ' + _e(h))
        h = h / k
        i += 1
    n = len(fws)
    efw = fws[n - 1] + (fws[n - 1] - fws[n - 2]) / (k - 1.0)
    ece = ces[n - 1] + (ces[n - 1] - ces[n - 2]) / (k * k - 1.0)
    out = ['central -> ' + _g(ces[n - 1]),
           'improved central = ' + _g(ece),
           'improved forward = ' + _g(efw)]
    ex = _exact_d(f, x)
    if ex is not None:
        out.append("exact f'(x) = " + _g(ex))
    noisy = False
    for nm, vals in (('forward', fws), ('central', ces)):
        r, last = _good_ratio(vals)
        if r is not None:
            out.append(_w(nm + ' ratio ' + _e(r) + ', order ~ ' +
                          _f(-math.log(r) / math.log(k), 3)))
        if not last:
            noisy = True
    out.append(_w('h / ' + _e(k) + ' each row; ratio 1/k means error ~ h,'))
    out.append(_w('1/k^2 means error ~ h^2'))
    out.append(_w('improved: X + d/(k-1) forward,'))
    out.append(_w('X + d/(k^2-1) central'))
    out.append(_w('-- forward --'))
    out += _table(labs, fws)
    out.append(_w('-- central --'))
    out += _table(labs, ces)
    if noisy:
        out.append(_wn('last rows: rounding error dominates'))
    return out

def _lg(v):
    v = abs(v)
    return math.log10(v) if v > 1e-17 else -17.0

def t_dplot(f, x):
    _chk(f)
    ex = _exact_d(f, x)
    if ex is None:
        raise ValueError("the CAS cannot find f'(x)")
    fp = []
    cp = []
    rows = []
    best = [None, None]
    i = 1
    while i <= 12:
        h = 10.0 ** (-i)
        ef = _fwd(f, x, h) - ex
        ec = _cen(f, x, h) - ex
        fp.append((-float(i), _lg(ef)))
        cp.append((-float(i), _lg(ec)))
        rows.append(_w('h 1e-' + str(i) + '  fwd err ' + _e(ef) +
                       '  cen err ' + _e(ec)))
        if best[0] is None or abs(ef) < best[0][1]:
            best[0] = (i, abs(ef))
        if best[1] is None or abs(ec) < best[1][1]:
            best[1] = (i, abs(ec))
        i += 1
    import plot
    ys = [p[1] for p in fp + cp]
    plot.run([fp, cp], -12.5, -0.5, 'lines',
             'log10|error| v log10 h', min(ys) - 0.5, max(ys) + 0.5)
    out = ['best forward h = 1e-' + str(best[0][0]),
           'best central h = 1e-' + str(best[1][0]),
           'smallest central error ' + _e(best[1][1])]
    out.append(_w('blue forward, red central'))
    out.append(_w('large h: truncation error (h, h^2)'))
    out.append(_w('small h: rounding error ~ 1/h from'))
    out.append(_w('subtracting nearly equal f values'))
    return out + rows

# ---- N numerical integration ------------------------------------------------
# Nc3 midpoint, trapezium and Simpson's rules, c4 their error behaviour.

def _anti(t):
    try:
        F = cascalc.integ(t, 'x')
    except Exception:
        return None
    if F is None:
        return None
    try:
        return cascalc.tidy(F)
    except Exception:
        return F

def _exact_int(t, a, b):
    F = _anti(t)
    if F is not None:
        hi = _at(F, b)
        lo = _at(F, a)
        if hi is not None and lo is not None:
            return hi - lo
    return None

def _mid(f, a, b, n):
    h = (b - a) / n
    tot = 0.0
    i = 0
    while i < n:
        tot += _fx(f, a + (i + 0.5) * h)
        i += 1
    return tot * h

def _trap(f, a, b, n):
    h = (b - a) / n
    tot = _fx(f, a) + _fx(f, b)
    i = 1
    while i < n:
        tot += 2.0 * _fx(f, a + i * h)
        i += 1
    return tot * h / 2.0

def _simp(f, a, b, n):
    h = (b - a) / n
    tot = _fx(f, a) + _fx(f, b)
    i = 1
    while i < n:
        tot += (4.0 if (i % 2) else 2.0) * _fx(f, a + i * h)
        i += 1
    return tot * h / 3.0

def _strips(f, a, b, n):
    _chk(f)
    if a == b:
        raise ValueError('limits are equal')
    return _int_in(n, 1, 1000, 'n')

def _ords(f, xs):
    out = []
    i = 0
    while i < len(xs) and i < 12:
        out.append(_w('  x = ' + _g7(xs[i]) + '   f = ' + _g(_fx(f, xs[i]))))
        i += 1
    if len(xs) > 12:
        out.append(_w('  ... ' + str(len(xs) - 12) + ' more ordinates'))
    return out

def _vs_exact(f, a, b, val):
    ex = _exact_int(f, a, b)
    if ex is None:
        return []
    return ['exact = ' + _g(ex), _w('error = ' + _e(val - ex))]

def t_mid(f, a, b, n):
    n = _strips(f, a, b, n)
    h = (b - a) / n
    val = _mid(f, a, b, n)
    out = ['M = ' + _g(val)] + _vs_exact(f, a, b, val)
    out.append(_w('M = h(f(x1/2) + f(x3/2) + ...), h = ' + _g(h)))
    return out + _ords(f, [a + (i + 0.5) * h for i in range(n)])

def t_trap(f, a, b, n):
    n = _strips(f, a, b, n)
    h = (b - a) / n
    val = _trap(f, a, b, n)
    out = ['T = ' + _g(val)] + _vs_exact(f, a, b, val)
    out.append(_w('T = h/2 (f0 + 2(f1 + ...) + fn), h = ' + _g(h)))
    return out + _ords(f, [a + i * h for i in range(n + 1)])

def t_simp(f, a, b, n):
    n = _strips(f, a, b, n)
    if n % 2:
        raise ValueError('n must be even')
    h = (b - a) / n
    val = _simp(f, a, b, n)
    out = ['S = ' + _g(val)] + _vs_exact(f, a, b, val)
    out.append(_w('S = h/3 (ends + 4 odds + 2 evens), h = ' + _g(h)))
    half = n // 2
    out.append(_w('also S(' + str(n) + ') = (2M(' + str(half) + ') + T(' +
                  str(half) + '))/3'))
    return out + _ords(f, [a + i * h for i in range(n + 1)])

def t_itable(f, a, b, n):
    n = 1 if n is None else n
    n = _strips(f, a, b, n)
    if n > 32:
        raise ValueError('n from 1 to 32')
    ms = []
    ts = []
    ss = []
    lm = []
    ls = []
    k = 0
    while k < 6:
        m = _mid(f, a, b, n)
        t = _trap(f, a, b, n)
        ms.append(m)
        ts.append(t)
        ss.append((2.0 * m + t) / 3.0)
        lm.append('n=' + str(n))
        ls.append('n=' + str(2 * n))
        n *= 2
        k += 1
    N = len(ss)
    imp = ss[N - 1] + (ss[N - 1] - ss[N - 2]) / 15.0
    out = ['best S = ' + _g(ss[N - 1]), 'improved S = ' + _g(imp),
           'best T = ' + _g(ts[N - 1]), 'best M = ' + _g(ms[N - 1])]
    ex = _exact_int(f, a, b)
    if ex is not None:
        out.append('exact = ' + _g(ex))
    for nm, vals in (('M', ms), ('T', ts), ('S', ss)):
        r = _lastr(vals)
        if r is not None:
            out.append(_w(nm + ' ratio of differences ' + _e(r)))
    out.append(_w('M, T ratio 1/4: error ~ h^2'))
    out.append(_w('S ratio 1/16: error ~ h^4'))
    out.append(_w('T(2n) = (M(n) + T(n))/2, S(2n) = (2M+T)/3'))
    out.append(_w('improved S = S + d/15'))
    out.append(_w('-- midpoint M --'))
    out += _table(lm, ms)
    out.append(_w('-- trapezium T --'))
    out += _table(lm, ts)
    out.append(_w('-- Simpson S --'))
    return out + _table(ls, ss)

# ---- A approximating functions ----------------------------------------------
# Nf1 Newton's forward difference formula and difference tables, f2 the
# interpolating polynomial.

def _dtab(ys):
    rows = [list(ys)]
    while len(rows[len(rows) - 1]) > 1:
        p = rows[len(rows) - 1]
        rows.append([p[i] - p[i - 1] for i in range(1, len(p))])
    return rows

def _chunk(tag, vals, fm=None):
    # values after a tag, split over working lines of at most 50 characters
    out = []
    cur = tag + ':'
    for v in vals:
        s = ' ' + (fm(v) if fm else _f(v, 6))
        if len(cur) + len(s) > 50:
            out.append(_w(cur))
            cur = '   '
        cur += s
    out.append(_w(cur))
    return out

def _near(a, b):
    return abs(a - b) <= 1e-9 * (1.0 + abs(a) + abs(b))

def _degree(rows):
    k = 0
    while k < len(rows):
        r = rows[k]
        if len(r) >= 2:
            same = True
            for v in r:
                if not _near(v, r[0]):
                    same = False
            if same:
                return k
        k += 1
    return None

def _pmul_lin(p, m, c):
    # p(x) * (m x + c), coefficients low to high
    out = [0.0] * (len(p) + 1)
    i = 0
    while i < len(p):
        out[i + 1] += p[i] * m
        out[i] += p[i] * c
        i += 1
    return out

def _padd(p, q, s):
    n = len(p) if len(p) > len(q) else len(q)
    out = []
    i = 0
    while i < n:
        v = p[i] if i < len(p) else 0.0
        if i < len(q):
            v += s * q[i]
        out.append(v)
        i += 1
    return out

def _nn(v):
    # number node, exact rational when v is one
    if -1e15 < v < 1e15 and v == int(v):
        return ('n', int(v))
    q = 2
    while q <= 24:
        pv = v * q
        r = int(round(pv))
        if abs(pv - r) < 1e-9 * (abs(pv) if abs(pv) > 1.0 else 1.0):
            return ('/', ('n', r), ('n', q))
        q += 1
    return ('n', v)

def _snapc(v, scale):
    return 0.0 if abs(v) < 1e-10 * scale else v

def _ptree(c):
    scale = 1.0
    for v in c:
        if abs(v) > scale:
            scale = abs(v)
    terms = []
    k = len(c) - 1
    while k >= 0:
        v = _snapc(c[k], scale)
        if v != 0:
            if k == 0:
                terms.append(_nn(v))
            elif k == 1:
                terms.append(('*', _nn(v), X))
            else:
                terms.append(('*', _nn(v), ('^', X, ('n', k))))
        k -= 1
    if not terms:
        return ('n', 0)
    try:
        return caseng.simplify(_balanced(terms))
    except Exception:
        return _balanced(terms)

def _newton_poly(x0, h, lead):
    # Newton forward polynomial in x from leading differences
    px = [0.0]
    term = [1.0]
    k = 0
    while k < len(lead):
        px = _padd(px, term, lead[k] / _factf(k))
        # multiply by (s - k) with s = (x - x0)/h
        term = _pmul_lin(term, 1.0 / h, -x0 / h - k)
        k += 1
    return px

def _factf(k):
    r = 1.0
    i = 2
    while i <= k:
        r *= i
        i += 1
    return r

def _fd_check(h, ys):
    if h == 0:
        raise ValueError('h must be non-zero')
    if len(ys) < 2 or len(ys) > 12:
        raise ValueError('give 2 to 12 y values')

def t_fdtab(x0, h, ys):
    _fd_check(h, ys)
    rows = _dtab(ys)
    deg = _degree(rows[1:])
    lead = [r[0] for r in rows]
    if deg is not None:
        deg += 1
        if _near(rows[deg][0], 0.0):
            deg -= 1
        lead = lead[:deg + 1]
    px = _newton_poly(x0, h, lead)
    out = []
    if deg == 0:
        out.append('constant data: degree 0')
    elif deg is not None:
        out.append('D' + str(deg) + ' constant: degree ' + str(deg))
    else:
        out.append('degree ' + str(len(ys) - 1) + ' (no constant row)')
    out.append('p(x) =')
    out.append(_m(_ptree(px)))
    out.append(_w('s = (x - x0)/h, p = y0 + s D1 + s(s-1)/2! D2 + ...'))
    out += _chunk('leading differences', lead)
    out += _chunk('y ', rows[0])
    k = 1
    while k < len(rows):
        out += _chunk('D' + str(k), rows[k])
        k += 1
    return out

def t_fdest(x0, h, x, ys):
    _fd_check(h, ys)
    rows = _dtab(ys)
    s = (x - x0) / h
    tot = 0.0
    cf = 1.0
    work = [_w('s = (x - x0)/h = ' + _g(s))]
    last = 0.0
    k = 0
    while k < len(rows):
        term = rows[k][0] * cf
        tot += term
        last = term
        work.append(_w('D' + str(k) + ' term ' + _g(term) + '  sum ' + _g(tot)))
        cf = cf * (s - k) / (k + 1)
        k += 1
    out = ['p(' + _g7(x) + ') = ' + _g(tot)]
    out.append(_w('size of last term used ' + _e(abs(last))))
    if s < 0 or s > len(ys) - 1:
        out.append(_wn('x is outside the table: extrapolation'))
    return out + work

def t_lagrange(xy):
    if len(xy) % 2 or len(xy) < 4 or len(xy) > 16:
        raise ValueError('give 2 to 8 pairs x,y')
    xs = [xy[i] for i in range(0, len(xy), 2)]
    ys = [xy[i] for i in range(1, len(xy), 2)]
    n = len(xs)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            if xs[i] == xs[j]:
                raise ValueError('x values must differ')
            j += 1
        i += 1
    px = [0.0]
    i = 0
    while i < n:
        L = [1.0]
        den = 1.0
        j = 0
        while j < n:
            if j != i:
                L = _pmul_lin(L, 1.0, -xs[j])
                den *= xs[i] - xs[j]
            j += 1
        px = _padd(px, L, ys[i] / den)
        i += 1
    while len(px) > 1 and abs(px[len(px) - 1]) < 1e-12:
        px.pop()
    out = ['p(x) =', _m(_ptree(px)), 'degree ' + str(len(px) - 1)]
    out.append(_w('p(x) = sum y(i) L(i)(x), L(i) = prod'))
    out.append(_w('  (x - x(j))/(x(i) - x(j)), j != i'))
    return out

# ---- I improved estimates ---------------------------------------------------
# U8 use error analysis to produce an improved estimate: Richardson
# extrapolation, Aitken's delta-squared, and the ratio-of-differences limit.

def t_richardson(p, ests):
    if p <= 0:
        raise ValueError('p must be > 0')
    if len(ests) < 2 or len(ests) > 10:
        raise ValueError('give 2 to 10 estimates')
    col = list(ests)
    out = []
    work = [_w('estimates with h halving; error ~ h^p'),
            _w('R = new + (new - old)/(2^(pj) - 1)')]
    work += _chunk('col 0', col, _g)
    j = 1
    while len(col) > 1:
        fac = 2.0 ** (p * j) - 1.0
        col = [col[i] + (col[i] - col[i - 1]) / fac for i in range(1, len(col))]
        work += _chunk('col ' + str(j) + ' (/' + _e(fac) + ')', col, _g)
        j += 1
    best = col[0]
    out.append('best = ' + _g(best))
    out.append('change from last = ' + _e(best - ests[len(ests) - 1]))
    return out + work

def t_aitken(xs):
    if len(xs) < 3:
        raise ValueError('need at least 3 terms')
    work = [_w('y = x2 - (x2 - x1)^2 / (x2 - 2x1 + x0)')]
    ys = []
    k = 0
    while k + 2 < len(xs):
        a = xs[k]
        b = xs[k + 1]
        c = xs[k + 2]
        den = c - 2.0 * b + a
        if den == 0:
            work.append(_wn('terms ' + str(k) + '-' + str(k + 2) +
                            ': second difference 0'))
        else:
            y = c - (c - b) * (c - b) / den
            ys.append(y)
            work.append(_w('from x' + str(k) + '..x' + str(k + 2) + ': ' + _g(y)))
        k += 1
    if not ys:
        return [_wn('no accelerated value (differences constant)')] + work
    best = ys[len(ys) - 1]
    return (['improved = ' + _g(best),
             'change from last = ' + _e(best - xs[len(xs) - 1])] + work)

def t_ratiolim(r, ests):
    if abs(r) >= 1.0 or r == 0:
        raise ValueError('need 0 < |r| < 1')
    if len(ests) < 2:
        raise ValueError('need at least 2 estimates')
    n = len(ests) - 1
    d = ests[n] - ests[n - 1]
    lim = ests[n] + d * r / (1.0 - r)
    out = ['limit ~ ' + _g(lim), 'error in last ~ ' + _e(ests[n] - lim)]
    out.append(_w('later differences d r + d r^2 + ... = d r/(1-r)'))
    out.append(_w('last difference d = ' + _e(d)))
    if n >= 2:
        d0 = ests[n - 1] - ests[n - 2]
        if d0 != 0:
            out.append(_w('observed ratio ' + _e(d / d0) + ' (given ' + _e(r) + ')'))
    return out

SECTIONS = [
    ('U', 'Errors', [
        ('Absolute/rel error', 'approx,exact', t_error),
        ('Error in a+b, a-b', 'a,ea,b,eb', t_sumdiff),
        ('Error in ab, a/b', 'a,ea,b,eb', t_prodquot),
        ('Error in f(x)', 'f(x),x,dx', t_errfx),
        ('Chop vs round d.p.', 'x,d', t_chop_dp),
        ('Chop vs round s.f.', 'x,k', t_chop_sf),
        ('k s.f. arithmetic', 'f(x),x,k', t_ksf),
        ('Two forms compared', 'f(x),g(x),x,k', t_twoforms),
    ]),
    ('E', 'Solving equations', [
        ('Bisection', 'f(x),a,b,tol?', t_bisect),
        ('False position', 'f(x),a,b,tol?', t_falsepos),
        ('Secant method', 'f(x),x0,x1,tol?', t_secant),
        ('Newton-Raphson', 'f(x),x0,tol?', t_newton),
        ('Fixed point x=g(x)', 'g(x),x0,tol?', t_fixed),
        ('Relaxation', 'g(x),x0,lambda,tol?', t_relax),
        ('Staircase/cobweb', 'g(x),x0,n?', t_cobweb),
        ('Order from iterates', 'x*', t_order),
        ('Compare methods', 'f(x),a,b,tol?', t_compare),
        ('Justify root to d dp', 'f(x),x,d', t_justify),
    ]),
    ('D', 'Numerical differentiation', [
        ('Forward and central', 'f(x),x,h', t_fdiff),
        ('Derivative h table', 'f(x),x,h?,k?', t_dtable),
        ('Error vs h plot', 'f(x),x', t_dplot),
    ]),
    ('N', 'Numerical integration', [
        ('Midpoint rule', 'f(x),a,b,n', t_mid),
        ('Trapezium rule', 'f(x),a,b,n', t_trap),
        ("Simpson's rule", 'f(x),a,b,n', t_simp),
        ('Integration table', 'f(x),a,b,n?', t_itable),
    ]),
    ('A', 'Approximating functions', [
        ('Forward diff table', 'x0,h,y*', t_fdtab),
        ('Newton fwd estimate', 'x0,h,x,y*', t_fdest),
        ('Lagrange polynomial', 'xy*', t_lagrange),
    ]),
    ('I', 'Improved estimates', [
        ('Richardson', 'p,est*', t_richardson),
        ('Aitken delta squared', 'x*', t_aitken),
        ('Limit from ratio r', 'r,est*', t_ratiolim),
    ]),
]
