import math
import casui
import caslex
import caseng
import cascalc
import casutil

_asknum = casutil.asknum
_askopt = casutil.asknum
_askg = casutil.askg
_fn = casutil.fmt
_atan2 = casutil.atan2
_deg = casutil.deg
_rad = casutil.rad
_show = casutil.show
_w = casutil.w
_warn = casutil.warn


def suvat():
    casui.show_text('SUVAT', 'Enter known values.\nLeave unknowns blank/Cancel.\nNeed any 3 of u v a s t.', casui.BLACK)
    u = _askopt('u (init vel)=')
    v = _askopt('v (final vel)=')
    a = _askopt('a (accel)=')
    s = _askopt('s (displ)=')
    t = _askopt('t (time)=')
    known = 0
    for q in (u, v, a, s, t):
        if q is not None:
            known += 1
    if known < 3:
        _show('SUVAT', ['Need at least 3 knowns.', 'Got ' + str(known) + '.'])
        return
    rooted = [False]
    for _it in range(6):
        prog = False
        if v is None and u is not None and a is not None and t is not None:
            v = u + a * t
            prog = True
        if u is None and v is not None and a is not None and t is not None:
            u = v - a * t
            prog = True
        if a is None and v is not None and u is not None and t is not None and t != 0:
            a = (v - u) / t
            prog = True
        if t is None and v is not None and u is not None and a is not None and a != 0:
            t = (v - u) / a
            prog = True
        if s is None and u is not None and v is not None and t is not None:
            s = 0.5 * (u + v) * t
            prog = True
        if t is None and s is not None and u is not None and v is not None and (u + v) != 0:
            t = 2.0 * s / (u + v)
            prog = True
        if s is None and u is not None and a is not None and t is not None:
            s = u * t + 0.5 * a * t * t
            prog = True
        if v is None and u is not None and a is not None and s is not None:
            d = u * u + 2.0 * a * s
            if d >= 0:
                v = math.sqrt(d)
                rooted[0] = True
                prog = True
        if u is None and v is not None and a is not None and s is not None:
            d = v * v - 2.0 * a * s
            if d >= 0:
                u = math.sqrt(d)
                rooted[0] = True
                prog = True
        if a is None and v is not None and u is not None and s is not None and s != 0:
            a = (v * v - u * u) / (2.0 * s)
            prog = True
        if s is None and v is not None and u is not None and a is not None and a != 0:
            s = (v * v - u * u) / (2.0 * a)
            prog = True
        if a is None and s is not None and u is not None and t is not None and t != 0:
            a = 2.0 * (s - u * t) / (t * t)
            prog = True
        if u is None and s is not None and a is not None and t is not None and t != 0:
            u = (s - 0.5 * a * t * t) / t
            prog = True
        if a is None and s is not None and v is not None and t is not None and t != 0:
            a = 2.0 * (v * t - s) / (t * t)
            prog = True
        if not prog:
            break
    lines = []
    lines.append('u = ' + (_fn(u) if u is not None else '?'))
    lines.append('v = ' + (_fn(v) if v is not None else '?'))
    lines.append('a = ' + (_fn(a) if a is not None else '?'))
    lines.append('s = ' + (_fn(s) if s is not None else '?'))
    lines.append('t = ' + (_fn(t) if t is not None else '?'))
    if rooted[0]:
        lines.append(_warn('(sqrt step: positive root'))
        lines.append(_warn(' taken - check direction)'))
    _show('SUVAT result', lines)


def projectile():
    g = _askg()
    u = _asknum('launch speed u=')
    if u is None:
        return
    ad = _asknum('angle deg=')
    if ad is None:
        return
    a = _rad(ad)
    if g == 0:
        _show('Projectile', ['g must be nonzero.'])
        return
    tof = 2.0 * u * math.sin(a) / g
    hmax = (u * math.sin(a)) ** 2 / (2.0 * g)
    rng = u * u * math.sin(2.0 * a) / g
    l1 = ['Time of flight = ' + _fn(tof) + ' s', 'Max height = ' + _fn(hmax) + ' m',
          'Range = ' + _fn(rng) + ' m', _w('ux = ' + _fn(u * math.cos(a))),
          _w('uy = ' + _fn(u * math.sin(a)))]
    _show('Projectile', l1)
    t = _askopt('time t (blank skip)=')
    if t is None:
        return
    x = u * math.cos(a) * t
    y = u * math.sin(a) * t - 0.5 * g * t * t
    vx = u * math.cos(a)
    vy = u * math.sin(a) - g * t
    spd = math.sqrt(vx * vx + vy * vy)
    dirn = _deg(_atan2(vy, vx))
    l2 = ['At t = ' + _fn(t) + ' s:', 'x = ' + _fn(x) + ' m', 'y = ' + _fn(y) + ' m', 'speed = ' + _fn(spd), 'dir = ' + _fn(dirn) + ' deg']
    _show('Projectile pos/vel', l2)


def resultant():
    f1 = _asknum('force 1 mag=')
    if f1 is None:
        return
    a1 = _asknum('force 1 angle deg=')
    if a1 is None:
        return
    f2 = _asknum('force 2 mag=')
    if f2 is None:
        return
    a2 = _asknum('force 2 angle deg=')
    if a2 is None:
        return
    x = f1 * math.cos(_rad(a1)) + f2 * math.cos(_rad(a2))
    y = f1 * math.sin(_rad(a1)) + f2 * math.sin(_rad(a2))
    mag = math.sqrt(x * x + y * y)
    dirn = _deg(_atan2(y, x))
    _show('Resultant force', [_w('Rx = ' + _fn(x)), _w('Ry = ' + _fn(y)),
                              'Magnitude = ' + _fn(mag),
                              'Direction = ' + _fn(dirn) + ' deg'])


def resolve():
    f = _asknum('force mag=')
    if f is None:
        return
    ad = _asknum('angle deg=')
    if ad is None:
        return
    a = _rad(ad)
    _show('Resolve force', ['Fx = ' + _fn(f * math.cos(a)), 'Fy = ' + _fn(f * math.sin(a)),
                            _w('(horiz comp = F cos)'), _w('(vert comp = F sin)')])


def equilibrium():
    casui.show_text('Equilibrium', 'Enter forces as mag,angle.\nBlank mag ends.\nChecks sum = 0.', casui.BLACK)
    sx = 0.0
    sy = 0.0
    n = 0
    while True:
        m = _askopt('force ' + str(n + 1) + ' mag=')
        if m is None:
            break
        ad = _asknum('angle deg=')
        if ad is None:
            break
        sx += m * math.cos(_rad(ad))
        sy += m * math.sin(_rad(ad))
        n += 1
        if n >= 8:
            break
    if n == 0:
        _show('Equilibrium', ['No forces entered.'])
        return
    res = math.sqrt(sx * sx + sy * sy)
    eq = 'YES (in equilibrium)' if res < 0.001 else 'NO'
    _show('Equilibrium', [_w('Sum Fx = ' + _fn(sx)), _w('Sum Fy = ' + _fn(sy)),
                          'Resultant = ' + _fn(res), 'Equilibrium: ' + eq])


def newton2():
    casui.show_text('Newton II', 'F = m a.\nEnter two, leave one blank.', casui.BLACK)
    f = _askopt('F (N)=')
    m = _askopt('m (kg)=')
    a = _askopt('a (m/s^2)=')
    known = 0
    for q in (f, m, a):
        if q is not None:
            known += 1
    if known < 2:
        _show('Newton II', ['Need 2 of F m a.'])
        return
    if f is None:
        f = m * a
    elif m is None:
        if a == 0:
            _show('Newton II', ['a = 0, m undefined.'])
            return
        m = f / a
    elif a is None:
        if m == 0:
            _show('Newton II', ['m = 0, a undefined.'])
            return
        a = f / m
    _show('Newton II result', ['F = ' + _fn(f) + ' N', 'm = ' + _fn(m) + ' kg', 'a = ' + _fn(a) + ' m/s^2'])


def friction_max():
    mu = _asknum('mu (coeff)=')
    if mu is None:
        return
    r = _asknum('R (normal reac N)=')
    if r is None:
        return
    _show('Max friction', [_w('F_max = mu R'), 'F_max = ' + _fn(mu * r) + ' N'])


def friction_horiz():
    g = _askg()
    m = _asknum('mass m (kg)=')
    if m is None:
        return
    mu = _asknum('mu=')
    if mu is None:
        return
    p = _asknum('applied force P (N)=')
    if p is None:
        return
    if m == 0:
        _show('Horiz plane', ['mass = 0.'])
        return
    rr = m * g
    fmax = mu * rr
    lines = [_w('R = ' + _fn(rr) + ' N'), _w('F_max = ' + _fn(fmax) + ' N')]
    if p <= fmax:
        lines.append('P <= F_max: static.')
        lines.append('Friction = ' + _fn(p) + ' N')
        lines.append('a = 0 m/s^2')
    else:
        a = (p - fmax) / m
        lines.append('P > F_max: moving.')
        lines.append('Net = ' + _fn(p - fmax) + ' N')
        lines.append('a = ' + _fn(a) + ' m/s^2')
    _show('Horiz plane', lines)


def friction_incline():
    g = _askg()
    m = _asknum('mass m (kg)=')
    if m is None:
        return
    th = _asknum('incline angle deg=')
    if th is None:
        return
    mu = _asknum('mu=')
    if mu is None:
        return
    if m == 0:
        _show('Incline', ['mass = 0.'])
        return
    a = _rad(th)
    w = m * g
    drive = w * math.sin(a)
    rr = w * math.cos(a)
    fmax = mu * rr
    lines = [_w('Weight = ' + _fn(w) + ' N'), _w('Along: mg sin = ' + _fn(drive)),
             _w('R = mg cos = ' + _fn(rr)), _w('F_max = ' + _fn(fmax))]
    if drive <= fmax:
        lines.append('Stays at rest.')
        lines.append('a = 0 m/s^2')
    else:
        acc = (drive - fmax) / m
        lines.append('Slides down.')
        lines.append('a = ' + _fn(acc) + ' m/s^2')
    _show('Incline', lines)


def pulley():
    g = _askg()
    casui.show_text('Pulley', 'Two masses, smooth pulley.\nm1 and m2 hang;\nheavier accelerates down.', casui.BLACK)
    m1 = _asknum('mass m1 (kg)=')
    if m1 is None:
        return
    m2 = _asknum('mass m2 (kg)=')
    if m2 is None:
        return
    tot = m1 + m2
    if tot == 0:
        _show('Pulley', ['Total mass = 0.'])
        return
    a = (m1 - m2) * g / tot
    tens = 2.0 * m1 * m2 * g / tot
    lines = [_w('a = (m1-m2)g/(m1+m2)'), 'a = ' + _fn(abs(a)) + ' m/s^2']
    if a > 0:
        lines.append('m1 accelerates down.')
    elif a < 0:
        lines.append('m2 accelerates down.')
    else:
        lines.append('System balanced.')
    lines.append('Tension T = ' + _fn(tens) + ' N')
    _show('Connected particles', lines)


def moments():
    casui.show_text('Moments', 'Moments about a pivot.\nForce up+, dist signed\n(left of pivot dist<0).\nThen unknown reaction.', casui.BLACK)
    smom = 0.0
    sforce = 0.0
    n = 0
    while True:
        f = _askopt('force ' + str(n + 1) + ' (N, up+) =')
        if f is None:
            break
        d = _asknum('dist from pivot (m)=')
        if d is None:
            break
        smom += f * d
        sforce += f
        n += 1
        if n >= 8:
            break
    if n == 0:
        _show('Moments', ['No forces entered.'])
        return
    dr = _askopt('unknown reac dist (blank=net)=')
    lines = ['Sum moments = ' + _fn(smom) + ' Nm', 'Sum forces = ' + _fn(sforce) + ' N']
    if dr is not None and dr != 0:
        rr = -smom / dr
        lines.append('Reaction at d=' + _fn(dr) + ':')
        lines.append('R = ' + _fn(rr) + ' N')
        lines.append(_w('(balances moments)'))
    else:
        if abs(smom) < 0.001:
            lines.append('Moments balance.')
        else:
            lines.append('Net moment not zero.')
    _show('Moments result', lines)


TOOLS = [
    ('SUVAT solver', suvat),
    ('Projectiles', projectile),
    ('Resultant of forces', resultant),
    ('Resolve a force', resolve),
    ('Equilibrium check', equilibrium),
    ('Newton II F=ma', newton2),
    ('Friction F=mu R', friction_max),
    ('Friction horiz plane', friction_horiz),
    ('Friction incline', friction_incline),
    ('Pulley (connected)', pulley),
    ('Moments / reactions', moments),
]


def _tvalue(tree, tv):
    try:
        val = caseng.evalf(tree, 0.0, False, {'t': tv})
    except:
        return None
    if isinstance(val, complex) or val != val:
        return None
    return val

def _tparse(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    tree = caslex.parse(s)
    if tree is None:
        _show('Variable acceleration', ['Could not read that expression.'])
        return None
    if caseng.count_var(tree, 'x'):
        _show('Variable acceleration', ['Type the time variable as t,',
                                        'not x. Use ALPHA then the',
                                        'divide key for t.'])
        return None
    return tree

def kinematics():
    _show('Variable acceleration', ['SUVAT only works when a is',
                                    'constant. Here a, v or s is a',
                                    'function of t and calculus does',
                                    'the work:',
                                    '  v = ds/dt   a = dv/dt',
                                    '  v = int a dt   s = int v dt'])
    which = casui.menu('You are given', ['s(t) displacement', 'v(t) velocity',
                                         'a(t) acceleration'])
    if which == -1:
        return
    tree = _tparse(('s(t) =', 'v(t) =', 'a(t) =')[which])
    if tree is None:
        return
    s = None
    v = None
    a = None
    lines = []
    if which == 0:
        s = tree
        try:
            v = cascalc.tidy(caseng.diff(s, 't'))
            a = cascalc.tidy(caseng.diff(v, 't'))
        except:
            _show('Variable acceleration', ['Cannot differentiate that.'])
            return
    elif which == 1:
        v = tree
        try:
            a = cascalc.tidy(caseng.diff(v, 't'))
        except:
            a = None
        S = cascalc.integ(v, 't')
        if S is not None:
            s0 = _asknum('s when t=0 [0]')
            if s0 is None:
                s0 = 0.0
            base = _tvalue(S, 0.0)
            c = 0.0 if base is None else s0 - base
            s = cascalc.tidy(('+', S, ('n', c)))
            lines.append(_w('s(0) = ' + _fn(s0) + ' fixes the constant'))
    else:
        a = tree
        V = cascalc.integ(a, 't')
        if V is None:
            _show('Variable acceleration', ['a(t) has no elementary integral,',
                                            'so v cannot be written down.'])
            return
        v0 = _asknum('v when t=0 [0]')
        if v0 is None:
            v0 = 0.0
        base = _tvalue(V, 0.0)
        c = 0.0 if base is None else v0 - base
        v = cascalc.tidy(('+', V, ('n', c)))
        S = cascalc.integ(v, 't')
        if S is not None:
            s0 = _asknum('s when t=0 [0]')
            if s0 is None:
                s0 = 0.0
            base = _tvalue(S, 0.0)
            c2 = 0.0 if base is None else s0 - base
            s = cascalc.tidy(('+', S, ('n', c2)))
        lines.append(_w('v(0) = ' + _fn(v0) + ' fixes the constant'))
    out = []
    if s is not None:
        out.append('s(t) = ' + caseng.tostr(s))
    else:
        out.append(_warn('s(t): no elementary integral'))
    if v is not None:
        out.append('v(t) = ' + caseng.tostr(v))
    if a is not None:
        out.append('a(t) = ' + caseng.tostr(a))
    out.append('')
    for ln in lines:
        out.append(ln)
    if v is not None:
        zeros = cascalc.solve(v, 't')
        pos = []
        for r in zeros:
            if r >= 0:
                pos.append(r)
        out.append('')
        if pos:
            out.append('at rest (v = 0) when:')
            for r in pos:
                extra = ''
                if s is not None:
                    sv = _tvalue(s, r)
                    if sv is not None:
                        extra = '   s = ' + _fn(sv)
                out.append('  t = ' + _fn(r) + extra)
            out.append(_warn('(these are the turning points of s,'))
            out.append(_warn(' so distance travelled and'))
            out.append(_warn(' displacement differ after them)'))
        else:
            out.append(_warn('v is never 0 for t >= 0 in the'))
            out.append(_warn('search range, so the motion does'))
            out.append(_warn('not reverse.'))
    tv = _asknum('values at t = (or cancel)')
    if tv is not None:
        out.append('')
        out.append('at t = ' + _fn(tv) + ':')
        for nm, tr in (('s', s), ('v', v), ('a', a)):
            if tr is None:
                continue
            val = _tvalue(tr, tv)
            out.append('  ' + nm + ' = ' + ('undefined' if val is None else _fn(val)))
    _show('Variable acceleration', out)

def distance_travelled():
    _show('Distance vs displacement', ['Displacement is int v dt.',
                                       'Distance travelled is int |v| dt,',
                                       'and they differ as soon as v',
                                       'changes sign. Enter v(t) and the',
                                       'time interval.'])
    v = _tparse('v(t) =')
    if v is None:
        return
    t0 = _asknum('from t =')
    if t0 is None:
        return
    t1 = _asknum('to t =')
    if t1 is None:
        return
    if t1 < t0:
        t0, t1 = t1, t0
    turns = []
    for r in cascalc.solve(v, 't'):
        if t0 + 1e-9 < r < t1 - 1e-9:
            turns.append(r)
    turns.sort()
    bounds = [t0] + turns + [t1]
    disp = 0.0
    dist = 0.0
    parts = []
    i = 0
    ok = True
    while i < len(bounds) - 1:
        seg = cascalc.defint(v, bounds[i], bounds[i + 1], False, 200, 't')
        if seg is None:
            ok = False
            break
        disp += seg
        dist += seg if seg >= 0 else -seg
        parts.append((bounds[i], bounds[i + 1], seg))
        i += 1
    if not ok:
        _show('Distance', ['Could not integrate v over that', 'interval.'])
        return
    lines = [_w('v(t) = ' + caseng.tostr(caseng.simplify(v))),
             _w('from t = ' + _fn(t0) + ' to t = ' + _fn(t1)), '']
    if turns:
        lines.append(_w('v = 0 inside the interval at:'))
        for r in turns:
            lines.append(_w('  t = ' + _fn(r)))
        lines.append(_w('so the motion reverses - split the'))
        lines.append(_w('integral there:'))
        for a0, b0, seg in parts:
            lines.append(_w('  ' + _fn(a0) + ' to ' + _fn(b0) + ':  ' + _fn(seg)))
        lines.append('')
    lines.append('displacement = ' + _fn(disp))
    lines.append('distance     = ' + _fn(dist))
    if abs(dist - abs(disp)) > 1e-6:
        lines.append('')
        lines.append(_warn('They differ because v changes sign.'))
    else:
        lines.append('')
        lines.append(_warn('Same, because v keeps one sign.'))
    _show('Distance', lines)

def connected():
    _show('Connected particles', ['Two masses joined over a smooth',
                                  'pulley. Each one either hangs',
                                  'vertically or sits on a plane at',
                                  'an angle, possibly rough.',
                                  'Angle 90 means hanging.'])
    g = _askg()
    m1 = _asknum('mass 1 (kg)')
    if m1 is None or m1 <= 0:
        return
    a1 = _asknum('mass 1 plane angle deg [90]')
    if a1 is None:
        a1 = 90.0
    mu1 = _asknum('mass 1 friction mu [0]')
    if mu1 is None:
        mu1 = 0.0
    m2 = _asknum('mass 2 (kg)')
    if m2 is None or m2 <= 0:
        return
    a2 = _asknum('mass 2 plane angle deg [90]')
    if a2 is None:
        a2 = 90.0
    mu2 = _asknum('mass 2 friction mu [0]')
    if mu2 is None:
        mu2 = 0.0
    s1 = math.sin(_rad(a1))
    c1 = math.cos(_rad(a1))
    s2 = math.sin(_rad(a2))
    c2 = math.cos(_rad(a2))
    drive = m1 * g * s1 - m2 * g * s2
    fric = mu1 * m1 * g * c1 + mu2 * m2 * g * c2
    lines = [_w('g = ' + _fn(g)),
             _w('mass 1: ' + _fn(m1) + ' kg at ' + _fn(a1) + ' deg, mu = ' + _fn(mu1)),
             _w('mass 2: ' + _fn(m2) + ' kg at ' + _fn(a2) + ' deg, mu = ' + _fn(mu2)),
             '',
             _w('driving force along the string:'),
             _w('  m1 g sin' + _fn(a1) + ' - m2 g sin' + _fn(a2) + ' = ' + _fn(drive)),
             _w('maximum total friction:'),
             _w('  mu1 m1 g cos' + _fn(a1) + ' + mu2 m2 g cos' + _fn(a2) + ' = ' + _fn(fric))]
    if abs(drive) <= fric + 1e-9:
        lines.append('')
        lines.append('|driving| <= friction, so the')
        lines.append('system stays at rest. Friction')
        lines.append('takes the value that balances it,')
        lines.append('which is ' + _fn(abs(drive)) + ' N, not its maximum.')
        lines.append(_warn('Tension is then indeterminate from'))
        lines.append(_warn('these equations alone.'))
        _show('Connected particles', lines)
        return
    sgn = 1.0 if drive > 0 else -1.0
    a = (abs(drive) - fric) / (m1 + m2)
    f2 = mu2 * m2 * g * c2
    T = m2 * a + m2 * g * s2 + f2 if sgn > 0 else m1 * a + m1 * g * s1 + mu1 * m1 * g * c1
    lines.append('')
    lines.append(_w('acceleration a = (|drive| - friction)'))
    lines.append(_w('                 / (m1 + m2)'))
    lines.append('a = ' + _fn(a) + ' m/s^2')
    lines.append('mass ' + ('1' if sgn > 0 else '2') + ' accelerates down its plane.')
    lines.append('tension T = ' + _fn(T) + ' N')
    lines.append('')
    lines.append('')
    lines.append(_w('(T is the same throughout a light'))
    lines.append(_w(' inextensible string over a smooth'))
    lines.append(_w(' pulley - that is what makes one'))
    lines.append(_w(' equation per mass enough)'))
    _show('Connected particles', lines)

def projectile_inverse():
    _show('Find the launch', ['Given something about the flight,',
                              'work back to the launch speed u',
                              'and angle. Pick what you know.'])
    which = casui.menu('You know', ['range and angle', 'max height and angle',
                                    'position (x, y) at time t',
                                    'speed u and a target (x, y)',
                                    'range and time of flight'])
    if which == -1:
        return
    g = _askg()
    if g <= 0:
        _show('Find the launch', ['g must be positive.'])
        return
    lines = [_w('g = ' + _fn(g))]
    if which == 0:
        R = _asknum('range R (m)')
        if R is None:
            return
        ad = _asknum('angle (deg)')
        if ad is None:
            return
        s2 = math.sin(2.0 * _rad(ad))
        if abs(s2) < 1e-12 or R / s2 <= 0:
            _show('Find the launch', ['R = u^2 sin2a / g cannot be solved',
                                      'for these values.'])
            return
        u = math.sqrt(R * g / s2)
        lines.append(_w('R = u^2 sin(2a) / g'))
        lines.append(_w('u = sqrt(Rg / sin 2a)'))
        lines.append('u = ' + _fn(u) + ' m/s at ' + _fn(ad) + ' deg')
        lines.append('')
        other = 90.0 - ad
        if abs(other - ad) > 1e-9:
            lines.append(_warn('NOTE: ' + _fn(other) + ' deg gives the same range'))
            lines.append(_warn('with the same speed - sin2a is equal'))
            lines.append(_warn('for a and 90 - a. The higher angle is'))
            lines.append(_warn('the slower, higher trajectory.'))
    elif which == 1:
        H = _asknum('max height H (m)')
        if H is None or H < 0:
            return
        ad = _asknum('angle (deg)')
        if ad is None:
            return
        sa = math.sin(_rad(ad))
        if abs(sa) < 1e-12:
            _show('Find the launch', ['At 0 degrees the projectile never',
                                      'rises, so H = 0 for every u.'])
            return
        u = math.sqrt(2.0 * g * H) / sa
        lines.append(_w('H = (u sin a)^2 / (2g)'))
        lines.append(_w('u = sqrt(2gH) / sin a'))
        lines.append('u = ' + _fn(u) + ' m/s at ' + _fn(ad) + ' deg')
    elif which == 2:
        x = _asknum('horizontal distance x (m)')
        if x is None:
            return
        y = _asknum('height y (m, above launch)')
        if y is None:
            return
        t = _asknum('time t (s)')
        if t is None or t <= 0:
            _show('Find the launch', ['t must be positive.'])
            return
        ux = x / t
        uy = (y + 0.5 * g * t * t) / t
        u = math.sqrt(ux * ux + uy * uy)
        ang = _deg(_atan2(uy, ux))
        lines.append(_w('x = ux t          so ux = x/t = ' + _fn(ux)))
        lines.append(_w('y = uy t - gt^2/2 so uy = (y + gt^2/2)/t'))
        lines.append(_w('                        = ' + _fn(uy)))
        lines.append('')
        lines.append('u = sqrt(ux^2 + uy^2) = ' + _fn(u) + ' m/s')
        lines.append('angle = ' + _fn(ang) + ' deg above the horizontal')
    elif which == 3:
        u = _asknum('launch speed u (m/s)')
        if u is None or u <= 0:
            return
        x = _asknum('target x (m)')
        if x is None or x == 0:
            _show('Find the launch', ['x must be non-zero.'])
            return
        y = _asknum('target y (m, above launch)')
        if y is None:
            return
        A = g * x * x / (2.0 * u * u)
        B = -x
        C = y + A
        disc = B * B - 4.0 * A * C
        lines.append(_w('y = x tan a - gx^2(1 + tan^2 a)/(2u^2)'))
        lines.append(_w('is a quadratic in tan a:'))
        lines.append(_w('  ' + _fn(A) + ' T^2 + ' + _fn(B) + ' T + ' + _fn(C) + ' = 0'))
        lines.append(_w('discriminant = ' + _fn(disc)))
        if disc < -1e-12:
            lines.append('')
            lines.append('Negative: at ' + _fn(u) + ' m/s the target is')
            lines.append('OUT OF RANGE at any angle.')
        else:
            if disc < 0:
                disc = 0.0
            rt = math.sqrt(disc)
            t1 = (-B + rt) / (2.0 * A)
            t2 = (-B - rt) / (2.0 * A)
            a1 = _deg(math.atan(t1))
            a2 = _deg(math.atan(t2))
            lines.append('')
            if rt < 1e-9:
                lines.append('One solution: the target is exactly')
                lines.append('at the limit of the range.')
                lines.append('  angle = ' + _fn(a1) + ' deg')
            else:
                lines.append('TWO angles reach the target:')
                lines.append('  high ball ' + _fn(a1) + ' deg')
                lines.append('  low ball  ' + _fn(a2) + ' deg')
                lines.append(_w('(the low one gets there sooner)'))
    else:
        R = _asknum('range R (m)')
        if R is None:
            return
        T = _asknum('time of flight T (s)')
        if T is None or T <= 0:
            _show('Find the launch', ['T must be positive.'])
            return
        ux = R / T
        uy = g * T / 2.0
        u = math.sqrt(ux * ux + uy * uy)
        ang = _deg(_atan2(uy, ux))
        lines.append(_w('back at launch height, so T = 2 uy/g'))
        lines.append(_w('uy = gT/2 = ' + _fn(uy)))
        lines.append(_w('ux = R/T  = ' + _fn(ux)))
        lines.append('')
        lines.append('u = ' + _fn(u) + ' m/s at ' + _fn(ang) + ' deg')
    _show('Find the launch', lines)


TOOLS.append(('Projectile: find the launch', projectile_inverse))
TOOLS.append(('Variable acceleration', kinematics))
TOOLS.append(('Distance vs displacement', distance_travelled))
TOOLS.append(('Connected particles', connected))

def run():
    casutil.run_tools('MECHANICS', TOOLS)