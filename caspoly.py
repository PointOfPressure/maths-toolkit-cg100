import caseng

def rmake(n, d):
    if d == 0:
        return None
    if d < 0:
        n = -n
        d = -d
    g = caseng.gcd(n, d)
    if g:
        n = n // g
        d = d // g
    return (n, d)

R0 = (0, 1)
R1 = (1, 1)

def radd(a, b):
    return rmake(a[0] * b[1] + b[0] * a[1], a[1] * b[1])

def rsub(a, b):
    return rmake(a[0] * b[1] - b[0] * a[1], a[1] * b[1])

def rmul(a, b):
    return rmake(a[0] * b[0], a[1] * b[1])

def rdiv(a, b):
    if b[0] == 0:
        return None
    return rmake(a[0] * b[1], a[1] * b[0])

def rneg(a):
    return (-a[0], a[1])

def rzero(a):
    return a[0] == 0

def rint(a):
    return a[0] if a[1] == 1 else None

def ratof(node):
    t = node[0]
    if t == 'n':
        v = node[1]
        if isinstance(v, int):
            return (v, 1)
        if isinstance(v, float) and v == int(v) and -1e15 < v < 1e15:
            return (int(v), 1)
        return None
    if t == 'neg':
        r = ratof(node[1])
        return None if r is None else rneg(r)
    if t == '/':
        a = ratof(node[1])
        b = ratof(node[2])
        if a is None or b is None:
            return None
        return rdiv(a, b)
    if t == '*':
        a = ratof(node[1])
        b = ratof(node[2])
        if a is None or b is None:
            return None
        return rmul(a, b)
    if t == '+':
        a = ratof(node[1])
        b = ratof(node[2])
        if a is None or b is None:
            return None
        return radd(a, b)
    if t == '-':
        a = ratof(node[1])
        b = ratof(node[2])
        if a is None or b is None:
            return None
        return rsub(a, b)
    if t == '^':
        a = ratof(node[1])
        b = ratof(node[2])
        if a is None or b is None:
            return None
        e = rint(b)
        if e is None or e < -64 or e > 64:
            return None
        if e >= 0:
            return rmake(a[0] ** e, a[1] ** e)
        if a[0] == 0:
            return None
        return rmake(a[1] ** (-e), a[0] ** (-e))
    return None

def ratnode(r):
    if r[1] == 1:
        return ('n', r[0])
    return ('/', ('n', r[0]), ('n', r[1]))

MAXPOW = 12

def _factors(node, coef, facs):
    t = node[0]
    if t == 'n':
        r = ratof(node)
        return None if r is None else rmul(coef, r)
    if t == 'neg':
        return _factors(node[1], rneg(coef), facs)
    if t == '*':
        c = _factors(node[1], coef, facs)
        if c is None:
            return None
        return _factors(node[2], c, facs)
    if t == '/':
        c = _factors(node[1], coef, facs)
        if c is None:
            return None
        r = ratof(node[2])
        if r is not None:
            return rdiv(c, r)
        inv = []
        c2 = _factors(node[2], R1, inv)
        if c2 is None or rzero(c2):
            return None
        for key, base, e in inv:
            facs.append((key, base, -e))
        return rdiv(c, c2)
    if t == '^':
        r = ratof(node)
        if r is not None:
            return rmul(coef, r)
        e = ratof(node[2])
        ei = None if e is None else rint(e)
        if ei is not None and -MAXPOW <= ei <= MAXPOW:
            inner = []
            c = _factors(node[1], R1, inner)
            if c is None:
                return None
            if ei >= 0:
                ck = rmake(c[0] ** ei, c[1] ** ei)
            else:
                if c[0] == 0:
                    return None
                ck = rmake(c[1] ** (-ei), c[0] ** (-ei))
            if ck is None:
                return None
            for key, base, be in inner:
                facs.append((key, base, be * ei))
            return rmul(coef, ck)
    key = caseng.tostr(node)
    facs.append((key, node, 1))
    return coef

def term_of(node):
    facs = []
    c = _factors(node, R1, facs)
    if c is None:
        return None
    merged = {}
    order = []
    for key, base, e in facs:
        if key in merged:
            merged[key] = (base, merged[key][1] + e)
        else:
            merged[key] = (base, e)
            order.append(key)
    order.sort()
    out = []
    for key in order:
        base, e = merged[key]
        if e != 0:
            out.append((key, base, e))
    return (c, out)

def term_key(facs):
    parts = []
    for key, base, e in facs:
        parts.append(key + "^" + str(e))
    return ",".join(parts)

def term_deg(facs):
    d = 0
    for key, base, e in facs:
        d += e
    return d

def _mulchain(items):
    node = None
    for f in items:
        node = f if node is None else ('*', node, f)
    return node

def term_node(coef, facs):
    top = []
    bot = []
    for key, base, e in facs:
        if e > 0:
            top.append(base if e == 1 else ('^', base, ('n', e)))
        elif e < 0:
            bot.append(base if e == -1 else ('^', base, ('n', -e)))
    num = _mulchain(top)
    den = _mulchain(bot)
    neg = coef[0] < 0
    cn = -coef[0] if neg else coef[0]
    if cn != 1 or num is None:
        num = ('n', cn) if num is None else ('*', ('n', cn), num)
    if coef[1] != 1:
        den = ('n', coef[1]) if den is None else ('*', ('n', coef[1]), den)
    if neg:
        num = ('neg', num)
    return num if den is None else ('/', num, den)

def cancel(node):
    if node[0] not in ('*', '/', 'neg', '^'):
        return caseng.simplify(node)
    tm = term_of(node)
    if tm is None:
        return caseng.simplify(node)
    return term_node(tm[0], tm[1])

def _addterms(node, sign, out):
    stack = [(node, sign)]
    while stack:
        n, s = stack.pop()
        t = n[0]
        if t == '+':
            stack.append((n[1], s))
            stack.append((n[2], s))
        elif t == '-':
            stack.append((n[1], s))
            stack.append((n[2], -s))
        elif t == 'neg':
            stack.append((n[1], -s))
        else:
            out.append((n, s))

def _mulout(a, b):
    ta = []
    tb = []
    _addterms(a, 1, ta)
    _addterms(b, 1, tb)
    parts = []
    for na, sa in ta:
        for nb, sb in tb:
            p = ('*', na, nb)
            parts.append(p if sa * sb > 0 else ('neg', p))
    node = parts[0]
    i = 1
    while i < len(parts):
        node = ('+', node, parts[i])
        i += 1
    return node

def expand(node):
    return caseng.simplify(_ex(node))

def _ex(n):
    t = n[0]
    if t == 'n' or t == 'v':
        return n
    if t == 'neg':
        return ('neg', _ex(n[1]))
    if t == '+' or t == '-':
        return (t, _ex(n[1]), _ex(n[2]))
    if t == '*':
        return _mulout(_ex(n[1]), _ex(n[2]))
    if t == '/':
        a = _ex(n[1])
        b = _ex(n[2])
        if ratof(b) is not None:
            ts = []
            _addterms(a, 1, ts)
            node = None
            for tn, s in ts:
                piece = ('/', tn, b)
                if s < 0:
                    piece = ('neg', piece)
                node = piece if node is None else ('+', node, piece)
            return node
        return ('/', a, b)
    if t == '^':
        a = _ex(n[1])
        e = ratof(n[2])
        ei = None if e is None else rint(e)
        if ei is not None and 0 <= ei <= MAXPOW and a[0] in ('+', '-'):
            if ei == 0:
                return ('n', 1)
            out = a
            i = 1
            while i < ei:
                out = _mulout(out, a)
                i += 1
            return out
        return ('^', a, _ex(n[2]))
    if len(n) == 2:
        return (n[0], _ex(n[1]))
    if len(n) == 3:
        return (n[0], _ex(n[1]), _ex(n[2]))
    return n

def collect(node):
    leaves = []
    _addterms(node, 1, leaves)
    if len(leaves) == 1 and leaves[0][1] == 1 and leaves[0][0][0] not in ('*', '/', '^'):
        return caseng.simplify(node)
    bag = {}
    order = []
    for leaf, sign in leaves:
        tm = term_of(leaf)
        if tm is None:
            return caseng.simplify(node)
        coef, facs = tm
        if sign < 0:
            coef = rneg(coef)
        k = term_key(facs)
        if k in bag:
            bag[k] = (radd(bag[k][0], coef), facs)
        else:
            bag[k] = (coef, facs)
            order.append(k)
    keep = []
    for k in order:
        coef, facs = bag[k]
        if not rzero(coef):
            keep.append((term_deg(facs), k, coef, facs))
    if not keep:
        return ('n', 0)
    keep.sort(key=lambda it: (-it[0], 0 if it[2][0] > 0 else 1, it[1]))
    out = None
    for deg, k, coef, facs in keep:
        piece = term_node(coef, facs)
        if out is None:
            out = piece
        elif piece[0] == 'neg':
            out = ('-', out, piece[1])
        elif coef[0] < 0:
            out = ('-', out, term_node(rneg(coef), facs))
        else:
            out = ('+', out, piece)
    return out

def ptrim(p):
    while p and rzero(p[-1]):
        p.pop()
    return p

def poly(node, var):
    t = node[0]
    if t == 'v':
        if node[1] == var:
            return [R0, R1]
        return None
    if t == 'n':
        r = ratof(node)
        return None if r is None else ([] if rzero(r) else [r])
    if t == 'neg':
        p = poly(node[1], var)
        return None if p is None else [rneg(c) for c in p]
    if t == '+' or t == '-':
        a = poly(node[1], var)
        b = poly(node[2], var)
        if a is None or b is None:
            return None
        return padd(a, b) if t == '+' else psub(a, b)
    if t == '*':
        a = poly(node[1], var)
        b = poly(node[2], var)
        if a is None or b is None:
            return None
        return pmul(a, b)
    if t == '/':
        a = poly(node[1], var)
        r = ratof(node[2])
        if a is None or r is None or rzero(r):
            return None
        return ptrim([rdiv(c, r) for c in a])
    if t == '^':
        e = ratof(node[2])
        ei = None if e is None else rint(e)
        if ei is None or ei < 0 or ei > MAXPOW:
            return None
        a = poly(node[1], var)
        if a is None:
            return None
        out = [R1]
        i = 0
        while i < ei:
            out = pmul(out, a)
            i += 1
        return out
    return None

def padd(a, b):
    n = len(a) if len(a) > len(b) else len(b)
    out = []
    i = 0
    while i < n:
        x = a[i] if i < len(a) else R0
        y = b[i] if i < len(b) else R0
        out.append(radd(x, y))
        i += 1
    return ptrim(out)

def psub(a, b):
    n = len(a) if len(a) > len(b) else len(b)
    out = []
    i = 0
    while i < n:
        x = a[i] if i < len(a) else R0
        y = b[i] if i < len(b) else R0
        out.append(rsub(x, y))
        i += 1
    return ptrim(out)

def pmul(a, b):
    if not a or not b:
        return []
    out = []
    i = 0
    while i < len(a) + len(b) - 1:
        out.append(R0)
        i += 1
    i = 0
    while i < len(a):
        if not rzero(a[i]):
            j = 0
            while j < len(b):
                out[i + j] = radd(out[i + j], rmul(a[i], b[j]))
                j += 1
        i += 1
    return ptrim(out)

def pscale(a, r):
    return ptrim([rmul(c, r) for c in a])

def pdivmod(a, b):
    b = ptrim(list(b))
    if not b:
        return None
    r = list(a)
    q = []
    i = 0
    while i < len(a) - len(b) + 1:
        q.append(R0)
        i += 1
    while len(r) >= len(b) and r:
        k = len(r) - len(b)
        c = rdiv(r[-1], b[-1])
        if c is None:
            return None
        q[k] = c
        i = 0
        while i < len(b):
            r[k + i] = rsub(r[k + i], rmul(c, b[i]))
            i += 1
        ptrim(r)
    return (ptrim(q), r)

def _coefterm(c, power):
    # c * power with no "1*" and negatives folded into the numerator
    neg = c[0] < 0
    top = -c[0] if neg else c[0]
    node = power if top == 1 else ('*', ('n', top), power)
    if neg:
        node = ('neg', node) if top == 1 else ('*', ('n', -top), power)
    if c[1] == 1:
        return node
    return ('/', node, ('n', c[1]))

def ptree(p, var):
    if not p:
        return ('n', 0)
    node = None
    i = len(p) - 1
    while i >= 0:
        c = p[i]
        if not rzero(c):
            if i == 0:
                piece = ratnode(c)
            else:
                power = ('v', var) if i == 1 else ('^', ('v', var), ('n', i))
                piece = _coefterm(c, power)
            if node is None:
                node = piece
            elif c[0] < 0:
                pos = (-c[0], c[1])
                if i == 0:
                    node = ('-', node, ratnode(pos))
                else:
                    power = ('v', var) if i == 1 else ('^', ('v', var), ('n', i))
                    node = ('-', node, _coefterm(pos, power))
            else:
                node = ('+', node, piece)
        i -= 1
    return ('n', 0) if node is None else node

def pcontent(p):
    num = 0
    den = 1
    for c in p:
        num = caseng.gcd(num, c[0])
        den = den // caseng.gcd(den, c[1]) * c[1]
    if num == 0:
        return R1
    return rmake(num, den)

def _divisors(n):
    n = abs(n)
    out = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            if d != n // d:
                out.append(n // d)
        d += 1
    out.sort()
    return out

def roots_rational(p):
    p = ptrim(list(p))
    out = []
    if len(p) < 2:
        return out
    while len(p) >= 2 and rzero(p[0]):
        out.append(R0)
        p = p[1:]
    if len(p) < 2:
        return out
    g = pcontent(p)
    if g is not None and not rzero(g):
        p = [rdiv(c, g) for c in p]
    c0 = rint(p[0])
    cn = rint(p[-1])
    if c0 is None or cn is None:
        return out
    found = True
    while found and len(p) >= 2:
        found = False
        c0 = rint(p[0])
        cn = rint(p[-1])
        if c0 is None or cn is None or c0 == 0:
            break
        for num in _divisors(c0):
            for den in _divisors(cn):
                for s in (1, -1):
                    cand = rmake(s * num, den)
                    if cand is None or peval(p, cand) != R0:
                        continue
                    qr = pdivmod(p, [rneg(cand), R1])
                    if qr is None or qr[1]:
                        continue
                    out.append(cand)
                    p = qr[0]
                    found = True
                    break
                if found:
                    break
            if found:
                break
    return out

def peval(p, r):
    acc = R0
    i = len(p) - 1
    while i >= 0:
        acc = radd(rmul(acc, r), p[i])
        i -= 1
    return acc

def pfactors(p, var):
    p = ptrim(list(p))
    if len(p) < 2:
        return (p[0] if p else R0, [])
    lead = p[-1]
    p = [rdiv(c, lead) for c in p]
    out = []
    for r in roots_rational(p):
        f = [rneg(r), R1]
        qr = pdivmod(p, f)
        if qr is None or qr[1]:
            continue
        p = qr[0]
        placed = False
        for i in range(len(out)):
            if out[i][0] == f:
                out[i] = (f, out[i][1] + 1)
                placed = True
                break
        if not placed:
            out.append((f, 1))
    if len(p) > 1:
        out.append((p, 1))
    return (lead, out)

def factor(node, var='x'):
    p = poly(node, var)
    if p is None or len(p) < 2:
        return None
    lead, fs = pfactors(p, var)
    if not fs:
        return None
    if len(fs) == 1 and fs[0][1] == 1 and len(fs[0][0]) == len(p):
        return None
    parts = []
    for f, m in fs:
        den = 1
        for c in f:
            den = den // caseng.gcd(den, c[1]) * c[1]
        if den != 1:
            f = [rmul(c, (den, 1)) for c in f]
            k = rmake(1, den ** m)
            lead = rmul(lead, k)
        ft = ptree(f, var)
        parts.append(ft if m == 1 else ('^', ft, ('n', m)))
    node2 = parts[0]
    i = 1
    while i < len(parts):
        node2 = ('*', node2, parts[i])
        i += 1
    if lead != R1:
        node2 = ('*', ratnode(lead), node2)
    return caseng.simplify(node2)

def solve_rat(A, b):
    n = len(A)
    if n == 0:
        return []
    m = len(A[0])
    if m != n:
        return None
    M = []
    i = 0
    while i < n:
        M.append(list(A[i]) + [b[i]])
        i += 1
    col = 0
    while col < n:
        piv = -1
        r = col
        while r < n:
            if not rzero(M[r][col]):
                piv = r
                break
            r += 1
        if piv < 0:
            return None
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        j = col
        while j <= n:
            M[col][j] = rdiv(M[col][j], d)
            j += 1
        r = 0
        while r < n:
            if r != col and not rzero(M[r][col]):
                f = M[r][col]
                j = col
                while j <= n:
                    M[r][j] = rsub(M[r][j], rmul(f, M[col][j]))
                    j += 1
            r += 1
        col += 1
    return [M[i][n] for i in range(n)]

def partial(numn, denn, var='x'):
    N = poly(numn, var)
    D = poly(denn, var)
    if N is None or D is None or len(D) < 2:
        return None
    qr = pdivmod(N, D)
    if qr is None:
        return None
    quot, rem = qr
    if not rem:
        return (ptree(quot, var) if quot else None, [])
    lead, fs = pfactors(D, var)
    if not fs:
        return None
    for f, m in fs:
        if len(f) > 3:
            return None
    cols = []
    for f, m in fs:
        d = len(f) - 1
        i = 1
        while i <= m:
            k = 0
            while k < d:
                cols.append((f, i, k))
                k += 1
            i += 1
    deg = len(D) - 1
    if len(cols) != deg:
        return None
    Dm = [rdiv(c, lead) for c in D]
    basis = []
    for f, i, k in cols:
        fp = [R1]
        t = 0
        while t < i:
            fp = pmul(fp, f)
            t += 1
        qr2 = pdivmod(Dm, fp)
        if qr2 is None or qr2[1]:
            return None
        b = qr2[0]
        if k:
            shift = []
            s = 0
            while s < k:
                shift.append(R0)
                s += 1
            b = pmul(b, shift + [R1])
        basis.append(b)
    target = [rdiv(c, lead) for c in rem]
    A = []
    rhs = []
    row = 0
    while row < deg:
        A.append([(basis[j][row] if row < len(basis[j]) else R0) for j in range(deg)])
        rhs.append(target[row] if row < len(target) else R0)
        row += 1
    sol = solve_rat(A, rhs)
    if sol is None:
        return None
    terms = []
    j = 0
    while j < deg:
        f, i, k = cols[j]
        c = sol[j]
        if not rzero(c):
            top = ratnode(c) if k == 0 else caseng.simplify(('*', ratnode(c), ('v', var)))
            merged = False
            for tix in range(len(terms)):
                if terms[tix][1] == f and terms[tix][2] == i:
                    terms[tix] = (caseng.simplify(('+', terms[tix][0], top)), f, i)
                    merged = True
                    break
            if not merged:
                terms.append((top, f, i))
        j += 1
    out = []
    for top, f, i in terms:
        out.append((top, ptree(f, var), i))
    return (ptree(quot, var) if quot else None, out)


def pgcd(a, b):
    # monic gcd of two rational-coefficient polynomials; at most 60 steps
    a = ptrim(list(a))
    b = ptrim(list(b))
    guard = 0
    while b and guard < 60:
        guard += 1
        qr = pdivmod(a, b)
        if qr is None:
            return None
        a = b
        b = ptrim(qr[1])
    if not a:
        return None
    lead = a[-1]
    return [rdiv(c, lead) for c in a]

def polyfrac(node, var):
    # node -> (numerator poly, denominator poly) over the rationals, else None
    t = node[0]
    if t == 'n':
        r = ratof(node)
        if r is None:
            return None
        return ([] if rzero(r) else [r], [R1])
    if t == 'v':
        if node[1] == var:
            return ([R0, R1], [R1])
        return None
    if t == 'neg':
        f = polyfrac(node[1], var)
        if f is None:
            return None
        return ([rneg(c) for c in f[0]], f[1])
    if t == '+' or t == '-':
        A = polyfrac(node[1], var)
        if A is None:
            return None
        B = polyfrac(node[2], var)
        if B is None:
            return None
        u = pmul(A[0], B[1])
        v = pmul(B[0], A[1])
        return (padd(u, v) if t == '+' else psub(u, v), pmul(A[1], B[1]))
    if t == '*':
        A = polyfrac(node[1], var)
        if A is None:
            return None
        B = polyfrac(node[2], var)
        if B is None:
            return None
        return (pmul(A[0], B[0]), pmul(A[1], B[1]))
    if t == '/':
        A = polyfrac(node[1], var)
        if A is None:
            return None
        B = polyfrac(node[2], var)
        if B is None or not B[0]:
            return None
        return (pmul(A[0], B[1]), pmul(A[1], B[0]))
    if t == '^':
        e = ratof(node[2])
        ei = None if e is None else rint(e)
        if ei is None or ei > MAXPOW or ei < -MAXPOW:
            return None
        A = polyfrac(node[1], var)
        if A is None:
            return None
        num, den = A
        if ei < 0:
            num, den = den, num
            ei = -ei
            if not num:
                return None
        rn = [R1]
        rd = [R1]
        i = 0
        while i < ei:
            rn = pmul(rn, num)
            rd = pmul(rd, den)
            i += 1
        return (rn, rd)
    return None

def pderiv(p):
    out = []
    i = 1
    while i < len(p):
        out.append(rmul(p[i], (i, 1)))
        i += 1
    return ptrim(out)

def sqfree(D):
    # D -> [(a1, 1), (a2, 2), ...] with D = prod ai^i; at most 6 levels
    g = pgcd(D, pderiv(D))
    if g is None or len(g) < 2:
        return [(D, 1)]
    qr = pdivmod(D, g)
    if qr is None or qr[1]:
        return [(D, 1)]
    w = ptrim(qr[0])
    out = []
    i = 1
    while i <= 6 and len(w) > 1:
        y = pgcd(w, g)
        if y is None:
            break
        qa = pdivmod(w, y)
        if qa is None or qa[1]:
            break
        a = ptrim(qa[0])
        if len(a) > 1:
            out.append((a, i))
        w = ptrim(y)
        qg = pdivmod(g, y)
        if qg is None or qg[1]:
            break
        g = ptrim(qg[0])
        i += 1
    if not out:
        return [(D, 1)]
    return out

def denfactored(D, var):
    parts = []
    for a, m in sqfree(D):
        t = ptree(a, var)
        f = factor(t, var)
        base = t if f is None else f
        parts.append(base if m == 1 else ('^', base, ('n', m)))
    node = parts[0]
    i = 1
    while i < len(parts):
        node = ('*', node, parts[i])
        i += 1
    return caseng.simplify(node)

def ratnorm(node, var, needcancel=False):
    # one rational expression over a common denominator, cancelled
    f = polyfrac(node, var)
    if f is None:
        return None
    N = ptrim(list(f[0]))
    D = ptrim(list(f[1]))
    if not D:
        return None
    if not N:
        return ('n', 0)
    if len(D) < 2:
        return None
    g = pgcd(N, D)
    if g is None:
        return None
    if needcancel and len(g) < 2:
        return None
    if len(g) > 1:
        qn = pdivmod(N, g)
        qd = pdivmod(D, g)
        if qn is None or qd is None or qn[1] or qd[1]:
            return None
        N = ptrim(qn[0])
        D = ptrim(qd[0])
    if not D:
        return None
    c = pcontent(D)
    if c is None or rzero(c):
        return None
    if D[-1][0] < 0:
        c = rneg(c)
    N = ptrim([rdiv(x, c) for x in N])
    D = ptrim([rdiv(x, c) for x in D])
    if len(D) < 2:
        d0 = D[0] if D else R1
        return ptree(ptrim([rdiv(x, d0) for x in N]), var)
    return ('/', ptree(N, var), denfactored(D, var))


def _denpoly(node, var):
    f = polyfrac(node, var)
    return None if f is None else ptrim(list(f[1]))

MAXSHARE = 8

def ratshare(node, var):
    # do the additive terms of node share denominator factors?  (a term with no
    # denominator counts as sharing: x + 1/x becomes one fraction)
    terms = []
    _addterms(node, 1, terms)
    if len(terms) > MAXSHARE:
        return False
    dens = []
    for t, s in terms:
        d = _denpoly(t, var)
        if d is None:
            return False
        if len(d) < 2:
            return True
        dens.append(d)
    i = 0
    while i < len(dens):
        j = i + 1
        while j < len(dens):
            g = pgcd(dens[i], dens[j])
            if g is not None and len(g) > 1:
                return True
            j += 1
        i += 1
    return False
