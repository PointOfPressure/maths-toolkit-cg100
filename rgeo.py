# Recognising Coord geometry: points from the boxes, each row a line, a
# circle, another curve, or half of a parametric pair (recog.py reads the
# other topics; this loads only for Coord geometry).
import caslex
from recog import (Form, parse_row, letters, has, hasfloat, _and)

def tdeg(t, vs):
    # total degree in the letters vs (x and y), else None
    k = t[0]
    if k == 'n':
        return 0
    if k == 'v':
        return 1 if t[1] in vs else 0
    if k == '+' or k == '-':
        a = tdeg(t[1], vs)
        b = tdeg(t[2], vs)
        if a is None or b is None:
            return None
        return a if a > b else b
    if k == 'neg':
        return tdeg(t[1], vs)
    if k == '*':
        a = tdeg(t[1], vs)
        b = tdeg(t[2], vs)
        if a is None or b is None:
            return None
        return a + b
    if k == '/':
        if tdeg(t[2], vs) != 0:
            return None
        return tdeg(t[1], vs)
    if k == '^':
        e = t[2]
        d = tdeg(t[1], vs)
        if d == 0 and tdeg(e, vs) == 0:
            return 0
        if d is None or e[0] != 'n' or not isinstance(e[1], int) or e[1] < 0:
            return None
        return d * e[1]
    for v in vs:
        if has(t, v):
            return None
    return 0

def _geokind(r, F):
    # a row: 'line', 'circle', 'curve', or 'x(t)' / 'y(t)' / 'expr' for a
    # parametric pair
    if r.rel != '=':
        return 'expr'
    if r.name in ('x', 'y'):
        ls = letters(r.f)
        if [c for c in ls if c not in ('x', 'y')] and 'x' not in ls and 'y' not in ls:
            return r.name + '(t)'
    E = recog_eq(r)
    d = tdeg(E, ('x', 'y'))
    if d is not None and d <= 1:
        return 'line'
    if d == 2:
        import eng
        cx = eng.coeffs(E, 'x')
        cy = eng.coeffs(E, 'y')
        if cx is not None and cy is not None and len(cx) == 3 and len(cy) == 3:
            if not has(cx[1], 'y') and not has(cy[1], 'x') and \
                    eng.S(('-', cx[2], cy[2])) == ('n', 0) and not has(cx[2], 'y'):
                return 'circle'
    return 'curve'

def recog_eq(r):
    # the row as one tree that is 0
    if r.name is not None and len(r.name) == 1:
        return ('-', ('v', r.name), r.f)
    return ('-', r.lhs, r.rhs) if r.rel else r.f

def geo(pts, eqs):
    # pts: [(x text, y text)] from the boxes A, B, C; eqs: typed rows
    F = Form()
    F.kind = 'geo'
    F.points = []
    F.items = []
    for i in range(len(pts)):
        xs, ys = pts[i]
        nm = 'ABC'[i]
        if not xs.strip() and not ys.strip():
            continue
        if not xs.strip() or not ys.strip():
            F.err = nm + ': fill in both boxes'
            F.note = F.err
            return F
        try:
            xt = caslex.parse(xs)
            yt = caslex.parse(ys)
        except ValueError as e:
            F.err = nm + ': ' + str(e)
            F.note = F.err
            return F
        if xt is None or yt is None:
            F.err = nm + ': cannot read that'
            F.note = F.err
            return F
        F.points.append((nm, xt, yt))
    for t in eqs:
        r = parse_row(t)
        if r.err:
            F.err = r.err
            F.note = F.err
            return F
        F.rows.append(r)
    for r in F.rows:
        F.items.append(_geokind(r, F))
        if hasfloat(r.f):
            F.dec = True
    ks = F.items
    if len(ks) == 2 and sorted([k[0] for k in ks if k in ('x(t)', 'y(t)')]) == ['x', 'y'] or \
            ks == ['expr', 'expr']:
        F.items = ['param']
    ls = []
    for p in F.points:
        letters(p[1], ls)
        letters(p[2], ls)
    for r in F.rows:
        letters(r.f, ls)
        if r.name is not None and len(r.name) == 1 and r.name not in ls:
            ls.append(r.name)
    if F.items == ['param']:
        tv = [c for c in ls if c not in ('x', 'y')]
        F.var = tv[0] if tv else 't'
        F.letters = [c for c in tv if c != F.var]
    else:
        F.var = 'x'
        F.letters = [c for c in ls if c not in ('x', 'y')]
    for p in F.points:
        if hasfloat(p[1]) or hasfloat(p[2]):
            F.dec = True
    F.note = _geonote(F)
    return F

def _geonote(F):
    n = len(F.points)
    names = [p[0] for p in F.points]
    parts = []
    if F.items == ['param']:
        parts.append('parametric x(' + F.var + '), y(' + F.var + ')')
    else:
        for k in F.items:
            parts.append({'line': 'line', 'circle': 'circle', 'curve': 'curve',
                          'expr': 'curve y = f(x)'}.get(k, k))
        if len(parts) == 2 and parts[0] == parts[1]:
            parts = ['two ' + parts[0] + 's']
    if n == 1:
        parts.append('point ' + names[0])
    elif n > 1:
        parts.append(str(n) + ' points ' + _and(names))
    if not parts:
        return 'nothing filled in'
    s = _and(parts)
    if F.letters:
        s += ', ' + _and(F.letters) + ' unknown'
    return s
