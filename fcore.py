# OCR B (MEI) Further Maths H645, Core Pure (Y420): proof, complex numbers,
# matrices and transformations, vectors and 3-D, roots of polynomials, series.
# Calculus, polar, hyperbolic functions and differential equations are in fcalc.
import math
import caslex
import caseng
import cascalc
import caspoly
import casutil

_f = casutil.fmt
_w = casutil.w
_warn = casutil.warn
_m = casutil.m
_fv = casutil.fmtv
_wn = casutil.warn
PI = math.pi

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

def _cx(v):
    return complex(v) if not isinstance(v, complex) else v

def _abs(v):
    return caseng._cabs(_cx(v))

def _arg(v):
    return caseng._carg(_cx(v))

def _at(tree, name, val):
    # value of a tree in one named variable, or None
    try:
        v = caseng.evalf(tree, 0.0, False, {name: val})
    except Exception:
        return None
    if isinstance(v, complex):
        return None
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

def _polytree(co, var):
    # co low->high, numeric; builds a tidy tree, printer handles exact forms
    node = None
    i = len(co) - 1
    while i >= 0:
        c = casutil.clean(co[i])
        if c == 0:
            i -= 1
            continue
        neg = (not isinstance(c, complex)) and c < 0
        mag = -c if neg else c
        if i == 0:
            piece = ('n', mag)
        else:
            pw = ('v', var) if i == 1 else ('^', ('v', var), ('n', i))
            piece = pw if mag == 1 else ('*', ('n', mag), pw)
        if node is None:
            node = ('neg', piece) if neg else piece
        else:
            node = ('-', node, piece) if neg else ('+', node, piece)
        i -= 1
    return ('n', 0) if node is None else node

def _isint(v):
    return (not isinstance(v, complex)) and v == int(v)

def _ratpoly(co):
    # co low->high numeric -> caspoly rational list, or None
    out = []
    for c in co:
        if isinstance(c, complex) or not _isint(c):
            return None
        out.append((int(c), 1))
    return caspoly.ptrim(out)

def _peval(co, z):
    # co high->low, Horner in complex
    acc = complex(0, 0)
    i = 0
    while i < len(co):
        acc = acc * z + _cx(co[i])
        i += 1
    return acc

def _droots(co):
    # Durand-Kerner: all roots of co (high->low), complex
    while co and co[0] == 0:
        co = co[1:]
    n = len(co) - 1
    if n < 1:
        return []
    a = [_cx(c) / _cx(co[0]) for c in co]
    z = []
    p = complex(1.0, 0.0)
    s = complex(0.4, 0.9)
    k = 0
    while k < n:
        z.append(p)
        p = p * s
        k += 1
    it = 0
    while it < 300:
        moved = 0
        i = 0
        while i < n:
            den = complex(1.0, 0.0)
            j = 0
            while j < n:
                if j != i:
                    den = den * (z[i] - z[j])
                j += 1
            if den == 0:
                i += 1
                continue
            d = _peval(a, z[i]) / den
            z[i] = z[i] - d
            if caseng._cabs(d) > 1e-15:
                moved = 1
            i += 1
        if not moved:
            break
        it += 1
    return z

def _cleanroot(v):
    v = casutil.clean(v)
    if isinstance(v, complex):
        re = v.real
        im = v.imag
        nr = float(int(re + 0.5) if re >= 0 else -int(-re + 0.5))
        ni = float(int(im + 0.5) if im >= 0 else -int(-im + 0.5))
        if abs(re - nr) < 1e-9 and abs(im - ni) < 1e-9:
            return casutil.clean(complex(nr, ni))
        return v
    n = float(int(v + 0.5) if v >= 0 else -int(-v + 0.5))
    if abs(v - n) < 1e-9:
        return casutil.clean(n)
    return v

def _roots(co):
    # all roots of a polynomial, co high->low. Rational roots exactly.
    while co and co[0] == 0:
        co = co[1:]
    if len(co) < 2:
        raise ValueError('leading coefficient is 0')
    lo = []
    i = len(co) - 1
    while i >= 0:
        lo.append(co[i])
        i -= 1
    rp = _ratpoly(lo)
    out = []
    if rp is not None:
        for r in caspoly.roots_rational(rp):
            qr = caspoly.pdivmod(rp, [caspoly.rneg(r), caspoly.R1])
            if qr is None or qr[1]:
                continue
            rp = qr[0]
            out.append(casutil.clean(r[0] * 1.0 / r[1]))
        if len(rp) < 2:
            return out
        rest = []
        i = len(rp) - 1
        while i >= 0:
            rest.append(rp[i][0] * 1.0 / rp[i][1])
            i -= 1
        co = rest
    if len(co) == 3:
        a, b, c = co[0], co[1], co[2]
        d = b * b - 4.0 * a * c
        if d >= 0:
            s = math.sqrt(d)
            out.append(_cleanroot((-b + s) / (2.0 * a)))
            out.append(_cleanroot((-b - s) / (2.0 * a)))
        else:
            s = math.sqrt(-d)
            out.append(_cleanroot(complex(-b / (2.0 * a), s / (2.0 * a))))
            out.append(_cleanroot(complex(-b / (2.0 * a), -s / (2.0 * a))))
        return out
    for z in _droots(co):
        out.append(_cleanroot(z))
    return out

def _sortroots(rs):
    reals = []
    cxs = []
    for r in rs:
        if isinstance(r, complex):
            cxs.append(r)
        else:
            reals.append(r)
    reals.sort()
    return reals + cxs

# ---- matrices ---------------------------------------------------------------

def _mm(A, B):
    out = []
    i = 0
    while i < len(A):
        row = []
        j = 0
        while j < len(B[0]):
            s = 0
            k = 0
            while k < len(B):
                s = s + A[i][k] * B[k][j]
                k += 1
            row.append(casutil.clean(s))
            j += 1
        out.append(row)
        i += 1
    return out

def _mpow(A, n):
    r = _ident(len(A))
    i = 0
    while i < n:
        r = _mm(r, A)
        i += 1
    return r

def _ident(n):
    out = []
    i = 0
    while i < n:
        out.append([1 if j == i else 0 for j in range(n)])
        i += 1
    return out

def _det2(A):
    return casutil.clean(A[0][0] * A[1][1] - A[0][1] * A[1][0])

def _det3(A):
    return casutil.clean(
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))

def _inv2(A):
    d = _det2(A)
    if d == 0:
        return None
    return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]

def _inv3(A):
    d = _det3(A)
    if d == 0:
        return None
    co = []
    i = 0
    while i < 3:
        row = []
        j = 0
        while j < 3:
            r = [0, 1, 2]
            r.remove(i)
            c = [0, 1, 2]
            c.remove(j)
            mn = (A[r[0]][c[0]] * A[r[1]][c[1]] - A[r[0]][c[1]] * A[r[1]][c[0]])
            row.append(mn if (i + j) % 2 == 0 else -mn)
            j += 1
        co.append(row)
        i += 1
    out = []
    i = 0
    while i < 3:
        out.append([casutil.clean(co[j][i] / d) for j in range(3)])
        i += 1
    return out

def _mlines(name, A):
    rows = casutil.fmtm(A)
    out = []
    i = 0
    while i < len(rows):
        out.append((name + ' = ' if i == 0 else ' ' * (len(name) + 3)) + rows[i])
        i += 1
    return out

def _scale(v):
    # scale a vector to the tidiest equivalent: small integers if possible
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
        return [casutil.clean(c) for c in v]
    out = []
    for c in v:
        t = c * best
        out.append(int(t + 0.5) if t >= 0 else -int(-t + 0.5))
    g = 0
    for c in out:
        g = casutil.gcd(g, int(c))
    if g > 1:
        out = [int(c) // g for c in out]
    lead = 0
    for c in out:
        if c != 0:
            lead = c
            break
    if lead < 0:
        out = [-c for c in out]
    return out

# ---- P  Proof ---------------------------------------------------------------

def _intat(tree, name, i):
    try:
        v = caseng.evalf(tree, 0, False, {name: i})
    except Exception:
        return None
    if isinstance(v, complex):
        return None
    if isinstance(v, int):
        return v
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if abs(v - n) > 1e-6 * (1.0 + abs(v)):
        return None
    return n

def _onlyvar(tree, var, what):
    for v in caseng.vars_in(tree):
        if v != var:
            raise ValueError(what + ': type it in ' + var)

def _shift(tree, var, k):
    return caseng.subst(tree, var, ('+', ('v', var), ('n', k)))

def _samepoly(a, b, var):
    try:
        pa = caspoly.poly(caspoly.expand(a), var)
        pb = caspoly.poly(caspoly.expand(b), var)
    except Exception:
        return None
    if pa is None or pb is None:
        return None
    return caspoly.ptrim(pa) == caspoly.ptrim(pb)

def t_ind_sum(u, S):
    u = caseng.subst(u, 'r', ('v', 'n'))
    _onlyvar(u, 'n', 'u(r)')
    _onlyvar(S, 'n', 'S(n)')
    u1 = _at(u, 'n', 1.0)
    s1 = _at(S, 'n', 1.0)
    if u1 is None or s1 is None:
        raise ValueError('cannot evaluate at n = 1')
    base = abs(u1 - s1) <= 1e-9 * (1.0 + abs(s1))
    lines = []
    if not base:
        lines.append('Base case fails at n = 1')
        lines.append(_w('S(1) = ' + _f(s1) + ',  u(1) = ' + _f(u1)))
        lines.append(_warn('the claimed S(n) is wrong'))
        return lines
    dif = ('-', _shift(S, 'n', 1), S)
    want = _shift(u, 'n', 1)
    same = _samepoly(dif, want, 'n')
    how = 'exactly'
    if same is None:
        how = 'at n = 1..10'
        same = True
        i = 1
        while i <= 10:
            a = _at(dif, 'n', float(i))
            b = _at(want, 'n', float(i))
            if a is None or b is None:
                same = False
                break
            if abs(a - b) > 1e-7 * (1.0 + abs(b)):
                same = False
                break
            i += 1
    if same:
        lines.append('Proved for all n >= 1')
    else:
        lines.append('Inductive step fails')
    lines.append(_w('S(1) = ' + _f(s1) + ' = u(1), base case holds'))
    ds = caseng.tostr(cascalc.tidy(caspoly.expand(dif)))
    ws = caseng.tostr(cascalc.tidy(caspoly.expand(want)))
    lines.append(_w('S(k+1)-S(k) = ' + ds[:38]))
    lines.append(_w('u(k+1)      = ' + ws[:38]))
    if same:
        lines.append(_w('equal ' + how + ', so the step holds'))
    else:
        lines.append(_warn('S(k+1)-S(k) is not u(k+1)'))
    return lines

def t_ind_div(f, k, mm):
    _onlyvar(f, 'n', 'f(n)')
    k = _iv(k, 'k', 2, 1000000000)
    vals = []
    i = 1
    while i <= 12:
        v = _intat(f, 'n', i)
        if v is None:
            raise ValueError('f(n) is not a whole number')
        vals.append(v)
        i += 1
    bad = 0
    i = 0
    while i < 12:
        if vals[i] % k != 0:
            bad = i + 1
            break
        i += 1
    if bad:
        return ['Not divisible: n = ' + str(bad),
                _w('f(' + str(bad) + ') = ' + str(vals[bad - 1]) + ', remainder ' +
                   str(vals[bad - 1] % k)),
                _warn('one counterexample disproves it')]
    cand = []
    if mm is None:
        j = 1
        while j <= 12:
            cand.append(j)
            cand.append(-j)
            j += 1
    else:
        cand = [_iv(mm, 'm', -1000, 1000)]
    use = None
    for m in cand:
        ok = True
        i = 1
        while i <= 8:
            a = _intat(f, 'n', i + 1)
            b = _intat(f, 'n', i)
            if a is None or b is None or (a - m * b) % k != 0:
                ok = False
                break
            i += 1
        if ok:
            use = m
            break
    lines = []
    if use is None:
        lines.append('True for n = 1..12')
        lines.append(_warn('no m makes f(k+1)-m f(k) work'))
        lines.append(_w('f(1..4) = ' + ', '.join([str(v) for v in vals[:4]])))
        return lines
    lines.append(str(k) + ' divides f(n): proved')
    lines.append(_w('f(1..4) = ' + ', '.join([str(v) for v in vals[:4]])))
    ms = '' if use == 1 else ('-' if use == -1 else str(use) + ' ')
    lines.append(_w('use f(k+1) = ' + ms + 'f(k) + d, d a multiple of ' + str(k)))
    ds = []
    i = 1
    while i <= 4:
        ds.append(str(_intat(f, 'n', i + 1) - use * _intat(f, 'n', i)))
        i += 1
    lines.append(_w('d at k=1..4: ' + ', '.join(ds)))
    lines.append(_w('both terms divide by ' + str(k) + ', so f(k+1) does'))
    return lines

def t_ind_mpow(A, p, q, r, s):
    F = [[p, q], [r, s]]
    i = 0
    while i < 2:
        j = 0
        while j < 2:
            _onlyvar(F[i][j], 'n', 'entry')
            j += 1
        i += 1
    fail = 0
    n = 1
    while n <= 6:
        P = _mpow(A, n)
        i = 0
        while i < 2 and not fail:
            j = 0
            while j < 2:
                v = _at(F[i][j], 'n', float(n))
                if v is None or abs(v - P[i][j]) > 1e-7 * (1.0 + abs(P[i][j])):
                    fail = n
                    break
                j += 1
            i += 1
        if fail:
            break
        n += 1
    lines = []
    if fail == 1:
        lines.append('Base case fails at n = 1')
    elif fail:
        lines.append('Fails at n = ' + str(fail))
    else:
        lines.append('Proved for all n >= 1')
    for ln in _mlines('M^2', _mpow(A, 2)):
        lines.append(_w(ln))
    for ln in _mlines('M^3', _mpow(A, 3)):
        lines.append(_w(ln))
    if fail:
        lines.append(_warn('the claimed M^n is wrong'))
    else:
        lines.append(_w('checked n = 1..6; step is M^(k+1) = M M^k'))
    return lines

def _envat(tree, env):
    # value of a tree with several named variables, or None
    try:
        v = caseng.evalf(tree, 0.0, False, env)
    except Exception:
        return None
    if isinstance(v, complex):
        return None
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

def _iszero(t):
    return t[0] == 'n' and not isinstance(t[1], complex) and t[1] == 0

def t_ind_rec(f, u1, g):
    # Pp4: u(n+1) = f(u(n), n), u(1) = u1; claimed u(n) = g(n)
    for v in caseng.vars_in(f):
        if v != 'u' and v != 'n':
            raise ValueError('f: type it in u (and n)')
    _onlyvar(g, 'n', 'g(n)')
    g1 = _at(g, 'n', 1.0)
    if g1 is None:
        raise ValueError('cannot evaluate g(1)')
    if abs(g1 - u1) > 1e-9 * (1.0 + abs(u1)):
        return ['Base case fails at n = 1',
                _w('g(1) = ' + _f(g1) + ',  u1 = ' + _f(u1)),
                _warn('the claimed formula is wrong')]
    seq = [u1]
    i = 1
    while i < 6:
        nx = _envat(f, {'u': seq[i - 1], 'n': float(i)})
        if nx is None:
            raise ValueError('f is undefined at n = ' + str(i))
        seq.append(nx)
        i += 1
    lhs = _shift(g, 'n', 1)
    rhs = caseng.subst(f, 'u', g)
    how = None
    same = False
    try:
        if _iszero(caseng.simplify(('-', lhs, rhs))):
            same = True
            how = 'exactly'
    except Exception:
        pass
    if not same:
        sp = _samepoly(lhs, rhs, 'n')
        if sp is not None:
            same = sp
            how = 'exactly'
    if how is None:
        how = 'at k = 1..10'
        same = True
        k = 1
        while k <= 10:
            a = _at(lhs, 'n', float(k))
            b = _at(rhs, 'n', float(k))
            if a is None or b is None or abs(a - b) > 1e-7 * (1.0 + abs(b)):
                same = False
                break
            k += 1
    if not same:
        head = 'Inductive step fails'
    elif how == 'exactly':
        head = 'Proved for all n >= 1'
    else:
        head = 'Step holds at k = 1..10'
    lines = [head]
    lines.append(_w('g(1) = ' + _f(g1) + ' = u1, base case holds'))
    lines.append(_w('assume u(k) = g(k); then u(k+1) = f(g(k), k)'))
    lines.append(_w('need f(g(k), k) = g(k+1): ' +
                    ('true ' + how if same else 'false')))
    lines.append(_w('u1..u6 = ' + ', '.join([_f(v) for v in seq])))
    if not same:
        k = 1
        while k <= 6:
            gv = _at(g, 'n', float(k))
            if gv is None or abs(gv - seq[k - 1]) > 1e-7 * (1.0 + abs(gv)):
                lines.append(_warn('g(' + str(k) + ') = ' + ('undefined' if gv is None
                                                             else _f(gv)) +
                                   ' but u' + str(k) + ' = ' + _f(seq[k - 1])))
                break
            k += 1
    elif how != 'exactly':
        lines.append(_warn('checked numerically: show the algebra'))
    return lines

def t_ind_dm(theta, n):
    # Pp5: (cos t + i sin t)^n = cos nt + i sin nt, by induction
    n = _iv(n, 'n', -12, 12)
    if n == 0:
        raise ValueError('n must not be 0')
    z = complex(math.cos(theta), math.sin(theta))
    step = z if n > 0 else complex(z.real, -z.imag)
    p = complex(1.0, 0.0)
    worst = 0.0
    rows = []
    k = 1
    while k <= abs(n):
        p = p * step
        kk = k if n > 0 else -k
        q = complex(math.cos(kk * theta), math.sin(kk * theta))
        d = caseng._cabs(p - q)
        if d > worst:
            worst = d
        if k <= 4 or k == abs(n):
            rows.append(_w('n = ' + str(kk) + ': ' + _f(_rect(1.0, kk * theta))))
        k += 1
    ok = worst < 1e-9
    lines = ['z^' + str(n) + ' = ' + _f(_rect(1.0, n * theta)),
             'agrees with cos nt + i sin nt' if ok else 'does not agree',
             _w('z = cos t + i sin t, t = ' + _f(theta))]
    if n > 0:
        lines.append(_w('base: n = 1 is cos t + i sin t itself'))
        lines.append(_w('step: (cos kt + i sin kt)(cos t + i sin t)'))
        lines.append(_w(' = cos kt cos t - sin kt sin t'))
        lines.append(_w('   + i(sin kt cos t + cos kt sin t)'))
        lines.append(_w(' = cos(k+1)t + i sin(k+1)t, compound angles'))
    else:
        lines.append(_w('n < 0: put n = -m, m > 0'))
        lines.append(_w('z^-m = 1/(cos mt + i sin mt)'))
        lines.append(_w(' = cos mt - i sin mt = cos(-mt) + i sin(-mt)'))
    for r in rows:
        lines.append(r)
    return lines

def _isprime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def _smallfactor(n):
    if n % 2 == 0:
        return 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return i
        i += 2
    return n

def _range(a, b):
    a = _iv(a, 'a', -100000, 100000)
    b = _iv(b, 'b', a, a + 5000)
    return a, b

def t_cx_prime(f, a, b):
    # disprove "f(n) is always prime" by a counterexample
    _onlyvar(f, 'n', 'f(n)')
    a, b = _range(a, b)
    n = a
    while n <= b:
        v = _intat(f, 'n', n)
        if v is None:
            return ['Counterexample: n = ' + str(n),
                    'f(' + str(n) + ') is not a whole number',
                    _w('one counterexample disproves the claim')]
        if v > 1e10:
            return ['No counterexample, n = ' + str(a) + '..' + str(n - 1),
                    _warn('f(' + str(n) + ') is too big to test'),
                    _warn('checking cases is not a proof')]
        if not _isprime(v):
            out = ['Counterexample: n = ' + str(n)]
            if v < 2:
                out.append('f(' + str(n) + ') = ' + str(v) + ', not prime')
            else:
                p = _smallfactor(v)
                out.append('f(' + str(n) + ') = ' + str(v) + ' = ' + str(p) +
                           ' x ' + str(v // p))
            out.append(_w('one counterexample disproves the claim'))
            return out
        n += 1
    return ['No counterexample, n = ' + str(a) + '..' + str(n - 1),
            _warn('checking cases is not a proof'),
            _w('every f(n) in the range is prime')]

def t_cx_ineq(f, g, a, b):
    # disprove "f(n) > g(n) for all n" by a counterexample
    _onlyvar(f, 'n', 'f(n)')
    _onlyvar(g, 'n', 'g(n)')
    a, b = _range(a, b)
    n = a
    while n <= b:
        fv = _at(f, 'n', float(n))
        gv = _at(g, 'n', float(n))
        if fv is None or gv is None:
            return ['Counterexample: n = ' + str(n),
                    'f or g is undefined there',
                    _w('one counterexample disproves the claim')]
        if not fv > gv:
            return ['Counterexample: n = ' + str(n),
                    'f = ' + _f(fv) + ', g = ' + _f(gv),
                    _w('f(n) > g(n) is false here, so the claim'),
                    _w('"f(n) > g(n) for all n" is disproved')]
        n += 1
    return ['No counterexample, n = ' + str(a) + '..' + str(b),
            _warn('checking cases is not a proof'),
            _w('f(n) > g(n) at every n in the range')]

# ---- J  Complex numbers -----------------------------------------------------

def _pol(z):
    return (_abs(z), _arg(z))

def _snap(x):
    n = int(x + 0.5) if x >= 0 else -int(-x + 0.5)
    if abs(x - n) < 1e-11 * (1.0 + abs(x)):
        return float(n)
    return x

def _rect(r, th):
    return casutil.clean(complex(_snap(r * math.cos(th)), _snap(r * math.sin(th))))

def _expform(r, th):
    return _f(r) + 'e^(i ' + _f(th) + ')'

def _trigform(r, th):
    return _f(r) + '(cos ' + _f(th) + ' + i sin ' + _f(th) + ')'

def t_zw(z, w):
    lines = ['z+w = ' + _f(z + w), 'z-w = ' + _f(z - w), 'zw = ' + _f(z * w)]
    if w == 0:
        lines.append(_warn('z/w undefined: w = 0'))
    else:
        lines.append('z/w = ' + _f(z / w))
        cw = complex(_cx(w).real, -_cx(w).imag)
        lines.append(_w('z/w = z*conj(w)/|w|^2, |w|^2 = ' + _f(_abs(w) ** 2)))
        lines.append(_w('z*conj(w) = ' + _f(z * cw)))
    lines.append(_w('Re(zw) = ' + _f(_cx(z * w).real) +
                    ', Im(zw) = ' + _f(_cx(z * w).imag)))
    return lines

def t_modarg(z):
    if z == 0:
        raise ValueError('arg(0) is undefined')
    r, th = _pol(z)
    return ['|z| = ' + _f(r),
            'arg z = ' + _f(th) + ' rad',
            'arg z = ' + _f(th * 180.0 / PI) + ' deg',
            'z = ' + _trigform(r, th),
            'z = ' + _expform(r, th),
            'conj z = ' + _f(complex(_cx(z).real, -_cx(z).imag)),
            _w('|z|^2 = z conj(z) = ' + _f(r * r)),
            _w('arg from atan2(Im, Re), -pi < arg <= pi')]

def t_frommodarg(r, theta):
    if r < 0:
        raise ValueError('r must be >= 0')
    z = _rect(r, theta)
    return ['z = ' + _f(z),
            _w('x = r cos t = ' + _f(r) + ' x ' + _f(math.cos(theta)) +
               ' = ' + _f(_cx(z).real)),
            _w('y = r sin t = ' + _f(r) + ' x ' + _f(math.sin(theta)) +
               ' = ' + _f(_cx(z).imag)),
            _w('theta = ' + _f(theta * 180.0 / PI) + ' deg')]

def _princ(th):
    while th > PI + 1e-12:
        th -= 2.0 * PI
    while th <= -PI - 1e-12:
        th += 2.0 * PI
    return th

def t_mamul(r1, t1, r2, t2):
    if r1 < 0 or r2 < 0:
        raise ValueError('moduli must be >= 0')
    lines = ['zw: r = ' + _f(r1 * r2) + ', arg = ' + _f(_princ(t1 + t2)),
             'zw = ' + _f(_rect(r1 * r2, t1 + t2))]
    if r2 == 0:
        lines.append(_warn('z/w undefined: |w| = 0'))
    else:
        lines.append('z/w: r = ' + _f(r1 / r2) + ', arg = ' + _f(_princ(t1 - t2)))
        lines.append('z/w = ' + _f(_rect(r1 / r2, t1 - t2)))
    lines.append(_w('multiply moduli, add arguments'))
    lines.append(_w('arg sum ' + _f(t1 + t2) + ' -> ' + _f(_princ(t1 + t2)) +
                    ' in (-pi, pi]'))
    return lines

def t_zpow(z, n):
    n = _iv(n, 'n', -64, 64)
    if z == 0:
        raise ValueError('z must not be 0')
    r, th = _pol(z)
    rn = r ** n
    lines = ['z^' + str(n) + ' = ' + _f(_rect(rn, n * th)),
             '|z^n| = ' + _f(rn),
             'arg = ' + _f(_princ(n * th)) + ' rad']
    lines.append(_w('de Moivre: z^n = r^n(cos nt + i sin nt)'))
    lines.append(_w('r = ' + _f(r) + ', t = ' + _f(th) + ', nt = ' + _f(n * th)))
    return lines

def _argand(pts, title):
    import plot
    plot.run(pts, kind='points', title=title)

def t_nroots(z, n):
    n = _iv(n, 'n', 2, 16)
    if z == 0:
        raise ValueError('z must not be 0')
    r, th = _pol(z)
    rr = r ** (1.0 / n)
    out = []
    pts = []
    k = 0
    while k < n:
        ang = (th + 2.0 * PI * k) / n
        v = _rect(rr, ang)
        out.append('w' + str(k) + ' = ' + _f(v))
        pts.append((_cx(v).real, _cx(v).imag))
        k += 1
    _argand(pts, 'roots of ' + _f(z))
    lines = out
    lines.append(_w('|w| = ' + _f(r) + '^(1/' + str(n) + ') = ' + _f(rr)))
    lines.append(_w('args (' + _f(th) + ' + 2pi k)/' + str(n) + ', k = 0..' + str(n - 1)))
    lines.append(_w('they are a regular ' + str(n) + '-gon, sum = 0'))
    return lines

def t_unity(n):
    n = _iv(n, 'n', 2, 16)
    out = []
    pts = []
    k = 0
    while k < n:
        ang = 2.0 * PI * k / n
        v = _rect(1.0, ang)
        out.append('w^' + str(k) + ' = ' + _f(v))
        pts.append((_cx(v).real, _cx(v).imag))
        k += 1
    _argand(pts, str(n) + 'th roots of 1')
    out.append(_w('w = e^(2pi i/' + str(n) + '), args 2pi k/' + str(n)))
    out.append(_w('1 + w + ... + w^' + str(n - 1) + ' = 0'))
    out.append(_w('regular ' + str(n) + '-gon on the unit circle'))
    return out

def _seg(p, q):
    # a straight segment p -> q as a parametric curve for plot.run
    px = _cx(p).real
    py = _cx(p).imag
    dx = _cx(q).real - px
    dy = _cx(q).imag - py
    X = ('v', 'x')
    return (('+', ('n', px), ('*', ('n', dx), X)),
            ('+', ('n', py), ('*', ('n', dy), X)), 0.0, 1.0)

def _drawsegs(segs, title):
    import plot
    plot.run(segs, kind='param', title=title)

def t_argops(z, w):
    # j10: sum, difference, product and quotient on an Argand diagram
    s = casutil.clean(z + w)
    d = casutil.clean(z - w)
    p = casutil.clean(z * w)
    segs = [_seg(0, z), _seg(0, w), _seg(z, s), _seg(w, s), _seg(w, z)]
    if p != 0:
        segs.append(_seg(0, p))
    _drawsegs(segs, 'O, z, w, z+w and zw')
    lines = ['z+w = ' + _f(s), 'z-w = ' + _f(d), 'zw = ' + _f(p)]
    if w != 0:
        lines.append('z/w = ' + _f(casutil.clean(z / w)))
    lines.append(_w('z+w: 4th corner of parallelogram O, z, w'))
    lines.append(_w('z-w: the vector from w to z'))
    if z != 0 and w != 0:
        lines.append(_w('|zw| = |z||w| = ' + _f(_abs(z)) + ' x ' + _f(_abs(w)) +
                        ' = ' + _f(_abs(p))))
        lines.append(_w('arg zw = arg z + arg w = ' + _f(_princ(_arg(z) + _arg(w)))))
        lines.append(_w('arg z/w = arg z - arg w = ' + _f(_princ(_arg(z) - _arg(w)))))
        lines.append(_w('zw: z scaled by |w| and turned by arg w'))
    return lines

def _tidyz(z, scale):
    # drop rounding dust relative to the size of the figure
    z = _cx(z)
    re = z.real
    im = z.imag
    if abs(re) < 1e-12 * scale:
        re = 0.0
    if abs(im) < 1e-12 * scale:
        im = 0.0
    return casutil.clean(complex(_snap(re), _snap(im)))

def _polylines(c, v0, n, title):
    r = _abs(_cx(v0) - _cx(c))
    if r < 1e-12:
        raise ValueError('the points coincide')
    vs = []
    k = 0
    while k < n:
        ang = _arg(_cx(v0) - _cx(c)) + 2.0 * PI * k / n
        vs.append(_tidyz(_cx(c) + _rect(r, ang), 1.0 + r + _abs(c)))
        k += 1
    segs = []
    k = 0
    while k < n:
        segs.append(_seg(vs[k], vs[(k + 1) % n]))
        k += 1
    _drawsegs(segs, title)
    out = []
    k = 0
    while k < n:
        out.append('v' + str(k + 1) + ' = ' + _f(vs[k]))
        k += 1
    side = 2.0 * r * math.sin(PI / n)
    out.append('side = ' + _f(casutil.clean(_snap(side))))
    out.append('area = ' + _f(casutil.clean(_snap(0.5 * n * r * r *
                                                  math.sin(2.0 * PI / n)))))
    out.append(_w('centre ' + _f(c) + ', radius ' + _f(r)))
    out.append(_w('each vertex: multiply (v - c) by'))
    out.append(_w('e^(2pi i/' + str(n) + ') = ' + _f(_rect(1.0, 2.0 * PI / n))))
    out.append(_w('vertices = c + (v1 - c) x nth roots of 1'))
    return out

def t_poly_centre(z1, z2, n):
    # j19/j20: regular n-gon from its centre z1 and one vertex z2
    n = _iv(n, 'n', 3, 12)
    return _polylines(z1, z2, n, 'regular ' + str(n) + '-gon')

def t_poly_edge(z1, z2, n):
    # j20: regular n-gon from two adjacent vertices, anticlockwise
    n = _iv(n, 'n', 3, 12)
    if z1 == z2:
        raise ValueError('the points coincide')
    rot = complex(math.cos(2.0 * PI / n), math.sin(2.0 * PI / n))
    c = (_cx(z1) * rot - _cx(z2)) / (rot - 1.0)
    c = _tidyz(c, 1.0 + _abs(z1) + _abs(z2))
    out = _polylines(c, z1, n, 'regular ' + str(n) + '-gon')
    out.insert(0, 'centre = ' + _f(c))
    out.append(_w('z2 - c = (z1 - c) e^(2pi i/n) gives c'))
    return out

def _rootlines(co, name):
    rs = _sortroots(_roots(co))
    out = []
    i = 0
    while i < len(rs):
        out.append(name + str(i + 1) + ' = ' + _f(rs[i]))
        i += 1
    return rs, out

def t_quad(a, b, c):
    if a == 0:
        raise ValueError('a must not be 0')
    d = b * b - 4.0 * a * c
    rs, out = _rootlines([a, b, c], 'z')
    out.append(_w('disc = b^2-4ac = ' + _f(d)))
    if d < 0:
        out.append(_w('roots are a conjugate pair'))
    out.append(_w('sum = -b/a = ' + _f(-b * 1.0 / a) +
                  ', product = c/a = ' + _f(c * 1.0 / a)))
    return out

def _rootres(co, z):
    zz = _cx(z)
    az = caseng._cabs(zz)
    den = 0.0
    for c in co:
        den = den * az + abs(c)
    if den < 1e-12:
        den = 1e-12
    return caseng._cabs(_peval(co, zz)) / den

def _checkroot(co, z, out):
    if _rootres(co, z) > 1e-9:
        out.append(_warn(_f(z) + ' is not a root'))
    else:
        zs = _f(z)
        if ('+' in zs) or ('-' in zs[1:]):
            fac = '(z-(' + zs + '))'
        elif zs[:1] == '-':
            fac = '(z+' + zs[1:] + ')'
        else:
            fac = '(z-' + zs + ')'
        out.append(_w(zs + ' is a root: divide by ' + fac))
        if isinstance(casutil.clean(z), complex):
            re = _cx(z).real
            md = _abs(z)
            q = 'z^2'
            if re:
                q += ('-' if re > 0 else '+') + _f(2 * abs(re)) + 'z'
            out.append(_w('with its conjugate: factor ' + q + '+' + _f(md * md)))

def t_cubic(a, b, c, d, z):
    if a == 0:
        raise ValueError('a must not be 0')
    rs, out = _rootlines([a, b, c, d], 'z')
    if z is not None:
        _checkroot([a, b, c, d], z, out)
    out.append(_w('sum = -b/a = ' + _f(-b * 1.0 / a)))
    out.append(_w('product = -d/a = ' + _f(-d * 1.0 / a)))
    nr = 0
    for r in rs:
        if isinstance(r, complex):
            nr += 1
    if nr:
        out.append(_w('non-real roots come in conjugate pairs'))
    return out

def t_quartic(a, b, c, d, e, z):
    if a == 0:
        raise ValueError('a must not be 0')
    rs, out = _rootlines([a, b, c, d, e], 'z')
    if z is not None:
        _checkroot([a, b, c, d, e], z, out)
    out.append(_w('sum = -b/a = ' + _f(-b * 1.0 / a)))
    out.append(_w('product = e/a = ' + _f(e * 1.0 / a)))
    return out

def t_argand(data):
    if len(data) < 2 or len(data) % 2:
        raise ValueError('give pairs x, y')
    pts = []
    out = []
    i = 0
    while i < len(data):
        z = casutil.clean(complex(data[i], data[i + 1]))
        pts.append((data[i], data[i + 1]))
        out.append('z' + str(i // 2 + 1) + ' = ' + _f(z) + ', |z| = ' + _f(_abs(z)))
        i += 2
    _argand(pts, 'Argand diagram')
    return out

def _circlepts(cx, cy, r):
    pts = []
    i = 0
    while i < 72:
        t = 2.0 * PI * i / 72.0
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        i += 1
    return pts

def t_loc_circle(z1, r):
    if r <= 0:
        raise ValueError('r must be > 0')
    a = _cx(z1).real
    b = _cx(z1).imag
    _argand(_circlepts(a, b, r), '|z-a| = ' + _f(r))
    d = math.sqrt(a * a + b * b)
    return ['circle centre ' + _f(z1) + ' radius ' + _f(r),
            '(x-' + _f(a) + ')^2+(y-' + _f(b) + ')^2 = ' + _f(r * r),
            'greatest |z| = ' + _f(d + r),
            'least |z| = ' + _f(d - r if d > r else 0.0),
            _w('|z-a| = r is the set of points r from a'),
            _w('|a| = ' + _f(d))]

def _off(name, v):
    v = casutil.clean(v)
    if v == 0:
        return name
    return name + ('+' if v < 0 else '-') + _f(-v if v < 0 else v)

def t_loc_halfline(z1, theta):
    a = _cx(z1).real
    b = _cx(z1).imag
    th = _princ(theta)
    import plot
    pts = []
    i = 1
    while i <= 40:
        s = i * 0.25
        pts.append((a + s * math.cos(th), b + s * math.sin(th)))
        i += 1
    plot.run(pts, kind='points', title='arg(z-a) = ' + _f(th))
    lines = ['half-line from ' + _f(z1),
             'at ' + _f(th) + ' rad = ' + _f(th * 180.0 / PI) + ' deg']
    if abs(math.cos(th)) < 1e-12:
        lines.append('x = ' + _f(a) + ', y ' + ('>' if math.sin(th) > 0 else '<') +
                     ' ' + _f(b))
    else:
        mgr = casutil.clean(_snap(math.tan(th)))
        ms = '' if mgr == 1 else ('-' if mgr == -1 else _f(mgr))
        lines.append(_off('y', b) + ' = ' + ms + '(' + _off('x', a) + ')')
        lines.append('only x ' + ('>' if math.cos(th) > 0 else '<') + ' ' + _f(a))
    lines.append(_warn('the point ' + _f(z1) + ' itself is excluded'))
    if abs(math.cos(th)) >= 1e-12:
        lines.append(_w('gradient = tan(' + _f(th) + ')'))
    return lines

def t_loc_bisect(z1, z2):
    if z1 == z2:
        raise ValueError('z1 and z2 are the same point')
    ax = _cx(z1).real
    ay = _cx(z1).imag
    bx = _cx(z2).real
    by = _cx(z2).imag
    mx = (ax + bx) / 2.0
    my = (ay + by) / 2.0
    dx = bx - ax
    dy = by - ay
    lines = ['perp bisector of ' + _f(z1) + ' ' + _f(z2),
             'midpoint (' + _f(mx) + ', ' + _f(my) + ')']
    if abs(dy) < 1e-12:
        lines.append('x = ' + _f(mx))
        pts = [(mx, my - 6.0 + 0.3 * i) for i in range(41)]
    else:
        gr = -dx / dy
        cc = my - gr * mx
        lines.append('y = ' + _f(gr) + 'x + ' + _f(cc))
        lines.append(_w('gradient of z1z2 = ' + (_f(dy / dx) if abs(dx) > 1e-12
                                                 else 'infinite')))
        pts = []
        i = 0
        while i <= 40:
            xx = mx - 6.0 + 0.3 * i
            pts.append((xx, gr * xx + cc))
            i += 1
    lines.append(_w('|z-z1| = |z-z2|: equidistant from both'))
    import plot
    plot.run(pts, kind='points', title='perpendicular bisector')
    return lines

def _joinsigned(terms):
    out = ''
    for sign, piece in terms:
        if out == '':
            out = ('-' + piece) if sign < 0 else piece
        else:
            out += ('-' if sign < 0 else '+') + piece
    return out if out else '0'

def t_multangle(n):
    n = _iv(n, 'n', 2, 6)
    ct = []
    st = []
    k = 0
    while k <= n:
        c = casutil.ncr(n, k)
        body = ''
        if n - k > 0:
            body += 'c^' + str(n - k) if n - k > 1 else 'c'
        if k > 0:
            body += 's^' + str(k) if k > 1 else 's'
        if body == '':
            body = '1'
        piece = (str(c) + body) if c != 1 else body
        mk = k % 4
        if mk == 0:
            ct.append((1, piece))
        elif mk == 1:
            st.append((1, piece))
        elif mk == 2:
            ct.append((-1, piece))
        else:
            st.append((-1, piece))
        k += 1
    return ['cos ' + str(n) + 't = ' + _joinsigned(ct),
            'sin ' + str(n) + 't = ' + _joinsigned(st),
            _w('c = cos t, s = sin t'),
            _w('from (c+is)^' + str(n) + ' = cos ' + str(n) + 't + i sin ' + str(n) + 't'),
            _w('use s^2 = 1-c^2 to get cosines alone')]

def _mulstr(name, terms, den):
    g = den
    for c, mlt in terms:
        g = casutil.gcd(g, c)
    if g > 1:
        den = den // g
        terms = [(c // g, mlt) for c, mlt in terms]
    if terms and terms[0][0] < 0:
        terms = terms[::-1]
    out = ''
    for c, mlt in terms:
        piece = ('' if mlt == 0 else name + (' t' if mlt == 1 else str(mlt) + 't'))
        if piece == '':
            piece = str(abs(c))
        elif abs(c) != 1:
            piece = str(abs(c)) + piece
        if out == '':
            out = ('-' if c < 0 else '') + piece
        else:
            out += ('-' if c < 0 else '+') + piece
    if den != 1:
        out = '(' + out + ')/' + str(den)
    return out

def t_powtomult(n):
    n = _iv(n, 'n', 2, 6)
    ct = []
    k = 0
    while 2 * k < n:
        ct.append((2 * casutil.ncr(n, k), n - 2 * k))
        k += 1
    if n % 2 == 0:
        ct.append((casutil.ncr(n, n // 2), 0))
    stt = []
    if n % 2 == 0:
        sgn = 1 if (n // 2) % 2 == 0 else -1
        k = 0
        while 2 * k < n:
            stt.append((sgn * 2 * ((-1) ** k) * casutil.ncr(n, k), n - 2 * k))
            k += 1
        stt.append((casutil.ncr(n, n // 2), 0))
        sname = 'cos'
        sden = 2 ** n
    else:
        sgn = 1 if ((n - 1) // 2) % 2 == 0 else -1
        k = 0
        while 2 * k < n:
            stt.append((sgn * ((-1) ** k) * casutil.ncr(n, k), n - 2 * k))
            k += 1
        sname = 'sin'
        sden = 2 ** (n - 1)
    out = []
    ch = 'cos^' + str(n) + ' t = '
    cb = _mulstr('cos', ct, 2 ** n)
    sh = 'sin^' + str(n) + ' t = '
    sb = _mulstr(sname, stt, sden)
    for h, b in ((ch, cb), (sh, sb)):
        if len(h) + len(b) <= 36:
            out.append(h + b)
        else:
            out.append(h[:len(h) - 1])
            out.append(b)
    out.append(_w('z = cos t + i sin t, z + 1/z = 2cos t'))
    out.append(_w('z - 1/z = 2i sin t, z^m + 1/z^m = 2cos mt'))
    out.append(_w('expand (z +/- 1/z)^' + str(n) + ' and pair the terms'))
    return out

# ---- M  Matrices and transformations ----------------------------------------

def _rank(M, tol):
    R = [list(r) for r in M]
    rows = len(R)
    cols = len(R[0])
    row = 0
    col = 0
    while col < cols and row < rows:
        best = row
        r = row
        while r < rows:
            if abs(R[r][col]) > abs(R[best][col]):
                best = r
            r += 1
        if abs(R[best][col]) <= tol:
            col += 1
            continue
        R[row], R[best] = R[best], R[row]
        pv = R[row][col]
        r = 0
        while r < rows:
            if r != row and R[r][col] != 0:
                fac = R[r][col] / pv
                c = col
                while c < cols:
                    R[r][c] -= fac * R[row][c]
                    c += 1
            r += 1
        row += 1
        col += 1
    return row

def _tol(M):
    big = 1.0
    for r in M:
        for v in r:
            if abs(v) > big:
                big = abs(v)
    return big * 1e-9

def _para(u, v):
    return abs(u[0] * v[1] - u[1] * v[0]) < 1e-9 and \
        abs(u[0] * v[2] - u[2] * v[0]) < 1e-9 and \
        abs(u[1] * v[2] - u[2] * v[1]) < 1e-9

def _cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]]

def _nullvec(M):
    # one vector spanning the null space of a square float matrix, or None
    n = len(M)
    a = [list(r) for r in M]
    tol = _tol(M)
    piv = []
    row = 0
    col = 0
    while row < n and col < n:
        best = row
        r = row
        while r < n:
            if abs(a[r][col]) > abs(a[best][col]):
                best = r
            r += 1
        if abs(a[best][col]) <= tol:
            col += 1
            continue
        a[row], a[best] = a[best], a[row]
        d = a[row][col]
        j = 0
        while j < n:
            a[row][j] /= d
            j += 1
        r = 0
        while r < n:
            if r != row and abs(a[r][col]) > 1e-14:
                fc = a[r][col]
                j = 0
                while j < n:
                    a[r][j] -= fc * a[row][j]
                    j += 1
            r += 1
        piv.append(col)
        row += 1
        col += 1
    free = []
    c = 0
    while c < n:
        if c not in piv:
            free.append(c)
        c += 1
    if not free:
        return None
    fc = free[0]
    v = [0.0] * n
    v[fc] = 1.0
    i = 0
    while i < len(piv):
        v[piv[i]] = -a[i][fc]
        i += 1
    return _scale(v)

def _nullity(M):
    return len(M) - _rank(M, _tol(M))

def t_lin2(p, q, A, B):
    out = []
    R = [[p * A[i][j] + q * B[i][j] for j in range(2)] for i in range(2)]
    for ln in _mlines('pA+qB', R):
        out.append(ln)
    out.append(_w('add entry by entry; both must be 2x2'))
    out.append(_w('p = ' + _f(p) + ', q = ' + _f(q)))
    return out

def t_lin3(p, q, A, B):
    out = []
    R = [[p * A[i][j] + q * B[i][j] for j in range(3)] for i in range(3)]
    for ln in _mlines('pA+qB', R):
        out.append(ln)
    out.append(_w('add entry by entry; both must be 3x3'))
    out.append(_w('p = ' + _f(p) + ', q = ' + _f(q)))
    return out

def t_mul2(A, B):
    out = _mlines('AB', _mm(A, B)) + _mlines('BA', _mm(B, A))
    out.append(_w('AB = A applied after B (B first)'))
    out.append(_w('row i of A times column j of B'))
    if _mm(A, B) != _mm(B, A):
        out.append(_warn('AB is not BA: order matters'))
    return out

def t_mul3(A, B):
    out = _mlines('AB', _mm(A, B))
    for ln in _mlines('BA', _mm(B, A)):
        out.append(_w(ln))
    out.append(_w('AB = A applied after B (B first)'))
    return out

def t_det2(A):
    d = _det2(A)
    out = ['det A = ' + _f(d), 'area scale factor = ' + _f(abs(d))]
    if d == 0:
        out.append(_warn('singular: the plane collapses to a line'))
    elif d < 0:
        out.append(_warn('det < 0: orientation is reversed'))
    else:
        out.append(_w('det > 0: orientation is preserved'))
    out.append(_w('det = ad - bc = ' + _f(A[0][0]) + 'x' + _f(A[1][1]) +
                  ' - ' + _f(A[0][1]) + 'x' + _f(A[1][0])))
    return out

def t_det3(A):
    d = _det3(A)
    out = ['det A = ' + _f(d), 'volume scale factor = ' + _f(abs(d))]
    if d == 0:
        out.append(_warn('singular: volume collapses to 0'))
    elif d < 0:
        out.append(_warn('det < 0: orientation is reversed'))
    else:
        out.append(_w('det > 0: orientation is preserved'))
    out.append(_w('expanded along row 1 with the 2x2 minors'))
    out.append(_w('minors: ' + _f(A[1][1] * A[2][2] - A[1][2] * A[2][1]) + ', ' +
                  _f(A[1][0] * A[2][2] - A[1][2] * A[2][0]) + ', ' +
                  _f(A[1][0] * A[2][1] - A[1][1] * A[2][0])))
    return out

def t_inv2(A):
    d = _det2(A)
    if d == 0:
        return ['no inverse: det A = 0', _warn('A is singular')]
    out = _mlines('A^-1', _inv2(A))
    out.append(_w('det = ' + _f(d) + ', swap a and d, negate b and c'))
    out.append(_w('then divide every entry by det'))
    return out

def t_inv3(A):
    d = _det3(A)
    if d == 0:
        return ['no inverse: det A = 0', _warn('A is singular')]
    out = _mlines('A^-1', _inv3(A))
    out.append(_w('det = ' + _f(d)))
    out.append(_w('A^-1 = (1/det) x adjugate (cofactors, then'))
    out.append(_w('transpose); (AB)^-1 = B^-1 A^-1'))
    return out

def t_solve3(A, b):
    d = _det3(A)
    if d != 0:
        iv = _inv3(A)
        x = [casutil.clean(iv[i][0] * b[0] + iv[i][1] * b[1] + iv[i][2] * b[2])
             for i in range(3)]
        out = ['x = ' + _f(x[0]), 'y = ' + _f(x[1]), 'z = ' + _f(x[2]),
               'unique point: the planes meet there']
        out.append(_w('det A = ' + _f(d) + ', so A^-1 exists'))
        for ln in _mlines('A^-1', iv):
            out.append(_w(ln))
        out.append(_w('x = A^-1 b'))
        return out
    out = ['det A = 0: no unique solution']
    for ln in _planes_sing(A, b):
        out.append(ln)
    return out

def _sheafline(A, b):
    # a point and direction of the common line of consistent planes
    p = 0
    q = 1
    if _para(A[0], A[1]):
        q = 2
        if _para(A[0], A[2]):
            p = 1
    dv = _cross(A[p], A[q])
    k = 0
    j = 1
    while j < 3:
        if abs(dv[j]) > abs(dv[k]):
            k = j
        j += 1
    u = [0, 1, 2]
    u.remove(k)
    a1 = A[p][u[0]]
    b1 = A[p][u[1]]
    a2 = A[q][u[0]]
    b2 = A[q][u[1]]
    dd = a1 * b2 - a2 * b1
    pt = [0.0, 0.0, 0.0]
    pt[u[0]] = casutil.clean(_snap((b[p] * b2 - b[q] * b1) / dd))
    pt[u[1]] = casutil.clean(_snap((a1 * b[q] - a2 * b[p]) / dd))
    pt[k] = 0
    return pt, _scale(dv)

def _planes_sing(A, b):
    # v4: how three planes with det = 0 sit
    aug = [A[i] + [b[i]] for i in range(3)]
    ra = _rank(A, _tol(A))
    rb = _rank(aug, _tol(aug))
    out = []
    if ra == 2 and rb == 2:
        pt, dv = _sheafline(A, b)
        out.append('sheaf: the planes share a line')
        out.append('point ' + casutil.fmtv(pt))
        out.append('direction ' + casutil.fmtv(dv))
        out.append(_w('r = ' + casutil.fmtv(pt) + ' + t' + casutil.fmtv(dv)))
        out.append(_w('consistent: infinitely many solutions'))
    elif ra == 2 and rb == 3:
        par = _para(A[0], A[1]) or _para(A[0], A[2]) or _para(A[1], A[2])
        if par:
            out.append('two planes are parallel')
            out.append('no solution')
            out.append(_w('the third plane cuts both of them'))
        else:
            out.append('triangular prism: no solution')
            out.append(_w('each pair meets in a line, all three parallel'))
    elif ra == 1 and rb == 1:
        out.append('the three planes are the same')
        out.append(_w('any point of that plane is a solution'))
    elif ra == 1:
        out.append('parallel planes: no solution')
        out.append(_w('the normals are all parallel'))
    else:
        out.append(_warn('degenerate: a normal is the zero vector'))
    out.append(_w('rank A = ' + str(ra) + ', rank [A|b] = ' + str(rb)))
    return out

def t_rot2(theta):
    t = theta * PI / 180.0
    c = _snap(math.cos(t))
    s = _snap(math.sin(t))
    out = _mlines('R', [[c, -s], [s, c]])
    out.append('rotation ' + _f(theta) + ' deg about O')
    out.append(_w('anticlockwise positive; det = 1'))
    out.append(_w('R(a)R(b) = R(a+b), R^-1 = R(-a)'))
    return out

def t_ref2(theta):
    t = 2.0 * theta * PI / 180.0
    c = _snap(math.cos(t))
    s = _snap(math.sin(t))
    out = _mlines('M', [[c, s], [s, -c]])
    out.append('reflect in y = x tan ' + _f(theta) + ' deg')
    out.append(_w('entries use 2 x ' + _f(theta) + ' = ' + _f(2 * theta) + ' deg'))
    out.append(_w('det = -1, M^2 = I'))
    return out

def t_stretch2(p, q):
    out = _mlines('S', [[p, 0], [0, q]])
    if p == q:
        out.append('enlargement scale factor ' + _f(p))
    else:
        out.append('stretch x by ' + _f(p) + ', y by ' + _f(q))
    out.append('det = ' + _f(p * q) + ' = area scale factor')
    if p == 1:
        out.append(_w('x-axis invariant: stretch parallel to y'))
    if q == 1:
        out.append(_w('y-axis invariant: stretch parallel to x'))
    return out

def _mirror(th):
    th = casutil.clean(_snap(th))
    if th == 0:
        return 'the x-axis'
    if th == 90 or th == -90:
        return 'the y-axis'
    if th == 45:
        return 'y = x'
    if th == -45:
        return 'y = -x'
    return 'y = x tan ' + _f(th) + ' deg'

def _desc2(A):
    # m4: words for a 2x2 matrix, as a list of answer lines
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    det = _det2(A)
    tol = 1e-9 * (1.0 + abs(a) + abs(b) + abs(c) + abs(d))
    if abs(b) < tol and abs(c) < tol and abs(a - d) < tol:
        if abs(a) < tol:
            return ['zero matrix: all points to O']
        if abs(a - 1.0) < tol:
            return ['identity: every point fixed']
        if abs(a + 1.0) < tol:
            return ['rotation 180 deg about O']
        return ['enlargement scale factor ' + _f(a)]
    if abs(a - d) < tol and abs(b + c) < tol:
        r = math.sqrt(a * a + c * c)
        s = 'rotation ' + _f(_snap(math.atan2(c, a) * 180.0 / PI)) + ' deg about O'
        return [s] if abs(r - 1.0) < 1e-9 else [s, 'and enlargement sf ' + _f(r)]
    if abs(a + d) < tol and abs(b - c) < tol:
        r = math.sqrt(a * a + b * b)
        s = 'reflection in ' + _mirror(0.5 * math.atan2(b, a) * 180.0 / PI)
        return [s] if abs(r - 1.0) < 1e-9 else [s, 'and enlargement sf ' + _f(r)]
    if abs(b) < tol and abs(c) < tol:
        if abs(a - 1.0) < tol:
            return ['stretch parallel to y-axis, sf ' + _f(d)]
        if abs(d - 1.0) < tol:
            return ['stretch parallel to x-axis, sf ' + _f(a)]
        return ['stretch x by ' + _f(a) + ', y by ' + _f(d)]
    if abs(det - 1.0) < tol and abs(a + d - 2.0) < tol:
        if abs(c) < tol:
            return ['shear, x-axis fixed, factor ' + _f(b)]
        if abs(b) < tol:
            return ['shear, y-axis fixed, factor ' + _f(c)]
        v = _nullvec([[a - 1.0, b], [c, d - 1.0]])
        if v is not None:
            ln = 'x = 0' if v[0] == 0 else _ymx(v[1] * 1.0 / v[0])
            return ['shear, line ' + ln + ' fixed']
    return ['not a standard transformation']

def t_describe(A):
    det = _det2(A)
    out = _desc2(A)
    out.append('det = ' + _f(det))
    if det < 0:
        out.append(_w('det < 0: orientation reversed'))
    out.append(_w('rotate [[c,-s],[s,c]], reflect [[c,s],[s,-c]]'))
    out.append(_w('columns are the images of i and j'))
    return out

def t_shear2(k, axis):
    ax = _iv(axis, 'axis', 1, 2)
    M = [[1, k], [0, 1]] if ax == 1 else [[1, 0], [k, 1]]
    out = _mlines('S', M)
    out.append('shear, ' + ('x' if ax == 1 else 'y') + '-axis fixed, factor ' + _f(k))
    out.append(_w('axis 1 = x-axis fixed, 2 = y-axis fixed'))
    if ax == 1:
        out.append(_w('(x, y) -> (x + ' + _f(k) + 'y, y); det = 1'))
    else:
        out.append(_w('(x, y) -> (x, y + ' + _f(k) + 'x); det = 1'))
    return out

def _thenlines(P, da, db, dp, detP):
    out = _mlines('BA', P)
    for tag, ds in (('A', da), ('B', db), ('BA', dp)):
        out.append(tag + ': ' + ds[0])
        for more in ds[1:]:
            out.append(' ' * (len(tag) + 2) + more)
    out.append(_w('A first, then B: the single matrix is BA'))
    out.append(_w('det BA = det B x det A = ' + _f(detP)))
    return out

def t_then2(A, B):
    # m5: successive transformations
    P = _mm(B, A)
    return _thenlines(P, _desc2(A), _desc2(B), _desc2(P), _det2(P))

_AXN = ('x', 'y', 'z')

def _rot3m(ax, deg):
    t = deg * PI / 180.0
    c = casutil.clean(_snap(math.cos(t)))
    s = casutil.clean(_snap(math.sin(t)))
    if ax == 1:
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if ax == 2:
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

def _same3(A, B):
    i = 0
    while i < 3:
        j = 0
        while j < 3:
            if abs(A[i][j] - B[i][j]) > 1e-9:
                return False
            j += 1
        i += 1
    return True

def _desc3(A):
    # m4: the 3-D maps in the spec, else a plain verdict
    diag = True
    i = 0
    while i < 3:
        j = 0
        while j < 3:
            if i != j and abs(A[i][j]) > 1e-9:
                diag = False
            j += 1
        i += 1
    if diag:
        a = A[0][0]
        if abs(A[1][1] - a) < 1e-9 and abs(A[2][2] - a) < 1e-9:
            if abs(a - 1.0) < 1e-9:
                return ['identity: every point fixed']
            if abs(a) < 1e-9:
                return ['zero matrix: all points to O']
            return ['enlargement scale factor ' + _f(a)]
    pl = 1
    while pl <= 3:
        M = _ident(3)
        M[pl - 1][pl - 1] = -1
        if _same3(A, M):
            return ['reflect in the plane ' + _AXN[pl - 1] + ' = 0']
        pl += 1
    ax = 1
    while ax <= 3:
        for deg in (90, 180, 270):
            if _same3(A, _rot3m(ax, deg)):
                return ['rotate ' + str(deg) + ' deg about ' + _AXN[ax - 1]]
        ax += 1
    if diag:
        return ['stretch: x by ' + _f(A[0][0]) + ', y by ' + _f(A[1][1]) +
                ', z by ' + _f(A[2][2])]
    return ['not a single standard map']

def t_describe3(A):
    det = _det3(A)
    out = _desc3(A)
    out.append('det = ' + _f(det))
    if det < 0:
        out.append(_w('det < 0: orientation reversed'))
    out.append(_w('|det| = volume scale factor = ' + _f(abs(det))))
    out.append(_w('checks rotations of 90, 180, 270 deg about'))
    out.append(_w('an axis and reflections in x/y/z = 0'))
    return out

def t_then3(A, B):
    # m5: successive transformations in 3-D
    P = _mm(B, A)
    return _thenlines(P, _desc3(A), _desc3(B), _desc3(P), _det3(P))

def t_detk(a, b, c, d, e, f, g, h, i):
    # m15: determinant of a 3x3 with algebraic entries
    M = [[a, b, c], [d, e, f], [g, h, i]]
    vs = []
    for row in M:
        for t in row:
            for v in caseng.vars_in(t):
                if v not in vs:
                    vs.append(v)
    if len(vs) > 1:
        raise ValueError('use one letter, e.g. k')
    var = vs[0] if vs else 'k'

    def minor(p, q, r, s):
        return ('-', ('*', p, s), ('*', q, r))
    m1 = minor(e, f, h, i)
    m2 = minor(d, f, g, i)
    m3 = minor(d, e, g, h)
    T = ('+', ('-', ('*', a, m1), ('*', b, m2)), ('*', c, m3))
    P = None
    try:
        P = caspoly.poly(T, var)
    except Exception:
        P = None
    out = []
    roots = []
    if P is not None:
        P = caspoly.ptrim(P)
        tree = caseng.simplify(caspoly.ptree(P, var))
        out.append('det =')
        out.append(_m(tree))
        if len(P) == 0:
            out.append('singular for every ' + var)
        elif len(P) == 1:
            out.append('never singular')
        else:
            hi = []
            j = len(P) - 1
            while j >= 0:
                hi.append(P[j][0] * 1.0 / P[j][1])
                j -= 1
            for r in _roots(hi):
                if not isinstance(r, complex):
                    _addroot(roots, r)
    else:
        tree = cascalc.tidy(T)
        out.append('det =')
        out.append(_m(tree))
        try:
            for r in cascalc.solve(T, var):
                _addroot(roots, r)
        except Exception:
            roots = []
        out.append(_warn('roots searched in -20..20 only'))
    if P is None or len(P) > 1:
        roots.sort()
        if roots:
            vals = [_f(0 if abs(r) < 1e-6 else r) for r in roots[:8]]
            if len(vals) <= 3:
                out.append('singular when ' + var + ' = ' + ', '.join(vals))
            else:
                out.append('singular when ' + var + ' =')
                j = 0
                while j < len(vals):
                    out.append('  ' + ', '.join(vals[j:j + 4]))
                    j += 4
                if len(roots) > 8:
                    out.append(_w(str(len(roots) - 8) + ' more roots not shown'))
        else:
            out.append('no real ' + var + ' makes it singular')
    out.append(_w('expand along row 1: a(ei-fh) - b(di-fg) + c(dh-eg)'))
    for nm, mt in (('ei-fh', m1), ('di-fg', m2), ('dh-eg', m3)):
        try:
            out.append(_w(nm + ' = ' + caseng.tostr(cascalc.tidy(mt))[:40]))
        except Exception:
            pass
    adj = []
    r = 0
    while r < 3:
        row = []
        cc = 0
        while cc < 3:
            # adj[r][cc] = cofactor of entry (cc, r)
            rs = [0, 1, 2]
            rs.remove(cc)
            cs = [0, 1, 2]
            cs.remove(r)
            t = minor(M[rs[0]][cs[0]], M[rs[0]][cs[1]], M[rs[1]][cs[0]], M[rs[1]][cs[1]])
            if (r + cc) % 2:
                t = ('neg', t)
            try:
                row.append(caseng.tostr(cascalc.tidy(t)))
            except Exception:
                row.append('?')
            cc += 1
        adj.append(row)
        r += 1
    out.append(_w('M^-1 = adj(M)/det, where det != 0:'))
    r = 0
    while r < 3:
        out.append(_w('adj r' + str(r + 1) + ': [' + ', '.join(adj[r]) + ']'))
        r += 1
    return out

def _addroot(lst, r):
    r = _cleanroot(r)
    for u in lst:
        if abs(u - r) < 1e-7:
            return
    lst.append(r)

def t_rot3(axis, theta):
    ax = _iv(axis, 'axis', 1, 3)
    out = _mlines('R', _rot3m(ax, theta))
    out.append('rotate ' + _f(theta) + ' deg about ' + _AXN[ax - 1])
    out.append(_w('axis 1 = x, 2 = y, 3 = z; det = 1'))
    out.append(_w('the ' + _AXN[ax - 1] + '-axis is invariant'))
    return out

def t_ref3(plane):
    pl = _iv(plane, 'plane', 1, 3)
    M = _ident(3)
    M[pl - 1][pl - 1] = -1
    out = _mlines('M', M)
    out.append('reflect in the plane ' + _AXN[pl - 1] + ' = 0')
    out.append('det = -1: orientation reversed')
    out.append(_w('plane 1 = x=0, 2 = y=0, 3 = z=0'))
    return out

def _ymx(m):
    m = casutil.clean(_snap(m))
    if m == 0:
        return 'y = 0'
    if m == 1:
        return 'y = x'
    if m == -1:
        return 'y = -x'
    return 'y = ' + _f(m) + 'x'

def t_invar(A):
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    S = [[a - 1.0, b], [c, d - 1.0]]
    ds = _det2(S)
    out = []
    if abs(ds) > 1e-12:
        out.append('only invariant point is (0, 0)')
    else:
        v = _nullvec(S)
        if v is None or _nullity(S) >= 2:
            out.append('every point is invariant (A = I)')
        elif v[0] == 0:
            out.append('line of invariant points x = 0')
        else:
            out.append('line of invariant points ' + _ymx(v[1] * 1.0 / v[0]))
    out.append(_w('det(A - I) = ' + _f(ds)))
    ms = []
    if abs(b) < 1e-12:
        if abs(a - d) > 1e-12:
            ms.append(c / (a - d))
        elif abs(c) < 1e-12:
            out.append('every line through O is invariant')
    else:
        disc = (a - d) * (a - d) + 4.0 * b * c
        out.append(_w('b m^2 + (a-d) m - c = 0, disc = ' + _f(disc)))
        if disc < -1e-12:
            out.append('no invariant line through O')
        else:
            if disc < 0:
                disc = 0.0
            rt = math.sqrt(disc)
            ms.append((-(a - d) + rt) / (2.0 * b))
            if rt > 1e-12:
                ms.append((-(a - d) - rt) / (2.0 * b))
    for mg in ms:
        out.append('invariant line ' + _ymx(mg))
    if abs(b) < 1e-12:
        out.append('invariant line x = 0')
    out.append(_w('y = mx maps to y = mx when c + dm = m(a + bm)'))
    return out

# ---- V  Vectors and 3-D -----------------------------------------------------

def _sub3(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def _dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _cross3(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]

def _mag3(a):
    return math.sqrt(_dot3(a, a))

def _step(a, d, t):
    return [a[0] + t * d[0], a[1] + t * d[1], a[2] + t * d[2]]

def _nonzero(v, name):
    if _mag3(v) < 1e-12:
        raise ValueError(name + ' is the zero vector')
    return v

def _ints(vals):
    out = []
    for c in vals:
        k = int(round(c))
        if abs(c - k) > 1e-9:
            return None
        out.append(k)
    return out

def _simp_vec(v):
    iv = _ints(v)
    if iv is None:
        return v
    g = 0
    for c in iv:
        g = casutil.gcd(g, c)
    if g <= 1:
        return iv
    return [c // g for c in iv]

def _simp_plane(n, d):
    iv = _ints([n[0], n[1], n[2], d])
    if iv is None:
        return (n, d)
    g = 0
    for c in iv:
        g = casutil.gcd(g, c)
    if g <= 1:
        return (n, d)
    return ([iv[0] // g, iv[1] // g, iv[2] // g], iv[3] // g)

def _angle_lines(c):
    r = casutil.acos_safe(c)
    return ['angle = ' + _f(r) + ' rad',
            '      = ' + _f(casutil.deg(r)) + ' deg']

def _cart_line(a, d):
    names = ('x', 'y', 'z')
    parts = []
    fixed = []
    i = 0
    while i < 3:
        if abs(d[i]) > 1e-12:
            top = names[i]
            if abs(a[i]) > 1e-12:
                top = '(' + names[i] + (' - ' if a[i] > 0 else ' + ') + _f(abs(a[i])) + ')'
            if abs(d[i] - 1.0) < 1e-12:
                parts.append(top)
            elif d[i] < 0:
                parts.append(top + '/(' + _f(d[i]) + ')')
            else:
                parts.append(top + '/' + _f(d[i]))
        else:
            fixed.append(names[i] + ' = ' + _f(a[i]))
        i += 1
    out = []
    if parts:
        out.append(' = '.join(parts))
    for s in fixed:
        out.append(s)
    return out

def _plane_lines(n, d):
    n, d = _simp_plane(n, d)
    names = ('x', 'y', 'z')
    s = ''
    i = 0
    while i < 3:
        c = n[i]
        if abs(c) > 1e-12:
            if s == '':
                s = ('-' if c < 0 else '') + ('' if abs(abs(c) - 1.0) < 1e-12 else _f(abs(c))) + names[i]
            else:
                s = s + (' - ' if c < 0 else ' + ') + ('' if abs(abs(c) - 1.0) < 1e-12 else _f(abs(c))) + names[i]
        i += 1
    return ['r.' + _fv(n) + ' = ' + _f(d), s + ' = ' + _f(d)]

def t_line_2pts(A, B):
    d = _nonzero(_sub3(B, A), 'B - A')
    d = _simp_vec(d)
    out = ['r = ' + _fv(A) + ' + t' + _fv(d)]
    for s in _cart_line(A, d):
        out.append(s)
    out.append(_w('direction = B - A'))
    out.append(_w('|d| = ' + _f(_mag3(d))))
    return out

def t_line_cart(a, d):
    _nonzero(d, 'd')
    d = _simp_vec(d)
    out = ['r = ' + _fv(a) + ' + t' + _fv(d)]
    for s in _cart_line(a, d):
        out.append(s)
    out.append(_w('|d| = ' + _f(_mag3(d))))
    return out

def t_plane_3pts(A, B, C):
    n = _cross3(_sub3(B, A), _sub3(C, A))
    if _mag3(n) < 1e-12:
        raise ValueError('the three points are collinear')
    n = _simp_vec(n)
    d = _dot3(n, A)
    out = _plane_lines(n, d)
    out.append(_w('n = (B-A) x (C-A) = ' + _fv(n)))
    out.append(_w('d = n.A = ' + _f(d)))
    return out

def t_plane_pt_n(p, n):
    _nonzero(n, 'n')
    d = _dot3(n, p)
    out = _plane_lines(n, d)
    out.append(_w('d = n.p = ' + _f(d)))
    out.append(_w('|n| = ' + _f(_mag3(n))))
    return out

def _posfirst(v):
    for c in v:
        if abs(c) > 1e-12:
            return [-x for x in v] if c < 0 else v
    return v

def t_plane_2dirs(a, b, c):
    # v2: r = a + s b + t c  ->  n.r = d and cartesian
    n = _cross3(b, c)
    if _mag3(n) < 1e-12 * (1.0 + _mag3(b) * _mag3(c)):
        raise ValueError('the directions are parallel')
    n = _posfirst(_simp_vec(n))
    d = _dot3(n, a)
    out = _plane_lines(n, d)
    out.append(_w('r = ' + _fv(a) + ' + s' + _fv(b) + ' + t' + _fv(c)))
    out.append(_w('n = b x c = ' + _fv(n)))
    out.append(_w('d = n.a = ' + _f(d)))
    return out

def t_plane_to_vec(n, d):
    # v2: n.r = d  ->  r = p + s u + t v
    _nonzero(n, 'n')
    k = 0
    j = 1
    while j < 3:
        if abs(n[j]) > abs(n[k]):
            k = j
        j += 1
    p = [0, 0, 0]
    p[k] = casutil.clean(d * 1.0 / n[k])
    cands = [[n[1], -n[0], 0], [n[2], 0, -n[0]], [0, n[2], -n[1]]]
    dirs = []
    for v in cands:
        if _mag3(v) < 1e-12:
            continue
        if dirs and _mag3(_cross3(dirs[0], v)) < 1e-9 * _mag3(v) * _mag3(dirs[0]):
            continue
        dirs.append(_posfirst(_simp_vec(v)))
        if len(dirs) == 2:
            break
    out = ['point ' + _fv(p),
           'directions ' + _fv(dirs[0]) + ', ' + _fv(dirs[1])]
    out.append(_w('r = ' + _fv(p) + ' + s' + _fv(dirs[0]) + ' + t' + _fv(dirs[1])))
    out.append(_w('both directions have zero dot product with n'))
    out.append(_w('the point has n.p = ' + _f(d)))
    return out

def t_angle_lines(d1, d2):
    _nonzero(d1, 'd1')
    _nonzero(d2, 'd2')
    dp = _dot3(d1, d2)
    c = abs(dp) / (_mag3(d1) * _mag3(d2))
    out = _angle_lines(c)
    out.append(_w('cos = |d1.d2|/(|d1||d2|) = ' + _f(c)))
    out.append(_w('d1.d2 = ' + _f(dp)))
    return out

def t_angle_lp(d, n):
    _nonzero(d, 'd')
    _nonzero(n, 'n')
    s = abs(_dot3(d, n)) / (_mag3(d) * _mag3(n))
    if s > 1.0:
        s = 1.0
    r = math.asin(s)
    out = ['angle = ' + _f(r) + ' rad',
           '      = ' + _f(casutil.deg(r)) + ' deg']
    out.append(_w('sin = |d.n|/(|d||n|) = ' + _f(s)))
    out.append(_w('d.n = ' + _f(_dot3(d, n))))
    return out

def t_angle_planes(n1, n2):
    _nonzero(n1, 'n1')
    _nonzero(n2, 'n2')
    dp = _dot3(n1, n2)
    c = abs(dp) / (_mag3(n1) * _mag3(n2))
    out = _angle_lines(c)
    out.append(_w('cos = |n1.n2|/(|n1||n2|) = ' + _f(c)))
    out.append(_w('n1.n2 = ' + _f(dp)))
    return out

def t_perp_check(a, b):
    _nonzero(a, 'a')
    _nonzero(b, 'b')
    dp = _dot3(a, b)
    cr = _cross3(a, b)
    scale = _mag3(a) * _mag3(b)
    out = ['perpendicular' if abs(dp) < 1e-9 * scale else 'not perpendicular']
    out.append('parallel' if _mag3(cr) < 1e-9 * scale else 'not parallel')
    out.append(_w('a.b = ' + _f(dp)))
    out.append(_w('a x b = ' + _fv(cr)))
    return out

def t_cross(a, b):
    cr = _cross3(a, b)
    mc = _mag3(cr)
    out = ['a x b = ' + _fv(cr), '|a x b| = ' + _f(mc)]
    out.append(_w('a.b = ' + _f(_dot3(a, b))))
    ma = _mag3(a)
    mb = _mag3(b)
    if ma > 1e-12 and mb > 1e-12:
        out.append(_w('sin t = |a x b|/(|a||b|) = ' + _f(mc / (ma * mb))))
    if mc > 1e-12:
        out.append(_w('n-hat = ' + _fv([c / mc for c in cr])))
        out.append(_w('a x b = |a||b| sin t n-hat, perp to a and b'))
    else:
        out.append(_w('a x b = 0: a and b are parallel'))
    return out

def t_scalar(a, b):
    # Pv1: scalar product and the angle between two vectors
    _nonzero(a, 'a')
    _nonzero(b, 'b')
    dp = _dot3(a, b)
    ma = _mag3(a)
    mb = _mag3(b)
    c = dp / (ma * mb)
    r = casutil.acos_safe(c)
    out = ['a.b = ' + _f(dp), 'angle = ' + _f(r) + ' rad',
           '      = ' + _f(casutil.deg(r)) + ' deg']
    if abs(dp) < 1e-9 * ma * mb:
        out.append('a and b are perpendicular')
    out.append(_w('|a| = ' + _f(ma) + ',  |b| = ' + _f(mb)))
    out.append(_w('cos t = a.b/(|a||b|) = ' + _f(c)))
    return out

def t_tri_area(A, B, C):
    cr = _cross3(_sub3(B, A), _sub3(C, A))
    area = 0.5 * _mag3(cr)
    out = ['area = ' + _f(area)]
    out.append(_w('area = 0.5|(B-A) x (C-A)|'))
    out.append(_w('(B-A) x (C-A) = ' + _fv(cr)))
    return out

def t_on_line(a, b, p):
    _nonzero(b, 'b')
    cr = _cross3(_sub3(p, a), b)
    scale = _mag3(_sub3(p, a)) * _mag3(b) + 1.0
    on = _mag3(cr) < 1e-9 * scale
    out = ['p is on the line' if on else 'p is not on the line']
    if on:
        t = _dot3(_sub3(p, a), b) / _dot3(b, b)
        out.append('t = ' + _f(t))
    out.append(_w('(r-a) x b = 0 defines the line'))
    out.append(_w('(p-a) x b = ' + _fv(cr)))
    return out

def _line_pair(a1, d1, a2, d2):
    _nonzero(d1, 'd1')
    _nonzero(d2, 'd2')
    cr = _cross3(d1, d2)
    wv = _sub3(a2, a1)
    mc = _mag3(cr)
    scale = _mag3(d1) * _mag3(d2)
    if mc < 1e-9 * scale:
        dist = _mag3(_cross3(wv, d1)) / _mag3(d1)
        if dist < 1e-9 * (1.0 + _mag3(wv)):
            return ('same', 0.0, cr)
        return ('par', dist, cr)
    dist = abs(_dot3(wv, cr)) / mc
    t = _dot3(_cross3(wv, d2), cr) / (mc * mc)
    s = _dot3(_cross3(wv, d1), cr) / (mc * mc)
    if dist < 1e-9 * (1.0 + _mag3(wv) + _mag3(d1) + _mag3(d2)):
        return ('meet', (t, s, _step(a1, d1, t)), cr)
    return ('skew', (dist, t, s), cr)

def t_line_meet(a1, d1, a2, d2):
    kind, info, cr = _line_pair(a1, d1, a2, d2)
    out = []
    if kind == 'same':
        out.append('the same line')
    elif kind == 'par':
        out.append('parallel, no intersection')
        out.append('distance = ' + _f(info))
    elif kind == 'meet':
        t, s, p = info
        out.append('they meet at ' + _fv(p))
        out.append(_w('t = ' + _f(t) + ',  s = ' + _f(s)))
    else:
        dist, t, s = info
        out.append('skew lines')
        out.append('distance = ' + _f(dist))
        out.append(_w('nearest on line 1: ' + _fv(_step(a1, d1, t))))
        out.append(_w('nearest on line 2: ' + _fv(_step(a2, d2, s))))
    out.append(_w('d1 x d2 = ' + _fv(cr)))
    out.append(_w('a2 - a1 = ' + _fv(_sub3(a2, a1))))
    return out

def t_line_dist(a1, d1, a2, d2):
    kind, info, cr = _line_pair(a1, d1, a2, d2)
    out = []
    if kind == 'same':
        out.append('the same line')
        out.append('distance = 0')
    elif kind == 'par':
        out.append('parallel lines')
        out.append('distance = ' + _f(info))
        out.append(_w('d = |(a2-a1) x d1|/|d1|'))
    elif kind == 'meet':
        out.append('lines intersect')
        out.append('distance = 0')
        out.append(_w('meet at ' + _fv(info[2])))
    else:
        out.append('skew lines')
        out.append('distance = ' + _f(info[0]))
        out.append(_w('d = |(a2-a1).(d1 x d2)|/|d1 x d2|'))
    out.append(_w('d1 x d2 = ' + _fv(cr)))
    return out

def t_line_plane(a, d, n, k):
    _nonzero(d, 'd')
    _nonzero(n, 'n')
    nd = _dot3(n, d)
    na = _dot3(n, a)
    out = []
    if abs(nd) < 1e-12 * _mag3(n) * _mag3(d):
        if abs(na - k) < 1e-9 * (1.0 + abs(k)):
            out.append('the line lies in the plane')
        else:
            out.append('parallel, never meets')
            out.append('distance = ' + _f(abs(na - k) / _mag3(n)))
    else:
        t = (k - na) / nd
        p = _step(a, d, t)
        out.append('meets at ' + _fv(p))
        out.append(_w('t = (k - n.a)/(n.d) = ' + _f(t)))
        s = abs(nd) / (_mag3(n) * _mag3(d))
        if s > 1.0:
            s = 1.0
        r = math.asin(s)
        out.append('angle = ' + _f(r) + ' rad')
        out.append('      = ' + _f(casutil.deg(r)) + ' deg')
    out.append(_w('n.d = ' + _f(nd) + ',  n.a = ' + _f(na)))
    return out

def t_pt_line(p, a, d):
    _nonzero(d, 'd')
    wv = _sub3(p, a)
    cr = _cross3(wv, d)
    dist = _mag3(cr) / _mag3(d)
    t = _dot3(wv, d) / _dot3(d, d)
    foot = _step(a, d, t)
    out = ['distance = ' + _f(dist), 'foot = ' + _fv(foot)]
    out.append(_w('d = |(p-a) x d|/|d|'))
    out.append(_w('(p-a) x d = ' + _fv(cr)))
    out.append(_w('t = (p-a).d/|d|^2 = ' + _f(t)))
    return out

def t_planes3(n1, d1, n2, d2, n3, d3):
    # v4: three planes, classified and solved
    A = [list(n1), list(n2), list(n3)]
    b = [d1, d2, d3]
    for v, nm in ((n1, 'n1'), (n2, 'n2'), (n3, 'n3')):
        _nonzero(v, nm)
    det = _det3(A)
    if det != 0:
        iv = _inv3(A)
        x = [casutil.clean(iv[i][0] * b[0] + iv[i][1] * b[1] + iv[i][2] * b[2])
             for i in range(3)]
        return ['meet at one point', _fv(x),
                _w('det of the normals = ' + _f(det) + ' != 0'),
                _w('solve the three equations by A^-1')]
    out = _planes_sing(A, b)
    out.append(_w('det of the normals = 0: no single point'))
    return out

def t_pt_plane(p, n, k):
    _nonzero(n, 'n')
    mn = _mag3(n)
    gap = _dot3(n, p) - k
    dist = abs(gap) / mn
    foot = [p[i] - gap * n[i] / (mn * mn) for i in range(3)]
    out = ['distance = ' + _f(dist), 'foot = ' + _fv(foot)]
    out.append(_w('d = |n.p - k|/|n|'))
    out.append(_w('n.p = ' + _f(_dot3(n, p)) + ',  |n| = ' + _f(mn)))
    return out

# ---- A  Algebra: roots of polynomials ---------------------------------------

def _coeffs(co, lo, hi):
    while len(co) > 1 and co[0] == 0:
        co = co[1:]
    n = len(co) - 1
    if n < lo or n > hi:
        raise ValueError('degree must be ' + str(lo) + '..' + str(hi))
    return co, n

def _elem(co):
    # e1..en from coefficients high->low
    n = len(co) - 1
    out = []
    i = 1
    while i <= n:
        out.append(casutil.clean(((-1.0) ** i) * co[i] / co[0]))
        i += 1
    return out

def t_vieta(coeffs):
    co, n = _coeffs(coeffs, 2, 4)
    e = _elem(co)
    names = ['sum of roots', 'sum of pairs', 'sum of triples', 'product of all']
    out = []
    i = 0
    while i < n:
        nm = names[i] if i < 3 else names[3]
        if i == n - 1:
            nm = 'product of all'
        out.append(nm + ' = ' + _f(e[i]))
        i += 1
    out.append(_w('e1 = -b/a, e2 = c/a, e3 = -d/a, e4 = e/a'))
    out.append(_w('sum of squares = e1^2 - 2e2 = ' +
                  _f(casutil.clean(e[0] * e[0] - 2 * e[1]))))
    if n >= 3:
        out.append(_w('sum of 1/root = ' +
                      (_f(casutil.clean(e[n - 2] / e[n - 1])) if e[n - 1] else 'undefined')))
    return out

def t_powersums(k, coeffs):
    k = _iv(k, 'k', 1, 8)
    co, n = _coeffs(coeffs, 2, 4)
    e = _elem(co)
    p = []
    m = 1
    while m <= k:
        s = 0.0
        i = 1
        while i < m and i <= n:
            s += ((-1.0) ** (i - 1)) * e[i - 1] * p[m - i - 1]
            i += 1
        if m <= n:
            s += ((-1.0) ** (m - 1)) * m * e[m - 1]
        p.append(casutil.clean(s))
        m += 1
    out = []
    i = 0
    while i < k:
        out.append('S' + str(i + 1) + ' = sum a^' + str(i + 1) + ' = ' + _f(p[i]))
        i += 1
    out.append(_w('Newton: S1 = e1, S2 = e1 S1 - 2e2,'))
    out.append(_w('S3 = e1 S2 - e2 S1 + 3e3, then e4 joins in'))
    out.append(_w('e1 = ' + _f(e[0]) + ', e2 = ' + _f(e[1])))
    return out

def _fitpoly(co, var, out, head):
    # co high->low: answer as a typeset tree plus the coefficient list
    lo = []
    i = len(co) - 1
    while i >= 0:
        lo.append(co[i])
        i -= 1
    out.append(head)
    out.append(_m(_polytree(lo, var)))
    out.append(_w('coefficients high to low: ' +
                  ', '.join([_f(casutil.clean(c)) for c in co])))

def t_rootlin(p, q, coeffs):
    if p == 0:
        raise ValueError('p must not be 0')
    co, n = _coeffs(coeffs, 2, 4)
    new = [0.0] * (n + 1)
    i = 0
    while i <= n:
        # a_i * p^i * (y - q)^(n-i)
        d = n - i
        j = 0
        while j <= d:
            new[n - j] += co[i] * (p ** i) * casutil.ncr(d, j) * ((-q) ** (d - j))
            j += 1
        i += 1
    ps = 'a' if p == 1 else ('-a' if p == -1 else _f(p) + 'a')
    hd = 'roots ' + ps
    if q:
        hd += (' - ' if q < 0 else ' + ') + _f(-q if q < 0 else q)
    out = []
    _fitpoly([casutil.clean(c) for c in new], 'x', out, hd + ':')
    out.append(_w('substitute x = (y - ' + _f(q) + ')/' + _f(p) + ' and'))
    out.append(_w('multiply through by ' + _f(p) + '^' + str(n)))
    return out

def t_rootrecip(coeffs):
    co, n = _coeffs(coeffs, 2, 4)
    if co[n] == 0:
        raise ValueError('constant term is 0: a root is 0')
    new = []
    i = n
    while i >= 0:
        new.append(co[i])
        i -= 1
    out = []
    _fitpoly(new, 'x', out, 'roots 1/a:')
    out.append(_w('put x = 1/y and multiply by y^' + str(n) + ':'))
    out.append(_w('the coefficients reverse'))
    return out

def t_rootsq(coeffs):
    co, n = _coeffs(coeffs, 2, 4)
    lo = []
    i = n
    while i >= 0:
        lo.append(co[i])
        i -= 1
    ev = []
    od = []
    i = 0
    while i < len(lo):
        if i % 2:
            od.append(lo[i])
        else:
            ev.append(lo[i])
        i += 1
    def mul(a, b):
        r = [0.0] * (len(a) + len(b) - 1)
        i2 = 0
        while i2 < len(a):
            j2 = 0
            while j2 < len(b):
                r[i2 + j2] += a[i2] * b[j2]
                j2 += 1
            i2 += 1
        return r
    ee = mul(ev, ev)
    oo = [0.0] + mul(od, od)
    g = []
    i = 0
    while i < len(ee) or i < len(oo):
        g.append((ee[i] if i < len(ee) else 0.0) - (oo[i] if i < len(oo) else 0.0))
        i += 1
    while len(g) > 1 and abs(g[len(g) - 1]) < 1e-12:
        g.pop()
    if g[len(g) - 1] < 0:
        g = [-c for c in g]
    hi = []
    i = len(g) - 1
    while i >= 0:
        hi.append(casutil.clean(g[i]))
        i -= 1
    out = []
    _fitpoly(hi, 'x', out, 'roots a^2:')
    out.append(_w('write f(x) = E(x^2) + x O(x^2), then'))
    out.append(_w('the new polynomial is E(y)^2 - y O(y)^2'))
    return out

# ---- S  Series --------------------------------------------------------------

def t_sumpow(n):
    n = _iv(n, 'n', 0, 100000000)
    s1 = n * (n + 1) // 2
    s2 = n * (n + 1) * (2 * n + 1) // 6
    return ['sum r = n(n+1)/2 = ' + _f(s1),
            'sum r^2 = n(n+1)(2n+1)/6 = ' + _f(s2),
            'sum r^3 = (n(n+1)/2)^2 = ' + _f(s1 * s1),
            _w('r = 1 to ' + str(n)),
            _w('sum r^3 = (sum r)^2')]

def _sumtable(kmax):
    # P[k](n) = sum of r^k for r = 1..n, as rational polynomials in n
    Ps = [[caspoly.R0, caspoly.R1]]
    k = 1
    while k <= kmax:
        t = [caspoly.R1]
        i = 0
        while i <= k:
            t = caspoly.pmul(t, [caspoly.R1, caspoly.R1])
            i += 1
        t = caspoly.psub(t, [caspoly.R1])
        j = 0
        while j < k:
            t = caspoly.psub(t, caspoly.pscale(Ps[j], (casutil.ncr(k + 1, j), 1)))
            j += 1
        Ps.append(caspoly.pscale(t, caspoly.rmake(1, k + 1)))
        k += 1
    return Ps

def _ratf(r):
    return casutil.clean(r[0] * 1.0 / r[1])

def t_sumpoly(fr, a, b):
    _onlyvar(fr, 'r', 'f(r)')
    a = _iv(a, 'a', -1000000, 1000000)
    p = caspoly.poly(fr, 'r')
    if p is None:
        raise ValueError('f(r) must be a polynomial in r')
    if len(p) > 7:
        raise ValueError('degree up to 6')
    Ps = _sumtable(len(p))
    S = []
    k = 0
    while k < len(p):
        S = caspoly.padd(S, caspoly.pscale(Ps[k], p[k]))
        k += 1
    base = caspoly.peval(S, (a - 1, 1))
    Sa = caspoly.psub(S, [base])
    out = []
    if b is not None:
        b = _iv(b, 'b', a, 1000000000)
        tot = caspoly.rsub(caspoly.peval(S, (b, 1)), base)
        out.append('sum = ' + _f(_ratf(tot)))
    out.append('S(n) =')
    out.append(_m(caseng.simplify(caspoly.ptree(Sa, 'n'))))
    out.append(_w('r = ' + str(a) + ' to n'))
    out.append(_w('sum r = n(n+1)/2, sum r^2 = n(n+1)(2n+1)/6,'))
    out.append(_w('sum r^3 = n^2(n+1)^2/4; combine term by term'))
    if a != 1:
        out.append(_w('subtract the sum up to r = ' + str(a - 1) +
                      ' (' + _f(_ratf(base)) + ')'))
    return out

def t_diffs(fr, n):
    _onlyvar(fr, 'r', 'f(r)')
    if fr[0] != '/':
        raise ValueError('type f(r) as one fraction')
    try:
        res = caspoly.partial(fr[1], fr[2], 'r')
    except Exception:
        res = None
    if res is None or res[0] is not None or len(res[1]) < 2:
        raise ValueError('partial fractions do not telescope')
    kk = None
    tops = []
    offs = []
    for top, fac, power in res[1]:
        if power != 1:
            raise ValueError('repeated factor: no telescoping')
        pp = caspoly.poly(fac, 'r')
        cc = caspoly.ratof(top)
        if pp is None or len(pp) != 2 or cc is None:
            raise ValueError('pieces must be constant over linear')
        if kk is None:
            kk = pp[1]
        elif pp[1] != kk:
            raise ValueError('denominators differ in the r coefficient')
        tops.append(cc)
        offs.append(caspoly.rdiv(pp[0], pp[1]))
    omin = offs[0]
    for o in offs:
        if caspoly.rsub(o, omin)[0] < 0:
            omin = o
    idx = []
    m = 0
    for o in offs:
        d = caspoly.rint(caspoly.rsub(o, omin))
        if d is None or d < 0 or d > 8:
            raise ValueError('gaps are not whole steps in r')
        idx.append(d)
        if d > m:
            m = d
    a = []
    j = 0
    while j <= m:
        a.append(caspoly.R0)
        j += 1
    i = 0
    while i < len(tops):
        a[idx[i]] = caspoly.radd(a[idx[i]], tops[i])
        i += 1
    tot = caspoly.R0
    for c in a:
        tot = caspoly.radd(tot, c)
    if not caspoly.rzero(tot):
        raise ValueError('the numerators do not cancel')
    bs = []
    acc = caspoly.R0
    j = 0
    while j < m:
        acc = caspoly.radd(acc, a[j])
        bs.append(acc)
        j += 1

    q = 1
    jj = 0
    while jj < len(bs):
        if not caspoly.rzero(bs[jj]):
            q = casutil.lcm(q, bs[jj][1])
            q = casutil.lcm(q, caspoly.radd(omin, (jj, 1))[1])
        jj += 1

    def build(var, shift):
        node = None
        jj2 = 0
        while jj2 < len(bs):
            if not caspoly.rzero(bs[jj2]):
                kv = ('v', var) if q == 1 else ('*', ('n', q), ('v', var))
                off = caspoly.rmul((q, 1), caspoly.radd(omin, (jj2 + shift, 1)))
                if caspoly.rzero(off):
                    den = kv
                elif off[0] < 0:
                    den = ('-', kv, caspoly.ratnode(caspoly.rneg(off)))
                else:
                    den = ('+', kv, caspoly.ratnode(off))
                num = caspoly.rmul(bs[jj2], (q, 1))
                neg = num[0] < 0
                piece = ('/', caspoly.ratnode(caspoly.rneg(num) if neg else num), den)
                if node is None:
                    node = ('neg', piece) if neg else piece
                else:
                    node = ('-', node, piece) if neg else ('+', node, piece)
            jj2 += 1
        return node

    def gval(rv):
        tot2 = 0.0
        jj = 0
        while jj < len(bs):
            den = _ratf(kk) * (rv + _ratf(caspoly.radd(omin, (jj, 1))))
            if den == 0:
                return None
            tot2 += _ratf(bs[jj]) / den
            jj += 1
        return tot2

    g = build('r', 0)
    if g is None:
        raise ValueError('the terms cancel to nothing')
    for rv in (1.0, 2.0, 3.5, 7.0):
        try:
            lhs = caseng.evalf(fr, 0.0, False, {'r': rv})
        except Exception:
            continue
        g1 = gval(rv)
        g2 = gval(rv + 1.0)
        if g1 is None or g2 is None:
            continue
        if abs(lhs - (g1 - g2)) > 1e-9 * (1.0 + abs(lhs)):
            raise ValueError('f(r) is not g(r) - g(r+1)')
    gn = build('n', 1)
    g1v = casutil.clean(gval(1.0))
    gs = caseng.tostr(gn)
    if ('+' in gs) or ('-' in gs[1:]):
        gs = '(' + gs + ')'
    out = ['g(r) = ' + caseng.tostr(g),
           'S(n) = ' + _f(g1v) + ' - ' + gs]
    if n is not None:
        nn = _iv(n, 'n', 1, 1000000000)
        gt = gval(float(nn) + 1.0)
        if gt is None:
            raise ValueError('g is undefined at n+1')
        out.append('S(' + str(nn) + ') = ' + _f(casutil.clean(g1v - gt)))
    out.append(_w('f(r) = g(r) - g(r+1), so the sum telescopes'))
    out.append(_w('S(n) = g(1) - g(n+1), g(1) = ' + _f(g1v)))
    out.append(_w('as n -> inf, S(n) -> ' + _f(g1v) + ' if g(n+1) -> 0'))
    return out

def _cfrat(x):
    # best rational n/d (d <= 100000) by continued fractions, or None
    if isinstance(x, complex) or x != x or abs(x) > 1e12:
        return None
    sgn = -1 if x < 0 else 1
    y = abs(x)
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    r = y
    i = 0
    while i < 30:
        a = int(r)
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        if k1 > 100000:
            return None
        if abs(h1 * 1.0 / k1 - y) < 1e-10 * (1.0 + y):
            return (sgn * h1, k1)
        f = r - a
        if f < 1e-14:
            return None
        r = 1.0 / f
        i += 1
    return None

def _ratcoef(v, fact):
    q = _cfrat(v)
    if q is None:
        return None
    return caspoly.rmake(q[0], q[1] * fact)

_GEN = (('e^(x)', 'term r: x^r/r!'),
        ('sin(x)', 'term r: (-1)^r x^(2r+1)/(2r+1)!'),
        ('cos(x)', 'term r: (-1)^r x^(2r)/(2r)!'),
        ('ln(x+1)', 'term r: (-1)^(r+1) x^r/r'),
        ('ln(1+x)', 'term r: (-1)^(r+1) x^r/r'))

_ALL = (None, False, None, False)

def _ival_and(I, J):
    # intersection of intervals (lo, lo incl, hi, hi incl); None = unknown
    if I is None or J is None:
        return None
    lo, li = I[0], I[1]
    if J[0] is not None and (lo is None or J[0] > lo or (J[0] == lo and not J[1])):
        lo, li = J[0], J[1]
    hi, hin = I[2], I[3]
    if J[2] is not None and (hi is None or J[2] < hi or (J[2] == hi and not J[3])):
        hi, hin = J[2], J[3]
    return (lo, li, hi, hin)

def _linx(t):
    # (c, a) when t = c + a x, else None
    try:
        P = caspoly.poly(t, 'x')
    except Exception:
        return None
    if P is None or len(P) > 2:
        return None
    c = P[0][0] * 1.0 / P[0][1] if len(P) > 0 else 0.0
    a = P[1][0] * 1.0 / P[1][1] if len(P) > 1 else 0.0
    return (c, a)

def _constv(t):
    try:
        v = caseng.evalf(t, 0.0, False, {})
    except Exception:
        return None
    return None if isinstance(v, complex) else v

def _ipow(base, p):
    # interval where the binomial series of base^p converges
    if abs(p - int(p)) < 1e-12 and p >= 0:
        return _ival(base)
    if base[0] == '^' and not cascalc.has_var(base[2], 'x'):
        q = _constv(base[2])
        return None if q is None else _ipow(base[1], p * q)
    if base[0] == 'sqrt':
        return _ipow(base[1], p * 0.5)
    L = _linx(base)
    if L is None:
        return None
    c, a = L
    if a == 0:
        return _ALL
    if c == 0:
        return None
    r = abs(c / a)
    return (-r, False, r, False)

def _ival(t):
    # s4/s5: interval of validity of the Maclaurin series of t
    if not cascalc.has_var(t, 'x'):
        return _ALL
    k = t[0]
    if k == 'v':
        return _ALL
    if k in ('+', '-', '*'):
        return _ival_and(_ival(t[1]), _ival(t[2]))
    if k == 'neg' or k in ('exp', 'sin', 'cos', 'sinh', 'cosh'):
        return _ival(t[1])
    if k == '/':
        if not cascalc.has_var(t[2], 'x'):
            return _ival(t[1])
        return _ival_and(_ival(t[1]), _ipow(t[2], -1.0))
    if k == '^':
        if not cascalc.has_var(t[2], 'x'):
            p = _constv(t[2])
            return None if p is None else _ipow(t[1], p)
        if not cascalc.has_var(t[1], 'x'):
            return _ival(t[2])
        return None
    if k == 'sqrt':
        return _ipow(t[1], 0.5)
    if k == 'ln':
        L = _linx(t[1])
        if L is None or L[0] <= 0:
            return None
        c, a = L
        if a == 0:
            return _ALL
        r = c / abs(a)
        return (-r, False, r, True) if a > 0 else (-r, True, r, False)
    if k == 'atan':
        L = _linx(t[1])
        if L is None or L[0] != 0 or L[1] == 0:
            return None
        r = 1.0 / abs(L[1])
        return (-r, True, r, True)
    return None

def _ivalstr(I):
    if I[0] is None and I[2] is None:
        return 'valid for all x'
    s = ''
    if I[0] is not None:
        s = _f(casutil.clean(I[0])) + (' <= ' if I[1] else ' < ')
    s += 'x'
    if I[2] is not None:
        s += (' <= ' if I[3] else ' < ') + _f(casutil.clean(I[2]))
    return 'valid for ' + s

def _inival(I, x):
    if I[0] is not None and (x < I[0] or (x == I[0] and not I[1])):
        return False
    if I[2] is not None and (x > I[2] or (x == I[2] and not I[3])):
        return False
    return True

def _mac(f, n):
    # coefficients c_0..c_n (floats) and the series as a tree
    for v in caseng.vars_in(f):
        if v != 'x':
            raise ValueError('f(x): type it in x')
    co = []
    rat = []
    ok = True
    d = f
    fact = 1
    k = 0
    while k <= n:
        if k:
            fact *= k
        v = _at(d, 'x', 0.0)
        if v is None:
            raise ValueError('undefined at x = 0 (term ' + str(k) + ')')
        co.append(v / fact)
        r = _ratcoef(v, fact)
        if r is None:
            ok = False
        else:
            rat.append(r)
        if k < n:
            try:
                d = caseng.simplify(caseng.diff(d, 'x'))
            except Exception:
                raise ValueError('cannot differentiate that far')
        k += 1
    if ok:
        tree = caseng.simplify(caspoly.ptree(caspoly.ptrim(rat), 'x'))
    else:
        tree = _polytree(co, 'x')
    return co, tree

def t_maclaurin(f, n):
    # s3, s4, s5
    n = _iv(n, 'n', 1, 8)
    co, tree = _mac(f, n)
    out = ['f(x) =', _m(tree)]
    I = _ival(f)
    if I is None:
        out.append(_warn('validity: not a standard form'))
    elif I[0] is None and I[2] is None:
        out.append(_w('valid for all x'))
    else:
        out.append(_warn(_ivalstr(I)))
    key = caseng.tostr(caseng.simplify(f))
    for nm, gen in _GEN:
        if key == nm:
            out.append(_w(gen))
    out.append(_w('terms up to x^' + str(n) + '; c_r = f^(r)(0)/r!'))
    out.append(_w('f(0) = ' + _f(co[0]) + ', f\'(0) = ' + _f(co[1])))
    return out

def t_macapprox(f, n, a):
    # s3: use the series to approximate f(a)
    n = _iv(n, 'n', 1, 8)
    co, tree = _mac(f, n)
    s = 0.0
    k = n
    while k >= 0:
        s = s * a + co[k]
        k -= 1
    out = ['series = ' + casutil.sf3(s)]
    tv = _at(f, 'x', a)
    if tv is None:
        out.append(_warn('f is undefined at x = ' + _f(a)))
    else:
        out.append('f(a) = ' + casutil.sf3(tv))
        out.append('error = ' + casutil.sf3(tv - s))
    I = _ival(f)
    if I is None:
        out.append(_warn('validity: not a standard form'))
    elif not _inival(I, a):
        out.append(_warn('x = ' + _f(a) + ' is outside the interval'))
        out.append(_warn(_ivalstr(I)))
    else:
        out.append(_w(_ivalstr(I)))
    out.append(_w('series to x^' + str(n) + ': ' + caseng.tostr(tree)[:34]))
    out.append(_w('series value ' + _f(s, 6)))
    return out

def _torat(v):
    if isinstance(v, complex):
        return None
    q = 1
    while q <= 24:
        t = v * q
        n = int(t + 0.5) if t >= 0 else -int(-t + 0.5)
        if abs(v - n * 1.0 / q) < 1e-12 * (1.0 + abs(v)):
            return caspoly.rmake(n, q)
        q += 1
    return None

def t_binom(p, n):
    n = _iv(n, 'n', 1, 10)
    co = []
    c = 1.0
    k = 0
    while k <= n:
        co.append(c)
        c = c * (p - k) / (k + 1)
        k += 1
    rat = []
    pr = _torat(p)
    ok = pr is not None
    if ok:
        cr = caspoly.R1
        k = 0
        while k <= n:
            rat.append(cr)
            cr = caspoly.rdiv(caspoly.rmul(cr, caspoly.rsub(pr, (k, 1))), (k + 1, 1))
            k += 1
    if ok:
        tree = caseng.simplify(caspoly.ptree(caspoly.ptrim(rat), 'x'))
    else:
        tree = _polytree(co, 'x')
    out = ['(1+x)^' + _f(p) + ' =', _m(tree)]
    ip = (not isinstance(p, complex)) and p == int(p) and p >= 0
    if ip and p <= n:
        out.append(_w('p is a whole number: the series stops'))
    else:
        out.append(_warn('valid only for |x| < 1'))
    out.append(_w('c_r = p(p-1)...(p-r+1)/r!'))
    out.append(_w('terms up to x^' + str(n)))
    return out

SECTIONS = [
    # Pp4 sum / nth term / M^n, Pp5 divisibility / de Moivre, * counter-example
    ('P', 'Proof', [
        ('Induction: sum', 'u(r),S(n)', t_ind_sum),
        ('Induction: recurrence', 'f(u n),u1,g(n)', t_ind_rec),
        ('Induction: M^n', 'A[2x2],p(n),q(n),r(n),s(n)', t_ind_mpow),
        ('Induction: divisor', 'f(n),k,m?', t_ind_div),
        ('Induction: de Moivre', 'theta,n', t_ind_dm),
        ('Counterexample: prime', 'f(n),a,b', t_cx_prime),
        ('Counterexample: f > g', 'f(n),g(n),a,b', t_cx_ineq),
    ]),
    # Pj1 j2-j4 j6-j11 Pj12 j13-j16 j19 j20
    ('J', 'Complex numbers', [
        ('Arithmetic z, w', 'z,w', t_zw),
        ('Argand sum/product', 'z,w', t_argops),
        ('Modulus-argument', 'z', t_modarg),
        ('From mod-arg form', 'r,theta', t_frommodarg),
        ('Multiply in mod-arg', 'r1,t1,r2,t2', t_mamul),
        ('De Moivre z^n', 'z,n', t_zpow),
        ('nth roots of z', 'z,n', t_nroots),
        ('Roots of unity', 'n', t_unity),
        ('Polygon: centre+vertex', 'z1,z2,n', t_poly_centre),
        ('Polygon: two vertices', 'z1,z2,n', t_poly_edge),
        ('Quadratic roots', 'a,b,c', t_quad),
        ('Cubic real coeffs', 'a,b,c,d,z?', t_cubic),
        ('Quartic real coeffs', 'a,b,c,d,e,z?', t_quartic),
        ('Argand plot', 'data*', t_argand),
        ('Locus |z-z1| = r', 'z1,r', t_loc_circle),
        ('Locus arg(z-z1) = t', 'z1,theta', t_loc_halfline),
        ('Locus |z-z1|=|z-z2|', 'z1,z2', t_loc_bisect),
        ('cos nt, sin nt powers', 'n', t_multangle),
        ('cos^n t, sin^n t', 'n', t_powtomult),
    ]),
    # Pm1 m4 m5 m7-m9 m11-m13 m15 Pm6 (m2 m3 m10 m14 are properties to quote)
    ('M', 'Matrices, transformations', [
        ('pA + qB (2x2)', 'p,q,A[2x2],B[2x2]', t_lin2),
        ('pA + qB (3x3)', 'p,q,A[3x3],B[3x3]', t_lin3),
        ('AB and BA (2x2)', 'A[2x2],B[2x2]', t_mul2),
        ('AB and BA (3x3)', 'A[3x3],B[3x3]', t_mul3),
        ('Determinant 2x2', 'A[2x2]', t_det2),
        ('Determinant 3x3', 'A[3x3]', t_det3),
        ('Det 3x3 in terms of k', 'a(k),b(k),c(k),d(k),e(k),f(k),g(k),h(k),i(k)', t_detk),
        ('Inverse 2x2', 'A[2x2]', t_inv2),
        ('Inverse 3x3', 'A[3x3]', t_inv3),
        ('Solve 3 eqns by A^-1', 'A[3x3],b[3]', t_solve3),
        ('Rotation 2D (deg)', 'theta', t_rot2),
        ('Reflect in y=x tan t', 'theta', t_ref2),
        ('Stretch or enlarge 2D', 'p,q', t_stretch2),
        ('Shear 2D', 'k,axis', t_shear2),
        ('Describe a 2x2', 'A[2x2]', t_describe),
        ('A then B (2x2)', 'A[2x2],B[2x2]', t_then2),
        ('Rotation 3D (axis)', 'axis,theta', t_rot3),
        ('Reflect 3D in plane', 'plane', t_ref3),
        ('Describe a 3x3', 'A[3x3]', t_describe3),
        ('A then B (3x3)', 'A[3x3],B[3x3]', t_then3),
        ('Invariant points/lines', 'A[2x2]', t_invar),
    ]),
    # Pv1 v2-v6 Pv7 v8-v13 Pv14 v15-v17
    ('V', 'Vectors and 3-D', [
        ('Scalar product, angle', 'a[3],b[3]', t_scalar),
        ('Perpendicular check', 'a[3],b[3]', t_perp_check),
        ('Vector product', 'a[3],b[3]', t_cross),
        ('Area of triangle', 'A[3],B[3],C[3]', t_tri_area),
        ('Line from two points', 'A[3],B[3]', t_line_2pts),
        ('Line to cartesian', 'a[3],d[3]', t_line_cart),
        ('Is p on (r-a)xb=0', 'a[3],b[3],p[3]', t_on_line),
        ('Plane from 3 points', 'A[3],B[3],C[3]', t_plane_3pts),
        ('Plane point + normal', 'p[3],n[3]', t_plane_pt_n),
        ('Plane pt + 2 dirs', 'a[3],b[3],c[3]', t_plane_2dirs),
        ('Plane cartesian->vec', 'n[3],d', t_plane_to_vec),
        ('Three planes', 'n1[3],d1,n2[3],d2,n3[3],d3', t_planes3),
        ('Angle between lines', 'd1[3],d2[3]', t_angle_lines),
        ('Angle line and plane', 'd[3],n[3]', t_angle_lp),
        ('Angle between planes', 'n1[3],n2[3]', t_angle_planes),
        ('Intersect two lines', 'a1[3],d1[3],a2[3],d2[3]', t_line_meet),
        ('Distance two lines', 'a1[3],d1[3],a2[3],d2[3]', t_line_dist),
        ('Line meets plane', 'a[3],d[3],n[3],k', t_line_plane),
        ('Point to line dist', 'p[3],a[3],d[3]', t_pt_line),
        ('Point to plane dist', 'p[3],n[3],k', t_pt_plane),
    ]),
    # Pa1 a2 (quadratic, cubic, quartic)
    ('A', 'Roots of polynomials', [
        ('Vieta root sums', 'coeffs*', t_vieta),
        ('Power sums of roots', 'k,coeffs*', t_powersums),
        ('Roots p a + q', 'p,q,coeffs*', t_rootlin),
        ('Roots 1/a', 'coeffs*', t_rootrecip),
        ('Roots a^2', 'coeffs*', t_rootsq),
    ]),
    # Ps1 Ps2 s3 s4 s5
    ('S', 'Series, Maclaurin', [
        ('Sum r, r^2, r^3', 'n', t_sumpow),
        ('Sum f(r), r = a..b', 'f(r),a,b?', t_sumpoly),
        ('Method of differences', 'f(r),n?', t_diffs),
        ('Maclaurin series', 'f(x),n', t_maclaurin),
        ('Maclaurin approx', 'f(x),n,a', t_macapprox),
        ('Binomial (1+x)^p', 'p,n', t_binom),
    ]),
]
