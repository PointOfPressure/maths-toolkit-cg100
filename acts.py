# Action registry. Each action says which forms it applies to (its test on
# the recognised form) and which engine runs it; offers() lists, for one
# topic, every action that fits, most likely first. An action that can't
# apply is never offered, and every one that can is in More.
# An offer is (label, engine module, function, arg, ask): ask lists what the
# action still needs (topic.prompt), arg picks a variant (a letter, a sign).

def _row(F):
    return F.rows[0]

def _eq(F):
    r = _row(F)
    return not F.pair and r.rel == '=' and r.name is None

def _ineq(F):
    r = _row(F)
    return not F.pair and r.rel in ('<', '>', '<=', '>=')

def _fn(F):
    # a function of the variable: an expression, or y = ..., f(x) = ...
    r = _row(F)
    return not F.pair and F.kind not in ('num', 'const', 'xy', 'model') and \
        (r.rel == '' or r.name is not None)

def _poly(F, d):
    return F.poly and F.deg == d

def _single(F):
    return not F.pair and F.kind not in ('num', 'const')

# ---- the actions ----------------------------------------------------------------------------
# each returns [(priority, offer), ...]; lower priority shows first

def a_solve(F):
    if F.pair == 'simul':
        return [(1, ('Solve', 'e_fn', 'simul', None, None))]
    if F.pair == 'fg':
        return [(3, ('Solve f = g', 'e_fn', 'meet', None, None))]
    if _eq(F) and F.kind != 'xy' and F.kind != 'model':
        return [(1, ('Solve', 'e_solve', 'solve', None, None))]
    return []

def a_roots(F):
    if _fn(F):
        p = 12 if F.poly and F.deg == 2 else (11 if F.poly and F.deg >= 3 else 10)
        if F.kind in ('func', 'log', 'abs', 'power', 'trig', 'rat'):
            p = 20
        return [(p, ('Roots', 'e_solve', 'solve', None, None))]
    return []

def a_ineq(F):
    if _ineq(F):
        return [(1, ('Solve inequality', 'e_alg', 'ineq', None, None))]
    if _fn(F) and F.poly and F.deg >= 2:
        return [(30, ('Inequality', 'e_alg', 'ineq', None,
                      ('choose', ['f(x) > 0', 'f(x) >= 0', 'f(x) < 0', 'f(x) <= 0'])))]
    return []

def a_csq(F):
    if F.poly and F.deg == 2 and not _ineq(F) and not F.pair:
        return [(10 if not _eq(F) else 6, ('Complete square', 'e_alg', 'csq', None, None))]
    return []

def a_fact(F):
    if F.pair or _ineq(F):
        return []
    if F.poly and F.deg >= 2 or F.qin:
        p = 11 if F.poly and F.deg == 2 else 10
        if _eq(F):
            p = 5
        if F.qin and not F.poly:
            p = 3
        return [(p, ('Factorise', 'e_alg', 'fact', None, None))]
    if F.poly and F.deg == 1 and F.letters and not _eq(F):
        return [(25, ('Factorise', 'e_alg', 'fact', None, None))]
    return []

def a_disc(F):
    if F.poly and F.deg == 2 and not F.pair and not _ineq(F):
        return [(13 if not _eq(F) else 7, ('Discriminant', 'e_alg', 'disc', None, None))]
    return []

def a_vertex(F):
    if F.poly and F.deg == 2 and _fn(F):
        return [(14, ('Vertex', 'e_alg', 'vertex', None, None))]
    return []

def a_subu(F):
    if F.qin and not F.pair and not _ineq(F):
        return [(2, ('Sub u = ' + F.ushow, 'e_solve', 'subu', None, None))]
    return []

def a_graph(F):
    if F.kind in ('num', 'const') or F.pair == 'two' or F.kind == 'model':
        return []
    ask = None
    ls = [c for c in F.letters]
    if ls:
        ask = [(c + ' =', 1, False) for c in ls[:3]]
    return [(15, ('Graph', 'e_alg', 'graph', None, ask))]

def a_expand(F):
    if F.pair or _ineq(F):
        return []
    if F.expand and F.kind != 'log':
        return [(9 if not _eq(F) else 20, ('Expand', 'e_alg', 'expand', None, None))]
    return []

def a_rearr(F):
    r = _row(F)
    if F.pair or r.rel != '=':
        return []
    out = []
    if r.name is not None:
        if len(r.name) == 1:
            vs = [F.var] + [c for c in F.letters]
            if F.kind == 'model':
                vs = F.consts + [F.var]
        else:
            return []
    else:
        vs = F.vars2[::-1] if F.kind == 'xy' else [F.var] + [c for c in F.letters]
    import recog
    i = 0
    for v in vs:
        t = r.f if r.name is not None else F.rows[0].f
        n = _count(t, v) + (1 if r.name == v else 0)
        if n != 1 and recog.pdeg(t, v, [False]) != 1:
            continue
        p = 7 + i
        if F.kind == 'xy':
            p = 1 + i
        elif F.kind in ('exp', 'exp2') and v == F.var:
            p = 2
        out.append((p, ('Rearrange for ' + v, 'e_solve', 'rearr', v, None)))
        i += 1
    return out

def _count(t, v):
    k = t[0]
    if k == 'v':
        return 1 if t[1] == v else 0
    if k == 'n':
        return 0
    n = 0
    for c in t[1:]:
        n += _count(c, v)
    return n

def _invertible(F):
    # y = f(x) rearranges for x: x once, linear in x, or (ax + b)/(cx + d)
    import recog
    f = _row(F).f
    v = F.var
    if _count(f, v) == 1 or recog.pdeg(f, v, [False]) == 1:
        return True
    if F.poly and F.deg == 2:
        return True     # shows why there is no inverse
    if f[0] == '/' and recog.pdeg(f[1], v, [False]) is not None and \
            recog.pdeg(f[1], v, [False]) <= 1 and recog.pdeg(f[2], v, [False]) == 1:
        return True
    return False

def a_inv(F):
    if _fn(F) and not F.letters:
        p = 8 if F.kind in ('rat', 'func', 'log', 'power') or F.kind == 'exp' else 40
        if F.poly and F.deg == 1:
            p = 12
        if not _invertible(F):
            p = 42
        return [(p, ('Inverse', 'e_fn', 'inverse', None, None))]
    return []

def a_dom(F):
    if _fn(F) and F.kind in ('rat', 'func', 'log', 'power', 'qpow', 'exp', 'abs', 'trig'):
        return [(6, ('Domain', 'e_fn', 'domain', None, None))]
    return []

def a_range(F):
    if _fn(F) and not F.letters:
        p = 7 if not F.poly else 41
        return [(p, ('Range', 'e_fn', 'range_', None, None)),
                (p + 30, ('Range on an interval', 'e_fn', 'range_', 'ab',
                          [('from ' + F.var + ' =', 1, True), ('to ' + F.var + ' =', 1, True)]))]
    return []

def a_pf(F):
    if F.kind == 'rat' and _fn(F):
        return [(1, ('Partial fractions', 'e_alg', 'pf', None, None))]
    return []

def a_simp(F):
    if F.pair or _ineq(F) or _eq(F):
        return []
    if F.kind == 'num':
        return [(2, ('Simplify', 'e_alg', 'simp', None, None))]
    if F.kind in ('rat', 'func', 'power', 'qpow', 'abs', 'const', 'exp'):
        return [(2 if F.kind == 'rat' else 5, ('Simplify', 'e_alg', 'simp', None, None))]
    return []

def a_ratl(F):
    if F.pair or _eq(F) or _ineq(F):
        return []
    if _sqrtden(_row(F).f):
        return [(3, ('Rationalise', 'e_alg', 'ratl', None, None))]
    return []

def _sqrtden(t):
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k == '/' and _hassqrt(t[2]):
        return True
    for c in t[1:]:
        if _sqrtden(c):
            return True
    return False

def _hassqrt(t):
    k = t[0]
    if k == 'sqrt':
        return True
    if k == '^' and t[2][0] == '/':
        return True
    if k == 'n' or k == 'v':
        return False
    for c in t[1:]:
        if _hassqrt(c):
            return True
    return False

def a_ftheorem(F):
    if F.poly and F.deg >= 2 and _fn(F):
        return [(12 if F.deg >= 3 else 50, ('Factor theorem', 'e_alg', 'ftheorem', None,
                                             [(F.var + ' =', 1, False)]))]
    return []

def a_divide(F):
    if F.poly and F.deg >= 2 and _fn(F):
        return [(13 if F.deg >= 3 else 51, ('Divide', 'e_alg', 'divide', None,
                                             [('divide by', 1, False)]))]
    if F.kind == 'rat' and _fn(F):
        return [(30, ('Divide out', 'e_alg', 'divide', 'own', None))]
    return []

def a_transform(F):
    if _fn(F) and not F.letters:
        return [(45, ('Transform', 'e_alg', 'transform', None,
                      [('(a, b) =', 2, False), ('(c, d) =', 2, False)]))]
    return []

def a_comp(F):
    if F.pair == 'fg':
        return [(1, ('fg and gf', 'e_fn', 'comp', None, None))]
    return []

# ---- Exp and logs ---------------------------------------------------------------------------

def a_logs(F):
    # take logs of both sides
    if _eq(F) and F.kind in ('exp', 'exp2') and not F.qin:
        return [(3, ('Take logs', 'e_solve', 'takelogs', None, None))]
    return []

def a_combine(F):
    if F.kind == 'log' and not F.pair or F.kind == 'num' and F.logs:
        p = 2 if _eq(F) else 1
        return [(p, ('Combine logs', 'e_exp', 'combine', None, None)),
                (p + 1, ('Expand logs', 'e_exp', 'expandlogs', None, None))]
    return []

def a_eval(F):
    if F.kind == 'num' and not F.pair:
        return [(1, ('Evaluate', 'e_exp', 'evaluate', None, None))]
    return []

def a_model(F):
    if F.kind == 'model':
        nm = _row(F).name
        v = F.var
        pt = ('(' + v + ', ' + nm + ') =', 2, False)
        return [(1, ('From two points', 'e_exp', 'model', None,
                     [pt, pt, ('then at ' + v + ' =', 1, True)])),
                (2, ('Log-linear form', 'e_exp', 'loglin', None, None))]
    return []

def a_implicit(F):
    if F.kind == 'xy':
        return [(3, ('Implicit dy/dx', 'e_exp', 'implicit', None, None))]
    return []

# ---- Coord geometry ---------------------------------------------------------------------------

def _geo(F):
    return F.kind == 'geo'

def _n(F):
    return len(F.points) if _geo(F) else 0

def g_points(F):
    # two points (or each pair of three): mockup 5's six, in its order
    if not _geo(F) or F.items or _n(F) < 2:
        return []
    out = []
    pairs = ['AB'] if _n(F) == 2 else ['AB', 'BC', 'AC']
    base = 1 if _n(F) == 2 else 10
    for i in range(len(pairs)):
        pr = pairs[i]
        sfx = '' if _n(F) == 2 else ' ' + pr
        p = base + 6 * i
        out += [(p, ('Perp bisector' + sfx, 'e_geo', 'perpbis', pr, None)),
                (p + 1, ('Midpoint' + sfx, 'e_geo', 'midpoint', pr, None)),
                (p + 2, ('Gradient' + sfx, 'e_geo', 'gradient', pr, None)),
                (p + 3, ('Distance' + sfx, 'e_geo', 'distance', pr, None)),
                (p + 4, ('Line ' + pr, 'e_geo', 'line', pr, None)),
                (p + 5, ('Circle diam ' + pr, 'e_geo', 'circlediam', pr, None))]
    return out

def g_three(F):
    if _geo(F) and not F.items and _n(F) == 3:
        return [(1, ('Circle ABC', 'e_geo', 'circle3', None, None)),
                (2, ('Triangle ABC', 'e_geo', 'triangle', None, None))]
    return []

def g_pointline(F):
    if _geo(F) and F.items == ['line'] and _n(F) == 1:
        return [(1, ('Parallel through A', 'e_geo', 'parallel', None, None)),
                (2, ('Perpendicular thru A', 'e_geo', 'perpendicular', None, None)),
                (3, ('Foot of perpendicular', 'e_geo', 'foot', None, None)),
                (4, ('Is A on it?', 'e_geo', 'online', None, None))]
    return []

def g_twoline(F):
    if _geo(F) and F.items == ['line'] and _n(F) == 2:
        return [(1, ('Circle, centre on line', 'e_geo', 'circleline', None, None))] + \
            [(p + 1, o) for p, o in g_points_on(F)]
    return []

def g_points_on(F):
    # the two-point actions when a line is there too
    out = []
    for p, o in g_points(_noitems(F)):
        out.append((p + 10, o))
    return out

class _V:
    pass

def _noitems(F):
    G = _V()
    G.kind = F.kind
    G.points = F.points
    G.items = []
    return G

def g_circle(F):
    if not _geo(F) or 'circle' not in F.items:
        return []
    out = [(2, ('Centre and radius', 'e_geo', 'centre', None, None))]
    if F.items == ['circle'] and _n(F) == 1 and not F.letters:
        out += [(1, ('Tangent at A', 'e_geo', 'tangent', None, None)),
                (3, ('A inside or outside?', 'e_geo', 'inside', None, None)),
                (4, ('Is A on it?', 'e_geo', 'online', None, None))]
    return out

def g_line(F):
    if _geo(F) and F.items == ['line'] and _n(F) == 0:
        return [(1, ('Gradient, intercepts', 'e_geo', 'lineform', None, None))]
    return []

def g_meet(F):
    if _geo(F) and len(F.items) == 2 and 'param' not in F.items and _n(F) == 0:
        out = [(1, ('Where they meet', 'e_geo', 'meet', None, None))]
        if F.items == ['line', 'line']:
            out.append((2, ('Parallel? Perpendicular?', 'e_geo', 'compare', None, None)))
        return out
    return []

def g_param(F):
    if _geo(F) and F.items == ['param']:
        import recog
        out = [(2, ('Point at ' + F.var, 'e_geo', 'at', None, [(F.var + ' =', 1, False)]))]
        for r in F.rows:
            # t can be got on its own from x or y: the Cartesian equation
            if _count(r.f, F.var) == 1 or recog.pdeg(r.f, F.var, [False]) == 1:
                out.insert(0, (1, ('Cartesian equation', 'e_geo', 'cartesian', None, None)))
                break
        return out
    return []

def g_graph(F):
    if _geo(F) and F.items and 'param' not in F.items and not F.letters:
        return [(15, ('Graph', 'e_geo', 'graph', None, None))]
    return []

GEO = (g_points, g_three, g_pointline, g_twoline, g_circle, g_line, g_meet, g_param, g_graph)

ALG = (a_solve, a_ineq, a_pf, a_csq, a_fact, a_roots, a_disc, a_vertex, a_subu,
       a_comp, a_inv, a_dom, a_range, a_graph, a_expand, a_simp, a_ratl, a_rearr,
       a_ftheorem, a_divide, a_combine, a_eval, a_transform)
EXP = (a_solve, a_subu, a_logs, a_rearr, a_combine, a_eval, a_model, a_implicit,
       a_ineq, a_fact, a_roots, a_inv, a_dom, a_range, a_graph, a_simp, a_expand,
       a_transform)
TOPIC = {'alg': ALG, 'exp': EXP, 'geo': GEO}

def offers(F, tid):
    got = []
    n = 0
    for fn in TOPIC[tid]:
        for p, o in fn(F):
            got.append((p, n, o))
            n += 1
    got.sort()
    out = []
    seen = []
    for p, n, o in got:
        if o[0] not in seen:
            seen.append(o[0])
            out.append(o)
    return out
