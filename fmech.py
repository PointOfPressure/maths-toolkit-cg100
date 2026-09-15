# AQA Further Maths 7367, Mechanics option.
# MA dimensional analysis, MB momentum and collisions, MC work energy power,
# MD circular motion, ME centres of mass and moments.
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

# ---- MA  dimensional analysis ----------------------------------------------

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

# ---- MB  momentum and collisions -------------------------------------------

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
          _W('normal ' + _S(nor) + ' -> e x that = ' + _S(nout))]
    if m is not None:
        _pos(m, 'm')
        ans.append('impulse = ' + _S(m * (1.0 + e) * nor) + ' N s')
        ans.append('KE lost = ' + _S(0.5 * m * nor * nor * (1 - e * e)) + ' J')
        wk.append(_W('impulse m(1+e)u sin, along the normal'))
    cav = []
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

def t_oblique(m1, u1, m2, u2, e):
    _pos(m1, 'm1')
    _pos(m2, 'm2')
    _ck_e(e)
    sep = e * (u1[0] - u2[0])
    x1 = (m1 * u1[0] + m2 * u2[0] - m2 * sep) / (m1 + m2)
    x2 = x1 + sep
    y1 = u1[1]
    y2 = u2[1]
    s1 = _mag(x1, y1)
    s2 = _mag(x2, y2)
    ke0 = _ke(m1, _mag(u1[0], u1[1]), m2, _mag(u2[0], u2[1]))
    ke1 = _ke(m1, s1, m2, s2)
    ans = ['v1 = ' + _vec(x1, y1) + ' m/s', 'v2 = ' + _vec(x2, y2) + ' m/s',
           'speed 1 = ' + _S(s1) + ' m/s', 'speed 2 = ' + _S(s2) + ' m/s']
    ans.extend(_keans(ke0, ke1))
    wk = [_W('smooth spheres: y parts unchanged'),
          _W('along x: v2 - v1 = e(u1 - u2) = ' + _S(sep)),
          _W('angle 1 = ' + _S(_dirdeg(x1, y1)) + ' deg to x'),
          _W('angle 2 = ' + _S(_dirdeg(x2, y2)) + ' deg to x')]
    wk.extend(_kewk(ke0, ke1))
    return ans + wk + [_C('x is the line of centres')]

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

# ---- MC  work, energy and power --------------------------------------------

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

# ---- MD  circular motion ----------------------------------------------------

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
            _C('horizontal rough table, no string')]

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

# ---- ME  centres of mass and moments ---------------------------------------

def t_com(data):
    if len(data) < 3 or len(data) % 3:
        raise ValueError('give m,x,y for each part')
    tot = 0.0
    sx = 0.0
    sy = 0.0
    i = 0
    while i < len(data):
        tot += data[i]
        sx += data[i] * data[i + 1]
        sy += data[i] * data[i + 2]
        i += 3
    if tot == 0:
        raise ValueError('total mass is zero')
    return ['x bar = ' + _S(sx / tot), 'y bar = ' + _S(sy / tot),
            'total mass = ' + _S(tot),
            _W('sum m x = ' + _S(sx) + ', sum m y = ' + _S(sy)),
            _W('x bar = sum(m x) / sum(m), ' + str(len(data) // 3) +
               ' parts'),
            _C('use a negative mass for a hole')]

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

def _first(ta, tb, aname, bname):
    if ta < tb - 1e-12:
        return aname
    if tb < ta - 1e-12:
        return bname
    return 'it slides and topples together'

def t_topple(base, h, mu):
    _pos(base, 'base')
    _pos(h, 'h')
    _ck_mu(mu)
    tt = casutil.deg(math.atan(base / h))
    ts = casutil.deg(math.atan(mu))
    return ['topple angle = ' + _S(tt) + ' deg',
            'slide angle = ' + _S(ts) + ' deg',
            _first(tt, ts, 'it topples first', 'it slides first'),
            _W('topples when tan th > base/h = ' + _S(base / h)),
            _W('slides when tan th > mu = ' + _S(mu)),
            _C('uniform block, base wide and h tall')]

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

SECTIONS = [
    ('MA', 'Dimensional analysis', [
        ('Dimensions list', '', t_dimlist),
        ('Name from M,L,T', 'M,L,T', t_dimname),
        ('Check consistency', 'lhs[3],rhs[3]', t_dimcheck),
        ('Find powers a,b,c', 'Q[3],A[3],B[3],C[3]', t_dimpow),
    ]),
    ('MB', 'Momentum and collisions', [
        ('Conservation 1D', 'm1,u1,m2,u2,v1,v2', t_cons1d),
        ('Coalesce, one mass', 'm1,u1,m2,u2', t_coalesce),
        ('Direct impact, e', 'm1,u1,m2,u2,e', t_direct),
        ('Wall: speed and angle', 'u,angle,e,m?', t_wall),
        ('Wall: velocity vector', 'v[2],e,m?', t_wallvec),
        ('Oblique, two spheres', 'm1,u1[2],m2,u2[2],e', t_oblique),
        ('Impulse 1D', 'm,u,v,t?', t_impulse1),
        ('Impulse 2D', 'm,u[2],v[2]', t_impulse2),
        ('Impulse of F(t)', 'F(t),t0,t1,m?', t_impulseF),
        ('Three in a line', 'mA,uA,mB,mC,e', t_three),
    ]),
    ('MC', 'Work, energy and power', [
        ('Work F d cos th', 'F,d,angle', t_workfd),
        ('KE and GPE change', 'm,u,v,h,g?', t_energy),
        ('Energy vs resistance', 'm,u,v,h,F,d,g?', t_energyres),
        ('Hooke and EPE: k', 'k,x', t_hooke_k),
        ('Hooke and EPE: lam', 'lam,l,x', t_hooke_lam),
        ('Work of F(x)', 'F(x),a,b,m?,u?', t_varwork),
        ('Power P = F v', 'P,F,v', t_power),
        ('Max speed on a slope', 'P,m,R,angle,g?', t_slopemax),
        ('Accel at speed v', 'P,m,R,angle,v,g?', t_slopeacc),
        ('Elastic equilibrium', 'm,lam,l,g?', t_elastic_eq),
        ('Elastic max extension', 'm,lam,l,v,g?', t_elastic_max),
    ]),
    ('MD', 'Circular motion', [
        ('Angular speed units', 'om,r?', t_angspeed),
        ('Rev per min to rad/s', 'rpm,r?', t_rpm),
        ('Circle from v and r', 'm,v,r', t_circ_v),
        ('Circle from om and r', 'm,om,r', t_circ_om),
        ('Circle: vectors r,v,a', 'r,om,t', t_circ_vec),
        ('Conical: angle given', 'm,l,angle,g?', t_conical),
        ('Conical: omega given', 'm,l,om,g?', t_conical_om),
        ('Conical, two strings', 'm,a,b,h,om,g?', t_conical2),
        ('Banked track speeds', 'r,angle,mu?,g?', t_bank),
        ('Banked: friction at v', 'm,r,v,angle,g?', t_bankfr),
        ('Rough table circle', 'm,r,mu,g?', t_rough),
        ('Vert circle: string', 'm,r,u,angle,g?', t_vcircle),
        ('Vert circle: rod', 'm,r,u,angle,g?', t_vrod),
        ('Outside a sphere', 'r,u,g?', t_sphereout),
    ]),
    ('ME', 'Centres of mass and moments', [
        ('COM of parts m,x,y', 'data*', t_com),
        ('Standard centroids', '', t_centroids),
        ('Arc/sector centroid', 'r,angle', t_sector),
        ('Lamina under y = f(x)', 'f(x),a,b', t_lamina),
        ('Lamina between curves', 'f(x),g(x),a,b', t_between),
        ('Solid of revolution Ox', 'f(x),a,b', t_revolve),
        ('Slide or topple, slope', 'base,h,mu', t_topple),
        ('Push a block', 'W,base,y,mu', t_push),
        ('Suspend a lamina', 'px,py,gx,gy', t_suspend),
        ('Ladder, smooth wall', 'L,W,x,Wp,mu,angle?', t_ladder),
        ('Beam on two supports', 'L,W,a,b,P,x', t_beam),
        ('Rod, hinge and string', 'L,W,d,alpha,P,x', t_hinge),
        ('Forces and moments', 'data*', t_moments),
    ]),
]
