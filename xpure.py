import math
import casui
import caslex
import caseng
import cascalc
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now

def _cstr(z):
    return casutil.fmtc(z.real, z.imag)

# ---------- recurrence relation a_n = p a(n-1) + q a(n-2) ----------
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
    # characteristic: x^2 - p x - q = 0
    disc = p * p + 4 * q
    out = ['char: x^2 -(' + _fn(p) + ')x -(' + _fn(q) + ')=0', 'disc = ' + _fn(disc)]
    if disc > 1e-12:
        sd = math.sqrt(disc)
        r1 = (p + sd) / 2.0
        r2 = (p - sd) / 2.0
        # a0 = A+B, a1 = A r1 + B r2
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
        # theta = atan(im/re) adjusted for quadrant (no atan2 on this device)
        if re == 0:
            th = math.pi / 2 if im >= 0 else -math.pi / 2
        else:
            th = math.atan(im / re)
            if re < 0:
                th = th + math.pi
        # a0 = A , a1 = mod(A cos th + B sin th); im>0 so theta in (0,pi), sin th>0
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
        # a0 = A , a1 = (A+B) r
        A = a0
        if r == 0:
            B = 0.0
        else:
            B = a1 / r - A
        out.append('repeated root r=' + _fn(r))
        out.append('a_n = (A + B n) r^n')
        out.append('A=' + _fn(A) + ' B=' + _fn(B))
    _pages('Recurrence', out)
    # generate terms iteratively
    terms = [a0, a1]
    for n in range(2, 10):
        terms.append(p * terms[n - 1] + q * terms[n - 2])
    tl = []
    for n in range(0, 10):
        tl.append('a_' + str(n) + ' = ' + _fn(terms[n]))
    _pages('Terms a_0..a_9', tl)

# ---------- group theory (Cayley table of element indices) ----------
def t_group():
    n = _askint('Group order n (<=8)')
    if n is None or n < 1 or n > 8:
        _show('Group', ['Need 1..8.'])
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
            _show('Group', ['Row ' + str(i) + ' needs ' + str(n) + ' entries.'])
            return
        T.append(row)
    out = []
    # closure: every product index is a valid element 0..n-1
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
    # identity: e with T[e][x]=x and T[x][e]=x for all x (two-sided)
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
        out.append('Identity: none -> not a group')
        _pages('Group', out)
        return
    out.append('Identity: e = ' + str(ident))
    # inverses: a*b = b*a = e
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
    # abelian: T symmetric
    ab = True
    for i in range(n):
        for j in range(n):
            if T[i][j] != T[j][i]:
                ab = False
    out.append('Abelian: ' + ('yes' if ab else 'no'))
    # order of each element: smallest k>=1 with a^k = e
    orders = []
    cyclic = False
    for a in range(n):
        cur = a          # a^1
        k = 1
        while cur != ident and k <= n:
            cur = T[a][cur]   # multiply by a
            k += 1
        if cur != ident:
            k = 0  # no finite order in this table (not a true group element)
        orders.append(k)
        if k == n:
            cyclic = True
    out.append('Cyclic: ' + ('yes' if cyclic else 'no'))
    ol = []
    for a in range(n):
        ol.append('ord(' + str(a) + ') = ' + str(orders[a]))
    # Lagrange note: order of every element divides n
    divs = []
    for d in range(1, n + 1):
        if n % d == 0:
            divs.append(str(d))
    lag = ['Lagrange: elt orders', 'must divide n=' + str(n), 'divisors: ' + ' '.join(divs)]
    _pages('Group summary', out)
    _pages('Element orders', ol)
    _pages('Lagrange', lag)

# ---------- 2x2 eigenvalues + eigenvectors ----------
def _eigvec(a, b, c, d, L):
    # solve (A - L I) v = 0 ; rows: (a-L)x + b y = 0 ; c x + (d-L)y = 0
    r1 = (a - L, b)
    r2 = (c, d - L)
    if abs(r1[0]) > 1e-9 or abs(r1[1]) > 1e-9:
        pp, qq = r1
    else:
        pp, qq = r2
    # pp x + qq y = 0 -> proportional vector
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
    out = ['M=[[' + _fn(a) + ',' + _fn(b) + '],', '   [' + _fn(c) + ',' + _fn(d) + ']]',
           'char: L^2-(' + _fn(tr) + ')L+(' + _fn(det) + ')=0', 'disc=' + _fn(disc)]
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
            out.append('P cols = eigenvectors')
        else:
            out.append('Repeated eigenvalue;')
            out.append('diagonalisable only if')
            out.append('2 indep eigenvectors.')
    else:
        sd = math.sqrt(-disc)
        re = tr / 2.0
        im = sd / 2.0
        out.append('complex eigenvalues:')
        out.append('L = ' + _fn(re) + ' +/- ' + _fn(im) + ' i')
        out.append('(no real eigenvectors)')
    _pages('2x2 Eigen', out)

# ---------- modular arithmetic ----------
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
                _show('powmod', ['Need m!=0, b>=0.'])
                continue
            _show('a^b mod m', [str(a) + '^' + str(b) + ' mod ' + str(m), '= ' + str(_powmod(a, b, m))])
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
                _show('inverse', ['No inverse: gcd(a,m)!=1', 'gcd=' + str(_gcd(a, m))])
            else:
                _show('inverse', ['inv of ' + str(a) + ' mod ' + str(m), '= ' + str(inv),
                                  'check: ' + str(a) + '*' + str(inv) + ' mod m =' + str((a * inv) % m)])

# ---------- numerical partial derivative (single-var engine) ----------
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
    # Real partial derivatives, taken symbolically. This used to be a
    # single-variable central difference that said so in its own output,
    # because the engine only bound x - caseng.diff has always taken a
    # variable, and evalf now takes an environment, so dz/dy is no harder
    # than dz/dx.
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
        _show('Partial derivatives', ['Cannot differentiate that.'])
        return
    lines = ['z = ' + caseng.tostr(caseng.simplify(f)), '',
             'dz/dx = ' + caseng.tostr(fx),
             'dz/dy = ' + caseng.tostr(fy), '',
             'd2z/dx2  = ' + caseng.tostr(fxx),
             'd2z/dy2  = ' + caseng.tostr(fyy),
             'd2z/dxdy = ' + caseng.tostr(fxy)]
    if caseng.tostr(fxy) == caseng.tostr(fyx):
        lines.append('d2z/dydx is the same, as it should')
        lines.append('be for a well-behaved f.')
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
                lines.append('(grad points the way z increases')
                lines.append(' fastest, and is perpendicular to')
                lines.append(' the contour through the point)')
    _pages('Partial derivatives', lines)


def t_surface_stat():
    # Stationary points of z = f(x, y): solve dz/dx = 0 and dz/dy = 0 together
    # by 2-D Newton from a starting guess, then classify with the discriminant
    # D = f_xx f_yy - f_xy^2. D < 0 is a saddle, which has no one-variable
    # analogue and is the case worth naming.
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
        _show('Stationary points', ['Cannot differentiate that.'])
        return
    x0 = _asknum('start searching near x = [0]')
    if x0 is None:
        x0 = 0.0
    y0 = _asknum('and y = [0]')
    if y0 is None:
        y0 = 0.0
    lines = ['z = ' + caseng.tostr(caseng.simplify(f)),
             'dz/dx = ' + caseng.tostr(cascalc.tidy(fx)),
             'dz/dy = ' + caseng.tostr(cascalc.tidy(fy)), '']
    # 2-D Newton on (fx, fy) = (0, 0)
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
        lines.append('No stationary point found from that')
        lines.append('starting guess. Try another - Newton')
        lines.append('finds the one it is nearest to.')
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
        lines.append('second derivatives undefined there.')
        _pages('Stationary points', lines)
        return
    D = A * C - B * B
    lines.append('')
    lines.append('fxx = ' + _fn(A) + '  fyy = ' + _fn(C) + '  fxy = ' + _fn(B))
    lines.append('D = fxx fyy - fxy^2 = ' + _fn(D))
    lines.append('')
    if D > 1e-12:
        if A > 0:
            lines.append('D > 0 and fxx > 0: MINIMUM')
        else:
            lines.append('D > 0 and fxx < 0: MAXIMUM')
    elif D < -1e-12:
        lines.append('D < 0: SADDLE POINT')
        lines.append('(a maximum along one direction and')
        lines.append(' a minimum along another - there is')
        lines.append(' no one-variable equivalent)')
    else:
        lines.append('D = 0: the test tells you nothing.')
        lines.append('Look at f along a few directions')
        lines.append('through the point.')
    _pages('Stationary points', lines)


def t_tangent_plane():
    # Tangent plane and normal line to z = f(x, y) at a point.
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
        _show('Tangent plane', ['Cannot differentiate that.'])
        return
    env = {'x': a, 'y': b}
    z0 = _at(f, env)
    p = _at(fx, env)
    q = _at(fy, env)
    if z0 is None or p is None or q is None:
        _show('Tangent plane', ['f or its derivatives are undefined',
                                'at that point.'])
        return
    lines = ['z = ' + caseng.tostr(caseng.simplify(f)),
             'at (' + _fn(a) + ', ' + _fn(b) + '), z = ' + _fn(z0), '',
             'fx = ' + caseng.tostr(cascalc.tidy(fx)) + '  ->  ' + _fn(p),
             'fy = ' + caseng.tostr(cascalc.tidy(fy)) + '  ->  ' + _fn(q), '',
             'TANGENT PLANE',
             '  z = ' + _fn(z0) + ' + ' + _fn(p) + '(x - ' + _fn(a) + ')',
             '           + ' + _fn(q) + '(y - ' + _fn(b) + ')',
             '  i.e. ' + _fn(p) + 'x + ' + _fn(q) + 'y - z = ' +
             _fn(p * a + q * b - z0), '',
             'NORMAL LINE',
             '  r = (' + _fn(a) + ', ' + _fn(b) + ', ' + _fn(z0) + ')',
             '      + t(' + _fn(p) + ', ' + _fn(q) + ', -1)', '',
             'grad f = (' + _fn(p) + ', ' + _fn(q) + ')',
             '(the surface normal is (fx, fy, -1);',
             ' grad f alone is the 2-D gradient of',
             ' the height, perpendicular to the',
             ' contour through the point)']
    _pages('Tangent plane', lines)


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _cubic_roots(a, b, c, d):
    # real roots of a x^3 + b x^2 + c x + d, by trigonometric/Cardano solution
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
    # three distinct real roots
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
    # a non-zero vector in the null space of the 3x3 matrix m, by elimination
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
    # scale so the largest component is 1, which is how they are written down
    big = 0
    k = 1
    while k < 3:
        if abs(v[k]) > abs(v[big]):
            big = k
        k += 1
    s = v[big]
    return [v[0] / s, v[1] / s, v[2] / s]


def t_eigen3():
    # 3x3 eigenvalues and eigenvectors. The specification asks for 3x3 work and
    # both eigen tools in this toolkit were 2x2 only.
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
    # sum of the 2x2 principal minors
    m2 = ((m[1][1] * m[2][2] - m[1][2] * m[2][1])
          + (m[0][0] * m[2][2] - m[0][2] * m[2][0])
          + (m[0][0] * m[1][1] - m[0][1] * m[1][0]))
    lines = ['M =']
    i = 0
    while i < 3:
        lines.append('  [ ' + _fn(m[i][0]) + '  ' + _fn(m[i][1]) + '  ' + _fn(m[i][2]) + ' ]')
        i += 1
    lines.append('')
    lines.append('trace = ' + _fn(tr) + ', det = ' + _fn(det))
    lines.append('characteristic equation:')
    lines.append('  k^3 - ' + _fn(tr) + 'k^2 + ' + _fn(m2) + 'k - ' + _fn(det) + ' = 0')
    roots = _cubic_roots(1.0, -tr, m2, -det)
    if not roots:
        lines.append('')
        lines.append('No real eigenvalue.')
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
            lines.append('    eigenvector not recoverable')
            vecs.append(None)
            continue
        vecs.append(v)
        lines.append('    eigenvector (' + _fn(v[0]) + ', ' + _fn(v[1]) +
                     ', ' + _fn(v[2]) + ')')
        # check Mv = kv, which is the definition and worth showing
        mv = [m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
              m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
              m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]]
        err = 0.0
        k = 0
        while k < 3:
            e = mv[k] - L * v[k]
            err += e if e >= 0 else -e
            k += 1
        lines.append('    check |Mv - kv| = ' + _fn(err, 6))
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
            lines.append('M^' + str(n) + ' = P D^' + str(n) + ' P-inverse, with')
            k = 0
            while k < 3:
                lines.append('  ' + _fn(roots[k]) + '^' + str(n) + ' = ' +
                             _fn(roots[k] ** n, 6))
                k += 1
    else:
        lines.append('Not three distinct real eigenvalues,')
        lines.append('so M may not be diagonalisable over')
        lines.append('the reals.')
    lines.append('')
    lines.append('CAYLEY-HAMILTON: M satisfies its own')
    lines.append('characteristic equation, so')
    lines.append('  M^3 = ' + _fn(tr) + 'M^2 - ' + _fn(m2) + 'M + ' + _fn(det) + 'I')
    lines.append('which is how to reduce any higher')
    lines.append('power by hand.')
    _pages('3x3 eigen', lines)


TOOLS = [
    ('Recurrence relation', t_recur),
    ('Group theory', t_group),
    ('2x2 Eigen/diag', t_eigen),
    ('Modular arithmetic', t_mod),
    ('Partial derivatives', t_partial),
    ('Surface stationary pts', t_surface_stat),
    ('Tangent plane / normal', t_tangent_plane),
    ('3x3 Eigen/diag', t_eigen3),
]

def run():
    casutil.run_tools('Extra Pure', TOOLS)
