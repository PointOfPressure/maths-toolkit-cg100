# pure640.py - OCR B MEI H640 Pure section for the fx-CG100 maths toolkit.
# Non-calculus pure tools: quadratics, simultaneous equations, sequences/
# series, binomial, logarithms, coordinate geometry, circles, trig.
# Calculus lives in the CAS section. Stock CASIO MicroPython 1.9.4:
# ASCII only, no f-strings, iterative only, hand-built atan2.
import math
import casui
import caslex
import caseng
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_fc = casutil.fmtc
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now
_w = casutil.w             # working: hidden when the Working setting is off
_warn = casutil.warn       # a caveat on the answer: always shown
_atan2 = casutil.atan2
_nCr = casutil.ncr

# 1. QUADRATIC SOLVER -------------------------------------------------------
def t_quadratic():
    a = _asknum('a (x^2 coeff)')
    if a is None:
        return
    b = _asknum('b (x coeff)')
    if b is None:
        return
    c = _asknum('c (constant)')
    if c is None:
        return
    if a == 0:
        if b == 0:
            _show('Quadratic', ['a = b = 0:', 'not an equation in x.'])
            return
        _show('Linear bx+c=0', [_w('b=' + _fn(b) + ' c=' + _fn(c)), 'x = ' + _fn(-c / b)])
        return
    disc = b * b - 4 * a * c
    h = -b / (2.0 * a)
    k = c - b * b / (4.0 * a)
    lines = [_w('a=' + _fn(a) + ' b=' + _fn(b)), _w('c=' + _fn(c)),
             _w('disc b^2-4ac = ' + _fn(disc))]
    if disc > 0:
        rt = math.sqrt(disc)
        lines += ['two real roots:', 'x = ' + _fn((-b + rt) / (2.0 * a)), 'x = ' + _fn((-b - rt) / (2.0 * a))]
    elif disc == 0:
        lines += ['one repeated root:', 'x = ' + _fn(h)]
    else:
        im = math.sqrt(-disc) / (2.0 * a)
        lines += ['complex conj roots:', 'x = ' + _fc(h, im), 'x = ' + _fc(h, -im)]
    lines += ['comp sq form:', _fn(a) + '(x-(' + _fn(h) + '))^2', '  +(' + _fn(k) + ')',
              'vertex (' + _fn(h) + ',' + _fn(k) + ')']
    _pages('Quadratic', lines)

# 2. SIMULTANEOUS EQUATIONS -------------------------------------------------
def _simul_linear():
    _show('Two linear eqns', ['a1 x + b1 y = c1', 'a2 x + b2 y = c2', 'enter the six values.'])
    vs = []
    for nm in ('a1', 'b1', 'c1', 'a2', 'b2', 'c2'):
        v = _asknum(nm)
        if v is None:
            return
        vs.append(v)
    a1, b1, c1, a2, b2, c2 = vs
    det = a1 * b2 - a2 * b1
    if det == 0:
        _show('Two linear eqns', [_w('a1 b2 - a2 b1 = 0'), 'no unique solution', '(parallel/same line).'])
        return
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    _show('Two linear eqns', [_w('by elimination:'), 'x = ' + _fn(x), 'y = ' + _fn(y)])

def _simul_linquad():
    _show('Linear + quadratic', ['line  y = m x + c', 'curve y = p x^2+q x+r', 'solve by substitution.'])
    vs = []
    for nm in ('m (line grad)', 'c (line interc)', 'p (x^2 coeff)', 'q (x coeff)', 'r (constant)'):
        v = _asknum(nm)
        if v is None:
            return
        vs.append(v)
    m, c, p, q, r = vs
    # p x^2 + q x + r = m x + c  ->  A x^2 + B x + C = 0
    A = p
    B = q - m
    C = r - c
    if A == 0:
        if B == 0:
            _show('Linear + quad', [_w('reduces to 0 = ' + _fn(C)), 'no/all intersections.'])
            return
        x = -C / B
        _show('Linear + quad', ['one intersection:', '(' + _fn(x) + ',' + _fn(m * x + c) + ')'])
        return
    disc = B * B - 4 * A * C
    lines = [_w('p x^2+(q-m)x+(r-c)=0'), _w('disc = ' + _fn(disc))]
    if disc < 0:
        lines += ['disc < 0: line and', 'curve do not meet.']
    elif disc == 0:
        x = -B / (2.0 * A)
        lines += ['tangent (1 point):', '(' + _fn(x) + ',' + _fn(m * x + c) + ')']
    else:
        rt = math.sqrt(disc)
        x1 = (-B + rt) / (2.0 * A)
        x2 = (-B - rt) / (2.0 * A)
        lines += ['two points:', '(' + _fn(x1) + ',' + _fn(m * x1 + c) + ')', '(' + _fn(x2) + ',' + _fn(m * x2 + c) + ')']
    _pages('Linear + quadratic', lines)

def t_simul():
    labels = ['Two linear', 'Linear + quadratic']
    while True:
        c = casui.menu('SIMULTANEOUS', labels)
        if c == -1:
            return
        if c == 0:
            _simul_linear()
        else:
            _simul_linquad()

# 3. ARITHMETIC SEQUENCE / SERIES -------------------------------------------
def t_arith():
    a = _asknum('a (first term)')
    if a is None:
        return
    d = _asknum('d (common diff)')
    if d is None:
        return
    n = _askint('n (term number)')
    if n is None or n < 1:
        _show('Arithmetic', ['need n >= 1.'])
        return
    un = a + (n - 1) * d
    sn = n / 2.0 * (2 * a + (n - 1) * d)
    _show('Arithmetic', [_w('a=' + _fn(a) + ' d=' + _fn(d)), _w('n=' + str(n)),
                         _w('Un = a+(n-1)d'), 'Un = ' + _fn(un),
                         _w('Sn = n/2(2a+(n-1)d)'), 'Sn = ' + _fn(sn)])

# 4. GEOMETRIC SEQUENCE / SERIES --------------------------------------------
def t_geo():
    a = _asknum('a (first term)')
    if a is None:
        return
    r = _asknum('r (common ratio)')
    if r is None:
        return
    n = _askint('n (term number)')
    if n is None or n < 1:
        _show('Geometric', ['need n >= 1.'])
        return
    un = a * r ** (n - 1)
    if r == 1:
        sn = a * n
    else:
        sn = a * (1 - r ** n) / (1 - r)
    lines = [_w('a=' + _fn(a) + ' r=' + _fn(r)), _w('n=' + str(n)), _w('Un = a r^(n-1)'),
             'Un = ' + _fn(un), _w('Sn = a(1-r^n)/(1-r)'), 'Sn = ' + _fn(sn)]
    if abs(r) < 1:
        lines += [_w('|r|<1: S(inf)=a/(1-r)'), 'S(inf) = ' + _fn(a / (1 - r))]
    else:
        lines.append('|r|>=1: no sum to inf')
    _pages('Geometric', lines)

# 5. BINOMIAL EXPANSION -----------------------------------------------------
def _binom_int():
    a = _asknum('a (constant)')
    if a is None:
        return
    b = _asknum('b (coeff of x)')
    if b is None:
        return
    n = _askint('n (whole >= 0)')
    if n is None or n < 0:
        _show('(a+bx)^n', ['need whole n >= 0.'])
        return
    if n > 30:
        _show('(a+bx)^n', ['n too large to list', '(use one-coeff tool).'])
        return
    lines = [_w('(a + b x)^' + str(n)), _w('a=' + _fn(a) + ' b=' + _fn(b)),
             _w('------------------')]
    r = 0
    while r <= n:
        term = _nCr(n, r) * (a ** (n - r)) * (b ** r)
        lines.append('x^' + str(r) + ': ' + _fn(term))
        r += 1
    _pages('(a+bx)^n', lines)

def _binom_real():
    n = _asknum('n (any real)')
    if n is None:
        return
    k = _askint('how many terms')
    if k is None or k < 1:
        _show('(1+x)^n', ['need >= 1 term.'])
        return
    if k > 30:
        k = 30
    lines = [_w('(1 + x)^' + _fn(n)), _warn('valid for |x| < 1'), _w('------------------')]
    coef = 1.0
    r = 0
    while r < k:
        if r == 0:
            c = 1.0
        else:
            coef = coef * (n - r + 1) / r
            c = coef
        lines.append('x^' + str(r) + ': ' + _fn(c))
        r += 1
    _pages('(1+x)^n', lines)

def _binom_coeff():
    a = _asknum('a (constant)')
    if a is None:
        return
    b = _asknum('b (coeff of x)')
    if b is None:
        return
    n = _askint('n (whole >= 0)')
    if n is None or n < 0:
        _show('Term coeff', ['need whole n >= 0.'])
        return
    k = _askint('which power k')
    if k is None:
        return
    if k < 0 or k > n:
        _show('Term coeff', [_w('k outside 0..n:'), 'coeff of x^' + str(k) + ' = 0'])
        return
    ncr = _nCr(n, k)
    coef = ncr * (a ** (n - k)) * (b ** k)
    _show('Term coeff', [_w('term in (a+bx)^' + str(n)),
                         _w('nCr(' + str(n) + ',' + str(k) + ') = ' + str(ncr)),
                         'coeff of x^' + str(k) + ':', '  ' + _fn(coef)])

def t_binom():
    labels = ['(a+bx)^n list terms', '(1+x)^n real n', 'one coeff of x^k']
    while True:
        c = casui.menu('BINOMIAL', labels)
        if c == -1:
            return
        [_binom_int, _binom_real, _binom_coeff][c]()

# 6. LOGARITHMS -------------------------------------------------------------
def _log_solve():
    a = _asknum('a (base, a>0)')
    if a is None:
        return
    b = _asknum('b (a^x = b)')
    if b is None:
        return
    if a <= 0 or a == 1 or b <= 0:
        _show('Solve a^x=b', ['need a>0, a!=1, b>0.'])
        return
    _show('Solve a^x=b', [_w('a=' + _fn(a) + '  b=' + _fn(b)), _w('x = log b / log a'),
                          'x = ' + _fn(math.log(b) / math.log(a))])

def _log_eval():
    c = _asknum('c (base, c>0)')
    if c is None:
        return
    v = _asknum('v (value, v>0)')
    if v is None:
        return
    if c <= 0 or c == 1 or v <= 0:
        _show('log base c', ['need c>0, c!=1, v>0.'])
        return
    _show('log base c of v', [_w('c=' + _fn(c) + '  v=' + _fn(v)),
                              _w('log_c v = ln v / ln c'),
                              '= ' + _fn(math.log(v) / math.log(c))])

def _log_laws():
    _pages('Log laws', ['log(xy) = log x + log y', 'log(x/y) = log x - log y',
                        'log(x^k) = k log x', 'log_a a = 1', 'log_a 1 = 0',
                        'change of base:', ' log_a x = log x / log a',
                        'a^x = e^(x ln a)', 'ln = log base e'])

def t_log():
    labels = ['Solve a^x = b', 'log base c of v', 'Log-law reference']
    while True:
        c = casui.menu('LOGARITHMS', labels)
        if c == -1:
            return
        [_log_solve, _log_eval, _log_laws][c]()

# 7. COORDINATE GEOMETRY ----------------------------------------------------
def t_coord():
    _show('Coord geometry', ['enter two points', 'P1=(x1,y1)', 'P2=(x2,y2)'])
    vs = []
    for nm in ('x1', 'y1', 'x2', 'y2'):
        v = _asknum(nm)
        if v is None:
            return
        vs.append(v)
    x1, y1, x2, y2 = vs
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    lines = ['dist = ' + _fn(dist), 'mid = (' + _fn((x1 + x2) / 2.0) + ',' + _fn((y1 + y2) / 2.0) + ')']
    if dx == 0:
        lines += ['gradient: undefined', 'line: x = ' + _fn(x1)]
    else:
        m = dy / dx
        b = y1 - m * x1
        eqn = 'line y = ' + _fn(m) + 'x'
        if b < 0:
            eqn += ' - ' + _fn(-b)      # not "x + -3"
        elif b > 0:
            eqn += ' + ' + _fn(b)
        lines += ['gradient m = ' + _fn(m), eqn]
        if m != 0:
            lines.append('perp grad = ' + _fn(-1.0 / m))
        else:
            lines.append('perp grad: undefined')
    _pages('Coord geometry', lines)

# 8. CIRCLE -----------------------------------------------------------------
def _circle_from_cr():
    a = _asknum('centre x = a')
    if a is None:
        return
    b = _asknum('centre y = b')
    if b is None:
        return
    r = _asknum('radius r (>0)')
    if r is None or r <= 0:
        _show('Circle', ['need r > 0.'])
        return
    D = -2 * a
    E = -2 * b
    F = a * a + b * b - r * r
    _pages('Centre+r -> eqn', [_w('centre (' + _fn(a) + ',' + _fn(b) + ')'), _w('radius ' + _fn(r)),
                               '(x-(' + _fn(a) + '))^2 +', '(y-(' + _fn(b) + '))^2 = ' + _fn(r * r),
                               'x^2+y^2 +(' + _fn(D) + ')x', ' +(' + _fn(E) + ')y +(' + _fn(F) + ')=0'])

def _circle_from_eqn():
    _show('Circle from eqn', ['x^2+y^2 +Dx +Ey +F = 0', 'enter D, E, F.'])
    D = _asknum('D')
    if D is None:
        return
    E = _asknum('E')
    if E is None:
        return
    F = _asknum('F')
    if F is None:
        return
    cx = -D / 2.0
    cy = -E / 2.0
    r2 = cx * cx + cy * cy - F
    if r2 < 0:
        _show('Circle from eqn', ['r^2 = ' + _fn(r2), 'negative: not a', 'real circle.'])
        return
    _show('Circle from eqn', ['centre (' + _fn(cx) + ',' + _fn(cy) + ')', _w('r^2 = ' + _fn(r2)),
                              'radius = ' + _fn(math.sqrt(r2))])

def _circle_3pts():
    # The circle through three points. Its centre is where the perpendicular
    # bisectors of two chords meet, which is the "perpendicular bisector of a
    # chord passes through the centre" property doing actual work.
    _show('Circle through 3 points', ['The centre is where the perpendicular',
                                      'bisectors of two of the chords meet.',
                                      'Enter the three points.'])
    pts = []
    for nm in ('A', 'B', 'C'):
        x = _asknum(nm + ' x')
        if x is None:
            return
        y = _asknum(nm + ' y')
        if y is None:
            return
        pts.append((x, y))
    (x1, y1), (x2, y2), (x3, y3) = pts
    # |P-A|^2 = |P-B|^2 gives a linear equation; two of them fix the centre
    a1 = 2.0 * (x2 - x1)
    b1 = 2.0 * (y2 - y1)
    c1 = x2 * x2 - x1 * x1 + y2 * y2 - y1 * y1
    a2 = 2.0 * (x3 - x1)
    b2 = 2.0 * (y3 - y1)
    c2 = x3 * x3 - x1 * x1 + y3 * y3 - y1 * y1
    det = a1 * b2 - a2 * b1
    lines = [_w('A(' + _fn(x1) + ', ' + _fn(y1) + ')  B(' + _fn(x2) + ', ' +
                _fn(y2) + ')  C(' + _fn(x3) + ', ' + _fn(y3) + ')'), '']
    if abs(det) < 1e-12:
        lines.append('The three points are COLLINEAR, so no')
        lines.append('circle passes through all of them.')
        _pages('Circle through 3 points', lines)
        return
    cx = (c1 * b2 - c2 * b1) / det
    cy = (a1 * c2 - a2 * c1) / det
    r = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
    lines.append('centre (' + _fn(cx) + ', ' + _fn(cy) + ')')
    lines.append('radius ' + _fn(r))
    lines.append('')
    lines.append('(x - ' + _fn(cx) + ')^2 + (y - ' + _fn(cy) + ')^2 = ' +
                 _fn(r * r))
    # check all three really are on it
    ok = True
    for (px, py) in pts:
        d = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        if abs(d - r) > 1e-6:
            ok = False
    lines.append('')
    lines.append(_warn('all three points on the circle: ' + ('yes' if ok else 'NO')))
    # angle in a semicircle: is any chord a diameter?
    for i in range(3):
        j = (i + 1) % 3
        k = (i + 2) % 3
        dx = pts[j][0] - pts[k][0]
        dy = pts[j][1] - pts[k][1]
        if abs(math.sqrt(dx * dx + dy * dy) - 2.0 * r) < 1e-9:
            lines.append('')
            lines.append(_w('One chord is a DIAMETER, so the angle'))
            lines.append(_w('at the third point is 90 degrees -'))
            lines.append(_w('the angle in a semicircle.'))
            break
    _pages('Circle through 3 points', lines)


def _circle_tangent():
    # Tangent at a point on a circle: perpendicular to the radius there.
    _show('Tangent to a circle', ['At a point on the circle, the tangent',
                                  'is PERPENDICULAR TO THE RADIUS.',
                                  'So its gradient is -1/(radius gradient).'])
    cx = _asknum('centre x')
    if cx is None:
        return
    cy = _asknum('centre y')
    if cy is None:
        return
    px = _asknum('point on the circle, x')
    if px is None:
        return
    py = _asknum('point y')
    if py is None:
        return
    r = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    lines = [_w('centre (' + _fn(cx) + ', ' + _fn(cy) + ')'),
             _w('point  (' + _fn(px) + ', ' + _fn(py) + ')'),
             _w('radius = ' + _fn(r)), '']
    if r < 1e-12:
        lines.append('The point IS the centre, so there is')
        lines.append('no radius and no tangent.')
        _pages('Tangent to a circle', lines)
        return
    dx = px - cx
    dy = py - cy
    if abs(dx) < 1e-12:
        lines.append('the radius is vertical, so the tangent')
        lines.append('is HORIZONTAL:  y = ' + _fn(py))
    elif abs(dy) < 1e-12:
        lines.append('the radius is horizontal, so the tangent')
        lines.append('is VERTICAL:  x = ' + _fn(px))
    else:
        mr = dy / dx
        mt = -1.0 / mr
        lines.append(_w('radius gradient  = ' + _fn(mr)))
        lines.append(_w('tangent gradient = -1/that = ' + _fn(mt)))
        lines.append('')
        lines.append('y - ' + _fn(py) + ' = ' + _fn(mt) + '(x - ' + _fn(px) + ')')
        lines.append('y = ' + _fn(mt) + 'x + ' + _fn(py - mt * px))
        lines.append('')
        lines.append(_warn('check: ' + _fn(mr) + ' x ' + _fn(mt) + ' = ' +
                           _fn(mr * mt) + ' (should be -1)'))
    _pages('Tangent to a circle', lines)


def _circle_param():
    # Parametric form of a circle, both ways.
    _show('Circle in parametric form', ['x = a + r cos t',
                                        'y = b + r sin t',
                                        'traces the circle centre (a,b)',
                                        'radius r as t goes 0 to 2pi.'])
    cx = _asknum('centre a')
    if cx is None:
        return
    cy = _asknum('centre b')
    if cy is None:
        return
    r = _asknum('radius r')
    if r is None or r <= 0:
        _show('Parametric circle', ['The radius must be positive.'])
        return
    lines = ['x = ' + _fn(cx) + ' + ' + _fn(r) + ' cos t',
             'y = ' + _fn(cy) + ' + ' + _fn(r) + ' sin t', '',
             _w('eliminating t with cos^2 + sin^2 = 1:'),
             _w('  ((x-' + _fn(cx) + ')/' + _fn(r) + ')^2 + ((y-' + _fn(cy) +
                ')/' + _fn(r) + ')^2 = 1'),
             '  (x-' + _fn(cx) + ')^2 + (y-' + _fn(cy) + ')^2 = ' + _fn(r * r),
             '', 'so it is the circle centre (' + _fn(cx) + ', ' + _fn(cy) +
             '), radius ' + _fn(r) + '.']
    t = _asknum('point at t = (radians, or cancel)')
    if t is not None:
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)
        lines.append('')
        lines.append('at t = ' + _fn(t) + ':  (' + _fn(x) + ', ' + _fn(y) + ')')
        lines.append('  dx/dt = ' + _fn(-r * math.sin(t)))
        lines.append('  dy/dt = ' + _fn(r * math.cos(t)))
        if abs(math.sin(t)) > 1e-12:
            lines.append('  dy/dx = -cot t = ' +
                         _fn(-math.cos(t) / math.sin(t)))
            lines.append(_w('  (perpendicular to the radius, as'))
            lines.append(_w('   it must be)'))
        else:
            lines.append('  dx/dt = 0 here: the tangent is vertical')
    _pages('Parametric circle', lines)


def t_proportion():
    # Proportional relationships. Finding k from one pair is a division, but
    # recognising the model and using it is the statement, and the log-log
    # gradient is how you tell y = k x^n from y = k b^x.
    _show('Proportion', ['y = k x      direct',
                         'y = k / x    inverse',
                         'y = k x^n    a power law',
                         'Give one pair (or two, for the power),',
                         'and it finds k and then predicts.'])
    kind = casui.menu('Model', ['y = k x  (direct)', 'y = k / x  (inverse)',
                                'y = k x^n  (find n too)'])
    if kind == -1:
        return
    x1 = _asknum('x1')
    if x1 is None:
        return
    y1 = _asknum('y1')
    if y1 is None:
        return
    lines = []
    if kind == 2:
        x2 = _asknum('x2')
        if x2 is None:
            return
        y2 = _asknum('y2')
        if y2 is None:
            return
        if x1 <= 0 or x2 <= 0 or y1 <= 0 or y2 <= 0:
            _show('Proportion', ['A power law needs positive values',
                                 'to take logs of.'])
            return
        if abs(math.log(x2) - math.log(x1)) < 1e-12:
            _show('Proportion', ['The two x values are the same, so n',
                                 'cannot be found.'])
            return
        n = (math.log(y2) - math.log(y1)) / (math.log(x2) - math.log(x1))
        k = y1 / (x1 ** n)
        lines = [_w('(' + _fn(x1) + ', ' + _fn(y1) + ') and (' + _fn(x2) + ', ' +
                    _fn(y2) + ')'), '',
                 _w('y = k x^n, so log y = log k + n log x:'),
                 _w('  n = (log y2 - log y1)/(log x2 - log x1)'),
                 _w('    = ' + _fn(n, 6)),
                 _w('  k = y1 / x1^n = ' + _fn(k, 6)), '',
                 'y = ' + _fn(k, 6) + ' x^' + _fn(n, 6)]
    elif kind == 0:
        if abs(x1) < 1e-12:
            _show('Proportion', ['x = 0 gives no information about k.'])
            return
        k = y1 / x1
        lines = [_w('y = k x with (' + _fn(x1) + ', ' + _fn(y1) + ')'),
                 _w('  k = y/x = ' + _fn(k, 6)), '',
                 'y = ' + _fn(k, 6) + ' x', '',
                 _w('doubling x doubles y; the graph is a'),
                 _w('straight line through the origin.')]
    else:
        k = y1 * x1
        lines = [_w('y = k/x with (' + _fn(x1) + ', ' + _fn(y1) + ')'),
                 _w('  k = xy = ' + _fn(k, 6)), '',
                 'y = ' + _fn(k, 6) + ' / x', '',
                 _w('doubling x halves y; xy is constant,'),
                 _w('and the graph is a hyperbola.')]
    xq = _asknum('predict y when x = (or cancel)')
    if xq is not None:
        try:
            if kind == 0:
                yq = k * xq
            elif kind == 1:
                yq = k / xq
            else:
                yq = k * (xq ** n)
        except:
            yq = None
        lines.append('')
        if yq is None:
            lines.append('undefined at x = ' + _fn(xq))
        else:
            lines.append('at x = ' + _fn(xq) + ':  y = ' + _fn(yq, 6))
    yq = _asknum('and x when y = (or cancel)')
    if yq is not None:
        try:
            if kind == 0:
                xr = yq / k
            elif kind == 1:
                xr = k / yq
            else:
                xr = (yq / k) ** (1.0 / n)
        except:
            xr = None
        lines.append('')
        if xr is None:
            lines.append('undefined at y = ' + _fn(yq))
        else:
            lines.append('at y = ' + _fn(yq) + ':  x = ' + _fn(xr, 6))
    _pages('Proportion', lines)


def t_circle():
    labels = ['Centre+r -> equation', 'Equation -> centre+r',
              'Circle through 3 points', 'Tangent at a point',
              'Parametric form']
    while True:
        c = casui.menu('CIRCLE', labels)
        if c == -1:
            return
        if c == 2:
            _circle_3pts()
        elif c == 3:
            _circle_tangent()
        elif c == 4:
            _circle_param()
        elif c == 0:
            _circle_from_cr()
        else:
            _circle_from_eqn()

# 9. TRIG -------------------------------------------------------------------
def _trig_solve():
    labels = ['sin x = k', 'cos x = k', 'tan x = k']
    f = casui.menu('Solve over 0..360', labels)
    if f == -1:
        return
    k = _asknum('k')
    if k is None:
        return
    try:
        if f == 0:
            base = casutil.deg(math.asin(k))
            cand = [base, 180 - base]
        elif f == 1:
            base = casutil.deg(math.acos(k))
            cand = [base, -base]
        else:
            base = casutil.deg(math.atan(k))
            cand = [base, base + 180, base - 180]
    except:
        _show('Solve trig', ['no solution:', '|k| > 1 for sin/cos.'])
        return
    sols = []
    for cv in cand:
        x = cv
        while x < -1e-9:
            x += 360
        while x >= 360 - 1e-9:
            x -= 360
        x = round(x, 4)
        if x < 0:
            x = 0.0
        if x not in sols:
            sols.append(x)
    sols.sort()
    lines = [_w('k = ' + _fn(k)), _w('range 0..360 deg'), _w('------------------')]
    if not sols:
        lines.append('no solutions in range.')
    else:
        for x in sols:
            lines.append('x = ' + _fn(x) + ' deg')
    _pages('Solve trig', lines)

def _trig_rform():
    _show('R-form', ['a sin x + b cos x', '= R sin(x + alpha)', 'enter a and b.'])
    a = _asknum('a (sin coeff)')
    if a is None:
        return
    b = _asknum('b (cos coeff)')
    if b is None:
        return
    R = math.sqrt(a * a + b * b)
    # R sin(x+alpha)=R sin x cos al + R cos x sin al; match a=R cos al, b=R sin al
    alpha = casutil.deg(_atan2(b, a))
    _pages('R-form', [_w('a=' + _fn(a) + '  b=' + _fn(b)), _w('R = sqrt(a^2+b^2)'),
                      'R = ' + _fn(R), '= R sin(x + alpha)', _w('tan alpha = b/a'),
                      'alpha = ' + _fn(alpha) + ' deg',
                      '(rad = ' + _fn(casutil.rad(alpha)) + ')'])

def _trig_exact():
    _pages('Exact values', ['deg | sin   cos   tan', '0   | 0     1     0', '30  |1/2   r3/2  1/r3',
                            '45  |1/r2  1/r2   1', '60  |r3/2  1/2    r3', '90  | 1     0    undef',
                            '(r = square root)', 'r2 ~ 1.41421', 'r3 ~ 1.73205'])

def _trig_roots(f, k, lo, hi, full):
    # every x in [lo, hi] with sin/cos/tan(x) = k, in the unit implied by
    # `full` (360 for degrees, 2pi for radians). Shared by the plain solver and
    # the identity-based one so they cannot disagree about the second solution.
    try:
        if f == 0:
            base = math.asin(k)
        elif f == 1:
            base = math.acos(k)
        else:
            base = math.atan(k)
    except:
        return None
    if full > 100.0:
        base = casutil.deg(base)
    if f == 0:
        partners = [base, full / 2.0 - base]
        period = full
    elif f == 1:
        partners = [base, -base]
        period = full
    else:
        partners = [base]
        period = full / 2.0
    sols = []
    for a0 in partners:
        n = -400
        while n <= 400:
            x = a0 + n * period
            if lo - 1e-9 <= x <= hi + 1e-9:
                r = round(x, 6)
                dup = False
                for e in sols:
                    if abs(e - r) < 1e-6:
                        dup = True
                        break
                if not dup:
                    sols.append(r)
            n += 1
    sols.sort()
    return sols


_IDFORMS = [
    ('a sin^2 x + b sin x + c = 0', 0, None),
    ('a cos^2 x + b cos x + c = 0', 1, None),
    ('a tan^2 x + b tan x + c = 0', 2, None),
    ('a sin^2 x + b cos x + c = 0', 1, 'sin2'),
    ('a cos^2 x + b sin x + c = 0', 0, 'cos2'),
    ('a sec^2 x + b tan x + c = 0', 2, 'sec2'),
]


def _trig_identity():
    # Equations that need an identity BEFORE they become a quadratic. This is
    # the technique H640 t19 is about, and the plain solver cannot touch them:
    # it only handles sin x = k.
    _show('Trig equations by identity', [
        'These become quadratics once you use',
        '  sin^2 x = 1 - cos^2 x',
        '  cos^2 x = 1 - sin^2 x',
        '  sec^2 x = 1 + tan^2 x',
        'Pick the shape of your equation.'])
    labels = []
    for name, f, ident in _IDFORMS:
        labels.append(name)
    pick = casui.menu('Which form', labels)
    if pick == -1:
        return
    name, f, ident = _IDFORMS[pick]
    unit = casui.menu('Angle unit', ['degrees', 'radians'])
    if unit == -1:
        return
    full = 360.0 if unit == 0 else 2.0 * math.pi
    unm = 'deg' if unit == 0 else 'rad'
    a = _asknum('a')
    if a is None:
        return
    b = _asknum('b')
    if b is None:
        return
    c = _asknum('c')
    if c is None:
        return
    lo = _asknum('from x = [0]')
    if lo is None:
        lo = 0.0
    hi = _asknum('to x = [' + _fn(full) + ']')
    if hi is None:
        hi = full
    if hi < lo:
        lo, hi = hi, lo
    # build the heading from the coefficients rather than patching the template
    # string, which produced "+ + 1 sin x"
    parts = name.split(' ')
    sq = parts[1]                      # "sin^2" / "cos^2" / "tan^2" / "sec^2"
    lin = parts[5]                     # "sin" / "cos" / "tan"
    lines = [_w(_lead(a, sq + ' x') + ' ' + _signed(b, lin + ' x') + ' ' +
                _signed(c) + ' = 0'),
             _w('for ' + _fn(lo) + ' <= x <= ' + _fn(hi) + ' ' + unm), '']
    # apply the identity to get a quadratic in ONE function
    A = a
    B = b
    C = c
    fname = ('sin', 'cos', 'tan')[f]
    if ident == 'sin2':
        # a(1 - cos^2) + b cos + c = 0  ->  -a cos^2 + b cos + (a + c) = 0
        lines.append(_w('use sin^2 x = 1 - cos^2 x:'))
        A = -a
        C = a + c
    elif ident == 'cos2':
        lines.append(_w('use cos^2 x = 1 - sin^2 x:'))
        A = -a
        C = a + c
    elif ident == 'sec2':
        # a(1 + tan^2) + b tan + c = 0  ->  a tan^2 + b tan + (a + c) = 0
        lines.append(_w('use sec^2 x = 1 + tan^2 x:'))
        C = a + c
    lines.append(_w('  ' + _lead(A, fname + '^2 x') + ' ' +
                    _signed(B, fname + ' x') + ' ' + _signed(C) + ' = 0'))
    lines.append('')
    lines.append(_w('let u = ' + fname + ' x:'))
    lines.append(_w('  ' + _lead(A, 'u^2') + ' ' + _signed(B, 'u') + ' ' +
                    _signed(C) + ' = 0'))
    roots = []
    if abs(A) < 1e-12:
        if abs(B) < 1e-12:
            lines.append('')
            lines.append('a and b are both 0, so this is not an')
            lines.append('equation in x.')
            _pages('Trig by identity', lines)
            return
        roots = [-C / B]
        lines.append(_w('  (linear) u = ' + _fn(roots[0])))
    else:
        disc = B * B - 4.0 * A * C
        lines.append(_w('  discriminant = ' + _fn(disc)))
        if disc < -1e-12:
            lines.append('')
            lines.append('Negative, so there is no real u and')
            lines.append('therefore NO SOLUTION for x.')
            _pages('Trig by identity', lines)
            return
        if disc < 0:
            disc = 0.0
        rt = math.sqrt(disc)
        roots = [(-B + rt) / (2.0 * A)]
        if rt > 1e-12:
            roots.append((-B - rt) / (2.0 * A))
    lines.append('')
    allsols = []
    for u in roots:
        lines.append(_w(fname + ' x = ' + _fn(u)))
        if f != 2 and (u > 1.0 + 1e-12 or u < -1.0 - 1e-12):
            lines.append(_warn('  |' + fname + ' x| cannot exceed 1, so this'))
            lines.append(_warn('  root gives no solutions - discard it.'))
            continue
        uu = u
        if f != 2:
            if uu > 1.0:
                uu = 1.0
            if uu < -1.0:
                uu = -1.0
        sols = _trig_roots(f, uu, lo, hi, full)
        if not sols:
            lines.append(_w('  no x in the interval'))
            continue
        for x in sols:
            lines.append(_w('  x = ' + _fn(x) + ' ' + unm))
            dup = False
            for e in allsols:
                if abs(e - x) < 1e-6:
                    dup = True
                    break
            if not dup:
                allsols.append(x)
    allsols.sort()
    lines.append('')
    if allsols:
        lines.append('ALL SOLUTIONS in order:')
        row = ''
        for x in allsols:
            piece = _fn(x)
            if len(row) + len(piece) > 30:
                lines.append('  ' + row)
                row = ''
            row = (row + ', ' + piece) if row else piece
        if row:
            lines.append('  ' + row)
        lines.append('(' + str(len(allsols)) + ' solutions)')
        # independent check: substitute each back into the ORIGINAL equation
        bad = 0
        for x in allsols:
            r = x if unit == 1 else casutil.rad(x)
            sv = math.sin(r)
            cv = math.cos(r)
            if f == 2 and abs(cv) < 1e-9:
                continue
            tv = sv / cv if abs(cv) > 1e-12 else 0.0
            if ident == 'sin2':
                val = a * sv * sv + b * cv + c
            elif ident == 'cos2':
                val = a * cv * cv + b * sv + c
            elif ident == 'sec2':
                val = a / (cv * cv) + b * tv + c
            elif f == 0:
                val = a * sv * sv + b * sv + c
            elif f == 1:
                val = a * cv * cv + b * cv + c
            else:
                val = a * tv * tv + b * tv + c
            if abs(val) > 1e-6:
                bad += 1
        lines.append(_warn('checked back in the original: ' +
                           ('all satisfy it' if bad == 0 else str(bad) + ' DO NOT')))
    else:
        lines.append('No solutions in that interval.')
    _pages('Trig by identity', lines)


def _trig_general():
    # The bare solver above is locked to 0..360 degrees and to sin x = k. This
    # one takes any interval, either angle unit, and a multiple angle, which is
    # what the equations on the paper actually look like: sin(2x - 30) = 0.5
    # over 0 <= x <= 360 has four solutions and the naive route finds one.
    labels = ['sin(px + q) = k', 'cos(px + q) = k', 'tan(px + q) = k']
    f = casui.menu('Solve trig equation', labels)
    if f == -1:
        return
    unit = casui.menu('Angle unit', ['degrees', 'radians'])
    if unit == -1:
        return
    full = 360.0 if unit == 0 else 2.0 * math.pi
    p = _asknum('p (coeff of x) [1]')
    if p is None:
        p = 1.0
    if p == 0:
        _show('Solve trig', ['p = 0 leaves no x to solve for.'])
        return
    q = _asknum('q (inside constant) [0]')
    if q is None:
        q = 0.0
    k = _asknum('k (right-hand side)')
    if k is None:
        return
    lo = _asknum('from x = [0]')
    if lo is None:
        lo = 0.0
    hi = _asknum('to x = [' + _fn(full) + ']')
    if hi is None:
        hi = full
    if hi < lo:
        lo, hi = hi, lo
    # principal value, in the chosen unit
    try:
        if f == 0:
            base = math.asin(k)
        elif f == 1:
            base = math.acos(k)
        else:
            base = math.atan(k)
    except:
        _show('Solve trig', ['No solution: |k| must be at most 1',
                             'for sin and cos.'])
        return
    if unit == 0:
        base = casutil.deg(base)
    # every angle A with the required value, as base + n*period or its partner
    if f == 0:
        partners = [base, full / 2.0 - base]
        period = full
    elif f == 1:
        partners = [base, -base]
        period = full
    else:
        partners = [base]
        period = full / 2.0
    sols = []
    for a0 in partners:
        # A = p x + q, so x = (A - q)/p; step A by the period both ways
        n = -400
        while n <= 400:
            A = a0 + n * period
            x = (A - q) / p
            if lo - 1e-9 <= x <= hi + 1e-9:
                r = round(x, 6)
                dup = False
                for e in sols:
                    if abs(e - r) < 1e-6:
                        dup = True
                if not dup:
                    sols.append(r)
            n += 1
    sols.sort()
    nm = ('sin', 'cos', 'tan')[f]
    unm = 'deg' if unit == 0 else 'rad'
    lines = [_w(nm + '(' + _fn(p) + 'x + ' + _fn(q) + ') = ' + _fn(k)),
             _w('for ' + _fn(lo) + ' <= x <= ' + _fn(hi) + ' ' + unm),
             _w('principal value ' + _fn(base) + ' ' + unm),
             _w('period in x is ' + _fn(period / (p if p > 0 else -p)) + ' ' + unm),
             _w('------------------')]
    if not sols:
        lines.append('no solutions in that interval.')
    else:
        for x in sols:
            lines.append('x = ' + _fn(x) + ' ' + unm)
        lines.append('')
        lines.append(str(len(sols)) + ' solutions.')
        lines.append(_w('A multiple angle gives p times as many'))
        lines.append(_w('as the plain equation would.'))
    _pages('Solve trig', lines)


def _trig_compound():
    _pages('Compound and double angles', [
        'COMPOUND ANGLES',
        ' sin(A+B) = sinA cosB + cosA sinB',
        ' sin(A-B) = sinA cosB - cosA sinB',
        ' cos(A+B) = cosA cosB - sinA sinB',
        ' cos(A-B) = cosA cosB + sinA sinB',
        ' tan(A+B) = (tanA+tanB)/(1-tanA tanB)',
        ' tan(A-B) = (tanA-tanB)/(1+tanA tanB)',
        '',
        'DOUBLE ANGLES (put B = A)',
        ' sin2A = 2 sinA cosA',
        ' cos2A = cos^2 A - sin^2 A',
        '       = 2cos^2 A - 1',
        '       = 1 - 2sin^2 A',
        ' tan2A = 2tanA / (1 - tan^2 A)',
        '',
        'REARRANGED, for integrating',
        ' sin^2 A = (1 - cos2A)/2',
        ' cos^2 A = (1 + cos2A)/2',
        '',
        'HALF ANGLE t = tan(A/2)',
        ' sinA = 2t/(1+t^2)',
        ' cosA = (1-t^2)/(1+t^2)',
        ' tanA = 2t/(1-t^2)',
        '',
        'PYTHAGOREAN',
        ' sin^2 + cos^2 = 1',
        ' 1 + tan^2 = sec^2',
        ' 1 + cot^2 = cosec^2',
        '',
        'SUM TO PRODUCT',
        ' sinP + sinQ = 2 sin((P+Q)/2) cos((P-Q)/2)',
        ' cosP + cosQ = 2 cos((P+Q)/2) cos((P-Q)/2)',
        ' cosP - cosQ = -2 sin((P+Q)/2) sin((P-Q)/2)',
    ])


def _trig_expand():
    # Evaluate a compound-angle expansion numerically, both ways, so the
    # identity can be checked rather than taken on trust.
    _show('Check an expansion', ['Enter A and B in degrees.',
                                 'Both sides of each identity are',
                                 'worked out separately and compared.'])
    A = _asknum('A (deg)')
    if A is None:
        return
    B = _asknum('B (deg)')
    if B is None:
        return
    ra = casutil.rad(A)
    rb = casutil.rad(B)
    sa = math.sin(ra)
    ca = math.cos(ra)
    sb = math.sin(rb)
    cb = math.cos(rb)
    rows = [('sin(A+B)', math.sin(ra + rb), sa * cb + ca * sb),
            ('sin(A-B)', math.sin(ra - rb), sa * cb - ca * sb),
            ('cos(A+B)', math.cos(ra + rb), ca * cb - sa * sb),
            ('cos(A-B)', math.cos(ra - rb), ca * cb + sa * sb),
            ('sin(2A)', math.sin(2 * ra), 2 * sa * ca),
            ('cos(2A)', math.cos(2 * ra), ca * ca - sa * sa)]
    lines = [_w('A = ' + _fn(A) + ' deg, B = ' + _fn(B) + ' deg'), '']
    for nm, direct, expanded in rows:
        lines.append(nm + ' = ' + _fn(direct, 6))
        lines.append(_warn('  expansion  ' + _fn(expanded, 6) +
                           ('  agrees' if abs(direct - expanded) < 1e-9 else '  DIFFERS')))
    if abs(ca * cb) > 1e-12 and abs(1.0 - (sa / ca) * (sb / cb)) > 1e-12:
        ta = sa / ca
        tb = sb / cb
        lines.append('tan(A+B) = ' + _fn(math.tan(ra + rb), 6))
        lines.append(_warn('  expansion  ' + _fn((ta + tb) / (1.0 - ta * tb), 6)))
    _pages('Compound angles', lines)


def t_trig():
    labels = ['Solve sin/cos/tan (0-360)', 'Solve p x + q, any range',
              'Solve using an identity', 'R-form a sin+b cos',
              'Compound/double angles', 'Check an expansion',
              'Exact-value table']
    while True:
        c = casui.menu('TRIG', labels)
        if c == -1:
            return
        [_trig_solve, _trig_general, _trig_identity, _trig_rform,
         _trig_compound, _trig_expand, _trig_exact][c]()


def t_triangle():
    # Sine rule and cosine rule. The audit put this first on the whole missing
    # list: it appears in essentially every H640 pure paper and there was no
    # route to it at all. Angles in degrees; sides a, b, c face angles A, B, C.
    labels = ['SSS - three sides', 'SAS - two sides + included angle',
              'ASA - two angles + a side', 'SSA - two sides + non-included angle']
    c = casui.menu('Solve a triangle', labels)
    if c == -1:
        return
    A = None
    B = None
    C = None
    a = None
    b = None
    cc = None
    warn = None
    if c == 0:
        a = _asknum('side a')
        b = _asknum('side b')
        cc = _asknum('side c')
        if a is None or b is None or cc is None:
            return
        if a <= 0 or b <= 0 or cc <= 0:
            _show('Triangle', ['Sides must be positive.'])
            return
        if a + b <= cc or a + cc <= b or b + cc <= a:
            _show('Triangle', ['These three lengths cannot form',
                               'a triangle: the two shorter ones',
                               'must add to more than the longest.'])
            return
        A = casutil.deg(casutil.acos_safe((b * b + cc * cc - a * a) / (2.0 * b * cc)))
        B = casutil.deg(casutil.acos_safe((a * a + cc * cc - b * b) / (2.0 * a * cc)))
        C = 180.0 - A - B
    elif c == 1:
        b = _asknum('side b')
        cc = _asknum('side c')
        A = _asknum('included angle A (deg)')
        if b is None or cc is None or A is None:
            return
        if b <= 0 or cc <= 0 or A <= 0 or A >= 180:
            _show('Triangle', ['Need positive sides and',
                               '0 < A < 180.'])
            return
        a = math.sqrt(b * b + cc * cc - 2.0 * b * cc * math.cos(casutil.rad(A)))
        B = casutil.deg(casutil.acos_safe((a * a + cc * cc - b * b) / (2.0 * a * cc)))
        C = 180.0 - A - B
    elif c == 2:
        A = _asknum('angle A (deg)')
        B = _asknum('angle B (deg)')
        a = _asknum('side a (opposite A)')
        if A is None or B is None or a is None:
            return
        if A <= 0 or B <= 0 or A + B >= 180 or a <= 0:
            _show('Triangle', ['Need A > 0, B > 0, A + B < 180',
                               'and a positive side.'])
            return
        C = 180.0 - A - B
        k = a / math.sin(casutil.rad(A))
        b = k * math.sin(casutil.rad(B))
        cc = k * math.sin(casutil.rad(C))
    else:
        a = _asknum('side a')
        b = _asknum('side b')
        A = _asknum('angle A (deg), opposite a')
        if a is None or b is None or A is None:
            return
        if a <= 0 or b <= 0 or A <= 0 or A >= 180:
            _show('Triangle', ['Need positive sides and 0 < A < 180.'])
            return
        s = b * math.sin(casutil.rad(A)) / a
        if s > 1.0 + 1e-12:
            _show('Triangle', ['No triangle: sin B would have to',
                               'be ' + _fn(s) + ', which is more than 1.'])
            return
        if s > 1.0:
            s = 1.0
        B = casutil.deg(math.asin(s))
        # the ambiguous case: 180 - B may also work
        B2 = 180.0 - B
        if a < b and A + B2 < 180.0 and abs(B2 - B) > 1e-9:
            warn = B2
        C = 180.0 - A - B
        cc = a * math.sin(casutil.rad(C)) / math.sin(casutil.rad(A))
    area = 0.5 * a * b * math.sin(casutil.rad(C))
    lines = ['a = ' + _fn(a) + '   A = ' + _fn(A) + ' deg',
             'b = ' + _fn(b) + '   B = ' + _fn(B) + ' deg',
             'c = ' + _fn(cc) + '   C = ' + _fn(C) + ' deg',
             '',
             'area = (1/2)ab sinC = ' + _fn(area),
             'perimeter = ' + _fn(a + b + cc)]
    if c == 0 or c == 1:
        lines.append('')
        lines.append(_w('cosine rule: a^2 = b^2 + c^2 - 2bc cosA'))
    else:
        lines.append('')
        lines.append(_w('sine rule: a/sinA = b/sinB = c/sinC'))
        lines.append(_w('  common ratio = ' + _fn(a / math.sin(casutil.rad(A)))))
    if warn is not None:
        C2 = 180.0 - A - warn
        c2 = a * math.sin(casutil.rad(C2)) / math.sin(casutil.rad(A))
        lines.append('')
        lines.append(_warn('AMBIGUOUS CASE: a < b, so there is'))
        lines.append(_warn('a second triangle -'))
        lines.append(_warn('  B = ' + _fn(warn) + ' deg'))
        lines.append(_warn('  C = ' + _fn(C2) + ' deg'))
        lines.append(_warn('  c = ' + _fn(c2)))
        lines.append(_warn('Check the question for which one'))
        lines.append(_warn('is wanted.'))
    _pages('Triangle', lines)


def t_arc_sector():
    # Arc length and sector area. r theta and (1/2) r^2 theta need theta in
    # RADIANS; the degree versions carry the pi/180. Mixing them up is the
    # standard way to lose these marks.
    _show('Arc and sector', ['For a sector of radius r and angle',
                             'theta: arc = r theta and',
                             'area = (1/2) r^2 theta,',
                             'with theta IN RADIANS.'])
    r = _asknum('radius r')
    if r is None or r <= 0:
        return
    unit = casui.menu('Angle given in', ['radians', 'degrees'])
    if unit == -1:
        return
    th = _asknum('angle theta')
    if th is None:
        return
    rad = th if unit == 0 else casutil.rad(th)
    degs = casutil.deg(rad) if unit == 0 else th
    arc = r * rad
    area = 0.5 * r * r * rad
    chord = 2.0 * r * math.sin(rad / 2.0)
    seg_area = 0.5 * r * r * (rad - math.sin(rad))
    lines = [_w('r = ' + _fn(r)),
             _w('theta = ' + _fn(rad) + ' rad = ' + _fn(degs) + ' deg'),
             '',
             'arc length  = r theta      = ' + _fn(arc),
             'sector area = (1/2)r^2 th  = ' + _fn(area),
             '',
             'chord       = 2r sin(th/2) = ' + _fn(chord),
             'segment area = (1/2)r^2(th - sin th)',
             '             = ' + _fn(seg_area),
             '',
             'perimeter of the sector',
             '  = arc + 2r = ' + _fn(arc + 2.0 * r)]
    if unit == 1:
        lines.append('')
        lines.append(_w('(the degrees were converted first -'))
        lines.append(_w(' r theta only works in radians)'))
    _pages('Arc and sector', lines)


def t_inequality():
    # Linear and quadratic inequalities. The quadratic case is where the marks
    # go: the solution set is between the roots or outside them depending on
    # the sign of a and the direction, and getting that backwards is the
    # standard error.
    kind = casui.menu('Inequality', ['linear  ax + b  ? 0', 'quadratic ax^2+bx+c ? 0'])
    if kind == -1:
        return
    rel = casui.menu('Direction', ['> 0', '>= 0', '< 0', '<= 0'])
    if rel == -1:
        return
    sym = ('>', '>=', '<', '<=')[rel]
    strict = (rel == 0 or rel == 2)
    want_pos = (rel <= 1)
    a = _asknum('a')
    if a is None:
        return
    b = _asknum('b')
    if b is None:
        return
    if kind == 0:
        lines = [_w(_fn(a) + 'x + ' + _fn(b) + ' ' + sym + ' 0')]
        if a == 0:
            ok = (b > 0) if want_pos and strict else ((b >= 0) if want_pos else
                                                      ((b < 0) if strict else (b <= 0)))
            lines.append('a = 0, so this says ' + _fn(b) + ' ' + sym + ' 0,')
            lines.append('which is ' + ('true for every x.' if ok else 'never true.'))
            _pages('Inequality', lines)
            return
        root = -b / a
        # dividing by a negative flips the inequality - the classic slip
        flip = a < 0
        eff = sym
        if flip:
            eff = ('<', '<=', '>', '>=')[rel]
            lines.append(_w('a < 0, so dividing by a FLIPS the sign'))
        lines.append('x ' + eff + ' ' + _fn(root))
        _pages('Inequality', lines)
        return
    c = _asknum('c')
    if c is None:
        return
    lines = [_w(_fn(a) + 'x^2 + ' + _fn(b) + 'x + ' + _fn(c) + ' ' + sym + ' 0')]
    if a == 0:
        lines.append('a = 0: this is linear, not quadratic.')
        _pages('Inequality', lines)
        return
    disc = b * b - 4.0 * a * c
    lines.append(_w('discriminant = ' + _fn(disc)))
    lo = None
    hi = None
    if disc > 0:
        rt = math.sqrt(disc)
        lo = (-b - rt) / (2.0 * a)
        hi = (-b + rt) / (2.0 * a)
        if lo > hi:
            lo, hi = hi, lo
        lines.append(_w('roots ' + _fn(lo) + ' and ' + _fn(hi)))
    elif abs(disc) < 1e-12:
        lo = -b / (2.0 * a)
        hi = lo
        lines.append(_w('one repeated root ' + _fn(lo)))
    else:
        lines.append(_w('no real roots: the curve never'))
        lines.append(_w('crosses the axis.'))
    up = a > 0
    lines.append(_w('the parabola opens ' + ('upwards' if up else 'downwards')))
    lines.append('')
    inside_is_neg = up          # between the roots, an upward parabola is < 0
    if lo is None:
        always = (up == want_pos)
        lines.append('so it is ' + ('always' if always else 'never') +
                     ' ' + sym + ' 0:')
        lines.append('  ' + ('every real x' if always else 'no solutions'))
    elif abs(hi - lo) < 1e-12:
        lines.append(_w('the curve touches the axis at ' + _fn(lo) + '.'))
        if want_pos == up:
            lines.append('  every x' + ('' if strict else '') +
                         (' except x = ' + _fn(lo) if strict else ''))
        else:
            lines.append('  x = ' + _fn(lo) if not strict else '  no solutions')
    else:
        between = (want_pos != inside_is_neg)
        oc = '<=' if not strict else '<'
        if between:
            lines.append('  ' + _fn(lo) + ' ' + oc + ' x ' + oc + ' ' + _fn(hi))
            lines.append(_w('  (between the roots)'))
        else:
            gt = '>=' if not strict else '>'
            lt = '<=' if not strict else '<'
            lines.append('  x ' + lt + ' ' + _fn(lo) + '  or  x ' + gt + ' ' + _fn(hi))
            lines.append(_w('  (outside the roots)'))
    lines.append('')
    lines.append('The sketch follows: the curve, and the')
    lines.append('part of the x-axis that satisfies it.')
    _pages('Inequality', lines)
    _draw_quad_region(a, b, c, lo, hi, rel, strict, want_pos, up)


def _draw_quad_region(a, b, c, lo, hi, rel, strict, want_pos, up):
    # Draw y = ax^2+bx+c with the solution set marked ON THE X-AXIS. Sketching
    # it and shading is the check the specification asks for, and it is the one
    # that survives getting the inequality direction backwards.
    if lo is None:
        centre = -b / (2.0 * a)
        xa = centre - 5.0
        xb = centre + 5.0
    else:
        pad = 2.0 + (hi - lo)
        xa = lo - pad
        xb = hi + pad
    ys = []
    n = 200
    i = 0
    while i <= n:
        xv = xa + (xb - xa) * i / float(n)
        ys.append(a * xv * xv + b * xv + c)
        i += 1
    ylo, yhi = casutil.nice_range(ys, 0.12, True)
    fr = casutil.frame(xa, xb, ylo, yhi)
    sym = ('>', '>=', '<', '<=')[rel]
    casutil.axes(fr, 'y = ' + _fn(a) + 'x^2 ' + _signed(b) + 'x ' + _signed(c) +
                 '   solve ' + sym + ' 0', 'x', 'y')
    # the curve
    prev = None
    i = 0
    while i <= n:
        xv = xa + (xb - xa) * i / float(n)
        yv = ys[i]
        if prev is not None:
            casutil.seg(fr, prev[0], prev[1], xv, yv, casui.ACC)
        prev = (xv, yv)
        i += 1
    # the solution set, as a thick band along y = 0
    band = (yhi - ylo) * 0.012
    i = 0
    while i <= n:
        xv = xa + (xb - xa) * i / float(n)
        yv = ys[i]
        ok = (yv > 0) if (rel == 0) else ((yv >= 0) if rel == 1 else
                                          ((yv < 0) if rel == 2 else (yv <= 0)))
        if ok:
            casutil.seg(fr, xv, -band, xv, band, casui.RED)
        i += 1
    if lo is not None:
        casutil.marker(fr, lo, 0.0, casui.BLACK, 2)
        casutil.marker(fr, hi, 0.0, casui.BLACK, 2)
    note = 'red = solution set'
    if lo is None:
        note += ' (no real roots)'
    elif abs(hi - lo) < 1e-12:
        note += '   repeated root ' + _fn(lo)
    else:
        note += '   roots ' + _fn(lo) + ', ' + _fn(hi)
    casutil.chart_hold(note)


def _signed(v, body=''):
    # "+ 3x" / "- 3x" / "+ x", so nothing prints "+ -24" or "+ 1x"
    m = -v if v < 0 else v
    sgn = '- ' if v < 0 else '+ '
    if body and abs(m - 1.0) < 1e-12:
        return sgn + body
    return sgn + _fn(m) + body


def _lead(v, body):
    # the first term of an expression: "3x", "-x", "x"
    if abs(v - 1.0) < 1e-12:
        return body
    if abs(v + 1.0) < 1e-12:
        return '-' + body
    return _fn(v) + body


def _sqsplit(v):
    # v = a*a*b with b square-free
    a = 1
    b = int(v)
    d = 2
    while d * d <= b:
        while b % (d * d) == 0:
            b //= d * d
            a *= d
        d += 1 if d == 2 else 2
    return (a, b)


def _surdstr(a, b):
    # a*sqrt(b) written the way it goes on paper
    if b == 1:
        return _fn(a)
    if a == 1:
        return 'sqrt(' + str(b) + ')'
    if a == -1:
        return '-sqrt(' + str(b) + ')'
    return _fn(a) + 'sqrt(' + str(b) + ')'


def _br(v):
    # bracket a negative so "-1^2" cannot be read as -(1^2)
    s = _fn(v)
    return ('(' + s + ')') if s[:1] == '-' else s


def _pmsurd(b, n):
    # ' + b sqrt(n)', or ' - |b| sqrt(n)' when b is negative. The sign belongs
    # to the operator, not to the term: joining with a bare ' + ' or ' - ' and
    # letting _surdstr carry the minus prints '1 - -sqrt(2)', which is right
    # but is not how anyone writes it down.
    if b < 0:
        return ' - ' + _surdstr(-b, n)
    return ' + ' + _surdstr(b, n)


def _sumstr(a, b, n):
    # a + b sqrt(n) in exact form, with the degenerate terms dropped
    if abs(b) < 1e-12:
        return _fn(a)
    if abs(a) < 1e-12:
        return _surdstr(b, n)
    return _fn(a) + _pmsurd(b, n)


def t_surds():
    # Manipulating surds, and rationalising a denominator. These are exact-form
    # marks, and the CAS holds numbers as floats with exact folding only for
    # integers and fractions, so sqrt(8) reaching 2 sqrt(2) needs its own route.
    what = casui.menu('Surds', ['Simplify sqrt(n)',
                                'a sqrt(m) +/- b sqrt(n)',
                                'Multiply two surds',
                                'Rationalise  k/(p + q sqrt(n))'])
    if what == -1:
        return
    if what == 0:
        n = _askint('n in sqrt(n)', 0, 10 ** 12)
        if n is None:
            return
        a, b = _sqsplit(n)
        lines = [_w('sqrt(' + str(n) + ')')]
        if b == 1:
            lines.append('  = ' + str(a) + '   (a perfect square)')
        elif a == 1:
            lines.append('  sqrt(' + str(n) + ') is already in simplest form')
            lines.append(_w('  (' + str(n) + ' has no square factor)'))
        else:
            lines.append(_w('  = sqrt(' + str(a * a) + ' x ' + str(b) + ')'))
            lines.append('  = ' + str(a) + 'sqrt(' + str(b) + ')')
        lines.append('')
        lines.append(_w('decimal check: ' + _fn(math.sqrt(n), 6)))
        _pages('Surds', lines)
        return
    if what == 1:
        a = _asknum('a (coeff of the first surd)')
        if a is None:
            return
        m = _askint('m in sqrt(m)', 0, 10 ** 12)
        if m is None:
            return
        b = _asknum('b (coeff of the second)')
        if b is None:
            return
        n = _askint('n in sqrt(n)', 0, 10 ** 12)
        if n is None:
            return
        pa, ra = _sqsplit(m)
        pb, rb = _sqsplit(n)
        lines = [_w(_surdstr(a, m) + _pmsurd(b, n)), '',
                 _w('simplify each first:'),
                 _w('  ' + _surdstr(a, m) + ' = ' + _surdstr(a * pa, ra)),
                 _w('  ' + _surdstr(b, n) + ' = ' + _surdstr(b * pb, rb)), '']
        if ra == rb:
            lines.append(_w('Like surds (both sqrt(' + str(ra) + ')), so add'))
            lines.append(_w('the coefficients:'))
            lines.append('  = ' + _surdstr(a * pa + b * pb, ra))
        else:
            lines.append(_warn('sqrt(' + str(ra) + ') and sqrt(' + str(rb) + ') are'))
            lines.append(_warn('different surds, so this does NOT'))
            lines.append(_warn('collect - leave it as'))
            lines.append('  ' + _surdstr(a * pa, ra) + _pmsurd(b * pb, rb))
        lines.append('')
        lines.append(_w('decimal check: ' +
                        _fn(a * math.sqrt(m) + b * math.sqrt(n), 6)))
        _pages('Surds', lines)
        return
    if what == 2:
        a = _asknum('a in a sqrt(m)')
        if a is None:
            return
        m = _askint('m', 0, 10 ** 12)
        if m is None:
            return
        b = _asknum('b in b sqrt(n)')
        if b is None:
            return
        n = _askint('n', 0, 10 ** 12)
        if n is None:
            return
        prod = m * n
        pa, ra = _sqsplit(prod)
        lines = [_w(_surdstr(a, m) + ' x ' + _surdstr(b, n)), '',
                 _w('sqrt(m) sqrt(n) = sqrt(mn):'),
                 _w('  = ' + _fn(a * b) + ' sqrt(' + str(prod) + ')'),
                 '  = ' + _surdstr(a * b * pa, ra), '',
                 _w('decimal check: ' +
                    _fn(a * b * math.sqrt(prod), 6))]
        _pages('Surds', lines)
        return
    # rationalise k / (p + q sqrt(n))
    k = _asknum('k (numerator)')
    if k is None:
        return
    p = _asknum('p (rational part of the bottom)')
    if p is None:
        return
    q = _asknum('q (coeff of the surd)')
    if q is None:
        return
    n = _askint('n in sqrt(n)', 0, 10 ** 12)
    if n is None:
        return
    den = p * p - q * q * n
    lines = [_w(_fn(k) + ' / (' + _sumstr(p, q, n) + ')'), '',
             _w('Multiply top and bottom by the'),
             _w('CONJUGATE ' + _sumstr(p, -q, n) + '.'),
             _w('The bottom becomes p^2 - q^2 n, which'),
             _w('has no surd in it - that is the point.'), '',
             _w('  bottom = ' + _br(p) + '^2 - ' + _br(q) + '^2 x ' + str(n) +
                ' = ' + _fn(den))]
    if abs(den) < 1e-12:
        lines.append('')
        lines.append('The bottom comes out zero, so the')
        lines.append('original expression is undefined.')
        _pages('Surds', lines)
        return
    lines.append(_w('  top    = ' + _fn(k) + '(' + _sumstr(p, -q, n) + ')'))
    lines.append('')
    # the fraction form is what goes on the paper; the decimals are the check.
    # num2 is the coefficient of sqrt(n), sign included, and a negative bottom
    # is negated away rather than printed as "/ -1".
    num1 = k * p
    num2 = -k * q
    d = den
    if d < 0:
        num1 = -num1
        num2 = -num2
        d = -d
    g = casutil.gcd(int(round(num1)), casutil.gcd(int(round(num2)), int(round(d)))) \
        if (abs(num1 - round(num1)) < 1e-9 and abs(num2 - round(num2)) < 1e-9
            and abs(d - round(d)) < 1e-9) else 1
    if abs(d - 1) < 1e-12:
        lines.append('  = ' + _sumstr(num1, num2, n))
    elif abs(d / g - 1) < 1e-12:
        # the bottom cancels away entirely, so the exact form has no fraction
        lines.append(_w('  = (' + _sumstr(num1, num2, n) + ') / ' + _fn(d)))
        lines.append('  = ' + _sumstr(num1 / g, num2 / g, n))
    elif g > 1:
        # the unreduced fraction is a step, not the answer
        lines.append(_w('  = (' + _sumstr(num1, num2, n) + ') / ' + _fn(d)))
        lines.append('  = (' + _sumstr(num1 / g, num2 / g, n) +
                     ') / ' + _fn(d / g) +
                     '   (top and bottom divided by ' + str(g) + ')')
    else:
        lines.append('  = (' + _sumstr(num1, num2, n) + ') / ' + _fn(d))
    lines.append('')
    lines.append(_w('decimal check: ' +
                    _fn(k / (p + q * math.sqrt(n)), 6)))
    _pages('Surds', lines)


def t_linecircle():
    # Where a line meets a circle. Simultaneous eqns already substitutes a line
    # into a parabola and reads the discriminant; this is the same routine with
    # a circle, and it is on every H640 paper.
    _show('Line and circle', ['Circle (x-a)^2 + (y-b)^2 = r^2',
                              'Line   y = m x + c',
                              'Substitute and read the discriminant:',
                              'two points, a tangent, or no meeting.'])
    a = _asknum('circle centre a')
    if a is None:
        return
    b = _asknum('circle centre b')
    if b is None:
        return
    r = _asknum('radius r')
    if r is None or r <= 0:
        _show('Line and circle', ['The radius must be positive.'])
        return
    vert = casui.menu('The line is', ['y = m x + c', 'vertical, x = k'])
    if vert == -1:
        return
    lines = [_w('circle (x-' + _fn(a) + ')^2 + (y-' + _fn(b) + ')^2 = ' + _fn(r * r))]
    if vert == 1:
        k = _asknum('k in x = k')
        if k is None:
            return
        lines.append(_w('line x = ' + _fn(k)))
        d = r * r - (k - a) * (k - a)
        lines.append('')
        lines.append(_w('(y-' + _fn(b) + ')^2 = ' + _fn(d)))
        if d < -1e-12:
            lines.append('negative, so the line MISSES the circle')
        elif d < 1e-12:
            lines.append('zero: TANGENT at (' + _fn(k) + ', ' + _fn(b) + ')')
        else:
            s = math.sqrt(d)
            lines.append('two points:')
            lines.append('  (' + _fn(k) + ', ' + _fn(b + s) + ')')
            lines.append('  (' + _fn(k) + ', ' + _fn(b - s) + ')')
        _pages('Line and circle', lines)
        return
    m = _asknum('m (gradient)')
    if m is None:
        return
    c = _asknum('c (intercept)')
    if c is None:
        return
    lines.append(_w('line y = ' + _fn(m) + 'x + ' + _fn(c)))
    # (x-a)^2 + (mx + c - b)^2 = r^2
    A = 1.0 + m * m
    B = -2.0 * a + 2.0 * m * (c - b)
    C = a * a + (c - b) * (c - b) - r * r
    disc = B * B - 4.0 * A * C
    lines.append('')
    lines.append(_w('substituting gives'))
    lines.append(_w('  ' + _fn(A) + 'x^2 ' + _signed(B) + 'x ' + _signed(C) + ' = 0'))
    lines.append(_w('  discriminant = ' + _fn(disc)))
    lines.append('')
    if disc < -1e-9:
        lines.append('NEGATIVE: the line misses the circle.')
        d = abs(m * a - b + c) / math.sqrt(1.0 + m * m)
        lines.append(_w('distance from the centre to the line'))
        lines.append(_w('  = |ma - b + c| / sqrt(1+m^2) = ' + _fn(d)))
        lines.append(_w('which is more than r = ' + _fn(r) + '.'))
    elif disc < 1e-9:
        x = -B / (2.0 * A)
        lines.append('ZERO: the line is a TANGENT, touching at')
        lines.append('  (' + _fn(x) + ', ' + _fn(m * x + c) + ')')
        lines.append('')
        lines.append(_w('the radius to that point has gradient'))
        if abs(x - a) > 1e-12:
            lines.append(_w('  ' + _fn((m * x + c - b) / (x - a)) +
                            ', and m x that = ' +
                            _fn(m * (m * x + c - b) / (x - a))))
            lines.append(_w('  (-1 confirms tangent perp to radius)'))
    else:
        rt = math.sqrt(disc)
        x1 = (-B + rt) / (2.0 * A)
        x2 = (-B - rt) / (2.0 * A)
        y1 = m * x1 + c
        y2 = m * x2 + c
        lines.append('POSITIVE: two points of intersection')
        lines.append('  (' + _fn(x1) + ', ' + _fn(y1) + ')')
        lines.append('  (' + _fn(x2) + ', ' + _fn(y2) + ')')
        lines.append('')
        lines.append('chord length = ' +
                     _fn(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)))
        lines.append('midpoint (' + _fn((x1 + x2) / 2.0) + ', ' +
                     _fn((y1 + y2) / 2.0) + ')')
    _pages('Line and circle', lines)


def t_sequence():
    # Generate a sequence from a kth-term formula or a recurrence, then say what
    # it does: increasing, decreasing, periodic, convergent, divergent.
    how = casui.menu('Sequence given by', ['a formula for u(n)',
                                           'a recurrence u(n+1) = f(u(n))'])
    if how == -1:
        return
    terms = []
    lines = []
    if how == 0:
        t = casui.input_expr('u(n) = (type n)')
        if t is None:
            return
        tree = caslex.parse(t)
        if tree is None:
            _show('Sequence', ['Could not read that.'])
            return
        start = _askint('first n [1]', -1000, 1000)
        if start is None:
            start = 1
        count = _askint('how many terms [12]', 1, 60)
        if count is None:
            count = 12
        lines.append(_w('u(n) = ' + caseng.tostr(caseng.simplify(tree))))
        i = 0
        while i < count:
            nv = float(start + i)
            try:
                v = caseng.evalf(tree, nv, False, {'n': nv})
            except:
                v = None
            if v is None or v != v:
                lines.append('u(' + str(start + i) + ') undefined')
                terms = []
                break
            terms.append(v)
            i += 1
    else:
        t = casui.input_expr('u(n+1) = f(u(n)), type u(n) as x')
        if t is None:
            return
        tree = caslex.parse(t)
        if tree is None:
            _show('Sequence', ['Could not read that.'])
            return
        u0 = _asknum('first term u(1)')
        if u0 is None:
            return
        count = _askint('how many terms [12]', 1, 60)
        if count is None:
            count = 12
        lines.append(_w('u(n+1) = ' + caseng.tostr(caseng.simplify(tree))))
        lines.append(_w('u(1) = ' + _fn(u0)))
        start = 1
        v = u0
        terms.append(v)
        i = 1
        while i < count:
            try:
                v = caseng.evalf(tree, v)
            except:
                v = None
            if v is None or v != v or v > 1e300 or v < -1e300:
                lines.append(_warn('term ' + str(i + 1) + ' overflowed or is undefined'))
                break
            terms.append(v)
            i += 1
    if not terms:
        _pages('Sequence', lines)
        return
    lines.append('')
    i = 0
    while i < len(terms):
        lines.append('  u(' + str(start + i) + ') = ' + _fn(terms[i], 6))
        i += 1
    lines.append('')
    # --- behaviour
    up = True
    down = True
    i = 1
    while i < len(terms):
        if terms[i] <= terms[i - 1] + 1e-12:
            up = False
        if terms[i] >= terms[i - 1] - 1e-12:
            down = False
        i += 1
    period = 0
    i = 1
    while i < len(terms) and not period:
        if abs(terms[i] - terms[0]) < 1e-9:
            # confirm the whole block repeats, not just one coincidence
            ok = True
            j = 0
            while j + i < len(terms):
                if abs(terms[j + i] - terms[j]) > 1e-9:
                    ok = False
                    break
                j += 1
            if ok and j > 0:
                period = i
        i += 1
    if period:
        lines.append('PERIODIC with period ' + str(period) + '.')
        lines.append(_w('The terms repeat in blocks of ' + str(period) + '.'))
    elif up:
        lines.append('INCREASING: every term is bigger than')
        lines.append('the one before.')
    elif down:
        lines.append('DECREASING: every term is smaller than')
        lines.append('the one before.')
    else:
        lines.append('Neither increasing nor decreasing')
        lines.append('throughout - the terms go up and down.')
    if len(terms) >= 4:
        d1 = terms[len(terms) - 1] - terms[len(terms) - 2]
        d0 = terms[len(terms) - 2] - terms[len(terms) - 3]
        last = terms[len(terms) - 1]
        if abs(d1) < 1e-7 * (1.0 + abs(last)):
            lines.append('')
            lines.append('CONVERGENT: settling on about ' + _fn(last, 6) + '.')
        elif abs(d0) > 1e-12 and abs(d1 / d0) > 1.05 and abs(last) > 1e6:
            lines.append('')
            lines.append('DIVERGENT: the terms are growing without')
            lines.append('bound.')
    _pages('Sequence', lines)

# registry ------------------------------------------------------------------
TOOLS = [
    ('Quadratic solver', t_quadratic),
    ('Simultaneous eqns', t_simul),
    ('Arithmetic seq/sum', t_arith),
    ('Geometric seq/sum', t_geo),
    ('Binomial expansion', t_binom),
    ('Logarithms', t_log),
    ('Coord geometry', t_coord),
    ('Circle', t_circle),
    ('Trig tools', t_trig),
    ('Solve a triangle', t_triangle),
    ('Arc length & sector', t_arc_sector),
    ('Inequalities', t_inequality),
    ('Surds & rationalising', t_surds),
    ('Line meets circle', t_linecircle),
    ('Sequences & behaviour', t_sequence),
    ('Proportion k x, k/x', t_proportion),
]

def run():
    casutil.run_tools('Pure (Maths) H640', TOOLS)
