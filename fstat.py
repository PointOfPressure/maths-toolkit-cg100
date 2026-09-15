# AQA Further Maths 7367, Statistics option: sections SA to SH.
# Discrete random variables, Poisson, Type I/II errors, continuous random
# variables, chi-squared for association, exponential, one-sample t and
# confidence intervals.
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

def _level(v, name):
    if v <= 0 or v >= 100:
        raise ValueError(name + ' must be 0 to 100')
    return v / 100.0

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

def _pairs(data):
    # alternating value, probability
    if len(data) < 2 or len(data) % 2:
        raise ValueError('need value,prob pairs')
    xs = []
    ps = []
    i = 0
    while i < len(data):
        xs.append(data[i])
        ps.append(data[i + 1])
        i += 2
    for q in ps:
        if q < 0 or q > 1:
            raise ValueError('probability must be 0 to 1')
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

def _tstar(df, p):
    # (critical value, came from the table)
    v = tables.t_crit(df, p)
    if v is not None:
        return (v, True)
    lo = 0.0
    hi = 4.0
    i = 0
    while i < 40 and _t_sf(hi, df) > p:
        hi *= 2.0
        i += 1
    i = 0
    while i < 60:
        mid = 0.5 * (lo + hi)
        if _t_sf(mid, df) > p:
            lo = mid
        else:
            hi = mid
        i += 1
    return (0.5 * (lo + hi), False)

def _zstar(p):
    v = tables.z_crit(p)
    if v is not None:
        return (v, True)
    return (casutil.invphi(1.0 - p), False)

def _pfmt(p):
    if p < 1e-4:
        return 'p < 0.0001'
    return 'p = ' + sf3(p)

def _verdict(p, alpha, pct):
    if p <= alpha:
        return 'reject H0 at ' + fmt(pct) + '%'
    return 'accept H0 at ' + fmt(pct) + '%'

# =============================================================================
# SA  Discrete random variables and expectation
# =============================================================================

def t_drv(data):
    xs, ps = _pairs(data)
    out = []
    e1, e2, var = _moments(xs, ps)
    out.append('E(X) = ' + fmt(e1))
    out.append('Var(X) = ' + fmt(var))
    out.append('SD = ' + sf3(_sqrt(var)))
    # mode
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
    # median: order by value, then cumulative probability
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
    med = None
    j = 0
    while j < len(sx):
        cum += sp[j]
        if abs(cum - 0.5) < 1e-12 and j + 1 < len(sx):
            med = 0.5 * (sx[j] + sx[j + 1])
            break
        if cum > 0.5:
            med = sx[j]
            break
        j += 1
    if med is None:
        med = sx[len(sx) - 1]
    out.append('median = ' + fmt(med))
    out.append(w('E(X) = sum x*p = ' + fmt(e1)))
    out.append(w('E(X^2) = sum x^2*p = ' + fmt(e2)))
    out.append(w('Var = E(X^2)-E(X)^2 = ' + fmt(e2) + '-' +
                 fmt(e1 * e1) + ' = ' + fmt(var)))
    out.append(w('median: first x with cum P >= 0.5'))
    _sumcheck(ps, out)
    return out

def t_drvf(p, n):
    n = _int(n, 'n')
    if n < 1 or n > 200:
        raise ValueError('n must be 1 to 200')
    xs = []
    ps = []
    i = 1
    while i <= n:
        v = casutil.real(casutil.ev(p, float(i)))
        if v < -1e-12:
            raise ValueError('P(X=' + fmt(i) + ') is negative')
        xs.append(i)
        ps.append(v)
        i += 1
    out = []
    e1, e2, var = _moments(xs, ps)
    _ev_var_lines(e1, e2, var, out)
    tot = _sumcheck(ps, out)
    shown = []
    i = 0
    while i < len(xs) and i < 6:
        shown.append('P(' + fmt(xs[i]) + ')=' + sf3(ps[i]))
        i += 1
    out.append(w(' '.join(shown)))
    out.insert(0, 'sum P = ' + fmt(tot))
    return out

def t_linear(a, b, mean, var):
    if var < 0:
        raise ValueError('Var(X) must be >= 0')
    ey = a * mean + b
    vy = a * a * var
    return ['E(aX+b) = ' + fmt(ey),
            'Var(aX+b) = ' + fmt(vy),
            'SD(aX+b) = ' + sf3(_sqrt(vy)),
            w('E(aX+b) = aE(X)+b = ' + fmt(a) + '*' + fmt(mean) +
              _sign(b) + ' = ' + fmt(ey)),
            w('Var(aX+b) = a^2Var(X) = ' + fmt(a * a) + '*' +
              fmt(var) + ' = ' + fmt(vy)),
            w('b shifts the mean, never the variance')]

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

def t_dunif(n):
    n = _int(n, 'n')
    if n < 1:
        raise ValueError('n must be >= 1')
    e1 = (n + 1) / 2.0
    var = (n * n - 1) / 12.0
    return ['P(X=x) = ' + fmt(1.0 / n),
            'E(X) = (n+1)/2 = ' + fmt(e1),
            'Var(X) = (n^2-1)/12 = ' + fmt(var),
            'SD = ' + sf3(_sqrt(var)),
            w('X uniform on 1, 2, ..., ' + fmt(n)),
            w('E(X) = (1/n)sum x = (1/n)*n(n+1)/2'),
            w('     = (n+1)/2 = ' + fmt(e1)),
            w('E(X^2) = (1/n)*n(n+1)(2n+1)/6'),
            w('       = (n+1)(2n+1)/6 = ' +
              fmt((n + 1) * (2 * n + 1) / 6.0)),
            w('Var = E(X^2)-E(X)^2'),
            w('    = (n+1)(2n+1)/6 - (n+1)^2/4'),
            w('    = (n^2-1)/12 = ' + fmt(var))]

# =============================================================================
# SB  Poisson distribution
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
    return ['least k with P(X<=k) >= p',
            'k = ' + fmt(k),
            'P(X<=k) = ' + sf3(cum[k]),
            'P(X<=k-1) = ' + sf3(below),
            w('p = ' + sf3(p) + ', mu = ' + sf3(mu)),
            w('P(X>=k) = ' + sf3(1.0 - below))]

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

def _pois_test(mu0, obs, pct, upper):
    _mu(mu0, 'mu0')
    obs = _whole(obs, 'obs', 0, 1000)
    a = _level(pct, 'level%')
    out = []
    lim = _pois_lim(mu0)
    if obs > lim:
        lim = obs
    cum = _pois_cum(mu0, lim)
    ge = lambda j: 1.0 - cum[j - 1] if j > 0 else 1.0
    if upper:
        k = 0
        while k < lim and ge(k) > a:
            k += 1
        act = ge(k)
        p = ge(obs)
        out.append('H1: mu > ' + sf3(mu0))
        out.append('critical region X >= ' + fmt(k))
        rej = obs >= k
    else:
        k = -1
        while k + 1 < lim and cum[k + 1] <= a:
            k += 1
        act = cum[k] if k >= 0 else 0.0
        p = cum[obs]
        if k < 0:
            out.append(warn('critical region is empty'))
            out.append('no X can reject H0')
        else:
            out.append('H1: mu < ' + sf3(mu0))
            out.append('critical region X <= ' + fmt(k))
        rej = k >= 0 and obs <= k
    out.append(_pfmt(p))
    out.append('reject H0' if rej else 'accept H0')
    out.append('P(Type I) = ' + sf3(act))
    out.append(w('H0: mu = ' + sf3(mu0) + ', X ~ Po(mu)'))
    out.append(w('level ' + fmt(pct) + '% so alpha = ' + sf3(a)))
    out.append(w('actual alpha = ' + sf3(act) + ' <= ' + sf3(a)))
    out.append(w('p = ' + sf3(p) + (' <= ' if p <= a else ' > ') +
                 sf3(a) + ' = alpha'))
    return out

def t_pois_up(mu0, obs, pct):
    return _pois_test(mu0, obs, pct, True)

def t_pois_lo(mu0, obs, pct):
    return _pois_test(mu0, obs, pct, False)

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
    out.append(w('n = ' + fmt(n) + ', s uses n-1'))
    out.append(w('Po(mu) has mean = variance = mu'))
    out.append(w('so mu estimate = xbar = ' + sf3(mean)))
    return out

# =============================================================================
# SC  Type I and Type II errors
# =============================================================================

def _region_line(lo, hi):
    parts = []
    if lo is not None:
        parts.append('X <= ' + fmt(lo))
    if hi is not None:
        parts.append('X >= ' + fmt(hi))
    if not parts:
        return 'critical region empty'
    return 'reject if ' + ' or '.join(parts)

def _region(lo, hi):
    if lo is None and hi is None:
        raise ValueError('need a critical region')
    if lo is not None:
        lo = _int(lo, 'lo')
    if hi is not None:
        hi = _int(hi, 'hi')
    if lo is not None and hi is not None and lo >= hi:
        raise ValueError('need lo < hi')
    return (lo, hi)

def _disc_tail(cdf, lo, hi, arg):
    # P(in the critical region) for a distribution given as a cdf function
    p = 0.0
    if lo is not None:
        p += cdf(arg, lo)
    if hi is not None:
        p += 1.0 - cdf(arg, hi - 1)
    if p < 0.0:
        p = 0.0
    if p > 1.0:
        p = 1.0
    return p

def _bin_cdf(np_, k):
    n, p = np_
    if k < 0:
        return 0.0
    return casutil.binom_cdf(n, p, k)

def _po_cdf(mu, k):
    if k < 0:
        return 0.0
    if k > 2000:
        return 1.0
    return casutil.poisson_cdf(mu, k)

def _bin_setup(n, p, name):
    n = _whole(n, 'n', 1, 500)
    if p <= 0 or p >= 1:
        raise ValueError(name + ' must be 0 to 1')
    return n

def _tail_lines(cdf, lo, hi, arg, out):
    if lo is not None:
        out.append(w('P(X<=' + fmt(lo) + ') = ' + sf3(cdf(arg, lo))))
    if hi is not None:
        out.append(w('P(X>=' + fmt(hi) + ') = ' +
                     sf3(1.0 - cdf(arg, hi - 1))))

def t_typeI_bin(n, p0, lo, hi):
    n = _bin_setup(n, p0, 'p0')
    lo, hi = _region(lo, hi)
    a = _disc_tail(_bin_cdf, lo, hi, (n, p0))
    out = [_region_line(lo, hi),
           'P(Type I) = ' + sf3(a),
           'as a % = ' + sf3(a * 100.0) + '%',
           w('X ~ B(' + fmt(n) + ', ' + sf3(p0) + ') under H0'),
           w('alpha = P(reject H0 | H0 true)')]
    _tail_lines(_bin_cdf, lo, hi, (n, p0), out)
    out.append(w('alpha = ' + sf3(a) + ', at most the set level'))
    return out

def t_typeII_bin(n, p0, lo, hi, p1):
    n = _bin_setup(n, p0, 'p0')
    if p1 <= 0 or p1 >= 1:
        raise ValueError('p1 must be 0 to 1')
    lo, hi = _region(lo, hi)
    a = _disc_tail(_bin_cdf, lo, hi, (n, p0))
    pw = _disc_tail(_bin_cdf, lo, hi, (n, p1))
    b = 1.0 - pw
    return [_region_line(lo, hi),
            'P(Type II) = ' + sf3(b),
            'power = ' + sf3(pw),
            'P(Type I) = ' + sf3(a),
            w('B(' + fmt(n) + ', ' + sf3(p0) + ') under H0'),
            w('B(' + fmt(n) + ', ' + sf3(p1) + ') is the truth'),
            w('beta = P(accept H0 | p = ' + sf3(p1) + ')'),
            w('power = 1 - beta = ' + sf3(pw))]

def t_typeI_pois(mu0, lo, hi):
    _mu(mu0, 'mu0')
    lo, hi = _region(lo, hi)
    a = _disc_tail(_po_cdf, lo, hi, mu0)
    out = [_region_line(lo, hi),
           'P(Type I) = ' + sf3(a),
           'as a % = ' + sf3(a * 100.0) + '%',
           w('X ~ Po(' + sf3(mu0) + ') under H0'),
           w('alpha = P(X in critical region)')]
    _tail_lines(_po_cdf, lo, hi, mu0, out)
    out.append(w('alpha = ' + sf3(a) + ', at most the set level'))
    return out

def t_typeII_pois(mu0, lo, hi, mu1):
    _mu(mu0, 'mu0')
    _mu(mu1, 'mu1')
    lo, hi = _region(lo, hi)
    a = _disc_tail(_po_cdf, lo, hi, mu0)
    pw = _disc_tail(_po_cdf, lo, hi, mu1)
    b = 1.0 - pw
    return [_region_line(lo, hi),
            'P(Type II) = ' + sf3(b),
            'power = ' + sf3(pw),
            'P(Type I) = ' + sf3(a),
            w('Po(' + sf3(mu0) + ') under H0, true mu = ' + sf3(mu1)),
            w('beta = P(accept H0 | mu = ' + sf3(mu1) + ')'),
            w('power = 1 - beta = ' + sf3(pw))]

def _norm_tail(mu, se, c1, c2):
    p = 0.0
    if c1 is not None:
        p += casutil.phi((c1 - mu) / se)
    if c2 is not None:
        p += 1.0 - casutil.phi((c2 - mu) / se)
    if p < 0.0:
        p = 0.0
    if p > 1.0:
        p = 1.0
    return p

def _norm_setup(sigma, n, c1, c2):
    _pos(sigma, 'sigma')
    n = _whole(n, 'n', 1, 1000000)
    if c1 is None and c2 is None:
        raise ValueError('need a critical value')
    if c1 is not None and c2 is not None and c1 >= c2:
        raise ValueError('need c1 < c2')
    return (n, sigma / math.sqrt(n))

def t_typeI_norm(mu0, sigma, n, c1, c2):
    n, se = _norm_setup(sigma, n, c1, c2)
    a = _norm_tail(mu0, se, c1, c2)
    out = ['P(Type I) = ' + sf3(a),
           'as a % = ' + sf3(a * 100.0) + '%',
           w('Xbar ~ N(' + sf3(mu0) + ', sigma^2/n) under H0'),
           w('SE = sigma/sqrt(n) = ' + sf3(se))]
    if c1 is not None:
        out.append(w('z1 = (' + sf3(c1) + '-' + sf3(mu0) + ')/SE = ' +
                     sf3((c1 - mu0) / se)))
    if c2 is not None:
        out.append(w('z2 = (' + sf3(c2) + '-' + sf3(mu0) + ')/SE = ' +
                     sf3((c2 - mu0) / se)))
    out.append(w('alpha = P(Xbar in critical region)'))
    return out

def t_typeII_norm(mu0, sigma, n, c1, c2, mu1):
    n, se = _norm_setup(sigma, n, c1, c2)
    a = _norm_tail(mu0, se, c1, c2)
    pw = _norm_tail(mu1, se, c1, c2)
    b = 1.0 - pw
    return ['P(Type II) = ' + sf3(b),
            'power = ' + sf3(pw),
            'P(Type I) = ' + sf3(a),
            w('SE = sigma/sqrt(n) = ' + sf3(se)),
            w('true mean ' + sf3(mu1) + ', H0 mean ' + sf3(mu0)),
            w('beta = P(accept H0 | mu = ' + fmt(mu1) + ')'),
            w('power = 1 - beta = ' + sf3(pw))]

# =============================================================================
# SD  Continuous random variables
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

def _quantile(pieces, p):
    lo = pieces[0][1]
    hi = pieces[len(pieces) - 1][2]
    i = 0
    while i < 40:
        mid = 0.5 * (lo + hi)
        v = _cdfat(pieces, mid)
        if v is None:
            return None
        if v < p:
            lo = mid
        else:
            hi = mid
        i += 1
    return 0.5 * (lo + hi)

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

def t_pdf(f, a, b):
    pieces = [_piece(f, a, b)]
    chk = _validity(pieces)
    e1, x1 = _moment(pieces, 1)
    e2, x2 = _moment(pieces, 2)
    if e1 is None or e2 is None:
        raise ValueError('cannot integrate x*f(x)')
    var = e2 - e1 * e1
    out = ['E(X) = ' + fmt(e1),
           'E(X^2) = ' + fmt(e2),
           'Var(X) = ' + fmt(var),
           'SD = ' + sf3(_sqrt(var))]
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
    out.append(w('f(x) = dF/dx'))
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
        ex = True
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
        out.append(w('P = (overlap)/(b-a) = ' + fmt(hi - lo) + '/' +
                     fmt(b - a)))
    out.append(w('E(X) = int x/(b-a) dx = (b^2-a^2)/2(b-a)'))
    out.append(w('     = (a+b)/2'))
    out.append(w('E(X^2) = (b^3-a^3)/3(b-a)'))
    out.append(w('Var = E(X^2)-E(X)^2 = (b-a)^2/12'))
    return out

def t_sumxy(mx, vx, my, vy):
    if vx < 0 or vy < 0:
        raise ValueError('variances must be >= 0')
    return ['E(X+Y) = ' + fmt(mx + my),
            'Var(X+Y) = ' + fmt(vx + vy),
            'E(X-Y) = ' + fmt(mx - my),
            'Var(X-Y) = ' + fmt(vx + vy),
            'SD(X+Y) = ' + sf3(_sqrt(vx + vy)),
            w('X and Y assumed independent'),
            w('Var(X-Y) adds the variances too'),
            w('Var = ' + fmt(vx) + ' + ' + fmt(vy) + ' = ' + fmt(vx + vy))]

# =============================================================================
# SE  Chi squared tests for association
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
    i = 0
    while i < r:
        s = 0.0
        j = 0
        while j < c:
            s += obs[i][j]
            j += 1
        rowt.append(s)
        i += 1
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

def _exp_lines(r, c, exp, rowt, colt, tot, out, rows=True):
    out.append(w('E = row total * col total / N'))
    out.append(w('N = ' + fmt(tot)))
    i = 0
    while rows and i < r:
        out.append(w('E r' + fmt(i + 1) + ': ' +
                     ' '.join([sf3(v) for v in exp[i]])))
        i += 1
    out.append(w('row totals: ' + ' '.join([fmt(v) for v in rowt])))
    out.append(w('col totals: ' + ' '.join([fmt(v) for v in colt])))
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
    return small

def t_assoc(rows, cols, data):
    r, c, obs, exp, rowt, colt, tot = _table(rows, cols, data)
    yates = (r == 2 and c == 2)
    chi = 0.0
    bi = 0
    bj = 0
    bc = -1.0
    i = 0
    while i < r:
        j = 0
        while j < c:
            d = obs[i][j] - exp[i][j]
            ad = d if d >= 0 else -d
            if yates:
                ad = ad - 0.5
            con = ad * ad / exp[i][j]
            chi += con
            if con > bc:
                bc = con
                bi = i
                bj = j
            j += 1
        i += 1
    df = (r - 1) * (c - 1)
    p = _chi2_sf(chi, df)
    c5 = tables.chi_crit(df, 0.05)
    c1 = tables.chi_crit(df, 0.01)
    out = ['chi^2 = ' + sf3(chi), 'df = ' + fmt(df)]
    if c5 is None:
        out.append(warn('no chi table entry for df = ' + fmt(df)))
        out.append(_pfmt(p))
        out.append('association at 5%' if p <= 0.05
                   else 'no association at 5%')
    else:
        out.append('5% crit = ' + sf3(c5))
        if c1 is not None:
            out.append('1% crit = ' + sf3(c1))
        out.append(_pfmt(p))
        if chi > c5:
            out.append('reject H0: association')
        else:
            out.append('accept H0: no association')
    out.append('biggest cell r' + fmt(bi + 1) + 'c' + fmt(bj + 1) +
               (' O>E' if obs[bi][bj] > exp[bi][bj] else ' O<E'))
    out.append(w('H0: no association between the'))
    out.append(w('    two factors'))
    out.append(w('df = (r-1)(c-1) = ' + fmt(df)))
    if yates:
        out.append(w('2x2 so Yates: (|O-E|-0.5)^2/E'))
    else:
        out.append(w('chi^2 = sum (O-E)^2/E = ' + sf3(chi)))
    out.append(w('largest (O-E)^2/E = ' + sf3(bc) + ' at r' +
                 fmt(bi + 1) + 'c' + fmt(bj + 1)))
    _exp_lines(r, c, exp, rowt, colt, tot, out)
    return out

def t_expected(rows, cols, data):
    r, c, obs, exp, rowt, colt, tot = _table(rows, cols, data)
    out = ['expected frequencies:']
    i = 0
    while i < r:
        out.append('r' + fmt(i + 1) + ': ' +
                   ' '.join([sf3(v) for v in exp[i]]))
        i += 1
    _exp_lines(r, c, exp, rowt, colt, tot, out, False)
    return out

def t_chistat(chi, df, pct):
    if chi < 0:
        raise ValueError('chi^2 must be >= 0')
    df = _whole(df, 'df', 1, 1000)
    a = _level(pct, 'level%')
    cv = tables.chi_crit(df, a)
    p = _chi2_sf(chi, df)
    out = ['chi^2 = ' + sf3(chi), 'df = ' + fmt(df)]
    if cv is None:
        out.append(warn('no chi table entry for df = ' + fmt(df) +
                        ' at ' + fmt(pct) + '%'))
        out.append(_pfmt(p))
        out.append(_verdict(p, a, pct))
    else:
        out.append('crit = ' + sf3(cv))
        out.append(_pfmt(p))
        if chi > cv:
            out.append('reject H0 at ' + fmt(pct) + '%')
        else:
            out.append('accept H0 at ' + fmt(pct) + '%')
        out.append(w('chi^2 ' + ('>' if chi > cv else '<=') + ' crit = ' +
                     sf3(cv)))
    out.append(w('upper tail chi^2 test, df = ' + fmt(df)))
    return out

# =============================================================================
# SF  Exponential distribution
# =============================================================================

def t_exp(lam):
    _pos(lam, 'lambda')
    var = 1.0 / (lam * lam)
    return ['mean = 1/L = ' + sf3(1.0 / lam),
            'Var = 1/L^2 = ' + sf3(var),
            'SD = 1/L = ' + sf3(1.0 / lam),
            'median = ln2/L = ' + sf3(math.log(2.0) / lam),
            w('f(x) = L e^(-Lx), x >= 0, L = ' + sf3(lam)),
            w('F(x) = 1 - e^(-Lx)'),
            w('E(X) = int x L e^(-Lx) dx = 1/L (by parts)'),
            w('E(X^2) = 2/L^2, so Var = 2/L^2-1/L^2 = 1/L^2'),
            w('F(m) = 0.5 gives m = ln2/L')]

def t_expp(lam, a, b):
    _pos(lam, 'lambda')
    if a < 0:
        raise ValueError('a must be >= 0')
    fa = 1.0 - math.exp(-lam * a)
    out = ['P(X<a) = ' + sf3(fa),
           'P(X>a) = ' + sf3(1.0 - fa)]
    if b is not None:
        if b < a:
            raise ValueError('need b >= a')
        fb = 1.0 - math.exp(-lam * b)
        out.append('P(a<X<b) = ' + sf3(fb - fa))
        out.append(w('= F(b)-F(a) = ' + sf3(fb) + '-' + sf3(fa)))
    out.append(w('F(x) = 1-e^(-Lx), L = ' + sf3(lam)))
    out.append(w('F(' + sf3(a) + ') = 1-e^(' + sf3(-lam * a) + ') = ' +
                 sf3(fa)))
    return out

def t_exprate(rate, t):
    _pos(rate, 'rate')
    if t < 0:
        raise ValueError('t must be >= 0')
    mu = rate * t
    p0 = math.exp(-mu)
    return ['T ~ Exp(' + sf3(rate) + ')',
            'P(T>t) = ' + sf3(p0),
            'P(T<t) = ' + sf3(1.0 - p0),
            'mean wait = ' + sf3(1.0 / rate),
            w('events ~ Po(' + sf3(rate) + ') per unit'),
            w('in time t = ' + sf3(t) + ', mu = rate*t = ' + sf3(mu)),
            w('P(T>t) = P(0 events) = e^(-mu) = ' + sf3(p0)),
            w('so waits between events are Exp(rate)')]

def t_memory(lam, s, t):
    _pos(lam, 'lambda')
    if s < 0 or t < 0:
        raise ValueError('s and t must be >= 0')
    ps = math.exp(-lam * s)
    pst = math.exp(-lam * (s + t))
    pt = math.exp(-lam * t)
    return ['P(X>s) = ' + sf3(ps),
            'P(X>s+t) = ' + sf3(pst),
            'P(X>s+t|X>s) = ' + sf3(pst / ps),
            'P(X>t) = ' + sf3(pt),
            'equal: memoryless',
            w('P(X>s+t|X>s) = P(X>s+t)/P(X>s)'),
            w('= e^(-L(s+t))/e^(-Ls) = e^(-Lt) = P(X>t)'),
            w('waiting s already has no effect')]

# =============================================================================
# SG  Inference, one sample t
# =============================================================================

def _ttest(n, xbar, s, mu0, pct, tail):
    n = _whole(n, 'n', 2, 5000)
    if s <= 0:
        raise ValueError('s must be > 0')
    tail = _int(tail, 'tail')
    if tail != 1 and tail != 2:
        raise ValueError('tail must be 1 or 2')
    a = _level(pct, 'level%')
    df = n - 1
    se = s / math.sqrt(n)
    t = (xbar - mu0) / se
    at = t if t >= 0 else -t
    p1 = _t_sf(at, df)
    p = 2.0 * p1 if tail == 2 else p1
    tc, tabled = _tstar(df, a / 2.0 if tail == 2 else a)
    out = ['t = ' + sf3(t), 'df = ' + fmt(df),
           'crit = ' + ('+/-' if tail == 2 else '') + sf3(tc),
           _pfmt(p)]
    out.append('reject H0 at ' + fmt(pct) + '%' if at > tc
               else 'accept H0 at ' + fmt(pct) + '%')
    if not tabled:
        out.append(warn('t table has no ' + fmt(pct) +
                        '% entry: value computed'))
    out.append(w('H0: mu = ' + sf3(mu0)))
    if tail == 2:
        out.append(w('H1: mu is not ' + sf3(mu0) + ' (2 tail)'))
    elif t >= 0:
        out.append(w('H1: mu > ' + sf3(mu0) + ' (1 tail)'))
    else:
        out.append(w('H1: mu < ' + sf3(mu0) + ' (1 tail)'))
    out.append(w('xbar = ' + sf3(xbar) + ', s = ' + sf3(s) +
                 ', n = ' + fmt(n)))
    out.append(w('SE = s/sqrt(n) = ' + sf3(se)))
    out.append(w('t = (xbar-mu0)/SE = (' + sf3(xbar) + '-' + sf3(mu0) +
                 ')/' + sf3(se)))
    out.append(w('t = ' + sf3(t) + ', df = n-1 = ' + fmt(df)))
    if tail == 1:
        out.append(w('1 tail: H1 follows the sign of t'))
    out.append(w('sigma unknown, estimated by s, so t'))
    return out

def t_ttest_data(mu0, pct, tail, data):
    n, mean, s = _mean_sd(data)
    return _ttest(n, mean, s, mu0, pct, tail)

def t_ttest_sum(n, xbar, s, mu0, pct, tail):
    return _ttest(_int(n, 'n'), xbar, s, mu0, pct, tail)

# =============================================================================
# SH  Confidence intervals
# =============================================================================

def _ci_lines(centre, half, out):
    out.insert(0, '(' + sf3(centre - half) + ', ' + sf3(centre + half) + ')')
    out.insert(1, 'centre ' + sf3(centre) + ' +/- ' + sf3(half))

def t_ci_z(xbar, sigma, n, pct):
    _pos(sigma, 'sigma')
    n = _whole(n, 'n', 1, 1000000)
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    z, tabled = _zstar(tp)
    se = sigma / math.sqrt(n)
    half = z * se
    out = []
    _ci_lines(xbar, half, out)
    out.append('z* = ' + sf3(z))
    if not tabled:
        out.append(warn('z table has no ' + fmt(pct) +
                        '% entry: value computed'))
    out.append(w('sigma known so z, not t'))
    out.append(w('tail p = ' + sf3(tp) + ', z* = ' + sf3(z)))
    out.append(w('SE = sigma/sqrt(n) = ' + sf3(se)))
    out.append(w('xbar +/- z*SE = ' + sf3(xbar) + ' +/- ' + sf3(half)))
    return out

def _ci_unknown(n, xbar, s, pct):
    n = _whole(n, 'n', 2, 5000)
    if s <= 0:
        raise ValueError('s must be > 0')
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    se = s / math.sqrt(n)
    out = []
    if n >= 30:
        k, tabled = _zstar(tp)
        note = 'z* = ' + sf3(k)
        why = w('n >= 30 so z with s for sigma')
    else:
        k, tabled = _tstar(n - 1, tp)
        note = 't* = ' + sf3(k) + ' (df ' + fmt(n - 1) + ')'
        why = w('n < 30 and sigma unknown so t, df = ' + fmt(n - 1))
    half = k * se
    _ci_lines(xbar, half, out)
    out.append(note)
    if not tabled:
        out.append(warn('table has no ' + fmt(pct) +
                        '% entry: value computed'))
    out.append(why)
    out.append(w('xbar = ' + sf3(xbar) + ', s = ' + sf3(s) +
                 ', n = ' + fmt(n)))
    out.append(w('SE = s/sqrt(n) = ' + sf3(se)))
    out.append(w('xbar +/- k*SE = ' + sf3(xbar) + ' +/- ' + sf3(half)))
    return out

def t_ci_data(pct, data):
    n, mean, s = _mean_sd(data)
    return _ci_unknown(n, mean, s, pct)

def t_ci_sum(n, xbar, s, pct):
    return _ci_unknown(_int(n, 'n'), xbar, s, pct)

def t_ci_in(lo, hi, mu0):
    if hi <= lo:
        raise ValueError('need hi > lo')
    centre = 0.5 * (lo + hi)
    half = 0.5 * (hi - lo)
    inside = lo <= mu0 <= hi
    return ['centre = ' + sf3(centre),
            'half width = ' + sf3(half),
            'width = ' + sf3(hi - lo),
            'mu0 ' + ('inside' if inside else 'outside') + ' the interval',
            'accept H0' if inside else 'reject H0',
            w('mu0 = ' + sf3(mu0) + ', CI = (' + sf3(lo) + ', ' +
              sf3(hi) + ')'),
            w('a C% CI holds every mu0 not rejected'),
            w('by a 2 tail test at the (100-C)% level')]

def t_ci_n(sigma, width, pct):
    if isinstance(width, complex) or isinstance(sigma, complex):
        raise ValueError('inputs must be real')
    _pos(sigma, 'sigma')
    _pos(width, 'width')
    cl = _level(pct, 'conf%')
    tp = (1.0 - cl) / 2.0
    z, tabled = _zstar(tp)
    exact = (2.0 * z * sigma / width) ** 2
    n = int(math.ceil(exact))
    if n < 1:
        n = 1
    out = ['n = ' + fmt(n),
           'z* = ' + sf3(z),
           'exact n = ' + sf3(exact)]
    if not tabled:
        out.append(warn('z table has no ' + fmt(pct) +
                        '% entry: value computed'))
    out.append(w('full width = 2 z sigma/sqrt(n) <= ' + sf3(width)))
    out.append(w('sqrt(n) >= 2 z sigma/width = ' + sf3(2.0 * z * sigma /
                                                       width)))
    out.append(w('n >= ' + sf3(exact) + ', round up'))
    return out

# =============================================================================

SECTIONS = [
    ('SA', 'Discrete random variables', [
        ('DRV from table', 'data*', t_drv),
        ('DRV from formula', 'p(x),n', t_drvf),
        ('E and Var of aX+b', 'a,b,mean,var', t_linear),
        ('E of g(X) from table', 'g(x),data*', t_egx),
        ('Discrete uniform 1-n', 'n', t_dunif),
    ]),
    ('SB', 'Poisson distribution', [
        ('Poisson P(X=k)', 'mu,k', t_pois),
        ('Poisson a<=X<=b', 'mu,a,b', t_poisrange),
        ('Poisson inverse', 'mu,p', t_poisinv),
        ('Sum of Poissons', 'k,mu*', t_poissum),
        ('Poisson test upper', 'mu0,obs,level%', t_pois_up),
        ('Poisson test lower', 'mu0,obs,level%', t_pois_lo),
        ('Poisson model check', 'data*', t_poischeck),
    ]),
    ('SC', 'Type I and Type II errors', [
        ('Type I binomial', 'n,p0,lo,hi?', t_typeI_bin),
        ('Type II binomial', 'n,p0,lo,hi,p1', t_typeII_bin),
        ('Type I Poisson', 'mu0,lo,hi?', t_typeI_pois),
        ('Type II Poisson', 'mu0,lo,hi,mu1', t_typeII_pois),
        ('Type I Normal', 'mu0,sigma,n,c1,c2?', t_typeI_norm),
        ('Type II Normal', 'mu0,sigma,n,c1,c2,mu1', t_typeII_norm),
    ]),
    ('SD', 'Continuous random vars', [
        ('pdf E Var and check', 'f(x),a,b', t_pdf),
        ('pdf median quartiles', 'f(x),a,b', t_pdfq),
        ('Mode of a pdf', 'f(x),a,b', t_pdfmode),
        ('cdf F(x) from a pdf', 'f(x),a,b,t', t_cdf),
        ('pdf P(c<X<d)', 'f(x),a,b,c,d', t_pdfp),
        ('E of g(X) from a pdf', 'g(x),f(x),a,b', t_pdfg),
        ('Piecewise pdf', 'f(x),g(x),a,b,c', t_pdfpw),
        ('Rectangular U(a,b)', 'a,b,c?,d?', t_rect),
        ('E and Var of aX+b', 'a,b,mean,var', t_linear),
        ('E and Var of X+Y', 'mx,vx,my,vy', t_sumxy),
    ]),
    ('SE', 'Chi squared association', [
        ('Chi-sq association', 'rows,cols,data*', t_assoc),
        ('Expected frequencies', 'rows,cols,data*', t_expected),
        ('Chi-sq from statistic', 'chi2,df,level%', t_chistat),
    ]),
    ('SF', 'Exponential distribution', [
        ('Exponential Exp(L)', 'lambda', t_exp),
        ('Exponential probs', 'lambda,a,b?', t_expp),
        ('Waits from a rate', 'rate,t', t_exprate),
        ('Memoryless check', 'lambda,s,t', t_memory),
    ]),
    ('SG', 'Inference one sample t', [
        ('t-test from data', 'mu0,level%,tail,data*', t_ttest_data),
        ('t-test from summary', 'n,xbar,s,mu0,level%,tail', t_ttest_sum),
    ]),
    ('SH', 'Confidence intervals', [
        ('CI mean sigma known', 'xbar,sigma,n,conf%', t_ci_z),
        ('CI from data', 'conf%,data*', t_ci_data),
        ('CI from summary', 'n,xbar,s,conf%', t_ci_sum),
        ('Is mu0 in the CI', 'lo,hi,mu0', t_ci_in),
        ('Sample size for width', 'sigma,width,conf%', t_ci_n),
    ]),
]
