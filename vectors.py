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

def _myacos(c):
    if c > 1.0:
        c = 1.0
    if c < -1.0:
        c = -1.0
    return math.acos(c)

def _deg(r):
    return r * 180.0 / math.pi

def _vec(name):
    x = _asknum(name + ' x:')
    if x is None:
        return None
    y = _asknum(name + ' y:')
    if y is None:
        return None
    z = _asknum(name + ' z (0 if 2D):')
    if z is None:
        return None
    return [x, y, z]

def _mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

def _vstr(v):
    return '(' + _fn(v[0]) + ', ' + _fn(v[1]) + ', ' + _fn(v[2]) + ')'

def t_mag():
    a = _vec('a')
    if a is None:
        return
    _show('MAGNITUDE', ['a = ' + _vstr(a), '|a| = ' + _fn(_mag(a))])

def t_dot():
    a = _vec('a')
    if a is None:
        return
    b = _vec('b')
    if b is None:
        return
    _show('DOT PRODUCT', ['a = ' + _vstr(a), 'b = ' + _vstr(b), 'a.b = ' + _fn(_dot(a, b))])

def t_angle():
    a = _vec('a')
    if a is None:
        return
    b = _vec('b')
    if b is None:
        return
    ma = _mag(a)
    mb = _mag(b)
    if ma == 0 or mb == 0:
        _show('ANGLE', ['Zero vector: undefined'])
        return
    c = _dot(a, b) / (ma * mb)
    r = _myacos(c)
    _show('ANGLE BETWEEN', ['cos = ' + _fn(c), 'angle = ' + _fn(_deg(r)) + ' deg', '      = ' + _fn(r) + ' rad'])

def t_cross():
    a = _vec('a')
    if a is None:
        return
    b = _vec('b')
    if b is None:
        return
    cr = _cross(a, b)
    _show('CROSS PRODUCT', ['a x b =', _vstr(cr), '|a x b| = ' + _fn(_mag(cr))])

def t_unit():
    a = _vec('a')
    if a is None:
        return
    m = _mag(a)
    if m == 0:
        _show('UNIT VECTOR', ['Zero vector: undefined'])
        return
    u = [a[0] / m, a[1] / m, a[2] / m]
    _show('UNIT VECTOR', ['|a| = ' + _fn(m), 'a-hat =', _vstr(u)])

def t_proj():
    a = _vec('a')
    if a is None:
        return
    b = _vec('b')
    if b is None:
        return
    mb = _mag(b)
    if mb == 0:
        _show('PROJECTION', ['b is zero: undefined'])
        return
    sp = _dot(a, b) / mb
    _show('SCALAR PROJ a on b', ['a.b = ' + _fn(_dot(a, b)), '|b| = ' + _fn(mb), 'proj = ' + _fn(sp)])

def t_paraperp():
    a = _vec('a')
    if a is None:
        return
    b = _vec('b')
    if b is None:
        return
    if _mag(a) < 1e-9 or _mag(b) < 1e-9:
        _show('PARA / PERP TEST', ['Zero vector: undefined'])
        return
    d = _dot(a, b)
    cr = _cross(a, b)
    mc = _mag(cr)
    res = []
    if mc < 1e-9:
        res.append('PARALLEL (a x b ~ 0)')
    else:
        res.append('Not parallel')
    if abs(d) < 1e-9:
        res.append('PERPENDICULAR (a.b ~ 0)')
    else:
        res.append('Not perpendicular')
    res.append('a.b = ' + _fn(d))
    res.append('|axb| = ' + _fn(mc))
    _show('PARA / PERP TEST', res)

def t_ptplane():
    n = _vec('normal n')
    if n is None:
        return
    d = _asknum('plane const d (n.r=d):')
    if d is None:
        return
    p = _vec('point p')
    if p is None:
        return
    mn = _mag(n)
    if mn == 0:
        _show('DISTANCE', ['Normal is zero: undefined'])
        return
    dist = abs(_dot(n, p) - d) / mn
    _show('PT TO PLANE', ['n.p = ' + _fn(_dot(n, p)), 'd = ' + _fn(d), 'dist = ' + _fn(dist)])

def t_planeangle():
    n1 = _vec('plane1 normal')
    if n1 is None:
        return
    n2 = _vec('plane2 normal')
    if n2 is None:
        return
    m1 = _mag(n1)
    m2 = _mag(n2)
    if m1 == 0 or m2 == 0:
        _show('PLANE ANGLE', ['Zero normal: undefined'])
        return
    c = abs(_dot(n1, n2)) / (m1 * m2)
    r = _myacos(c)
    _show('ANGLE OF PLANES', ['cos = ' + _fn(c), 'angle = ' + _fn(_deg(r)) + ' deg', '      = ' + _fn(r) + ' rad'])

def t_skew():
    a1 = _vec('line1 point a1')
    if a1 is None:
        return
    d1 = _vec('line1 dir d1')
    if d1 is None:
        return
    a2 = _vec('line2 point a2')
    if a2 is None:
        return
    d2 = _vec('line2 dir d2')
    if d2 is None:
        return
    cr = _cross(d1, d2)
    mc = _mag(cr)
    diff = [a1[0] - a2[0], a1[1] - a2[1], a1[2] - a2[2]]
    if mc < 1e-9:
        _show('SKEW LINES', ['d1 x d2 ~ 0:', 'lines parallel,', 'not skew'])
        return
    dist = abs(_dot(diff, cr)) / mc
    _show('SKEW LINE DIST', ['|d1 x d2| = ' + _fn(mc), 'shortest dist =', _fn(dist)])

TOOLS = [
    ('Magnitude |a|', t_mag),
    ('Dot product a.b', t_dot),
    ('Angle between', t_angle),
    ('Cross product a x b', t_cross),
    ('Unit vector', t_unit),
    ('Scalar projection', t_proj),
    ('Parallel / perp test', t_paraperp),
    ('Point to plane dist', t_ptplane),
    ('Angle between planes', t_planeangle),
    ('Skew lines distance', t_skew),
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('VECTORS & 3-D', labels)
        if c == -1:
            return
        TOOLS[c][1]()
