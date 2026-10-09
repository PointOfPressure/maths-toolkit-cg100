# Coord geometry actions: two or three points (gradient, midpoint, distance,
# the line through them, the perpendicular bisector, circles), a point with
# a line or circle (parallel and perpendicular lines, foot of the
# perpendicular, tangent, inside or out), a circle in any form (centre and
# radius by completing the square), where lines and curves meet, and
# parametric curves. Exact arithmetic, mark-scheme working.
import caseng
import caspoly
import eng
import recog
import rgeo
from eng import S, N, ZERO, ONE, txt, eq, val, has

X = ('v', 'x')
Y = ('v', 'y')

def _b(t):
    # (-3), (k + 1): a value in brackets only when it needs them
    s = txt(t)
    if s[:1] == '-' or ' + ' in s or ' - ' in s:
        return '(' + s + ')'
    return s

def _pts(F, names):
    out = []
    for nm in names:
        for p in F.points:
            if p[0] == nm:
                out.append(p)
    return out

def _pt(p):
    return p[0] + '(' + txt(p[1]) + ', ' + txt(p[2]) + ')'

def _coords(x, y):
    return '(' + txt(x) + ', ' + txt(y) + ')'

def _row(F, kind):
    for r, k in zip(F.rows, F.items):
        if k == kind:
            return r
    return None

# ---- lines as a x + b y + c = 0 ----------------------------------------------------------------

def _abc(E):
    # E = a x + b y + c (trees)
    g = caspoly.expand(S(E))
    ra = eng.linin(g, 'x')
    if ra is None:
        raise ValueError('not a straight line')
    rb = eng.linin(ra[1], 'y')
    if rb is None or has(ra[0], 'y'):
        raise ValueError('not a straight line')
    return S(ra[0]), S(rb[0]), S(rb[1])

def _gradient(a, b):
    # of a x + b y + c = 0; None when vertical
    if b == ZERO:
        return None
    return S(('neg', ('/', a, b)))

def _integer_form(a, b, c):
    # a x + b y + c = 0 with whole numbers, a > 0 (or b > 0 when a = 0)
    m = eng._intscale(eng.sumterms(a, 1, []) + eng.sumterms(b, 1, []) + eng.sumterms(c, 1, []))
    if m != 1:
        a = S(('*', N(m), a))
        b = S(('*', N(m), b))
        c = S(('*', N(m), c))
    ra = [caspoly.ratof(t) for t in (a, b, c)]
    if None not in ra:
        g = 0
        for r in ra:
            g = recog._gcd(g, r[0])
        if g > 1:
            a, b, c = [S(('/', t, N(g))) for t in (a, b, c)]
    lead = a if a != ZERO else b
    if eng.neg(lead)[0]:
        a, b, c = [S(('neg', t)) for t in (a, b, c)]
    t = eng.build([(u, 1) for u in (eng.mul(a, X), eng.mul(b, Y), c) if u != ZERO and a != ZERO or
                   (u != ZERO and u is not None)])
    return txt(t, False) + ' = 0'

def _line_through(x1, y1, m, lines, name='y'):
    # y - y1 = m(x - x1), then y = mx + c and the whole-number form
    if m is None:
        lines.append(eng.boxs('', 'x = ' + txt(x1)))
        return
    lhs = 'y' if y1 == ZERO else 'y - ' + _b(y1)
    rhs = 'x' if x1 == ZERO else '(x - ' + _b(x1) + ')'
    lines.append(lhs + ' = ' + _b(m) + ('' if rhs == 'x' and m != ONE else '') + rhs)
    c = S(('-', y1, ('*', m, x1)))
    rhs = eng.add(eng.mul(m, X) if m != ZERO else ZERO, c) if m != ZERO else c
    lines.append(eng.boxs('y = ', txt(rhs, False), rhs))
    a, b, cc = S(('neg', m)), ONE, S(('neg', c))
    if caspoly.ratof(m) is not None and caspoly.ratof(c) is not None:
        lines.append(_integer_form(a, b, cc))

# ---- two points ---------------------------------------------------------------------------------

def _two(F, arg):
    names = arg or 'AB'
    ps = _pts(F, names)
    if len(ps) != 2:
        raise ValueError('needs points ' + names[0] + ' and ' + names[1])
    p, q = ps
    if S(('-', p[1], q[1])) == ZERO and S(('-', p[2], q[2])) == ZERO:
        raise ValueError(names[0] + ' and ' + names[1] + ' are the same point')
    return ps

def _grad(p, q, lines):
    dy = S(('-', q[2], p[2]))
    dx = S(('-', q[1], p[1]))
    lines.append('gradient ' + p[0] + q[0] + ' = (' + txt(q[2]) + ' - ' + _b((p[2])) + ')/(' +
                 txt(q[1]) + ' - ' + _b((p[1])) + ')')
    if dx == ZERO:
        lines.append(p[0] + q[0] + ' is vertical')
        return None
    m = S(('/', dy, dx))
    lines.append('= ' + txt(('/', dy, dx)) + (' = ' + txt(m) if txt(m) != txt(('/', dy, dx)) else ''))
    return m

def _mid(p, q):
    return S(('/', ('+', p[1], q[1]), N(2))), S(('/', ('+', p[2], q[2]), N(2)))

def gradient(F, arg, vals):
    p, q = _two(F, arg)
    lines = [_pt(p) + ',  ' + _pt(q)]
    m = _grad(p, q, lines)
    if lines[-1].startswith('= '):
        lines.pop()
    if m is None:
        lines.append(eng.boxs('', 'vertical: no gradient'))
    else:
        lines.append(eng.box('gradient = ', m, not F.dec))
        if m != ZERO:
            lines.append('perpendicular gradient ' + txt(S(('neg', ('/', ONE, m)))))
    return lines

def midpoint(F, arg, vals):
    p, q = _two(F, arg)
    mx, my = _mid(p, q)
    lines = [_pt(p) + ',  ' + _pt(q),
             'midpoint = ((' + txt(p[1]) + ' + ' + _b((q[1])) + ')/2, (' + txt(p[2]) + ' + ' +
             _b((q[2])) + ')/2)']
    lines.append(eng.boxs('midpoint ', _coords(mx, my)))
    return lines

def distance(F, arg, vals):
    p, q = _two(F, arg)
    dx = S(('-', q[1], p[1]))
    dy = S(('-', q[2], p[2]))
    d2 = S(caspoly.expand(S(('+', ('^', dx, N(2)), ('^', dy, N(2))))))
    lines = [_pt(p) + ',  ' + _pt(q),
             p[0] + q[0] + '^2 = (' + txt(dx) + ')^2 + (' + txt(dy) + ')^2 = ' + txt(d2)]
    d = eng.nice(('sqrt', d2))
    lines.append(eng.box(p[0] + q[0] + ' = ', d, not F.dec))
    return lines

def line(F, arg, vals):
    p, q = _two(F, arg)
    lines = [_pt(p) + ',  ' + _pt(q)]
    m = _grad(p, q, lines)
    _line_through(p[1], p[2], m, lines)
    return lines

def perpbis(F, arg, vals):
    p, q = _two(F, arg)
    lines = [_pt(p) + ',  ' + _pt(q)]
    mx, my = _mid(p, q)
    lines.append('midpoint ' + _coords(mx, my))
    m = _grad(p, q, lines)
    if m is None:
        lines.append(eng.boxs('y = ', txt(my), my))
        return lines
    if m == ZERO:
        lines.append(eng.boxs('', 'x = ' + txt(mx)))
        return lines
    pm = S(('neg', ('/', ONE, m)))
    lines.append('perpendicular gradient = ' + txt(pm))
    _line_through(mx, my, pm, lines)
    return lines

def _circle_lines(a, b, r2, lines):
    # (x - a)^2 + (y - b)^2 = r^2, and expanded
    t = ('+', eng.sq(eng.add(X, S(('neg', a)))), eng.sq(eng.add(Y, S(('neg', b)))))
    lines.append(eng.boxs('', txt(t, False) + ' = ' + txt(r2), None))
    ex = caspoly.expand(S(('-', t, r2)))
    lines.append('expanded: ' + txt(ex, False) + ' = 0')

def circlediam(F, arg, vals):
    p, q = _two(F, arg)
    lines = [_pt(p) + ',  ' + _pt(q)]
    a, b = _mid(p, q)
    lines.append('centre = midpoint ' + _coords(a, b))
    r2 = S(caspoly.expand(S(('+', ('^', ('-', p[1], a), N(2)), ('^', ('-', p[2], b), N(2))))))
    lines.append('r^2 = (' + txt(S(('-', p[1], a))) + ')^2 + (' + txt(S(('-', p[2], b))) + ')^2 = ' + txt(r2))
    _circle_lines(a, b, r2, lines)
    lines.append('radius ' + txt(eng.nice(('sqrt', r2))))
    return lines

# ---- three points --------------------------------------------------------------------------------

def circle3(F, arg, vals):
    ps = _pts(F, 'ABC')
    lines = [',  '.join([_pt(p) for p in ps]), 'x^2 + y^2 + Dx + Ey + F = 0 through each:']
    A = []
    b = []
    for p in ps:
        x = caspoly.ratof(S(p[1]))
        y = caspoly.ratof(S(p[2]))
        if x is None or y is None:
            raise ValueError('needs numbers for the points')
        A.append([x, y, (1, 1)])
        rhs = caspoly.rneg(caspoly.radd(caspoly.rmul(x, x), caspoly.rmul(y, y)))
        b.append(rhs)
        lines.append(txt(eng.R(*x)) + 'D + ' + _b((eng.R(*y))) + 'E + F = ' + txt(eng.R(*rhs)))
    sol = caspoly.solve_rat(A, b)
    if sol is None:
        lines.append(eng.boxs('', 'the points are on one line: no circle'))
        return lines
    D, E, Fc = [eng.R(*s) for s in sol]
    lines.append('D = ' + txt(D) + ',  E = ' + txt(E) + ',  F = ' + txt(Fc))
    a = S(('/', ('neg', D), N(2)))
    bb = S(('/', ('neg', E), N(2)))
    r2 = S(('-', ('+', ('^', a, N(2)), ('^', bb, N(2))), Fc))
    lines.append('centre ' + _coords(a, bb) + ',  r^2 = ' + txt(r2))
    _circle_lines(a, bb, r2, lines)
    lines.append('radius ' + txt(eng.nice(('sqrt', r2))))
    return lines

def triangle(F, arg, vals):
    ps = _pts(F, 'ABC')
    lines = [',  '.join([_pt(p) for p in ps])]
    sides = []
    for p, q in ((ps[0], ps[1]), (ps[1], ps[2]), (ps[0], ps[2])):
        d2 = S(caspoly.expand(S(('+', ('^', ('-', q[1], p[1]), N(2)), ('^', ('-', q[2], p[2]), N(2))))))
        sides.append((p[0] + q[0], d2))
        lines.append(p[0] + q[0] + '^2 = ' + txt(d2) + ',  ' + p[0] + q[0] + ' = ' + txt(eng.nice(('sqrt', d2))))
    vs = [val(s[1]) for s in sides]
    right = None
    if None not in vs:
        for i in range(3):
            o = [vs[j] for j in range(3) if j != i]
            if abs(vs[i] - o[0] - o[1]) < 1e-9 * (1 + vs[i]):
                right = i
    if right is not None:
        nm = sides[right][0]
        corner = [c for c in 'ABC' if c not in nm][0]
        o = [sides[j][0] for j in range(3) if j != right]
        lines.append(o[0] + '^2 + ' + o[1] + '^2 = ' + nm + '^2')
        lines.append(eng.boxs('', 'right angle at ' + corner))
    else:
        lines.append(eng.boxs('', 'no right angle'))
    # the angles by the cosine rule
    if None not in vs:
        import math
        for i, corner in ((0, 'A'), (1, 'B'), (2, 'C')):
            opp = {'A': 1, 'B': 2, 'C': 0}[corner]
            adj = [vs[j] for j in range(3) if j != opp]
            c = (adj[0] + adj[1] - vs[opp]) / (2.0 * (adj[0] * adj[1]) ** 0.5)
            c = 1.0 if c > 1 else (-1.0 if c < -1 else c)
            ang = math.acos(c)
            lines.append('angle ' + corner + ' = ' + eng.sf(ang, 3) + ' rad = ' +
                         eng.sf(ang * 180 / math.pi, 3) + ' deg')
    # area by the shoelace formula
    (a, x1, y1), (b, x2, y2), (c, x3, y3) = ps
    ar = S(('/', ('-', ('+', ('*', x1, ('-', y2, y3)), ('+', ('*', x2, ('-', y3, y1)), ('*', x3, ('-', y1, y2)))),
                  ZERO), N(2)))
    av = val(ar)
    if av is not None and not isinstance(av, complex) and av < 0:
        ar = S(('neg', ar))
    lines.append(eng.box('area = ', ar, not F.dec))
    return lines

def circleline(F, arg, vals):
    # through A and B, centre on the line: the perpendicular bisector of AB
    # meets the line at the centre
    p, q = _pts(F, 'AB')
    r, a, b, c = _lineof(F)
    lines = [_pt(p) + ',  ' + _pt(q) + ',  centre on ' +
             (eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f))]
    mx, my = _mid(p, q)
    m = _grad(p, q, [])
    lines.append('the centre is on the perpendicular bisector of AB, through ' + _coords(mx, my))
    # perpendicular bisector as a2 x + b2 y + c2 = 0
    if m is None:
        a2, b2, c2 = ZERO, ONE, S(('neg', my))
    elif m == ZERO:
        a2, b2, c2 = ONE, ZERO, S(('neg', mx))
    else:
        pm = S(('neg', ('/', ONE, m)))
        lines.append('perpendicular gradient ' + txt(pm))
        a2, b2, c2 = S(('neg', pm)), ONE, S(('-', ('*', pm, mx), my))
    det = S(('-', ('*', a, b2), ('*', a2, b)))
    if det == ZERO:
        lines.append(eng.boxs('', 'the line is parallel to the bisector: no such circle'))
        return lines
    cx = S(('/', ('-', ('*', b, c2), ('*', b2, c)), det))
    cy = S(('/', ('-', ('*', c, a2), ('*', c2, a)), det))
    lines.append(eng.boxs('centre ', _coords(cx, cy)))
    r2 = S(caspoly.expand(S(('+', ('^', ('-', p[1], cx), N(2)), ('^', ('-', p[2], cy), N(2))))))
    lines.append('r^2 = ' + _pt(p)[1:] + ' to the centre squared = ' + txt(r2))
    _circle_lines(cx, cy, r2, lines)
    lines.append('radius ' + txt(eng.nice(('sqrt', r2))))
    return lines

# ---- a point and a line ---------------------------------------------------------------------------

def _lineof(F):
    r = _row(F, 'line')
    E = rgeo.recog_eq(r)
    a, b, c = _abc(E)
    return r, a, b, c

def parallel(F, arg, vals):
    p = F.points[0]
    r, a, b, c = _lineof(F)
    m = _gradient(a, b)
    lines = [eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f), _pt(p)]
    lines.append('gradient of the line ' + (txt(m) if m is not None else ': vertical'))
    _line_through(p[1], p[2], m, lines)
    return lines

def perpendicular(F, arg, vals):
    p = F.points[0]
    r, a, b, c = _lineof(F)
    m = _gradient(a, b)
    lines = [eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f), _pt(p)]
    if m is None:
        lines.append('the line is vertical: the perpendicular is horizontal')
        lines.append(eng.boxs('y = ', txt(p[2]), p[2]))
        return lines
    if m == ZERO:
        lines.append(eng.boxs('', 'x = ' + txt(p[1])))
        return lines
    pm = S(('neg', ('/', ONE, m)))
    lines.append('gradient ' + txt(m) + ',  perpendicular gradient ' + txt(pm))
    _line_through(p[1], p[2], pm, lines)
    return lines

def foot(F, arg, vals):
    # where the perpendicular from A meets the line, and the distance
    p = F.points[0]
    r, a, b, c = _lineof(F)
    lines = [txt(eng.build([(eng.mul(a, X), 1), (eng.mul(b, Y), 1), (c, 1)])) + ' = 0', _pt(p)]
    # the foot is A + t(a, b) with a(x) + b(y) + c = 0
    tv = S(('/', ('neg', ('+', ('+', ('*', a, p[1]), ('*', b, p[2])), c)),
            ('+', ('^', a, N(2)), ('^', b, N(2)))))
    fx = S(('+', p[1], ('*', a, tv)))
    fy = S(('+', p[2], ('*', b, tv)))
    lines.append('perpendicular from ' + p[0] + ' has direction (' + txt(a) + ', ' + txt(b) + ')')
    lines.append(eng.boxs('foot of the perpendicular ', _coords(fx, fy)))
    d2 = S(caspoly.expand(S(('+', ('^', ('-', fx, p[1]), N(2)), ('^', ('-', fy, p[2]), N(2))))))
    lines.append(eng.box('distance = ', eng.nice(('sqrt', d2)), not F.dec))
    return lines

def online(F, arg, vals):
    p = F.points[0]
    r = [x for x, k in zip(F.rows, F.items) if k in ('line', 'circle', 'curve')][0]
    E = rgeo.recog_eq(r)
    lhs = caseng.subst(caseng.subst(E, 'x', p[1]), 'y', p[2])
    v = S(lhs)
    lines = ['put x = ' + txt(p[1]) + ', y = ' + txt(p[2]) + ' into ' +
             (eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f))]
    lines.append('left - right = ' + txt(v))
    lines.append(eng.boxs('', p[0] + (' is on it' if v == ZERO else ' is not on it')))
    return lines

# ---- circles -----------------------------------------------------------------------------------------

def _circle(F):
    # centre (a, b) and r^2 of the circle row, with the completing-the-square lines
    r = _row(F, 'circle')
    E = S(rgeo.recog_eq(r))
    E = caspoly.expand(E)
    cx = eng.coeffs(E, 'x')
    k = cx[2]
    if k != ONE:
        E = caspoly.expand(S(('/', E, k)))
        cx = eng.coeffs(E, 'x')
    cy = eng.coeffs(cx[0], 'y')
    D = cx[1]
    Ey = cy[1] if len(cy) > 1 else ZERO
    C = cy[0]
    a = S(('/', ('neg', D), N(2)))
    b = S(('/', ('neg', Ey), N(2)))
    r2 = S(caspoly.expand(S(('-', ('+', ('^', a, N(2)), ('^', b, N(2))), C))))
    lines = [eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f)]
    if k != ONE:
        lines.append('divide by ' + txt(k))
    sqx = eng.sq(eng.add(X, S(('neg', a))))
    sqy = eng.sq(eng.add(Y, S(('neg', b))))
    parts = [(sqx, 1)]
    if a != ZERO:
        parts.append((eng.sq(a), -1))
    parts.append((sqy, 1))
    if b != ZERO:
        parts.append((eng.sq(b), -1))
    parts.append((C, 1))
    if a != ZERO or b != ZERO:
        lines.append(txt(eng.build(parts), False) + ' = 0')
    lines.append(txt(('+', sqx, sqy), False) + ' = ' + txt(r2))
    return a, b, r2, lines

def centre(F, arg, vals):
    a, b, r2, lines = _circle(F)
    lines.append(eng.boxs('centre ', _coords(a, b)))
    rv = val(r2)
    if rv is None and F.letters:
        lines.append(eng.boxs('radius^2 = ', txt(r2), r2))
        import cassolve
        k = F.letters[0]
        s = cassolve.ineq_str(cassolve.solve_ineq(r2, '>', k), k)
        if s:
            lines.append('a real circle needs r^2 > 0:  ' + s)
        return lines
    if rv is not None and rv <= 0:
        lines.append(eng.boxs('', 'r^2 = ' + txt(r2) + ' is not positive: no circle'))
        return lines
    lines.append(eng.box('radius = ', eng.nice(('sqrt', r2)), not F.dec))
    return lines

def tangent(F, arg, vals):
    p = F.points[0]
    a, b, r2, lines = _circle(F)
    lines = lines[:1] + ['centre ' + _coords(a, b)]
    on = S(caspoly.expand(S(('-', ('+', ('^', ('-', p[1], a), N(2)), ('^', ('-', p[2], b), N(2))), r2))))
    if on != ZERO:
        lines.append(eng.boxs('', p[0] + ' is not on the circle'))
        return lines
    dx = S(('-', p[1], a))
    dy = S(('-', p[2], b))
    if dx == ZERO:
        lines.append('radius to ' + p[0] + ' is vertical: the tangent is horizontal')
        lines.append(eng.boxs('y = ', txt(p[2]), p[2]))
        return lines
    m = S(('/', dy, dx))
    lines.append('gradient of the radius to ' + p[0] + ' = ' + txt(m))
    if m == ZERO:
        lines.append(eng.boxs('', 'x = ' + txt(p[1])))
        return lines
    pm = S(('neg', ('/', ONE, m)))
    lines.append('tangent gradient = ' + txt(pm))
    _line_through(p[1], p[2], pm, lines)
    return lines

def inside(F, arg, vals):
    p = F.points[0]
    a, b, r2, lines = _circle(F)
    lines = lines[:1] + ['centre ' + _coords(a, b) + ',  r^2 = ' + txt(r2)]
    d2 = S(caspoly.expand(S(('+', ('^', ('-', p[1], a), N(2)), ('^', ('-', p[2], b), N(2))))))
    lines.append('distance^2 from the centre to ' + p[0] + ' = ' + txt(d2))
    dv = val(d2)
    rv = val(r2)
    if dv is None or rv is None:
        raise ValueError('needs numbers')
    where = 'on' if abs(dv - rv) < 1e-12 else ('inside' if dv < rv else 'outside')
    lines.append(eng.boxs('', p[0] + ' is ' + where + ' the circle'))
    lines.append('distance ' + txt(eng.nice(('sqrt', d2))) + ',  radius ' + txt(eng.nice(('sqrt', r2))))
    return lines

# ---- lines on their own, and where things meet ---------------------------------------------------------

def lineform(F, arg, vals):
    r, a, b, c = _lineof(F)
    lines = [eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f)]
    m = _gradient(a, b)
    if m is None:
        lines.append(eng.boxs('', 'x = ' + txt(S(('neg', ('/', c, a)))) + ': vertical'))
        return lines
    k = S(('neg', ('/', c, b)))
    rhs = eng.add(eng.mul(m, X) if m != ZERO else ZERO, k) if m != ZERO else k
    lines.append(eng.boxs('y = ', txt(rhs, False), rhs))
    lines.append('gradient ' + txt(m) + ',  y-intercept (0, ' + txt(k) + ')')
    if a != ZERO:
        lines.append('x-intercept (' + txt(S(('neg', ('/', c, a)))) + ', 0)')
    if caspoly.ratof(m) is not None and caspoly.ratof(k) is not None:
        lines.append(_integer_form(a, b, c))
    return lines

def meet(F, arg, vals):
    # two rows: where they meet, by substitution (e_fn's simultaneous solver)
    import e_fn
    G = recog.Form()
    G.rows = F.rows
    G.pair = 'simul'
    G.vars2 = ['x', 'y']
    G.var = 'x'
    G.letters = F.letters
    G.dec = F.dec
    lines = e_fn.simul(G, None, None)
    if F.items.count('circle') == 1 and F.items.count('line') == 1:
        n = len([ln for ln in lines if isinstance(ln, tuple) and ln[0] == '='])
        tl = [ln for ln in lines if isinstance(ln, str) and 'no real roots' in ln]
        if tl:
            lines.append('the line misses the circle')
        elif n == 1:
            lines.append('one point: the line is a tangent')
    return lines

def compare(F, arg, vals):
    # two lines: parallel, perpendicular or neither
    ms = []
    lines = []
    for r in F.rows:
        a, b, c = _abc(rgeo.recog_eq(r))
        m = _gradient(a, b)
        ms.append(m)
        lines.append((eq(r.lhs, r.rhs) if r.name is None else r.name + ' = ' + txt(r.f)) +
                     ':  gradient ' + (txt(m) if m is not None else 'none (vertical)'))
    m1, m2 = ms
    if m1 is None or m2 is None:
        s = 'parallel' if m1 is None and m2 is None else \
            ('perpendicular' if (m1 == ZERO or m2 == ZERO) else 'neither')
    elif S(('-', m1, m2)) == ZERO:
        s = 'parallel'
    else:
        pr = S(('*', m1, m2))
        lines.append('product of the gradients = ' + txt(pr))
        s = 'perpendicular' if pr == N(-1) else 'neither parallel nor perpendicular'
    lines.append(eng.boxs('', s))
    return lines

# ---- parametric ---------------------------------------------------------------------------------------

def _xy(F):
    r1, r2 = F.rows
    if F.items == ['param'] and r1.rel == '=':
        xs = r1.f if r1.name == 'x' else r2.f
        ys = r2.f if r2.name == 'y' else r1.f
        return xs, ys
    return r1.f, r2.f

def cartesian(F, arg, vals):
    t = F.var
    xs, ys = _xy(F)
    lines = ['x = ' + txt(xs), 'y = ' + txt(ys)]
    for a, b, an, bn in ((xs, ys, 'x', 'y'), (ys, xs, 'y', 'x')):
        sub = []
        try:
            got = eng.solve_for(('v', an), a, t, sub)
        except (eng.Stuck, eng.NoRoot):
            continue
        if len(got) != 1:
            continue
        lines.append('from ' + an + ':  ' + t + ' = ' + txt(got[0]))
        put = caseng.subst(b, t, got[0])
        lines.append(bn + ' = ' + txt(put))
        res = eng.nice(put)
        lines.append(eng.boxs(bn + ' = ', txt(res), res))
        return lines
    # x = a sin t + b, y = c cos t + d: sin^2 + cos^2 = 1
    sx = _trigpart(xs, t)
    sy = _trigpart(ys, t)
    if sx and sy and sx[0] != sy[0] and sx[1] == sy[1]:
        U = ('-', X, sx[3])
        V = ('-', Y, sy[3])
        lines.append(sx[0] + '(' + txt(sx[1]) + ') = ' + txt(eng.nice(('/', U, sx[2]))) + ',  ' +
                     sy[0] + '(' + txt(sy[1]) + ') = ' + txt(eng.nice(('/', V, sy[2]))))
        lines.append('sin^2 + cos^2 = 1')
        res = ('+', eng.sq(eng.nice(('/', U, sx[2]))), eng.sq(eng.nice(('/', V, sy[2]))))
        lines.append(eng.boxs('', txt(res, False) + ' = 1', None))
        return lines
    raise ValueError('cannot get ' + t + ' on its own from x or y')

def _trigpart(e, t):
    # e = p sin(arg) + q (or cos): (name, arg, p, q), else None
    for fn in ('sin', 'cos'):
        found = []
        _find(e, fn, t, found)
        if len(found) == 1:
            g = caseng.subst_tree(e, found[0], ('v', 'zs'))
            pq = recog.lin(g, 'zs')
            if pq is not None and not has(pq[0], t) and not has(pq[1], t):
                return (fn, found[0][1], S(pq[0]), S(pq[1]))
    return None

def _find(e, fn, t, out):
    k = e[0]
    if k == fn and has(e, t):
        out.append(e)
        return
    if k in ('n', 'v'):
        return
    for c in e[1:]:
        _find(c, fn, t, out)

def at(F, arg, vals):
    t = F.var
    xs, ys = _xy(F)
    tv = vals[0]
    x = eng.nice(caseng.subst(xs, t, tv))
    y = eng.nice(caseng.subst(ys, t, tv))
    lines = [t + ' = ' + txt(tv) + ':  x = ' + txt(caseng.subst(xs, t, tv)) + ',  y = ' + txt(caseng.subst(ys, t, tv))]
    lines.append(eng.pair(('x', 'y'), (x, y), not F.dec))
    return lines

def graph(F, arg, vals):
    import plot
    curves = []
    for r, k in zip(F.rows, F.items):
        if k == 'circle':
            a, b, r2, ls = _circle(F)
            h = ('sqrt', ('-', r2, ('^', ('-', X, a), N(2))))
            curves += [S(('+', b, h)), S(('-', b, h))]
            continue
        if r.name == 'y':
            curves.append(r.f)
            continue
        try:
            curves += eng.solve_for(r.lhs, r.rhs, 'y', [])
        except Exception:
            raise ValueError('cannot write ' + r.text + ' as y = f(x) to plot')
    plot.run(curves, -6.0, 6.0, 'y', ' ; '.join([r.text for r in F.rows]))
    return None
