import math
import casui
import casutil
import caseng
import cascalc

_asknum = casutil.asknum
_askg = casutil.askg
_fn = casutil.fmt
_show = casutil.show
_w = casutil.w             # method / intermediate steps, hidden in answer mode
_warn = casutil.warn       # caveat about the answer, shown in both modes
_getlist = casutil.asklist
_askexpr = casutil.askexpr
_deg = casutil.deg
_rad = casutil.rad
_atan2 = casutil.atan2

def _choose(prompt):
    # Menu index typed as a number. int() raises on nan and on inf, and a
    # mistyped entry can be either, so both are turned into "cancelled".
    v = _asknum(prompt)
    if v is None or v != v or v > 1e9 or v < -1e9:
        return None
    return int(v)

def _defi(tree, a, b, var):
    # Definite integral: symbolic when the CAS manages it (exact, and it is
    # what the student would write down), numeric Simpson otherwise.
    s = None
    try:
        s = cascalc.integ(caseng.simplify(tree), var)
    except:
        s = None
    if s is not None:
        try:
            hi = caseng.evalf(s, b, False, {var: b})
            lo = caseng.evalf(s, a, False, {var: a})
            v = hi - lo
            if v == v and -1.7e308 < v < 1.7e308:
                return v
        except:
            pass
    return cascalc.defint(tree, a, b, False, 400, var)

# ---------- momentum & impulse ----------
def t_momentum():
    _show('Momentum/Impulse', ['1 conservation (find v2)',
        '2 impulse = m(v-u)', 'Enter 1 or 2 next'])
    k = _asknum('Choose 1 or 2')
    if k is None:
        return
    if int(k) == 2:
        m = _asknum('mass m')
        u = _asknum('initial u')
        v = _asknum('final v')
        if m is None or u is None or v is None:
            return
        j = m * (v - u)
        _show('Impulse', [_w('J = m(v-u)'), 'J = ' + _fn(j) + ' N s',
            'change p = ' + _fn(j) + ' kg m/s'])
        return
    _show('Conservation', ['m1u1+m2u2 = m1v1+m2v2',
        'enter masses, initial', 'speeds and v1, find v2'])
    m1 = _asknum('m1')
    u1 = _asknum('u1')
    m2 = _asknum('m2')
    u2 = _asknum('u2')
    v1 = _asknum('v1 (final 1)')
    if None in (m1, u1, m2, u2, v1):
        return
    if m2 == 0:
        _show('Conservation', [_warn('m2 = 0, cannot find v2')])
        return
    v2 = (m1 * u1 + m2 * u2 - m1 * v1) / m2
    p = m1 * u1 + m2 * u2
    _show('Conservation', ['total p = ' + _fn(p) + ' kg m/s',
        'v1 = ' + _fn(v1) + ' m/s', 'v2 = ' + _fn(v2) + ' m/s'])

# ---------- coefficient of restitution ----------
def t_restitution():
    _show('Restitution', ['e = (v2-v1)/(u1-u2)',
        '1 behind 2: u1 > u2.', 'Solve v1,v2 from',
        'conservation + e'])
    e = _asknum('e (0..1)')
    m1 = _asknum('m1')
    u1 = _asknum('u1')
    m2 = _asknum('m2')
    u2 = _asknum('u2')
    if None in (e, m1, u1, m2, u2):
        return
    tot = m1 + m2
    if tot == 0:
        _show('Restitution', [_warn('total mass 0')])
        return
    # conservation: m1 v1 + m2 v2 = m1 u1 + m2 u2 = P
    # restitution:  v2 - v1 = e (u1 - u2) = sep
    # => (m1+m2) v1 = P - m2 sep ;  v2 = v1 + sep
    p = m1 * u1 + m2 * u2
    sep = e * (u1 - u2)
    v1 = (p - m2 * sep) / tot
    v2 = v1 + sep
    ke0 = 0.5 * m1 * u1 * u1 + 0.5 * m2 * u2 * u2
    ke1 = 0.5 * m1 * v1 * v1 + 0.5 * m2 * v2 * v2
    _show('Restitution', ['v1 = ' + _fn(v1) + ' m/s',
        'v2 = ' + _fn(v2) + ' m/s', 'KE lost = ' + _fn(ke0 - ke1) + ' J'])

# ---------- work, energy, power ----------
def t_work():
    _show('Work/Energy/Power', ['1 KE = 0.5 m v^2', '2 GPE = m g h',
        '3 Work = F d', '4 Power = F v', '5 Power = W / t'])
    k = _asknum('Choose 1-5')
    if k is None:
        return
    k = int(k)
    if k == 1:
        m = _asknum('mass m')
        v = _asknum('speed v')
        if None in (m, v):
            return
        _show('Kinetic energy', [_w('KE = 0.5 m v^2'),
            'KE = ' + _fn(0.5 * m * v * v) + ' J'])
    elif k == 2:
        m = _asknum('mass m')
        h = _asknum('height h')
        if None in (m, h):
            return
        g = _askg()
        _show('GPE', [_w('GPE = m g h'), _w('g = ' + _fn(g)),
            'GPE = ' + _fn(m * g * h) + ' J'])
    elif k == 3:
        f = _asknum('force F')
        d = _asknum('distance d')
        if None in (f, d):
            return
        _show('Work done', [_w('W = F d'), 'W = ' + _fn(f * d) + ' J'])
    elif k == 4:
        f = _asknum('force F')
        v = _asknum('speed v')
        if None in (f, v):
            return
        _show('Power', [_w('P = F v'), 'P = ' + _fn(f * v) + ' W'])
    elif k == 5:
        w = _asknum('work W')
        t = _asknum('time t')
        if None in (w, t) or t == 0:
            return
        _show('Power', [_w('P = W / t'), 'P = ' + _fn(w / t) + ' W'])

# ---------- circular motion ----------
def t_circular():
    _show('Circular motion', ['1 a,F from v & r', '2 a,F from omega & r',
        '3 conical pendulum', '4 vertical circle top',
        '5 tangential acceleration'])
    k = _asknum('Choose 1-5')
    if k is None:
        return
    k = int(k)
    if k == 1:
        m = _asknum('mass m')
        v = _asknum('speed v')
        r = _asknum('radius r')
        if None in (m, v, r) or r == 0:
            return
        a = v * v / r
        _show('Circular (v,r)', ['a = v^2/r = ' + _fn(a) + ' m/s2',
            'F = m a = ' + _fn(m * a) + ' N',
            'omega = v/r = ' + _fn(v / r) + ' rad/s'])
    elif k == 2:
        m = _asknum('mass m')
        w = _asknum('omega (rad/s)')
        r = _asknum('radius r')
        if None in (m, w, r):
            return
        a = w * w * r
        _show('Circular (om,r)', ['a = omega^2 r = ' + _fn(a) + ' m/s2',
            'F = m a = ' + _fn(m * a) + ' N',
            'v = omega r = ' + _fn(w * r) + ' m/s'])
    elif k == 3:
        v = _asknum('speed v')
        r = _asknum('radius r')
        if None in (v, r) or r == 0:
            return
        g = _askg()
        if g == 0:
            return
        tan = v * v / (r * g)
        th = math.atan(tan)
        deg = th * 180.0 / math.pi
        _show('Conical pendulum', [_w('tan th = v^2/(r g)'),
            'tan th = ' + _fn(tan), 'theta = ' + _fn(deg) + ' deg'])
    elif k == 4:
        r = _asknum('radius r')
        if r is None or r < 0:
            return
        g = _askg()
        if g < 0:
            return
        vmin = math.sqrt(g * r)
        _show('Vertical circle', ['min speed at top',
            _w('v = sqrt(g r)'), 'v = ' + _fn(vmin) + ' m/s'])
    elif k == 5:
        # r6: the speed is changing, so there is a component of acceleration
        # along the tangent as well as the v^2/r towards the centre.
        r = _asknum('radius r')
        w = _asknum('omega (rad/s)')
        al = _asknum('angular accel alpha (rad/s2)')
        if None in (r, w, al):
            return
        ar = w * w * r
        at = al * r
        tot = math.sqrt(ar * ar + at * at)
        th = _deg(_atan2(at, ar))
        _show('Tangential accel', [_w('radial: a_r = omega^2 r'),
            'a_r = ' + _fn(ar) + ' m/s2',
            _w('tangential: a_t = r alpha = dv/dt'),
            'a_t = ' + _fn(at) + ' m/s2',
            _w('total a = sqrt(a_r^2 + a_t^2)'),
            'total a = ' + _fn(tot) + ' m/s2',
            'angle to radius = ' + _fn(th) + ' deg',
            'v = omega r = ' + _fn(w * r) + ' m/s'])

# ---------- Hooke's law / elastic PE ----------
def t_hooke():
    _show('Hooke / elastic', ['T = lambda x / l', 'EPE = lambda x^2/(2 l)',
        'enter lambda, x, l'])
    lam = _asknum('lambda (modulus)')
    x = _asknum('extension x')
    l = _asknum('natural length l')
    if None in (lam, x, l) or l == 0:
        return
    tens = lam * x / l
    epe = lam * x * x / (2.0 * l)
    _show('Hooke / elastic', ['T = lam x/l = ' + _fn(tens) + ' N',
        _w('EPE = lam x^2/(2l)'), 'EPE = ' + _fn(epe) + ' J'])

# ---------- centre of mass ----------
def t_com():
    _show('Centre of mass', ['1 one dimension', '2 two dimensions',
        'enter masses then coords'])
    k = _asknum('Choose 1 or 2')
    if k is None:
        return
    masses = _getlist('masses m (space sep)')
    if masses is None or len(masses) == 0:
        return
    sm = 0.0
    for m in masses:
        sm += m
    if sm == 0:
        _show('Centre of mass', [_warn('total mass 0')])
        return
    if int(k) == 1:
        xs = _getlist('x coords (space sep)')
        if xs is None or len(xs) != len(masses):
            _show('Centre of mass', [_warn('count mismatch')])
            return
        sx = 0.0
        for i in range(len(masses)):
            sx += masses[i] * xs[i]
        _show('COM (1-D)', [_w('total m = ' + _fn(sm)),
            'x_bar = ' + _fn(sx / sm)])
    else:
        xs = _getlist('x coords (space sep)')
        ys = _getlist('y coords (space sep)')
        if xs is None or ys is None or len(xs) != len(masses) or len(ys) != len(masses):
            _show('Centre of mass', [_warn('count mismatch')])
            return
        sx = 0.0
        sy = 0.0
        for i in range(len(masses)):
            sx += masses[i] * xs[i]
            sy += masses[i] * ys[i]
        _show('COM (2-D)', [_w('total m = ' + _fn(sm)),
            'x_bar = ' + _fn(sx / sm), 'y_bar = ' + _fn(sy / sm)])

# ---------- dimensional analysis ----------
def t_dim():
    _show('Dimensions', ['Enter M L T powers for', 'LHS and RHS, check',
        'they are consistent', 'e.g. force = 1 1 -2'])
    a = _getlist('LHS: M L T powers')
    b = _getlist('RHS: M L T powers')
    if a is None or b is None or len(a) != 3 or len(b) != 3:
        _show('Dimensions', [_warn('need 3 numbers each'), 'e.g.  1 1 -2'])
        return
    nm = ['M', 'L', 'T']
    same = True
    for i in range(3):
        if a[i] != b[i]:
            same = False
    lhs = ''
    rhs = ''
    for i in range(3):
        lhs += nm[i] + '^' + _fn(a[i]) + ' '
        rhs += nm[i] + '^' + _fn(b[i]) + ' '
    if same:
        res = 'CONSISTENT'
    else:
        res = 'NOT consistent'
    _show('Dimensions', [_w('LHS ' + lhs), _w('RHS ' + rhs), res])

# ---------- oblique impact: sphere and a smooth surface ----------
def t_oblique_wall():
    # i15/i17. The whole question turns on one modelling assumption: the
    # surface is SMOOTH, so it can exert no impulse along itself and the
    # component of velocity parallel to the surface is unchanged. Newton's
    # Experimental Law is applied to the normal component only.
    _show('Oblique: sphere/wall', ['Sphere hits a SMOOTH fixed surface.',
        'Resolve u along the surface and',
        'along the normal.',
        'SMOOTH => no impulse along the',
        'surface, so that part is',
        'UNCHANGED.',
        'NEL on the normal part only:',
        'normal out = e x normal in.'])
    u = _asknum('speed u')
    a = _asknum('angle to surface (deg)')
    e = _asknum('e (0..1)')
    if None in (u, a, e):
        return
    ra = _rad(a)
    tang = u * math.cos(ra)          # along the surface
    nin = u * math.sin(ra)           # into the surface, along the normal
    nout = e * nin                   # NEL, and it reverses
    v = math.sqrt(tang * tang + nout * nout)
    aout = _deg(_atan2(nout, tang))  # to the surface
    lines = [_w('u = ' + _fn(u) + ' m/s at ' + _fn(a) + ' deg'),
        _w('  to the surface'),
        _w('  (= ' + _fn(90.0 - a) + ' deg to the normal)'),
        _w('e = ' + _fn(e)), '',
        _warn('ASSUMPTION: smooth surface, so'),
        _warn('the component along the surface'),
        _warn('is UNCHANGED (no impulse on it)'),
        _w('along surface = ' + _fn(tang) + ' m/s'), '',
        _w('normal in = ' + _fn(nin) + ' m/s'),
        _w('NEL: normal out = e x normal in'),
        _w('normal out = ' + _fn(nout) + ' m/s'), '',
        'speed = ' + _fn(v) + ' m/s',
        'angle to surface = ' + _fn(aout) + ' deg',
        'angle to normal = ' + _fn(90.0 - aout) + ' deg',
        _w('tan(out to normal)'),
        _w('  = tan(in to normal) / e')]
    m = _asknum('mass m (or cancel to skip)')
    if m is not None:
        lines.append('')
        lines.append('KE lost = ' + _fn(0.5 * m * (u * u - v * v)) + ' J')
        lines.append(_w('  = 0.5 m (normal in)^2 (1-e^2)'))
        lines.append('impulse = ' + _fn(m * (1.0 + e) * nin) + ' N s')
        lines.append('  along the normal')
    _show('Oblique: sphere/wall', lines)

# ---------- oblique impact: two smooth spheres ----------
def t_oblique_spheres():
    # i14/i16/i17. Resolve along the line of centres: that is the only
    # direction in which the spheres push each other, because they are smooth.
    _show('Oblique: two spheres', ['Two SMOOTH spheres. Resolve along',
        'the line of centres (LOC).',
        'SMOOTH => no impulse',
        'perpendicular to the LOC, so',
        'each perpendicular part is',
        'UNCHANGED.',
        'Along the LOC: conservation of',
        'momentum and NEL.',
        'Angles are measured from the LOC.'])
    m1 = _asknum('m1')
    u1 = _asknum('speed u1')
    a1 = _asknum('angle of u1 to LOC (deg)')
    m2 = _asknum('m2')
    u2 = _asknum('speed u2')
    a2 = _asknum('angle of u2 to LOC (deg)')
    e = _asknum('e (0..1)')
    if None in (m1, u1, a1, m2, u2, a2, e):
        return
    if m1 + m2 == 0:
        _show('Oblique: two spheres', [_warn('total mass 0')])
        return
    x1 = u1 * math.cos(_rad(a1))
    y1 = u1 * math.sin(_rad(a1))
    x2 = u2 * math.cos(_rad(a2))
    y2 = u2 * math.sin(_rad(a2))
    p = m1 * x1 + m2 * x2
    sep = e * (x1 - x2)
    v1 = (p - m2 * sep) / (m1 + m2)
    v2 = v1 + sep
    s1 = math.sqrt(v1 * v1 + y1 * y1)
    s2 = math.sqrt(v2 * v2 + y2 * y2)
    d1 = _deg(_atan2(y1, v1))
    d2 = _deg(_atan2(y2, v2))
    kel = 0.5 * m1 * (x1 * x1 - v1 * v1) + 0.5 * m2 * (x2 * x2 - v2 * v2)
    _show('Oblique: two spheres', [_warn('ASSUMPTION: smooth spheres, so'),
        _warn('the parts perpendicular to the'),
        _warn('LOC are UNCHANGED'),
        _w('perp 1 = ' + _fn(y1) + ' m/s'),
        _w('perp 2 = ' + _fn(y2) + ' m/s'), '',
        _w('along LOC before:'),
        _w('u1 = ' + _fn(x1) + '  u2 = ' + _fn(x2)),
        _w('momentum ' + _fn(p) + ' kg m/s'),
        _w('NEL: separation = e x approach'), '',
        _w('v1 along LOC = ' + _fn(v1) + ' m/s'),
        _w('v2 along LOC = ' + _fn(v2) + ' m/s'), '',
        'speed 1 = ' + _fn(s1) + ' m/s',
        'angle 1 = ' + _fn(d1) + ' deg to LOC',
        'speed 2 = ' + _fn(s2) + ' m/s',
        'angle 2 = ' + _fn(d2) + ' deg to LOC', '',
        'KE lost = ' + _fn(kel) + ' J'])

# ---------- projectile: cartesian equation of the path ----------
def t_proj_path():
    # Mv3/v4/v5: eliminate t between x = u cos(a) t and y = u sin(a) t - gt^2/2.
    _show('Projectile path', ['x = u cos(a) t',
        'y = u sin(a) t - g t^2 / 2',
        'from the first, t = x/(u cos a),',
        'and substituting gives',
        'y = x tan a - g x^2/(2u^2cos^2a)',
        'a parabola through the origin.'])
    u = _asknum('speed u')
    a = _asknum('angle to horizontal (deg)')
    if None in (u, a):
        return
    g = _askg()
    ra = _rad(a)
    ca = math.cos(ra)
    if g <= 0 or u == 0 or abs(ca) < 1e-9:
        _show('Projectile path', [_warn('need g > 0, u > 0 and the'),
            _warn('angle away from 90 deg -'),
            _warn('a vertical launch has no'),
            _warn('cartesian path.')])
        return
    ta = math.tan(ra)
    kk = g / (2.0 * u * u * ca * ca)
    rng = 2.0 * u * u * math.sin(ra) * ca / g
    hmax = u * u * math.sin(ra) * math.sin(ra) / (2.0 * g)
    tof = 2.0 * u * math.sin(ra) / g
    lines = [_w('u = ' + _fn(u) + ' m/s at ' + _fn(a) + ' deg'),
        _w('g = ' + _fn(g)), '',
        'y = ' + _fn(ta) + ' x - ' + _fn(kk) + ' x^2', '',
        _w('tan a = ' + _fn(ta)),
        _w('g/(2u^2cos^2a) = ' + _fn(kk)), '',
        'range = ' + _fn(rng) + ' m',
        'max height = ' + _fn(hmax) + ' m',
        'time of flight = ' + _fn(tof) + ' s', '',
        'bounding parabola (all angles):',
        'y = ' + _fn(u * u / (2.0 * g)) + ' - ' +
        _fn(g / (2.0 * u * u)) + ' x^2']
    xq = _asknum('y at x = (or cancel)')
    if xq is not None:
        lines.append('')
        lines.append('y(' + _fn(xq) + ') = ' + _fn(xq * ta - kk * xq * xq) + ' m')
    _show('Projectile path', lines)
    if rng <= 0 or rng > 1e7:
        return
    xs = []
    ys = []
    i = 0
    while i <= 60:
        xv = rng * i / 60.0
        xs.append(xv)
        ys.append(xv * ta - kk * xv * xv)
        i += 1
    xr = casutil.nice_range(xs, 0.05, True)
    yr = casutil.nice_range(ys, 0.10, True)
    fr = casutil.frame(xr[0], xr[1], yr[0], yr[1])
    casutil.axes(fr, 'projectile path', 'x', 'y')
    i = 1
    while i <= 60:
        casutil.seg(fr, xs[i - 1], ys[i - 1], xs[i], ys[i], casui.ACC)
        i += 1
    casutil.chart_hold('range ' + _fn(rng) + ' m')

# ---------- projectile up or down an inclined plane ----------
def t_proj_incline():
    # v6/v7. Plane at b to the horizontal, launch angle a from the HORIZONTAL.
    # Landing when y = x tan b gives t = 2u sin(a-b)/(g cos b), so the range
    # measured up the slope is R = 2u^2 cos a sin(a-b)/(g cos^2 b).
    # dR/da = 0 at 2a - b = 90 deg, giving R_max = u^2/(g(1+sin b)).
    # b = 0 recovers the level-ground results: 45 deg and u^2/g.
    _show('Projectile: incline', ['Plane at b deg to the horizontal.',
        'b > 0 fires UP the slope,',
        'b < 0 fires DOWN the slope,',
        'b = 0 is level ground.',
        'a is measured from the',
        'HORIZONTAL.',
        'R = 2u^2 cos a sin(a-b)',
        '        / (g cos^2 b)'])
    u = _asknum('speed u')
    a = _asknum('angle a to horizontal (deg)')
    b = _asknum('slope b (deg, + up, - down)')
    if None in (u, a, b):
        return
    g = _askg()
    ra = _rad(a)
    rb = _rad(b)
    cb = math.cos(rb)
    if g <= 0 or abs(cb) < 1e-9:
        _show('Projectile: incline', [_warn('need g > 0 and |b| < 90 deg')])
        return
    tof = 2.0 * u * math.sin(ra - rb) / (g * cb)
    rr = 2.0 * u * u * math.cos(ra) * math.sin(ra - rb) / (g * cb * cb)
    besta = 45.0 + b / 2.0
    rmax = u * u / (g * (1.0 + math.sin(rb)))
    lines = [_w('u = ' + _fn(u) + ' m/s at ' + _fn(a) + ' deg'),
        _w('slope b = ' + _fn(b) + ' deg, g = ' + _fn(g)), '']
    if tof <= 0:
        lines.append(_warn('a is not above the slope, so the'))
        lines.append(_warn('particle does not travel up it:'))
        lines.append(_warn('need a > b.'))
    else:
        lines.append('time of flight = ' + _fn(tof) + ' s')
        lines.append('range along plane = ' + _fn(rr) + ' m')
        lines.append('horizontal range = ' + _fn(rr * cb) + ' m')
        lines.append('rise along plane = ' + _fn(rr * math.sin(rb)) + ' m')
    lines.append('')
    lines.append(_w('maximum range: 2a - b = 90 deg'))
    lines.append('best angle = ' + _fn(besta) + ' deg')
    lines.append('  (to the horizontal)')
    lines.append('max range = ' + _fn(rmax) + ' m')
    lines.append(_w('  = u^2 / (g(1 + sin b))'))
    if abs(b) < 1e-9:
        lines.append(_w('level ground: 45 deg, u^2/g'))
    _show('Projectile: incline', lines)

# ---------- elastic strings and springs: equilibrium and energy ----------
def t_elastic():
    # h5 and h7.
    _show('Elastic: equil/energy', ['1 equilibrium: m g = lam x / l',
        '2 max extension by energy',
        '3 modulus from a known extension'])
    k = _choose('Choose 1-3')
    if k is None:
        return
    if k == 2:
        m = _asknum('mass m')
        lam = _asknum('lambda (modulus)')
        l = _asknum('natural length l')
        v = _asknum('speed when the string')
        if None in (m, lam, l, v) or lam <= 0 or l <= 0 or m <= 0:
            _show('Elastic: max extension', [_warn('need m, lambda, l all > 0')])
            return
        g = _askg()
        # 0.5 m v^2 + m g x = lam x^2 / (2 l)   (KE + GPE = EPE)
        q = l * m * g / lam
        disc = q * q + l * m * v * v / lam
        if disc < 0:
            return
        x = q + math.sqrt(disc)
        epe = lam * x * x / (2.0 * l)
        _show('Elastic: max extension', [_w('KE + GPE lost = EPE gained'),
            _w('0.5 m v^2 + m g x = lam x^2/(2l)'), '',
            'KE at that instant = ' + _fn(0.5 * m * v * v) + ' J',
            'max extension x = ' + _fn(x) + ' m',
            'GPE lost = ' + _fn(m * g * x) + ' J',
            'EPE stored = ' + _fn(epe) + ' J',
            'total length = ' + _fn(l + x) + ' m',
            _w('(v = 0 gives x = 2 m g l / lam,'),
            _w(' twice the equilibrium value)')])
        return
    if k == 3:
        m = _asknum('mass m')
        l = _asknum('natural length l')
        x = _asknum('equilibrium extension x')
        if None in (m, l, x) or x == 0:
            _show('Elastic: modulus', [_warn('need a non-zero extension')])
            return
        g = _askg()
        lam = m * g * l / x
        _show('Elastic: modulus', [_w('m g = lam x / l  =>'),
            _w('lam = m g l / x'),
            'lambda = ' + _fn(lam) + ' N',
            'stiffness k = lam/l = ' + _fn(lam / l if l else 0.0) + ' N/m',
            'tension T = m g = ' + _fn(m * g) + ' N'])
        return
    m = _asknum('mass m')
    lam = _asknum('lambda (modulus)')
    l = _asknum('natural length l')
    if None in (m, lam, l) or lam == 0 or l == 0:
        _show('Elastic: equilibrium', [_warn('need lambda and l non-zero')])
        return
    g = _askg()
    x = m * g * l / lam
    _show('Elastic: equilibrium', [_w('hanging in equilibrium:'),
        _w('T = m g  and  T = lam x / l'),
        _w('so x = m g l / lam'), '',
        'extension x = ' + _fn(x) + ' m',
        'tension T = ' + _fn(m * g) + ' N',
        'total length = ' + _fn(l + x) + ' m',
        'EPE there = ' + _fn(lam * x * x / (2.0 * l)) + ' J'])

# ---------- centre of mass by calculus ----------
def t_com_calculus():
    # G7/G9/MG6.
    _show('COM by calculus', ['1 lamina under y = f(x)',
        '2 solid of revolution about Ox',
        '3 solid of revolution about Oy',
        'strips: mass is proportional to',
        'y dx for a lamina and to y^2 dx',
        'for a solid.'])
    k = _choose('Choose 1-3')
    if k is None:
        return
    if k == 3:
        f = _askexpr('x = g(y) =')
        var = 'y'
    else:
        f = _askexpr('y = f(x) =')
        var = 'x'
    if f is None:
        return
    a = _asknum(var + ' from')
    b = _asknum(var + ' to')
    if None in (a, b):
        return
    if b < a:
        a, b = b, a
    if b == a:
        _show('COM by calculus', [_warn('the limits are equal')])
        return
    sq = ('^', f, ('n', 2))
    vt = ('v', var)
    if k == 1:
        area = _defi(f, a, b, var)
        mx = _defi(('*', vt, f), a, b, var)
        my = _defi(('/', sq, ('n', 2)), a, b, var)
        if area is None or mx is None or my is None or area == 0:
            _show('COM: lamina', [_warn('could not integrate over'),
                _warn('that interval')])
            return
        _show('COM: lamina', [_w('uniform lamina under'),
            _w('y = ' + caseng.tostr(f)),
            _w('from x = ' + _fn(a) + ' to ' + _fn(b)), '',
            _w('A = int y dx'),
            'area A = ' + _fn(area), '',
            _w('x_bar = int x y dx / A'),
            _w('int x y dx = ' + _fn(mx)),
            'x_bar = ' + _fn(mx / area), '',
            _w('y_bar = int (y^2/2) dx / A'),
            _w('int y^2/2 dx = ' + _fn(my)),
            'y_bar = ' + _fn(my / area)])
        return
    i0 = _defi(sq, a, b, var)
    i1 = _defi(('*', vt, sq), a, b, var)
    if i0 is None or i1 is None or i0 == 0:
        _show('COM: solid', [_warn('could not integrate over'),
            _warn('that interval')])
        return
    axis = 'Ox' if k == 2 else 'Oy'
    other = 'y' if k == 2 else 'x'
    _show('COM: solid', [_w('solid of revolution about ' + axis),
        _w(('y = ' if k == 2 else 'x = ') + caseng.tostr(f)),
        _w('from ' + var + ' = ' + _fn(a) + ' to ' + _fn(b)), '',
        _w('V = pi int ' + ('y^2 dx' if k == 2 else 'x^2 dy')),
        _w('int = ' + _fn(i0)),
        'volume V = ' + _fn(math.pi * i0), '',
        _w(var + '_bar = int ' + var + ' r^2 d' + var + ' / int r^2 d' + var),
        _w('int ' + var + ' r^2 = ' + _fn(i1)),
        var + '_bar = ' + _fn(i1 / i0),
        other + '_bar = 0 by symmetry'])

# ---------- centres of mass of standard uniform bodies ----------
def t_com_standard():
    # G3. Distances are measured along the axis of symmetry from the point
    # named on each line.
    _show('Standard bodies', ['1 rod, length L',
        '2 triangular lamina, height h',
        '3 circular arc, r, half-angle A',
        '4 semicircular arc, r',
        '5 circular sector, r, half-angle A',
        '6 semicircular lamina, r',
        '7 solid hemisphere, r',
        '8 hollow hemisphere, r',
        '9 solid cone/pyramid, height h',
        '10 hollow cone, height h'])
    k = _choose('Choose 1-10')
    if k is None or k < 1 or k > 10:
        return
    if k in (3, 5):
        r = _asknum('radius r')
        ang = _asknum('half-angle A (deg)')
        if None in (r, ang):
            return
        aa = _rad(ang)
        if abs(aa) < 1e-12:
            _show('Standard bodies', [_warn('half-angle must be non-zero')])
            return
        if k == 3:
            d = r * math.sin(aa) / aa
            _show('Circular arc', ['centre of mass on the axis',
                'of symmetry, from the CENTRE',
                _w('d = r sin A / A  (A in radians)'),
                _w('A = ' + _fn(aa) + ' rad'),
                'distance = ' + _fn(d)])
        else:
            d = 2.0 * r * math.sin(aa) / (3.0 * aa)
            _show('Circular sector', ['from the CENTRE of the circle',
                _w('d = 2 r sin A / (3 A)'),
                _w('A = ' + _fn(aa) + ' rad'),
                'distance = ' + _fn(d)])
        return
    if k in (1, 2, 9, 10):
        s = _asknum('length L' if k == 1 else 'height h')
    else:
        s = _asknum('radius r')
    if s is None:
        return
    if k == 1:
        _show('Uniform rod', ['at the midpoint',
            _w('d = L / 2'), 'distance = ' + _fn(s / 2.0), 'from either end'])
    elif k == 2:
        _show('Triangular lamina', [_w('at the centroid: the mean of'),
            _w('the three vertices, and 2/3 of'),
            _w('the way down each median'),
            _w('d = h / 3'), 'distance = ' + _fn(s / 3.0),
            'above the base'])
    elif k == 4:
        _show('Semicircular arc', ['a uniform wire, from the CENTRE',
            _w('d = 2 r / pi'),
            'distance = ' + _fn(2.0 * s / math.pi)])
    elif k == 6:
        _show('Semicircular lamina', ['from the CENTRE of the',
            'bounding diameter',
            _w('d = 4 r / (3 pi)'),
            'distance = ' + _fn(4.0 * s / (3.0 * math.pi))])
    elif k == 7:
        _show('Solid hemisphere', ['from the CENTRE of the flat face',
            _w('d = 3 r / 8'),
            'distance = ' + _fn(3.0 * s / 8.0)])
    elif k == 8:
        _show('Hollow hemisphere', ['a shell, from the CENTRE of',
            'the rim',
            _w('d = r / 2'), 'distance = ' + _fn(s / 2.0)])
    elif k == 9:
        _show('Solid cone/pyramid', ['on the axis, from the APEX',
            _w('d = 3 h / 4'),
            'distance = ' + _fn(3.0 * s / 4.0),
            '(= h/4 above the base,',
            ' i.e. ' + _fn(s / 4.0) + ')'])
    else:
        _show('Hollow cone', ['the curved surface only,',
            'from the APEX',
            _w('d = 2 h / 3'),
            'distance = ' + _fn(2.0 * s / 3.0),
            '(= h/3 above the base,',
            ' i.e. ' + _fn(s / 3.0) + ')'])

# ---------- sliding versus toppling ----------
def t_topple():
    # d16, G5, G10. Two ways equilibrium can break, and the one that happens
    # is whichever needs the smaller tilt (or the smaller push).
    _show('Slide or topple', ['1 body on a plane being tilted',
        '2 horizontal force on a block',
        'toppling turns about the far',
        'edge; sliding needs F > mu R.'])
    k = _choose('Choose 1 or 2')
    if k is None:
        return
    if k == 2:
        w = _asknum('weight W')
        aa = _asknum('base half-width a')
        y = _asknum('height y of the force')
        mu = _asknum('mu')
        if None in (w, aa, y, mu) or y == 0:
            _show('Slide or topple', [_warn('need a non-zero height y')])
            return
        psl = mu * w
        pto = w * aa / y
        if pto < psl:
            first = 'topples first'
        elif psl < pto:
            first = 'slides first'
        else:
            first = 'slides and topples together'
        _show('Push on a block', [_w('sliding needs P > mu W'),
            _w('toppling needs P y > W a'), '',
            'P to slide = ' + _fn(psl) + ' N',
            'P to topple = ' + _fn(pto) + ' N',
            first])
        return
    aa = _asknum('base half-width a')
    h = _asknum('height h of the COM')
    mu = _asknum('mu')
    if None in (aa, h, mu) or h <= 0:
        _show('Slide or topple', [_warn('need h > 0')])
        return
    tto = _deg(math.atan(aa / h))
    tsl = _deg(math.atan(mu))
    if tto < tsl:
        first = 'topples first'
    elif tsl < tto:
        first = 'slides first'
    else:
        first = 'slides and topples together'
    lines = [_w('topples when tan th > a/h'),
        _w('slides when tan th > mu'), '',
        'topple angle = ' + _fn(tto) + ' deg',
        'slide angle = ' + _fn(tsl) + ' deg',
        first]
    th = _asknum('plane angle (deg, or cancel)')
    if th is not None:
        lines.append('')
        lines.append('at ' + _fn(th) + ' deg:')
        t = math.tan(_rad(th))
        lines.append('  ' + ('topples' if t > aa / h else 'does not topple'))
        lines.append('  ' + ('slides' if t > mu else 'does not slide'))
    _show('Tilting plane', lines)

# ---------- couples ----------
def t_couple():
    # d13. Two equal, opposite, parallel forces: zero resultant, but a turning
    # effect of the same size about EVERY point.
    _show('Couple', ['A couple is two equal, opposite,',
        'parallel forces F a distance d',
        'apart (d measured at right',
        'angles to them).',
        'Resultant force = 0, so it',
        'cannot be balanced by one force.',
        'Moment G = F d about any point.'])
    f = _asknum('force F')
    d = _asknum('distance d apart')
    if None in (f, d):
        return
    lines = [_w('G = F d'),
        'moment G = ' + _fn(f * d) + ' N m',
        'resultant force = 0 N', '',
        _w('demonstration: F up at x = 0'),
        _w('and F down at x = ' + _fn(d))]
    p = _asknum('moments about x = p (or cancel)')
    if p is not None:
        m0 = (0.0 - p) * f
        m1 = (d - p) * (-f)
        lines.append(_w('about x = ' + _fn(p) + ':'))
        lines.append(_w('  ' + _fn(m0) + ' + ' + _fn(m1)))
        lines.append('moment about p = ' + _fn(m0 + m1) + ' N m')
        lines.append(_w('  size F d whatever p is'))
    _show('Couple', lines)

# ---------- triangle of forces ----------
def t_triangle_forces():
    # d9. Three forces in equilibrium have zero resultant, so drawn head to
    # tail they close up into a triangle.
    _show('Triangle of forces', ['Three forces in equilibrium draw',
        'a CLOSED triangle head to tail.',
        '1 three magnitudes -> the angles',
        '  between the forces',
        '2 two forces -> the third'])
    k = _choose('Choose 1 or 2')
    if k is None:
        return
    if k == 2:
        f1 = _asknum('F1 magnitude')
        d1 = _asknum('F1 direction (deg)')
        f2 = _asknum('F2 magnitude')
        d2 = _asknum('F2 direction (deg)')
        if None in (f1, d1, f2, d2):
            return
        x1 = f1 * math.cos(_rad(d1))
        y1 = f1 * math.sin(_rad(d1))
        x2 = f2 * math.cos(_rad(d2))
        y2 = f2 * math.sin(_rad(d2))
        sx = x1 + x2
        sy = y1 + y2
        mag = math.sqrt(sx * sx + sy * sy)
        dr = _deg(_atan2(-sy, -sx))
        if dr < 0:
            dr += 360.0
        _show('Third force', [_w('for equilibrium F3 = -(F1 + F2)'),
            _w('F1 + F2 = (' + _fn(sx) + ', ' + _fn(sy) + ')'),
            'F3 = (' + _fn(-sx) + ', ' + _fn(-sy) + ')',
            'F3 = ' + _fn(mag) + ' N',
            'direction = ' + _fn(dr) + ' deg',
            _w('the three vectors head to tail'),
            _w('close the triangle.')])
        pts = [(0.0, 0.0), (x1, y1), (sx, sy), (0.0, 0.0)]
        _draw_polygon(pts, 'triangle of forces')
        return
    fs = _getlist('three magnitudes')
    if fs is None or len(fs) != 3:
        _show('Triangle of forces', [_warn('need three numbers,'),
            'e.g.  3 4 5'])
        return
    a, b, c = fs[0], fs[1], fs[2]
    if a <= 0 or b <= 0 or c <= 0:
        _show('Triangle of forces', [_warn('magnitudes must be positive')])
        return
    if a + b <= c or b + c <= a or c + a <= b:
        _show('Triangle of forces', [_warn('these cannot close into a'),
            _warn('triangle, so the three forces'),
            _warn('cannot be in equilibrium.')])
        return
    ca = casutil.acos_safe((b * b + c * c - a * a) / (2.0 * b * c))
    cb = casutil.acos_safe((c * c + a * a - b * b) / (2.0 * c * a))
    cc = casutil.acos_safe((a * a + b * b - c * c) / (2.0 * a * b))
    _show('Angles between forces', [_w('cosine rule on the closed'),
        _w('triangle; the angle between two'),
        _w('forces is 180 - the interior'),
        _w('angle opposite the third.'), '',
        'F1 to F2 = ' + _fn(180.0 - _deg(cc)) + ' deg',
        'F2 to F3 = ' + _fn(180.0 - _deg(ca)) + ' deg',
        'F3 to F1 = ' + _fn(180.0 - _deg(cb)) + ' deg',
        _w('(they add to 360)'), '',
        _w('Lami: F1/sin(F2^F3) = ...')])
    px = (a * a + c * c - b * b) / (2.0 * a)
    py2 = c * c - px * px
    py = math.sqrt(py2) if py2 > 0 else 0.0
    _draw_polygon([(0.0, 0.0), (a, 0.0), (px, py), (0.0, 0.0)],
                  'triangle of forces')

def _draw_polygon(pts, title):
    xs = []
    ys = []
    for p in pts:
        xs.append(p[0])
        ys.append(p[1])
    xr = casutil.nice_range(xs, 0.12, True)
    yr = casutil.nice_range(ys, 0.12, True)
    fr = casutil.frame(xr[0], xr[1], yr[0], yr[1])
    casutil.axes(fr, title, 'x', 'y')
    i = 1
    while i < len(pts):
        casutil.seg(fr, pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1],
                    casui.ACC)
        casutil.marker(fr, pts[i][0], pts[i][1])
        i += 1
    casutil.chart_hold('it closes: resultant is zero')

# ---------- units from dimensions, and changing units ----------
_NAMED = [
    (0.0, 0.0, 0.0, 'dimensionless (e, mu, an angle)'),
    (1.0, 0.0, 0.0, 'mass'),
    (0.0, 1.0, 0.0, 'length'),
    (0.0, 0.0, 1.0, 'time'),
    (0.0, 2.0, 0.0, 'area'),
    (0.0, 3.0, 0.0, 'volume'),
    (0.0, 1.0, -1.0, 'velocity or speed'),
    (0.0, 1.0, -2.0, 'acceleration'),
    (0.0, 0.0, -1.0, 'frequency / angular speed'),
    (1.0, -3.0, 0.0, 'density'),
    (1.0, 1.0, -1.0, 'momentum or impulse (N s)'),
    (1.0, 1.0, -2.0, 'force or weight (N)'),
    (1.0, 2.0, -2.0, 'work, energy or moment (J)'),
    (1.0, 2.0, -3.0, 'power (W)'),
    (1.0, -1.0, -2.0, 'pressure or stress (Pa)'),
    (1.0, 0.0, -2.0, 'stiffness (N/m)'),
    (1.0, 2.0, -1.0, 'angular momentum'),
]

def _unitstr(p):
    nm = ['kg', 'm', 's']
    out = ''
    for i in range(3):
        if p[i] == 0:
            continue
        if out:
            out += ' '
        out += nm[i]
        if p[i] != 1:
            out += '^' + _fn(p[i])
    if out == '':
        return 'no units (dimensionless)'
    return out

def t_units():
    # q3 (units from dimensions) and q4 (changing the units used).
    _show('Units', ['1 SI units from M L T powers',
        '2 change the units used',
        'e.g. force is M L T^-2, so it is',
        'measured in kg m s^-2.'])
    k = _choose('Choose 1 or 2')
    if k is None:
        return
    p = _getlist('M L T powers, e.g. 1 1 -2')
    if p is None or len(p) != 3:
        _show('Units', [_warn('need 3 numbers, e.g.  1 1 -2')])
        return
    us = _unitstr(p)
    name = None
    for row in _NAMED:
        if row[0] == p[0] and row[1] == p[1] and row[2] == p[2]:
            name = row[3]
    if k != 2:
        lines = [_w('M^' + _fn(p[0]) + ' L^' + _fn(p[1]) + ' T^' + _fn(p[2])),
            'SI units: ' + us]
        if name is not None:
            lines.append('this is ' + name)
        else:
            lines.append('(not a named quantity here)')
        if p[0] == 0 and p[1] == 0 and p[2] == 0:
            lines.append(_w('a dimensionless quantity: its'))
            lines.append(_w('value is the same in any'))
            lines.append(_w('consistent system of units.'))
        _show('Units', lines)
        return
    v = _asknum('value in kg, m, s')
    fac = _getlist('new units in kg m s')
    if v is None or fac is None or len(fac) != 3:
        _show('Units', [_warn('need the value and 3 factors,'),
            'e.g. 1 1000 3600 for km and h'])
        return
    if fac[0] <= 0 or fac[1] <= 0 or fac[2] <= 0:
        _show('Units', [_warn('unit sizes must be positive')])
        return
    d = (fac[0] ** p[0]) * (fac[1] ** p[1]) * (fac[2] ** p[2])
    if d == 0:
        _show('Units', [_warn('conversion factor is zero')])
        return
    _show('Change of units', [_w('quantity in ' + us),
        _w('value = ' + _fn(v)), '',
        _w('1 new mass unit = ' + _fn(fac[0]) + ' kg'),
        _w('1 new length unit = ' + _fn(fac[1]) + ' m'),
        _w('1 new time unit = ' + _fn(fac[2]) + ' s'), '',
        _w('divide by ' + _fn(fac[0]) + '^' + _fn(p[0]) + ' x ' +
        _fn(fac[1]) + '^' + _fn(p[1]) + ' x ' +
        _fn(fac[2]) + '^' + _fn(p[2])),
        'factor = ' + _fn(d),
        'new value = ' + _fn(v / d)])

# ---------- relative position and velocity in 2-D ----------
def t_relative():
    # Mk1.
    _show('Relative motion', ['Enter each vector as  x y .',
        'r_B rel A = r_B - r_A',
        'v_B rel A = v_B - v_A',
        'B seen from A moves in a',
        'straight line at the relative',
        'velocity.'])
    ra = _getlist('A position  x y')
    va = _getlist('A velocity  x y')
    rb = _getlist('B position  x y')
    vb = _getlist('B velocity  x y')
    if ra is None or va is None or rb is None or vb is None:
        return
    if len(ra) != 2 or len(va) != 2 or len(rb) != 2 or len(vb) != 2:
        _show('Relative motion', [_warn('need two numbers in each'),
            'entry, e.g.  3 -4'])
        return
    rx = rb[0] - ra[0]
    ry = rb[1] - ra[1]
    vx = vb[0] - va[0]
    vy = vb[1] - va[1]
    d0 = math.sqrt(rx * rx + ry * ry)
    sp = math.sqrt(vx * vx + vy * vy)
    lines = ['r rel = (' + _fn(rx) + ', ' + _fn(ry) + ')',
        'distance now = ' + _fn(d0) + ' m',
        'v rel = (' + _fn(vx) + ', ' + _fn(vy) + ')',
        'rel speed = ' + _fn(sp) + ' m/s']
    if sp > 0:
        lines.append('direction = ' + _fn(_deg(_atan2(vy, vx))) + ' deg')
        lines.append('  (anticlockwise from Ox)')
        ts = -(rx * vx + ry * vy) / (sp * sp)
        if ts < 0:
            ts = 0.0
        cx = rx + vx * ts
        cy = ry + vy * ts
        lines.append('')
        lines.append('closest at t = ' + _fn(ts) + ' s')
        lines.append('least distance = ' +
                     _fn(math.sqrt(cx * cx + cy * cy)) + ' m')
    else:
        lines.append('')
        lines.append('same velocity: the distance')
        lines.append('never changes.')
    tq = _asknum('distance at t = (or cancel)')
    if tq is not None:
        px = rx + vx * tq
        py = ry + vy * tq
        lines.append('')
        lines.append('at t = ' + _fn(tq) + ': r rel = (' + _fn(px) +
                     ', ' + _fn(py) + ')')
        lines.append('distance = ' + _fn(math.sqrt(px * px + py * py)) + ' m')
    _show('Relative motion', lines)

TOOLS = [
    ('Momentum & impulse', t_momentum),
    ('Restitution', t_restitution),
    ('Oblique impact: wall', t_oblique_wall),
    ('Oblique impact: spheres', t_oblique_spheres),
    ('Work/Energy/Power', t_work),
    ('Projectile path (cartesian)', t_proj_path),
    ('Projectile on an incline', t_proj_incline),
    ('Circular motion', t_circular),
    ('Hookes law / EPE', t_hooke),
    ('Elastic equilibrium/energy', t_elastic),
    ('Centre of mass', t_com),
    ('COM by calculus', t_com_calculus),
    ('COM standard bodies', t_com_standard),
    ('Slide or topple', t_topple),
    ('Couple', t_couple),
    ('Triangle of forces', t_triangle_forces),
    ('Relative motion 2-D', t_relative),
    ('Dimensional analysis', t_dim),
    ('Units & conversion', t_units),
]

def run():
    casutil.run_tools('Mechanics (FM)', TOOLS)
