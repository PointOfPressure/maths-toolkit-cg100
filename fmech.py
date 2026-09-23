# OCR B (MEI) Further Maths H645, Mechanics Major (Y421): also serves the
# Mechanics Minor (Y431), whose content is a subset of the Major's.
# D dimensional analysis, F forces and friction, M moments and rigid bodies,
# W work energy power, I impulse and momentum, G centre of mass,
# C circular motion, H Hooke's law, V vectors and variable forces.
# Each section comment lists the H645 statement codes it serves and marks
# them "Y421+Y431" (also in the Minor) or "Y421 only" (Major only).
# Every tool builds three lists - answers, working, caveats - and returns
# them in that order.
import math
import casutil
import caseng
import cascalc

_S = casutil.sf3
_F = casutil.fmt
_W = casutil.w
_C = casutil.warn

G = 9.8

# ---- small shared helpers ---------------------------------------------------

def _g(g):
    if g is None:
        return G
    if g <= 0:
        raise ValueError('g must be positive')
    return g

def _pos(v, name):
    if v is None or v <= 0:
        raise ValueError(name + ' must be > 0')
    return v

def _ck_e(e):
    if e < 0 or e > 1:
        raise ValueError('e must be 0 to 1')

def _ck_mu(mu):
    if mu < 0:
        raise ValueError('mu must be >= 0')

def _nz(v, name):
    if v == 0:
        raise ValueError(name + ' must not be 0')
    return v

def _unknown(vals):
    k = -1
    i = 0
    while i < len(vals):
        if vals[i] is None:
            if k >= 0:
                raise ValueError('exactly one ? please')
            k = i
        i += 1
    if k < 0:
        raise ValueError('mark the unknown with ?')
    return k

def _vec(x, y):
    return '(' + _S(x) + ', ' + _S(y) + ')'

def _dirdeg(x, y):
    return casutil.deg(math.atan2(y, x))

def _acute(x, y):
    return casutil.deg(math.atan2(abs(y), abs(x)))

def _mag(x, y):
    return math.sqrt(x * x + y * y)

def _tidy(v):
    r = math.floor(v + 0.5)
    if abs(v - r) < 1e-9:
        return int(r)
    return v

def _sind(a):
    v = math.sin(casutil.rad(a))
    return 0.0 if abs(v) < 1e-12 else v

def _cosd(a):
    v = math.cos(casutil.rad(a))
    return 0.0 if abs(v) < 1e-12 else v

def _sinc(a):
    if abs(a) < 1e-9:
        return 1.0
    return math.sin(a) / a

def _needvar(tree, var):
    for v in caseng.vars_in(tree):
        if v != var:
            raise ValueError('use ' + var + ' as the variable')

def _defi(tree, a, b, var):
    # exact antiderivative first, Simpson as the fallback
    s = None
    try:
        s = cascalc.integ(caseng.simplify(tree), var)
    except Exception:
        s = None
    if s is not None:
        try:
            hi = caseng.evalf(s, b, False, {var: b})
            lo = caseng.evalf(s, a, False, {var: a})
            v = hi - lo
            if not isinstance(v, complex) and v == v and -1e300 < v < 1e300:
                return v
        except Exception:
            pass
    v = cascalc.defint(tree, a, b, False, 400, var)
    if v is None:
        raise ValueError('cannot integrate that')
    return v

def _limits(a, b):
    if a == b:
        raise ValueError('the limits are equal')
    if b < a:
        return (b, a)
    return (a, b)

def _sq(tree):
    return ('^', tree, ('n', 2))

def _pairs(data, msg):
    if len(data) < 2 or len(data) % 2:
        raise ValueError(msg)
    out = []
    i = 0
    while i < len(data):
        out.append((data[i], data[i + 1]))
        i += 2
    return out

def _evt(tree, env):
    # real value of tree with the given bindings, radians always
    try:
        v = caseng.evalf(tree, 0.0, False, env)
    except ZeroDivisionError:
        raise ValueError('division by zero')
    except OverflowError:
        raise ValueError('too large')
    except ValueError as e:
        raise ValueError(str(e))
    except Exception:
        raise ValueError('cannot evaluate')
    v = casutil.clean(v)
    if isinstance(v, complex):
        raise ValueError('not real')
    if v != v or v > 1e300 or v < -1e300:
        raise ValueError('undefined')
    return v

def _dt(tree):
    return cascalc.tidy(caseng.diff(caseng.simplify(tree), 't'))

def _str(tree):
    return caseng.tostr(tree)

def _shift(tree, want, at):
    # add the constant that makes tree(at) = want
    c = want - _evt(tree, {'t': at})
    if c == 0:
        return cascalc.tidy(tree)
    return cascalc.tidy(('+', tree, ('n', c)))

def _anti(tree):
    s = None
    try:
        s = cascalc.integ(caseng.simplify(tree), 't')
    except Exception:
        s = None
    if s is None:
        raise ValueError('cannot integrate ' + _str(tree))
    return s

# ---- D  dimensional analysis -----------------------------------------------
# Y421+Y431: Mq1 dimensions of a quantity, q2 dimensionless quantities,
# q3 units from dimensions, q4 changing units, q5 checking consistency,
# q6 unknown indices. q7 (using a dimensional model) is judgement: no tool.

_DIMS = [
    ('dimensionless, e, mu', 0, 0, 0),
    ('mass', 1, 0, 0),
    ('length', 0, 1, 0),
    ('time', 0, 0, 1),
    ('area', 0, 2, 0),
    ('volume', 0, 3, 0),
    ('velocity, speed', 0, 1, -1),
    ('acceleration', 0, 1, -2),
    ('ang speed, frequency', 0, 0, -1),
    ('density', 1, -3, 0),
    ('momentum, impulse', 1, 1, -1),
    ('force, weight, modulus', 1, 1, -2),
    ('energy, work, moment', 1, 2, -2),
    ('power', 1, 2, -3),
    ('pressure, stress', 1, -1, -2),
    ('spring constant k', 1, 0, -2),
    ('angular momentum', 1, 2, -1),
    ('G (gravitation)', -1, 3, -2),
]

def _powstr(names, p):
    out = ''
    i = 0
    while i < 3:
        if p[i] != 0:
            if out:
                out += ' '
            out += names[i]
            if p[i] != 1:
                out += '^' + _F(p[i])
        i += 1
    return out

def _dimstr(p):
    s = _powstr(['M', 'L', 'T'], p)
    return s if s else '1'

def _unitstr(p):
    s = _powstr(['kg', 'm', 's'], p)
    return s if s else 'none'

def _dimname(p):
    for row in _DIMS:
        if row[1] == p[0] and row[2] == p[1] and row[3] == p[2]:
            return row[0]
    return None

def t_dimlist():
    out = []
    for row in _DIMS:
        out.append(row[0] + '  ' + _dimstr([row[1], row[2], row[3]]))
    return out

def t_dimname(M, L, T):
    p = [_tidy(M), _tidy(L), _tidy(T)]
    nm = _dimname(p)
    ans = [_dimstr(p), 'SI units: ' + _unitstr(p)]
    cav = []
    if nm is None:
        cav.append(_C('not a named quantity here'))
    else:
        ans.append('this is ' + nm)
    if p[0] == 0 and p[1] == 0 and p[2] == 0:
        cav.append(_C('dimensionless: a pure number'))
    return ans + cav

def t_dimprod(data):
    # data = M,L,T,power for each factor
    if len(data) < 4 or len(data) % 4:
        raise ValueError('give M,L,T,power per factor')
    p = [0.0, 0.0, 0.0]
    wk = []
    i = 0
    while i < len(data):
        q = [data[i], data[i + 1], data[i + 2]]
        k = data[i + 3]
        j = 0
        while j < 3:
            p[j] += q[j] * k
            j += 1
        wk.append(_W('(' + _dimstr([_tidy(q[0]), _tidy(q[1]), _tidy(q[2])]) +
                     ')^' + _F(k)))
        i += 4
    p = [_tidy(p[0]), _tidy(p[1]), _tidy(p[2])]
    ans = ['[Q] = ' + _dimstr(p), 'SI units: ' + _unitstr(p)]
    nm = _dimname(p)
    if nm is not None:
        ans.append('this is ' + nm)
    return ans + wk + [_W('multiply: add the powers of M, L, T'),
                       _C('pure numbers have no dimensions')]

def t_dimcheck(lhs, rhs):
    bad = ''
    i = 0
    while i < 3:
        if abs(lhs[i] - rhs[i]) > 1e-9:
            bad += 'MLT'[i]
        i += 1
    ans = ['CONSISTENT' if bad == '' else 'NOT consistent']
    wk = [_W('LHS = ' + _dimstr(lhs)), _W('RHS = ' + _dimstr(rhs))]
    if bad:
        cav = [_C('powers of ' + bad + ' differ')]
    else:
        cav = [_C('consistent, but not a proof')]
    return ans + wk + cav

def t_dimpow(Q, A, B, C):
    # Q = k A^a B^b C^c ; rows are M, L, T
    d = (A[0] * (B[1] * C[2] - B[2] * C[1])
         - B[0] * (A[1] * C[2] - A[2] * C[1])
         + C[0] * (A[1] * B[2] - A[2] * B[1]))
    if abs(d) < 1e-12:
        raise ValueError('powers are not unique')
    a = _tidy((Q[0] * (B[1] * C[2] - B[2] * C[1])
               - B[0] * (Q[1] * C[2] - Q[2] * C[1])
               + C[0] * (Q[1] * B[2] - Q[2] * B[1])) / d)
    b = _tidy((A[0] * (Q[1] * C[2] - Q[2] * C[1])
               - Q[0] * (A[1] * C[2] - A[2] * C[1])
               + C[0] * (A[1] * Q[2] - A[2] * Q[1])) / d)
    c = _tidy((A[0] * (B[1] * Q[2] - B[2] * Q[1])
               - B[0] * (A[1] * Q[2] - A[2] * Q[1])
               + Q[0] * (A[1] * B[2] - A[2] * B[1])) / d)
    return ['a = ' + _F(a), 'b = ' + _F(b), 'c = ' + _F(c),
            _W('Q = k A^(' + _F(a) + ') B^(' + _F(b) +
               ') C^(' + _F(c) + ')'),
            _W('Q is ' + _dimstr(Q) + ', matched on M, L, T'),
            _C('k is dimensionless, not found here')]

def t_units(value, M, L, T, mu, lu, tu):
    # mu, lu, tu: the new mass, length and time units measured in kg, m, s
    _pos(mu, 'mass unit')
    _pos(lu, 'length unit')
    _pos(tu, 'time unit')
    p = [_tidy(M), _tidy(L), _tidy(T)]
    if abs(p[0]) > 99 or abs(p[1]) > 99 or abs(p[2]) > 99:
        raise ValueError('powers must be -99 to 99')
    try:
        fac = ((float(mu) ** p[0]) * (float(lu) ** p[1]) *
               (float(tu) ** p[2]))
    except OverflowError:
        raise ValueError('number too large')
    if fac == 0:
        raise ValueError('conversion factor is zero')
    return ['new value = ' + _S(value / fac),
            '1 new unit = ' + _S(fac) + ' ' + _unitstr(p),
            _W('quantity is ' + _dimstr(p) + ', SI ' + _unitstr(p)),
            _W('divide by ' + _S(mu) + '^' + _F(p[0]) + ' x ' + _S(lu) +
               '^' + _F(p[1]) + ' x ' + _S(tu) + '^' + _F(p[2])),
            _C('value in SI; units sized in kg,m,s')]

# ---- F  forces and friction -------------------------------------------------
# Y421+Y431: d3 F <= mu R, d4 mu = tan(alpha), d5 Newton's laws with
# friction, d6 resolving, d7 resultant of concurrent forces, Md8 equilibrium
# iff the resultant is zero, d9 triangle of forces, d10 solving equilibrium by
# resolving or by a polygon of forces (Lami). Md1, d2 and the * force
# language are conceptual: no tool.

def _sumf(data):
    fs = _pairs(data, 'need force,angle pairs')
    sx = 0.0
    sy = 0.0
    tot = 0.0
    for f, ang in fs:
        sx += f * _cosd(ang)
        sy += f * _sind(ang)
        tot += abs(f)
    eps = 1e-9 * (tot if tot > 1.0 else 1.0)
    if abs(sx) <= eps:
        sx = 0.0
    if abs(sy) <= eps:
        sy = 0.0
    return (sx, sy, eps, len(fs))

def t_resultant(data):
    sx, sy, eps, n = _sumf(data)
    R = _mag(sx, sy)
    wk = [_W('Rx = sum F cos a = ' + _S(sx)),
          _W('Ry = sum F sin a = ' + _S(sy)),
          _W(str(n) + ' forces, angles from the x axis')]
    if R <= eps:
        return ['R = 0 N', 'in equilibrium'] + wk + \
               [_C('the force polygon closes')]
    d = _dirdeg(sx, sy)
    b = d - 180.0 if d > 0 else d + 180.0
    return ['R = ' + _S(R) + ' N', 'direction = ' + _S(d) + ' deg',
            'R = ' + _vec(sx, sy) + ' N',
            'not in equilibrium',
            'balance: ' + _S(R) + ' N at ' + _S(b) + ' deg'] + wk

def t_resolve(F, angle, line):
    d = angle - line
    return ['along = ' + _S(F * _cosd(d)) + ' N',
            'perpendicular = ' + _S(F * _sind(d)) + ' N',
            _W('angle between F and line = ' + _S(d) + ' deg'),
            _W('along F cos, perpendicular F sin'),
            _C('perp is 90 deg anticlockwise of line')]

def t_twoforce(p, q, data):
    sx, sy, eps, n = _sumf(data)
    det = _sind(q - p)
    if abs(det) < 1e-12:
        raise ValueError('P and Q are parallel')
    P = (-sx * _sind(q) + sy * _cosd(q)) / det
    Q = (-sy * _cosd(p) + sx * _sind(p)) / det
    ans = ['P = ' + _S(P) + ' N', 'Q = ' + _S(Q) + ' N']
    wk = [_W('known forces sum to ' + _vec(sx, sy)),
          _W('P cos p + Q cos q = ' + _S(-sx)),
          _W('P sin p + Q sin q = ' + _S(-sy))]
    cav = []
    if P < 0 or Q < 0:
        cav.append(_C('negative: that force points the other way'))
    return ans + wk + cav

def t_triforce(F1, F2, F3):
    _pos(F1, 'F1')
    _pos(F2, 'F2')
    _pos(F3, 'F3')
    if F1 + F2 <= F3 or F2 + F3 <= F1 or F3 + F1 <= F2:
        raise ValueError('these cannot close a triangle')
    a3 = casutil.deg(casutil.acos_safe((F1 * F1 + F2 * F2 - F3 * F3) /
                                       (2.0 * F1 * F2)))
    a1 = casutil.deg(casutil.acos_safe((F2 * F2 + F3 * F3 - F1 * F1) /
                                       (2.0 * F2 * F3)))
    a2 = 180.0 - a1 - a3
    return ['F1 to F2 = ' + _S(180.0 - a3) + ' deg',
            'F2 to F3 = ' + _S(180.0 - a1) + ' deg',
            'F3 to F1 = ' + _S(180.0 - a2) + ' deg',
            _W('triangle angles opposite F1,F2,F3:'),
            _W(_S(a1) + ', ' + _S(a2) + ', ' + _S(a3) + ' deg'),
            _W('angle between two = 180 - angle opposite third'),
            _W('Lami: F1/sin(F2^F3) = F2/sin(F3^F1)'),
            _C('the three angles add to 360')]

def t_mutan(mu, angle):
    k = _unknown([mu, angle])
    if k == 0:
        if angle < 0 or angle >= 90:
            raise ValueError('angle is 0 to 90')
        mu = math.tan(casutil.rad(angle))
        ans = ['mu = ' + _S(mu)]
    else:
        _ck_mu(mu)
        angle = casutil.deg(math.atan(mu))
        ans = ['angle = ' + _S(angle) + ' deg']
    return ans + [_W('about to slip: mg sin a = mu mg cos a'),
                  _W('so mu = tan a, the mass cancels'),
                  _C('no other force acting')]

def t_slope(m, angle, mu, F, g):
    g = _g(g)
    _pos(m, 'm')
    _ck_mu(mu)
    if angle < 0 or angle >= 90:
        raise ValueError('angle is 0 to 90')
    down = m * g * _sind(angle)
    rn = m * g * _cosd(angle)
    fmax = mu * rn
    drive = F - down
    wk = [_W('R = mg cos a = ' + _S(rn)),
          _W('mg sin a = ' + _S(down)),
          _W('F max = mu R = ' + _S(fmax)),
          _W('F - mg sin a = ' + _S(drive) + ' (up +)')]
    if abs(drive) <= fmax:
        ans = ['stays at rest', 'a = 0 m/s2',
               'friction = ' + _S(abs(drive)) + ' N']
        if drive > 0:
            ans.append('friction acts down the slope')
        elif drive < 0:
            ans.append('friction acts up the slope')
        cav = []
        if abs(abs(drive) - fmax) < 1e-9 * (1 + fmax):
            cav.append(_C('limiting: on the point of slipping'))
        return ans + wk + cav
    acc = (abs(drive) - fmax) / m
    return ['a = ' + _S(acc) + ' m/s2',
            'moves ' + ('up' if drive > 0 else 'down') + ' the slope',
            'friction = ' + _S(fmax) + ' N'] + wk + \
           [_C('F acts up, along the slope')]

def t_hold(m, angle, mu, beta, g):
    g = _g(g)
    _pos(m, 'm')
    _ck_mu(mu)
    if angle < 0 or angle >= 90:
        raise ValueError('angle is 0 to 90')
    b = 0.0 if beta is None else beta
    if b <= -90 or b >= 90:
        raise ValueError('beta is -90 to 90')
    sa = _sind(angle)
    ca = _cosd(angle)
    cb = _cosd(b)
    sb = _sind(b)
    if cb + mu * sb <= 1e-12:
        raise ValueError('P cannot hold it at that beta')
    lo = m * g * (sa - mu * ca) / (cb + mu * sb)
    ans = []
    cav = []
    if lo <= 0:
        ans.append('min P = 0 N')
        cav.append(_C('it rests without P: mu >= tan a'))
    else:
        ans.append('min P = ' + _S(lo) + ' N')
    dn = cb - mu * sb
    if dn <= 1e-12:
        ans.append('no max: P never drags it up')
    else:
        ans.append('max P = ' + _S(m * g * (sa + mu * ca) / dn) + ' N')
    wk = [_W('P at beta = ' + _S(b) + ' deg above the slope'),
          _W('min: P cos b + mu R = mg sin a'),
          _W('max: P cos b = mg sin a + mu R'),
          _W('R = mg cos a - P sin b, g = ' + _S(g))]
    if sb > 0:
        cav.append(_C('check R > 0: P must not lift it'))
    return ans + wk + cav

def t_frich(m, mu, P, angle, g):
    g = _g(g)
    _pos(m, 'm')
    _ck_mu(mu)
    if P < 0:
        raise ValueError('P must be >= 0')
    a = 0.0 if angle is None else angle
    if a <= -90 or a >= 90:
        raise ValueError('angle is -90 to 90')
    rn = m * g - P * _sind(a)
    if rn < 0:
        raise ValueError('P sin a > mg: it lifts off')
    fmax = mu * rn
    drive = P * _cosd(a)
    wk = [_W('R = mg - P sin a = ' + _S(rn)),
          _W('F max = mu R = ' + _S(fmax)),
          _W('P cos a = ' + _S(drive))]
    if drive <= fmax:
        return ['does not move', 'friction = ' + _S(drive) + ' N',
                'a = 0 m/s2'] + wk + [_C('friction is not at its maximum')
                                      if drive < fmax else
                                      _C('limiting: about to slip')]
    return ['it moves', 'a = ' + _S((drive - fmax) / m) + ' m/s2',
            'friction = ' + _S(fmax) + ' N'] + wk

# ---- M  moments and rigid bodies ---------------------------------------------
# Y421+Y431: d13 couples, d14 moments about an axis, d15 equilibrium of a
# rigid body, d16 sliding or toppling, G5 centre of mass in toppling.
# d11 force diagrams and d12 turning effect are conceptual: no tool.

def t_moments(data):
    if len(data) < 4 or len(data) % 4:
        raise ValueError('give Fx,Fy,x,y for each force')
    rx = 0.0
    ry = 0.0
    gm = 0.0
    i = 0
    while i < len(data):
        rx += data[i]
        ry += data[i + 1]
        gm += data[i + 2] * data[i + 1] - data[i + 3] * data[i]
        i += 4
    R = _mag(rx, ry)
    ans = ['R = ' + _vec(rx, ry) + ' N', '|R| = ' + _S(R) + ' N',
           'moment at O = ' + _S(gm) + ' N m']
    wk = [_W('G = sum (x Fy - y Fx), anticlockwise +')]
    cav = []
    if R < 1e-12:
        if abs(gm) < 1e-12:
            ans.append('in equilibrium')
        else:
            ans.append('a couple of ' + _S(gm) + ' N m')
            cav.append(_C('same moment about every point'))
    else:
        ans.append('direction = ' + _S(_dirdeg(rx, ry)) + ' deg')
        if abs(ry) > 1e-12:
            ans.append('cuts y = 0 at x = ' + _S(gm / ry))
        if abs(rx) > 1e-12:
            ans.append('cuts x = 0 at y = ' + _S(-gm / rx))
        wk.append(_W('line of action: x Ry - y Rx = ' + _S(gm)))
    return ans + wk + cav

def t_couple(F, d, p):
    ans = ['G = ' + _S(F * d) + ' N m', 'resultant force = 0 N']
    wk = [_W('G = F d, d the perpendicular gap'),
          _W('F down at x = 0, F up at x = ' + _S(d))]
    if p is not None:
        m0 = (0.0 - p) * (-F)
        m1 = (d - p) * F
        ans.append('about x = ' + _S(p) + ': ' + _S(m0 + m1) + ' N m')
        wk.append(_W('about p: ' + _S(m0) + ' + ' + _S(m1)))
    return ans + wk + [_C('a couple has the same moment everywhere')]

def t_beam(L, W, a, b, P, x):
    _pos(L, 'L')
    if a == b:
        raise ValueError('the supports coincide')
    Rb = (W * (L / 2.0 - a) + P * (x - a)) / (b - a)
    Ra = W + P - Rb
    ans = ['R at a = ' + _S(Ra) + ' N', 'R at b = ' + _S(Rb) + ' N']
    wk = [_W('about a: Rb(b-a) = W(L/2-a) + P(x-a)'),
          _W('Ra + Rb = W + P = ' + _S(W + P) + ' N'),
          _W('the weight acts at L/2 = ' + _S(L / 2.0))]
    cav = []
    if Ra < 0 or Rb < 0:
        cav.append(_C('a reaction is negative: it tips'))
    if x < 0 or x > L:
        cav.append(_C('the load is off the beam'))
    return ans + wk + cav

def t_ladder(L, W, x, Wp, mu, angle):
    _pos(L, 'L')
    _pos(mu, 'mu')
    if x < 0 or x > L:
        raise ValueError('x is 0 to L along the ladder')
    tot = W + Wp
    if tot <= 0:
        raise ValueError('total weight must be > 0')
    num = W * L / 2.0 + Wp * x
    tmin = num / (mu * tot * L)
    amin = casutil.deg(math.atan(tmin))
    ans = ['min angle = ' + _S(amin) + ' deg']
    wk = [_W('base moments: N L sin th = W L/2 + Wp x'),
          _W('N <= mu R, R = W + Wp = ' + _S(tot) + ' N'),
          _W('tan th = ' + _S(tmin))]
    if angle is not None:
        if angle <= 0 or angle >= 90:
            raise ValueError('angle is 0 to 90 exclusive')
        N = num / (L * math.tan(casutil.rad(angle)))
        ans.append('wall N = ' + _S(N) + ' N')
        ans.append('friction needed = ' + _S(N) + ' N')
        ans.append('mu needed = ' + _S(N / tot))
        ans.append('it slips' if angle < amin else 'it stays put')
    return ans + wk + [_C('smooth wall, x measured up the ladder')]

def t_hinge(L, W, d, alpha, P, x):
    _pos(L, 'L')
    _pos(d, 'd')
    if alpha <= 0 or alpha >= 180:
        raise ValueError('alpha is 0 to 180 exclusive')
    sa = _sind(alpha)
    if sa == 0:
        raise ValueError('the string lies along the rod')
    T = (W * L / 2.0 + P * x) / (d * sa)
    H = T * _cosd(alpha)
    V = W + P - T * sa
    ans = ['T = ' + _S(T) + ' N', 'hinge H = ' + _S(H) + ' N',
           'hinge V = ' + _S(V) + ' N',
           'hinge force = ' + _S(_mag(H, V)) + ' N']
    wk = [_W('about A: T d sin al = W L/2 + P x'),
          _W('H = T cos al, V = W + P - T sin al')]
    if _mag(H, V) > 0:
        wk.append(_W('hinge at ' + _S(_dirdeg(H, V)) + ' deg to the rod'))
    cav = [_C('rod horizontal, hinge at A, x from A')]
    if V < 0:
        cav.append(_C('the hinge pulls down on the rod'))
    return ans + wk + cav

def _first(ta, tb, aname, bname):
    if ta < tb - 1e-12:
        return aname
    if tb < ta - 1e-12:
        return bname
    return 'it slides and topples together'

def t_topple(a, h, mu, angle):
    _pos(a, 'a')
    _pos(h, 'h')
    _ck_mu(mu)
    tt = casutil.deg(math.atan(a / h))
    ts = casutil.deg(math.atan(mu))
    ans = ['topple angle = ' + _S(tt) + ' deg',
           'slide angle = ' + _S(ts) + ' deg',
           _first(tt, ts, 'it topples first', 'it slides first')]
    if angle is not None:
        if angle < 0 or angle >= 90:
            raise ValueError('angle is 0 to 90')
        t = math.tan(casutil.rad(angle))
        ans.append('at ' + _S(angle) + ' deg: ' +
                   ('topples' if t > a / h else 'no topple') + ', ' +
                   ('slides' if t > mu else 'no slide'))
    return ans + [_W('topples when tan th > a/h = ' + _S(a / h)),
                  _W('slides when tan th > mu = ' + _S(mu)),
                  _C('a: G to lower edge, h: height of G')]

def t_push(W, base, y, mu):
    _pos(W, 'W')
    _pos(base, 'base')
    _pos(y, 'y')
    _ck_mu(mu)
    ps = mu * W
    pt = W * base / (2.0 * y)
    return ['P to slide = ' + _S(ps) + ' N',
            'P to topple = ' + _S(pt) + ' N',
            _first(pt, ps, 'it topples first', 'it slides first'),
            _W('slides when P > mu W'),
            _W('topples when P y > W base/2'),
            _C('P is horizontal, y above the ground')]

# ---- W  work, energy and power ------------------------------------------------
# Y421+Y431: w2 work by a force incl. a variable force (calculus), w3 work
# in a direction by the scalar product, w4 KE, w5 GPE, w6 conservation of
# mechanical energy, w7 work-energy principle, w8 power = F . v.
# Mw1 (language) has no tool.

def t_workfd(F, d, angle):
    ca = _cosd(angle)
    wk = F * d * ca
    cav = []
    if wk < 0:
        cav.append(_C('negative: the force opposes motion'))
    if abs(ca) < 1e-12:
        cav.append(_C('a force at 90 deg does no work'))
    return ['W = ' + _S(wk) + ' J',
            _W('W = F d cos th'),
            _W('= ' + _S(F) + ' x ' + _S(d) + ' x ' + _S(ca))] + cav

def t_workdot(F, d):
    w = F[0] * d[0] + F[1] * d[1] + F[2] * d[2]
    fm = math.sqrt(F[0] * F[0] + F[1] * F[1] + F[2] * F[2])
    dm = math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
    ans = ['W = F.d = ' + _S(w) + ' J']
    wk = [_W('F.d = ' + _S(F[0]) + 'x' + _S(d[0]) + ' + ' + _S(F[1]) +
             'x' + _S(d[1]) + ' + ' + _S(F[2]) + 'x' + _S(d[2]))]
    cav = []
    if dm > 0:
        ans.append('F along d = ' + _S(w / dm) + ' N')
        if fm > 0:
            ans.append('angle F to d = ' +
                       _S(casutil.deg(casutil.acos_safe(w / (fm * dm)))) +
                       ' deg')
        wk.append(_W('|F| = ' + _S(fm) + ', |d| = ' + _S(dm)))
    if abs(w) < 1e-12:
        cav.append(_C('F is perpendicular to d: no work'))
    return ans + wk + cav + [_C('use z = 0 for 2-D')]

def t_varwork(F, a, b, m, u):
    _needvar(F, 'x')
    a, b = _limits(a, b)
    work = _defi(F, a, b, 'x')
    ans = ['W = ' + _S(work) + ' J']
    wk = [_W('W = int F dx from ' + _S(a) + ' to ' + _S(b)),
          _W('F(x) = ' + caseng.tostr(F))]
    cav = []
    if m is not None:
        _pos(m, 'm')
        u0 = 0.0 if u is None else u
        s = u0 * u0 + 2.0 * work / m
        wk.append(_W('W = 0.5 m v^2 - 0.5 m u^2, u = ' + _S(u0)))
        if s < 0:
            cav.append(_C('KE would go negative: it stops'))
        else:
            ans.append('v = ' + _S(math.sqrt(s)) + ' m/s')
        if u is None:
            cav.append(_C('u not given, taken as 0'))
    return ans + wk + cav

def t_energy(m, u, v, h, g):
    _pos(m, 'm')
    g = _g(g)
    dke = 0.5 * m * (v * v - u * u)
    dpe = m * g * h
    ans = ['change KE = ' + _S(dke) + ' J', 'change GPE = ' + _S(dpe) + ' J',
           'other work = ' + _S(dke + dpe) + ' J']
    wk = [_W('KE = 0.5 m v^2, GPE = m g h, h up'),
          _W('g = ' + _S(g) + ', other work = dKE + dGPE')]
    cav = []
    if abs(dke + dpe) < 1e-9:
        cav.append(_C('energy conserved: smooth, no driving'))
    return ans + wk + cav

def t_dropspeed(u, h, g):
    g = _g(g)
    s = u * u + 2.0 * g * h
    wk = [_W('0.5 m v^2 = 0.5 m u^2 + m g h, m cancels'),
          _W('v^2 = ' + _S(s) + ', g = ' + _S(g))]
    if s < 0:
        return ['it never gets there',
                'max rise = ' + _S(u * u / (2.0 * g)) + ' m'] + wk + \
               [_C('h < 0 is a rise')]
    return ['v = ' + _S(math.sqrt(s)) + ' m/s'] + wk + \
           [_C('h is the drop; only gravity does work')]

_ENAMES = ['m', 'u', 'v', 'h', 'F', 'd']
_EUNITS = ['kg', 'm/s', 'm/s', 'm', 'N', 'm']

def t_energyres(m, u, v, h, F, d, g):
    k = _unknown([m, u, v, h, F, d])
    g = _g(g)
    # 0.5 m (v^2 - u^2) + m g h + F d = 0 ; h = rise, F = resistance
    if k == 0:
        m = -F * d / _nz(0.5 * (v * v - u * u) + g * h, 'the energy change')
    else:
        _pos(m, 'm')
        if k == 1:
            s = v * v + 2 * g * h + 2 * F * d / m
            if s < 0:
                raise ValueError('no real u: it cannot get there')
            u = math.sqrt(s)
        elif k == 2:
            s = u * u - 2 * g * h - 2 * F * d / m
            if s < 0:
                raise ValueError('it stops before that point')
            v = math.sqrt(s)
        elif k == 3:
            h = -(0.5 * (v * v - u * u) + F * d / m) / g
        elif k == 4:
            F = -m * (0.5 * (v * v - u * u) + g * h) / _nz(d, 'd')
        else:
            d = -m * (0.5 * (v * v - u * u) + g * h) / _nz(F, 'F')
    got = [m, u, v, h, F, d][k]
    dke = 0.5 * m * (v * v - u * u)
    ans = [_ENAMES[k] + ' = ' + _S(got) + ' ' + _EUNITS[k],
           'change KE = ' + _S(dke) + ' J',
           'GPE gain = ' + _S(m * g * h) + ' J',
           'work vs resistance = ' + _S(F * d) + ' J']
    wk = [_W('0.5m(v^2 - u^2) + mgh + Fd = 0'),
          _W('h is the rise, F opposes over distance d'),
          _W('g = ' + _S(g))]
    cav = []
    if F < 0:
        cav.append(_C('F < 0: that force drives, not resists'))
    if m <= 0:
        cav.append(_C('m came out <= 0: check the signs'))
    return ans + wk + cav

def t_power(P, F, v):
    k = _unknown([P, F, v])
    if k == 0:
        P = F * v
    elif k == 1:
        F = P / _nz(v, 'v')
    else:
        v = P / _nz(F, 'F')
    return [['P', 'F', 'v'][k] + ' = ' + _S([P, F, v][k]) + ' ' +
            ['W', 'N', 'm/s'][k],
            _W('P = F v'),
            _W(_S(P) + ' = ' + _S(F) + ' x ' + _S(v)),
            _C('F is the tractive force, not the net')]

def t_powang(F, v, angle):
    ca = _cosd(angle)
    return ['P = ' + _S(F * v * ca) + ' W',
            'v along F = ' + _S(v * ca) + ' m/s',
            _W('P = F . v = F v cos th'),
            _W('= ' + _S(F) + ' x ' + _S(v) + ' x ' + _S(ca)),
            _C('th is between F and the velocity')]

def t_slopemax(P, m, R, angle, g):
    _pos(m, 'm')
    g = _g(g)
    gs = m * g * _sind(angle)
    res = R + gs
    if res <= 0:
        raise ValueError('no maximum: total resistance <= 0')
    return ['max speed = ' + _S(P / res) + ' m/s',
            'tractive force = ' + _S(res) + ' N',
            'mg sin th = ' + _S(gs) + ' N',
            _W('at max speed a = 0, so F = R + mg sin'),
            _W('P = F v, F = ' + _S(res) + ' N, g = ' + _S(g)),
            _C('a negative angle means downhill')]

def t_slopeacc(P, m, R, angle, v, g):
    _pos(m, 'm')
    _pos(v, 'v')
    g = _g(g)
    gs = m * g * _sind(angle)
    F = P / v
    net = F - R - gs
    ans = ['a = ' + _S(net / m) + ' m/s2',
           'tractive force = ' + _S(F) + ' N',
           'net force = ' + _S(net) + ' N']
    wk = [_W('F = P / v = ' + _S(P) + ' / ' + _S(v)),
          _W('ma = F - R - mg sin th'),
          _W('mg sin th = ' + _S(gs) + ' N')]
    cav = []
    if net < 0:
        cav.append(_C('negative: it is slowing down'))
    return ans + wk + cav

# ---- I  impulse and momentum -------------------------------------------------
# Y421+Y431: Mi1 impulse, i2 momentum, i3 impulse-momentum, i4 conservation,
# Mi6 direct impact, i7 Newton's experimental law, i8 e = 0, i9 impact with a
# wall, i10 direct impact problems, i11 e = 1, i12 KE loss when e < 1.
# Y421 only: Mi13 oblique impact, i14 NEL along the line of centres, i15
# sphere on a surface, i16 two spheres, i17 KE loss in oblique impact.
# i5 (language of direct impact) has no tool.

_CNAMES = ['m1', 'u1', 'm2', 'u2', 'v1', 'v2']
_CUNITS = ['kg', 'm/s', 'kg', 'm/s', 'm/s', 'm/s']

def _ke(m1, s1, m2, s2):
    return 0.5 * m1 * s1 * s1 + 0.5 * m2 * s2 * s2

def _keans(before, after):
    d = before - after
    if d < -1e-12:
        return ['KE gained = ' + _S(-d) + ' J']
    return ['KE lost = ' + _S(d) + ' J']

def _kewk(before, after):
    return [_W('KE before = ' + _S(before) + ' J'),
            _W('KE after = ' + _S(after) + ' J')]

def t_cons1d(m1, u1, m2, u2, v1, v2):
    k = _unknown([m1, u1, m2, u2, v1, v2])
    if k == 0:
        m1 = m2 * (v2 - u2) / _nz(u1 - v1, 'u1 - v1')
    elif k == 1:
        u1 = (m1 * v1 + m2 * v2 - m2 * u2) / _nz(m1, 'm1')
    elif k == 2:
        m2 = m1 * (u1 - v1) / _nz(v2 - u2, 'v2 - u2')
    elif k == 3:
        u2 = (m1 * v1 + m2 * v2 - m1 * u1) / _nz(m2, 'm2')
    elif k == 4:
        v1 = (m1 * u1 + m2 * u2 - m2 * v2) / _nz(m1, 'm1')
    else:
        v2 = (m1 * u1 + m2 * u2 - m1 * v1) / _nz(m2, 'm2')
    got = [m1, u1, m2, u2, v1, v2][k]
    p = m1 * u1 + m2 * u2
    ke0 = _ke(m1, u1, m2, u2)
    ke1 = _ke(m1, v1, m2, v2)
    ans = [_CNAMES[k] + ' = ' + _S(got) + ' ' + _CUNITS[k],
           'momentum = ' + _S(p) + ' kg m/s']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('m1u1+m2u2 = m1v1+m2v2'),
          _W(_S(m1) + '(' + _S(u1) + ') + ' + _S(m2) + '(' + _S(u2) +
             ') = ' + _S(p))]
    wk.extend(_kewk(ke0, ke1))
    cav = []
    if m1 <= 0 or m2 <= 0:
        cav.append(_C('a mass is not positive'))
    if ke1 > ke0 + 1e-9:
        cav.append(_C('KE rises: an explosion, not an impact'))
    return ans + wk + cav

def t_coalesce(m1, u1, m2, u2):
    tot = _nz(m1 + m2, 'm1 + m2')
    p = m1 * u1 + m2 * u2
    v = p / tot
    ke0 = _ke(m1, u1, m2, u2)
    ke1 = _ke(tot, v, 0.0, 0.0)
    ans = ['v = ' + _S(v) + ' m/s', 'momentum = ' + _S(p) + ' kg m/s']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('m1u1+m2u2 = (m1+m2)v'),
          _W(_S(p) + ' = ' + _S(tot) + ' v')]
    wk.extend(_kewk(ke0, ke1))
    return ans + wk + [_C('e = 0: they move off together')]

def t_direct(m1, u1, m2, u2, e):
    _pos(m1, 'm1')
    _pos(m2, 'm2')
    _ck_e(e)
    sep = e * (u1 - u2)
    v1 = (m1 * u1 + m2 * u2 - m2 * sep) / (m1 + m2)
    v2 = v1 + sep
    ke0 = _ke(m1, u1, m2, u2)
    ke1 = _ke(m1, v1, m2, v2)
    ans = ['v1 = ' + _S(v1) + ' m/s', 'v2 = ' + _S(v2) + ' m/s',
           'impulse on 2 = ' + _S(m2 * (v2 - u2)) + ' N s']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('m1u1+m2u2 = m1v1+m2v2'),
          _W('v2 - v1 = e(u1 - u2) = ' + _S(sep))]
    wk.extend(_kewk(ke0, ke1))
    cav = []
    if u1 <= u2:
        cav.append(_C('u1 <= u2: they never meet'))
    if e == 1:
        cav.append(_C('e = 1: perfectly elastic, KE kept'))
    if e == 0:
        cav.append(_C('e = 0: they coalesce'))
    return ans + wk + cav

def t_finde(u1, u2, v1, v2):
    e = (v2 - v1) / _nz(u1 - u2, 'u1 - u2')
    cav = []
    if e < -1e-12:
        cav.append(_C('e < 0: they would pass through'))
    elif e > 1 + 1e-12:
        cav.append(_C('e > 1: KE gained, impossible'))
    elif abs(e) < 1e-12:
        cav.append(_C('e = 0: they coalesce'))
    elif abs(e - 1) < 1e-12:
        cav.append(_C('e = 1: perfectly elastic'))
    return ['e = ' + _S(e),
            _W('e = separation / approach'),
            _W('= (' + _S(v2) + ' - ' + _S(v1) + ') / (' + _S(u1) + ' - ' +
               _S(u2) + ')')] + cav

def t_bounce(h, e, g):
    _pos(h, 'h')
    _ck_e(e)
    g = _g(g)
    u = math.sqrt(2.0 * g * h)
    t0 = u / g
    ans = ['speed at impact = ' + _S(u) + ' m/s',
           'rebound speed = ' + _S(e * u) + ' m/s',
           'rebound height = ' + _S(e * e * h) + ' m',
           'time to next bounce = ' + _S(2.0 * e * u / g) + ' s']
    wk = [_W('v = sqrt(2gh), rebound e v, height e^2 h'),
          _W('g = ' + _S(g) + ', first fall ' + _S(t0) + ' s')]
    cav = []
    if e < 1:
        ans.append('total distance = ' +
                   _S(h * (1 + e * e) / (1 - e * e)) + ' m')
        ans.append('total time = ' + _S(t0 * (1 + e) / (1 - e)) + ' s')
        wk.append(_W('sums of geometric series, ratio e^2 and e'))
    else:
        cav.append(_C('e = 1: it bounces for ever'))
    return ans + wk + cav

def t_wall(u, angle, e, m):
    _pos(u, 'u')
    _ck_e(e)
    if angle <= 0 or angle > 90:
        raise ValueError('angle to wall is 0 to 90')
    par = u * _cosd(angle)
    nor = u * _sind(angle)
    nout = e * nor
    v = _mag(par, nout)
    ans = ['speed = ' + _S(v) + ' m/s']
    if v > 0:
        ans.append('angle to wall = ' + _S(_acute(par, nout)) + ' deg')
    wk = [_W('along the wall ' + _S(par) + ' m/s, kept'),
          _W('normal ' + _S(nor) + ' -> e x that = ' + _S(nout)),
          _W('tan(out) = e tan(in), angles to the wall')]
    if m is not None:
        _pos(m, 'm')
        ans.append('impulse = ' + _S(m * (1.0 + e) * nor) + ' N s')
        ans.append('KE lost = ' + _S(0.5 * m * nor * nor * (1 - e * e)) + ' J')
        wk.append(_W('impulse m(1+e)u sin, along the normal'))
    cav = [_C('smooth wall: no impulse along it')]
    if e == 1:
        cav.append(_C('e = 1: rebound angle = angle in'))
    if e == 0:
        cav.append(_C('e = 0: it slides along the wall'))
    return ans + wk + cav

def t_wallvec(v, e, m):
    _ck_e(e)
    vy = v[1]
    ox = v[0]
    oy = -e * vy
    sp = _mag(ox, oy)
    ans = ['v out = ' + _vec(ox, oy) + ' m/s', 'speed = ' + _S(sp) + ' m/s']
    if sp > 0:
        ans.append('angle to wall = ' + _S(_acute(ox, oy)) + ' deg')
    wk = [_W('wall along x, normal along y'),
          _W('x part kept, y part -> -e y')]
    if m is not None:
        _pos(m, 'm')
        ans.append('impulse = ' + _S(abs(m * (oy - vy))) + ' N s')
        ans.append('KE lost = ' + _S(0.5 * m * vy * vy * (1 - e * e)) + ' J')
    return ans + wk + [_C('smooth wall: no impulse along it')]

def _oblique(m1, x1, y1, m2, x2, y2, e):
    _pos(m1, 'm1')
    _pos(m2, 'm2')
    _ck_e(e)
    sep = e * (x1 - x2)
    v1 = (m1 * x1 + m2 * x2 - m2 * sep) / (m1 + m2)
    v2 = v1 + sep
    ke0 = _ke(m1, _mag(x1, y1), m2, _mag(x2, y2))
    ke1 = _ke(m1, _mag(v1, y1), m2, _mag(v2, y2))
    return (v1, v2, sep, ke0, ke1)

def t_oblique(m1, u1, m2, u2, e):
    x1, x2, sep, ke0, ke1 = _oblique(m1, u1[0], u1[1], m2, u2[0], u2[1], e)
    y1 = u1[1]
    y2 = u2[1]
    ans = ['v1 = ' + _vec(x1, y1) + ' m/s', 'v2 = ' + _vec(x2, y2) + ' m/s',
           'speed 1 = ' + _S(_mag(x1, y1)) + ' m/s',
           'speed 2 = ' + _S(_mag(x2, y2)) + ' m/s']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('smooth spheres: y parts unchanged'),
          _W('along x: v2 - v1 = e(u1 - u2) = ' + _S(sep)),
          _W('angle 1 = ' + _S(_dirdeg(x1, y1)) + ' deg to x'),
          _W('angle 2 = ' + _S(_dirdeg(x2, y2)) + ' deg to x')]
    wk.extend(_kewk(ke0, ke1))
    cav = [_C('x is the line of centres')]
    if u1[0] <= u2[0]:
        cav.append(_C('no approach along x: no impact'))
    return ans + wk + cav

def t_obliqueang(m1, u1, a1, m2, u2, a2, e):
    x1 = u1 * _cosd(a1)
    y1 = u1 * _sind(a1)
    x2 = u2 * _cosd(a2)
    y2 = u2 * _sind(a2)
    v1, v2, sep, ke0, ke1 = _oblique(m1, x1, y1, m2, x2, y2, e)
    ans = ['speed 1 = ' + _S(_mag(v1, y1)) + ' m/s',
           'angle 1 = ' + _S(_dirdeg(v1, y1)) + ' deg to LOC',
           'speed 2 = ' + _S(_mag(v2, y2)) + ' m/s',
           'angle 2 = ' + _S(_dirdeg(v2, y2)) + ' deg to LOC']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('along LOC: u1 = ' + _S(x1) + ', u2 = ' + _S(x2)),
          _W('perp parts ' + _S(y1) + ', ' + _S(y2) + ' unchanged'),
          _W('after: v1 = ' + _S(v1) + ', v2 = ' + _S(v2) + ' along LOC'),
          _W('impulse on 2 = ' + _S(m2 * (v2 - x2)) + ' N s along LOC')]
    wk.extend(_kewk(ke0, ke1))
    cav = [_C('angles from the line of centres')]
    if x1 <= x2:
        cav.append(_C('no approach along LOC: no impact'))
    return ans + wk + cav

def t_impulse1(m, u, v, t):
    _pos(m, 'm')
    j = m * (v - u)
    ans = ['J = ' + _S(j) + ' N s', 'change in p = ' + _S(j) + ' kg m/s']
    wk = [_W('J = mv - mu = ' + _S(m * v) + ' - ' + _S(m * u))]
    if t is not None:
        if t <= 0:
            raise ValueError('t must be > 0')
        ans.append('mean force = ' + _S(j / t) + ' N')
        wk.append(_W('F t = mv - mu, t = ' + _S(t) + ' s'))
    return ans + wk

def t_impulse2(m, u, v):
    _pos(m, 'm')
    jx = m * (v[0] - u[0])
    jy = m * (v[1] - u[1])
    mg = _mag(jx, jy)
    ans = ['J = ' + _vec(jx, jy) + ' N s', '|J| = ' + _S(mg) + ' N s']
    if mg > 0:
        ans.append('direction = ' + _S(_dirdeg(jx, jy)) + ' deg')
    return ans + [_W('J = m(v - u), component by component')]

def t_impulseF(F, t0, t1, m):
    _needvar(F, 't')
    a, b = _limits(t0, t1)
    i = _defi(F, a, b, 't')
    ans = ['I = ' + _S(i) + ' N s']
    wk = [_W('I = int F dt from ' + _S(a) + ' to ' + _S(b)),
          _W('F(t) = ' + caseng.tostr(F))]
    if m is not None:
        _pos(m, 'm')
        ans.append('change in v = ' + _S(i / m) + ' m/s')
        wk.append(_W('I = mv - mu'))
    return ans + wk

def t_three(mA, uA, mB, mC, e):
    _pos(mA, 'mA')
    _pos(mB, 'mB')
    _pos(mC, 'mC')
    _ck_e(e)
    if uA <= 0:
        raise ValueError('uA must be > 0')
    vA = uA * (mA - e * mB) / (mA + mB)
    vB = vA + e * uA
    vB2 = vB * (mB - e * mC) / (mB + mC)
    vC = vB2 + e * vB
    ans = ['A: ' + _S(vA) + ' m/s', 'B: ' + _S(vB2) + ' m/s',
           'C: ' + _S(vC) + ' m/s']
    wk = [_W('A hits B: vA = ' + _S(vA) + ', vB = ' + _S(vB)),
          _W('B hits C: vB = ' + _S(vB2) + ', vC = ' + _S(vC)),
          _W('B and C start at rest, same e twice')]
    cav = []
    if vB <= 0:
        cav.append(_C('B does not reach C'))
    elif vA > vB2 + 1e-12:
        cav.append(_C('A catches B again: a third impact'))
    if vB2 > vC + 1e-12:
        cav.append(_C('B still catches C: check the data'))
    return ans + wk + cav

# ---- G  centre of mass ---------------------------------------------------------
# Y421+Y431: MG1 systems of particles in 1, 2 and 3 dimensions, G3 standard
# bodies, G4 composite bodies. G2 (symmetry) is reasoning: no tool.
# Y421 only: G8 compound bodies as particles, MG6 volumes of revolution,
# G7 solids of revolution by calculus, G9 laminas and arcs by calculus,
# G10 equilibrium of rigid bodies (a body hanging from a point).
# G5 (toppling) is in section M.

def _comn(data, k, names):
    # k coordinates per part after the mass
    step = k + 1
    if len(data) < step or len(data) % step:
        raise ValueError('give m,' + ','.join(names) + ' for each part')
    tot = 0.0
    s = [0.0] * k
    i = 0
    while i < len(data):
        tot += data[i]
        j = 0
        while j < k:
            s[j] += data[i] * data[i + 1 + j]
            j += 1
        i += step
    if tot == 0:
        raise ValueError('total mass is zero')
    ans = []
    wk = []
    j = 0
    while j < k:
        ans.append(names[j] + ' bar = ' + _S(s[j] / tot))
        wk.append(_W('sum m ' + names[j] + ' = ' + _S(s[j])))
        j += 1
    ans.append('total mass = ' + _S(tot))
    wk.append(_W('bar = sum(m pos) / sum(m), ' + str(len(data) // step) +
                 ' parts'))
    return ans + wk + [_C('use a negative mass for a hole')]

def t_com1(data):
    return _comn(data, 1, ['x'])

def t_com(data):
    return _comn(data, 2, ['x', 'y'])

def t_com3(data):
    return _comn(data, 3, ['x', 'y', 'z'])

def t_centroids():
    return ['rod L: L/2 from an end',
            'triangle: h/3 above the base',
            'semicircle arc: 2r/pi',
            'semicircle lamina: 4r/(3pi)',
            'arc, half angle a: r sin a / a',
            'sector: 2r sin a / (3a)',
            'solid cone h: 3h/4 from apex',
            'hollow cone h: 2h/3 from apex',
            'solid hemisphere: 3r/8',
            'hollow hemisphere: r/2',
            _W('from the centre or apex, a in radians')]

def t_sector(r, angle):
    _pos(r, 'r')
    if angle <= 0 or angle > 180:
        raise ValueError('half angle is 0 to 180')
    a = casutil.rad(angle)
    s = _sinc(a)
    return ['sector = ' + _S(2.0 * r * s / 3.0),
            'arc = ' + _S(r * s),
            _W('sector 2r sin a/(3a), arc r sin a/a'),
            _W('half angle a = ' + _S(a) + ' rad'),
            _C('measured from the centre of the circle')]

def t_lamina(f, a, b):
    _needvar(f, 'x')
    a, b = _limits(a, b)
    ar = _defi(f, a, b, 'x')
    if ar == 0:
        raise ValueError('the area is zero')
    mx = _defi(('*', ('v', 'x'), f), a, b, 'x')
    my = _defi(('/', _sq(f), ('n', 2)), a, b, 'x')
    return ['x bar = ' + _S(mx / ar), 'y bar = ' + _S(my / ar),
            'area = ' + _S(ar),
            _W('A = int y dx = ' + _S(ar)),
            _W('int x y dx = ' + _S(mx)),
            _W('int y^2/2 dx = ' + _S(my)),
            _C('uniform lamina, y = ' + caseng.tostr(f))]

def t_between(f, gf, a, b):
    _needvar(f, 'x')
    _needvar(gf, 'x')
    a, b = _limits(a, b)
    d = ('-', f, gf)
    ar = _defi(d, a, b, 'x')
    if ar == 0:
        raise ValueError('the area is zero')
    mx = _defi(('*', ('v', 'x'), d), a, b, 'x')
    my = _defi(('/', ('-', _sq(f), _sq(gf)), ('n', 2)), a, b, 'x')
    return ['x bar = ' + _S(mx / ar), 'y bar = ' + _S(my / ar),
            'area = ' + _S(ar),
            _W('A = int (f - g) dx = ' + _S(ar)),
            _W('int x(f - g) dx = ' + _S(mx)),
            _W('int (f^2 - g^2)/2 dx = ' + _S(my)),
            _C('f must be the upper curve')]

def t_arc(f, a, b):
    _needvar(f, 'x')
    a, b = _limits(a, b)
    df = cascalc.tidy(caseng.diff(caseng.simplify(f), 'x'))
    ds = ('sqrt', ('+', ('n', 1), _sq(df)))
    ln = cascalc.defint(ds, a, b, False, 400, 'x')
    mx = cascalc.defint(('*', ('v', 'x'), ds), a, b, False, 400, 'x')
    my = cascalc.defint(('*', f, ds), a, b, False, 400, 'x')
    if ln is None or mx is None or my is None:
        raise ValueError('cannot integrate along that arc')
    if ln <= 0:
        raise ValueError('the arc has no length')
    return ['x bar = ' + _S(mx / ln), 'y bar = ' + _S(my / ln),
            'arc length = ' + _S(ln),
            _W('ds = sqrt(1 + (dy/dx)^2) dx'),
            _W('dy/dx = ' + caseng.tostr(df)),
            _W('int x ds = ' + _S(mx) + ', int y ds = ' + _S(my)),
            _C('uniform wire along y = ' + caseng.tostr(f))]

def t_revolve(f, a, b):
    _needvar(f, 'x')
    a, b = _limits(a, b)
    i0 = _defi(_sq(f), a, b, 'x')
    if i0 == 0:
        raise ValueError('the volume is zero')
    i1 = _defi(('*', ('v', 'x'), _sq(f)), a, b, 'x')
    return ['x bar = ' + _S(i1 / i0),
            'volume = ' + _S(math.pi * i0),
            'y bar = 0 by symmetry',
            _W('V = pi int y^2 dx, int y^2 = ' + _S(i0)),
            _W('x bar = int x y^2 / int y^2'),
            _W('int x y^2 dx = ' + _S(i1)),
            _C('about Ox, y = ' + caseng.tostr(f))]

def t_revolvey(f, a, b):
    _needvar(f, 'y')
    a, b = _limits(a, b)
    i0 = _defi(_sq(f), a, b, 'y')
    if i0 == 0:
        raise ValueError('the volume is zero')
    i1 = _defi(('*', ('v', 'y'), _sq(f)), a, b, 'y')
    return ['y bar = ' + _S(i1 / i0),
            'volume = ' + _S(math.pi * i0),
            'x bar = 0 by symmetry',
            _W('V = pi int x^2 dy, int x^2 = ' + _S(i0)),
            _W('y bar = int y x^2 / int x^2'),
            _W('int y x^2 dy = ' + _S(i1)),
            _C('about Oy, x = ' + caseng.tostr(f))]

def t_suspend(px, py, gx, gy):
    dx = gx - px
    dy = gy - py
    if dx == 0 and dy == 0:
        raise ValueError('G is at the point of suspension')
    if dy >= 0:
        raise ValueError('G must be below P: gy < py')
    tilt = casutil.deg(math.atan2(abs(dx), -dy))
    return ['y axis to vertical = ' + _S(tilt) + ' deg',
            'x axis to vertical = ' + _S(90.0 - tilt) + ' deg',
            _W('PG hangs vertically, PG = ' + _vec(dx, dy)),
            _W('tan = |dx|/|dy|, |PG| = ' + _S(_mag(dx, dy))),
            _C('P is the point of suspension')]

# ---- C  circular motion ----------------------------------------------------------
# Y421 only: r3 v^2/r and r omega^2, r4 horizontal circles (conical pendulum,
# banked and flat bends), r5 more than one force, r6 tangential
# acceleration, r7 vertical circles by energy, r8 leaving the circle.
# Mr1 (language) and r2 (identifying forces) have no tool.

def _spin(om, r):
    ans = ['omega = ' + _S(om) + ' rad/s',
           'rev/s = ' + _S(om / (2.0 * math.pi)),
           'rev/min = ' + _S(om * 30.0 / math.pi)]
    if om != 0:
        ans.append('period = ' + _S(2.0 * math.pi / abs(om)) + ' s')
    if r is not None:
        ans.append('v = r omega = ' + _S(r * om) + ' m/s')
        ans.append('a = r omega^2 = ' + _S(r * om * om) + ' m/s2')
    return ans

def t_angspeed(om, r):
    return _spin(om, r) + [_W('1 rev = 2 pi rad, T = 2 pi / omega')]

def t_rpm(rpm, r):
    return _spin(rpm * math.pi / 30.0, r) + [
        _W('omega = 2 pi N / 60, N = ' + _S(rpm)),
        _W('1 rev/min = pi/30 rad/s')]

def t_circ_v(m, v, r):
    _pos(r, 'r')
    a = v * v / r
    return ['a = ' + _S(a) + ' m/s2', 'F = ' + _S(m * a) + ' N',
            'omega = ' + _S(v / r) + ' rad/s',
            _W('a = v^2 / r, F = m a, v = r omega'),
            _C('a points at the centre')]

def t_circ_om(m, om, r):
    _pos(r, 'r')
    a = om * om * r
    return ['a = ' + _S(a) + ' m/s2', 'F = ' + _S(m * a) + ' N',
            'v = ' + _S(om * r) + ' m/s',
            _W('a = r omega^2, F = m a'),
            _C('omega must be in rad/s')]

def t_tangential(r, om, alpha):
    _pos(r, 'r')
    ar = om * om * r
    at = alpha * r
    tot = _mag(ar, at)
    ans = ['radial a = ' + _S(ar) + ' m/s2',
           'tangential a = ' + _S(at) + ' m/s2',
           'total a = ' + _S(tot) + ' m/s2']
    if tot > 0:
        ans.append('angle to radius = ' + _S(_acute(ar, at)) + ' deg')
    return ans + [_W('radial r omega^2, tangential r alpha = dv/dt'),
                  _W('v = r omega = ' + _S(r * om) + ' m/s'),
                  _C('alpha = d omega/dt in rad/s2')]

def t_circ_vec(r, om, t):
    _pos(r, 'r')
    th = om * t
    cx = r * math.cos(th)
    cy = r * math.sin(th)
    return ['r = ' + _vec(cx, cy) + ' m',
            'v = ' + _vec(-r * om * math.sin(th), r * om * math.cos(th)) +
            ' m/s',
            'a = ' + _vec(-om * om * cx, -om * om * cy) + ' m/s2',
            'angle = ' + _S(casutil.deg(th)) + ' deg',
            _W('r = (r cos wt, r sin wt), v = dr/dt'),
            _W('a = -omega^2 r, speed = ' + _S(abs(r * om)) + ' m/s'),
            _C('r.v = 0: v is along the tangent')]

def t_conical(m, l, angle, g):
    _pos(m, 'm')
    _pos(l, 'l')
    g = _g(g)
    if angle <= 0 or angle >= 90:
        raise ValueError('angle is 0 to 90 exclusive')
    ca = _cosd(angle)
    r = l * _sind(angle)
    om = math.sqrt(g / (l * ca))
    return ['T = ' + _S(m * g / ca) + ' N',
            'omega = ' + _S(om) + ' rad/s',
            'v = ' + _S(r * om) + ' m/s',
            'period = ' + _S(2.0 * math.pi / om) + ' s',
            'radius = ' + _S(r) + ' m',
            _W('T cos th = mg, T sin th = m r om^2'),
            _W('om^2 = g/(l cos th), g = ' + _S(g)),
            _C('the string is never horizontal')]

def t_conical_om(m, l, om, g):
    _pos(m, 'm')
    _pos(l, 'l')
    _pos(om, 'omega')
    g = _g(g)
    c = g / (l * om * om)
    if c >= 1.0:
        return ['it hangs straight down',
                _W('cos th = g/(l om^2) = ' + _S(c)),
                _C('omega too small to make a cone')]
    a = casutil.acos_safe(c)
    r = l * math.sin(a)
    return ['angle = ' + _S(casutil.deg(a)) + ' deg',
            'T = ' + _S(m * g / c) + ' N',
            'radius = ' + _S(r) + ' m',
            'v = ' + _S(r * om) + ' m/s',
            _W('cos th = g/(l omega^2) = ' + _S(c)),
            _W('T = mg / cos th, g = ' + _S(g))]

def t_conical2(m, a, b, h, om, g):
    # a = upper string, b = lower string, h apart on the rod
    _pos(m, 'm')
    _pos(a, 'a')
    _pos(b, 'b')
    _pos(h, 'h')
    g = _g(g)
    if a + b <= h or abs(a - b) >= h:
        raise ValueError('these strings cannot both be taut')
    y = (a * a - b * b + h * h) / (2.0 * h)
    rr = a * a - y * y
    if rr <= 0:
        raise ValueError('no circle fits those lengths')
    r = math.sqrt(rr)
    A = m * (g + om * om * (h - y)) / h
    T1 = a * A
    T2 = b * (m * om * om - A)
    ans = ['upper T = ' + _S(T1) + ' N', 'lower T = ' + _S(T2) + ' N',
           'radius = ' + _S(r) + ' m', 'v = ' + _S(r * om) + ' m/s']
    wk = [_W('T1/a + T2/b = m omega^2'),
          _W('T1 y/a - T2 (h-y)/b = mg'),
          _W('y = ' + _S(y) + ' m below the top, g = ' + _S(g))]
    cav = []
    if T2 < 0:
        cav.append(_C('lower string slack: omega too small'))
    if T1 < 0:
        cav.append(_C('upper string slack: impossible'))
    return ans + wk + cav

def t_bank(r, angle, mu, g):
    _pos(r, 'r')
    g = _g(g)
    if angle <= 0 or angle >= 90:
        raise ValueError('angle is 0 to 90 exclusive')
    a = casutil.rad(angle)
    ta = math.tan(a)
    ans = ['design speed = ' + _S(math.sqrt(g * r * ta)) + ' m/s']
    wk = [_W('no friction: tan th = v^2/(r g)'),
          _W('g = ' + _S(g) + ', tan th = ' + _S(ta))]
    cav = []
    if mu is not None:
        _ck_mu(mu)
        dn = 1.0 - mu * ta
        lo = g * r * (ta - mu) / (1.0 + mu * ta)
        ans.append('min speed = ' +
                   _S(math.sqrt(lo) if lo > 0 else 0.0) + ' m/s')
        if dn <= 0:
            cav.append(_C('no upper limit: mu tan th >= 1'))
        else:
            ans.append('max speed = ' +
                       _S(math.sqrt(g * r * (ta + mu) / dn)) + ' m/s')
        wk.append(_W('v^2 = g r (tan + mu)/(1 - mu tan)'))
        if lo <= 0:
            cav.append(_C('it never slips down the bank'))
    return ans + wk + cav

def t_bankfr(m, r, v, angle, g):
    _pos(m, 'm')
    _pos(r, 'r')
    g = _g(g)
    sa = _sind(angle)
    ca = _cosd(angle)
    N = m * (v * v * sa / r + g * ca)
    F = m * (g * sa - v * v * ca / r)
    ans = ['N = ' + _S(N) + ' N', 'friction = ' + _S(abs(F)) + ' N']
    if N > 0:
        ans.append('mu needed = ' + _S(abs(F) / N))
    wk = [_W('N sin - F cos = mv^2/r'),
          _W('N cos + F sin = mg, g = ' + _S(g)),
          _W('F up the slope = ' + _S(F) + ' N')]
    if F > 1e-12:
        cav = [_C('friction acts up the slope')]
    elif F < -1e-12:
        cav = [_C('friction acts down the slope')]
    else:
        cav = [_C('design speed: no friction needed')]
    return ans + wk + cav

def t_rough(m, r, mu, g):
    _pos(m, 'm')
    _pos(r, 'r')
    _ck_mu(mu)
    g = _g(g)
    v = math.sqrt(mu * g * r)
    return ['max speed = ' + _S(v) + ' m/s',
            'max omega = ' + _S(v / r) + ' rad/s',
            'friction = ' + _S(mu * m * g) + ' N',
            _W('m v^2/r <= mu m g, so v^2 <= mu g r'),
            _W('g = ' + _S(g) + ', the mass cancels'),
            _C('flat rough bend or table, no string')]

def t_vcircle(m, r, u, angle, g):
    _pos(m, 'm')
    _pos(r, 'r')
    g = _g(g)
    ca = _cosd(angle)
    s = u * u - 2.0 * g * r * (1.0 - ca)
    ans = []
    cav = []
    if s < 0:
        ans.append('v = 0 m/s')
        cav.append(_C('it never reaches that angle'))
    else:
        ans.append('v = ' + _S(math.sqrt(s)) + ' m/s')
        ans.append('T = ' + _S(m * s / r + m * g * ca) + ' N')
    if u * u >= 5.0 * g * r:
        ans.append('completes the circle')
        ans.append('v at top = ' + _S(math.sqrt(u * u - 4.0 * g * r)) + ' m/s')
    elif u * u <= 2.0 * g * r:
        c = 1.0 - u * u / (2.0 * g * r)
        ans.append('oscillates, stops at ' +
                   _S(casutil.deg(casutil.acos_safe(c))) + ' deg')
        cav.append(_C('stays below the centre, string taut'))
    else:
        c = (2.0 * g * r - u * u) / (3.0 * g * r)
        ans.append('goes slack at ' +
                   _S(casutil.deg(casutil.acos_safe(c))) + ' deg')
        cav.append(_C('string goes slack before the top'))
    wk = [_W('v^2 = u^2 - 2gr(1 - cos th), th from bottom'),
          _W('T = mv^2/r + mg cos th, g = ' + _S(g)),
          _W('tangential a = g sin th = ' + _S(g * _sind(angle)) + ' m/s2'),
          _W('completes if u^2 >= 5gr = ' + _S(5.0 * g * r))]
    return ans + wk + cav

def t_vrod(m, r, u, angle, g):
    _pos(m, 'm')
    _pos(r, 'r')
    g = _g(g)
    ca = _cosd(angle)
    s = u * u - 2.0 * g * r * (1.0 - ca)
    ans = []
    cav = []
    if s < 0:
        ans.append('v = 0 m/s')
        cav.append(_C('it never reaches that angle'))
    else:
        f = m * s / r + m * g * ca
        ans.append('v = ' + _S(math.sqrt(s)) + ' m/s')
        ans.append('force in rod = ' + _S(abs(f)) + ' N')
        ans.append('tension' if f >= 0 else 'thrust')
    if u * u >= 4.0 * g * r:
        ans.append('completes: u^2 >= 4gr = ' + _S(4.0 * g * r))
    else:
        c = 1.0 - u * u / (2.0 * g * r)
        if c >= 1.0:
            cav.append(_C('u = 0: it does not move'))
        else:
            ans.append('stops at ' +
                       _S(casutil.deg(casutil.acos_safe(c))) + ' deg')
            cav.append(_C('falls back: u^2 < 4gr'))
    wk = [_W('v^2 = u^2 - 2gr(1 - cos th)'),
          _W('F = mv^2/r + mg cos th, g = ' + _S(g)),
          _W('tangential a = g sin th = ' + _S(g * _sind(angle)) + ' m/s2'),
          _W('a rod can push, so it needs only v >= 0 up top')]
    return ans + wk + cav

def t_sphereout(r, u, g):
    _pos(r, 'r')
    g = _g(g)
    c = (u * u + 2.0 * g * r) / (3.0 * g * r)
    if c >= 1.0:
        return ['it leaves at once',
                _W('cos th = (u^2 + 2gr)/(3gr) = ' + _S(c)),
                _W('needs u^2 < gr = ' + _S(g * r)),
                _C('u is already too fast at the top')]
    a = casutil.acos_safe(c)
    return ['leaves at ' + _S(casutil.deg(a)) + ' deg',
            'speed there = ' + _S(math.sqrt(u * u + 2.0 * g * r * (1.0 - c))) +
            ' m/s',
            'height dropped = ' + _S(r * (1.0 - c)) + ' m',
            'height above centre = ' + _S(r * c) + ' m',
            _W('N = 0 when 3 g r cos th = u^2 + 2 g r'),
            _W('cos th = ' + _S(c) + ', g = ' + _S(g) + ', mass cancels'),
            _C('th is measured from the top')]

# ---- H  Hooke's law and elastic energy ---------------------------------------------
# Y421 only: h2 Hooke's law, h3 stiffness or modulus, h4 tension, h5
# equilibrium position, h6 elastic energy, h7 energy with strings and
# springs. Mh1 (language) and h8 (when Hooke fails) have no tool.

def t_hooke_k(k, x):
    return ['T = ' + _S(k * x) + ' N',
            'EPE = ' + _S(0.5 * k * x * x) + ' J',
            _W('T = k x = ' + _S(k) + ' x ' + _S(x)),
            _W('EPE = 0.5 k x^2'),
            _C('a string pulls only while x > 0')]

def t_hooke_lam(lam, l, x):
    _pos(l, 'l')
    return ['T = ' + _S(lam * x / l) + ' N',
            'EPE = ' + _S(lam * x * x / (2.0 * l)) + ' J',
            'k = ' + _S(lam / l) + ' N/m',
            _W('T = lam x / l, EPE = lam x^2/(2l)'),
            _C('lam is a force, k = lam / l')]

def t_hooke_find(T, lam, l, x):
    k = _unknown([T, lam, l, x])
    if k == 0:
        T = lam * x / _pos(l, 'l')
    elif k == 1:
        lam = T * _pos(l, 'l') / _nz(x, 'x')
    elif k == 2:
        l = lam * x / _nz(T, 'T')
    else:
        x = T * _pos(l, 'l') / _nz(lam, 'lam')
    got = [T, lam, l, x][k]
    ans = [['T', 'lam', 'l', 'x'][k] + ' = ' + _S(got) + ' ' +
           ['N', 'N', 'm', 'm'][k]]
    cav = []
    if l > 0:
        ans.append('k = lam/l = ' + _S(lam / l) + ' N/m')
    else:
        cav.append(_C('l came out <= 0: check the signs'))
    return ans + [_W('T = lam x / l'),
                  _W(_S(T) + ' = ' + _S(lam) + ' x ' + _S(x) + ' / ' +
                     _S(l))] + cav

def t_modulus(m, l, x, g):
    _pos(m, 'm')
    _pos(l, 'l')
    _pos(x, 'x')
    g = _g(g)
    lam = m * g * l / x
    return ['lam = ' + _S(lam) + ' N',
            'k = ' + _S(lam / l) + ' N/m',
            'T = mg = ' + _S(m * g) + ' N',
            _W('hanging: mg = lam x / l, so lam = m g l / x'),
            _W('g = ' + _S(g)),
            _C('x is the equilibrium extension')]

def t_elastic_eq(m, lam, l, g):
    _pos(m, 'm')
    _pos(lam, 'lam')
    _pos(l, 'l')
    g = _g(g)
    x = m * g * l / lam
    return ['extension = ' + _S(x) + ' m',
            'T = mg = ' + _S(m * g) + ' N',
            'total length = ' + _S(l + x) + ' m',
            'EPE = ' + _S(lam * x * x / (2.0 * l)) + ' J',
            _W('mg = lam x / l, so x = m g l / lam'),
            _W('g = ' + _S(g))]

def t_elastic_max(m, lam, l, v, g):
    _pos(m, 'm')
    _pos(lam, 'lam')
    _pos(l, 'l')
    g = _g(g)
    q = l * m * g / lam
    x = q + math.sqrt(q * q + l * m * v * v / lam)
    return ['max extension = ' + _S(x) + ' m',
            'total length = ' + _S(l + x) + ' m',
            'EPE = ' + _S(lam * x * x / (2.0 * l)) + ' J',
            'equilibrium x = ' + _S(q) + ' m',
            _W('0.5mv^2 + mgx = lam x^2/(2l)'),
            _W('KE = ' + _S(0.5 * m * v * v) + ' J, GPE = ' +
               _S(m * g * x) + ' J'),
            _W('g = ' + _S(g)),
            _C('v is the speed as the string goes taut')]

def t_elastic_v(m, lam, l, x0, v0, x1):
    _pos(m, 'm')
    _pos(lam, 'lam')
    _pos(l, 'l')
    e0 = lam * x0 * x0 / (2.0 * l)
    e1 = lam * x1 * x1 / (2.0 * l)
    s = v0 * v0 + 2.0 * (e0 - e1) / m
    wk = [_W('0.5mv^2 + lam x^2/(2l) is constant'),
          _W('EPE ' + _S(e0) + ' J -> ' + _S(e1) + ' J')]
    if s < 0:
        amp = math.sqrt(x0 * x0 + m * v0 * v0 * l / lam)
        return ['it never reaches x = ' + _S(x1),
                'max |x| = ' + _S(amp) + ' m'] + wk
    return ['v = ' + _S(math.sqrt(s)) + ' m/s'] + wk + \
           [_C('smooth horizontal spring; x < 0 compresses')]

# ---- V  vectors and variable forces -------------------------------------------------
# Y421 only: Mk1 2-D position and relative position, k2 2-D kinematics by
# calculus and constant acceleration, Mv1 variable acceleration by
# calculus, v2 force from the motion, Mv3 eliminate the parameter, v4 the
# bounding parabola, v5 cartesian path of a projectile, v6 range on an
# inclined plane, v7 maximum range, v9 verify a solution of a DE of motion,
# v10 constants from initial conditions, v11 the SHM equation, v12 SHM
# amplitude and period. Mv8 (forming a DE) is modelling: no tool.

def _needt(tree, allowed):
    for v in caseng.vars_in(tree):
        if v not in allowed:
            raise ValueError('use ' + ', '.join(allowed) + ' only')

def t_rdiff(x, y, t):
    _needt(x, ['t'])
    _needt(y, ['t'])
    vx = _dt(x)
    vy = _dt(y)
    ax = _dt(vx)
    ay = _dt(vy)
    ans = ['vx = ' + _str(vx), 'vy = ' + _str(vy),
           'ax = ' + _str(ax), 'ay = ' + _str(ay)]
    wk = [_W('v = dr/dt, a = dv/dt, each part')]
    if t is not None:
        e = {'t': t}
        px = _evt(x, e)
        py = _evt(y, e)
        qx = _evt(vx, e)
        qy = _evt(vy, e)
        bx = _evt(ax, e)
        by = _evt(ay, e)
        ans.append('r = ' + _vec(px, py) + ' m')
        ans.append('v = ' + _vec(qx, qy) + ' m/s')
        ans.append('speed = ' + _S(_mag(qx, qy)) + ' m/s')
        ans.append('a = ' + _vec(bx, by) + ' m/s2')
        wk.append(_W('at t = ' + _S(t) + ', |a| = ' + _S(_mag(bx, by))))
        if _mag(qx, qy) > 0:
            wk.append(_W('moving at ' + _S(_dirdeg(qx, qy)) + ' deg to x'))
    return ans + wk

def t_aint(ax, ay, u, r0, t):
    _needt(ax, ['t'])
    _needt(ay, ['t'])
    vx = _shift(_anti(ax), u[0], 0.0)
    vy = _shift(_anti(ay), u[1], 0.0)
    rx = _shift(_anti(vx), r0[0], 0.0)
    ry = _shift(_anti(vy), r0[1], 0.0)
    ans = ['vx = ' + _str(vx), 'vy = ' + _str(vy),
           'x = ' + _str(rx), 'y = ' + _str(ry)]
    wk = [_W('v = int a dt + c, c from v(0) = ' + _vec(u[0], u[1])),
          _W('r = int v dt + c, c from r(0) = ' + _vec(r0[0], r0[1]))]
    if t is not None:
        e = {'t': t}
        qx = _evt(vx, e)
        qy = _evt(vy, e)
        ans.append('v = ' + _vec(qx, qy) + ' m/s')
        ans.append('speed = ' + _S(_mag(qx, qy)) + ' m/s')
        ans.append('r = ' + _vec(_evt(rx, e), _evt(ry, e)) + ' m')
    return ans + wk

def t_vsuvat(r0, u, a, t):
    rx = r0[0] + u[0] * t + 0.5 * a[0] * t * t
    ry = r0[1] + u[1] * t + 0.5 * a[1] * t * t
    vx = u[0] + a[0] * t
    vy = u[1] + a[1] * t
    return ['r = ' + _vec(rx, ry) + ' m',
            'v = ' + _vec(vx, vy) + ' m/s',
            'speed = ' + _S(_mag(vx, vy)) + ' m/s',
            'distance from O = ' + _S(_mag(rx, ry)) + ' m',
            _W('r = r0 + u t + a t^2/2, v = u + a t'),
            _C('constant acceleration only')]

def t_force(m, x, y, t):
    _pos(m, 'm')
    _needt(x, ['t'])
    _needt(y, ['t'])
    ax = _dt(_dt(x))
    ay = _dt(_dt(y))
    e = {'t': t}
    fx = m * _evt(ax, e)
    fy = m * _evt(ay, e)
    F = _mag(fx, fy)
    ans = ['F = ' + _vec(fx, fy) + ' N', '|F| = ' + _S(F) + ' N']
    if F > 0:
        ans.append('direction = ' + _S(_dirdeg(fx, fy)) + ' deg')
    return ans + [_W('a = d2r/dt2 = (' + _str(ax) + ', ' + _str(ay) + ')'),
                  _W('F = m a at t = ' + _S(t)),
                  _C('F is the resultant force')]

def t_relative(rA, vA, rB, vB):
    rx = rB[0] - rA[0]
    ry = rB[1] - rA[1]
    vx = vB[0] - vA[0]
    vy = vB[1] - vA[1]
    sp = _mag(vx, vy)
    ans = ['r of B rel A = ' + _vec(rx, ry),
           'v of B rel A = ' + _vec(vx, vy),
           'distance now = ' + _S(_mag(rx, ry)) + ' m',
           'relative speed = ' + _S(sp) + ' m/s']
    wk = [_W('B rel A = B - A, for r and for v')]
    if sp > 0:
        ts = -(rx * vx + ry * vy) / (sp * sp)
        cav = []
        if ts < 0:
            ts = 0.0
            cav.append(_C('moving apart: closest now'))
        cx = rx + vx * ts
        cy = ry + vy * ts
        ans.append('closest at t = ' + _S(ts) + ' s')
        ans.append('least distance = ' + _S(_mag(cx, cy)) + ' m')
        wk.append(_W('min |r + v t|: t = -r.v / |v|^2'))
        wk.append(_W('v rel at ' + _S(_dirdeg(vx, vy)) + ' deg to x'))
        return ans + wk + cav
    return ans + wk + [_C('same velocity: distance fixed')]

def t_avf(f, v0, v1):
    _needvar(f, 'v')
    if v0 == v1:
        raise ValueError('v0 and v1 are equal')
    lo, hi = _limits(v0, v1)
    i = 0
    prev = None
    while i <= 40:
        vv = lo + (hi - lo) * i / 40.0
        try:
            fv = _evt(f, {'v': vv})
        except ValueError:
            fv = None
        if fv is not None:
            if fv == 0 or (prev is not None and (prev > 0) != (fv > 0)):
                raise ValueError('a = 0 between: v1 not reached')
            prev = fv
        i += 1
    tt = _defi(('/', ('n', 1), f), lo, hi, 'v')
    xx = _defi(('/', ('v', 'v'), f), lo, hi, 'v')
    if v1 < v0:
        tt = -tt
        xx = -xx
    ans = ['time = ' + _S(tt) + ' s', 'distance = ' + _S(xx) + ' m']
    cav = []
    if tt < 0:
        cav.append(_C('t < 0: a pushes v away from v1'))
    return ans + [_W('dv/dt = f(v): t = int 1/f(v) dv'),
                  _W('v dv/dx = f(v): x = int v/f(v) dv'),
                  _W('from v = ' + _S(v0) + ' to ' + _S(v1))] + cav

def _signed(c, s):
    if c < 0:
        return ' - ' + _S(-c) + s
    return ' + ' + _S(c) + s

def t_projpath(u, angle, g):
    _pos(u, 'u')
    g = _g(g)
    if angle <= -90 or angle >= 90:
        raise ValueError('angle is -90 to 90 exclusive')
    ca = _cosd(angle)
    ta = math.tan(casutil.rad(angle))
    k = g / (2.0 * u * u * ca * ca)
    sa = _sind(angle)
    if abs(ta) < 1e-12:
        lin = ''
    elif abs(ta - 1) < 1e-12:
        lin = 'x - '
    elif abs(ta + 1) < 1e-12:
        lin = '-x - '
    else:
        lin = _S(ta) + 'x - '
    ans = ['y = ' + (lin if lin else '-') + _S(k) + 'x^2']
    if sa > 0:
        ans.append('range = ' + _S(2.0 * u * u * sa * ca / g) + ' m')
        ans.append('max height = ' + _S(u * u * sa * sa / (2.0 * g)) + ' m')
        ans.append('time of flight = ' + _S(2.0 * u * sa / g) + ' s')
    return ans + [
        _W('x = u cos a t, so t = x/(u cos a)'),
        _W('y = u sin a t - g t^2/2, substitute for t'),
        _W('y = x tan a - g x^2/(2u^2 cos^2 a)'),
        _W('= x tan a - g x^2 (1 + tan^2 a)/(2u^2)'),
        _W('bounding: y = ' + _S(u * u / (2.0 * g)) + ' - ' +
           _S(g / (2.0 * u * u)) + 'x^2'),
        _C('launched from O, g = ' + _S(g))]

def t_projpt(u, x, y, g):
    _pos(u, 'u')
    _pos(x, 'x')
    g = _g(g)
    aa = g * x * x / (2.0 * u * u)
    disc = x * x - 4.0 * aa * (y + aa)
    wk = [_W('y = x T - g x^2 (1 + T^2)/(2u^2), T = tan a'),
          _W(_S(aa) + 'T^2 - ' + _S(x) + 'T' + _signed(y + aa, '') +
             ' = 0'),
          _W('discriminant = ' + _S(disc))]
    if disc < 0:
        return ['out of reach'] + wk + \
               [_C('above the bounding parabola')]
    r = math.sqrt(disc)
    a1 = casutil.deg(math.atan((x + r) / (2.0 * aa)))
    a2 = casutil.deg(math.atan((x - r) / (2.0 * aa)))
    if r == 0:
        return ['angle = ' + _S(a1) + ' deg'] + wk + \
               [_C('one angle: on the bounding parabola')]
    return ['low angle = ' + _S(a2) + ' deg',
            'high angle = ' + _S(a1) + ' deg'] + wk

def t_bounding(u, x, g):
    _pos(u, 'u')
    g = _g(g)
    c = u * u / (2.0 * g)
    k = g / (2.0 * u * u)
    ans = ['y = ' + _S(c) + ' - ' + _S(k) + 'x^2',
           'max reach on level = ' + _S(u * u / g) + ' m']
    wk = [_W('T^2 quadratic has a repeated root on it'),
          _W('points above it cannot be reached')]
    if x is not None:
        ans.append('highest at x: y = ' + _S(c - k * x * x) + ' m')
        if x != 0:
            ans.append('angle = ' +
                       _S(casutil.deg(math.atan(u * u / (g * x)))) + ' deg')
            wk.append(_W('tan a = u^2/(g x) there'))
    return ans + wk + [_C('all launch angles, speed u from O')]

def t_incline(u, angle, slope, g):
    _pos(u, 'u')
    g = _g(g)
    if slope <= -90 or slope >= 90:
        raise ValueError('slope is -90 to 90')
    if angle <= -90 or angle >= 90:
        raise ValueError('angle is -90 to 90')
    cb = _cosd(slope)
    s = _sind(angle - slope)
    if s <= 0:
        raise ValueError('aim above the slope: angle > slope')
    tof = 2.0 * u * s / (g * cb)
    rr = 2.0 * u * u * _cosd(angle) * s / (g * cb * cb)
    return ['time of flight = ' + _S(tof) + ' s',
            'range along plane = ' + _S(rr) + ' m',
            'horizontal range = ' + _S(rr * cb) + ' m',
            'best angle = ' + _S(45.0 + slope / 2.0) + ' deg',
            'max range = ' + _S(u * u / (g * (1.0 + _sind(slope)))) + ' m',
            _W('axes along/perp to the plane: perp motion'),
            _W('u sin(a-b) t - g cos b t^2/2 = 0'),
            _W('R = 2u^2 cos a sin(a-b)/(g cos^2 b)'),
            _C('angles from horizontal; slope < 0 is down')]

def t_maxrange(u, slope, g):
    _pos(u, 'u')
    g = _g(g)
    if slope < 0 or slope >= 90:
        raise ValueError('slope is 0 to 90')
    sb = _sind(slope)
    return ['up: ' + _S(u * u / (g * (1.0 + sb))) + ' m at ' +
            _S(45.0 + slope / 2.0) + ' deg',
            'down: ' + _S(u * u / (g * (1.0 - sb))) + ' m at ' +
            _S(45.0 - slope / 2.0) + ' deg',
            _W('R = u^2 (sin(2a - b) - sin b)/(g cos^2 b)'),
            _W('max when 2a - b = 90: R = u^2/(g(1 + sin b))'),
            _C('angles above the horizontal')]

def t_shm(k, x0, v0, t):
    _pos(k, 'k')
    om = math.sqrt(k)
    b = v0 / om
    amp = _mag(x0, b)
    ans = ['omega = ' + _S(om) + ' rad/s',
           'period = ' + _S(2.0 * math.pi / om) + ' s',
           'amplitude = ' + _S(amp),
           'x = ' + _S(x0) + 'cos(' + _S(om) + 't)' +
           _signed(b, 'sin(' + _S(om) + 't)'),
           'max speed = ' + _S(om * amp),
           'max accel = ' + _S(k * amp)]
    wk = [_W('x = A cos wt + B sin wt, w^2 = k'),
          _W('A = x(0), B = v(0)/w'),
          _W('= R cos(wt - phi), R = ' + _S(amp) + ', phi = ' +
             _S(math.atan2(b, x0)) + ' rad')]
    if t is not None:
        c = math.cos(om * t)
        s = math.sin(om * t)
        ans.append('x(' + _S(t) + ') = ' + _S(x0 * c + b * s))
        ans.append('v(' + _S(t) + ') = ' + _S(om * (b * c - x0 * s)))
    return ans + wk + [_C("x'' = -k x, x from the centre")]

def t_shmv(om, a, x):
    _pos(om, 'omega')
    _pos(a, 'a')
    if abs(x) > a:
        raise ValueError('|x| cannot exceed a')
    return ['v = ' + _S(om * math.sqrt(a * a - x * x)),
            'accel = ' + _S(-om * om * x),
            'period = ' + _S(2.0 * math.pi / om) + ' s',
            'max speed = ' + _S(om * a),
            _W('v^2 = w^2 (a^2 - x^2), accel = -w^2 x'),
            _C('speed either way; accel to the centre')]

_CVALS = [1.3, -0.7, 0.9, 2.1, -1.6, 0.45, 1.75, -2.3]
_TS = [0.13, 0.57, 1.01, 1.72, 2.39, 3.3]

def _envs(trees, fixed):
    # every name other than the fixed ones gets a sample value
    names = []
    for tr in trees:
        for v in caseng.vars_in(tr):
            if v not in fixed and v not in names:
                names.append(v)
    names.sort()
    env = {}
    i = 0
    while i < len(names):
        env[names[i]] = _CVALS[i % len(_CVALS)]
        i += 1
    return (names, env)

def _verify(checks):
    # checks: list of (lhs, rhs) value pairs, or None where undefined
    n = 0
    for pr in checks:
        if pr is None:
            continue
        n += 1
        lhs, rhs = pr
        if abs(lhs - rhs) > 1e-7 * (1.0 + abs(lhs) + abs(rhs)):
            return (n, pr)
    if n == 0:
        raise ValueError('cannot evaluate at any test t')
    return (n, None)

def _verdict(n, bad, names):
    if bad is None:
        ans = ['satisfies the DE']
        wk = [_W('checked at ' + str(n) + ' values of t')]
    else:
        ans = ['does NOT satisfy the DE']
        wk = [_W('LHS ' + _S(bad[0]) + ' vs RHS ' + _S(bad[1]))]
    cav = []
    if names:
        cav.append(_C('constants ' + ', '.join(names) + ' kept general'))
    return ans, wk, cav

def t_verify2(x, f):
    for v in caseng.vars_in(x):
        if v in ('x', 'v'):
            raise ValueError('x(t) must not use x or v')
    names, env = _envs([x, f], ['t', 'x', 'v'])
    dx = _dt(x)
    d2 = _dt(dx)
    checks = []
    for tv in _TS:
        e = dict(env)
        e['t'] = tv
        try:
            X = _evt(x, e)
            V = _evt(dx, e)
            A = _evt(d2, e)
            e['x'] = X
            e['v'] = V
            checks.append((A, _evt(f, e)))
        except ValueError:
            checks.append(None)
    n, bad = _verify(checks)
    ans, wk, cav = _verdict(n, bad, names)
    return ans + [_W("x' = " + _str(dx)), _W("x'' = " + _str(d2)),
                  _W("DE: x'' = " + _str(f) + ", v = x'")] + wk + cav

def t_verify1(x, f):
    for v in caseng.vars_in(x):
        if v == 'x':
            raise ValueError('x(t) must not use x')
    names, env = _envs([x, f], ['t', 'x'])
    dx = _dt(x)
    checks = []
    for tv in _TS:
        e = dict(env)
        e['t'] = tv
        try:
            X = _evt(x, e)
            V = _evt(dx, e)
            e['x'] = X
            checks.append((V, _evt(f, e)))
        except ValueError:
            checks.append(None)
    n, bad = _verify(checks)
    ans, wk, cav = _verdict(n, bad, names)
    return ans + [_W("x' = " + _str(dx)),
                  _W("DE: x' = " + _str(f))] + wk + cav

def _num(v):
    v = casutil.clean(v)
    if isinstance(v, float):
        r = math.floor(v + 0.5)
        if abs(v - r) < 1e-9:
            v = int(r)
    return ('n', v)

def t_consts2(x, t0, x0, v0):
    _needt(x, ['t', 'a', 'b'])
    dx = _dt(x)

    def at(tree, a, b):
        return _evt(tree, {'t': t0, 'a': a, 'b': b})
    X0 = at(x, 0.0, 0.0)
    V0 = at(dx, 0.0, 0.0)
    Xa = at(x, 1.0, 0.0) - X0
    Va = at(dx, 1.0, 0.0) - V0
    Xb = at(x, 0.0, 1.0) - X0
    Vb = at(dx, 0.0, 1.0) - V0
    chk = at(x, 2.0, 3.0) - (X0 + 2 * Xa + 3 * Xb)
    if abs(chk) > 1e-7 * (1 + abs(X0) + abs(Xa) + abs(Xb)):
        raise ValueError('x(t) must be linear in a and b')
    det = Xa * Vb - Xb * Va
    if abs(det) < 1e-12:
        raise ValueError('a and b are not determined')
    p = x0 - X0
    q = v0 - V0
    a = (p * Vb - q * Xb) / det
    b = (Xa * q - Va * p) / det
    part = cascalc.tidy(caseng.subst(caseng.subst(x, 'a', _num(a)),
                                     'b', _num(b)))
    return ['a = ' + _F(a), 'b = ' + _F(b), 'x =', casutil.m(part),
            _W("x' = " + _str(dx)),
            _W('x(' + _S(t0) + ') = ' + _S(x0) + ", x'(" + _S(t0) +
               ') = ' + _S(v0)),
            _W('two linear equations in a and b')]

def t_const1(x, t0, x0):
    _needt(x, ['t', 'c'])

    def fc(c):
        return _evt(x, {'t': t0, 'c': c}) - x0
    c = None
    try:
        f0 = fc(0.0)
        f1 = fc(1.0)
        f2 = fc(2.0)
        if abs(f2 - 2 * f1 + f0) < 1e-9 * (1 + abs(f0) + abs(f1)):
            if abs(f1 - f0) < 1e-12:
                raise ValueError('c does not appear at t0')
            c = -f0 / (f1 - f0)
    except ValueError as e:
        if str(e) == 'c does not appear at t0':
            raise
        c = None
    if c is None:
        for c0 in (1.0, 0.5, 2.0, -1.0, 0.1, 5.0, -3.0):
            cc = c0
            k = 0
            while k < 60:
                try:
                    y = fc(cc)
                    h = 1e-6 * (1 + abs(cc))
                    dy = (fc(cc + h) - y) / h
                except ValueError:
                    break
                if abs(y) < 1e-11 * (1 + abs(x0)):
                    c = cc
                    break
                if dy == 0:
                    break
                cc = cc - y / dy
                k += 1
            if c is not None:
                break
    if c is None:
        raise ValueError('no c found near 0 to 5')
    part = cascalc.tidy(caseng.subst(x, 'c', _num(c)))
    return ['c = ' + _F(c), 'x =', casutil.m(part),
            _W('solve x(' + _S(t0) + ') = ' + _S(x0) + ' for c')]

SECTIONS = [
    ('D', 'Dimensional analysis', [
        ('Dimensions list', '', t_dimlist),
        ('Name from M,L,T', 'M,L,T', t_dimname),
        ('Dims of a product', 'M L T power*', t_dimprod),
        ('Check consistency', 'lhs[3],rhs[3]', t_dimcheck),
        ('Find powers a,b,c', 'Q[3],A[3],B[3],C[3]', t_dimpow),
        ('Change of units', 'value,M,L,T,kg,m,s', t_units),
    ]),
    ('F', 'Forces and friction', [
        ('Resultant of forces', 'F angle pairs*', t_resultant),
        ('Resolve along a line', 'F,angle,line', t_resolve),
        ('Two unknown forces', 'p,q,F angle pairs*', t_twoforce),
        ('Triangle of forces', 'F1,F2,F3', t_triforce),
        ('mu = tan(angle)', 'mu,angle', t_mutan),
        ('Rough slope, force F', 'm,angle,mu,F,g?', t_slope),
        ('Force range to hold', 'm,angle,mu,beta?,g?', t_hold),
        ('Friction, level ground', 'm,mu,P,angle?,g?', t_frich),
    ]),
    ('M', 'Moments and rigid bodies', [
        ('Forces and moments', 'Fx Fy x y*', t_moments),
        ('Couple', 'F,d,p?', t_couple),
        ('Beam on two supports', 'L,W,a,b,P,x', t_beam),
        ('Ladder, smooth wall', 'L,W,x,Wp,mu,angle?', t_ladder),
        ('Rod, hinge and string', 'L,W,d,alpha,P,x', t_hinge),
        ('Slide or topple, slope', 'a,h,mu,angle?', t_topple),
        ('Push a block', 'W,base,y,mu', t_push),
    ]),
    ('W', 'Work, energy and power', [
        ('Work F d cos th', 'F,d,angle', t_workfd),
        ('Work F.d vectors', 'F[3],d[3]', t_workdot),
        ('Work of F(x)', 'F(x),a,b,m?,u?', t_varwork),
        ('KE and GPE change', 'm,u,v,h,g?', t_energy),
        ('Speed after a drop', 'u,h,g?', t_dropspeed),
        ('Energy vs resistance', 'm,u,v,h,F,d,g?', t_energyres),
        ('Power P = F v', 'P,F,v', t_power),
        ('Power, F at an angle', 'F,v,angle', t_powang),
        ('Max speed on a slope', 'P,m,R,angle,g?', t_slopemax),
        ('Accel at speed v', 'P,m,R,angle,v,g?', t_slopeacc),
    ]),
    ('I', 'Impulse and momentum', [
        ('Conservation 1D', 'm1,u1,m2,u2,v1,v2', t_cons1d),
        ('Coalesce, one mass', 'm1,u1,m2,u2', t_coalesce),
        ('Direct impact, e', 'm1,u1,m2,u2,e', t_direct),
        ('Find e', 'u1,u2,v1,v2', t_finde),
        ('Ball bouncing', 'h,e,g?', t_bounce),
        ('Wall: speed and angle', 'u,angle,e,m?', t_wall),
        ('Wall: velocity vector', 'v[2],e,m?', t_wallvec),
        ('Oblique: vectors', 'm1,u1[2],m2,u2[2],e', t_oblique),
        ('Oblique: speed, angle', 'm1,u1,a1,m2,u2,a2,e', t_obliqueang),
        ('Impulse 1D', 'm,u,v,t?', t_impulse1),
        ('Impulse 2D', 'm,u[2],v[2]', t_impulse2),
        ('Impulse of F(t)', 'F(t),t0,t1,m?', t_impulseF),
        ('Three in a line', 'mA,uA,mB,mC,e', t_three),
    ]),
    ('G', 'Centre of mass', [
        ('COM in a line m,x', 'm x*', t_com1),
        ('COM of parts m,x,y', 'm x y*', t_com),
        ('COM in 3-D m,x,y,z', 'm x y z*', t_com3),
        ('Standard centroids', '', t_centroids),
        ('Arc/sector centroid', 'r,angle', t_sector),
        ('Lamina under y = f(x)', 'f(x),a,b', t_lamina),
        ('Lamina between curves', 'f(x),g(x),a,b', t_between),
        ('Wire along y = f(x)', 'f(x),a,b', t_arc),
        ('Solid of revolution Ox', 'f(x),a,b', t_revolve),
        ('Solid of revolution Oy', 'g(y),a,b', t_revolvey),
        ('Suspend a lamina', 'px,py,gx,gy', t_suspend),
    ]),
    ('C', 'Circular motion', [
        ('Angular speed units', 'om,r?', t_angspeed),
        ('Rev per min to rad/s', 'rpm,r?', t_rpm),
        ('Circle from v and r', 'm,v,r', t_circ_v),
        ('Circle from om and r', 'm,om,r', t_circ_om),
        ('Tangential accel', 'r,om,alpha', t_tangential),
        ('Circle: vectors r,v,a', 'r,om,t', t_circ_vec),
        ('Conical: angle given', 'm,l,angle,g?', t_conical),
        ('Conical: omega given', 'm,l,om,g?', t_conical_om),
        ('Conical, two strings', 'm,a,b,h,om,g?', t_conical2),
        ('Banked track speeds', 'r,angle,mu?,g?', t_bank),
        ('Banked: friction at v', 'm,r,v,angle,g?', t_bankfr),
        ('Rough flat bend', 'm,r,mu,g?', t_rough),
        ('Vert circle: string', 'm,r,u,angle,g?', t_vcircle),
        ('Vert circle: rod', 'm,r,u,angle,g?', t_vrod),
        ('Outside a sphere', 'r,u,g?', t_sphereout),
    ]),
    ('H', "Hooke's law", [
        ('Hooke and EPE: k', 'k,x', t_hooke_k),
        ('Hooke and EPE: lam', 'lam,l,x', t_hooke_lam),
        ('Hooke: find unknown', 'T,lam,l,x', t_hooke_find),
        ('Modulus from hanging', 'm,l,x,g?', t_modulus),
        ('Elastic equilibrium', 'm,lam,l,g?', t_elastic_eq),
        ('Elastic max extension', 'm,lam,l,v,g?', t_elastic_max),
        ('Spring: speed at x', 'm,lam,l,x0,v0,x1', t_elastic_v),
    ]),
    ('V', 'Vectors, variable forces', [
        ('r(t) to v and a', 'x(t),y(t),t?', t_rdiff),
        ('a(t) to v and r', 'ax(t),ay(t),u[2],r0[2],t?', t_aint),
        ('Vector suvat', 'r0[2],u[2],a[2],t', t_vsuvat),
        ('Force from r(t)', 'm,x(t),y(t),t', t_force),
        ('Relative motion', 'rA[2],vA[2],rB[2],vB[2]', t_relative),
        ('a = f(v): t and x', 'f(v),v0,v1', t_avf),
        ('Projectile path', 'u,angle,g?', t_projpath),
        ('Angle to hit (x,y)', 'u,x,y,g?', t_projpt),
        ('Bounding parabola', 'u,x?,g?', t_bounding),
        ('Projectile on incline', 'u,angle,slope,g?', t_incline),
        ('Max range on incline', 'u,slope,g?', t_maxrange),
        ('SHM from x0, v0', 'k,x0,v0,t?', t_shm),
        ('SHM speed at x', 'om,a,x', t_shmv),
        ("Verify x'' = f(x,v,t)", 'x(t),f(x,v,t)', t_verify2),
        ("Verify x' = f(x,t)", 'x(t),f(x,t)', t_verify1),
        ('Fit a,b from x0,v0', 'x(t),t0,x0,v0', t_consts2),
        ('Fit c from x(t0)', 'x(t),t0,x0', t_const1),
    ]),
]
