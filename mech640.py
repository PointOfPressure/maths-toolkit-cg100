import math
import casui
import caslex
import caseng


def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None


def _askopt(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    s = s.strip()
    if s == '':
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None


def _askg():
    v = casui.input_expr('g [9.8]')
    if v is None:
        return 9.8
    v = v.strip()
    if v == '':
        return 9.8
    t = caslex.parse(v)
    if t is None:
        return 9.8
    try:
        return caseng.evalf(t, 0.0)
    except:
        return 9.8


def _fn(x):
    try:
        r = round(x, 4)
    except:
        return str(x)
    try:
        if r == int(r):
            return str(int(r))
    except:
        return str(r)
    return str(r)


def _atan2(y, x):
    if x > 0:
        return math.atan(y / x)
    if x < 0:
        if y >= 0:
            return math.atan(y / x) + math.pi
        return math.atan(y / x) - math.pi
    if y > 0:
        return math.pi / 2.0
    if y < 0:
        return -math.pi / 2.0
    return 0.0


def _deg(r):
    return r * 180.0 / math.pi


def _rad(d):
    return d * math.pi / 180.0


def _show(title, lines):
    casui.result_screen(title, lines)


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
                prog = True
        if u is None and v is not None and a is not None and s is not None:
            d = v * v - 2.0 * a * s
            if d >= 0:
                u = math.sqrt(d)
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
    l1 = ['Time of flight = ' + _fn(tof) + ' s', 'Max height = ' + _fn(hmax) + ' m', 'Range = ' + _fn(rng) + ' m', 'ux = ' + _fn(u * math.cos(a)), 'uy = ' + _fn(u * math.sin(a))]
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
    _show('Resultant force', ['Rx = ' + _fn(x), 'Ry = ' + _fn(y), 'Magnitude = ' + _fn(mag), 'Direction = ' + _fn(dirn) + ' deg'])


def resolve():
    f = _asknum('force mag=')
    if f is None:
        return
    ad = _asknum('angle deg=')
    if ad is None:
        return
    a = _rad(ad)
    _show('Resolve force', ['Fx = ' + _fn(f * math.cos(a)), 'Fy = ' + _fn(f * math.sin(a)), '(horiz comp = F cos)', '(vert comp = F sin)'])


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
    _show('Equilibrium', ['Sum Fx = ' + _fn(sx), 'Sum Fy = ' + _fn(sy), 'Resultant = ' + _fn(res), 'Equilibrium: ' + eq])


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
    _show('Max friction', ['F_max = mu R', 'F_max = ' + _fn(mu * r) + ' N'])


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
    lines = ['R = ' + _fn(rr) + ' N', 'F_max = ' + _fn(fmax) + ' N']
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
    lines = ['Weight = ' + _fn(w) + ' N', 'Along: mg sin = ' + _fn(drive), 'R = mg cos = ' + _fn(rr), 'F_max = ' + _fn(fmax)]
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
    lines = ['a = (m1-m2)g/(m1+m2)', 'a = ' + _fn(abs(a)) + ' m/s^2']
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
        lines.append('(balances moments)')
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


def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('MECHANICS', labels)
        if c == -1:
            return
        TOOLS[c][1]()