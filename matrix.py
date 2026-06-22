import math
import casui
import caslex
import caseng

A = [[0.0]]
B = [[0.0]]


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


def _askint(prompt, lo, hi):
    v = _asknum(prompt)
    if v is None:
        return None
    n = int(round(v))
    if n < lo:
        n = lo
    if n > hi:
        n = hi
    return n


def _fn(x):
    r = round(x, 4)
    if r == 0:
        r = 0.0
    if r == int(r):
        return str(int(r))
    return str(r)


def _show(title, lines):
    casui.result_screen(title, lines)


def _rowstr(row):
    parts = []
    for v in row:
        parts.append(_fn(v))
    return '[ ' + '  '.join(parts) + ' ]'


def _matlines(name, m):
    out = []
    if m is None:
        return [name + ' not set']
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
        _show('ERROR', ['A and B must be', 'the same size'])
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
        _show('ERROR', ['cols A must = rows B', str(ca) + ' vs ' + str(rb)])
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
        _show('ERROR', ['det needs a', 'square matrix'])
        return
    d = _det(A)
    _show('det A', ['det(A) = ' + _fn(d)])


def t_inv():
    n = len(A)
    if n != len(A[0]):
        _show('ERROR', ['inverse needs a', 'square matrix'])
        return
    d = _det(A)
    if abs(d) < 1e-9:
        _show('inverse', ['det = 0', 'A is singular', 'no inverse'])
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
        _show('ERROR', ['solve needs a', 'square matrix A'])
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
            _show('solve', ['no unique', 'solution', '(singular A)'])
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
        _show('ERROR', ['eigenvalues here', 'are 2x2 only'])
        return
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    tr = a + d
    de = a * d - b * c
    disc = tr * tr - 4 * de
    out = ['trace = ' + _fn(tr), 'det = ' + _fn(de)]
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
    lines = [note] + _matlines('A', m) + ['det = ' + _fn(det), '|det| = area scale']
    _show('TRANSFORM', lines)


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
]


def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('MATRICES', labels)
        if c == -1:
            return
        TOOLS[c][1]()