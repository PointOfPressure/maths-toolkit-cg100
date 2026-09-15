# AQA 7357 sections G-J: differentiation, integration, numerical methods and
# vectors. Each tool takes the parsed fields and returns result lines.
import math
import caseng
import cascalc
import caspoly
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
    return cascalc.tidy(caseng.diff(t, var))

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

def _roots(f, lo=None, hi=None):
    df = caseng.diff(f, 'x')
    if lo is None:
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
    F = cascalc.integ(f)
    return cascalc.tidy(F) if F is not None else None

def _piece(f, F, a, b):
    if F is not None:
        va = casutil.evx(F, a)
        vb = casutil.evx(F, b)
        if va is not None and vb is not None:
            return vb - va
    return cascalc.defint(f, a, b)

# ---- G differentiation -------------------------------------------------------

def t_deriv(f):
    _chk(f, ('x',))
    d1 = _diff(f)
    d2 = _diff(d1)
    return ["f'(x) =", _m(d1), "f''(x) =", _m(d2)]

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

def t_stationary(f):
    _chk(f, ('x',))
    d1 = _diff(f)
    d2 = _diff(d1)
    rs = _roots(d1)
    out = []
    for r in rs[:8]:
        y = casutil.evx(f, r)
        out.append(_nature(d1, d2, r) + ' at ' +
                   (_pt(r, y) if y is not None else '(' + _f(r) + ', ?)'))
    if not out:
        out.append('none in -20 <= x <= 20')
    out.append(_w("f'(x) = " + _ts(d1)))
    out.append(_w("f''(x) = " + _ts(d2)))
    if len(rs) > 8:
        out.append(_warn('only the first 8 shown'))
    return out

def t_inflect(f):
    _chk(f, ('x',))
    d2 = _diff(_diff(f))
    segs = _segments(d2, _roots(d2))
    out = []
    i = 0
    while i < len(segs) - 1:
        r = segs[i][1]
        y = casutil.evx(f, r)
        out.append('inflection at ' +
                   (_pt(r, y) if y is not None else '(' + _f(r) + ', ?)'))
        i += 1
    if not out:
        out.append('no inflection point')
    for ln in _ivl(segs, 'convex', 'concave'):
        out.append(ln)
    out.append(_w("f''(x) = " + _ts(d2)))
    out.append(_w("convex means f''(x) > 0"))
    return out

def t_incdec(f):
    _chk(f, ('x',))
    d1 = _diff(f)
    out = _ivl(_segments(d1, _roots(d1)), 'increasing', 'decreasing')
    if not out:
        out = ['constant in -20 <= x <= 20']
    out.append(_w("f'(x) = " + _ts(d1)))
    return out

def t_firstprin(f, a):
    _chk(f, ('x',))
    fa = _val(f, a)
    ex = _val(_diff(f), a)
    out = ["f'(" + _f(a) + ') = ' + _f(ex)]
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
    out.insert(0, 'at ' + _pt(xv, yv) + ': dy/dx = ' + _f(gv))
    fv = casutil.evx(F, xv, env)
    if fv is not None and (fv > 1e-6 or fv < -1e-6):
        out.append(_warn('F = ' + _f(fv) + ': not on the curve'))
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
    return ['f(' + _f(a) + ') = ' + _f(_val(f, a)),
            "f'(" + _f(a) + ') = ' + _f(_val(d1, a)),
            "f''(" + _f(a) + ') = ' + _f(_val(d2, a)),
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
    out.append('integral = ' + _f(val))
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
    head = [name + ' = ' + _f(total), _w('signed integral = ' + _f(signed))]
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

def t_subst(f, u):
    _chk(f, ('x',))
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
        return [_warn('x remains: try another u')] + out
    G = cascalc.integ(inu, 'u')
    if G is None:
        return [_warn('the u integral is not standard')] + out + \
               [_w('in u: ' + _ts(inu))]
    G = cascalc.tidy(G)
    back = cascalc.tidy(caseng.subst(G, 'u', us))
    return ['int f(x) dx =', _m(('+', back, ('v', 'c'))),
            _w('in u: int ' + _ts(inu) + ' du = ' + _ts(G))] + out + \
           [_w('d/dx of the answer: ' +
               ('agrees' if _agrees(_diff(back), f) else 'DISAGREES'))]

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

def _sep(f, g):
    _chk(f, ('x',))
    _chk(g, ('y',))
    A = cascalc.integ(caseng.simplify(('/', ('n', 1), g)), 'y')
    B = cascalc.integ(f, 'x')
    if A is None or B is None:
        raise ValueError('no standard integral')
    return cascalc.tidy(A), cascalc.tidy(B)

def t_separable(f, g):
    A, B = _sep(f, g)
    return [_ts(A) + ' = ' + _ts(B) + ' + c',
            _w('dy/dx = f(x) g(y)'),
            _w('int 1/g(y) dy = int f(x) dx'),
            _w('int 1/g(y) dy = ' + _ts(A)),
            _w('int f(x) dx = ' + _ts(B))]

def t_separable_pt(f, g, x0, y0):
    A, B = _sep(f, g)
    a0 = _val(A, 0.0, {'y': y0})
    b0 = _val(B, x0)
    c = a0 - b0
    if c == 0:
        eqn = _ts(A) + ' = ' + _ts(B)
    elif c < 0:
        eqn = _ts(A) + ' = ' + _ts(B) + ' - ' + _f(-c)
    else:
        eqn = _ts(A) + ' = ' + _ts(B) + ' + ' + _f(c)
    out = [eqn, _w('c = ' + _f(a0) + ' - ' + _f(b0) + ' = ' + _f(c))]
    Ap = caseng.strip_abs(A)
    inv = caseng.invert(Ap, 'y', 'u')
    if inv is not None:
        ex = cascalc.tidy(caseng.subst(inv, 'u',
                                       caseng.simplify(('+', B, ('n', c)))))
        yv = casutil.evx(ex, x0)
        out.insert(0, 'y =')
        out.insert(1, _m(ex))
        if yv is None or not (-1e-6 < yv - y0 < 1e-6):
            out.append(_warn('explicit form misses the point'))
        elif Ap != A:
            out.append(_warn('y keeps the sign it has at x0'))
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

def t_fixed(g, x0, n):
    _chk(g, ('x',))
    n = _posint(n, 8, 30)
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
        work.append(_w('x' + str(i) + ' = ' + _g(x)))
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
        ('Connected rates', 'y(x),x,dx/dt', t_connected),
        ('Inverse derivative', 'f(x),a', t_invderiv),
        ("f, f' and f'' at a", 'f(x),a', t_valat),
    ]),
    ('H', 'Integration', [
        ('Indefinite integral', 'f(x)', t_indef),
        ('Definite integral', 'f(x),a,b', t_defint),
        ('Area under curve', 'f(x),a,b', t_area),
        ('Area between curves', 'f(x),g(x),a?,b?', t_between),
        ('Substitution u=g(x)', 'f(x),u(x)', t_subst),
        ('Integration by parts', 'u(x),dv(x)', t_byparts),
        ('Riemann sum table', 'f(x),a,b', t_riemann),
        ('Separable DE', 'f(x),g(y)', t_separable),
        ('Separable DE at point', 'f(x),g(y),x0,y0', t_separable_pt),
        ('d/dx of an integral', 'f(x),a', t_ftc),
    ]),
    ('I', 'Numerical methods', [
        ('Sign change table', 'f(x),a,b,n?', t_signchange),
        ('Newton-Raphson', 'f(x),x0,n?', t_newton),
        ('Fixed point x=g(x)', 'g(x),x0,n?', t_fixed),
        ('Bisection', 'f(x),a,b,n?', t_bisect),
        ('Trapezium rule', 'f(x),a,b,n', t_trapezium),
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
    ]),
]
