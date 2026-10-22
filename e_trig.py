# Trig actions on expressions and identities: R form, small angles, compound
# angles, simplify, exact values, the other ratios from one, identity checks;
# and the helpers the trig equations (e_tsolve.py) and the triangle and
# sector boxes (e_tri.py) share. Trees are worked in radians: degrees are
# turned into radians on the way in and back on the way out.
import math
import caseng
import caspoly
import casui
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has, Stuck

PI = ('v', 'pi')
TRIG = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot')
RECIP = {'sec': 'cos', 'cosec': 'sin', 'cot': 'tan'}
INV = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan'}

def _ex(t):
    # exact tidy: compound angles out, like terms in
    import casalg
    try:
        r = casalg.expand(S(t), True, False)
        return r if r is not None else S(t)
    except Exception:
        return S(t)

def _rad(t):
    # degrees -> the same tree in radians: trig arguments times pi/180,
    # inverse trig results times 180/pi
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if k in TRIG:
        return (k, ('*', _rad(t[1]), ('/', PI, N(180))))
    if k in ('asin', 'acos', 'atan'):
        return ('*', (k, _rad(t[1])), ('/', N(180), PI))
    return (k,) + tuple([_rad(c) for c in t[1:]])

def _f(E, v, x):
    # E at v = x (float), None when undefined
    try:
        y = caseng.evalf(E, x, False, {v: x})
    except Exception:
        return None
    if isinstance(y, complex):
        if abs(y.imag) > 1e-9:
            return None
        y = y.real
    if y != y or abs(y) > 1e12:
        return None
    return y

def _fl(x):
    # a float as a tree (a minus outside: S misreads ('n', -1.3))
    return N(x) if x >= 0 else ('neg', N(-x))

def _ok(*ts):
    for t in ts:
        if not _nice(t):
            return False
    return True

def _calc(op, a, b):
    # exact when both are, else a float (S would turn a float into a fraction)
    if _ok(a, b):
        return S((op, a, b))
    x, y = val(a), val(b)
    return _fl(x + y if op == '+' else (x - y if op == '-' else (x * y if op == '*' else x / y)))

def _defined(E, v, x):
    # no denominator, tan, sec, cosec or cot at a zero there
    k = E[0]
    if k == 'n' or k == 'v':
        return True
    chk = None
    if k == '/':
        chk = E[2]
    elif k in ('tan', 'sec'):
        chk = ('cos', E[1])
    elif k in ('cosec', 'cot'):
        chk = ('sin', E[1])
    if chk is not None:
        y = _f(chk, v, x)
        if y is not None and abs(y) < 1e-9:
            return False
    for c in E[1:]:
        if not _defined(c, v, x):
            return False
    return True

def _nice(t):
    # an exact angle worth showing: no inverse trig, no decimals
    s = txt(t)
    return 'asin' not in s and 'acos' not in s and 'atan' not in s and not eng._floaty(t)

def _unit(deg):
    return (N(180), N(360)) if deg else (PI, ('*', N(2), PI))

def _sides(F):
    if F.pair:
        return F.rows[0].f, F.rows[1].f
    r = F.rows[0]
    if r.rel == '=' and r.name is None:
        return r.lhs, r.rhs
    return r.f, ZERO

def _arg(A):
    s = txt(A)
    return s if A[0] == 'v' else '(' + s + ')'

def _alpha(y, x, R):
    # the angle with cos = x/R, sin = y/R, in (-pi, pi]: exact when it is
    xv = val(x)
    yv = val(y)
    a = S(('atan', ('/', y, x))) if xv else S(('/', PI, N(2 if yv > 0 else -2)))
    if xv is not None and xv < 0:
        a = S(('+', a, PI)) if yv >= 0 else S(('-', a, PI))
    if not _nice(a):
        return N(math.atan2(yv, xv))
    return a

def _angtxt(a, deg):
    # an angle in radians (tree) as text in the unit asked
    if deg:
        d = S(('/', ('*', a, N(180)), PI))
        if _nice(d) and 'pi' not in txt(d):
            return txt(d)
        return eng.dec(val(a) * 180 / math.pi)
    if _nice(a):
        v = val(a)
        return txt(a) + ('' if a[0] == 'n' or v is None else ' = ' + eng.dec(v))
    return eng.dec(val(a))

def _tv(t):
    s = txt(t)
    if eng._floaty(t) or not _nice(t) or 'sin(' in s or 'cos(' in s or 'tan(' in s:
        return eng.dec(val(t))
    return s


# ---- identities -------------------------------------------------------------------------------

def _identity(F, arg, vals):
    v = F.var
    L, R = _sides(F)
    deg = casui.SET['angle'] == 'deg'
    lines = [txt(L) + ' = ' + txt(R) + ' ?']
    D = ('-', L, R)
    Dr = _rad(D) if deg else D
    xs = (0.3, 0.7, 1.1, 1.3, 1.9, 2.6, 4.0, 5.3, -0.9)
    tried = 0
    for x in xs:
        if deg:
            x = x * 180 / math.pi
        a = _f(_rad(L) if deg else L, v, x)
        b = _f(_rad(R) if deg else R, v, x)
        if a is None or b is None:
            continue
        tried += 1
        if abs(a - b) > 1e-7 * (1 + abs(a) + abs(b)):
            lines.append('at ' + v + ' = ' + eng.dec(x) + ': left side ' + eng.dec(a) + ', right side ' + eng.dec(b))
            lines.append(eng.boxs('', 'not an identity'))
            lines.append(('w', 'if the question limits ' + v + ' (0 < ' + v + ' < pi/2), it may hold there: '
                          'check that value is outside it'))
            return lines
    if tried < 3:
        raise ValueError('both sides are undefined at the test points')
    try:
        z = _ex(Dr)
        if z == ZERO:
            lines.append('left side - right side simplifies to 0')
    except Exception:
        pass
    lines.append('both sides agree at ' + str(tried) + ' values of ' + v)
    lines.append(eng.boxs('', 'it is an identity (where both sides are defined)'))
    lines.append(('w', 'the proof is still yours to write: this only checks it'))
    return lines

# ---- expressions -------------------------------------------------------------------------------

def _rform(F, arg, vals):
    v = F.var
    import acts_trig
    a, b, k, A = acts_trig.rparts(F.rows[0].f, v)
    a = S(a)
    b = S(b)
    k = S(k)
    i = vals[0]
    deg = casui.SET['angle'] == 'deg'
    fn = 'sin' if i < 2 else 'cos'
    sg = '+' if i % 2 == 0 else '-'
    an = _arg(A)
    form = 'R ' + fn + '(' + txt(A) + ' ' + sg + ' a)'
    lines = [txt(eng.add(eng.mul(a, ('sin', A)), eng.mul(b, ('cos', A)))) + ' = ' + form]
    if fn == 'sin':
        lines.append('= R sin ' + an + ' cos a ' + sg + ' R cos ' + an + ' sin a')
        rc, rs = a, (b if sg == '+' else S(('neg', b)))
    else:
        lines.append('= R cos ' + an + ' cos a ' + ('-' if sg == '+' else '+') + ' R sin ' + an + ' sin a')
        rc, rs = b, (S(('neg', a)) if sg == '+' else a)
    lines.append('R cos a = ' + txt(rc) + ',  R sin a = ' + txt(rs))
    R = S(('sqrt', S(('+', ('^', rc, N(2)), ('^', rs, N(2))))))
    lines.append('R = sqrt(' + txt(rc) + '^2 + ' + eng._br(txt(rs)) + '^2) = ' + txt(R))
    al = _alpha(rs, rc, R)
    lines.append('tan a = ' + txt(S(('/', rs, rc))))
    at = _angtxt(al, deg)
    ot = _angtxt(al, not deg)
    lines.append(eng.box('R = ', R, not F.dec))
    lines.append(eng.boxs('a = ', at))
    lines.append(('w', 'a = ' + ot + (' rad' if deg else ' deg')))
    an = at.split(' ')[0]
    if an[:1] == '-':
        an = an[1:]
        sg = '-' if sg == '+' else '+'
    w = txt(R) + ' ' + fn + '(' + txt(A) + ' ' + sg + ' ' + an + ')'
    if k != ZERO:
        w += ' + ' + txt(k)
    lines.append(w)
    mx = S(('+', R, k))
    mn = S(('-', k, R))
    lines.append('max ' + txt(mx) + ', min ' + txt(mn))
    return lines

def _approx(t, out):
    # small angles: sin A ~ A, tan A ~ A, cos A ~ 1 - A^2/2
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if k in ('sin', 'tan', 'cos'):
        A = t[1]
        rep = A if k != 'cos' else ('-', ONE, ('/', ('^', A, N(2)), N(2)))
        s = k + ' ' + _arg(A) + ' ~ ' + txt(rep)
        if s not in out:
            out.append(s)
        return rep
    return (k,) + tuple([_approx(c, out) for c in t[1:]])

def _small(F, arg, vals):
    import casalg
    v = F.var
    f = F.rows[0].f
    lines = [txt(f)]
    subs = []
    g = _approx(f, subs)
    lines += subs
    lines.append('~ ' + txt(g))
    G = S(f)
    n = 2
    while True:
        co = casalg.taylor(G, v, n)
        if co is None:
            raise ValueError('no small-angle form at ' + v + ' = 0')
        if [c for c in co if c[0]] or n >= 4:
            break
        n += 1
    t = eng.build([(eng.mul(eng.R(*co[i]), ('^', ('v', v), N(i)) if i > 1 else (('v', v) if i else ONE)), 1)
                   for i in range(n + 1) if co[i][0]])
    lines.append(('w', 'terms beyond ' + v + '^' + str(n) + ' dropped'))
    lines.append(eng.boxt('~ ', t))
    return lines

def _simplify(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    deg = casui.SET['angle'] == 'deg'
    lines = [txt(f)]
    fr = _rad(f) if deg else f
    ys = [_f(fr, v, x) for x in (0.3, 0.7, 1.1, 2.6)]
    ys = [y for y in ys if y is not None]
    if len(ys) >= 3 and max(ys) - min(ys) < 1e-9 * (1 + abs(ys[0])):
        c = eng._snap(ys[0]) if hasattr(eng, '_snap') else N(ys[0])
        r = round(ys[0])
        c = N(int(r)) if abs(r - ys[0]) < 1e-9 else c
        lines.append(('w', 'the same value at every ' + v + ' tried: a constant'))
        lines.append(eng.box('= ', c))
        return lines
    g = _ex(f)
    h = S(f)
    best = g if len(txt(g)) <= len(txt(h)) else h
    lines.append(eng.boxt('= ', best))
    return lines

def _expand(F, arg, vals):
    f = F.rows[0].f
    lines = [txt(f)]
    g = _ex(f)
    lines.append(eng.boxt('= ', g))
    return lines

# ---- numbers -----------------------------------------------------------------------------------

def _inv(t):
    # cos(asin k) = sqrt(1 - k^2) and the like
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    t = (k,) + tuple([_inv(c) for c in t[1:]])
    if k in RECIP and t[1][0] in ('asin', 'acos', 'atan'):
        return ('/', ONE, _inv((RECIP[k], t[1])))
    if k in ('sin', 'cos', 'tan') and t[1][0] in ('asin', 'acos', 'atan'):
        g, u = t[1][0], t[1][1]
        if g[1:] == k:
            return u
        if g == 'atan':
            r = ('sqrt', ('+', ONE, ('^', u, N(2))))
            return ('/', u, r) if k == 'sin' else ('/', ONE, r)
        o = ('sqrt', ('-', ONE, ('^', u, N(2))))
        if k == 'tan':
            return ('/', u, o) if g == 'asin' else ('/', o, u)
        return o
    return t

def _shift(t):
    # sin(m pi + b) = (-1)^m sin b and the like, so an inverse trig can be undone
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    t = (k,) + tuple([_shift(c) for c in t[1:]])
    if k in RECIP:
        return ('/', ONE, _shift((RECIP[k], t[1])))
    if k not in ('sin', 'cos', 'tan'):
        return t
    inv = []
    rest = []
    for u, sg in eng.sumterms(caspoly.expand(S(t[1])), 1, []):
        if u[0] in ('asin', 'acos', 'atan'):
            inv.append((u, sg))
        else:
            rest.append((u, sg))
    if len(inv) != 1 or not rest:
        return t
    m = val(eng.build(rest))
    if m is None or abs(m / math.pi - round(m / math.pi)) > 1e-12:
        return t
    m = int(round(m / math.pi))
    b, sg = inv[0]
    out = (k, b)
    flip = (k != 'tan' and m % 2) != (k != 'cos' and sg < 0)
    return ('neg', out) if flip else out

def _evaluate(F, arg, vals):
    f = F.rows[0].f
    deg = casui.SET['angle'] == 'deg'
    lines = [txt(f) + (' (degrees)' if deg else '')]
    g = _rad(f) if deg else f
    g = _inv(_shift(S(g)))
    g = _inv(_shift(S(g)))
    r = _ex(g)
    if not eng._floaty(r):
        r = eng.nice(r)
    lines.append(eng.box('= ', r, not F.dec))
    return lines

def _ratios(F, arg, vals):
    r = F.rows[0]
    v = F.var
    q = vals[0]
    for L, Rt in ((r.lhs, r.rhs), (r.rhs, r.lhs)):
        if L[0] in TRIG and L[1] == ('v', v):
            break
    fn = L[0]
    k = S(Rt)
    lines = [fn + ' ' + v + ' = ' + txt(k)]
    kv = val(k)
    if kv is None or isinstance(kv, complex):
        raise ValueError(txt(k) + ' is not a number')
    if fn in ('sin', 'cos') and abs(kv) > 1 or fn in ('sec', 'cosec') and abs(kv) < 1:
        raise ValueError('no angle has ' + fn + ' ' + v + ' = ' + txt(k))
    if fn in RECIP:
        k = S(('/', ONE, k))
        fn = RECIP[fn]
        lines.append(fn + ' ' + v + ' = ' + txt(k))
    # signs in the quadrant: sin, cos, tan
    sg = ((1, 1, 1), (1, -1, -1), (-1, -1, 1), (-1, 1, -1))[q]
    if fn == 'tan':
        sec2 = S(('+', ONE, ('^', k, N(2))))
        lines.append('sec^2 ' + v + ' = 1 + tan^2 ' + v + ' = ' + txt(sec2))
        c = S(('*', N(sg[1]), ('/', ONE, ('sqrt', sec2))))
        s = S(('*', k, c))
    elif fn == 'sin':
        s = k
        c2 = S(('-', ONE, ('^', k, N(2))))
        lines.append('cos^2 ' + v + ' = 1 - sin^2 ' + v + ' = ' + txt(c2))
        c = S(('*', N(sg[1]), ('sqrt', c2)))
    else:
        c = k
        s2 = S(('-', ONE, ('^', k, N(2))))
        lines.append('sin^2 ' + v + ' = 1 - cos^2 ' + v + ' = ' + txt(s2))
        s = S(('*', N(sg[0]), ('sqrt', s2)))
    if (val(s) or 0) * sg[0] < -1e-12 or (val(c) or 0) * sg[1] < -1e-12:
        raise ValueError(fn + ' ' + v + ' = ' + txt(k) + ' has the wrong sign for that quadrant')
    lines.append(('w', ('sin', 'cos', 'tan')[0] + ' ' + ('> 0' if sg[0] > 0 else '< 0') + ', cos ' +
                  ('> 0' if sg[1] > 0 else '< 0') + ' there'))
    t = S(('/', s, c)) if val(c) else None
    out = [('sin', s), ('cos', c), ('tan', t)]
    for nm, x in out:
        if x is None:
            lines.append(eng.boxs(nm + ' ' + v + ' = ', 'undefined'))
        else:
            lines.append(eng.box(nm + ' ' + v + ' = ', eng.nice(_ex(x)), not F.dec))
    for nm, x in out:
        if x is not None and val(x):
            lines.append(('w', {'sin': 'cosec', 'cos': 'sec', 'tan': 'cot'}[nm] + ' ' + v + ' = ' +
                          txt(eng.nice(_ex(('/', ONE, x))))))
    return lines

# ---- triangles (boxes a b c A B C area) ----------------------------------------------------------

# ---- entry points: the trees here are in radians whatever the Angle setting --------------------

def _r(fn):
    def run(F, arg, vals):
        old = casui.DEG
        casui.DEG = False
        try:
            return fn(F, arg, vals)
        finally:
            casui.DEG = old
    return run

identity = _r(_identity)
rform = _r(_rform)
small = _r(_small)
simplify = _r(_simplify)
expand = _r(_expand)
evaluate = _r(_evaluate)
ratios = _r(_ratios)
