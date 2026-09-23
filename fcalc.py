# OCR B (MEI) Further Maths H645, Core Pure (Y420): calculus, polar
# coordinates, hyperbolic functions and differential equations (including
# SHM, damping, coupled systems and a = v dv/dx). The rest is in fcore.
import math
import caseng
import cascalc
import caspoly
import casutil

_f = casutil.fmt
_w = casutil.w
_wn = casutil.warn
_m = casutil.m
_mw = casutil.mw
_fv = casutil.fmtv

X = ('v', 'x')
PI = math.pi
E = math.e

# ---- shared calculus helpers ------------------------------------------------

def _ts(t):
    return caseng.tostr(t)

def _tidy(t):
    try:
        return cascalc.tidy(t)
    except Exception:
        return t

def _anti(tree, var='x'):
    # antiderivative, tidied, or None
    try:
        F = cascalc.integ(tree, var)
    except Exception:
        return None
    if F is None:
        return None
    return _tidy(F)

def _at(tree, v, var='x'):
    # real value of tree at var = v, or None
    try:
        r = caseng.evalf(tree, v, False, {var: v})
    except Exception:
        return None
    if isinstance(r, complex):
        return None
    if r != r or r > 1e300 or r < -1e300:
        return None
    return r

def _num(tree, a, b, var='x', n=400):
    try:
        return cascalc.defint(tree, a, b, False, n, var)
    except Exception:
        return None

def _exact_int(tree, a, b, var='x'):
    # (value, antiderivative or None, exact flag)
    F = _anti(tree, var)
    if F is not None:
        hi = _at(F, b, var)
        lo = _at(F, a, var)
        if hi is not None and lo is not None:
            return (hi - lo, F, True)
    return (_num(tree, a, b, var), F, False)

def _gap(tree, a, b, var='x'):
    # True if the integrand is undefined somewhere strictly inside [a, b]
    i = 1
    while i < 40:
        if _at(tree, a + (b - a) * i / 40.0, var) is None:
            return True
        i += 1
    return False

GAPMSG = 'f is undefined inside the range'

def _order(a, b):
    if a == b:
        raise ValueError('limits are equal')
    return (b, a) if b < a else (a, b)

def _ivar(tree, want):
    vs = caseng.vars_in(tree)
    if want in vs or not vs:
        return want
    if 'x' in vs:
        return 'x'
    return vs[0]

def _dvar(tree, var):
    try:
        return _tidy(caseng.diff(tree, var))
    except Exception:
        raise ValueError('cannot differentiate')

def _nn(v):
    # exact-rational tree node, so caspoly can collect terms
    if -1e15 < v < 1e15 and v == int(v):
        return ('n', int(v))
    q = 2
    while q <= 360:
        pv = v * q
        r = int(round(pv))
        if abs(pv - r) < 1e-9 * (abs(pv) if abs(pv) > 1.0 else 1.0):
            return caseng.simplify(('/', ('n', r), ('n', q)))
        q += 1
    return ('n', v)

def _signed(v, body):
    sgn = ' - ' if v < 0 else ' + '
    av = abs(v)
    if body != '' and abs(av - 1.0) < 1e-12:
        return sgn + body
    return sgn + _f(av) + body

def _lead(v, body):
    if abs(v - 1.0) < 1e-12:
        return body
    if abs(v + 1.0) < 1e-12:
        return '-' + body
    return _f(v) + body

def _trigrhs(mm, nn, ang):
    s = ''
    if abs(mm) > 1e-12:
        s = _lead(mm, 'cos ' + ang)
    if abs(nn) > 1e-12:
        s = s + _signed(nn, 'sin ' + ang) if s else _lead(nn, 'sin ' + ang)
    return s if s else '0'

def _expstr(k, p):
    if abs(p) < 1e-12:
        e = '1'
    elif abs(p - 1.0) < 1e-12:
        e = 'e^x'
    elif abs(p + 1.0) < 1e-12:
        e = 'e^(-x)'
    else:
        e = 'e^(' + _f(p) + 'x)'
    if abs(k - 1.0) < 1e-12:
        return e
    if abs(k + 1.0) < 1e-12:
        return '-' + e
    return _f(k) + ' ' + e

def _sq(t):
    return caseng.simplify(('^', t, ('n', 2)))

def _pos(v, name):
    if v is None or v <= 0:
        raise ValueError(name + ' must be > 0')
    return v

# ---- C  Calculus ------------------------------------------------------------

def _verdict(vals):
    # ('c', limit) / ('d', None) / ('?', None) from a table of partial values
    good = []
    for v in vals:
        if v is not None:
            good.append(v)
    k = len(good)
    if k < 3:
        return ('?', None)
    last = good[k - 1]
    d1 = last - good[k - 2]
    d0 = good[k - 2] - good[k - 3]
    if abs(d1) <= 1e-9 * (1.0 + abs(last)):
        return ('c', last)
    if abs(last) > 1e8 or abs(d0) < 1e-290:
        return ('d', None)
    r = abs(d1 / d0)
    if r > 0.9:
        return ('d', None)
    return ('c', last + d1 * r / (1.0 - r))

def _verdict_line(kind, val):
    if kind == 'c':
        return 'integral = ' + _f(val)
    if kind == 'd':
        return 'diverges'
    return 'no limit found'

def t_int_inf(f, a):
    F = _anti(f)
    pts = []
    t = 1.0
    i = 0
    while i < 7:
        pts.append(a + t)
        t *= 10.0
        i += 1
    vals = []
    if F is not None:
        lo = _at(F, a)
        for b in pts:
            hi = _at(F, b)
            vals.append(None if (hi is None or lo is None) else hi - lo)
    else:
        tot = 0.0
        prev = a
        ok = True
        for b in pts:
            seg = _num(f, prev, b, 'x', 200) if ok else None
            if seg is None:
                ok = False
                vals.append(None)
            else:
                tot += seg
                vals.append(tot)
            prev = b
    kind, val = _verdict(vals)
    if kind == 'c' and F is not None:
        lo = _at(F, a)
        hi = _at(F, a + 1e12)
        if lo is not None and hi is not None:
            if abs(hi - lo - val) <= 1e-6 * (1.0 + abs(val)):
                val = hi - lo
    out = [_verdict_line(kind, val)]
    out.append(_w('int f dx from ' + _f(a) + ' to infinity'))
    if F is not None:
        out.append(_mw(F))
    i = 0
    while i < len(pts):
        s = 'failed' if vals[i] is None else _f(vals[i], 6)
        out.append(_w('  up to ' + _f(pts[i], 6) + ':  ' + s))
        i += 1
    if kind == 'c':
        out.append(_wn('value of a limit, found numerically'))
    return out

def t_int_sing(f, a, b):
    a, b = _order(a, b)
    fa = _at(f, a)
    fb = _at(f, b)
    if fa is not None and fb is not None:
        raise ValueError('f is defined at both ends')
    if fa is None and fb is None:
        raise ValueError('both ends undefined')
    bad = a if fa is None else b
    at_a = fa is None
    h = b - a
    eps = []
    e = 0.1 * h
    i = 0
    while i < 6:
        eps.append(e)
        e /= 10.0
        i += 1
    F = _anti(f)
    vals = []
    if F is not None:
        for e in eps:
            if at_a:
                hi = _at(F, b)
                lo = _at(F, a + e)
            else:
                hi = _at(F, b - e)
                lo = _at(F, a)
            vals.append(None if (hi is None or lo is None) else hi - lo)
    else:
        tot = 0.0
        prev = None
        ok = True
        for e in eps:
            if not ok:
                vals.append(None)
                continue
            if prev is None:
                seg = _num(f, a + e, b, 'x', 200) if at_a else _num(f, a, b - e, 'x', 200)
            elif at_a:
                seg = _num(f, a + e, a + prev, 'x', 200)
            else:
                seg = _num(f, b - prev, b - e, 'x', 200)
            if seg is None:
                ok = False
                vals.append(None)
            else:
                tot += seg
                vals.append(tot)
            prev = e
    kind, val = _verdict(vals)
    out = [_verdict_line(kind, val)]
    out.append(_wn('f is undefined at x = ' + _f(bad)))
    out.append(_w('int f dx from ' + _f(a) + ' to ' + _f(b)))
    if F is not None:
        out.append(_mw(F))
    i = 0
    while i < len(eps):
        s = 'failed' if vals[i] is None else _f(vals[i], 6)
        out.append(_w('  gap ' + _f(eps[i], 3) + ':  ' + s))
        i += 1
    return out

def _volume(f, a, b, var, axis):
    a, b = _order(a, b)
    val, F, exact = _exact_int(_sq(f), a, b, var)
    if val is None:
        raise ValueError('cannot integrate over that range')
    v = PI * val
    out = ['V = ' + _f(v)]
    if _f(v) != casutil.sf3(v):
        out.append('  = ' + casutil.sf3(v))
    lab = 'y^2 dx' if axis == 'x' else 'x^2 dy'
    out.append(_w('V = pi * int ' + lab + ', ' + _f(a) + ' to ' + _f(b)))
    if F is not None:
        out.append(_mw(F))
    out.append(_w('int ' + lab + ' = ' + _f(val, 6)))
    if not exact:
        out.append(_wn('integral found numerically'))
    if _gap(f, a, b, var):
        out.append(_wn(GAPMSG))
    return out

def t_vol_x(f, a, b):
    return _volume(f, a, b, _ivar(f, 'x'), 'x')

def t_vol_y(g, c, d):
    return _volume(g, c, d, _ivar(g, 'y'), 'y')

def t_mean(f, a, b):
    a, b = _order(a, b)
    val, F, exact = _exact_int(f, a, b)
    if val is None:
        raise ValueError('cannot integrate over that range')
    mean = val / (b - a)
    out = ['mean = ' + _f(mean)]
    if _f(mean) != casutil.sf3(mean):
        out.append('     = ' + casutil.sf3(mean))
    out.append(_w('mean = (1/(b-a)) int f dx'))
    if F is not None:
        out.append(_mw(F))
    out.append(_w('int f dx = ' + _f(val, 6) + ',  b-a = ' + _f(b - a)))
    if not exact:
        out.append(_wn('integral found numerically'))
    if _gap(f, a, b):
        out.append(_wn(GAPMSG))
    hits = []
    try:
        for r in cascalc.solve(caseng.simplify(('-', f, ('n', mean))), 'x'):
            if a - 1e-9 <= r <= b + 1e-9:
                hits.append(r)
    except Exception:
        hits = []
    for r in hits:
        out.append('f = mean at x = ' + _f(r))
    return out

def t_partial_int(p, q):
    pf = None
    try:
        pf = caspoly.partial(p, q)
    except Exception:
        pf = None
    if pf is None:
        raise ValueError('cannot split into partial fractions')
    quot, terms = pf
    s = quot
    for top, den, k in terms:
        piece = ('/', _tidy(top), den if k == 1 else ('^', den, ('n', k)))
        s = piece if s is None else ('+', s, piece)
    if s is None:
        s = ('n', 0)
    F = _anti(('/', p, q))
    out = []
    if F is not None:
        out.append(_m(F))
    else:
        out.append('no elementary integral')
    out.append(_w('f(x) = (' + _ts(p) + ')/(' + _ts(q) + ')'))
    out.append(_w('partial fractions:'))
    out.append(_mw(caseng.simplify(s)))
    if F is None:
        out.append(_wn('integrate the parts by hand'))
    return out

def t_invtrig_diff(f, a):
    d = _dvar(f, _ivar(f, 'x'))
    out = [_m(d)]
    if a is not None:
        v = _at(d, a, _ivar(f, 'x'))
        if v is None:
            out.append(_wn('derivative undefined at ' + _f(a)))
        else:
            out.append("f'(" + _f(a) + ') = ' + _f(v))
    out.append(_w('f(x) = ' + _ts(f)))
    return out

def t_int_asin(a, p, q):
    a = _pos(a, 'a')
    if abs(p) > a or abs(q) > a:
        raise ValueError('need |p| and |q| <= a')
    val = math.asin(q / a) - math.asin(p / a)
    F = ('asin', ('/', X, _nn(a)))
    out = ['integral = ' + _f(val)]
    if _f(val) != casutil.sf3(val):
        out.append('     = ' + casutil.sf3(val))
    out.append(_w('int 1/sqrt(a^2-x^2) dx = asin(x/a)'))
    out.append(_mw(F))
    out.append(_w('asin(' + _f(q / a) + ') - asin(' + _f(p / a) + ')'))
    return out

def t_int_atan(a, p, q):
    a = _pos(a, 'a')
    val = (math.atan(q / a) - math.atan(p / a)) / a
    F = ('/', ('atan', ('/', X, _nn(a))), _nn(a))
    out = ['integral = ' + _f(val)]
    if _f(val) != casutil.sf3(val):
        out.append('     = ' + casutil.sf3(val))
    out.append(_w('int 1/(a^2+x^2) dx = (1/a)atan(x/a)'))
    out.append(_mw(F))
    out.append(_w('(1/' + _f(a) + ')(atan(' + _f(q / a) + ') - atan(' + _f(p / a) + '))'))
    return out

# ---- PO  Polar coordinates --------------------------------------------------

def t_polar_to_xy(r, th):
    x = r * math.cos(th)
    y = r * math.sin(th)
    out = ['x = ' + _f(x), 'y = ' + _f(y)]
    out.append(_w('x = r cos(th), y = r sin(th)'))
    out.append(_w('r = ' + _f(r) + ', th = ' + _f(th) + ' rad'))
    return out

def t_xy_to_polar(x, y):
    r = math.sqrt(x * x + y * y)
    th = math.atan2(y, x)
    out = ['r = ' + _f(r), 'theta = ' + _f(th) + ' rad',
           '      = ' + _f(casutil.deg(th)) + ' deg']
    out.append(_w('r = sqrt(x^2+y^2), th = atan2(y, x)'))
    out.append(_w('-pi < theta <= pi'))
    return out

def _polar_r(tree, th):
    v = casutil.evx(tree, th)
    return v

def t_polar_plot(r):
    import plot
    plot.run([r], 0.0, 2.0 * PI, 'polar', 'r = ' + _ts(r))
    out = []
    names = ('0', 'pi/2', 'pi', '3pi/2')
    ths = (0.0, PI / 2.0, PI, 3.0 * PI / 2.0)
    i = 0
    while i < 4:
        v = _polar_r(r, ths[i])
        out.append('r(' + names[i] + ') = ' + ('undefined' if v is None else _f(v)))
        i += 1
    best = None
    bth = 0.0
    i = 0
    while i <= 360:
        th = 2.0 * PI * i / 360.0
        v = _polar_r(r, th)
        if v is not None and (best is None or abs(v) > abs(best)):
            best = v
            bth = th
        i += 1
    if best is not None:
        out.append(_w('largest |r| = ' + _f(abs(best)) + ' at th = ' + _f(bth)))
    return out

def t_polar_area(r, a, b):
    a, b = _order(a, b)
    sq = _sq(r)
    val, F, exact = _exact_int(sq, a, b)
    if val is None:
        raise ValueError('cannot integrate over that range')
    area = 0.5 * val
    out = ['area = ' + _f(area)]
    if _f(area) != casutil.sf3(area):
        out.append('     = ' + casutil.sf3(area))
    out.append(_w('A = (1/2) int r^2 dth, ' + _f(a) + ' to ' + _f(b)))
    if F is not None:
        out.append(_mw(F))
    out.append(_w('int r^2 dth = ' + _f(val, 6)))
    if not exact:
        out.append(_wn('integral found numerically'))
    if _gap(sq, a, b):
        out.append(_wn(GAPMSG))
    return out

# ---- H  Hyperbolic functions ------------------------------------------------

def _sh(x):
    return (math.exp(x) - math.exp(-x)) / 2.0

def _ch(x):
    return (math.exp(x) + math.exp(-x)) / 2.0

def _th(x):
    if x > 350.0:
        return 1.0
    if x < -350.0:
        return -1.0
    e2 = math.exp(2.0 * x)
    return (e2 - 1.0) / (e2 + 1.0)

def _ash(u):
    v = math.log(abs(u) + math.sqrt(u * u + 1.0))
    return v if u >= 0 else -v

def t_hyp_six(x):
    s = _sh(x)
    c = _ch(x)
    t = _th(x)
    out = ['sinh x = ' + _f(s), 'cosh x = ' + _f(c), 'tanh x = ' + _f(t),
           'sech x = ' + _f(1.0 / c)]
    if abs(s) < 1e-12:
        out.append(_wn('cosech and coth undefined at 0'))
    else:
        out.append('cosech x = ' + _f(1.0 / s))
        out.append('coth x = ' + _f(c / s))
    out.append(_w('sinh x = (e^x - e^-x)/2'))
    out.append(_w('cosh x = (e^x + e^-x)/2'))
    out.append(_w('cosh^2 x - sinh^2 x = ' + _f(c * c - s * s)))
    return out

def t_hyp_inv(x):
    out = []
    out.append('arsinh x = ' + _f(_ash(x)))
    out.append(_w('arsinh x = ln(x + sqrt(x^2+1))'))
    out.append(_w('  = ln(' + _f(x) + ' + ' + _f(math.sqrt(x * x + 1.0)) + ')'))
    if x >= 1.0:
        vc = math.log(x + math.sqrt(x * x - 1.0))
        out.append('arcosh x = ' + _f(vc))
        out.append(_w('arcosh x = ln(x + sqrt(x^2-1))'))
        out.append(_w('  = ln(' + _f(x) + ' + ' + _f(math.sqrt(x * x - 1.0)) + ')'))
    else:
        out.append(_wn('arcosh needs x >= 1'))
    if -1.0 < x < 1.0:
        vt = 0.5 * math.log((1.0 + x) / (1.0 - x))
        out.append('artanh x = ' + _f(vt))
        out.append(_w('artanh x = (1/2)ln((1+x)/(1-x))'))
    else:
        out.append(_wn('artanh needs |x| < 1'))
    return out

def _usurd(c, rt, den, sgn):
    s = _f(c) + (' + ' if sgn > 0 else ' - ') + _f(rt)
    if abs(den - 1.0) < 1e-12:
        return s
    return '(' + s + ')/' + _f(den)

def t_hyp_solve(a, b, c):
    # a cosh x + b sinh x = c, via u = e^x: (a+b)u^2 - 2c u + (a-b) = 0
    if abs(a) < 1e-12 and abs(b) < 1e-12:
        raise ValueError('a and b are both zero')
    out = []
    roots = []
    if abs(a + b) < 1e-12:
        if abs(c) < 1e-12:
            raise ValueError('no solution')
        u = (a - b) / (2.0 * c)
        roots.append((u, _f(u)))
        out.append(_w('a+b = 0, so -2c u + (a-b) = 0'))
    else:
        disc = c * c - a * a + b * b
        out.append(_w('(a+b)u^2 - 2c u + (a-b) = 0, u = e^x'))
        out.append(_w('disc/4 = c^2 - a^2 + b^2 = ' + _f(disc)))
        if disc < -1e-12:
            return ['no real solutions', _wn('c^2 - a^2 + b^2 < 0')] + out
        if disc < 0:
            disc = 0.0
        rt = math.sqrt(disc)
        den = a + b
        if rt < 1e-12:
            roots.append((c / den, _f(c / den)))
        else:
            roots.append(((c + rt) / den, _usurd(c, rt, den, 1)))
            roots.append(((c - rt) / den, _usurd(c, rt, den, -1)))
    ans = []
    for u, us in roots:
        if u > 1e-300:
            ans.append(('x = ln(' + us + ')', math.log(u)))
        else:
            out.append(_wn('u = ' + _f(u) + ' rejected, e^x > 0'))
    if not ans:
        return ['no real solutions'] + out
    head = []
    for s, v in ans:
        head.append(s)
        head.append('  = ' + _f(v))
    return head + out

def t_hyp_ident(x):
    s = _sh(x)
    c = _ch(x)
    t = _th(x)
    out = ['cosh^2-sinh^2 = ' + _f(c * c - s * s)]
    out.append('sech^2 = ' + _f(1.0 / (c * c)) + ', 1-tanh^2 = ' + _f(1.0 - t * t))
    out.append('cosh2x = ' + _f(_ch(2.0 * x)) + ', c^2+s^2 = ' + _f(c * c + s * s))
    out.append('sinh2x = ' + _f(_sh(2.0 * x)) + ', 2sc = ' + _f(2.0 * s * c))
    out.append('tanh x = ' + _f(t) + ', s/c = ' + _f(s / c))
    if abs(s) < 1e-12:
        out.append(_wn('cosech and coth undefined at 0'))
    else:
        out.append('cosech^2 = ' + _f(1.0 / (s * s)) + ', coth^2-1 = ' + _f(c * c / (s * s) - 1.0))
    out.append(_w('x = ' + _f(x)))
    if abs(x) > 18.0:
        out.append(_wn('large |x|: the digits cancel'))
    return out

def t_hyp_diff(f, a):
    var = _ivar(f, 'x')
    d = _dvar(f, var)
    out = [_m(d)]
    if a is not None:
        v = _at(d, a, var)
        if v is None:
            out.append(_wn('derivative undefined at ' + _f(a)))
        else:
            out.append("f'(" + _f(a) + ') = ' + _f(v))
    out.append(_w('f(x) = ' + _ts(f)))
    return out

def t_hyp_int(f, a, b):
    var = _ivar(f, 'x')
    F = _anti(f, var)
    out = []
    if F is None:
        out.append('no elementary integral')
    else:
        out.append(_m(F))
    if a is not None and b is not None:
        val, F2, exact = _exact_int(f, a, b, var)
        if val is None:
            out.append(_wn('cannot integrate over that range'))
        else:
            out.append('int from ' + _f(a) + ' to ' + _f(b) + ' = ' + _f(val))
            if not exact:
                out.append(_wn('definite value found numerically'))
            if _gap(f, a, b, var):
                out.append(_wn(GAPMSG))
    out.append(_w('f(x) = ' + _ts(f)))
    return out

def t_hyp_plot(xmax):
    import plot
    xmax = _pos(xmax, 'xmax')
    trees = [('sinh', X), ('cosh', X), ('tanh', X)]
    plot.run(trees, -xmax, xmax, 'y', 'sinh, cosh, tanh')
    out = ['sinh x: all x, all y, odd',
           'cosh x: all x, y >= 1, even',
           'tanh x: all x, -1 < y < 1, odd']
    out.append(_w('at x = ' + _f(xmax) + ':'))
    out.append(_w('  sinh = ' + _f(_sh(xmax)) + ', cosh = ' + _f(_ch(xmax))))
    out.append(_w('  tanh = ' + _f(_th(xmax))))
    return out

def t_int_arsinh(a, p, q):
    a = _pos(a, 'a')
    val = _ash(q / a) - _ash(p / a)
    F = ('asinh', ('/', X, _nn(a)))
    out = ['integral = ' + _f(val)]
    out.append(_w('int 1/sqrt(x^2+a^2) dx = arsinh(x/a)'))
    out.append(_mw(F))
    out.append(_w('arsinh(' + _f(q / a) + ') - arsinh(' + _f(p / a) + ')'))
    out.append(_w('arsinh t = ln(t + sqrt(t^2+1))'))
    return out

def t_int_arcosh(a, p, q):
    a = _pos(a, 'a')
    lo = p if p < q else q
    if lo < a:
        raise ValueError('need p and q >= a')
    val = math.log(q / a + math.sqrt(q * q / (a * a) - 1.0)) - \
        math.log(p / a + math.sqrt(p * p / (a * a) - 1.0))
    F = ('acosh', ('/', X, _nn(a)))
    out = ['integral = ' + _f(val)]
    out.append(_w('int 1/sqrt(x^2-a^2) dx = arcosh(x/a)'))
    out.append(_mw(F))
    out.append(_w('arcosh(' + _f(q / a) + ') - arcosh(' + _f(p / a) + ')'))
    out.append(_w('arcosh t = ln(t + sqrt(t^2-1))'))
    out.append(_wn('needs x >= a > 0'))
    return out

# ---- D  Differential equations ----------------------------------------------

def _aux(a, b, c):
    if abs(a) < 1e-12:
        raise ValueError('a must not be zero')
    disc = b * b - 4.0 * a * c
    tol = 1e-12 * (b * b + 4.0 * abs(a * c) + 1.0)
    if disc > tol:
        r = math.sqrt(disc)
        return ('r', (-b + r) / (2.0 * a), (-b - r) / (2.0 * a), disc)
    if disc < -tol:
        return ('c', -b / (2.0 * a), math.sqrt(-disc) / (2.0 * a), disc)
    return ('e', -b / (2.0 * a), 0.0, disc)

def _cf_tree(kind, p, q, var='x'):
    V = ('v', var)
    A = ('v', 'A')
    B = ('v', 'B')
    pn = _nn(p)
    qn = _nn(q)
    if kind == 'r':
        return caseng.simplify(('+', ('*', A, ('exp', ('*', pn, V))),
                                     ('*', B, ('exp', ('*', qn, V)))))
    if kind == 'e':
        return caseng.simplify(('*', ('+', A, ('*', B, V)),
                                     ('exp', ('*', pn, V))))
    return caseng.simplify(('*', ('exp', ('*', pn, V)),
                            ('+', ('*', A, ('cos', ('*', qn, V))),
                                  ('*', B, ('sin', ('*', qn, V))))))

def _root_line(kind, p, q):
    if kind == 'r':
        return 'm = ' + _f(p) + ' and ' + _f(q)
    if kind == 'e':
        return 'm = ' + _f(p) + ' (repeated)'
    return 'm = ' + _f(p) + ' +/- ' + _f(q) + ' i'

def _aux_work(a, b, c, disc):
    eq = _lead(a, 'm^2')
    if abs(b) > 1e-12:
        eq += _signed(b, 'm')
    if abs(c) > 1e-12:
        eq += _signed(c, '')
    return [_w('aux: ' + eq + ' = 0'),
            _w('disc = b^2 - 4ac = ' + _f(disc))]

def _fit_ab(kind, p, q, y0, v0):
    if kind == 'r':
        if abs(p - q) < 1e-12:
            return None
        A = (v0 - q * y0) / (p - q)
        return (A, y0 - A)
    if kind == 'e':
        return (y0, v0 - p * y0)
    if abs(q) < 1e-12:
        return None
    return (y0, (v0 - p * y0) / q)

def _sub_ab(tree, A, B):
    t = caseng.subst(tree, 'A', _nn(A))
    t = caseng.subst(t, 'B', _nn(B))
    return _tidy(t)

def _logpart(t):
    if t[0] == 'ln':
        return (t[1], ('n', 1))
    if t[0] == 'neg':
        inner = _logpart(t[1])
        return None if inner is None else (inner[0], caseng.simplify(('neg', inner[1])))
    if t[0] == '*':
        if t[1][0] == 'ln' and not caseng.vars_in(t[2]):
            return (t[1][1], t[2])
        if t[2][0] == 'ln' and not caseng.vars_in(t[1]):
            return (t[2][1], t[1])
    if t[0] == '/' and t[1][0] == 'ln' and not caseng.vars_in(t[2]):
        return (t[1][1], caseng.simplify(('/', ('n', 1), t[2])))
    return None

def _ifactor(t):
    lg = _logpart(t)
    if lg is None:
        return caseng.simplify(('exp', t))
    pw = lg[1]
    if pw[0] == 'n' and pw[1] < 0:
        base = lg[0] if pw[1] == -1 else ('^', lg[0], ('n', -pw[1]))
        return caseng.simplify(('/', ('n', 1), base))
    return caseng.simplify(('^', lg[0], pw))

def _flat_mul(t, out):
    if t[0] == '*':
        _flat_mul(t[1], out)
        _flat_mul(t[2], out)
    else:
        out.append(t)

def _merge_exp(t):
    parts = []
    _flat_mul(t, parts)
    ex = None
    rest = []
    for q in parts:
        if q[0] == 'exp':
            ex = q[1] if ex is None else ('+', ex, q[1])
        else:
            rest.append(q)
    if ex is None:
        return t
    node = ('exp', _tidy(ex))
    for q in rest:
        node = ('*', node, q)
    return caseng.simplify(node)

def t_intfactor(P, Q, x0, y0):
    ip = _anti(P)
    if ip is None:
        raise ValueError('cannot integrate P(x)')
    plain = caseng.strip_abs(ip)
    IF = _ifactor(plain)
    out = ['IF =', _m(IF)]
    prod = _merge_exp(caseng.simplify(('*', IF, Q)))
    try:
        prod = caspoly.cancel(prod)
    except Exception:
        pass
    R = _anti(prod)
    if R is None:
        out.append(_wn('int (IF)Q dx is not elementary'))
        out.append(_w('y = (1/IF) int IF*Q dx'))
        out.append(_w('int P dx = ' + _ts(ip)))
        return out
    gen = _tidy(('/', ('+', R, ('v', 'C')), IF))
    out.append('y =')
    out.append(_m(gen))
    out.append(_w('P = ' + _ts(P) + ',  Q = ' + _ts(Q)))
    out.append(_w('int P dx = ' + _ts(ip)))
    out.append(_w('IF*Q = ' + _ts(prod)))
    out.append(_w('int IF*Q dx = ' + _ts(R)))
    if x0 is not None and y0 is not None:
        rv = _at(R, x0)
        iv = _at(IF, x0)
        if rv is None or iv is None or abs(iv) < 1e-12:
            out.append(_wn('the point is outside the domain'))
        else:
            C = y0 * iv - rv
            out.append('C = ' + _f(C))
            out.append(_m(_tidy(('/', ('+', R, _nn(C)), IF))))
    return out

def t_second_order(a, b, c):
    kind, p, q, disc = _aux(a, b, c)
    out = [_root_line(kind, p, q), _m(_cf_tree(kind, p, q))]
    for ln in _aux_work(a, b, c, disc):
        out.append(ln)
    if kind == 'r':
        out.append(_w('disc > 0: y = A e^(m1 x) + B e^(m2 x)'))
    elif kind == 'e':
        out.append(_w('disc = 0: y = (A + Bx) e^(m x)'))
    else:
        out.append(_w('disc < 0: y = e^(px)(A cos qx + B sin qx)'))
    return out

def t_second_ivp(a, b, c, y0, v0):
    kind, p, q, disc = _aux(a, b, c)
    cf = _cf_tree(kind, p, q)
    ab = _fit_ab(kind, p, q, y0, v0)
    if ab is None:
        raise ValueError('cannot fit A and B')
    out = [_m(_sub_ab(cf, ab[0], ab[1]))]
    out.append('A = ' + _f(ab[0]) + ',  B = ' + _f(ab[1]))
    out.append(_w(_root_line(kind, p, q)))
    out.append(_w('CF: ' + _ts(cf)))
    out.append(_w('y(0) = ' + _f(y0) + ",  y'(0) = " + _f(v0)))
    for ln in _aux_work(a, b, c, disc):
        out.append(ln)
    return out

def _gauss(M, rhs):
    n = len(rhs)
    i = 0
    while i < n:
        piv = i
        k = i
        while k < n:
            if abs(M[k][i]) > abs(M[piv][i]):
                piv = k
            k += 1
        if abs(M[piv][i]) < 1e-12:
            return None
        M[i], M[piv] = M[piv], M[i]
        rhs[i], rhs[piv] = rhs[piv], rhs[i]
        k = 0
        while k < n:
            if k != i:
                fct = M[k][i] / M[i][i]
                j = i
                while j < n:
                    M[k][j] -= fct * M[i][j]
                    j += 1
                rhs[k] -= fct * rhs[i]
            k += 1
        i += 1
    return [rhs[i] / M[i][i] for i in range(n)]

def _poly_coeffs(tree):
    p = caspoly.poly(tree, 'x')
    if p is None:
        raise ValueError('f(x) must be a polynomial in x')
    if not p:
        return [0.0]
    return [r[0] / float(r[1]) for r in p]

def _poly_tree(cs):
    node = None
    i = len(cs) - 1
    while i >= 0:
        v = cs[i]
        if abs(v) > 1e-12:
            av = abs(v)
            if i == 0:
                body = _nn(av)
            else:
                pw = X if i == 1 else ('^', X, ('n', i))
                body = pw if abs(av - 1.0) < 1e-12 else ('*', _nn(av), pw)
            if node is None:
                node = ('neg', body) if v < 0 else body
            else:
                node = ('-', node, body) if v < 0 else ('+', node, body)
        i -= 1
    return ('n', 0) if node is None else caseng.simplify(node)

def _poly_pi(a, b, c, cs):
    n = len(cs) - 1
    bump = 0
    if abs(c) < 1e-12:
        bump = 1
        if abs(b) < 1e-12:
            bump = 2
    size = n + 1
    M = []
    rhs = []
    row = 0
    while row < size:
        r = []
        j = 0
        while j < size:
            p = bump + j
            v = 0.0
            if p == row:
                v += c
            if p - 1 == row:
                v += b * p
            if p - 2 == row:
                v += a * p * (p - 1)
            r.append(v)
            j += 1
        M.append(r)
        rhs.append(cs[row] if row < len(cs) else 0.0)
        row += 1
    sol = _gauss(M, rhs)
    if sol is None:
        return None
    out = []
    i = 0
    while i < bump:
        out.append(0.0)
        i += 1
    for v in sol:
        out.append(v)
    return out

def _pi_out(a, b, c, pit, work, y0=None, v0=None):
    kind, p, q, disc = _aux(a, b, c)
    cf = _cf_tree(kind, p, q)
    pit = _tidy(pit)
    gen = _tidy(('+', cf, pit))
    out = []
    if y0 is not None and v0 is not None:
        # c13 with conditions y(0) = y0, y'(0) = v0: fit A and B to y - PI
        py = _at(pit, 0.0)
        pd = _at(_dvar(pit, 'x'), 0.0)
        ab = None
        if py is not None and pd is not None:
            ab = _fit_ab(kind, p, q, y0 - py, v0 - pd)
        if ab is None:
            raise ValueError('cannot fit A and B')
        out.append(_m(_tidy(('+', _sub_ab(cf, ab[0], ab[1]), pit))))
        out.append('A = ' + _f(ab[0]) + ',  B = ' + _f(ab[1]))
        out.append(_w('general: ' + _ts(gen)))
        out.append(_w('y(0) = ' + _f(y0) + ",  y'(0) = " + _f(v0)))
    else:
        out.append(_m(gen))
    out.append(_w('CF: ' + _ts(cf)))
    out.append(_w('PI: ' + _ts(pit)))
    out.append(_w(_root_line(kind, p, q)))
    for ln in work:
        out.append(_w(ln))
    for ln in _aux_work(a, b, c, disc):
        out.append(ln)
    return out

def t_pi_poly(a, b, c, p, y0, v0):
    _aux(a, b, c)
    cs = _poly_coeffs(p)
    sol = _poly_pi(a, b, c, cs)
    if sol is None:
        raise ValueError('no polynomial PI exists')
    pit = _poly_tree(sol)
    work = ['f(x) = ' + _ts(p)]
    if abs(c) < 1e-12:
        work.append('c = 0, so the trial is raised a degree')
    return _pi_out(a, b, c, pit, work, y0, v0)

def t_pi_exp(a, b, c, k, p, y0, v0):
    _aux(a, b, c)
    ex = ('exp', ('*', ('n', p), X))
    den = a * p * p + b * p + c
    work = ['f(x) = ' + _expstr(k, p)]
    if abs(den) > 1e-12:
        pit = caseng.simplify(('*', _nn(k / den), ex))
        work.append('trial C e^(px): C(ap^2+bp+c) = k')
        work.append('ap^2+bp+c = ' + _f(den))
    else:
        den2 = 2.0 * a * p + b
        if abs(den2) > 1e-12:
            pit = caseng.simplify(('*', ('*', _nn(k / den2), X), ex))
            work.append('p is a root, so trial C x e^(px)')
            work.append('2ap+b = ' + _f(den2))
        else:
            pit = caseng.simplify(('*', ('*', _nn(k / (2.0 * a)), ('^', X, ('n', 2))), ex))
            work.append('p is a repeated root: trial C x^2 e^(px)')
            work.append('2a = ' + _f(2.0 * a))
    return _pi_out(a, b, c, pit, work, y0, v0)

def t_pi_trig(a, b, c, mm, nn, wv, y0, v0):
    _aux(a, b, c)
    if abs(wv) < 1e-12:
        raise ValueError('w must not be zero')
    cw = ('cos', ('*', ('n', wv), X))
    sw = ('sin', ('*', ('n', wv), X))
    u = c - a * wv * wv
    v = b * wv
    det = u * u + v * v
    ang = 'x' if abs(wv - 1.0) < 1e-12 else _f(wv) + 'x'
    work = ['f(x) = ' + _trigrhs(mm, nn, ang)]
    if det > 1e-12 * (1.0 + u * u + v * v):
        P = (mm * u - nn * v) / det
        Q = (mm * v + nn * u) / det
        pit = caseng.simplify(('+', ('*', _nn(P), cw), ('*', _nn(Q), sw)))
        work.append('trial P cos + Q sin')
        work.append('(c-aw^2)P + bwQ = m; -bwP + (c-aw^2)Q = n')
        work.append('c-aw^2 = ' + _f(u) + ', bw = ' + _f(v))
    else:
        P = -nn / (2.0 * a * wv)
        Q = mm / (2.0 * a * wv)
        pit = caseng.simplify(('+', ('*', ('*', _nn(P), X), cw),
                                     ('*', ('*', _nn(Q), X), sw)))
        work.append('wi is a root, so trial x(P cos + Q sin)')
        work.append('2awQ = m, -2awP = n')
    work.append('P = ' + _f(P) + ', Q = ' + _f(Q))
    return _pi_out(a, b, c, pit, work, y0, v0)

def _shm_lines(w, x0, v0):
    T = 2.0 * PI / w
    T_ = ('v', 't')
    out = ['period T = ' + _f(T), 'frequency = ' + _f(1.0 / T)]
    work = [_w("x'' = -w^2 x,  w = " + _f(w)), _w('T = 2pi/w')]
    if x0 is None or v0 is None:
        out.append(_m(caseng.simplify(
            ('+', ('*', ('v', 'C'), ('cos', ('*', _nn(w), T_))),
                  ('*', ('v', 'D'), ('sin', ('*', _nn(w), T_)))))))
        out.append(_wn('give x(0) and v(0) for R and phi'))
        return out + work
    C = x0
    D = v0 / w
    R = math.sqrt(C * C + D * D)
    phi = math.atan2(D, C)
    body = ('*', _nn(w), T_)
    if abs(phi) > 1e-12:
        body = ('-', body, _nn(phi))
    xt = caseng.simplify(('*', _nn(R), ('cos', body)))
    out = ['amplitude R = ' + _f(R), 'period T = ' + _f(T), _m(xt),
           'max speed = ' + _f(R * w),
           'max accel = ' + _f(R * w * w)]
    work.append(_w('C = x(0) = ' + _f(C) + ',  D = v(0)/w = ' + _f(D)))
    work.append(_w('R = sqrt(C^2+D^2), phi = atan2(D, C)'))
    work.append(_w('phi = ' + _f(phi) + ' rad'))
    work.append(_w('v^2 = w^2(R^2 - x^2)'))
    return out + work

def t_shm(w, x0, v0):
    return _shm_lines(_pos(w, 'w'), x0, v0)

def t_hooke_shm(k, m):
    k = _pos(k, 'k')
    m = _pos(m, 'm')
    w = math.sqrt(k / m)
    out = ['w = ' + _f(w), 'period T = ' + _f(2.0 * PI / w),
           'frequency = ' + _f(w / (2.0 * PI))]
    out.append(_w('T = kx and m a = -T give m x\'\' = -k x'))
    out.append(_w("x'' = -(k/m)x, so w^2 = k/m = " + _f(k / m)))
    return out

def t_damping(m, c, k):
    m = _pos(m, 'm')
    k = _pos(k, 'k')
    if c < 0:
        raise ValueError('c must be >= 0')
    kind, p, q, disc = _aux(m, c, k)
    if abs(c) < 1e-12:
        head = 'no damping (SHM)'
    elif kind == 'c':
        head = 'light damping'
    elif kind == 'e':
        head = 'critical damping'
    else:
        head = 'heavy damping'
    out = [head, _root_line(kind, p, q), _m(_cf_tree(kind, p, q, 't'))]
    out.append(_w("m x'' + c x' + k x = 0"))
    out.append(_w('disc = c^2 - 4mk = ' + _f(disc)))
    out.append(_w('c^2 = ' + _f(c * c) + ',  4mk = ' + _f(4.0 * m * k)))
    if abs(c) < 1e-12:
        out.append(_w('oscillates, amplitude constant'))
    elif kind == 'c':
        out.append(_w('oscillates, amplitude decays'))
    elif kind == 'e':
        out.append(_w('fastest return, no overshoot'))
    else:
        out.append(_w('no oscillation'))
    return out

def t_coupled(a, b, c, d, x0, y0):
    tr = a + d
    det = a * d - b * c
    kind, p, q, disc = _aux(1.0, -tr, det)
    xt = _cf_tree(kind, p, q, 't')
    out = []
    if x0 is not None and y0 is not None:
        xp0 = a * x0 + b * y0
        ab = _fit_ab(kind, p, q, x0, xp0)
        if ab is not None:
            xt = _sub_ab(xt, ab[0], ab[1])
    out.append('x =')
    out.append(_m(xt))
    if abs(b) > 1e-12:
        yt = _tidy(('/', ('-', caseng.diff(xt, 't'), ('*', _nn(a), xt)), _nn(b)))
        out.append('y =')
        out.append(_m(yt))
    else:
        out.append(_wn('b = 0: solve dx/dt first, then dy/dt'))
    out.append(_w("x'' - (a+d)x' + (ad-bc)x = 0"))
    out.append(_w('a+d = ' + _f(tr) + ',  ad-bc = ' + _f(det)))
    out.append(_w(_root_line(kind, p, q)))
    out.append(_w('disc = ' + _f(disc)))
    out.append(_w('y = (dx/dt - a x)/b'))
    if x0 is not None and y0 is not None:
        out.append(_w('x(0) = ' + _f(x0) + ',  y(0) = ' + _f(y0)))
    return out

def _onlyv(tree, var, what):
    for v in caseng.vars_in(tree):
        if v != var:
            raise ValueError(what + ': type it in ' + var)

def _eqlines(lhs, rhs):
    s = lhs + ' = ' + rhs
    if len(s) <= 36:
        return [s]
    return [lhs + ' =', '  ' + rhs]

def t_separable(f, g, x0, y0):
    # c8: dy/dx = f(x) g(y)
    _onlyv(f, 'x', 'f(x)')
    _onlyv(g, 'y', 'g(y)')
    A = _anti(caseng.simplify(('/', ('n', 1), g)), 'y')
    B = _anti(f, 'x')
    if A is None or B is None:
        raise ValueError('no standard integral')
    work = [_w('dy/dx = f(x) g(y): int dy/g(y) = int f(x) dx'),
            _w('int 1/g(y) dy = ' + _ts(A)),
            _w('int f(x) dx = ' + _ts(B))]
    if x0 is None or y0 is None:
        return _eqlines(_ts(A), _ts(B) + ' + c') + work
    a0 = _at(A, y0, 'y')
    b0 = _at(B, x0, 'x')
    if a0 is None or b0 is None:
        raise ValueError('the point is outside the domain')
    c = a0 - b0
    ct = _nn(c)
    try:
        t2 = _tidy(('-', caseng.subst(A, 'y', _nn(y0)), caseng.subst(B, 'x', _nn(x0))))
        v2 = _at(t2, 0.0)
        if v2 is not None and abs(v2 - c) < 1e-9 * (1.0 + abs(c)):
            ct = t2
    except Exception:
        pass
    if abs(c) < 1e-12:
        rhs = _ts(B)
        ct = ('n', 0)
    else:
        rhs = _ts(B) + ' + ' + _ts(ct)
        if rhs.startswith(_ts(B) + ' + -'):
            rhs = _ts(B) + ' - ' + rhs[len(_ts(B)) + 4:]
    out = _eqlines(_ts(A), rhs)
    Ap = caseng.strip_abs(A)
    inv = None
    try:
        inv = caseng.invert(Ap, 'y', 'u')
    except Exception:
        inv = None
    if inv is not None:
        ex = _tidy(caseng.subst(inv, 'u', caseng.simplify(('+', B, ct))))
        yv = _at(ex, x0)
        if yv is not None and abs(yv - y0) < 1e-6 * (1.0 + abs(y0)):
            out = ['y ='] + [_m(ex)] + [_w(ln) for ln in out]
            if Ap != A:
                out.append(_wn('y keeps the sign it has at x0'))
    out.append(_w('c = ' + _ts(ct) + ' from (' + _f(x0) + ', ' + _f(y0) + ')'))
    return out + work

def t_avdx(f, x0, v0, x1):
    # p21/p22: a = v dv/dx = f(x), with v = v0 at x = x0
    _onlyv(f, 'x', 'f(x)')
    F = _anti(f)
    if F is None:
        raise ValueError('cannot integrate f(x)')
    F0 = _at(F, x0)
    if F0 is None:
        raise ValueError('int f dx is undefined at x0')
    V2 = _tidy(('+', _nn(v0 * v0 - 2.0 * F0), ('*', ('n', 2), F)))
    out = ['v^2 =', _m(V2)]
    if x1 is not None:
        w2 = _at(V2, x1)
        if w2 is None:
            out.append(_wn('v^2 is undefined at x = ' + _f(x1)))
        elif w2 < -1e-9:
            out.append('x = ' + _f(x1) + ' is never reached')
            out.append(_wn('v^2 = ' + _f(w2) + ' < 0 there'))
        else:
            vv = math.sqrt(w2) if w2 > 0 else 0.0
            if vv == 0:
                out.append('at x = ' + _f(x1) + ': v = 0')
            else:
                out.append('at x = ' + _f(x1) + ': v = +/-' + _f(vv))
    zs = []
    try:
        for r in cascalc.solve(V2, 'x'):
            zs.append(0.0 if abs(r) < 1e-6 else r)
    except Exception:
        zs = []
    if zs:
        out.append('v = 0 at x = ' + ', '.join([_f(r) for r in zs[:4]]))
    out.append(_w('a = v dv/dx = d(v^2/2)/dx'))
    out.append(_w('v^2/2 = int f dx + c, int f dx = ' + _ts(F)[:22]))
    out.append(_w('v = ' + _f(v0) + ' at x = ' + _f(x0) + ' fixes c'))
    return out

def t_afv(f, v0, v1):
    # p22: a = f(v); time and distance for v to go from v0 to v1
    _onlyv(f, 'v', 'f(v)')
    if v0 == v1:
        raise ValueError('v0 and v1 are equal')
    lo = v0 if v0 < v1 else v1
    hi = v1 if v0 < v1 else v0
    sg = None
    i = 0
    while i <= 40:
        fv = _at(f, lo + (hi - lo) * i / 40.0, 'v')
        if fv is None:
            raise ValueError('f(v) is undefined between v0 and v1')
        s = 0 if abs(fv) < 1e-12 else (1 if fv > 0 else -1)
        if s == 0 or (sg is not None and s != sg):
            return ['v never reaches ' + _f(v1),
                    _wn('f(v) = 0 between: a terminal speed'),
                    _w('the time integral int dv/f(v) diverges')]
        sg = s
        i += 1
    it = caseng.simplify(('/', ('n', 1), f))
    ix = caseng.simplify(('/', ('v', 'v'), f))
    tv, Ft, e1 = _exact_int(it, v0, v1, 'v')
    xv, Fx, e2 = _exact_int(ix, v0, v1, 'v')
    if tv is None or xv is None:
        raise ValueError('cannot integrate over that range')
    out = ['time = ' + _f(tv), 'distance = ' + _f(xv)]
    if tv < 0:
        out.append(_wn('time < 0: a pushes v away from v1'))
    out.append(_w('dv/dt = f(v): t = int dv/f(v)'))
    if Ft is not None:
        out.append(_mw(Ft))
    out.append(_w('v dv/dx = f(v): x = int v/f(v) dv'))
    if Fx is not None:
        out.append(_mw(Fx))
    out.append(_w('from v = ' + _f(v0) + ' to v = ' + _f(v1)))
    if not (e1 and e2):
        out.append(_wn('found numerically'))
    return out

SECTIONS = [
    # Pc1 c2 c3 c4 c5 c6
    ('C', 'Calculus', [
        ('Integral to infinity', 'f(x),a', t_int_inf),
        ('Singular endpoint int', 'f(x),a,b', t_int_sing),
        ('Volume about x-axis', 'f(x),a,b', t_vol_x),
        ('Volume about y-axis', 'g(y),c,d', t_vol_y),
        ('Mean value of f', 'f(x),a,b', t_mean),
        ('Integrate by partials', 'p(x),q(x)', t_partial_int),
        ('d/dx inverse trig', 'f(x),a?', t_invtrig_diff),
        ('Int 1/sqrt(a2-x2)', 'a,p,q', t_int_asin),
        ('Int 1/(a2+x2)', 'a,p,q', t_int_atan),
    ]),
    # PP1 P2 P3
    ('PO', 'Polar coordinates', [
        ('Polar to cartesian', 'r,theta', t_polar_to_xy),
        ('Cartesian to polar', 'x,y', t_xy_to_polar),
        ('Plot r = f(theta)', 'r(x)', t_polar_plot),
        ('Polar area', 'r(x),a,b', t_polar_area),
    ]),
    # Pa3 a4 a5 Pa6 a7 a8
    ('H', 'Hyperbolic functions', [
        ('Six hyperbolics at x', 'x', t_hyp_six),
        ('Inverse hyperbolics', 'x', t_hyp_inv),
        ('Solve a cosh+b sinh=c', 'a,b,c', t_hyp_solve),
        ('Identity check at x', 'x', t_hyp_ident),
        ('Plot sinh cosh tanh', 'xmax', t_hyp_plot),
        ('d/dx hyperbolic', 'f(x),a?', t_hyp_diff),
        ('Integrate hyperbolic', 'f(x),a?,b?', t_hyp_int),
        ('Int 1/sqrt(x2+a2)', 'a,p,q', t_int_arsinh),
        ('Int 1/sqrt(x2-a2)', 'a,p,q', t_int_arcosh),
    ]),
    # c8 c9 c10 c11-c14 c16-c18 Pc7 Pc15 p21 p22 (Pp19 p20 are modelling)
    ('D', 'Differential equations', [
        ('Separable DE', 'f(x),g(y),x0?,y0?', t_separable),
        ('Integrating factor', 'P(x),Q(x),x0?,y0?', t_intfactor),
        ('Second order homogen', 'a,b,c', t_second_order),
        ('Second order with IVs', 'a,b,c,y0,v0', t_second_ivp),
        ('PI polynomial RHS', 'a,b,c,p(x),y0?,v0?', t_pi_poly),
        ('PI for k e^(px)', 'a,b,c,k,p,y0?,v0?', t_pi_exp),
        ('PI for m cos + n sin', 'a,b,c,m,n,omega,y0?,v0?', t_pi_trig),
        ('SHM from omega', 'omega,x0?,v0?', t_shm),
        ('Hooke law SHM', 'k,m', t_hooke_shm),
        ('Damping classify', 'm,c,k', t_damping),
        ('Coupled equations', 'a,b,c,d,x0?,y0?', t_coupled),
        ('a = v dv/dx = f(x)', 'f(x),x0,v0,x1?', t_avdx),
        ('a = f(v): dist, time', 'f(v),v0,v1', t_afv),
    ]),
]
