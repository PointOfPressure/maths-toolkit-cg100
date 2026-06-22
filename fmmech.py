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

def _askg():
    v = _asknum('g =? (def 9.8)')
    if v is None:
        return 9.8
    return v

def _fn(x):
    try:
        r = round(x, 4)
    except:
        return str(x)
    if r == int(r):
        return str(int(r))
    return str(r)

def _show(title, lines):
    casui.result_screen(title, lines)

def _getlist(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    out = []
    for p in s.replace(',', ' ').split():
        try:
            out.append(float(p))
        except:
            return None
    return out

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
        _show('Impulse', ['J = m(v-u)', 'J = ' + _fn(j) + ' N s',
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
        _show('Conservation', ['m2 = 0, cannot find v2'])
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
        _show('Restitution', ['total mass 0'])
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
        _show('Kinetic energy', ['KE = 0.5 m v^2',
            'KE = ' + _fn(0.5 * m * v * v) + ' J'])
    elif k == 2:
        m = _asknum('mass m')
        h = _asknum('height h')
        if None in (m, h):
            return
        g = _askg()
        _show('GPE', ['GPE = m g h', 'g = ' + _fn(g),
            'GPE = ' + _fn(m * g * h) + ' J'])
    elif k == 3:
        f = _asknum('force F')
        d = _asknum('distance d')
        if None in (f, d):
            return
        _show('Work done', ['W = F d', 'W = ' + _fn(f * d) + ' J'])
    elif k == 4:
        f = _asknum('force F')
        v = _asknum('speed v')
        if None in (f, v):
            return
        _show('Power', ['P = F v', 'P = ' + _fn(f * v) + ' W'])
    elif k == 5:
        w = _asknum('work W')
        t = _asknum('time t')
        if None in (w, t) or t == 0:
            return
        _show('Power', ['P = W / t', 'P = ' + _fn(w / t) + ' W'])

# ---------- circular motion ----------
def t_circular():
    _show('Circular motion', ['1 a,F from v & r', '2 a,F from omega & r',
        '3 conical pendulum', '4 vertical circle top'])
    k = _asknum('Choose 1-4')
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
        _show('Conical pendulum', ['tan th = v^2/(r g)',
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
            'v = sqrt(g r)', 'v = ' + _fn(vmin) + ' m/s'])

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
        'EPE = lam x^2/(2l)', 'EPE = ' + _fn(epe) + ' J'])

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
        _show('Centre of mass', ['total mass 0'])
        return
    if int(k) == 1:
        xs = _getlist('x coords (space sep)')
        if xs is None or len(xs) != len(masses):
            _show('Centre of mass', ['count mismatch'])
            return
        sx = 0.0
        for i in range(len(masses)):
            sx += masses[i] * xs[i]
        _show('COM (1-D)', ['total m = ' + _fn(sm),
            'x_bar = ' + _fn(sx / sm)])
    else:
        xs = _getlist('x coords (space sep)')
        ys = _getlist('y coords (space sep)')
        if xs is None or ys is None or len(xs) != len(masses) or len(ys) != len(masses):
            _show('Centre of mass', ['count mismatch'])
            return
        sx = 0.0
        sy = 0.0
        for i in range(len(masses)):
            sx += masses[i] * xs[i]
            sy += masses[i] * ys[i]
        _show('COM (2-D)', ['total m = ' + _fn(sm),
            'x_bar = ' + _fn(sx / sm), 'y_bar = ' + _fn(sy / sm)])

# ---------- dimensional analysis ----------
def t_dim():
    _show('Dimensions', ['Enter M L T powers for', 'LHS and RHS, check',
        'they are consistent', 'e.g. force = 1 1 -2'])
    a = _getlist('LHS: M L T powers')
    b = _getlist('RHS: M L T powers')
    if a is None or b is None or len(a) != 3 or len(b) != 3:
        _show('Dimensions', ['need 3 numbers each', 'e.g.  1 1 -2'])
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
    _show('Dimensions', ['LHS ' + lhs, 'RHS ' + rhs, res])

TOOLS = [
    ('Momentum & impulse', t_momentum),
    ('Restitution', t_restitution),
    ('Work/Energy/Power', t_work),
    ('Circular motion', t_circular),
    ('Hookes law / EPE', t_hooke),
    ('Centre of mass', t_com),
    ('Dimensional analysis', t_dim),
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Mechanics (FM)', labels)
        if c == -1:
            return
        TOOLS[c][1]()
