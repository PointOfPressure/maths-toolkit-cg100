# OCR B (MEI) Further Maths H645, Further Pure with Technology (Y436): curves, DEs, number theory.
# OCR is withdrawing Y436: the last assessment is Summer 2028, with no resit.
# The paper is sat with graphing software, a CAS and a programming language;
# these tools cover its mathematics, not that environment. Symbolic work uses
# the repo CAS where it is reliable and falls back to numbers with a caveat.
# Polar curves take theta as t (or x); a family parameter is a (curves) or
# c (differential equations).
import math
import caseng
import cascalc
import caspoly
import casalg
import cassolve
import casutil

_f = casutil.fmt
_w = casutil.w
_wn = casutil.warn
_m = casutil.m
_mw = casutil.mw

X = ('v', 'x')
PI = math.pi

# ---- shared helpers ---------------------------------------------------------

def _ts(t):
    return caseng.tostr(t)

def _tidy(t):
    try:
        return cascalc.tidy(t)
    except Exception:
        return t

def _flt(v):
    return v if isinstance(v, complex) else float(v)

def _at(tree, v, var='x', env=None):
    # real finite value of tree at var = v, or None. Floats only: an exact
    # int ** int would build a huge integer.
    v = _flt(v)
    e = {var: v}
    if env:
        for k in env:
            if k != var:
                e[k] = _flt(env[k])
    try:
        r = caseng.evalf(tree, v if var == 'x' else 0.0, False, e)
    except Exception:
        return None
    if isinstance(r, complex):
        if abs(r.imag) > 1e-12 * (1.0 + abs(r.real)):
            return None
        r = r.real
    if r != r or r > 1e300 or r < -1e300:
        return None
    return r

def _iv(v, name, lo, hi):
    # an integer field, checked
    if v is None:
        raise ValueError(name + ' missing')
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if v - n > 1e-9 or n - v > 1e-9:
        raise ValueError(name + ' must be a whole number')
    if n < lo or n > hi:
        raise ValueError(name + ' must be ' + str(lo) + ' to ' + str(hi))
    return n

def _snap(v):
    # kill rounding noise near a whole number
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if abs(v - n) < 1e-9 * (1.0 + abs(v)):
        return float(n)
    return v

def _lsnap(v):
    # looser snap for numerically estimated limits
    if v != v or abs(v) > 1e12:
        return v
    n = int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    if abs(v - n) < 1e-6:
        return float(n)
    return v

def _snaprat(x):
    q = 1
    while q <= 24:
        t = x * q
        n = int(t + 0.5) if t >= 0 else -int(-t + 0.5)
        if abs(x - n * 1.0 / q) < 1e-6 * (1.0 + abs(x)):
            return casutil.clean(n * 1.0 / q)
        q += 1
    return x

def _nn(v):
    # exact-rational tree node where possible
    v = casutil.clean(v)
    if abs(v) > 1000:
        return ('n', float(v))
    if isinstance(v, int):
        return ('n', v)
    q = 2
    while q <= 360:
        pv = v * q
        r = int(pv + 0.5) if pv >= 0 else -int(-pv + 0.5)
        if abs(pv - r) < 1e-9 * (abs(pv) if abs(pv) > 1.0 else 1.0):
            return caseng.simplify(('/', ('n', r), ('n', q)))
        q += 1
    return ('n', v)

def _order(a, b):
    a = float(a)
    b = float(b)
    if a == b:
        raise ValueError('the two limits are equal')
    return (b, a) if b < a else (a, b)

def _pvar(tree, want, alt='x'):
    # the variable a one-variable expression is written in
    vs = caseng.vars_in(tree)
    if want in vs or not vs:
        return want
    if alt in vs:
        return alt
    return vs[0]

def _inx(tree, var):
    # the same expression written in x (plot and evalf bind x)
    if var == 'x':
        return tree
    return caseng.subst(tree, var, X)

def _dvar(tree, var):
    try:
        return _tidy(caseng.diff(tree, var))
    except Exception:
        raise ValueError('cannot differentiate')

def _addnear(vals, v, tol):
    for u in vals:
        if abs(u - v) < tol:
            return
    vals.append(v)

def _flist(vals, k=5):
    s = ', '.join([_f(v) for v in vals[:k]])
    if len(vals) > k:
        s += ', ...'
    return s

def _coef(m, body):
    # m*body with a readable coefficient: x, -x, 3x, (1/3)x, 0.707x
    if abs(m - 1.0) < 1e-12:
        return body
    if m < 0:
        return '-' + _coef(-m, body)
    s = _f(m)
    if '/' in s or 'sqrt' in s or 'pi' in s:
        s = '(' + s + ')'
    return s + body

def _lin(m, c, lhs='y', var='x'):
    m = casutil.clean(_snap(m))
    c = casutil.clean(_snap(c))
    if m == 0:
        return lhs + ' = ' + _f(c)
    s = lhs + ' = ' + _coef(m, var)
    if c == 0:
        return s
    return s + (' - ' + _f(-c) if c < 0 else ' + ' + _f(c))

def _bisect(fn, lo, hi, flo):
    i = 0
    while i < 80 and hi - lo > 1e-13 * (1.0 + abs(lo)):
        mid = (lo + hi) / 2.0
        fm = fn(mid)
        if fm is None:
            return None
        if fm == 0:
            return mid
        if (fm < 0) == (flo < 0):
            lo = mid
            flo = fm
        else:
            hi = mid
        i += 1
    return (lo + hi) / 2.0

def _valley(fn, lo, hi):
    # minimise |fn| on [lo, hi] (a touching root)
    i = 0
    while i < 90 and hi - lo > 1e-12:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        a = fn(m1)
        b = fn(m2)
        if a is None or b is None:
            return None
        if abs(a) < abs(b):
            hi = m2
        else:
            lo = m1
        i += 1
    return (lo + hi) / 2.0

def _scan(fn, lo, hi, n=400):
    # real roots of fn (value or None) on [lo, hi]: sign changes and touches
    xs = []
    vs = []
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / n
        xs.append(x)
        vs.append(fn(x))
        i += 1
    tol = 1e-7 * (hi - lo)
    out = []
    i = 0
    while i <= n:
        b = vs[i]
        if b is not None and b == 0:
            _addnear(out, xs[i], tol)
        elif b is not None and i > 0 and vs[i - 1] is not None and vs[i - 1] != 0:
            a = vs[i - 1]
            if (a < 0) != (b < 0):
                r = _bisect(fn, xs[i - 1], xs[i], a)
                if r is not None:
                    fr = fn(r)
                    big = abs(a) if abs(a) > abs(b) else abs(b)
                    if fr is not None and abs(fr) <= 1e-6 * (1.0 + big):
                        _addnear(out, r, tol)
            elif i < n and vs[i + 1] is not None and abs(b) < abs(a) and \
                    abs(b) < abs(vs[i + 1]) and (vs[i + 1] < 0) == (b < 0):
                r = _valley(fn, xs[i - 1], xs[i + 1])
                if r is not None:
                    fr = fn(r)
                    if fr is not None and abs(fr) < 1e-9:
                        _addnear(out, r, tol)
        i += 1
    out.sort()
    return [_snap(r) for r in out]

def _roots_of(tree, lo, hi, var='x', env=None):
    return _scan(lambda v: _at(tree, v, var, env), lo, hi)

def _yrange(tree, lo, hi, extra):
    ys = []
    i = 0
    while i <= 120:
        v = _at(tree, lo + (hi - lo) * i / 120.0)
        if v is not None:
            ys.append(v)
        i += 1
    for x in extra:
        v = _at(tree, x)
        if v is not None:
            ys.append(v)
    if not ys:
        return None
    return (min(ys), max(ys))

def _plot(curves, lo, hi, kind, title, ylo=None, yhi=None):
    import plot
    plot.run(curves, lo, hi, kind, title[:50], ylo, yhi)

# ---- C  investigation of curves: plotting, families, limits ---------------
# C2 C3 C4 C9 C10 C11 C12 TC1

def t_plot(f, a, b):
    if (a is None) != (b is None):
        raise ValueError('give both a and b, or neither')
    lo, hi = (-6.0, 6.0) if a is None else _order(a, b)
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    _plot([tree], lo, hi, 'y', 'y = ' + _ts(f))
    rts = _roots_of(tree, lo, hi)
    out = ['roots: ' + _flist(rts) if rts else 'no roots in range']
    if lo <= 0 <= hi:
        v = _at(tree, 0.0)
        out.append('f(0) = ' + ('undefined' if v is None else _f(v)))
    try:
        d = _dvar(tree, 'x')
        tps = _roots_of(d, lo, hi)
    except ValueError:
        d = None
        tps = []
    for x in tps[:5]:
        v = _at(tree, x)
        if v is not None:
            out.append('turning point (' + _f(x) + ', ' + _f(_snap(v)) + ')')
    yr = _yrange(tree, lo, hi, tps)
    out.append(_w('x from ' + _f(lo) + ' to ' + _f(hi)))
    if yr is not None:
        out.append(_w('y from ' + _f(yr[0]) + ' to ' + _f(yr[1])))
    if d is not None:
        out.append(_w("f'(x) = " + _ts(d)))
    return out

FAM_MAX = 6

def _family(f, name, vals, lo, hi):
    if name not in caseng.vars_in(f):
        raise ValueError('the expression does not use ' + name)
    vals = vals[:FAM_MAX]
    curves = []
    out = []
    for v in vals:
        g = caseng.subst(f, name, _nn(v))
        curves.append(g)
        tag = name + '=' + _f(v)
        try:
            tps = _roots_of(_dvar(g, 'x'), lo, hi)
        except ValueError:
            tps = []
        yr = _yrange(g, lo, hi, tps)
        if yr is None:
            out.append(tag + ': undefined in range')
            continue
        out.append(tag + ' y in [' + _f(_snap(yr[0])) + ', ' + _f(_snap(yr[1])) + ']')
        rts = _roots_of(g, lo, hi)
        out.append(tag + ' roots: ' + (_flist(rts, 4) if rts else 'none in range'))
        if tps:
            out.append(_w(tag + ' turning at x = ' + _flist(tps, 4)))
    out.append(_w('members: ' + str(len(vals)) + ', x from ' + _f(lo) + ' to ' + _f(hi)))
    return curves, out

def t_family(f, xlo, xhi, avals):
    lo, hi = _order(xlo, xhi)
    curves, out = _family(f, 'a', avals, lo, hi)
    _plot(curves, lo, hi, 'y', 'y = ' + _ts(f))
    return out

def _polar_minmax(tree):
    lo = None
    hi = None
    ilo = 0
    i = 0
    while i <= 720:
        v = _at(tree, 2.0 * PI * i / 720.0)
        if v is not None:
            if lo is None or v < lo:
                lo = v
                ilo = i
            if hi is None or v > hi:
                hi = v
        i += 1
    if lo is None:
        return None
    a = 2.0 * PI * (ilo - 1) / 720.0
    b = 2.0 * PI * (ilo + 1) / 720.0
    k = 0
    while k < 60:
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        v1 = _at(tree, m1)
        v2 = _at(tree, m2)
        if v1 is None or v2 is None:
            break
        if v1 < v2:
            b = m2
        else:
            a = m1
        k += 1
    v = _at(tree, (a + b) / 2.0)
    if v is not None and v < lo:
        lo = v
    return (_snap(lo), _snap(hi))

def t_family_polar(r, avals):
    var = _pvar(r, 't', 'x')
    tree = _inx(r, var)
    if 'a' not in caseng.vars_in(tree):
        raise ValueError('the expression does not use a')
    curves = []
    out = []
    for a in avals[:FAM_MAX]:
        g = caseng.subst(tree, 'a', _nn(a))
        curves.append(g)
        tag = 'a=' + _f(a)
        mm = _polar_minmax(g)
        if mm is None:
            out.append(tag + ': undefined')
            continue
        out.append(tag + ' r in [' + _f(mm[0]) + ', ' + _f(mm[1]) + ']')
        if abs(mm[0]) < 1e-7:
            out.append(tag + ' r touches 0: meets pole')
        elif mm[0] < 0 and mm[1] > 0:
            out.append(tag + ' r changes sign: loop')
        elif mm[1] < 0:
            out.append(_w(tag + ' r < 0 throughout'))
        else:
            out.append(_w(tag + ' r > 0: no loop, bounded'))
    out.append(_w('theta from 0 to 2pi'))
    _plot(curves, 0.0, 2.0 * PI, 'polar', 'r = ' + _ts(r))
    return out

def t_family_param(xt, yt, tlo, thi, avals):
    lo, hi = _order(tlo, thi)
    vs = caseng.vars_in(xt) + caseng.vars_in(yt)
    if 'a' not in vs:
        raise ValueError('the curve does not use a')
    var = 't' if 't' in vs else 'x'
    xa = _inx(xt, var)
    ya = _inx(yt, var)
    curves = []
    out = []
    for a in avals[:FAM_MAX]:
        gx = caseng.subst(xa, 'a', _nn(a))
        gy = caseng.subst(ya, 'a', _nn(a))
        curves.append((gx, gy, lo, hi))
        tag = 'a=' + _f(a)
        xs = []
        ys = []
        i = 0
        while i <= 200:
            t = lo + (hi - lo) * i / 200.0
            u = _at(gx, t)
            v = _at(gy, t)
            if u is not None and v is not None:
                xs.append(u)
                ys.append(v)
            i += 1
        if not xs:
            out.append(tag + ': undefined')
            continue
        out.append(tag + ' x in [' + _f(_snap(min(xs))) + ', ' + _f(_snap(max(xs))) + ']')
        out.append(tag + ' y in [' + _f(_snap(min(ys))) + ', ' + _f(_snap(max(ys))) + ']')
        u0 = _at(gx, lo)
        u1 = _at(gx, hi)
        v0 = _at(gy, lo)
        v1 = _at(gy, hi)
        if None not in (u0, u1, v0, v1) and abs(u0 - u1) + abs(v0 - v1) < 1e-9:
            out.append(_w(tag + ' closed: ends meet'))
    out.append(_w('t from ' + _f(lo) + ' to ' + _f(hi)))
    _plot(curves, lo, hi, 'param', 'x = ' + _ts(xt) + ', y = ' + _ts(yt))
    return out

ENV_NX = 41
ENV_EVERY = 10

def t_envelope(f, xlo, xhi, alo, ahi):
    xlo, xhi = _order(xlo, xhi)
    alo, ahi = _order(alo, ahi)
    if 'a' not in caseng.vars_in(f):
        raise ValueError('the expression does not use a')
    g = _dvar(f, 'a')
    env = []
    i = 0
    while i < ENV_NX:
        x = xlo + (xhi - xlo) * i / (ENV_NX - 1.0)
        for a in _scan(lambda v: _at(g, v, 'a', {'x': x}), alo, ahi, 80)[:3]:
            y = _at(f, a, 'a', {'x': x})
            if y is not None:
                env.append((_snap(x), _snap(a), _snap(y), i))
        i += 1
    members = []
    k = 0
    while k < 7:
        members.append(caseng.subst(f, 'a', _nn(alo + (ahi - alo) * k / 6.0)))
        k += 1
    out = []
    if not env:
        _plot(members, xlo, xhi, 'y', 'y = ' + _ts(f))
        return ['no envelope for a in range',
                _w('df/da = ' + _ts(g)),
                _wn('df/da = 0 has no solution')]
    sym = None
    try:
        for r in cassolve.roots(caseng.simplify(g), 'a') or []:
            e = _tidy(caseng.subst(f, 'a', r))
            ok = 0
            for p in env:
                ya = _at(e, p[0])
                ar = _at(r, p[0])
                if ya is not None and ar is not None and abs(ar - p[1]) < 1e-6 * (1 + abs(p[1])) \
                        and abs(ya - p[2]) < 1e-6 * (1 + abs(p[2])):
                    ok += 1
            if ok > 0:
                sym = (r, e, ok)
                break
    except Exception:
        sym = None
    if sym is not None:
        s = _ts(sym[1])
        if len(s) <= 22:
            out.append('envelope y = ' + s)
        else:
            out.append('envelope y =')
            out.append(_m(sym[1]))
        out.append(_w('from a = ' + _ts(sym[0])))
        if sym[2] < len(env):
            out.append(_wn('matches ' + str(sym[2]) + ' of ' + str(len(env)) + ' points'))
        members.append(sym[1])
    else:
        out.append(_wn('no formula: points found numerically'))
    out.append(_w('df/da = ' + _ts(g)))
    out.append(_w('envelope: df/da = 0 and y = f(x, a)'))
    for p in env:
        if p[3] % ENV_EVERY == 0:
            out.append('x=' + _f(p[0]) + ' a=' + _f(p[1]) + ' y=' + _f(p[2]))
    out.append(_w('envelope points found: ' + str(len(env))))
    _plot(members, xlo, xhi, 'y', 'y = ' + _ts(f))
    return out

LIM_H = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
LIM_X = [1e2, 1e3, 1e4, 1e5, 1e6]
LIM_X2 = [10.0, 20.0, 50.0, 100.0, 200.0, 500.0]

def _samples(tree, pts):
    return [_at(tree, p) for p in pts]

def _verdict(vals):
    # ('num', L) / ('inf', sign) / ('none', None) from a converging table
    n = len(vals)
    if n < 3:
        return ('none', None)
    a = vals[n - 3]
    b = vals[n - 2]
    c = vals[n - 1]
    if a is None or b is None or c is None:
        return ('none', None)
    d1 = abs(c - b)
    d2 = abs(b - a)
    if d1 <= 1e-3 * (1.0 + abs(c)) and d2 <= 1e-2 * (1.0 + abs(b)):
        L = (10.0 * c - b) / 9.0
        if abs(L - c) > 10.0 * d1 + 1e-9:
            L = c
        return ('num', _lsnap(L))
    if abs(c) > 1e4 and abs(c) >= 3.0 * abs(b) and abs(b) >= 3.0 * abs(a) \
            and (c < 0) == (b < 0):
        return ('inf', 1.0 if c > 0 else -1.0)
    return ('none', None)

def _vstr(k):
    if k[0] == 'num':
        return _f(k[1])
    if k[0] == 'inf':
        return '+infinity' if k[1] > 0 else '-infinity'
    return 'no limit found'

def _blowup(tree, c, sgn):
    prev = None
    for d in (1e-2, 1e-4, 1e-6, 1e-8):
        v = _at(tree, c + sgn * d)
        if v is None:
            return False
        v = abs(v)
        if prev is not None and v <= prev * 1.2:
            return False
        prev = v
    return prev > 10.0

def _side(tree, c, sgn):
    k = _verdict(_samples(tree, [c + sgn * h for h in LIM_H]))
    if k[0] != 'none':
        return k
    if _blowup(tree, c, sgn):
        v = _at(tree, c + sgn * 1e-8)
        if v is not None:
            return ('inf', 1.0 if v > 0 else -1.0)
    return k

def _towards(tree, c, sgn, L):
    # do f(c +/- h) close in on L as h -> 0 (slow approach, e.g. sqrt)?
    prev = None
    for h in (1e-4, 1e-6, 1e-8, 1e-10):
        v = _at(tree, c + sgn * h)
        if v is None:
            return False
        dist = abs(v - L)
        if prev is not None and dist > prev:
            return False
        prev = dist
    return prev < 1e-3 * (1.0 + abs(L))

def _nodeval(node):
    # value of a constant CAS result, infinities allowed
    if node is None:
        return None
    try:
        v = caseng.evalf(node, 0.0, False, None)
    except Exception:
        return None
    if isinstance(v, complex) or v != v:
        return None
    return v

def _caslim(tree, a, inf=0):
    if abs(a) > 1000:
        return None
    try:
        if inf:
            node = casalg.limit(tree, 'x', None, inf)
        else:
            node = casalg.limit(tree, 'x', _nn(a))
    except Exception:
        return None
    if node is None or caseng.vars_in(node):
        return None
    return _nodeval(node)

def _close(u, v):
    return abs(u - v) <= 1e-6 * (1.0 + abs(v))

def t_limit(f, a):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    kl = _side(tree, a, -1.0)
    kr = _side(tree, a, 1.0)
    cas = _caslim(tree, a)
    if cas is not None and -1e300 < cas < 1e300:
        if kl[0] == 'none' and _towards(tree, a, -1.0, cas):
            kl = ('num', cas)
        if kr[0] == 'none' and _towards(tree, a, 1.0, cas):
            kr = ('num', cas)
    out = []
    L = None
    if kl[0] == 'num' and kr[0] == 'num' and _close(kl[1], kr[1]):
        L = _lsnap((kl[1] + kr[1]) / 2.0)
        if cas is not None and -1e300 < cas < 1e300 and _close(cas, L):
            L = cas
            out.append('limit = ' + _f(L))
            out.append(_w('CAS: substitution / l\'Hopital'))
        else:
            out.append('limit = ' + _f(L))
            out.append(_wn('limit found numerically'))
    elif kl[0] == 'inf' and kr[0] == 'inf' and kl[1] == kr[1]:
        out.append('limit = ' + _vstr(kl))
        out.append('x = ' + _f(a) + ' is a vertical asymptote')
    elif kl[0] == 'inf' or kr[0] == 'inf':
        out.append('no limit: sides differ')
        out.append('x = ' + _f(a) + ' is a vertical asymptote')
    elif kl[0] == 'num' and kr[0] == 'num':
        out.append('no limit: sides differ')
    elif kl[0] == 'num' or kr[0] == 'num':
        out.append('one-sided limit only')
        out.append(_wn('f is not defined on both sides'))
    else:
        out.append('no limit found')
        out.append(_wn('f does not settle near x = ' + _f(a)))
    out.append('from below: ' + _vstr(kl))
    out.append('from above: ' + _vstr(kr))
    if L is not None:
        fa = _at(tree, a)
        if fa is None:
            out.append('f(' + _f(a) + ') undefined: a hole')
        elif _close(fa, L):
            out.append('continuous at x = ' + _f(a))
        else:
            out.append('f(' + _f(a) + ') = ' + _f(fa) + ': removable')
    out.append(_w('h       f(a-h)        f(a+h)'))
    lv = _samples(tree, [a - h for h in LIM_H])
    rv = _samples(tree, [a + h for h in LIM_H])
    i = 0
    while i < len(LIM_H):
        out.append(_w(_f(LIM_H[i], 1) + '   ' + ('undef' if lv[i] is None else _f(lv[i], 6)) +
                      '   ' + ('undef' if rv[i] is None else _f(rv[i], 6))))
        i += 1
    return out

def _endk(tree, sgn):
    # verdict as x -> sgn*infinity; a shorter table when big x overflows
    k = _verdict(_samples(tree, [sgn * v for v in LIM_X]))
    if k[0] == 'none':
        pre = []
        for v in LIM_X2:
            fv = _at(tree, sgn * v)
            if fv is None:
                break
            pre.append(fv)
        if len(pre) >= 3:
            k = _verdict(pre)
    return k

def _lim_inf(f, sgn):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    vals = _samples(tree, [sgn * v for v in LIM_X])
    k = _endk(tree, sgn)
    cas = _caslim(tree, 0, 1 if sgn > 0 else -1)
    out = []
    if cas is not None and (k[0] == 'none' or (k[0] == 'num' and -1e300 < cas < 1e300 and
                                              abs(cas - k[1]) < 1e-3 * (1 + abs(cas))) or
                            (k[0] == 'inf' and (cas > 1e300 or cas < -1e300) and (cas > 0) == (k[1] > 0))):
        if cas > 1e300:
            out.append('limit = +infinity')
        elif cas < -1e300:
            out.append('limit = -infinity')
        else:
            out.append('limit = ' + _f(cas))
            out.append('horizontal asymptote y = ' + _f(cas))
        out.append(_w('CAS: leading terms / l\'Hopital'))
    else:
        out.append('no limit found' if k[0] == 'none' else 'limit = ' + _vstr(k))
        if k[0] == 'num':
            out.append('horizontal asymptote y = ' + _f(k[1]))
        if k[0] != 'none':
            out.append(_wn('limit found numerically'))
    name = 'x=' if sgn > 0 else 'x=-'
    i = 0
    while i < len(LIM_X):
        out.append(_w(name + _f(LIM_X[i]) + '  f = ' + ('undefined' if vals[i] is None else _f(vals[i], 6))))
        i += 1
    return out

def t_lim_pinf(f):
    return _lim_inf(f, 1.0)

def t_lim_ninf(f):
    return _lim_inf(f, -1.0)

VA_LO = -20.0
VA_HI = 20.0
VA_N = 400
MAX_VA = 12

def _absev(tree, x):
    v = _at(tree, x)
    return 1e300 if v is None else abs(v)

def _peak(tree, lo, hi):
    i = 0
    while i < 90 and (hi - lo) > 1e-11:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        if _absev(tree, m1) < _absev(tree, m2):
            lo = m1
        else:
            hi = m2
        i += 1
    return _lsnap((lo + hi) / 2.0)

def _brackets(tree, lo, hi, n):
    xs = []
    vs = []
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / n
        xs.append(x)
        vs.append(_at(tree, x))
        i += 1
    out = []
    i = 1
    while i < n:
        a = vs[i - 1]
        b = vs[i]
        d = vs[i + 1]
        hit = False
        if b is None and (a is not None or d is not None):
            hit = True
        elif b is not None and abs(b) > 50.0:
            if (a is None or abs(b) > 5.0 * abs(a)) or (d is None or abs(b) > 5.0 * abs(d)):
                hit = True
        if not hit and b is not None and d is not None:
            if abs(b) > 10.0 and abs(d) > 10.0 and ((b < 0) != (d < 0)):
                out.append((xs[i], xs[i + 1]))
        if hit:
            out.append((xs[i - 1], xs[i + 1]))
        i += 1
    return out

def _verticals(tree, lo, hi):
    out = []
    for br in _brackets(tree, lo, hi, VA_N):
        if len(out) >= MAX_VA:
            break
        c = _peak(tree, br[0], br[1])
        if c < lo or c > hi:
            continue
        if _blowup(tree, c, 1.0) or _blowup(tree, c, -1.0):
            _addnear(out, c, 1e-3)
    out.sort()
    return out

def _ratparts(tree):
    # exact (N, D) rational polynomials low->high, or None
    try:
        pf = caspoly.polyfrac(tree, 'x')
    except Exception:
        return None
    if pf is None:
        return None
    N = caspoly.ptrim(list(pf[0]))
    D = caspoly.ptrim(list(pf[1]))
    if not D:
        return None
    return (N, D)

def _rv(r):
    return r[0] * 1.0 / r[1]

def t_asymptotes(f):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    out = []
    vs = _verticals(tree, VA_LO, VA_HI)
    for c in vs:
        out.append('vertical: x = ' + _f(c))
        out.append('  from below f -> ' + _vstr(_side(tree, c, -1.0)))
        out.append('  from above f -> ' + _vstr(_side(tree, c, 1.0)))
    if not vs:
        out.append('no vertical asymptote')
    if len(vs) >= MAX_VA:
        out.append(_wn('first ' + str(MAX_VA) + ' vertical asymptotes only'))
    out.append(_w('verticals searched for x from -20 to 20'))
    done = False
    rp = _ratparts(tree)
    if rp is not None and len(rp[1]) >= 2:
        N, D = rp
        qr = caspoly.pdivmod(N, D) if N else ([], [])
        if qr is not None:
            q = caspoly.ptrim(list(qr[0]))
            rem = caspoly.ptrim(list(qr[1]))
            if len(q) <= 1:
                v = 0.0 if not q else _rv(q[0])
                out.append('horizontal: y = ' + _f(v) + ' (exact)')
                out.append(_w('deg num <= deg den: f -> ratio of'))
                out.append(_w('leading terms (0 if num is lower)'))
                done = True
            elif len(q) == 2:
                out.append('oblique: ' + _lin(_rv(q[1]), _rv(q[0])) + ' (exact)')
                out.append(_w('num = q(x) den + r(x), r = ' +
                              (_ts(caspoly.ptree(rem, 'x')) if rem else '0')))
                out.append(_w('r/den -> 0, so f - q(x) -> 0'))
                done = True
            else:
                out.append('no horizontal or oblique')
                out.append(_w('deg num - deg den = ' + str(len(q) - 1)))
                done = True
    kp = _endk(tree, 1.0)
    km = _endk(tree, -1.0)
    if not done:
        for sgn, k, name in ((1.0, kp, '+inf'), (-1.0, km, '-inf')):
            if k[0] == 'num':
                out.append('as x->' + name + ': y = ' + _f(k[1]))
                continue
            mk = _verdict(_samples(('/', tree, X), [sgn * v for v in LIM_X]))
            if mk[0] != 'num' or abs(mk[1]) < 1e-9:
                out.append('none as x->' + name)
                continue
            m = mk[1]
            bk = _verdict(_samples(('-', tree, ('*', ('n', m), X)), [sgn * v for v in LIM_X]))
            if bk[0] == 'num':
                out.append('as x->' + name + ': ' + _lin(m, bk[1]))
                out.append(_w('  m = lim f/x = ' + _f(m) + ', c = lim f - mx = ' + _f(bk[1])))
            else:
                out.append('none as x->' + name)
        out.append(_wn('end behaviour found numerically'))
    for k, name in ((kp, '+inf'), (km, '-inf')):
        out.append(_w(('no limit' if k[0] == 'none' else 'f -> ' + _vstr(k)) + ' as x -> ' + name))
    _plot([tree], -8.0, 8.0, 'y', 'y = ' + _ts(f))
    return out

# rational-function graphs (moved from the AQA core pure module)

def _num(v):
    return ('n', casutil.clean(v))

def _linT(a, b):
    t = ('*', _num(a), X) if a != 1 else X
    if a == 0:
        return _num(b)
    if b == 0:
        return t
    return ('+', t, _num(b))

def _quadT(a, b, c):
    t = None
    if a != 0:
        t = ('^', X, ('n', 2)) if a == 1 else ('*', _num(a), ('^', X, ('n', 2)))
    lb = _linT(b, c)
    if t is None:
        return lb
    if b == 0 and c == 0:
        return t
    return ('+', t, lb)

def _qreal(co):
    # real roots of a linear or quadratic, co high->low, snapped
    while co and co[0] == 0:
        co = co[1:]
    if len(co) < 2:
        return []
    if len(co) == 2:
        return [_snaprat(-co[1] * 1.0 / co[0])]
    a, b, c = co[0], co[1], co[2]
    d = b * b - 4.0 * a * c
    if d < 0:
        return []
    s = math.sqrt(d)
    rs = [_snaprat((-b - s) / (2.0 * a)), _snaprat((-b + s) / (2.0 * a))]
    if d == 0:
        rs = rs[:1]
    rs.sort()
    return rs

def _eqstr(co, var):
    # co high->low -> '4y^2-40y+36'
    out = ''
    n = len(co) - 1
    i = 0
    while i <= n:
        c = casutil.clean(co[i])
        p = n - i
        if c != 0:
            neg = c < 0
            mag = -c if neg else c
            s = _f(mag)
            if p == 0:
                piece = s
            else:
                pw = var if p == 1 else var + '^' + str(p)
                piece = pw if mag == 1 else s + pw
            if out == '':
                out = ('-' if neg else '') + piece
            else:
                out += ('-' if neg else '+') + piece
        i += 1
    return out if out else '0'

def _quadrange(A, B, C, D, E, F, out):
    P = E * E - 4.0 * D * F
    Q = 4.0 * A * F + 4.0 * C * D - 2.0 * B * E
    R = B * B - 4.0 * A * C
    ys = []
    if P == 0 and Q == 0:
        if R >= 0:
            out.append('y can take any value')
        else:
            out.append(_wn('no real y: check the coefficients'))
    elif P == 0:
        y0 = _snaprat(-R / Q)
        out.append('range: y ' + ('>= ' if Q > 0 else '<= ') + _f(y0))
        ys = [y0]
    else:
        dd = Q * Q - 4.0 * P * R
        if dd < 0:
            out.append('range: ' + ('every real y' if P > 0 else 'no real y'))
        else:
            sq = math.sqrt(dd)
            y1 = _snaprat((-Q - sq) / (2.0 * P))
            y2 = _snaprat((-Q + sq) / (2.0 * P))
            if y1 > y2:
                y1, y2 = y2, y1
            ys = [y1, y2]
            if P > 0:
                out.append('range: y <= ' + _f(y1) + ' or y >= ' + _f(y2))
            else:
                out.append('range: ' + _f(y1) + ' <= y <= ' + _f(y2))
    for y in ys:
        den = 2.0 * (A - y * D)
        if abs(den) > 1e-12:
            out.append('stationary point (' + _f(_snaprat(-(B - y * E) / den)) + ', ' + _f(y) + ')')
    out.append(_w('y(Dx^2+Ex+F) = Ax^2+Bx+C, so'))
    out.append(_w('(A-yD)x^2+(B-yE)x+(C-yF) = 0'))
    out.append(_w('real x needs ' + _eqstr([P, Q, R], 'y') + ' >= 0'))

def _plot1(tree, centre, title):
    _plot([tree], centre - 8.0, centre + 8.0, 'y', title)

def t_rat1(a, b, c, d):
    if c == 0:
        raise ValueError('c = 0: this is a straight line')
    if a * d - b * c == 0:
        return ['constant: y = ' + _f(a * 1.0 / c), _wn('the factors cancel')]
    va = _snaprat(-d * 1.0 / c)
    _plot1(('/', _linT(a, b), _linT(c, d)), va, 'y = (ax+b)/(cx+d)')
    out = ['vertical asymptote x = ' + _f(va),
           'horizontal asymptote y = ' + _f(casutil.clean(a * 1.0 / c))]
    if a != 0:
        out.append('crosses x-axis at ' + _f(_snaprat(-b * 1.0 / a)))
    else:
        out.append(_w('a = 0: never crosses the x-axis'))
    if d != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(b * 1.0 / d)))
    else:
        out.append(_w('d = 0: the y-axis is the asymptote'))
    out.append(_w('x -> inf gives y -> a/c; x = -d/c kills the'))
    out.append(_w('denominator'))
    return out

def t_rat2(a, b, c, d, e):
    if d == 0:
        raise ValueError('d = 0: not a rational function')
    if a == 0:
        raise ValueError('a = 0: use the (ax+b)/(cx+d) tool')
    va = _snaprat(-e * 1.0 / d)
    mg = a * 1.0 / d
    kk = (b - mg * e) * 1.0 / d
    rem = c - kk * e
    _plot1(('/', _quadT(a, b, c), _linT(d, e)), va, 'y = (ax^2+bx+c)/(dx+e)')
    out = ['vertical asymptote x = ' + _f(va)]
    if rem == 0:
        out.append(_lin(mg, kk) + ' (a straight line)')
        out.append(_wn('exact division: a hole at x = ' + _f(va)))
    else:
        out.append('oblique asymptote ' + _lin(mg, kk))
    if e != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(c * 1.0 / e)))
    xs = _qreal([a, b, c])
    out.append('crosses x-axis at ' + _flist(xs) if xs else 'no x-intercept')
    _quadrange(a, b, c, 0.0, d, e, out)
    if rem != 0:
        fr = _ts(caseng.simplify(('/', _num(abs(rem)), _linT(d, e))))
        out.append(_w('divide out: ' + _lin(mg, kk) + (' - ' if rem < 0 else ' + ') + fr))
    return out

def t_rat3(a, b, c, d, e, f):
    if d == 0:
        raise ValueError('d = 0: use the quad/linear tool')
    vas = _qreal([d, e, f])
    _plot1(('/', _quadT(a, b, c), _quadT(d, e, f)), vas[0] if vas else 0.0, 'y = quad/quad')
    out = []
    if vas:
        out.append('vertical asymptotes x = ' + _flist(vas))
    else:
        out.append('no vertical asymptote')
    out.append('horizontal asymptote y = ' + _f(casutil.clean(a * 1.0 / d)))
    if f != 0:
        out.append('crosses y-axis at ' + _f(casutil.clean(c * 1.0 / f)))
    xs = _qreal([a, b, c]) if (a or b) else []
    out.append('crosses x-axis at ' + _flist(xs) if xs else 'no x-intercept')
    _quadrange(a, b, c, d, e, f, out)
    return out

def t_stationary(f):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    d1 = _dvar(tree, 'x')
    try:
        d2 = _dvar(d1, 'x')
    except ValueError:
        d2 = None
    out = []
    roots = _roots_of(d1, VA_LO, VA_HI)
    for r in roots:
        g0 = _at(d1, r)
        c = _lsnap(r)
        gc = _at(d1, c)
        if g0 is not None and gc is not None and abs(gc) <= abs(g0) + 1e-12:
            r = c
        y = _at(tree, r)
        if y is None:
            continue
        word = None
        dd = 0.01 * (1.0 + abs(r))
        for rr in roots:
            if rr != r and abs(rr - r) / 3.0 < dd:
                dd = abs(rr - r) / 3.0
        la = _at(d1, r - dd)
        rb = _at(d1, r + dd)
        if la is not None and rb is not None:
            if la < 0.0 and rb > 0.0:
                word = 'minimum'
            elif la > 0.0 and rb < 0.0:
                word = 'maximum'
            elif (la > 0.0 and rb > 0.0) or (la < 0.0 and rb < 0.0):
                word = 'inflection'
        s = None if d2 is None else _at(d2, r)
        if word is None and s is not None:
            word = 'minimum' if s > 0 else ('maximum' if s < 0 else None)
        if word is None:
            word = 'inflection'
        out.append(word + ' (' + _f(r) + ', ' + _f(_snap(y)) + ')')
        if s is not None:
            out.append(_w("  f'' = " + _f(_snap(s)) + ' (supporting only)'))
    if not out:
        out.append('no stationary point')
    out.append(_w("f'(x) = " + _ts(d1)))
    out.append(_w('searched x from -20 to 20; nature from'))
    out.append(_w("the sign of f' either side"))
    return out

def _gridundef(tree, lo, hi, n):
    out = []
    prev = True
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / n
        ok = _at(tree, x) is not None
        if not ok and prev:
            out.append(x)
        prev = ok
        i += 1
    return out

def t_cusps(f):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    d1 = _dvar(tree, 'x')
    cands = []
    for br in _brackets(d1, VA_LO, VA_HI, VA_N):
        c = _peak(d1, br[0], br[1])
        if VA_LO <= c <= VA_HI:
            _addnear(cands, c, 1e-3)
    for c in _gridundef(d1, VA_LO, VA_HI, VA_N):
        _addnear(cands, _lsnap(c), 1e-3)
    cands.sort()
    out = []
    for c in cands:
        fa = _at(tree, c - 1e-6)
        fb = _at(tree, c + 1e-6)
        if fa is None or fb is None:
            continue
        if abs(fa - fb) > 1e-3 * (1.0 + abs(fa)):
            continue
        if _blowup(tree, c, 1.0) or _blowup(tree, c, -1.0):
            continue
        kl = _side(d1, c, -1.0)
        kr = _side(d1, c, 1.0)
        sl = _vstr(kl)
        sr = _vstr(kr)
        if sl == sr or (kl[0] == 'none' and kr[0] == 'none'):
            continue
        fc = _at(tree, c)
        if fc is None:
            fc = (fa + fb) / 2.0
        if kl[0] == 'inf' and kr[0] == 'inf':
            word = 'cusp'
        elif kl[0] == 'inf' or kr[0] == 'inf':
            word = 'vertical tangent'
        else:
            word = 'corner'
        out.append(word + ' at (' + _f(c) + ', ' + _f(_snap(fc)) + ')')
        out.append("  f' from below -> " + sl)
        out.append("  f' from above -> " + sr)
    if not out:
        out.append('no cusp or corner found')
        out.append(_w("f' has the same limit from both sides"))
        out.append(_w('everywhere f is continuous'))
    else:
        out.append(_w("f is continuous but the one-sided limits"))
        out.append(_w("of f' differ; opposite infinities = cusp"))
    out.append(_w('searched x from -20 to 20'))
    return out

# ---- T  investigation of curves: tangents, conversion, arc length ---------
# C2 C5 C6 C7 C8 c2

def _tn_lines(x0, y0, dxs, dys, out):
    # tangent and normal from a direction (dxs, dys); returns gradient or None
    tiny = 1e-12 * (1.0 + abs(dxs) + abs(dys))
    if abs(dxs) <= tiny and abs(dys) <= tiny:
        out.append(_wn('both derivatives are 0: singular point'))
        out.append(_wn('(a cusp is possible); no tangent here'))
        return None
    if abs(dxs) <= tiny:
        out.append('gradient undefined')
        out.append('tangent x = ' + _f(_snap(x0)))
        out.append('normal ' + _lin(0.0, y0))
        return None
    m = _snap(dys / dxs)
    out.append('gradient dy/dx = ' + _f(m))
    out.append('tangent ' + _lin(m, y0 - m * x0))
    if m == 0:
        out.append('normal x = ' + _f(_snap(x0)))
    else:
        out.append('normal ' + _lin(-1.0 / m, y0 + x0 / m))
    return m

def _eqv(name, tree, v):
    a = _ts(tree)
    b = _f(_snap(v))
    return name + ' = ' + a if a == b else name + ' = ' + a + ' = ' + b

def _linetree(m, x0, y0):
    return ('+', ('*', ('n', m), ('-', X, ('n', x0))), ('n', y0))

def t_tan_cart(f, a):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    d = _dvar(tree, 'x')
    y0 = _at(tree, a)
    if y0 is None:
        raise ValueError('f is undefined at x = ' + _f(a))
    y0 = _snap(y0)
    out = ['point (' + _f(a) + ', ' + _f(y0) + ')']
    m = _at(d, a)
    curves = [tree]
    if m is None:
        k = _side(d, a, 1.0)
        if k[0] == 'inf':
            _tn_lines(a, y0, 0.0, 1.0, out)
        else:
            out.append(_wn('f is not differentiable here'))
    else:
        m = _tn_lines(a, y0, 1.0, m, out)
        if m is not None:
            curves.append(_linetree(m, a, y0))
            if m != 0:
                curves.append(_linetree(-1.0 / m, a, y0))
    out.append(_w("dy/dx = " + _ts(d)))
    _plot(curves, a - 6.0, a + 6.0, 'y', 'tangent at x = ' + _f(a))
    return out

def t_tan_var(f, ps):
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    d = _dvar(tree, 'x')
    P = ('v', 'p')
    sym = ('+', ('*', caseng.subst(d, 'x', P), ('-', X, P)), caseng.subst(tree, 'x', P))
    try:
        sym = caspoly.collect(caspoly.expand(sym))
    except Exception:
        sym = _tidy(sym)
    out = []
    s = _ts(sym)
    if len(s) <= 30:
        out.append('y = ' + s)
    else:
        out.append('tangent at x = p:')
        out.append(_m(sym))
    out.append(_w("y = f'(p)(x - p) + f(p)"))
    curves = [tree]
    for p in ps[:5]:
        y0 = _at(tree, p)
        m = _at(d, p)
        if y0 is None or m is None:
            out.append('p=' + _f(p) + ': no tangent')
            continue
        m = _snap(m)
        y0 = _snap(y0)
        out.append('p=' + _f(p) + ': ' + _lin(m, y0 - m * p))
        curves.append(_linetree(m, p, y0))
    lo = min(ps) - 3.0
    hi = max(ps) + 3.0
    _plot(curves, lo, hi, 'y', 'tangents to y = ' + _ts(f))
    return out

def _par_var(xt, yt):
    vs = caseng.vars_in(xt) + caseng.vars_in(yt)
    if 't' in vs or not vs:
        return 't'
    if 'x' in vs:
        return 'x'
    return vs[0]

def t_tan_param(xt, yt, t0):
    var = _par_var(xt, yt)
    dx = _dvar(xt, var)
    dy = _dvar(yt, var)
    x0 = _at(xt, t0, var)
    y0 = _at(yt, t0, var)
    u = _at(dx, t0, var)
    v = _at(dy, t0, var)
    if None in (x0, y0, u, v):
        raise ValueError('curve undefined at t = ' + _f(t0))
    x0 = _snap(x0)
    y0 = _snap(y0)
    out = ['point (' + _f(x0) + ', ' + _f(y0) + ')']
    m = _tn_lines(x0, y0, u, v, out)
    out.append(_w(_eqv('dx/dt', dx, u)))
    out.append(_w(_eqv('dy/dt', dy, v)))
    out.append(_w('dy/dx = (dy/dt)/(dx/dt)'))
    curves = [(_inx(xt, var), _inx(yt, var), t0 - PI, t0 + PI)]
    if m is not None:
        curves.append((('+', ('n', x0), X), ('+', ('n', y0), ('*', ('n', m), X)), -3.0, 3.0))
    _plot(curves, t0 - PI, t0 + PI, 'param', 'tangent at t = ' + _f(t0))
    return out

def t_tan_polar(r, th):
    var = _pvar(r, 't', 'x')
    dr = _dvar(r, var)
    r0 = _at(r, th, var)
    q = _at(dr, th, var)
    if r0 is None or q is None:
        raise ValueError('r undefined at theta = ' + _f(th))
    c = math.cos(th)
    s = math.sin(th)
    x0 = _snap(r0 * c)
    y0 = _snap(r0 * s)
    out = ['point (' + _f(x0) + ', ' + _f(y0) + ')']
    u = q * c - r0 * s
    v = q * s + r0 * c
    _tn_lines(x0, y0, u, v, out)
    out.append(_w('r = ' + _f(_snap(r0)) + ', ' + _eqv('dr/dtheta', dr, q)))
    out.append(_w('dy/dx = (r\' sin + r cos)/(r\' cos - r sin)'))
    out.append(_w('x = r cos(theta), y = r sin(theta)'))
    _plot([_inx(r, var)], 0.0, 2.0 * PI, 'polar', 'r = ' + _ts(r))
    return out

def t_tan_implicit(F, x0, y0):
    Fx = _dvar(F, 'x')
    Fy = _dvar(F, 'y')
    env = {'y': y0}
    v = _at(F, x0, 'x', env)
    if v is None:
        raise ValueError('F is undefined at that point')
    out = ['point (' + _f(x0) + ', ' + _f(y0) + ')']
    if abs(v) > 1e-6 * (1.0 + abs(x0) + abs(y0)):
        out.append(_wn('not on the curve: F = ' + _f(v)))
    a = _at(Fx, x0, 'x', env)
    b = _at(Fy, x0, 'x', env)
    if a is None or b is None:
        raise ValueError('cannot differentiate at that point')
    _tn_lines(x0, y0, b, -a, out)
    out.append(_w('dy/dx = -(dF/dx)/(dF/dy)'))
    out.append(_w(_eqv('dF/dx', Fx, a)))
    out.append(_w(_eqv('dF/dy', Fy, b)))
    return out

def t_chord(f, a, b):
    if a == b:
        raise ValueError('a and b must differ')
    var = _pvar(f, 'x')
    tree = _inx(f, var)
    ya = _at(tree, a)
    yb = _at(tree, b)
    if ya is None or yb is None:
        raise ValueError('f is undefined at a or b')
    m = _snap((yb - ya) / (b - a))
    out = ['chord gradient = ' + _f(m),
           'chord ' + _lin(m, ya - m * a),
           _w('through (' + _f(a) + ', ' + _f(_snap(ya)) + ') and (' + _f(b) + ', ' + _f(_snap(yb)) + ')')]
    d = _dvar(tree, 'x')
    mt = _at(d, a)
    if mt is not None:
        out.append("f'(" + _f(a) + ') = ' + _f(_snap(mt)))
        out.append(_w('chords from x = a as the other end closes in:'))
        for h in (1.0, 0.1, 0.01, 0.001):
            v = _at(tree, a + h)
            if v is not None:
                out.append(_w('  b = a+' + _f(h, 1) + ': gradient ' + _f((v - ya) / h, 6)))
    _plot([tree, _linetree(m, a, ya)], min(a, b) - 3.0, max(a, b) + 3.0, 'y', 'chord')
    return out

# polynomials in x, y, r as {(i, j, k): coef} for the polar/cartesian swap

def _pc(c):
    return {(0, 0, 0): c} if c != 0 else {}

def _padd(a, b, s):
    out = {}
    for k in a:
        out[k] = a[k]
    for k in b:
        v = out.get(k, 0) + s * b[k]
        if abs(v) < 1e-12:
            if k in out:
                del out[k]
        else:
            out[k] = v
    return out

def _pmul(a, b):
    out = {}
    for ka in a:
        for kb in b:
            k = (ka[0] + kb[0], ka[1] + kb[1], ka[2] + kb[2])
            out[k] = out.get(k, 0) + a[ka] * b[kb]
    for k in list(out.keys()):
        if abs(out[k]) < 1e-12:
            del out[k]
    return out

def _ppow(a, n):
    out = _pc(1)
    i = 0
    while i < n:
        out = _pmul(out, a)
        i += 1
    return out

def _peq(a, b):
    if len(a) != len(b):
        return False
    for k in a:
        if k not in b or abs(a[k] - b[k]) > 1e-12:
            return False
    return True

def _mono(i, j, k):
    return {(i, j, k): 1}

def _trigk(k):
    # cos(k th), sin(k th) as (poly in x, y)/r^k: Re/Im of (x + iy)^k
    re = _pc(1)
    im = {}
    i = 0
    while i < k:
        re, im = (_padd(_pmul(re, _mono(1, 0, 0)), _pmul(im, _mono(0, 1, 0)), -1),
                  _padd(_pmul(re, _mono(0, 1, 0)), _pmul(im, _mono(1, 0, 0)), 1))
        i += 1
    return re, im

def _kof(arg, tv):
    # k when arg is k*theta with integer 1 <= k <= 6
    if arg == ('v', tv):
        return 1
    if arg[0] == '*' and arg[2] == ('v', tv) and arg[1][0] == 'n':
        k = arg[1][1]
        if k == int(k) and 1 <= k <= 6:
            return int(k)
    return None

def _rf(node, tv):
    # node -> (N, D) polynomials; tv is the polar angle variable, or None for x, y
    vs = caseng.vars_in(node)
    if not vs:
        v = _nodeval(node)
        if v is None or v != v or abs(v) > 1e300:
            raise ValueError('bad constant')
        return (_pc(v), _pc(1))
    t = node[0]
    if t == 'v':
        if tv is None and node[1] == 'x':
            return (_mono(1, 0, 0), _pc(1))
        if tv is None and node[1] == 'y':
            return (_mono(0, 1, 0), _pc(1))
        raise ValueError('cannot convert ' + node[1])
    if t == 'neg':
        a = _rf(node[1], tv)
        return (_padd({}, a[0], -1), a[1])
    if t == '+' or t == '-':
        a = _rf(node[1], tv)
        b = _rf(node[2], tv)
        s = 1 if t == '+' else -1
        if _peq(a[1], b[1]):
            return (_padd(a[0], b[0], s), a[1])
        return (_padd(_pmul(a[0], b[1]), _pmul(b[0], a[1]), s), _pmul(a[1], b[1]))
    if t == '*':
        a = _rf(node[1], tv)
        b = _rf(node[2], tv)
        return (_pmul(a[0], b[0]), _pmul(a[1], b[1]))
    if t == '/':
        a = _rf(node[1], tv)
        b = _rf(node[2], tv)
        if not b[0]:
            raise ValueError('division by zero')
        return (_pmul(a[0], b[1]), _pmul(a[1], b[0]))
    if t == '^':
        e = _nodeval(node[2]) if not caseng.vars_in(node[2]) else None
        if e is None or e != int(e) or abs(e) > 8:
            raise ValueError('only whole-number powers')
        a = _rf(node[1], tv)
        n = int(e)
        if n >= 0:
            return (_ppow(a[0], n), _ppow(a[1], n))
        if not a[0]:
            raise ValueError('division by zero')
        return (_ppow(a[1], -n), _ppow(a[0], -n))
    if tv is not None and t in ('cos', 'sin', 'tan', 'sec', 'cosec', 'cot'):
        k = _kof(node[1], tv)
        if k is None:
            raise ValueError('only trig of k*theta')
        c, s = _trigk(k)
        rk = _mono(0, 0, k)
        if t == 'cos':
            return (c, rk)
        if t == 'sin':
            return (s, rk)
        if t == 'sec':
            return (rk, c)
        if t == 'cosec':
            return (rk, s)
        if t == 'tan':
            return (s, c)
        return (c, s)
    raise ValueError('cannot convert ' + t)

def _unmono(P):
    # divide out the common monomial factor
    if not P:
        return P
    lo = None
    for k in P:
        lo = list(k) if lo is None else [min(lo[0], k[0]), min(lo[1], k[1]), min(lo[2], k[2])]
    out = {}
    for k in P:
        out[(k[0] - lo[0], k[1] - lo[1], k[2] - lo[2])] = P[k]
    return out

def _pnorm(P):
    # leading coefficient positive, integer coefficients when rational
    if not P:
        return P
    keys = sorted(P.keys(), key=lambda k: (-(k[0] + k[1] + k[2]), -k[0], -k[1]))
    lead = P[keys[0]]
    den = 1
    for k in P:
        q = 1
        while q <= 60:
            v = P[k] * q
            if abs(v - int(v + (0.5 if v >= 0 else -0.5))) < 1e-9:
                break
            q += 1
        if q <= 60:
            den = den * q // casutil.gcd(den, q)
    g = 0
    for k in P:
        v = P[k] * den
        iv = int(v + (0.5 if v >= 0 else -0.5))
        if abs(v - iv) > 1e-9:
            g = 0
            break
        g = casutil.gcd(g, abs(iv)) if g else abs(iv)
    s = den * 1.0 / g if g else 1.0 / abs(lead)
    if lead < 0:
        s = -s
    out = {}
    for k in P:
        out[k] = casutil.clean(_snap(P[k] * s))
    return out

def _pstr(P, names):
    if not P:
        return '0'
    keys = sorted(P.keys(), key=lambda k: (-(k[0] + k[1] + k[2]), -k[0], -k[1]))
    s = ''
    for k in keys:
        c = P[k]
        body = ''
        for i in range(3):
            if k[i] == 1:
                body += names[i]
            elif k[i] > 1:
                body += names[i] + '^' + str(k[i])
        mag = abs(c)
        cs = _f(mag)
        if body and mag == 1:
            piece = body
        elif body:
            piece = ('(' + cs + ')' if ('/' in cs or 'sqrt' in cs) else cs) + body
        else:
            piece = cs
        if s == '':
            s = ('-' if c < 0 else '') + piece
        else:
            s += (' - ' if c < 0 else ' + ') + piece
    return s

def _chunks(s, n):
    # split a long sum at its + and - signs into lines of <= n chars
    parts = []
    cur = ''
    for tok in s.split(' '):
        if len(cur) + len(tok) + 1 > n and cur:
            parts.append(cur)
            cur = tok
        else:
            cur = tok if cur == '' else cur + ' ' + tok
    if cur:
        parts.append(cur)
    return parts

def _eqlines(s, rhs):
    whole = s + ' = ' + rhs
    if len(whole) <= 34:
        return [whole]
    out = []
    for p in _chunks(whole, 34):
        out.append(p)
    return out

TH = ('v', 'theta')

def _trigtree(terms):
    # terms [(coef, node)] -> sum tree
    node = None
    for c, body in terms:
        c = casutil.clean(_snap(c))
        piece = _nn(abs(c)) if body is None else (body if abs(c) == 1 else ('*', _nn(abs(c)), body))
        if node is None:
            node = ('neg', piece) if c < 0 else piece
        else:
            node = ('-', node, piece) if c < 0 else ('+', node, piece)
    return node if node is not None else ('n', 0)

def _ptrig(Pd, d):
    # homogeneous degree-d terms {(i, j): c} as a function of theta: tree
    mono = []
    for ij in sorted(Pd.keys(), key=lambda k: -k[0]):
        i, j = ij
        body = None
        if i:
            body = ('cos', TH) if i == 1 else ('^', ('cos', TH), ('n', i))
        if j:
            sj = ('sin', TH) if j == 1 else ('^', ('sin', TH), ('n', j))
            body = sj if body is None else ('*', body, sj)
        mono.append((Pd[ij], body))
    n = 4 * d + 4
    vals = []
    q = 0
    while q < n:
        th = 2.0 * PI * q / n
        c = math.cos(th)
        s = math.sin(th)
        v = 0.0
        for ij in Pd:
            v += Pd[ij] * c ** ij[0] * s ** ij[1]
        vals.append(v)
        q += 1
    four = []
    k = 0
    while k <= d:
        ak = 0.0
        bk = 0.0
        q = 0
        while q < n:
            th = 2.0 * PI * q / n
            ak += vals[q] * math.cos(k * th)
            bk += vals[q] * math.sin(k * th)
            q += 1
        ak = ak / n if k == 0 else 2.0 * ak / n
        bk = 2.0 * bk / n
        arg = TH if k == 1 else ('*', ('n', k), TH)
        if abs(ak) > 1e-9:
            four.append((ak, None if k == 0 else ('cos', arg)))
        if abs(bk) > 1e-9:
            four.append((bk, ('sin', arg)))
        k += 1
    pick = four if len(four) <= len(mono) else mono
    return _trigtree(pick)

def t_cart_to_polar(F):
    try:
        N, D = _rf(F, None)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError('needs a polynomial/rational F(x, y)')
    if not N:
        return ['F is identically 0']
    groups = {}
    for k in N:
        d = k[0] + k[1]
        if d not in groups:
            groups[d] = {}
        groups[d][(k[0], k[1])] = N[k]
    degs = sorted(groups.keys())
    low = degs[0]
    out = []
    trees = {}
    for d in degs:
        trees[d] = _ptrig(groups[d], d)
    if len(degs) == 1:
        s = caseng.tostr(caseng.simplify(trees[low]))
        out.append(s + ' = 0')
        out.append(_w('only lines through the pole: r is free'))
    elif len(degs) == 2:
        hi = degs[1]
        p = hi - low
        rhs = caseng.simplify(('/', ('neg', trees[low]), trees[hi]))
        lhs = 'r' if p == 1 else 'r^' + str(p)
        s = _ts(rhs)
        if len(lhs + s) <= 30:
            out.append(lhs + ' = ' + s)
        else:
            out.append(lhs + ' =')
            out.append(_m(rhs))
        v = _nodeval(rhs) if not caseng.vars_in(rhs) else None
        if v is not None and p == 2 and v > 0:
            out.append('r = ' + _f(math.sqrt(v)))
    else:
        s = ''
        for d in reversed(degs):
            rp = '' if d == low else ('r' if d - low == 1 else 'r^' + str(d - low))
            ts = _ts(caseng.simplify(trees[d]))
            if rp and ts in ('1', '-1'):
                piece = ts[:-1] + rp
            else:
                piece = '(' + ts + ')' + ('*' + rp if rp else '')
            s = piece if s == '' else s + ' + ' + piece
        out.extend(_eqlines(s, '0'))
    if low > 0:
        out.append(_w('divided by r' + ('' if low == 1 else '^' + str(low)) + ' (r = 0 is the pole)'))
    out.append(_w('x = r cos(theta), y = r sin(theta)'))
    if D != _pc(1) and len(D) > 0 and not (len(D) == 1 and (0, 0, 0) in D):
        out.append(_wn('assumes the denominator is not 0'))
    return out

def t_polar_to_cart(r):
    var = _pvar(r, 't', 'x')
    try:
        N, D = _rf(r, var)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError('needs r built from cos, sin, tan of k*theta')
    E = _unmono(_padd(_pmul(_mono(0, 0, 1), D), N, -1))
    A = {}
    B = {}
    rr = {(2, 0, 0): 1, (0, 2, 0): 1}
    for k in E:
        base = {(k[0], k[1], 0): E[k]}
        e = k[2]
        if e % 2 == 0:
            A = _padd(A, _pmul(base, _ppow(rr, e // 2)), 1)
        else:
            B = _padd(B, _pmul(base, _ppow(rr, (e - 1) // 2)), 1)
    out = []
    if B:
        P = _padd(_pmul(A, A), _pmul(rr, _pmul(B, B)), -1)
    else:
        P = A
    P = _pnorm(P)
    out.extend(_eqlines(_pstr(P, ('x', 'y', 'r')), '0'))
    if B:
        out.append(_wn('squared to remove r: check r >= 0'))
        nm = ('x', 'y', 'r')
        if len(B) == 1 and (0, 0, 0) in B:
            b = B[(0, 0, 0)]
            neg = {}
            for k in A:
                neg[k] = casutil.clean(_snap(-A[k] / b))
            out.append(_w('from r = ' + _pstr(neg, nm)))
        else:
            out.append(_w('from r(' + _pstr(B, nm) + ') = ' + _pstr(_padd({}, A, -1), nm)))
    out.append(_w('cos = x/r, sin = y/r, r^2 = x^2 + y^2'))
    return out

def _arc(integ, a, b, var, head):
    a = float(a)
    b = float(b)
    v1 = None
    v2 = None
    try:
        v1 = cascalc.defint(integ, a, b, False, 200, var)
        v2 = cascalc.defint(integ, a, b, False, 800, var)
    except Exception:
        v2 = None
    if v2 is None or v2 != v2:
        raise ValueError('integrand undefined in that range')
    val = v2
    exact = False
    try:
        F = cascalc.integ(integ, var)
    except Exception:
        F = None
    if F is not None:
        hi = _at(F, b, var)
        lo = _at(F, a, var)
        if hi is not None and lo is not None and abs((hi - lo) - v2) < 1e-6 * (1.0 + abs(v2)):
            val = hi - lo
            exact = True
    out = ['s = ' + (_f(val) if exact else casutil.sf3(val))]
    if exact and _f(val) != casutil.sf3(val):
        out.append('  = ' + casutil.sf3(val))
    for ln in head:
        out.append(_w(ln))
    out.append(_w('from ' + _f(a) + ' to ' + _f(b)))
    if exact:
        out.append(_mw(_tidy(F)))
    else:
        if _f(val) != casutil.sf3(val):
            out.append(_w('numerically matches ' + _f(val)))
        if v1 is not None:
            out.append(_w('Simpson 800 panels; change on halving h ' + _f(abs(v2 - v1), 3)))
    return out

def _sq(t):
    return caseng.simplify(('^', t, ('n', 2)))

def t_arc_cart(f, a, b):
    a, b = _order(a, b)
    var = _pvar(f, 'x')
    d = _dvar(f, var)
    integ = ('sqrt', ('+', ('n', 1), _sq(d)))
    return _arc(integ, a, b, var, ['s = int sqrt(1 + (dy/dx)^2) dx', 'dy/dx = ' + _ts(d)])

def t_arc_param(xt, yt, a, b):
    a, b = _order(a, b)
    var = _par_var(xt, yt)
    dx = _dvar(xt, var)
    dy = _dvar(yt, var)
    integ = ('sqrt', ('+', _sq(dx), _sq(dy)))
    return _arc(integ, a, b, var, ["s = int sqrt(x'^2 + y'^2) dt",
                                   'dx/dt = ' + _ts(dx), 'dy/dt = ' + _ts(dy)])

def t_arc_polar(r, a, b):
    a, b = _order(a, b)
    var = _pvar(r, 't', 'x')
    dr = _dvar(r, var)
    integ = ('sqrt', ('+', _sq(r), _sq(dr)))
    return _arc(integ, a, b, var, ['s = int sqrt(r^2 + (dr/dtheta)^2) dtheta',
                                   'dr/dtheta = ' + _ts(dr)])

# ---- D  exploring differential equations ------------------------------------
# c4 c5 c6 c7 c8 c9 c10 Tc1 (c3 modelling is judgement: no tool)

def _fxy(f, x, y):
    x = float(x)
    y = float(y)
    try:
        v = caseng.evalf(f, x, False, {'x': x, 'y': y})
    except Exception:
        raise ValueError('cannot evaluate f at x = ' + _f(x) + ', y = ' + _f(y, 4))
    if isinstance(v, complex) or v != v or v > 1e300 or v < -1e300:
        raise ValueError('cannot evaluate f at x = ' + _f(x) + ', y = ' + _f(y, 4))
    return v

def _st_euler(f, x, y, h):
    return y + h * _fxy(f, x, y)

def _st_heun(f, x, y, h):
    k1 = _fxy(f, x, y)
    k2 = _fxy(f, x + h, y + h * k1)
    return y + h * (k1 + k2) / 2.0

def _st_mid(f, x, y, h):
    k1 = _fxy(f, x, y)
    k2 = _fxy(f, x + h / 2.0, y + h * k1 / 2.0)
    return y + h * k2

def _st_rk4(f, x, y, h):
    k1 = _fxy(f, x, y)
    k2 = _fxy(f, x + h / 2.0, y + h * k1 / 2.0)
    k3 = _fxy(f, x + h / 2.0, y + h * k2 / 2.0)
    k4 = _fxy(f, x + h, y + h * k3)
    return y + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

def _march(f, x0, y0, h, n, step):
    y = y0
    i = 0
    while i < n:
        y = step(f, x0 + i * h, y, h)
        if y != y or y > 1e300 or y < -1e300:
            raise ValueError('the solution blows up')
        i += 1
    return y

def _hn(h, n, cap):
    n = _iv(n, 'n', 1, cap)
    if h == 0:
        raise ValueError('h must not be zero')
    return n

def t_euler(f, x0, y0, h, n):
    n = _hn(h, n, 50)
    out = []
    rows = []
    y = y0
    i = 0
    while i < n:
        x = x0 + i * h
        s = _fxy(f, x, y)
        y = y + h * s
        rows.append(_w('x=' + _f(_snap(x + h), 6) + '  y=' + _f(y, 6) + '  (slope ' + _f(s, 4) + ')'))
        i += 1
    out.append('y(' + _f(_snap(x0 + n * h), 6) + ') = ' + casutil.sf3(y))
    out.append(_w('y(r+1) = y(r) + h f(x(r), y(r))'))
    out.append(_w('x=' + _f(x0) + '  y=' + _f(y0, 6)))
    return out + rows

def t_euler_halve(f, x0, y0, X1, n):
    n = _iv(n, 'n', 1, 100)
    if X1 == x0:
        raise ValueError('X must differ from x0')
    out = []
    vals = []
    k = 0
    while k < 4:
        m = n * (2 ** k)
        h = (X1 - x0) / m
        v = _march(f, x0, y0, h, m, _st_euler)
        vals.append(v)
        out.append('h=' + _f(_snap(h * 1e9) / 1e9) + ': y(X) = ' + _f(v, 6))
        k += 1
    ref = _march(f, x0, y0, (X1 - x0) / (8 * n), 8 * n, _st_rk4)
    out.append('RK4 with h/8: ' + _f(ref, 6))
    d1 = vals[1] - vals[0]
    d2 = vals[2] - vals[1]
    d3 = vals[3] - vals[2]
    out.append(_w('changes: ' + _f(d1, 3) + ', ' + _f(d2, 3) + ', ' + _f(d3, 3)))
    if abs(d3) > 1e-15 and abs(d2) > 1e-15:
        out.append(_w('ratios: ' + _f(d1 / d2, 3) + ', ' + _f(d2 / d3, 3)))
    out.append(_w('halving h roughly halves the error: Euler'))
    out.append(_w('is first order (ratio of changes -> 2)'))
    out.append(_w('extrapolated 2y(h/8) - y(h/4) = ' + _f(2 * vals[3] - vals[2], 6)))
    return out

def _rk_table(f, x0, y0, h, n, kind):
    out = []
    y = y0
    i = 0
    while i < n:
        x = x0 + i * h
        k1 = _fxy(f, x, y)
        if kind == 'heun':
            k2 = _fxy(f, x + h, y + h * k1)
            y = y + h * (k1 + k2) / 2.0
            ks = 'k1=' + _f(k1, 5) + ' k2=' + _f(k2, 5)
        elif kind == 'mid':
            k2 = _fxy(f, x + h / 2.0, y + h * k1 / 2.0)
            y = y + h * k2
            ks = 'k1=' + _f(k1, 5) + ' k2=' + _f(k2, 5)
        else:
            k2 = _fxy(f, x + h / 2.0, y + h * k1 / 2.0)
            k3 = _fxy(f, x + h / 2.0, y + h * k2 / 2.0)
            k4 = _fxy(f, x + h, y + h * k3)
            y = y + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            ks = 'k ' + _f(k1, 4) + ', ' + _f(k2, 4) + ', ' + _f(k3, 4) + ', ' + _f(k4, 4)
        if y != y or y > 1e300 or y < -1e300:
            raise ValueError('the solution blows up')
        out.append(_w('x=' + _f(_snap(x + h), 6) + '  y=' + _f(y, 8)))
        out.append(_w('  ' + ks))
        i += 1
    return y, out

def t_rk2_heun(f, x0, y0, h, n):
    n = _hn(h, n, 50)
    y, rows = _rk_table(f, x0, y0, h, n, 'heun')
    out = ['y(' + _f(_snap(x0 + n * h), 6) + ') = ' + casutil.sf3(y),
           _w('k1 = f(x, y), k2 = f(x+h, y+h k1)'),
           _w('y(r+1) = y(r) + h(k1 + k2)/2')]
    return out + rows

def t_rk2_mid(f, x0, y0, h, n):
    n = _hn(h, n, 50)
    y, rows = _rk_table(f, x0, y0, h, n, 'mid')
    out = ['y(' + _f(_snap(x0 + n * h), 6) + ') = ' + casutil.sf3(y),
           _w('k1 = f(x, y), k2 = f(x+h/2, y+h k1/2)'),
           _w('y(r+1) = y(r) + h k2')]
    return out + rows

def t_rk4(f, x0, y0, h, n):
    n = _hn(h, n, 50)
    y, rows = _rk_table(f, x0, y0, h, n, 'rk4')
    out = ['y(' + _f(_snap(x0 + n * h), 6) + ') = ' + _f(y, 6),
           _w('k1 = f(x, y), k2 = f(x+h/2, y+h k1/2)'),
           _w('k3 = f(x+h/2, y+h k2/2), k4 = f(x+h, y+h k3)'),
           _w('y(r+1) = y(r) + h(k1 + 2k2 + 2k3 + k4)/6')]
    return out + rows

def t_compare(f, x0, y0, h, n):
    n = _hn(h, n, 200)
    X1 = _snap(x0 + n * h)
    e = _march(f, x0, y0, h, n, _st_euler)
    r2 = _march(f, x0, y0, h, n, _st_heun)
    r4 = _march(f, x0, y0, h, n, _st_rk4)
    out = ['at x = ' + _f(X1) + ':',
           'Euler y = ' + _f(e, 6),
           'RK2 y = ' + _f(r2, 6),
           'RK4 y = ' + _f(r4, 6)]
    e2 = _march(f, x0, y0, h / 2.0, 2 * n, _st_euler)
    q2 = _march(f, x0, y0, h / 2.0, 2 * n, _st_heun)
    q4 = _march(f, x0, y0, h / 2.0, 2 * n, _st_rk4)
    out.append(_w('with h/2: Euler ' + _f(e2, 6) + ', RK2 ' + _f(q2, 6)))
    out.append(_w('          RK4 ' + _f(q4, 8)))
    out.append(_w('change on halving: Euler ' + _f(e2 - e, 3) + ', RK2 ' + _f(q2 - r2, 3)))
    out.append(_w('                   RK4 ' + _f(q4 - r4, 3)))
    out.append(_w('halving h divides the error by about'))
    out.append(_w('2 (Euler), 4 (RK2), 16 (RK4)'))
    out.append(_w('RK2 here: k2 = f(x+h, y+h k1), mean slope'))
    return out

FIELD_NX = 13
FIELD_NY = 9
FIELD_PX = 12.0

def t_field(f, xlo, xhi, ylo, yhi, x0, y0):
    xlo, xhi = _order(xlo, xhi)
    ylo, yhi = _order(ylo, yhi)
    if (x0 is None) != (y0 is None):
        raise ValueError('give both x0 and y0, or neither')
    sx = 383.0 / (xhi - xlo)
    sy = 162.0 / (yhi - ylo)
    dashes = []
    drawn = 0
    j = 0
    while j < FIELD_NY:
        y = ylo + (yhi - ylo) * (j + 0.5) / FIELD_NY
        i = 0
        while i < FIELD_NX:
            x = xlo + (xhi - xlo) * (i + 0.5) / FIELD_NX
            i += 1
            try:
                m = _fxy(f, x, y)
            except ValueError:
                continue
            if m > 1e6:
                m = 1e6
            if m < -1e6:
                m = -1e6
            ux = sx
            uy = m * sy
            nrm = math.sqrt(ux * ux + uy * uy)
            dxw = ux / nrm * FIELD_PX / 2.0 / sx
            dyw = uy / nrm * FIELD_PX / 2.0 / sy
            if dashes:
                dashes.append(None)
            dashes.append((x - dxw, y - dyw))
            dashes.append((x + dxw, y + dyw))
            drawn += 1
        j += 1
    out = ['dashes drawn: ' + str(drawn) + ' of ' + str(FIELD_NX * FIELD_NY)]
    curves = [dashes] if dashes else []
    if x0 is not None:
        halves = {}
        for end, name in ((xhi, 'forward'), (xlo, 'back')):
            pts = []
            halves[name] = pts
            if end == x0:
                continue
            steps = 80
            h = (end - x0) / steps
            y = y0
            last = x0
            ok = True
            i = 0
            while i < steps:
                try:
                    y = _st_rk4(f, x0 + i * h, y, h)
                except ValueError:
                    ok = False
                    break
                if y != y or abs(y) > 1e12:
                    ok = False
                    break
                last = x0 + (i + 1) * h
                if ylo - (yhi - ylo) <= y <= yhi + (yhi - ylo):
                    pts.append((last, y))
                elif pts and pts[len(pts) - 1] is not None:
                    pts.append(None)
                i += 1
            if ok:
                out.append('y(' + _f(_snap(last)) + ') = ' + _f(y, 6))
            else:
                out.append(_wn(name + ' solution stops at x = ' + _f(last, 4)))
        back = halves.get('back', [])
        path = []
        k = len(back) - 1
        while k >= 0:
            path.append(back[k])
            k -= 1
        path.append((x0, y0))
        curves.append(path + halves.get('forward', []))
        out.append(_w('solution through (' + _f(x0) + ', ' + _f(y0) + ') by RK4'))
    out.append(_w('grid ' + str(FIELD_NX) + ' x ' + str(FIELD_NY) + '; each dash has slope f(x, y)'))
    if curves:
        _plot(curves, xlo, xhi, 'lines', 'dy/dx = ' + _ts(f), ylo, yhi)
    return out

VDE_X = [-1.3, -0.4, 0.35, 0.9, 1.7]

def t_verify(y, F):
    d1 = _dvar(y, 'x')
    d2 = _dvar(d1, 'x')
    out = []
    sym = None
    try:
        s = caseng.subst(F, 'q', d2)
        s = caseng.subst(s, 'p', d1)
        s = caseng.subst(s, 'y', y)
        sym = _tidy(caseng.simplify(s))
        try:
            sym = caspoly.collect(sym)
        except Exception:
            pass
    except Exception:
        sym = None
    worst = 0.0
    tested = 0
    for xv in VDE_X:
        yv = _at(y, xv)
        pv = _at(d1, xv)
        qv = _at(d2, xv)
        if None in (yv, pv, qv):
            continue
        rv = _at(F, xv, 'x', {'y': yv, 'p': pv, 'q': qv})
        if rv is None:
            continue
        rel = abs(rv) / (1.0 + abs(yv) + abs(pv) + abs(qv))
        if rel > worst:
            worst = rel
        tested += 1
    if tested == 0:
        out.append('not checked')
        out.append(_wn('the equation could not be evaluated'))
    elif (sym is not None and sym == ('n', 0)) or worst < 1e-9:
        out.append('verified: y is a solution')
    else:
        out.append('not a solution')
    if sym is not None:
        s = _ts(sym)
        out.append(_w('F after substituting: ' + (s if len(s) <= 28 else s[:26] + '..')))
    out.append(_w('dy/dx = ' + _ts(d1)))
    out.append(_w('d2y/dx2 = ' + _ts(d2)))
    out.append(_w('checked at ' + str(tested) + ' x values, worst'))
    out.append(_w('relative residual ' + _f(worst, 3)))
    out.append(_w('equation typed as F = 0, p = dy/dx, q = d2y/dx2'))
    return out

def _csolve(yc, x0, y0):
    def g(c):
        v = _at(yc, c, 'c', {'x': x0})
        return None if v is None else v - y0
    g0 = g(0.0)
    g1 = g(1.0)
    g2 = g(2.0)
    if None not in (g0, g1, g2) and abs(g2 - 2 * g1 + g0) < 1e-9 * (1 + abs(g1)) and g1 != g0:
        return [_snap(-g0 / (g1 - g0))], True
    rs = _scan(g, -50.0, 50.0, 1000)
    return rs, False

def t_particular(yc, x0, y0):
    if 'c' not in caseng.vars_in(yc):
        raise ValueError('the general solution must use c')
    cs, lin = _csolve(yc, x0, y0)
    if not cs:
        return ['no c found', _wn('searched c from -50 to 50')]
    out = []
    for c in cs[:3]:
        out.append('c = ' + _f(c))
        p = _tidy(caseng.subst(yc, 'c', _nn(c)))
        s = _ts(p)
        if len(s) <= 30:
            out.append('y = ' + s)
        else:
            out.append(_m(p))
    out.append(_w('from y(' + _f(x0) + ') = ' + _f(y0)))
    if not lin:
        out.append(_wn('c found numerically in -50..50'))
    return out

def t_sol_family(yc, xlo, xhi, cs):
    lo, hi = _order(xlo, xhi)
    curves, out = _family(yc, 'c', cs, lo, hi)
    _plot(curves, lo, hi, 'y', 'y = ' + _ts(yc))
    return out

# ---- N  number theory -----------------------------------------------------------
# T3 T4 T5 T6 T7 T8 T9 T10

NT_MAX = 10 ** 10

def _gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def _egcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t

def _powmod(a, b, m):
    r = 1 % m
    a = a % m
    while b > 0:
        if b & 1:
            r = (r * a) % m
        a = (a * a) % m
        b >>= 1
    return r

def _big(n, name):
    if n > NT_MAX:
        raise ValueError(name + ' too large (max 10^10)')

def _factors(n):
    facs = []
    m = n
    d = 2
    while d * d <= m:
        e = 0
        while m % d == 0:
            m //= d
            e += 1
        if e:
            facs.append((d, e))
        d = 3 if d == 2 else d + 2
    if m > 1:
        facs.append((m, 1))
    return facs

def _isprime(n):
    if n < 2:
        return False
    f = _factors(n)
    return len(f) == 1 and f[0][1] == 1

def _fstr(facs):
    parts = []
    for p, e in facs:
        parts.append(str(p) if e == 1 else str(p) + '^' + str(e))
    return ' * '.join(parts)

def _long(label, v):
    # a long integer split over lines
    s = str(v)
    out = [label + s[:30]]
    i = 30
    while i < len(s):
        out.append('    ' + s[i:i + 30])
        i += 30
    return out

def t_gcd(a, b):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    b = _iv(b, 'b', -NT_MAX, NT_MAX)
    if a == 0 and b == 0:
        raise ValueError('a and b cannot both be 0')
    g = _gcd(a, b)
    l = abs(a * b) // g
    out = ['gcd = ' + str(g), 'lcm = ' + str(l)]
    out.append(_w('gcd x lcm = |a b| = ' + str(abs(a * b))))
    if a and b and abs(a) <= NT_MAX and abs(b) <= NT_MAX:
        out.append(_w(str(abs(a)) + ' = ' + (_fstr(_factors(abs(a))) if abs(a) > 1 else '1')))
        out.append(_w(str(abs(b)) + ' = ' + (_fstr(_factors(abs(b))) if abs(b) > 1 else '1')))
    if g == 1:
        out.append(_w('coprime'))
    return out

def t_euclid(a, b):
    a = _iv(a, 'a', 1, NT_MAX)
    b = _iv(b, 'b', 1, NT_MAX)
    g, u, v = _egcd(a, b)
    out = ['gcd(' + str(a) + ', ' + str(b) + ') = ' + str(g),
           str(g) + ' = ' + str(a) + '(' + str(u) + ') + ' + str(b) + '(' + str(v) + ')']
    p, q = a, b
    k = 0
    while q and k < 40:
        out.append(_w(str(p) + ' = ' + str(p // q) + ' x ' + str(q) + ' + ' + str(p % q)))
        p, q = q, p % q
        k += 1
    out.append(_w('last non-zero remainder is the gcd;'))
    out.append(_w('back-substitute for the Bezout pair'))
    return out

def t_prime(n):
    n = _iv(n, 'n', -NT_MAX, NT_MAX)
    if n < 2:
        return [str(n) + ' is not prime', _w('primes are whole numbers >= 2')]
    facs = _factors(n)
    if len(facs) == 1 and facs[0][1] == 1:
        return [str(n) + ' is prime',
                _w('no divisor from 2 to ' + str(int(math.sqrt(n)) + 1))]
    return [str(n) + ' is not prime',
            'smallest factor ' + str(facs[0][0]),
            _w(str(n) + ' = ' + _fstr(facs))]

def t_factor(n):
    n = _iv(n, 'n', 2, NT_MAX)
    facs = _factors(n)
    out = _long(str(n) + ' = ', _fstr(facs))
    if len(facs) == 1 and facs[0][1] == 1:
        out.append('n is prime')
    nd = 1
    sd = 1
    for p, e in facs:
        nd *= e + 1
        sd *= (p ** (e + 1) - 1) // (p - 1)
    out.append('number of divisors ' + str(nd))
    out.append(_w('sum of divisors ' + str(sd)))
    out.append(_w('trial division by 2, 3, 5, 7, ... to sqrt n'))
    return out

def t_totient(n):
    n = _iv(n, 'n', 1, NT_MAX)
    facs = _factors(n) if n > 1 else []
    r = n
    for p, e in facs:
        r = r // p * (p - 1)
    out = ['phi(' + str(n) + ') = ' + str(r)]
    if facs:
        s = str(n)
        for p, e in facs:
            s += '(1-1/' + str(p) + ')'
        out.append(_w('phi = ' + s))
    if len(facs) == 1 and facs[0][1] == 1:
        out.append(_w('n prime: phi(n) = n - 1'))
    out.append(_w('counts 1..n coprime to n; a^phi(n) = 1'))
    out.append(_w('(mod n) when gcd(a, n) = 1 (Euler)'))
    return out

def t_powmod(a, b, m):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    b = _iv(b, 'b', 0, 10 ** 12)
    m = _iv(m, 'm', 1, NT_MAX)
    out = [str(a) + '^' + str(b) + ' mod ' + str(m) + ' = ' + str(_powmod(a, b, m))]
    bits = ''
    t = b
    while t:
        bits = str(t & 1) + bits
        t >>= 1
    out.append(_w('b in binary: ' + (bits or '0')))
    sq = a % m
    k = 0
    while k < len(bits) and k < 12:
        out.append(_w('  a^' + str(2 ** k) + ' = ' + str(sq) + ' (mod ' + str(m) + ')'))
        sq = sq * sq % m
        k += 1
    out.append(_w('multiply the powers for the 1 bits'))
    return out

def t_modinv(a, m):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    m = _iv(m, 'm', 2, NT_MAX)
    g, x, y = _egcd(a % m, m)
    if g != 1:
        return ['no inverse', _wn('gcd(a, m) = ' + str(g) + ', not 1')]
    inv = x % m
    return ['inverse = ' + str(inv),
            _w(str(a) + ' x ' + str(inv) + ' = ' + str(a * inv) + ' = 1 (mod ' + str(m) + ')'),
            _w('from Euclid: ' + str(a % m) + '(' + str(x) + ') + ' + str(m) + '(' + str(y) + ') = 1')]

def t_lincong(a, b, m):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    b = _iv(b, 'b', -NT_MAX, NT_MAX)
    m = _iv(m, 'm', 2, NT_MAX)
    g, x, y = _egcd(a % m, m)
    if b % g:
        return ['no solution', _wn('gcd(a, m) = ' + str(g) + ' does not divide ' + str(b))]
    mg = m // g
    x0 = (x * (b // g)) % mg
    out = ['x = ' + str(x0) + ' (mod ' + str(mg) + ')']
    if g > 1:
        sols = [str(x0 + k * mg) for k in range(min(g, 8))]
        out.append(str(g) + ' solutions mod ' + str(m) + ':')
        out.append(', '.join(sols) + (', ...' if g > 8 else ''))
    out.append(_w('gcd(a, m) = ' + str(g) + '; divide through, then'))
    out.append(_w('multiply by the inverse of a/g mod m/g'))
    return out

def t_crt(a1, m1, a2, m2):
    a1 = _iv(a1, 'a1', -NT_MAX, NT_MAX)
    a2 = _iv(a2, 'a2', -NT_MAX, NT_MAX)
    m1 = _iv(m1, 'm1', 1, NT_MAX)
    m2 = _iv(m2, 'm2', 1, NT_MAX)
    g, u, v = _egcd(m1, m2)
    if (a2 - a1) % g:
        return ['no solution', _wn('a1 and a2 differ mod gcd = ' + str(g))]
    l = m1 // g * m2
    k = ((a2 - a1) // g * u) % (m2 // g)
    x = (a1 + m1 * k) % l
    return ['x = ' + str(x) + ' (mod ' + str(l) + ')',
            _w('x = a1 + m1 k with m1 k = a2 - a1 (mod m2)'),
            _w('k = ' + str(k) + '; check ' + str(x % m1) + ' mod ' + str(m1) +
               ', ' + str(x % m2) + ' mod ' + str(m2))]

def t_fermat(a, p):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    p = _iv(p, 'p', 2, NT_MAX)
    r = _powmod(a, p - 1, p)
    out = ['a^(p-1) mod p = ' + str(r)]
    g = _gcd(a, p)
    pr = _isprime(p)
    if g != 1:
        out.append(_wn('gcd(a, p) = ' + str(g) + ': Fermat does not apply'))
    elif r != 1:
        out.append('not 1, so p is composite')
    elif pr:
        out.append('= 1, as Fermat says (p prime)')
    else:
        out.append('= 1 but p is composite:')
        out.append('a pseudoprime base ' + str(a))
    out.append(_w('p is ' + ('prime' if pr else 'not prime')))
    out.append(_w('Fermat: a^(p-1) = 1 (mod p) for prime p'))
    out.append(_w('not dividing a'))
    return out

WILSON_MAX = 100000

def t_wilson(p):
    p = _iv(p, 'p', 2, WILSON_MAX)
    w = 1
    i = 2
    while i < p:
        w = (w * i) % p
        i += 1
    out = ['(p-1)! mod p = ' + str(w)]
    if w == p - 1:
        out.append('= -1 (mod p): p is prime')
    else:
        out.append('not -1 (mod p): p is not prime')
    out.append(_w('Wilson: (p-1)! = -1 (mod p) exactly'))
    out.append(_w('when p is prime; -1 mod p = ' + str(p - 1)))
    return out

PY_MAX = 10000
PY_LIST = 40

def t_pythag(cmax):
    lim = _iv(cmax, 'c max', 5, PY_MAX)
    trs = []
    m = 2
    while m * m + 1 <= lim:
        n = 1
        while n < m:
            if (m - n) % 2 == 1 and _gcd(m, n) == 1:
                c = m * m + n * n
                if c <= lim:
                    a = m * m - n * n
                    b = 2 * m * n
                    if a > b:
                        a, b = b, a
                    trs.append((c, a, b))
            n += 1
        m += 1
    trs.sort()
    out = ['primitive triples: ' + str(len(trs))]
    for c, a, b in trs[:PY_LIST]:
        out.append(str(a) + ', ' + str(b) + ', ' + str(c))
    if len(trs) > PY_LIST:
        out.append(_w('first ' + str(PY_LIST) + ' shown'))
    out.append(_w('(m^2-n^2, 2mn, m^2+n^2), m > n coprime,'))
    out.append(_w('opposite parity; others are multiples'))
    return out

def t_triple(m, n):
    m = _iv(m, 'm', 1, 10 ** 6)
    n = _iv(n, 'n', 1, 10 ** 6)
    if n >= m:
        raise ValueError('need m > n')
    a = m * m - n * n
    b = 2 * m * n
    c = m * m + n * n
    out = ['(' + str(a) + ', ' + str(b) + ', ' + str(c) + ')']
    prim = _gcd(m, n) == 1 and (m - n) % 2 == 1
    out.append('primitive' if prim else 'not primitive')
    if not prim:
        g = _gcd(_gcd(a, b), c)
        out.append(_w(str(g) + ' x (' + str(a // g) + ', ' + str(b // g) + ', ' + str(c // g) + ')'))
    out.append(_w(str(a) + '^2 + ' + str(b) + '^2 = ' + str(a * a + b * b) + ' = ' + str(c) + '^2'))
    return out

def _isqrt(n):
    if n < 2:
        return n
    x = int(math.sqrt(n))
    while x * x > n:
        x -= 1
    while (x + 1) * (x + 1) <= n:
        x += 1
    return x

def t_pell(n):
    n = _iv(n, 'n', 2, 100000)
    a0 = _isqrt(n)
    if a0 * a0 == n:
        return ['only x = 1, y = 0', _wn(str(n) + ' is a perfect square')]
    m = 0
    d = 1
    a = a0
    hp, h = 1, a0
    kp, k = 0, 1
    steps = 0
    cf = [a0]
    while h * h - n * k * k != 1 and steps < 4000:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        if len(cf) < 8:
            cf.append(a)
        h, hp = a * h + hp, h
        k, kp = a * k + kp, k
        steps += 1
    if h * h - n * k * k != 1:
        return ['no solution found', _wn('4000 continued-fraction steps')]
    out = _long('x = ', h) + _long('y = ', k)
    out.append(_w('check x^2 - ' + str(n) + 'y^2 = ' + str(h * h - n * k * k)))
    out.append(_w('sqrt(' + str(n) + ') = [' + str(cf[0]) + '; ' +
                  ', '.join([str(c) for c in cf[1:]]) + (', ...' if steps >= 7 else '') + ']'))
    out.append(_w('next from (x + y sqrt n)^j:'))
    xx, yy = h, k
    j = 2
    while j <= 3:
        xx, yy = h * xx + n * k * yy, h * yy + k * xx
        for ln in _long('j=' + str(j) + ' x = ', xx) + _long('     y = ', yy):
            out.append(_w(ln))
        j += 1
    return out

def _tterm(v):
    if v == 0:
        return ''
    if v < 0:
        return ' - ' + (str(-v) if v != -1 else '') + 't'
    return ' + ' + (str(v) if v != 1 else '') + 't'

def t_dioph(a, b, c):
    a = _iv(a, 'a', -NT_MAX, NT_MAX)
    b = _iv(b, 'b', -NT_MAX, NT_MAX)
    c = _iv(c, 'c', -NT_MAX, NT_MAX)
    sb = ' + ' + str(b) if b >= 0 else ' - ' + str(-b)
    head = _w(str(a) + 'x' + sb + 'y = ' + str(c))
    if a == 0 and b == 0:
        if c == 0:
            return ['every (x, y) is a solution', head]
        return ['no solutions', head]
    g, u, v = _egcd(a, b)
    if g < 0:
        g, u, v = -g, -u, -v
    if c % g != 0:
        return ['no integer solutions',
                _wn('gcd ' + str(g) + ' does not divide ' + str(c)), head]
    k = c // g
    x0 = u * k
    y0 = v * k
    bg = b // g
    ag = a // g
    out = ['x = ' + str(x0) + _tterm(bg),
           'y = ' + str(y0) + _tterm(-ag),
           'particular x0 = ' + str(x0) + ', y0 = ' + str(y0)]
    if bg != 0:
        t = -x0 // bg
        best = None
        j = -2
        while j <= 2:
            xx = x0 + bg * (t + j)
            yy = y0 - ag * (t + j)
            if xx >= 0 and (best is None or xx < best[0]):
                best = (xx, yy)
            j += 1
        if best is not None:
            out.append('least x >= 0: (' + str(best[0]) + ', ' + str(best[1]) + ')')
    out.append(head)
    out.append(_w('gcd(' + str(a) + ', ' + str(b) + ') = ' + str(g) + '; Bezout ' +
                  str(a) + '(' + str(u) + ') + ' + str(b) + '(' + str(v) + ') = ' + str(g)))
    out.append(_w('scale by ' + str(k) + '; t is any integer'))
    return out

SEARCH_MAX = 40

def t_search(F, N):
    N = _iv(N, 'N', 1, SEARCH_MAX)
    for v in caseng.vars_in(F):
        if v not in ('x', 'y'):
            raise ValueError('F may only use x and y')
    sols = []
    x = -N
    while x <= N:
        y = -N
        while y <= N:
            v = _at(F, float(x), 'x', {'y': float(y)})
            if v is not None and abs(v) < 1e-9:
                sols.append((x, y))
            y += 1
        x += 1
    out = ['solutions found: ' + str(len(sols))]
    line = ''
    for x, y in sols[:40]:
        piece = '(' + str(x) + ', ' + str(y) + ')'
        if len(line) + len(piece) + 1 > 34:
            out.append(line)
            line = piece
        else:
            line = piece if line == '' else line + ' ' + piece
    if line:
        out.append(line)
    if len(sols) > 40:
        out.append(_w('first 40 shown'))
    out.append(_w('integer x, y with |x|, |y| <= ' + str(N) + ' and F = 0'))
    out.append(_wn('a search: solutions outside it are missed'))
    return out

DIGITS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def t_tobase(n, b):
    n = _iv(n, 'n', -10 ** 15, 10 ** 15)
    b = _iv(b, 'b', 2, 36)
    v = abs(n)
    s = ''
    steps = []
    while v > 0:
        steps.append(_w(str(v) + ' = ' + str(b) + ' x ' + str(v // b) + ' + ' + str(v % b)))
        s = DIGITS[v % b] + s
        v //= b
    if s == '':
        s = '0'
    out = [('-' if n < 0 else '') + s + ' (base ' + str(b) + ')']
    out.append(_w('remainders read from the bottom up:'))
    return out + steps[:20]

def t_frombase(d, b):
    b = _iv(b, 'b', 2, 10)
    d = _iv(d, 'digits', 0, 10 ** 15)
    s = str(d)
    v = 0
    for ch in s:
        k = ord(ch) - 48
        if k >= b:
            raise ValueError('digit ' + ch + ' is not allowed in base ' + str(b))
        v = v * b + k
    out = [s + ' (base ' + str(b) + ') = ' + str(v)]
    terms = []
    i = len(s) - 1
    for ch in s:
        if ch != '0':
            terms.append(ch + 'x' + str(b) + '^' + str(i))
        i -= 1
    out.append(_w(' + '.join(terms[:8]) + (' + ...' if len(terms) > 8 else '')))
    out.append(_wn('digits typed 0-9 only (bases 2 to 10)'))
    return out

SECTIONS = [
    ('C', 'Curves: plots and limits', [
        ('Plot y = f(x)', 'f(x),a?,b?', t_plot),
        ('Family y = f(x, a)', 'f(x a),xlo,xhi,a*', t_family),
        ('Family polar r(t, a)', 'r(t a),a*', t_family_polar),
        ('Family parametric', 'x(t a),y(t a),tlo,thi,a*', t_family_param),
        ('Envelope of family', 'f(x a),xlo,xhi,alo,ahi', t_envelope),
        ('Limit x -> a', 'f(x),a', t_limit),
        ('Limit x -> +infinity', 'f(x)', t_lim_pinf),
        ('Limit x -> -infinity', 'f(x)', t_lim_ninf),
        ('Asymptotes', 'f(x)', t_asymptotes),
        ('Graph (ax+b)/(cx+d)', 'a,b,c,d', t_rat1),
        ('Graph quad / linear', 'a,b,c,d,e', t_rat2),
        ('Graph quad / quad', 'a,b,c,d,e,f', t_rat3),
        ('Stationary points', 'f(x)', t_stationary),
        ('Cusps (gradient limit)', 'f(x)', t_cusps),
    ]),
    ('T', 'Curves: tangents, arcs', [
        ('Tangent, normal y=f(x)', 'f(x),a', t_tan_cart),
        ('Tangent at variable p', 'f(x),p*', t_tan_var),
        ('Tangent parametric', 'x(t),y(t),t', t_tan_param),
        ('Tangent polar', 'r(t),theta', t_tan_polar),
        ('Tangent implicit', 'F(x y),x0,y0', t_tan_implicit),
        ('Chord of y = f(x)', 'f(x),a,b', t_chord),
        ('Cartesian to polar', 'F(x y)', t_cart_to_polar),
        ('Polar to cartesian', 'r(t)', t_polar_to_cart),
        ('Arc length y=f(x)', 'f(x),a,b', t_arc_cart),
        ('Arc length parametric', 'x(t),y(t),a,b', t_arc_param),
        ('Arc length polar', 'r(t),a,b', t_arc_polar),
    ]),
    ('D', 'Differential equations', [
        ('Tangent field', 'f(x y),xlo,xhi,ylo,yhi,x0?,y0?', t_field),
        ('Verify a DE solution', 'y(x),F(x y p q)', t_verify),
        ('Particular solution', 'y(x c),x0,y0', t_particular),
        ('Solution family', 'y(x c),xlo,xhi,c*', t_sol_family),
        ('Euler step by step', 'f(x y),x0,y0,h,n', t_euler),
        ('Euler: halving h', 'f(x y),x0,y0,X,n', t_euler_halve),
        ('RK2 (modified Euler)', 'f(x y),x0,y0,h,n', t_rk2_heun),
        ('RK2 (midpoint)', 'f(x y),x0,y0,h,n', t_rk2_mid),
        ('RK4', 'f(x y),x0,y0,h,n', t_rk4),
        ('Euler, RK2, RK4', 'f(x y),x0,y0,h,n', t_compare),
    ]),
    ('N', 'Number theory', [
        ('gcd and lcm', 'a,b', t_gcd),
        ('Euclid and Bezout', 'a,b', t_euclid),
        ('Prime test', 'n', t_prime),
        ('Prime factorise', 'n', t_factor),
        ('Euler totient phi(n)', 'n', t_totient),
        ('a^b mod m', 'a,b,m', t_powmod),
        ('Modular inverse', 'a,m', t_modinv),
        ('Solve ax = b (mod m)', 'a,b,m', t_lincong),
        ('Chinese remainder', 'a1,m1,a2,m2', t_crt),
        ("Fermat's little thm", 'a,p', t_fermat),
        ("Wilson's theorem", 'p', t_wilson),
        ('Pythagorean triples', 'c max', t_pythag),
        ('Triple from m, n', 'm,n', t_triple),
        ("Pell x^2-ny^2=1", 'n', t_pell),
        ('Linear ax+by=c', 'a,b,c', t_dioph),
        ('Integer solutions', 'F(x y),N', t_search),
        ('Decimal to base b', 'n,b', t_tobase),
        ('Base b to decimal', 'digits,b', t_frombase),
    ]),
]
