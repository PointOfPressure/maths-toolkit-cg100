# OCR B (MEI) Further Maths H645, Extra Pure (Y435): recurrence relations,
# sets and groups, matrices (eigenvalues), multivariable calculus.
import math
import caseng
import cascalc
import caspoly
import casutil

_f = casutil.fmt
_w = casutil.w
_warn = casutil.warn
_fv = casutil.fmtv

# ---- small shared helpers ---------------------------------------------------

def _iv(v, name, lo, hi):
    # an integer field, checked
    if v is None:
        raise ValueError(name + ' missing')
    if isinstance(v, complex):
        raise ValueError(name + ' must be real')
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if v - n > 1e-9 or n - v > 1e-9:
        raise ValueError(name + ' must be a whole number')
    if n < lo or n > hi:
        raise ValueError(name + ' is ' + str(lo) + '..' + str(hi))
    return n

def _ts(t):
    try:
        return caseng.tostr(cascalc.tidy(t))
    except Exception:
        return caseng.tostr(t)

def _ev(tree, env):
    # real value of tree in the named variables, or None
    try:
        v = caseng.evalf(tree, 0.0, False, env)
    except Exception:
        return None
    if isinstance(v, complex):
        if abs(v.imag) > 1e-12 * (1.0 + abs(v.real)):
            return None
        v = v.real
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

def _only(tree, allowed, what):
    for v in caseng.vars_in(tree):
        if v not in allowed:
            raise ValueError(what + ' uses ' + v + '; only ' + ', '.join(allowed))

def _diff(tree, var):
    try:
        return caseng.simplify(caseng.diff(tree, var))
    except Exception:
        raise ValueError('cannot differentiate that')

def _snap(x):
    n = int(x + 0.5) if x >= 0 else -int(-x + 0.5)
    if abs(x - n) < 1e-11 * (1.0 + abs(x)):
        return float(n)
    return x

def _rat(x):
    # (p, q) with q <= 64 when x is that fraction, else None
    q = 1
    while q <= 64:
        t = x * q
        p = int(t + 0.5) if t >= 0 else -int(-t + 0.5)
        if abs(t - p) < 1e-9 * (1.0 + abs(t)):
            g = casutil.gcd(abs(p), q) if p else q
            return (p // g, q // g)
        q += 1
    return None

def _snapr(x):
    r = _rat(x)
    if r is None:
        return x
    return casutil.clean(r[0] * 1.0 / r[1])

def _sqf(disc):
    # disc rational > 0 -> (s, d, q): sqrt(disc) = s sqrt(d) / q, d squarefree
    r = _rat(disc)
    if r is None or r[0] <= 0:
        return None
    m = r[0] * r[1]
    if m > 100000000:
        return None
    s = 1
    k = 2
    while k * k <= m:
        while m % (k * k) == 0:
            m //= k * k
            s *= k
        k += 1
    return (s, m, r[1])

def _qlab(p, s, d):
    # exact label for p + s where s = k sqrt(d), p and k rational; None if not
    if d is None or d <= 1:
        return None
    rp = _rat(p)
    rk = _rat(s / math.sqrt(d))
    if rp is None or rk is None or rk[0] == 0:
        return None
    kn = abs(rk[0])
    sur = ('' if kn == 1 else str(kn)) + 'sqrt(' + str(d) + ')'
    if rk[1] != 1:
        sur += '/' + str(rk[1])
    neg = rk[0] < 0
    if rp[0] == 0:
        return ('-' if neg else '') + sur
    return _f(casutil.clean(rp[0] * 1.0 / rp[1])) + ('-' if neg else '+') + sur

def _lsolve(M, v):
    # Gauss-Jordan with partial pivoting; None if singular
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
            if r != c and A[r][c] != 0:
                fq = A[r][c]
                j = c
                while j <= n:
                    A[r][j] -= fq * A[c][j]
                    j += 1
            r += 1
        c += 1
    return [A[i][n] for i in range(n)]

def _plain(s):
    for ch in s:
        if ch not in '0123456789.':
            return False
    return True

def _coefstr(v, lab):
    s = lab if lab else _f(v)
    return s if _plain(s) else '(' + s + ')'

def _linstr(terms, const):
    # [(coef, 'x'), ...], const -> '2x + 4y - 3'
    out = ''
    for c, name in terms:
        c = casutil.clean(_snapr(c))
        if c == 0:
            continue
        neg = c < 0
        mag = -c if neg else c
        body = name if mag == 1 else _coefstr(mag, None) + name
        if out == '':
            out = ('-' if neg else '') + body
        else:
            out += (' - ' if neg else ' + ') + body
    const = casutil.clean(_snapr(const))
    if const != 0 or out == '':
        if out == '':
            out = _f(const)
        else:
            out += (' - ' if const < 0 else ' + ') + _f(abs(const))
    return out

# ============================================================================
# R  Recurrence relations
# ============================================================================
# s2 s3 s4 s5 s6 s7 s8 s9 (Xs1 modelling: no tool)

def _nv(tree, n):
    return _ev(tree, {'n': n})

def _n0(v):
    return 0 if v is None else _iv(v, 'n0', 0, 100)

def _flatsum(t):
    out = []
    st = [(t, 1)]
    while st:
        nd, s = st.pop()
        k = nd[0]
        if k == '+':
            st.append((nd[1], s))
            st.append((nd[2], s))
        elif k == '-':
            st.append((nd[1], s))
            st.append((nd[2], -s))
        elif k == 'neg':
            st.append((nd[1], -s))
        else:
            out.append(nd if s > 0 else ('neg', nd))
    return out

def _expnode(t):
    # first subtree k^(..n..) or exp(..n..), or None
    st = [t]
    while st:
        nd = st.pop()
        k = nd[0]
        if k == 'n' or k == 'v':
            continue
        if k == '^' and 'n' in caseng.vars_in(nd[2]) and \
                'n' not in caseng.vars_in(nd[1]):
            return nd
        if k == 'exp' and 'n' in caseng.vars_in(nd[1]):
            return nd
        i = 1
        while i < len(nd):
            if isinstance(nd[i], tuple):
                st.append(nd[i])
            i += 1
    return None

def _polydeg(vals):
    # degree of the polynomial through vals (equally spaced), -1 for all 0
    scale = 0.0
    for v in vals:
        if abs(v) > scale:
            scale = abs(v)
    cur = list(vals)
    k = 0
    while k < len(vals) - 2:
        allz = True
        for v in cur:
            if abs(v) > 1e-9 * (scale + 1.0) * (1 << k):
                allz = False
                break
        if allz:
            return k - 1
        cur = [cur[i] - cur[i - 1] for i in range(1, len(cur))]
        k += 1
    return None

def _form(term):
    # (b, d): term = (degree d polynomial in n) * b^n; None if not that shape
    node = _expnode(term)
    b = 1.0
    if node is not None:
        v0 = _nv(node, 0)
        v1 = _nv(node, 1)
        v2 = _nv(node, 2)
        if v0 is None or v1 is None or v2 is None or v0 == 0 or v1 == 0:
            return None
        b = v1 / v0
        if abs(v2 / v1 - b) > 1e-9 * (1.0 + abs(b)):
            return None
        b = _snapr(b)
    vals = []
    n = 0
    while n <= 9:
        v = _nv(term, n)
        if v is None:
            return None
        vals.append(v / (b ** n))
        n += 1
    d = _polydeg(vals)
    if d is None or d > 4:
        return None
    return (b, d)

def _groups(f):
    # f(n) as a sum of poly * b^n: [[b, d], ...]; None if not that shape
    gs = []
    for t in _flatsum(f):
        fb = _form(t)
        if fb is None:
            return None
        b, d = fb
        if d < 0:
            continue
        hit = False
        for g in gs:
            if abs(g[0] - b) < 1e-9 * (1.0 + abs(b)):
                if d > g[1]:
                    g[1] = d
                hit = True
        if not hit:
            gs.append([b, d])
    return gs

def _pv(kind, e, b, n):
    if kind == 'p':
        return (n ** e) * (b ** n)
    if kind == 'c':
        return (e ** n) * math.cos(n * b)
    return (e ** n) * math.sin(n * b)

def _lop(co, e, b, n):
    k = len(co)
    v = _pv('p', e, b, n + k)
    i = 0
    while i < k:
        v -= co[i] * _pv('p', e, b, n + i)
        i += 1
    return v

def _mult(co, b):
    # how many times b is a root of the auxiliary equation
    tol = 1e-9 * (1.0 + abs(b))
    if len(co) == 1:
        return 1 if abs(b - co[0]) < tol else 0
    p = b * b - co[1] * b - co[0]
    if abs(p) > tol * (1.0 + abs(b)):
        return 0
    return 2 if abs(2 * b - co[1]) < tol else 1

def _bstr(b, lab):
    s = lab if lab else _f(b)
    if not _plain(s):
        s = '(' + s + ')'
    return s + '^n'

def _trial(b, d, s):
    if d == 0:
        head = 'C'
    else:
        head = '(C0'
        j = 1
        while j <= d:
            head += '+C' + str(j) + ('n' if j == 1 else 'n^' + str(j))
            j += 1
        head += ')'
    if s == 1:
        head += '*n'
    elif s > 1:
        head += '*n^' + str(s)
    if abs(b - 1.0) > 1e-12:
        head += '*' + _bstr(b, None)
    return head

def _partic(co, f):
    # particular solution pieces for u(n+k) = sum co[i] u(n+i) + f(n)
    gs = _groups(f)
    if gs is None:
        return None
    basis = []
    notes = []
    for b, d in gs:
        s = _mult(co, b)
        notes.append('trial ' + _trial(b, d, s))
        if s:
            notes.append('(' + _f(b) + ' is an aux root: extra n' +
                         ('' if s == 1 else '^2') + ')')
        j = 0
        while j <= d:
            basis.append((s + j, b))
            j += 1
    if not basis:
        return [], notes
    m = len(basis)
    rows = []
    rhs = []
    n = 0
    while n < m:
        rows.append([_lop(co, e, b, n) for (e, b) in basis])
        v = _nv(f, n)
        if v is None:
            return None
        rhs.append(v)
        n += 1
    c = _lsolve(rows, rhs)
    if c is None:
        return None
    c = [_snapr(x) for x in c]
    n = 0
    while n < m + 6:
        got = 0.0
        i = 0
        while i < m:
            got += c[i] * _lop(co, basis[i][0], basis[i][1], n)
            i += 1
        want = _nv(f, n)
        if want is None or abs(got - want) > 1e-6 * (1.0 + abs(want)):
            return None
        n += 1
    pieces = []
    i = m - 1
    while i >= 0:
        if c[i] != 0:
            pieces.append((c[i], None, 'p', basis[i][0], basis[i][1], None))
        i -= 1
    return pieces, notes

def _pieceval(pieces, n):
    v = 0.0
    for c, cl, kind, e, b, bl in pieces:
        v += c * _pv(kind, e, b, n)
    return v

def _piecestr(pc):
    # -> (neg, body)
    c, cl, kind, e, b, bl = pc
    if cl is not None and cl[0] != '-':
        neg = False
        mag = c
    elif cl is not None:
        neg = True
        mag = -c
        cl = cl[1:]
    else:
        c = casutil.clean(c)
        neg = c < 0
        mag = -c if neg else c
    fs = []
    if kind == 'p':
        if e == 1:
            fs.append('n')
        elif e > 1:
            fs.append('n^' + str(e))
        if abs(b - 1.0) > 1e-12:
            fs.append(_bstr(b, bl))
    else:
        if abs(e - 1.0) > 1e-12:
            fs.append(_bstr(e, bl))
        fs.append(('cos' if kind == 'c' else 'sin') + '(n*' + _f(b) + ')')
    if not fs:
        return neg, (cl if cl else _f(mag))
    if abs(mag - 1.0) > 1e-12:
        fs.insert(0, _coefstr(mag, cl))
    return neg, '*'.join(fs)

def _wrap(head, pieces):
    parts = [_piecestr(p) for p in pieces if p[0] != 0]
    if not parts:
        return [head + '0']
    out = []
    cur = head
    first = True
    for neg, body in parts:
        if first:
            cur += ('-' if neg else '') + body
            first = False
            continue
        tok = (' - ' if neg else ' + ') + body
        if len(cur) + len(tok) > 35:
            out.append(cur)
            cur = '    ' + tok.strip()
        else:
            cur += tok
    out.append(cur)
    return out

def _iterate(co, f, init, n0, count):
    # terms u(n0), u(n0+1), ... from the recurrence; stops early if undefined
    k = len(co)
    u = list(init)
    n = n0
    while len(u) < count:
        fv = _nv(f, n)
        if fv is None:
            break
        v = fv
        i = 0
        while i < k:
            v += co[i] * u[len(u) - k + i]
            i += 1
        if v != v or abs(v) > 1e200:
            break
        u.append(v)
        n += 1
    return u

def _termline(u, n0, cnt):
    s = ''
    k = 0
    while k < len(u) and k < cnt:
        t = _f(u[k])
        if k and len(s) + len(t) > 36:
            break
        s += (', ' if k else '') + t
        k += 1
    return 'u(' + str(n0) + '..' + str(n0 + k - 1) + '): ' + s

def _check(pieces, u, n0, out):
    err = 0.0
    i = 0
    while i < len(u):
        cf = _pieceval(pieces, n0 + i)
        e = abs(cf - u[i]) / (1.0 + abs(u[i]))
        if e > err:
            err = e
        i += 1
    if err < 1e-6:
        out.append(_w('checked against the recurrence for ' +
                      str(len(u)) + ' terms'))
        return True
    out.append(_warn('closed form fails the check (' + casutil.sf3(err) + ')'))
    return False

def _fline(f):
    return _w('f(n) = ' + _ts(f))

def t_rec1h(a, u0):
    if a == 0 or u0 == 0:
        out = ['u(n) = 0 for n >= 1' if u0 != 0 else 'u(n) = 0 for all n']
    else:
        out = _wrap('u(n) = ', [(u0, None, 'p', 0, a, None)])
    if u0 == 0 or a == 0:
        pass
    elif a == 1:
        out.append('constant')
    elif a == -1:
        out.append('periodic, period 2')
    elif abs(a) < 1:
        out.append('convergent: u(n) -> 0')
        if a < 0:
            out.append('oscillating: signs alternate')
    elif a > 1:
        out.append('divergent: u(n) -> ' + ('inf' if u0 > 0 else '-inf'))
    else:
        out.append('divergent, oscillating')
    out.append(_w('each term is a times the one before,'))
    out.append(_w('so u(n) = u(0) a^n'))
    u = _iterate([a], ('n', 0), [u0], 0, 8)
    out.append(_w(_termline(u, 0, 8)))
    return out

def t_rec1(a, f, u0, n0):
    _only(f, ['n'], 'f(n)')
    n0 = _n0(n0)
    u = _iterate([a], f, [u0], n0, 11)
    if a == 0:
        out = ['u(n) = f(n-1) for n > ' + str(n0),
               _warn('a = 0: no complementary function'), _fline(f)]
        out.append(_w(_termline(u, n0, 8)))
        return out
    P = _partic([a], f)
    if P is None:
        out = [_warn('f(n) is not poly or k b^n: no'),
               _warn('standard trial; exact answer is'),
               'u(n) = a^(n-n0) u(n0)',
               '  + sum a^(n-1-k) f(k), k=n0..n-1',
               _fline(f), _w(_termline(u, n0, 8))]
        return out
    pieces, notes = P
    A = _snapr((u0 - _pieceval(pieces, n0)) / (a ** n0))
    full = [(A, None, 'p', 0, a, None)] + pieces
    out = _wrap('u(n) = ', full)
    out.append(_w('u(n+1) = ' + _linstr([(a, 'u(n)')], 0) + ' + f(n)'))
    out.append(_fline(f))
    out.append(_w('CF: A' + ('' if a == 1 else '*' + _bstr(a, None))))
    for nt in notes:
        out.append(_w(nt))
    for ln in _wrap('p(n) = ', pieces):
        out.append(_w(ln))
    out.append(_w('u(' + str(n0) + ') = ' + _f(u0) + ' gives A = ' + _f(A)))
    _check(full, u, n0, out)
    out.append(_w(_termline(u, n0, 8)))
    return out

def _aux(a, b):
    # roots of x^2 - a x - b = 0 -> (kind, data, lines)
    disc = a * a + 4.0 * b
    tol = 1e-12 * (1.0 + a * a + abs(b))
    q = _sqf(disc) if disc > 0 else None
    d = None if q is None else q[1]
    if disc > tol:
        s = math.sqrt(disc) / 2.0
        r1 = _snap(a / 2.0 + s)
        r2 = _snap(a / 2.0 - s)
        l1 = _qlab(a / 2.0, s, d)
        l2 = _qlab(a / 2.0, -s, d)
        return 'real', (r1, r2, l1, l2, d)
    if disc < -tol:
        R = math.sqrt(-b)
        th = math.atan2(math.sqrt(-disc) / 2.0, a / 2.0)
        return 'cx', (R, th)
    return 'rep', (a / 2.0,)

def _cf(kind, data, A, B, AL=None, BL=None):
    if kind == 'real':
        r1, r2, l1, l2, d = data
        return [(A, AL, 'p', 0, r1, l1), (B, BL, 'p', 0, r2, l2)]
    if kind == 'rep':
        return [(A, None, 'p', 0, data[0], None), (B, None, 'p', 1, data[0], None)]
    R, th = data
    return [(A, None, 'c', R, th, None), (B, None, 's', R, th, None)]

def _auxlines(a, b, kind, data, out):
    out.append(_w('aux: x^2 = ' + _linstr([(a, 'x')], b) + ', disc = ' +
                  _f(a * a + 4.0 * b)))
    if kind == 'real':
        r1, r2, l1, l2, d = data
        out.append(_w('roots ' + (l1 if l1 else _f(r1)) + ', ' +
                      (l2 if l2 else _f(r2))))
        out.append(_w('CF: A r1^n + B r2^n'))
    elif kind == 'rep':
        out.append(_w('repeated root ' + _f(data[0]) + ': CF (A + Bn)' +
                      _bstr(data[0], None)))
    else:
        R, th = data
        out.append(_w('complex roots, modulus ' + _f(R) + ', arg ' + _f(th)))
        out.append(_w('CF: R^n (A cos(n t) + B sin(n t))'))

def _fit2(kind, data, g0, g1, n0):
    cf = _cf(kind, data, 1.0, 0.0)
    M = [[_pv(cf[0][2], cf[0][3], cf[0][4], n0), _pv(cf[1][2], cf[1][3], cf[1][4], n0)],
         [_pv(cf[0][2], cf[0][3], cf[0][4], n0 + 1),
          _pv(cf[1][2], cf[1][3], cf[1][4], n0 + 1)]]
    AB = _lsolve(M, [g0, g1])
    if AB is None:
        return None
    A = _snapr(_snap(AB[0]))
    B = _snapr(_snap(AB[1]))
    AL = None
    BL = None
    if kind == 'real' and data[4] is not None and data[2] is not None:
        P = (A + B) / 2.0
        Q = (A - B) / 2.0
        AL = _qlab(P, Q, data[4])
        BL = _qlab(P, -Q, data[4])
        if AL is None or BL is None:
            AL = None
            BL = None
    return A, B, AL, BL

def _shape(kind, data, A, B, AL, BL, pieces):
    # the closed form by name, when written out it will not fit a line
    tail = ' + p(n)' if pieces else ''
    if kind == 'real':
        out = ['u(n) = A r1^n + B r2^n' + tail,
               'r1 = ' + (data[2] if data[2] else _f(data[0])),
               'r2 = ' + (data[3] if data[3] else _f(data[1]))]
    elif kind == 'rep':
        out = ['u(n) = (A + Bn) r^n' + tail, 'r = ' + _f(data[0])]
    else:
        out = ['u(n) = R^n(A cos nt + B sin nt)' + tail,
               'R = ' + _f(data[0]) + ', t = ' + _f(data[1])]
    out.append('A = ' + (AL if AL else _f(A)))
    out.append('B = ' + (BL if BL else _f(B)))
    if pieces:
        for ln in _wrap('p(n) = ', pieces):
            out.append(ln)
    return out

def _behav(kind, data, A, B):
    tiny = 1e-9
    if kind == 'cx':
        R, th = data
        if abs(A) < tiny and abs(B) < tiny:
            return ['u(n) = 0 for all n']
        if R < 1 - 1e-12:
            return ['convergent: u(n) -> 0', _w('oscillates (complex roots)')]
        if R > 1 + 1e-12:
            return ['divergent, oscillating']
        r = _rat(th / math.pi)
        if r is not None and r[0] != 0:
            per = r[1] * 2 // casutil.gcd(r[1] * 2, r[0] if r[0] > 0 else -r[0])
            return ['periodic, period ' + str(per)]
        return ['bounded, oscillating, not periodic']
    if kind == 'rep':
        r = data[0]
        if abs(A) < tiny and abs(B) < tiny:
            return ['u(n) = 0 for all n']
        if abs(r) < 1 - 1e-12:
            return ['convergent: u(n) -> 0']
        if abs(B) > tiny or abs(r) > 1 + 1e-12:
            return ['divergent' + (', oscillating' if r < 0 else '')]
        return ['constant' if r > 0 else 'periodic, period 2']
    r1, r2 = data[0], data[1]
    live = []
    if abs(A) > tiny:
        live.append((r1, A))
    if abs(B) > tiny:
        live.append((r2, B))
    if not live:
        return ['u(n) = 0 for all n']
    big = 0.0
    for r, c in live:
        if abs(r) > big:
            big = abs(r)
    if big < 1 - 1e-12:
        return ['convergent: u(n) -> 0']
    if big > 1 + 1e-12:
        neg = False
        for r, c in live:
            if abs(abs(r) - big) < 1e-12 and r < 0:
                neg = True
        return ['divergent' + (', oscillating' if neg else '')]
    lim = None
    per = False
    for r, c in live:
        if abs(r - 1) < 1e-12:
            lim = c
        elif abs(r + 1) < 1e-12:
            per = True
    if per:
        return ['bounded: tends to period 2']
    return ['convergent: u(n) -> ' + _f(lim)]

def _rec2(a, b, f, u0, u1, n0, hom):
    if b == 0:
        return [_warn('b = 0: this is first order in u(n+1)'),
                _w(_termline(_iterate([0.0, a], f, [u0, u1], n0, 8), n0, 8))]
    kind, data = _aux(a, b)
    co = [b, a]
    u = _iterate(co, f, [u0, u1], n0, 11)
    P = _partic(co, f)
    if P is None:
        out = [_warn('f(n) is not poly or k b^n:'),
               _warn('no standard trial solution')]
        _auxlines(a, b, kind, data, out)
        out.append(_w(_termline(u, n0, 8)))
        return out
    pieces, notes = P
    g0 = u0 - _pieceval(pieces, n0)
    g1 = u1 - _pieceval(pieces, n0 + 1)
    fit = _fit2(kind, data, g0, g1, n0)
    if fit is None:
        return [_warn('the two terms do not fix A and B')]
    A, B, AL, BL = fit
    full = _cf(kind, data, A, B, AL, BL) + pieces
    out = _wrap('u(n) = ', full)
    if max([len(ln) for ln in out]) > 35:
        out = _shape(kind, data, A, B, AL, BL, pieces)
    if hom:
        for ln in _behav(kind, data, A, B):
            out.append(ln)
    out.append(_w('u(n+2) = ' + _linstr([(a, 'u(n+1)'), (b, 'u(n)')], 0) +
                  ('' if hom else ' + f(n)')))
    if not hom:
        out.append(_fline(f))
    _auxlines(a, b, kind, data, out)
    for nt in notes:
        out.append(_w(nt))
    if pieces:
        for ln in _wrap('p(n) = ', pieces):
            out.append(_w(ln))
    out.append(_w('A = ' + (AL if AL else _f(A)) + ', B = ' + (BL if BL else _f(B))))
    _check(full, u, n0, out)
    out.append(_w(_termline(u, n0, 8)))
    return out

def t_rec2h(a, b, u0, u1):
    return _rec2(a, b, ('n', 0), u0, u1, 0, True)

def t_rec2(a, b, f, u0, u1, n0):
    _only(f, ['n'], 'f(n)')
    return _rec2(a, b, f, u0, u1, _n0(n0), False)

def _verify(F, cand, order):
    allowed = ['n', 'u'] if order == 1 else ['n', 'u', 'v']
    _only(F, allowed, 'F')
    _only(cand, ['n'], 'u(n)')
    out = []
    ok = True
    bad = None
    n = 0
    rows = []
    while n <= 12:
        c0 = _nv(cand, n)
        c1 = _nv(cand, n + 1)
        c2 = _nv(cand, n + 2) if order == 2 else 0.0
        if c0 is None or c1 is None or c2 is None:
            n += 1
            continue
        env = {'n': n, 'u': c0}
        if order == 2:
            env['v'] = c1
        rv = _ev(F, env)
        lv = c1 if order == 1 else c2
        if rv is None:
            n += 1
            continue
        if abs(lv - rv) > 1e-7 * (1.0 + abs(lv)):
            ok = False
            if bad is None:
                bad = (n, lv, rv)
        if len(rows) < 3:
            rows.append(_w('n=' + str(n) + ': LHS ' + _f(lv) + ', RHS ' + _f(rv)))
        n += 1
    if not rows:
        raise ValueError('u(n) or F undefined for n = 0..12')
    if ok:
        out.append('u(n) satisfies the recurrence')
    else:
        out.append('does NOT satisfy the recurrence')
        out.append('fails at n = ' + str(bad[0]) + ': ' + _f(bad[1]) +
                   ' vs ' + _f(bad[2]))
    init = [_nv(cand, 0), _nv(cand, 1)]
    if init[0] is not None and init[1] is not None:
        out.append('it gives u(0) = ' + _f(init[0]) +
                   (', u(1) = ' + _f(init[1]) if order == 2 else ''))
    try:
        np1 = ('+', ('v', 'n'), ('n', 1))
        left = caseng.subst(cand, 'n', np1 if order == 1 else
                            ('+', ('v', 'n'), ('n', 2)))
        right = caseng.subst(F, 'u', cand)
        if order == 2:
            right = caseng.subst(right, 'v', caseng.subst(cand, 'n', np1))
        if _ts(('-', caspoly.expand(left), caspoly.expand(right))) == '0':
            out.append(_w('LHS - RHS simplifies to 0 exactly'))
    except Exception:
        pass
    out.append(_w('LHS u(n+' + str(order) + ') from u(n); RHS is F with'))
    out.append(_w('u = u(n)' + (', v = u(n+1)' if order == 2 else '') +
                  ' substituted'))
    for r in rows:
        out.append(r)
    return out

def t_verify1(F, cand):
    return _verify(F, cand, 1)

def t_verify2(F, cand):
    return _verify(F, cand, 2)

def t_behave(F, u0):
    _only(F, ['n', 'u'], 'F')
    seq = [u0]
    broke = False
    diverged = False
    n = 0
    while n < 300:
        v = _ev(F, {'u': seq[n], 'n': n})
        if v is None:
            broke = True
            break
        seq.append(v)
        if abs(v) > 1e12:
            diverged = True
            break
        n += 1
    m = len(seq) - 1
    conv = False
    if not diverged and not broke:
        conv = True
        k = m - 5
        while k < m:
            if abs(seq[k + 1] - seq[k]) > 1e-9 * (1.0 + abs(seq[k])):
                conv = False
                break
            k += 1
    period = 0
    if not diverged and not broke and not conv:
        p = 2
        while p <= 12:
            good = True
            k = m - 3 * p
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
    out = []
    if broke:
        out.append(_warn('F undefined at u(' + str(m) + ')'))
    elif diverged:
        out.append('divergent: |u(n)| > 1e12 by n=' + str(m))
    elif conv:
        out.append('convergent: u(n) -> ' + _f(seq[m]))
    elif period:
        out.append('periodic, period ' + str(period))
        out.append('cycle ' + ', '.join([_f(seq[i]) for i in range(m - period + 1, m + 1)]))
    else:
        out.append('bounded, no limit or period seen')
        out.append(_w('over 300 terms (or converging slowly)'))
    if inc and not dec:
        out.append('increasing')
    elif dec and not inc:
        out.append('decreasing')
    elif osc and len(seq) > 3:
        out.append('oscillating (steps alternate sign)')
    if 'n' not in caseng.vars_in(F):
        try:
            roots = cascalc.solve(('-', F, ('v', 'u')), 'u')
        except Exception:
            roots = []
        dF = None
        try:
            dF = _diff(F, 'u')
        except ValueError:
            pass
        for r in roots[:4]:
            if dF is not None:
                k = 0
                while k < 30:
                    gv = _ev(F, {'u': r, 'n': 0})
                    dv = _ev(dF, {'u': r, 'n': 0})
                    if gv is None or dv is None or abs(dv - 1) < 1e-12:
                        break
                    step = (gv - r) / (dv - 1)
                    r -= step
                    if abs(step) < 1e-15 * (1 + abs(r)):
                        break
                    k += 1
            r = _snapr(_snap(r))
            if abs(r) < 1e-12:
                r = 0
            g = None if dF is None else _ev(dF, {'u': r, 'n': 0})
            tag = ''
            if g is not None:
                tag = ', attracting' if abs(g) < 1 - 1e-9 else \
                    (', repelling' if abs(g) > 1 + 1e-9 else ", |F'| = 1")
            out.append('fixed point ' + _f(r) + tag)
        if not roots:
            out.append(_w('no fixed point F(u) = u in -20..20'))
        out.append(_w('a limit L must satisfy L = F(L)'))
    out.append(_w(_termline(seq, 0, 8)))
    pts = [(float(i), seq[i]) for i in range(min(len(seq), 40))]
    import plot
    plot.run(pts, kind='points', title='u(n) against n')
    return out

def t_assoc(F, u0, g):
    _only(F, ['n', 'u'], 'F')
    _only(g, ['n', 'u'], 'g')
    u = u0
    ws = []
    n = 0
    while n <= 400:
        wv = _ev(g, {'n': n, 'u': u})
        ws.append(wv)
        v = _ev(F, {'n': n, 'u': u})
        if v is None or abs(v) > 1e150:
            break
        u = v
        n += 1
    good = [(i, ws[i]) for i in range(len(ws)) if ws[i] is not None]
    if not good:
        raise ValueError('w(n) = g(n, u(n)) never defined')
    out = []
    last = good[len(good) - 1]
    if len(good) > 20:
        a = good[len(good) - 2][1]
        b = last[1]
        if abs(b - a) < 1e-6 * (1.0 + abs(b)):
            out.append('w(n) -> ' + _f(b))
        elif abs(b) > 1e9:
            out.append('w(n) diverges')
        else:
            out.append('w(n) does not settle by n = ' + str(last[0]))
    else:
        out.append(_warn('u(n) left the range by n = ' + str(len(ws))))
    out.append(_w('w(n) = g(n, u(n)), u(n+1) = F(n, u(n))'))
    for i, v in good[:6]:
        out.append(_w('w(' + str(i) + ') = ' + _f(v)))
    for i, v in good:
        if i in (10, 100) or (i, v) == last:
            out.append('w(' + str(i) + ') = ' + _f(v))
    return out

def t_ratio(a, b, u0, u1):
    if b == 0:
        raise ValueError('b = 0: not second order')
    u = _iterate([b, a], ('n', 0), [u0, u1], 0, 61)
    out = []
    kind, data = _aux(a, b)
    rs = []
    i = 0
    while i + 1 < len(u) and i < 60:
        if u[i] != 0:
            rs.append((i, u[i + 1] / u[i]))
        i += 1
    if not rs:
        raise ValueError('all terms are 0')
    fit = _fit2(kind, data, u0, u1, 0)
    if kind == 'real' and fit is not None:
        r1, r2, l1, l2, d = data
        A, B = fit[0], fit[1]
        big = max(abs(A), abs(B))
        cands = []
        if abs(A) > 1e-9 * big:
            cands.append((r1, l1))
        if abs(B) > 1e-9 * big:
            cands.append((r2, l2))
        cands.sort(key=lambda t: -abs(t[0]))
        if not cands:
            out.append('no limit found')
        elif len(cands) == 2 and abs(abs(cands[0][0]) - abs(cands[1][0])) < 1e-12:
            out.append('no limit: roots of equal size')
        else:
            r, lab = cands[0]
            out.append('u(n+1)/u(n) -> ' + (lab if lab else _f(r)))
            out.append(_w('the root of larger modulus dominates'))
    elif kind == 'rep':
        out.append('u(n+1)/u(n) -> ' + _f(data[0]))
        out.append(_w('(A + Bn) r^n: ratio -> r, slowly'))
    else:
        out.append('no limit: the ratio oscillates')
        out.append(_w('complex roots: R^n cos(n t + c)'))
    _auxlines(a, b, kind, data, out)
    for i, r in rs[:6]:
        out.append(_w('u(' + str(i + 1) + ')/u(' + str(i) + ') = ' + _f(r)))
    li, lr = rs[len(rs) - 1]
    out.append(_w('u(' + str(li + 1) + ')/u(' + str(li) + ') = ' + _f(lr)))
    return out

# ============================================================================
# G  Sets and groups
# ============================================================================
# XS1 (sets), Xa1 a2 a3 a4 a5 a6 a7 a8 (S2 number sets: notation only)

def _setnorm(v):
    out = []
    for x in v:
        x = casutil.clean(x)
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
    return _setnorm(list(a) + list(b))

def _sinter(a, b):
    return [x for x in a if _inset(x, b)]

def _sdiff(a, b):
    return [x for x in a if not _inset(x, b)]

def _ssub(a, b):
    for x in a:
        if not _inset(x, b):
            return False
    return True

def _sstr(s):
    if not s:
        return '{ }'
    return '{' + ', '.join([_f(x) for x in s]) + '}'

def t_sets(nA, nB, elems):
    na = _iv(nA, 'nA', 0, 60)
    nb = _iv(nB, 'nB', 0, 60)
    if len(elems) < na + nb:
        raise ValueError('need nA + nB = ' + str(na + nb) + ' elements')
    A = _setnorm(elems[:na])
    B = _setnorm(elems[na:na + nb])
    E = _setnorm(elems[na + nb:])
    out = []
    if not E:
        E = _sunion(A, B)
        out.append(_warn('no E given: E = A u B'))
    elif not (_ssub(A, E) and _ssub(B, E)):
        E = _sunion(E, _sunion(A, B))
        out.append(_warn('E did not contain A and B: enlarged'))
    un = _sunion(A, B)
    it = _sinter(A, B)
    out.append('A u B = ' + _sstr(un))
    out.append('A n B = ' + _sstr(it))
    out.append("A' = " + _sstr(_sdiff(E, A)))
    out.append("B' = " + _sstr(_sdiff(E, B)))
    out.append('A \\ B = ' + _sstr(_sdiff(A, B)))
    out.append('B \\ A = ' + _sstr(_sdiff(B, A)))
    out.append('A c B: ' + ('yes' if _ssub(A, B) else 'no') +
               ',  B c A: ' + ('yes' if _ssub(B, A) else 'no'))
    out.append('disjoint: ' + ('yes' if not it else 'no'))
    out.append('|A u B| = ' + str(len(un)) + ', |A n B| = ' + str(len(it)))
    out.append(_w('E = ' + _sstr(E) + ', |E| = ' + str(len(E))))
    out.append(_w('A = ' + _sstr(A) + ', |A| = ' + str(len(A))))
    out.append(_w('B = ' + _sstr(B) + ', |B| = ' + str(len(B))))
    out.append(_w('|A|+|B|-|A n B| = ' + str(len(A) + len(B) - len(it)) +
                  ' = |A u B|'))
    dm = _sinter(_sdiff(E, A), _sdiff(E, B))
    out.append(_w("(A u B)' = A' n B' = " + _sstr(dm)))
    out.append(_w('u union, n intersection, \' complement,'))
    out.append(_w('\\ difference, c subset, { } empty set'))
    return out

def t_subsets(elems):
    S = _setnorm(elems)
    k = len(S)
    if k > 5:
        raise ValueError('at most 5 elements (2^5 subsets)')
    out = ['|P(S)| = 2^' + str(k) + ' = ' + str(1 << k)]
    out.append('proper subsets: ' + str((1 << k) - 1))
    size = 0
    while size <= k:
        row = []
        mask = 0
        while mask < (1 << k):
            c = 0
            sub = []
            i = 0
            while i < k:
                if mask & (1 << i):
                    c += 1
                    sub.append(S[i])
                i += 1
            if c == size:
                row.append(_sstr(sub))
            mask += 1
        out.append(_w('size ' + str(size) + ' (' + str(len(row)) + '): ' + ' '.join(row)))
        size += 1
    return out

# ---- group tables: n, then the n*n entries row by row. The elements are the
# n distinct entries in increasing order (so 0..n-1 as indices, or labels
# such as 1,3,5,7); row i and column i belong to the i-th smallest.

def _gread(n, vals, name):
    n = _iv(n, 'n', 1, 10)
    if len(vals) != n * n:
        raise ValueError(name + ' needs n*n = ' + str(n * n) + ' entries')
    ints = [_iv(v, 'entry', -99999, 99999) for v in vals]
    labs = []
    for v in ints:
        if v not in labs:
            labs.append(v)
    labs.sort()
    if len(labs) != n:
        return n, labs, None
    idx = {}
    i = 0
    while i < n:
        idx[labs[i]] = i
        i += 1
    T = [[idx[ints[i * n + j]] for j in range(n)] for i in range(n)]
    return n, labs, T

def _gcheck(T, labs):
    # -> (identity, inverses, None) or (.., .., reason it is not a group)
    n = len(T)
    L = lambda i: str(labs[i])
    e = -1
    a = 0
    while a < n and e < 0:
        ok = True
        x = 0
        while x < n:
            if T[a][x] != x or T[x][a] != x:
                ok = False
                break
            x += 1
        if ok:
            e = a
        a += 1
    if e < 0:
        return -1, None, 'no identity element'
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
        if found < 0:
            return e, None, L(a) + ' has no inverse'
        inv.append(found)
        a += 1
    a = 0
    while a < n:
        b = 0
        while b < n:
            ab = T[a][b]
            c = 0
            while c < n:
                if T[ab][c] != T[a][T[b][c]]:
                    return e, inv, 'not associative: (' + L(a) + '*' + L(b) + \
                        ')*' + L(c) + ' != ' + L(a) + '*(' + L(b) + '*' + L(c) + ')'
                c += 1
            b += 1
        a += 1
    return e, inv, None

def _notgroup(n, labs, what):
    if len(labs) > n:
        return [what + ' is not closed', _w(str(len(labs)) + ' different entries for ' +
                                           str(n) + ' elements')]
    return [what + ' is not a group',
            _w('only ' + str(len(labs)) + ' distinct entries: a group row')
            , _w('holds every element exactly once')]

def _group(n, vals, name):
    n, labs, T = _gread(n, vals, name)
    if T is None:
        raise ValueError(_notgroup(n, labs, name)[0])
    e, inv, err = _gcheck(T, labs)
    if err:
        raise ValueError(name + ': ' + err)
    return labs, T, e, inv

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

def _isab(T):
    n = len(T)
    for i in range(n):
        for j in range(n):
            if T[i][j] != T[j][i]:
                return False
    return True

def t_gaxioms(n, table):
    n, labs, T = _gread(n, table, 'G')
    if T is None:
        return _notgroup(n, labs, 'G')
    e, inv, err = _gcheck(T, labs)
    L = lambda i: str(labs[i])
    out = []
    if err:
        out.append('not a group')
        out.append(err)
        out.append(_w('closure: yes (n entries)'))
        if e >= 0:
            out.append(_w('identity e = ' + L(e)))
        return out
    od = _orders(T, e)
    out.append('G is a group of order ' + str(n))
    out.append('identity e = ' + L(e))
    out.append('abelian: ' + ('yes' if _isab(T) else 'no'))
    gens = [L(a) for a in range(n) if od[a] == n]
    out.append('cyclic: ' + ('yes, <' + gens[0] + '>' if gens else 'no'))
    out.append(_w('closure: every entry is in G'))
    out.append(_w('associativity checked for all ' + str(n ** 3) + ' triples'))
    s = ''
    for a in range(n):
        s += ('' if a == 0 else ', ') + L(a) + '^-1=' + L(inv[a])
        if len(s) > 40 or a == n - 1:
            out.append(_w(s))
            s = ''
    out.append(_w('elements: ' + ' '.join([L(a) for a in range(n)])))
    return out

def t_gorders(n, table):
    labs, T, e, inv = _group(n, table, 'G')
    n = len(T)
    od = _orders(T, e)
    out = []
    for a in range(n):
        out.append('ord(' + str(labs[a]) + ') = ' + str(od[a]))
    gens = [str(labs[a]) for a in range(n) if od[a] == n]
    if gens:
        out.append('cyclic, generators ' + ', '.join(gens))
    else:
        out.append('not cyclic: no element of order ' + str(n))
    divs = [str(d) for d in range(1, n + 1) if n % d == 0]
    out.append(_w('Lagrange: each order divides |G| = ' + str(n)))
    out.append(_w('divisors of ' + str(n) + ': ' + ' '.join(divs)))
    return out

def _close(T, mask):
    n = len(T)
    mem = [i for i in range(n) if (mask >> i) & 1]
    k = 0
    while k < len(mem):
        a = mem[k]
        for b in list(mem):
            for c in (T[a][b], T[b][a]):
                if not (mask >> c) & 1:
                    mask |= 1 << c
                    mem.append(c)
        k += 1
    return mask

def _subgroups(T):
    n = len(T)
    subs = []
    for a in range(n):
        m = _close(T, 1 << a)
        if m not in subs:
            subs.append(m)
    i = 0
    while i < len(subs):
        j = 0
        while j < i:
            m = _close(T, subs[i] | subs[j])
            if m not in subs:
                subs.append(m)
            j += 1
        i += 1
    items = [([k for k in range(n) if (m >> k) & 1]) for m in subs]
    items.sort(key=lambda h: (len(h), h))
    return items

def t_subgroups(n, table):
    labs, T, e, inv = _group(n, table, 'G')
    n = len(T)
    subs = _subgroups(T)
    out = [str(len(subs)) + ' subgroups of G (order ' + str(n) + ')']
    for H in subs:
        k = len(H)
        tag = ' trivial' if k == 1 else (' G' if k == n else '')
        out.append('{' + ','.join([str(labs[h]) for h in H]) + '} order ' +
                   str(k) + tag)
    sizes = []
    for H in subs:
        if len(H) not in sizes:
            sizes.append(len(H))
    out.append(_w('Lagrange: |H| divides |G|; orders seen'))
    out.append(_w(' '.join([str(s) for s in sizes]) + ', index [G:H] = ' +
                  ' '.join([str(n // s) for s in sizes])))
    miss = [str(d) for d in range(1, n + 1) if n % d == 0 and d not in sizes]
    if miss:
        out.append(_w('divisors with no subgroup: ' + ' '.join(miss)))
        out.append(_w('(the converse of Lagrange is false)'))
    cyc = []
    for a in range(n):
        m = _close(T, 1 << a)
        if len([k for k in range(n) if (m >> k) & 1]) == n:
            cyc.append(str(labs[a]))
    out.append(_w('<a> = G for a = ' + (' '.join(cyc) if cyc else 'none')))
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

def _iso(G, eg, H, eh):
    # an isomorphism G -> H as a list, or None
    n = len(G)
    og = _orders(G, eg)
    oh = _orders(H, eh)
    if sorted(og) != sorted(oh):
        return None
    phi = [-1] * n
    used = [False] * n
    phi[eg] = eh
    used[eh] = True
    todo = [a for a in range(n) if a != eg]
    cand = [0] * len(todo)
    depth = 0
    while 0 <= depth < len(todo):
        g = todo[depth]
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
            if depth < len(todo):
                cand[depth] = 0
        else:
            cand[depth] = 0
            depth -= 1
    if depth < 0:
        return None
    return phi

def _maplines(phi, gname, hname):
    out = []
    s = ''
    i = 0
    while i < len(phi):
        piece = gname(i) + '->' + hname(phi[i])
        if s and len(s) + len(piece) > 32:
            out.append(s)
            s = ''
        s += ('' if s == '' else ', ') + piece
        i += 1
    if s:
        out.append(s)
    return out

def t_giso(n, tables):
    n = _iv(n, 'n', 1, 10)
    if len(tables) != 2 * n * n:
        raise ValueError('need 2n^2 = ' + str(2 * n * n) + ' entries (G then H)')
    gl, G, eg, ig = _group(n, tables[:n * n], 'G')
    hl, H, eh, ih = _group(n, tables[n * n:], 'H')
    og = _orders(G, eg)
    oh = _orders(H, eh)
    out = []
    phi = _iso(G, eg, H, eh)
    if phi is None:
        out.append('G and H are NOT isomorphic')
        if sorted(og) != sorted(oh):
            out.append(_w('their element orders differ'))
        else:
            out.append(_w('no order-preserving map works'))
    else:
        out.append('G and H are isomorphic')
        out.append('phi:')
        for ln in _maplines(phi, lambda i: str(gl[i]), lambda i: str(hl[i])):
            out.append(ln)
        out.append(_w('phi(ab) = phi(a)phi(b) for all ' + str(n * n) + ' pairs'))
    out.append(_w('orders in G: ' + ' '.join([str(v) for v in sorted(og)])))
    out.append(_w('orders in H: ' + ' '.join([str(v) for v in sorted(oh)])))
    return out

# ---- standard groups, as index tables with element names

def _cyc(n):
    return [[(i + j) % n for j in range(n)] for i in range(n)]

def _cycname(i):
    return 'e' if i == 0 else ('g' if i == 1 else 'g^' + str(i))

def _dih(m):
    # D_m, order 2m: index k + m f is r^k s^f, with s r = r^-1 s
    T = []
    for i in range(2 * m):
        k1 = i % m
        f1 = i // m
        row = []
        for j in range(2 * m):
            k2 = j % m
            f2 = j // m
            k = (k1 + (k2 if f1 == 0 else -k2)) % m
            row.append(k + m * ((f1 + f2) % 2))
        T.append(row)
    return T

def _dihname(m):
    def nm(i):
        k = i % m
        r = '' if k == 0 else ('r' if k == 1 else 'r^' + str(k))
        if i >= m:
            return (r + ' s') if r else 's'
        return r if r else 'e'
    return nm

def _prod(A, B):
    na = len(A)
    nb = len(B)
    return [[A[i // nb][j // nb] * nb + B[i % nb][j % nb] for j in range(na * nb)]
            for i in range(na * nb)]

def _prodname(nb):
    return lambda i: '(' + str(i // nb) + ',' + str(i % nb) + ')'

def _q8():
    # 0..3 = 1 i j k, 4..7 = -1 -i -j -k
    U = [[(0, 0), (0, 1), (0, 2), (0, 3)],
         [(0, 1), (1, 0), (0, 3), (1, 2)],
         [(0, 2), (1, 3), (1, 0), (0, 1)],
         [(0, 3), (0, 2), (1, 1), (1, 0)]]
    T = []
    for a in range(8):
        row = []
        for b in range(8):
            s, u = U[a % 4][b % 4]
            s = (s + a // 4 + b // 4) % 2
            row.append(u + 4 * s)
        T.append(row)
    return T

def _q8name(i):
    return ('-' if i >= 4 else '') + ['1', 'i', 'j', 'k'][i % 4]

def _standard(n):
    # every group of order n <= 10, up to isomorphism
    out = [('C' + str(n) + ' (cyclic)', _cyc(n), _cycname)]
    if n == 4:
        out.append(('V4 = C2 x C2 (Klein)', _prod(_cyc(2), _cyc(2)), _prodname(2)))
    elif n == 6:
        out.append(('D3 = S3 (triangle)', _dih(3), _dihname(3)))
    elif n == 8:
        out.append(('C4 x C2', _prod(_cyc(4), _cyc(2)), _prodname(2)))
        out.append(('C2 x C2 x C2', _prod(_prod(_cyc(2), _cyc(2)), _cyc(2)),
                    lambda i: '(' + str(i // 4) + ',' + str((i // 2) % 2) + ',' +
                    str(i % 2) + ')'))
        out.append(('D4 (square)', _dih(4), _dihname(4)))
        out.append(('Q8 (quaternion)', _q8(), _q8name))
    elif n == 9:
        out.append(('C3 x C3', _prod(_cyc(3), _cyc(3)), _prodname(3)))
    elif n == 10:
        out.append(('D5 (pentagon)', _dih(5), _dihname(5)))
    return out

def t_gident(n, table):
    labs, T, e, inv = _group(n, table, 'G')
    n = len(T)
    for name, S, nm in _standard(n):
        phi = _iso(T, e, S, 0)
        if phi is not None:
            out = ['isomorphic to ' + name]
            for ln in _maplines(phi, lambda i: str(labs[i]), nm):
                out.append(ln)
            out.append(_w('order ' + str(n) + ' has ' + str(len(_standard(n))) +
                          ' groups up to isomorphism'))
            return out
    return [_warn('no match found')]

def _rows(T, labs, out):
    out.append(_w('table code: ' + str(len(T)) + ', then the rows'))
    for i in range(len(T)):
        out.append(_w(' '.join([str(labs[v]) for v in T[i]])))

def t_zadd(n):
    n = _iv(n, 'n', 1, 12)
    out = ['Z' + str(n) + ' under + mod ' + str(n) + ': cyclic']
    gens = [str(k) for k in range(n) if casutil.gcd(k, n) == 1 or n == 1]
    out.append('generators: ' + ', '.join(gens))
    s = ''
    for k in range(n):
        piece = 'ord(' + str(k) + ')=' + str(n // casutil.gcd(k, n) if k else 1)
        if s and len(s) + len(piece) > 33:
            out.append(s)
            s = ''
        s += ('' if s == '' else ' ') + piece
    out.append(s)
    out.append(_w('identity 0, inverse of k is n - k'))
    out.append(_w('ord(k) = n / gcd(k, n)'))
    _rows(_cyc(n), list(range(n)), out)
    return out

def t_zmul(n):
    n = _iv(n, 'n', 2, 30)
    U = [k for k in range(1, n) if casutil.gcd(k, n) == 1]
    m = len(U)
    T = [[U.index((a * b) % n) for b in U] for a in U]
    od = _orders(T, 0)
    out = ['units mod ' + str(n) + ': order ' + str(m)]
    s = '{'
    for k in U:
        s += ('' if s == '{' else ',') + str(k)
    out.append(s + '}')
    gens = [str(U[i]) for i in range(m) if od[i] == m]
    out.append('cyclic, generators ' + ', '.join(gens) if gens else 'not cyclic')
    s = ''
    for i in range(m):
        piece = 'ord(' + str(U[i]) + ')=' + str(od[i])
        if s and len(s) + len(piece) > 33:
            out.append(s)
            s = ''
        s += ('' if s == '' else ' ') + piece
    out.append(s)
    if m < n - 1:
        bad = [k for k in range(1, n) if k not in U]
        out.append(_w('{1..' + str(n - 1) + '} is not a group: ' + str(bad[0]) +
                      ' has no inverse'))
    if m <= 10:
        _rows(T, U, out)
    return out

def t_dihedral(m):
    m = _iv(m, 'n', 3, 6)
    T = _dih(m)
    nm = _dihname(m)
    od = _orders(T, 0)
    out = ['D' + str(m) + ': order ' + str(2 * m) + ', not abelian']
    for i in range(2 * m):
        k = i % m
        if i == 0:
            what = 'identity'
        elif i < m:
            what = 'rotate ' + _f(360.0 * k / m) + ' deg'
        else:
            what = 'reflect in ' + _f(180.0 * k / m) + ' deg line'
        out.append(str(i) + ' = ' + nm(i) + ': ' + what)
    out.append('orders: ' + ' '.join([str(v) for v in od]))
    out.append(_w('r = rotation by 360/' + str(m) + ', s = reflection'))
    out.append(_w('in the x-axis; lines at angles from it'))
    out.append(_w('s r = r^-1 s; r^k s means s first, then r^k'))
    _rows(T, list(range(2 * m)), out)
    return out

# ============================================================================
# M  Matrices: eigenvalues and eigenvectors
# ============================================================================
# Xm1 m2 m3 m4 m5 m6

def _mm(A, B):
    return [[casutil.clean(_snap(sum([A[i][k] * B[k][j] for k in range(len(B))])))
             for j in range(len(B[0]))] for i in range(len(A))]

def _ident(n):
    return [[1 if j == i else 0 for j in range(n)] for i in range(n)]

def _mpow(A, n):
    r = _ident(len(A))
    i = 0
    while i < n:
        r = _mm(r, A)
        i += 1
    return r

def _det2(A):
    return casutil.clean(A[0][0] * A[1][1] - A[0][1] * A[1][0])

def _det3(A):
    return casutil.clean(
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))

def _inv(A):
    n = len(A)
    if n == 2:
        d = _det2(A)
        if abs(d) < 1e-12:
            return None
        return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]
    d = _det3(A)
    if abs(d) < 1e-12:
        return None
    co = []
    for i in range(3):
        row = []
        for j in range(3):
            r = [k for k in range(3) if k != i]
            c = [k for k in range(3) if k != j]
            mn = A[r[0]][c[0]] * A[r[1]][c[1]] - A[r[0]][c[1]] * A[r[1]][c[0]]
            row.append(mn if (i + j) % 2 == 0 else -mn)
        co.append(row)
    return [[casutil.clean(_snapr(co[j][i] / d)) for j in range(3)] for i in range(3)]

def _mlines(name, A):
    rows = casutil.fmtm([[casutil.clean(_snapr(v)) for v in r] for r in A])
    return [(name + ' = ' if i == 0 else ' ' * (len(name) + 3)) + rows[i]
            for i in range(len(rows))]

def _scale(v):
    # tidiest equivalent direction: small integers if possible
    best = None
    k = 1
    while k <= 24:
        ok = True
        for c in v:
            t = c * k
            n = int(t + 0.5) if t >= 0 else -int(-t + 0.5)
            if abs(t - n) > 1e-9:
                ok = False
                break
        if ok:
            best = k
            break
        k += 1
    if best is None:
        big = 0.0
        for c in v:
            if abs(c) > abs(big):
                big = c
        return [casutil.clean(c / big) for c in v]
    out = []
    for c in v:
        t = c * best
        out.append(int(t + 0.5) if t >= 0 else -int(-t + 0.5))
    g = 0
    for c in out:
        g = casutil.gcd(g, int(abs(c)))
    if g > 1:
        out = [c // g for c in out]
    for c in out:
        if c != 0:
            if c < 0:
                out = [-x for x in out]
            break
    return out

def _tol(M):
    big = 1.0
    for r in M:
        for v in r:
            if abs(v) > big:
                big = abs(v)
    return big * 1e-9

def _rref(M):
    n = len(M)
    a = [list(r) for r in M]
    tol = _tol(M)
    piv = []
    row = 0
    col = 0
    while row < n and col < n:
        best = row
        for r in range(row, n):
            if abs(a[r][col]) > abs(a[best][col]):
                best = r
        if abs(a[best][col]) <= tol:
            col += 1
            continue
        a[row], a[best] = a[best], a[row]
        d = a[row][col]
        for j in range(n):
            a[row][j] /= d
        for r in range(n):
            if r != row and abs(a[r][col]) > 1e-14:
                fc = a[r][col]
                for j in range(n):
                    a[r][j] -= fc * a[row][j]
        piv.append(col)
        row += 1
        col += 1
    return a, piv

def _nullvec(M):
    n = len(M)
    a, piv = _rref(M)
    free = [c for c in range(n) if c not in piv]
    if not free:
        return None
    fc = free[0]
    v = [0.0] * n
    v[fc] = 1.0
    for i in range(len(piv)):
        v[piv[i]] = -a[i][fc]
    return _scale(v)

def _nullbasis(M):
    n = len(M)
    a, piv = _rref(M)
    out = []
    for fc in [c for c in range(n) if c not in piv]:
        v = [0.0] * n
        v[fc] = 1.0
        for i in range(len(piv)):
            v[piv[i]] = -a[i][fc]
        out.append(_scale(v))
    return out

def _nullity(M):
    return len(M) - len(_rref(M)[1])

def _eqstr(co, var):
    out = ''
    n = len(co) - 1
    for i in range(n + 1):
        c = casutil.clean(co[i])
        p = n - i
        if c != 0:
            neg = c < 0
            mag = -c if neg else c
            s = _f(mag)
            if p == 0:
                piece = s
            else:
                pw = var if p == 1 else var + '^' + str(p)
                piece = pw if mag == 1 else s + pw
            if out == '':
                out = ('-' if neg else '') + piece
            else:
                out += ('-' if neg else '+') + piece
    return out if out else '0'

def _cubic(co):
    # real roots of a cubic, co high->low; rational roots exactly
    rp = []
    ok = True
    for i in range(len(co) - 1, -1, -1):
        c = co[i]
        if abs(c) > 1e9 or c != int(c):
            ok = False
            break
        rp.append((int(c), 1))
    out = []
    rest = [float(c) for c in co]
    if ok:
        p = caspoly.ptrim(rp)
        for r in caspoly.roots_rational(p):
            qr = caspoly.pdivmod(p, [caspoly.rneg(r), caspoly.R1])
            if qr is None or qr[1]:
                continue
            p = qr[0]
            out.append(casutil.clean(r[0] * 1.0 / r[1]))
            while True:
                qr = caspoly.pdivmod(p, [caspoly.rneg(r), caspoly.R1])
                if qr is None or qr[1] or len(p) < 2:
                    break
                p = qr[0]
                out.append(casutil.clean(r[0] * 1.0 / r[1]))
        rest = [p[i][0] * 1.0 / p[i][1] for i in range(len(p) - 1, -1, -1)]
    while len(rest) > 1 and rest[0] == 0:
        rest = rest[1:]
    if len(rest) == 2:
        out.append(_snap(-rest[1] / rest[0]))
    elif len(rest) == 3:
        a, b, c = rest
        d = b * b - 4 * a * c
        if d >= -1e-12:
            s = math.sqrt(d if d > 0 else 0.0)
            out.append(_snap((-b + s) / (2 * a)))
            out.append(_snap((-b - s) / (2 * a)))
    elif len(rest) == 4:
        a, b, c, d = rest
        b /= a
        c /= a
        d /= a
        p = c - b * b / 3.0
        q = 2.0 * b * b * b / 27.0 - b * c / 3.0 + d
        off = -b / 3.0
        disc = q * q / 4.0 + p * p * p / 27.0
        if disc > 1e-14:
            s = math.sqrt(disc)
            u = -q / 2.0 + s
            v = -q / 2.0 - s
            cu = u ** (1.0 / 3.0) if u >= 0 else -((-u) ** (1.0 / 3.0))
            cv = v ** (1.0 / 3.0) if v >= 0 else -((-v) ** (1.0 / 3.0))
            out.append(_snap(cu + cv + off))
        elif abs(p) < 1e-12:
            out.append(_snap(off))
        else:
            r = math.sqrt(-p * p * p / 27.0)
            ph = math.acos(max(-1.0, min(1.0, -q / (2.0 * r))))
            mg = 2.0 * math.sqrt(-p / 3.0)
            for k in range(3):
                out.append(_snap(mg * math.cos((ph + 2.0 * math.pi * k) / 3.0) + off))
    out = [casutil.clean(x) for x in out]
    out.sort()
    return out

def _eig2(A):
    a, b, c, d = A[0][0], A[0][1], A[1][0], A[1][1]
    tr = a + d
    det = _det2(A)
    disc = tr * tr - 4.0 * det
    return tr, det, disc

def _vec2(A, L):
    p = A[0][0] - L
    q = A[0][1]
    if abs(p) < 1e-9 and abs(q) < 1e-9:
        p = A[1][0]
        q = A[1][1] - L
    if abs(q) > 1e-9:
        return _scale([1.0, -p / q])
    if abs(p) > 1e-9:
        return _scale([-q / p, 1.0])
    return [1, 0]

def _vals2(A):
    # real eigenvalues with exact labels -> [(L, label)]
    tr, det, disc = _eig2(A)
    if disc < -1e-12:
        return None
    if disc < 0:
        disc = 0.0
    s = math.sqrt(disc) / 2.0
    q = _sqf(disc)
    d = None if q is None else q[1]
    l1 = _snap(tr / 2.0 + s)
    l2 = _snap(tr / 2.0 - s)
    return [(l1, _qlab(tr / 2.0, s, d)), (l2, _qlab(tr / 2.0, -s, d))]

def _lline(v):
    # invariant line through O along v (2D)
    if abs(v[0]) < 1e-12:
        return 'x = 0'
    m = casutil.clean(_snapr(v[1] * 1.0 / v[0]))
    if m == 0:
        return 'y = 0'
    if m == 1:
        return 'y = x'
    if m == -1:
        return 'y = -x'
    return 'y = ' + _coefstr(m, None) + 'x' if m > 0 else 'y = -' + _coefstr(-m, None) + 'x'

def _pair(out, a, b):
    # 'a, b' on one answer line if it fits, else two
    if len(a) + len(b) + 2 <= 35:
        out.append(a + ', ' + b)
    else:
        out.append(a)
        out.append('  ' + b)

def _meaning(L):
    if L == 1:
        return 'points on it are invariant'
    if L == 0:
        return 'squashed onto O'
    k = '' if abs(L) == 1 else _coefstr(abs(L), None)
    return 'P -> ' + ('-' if L < 0 else '') + k + 'P' + (' (reversed)' if L < 0 else '')

def t_eig2(A):
    tr, det, disc = _eig2(A)
    out = ['char eq: ' + _eqstr([1, -tr, det], 'L') + ' = 0']
    vs = _vals2(A)
    if vs is None:
        s = math.sqrt(-disc) / 2.0
        out.append('L = ' + _f(complex(tr / 2.0, s)) + ', ' + _f(complex(tr / 2.0, -s)))
        out.append(_warn('complex: no real eigenvectors,'))
        out.append(_warn('so no invariant line through O'))
        out.append(_w('disc = ' + _f(disc) + ' < 0'))
        return out
    (l1, n1), (l2, n2) = vs
    v1 = _vec2(A, l1)
    _pair(out, 'L1 = ' + (n1 if n1 else _f(l1)), 'v1 = ' + _fv(v1))
    rep = abs(l1 - l2) < 1e-9
    if rep:
        nl = _nullity([[A[0][0] - l1, A[0][1]], [A[1][0], A[1][1] - l1]])
        out.append(_warn('repeated eigenvalue L = ' + _f(l1)))
        if nl >= 2:
            out.append('every line through O is invariant')
            out.append(_w('M = ' + _f(l1) + 'I: every vector is an eigenvector'))
        else:
            out.append('invariant line ' + _lline(v1))
            out.append(_w('only one eigenvector: not diagonalisable'))
    else:
        v2 = _vec2(A, l2)
        _pair(out, 'L2 = ' + (n2 if n2 else _f(l2)), 'v2 = ' + _fv(v2))
        out.append('invariant line ' + _lline(v1))
        out.append('invariant line ' + _lline(v2))
        out.append(_w(_lline(v1) + ': ' + _meaning(l1)))
        out.append(_w(_lline(v2) + ': ' + _meaning(l2)))
    out.append(_w('trace = ' + _f(tr) + ' = L1+L2, det = ' + _f(det) + ' = L1L2'))
    out.append(_w('Mv = Lv: v keeps its direction, scaled by L'))
    return out

def _charpoly3(A):
    tr = A[0][0] + A[1][1] + A[2][2]
    m2 = ((A[1][1] * A[2][2] - A[1][2] * A[2][1])
          + (A[0][0] * A[2][2] - A[0][2] * A[2][0])
          + (A[0][0] * A[1][1] - A[0][1] * A[1][0]))
    return [1, -tr, m2, -_det3(A)]

def _shift(A, L):
    n = len(A)
    return [[A[i][j] - (L if i == j else 0) for j in range(n)] for i in range(n)]

def t_eig3(A):
    co = _charpoly3(A)
    ls = _cubic(co)
    out = ['char eq: ' + _eqstr(co, 'L') + ' = 0']
    if len(ls) < 3:
        out.append(_warn(('one real eigenvalue' if ls else 'no real eigenvalues') +
                         '; the rest complex'))
    seen = []
    for L in ls:
        dup = False
        for s in seen:
            if abs(s - L) < 1e-9:
                dup = True
        if dup:
            continue
        seen.append(L)
        cnt = len([s for s in ls if abs(s - L) < 1e-9])
        S = _shift(A, L)
        vs = _nullbasis(S)
        tag = '' if cnt == 1 else ' (x' + str(cnt) + ')'
        if not vs:
            out.append('L = ' + _f(L) + tag + ': no eigenvector found')
            continue
        v = vs[0]
        _pair(out, 'L = ' + _f(L) + tag, 'v = ' + ', '.join([_fv(x) for x in vs]))
        if cnt > 1:
            out.append(_warn('repeated: eigenspace is ' + str(len(vs)) + 'D'))
        if len(vs) == 2:
            out.append(_w('plane of these vectors: ' + _meaning(L)))
        elif len(vs) == 1:
            out.append(_w('line r = t' + _fv(v) + ': ' + _meaning(L)))
        Mv = [sum([A[i][k] * v[k] for k in range(3)]) for i in range(3)]
        err = sum([abs(Mv[i] - L * v[i]) for i in range(3)])
        if err > 1e-6:
            out.append(_warn('check |Mv - Lv| = ' + casutil.sf3(err)))
    out.append(_w('trace = ' + _f(-co[1]) + ' = sum of eigenvalues'))
    out.append(_w('det = ' + _f(-co[3]) + ' = product of eigenvalues'))
    out.append(_w('each v solves (M - L I)v = 0'))
    return out

def _diaglines(A, ls, vs, n, out):
    k = len(ls)
    P = [[vs[j][i] for j in range(k)] for i in range(k)]
    D = [[ls[i] if i == j else 0 for j in range(k)] for i in range(k)]
    for ln in _mlines('P', P):
        out.append(ln)
    for ln in _mlines('D', D):
        out.append(ln)
    Pi = _inv(P)
    if Pi is not None:
        for ln in _mlines('P^-1', Pi):
            out.append(_w(ln))
    if n is not None:
        nn = _iv(n, 'n', 0, 40)
        for ln in _mlines('M^' + str(nn), _mpow(A, nn)):
            out.append(ln)
        ps = [_coefstr(L, None) + '^' + str(nn) + ' = ' + _f(casutil.clean(_snap(L ** nn)))
              for L in ls]
        out.append(_w('D^' + str(nn) + ': ' + ', '.join(ps)))
    out.append(_w('M^n = P D^n P^-1, D^n = diag(L^n)'))
    out.append(_w('columns of P are the eigenvectors,'))
    out.append(_w('in the same order as L in D'))

def t_diag2(A, n):
    vs = _vals2(A)
    if vs is None:
        return ['not diagonalisable over the reals',
                _warn('the eigenvalues are complex')]
    l1 = vs[0][0]
    l2 = vs[1][0]
    if abs(l1 - l2) < 1e-9:
        if _nullity(_shift(A, l1)) < 2:
            return ['not diagonalisable',
                    _warn('repeated L = ' + _f(l1) + ', one eigenvector')]
        v1, v2 = [1, 0], [0, 1]
    else:
        v1 = _vec2(A, l1)
        v2 = _vec2(A, l2)
    out = ['M = P D P^-1', 'D = diag(' + _f(l1) + ', ' + _f(l2) + ')']
    _diaglines(A, [l1, l2], [v1, v2], n, out)
    return out

def t_diag3(A, n):
    co = _charpoly3(A)
    ls = _cubic(co)
    vs = []
    ok = len(ls) == 3
    if ok:
        i = 0
        while i < 3:
            L = ls[i]
            S = _shift(A, L)
            cnt = len([s for s in ls if abs(s - L) < 1e-9])
            if cnt > 1:
                a, piv = _rref(S)
                free = [c for c in range(3) if c not in piv]
                if len(free) < cnt:
                    ok = False
                    break
                for fc in free[:cnt]:
                    v = [0.0] * 3
                    v[fc] = 1.0
                    for r in range(len(piv)):
                        v[piv[r]] = -a[r][fc]
                    vs.append(_scale(v))
                i += cnt
                continue
            v = _nullvec(S)
            if v is None:
                ok = False
                break
            vs.append(v)
            i += 1
    if ok:
        P = [[vs[j][i] for j in range(3)] for i in range(3)]
        if abs(_det3(P)) < 1e-9:
            ok = False
    if not ok:
        return ['not diagonalisable over the reals',
                _warn('needs 3 independent real eigenvectors'),
                _w('char eq: ' + _eqstr(co, 'L') + ' = 0')]
    out = ['M = P D P^-1',
           'D = diag(' + ', '.join([_f(L) for L in ls]) + ')']
    _diaglines(A, ls, vs, n, out)
    return out

def _lincomb(cs, mats):
    n = len(mats[0])
    return [[casutil.clean(_snap(sum([cs[k] * mats[k][i][j] for k in range(len(cs))])))
             for j in range(n)] for i in range(n)]

def _meq(A, B):
    for i in range(len(A)):
        for j in range(len(A)):
            if abs(A[i][j] - B[i][j]) > 1e-9 * (1.0 + abs(A[i][j])):
                return False
    return True

def _mterm(parts):
    # [(coef, 'M^2'), ...] -> '5M - 6I'
    return _linstr(parts, 0)

def t_ch2(A, n):
    tr, det, disc = _eig2(A)
    I = _ident(2)
    M2 = _mm(A, A)
    rhs = _lincomb([tr, -det], [A, I])
    out = ['M^2 = ' + _mterm([(tr, 'M'), (-det, 'I')])]
    out.append(_w('char eq ' + _eqstr([1, -tr, det], 'L') + ' = 0, and M'))
    out.append(_w('satisfies it: M^2 - ' + _f(tr) + 'M + ' + _f(det) + 'I = 0'))
    out.append(_w('check M^2 both ways: ' + ('agrees' if _meq(M2, rhs) else 'DIFFERS')))
    if abs(det) > 1e-12:
        out.append('M^-1 = (' + _mterm([(tr, 'I'), (-1, 'M')]) + ')/' + _coefstr(det, None))
        for ln in _mlines('M^-1', _inv(A)):
            out.append(_w(ln))
    else:
        out.append(_warn('det = 0: M has no inverse'))
    if n is not None:
        nn = _iv(n, 'n', 0, 60)
        p, q = 0.0, 1.0
        k = 0
        while k < nn:
            p, q = tr * p + q, -det * p
            k += 1
        out.append('M^' + str(nn) + ' = ' + _mterm([(p, 'M'), (q, 'I')]))
        for ln in _mlines('M^' + str(nn), _lincomb([p, q], [A, I])):
            out.append(_w(ln))
        out.append(_w('M^(k+1) = M M^k, then M^2 -> trM - detI'))
    return out

def t_ch3(A, n):
    co = _charpoly3(A)
    tr = -co[1]
    m2 = co[2]
    det = -co[3]
    I = _ident(3)
    M2 = _mm(A, A)
    M3 = _mm(M2, A)
    rhs = _lincomb([tr, -m2, det], [M2, A, I])
    out = ['M^3 = ' + _mterm([(tr, 'M^2'), (-m2, 'M'), (det, 'I')])]
    out.append(_w('char eq: ' + _eqstr(co, 'L') + ' = 0'))
    out.append(_w('M satisfies its own characteristic eq'))
    out.append(_w('check M^3 both ways: ' + ('agrees' if _meq(M3, rhs) else 'DIFFERS')))
    if abs(det) > 1e-12:
        out.append('M^-1 = (' + _mterm([(1, 'M^2'), (-tr, 'M'), (m2, 'I')]) +
                   ')/' + _coefstr(det, None))
        for ln in _mlines('M^-1', _inv(A)):
            out.append(_w(ln))
    else:
        out.append(_warn('det = 0: M has no inverse'))
    if n is not None:
        nn = _iv(n, 'n', 0, 60)
        x, y, z = 0.0, 0.0, 1.0
        k = 0
        while k < nn:
            x, y, z = tr * x + y, z - m2 * x, det * x
            k += 1
        out.append('M^' + str(nn) + ' = ' + _mterm([(x, 'M^2'), (y, 'M'), (z, 'I')]))
        for ln in _mlines('M^' + str(nn), _lincomb([x, y, z], [M2, A, I])):
            out.append(_w(ln))
    return out

def _checkvec(A, v):
    n = len(v)
    if max([abs(c) for c in v]) < 1e-12:
        raise ValueError('v must not be the zero vector')
    Mv = [casutil.clean(_snap(sum([A[i][k] * v[k] for k in range(n)]))) for i in range(n)]
    big = 0
    for i in range(n):
        if abs(v[i]) > abs(v[big]):
            big = i
    L = Mv[big] / v[big]
    err = sum([abs(Mv[i] - L * v[i]) for i in range(n)])
    out = []
    if err < 1e-9 * (1.0 + sum([abs(c) for c in Mv])):
        L = casutil.clean(_snapr(L))
        out.append('yes: Mv = ' + _coefstr(L, None) + 'v, L = ' + _f(L))
        out.append(_w('the line through O along v is invariant'))
    else:
        out.append('no: Mv is not a multiple of v')
    out.append('Mv = ' + _fv(Mv))
    return out

def t_chk2(A, v):
    return _checkvec(A, v)

def t_chk3(A, v):
    return _checkvec(A, v)

# ============================================================================
# C  Multivariable calculus
# ============================================================================
# c2 c3 c4 c5 c6 c7 (Xc1 definitional)

def _xy(f):
    _only(f, ['x', 'y'], 'f(x,y)')

def _pt(f, a, b):
    return _ev(f, {'x': a, 'y': b})

def t_partial(f, a, b):
    _xy(f)
    fx = _diff(f, 'x')
    fy = _diff(f, 'y')
    out = ['dz/dx = ' + _ts(fx), 'dz/dy = ' + _ts(fy)]
    fxx = _diff(fx, 'x')
    fyy = _diff(fy, 'y')
    fxy = _diff(fx, 'y')
    out.append(_w('d2z/dx2 = ' + _ts(fxx)))
    out.append(_w('d2z/dy2 = ' + _ts(fyy)))
    out.append(_w('d2z/dxdy = ' + _ts(fxy)))
    out.append(_w('dz/dx holds y constant; dz/dy holds x'))
    if a is None and b is None:
        return out
    if a is None or b is None:
        raise ValueError('give both a and b, or neither')
    z = _pt(f, a, b)
    p = _pt(fx, a, b)
    q = _pt(fy, a, b)
    if z is None or p is None or q is None:
        out.append(_warn('undefined at (' + _f(a) + ', ' + _f(b) + ')'))
        return out
    out.append('at (' + _f(a) + ', ' + _f(b) + '): z = ' + _f(z))
    out.append('dz/dx = ' + _f(p) + ', dz/dy = ' + _f(q))
    out.append('grad z = ' + _fv([p, q]))
    out.append(_w('|grad z| = ' + _f(math.sqrt(p * p + q * q)) +
                  ', normal to the contour'))
    return out

def _newton(fx, fy, fxx, fxy, fyy, x, y):
    # 2-D Newton on grad z = 0; only a converged run counts
    i = 0
    while i < 100:
        a = _pt(fx, x, y)
        b = _pt(fy, x, y)
        if a is None or b is None:
            return None
        if a == 0 and b == 0:
            return (x, y)
        h11 = _pt(fxx, x, y)
        h12 = _pt(fxy, x, y)
        h22 = _pt(fyy, x, y)
        if h11 is None or h12 is None or h22 is None:
            return None
        det = h11 * h22 - h12 * h12
        if det == 0:
            if abs(a) < 1e-12 and abs(b) < 1e-12:
                return (x, y)
            return None
        dx = (a * h22 - b * h12) / det
        dy = (h11 * b - h12 * a) / det
        x -= dx
        y -= dy
        if abs(x) > 10 or abs(y) > 10:
            return None
        if abs(dx) < 1e-12 * (1 + abs(x)) and abs(dy) < 1e-12 * (1 + abs(y)):
            a = _pt(fx, x, y)
            b = _pt(fy, x, y)
            if a is None or b is None or abs(a) > 1e-8 or abs(b) > 1e-8:
                return None
            return (x, y)
        i += 1
    return None

def t_stat(f, a, b):
    _xy(f)
    fx = _diff(f, 'x')
    fy = _diff(f, 'y')
    fxx = _diff(fx, 'x')
    fyy = _diff(fy, 'y')
    fxy = _diff(fx, 'y')
    starts = []
    if a is not None and b is not None:
        starts.append((a, b))
    for sx in (-3.3, -1.4, 0.0, 1.3, 3.4):
        for sy in (-3.6, -1.2, 0.0, 1.5, 3.1):
            starts.append((sx, sy))
    found = []
    for sx, sy in starts:
        p = _newton(fx, fy, fxx, fxy, fyy, sx, sy)
        if p is None:
            continue
        x = 0 if abs(p[0]) < 1e-9 else _snapr(_snap(p[0]))
        y = 0 if abs(p[1]) < 1e-9 else _snapr(_snap(p[1]))
        dup = False
        for q in found:
            if abs(q[0] - x) < 1e-6 * (1 + abs(x)) and abs(q[1] - y) < 1e-6 * (1 + abs(y)):
                dup = True
        if not dup:
            found.append((x, y))
        if len(found) >= 8:
            break
    out = [_w('dz/dx = ' + _ts(fx)), _w('dz/dy = ' + _ts(fy))]
    if not found:
        out.insert(0, _warn('no stationary point found'))
        out.append(_w('searched |x|, |y| <= 10 from starts in -4..4'))
        return out
    found.sort()
    head = [str(len(found)) + ' stationary point' + ('' if len(found) == 1 else 's')]
    for x, y in found:
        z = _pt(f, x, y)
        A = _pt(fxx, x, y)
        B = _pt(fxy, x, y)
        C = _pt(fyy, x, y)
        pt = '(' + _f(x) + ', ' + _f(y) + ', ' + ('?' if z is None else _f(_snap(z))) + ')'
        if A is None or B is None or C is None:
            head.append(pt + ' ?')
            continue
        D = A * C - B * B
        if D > 1e-9:
            kind = 'min' if A > 0 else 'max'
        elif D < -1e-9:
            kind = 'saddle'
        else:
            kind = 'D = 0, test fails'
        head.append(pt + ' ' + kind)
        out.append(_w(pt + ': fxx=' + _f(A) + ' fyy=' + _f(C) + ' fxy=' + _f(B) +
                      ' D=' + _f(D)))
    if len(found) >= 8:
        head.append(_warn('first 8 found; there may be more'))
    out.append(_w('D = fxx fyy - fxy^2: D > 0 max/min by'))
    out.append(_w('sign of fxx, D < 0 saddle; D = 0: look'))
    out.append(_w('at z along lines through the point'))
    out.append(_w('Newton from starts in -4..4, |x|,|y| <= 10'))
    return head + out

def t_tplane(f, a, b):
    _xy(f)
    fx = _diff(f, 'x')
    fy = _diff(f, 'y')
    z = _pt(f, a, b)
    p = _pt(fx, a, b)
    q = _pt(fy, a, b)
    if z is None or p is None or q is None:
        raise ValueError('f or its derivatives undefined there')
    z, p, q = _snap(z), _snap(p), _snap(q)
    k = z - p * a - q * b
    out = ['z = ' + _linstr([(p, 'x'), (q, 'y')], k)]
    out.append('normal (fx, fy, -1) = ' + _fv([p, q, -1]))
    out.append('r = ' + _fv([a, b, z]) + ' + t' + _fv([p, q, -1]))
    out.append(_w('point (' + _f(a) + ', ' + _f(b) + ', ' + _f(z) + ') on z = f'))
    out.append(_w('dz/dx = ' + _ts(fx) + ' = ' + _f(p)))
    out.append(_w('dz/dy = ' + _ts(fy) + ' = ' + _f(q)))
    out.append(_w('z - z0 = fx(x - a) + fy(y - b)'))
    return out

def t_gradg(g, a, b, c):
    _only(g, ['x', 'y', 'z'], 'g(x,y,z)')
    env = {'x': a, 'y': b, 'z': c}
    ds = [_diff(g, v) for v in ('x', 'y', 'z')]
    n = [_ev(d, env) for d in ds]
    k = _ev(g, env)
    if k is None or None in n:
        raise ValueError('g or its derivatives undefined there')
    n = [casutil.clean(_snap(v)) for v in n]
    out = ['grad g = ' + _fv(n)]
    if max([abs(v) for v in n]) < 1e-12:
        out.append(_warn('grad g = 0: no normal at this point'))
        return out
    s = _scale(n)
    d = casutil.clean(_snap(sum([s[i] * [a, b, c][i] for i in range(3)])))
    out.append('normal direction ' + _fv(s))
    out.append('tangent plane: ' + _linstr([(s[0], 'x'), (s[1], 'y'), (s[2], 'z')], 0) +
               ' = ' + _f(d))
    out.append('r = ' + _fv([a, b, c]) + ' + t' + _fv(s))
    out.append(_w('surface g = ' + _f(casutil.clean(_snap(k))) + ' through the point'))
    out.append(_w('dg/dx = ' + _ts(ds[0])))
    out.append(_w('dg/dy = ' + _ts(ds[1])))
    out.append(_w('dg/dz = ' + _ts(ds[2])))
    return out

def _axiscut(f, c, axis):
    # where the contour f = c meets y = 0 (axis 'x') or x = 0 (axis 'y')
    if axis == 'x':
        t = caseng.subst(f, 'y', ('n', 0))
    else:
        t = caseng.subst(caseng.subst(f, 'x', ('n', 0)), 'y', ('v', 'x'))
    same = True
    for xv in (-3.7, -1.3, 0.4, 2.9):
        v = _ev(t, {'x': xv})
        if v is None or abs(v - c) > 1e-12 * (1 + abs(c)):
            same = False
    if same:
        return None
    try:
        rs = cascalc.solve(('-', t, ('n', c)), 'x')
    except Exception:
        rs = []
    rs = [casutil.clean(_snapr(_snap(r))) for r in rs]
    return rs

def t_contour(f, cs):
    _xy(f)
    if len(cs) > 6:
        raise ValueError('at most 6 levels')
    N = 48
    lo = -5.0
    h = 10.0 / N
    grid = [[_pt(f, lo + i * h, lo + j * h) for i in range(N + 1)] for j in range(N + 1)]
    polys = []
    out = []
    for c in cs:
        # marching squares: one segment (two for a saddle cell) per cell
        pl = []
        cnt = 0
        for j in range(N):
            r0 = grid[j]
            r1 = grid[j + 1]
            y0 = lo + j * h
            for i in range(N):
                z00 = r0[i]
                z10 = r0[i + 1]
                z01 = r1[i]
                z11 = r1[i + 1]
                if z00 is None or z10 is None or z01 is None or z11 is None:
                    continue
                x0 = lo + i * h
                cp = []
                for za, zb, xa, ya, dx, dy in ((z00, z10, x0, y0, h, 0.0),
                                               (z10, z11, x0 + h, y0, 0.0, h),
                                               (z01, z11, x0, y0 + h, h, 0.0),
                                               (z00, z01, x0, y0, 0.0, h)):
                    if za != zb and (za - c) * (zb - c) <= 0:
                        t = (c - za) / (zb - za)
                        cp.append((xa + dx * t, ya + dy * t))
                if len(cp) >= 2:
                    pl.append(cp[0])
                    pl.append(cp[1])
                    pl.append(None)
                    cnt += 1
                    if len(cp) == 4:
                        pl.append(cp[2])
                        pl.append(cp[3])
                        pl.append(None)
                        cnt += 1
        if pl:
            polys.append(pl)
        xs = _axiscut(f, c, 'x')
        ys = _axiscut(f, c, 'y')
        for ax, var, rs in (('y=0', 'x', xs), ('x=0', 'y', ys)):
            if rs is None:
                tail = 'contains ' + ax
            elif rs:
                tail = 'cuts ' + ax + ' at ' + var + ' = ' + ', '.join([_f(v) for v in rs[:4]])
            else:
                tail = 'cuts ' + ax + ' nowhere'
            out.append('z = ' + _f(c) + ' ' + tail)
        out.append(_w('z = ' + _f(c) + ': ' + str(cnt) + ' segments in -5..5'))
    out.append(_w('contours of z = ' + _ts(f)))
    out.append(_w('contours close together: steep surface'))
    out.append(_w('rings round a point: max or min there'))
    if not polys:
        out.insert(0, _warn('no contour points in -5 <= x, y <= 5'))
        return out
    import plot
    plot.run(polys, kind='lines', title='contours z = ' + ', '.join([_f(c) for c in cs]))
    return out

def _sections(f, ks, var):
    _xy(f)
    if len(ks) > 4:
        raise ValueError('at most 4 sections')
    other = 'y' if var == 'x' else 'x'
    out = []
    curves = []
    for k in ks:
        t = caseng.subst(f, var, ('n', k))
        out.append(var + ' = ' + _f(k) + ': z = ' + _ts(t))
        if var == 'x':
            t = caseng.subst(t, 'y', ('v', 'x'))
        curves.append(t)
    out.append(_w('each section is a curve z against ' + other))
    out.append(_w('in the plane ' + var + ' = constant'))
    import plot
    plot.run(curves, -5.0, 5.0, 'y', 'z against ' + other + ', ' + var + ' = ' +
             ', '.join([_f(k) for k in ks]))
    return out

def t_secy(f, ks):
    return _sections(f, ks, 'y')

def t_secx(f, ks):
    return _sections(f, ks, 'x')

# ============================================================================

SECTIONS = [
    ('R', 'Recurrence relations', [
        ('u(n+1) = a u(n)', 'a,u0', t_rec1h),
        ('1st order a u + f(n)', 'a,f(n),u0,n0?', t_rec1),
        ('2nd order homogeneous', 'a,b,u0,u1', t_rec2h),
        ('2nd order + f(n)', 'a,b,f(n),u0,u1,n0?', t_rec2),
        ('Verify u(n+1)=F(n,u)', 'F(n,u),u(n)', t_verify1),
        ('Verify u(n+2)=F(n,u,v)', 'F(n,u,v),u(n)', t_verify2),
        ('Behaviour u(n+1)=F', 'F(n,u),u0', t_behave),
        ('Associated sequence', 'F(n,u),u0,g(n,u)', t_assoc),
        ('Ratio u(n+1)/u(n)', 'a,b,u0,u1', t_ratio),
    ]),
    ('G', 'Sets and groups', [
        ('Sets A, B in E', 'nA,nB,elements*', t_sets),
        ('Subsets of a set', 'elements*', t_subsets),
        ('Group axioms', 'n,table*', t_gaxioms),
        ('Element orders', 'n,table*', t_gorders),
        ('Subgroups, Lagrange', 'n,table*', t_subgroups),
        ('Isomorphism G to H', 'n,tables*', t_giso),
        ('Identify group (n<=10)', 'n,table*', t_gident),
        ('Z_n under + mod n', 'n', t_zadd),
        ('Units under x mod n', 'n', t_zmul),
        ('Symmetries of n-gon', 'n', t_dihedral),
    ]),
    ('M', 'Matrices: eigenvalues', [
        ('Eigen 2x2', 'A[2x2]', t_eig2),
        ('Eigen 3x3', 'A[3x3]', t_eig3),
        ('Diagonalise 2x2 M^n', 'A[2x2],n?', t_diag2),
        ('Diagonalise 3x3 M^n', 'A[3x3],n?', t_diag3),
        ('Cayley-Hamilton 2x2', 'A[2x2],n?', t_ch2),
        ('Cayley-Hamilton 3x3', 'A[3x3],n?', t_ch3),
        ('Is v eigenvector 2x2', 'A[2x2],v[2]', t_chk2),
        ('Is v eigenvector 3x3', 'A[3x3],v[3]', t_chk3),
    ]),
    ('C', 'Multivariable calculus', [
        ('Partial derivatives', 'f(x,y),a?,b?', t_partial),
        ('Stationary points', 'f(x,y),a?,b?', t_stat),
        ('Tangent plane z=f', 'f(x,y),a,b', t_tplane),
        ('grad g, normal, plane', 'g(x,y,z),a,b,c', t_gradg),
        ('Contours z = c', 'f(x,y),c*', t_contour),
        ('Sections y = k', 'f(x,y),k*', t_secy),
        ('Sections x = k', 'f(x,y),k*', t_secx),
    ]),
]
