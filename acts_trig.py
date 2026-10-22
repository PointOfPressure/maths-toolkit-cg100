# Trig's actions (acts.py has the registry). Equations in sin, cos, tan and
# their reciprocals (solved on an interval, in degrees or radians), identities
# to check (one row with = or two rows), a sin x + b cos x (R form),
# expressions (small angles, compound angles, simplify), numbers (exact
# values), and, with nothing typed, the triangle and sector boxes.
import casui
from acts import a_graph

TRIG = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot')

def _hastrig(t, v):
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k in TRIG:
        return v is None or _has(t[1], v)
    for c in t[1:]:
        if _hastrig(c, v):
            return True
    return False

def _has(t, v):
    k = t[0]
    if k == 'v':
        return t[1] == v
    if k == 'n':
        return False
    for c in t[1:]:
        if _has(c, v):
            return True
    return False

def _deg():
    return casui.SET['angle'] == 'deg'

def _row(F):
    return F.rows[0]

def _eqn(F):
    # one trig equation in the variable, or two rows f and g
    if F.kind in ('blank', 'num', 'const', 'de', 'xy') or F.err:
        return False
    if F.pair == 'fg':
        return _hastrig(F.rows[0].f, F.var) or _hastrig(F.rows[1].f, F.var)
    r = _row(F)
    return not F.pair and r.rel == '=' and r.name is None and _hastrig(r.f, F.var)

def _expr(F):
    if F.pair or F.kind in ('blank', 'de', 'xy'):
        return False
    r = _row(F)
    return (r.rel == '' or r.name is not None) and _hastrig(r.f, F.var) and F.kind != 'num'

def rparts(f, v):
    # a sin A + b cos A + c: (a, b, c, A) trees, else None
    import recog
    a = b = None
    A = None
    c = []
    for t, sg in recog.terms(f, 1, []):
        fn = None
        co = []
        for g, e in recog.factors(t, 1, []):
            if g[0] in ('sin', 'cos') and _has(g[1], v) and e > 0 and fn is None:
                fn = g
            elif _has(g, v):
                return None
            else:
                co.append((g, e))
        ct = ('n', sg)
        for g, e in co:
            ct = ('*', ct, g) if e > 0 else ('/', ct, g)
        if fn is None:
            c.append(ct)
            continue
        if A is not None and fn[1] != A:
            return None
        A = fn[1]
        if fn[0] == 'sin':
            a = ct if a is None else ('+', a, ct)
        else:
            b = ct if b is None else ('+', b, ct)
    if a is None or b is None:
        return None
    k = ('n', 0)
    for t in c:
        k = ('+', k, t)
    return (a, b, k, A)

def _simple(F):
    # sin x = k (or sec x = k ...): the other ratios
    r = _row(F)
    if F.pair or r.rel != '=' or r.name is not None:
        return False
    for L, R in ((r.lhs, r.rhs), (r.rhs, r.lhs)):
        if L[0] in TRIG and L[1] == ('v', F.var) and not _has(R, F.var):
            return True
    return False

def _small(t, v):
    # every trig argument is a multiple of the variable: small when it is
    k = t[0]
    if k == 'n' or k == 'v':
        return True
    if k in TRIG:
        import recog
        pq = recog.lin(t[1], v)
        if pq is None or recog.has(pq[1], v) or recog.numv(pq[1]) != 0:
            return False
    for c in t[1:]:
        if not _small(c, v):
            return False
    return True

def t_solve(F):
    if not _eqn(F):
        return []
    d = _deg()
    v = F.var
    ask = [('from ' + v + ' =', 1, True), ('to ' + v + ' =', 1, True)]
    out = [(1 if d else 2, ('Solve (degrees)', 'e_tsolve', 'solve', 'deg', ask)),
           (2 if d else 1, ('Solve (radians)', 'e_tsolve', 'solve', 'rad', ask)),
           (6, ('Identity?', 'e_trig', 'identity', None, None))]
    if _simple(F):
        out.append((3, ('Other ratios', 'e_trig', 'ratios', None,
                        ('choose', ['0 to 90 deg (acute)', '90 to 180 deg (obtuse)',
                                    '180 to 270 deg', '270 to 360 deg']))))
    return out

def t_expr(F):
    if not _expr(F):
        return []
    v = F.var
    f = _row(F).f
    out = [(5, ('Simplify', 'e_trig', 'simplify', None, None)),
           (6, ('Expand', 'e_trig', 'expand', None, None))]
    if _small(f, v):
        out.append((3, ('Small angle approx', 'e_trig', 'small', None, None)))
    if rparts(f, v) is not None:
        x = v
        out.append((1, ('R form', 'e_trig', 'rform', None,
                        ('choose', ['R sin(' + x + ' + a)', 'R sin(' + x + ' - a)',
                                    'R cos(' + x + ' + a)', 'R cos(' + x + ' - a)']))))
    return out

def t_pair(F):
    if F.pair == 'fg' and _eqn(F):
        return [(0, ('Identity?', 'e_trig', 'identity', None, None))]
    return []

def t_num(F):
    if F.kind == 'num' and not F.pair and _hastrig(_row(F).f, None) or \
            F.kind == 'num' and not F.pair and _inv(_row(F).f):
        return [(1, ('Exact value', 'e_trig', 'evaluate', None, None))]
    return []

def _inv(t):
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k in ('asin', 'acos', 'atan'):
        return True
    for c in t[1:]:
        if _inv(c):
            return True
    return False

def t_blank(F):
    if F.kind != 'blank':
        return []
    u = 'deg' if _deg() else 'rad'
    return [(1, ('Triangle', 'e_tri', 'triangle', None,
                 ('boxes', ['a', 'b', 'c', 'A', 'B', 'C', 'area'], 3))),
            (2, ('Arc and sector', 'e_tri', 'sector', None,
                 ('boxes', ['r', 'angle (' + u + ')', 'arc', 'area', 'perimeter', 'segment'], 2)))]

def t_graph(F):
    if _expr(F) and not F.letters:
        return a_graph(F)
    return []

ACTS = (t_blank, t_solve, t_pair, t_expr, t_num, t_graph)
