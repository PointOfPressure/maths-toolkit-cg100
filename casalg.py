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
    finally:
        caseng.FOLD[0] = True
    return n

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

def maclaurin(f, var='x', n=4):
    if n > MAXTERMS:
        n = MAXTERMS
    items = []
    g = _S(f)
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

def _limit_inf(g, var, sgn):
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
