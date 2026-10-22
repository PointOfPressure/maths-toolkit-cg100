# Statistics actions on a distribution: B(n, p) probabilities, mean and
# variance, the binomial test and critical regions; N(mu, sigma^2)
# probabilities (standardised to Z), the inverse, the test for a mean, and
# mu or sigma from one probability. Plain floats (math only): a test needs
# no CAS. Working to 5 s.f.; the box gives the Decimals setting on FORMAT.
import math
import fmt

def _s(x):
    return fmt.sf(x, 5) if x is not None else '-'

def box(pre, x):
    d = fmt.dec(x)
    s = _s(x)
    return ('=', pre, s, d if d != s else None, ('n', x) if x >= 0 else ('neg', ('n', -x)))

def _v(t, name):
    if t is None:
        raise ValueError('fill in ' + name)
    import recog
    x = recog.numv(t)
    if x is None:
        raise ValueError(name + ' must be a number')
    return x

def _int(t, name):
    x = _v(t, name)
    if x != int(x):
        raise ValueError(name + ' must be a whole number')
    return int(x)

def sig(t):
    # a significance level: 5 is 5%, 0.05 is 5% too
    a = _v(t, 'the significance level')
    if a <= 0 or a >= 100:
        raise ValueError('significance level: a percentage')
    return a / 100.0 if a >= 1 else a

def pct(a):
    return fmt.sf(a * 100, 4) + '%'

# ---- the binomial ---------------------------------------------------------------------------

def pmf(n, p, k):
    if k < 0 or k > n:
        return 0.0
    if p <= 0:
        return 1.0 if k == 0 else 0.0
    if p >= 1:
        return 1.0 if k == n else 0.0
    lc = 0.0
    for i in range(k):
        lc += math.log(n - i) - math.log(i + 1)
    return math.exp(lc + k * math.log(p) + (n - k) * math.log(1 - p))

def cdf(n, p, k):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    t = 0.0
    for i in range(k + 1):
        t += pmf(n, p, i)
    return min(t, 1.0)

def _bx(F):
    return 'X ~ B(' + str(F.n) + ', ' + _s(F.p) + ')'

def bprob(F, arg, vals):
    n, p = F.n, F.p
    lines = [_bx(F)]
    if arg == 'eq':
        r = _int(vals[0], 'r')
        x = pmf(n, p, r)
        lines.append('P(X = ' + str(r) + ') = ' + str(n) + 'C' + str(r) + ' (' + _s(p) + ')^' + str(r) +
                     ' (' + _s(1 - p) + ')^' + str(n - r))
        lines.append(box('P(X = ' + str(r) + ') = ', x))
    elif arg == 'le':
        r = _int(vals[0], 'r')
        lines.append(box('P(X <= ' + str(r) + ') = ', cdf(n, p, r)))
    elif arg == 'ge':
        r = _int(vals[0], 'r')
        c = cdf(n, p, r - 1)
        lines.append('P(X >= ' + str(r) + ') = 1 - P(X <= ' + str(r - 1) + ') = 1 - ' + _s(c))
        lines.append(box('P(X >= ' + str(r) + ') = ', 1 - c))
    else:
        a = _int(vals[0], 'a')
        b = _int(vals[1], 'b')
        if b < a:
            raise ValueError('b is less than a')
        hi = cdf(n, p, b)
        lo = cdf(n, p, a - 1)
        lines.append('P(' + str(a) + ' <= X <= ' + str(b) + ') = P(X <= ' + str(b) + ') - P(X <= ' + str(a - 1) + ')')
        lines.append('= ' + _s(hi) + ' - ' + _s(lo))
        lines.append(box('P(' + str(a) + ' <= X <= ' + str(b) + ') = ', hi - lo))
    lines.append(('w', 'P(X < r) = P(X <= r - 1); P(X > r) = P(X >= r + 1)'))
    return lines

def bmean(F, arg, vals):
    n, p = F.n, F.p
    m = n * p
    v = n * p * (1 - p)
    return [_bx(F), 'E(X) = np = ' + str(n) + ' x ' + _s(p), box('mean = ', m),
            'Var(X) = np(1 - p) = ' + str(n) + ' x ' + _s(p) + ' x ' + _s(1 - p), box('variance = ', v),
            box('sd = ', math.sqrt(v))]

TAILS = ['lower tail (H1: p < p0)', 'upper tail (H1: p > p0)', 'two-tail (H1: p != p0)']
MTAILS = ['lower tail (H1: mu < mu0)', 'upper tail (H1: mu > mu0)', 'two-tail (H1: mu != mu0)']

def _low(n, p, a):
    # largest c with P(X <= c) <= a, or -1
    c = -1
    t = 0.0
    for k in range(n + 1):
        t += pmf(n, p, k)
        if t > a + 1e-12:
            break
        c = k
    return c

def _up(n, p, a):
    # smallest c with P(X >= c) <= a, or n + 1
    c = n + 1
    t = 0.0
    for k in range(n, -1, -1):
        t += pmf(n, p, k)
        if t > a + 1e-12:
            break
        c = k
    return c

def _region(n, p, tail, a, lines):
    out = []
    if tail in (0, 2):
        aa = a if tail == 0 else a / 2
        c = _low(n, p, aa)
        if c >= 0:
            out.append('X <= ' + str(c))
            lines.append(('w', 'P(X <= ' + str(c) + ') = ' + _s(cdf(n, p, c)) + ' <= ' + _s(aa) + ', P(X <= ' +
                          str(c + 1) + ') = ' + _s(cdf(n, p, c + 1)) + ' > ' + _s(aa)))
    if tail in (1, 2):
        aa = a if tail == 1 else a / 2
        c = _up(n, p, aa)
        if c <= n:
            out.append('X >= ' + str(c))
            lines.append(('w', 'P(X >= ' + str(c) + ') = ' + _s(1 - cdf(n, p, c - 1)) + ' <= ' + _s(aa) +
                          ', P(X >= ' + str(c - 1) + ') = ' + _s(1 - cdf(n, p, c - 2)) + ' > ' + _s(aa)))
    return ' or '.join(out) if out else 'none: no outcome is that unlikely'

def btest(F, arg, vals):
    n, p = F.n, F.p
    tail = vals[0]
    x = _int(vals[1], 'x')
    a = sig(vals[2])
    sg = ('<', '>', '!=')[tail]
    lines = ['H0: p = ' + _s(p) + ',  H1: p ' + sg + ' ' + _s(p),
             'under H0, ' + _bx(F) + ';  significance level ' + pct(a)]
    if tail == 2:
        up = x > n * p
        lines.append(('w', 'two-tail: compare with ' + pct(a / 2) + ' in the tail ' + str(x) + ' is in'))
    else:
        up = tail == 1
    aa = a if tail < 2 else a / 2
    if up:
        pv = 1 - cdf(n, p, x - 1)
        lines.append('P(X >= ' + str(x) + ') = 1 - P(X <= ' + str(x - 1) + ') = ' + _s(pv))
    else:
        pv = cdf(n, p, x)
        lines.append('P(X <= ' + str(x) + ') = ' + _s(pv))
    rej = pv <= aa
    lines.append(_s(pv) + (' <= ' if rej else ' > ') + _s(aa))
    lines.append('critical region: ' + _region(n, p, tail, a, lines))
    lines.append(fmt.boxs('', 'reject H0' if rej else 'do not reject H0'))
    lines.append(('w', ('sufficient' if rej else 'insufficient') + ' evidence at the ' + pct(a) +
                  ' level that p ' + ('has changed' if tail == 2 else ('is less' if tail == 0 else 'is greater')) +
                  ' (in context)'))
    return lines

def bcrit(F, arg, vals):
    n, p = F.n, F.p
    tail = vals[0]
    a = sig(vals[1])
    lines = ['under H0, ' + _bx(F) + ';  ' + TAILS[tail] + ', ' + pct(a)]
    r = _region(n, p, tail, a, lines)
    lines.append(fmt.boxs('critical region: ', r))
    return lines

# ---- the normal --------------------------------------------------------------------------------

def erf(x):
    # series near 0, continued fraction beyond (10 s.f. or better)
    s = 1.0 if x >= 0 else -1.0
    x = abs(x)
    if x < 3.0:
        t = x
        tot = x
        k = 0
        while abs(t) > 1e-17 * abs(tot):
            k += 1
            t = -t * x * x / k
            tot += t / (2 * k + 1)
        return s * 2.0 / math.sqrt(math.pi) * tot
    if x > 9.0:
        return s
    # erfc by its continued fraction (Lentz)
    f = 0.0
    for k in range(60, 0, -1):
        f = k / 2.0 / (x + f)
    return s * (1.0 - math.exp(-x * x) / math.sqrt(math.pi) / (x + f))

def phi(z):
    return 0.5 * (1.0 + erf(z / math.sqrt(2.0)))

def invphi(q):
    if q <= 0 or q >= 1:
        raise ValueError('a probability between 0 and 1')
    lo = -10.0
    hi = 10.0
    for i in range(70):
        m = (lo + hi) / 2
        if phi(m) < q:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2

def _nx(F):
    return 'X ~ N(' + _s(F.mu) + ', ' + _s(F.sd) + '^2)'

def _need(F):
    if F.mu is None or F.sd is None:
        raise ValueError('mu or sigma is ?: use Find mu or sigma first')

def _z(F, x):
    return (x - F.mu) / F.sd

def nprob(F, arg, vals):
    _need(F)
    lines = [_nx(F)]
    if arg == 'between':
        a = _v(vals[0], 'a')
        b = _v(vals[1], 'b')
        if b < a:
            a, b = b, a
        za, zb = _z(F, a), _z(F, b)
        lines.append('P(' + _s(a) + ' < X < ' + _s(b) + ') = P(' + _s(za) + ' < Z < ' + _s(zb) + ')')
        lines.append('= ' + _s(phi(zb)) + ' - ' + _s(phi(za)))
        lines.append(box('P(' + _s(a) + ' < X < ' + _s(b) + ') = ', phi(zb) - phi(za)))
        return lines
    x = _v(vals[0], 'x')
    z = _z(F, x)
    lines.append('z = (' + _s(x) + ' - ' + _s(F.mu) + ')/' + _s(F.sd) + ' = ' + _s(z))
    if arg == 'lt':
        lines.append(box('P(X < ' + _s(x) + ') = ', phi(z)))
    else:
        lines.append('P(X > ' + _s(x) + ') = 1 - P(Z < ' + _s(z) + ')')
        lines.append(box('P(X > ' + _s(x) + ') = ', 1 - phi(z)))
    return lines

def ninv(F, arg, vals):
    _need(F)
    q = _v(vals[0], 'the probability')
    z = invphi(q)
    x = F.mu + z * F.sd
    return [_nx(F), 'P(X < x) = ' + _s(q) + ':  z = ' + _s(z), 'x = mu + z sigma = ' + _s(F.mu) + ' + ' +
            fmt.br(_s(z)) + ' x ' + _s(F.sd), box('x = ', x)]

def nfind(F, arg, vals):
    # mu or sigma from P(X < x) = q (or P(X > x) = q)
    d = vals[0]
    x = _v(vals[1], 'x')
    q = _v(vals[2], 'the probability')
    lines = []
    if d == 1:
        lines.append('P(X > ' + _s(x) + ') = ' + _s(q) + ', so P(X < ' + _s(x) + ') = ' + _s(1 - q))
        q = 1 - q
    z = invphi(q)
    lines.append('z = ' + _s(z))
    if F.mu is None:
        mu = x - z * F.sd
        lines.append(_s(x) + ' = mu + ' + fmt.br(_s(z)) + ' x ' + _s(F.sd))
        lines.append(box('mu = ', mu))
    else:
        if abs(z) < 1e-12 or (x - F.mu) / z <= 0:
            raise ValueError('no positive sigma fits')
        lines.append('(' + _s(x) + ' - ' + _s(F.mu) + ')/sigma = ' + _s(z))
        lines.append(box('sigma = ', (x - F.mu) / z))
    return lines

def ztest(F, arg, vals):
    _need(F)
    tail = vals[0]
    n = _int(vals[1], 'n')
    xb = _v(vals[2], 'the sample mean')
    a = sig(vals[3])
    se = F.sd / math.sqrt(n)
    sg = ('<', '>', '!=')[tail]
    z = (xb - F.mu) / se
    lines = ['H0: mu = ' + _s(F.mu) + ',  H1: mu ' + sg + ' ' + _s(F.mu),
             'under H0, Xbar ~ N(' + _s(F.mu) + ', ' + _s(F.sd) + '^2/' + str(n) + ');  ' + pct(a),
             'z = (' + _s(xb) + ' - ' + _s(F.mu) + ')/(' + _s(F.sd) + '/sqrt(' + str(n) + ')) = ' + _s(z)]
    if tail == 0:
        pv = phi(z)
        c = invphi(a)
        rej = z <= c
        lines.append('critical value ' + _s(c) + ';  p-value P(Z < ' + _s(z) + ') = ' + _s(pv))
    elif tail == 1:
        pv = 1 - phi(z)
        c = invphi(1 - a)
        rej = z >= c
        lines.append('critical value ' + _s(c) + ';  p-value P(Z > ' + _s(z) + ') = ' + _s(pv))
    else:
        pv = 1 - phi(abs(z))
        c = invphi(1 - a / 2)
        rej = abs(z) >= c
        lines.append('critical values +-' + _s(c) + ';  P(Z > ' + _s(abs(z)) + ') = ' + _s(pv) + ' vs ' + _s(a / 2))
    lines.append(fmt.boxs('', 'reject H0' if rej else 'do not reject H0'))
    lines.append(('w', ('sufficient' if rej else 'insufficient') + ' evidence at the ' + pct(a) +
                  ' level that the mean ' + ('has changed' if tail == 2 else
                                             ('is less' if tail == 0 else 'is greater')) + ' (in context)'))
    return lines
