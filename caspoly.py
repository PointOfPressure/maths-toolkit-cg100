# caspoly.py - exact rational polynomial algebra for the CAS: collect like
# terms, expand brackets, factorise, and split a rational function into partial
# fractions. caseng.simplify only ever applied local rules, so it folded
# constants and identities but would not gather 3x + 2x, multiply out (x+1)^3,
# or take (2x-1)(x+4) apart again.
#
# Coefficients are exact rationals held as (numerator, denominator) pairs with a
# positive denominator, reduced. Floats are only used when a coefficient cannot
# be written exactly, and then the whole route is abandoned rather than silently
# rounding - a partial fraction decomposition that is right to 6 dp is not an
# answer a student can write down.
#
# Recursion here is on expression nesting, never on the length of a list, so it
# stays inside the handheld's shallow call stack. Polynomials are lists indexed
# by power and every loop over one is iterative.
import caseng

# ---------------------------------------------------------------- rationals --
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
    # the integer value if this rational is one, else None
    return a[0] if a[1] == 1 else None

def ratof(node):
    # exact rational value of a numeric subtree, or None if it is not one.
    # A float is accepted only when it is a whole number: 0.5 is exact in
    # binary but 0.1 is not, and guessing which is which is how a CAS starts
    # printing 3333333333/10000000000.
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

# ----------------------------------------------------------- term structure --
# A term is (coefficient, [(basekey, basetree, exponent), ...]) with the factor
# list sorted by basekey so two terms that are the same product compare equal.
MAXPOW = 12   # (a+b)^n above this is left alone; the handheld has to stay quick

def _factors(node, coef, facs):
    # split node into a rational coefficient and a list of base**exponent
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
            # (k*x)^3 has to send k^3 to the coefficient, not leave it inside
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
    # (coefficient, sorted factor list) or None if the coefficients are not exact
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

def term_node(coef, facs):
    if not facs:
        return ratnode(coef)
    body = None
    for key, base, e in facs:
        if e == 1:
            f = base
        else:
            f = ('^', base, ('n', e)) if e > 0 else ('^', base, ('neg', ('n', -e)))
        body = f if body is None else ('*', body, f)
    if coef == R1:
        return body
    if coef == (-1, 1):
        return ('neg', body)
    if coef[1] == 1:
        return ('*', ('n', coef[0]), body)
    return ('/', ('*', ('n', coef[0]), body), ('n', coef[1]))

# ------------------------------------------------------------------- expand --
def _addterms(node, sign, out):
    # flatten a sum/difference chain into signed leaves, iteratively enough that
    # a hundred-term sum cannot outrun the call stack
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
    # (sum of terms) * (sum of terms), distributed
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
    # multiply out brackets, then gather like terms
    return collect(_ex(node))

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
        # (p+q)/c splits only over a constant denominator; over a general one it
        # would not be an expansion, just a longer expression
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

# ------------------------------------------------------------------ collect --
def collect(node):
    # gather like terms: 3x + 2x -> 5x, x + x^2 - x -> x^2.
    # Returns the input unchanged if any coefficient is not an exact rational,
    # so nothing is silently rounded.
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
    # Highest degree first; among equal degrees a positive term leads, so the
    # answer reads "x-atan(x)" rather than "-atan(x)+x". Alphabetical after
    # that, so the same expression always prints the same way.
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
    return caseng.simplify(out)

# --------------------------------------------------------------- polynomials --
# A polynomial is a list of rationals indexed by power: [c0, c1, c2] is
# c0 + c1 x + c2 x^2. The empty list is the zero polynomial.
def ptrim(p):
    while p and rzero(p[-1]):
        p.pop()
    return p

def poly(node, var):
    # coefficient list for a polynomial in var, else None
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
    # a constant subtree in some other form (pi, sqrt(2)) is not exact here
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
    # long division: a = q*b + r with deg(r) < deg(b)
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

def ptree(p, var):
    # coefficient list back to an expression tree, highest power first
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
                if c == R1:
                    piece = power
                elif c == (-1, 1):
                    piece = ('neg', power)
                elif c[1] == 1:
                    piece = ('*', ('n', c[0]), power)
                else:
                    piece = ('/', ('*', ('n', c[0]), power), ('n', c[1]))
            if node is None:
                node = piece
            elif c[0] < 0:
                pos = (-c[0], c[1])
                if i == 0:
                    node = ('-', node, ratnode(pos))
                else:
                    power = ('v', var) if i == 1 else ('^', ('v', var), ('n', i))
                    if pos == R1:
                        node = ('-', node, power)
                    elif pos[1] == 1:
                        node = ('-', node, ('*', ('n', pos[0]), power))
                    else:
                        node = ('-', node, ('/', ('*', ('n', pos[0]), power), ('n', pos[1])))
            else:
                node = ('+', node, piece)
        i -= 1
    return ('n', 0) if node is None else node

# ------------------------------------------------------------- factorisation --
def pcontent(p):
    # the rational g with p = g * (primitive integer polynomial)
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
    # every rational root of p, by the rational root theorem, with multiplicity
    p = ptrim(list(p))
    out = []
    if len(p) < 2:
        return out
    while len(p) >= 2 and rzero(p[0]):
        out.append(R0)                     # x is a factor
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
    # Horner, exactly
    acc = R0
    i = len(p) - 1
    while i >= 0:
        acc = radd(rmul(acc, r), p[i])
        i -= 1
    return acc

def pfactors(p, var):
    # p -> (leading rational, [(factor coefficient list, multiplicity), ...])
    # Factors are monic linear (x - r) or irreducible monic quadratic. Anything
    # that will not split that far is returned whole.
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
        # what is left has no rational root; keep quadratics whole and give up
        # gracefully on anything higher rather than inventing a factorisation
        out.append((p, 1))
    return (lead, out)

def factor(node, var='x'):
    # factorise a polynomial; None if it is not one, or will not factor further
    p = poly(node, var)
    if p is None or len(p) < 2:
        return None
    lead, fs = pfactors(p, var)
    if not fs:
        return None
    # a single factor of full degree means nothing was taken out
    if len(fs) == 1 and fs[0][1] == 1 and len(fs[0][0]) == len(p):
        return None
    # Clear denominators out of each factor and push them into the leading
    # coefficient, so 2x^2+7x+3 factorises as (2x+1)(x+3) - what a student
    # writes - rather than the equally true but useless 2(x+1/2)(x+3).
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

# --------------------------------------------------------- partial fractions --
def solve_rat(A, b):
    # Gauss-Jordan over the rationals; None if singular
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
    # Split N(x)/D(x) into a polynomial part plus partial fractions.
    # Returns (polynomial part tree or None, [(numerator tree, factor tree,
    # power), ...]) or None if the split is not available exactly.
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
            return None          # a cubic or worse we could not split: no answer
    # unknowns: for factor f of degree d and multiplicity m, d*m of them
    cols = []                    # (factor, power, degree offset)
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
    # basis_j = (D/lead) / f^i * x^k, so sum(c_j basis_j) == rem/lead
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
            # gather the two halves of a quadratic numerator (Bx + C) as one
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
