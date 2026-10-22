# Trig equations: sin, cos, tan (and sec, cosec, cot) of one angle A = p x + q,
# perhaps with 2A, turned into a polynomial in one ratio (an identity where
# needed: sin^2 + cos^2 = 1, double angles, divide by cos or cos^2, R form),
# solved, then every angle in the interval from the principal value.
# Anything else is solved numerically on the interval, and the page says so.
import math
import caseng
import caspoly
import casui
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, has, Stuck
from e_trig import (PI, TRIG, RECIP, INV, _ex, _rad, _f, _fl, _ok, _calc, _defined, _nice, _unit,
                    _sides, _arg, _alpha, _angtxt, _r, val)

# ---- the trig atoms of an equation -------------------------------------------------------------

def _atoms(t, v, out):
    k = t[0]
    if k == 'n' or k == 'v':
        return out
    if k in TRIG and has(t[1], v):
        if recog.lin(t[1], v) is None:
            raise Stuck()
        if (k, t[1]) not in out:
            out.append((k, t[1]))
        return out
    for c in t[1:]:
        _atoms(c, v, out)
    return out

def _pq(A, v):
    p, q = recog.lin(A, v)
    return S(p), S(q)

def _swap(t, table):
    # trig atoms -> letter trees
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if k in TRIG:
        for a, rep in table:
            if a == (k, t[1]):
                return rep
    return (k,) + tuple([_swap(c, table) for c in t[1:]])

def _back(t, A):
    # letters -> sin A, cos A, tan A for the working
    return caseng.subst(caseng.subst(caseng.subst(t, 'zs', ('sin', A)), 'zc', ('cos', A)), 'zt', ('tan', A))

def _num(t, var=None):
    # numerator of a single fraction
    import casalg
    g = casalg.single_fraction(S(t), var)
    while g[0] == '/':
        g = g[1]
    if g[0] == 'neg':
        g = g[1]
    if var is not None and _dens(g, var, []):
        # surds in the coefficients: times every denominator holding var
        m = ONE
        for d in _dens(g, var, []):
            m = ('*', m, d)
        g = S(caspoly.expand(S(('*', g, m))))
    return caspoly.expand(g)

def _dens(t, v, out):
    k = t[0]
    if k == 'n' or k == 'v':
        return out
    if k == '/' and has(t[2], v) and t[2] not in out:
        out.append(t[2])
    for c in t[1:]:
        _dens(c, v, out)
    return out

def _co(t, v):
    co = eng.coeffs(t, v)
    if co is None:
        raise Stuck()
    while len(co) > 1 and co[-1] == ZERO:
        co.pop()
    return co

# ---- solving ----------------------------------------------------------------------------------

def _reduce(E, v, lines, deg):
    # -> [(fn, A, shift, [values])]: fn(A + shift) = value
    ats = _atoms(E, v, [])
    if not ats:
        raise Stuck()
    args = []
    for fn, A in ats:
        if A not in args:
            args.append(A)
    # the base angle: smallest multiple of the variable; the rest twice it
    args.sort(key=lambda a: abs(val(_pq(a, v)[0]) or 0))
    A = args[0]
    p, q = _pq(A, v)
    dbl = None
    for B in args[1:]:
        p2, q2 = _pq(B, v)
        if S(('-', p2, ('*', N(2), p))) != ZERO or S(('-', q2, ('*', N(2), q))) != ZERO:
            raise Stuck()
        dbl = B
    fns = []
    for fn, B in ats:
        g = RECIP.get(fn, fn)
        if B == A and g not in fns:
            fns.append(g)
    s, c, t = ('v', 'zs'), ('v', 'zc'), ('v', 'zt')
    if dbl is None and len(fns) == 1:
        # one ratio of one angle: a polynomial in it
        g = fns[0]
        u = {'sin': s, 'cos': c, 'tan': t}[g]
        tab = [((fn, A), u if fn == g else ('/', ONE, u)) for fn in (g, _rec(g))]
        G = _num(_swap(E, tab), u[1])
        co = _co(G, u[1])
        return [(g, A, None, _poly(co, g, A, lines))]
    # sin and cos (tan as sin/cos), double angles in terms of A
    tab = [(('sin', A), s), (('cos', A), c), (('tan', A), ('/', s, c)),
           (('sec', A), ('/', ONE, c)), (('cosec', A), ('/', ONE, s)), (('cot', A), ('/', c, s))]
    if dbl is not None:
        rest = [RECIP.get(fn, fn) for fn, B in ats if B == A]
        if 'cos' in rest and 'sin' not in rest:
            c2 = ('-', ('*', N(2), ('^', c, N(2))), ONE)
            lines.append(('w', 'cos 2A = 2cos^2 A - 1'))
        else:
            c2 = ('-', ONE, ('*', N(2), ('^', s, N(2))))
            lines.append(('w', 'cos 2A = 1 - 2sin^2 A'))
        s2 = ('*', N(2), ('*', s, c))
        lines.append(('w', 'sin 2A = 2sin A cos A'))
        tab += [(('sin', dbl), s2), (('cos', dbl), c2), (('tan', dbl), ('/', s2, c2)),
                (('sec', dbl), ('/', ONE, c2)), (('cosec', dbl), ('/', ONE, s2)),
                (('cot', dbl), ('/', c2, s2))]
    G = _num(_swap(E, tab))
    P = {}
    for i, ci in enumerate(_co(G, 'zs')):
        for j, cij in enumerate(_co(ci, 'zc')):
            if cij != ZERO:
                P[(i, j)] = cij
    if dbl is not None:
        lines.append(eq(_back(eng.build([(_mono(P[k], k), 1) for k in _order(P)]), A), ZERO))
    if not [k for k in P if k[0] % 2]:
        # sin only squared: sin^2 = 1 - cos^2
        G = caspoly.expand(eng.build([(_mono(P[k], k, 'cos'), 1) for k in P]))
        lines.append(('w', 'sin^2 A = 1 - cos^2 A'))
        return [('cos', A, None, _poly(_co(G, 'zc'), 'cos', A, lines))]
    if not [k for k in P if k[1] % 2]:
        G = caspoly.expand(eng.build([(_mono(P[k], k, 'sin'), 1) for k in P]))
        lines.append(('w', 'cos^2 A = 1 - sin^2 A'))
        return [('sin', A, None, _poly(_co(G, 'zs'), 'sin', A, lines))]
    degs = [i + j for i, j in P]
    if max(degs) == 1:
        a = P.get((1, 0), ZERO)
        b = P.get((0, 1), ZERO)
        k = S(('neg', P.get((0, 0), ZERO)))
        if k == ZERO:
            # a sin A + b cos A = 0: divide by cos A
            lines.append(('w', 'divide by cos ' + txt(A) + ':'))
            tv = S(('neg', ('/', b, a)))
            lines.append('tan ' + _arg(A) + ' = ' + txt(tv))
            return [('tan', A, None, [tv])]
        return _rform_eq(a, b, k, A, lines, deg)
    if [d for d in degs if d not in (0, 2)] == []:
        # a sin^2 + b sin cos + c cos^2 = k: k (sin^2 + cos^2), then / cos^2
        k = P.get((0, 0), ZERO)
        co = [S(('+', P.get((0, 2), ZERO), k)), P.get((1, 1), ZERO), S(('+', P.get((2, 0), ZERO), k))]
        if k != ZERO:
            lines.append(('w', 'write the number as it times (sin^2 + cos^2)'))
        lines.append(('w', 'divide by cos^2 ' + _arg(A) + ':'))
        out = []
        if co[2] == ZERO:
            lines.append(('w', 'cos ' + _arg(A) + ' = 0 is a solution too'))
            out.append(('cos', A, None, [ZERO]))
            co = co[:2]
        return [('tan', A, None, _poly(co, 'tan', A, lines))] + out
    raise Stuck()

def _rec(g):
    return {'sin': 'cosec', 'cos': 'sec', 'tan': 'cot'}[g]

def _order(P):
    ks = list(P.keys())
    ks.sort(key=lambda k: -(k[0] + k[1]) * 10 - k[0])
    return ks

def _mono(c, k, to=None):
    i, j = k
    s, cc = ('v', 'zs'), ('v', 'zc')
    if to == 'cos':
        # sin^i = (1 - cos^2)^(i/2)
        m = ('^', ('-', ONE, ('^', cc, N(2))), N(i // 2))
        return ('*', c, ('*', m, ('^', cc, N(j))))
    if to == 'sin':
        m = ('^', ('-', ONE, ('^', s, N(2))), N(j // 2))
        return ('*', c, ('*', ('^', s, N(i)), m))
    return S(('*', c, ('*', ('^', s, N(i)), ('^', cc, N(j)))))

def _poly(co, g, A, lines):
    # roots of a polynomial in g(A), with the working
    import e_solve
    U = (g, A)
    d = len(co) - 1
    if d < 1:
        if co[0] == ZERO:
            raise Stuck()
        lines.append(eq(co[0], ZERO) + ': never true')
        return []
    if d == 1:
        r = S(('neg', ('/', co[0], co[1])))
        lines.append(eq(eng.ptree(co, U), ZERO))
        rt = eng.nice(_ex(r)) if eng._floaty(r) is False else r
        lines.append(g + ' ' + _arg(A) + ' = ' + txt(rt))
        return [rt]
    if d == 2:
        return [_ex(r) for r in e_solve.quad(co, U, lines, True)]
    lines.append('let u = ' + g + ' ' + _arg(A))
    rs = e_solve.poly(eng.ptree(co, ('v', 'u')), ZERO, 'u', None, lines)
    return [_ex(r) for r in rs or []]

def _rform_eq(a, b, k, A, lines, deg):
    # a sin A + b cos A = k: R sin(A + al) = k
    if eng.neg(a)[0]:
        a, b, k = S(('neg', a)), S(('neg', b)), S(('neg', k))
    R2 = S(('+', ('^', a, N(2)), ('^', b, N(2))))
    R = S(('sqrt', R2))
    al = _alpha(b, a, R)
    lines.append(('w', 'R form: ' + txt(eng.add(eng.mul(a, ('sin', A)), eng.mul(b, ('cos', A)))) +
                  ' = R sin(' + txt(A) + ' + a)'))
    lines.append('R = sqrt(' + txt(a) + '^2 + ' + eng._br(txt(b)) + '^2) = ' + txt(R))
    lines.append('tan a = ' + txt(S(('/', b, a))) + ', a = ' + _angtxt(al, deg))
    v = S(('/', k, R))
    lines.append(txt(R) + ' sin(' + txt(A) + ' + a) = ' + txt(k))
    return [('sin', A, al, [v])]

def _values(fn, A, shift, u, v, deg, lo, hi, lines):
    # every v in [lo, hi] with fn(A + shift) = u; A = p v + q
    uv = val(u)
    an = fn + ' ' + (_arg(A) if shift is None else '(' + txt(A) + ' + a)')
    if uv is None or isinstance(uv, complex):
        lines.append(an + ' = ' + txt(u) + ': not a real value')
        return []
    if fn != 'tan' and abs(uv) > 1 + 1e-12:
        lines.append(an + ' = ' + txt(u) + ': no solutions, as -1 <= ' + fn + ' <= 1')
        return []
    half, per = _unit(deg)
    # the principal value, in the unit of the question
    pr = S((INV[fn], u))
    if deg:
        pr = S(('/', ('*', pr, N(180)), PI))
    if not _ok(pr, u):
        pr = _fl(val(pr))
    elif val(pr) == 0:
        pr = ZERO
    if fn == 'sin':
        base = [pr, _calc('-', half, pr)]
    elif fn == 'cos':
        base = [pr, _calc('-', ZERO, pr)]
    else:
        base = [pr]
        per = half
    p, q = _pq(A, v)
    sh = ZERO
    if shift is not None:
        sh = S(('/', ('*', shift, N(180)), PI)) if deg and _nice(shift) else shift
        if not _nice(sh):
            sh = _fl(val(shift) * (180 / math.pi if deg else 1))
    # the range of the angle B = A + shift
    b1 = val(p) * val(lo) + val(q) + val(sh)
    b2 = val(p) * val(hi) + val(q) + val(sh)
    if b1 > b2:
        b1, b2 = b2, b1
    pv = val(per)
    Bs = []
    for b in base:
        bv = val(b)
        k = int(math.floor((b1 - bv) / pv)) - 1
        while bv + k * pv <= b2 + 1e-9:
            if bv + k * pv >= b1 - 1e-9:
                B = _calc('+', b, S(('*', N(k), per)))
                if not [1 for c in Bs if abs(val(c) - val(B)) < 1e-9]:
                    Bs.append(B)
            k += 1
    Bs.sort(key=lambda t: val(t))
    out = []
    for B in Bs:
        x = _calc('/', _calc('-', _calc('-', B, sh), q), p)
        out.append(x)
    plain = shift is None and p == ONE and q == ZERO
    ptxt = txt(pr) if _nice(pr) else eng.dec(val(pr))
    if plain:
        lines.append(an + ' = ' + txt(u) + ': principal value ' + ptxt + ', ' + v + ' = ' +
                     (', '.join([_vt(x) for x in out]) or 'none in range'))
    else:
        bn = txt(A) if shift is None else txt(A) + ' + a'
        lines.append(an + ' = ' + txt(u) + ': principal value ' + ptxt)
        lines.append(('w', 'for ' + eng.dec(b1) + ' <= ' + bn + ' <= ' + eng.dec(b2)))
        lines.append(bn + ' = ' + (', '.join([_vt(b) for b in Bs]) or 'none in range'))
        if out:
            lines.append(v + ' = ' + ', '.join([_vt(x) for x in out]))
    return out

def _vt(t):
    return txt(t) if _nice(t) and t[0] != 'n' or t[0] == 'n' and isinstance(t[1], int) else eng.dec(val(t))

def _scan(E, v, lo, hi):
    # roots of E on [lo, hi] by sign changes and touching minima
    n = 720
    h = (hi - lo) / n
    xs = [lo + i * h for i in range(n + 1)]
    ys = [_f(E, v, x) for x in xs]
    out = []
    for i in range(n):
        a, b = ys[i], ys[i + 1]
        if a is None or b is None:
            continue
        if a == 0:
            out.append(xs[i])
            continue
        if a * b < 0:
            x0, x1 = xs[i], xs[i + 1]
            for j in range(60):
                m = (x0 + x1) / 2
                fm = _f(E, v, m)
                if fm is None:
                    break
                if (fm < 0) == (a < 0):
                    x0 = m
                else:
                    x1 = m
            m = (x0 + x1) / 2
            fm = _f(E, v, m)
            if fm is not None and abs(fm) < 1e-6 * (1 + abs(a) + abs(b)):
                out.append(m)
        elif 0 < i and ys[i - 1] is not None and abs(a) < abs(ys[i - 1]) and abs(a) <= abs(b) and \
                abs(a) < 1e-2 * (1 + abs(b)):
            x0, x1 = xs[i - 1], xs[i + 1]
            for j in range(80):
                m1 = x0 + (x1 - x0) / 3
                m2 = x1 - (x1 - x0) / 3
                f1 = _f(E, v, m1)
                f2 = _f(E, v, m2)
                if f1 is None or f2 is None:
                    break
                if abs(f1) < abs(f2):
                    x1 = m2
                else:
                    x0 = m1
            m = (x0 + x1) / 2
            fm = _f(E, v, m)
            if fm is not None and abs(fm) < 1e-9:
                out.append(m)
    if ys[n] is not None and ys[n] == 0:
        out.append(hi)
    res = []
    for x in out:
        if not [1 for r in res if abs(r - x) < 1e-7 * (1 + abs(x))]:
            res.append(x)
    return res

def _snap(x, deg):
    # a numerical root as an exact angle when it is one
    if deg:
        r = round(x * 2) / 2.0
        if abs(r - x) < 1e-7:
            return N(int(r)) if r == int(r) else S(('/', N(int(r * 2)), N(2)))
        return N(x)
    k = x / math.pi
    for d in (1, 2, 3, 4, 6, 8, 12):
        m = round(k * d)
        if abs(m - k * d) < 1e-8:
            return S(('/', ('*', N(int(m)), PI), N(d)))
    return N(x)

def _solve(F, arg, vals):
    deg = arg == 'deg'
    v = F.var
    L, R = _sides(F)
    half, per = _unit(deg)
    lo = vals[0] if vals and vals[0] is not None else ZERO
    hi = vals[1] if vals and vals[1] is not None else per
    lov = val(lo)
    hiv = val(hi)
    if lov is None or hiv is None or lov >= hiv:
        raise ValueError('the interval needs from < to')
    E = ('-', L, R)
    Er = _rad(E) if deg else E
    head = [eq(L, R), ('w', txt(lo) + ' <= ' + v + ' <= ' + txt(hi) + (', degrees' if deg else ', radians'))]
    lines = list(head)
    try:
        xs = []
        for fn, A, shift, us in _reduce(E, v, lines, deg):
            for u in us:
                xs += _values(fn, A, shift, u, v, deg, lo, hi, lines)
        exact = True
    except (Stuck, ValueError, TypeError, ZeroDivisionError):
        lines = list(head)
        lines.append(('w', 'no identity route: roots found numerically on the interval'))
        xs = [_snap(x, deg) for x in _scan(Er, v, lov, hiv)]
        exact = False
    # keep each root once, in the interval, where the equation holds
    good = []
    for x in xs:
        xv = val(x)
        if xv is None or xv < lov - 1e-9 or xv > hiv + 1e-9:
            continue
        if [1 for g in good if abs(val(g) - xv) < 1e-7 * (1 + abs(xv))]:
            continue
        y = _f(Er, v, xv)
        if y is None or abs(y) > 1e-6 * (1 + abs(_f(_rad(L) if deg else L, v, xv) or 0)) or \
                not _defined(Er, v, xv):
            if exact:
                lines.append(('!', v + ' = ' + _vt(x) + ' does not satisfy the equation (undefined there): reject'))
            continue
        good.append(x)
    good.sort(key=lambda t: val(t))
    if not good:
        lines.append(eng.boxs('', 'no solutions in the interval'))
        return lines
    ends = []
    for x in good:
        lines.append(eng.box(v + ' = ', x, not F.dec and _nice(x) and x[0] != 'n' or x == N(0) or
                             x[0] == 'n' and isinstance(x[1], int)))
        if abs(val(x) - lov) < 1e-9 or abs(val(x) - hiv) < 1e-9:
            ends.append(_vt(x))
    if ends:
        lines.append(('w', v + ' = ' + ', '.join(ends) + ' is an end of the interval: leave it out if the '
                      'interval is strict (<)'))
    return lines

solve = _r(_solve)
