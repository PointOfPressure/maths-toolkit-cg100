# Algebra operations built on the canonical engine: expand (polynomial,
# binomial, compound-angle, log), factorise, complete the square, polynomial
# division, single fraction, rationalise, substitute, rearrange, series, limit.
import caseng
import caspoly

MAXDEPTH = 6       # compound-angle / log expansion passes
MAXTERMS = 12      # series terms
MAXHOP = 6         # l'Hopital passes
MAXGUESS = 8       # candidate sub-expressions tried when factorising
R1 = (1, 1)

def _S(n):
    return caseng.simplify(n)

def _terms(n, sgn=1):
    out = []
    caseng._flatadd(n, sgn, out)
    return out

def _sum(items):
    return caseng._addf(items)

def _prod(items):
    return caseng._mulf(items)

def _num(v):
    return ('n', v)

def _rat(p, q):
    return caseng._ratnode(caseng._rq(p, q))

# ---- expand ---------------------------------------------------------------

def _splitarg(arg):
    # arg -> (A, B) with arg = A + B, or k*u -> (u, (k-1)u)
    k = caseng._pimult(caseng.simplify(arg))
    if k is not None and k[1] == 12:
        # pi/12 families: p/12 = a/4 + b/3 with 3a + 4b = p
        p = k[0]
        b = 0
        while b < 3 and (p - 4 * b) % 3:
            b += 1
        if b < 3:
            a = (p - 4 * b) // 3
            return (_prod([(_rat(a, 4), 1), (('v', 'pi'), 1)]),
                    _prod([(_rat(b, 3), 1), (('v', 'pi'), 1)]))
    raw = _terms(arg)
    if len(raw) >= 2:
        return (_sum([raw[0]]), _sum(raw[1:]))
    coef, fl, cxc, out = caseng._termparts([(arg, 1)])
    if fl is None and cxc is None and coef[1] == 1 and coef[0] >= 2 and out:
        u = caseng._termnode(R1, None, None, out)
        return (u, _prod([(_num(coef[0] - 1), 1), (u, 1)]))
    return None

def _extrig(n, depth):
    t = n[0]
    if depth >= MAXDEPTH:
        return n
    if t == 'sin' or t == 'cos' or t == 'tan':
        sp = _splitarg(n[1])
        if sp is not None:
            a, b = sp
            sa = _extrig(('sin', a), depth + 1)
            ca = _extrig(('cos', a), depth + 1)
            sb = _extrig(('sin', b), depth + 1)
            cb = _extrig(('cos', b), depth + 1)
            if t == 'sin':
                return _sum([(_prod([(sa, 1), (cb, 1)]), 1),
                             (_prod([(ca, 1), (sb, 1)]), 1)])
            if t == 'cos':
                return _sum([(_prod([(ca, 1), (cb, 1)]), 1),
                             (_prod([(sa, 1), (sb, 1)]), -1)])
            ta = _extrig(('tan', a), depth + 1)
            tb = _extrig(('tan', b), depth + 1)
            top = _sum([(ta, 1), (tb, 1)])
            bot = _sum([(_num(1), 1), (_prod([(ta, 1), (tb, 1)]), -1)])
            return _prod([(top, 1), (bot, -1)])
    if t == 'sinh' or t == 'cosh':
        sp = _splitarg(n[1])
        if sp is not None:
            a, b = sp
            sa = _extrig(('sinh', a), depth + 1)
            ca = _extrig(('cosh', a), depth + 1)
            sb = _extrig(('sinh', b), depth + 1)
            cb = _extrig(('cosh', b), depth + 1)
            if t == 'sinh':
                return _sum([(_prod([(sa, 1), (cb, 1)]), 1),
                             (_prod([(ca, 1), (sb, 1)]), 1)])
            return _sum([(_prod([(ca, 1), (cb, 1)]), 1),
                         (_prod([(sa, 1), (sb, 1)]), 1)])
    return n

def _exlog(n):
    # ln(ab) -> ln a + ln b, ln(a/b) -> ln a - ln b, ln(a^k) -> k ln a
    t = n[0]
    if t != 'ln' and t != 'log':
        return n
    coef, fl, cxc, out = caseng._termparts([(n[1], 1)])
    if fl is not None or cxc is not None:
        return n
    items = []
    if coef != R1:
        if coef[0] < 0:
            return n
        if coef[0] != 1:
            items.append(((t, _num(coef[0])), 1))
        if coef[1] != 1:
            items.append(((t, _num(coef[1])), -1))
    for b, e in out:
        if b == ('v', 'e') and t == 'ln':
            items.append((e, 1))
            continue
        items.append((_prod([(e, 1), ((t, b), 1)]), 1))
    if not items:
        return _num(0)
    if len(items) == 1 and items[0][1] == 1 and coef == R1 and len(out) == 1 \
            and caseng._ratval(out[0][1]) == R1:
        return n
    return _sum(items)

def _walk(n, fn, depth):
    t = n[0]
    if t == 'n' or t == 'v':
        return n
    if len(n) == 2:
        return fn((t, _walk(n[1], fn, depth + 1)), depth)
    if len(n) == 3:
        return fn((t, _walk(n[1], fn, depth + 1), _walk(n[2], fn, depth + 1)), depth)
    return n

def expand(node, trig=True, logs=True):
    n = node
    if not (trig or logs):
        return caspoly.expand(_S(n))
    def step(x, d):
        if trig:
            x = _extrig(x, 0)
        if logs:
            x = _exlog(x)
        return x
    caseng.FOLD[0] = False
    try:
        n = caspoly.expand(_walk(_S(n), step, 0))
        if trig:
            n = expairs(n)
    finally:
        caseng.FOLD[0] = True
    return n

def _eiparts(t):
    # c * e^(i k u) -> (c tree, k rational, u tree) else None
    coef, fl, cxc, out = caseng._termparts([(t, 1)])
    hit = None
    arg = None
    for f in out:
        if f[0][0] == 'exp' and caseng._ratval(f[1]) == R1:
            hit = f
            arg = f[0][1]
            break
        if f[0] == ('v', 'e'):
            hit = f
            arg = f[1]
            break
    if hit is None:
        return None
    c2, f2, cx2, o2 = caseng._termparts([(arg, 1)])
    if f2 is not None or cx2 is None or cx2.real != 0 or not o2:
        return None
    k = caseng._fltrat(cx2.imag)
    if k is None:
        return None
    k = caspoly.rmul(k, c2)
    rest = [f for f in out if f is not hit]
    c = caseng._termnode(coef, fl, cxc, rest)
    u = caseng._termnode(R1, None, None, o2)
    return (c, k, u)

def expairs(node):
    # c e^(iku) + c e^(-iku) -> 2c cos(ku); c e^(iku) - c e^(-iku) -> 2ic sin(ku)
    n = _S(node)
    ts = _terms(n)
    info = []
    for t, s in ts:
        p = _eiparts(t)
        if p is not None and s < 0:
            p = (_S(('neg', p[0])), p[1], p[2])
        info.append(p)
    if len([p for p in info if p is not None]) < 2:
        return node
    used = [False] * len(ts)
    out = []
    hit = False
    for i in range(len(ts)):
        if used[i] or info[i] is None:
            continue
        ci, ki, ui = info[i]
        for j in range(i + 1, len(ts)):
            if used[j] or info[j] is None:
                continue
            cj, kj, uj = info[j]
            if kj != (-ki[0], ki[1]) or caseng.tostr(ui) != caseng.tostr(uj):
                continue
            ang = _S(_prod([(caseng._ratnode(ki if ki[0] > 0 else kj), 1), (ui, 1)]))
            same = caseng.tostr(ci) == caseng.tostr(cj)
            opp = caseng.tostr(_S(('neg', ci))) == caseng.tostr(cj)
            if same:
                out.append((_prod([(_num(2), 1), (ci, 1), (('cos', ang), 1)]), 1))
            elif opp:
                cp = ci if ki[0] > 0 else cj
                out.append((_prod([(_num(2j), 1), (cp, 1), (('sin', ang), 1)]), 1))
            else:
                continue
            used[i] = True
            used[j] = True
            hit = True
            break
    if not hit:
        return node
    for i in range(len(ts)):
        if not used[i]:
            out.append(ts[i])
    return _S(_sum(out))

def combine_log(node):
    # a ln u + b ln v -> ln(u^a v^b)
    raw = _terms(_S(node))
    items = []
    rest = []
    name = None
    for t, s in raw:
        coef, fl, cxc, out = caseng._termparts([(t, 1)])
        hit = None
        for b, e in out:
            if (b[0] == 'ln' or b[0] == 'log') and caseng._ratval(e) == R1:
                hit = b
                break
        if hit is None or fl is not None or cxc is not None or len(out) != 1:
            rest.append((t, s))
            continue
        if name is None:
            name = hit[0]
        elif name != hit[0]:
            rest.append((t, s))
            continue
        k = coef if s > 0 else (-coef[0], coef[1])
        items.append((hit[1], k))
    if len(items) < 2:
        return _S(node)
    arg = _prod([(caseng._pow(u, caseng._ratnode(k)), 1) for u, k in items])
    out = [((name, arg), 1)]
    return _sum(out + rest)

MAXPRIME = 1000    # trial division for the primes of a log argument

def _primes(n, acc, k):
    # add k * (exponent of p) for each prime p of the positive integer n
    d = 2
    while d <= MAXPRIME and d * d <= n:
        while n % d == 0:
            acc[d] = caspoly.radd(acc.get(d, caspoly.R0), k)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        acc[n] = caspoly.radd(acc.get(n, caspoly.R0), k)

def _rgcd(a, b):
    # gcd of two positive rationals
    return (caseng.gcd(a[0], b[0]), a[1] * b[1] // caseng.gcd(a[1], b[1]))

def _hypln(n, d):
    # asinh u -> ln(u + sqrt(u^2+1)), acosh u -> ln(u + sqrt(u^2-1)),
    # atanh u -> ln((1+u)/(1-u))/2
    t = n[0]
    if t == 'asinh':
        u = n[1]
        return ('ln', ('+', u, ('sqrt', ('+', ('^', u, _num(2)), _num(1)))))
    if t == 'acosh':
        u = n[1]
        return ('ln', ('+', u, ('sqrt', ('-', ('^', u, _num(2)), _num(1)))))
    if t == 'atanh':
        u = n[1]
        return ('/', ('ln', ('/', ('+', _num(1), u), ('-', _num(1), u))), _num(2))
    return n

def lnform(node):
    # exact constants in log form: inverse hyperbolics as logs, and the
    # constant logs combined: ln 2 + ln5/2 - ln10/2 -> ln(2)/2,
    # arsinh(sqrt3) - arsinh(sqrt3/3) -> ln((2sqrt(3)+3)/3)
    n = _S(_walk(node, _hypln, 0))
    if n[0] != '+' and n[0] != '-':
        # a product such as pi(3ln25 - 3ln9 + 4): each bracketed sum
        coef, fl, cxc, out = caseng._termparts([(n, 1)])
        hit = False
        for f in out:
            if f[0][0] in ('+', '-') and 'ln' in caseng.tostr(f[0]):
                f[0] = _lnsum(f[0])
                hit = True
        return caseng._termnode(coef, fl, cxc, out) if hit else n
    return _lnsum(n)

def _lnsum(n):
    acc = {}
    surd = []
    rest = []
    for t, s in _terms(n):
        coef, fl, cxc, out = caseng._termparts([(t, 1)])
        if fl is None and cxc is None and len(out) == 1 and out[0][0][0] == 'ln' \
                and caseng._ratval(out[0][1]) == R1 and not caseng.vars_in(out[0][0][1]):
            k = coef if s > 0 else (-coef[0], coef[1])
            a = out[0][0][1]
            r = caseng._ratval(a)
            if r is not None and r[0] > 0:
                _primes(r[0], acc, k)
                _primes(r[1], acc, (-k[0], k[1]))
            else:
                surd.append((a, k))
            continue
        rest.append((t, s))
    items = [(_num(p), e) for p, e in acc.items() if e[0] != 0] + surd
    if not items:
        return _S(_sum(rest)) if rest else _num(0)
    g = None
    for b, e in items:
        ae = (abs(e[0]), e[1])
        g = ae if g is None else _rgcd(g, ae)
    if surd:
        # keep the surd argument whole and let a prime go under a root:
        # ln(2+sqrt3) - ln(3)/2 -> ln((2+sqrt3)/sqrt3), not ln((7+4sqrt3)/3)/2
        gs = None
        for b, e in surd:
            ae = (abs(e[0]), e[1])
            gs = ae if gs is None else _rgcd(gs, ae)
        ok = True
        for p, e in acc.items():
            if caspoly.rdiv(e, gs)[1] > 2:
                ok = False
        if ok:
            g = gs
    # a single log term with a positive multiple: g ln(prod b^(e/g))
    neg = 0
    for b, e in items:
        if e[0] < 0:
            neg += 1
    if neg * 2 > len(items):
        g = (-g[0], g[1])
    arg = _prod([(caseng._pow(b, caseng._ratnode(caspoly.rdiv(e, g))), 1) for b, e in items])
    best = arg
    sa = caseng.tostr(arg)
    fs = []
    if 'sqrt' in sa:
        # a surd in a denominator, or a bracket times a surd: tidy it
        fs = [rationalise, caspoly.expand]
        if '/' in sa:
            fs.append(lambda a: caspoly.expand(rationalise(a)))
    for f in fs:
        try:
            a2 = _S(f(arg))
        except Exception:
            continue
        if len(caseng.tostr(a2)) < len(caseng.tostr(best)):
            best = a2
    arg = best
    lg = _prod([(caseng._ratnode(g), 1), (('ln', arg), 1)])
    return _sum([(lg, 1)] + rest)

def logbase(node, b):
    # a^x -> b^(x log_b a)  (4^x -> 2^(2x))
    def step(x, d):
        if x[0] != '^':
            return x
        base = caseng._ratval(x[1])
        if base is None or base[1] != 1 or base[0] < 2:
            return x
        j = caseng._logpow(base[0], b)
        if j is None:
            return x
        return caseng._pow(_num(b), _prod([(_num(j), 1), (x[2], 1)]))
    return _walk(_S(node), step, 0)

def to_exp(node):
    # hyperbolics and inverse hyperbolics in exponential / log form
    def step(x, d):
        t = x[0]
        if t == 'sinh':
            return _prod([(_sum([(('exp', x[1]), 1), (('exp', _negt(x[1])), -1)]), 1),
                          (_num(2), -1)])
        if t == 'cosh':
            return _prod([(_sum([(('exp', x[1]), 1), (('exp', _negt(x[1])), 1)]), 1),
                          (_num(2), -1)])
        if t == 'tanh':
            up = _sum([(('exp', _prod([(_num(2), 1), (x[1], 1)])), 1), (_num(-1), 1)])
            dn = _sum([(('exp', _prod([(_num(2), 1), (x[1], 1)])), 1), (_num(1), 1)])
            return _prod([(up, 1), (dn, -1)])
        if t == 'asinh':
            return ('ln', _sum([(x[1], 1),
                                (('sqrt', _sum([(caseng._pow(x[1], _num(2)), 1),
                                                (_num(1), 1)])), 1)]))
        if t == 'acosh':
            return ('ln', _sum([(x[1], 1),
                                (('sqrt', _sum([(caseng._pow(x[1], _num(2)), 1),
                                                (_num(-1), 1)])), 1)]))
        if t == 'atanh':
            up = _sum([(_num(1), 1), (x[1], 1)])
            dn = _sum([(_num(1), 1), (x[1], -1)])
            return _prod([(('ln', _prod([(up, 1), (dn, -1)])), 1), (_num(2), -1)])
        return x
    return _S(_walk(_S(node), step, 0))

def _negt(n):
    return caseng._negnode(n)

# ---- factorise ------------------------------------------------------------

def common_factor(node):
    # -> (factor, rest) with node = factor * rest, or None
    raw = _terms(_S(node))
    if len(raw) < 2:
        return None
    parts = []
    for n, s in raw:
        coef, fl, cxc, out = caseng._termparts([(n, 1)])
        if fl is not None or cxc is not None:
            return None
        if s < 0:
            coef = (-coef[0], coef[1])
        parts.append((coef, out))
    gnum = 0
    gden = 1
    for coef, out in parts:
        gnum = caseng.gcd(gnum, coef[0])
        gden = gden // caseng.gcd(gden, coef[1]) * coef[1]
    if gnum == 0:
        return None
    g = caseng._rq(gnum, gden)
    common = []
    for b, e in parts[0][1]:
        r = caseng._ratval(e)
        if r is None or r[0] <= 0:
            continue
        lo = r
        ok = True
        for coef, out in parts[1:]:
            got = None
            for b2, e2 in out:
                if b2 == b:
                    got = caseng._ratval(e2)
            if got is None or got[0] <= 0:
                ok = False
                break
            if got[0] * lo[1] < lo[0] * got[1]:
                lo = got
        if ok:
            common.append([b, caseng._ratnode(lo)])
    if g == R1 and not common:
        return None
    if parts[0][0][0] < 0:
        g = (-g[0], g[1])
    fac = caseng._termnode(g, None, None, common)
    if fac == _num(1):
        return None
    rest = _sum([(_prod([(n, 1), (fac, -1)]), s) for n, s in raw])
    return (fac, rest)

def _polyin(node, mindeg=2):
    # node as a polynomial in some sub-expression u -> (u, coeffs) or None
    raw = _terms(_S(node))
    if len(raw) < 2 or len(raw) > MAXGUESS:
        return None
    rows = []
    base = None
    for n, s in raw:
        coef, fl, cxc, out = caseng._termparts([(n, 1)])
        if fl is not None or cxc is not None or len(out) > 1:
            return None
        if s < 0:
            coef = (-coef[0], coef[1])
        if not out:
            rows.append((coef, None))
            continue
        if base is None:
            base = out[0][0]
        elif base != out[0][0]:
            return None
        rows.append((coef, out[0][1]))
    if base is None:
        return None
    exps = [_num(1)]
    for c, e in rows:
        if e is not None and e not in exps:
            exps.append(e)
    for unit in exps:
        ks = []
        ok = True
        for c, e in rows:
            if e is None:
                ks.append(0)
                continue
            r = caseng._ratval(_prod([(e, 1), (unit, -1)]))
            if r is None or r[1] != 1 or r[0] < 0 or r[0] > caspoly.MAXPOW:
                ok = False
                break
            ks.append(r[0])
        if not ok:
            continue
        deg = 0
        for k in ks:
            if k > deg:
                deg = k
        if deg < mindeg:
            continue
        co = []
        i = 0
        while i <= deg:
            co.append(caspoly.R0)
            i += 1
        i = 0
        for c, e in rows:
            co[ks[i]] = caspoly.radd(co[ks[i]], c)
            i += 1
        u = caseng._termnode(R1, None, None, [[base, unit]])
        return (u, caspoly.ptrim(co))
    return None

def _fromfactors(lead, fs, u):
    parts = []
    for f, m in fs:
        den = 1
        for c in f:
            den = den // caseng.gcd(den, c[1]) * c[1]
        if den != 1:
            f = [caspoly.rmul(c, (den, 1)) for c in f]
            lead = caspoly.rmul(lead, caseng._rq(1, den ** m))
        ft = _polytree(f, u)
        parts.append((ft if m == 1 else caseng._pow(ft, _num(m)), 1))
    if lead != R1:
        parts.append((caspoly.ratnode(lead), 1))
    return _prod(parts)

def _polytree(co, u):
    items = []
    i = len(co) - 1
    while i >= 0:
        if not caspoly.rzero(co[i]):
            items.append((_prod([(caspoly.ratnode(co[i]), 1),
                                 (caseng._pow(u, _num(i)), 1)]), 1))
        i -= 1
    if not items:
        return _num(0)
    return _sum(items)

def factorise(node, var='x', surds=False):
    n = _S(node)
    r = caspoly.factor(n, var)
    if r is not None:
        return r
    sub = _polyin(n)
    if sub is not None:
        u, co = sub
        lead, fs = caspoly.pfactors(co, var)
        if fs and not (len(fs) == 1 and fs[0][1] == 1 and len(fs[0][0]) == len(co)):
            return _fromfactors(lead, fs, u)
    cf = common_factor(n)
    if cf is not None:
        inner = caspoly.factor(cf[1], var)
        if inner is None:
            inner = cf[1]
        if inner[0] in ('+', '-', '*', '^'):
            return _prod([(cf[0], 1), (inner, 1)])
    if surds:
        s = dots_surd(n, var)
        if s is not None:
            return s
    c = cubes(n, var)
    if c is not None:
        return c
    return None

def dots_surd(node, var='x'):
    # x^2 - a  ->  (x - sqrt a)(x + sqrt a) with a not a perfect square
    p = caspoly.poly(_S(node), var)
    if p is None or len(p) != 3 or not caspoly.rzero(p[1]):
        return None
    a = p[2]
    c = caspoly.rdiv(caspoly.rneg(p[0]), a)
    if c is None or c[0] <= 0:
        return None
    root = caseng._pow(caspoly.ratnode(c), _rat(1, 2))
    x = ('v', var)
    body = _prod([(_sum([(x, 1), (root, -1)]), 1), (_sum([(x, 1), (root, 1)]), 1)])
    if a == R1:
        return body
    return _prod([(caspoly.ratnode(a), 1), (body, 1)])

def cubes(node, var='x'):
    # a^3 +/- b^3 with rational cube roots
    p = caspoly.poly(_S(node), var)
    if p is None or len(p) != 4:
        return None
    if not caspoly.rzero(p[1]) or not caspoly.rzero(p[2]):
        return None
    a3 = p[3]
    b3 = p[0]
    a = _cuberoot(a3)
    b = _cuberoot(b3)
    if a is None or b is None:
        return None
    x = ('v', var)
    ax = _prod([(caspoly.ratnode(a), 1), (x, 1)])
    bb = caspoly.ratnode(b)
    lin = _sum([(ax, 1), (bb, 1)])
    quad = _sum([(caseng._pow(ax, _num(2)), 1), (_prod([(ax, 1), (bb, 1)]), -1),
                 (caseng._pow(bb, _num(2)), 1)])
    return _prod([(lin, 1), (quad, 1)])

def _cuberoot(r):
    if r[0] == 0:
        return caspoly.R0
    sgn = 1
    p = r[0]
    if p < 0:
        sgn = -1
        p = -p
    a = caseng._introot(p, 3)
    b = caseng._introot(r[1], 3)
    if a is None or b is None:
        return None
    return caseng._rq(sgn * a, b)

def complete_square(node, var='x'):
    # a x^2 + b x + c -> a(x + b/2a)^2 + (c - b^2/4a)
    p = caspoly.poly(_S(node), var)
    if p is None or len(p) != 3:
        return None
    a = p[2]
    b = p[1]
    c = p[0]
    h = caspoly.rdiv(b, caspoly.rmul(a, (2, 1)))
    k = caspoly.rsub(c, caspoly.rmul(a, caspoly.rmul(h, h)))
    inner = _sum([(('v', var), 1), (caspoly.ratnode(h), 1)])
    sq = caseng._pow(inner, _num(2))
    items = [(_prod([(caspoly.ratnode(a), 1), (sq, 1)]), 1)]
    if not caspoly.rzero(k):
        items.append((caspoly.ratnode(k), 1))
    return _sum(items)

# ---- polynomial division --------------------------------------------------

def divide(num, den, var='x'):
    # -> (quotient tree, remainder tree) or None
    a = caspoly.poly(_S(num), var)
    b = caspoly.poly(_S(den), var)
    if a is None or b is None or not b:
        return None
    qr = caspoly.pdivmod(a, b)
    if qr is None:
        return None
    return (caspoly.ptree(qr[0], var), caspoly.ptree(qr[1], var))

def remainder(p, a, var='x'):
    # remainder theorem: p(a)
    return _S(caseng.subst(_S(p), var, _S(a)))

# ---- single fraction, rationalising ---------------------------------------

def single_fraction(node, var=None):
    n = _S(node)
    vs = caseng.vars_in(n)
    if var is None and len(vs) == 1:
        var = vs[0]
    if var is not None and var in vs:
        try:
            r = caspoly.ratnorm(n, var)
        except Exception:
            r = None
        if r is not None:
            return r
    raw = _terms(n)
    if len(raw) < 2:
        return n
    dens = []
    keys = []
    for t, s in raw:
        coef, fl, cxc, out = caseng._termparts([(t, 1)])
        for b, e in out:
            r = caseng._ratval(e)
            if r is None or r[0] >= 0:
                continue
            k = caseng.tostr(b)
            p = (-r[0], r[1])
            if k in keys:
                i = keys.index(k)
                if p[0] * dens[i][1][1] > dens[i][1][0] * p[1]:
                    dens[i] = [b, p]
            else:
                keys.append(k)
                dens.append([b, p])
        if coef[1] != 1:
            k = str(coef[1])
            if k not in keys:
                keys.append(k)
                dens.append([_num(coef[1]), (1, 1)])
    if not dens:
        return n
    D = _prod([(caseng._pow(b, caseng._ratnode(p)), 1) for b, p in dens])
    N = _sum([(_prod([(t, 1), (D, 1)]), s) for t, s in raw])
    N = caspoly.expand(N)
    return _prod([(N, 1), (D, -1)])

def rationalise(node):
    # clear surds from the denominator, symbolic ones too
    n = _S(node)
    guard = 0
    while guard < 4:
        guard += 1
        coef, fl, cxc, out = caseng._termparts([(n, 1)])
        hit = None
        for b, e in out:
            r = caseng._ratval(e)
            if r is None or r[0] >= 0:
                continue
            if caseng._hassqrt(b) or (b[0] == '+' or b[0] == '-'):
                if caseng._hassqrt(b):
                    hit = (b, r)
                    break
        if hit is None:
            return n
        b, r = hit
        if b[0] == 'sqrt':
            n = _prod([(n, 1), (b, 1), (b, -1)])
            n = _prod([(_prod([(n, 1), (b, 1)]), 1), (b[1], -1)])
            continue
        conj = _conj(b)
        if conj is None:
            return n
        top = _mulnum(n, conj)
        bot = caspoly.expand(_prod([(b, 1), (conj, 1)]))
        if caseng._isneg(bot):
            top = _negt(top)
            bot = _negt(bot)
        return _S(_prod([(top, 1), (bot, -1)]))
    return n

def _mulnum(node, conj):
    coef, fl, cxc, out = caseng._termparts([(_S(node), 1)])
    keep = []
    for b, e in out:
        r = caseng._ratval(e)
        if r is not None and r[0] < 0 and (b[0] == '+' or b[0] == '-') \
                and caseng._hassqrt(b):
            continue
        keep.append([b, e])
    top = caseng._termnode(coef, fl, cxc, keep)
    return caspoly.expand(_prod([(top, 1), (conj, 1)]))

def _conj(b):
    raw = _terms(b)
    rat = []
    surd = []
    for node, s in raw:
        if caseng._hassqrt(node):
            surd.append((node, -s))
        else:
            rat.append((node, s))
    if not surd or not rat or len(surd) > 1:
        return None
    return _sum(rat + surd)

# ---- substitution and rearranging -----------------------------------------

def subst_exact(f, var, value):
    return _S(caseng.subst(_S(f), var, _S(value)))

def linin(n, var):
    # n = A*var + B with A, B free of var, else None
    t = n[0]
    if not caseng._hasvar(n, var):
        return (_num(0), n)
    if t == 'v':
        return (_num(1), _num(0))
    if t == 'neg':
        r = linin(n[1], var)
        return None if r is None else (_negt(r[0]), _negt(r[1]))
    if t == '+' or t == '-':
        p = linin(n[1], var)
        q = linin(n[2], var)
        if p is None or q is None:
            return None
        sg = 1 if t == '+' else -1
        return (_sum([(p[0], 1), (q[0], sg)]), _sum([(p[1], 1), (q[1], sg)]))
    if t == '*':
        p = linin(n[1], var)
        q = linin(n[2], var)
        if p is None or q is None:
            return None
        if p[0] != _num(0) and q[0] != _num(0):
            return None
        if p[0] == _num(0):
            return (_prod([(p[1], 1), (q[0], 1)]), _prod([(p[1], 1), (q[1], 1)]))
        return (_prod([(q[1], 1), (p[0], 1)]), _prod([(q[1], 1), (p[1], 1)]))
    if t == '/':
        if caseng._hasvar(n[2], var):
            return None
        p = linin(n[1], var)
        if p is None:
            return None
        return (_prod([(p[0], 1), (n[2], -1)]), _prod([(p[1], 1), (n[2], -1)]))
    if t == '^':
        r = caseng._ratval(n[2])
        if r == R1:
            return linin(n[1], var)
        return None
    return None

def _cleardenom(E, var):
    raw = _terms(E)
    keys = []
    dens = []
    for t, s in raw:
        coef, fl, cxc, out = caseng._termparts([(t, 1)])
        for b, e in out:
            r = caseng._ratval(e)
            if r is None or r[0] >= 0 or not caseng._hasvar(b, var):
                continue
            k = caseng.tostr(b)
            p = (-r[0], r[1])
            if k in keys:
                i = keys.index(k)
                if p[0] * dens[i][1][1] > dens[i][1][0] * p[1]:
                    dens[i] = [b, p]
            else:
                keys.append(k)
                dens.append([b, p])
    if not dens:
        return (E, _num(1))
    D = _prod([(caseng._pow(b, caseng._ratnode(p)), 1) for b, p in dens])
    return (_sum([(_prod([(t, 1), (D, 1)]), s) for t, s in raw]), D)

def make_subject(lhs, rhs, var='x'):
    # solve lhs = rhs for var, exactly, when it is linear after clearing
    E = _sum([(_S(lhs), 1), (_S(rhs), -1)])
    E, D = _cleardenom(E, var)
    E = caspoly.expand(E)
    r = linin(E, var)
    if r is None or r[0] == _num(0):
        inv = caseng.invert(_S(lhs), var, 'y') if _S(rhs) == ('v', 'y') else None
        return inv
    return _S(_prod([(_negt(r[1]), 1), (r[0], -1)]))

def rearrange(f, var='x', yname='y'):
    # y = f(x)  ->  x = ...
    return make_subject(_S(f), ('v', yname), var)

# ---- series ---------------------------------------------------------------

# ---- truncated power series (exact rational coefficients) ---------------
# Each series is a list of n+1 rationals (p, q).  Every operation is O(n^2), so
# a 12-term series of e^(sin x) costs a few hundred multiplications instead of
# twelve symbolic derivatives.

def _tz(n):
    return [caspoly.R0] * (n + 1)

def _tmul(a, b, n):
    out = _tz(n)
    i = 0
    while i <= n:
        if a[i][0]:
            j = 0
            while i + j <= n:
                if b[j][0]:
                    out[i + j] = caspoly.radd(out[i + j], caspoly.rmul(a[i], b[j]))
                j += 1
        i += 1
    return out

def _tdiv(a, b, n):
    if b[0][0] == 0:
        return None
    out = _tz(n)
    k = 0
    while k <= n:
        s = a[k]
        j = 1
        while j <= k:
            if b[j][0]:
                s = caspoly.rsub(s, caspoly.rmul(b[j], out[k - j]))
            j += 1
        out[k] = caspoly.rdiv(s, b[0])
        k += 1
    return out

def _tpow(a, al, n):
    # a^al, al rational (p, q); a0 = 0 only for whole al >= 0
    if al[1] == 1 and 0 <= al[0] <= 64:
        out = [caspoly.R1] + _tz(n)[1:]
        i = 0
        while i < al[0]:
            out = _tmul(out, a, n)
            i += 1
        return out
    if a[0][0] == 0:
        return None
    b0 = caseng._ratpow(a[0], al)
    r0 = None if b0 is None else caseng._ratval(b0)
    if r0 is None:
        return None
    out = [r0] + _tz(n)[1:]
    a1 = caspoly.radd(al, caspoly.R1)
    k = 1
    while k <= n:
        s = caspoly.R0
        j = 1
        while j <= k:
            if a[j][0]:
                c = caspoly.rsub(caspoly.rmul(a1, (j, 1)), (k, 1))
                s = caspoly.radd(s, caspoly.rmul(caspoly.rmul(c, a[j]), out[k - j]))
            j += 1
        out[k] = caspoly.rdiv(s, caspoly.rmul((k, 1), a[0]))
        k += 1
    return out

def _tder(a, n):
    return [caspoly.rmul((k + 1, 1), a[k + 1]) for k in range(n)] + [caspoly.R0]

def _tint(a, c0, n):
    return [c0] + [caspoly.rdiv(a[k - 1], (k, 1)) for k in range(1, n + 1)]

def _tsc(a, n, hyp):
    # (sin a, cos a) or (sinh a, cosh a) for a0 = 0
    s = _tz(n)
    c = [caspoly.R1] + _tz(n)[1:]
    k = 1
    while k <= n:
        ss = caspoly.R0
        cc = caspoly.R0
        j = 1
        while j <= k:
            if a[j][0]:
                ja = caspoly.rmul((j, 1), a[j])
                ss = caspoly.radd(ss, caspoly.rmul(ja, c[k - j]))
                cc = caspoly.radd(cc, caspoly.rmul(ja, s[k - j]))
            j += 1
        s[k] = caspoly.rdiv(ss, (k, 1))
        c[k] = caspoly.rdiv(cc, (k, 1)) if hyp else caspoly.rneg(caspoly.rdiv(cc, (k, 1)))
        k += 1
    return s, c

def _tconst(node):
    r = caspoly.ratof(node)
    if r is None and node[0] == 'n' and isinstance(node[1], float):
        r = caseng._fltrat(node[1])
    return r

def taylor(f, var, n):
    # Maclaurin coefficients c_0..c_n of f as rationals, or None
    try:
        return _tay(f, var, n)
    except (ZeroDivisionError, TypeError, ValueError):
        return None

def _tay(f, var, n):
    t = f[0]
    if not caseng._hasvar(f, var):
        r = _tconst(f)
        return None if r is None else [r] + _tz(n)[1:]
    if t == 'v':
        out = _tz(n)
        if n >= 1:
            out[1] = caspoly.R1
        return out
    if t == 'neg':
        a = _tay(f[1], var, n)
        return None if a is None else [caspoly.rneg(c) for c in a]
    if t in ('+', '-', '*', '/'):
        a = _tay(f[1], var, n)
        b = None if a is None else _tay(f[2], var, n)
        if b is None:
            return None
        if t == '+':
            return [caspoly.radd(a[i], b[i]) for i in range(n + 1)]
        if t == '-':
            return [caspoly.rsub(a[i], b[i]) for i in range(n + 1)]
        if t == '*':
            return _tmul(a, b, n)
        return _tdiv(a, b, n)
    if t == '^':
        if caseng._hasvar(f[2], var):
            return None
        al = _tconst(caseng.simplify(f[2]))
        a = None if al is None else _tay(f[1], var, n)
        return None if a is None else _tpow(a, al, n)
    if t not in ('exp', 'ln', 'sqrt', 'sin', 'cos', 'tan', 'sec', 'cosec', 'cot',
                 'sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth',
                 'asin', 'atan', 'asinh', 'atanh'):
        return None
    a = _tay(f[1], var, n)
    if a is None:
        return None
    if t == 'sqrt':
        return _tpow(a, (1, 2), n)
    if t == 'ln':
        if a[0] != caspoly.R1:
            return None
        d = _tdiv(_tder(a, n), a, n)
        return None if d is None else _tint(d, caspoly.R0, n)
    if a[0][0] != 0:
        return None
    if t == 'exp':
        b = [caspoly.R1] + _tz(n)[1:]
        k = 1
        while k <= n:
            s = caspoly.R0
            j = 1
            while j <= k:
                if a[j][0]:
                    s = caspoly.radd(s, caspoly.rmul(caspoly.rmul((j, 1), a[j]), b[k - j]))
                j += 1
            b[k] = caspoly.rdiv(s, (k, 1))
            k += 1
        return b
    if t in ('asin', 'atan', 'asinh', 'atanh'):
        sq = _tmul(a, a, n)
        sg = caspoly.R1 if t in ('atan', 'asinh') else (-1, 1)
        w = [caspoly.radd(caspoly.R1, caspoly.rmul(sg, sq[0]))] + \
            [caspoly.rmul(sg, sq[k]) for k in range(1, n + 1)]
        if t in ('asin', 'asinh'):
            w = _tpow(w, (-1, 2), n)
            d = None if w is None else _tmul(_tder(a, n), w, n)
        else:
            d = _tdiv(_tder(a, n), w, n)
        return None if d is None else _tint(d, caspoly.R0, n)
    hyp = t in ('sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth')
    s, c = _tsc(a, n, hyp)
    one = [caspoly.R1] + _tz(n)[1:]
    if t in ('sin', 'sinh'):
        return s
    if t in ('cos', 'cosh'):
        return c
    if t in ('tan', 'tanh'):
        return _tdiv(s, c, n)
    if t in ('sec', 'sech'):
        return _tdiv(one, c, n)
    return None

def maclaurin(f, var='x', n=4):
    if n > MAXTERMS:
        n = MAXTERMS
    items = []
    g = _S(f)
    co = taylor(g, var, n - 1) if n >= 1 else None
    if co is not None:
        k = 0
        while k < n:
            if co[k][0]:
                items.append((_prod([(caspoly.ratnode(co[k]), 1),
                                     (caseng._pow(('v', var), _num(k)), 1)]), 1))
            k += 1
        return _sum(items) if items else _num(0)
    k = 0
    fact = 1
    while k < n:
        if k:
            fact *= k
        try:
            c = _S(caseng.subst(g, var, _num(0)))
        except Exception:
            return None
        if caseng.vars_in(c):
            return None
        if c != _num(0):
            items.append((_prod([(c, 1), (_num(fact), -1),
                                 (caseng._pow(('v', var), _num(k)), 1)]), 1))
        if k + 1 < n:
            try:
                g = _S(caseng.diff(g, var))
            except Exception:
                return None
        k += 1
    if not items:
        return _num(0)
    return _sum(items)

def binom_series(a, n, terms=4, var='x'):
    # (1 + a x)^n to `terms` terms, n any rational
    if terms > MAXTERMS:
        terms = MAXTERMS
    rn = caseng._ratval(_S(n))
    if rn is None:
        return None
    items = []
    k = 0
    fact = 1
    coef = (1, 1)
    while k < terms:
        if k:
            fact *= k
            coef = caspoly.rmul(coef, caspoly.rsub(rn, (k - 1, 1)))
        c = caspoly.rdiv(coef, (fact, 1))
        if c is None:
            return None
        if not caspoly.rzero(c):
            items.append((_prod([(caspoly.ratnode(c), 1),
                                 (caseng._pow(_prod([(_S(a), 1), (('v', var), 1)]),
                                              _num(k)), 1)]), 1))
        k += 1
    if not items:
        return _num(0)
    return _sum(items)

def binom_validity(a):
    # |a x| < 1  ->  |x| < 1/|a|
    return _S(_prod([(caseng._sfn('abs', _S(a)), -1)]))

# ---- limits ---------------------------------------------------------------

def _value(f, var, a):
    try:
        v = _S(caseng.subst(_S(f), var, _S(a)))
    except Exception:
        return None
    if caseng.vars_in(v):
        return None
    try:
        caseng.evalf(v, 0.0)
    except Exception:
        return None
    return v

def limit(f, var='x', a=('n', 0), inf=0):
    g = _S(f)
    if inf:
        return _limit_inf(g, var, inf)
    guard = 0
    while guard < MAXHOP:
        guard += 1
        v = _value(g, var, a)
        if v is not None:
            return v
        num, den = _split(g)
        if den is None:
            return None
        nv = _value(num, var, a)
        dv = _value(den, var, a)
        if nv == _num(0) and dv == _num(0):
            try:
                num = _S(caseng.diff(num, var))
                den = _S(caseng.diff(den, var))
            except Exception:
                return None
            g = _S(_prod([(num, 1), (den, -1)]))
            continue
        return None
    return None

def _split(g):
    coef, fl, cxc, out = caseng._termparts([(g, 1)])
    top = []
    bot = []
    for b, e in out:
        r = caseng._ratval(e)
        if r is not None and r[0] < 0:
            bot.append([b, caseng._ratnode((-r[0], r[1]))])
        else:
            top.append([b, e])
    if not bot:
        return (g, None)
    return (caseng._termnode(coef, fl, cxc, top),
            caseng._termnode(R1, None, None, bot))

# f ~ c e^(a x) x^b as x -> +inf, as (c, a, b): c a tree, a and b floats
VAN = -1e9         # a = VAN: tends to 0 at an unknown rate (ln of something -> 1)

def _asy(f, var):
    t = f[0]
    if not caseng._hasvar(f, var):
        try:
            v = caseng.evalf(f, 0.0)
        except Exception:
            return None
        if isinstance(v, complex) or v != v:
            return None
        return None if v == 0 else (f, 0.0, 0.0)
    if t == 'v':
        return (_num(1), 0.0, 1.0)
    if t == 'neg':
        a = _asy(f[1], var)
        return None if a is None else (_S(('neg', a[0])), a[1], a[2])
    if t == '+' or t == '-':
        a = _asy(f[1], var)
        b = _asy(f[2], var)
        if a is None or b is None:
            return None
        if t == '-':
            b = (_S(('neg', b[0])), b[1], b[2])
        if abs(a[1] - b[1]) > 1e-12:
            return a if a[1] > b[1] else b
        if abs(a[2] - b[2]) > 1e-12:
            return a if a[2] > b[2] else b
        c = _S(('+', a[0], b[0]))
        if c == _num(0):
            return None
        return (c, a[1], a[2])
    if t == '*' or t == '/':
        a = _asy(f[1], var)
        b = _asy(f[2], var)
        if a is None or b is None:
            return None
        for p, q in ((a, b), (b, a)):
            # a vanishing log times anything but a constant: rate unknown
            if p[1] == VAN and (q[1] != 0.0 or q[2] != 0.0 or t == '/'):
                return None
        if t == '*':
            return (_S(('*', a[0], b[0])), a[1] + b[1], a[2] + b[2])
        return (_S(('/', a[0], b[0])), a[1] - b[1], a[2] - b[2])
    if t == 'sqrt':
        return _asy(('^', f[1], ('/', _num(1), _num(2))), var)
    if t == '^':
        if caseng._hasvar(f[2], var):
            if caseng._hasvar(f[1], var):
                return None
            return _asy(('exp', ('*', f[2], ('ln', f[1]))), var)
        try:
            p = caseng.evalf(f[2], 0.0)
        except Exception:
            return None
        a = _asy(f[1], var)
        if a is None or isinstance(p, complex):
            return None
        try:
            cv = caseng.evalf(a[0], 0.0)
        except Exception:
            return None
        if cv < 0 and p != int(p):
            return None
        return (_S(('^', a[0], f[2])), a[1] * p, a[2] * p)
    if t == 'ln':
        a = _asy(f[1], var)
        if a is None or a[1] != 0.0 or a[2] != 0.0:
            return None
        try:
            cv = caseng.evalf(a[0], 0.0)
        except Exception:
            return None
        if isinstance(cv, complex) or cv <= 0:
            return None
        if abs(cv - 1.0) < 1e-15:
            return (_num(1), VAN, 0.0)
        return (_S(('ln', a[0])), 0.0, 0.0)
    if t == 'exp':
        r = linin(_S(f[1]), var)
        if r is None:
            return None
        try:
            k = caseng.evalf(r[0], 0.0)
        except Exception:
            return None
        if isinstance(k, complex):
            return None
        return (_S(('exp', r[1])), k, 0.0)
    return None

def _limit_asy(g, var, sgn):
    if sgn < 0:
        g = caseng.subst(g, var, ('neg', ('v', var)))
    a = _asy(g, var)
    if a is None:
        return None
    c, al, be = a
    if al < -1e-12 or (abs(al) <= 1e-12 and be < -1e-12):
        return _num(0)
    if abs(al) <= 1e-12 and abs(be) <= 1e-12:
        return c
    try:
        cv = caseng.evalf(c, 0.0)
    except Exception:
        return None
    return _num(float('inf') if cv > 0 else float('-inf'))

def _limit_inf(g, var, sgn):
    r = _limit_inf0(g, var, sgn)
    if r is None:
        try:
            r = _limit_asy(g, var, sgn)
        except Exception:
            r = None
    return r

def _limit_inf0(g, var, sgn):
    vs = caseng.vars_in(g)
    if len(vs) == 1 and vs[0] == var:
        try:
            f = caspoly.polyfrac(g, var)
        except Exception:
            f = None
        if f is not None:
            N = caspoly.ptrim(list(f[0]))
            D = caspoly.ptrim(list(f[1]))
            if not N:
                return _num(0)
            if not D:
                return None
            dn = len(N) - 1
            dd = len(D) - 1
            if dn < dd:
                return _num(0)
            if dn == dd:
                return caspoly.ratnode(caspoly.rdiv(N[-1], D[-1]))
            lead = caspoly.rdiv(N[-1], D[-1])
            s = 1 if lead[0] > 0 else -1
            if sgn < 0 and (dn - dd) % 2:
                s = -s
            return _num(float('inf') if s > 0 else float('-inf'))
    return None
