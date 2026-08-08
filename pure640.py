# pure640.py - OCR B MEI H640 Pure section for the fx-CG100 maths toolkit.
# Non-calculus pure tools: quadratics, simultaneous equations, sequences/
# series, binomial, logarithms, coordinate geometry, circles, trig.
# Calculus lives in the CAS section. Stock CASIO MicroPython 1.9.4:
# ASCII only, no f-strings, iterative only, hand-built atan2.
import math
import casui
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_fc = casutil.fmtc
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now
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
    alpha = casutil.deg(_atan2(b, a))
    _pages('R-form', ['a=' + _fn(a) + '  b=' + _fn(b), 'R = sqrt(a^2+b^2)', 'R = ' + _fn(R),
                      '= R sin(x + alpha)', 'tan alpha = b/a', 'alpha = ' + _fn(alpha) + ' deg',
                      '(rad = ' + _fn(casutil.rad(alpha)) + ')'])

def _trig_exact():
    _pages('Exact values', ['deg | sin   cos   tan', '0   | 0     1     0', '30  |1/2   r3/2  1/r3',
                            '45  |1/r2  1/r2   1', '60  |r3/2  1/2    r3', '90  | 1     0    undef',
                            '(r = square root)', 'r2 ~ 1.41421', 'r3 ~ 1.73205'])

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
    lines = [nm + '(' + _fn(p) + 'x + ' + _fn(q) + ') = ' + _fn(k),
             'for ' + _fn(lo) + ' <= x <= ' + _fn(hi) + ' ' + unm,
             'principal value ' + _fn(base) + ' ' + unm,
             'period in x is ' + _fn(period / (p if p > 0 else -p)) + ' ' + unm,
             '------------------']
    if not sols:
        lines.append('no solutions in that interval.')
    else:
        for x in sols:
            lines.append('x = ' + _fn(x) + ' ' + unm)
        lines.append('')
        lines.append(str(len(sols)) + ' solutions. A multiple angle')
        lines.append('gives p times as many as the')
        lines.append('plain equation would.')
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
    lines = ['A = ' + _fn(A) + ' deg, B = ' + _fn(B) + ' deg', '']
    for nm, direct, expanded in rows:
        lines.append(nm + ' = ' + _fn(direct, 6))
        lines.append('  expansion  ' + _fn(expanded, 6) +
                     ('  agrees' if abs(direct - expanded) < 1e-9 else '  DIFFERS'))
    if abs(ca * cb) > 1e-12 and abs(1.0 - (sa / ca) * (sb / cb)) > 1e-12:
        ta = sa / ca
        tb = sb / cb
        lines.append('tan(A+B) = ' + _fn(math.tan(ra + rb), 6))
        lines.append('  expansion  ' + _fn((ta + tb) / (1.0 - ta * tb), 6))
    _pages('Compound angles', lines)


def t_trig():
    labels = ['Solve sin/cos/tan (0-360)', 'Solve p x + q, any range',
              'R-form a sin+b cos', 'Compound/double angles',
              'Check an expansion', 'Exact-value table']
    while True:
        c = casui.menu('TRIG', labels)
        if c == -1:
            return
        [_trig_solve, _trig_general, _trig_rform, _trig_compound,
         _trig_expand, _trig_exact][c]()


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
        lines.append('cosine rule: a^2 = b^2 + c^2 - 2bc cosA')
    else:
        lines.append('')
        lines.append('sine rule: a/sinA = b/sinB = c/sinC')
        lines.append('  common ratio = ' + _fn(a / math.sin(casutil.rad(A))))
    if warn is not None:
        C2 = 180.0 - A - warn
        c2 = a * math.sin(casutil.rad(C2)) / math.sin(casutil.rad(A))
        lines.append('')
        lines.append('AMBIGUOUS CASE: a < b, so there is')
        lines.append('a second triangle -')
        lines.append('  B = ' + _fn(warn) + ' deg')
        lines.append('  C = ' + _fn(C2) + ' deg')
        lines.append('  c = ' + _fn(c2))
        lines.append('Check the question for which one')
        lines.append('is wanted.')
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
    lines = ['r = ' + _fn(r),
             'theta = ' + _fn(rad) + ' rad = ' + _fn(degs) + ' deg',
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
        lines.append('(the degrees were converted first -')
        lines.append(' r theta only works in radians)')
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
        lines = [_fn(a) + 'x + ' + _fn(b) + ' ' + sym + ' 0']
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
            lines.append('a < 0, so dividing by a FLIPS the sign')
        lines.append('x ' + eff + ' ' + _fn(root))
        _pages('Inequality', lines)
        return
    c = _asknum('c')
    if c is None:
        return
    lines = [_fn(a) + 'x^2 + ' + _fn(b) + 'x + ' + _fn(c) + ' ' + sym + ' 0']
    if a == 0:
        lines.append('a = 0: this is linear, not quadratic.')
        _pages('Inequality', lines)
        return
    disc = b * b - 4.0 * a * c
    lines.append('discriminant = ' + _fn(disc))
    lo = None
    hi = None
    if disc > 0:
        rt = math.sqrt(disc)
        lo = (-b - rt) / (2.0 * a)
        hi = (-b + rt) / (2.0 * a)
        if lo > hi:
            lo, hi = hi, lo
        lines.append('roots ' + _fn(lo) + ' and ' + _fn(hi))
    elif abs(disc) < 1e-12:
        lo = -b / (2.0 * a)
        hi = lo
        lines.append('one repeated root ' + _fn(lo))
    else:
        lines.append('no real roots: the curve never')
        lines.append('crosses the axis.')
    up = a > 0
    lines.append('the parabola opens ' + ('upwards' if up else 'downwards'))
    lines.append('')
    inside_is_neg = up          # between the roots, an upward parabola is < 0
    if lo is None:
        always = (up == want_pos)
        lines.append('so it is ' + ('always' if always else 'never') +
                     ' ' + sym + ' 0:')
        lines.append('  ' + ('every real x' if always else 'no solutions'))
    elif abs(hi - lo) < 1e-12:
        lines.append('the curve touches the axis at ' + _fn(lo) + '.')
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
            lines.append('  (between the roots)')
        else:
            gt = '>=' if not strict else '>'
            lt = '<=' if not strict else '<'
            lines.append('  x ' + lt + ' ' + _fn(lo) + '  or  x ' + gt + ' ' + _fn(hi))
            lines.append('  (outside the roots)')
    lines.append('')
    lines.append('Sketch the parabola and shade the')
    lines.append('part on the right side of the axis -')
    lines.append('that is the check that never fails.')
    _pages('Inequality', lines)

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
]

def run():
    casutil.run_tools('Pure (Maths) H640', TOOLS)
