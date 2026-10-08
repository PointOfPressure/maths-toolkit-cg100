# AQA 7357 sections P-S: quantities and units, kinematics, forces and
# Newton's laws, moments.
import math
import caseng
import cascalc
import caspoly
import casalg
import casutil

_s3 = casutil.sf3
_w = casutil.w
_warn = casutil.warn
_rad = casutil.rad
_deg = casutil.deg

G = 9.8

# ---- small shared helpers ---------------------------------------------------

def _g(g):
    if g is None:
        return G
    if g <= 0:
        raise ValueError('g must be > 0')
    return g

def _pairs(data, msg):
    if len(data) < 2 or len(data) % 2:
        raise ValueError(msg)
    out = []
    i = 0
    while i < len(data):
        out.append((data[i], data[i + 1]))
        i += 2
    return out

def _dirn(x, y):
    return _deg(math.atan2(y, x))

def _v2(x, y):
    return '(' + _s3(x) + ', ' + _s3(y) + ')'

def _term(c, s):
    if c < 0:
        return ' - ' + _s3(-c) + s
    return ' + ' + _s3(c) + s

def _tcheck(tree):
    # t is the variable; other letters are constants kept in the answer
    out = []
    for nm in caseng.vars_in(tree):
        if nm in ('x', 'y'):
            raise ValueError('use t as the variable')
        if nm != 't':
            out.append(nm)
    return out

def _lets(*trees):
    for t in trees:
        for nm in caseng.vars_in(t):
            if nm != 't':
                return True
    return False

def _tval(tree, tv):
    return casutil.ev(tree, 0.0, {'t': tv})

def _tnode(tv):
    r = caseng._fltrat(float(tv))
    return caseng._ratnode(r) if r is not None else ('n', tv)

def _tv(tree, tv):
    # tree at t = tv: a number, or an expression when letters remain
    if _lets(tree):
        return caseng.tostr(caseng.simplify(caseng.subst(tree, 't', _tnode(tv))))
    return _s3(_tval(tree, tv))

def _shift(tree, want, at):
    # add the constant that makes tree(at) = want
    if _lets(tree):
        c = caseng.simplify(('-', _tnode(want),
                             caseng.subst(tree, 't', _tnode(at))))
        return cascalc.tidy(('+', tree, c))
    c = want - _tval(tree, at)
    if c == 0:
        return cascalc.tidy(tree)
    return cascalc.tidy(('+', tree, ('n', c)))

def _rest_lines(v):
    if _lets(v):
        return []
    out = []
    n = 0
    p = caspoly.poly(v, 't')
    rs = _troots(v) if p is not None and len(p) <= 3 else cascalc.solve(v, 't')
    for r in rs:
        if r >= -1e-9 and n < 4:
            out.append(_w('v = 0 at t = ' + _s3(r if r > 0 else 0.0)))
            n += 1
    return out

# ---- P  Quantities and units ------------------------------------------------

def t_kmh(v):
    return ['v = ' + _s3(v / 3.6) + ' m/s',
            _w('1 km/h = 1000/3600 m/s'),
            _w(_s3(v) + ' / 3.6 = ' + _s3(v / 3.6))]

def t_ms(v):
    return ['v = ' + _s3(v * 3.6) + ' km/h',
            _w('1 m/s = 3600/1000 km/h'),
            _w(_s3(v) + ' x 3.6 = ' + _s3(v * 3.6))]

# derived SI units (spec point P1); shown as working on the weight tool
_SI = ('base: length m, mass kg, time s',
       'velocity: m s^-1',
       'acceleration: m s^-2',
       'force: kg m s^-2 = N',
       'weight: kg m s^-2 = N',
       'moment: N m = kg m^2 s^-2',
       'momentum: kg m s^-1 = N s',
       'energy: N m = kg m^2 s^-2 = J',
       'power: J s^-1 = W')

def t_weight(m, g):
    g = _g(g)
    if m < 0:
        raise ValueError('m must be >= 0')
    out = ['W = ' + _s3(m * g) + ' N',
           _w('W = mg = ' + _s3(m) + ' x ' + _s3(g) + ' = ' + _s3(m * g)),
           _w('mass in kg, weight in N: a force')]
    for s in _SI:
        out.append(_w(s))
    return out

# ---- Q  Kinematics ----------------------------------------------------------

_SNAME = ('u', 'v', 'a', 's', 't')
_SUNIT = (' m/s', ' m/s', ' m/s^2', ' m', ' s')

def _pick_t(c1, c2):
    # c1, c2 are (value, t) candidates from a square root; prefer t >= 0
    if c1[1] >= 0:
        return (c1[0], c1[1], c2 if c2[1] >= 0 else None)
    return (c2[0], c2[1], None)

def t_suvat(u, v, a, s, t):
    unk = []
    i = 0
    for q in (u, v, a, s, t):
        if q is None:
            unk.append(i)
        i += 1
    if len(unk) != 2:
        raise ValueError('mark exactly two as ?')
    k = (unk[0], unk[1])
    wk = []
    extra = []
    if k == (0, 1):
        if t == 0:
            raise ValueError('t = 0: u not determined')
        u = s / t - a * t / 2.0
        v = u + a * t
        wk = ['s = ut+at^2/2 so u = s/t - at/2', 'v = u+at']
    elif k == (0, 2):
        if t == 0:
            raise ValueError('t = 0: a not determined')
        u = 2.0 * s / t - v
        a = (v - u) / t
        wk = ['s = (u+v)t/2 so u = 2s/t - v', 'a = (v-u)/t']
    elif k == (0, 3):
        u = v - a * t
        s = (u + v) * t / 2.0
        wk = ['u = v-at', 's = (u+v)t/2']
    elif k == (0, 4):
        if a == 0:
            u = v
            if v == 0:
                raise ValueError('a = 0, v = 0: t not determined')
            t = s / v
            wk = ['a = 0 so u = v', 't = s/v']
        else:
            d = v * v - 2.0 * a * s
            if d < 0:
                raise ValueError('v^2-2as < 0: no real u')
            r = math.sqrt(d)
            u, t, alt = _pick_t((r, (v - r) / a), (-r, (v + r) / a))
            wk = ['u^2 = v^2-2as = ' + _s3(d), 'u = sqrt(' + _s3(d) + ')',
                  't = (v-u)/a']
            if alt is not None:
                extra = [_warn('also u = ' + _s3(alt[0]) + ', t = ' +
                               _s3(alt[1]))]
    elif k == (1, 2):
        if t == 0:
            raise ValueError('t = 0: a not determined')
        v = 2.0 * s / t - u
        a = (v - u) / t
        wk = ['s = (u+v)t/2 so v = 2s/t - u', 'a = (v-u)/t']
    elif k == (1, 3):
        v = u + a * t
        s = u * t + a * t * t / 2.0
        wk = ['v = u+at = ' + _s3(u) + '+' + _s3(a) + 'x' + _s3(t),
              's = ut+at^2/2 = ' + _s3(s)]
    elif k == (1, 4):
        if a == 0:
            v = u
            if u == 0:
                raise ValueError('a = 0, u = 0: t not determined')
            t = s / u
            wk = ['a = 0 so v = u', 't = s/u']
        else:
            d = u * u + 2.0 * a * s
            if d < 0:
                raise ValueError('u^2+2as < 0: no real v')
            r = math.sqrt(d)
            v, t, alt = _pick_t((r, (r - u) / a), (-r, (-r - u) / a))
            wk = ['v^2 = u^2+2as = ' + _s3(d), 'v = sqrt(' + _s3(d) + ')',
                  't = (v-u)/a']
            if alt is not None:
                extra = [_warn('also v = ' + _s3(alt[0]) + ', t = ' +
                               _s3(alt[1]))]
    elif k == (2, 3):
        if t == 0:
            raise ValueError('t = 0: a not determined')
        a = (v - u) / t
        s = (u + v) * t / 2.0
        wk = ['a = (v-u)/t', 's = (u+v)t/2']
    elif k == (2, 4):
        if u + v == 0:
            raise ValueError('u+v = 0: t not determined')
        t = 2.0 * s / (u + v)
        if t == 0:
            raise ValueError('t = 0: a not determined')
        a = (v - u) / t
        wk = ['s = (u+v)t/2 so t = 2s/(u+v)', 'a = (v-u)/t']
    else:
        if a == 0:
            raise ValueError('a = 0: s and t not determined')
        t = (v - u) / a
        s = (u + v) * t / 2.0
        wk = ['t = (v-u)/a', 's = (u+v)t/2']
    vals = (u, v, a, s, t)
    ans = []
    for i in unk:
        ans.append(_SNAME[i] + ' = ' + _s3(vals[i]) + _SUNIT[i])
    if t < 0:
        extra.append(_warn('t < 0: check the signs'))
    out = ans
    for ln in wk:
        out.append(_w(ln))
    return out + extra

def t_vertical(u, h, g):
    g = _g(g)
    if u < 0:
        raise ValueError('u is the speed upwards')
    tt = u / g
    hm = u * u / (2.0 * g)
    ans = ['time to top = ' + _s3(tt) + ' s',
           'max height = ' + _s3(hm) + ' m',
           'back at start t = ' + _s3(2.0 * tt) + ' s']
    wk = [_w('up is positive, a = -g = ' + _s3(-g)),
          _w('t = u/g, H = u^2/(2g)')]
    if h is None:
        return ans + wk
    d = u * u - 2.0 * g * h
    wk.append(_w('v^2 = u^2-2gh = ' + _s3(d)))
    if d < 0:
        return ans + wk + [_warn('no real solution: max height not reached')]
    r = math.sqrt(d)
    ans.append('speed at h = ' + _s3(r) + ' m/s')
    t1 = (u - r) / g
    t2 = (u + r) / g
    if t1 >= 0:
        ans.append('going up at t = ' + _s3(t1) + ' s')
    ans.append('coming down at t = ' + _s3(t2) + ' s')
    return ans + wk

def t_vt(data):
    pts = _pairs(data, 'need t,v pairs')
    if len(pts) < 2:
        raise ValueError('need at least two points')
    disp = 0.0
    dist = 0.0
    wk = []
    i = 1
    while i < len(pts):
        t0, v0 = pts[i - 1]
        t1, v1 = pts[i]
        dt = t1 - t0
        if dt <= 0:
            raise ValueError('times must increase')
        ar = (v0 + v1) * dt / 2.0
        disp += ar
        if v0 * v1 < 0:
            f = v0 / (v0 - v1)
            dist += abs(0.5 * v0 * f * dt) + abs(0.5 * v1 * (1.0 - f) * dt)
        else:
            dist += abs(ar)
        wk.append(_w('seg ' + str(i) + ': a = ' + _s3((v1 - v0) / dt) +
                     ' m/s^2'))
        i += 1
    ans = ['displacement = ' + _s3(disp) + ' m',
           'distance = ' + _s3(dist) + ' m']
    S = 0.0
    zs = []
    cum = ['s(' + _s3(pts[0][0]) + ') = 0']
    i = 1
    while i < len(pts):
        t0, v0 = pts[i - 1]
        t1, v1 = pts[i]
        dt = t1 - t0
        k = (v1 - v0) / dt
        # s = S + v0 u + k u^2 / 2 on 0 < u <= dt
        if k == 0:
            us = [-S / v0] if v0 != 0 else []
        else:
            D = v0 * v0 - 2.0 * k * S
            us = []
            if D >= 0:
                rt = math.sqrt(D)
                us = [(-v0 - rt) / k, (-v0 + rt) / k]
        for u in sorted(us):
            if 1e-9 < u <= dt + 1e-9 and S != 0 or (S == 0 and u > 1e-9 and
                                                    u <= dt + 1e-9):
                if casutil.fmt(t0 + u, 6) not in zs:
                    zs.append(casutil.fmt(t0 + u, 6))
        S += (v0 + v1) * dt / 2.0
        cum.append('s(' + _s3(t1) + ') = ' + _s3(S))
        i += 1
    if zs:
        ans.append('back at s = 0 at t = ' + ', '.join(zs))
    for c in cum:
        wk.append(_w(c))
    wk.append(_w('a = gradient, s = area under v-t'))
    import plot
    plot.run(pts, kind='points', title='v-t graph')
    return ans + wk

def t_st(data):
    pts = _pairs(data, 'need t,s pairs')
    if len(pts) < 2:
        raise ValueError('need at least two points')
    ans = []
    dist = 0.0
    i = 1
    while i < len(pts):
        t0, s0 = pts[i - 1]
        t1, s1 = pts[i]
        dt = t1 - t0
        if dt <= 0:
            raise ValueError('times must increase')
        ans.append('seg ' + str(i) + ': v = ' + _s3((s1 - s0) / dt) + ' m/s')
        dist += abs(s1 - s0)
        i += 1
    ans.append('displacement = ' + _s3(pts[len(pts) - 1][1] - pts[0][1]) + ' m')
    ans.append('distance = ' + _s3(dist) + ' m')
    import plot
    plot.run(pts, kind='points', title='s-t graph')
    return ans + [_w('v = gradient of the s-t graph')]

def t_sva(f, tv):
    _tcheck(f)
    v = cascalc.tidy(caseng.diff(f, 't'))
    a = cascalc.tidy(caseng.diff(v, 't'))
    ans = ['v = ' + caseng.tostr(v), 'a = ' + caseng.tostr(a)]
    if tv is not None:
        ts = _s3(tv)
        ans.append('s(' + ts + ') = ' + _tv(f, tv) + ' m')
        ans.append('v(' + ts + ') = ' + _tv(v, tv) + ' m/s')
        ans.append('a(' + ts + ') = ' + _tv(a, tv) + ' m/s^2')
    return ans + [_w('v = ds/dt, a = dv/dt')] + _rest_lines(v)

def t_vsa(f, s0, tv):
    _tcheck(f)
    a = cascalc.tidy(caseng.diff(f, 't'))
    s0 = 0.0 if s0 is None else s0
    ans = []
    wk = [_w('s = int v dt, a = dv/dt'),
          _w('s(0) = ' + _s3(s0) + ' fixes the constant')]
    S = cascalc.integ(f, 't')
    if S is None:
        wk.append(_warn('no elementary integral for s'))
        s = None
    else:
        s = _shift(S, s0, 0.0)
        ans.append('s = ' + caseng.tostr(s))
    ans.append('a = ' + caseng.tostr(a))
    if tv is not None:
        ts = _s3(tv)
        if s is not None:
            ans.append('s(' + ts + ') = ' + _tv(s, tv) + ' m')
        ans.append('v(' + ts + ') = ' + _tv(f, tv) + ' m/s')
        ans.append('a(' + ts + ') = ' + _tv(a, tv) + ' m/s^2')
    return ans + wk + _rest_lines(f)

def t_avs(f, v0, s0, tv):
    _tcheck(f)
    v0 = 0.0 if v0 is None else v0
    s0 = 0.0 if s0 is None else s0
    V = cascalc.integ(f, 't')
    if V is None:
        raise ValueError('no elementary integral for v')
    v = _shift(V, v0, 0.0)
    ans = ['v = ' + caseng.tostr(v)]
    wk = [_w('v = int a dt, s = int v dt'),
          _w('v(0) = ' + _s3(v0) + ', s(0) = ' + _s3(s0))]
    S = cascalc.integ(v, 't')
    s = None
    if S is None:
        wk.append(_warn('no elementary integral for s'))
    else:
        s = _shift(S, s0, 0.0)
        ans.append('s = ' + caseng.tostr(s))
    if tv is not None:
        ts = _s3(tv)
        if s is not None:
            ans.append('s(' + ts + ') = ' + _tv(s, tv) + ' m')
        ans.append('v(' + ts + ') = ' + _tv(v, tv) + ' m/s')
        ans.append('a(' + ts + ') = ' + _tv(f, tv) + ' m/s^2')
    return ans + wk

def t_dist(f, t0, t1):
    _tcheck(f)
    if t1 < t0:
        t0, t1 = t1, t0
    if t1 == t0:
        raise ValueError('t0 and t1 must differ')
    turns = []
    p = caspoly.poly(f, 't')
    for r in (_troots(f) if p is not None and len(p) <= 3 else
              cascalc.solve(f, 't')):
        if t0 + 1e-9 < r and r < t1 - 1e-9:
            turns.append(r)
    turns.sort()
    bounds = [t0] + turns + [t1]
    disp = 0.0
    dist = 0.0
    i = 0
    while i < len(bounds) - 1:
        seg = cascalc.defint(f, bounds[i], bounds[i + 1], False, 200, 't')
        if seg is None:
            raise ValueError('cannot integrate v(t)')
        disp += seg
        dist += abs(seg)
        i += 1
    ans = ['displacement = ' + _s3(disp) + ' m',
           'distance = ' + _s3(dist) + ' m']
    wk = [_w('displacement = int v dt'), _w('distance = int |v| dt')]
    for r in turns:
        wk.append(_w('v = 0 at t = ' + _s3(r) + ': split here'))
    if not turns:
        wk.append(_w('v keeps one sign, so they agree'))
    return ans + wk

def _quadt(c0, c1, c2):
    T = ('v', 't')
    node = caseng.simplify(('+', ('+', caseng._numnode(c0),
                                  ('*', caseng._numnode(c1), T)),
                            ('*', caseng._numnode(c2), ('^', T, ('n', 2)))))
    return caseng.tostr(node)

def t_vecsuvat(r0, u, a, t):
    if t is None:
        return ['r = (' + _quadt(r0[0], u[0], a[0] / 2.0) + ', ' +
                _quadt(r0[1], u[1], a[1] / 2.0) + ')',
                'v = (' + _quadt(u[0], a[0], 0) + ', ' +
                _quadt(u[1], a[1], 0) + ')',
                _w('r = r0 + ut + at^2/2'), _w('v = u + at')]
    rx = r0[0] + u[0] * t + 0.5 * a[0] * t * t
    ry = r0[1] + u[1] * t + 0.5 * a[1] * t * t
    vx = u[0] + a[0] * t
    vy = u[1] + a[1] * t
    sp = math.sqrt(vx * vx + vy * vy)
    ans = ['r = ' + _v2(rx, ry) + ' m',
           'v = ' + _v2(vx, vy) + ' m/s',
           'speed = ' + _s3(sp) + ' m/s']
    if sp == 0:
        ans.append(_warn('v = 0: direction undefined'))
    else:
        ans.append('direction = ' + _s3(_dirn(vx, vy)) + ' deg')
    return ans + [_w('r = r0 + ut + at^2/2'), _w('v = u + at'),
                  _w('angle measured from the x axis')]

def _tscan(tree):
    # zeros for 0 <= t <= 20 by a coarse scan and bisection
    out = []
    n = 100
    prev = None
    i = 0
    while i <= n and len(out) < 3:
        t = 20.0 * i / n
        try:
            v = _tval(tree, t)
        except ValueError:
            v = None
        if isinstance(v, complex):
            v = None
        if v is not None and v == 0:
            out.append(t)
        elif v is not None and prev is not None and (v < 0) != (prev[1] < 0):
            a = prev[0]
            b = t
            fa = prev[1]
            k = 0
            while k < 50:
                mid = (a + b) / 2.0
                fm = _tval(tree, mid)
                if (fm < 0) == (fa < 0):
                    a = mid
                    fa = fm
                else:
                    b = mid
                k += 1
            out.append((a + b) / 2.0)
        prev = None if v is None else (t, v)
        i += 1
    return out

def _troots(tree):
    # zeros in t: closed form for a polynomial of degree <= 2, else a scan
    p = caspoly.poly(tree, 't')
    if p is None or len(p) > 3:
        return _tscan(tree)
    c = [q[0] / float(q[1]) for q in p] + [0.0, 0.0, 0.0]
    if len(p) == 3:
        D = c[1] * c[1] - 4.0 * c[2] * c[0]
        if D < 0:
            return []
        rt = math.sqrt(D)
        return sorted([(-c[1] - rt) / (2.0 * c[2]), (-c[1] + rt) / (2.0 * c[2])])
    if len(p) == 2:
        return [-c[0] / c[1]]
    return []

def _zeros(tree, what):
    if _lets(tree):
        return []
    out = []
    seen = []
    for r in _troots(tree):
        r = r if r > 1e-6 else 0.0
        if r >= -1e-6 and len(out) < 3 and _s3(r) not in seen:
            seen.append(_s3(r))
            out.append(_w(what + ' at t = ' + _s3(r)))
    return out

def _vecat(r, v, a, tv):
    ts = _s3(tv)
    if _lets(r[0], r[1], v[0], v[1]):
        return ['r(' + ts + ') = (' + _tv(r[0], tv) + ', ' + _tv(r[1], tv) + ')',
                'v(' + ts + ') = (' + _tv(v[0], tv) + ', ' + _tv(v[1], tv) + ')',
                'a(' + ts + ') = (' + _tv(a[0], tv) + ', ' + _tv(a[1], tv) + ')']
    px = _tval(r[0], tv)
    py = _tval(r[1], tv)
    qx = _tval(v[0], tv)
    qy = _tval(v[1], tv)
    sp = math.sqrt(qx * qx + qy * qy)
    out = ['r(' + ts + ') = ' + _v2(px, py) + ' m',
           'v(' + ts + ') = ' + _v2(qx, qy) + ' m/s',
           'speed = ' + casutil.fmt(sp) + ' m/s',
           'a(' + ts + ') = ' + _v2(_tval(a[0], tv), _tval(a[1], tv)) + ' m/s^2']
    if casutil.fmt(sp) != _s3(sp):
        out.append(_w('speed = ' + _s3(sp) + ' m/s'))
    if sp > 0:
        out.append(_w('v at ' + _s3(_dirn(qx, qy)) + ' deg to i'))
    return out

def t_vrdiff(x, y, tv):
    _tcheck(x)
    _tcheck(y)
    vx = cascalc.tidy(caseng.diff(x, 't'))
    vy = cascalc.tidy(caseng.diff(y, 't'))
    ax = cascalc.tidy(caseng.diff(vx, 't'))
    ay = cascalc.tidy(caseng.diff(vy, 't'))
    ans = ['v = (' + caseng.tostr(vx) + ')i + (' + caseng.tostr(vy) + ')j',
           'a = (' + caseng.tostr(ax) + ')i + (' + caseng.tostr(ay) + ')j']
    if tv is not None:
        ans += _vecat((x, y), (vx, vy), (ax, ay), tv)
    return ans + [_w('v = dr/dt, a = dv/dt, each part')] + \
        _zeros(vy, 'v parallel to i') + _zeros(vx, 'v parallel to j')

def t_vvint(vx, vy, r0, tv):
    _tcheck(vx)
    _tcheck(vy)
    X = cascalc.integ(vx, 't')
    Y = cascalc.integ(vy, 't')
    if X is None or Y is None:
        raise ValueError('no elementary integral for r')
    x = _shift(X, r0[0], 0.0)
    y = _shift(Y, r0[1], 0.0)
    ax = cascalc.tidy(caseng.diff(vx, 't'))
    ay = cascalc.tidy(caseng.diff(vy, 't'))
    ans = ['r = (' + caseng.tostr(x) + ')i + (' + caseng.tostr(y) + ')j',
           'a = (' + caseng.tostr(ax) + ')i + (' + caseng.tostr(ay) + ')j']
    if tv is not None:
        ans += _vecat((x, y), (vx, vy), (ax, ay), tv)
    return ans + [_w('r = int v dt with r(0) = ' + _v2(r0[0], r0[1])),
                  _w('a = dv/dt')] + \
        _zeros(vy, 'v parallel to i') + _zeros(vx, 'v parallel to j')

def t_vaint(ax, ay, v0, r0, tv):
    _tcheck(ax)
    _tcheck(ay)
    VX = cascalc.integ(ax, 't')
    VY = cascalc.integ(ay, 't')
    if VX is None or VY is None:
        raise ValueError('no elementary integral for v')
    vx = _shift(VX, v0[0], 0.0)
    vy = _shift(VY, v0[1], 0.0)
    X = cascalc.integ(vx, 't')
    Y = cascalc.integ(vy, 't')
    if X is None or Y is None:
        raise ValueError('no elementary integral for r')
    x = _shift(X, r0[0], 0.0)
    y = _shift(Y, r0[1], 0.0)
    ans = ['v = (' + caseng.tostr(vx) + ')i + (' + caseng.tostr(vy) + ')j',
           'r = (' + caseng.tostr(x) + ')i + (' + caseng.tostr(y) + ')j']
    if tv is not None:
        ans += _vecat((x, y), (vx, vy), (ax, ay), tv)
    return ans + [_w('v = int a dt, v(0) = ' + _v2(v0[0], v0[1])),
                  _w('r = int v dt, r(0) = ' + _v2(r0[0], r0[1]))] + \
        _zeros(vy, 'v parallel to i') + _zeros(vx, 'v parallel to j')

def t_meet2(sA, uA, aA, sB, uB, aB):
    A = (aA - aB) / 2.0
    B = uA - uB
    C = sA - sB
    ts = []
    if A == 0:
        if B == 0:
            if C == 0:
                return ['together at all times', _warn('identical motions')]
            return ['they never meet', _w('same speed, different start')]
        ts = [-C / B]
    else:
        D = B * B - 4.0 * A * C
        if D >= 0:
            rt = math.sqrt(D)
            ts = [(-B - rt) / (2.0 * A), (-B + rt) / (2.0 * A)]
            if D == 0:
                ts = ts[:1]
    ts = [t for t in ts if t >= -1e-12]
    ts.sort()
    eq = ''
    for c, nm in ((A, 't^2'), (B, 't'), (C, '')):
        if c != 0:
            eq += _term(c, nm) if abs(c) != 1 or nm == '' else \
                (' - ' if c < 0 else ' + ') + nm
    eq = eq[3:] if eq[:3] == ' + ' else '-' + eq[3:]
    wk = [_w('s = s0 + ut + at^2/2 for each'), _w(eq + ' = 0')]
    if not ts:
        return ['they never meet for t >= 0'] + wk
    out = []
    for t in ts:
        t = 0.0 if t < 0 else t
        out.append('t = ' + _s3(t) + ' s, s = ' +
                   _s3(sA + uA * t + 0.5 * aA * t * t) + ' m')
        out.append(_w('vA = ' + _s3(uA + aA * t) + ', vB = ' + _s3(uB + aB * t)))
    return out + wk

def _proj(u, ang, h, g):
    g = _g(g)
    if u <= 0:
        raise ValueError('u must be > 0')
    if h is None:
        h = 0.0
    if h < 0:
        raise ValueError('h must be >= 0')
    if ang <= -90 or ang >= 90:
        raise ValueError('angle must be within -90 to 90')
    ra = _rad(ang)
    return (g, h, u * math.cos(ra), u * math.sin(ra), ra)

def t_proj(u, ang, h, g):
    g, h, ux, uy, ra = _proj(u, ang, h, g)
    d = uy * uy + 2.0 * g * h
    tf = (uy + math.sqrt(d)) / g
    rng = ux * tf
    hm = h + uy * uy / (2.0 * g) if uy > 0 else h
    kk = g / (2.0 * ux * ux)
    vy = uy - g * tf
    ans = ['time of flight = ' + _s3(tf) + ' s',
           'range = ' + _s3(rng) + ' m',
           'max height = ' + _s3(hm) + ' m',
           'y = ' + _s3(h) + _term(math.tan(ra), 'x') + _term(-kk, 'x^2'),
           'lands at ' + _v2(ux, vy) + ' m/s, speed ' +
           _s3(math.sqrt(ux * ux + vy * vy)) + ' m/s',
           'landing angle ' + _s3(-_dirn(ux, vy)) + ' deg below level']
    wk = [_w('ux = u cos a = ' + _s3(ux)),
          _w('uy = u sin a = ' + _s3(uy)),
          _w('0 = h + uy t - gt^2/2 gives t'),
          _w('y = h + x tan a - gx^2/(2u^2cos^2a)')]
    if uy <= 0:
        wk.append(_warn('launched level or below: max height is h'))
    if 0 < rng < 1e7:
        import plot
        pts = []
        i = 0
        while i <= 40:
            tt = tf * i / 40.0
            pts.append((ux * tt, h + uy * tt - 0.5 * g * tt * tt))
            i += 1
        plot.run(pts, kind='points', title='projectile path')
    return ans + wk

def t_projfindu(ang, tt, rg, hm, g):
    g = _g(g)
    if ang <= 0 or ang >= 90:
        raise ValueError('angle must be between 0 and 90')
    ra = _rad(ang)
    sa = math.sin(ra)
    if tt is not None:
        u = g * tt / sa
        how = 'time to top: u sin a = g T'
    elif rg is not None:
        u = math.sqrt(rg * g / math.sin(2.0 * ra))
        how = 'range on level ground: R = u^2 sin 2a / g'
    elif hm is not None:
        u = math.sqrt(2.0 * g * hm) / sa
        how = 'max height: H = (u sin a)^2 / (2g)'
    else:
        raise ValueError('give T, R or H')
    return ['u = ' + _s3(u) + ' m/s',
            'ux = ' + _s3(u * math.cos(ra)) + ', uy = ' + _s3(u * sa) + ' m/s',
            _w(how), _w('launched from ground level')]

def t_projat(u, ang, t, h, g):
    g, h, ux, uy, ra = _proj(u, ang, h, g)
    x = ux * t
    y = h + uy * t - 0.5 * g * t * t
    vy = uy - g * t
    sp = math.sqrt(ux * ux + vy * vy)
    ans = ['x = ' + _s3(x) + ' m', 'y = ' + _s3(y) + ' m',
           'v = ' + _v2(ux, vy) + ' m/s',
           'speed = ' + _s3(sp) + ' m/s',
           'direction = ' + _s3(_dirn(ux, vy)) + ' deg']
    wk = [_w('x = ux t, y = h + uy t - gt^2/2'),
          _w('vx = ux = ' + _s3(ux) + ', vy = uy - gt')]
    if y < 0:
        wk.append(_warn('y < 0: it has already landed'))
    if t < 0:
        wk.append(_warn('t < 0: before the launch'))
    return ans + wk

def t_projang(u, rg, g):
    g = _g(g)
    if u <= 0:
        raise ValueError('u must be > 0')
    if rg <= 0:
        raise ValueError('range must be > 0')
    rmax = u * u / g
    s2 = rg * g / (u * u)
    wk = [_w('R = u^2 sin(2a)/g so sin 2a = ' + _s3(s2)),
          _w('max range u^2/g = ' + _s3(rmax) + ' m at 45 deg')]
    if s2 > 1.0:
        return [_warn('out of range: max is ' + _s3(rmax) + ' m')] + wk
    a1 = _deg(math.asin(s2)) / 2.0
    a2 = 90.0 - a1
    ans = ['angle = ' + _s3(a1) + ' deg']
    if abs(a2 - a1) > 1e-9:
        ans.append('or angle = ' + _s3(a2) + ' deg')
        wk.append(_w('a and 90-a give the same range'))
    return ans + wk

def t_projpt(u, x, y, g):
    g = _g(g)
    if u <= 0:
        raise ValueError('u must be > 0')
    if x <= 0:
        raise ValueError('x must be > 0')
    aa = g * x * x / (2.0 * u * u)
    disc = x * x - 4.0 * aa * (y + aa)
    wk = [_w('y = x tanA - gx^2(1+tan^2A)/(2u^2)'),
          _w(_s3(aa) + 'T^2 - ' + _s3(x) + 'T + ' + _s3(y + aa) + ' = 0'),
          _w('discriminant = ' + _s3(disc))]
    if disc < 0:
        return [_warn('out of reach at ' + _s3(u) + ' m/s')] + wk
    r = math.sqrt(disc)
    a1 = _deg(math.atan((x + r) / (2.0 * aa)))
    a2 = _deg(math.atan((x - r) / (2.0 * aa)))
    if r == 0:
        return ['angle = ' + _s3(a1) + ' deg'] + wk + \
               [_warn('one angle only: the point is at the limit')]
    return ['low angle = ' + _s3(a2) + ' deg',
            'high angle = ' + _s3(a1) + ' deg'] + wk

# ---- R  Forces and Newton's laws --------------------------------------------

def t_resolve(f, ang):
    ra = _rad(ang)
    return ['Fx = ' + _s3(f * math.cos(ra)) + ' N',
            'Fy = ' + _s3(f * math.sin(ra)) + ' N',
            _w('Fx = F cos a, Fy = F sin a'),
            _w('a measured from the x axis')]

def _sum_forces(data):
    fs = _pairs(data, 'need force,angle pairs')
    sx = 0.0
    sy = 0.0
    tot = 0.0
    for f, ang in fs:
        ra = _rad(ang)
        sx += f * math.cos(ra)
        sy += f * math.sin(ra)
        tot += abs(f)
    eps = 1e-9 * (tot if tot > 1.0 else 1.0)
    if abs(sx) <= eps:
        sx = 0.0
    if abs(sy) <= eps:
        sy = 0.0
    return (sx, sy, math.sqrt(sx * sx + sy * sy), tot, len(fs))

def t_resultant(data):
    sx, sy, mag, tot, n = _sum_forces(data)
    wk = [_w('Rx = sum F cos a = ' + _s3(sx)),
          _w('Ry = sum F sin a = ' + _s3(sy)),
          _w(str(n) + ' forces, R = sqrt(Rx^2+Ry^2)')]
    if mag <= 1e-9 * (tot if tot > 1.0 else 1.0):
        return ['R = 0 N', _warn('the forces are in equilibrium')] + wk
    return ['R = ' + _s3(mag) + ' N',
            'direction = ' + _s3(_dirn(sx, sy)) + ' deg'] + wk

def t_equil(data):
    sx, sy, mag, tot, n = _sum_forces(data)
    wk = [_w('Rx = ' + _s3(sx) + ', Ry = ' + _s3(sy)),
          _w('equilibrium needs Rx = Ry = 0')]
    if mag <= 1e-9 * (tot if tot > 1.0 else 1.0):
        return ['in equilibrium', 'R = 0 N'] + wk
    d = _dirn(sx, sy)
    return ['not in equilibrium',
            'R = ' + _s3(mag) + ' N at ' + _s3(d) + ' deg',
            'balance: ' + _s3(mag) + ' N at ' + _s3(d - 180.0 if d > 0 else d + 180.0) + ' deg'] + wk

def t_two(p, q, data):
    fs = _pairs(data, 'need force,angle pairs') if data else []
    sx = 0.0
    sy = 0.0
    for f, ang in fs:
        sx += f * math.cos(_rad(ang))
        sy += f * math.sin(_rad(ang))
    eps = 1e-9 * (1.0 + abs(sx) + abs(sy))
    sx = 0.0 if abs(sx) < eps else sx
    sy = 0.0 if abs(sy) < eps else sy
    det = math.sin(_rad(q - p))
    if abs(det) < 1e-12:
        raise ValueError('P and Q are parallel')
    P = (-sx * math.sin(_rad(q)) + sy * math.cos(_rad(q))) / det
    Q = (-sy * math.cos(_rad(p)) + sx * math.sin(_rad(p))) / det
    out = ['P = ' + _s3(P) + ' N', 'Q = ' + _s3(Q) + ' N',
           _w('known forces sum to ' + _v2(sx, sy)),
           _w('P cos p + Q cos q = ' + _s3(-sx)),
           _w('P sin p + Q sin q = ' + _s3(-sy))]
    if P < 0 or Q < 0:
        out.append(_warn('negative: that force points the other way'))
    return out

def t_fma(f, m, a):
    n = 0
    for q in (f, m, a):
        if q is None:
            n += 1
    if n != 1:
        raise ValueError('mark exactly one as ?')
    if f is None:
        f = m * a
        out = ['F = ' + _s3(f) + ' N']
    elif m is None:
        if a == 0:
            raise ValueError('a = 0: m not determined')
        m = f / a
        out = ['m = ' + _s3(m) + ' kg']
    else:
        if m == 0:
            raise ValueError('m = 0: a not determined')
        a = f / m
        out = ['a = ' + _s3(a) + ' m/s^2']
    return out + [_w('F = ma: ' + _s3(f) + ' = ' + _s3(m) + ' x ' + _s3(a)),
                  _w('F is the resultant force in N')]

def t_dynplane(m, data):
    if m <= 0:
        raise ValueError('m must be > 0')
    sx, sy, mag, tot, n = _sum_forces(data)
    wk = [_w('Rx = ' + _s3(sx) + ', Ry = ' + _s3(sy)),
          _w('R = ' + _s3(mag) + ' N, a = R/m')]
    if mag <= 1e-9 * (tot if tot > 1.0 else 1.0):
        return ['a = 0 m/s^2', _warn('resultant is zero: no acceleration')] + wk
    return ['a = ' + _s3(mag / m) + ' m/s^2',
            'direction = ' + _s3(_dirn(sx, sy)) + ' deg',
            'ax = ' + _s3(sx / m) + ', ay = ' + _s3(sy / m)] + wk

def t_pulley(m1, m2, g):
    g = _g(g)
    if m1 <= 0 or m2 <= 0:
        raise ValueError('masses must be > 0')
    tot = m1 + m2
    a = (m1 - m2) * g / tot
    tn = 2.0 * m1 * m2 * g / tot
    ans = ['a = ' + _s3(abs(a)) + ' m/s^2', 'T = ' + _s3(tn) + ' N']
    if a > 0:
        ans.append('m1 goes down')
    elif a < 0:
        ans.append('m2 goes down')
    else:
        ans.append('balanced: a = 0')
    return ans + [_w('a = (m1-m2)g/(m1+m2)'),
                  _w('T = 2 m1 m2 g/(m1+m2)'),
                  _w('same T each side: smooth peg')]

def t_lift(m, a, g):
    g = _g(g)
    if m <= 0:
        raise ValueError('m must be > 0')
    r = m * (g + a)
    ans = ['R = ' + _s3(r) + ' N']
    wk = [_w('R - mg = ma so R = m(g+a)'),
          _w('weight mg = ' + _s3(m * g) + ' N'),
          _w('a > 0 is upwards')]
    if r < 0:
        wk.append(_warn('R < 0: contact is lost'))
    elif a > 0:
        wk.append(_w('R > mg: feels heavier'))
    elif a < 0:
        wk.append(_w('R < mg: feels lighter'))
    return ans + wk

def t_tablepulley(m1, m2, mu, g):
    g = _g(g)
    if m1 <= 0 or m2 <= 0:
        raise ValueError('masses must be > 0')
    if mu < 0:
        raise ValueError('mu must be >= 0')
    fmax = mu * m1 * g
    pull = m2 * g
    wk = [_w('R = m1 g = ' + _s3(m1 * g)),
          _w('F max = mu m1 g = ' + _s3(fmax)),
          _w('hanging weight m2 g = ' + _s3(pull))]
    if pull <= fmax:
        return ['stays at rest', 'a = 0 m/s^2',
                'friction = ' + _s3(pull) + ' N',
                'T = ' + _s3(pull) + ' N'] + wk
    acc = (pull - fmax) / (m1 + m2)
    return ['a = ' + _s3(acc) + ' m/s^2',
            'T = ' + _s3(m2 * (g - acc)) + ' N'] + wk + \
           [_w('a = (m2 g - mu m1 g)/(m1+m2)'), _w('m2: m2 g - T = m2 a')]

def t_towbar(m1, m2, d, r1, r2, a):
    unk = [q is None for q in (m1, m2, d, r1, r2)]
    n = 0
    for u in unk:
        if u:
            n += 1
    if n > 1:
        raise ValueError('mark at most one as ?')
    if n == 1 and a is None:
        raise ValueError('give a to find the ?')
    wk = [_w('whole system: D-R1-R2 = (m1+m2)a'),
          _w('trailer only: T-R2 = m2 a'),
          _w('m1 drives, m2 is towed')]
    ans = []
    if d is None:
        d = r1 + r2 + (m1 + m2) * a
        ans.append('D = ' + _s3(d) + ' N')
    elif r1 is None:
        r1 = d - r2 - (m1 + m2) * a
        ans.append('R1 = ' + _s3(r1) + ' N')
    elif r2 is None:
        r2 = d - r1 - (m1 + m2) * a
        ans.append('R2 = ' + _s3(r2) + ' N')
    elif m1 is None or m2 is None:
        if a == 0:
            raise ValueError('a = 0: the mass is not determined')
        tot = (d - r1 - r2) / a
        if m1 is None:
            m1 = tot - m2
            ans.append('m1 = ' + _s3(m1) + ' kg')
        else:
            m2 = tot - m1
            ans.append('m2 = ' + _s3(m2) + ' kg')
    if m1 <= 0 or m2 <= 0:
        raise ValueError('masses must be > 0')
    if a is None or n == 0:
        a = (d - r1 - r2) / (m1 + m2)
    tn = m2 * a + r2
    ans += ['a = ' + _s3(a) + ' m/s^2', 'T = ' + _s3(tn) + ' N']
    if tn < 0:
        wk.append(_warn('T < 0: the bar is in thrust'))
    return ans + wk

def t_frich(m, mu, p, ang, g, a):
    g = _g(g)
    if m <= 0:
        raise ValueError('m must be > 0')
    ang = 0.0 if ang is None else ang
    if ang <= -90 or ang >= 90:
        raise ValueError('angle must be within -90 to 90')
    ra = _rad(ang)
    c = math.cos(ra)
    s = math.sin(ra)
    if p is None or mu is None:
        aa = 0.0 if a is None else a
        tag = 'on the point of moving' if a is None else 'moving'
        if p is None:
            if mu is None or mu < 0:
                raise ValueError('mark one of mu, P as ?')
            den = c + mu * s
            if den <= 0:
                raise ValueError('cannot pull it that way')
            p = (m * aa + mu * m * g) / den
            ans = ['P = ' + _s3(p) + ' N']
            wk = [_w('P cos a - mu(mg - P sin a) = ma, ' + tag)]
        else:
            rn = m * g - p * s
            if rn <= 0:
                raise ValueError('P sin a >= mg: it lifts off')
            mu = (p * c - m * aa) / rn
            ans = ['mu = ' + _s3(mu)]
            wk = [_w('P cos a - mu R = ma, ' + tag)]
            if mu < 0:
                wk.append(_warn('mu < 0: P is too small for that a'))
        rn = m * g - p * s
        return ans + ['R = ' + _s3(rn) + ' N',
                      'friction = ' + _s3(mu * rn) + ' N'] + wk + \
            [_w('R = mg - P sin a = ' + _s3(rn))]
    if mu < 0:
        raise ValueError('mu must be >= 0')
    if p < 0:
        raise ValueError('P must be >= 0')
    rn = m * g - p * s
    if rn < 0:
        raise ValueError('P sin a > mg: it lifts off')
    fmax = mu * rn
    drive = p * c
    wk = [_w('R = mg - P sin a = ' + _s3(rn)),
          _w('F max = mu R = ' + _s3(fmax)),
          _w('P cos a = ' + _s3(drive))]
    if drive <= fmax:
        return ['does not move', 'friction = ' + _s3(drive) + ' N',
                'a = 0 m/s^2'] + wk + [_w('friction is not at its maximum')]
    return ['it moves', 'a = ' + _s3((drive - fmax) / m) + ' m/s^2',
            'friction = ' + _s3(fmax) + ' N'] + wk

def _slope_u(m, g, down, rn, mu, f, u):
    # moving with speed u along the slope (up +): friction opposes u
    fr = mu * rn
    acc = (f - down - fr) / m if u > 0 else (f - down + fr) / m
    ans = ['a = ' + _s3(acc) + ' m/s^2 (up the slope +)',
           'friction = ' + _s3(fr) + ' N ' + ('down' if u > 0 else 'up') +
           ' the slope']
    wk = [_w('moving ' + ('up' if u > 0 else 'down') + ': friction opposes it'),
          _w('R = mg cos a = ' + _s3(rn))]
    if u > 0 and acc < 0:
        ts = u / -acc
        ans.append('stops after ' + _s3(ts) + ' s, ' + _s3(u * u / (-2.0 * acc)) +
                   ' m up')
        if f - down + fr < 0:
            wk.append(_w('then slides back down'))
        else:
            wk.append(_w('then stays at rest'))
    return ans + wk

def t_slope(m, ang, mu, f, g, a, u):
    g = _g(g)
    if m is None or m <= 0:
        raise ValueError('m must be > 0')
    if ang < 0 or ang >= 90:
        raise ValueError('angle must be 0 to 90')
    ra = _rad(ang)
    down = m * g * math.sin(ra)
    rn = m * g * math.cos(ra)
    if mu is None:
        if f is None:
            raise ValueError('mark one of mu, F as ?')
        aa = 0.0 if a is None else a
        net = f - down - m * aa
        if net >= 0:
            mu = net / rn
            how = 'moving up' if a is not None else 'about to slip up'
        else:
            mu = (down - f - m * aa) / rn if a is not None else -net / rn
            how = 'moving down' if a is not None else 'about to slip down'
        return ['mu = ' + _s3(mu), 'friction = ' + _s3(mu * rn) + ' N',
                _w(how + ': F - mg sin a -+ mu R = ma'),
                _w('R = mg cos a = ' + _s3(rn)),
                _w('mg sin a = ' + _s3(down))]
    if mu < 0:
        raise ValueError('mu must be >= 0')
    fmax = mu * rn
    if u is not None and u != 0:
        return _slope_u(m, g, down, rn, mu, 0.0 if f is None else f, u)
    if f is None:
        if a is not None:
            f = m * a + down + fmax
            return ['F = ' + _s3(f) + ' N', _w('moving up: F - mg sin a - mu R = ma'),
                    _w('R = mg cos a = ' + _s3(rn)),
                    _w('F max = mu R = ' + _s3(fmax))]
        lo = down - fmax
        return ['at rest for ' + _s3(lo if lo > 0 else 0.0) + ' <= F <= ' +
                _s3(down + fmax) + ' N',
                _w('R = mg cos a = ' + _s3(rn)),
                _w('F max = mu R = ' + _s3(fmax)),
                _w('about to slip down: F = mg sin a - mu R'),
                _w('about to slip up: F = mg sin a + mu R'),
                _w('F acts up the slope, parallel to it')] + \
            ([_warn('mu >= tan a: rests with no F')] if lo <= 0 else [])
    drive = f - down
    wk = [_w('R = mg cos a = ' + _s3(rn)),
          _w('mg sin a = ' + _s3(down)),
          _w('F max = mu R = ' + _s3(fmax)),
          _w('F - mg sin a = ' + _s3(drive) + ' (up +)')]
    if abs(drive) <= fmax:
        ans = ['stays at rest', 'a = 0 m/s^2',
               'friction = ' + _s3(abs(drive)) + ' N']
        if drive > 0:
            ans.append('friction acts down the slope')
        elif drive < 0:
            ans.append('friction acts up the slope')
        return ans + wk
    acc = (abs(drive) - fmax) / m
    return ['a = ' + _s3(acc) + ' m/s^2',
            'moves ' + ('up' if drive > 0 else 'down') + ' the slope',
            'friction = ' + _s3(fmax) + ' N'] + wk

def t_slopepull(m, ang, th, p, mu, a, res, g):
    # pull P at th above the line of greatest slope, moving up the slope
    g = _g(g)
    if m <= 0:
        raise ValueError('m must be > 0')
    if ang < 0 or ang >= 90 or th <= -90 or th >= 90:
        raise ValueError('angles must be 0 to 90')
    res = 0.0 if res is None else res
    aa = 0.0 if a is None else a
    ra = _rad(ang)
    rt = _rad(th)
    c = math.cos(rt)
    s = math.sin(rt)
    wt = m * g * math.sin(ra)
    nc = m * g * math.cos(ra)
    wk = [_w('R = mg cos a - P sin th'),
          _w('P cos th - mg sin a - mu R - resist = ma')]
    if p is None:
        if mu is None:
            raise ValueError('mark one of P, mu as ?')
        p = (m * aa + wt + mu * nc + res) / (c + mu * s)
        ans = ['P = ' + _s3(p) + ' N']
    elif mu is None:
        rn = nc - p * s
        if rn <= 0:
            raise ValueError('R <= 0: it lifts off')
        mu = (p * c - wt - res - m * aa) / rn
        ans = ['mu = ' + _s3(mu)]
    else:
        rn = nc - p * s
        if rn < 0:
            raise ValueError('R < 0: it lifts off')
        acc = (p * c - wt - mu * rn - res) / m
        ans = ['a = ' + _s3(acc) + ' m/s^2']
        if acc < 0:
            wk.append(_warn('a < 0: it slows, or it does not move up'))
    rn = nc - p * s
    return ans + ['R = ' + _s3(rn) + ' N', 'friction = ' + _s3(mu * rn) + ' N'] + \
        wk + [_w('mg sin a = ' + _s3(wt) + ', mg cos a = ' + _s3(nc))]

def t_slopepulley(m1, ang, mu, m2, g, a):
    g = _g(g)
    if ang < 0 or ang >= 90:
        raise ValueError('angle must be 0 to 90')
    ra = _rad(ang)
    sa = math.sin(ra)
    ca = math.cos(ra)
    n = 0
    for q in (m1, mu, m2):
        if q is None:
            n += 1
    if n > 1:
        raise ValueError('mark at most one as ?')
    if n == 1:
        aa = 0.0 if a is None else a
        tag = 'moving' if a is not None else 'on the point of moving'
        wk = [_w('m2 falls, m1 moves up the slope, ' + tag),
              _w('m2 g - m1 g sin a - mu m1 g cos a = (m1+m2)a')]
        if mu is None:
            if m1 <= 0 or m2 <= 0:
                raise ValueError('masses must be > 0')
            rn = m1 * g * ca
            net = m2 * g - m1 * g * sa
            if net >= 0:
                mu = (net - (m1 + m2) * aa) / rn
            else:
                wk[0] = _w('m1 slides down, m2 rises, ' + tag)
                mu = (-net - (m1 + m2) * aa) / rn
            ans = ['mu = ' + _s3(mu)]
        elif m2 is None:
            m2 = m1 * (aa + g * sa + mu * g * ca) / (g - aa)
            ans = ['m2 = ' + _s3(m2) + ' kg']
        else:
            m1 = m2 * (g - aa) / (aa + g * sa + mu * g * ca)
            ans = ['m1 = ' + _s3(m1) + ' kg']
        tn = m2 * (g - aa)
        return ans + ['T = ' + _s3(tn) + ' N',
                      'friction = ' + _s3(mu * m1 * g * ca) + ' N'] + wk
    if m1 <= 0 or m2 <= 0:
        raise ValueError('masses must be > 0')
    if mu < 0:
        raise ValueError('mu must be >= 0')
    down = m1 * g * sa
    rn = m1 * g * ca
    fmax = mu * rn
    pull = m2 * g
    wk = [_w('R = m1 g cos a = ' + _s3(rn)),
          _w('F max = mu R = ' + _s3(fmax)),
          _w('m1 g sin a = ' + _s3(down) + ', m2 g = ' + _s3(pull))]
    net = pull - down
    if abs(net) <= fmax:
        return ['stays at rest', 'T = ' + _s3(pull) + ' N',
                'friction = ' + _s3(abs(net)) + ' N ' +
                ('down' if net > 0 else 'up') + ' the slope'] + wk
    acc = (abs(net) - fmax) / (m1 + m2)
    if net > 0:
        tn = m2 * (g - acc)
        how = 'm2 falls, m1 moves up the slope'
    else:
        tn = m2 * (g + acc)
        how = 'm2 rises, m1 slides down the slope'
    return ['a = ' + _s3(acc) + ' m/s^2', 'T = ' + _s3(tn) + ' N', how,
            'friction = ' + _s3(fmax) + ' N'] + wk + \
        [_w('whole system: |m2 g - m1 g sin a| - mu R = (m1+m2)a')]

# ---- S  Moments -------------------------------------------------------------

def t_moments(data):
    fd = _pairs(data, 'need force,distance pairs')
    tot = 0.0
    sf = 0.0
    wk = []
    i = 0
    while i < len(fd):
        f, d = fd[i]
        tot += f * d
        sf += f
        wk.append(_w('F' + str(i + 1) + ' x d = ' + _s3(f) + ' x ' + _s3(d) +
                     ' = ' + _s3(f * d)))
        i += 1
    ans = ['sum of moments = ' + _s3(tot) + ' Nm',
           'sum of forces = ' + _s3(sf) + ' N']
    if tot == 0:
        ans.append('moments balance')
    else:
        ans.append(('anticlockwise' if tot > 0 else 'clockwise') + ' overall')
    return ans + wk + [_w('moment = force x perpendicular dist'),
                       _w('signs: anticlockwise positive')]

def t_ladder(L, W, ang, mu, Wp, x):
    if L <= 0 or W < 0:
        raise ValueError('need L > 0, W >= 0')
    if ang <= 0 or ang >= 90:
        raise ValueError('angle is 0 to 90 exclusive')
    Wp = 0.0 if Wp is None else Wp
    if Wp < 0:
        raise ValueError('Wp must be >= 0')
    tn = math.tan(_rad(ang))
    R = W + Wp
    if R <= 0:
        raise ValueError('total weight must be > 0')
    wk = [_w('R = W + Wp = ' + _s3(R) + ' N'),
          _w('about the foot: S L sin a = W (L/2) cos a + Wp x cos a'),
          _w('F = S, smooth wall, angle a to the ground')]
    if x is None:
        if mu is None or Wp == 0:
            x = 0.0
        else:
            xm = (mu * R * L * tn - W * L / 2.0) / Wp
            if xm < 0:
                return ['slips even with no climber'] + wk
            if xm >= L:
                return ['can climb to the top'] + wk
            return ['can climb x = ' + _s3(xm) + ' m',
                    _w('at the limit S = F = mu R = ' + _s3(mu * R))] + wk
    if x < 0 or x > L:
        raise ValueError('x is 0 to L along the ladder')
    S = (W * L / 2.0 + Wp * x) / (L * tn)
    out = ['S = ' + _s3(S) + ' N (wall)', 'R = ' + _s3(R) + ' N (ground)',
           'F = ' + _s3(S) + ' N', 'mu needed = ' + _s3(S / R)]
    if mu is not None:
        out.append('it slips' if S > mu * R + 1e-12 else 'it stays put')
        amin = _deg(math.atan((W * L / 2.0 + Wp * x) / (mu * R * L))) if mu > 0 else 90.0
        out.append(_w('least angle = ' + _s3(amin) + ' deg'))
    return out + wk

def t_momsolve(cw, acw):
    # clockwise moments = anticlockwise moments, one unknown letter; g may
    # stay as a letter
    vs = []
    for t in (cw, acw):
        for v in caseng.vars_in(t):
            if v not in vs:
                vs.append(v)
    unk = [v for v in vs if v != 'g']
    if len(unk) > 1:
        raise ValueError('one unknown letter only (g may stay)')
    if not unk and 'g' not in vs:
        raise ValueError('use a letter for the unknown')
    u = unk[0] if unk else 'g'
    S = caseng.simplify
    E = S(('-', cw, acw))
    lin = casalg.linin(caspoly.expand(E), u)
    if lin is None or lin[0] == ('n', 0):
        raise ValueError('the moments must be linear in ' + u)
    sol = S(('neg', ('/', lin[1], lin[0])))
    out = [u + ' = ' + caseng.tostr(sol)]
    if 'g' in caseng.vars_in(sol):
        v = casutil.ev(sol, 0.0, {'g': G})
        out.append(_w(u + ' = ' + _s3(v) + ' with g = 9.8'))
    else:
        v = casutil.ev(sol)
        if caseng.tostr(sol) != _s3(v):
            out.append(_w(u + ' = ' + _s3(v)))
    out.append(_w('clockwise = anticlockwise about the pivot'))
    out.append(_w(caseng.tostr(S(cw)) + ' = ' + caseng.tostr(S(acw))))
    return out

def _gx(v, g):
    return _s3(v / g) + 'g'

def t_beam(l, mm, a, b, loads):
    if l <= 0:
        raise ValueError('L must be > 0')
    if mm < 0:
        raise ValueError('M must be >= 0')
    if a > b:
        a, b = b, a
    if a == b:
        raise ValueError('supports must be apart')
    loads = [] if loads is None else list(loads)
    g = G
    if len(loads) % 2 == 1:
        g = _g(loads.pop())
    ld = _pairs(loads, 'need position,mass pairs') if loads else []
    tot = mm
    mom = mm * (l / 2.0 - a)
    off = False
    for x, ms in ld:
        if ms < 0:
            raise ValueError('load mass must be >= 0')
        if x < 0 or x > l:
            off = True
        tot += ms
        mom += ms * (x - a)
    rb = mom * g / (b - a)
    ra = tot * g - rb
    ans = ['R at ' + _s3(a) + ' m = ' + _s3(ra) + ' N = ' + _gx(ra, g),
           'R at ' + _s3(b) + ' m = ' + _s3(rb) + ' N = ' + _gx(rb, g)]
    wk = [_w('g = ' + _s3(g) + ', total weight = ' + _s3(tot * g) + ' N'),
          _w('beam weight acts at L/2 = ' + _s3(l / 2.0)),
          _w('about A: RB(b-a) = sum W x dist'),
          _w('RB x ' + _s3(b - a) + ' = ' + _s3(mom * g)),
          _w('an odd last value sets g')]
    if ra < 0 or rb < 0:
        wk.append(_warn('a reaction is negative: the beam tilts'))
    if off:
        wk.append(_warn('a load sits off the beam'))
    return ans + wk

def t_tilt(l, mm, a, b, m):
    if l <= 0:
        raise ValueError('L must be > 0')
    if m <= 0:
        raise ValueError('m must be > 0')
    if a > b:
        a, b = b, a
    if a == b:
        raise ValueError('supports must be apart')
    xb = b + mm * (b - l / 2.0) / m
    xa = a - mm * (l / 2.0 - a) / m
    ans = ['tilts about B if x > ' + _s3(xb) + ' m',
           'tilts about A if x < ' + _s3(xa) + ' m']
    wk = [_w('RA = 0: M(b-L/2) + m(b-x) = 0'),
          _w('RB = 0: M(L/2-a) + m(x-a) = 0'),
          _w('x measured from the same end as a, b')]
    if xb > l:
        wk.append(_warn('x > L: it cannot tilt about B'))
    if xa < 0:
        wk.append(_warn('x < 0: it cannot tilt about A'))
    return ans + wk

SECTIONS = [
    ('P', 'Quantities and units', [
        ('km/h to m/s', 'v', t_kmh),
        ('m/s to km/h', 'v', t_ms),
        ('Weight and SI units', 'm,g?', t_weight),
    ]),
    ('Q', 'Kinematics', [
        ('SUVAT', 'u,v,a,s,t', t_suvat),
        ('Vertical under gravity', 'u,h?,g?', t_vertical),
        ('v-t graph points', 't v pairs*', t_vt),
        ('s-t graph points', 't s pairs*', t_st),
        ('s(t) to v and a', 's(t),t?', t_sva),
        ('v(t) to s and a', 'v(t),s0?,t?', t_vsa),
        ('a(t) to v and s', 'a(t),v0?,s0?,t?', t_avs),
        ('Distance from v(t)', 'v(t),t0,t1', t_dist),
        ('Vector SUVAT', 'r0[2],u[2],a[2],t?', t_vecsuvat),
        ('Vector r(t) to v, a', 'x(t),y(t),t?', t_vrdiff),
        ('Vector v(t) to r, a', 'vx(t),vy(t),r0[2],t?', t_vvint),
        ('Vector a(t) to v, r', 'ax(t),ay(t),v0[2],r0[2],t?', t_vaint),
        ('Two particles meet', 'sA,uA,aA,sB,uB,aB', t_meet2),
        ('Projectile launch', 'u,angle,h?,g?', t_proj),
        ('Projectile at time t', 'u,angle,t,h?,g?', t_projat),
        ('Projectile angle', 'u,range,g?', t_projang),
        ('Projectile find u', 'angle,T?,R?,H?,g?', t_projfindu),
        ('Projectile to a point', 'u,x,y,g?', t_projpt),
    ]),
    ('R', 'Forces and Newton laws', [
        ('Resolve a force', 'F,angle', t_resolve),
        ('Resultant of forces', 'F angle pairs*', t_resultant),
        ('Equilibrium check', 'F angle pairs*', t_equil),
        ('Two unknown forces', 'p,q,F angle pairs*', t_two),
        ('Newton II F = ma', 'F,m,a', t_fma),
        ('Plane dynamics', 'm,F angle pairs*', t_dynplane),
        ('Pulley over a peg', 'm1,m2,g?', t_pulley),
        ('Tow bar in a line', 'm1,m2,D,R1,R2,a?', t_towbar),
        ('Lift reaction', 'm,a,g?', t_lift),
        ('Friction horizontal', 'm,mu,P,angle?,g?,a?', t_frich),
        ('Rough slope', 'm,angle,mu,F,g?,a?,u?', t_slope),
        ('Slope, pull at angle', 'm,angle,th,P,mu,a?,resist?,g?', t_slopepull),
        ('Mass on rough table', 'm1,m2,mu,g?', t_tablepulley),
        ('Slope and pulley', 'm1,angle,mu,m2,g?,a?', t_slopepulley),
    ]),
    ('S', 'Moments', [
        ('Moments about a point', 'F d pairs*', t_moments),
        ('Moments: find unknown', 'cw(m),acw(m)', t_momsolve),
        ('Beam on two supports', 'L,M,a,b,pos mass pairs g*?', t_beam),
        ('Tilting point', 'L,M,a,b,m', t_tilt),
        ('Ladder, smooth wall', 'L,W,angle,mu?,Wp?,x?', t_ladder),
    ]),
]
