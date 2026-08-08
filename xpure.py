import math
import casui
import caslex
import caseng
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
def t_partial():
    s = casui.input_expr('f in x (single var engine)')
    if s is None:
        return
    t = caslex.parse(s)
    if t is None:
        _show('Partial', ['Parse failed.'])
        return
    x0 = _asknum('evaluate d/dx at x =')
    if x0 is None:
        return
    h = 1e-5
    try:
        fp = caseng.evalf(t, x0 + h)
        fm = caseng.evalf(t, x0 - h)
        deriv = (fp - fm) / (2 * h)
    except:
        _show('Partial', ['Evaluation failed.'])
        return
    out = ['f = ' + caseng.tostr(t), 'NOTE: engine has 1 var x;', 'this is d/dx (central diff).',
           "f'(" + _fn(x0) + ') ~ ' + _fn(deriv), 'h=' + str(h)]
    _pages('Partial deriv', out)

TOOLS = [
    ('Recurrence relation', t_recur),
    ('Group theory', t_group),
    ('2x2 Eigen/diag', t_eigen),
    ('Modular arithmetic', t_mod),
    ('Partial deriv (num)', t_partial),
]

def run():
    casutil.run_tools('Extra Pure', TOOLS)
