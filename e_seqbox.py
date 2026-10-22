# AP and GP fact boxes (mockup F): fill in three of a, d (or r), n, u(n),
# S(n) (and S to infinity for a GP), ? for what you want. Each formula with
# one unknown left is solved (the Algebra solver's working), then put into
# the others; two formulas in two unknowns are solved together. n must be a
# positive whole number: when the sum or term asked for falls between two
# n, the page gives both sides (n for S(n) > k).
import math
import caseng
import eng
import recog
from eng import S, N, ZERO, ONE, txt, val, has

A, D, R, NN, L, SN, SI = [('v', c) for c in ('a', 'd', 'r', 'n', 'l', 's', 'z')]

AP = (('a', 'd', 'n', 'u(n)', 'S(n)'),
      ((L, ('+', A, ('*', ('-', NN, ONE), D)), 'u(n) = a + (n - 1)d'),
       (SN, ('*', ('/', NN, N(2)), ('+', ('*', N(2), A), ('*', ('-', NN, ONE), D))), 'S(n) = n/2 (2a + (n - 1)d)'),
       (SN, ('*', ('/', NN, N(2)), ('+', A, L)), 'S(n) = n/2 (a + u(n))')))
GP = (('a', 'r', 'n', 'u(n)', 'S(n)', 'S(inf)'),
      ((L, ('*', A, ('^', R, ('-', NN, ONE))), 'u(n) = a r^(n - 1)'),
       (SN, ('/', ('*', A, ('-', ONE, ('^', R, NN))), ('-', ONE, R)), 'S(n) = a(1 - r^n)/(1 - r)'),
       (SI, ('/', A, ('-', ONE, R)), 'S(inf) = a/(1 - r), |r| < 1')))
LET = {'AP': ('a', 'd', 'n', 'l', 's'), 'GP': ('a', 'r', 'n', 'l', 's', 'z')}

def _unknowns(t, known):
    return [c for c in recog.letters(t) if c not in known]

def _put(t, known):
    for c in known:
        t = caseng.subst(t, c, known[c])
    return t

def _solve1(L_, R_, v, lines):
    # one equation in v: the Algebra solver's working, its roots
    import e_solve
    G = recog.from_trees(L_, R_)
    G.var = v
    G.letters = [c for c in G.letters if c != v]
    sub = e_solve.solve(G, None, None)
    lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
    return getattr(G, 'roots', []) or []

def facts(F, arg, vals):
    names, eqs = AP if arg == 'AP' else GP
    lets = LET[arg]
    known = {}
    want = []
    for i in range(len(names)):
        if vals[i] == '?':
            want.append(lets[i])
        elif vals[i] is not None:
            known[lets[i]] = vals[i]
    if len(known) < 2:
        raise ValueError('fill in three of them')
    if 'n' in known:
        n = val(known['n'])
        if n is None or n != int(n) or n < 1:
            raise ValueError('n must be a positive whole number')
    lines = []
    shown = {}
    left = [e for e in eqs]
    note = []
    for step in range(6):
        if want and not [c for c in want if c not in known]:
            break
        done = False
        for e in left:
            us = _unknowns(e[0], known) + [c for c in _unknowns(e[1], known) if c not in _unknowns(e[0], known)]
            if len(us) != 1:
                continue
            v = us[0]
            if e[0] == ('v', v) and want and v not in want:
                continue
            if e[2] not in shown:
                lines.append(e[2])
                shown[e[2]] = 1
            Lt = S(_put(e[0], known))
            Rt = _put(e[1], known)
            if e[0] == ('v', v):
                # the unknown is the subject: work it out (in decimals when
                # they were typed: S makes 1.002^120 an enormous fraction)
                r = _tidy(Rt)
                if _dec(vals) and len(txt(r)) > 30:
                    r = _fl(val(Rt))
                lines.append(names[lets.index(v)] + ' = ' + txt(_show(e[1], known)) + ' = ' + _vt(r))
                known[v] = r
                left.remove(e)
                done = True
                break
            rs = _solve1(Lt, Rt, v, lines)
            rs = [r for r in rs if _ok(v, r, arg)]
            if not rs:
                raise ValueError('no ' + names[lets.index(v)] + ' fits')
            r = rs[0]
            if len(rs) > 1:
                lines.append(('w', 'also ' + names[lets.index(v)] + ' = ' + txt(rs[1]) + ': taking ' + txt(r)))
            if v == 'n':
                x = val(r)
                if abs(x - round(x)) > 1e-9:
                    r = _between(x, e, known, arg, lines, note)
            known[v] = r
            left.remove(e)
            done = True
            break
        if not done:
            break
    miss = [c for c in (want or lets) if c not in known and (c != 'z' or 'z' in want)]
    if miss and len(left) >= 2:
        # two formulas, two unknowns: together
        import e_fn
        pair = [e for e in left if len(set(_unknowns(e[0], known) + _unknowns(e[1], known))) <= 2][:2]
        if len(pair) == 2:
            rows = [txt(S(_put(e[0], known))) + '=' + txt(_put(e[1], known)) for e in pair]
            G = recog.form(rows)
            if G.pair == 'simul':
                lines += [e[2] for e in pair]
                sub = e_fn.simul(G, None, None)
                lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
                got = getattr(G, 'sols', None)
                for ln in sub:
                    if isinstance(ln, tuple) and ln[0] == '=':
                        lines.append(ln)
                if got is None:
                    return lines
    for c in lets:
        if c in known or (c == 'z' and not (arg == 'GP' and _conv(known))) or want and c not in want:
            continue
        for e in eqs:
            if e[0] == ('v', c) and not _unknowns(e[1], known):
                known[c] = _tidy(_put(e[1], known))
    if arg == 'GP' and 'z' in want and 'r' in known and not _conv(known):
        lines.append(eng.boxs('', '|r| >= 1: no sum to infinity'))
    gap = [c for c in (want or lets) if c not in known and c != 'z']
    if gap and not [ln for ln in lines if isinstance(ln, tuple) and ln[0] == '=']:
        raise ValueError('fill in three of them')
    for i in range(len(names)):
        c = lets[i]
        if c not in known:
            continue
        if (want and c in want) or (not want and vals[i] is None):
            t = known[c] if _dec(vals) and len(txt(known[c])) > 30 else _tidy(known[c])
            td = _term(t) if _dec(vals) else None
            if td is not None:
                lines.append(eng.boxs(names[i] + ' = ', td, t))
            else:
                lines.append(eng.box(names[i] + ' = ', t, not F.dec and not _dec(vals)))
    lines += note
    return lines

def _show(t, known):
    # the formula with the values in, negatives in brackets
    for c in known:
        s = txt(known[c])
        simple = s.replace('.', '').isdigit() or s.isalpha()
        t = caseng.subst(t, c, ('v', s if simple else '(' + s + ')'))
    return t

def _vt(t):
    x = val(t)
    s = txt(t)
    if x is not None and not isinstance(x, complex) and ('.' in s or len(s) > 16):
        return eng.dec(x)
    return s

def _fl(x):
    return N(x) if x >= 0 else ('neg', N(-x))

def _term(t):
    # a fraction with a short exact decimal (9372/25 = 374.88), as that decimal
    import caspoly
    r = caspoly.ratof(t)
    if r is None or r[1] == 1:
        return None
    q = r[1]
    k = 0
    while q % 10 == 0 or q % 2 == 0 or q % 5 == 0:
        if q % 10 == 0:
            q //= 10
        elif q % 2 == 0:
            q //= 2
        else:
            q //= 5
        k += 1
    if q != 1 or k > 8:
        return None
    s = eng.sf(r[0] / float(r[1]), 12)
    return s if len(s.replace('-', '').replace('.', '')) <= 10 else None

def _dec(vals):
    return [1 for x in vals if x not in (None, '?') and recog.hasfloat(x)] != []

def _tidy(t):
    try:
        import caspoly
        return eng.nice(caspoly.expand(S(t)))
    except Exception:
        return S(t)

def _conv(known):
    r = known.get('r')
    x = val(r) if r is not None else None
    return x is not None and not isinstance(x, complex) and abs(x) < 1

def _ok(v, r, arg):
    x = val(r)
    if x is None or isinstance(x, complex):
        return False
    if v == 'n':
        return x > 0
    if v == 'r' and arg == 'GP':
        return x != 1
    return True

def _between(x, e, known, arg, lines, note):
    # n not whole: the value is passed between floor and ceil
    lo = int(math.floor(x))
    hi = lo + 1
    nm = 'S(n)' if e[0] == SN else ('u(n)' if e[0] == L else 'S(inf)')
    lines.append('n = ' + ('%.4f' % x) + ' is not a whole number:')
    for k in (lo, hi):
        if k < 1:
            continue
        kn = dict(known)
        kn['n'] = N(k)
        y = val(_put(e[1], kn))
        lines.append(nm.replace('n', str(k)) + ' = ' + eng.dec(y))
    note.append(('w', nm + ' passes ' + txt(known.get(recog.letters(e[0])[0])) + ' between n = ' +
                 str(lo) + ' and n = ' + str(hi)))
    return N(hi)
