import math
import casui
import caslex
import caseng
import cascalc
import caspoly
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_show = casutil.show
_pages = casutil.show
_w = casutil.w
_warn = casutil.warn

def _cstr(z):
    return casutil.fmtc(z.real, z.imag)

def t_recur():
    p = _asknum('p in a_n=p*a(n-1)+q*a(n-2)')
    if p is None:
        return
    q = _asknum('q (the a(n-2) coeff)')
    if q is None:
        return
    a0 = _asknum('a_0')
    if a0 is None:
        return
    a1 = _asknum('a_1')
    if a1 is None:
        return
    disc = p * p + 4 * q
    out = [_w('char: x^2 -(' + _fn(p) + ')x -(' + _fn(q) + ')=0'),
           _w('disc = ' + _fn(disc))]
    if disc > 1e-12:
        sd = math.sqrt(disc)
        r1 = (p + sd) / 2.0
        r2 = (p - sd) / 2.0
        det = r1 - r2
        A = (a1 - a0 * r2) / det
        B = a0 - A
        out.append('roots r1=' + _fn(r1) + ' r2=' + _fn(r2))
        out.append('a_n = A r1^n + B r2^n')
        out.append('A=' + _fn(A) + ' B=' + _fn(B))
    elif disc < -1e-12:
        sd = math.sqrt(-disc)
        re = p / 2.0
        im = sd / 2.0
        mod = math.sqrt(re * re + im * im)
        if re == 0:
            th = math.pi / 2 if im >= 0 else -math.pi / 2
        else:
            th = math.atan(im / re)
            if re < 0:
                th = th + math.pi
        A = a0
        st = math.sin(th)
        if abs(st) < 1e-12 or mod == 0:
            B = 0.0
        else:
            B = (a1 / mod - A * math.cos(th)) / st
        out.append('complex roots, mod=' + _fn(mod))
        out.append('theta=' + _fn(th) + ' rad')
        out.append('a_n=mod^n(A cos(n th)+B sin(n th))')
        out.append('A=' + _fn(A) + ' B=' + _fn(B))
    else:
        r = p / 2.0
        A = a0
        if r == 0:
            B = 0.0
        else:
            B = a1 / r - A
        out.append('repeated root r=' + _fn(r))
        out.append('a_n = (A + B n) r^n')
        out.append('A=' + _fn(A) + ' B=' + _fn(B))
    _pages('Recurrence', out)
    terms = [a0, a1]
    for n in range(2, 10):
        terms.append(p * terms[n - 1] + q * terms[n - 2])
    tl = []
    for n in range(0, 10):
        tl.append('a_' + str(n) + ' = ' + _fn(terms[n]))
    _pages('Terms a_0..a_9', tl)

def t_group():
    n = _askint('Group order n (<=8)')
    if n is None or n < 1 or n > 8:
        _show('Group', [_warn('Need 1..8.')])
        return
    T = []
    for i in range(n):
        s = casui.input_expr('Row ' + str(i) + ' (' + str(n) + ' indices 0..' + str(n - 1) + ')')
        if s is None:
            return
        parts = s.replace(',', ' ').split()
        row = []
        for tok in parts:
            try:
                row.append(int(float(tok)))
            except:
                pass
        if len(row) != n:
            _show('Group', [_warn('Row ' + str(i) + ' needs ' + str(n) + ' entries.')])
            return
        T.append(row)
    out = []
    closed = True
    for i in range(n):
        for j in range(n):
            v = T[i][j]
            if v < 0 or v >= n:
                closed = False
    out.append('Closure: ' + ('yes' if closed else 'NO'))
    if not closed:
        _pages('Group', out)
        return
    ident = -1
    for e in range(n):
        good = True
        for x in range(n):
            if T[e][x] != x or T[x][e] != x:
                good = False
                break
        if good:
            ident = e
            break
    if ident == -1:
        out.append(_warn('Identity: none -> not a group'))
        _pages('Group', out)
        return
    out.append('Identity: e = ' + str(ident))
    inv = [-1] * n
    allinv = True
    for a in range(n):
        for b in range(n):
            if T[a][b] == ident and T[b][a] == ident:
                inv[a] = b
                break
        if inv[a] == -1:
            allinv = False
    out.append('All inverses: ' + ('yes' if allinv else 'NO'))
    ab = True
    for i in range(n):
        for j in range(n):
            if T[i][j] != T[j][i]:
                ab = False
    out.append('Abelian: ' + ('yes' if ab else 'no'))
    orders = []
    cyclic = False
    for a in range(n):
        cur = a
        k = 1
        while cur != ident and k <= n:
            cur = T[a][cur]
            k += 1
        if cur != ident:
            k = 0
        orders.append(k)
        if k == n:
            cyclic = True
    out.append('Cyclic: ' + ('yes' if cyclic else 'no'))
    ol = []
    for a in range(n):
        ol.append('ord(' + str(a) + ') = ' + str(orders[a]))
    divs = []
    for d in range(1, n + 1):
        if n % d == 0:
            divs.append(str(d))
    lag = [_w('Lagrange: elt orders'), _w('must divide n=' + str(n)),
           'divisors: ' + ' '.join(divs)]
    _pages('Group summary', out)
    _pages('Element orders', ol)
    _pages('Lagrange', lag)

def _eigvec(a, b, c, d, L):
    r1 = (a - L, b)
    r2 = (c, d - L)
    if abs(r1[0]) > 1e-9 or abs(r1[1]) > 1e-9:
        pp, qq = r1
    else:
        pp, qq = r2
    if abs(qq) > 1e-12:
        v = (1.0, -pp / qq)
    elif abs(pp) > 1e-12:
        v = (-qq / pp, 1.0)
    else:
        v = (1.0, 0.0)
    return v

def t_eigen():
    a = _asknum('a (top-left)')
    if a is None:
        return
    b = _asknum('b (top-right)')
    if b is None:
        return
    c = _asknum('c (bottom-left)')
    if c is None:
        return
    d = _asknum('d (bottom-right)')
    if d is None:
        return
    tr = a + d
    det = a * d - b * c
    disc = tr * tr - 4 * det
    out = [_w('M=[[' + _fn(a) + ',' + _fn(b) + '],'),
           _w('   [' + _fn(c) + ',' + _fn(d) + ']]'),
           _w('char: L^2-(' + _fn(tr) + ')L+(' + _fn(det) + ')=0'),
           _w('disc=' + _fn(disc))]
    if disc >= -1e-12:
        if disc < 0:
            disc = 0.0
        sd = math.sqrt(disc)
        l1 = (tr + sd) / 2.0
        l2 = (tr - sd) / 2.0
        out.append('lambda1 = ' + _fn(l1))
        out.append('lambda2 = ' + _fn(l2))
        for L in (l1, l2):
            ev = _eigvec(a, b, c, d, L)
            out.append('L=' + _fn(L) + ' v=(' + _fn(ev[0]) + ',' + _fn(ev[1]) + ')')
        if abs(l1 - l2) > 1e-9:
            out.append('Distinct -> diagonalisable:')
            out.append('M = P D P^-1, D=diag(L1,L2)')
            out.append(_w('P cols = eigenvectors'))
        else:
            out.append(_warn('Repeated eigenvalue;'))
            out.append(_warn('diagonalisable only if'))
            out.append(_warn('2 indep eigenvectors.'))
    else:
        sd = math.sqrt(-disc)
        re = tr / 2.0
        im = sd / 2.0
        out.append('complex eigenvalues:')
        out.append('L = ' + _fn(re) + ' +/- ' + _fn(im) + ' i')
        out.append(_warn('(no real eigenvectors)'))
    _pages('2x2 Eigen', out)

_gcd = casutil.gcd
_powmod = casutil.powmod
_modinv = casutil.modinv

def t_mod():
    labels = ['a mod m', 'a^b mod m', 'gcd(a,b)', 'modular inverse']
    while True:
        c = casui.menu('Modular', labels)
        if c == -1:
            return
        if c == 0:
            a = _askint('a')
            m = _askint('m')
            if a is None or m is None or m == 0:
                continue
            _show('a mod m', [str(a) + ' mod ' + str(m) + ' = ' + str(a % m)])
        elif c == 1:
            a = _askint('base a')
            b = _askint('exponent b (>=0)')
            m = _askint('modulus m')
            if a is None or b is None or m is None or m == 0 or b < 0:
                _show('powmod', [_warn('Need m!=0, b>=0.')])
                continue
            _show('a^b mod m', [_w(str(a) + '^' + str(b) + ' mod ' + str(m)),
                                '= ' + str(_powmod(a, b, m))])
        elif c == 2:
            a = _askint('a')
            b = _askint('b')
            if a is None or b is None:
                continue
            _show('gcd', ['gcd(' + str(a) + ',' + str(b) + ') = ' + str(_gcd(a, b))])
        else:
            a = _askint('a')
            m = _askint('modulus m')
            if a is None or m is None or m == 0:
                continue
            inv = _modinv(a, m)
            if inv is None:
                _show('inverse', [_warn('No inverse: gcd(a,m)!=1'),
                                  'gcd=' + str(_gcd(a, m))])
            else:
                _show('inverse', [_w('inv of ' + str(a) + ' mod ' + str(m)),
                                  '= ' + str(inv),
                                  _warn('check: ' + str(a) + '*' + str(inv) +
                                        ' mod m =' + str((a * inv) % m))])

def _mvparse(prompt):
    st = casui.input_expr(prompt)
    if st is None:
        return None
    t = caslex.parse(st)
    if t is None:
        _show('Could not read that', ['"' + st + '" is not an expression',
                                      'this toolkit can read.'])
        return None
    return t


def _at(tree, env):
    try:
        v = caseng.evalf(tree, env['x'] if 'x' in env else 0.0, False, env)
    except:
        return None
    if isinstance(v, complex) or v != v or v > 1.7e308 or v < -1.7e308:
        return None
    return v


def t_partial():
    _show('Partial derivatives', ['Enter z = f(x, y), using both',
                                  'letters, for example x^2*y + y^3.',
                                  'dz/dx treats y as a constant and',
                                  'dz/dy treats x as one.'])
    f = _mvparse('z = f(x,y) =')
    if f is None:
        return
    try:
        fx = cascalc.tidy(caseng.diff(f, 'x'))
        fy = cascalc.tidy(caseng.diff(f, 'y'))
        fxx = cascalc.tidy(caseng.diff(fx, 'x'))
        fyy = cascalc.tidy(caseng.diff(fy, 'y'))
        fxy = cascalc.tidy(caseng.diff(fx, 'y'))
        fyx = cascalc.tidy(caseng.diff(fy, 'x'))
    except:
        _show('Partial derivatives', [_warn('Cannot differentiate that.')])
        return
    lines = [_w('z = ' + caseng.tostr(caseng.simplify(f))), '',
             'dz/dx = ' + caseng.tostr(fx),
             'dz/dy = ' + caseng.tostr(fy), '',
             'd2z/dx2  = ' + caseng.tostr(fxx),
             'd2z/dy2  = ' + caseng.tostr(fyy),
             'd2z/dxdy = ' + caseng.tostr(fxy)]
    if caseng.tostr(fxy) == caseng.tostr(fyx):
        lines.append(_w('d2z/dydx is the same, as it should'))
        lines.append(_w('be for a well-behaved f.'))
    else:
        lines.append('d2z/dydx = ' + caseng.tostr(fyx))
    xv = _asknum('at x = (or cancel)')
    if xv is not None:
        yv = _asknum('and y =')
        if yv is not None:
            env = {'x': xv, 'y': yv}
            lines.append('')
            lines.append('at (' + _fn(xv) + ', ' + _fn(yv) + '):')
            for nm, tr in (('z', f), ('dz/dx', fx), ('dz/dy', fy),
                           ('d2z/dx2', fxx), ('d2z/dy2', fyy), ('d2z/dxdy', fxy)):
                v = _at(tr, env)
                lines.append('  ' + nm + ' = ' + ('undefined' if v is None else _fn(v)))
            gx = _at(fx, env)
            gy = _at(fy, env)
            if gx is not None and gy is not None:
                lines.append('')
                lines.append('grad z = (' + _fn(gx) + ', ' + _fn(gy) + ')')
                lines.append('|grad z| = ' + _fn(math.sqrt(gx * gx + gy * gy)))
                lines.append(_w('(grad points the way z increases'))
                lines.append(_w(' fastest, and is perpendicular to'))
                lines.append(_w(' the contour through the point)'))
    _pages('Partial derivatives', lines)


def t_surface_stat():
    _show('Stationary points of a surface', ['For z = f(x, y), solve',
                                             '  dz/dx = 0 and dz/dy = 0',
                                             'together, then classify with',
                                             '  D = fxx fyy - fxy^2.'])
    f = _mvparse('z = f(x,y) =')
    if f is None:
        return
    try:
        fx = caseng.simplify(caseng.diff(f, 'x'))
        fy = caseng.simplify(caseng.diff(f, 'y'))
        fxx = caseng.simplify(caseng.diff(fx, 'x'))
        fyy = caseng.simplify(caseng.diff(fy, 'y'))
        fxy = caseng.simplify(caseng.diff(fx, 'y'))
    except:
        _show('Stationary points', [_warn('Cannot differentiate that.')])
        return
    x0 = _asknum('start searching near x = [0]')
    if x0 is None:
        x0 = 0.0
    y0 = _asknum('and y = [0]')
    if y0 is None:
        y0 = 0.0
    lines = [_w('z = ' + caseng.tostr(caseng.simplify(f))),
             _w('dz/dx = ' + caseng.tostr(cascalc.tidy(fx))),
             _w('dz/dy = ' + caseng.tostr(cascalc.tidy(fy))), '']
    x = x0
    y = y0
    ok = False
    i = 0
    while i < 60:
        env = {'x': x, 'y': y}
        a = _at(fx, env)
        b = _at(fy, env)
        if a is None or b is None:
            break
        if abs(a) < 1e-12 and abs(b) < 1e-12:
            ok = True
            break
        j11 = _at(fxx, env)
        j12 = _at(fxy, env)
        j22 = _at(fyy, env)
        if j11 is None or j12 is None or j22 is None:
            break
        det = j11 * j22 - j12 * j12
        if abs(det) < 1e-14:
            break
        dx = (a * j22 - b * j12) / det
        dy = (j11 * b - j12 * a) / det
        x -= dx
        y -= dy
        if abs(dx) < 1e-13 and abs(dy) < 1e-13:
            ok = True
            break
        i += 1
    if not ok:
        env = {'x': x, 'y': y}
        a = _at(fx, env)
        b = _at(fy, env)
        ok = a is not None and b is not None and abs(a) < 1e-7 and abs(b) < 1e-7
    if not ok:
        lines.append(_warn('No stationary point found from that'))
        lines.append(_warn('starting guess. Try another - Newton'))
        lines.append(_warn('finds the one it is nearest to.'))
        _pages('Stationary points', lines)
        return
    env = {'x': x, 'y': y}
    zv = _at(f, env)
    A = _at(fxx, env)
    B = _at(fxy, env)
    C = _at(fyy, env)
    lines.append('stationary point at')
    lines.append('  x = ' + _fn(x) + ', y = ' + _fn(y))
    if zv is not None:
        lines.append('  z = ' + _fn(zv))
    if A is None or B is None or C is None:
        lines.append(_warn('second derivatives undefined there.'))
        _pages('Stationary points', lines)
        return
    D = A * C - B * B
    lines.append('')
    lines.append(_w('fxx = ' + _fn(A) + '  fyy = ' + _fn(C) + '  fxy = ' + _fn(B)))
    lines.append(_w('D = fxx fyy - fxy^2 = ' + _fn(D)))
    lines.append('')
    if D > 1e-12:
        if A > 0:
            lines.append('D > 0 and fxx > 0: MINIMUM')
        else:
            lines.append('D > 0 and fxx < 0: MAXIMUM')
    elif D < -1e-12:
        lines.append('D < 0: SADDLE POINT')
        lines.append(_w('(a maximum along one direction and'))
        lines.append(_w(' a minimum along another - there is'))
        lines.append(_w(' no one-variable equivalent)'))
    else:
        lines.append(_warn('D = 0: the test tells you nothing.'))
        lines.append(_warn('Look at f along a few directions'))
        lines.append(_warn('through the point.'))
    _pages('Stationary points', lines)


def t_tangent_plane():
    _show('Tangent plane', ['At (a, b) on z = f(x, y):',
                            '  z = f(a,b) + fx(a,b)(x-a)',
                            '            + fy(a,b)(y-b)',
                            'and the normal has direction',
                            '  (fx, fy, -1).'])
    f = _mvparse('z = f(x,y) =')
    if f is None:
        return
    a = _asknum('at x =')
    if a is None:
        return
    b = _asknum('and y =')
    if b is None:
        return
    try:
        fx = caseng.simplify(caseng.diff(f, 'x'))
        fy = caseng.simplify(caseng.diff(f, 'y'))
    except:
        _show('Tangent plane', [_warn('Cannot differentiate that.')])
        return
    env = {'x': a, 'y': b}
    z0 = _at(f, env)
    p = _at(fx, env)
    q = _at(fy, env)
    if z0 is None or p is None or q is None:
        _show('Tangent plane', [_warn('f or its derivatives are undefined'),
                                _warn('at that point.')])
        return
    lines = [_w('z = ' + caseng.tostr(caseng.simplify(f))),
             'at (' + _fn(a) + ', ' + _fn(b) + '), z = ' + _fn(z0), '',
             _w('fx = ' + caseng.tostr(cascalc.tidy(fx)) + '  ->  ' + _fn(p)),
             _w('fy = ' + caseng.tostr(cascalc.tidy(fy)) + '  ->  ' + _fn(q)), '',
             'TANGENT PLANE',
             '  z = ' + _fn(z0) + ' + ' + _fn(p) + '(x - ' + _fn(a) + ')',
             '           + ' + _fn(q) + '(y - ' + _fn(b) + ')',
             '  i.e. ' + _fn(p) + 'x + ' + _fn(q) + 'y - z = ' +
             _fn(p * a + q * b - z0), '',
             'NORMAL LINE',
             '  r = (' + _fn(a) + ', ' + _fn(b) + ', ' + _fn(z0) + ')',
             '      + t(' + _fn(p) + ', ' + _fn(q) + ', -1)', '',
             'grad f = (' + _fn(p) + ', ' + _fn(q) + ')',
             _w('(the surface normal is (fx, fy, -1);'),
             _w(' grad f alone is the 2-D gradient of'),
             _w(' the height, perpendicular to the'),
             _w(' contour through the point)')]
    _pages('Tangent plane', lines)


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _cubic_roots(a, b, c, d):
    if abs(a) < 1e-14:
        if abs(b) < 1e-14:
            if abs(c) < 1e-14:
                return []
            return [-d / c]
        disc = c * c - 4.0 * b * d
        if disc < 0:
            return []
        r = math.sqrt(disc)
        return sorted([(-c + r) / (2.0 * b), (-c - r) / (2.0 * b)])
    b /= a
    c /= a
    d /= a
    p = c - b * b / 3.0
    q = 2.0 * b * b * b / 27.0 - b * c / 3.0 + d
    off = -b / 3.0
    disc = q * q / 4.0 + p * p * p / 27.0
    if disc > 1e-12:
        s = math.sqrt(disc)
        u = -q / 2.0 + s
        v = -q / 2.0 - s
        cu = (u ** (1.0 / 3.0)) if u >= 0 else -((-u) ** (1.0 / 3.0))
        cv = (v ** (1.0 / 3.0)) if v >= 0 else -((-v) ** (1.0 / 3.0))
        return [cu + cv + off]
    if abs(disc) <= 1e-12:
        if abs(q) < 1e-14:
            return [off]
        u = (-q / 2.0) ** (1.0 / 3.0) if q <= 0 else -((q / 2.0) ** (1.0 / 3.0))
        return sorted([2.0 * u + off, -u + off])
    r = math.sqrt(-p * p * p / 27.0)
    phi = math.acos(max(-1.0, min(1.0, -q / (2.0 * r))))
    m = 2.0 * ((-p / 3.0) ** 0.5)
    out = []
    k = 0
    while k < 3:
        out.append(m * math.cos((phi + 2.0 * math.pi * k) / 3.0) + off)
        k += 1
    return sorted(out)


def _nullvec3(m):
    a = [[m[0][0], m[0][1], m[0][2]],
         [m[1][0], m[1][1], m[1][2]],
         [m[2][0], m[2][1], m[2][2]]]
    piv = []
    row = 0
    col = 0
    while row < 3 and col < 3:
        best = row
        r = row
        while r < 3:
            if abs(a[r][col]) > abs(a[best][col]):
                best = r
            r += 1
        if abs(a[best][col]) < 1e-9:
            col += 1
            continue
        a[row], a[best] = a[best], a[row]
        d = a[row][col]
        j = 0
        while j < 3:
            a[row][j] /= d
            j += 1
        r = 0
        while r < 3:
            if r != row and abs(a[r][col]) > 1e-14:
                f = a[r][col]
                j = 0
                while j < 3:
                    a[r][j] -= f * a[row][j]
                    j += 1
            r += 1
        piv.append(col)
        row += 1
        col += 1
    free = []
    c = 0
    while c < 3:
        if c not in piv:
            free.append(c)
        c += 1
    if not free:
        return None
    fc = free[0]
    v = [0.0, 0.0, 0.0]
    v[fc] = 1.0
    i = 0
    while i < len(piv):
        v[piv[i]] = -a[i][fc]
        i += 1
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if n < 1e-12:
        return None
    big = 0
    k = 1
    while k < 3:
        if abs(v[k]) > abs(v[big]):
            big = k
        k += 1
    s = v[big]
    return [v[0] / s, v[1] / s, v[2] / s]


def t_eigen3():
    _show('3x3 eigenvalues', ['Enter the nine entries of M.',
                              'The characteristic equation',
                              'det(M - kI) = 0 is a cubic; its',
                              'real roots are the eigenvalues.'])
    m = []
    i = 0
    while i < 3:
        row = []
        j = 0
        while j < 3:
            v = _asknum('M[' + str(i + 1) + ',' + str(j + 1) + ']')
            if v is None:
                return
            row.append(v)
            j += 1
        m.append(row)
        i += 1
    tr = m[0][0] + m[1][1] + m[2][2]
    det = _det3(m)
    m2 = ((m[1][1] * m[2][2] - m[1][2] * m[2][1])
          + (m[0][0] * m[2][2] - m[0][2] * m[2][0])
          + (m[0][0] * m[1][1] - m[0][1] * m[1][0]))
    lines = [_w('M =')]
    i = 0
    while i < 3:
        lines.append(_w('  [ ' + _fn(m[i][0]) + '  ' + _fn(m[i][1]) + '  ' +
                     _fn(m[i][2]) + ' ]'))
        i += 1
    lines.append('')
    lines.append(_w('trace = ' + _fn(tr) + ', det = ' + _fn(det)))
    lines.append(_w('characteristic equation:'))
    lines.append(_w('  k^3 - ' + _fn(tr) + 'k^2 + ' + _fn(m2) + 'k - ' +
                 _fn(det) + ' = 0'))
    roots = _cubic_roots(1.0, -tr, m2, -det)
    if not roots:
        lines.append('')
        lines.append(_warn('No real eigenvalue.'))
        _pages('3x3 eigen', lines)
        return
    lines.append('')
    lines.append('eigenvalues (real):')
    vecs = []
    for L in roots:
        lines.append('  k = ' + _fn(L))
        sh = [[m[0][0] - L, m[0][1], m[0][2]],
              [m[1][0], m[1][1] - L, m[1][2]],
              [m[2][0], m[2][1], m[2][2] - L]]
        v = _nullvec3(sh)
        if v is None:
            lines.append(_warn('    eigenvector not recoverable'))
            vecs.append(None)
            continue
        vecs.append(v)
        lines.append('    eigenvector (' + _fn(v[0]) + ', ' + _fn(v[1]) +
                     ', ' + _fn(v[2]) + ')')
        mv = [m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
              m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
              m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]]
        err = 0.0
        k = 0
        while k < 3:
            e = mv[k] - L * v[k]
            err += e if e >= 0 else -e
            k += 1
        lines.append(_warn('    check |Mv - kv| = ' + _fn(err, 6)))
    good = []
    for v in vecs:
        if v is not None:
            good.append(v)
    lines.append('')
    if len(roots) == 3 and len(good) == 3:
        lines.append('Three distinct real eigenvalues, so')
        lines.append('M is DIAGONALISABLE: M = P D P-inverse')
        lines.append('with P the eigenvectors as columns')
        lines.append('and D = diag(' + _fn(roots[0]) + ', ' + _fn(roots[1]) +
                     ', ' + _fn(roots[2]) + ').')
        lines.append('P =')
        i = 0
        while i < 3:
            lines.append('  [ ' + _fn(good[0][i]) + '  ' + _fn(good[1][i]) +
                         '  ' + _fn(good[2][i]) + ' ]')
            i += 1
        n = _askint('M^n for n = (or cancel)', 1, 60)
        if n is not None:
            lines.append('')
            lines.append(_w('M^' + str(n) + ' = P D^' + str(n) +
                         ' P-inverse, with'))
            k = 0
            while k < 3:
                lines.append('  ' + _fn(roots[k]) + '^' + str(n) + ' = ' +
                             _fn(roots[k] ** n, 6))
                k += 1
    else:
        lines.append(_warn('Not three distinct real eigenvalues,'))
        lines.append(_warn('so M may not be diagonalisable over'))
        lines.append(_warn('the reals.'))
    lines.append('')
    lines.append(_w('CAYLEY-HAMILTON: M satisfies its own'))
    lines.append(_w('characteristic equation, so'))
    lines.append('  M^3 = ' + _fn(tr) + 'M^2 - ' + _fn(m2) + 'M + ' + _fn(det) + 'I')
    lines.append(_w('which is how to reduce any higher'))
    lines.append(_w('power by hand.'))
    _pages('3x3 eigen', lines)


def _onlyvars(tree, allowed, title):
    for v in caseng.vars_in(tree):
        if v not in allowed:
            _show(title, ['That expression uses the letter "' + v + '".',
                          'This tool only knows ' + ', '.join(allowed) + '.'])
            return False
    return True


def _fat(tree, n):
    return _at(tree, {'n': float(n)})


def _fsamples(tree, lo, hi):
    out = []
    n = lo
    while n <= hi:
        v = _fat(tree, n)
        if v is None:
            return None
        out.append(v)
        n += 1
    return out


def _polydeg(vals):
    scale = 0.0
    for v in vals:
        if abs(v) > scale:
            scale = abs(v)
    cur = list(vals)
    k = 0
    while k < len(vals) and k <= 5:
        allz = True
        for v in cur:
            if abs(v) > 1e-9 * (scale + 1.0) * (1 << k):
                allz = False
                break
        if allz:
            return k - 1
        nxt = []
        i = 1
        while i < len(cur):
            nxt.append(cur[i] - cur[i - 1])
            i += 1
        cur = nxt
        k += 1
    return None


def _fform(tree):
    vals = _fsamples(tree, 0, 8)
    if vals is None:
        return None
    d = _polydeg(vals)
    if d is not None:
        return (1.0, d if d > 0 else 0)
    if abs(vals[0]) < 1e-300:
        return None
    b = vals[1] / vals[0]
    if abs(b) < 1e-12:
        return None
    v = vals[0]
    i = 0
    while i < len(vals):
        if abs(vals[i] - v) > 1e-7 * (abs(v) + 1.0):
            return None
        v *= b
        i += 1
    return (b, 0)


def _bstr(b):
    s = _fn(b)
    return '(' + s + ')' if b < 0 else s


def _formname(b, d):
    if abs(b - 1.0) < 1e-12:
        if d == 0:
            return 'a constant'
        if d == 1:
            return 'linear in n'
        return 'a polynomial of degree ' + str(d)
    if d == 0:
        return 'k * ' + _bstr(b) + '^n'
    return 'a degree ' + str(d) + ' polynomial times ' + _bstr(b) + '^n'


def _powf(b, n):
    try:
        return b ** n
    except:
        return 1.7e308 if (b > 0 or n % 2 == 0) else -1.7e308


def _bval(e, b, n):
    p = 1.0
    i = 0
    while i < e:
        p *= n
        i += 1
    return p * _powf(b, n)


def _lop(co, e, b, n):
    k = len(co)
    v = _bval(e, b, n + k)
    i = 0
    while i < k:
        v -= co[i] * _bval(e, b, n + i)
        i += 1
    return v


def _lsolve(M, v):
    n = len(v)
    A = []
    i = 0
    while i < n:
        row = list(M[i])
        row.append(v[i])
        A.append(row)
        i += 1
    c = 0
    while c < n:
        best = c
        r = c
        while r < n:
            if abs(A[r][c]) > abs(A[best][c]):
                best = r
            r += 1
        if abs(A[best][c]) < 1e-12:
            return None
        A[c], A[best] = A[best], A[c]
        d = A[c][c]
        j = c
        while j <= n:
            A[c][j] /= d
            j += 1
        r = 0
        while r < n:
            if r != c and abs(A[r][c]) > 1e-15:
                fq = A[r][c]
                j = c
                while j <= n:
                    A[r][j] -= fq * A[c][j]
                    j += 1
            r += 1
        c += 1
    out = []
    i = 0
    while i < n:
        out.append(A[i][n])
        i += 1
    return out


def _particular(co, tree, b, d, s):
    m = d + 1
    M = []
    rhs = []
    n = 0
    while n < m:
        row = []
        j = 0
        while j < m:
            row.append(_lop(co, s + j, b, n))
            j += 1
        M.append(row)
        v = _fat(tree, n)
        if v is None:
            return None
        rhs.append(v)
        n += 1
    c = _lsolve(M, rhs)
    if c is None:
        return None
    j = 0
    while j < m:
        r = float(int(round(c[j])))
        if abs(c[j] - r) < 1e-9 * (abs(c[j]) + 1.0):
            c[j] = r
        j += 1
    n = 0
    while n <= m + 4:
        got = 0.0
        j = 0
        while j < m:
            got += c[j] * _lop(co, s + j, b, n)
            j += 1
        want = _fat(tree, n)
        if want is None:
            return None
        if abs(got - want) > 1e-6 * (abs(want) + 1.0):
            return None
        n += 1
    return c


def _pval(c, b, s, n):
    v = 0.0
    j = 0
    while j < len(c):
        v += c[j] * _bval(s + j, b, n)
        j += 1
    return v


def _mono(coef, e, b, first):
    if abs(coef) < 1e-12:
        return ''
    neg = coef < 0
    mag = -coef if neg else coef
    parts = []
    if e == 0 and abs(b - 1.0) < 1e-12:
        parts.append(_fn(mag))
    else:
        if abs(mag - 1.0) > 1e-9:
            parts.append(_fn(mag))
        if e == 1:
            parts.append('n')
        elif e > 1:
            parts.append('n^' + str(e))
        if abs(b - 1.0) > 1e-12:
            parts.append(_bstr(b) + '^n')
    body = '*'.join(parts)
    if body == '':
        body = '1'
    if first:
        return ('-' + body) if neg else body
    return (' - ' + body) if neg else (' + ' + body)


def _signed(v):
    return ('- ' + _fn(-v)) if v < 0 else ('+ ' + _fn(v))


def _trigterm(c, name, th, first):
    if abs(c) < 1e-12:
        return ''
    neg = c < 0
    mag = -c if neg else c
    body = (('' if abs(mag - 1.0) < 1e-9 else _fn(mag) + '*') + name +
            '(' + _fn(th) + 'n)')
    if first:
        return ('-' + body) if neg else body
    return (' - ' + body) if neg else (' + ' + body)


def _sumstr(terms):
    out = ''
    for c, e, b in terms:
        out += _mono(c, e, b, out == '')
    return out if out != '' else '0'


def _pterms(c, b, s):
    out = []
    j = len(c) - 1
    while j >= 0:
        out.append((c[j], s + j, b))
        j -= 1
    return out


def _asknz(prompt):
    v = _asknum(prompt)
    if v is None:
        return 0
    return int(round(v))


def t_recur_nonhom():
    _show('First order recurrence', ['u(n+1) = a u(n) + f(n)',
          'Solved as A a^n plus a particular',
          'term whose shape follows f(n).'])
    a = _asknum('a in u(n+1) = a u(n) + f(n)')
    if a is None:
        return
    ft = casutil.askexpr('f(n) = (in n; type 0 for none)')
    if ft is None:
        return
    if not _onlyvars(ft, ['n'], 'First order recurrence'):
        return
    u0 = _asknum('first term u(n0) =')
    if u0 is None:
        return
    n0 = _asknz('n0, the index of that term [0]')
    if n0 < 0 or n0 > 100:
        _show('First order recurrence', [_warn('n0 must be between 0 and 100.')])
        return
    lines = [_w('u(n+1) = ' + _fn(a) + ' u(n) + f(n)'),
             _w('f(n) = ' + caseng.tostr(caseng.simplify(ft))),
             _w('u(' + str(n0) + ') = ' + _fn(u0)), '']
    if abs(a) < 1e-12:
        lines.append(_w('a = 0, so u(n+1) = f(n) outright'))
        lines.append(_w('and u(n) = f(n-1) for n > ' + str(n0) + '.'))
        lines.append(_warn('There is no complementary function'))
        lines.append(_warn('to fit.'))
        _pages('First order recurrence', lines + _recur1_terms(a, ft, u0, n0))
        return
    form = _fform(ft)
    c = None
    if form is not None:
        b, d = form
        if d > 4:
            form = None
    if form is not None:
        s = 1 if abs(b - a) < 1e-9 * (abs(a) + 1.0) else 0
        c = _particular([a], ft, b, d, s)
    if c is None:
        lines.append(_warn('f(n) is not a constant, a'))
        lines.append(_warn('polynomial or k b^n, so there is no'))
        lines.append(_warn('standard trial solution. The exact'))
        lines.append(_warn('answer is still'))
        lines.append('  u(n) = a^(n-n0) u(n0)')
        lines.append('       + sum a^(n-1-k) f(k),')
        lines.append('  the sum over k = n0 .. n-1.')
        _pages('First order recurrence', lines + _recur1_terms(a, ft, u0, n0))
        return
    lines.append(_w('f(n) is ' + _formname(b, d) + '.'))
    lines.append(_w('complementary function: A * ' + _bstr(a) + '^n'))
    if s:
        lines.append(_w('RESONANCE: b = a = ' + _fn(a) + ', so the'))
        lines.append(_w('trial term carries an extra n.'))
    lines.append(_w('trial p(n) = ' + _trialstr(b, d, s)))
    lines.append('p(n) = ' + _sumstr(_pterms(c, b, s)))
    A = (u0 - _pval(c, b, s, n0)) / _powf(a, n0)
    lines.append(_w('u(' + str(n0) + ') = ' + _fn(u0) + ' fixes A = ' + _fn(A)))
    closed = _sumstr([(A, 0, a)] + _pterms(c, b, s))
    rows = []
    err = 0.0
    uv = u0
    k = 0
    while k <= 10:
        n = n0 + k
        cf = A * _powf(a, n) + _pval(c, b, s, n)
        e = abs(cf - uv)
        if e / (1.0 + abs(uv)) > err:
            err = e / (1.0 + abs(uv))
        rows.append(_w('n=' + str(n) + '  u=' + _fn(uv) + '  closed=' + _fn(cf)))
        fv = _fat(ft, n)
        if fv is None:
            break
        uv = a * uv + fv
        k += 1
    lines.append('')
    if err < 1e-6:
        lines.append('CLOSED FORM')
        lines.append('u(n) = ' + closed)
        lines.append(_warn('checked against the recurrence for'))
        lines.append(_warn('11 terms: largest relative'))
        lines.append(_warn('difference ' + _fn(err, 10) + '.'))
    else:
        lines.append(_warn('The trial solution did NOT survive'))
        lines.append(_warn('the check (relative difference ' +
                     _fn(err, 6) + '),'))
        lines.append(_warn('so no closed form is offered.'))
        lines.append('candidate was ' + closed)
    lines.append('')
    lines.append(_w('term from the recurrence, then from'))
    lines.append(_w('the closed form:'))
    _pages('First order recurrence', lines + rows)


def _trialstr(b, d, s):
    if d == 0:
        head = 'C'
    else:
        head = '(C0'
        j = 1
        while j <= d:
            head += ' + C' + str(j) + (' n' if j == 1 else ' n^' + str(j))
            j += 1
        head += ')'
    tail = ''
    if s == 1:
        tail += ' n'
    elif s > 1:
        tail += ' n^' + str(s)
    if abs(b - 1.0) > 1e-12:
        tail += ' ' + _bstr(b) + '^n'
    return head + tail


def _recur1_terms(a, ft, u0, n0):
    out = ['', _w('the sequence itself:')]
    uv = u0
    k = 0
    while k <= 10:
        out.append('u(' + str(n0 + k) + ') = ' + _fn(uv))
        fv = _fat(ft, n0 + k)
        if fv is None:
            break
        uv = a * uv + fv
        k += 1
    return out


def _cbasis(kind, p, q, idx, n):
    if kind == 'real':
        return _powf(p, n) if idx == 0 else _powf(q, n)
    if kind == 'rep':
        return _powf(p, n) if idx == 0 else n * _powf(p, n)
    return _powf(p, n) * (math.cos(n * q) if idx == 0 else math.sin(n * q))


def t_recur_nonhom2():
    _show('Second order recurrence', ['u(n+2) = a u(n+1) + b u(n) + f(n)',
          'x^2 - a x - b = 0 gives the',
          'complementary function; a particular',
          'term is added on top.'])
    ca = _asknum('a in u(n+2)=a u(n+1)+b u(n)+f(n)')
    if ca is None:
        return
    cb = _asknum('b (the u(n) coefficient)')
    if cb is None:
        return
    ft = casutil.askexpr('f(n) = (in n; type 0 for none)')
    if ft is None:
        return
    if not _onlyvars(ft, ['n'], 'Second order recurrence'):
        return
    u0 = _asknum('first term u(n0) =')
    if u0 is None:
        return
    u1 = _asknum('next term u(n0+1) =')
    if u1 is None:
        return
    n0 = _asknz('n0, the index of the first [0]')
    if n0 < 0 or n0 > 100:
        _show('Second order recurrence', [_warn('n0 must be between 0 and 100.')])
        return
    lines = [_w('u(n+2) = ' + _fn(ca) + ' u(n+1) ' + _signed(cb) + ' u(n) + f(n)'),
             _w('f(n) = ' + caseng.tostr(caseng.simplify(ft))),
             _w('u(' + str(n0) + ') = ' + _fn(u0) +
             ', u(' + str(n0 + 1) + ') = ' + _fn(u1)), '',
             _w('auxiliary: x^2 - (' + _fn(ca) + ')x - (' + _fn(cb) + ') = 0')]
    disc = ca * ca + 4.0 * cb
    lines.append(_w('discriminant = ' + _fn(disc)))
    if disc > 1e-12:
        sd = math.sqrt(disc)
        r1 = (ca + sd) / 2.0
        r2 = (ca - sd) / 2.0
        kind = 'real'
        pp, qq = r1, r2
        lines.append(_w('distinct real roots r1 = ' + _fn(r1) +
                     ', r2 = ' + _fn(r2)))
        lines.append(_w('CF = A(' + _fn(r1) + ')^n + B(' + _fn(r2) + ')^n'))
    elif disc < -1e-12:
        sd = math.sqrt(-disc)
        re = ca / 2.0
        im = sd / 2.0
        kind = 'cx'
        pp = math.sqrt(re * re + im * im)
        qq = casutil.atan2(im, re)
        lines.append(_w('complex roots ' + _cstr(complex(re, im)) +
                     ' and ' + _cstr(complex(re, -im))))
        lines.append(_w('modulus R = ' + _fn(pp) + ', argument t = ' +
                     _fn(qq) + ' rad'))
        lines.append(_w('CF = R^n (A cos(n t) + B sin(n t))'))
    else:
        kind = 'rep'
        pp = ca / 2.0
        qq = 0.0
        lines.append(_w('repeated root r = ' + _fn(pp)))
        lines.append(_w('CF = (A + B n)(' + _fn(pp) + ')^n'))
    co = [cb, ca]
    form = _fform(ft)
    c = None
    s = 0
    if form is not None:
        fb, d = form
        if d > 4:
            form = None
    if form is not None:
        if abs(fb * fb - ca * fb - cb) < 1e-9 * (1.0 + abs(cb) + abs(ca)):
            s = 1
            if kind == 'rep' and abs(fb - pp) < 1e-9 * (1.0 + abs(pp)):
                s = 2
        c = _particular(co, ft, fb, d, s)
    if c is None:
        lines.append('')
        lines.append(_warn('f(n) is not a constant, a polynomial'))
        lines.append(_warn('or k b^n, so there is no standard'))
        lines.append(_warn('trial solution to add. Only the'))
        lines.append(_warn('sequence itself is shown.'))
        _pages('Second order recurrence',
               lines + _recur2_terms(ca, cb, ft, u0, u1, n0))
        return
    lines.append('')
    lines.append(_w('f(n) is ' + _formname(fb, d) + '.'))
    if s:
        lines.append(_w('RESONANCE: ' + _fn(fb) + ' is a root of the'))
        lines.append(_w('auxiliary equation ' +
                     ('twice' if s == 2 else 'once') + ', so the'))
        lines.append(_w('trial term carries n^' + str(s) + '.'))
    lines.append(_w('trial p(n) = ' + _trialstr(fb, d, s)))
    lines.append('p(n) = ' + _sumstr(_pterms(c, fb, s)))
    g0 = u0 - _pval(c, fb, s, n0)
    g1 = u1 - _pval(c, fb, s, n0 + 1)
    M = [[_cbasis(kind, pp, qq, 0, n0), _cbasis(kind, pp, qq, 1, n0)],
         [_cbasis(kind, pp, qq, 0, n0 + 1), _cbasis(kind, pp, qq, 1, n0 + 1)]]
    AB = _lsolve(M, [g0, g1])
    if AB is None:
        lines.append(_warn('The two given terms do not fix A'))
        lines.append(_warn('and B (the system is singular).'))
        _pages('Second order recurrence',
               lines + _recur2_terms(ca, cb, ft, u0, u1, n0))
        return
    A, B = AB[0], AB[1]
    lines.append(_w('the two given terms fix'))
    lines.append(_w('  A = ' + _fn(A) + ',  B = ' + _fn(B)))
    if kind == 'real':
        closed = _sumstr([(A, 0, pp), (B, 0, qq)] + _pterms(c, fb, s))
    elif kind == 'rep':
        closed = _sumstr([(A, 0, pp), (B, 1, pp)] + _pterms(c, fb, s))
    else:
        inner = _trigterm(A, 'cos', qq, True) + _trigterm(B, 'sin', qq, False)
        if inner == '':
            inner = '0'
        if abs(pp - 1.0) < 1e-9:
            closed = inner
        else:
            closed = _fn(pp) + '^n*(' + inner + ')'
        tail = _sumstr(_pterms(c, fb, s))
        if tail != '0':
            closed += ' + ' + tail
    rows = []
    err = 0.0
    ua = u0
    ub = u1
    k = 0
    while k <= 10:
        n = n0 + k
        cf = (A * _cbasis(kind, pp, qq, 0, n) + B * _cbasis(kind, pp, qq, 1, n)
              + _pval(c, fb, s, n))
        e = abs(cf - ua) / (1.0 + abs(ua))
        if e > err:
            err = e
        rows.append(_w('n=' + str(n) + '  u=' + _fn(ua) + '  closed=' + _fn(cf)))
        fv = _fat(ft, n)
        if fv is None:
            break
        ua, ub = ub, ca * ub + cb * ua + fv
        k += 1
    lines.append('')
    if err < 1e-6:
        lines.append('CLOSED FORM')
        lines.append('u(n) = ' + closed)
        lines.append(_warn('checked against the recurrence for'))
        lines.append(_warn('11 terms: largest relative'))
        lines.append(_warn('difference ' + _fn(err, 10) + '.'))
    else:
        lines.append(_warn('The trial solution did NOT survive'))
        lines.append(_warn('the check (relative difference ' +
                     _fn(err, 6) + '),'))
        lines.append(_warn('so no closed form is offered.'))
        lines.append('candidate was ' + closed)
    lines.append('')
    lines.append(_w('term from the recurrence, then from'))
    lines.append(_w('the closed form:'))
    _pages('Second order recurrence', lines + rows)


def _recur2_terms(ca, cb, ft, u0, u1, n0):
    out = ['', _w('the sequence itself:')]
    ua = u0
    ub = u1
    k = 0
    while k <= 10:
        out.append('u(' + str(n0 + k) + ') = ' + _fn(ua))
        fv = _fat(ft, n0 + k)
        if fv is None:
            break
        ua, ub = ub, ca * ub + cb * ua + fv
        k += 1
    return out


def t_recur_verify():
    labels = ['u(n+1) = f(n, u)', 'u(n+2) = f(n, u, v)']
    c = casui.menu('Verify a solution', labels)
    if c == -1:
        return
    order = c + 1
    _show('Verify a solution', [
        'Type the right-hand side of the',
        'recurrence with',
        '  u for u(n)',
        '  v for u(n+1)   (2nd order only)',
        '  n for the index,',
        'then the closed form you want to',
        'test, as an expression in n.',
        '',
        'Each side is worked out separately',
        'and the two are set side by side.'])
    allowed = ['n', 'u'] if order == 1 else ['n', 'u', 'v']
    rhs = casutil.askexpr('u(n+' + str(order) + ') = (in n, u' +
                          (', v' if order == 2 else '') + ')')
    if rhs is None:
        return
    if not _onlyvars(rhs, allowed, 'Verify a solution'):
        return
    cand = casutil.askexpr('candidate u(n) = (in n)')
    if cand is None:
        return
    if not _onlyvars(cand, ['n'], 'Verify a solution'):
        return
    n0 = _asknz('check from n = [0]')
    if n0 < 0 or n0 > 100:
        _show('Verify a solution', [_warn('start between 0 and 100, please.')])
        return
    lines = [_w('recurrence: u(n+' + str(order) + ') = ' +
             caseng.tostr(caseng.simplify(rhs))),
             _w('candidate:  u(n) = ' + caseng.tostr(caseng.simplify(cand))), '']
    try:
        nplus = ('+', ('v', 'n'), ('n', 1))
        cn1 = caseng.subst(cand, 'n', nplus)
        cn2 = caseng.subst(cand, 'n', ('+', ('v', 'n'), ('n', 2)))
        left = cn1 if order == 1 else cn2
        sub = caseng.subst(rhs, 'u', cand)
        if order == 2:
            sub = caseng.subst(sub, 'v', cn1)
        ls = caseng.tostr(cascalc.tidy(caspoly.collect(caspoly.expand(left))))
        rs = caseng.tostr(cascalc.tidy(caspoly.collect(caspoly.expand(sub))))
        lines.append(_w('substituting the candidate:'))
        lines.append(_w('  LHS u(n+' + str(order) + ') = ' + ls))
        lines.append(_w('  RHS            = ' + rs))
        if ls == rs:
            lines.append('  the two sides are identical after')
            lines.append('  expanding, which settles it exactly.')
        lines.append('')
    except:
        pass
    ok = True
    rows = []
    k = 0
    while k <= 10:
        n = n0 + k
        cv = _fat(cand, n)
        c1 = _fat(cand, n + 1)
        c2 = _fat(cand, n + 2)
        if cv is None or c1 is None or (order == 2 and c2 is None):
            rows.append(_warn('n=' + str(n) + '  undefined there'))
            ok = False
            break
        env = {'n': float(n), 'u': cv}
        if order == 2:
            env['v'] = c1
        rv = _at(rhs, env)
        lv = c1 if order == 1 else c2
        if rv is None:
            rows.append(_warn('n=' + str(n) + '  RHS undefined'))
            ok = False
            break
        d = abs(lv - rv)
        if d > 1e-7 * (1.0 + abs(lv)):
            ok = False
        rows.append(_w('n=' + str(n) + '  LHS=' + _fn(lv) + '  RHS=' + _fn(rv) +
                    '  diff=' + _fn(d, 8)))
        k += 1
    if ok:
        lines.append('VERDICT: the closed form SATISFIES')
        lines.append('the recurrence.')
        lines.append(_w('(It is the solution of that'))
        lines.append(_w(' recurrence with the first ' + str(order)))
        lines.append(_w(' term(s) it produces itself.)'))
    else:
        lines.append(_warn('VERDICT: the closed form does NOT'))
        lines.append(_warn('satisfy the recurrence.'))
    lines.append('')
    lines.append(_w('LHS is u(n+' + str(order) + ') from the closed form,'))
    lines.append(_w('RHS is the recurrence with the closed'))
    lines.append(_w('form substituted:'))
    _pages('Verify a solution', lines + rows)


def t_recur_behave():
    _show('Behaviour of a sequence', ['u(n+1) = f(u(n)).',
          'Reports convergence, divergence,',
          'period and oscillation, and the',
          'fixed points where f(u) = u.'])
    f = casutil.askexpr('u(n+1) = f(u) = (in u)')
    if f is None:
        return
    if not _onlyvars(f, ['u', 'n'], 'Behaviour of a sequence'):
        return
    u0 = _asknum('u(0) =')
    if u0 is None:
        return
    lines = [_w('u(n+1) = ' + caseng.tostr(caseng.simplify(f))),
             _w('u(0) = ' + _fn(u0)), '']
    seq = [u0]
    diverged = False
    broke = False
    n = 0
    while n < 300:
        v = _at(f, {'u': seq[n], 'n': float(n)})
        if v is None:
            broke = True
            break
        if abs(v) > 1e12:
            seq.append(v)
            diverged = True
            break
        seq.append(v)
        n += 1
    shown = []
    i = 0
    while i < len(seq) and i < 12:
        shown.append(_w('u(' + str(i) + ') = ' + _fn(seq[i])))
        i += 1
    m = len(seq) - 1
    conv = False
    if not diverged and not broke and m > 20:
        conv = True
        k = m - 4
        while k < m:
            if abs(seq[k + 1] - seq[k]) > 1e-9 * (1.0 + abs(seq[k])):
                conv = False
                break
            k += 1
    period = 0
    if not diverged and not broke and m > 40 and not conv:
        p = 1
        while p <= 12:
            good = True
            k = m - 2 * p
            while k <= m - p:
                if abs(seq[k] - seq[k + p]) > 1e-7 * (1.0 + abs(seq[k])):
                    good = False
                    break
                k += 1
            if good:
                period = p
                break
            p += 1
    inc = True
    dec = True
    osc = True
    i = 1
    while i < len(seq) and i < 30:
        d = seq[i] - seq[i - 1]
        if d < -1e-12:
            inc = False
        if d > 1e-12:
            dec = False
        if i >= 2:
            e = seq[i - 1] - seq[i - 2]
            if d * e > 0 or abs(d) < 1e-15:
                osc = False
        i += 1
    lines.append('BEHAVIOUR')
    if broke:
        lines.append(_warn('The sequence leaves the domain of f'))
        lines.append(_warn('at u(' + str(len(seq) - 1) + '), so it stops there.'))
    elif diverged:
        lines.append(_warn('DIVERGENT: |u(n)| passes 1e12 by'))
        lines.append(_warn('n = ' + str(len(seq) - 1) + ' and keeps growing.'))
    elif conv:
        lines.append('CONVERGENT: u(n) -> ' + _fn(seq[m]))
        lines.append(_w('The limit L satisfies L = f(L), which'))
        lines.append(_w('is why the fixed points below are'))
        lines.append(_w('the only possible limits.'))
    elif period == 1:
        lines.append('Constant from some point on.')
    elif period:
        lines.append('PERIODIC with period ' + str(period) + ':')
        lines.append(_w('u(n+' + str(period) + ') = u(n) for large n.'))
        cyc = []
        i = m - period + 1
        while i <= m:
            cyc.append(_fn(seq[i]))
            i += 1
        lines.append('the cycle is ' + ', '.join(cyc))
    else:
        lines.append(_warn('Neither settling nor repeating over'))
        lines.append(_warn('300 terms: bounded but not periodic'))
        lines.append(_warn('(or converging too slowly to see).'))
    if inc and not dec:
        lines.append('It is INCREASING over the terms shown.')
    elif dec and not inc:
        lines.append('It is DECREASING over the terms shown.')
    elif osc:
        lines.append('It OSCILLATES: the steps alternate in')
        lines.append('sign, so the terms straddle the limit.')
    lines.append('')
    lines.append('FIXED POINTS  (f(u) = u)')
    if 'n' in caseng.vars_in(f):
        lines.append(_warn('f depends on n as well as u, so there'))
        lines.append(_warn('are no fixed points of a single map.'))
    else:
        try:
            roots = cascalc.solve(('-', f, ('v', 'u')), 'u')
        except:
            roots = []
        if not roots:
            lines.append(_warn('None found in -20 <= u <= 20, so the'))
            lines.append(_warn('sequence has no limit to settle to'))
            lines.append(_warn('in that range.'))
        else:
            try:
                df = caseng.simplify(caseng.diff(f, 'u'))
                lines.append(_w("f'(u) = " + caseng.tostr(cascalc.tidy(df))))
            except:
                df = None
            for r in roots:
                g = None if df is None else _at(df, {'u': r})
                if g is None:
                    lines.append(_warn('u = ' + _fn(r) + '  (slope unknown)'))
                    continue
                if abs(g) < 1.0 - 1e-9:
                    tag = 'ATTRACTING: nearby terms are pulled in'
                elif abs(g) > 1.0 + 1e-9:
                    tag = 'REPELLING: nearby terms are pushed away'
                else:
                    tag = "|f'| = 1: the test decides nothing"
                lines.append('u = ' + _fn(r) + ",  f'= " + _fn(g))
                lines.append('   ' + tag)
    lines.append('')
    lines.append(_w('the first terms:'))
    _pages('Behaviour of a sequence', lines + shown)


def _setnorm(v):
    out = []
    for x in v:
        dup = False
        for y in out:
            if abs(x - y) < 1e-9:
                dup = True
                break
        if not dup:
            out.append(x)
    out.sort()
    return out


def _inset(x, s):
    for y in s:
        if abs(x - y) < 1e-9:
            return True
    return False


def _sunion(a, b):
    out = list(a)
    for x in b:
        if not _inset(x, out):
            out.append(x)
    out.sort()
    return out


def _sinter(a, b):
    out = []
    for x in a:
        if _inset(x, b):
            out.append(x)
    return out


def _sdiff(a, b):
    out = []
    for x in a:
        if not _inset(x, b):
            out.append(x)
    return out


def _ssubset(a, b):
    for x in a:
        if not _inset(x, b):
            return False
    return True


def _seq(a, b):
    return _ssubset(a, b) and _ssubset(b, a)


def _sstr(s):
    if not s:
        return '{ }'
    parts = []
    for x in s:
        parts.append(_fn(x))
    return '{' + ', '.join(parts) + '}'


def t_sets():
    _show('Sets and notation', [
        'Type each set as a list of numbers,',
        'separated by spaces or commas.',
        'Repeats are dropped - a set holds',
        'each element once, and order does',
        'not matter.',
        '',
        'The third set is optional: press',
        'EXIT to work with two.'])
    E = casutil.asklist('universal set E =')
    if E is None:
        return
    A = casutil.asklist('A =')
    if A is None:
        return
    B = casutil.asklist('B =')
    if B is None:
        return
    C = casutil.asklist('C = (optional)')
    E = _setnorm(E)
    A = _setnorm(A)
    B = _setnorm(B)
    C = None if C is None else _setnorm(C)
    E = _sunion(E, _sunion(A, B))
    if C is not None:
        E = _sunion(E, C)
    lines = [_w('NOTATION'),
             _w("  A u B    union: in A or B or both"),
             _w("  A n B    intersection: in both"),
             _w("  A'       complement: in E, not in A"),
             _w("  A \\ B    difference: in A, not in B"),
             _w("  A (+) B  symmetric difference:"),
             _w("           in exactly one of the two"),
             _w("  A c B    A is a subset of B: every"),
             _w("           element of A is in B"),
             _w("  |A|      cardinality: how many"),
             _w("  P(A)     power set: every subset"),
             _w("  { }      the empty set"),
             '',
             _w('E = ' + _sstr(E) + '   |E| = ' + str(len(E))),
             _w('A = ' + _sstr(A) + '   |A| = ' + str(len(A))),
             _w('B = ' + _sstr(B) + '   |B| = ' + str(len(B)))]
    if C is not None:
        lines.append(_w('C = ' + _sstr(C) + '   |C| = ' + str(len(C))))
    un = _sunion(A, B)
    it = _sinter(A, B)
    lines.append('')
    lines.append('A u B = ' + _sstr(un) + '   |A u B| = ' + str(len(un)))
    lines.append('A n B = ' + _sstr(it) + '   |A n B| = ' + str(len(it)))
    lines.append("A' = " + _sstr(_sdiff(E, A)))
    lines.append("B' = " + _sstr(_sdiff(E, B)))
    lines.append('A \\ B = ' + _sstr(_sdiff(A, B)))
    lines.append('B \\ A = ' + _sstr(_sdiff(B, A)))
    lines.append('A (+) B = ' + _sstr(_sunion(_sdiff(A, B), _sdiff(B, A))))
    lines.append('')
    lines.append('|A| + |B| - |A n B| = ' + str(len(A)) + ' + ' + str(len(B)) +
                 ' - ' + str(len(it)) + ' = ' + str(len(A) + len(B) - len(it)))
    lines.append('which is |A u B| = ' + str(len(un)) +
                 ('  (agrees)' if len(un) == len(A) + len(B) - len(it)
                  else '  (DISAGREES)'))
    lines.append('')
    lines.append('A c B: ' + ('YES' if _ssubset(A, B) else 'no'))
    lines.append('B c A: ' + ('YES' if _ssubset(B, A) else 'no'))
    lines.append('A = B: ' + ('YES' if _seq(A, B) else 'no'))
    lines.append('A and B disjoint (A n B = { }): ' +
                 ('YES' if not it else 'no'))
    lines.append('')
    lines.append('|P(A)| = 2^' + str(len(A)) + ' = ' + str(1 << len(A)))
    lines.append('|P(B)| = 2^' + str(len(B)) + ' = ' + str(1 << len(B)))
    if len(A) <= 4:
        subs = []
        mask = 0
        while mask < (1 << len(A)):
            sub = []
            i = 0
            while i < len(A):
                if mask & (1 << i):
                    sub.append(A[i])
                i += 1
            subs.append(_sstr(sub))
            mask += 1
        lines.append('P(A) = { ' + ', '.join(subs) + ' }')
    lines.append('')
    lines.append('DE MORGAN')
    dm1 = _seq(_sdiff(E, un), _sinter(_sdiff(E, A), _sdiff(E, B)))
    dm2 = _seq(_sdiff(E, it), _sunion(_sdiff(E, A), _sdiff(E, B)))
    lines.append("(A u B)' = " + _sstr(_sdiff(E, un)))
    lines.append("A' n B'  = " + _sstr(_sinter(_sdiff(E, A), _sdiff(E, B))))
    lines.append('  equal: ' + ('YES' if dm1 else 'NO'))
    lines.append("(A n B)' = " + _sstr(_sdiff(E, it)))
    lines.append("A' u B'  = " + _sstr(_sunion(_sdiff(E, A), _sdiff(E, B))))
    lines.append('  equal: ' + ('YES' if dm2 else 'NO'))
    if C is not None:
        lines.append('')
        lines.append('THREE SETS')
        lines.append('A u B u C = ' + _sstr(_sunion(un, C)))
        lines.append('A n B n C = ' + _sstr(_sinter(it, C)))
        lines.append('(A u B) n C = ' + _sstr(_sinter(un, C)))
        lines.append('(A n C) u (B n C) = ' +
                     _sstr(_sunion(_sinter(A, C), _sinter(B, C))))
        lines.append('  those two are equal: ' +
                     ('YES' if _seq(_sinter(un, C),
                                    _sunion(_sinter(A, C), _sinter(B, C)))
                      else 'NO'))
        tot = (len(A) + len(B) + len(C) - len(it) - len(_sinter(A, C))
               - len(_sinter(B, C)) + len(_sinter(it, C)))
        lines.append(_w('inclusion-exclusion for three sets'))
        lines.append(_w('gives |A u B u C| = ' + str(tot) + ', and counting'))
        lines.append(_w('them gives ' + str(len(_sunion(un, C))) + '.'))
    _pages('Sets and notation', lines)


def _readtable(tag, n):
    T = []
    i = 0
    while i < n:
        s = casui.input_expr(tag + ' row ' + str(i) + ' (' + str(n) +
                             ' indices 0..' + str(n - 1) + ')')
        if s is None:
            return None
        row = []
        for tok in s.replace(',', ' ').split():
            try:
                row.append(int(float(tok)))
            except:
                pass
        if len(row) != n:
            return None
        for v in row:
            if v < 0 or v >= n:
                return None
        T.append(row)
        i += 1
    return T


def _identity(T):
    n = len(T)
    e = 0
    while e < n:
        good = True
        x = 0
        while x < n:
            if T[e][x] != x or T[x][e] != x:
                good = False
                break
            x += 1
        if good:
            return e
        e += 1
    return -1


def _inverses(T, e):
    n = len(T)
    inv = []
    a = 0
    while a < n:
        found = -1
        b = 0
        while b < n:
            if T[a][b] == e and T[b][a] == e:
                found = b
                break
            b += 1
        inv.append(found)
        a += 1
    return inv


def _cyclic_sub(T, e, a):
    n = len(T)
    out = [a]
    cur = a
    k = 0
    while cur != e and k < n:
        cur = T[a][cur]
        out.append(cur)
        k += 1
    if cur != e:
        return None
    got = []
    for v in out:
        if v not in got:
            got.append(v)
    got.sort()
    return got


def t_subgroups():
    _show('Subgroups and Lagrange', ['Enter the order, then the Cayley',
          'table row by row.',
          'Lists every subgroup with its',
          'index [G:H]. |H| divides |G|.'])
    n = _askint('Group order n (<=8)')
    if n is None or n < 1 or n > 8:
        _show('Subgroups', [_warn('Need 1..8.')])
        return
    T = _readtable('G', n)
    if T is None:
        _show('Subgroups', [_warn('Each row needs ' + str(n) + ' entries,'),
                            _warn('each one an index 0..' + str(n - 1) + '.')])
        return
    e = _identity(T)
    if e < 0:
        _show('Subgroups', [_warn('That table has no two-sided'),
                            _warn('identity, so it is not a group.')])
        return
    inv = _inverses(T, e)
    for a in range(n):
        if inv[a] < 0:
            _show('Subgroups', [_warn('Element ' + str(a) + ' has no inverse,'),
                                _warn('so this is not a group.')])
            return
    lines = ['|G| = ' + str(n) + ', identity e = ' + str(e), '']
    selfinv = True
    a = 0
    while a < n:
        if inv[a] != a:
            selfinv = False
        a += 1
    lines.append('CYCLIC SUBGROUPS <a>')
    lines.append(_w('(the powers of a single element)'))
    found = []
    a = 0
    while a < n:
        H = _cyclic_sub(T, e, a)
        if H is None:
            lines.append(_warn('<' + str(a) + '> never returns to e'))
            a += 1
            continue
        lines.append('<' + str(a) + '> = ' + _sstr(H) + '   order ' +
                     str(len(H)) + ',  ord(' + str(a) + ') = ' + str(len(H)))
        key = _sstr(H)
        if key not in found:
            found.append(key)
        a += 1
    lines.append('')
    lines.append('distinct cyclic subgroups: ' + str(len(found)))
    subs = []
    mask = 0
    while mask < (1 << n):
        if not (mask & (1 << e)):
            mask += 1
            continue
        mem = []
        i = 0
        while i < n:
            if mask & (1 << i):
                mem.append(i)
            i += 1
        ok = True
        for i in mem:
            for j in mem:
                if T[i][j] not in mem:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            for i in mem:
                if inv[i] not in mem:
                    ok = False
                    break
        if ok:
            subs.append(mem)
        mask += 1
    ordered = []
    for H in subs:
        pos = 0
        while pos < len(ordered) and len(ordered[pos]) <= len(H):
            pos += 1
        ordered.insert(pos, H)
    subs = ordered
    lines.append('')
    lines.append('ALL SUBGROUPS H <= G: ' + str(len(subs)) + ' of them')
    counts = [0] * (n + 1)
    lag = True
    for H in subs:
        k = len(H)
        counts[k] += 1
        if n % k:
            lag = False
        lines.append(_sstr(H) + '   |H| = ' + str(k) + ',  [G:H] = ' +
                     (str(n // k) if k and n % k == 0 else '?'))
    lines.append('')
    lines.append('LAGRANGE')
    k = 1
    while k <= n:
        if counts[k]:
            lines.append('subgroups of order ' + str(k) + ': ' +
                         str(counts[k]) +
                         ('  (' + str(n) + '/' + str(k) + ' = ' +
                          str(n // k) + ')' if n % k == 0
                          else '  DOES NOT DIVIDE ' + str(n)))
        k += 1
    lines.append('every |H| divides |G| = ' + str(n) + ': ' +
                 ('YES' if lag else 'NO'))
    divs = []
    d = 1
    while d <= n:
        if n % d == 0:
            divs.append(str(d))
        d += 1
    lines.append('divisors of ' + str(n) + ': ' + ' '.join(divs))
    lines.append(_w('The converse of Lagrange is false in'))
    lines.append(_w('general: a divisor of |G| need not be'))
    lines.append(_w('the order of any subgroup.'))
    if selfinv:
        lines.append('')
        lines.append('Every element is its own inverse,')
        lines.append('so every non-identity element has')
        lines.append('order 2 and the group is abelian.')
    _pages('Subgroups and Lagrange', lines)


def t_isomorph():
    _show('Group isomorphism', ['Enter the order, then a Cayley table',
          'for G and one for H.',
          'Searches for a bijection phi with',
          'phi(ab) = phi(a) phi(b).'])
    n = _askint('order of both groups (<=8)')
    if n is None or n < 1 or n > 8:
        _show('Group isomorphism', [_warn('Need 1..8.')])
        return
    G = _readtable('G', n)
    if G is None:
        _show('Group isomorphism', [_warn('G: each row needs ' + str(n) +
                                    ' indices 0..' + str(n - 1) + '.')])
        return
    H = _readtable('H', n)
    if H is None:
        _show('Group isomorphism', [_warn('H: each row needs ' + str(n) +
                                    ' indices 0..' + str(n - 1) + '.')])
        return
    eg = _identity(G)
    eh = _identity(H)
    if eg < 0 or eh < 0:
        _show('Group isomorphism', [_warn('One of the tables has no'),
                                    _warn('identity, so it is not a group.')])
        return
    og = _orders(G, eg)
    oh = _orders(H, eh)
    lines = [_w('|G| = |H| = ' + str(n)),
             _w('identity of G is ' + str(eg) + ', of H is ' + str(eh)), '',
             _w('element orders in G: ' + ' '.join([str(v) for v in og])),
             _w('element orders in H: ' + ' '.join([str(v) for v in oh]))]
    if sorted(og) != sorted(oh):
        lines.append('')
        lines.append('The two order lists do not match, and')
        lines.append('an isomorphism must preserve orders,')
        lines.append('so G and H are NOT isomorphic.')
        _pages('Group isomorphism', lines)
        return
    phi = [-1] * n
    used = [False] * n
    phi[eg] = eh
    used[eh] = True
    order_g = []
    a = 0
    while a < n:
        if a != eg:
            order_g.append(a)
        a += 1
    cand = [0] * len(order_g)
    depth = 0
    ok = False
    while depth >= 0:
        if depth >= len(order_g):
            ok = True
            break
        g = order_g[depth]
        if phi[g] >= 0:
            used[phi[g]] = False
            phi[g] = -1
        h = cand[depth]
        placed = False
        while h < n:
            if not used[h] and og[g] == oh[h]:
                phi[g] = h
                used[h] = True
                if _partial_ok(G, H, phi):
                    placed = True
                    break
                used[h] = False
                phi[g] = -1
            h += 1
        if placed:
            cand[depth] = h + 1
            depth += 1
            if depth < len(order_g):
                cand[depth] = 0
        else:
            cand[depth] = 0
            depth -= 1
    if not ok:
        lines.append('')
        lines.append('Every order-preserving bijection was')
        lines.append('tried and none is a homomorphism, so')
        lines.append('G and H are NOT isomorphic.')
        _pages('Group isomorphism', lines)
        return
    bad = 0
    i = 0
    while i < n:
        j = 0
        while j < n:
            if phi[G[i][j]] != H[phi[i]][phi[j]]:
                bad += 1
            j += 1
        i += 1
    lines.append('')
    lines.append('G and H are ISOMORPHIC.')
    lines.append('phi:')
    a = 0
    while a < n:
        lines.append('  ' + str(a) + ' -> ' + str(phi[a]) +
                     '   (order ' + str(og[a]) + ')')
        a += 1
    lines.append('')
    lines.append(_warn('checked phi(ab) = phi(a)phi(b) for all ' +
                 str(n * n) + ' products:'))
    lines.append(_warn('mismatches = ' + str(bad) +
                 ('  (a genuine isomorphism)' if bad == 0 else '  (FAILED)')))
    _pages('Group isomorphism', lines)


def _orders(T, e):
    n = len(T)
    out = []
    a = 0
    while a < n:
        cur = a
        k = 1
        while cur != e and k <= n:
            cur = T[a][cur]
            k += 1
        out.append(k if cur == e else 0)
        a += 1
    return out


def _partial_ok(G, H, phi):
    n = len(G)
    i = 0
    while i < n:
        if phi[i] >= 0:
            j = 0
            while j < n:
                if phi[j] >= 0:
                    k = G[i][j]
                    if phi[k] >= 0 and phi[k] != H[phi[i]][phi[j]]:
                        return False
                j += 1
        i += 1
    return True


def _cross(pts, x, y, ex, ey, za, zb, k):
    if (za - k) * (zb - k) > 0 or za == zb:
        return
    t = (k - za) / (zb - za)
    pts.append((x + ex * t, y + ey * t))


def t_contours():
    _show('Contours and sections', ['z = f(x, y).',
          'A contour is f = k; a section holds',
          'one variable fixed.',
          'Enter f, then the x and y ranges.'])
    f = _mvparse('z = f(x,y) =')
    if f is None:
        return
    xlo = _asknum('x from [-3]')
    if xlo is None:
        xlo = -3.0
    xhi = _asknum('x to [3]')
    if xhi is None:
        xhi = 3.0
    if xhi <= xlo:
        xhi = xlo + 1.0
    ylo = _asknum('y from [-3]')
    if ylo is None:
        ylo = -3.0
    yhi = _asknum('y to [3]')
    if yhi is None:
        yhi = 3.0
    if yhi <= ylo:
        yhi = ylo + 1.0
    NX = 36
    NY = 24
    grid = []
    zlo = None
    zhi = None
    j = 0
    while j <= NY:
        yv = ylo + (yhi - ylo) * j / NY
        row = []
        i = 0
        while i <= NX:
            xv = xlo + (xhi - xlo) * i / NX
            v = _at(f, {'x': xv, 'y': yv})
            row.append(v)
            if v is not None:
                if zlo is None or v < zlo:
                    zlo = v
                if zhi is None or v > zhi:
                    zhi = v
            i += 1
        grid.append(row)
        j += 1
    if zlo is None:
        _show('Contours', [_warn('f could not be evaluated anywhere'),
                           _warn('on that rectangle.')])
        return
    lines = [_w('z = ' + caseng.tostr(caseng.simplify(f))),
             _w('x in [' + _fn(xlo) + ', ' + _fn(xhi) + '], y in [' +
             _fn(ylo) + ', ' + _fn(yhi) + ']'),
             _w('on a ' + str(NX + 1) + ' x ' + str(NY + 1) + ' grid'),
             'z runs from ' + _fn(zlo) + ' to ' + _fn(zhi), '']
    levels = []
    m = 1
    while m <= 5:
        levels.append(zlo + (zhi - zlo) * m / 6.0)
        m += 1
    ls = []
    for k in levels:
        ls.append(_fn(k))
    lines.append('contour levels: ' + ', '.join(ls))
    if zhi - zlo < 1e-12:
        lines.append(_warn('z is constant here, so every point'))
        lines.append(_warn('is on the same contour and there is'))
        lines.append(_warn('nothing to draw.'))
        _pages('Contours and sections', lines)
        return
    ysec = []
    m = 1
    while m <= 3:
        ysec.append(ylo + (yhi - ylo) * m / 4.0)
        m += 1
    ss = []
    for yv in ysec:
        ss.append(_fn(yv))
    lines.append(_w('sections drawn at y = ' + ', '.join(ss)))
    lines.append('')
    lines.append(_w('the middle section, z against x at'))
    lines.append(_w('y = ' + _fn(ysec[1]) + ':'))
    i = 0
    while i <= 6:
        xv = xlo + (xhi - xlo) * i / 6.0
        v = _at(f, {'x': xv, 'y': ysec[1]})
        lines.append('  x = ' + _fn(xv) + '   z = ' +
                     ('undefined' if v is None else _fn(v)))
        i += 1
    lines.append('')
    lines.append(_w('Closed contours around a point mean a'))
    lines.append(_w('maximum or a minimum there; contours'))
    lines.append(_w('that cross mean a saddle. Contours'))
    lines.append(_w('close together mean a steep surface.'))
    _pages('Contours and sections', lines)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'contours of z = f(x,y)', 'x', 'y')
    dx = (xhi - xlo) / NX
    dy = (yhi - ylo) / NY
    for k in levels:
        j = 0
        while j < NY:
            i = 0
            while i < NX:
                z00 = grid[j][i]
                z10 = grid[j][i + 1]
                z01 = grid[j + 1][i]
                z11 = grid[j + 1][i + 1]
                if (z00 is None or z10 is None or z01 is None or
                        z11 is None):
                    i += 1
                    continue
                x0 = xlo + i * dx
                y0 = ylo + j * dy
                pts = []
                _cross(pts, x0, y0, dx, 0.0, z00, z10, k)
                _cross(pts, x0 + dx, y0, 0.0, dy, z10, z11, k)
                _cross(pts, x0, y0 + dy, dx, 0.0, z01, z11, k)
                _cross(pts, x0, y0, 0.0, dy, z00, z01, k)
                if len(pts) >= 2:
                    casutil.seg(fr, pts[0][0], pts[0][1], pts[1][0],
                                pts[1][1], casui.ACC)
                if len(pts) == 4:
                    casutil.seg(fr, pts[2][0], pts[2][1], pts[3][0],
                                pts[3][1], casui.ACC)
                i += 1
            j += 1
    casutil.chart_hold('levels ' + ls[0] + ' .. ' + ls[4])
    fr2 = casutil.frame(xlo, xhi, zlo, zhi)
    casutil.axes(fr2, 'sections z against x', 'x', 'z')
    for yv in ysec:
        px = None
        pz = None
        i = 0
        while i <= NX:
            xv = xlo + (xhi - xlo) * i / NX
            v = _at(f, {'x': xv, 'y': yv})
            if v is not None and pz is not None:
                casutil.seg(fr2, px, pz, xv, v, casui.ACC)
            px = xv
            pz = v
            i += 1
    casutil.chart_hold('y = ' + ', '.join(ss))


TOOLS = [
    ('Recurrence relation', t_recur),
    ('Recurrence 1st order', t_recur_nonhom),
    ('Recurrence 2nd order', t_recur_nonhom2),
    ('Verify a recurrence', t_recur_verify),
    ('Recurrence behaviour', t_recur_behave),
    ('Sets and notation', t_sets),
    ('Group theory', t_group),
    ('Subgroups & Lagrange', t_subgroups),
    ('Group isomorphism', t_isomorph),
    ('2x2 Eigen/diag', t_eigen),
    ('Modular arithmetic', t_mod),
    ('Partial derivatives', t_partial),
    ('Surface stationary pts', t_surface_stat),
    ('Tangent plane / normal', t_tangent_plane),
    ('Contours & sections', t_contours),
    ('3x3 Eigen/diag', t_eigen3),
]

def run():
    casutil.run_tools('Extra Pure', TOOLS)
