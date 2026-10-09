# Two-row and function actions: simultaneous equations, f and g (composites,
# where they meet), inverse, domain and range. Exact where the algebra
# allows, with the steps a mark scheme shows.
import caseng
import caspoly
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has, Stuck, NoRoot

def _sub(f, v, a):
    return caseng.subst(f, v, a)

# ---- simultaneous equations ----------------------------------------------------------------------

def _lincoef(E, xs):
    # E = a x + b y + c (numbers): -> [a, b, -c] as rationals, else None
    g = caspoly.expand(S(E))
    out = []
    for v in xs:
        r = eng.linin(g, v)
        if r is None:
            return None
        c = caspoly.ratof(S(r[0]))
        if c is None:
            return None
        out.append(c)
        g = r[1]
    k = caspoly.ratof(S(g))
    if k is None:
        return None
    return out + [caspoly.rneg(k)]

def _rt(r):
    return eng.R(*r)

def _row(c, xs):
    # a x + b y = c as text
    t = eng.build([(eng.mul(_rt(c[0]), ('v', xs[0])), 1), (eng.mul(_rt(c[1]), ('v', xs[1])), 1)])
    return txt(t, False) + ' = ' + txt(_rt(c[2]))

def simul(F, arg, vals):
    a, b = F.rows
    xs = F.vars2 if len(F.vars2) == 2 else ['x', 'y']
    E1 = S(recog.eqtree(a)) if a.name else S(('-', a.lhs, a.rhs))
    E2 = S(recog.eqtree(b)) if b.name else S(('-', b.lhs, b.rhs))
    lines = ['(1)  ' + _rowtxt(a), '(2)  ' + _rowtxt(b)]
    c1 = _lincoef(E1, xs)
    c2 = _lincoef(E2, xs)
    if c1 is not None and c2 is not None:
        return _elim(c1, c2, xs, lines, F)
    return _subst(E1, E2, a, b, xs, lines, F)

def _rowtxt(r):
    if r.name:
        return r.name + ' = ' + txt(r.f)
    return eq(r.lhs, r.rhs)

def _elim(c1, c2, xs, lines, F):
    # elimination: match the coefficients of the second unknown
    x, y = xs
    b1 = c1[1]
    b2 = c2[1]
    det = caspoly.rsub(caspoly.rmul(c1[0], c2[1]), caspoly.rmul(c2[0], c1[1]))
    if det[0] == 0:
        same = caspoly.rsub(caspoly.rmul(c1[0], c2[2]), caspoly.rmul(c2[0], c1[2]))[0] == 0
        lines.append(eng.boxs('', 'the same line: infinitely many solutions' if same
                              else 'parallel lines: no solution'))
        return lines
    if b1[0] == 0 or b2[0] == 0:
        # one equation has no y: x from it, then y
        pass
    m1 = (abs(b2[0]) * b1[1], 1)
    m2 = (abs(b1[0]) * b2[1], 1)
    g = recog._gcd(m1[0], m2[0]) or 1
    m1 = (m1[0] // g, 1)
    m2 = (m2[0] // g, 1)
    if b1[0] == 0 or b2[0] == 0:
        m1 = (1, 1)
        m2 = (1, 1)
    r1 = [caspoly.rmul(c, m1) for c in c1]
    r2 = [caspoly.rmul(c, m2) for c in c2]
    if m1 != (1, 1):
        lines.append('(1) x ' + str(m1[0]) + ':  ' + _row(r1, xs))
    if m2 != (1, 1):
        lines.append('(2) x ' + str(m2[0]) + ':  ' + _row(r2, xs))
    same = (r1[1][0] > 0) == (r2[1][0] > 0)
    op = caspoly.rsub if same else caspoly.radd
    r = [op(r1[i], r2[i]) for i in range(3)]
    if r[0][0] == 0:
        r = [op(r1[i], r2[i]) for i in range(3)]
    lines.append(('subtract' if same else 'add') + ':  ' + txt(eng.mul(_rt(r[0]), ('v', x))) +
                 ' = ' + txt(_rt(r[2])))
    xv = caspoly.rdiv(r[2], r[0])
    lines.append(x + ' = ' + txt(_rt(xv)))
    # y from whichever equation has y
    src, cc = ('1', c1) if c1[1][0] != 0 else ('2', c2)
    rest = caspoly.rsub(cc[2], caspoly.rmul(cc[0], xv))
    yv = caspoly.rdiv(rest, cc[1])
    lines.append('in (' + src + '):  ' + txt(eng.mul(_rt(cc[1]), ('v', y))) + ' = ' + txt(_rt(rest)))
    lines.append(eng.box(x + ' = ', _rt(xv), not F.dec))
    lines.append(eng.box(y + ' = ', _rt(yv), not F.dec))
    return lines

def _oneunknown(E1, E2, a, b, xs, lines, F):
    # one equation holds only one of the unknowns: solve it, then the other
    import e_solve
    for E, O, n in ((E1, E2, '1'), (E2, E1, '2')):
        for v, u in ((xs[0], xs[1]), (xs[1], xs[0])):
            if has(E, v) and not has(E, u):
                G = recog.from_trees(E, ZERO)
                G.var = v
                sub = e_solve.solve(G, None, None)
                lines.append('(' + n + ') has only ' + v + ':')
                lines += [ln for ln in sub[1:] if not (isinstance(ln, tuple) and ln[0] == '=')]
                pairs = []
                for r in getattr(G, 'roots', []) or []:
                    H = recog.from_trees(caseng.subst(O, v, r), ZERO)
                    H.var = u
                    s2 = e_solve.solve(H, None, None)
                    lines.append(v + ' = ' + txt(r) + ':  ' + txt(caseng.subst(O, v, r)) + ' = 0')
                    for w in getattr(H, 'roots', []) or []:
                        pairs.append((r, w) if v == xs[0] else (w, r))
                if not pairs:
                    lines.append(eng.boxs('', 'no real solutions'))
                for p, q in pairs:
                    lines.append(eng.pair(xs, (p, q), not F.dec))
                return lines
    return None

def _subst(E1, E2, a, b, xs, lines, F):
    # one equation gives one unknown in terms of the other: substitute it
    import e_solve
    x, y = xs
    one = _oneunknown(E1, E2, a, b, xs, lines, F)
    if one is not None:
        return one
    pick = None
    for E, o, n, r in ((E1, E2, '1', a), (E2, E1, '2', b)):
        for v, u in ((y, x), (x, y)):
            if recog.pdeg(E, v, [False]) == 1 and (r.name == v or eng.count(E, v) >= 1):
                if r.name == v:
                    pick = (v, u, r.f, o, n, [])
                else:
                    sub = []
                    try:
                        got = eng.solve_for(E, ZERO, v, sub)
                    except Stuck:
                        continue
                    if len(got) != 1:
                        continue
                    pick = (v, u, got[0], o, n, sub)
                break
        if pick:
            break
    if pick is None:
        import cassolve
        sol = cassolve.simultaneous([E1, E2], xs)
        if sol is None:
            raise ValueError('no substitution found: neither equation is linear in ' + x + ' or ' + y)
        lines.append(('w', 'solved by the CAS'))
        lines.append(eng.box(x + ' = ', sol[0]))
        lines.append(eng.box(y + ' = ', sol[1]))
        return lines
    v, u, expr, other, n, sub = pick
    if sub:
        lines.append('from (' + n + '):  ' + v + ' = ' + txt(expr))
    m = '2' if n == '1' else '1'
    put = _sub(other, v, expr)
    orow = b if n == '1' else a
    if orow.name and len(orow.name) == 1:
        ol, orr = ('v', orow.name), orow.f
    else:
        ol, orr = orow.lhs, orow.rhs
    lines.append('into (' + m + '):  ' + eq(_sub(ol, v, expr), _sub(orr, v, expr)))
    G = recog.Form()
    G.var = u
    G.dec = F.dec
    rs = None
    try:
        if recog.pdeg(S(put), u, [False]) is None:
            raise Stuck()
        rs = e_solve.poly(put, ZERO, u, G, lines)
    except Stuck:
        try:
            rs = eng.solve_for(put, ZERO, u, lines)
        except (Stuck, NoRoot):
            # whatever form it is now (fractions, logs): Solve's own method
            H = recog.from_trees(put, ZERO)
            H.var = u
            H.dec = F.dec
            sub = e_solve.solve(H, None, None)
            lines += [ln for ln in sub[1:] if not (isinstance(ln, tuple) and ln[0] == '=')]
            rs = getattr(H, 'roots', None)
    if rs is None:
        raise ValueError('every ' + u + ' works: the equations are not independent')
    pairs = []
    for r in e_solve._sorted(e_solve._dedupe(rs)):
        w = eng.nice(_sub(expr, u, r))
        lines.append(u + ' = ' + txt(r) + ':  ' + v + ' = ' + txt(w))
        pairs.append((r, w) if u == x else (w, r))
    if not pairs:
        lines.append(eng.boxs('', 'no real solutions'))
    for p, q in pairs:
        lines.append(eng.pair((x, y), (p, q), not F.dec))
    return lines

# ---- f and g ------------------------------------------------------------------------------------------

def _names(F):
    out = []
    for r, d in zip(F.rows, ('f', 'g')):
        out.append(r.name[0] if r.name and len(r.name) == 4 else d)
    return out

def _simpler(t, v):
    # a polynomial expanded, else the tidier of the simplified form and one
    # fraction: no fraction inside a numerator, then the shorter
    import casalg
    e = caspoly.expand(S(t))
    co = eng.coeffs(e, v)
    if co is not None:
        return eng.ptree(co, ('v', v))
    cands = [eng.nice(t)]
    try:
        sf = casalg.single_fraction(S(t), v)
    except Exception:
        sf = None
    if sf is not None:
        cands.append(eng.nice(sf))
    best = None
    for c in cands:
        key = (eng._nested(c), len(txt(c)))
        if best is None or key < best[0]:
            best = (key, c)
    return best[1]

def comp(F, arg, vals):
    v = F.var
    V = ('v', v)
    f, g = F.rows[0].f, F.rows[1].f
    nf, ng = _names(F)
    lines = [nf + '(' + v + ') = ' + txt(f), ng + '(' + v + ') = ' + txt(g)]
    out = []
    for a, b, na, nb in ((f, g, nf, ng), (g, f, ng, nf)):
        name = na + nb + '(' + v + ')'
        lines.append(name + ' = ' + na + '(' + nb + '(' + v + ')) = ' + na + '(' + txt(b) + ')')
        raw = _sub(a, v, b)
        lines.append('= ' + txt(raw))
        t = _simpler(raw, v)
        if txt(t) == txt(raw):
            lines.pop()
        out.append((name, t))
    for name, t in out:
        lines.append(eng.boxt(name + ' = ', t))
    return lines

def meet(F, arg, vals):
    import e_solve
    f, g = F.rows[0].f, F.rows[1].f
    nf, ng = _names(F)
    G = recog.from_trees(f, g)
    lines = e_solve.solve(G, None, None)
    lines[0] = nf + '(' + F.var + ') = ' + ng + '(' + F.var + '):  ' + lines[0]
    for r in G.roots if hasattr(G, 'roots') else []:
        y = eng.nice(_sub(f, F.var, r))
        lines.append('meet at (' + txt(r) + ', ' + txt(y) + ')')
    return lines

# ---- inverse ---------------------------------------------------------------------------------------------

def inverse(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    Y = ('v', 'y')
    V = ('v', v)
    lines = ['y = ' + txt(f)]
    sub = []
    try:
        xs = eng.solve_for(Y, f, v, sub)
    except (Stuck, NoRoot):
        xs = None
    if xs is not None and len(xs) == 1:
        lines += sub
        inv = eng.nice(_sub(xs[0], 'y', V))
        lines.append('swap ' + v + ' and y')
        lines.append(eng.boxs('f^-1(' + v + ') = ', txt(inv), inv))
        try:
            rg = range_text(f, v, None)
        except Exception:
            rg = None
        if rg:
            lines.append('domain of f^-1 = range of f: ' + rg.replace('f(' + v + ')', v))
        return lines
    w = _witness(f, v)
    if xs is not None and len(xs) == 2:
        # two branches: one for each side of the turning point
        lines += sub
        lines.append(eng.boxs('', 'many-to-one: ' + (w or 'two ' + v + ' for one y') + ', so no inverse'))
        y0 = None
        for x0 in (2, 3, 1, 5, 0.5):
            y0 = val(_sub(f, v, N(x0)))
            if y0 is not None and not isinstance(y0, complex):
                a = val(_sub(xs[0], 'y', N(y0)))
                b = val(_sub(xs[1], 'y', N(y0)))
                if a is not None and b is not None and not isinstance(a, complex) and \
                        not isinstance(b, complex) and abs(a - b) > 1e-9:
                    break
            y0 = None
        if y0 is not None:
            hi, lo = (xs[0], xs[1]) if a > b else (xs[1], xs[0])
            h = _snap((a + b) / 2.0)
            lines.append('with the domain cut at ' + v + ' = ' + txt(h) + ':')
            lines.append(eng.boxs('f on ' + v + ' >= ' + txt(h) + ':  f^-1(' + v + ') = ',
                                  txt(eng.nice(_sub(hi, 'y', V))), eng.nice(_sub(hi, 'y', V))))
            lines.append(eng.boxs('f on ' + v + ' <= ' + txt(h) + ':  f^-1(' + v + ') = ',
                                  txt(eng.nice(_sub(lo, 'y', V))), eng.nice(_sub(lo, 'y', V))))
        return lines
    if w is not None:
        lines.append(eng.boxs('', 'many-to-one: ' + w))
        lines.append('so f has no inverse')
        return lines
    raise ValueError('cannot rearrange y = f(x) for x')

def _witness(f, v):
    # f(a) = f(b) with a != b: simple pairs first, then f(x) = f(a) solved
    for a, b in ((-1, 1), (-2, 2), (0, 2), (1, 3), (-3, 3)):
        fa = val(_sub(f, v, N(a)))
        fb = val(_sub(f, v, N(b)))
        if fa is None or fb is None or isinstance(fa, complex) or isinstance(fb, complex):
            continue
        if abs(fa - fb) < 1e-9 * (1 + abs(fa)):
            ex = eng.nice(_sub(f, v, N(a)))
            return 'f(' + str(a) + ') = f(' + str(b) + ') = ' + txt(ex)
    import e_solve
    for a in (0, 1, 2, -1, -2, 3):
        ya = eng.nice(_sub(f, v, N(a)))
        yv = val(ya)
        if yv is None or isinstance(yv, complex):
            continue
        G = recog.from_trees(f, ya)
        try:
            rs = e_solve.solve(G, None, None)
        except Exception:
            continue
        for ln in rs:
            if isinstance(ln, tuple) and ln[0] == '=' and len(ln) > 4 and ln[4] is not None:
                b = ln[4]
                bv = val(b)
                if bv is not None and not isinstance(bv, complex) and abs(bv - a) > 1e-6 * (1 + abs(a)):
                    return 'f(' + str(a) + ') = f(' + txt(b) + ') = ' + txt(ya)
    return None

# ---- domain ---------------------------------------------------------------------------------------------

def _conds(t, v, out):
    # what the domain needs: (tree, '>=' / '>' / '!=', why)
    k = t[0]
    if k in ('n', 'v'):
        return out
    for c in t[1:]:
        _conds(c, v, out)
    if k == 'sqrt' and has(t[1], v):
        out.append((t[1], '>=', 'square root'))
    elif k in ('ln', 'log') and has(t[1], v):
        out.append((t[1], '>', 'log'))
    elif k == 'logb' and has(t[2], v):
        out.append((t[2], '>', 'log'))
    elif k == '/' and has(t[2], v):
        out.append((t[2], '!=', 'denominator'))
    elif k == '^' and has(t[1], v) and not has(t[2], v):
        r = recog.rat(t[2])
        if r is not None and r[1] % 2 == 0:
            out.append((t[1], '>=' if r[0] > 0 else '>', 'even root'))
        elif r is not None and r[0] < 0:
            out.append((t[1], '!=', 'negative power'))
    elif k in ('asin', 'acos') and has(t[1], v):
        out.append((('-', ONE, ('^', t[1], N(2))), '>=', k))
    return out

INF = None

def _lt(a, b):
    # interval ends: None is -inf as a low end and +inf as a high end
    return val(a) < val(b)

def _inter(A, B):
    out = []
    for a in A:
        for b in B:
            lo, loc = a[0], a[2]
            if b[0] is not None and (lo is None or val(b[0]) > val(lo) + 1e-12):
                lo, loc = b[0], b[2]
            elif b[0] is not None and lo is not None and abs(val(b[0]) - val(lo)) <= 1e-12:
                loc = loc and b[2]
            hi, hic = a[1], a[3]
            if b[1] is not None and (hi is None or val(b[1]) < val(hi) - 1e-12):
                hi, hic = b[1], b[3]
            elif b[1] is not None and hi is not None and abs(val(b[1]) - val(hi)) <= 1e-12:
                hic = hic and b[3]
            if lo is not None and hi is not None:
                d = val(hi) - val(lo)
                if d < -1e-12 or (abs(d) <= 1e-12 and not (loc and hic)):
                    continue
            out.append([lo, hi, loc, hic])
    return out

def domain_ivs(f, v, lines):
    import cassolve
    ivs = [[None, None, False, False]]
    holes = []
    for g, op, why in _conds(f, v, []):
        if op == '!=':
            rs = [r for r in (cassolve.solve_exact(g, v) or []) if not isinstance(val(r), complex)
                  and val(r) is not None]
            if lines is not None:
                lines.append(why + ':  ' + txt(g) + ' != 0' +
                             ((',  ' + v + ' != ' + ', '.join([txt(r) for r in rs])) if rs else ''))
            holes += rs
        else:
            got = cassolve.solve_ineq(g, op, v)
            if lines is not None:
                a = txt(g) + ' ' + op + ' 0'
                b = cassolve.ineq_str(got, v) if got else ''
                if b.replace(' ', '') == a.replace(' ', ''):
                    b = ''
                lines.append(why + ':  ' + a + ((',  ' + b) if b else ''))
            ivs = _inter(ivs, got)
    keep = []
    for h in holes:
        hv = val(h)
        for iv in ivs:
            lo = -1e300 if iv[0] is None else val(iv[0])
            hi = 1e300 if iv[1] is None else val(iv[1])
            # a hole at a closed end opens that end: x <= 5, x != 5 is x < 5
            if abs(hv - lo) <= 1e-12:
                iv[2] = False
            elif abs(hv - hi) <= 1e-12:
                iv[3] = False
            elif lo < hv < hi:
                if h not in keep:
                    keep.append(h)
    return ivs, keep

def domain_text(ivs, holes, v):
    import cassolve
    if not ivs:
        return 'no real ' + v
    if ivs == [[None, None, False, False]]:
        s = 'all real ' + v
        if holes:
            s = v + ' != ' + ', '.join([txt(h) for h in holes])
        return s
    s = cassolve.ineq_str(ivs, v)
    for h in holes:
        s += ', ' + v + ' != ' + txt(h)
    return s

def domain(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    lines = ['f(' + v + ') = ' + txt(f)]
    ivs, holes = domain_ivs(f, v, lines)
    if len(lines) == 1:
        lines.append('no root, log or denominator with ' + v + ' in it')
    lines.append(eng.boxs('domain: ', domain_text(ivs, holes, v)))
    return lines

# ---- range ---------------------------------------------------------------------------------------------

BIG = (1e3, 1e6, 1e9)

def _f(f, v, x):
    y = val(f, {v: x})
    if y is None or isinstance(y, complex):
        return None
    return y

def _endlim(f, v, end, side):
    # what f tends to at an end: ('inf', sign) or ('val', y), None when it has
    # no limit; side +1 approaches from the right (a low end), -1 from the left
    if end is None:
        xs = [side * -b for b in (10.0, 100.0, 1e3, 1e6, 1e9)]
    else:
        e = val(end)
        xs = [e + side * d for d in (1e-2, 1e-4, 1e-7, 1e-10)]
    ys = []
    for x in xs:
        y = _f(f, v, x)
        if y is None:
            break
        ys.append(y)
    if not ys:
        return None
    last = ys[-1]
    if abs(last) > 1e8:
        return ('inf', 1 if last > 0 else -1)
    if len(ys) < len(xs):
        # it stopped working on the way out: blowing up if it was growing
        if len(ys) > 1 and abs(ys[-1]) > 2 * abs(ys[-2]):
            return ('inf', 1 if last > 0 else -1)
        return None if end is not None else ('val', last)
    d1 = ys[-2] - ys[-3]
    d2 = ys[-1] - ys[-2]
    tiny = 1e-6 * (1 + abs(last))
    if abs(d2) > tiny and (d1 > 0) == (d2 > 0) and abs(d2) >= 0.5 * abs(d1):
        # not settling (ln x, sqrt x, a pole): unbounded that way
        return ('inf', 1 if d2 > 0 else -1)
    if abs(d2) > tiny and (d1 > 0) != (d2 > 0):
        return None
    if abs(last) < 1e-9 or (abs(last) < 1e-3 and abs(d2) > 1e-9):
        return ('val', 0.0)
    return ('val', last)

def range_ivs(f, v, ivs, lines):
    import cassolve
    import cascalc
    d = cascalc.tidy(caseng.diff(f, v))
    if lines is not None:
        lines.append("f'(" + v + ') = ' + txt(d))
    st = []
    if len(ivs) == 1 and ivs[0][0] is not None and ivs[0][1] is not None:
        # a finite interval: every stationary point in it (a trig one repeats)
        dd = None
        for g, e in recog.factors(d, 1, []):
            if has(g, v) and e > 0:
                dd = g if dd is None else ('*', dd, g)
        try:
            st = cassolve.solve_interval(dd or d, v, ivs[0][0], S(('+', ivs[0][1], N(1e-9))))
        except Exception:
            st = []
    if not st:
        st = cassolve.solve_exact(d, v) or []
    st = [r for r in st if val(r) is not None and not isinstance(val(r), complex)]
    if not st and has(d, v):
        st = [_snap(r) for r in (cascalc.solve(d, v, eng.casui.DEG, wide=True) or [])]
    kinks = []
    for g, op, why in _abs(f, v, []):
        kinks += cassolve.solve_exact(g, v) or []
    vals_at = _surdvals(f, v, st)
    shown = [0]
    out = []
    for iv in ivs:
        lo, hi, loc, hic = iv
        cands = []     # (value, exact tree or None, attained)
        for r in st + kinks:
            rv = val(r)
            if rv is None or isinstance(rv, complex):
                continue
            if (lo is None or rv > val(lo) - 1e-12) and (hi is None or rv < val(hi) + 1e-12):
                y = vals_at.get(txt(r)) or eng.nice(_sub(f, v, r))
                yv = val(y)
                if yv is not None and not isinstance(yv, complex):
                    cands.append((yv, y, True))
                    if lines is not None and r not in kinks and shown[0] < 4:
                        shown[0] += 1
                        lines.append('stationary at ' + v + ' = ' + txt(r) + ':  f = ' + txt(y))
        if lo is not None and hi is not None:
            # a finite interval: turning points found by sampling too, so a
            # trig one the CAS solves only once is not missed
            for x in _turns(f, v, val(lo), val(hi)):
                y = _f(f, v, x)
                if y is not None:
                    cands.append((y, _snap(y), True))
        for end, side, closed in ((lo, 1, loc), (hi, -1, hic)):
            if end is not None and closed:
                y = eng.nice(_sub(f, v, end))
                yv = val(y)
                if yv is not None and not isinstance(yv, complex):
                    cands.append((yv, y, True))
                    continue
                # not defined at that end after all: its limit then
            lim = _endlim(f, v, end, side)
            if lim is None:
                continue
            if lim[0] == 'inf':
                cands.append((lim[1] * 1e300, None, False))
            else:
                ex = None
                if end is not None:
                    try:
                        ex = eng.nice(_sub(f, v, end))
                        if val(ex) is None or abs(val(ex) - lim[1]) > 1e-6 * (1 + abs(lim[1])):
                            ex = None
                    except Exception:
                        ex = None
                if ex is None:
                    ex = _snap(lim[1])
                cands.append((lim[1], ex, False))
                if lines is not None and end is None:
                    lines.append('as ' + v + ' -> ' + ('-' if side > 0 else '') + 'inf,  f(' + v + ') -> ' +
                                 (txt(ex) if ex is not None else str(lim[1])))
        if not cands:
            continue
        lo_c = min(cands, key=lambda c: c[0])
        hi_c = max(cands, key=lambda c: c[0])
        # attained if any candidate at that value is attained
        loa = [c for c in cands if abs(c[0] - lo_c[0]) <= 1e-9 * (1 + abs(lo_c[0])) and c[2]]
        hia = [c for c in cands if abs(c[0] - hi_c[0]) <= 1e-9 * (1 + abs(hi_c[0])) and c[2]]
        out.append([None if lo_c[0] < -1e299 else (loa[0][1] if loa else lo_c[1]),
                    None if hi_c[0] > 1e299 else (hia[0][1] if hia else hi_c[1]),
                    bool(loa), bool(hia), lo_c[0], hi_c[0]])
    # pieces that overlap join up
    out.sort(key=lambda p: p[4])
    merged = []
    for p in out:
        if merged:
            q = merged[-1]
            if q[5] >= p[4] - 1e-12:
                if p[5] > q[5]:
                    q[1], q[3], q[5] = p[1], p[3], p[5]
                elif abs(p[5] - q[5]) <= 1e-12:
                    q[3] = q[3] or p[3]
                continue
        merged.append(p)
    return merged

def _turns(f, v, a, b, n=240):
    # local maxima and minima of f on [a, b] from samples, each refined
    xs = [a + (b - a) * i / float(n) for i in range(n + 1)]
    ys = [_f(f, v, x) for x in xs]
    out = []
    for i in range(1, n):
        y0, y1, y2 = ys[i - 1], ys[i], ys[i + 1]
        if y0 is None or y1 is None or y2 is None:
            continue
        if (y1 >= y0 and y1 >= y2) or (y1 <= y0 and y1 <= y2):
            up = y1 >= y0 and y1 >= y2
            lo = xs[i - 1]
            hi = xs[i + 1]
            for k in range(40):
                m1 = lo + (hi - lo) / 3.0
                m2 = hi - (hi - lo) / 3.0
                f1 = _f(f, v, m1)
                f2 = _f(f, v, m2)
                if f1 is None or f2 is None:
                    break
                if (f1 < f2) == up:
                    lo = m1
                else:
                    hi = m2
            out.append((lo + hi) / 2.0)
    return out

def _frac(x):
    # a float as a small fraction (p, q) when it is one, else None
    for q in range(1, 1001):
        p = round(x * q)
        if abs(p - x * q) < 1e-7 * q:
            return (int(p), q)
    return None

def _sqrtof(t):
    k = t[0]
    if k == 'sqrt' and t[1][0] == 'n':
        return t[1][1]
    if k in ('n', 'v'):
        return None
    for c in t[1:]:
        r = _sqrtof(c)
        if r is not None:
            return r
    return None

def _surdvals(f, v, roots):
    # f at a pair of conjugate roots (p +- q sqrt c) of a rational f is
    # P +- Q sqrt c: found from the two values, so it prints as simply as that
    out = {}
    if recog.letters(f) != [v]:
        return out
    for i in range(len(roots)):
        for j in range(i + 1, len(roots)):
            c = _sqrtof(roots[i])
            if c is None or c != _sqrtof(roots[j]) or not isinstance(c, int):
                continue
            a = val(_sub(f, v, roots[i]))
            b = val(_sub(f, v, roots[j]))
            if a is None or b is None or isinstance(a, complex) or isinstance(b, complex):
                continue
            P = _frac((a + b) / 2.0)
            Q = _frac((a - b) / (2.0 * c ** 0.5))
            if P is None or Q is None:
                continue
            sq = ('sqrt', N(c))
            for r, sg in ((roots[i], 1), (roots[j], -1)):
                t = eng.nice(('+', eng.R(*P), ('*', eng.R(sg * Q[0], Q[1]), sq)))
                tv = val(t)
                if tv is not None and abs(tv - val(_sub(f, v, r))) < 1e-9 * (1 + abs(tv)):
                    out[txt(r)] = t
    return out

def _abs(t, v, out):
    k = t[0]
    if k in ('n', 'v'):
        return out
    if k == 'abs' and has(t[1], v):
        out.append((t[1], '', 'abs'))
    for c in t[1:]:
        _abs(c, v, out)
    return out

def _snap(y):
    # a limit as an exact number when it is one
    s = caseng.exactstr(y, 1e-7)
    if s is not None:
        import caslex
        try:
            t = caslex.parse(s)
            if t is not None:
                return t
        except ValueError:
            pass
    return ('n', float(eng.sf(y, 6)))

def range_str(pieces):
    if not pieces:
        return 'no values'
    parts = []
    for lo, hi, loc, hic, a, b in pieces:
        if lo is None and hi is None:
            return 'all real values'
        if lo is None:
            parts.append('f(x) ' + ('<=' if hic else '<') + ' ' + txt(hi))
        elif hi is None:
            parts.append('f(x) ' + ('>=' if loc else '>') + ' ' + txt(lo))
        elif abs(a - b) < 1e-12:
            parts.append('f(x) = ' + txt(lo))
        else:
            parts.append(txt(lo) + (' <= ' if loc else ' < ') + 'f(x)' + (' <= ' if hic else ' < ') + txt(hi))
    return ' or '.join(parts)

def range_text(f, v, ab, lines=None):
    if ab is None:
        ivs, holes = domain_ivs(f, v, None)
    else:
        lo, hi = ab
        ivs = [[lo, hi, lo is not None, hi is not None]]
        holes = []
    if holes:
        # split the pieces at the excluded points (poles)
        pts = [h for h in holes]
        pts.sort(key=lambda h: val(h))
        new = []
        for iv in ivs:
            cur = list(iv)
            for h in pts:
                hv = val(h)
                lo = -1e300 if cur[0] is None else val(cur[0])
                hi = 1e300 if cur[1] is None else val(cur[1])
                if lo < hv < hi:
                    new.append([cur[0], h, cur[2], False])
                    cur = [h, cur[1], False, cur[3]]
            new.append(cur)
        ivs = new
    s = range_str(range_ivs(f, v, ivs, lines))
    return s.replace('f(x)', 'f(' + v + ')')

def range_(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    lines = ['f(' + v + ') = ' + txt(f)]
    ab = None
    if arg == 'ab':
        ab = (vals[0], vals[1])
        lines.append('for ' + (txt(ab[0]) if ab[0] is not None else '-inf') + ' <= ' + v + ' <= ' +
                     (txt(ab[1]) if ab[1] is not None else 'inf'))
    else:
        ivs, holes = domain_ivs(f, v, None)
        dt = domain_text(ivs, holes, v)
        if dt != 'all real ' + v:
            lines.append('domain: ' + dt)
    s = range_text(f, v, ab, lines)
    lines.append(eng.boxs('range: ', s))
    return lines
