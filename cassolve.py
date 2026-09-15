# Exact equation solving: polynomials, polynomials in a function, exponential,
# logarithmic, surd, modulus, rational, trigonometric (interval and general),
# hyperbolic, simultaneous systems and inequalities.
import caseng
import caspoly
import casalg

MAXDEPTH = 4        # nested isolate/substitute passes
MAXROOTS = 12       # roots kept from one equation
MAXPERIOD = 24      # periods scanned when listing trig roots on an interval
MAXCASE = 4         # modulus sign cases
TOL = 1e-7
R1 = (1, 1)

def _S(n):
    return caseng.simplify(n)

def _num(v):
    return ('n', v)

def _sum(items):
    return caseng._addf(items)

def _prod(items):
    return caseng._mulf(items)

def _terms(n, s=1):
    out = []
    caseng._flatadd(n, s, out)
    return out

def _neg(n):
    return caseng._negnode(n)

def _has(n, var):
    return caseng._hasvar(n, var)

def _find(n, names, out):
    t = n[0]
    if t in names and n not in out:
        out.append(n)
    if t == 'n' or t == 'v':
        return out
    if len(n) >= 2:
        _find(n[1], names, out)
    if len(n) >= 3:
        _find(n[2], names, out)
    return out

def _val(n):
    try:
        return caseng.evalf(n, 0.0)
    except Exception:
        return None

def check(f, var, r):
    # does r really satisfy f = 0 (domain and extraneous roots included)?
    try:
        v = caseng.evalf(_S(caseng.subst(f, var, r)), 0.0)
    except Exception:
        return False
    if v != v:
        return False
    a = abs(v)
    return a < 1e-6

def _dedupe(roots):
    out = []
    keys = []
    for r in roots:
        k = caseng.tostr(r)
        if k in keys:
            continue
        keys.append(k)
        out.append(r)
        if len(out) >= MAXROOTS:
            break
    return out

def _sortroots(roots):
    keyed = []
    i = 0
    for r in roots:
        v = _val(r)
        if v is None or isinstance(v, complex):
            keyed.append((1, 0.0, i, r))
        else:
            keyed.append((0, v, i, r))
        i += 1
    keyed.sort(key=lambda it: (it[0], it[1], it[2]))
    return [it[3] for it in keyed]

# ---- polynomials ----------------------------------------------------------

def quadratic(a, b, c):
    # exact roots of a x^2 + b x + c, a, b, c rational pairs
    disc = caspoly.rsub(caspoly.rmul(b, b), caspoly.rmul((4, 1), caspoly.rmul(a, c)))
    root = caseng._pow(caspoly.ratnode(disc), ('/', _num(1), _num(2)))
    den = caspoly.rmul((2, 1), a)
    out = []
    for sg in (1, -1):
        top = _sum([(caspoly.ratnode(caspoly.rneg(b)), 1), (root, sg)])
        out.append(_prod([(top, 1), (caspoly.ratnode(den), -1)]))
    if out[0] == out[1]:
        return [out[0]]
    return out

def poly_roots(p):
    p = caspoly.ptrim(list(p))
    out = []
    guard = 0
    while len(p) >= 2 and guard < 12:
        guard += 1
        if caspoly.rzero(p[0]):
            out.append(_num(0))
            p = p[1:]
            continue
        if len(p) == 2:
            out.append(caspoly.ratnode(caspoly.rdiv(caspoly.rneg(p[0]), p[1])))
            break
        if len(p) == 3:
            out.extend(quadratic(p[2], p[1], p[0]))
            break
        rr = caspoly.roots_rational(p)
        if not rr:
            break
        r = rr[0]
        qr = caspoly.pdivmod(p, [caspoly.rneg(r), caspoly.R1])
        if qr is None or qr[1]:
            break
        out.append(caspoly.ratnode(r))
        p = qr[0]
    return out

# ---- inverting one function ----------------------------------------------

def _lin(g, var):
    r = casalg.linin(_S(g), var)
    if r is None or r[0] == _num(0):
        return None
    if _has(r[0], var) or _has(r[1], var):
        return None
    return r

def _fromlin(r, value, var):
    # a*var + b = value  ->  var
    return _S(_prod([(_sum([(value, 1), (r[1], -1)]), 1), (r[0], -1)]))

_PRINC = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan'}

def invert_eq(u, value, var, depth):
    # solutions of u = value for var; u contains var
    t = u[0]
    if depth > MAXDEPTH:
        return []
    if t == 'v' and u[1] == var:
        return [_S(value)]
    if t == 'exp':
        v = _val(value)
        if v is None or isinstance(v, complex) or v <= 0:
            return []
        return roots(_sum([(u[1], 1), (caseng._sfn('ln', _S(value)), -1)]), var, depth + 1)
    if t == 'ln':
        return roots(_sum([(u[1], 1), (caseng._sfn('exp', _S(value)), -1)]), var, depth + 1)
    if t == 'log':
        return roots(_sum([(u[1], 1),
                           (caseng._pow(_num(10), _S(value)), -1)]), var, depth + 1)
    if t == 'sqrt':
        v = _val(value)
        if v is None or isinstance(v, complex) or v < 0:
            return []
        return roots(_sum([(u[1], 1), (caseng._pow(_S(value), _num(2)), -1)]),
                     var, depth + 1)
    if t == 'abs':
        out = []
        for sg in (1, -1):
            out.extend(roots(_sum([(u[1], 1), (_S(value), -sg)]), var, depth + 1))
        return out
    if t == '^' and not _has(u[1], var):
        base = _S(u[1])
        lv = _S(_prod([(caseng._sfn('ln', _S(value)), 1),
                       (caseng._sfn('ln', base), -1)]))
        return roots(_sum([(u[2], 1), (lv, -1)]), var, depth + 1)
    if t in _PRINC:
        out = []
        for a in trig_principal(t, _S(value)):
            out.extend(roots(_sum([(u[1], 1), (a, -1)]), var, depth + 1))
        return out
    if t == 'cosh' or t == 'sinh' or t == 'tanh':
        for a in _hyp_principal(t, _S(value)):
            pass
        out = []
        for a in _hyp_principal(t, _S(value)):
            out.extend(roots(_sum([(u[1], 1), (a, -1)]), var, depth + 1))
        return out
    if t == '^' and not _has(u[2], var):
        e = caseng._ratval(u[2])
        if e is not None and e[1] == 1 and e[0] > 0:
            out = []
            rt = caseng._pow(_S(value), caseng._ratnode((1, e[0])))
            signs = (1, -1) if e[0] % 2 == 0 else (1,)
            for sg in signs:
                out.extend(roots(_sum([(u[1], 1), (rt, -sg)]), var, depth + 1))
            return out
    # last resort: a single occurrence of var, invert step by step
    if caseng.count_var(u, var) == 1:
        g = caseng.invert(u, var, '_y')
        if g is not None:
            return [_S(caseng.subst(g, '_y', _S(value)))]
    return []

def trig_principal(name, v):
    # the solutions of name(A) = v in one period, as exact trees
    x = _val(v)
    if x is None or isinstance(x, complex):
        return []
    if name == 'tan':
        return [caseng._sfn('atan', v)]
    if x > 1 or x < -1:
        return []
    if name == 'sin':
        a = caseng._sfn('asin', v)
        b = _sum([(('v', 'pi'), 1), (a, -1)])
        return [a] if _S(a) == _S(b) else [a, b]
    a = caseng._sfn('acos', v)
    b = _neg(a)
    return [a] if _S(a) == _S(b) else [a, b]

def _hyp_principal(name, v):
    x = _val(v)
    if x is None or isinstance(x, complex):
        return []
    sq2 = ('/', _num(1), _num(2))
    if name == 'cosh':
        if x < 1:
            return []
        rt = caseng._pow(_sum([(caseng._pow(v, _num(2)), 1), (_num(-1), 1)]), sq2)
        a = caseng._sfn('ln', _sum([(v, 1), (rt, 1)]))
        return [a, _neg(a)]
    if name == 'sinh':
        rt = caseng._pow(_sum([(caseng._pow(v, _num(2)), 1), (_num(1), 1)]), sq2)
        return [caseng._sfn('ln', _sum([(v, 1), (rt, 1)]))]
    if x <= -1 or x >= 1:
        return []
    up = _sum([(_num(1), 1), (v, 1)])
    dn = _sum([(_num(1), 1), (v, -1)])
    return [_prod([(caseng._sfn('ln', _prod([(up, 1), (dn, -1)])), 1), (_num(2), -1)])]

# ---- exponential substitution --------------------------------------------

def _expparts(f, var):
    # every e^(A x + B) / a^(A x + B) in f, as (node, base, A, B); one base only
    nodes = _find(_S(f), ('exp', '^'), [])
    out = []
    base = None
    for n in nodes:
        if n[0] == 'exp':
            g = n[1]
            b = ('v', 'e')
        else:
            if _has(n[1], var) or not _has(n[2], var):
                continue
            g = n[2]
            b = _S(n[1])
        r = _lin(g, var)
        if r is None:
            return None
        if base is None:
            base = b
        elif base != b:
            return None
        out.append((n, b, r[0], r[1]))
    if not out:
        return None
    return (base, out)

def _expsolve(f, var, depth):
    ep = _expparts(f, var)
    if ep is None:
        return None
    base, parts = ep
    unit = None
    for n, b, A, B in parts:
        v = _val(A)
        if v is None or isinstance(v, complex):
            return None
        if unit is None or abs(v) < abs(_val(unit)):
            unit = A
    g = _S(f)
    for n, b, A, B in parts:
        k = caseng._ratval(_S(_prod([(A, 1), (unit, -1)])))
        if k is None or k[1] != 1:
            return None
        rep = _prod([(caseng._pow(b, B), 1),
                     (caseng._pow(('v', '_t'), _num(k[0])), 1)])
        g = caseng.subst_tree(g, n, rep)
    g = _S(g)
    if _has(g, var):
        return None
    g2, D = casalg._cleardenom(g, '_t')
    g2 = caspoly.expand(g2)
    p = caspoly.poly(g2, '_t')
    if p is None:
        return None
    out = []
    for tv in poly_roots(p):
        v = _val(tv)
        if v is None or isinstance(v, complex) or v <= 0:
            continue
        ln = _S(_prod([(caseng._sfn('ln', tv), 1),
                       (caseng._sfn('ln', base), -1)])) if base != ('v', 'e') \
            else caseng._sfn('ln', tv)
        out.extend(roots(_sum([(_prod([(unit, 1), (('v', var), 1)]), 1), (ln, -1)]),
                         var, depth + 1))
    return out

# ---- logs, surds, modulus -------------------------------------------------

def _logsolve(f, var, depth):
    g = _S(casalg.combine_log(_S(f)))
    ls = _find(g, ('ln', 'log'), [])
    if len(ls) != 1 or not _has(ls[0], var):
        return None
    L = ls[0]
    r = casalg.linin(g, '_L') if False else None
    coef = None
    rest = []
    for tn, s in _terms(g):
        if tn == L or (tn[0] == '*' and False):
            pass
        c, fl, cx, out = caseng._termparts([(tn, 1)])
        if len(out) == 1 and out[0][0] == L and caseng._ratval(out[0][1]) == R1 \
                and fl is None and cx is None:
            coef = c if s > 0 else (-c[0], c[1])
        else:
            rest.append((tn, s))
    if coef is None or coef[0] == 0:
        return None
    for tn, s in rest:
        if _has(tn, var):
            return None
    k = _S(_prod([(_neg(_sum(rest)) if rest else _num(0), 1),
                  (caspoly.ratnode(coef), -1)]))
    if L[0] == 'ln':
        target = caseng._sfn('exp', k)
    else:
        target = caseng._pow(_num(10), k)
    return roots(_sum([(L[1], 1), (target, -1)]), var, depth + 1)

def _surdsolve(f, var, depth):
    sq = []
    for n in _find(_S(f), ('sqrt',), []):
        if _has(n, var):
            sq.append(n)
    if not sq:
        return None
    S = sq[0]
    coef = None
    rest = []
    for tn, s in _terms(_S(f)):
        c, fl, cx, out = caseng._termparts([(tn, 1)])
        hit = None
        keep = []
        for b, e in out:
            if b == S[1] and caseng._ratval(e) == (1, 2):
                hit = True
            else:
                keep.append([b, e])
        if hit and fl is None and cx is None:
            piece = caseng._termnode(c, None, None, keep)
            coef = piece if s > 0 else _neg(piece)
        else:
            rest.append((tn, s))
    if coef is None:
        return None
    R = _neg(_sum(rest)) if rest else _num(0)
    lhs = _prod([(caseng._pow(coef, _num(2)), 1), (S[1], 1)])
    eq = _sum([(lhs, 1), (caseng._pow(R, _num(2)), -1)])
    return roots(eq, var, depth + 1)

def _abssolve(f, var, depth):
    abs_nodes = []
    for n in _find(_S(f), ('abs',), []):
        if _has(n, var):
            abs_nodes.append(n)
    if not abs_nodes or len(abs_nodes) > 2:
        return None
    out = []
    n = len(abs_nodes)
    case = 0
    while case < (1 << n):
        g = _S(f)
        i = 0
        while i < n:
            sgn = 1 if (case >> i) & 1 == 0 else -1
            rep = abs_nodes[i][1] if sgn > 0 else _neg(abs_nodes[i][1])
            g = caseng.subst_tree(g, abs_nodes[i], rep)
            i += 1
        rr = roots(_S(g), var, depth + 1)
        if rr:
            out.extend(rr)
        case += 1
    return out

# ---- the main entry -------------------------------------------------------

def roots(f, var, depth=0):
    if depth > MAXDEPTH:
        return []
    g = _S(f)
    if not _has(g, var):
        return []
    g2, D = casalg._cleardenom(g, var)
    g2 = caspoly.expand(g2)
    p = caspoly.poly(g2, var)
    if p is not None:
        return poly_roots(p)
    if _find(g, ('sinh', 'cosh', 'tanh'), []):
        g = _S(casalg.to_exp(g))
    for fn in (_expsolve, _logsolve, _surdsolve, _abssolve):
        try:
            r = fn(g, var, depth)
        except Exception:
            r = None
        if r:
            return r
    sub = casalg._polyin(caspoly.expand(g2), 1)
    if sub is not None:
        u, co = sub
        out = []
        for v in poly_roots(co):
            out.extend(invert_eq(u, v, var, depth + 1))
        if out:
            return out
    if caseng.count_var(g, var) == 1:
        inv = caseng.invert(g, var, '_y')
        if inv is not None:
            return [_S(caseng.subst(inv, '_y', _num(0)))]
    return []

def solve_exact(tree, var='x'):
    # exact solutions of tree = 0, extraneous and out-of-domain ones removed
    f = _S(tree)
    out = []
    for r in _dedupe(roots(f, var, 0)):
        if check(f, var, r):
            out.append(r)
    return _sortroots(out)

def solve_any(tree, var='x', deg=False):
    # -> (list of trees, exact?)
    r = solve_exact(tree, var)
    if r:
        return (r, True)
    import cascalc
    return ([_num(v) for v in cascalc.solve(tree, var, deg)], False)

# ---- trigonometric equations ---------------------------------------------

def _trigreduce(f, var):
    # -> (name, A, B, [values]) with name(A var + B) = value
    g = caspoly.expand(_S(f))
    sub = casalg._polyin(g, 1)
    if sub is None:
        return None
    u, co = sub
    if u[0] not in _PRINC:
        return None
    r = _lin(u[1], var)
    if r is None:
        return None
    vals = []
    for v in poly_roots(co):
        x = _val(v)
        if x is None or isinstance(x, complex):
            continue
        vals.append(v)
    if not vals:
        return None
    return (u[0], r[0], r[1], vals)

def general_trig(f, var='x', nname='n'):
    # general solution, as a list of exact trees in n
    red = _trigreduce(f, var)
    if red is None:
        return None
    name, A, B, vals = red
    N = ('v', nname)
    out = []
    for v in vals:
        for a in trig_principal(name, v):
            per = _num(1) if name == 'tan' else _num(2)
            shift = _prod([(per, 1), (N, 1), (('v', 'pi'), 1)])
            out.append(_S(_sum([(_prod([(a, 1), (A, -1)]), 1),
                                (_prod([(shift, 1), (A, -1)]), 1),
                                (_prod([(B, 1), (A, -1)]), -1)])))
    return out

def solve_interval(tree, var='x', lo=None, hi=None):
    # exact solutions in [lo, hi); trig equations get every period in range
    f = _S(tree)
    red = _trigreduce(f, var)
    out = []
    if red is not None:
        name, A, B, vals = red
        lov = _val(lo) if lo is not None else -6.283185307179586
        hiv = _val(hi) if hi is not None else 6.283185307179586
        per = 1 if name == 'tan' else 2
        for v in vals:
            for a in trig_principal(name, v):
                k = -MAXPERIOD
                while k <= MAXPERIOD:
                    shift = _prod([(_num(per * k), 1), (('v', 'pi'), 1)])
                    x = _S(_prod([(_sum([(a, 1), (shift, 1), (B, -1)]), 1), (A, -1)]))
                    xv = _val(x)
                    if xv is not None and not isinstance(xv, complex) \
                            and xv >= lov - 1e-9 and xv < hiv - 1e-9:
                        out.append(x)
                    k += 1
        out = _dedupe(out)
        keep = []
        for r in out:
            if check(f, var, r):
                keep.append(r)
        return _sortroots(keep)
    for r in solve_exact(f, var):
        v = _val(r)
        if v is None or isinstance(v, complex):
            continue
        if lo is not None and v < _val(lo) - 1e-9:
            continue
        if hi is not None and v >= _val(hi) - 1e-9:
            continue
        out.append(r)
    return out

# ---- simultaneous equations ----------------------------------------------

def simultaneous(eqs, names):
    # every eq is a tree equal to zero; linear systems solved exactly
    n = len(names)
    if len(eqs) != n or n > 4:
        return None
    A = []
    b = []
    for e in eqs:
        g = caspoly.expand(_S(e))
        row = []
        rest = g
        for v in names:
            r = casalg.linin(rest, v)
            if r is None:
                return None
            c = caspoly.ratof(_S(r[0]))
            if c is None:
                return None
            row.append(c)
            rest = r[1]
        k = caspoly.ratof(_S(rest))
        if k is None:
            return None
        A.append(row)
        b.append(caspoly.rneg(k))
    sol = caspoly.solve_rat(A, b)
    if sol is None:
        return None
    return [caspoly.ratnode(s) for s in sol]

def linear_quadratic(lin, quad, xv='x', yv='y'):
    # lin, quad are trees equal to zero; -> list of (x, y) exact pairs
    r = casalg.linin(caspoly.expand(_S(lin)), yv)
    if r is None or r[0] == _num(0):
        r2 = casalg.linin(caspoly.expand(_S(lin)), xv)
        if r2 is None or r2[0] == _num(0):
            return None
        xs = _S(_prod([(_neg(r2[1]), 1), (r2[0], -1)]))
        sub = _S(caseng.subst(_S(quad), xv, xs))
        out = []
        for y in solve_exact(sub, yv):
            out.append((_S(caseng.subst(xs, yv, y)), y))
        return out
    ys = _S(_prod([(_neg(r[1]), 1), (r[0], -1)]))
    sub = _S(caseng.subst(_S(quad), yv, ys))
    out = []
    for x in solve_exact(sub, xv):
        out.append((x, _S(caseng.subst(ys, xv, x))))
    return out

# ---- inequalities ---------------------------------------------------------

def _poles(f, var):
    out = []
    g = _S(f)
    for tn, s in _terms(g):
        c, fl, cx, parts = caseng._termparts([(tn, 1)])
        for b, e in parts:
            r = caseng._ratval(e)
            if r is not None and r[0] < 0 and _has(b, var):
                out.extend(solve_exact(b, var))
    return out

def solve_ineq(f, op, var='x'):
    # f op 0 with op in '<', '<=', '>', '>='; -> list of (lo, hi, loclosed, hiclosed)
    g = _S(f)
    strict = (op == '<' or op == '>')
    up = (op == '>' or op == '>=')
    cuts = []
    for r in solve_exact(g, var):
        v = _val(r)
        if v is not None and not isinstance(v, complex):
            cuts.append((v, r, not strict))
    for r in _poles(g, var):
        v = _val(r)
        if v is not None and not isinstance(v, complex):
            cuts.append((v, r, False))
    cuts.sort(key=lambda it: it[0])
    pts = []
    for v, r, closed in cuts:
        if pts and abs(pts[-1][0] - v) < 1e-12:
            continue
        pts.append((v, r, closed))
    bounds = [None] + [p[0] for p in pts] + [None]
    out = []
    i = 0
    while i < len(bounds) - 1:
        a = bounds[i]
        b = bounds[i + 1]
        if a is None and b is None:
            probe = 0.0
        elif a is None:
            probe = b - 1.0
        elif b is None:
            probe = a + 1.0
        else:
            probe = (a + b) / 2.0
        try:
            y = caseng.evalf(g, probe, False, {var: probe})
        except Exception:
            y = None
        ok = False
        if y is not None and not isinstance(y, complex) and y == y:
            ok = (y > 0) if up else (y < 0)
        if ok:
            lo = None if i == 0 else pts[i - 1][1]
            loc = False if i == 0 else pts[i - 1][2]
            hi = None if i == len(bounds) - 2 else pts[i][1]
            hic = False if i == len(bounds) - 2 else pts[i][2]
            out.append([lo, hi, loc, hic])
        i += 1
    merged = []
    for iv in out:
        if merged and merged[-1][1] is not None and iv[0] is not None \
                and caseng.tostr(merged[-1][1]) == caseng.tostr(iv[0]) \
                and (merged[-1][3] or iv[2]):
            merged[-1][1] = iv[1]
            merged[-1][3] = iv[3]
        else:
            merged.append(iv)
    return merged

def ineq_str(ivs, var='x'):
    if not ivs:
        return 'no solution'
    parts = []
    for lo, hi, loc, hic in ivs:
        if lo is None and hi is None:
            return 'all real ' + var
        if lo is None:
            parts.append(var + (' <= ' if hic else ' < ') + caseng.tostr(hi))
        elif hi is None:
            parts.append(var + (' >= ' if loc else ' > ') + caseng.tostr(lo))
        else:
            parts.append(caseng.tostr(lo) + (' <= ' if loc else ' < ') + var +
                         (' <= ' if hic else ' < ') + caseng.tostr(hi))
    return ' or '.join(parts)

def ineq_set(ivs, var='x'):
    if not ivs:
        return '{}'
    parts = []
    for lo, hi, loc, hic in ivs:
        l = '(-inf' if lo is None else (('[' if loc else '(') + caseng.tostr(lo))
        r = 'inf)' if hi is None else (caseng.tostr(hi) + (']' if hic else ')'))
        parts.append(l + ', ' + r)
    return ' U '.join(parts)
