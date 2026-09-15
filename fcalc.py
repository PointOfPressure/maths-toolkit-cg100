# AQA Further Maths 7367, sections E-J: further calculus, further vectors,
# polar coordinates, hyperbolic functions, differential equations and
# numerical methods.
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

def _refine(tree, a, b, var='x'):
    # (value at 800 panels, |change on halving h|)
    v1 = _num(tree, a, b, var, 200)
    v2 = _num(tree, a, b, var, 800)
    if v1 is None or v2 is None:
        return (v2, None)
    return (v2, abs(v2 - v1))

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

def _snap(v):
    return 0.0 if -1e-7 < v < 1e-7 else v

def _sq(t):
    return caseng.simplify(('^', t, ('n', 2)))

def _pos(v, name):
    if v is None or v <= 0:
        raise ValueError(name + ' must be > 0')
    return v

def _int_in(v, lo, hi, name):
    k = int(round(v))
    if k < lo or k > hi:
        raise ValueError(name + ' from ' + str(lo) + ' to ' + str(hi))
    return k

# ---- E further calculus -----------------------------------------------------

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

def _arc_lines(integ, a, b, var, head):
    val, diff = _refine(integ, a, b, var)
    if val is None:
        raise ValueError('integrand undefined in that range')
    out = ['s = ' + casutil.sf3(val)]
    sym = _anti(integ, var)
    if sym is not None:
        ex = _exact_int(integ, a, b, var)
        if ex[2]:
            out = ['s = ' + _f(ex[0])]
            out.append(_mw(sym))
    for ln in head:
        out.append(_w(ln))
    out.append(_w('from ' + _f(a) + ' to ' + _f(b)))
    if diff is not None:
        out.append(_w('change on halving h = ' + _f(diff, 3)))
    return out

def t_arclen(f, a, b):
    a, b = _order(a, b)
    var = _ivar(f, 'x')
    d = _dvar(f, var)
    integ = ('sqrt', ('+', ('n', 1), _sq(d)))
    return _arc_lines(integ, a, b, var,
                      ['s = int sqrt(1 + (dy/dx)^2) dx',
                       'dy/dx = ' + _ts(d)])

def _par_var(xt, yt):
    vs = caseng.vars_in(xt) + caseng.vars_in(yt)
    if 't' in vs or not vs:
        return 't'
    if 'x' in vs:
        return 'x'
    return vs[0]

def t_arclen_par(xt, yt, a, b):
    a, b = _order(a, b)
    var = _par_var(xt, yt)
    dx = _dvar(xt, var)
    dy = _dvar(yt, var)
    integ = ('sqrt', ('+', _sq(dx), _sq(dy)))
    return _arc_lines(integ, a, b, var,
                      ["s = int sqrt(x'^2 + y'^2) dt",
                       "dx/dt = " + _ts(dx),
                       "dy/dt = " + _ts(dy)])

def _surf_lines(integ, a, b, var, head):
    val, diff = _refine(integ, a, b, var)
    ex = _exact_int(integ, a, b, var)
    if ex[2]:
        val = ex[0]
        diff = None
    if val is None:
        raise ValueError('integrand undefined in that range')
    s = 2.0 * PI * val
    out = ['S = ' + _f(s)]
    if _f(s) != casutil.sf3(s):
        out.append('  = ' + casutil.sf3(s))
    for ln in head:
        out.append(_w(ln))
    out.append(_w('int part = ' + _f(val, 6) + ', ' + _f(a) + ' to ' + _f(b)))
    if diff is not None:
        out.append(_w('change on halving h = ' + _f(diff, 3)))
    return out

def t_surf_x(f, a, b):
    a, b = _order(a, b)
    var = _ivar(f, 'x')
    d = _dvar(f, var)
    integ = ('*', f, ('sqrt', ('+', ('n', 1), _sq(d))))
    return _surf_lines(integ, a, b, var,
                       ['S = 2pi int y sqrt(1 + (dy/dx)^2) dx',
                        'dy/dx = ' + _ts(d)])

def t_surf_par(xt, yt, a, b):
    a, b = _order(a, b)
    var = _par_var(xt, yt)
    dx = _dvar(xt, var)
    dy = _dvar(yt, var)
    integ = ('*', yt, ('sqrt', ('+', _sq(dx), _sq(dy))))
    return _surf_lines(integ, a, b, var,
                       ["S = 2pi int y sqrt(x'^2 + y'^2) dt",
                        "dx/dt = " + _ts(dx),
                        "dy/dt = " + _ts(dy)])

# ---- E reduction formulae ---------------------------------------------------

def _frac(r):
    if r[0] == 0:
        return '0'
    if r[1] == 1:
        return str(r[0])
    return str(r[0]) + '/' + str(r[1])

def _cfrac(r, name):
    p = r[0]
    sgn = '-' if p < 0 else ''
    if p < 0:
        p = -p
    top = name if p == 1 else str(p) + name
    return sgn + top + ('' if r[1] == 1 else '/' + str(r[1]))

def _exstr(ra, rb, name):
    parts = []
    if ra[0] != 0:
        parts.append(_frac(ra))
    if rb[0] != 0:
        parts.append(_cfrac(rb, name))
    if not parts:
        return '0'
    if len(parts) == 2 and parts[0][0] == '-' and parts[1][0] != '-':
        parts = [parts[1], parts[0]]
    s = parts[0]
    i = 1
    while i < len(parts):
        p = parts[i]
        s = s + (' - ' + p[1:] if p[0] == '-' else ' + ' + p)
        i += 1
    return s

def _exval(ra, rb, c):
    return ra[0] / float(ra[1]) + rb[0] / float(rb[1]) * c

def _red_out(n, rows, name, c, head):
    ra, rb = rows[len(rows) - 1][1], rows[len(rows) - 1][2]
    val = _exval(ra, rb, c)
    ex = _exstr(ra, rb, name)
    out = []
    if len(ex) <= 26:
        out.append('I_' + str(n) + ' = ' + ex)
        if ex != casutil.sf3(val):
            out.append('    = ' + casutil.sf3(val))
    else:
        out.append('I_' + str(n) + ' = ' + casutil.sf3(val))
    for ln in head:
        out.append(_w(ln))
    for k, a2, b2 in rows:
        v2 = _exval(a2, b2, c)
        e2 = _exstr(a2, b2, name)
        if len(e2) > 22:
            out.append(_w('  I_' + str(k) + ' = ' + _f(v2, 6)))
        else:
            out.append(_w('  I_' + str(k) + ' = ' + e2 + ' = ' + _f(v2, 6)))
    return out

def _red_estep(n):
    # I_n = e - n I_(n-1), I_0 = e - 1;  I_n = ra + rb*e
    ra = (-1, 1)
    rb = (1, 1)
    rows = [(0, ra, rb)]
    k = 1
    while k <= n:
        ra = caspoly.rmul((-k, 1), ra)
        rb = caspoly.rsub((1, 1), caspoly.rmul((k, 1), rb))
        rows.append((k, ra, rb))
        k += 1
    return rows

def t_red_xexp(n):
    n = _int_in(n, 0, 12, 'n')
    rows = _red_estep(n)
    return _red_out(n, rows, 'e', E,
                    ['I_n = int x^n e^x dx, 0 to 1',
                     'I_n = e - n I_(n-1),  I_0 = e - 1'])

def t_red_lnx(n):
    n = _int_in(n, 0, 12, 'n')
    rows = _red_estep(n)
    return _red_out(n, rows, 'e', E,
                    ['I_n = int (ln x)^n dx, 1 to e',
                     'I_n = e - n I_(n-1),  I_0 = e - 1'])

def _red_wallis(n):
    # int sin^n or cos^n over 0..pi/2;  I_n = ra + rb*pi
    if n % 2:
        ra, rb, k = (1, 1), (0, 1), 1
    else:
        ra, rb, k = (0, 1), (1, 2), 0
    rows = [(k, ra, rb)]
    k += 2
    while k <= n:
        fac = (k - 1, k)
        ra = caspoly.rmul(fac, ra)
        rb = caspoly.rmul(fac, rb)
        rows.append((k, ra, rb))
        k += 2
    return rows

def t_red_sin(n):
    n = _int_in(n, 0, 20, 'n')
    return _red_out(n, _red_wallis(n), 'pi', PI,
                    ['I_n = int sin^n x dx, 0 to pi/2',
                     'I_n = ((n-1)/n) I_(n-2)',
                     'I_0 = pi/2,  I_1 = 1'])

def t_red_cos(n):
    n = _int_in(n, 0, 20, 'n')
    return _red_out(n, _red_wallis(n), 'pi', PI,
                    ['I_n = int cos^n x dx, 0 to pi/2',
                     'I_n = ((n-1)/n) I_(n-2)',
                     'I_0 = pi/2,  I_1 = 1'])

def t_red_tan(n):
    n = _int_in(n, 0, 20, 'n')
    if n % 2:
        ra, rb, k, name, c = (0, 1), (1, 2), 1, 'ln2', math.log(2.0)
    else:
        ra, rb, k, name, c = (0, 1), (1, 4), 0, 'pi', PI
    rows = [(k, ra, rb)]
    k += 2
    while k <= n:
        ra = caspoly.rsub((1, k - 1), ra)
        rb = caspoly.rneg(rb)
        rows.append((k, ra, rb))
        k += 2
    return _red_out(n, rows, name, c,
                    ['I_n = int tan^n x dx, 0 to pi/4',
                     'I_n = 1/(n-1) - I_(n-2)',
                     'I_0 = pi/4,  I_1 = (ln 2)/2'])

def t_lim_xexp(k):
    k = _pos(k, 'k')
    out = ['limit = 0']
    out.append(_w('x^k e^-x as x -> infinity, k = ' + _f(k)))
    xs = [1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
    for xv in xs:
        v = math.exp(k * math.log(xv) - xv)
        out.append(_w('  x = ' + _f(xv) + ':  ' + _f(v, 4)))
    out.append(_w('e^x beats every power of x'))
    return out

def t_lim_xlnx(k):
    k = _pos(k, 'k')
    out = ['limit = 0']
    out.append(_w('x^k ln x as x -> 0+, k = ' + _f(k)))
    xs = [0.1, 0.01, 1e-3, 1e-4, 1e-6, 1e-8]
    for xv in xs:
        v = math.exp(k * math.log(xv)) * math.log(xv)
        out.append(_w('  x = ' + _f(xv, 3) + ':  ' + _f(v, 4)))
    out.append(_w('x^k beats ln x at 0'))
    return out

# ---- F further vectors ------------------------------------------------------

def _sub3(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def _dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _cross3(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]

def _mag3(a):
    return math.sqrt(_dot3(a, a))

def _step(a, d, t):
    return [a[0] + t * d[0], a[1] + t * d[1], a[2] + t * d[2]]

def _nonzero(v, name):
    if _mag3(v) < 1e-12:
        raise ValueError(name + ' is the zero vector')
    return v

def _ints(vals):
    out = []
    for c in vals:
        k = int(round(c))
        if abs(c - k) > 1e-9:
            return None
        out.append(k)
    return out

def _simp_vec(v):
    iv = _ints(v)
    if iv is None:
        return v
    g = 0
    for c in iv:
        g = casutil.gcd(g, c)
    if g <= 1:
        return iv
    return [c // g for c in iv]

def _simp_plane(n, d):
    iv = _ints([n[0], n[1], n[2], d])
    if iv is None:
        return (n, d)
    g = 0
    for c in iv:
        g = casutil.gcd(g, c)
    if g <= 1:
        return (n, d)
    return ([iv[0] // g, iv[1] // g, iv[2] // g], iv[3] // g)

def _angle_lines(c):
    r = casutil.acos_safe(c)
    return ['angle = ' + _f(r) + ' rad',
            '      = ' + _f(casutil.deg(r)) + ' deg']

def _cart_line(a, d):
    names = ('x', 'y', 'z')
    parts = []
    fixed = []
    i = 0
    while i < 3:
        if abs(d[i]) > 1e-12:
            top = names[i]
            if abs(a[i]) > 1e-12:
                top = '(' + names[i] + (' - ' if a[i] > 0 else ' + ') + _f(abs(a[i])) + ')'
            if abs(d[i] - 1.0) < 1e-12:
                parts.append(top)
            elif d[i] < 0:
                parts.append(top + '/(' + _f(d[i]) + ')')
            else:
                parts.append(top + '/' + _f(d[i]))
        else:
            fixed.append(names[i] + ' = ' + _f(a[i]))
        i += 1
    out = []
    if parts:
        out.append(' = '.join(parts))
    for s in fixed:
        out.append(s)
    return out

def _plane_lines(n, d):
    n, d = _simp_plane(n, d)
    names = ('x', 'y', 'z')
    s = ''
    i = 0
    while i < 3:
        c = n[i]
        if abs(c) > 1e-12:
            if s == '':
                s = ('-' if c < 0 else '') + ('' if abs(abs(c) - 1.0) < 1e-12 else _f(abs(c))) + names[i]
            else:
                s = s + (' - ' if c < 0 else ' + ') + ('' if abs(abs(c) - 1.0) < 1e-12 else _f(abs(c))) + names[i]
        i += 1
    return ['r.' + _fv(n) + ' = ' + _f(d), s + ' = ' + _f(d)]

def t_line_2pts(A, B):
    d = _nonzero(_sub3(B, A), 'B - A')
    d = _simp_vec(d)
    out = ['r = ' + _fv(A) + ' + t' + _fv(d)]
    for s in _cart_line(A, d):
        out.append(s)
    out.append(_w('direction = B - A'))
    out.append(_w('|d| = ' + _f(_mag3(d))))
    return out

def t_line_cart(a, d):
    _nonzero(d, 'd')
    d = _simp_vec(d)
    out = ['r = ' + _fv(a) + ' + t' + _fv(d)]
    for s in _cart_line(a, d):
        out.append(s)
    out.append(_w('|d| = ' + _f(_mag3(d))))
    return out

def t_plane_3pts(A, B, C):
    n = _cross3(_sub3(B, A), _sub3(C, A))
    if _mag3(n) < 1e-12:
        raise ValueError('the three points are collinear')
    n = _simp_vec(n)
    d = _dot3(n, A)
    out = _plane_lines(n, d)
    out.append(_w('n = (B-A) x (C-A) = ' + _fv(n)))
    out.append(_w('d = n.A = ' + _f(d)))
    return out

def t_plane_pt_n(p, n):
    _nonzero(n, 'n')
    d = _dot3(n, p)
    out = _plane_lines(n, d)
    out.append(_w('d = n.p = ' + _f(d)))
    out.append(_w('|n| = ' + _f(_mag3(n))))
    return out

def t_angle_lines(d1, d2):
    _nonzero(d1, 'd1')
    _nonzero(d2, 'd2')
    dp = _dot3(d1, d2)
    c = abs(dp) / (_mag3(d1) * _mag3(d2))
    out = _angle_lines(c)
    out.append(_w('cos = |d1.d2|/(|d1||d2|) = ' + _f(c)))
    out.append(_w('d1.d2 = ' + _f(dp)))
    return out

def t_angle_lp(d, n):
    _nonzero(d, 'd')
    _nonzero(n, 'n')
    s = abs(_dot3(d, n)) / (_mag3(d) * _mag3(n))
    if s > 1.0:
        s = 1.0
    r = math.asin(s)
    out = ['angle = ' + _f(r) + ' rad',
           '      = ' + _f(casutil.deg(r)) + ' deg']
    out.append(_w('sin = |d.n|/(|d||n|) = ' + _f(s)))
    out.append(_w('d.n = ' + _f(_dot3(d, n))))
    return out

def t_angle_planes(n1, n2):
    _nonzero(n1, 'n1')
    _nonzero(n2, 'n2')
    dp = _dot3(n1, n2)
    c = abs(dp) / (_mag3(n1) * _mag3(n2))
    out = _angle_lines(c)
    out.append(_w('cos = |n1.n2|/(|n1||n2|) = ' + _f(c)))
    out.append(_w('n1.n2 = ' + _f(dp)))
    return out

def t_perp_check(a, b):
    _nonzero(a, 'a')
    _nonzero(b, 'b')
    dp = _dot3(a, b)
    cr = _cross3(a, b)
    scale = _mag3(a) * _mag3(b)
    out = ['perpendicular' if abs(dp) < 1e-9 * scale else 'not perpendicular']
    out.append('parallel' if _mag3(cr) < 1e-9 * scale else 'not parallel')
    out.append(_w('a.b = ' + _f(dp)))
    out.append(_w('a x b = ' + _fv(cr)))
    return out

def t_cross(a, b):
    cr = _cross3(a, b)
    out = ['a x b = ' + _fv(cr), '|a x b| = ' + _f(_mag3(cr))]
    out.append(_w('a.b = ' + _f(_dot3(a, b))))
    return out

def t_tri_area(A, B, C):
    cr = _cross3(_sub3(B, A), _sub3(C, A))
    area = 0.5 * _mag3(cr)
    out = ['area = ' + _f(area)]
    out.append(_w('area = 0.5|(B-A) x (C-A)|'))
    out.append(_w('(B-A) x (C-A) = ' + _fv(cr)))
    return out

def t_on_line(a, b, p):
    _nonzero(b, 'b')
    cr = _cross3(_sub3(p, a), b)
    scale = _mag3(_sub3(p, a)) * _mag3(b) + 1.0
    on = _mag3(cr) < 1e-9 * scale
    out = ['p is on the line' if on else 'p is not on the line']
    if on:
        t = _dot3(_sub3(p, a), b) / _dot3(b, b)
        out.append('t = ' + _f(t))
    out.append(_w('(r-a) x b = 0 defines the line'))
    out.append(_w('(p-a) x b = ' + _fv(cr)))
    return out

def _line_pair(a1, d1, a2, d2):
    _nonzero(d1, 'd1')
    _nonzero(d2, 'd2')
    cr = _cross3(d1, d2)
    wv = _sub3(a2, a1)
    mc = _mag3(cr)
    scale = _mag3(d1) * _mag3(d2)
    if mc < 1e-9 * scale:
        dist = _mag3(_cross3(wv, d1)) / _mag3(d1)
        if dist < 1e-9 * (1.0 + _mag3(wv)):
            return ('same', 0.0, cr)
        return ('par', dist, cr)
    dist = abs(_dot3(wv, cr)) / mc
    t = _dot3(_cross3(wv, d2), cr) / (mc * mc)
    s = _dot3(_cross3(wv, d1), cr) / (mc * mc)
    if dist < 1e-9 * (1.0 + _mag3(wv) + _mag3(d1) + _mag3(d2)):
        return ('meet', (t, s, _step(a1, d1, t)), cr)
    return ('skew', (dist, t, s), cr)

def t_line_meet(a1, d1, a2, d2):
    kind, info, cr = _line_pair(a1, d1, a2, d2)
    out = []
    if kind == 'same':
        out.append('the same line')
    elif kind == 'par':
        out.append('parallel, no intersection')
        out.append('distance = ' + _f(info))
    elif kind == 'meet':
        t, s, p = info
        out.append('they meet at ' + _fv(p))
        out.append(_w('t = ' + _f(t) + ',  s = ' + _f(s)))
    else:
        dist, t, s = info
        out.append('skew lines')
        out.append('distance = ' + _f(dist))
        out.append(_w('nearest on line 1: ' + _fv(_step(a1, d1, t))))
        out.append(_w('nearest on line 2: ' + _fv(_step(a2, d2, s))))
    out.append(_w('d1 x d2 = ' + _fv(cr)))
    out.append(_w('a2 - a1 = ' + _fv(_sub3(a2, a1))))
    return out

def t_line_dist(a1, d1, a2, d2):
    kind, info, cr = _line_pair(a1, d1, a2, d2)
    out = []
    if kind == 'same':
        out.append('the same line')
        out.append('distance = 0')
    elif kind == 'par':
        out.append('parallel lines')
        out.append('distance = ' + _f(info))
        out.append(_w('d = |(a2-a1) x d1|/|d1|'))
    elif kind == 'meet':
        out.append('lines intersect')
        out.append('distance = 0')
        out.append(_w('meet at ' + _fv(info[2])))
    else:
        out.append('skew lines')
        out.append('distance = ' + _f(info[0]))
        out.append(_w('d = |(a2-a1).(d1 x d2)|/|d1 x d2|'))
    out.append(_w('d1 x d2 = ' + _fv(cr)))
    return out

def t_line_plane(a, d, n, k):
    _nonzero(d, 'd')
    _nonzero(n, 'n')
    nd = _dot3(n, d)
    na = _dot3(n, a)
    out = []
    if abs(nd) < 1e-12 * _mag3(n) * _mag3(d):
        if abs(na - k) < 1e-9 * (1.0 + abs(k)):
            out.append('the line lies in the plane')
        else:
            out.append('parallel, never meets')
            out.append('distance = ' + _f(abs(na - k) / _mag3(n)))
    else:
        t = (k - na) / nd
        p = _step(a, d, t)
        out.append('meets at ' + _fv(p))
        out.append(_w('t = (k - n.a)/(n.d) = ' + _f(t)))
        s = abs(nd) / (_mag3(n) * _mag3(d))
        if s > 1.0:
            s = 1.0
        r = math.asin(s)
        out.append('angle = ' + _f(r) + ' rad')
        out.append('      = ' + _f(casutil.deg(r)) + ' deg')
    out.append(_w('n.d = ' + _f(nd) + ',  n.a = ' + _f(na)))
    return out

def t_pt_line(p, a, d):
    _nonzero(d, 'd')
    wv = _sub3(p, a)
    cr = _cross3(wv, d)
    dist = _mag3(cr) / _mag3(d)
    t = _dot3(wv, d) / _dot3(d, d)
    foot = _step(a, d, t)
    out = ['distance = ' + _f(dist), 'foot = ' + _fv(foot)]
    out.append(_w('d = |(p-a) x d|/|d|'))
    out.append(_w('(p-a) x d = ' + _fv(cr)))
    out.append(_w('t = (p-a).d/|d|^2 = ' + _f(t)))
    return out

def t_pt_plane(p, n, k):
    _nonzero(n, 'n')
    mn = _mag3(n)
    gap = _dot3(n, p) - k
    dist = abs(gap) / mn
    foot = [p[i] - gap * n[i] / (mn * mn) for i in range(3)]
    out = ['distance = ' + _f(dist), 'foot = ' + _fv(foot)]
    out.append(_w('d = |n.p - k|/|n|'))
    out.append(_w('n.p = ' + _f(_dot3(n, p)) + ',  |n| = ' + _f(mn)))
    return out

# ---- G polar coordinates ----------------------------------------------------

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

def _polar_tangents(r, a, b, which):
    a, b = _order(a, b)
    body = ('*', r, ('sin', X)) if which == 'para' else ('*', r, ('cos', X))
    d = _dvar(body, 'x')
    tol = 1e-6 * (1.0 + abs(b - a))
    roots = []
    try:
        for t in cascalc.solve(d, 'x'):
            if a - tol <= t <= b + tol:
                roots.append(_snap(t))
    except Exception:
        roots = []
    out = []
    if not roots:
        out.append('none found in that range')
    for t in roots:
        rv = _polar_r(r, t)
        if rv is None:
            continue
        rv = _snap(rv)
        out.append('theta = ' + _f(t) + ', r = ' + _f(rv))
        out.append(_w('  point ' + _fv([_snap(rv * math.cos(t)),
                                        _snap(rv * math.sin(t))])))
    if which == 'para':
        out.append(_w('tangent parallel to the initial line'))
        out.append(_w('when d(r sin th)/dth = 0'))
    else:
        out.append(_w('tangent perpendicular to it'))
        out.append(_w('when d(r cos th)/dth = 0'))
    out.append(_mw(d))
    return out

def t_polar_tan_para(r, a, b):
    return _polar_tangents(r, a, b, 'para')

def t_polar_tan_perp(r, a, b):
    return _polar_tangents(r, a, b, 'perp')

# ---- H hyperbolic functions -------------------------------------------------

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

# ---- I differential equations ------------------------------------------------

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

def _pi_out(a, b, c, pit, work):
    kind, p, q, disc = _aux(a, b, c)
    cf = _cf_tree(kind, p, q)
    pit = _tidy(pit)
    out = [_m(_tidy(('+', cf, pit)))]
    out.append(_w('CF: ' + _ts(cf)))
    out.append(_w('PI: ' + _ts(pit)))
    out.append(_w(_root_line(kind, p, q)))
    for ln in work:
        out.append(_w(ln))
    for ln in _aux_work(a, b, c, disc):
        out.append(ln)
    return out

def t_pi_poly(a, b, c, p):
    _aux(a, b, c)
    cs = _poly_coeffs(p)
    sol = _poly_pi(a, b, c, cs)
    if sol is None:
        raise ValueError('no polynomial PI exists')
    pit = _poly_tree(sol)
    work = ['f(x) = ' + _ts(p)]
    if abs(c) < 1e-12:
        work.append('c = 0, so the trial is raised a degree')
    return _pi_out(a, b, c, pit, work)

def t_pi_exp(a, b, c, k, p):
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
    return _pi_out(a, b, c, pit, work)

def t_pi_trig(a, b, c, mm, nn, wv):
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
    return _pi_out(a, b, c, pit, work)

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

# ---- J numerical methods -----------------------------------------------------

def _strips(f, a, b, n):
    n = _int_in(n, 1, 200, 'n')
    if a == b:
        raise ValueError('limits are equal')
    return (n, (b - a) / n)

def _fx(f, x):
    v = casutil.evx(f, x)
    if v is None:
        raise ValueError('f undefined at x = ' + _f(x))
    return v

def _midord(f, a, b, n, h):
    tot = 0.0
    i = 0
    while i < n:
        tot += _fx(f, a + (i + 0.5) * h)
        i += 1
    return tot * h

def _trap(f, a, b, n, h):
    tot = _fx(f, a) + _fx(f, b)
    i = 1
    while i < n:
        tot += 2.0 * _fx(f, a + i * h)
        i += 1
    return tot * h / 2.0

def _simpson(f, a, b, n, h):
    tot = _fx(f, a) + _fx(f, b)
    i = 1
    while i < n:
        tot += (4.0 if (i % 2) else 2.0) * _fx(f, a + i * h)
        i += 1
    return tot * h / 3.0

def t_midordinate(f, a, b, n):
    n, h = _strips(f, a, b, n)
    val = _midord(f, a, b, n, h)
    out = ['M = ' + casutil.sf3(val)]
    out.append(_w('M = h(y(1/2) + y(3/2) + ... ), h = ' + _f(h)))
    i = 0
    while i < n and i < 12:
        xm = a + (i + 0.5) * h
        out.append(_w('  x = ' + _f(xm, 6) + ':  ' + _f(_fx(f, xm), 6)))
        i += 1
    if n > 12:
        out.append(_w('  ... ' + str(n - 12) + ' more ordinates'))
    ex = _exact_int(f, a, b)
    if ex[0] is not None:
        out.append(_w('exact = ' + _f(ex[0], 6) + ', error = ' + _f(ex[0] - val, 3)))
    if _gap(f, a, b):
        out.append(_wn(GAPMSG))
    return out

def t_simpson(f, a, b, n):
    n, h = _strips(f, a, b, n)
    if n % 2:
        raise ValueError('n must be even')
    val = _simpson(f, a, b, n, h)
    out = ['S = ' + casutil.sf3(val)]
    out.append(_w('S = (h/3)(ends + 4odds + 2evens)'))
    out.append(_w('h = ' + _f(h) + ', n = ' + str(n)))
    i = 0
    while i <= n and i < 13:
        out.append(_w('  y' + str(i) + ' = ' + _f(_fx(f, a + i * h), 6)))
        i += 1
    if n + 1 > 13:
        out.append(_w('  ... ' + str(n + 1 - 13) + ' more ordinates'))
    ex = _exact_int(f, a, b)
    if ex[0] is not None:
        out.append(_w('exact = ' + _f(ex[0], 6) + ', error = ' + _f(ex[0] - val, 3)))
    if _gap(f, a, b):
        out.append(_wn(GAPMSG))
    return out

def t_compare(f, a, b, n):
    n, h = _strips(f, a, b, n)
    mid = _midord(f, a, b, n, h)
    tra = _trap(f, a, b, n, h)
    out = ['mid-ordinate = ' + casutil.sf3(mid),
           'trapezium = ' + casutil.sf3(tra)]
    sim = None
    if n % 2 == 0:
        sim = _simpson(f, a, b, n, h)
        out.append('Simpson = ' + casutil.sf3(sim))
    else:
        out.append(_wn("Simpson's rule needs an even n"))
    val, F, exact = _exact_int(f, a, b)
    if val is not None:
        out.append('exact = ' + _f(val))
        out.append(_w('errors:'))
        out.append(_w('  mid-ordinate ' + _f(val - mid, 3)))
        out.append(_w('  trapezium    ' + _f(val - tra, 3)))
        if sim is not None:
            out.append(_w('  Simpson      ' + _f(val - sim, 3)))
        if not exact:
            out.append(_wn('"exact" is a fine numerical value'))
    out.append(_w('n = ' + str(n) + ', h = ' + _f(h)))
    out.append(_w('M + 2T over 3 = ' + _f((mid + 2.0 * tra) / 3.0, 6)))
    if _gap(f, a, b):
        out.append(_wn(GAPMSG))
    return out

def _fxy(f, x, y):
    try:
        v = caseng.evalf(f, x, False, {'x': x, 'y': y})
    except Exception:
        raise ValueError('cannot evaluate f at x = ' + _f(x))
    if isinstance(v, complex) or v != v or v > 1e300 or v < -1e300:
        raise ValueError('cannot evaluate f at x = ' + _f(x))
    return v

def _steps(n):
    return _int_in(n, 1, 40, 'n')

def _table(rows):
    out = []
    for i, x, y in rows:
        out.append(_w('  r=' + str(i) + '  x = ' + _f(x, 6) + '  y = ' + _f(y, 6)))
    return out

def t_euler(f, x0, y0, h, n):
    n = _steps(n)
    if h == 0:
        raise ValueError('h must not be zero')
    x = x0
    y = y0
    rows = [(0, x, y)]
    i = 1
    while i <= n:
        s = _fxy(f, x, y)
        y = y + h * s
        x = x + h
        rows.append((i, x, y))
        i += 1
    out = ['y(' + _f(x) + ') = ' + casutil.sf3(y)]
    out.append(_w('y(r+1) = y(r) + h f(x(r), y(r))'))
    out.append(_w('h = ' + _f(h) + ', n = ' + str(n)))
    return out + _table(rows)

def t_euler_improved(f, x0, y0, h, n):
    n = _steps(n)
    if h == 0:
        raise ValueError('h must not be zero')
    if n < 2:
        raise ValueError('n must be at least 2')
    y1 = y0 + h * _fxy(f, x0, y0)
    rows = [(0, x0, y0), (1, x0 + h, y1)]
    prev = y0
    y = y1
    x = x0 + h
    i = 2
    while i <= n:
        s = _fxy(f, x, y)
        nxt = prev + 2.0 * h * s
        prev = y
        y = nxt
        x = x + h
        rows.append((i, x, y))
        i += 1
    out = ['y(' + _f(x) + ') = ' + casutil.sf3(y)]
    out.append(_w('y(r+1) = y(r-1) + 2h f(x(r), y(r))'))
    out.append(_w('y(1) from one Euler step'))
    out.append(_w('h = ' + _f(h) + ', n = ' + str(n)))
    return out + _table(rows)

SECTIONS = [
    ('E', 'Further calculus', [
        ('Integral to infinity', 'f(x),a', t_int_inf),
        ('Singular endpoint int', 'f(x),a,b', t_int_sing),
        ('Volume about x-axis', 'f(x),a,b', t_vol_x),
        ('Volume about y-axis', 'g(y),c,d', t_vol_y),
        ('Mean value of f', 'f(x),a,b', t_mean),
        ('Integrate by partials', 'p(x),q(x)', t_partial_int),
        ('d/dx inverse trig', 'f(x),a?', t_invtrig_diff),
        ('Int 1/sqrt(a2-x2)', 'a,p,q', t_int_asin),
        ('Int 1/(a2+x2)', 'a,p,q', t_int_atan),
        ('Arc length y=f(x)', 'f(x),a,b', t_arclen),
        ('Arc length parametric', 'x(t),y(t),a,b', t_arclen_par),
        ('Surface area x-axis', 'f(x),a,b', t_surf_x),
        ('Surface area param', 'x(t),y(t),a,b', t_surf_par),
        ('Reduction x^n e^x', 'n', t_red_xexp),
        ('Reduction sin^n', 'n', t_red_sin),
        ('Reduction cos^n', 'n', t_red_cos),
        ('Reduction tan^n', 'n', t_red_tan),
        ('Reduction (ln x)^n', 'n', t_red_lnx),
        ('Limit x^k e^-x', 'k', t_lim_xexp),
        ('Limit x^k ln x', 'k', t_lim_xlnx),
    ]),
    ('F', 'Further vectors', [
        ('Line from two points', 'A[3],B[3]', t_line_2pts),
        ('Line to cartesian', 'a[3],d[3]', t_line_cart),
        ('Plane from 3 points', 'A[3],B[3],C[3]', t_plane_3pts),
        ('Plane point + normal', 'p[3],n[3]', t_plane_pt_n),
        ('Angle between lines', 'd1[3],d2[3]', t_angle_lines),
        ('Angle line and plane', 'd[3],n[3]', t_angle_lp),
        ('Angle between planes', 'n1[3],n2[3]', t_angle_planes),
        ('Perpendicular check', 'a[3],b[3]', t_perp_check),
        ('Vector product', 'a[3],b[3]', t_cross),
        ('Area of triangle', 'A[3],B[3],C[3]', t_tri_area),
        ('Is p on (r-a)xb=0', 'a[3],b[3],p[3]', t_on_line),
        ('Intersect two lines', 'a1[3],d1[3],a2[3],d2[3]', t_line_meet),
        ('Distance two lines', 'a1[3],d1[3],a2[3],d2[3]', t_line_dist),
        ('Line meets plane', 'a[3],d[3],n[3],k', t_line_plane),
        ('Point to line dist', 'p[3],a[3],d[3]', t_pt_line),
        ('Point to plane dist', 'p[3],n[3],k', t_pt_plane),
    ]),
    ('G', 'Polar coordinates', [
        ('Polar to cartesian', 'r,theta', t_polar_to_xy),
        ('Cartesian to polar', 'x,y', t_xy_to_polar),
        ('Plot r = f(theta)', 'r(x)', t_polar_plot),
        ('Polar area', 'r(x),a,b', t_polar_area),
        ('Tangent para to axis', 'r(x),a,b', t_polar_tan_para),
        ('Tangent perp to axis', 'r(x),a,b', t_polar_tan_perp),
    ]),
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
    ('I', 'Differential equations', [
        ('Integrating factor', 'P(x),Q(x),x0?,y0?', t_intfactor),
        ('Second order homogen', 'a,b,c', t_second_order),
        ('Second order with IVs', 'a,b,c,y0,v0', t_second_ivp),
        ('PI polynomial RHS', 'a,b,c,p(x)', t_pi_poly),
        ('PI for k e^(px)', 'a,b,c,k,p', t_pi_exp),
        ('PI for m cos + n sin', 'a,b,c,m,n,omega', t_pi_trig),
        ('SHM from omega', 'omega,x0?,v0?', t_shm),
        ('Hooke law SHM', 'k,m', t_hooke_shm),
        ('Damping classify', 'm,c,k', t_damping),
        ('Coupled equations', 'a,b,c,d,x0?,y0?', t_coupled),
    ]),
    ('J', 'Numerical methods', [
        ('Mid-ordinate rule', 'f(x),a,b,n', t_midordinate),
        ("Simpson's rule", 'f(x),a,b,n', t_simpson),
        ('Compare rules', 'f(x),a,b,n', t_compare),
        ('Euler step by step', 'f(x y),x0,y0,h,n', t_euler),
        ('Improved Euler', 'f(x y),x0,y0,h,n', t_euler_improved),
    ]),
]
