# Kinematics boxes: SUVAT (any three of s, u, v, a, t; the equation without
# the one not wanted, solved by the Algebra solver), a projectile (speed and
# angle, or the speed from the time or range), and a v-t graph from typed
# times and velocities (gradients, areas, where it is back at the start).
import math
import caseng
import eng
import recog
from eng import S, N, ZERO, ONE, txt, val

V = dict([(c, ('v', c)) for c in 'suvat'])
EQS = (('v = u + at', 's', (V['v'], ('+', V['u'], ('*', V['a'], V['t'])))),
       ('s = ut + (1/2)at^2', 'v', (V['s'], ('+', ('*', V['u'], V['t']), ('/', ('*', V['a'], ('^', V['t'], N(2))), N(2))))),
       ('s = (1/2)(u + v)t', 'a', (V['s'], ('/', ('*', ('+', V['u'], V['v']), V['t']), N(2)))),
       ('v^2 = u^2 + 2as', 't', (('^', V['v'], N(2)), ('+', ('^', V['u'], N(2)), ('*', N(2), ('*', V['a'], V['s']))))),
       ('s = vt - (1/2)at^2', 'u', (V['s'], ('-', ('*', V['v'], V['t']), ('/', ('*', V['a'], ('^', V['t'], N(2))), N(2))))))

def _put(t, k):
    for c in k:
        t = caseng.subst(t, c, k[c])
    return t

def _solve1(L, R, v, lines):
    import e_solve
    G = recog.from_trees(L, R)
    G.var = v
    G.letters = [c for c in G.letters if c != v]
    sub = e_solve.solve(G, None, None)
    lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
    return getattr(G, 'roots', []) or []

def suvat(F, arg, vals):
    names = 'suvat'
    k = {}
    want = []
    for i in range(5):
        if vals[i] == '?':
            want.append(names[i])
        elif vals[i] is not None:
            k[names[i]] = vals[i]
    if len(k) < 3:
        raise ValueError('fill in three of s, u, v, a, t')
    if 't' in k and (val(k['t']) or 0) < 0:
        raise ValueError('t must be positive')
    lines = []
    miss = [c for c in names if c not in k]
    for step in range(2):
        miss = [c for c in names if c not in k]
        if not miss or want and not [c for c in want if c not in k]:
            break
        target = [c for c in (want or miss) if c not in k][0]
        other = [c for c in miss if c != target]
        eqn = None
        for e in EQS:
            if e[1] in other or not other:
                if target in recog.letters(e[2][0]) + recog.letters(e[2][1]):
                    eqn = e
                    break
        if eqn is None:
            raise ValueError('cannot find ' + target)
        lines.append(eqn[0])
        rs = _solve1(S(_put(eqn[2][0], k)), _put(eqn[2][1], k), target, lines)
        rs = [r for r in rs if val(r) is not None and not isinstance(val(r), complex)]
        if target == 't':
            rs = [r for r in rs if val(r) >= -1e-12]
        if target in ('u', 'v') and len(rs) > 1:
            # a speed from a square: the positive one first (the sign is the direction)
            rs.sort(key=lambda r: -val(r))
        if not rs:
            raise ValueError('no real ' + target + ': those values cannot happen together')
        if len(rs) > 1:
            lines.append(('w', target + ' = ' + ' or '.join([eng.dec(val(r)) for r in rs]) + ': taking ' +
                          eng.dec(val(rs[0])) + (' (the first time)' if target == 't' else ' (positive: choose the direction)')))
        k[target] = rs[0]
    for i in range(5):
        c = names[i]
        if c in k and vals[i] in (None, '?') and (not want or c in want):
            lines.append(eng.box(c + ' = ', eng.nice(S(k[c])), not recog.hasfloat(k[c]) and not _dec(vals)))
    return lines

def _dec(vals):
    return [1 for x in vals if x not in (None, '?') and recog.hasfloat(x)] != []

def _f(t, name):
    if t is None:
        return None
    x = recog.numv(t)
    if x is None:
        x = val(t)
    if x is None or isinstance(x, complex):
        raise ValueError(name + ' must be a number')
    return x

def projectile(F, arg, vals):
    import casui
    from fmt import sf
    u = _f(vals[0] if vals[0] != '?' else None, 'u')
    th = _f(vals[1], 'the angle')
    h = _f(vals[2], 'the height') or 0.0
    g = _f(vals[3], 'g') or 9.8
    T = _f(vals[4] if vals[4] != '?' else None, 'the time')
    R = _f(vals[5] if vals[5] != '?' else None, 'the range')
    if th is None:
        raise ValueError('fill in the angle')
    deg = casui.SET['angle'] == 'deg'
    a = th * math.pi / 180 if deg else th
    c, s = math.cos(a), math.sin(a)
    lines = [('w', 'angle above the horizontal, in ' + ('degrees' if deg else 'radians') +
              '; launched ' + sf(h, 4) + ' m above the landing level; g = ' + sf(g, 4))]
    if u is None:
        if R is not None:
            # h + R tan a - g R^2/(2 u^2 cos^2 a) = 0
            d = h + R * s / c
            if d <= 0:
                raise ValueError('no speed reaches that range')
            u = math.sqrt(g * R * R / (2 * c * c * d))
            lines.append('x: ' + sf(R, 4) + ' = u cos a T,  y: 0 = ' + sf(h, 4) + ' + u sin a T - (1/2)g T^2')
        elif T is not None:
            u = (g * T * T / 2 - h) / (T * s)
            lines.append('y: 0 = ' + sf(h, 4) + ' + u sin a (' + sf(T, 4) + ') - (1/2)(' + sf(g, 4) + ')(' + sf(T, 4) + ')^2')
            if u <= 0:
                raise ValueError('no positive speed fits that time')
        else:
            raise ValueError('fill in u, or the time or range to find it')
        lines.append(eng.box('u = ', N(u), False))
    ux, uy = u * c, u * s
    lines.append('u cos a = ' + sf(ux, 5) + ',  u sin a = ' + sf(uy, 5))
    # flight: h + uy t - g t^2 / 2 = 0, the positive root
    disc = uy * uy + 2 * g * h
    if disc < 0:
        raise ValueError('it never comes down to that level')
    tf = (uy + math.sqrt(disc)) / g
    lines.append(('w', '0 = ' + sf(h, 4) + ' + ' + sf(uy, 5) + 't - ' + sf(g / 2, 4) + 't^2'))
    lines.append(eng.box('time of flight = ', N(tf), False))
    lines.append(eng.box('range = ', N(ux * tf), False))
    tm = uy / g
    if tm > 0:
        lines.append('top at t = ' + sf(tm, 4) + ': height above launch uy^2/(2g)')
        lines.append(eng.box('greatest height = ', N(uy * uy / (2 * g)), False))
    vy = uy - g * tf
    sp = math.sqrt(ux * ux + vy * vy)
    ang = math.atan2(-vy, ux)
    lines.append(('w', 'lands at ' + sf(sp, 4) + ' m/s, ' + (sf(ang * 180 / math.pi, 4) + ' deg' if deg else
                                                             sf(ang, 4) + ' rad') + ' below the horizontal'))
    return lines

def vtgraph(F, arg, vals):
    from fmt import sf
    ts, vs = F.ts, F.vs
    lines = []
    cum = 0.0
    tot = 0.0
    backs = []
    for i in range(len(ts) - 1):
        t0, t1, v0, v1 = ts[i], ts[i + 1], vs[i], vs[i + 1]
        dt = t1 - t0
        a = (v1 - v0) / dt
        area = (v0 + v1) / 2 * dt
        # distance: split where v crosses 0
        if v0 * v1 < 0:
            tc = t0 + v0 / (v0 - v1) * dt
            d = abs(v0) * (tc - t0) / 2 + abs(v1) * (t1 - tc) / 2
        else:
            d = abs(area)
        # back where it started inside this piece: cum + v0 x + a x^2/2 = 0
        if a != 0:
            disc = v0 * v0 - 2 * a * cum
            if disc >= 0:
                for sgn in (1, -1):
                    x = (-v0 + sgn * math.sqrt(disc)) / a
                    if 1e-9 < x <= dt + 1e-9:
                        backs.append(t0 + x)
        elif v0 != 0:
            x = -cum / v0
            if 1e-9 < x <= dt + 1e-9:
                backs.append(t0 + x)
        cum += area
        tot += d
        lines.append('t ' + sf(t0, 4) + ' to ' + sf(t1, 4) + ': a = ' + sf(a, 4) + ', area ' + sf(area, 5) +
                     ', so far ' + sf(cum, 5))
    lines.append(eng.box('displacement = ', N(cum) if cum >= 0 else ('neg', N(-cum)), False))
    lines.append(eng.box('distance = ', N(tot), False))
    if backs:
        bs = []
        for b in backs:
            if not [1 for c in bs if abs(c - b) < 1e-9]:
                bs.append(b)
        lines.append(eng.boxs('back at the start at t = ', ', '.join([sf(b, 4) for b in bs])))
    lines.append(('w', 'straight lines between the points; area under v-t is displacement'))
    return lines
