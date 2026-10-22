# Kinematics with v, s or a as a function of t (a number or a vector in i
# and j): differentiate down (s -> v -> a), integrate up with the starting
# value asked for, when at rest, values at a time, the distance travelled
# (split where v = 0), the largest or smallest v, speed. Calculus from the
# Calculus engine (e_calc), solving from e_solve.
import caseng
import eng
import recog
from eng import S, N, ZERO, ONE, txt, val

T = ('v', 't')
NAME = {'s': 's', 'v': 'v', 'a': 'a'}

def _d(f):
    import e_calc
    return e_calc.deriv(f, 't')

def _i(f):
    import e_calc
    r = e_calc._integ(f, 't')
    if r is None:
        raise ValueError('no integral in standard functions')
    return r

def _vt(F, f):
    # a scalar, or [x, y] as (x)i + (y)j
    if F.vec is None:
        return txt(f)
    out = ''
    for c, u in zip(f, ('i', 'j')):
        c = S(c)
        if c == ZERO:
            continue
        s = txt(c)
        if ' ' in s or '/' in s or '(' in s or 'e^' in s:
            s = '(' + s + ')'
        elif s == '1':
            s = ''
        elif s == '-1':
            s = '-'
        if out:
            out += ' - ' + s[1:] + u if s[:1] == '-' else ' + ' + s + u
        else:
            out = s + u
    return out or '0'

def pythag(t):
    # c sin^2 A + c cos^2 A -> c, so |a| of e^t(cos t, sin t) comes out 2e^t
    ts = eng.sumterms(caspoly_expand(t), 1, [])
    keys = []
    for u, sg in ts:
        k = None
        rest = ONE
        for f, e in recog.factors(u, 1, []):
            if k is None and e > 0 and f[0] == '^' and f[2] == N(2) and f[1][0] in ('sin', 'cos'):
                k = (f[1][0], f[1][1])
            else:
                rest = ('*', rest, f) if e > 0 else ('/', rest, f)
        keys.append((k, txt(S(('*', N(sg), rest))), S(('*', N(sg), rest))))
    out = []
    used = []
    for i in range(len(keys)):
        if i in used:
            continue
        k, rt, r = keys[i]
        if k is not None:
            other = ('cos' if k[0] == 'sin' else 'sin', k[1])
            for j in range(i + 1, len(keys)):
                if j not in used and keys[j][0] == other and keys[j][1] == rt:
                    used.append(j)
                    out.append((r, 1))
                    break
            else:
                out.append((ts[i][0], ts[i][1]))
            continue
        out.append((ts[i][0], ts[i][1]))
    return S(eng.build(out))

def caspoly_expand(t):
    import caspoly
    return caspoly.expand(S(t))

def _root(t):
    # sqrt of a product, factor by factor: sqrt(4 e^(2t)) = 2e^t
    out = ONE
    for f, e in recog.factors(S(t), 1, []):
        if f[0] == 'exp':
            g = ('exp', ('/', f[1], N(2)))
        elif f[0] == '^' and f[2][0] == 'n' and isinstance(f[2][1], int) and f[2][1] % 2 == 0:
            g = ('^', f[1], N(f[2][1] // 2))
        elif f[0] == 'n' and f[1] >= 0:
            g = ('sqrt', f)
        else:
            return ('sqrt', t)
        out = ('*', out, g) if e > 0 else ('/', out, g)
    return out

def mag(f):
    return eng.nice(S(_root(pythag(('+', ('^', f[0], N(2)), ('^', f[1], N(2)))))))

def _map(F, fn, f):
    return [fn(c) for c in f] if F.vec is not None else fn(f)

def _at(F, f, t):
    if F.vec is not None:
        return [eng.nice(S(caseng.subst(c, 't', t))) for c in f]
    return eng.nice(S(caseng.subst(f, 't', t)))

def _chain(F):
    # {'s': .., 'v': .., 'a': ..} as far as differentiating goes
    q = F.kq
    f = F.f if F.vec is None else F.vec
    got = {q: f}
    if q == 's':
        got['v'] = _map(F, _d, f)
        got['a'] = _map(F, _d, got['v'])
    elif q == 'v':
        got['a'] = _map(F, _d, f)
    return got

def _head(F):
    f = F.f if F.vec is None else F.vec
    return F.kq + ' = ' + _vt(F, f)

def _box(F, pre, f):
    if F.vec is None:
        return eng.box(pre, f, not F.dec) if not recog.letters(f) else eng.boxt(pre, f)
    return eng.boxs(pre, _vt(F, f), None)

def deriv(F, arg, vals):
    # arg 'v' or 'a': differentiate down to it
    got = _chain(F)
    lines = [_head(F)]
    if F.kq == 's':
        lines.append('v = ds/dt = ' + _vt(F, got['v']))
    if arg == 'a':
        lines.append('a = dv/dt = ' + _vt(F, got['a']))
    lines.append(_box(F, arg + ' = ', got[arg]))
    if F.vec is not None:
        lines.append(('w', '|' + arg + '| = ' + txt(mag(got[arg]))))
    return lines

def integ(F, arg, vals):
    # arg 'v' (from a) or 's' (from v, or from a twice); vals: the starting values
    f = F.f if F.vec is None else F.vec
    lines = [_head(F)]
    steps = ['v', 's'] if F.kq == 'a' and arg == 's' else [arg]
    k = 0
    for q in steps:
        lo = 'a' if q == 'v' else 'v'
        I = _map(F, _i, f)
        c0 = vals[k] if vals and k < len(vals) and vals[k] is not None else None
        k += 1
        if F.vec is not None:
            c0 = c0 if c0 is not None else None
            cs = [ZERO, ZERO]
            if c0 is not None:
                import rvec
                cs = rvec.comps(c0)
                if cs is None:
                    raise ValueError('the starting ' + q + ': a vector in i and j')
                cs = [S(cs[0]), S(cs[1])]
            at0 = _at(F, I, ZERO)
            f = [eng.nice(S(('+', a, ('-', c, b)))) for a, b, c in zip(I, at0, cs)]
        else:
            c = c0 if c0 is not None else ZERO
            at0 = eng.nice(S(caseng.subst(I, 't', ZERO)))
            f = eng.nice(S(('+', I, ('-', c, at0))))
        lines.append(q + ' = integral of ' + lo + ' dt = ' + _vt(F, I) + ' + c')
        lines.append(('w', q + ' = ' + (txt(c0) if c0 is not None else '0') + ' when t = 0'))
        lines.append(q + ' = ' + _vt(F, f))
    lines.append(_box(F, arg + ' = ', f))
    return lines

def _vfun(F):
    got = _chain(F)
    if 'v' not in got:
        raise ValueError('needs v or s')
    return got['v']

def _roots(f, lines):
    import e_solve
    G = recog.from_trees(f, ZERO)
    G.var = 't'
    G.letters = [c for c in G.letters if c != 't']
    sub = e_solve.solve(G, None, None)
    lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
    out = []
    for r in getattr(G, 'roots', []) or []:
        x = val(r)
        if x is not None and not isinstance(x, complex) and x >= -1e-12:
            out.append(r)
    return out

def rest(F, arg, vals):
    v = _vfun(F)
    lines = [_head(F)]
    if F.kq == 's':
        lines.append('v = ds/dt = ' + _vt(F, v))
    if F.vec is not None:
        lines.append('at rest: both parts of v are 0')
        ts = _roots(v[0], lines)
        ok = [t for t in ts if abs(val(S(caseng.subst(v[1], 't', t))) or 0) < 1e-9]
        if not ok:
            lines.append(eng.boxs('', 'never at rest (t >= 0)'))
        for t in ok:
            lines.append(eng.box('t = ', t, not F.dec))
        return lines
    lines.append('v = 0:')
    ts = _roots(v, lines)
    if not ts:
        lines.append(eng.boxs('', 'never at rest (t >= 0)'))
    for t in ts:
        lines.append(eng.box('t = ', t, not F.dec))
    return lines

def at(F, arg, vals):
    t = vals[0]
    got = _chain(F)
    lines = [_head(F)]
    for q in ('s', 'v', 'a'):
        if q in got:
            x = _at(F, got[q], t)
            lines.append(_box(F, q + '(' + txt(t) + ') = ', x))
            if q == 'v' and F.vec is not None:
                sp = mag(x)
                lines.append(eng.box('speed = ', sp, not F.dec) if not recog.letters(sp) else eng.boxt('speed = ', sp))
            if q == 'a' and F.vec is not None:
                m = mag(x)
                lines.append(('w', '|a| = ' + txt(m)))
    return lines

def distance(F, arg, vals):
    # total distance from t = a to t = b: |s(b) - s(t1)| + ... split where v = 0
    if F.vec is not None or F.letters:
        raise ValueError('distance needs a number v with no letters')
    a = vals[0] if vals[0] is not None else ZERO
    b = vals[1]
    v = _vfun(F)
    s = F.f if F.kq == 's' else _i(v)
    lines = [_head(F)]
    if F.kq != 's':
        lines.append('s = ' + txt(s) + ' (+ c, which cancels)')
    sub = []
    av, bv = val(a), val(b)
    if av is None or bv is None or isinstance(av, complex) or isinstance(bv, complex) or bv <= av:
        raise ValueError('the times need from < to')
    ts = [t for t in _roots(v, sub) if av < val(t) < bv]
    pts = [a] + ts + [b]
    if ts:
        lines.append('v = 0 at t = ' + ', '.join([txt(t) for t in ts]) + ': it turns round')
    tot = ZERO
    for i in range(len(pts) - 1):
        d = eng.nice(S(('-', caseng.subst(s, 't', pts[i + 1]), caseng.subst(s, 't', pts[i]))))
        dv = val(d)
        if dv is None or isinstance(dv, complex):
            raise ValueError('s is not real between t = ' + txt(pts[i]) + ' and ' + txt(pts[i + 1]))
        lines.append('t = ' + txt(pts[i]) + ' to ' + txt(pts[i + 1]) + ': s changes by ' + txt(d))
        tot = ('+', tot, ('abs', d)) if dv < 0 else ('+', tot, d)
    tot = eng.nice(S(tot))
    lines.append(eng.box('distance = ', tot, not F.dec))
    disp = eng.nice(S(('-', caseng.subst(s, 't', b), caseng.subst(s, 't', a))))
    lines.append(('w', 'displacement ' + txt(disp)))
    return lines

def extreme(F, arg, vals):
    # largest or smallest v: dv/dt = 0
    if F.vec is not None:
        raise ValueError('for a number v')
    v = _vfun(F)
    a = _d(v)
    lines = [_head(F), 'a = dv/dt = ' + txt(a), 'a = 0:']
    ts = _roots(a, lines)
    if not ts:
        lines.append(eng.boxs('', 'no turning point of v for t >= 0'))
    for t in ts:
        x = eng.nice(S(caseng.subst(v, 't', t)))
        c = val(S(caseng.subst(_d(a), 't', t)))
        kind = 'maximum' if c is not None and c < 0 else ('minimum' if c is not None and c > 0 else 'stationary')
        lines.append(eng.pair(('t', 'v'), (t, x), not F.dec))
        lines.append(kind + ' v')
    return lines
