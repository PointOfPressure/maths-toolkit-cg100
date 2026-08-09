import math
import casui
import casutil

A = [[0.0]]
B = [[0.0]]

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_show = casutil.show
_w = casutil.w
_warn = casutil.warn


def _rowstr(row):
    parts = []
    for v in row:
        parts.append(_fn(v))
    return '[ ' + '  '.join(parts) + ' ]'


def _matlines(name, m):
    out = []
    if m is None:
        return [_warn(name + ' not set')]
    out.append(name + ' =')
    for row in m:
        out.append('  ' + _rowstr(row))
    return out


def _enter(name):
    n = _askint('rows of ' + name + ' (1-3):', 1, 3)
    if n is None:
        return None
    c = _askint('cols of ' + name + ' (1-3):', 1, 3)
    if c is None:
        return None
    m = []
    for i in range(n):
        row = []
        for j in range(c):
            v = _asknum(name + '[' + str(i + 1) + ',' + str(j + 1) + ']:')
            if v is None:
                return None
            row.append(v)
        m.append(row)
    return m


def _dims(m):
    return (len(m), len(m[0]))


def _samedim(p, q):
    return len(p) == len(q) and len(p[0]) == len(q[0])


def _addsub(sign):
    if not _samedim(A, B):
        _show('ERROR', [_warn('A and B must be'), _warn('the same size')])
        return
    r = []
    for i in range(len(A)):
        row = []
        for j in range(len(A[0])):
            row.append(A[i][j] + sign * B[i][j])
        r.append(row)
    nm = 'A+B' if sign > 0 else 'A-B'
    _show(nm, _matlines(nm, r))


def _det(m):
    n = len(m)
    if n != len(m[0]):
        return None
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    a = m[0][0]
    b = m[0][1]
    c = m[0][2]
    d = m[1][0]
    e = m[1][1]
    f = m[1][2]
    g = m[2][0]
    h = m[2][1]
    i = m[2][2]
    return a * e * i + b * f * g + c * d * h - c * e * g - a * f * h - b * d * i


def t_enterA():
    global A
    m = _enter('A')
    if m is None:
        return
    A = m
    _show('A stored', _matlines('A', A))


def t_enterB():
    global B
    m = _enter('B')
    if m is None:
        return
    B = m
    _show('B stored', _matlines('B', B))


def t_showAB():
    _show('A', _matlines('A', A) + _matlines('B', B))


def t_add():
    _addsub(1)


def t_sub():
    _addsub(-1)


def t_scalar():
    k = _asknum('scalar k:')
    if k is None:
        return
    r = []
    for i in range(len(A)):
        row = []
        for j in range(len(A[0])):
            row.append(k * A[i][j])
        r.append(row)
    _show('k*A', _matlines('kA', r))


def t_mul():
    ra, ca = _dims(A)
    rb, cb = _dims(B)
    if ca != rb:
        _show('ERROR', [_warn('cols A must = rows B'), _warn(str(ca) + ' vs ' + str(rb))])
        return
    r = []
    for i in range(ra):
        row = []
        for j in range(cb):
            s = 0.0
            for k in range(ca):
                s += A[i][k] * B[k][j]
            row.append(s)
        r.append(row)
    _show('A*B', _matlines('AB', r))


def t_trans():
    rows = len(A)
    cols = len(A[0])
    r = []
    for j in range(cols):
        row = []
        for i in range(rows):
            row.append(A[i][j])
        r.append(row)
    _show('A transpose', _matlines('At', r))


def t_det():
    if len(A) != len(A[0]):
        _show('ERROR', [_warn('det needs a'), _warn('square matrix')])
        return
    d = _det(A)
    _show('det A', ['det(A) = ' + _fn(d)])


def t_inv():
    n = len(A)
    if n != len(A[0]):
        _show('ERROR', [_warn('inverse needs a'), _warn('square matrix')])
        return
    d = _det(A)
    if abs(d) < 1e-9:
        _show('inverse', [_w('det = 0'), _warn('A is singular'), 'no inverse'])
        return
    if n == 1:
        _show('inverse', _matlines('Ai', [[1.0 / A[0][0]]]))
        return
    if n == 2:
        a = A[0][0]
        b = A[0][1]
        c = A[1][0]
        e = A[1][1]
        r = [[e / d, -b / d], [-c / d, a / d]]
        _show('inverse', _matlines('Ai', r))
        return
    a = A[0][0]
    b = A[0][1]
    c = A[0][2]
    dd = A[1][0]
    e = A[1][1]
    f = A[1][2]
    g = A[2][0]
    h = A[2][1]
    i = A[2][2]
    co = [[(e * i - f * h), -(dd * i - f * g), (dd * h - e * g)],
          [-(b * i - c * h), (a * i - c * g), -(a * h - b * g)],
          [(b * f - c * e), -(a * f - c * dd), (a * e - b * dd)]]
    r = []
    for p in range(3):
        row = []
        for q in range(3):
            row.append(co[q][p] / d)
        r.append(row)
    _show('inverse', _matlines('Ai', r))


def t_solve():
    n = len(A)
    if n != len(A[0]):
        _show('ERROR', [_warn('solve needs a'), _warn('square matrix A')])
        return
    bb = []
    for i in range(n):
        v = _asknum('b[' + str(i + 1) + ']:')
        if v is None:
            return
        bb.append(v)
    m = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(A[i][j])
        row.append(bb[i])
        m.append(row)
    for col in range(n):
        piv = col
        big = abs(m[col][col])
        for r in range(col + 1, n):
            if abs(m[r][col]) > big:
                big = abs(m[r][col])
                piv = r
        if big < 1e-9:
            _show('solve', ['no unique', 'solution', _warn('(singular A)')])
            return
        if piv != col:
            tmp = m[col]
            m[col] = m[piv]
            m[piv] = tmp
        pv = m[col][col]
        for r in range(n):
            if r != col:
                fac = m[r][col] / pv
                for cc in range(col, n + 1):
                    m[r][cc] -= fac * m[col][cc]
    out = ['solution x:']
    for i in range(n):
        out.append('x' + str(i + 1) + ' = ' + _fn(m[i][n] / m[i][i]))
    _show('solve Ax=b', out)


def t_eig():
    if len(A) != 2 or len(A[0]) != 2:
        _show('ERROR', [_warn('eigenvalues here'), _warn('are 2x2 only')])
        return
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    tr = a + d
    de = a * d - b * c
    disc = tr * tr - 4 * de
    out = [_w('trace = ' + _fn(tr)), _w('det = ' + _fn(de))]
    if disc >= 0:
        r = math.sqrt(disc)
        l1 = (tr + r) / 2.0
        l2 = (tr - r) / 2.0
        out.append('L1 = ' + _fn(l1))
        out.append('L2 = ' + _fn(l2))
    else:
        re = tr / 2.0
        im = math.sqrt(-disc) / 2.0
        out.append('L1 = ' + _fn(re) + ' + ' + _fn(im) + 'i')
        out.append('L2 = ' + _fn(re) + ' - ' + _fn(im) + 'i')
    _show('eigenvalues 2x2', out)


def t_transform():
    global A
    opts = ['Rotation', 'Reflect x-axis', 'Reflect y-axis', 'Reflect y=x', 'Enlargement', 'Stretch', 'Shear']
    c = casui.menu('2D TRANSFORM', opts)
    if c == -1:
        return
    m = None
    note = ''
    if c == 0:
        th = _asknum('angle theta (deg):')
        if th is None:
            return
        rad = th * math.pi / 180.0
        co = math.cos(rad)
        si = math.sin(rad)
        m = [[co, -si], [si, co]]
        note = 'rotation ' + _fn(th) + ' deg'
    elif c == 1:
        m = [[1.0, 0.0], [0.0, -1.0]]
        note = 'reflect in x-axis'
    elif c == 2:
        m = [[-1.0, 0.0], [0.0, 1.0]]
        note = 'reflect in y-axis'
    elif c == 3:
        m = [[0.0, 1.0], [1.0, 0.0]]
        note = 'reflect in y=x'
    elif c == 4:
        k = _asknum('scale factor k:')
        if k is None:
            return
        m = [[k, 0.0], [0.0, k]]
        note = 'enlargement k=' + _fn(k)
    elif c == 5:
        kx = _asknum('x stretch:')
        if kx is None:
            return
        ky = _asknum('y stretch:')
        if ky is None:
            return
        m = [[kx, 0.0], [0.0, ky]]
        note = 'stretch'
    elif c == 6:
        sh = _asknum('shear factor:')
        if sh is None:
            return
        m = [[1.0, sh], [0.0, 1.0]]
        note = 'shear (x direction)'
    A = m
    det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
    lines = [note] + _matlines('A', m) + ['det = ' + _fn(det), _w('|det| = area scale')]
    _show('TRANSFORM', lines)


def t_invariant():
    # An invariant POINT satisfies Ap = p, i.e. (A - I)p = 0. An invariant LINE
    # is mapped to itself as a set: its points move along it but do not leave
    # it. Students routinely conflate the two, so both are reported and the
    # difference is spelled out.
    if A is None:
        _show('INVARIANT', [_warn('Enter A first.')])
        return
    if len(A) != 2 or len(A[0]) != 2:
        _show('INVARIANT', [_warn('A must be 2x2 for this tool.')])
        return
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    lines = [_w(ln) for ln in _matlines('A', A)] + ['']
    # invariant points: (A - I)p = 0
    p = a - 1.0
    q = b
    r = c
    s = d - 1.0
    det = p * s - q * r
    lines.append('INVARIANT POINTS  (A p = p)')
    lines.append(_w('solve (A - I)p = 0:'))
    lines.append(_w('  (' + _fn(p) + ')x + (' + _fn(q) + ')y = 0'))
    lines.append(_w('  (' + _fn(r) + ')x + (' + _fn(s) + ')y = 0'))
    if abs(det) > 1e-12:
        lines.append('det(A - I) = ' + _fn(det) + ', not 0,')
        lines.append('so the origin is the only')
        lines.append('invariant point.')
    else:
        lines.append('det(A - I) = 0, so there is a whole')
        lines.append('LINE of invariant points:')
        if abs(p) > 1e-12 or abs(q) > 1e-12:
            if abs(q) > 1e-12:
                lines.append('  y = ' + _fn(-p / q) + ' x')
            else:
                lines.append('  x = 0')
        elif abs(r) > 1e-12 or abs(s) > 1e-12:
            if abs(s) > 1e-12:
                lines.append('  y = ' + _fn(-r / s) + ' x')
            else:
                lines.append('  x = 0')
        else:
            lines.append('  every point (A is the identity)')
    # invariant lines through the origin: y = mx maps to y = mx, so
    # (c + d m) = m (a + b m), i.e. b m^2 + (a - d) m - c = 0
    lines.append('')
    lines.append('INVARIANT LINES y = m x')
    lines.append(_w('need c + d m = m(a + b m), so'))
    lines.append(_w('  b m^2 + (a - d)m - c = 0'))
    lines.append(_w('  (' + _fn(b) + ')m^2 + (' + _fn(a - d) + ')m - (' + _fn(c) + ') = 0'))
    ms = []
    if abs(b) < 1e-12:
        if abs(a - d) > 1e-12:
            ms.append(c / (a - d))
        elif abs(c) < 1e-12:
            lines.append('  every m works: every line')
            lines.append('  through the origin is invariant')
    else:
        disc = (a - d) * (a - d) + 4.0 * b * c
        if disc < -1e-12:
            lines.append('  no real m: no invariant line')
            lines.append('  through the origin')
        else:
            if disc < 0:
                disc = 0.0
            rt = math.sqrt(disc)
            ms.append((-(a - d) + rt) / (2.0 * b))
            if rt > 1e-12:
                ms.append((-(a - d) - rt) / (2.0 * b))
    for m in ms:
        lines.append('  y = ' + _fn(m) + ' x')
    # x = 0 is invariant when the image of (0,1) has zero x-component
    if abs(b) < 1e-12:
        lines.append('  x = 0 (the y-axis) as well')
    lines.append('')
    lines.append(_w('A line of invariant points is'))
    lines.append(_w('invariant; an invariant line need'))
    lines.append(_w('not have any invariant point on it'))
    lines.append(_w('other than the origin.'))
    _show('INVARIANT', lines)


def t_transform3():
    # 3x3 transformation matrices: rotations about and reflections in the
    # coordinate axes and planes.
    global A
    opts = ['Rotate about x-axis', 'Rotate about y-axis', 'Rotate about z-axis',
            'Reflect in plane x=0', 'Reflect in plane y=0', 'Reflect in plane z=0',
            'Enlargement k']
    c = casui.menu('3D TRANSFORM', opts)
    if c == -1:
        return
    m = None
    note = ''
    if c <= 2:
        th = _asknum('angle theta (deg):')
        if th is None:
            return
        rad = th * math.pi / 180.0
        co = math.cos(rad)
        si = math.sin(rad)
        if c == 0:
            m = [[1.0, 0.0, 0.0], [0.0, co, -si], [0.0, si, co]]
            note = 'rotation ' + _fn(th) + ' deg about x'
        elif c == 1:
            m = [[co, 0.0, si], [0.0, 1.0, 0.0], [-si, 0.0, co]]
            note = 'rotation ' + _fn(th) + ' deg about y'
        else:
            m = [[co, -si, 0.0], [si, co, 0.0], [0.0, 0.0, 1.0]]
            note = 'rotation ' + _fn(th) + ' deg about z'
    elif c == 3:
        m = [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        note = 'reflect in the plane x = 0'
    elif c == 4:
        m = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]
        note = 'reflect in the plane y = 0'
    elif c == 5:
        m = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]
        note = 'reflect in the plane z = 0'
    else:
        k = _asknum('scale factor k:')
        if k is None:
            return
        m = [[k, 0.0, 0.0], [0.0, k, 0.0], [0.0, 0.0, k]]
        note = 'enlargement k = ' + _fn(k)
    A = m
    det = _det(m)
    lines = [note] + _matlines('A', m) + ['det = ' + _fn(det),
                                          _w('|det| = volume scale factor')]
    if det < 0:
        lines.append('det < 0: orientation is reversed')
        lines.append('(it includes a reflection)')
    _show('3D TRANSFORM', lines)


TOOLS = [
    ('Enter A', t_enterA),
    ('Enter B', t_enterB),
    ('Show A and B', t_showAB),
    ('A + B', t_add),
    ('A - B', t_sub),
    ('k * A', t_scalar),
    ('A * B', t_mul),
    ('Transpose A', t_trans),
    ('Determinant A', t_det),
    ('Inverse A', t_inv),
    ('Solve A x = b', t_solve),
    ('Eigenvalues 2x2', t_eig),
    ('2D transform builder', t_transform),
    ('3D transform builder', t_transform3),
    ('Invariant points/lines', t_invariant),
]


def run():
    casutil.run_tools('MATRICES', TOOLS)