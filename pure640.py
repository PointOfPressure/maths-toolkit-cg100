# pure640.py - OCR B MEI H640 Pure section for the fx-CG100 maths toolkit.
# Non-calculus pure tools: quadratics, simultaneous equations, sequences/
# series, binomial, logarithms, coordinate geometry, circles, trig.
# Calculus lives in the CAS section. Stock CASIO MicroPython 1.9.4:
# ASCII only, no f-strings, iterative only, hand-built atan2.
import math
import casui
import caslex
import caseng

def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None

def _askint(prompt):
    v = _asknum(prompt)
    if v is None:
        return None
    try:
        return int(round(v))
    except:
        return None

def _fn(x):
    try:
        r = round(x, 4)
    except:
        return str(x)
    if r == 0:
        r = 0.0
    if r == int(r):
        return str(int(r))
    return str(r)

def _fc(re, im):
    if im >= 0:
        return _fn(re) + ' + ' + _fn(im) + 'i'
    return _fn(re) + ' - ' + _fn(-im) + 'i'

def _show(title, lines):
    casui.result_screen(title, lines)

def _pages(title, lines):
    per = 6
    i = 0
    n = len(lines)
    if n == 0:
        _show(title, [])
        return
    while i < n:
        _show(title, lines[i:i + per])
        i += per

def _atan2(y, x):
    if x > 0:
        return math.atan(y / x)
    if x < 0:
        if y >= 0:
            return math.atan(y / x) + math.pi
        return math.atan(y / x) - math.pi
    if y > 0:
        return math.pi / 2.0
    if y < 0:
        return -math.pi / 2.0
    return 0.0

def _nCr(n, r):
    if r < 0 or r > n:
        return 0
    if r > n - r:
        r = n - r
    c = 1
    i = 1
    while i <= r:
        c = c * (n - r + i) // i
        i += 1
    return c

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
        _show('Linear bx+c=0', ['b=' + _fn(b) + ' c=' + _fn(c), 'x = ' + _fn(-c / b)])
        return
    disc = b * b - 4 * a * c
    h = -b / (2.0 * a)
    k = c - b * b / (4.0 * a)
    lines = ['a=' + _fn(a) + ' b=' + _fn(b), 'c=' + _fn(c), 'disc b^2-4ac = ' + _fn(disc)]
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
        _show('Two linear eqns', ['a1 b2 - a2 b1 = 0', 'no unique solution', '(parallel/same line).'])
        return
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    _show('Two linear eqns', ['by elimination:', 'x = ' + _fn(x), 'y = ' + _fn(y)])

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
            _show('Linear + quad', ['reduces to 0 = ' + _fn(C), 'no/all intersections.'])
            return
        x = -C / B
        _show('Linear + quad', ['one intersection:', '(' + _fn(x) + ',' + _fn(m * x + c) + ')'])
        return
    disc = B * B - 4 * A * C
    lines = ['p x^2+(q-m)x+(r-c)=0', 'disc = ' + _fn(disc)]
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
    _show('Arithmetic', ['a=' + _fn(a) + ' d=' + _fn(d), 'n=' + str(n), 'Un = a+(n-1)d',
                         'Un = ' + _fn(un), 'Sn = n/2(2a+(n-1)d)', 'Sn = ' + _fn(sn)])

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
    lines = ['a=' + _fn(a) + ' r=' + _fn(r), 'n=' + str(n), 'Un = a r^(n-1)', 'Un = ' + _fn(un),
             'Sn = a(1-r^n)/(1-r)', 'Sn = ' + _fn(sn)]
    if abs(r) < 1:
        lines += ['|r|<1: S(inf)=a/(1-r)', 'S(inf) = ' + _fn(a / (1 - r))]
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
    lines = ['(a + b x)^' + str(n), 'a=' + _fn(a) + ' b=' + _fn(b), '------------------']
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
    lines = ['(1 + x)^' + _fn(n), 'valid for |x| < 1', '------------------']
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
        _show('Term coeff', ['k outside 0..n:', 'coeff of x^' + str(k) + ' = 0'])
        return
    ncr = _nCr(n, k)
    coef = ncr * (a ** (n - k)) * (b ** k)
    _show('Term coeff', ['term in (a+bx)^' + str(n), 'nCr(' + str(n) + ',' + str(k) + ') = ' + str(ncr),
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
    _show('Solve a^x=b', ['a=' + _fn(a) + '  b=' + _fn(b), 'x = log b / log a',
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
    _show('log base c of v', ['c=' + _fn(c) + '  v=' + _fn(v), 'log_c v = ln v / ln c',
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
        lines += ['gradient m = ' + _fn(m), 'line y = ' + _fn(m) + 'x + ' + _fn(b)]
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
    _pages('Centre+r -> eqn', ['centre (' + _fn(a) + ',' + _fn(b) + ')', 'radius ' + _fn(r),
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
    _show('Circle from eqn', ['centre (' + _fn(cx) + ',' + _fn(cy) + ')', 'r^2 = ' + _fn(r2),
                              'radius = ' + _fn(math.sqrt(r2))])

def t_circle():
    labels = ['Centre+r -> equation', 'Equation -> centre+r']
    while True:
        c = casui.menu('CIRCLE', labels)
        if c == -1:
            return
        if c == 0:
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
            base = math.degrees(math.asin(k))
            cand = [base, 180 - base]
        elif f == 1:
            base = math.degrees(math.acos(k))
            cand = [base, -base]
        else:
            base = math.degrees(math.atan(k))
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
    lines = ['k = ' + _fn(k), 'range 0..360 deg', '------------------']
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
    alpha = math.degrees(_atan2(b, a))
    _pages('R-form', ['a=' + _fn(a) + '  b=' + _fn(b), 'R = sqrt(a^2+b^2)', 'R = ' + _fn(R),
                      '= R sin(x + alpha)', 'tan alpha = b/a', 'alpha = ' + _fn(alpha) + ' deg',
                      '(rad = ' + _fn(math.radians(alpha)) + ')'])

def _trig_exact():
    _pages('Exact values', ['deg | sin   cos   tan', '0   | 0     1     0', '30  |1/2   r3/2  1/r3',
                            '45  |1/r2  1/r2   1', '60  |r3/2  1/2    r3', '90  | 1     0    undef',
                            '(r = square root)', 'r2 ~ 1.41421', 'r3 ~ 1.73205'])

def t_trig():
    labels = ['Solve sin/cos/tan', 'R-form a sin+b cos', 'Exact-value table']
    while True:
        c = casui.menu('TRIG', labels)
        if c == -1:
            return
        [_trig_solve, _trig_rform, _trig_exact][c]()

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
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Pure (Maths) H640', labels)
        if c == -1:
            return
        TOOLS[c][1]()
