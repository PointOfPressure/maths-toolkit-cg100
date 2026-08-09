import math
import casui
import caslex
import caseng
import caspoly
import casutil
import cascalc

_asknum = casutil.asknum
_askint = casutil.askint
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show

def _pf(tree):
    return caseng.tostr(cascalc.tidy(tree))

def _evalx(tree, xv):
    try:
        v = caseng.evalf(tree, xv)
    except:
        return None
    if isinstance(v, complex) or v != v or v > 1.7e308 or v < -1.7e308:
        return None
    return v

def t_first_order():
    # dy/dx + P(x) y = Q(x). Finding the integrating factor is half the
    # question; the marks are in performing int (IF * Q) dx and then applying
    # the condition, so this now carries it through to y = ...
    casui.show_text('First order linear',
                    'dy/dx + P(x)y = Q(x).\nEnter P(x), then Q(x).\n'
                    'IF = e^(int P dx); multiply through,\nintegrate, divide back.',
                    casui.BLACK)
    s = casui.input_expr('P(x):')
    if s is None:
        return                      # cancelled - say nothing
    P = caslex.parse(s)
    if P is None:
        _show('FIRST ORDER LINEAR', ['Could not read P(x).'])
        return
    sq = casui.input_expr('Q(x):')
    Q = None if sq is None else caslex.parse(sq)
    ip = cascalc.integ(P)
    lines = ['dy/dx + P(x)y = Q(x)', 'P(x) = ' + _pf(P)]
    if Q is not None:
        lines.append('Q(x) = ' + _pf(Q))
    lines.append('')
    if ip is None:
        lines.append('int P dx has no elementary form,')
        lines.append('so the integrating factor cannot be')
        lines.append('written down. IF = e^(int P dx).')
        _show('FIRST ORDER LINEAR', lines)
        return
    ip = cascalc.tidy(ip)
    # int P dx comes out with a modulus (int 1/x dx = ln|x|); the integrating
    # factor conventionally drops it, because any constant multiple of the IF
    # works and the sign is absorbed by the arbitrary constant.
    plain = caseng.strip_abs(ip)
    IF = caseng.simplify(('exp', plain))
    lines.append('int P dx = ' + caseng.tostr(ip))
    if plain != ip:
        lines.append('(any constant multiple of the IF')
        lines.append(' works, so the modulus is dropped)')
    lines.append('IF = e^(' + caseng.tostr(plain) + ')')
    lines.append('   = ' + _pf(IF))
    lines.append('')
    lines.append('d/dx(IF * y) = IF * Q(x)')
    if Q is None:
        lines.append('y = (1/IF) int IF*Q dx')
        _show('FIRST ORDER LINEAR', lines)
        return
    prod = caspoly.cancel(caseng.simplify(('*', IF, Q)))
    lines.append('IF * Q = ' + caseng.tostr(prod))
    R = cascalc.integ(prod)
    if R is None:
        lines.append('')
        lines.append('int IF*Q dx has no elementary form.')
        lines.append('y = (1/IF) int IF*Q dx + C/IF')
        _show('FIRST ORDER LINEAR', lines)
        return
    R = cascalc.tidy(R)
    lines.append('int IF*Q dx = ' + caseng.tostr(R))
    lines.append('')
    gen = caspoly.cancel(caseng.simplify(('/', R, IF)))
    lines.append('y = (' + caseng.tostr(R) + ' + C) / (' + caseng.tostr(IF) + ')')
    lines.append('  = ' + caseng.tostr(gen) + ' + C/(' + caseng.tostr(IF) + ')')
    x0 = _asknum('condition: x = (or cancel)')
    if x0 is not None:
        y0 = _asknum('when y =')
        if y0 is not None:
            rv = _evalx(R, x0)
            iv = _evalx(IF, x0)
            if rv is None or iv is None or iv == 0:
                lines.append('')
                lines.append('That point is outside the domain of')
                lines.append('the integrating factor.')
            else:
                C = y0 * iv - rv
                full = caspoly.cancel(caseng.simplify(
                    ('/', ('+', R, ('n', C)), IF)))
                lines.append('')
                lines.append('at (' + _fn(x0) + ', ' + _fn(y0) + '):  C = ' + _fn(C))
                lines.append('y = ' + caseng.tostr(full))
                chk = _evalx(full, x0)
                if chk is not None and abs(chk - y0) < 1e-6:
                    lines.append('(checked at the given point)')
    _show('FIRST ORDER LINEAR', lines)

def t_second_order():
    a = _asknum("a in y'' + a y' + b y = 0:")
    if a is None:
        return
    b = _asknum('b:')
    if b is None:
        return
    disc = a * a - 4.0 * b
    lines = ["y'' + a y' + b y = 0", 'aux: m^2 + a m + b = 0', 'm^2 + (' + _fn(a) + ')m + (' + _fn(b) + ') = 0', 'disc = a^2 - 4b = ' + _fn(disc)]
    if disc > 1e-9:
        rt = math.sqrt(disc)
        m1 = (-a + rt) / 2.0
        m2 = (-a - rt) / 2.0
        lines.append('Real roots:')
        lines.append('m1 = ' + _fn(m1) + ', m2 = ' + _fn(m2))
        lines.append('y = A e^(' + _fn(m1) + 'x)')
        lines.append('  + B e^(' + _fn(m2) + 'x)')
    elif disc < -1e-9:
        p = -a / 2.0
        q = math.sqrt(-disc) / 2.0
        lines.append('Complex roots p +/- q i:')
        lines.append('p = ' + _fn(p) + ', q = ' + _fn(q))
        lines.append('y = e^(' + _fn(p) + 'x) *')
        lines.append('  (A cos(' + _fn(q) + 'x)')
        lines.append('   + B sin(' + _fn(q) + 'x))')
    else:
        m = -a / 2.0
        lines.append('Repeated root m = ' + _fn(m))
        lines.append('y = (A + B x) e^(' + _fn(m) + 'x)')
    _show('SECOND ORDER CF', lines)

def t_shm():
    w = _asknum('angular freq w (>0):')
    if w is None:
        return
    if w <= 0:
        _show('SHM', ['w must be > 0.'])
        return
    T = 2.0 * math.pi / w
    f = w / (2.0 * math.pi)
    lines = ["x'' = -w^2 x", 'Simple harmonic motion', 'w = ' + _fn(w), 'Period T = 2 pi / w', 'T = ' + _fn(T), 'Frequency f = 1/T = ' + _fn(f), 'x = A cos(w t - phi)', '  = C cos(w t) + D sin(w t)']
    _show('SHM', lines)

def t_damping():
    a = _asknum("damping a in x'' + a x' + b x = 0:")
    if a is None:
        return
    b = _asknum('stiffness b:')
    if b is None:
        return
    disc = a * a - 4.0 * b
    lines = ["x'' + a x' + b x = 0", 'disc = a^2 - 4b = ' + _fn(disc)]
    if disc > 1e-9:
        lines.append('OVER-DAMPED (disc > 0)')
        lines.append('Two real roots; returns to')
        lines.append('rest with no oscillation.')
    elif disc < -1e-9:
        lines.append('UNDER-DAMPED (disc < 0)')
        lines.append('Complex roots; oscillates')
        lines.append('with decaying amplitude.')
    else:
        lines.append('CRITICAL (disc = 0)')
        lines.append('Repeated root; fastest')
        lines.append('return, no overshoot.')
    _show('DAMPING CLASSIFIER', lines)

def _ex(k):
    # e^(kx) written the way it is on paper: e^x, e^(-x), e^(2x)
    if abs(k - 1.0) < 1e-12:
        return 'e^x'
    if abs(k + 1.0) < 1e-12:
        return 'e^(-x)'
    if abs(k) < 1e-12:
        return '1'
    return 'e^(' + _fn(k) + 'x)'


def _coefstr(c, body, sep=' '):
    # c * body, with 1 and -1 written as nothing and a minus sign
    if abs(c - 1.0) < 1e-12:
        return body
    if abs(c + 1.0) < 1e-12:
        return '-' + body
    return _fn(c) + sep + body


def _term(c, body):
    # the same, but with no space - "3x", not "3 x"
    return _coefstr(c, body, '')


def _amp(letter, k):
    # "A e^(2x)", but just "A" when the exponential is 1
    if abs(k) < 1e-12:
        return letter
    return letter + ' ' + _ex(k)


def _cf_lines(a, b):
    # complementary function of y'' + a y' + b y = 0, plus the auxiliary roots
    disc = a * a - 4.0 * b
    if disc > 1e-9:
        rt = math.sqrt(disc)
        m1 = (-a + rt) / 2.0
        m2 = (-a - rt) / 2.0
        return (['m = ' + _fn(m1) + ' and ' + _fn(m2),
                 'CF: y = ' + _amp('A', m1) + ' + ' + _amp('B', m2)],
                [m1, m2])
    if disc < -1e-9:
        p = -a / 2.0
        q = math.sqrt(-disc) / 2.0
        head = '' if abs(p) < 1e-12 else _ex(p) + ' '
        return (['m = ' + _fn(p) + ' +/- ' + _fn(q) + 'i',
                 'CF: y = ' + head + '(A cos ' + _fn(q) + 'x',
                 '            + B sin ' + _fn(q) + 'x)'],
                [(p, q)])
    m = -a / 2.0
    return (['m = ' + _fn(m) + ' (repeated)',
             'CF: y = (A + Bx)' + ('' if abs(m) < 1e-12 else ' ' + _ex(m))],
            [m, m])


def _trigstr(P, Q, w):
    # P cos wx + Q sin wx, dropping a zero term rather than printing "0 cos x"
    ang = 'x' if abs(w - 1.0) < 1e-12 else _fn(w) + 'x'
    parts = []
    if abs(P) > 1e-12:
        parts.append(_coefstr(P, 'cos ' + ang))
    if abs(Q) > 1e-12:
        s = _coefstr(Q, 'sin ' + ang)
        parts.append(s if not parts else ('- ' + s[1:] if s[0] == '-' else '+ ' + s))
    if not parts:
        return '0'
    return ' '.join(parts)


def _solve2(m11, m12, m21, m22, r1, r2):
    det = m11 * m22 - m12 * m21
    if abs(det) < 1e-12:
        return None
    return ((r1 * m22 - r2 * m12) / det, (m11 * r2 - m21 * r1) / det)


def _poly_pi(a, b, coeffs):
    # Particular integral for y'' + a y' + b y = polynomial, given the
    # right-hand side lowest-power-first.
    #
    # The trial STARTS at x^bump rather than carrying a free constant term.
    # When b = 0 a constant already solves the homogeneous equation, so leaving
    # c_0 as an unknown makes the linear system singular - it has no unique
    # solution because the CF's own constant can absorb any value. Forcing the
    # trial to begin at x (or x^2 when a = b = 0) is the same step as
    # "multiply the trial by x because it is already in the CF".
    n = len(coeffs) - 1
    bump = 0
    if abs(b) < 1e-12:
        bump = 1
        if abs(a) < 1e-12:
            bump = 2
    if n + bump > 6:
        return None
    size = n + 1                      # unknowns c_bump .. c_{n+bump}

    def coef(k):
        # column index of c_k, or -1 if that power is not an unknown
        if k < bump or k > n + bump:
            return -1
        return k - bump

    M = []
    rhs = []
    j = 0
    while j < size:
        row = []
        k = 0
        while k < size:
            row.append(0.0)
            k += 1
        c = coef(j)
        if c >= 0:
            row[c] += b
        c = coef(j + 1)
        if c >= 0:
            row[c] += a * (j + 1)
        c = coef(j + 2)
        if c >= 0:
            row[c] += (j + 2) * (j + 1)
        M.append(row)
        rhs.append(coeffs[j] if j < len(coeffs) else 0.0)
        j += 1
    # Gaussian elimination with partial pivoting
    i = 0
    while i < size:
        piv = i
        k = i
        while k < size:
            if abs(M[k][i]) > abs(M[piv][i]):
                piv = k
            k += 1
        if abs(M[piv][i]) < 1e-12:
            return None
        M[i], M[piv] = M[piv], M[i]
        rhs[i], rhs[piv] = rhs[piv], rhs[i]
        k = 0
        while k < size:
            if k != i:
                f = M[k][i] / M[i][i]
                j = i
                while j < size:
                    M[k][j] -= f * M[i][j]
                    j += 1
                rhs[k] -= f * rhs[i]
            k += 1
        i += 1
    out = []
    i = 0
    while i < bump:
        out.append(0.0)               # the forced zero low-order terms
        i += 1
    i = 0
    while i < size:
        out.append(rhs[i] / M[i][i])
        i += 1
    return out


def _polystr(cs):
    parts = []
    i = len(cs) - 1
    while i >= 0:
        c = cs[i]
        if abs(c) < 1e-12:
            i -= 1
            continue
        if i == 0:
            parts.append(_fn(c))
        elif i == 1:
            parts.append(_term(c, 'x'))
        else:
            parts.append(_term(c, 'x^' + str(i)))
        i -= 1
    if not parts:
        return '0'
    out = parts[0]
    i = 1
    while i < len(parts):
        out += (' + ' if not parts[i].startswith('-') else ' ') + parts[i]
        i += 1
    return out


def t_particular():
    # Particular integral for y'' + a y' + b y = f(x). Without it the second
    # order equation never gets a general solution, and that question is on
    # every Core Pure paper.
    casui.show_text('Particular integral',
                    "y'' + a y' + b y = f(x).\\nThe general solution is\\n"
                    'CF + PI. Pick the shape of f(x).', casui.BLACK)
    a = _asknum("a (coeff of y')")
    if a is None:
        return
    b = _asknum('b (coeff of y)')
    if b is None:
        return
    kind = casui.menu('f(x) is', ['a polynomial in x', 'k e^(px)',
                                  'm cos(wx) + n sin(wx)'])
    if kind == -1:
        return
    cflines, roots = _cf_lines(a, b)
    lines = ["y'' + (" + _fn(a) + ")y' + (" + _fn(b) + ")y = f(x)",
             'auxiliary: m^2 + (' + _fn(a) + ')m + (' + _fn(b) + ') = 0']
    for ln in cflines:
        lines.append(ln)
    lines.append('')
    pistr = None
    if kind == 0:
        deg = _askint('degree of f (0-4)', 0, 4)
        if deg is None:
            return
        cs = []
        i = 0
        while i <= deg:
            v = _asknum('coeff of x^' + str(i))
            if v is None:
                return
            cs.append(v)
            i += 1
        lines.append('f(x) = ' + _polystr(cs))
        sol = _poly_pi(a, b, cs)
        if sol is None:
            lines.append('')
            lines.append('No polynomial particular integral')
            lines.append('could be found for this equation.')
            _show('PARTICULAR INTEGRAL', lines)
            return
        pistr = _polystr(sol)
        if abs(b) < 1e-12:
            lines.append('b = 0, so a constant solves the')
            lines.append('homogeneous equation - the trial')
            lines.append('polynomial has to be raised a degree.')
    elif kind == 1:
        k = _asknum('k in k e^(px)')
        if k is None:
            return
        p = _asknum('p in k e^(px)')
        if p is None:
            return
        lines.append('f(x) = ' + _coefstr(k, _ex(p)))
        den = p * p + a * p + b
        if abs(den) > 1e-12:
            pistr = _coefstr(k / den, _ex(p))
        else:
            lines.append('p is a root of the auxiliary equation,')
            lines.append('so C e^(px) is already in the CF -')
            lines.append('multiply the trial by x.')
            den2 = 2.0 * p + a
            if abs(den2) > 1e-12:
                pistr = _coefstr(k / den2, 'x ' + _ex(p))
            else:
                lines.append('It is a REPEATED root, so multiply')
                lines.append('by x again.')
                pistr = _coefstr(k / 2.0, 'x^2 ' + _ex(p))
    else:
        m = _asknum('m (cos coeff)')
        if m is None:
            return
        n = _asknum('n (sin coeff)')
        if n is None:
            return
        w = _asknum('w (inside the trig)')
        if w is None:
            return
        lines.append('f(x) = ' + _trigstr(m, n, w))
        # trial P cos wx + Q sin wx gives
        #   (b - w^2)P + a w Q = m ,  -a w P + (b - w^2)Q = n
        r = _solve2(b - w * w, a * w, -a * w, b - w * w, m, n)
        if r is not None:
            pistr = _trigstr(r[0], r[1], w)
        else:
            lines.append('w i is a root of the auxiliary')
            lines.append('equation, so cos/sin at that')
            lines.append('frequency is already in the CF -')
            lines.append('multiply the trial by x.')
            # y = x(P cos + Q sin): substituting gives
            #   (2Qw + aP) cos + (-2Pw + aQ) sin, once b = w^2 and a w terms cancel
            r = _solve2(a, 2.0 * w, -2.0 * w, a, m, n)
            if r is None:
                lines.append('The system is degenerate; solve by')
                lines.append('hand from the trial x(P cos + Q sin).')
                _show('PARTICULAR INTEGRAL', lines)
                return
            pistr = 'x(' + _trigstr(r[0], r[1], w) + ')'
    lines.append('')
    lines.append('PI: y = ' + pistr)
    lines.append('')
    lines.append('GENERAL SOLUTION = CF + PI:')
    for ln in cflines[1:]:
        lines.append('  ' + ln.replace('CF: ', ''))
    lines.append('  + ' + pistr)
    lines.append('')
    lines.append("Two conditions on y (and y') fix")
    lines.append('A and B. The PI has no arbitrary')
    lines.append('constants - do not add one.')
    _show('PARTICULAR INTEGRAL', lines)


TOOLS = [('First-order linear (IF)', t_first_order),
         ('Second-order const-coeff', t_second_order),
         ('Particular integral', t_particular),
         ('SHM recogniser', t_shm),
         ('Damping classifier', t_damping)]

def run():
    casutil.run_tools('DIFFERENTIAL EQUATIONS', TOOLS)