# Calculus actions: differentiate (with the product, quotient or chain rule
# written out), second derivative, stationary points and their nature,
# tangent and normal, where it increases, integrate, definite integrals and
# areas, implicit and parametric dy/dx, separable differential equations and
# the area between two curves.
import caseng
import caspoly
import cascalc
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has

def _d(f, v):
    return cascalc.tidy(caseng.diff(f, v))

def _fn(F):
    # the function: f from 'f', 'y = f', 'f(x) = f'
    r = F.rows[0]
    return r.f

def _yname(F):
    r = F.rows[0]
    if r.name is not None and len(r.name) == 1:
        return r.name
    return 'y'

# ---- the tidiest derivative ---------------------------------------------------------------------

def _agree(a, b, v):
    hit = 0
    for x in (0.43, 1.31, 2.17, 3.4, -0.77):
        p = val(a, {v: x})
        q = val(b, {v: x})
        if p is None or q is None or isinstance(p, complex) or isinstance(q, complex):
            continue
        if abs(p - q) > 1e-6 * (1 + abs(q)):
            return False
        hit += 1
    return hit > 0

def _pfac(t, v):
    # t = c * prod p_i^e_i * prod e^(u_k), p_i and u_k' polynomials in v:
    # (c, [(poly, e)], [u]) or None (after mcalc's, for any variable)
    k = t[0]
    if k == 'n':
        r = caseng._ratval(t)
        return None if r is None else (r, [], [])
    if k == 'neg':
        a = _pfac(t[1], v)
        return None if a is None else ((-a[0][0], a[0][1]), a[1], a[2])
    if k == '*' or k == '/':
        a = _pfac(t[1], v)
        b = _pfac(t[2], v)
        if a is None or b is None:
            return None
        if k == '/':
            if b[0][0] == 0:
                return None
            b = ((b[0][1], b[0][0]), [(p, (-e[0], e[1])) for p, e in b[1]],
                 [('neg', u) for u in b[2]])
        return (caspoly.rmul(a[0], b[0]), a[1] + b[1], a[2] + b[2])
    if k == 'exp' or (k == '^' and t[1] == ('v', 'e')):
        u = t[1] if k == 'exp' else t[2]
        if caspoly.poly(caseng.diff(u, v), v) is None:
            return None
        return ((1, 1), [], [u])
    if k == 'sqrt' or k == '^':
        e = (1, 2) if k == 'sqrt' else caseng._ratval(t[2])
        if e is None:
            return None
        a = _pfac(t[1], v)
        if a is None or a[2]:
            return None
        if a[0] != (1, 1) and e[1] != 1:
            return None
        c = a[0]
        if e[1] == 1:
            c = caspoly.rmake(c[0] ** e[0], c[1] ** e[0]) if e[0] >= 0 else \
                caspoly.rmake(c[1] ** (-e[0]), c[0] ** (-e[0]))
        return (c, [(p, caspoly.rmul(x, e)) for p, x in a[1]], [])
    p = caspoly.poly(t, v)
    if p is None or len(caspoly.ptrim(list(p))) < 2:
        return None
    return ((1, 1), [(caspoly.ptrim(list(p)), (1, 1))], [])

def _ptree(p, e, v):
    b = caspoly.ptree(p, v)
    if e == (1, 1):
        return b
    if e == (1, 2):
        return ('sqrt', b)
    return ('^', b, caspoly.ratnode(e))

def _onefrac(f, v):
    # f' as one fraction when f is a product of powers of polynomials and
    # exponentials: x/sqrt(2x - 2) -> (x - 2)/(2x - 2)^(3/2)
    pf = _pfac(f, v)
    if pf is None or not (pf[1] or pf[2]):
        return None
    c, fs, us = pf
    M = [caspoly.R0]
    for i in range(len(fs)):
        term = caspoly.pscale(caspoly.pderiv(fs[i][0]), fs[i][1])
        for j in range(len(fs)):
            if j != i:
                term = caspoly.pmul(term, fs[j][0])
        M = caspoly.padd(M, term)
    for u in us:
        du = caspoly.poly(caseng.diff(u, v), v)
        for p, e in fs:
            du = caspoly.pmul(du, p)
        M = caspoly.padd(M, du)
    M = caspoly.ptrim([caspoly.rmul(x, c) for x in M])
    if not M:
        return ZERO
    node = caspoly.ptree(M, v)
    if us:
        ex = us[0]
        for u in us[1:]:
            ex = ('+', ex, u)
        node = ('*', node, ('exp', S(ex)))
    den = None
    for p, e in fs:
        e1 = caspoly.rsub(e, (1, 1))
        if e1[0] > 0:
            node = ('*', node, _ptree(p, e1, v))
        elif e1[0] < 0:
            q = _ptree(p, (-e1[0], e1[1]), v)
            den = q if den is None else ('*', den, q)
    return node if den is None else ('/', node, den)

def _nfrac(t):
    # fractions in t, not counting those in powers ((2x - 2)^(3/2) has none)
    k = t[0]
    if k in ('n', 'v'):
        return 0
    if k == '^':
        return _nfrac(t[1])
    n = 1 if k == '/' else 0
    for c in t[1:]:
        n += _nfrac(c)
    return n

def deriv(f, v):
    # f' in the tidiest of a few correct forms
    d = _d(f, v)
    cands = [d, eng.nice(d)]
    try:
        q = _onefrac(f, v)
        if q is not None and _agree(q, d, v):
            cands.append(q)
    except Exception:
        pass
    try:
        e = caspoly.collect(caspoly.expand(d))
        if _agree(e, d, v):
            cands.append(e)
    except Exception:
        pass
    best = None
    for c in cands:
        s = txt(c)
        key = (eng._nested(c), _nfrac(c) > 1, len(s))
        if best is None or key < best[0]:
            best = (key, c)
    return best[1]

# ---- differentiating, with the rule ---------------------------------------------------------------

def _rule(f, v, lines):
    # the product, quotient or chain rule written out, when it is used
    k = f[0]
    V = ('v', v)
    dv = 'd' + v
    if k == '*' and has(f[1], v) and has(f[2], v):
        u, w = f[1], f[2]
        du = deriv(u, v)
        dw = deriv(w, v)
        lines.append('product rule: u = ' + txt(u) + ',  v = ' + txt(w))
        lines.append('du/' + dv + ' = ' + txt(du) + ',  dv/' + dv + ' = ' + txt(dw))
        lines.append('= u dv/' + dv + ' + v du/' + dv + ' = ' +
                     txt(('+', ('*', u, dw), ('*', w, du))))
        return
    if k == '/' and has(f[1], v) and has(f[2], v):
        u, w = f[1], f[2]
        du = deriv(u, v)
        dw = deriv(w, v)
        lines.append('quotient rule: u = ' + txt(u) + ',  v = ' + txt(w))
        lines.append('du/' + dv + ' = ' + txt(du) + ',  dv/' + dv + ' = ' + txt(dw))
        lines.append('= (v du/' + dv + ' - u dv/' + dv + ')/v^2 = ' +
                     txt(('/', ('-', ('*', w, du), ('*', u, dw)), ('^', w, N(2)))))
        return
    inner = _inner(f, v)
    if inner is not None:
        U = ('v', 'u')
        outer = caseng.subst_tree(f, inner, U)
        if has(outer, v):
            return
        lines.append('chain rule: u = ' + txt(inner) + ',  y = ' + txt(outer))
        lines.append('dy/du = ' + txt(deriv(outer, 'u')) + ',  du/' + dv + ' = ' + txt(deriv(inner, v)))

def _inner(f, v):
    # the inside of a function of a non-linear inside (or a power of a sum)
    k = f[0]
    if k == 'neg' or (k == '*' and not has(f[1], v)):
        return _inner(f[2] if k == '*' else f[1], v)
    if k in ('sin', 'cos', 'tan', 'ln', 'log', 'exp', 'sqrt', 'sec', 'cosec', 'cot'):
        a = f[1]
        if has(a, v) and a != ('v', v) and recog.lin(a, v) is None or \
                (k in ('sqrt', 'ln', 'log') and has(a, v) and a != ('v', v)):
            return a
    if k == '^' and has(f[1], v) and not has(f[2], v) and f[1][0] in ('+', '-', '*'):
        return f[1]
    if k == '/' and not has(f[1], v) and f[2][0] in ('^', 'sqrt') and f[2][1][0] in ('+', '-'):
        return f[2][1]
    return None

def differentiate(F, arg, vals):
    f = _fn(F)
    v = F.var
    y = _yname(F)
    lines = [y + ' = ' + txt(f)]
    _rule(f, v, lines)
    d = deriv(f, v)
    lines.append(eng.boxt('d' + y + '/d' + v + ' = ', d))
    return lines

def second(F, arg, vals):
    f = _fn(F)
    v = F.var
    y = _yname(F)
    d1 = deriv(f, v)
    d2 = deriv(d1, v)
    lines = [y + ' = ' + txt(f), 'd' + y + '/d' + v + ' = ' + txt(d1)]
    lines.append(eng.boxt('d2' + y + '/d' + v + '2 = ', d2))
    return lines

# ---- stationary points, increasing --------------------------------------------------------------

def _zeros(d, v, lines):
    # where d = 0, solved the way Solve would (with its working)
    import e_solve
    G = recog.from_trees(d, ZERO)
    G.var = v
    sub = e_solve.solve(G, None, None)
    for ln in sub[1:]:
        if not (isinstance(ln, tuple) and ln[0] == '='):
            lines.append(ln)
    rs = getattr(G, 'roots', None) or []
    env = {}
    for c in recog.letters(d):
        if c != v:
            env[c] = 1.7
    out = []
    for r in rs:
        rv = val(r, env)
        if rv is None or isinstance(rv, complex):
            continue
        if r[0] == 'n' and isinstance(r[1], float):
            import e_fn
            r = e_fn._snap(r[1])
        out.append(r)
    return out

def stationary(F, arg, vals):
    f = _fn(F)
    v = F.var
    y = _yname(F)
    d1 = deriv(f, v)
    lines = [y + ' = ' + txt(f), 'd' + y + '/d' + v + ' = ' + txt(d1), 'd' + y + '/d' + v + ' = 0:']
    rs = _zeros(d1, v, lines)
    if not rs:
        lines.append(eng.boxs('', 'no stationary points'))
        return lines
    d2 = deriv(d1, v)
    lines.append('d2' + y + '/d' + v + '2 = ' + txt(d2))
    if F.letters:
        lines.append(('w', ', '.join(F.letters) + ' taken as positive'))
    for r in rs:
        yv = eng.nice(caseng.subst(f, v, r))
        env = {}
        for k in F.letters:
            env[k] = 1.7
        c = val(caseng.subst(d2, v, r), env)
        if c is None or isinstance(c, complex):
            kind = 'stationary point'
        elif c > 1e-9:
            kind = 'minimum'
        elif c < -1e-9:
            kind = 'maximum'
        else:
            kind = _sign_change(d1, v, r, env)
        cs = eng.nice(caseng.subst(d2, v, r))
        lines.append(v + ' = ' + txt(r) + ':  d2' + y + '/d' + v + '2 = ' + txt(cs) +
                     (' > 0' if kind == 'minimum' and c is not None and c > 0 else
                      (' < 0' if kind == 'maximum' and c is not None and c < 0 else '')))
        lines.append(eng.pair((v, y), (r, yv), not F.dec))
        lines.append(kind)
    return lines

def _sign_change(d1, v, r, env):
    # d2 = 0: the sign of dy/dx either side decides (letters at their
    # sample values, as for d2)
    x = val(r, env)
    if x is None or isinstance(x, complex):
        return 'stationary point'
    h = 1e-3 * (1 + abs(x))
    e1 = {}
    e2 = {}
    for k in env:
        e1[k] = env[k]
        e2[k] = env[k]
    e1[v] = x - h
    e2[v] = x + h
    a = val(d1, e1)
    b = val(d1, e2)
    if isinstance(a, complex) or isinstance(b, complex):
        return 'stationary point'
    if a is None or b is None:
        return 'stationary point'
    if a < 0 < b:
        return 'minimum (sign change)'
    if a > 0 > b:
        return 'maximum (sign change)'
    return 'point of inflection'

def increasing(F, arg, vals):
    import cassolve
    f = _fn(F)
    v = F.var
    y = _yname(F)
    d1 = deriv(f, v)
    lines = [y + ' = ' + txt(f), 'd' + y + '/d' + v + ' = ' + txt(d1)]
    up = cassolve.ineq_str(_join(cassolve.solve_ineq(d1, '>', v)), v)
    dn = cassolve.ineq_str(_join(cassolve.solve_ineq(d1, '<', v)), v)
    lines.append(eng.boxs('increasing (d' + y + '/d' + v + ' > 0): ', _none(up)))
    lines.append(eng.boxs('decreasing (d' + y + '/d' + v + ' < 0): ', _none(dn)))
    return lines

def _none(s):
    return 'nowhere' if not s or s == 'no solution' else s

def _join(ivs):
    # x < 0 and x > 0 around a lone stationary point join up: still increasing
    out = []
    for iv in ivs:
        if out and out[-1][1] is not None and iv[0] is not None and \
                abs(val(out[-1][1]) - val(iv[0])) < 1e-12:
            out[-1] = [out[-1][0], iv[1], out[-1][2], iv[3]]
        else:
            out.append(list(iv))
    return out

# ---- tangent and normal ---------------------------------------------------------------------------

def _at(F, a):
    f = _fn(F)
    v = F.var
    y = _yname(F)
    d1 = deriv(f, v)
    y1 = eng.nice(caseng.subst(f, v, a))
    m = eng.nice(caseng.subst(d1, v, a))
    lines = [y + ' = ' + txt(f), v + ' = ' + txt(a) + ':  ' + y + ' = ' + txt(y1),
             'd' + y + '/d' + v + ' = ' + txt(d1),
             'at ' + v + ' = ' + txt(a) + ':  d' + y + '/d' + v + ' = ' + txt(m)]
    return y1, m, lines

def _line(x1, y1, m, v, y, lines):
    import e_geo
    if m is None:
        lines.append(eng.boxs('', v + ' = ' + txt(x1)))
        return
    if m == ZERO:
        lines.append(eng.boxt(y + ' = ', y1))
        return
    lhs = y if y1 == ZERO else y + ' - ' + e_geo._b(y1)
    rhs = v if x1 == ZERO else '(' + v + ' - ' + e_geo._b(x1) + ')'
    lines.append(lhs + ' = ' + e_geo._b(m) + rhs)
    c = S(('-', y1, ('*', m, x1)))
    V = ('v', v)
    rhs = eng.add(eng.mul(m, V), c) if m != ZERO else c
    lines.append(eng.boxt(y + ' = ', rhs, False))

def tangent(F, arg, vals):
    a = vals[0]
    y1, m, lines = _at(F, a)
    _line(a, y1, m, F.var, _yname(F), lines)
    return lines

def normal(F, arg, vals):
    a = vals[0]
    y1, m, lines = _at(F, a)
    if m == ZERO:
        lines.append('the tangent is horizontal, so the normal is vertical')
        lines.append(eng.boxs('', F.var + ' = ' + txt(a)))
        return lines
    n = eng.nice(('neg', ('/', ONE, m)))
    lines.append('normal gradient = -1/(' + txt(m) + ') = ' + txt(n))
    _line(a, y1, n, F.var, _yname(F), lines)
    return lines

# ---- integrating -----------------------------------------------------------------------------------

def _integ(f, v):
    r = cascalc.integ(f, v)
    return None if r is None else eng.nice(cascalc.tidy(r))

def integrate(F, arg, vals):
    f = _fn(F)
    v = F.var
    lines = ['integral of ' + txt(f) + ' d' + v]
    I = _integ(f, v)
    if I is None:
        lines.append(('!', 'no integral in terms of standard functions: try Definite integral'))
        return lines
    lines.append(eng.boxs('= ', txt(I) + ' + c', I))
    return lines

def definite(F, arg, vals):
    f = _fn(F)
    v = F.var
    a, b = vals
    lines = ['integral from ' + txt(a) + ' to ' + txt(b) + ' of ' + txt(f) + ' d' + v]
    if val(a) is None or val(b) is None:
        raise ValueError('needs numbers for the limits')
    ok = _finite(f, v, a, b)
    if not ok:
        # 1/(x - 1) from 0 to 2: F(b) - F(a) would give a wrong number
        raise ValueError(txt(f) + ' is not defined all the way from ' + txt(a) + ' to ' + txt(b) +
                         ': no finite integral')
    if ok == 'end':
        # ln x from 0 to 1: improper at an end, fine if F has a limit there
        try:
            ex = cascalc.defint_exact(f, a, b, v)
        except Exception:
            ex = None
        if ex is None or val(ex) is None:
            raise ValueError(txt(f) + ' is not defined at an end and its integral has no limit there')
        lines.append(('w', 'improper at an end: F(b) - F(a) taken as a limit there'))
        lines.append(eng.box('= ', eng.nice(ex), not F.dec))
        return lines
    I = _integ(f, v)
    ex = None
    if I is not None:
        lines.append('= [' + txt(I) + '] from ' + txt(a) + ' to ' + txt(b))
        Ib = caseng.subst(I, v, b)
        Ia = caseng.subst(I, v, a)
        lines.append('= (' + txt(Ib) + ') - (' + txt(Ia) + ')')
        try:
            ex = cascalc.defint_exact(f, a, b, v)
        except ValueError as e:
            lines.append(('!', str(e)))
            return lines
        except Exception:
            ex = None
        if ex is None:
            ex = S(('-', Ib, Ia))
    if ex is not None and val(ex) is not None:
        lines.append(eng.box('= ', eng.nice(ex), not F.dec))
        return lines
    r = cascalc.defint(f, val(a), val(b), eng.casui.DEG, var=v)
    if r is None:
        raise ValueError('cannot evaluate it over that range')
    lines.append(('w', 'no exact integral: by the numerical method'))
    lines.append(eng.box('= ', N(r), False))
    return lines

def _crossings(f, v, a, b, n=200):
    # where f changes sign between a and b, found by sampling (a trig f has
    # more roots than the CAS lists)
    import e_fn
    out = []
    prev = None
    for i in range(n + 1):
        x = a + (b - a) * i / float(n)
        y = val(f, {v: x})
        if y is None or isinstance(y, complex):
            prev = None
            continue
        if prev is not None and (prev[1] < 0) != (y < 0) and prev[1] != 0:
            lo, hi, ylo = prev[0], x, prev[1]
            for k in range(50):
                m = (lo + hi) / 2.0
                ym = val(f, {v: m})
                if ym is None:
                    break
                if (ym < 0) == (ylo < 0):
                    lo, ylo = m, ym
                else:
                    hi = m
            out.append(e_fn._snap((lo + hi) / 2.0))
        prev = (x, y)
    return out

def _finite(f, v, lo, hi, n=64):
    # defined (and not huge) all the way from lo to hi: no zero of a
    # denominator, no edge of the domain in between, and sampled. A trouble
    # spot exactly at an end is allowed when the integral has a limit there
    # (the caller checks): 'end' then, True when fine, False otherwise.
    a = val(lo)
    b = val(hi)
    if a > b:
        a, b = b, a
    e = 1e-9 * (1 + abs(a) + abs(b))
    end = False
    try:
        import e_fn
        ivs, holes = e_fn.domain_ivs(f, v, None)
    except Exception:
        ivs, holes = None, []
    for h in holes:
        hv = val(h)
        if hv is not None and a - e <= hv <= b + e:
            if abs(hv - a) <= e or abs(hv - b) <= e:
                end = True
            else:
                return False
    if ivs is not None:
        inside = False
        for iv in ivs:
            l = -1e300 if iv[0] is None else val(iv[0])
            r = 1e300 if iv[1] is None else val(iv[1])
            if l <= a + e and b - e <= r:
                inside = True
                if (abs(l - a) <= e and not iv[2]) or (abs(r - b) <= e and not iv[3]):
                    end = True
        if not inside:
            return False
    if end:
        return 'end'
    for i in range(n + 1):
        y = val(f, {v: a + (b - a) * i / float(n)})
        if y is None or isinstance(y, complex) or abs(y) > 1e8:
            return False
    return True

def _num(f, lo, hi, v):
    # a definite integral by the numerical method; refuses a blow-up
    if _finite(f, v, lo, hi) is not True:
        raise ValueError('no finite area: the curve is not defined all the way from ' + txt(lo) +
                         ' to ' + txt(hi))
    r = cascalc.defint(f, val(lo), val(hi), eng.casui.DEG, var=v)
    if r is None or isinstance(r, complex) or r != r or abs(r) > 1e12:
        raise ValueError('no finite area: the curve is not defined all the way from ' + txt(lo) +
                         ' to ' + txt(hi))
    return N(r)

def area(F, arg, vals):
    # area between the curve and the axis: split where it crosses
    f = _fn(F)
    v = F.var
    a, b = vals
    av = val(a)
    bv = val(b)
    if av is None or bv is None:
        raise ValueError('needs numbers for the limits')
    lines = ['area between ' + txt(f) + ' and the ' + v + '-axis from ' + txt(a) + ' to ' + txt(b)]
    if _finite(f, v, a, b) is False:
        raise ValueError('the curve is not defined all the way from ' + txt(a) + ' to ' + txt(b))
    cuts = []
    sub = []
    for r in _zeros(f, v, sub) + _crossings(f, v, av, bv):
        rv = val(r)
        if av + 1e-9 < rv < bv - 1e-9 and not [c for c in cuts if abs(val(c) - rv) < 1e-7]:
            cuts.append(r)
    cuts.sort(key=lambda t: val(t))
    pts = [a] + cuts + [b]
    if cuts:
        lines.append('it crosses the axis at ' + v + ' = ' + ', '.join([txt(c) for c in cuts]))
    total = ZERO
    for i in range(len(pts) - 1):
        lo, hi = pts[i], pts[i + 1]
        try:
            I = cascalc.defint_exact(f, lo, hi, v)
        except Exception:
            I = None
        if I is None or val(I) is None:
            I = _num(f, lo, hi, v)
        I = eng.nice(I)
        lines.append('from ' + txt(lo) + ' to ' + txt(hi) + ':  ' + txt(I))
        total = S(('+', total, I if val(I) >= 0 else ('neg', I)))
    lines.append(eng.box('area = ', eng.nice(total), not F.dec))
    return lines

# ---- implicit and parametric ------------------------------------------------------------------------

def implicit(F, arg, vals):
    import e_exp
    lines = e_exp.implicit(F, arg, vals)
    if vals:
        x0, y0 = vals[0], vals[1]
        d = [ln for ln in lines if isinstance(ln, tuple) and ln[0] == '='][0][4]
        m = eng.nice(caseng.subst(caseng.subst(d, 'x', x0), 'y', y0))
        lines.append('at (' + txt(x0) + ', ' + txt(y0) + '):  dy/dx = ' + txt(m))
        lines.append(eng.box('gradient = ', m, not F.dec))
        if arg == 'tangent':
            _line(x0, y0, m, 'x', 'y', lines)
    return lines

def _xy(F):
    r1, r2 = F.rows
    if r1.name == 'x' or r2.name == 'y':
        return (r1.f, r2.f) if r1.name == 'x' else (r2.f, r1.f)
    return r1.f, r2.f

def parametric(F, arg, vals):
    t = F.var
    xs, ys = _xy(F)
    dx = deriv(xs, t)
    dy = deriv(ys, t)
    lines = ['x = ' + txt(xs) + ',  y = ' + txt(ys),
             'dx/d' + t + ' = ' + txt(dx) + ',  dy/d' + t + ' = ' + txt(dy)]
    if dx == ZERO:
        raise ValueError('dx/d' + t + ' is 0: x does not change')
    d = eng.nice(('/', dy, dx))
    lines.append('dy/dx = (dy/d' + t + ')/(dx/d' + t + ')')
    lines.append(eng.boxt('dy/dx = ', d))
    if vals:
        tv = vals[0]
        m = eng.nice(caseng.subst(d, t, tv))
        x0 = eng.nice(caseng.subst(xs, t, tv))
        y0 = eng.nice(caseng.subst(ys, t, tv))
        lines.append('at ' + t + ' = ' + txt(tv) + ':  (' + txt(x0) + ', ' + txt(y0) + '),  dy/dx = ' + txt(m))
        if arg == 'tangent':
            _line(x0, y0, m, 'x', 'y', lines)
        else:
            lines.append(eng.box('gradient = ', m, not F.dec))
    return lines

# ---- differential equations ------------------------------------------------------------------------

def de(F, arg, vals):
    # dy/dx = f(x) g(y): separate, integrate both sides
    r = F.rows[0]
    y, x = r.de
    rhs = r.f
    fx = ONE
    gy = ONE
    for fac, e in recog.factors(rhs, 1, []):
        if has(fac, y) and has(fac, x):
            raise ValueError('the variables do not separate')
        if has(fac, y):
            gy = ('*', gy, fac) if e > 0 else ('/', gy, fac)
        else:
            fx = ('*', fx, fac) if e > 0 else ('/', fx, fac)
    fx = S(fx)
    gy = S(gy)
    lines = ['d' + y + '/d' + x + ' = ' + txt(rhs)]
    lines.append('separate:  ' + txt(eng.nice(('/', ONE, gy))) + ' d' + y + ' = ' + txt(fx) + ' d' + x)
    G = cascalc.integ(S(('/', ONE, gy)), y)
    Fx = cascalc.integ(fx, x)
    if G is None or Fx is None:
        raise ValueError('cannot integrate one side')
    G = eng.nice(cascalc.tidy(G))
    Fx = eng.nice(cascalc.tidy(Fx))
    C = ('v', 'c')
    lines.append(txt(G) + ' = ' + txt(Fx) + ' + c')
    if vals:
        x0, y0 = vals
        cv = eng.nice(('-', caseng.subst(G, y, y0), caseng.subst(Fx, x, x0)))
        lines.append(x + ' = ' + txt(x0) + ', ' + y + ' = ' + txt(y0) + ':  c = ' + txt(cv))
        C = cv
    lg = _lnof(G)
    if lg is not None:
        # k ln|g(y)| = F + c: g(y)^k = A e^F, A = +-e^c
        k, g = lg
        lhs = g
        if k != ONE:
            Fx = eng.nice(('/', Fx, k))
            lines.append('ln|' + txt(g) + '| = ' + txt(Fx) + ' + c')
        if vals:
            A = eng.nice(('*', caseng.subst(lhs, y, vals[1]), ('exp', ('neg', caseng.subst(Fx, x, vals[0])))))
            lines.append(txt(lhs) + ' = A e^(' + txt(Fx) + '),  A = ' + txt(A))
        else:
            A = ('v', 'a')
            lines.append(txt(lhs) + ' = A e^(' + txt(Fx) + ')  (A = +-e^c)')
        R = eng.mul(A, ('exp', Fx))
        if lhs == ('v', y):
            lines.append(eng.boxt(y + ' = ', eng.nice(R)))
            return lines
        try:
            sub = []
            sol = eng.solve_for(lhs, R, y, sub)
            lines += sub[:-1]
            for s in sol:
                lines.append(eng.boxt(y + ' = ', eng.nice(s)))
        except (eng.Stuck, eng.NoRoot):
            lines.append(eng.boxs('', txt(lhs) + ' = ' + txt(R)))
        return lines
    rhs2 = eng.add(Fx, C) if C != ZERO else Fx
    try:
        sub = []
        sol = eng.solve_for(G, rhs2, y, sub)
        lines += sub[:-1]
        if vals and len(sol) > 1:
            # the branch through the point
            keep = []
            for s in sol:
                sv = val(caseng.subst(s, x, vals[0]))
                if sv is not None and abs(sv - val(vals[1])) < 1e-6 * (1 + abs(sv)):
                    keep.append(s)
            sol = keep or sol
        for s in sol:
            lines.append(eng.boxt(y + ' = ', eng.nice(s)))
    except (eng.Stuck, eng.NoRoot):
        lines.append(eng.boxs('', txt(G) + ' = ' + txt(rhs2)))
    return lines

def _lnof(G):
    # G = k ln|g| (or k ln g): (k, g), else None
    k = ONE
    t = G
    if t[0] == '*' and caspoly.ratof(t[1]) is not None:
        k, t = t[1], t[2]
    elif t[0] == '/' and caspoly.ratof(t[2]) is not None:
        k, t = S(('/', ONE, t[2])), t[1]
    elif t[0] == 'neg':
        k, t = N(-1), t[1]
    if t[0] == 'ln':
        g = t[1][1] if t[1][0] == 'abs' else t[1]
        return (k, g)
    return None

# ---- inflection, implicit dy/dx = 0, first principles ----------------------------------------------

def inflection(F, arg, vals):
    import cassolve
    f = _fn(F)
    v = F.var
    y = _yname(F)
    d1 = deriv(f, v)
    d2 = deriv(d1, v)
    lines = [y + ' = ' + txt(f), 'd' + y + '/d' + v + ' = ' + txt(d1),
             'd2' + y + '/d' + v + '2 = ' + txt(d2), 'd2' + y + '/d' + v + '2 = 0:']
    rs = _zeros(d2, v, lines)
    found = False
    for r in rs:
        x0 = val(r)
        h = 1e-3 * (1 + abs(x0))
        a = val(d2, {v: x0 - h})
        b = val(d2, {v: x0 + h})
        if a is None or b is None or (a > 0) == (b > 0):
            lines.append(v + ' = ' + txt(r) + ': no sign change, not an inflection')
            continue
        found = True
        lines.append(v + ' = ' + txt(r) + ':  d2' + y + '/d' + v + '2 changes sign')
        lines.append(eng.pair((v, y), (r, eng.nice(caseng.subst(f, v, r))), not F.dec))
    if not found:
        lines.append(eng.boxs('', 'no points of inflection'))
    up = cassolve.ineq_str(cassolve.solve_ineq(d2, '>', v), v)
    dn = cassolve.ineq_str(cassolve.solve_ineq(d2, '<', v), v)
    lines.append('convex (d2' + y + '/d' + v + '2 > 0): ' + (up or 'nowhere'))
    lines.append('concave (d2' + y + '/d' + v + '2 < 0): ' + (dn or 'nowhere'))
    return lines

def flat(F, arg, vals):
    # points of F(x, y) = 0 where dy/dx = 0: dF/dx = 0 with F = 0
    import e_fn
    r = F.rows[0]
    E = S(('-', r.lhs, r.rhs))
    fx = cascalc.tidy(caseng.diff(E, 'x'))
    lines = [eq(r.lhs, r.rhs), 'dy/dx = 0 where d/dx of the left side (y fixed) is 0:',
             txt(fx) + ' = 0']
    G = recog.Form()
    G.rows = [recog.from_trees(fx, ZERO).rows[0], r]
    G.pair = 'simul'
    G.vars2 = ['x', 'y']
    G.var = 'x'
    G.letters = F.letters
    G.dec = F.dec
    sub = e_fn.simul(G, None, None)
    return lines + sub[2:]

def firstp(F, arg, vals):
    # (f(x + h) - f(x))/h, the h cancelled, then h -> 0
    f = _fn(F)
    v = F.var
    H = ('v', 'h')
    fxh = caseng.subst(f, v, ('+', ('v', v), H))
    lines = ['f(' + v + ') = ' + txt(f),
             '(f(' + v + ' + h) - f(' + v + '))/h = (' + txt(fxh) + ' - (' + txt(f) + '))/h']
    num = caspoly.expand(S(('-', fxh, f)))
    lines.append('= (' + txt(num) + ')/h')
    co = eng.coeffs(num, 'h')
    if co is None or co[0] != ZERO:
        raise ValueError('the h does not cancel')
    q = eng.ptree(co[1:], H)
    lines.append('= ' + txt(q))
    lim = S(caseng.subst(q, 'h', ZERO))
    lines.append('as h -> 0:')
    lines.append(eng.boxt("f'(" + v + ') = ', lim))
    return lines

# ---- two curves --------------------------------------------------------------------------------------

def between(F, arg, vals):
    v = F.var
    f, g = F.rows[0].f, F.rows[1].f
    lines = ['area between y = ' + txt(f) + ' and y = ' + txt(g)]
    if vals:
        pts = [vals[0], vals[1]]
    else:
        sub = []
        pts = _zeros(S(('-', f, g)), v, sub)
        pts.sort(key=lambda t: val(t))
        if len(pts) < 2:
            raise ValueError('they meet fewer than twice: give the limits (Area between, limits)')
        lines.append('they meet at ' + v + ' = ' + ', '.join([txt(p) for p in pts]))
    total = ZERO
    h = S(('-', f, g))
    for i in range(len(pts) - 1):
        lo, hi = pts[i], pts[i + 1]
        try:
            I = cascalc.defint_exact(h, lo, hi, v)
        except Exception:
            I = None
        if I is None or val(I) is None:
            I = _num(h, lo, hi, v)
        I = eng.nice(I)
        lines.append('integral of (' + txt(h) + ') from ' + txt(lo) + ' to ' + txt(hi) + ' = ' + txt(I))
        total = S(('+', total, I if val(I) >= 0 else ('neg', I)))
    lines.append(eng.box('area = ', eng.nice(total), not F.dec))
    return lines
