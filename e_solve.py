# Solve, Roots, Rearrange and Sub u, shared by every topic. The method
# follows the recognised form, as a mark scheme would: factors or the
# formula for a quadratic, the factor theorem for a cubic, a substitution for
# a hidden quadratic, logs for an exponential, combining logs for a log
# equation, cases for a modulus. Anything else goes to the CAS solver, and
# the page says so.
import caseng
import caspoly
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has, count, Stuck, NoRoot

def sides(F):
    # the row as L = R (an expression or 'y = f' is f = 0)
    r = F.rows[0]
    if r.rel == '=' and r.name is None:
        return r.lhs, r.rhs
    return r.f, ZERO

def _exact(F):
    return not F.dec

def _sorted(rs):
    def key(t):
        v = val(t)
        return v if isinstance(v, (int, float)) else 1e300
    out = list(rs)
    out.sort(key=key)
    return out

def _dedupe(rs):
    out = []
    seen = []
    for r in rs:
        v = val(r)
        k = txt(r) if v is None or isinstance(v, complex) else round(v, 9)
        if k not in seen:
            seen.append(k)
            out.append(r)
    return out

def boxroots(v, rs, F, lines):
    rs = _sorted(_dedupe(rs))
    F.roots = rs
    if not rs:
        lines.append(eng.boxs('', 'no real solutions'))
        return lines
    last = lines[-1] if lines else None
    if len(rs) == 1 and isinstance(last, str) and last == v + ' = ' + txt(rs[0]):
        lines.pop()
    for r in rs:
        lines.append(eng.box(v + ' = ', r, _exact(F)))
    return lines

# ---- quadratics ------------------------------------------------------------------------------

def _isq(n):
    # integer square root when n is a perfect square, else None
    if n < 0:
        return None
    r = int(n ** 0.5)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r if r * r == n else None

def _ratco(co):
    out = []
    for c in co:
        r = caspoly.ratof(c)
        if r is None:
            return None
        out.append(r)
    return out

def _intco(co):
    # rational coefficients scaled to integers: 1/2 u^2 - 5/4 u + 1 -> 2u^2 - 5u + 4
    rs = _ratco(co)
    if rs is None:
        return co
    m = 1
    for p, q in rs:
        m = m * q // recog._gcd(m, q)
    if m == 1:
        return co
    return [eng.R(*caspoly.rmul(r, (m, 1))) for r in rs]

def quad(co, v, lines, show=True):
    # roots of co[2] v^2 + co[1] v + co[0] = 0, writing the method
    co = _intco(co)
    V = ('v', v) if isinstance(v, str) else v
    vn = v if isinstance(v, str) else txt(v)
    if eng.neg(co[2])[0] and caspoly.ratof(co[2]) is not None:
        # -x^2 - 5x + 10 = 0: times -1 first
        if not show and (not lines or lines[-1] != eq(eng.ptree(co, V), ZERO)):
            lines.append(eq(eng.ptree(co, V), ZERO))
        co = [S(('neg', c)) for c in co]
        show = True
    c, b, a = co[0], co[1], co[2]
    if show:
        lines.append(eq(eng.ptree(co, V), ZERO))
    rs = _ratco(co)
    if rs is not None:
        A, B, C = rs[2], rs[1], rs[0]
        D = caspoly.rsub(caspoly.rmul(B, B), caspoly.rmul((4, 1), caspoly.rmul(A, C)))
        if D[0] < 0:
            lines.append('b^2 - 4ac = ' + txt(eng.R(*D)) + ' < 0: no real roots')
            return []
        p = _isq(D[0])
        q = _isq(D[1])
        if p is not None and q is not None:
            f = caspoly.factor(eng.ptree(co, ('v', 'zu')), 'zu')
            if f is not None:
                ft = caseng.subst(f, 'zu', V)
                lines.append(eq(ft, ZERO))
            out = []
            for sg in (1, -1):
                r = caspoly.rdiv(caspoly.radd(caspoly.rneg(B), (sg * p, q)), caspoly.rmul((2, 1), A))
                out.append(eng.R(*r))
            if D[0] == 0:
                lines.append(vn + ' = ' + txt(out[0]) + ' (repeated)')
                return [out[0]]
            out = _sorted(out)
            lines.append(vn + ' = ' + txt(out[0]) + ' or ' + vn + ' = ' + txt(out[1]))
            return out
        Dt = eng.R(*D)
        top = txt(S(('neg', b))) + ' +- sqrt(' + txt(Dt) + ')'
        den = S(('*', N(2), a))
        lines.append(vn + ' = (' + top + ')' + ('' if den == ONE else '/' + eng._br(txt(den))))
        out = []
        for sg in (1, -1):
            sq = ('sqrt', Dt)
            out.append(S(('/', ('+', ('neg', b), sq if sg > 0 else ('neg', sq)), den)))
        return _sorted(out)
    # letters: the formula with them in
    import cassolve
    D = S(caspoly.expand(S(('-', ('*', b, b), ('*', N(4), ('*', a, c))))))
    den = S(('*', N(2), a))
    lines.append(vn + ' = (' + txt(S(('neg', b))) + ' +- sqrt(' + txt(D) + '))' +
                 ('' if den == ONE else '/' + eng._br(txt(den))))
    rs = cassolve.roots_co([c, b, a], v if isinstance(v, str) else 'x')
    return rs or []

# ---- polynomials ----------------------------------------------------------------------------

def _std(L, Rt, v, lines):
    # coefficients of L - R, writing 'p(x) = 0' when that is new
    E = caspoly.expand(S(('-', L, Rt)))
    co = eng.coeffs(E, v)
    if co is None:
        raise Stuck()
    shown = [eng.decimal(c) for c in co] if recog.hasfloat(L) or recog.hasfloat(Rt) else co
    std = eq(eng.ptree(shown, ('v', v)), ZERO)
    if not lines or lines[-1] != std:
        if Rt != ZERO or txt(L) != txt(eng.ptree(shown, ('v', v))):
            lines.append(std)
    return co

def poly(L, Rt, v, F, lines):
    E = caspoly.expand(S(('-', L, Rt)))
    co = eng.coeffs(E, v)
    if co is None:
        raise Stuck()
    d = len(co) - 1
    if d >= 2:
        co = _std(L, Rt, v, lines)
    if d < 1:
        if co[0] == ZERO:
            return None
        lines.append(eq(co[0], ZERO) + ': never true')
        return []
    if d == 1:
        try:
            return eng.solve_for(L, Rt, v, lines)
        except Stuck:
            return [S(('neg', ('/', co[0], co[1])))]
    if d == 2:
        return quad(co, v, lines, False)
    return cubic(co, v, lines)

def cubic(co, v, lines):
    # a rational root by the factor theorem, then what is left
    rs = _ratco(co)
    V = ('v', v)
    if rs is None:
        return _cas(eng.ptree(co, V), v, lines)
    found = caspoly.roots_rational(list(rs))
    if not found:
        return _numeric(eng.ptree(co, V), v, lines, 'no rational roots')
    r = found[0]
    fac = _linfac(r, V)
    lines.append('f(' + txt(eng.R(*r)) + ') = 0, so (' + txt(fac) + ') is a factor')
    q = caspoly.pdivmod(list(rs), [caspoly.rneg(r), caspoly.R1])
    Q = [eng.R(*caspoly.rdiv(c, (r[1], 1))) for c in q[0]]
    lines.append('f(' + v + ') = (' + txt(fac) + ')(' + txt(eng.ptree(Q, V)) + ')')
    out = [eng.R(*r)]
    if len(Q) == 3:
        out += quad(Q, v, lines, False)
    elif len(Q) == 2:
        out.append(S(('neg', ('/', Q[0], Q[1]))))
    elif len(Q) > 3:
        out += cubic(Q, v, lines)
    return out

def _linfac(r, V):
    # root p/q -> factor (q x - p)
    p, q = r
    a = V if q == 1 else ('*', N(q), V)
    return eng.add(a, N(-p))

# ---- hidden quadratics -------------------------------------------------------------------------

def _kdiv(m, k):
    # m / k for multipliers (p, q) or (v, 0)
    a = recog._pq(m) / recog._pq(k)
    n = int(round(a))
    if abs(a - n) > 1e-9:
        raise Stuck()
    return n

def uterms(E, F, v):
    # E as a quadratic in u = F.u: coefficient trees [c0, c1, c2] (times u
    # first for u + 1/u), and the lines rewriting each term
    k = F.uk
    co = [[], [], [], []]
    shows = []
    for t, sg in recog.terms(E, 1, []):
        c = []
        j = 0
        for f, e in recog.factors(t, 1, []):
            a = recog.xpart(f, v)
            if a[0] == 'c':
                c.append((f, e))
                continue
            if a[0] == 'o':
                raise Stuck()
            if a[0] == 'p':
                j += e * _kdiv(a[1], k)
                continue
            if a[0] == 'f':
                j += e * _kdiv(a[2], k)
                continue
            # base^(p v + q): u^(p m / k) times base^q
            if f[0] == 'exp':
                pq = recog.lin(f[1], v)
                if pq[1] != ZERO:
                    c.append((('exp', pq[1]), e))
            else:
                pq = recog.lin(f[2], v)
                if pq[1] != ZERO:
                    c.append((('^', f[1], pq[1]), e))
            j += e * _kdiv(a[2], k)
        if F.recip:
            j += 1
        if j < 0 or j > 2:
            raise Stuck()
        ct = ONE
        for f, e in c:
            ct = ('*', ct, f) if e > 0 else ('/', ct, f)
        ct = S(ct)
        co[j].append((ct, sg))
        jj = j - 1 if F.recip else j
        if jj > 0:
            # 4^x = (2^x)^2 = u^2, 2^(x+3) = 8(2^x) = 8u
            U = F.u
            ut = ('^', U, N(jj)) if jj > 1 else U
            if txt(t) != txt(eng.mul(ct, ut)):
                uu = ('^', ('v', 'u'), N(jj)) if jj > 1 else ('v', 'u')
                shows.append(txt(t) + ' = ' + txt(eng.mul(ct, ut)) + ' = ' + txt(eng.mul(ct, uu)))
    out = [S(eng.build(co[i])) if co[i] else ZERO for i in range(3)]
    return out, shows

def qin(L, Rt, v, F, lines, upto=False):
    # substitution: u = 2^x, x^2, sqrt x ... then back again
    co, shows = uterms(('-', L, Rt), F, v)
    lines.append('let u = ' + F.ushow)
    lines.extend(shows)
    if F.recip:
        lines.append('times u: ' + eq(eng.ptree(co, ('v', 'u')), ZERO))
    if upto:
        return co
    us = quad(co, 'u', lines, not F.recip)
    out = []
    for r in us:
        sub = []
        try:
            got = eng.isolate(F.u, r, v, sub)
            lines.append(F.ushow + ' = ' + txt(r))
            lines.extend(sub)
            out += got
        except NoRoot:
            lines.append(F.ushow + ' = ' + txt(r) + ': no solution, as ' + F.ushow +
                         (' > 0' if F.kind == 'exp' else ' >= 0'))
    return out

def subu(F, arg, vals):
    L, Rt = sides(F)
    lines = [eq(L, Rt)]
    co = qin(L, Rt, F.var, F, lines, True)
    co = _intco(co)
    lines.append(eng.boxs('', eq(eng.ptree(co, ('v', 'u')), ZERO)))
    return lines

# ---- exponentials --------------------------------------------------------------------------------

def _single_exp(t, v):
    # base^E (or e^E) with v in E: (root base, multiplier m, E tree, base tree)
    if t[0] == 'exp':
        return t
    if t[0] == '^' and not has(t[1], v) and has(t[2], v):
        return t
    return None

def _rebase(t, v):
    # 8^(x-1) -> 2^(3(x - 1)): the root base's power
    if t[0] == 'exp':
        return (('v', 'e'), t[1])
    rb = recog.rootbase(t[1])
    if rb is None or not isinstance(rb[0], int):
        return (t[1], t[2])
    b, m = rb
    e = t[2] if m == 1 else ('*', N(m), t[2])
    return (N(b), e)

def expsolve(L, Rt, v, F, lines):
    if count(L, v) + count(Rt, v) == 1:
        return eng.solve_for(L, Rt, v, lines)
    a = _single_exp(L, v)
    b = _single_exp(Rt, v)
    if a is not None and b is not None:
        ba, ea = _rebase(a, v)
        bb, eb = _rebase(b, v)
        if ba == bb:
            lines.append(eq(('^', ba, ea) if ba != ('v', 'e') else ('exp', ea),
                            ('^', bb, eb) if bb != ('v', 'e') else ('exp', eb)))
            lines.append(eq(ea, eb))
            return eng.solve_for(ea, eb, v, lines)
    return takelogs_lines(L, Rt, v, lines)

def _lnside(t, v):
    # ln of a product of numbers and exponentials, as a sum
    fs = recog.factors(t, 1, [])
    out = None
    for f, e in fs:
        if f[0] == 'exp':
            g = f[1]
        elif f[0] == '^' and not has(f[1], v):
            g = ('*', f[2], eng.logto(('v', 'e'), f[1])) if f[1] != ('v', 'e') else f[2]
        elif not has(f, v):
            g = ('ln', f)
        else:
            raise Stuck()
        if e < 0:
            g = ('neg', g)
        out = g if out is None else ('+', out, g)
    return out

def takelogs_lines(L, Rt, v, lines):
    # ln both sides, then a linear equation
    if count(L, v) == 1 and L[0] in ('+', '-') and not has(Rt, v):
        # 2^x + 3 = 15: the exponential on its own first
        ts = eng.sumterms(L, 1, [])
        keep = [(t, s) for t, s in ts if has(t, v)]
        move = [(t, -s) for t, s in ts if not has(t, v)]
        t, sg = keep[0]
        Rt = S(eng.build(eng.sumterms(Rt, 1, []) + move))
        L = t
        if sg < 0:
            Rt = S(('neg', Rt))
        lines.append(eq(L, Rt))
    la = _lnside(L, v)
    lb = _lnside(Rt, v)
    lines.append(eq(('ln', L), ('ln', Rt)))
    la = _tidyln(la)
    lb = _tidyln(lb)
    lines.append(eq(la, lb))
    return eng.solve_for(la, lb, v, lines)

def _tidyln(t):
    # ln of a number stays as ln n; ln e^k -> k
    return t

def takelogs(F, arg, vals):
    L, Rt = sides(F)
    v = F.var
    lines = [eq(L, Rt)]
    try:
        rs = takelogs_lines(L, Rt, v, lines)
    except NoRoot as e:
        lines.append(eng.boxs('', 'no solution: ' + str(e) + ' is not positive'))
        return lines
    except Stuck:
        raise ValueError('cannot take logs of that as it is')
    return boxroots(v, rs, F, lines)

# ---- logs ------------------------------------------------------------------------------------------

def logterms(t, v):
    # [(coef, base, arg)] and the other terms [(term, sign)] of a sum
    logs = []
    rest = []
    for term, sg in recog.terms(t, 1, []):
        fs = recog.factors(term, 1, [])
        lg = None
        c = []
        for f, e in fs:
            if f[0] in ('ln', 'log', 'logb') and e > 0 and lg is None:
                lg = f
            else:
                c.append((f, e))
        if lg is None:
            rest.append((term, sg))
            continue
        ct = N(sg)
        for f, e in c:
            ct = ('*', ct, f) if e > 0 else ('/', ct, f)
        ct = S(ct)
        if lg[0] == 'ln':
            logs.append((ct, ('v', 'e'), lg[1]))
        elif lg[0] == 'log':
            logs.append((ct, N(10), lg[1]))
        else:
            logs.append((ct, lg[1], lg[2]))
    return logs, rest

def combine(logs):
    # one log's argument from c log g terms: powers up, + times, - divides
    num = None
    den = None
    logs = [x for x in logs if not eng._hasvar(x[2])] + [x for x in logs if eng._hasvar(x[2])]
    for c, b, g in logs:
        n, a = eng.neg(c)
        p = g if a == ONE else ('^', g, a)
        if n:
            den = p if den is None else ('*', den, p)
        else:
            num = p if num is None else ('*', num, p)
    if num is None:
        num = ONE
    return num if den is None else ('/', num, den)

def _lg(b, g):
    return eng.logto(b, g)

def logsolve(L, Rt, v, F, lines):
    la, ra = logterms(L, v)
    lb, rb = logterms(Rt, v)
    for t, sg in ra + rb:
        if has(t, v):
            # x outside the logs too: not a log equation this method solves
            raise Stuck()
    allb = [x[1] for x in la + lb]
    for b in allb:
        if b != allb[0]:
            raise Stuck()
    base = allb[0]
    args = [x[2] for x in la + lb]
    if la and lb and not ra and not rb:
        G = combine(la)
        H = combine(lb)
        lines.append(eq(_lg(base, G), _lg(base, H)))
    else:
        logs = la + [(S(('neg', c)), b, g) for c, b, g in lb]
        K = S(eng.build(rb + [(t, -s) for t, s in ra]))
        G = combine(logs)
        if eq(_lg(base, G), K) != lines[-1]:
            lines.append(eq(_lg(base, G), K))
        H = S(('^', base, K)) if base != ('v', 'e') else S(('exp', K))
    if lines[-1] == lines[0] and len(lines) > 1:
        lines.pop()
    lines.append(eq(G, H))
    rs = algebraic(G, H, v, F, lines)
    out = []
    for r in rs:
        bad = None
        for g in args:
            gv = val(caseng.subst(g, v, r))
            if gv is None or isinstance(gv, complex) or gv <= 0:
                bad = g
                break
        if bad is None:
            out.append(r)
        else:
            lines.append(v + ' = ' + txt(r) + ': log of ' + txt(S(caseng.subst(bad, v, r))) +
                         ' is undefined, so reject')
    return out

def algebraic(G, H, v, F, lines):
    # G = H once the logs or the modulus are gone: polynomial or fractions
    G, H = eng.clearfrac(G, H, v, lines)
    try:
        rs = poly(G, H, v, F, lines)
        return [] if rs is None else rs
    except Stuck:
        return _cas(S(('-', G, H)), v, lines)

# ---- modulus -----------------------------------------------------------------------------------------

def abssolve(L, Rt, v, F, lines):
    if L[0] != 'abs' and Rt[0] == 'abs':
        L, Rt = Rt, L
    if L[0] != 'abs':
        raise Stuck()
    a = L[1]
    cases = []
    if Rt[0] == 'abs':
        b = Rt[1]
        cases = [(a, b), (a, ('neg', b))]
    else:
        cases = [(a, Rt), (a, ('neg', Rt))]
    out = []
    for g, h in cases:
        h = S(h)
        lines.append(eq(g, h))
        sub = []
        try:
            rs = algebraic(g, h, v, F, sub)
        except Stuck:
            rs = []
        lines.extend(sub)
        out += rs
    good = []
    E = ('-', L, Rt)
    for r in _dedupe(out):
        e = val(caseng.subst(E, v, r))
        if e is not None and not isinstance(e, complex) and abs(e) < 1e-9:
            good.append(r)
        else:
            lines.append(v + ' = ' + txt(r) + ' does not fit the original: reject')
    return good

# ---- fractions -----------------------------------------------------------------------------------------

def _dens(t, v, out):
    # the denominators holding v
    k = t[0]
    if k == 'n' or k == 'v':
        return out
    if k == '/' and has(t[2], v):
        out.append(t[2])
    for c in t[1:]:
        _dens(c, v, out)
    return out

def ratsolve(L, Rt, v, F, lines):
    # one fraction: multiply up; several: one fraction over a common
    # denominator, then its top = 0. Roots that zero a denominator are out.
    dens = _dens(L, v, []) + _dens(Rt, v, [])
    L2, R2 = eng.clearfrac(L, Rt, v, lines)
    if not _dens(L2, v, []) and not _dens(R2, v, []):
        rs = poly(L2, R2, v, F, lines)
        if rs is None:
            rs = []
    else:
        import casalg
        del lines[1:]
        E = casalg.single_fraction(S(('-', L, Rt)), v)
        if E is None or E[0] != '/':
            raise Stuck()
        lines.append(eq(E, ZERO))
        lines.append(eq(E[1], ZERO))
        rs = poly(E[1], ZERO, v, F, lines)
        if rs is None:
            rs = []
    good = []
    for r in rs:
        bad = False
        for d in dens:
            dv = val(caseng.subst(d, v, r))
            if dv is None or (not isinstance(dv, complex) and abs(dv) < 1e-12):
                bad = True
        if bad:
            lines.append(v + ' = ' + txt(r) + ' makes a denominator 0: reject')
        else:
            good.append(r)
    return good

# ---- the CAS when no method above fits ------------------------------------------------------------------

def _cas(E, v, lines):
    import cassolve
    rs = cassolve.solve_exact(E, v)
    if rs:
        lines.append(('w', 'solved by the CAS'))
        return rs
    return _numeric(E, v, lines, 'no exact method')

def _numeric(E, v, lines, why):
    import cassolve
    import cascalc
    rs, exact = cassolve.solve_any(E, v, eng.casui.DEG)
    if rs:
        lines.append(('w', why + ': roots found numerically, ' + cascalc.range_str(v)))
    return rs

# ---- the actions -------------------------------------------------------------------------------------------

def solve(F, arg, vals):
    L, Rt = sides(F)
    v = F.var
    lines = [eq(L, Rt)]
    k = F.kind
    try:
        if F.qin:
            rs = qin(L, Rt, v, F, lines)
        elif k == 'poly':
            rs = poly(L, Rt, v, F, lines)
        elif k == 'exp' or k == 'exp2':
            rs = expsolve(L, Rt, v, F, lines)
        elif k == 'log':
            rs = logsolve(L, Rt, v, F, lines)
        elif k == 'abs':
            rs = abssolve(L, Rt, v, F, lines)
        elif k == 'rat':
            rs = ratsolve(L, Rt, v, F, lines)
        elif k == 'power' and count(L, v) + count(Rt, v) == 1:
            rs = eng.solve_for(L, Rt, v, lines)
        else:
            rs = _cas(S(('-', L, Rt)), v, lines)
    except NoRoot as e:
        lines.append(eng.boxs('', 'no solution: ' + str(e) + ' is not positive'))
        return lines
    except Stuck:
        lines = [eq(L, Rt)]
        rs = _cas(S(('-', L, Rt)), v, lines)
    if rs is None:
        lines.append(eng.boxs('', 'true for every ' + v))
        return lines
    return boxroots(v, rs, F, lines)

def rearr(F, v, vals):
    r = F.rows[0]
    if r.name is not None and len(r.name) == 1:
        L, Rt = ('v', r.name), r.f
    else:
        L, Rt = r.lhs, r.rhs
    lines = [eq(L, Rt)]
    if F.kind in ('log', 'xy', 'const') and has(L, v):
        # logs of one base, v inside: one log first (log laws)
        logs, rest = logterms(L, v)
        if len(logs) > 1 and [1 for c, b, g in logs if b != logs[0][1]] == []:
            L = eng.build([(eng.logto(logs[0][1], combine(logs)), 1)] + rest)
            lines.append(eq(L, Rt))
    try:
        rs = eng.solve_for(L, Rt, v, lines)
    except NoRoot as e:
        lines.append(eng.boxs('', 'no solution: ' + str(e) + ' is not positive'))
        return lines
    except Stuck:
        import cassolve
        rs = cassolve.solve_exact(S(('-', L, Rt)), v)
        if not rs:
            raise ValueError('cannot make ' + v + ' the subject')
        lines = [eq(L, Rt), ('w', 'rearranged by the CAS')]
    out = lines
    if len(rs) == 1 and out and out[-1] == v + ' = ' + txt(rs[0]):
        out.pop()
    for t in rs:
        out.append(eng.boxs(v + ' = ', txt(t), t))
    return out
