# Algebra actions: complete the square, factorise, discriminant, vertex,
# expand, inequalities, the factor theorem, division, simplify, rationalise,
# partial fractions and the graph. Letters other than x are constants; the
# working is what a mark scheme shows, the answer is boxed.
import caseng
import caspoly
import eng
from eng import S, N, ZERO, ONE, txt, eq, val, has

def _expr(F):
    # what the action works on: f for 'f', 'y = f' or 'f(x) = f'; L - R for
    # an equation, as f = 0
    r = F.rows[0]
    if r.rel and r.name is None:
        return S(('-', r.lhs, r.rhs))
    return r.f

def _first(F):
    r = F.rows[0]
    if r.rel and r.name is None:
        return eq(r.lhs, r.rhs) if r.rel == '=' else txt(r.lhs) + ' ' + r.rel + ' ' + txt(r.rhs)
    if r.name is not None:
        return r.name + ' = ' + txt(r.f)
    return txt(r.f)

def _co(F, f=None):
    f = _expr(F) if f is None else f
    co = eng.coeffs(caspoly.expand(S(f)), F.var)
    if co is None:
        raise ValueError('not a polynomial in ' + F.var)
    return co

def _par(t):
    # brackets for a substituted value: (-3), (k + 1)
    k = t[0]
    if k in ('+', '-', 'neg') or (k == 'n' and not isinstance(t[1], complex) and t[1] < 0) or \
            eng.neg(t)[0]:
        return ('(', t)
    return t

def _ptxt(t):
    return '(' + txt(t) + ')' if _par(t)[0] == '(' else txt(t)

# ---- completing the square ----------------------------------------------------------------

def _square(F):
    # (a, h, k) with f = a(x + h)^2 + k, and the working lines
    v = F.var
    V = ('v', v)
    co = _co(F)
    if len(co) != 3:
        raise ValueError('not a quadratic in ' + v)
    c, b, a = co
    lines = [_first(F)]
    if F.rows[0].rel:
        lines.append(eq(eng.ptree(co, V), ZERO))
    if a == ONE:
        h = S(('/', b, N(2)))
        lines.append('= ' + txt(eng.add(eng.add(eng.sq(eng.add(V, h)), ('neg', eng.sq(h))), c), False))
        k = S(('-', c, ('^', h, N(2))))
        lines.append('= ' + txt(eng.add(eng.add(eng.sq(eng.add(V, h)), S(('neg', eng.sq(h)))), c), False))
    else:
        ba = S(('/', b, a))
        h = S(('/', b, ('*', N(2), a)))
        inner = eng.add(eng.sq(V), eng.mul(ba, V) if ba != ONE else V)
        at = txt(a) if caspoly.ratof(a) is not None else _ptxt(a)
        lines.append('= ' + at + '[' + txt(inner, False) + '] ' + _sgn(c))
        lines.append('= ' + at + '[' + txt(eng.add(eng.sq(eng.add(V, h)), S(('neg', eng.sq(h)))), False) +
                     '] ' + _sgn(c))
        k = S(('-', c, ('*', a, ('^', h, N(2)))))
        lines.append('= ' + txt(eng.add(eng.add(eng.mul(a, eng.sq(eng.add(V, h))),
                                                S(('neg', ('*', a, eng.sq(h))))), c), False))
    return a, h, k, lines

def _sgn(c):
    n, a = eng.neg(c)
    if a == ZERO:
        return ''
    return ('- ' if n else '+ ') + txt(a)

def _form(a, h, k, V):
    return eng.add(eng.mul(a, eng.sq(eng.add(V, h))), k)

def csq(F, arg, vals):
    v = F.var
    V = ('v', v)
    a, h, k, lines = _square(F)
    sq = _form(a, h, k, V)
    tail = ' = 0' if F.rows[0].rel == '=' and F.rows[0].name is None else ''
    if lines and lines[-1] == '= ' + txt(sq):
        lines.pop()
    lines.append(eng.boxs('', txt(sq) + tail))
    lines += _turning(a, h, k, v)
    return lines

def _turning(a, h, k, v):
    x0 = S(('neg', h))
    out = ['vertex (' + txt(x0) + ', ' + txt(k) + ')']
    av = val(a)
    if av is not None and not isinstance(av, complex):
        out.append(('minimum' if av > 0 else 'maximum') + ' value ' + txt(k) + ' at ' + v + ' = ' + txt(x0))
    out.append('line of symmetry ' + v + ' = ' + txt(x0))
    return out

def vertex(F, arg, vals):
    v = F.var
    a, h, k, lines = _square(F)
    lines.append('= ' + txt(_form(a, h, k, ('v', v))))
    x0 = S(('neg', h))
    t = _turning(a, h, k, v)
    lines.append(eng.boxs('vertex ', '(' + txt(x0) + ', ' + txt(k) + ')'))
    return lines + t[1:]

# ---- factorising --------------------------------------------------------------------------------

def _factor(f, v, lines):
    # factorised tree of a polynomial (letters allowed), writing a factor
    # theorem step for cubics and up; None when it does not factorise
    co = eng.coeffs(caspoly.expand(S(f)), v)
    V = ('v', v)
    rs = None
    if co is not None:
        rs = [caspoly.ratof(c) for c in co]
        if None in rs:
            rs = None
    if rs is not None and len(rs) >= 4:
        found = caspoly.roots_rational(list(rs))
        if found:
            import e_solve
            r = found[0]
            fac = e_solve._linfac(r, V)
            lines.append('f(' + txt(eng.R(*r)) + ') = 0, so (' + txt(fac) + ') is a factor')
            q = caspoly.pdivmod(list(rs), [caspoly.rneg(r), caspoly.R1])
            Q = [eng.R(*caspoly.rdiv(c, (r[1], 1))) for c in q[0]]
            lines.append('= (' + txt(fac) + ')(' + txt(eng.ptree(Q, V)) + ')')
    t = caspoly.factor(S(f), v) if rs is not None else None
    if t is None:
        import cassolve
        t = cassolve.factor_sym(S(f), v)
    if t is None:
        import casalg
        try:
            t = casalg.factorise(S(f), v)
        except Exception:
            t = None
        if t is not None and txt(t) == txt(S(f)):
            t = None
    return t

def fact(F, arg, vals):
    v = F.var
    lines = [_first(F)]
    f = _expr(F)
    tail = ' = 0' if F.rows[0].rel == '=' and F.rows[0].name is None else ''
    if F.qin and not F.poly:
        import e_solve
        co, shows = e_solve.uterms(f, F, v)
        co = e_solve._intco(co)
        lines.append('let u = ' + F.ushow)
        lines.extend(shows)
        U = ('v', 'u')
        qt = eng.ptree(co, U)
        ft = caspoly.factor(qt, 'u')
        if ft is None:
            raise ValueError('the quadratic in u does not factorise')
        lines.append(txt(qt) + ' = ' + txt(ft))
        back = caseng.subst(ft, 'u', F.u)
        lines.append(eng.boxs('', txt(back) + tail))
        return lines
    if tail:
        lines.append(eq(f, ZERO))
    t = _factor(f, v, lines)
    if t is None:
        lines.append(eng.boxs('', 'does not factorise with rational numbers'))
        return lines
    lines.append(eng.boxs('', txt(t) + tail))
    return lines

# ---- discriminant ----------------------------------------------------------------------------------

def disc(F, arg, vals):
    v = F.var
    co = _co(F)
    if len(co) != 3:
        raise ValueError('not a quadratic in ' + v)
    c, b, a = co
    lines = [_first(F)]
    lines.append('a = ' + txt(a) + ',  b = ' + txt(b) + ',  c = ' + txt(c))
    raw = '(' + txt(b) + ')^2 - 4(' + txt(a) + ')(' + txt(c) + ')'
    D = S(caspoly.expand(S(('-', ('*', b, b), ('*', N(4), ('*', a, c))))))
    lines.append('b^2 - 4ac = ' + raw)
    lines.append('= ' + txt(D))
    ls = [x for x in _letters(D) if x != v]
    if not ls:
        d = val(D)
        if d is None:
            raise ValueError('cannot tell the sign of ' + txt(D))
        if abs(d) < 1e-12:
            lines.append(eng.boxs('', 'b^2 - 4ac = 0: equal roots (one repeated root)'))
        elif d > 0:
            lines.append(eng.boxs('', 'b^2 - 4ac > 0: two distinct real roots'))
        else:
            lines.append(eng.boxs('', 'b^2 - 4ac < 0: no real roots'))
        return lines
    if len(ls) > 1:
        lines.append(eng.boxs('b^2 - 4ac = ', txt(D)))
        return lines
    k = ls[0]
    import cassolve
    crit = cassolve.solve_exact(D, k)
    if crit:
        lines.append(txt(D) + ' = 0 when ' + k + ' = ' + ' or '.join([txt(r) for r in _sorted(crit)]))
    gt = cassolve.ineq_str(cassolve.solve_ineq(D, '>', k), k)
    lt = cassolve.ineq_str(cassolve.solve_ineq(D, '<', k), k)
    ge = cassolve.ineq_str(cassolve.solve_ineq(D, '>=', k), k)
    lines.append(eng.boxs('two distinct real roots: ', gt))
    lines.append(eng.boxs('equal roots: ', k + ' = ' + ' or '.join([txt(r) for r in _sorted(crit)])
                          if crit else 'never'))
    lines.append(eng.boxs('real roots: ', ge))
    lines.append(eng.boxs('no real roots: ', lt))
    if has(a, k):
        for r in cassolve.solve_exact(a, k) or []:
            lines.append(('w', k + ' = ' + txt(r) + ' makes a = 0: not a quadratic then'))
    return lines

def _sorted(rs):
    import e_solve
    return e_solve._sorted(rs)

def _letters(t):
    import recog
    return recog.letters(t)

# ---- expand, inequalities --------------------------------------------------------------------------

def _upfirst(t, v):
    # typed with the number first, (2 + kx)^5: ascending powers
    while t[0] in ('^', '*', 'neg'):
        t = t[1]
    if t[0] in ('+', '-'):
        while t[0] in ('+', '-'):
            t = t[1]
        return not has(t, v)
    return False

def _expanded(t, v):
    e = caspoly.expand(S(t))
    co = eng.coeffs(e, v)
    up = _upfirst(t, v)
    if co is not None and len(co) > 1:
        if up:
            return eng.build([(eng.ptree([ZERO] * i + [co[i]], ('v', v)), 1)
                              for i in range(len(co)) if co[i] != ZERO])
        return eng.ptree(co, ('v', v))
    if e[0] == '/' and e[2][0] in ('v', '^') and has(e[2], v):
        # one power of x underneath: term by term, 256x^8 - ... + 6561/x^8
        ts = eng.sumterms(e[1], 1, [])
        return eng.build([(S(('/', a, e[2])), b) for a, b in ts])
    return e

def expand(F, arg, vals):
    r = F.rows[0]
    v = F.var
    lines = [_first(F)]
    if r.rel and r.name is None:
        lines.append(eng.boxs('', txt(_expanded(r.lhs, v)) + ' ' + r.rel + ' ' + txt(_expanded(r.rhs, v))))
    else:
        lines.append(eng.boxs((r.name + ' = ') if r.name else '', txt(_expanded(r.f, v))))
    return lines

OPS = ('>', '>=', '<', '<=')

def ineq(F, arg, vals):
    import cassolve
    r = F.rows[0]
    v = F.var
    if vals is not None:
        op = OPS[vals[0]]
        E = r.f
        lines = [txt(E) + ' ' + op + ' 0']
    else:
        op = r.rel
        E = S(('-', r.lhs, r.rhs))
        lines = [_first(F)]
        if r.rhs != ZERO:
            lines.append(txt(E) + ' ' + op + ' 0')
    crit = cassolve.solve_exact(E, v)
    if crit:
        lines.append(txt(E) + ' = 0 when ' + v + ' = ' + ', '.join([txt(x) for x in _sorted(crit)]))
    co = eng.coeffs(caspoly.expand(S(E)), v) if F.poly else None
    if co is not None and len(co) == 3:
        av = val(co[2])
        if av is not None and not isinstance(av, complex):
            up = av > 0
            want = op[0] == '>'
            lines.append(('w', 'graph is a ' + ('U' if up else 'cap') + ' shape: ' + op[0] + ' 0 ' +
                          ('outside' if up == want else 'between') + ' the roots'))
    ivs = cassolve.solve_ineq(E, op, v)
    s = cassolve.ineq_str(ivs, v)
    lines.append(eng.boxs('', s if s else 'no ' + v + ' fits'))
    return lines

# ---- factor theorem, division ------------------------------------------------------------------------

def ftheorem(F, arg, vals):
    v = F.var
    f = _expr(F)
    a = vals[0]
    lines = ['f(' + v + ') = ' + txt(f)]
    sub = _subtxt(f, v, a)
    fa = S(caseng.subst(f, v, a))
    lines.append('f(' + txt(a) + ') = ' + sub)
    if fa == ZERO:
        lines.append('= 0')
        ar = caspoly.ratof(S(a))
        fac = eng.add(('v', v), S(('neg', a)))
        box = ['(' + txt(fac) + ') is a factor']
        if ar is not None and ar[1] != 1:
            import e_solve
            box.append('(' + txt(e_solve._linfac(ar, ('v', v))) + ') is a factor')
        lines.append(eng.boxs('f(' + txt(a) + ') = 0, so ', box[-1]))
        if len(box) > 1:
            lines.append('(' + box[0][1:].split(')')[0] + ') is also a factor')
    else:
        lines.append('= ' + txt(fa))
        lines.append(eng.boxs('f(' + txt(a) + ') = ' + txt(fa) + ': ', 'not a factor, remainder ' + txt(fa)))
    return lines

def _subtxt(f, v, a):
    # f with v replaced by (a), unsimplified: 30(-1/2)^3 - 7(-1/2)^2 ...
    s = txt(caseng.subst(f, v, ('v', 'zq')))
    at = txt(a)
    if not eng._simple(at) or at[0] == '-':
        at = '(' + at + ')'
    return s.replace('zq', at)

def divide(F, arg, vals):
    import casalg
    v = F.var
    V = ('v', v)
    f = F.rows[0].f
    if arg == 'own':
        import casalg as ca
        sf = f if f[0] == '/' else ca.single_fraction(f, v)
        num, den = sf[1], sf[2]
    else:
        num = _expr(F)
        den = vals[0]
    got = casalg.divide(num, den, v)
    if got is None:
        raise ValueError('cannot divide those as polynomials in ' + v)
    q, r = got
    q = S(q)
    r = S(r)
    lines = ['(' + txt(num) + ') / (' + txt(den) + ')']
    lines.append(txt(num) + ' = (' + txt(den) + ')(' + txt(q) + ')' + ('' if r == ZERO else ' ' + _sgn(r)))
    lines.append(eng.boxs('quotient ', txt(q)))
    lines.append(eng.boxs('remainder ', txt(r)))
    if r != ZERO:
        rr = caspoly.ratof(r)
        part = _over(rr, den) if rr is not None else ('/', r, den)
        lines.append('so ' + txt(('/', num, den)) + ' = ' + txt(eng.add(q, part)))
    return lines

# ---- simplify, rationalise ---------------------------------------------------------------------------

def simp(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    lines = [_first(F)]
    if F.kind == 'num':
        t = eng.nice(S(eng.tidylog(f)))
        lines.append(eng.box('= ', t))
        return lines
    if F.kind == 'rat':
        import casalg
        n0, d0 = _numden(f)
        if n0 is not None:
            fn = _factor(n0, v, [])
            fd = _factor(d0, v, [])
            if fn is not None or fd is not None:
                lines.append('= ' + txt(('/', fn or n0, fd or d0)))
        t = casalg.single_fraction(f, v)
        t = eng.nice(t) if t is not None else eng.nice(f)
        lines.append(eng.boxs('= ', txt(t)))
        return lines
    t = eng.nice(f)
    lines.append(eng.boxs('= ', txt(t)))
    return lines

def _numden(f):
    if f[0] == '/':
        return f[1], f[2]
    return None, None

def ratl(F, arg, vals):
    f = F.rows[0].f
    v = F.var
    lines = [_first(F)]
    if f[0] != '/':
        raise ValueError('type it as one fraction')
    num, den = f[1], f[2]
    cj = _conj(den)
    if cj is None:
        raise ValueError('nothing to rationalise')
    lines.append('times top and bottom by ' + txt(cj))
    top = _posroots(caspoly.expand(S(('*', num, cj))), v)
    bot = _posroots(caspoly.expand(S(('*', den, cj))), v)
    top = S(top)
    bot = S(bot)
    lines.append('= (' + txt(top) + ')/(' + txt(bot) + ')')
    co = eng.coeffs(bot, v) if has(bot, v) else None
    if (co is not None and eng.neg(co[-1])[0]) or (co is None and eng.neg(bot)[0]):
        top = S(('neg', top))
        bot = S(('neg', bot))
    t = eng.nice(('/', top, bot)) if F.kind == 'num' else ('/', top, bot)
    if F.kind == 'num':
        lines.append(eng.box('= ', t))
    else:
        lines.append(eng.boxs('= ', txt(t)))
        lines.append(('w', v + ' > 0 assumed for the roots'))
    return lines

def _conj(d):
    # 4 + 2 sqrt 3 -> 4 - 2 sqrt 3: the surd part changes sign
    ts = eng.sumterms(d, 1, [])
    if len(ts) != 2:
        return None
    sur = [(t, s) for t, s in ts if _surd(t)]
    rest = [(t, s) for t, s in ts if not _surd(t)]
    if len(sur) == 2:
        return eng.build([sur[0], (sur[1][0], -sur[1][1])])
    if len(sur) != 1:
        return None
    return eng.build(rest + [(sur[0][0], -sur[0][1])])

def _surd(t):
    k = t[0]
    if k == 'sqrt':
        return True
    if k in ('n', 'v'):
        return False
    for c in t[1:]:
        if _surd(c):
            return True
    return False

def _posroots(t, v):
    # sqrt(16x^2) -> 4x, sqrt(8x) sqrt(2x) -> 4x: x > 0 assumed
    import recog
    k = t[0]
    if k in ('n', 'v'):
        return t
    t = (k,) + tuple([_posroots(c, v) for c in t[1:]])
    if k == 'sqrt':
        m = S(t[1])
        c = (1, 1)
        n = 0
        rest = []
        for f, e in recog.factors(m, 1, []):
            r = caspoly.ratof(f)
            if r is not None and e > 0:
                c = caspoly.rmul(c, r)
            elif f == ('v', v) and e > 0:
                n += 1
            elif f[0] == '^' and f[1] == ('v', v) and f[2][0] == 'n' and e > 0:
                n += f[2][1]
            else:
                rest.append((f, e))
        if not rest and n > 0 and c[1] == 1 and c[0] > 0:
            # the square factors come out: sqrt(8x) = 2 sqrt(2x), sqrt(16x^2) = 4x
            p = c[0]
            sq = 1
            d = 2
            while d * d <= p:
                while p % (d * d) == 0:
                    p //= d * d
                    sq *= d
                d += 1
            out = eng.mul(N(sq), ('^', ('v', v), N(n // 2)) if n // 2 > 1 else
                          (('v', v) if n // 2 == 1 else ONE))
            if n % 2 or p > 1:
                inner = eng.mul(N(p), ('v', v)) if n % 2 else N(p)
                out = eng.mul(out, ('sqrt', inner))
            return S(out)
    return t

# ---- partial fractions ---------------------------------------------------------------------------------

LET = 'ABCDEFGH'

def _dfactors(den, v):
    # the denominator's factors as typed: [(tree, poly, power)], constant
    import recog
    out = []
    const = (1, 1)
    for f, e in recog.factors(den, 1, []):
        if e < 0:
            raise ValueError('a fraction inside the denominator')
        m = 1
        g = f
        if f[0] == '^' and f[2][0] == 'n' and isinstance(f[2][1], int):
            m = f[2][1]
            g = f[1]
        p = caspoly.poly(g, v)
        if p is None:
            raise ValueError('not a polynomial: ' + txt(g))
        if len(p) <= 1:
            c = p[0] if p else (0, 1)
            k = 0
            while k < m:
                const = caspoly.rmul(const, c)
                k += 1
            continue
        if len(p) > 2:
            # an unfactorised quadratic or more: its linear factors
            t = caspoly.factor(g, v)
            if t is None:
                out.append((g, p, m))
                continue
            sub = []
            sgn = 1
            for h, e2 in recog.factors(t, 1, []):
                if h[0] == 'n':
                    const = caspoly.rmul(const, caspoly.ratof(h))
                    continue
                if h[0] == 'neg':
                    sgn = -sgn
                    h = h[1]
                mm = 1
                hh = h
                if h[0] == '^':
                    mm = h[2][1]
                    hh = h[1]
                sub.append([hh, caspoly.poly(hh, v), mm * m])
            # -(3x + 4)(3x - 4): turn one factor round, (4 - 3x)
            if _negfac(t):
                sgn = -sgn
            if sgn < 0 and sub:
                # turn round a factor with a negative constant: 3x - 4 -> 4 - 3x
                pick = [x for x in sub if x[2] % 2 == 1 and x[1][0][0] < 0] or \
                    [x for x in sub if x[2] % 2 == 1]
                if pick:
                    x = pick[0]
                    x[1] = [caspoly.rneg(c) for c in x[1]]
                    x[0] = eng.order(caspoly.ptree(x[1], v))
                    sgn = 1
            if sgn < 0:
                const = caspoly.rneg(const)
            for s in sub:
                out.append((s[0], s[1], s[2]))
            continue
        out.append((g, p, m))
    return out, const

def _negfac(t):
    k = t[0]
    if k == 'neg':
        return True
    if k == '*':
        return _negfac(t[1])
    if k == 'n':
        return not isinstance(t[1], complex) and t[1] < 0
    return False

def _ppow(p, m):
    out = [caspoly.R1]
    for i in range(m):
        out = caspoly.pmul(out, p)
    return out

def pf(F, arg, vals):
    v = F.var
    V = ('v', v)
    f = F.rows[0].f
    if f[0] != '/':
        import casalg
        f = casalg.single_fraction(f, v)
        if f is None or f[0] != '/':
            raise ValueError('type it as one fraction')
    num, den = f[1], f[2]
    Np = caspoly.poly(num, v)
    if Np is None:
        raise ValueError('the top is not a polynomial in ' + v)
    facs, const = _dfactors(den, v)
    if not facs:
        raise ValueError('no ' + v + ' in the denominator')
    for g, p, m in facs:
        if len(p) > 3:
            raise ValueError('a factor of degree 3 or more: ' + txt(g))
    D = [const]
    for g, p, m in facs:
        D = caspoly.pmul(D, _ppow(p, m))
    lines = [txt(f)]
    quot = None
    qr = caspoly.pdivmod(Np, D)
    rem = qr[1]
    if qr[0]:
        quot = caspoly.ptree(qr[0], v)
        lines.append('divide first: ' + txt(f) + ' = ' + txt(quot) + ' + (' +
                     txt(caspoly.ptree(rem, v)) + ')/(' + txt(den) + ')')
    # unknowns: A/(g), B/(g)^2 ..., (Bx + C)/(quadratic)
    cols = []
    names = []
    for g, p, m in facs:
        for j in range(1, m + 1):
            if len(p) == 3:
                cols.append((g, p, j, 1))
                cols.append((g, p, j, 0))
                names.append(LET[len(names)])
                names.append(LET[len(names)])
            else:
                cols.append((g, p, j, 0))
                names.append(LET[len(names)])
    if len(cols) > len(LET):
        raise ValueError('too many factors')
    basis = []
    for g, p, j, k in cols:
        b = caspoly.pdivmod(D, _ppow(p, j))[0]
        if k:
            b = caspoly.pmul(b, [caspoly.R0, caspoly.R1])
        basis.append(b)
    n = len(cols)
    A = []
    rhs = []
    for row in range(n):
        A.append([(basis[c][row] if row < len(basis[c]) else caspoly.R0) for c in range(n)])
        rhs.append(rem[row] if row < len(rem) else caspoly.R0)
    sol = caspoly.solve_rat(A, rhs)
    if sol is None:
        raise ValueError('these factors do not give partial fractions')
    # the form, the identity, then each constant
    terms = []
    i = 0
    for g, p, j, k in cols:
        if len(p) == 3 and k == 1:
            top = ('+', ('*', ('v', names[i]), V), ('v', names[i + 1]))
            terms.append(('/', top, _gp(g, j)))
        elif len(p) != 3:
            terms.append(('/', ('v', names[i]), _gp(g, j)))
        i += 1
    form = terms[0]
    for t in terms[1:]:
        form = ('+', form, t)
    lines.append(txt(('/', caspoly.ptree(rem, v), den)) + ' = ' + txt(form))
    idt = None
    i = 0
    for g, p, j, k in cols:
        if len(p) == 3 and k == 0:
            i += 1
            continue
        top = ('v', names[i]) if len(p) != 3 else ('+', ('*', ('v', names[i]), V), ('v', names[i + 1]))
        rest = _restprod(facs, g, j, const)
        piece = eng.mul(top, rest) if rest is not None else top
        idt = piece if idt is None else ('+', idt, piece)
        i += 1
    lines.append(txt(caspoly.ptree(rem, v)) + ' = ' + txt(idt))
    # cover-up: x = root of each single linear factor
    for c in range(n):
        g, p, j, k = cols[c]
        if len(p) == 2 and j == _mult(facs, g):
            r = caspoly.rdiv(caspoly.rneg(p[0]), p[1])
            lhs = caspoly.peval(rem, r)
            co = caspoly.peval(basis[c], r)
            lines.append(v + ' = ' + txt(eng.R(*r)) + ':  ' + txt(eng.R(*lhs)) + ' = ' +
                         txt(eng.mul(eng.R(*co), ('v', names[c]))) + ',  ' + names[c] + ' = ' +
                         txt(eng.R(*sol[c])))
    rest = [names[c] + ' = ' + txt(eng.R(*sol[c])) for c in range(n)
            if not (len(cols[c][1]) == 2 and cols[c][2] == _mult(facs, cols[c][0]))]
    if rest:
        lines.append('comparing coefficients: ' + ', '.join(rest))
    # the answer
    out = None if quot is None else quot
    i = 0
    for g, p, j, k in cols:
        if len(p) == 3:
            if k == 0:
                i += 1
                continue
            top = S(('+', ('*', eng.R(*sol[i]), V), eng.R(*sol[i + 1])))
            piece = ('/', top, _gp(g, j))
        else:
            piece = _over(sol[i], _gp(g, j))
        i += 1
        if piece is None:
            continue
        out = piece if out is None else eng.add(out, piece)
    lines.append(eng.boxs('', txt(out) if out is not None else '0'))
    return lines

def _gp(g, j):
    return g if j == 1 else ('^', g, N(j))

def _over(c, d):
    # c/d with c rational: 1/(8(4 - 3x)), -6/(x + 2)^2
    p, q = c
    if p == 0:
        return None
    sg = -1 if p < 0 else 1
    p = abs(p)
    bot = d if q == 1 else ('*', N(q), d)
    t = ('/', N(p), bot)
    return ('neg', t) if sg < 0 else t

def _mult(facs, g):
    for h, p, m in facs:
        if h == g:
            return m
    return 1

def _restprod(facs, g, j, const):
    out = None
    if const != (1, 1):
        out = eng.R(*const)
    for h, p, m in facs:
        e = m - j if h == g else m
        if e <= 0:
            continue
        t = h if e == 1 else ('^', h, N(e))
        out = t if out is None else ('*', out, t)
    return out

# ---- graph ----------------------------------------------------------------------------------------------

def graph(F, arg, vals):
    import plot
    r = F.rows[0]
    v = F.var
    curves = []
    rows = F.rows
    for row in rows:
        if row.rel == '=' and row.name is None:
            if F.kind == 'xy' or F.pair == 'simul':
                import e_solve
                try:
                    ys = eng.solve_for(row.lhs, row.rhs, 'y', [])
                except Exception:
                    raise ValueError('cannot write it as y = f(x) to plot')
                curves += ys
            else:
                curves += [row.lhs, row.rhs]
        else:
            curves.append(row.f)
    ls = [c for c in F.letters][:3]
    if vals:
        for i in range(len(ls)):
            curves = [caseng.subst(c, ls[i], vals[i]) for c in curves]
    if v != 'x':
        curves = [caseng.subst(c, v, ('v', 'x')) for c in curves]
    plot.run(curves, -6.0, 6.0, 'y', ' ; '.join([x.text for x in rows]))
    return None
