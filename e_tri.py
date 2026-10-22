# Triangles (boxes a, b, c, A, B, C and area: the cosine rule, the sine rule
# with its ambiguous case, (1/2)ab sin C) and arcs and sectors (boxes r,
# angle, arc, area, perimeter, segment), exact where the values allow.
import math
import casui
import eng
import recog
from eng import S, N, ZERO, ONE, txt
from e_trig import PI, _ex, _nice, _calc, _tv, _r, val

def _ang(t, deg):
    # an angle as typed -> radians tree
    return S(('/', ('*', t, PI), N(180))) if deg else t

def _out(t, deg):
    # radians tree -> the unit of the question
    if deg:
        d = S(('/', ('*', t, N(180)), PI))
        return d if _nice(d) and 'pi' not in txt(d) else N(val(d))
    return t if _nice(t) else N(val(t))

def _acos(x):
    a = S(('acos', x))
    return a if _nice(a) else N(math.acos(max(-1.0, min(1.0, val(x)))))

def _typeddec(F, vals):
    return F.dec or [1 for x in vals if x not in (None, '?') and recog.hasfloat(x)] != []

def _triangle(F, arg, vals):
    deg = casui.SET['angle'] == 'deg'
    dec = _typeddec(F, vals)
    nm = ['a', 'b', 'c', 'A', 'B', 'C']
    want = [i for i in range(7) if vals[i] == '?']
    kn = {}
    for i in range(6):
        if vals[i] is not None and vals[i] != '?':
            x = val(vals[i])
            if x is None or x <= 0:
                raise ValueError(nm[i] + ' must be a positive number')
            kn[i] = vals[i] if i < 3 else _ang(vals[i], deg)
    area = vals[6] if vals[6] not in (None, '?') else None
    lines = [('w', 'angle A is opposite side a, and so on; angles in ' + ('degrees' if deg else 'radians'))]
    sides = [i for i in range(3) if i in kn]
    angs = [i - 3 for i in range(3, 6) if i in kn]
    if len(sides) + len(angs) + (1 if area is not None else 0) < 3 or not sides:
        raise ValueError('fill in three of them, with at least one side')
    s = [kn.get(i) for i in range(3)]
    A = [kn.get(i + 3) for i in range(3)]
    if len(angs) == 2:
        j = [i for i in range(3) if A[i] is None][0]
        A[j] = S(('-', ('-', PI, A[angs[0]]), A[angs[1]]))
        if (val(A[j]) or 0) <= 0:
            raise ValueError('the two angles add up to 180 deg or more')
        lines.append(nm[j + 3] + ' = 180 - ' + _tv(_out(A[angs[0]], True)) + ' - ' + _tv(_out(A[angs[1]], True)) +
                     ' = ' + _tv(_out(A[j], True)) + ' deg')
        angs = [0, 1, 2]
    sols = [(s, A)]
    if len(sides) == 3:
        sols = [_sss(s, A, lines, deg)]
    elif len(sides) == 2 and area is not None and len(angs) == 0:
        sols = _area2(s, A, area, lines, deg)
    elif len(sides) == 2:
        i, j = sides
        k = 3 - i - j
        if A[k] is not None:
            sols = [_sas(s, A, k, lines, deg)]
        else:
            sols = _ssa(s, A, lines, deg)
    else:
        sols = [_aas(s, A, lines, deg)]
    for s2, A2 in sols:
        if len(sols) > 1:
            lines.append(('w', 'triangle ' + str(sols.index((s2, A2)) + 1) + ':'))
        ar = S(('/', ('*', ('*', s2[0], s2[1]), ('sin', A2[2])), N(2)))
        if area is None:
            lines.append('area = (1/2) ab sin C = ' + _tv(ar))
        for i in range(7):
            if want and i not in want:
                continue
            if not want and (i in kn or i == 6 and area is not None):
                continue
            if i < 3:
                lines.append(eng.box(nm[i] + ' = ', s2[i], not dec))
            elif i < 6:
                o = _out(A2[i - 3], deg)
                lines.append(eng.box(nm[i] + ' = ', o, not dec and not eng._floaty(o)))
            else:
                lines.append(eng.box('area = ', ar, not dec))
        if not deg:
            lines.append(('w', 'in degrees: ' + ', '.join([nm[i + 3] + ' = ' + _tv(_out(A2[i], True))
                                                          for i in range(3)])))
    return lines

def _sss(s, A, lines, deg):
    a, b, c = s
    if val(a) + val(b) <= val(c) or val(a) + val(c) <= val(b) or val(b) + val(c) <= val(a):
        raise ValueError('those three sides cannot make a triangle')
    nm = 'abc'
    A = list(A)
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        x = S(('/', ('-', ('+', ('^', s[j], N(2)), ('^', s[k], N(2))), ('^', s[i], N(2))),
               ('*', N(2), ('*', s[j], s[k]))))
        A[i] = _acos(x)
        if i < 2:
            lines.append('cos ' + nm[i].upper() + ' = (' + nm[j] + '^2 + ' + nm[k] + '^2 - ' + nm[i] + '^2)/(2' +
                         nm[j] + nm[k] + ') = ' + _tv(x))
    A[2] = _calc('-', _calc('-', PI, A[0]), A[1])
    return (s, A)

def _sas(s, A, k, lines, deg):
    nm = 'abc'
    i, j = (k + 1) % 3, (k + 2) % 3
    sq = S(('-', ('+', ('^', s[i], N(2)), ('^', s[j], N(2))),
            ('*', N(2), ('*', ('*', s[i], s[j]), ('cos', A[k])))))
    lines.append(nm[k] + '^2 = ' + nm[i] + '^2 + ' + nm[j] + '^2 - 2' + nm[i] + nm[j] + ' cos ' + nm[k].upper() +
                 ' = ' + _tv(sq))
    s = list(s)
    s[k] = eng.nice(S(('sqrt', sq)))
    if eng._floaty(s[k]) or not _nice(s[k]):
        s[k] = N(val(s[k]))
    lines.append(nm[k] + ' = ' + _tv(s[k]))
    return _sss(s, A, [], deg)

def _ssa(s, A, lines, deg):
    nm = 'abc'
    k = [i for i in range(3) if A[i] is not None][0]
    if s[k] is None:
        raise ValueError('give the side opposite the angle, or the angle between the two sides')
    j = [i for i in range(3) if s[i] is not None and i != k][0]
    x = S(('/', ('*', s[j], ('sin', A[k])), s[k]))
    xv = val(x)
    lines.append('sin ' + nm[j].upper() + ' = ' + nm[j] + ' sin ' + nm[k].upper() + ' / ' + nm[k] + ' = ' + _tv(x))
    if xv > 1 + 1e-12:
        raise ValueError('sin ' + nm[j].upper() + ' would be ' + eng.dec(xv) + ' > 1: no triangle')
    b1 = S(('asin', x))
    if not _nice(b1):
        b1 = N(math.asin(min(1.0, xv)))
    b2 = S(('-', PI, b1)) if _nice(b1) else N(math.pi - val(b1))
    out = []
    for B in (b1, b2):
        if val(B) + val(A[k]) < math.pi - 1e-9 and not [1 for o in out if abs(val(o[1][j]) - val(B)) < 1e-9]:
            A2 = list(A)
            A2[j] = B
            m = 3 - j - k
            A2[m] = S(('-', ('-', PI, A[k]), B)) if _nice(B) else N(math.pi - val(A[k]) - val(B))
            s2 = list(s)
            s2[m] = S(('/', ('*', s[k], ('sin', A2[m])), ('sin', A[k])))
            if not _nice(s2[m]):
                s2[m] = N(val(s2[m]))
            out.append((s2, A2))
    if len(out) == 2:
        lines.append(nm[j].upper() + ' = ' + _tv(_out(b1, deg)) + ' or ' + _tv(_out(b2, deg)) +
                     ': both make a triangle (ambiguous case)')
    return out

def _aas(s, A, lines, deg):
    nm = 'abc'
    k = [i for i in range(3) if s[i] is not None][0]
    r = S(('/', s[k], ('sin', A[k])))
    lines.append(nm[k] + '/sin ' + nm[k].upper() + ' = ' + _tv(r))
    s = list(s)
    for i in range(3):
        if s[i] is None:
            s[i] = S(('*', r, ('sin', A[i])))
            if not _nice(s[i]):
                s[i] = N(val(s[i]))
            lines.append(nm[i] + ' = ' + nm[k] + ' sin ' + nm[i].upper() + ' / sin ' + nm[k].upper() + ' = ' + _tv(s[i]))
    return (s, A)

def _area2(s, A, area, lines, deg):
    nm = 'abc'
    i, j = [x for x in range(3) if s[x] is not None]
    k = 3 - i - j
    x = S(('/', ('*', N(2), area), ('*', s[i], s[j])))
    lines.append('area = (1/2)' + nm[i] + nm[j] + ' sin ' + nm[k].upper() + ', sin ' + nm[k].upper() + ' = ' + _tv(x))
    if val(x) > 1 + 1e-12:
        raise ValueError('that area is too big for those sides')
    c1 = S(('asin', x))
    if not _nice(c1):
        c1 = N(math.asin(min(1.0, val(x))))
    out = []
    for C in (c1, S(('-', PI, c1)) if _nice(c1) else N(math.pi - val(c1))):
        if [1 for o in out if abs(val(o[1][k]) - val(C)) < 1e-9]:
            continue
        A2 = list(A)
        A2[k] = C
        out.append(_sas(s, A2, k, lines, deg))
    return out

# ---- arcs and sectors (boxes r, angle, arc, area, perimeter, segment) --------------------------

def _sector(F, arg, vals):
    deg = casui.SET['angle'] == 'deg'
    dec = _typeddec(F, vals)
    nm = ['r', 'angle', 'arc', 'area', 'perimeter', 'segment']
    want = [i for i in range(6) if vals[i] == '?']
    k = {}
    for i in range(5):
        if vals[i] is not None and vals[i] != '?':
            if (val(vals[i]) or 0) <= 0:
                raise ValueError(nm[i] + ' must be a positive number')
            k[i] = vals[i]
    if 1 in k:
        k[1] = _ang(k[1], deg)
    lines = [('w', 'arc = r th, area = (1/2) r^2 th, perimeter = 2r + arc, th in radians')]
    if deg and 1 in k:
        lines.append('th = ' + txt(k[1]) + ' rad')
    r = k.get(0)
    th = k.get(1)
    sols = []
    if r is not None and th is not None:
        sols = [(r, th)]
    elif r is not None:
        if 2 in k:
            th = S(('/', k[2], r))
            lines.append('th = arc / r = ' + txt(th))
        elif 3 in k:
            th = S(('/', ('*', N(2), k[3]), ('^', r, N(2))))
            lines.append('th = 2 area / r^2 = ' + txt(th))
        elif 4 in k:
            th = S(('-', ('/', k[4], r), N(2)))
            lines.append('th = perimeter / r - 2 = ' + txt(th))
        sols = [(r, th)]
    elif th is not None:
        if 2 in k:
            r = S(('/', k[2], th))
            lines.append('r = arc / th = ' + txt(r))
        elif 3 in k:
            r = eng.nice(S(('sqrt', ('/', ('*', N(2), k[3]), th))))
            lines.append('r^2 = 2 area / th, r = ' + txt(r))
        elif 4 in k:
            r = S(('/', k[4], ('+', N(2), th)))
            lines.append('r = perimeter / (2 + th) = ' + txt(r))
        sols = [(r, th)]
    elif 2 in k and 3 in k:
        r = S(('/', ('*', N(2), k[3]), k[2]))
        lines.append('area / arc = r/2, r = ' + txt(r))
        sols = [(r, S(('/', k[2], r)))]
    elif 2 in k and 4 in k:
        r = S(('/', ('-', k[4], k[2]), N(2)))
        lines.append('r = (perimeter - arc)/2 = ' + txt(r))
        sols = [(r, S(('/', k[2], r)))]
    elif 3 in k and 4 in k:
        import e_solve
        lines.append('r (2 + th) = P and r^2 th = 2 area:')
        for x in e_solve.quad([S(('*', N(2), k[3])), S(('neg', k[4])), N(2)], 'r', lines, True):
            if (val(x) or 0) > 0:
                sols.append((x, S(('-', ('/', k[4], x), N(2)))))
    if not sols or None in sols[0]:
        raise ValueError('fill in two of r, angle, arc, area and perimeter')
    for r, th in sols:
        if (val(th) or 0) <= 0 or val(th) > 2 * math.pi + 1e-9:
            raise ValueError('the angle comes out as ' + eng.dec(val(th)) + ' rad: not a sector')
        arc = S(('*', r, th))
        area = S(('/', ('*', ('^', r, N(2)), th), N(2)))
        per = S(('+', ('*', N(2), r), arc))
        seg = eng.nice(_ex(('*', ('/', ('^', r, N(2)), N(2)), ('-', th, ('sin', th)))))
        chord = eng.nice(_ex(('*', ('*', N(2), r), ('sin', ('/', th, N(2))))))
        got = [r, _out(th, deg), arc, area, per, seg]
        lines.append('arc = ' + (eng.dec(val(arc)) if dec else _tv(arc)) + ',  area = ' +
                     (eng.dec(val(area)) if dec else _tv(area)))
        lines.append('segment = (1/2) r^2 (th - sin th) = ' + _tv(seg))
        for i in range(6):
            if (want and i in want) or (not want and i not in k):
                lines.append(eng.box(nm[i] + ' = ', got[i], not dec))
        lines.append(('w', 'chord = 2r sin(th/2) = ' + _tv(chord)))
        o = _out(th, not deg)
        lines.append(('w', 'angle = ' + _tv(o) + (' rad' if deg else ' deg')))
    return lines

triangle = _r(_triangle)
sector = _r(_sector)
