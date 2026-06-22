import math
import casui
import caslex
import caseng

def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None

def _askint(prompt):
    v = _asknum(prompt)
    if v is None:
        return None
    return int(round(v))

def _asklist(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    out = []
    for p in s.replace(',', ' ').split():
        try:
            out.append(float(p))
        except:
            pass
    if len(out) == 0:
        return None
    return out

def _fn(x):
    r = round(x, 4)
    if r == int(r):
        return str(int(r))
    return str(r)

def _show(title, lines):
    casui.result_screen(title, lines)

# --- numeric primitives (math lacks factorial / erf) ---

def _fact(n):
    r = 1.0
    i = 2
    while i <= n:
        r = r * i
        i += 1
    return r

def _ncr(n, r):
    if r < 0 or r > n:
        return 0.0
    if r > n - r:
        r = n - r
    res = 1.0
    i = 0
    while i < r:
        res = res * (n - i) / (i + 1)
        i += 1
    return res

def _erf(x):
    # Abramowitz & Stegun 7.1.26
    s = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * math.exp(-x * x)
    return s * y

def _phi(z):
    return 0.5 * (1.0 + _erf(z / math.sqrt(2.0)))

def _invphi(p):
    if p <= 0.0:
        return -6.0
    if p >= 1.0:
        return 6.0
    lo = -6.0
    hi = 6.0
    i = 0
    while i < 80:
        mid = (lo + hi) / 2.0
        if _phi(mid) < p:
            lo = mid
        else:
            hi = mid
        i += 1
    return (lo + hi) / 2.0

def _poispmf(mu, k):
    return math.exp(-mu) * (mu ** k) / _fact(k)

def _binpmf(n, p, k):
    return _ncr(n, k) * (p ** k) * ((1.0 - p) ** (n - k))

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
    cdf = 0.0
    j = 0
    while j <= k:
        cdf += _poispmf(mu, j)
        j += 1
    _show('Poisson', ['mu = ' + _fn(mu) + '  k = ' + str(k), 'P(X=k) = ' + _fn(pmf), 'P(X<=k) = ' + _fn(cdf), 'P(X>=k) = ' + _fn(1.0 - cdf + pmf)])

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
    pmf = _binpmf(n, p, k)
    cdf = 0.0
    j = 0
    while j <= k:
        cdf += _binpmf(n, p, j)
        j += 1
    _show('Binomial', ['n=' + str(n) + ' p=' + _fn(p) + ' k=' + str(k), 'P(X=k) = ' + _fn(pmf), 'P(X<=k) = ' + _fn(cdf), 'P(X>=k) = ' + _fn(1.0 - cdf + pmf)])

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
    _show('PMCC r', ['n = ' + str(n), 'Sxy = ' + _fn(Sxy), 'Sxx = ' + _fn(Sxx), 'Syy = ' + _fn(Syy), 'r = ' + _fn(r)])

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
    _show('Spearman rs', ['n = ' + str(n), '(PMCC of ranks,', ' ties averaged)', 'rs = ' + _fn(rs)])

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
    if xv is not None:
        lines.append('at x=' + _fn(xv) + ': y=' + _fn(a + b * xv))
    _show('Least squares', lines)

# chi-squared 5% critical values, df 1..10
_CHI5 = [3.841, 5.991, 7.815, 9.488, 11.070, 12.592, 14.067, 15.507, 16.919, 18.307]

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
    chi = 0.0
    i = 0
    while i < len(O):
        if E[i] <= 0:
            _show('Chi-squared', ['Expected has 0 cell'])
            return
        chi += (O[i] - E[i]) ** 2 / E[i]
        i += 1
    df = len(O) - 1
    lines = ['chi^2 = ' + _fn(chi), 'df = ' + str(df) + ' (cells-1)']
    if 1 <= df <= 10:
        cv = _CHI5[df - 1]
        lines.append('5% crit = ' + _fn(cv))
        if chi > cv:
            lines.append('chi^2>crit: reject H0')
        else:
            lines.append('chi^2<=crit: accept H0')
    else:
        lines.append('df outside 1..10 table')
    _show('Chi-squared GOF', lines)

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
    ('Poisson pmf/cdf', t_pois),
    ('Binomial pmf/cdf', t_bin),
    ('Normal P(a<X<b)', t_norm),
    ('Standardise z', t_std),
    ('Inverse Normal', t_inv),
    ('PMCC r', t_pmcc),
    ('Spearman rank', t_spear),
    ('Regression y=a+bx', t_reg),
    ('Chi-squared GOF', t_chi),
    ('CI for mean', t_cimean),
    ('CI for proportion', t_ciprop),
    ('z-test for mean', t_ztest),
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Statistics (FM)', labels)
        if c == -1:
            return
        TOOLS[c][1]()