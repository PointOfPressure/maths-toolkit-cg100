import math
import casutil

_asknum = casutil.asknum
_fn = casutil.fmt
_show = casutil.show
_myacos = casutil.acos_safe
_deg = casutil.deg

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
    _show('SKEW LINE DIST', ['|d1 x d2| = ' + _fn(mc), 'shortest dist = ' + _fn(dist)])

def t_ptline():
    # distance from a point to the line r = a + t d, i.e. |(p - a) x d| / |d|
    a = _vec('line point a')
    if a is None:
        return
    d = _vec('line direction d')
    if d is None:
        return
    p = _vec('point p')
    if p is None:
        return
    md = _mag(d)
    if md == 0:
        _show('PT TO LINE', ['Direction is zero:', 'not a line.'])
        return
    w = [p[0] - a[0], p[1] - a[1], p[2] - a[2]]
    cr = _cross(w, d)
    dist = _mag(cr) / md
    t = _dot(w, d) / (md * md)
    foot = [a[0] + t * d[0], a[1] + t * d[1], a[2] + t * d[2]]
    _show('PT TO LINE', ['|(p-a) x d| = ' + _fn(_mag(cr)), '|d| = ' + _fn(md),
                         'dist = ' + _fn(dist), 'nearest point on line:', _vstr(foot)])

def t_lineeq():
    # Build the equation of a line. Every other vector tool here consumes a
    # line; none of them could produce one, which is the first thing a vectors
    # question actually asks for.
    how = casutil.askint('1 = through two points, 2 = point + direction', 1, 2)
    if how is None:
        return
    a = _vec('point A')
    if a is None:
        return
    if how == 1:
        b = _vec('point B')
        if b is None:
            return
        d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
    else:
        d = _vec('direction d')
        if d is None:
            return
    if _mag(d) < 1e-12:
        _show('Line', ['The direction is the zero vector,',
                       'so this does not define a line.'])
        return
    lines = ['through ' + _vstr(a),
             'direction ' + _vstr(d), '',
             'VECTOR FORM',
             '  r = ' + _vstr(a) + ' + t' + _vstr(d), '',
             'PARAMETRIC',
             '  x = ' + _fn(a[0]) + ' + ' + _fn(d[0]) + 't',
             '  y = ' + _fn(a[1]) + ' + ' + _fn(d[1]) + 't',
             '  z = ' + _fn(a[2]) + ' + ' + _fn(d[2]) + 't', '',
             'CARTESIAN']
    parts = []
    fixed = []
    names = ('x', 'y', 'z')
    i = 0
    while i < 3:
        if abs(d[i]) > 1e-12:
            parts.append('(' + names[i] + ' - ' + _fn(a[i]) + ')/' + _fn(d[i]))
        else:
            fixed.append(names[i] + ' = ' + _fn(a[i]))
        i += 1
    if parts:
        lines.append('  ' + ' = '.join(parts))
    for f in fixed:
        lines.append('  with ' + f)
    if not parts:
        lines.append('  (the direction is zero in every')
        lines.append('   component - not a line)')
    lines.append('')
    lines.append('|d| = ' + _fn(_mag(d)))
    u = _mag(d)
    lines.append('unit direction ' + _vstr([d[0] / u, d[1] / u, d[2] / u]))
    t = _asknum('point at t = (or cancel)')
    if t is not None:
        lines.append('')
        lines.append('at t = ' + _fn(t) + ': ' +
                     _vstr([a[0] + t * d[0], a[1] + t * d[1], a[2] + t * d[2]]))
    _show('Equation of a line', lines)


def t_lineplane():
    # Where a line meets a plane. Substituting the parametric line into the
    # plane equation gives one equation in t; the two degenerate cases (line
    # parallel to the plane, and line lying in it) have to be told apart, and
    # they are the ones worth marks.
    _show('Line meets plane', ['Line r = a + t d.',
                               'Plane n . r = k, so enter the',
                               'normal n and the constant k.'])
    a = _vec('line point a')
    if a is None:
        return
    d = _vec('line direction d')
    if d is None:
        return
    n = _vec('plane normal n')
    if n is None:
        return
    k = _asknum('plane constant k (n.r = k)')
    if k is None:
        return
    nd = _dot(n, d)
    na = _dot(n, a)
    lines = ['line r = ' + _vstr(a) + ' + t' + _vstr(d),
             'plane ' + _vstr(n) + ' . r = ' + _fn(k), '',
             'n . d = ' + _fn(nd), 'n . a = ' + _fn(na), '']
    if abs(nd) < 1e-12:
        if abs(na - k) < 1e-9:
            lines.append('n . d = 0 and a is in the plane,')
            lines.append('so the whole LINE LIES IN the plane -')
            lines.append('every point of it is an intersection.')
        else:
            lines.append('n . d = 0 but a is not in the plane,')
            lines.append('so the line is PARALLEL to the plane')
            lines.append('and never meets it.')
            dist = abs(na - k) / _mag(n)
            lines.append('distance from the line to the plane')
            lines.append('  = |n.a - k| / |n| = ' + _fn(dist))
        _show('Line meets plane', lines)
        return
    t = (k - na) / nd
    p = [a[0] + t * d[0], a[1] + t * d[1], a[2] + t * d[2]]
    lines.append('n.(a + t d) = k gives')
    lines.append('  ' + _fn(na) + ' + ' + _fn(nd) + 't = ' + _fn(k))
    lines.append('  t = ' + _fn(t))
    lines.append('')
    lines.append('they meet at ' + _vstr(p))
    chk = _dot(n, p)
    lines.append('check n.p = ' + _fn(chk) + ' (should be ' + _fn(k) + ')')
    # the angle between the line and the plane is 90 - angle(d, n)
    ang = _deg(_myacos(abs(nd) / (_mag(n) * _mag(d))))
    lines.append('')
    lines.append('angle between d and n = ' + _fn(ang) + ' deg')
    lines.append('angle between the LINE and the PLANE')
    lines.append('  = 90 - that = ' + _fn(90.0 - ang) + ' deg')
    _show('Line meets plane', lines)


TOOLS = [
    ('Magnitude |a|', t_mag),
    ('Dot product a.b', t_dot),
    ('Angle between', t_angle),
    ('Cross product a x b', t_cross),
    ('Unit vector', t_unit),
    ('Scalar projection', t_proj),
    ('Parallel / perp test', t_paraperp),
    ('Point to line dist', t_ptline),
    ('Equation of a line', t_lineeq),
    ('Line meets plane', t_lineplane),
    ('Point to plane dist', t_ptplane),
    ('Angle between planes', t_planeangle),
    ('Skew lines distance', t_skew),
]

def run():
    casutil.run_tools('VECTORS & 3-D', TOOLS)
