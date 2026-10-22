# Forces: box forms whose engine writes the equations of motion or of
# equilibrium and solves them for whatever is ? (one or two unknowns), so
# every value can be the one asked for (mu from a, P from a, a mass from a
# reaction). A block on a slope or a rough surface (a pull at an angle,
# moving up or down), a pulley (a hanging mass and one on a table, a slope
# or hanging too), towing in a line, moments on a beam or rod, and the
# resultant or equilibrium of forces given as F@angle or in i and j.
# Angles in degrees, as mechanics questions give them. g is 9.8 unless the g
# box says otherwise (type g to keep it as a letter).
import caslex
import caseng
import eng
import recog
from eng import S, N, ZERO, ONE, txt, val

PI = ('v', 'pi')

def _sin(d):
    return ('sin', ('/', ('*', d, PI), N(180)))

def _cos(d):
    return ('cos', ('/', ('*', d, PI), N(180)))

def _tree(s, name, unk):
    # one box: '?' is the unknown named after the box, a letter is an unknown
    s = s.strip()
    if s == '?':
        unk.append(name)
        return ('v', name)
    t = caslex.parse(s)
    if t is None:
        raise ValueError(name + ': cannot read that')
    for c in recog.letters(t):
        if c != 'g' and c not in unk:
            unk.append(c)
    return t

def _boxes(vals, names, opt):
    # -> {name: tree}, unknowns; opt: names that may be left empty (0)
    k = {}
    unk = []
    for v, nm in zip(vals, names):
        if v is None or not v.strip():
            k[nm] = None
            continue
        k[nm] = _tree(v, nm, unk)
    return k, unk

def _z(k, nm):
    return k[nm] if k.get(nm) is not None else ZERO

def _put(t, sol, g):
    for c in sol:
        t = caseng.subst(t, c, sol[c])
    if g is not None:
        t = caseng.subst(t, 'g', g)
    return t

def solve1(L, R, v, lines):
    # one equation in one unknown v (other letters are constants)
    import e_solve
    G = recog.Form()
    r = recog.Row('')
    r.rel = '='
    r.lhs = L
    r.rhs = R
    r.f = ('-', L, R)
    G.rows = [r]
    G.var = v
    G.letters = [c for c in recog.letters(r.f) if c != v]
    G.dec = recog.hasfloat(r.f)
    recog.analyse(G, r.f, v)
    sub = e_solve.solve(G, None, None)
    lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
    return [x for x in (getattr(G, 'roots', []) or [])
            if val(x) is None or not isinstance(val(x), complex)]

def _lin2(E, us):
    # E = a u + b w + c with a, b, c free of u and w (g may be in them)
    import caspoly
    g = caspoly.expand(S(E))
    r1 = eng.linin(g, us[0])
    if r1 is None:
        return None
    r2 = eng.linin(r1[1], us[1])
    if r2 is None or recog.has(r1[0], us[1]):
        return None
    return S(r1[0]), S(r2[0]), S(r2[1])

def simul(e1, e2, us, lines):
    # two equations, linear in the two unknowns: solved together
    c1 = _lin2(('-', e1[0], e1[1]), us)
    c2 = _lin2(('-', e2[0], e2[1]), us)
    if c1 is None or c2 is None:
        raise ValueError('these equations are not linear in ' + us[0] + ' and ' + us[1])
    a1, b1, k1 = c1
    a2, b2, k2 = c2
    det = S(('-', ('*', a1, b2), ('*', a2, b1)))
    if det == ZERO:
        raise ValueError('the two equations do not fix ' + us[0] + ' and ' + us[1])
    u = eng.nice(S(('/', ('-', ('*', b1, k2), ('*', b2, k1)), det)))
    w = eng.nice(S(('/', ('-', ('*', a2, k1), ('*', a1, k2)), det)))
    lines.append('(1)  ' + txt(S(e1[0])) + ' = ' + txt(S(e1[1])))
    lines.append('(2)  ' + txt(S(e2[0])) + ' = ' + txt(S(e2[1])))
    lines.append('solving (1) and (2) together:  ' + us[0] + ' = ' + txt(u))
    return {us[0]: u, us[1]: w}

def solve_set(eqs, unk, g, lines):
    # eqs: [(label, L, R)]; solves for the unknowns in unk, one equation at a
    # time where it can, two together where it must
    sol = {}
    left = list(eqs)
    for step in range(4):
        if not [u for u in unk if u not in sol]:
            break
        done = False
        for e in left:
            t = S(('-', _put(e[1], sol, g), _put(e[2], sol, g)))
            us = [u for u in unk if u not in sol and recog.has(t, u)]
            if len(us) == 1:
                lines.append(e[0])
                rs = solve1(S(_put(e[1], sol, g)), S(_put(e[2], sol, g)), us[0], lines)
                rs = [x for x in rs if us[0] in ('a', 'p', 'T') or val(x) is None or val(x) >= -1e-12] or rs
                if not rs:
                    raise ValueError('no value of ' + us[0] + ' fits')
                sol[us[0]] = eng.nice(S(rs[0]))
                left.remove(e)
                done = True
                break
        if done:
            continue
        rest = [u for u in unk if u not in sol]
        two = [e for e in left if [u for u in rest if recog.has(S(('-', _put(e[1], sol, g), _put(e[2], sol, g))), u)]]
        if len(rest) == 2 and len(two) >= 2:
            lines.append(two[0][0])
            lines.append(two[1][0])
            got = simul((S(_put(two[0][1], sol, g)), S(_put(two[0][2], sol, g))),
                        (S(_put(two[1][1], sol, g)), S(_put(two[1][2], sol, g))), rest, lines)
            for u in rest:
                if u in got:
                    sol[u] = eng.nice(S(got[u]))
            break
        break
    miss = [u for u in unk if u not in sol]
    if miss:
        raise ValueError('too many unknowns: ' + ', '.join(miss) + ' (two at most, from these equations)')
    return sol

def _show(sol, unk, lines, dec):
    for u in unk:
        x = sol[u]
        lines.append(eng.box(u + ' = ', x, not dec) if not recog.letters(x) or recog.letters(x) == ['g']
                     and not dec else eng.boxt(u + ' = ', x))

def _dec(vals):
    return [1 for v in vals if v and '.' in v] != []

def _gv(vals, i):
    if vals[i] and vals[i].strip():
        t = caslex.parse(vals[i])
        if t is None:
            raise ValueError('g: cannot read that')
        return None if t == ('v', 'g') else t
    return ('/', N(49), N(5))

# ---- a block on a slope or a rough surface -----------------------------------------------------

def block(F, arg, vals):
    # boxes: m, slope, P, pull angle, mu, a, moving, g
    names = ['m', 'slope', 'P', 'pull', 'mu', 'a']
    k, unk = _boxes(vals[:6], names, ())
    g = _gv(vals, 7)
    mv = (vals[6] or '').strip().lower()
    if k['m'] is None:
        raise ValueError('fill in m (? to find it)')
    al = _z(k, 'slope')
    P = _z(k, 'P')
    ph = _z(k, 'pull')
    mu = _z(k, 'mu')
    m = k['m']
    G = ('v', 'g')
    lines = [('w', 'angles in degrees; P pulls at "pull" degrees above the slope, up it')]
    R = ('-', ('*', ('*', m, G), _cos(al)), ('*', P, _sin(ph)))
    drive = ('-', ('*', P, _cos(ph)), ('*', ('*', m, G), _sin(al)))
    lines.append('R = mg cos(slope) - P sin(pull) = ' + txt(S(_put(R, {}, g))))
    if k['a'] is None and not unk:
        # does it move? compare the push along the slope with friction at most mu R
        d = val(S(_put(drive, {}, g)))
        fr = val(S(_put(('*', mu, R), {}, g)))
        lines.append('along the slope: P cos(pull) - mg sin(slope) = ' + eng.sf(d, 4) + ',  mu R = ' + eng.sf(fr, 4))
        if abs(d) <= fr + 1e-12:
            lines.append(eng.boxs('', 'it stays at rest (friction ' + eng.sf(abs(d), 4) + ' <= mu R)'))
            return lines
        a = (abs(d) - fr) / val(S(_put(m, {}, g)))
        lines.append(eng.boxs('', 'it moves ' + ('up' if d > 0 else 'down') + ' the slope'))
        lines.append(eng.box('a = ', N(a), False))
        return lines
    a = _z(k, 'a')
    if mv in ('down', 'd'):
        sgn = -1
    elif mv in ('up', 'u', ''):
        sgn = 1
    else:
        raise ValueError('moving: up or down (empty is up)')
    # moving up: P cos - mg sin - mu R = m a; down: mg sin - P cos - mu R = m a
    lhs = ('-', drive if sgn > 0 else ('neg', drive), ('*', mu, R))
    lines.append(('w', 'moving ' + ('up' if sgn > 0 else 'down') + ' the slope, friction against it'))
    eqs = [(('P cos(pull) - mg sin(slope)' if sgn > 0 else 'mg sin(slope) - P cos(pull)') + ' - mu R = ma',
            lhs, ('*', m, a))]
    sol = solve_set(eqs, unk, g, lines)
    _show(sol, unk, lines, _dec(vals))
    if 'mu' in sol and (val(sol['mu']) or 0) < 0:
        lines.append(('!', 'mu comes out negative: it would move the other way'))
    return lines

# ---- a pulley ------------------------------------------------------------------------------------

def pulley(F, arg, vals):
    # boxes: m1 (on the table or slope), slope, mu, m2 (hanging), a, T, g
    k, unk = _boxes(vals[:6], ['m1', 'slope', 'mu', 'm2', 'a', 'T'], ())
    g = _gv(vals, 6)
    if k['m1'] is None or k['m2'] is None:
        raise ValueError('fill in m1 and m2 (? to find one)')
    for nm in ('a', 'T'):
        if k[nm] is None:
            unk.append(nm)
            k[nm] = ('v', nm)
    m1, m2 = k['m1'], k['m2']
    al = _z(k, 'slope')
    mu = _z(k, 'mu')
    G = ('v', 'g')
    lines = [('w', 'm2 hangs and falls; m1 is on a table (slope 0), a slope, or hangs too (slope 90)')]
    e1 = ('m2: m2 g - T = m2 a', ('-', ('*', m2, G), k['T']), ('*', m2, k['a']))
    e2 = ('m1: T - m1 g sin(slope) - mu m1 g cos(slope) = m1 a',
          ('-', ('-', k['T'], ('*', ('*', m1, G), _sin(al))), ('*', mu, ('*', ('*', m1, G), _cos(al)))),
          ('*', m1, k['a']))
    sol = solve_set([e1, e2], unk, g, lines)
    _show(sol, unk, lines, _dec(vals))
    if 'a' in sol and (val(sol['a']) or 0) < 0:
        lines.append(('!', 'a < 0: m2 would not fall; check friction holds it at rest'))
    return lines

# ---- towing ---------------------------------------------------------------------------------------

def towing(F, arg, vals):
    # boxes: m1 (car), m2 (trailer), D, R1, R2, a, T, g
    k, unk = _boxes(vals[:7], ['m1', 'm2', 'D', 'R1', 'R2', 'a', 'T'], ())
    g = _gv(vals, 7)
    for nm in ('a', 'T'):
        if k[nm] is None:
            unk.append(nm)
            k[nm] = ('v', nm)
    for nm in ('m1', 'm2', 'D'):
        if k[nm] is None:
            raise ValueError('fill in ' + nm + ' (? to find it)')
    R1, R2 = _z(k, 'R1'), _z(k, 'R2')
    lines = [('w', 'D drives the car (m1); the trailer (m2) is pulled by T in the bar; R1, R2 resist')]
    e1 = ('whole: D - R1 - R2 = (m1 + m2) a', ('-', ('-', k['D'], R1), R2), ('*', ('+', k['m1'], k['m2']), k['a']))
    e2 = ('trailer: T - R2 = m2 a', ('-', k['T'], R2), ('*', k['m2'], k['a']))
    sol = solve_set([e1, e2], unk, g, lines)
    _show(sol, unk, lines, _dec(vals))
    if 'T' in sol and (val(sol['T']) or 0) < 0:
        lines.append(('w', 'T < 0: the bar pushes (a thrust)'))
    return lines

# ---- moments ----------------------------------------------------------------------------------------

def _items(s, unk, base):
    # 'F@x, F@x' -> [(F, x)]
    out = []
    if not s or not s.strip():
        return out
    for p in s.split(','):
        if '@' not in p:
            raise ValueError('each force as F@x (or F@angle)')
        f, x = p.split('@', 1)
        n = base + str(len(unk) + 1)
        out.append((_tree(f, n, unk), _tree(x, n + 'x', unk)))
    return out

def moments(F, arg, vals):
    # boxes: down (F@x, ...), up (F@x, ...), g; x from one end
    unk = []
    down = _items(vals[0], unk, 'F')
    up = _items(vals[1], unk, 'R')
    g = _gv(vals, 2)
    if not down and not up:
        raise ValueError('fill in the forces, as F@x')
    lines = [('w', 'distances from one end; masses as 4g (g = ' + (txt(g) if g is not None else 'g') + ')')]
    sd = ZERO
    su = ZERO
    md = ZERO
    mu = ZERO
    for f, x in down:
        sd = ('+', sd, f)
        md = ('+', md, ('*', f, x))
    for f, x in up:
        su = ('+', su, f)
        mu = ('+', mu, ('*', f, x))
    e1 = ('up = down: ' + txt(S(su)) + ' = ' + txt(S(sd)), su, sd)
    e2 = ('moments about the end: ' + txt(S(mu)) + ' = ' + txt(S(md)), mu, md)
    if not unk:
        a = val(S(_put(('-', su, sd), {}, g)))
        b = val(S(_put(('-', mu, md), {}, g)))
        lines.append('up - down = ' + eng.sf(a, 4) + ',  clockwise and anticlockwise differ by ' + eng.sf(b, 4))
        lines.append(eng.boxs('', 'in equilibrium' if abs(a) < 1e-9 and abs(b) < 1e-9 else 'not in equilibrium'))
        return lines
    sol = solve_set([e1, e2], unk, g, lines)
    _show(sol, unk, lines, _dec(vals))
    lines.append(('w', 'about to tilt about a support: the other reaction is 0'))
    return lines

# ---- resultant or equilibrium of forces --------------------------------------------------------------

def forces(F, arg, vals):
    # box: forces as F@angle (degrees anticlockwise from i) or ai + bj; g
    import rvec
    unk = []
    g = _gv(vals, 1)
    if not vals[0]:
        raise ValueError('fill in the forces')
    xs = ZERO
    ys = ZERO
    for p in vals[0].split(','):
        p = p.strip()
        if '@' in p:
            f, an = p.split('@', 1)
            n = 'F' + str(len(unk) + 1)
            ft = _tree(f, n, unk)
            at = _tree(an, 'th' + str(len(unk) + 1), unk)
            xs = ('+', xs, ('*', ft, _cos(at)))
            ys = ('+', ys, ('*', ft, _sin(at)))
        else:
            v, d = rvec.parse_vec(p)
            for c in recog.letters(v[0]) + recog.letters(v[1]):
                if c != 'g' and c not in unk:
                    unk.append(c)
            xs = ('+', xs, v[0])
            ys = ('+', ys, v[1])
    lines = [('w', 'angles in degrees, anticlockwise from i (bearings: 90 - bearing)')]
    X = eng.nice(S(_put(xs, {}, g)))
    Y = eng.nice(S(_put(ys, {}, g)))
    if not unk:
        lines.append('sum of i parts = ' + txt(X) + ',  sum of j parts = ' + txt(Y))
        import math
        xv, yv = val(X), val(Y)
        lines.append(eng.box('resultant = ', eng.nice(S(('sqrt', ('+', ('^', X, N(2)), ('^', Y, N(2)))))), True))
        lines.append(eng.boxs('direction = ', eng.sf(math.atan2(yv, xv) * 180 / math.pi, 4) + ' deg from i'))
        return lines
    lines.append('in equilibrium: the i parts and the j parts each add to 0')
    sol = solve_set([('i: ' + txt(X) + ' = 0', X, ZERO), ('j: ' + txt(Y) + ' = 0', Y, ZERO)], unk, None, lines)
    _show(sol, unk, lines, _dec(vals))
    return lines
