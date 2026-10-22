# Sequences and series actions on what was typed: terms of u(n) or of a
# recurrence (with what they do: arithmetic, geometric, periodic,
# converging), sums (the AP or GP formula when the terms are one, so
# letters are fine; else term by term), which term has a value, the limit
# of a recurrence, and binomial expansions (whole n: every term or the
# first few; any other n: the series and where it is valid).
import math
import caseng
import caspoly
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has

def _sub(f, v, k):
    return S(caseng.subst(f, v, k))

def _num(t, name):
    if t is None:
        return None
    x = val(t)
    if x is None or isinstance(x, complex) or x != int(x):
        raise ValueError(name + ' must be a whole number')
    return int(x)

def _exactish(t):
    # tidy a term: exact when it can be
    try:
        return eng.nice(caspoly.expand(S(t)))
    except Exception:
        return S(t)

def _list(name, ts, first, cap=8):
    if len(ts) <= cap:
        return ',  '.join([name + '(' + str(first + i) + ') = ' + _t(ts[i]) for i in range(len(ts))])
    return ',  '.join([name + '(' + str(first + i) + ') = ' + _t(ts[i]) for i in range(cap - 2)]) + \
        ',  ...,  ' + name + '(' + str(first + len(ts) - 1) + ') = ' + _t(ts[-1])

def _t(t):
    s = txt(t)
    if len(s) > 14 and not recog.letters(t):
        v = val(t)
        if v is not None and not isinstance(v, complex):
            return eng.dec(v)
    return s

def total(ts):
    # the sum of the terms, added in pairs so the tree stays shallow (the
    # calculator stops at about 92 nested calls)
    ts = list(ts)
    if not ts:
        return ZERO
    while len(ts) > 1:
        nxt = []
        for i in range(0, len(ts) - 1, 2):
            nxt.append(_exactish(('+', ts[i], ts[i + 1])))
        if len(ts) % 2:
            nxt.append(ts[-1])
        ts = nxt
    return ts[0]

def _same(a, b):
    if txt(a) == txt(b):
        return True
    x = val(a)
    y = val(b)
    if x is None or y is None or isinstance(x, complex) or isinstance(y, complex):
        return False
    return abs(x - y) <= 1e-9 * (1 + abs(x))

def behaviour(ts, lines):
    # what the terms do: arithmetic, geometric, periodic, monotonic, converging
    n = len(ts)
    if n < 3:
        return
    ds = [S(('-', ts[i + 1], ts[i])) for i in range(n - 1)]
    if [1 for d in ds if not _same(d, ds[0])] == []:
        lines.append('arithmetic: a = ' + txt(ts[0]) + ', d = ' + txt(ds[0]))
        return
    if [1 for t in ts if val(t) == 0] == []:
        rs = [S(('/', ts[i + 1], ts[i])) for i in range(n - 1)]
        if [1 for r in rs if not _same(r, rs[0])] == []:
            lines.append('geometric: a = ' + txt(ts[0]) + ', r = ' + txt(rs[0]))
            return
    for p in range(1, n):
        if [1 for i in range(n - p) if not _same(ts[i], ts[i + p])] == []:
            lines.append('periodic, period ' + str(p))
            return
    vs = [val(t) for t in ts]
    if None in vs or [1 for x in vs if isinstance(x, complex)]:
        return
    if [1 for i in range(n - 1) if vs[i + 1] <= vs[i]] == []:
        lines.append('increasing')
    elif [1 for i in range(n - 1) if vs[i + 1] >= vs[i]] == []:
        lines.append('decreasing')
    else:
        lines.append('neither increasing nor decreasing')
    if n >= 8:
        a, b, c = vs[-3], vs[-2], vs[-1]
        if abs(c - b) < abs(b - a) < abs(vs[1] - vs[0]) and abs(c - b) < 1e-3 * (1 + abs(c)):
            lines.append(('w', 'the terms settle towards ' + eng.dec(c) + ': it converges'))

# ---- u(n) = f(n) -----------------------------------------------------------------------------

def terms(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    a = _num(vals[0], 'from') if vals and vals[0] is not None else 1
    m = _num(vals[1], 'how many') if vals and vals[1] is not None else 6
    if m < 1 or m > 200:
        raise ValueError('how many: 1 to 200')
    nm = F.rows[0].name[0] if F.rows[0].name else 'u'
    lines = [nm + '(' + v + ') = ' + txt(f)]
    ts = [_exactish(_sub(f, v, N(k))) for k in range(a, a + m)]
    lines.append(_list(nm, ts, a))
    behaviour(ts, lines)
    lines.append(eng.boxs('', ', '.join([_t(t) for t in ts[:10]]) + (', ...' if m > 10 else '')))
    return lines

def which(F, arg, vals):
    # which term is k: solve f(n) = k, n a positive whole number
    import e_solve
    v = F.var
    f = F.rows[0].f
    k = vals[0]
    lines = []
    G = recog.from_trees(f, k)
    G.var = v
    G.letters = [c for c in G.letters if c != v]
    sub = e_solve.solve(G, None, None)
    lines += [ln for ln in sub if not (isinstance(ln, tuple) and ln[0] == '=')]
    got = []
    for r in getattr(G, 'roots', []) or []:
        x = val(r)
        if x is None or isinstance(x, complex):
            continue
        if abs(x - round(x)) < 1e-9 and round(x) >= 1:
            got.append(int(round(x)))
        else:
            lines.append(v + ' = ' + _t(r) + ': not a whole number')
    if not got:
        lines.append(eng.boxs('', txt(k) + ' is not a term'))
        return lines
    for x in got:
        lines.append(eng.boxs('', txt(k) + ' is term ' + str(x)))
    return lines

def _isgp(f, v):
    # f(v+1)/f(v) the same for every v: the ratio, else None
    r = S(('/', caseng.subst(f, v, ('+', ('v', v), ONE)), f))
    try:
        r = eng.nice(caspoly.expand(r))
    except Exception:
        pass
    if has(r, v):
        return None
    return r

def sum_(F, arg, vals):
    v = F.var
    f = F.rows[0].f
    a = vals[0]
    b = vals[1]
    lines = ['sum of ' + txt(f) + ' from ' + v + ' = ' + txt(a) + (' to ' + txt(b) if b is not None else
                                                                   ' to infinity')]
    p = recog.pdeg(f, v, [False])
    n = None if b is None else S(('+', ('-', b, a), ONE))
    if b is not None and p is not None and p <= 1:
        # an arithmetic series
        u1 = _exactish(_sub(f, v, a))
        un = _exactish(_sub(f, v, b))
        lines.append('arithmetic: first term ' + txt(u1) + ', last term ' + txt(un) + ', ' + txt(n) + ' terms')
        s = _exactish(('*', ('/', n, N(2)), ('+', u1, un)))
        lines.append('S = n/2 (first + last) = ' + txt(n) + '/2 (' + txt(u1) + ' + ' + eng._br(txt(un)) + ')')
        lines.append(eng.box('sum = ', s) if not recog.letters(s) else eng.boxt('sum = ', s))
        return lines
    r = _isgp(f, v)
    if r is not None and val(r) is not None:
        u1 = _exactish(_sub(f, v, a))
        lines.append('geometric: first term ' + txt(u1) + ', r = ' + txt(r))
        if b is None:
            if abs(val(r)) >= 1:
                lines.append(eng.boxs('', 'no sum to infinity: |r| >= 1'))
                return lines
            s = _exactish(('/', u1, ('-', ONE, r)))
            lines.append('S = a/(1 - r)')
        else:
            s = _exactish(('/', ('*', u1, ('-', ONE, ('^', r, n))), ('-', ONE, r)))
            lines.append('S = a(1 - r^n)/(1 - r), n = ' + txt(n))
        lines.append(eng.box('sum = ', s) if not recog.letters(s) else eng.boxt('sum = ', s))
        return lines
    if b is None:
        raise ValueError('a sum to infinity needs a geometric series')
    lo = _num(a, 'from')
    hi = _num(b, 'to')
    if hi < lo:
        raise ValueError('to is less than from')
    if hi - lo > 400:
        if recog.letters(f):
            raise ValueError('too many terms to add with letters in')
        tot = 0.0
        for k in range(lo, hi + 1):
            x = recog.numv(caseng.subst(f, v, N(k)))
            if x is None:
                raise ValueError('a term is undefined at ' + v + ' = ' + str(k))
            tot += x
        lines.append(('w', 'added term by term'))
        lines.append(eng.box('sum = ', N(tot), False))
        return lines
    ts = [_exactish(_sub(f, v, N(k))) for k in range(lo, hi + 1)]
    lines.append(' + '.join([_t(t) for t in ts[:6]]) + (' + ...' if len(ts) > 6 else ''))
    s = total(ts)
    lines.append(eng.box('sum = ', s) if not recog.letters(s) else eng.boxt('sum = ', s))
    return lines

# ---- recurrences ----------------------------------------------------------------------------------

def _run(F, u1, m):
    g = F.g
    u = F.u
    ts = [u1]
    exact = True
    for k in range(1, m):
        prev = ts[-1]
        nxt = caseng.subst(caseng.subst(g, u, prev), 'n', N(k))
        if exact:
            t = _exactish(nxt)
            if len(txt(t)) > 40:
                exact = False
                t = N(val(t))
        else:
            x = val(nxt)
            if x is None or isinstance(x, complex):
                raise ValueError(u + '(' + str(k + 1) + ') is undefined')
            t = N(x) if x >= 0 else ('neg', N(-x))
        ts.append(t)
    return ts

def _rule(F):
    return F.u + '(n+1) = ' + txt(caseng.subst(F.g, F.u, ('v', F.u + '(n)')))

def rterms(F, arg, vals):
    u = F.u
    u1 = vals[0]
    m = _num(vals[1], 'how many') if vals[1] is not None else 6
    if m < 1 or m > 1000:
        raise ValueError('how many: 1 to 1000')
    lines = [_rule(F) + ',  ' + u + '(1) = ' + txt(u1)]
    ts = _run(F, u1, m)
    lines.append(_list(u, ts, 1))
    behaviour(ts[:30], lines)
    lines.append(eng.box(u + '(' + str(m) + ') = ', ts[-1], not eng._floaty(ts[-1])))
    return lines

def rsum(F, arg, vals):
    u = F.u
    u1 = vals[0]
    m = _num(vals[1], 'N')
    if m < 1 or m > 1000:
        raise ValueError('N: 1 to 1000')
    lines = [_rule(F) + ',  ' + u + '(1) = ' + txt(u1)]
    ts = _run(F, u1, m)
    lines.append(_list(u, ts, 1))
    for p in range(1, 7):
        if m > 2 * p and [1 for i in range(min(m, 20) - p) if not _same(ts[i], ts[i + p])] == []:
            cyc = _exactish(eng.build([(t, 1) for t in ts[:p]]))
            lines.append('period ' + str(p) + ': each cycle of ' + str(p) + ' sums to ' + txt(cyc))
            lines.append(str(m // p) + ' cycles, then ' + str(m % p) + ' more term(s)')
            break
    s = total(ts)
    lines.append(eng.box('sum of ' + str(m) + ' terms = ', s, not eng._floaty(s)))
    return lines

def limit(F, arg, vals):
    # L = f(L), and whether the terms go there
    import e_solve
    u = F.u
    g = F.g
    if has(g, 'n'):
        raise ValueError('f depends on n: no fixed limit')
    L = ('v', 'L')
    lines = ['if it converges to L:  L = ' + txt(caseng.subst(g, u, L))]
    G = recog.from_trees(L, caseng.subst(g, u, L))
    G.var = 'L'
    G.letters = [c for c in G.letters if c != 'L']
    sub = e_solve.solve(G, None, None)
    lines += sub[1:]
    d = S(caseng.diff(g, u))
    for r in getattr(G, 'roots', []) or []:
        k = val(caseng.subst(d, u, r))
        if k is None or isinstance(k, complex):
            continue
        lines.append(('w', 'L = ' + _t(r) + ': |f\'(L)| = ' + eng.dec(abs(k)) +
                      (' < 1, terms near it go to it' if abs(k) < 1 else ' >= 1, terms move away')))
    return lines

# ---- binomial expansions -----------------------------------------------------------------------

def _parts(F):
    f = F.rows[0].f
    ts = recog.terms(f[1], 1, [])
    a = ts[0][0] if ts[0][1] > 0 else ('neg', ts[0][0])
    b = ts[1][0] if ts[1][1] > 0 else ('neg', ts[1][0])
    return S(a), S(b), S(f[2])

def _choose(n, k):
    # n(n-1)...(n-k+1)/k! for a rational tree n
    c = ONE
    for i in range(k):
        c = ('*', c, ('/', ('-', n, N(i)), N(i + 1)))
    return S(c)

def _binom(F, m, lines):
    # the first m terms as trees
    v = F.var
    a, b, n = _parts(F)
    whole = n[0] == 'n' and isinstance(n[1], int) and n[1] >= 0
    if not whole and has(a, v):
        if has(b, v):
            raise ValueError('a power that is not a whole number needs a number term in the bracket')
        a, b = b, a
    if whole and m > n[1] + 1:
        m = n[1] + 1
    out = []
    if not whole:
        lines.append('(' + txt(a) + ' + ' + txt(b) + ')^' + eng._br(txt(n)) + ' = ' + eng._br(txt(a)) + '^' +
                     eng._br(txt(n)) + ' (1 + ' + txt(S(('/', b, a))) + ')^' + eng._br(txt(n)))
    for k in range(m):
        if whole:
            c = N(caseng._factorial(n[1]) // (caseng._factorial(k) * caseng._factorial(n[1] - k)))
            cs = str(n[1]) + 'C' + str(k)
        else:
            c = _choose(n, k)
            cs = txt(c)
        t = _exactish(('*', ('*', c, ('^', a, ('-', n, N(k)))), ('^', b, N(k))))
        lines.append(cs + ' (' + txt(a) + ')^' + eng._br(txt(S(('-', n, N(k))))) + ' (' + txt(b) + ')^' + str(k) +
                     ' = ' + txt(t))
        out.append(t)
    if not whole:
        r = S(('/', b, a))
        lines.append(('w', 'valid for |' + txt(r) + '| < 1'))
    return out

def expand(F, arg, vals):
    a, b, n = _parts(F)
    whole = n[0] == 'n' and isinstance(n[1], int) and n[1] >= 0
    m = _num(vals[0], 'how many terms') if vals and vals[0] is not None else (n[1] + 1 if whole else 4)
    if m < 1 or m > 30:
        raise ValueError('how many terms: 1 to 30')
    lines = [txt(F.rows[0].f)]
    ts = _binom(F, m, lines)
    t = eng.build([(x, 1) for x in ts])
    lines.append(eng.boxt('= ' if whole and m >= n[1] + 1 else '~ ', t, False))
    return lines

def coefficient(F, arg, vals):
    v = F.var
    k = _num(vals[0], 'power')
    if k < 0 or k > 60:
        raise ValueError('power: 0 to 60')
    lines = [txt(F.rows[0].f)]
    sub = []
    a, b, n = _parts(F)
    whole = n[0] == 'n' and isinstance(n[1], int) and n[1] >= 0
    ts = _binom(F, 61, sub)
    for i in range(len(ts)):
        t = ts[i]
        co = eng.coeffs(caspoly.expand(t), v)
        if co is not None and len(co) - 1 == k and [c for c in co[:-1] if c != ZERO] == []:
            lines.append(sub[i + (0 if whole else 1)])
            lines.append(eng.box('coefficient of ' + v + '^' + str(k) + ' = ', S(co[-1])))
            return lines
    lines.append(eng.boxs('', 'no ' + v + '^' + str(k) + ' term'))
    return lines
