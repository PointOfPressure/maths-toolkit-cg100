# AQA Further Maths 7367 sections A-D: proof, complex numbers, matrices,
# further algebra and functions.
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

# ---- A  Proof ---------------------------------------------------------------

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

# ---- B  Complex numbers -----------------------------------------------------

def _pol(z):
    return (_abs(z), _arg(z))

def _snaprat(x):
    q = 1
    while q <= 24:
        t = x * q
        n = int(t + 0.5) if t >= 0 else -int(-t + 0.5)
        if abs(x - n * 1.0 / q) < 1e-6 * (1.0 + abs(x)):
            return casutil.clean(n * 1.0 / q)
        q += 1
    return x

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

def t_gsum(z, w, n):
    n = _iv(n, 'n', 1, 400)
    if w == 1:
        s = z * n
    else:
        s = z * (1 - caseng._cpow(_cx(w), n)) / (1 - _cx(w))
    s = casutil.clean(s)
    lines = ['S = ' + _f(s), '|S| = ' + _f(_abs(s))]
    if w != 1:
        lines.append(_w('S = a(1-r^n)/(1-r), r^n = ' +
                        _f(casutil.clean(caseng._cpow(_cx(w), n)))))
    else:
        lines.append(_w('r = 1, so S = n a'))
    if _abs(w) < 1:
        lines.append('S(infinity) = ' + _f(casutil.clean(z / (1 - _cx(w)))))
        lines.append(_w('|r| = ' + _f(_abs(w)) + ' < 1, so it converges'))
    else:
        lines.append(_warn('|r| = ' + _f(_abs(w)) + ' >= 1: no sum to infinity'))
    return lines

# ---- C  Matrices ------------------------------------------------------------

def _eqstr(co, var):
    # co high->low, numeric -> 'L^3-6L^2+11L-6'
    out = ''
    n = len(co) - 1
    i = 0
    while i <= n:
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
        i += 1
    return out if out else '0'

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
    aug = [A[i] + [b[i]] for i in range(3)]
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
    ra = _rank(A, _tol(A))
    rb = _rank(aug, _tol(aug))
    out = ['det A = 0: no unique solution']
    if ra == 2 and rb == 2:
        dirv = None
        if not _para(A[0], A[1]):
            dirv = _cross(A[0], A[1])
        elif not _para(A[0], A[2]):
            dirv = _cross(A[0], A[2])
        else:
            dirv = _cross(A[1], A[2])
        out.append('planes meet in a line (sheaf)')
        out.append('direction ' + casutil.fmtv(_scale(dirv)))
        out.append(_w('consistent: infinitely many solutions'))
    elif ra == 2 and rb == 3:
        par = _para(A[0], A[1]) or _para(A[0], A[2]) or _para(A[1], A[2])
        if par:
            out.append('two planes are parallel')
            out.append('no solution')
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
        out.append(_warn('degenerate: a row of A is all zero'))
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

def t_describe(A):
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
    det = _det2(A)
    out = []
    if b == 0 and c == 0:
        if a == d:
            out.append('enlargement scale factor ' + _f(a))
        else:
            out.append('stretch x by ' + _f(a) + ', y by ' + _f(d))
    elif abs(a - d) < 1e-12 and abs(b + c) < 1e-12 and abs(det - (a * a + c * c)) < 1e-9:
        r = math.sqrt(a * a + c * c)
        th = math.atan2(c, a) * 180.0 / PI
        if abs(r - 1.0) < 1e-9:
            out.append('rotation ' + _f(_snap(th)) + ' deg about O')
        else:
            out.append('rotation ' + _f(_snap(th)) + ' deg, enlarge ' + _f(r))
    elif abs(a + d) < 1e-12 and abs(b - c) < 1e-12 and abs(det + (a * a + b * b)) < 1e-9:
        r = math.sqrt(a * a + b * b)
        th = 0.5 * math.atan2(b, a) * 180.0 / PI
        if abs(r - 1.0) < 1e-9:
            out.append('reflection in y = x tan ' + _f(_snap(th)) + ' deg')
        else:
            out.append('reflect in y = x tan ' + _f(_snap(th)) + ', enlarge ' + _f(r))
    elif a == 1 and d == 1 and c == 0:
        out.append('shear, x-axis invariant, factor ' + _f(b))
    elif a == 1 and d == 1 and b == 0:
        out.append('shear, y-axis invariant, factor ' + _f(c))
    else:
        out.append('not a standard transformation')
    out.append('det = ' + _f(det))
    if det < 0:
        out.append(_w('det < 0: orientation reversed'))
    out.append(_w('rotation: [[c,-s],[s,c]]; reflection: [[c,s],[s,-c]]'))
    return out

_AXN = ('x', 'y', 'z')

def t_rot3(axis, theta):
    ax = _iv(axis, 'axis', 1, 3)
    t = theta * PI / 180.0
    c = _snap(math.cos(t))
    s = _snap(math.sin(t))
    if ax == 1:
        M = [[1, 0, 0], [0, c, -s], [0, s, c]]
    elif ax == 2:
        M = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    else:
        M = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    out = _mlines('R', M)
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

def _eig2(A):
    a = A[0][0]
    b = A[0][1]
    c = A[1][0]
    d = A[1][1]
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

def t_eig2(A):
    tr, det, disc = _eig2(A)
    out = []
    out.append('char eq: ' + _eqstr([1, -tr, det], 'L') + ' = 0')
    if disc < -1e-12:
        s = math.sqrt(-disc)
        l1 = complex(tr / 2.0, s / 2.0)
        out.append('L = ' + _f(casutil.clean(l1)) + ' and its conjugate')
        out.append(_warn('no real eigenvalues, so no real'))
        out.append(_warn('eigenvectors (a rotation-like map)'))
        out.append(_w('disc = ' + _f(disc) + ' < 0'))
        return out
    if disc < 0:
        disc = 0.0
    rt = math.sqrt(disc)
    l1 = _snap((tr + rt) / 2.0)
    l2 = _snap((tr - rt) / 2.0)
    v1 = _vec2(A, l1)
    out.append('L1 = ' + _f(l1) + ', v1 = ' + casutil.fmtv(v1))
    if abs(l1 - l2) < 1e-9:
        nl = _nullity([[A[0][0] - l1, A[0][1]], [A[1][0], A[1][1] - l1]])
        out.append(_warn('repeated eigenvalue L = ' + _f(l1)))
        if nl >= 2:
            out.append(_w('eigenspace is 2D: A is ' + _f(l1) + ' I'))
        else:
            out.append(_w('only one eigenvector: not diagonalisable'))
    else:
        out.append('L2 = ' + _f(l2) + ', v2 = ' + casutil.fmtv(_vec2(A, l2)))
        out.append(_w('distinct eigenvalues, so diagonalisable'))
    out.append(_w('trace = ' + _f(tr) + ' = L1+L2, det = ' + _f(det) + ' = L1L2'))
    out.append(_w('Av = Lv: v keeps its direction, scaled by L'))
    return out

def _charpoly3(A):
    tr = A[0][0] + A[1][1] + A[2][2]
    m2 = ((A[1][1] * A[2][2] - A[1][2] * A[2][1])
          + (A[0][0] * A[2][2] - A[0][2] * A[2][0])
          + (A[0][0] * A[1][1] - A[0][1] * A[1][0]))
    return [1, -tr, m2, -_det3(A)]

def _realeigs(A):
    co = _charpoly3(A)
    out = []
    for r in _roots(co):
        if not isinstance(r, complex):
            out.append(_snap(r))
    out.sort()
    return co, out

def t_eig3(A):
    co, ls = _realeigs(A)
    out = ['char eq: ' + _eqstr(co, 'L') + ' = 0']
    if not ls:
        out.append(_warn('no real eigenvalues'))
        return out
    seen = []
    for L in ls:
        rep = False
        for s in seen:
            if abs(s - L) < 1e-9:
                rep = True
        seen.append(L)
        if rep:
            continue
        S = [[A[i][j] - (L if i == j else 0) for j in range(3)] for i in range(3)]
        v = _nullvec(S)
        cnt = 0
        for s in ls:
            if abs(s - L) < 1e-9:
                cnt += 1
        tag = '' if cnt == 1 else ' (x' + str(cnt) + ')'
        if v is None:
            out.append('L = ' + _f(L) + tag + ': no eigenvector')
        else:
            out.append('L = ' + _f(L) + tag + ', v = ' + casutil.fmtv(v))
            if cnt > 1:
                nl = _nullity(S)
                out.append(_warn('repeated L: eigenspace is ' + str(nl) + 'D'))
    out.append(_w('trace = ' + _f(-co[1]) + ' = sum of eigenvalues'))
    out.append(_w('det = ' + _f(-co[3]) + ' = product of eigenvalues'))
    out.append(_w('solve (A - L I)v = 0 for each L'))
    return out

def _diaglines(A, ls, vs, n, out):
    U = []
    i = 0
    while i < len(A):
        U.append([vs[j][i] for j in range(len(ls))])
        i += 1
    for ln in _mlines('U', U):
        out.append(ln)
    D = [[ls[i] if i == j else 0 for j in range(len(ls))] for i in range(len(ls))]
    for ln in _mlines('D', D):
        out.append(_w(ln))
    if n is not None:
        nn = _iv(n, 'n', 0, 40)
        for ln in _mlines('M^' + str(nn), _mpow(A, nn)):
            out.append(ln)
        out.append(_w('M^n = U D^n U^-1, D^n = diag of L^n'))
        ps = []
        for L in ls:
            ps.append(_f(L) + '^' + str(nn) + ' = ' + _f(casutil.clean(L ** nn)))
        out.append(_w(', '.join(ps)))
    else:
        out.append(_w('M^n = U D^n U^-1, D^n = diag of L^n'))

def t_diag2(A, n):
    tr, det, disc = _eig2(A)
    if disc < -1e-12:
        return ['not diagonalisable over the reals',
                _warn('the eigenvalues are complex')]
    rt = math.sqrt(disc if disc > 0 else 0.0)
    l1 = _snap((tr + rt) / 2.0)
    l2 = _snap((tr - rt) / 2.0)
    if abs(l1 - l2) < 1e-9 and _nullity([[A[0][0] - l1, A[0][1]],
                                         [A[1][0], A[1][1] - l1]]) < 2:
        return ['not diagonalisable',
                _warn('repeated L = ' + _f(l1) + ' with one eigenvector')]
    v1 = _vec2(A, l1)
    v2 = _vec2(A, l2)
    if abs(l1 - l2) < 1e-9:
        v1 = [1, 0]
        v2 = [0, 1]
    out = ['M = U D U^-1, D = diag(' + _f(l1) + ', ' + _f(l2) + ')']
    _diaglines(A, [l1, l2], [v1, v2], n, out)
    out.append(_w('U columns are the eigenvectors, in the'))
    out.append(_w('same order as the eigenvalues in D'))
    return out

def t_diag3(A, n):
    co, ls = _realeigs(A)
    vs = []
    ok = len(ls) == 3
    if ok:
        for L in ls:
            S = [[A[i][j] - (L if i == j else 0) for j in range(3)] for i in range(3)]
            v = _nullvec(S)
            if v is None:
                ok = False
                break
            vs.append(v)
    if ok:
        U = [[vs[j][i] for j in range(3)] for i in range(3)]
        if _det3(U) == 0:
            ok = False
    if not ok:
        return ['not diagonalisable over the reals',
                _warn('needs 3 independent real eigenvectors'),
                _w('char eq: ' + _eqstr(co, 'L') + ' = 0')]
    out = ['M = U D U^-1',
           'D = diag(' + _f(ls[0]) + ', ' + _f(ls[1]) + ', ' + _f(ls[2]) + ')']
    _diaglines(A, ls, vs, n, out)
    return out

# ---- D  Further algebra and functions ---------------------------------------

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

def _ratcoef(v, fact):
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if abs(v - n) < 1e-9 * (1.0 + abs(v)):
        return caspoly.rmake(n, fact)
    return None

_GEN = (('e^(x)', 'term r: x^r/r!', ''),
        ('sin(x)', 'term r: (-1)^r x^(2r+1)/(2r+1)!', ''),
        ('cos(x)', 'term r: (-1)^r x^(2r)/(2r)!', ''),
        ('ln(x+1)', 'term r: (-1)^(r+1) x^r/r', 'valid for -1 < x <= 1'),
        ('ln(1+x)', 'term r: (-1)^(r+1) x^r/r', 'valid for -1 < x <= 1'))

def t_maclaurin(f, n):
    n = _iv(n, 'n', 1, 8)
    co = []
    rat = []
    ok = True
    d = f
    fact = 1
    k = 0
    while k <= n:
        if k:
            fact *= k
        v = casutil.evx(d, 0.0)
        if v is None:
            raise ValueError('undefined at x = 0 (term ' + str(k) + ')')
        co.append(v / fact)
        r = _ratcoef(v, fact)
        if r is None:
            ok = False
        else:
            rat.append(r)
        try:
            d = caseng.simplify(caseng.diff(d, 'x'))
        except Exception:
            raise ValueError('cannot differentiate that far')
        k += 1
    if ok:
        tree = caseng.simplify(caspoly.ptree(caspoly.ptrim(rat), 'x'))
    else:
        tree = _polytree(co, 'x')
    out = ['f(x) =', _m(tree)]
    key = caseng.tostr(caseng.simplify(f))
    for nm, gen, note in _GEN:
        if key == nm:
            out.append(_w(gen))
            if note:
                out.append(_warn(note))
    out.append(_w('terms up to x^' + str(n) + '; c_r = f^(r)(0)/r!'))
    out.append(_w('f(0) = ' + _f(co[0]) + ', f\'(0) = ' + _f(co[1] if n >= 1 else 0)))
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

def _side(f, a, sgn):
    vals = []
    h = 1e-4
    i = 0
    while i < 3:
        v = casutil.evx(f, a + sgn * h)
        if v is None:
            return None
        vals.append(v)
        h = h / 10.0
        i += 1
    if abs(vals[2] - vals[1]) > 1e-3 * (1.0 + abs(vals[2])):
        return None
    return vals[2]

def t_limit(f, a):
    lft = _side(f, a, -1.0)
    rgt = _side(f, a, 1.0)
    out = []
    lh = None
    if f[0] == '/':
        num = f[1]
        den = f[2]
        i = 0
        while i < 5:
            nv = casutil.evx(num, a)
            dv = casutil.evx(den, a)
            if nv is None or dv is None:
                break
            if abs(dv) > 1e-9:
                lh = nv / dv
                break
            if abs(nv) > 1e-9:
                lh = None
                break
            try:
                num = caseng.simplify(caseng.diff(num, 'x'))
                den = caseng.simplify(caseng.diff(den, 'x'))
            except Exception:
                break
            i += 1
        if lh is not None and i > 0:
            out.append('limit = ' + _f(casutil.clean(_snap(lh))))
            out.append(_w("l'Hopital " + str(i) + 'x: 0/0, differentiate top'))
            out.append(_w('and bottom, then put x = ' + _f(a)))
    if not out:
        if lft is None or rgt is None:
            raise ValueError('f(x) is not defined on both sides')
        if abs(lft - rgt) > 1e-3 * (1.0 + abs(rgt)):
            return ['no limit: the two sides differ',
                    'from below: ' + _f(lft), 'from above: ' + _f(rgt)]
        out.append('limit = ' + _f(casutil.clean(_snap((lft + rgt) / 2.0))))
        out.append(_w('numerically, from both sides'))
    v = casutil.evx(f, a)
    if v is not None:
        out.append(_w('f(' + _f(a) + ') = ' + _f(v) + ' (continuous there)'))
    else:
        out.append(_w('f is undefined at x = ' + _f(a)))
    if lft is not None:
        out.append(_w('x = ' + _f(a) + '-0.000001: ' + _f(lft)))
    if rgt is not None:
        out.append(_w('x = ' + _f(a) + '+0.000001: ' + _f(rgt)))
    return out

def _dens(t, out):
    if t[0] == '/':
        out.append(t[2])
    if len(t) >= 2 and isinstance(t[1], tuple):
        _dens(t[1], out)
    if len(t) >= 3 and isinstance(t[2], tuple):
        _dens(t[2], out)

def _addpt(lst, v):
    for u in lst:
        if abs(u - v) < 1e-6:
            return
    lst.append(v)

def _sign(h, x):
    v = casutil.evx(h, x)
    if v is None:
        return 0
    if v > 1e-12:
        return 1
    if v < -1e-12:
        return -1
    return 0

def _intervals(f, g, want):
    h = ('-', f, g)
    flat = True
    for xv in (-7.3, -2.1, -0.4, 0.6, 1.7, 5.2, 11.3):
        if _sign(h, xv) != 0:
            flat = False
            break
    if flat:
        return (['f(x) = g(x) where both are defined'], [])
    roots = []
    poles = []
    for r in cascalc.solve(h):
        v = casutil.evx(h, r)
        if v is None or abs(v) > 1e-4:
            _addpt(poles, r)
        else:
            _addpt(roots, r)
    ds = []
    _dens(h, ds)
    for d in ds:
        if cascalc.has_var(d, 'x'):
            for r in cascalc.solve(d):
                _addpt(poles, r)
    pts = []
    for r in roots:
        _addpt(pts, r)
    for r in poles:
        _addpt(pts, r)
    pts.sort()
    out = []
    if not pts:
        s = _sign(h, 0.0)
        if s == want:
            out.append('true for every x')
        else:
            out.append('no solutions')
        return out, pts
    i = 0
    while i <= len(pts):
        lo = pts[i - 1] if i > 0 else None
        hi = pts[i] if i < len(pts) else None
        if lo is None:
            mid = hi - 1.0
        elif hi is None:
            mid = lo + 1.0
        else:
            mid = (lo + hi) / 2.0
        if _sign(h, mid) == want:
            if lo is None:
                out.append('x < ' + _f(_snaprat(hi)))
            elif hi is None:
                out.append('x > ' + _f(_snaprat(lo)))
            else:
                out.append(_f(_snaprat(lo)) + ' < x < ' + _f(_snaprat(hi)))
        i += 1
    if not out:
        out.append('no solutions')
    return out, pts

def _ineq(f, g, want, sym):
    out, pts = _intervals(f, g, want)
    lines = []
    for ln in out:
        lines.append(ln)
    lines.append(_w('f(x) ' + sym + ' g(x): sign of f - g between'))
    lines.append(_w('its zeros and vertical asymptotes'))
    if pts:
        cs = ', '.join([_f(_snaprat(p)) for p in pts[:8]])
        lines.append(_w('critical values: ' + cs + ('..' if len(pts) > 8 else '')))
    lines.append(_warn('searched -20 < x < 20 only'))
    return lines

def t_ineq_gt(f, g):
    return _ineq(f, g, 1, '>')

def t_ineq_lt(f, g):
    return _ineq(f, g, -1, '<')

def _num(v):
    return ('n', casutil.clean(v))

def _linT(a, b):
    t = ('*', _num(a), ('v', 'x')) if a != 1 else ('v', 'x')
    if a == 0:
        return _num(b)
    if b == 0:
        return t
    return ('+', t, _num(b))

def _quadT(a, b, c):
    t = None
    if a != 0:
        t = ('^', ('v', 'x'), ('n', 2)) if a == 1 else \
            ('*', _num(a), ('^', ('v', 'x'), ('n', 2)))
    lb = _linT(b, c)
    if t is None:
        return lb
    if b == 0 and c == 0:
        return t
    return ('+', t, lb)

def _mxc(m, c):
    m = casutil.clean(m)
    c = casutil.clean(c)
    if m == 0:
        return 'y = ' + _f(c)
    ms = 'x' if m == 1 else ('-x' if m == -1 else _f(m) + 'x')
    if c == 0:
        return 'y = ' + ms
    return 'y = ' + ms + (' - ' if c < 0 else ' + ') + _f(-c if c < 0 else c)

def _plot1(tree, centre, title):
    import plot
    plot.run([tree], centre - 8.0, centre + 8.0, kind='y', title=title)

def _quadrange(A, B, C, D, E, F, out):
    P = E * E - 4.0 * D * F
    Q = 4.0 * A * F + 4.0 * C * D - 2.0 * B * E
    R = B * B - 4.0 * A * C
    ys = []
    if P == 0 and Q == 0:
        if R >= 0:
            out.append('y can take any value')
        else:
            out.append(_warn('no real y: check the coefficients'))
    elif P == 0:
        y0 = _snaprat(-R / Q)
        out.append('range: y ' + ('>= ' if Q > 0 else '<= ') + _f(y0))
        ys = [y0]
    else:
        dd = Q * Q - 4.0 * P * R
        if dd < 0:
            out.append('range: ' + ('every real y' if P > 0 else 'no real y'))
        else:
            sq = math.sqrt(dd)
            y1 = _snaprat((-Q - sq) / (2.0 * P))
            y2 = _snaprat((-Q + sq) / (2.0 * P))
            if y1 > y2:
                y1, y2 = y2, y1
            ys = [y1, y2]
            if P > 0:
                out.append('range: y <= ' + _f(y1) + ' or y >= ' + _f(y2))
            else:
                out.append('range: ' + _f(y1) + ' <= y <= ' + _f(y2))
    for y in ys:
        den = 2.0 * (A - y * D)
        if abs(den) > 1e-12:
            out.append('stationary point (' +
                       _f(_snaprat(-(B - y * E) / den)) + ', ' + _f(y) + ')')
    out.append(_w('y(Dx^2+Ex+F) = Ax^2+Bx+C, so'))
    out.append(_w('(A-yD)x^2+(B-yE)x+(C-yF) = 0'))
    out.append(_w('real x needs ' + _eqstr([P, Q, R], 'y') + ' >= 0'))

def t_rat1(a, b, c, d):
    if c == 0:
        raise ValueError('c = 0: this is a straight line')
    if a * d - b * c == 0:
        return ['constant: y = ' + _f(a * 1.0 / c),
                _warn('the factors cancel')]
    va = _snaprat(-d * 1.0 / c)
    tree = ('/', _linT(a, b), _linT(c, d))
    _plot1(tree, va, 'y = (ax+b)/(cx+d)')
    out = ['vertical asymptote x = ' + _f(va),
           'horizontal asymptote y = ' + _f(casutil.clean(a * 1.0 / c))]
    if a != 0:
        out.append('crosses x-axis at ' + _f(_snaprat(-b * 1.0 / a)))
    else:
        out.append(_w('a = 0: never crosses the x-axis'))
    if d != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(b * 1.0 / d)))
    else:
        out.append(_w('d = 0: the y-axis is the asymptote'))
    out.append(_w('x -> inf gives y -> a/c; x = -d/c kills the'))
    out.append(_w('denominator'))
    return out

def t_rat2(a, b, c, d, e):
    if d == 0:
        raise ValueError('d = 0: use the (ax+b)/(cx+d) tool')
    if a == 0:
        raise ValueError('a = 0: use the (ax+b)/(cx+d) tool')
    va = _snaprat(-e * 1.0 / d)
    mg = a * 1.0 / d
    kk = (b - mg * e) * 1.0 / d
    rem = c - kk * e
    tree = ('/', _quadT(a, b, c), _linT(d, e))
    _plot1(tree, va, 'y = (ax^2+bx+c)/(dx+e)')
    out = ['vertical asymptote x = ' + _f(va)]
    if rem == 0:
        out.append(_mxc(mg, kk) + ' (a straight line)')
        out.append(_warn('exact division: a hole at x = ' + _f(va)))
    else:
        out.append('oblique asymptote ' + _mxc(mg, kk))
    if e != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(c * 1.0 / e)))
    rs = _roots([a, b, c])
    xs = []
    for r in rs:
        if not isinstance(r, complex):
            xs.append(_f(_snaprat(r)))
    xs.sort()
    out.append('crosses x-axis at ' + ', '.join(xs) if xs else 'no x-intercept')
    _quadrange(a, b, c, 0.0, d, e, out)
    out.append(_w('divide out: ' + _mxc(mg, kk) + ' + ' +
                  _f(casutil.clean(rem)) + '/(' + _f(d) + 'x+' + _f(e) + ')'))
    return out

def t_rat3(a, b, c, d, e, f):
    if d == 0:
        raise ValueError('d = 0: use the quad/linear tool')
    tree = ('/', _quadT(a, b, c), _quadT(d, e, f))
    dr = _roots([d, e, f])
    vas = []
    for r in dr:
        if not isinstance(r, complex):
            vas.append(_snaprat(r))
    vas.sort()
    _plot1(tree, vas[0] if vas else 0.0, 'y = quad/quad')
    out = []
    if vas:
        out.append('vertical asymptotes x = ' +
                   ', '.join([_f(v) for v in vas]))
    else:
        out.append('no vertical asymptote')
    out.append('horizontal asymptote y = ' + _f(casutil.clean(a * 1.0 / d)))
    if f != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(c * 1.0 / f)))
    xs = []
    for r in _roots([a, b, c]) if a or b else []:
        if not isinstance(r, complex):
            xs.append(_f(_snaprat(r)))
    xs.sort()
    out.append('crosses x-axis at ' + ', '.join(xs) if xs else 'no x-intercept')
    _quadrange(a, b, c, d, e, f, out)
    return out

def t_absgraph(fx):
    import plot
    af = ('abs', fx)
    fa = caseng.subst(fx, 'x', ('abs', ('v', 'x')))
    plot.run([fx, af, fa], -6.0, 6.0, kind='y', title='f, |f|, f(|x|)')
    zs = cascalc.solve(fx)
    out = []
    if zs:
        out.append('zeros of f: ' + ', '.join([_f(_snaprat(z)) for z in zs]))
        out.append('|f| has a corner at each of them')
    else:
        out.append('f has no zero in -20 < x < 20')
    y0 = casutil.evx(fx, 0.0)
    if y0 is not None:
        out.append('f(0) = ' + _f(casutil.clean(y0)))
    out.append(_w('|f(x)|: reflect the part below the x-axis'))
    out.append(_w('f(|x|): keep x >= 0 and mirror it in the y-axis'))
    out.append(_warn('zeros searched in -20 < x < 20'))
    return out

def _conicplot(curves, title):
    import plot
    plot.run(curves, kind='param', title=title)

def t_parab(a):
    if a == 0:
        raise ValueError('a must not be 0')
    xt = ('*', _num(a), ('^', ('v', 'x'), ('n', 2)))
    yt = ('*', _num(2.0 * a), ('v', 'x'))
    _conicplot([(xt, yt, -4.0, 4.0)], 'y^2 = 4ax')
    return ['y^2 = ' + _f(4.0 * a) + 'x, vertex (0, 0)',
            'focus (' + _f(a) + ', 0)',
            'directrix x = ' + _f(-a),
            'parametric (' + _f(a) + 't^2, ' + _f(2.0 * a) + 't)',
            _w('axis of symmetry y = 0'),
            _w('distance to focus = distance to directrix')]

def t_ellipse(a, b):
    if a <= 0 or b <= 0:
        raise ValueError('a and b must be > 0')
    xt = ('*', _num(a), ('cos', ('v', 'x')))
    yt = ('*', _num(b), ('sin', ('v', 'x')))
    _conicplot([(xt, yt, 0.0, 2.0 * PI)], 'ellipse')
    big = a if a > b else b
    sml = b if a > b else a
    ec = math.sqrt(1.0 - (sml * sml) / (big * big))
    out = ['x-intercepts (+/-' + _f(a) + ', 0)',
           'y-intercepts (0, +/-' + _f(b) + ')',
           'eccentricity e = ' + _f(_snaprat(ec))]
    if a > b:
        out.append('foci (+/-' + _f(_snaprat(a * ec)) + ', 0)')
    elif b > a:
        out.append('foci (0, +/-' + _f(_snaprat(b * ec)) + ')')
    else:
        out.append('a circle radius ' + _f(a))
    out.append(_w('parametric (' + _f(a) + 'cos t, ' + _f(b) + 'sin t)'))
    out.append(_w('b^2 = a^2(1 - e^2); area = pi ab = ' + _f(PI * a * b)))
    return out

def t_hyper(a, b):
    if a <= 0 or b <= 0:
        raise ValueError('a and b must be > 0')
    xt = ('*', _num(a), ('cosh', ('v', 'x')))
    yt = ('*', _num(b), ('sinh', ('v', 'x')))
    xt2 = ('*', _num(-a), ('cosh', ('v', 'x')))
    _conicplot([(xt, yt, -2.0, 2.0), (xt2, yt, -2.0, 2.0)], 'hyperbola')
    ec = math.sqrt(1.0 + (b * b) / (a * a))
    return ['vertices (+/-' + _f(a) + ', 0)',
            'asymptotes y = +/-' + _f(casutil.clean(b * 1.0 / a)) + 'x',
            'eccentricity e = ' + _f(_snaprat(ec)),
            'foci (+/-' + _f(_snaprat(a * ec)) + ', 0)',
            _w('parametric (' + _f(a) + 'sec t, ' + _f(b) + 'tan t)'),
            _w('or (+/-' + _f(a) + 'cosh t, ' + _f(b) + 'sinh t)'),
            _w('b^2 = a^2(e^2 - 1); no y-intercept')]

def t_recthyp(c):
    if c == 0:
        raise ValueError('c must not be 0')
    xt = ('*', _num(c), ('v', 'x'))
    yt = ('/', _num(c), ('v', 'x'))
    _conicplot([(xt, yt, 0.12, 8.0), (xt, yt, -8.0, -0.12)], 'xy = c^2')
    return ['xy = ' + _f(c * c) + ', asymptotes x = 0, y = 0',
            'vertices (' + _f(c) + ', ' + _f(c) + ') and (' +
            _f(-c) + ', ' + _f(-c) + ')',
            'parametric (' + _f(c) + 't, ' + _f(c) + '/t)',
            _w('the axes are the asymptotes; e = sqrt(2)'),
            _w('it is x^2-y^2 = ' + _f(2.0 * c * c) + ' turned 45 deg')]

def t_transform(fx, p, q, a, b):
    if p is None:
        p = 1
    if q is None:
        q = 1
    if a is None:
        a = 0
    if b is None:
        b = 0
    if p == 0 or q == 0:
        raise ValueError('p and q must not be 0')
    inner = ('-', ('v', 'x'), _num(a)) if a != 0 else ('v', 'x')
    if p != 1:
        inner = ('/', inner, _num(p))
    g = caseng.subst(fx, 'x', inner)
    if q != 1:
        g = ('*', _num(q), g)
    if b != 0:
        g = ('+', g, _num(b))
    try:
        g = caseng.simplify(g)
    except Exception:
        pass
    out = ['y =', _m(g)]
    out.append(_w('y = ' + _f(q) + ' f((x - ' + _f(a) + ')/' + _f(p) + ') + ' + _f(b)))
    if p != 1:
        out.append(_w('stretch x by ' + _f(p) + (' (reflect in Oy)' if p < 0 else '')))
    if a != 0:
        out.append(_w('translate ' + _f(a) + ' in x'))
    if q != 1:
        out.append(_w('stretch y by ' + _f(q) + (' (reflect in Ox)' if q < 0 else '')))
    if b != 0:
        out.append(_w('translate ' + _f(b) + ' in y'))
    return out

SECTIONS = [
    ('A', 'Proof', [
        ('Induction: sum', 'u(r),S(n)', t_ind_sum),
        ('Induction: divisor', 'f(n),k,m?', t_ind_div),
        ('Induction: M^n', 'A[2x2],p(n),q(n),r(n),s(n)', t_ind_mpow),
    ]),
    ('B', 'Complex numbers', [
        ('Arithmetic z, w', 'z,w', t_zw),
        ('Modulus-argument', 'z', t_modarg),
        ('From mod-arg form', 'r,theta', t_frommodarg),
        ('Multiply in mod-arg', 'r1,t1,r2,t2', t_mamul),
        ('De Moivre z^n', 'z,n', t_zpow),
        ('nth roots of z', 'z,n', t_nroots),
        ('Roots of unity', 'n', t_unity),
        ('Quadratic roots', 'a,b,c', t_quad),
        ('Cubic real coeffs', 'a,b,c,d,z?', t_cubic),
        ('Quartic real coeffs', 'a,b,c,d,e,z?', t_quartic),
        ('Argand plot', 'data*', t_argand),
        ('Locus |z-z1| = r', 'z1,r', t_loc_circle),
        ('Locus arg(z-z1) = t', 'z1,theta', t_loc_halfline),
        ('Locus |z-z1|=|z-z2|', 'z1,z2', t_loc_bisect),
        ('cos nt, sin nt powers', 'n', t_multangle),
        ('cos^n t, sin^n t', 'n', t_powtomult),
        ('Complex geometric sum', 'z,w,n', t_gsum),
    ]),
    ('C', 'Matrices', [
        ('pA + qB (2x2)', 'p,q,A[2x2],B[2x2]', t_lin2),
        ('pA + qB (3x3)', 'p,q,A[3x3],B[3x3]', t_lin3),
        ('AB and BA (2x2)', 'A[2x2],B[2x2]', t_mul2),
        ('AB and BA (3x3)', 'A[3x3],B[3x3]', t_mul3),
        ('Determinant 2x2', 'A[2x2]', t_det2),
        ('Determinant 3x3', 'A[3x3]', t_det3),
        ('Inverse 2x2', 'A[2x2]', t_inv2),
        ('Inverse 3x3', 'A[3x3]', t_inv3),
        ('Solve 3 eqns by A^-1', 'A[3x3],b[3]', t_solve3),
        ('Rotation 2D (deg)', 'theta', t_rot2),
        ('Reflect in y=x tan t', 'theta', t_ref2),
        ('Stretch or enlarge 2D', 'p,q', t_stretch2),
        ('Describe a 2x2', 'A[2x2]', t_describe),
        ('Rotation 3D (axis)', 'axis,theta', t_rot3),
        ('Reflect 3D in plane', 'plane', t_ref3),
        ('Invariant points/lines', 'A[2x2]', t_invar),
        ('Eigen 2x2', 'A[2x2]', t_eig2),
        ('Eigen 3x3', 'A[3x3]', t_eig3),
        ('Diagonalise 2x2 M^n', 'A[2x2],n?', t_diag2),
        ('Diagonalise 3x3 M^n', 'A[3x3],n?', t_diag3),
    ]),
    ('D', 'Further algebra and functions', [
        ('Vieta root sums', 'coeffs*', t_vieta),
        ('Power sums of roots', 'k,coeffs*', t_powersums),
        ('Roots p a + q', 'p,q,coeffs*', t_rootlin),
        ('Roots 1/a', 'coeffs*', t_rootrecip),
        ('Roots a^2', 'coeffs*', t_rootsq),
        ('Sum r, r^2, r^3', 'n', t_sumpow),
        ('Sum f(r), r = a..b', 'f(r),a,b?', t_sumpoly),
        ('Method of differences', 'f(r),n?', t_diffs),
        ('Maclaurin series', 'f(x),n', t_maclaurin),
        ('Binomial (1+x)^p', 'p,n', t_binom),
        ('Limit as x -> a', 'f(x),a', t_limit),
        ('Solve f(x) > g(x)', 'f(x),g(x)', t_ineq_gt),
        ('Solve f(x) < g(x)', 'f(x),g(x)', t_ineq_lt),
        ('Graph (ax+b)/(cx+d)', 'a,b,c,d', t_rat1),
        ('Graph quad / linear', 'a,b,c,d,e', t_rat2),
        ('Graph quad / quad', 'a,b,c,d,e,f', t_rat3),
        ('Graph f, |f|, f(|x|)', 'f(x)', t_absgraph),
        ('Parabola y^2 = 4ax', 'a', t_parab),
        ('Ellipse x2/a2+y2/b2', 'a,b', t_ellipse),
        ('Hyperbola x2/a2-y2/b2', 'a,b', t_hyper),
        ('Rect hyperbola xy=c^2', 'c', t_recthyp),
        ('Transform y = f(x)', 'f(x),p?,q?,a?,b?', t_transform),
    ]),
]
