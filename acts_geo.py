# Coord geometry's actions (acts.py has the registry and the others).
from acts import _count

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
ACTS = GEO
