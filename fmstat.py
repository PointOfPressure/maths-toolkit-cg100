import math
import casui
import caseng
import cascalc
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show
_ncr = casutil.ncr
_erf = casutil.erf
_phi = casutil.phi
_invphi = casutil.invphi
_poispmf = casutil.poisson_pmf
_binpmf = casutil.binom_pmf

def _asklist(prompt):
    # this module treats "nothing entered" as a cancel
    v = casutil.asklist(prompt)
    if not v:
        return None
    return v

# ------------------------------------------------- sampling distributions --
# The normal distribution itself is NOT re-implemented here: phi/invphi/erf
# come from casutil, which is the single copy. What follows is the chi-squared
# and Student t machinery, which casutil does not carry.

def _chi2_sf(x, k):
    # P(X > x) for chi-squared on k degrees of freedom, from the standard
    # two-step recurrence
    #   Q(x,k) = Q(x,k-2) + (x/2)^((k-2)/2) e^(-x/2) / Gamma(k/2),
    # started at Q(x,1) = 2(1-phi(sqrt x)) and Q(x,2) = e^(-x/2). Successive
    # terms satisfy t(k+2) = t(k) * x/k, so no gamma function is ever needed.
    if k < 1:
        return 1.0
    if x <= 0.0:
        return 1.0
    if x > 1500.0:
        return 0.0          # e^(-x/2) has underflowed to zero anyway
    if k % 2 == 0:
        q = math.exp(-x / 2.0)
        t = (x / 2.0) * q                                   # the k = 4 term
        j = 4
    else:
        q = 2.0 * (1.0 - _phi(math.sqrt(x)))
        t = math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0)   # the k = 3 term
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

def _chi2_crit(k, a):
    # upper-tail critical value: the x with P(X > x) = a. Bisection is safe
    # because the survivor function is strictly decreasing in x.
    lo = 0.0
    hi = 4.0
    i = 0
    while i < 200 and _chi2_sf(hi, k) > a:
        hi *= 2.0
        i += 1
    i = 0
    while i < 80:
        m = 0.5 * (lo + hi)
        if _chi2_sf(m, k) > a:
            lo = m
        else:
            hi = m
        i += 1
    return 0.5 * (lo + hi)

def _t_sf(t, v):
    # P(T > t) on v degrees of freedom, from the classic finite-sum expression
    # for A(t|v) = P(-t < T < t) with theta = atan(t/sqrt(v)). Exact for every
    # integer v, and no gamma function or continued fraction is involved.
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

def _t_crit(v, a):
    # one-tail critical value of t on v degrees of freedom
    lo = 0.0
    hi = 4.0
    i = 0
    while i < 200 and _t_sf(hi, v) > a:
        hi *= 2.0
        i += 1
    i = 0
    while i < 80:
        m = 0.5 * (lo + hi)
        if _t_sf(m, v) > a:
            lo = m
        else:
            hi = m
        i += 1
    return 0.5 * (lo + hi)

# --- tools ---

def t_drv():
    xs = _asklist('Values x (csv):')
    if xs is None:
        return
    ps = _asklist('Probs P(X=x):')
    if ps is None:
        return
    if len(xs) != len(ps):
        _show('Discrete RV', ['Lists differ in length'])
        return
    sp = sum(ps)
    ex = 0.0
    ex2 = 0.0
    i = 0
    while i < len(xs):
        ex += xs[i] * ps[i]
        ex2 += xs[i] * xs[i] * ps[i]
        i += 1
    var = ex2 - ex * ex
    sd = math.sqrt(var) if var > 0 else 0.0
    _show('Discrete RV', ['Sum P = ' + _fn(sp), 'E[X] = ' + _fn(ex), 'E[X^2] = ' + _fn(ex2), 'Var[X] = ' + _fn(var), 'SD = ' + _fn(sd)])

def t_pois():
    mu = _asknum('mean mu:')
    if mu is None or mu <= 0:
        return
    k = _askint('value k:')
    if k is None or k < 0:
        return
    pmf = _poispmf(mu, k)
    cdf = casutil.poisson_cdf(mu, k)   # one pass, not k passes
    _show('Poisson', ['mu = ' + _fn(mu) + '  k = ' + str(k),
                      'P(X=k) = ' + _fn(pmf),
                      'P(X<=k) = ' + _fn(cdf),
                      'P(X>=k) = ' + _fn(1.0 - cdf + pmf),
                      'mean = ' + _fn(mu),
                      'variance = ' + _fn(mu),
                      '(Poisson mean = variance)',
                      'SD = ' + _fn(math.sqrt(mu))])

def t_bin():
    n = _askint('n trials:')
    if n is None or n < 0:
        return
    p = _asknum('p success:')
    if p is None or p < 0 or p > 1:
        return
    k = _askint('value k:')
    if k is None or k < 0 or k > n:
        return
    if n > 5000:
        _show('Binomial', ['n too large (max 5000).'])
        return
    pmf = _binpmf(n, p, k)
    cdf = casutil.binom_cdf(n, p, k)
    lines = ['n=' + str(n) + ' p=' + _fn(p) + ' k=' + str(k),
             'P(X=k) = ' + _fn(pmf),
             'P(X<=k) = ' + _fn(cdf),
             'P(X>=k) = ' + _fn(1.0 - cdf + pmf),
             'mean np = ' + _fn(n * p),
             'var npq = ' + _fn(n * p * (1.0 - p))]
    # when n is large and p small the Poisson with mu = np is the standard
    # approximation; say so only when the usual conditions actually hold
    if n >= 50 and p <= 0.1:
        mu = n * p
        lines.append('n>=50, p<=0.1 so Poisson')
        lines.append(' approx with mu = np = ' + _fn(mu))
        lines.append('Pois P(X=k) = ' + _fn(_poispmf(mu, k)))
        lines.append('Pois P(X<=k) = ' + _fn(casutil.poisson_cdf(mu, k)))
    _show('Binomial', lines)

def t_geom():
    p = _asknum('p success:')
    if p is None or p <= 0 or p > 1:
        _show('Geometric', ['Need 0 < p <= 1'])
        return
    r = _askint('value r (>=1):')
    if r is None or r < 1:
        return
    q = 1.0 - p
    pmf = q ** (r - 1) * p
    upto = 1.0 - q ** r
    _show('Geometric', ['X = trial of 1st success',
                        'p = ' + _fn(p) + '  r = ' + str(r),
                        'P(X=r) = (1-p)^(r-1) p',
                        'P(X=r) = ' + _fn(pmf),
                        'P(X<=r) = 1-(1-p)^r',
                        'P(X<=r) = ' + _fn(upto),
                        'P(X>r) = (1-p)^r',
                        'P(X>r) = ' + _fn(q ** r),
                        'mean 1/p = ' + _fn(1.0 / p),
                        'var (1-p)/p^2 = ' + _fn(q / (p * p)),
                        'SD = ' + _fn(math.sqrt(q / (p * p)))])

def t_dunif():
    a = _askint('lowest value a:')
    if a is None:
        return
    b = _askint('highest value b:')
    if b is None or b < a:
        _show('Discrete uniform', ['Need b >= a'])
        return
    n = b - a + 1
    mean = (a + b) / 2.0
    var = (n * n - 1) / 12.0
    _show('Discrete uniform', ['X uniform on ' + str(a) + '..' + str(b),
                               'n values = ' + str(n),
                               'P(X=x) = 1/n = ' + _fn(1.0 / n),
                               'mean (a+b)/2 = ' + _fn(mean),
                               'var (n^2-1)/12 = ' + _fn(var),
                               'SD = ' + _fn(math.sqrt(var))])

def t_normplot():
    xs = _asklist('Data list:')
    if xs is None or len(xs) < 3:
        _show('Normal plot', ['Need at least 3 values.'])
        return
    n = len(xs)
    srt = list(xs)
    srt.sort()
    # plot the ordered data against the normal scores z_i = invphi((i-0.5)/n);
    # points close to a straight line support a normal model
    zs = []
    i = 0
    while i < n:
        zs.append(_invphi((i + 0.5) / n))
        i += 1
    m, _sx, _sy, Sxy, Sxx, Syy = _stats2(zs, srt)
    lines = ['n = ' + str(n), 'z_i = invphi((i-0.5)/n)']
    if Sxx > 0 and Syy > 0:
        r = Sxy / math.sqrt(Sxx * Syy)
        b = Sxy / Sxx
        a = _sy / n - b * _sx / n
        lines.append('r of plot = ' + _fn(r))
        lines.append('slope ~ sd = ' + _fn(b))
        lines.append('intercept ~ mean = ' + _fn(a))
        if r > 0.99:
            lines.append('very close to a line:')
            lines.append(' Normal looks reasonable')
        elif r > 0.96:
            lines.append('fairly close to a line')
        else:
            lines.append('clearly curved: Normal')
            lines.append(' looks doubtful')
    _show('Normal plot', lines)
    xlo, xhi = casutil.nice_range(zs)
    ylo, yhi = casutil.nice_range(srt)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'Normal probability plot', 'z score', 'data')
    i = 0
    while i < n:
        casutil.marker(fr, zs[i], srt[i], casui.BLACK, 2)
        i += 1
    if Sxx > 0:
        b = Sxy / Sxx
        a = _sy / n - b * _sx / n
        casutil.seg(fr, xlo, a + b * xlo, xhi, a + b * xhi, casui.ACC)
    casutil.chart_hold('EXIT to go back')

def t_norm():
    mu = _asknum('mean mu:')
    if mu is None:
        return
    sg = _asknum('SD sigma:')
    if sg is None or sg <= 0:
        return
    a = _asknum('lower a:')
    if a is None:
        return
    b = _asknum('upper b:')
    if b is None:
        return
    za = (a - mu) / sg
    zb = (b - mu) / sg
    pr = _phi(zb) - _phi(za)
    _show('Normal P(a<X<b)', ['mu=' + _fn(mu) + ' sigma=' + _fn(sg), 'z(a) = ' + _fn(za), 'z(b) = ' + _fn(zb), 'P(a<X<b) = ' + _fn(pr)])

def t_std():
    mu = _asknum('mean mu:')
    if mu is None:
        return
    sg = _asknum('SD sigma:')
    if sg is None or sg <= 0:
        return
    x = _asknum('value x:')
    if x is None:
        return
    z = (x - mu) / sg
    _show('Standardise', ['z = (x-mu)/sigma', 'z = ' + _fn(z), 'P(X<x) = ' + _fn(_phi(z)), 'P(X>x) = ' + _fn(1.0 - _phi(z))])

def t_inv():
    mu = _asknum('mean mu:')
    if mu is None:
        return
    sg = _asknum('SD sigma:')
    if sg is None or sg <= 0:
        return
    p = _asknum('prob P(X<x):')
    if p is None or p <= 0 or p >= 1:
        return
    z = _invphi(p)
    x = mu + z * sg
    _show('Inverse Normal', ['P(X<x) = ' + _fn(p), 'z = ' + _fn(z), 'x = ' + _fn(x)])

def _stats2(xs, ys):
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxy = 0.0
    sxx = 0.0
    syy = 0.0
    i = 0
    while i < n:
        sxy += xs[i] * ys[i]
        sxx += xs[i] * xs[i]
        syy += ys[i] * ys[i]
        i += 1
    Sxy = sxy - sx * sy / n
    Sxx = sxx - sx * sx / n
    Syy = syy - sy * sy / n
    return n, sx, sy, Sxy, Sxx, Syy

# One-tail critical values of the pmcc, rows n = 4 to 30, columns
# 5%, 2.5%, 1%, 0.5%. Under H0 (no correlation, bivariate normal) the exact
# relation is r = t / sqrt(t^2 + n - 2) with t the critical value of Student's
# t on n - 2 degrees of freedom, and this table was generated from that
# identity; it agrees to 4 d.p. with the printed pmcc table at every n checked.
_RCRIT_MIN = 4
_RCRIT = [
    (0.9000, 0.9500, 0.9800, 0.9900),   # n = 4
    (0.8054, 0.8783, 0.9343, 0.9587),   # n = 5
    (0.7293, 0.8114, 0.8822, 0.9172),   # n = 6
    (0.6694, 0.7545, 0.8329, 0.8745),   # n = 7
    (0.6215, 0.7067, 0.7887, 0.8343),   # n = 8
    (0.5822, 0.6664, 0.7498, 0.7977),   # n = 9
    (0.5494, 0.6319, 0.7155, 0.7646),   # n = 10
    (0.5214, 0.6021, 0.6851, 0.7348),   # n = 11
    (0.4973, 0.5760, 0.6581, 0.7079),   # n = 12
    (0.4762, 0.5529, 0.6339, 0.6835),   # n = 13
    (0.4575, 0.5324, 0.6120, 0.6614),   # n = 14
    (0.4409, 0.5140, 0.5923, 0.6411),   # n = 15
    (0.4259, 0.4973, 0.5742, 0.6226),   # n = 16
    (0.4124, 0.4821, 0.5577, 0.6055),   # n = 17
    (0.4000, 0.4683, 0.5425, 0.5897),   # n = 18
    (0.3887, 0.4555, 0.5285, 0.5751),   # n = 19
    (0.3783, 0.4438, 0.5155, 0.5614),   # n = 20
    (0.3687, 0.4329, 0.5034, 0.5487),   # n = 21
    (0.3598, 0.4227, 0.4921, 0.5368),   # n = 22
    (0.3515, 0.4132, 0.4815, 0.5256),   # n = 23
    (0.3438, 0.4044, 0.4716, 0.5151),   # n = 24
    (0.3365, 0.3961, 0.4622, 0.5052),   # n = 25
    (0.3297, 0.3882, 0.4534, 0.4958),   # n = 26
    (0.3233, 0.3809, 0.4451, 0.4869),   # n = 27
    (0.3172, 0.3739, 0.4372, 0.4785),   # n = 28
    (0.3115, 0.3673, 0.4297, 0.4705),   # n = 29
    (0.3061, 0.3610, 0.4226, 0.4629),   # n = 30
]

# One-tail critical values of Spearman's rs, rows n = 4 to 30, same columns.
# rs has no closed form under H0 - these are the published exact-permutation
# table values. None marks a level that cannot be reached at that n at all
# (with n = 4 there are only 24 rankings, so the smallest one-tail probability
# is 1/24 = 0.0417 and nothing below 5% exists).
_SCRIT_MIN = 4
_SCRIT = [
    (1.0000, None,   None,   None),     # n = 4
    (0.9000, 1.0000, 1.0000, None),     # n = 5
    (0.8286, 0.8857, 0.9429, 1.0000),   # n = 6
    (0.7143, 0.7857, 0.8929, 0.9286),   # n = 7
    (0.6429, 0.7381, 0.8333, 0.8810),   # n = 8
    (0.6000, 0.7000, 0.7833, 0.8333),   # n = 9
    (0.5636, 0.6485, 0.7455, 0.7939),   # n = 10
    (0.5364, 0.6182, 0.7091, 0.7545),   # n = 11
    (0.5035, 0.5874, 0.6783, 0.7273),   # n = 12
    (0.4835, 0.5604, 0.6484, 0.6978),   # n = 13
    (0.4637, 0.5385, 0.6264, 0.6747),   # n = 14
    (0.4464, 0.5214, 0.6036, 0.6536),   # n = 15
    (0.4294, 0.5029, 0.5824, 0.6324),   # n = 16
    (0.4142, 0.4877, 0.5662, 0.6152),   # n = 17
    (0.3987, 0.4716, 0.5501, 0.5975),   # n = 18
    (0.3893, 0.4596, 0.5351, 0.5825),   # n = 19
    (0.3789, 0.4466, 0.5218, 0.5684),   # n = 20
    (0.3688, 0.4364, 0.5091, 0.5545),   # n = 21
    (0.3597, 0.4252, 0.4975, 0.5426),   # n = 22
    (0.3518, 0.4160, 0.4862, 0.5306),   # n = 23
    (0.3435, 0.4070, 0.4757, 0.5200),   # n = 24
    (0.3362, 0.3977, 0.4662, 0.5100),   # n = 25
    (0.3299, 0.3901, 0.4571, 0.5002),   # n = 26
    (0.3236, 0.3828, 0.4487, 0.4915),   # n = 27
    (0.3175, 0.3755, 0.4401, 0.4828),   # n = 28
    (0.3113, 0.3685, 0.4325, 0.4744),   # n = 29
    (0.3059, 0.3624, 0.4251, 0.4665),   # n = 30
]

# the one-tail levels the two tables above are indexed by
_CORR_A = [0.05, 0.025, 0.01, 0.005]

def _corr_col(a1):
    # column index for a one-tail level, or -1 if it is not a tabulated one
    i = 0
    while i < len(_CORR_A):
        if abs(a1 - _CORR_A[i]) < 1e-9:
            return i
        i += 1
    return -1

def _corr_test(lines, coef, name, n, tab, tabmin, alpha, tail, src):
    # shared critical-value comparison for both correlation coefficients
    a1 = alpha if tail != 3 else alpha / 2.0
    if tail == 1:
        lines.append('H1: positive correlation')
    elif tail == 2:
        lines.append('H1: negative correlation')
    else:
        lines.append('H1: some correlation')
    lines.append('H0: no correlation')
    lines.append('alpha = ' + _fn(alpha * 100.0) + '% ' +
                 ('2-tail' if tail == 3 else '1-tail'))
    lines.append('one-tail level used = ' + _fn(a1 * 100.0) + '%')
    col = _corr_col(a1)
    if col < 0:
        lines.append('No table column for that')
        lines.append(' level (5/2.5/1/0.5% only)')
        return
    idx = n - tabmin
    if idx < 0 or idx >= len(tab):
        lines.append('n = ' + str(n) + ' is outside the')
        lines.append(' table (' + str(tabmin) + ' to ' +
                     str(tabmin + len(tab) - 1) + ')')
        return
    cv = tab[idx][col]
    if cv is None:
        lines.append('That level is unreachable')
        lines.append(' with n = ' + str(n))
        return
    lines.append('crit ' + name + ' = ' + _fn(cv))
    lines.append(src)
    if tail == 1:
        rej = coef >= cv
        lines.append('reject if ' + name + ' >= ' + _fn(cv))
    elif tail == 2:
        rej = coef <= -cv
        lines.append('reject if ' + name + ' <= -' + _fn(cv))
    else:
        rej = abs(coef) >= cv
        lines.append('reject if |' + name + '| >= ' + _fn(cv))
    if rej:
        lines.append('REJECT H0: correlation')
        lines.append(' is significant')
    else:
        lines.append('accept H0: not significant')

def _ask_corr_test():
    # (alpha, tail) or (None, None) when the test is to be skipped
    al = _asknum('alpha % (blank skip test):')
    if al is None:
        return (None, None)
    if al <= 0 or al >= 100:
        return (None, None)
    tl = _askint('tail 1=pos 2=neg 3=two:')
    if tl is None or tl < 1 or tl > 3:
        return (None, None)
    return (al / 100.0, tl)

def t_pmcc():
    xs = _asklist('x values (csv):')
    if xs is None:
        return
    ys = _asklist('y values (csv):')
    if ys is None:
        return
    if len(xs) != len(ys):
        _show('PMCC', ['Lists differ in length'])
        return
    n, sx, sy, Sxy, Sxx, Syy = _stats2(xs, ys)
    if Sxx <= 0 or Syy <= 0:
        _show('PMCC', ['Zero variance'])
        return
    r = Sxy / math.sqrt(Sxx * Syy)
    alpha, tail = _ask_corr_test()
    lines = ['n = ' + str(n), 'Sxy = ' + _fn(Sxy), 'Sxx = ' + _fn(Sxx),
             'Syy = ' + _fn(Syy), 'r = ' + _fn(r), 'r^2 = ' + _fn(r * r)]
    if alpha is not None:
        if n < 3:
            lines.append('Need n >= 3 to test.')
        else:
            _corr_test(lines, r, 'r', n, _RCRIT, _RCRIT_MIN, alpha, tail,
                       '(pmcc table, = t/sqrt(t^2+n-2))')
            # the t statistic is the same test written the other way round,
            # and it works for any n, including past the end of the table
            if abs(r) < 1.0:
                tst = r * math.sqrt((n - 2) / (1.0 - r * r))
                p1 = _t_sf(abs(tst), n - 2)
                lines.append('t = r sqrt((n-2)/(1-r^2))')
                lines.append('t = ' + _fn(tst) + ' on ' + str(n - 2) + ' df')
                lines.append('p (1-tail) = ' + _fp(p1))
                lines.append('p (2-tail) = ' + _fp(2.0 * p1))
    _show('PMCC r', lines)
    # a scatter plot: correlation is meaningless without looking at the shape
    xlo, xhi = casutil.nice_range(xs)
    ylo, yhi = casutil.nice_range(ys)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'Scatter (r = ' + _fn(r) + ')', 'x', 'y')
    i = 0
    while i < n:
        casutil.marker(fr, xs[i], ys[i], casui.BLACK, 2)
        i += 1
    if Sxx > 0:
        b = Sxy / Sxx
        a = sy / n - b * sx / n
        casutil.seg(fr, xlo, a + b * xlo, xhi, a + b * xhi, casui.ACC)
    casutil.chart_hold('EXIT to go back')

def _ranks(v):
    # rank ascending, ties take the average rank. Sort (value, index)
    # pairs directly so we do not depend on sorted(key=...) support.
    n = len(v)
    pairs = []
    i = 0
    while i < n:
        pairs.append((v[i], i))
        i += 1
    pairs.sort()
    idx = [p[1] for p in pairs]
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

def t_spear():
    xs = _asklist('x values (csv):')
    if xs is None:
        return
    ys = _asklist('y values (csv):')
    if ys is None:
        return
    if len(xs) != len(ys):
        _show('Spearman', ['Lists differ in length'])
        return
    rx = _ranks(xs)
    ry = _ranks(ys)
    n, sx, sy, Sxy, Sxx, Syy = _stats2(rx, ry)
    if Sxx <= 0 or Syy <= 0:
        _show('Spearman', ['Tied to one rank'])
        return
    rs = Sxy / math.sqrt(Sxx * Syy)
    alpha, tail = _ask_corr_test()
    lines = ['n = ' + str(n), '(PMCC of ranks,', ' ties averaged)',
             'rs = ' + _fn(rs)]
    tied = False
    i = 0
    while i < n:
        if rx[i] != int(rx[i]) or ry[i] != int(ry[i]):
            tied = True
        i += 1
    if alpha is not None:
        _corr_test(lines, rs, 'rs', n, _SCRIT, _SCRIT_MIN, alpha, tail,
                   '(Spearman rs table, exact)')
        if tied:
            lines.append('NOTE: there are ties, so')
            lines.append(' the table is approximate')
    _show('Spearman rs', lines)

def t_reg():
    xs = _asklist('x values (csv):')
    if xs is None:
        return
    ys = _asklist('y values (csv):')
    if ys is None:
        return
    if len(xs) != len(ys):
        _show('Regression', ['Lists differ in length'])
        return
    n, sx, sy, Sxy, Sxx, Syy = _stats2(xs, ys)
    if Sxx <= 0:
        _show('Regression', ['Zero x variance'])
        return
    b = Sxy / Sxx
    a = sy / n - b * sx / n
    xv = _asknum('predict at x:')
    lines = ['y = a + b x', 'a = ' + _fn(a), 'b = ' + _fn(b)]
    if Syy > 0:
        r = Sxy / math.sqrt(Sxx * Syy)
        lines.append('r = ' + _fn(r))
        lines.append('r^2 = ' + _fn(r * r))
        # the OTHER least squares line, x on y. It minimises horizontal
        # distances, so it is the one to use when predicting x from y; the two
        # lines coincide only when r^2 = 1 and both pass through (xbar, ybar).
        d = Sxy / Syy
        cc = sx / n - d * sy / n
        lines.append('x on y: x = c + d y')
        lines.append('c = ' + _fn(cc))
        lines.append('d = ' + _fn(d))
        lines.append('use y on x to predict y,')
        lines.append(' x on y to predict x')
        lines.append('means point (' + _fn(sx / n) + ', ' + _fn(sy / n) + ')')
    if xv is not None:
        lines.append('at x=' + _fn(xv) + ': y=' + _fn(a + b * xv))
    # residuals y - (a + bx): the model-fit check the audit flagged as missing
    lines.append('residuals y-(a+bx):')
    i = 0
    ssr = 0.0
    while i < n:
        e = ys[i] - (a + b * xs[i])
        ssr += e * e
        if i < 10:
            lines.append(' x=' + _fn(xs[i]) + ' e=' + _fn(e))
        i += 1
    if n > 10:
        lines.append(' (first 10 of ' + str(n) + ')')
    lines.append('sum of e^2 = ' + _fn(ssr))
    _show('Least squares', lines)

def _fp(p):
    # a p-value rounded to 4 d.p. prints as plain "0" once it drops below
    # 5e-5, which reads as if the tail were empty. Say "< 0.0001" instead.
    if p < 0.0001:
        return '< 0.0001'
    return _fn(p)

def _signed(v, name):
    # "2X - 3Y" rather than "2X + -3Y"
    if v < 0:
        return ' - ' + _fn(-v) + name
    return ' + ' + _fn(v) + name

def _chi_verdict(lines, chi, df, a):
    # shared reporting for both chi-squared tools, so the goodness-of-fit test
    # and the association test can never disagree about the decision rule
    cv = _chi2_crit(df, a)
    p = _chi2_sf(chi, df)
    lines.append('alpha = ' + _fn(a * 100.0) + '%')
    lines.append('crit = ' + _fn(cv))
    lines.append('(chi^2 upper tail, df ' + str(df) + ')')
    lines.append('p-value = ' + _fp(p))
    if chi > cv:
        lines.append('chi^2 > crit: reject H0')
    else:
        lines.append('chi^2 <= crit: accept H0')

def t_chi():
    O = _asklist('Observed O (csv):')
    if O is None:
        return
    E = _asklist('Expected E (csv):')
    if E is None:
        return
    if len(O) != len(E):
        _show('Chi-squared', ['Lists differ in length'])
        return
    # The degrees of freedom are cells - 1 - (parameters estimated from the
    # data). This used to be hard-coded as cells - 1, which is right only when
    # the model is fully specified in advance; fitting a Poisson mean, or a
    # binomial p, or a normal mu and sigma from the sample costs one degree of
    # freedom each, and using the wrong df makes the whole test wrong. So ask.
    m = _askint('params estimated (0):')
    if m is None:
        m = 0                      # blank means "none estimated", the common case
    if m < 0:
        _show('Chi-squared', ['Params cannot be negative'])
        return
    al = _asknum('alpha % (5):')
    if al is None:
        al = 5.0
    if al <= 0 or al >= 100:
        _show('Chi-squared', ['Need 0 < alpha < 100'])
        return
    chi = 0.0
    i = 0
    while i < len(O):
        if E[i] <= 0:
            _show('Chi-squared', ['Expected has 0 cell'])
            return
        chi += (O[i] - E[i]) ** 2 / E[i]
        i += 1
    df = len(O) - 1 - m
    if df < 1:
        _show('Chi-squared GOF', ['cells = ' + str(len(O)),
                                  'params estimated = ' + str(m),
                                  'df = ' + str(df) + ' is not >= 1',
                                  'Too few cells for this',
                                  'many fitted parameters.'])
        return
    lines = ['cells = ' + str(len(O)),
             'params estimated = ' + str(m),
             'df = cells-1-params',
             'df = ' + str(df),
             'chi^2 = ' + _fn(chi)]
    small = 0
    i = 0
    while i < len(E):
        if E[i] < 5:
            small += 1
        i += 1
    if small:
        lines.append('WARN: ' + str(small) + ' cell(s) E<5;')
        lines.append(' pool classes first')
    _chi_verdict(lines, chi, df, al / 100.0)
    _show('Chi-squared GOF', lines)

def t_assoc():
    # chi-squared test for association in an r x c contingency table
    r = _askint('rows r (2-8):')
    if r is None or r < 2 or r > 8:
        return
    c = _askint('cols c (2-8):')
    if c is None or c < 2 or c > 8:
        return
    obs = []
    i = 0
    while i < r:
        row = _asklist('row ' + str(i + 1) + ' (' + str(c) + ' values):')
        if row is None:
            return
        if len(row) != c:
            _show('Association', ['Row ' + str(i + 1) + ' has ' + str(len(row)),
                                  'values, expected ' + str(c)])
            return
        obs.append(row)
        i += 1
    al = _asknum('alpha % (5):')
    if al is None:
        al = 5.0
    if al <= 0 or al >= 100:
        _show('Association', ['Need 0 < alpha < 100'])
        return
    rowt = []
    i = 0
    while i < r:
        s = 0.0
        j = 0
        while j < c:
            if obs[i][j] < 0:
                _show('Association', ['Counts must be >= 0'])
                return
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
    i = 0
    while i < r:
        tot += rowt[i]
        i += 1
    if tot <= 0:
        _show('Association', ['Table total is 0'])
        return
    # E = row total * column total / grand total, which is what independence
    # predicts; the flat-list goodness-of-fit tool cannot form these at all
    lines = ['H0: no association', 'grand total = ' + _fn(tot)]
    chi = 0.0
    small = 0
    i = 0
    while i < r:
        j = 0
        while j < c:
            e = rowt[i] * colt[j] / tot
            if e <= 0:
                _show('Association', ['Zero expected frequency',
                                      'in row ' + str(i + 1) + ' col ' + str(j + 1)])
                return
            if e < 5:
                small += 1
            chi += (obs[i][j] - e) ** 2 / e
            lines.append('E[' + str(i + 1) + ',' + str(j + 1) + '] = ' + _fn(e) +
                         '  O = ' + _fn(obs[i][j]))
            j += 1
        i += 1
    df = (r - 1) * (c - 1)
    lines.append('df = (r-1)(c-1) = ' + str(df))
    lines.append('chi^2 = ' + _fn(chi))
    if small:
        lines.append('WARN: ' + str(small) + ' cell(s) E<5;')
        lines.append(' combine rows or columns')
    if r == 2 and c == 2:
        lines.append('2x2: Yates correction not')
        lines.append(' applied (not required)')
    _chi_verdict(lines, chi, df, al / 100.0)
    if chi > _chi2_crit(df, al / 100.0):
        lines.append('evidence of association')
    else:
        lines.append('no evidence of association')
    _show('Chi-sq association', lines)

# ----------------------------------------------- continuous random variables
# A model is held as a list of pieces, each (f, lo, hi, F), where f is the pdf
# on [lo, hi] as a parse tree and F is its antiderivative or None. An ordinary
# one-line pdf is just a one-piece list, so the piecewise case and the simple
# case share every routine below and cannot drift apart.
#
# Integration is exact where cascalc.integ can find an antiderivative and falls
# back to cascalc.defint (composite Simpson) where it cannot. integ returns
# None rather than a wrong answer when it is stuck, so trusting it is safe.

def _prep(f):
    # antiderivative once per piece: the quantile search integrates repeatedly
    # and re-deriving it inside the loop would be much slower on the handheld
    try:
        return cascalc.integ(f, 'x')
    except:
        return None

def _defint(f, F, a, b):
    # (value, exact_flag); (None, False) if it cannot be evaluated at all
    if b == a:
        return (0.0, True)
    if F is not None:
        try:
            v = caseng.evalf(F, b) - caseng.evalf(F, a)
            if v == v and -1.7e308 < v < 1.7e308:
                return (v, True)
        except:
            pass            # e.g. ln|x| at x = 0; fall through to Simpson
    v = cascalc.defint(f, a, b, False, 200, 'x')
    if v is None:
        return (None, False)
    return (v, False)

def _mkpiece(f, lo, hi):
    return (f, lo, hi, _prep(f))

def _xpow(f, m):
    # the integrand for the m-th moment: x^m * f(x)
    if m == 0:
        return f
    if m == 1:
        return ('*', ('v', 'x'), f)
    return ('*', ('^', ('v', 'x'), ('n', m)), f)

def _moment(pieces, m):
    # integral of x^m f(x) over the whole support; (value, exact_flag)
    tot = 0.0
    exact = True
    i = 0
    while i < len(pieces):
        f = pieces[i][0]
        lo = pieces[i][1]
        hi = pieces[i][2]
        g = _xpow(f, m)
        G = pieces[i][3] if m == 0 else _prep(g)
        v, ex = _defint(g, G, lo, hi)
        if v is None:
            return (None, False)
        tot += v
        if not ex:
            exact = False
        i += 1
    return (tot, exact)

def _pdfval(pieces, x):
    # f(x), or None outside the support / where it will not evaluate
    i = 0
    while i < len(pieces):
        if pieces[i][1] <= x <= pieces[i][2]:
            try:
                return caseng.evalf(pieces[i][0], x)
            except:
                return None
        i += 1
    return None

def _pdf_min(pieces, n):
    # smallest sampled value of f and where it happens, for the f >= 0 check
    lo = None
    lox = 0.0
    k = 0
    while k < len(pieces):
        a = pieces[k][1]
        b = pieces[k][2]
        i = 0
        while i <= n:
            x = a + (b - a) * i / float(n)
            v = _pdfval(pieces, x)
            if v is not None and (lo is None or v < lo):
                lo = v
                lox = x
            i += 1
        k += 1
    return (lo, lox)

def _cdf(pieces, t):
    # F(t) = P(X <= t), accumulated piece by piece
    tot = 0.0
    i = 0
    while i < len(pieces):
        lo = pieces[i][1]
        hi = pieces[i][2]
        if t <= lo:
            break
        u = hi if t > hi else t
        v, ex = _defint(pieces[i][0], pieces[i][3], lo, u)
        if v is None:
            return None
        tot += v
        i += 1
    return tot

def _quantile(pieces, p):
    # F is non-decreasing wherever f >= 0, so bisection on F(t) - p cannot
    # miss the root. cascalc.solve is deliberately not used here: it samples a
    # fixed [-20, 20] grid at 800 points and would step clean over the root
    # whenever the support is narrow (a pdf on [0, 0.1], say).
    lo = pieces[0][1]
    hi = pieces[len(pieces) - 1][2]
    i = 0
    while i < 50:
        m = 0.5 * (lo + hi)
        v = _cdf(pieces, m)
        if v is None:
            return None
        if v < p:
            lo = m
        else:
            hi = m
        i += 1
    return 0.5 * (lo + hi)

def _validity(pieces, lines):
    # the two defining properties of a pdf, each reported either way
    tot, exact = _moment(pieces, 0)
    if tot is None:
        lines.append('Cannot integrate f here.')
        return False
    lines.append('int f dx = ' + _fn(tot) + (' (exact)' if exact else ' (Simpson)'))
    ok = True
    if abs(tot - 1.0) > 5e-4:
        ok = False
        lines.append('NOT a pdf: integral is not 1')
    mn, mx = _pdf_min(pieces, 120)
    if mn is None:
        ok = False
        lines.append('NOT a pdf: f will not')
        lines.append(' evaluate on this range')
    elif mn < -1e-9:
        ok = False
        lines.append('NOT a pdf: f(' + _fn(mx) + ') =')
        lines.append(' ' + _fn(mn) + ', which is < 0')
    if ok:
        lines.append('valid pdf: YES')
    else:
        lines.append('valid pdf: NO (results')
        lines.append(' below assume it were)')
    return ok

def _moments_lines(pieces, lines):
    e1, x1 = _moment(pieces, 1)
    e2, x2 = _moment(pieces, 2)
    if e1 is None or e2 is None:
        lines.append('Cannot integrate for E(X).')
        return
    var = e2 - e1 * e1
    lines.append('E(X) = ' + _fn(e1))
    lines.append('E(X^2) = ' + _fn(e2))
    lines.append('Var(X) = E(X^2)-E(X)^2')
    lines.append('Var(X) = ' + _fn(var))
    lines.append('SD = ' + _fn(math.sqrt(var) if var > 0 else 0.0))

def _draw_pdf(pieces, title):
    lo = pieces[0][1]
    hi = pieces[len(pieces) - 1][2]
    xs = []
    ys = []
    i = 0
    while i <= 140:
        x = lo + (hi - lo) * i / 140.0
        xs.append(x)
        ys.append(_pdfval(pieces, x))
        i += 1
    good = []
    for v in ys:
        if v is not None:
            good.append(v)
    if not good:
        return
    ylo, yhi = casutil.nice_range(good, 0.08, True)
    fr = casutil.frame(lo, hi, ylo, yhi)
    casutil.axes(fr, title, 'x', 'f(x)')
    i = 1
    while i < len(xs):
        if ys[i - 1] is not None and ys[i] is not None:
            casutil.seg(fr, xs[i - 1], ys[i - 1], xs[i], ys[i], casui.ACC)
        i += 1
    casutil.chart_hold('EXIT to go back')

def _ask_pdf(title):
    # f, a, b -> a one-piece model, or None if anything was cancelled
    f = _askexpr('pdf f(x):')
    if f is None:
        return None
    a = _asknum('lower a:')
    if a is None:
        return None
    b = _asknum('upper b:')
    if b is None:
        return None
    if b <= a:
        _show(title, ['Need b > a.'])
        return None
    return [_mkpiece(f, a, b)]

def t_pdf():
    pieces = _ask_pdf('Continuous RV')
    if pieces is None:
        return
    lo = pieces[0][1]
    hi = pieces[0][2]
    lines = ['f(x) on [' + _fn(lo) + ', ' + _fn(hi) + ']']
    # the moments are reported even when the check fails: finding E(X) after
    # solving for an unknown constant k is a normal exam step, and the header
    # line already says loudly whether f is a pdf
    _validity(pieces, lines)
    _moments_lines(pieces, lines)
    _show('Continuous RV', lines)
    _draw_pdf(pieces, 'pdf f(x)')

def t_cdf():
    pieces = _ask_pdf('cdf F(x)')
    if pieces is None:
        return
    f = pieces[0][0]
    lo = pieces[0][1]
    hi = pieces[0][2]
    F = pieces[0][3]
    lines = ['f(x) on [' + _fn(lo) + ', ' + _fn(hi) + ']']
    _validity(pieces, lines)
    if F is not None:
        # F(x) = int from a to x of f, i.e. the antiderivative shifted so
        # that F(a) = 0
        try:
            base = caseng.evalf(F, lo)
            expr = F if base == 0 else ('-', F, ('n', base))
            lines.append('F(x) = ' + caseng.tostr(cascalc.tidy(expr)))
            lines.append(' for ' + _fn(lo) + ' <= x <= ' + _fn(hi))
        except:
            lines.append('F(x): numeric only')
    else:
        lines.append('F(x): numeric only')
    q1 = _quantile(pieces, 0.25)
    md = _quantile(pieces, 0.5)
    q3 = _quantile(pieces, 0.75)
    if md is None:
        lines.append('Cannot invert F.')
        _show('cdf F(x)', lines)
        return
    lines.append('solving F(x) = p:')
    lines.append('Q1 = ' + _fn(q1))
    lines.append('median = ' + _fn(md))
    lines.append('Q3 = ' + _fn(q3))
    lines.append('IQR = ' + _fn(q3 - q1))
    t = _asknum('P(X<=t), t (blank skip):')
    if t is not None:
        v = _cdf(pieces, t)
        if v is not None:
            if v > 1.0:
                v = 1.0
            lines.append('F(' + _fn(t) + ') = ' + _fn(v))
            lines.append('P(X>t) = ' + _fn(1.0 - v))
    _show('cdf F(x)', lines)
    # the cdf curve, with the median read off it
    xs = []
    ys = []
    i = 0
    while i <= 60:
        x = lo + (hi - lo) * i / 60.0
        v = _cdf(pieces, x)
        xs.append(x)
        ys.append(v)
        i += 1
    fr = casutil.frame(lo, hi, 0.0, 1.05)
    casutil.axes(fr, 'cdf F(x)', 'x', 'F(x)')
    i = 1
    while i < len(xs):
        if ys[i - 1] is not None and ys[i] is not None:
            casutil.seg(fr, xs[i - 1], ys[i - 1], xs[i], ys[i], casui.ACC)
        i += 1
    casutil.seg(fr, lo, 0.5, md, 0.5, casui.RED)
    casutil.seg(fr, md, 0.0, md, 0.5, casui.RED)
    casutil.chart_hold('EXIT to go back')

def t_pdfmode():
    pieces = _ask_pdf('Mode of a pdf')
    if pieces is None:
        return
    lo = pieces[0][1]
    hi = pieces[0][2]
    lines = ['f(x) on [' + _fn(lo) + ', ' + _fn(hi) + ']']
    _validity(pieces, lines)
    # coarse scan for the bracket, then a ternary search inside it. A scan is
    # used rather than solving f'(x) = 0 because the mode of an exam pdf is
    # very often at an endpoint, where the derivative is not zero at all.
    n = 200
    best = None
    bi = 0
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / float(n)
        v = _pdfval(pieces, x)
        if v is not None and (best is None or v > best):
            best = v
            bi = i
        i += 1
    if best is None:
        lines.append('f will not evaluate here.')
        _show('Mode of a pdf', lines)
        return
    step = (hi - lo) / float(n)
    a = lo + (bi - 1) * step
    b = lo + (bi + 1) * step
    if a < lo:
        a = lo
    if b > hi:
        b = hi
    i = 0
    while i < 60 and (b - a) > 1e-10:
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        v1 = _pdfval(pieces, m1)
        v2 = _pdfval(pieces, m2)
        if v1 is None or v2 is None:
            break
        if v1 < v2:
            a = m1
        else:
            b = m2
        i += 1
    xm = 0.5 * (a + b)
    fm = _pdfval(pieces, xm)
    if fm is None or fm < best:
        xm = lo + bi * step
        fm = best
    lines.append('mode = ' + _fn(xm))
    lines.append('f(mode) = ' + _fn(fm))
    if abs(xm - lo) <= 2.0 * step:
        lines.append('(at the left endpoint)')
    elif abs(xm - hi) <= 2.0 * step:
        lines.append('(at the right endpoint)')
    else:
        lines.append('(interior maximum)')
    _show('Mode of a pdf', lines)
    _draw_pdf(pieces, 'pdf f(x)')

def t_pdfpw():
    k = _askint('how many pieces (2-4):')
    if k is None or k < 2 or k > 4:
        return
    pieces = []
    i = 0
    while i < k:
        f = _askexpr('piece ' + str(i + 1) + ' f(x):')
        if f is None:
            return
        lo = _asknum('piece ' + str(i + 1) + ' from:')
        if lo is None:
            return
        hi = _asknum('piece ' + str(i + 1) + ' to:')
        if hi is None:
            return
        if hi <= lo:
            _show('Piecewise pdf', ['Piece ' + str(i + 1) + ': need to > from'])
            return
        if i > 0 and abs(lo - pieces[i - 1][2]) > 1e-9:
            _show('Piecewise pdf', ['Piece ' + str(i + 1) + ' starts at ' + _fn(lo),
                                    'but piece ' + str(i) + ' ended at ' +
                                    _fn(pieces[i - 1][2]) + '.',
                                    'Pieces must join up.'])
            return
        pieces.append(_mkpiece(f, lo, hi))
        i += 1
    lines = ['support [' + _fn(pieces[0][1]) + ', ' +
             _fn(pieces[k - 1][2]) + '] in ' + str(k) + ' pieces']
    _validity(pieces, lines)
    _moments_lines(pieces, lines)
    md = _quantile(pieces, 0.5)
    q1 = _quantile(pieces, 0.25)
    q3 = _quantile(pieces, 0.75)
    if md is not None:
        lines.append('Q1 = ' + _fn(q1))
        lines.append('median = ' + _fn(md))
        lines.append('Q3 = ' + _fn(q3))
    _show('Piecewise pdf', lines)
    _draw_pdf(pieces, 'piecewise pdf')

# -------------------------------------- linear combinations of random vars --

def t_lincomb():
    mx = _asknum('E(X):')
    if mx is None:
        return
    vx = _asknum('Var(X):')
    if vx is None or vx < 0:
        _show('aX+bY+c', ['Var(X) must be >= 0'])
        return
    my = _asknum('E(Y):')
    if my is None:
        return
    vy = _asknum('Var(Y):')
    if vy is None or vy < 0:
        _show('aX+bY+c', ['Var(Y) must be >= 0'])
        return
    a = _asknum('a in aX+bY+c:')
    if a is None:
        return
    b = _asknum('b:')
    if b is None:
        return
    c = _asknum('c:')
    if c is None:
        c = 0.0
    ew = a * mx + b * my + c
    vw = a * a * vx + b * b * vy
    sw = math.sqrt(vw) if vw > 0 else 0.0
    lines = ['W = ' + _fn(a) + 'X' + _signed(b, 'Y') + _signed(c, ''),
             'X, Y assumed INDEPENDENT',
             'E(W) = aE(X)+bE(Y)+c',
             'E(W) = ' + _fn(ew),
             'Var(W) = a^2VarX+b^2VarY',
             'Var(W) = ' + _fn(vw),
             'SD(W) = ' + _fn(sw),
             'E(X+Y) = ' + _fn(mx + my),
             'Var(X+Y) = ' + _fn(vx + vy),
             'E(X-Y) = ' + _fn(mx - my),
             'Var(X-Y) = ' + _fn(vx + vy),
             'note Var(X-Y) ADDS the',
             ' variances, never subtracts',
             'If X,Y are Normal then W is',
             ' Normal. The mean and var',
             ' above hold for ANY indep',
             ' X and Y.']
    w = _asknum('P(W<w), w (blank skip):')
    if w is not None:
        if sw > 0:
            z = (w - ew) / sw
            lines.append('assuming W Normal:')
            lines.append('z = ' + _fn(z))
            lines.append('P(W<w) = ' + _fn(_phi(z)))
            lines.append('P(W>w) = ' + _fn(1.0 - _phi(z)))
        else:
            lines.append('SD is 0: W is the constant ' + _fn(ew))
    _show('aX+bY+c', lines)

def t_nsum():
    mx = _asknum('E(X):')
    if mx is None:
        return
    vx = _asknum('Var(X):')
    if vx is None or vx < 0:
        _show('nX vs X1+..+Xn', ['Var(X) must be >= 0'])
        return
    n = _askint('n:')
    if n is None or n < 1:
        return
    # The distinction students lose marks on: nX is ONE observation scaled,
    # so its spread is scaled too; X1+...+Xn is n INDEPENDENT observations,
    # whose variances add. Same mean, different variance.
    vscale = n * n * vx
    vsum = n * vx
    lines = ['n = ' + str(n),
             '--- nX: ONE X, scaled ---',
             'E(nX) = nE(X) = ' + _fn(n * mx),
             'Var(nX) = n^2Var(X)',
             'Var(nX) = ' + _fn(vscale),
             'SD(nX) = ' + _fn(math.sqrt(vscale) if vscale > 0 else 0.0),
             '--- X1+..+Xn: n INDEP ---',
             'E(sum) = nE(X) = ' + _fn(n * mx),
             'Var(sum) = nVar(X)',
             'Var(sum) = ' + _fn(vsum),
             'SD(sum) = ' + _fn(math.sqrt(vsum) if vsum > 0 else 0.0),
             'SAME mean, DIFFERENT var',
             'ratio Var(nX)/Var(sum) = ' + _fn(float(n)),
             '--- sample mean Xbar ---',
             'E(Xbar) = ' + _fn(mx),
             'Var(Xbar) = Var(X)/n = ' + _fn(vx / n),
             'SD(Xbar) = ' + _fn(math.sqrt(vx / n) if vx > 0 else 0.0),
             'If X is Normal all three',
             ' of these are Normal too.']
    _show('nX vs X1+..+Xn', lines)

def t_cimean():
    xb = _asknum('sample mean:')
    if xb is None:
        return
    sg = _asknum('sigma (known):')
    if sg is None or sg <= 0:
        return
    n = _askint('n:')
    if n is None or n <= 0:
        return
    cl = _asknum('conf level % (95):')
    if cl is None or cl <= 0 or cl >= 100:
        return
    z = _invphi(1.0 - (1.0 - cl / 100.0) / 2.0)
    se = sg / math.sqrt(n)
    m = z * se
    _show('CI for mean', ['z* = ' + _fn(z), 'SE = ' + _fn(se), 'mean +/- ' + _fn(m), '(' + _fn(xb - m) + ', ' + _fn(xb + m) + ')', 'small n: use t, not z'])

def t_tint():
    # One-sample / paired t interval. For paired data enter the list of
    # DIFFERENCES: the paired test is just the one-sample test applied to them.
    a = _asklist('Data (or differences):')
    if a is None or len(a) < 2:
        _show('t interval', ['Need at least 2 values.'])
        return
    cl = _asknum('conf level % (95):')
    if cl is None:
        cl = 95.0
    if cl <= 0 or cl >= 100:
        _show('t interval', ['Need 0 < level < 100'])
        return
    n = len(a)
    tot = 0.0
    i = 0
    while i < n:
        tot += a[i]
        i += 1
    mean = tot / n
    ss = 0.0
    i = 0
    while i < n:
        ss += (a[i] - mean) * (a[i] - mean)
        i += 1
    s = math.sqrt(ss / (n - 1))
    se = s / math.sqrt(n)
    v = n - 1
    tc = _t_crit(v, (1.0 - cl / 100.0) / 2.0)
    m = tc * se
    lines = ['n = ' + str(n),
             'mean = ' + _fn(mean),
             's (n-1) = ' + _fn(s),
             'SE = s/sqrt(n) = ' + _fn(se),
             'df = ' + str(v),
             't* = ' + _fn(tc),
             'mean +/- ' + _fn(m),
             '(' + _fn(mean - m) + ', ' + _fn(mean + m) + ')',
             'sigma is estimated from the',
             ' sample, so this uses t, not z']
    # a confidence interval doubles as a two-tail test of any given mean
    mu0 = _asknum('test mean mu0 (blank skip):')
    if mu0 is not None:
        lines.append('mu0 = ' + _fn(mu0))
        if mu0 < mean - m or mu0 > mean + m:
            lines.append('mu0 outside the interval:')
            lines.append(' reject H0 at ' + _fn(100.0 - cl) + '%')
        else:
            lines.append('mu0 inside the interval:')
            lines.append(' accept H0 at ' + _fn(100.0 - cl) + '%')
        if se > 0:
            ts = (mean - mu0) / se
            lines.append('t = ' + _fn(ts))
            lines.append('p (2-tail) = ' + _fp(2.0 * _t_sf(abs(ts), v)))
    _show('t interval', lines)

def t_ciprop():
    k = _askint('successes:')
    if k is None or k < 0:
        return
    n = _askint('n:')
    if n is None or n <= 0 or k > n:
        return
    cl = _asknum('conf level % (95):')
    if cl is None or cl <= 0 or cl >= 100:
        return
    p = k / float(n)
    z = _invphi(1.0 - (1.0 - cl / 100.0) / 2.0)
    se = math.sqrt(p * (1.0 - p) / n)
    m = z * se
    _show('CI for proportion', ['p-hat = ' + _fn(p), 'z* = ' + _fn(z), 'SE = ' + _fn(se), 'p +/- ' + _fn(m), '(' + _fn(p - m) + ', ' + _fn(p + m) + ')'])

def t_ztest():
    mu0 = _asknum('H0 mean mu0:')
    if mu0 is None:
        return
    xb = _asknum('sample mean:')
    if xb is None:
        return
    sg = _asknum('sigma (known):')
    if sg is None or sg <= 0:
        return
    n = _askint('n:')
    if n is None or n <= 0:
        return
    al = _asknum('alpha % (5):')
    if al is None or al <= 0 or al >= 100:
        return
    se = sg / math.sqrt(n)
    z = (xb - mu0) / se
    a = al / 100.0
    zc1 = _invphi(1.0 - a)
    zc2 = _invphi(1.0 - a / 2.0)
    pv = 2.0 * (1.0 - _phi(abs(z)))
    _show('One-sample z-test', ['z = ' + _fn(z), '1-tail crit = +/-' + _fn(zc1), '2-tail crit = +/-' + _fn(zc2), 'p (2-tail) = ' + _fn(pv), '|z|>crit: reject H0'])

TOOLS = [
    ('Discrete RV E/Var', t_drv),
    ('Discrete uniform', t_dunif),
    ('Poisson pmf/cdf', t_pois),
    ('Binomial pmf/cdf', t_bin),
    ('Geometric dist', t_geom),
    ('Continuous RV E/Var', t_pdf),
    ('cdf, median, quartiles', t_cdf),
    ('Mode of a pdf', t_pdfmode),
    ('Piecewise pdf', t_pdfpw),
    ('Normal P(a<X<b)', t_norm),
    ('Standardise z', t_std),
    ('Inverse Normal', t_inv),
    ('aX+bY+c combination', t_lincomb),
    ('nX vs X1+..+Xn', t_nsum),
    ('Normal prob plot', t_normplot),
    ('PMCC r + test', t_pmcc),
    ('Spearman rs + test', t_spear),
    ('Regression y=a+bx', t_reg),
    ('Chi-squared GOF', t_chi),
    ('Chi-sq association', t_assoc),
    ('CI for mean (z)', t_cimean),
    ('t interval / paired', t_tint),
    ('CI for proportion', t_ciprop),
    ('z-test for mean', t_ztest),
]

def run():
    casutil.run_tools('Statistics (FM)', TOOLS)