# OCR B (MEI) Further Maths H645, Statistics Major (Y422) and Minor (Y432): discrete
# random variables, binomial/Poisson/geometric, continuous random variables,
# Normal, bivariate data, chi-squared tests, inference, Wilcoxon, simulation.
# The Minor paper is a subset of the Major, so one module serves both.
import math
import casutil
import tables
import caseng
import cascalc

fmt = casutil.fmt
sf3 = casutil.sf3
w = casutil.w
warn = casutil.warn

# ---- small shared helpers ---------------------------------------------------

def _int(v, name):
    iv = int(v)
    if iv != v:
        raise ValueError(name + ' must be a whole number')
    return iv

def _pos(v, name):
    if v <= 0:
        raise ValueError(name + ' must be > 0')
    return v

def _whole(v, name, lo, hi):
    # a count the loops below have to stay inside
    v = _int(v, name)
    if v < lo or v > hi:
        raise ValueError(name + ' must be ' + fmt(lo) + ' to ' + fmt(hi))
    return v

def _mu(v, name):
    if v <= 0 or v > 500:
        raise ValueError(name + ' must be 0 to 500')
    return v

def _prob(v, name):
    if v < 0 or v > 1:
        raise ValueError(name + ' must be 0 to 1')
    return v

def _level(v, name):
    if v <= 0 or v >= 100:
        raise ValueError(name + ' must be 0 to 100')
    return v / 100.0

def _tail(v):
    t = _int(v, 'tail')
    if t != 1 and t != 2:
        raise ValueError('tail must be 1 or 2')
    return t

def _mean_sd(xs):
    n = len(xs)
    if n < 2:
        raise ValueError('need at least 2 values')
    tot = 0.0
    for v in xs:
        tot += v
    mean = tot / n
    ss = 0.0
    for v in xs:
        ss += (v - mean) * (v - mean)
    return (n, mean, math.sqrt(ss / (n - 1)))

def _sqrt(v):
    return math.sqrt(v) if v > 0 else 0.0

def _sign(v):
    # ' + 3' / ' - 3' for readable working lines
    return ' + ' + fmt(v) if v >= 0 else ' - ' + fmt(-v)

def _split(data, what):
    # alternating first, second values -> two lists
    if len(data) < 2 or len(data) % 2:
        raise ValueError('need ' + what + ' pairs')
    a = []
    b = []
    i = 0
    while i < len(data):
        a.append(data[i])
        b.append(data[i + 1])
        i += 2
    return (a, b)

def _pairs(data):
    # alternating value, probability
    xs, ps = _split(data, 'value,prob')
    for q in ps:
        _prob(q, 'probability')
    return (xs, ps)

def _sumcheck(ps, out):
    tot = 0.0
    for q in ps:
        tot += q
    if abs(tot - 1.0) > 1e-9:
        out.append(warn('sum P = ' + fmt(tot) + ', not 1'))
    else:
        out.append(w('sum P = 1 (check)'))
    return tot

def _moments(xs, ps):
    e1 = 0.0
    e2 = 0.0
    i = 0
    while i < len(xs):
        e1 += xs[i] * ps[i]
        e2 += xs[i] * xs[i] * ps[i]
        i += 1
    return (e1, e2, e2 - e1 * e1)

def _ev_var_lines(e1, e2, var, out):
    out.append('E(X) = ' + fmt(e1))
    out.append('Var(X) = ' + fmt(var))
    out.append('SD = ' + sf3(_sqrt(var)))
    out.append(w('E(X) = sum x*p = ' + fmt(e1)))
    out.append(w('E(X^2) = sum x^2*p = ' + fmt(e2)))
    out.append(w('Var = E(X^2)-E(X)^2 = ' + fmt(e2) + '-' +
                 fmt(e1 * e1) + ' = ' + fmt(var)))

def _sorted(xs):
    out = list(xs)
    out.sort()
    return out

# ---- distribution functions -------------------------------------------------

def _chi2_sf(x, k):
    # P(chi^2_k > x)
    if k < 1 or x <= 0.0:
        return 1.0
    if x > 1500.0:
        return 0.0
    if k % 2 == 0:
        q = math.exp(-x / 2.0)
        t = (x / 2.0) * q
        j = 4
    else:
        q = 2.0 * (1.0 - casutil.phi(math.sqrt(x)))
        t = math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0)
        j = 3
    while j <= k:
        q += t
        t = t * x / j
        j += 2
    if q < 0.0:
        return 0.0
    if q > 1.0:
        return 1.0
    return q

def _t_sf(t, v):
    # P(T_v > t)
    if v < 1:
        return 0.5
    a = t if t >= 0 else -t
    th = math.atan(a / math.sqrt(v))
    c = math.cos(th)
    s = math.sin(th)
    if v == 1:
        area = 2.0 * th / math.pi
    elif v % 2 == 0:
        term = 1.0
        tot = 1.0
        j = 2
        while j <= v - 2:
            term = term * (j - 1.0) / j * c * c
            tot += term
            j += 2
        area = s * tot
    else:
        term = c
        tot = c
        j = 3
        while j <= v - 2:
            term = term * (j - 1.0) / j * c * c
            tot += term
            j += 2
        area = 2.0 / math.pi * (th + s * tot)
    p = 0.5 * (1.0 - area)
    if t < 0:
        p = 1.0 - p
    if p < 0.0:
        return 0.0
    if p > 1.0:
        return 1.0
    return p

def _bisect_sf(sf, p):
    # x with sf(x) = p for a decreasing upper-tail function on x >= 0
    lo = 0.0
    hi = 4.0
    i = 0
    while i < 40 and sf(hi) > p:
        hi *= 2.0
        i += 1
    i = 0
    while i < 60:
        mid = 0.5 * (lo + hi)
        if sf(mid) > p:
            lo = mid
        else:
            hi = mid
        i += 1
    return 0.5 * (lo + hi)

def _tstar(df, p):
    # (critical value, came from the table)
    v = tables.t_crit(df, p)
    if v is not None:
        return (v, True)
    return (_bisect_sf(lambda x: _t_sf(x, df), p), False)

def _zstar(p):
    v = tables.z_crit(p)
    if v is not None:
        return (v, True)
    return (casutil.invphi(1.0 - p), False)

def _chistar(df, p):
    v = tables.chi_crit(df, p)
    if v is not None:
        return (v, True)
    return (_bisect_sf(lambda x: _chi2_sf(x, df), p), False)

def _pfmt(p):
    if p < 1e-4:
        return 'p < 0.0001'
    return 'p = ' + sf3(p)

def _verdict(rej, pct):
    if rej:
        return 'reject H0 at ' + fmt(pct) + '%'
    return 'do not reject H0 at ' + fmt(pct) + '%'

def _computed(tabled, out):
    if not tabled:
        out.append(warn('not in the table: computed'))

# =============================================================================
# D  Discrete random variables
# SR1 R2 R3 R4 R5 SR6 R7 R8 R9
# =============================================================================

def _median_drv(xs, ps):
    sx = []
    sp = []
    i = 0
    while i < len(xs):
        j = 0
        while j < len(sx) and sx[j] <= xs[i]:
            j += 1
        sx.insert(j, xs[i])
        sp.insert(j, ps[i])
        i += 1
    cum = 0.0
    j = 0
    while j < len(sx):
        cum += sp[j]
        if abs(cum - 0.5) < 1e-12 and j + 1 < len(sx):
            return 0.5 * (sx[j] + sx[j + 1])
        if cum > 0.5:
            return sx[j]
        j += 1
    return sx[len(sx) - 1]

def t_drv(data):
    xs, ps = _pairs(data)
    out = []
    e1, e2, var = _moments(xs, ps)
    out.append('E(X) = ' + fmt(e1))
    out.append('Var(X) = ' + fmt(var))
    out.append('SD = ' + sf3(_sqrt(var)))
    best = ps[0]
    for q in ps:
        if q > best:
            best = q
    modes = []
    i = 0
    while i < len(xs):
        if ps[i] >= best - 1e-12:
            modes.append(fmt(xs[i]))
        i += 1
    out.append('mode = ' + ', '.join(modes))
    out.append('median = ' + fmt(_median_drv(xs, ps)))
    out.append(w('E(X) = sum x*p = ' + fmt(e1)))
    out.append(w('E(X^2) = sum x^2*p = ' + fmt(e2)))
    out.append(w('Var = E(X^2)-E(X)^2 = ' + fmt(e2) + '-' +
                 fmt(e1 * e1) + ' = ' + fmt(var)))
    out.append(w('median: first x with cum P >= 0.5'))
    _sumcheck(ps, out)
    return out

def _range_vals(g, a, b):
    a = _int(a, 'a')
    b = _int(b, 'b')
    if b < a:
        raise ValueError('need b >= a')
    if b - a > 500:
        raise ValueError('at most 501 values')
    xs = []
    gs = []
    i = a
    while i <= b:
        v = casutil.real(casutil.ev(g, float(i)))
        if v < -1e-12:
            raise ValueError('P(X=' + fmt(i) + ') is negative')
        xs.append(i)
        gs.append(v)
        i += 1
    return (xs, gs)

def _shown(xs, ps, out):
    shown = []
    i = 0
    while i < len(xs) and i < 5:
        shown.append('P(' + fmt(xs[i]) + ')=' + sf3(ps[i]))
        i += 1
    out.append(w(' '.join(shown)))

def t_drvf(p, a, b):
    xs, ps = _range_vals(p, a, b)
    out = []
    e1, e2, var = _moments(xs, ps)
    _ev_var_lines(e1, e2, var, out)
    tot = _sumcheck(ps, out)
    _shown(xs, ps, out)
    out.insert(0, 'sum P = ' + fmt(tot))
    return out

def t_drvk(g, a, b):
    xs, gs = _range_vals(g, a, b)
    tot = 0.0
    for v in gs:
        tot += v
    if tot <= 0:
        raise ValueError('sum of g(x) is 0')
    k = 1.0 / tot
    ps = [k * v for v in gs]
    e1, e2, var = _moments(xs, ps)
    out = ['k = ' + fmt(k)]
    _ev_var_lines(e1, e2, var, out)
    out.append(w('P(X=x) = k*g(x), sum P = 1'))
    out.append(w('k * ' + fmt(tot) + ' = 1 so k = ' + fmt(k)))
    _shown(xs, ps, out)
    return out

def t_egx(g, data):
    xs, ps = _pairs(data)
    gs = []
    i = 0
    while i < len(xs):
        gs.append(casutil.real(casutil.ev(g, float(xs[i]))))
        i += 1
    e1, e2, var = _moments(gs, ps)
    out = ['E(g(X)) = ' + fmt(e1),
           'E(g(X)^2) = ' + fmt(e2),
           'Var(g(X)) = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var)),
           w('E(g(X)) = sum g(x)*p = ' + fmt(e1)),
           w('Var = E(g^2)-E(g)^2 = ' + fmt(var))]
    shown = []
    i = 0
    while i < len(xs) and i < 5:
        shown.append('g(' + fmt(xs[i]) + ')=' + sf3(gs[i]))
        i += 1
    out.append(w(' '.join(shown)))
    _sumcheck(ps, out)
    return out

def t_linear(a, b, mean, var):
    if var < 0:
        raise ValueError('Var(X) must be >= 0')
    ey = a + b * float(mean)
    vy = b * b * float(var)
    return ['E(a+bX) = ' + fmt(ey),
            'Var(a+bX) = ' + fmt(vy),
            'SD(a+bX) = ' + sf3(_sqrt(vy)),
            w('E(a+bX) = a+bE(X) = ' + fmt(a) + _sign(b) + '*' +
              fmt(mean)),
            w('Var(a+bX) = b^2Var(X) = ' + fmt(b * b) + '*' + fmt(var)),
            w('a shifts the mean, never the variance')]

def t_sumxy(mx, vx, my, vy):
    if vx < 0 or vy < 0:
        raise ValueError('variances must be >= 0')
    return ['E(X+Y) = ' + fmt(mx + my),
            'E(X-Y) = ' + fmt(mx - my),
            'Var(X+Y) = ' + fmt(vx + vy),
            'Var(X-Y) = ' + fmt(vx + vy),
            'SD(X+-Y) = ' + sf3(_sqrt(vx + vy)),
            w('E(X+-Y) = E(X)+-E(Y) always'),
            w('Var needs X and Y independent'),
            w('Var(X-Y) adds the variances too'),
            w('Var = ' + fmt(vx) + ' + ' + fmt(vy) + ' = ' + fmt(vx + vy))]

def t_dunif(a, b, c, d):
    a = _int(a, 'a')
    b = _int(b, 'b')
    if b < a:
        raise ValueError('need b >= a')
    n = b - a + 1
    e1 = (a + b) / 2.0
    var = (n * n - 1) / 12.0
    out = ['P(X=x) = 1/n = ' + fmt(1.0 / n),
           'E(X) = (a+b)/2 = ' + fmt(e1),
           'Var(X) = (n^2-1)/12 = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var))]
    if c is not None and d is not None:
        lo = int(math.ceil(c))
        hi = int(math.floor(d))
        if lo < a:
            lo = a
        if hi > b:
            hi = b
        k = hi - lo + 1 if hi >= lo else 0
        out.append('P(c<=X<=d) = ' + fmt(k / float(n)))
        out.append(w(fmt(k) + ' of the ' + fmt(n) + ' values lie in [c, d]'))
    out.append(w('X uniform on ' + fmt(a) + ', ..., ' + fmt(b) +
                 ': n = ' + fmt(n)))
    out.append(w('same spread as 1..n shifted by ' + fmt(a - 1)))
    out.append(w('1..n: E(X^2) = (n+1)(2n+1)/6'))
    out.append(w('Var = (n+1)(2n+1)/6 - (n+1)^2/4'))
    out.append(w('    = (n^2-1)/12'))
    return out

# =============================================================================
# B  Binomial and Poisson
# R10 SR11 R12 R13 R14 R15
# =============================================================================

def _pois_ge(mu, k):
    if k <= 0:
        return 1.0
    v = 1.0 - casutil.poisson_cdf(mu, k - 1)
    return 0.0 if v < 0.0 else v

def _pois_cum(mu, kmax):
    # P(X<=k) for k = 0 .. kmax, built in one pass
    r = math.exp(-mu)
    c = r
    out = [c]
    i = 1
    while i <= kmax:
        r = r * mu / i
        c += r
        out.append(c if c < 1.0 else 1.0)
        i += 1
    return out

def _pois_lim(mu):
    return int(mu + 12.0 * math.sqrt(mu) + 60)

def t_pois(mu, k):
    _mu(mu, 'mu')
    k = _whole(k, 'k', 0, 1000)
    pk = casutil.poisson_pmf(mu, k)
    cd = casutil.poisson_cdf(mu, k)
    return ['P(X=k) = ' + sf3(pk),
            'P(X<=k) = ' + sf3(cd),
            'P(X>=k) = ' + sf3(_pois_ge(mu, k)),
            'mean = var = ' + sf3(mu),
            'SD = ' + sf3(math.sqrt(mu)),
            w('P(X=k) = e^-mu*mu^k/k! = ' + sf3(pk)),
            w('P(X>k) = 1-P(X<=k) = ' + sf3(1.0 - cd)),
            w('Po: mean = variance = mu = ' + sf3(mu))]

def t_poisrange(mu, a, b):
    _mu(mu, 'mu')
    a = _int(a, 'a')
    b = _whole(b, 'b', 0, 1000)
    if b < a:
        raise ValueError('need b >= a')
    if a < 0:
        a = 0
    lo = casutil.poisson_cdf(mu, a - 1) if a > 0 else 0.0
    hi = casutil.poisson_cdf(mu, b)
    p = hi - lo
    if p < 0.0:
        p = 0.0
    return ['P(a<=X<=b) = ' + sf3(p),
            'P(X<a) = ' + sf3(lo),
            'P(X>b) = ' + sf3(1.0 - hi),
            w('P(a<=X<=b) = P(X<=b)-P(X<=a-1)'),
            w('= ' + sf3(hi) + ' - ' + sf3(lo) + ' = ' + sf3(p))]

def t_poisinv(mu, p):
    _mu(mu, 'mu')
    if p <= 0 or p >= 1:
        raise ValueError('p must be 0 to 1')
    lim = _pois_lim(mu)
    cum = _pois_cum(mu, lim)
    k = 0
    while k < lim and cum[k] < p:
        k += 1
    below = cum[k - 1] if k > 0 else 0.0
    return ['k = ' + fmt(k),
            'P(X<=k) = ' + sf3(cum[k]),
            'P(X<=k-1) = ' + sf3(below),
            w('least k with P(X<=k) >= ' + sf3(p)),
            w('mu = ' + sf3(mu) + ', P(X>=k) = ' + sf3(1.0 - below))]

def t_poissum(k, mus):
    k = _whole(k, 'k', 0, 1000)
    tot = 0.0
    for v in mus:
        _pos(v, 'each mean')
        tot += v
    _mu(tot, 'total mu')
    return ['Y = sum Xi ~ Po(' + sf3(tot) + ')',
            'P(Y=k) = ' + sf3(casutil.poisson_pmf(tot, k)),
            'P(Y<=k) = ' + sf3(casutil.poisson_cdf(tot, k)),
            'P(Y>=k) = ' + sf3(_pois_ge(tot, k)),
            'SD = ' + sf3(math.sqrt(tot)),
            w('independent Po sum: mu = sum mu_i'),
            w('mu = ' + ' + '.join([sf3(v) for v in mus]) +
              ' = ' + sf3(tot))]

def _bin_n(n):
    return _whole(n, 'n', 1, 1000)

def t_binom(n, p, k):
    n = _bin_n(n)
    _prob(p, 'p')
    k = _whole(k, 'k', 0, n)
    pk = casutil.binom_pmf(n, p, k)
    cd = casutil.binom_cdf(n, p, k)
    ge = 1.0 - cd + pk
    return ['P(X=k) = ' + sf3(pk),
            'P(X<=k) = ' + sf3(cd),
            'P(X>=k) = ' + sf3(ge if ge > 0 else 0.0),
            'mean np = ' + sf3(n * p),
            'var np(1-p) = ' + sf3(n * p * (1.0 - p)),
            w('P(X=k) = nCk p^k (1-p)^(n-k)'),
            w('fixed n, independent trials, constant p')]

def t_papprox(n, p, k):
    n = _bin_n(n)
    _prob(p, 'p')
    k = _whole(k, 'k', 0, n)
    mu = n * p
    if mu <= 0:
        raise ValueError('np must be > 0')
    _mu(mu, 'np')
    bk = casutil.binom_pmf(n, p, k)
    bc = casutil.binom_cdf(n, p, k)
    pk = casutil.poisson_pmf(mu, k)
    pc = casutil.poisson_cdf(mu, k)
    out = ['Po(' + sf3(mu) + ') approximates B',
           'Po P(X=k) = ' + sf3(pk),
           'Po P(X<=k) = ' + sf3(pc),
           'B  P(X=k) = ' + sf3(bk),
           'B  P(X<=k) = ' + sf3(bc)]
    if n < 50 or p > 0.1:
        out.append(warn('n not large or p not small:'))
        out.append(warn('the approximation may be poor'))
    out.append(w('mu = np = ' + fmt(n) + '*' + sf3(p) + ' = ' + sf3(mu)))
    out.append(w('B var np(1-p) = ' + sf3(mu * (1.0 - p)) +
                 ', Po var = ' + sf3(mu)))
    out.append(w('error in P(X<=k) = ' + sf3(pc - bc)))
    return out

def t_poischeck(data):
    n, mean, s = _mean_sd(data)
    var = s * s
    if mean <= 0:
        raise ValueError('mean must be > 0')
    r = var / mean
    out = ['mean = ' + sf3(mean),
           'variance = ' + sf3(var),
           'var/mean = ' + sf3(r)]
    if abs(r - 1.0) <= 0.5:
        out.append('var near mean: Po plausible')
    else:
        out.append('var far from mean: not Po')
    out.append(w('n = ' + fmt(n) + ', variance uses n-1'))
    out.append(w('Po(mu) has mean = variance = mu'))
    out.append(w('so mu estimate = xbar = ' + sf3(mean)))
    out.append(w('also needs events random, independent'))
    return out

# =============================================================================
# G  Geometric distribution
# SR16 R17 R18
# =============================================================================

def _geo_p(p):
    if p <= 0 or p > 1:
        raise ValueError('p must be > 0 and <= 1')
    return p

def _geo_mv(p, out):
    q = 1.0 - p
    out.append('mean 1/p = ' + fmt(1.0 / p))
    out.append('var (1-p)/p^2 = ' + fmt(q / (p * p)))

def t_geom(p, r):
    _geo_p(p)
    r = _whole(r, 'r', 1, 100000)
    q = 1.0 - p
    out = ['P(X=r) = ' + fmt(q ** (r - 1) * p),
           'P(X<=r) = ' + fmt(1.0 - q ** r),
           'P(X>r) = ' + fmt(q ** r)]
    _geo_mv(p, out)
    out.append(w('X = trial of the first success'))
    out.append(w('P(X=r) = (1-p)^(r-1) p'))
    out.append(w('P(X>r) = (1-p)^r: first r all fail'))
    return out

def t_georange(p, a, b):
    _geo_p(p)
    a = _whole(a, 'a', 1, 100000)
    b = _whole(b, 'b', 1, 100000)
    if b < a:
        raise ValueError('need b >= a')
    q = 1.0 - p
    v = q ** (a - 1) - q ** b
    out = ['P(a<=X<=b) = ' + fmt(v)]
    _geo_mv(p, out)
    out.append(w('= P(X>a-1) - P(X>b)'))
    out.append(w('= (1-p)^(a-1) - (1-p)^b'))
    return out

def t_geoinv(p, prob):
    _geo_p(p)
    if prob <= 0 or prob >= 1:
        raise ValueError('prob must be 0 to 1')
    q = 1.0 - p
    if q <= 0:
        r = 1
    else:
        r = int(math.ceil(math.log(1.0 - prob) / math.log(q) - 1e-9))
        if r < 1:
            r = 1
        while 1.0 - q ** r < prob:
            r += 1
        while r > 1 and 1.0 - q ** (r - 1) >= prob:
            r -= 1
    return ['r = ' + fmt(r),
            'P(X<=r) = ' + sf3(1.0 - q ** r),
            'P(X<=r-1) = ' + sf3(1.0 - q ** (r - 1)),
            w('least r with 1-(1-p)^r >= ' + sf3(prob)),
            w('(1-p)^r <= 1-prob: r >= ln(1-prob)/ln(1-p)')]

# =============================================================================
# C  Continuous random variables
# SR19 R20 R21 SR22 R23 R24 R25 R26
# =============================================================================

def _prep(f):
    try:
        return cascalc.integ(f, 'x')
    except Exception:
        return None

def _defint(f, F, a, b):
    # (value, exact) - exact when an antiderivative was usable
    if b == a:
        return (0.0, True)
    if F is not None:
        hi = casutil.evx(F, b)
        lo = casutil.evx(F, a)
        if hi is not None and lo is not None:
            return (hi - lo, True)
    v = cascalc.defint(f, a, b, False, 200, 'x')
    if v is None:
        return (None, False)
    return (v, False)

def _piece(f, lo, hi):
    if hi <= lo:
        raise ValueError('need upper > lower')
    return (f, float(lo), float(hi), _prep(f))

def _xpow(f, m):
    if m == 0:
        return f
    if m == 1:
        return ('*', ('v', 'x'), f)
    return ('*', ('^', ('v', 'x'), ('n', m)), f)

def _moment(pieces, m):
    tot = 0.0
    exact = True
    for pc in pieces:
        g = _xpow(pc[0], m)
        G = pc[3] if m == 0 else _prep(g)
        v, ex = _defint(g, G, pc[1], pc[2])
        if v is None:
            return (None, False)
        tot += v
        if not ex:
            exact = False
    return (tot, exact)

def _fval(pieces, x):
    for pc in pieces:
        if pc[1] <= x <= pc[2]:
            return casutil.evx(pc[0], x)
    return 0.0

def _fmin(pieces, n):
    lo = None
    lox = 0.0
    for pc in pieces:
        i = 0
        while i <= n:
            x = pc[1] + (pc[2] - pc[1]) * i / float(n)
            v = _fval(pieces, x)
            if v is not None and (lo is None or v < lo):
                lo = v
                lox = x
            i += 1
    return (lo, lox)

def _cdfat(pieces, t):
    tot = 0.0
    for pc in pieces:
        if t <= pc[1]:
            break
        u = pc[2] if t > pc[2] else t
        v, ex = _defint(pc[0], pc[3], pc[1], u)
        if v is None:
            return None
        tot += v
    return tot

def _root(F, p, lo, hi):
    # x in [lo, hi] with F(x) = p for an increasing F (a function of x)
    i = 0
    while i < 50:
        mid = 0.5 * (lo + hi)
        v = F(mid)
        if v is None:
            return None
        if v < p:
            lo = mid
        else:
            hi = mid
        i += 1
    return 0.5 * (lo + hi)

def _quantile(pieces, p):
    return _root(lambda t: _cdfat(pieces, t), p, pieces[0][1],
                 pieces[len(pieces) - 1][2])

def _validity(pieces):
    # answer line, then the caveats and the working behind it
    tot, exact = _moment(pieces, 0)
    if tot is None:
        raise ValueError('cannot integrate f(x)')
    out = []
    ok = True
    if abs(tot - 1.0) > 5e-4:
        ok = False
        out.append(warn('not a pdf: int f = ' + sf3(tot)))
    mn, mx = _fmin(pieces, 120)
    if mn is None:
        ok = False
        out.append(warn('f(x) does not evaluate here'))
    elif mn < -1e-9:
        ok = False
        out.append(warn('not a pdf: f(' + sf3(mx) + ') = ' + sf3(mn)))
    out.append(w('int f dx = ' + fmt(tot) +
                 (' (exact)' if exact else ' (Simpson)')))
    out.insert(0, 'valid pdf: yes' if ok else 'valid pdf: no')
    return out

def _ev_lines(pieces, out):
    e1, x1 = _moment(pieces, 1)
    e2, x2 = _moment(pieces, 2)
    if e1 is None or e2 is None:
        raise ValueError('cannot integrate x*f(x)')
    var = e2 - e1 * e1
    out.append('E(X) = ' + fmt(e1))
    out.append('E(X^2) = ' + fmt(e2))
    out.append('Var(X) = ' + fmt(var))
    out.append('SD = ' + sf3(_sqrt(var)))
    return (e1, e2, var)

def t_pdf(f, a, b):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    out = []
    e1, e2, var = _ev_lines(pieces, out)
    out.extend(chk)
    out.append(w('E(X) = int x f(x) dx = ' + fmt(e1)))
    out.append(w('E(X^2) = int x^2 f(x) dx = ' + fmt(e2)))
    out.append(w('Var = E(X^2)-E(X)^2 = ' + fmt(var)))
    import plot
    plot.run([f], float(a), float(b), 'y', 'pdf f(x)')
    return out

def t_pdfq(f, a, b):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    q1 = _quantile(pieces, 0.25)
    md = _quantile(pieces, 0.5)
    q3 = _quantile(pieces, 0.75)
    if q1 is None or md is None or q3 is None:
        raise ValueError('cannot integrate f(x)')
    out = ['median m = ' + sf3(md),
           'Q1 = ' + sf3(q1),
           'Q3 = ' + sf3(q3),
           'IQR = ' + sf3(q3 - q1)]
    out.extend(chk)
    out.append(w('m solves int_a^m f dx = 0.5'))
    out.append(w('F(m) = ' + sf3(_cdfat(pieces, md))))
    out.append(w('F(Q1) = 0.25, F(Q3) = 0.75'))
    return out

def t_pdfmode(f, a, b):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    lo = float(a)
    hi = float(b)
    best = None
    bx = lo
    step = 200
    k = 0
    while k < 4:
        i = 0
        while i <= step:
            x = lo + (hi - lo) * i / float(step)
            v = _fval(pieces, x)
            if v is not None and (best is None or v > best):
                best = v
                bx = x
            i += 1
        span = (hi - lo) / float(step)
        lo = bx - span
        hi = bx + span
        if lo < a:
            lo = float(a)
        if hi > b:
            hi = float(b)
        k += 1
    if best is None:
        raise ValueError('cannot evaluate f(x)')
    out = ['mode = ' + sf3(bx), 'f(mode) = ' + sf3(best)]
    if abs(bx - a) < 1e-6 or abs(bx - b) < 1e-6:
        out.append(warn('mode is at an end of the range'))
    out.extend(chk)
    out.append(w('mode maximises f(x) on [' + fmt(a) + ', ' + fmt(b) + ']'))
    out.append(w('solve f\'(x) = 0 for the exact value'))
    return out

def t_cdf(f, a, b, t):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    out = []
    F = pieces[0][3]
    if F is not None:
        base = casutil.evx(F, float(a))
        if base is not None:
            expr = cascalc.tidy(('-', F, ('n', base)))
            out.append(w('F(x) = ' + caseng.tostr(cascalc.tidy(expr))))
    else:
        out.append(warn('no symbolic F(x): numeric only'))
    tv = float(t)
    if tv <= a:
        v = 0.0
    elif tv >= b:
        v = 1.0
    else:
        v = _cdfat(pieces, tv)
    if v is None:
        raise ValueError('cannot integrate f(x)')
    out.insert(0, 'F(' + sf3(t) + ') = ' + sf3(v))
    out.insert(1, 'P(X>t) = ' + sf3(1.0 - v))
    out.extend(chk)
    out.append(w('F(x) = int_a^x f(t) dt, F(a)=0, F(b)=1'))
    out.append(w('F(x) = 0 below a and 1 above b'))
    return out

def t_pdfp(f, a, b, c, d):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    if d < c:
        raise ValueError('need d >= c')
    lo = float(c)
    hi = float(d)
    if lo < a:
        lo = float(a)
    if hi > b:
        hi = float(b)
    if hi < lo:
        p = 0.0
    else:
        p, ex = _defint(f, pieces[0][3], lo, hi)
    if p is None:
        raise ValueError('cannot integrate f(x)')
    out = ['P(c<X<d) = ' + sf3(p)]
    out.extend(chk)
    out.append(w('P = int_' + sf3(lo) + '^' + sf3(hi) + ' f dx = ' + fmt(p)))
    out.append(w('range clipped to [' + sf3(a) + ', ' + sf3(b) + ']'))
    out.append(w('P(X=c) = 0 for a continuous X'))
    return out

def t_pdfg(g, f, a, b):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    gf = ('*', g, f)
    e1, ex1 = _defint(gf, _prep(gf), float(a), float(b))
    g2f = ('*', ('^', g, ('n', 2)), f)
    e2, ex2 = _defint(g2f, _prep(g2f), float(a), float(b))
    if e1 is None or e2 is None:
        raise ValueError('cannot integrate g(x)f(x)')
    var = e2 - e1 * e1
    out = ['E(g(X)) = ' + fmt(e1),
           'E(g(X)^2) = ' + fmt(e2),
           'Var(g(X)) = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var))]
    out.extend(chk)
    out.append(w('E(g(X)) = int g(x)f(x) dx = ' + fmt(e1)))
    out.append(w('Var = E(g^2)-E(g)^2 = ' + fmt(var)))
    return out

def t_pdfpw(f, g, a, b, c):
    pieces = [_piece(f, a, b), _piece(g, b, c)]
    chk = _validity(pieces)
    e1, x1 = _moment(pieces, 1)
    e2, x2 = _moment(pieces, 2)
    if e1 is None or e2 is None:
        raise ValueError('cannot integrate x*f(x)')
    var = e2 - e1 * e1
    md = _quantile(pieces, 0.5)
    out = ['E(X) = ' + fmt(e1),
           'Var(X) = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var))]
    if md is not None:
        out.append('median = ' + sf3(md))
    out.extend(chk)
    p1, q1 = _moment([pieces[0]], 0)
    p2, q2 = _moment([pieces[1]], 0)
    out.append(w('P(' + sf3(a) + '<X<' + sf3(b) + ') = ' + fmt(p1)))
    out.append(w('P(' + sf3(b) + '<X<' + sf3(c) + ') = ' + fmt(p2)))
    out.append(w('E(X) = sum of int x f over each piece'))
    return out

def _cdf_fn(F, a, b):
    def val(x):
        if x <= a:
            return 0.0
        if x >= b:
            return 1.0
        return casutil.evx(F, x)
    return val

def _cdf_checks(F, a, b, out):
    fa = casutil.evx(F, float(a))
    fb = casutil.evx(F, float(b))
    if fa is None or fb is None:
        raise ValueError('cannot evaluate F at a or b')
    ok = True
    if abs(fa) > 5e-4:
        ok = False
        out.append(warn('F(a) = ' + sf3(fa) + ', should be 0'))
    if abs(fb - 1.0) > 5e-4:
        ok = False
        out.append(warn('F(b) = ' + sf3(fb) + ', should be 1'))
    prev = fa
    i = 1
    while i <= 100:
        v = casutil.evx(F, a + (b - a) * i / 100.0)
        if v is None:
            raise ValueError('F does not evaluate on [a, b]')
        if v < prev - 1e-9:
            ok = False
            out.append(warn('F decreases: not a cdf'))
            break
        prev = v
        i += 1
    out.append(w('F(a) = ' + sf3(fa) + ', F(b) = ' + sf3(fb)))
    return ok

def t_pdffromcdf(F, a, b):
    if b <= a:
        raise ValueError('need b > a')
    try:
        f = cascalc.tidy(caseng.diff(F))
    except Exception:
        raise ValueError('cannot differentiate F(x)')
    out = ['f(x) = ' + caseng.tostr(f),
           'for ' + fmt(a) + ' <= x <= ' + fmt(b) + ', else 0']
    if _cdf_checks(F, a, b, out):
        _ev_lines([_piece(f, a, b)], out)
    else:
        out.append(warn('not a cdf on [a, b]: no E(X)'))
    out.append(w('f(x) = dF/dx'))
    out.append(w('E(X) = int x f(x) dx over [a, b]'))
    return out

def t_cdfq(F, a, b, p):
    if b <= a:
        raise ValueError('need b > a')
    out = []
    _cdf_checks(F, a, b, out)
    val = _cdf_fn(F, float(a), float(b))
    q1 = _root(val, 0.25, float(a), float(b))
    md = _root(val, 0.5, float(a), float(b))
    q3 = _root(val, 0.75, float(a), float(b))
    if q1 is None or md is None or q3 is None:
        raise ValueError('F does not evaluate on [a, b]')
    head = ['median = ' + sf3(md), 'Q1 = ' + sf3(q1), 'Q3 = ' + sf3(q3),
            'IQR = ' + sf3(q3 - q1)]
    if p is not None:
        if p <= 0 or p >= 1:
            raise ValueError('p must be 0 to 1')
        xp = _root(val, p, float(a), float(b))
        if xp is not None:
            head.append('F(x) = p at x = ' + sf3(xp))
    out = head + out
    out.append(w('solve F(m) = 0.5, F(Q1) = 0.25,'))
    out.append(w('F(Q3) = 0.75 on [' + fmt(a) + ', ' + fmt(b) + ']'))
    return out

def t_rect(a, b, c, d):
    if b <= a:
        raise ValueError('need b > a')
    e1 = (a + b) / 2.0
    var = (b - a) * (b - a) / 12.0
    out = ['f(x) = 1/(b-a) = ' + fmt(1.0 / (b - a)),
           'E(X) = (a+b)/2 = ' + fmt(e1),
           'Var(X) = (b-a)^2/12 = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var))]
    if c is not None and d is not None:
        lo = c if c > a else a
        hi = d if d < b else b
        p = (hi - lo) / (b - a) if hi > lo else 0.0
        out.append('P(c<X<d) = ' + fmt(p))
        out.append(w('P = (overlap)/(b-a) = ' + fmt(hi - lo if hi > lo
                                                     else 0) + '/' +
                     fmt(b - a)))
    out.append(w('E(X) = int x/(b-a) dx = (a+b)/2'))
    out.append(w('E(X^2) = (b^3-a^3)/3(b-a)'))
    out.append(w('Var = E(X^2)-E(X)^2 = (b-a)^2/12'))
    return out

# =============================================================================
# N  Normal distribution
# SR28 R27 R29 R30 R31 R32
# =============================================================================

def _nprob(mu, sd, a, b, out):
    za = (a - mu) / sd
    zb = (b - mu) / sd
    pa = casutil.phi(za)
    pb = casutil.phi(zb)
    out.append('P(a<X<b) = ' + sf3(pb - pa))
    out.append('P(X<a) = ' + sf3(pa))
    out.append('P(X>b) = ' + sf3(1.0 - pb))
    out.append(w('z(a) = (a-mu)/sigma = ' + sf3(za)))
    out.append(w('z(b) = (b-mu)/sigma = ' + sf3(zb)))
    out.append(w('P = Phi(z(b)) - Phi(z(a))'))

def t_normal(mu, sigma, a, b):
    _pos(sigma, 'sigma')
    if b < a:
        raise ValueError('need b >= a')
    out = []
    _nprob(mu, sigma, a, b, out)
    out.append(w('X ~ N(' + sf3(mu) + ', ' + sf3(sigma * sigma) + ')'))
    return out

def t_ninv(mu, sigma, p):
    _pos(sigma, 'sigma')
    if p <= 0 or p >= 1:
        raise ValueError('p must be 0 to 1')
    z = casutil.invphi(p)
    return ['x = ' + sf3(mu + z * sigma),
            'z = ' + sf3(z),
            w('P(X<x) = ' + sf3(p)),
            w('x = mu + z*sigma = ' + sf3(mu) + ' + ' + sf3(z) + '*' +
              sf3(sigma))]

def t_nfit(data):
    n, mean, s = _mean_sd(data)
    if s <= 0:
        raise ValueError('all values equal')
    in1 = 0
    in2 = 0
    for v in data:
        d = abs(v - mean)
        if d <= s:
            in1 += 1
        if d <= 2.0 * s:
            in2 += 1
    srt = _sorted(data)
    med = srt[n // 2] if n % 2 else 0.5 * (srt[n // 2 - 1] + srt[n // 2])
    return ['mu est = xbar = ' + sf3(mean),
            'sigma est = s = ' + sf3(s),
            'within 1 s: ' + sf3(100.0 * in1 / n) + '% (68.3%)',
            'within 2 s: ' + sf3(100.0 * in2 / n) + '% (95.4%)',
            w('n = ' + fmt(n) + ', s uses divisor n-1'),
            w('median = ' + sf3(med) + ' vs mean ' + sf3(mean)),
            w('Normal: symmetric, median near mean'),
            w('X ~ N(' + sf3(mean) + ', ' + sf3(s * s) + ') approx')]

def t_nsample(a, b, data):
    n, mean, s = _mean_sd(data)
    if s <= 0:
        raise ValueError('all values equal')
    if b < a:
        raise ValueError('need b >= a')
    out = []
    _nprob(mean, s, a, b, out)
    out.append(w('mu, sigma estimated by xbar = ' + sf3(mean)))
    out.append(w('and s = ' + sf3(s) + ' (n = ' + fmt(n) + ')'))
    if n < 30:
        out.append(warn('small sample: estimates are rough'))
    return out

def t_lincomb(a, b, c, mx, vx, my, vy, wv):
    # wv is the field k: P(W < k)
    if vx < 0 or vy < 0:
        raise ValueError('variances must be >= 0')
    ew = a * float(mx) + b * float(my) + c
    vw = a * a * float(vx) + b * b * float(vy)
    sw = _sqrt(vw)
    out = ['E(W) = ' + fmt(ew),
           'Var(W) = ' + fmt(vw),
           'SD(W) = ' + sf3(sw)]
    if wv is not None:
        if sw <= 0:
            out.append(warn('Var(W) = 0: W is constant'))
        else:
            z = (wv - ew) / sw
            out.append('P(W<k) = ' + sf3(casutil.phi(z)))
            out.append('P(W>k) = ' + sf3(1.0 - casutil.phi(z)))
            out.append(w('z = (k-E(W))/SD(W) = ' + sf3(z)))
    out.append(w('W = aX + bY + c, X and Y independent'))
    out.append(w('E(W) = aE(X)+bE(Y)+c'))
    out.append(w('Var(W) = a^2Var(X)+b^2Var(Y)'))
    out.append(w('X, Y Normal so W is Normal'))
    return out

def t_nsum(mu, var, n, wv):
    if var < 0:
        raise ValueError('Var(X) must be >= 0')
    n = _whole(n, 'n', 1, 1000000)
    vs = n * n * var
    va = n * var
    out = ['E(nX) = E(sum) = ' + fmt(n * mu),
           'Var(nX) = n^2Var(X) = ' + fmt(vs),
           'Var(X1+..+Xn) = ' + fmt(va),
           'Var(Xbar) = Var(X)/n = ' + fmt(var / n)]
    if wv is not None and var > 0:
        z1 = (wv - n * mu) / math.sqrt(vs)
        z2 = (wv - n * mu) / math.sqrt(va)
        out.append('P(nX<k) = ' + sf3(casutil.phi(z1)))
        out.append('P(sum<k) = ' + sf3(casutil.phi(z2)))
    out.append(w('nX: one value scaled by n'))
    out.append(w('X1+..+Xn: n independent values'))
    out.append(w('same mean, sum has smaller variance'))
    return out

def t_nplot(data):
    n = len(data)
    if n < 3:
        raise ValueError('need at least 3 values')
    srt = _sorted(data)
    zs = []
    i = 0
    while i < n:
        zs.append(casutil.invphi((i + 0.5) / n))
        i += 1
    mz = 0.0
    mx = 0.0
    for v in zs:
        mz += v
    for v in srt:
        mx += v
    mz /= n
    mx /= n
    szz = 0.0
    sxx = 0.0
    szx = 0.0
    i = 0
    while i < n:
        szz += (zs[i] - mz) * (zs[i] - mz)
        sxx += (srt[i] - mx) * (srt[i] - mx)
        szx += (zs[i] - mz) * (srt[i] - mx)
        i += 1
    if sxx <= 0:
        raise ValueError('all values equal')
    r = szx / math.sqrt(szz * sxx)
    b = szx / szz
    a = mx - b * mz
    pts = []
    i = 0
    while i < n:
        pts.append((zs[i], srt[i]))
        i += 1
    import plot
    plot.run(pts, 0.0, 1.0, 'points', 'Normal probability plot')
    out = ['r of plot = ' + sf3(r),
           'slope (sd est) = ' + sf3(b),
           'intercept (mean est) = ' + sf3(a)]
    if r > 0.98:
        out.append('close to a line: Normal fits')
    else:
        out.append(warn('curved: Normal is doubtful'))
    out.append(w('x: z = invphi((i-0.5)/n), y: sorted data'))
    out.append(w('straight line means Normal'))
    out.append(w('S shape: tails too short or long'))
    return out

# =============================================================================
# R  Bivariate data
# Sb1 b2 b4 Sb6 b7 Sb8 b9 b10 Sb11 b12 b13 b14 b15
# =============================================================================

def _xy(data, least):
    xs, ys = _split(data, 'x,y')
    if len(xs) < least:
        raise ValueError('need at least ' + fmt(least) + ' pairs')
    return (xs, ys)

def _bstats(xs, ys):
    n = len(xs)
    mx = 0.0
    my = 0.0
    i = 0
    while i < n:
        mx += xs[i]
        my += ys[i]
        i += 1
    mx /= n
    my /= n
    sxx = 0.0
    syy = 0.0
    sxy = 0.0
    i = 0
    while i < n:
        dx = xs[i] - mx
        dy = ys[i] - my
        sxx += dx * dx
        syy += dy * dy
        sxy += dx * dy
        i += 1
    return (n, mx, my, sxx, syy, sxy)

def _pmcc(xs, ys):
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if sxx <= 0 or syy <= 0:
        raise ValueError('x or y values all equal')
    return (sxy / math.sqrt(sxx * syy), n, mx, my, sxx, syy, sxy)

def _ranks(v):
    # rank 1 = smallest; ties share the mean rank
    n = len(v)
    idx = list(range(n))
    idx.sort(key=lambda k: v[k])
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        k = i
        while k <= j:
            r[idx[k]] = avg
            k += 1
        i = j + 1
    return r

def _yline(a, b, y, x):
    return y + ' = ' + sf3(a) + (' + ' if b >= 0 else ' - ') + sf3(abs(b)) + x

def t_scatter(data):
    xs, ys = _xy(data, 2)
    r, n, mx, my, sxx, syy, sxy = _pmcc(xs, ys)
    b = sxy / sxx
    a = my - b * mx
    big = 0
    bigv = -1.0
    i = 0
    while i < n:
        e = abs(ys[i] - (a + b * xs[i]))
        if e > bigv:
            bigv = e
            big = i
        i += 1
    pts = []
    i = 0
    while i < n:
        pts.append((xs[i], ys[i]))
        i += 1
    import plot
    plot.run(pts, 0.0, 1.0, 'points', 'Scatter diagram')
    return ['n = ' + fmt(n),
            'r = ' + sf3(r),
            'means (' + sf3(mx) + ', ' + sf3(my) + ')',
            w('furthest from y on x line:'),
            w('(' + sf3(xs[big]) + ', ' + sf3(ys[big]) +
              '), residual ' + sf3(ys[big] - a - b * xs[big])),
            w('look for outliers and curvature by eye')]

def t_pmccr(data):
    xs, ys = _xy(data, 2)
    r, n, mx, my, sxx, syy, sxy = _pmcc(xs, ys)
    return ['r = ' + sf3(r),
            'r^2 = ' + sf3(r * r),
            'n = ' + fmt(n),
            w('Sxx = ' + sf3(sxx) + ', Syy = ' + sf3(syy)),
            w('Sxy = ' + sf3(sxy)),
            w('r = Sxy/sqrt(Sxx*Syy)'),
            w('r measures linear association only'),
            w('|r| is the effect size')]

def _rcrit(n, a1):
    # PMCC critical value from the table, else exactly from t with n-2 df
    v = tables.pmcc_crit(n, a1)
    if v is not None:
        return (v, True)
    t = _tstar(n - 2, a1)[0]
    return (t / math.sqrt(t * t + n - 2), False)

def _scrit(n, a1):
    # (value or None, exact); exact comes from the full permutation count
    if tables.SPEAR_NMIN <= n <= tables.SPEAR_NMAX:
        ok = False
        for q in (0.05, 0.025, 0.01, 0.005):
            if abs(a1 - q) < 1e-12:
                ok = True
                a1 = q
        if ok:
            return (tables.spearman_crit(n, a1), True)
    t = _tstar(n - 2, a1)[0]
    return (t / math.sqrt(t * t + n - 2), False)

def _corr_test(coef, n, pct, tail, name, rho, out):
    a = _level(pct, 'sig%')
    tail = _tail(tail)
    a1 = a / 2.0 if tail == 2 else a
    if name == 'r':
        cv, tabled = _rcrit(n, a1)
    else:
        cv, tabled = _scrit(n, a1)
    out.append(name + ' = ' + sf3(coef))
    if cv is None:
        out.append(warn('n = ' + fmt(n) + ' too small for this level'))
        out.append(_verdict(False, pct))
    else:
        sgn = '-' if (tail == 1 and coef < 0) else ''
        out.append('crit = ' + ('+/-' if tail == 2 else sgn) + sf3(cv))
        out.append(_verdict(abs(coef) >= cv, pct))
        if not tabled:
            if name == 'r':
                out.append(w('crit = t/sqrt(t^2+n-2), df n-2'))
            else:
                out.append(warn('approx crit from t, df n-2'))
    out.append(w('H0: ' + rho + ' = 0, n = ' + fmt(n)))
    if tail == 2:
        out.append(w('H1: ' + rho + ' is not 0 (2 tail)'))
    elif coef >= 0:
        out.append(w('H1: ' + rho + ' > 0 (1 tail)'))
    else:
        out.append(w('H1: ' + rho + ' < 0 (1 tail)'))
    if tail == 1:
        out.append(w('1 tail: H1 follows the sign of ' + name))

def _rp(r, n, tail, out):
    if n > 2 and abs(r) < 1.0:
        t = r * math.sqrt((n - 2) / (1.0 - r * r))
        p = _t_sf(abs(t), n - 2)
        out.insert(2, _pfmt(2.0 * p if tail == 2 else p))
        out.append(w('t = r sqrt((n-2)/(1-r^2)) = ' + sf3(t)))

def t_pmcctest(pct, tail, data):
    xs, ys = _xy(data, 3)
    r, n, mx, my, sxx, syy, sxy = _pmcc(xs, ys)
    out = []
    _corr_test(r, n, pct, tail, 'r', 'rho', out)
    _rp(r, n, _tail(tail), out)
    out.append(w('assumes a bivariate Normal parent'))
    return out

def t_pmcctest_r(r, n, pct, tail):
    if r < -1 or r > 1:
        raise ValueError('r must be -1 to 1')
    n = _whole(n, 'n', 3, 100000)
    out = []
    _corr_test(r, n, pct, tail, 'r', 'rho', out)
    _rp(r, n, _tail(tail), out)
    return out

def _spear(xs, ys):
    rx = _ranks(xs)
    ry = _ranks(ys)
    n = len(xs)
    d2 = 0.0
    tied = False
    i = 0
    while i < n:
        d2 += (rx[i] - ry[i]) * (rx[i] - ry[i])
        if rx[i] != int(rx[i]) or ry[i] != int(ry[i]):
            tied = True
        i += 1
    if tied:
        rs = _pmcc(rx, ry)[0]
    else:
        rs = 1.0 - 6.0 * d2 / (n * (n * n - 1))
    return (rs, rx, ry, d2, tied)

def _spear_lines(rx, ry, d2, n, tied, out):
    out.append(w('sum d^2 = ' + fmt(d2) + ', n = ' + fmt(n)))
    if tied:
        out.append(w('ties: rs = PMCC of the ranks'))
    else:
        out.append(w('rs = 1 - 6 sum d^2/(n(n^2-1))'))
    i = 0
    while i < n and i < 8:
        out.append(w('ranks ' + fmt(rx[i]) + ', ' + fmt(ry[i])))
        i += 1

def t_spearman(data):
    xs, ys = _xy(data, 3)
    rs, rx, ry, d2, tied = _spear(xs, ys)
    out = ['rs = ' + sf3(rs), 'n = ' + fmt(len(xs))]
    _spear_lines(rx, ry, d2, len(xs), tied, out)
    return out

def t_speartest(pct, tail, data):
    xs, ys = _xy(data, 4)
    rs, rx, ry, d2, tied = _spear(xs, ys)
    out = []
    _corr_test(rs, len(xs), pct, tail, 'rs', 'rho_s', out)
    if tied:
        out.append(warn('ties: the critical value is approx'))
    _spear_lines(rx, ry, d2, len(xs), tied, out)
    return out

def t_speartest_rs(rs, n, pct, tail):
    if rs < -1 or rs > 1:
        raise ValueError('rs must be -1 to 1')
    n = _whole(n, 'n', 4, 100000)
    out = []
    _corr_test(rs, n, pct, tail, 'rs', 'rho_s', out)
    out.append(w('exact crit for n <= ' + fmt(tables.SPEAR_NMAX) +
                 ' at 5, 2.5, 1, 0.5%'))
    return out

def _resid_lines(xs, ys, a, b, out, cap):
    ss = 0.0
    i = 0
    while i < len(xs):
        e = ys[i] - (a + b * xs[i])
        ss += e * e
        if i < cap:
            out.append(w('x=' + sf3(xs[i]) + ' y=' + sf3(ys[i]) +
                         ' resid ' + sf3(e)))
        i += 1
    if len(xs) > cap:
        out.append(w('(first ' + fmt(cap) + ' of ' + fmt(len(xs)) + ')'))
    return ss

def t_regyx(data):
    xs, ys = _xy(data, 2)
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if sxx <= 0:
        raise ValueError('x values all equal')
    b = sxy / sxx
    a = my - b * mx
    out = [_yline(a, b, 'y', 'x'), 'b = ' + sf3(b), 'a = ' + sf3(a)]
    if syy > 0:
        r = sxy / math.sqrt(sxx * syy)
        out.append('r^2 = ' + sf3(r * r))
    out.append(w('b = Sxy/Sxx = ' + sf3(sxy) + '/' + sf3(sxx)))
    out.append(w('a = ybar - b xbar, through (' + sf3(mx) + ', ' +
                 sf3(my) + ')'))
    ss = _resid_lines(xs, ys, a, b, out, 8)
    out.append(w('sum of squared residuals = ' + sf3(ss)))
    out.append(w('minimises the sum of squared residuals'))
    pts = []
    i = 0
    while i < n:
        pts.append((xs[i], ys[i]))
        i += 1
    import plot
    plot.run(pts, 0.0, 1.0, 'points', _yline(a, b, 'y', 'x'))
    return out

def t_regxy(data):
    xs, ys = _xy(data, 2)
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if syy <= 0:
        raise ValueError('y values all equal')
    d = sxy / syy
    c = mx - d * my
    out = [_yline(c, d, 'x', 'y'), 'd = ' + sf3(d), 'c = ' + sf3(c)]
    out.append(w('d = Sxy/Syy = ' + sf3(sxy) + '/' + sf3(syy)))
    out.append(w('c = xbar - d ybar'))
    out.append(w('use to estimate x from a given y'))
    out.append(w('minimises horizontal squared residuals'))
    return out

def t_regboth(data):
    xs, ys = _xy(data, 2)
    r, n, mx, my, sxx, syy, sxy = _pmcc(xs, ys)
    b = sxy / sxx
    a = my - b * mx
    d = sxy / syy
    c = mx - d * my
    out = ['y on x: ' + _yline(a, b, 'y', 'x'),
           'x on y: ' + _yline(c, d, 'x', 'y'),
           'meet at (' + sf3(mx) + ', ' + sf3(my) + ')',
           'r = ' + sf3(r) + ', r^2 = ' + sf3(r * r)]
    out.append(w('b*d = r^2 = ' + sf3(b * d)))
    out.append(w('lines coincide only when |r| = 1'))
    out.append(w('y on x: x controlled, predict y'))
    out.append(w('x on y: y controlled, predict x'))
    out.append(w('both random: use the one for the'))
    out.append(w('variable you want to estimate'))
    return out

def t_resid(data):
    xs, ys = _xy(data, 2)
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if sxx <= 0:
        raise ValueError('x values all equal')
    b = sxy / sxx
    a = my - b * mx
    out = [_yline(a, b, 'y', 'x')]
    ss = 0.0
    big = 0
    bige = 0.0
    i = 0
    while i < n:
        e = ys[i] - (a + b * xs[i])
        ss += e * e
        if abs(e) > abs(bige):
            bige = e
            big = i
        if i < 12:
            out.append('x=' + sf3(xs[i]) + ': e = ' + sf3(e))
        i += 1
    out.append('sum e^2 = ' + sf3(ss))
    out.append('biggest at x = ' + sf3(xs[big]))
    if syy > 0:
        out.append(w('r^2 = ' + sf3(sxy * sxy / (sxx * syy)) +
                     ' of variation explained'))
    out.append(w('residual e = y - (a + bx)'))
    out.append(w('sum e = 0; look for pattern'))
    return out

def t_predy(x0, data):
    xs, ys = _xy(data, 2)
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if sxx <= 0:
        raise ValueError('x values all equal')
    b = sxy / sxx
    a = my - b * mx
    out = ['y = ' + sf3(a + b * x0), _yline(a, b, 'y', 'x')]
    if x0 < min(xs) or x0 > max(xs):
        out.append(warn('extrapolation: x outside data'))
    else:
        out.append(w('interpolation: x within the data'))
    out.append(w('y on x line, x0 = ' + sf3(x0)))
    return out

def t_predx(y0, data):
    xs, ys = _xy(data, 2)
    n, mx, my, sxx, syy, sxy = _bstats(xs, ys)
    if syy <= 0:
        raise ValueError('y values all equal')
    d = sxy / syy
    c = mx - d * my
    out = ['x = ' + sf3(c + d * y0), _yline(c, d, 'x', 'y')]
    if y0 < min(ys) or y0 > max(ys):
        out.append(warn('extrapolation: y outside data'))
    else:
        out.append(w('interpolation: y within the data'))
    out.append(w('x on y line, y0 = ' + sf3(y0)))
    return out

# =============================================================================
# H  Chi-squared tests
# Sb16 SH1 H2 H3 H4
# =============================================================================

def _table(rows, cols, data):
    r = _int(rows, 'rows')
    c = _int(cols, 'cols')
    if r < 2 or c < 2 or r > 10 or c > 10:
        raise ValueError('rows and cols must be 2 to 10')
    if len(data) != r * c:
        raise ValueError('need ' + fmt(r * c) + ' counts')
    obs = []
    i = 0
    while i < r:
        row = data[i * c:(i + 1) * c]
        for v in row:
            if v < 0:
                raise ValueError('counts must be >= 0')
        obs.append(row)
        i += 1
    rowt = []
    for row in obs:
        s = 0.0
        for v in row:
            s += v
        rowt.append(s)
    colt = []
    j = 0
    while j < c:
        s = 0.0
        i = 0
        while i < r:
            s += obs[i][j]
            i += 1
        colt.append(s)
        j += 1
    tot = 0.0
    for v in rowt:
        tot += v
    if tot <= 0:
        raise ValueError('table total is 0')
    exp = []
    i = 0
    while i < r:
        row = []
        j = 0
        while j < c:
            e = rowt[i] * colt[j] / tot
            if e <= 0:
                raise ValueError('zero expected frequency')
            row.append(e)
            j += 1
        exp.append(row)
        i += 1
    return (r, c, obs, exp, rowt, colt, tot)

def _small(r, c, exp, out):
    small = 0
    i = 0
    while i < r:
        j = 0
        while j < c:
            if exp[i][j] < 5:
                small += 1
            j += 1
        i += 1
    if small:
        out.append(warn(fmt(small) + ' cell(s) have E < 5'))
        out.append(warn('combine rows or columns first'))

def _exp_lines(r, exp, rowt, colt, tot, out, rows=True):
    out.append(w('E = row total * col total / N'))
    out.append(w('N = ' + fmt(tot)))
    i = 0
    while rows and i < r:
        out.append(w('E r' + fmt(i + 1) + ': ' +
                     ' '.join([sf3(v) for v in exp[i]])))
        i += 1
    out.append(w('row totals: ' + ' '.join([fmt(v) for v in rowt])))
    out.append(w('col totals: ' + ' '.join([fmt(v) for v in colt])))

def _contribs(r, c, obs, exp):
    con = []
    chi = 0.0
    i = 0
    while i < r:
        row = []
        j = 0
        while j < c:
            d = obs[i][j] - exp[i][j]
            v = d * d / exp[i][j]
            chi += v
            row.append(v)
            j += 1
        con.append(row)
        i += 1
    return (con, chi)

def _chi_verdict(chi, df, pct, out, h1):
    a = _level(pct, 'sig%')
    cv, tabled = _chistar(df, a)
    out.append('crit = ' + sf3(cv))
    out.append(_pfmt(_chi2_sf(chi, df)))
    out.append(_verdict(chi > cv, pct))
    if chi > cv:
        out.append(h1)
    _computed(tabled, out)

def t_assoc(rows, cols, pct, data):
    r, c, obs, exp, rowt, colt, tot = _table(rows, cols, data)
    con, chi = _contribs(r, c, obs, exp)
    df = (r - 1) * (c - 1)
    out = ['chi^2 = ' + sf3(chi), 'df = ' + fmt(df)]
    _chi_verdict(chi, df, pct, out, 'evidence of association')
    bi = 0
    bj = 0
    i = 0
    while i < r:
        j = 0
        while j < c:
            if con[i][j] > con[bi][bj]:
                bi = i
                bj = j
            j += 1
        i += 1
    out.append('biggest r' + fmt(bi + 1) + 'c' + fmt(bj + 1) +
               (' O>E' if obs[bi][bj] > exp[bi][bj] else ' O<E'))
    _small(r, c, exp, out)
    out.append(w('H0: no association between the'))
    out.append(w('    two factors'))
    out.append(w('df = (r-1)(c-1) = ' + fmt(df)))
    out.append(w('chi^2 = sum (O-E)^2/E, no Yates'))
    _exp_lines(r, exp, rowt, colt, tot, out)
    return out

def t_contrib(rows, cols, data):
    r, c, obs, exp, rowt, colt, tot = _table(rows, cols, data)
    con, chi = _contribs(r, c, obs, exp)
    out = []
    i = 0
    while i < r:
        parts = []
        j = 0
        while j < c:
            parts.append(('+' if obs[i][j] >= exp[i][j] else '-') +
                         sf3(con[i][j]))
            j += 1
        out.append('r' + fmt(i + 1) + ': ' + ' '.join(parts))
        i += 1
    out.append('chi^2 = ' + sf3(chi))
    out.append(w('(O-E)^2/E per cell; + means O > E'))
    out.append(w('big contributions show where the'))
    out.append(w('association comes from'))
    _exp_lines(r, exp, rowt, colt, tot, out)
    return out

def t_expected(rows, cols, data):
    r, c, obs, exp, rowt, colt, tot = _table(rows, cols, data)
    out = []
    i = 0
    while i < r:
        out.append('r' + fmt(i + 1) + ': ' +
                   ' '.join([sf3(v) for v in exp[i]]))
        i += 1
    _small(r, c, exp, out)
    _exp_lines(r, exp, rowt, colt, tot, out, False)
    return out

def _gof(obs, exp, labels, m, pct, out):
    k = len(obs)
    df = k - 1 - m
    if df < 1:
        raise ValueError('df = ' + fmt(df) + ': too few cells')
    chi = 0.0
    small = 0
    i = 0
    while i < k:
        if exp[i] <= 0:
            raise ValueError('an expected frequency is 0')
        d = obs[i] - exp[i]
        chi += d * d / exp[i]
        if exp[i] < 5:
            small += 1
        i += 1
    out.insert(0, 'chi^2 = ' + sf3(chi))
    out.insert(1, 'df = ' + fmt(df))
    head = []
    _chi_verdict(chi, df, pct, head, 'model does not fit')
    j = 0
    while j < len(head):
        out.insert(2 + j, head[j])
        j += 1
    if small:
        out.append(warn(fmt(small) + ' cell(s) have E < 5'))
    out.append(w('df = cells - 1 - estimated = ' + fmt(k) + ' - 1 - ' +
                 fmt(m)))
    i = 0
    while i < k and i < 12:
        d = obs[i] - exp[i]
        out.append(w(labels[i] + ': O ' + fmt(obs[i]) + ', E ' +
                     sf3(exp[i]) + ', ' + sf3(d * d / exp[i])))
        i += 1
    return chi

def _total(vs, name):
    tot = 0.0
    for v in vs:
        if v < 0:
            raise ValueError(name + ' must be >= 0')
        tot += v
    if tot <= 0:
        raise ValueError('total is 0')
    return tot

def _lab(n):
    return [fmt(i + 1) for i in range(n)]

def t_gofp(pct, data):
    obs, ps = _split(data, 'O,p')
    n = _total(obs, 'O')
    tot = _total(ps, 'p')
    if abs(tot - 1.0) > 1e-6:
        raise ValueError('probs sum to ' + sf3(tot) + ', not 1')
    exp = [n * q for q in ps]
    out = [w('E = N*p, N = ' + fmt(n))]
    _gof(obs, exp, _lab(len(obs)), 0, pct, out)
    return out

def t_gofe(pct, m, data):
    m = _whole(m, 'estimated', 0, 10)
    obs, exp = _split(data, 'O,E')
    n = _total(obs, 'O')
    ne = _total(exp, 'E')
    out = []
    if abs(n - ne) > 1e-6 * n:
        out.append(warn('sum O = ' + fmt(n) + ', sum E = ' + sf3(ne)))
    _gof(obs, exp, _lab(len(obs)), m, pct, out)
    return out

def t_gofu(pct, obs):
    if len(obs) < 2:
        raise ValueError('need at least 2 cells')
    n = _total(obs, 'O')
    e = n / len(obs)
    out = [w('uniform: E = N/k = ' + sf3(e) + ' each')]
    _gof(obs, [e] * len(obs), _lab(len(obs)), 0, pct, out)
    return out

def _pool(obs, exp, labels):
    # merge neighbouring cells until every E >= 5 (ordered classes only)
    go = []
    ge = []
    gl = []
    ao = 0.0
    ae = 0.0
    start = None
    i = 0
    while i < len(obs):
        if start is None:
            start = labels[i]
        ao += obs[i]
        ae += exp[i]
        last = labels[i]
        if ae >= 5:
            go.append(ao)
            ge.append(ae)
            gl.append(start if start == last else start + '-' + last)
            ao = 0.0
            ae = 0.0
            start = None
        i += 1
    if start is not None:
        if go:
            go[len(go) - 1] += ao
            ge[len(ge) - 1] += ae
            first = gl[len(gl) - 1].split('-')[0]
            gl[len(gl) - 1] = first + '-' + last
        else:
            go.append(ao)
            ge.append(ae)
            gl.append(start + '-' + last)
    return (go, ge, gl)

def _pool_note(k, go, out):
    if len(go) < k:
        out.append(w('pooled ' + fmt(k) + ' cells into ' + fmt(len(go)) +
                     ' so each E >= 5'))

def t_gofbin(n, p, pct, obs):
    n = _whole(n, 'n', 1, 200)
    if len(obs) != n + 1:
        raise ValueError('need ' + fmt(n + 1) + ' counts, x = 0..n')
    N = _total(obs, 'O')
    m = 0
    out = []
    if p is None:
        s = 0.0
        i = 0
        while i <= n:
            s += i * obs[i]
            i += 1
        p = s / (N * n)
        m = 1
        out.append(w('p estimated: xbar/n = ' + sf3(p)))
    _prob(p, 'p')
    exp = [N * casutil.binom_pmf(n, p, i) for i in range(n + 1)]
    labs = [fmt(i) for i in range(n + 1)]
    go, ge, gl = _pool(obs, exp, labs)
    _pool_note(n + 1, go, out)
    out.append(w('E = N*P(X=x), X ~ B(' + fmt(n) + ', ' + sf3(p) + ')'))
    _gof(go, ge, gl, m, pct, out)
    return out

def t_gofpois(mu, pct, obs):
    if len(obs) < 2 or len(obs) > 60:
        raise ValueError('need 2 to 60 counts, x = 0, 1, ..')
    N = _total(obs, 'O')
    k = len(obs)
    m = 0
    out = []
    if mu is None:
        s = 0.0
        i = 0
        while i < k:
            s += i * obs[i]
            i += 1
        mu = s / N
        m = 1
        out.append(w('mu estimated: xbar = ' + sf3(mu)))
        out.append(warn('last class taken as x = ' + fmt(k - 1)))
    _mu(mu, 'mu')
    exp = []
    cum = 0.0
    i = 0
    while i < k - 1:
        pr = casutil.poisson_pmf(mu, i)
        cum += pr
        exp.append(N * pr)
        i += 1
    exp.append(N * max(0.0, 1.0 - cum))
    labs = [fmt(i) for i in range(k)]
    labs[k - 1] = fmt(k - 1) + '+'
    go, ge, gl = _pool(obs, exp, labs)
    _pool_note(k, go, out)
    out.append(w('E = N*P(X=x), last cell P(X>=' + fmt(k - 1) + ')'))
    _gof(go, ge, gl, m, pct, out)
    return out

def t_chistat(chi, df, pct):
    if chi < 0:
        raise ValueError('chi^2 must be >= 0')
    df = _whole(df, 'df', 1, 1000)
    out = ['chi^2 = ' + sf3(chi), 'df = ' + fmt(df)]
    _chi_verdict(chi, df, pct, out, 'evidence against H0')
    out.append(w('upper tail chi^2 test, df = ' + fmt(df)))
    return out

# =============================================================================
# I  Inference: estimates, z test, confidence intervals
# SI1 I2 I4 I8 I9 I11 I13 H6
# =============================================================================

def _estimates(n, mean, ss, out):
    if ss < 0:
        ss = 0.0
    s2 = ss / (n - 1)
    out.append('xbar = ' + sf3(mean))
    out.append('s^2 = ' + sf3(s2))
    out.append('s = ' + sf3(_sqrt(s2)))
    out.append('SE = s/sqrt(n) = ' + sf3(_sqrt(s2) / math.sqrt(n)))
    out.append(w('n = ' + fmt(n) + ', Sxx = ' + sf3(ss)))
    out.append(w('s^2 = Sxx/(n-1): unbiased for sigma^2'))
    out.append(w('divisor n would give ' + sf3(ss / n)))
    out.append(w('xbar is unbiased for mu'))

def t_est(data):
    if len(data) < 2:
        raise ValueError('need at least 2 values')
    sx = 0.0
    sq = 0.0
    for v in data:
        sx += v
    mean = sx / len(data)
    for v in data:
        sq += (v - mean) * (v - mean)
    out = []
    _estimates(len(data), mean, sq, out)
    return out

def t_estsum(n, sx, sxx):
    n = _whole(n, 'n', 2, 10 ** 9)
    if sxx * n < sx * sx - 1e-9 * abs(sx * sx):
        raise ValueError('sum x^2 too small for sum x')
    out = []
    _estimates(n, sx / n, sxx - sx * sx / n, out)
    return out

def _ztest(mu0, sd, n, xbar, pct, tail, out):
    tail = _tail(tail)
    a = _level(pct, 'sig%')
    se = sd / math.sqrt(n)
    z = (xbar - mu0) / se
    az = abs(z)
    p1 = 1.0 - casutil.phi(az)
    p = 2.0 * p1 if tail == 2 else p1
    zc, tabled = _zstar(a / 2.0 if tail == 2 else a)
    sgn = '-' if (tail == 1 and z < 0) else ''
    out.append('z = ' + sf3(z))
    out.append('crit = ' + ('+/-' if tail == 2 else sgn) + sf3(zc))
    out.append(_pfmt(p))
    out.append(_verdict(az > zc, pct))
    _computed(tabled, out)
    out.append(w('H0: mu = ' + sf3(mu0)))
    if tail == 2:
        out.append(w('H1: mu is not ' + sf3(mu0) + ' (2 tail)'))
    elif z >= 0:
        out.append(w('H1: mu > ' + sf3(mu0) + ' (1 tail)'))
    else:
        out.append(w('H1: mu < ' + sf3(mu0) + ' (1 tail)'))
    out.append(w('SE = sigma/sqrt(n) = ' + sf3(se)))
    out.append(w('z = (xbar-mu0)/SE, Xbar ~ N(mu0, SE^2)'))
    if tail == 1:
        out.append(w('1 tail: H1 follows the sign of z'))

def t_ztest(mu0, sigma, n, xbar, pct, tail):
    _pos(sigma, 'sigma')
    n = _whole(n, 'n', 1, 10 ** 9)
    out = []
    _ztest(mu0, sigma, n, xbar, pct, tail, out)
    return out

def t_ztest_data(mu0, sigma, pct, tail, data):
    n, mean, s = _mean_sd(data)
    out = []
    if sigma is None:
        if s <= 0:
            raise ValueError('all values equal')
        sd = s
        if n < 30:
            out.append(warn('n < 30: s for sigma is rough'))
    else:
        sd = _pos(sigma, 'sigma')
    _ztest(mu0, sd, n, mean, pct, tail, out)
    out.append(w('xbar = ' + sf3(mean) + ', n = ' + fmt(n) +
                 (', s = ' + sf3(s) if sigma is None else '')))
    return out

def _ci_lines(centre, half, out):
    out.insert(0, '(' + sf3(centre - half) + ', ' + sf3(centre + half) + ')')
    out.insert(1, 'centre ' + sf3(centre) + ' +/- ' + sf3(half))

def t_ci_z(xbar, sigma, n, pct):
    _pos(sigma, 'sigma')
    n = _whole(n, 'n', 1, 10 ** 9)
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    z, tabled = _zstar(tp)
    se = sigma / math.sqrt(n)
    half = z * se
    out = []
    _ci_lines(xbar, half, out)
    out.append('z* = ' + sf3(z))
    _computed(tabled, out)
    out.append(w('sigma known so z, not t'))
    out.append(w('SE = sigma/sqrt(n) = ' + sf3(se)))
    out.append(w('xbar +/- z*SE = ' + sf3(xbar) + ' +/- ' + sf3(half)))
    return out

def _ci_unknown(n, xbar, s, pct, what):
    n = _whole(n, 'n', 2, 10 ** 6)
    if s <= 0:
        raise ValueError('s must be > 0')
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    se = s / math.sqrt(n)
    tk, ttab = _tstar(n - 1, tp)
    zk, ztab = _zstar(tp)
    out = []
    if n >= 30:
        k = zk
        tabled = ztab
        out.append('z* = ' + sf3(zk))
        out.append(w('n >= 30 so z with s for sigma'))
        out.append(w('t interval: ' + what + ' +/- ' + sf3(tk * se)))
    else:
        k = tk
        tabled = ttab
        out.append('t* = ' + sf3(tk) + ' (df ' + fmt(n - 1) + ')')
        out.append(w('sigma unknown so t, df = ' + fmt(n - 1)))
        out.append(w('assumes a Normal parent'))
    half = k * se
    _ci_lines(xbar, half, out)
    _computed(tabled, out)
    out.append(w(what + ' = ' + sf3(xbar) + ', s = ' + sf3(s) +
                 ', n = ' + fmt(n)))
    out.append(w('SE = s/sqrt(n) = ' + sf3(se)))
    return out

def t_ci_data(pct, data):
    n, mean, s = _mean_sd(data)
    return _ci_unknown(n, mean, s, pct, 'xbar')

def t_ci_sum(n, xbar, s, pct):
    return _ci_unknown(_int(n, 'n'), xbar, s, pct, 'xbar')

def t_ci_paired(pct, data):
    xs, ys = _xy(data, 2)
    ds = [xs[i] - ys[i] for i in range(len(xs))]
    n, mean, s = _mean_sd(ds)
    out = _ci_unknown(n, mean, s, pct, 'dbar')
    out.append(w('differences d = x - y'))
    out.append(w('CI for the mean difference'))
    return out

def t_ci_in(lo, hi, mu0):
    if hi <= lo:
        raise ValueError('need hi > lo')
    centre = 0.5 * (lo + hi)
    half = 0.5 * (hi - lo)
    inside = lo <= mu0 <= hi
    return ['mu0 ' + ('inside' if inside else 'outside') + ' the CI',
            'do not reject H0' if inside else 'reject H0',
            'centre = ' + sf3(centre),
            'half width = ' + sf3(half),
            w('mu0 = ' + sf3(mu0) + ', CI = (' + sf3(lo) + ', ' +
              sf3(hi) + ')'),
            w('a C% CI holds every mu0 not rejected'),
            w('by a 2 tail test at the (100-C)% level')]

def t_ci_n(sigma, width, pct):
    _pos(sigma, 'sigma')
    _pos(width, 'width')
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    z, tabled = _zstar(tp)
    exact = (2.0 * z * sigma / width) ** 2
    if exact > 1e12:
        raise ValueError('n too large')
    n = int(math.ceil(exact))
    if n < 1:
        n = 1
    out = ['n = ' + fmt(n),
           'z* = ' + sf3(z),
           'exact n = ' + sf3(exact)]
    _computed(tabled, out)
    out.append(w('full width = 2 z sigma/sqrt(n) <= ' + sf3(width)))
    out.append(w('n >= (2 z sigma/width)^2, round up'))
    out.append(w('4 times n halves the width'))
    return out

# =============================================================================
# W  Wilcoxon signed rank test
# SH5
# =============================================================================

def _wilcoxon(ds, pct, tail, h0, out):
    tail = _tail(tail)
    a = _level(pct, 'sig%')
    a1 = a / 2.0 if tail == 2 else a
    nz = []
    zeros = 0
    for d in ds:
        if d == 0:
            zeros += 1
        else:
            nz.append(d)
    n = len(nz)
    if n < 1:
        raise ValueError('every difference is 0')
    rk = _ranks([abs(d) for d in nz])
    wp = 0.0
    wm = 0.0
    i = 0
    while i < n:
        if nz[i] > 0:
            wp += rk[i]
        else:
            wm += rk[i]
        i += 1
    t = wp if wp < wm else wm
    tied = False
    for v in rk:
        if v != int(v):
            tied = True
    out.append('T = ' + fmt(t))
    out.append('W+ = ' + fmt(wp) + ', W- = ' + fmt(wm))
    out.append('n = ' + fmt(n) + ' non-zero')
    cv = tables.wilcoxon_crit(n, a1)
    if cv is None:
        mean = n * (n + 1) / 4.0
        sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
        z = (t + 0.5 - mean) / sd
        p = casutil.phi(z)
        p = 2.0 * p if tail == 2 else p
        out.append(_pfmt(p if p < 1 else 1.0))
        out.append(_verdict(p <= a, pct))
        out.append(warn('n > ' + fmt(tables.WILC_NMAX) +
                        ': Normal approximation'))
        out.append(w('z = (T+0.5-n(n+1)/4)/sd = ' + sf3(z)))
    else:
        p = tables.wilcoxon_cdf(n, int(math.floor(t)))
        p = 2.0 * p if tail == 2 else p
        if cv < 0:
            out.append(warn('n too small: cannot reject'))
            out.append(_verdict(False, pct))
        else:
            out.append('crit: reject if T <= ' + fmt(cv))
            out.append(_verdict(t <= cv, pct))
        out.append(_pfmt(p if p < 1 else 1.0))
    if tied:
        out.append(warn('tied ranks: exact values approx'))
    if zeros:
        out.append(w(fmt(zeros) + ' zero difference(s) dropped'))
    out.append(w('H0: ' + h0))
    out.append(w('rank |d|, sum ranks of + and - d'))
    if tail == 1:
        out.append(w('1 tail: H1 follows the data, T = min'))
    i = 0
    while i < n and i < 8:
        out.append(w('d = ' + sf3(nz[i]) + ', signed rank ' +
                     ('+' if nz[i] > 0 else '-') + fmt(rk[i])))
        i += 1

def t_wsingle(m0, pct, tail, data):
    if len(data) < 1:
        raise ValueError('need data')
    ds = [v - m0 for v in data]
    out = []
    _wilcoxon(ds, pct, tail, 'median = ' + sf3(m0), out)
    out.append(w('d = x - ' + sf3(m0) + '; assumes symmetry'))
    return out

def t_wpaired(pct, tail, data):
    xs, ys = _xy(data, 1)
    ds = [xs[i] - ys[i] for i in range(len(xs))]
    out = []
    _wilcoxon(ds, pct, tail, 'median difference = 0', out)
    out.append(w('d = x - y for each pair'))
    return out

def t_wcrit(n, pct, tail):
    n = _whole(n, 'n', 1, tables.WILC_NMAX)
    tail = _tail(tail)
    a = _level(pct, 'sig%')
    a1 = a / 2.0 if tail == 2 else a
    cv = tables.wilcoxon_crit(n, a1)
    out = []
    if cv < 0:
        out.append(warn('no critical value: n too small'))
        out.append('P(T=0) = ' + sf3(tables.wilcoxon_cdf(n, 0)))
    else:
        out.append('reject if T <= ' + fmt(cv))
        out.append('P(T<=' + fmt(cv) + ') = ' +
                   sf3(tables.wilcoxon_cdf(n, cv)))
        out.append('P(T<=' + fmt(cv + 1) + ') = ' +
                   sf3(tables.wilcoxon_cdf(n, cv + 1)))
    out.append(w('exact: count of rank subsets / 2^n'))
    out.append(w('one tail level ' + sf3(100.0 * a1) + '%'))
    out.append(w('E(T) = n(n+1)/4 = ' + fmt(n * (n + 1) / 4.0)))
    return out

def t_wfromt(T, n, pct, tail):
    n = _whole(n, 'n', 1, tables.WILC_NMAX)
    top = n * (n + 1) / 2.0
    if T < 0 or T > top:
        raise ValueError('T must be 0 to ' + fmt(top))
    if T > top / 2.0:
        T = top - T
    tail = _tail(tail)
    a = _level(pct, 'sig%')
    a1 = a / 2.0 if tail == 2 else a
    cv = tables.wilcoxon_crit(n, a1)
    p = tables.wilcoxon_cdf(n, int(math.floor(T)))
    p = 2.0 * p if tail == 2 else p
    out = ['T = ' + fmt(T)]
    if cv < 0:
        out.append(warn('n too small: cannot reject'))
    else:
        out.append('crit: reject if T <= ' + fmt(cv))
    out.append(_pfmt(p if p < 1 else 1.0))
    out.append(_verdict(cv >= 0 and T <= cv, pct))
    out.append(w('T = smaller of W+ and W-'))
    out.append(w('W+ + W- = n(n+1)/2 = ' + fmt(top)))
    return out

# =============================================================================
# Z  Simulation (a seeded generator keeps every tool pure)
# Z2
# =============================================================================

def _rng(seed):
    s = _whole(seed, 'seed', 0, 999999999)
    st = [(s * 69069 + 1234567) & 0x7FFFFFFF]
    i = 0
    while i < 5:
        _u(st)
        i += 1
    return st

def _u(st):
    st[0] = (1103515245 * st[0] + 12345) & 0x7FFFFFFF
    return (st[0] + 0.5) / 2147483648.0

def _trials(v):
    return _whole(v, 'trials', 10, 5000)

def _draw_cum(cum, u):
    # smallest index with cum[i] >= u (binary search)
    lo = 0
    hi = len(cum) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if cum[mid] < u:
            lo = mid + 1
        else:
            hi = mid
    return lo

def _sim_stats(vals, tmean, tvar, out):
    n = len(vals)
    tot = 0.0
    for v in vals:
        tot += v
    mean = tot / n
    ss = 0.0
    for v in vals:
        ss += (v - mean) * (v - mean)
    var = ss / (n - 1)
    out.append('sim mean = ' + sf3(mean) + ' (' + sf3(tmean) + ')')
    out.append('sim var = ' + sf3(var) + ' (' + sf3(tvar) + ')')
    out.append(w('theory values in brackets'))
    if tvar > 0:
        z = (mean - tmean) / math.sqrt(tvar / n)
        out.append(w('sim mean is ' + sf3(z) + ' SE from theory'))
    out.append(w('more trials: closer, error ~ 1/sqrt(N)'))

def _sim_counts(vals, xs, ps, out, title):
    # frequency table for integer outcomes against the model
    counts = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    n = float(len(vals))
    bars = []
    i = 0
    while i < len(xs):
        c = counts.get(xs[i], 0)
        if i < 12:
            out.append(w('x=' + fmt(xs[i]) + ': ' + fmt(c) + ' (' +
                         sf3(c / n) + ' vs ' + sf3(ps[i]) + ')'))
        bars.append((xs[i] - 0.4, xs[i] + 0.4, c / n))
        i += 1
    import plot
    plot.run(bars, xs[0] - 1.0, xs[len(xs) - 1] + 1.0, 'bars', title)

def _sim_hist(vals, title):
    lo = min(vals)
    hi = max(vals)
    if hi - lo < 1e-12:
        return
    k = 12
    counts = [0] * k
    for v in vals:
        b = int((v - lo) / (hi - lo) * k)
        if b >= k:
            b = k - 1
        counts[b] += 1
    wd = (hi - lo) / k
    bars = []
    i = 0
    while i < k:
        bars.append((lo + i * wd, lo + (i + 1) * wd, counts[i] / (len(vals) *
                                                                  wd)))
        i += 1
    import plot
    plot.run(bars, lo, hi, 'bars', title)

def _sim_discrete(xs, ps, trials, seed, title, tmean, tvar):
    st = _rng(seed)
    cum = []
    c = 0.0
    for q in ps:
        c += q
        cum.append(c)
    cum[len(cum) - 1] = 1.0
    vals = []
    i = 0
    while i < trials:
        vals.append(xs[_draw_cum(cum, _u(st))])
        i += 1
    out = []
    _sim_stats(vals, tmean, tvar, out)
    out.append(w(fmt(trials) + ' trials, seed ' + fmt(seed)))
    _sim_counts(vals, xs, ps, out, title)
    return out

def t_simbin(n, p, trials, seed):
    n = _whole(n, 'n', 1, 200)
    _prob(p, 'p')
    trials = _trials(trials)
    xs = list(range(n + 1))
    ps = [casutil.binom_pmf(n, p, k) for k in xs]
    return _sim_discrete(xs, ps, trials, seed, 'B(n, p) simulated',
                         n * p, n * p * (1.0 - p))

def t_simpois(mu, trials, seed):
    if mu <= 0 or mu > 100:
        raise ValueError('mu must be 0 to 100')
    trials = _trials(trials)
    lim = _pois_lim(mu)
    xs = list(range(lim + 1))
    ps = [casutil.poisson_pmf(mu, k) for k in xs]
    return _sim_discrete(xs, ps, trials, seed, 'Po(mu) simulated', mu, mu)

def t_simgeo(p, trials, seed):
    if p <= 0.01 or p > 1:
        raise ValueError('p must be 0.01 to 1')
    trials = _trials(trials)
    st = _rng(seed)
    vals = []
    q = 1.0 - p
    i = 0
    while i < trials:
        u = _u(st)
        if q <= 0:
            r = 1
        else:
            r = int(math.ceil(math.log(1.0 - u) / math.log(q)))
            if r < 1:
                r = 1
        vals.append(r)
        i += 1
    top = max(vals)
    xs = list(range(1, top + 1))
    ps = [q ** (r - 1) * p for r in xs]
    out = []
    _sim_stats(vals, 1.0 / p, q / (p * p), out)
    out.append(w(fmt(trials) + ' trials, seed ' + fmt(seed)))
    _sim_counts(vals, xs, ps, out, 'Geo(p) simulated')
    return out

def _normals(st, count):
    out = []
    while len(out) < count:
        u1 = _u(st)
        u2 = _u(st)
        r = math.sqrt(-2.0 * math.log(u1))
        out.append(r * math.cos(2.0 * math.pi * u2))
        out.append(r * math.sin(2.0 * math.pi * u2))
    return out[:count]

def t_simnorm(mu, sigma, trials, seed):
    _pos(sigma, 'sigma')
    trials = _trials(trials)
    st = _rng(seed)
    vals = [mu + sigma * z for z in _normals(st, trials)]
    out = []
    _sim_stats(vals, mu, sigma * sigma, out)
    within = 0
    for v in vals:
        if abs(v - mu) <= 1.96 * sigma:
            within += 1
    out.append('within 1.96 sd: ' + sf3(100.0 * within / trials) + '%')
    out.append(w(fmt(trials) + ' trials, seed ' + fmt(seed)))
    out.append(w('Box-Muller from uniform numbers'))
    _sim_hist(vals, 'N(mu, sigma^2) simulated')
    return out

def t_simunif(a, b, trials, seed):
    if b <= a:
        raise ValueError('need b > a')
    trials = _trials(trials)
    st = _rng(seed)
    vals = [a + (b - a) * _u(st) for i in range(trials)]
    out = []
    _sim_stats(vals, (a + b) / 2.0, (b - a) * (b - a) / 12.0, out)
    out.append(w(fmt(trials) + ' trials, seed ' + fmt(seed)))
    _sim_hist(vals, 'U(a, b) simulated')
    return out

def t_simmeans(a, b, n, trials, seed):
    if b <= a:
        raise ValueError('need b > a')
    n = _whole(n, 'n', 1, 100)
    trials = _trials(trials)
    if n * trials > 100000:
        raise ValueError('n * trials must be <= 100000')
    st = _rng(seed)
    vals = []
    i = 0
    while i < trials:
        s = 0.0
        j = 0
        while j < n:
            s += a + (b - a) * _u(st)
            j += 1
        vals.append(s / n)
        i += 1
    out = []
    _sim_stats(vals, (a + b) / 2.0, (b - a) * (b - a) / (12.0 * n), out)
    out.append(w('means of n = ' + fmt(n) + ' values from U(a, b)'))
    out.append(w('Var(Xbar) = sigma^2/n; shape -> Normal'))
    out.append(w(fmt(trials) + ' trials, seed ' + fmt(seed)))
    _sim_hist(vals, 'sample means simulated')
    return out

def t_simdrv(trials, seed, data):
    xs, ps = _pairs(data)
    tot = 0.0
    for q in ps:
        tot += q
    if abs(tot - 1.0) > 1e-6:
        raise ValueError('probs sum to ' + sf3(tot) + ', not 1')
    trials = _trials(trials)
    order = list(range(len(xs)))
    order.sort(key=lambda k: xs[k])
    sx = [xs[k] for k in order]
    sp = [ps[k] for k in order]
    e1, e2, var = _moments(sx, sp)
    return _sim_discrete(sx, sp, trials, seed, 'X simulated', e1, var)

# =============================================================================

SECTIONS = [
    ('D', 'Discrete random vars', [
        ('DRV from table', 'x p pairs*', t_drv),
        ('DRV from formula', 'p(x),a,b', t_drvf),
        ('DRV find k', 'g(x),a,b', t_drvk),
        ('E(g(X)) from table', 'g(x),x p pairs*', t_egx),
        ('E and Var of a+bX', 'a,b,mean,var', t_linear),
        ('E and Var of X+-Y', 'mx,vx,my,vy', t_sumxy),
        ('Discrete uniform', 'a,b,c?,d?', t_dunif),
    ]),
    ('B', 'Binomial and Poisson', [
        ('Poisson P(X=k)', 'mu,k', t_pois),
        ('Poisson a<=X<=b', 'mu,a,b', t_poisrange),
        ('Poisson least k', 'mu,p', t_poisinv),
        ('Sum of Poissons', 'k,mu*', t_poissum),
        ('Poisson approx to B', 'n,p,k', t_papprox),
        ('Poisson model check', 'data*', t_poischeck),
        ('Binomial P(X=k)', 'n,p,k', t_binom),
    ]),
    ('G', 'Geometric distribution', [
        ('Geometric P(X=r)', 'p,r', t_geom),
        ('Geometric a<=X<=b', 'p,a,b', t_georange),
        ('Geometric least r', 'p,prob', t_geoinv),
    ]),
    ('C', 'Continuous random vars', [
        ('pdf E Var and check', 'f(x),a,b', t_pdf),
        ('pdf median quartiles', 'f(x),a,b', t_pdfq),
        ('Mode of a pdf', 'f(x),a,b', t_pdfmode),
        ('cdf F(x) from a pdf', 'f(x),a,b,t', t_cdf),
        ('pdf from a cdf', 'F(x),a,b', t_pdffromcdf),
        ('cdf median quartiles', 'F(x),a,b,p?', t_cdfq),
        ('pdf P(c<X<d)', 'f(x),a,b,c,d', t_pdfp),
        ('E of g(X) from a pdf', 'g(x),f(x),a,b', t_pdfg),
        ('Piecewise pdf', 'f(x),g(x),a,b,c', t_pdfpw),
        ('Rectangular U(a,b)', 'a,b,c?,d?', t_rect),
    ]),
    ('N', 'Normal distribution', [
        ('Normal P(a<X<b)', 'mu,sigma,a,b', t_normal),
        ('Inverse Normal', 'mu,sigma,p', t_ninv),
        ('Normal fit to data', 'data*', t_nfit),
        ('Normal P from sample', 'a,b,data*', t_nsample),
        ('aX+bY+c', 'a,b,c,mx,vx,my,vy,k?', t_lincomb),
        ('nX vs X1+..+Xn', 'mu,var,n,k?', t_nsum),
        ('Normal prob plot', 'data*', t_nplot),
    ]),
    ('R', 'Bivariate data', [
        ('Scatter diagram', 'x y pairs*', t_scatter),
        ('PMCC r', 'x y pairs*', t_pmccr),
        ('PMCC test from data', 'sig%,tail,x y pairs*', t_pmcctest),
        ('PMCC test from r', 'r,n,sig%,tail', t_pmcctest_r),
        ('Spearman rs', 'x y pairs*', t_spearman),
        ('Spearman test data', 'sig%,tail,x y pairs*', t_speartest),
        ('Spearman test from rs', 'rs,n,sig%,tail', t_speartest_rs),
        ('Regression y on x', 'x y pairs*', t_regyx),
        ('Regression x on y', 'x y pairs*', t_regxy),
        ('Both regression lines', 'x y pairs*', t_regboth),
        ('Residuals', 'x y pairs*', t_resid),
        ('Predict y from x', 'x0,x y pairs*', t_predy),
        ('Predict x from y', 'y0,x y pairs*', t_predx),
    ]),
    ('H', 'Chi-squared tests', [
        ('Chi-sq association', 'rows,cols,sig%,data*', t_assoc),
        ('Chi-sq contributions', 'rows,cols,data*', t_contrib),
        ('Expected frequencies', 'rows,cols,data*', t_expected),
        ('GOF given probs', 'sig%,O p pairs*', t_gofp),
        ('GOF given expected', 'sig%,estimated,O E pairs*', t_gofe),
        ('GOF uniform', 'sig%,O*', t_gofu),
        ('GOF binomial', 'n,p,sig%,O*', t_gofbin),
        ('GOF Poisson', 'mu,sig%,O*', t_gofpois),
        ('Chi-sq crit and p', 'chi2,df,sig%', t_chistat),
    ]),
    ('I', 'Inference', [
        ('Estimates from data', 'data*', t_est),
        ('Estimates from sums', 'n,sumx,sumx2', t_estsum),
        ('z test for a mean', 'mu0,sigma,n,xbar,sig%,tail', t_ztest),
        ('z test from data', 'mu0,sigma,sig%,tail,data*', t_ztest_data),
        ('CI mean sigma known', 'xbar,sigma,n,conf%', t_ci_z),
        ('CI mean from data', 'conf%,data*', t_ci_data),
        ('CI mean from summary', 'n,xbar,s,conf%', t_ci_sum),
        ('CI paired data', 'conf%,x y pairs*', t_ci_paired),
        ('CI to test mu0', 'lo,hi,mu0', t_ci_in),
        ('Sample size for width', 'sigma,fullwidth,conf%', t_ci_n),
    ]),
    ('W', 'Wilcoxon signed rank', [
        ('Wilcoxon single sample', 'm0,sig%,tail,data*', t_wsingle),
        ('Wilcoxon paired', 'sig%,tail,x y pairs*', t_wpaired),
        ('Wilcoxon crit value', 'n,sig%,tail', t_wcrit),
        ('Wilcoxon from T', 'T,n,sig%,tail', t_wfromt),
    ]),
    ('Z', 'Simulation', [
        ('Simulate binomial', 'n,p,trials,seed', t_simbin),
        ('Simulate Poisson', 'mu,trials,seed', t_simpois),
        ('Simulate geometric', 'p,trials,seed', t_simgeo),
        ('Simulate Normal', 'mu,sigma,trials,seed', t_simnorm),
        ('Simulate U(a,b)', 'a,b,trials,seed', t_simunif),
        ('Simulate sample means', 'a,b,n,trials,seed', t_simmeans),
        ('Simulate a DRV', 'trials,seed,x p pairs*', t_simdrv),
    ]),
]
