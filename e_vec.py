# Vectors: magnitude and direction, unit vector; for two vectors a and b
# (or the position vectors of A and B) AB = b - a and its length, a + b and
# a - b, parallel or not (b = k a), the angle between (the cosine rule, as
# the course has no scalar product), the midpoint, a + t b; from boxes, a
# quadrilateral's sides (parallel pairs, equal lengths, its name) and the
# components from a size and a direction. Exact where the numbers allow.
import math
import casui
import eng
import recog
from eng import S, N, ZERO, ONE, txt, val

I, J, K = ('v', 'i'), ('v', 'j'), ('v', 'k')

def vt(v):
    # 3i - 4j (+ 2k) as text
    out = []
    for c, u in zip(v, (I, J, K)):
        if S(c) != ZERO:
            out.append((eng.mul(S(c), u), 1))
    return txt(eng.build(out), False) if out else '0'

def col(v, dim):
    return '(' + ', '.join([txt(S(c)) for c in v[:dim]]) + ')'

def _dim(F):
    return F.dim

def _sub(a, b):
    return [S(('-', x, y)) for x, y in zip(a, b)]

def _add(a, b):
    return [S(('+', x, y)) for x, y in zip(a, b)]

def _len2(v):
    return S(eng.build([(('^', c, N(2)), 1) for c in v]))

def _mag(v):
    return eng.nice(S(('sqrt', _len2(v))))

def _exact(F):
    return not [1 for v in F.vecs for c in v if recog.hasfloat(c)]

def _sq(v, dim):
    return ' + '.join([eng._br(txt(S(c))) + '^2' for c in v[:dim]])

def magnitude(F, arg, vals):
    v = F.vecs[0]
    d = _dim(F)
    m = _mag(v)
    lines = [vt(v) + ' = ' + col(v, d), '|v| = sqrt(' + _sq(v, d) + ')']
    lines.append(eng.box('|v| = ', m, _exact(F)))
    if d == 2:
        x, y = val(v[0]), val(v[1])
        if x is not None and y is not None and not isinstance(x, complex) and (x or y):
            deg = casui.SET['angle'] == 'deg'
            a = math.atan2(y, x)
            lines.append('angle with i: tan a = ' + txt(S(('/', v[1], v[0]))) if x else 'along j')
            s = eng.dec((a) * 180 / math.pi) + ' deg' if deg else eng.dec(a) + ' rad'
            lines.append(eng.boxs('angle with i = ', s))
            lines.append(('w', 'measured anticlockwise from i; ' +
                          (eng.dec(a) + ' rad' if deg else eng.dec((a) * 180 / math.pi) + ' deg')))
    return lines

def unit(F, arg, vals):
    v = F.vecs[0]
    m = _mag(v)
    if val(m) == 0:
        raise ValueError('the zero vector has no direction')
    lines = ['|v| = ' + txt(m)]
    u = [eng.nice(S(('/', c, m))) for c in v]
    lines.append(eng.boxs('unit vector = ', vt(u), None))
    return lines

def ab(F, arg, vals):
    a, b = F.vecs
    d = _dim(F)
    v = _sub(b, a)
    lines = ['AB = b - a = ' + col(b, d) + ' - ' + col(a, d)]
    lines.append(eng.boxs('AB = ', vt(v) + ' = ' + col(v, d)))
    lines.append('|AB| = sqrt(' + _sq(v, d) + ')')
    lines.append(eng.box('|AB| = ', _mag(v), _exact(F)))
    return lines

def sumdiff(F, arg, vals):
    a, b = F.vecs
    d = _dim(F)
    s = _add(a, b)
    t = _sub(a, b)
    lines = [eng.boxs('a + b = ', vt(s) + ' = ' + col(s, d)),
             eng.boxs('a - b = ', vt(t) + ' = ' + col(t, d)),
             eng.boxs('b - a = ', vt(_sub(b, a)))]
    lines.append(('w', 'resultant (the sum) has size ' + txt(_mag(s))))
    return lines

def parallel(F, arg, vals):
    a, b = F.vecs
    d = _dim(F)
    lines = []
    k = None
    for x, y in zip(a, b):
        if S(x) != ZERO:
            k = S(('/', y, x))
            break
    ok = k is not None and not [1 for x, y in zip(a, b) if S(('-', y, ('*', k, x))) != ZERO]
    if k is not None:
        lines.append('b = k a needs k = ' + ' = '.join([txt(S(('/', y, x))) for x, y in zip(a[:d], b[:d])
                                                       if S(x) != ZERO]))
    if ok:
        lines.append(eng.boxs('', 'parallel: b = ' + txt(k) + ' a'))
    else:
        lines.append(eng.boxs('', 'not parallel'))
    return lines

def angle(F, arg, vals):
    # the angle between a and b, by the cosine rule on |a|, |b|, |a - b|
    a, b = F.vecs
    p = _len2(a)
    q = _len2(b)
    r = _len2(_sub(a, b))
    if val(p) == 0 or val(q) == 0:
        raise ValueError('a zero vector has no angle')
    lines = ['|a|^2 = ' + txt(p) + ', |b|^2 = ' + txt(q) + ', |a - b|^2 = ' + txt(r),
             'cos t = (|a|^2 + |b|^2 - |a - b|^2)/(2|a||b|)']
    c = eng.nice(S(('/', ('-', ('+', p, q), r), ('*', N(2), ('sqrt', ('*', p, q))))))
    lines.append('cos t = ' + txt(c))
    deg = casui.SET['angle'] == 'deg'
    t = S(('acos', c))
    cv = val(c)
    if cv is None or isinstance(cv, complex):
        raise ValueError('cannot work out the angle')
    cv = max(-1.0, min(1.0, cv))
    if deg:
        d = S(('/', ('*', t, N(180)), ('v', 'pi')))
        nice = 'acos' not in txt(d) and 'pi' not in txt(d) and not eng._floaty(d)
        lines.append(eng.box('angle = ', d if nice else N((math.acos(cv)) * 180 / math.pi), nice))
        lines.append(('w', 'degrees; ' + eng.dec(math.acos(cv)) + ' rad'))
    else:
        nice = 'acos' not in txt(t) and not eng._floaty(t)
        lines.append(eng.box('angle = ', t if nice else N(math.acos(cv)), nice))
        lines.append(('w', 'radians; ' + eng.dec((math.acos(cv)) * 180 / math.pi) + ' deg'))
    return lines

def midpoint(F, arg, vals):
    a, b = F.vecs
    d = _dim(F)
    m = [S(('/', ('+', x, y), N(2))) for x, y in zip(a, b)]
    return ['(a + b)/2', eng.boxs('midpoint ', col(m, d) + ',  ' + vt(m))]

def along(F, arg, vals):
    a, b = F.vecs
    d = _dim(F)
    t = vals[0]
    r = [S(('+', x, ('*', t, y))) for x, y in zip(a, b)]
    lines = ['a + ' + eng._br(txt(t)) + ' b = ' + col(a, d) + ' + ' + eng._br(txt(t)) + col(b, d)]
    lines.append(eng.boxs('', vt(r) + ' = ' + col(r, d)))
    v = [val(x) for x in r[:d]]
    if None not in v and recog.hasfloat(t) or not _exact(F):
        lines.append(('w', '= (' + ', '.join([eng.dec(x) for x in v]) + ')'))
    return lines

def polar(F, arg, vals):
    r, a = vals
    if r is None or a is None or r == '?' or a == '?':
        raise ValueError('fill in the size and the angle')
    deg = casui.SET['angle'] == 'deg'
    ar = S(('/', ('*', a, ('v', 'pi')), N(180))) if deg else a
    x = eng.nice(S(('*', r, ('cos', ar))))
    y = eng.nice(S(('*', r, ('sin', ar))))
    lines = [('w', 'angle anticlockwise from i, in ' + ('degrees' if deg else 'radians')),
             'x = ' + txt(r) + ' cos ' + txt(a) + ',  y = ' + txt(r) + ' sin ' + txt(a)]
    ex = not recog.hasfloat(r) and not recog.hasfloat(a) and 'cos' not in txt(x) and 'sin' not in txt(y)
    if ex or val(x) is None or val(y) is None:
        lines.append(eng.boxs('', vt([x, y, ZERO]) + ' = ' + col([x, y], 2)))
    else:
        lines.append(eng.boxs('', '(' + eng.dec(val(x)) + ', ' + eng.dec(val(y)) + ')'))
    return lines

def quad(F, arg, vals):
    import rvec
    P = []
    for i in range(4):
        if not vals[i]:
            raise ValueError('fill in A, B, C and D')
        v, d = rvec.parse_vec(vals[i])
        P.append(v)
    names = 'ABCD'
    sides = []
    lines = []
    for i in range(4):
        j = (i + 1) % 4
        s = _sub(P[j], P[i])
        sides.append(s)
        lines.append(names[i] + names[j] + ' = ' + vt(s) + ',  |' + names[i] + names[j] + '| = ' + txt(_mag(s)))
    def par(u, w):
        for x, y in zip(u, w):
            if S(x) != ZERO:
                k = S(('/', y, x))
                return k if not [1 for p, q in zip(u, w) if S(('-', q, ('*', k, p))) != ZERO] else None
        return None
    k1 = par(sides[0], sides[2])
    k2 = par(sides[1], sides[3])
    if k1 is not None:
        lines.append('CD = ' + txt(k1) + ' AB: AB parallel to DC')
    if k2 is not None:
        lines.append('DA = ' + txt(k2) + ' BC: BC parallel to AD')
    eq = [val(_len2(s)) for s in sides]
    same = max(eq) - min(eq) < 1e-9 * (1 + max(eq))
    d1 = val(_len2(_sub(P[2], P[0])))
    d2 = val(_len2(_sub(P[3], P[1])))
    if k1 is not None and k2 is not None:
        right = abs(eq[0] + eq[1] - d1) < 1e-9 * (1 + d1)
        name = ('square' if right else 'rhombus') if same else ('rectangle' if right else 'parallelogram')
    elif k1 is not None or k2 is not None:
        name = 'trapezium'
        if abs(d1 - d2) < 1e-9 * (1 + d1):
            name = 'isosceles trapezium'
    elif abs(eq[0] - eq[1]) < 1e-9 * (1 + eq[0]) and abs(eq[2] - eq[3]) < 1e-9 * (1 + eq[2]) or \
            abs(eq[1] - eq[2]) < 1e-9 * (1 + eq[1]) and abs(eq[3] - eq[0]) < 1e-9 * (1 + eq[3]):
        name = 'kite'
    else:
        name = 'quadrilateral (no parallel sides)'
    lines.append(eng.boxs('ABCD is a ', name))
    return lines
