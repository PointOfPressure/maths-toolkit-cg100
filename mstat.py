# AQA 7357 sections K-O: statistical sampling, data presentation and
# interpretation, probability, statistical distributions, hypothesis testing.
# AQA conventions: sd of data uses the n divisor and s (n-1) is shown as
# working; quartiles sit at the n/4, n/2 and 3n/4 positions.
import math
import casutil
import tables

_W = casutil.w
_WARN = casutil.warn


def _f(v):
    return casutil.sf3(v)


def _p(v):
    return casutil.fmt(v)


def _c(v, sf):
    return casutil.fmt(v, sf)


# ---- small helpers ----------------------------------------------------------

def _srt(a):
    b = list(a)
    b.sort()
    return b


def _int(v, name):
    i = int(v)
    if i != v:
        raise ValueError(name + ' must be a whole number')
    return i


def _chunk(items, width):
    lines = []
    cur = ''
    for s in items:
        if cur == '':
            cur = s
        elif len(cur) + 1 + len(s) <= width:
            cur += ' ' + s
        else:
            lines.append(cur)
            cur = s
    if cur != '':
        lines.append(cur)
    return lines


# ponytail: 32-bit LCG instead of the random module so a sampling tool is a
# pure function of its fields (the runner re-calls it to re-render). The
# optional seed field is what gives a different sample.
def _seed(a, b, s):
    v = int(a) * 7919 + int(b) * 104729
    if s is not None:
        v += int(s) * 1000003
    return [(v & 0x7FFFFFFF) | 1]


def _rnd(st, hi):
    st[0] = (1103515245 * st[0] + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % hi + 1


def _stats(xs):
    # -> (n, mean, sd with n, s with n-1, sum x, sum x^2, Sxx)
    n = len(xs)
    sx = 0.0
    sxx = 0.0
    for v in xs:
        sx += v
        sxx += v * v
    mean = sx / n
    vp = sxx / n - mean * mean
    if vp < 0.0:
        vp = 0.0
    ss = sxx - sx * sx / n
    if ss < 0.0:
        ss = 0.0
    s1 = math.sqrt(ss / (n - 1)) if n > 1 else 0.0
    return (n, mean, math.sqrt(vp), s1, sx, sxx, ss)


def _qpos(srt, pos):
    # AQA position rule: a whole position takes the mean of that value and the
    # next one, otherwise the position is rounded up.
    n = len(srt)
    if n == 1:
        return srt[0]
    fl = int(math.floor(pos))
    if abs(pos - fl) < 1e-9:
        if fl < 1:
            return srt[0]
        if fl >= n:
            return srt[n - 1]
        return (srt[fl - 1] + srt[fl]) / 2.0
    i = int(math.ceil(pos))
    if i < 1:
        i = 1
    if i > n:
        i = n
    return srt[i - 1]


def _five(srt):
    n = len(srt)
    return (srt[0], _qpos(srt, n * 0.25), _qpos(srt, n * 0.5),
            _qpos(srt, n * 0.75), srt[n - 1])


def _fences(q1, q3):
    iqr = q3 - q1
    return (q1 - 1.5 * iqr, q3 + 1.5 * iqr, iqr)


def _xy(d):
    if len(d) < 4 or len(d) % 2:
        raise ValueError('need x,y pairs')
    out = []
    i = 0
    while i < len(d):
        out.append((d[i], d[i + 1]))
        i += 2
    return out


def _vf(d, what):
    if len(d) < 2 or len(d) % 2:
        raise ValueError('need value,' + what + ' pairs')
    out = []
    tot = 0.0
    i = 0
    while i < len(d):
        if d[i + 1] < 0:
            raise ValueError('each ' + what + ' must be >= 0')
        out.append((d[i], d[i + 1]))
        tot += d[i + 1]
        i += 2
    if tot <= 0:
        raise ValueError('the ' + what + ' values total 0')
    return out


def _tri(d):
    if len(d) < 3 or len(d) % 3:
        raise ValueError('need lower,upper,freq')
    out = []
    tot = 0.0
    i = 0
    while i < len(d):
        lo = d[i]
        hi = d[i + 1]
        fr = d[i + 2]
        if hi <= lo:
            raise ValueError('upper must exceed lower')
        if fr < 0:
            raise ValueError('frequency must be >= 0')
        out.append((lo, hi, fr))
        tot += fr
        i += 3
    if tot <= 0:
        raise ValueError('total frequency is 0')
    return out


def _wstats(prs):
    n = 0.0
    sx = 0.0
    sxx = 0.0
    for v, fr in prs:
        n += fr
        sx += fr * v
        sxx += fr * v * v
    mean = sx / n
    vp = sxx / n - mean * mean
    if vp < 0.0:
        vp = 0.0
    ss = sxx - sx * sx / n
    if ss < 0.0:
        ss = 0.0
    s1 = math.sqrt(ss / (n - 1.0)) if n > 1.0 else 0.0
    return (n, mean, math.sqrt(vp), s1, sx, sxx, ss)


def _cinterp(cl, target):
    run = 0.0
    for lo, hi, fr in cl:
        if target <= run + fr:
            if fr <= 0:
                return lo
            return lo + (target - run) / fr * (hi - lo)
        run += fr
    return cl[len(cl) - 1][1]


def _lin(pts):
    # -> (a, b, r, Sxx, Syy, Sxy)
    n = len(pts)
    sx = 0.0
    sy = 0.0
    sxy = 0.0
    sxx = 0.0
    syy = 0.0
    for x, y in pts:
        sx += x
        sy += y
        sxy += x * y
        sxx += x * x
        syy += y * y
    dxx = sxx - sx * sx / n
    dyy = syy - sy * sy / n
    dxy = sxy - sx * sy / n
    if dxx <= 0.0:
        raise ValueError('all x values are equal')
    b = dxy / dxx
    a = sy / n - b * sx / n
    r = dxy / math.sqrt(dxx * dyy) if dyy > 0.0 else None
    return (a, b, r, dxx, dyy, dxy)


def _yeq(a, b):
    if b < 0:
        return 'y = ' + _f(a) + ' - ' + _f(-b) + 'x'
    return 'y = ' + _f(a) + ' + ' + _f(b) + 'x'


def _bin(n, p):
    ni = _int(n, 'n')
    if ni < 1:
        raise ValueError('n must be 1 or more')
    if ni > 1000:
        raise ValueError('n too large (max 1000)')
    if p < 0.0 or p > 1.0:
        raise ValueError('p must be between 0 and 1')
    return ni


def _sd(sigma):
    if sigma <= 0.0:
        raise ValueError('sigma must be > 0')


def _prob(v, name):
    if v < 0.0 or v > 1.0:
        raise ValueError(name + ' must be between 0 and 1')


def _alpha(sig):
    if sig <= 0.0 or sig >= 100.0:
        raise ValueError('significance % must be 0 to 100')
    return sig / 100.0


def _zc(a):
    # (critical z, came from the table?) - falls back to the inverse cdf
    v = tables.z_crit(a)
    if v is not None:
        return (v, True)
    return (casutil.invphi(1.0 - a), False)


def _cr_low(n, p, a):
    # largest c with P(X <= c) <= a, or -1 when the region is empty
    c = -1
    acc = 0.0
    i = 0
    while i <= n:
        acc += casutil.binom_pmf(n, p, i)
        if acc > a + 1e-12:
            break
        c = i
        i += 1
    return c


def _cr_up(n, p, a):
    # smallest c with P(X >= c) <= a, or n+1 when the region is empty
    c = n + 1
    acc = 0.0
    i = n
    while i >= 0:
        acc += casutil.binom_pmf(n, p, i)
        if acc > a + 1e-12:
            break
        c = i
        i -= 1
    return c


def _verdict(rej, sig):
    if rej:
        return 'reject H0 at ' + _f(sig) + '%'
    return 'do not reject H0 at ' + _f(sig) + '%'


# ---- K statistical sampling --------------------------------------------------

def t_srs(N, n, seed):
    Ni = _int(N, 'N')
    ni = _int(n, 'n')
    if Ni < 1:
        raise ValueError('N must be 1 or more')
    if ni < 1 or ni > Ni:
        raise ValueError('need 1 <= n <= N')
    if ni > 100:
        raise ValueError('n too large (max 100)')
    st = _seed(Ni, ni, seed)
    got = {}
    out = []
    while len(out) < ni:
        v = _rnd(st, Ni)
        if v not in got:
            got[v] = 1
            out.append(v)
    out.sort()
    lines = [_p(ni) + ' from 1..' + _p(Ni)]
    for ln in _chunk([_p(v) for v in out], 34):
        lines.append(ln)
    lines.append(_W('number the population 1..' + _p(Ni)))
    lines.append(_W('draw without replacement'))
    lines.append(_W('every sample of size n equally likely'))
    lines.append(_W('change the seed for another sample'))
    return lines


def t_systematic(N, n, seed):
    Ni = _int(N, 'N')
    ni = _int(n, 'n')
    if Ni < 1:
        raise ValueError('N must be 1 or more')
    if ni < 1 or ni > Ni:
        raise ValueError('need 1 <= n <= N')
    if ni > 100:
        raise ValueError('n too large (max 100)')
    k = int(Ni // ni)
    if k < 1:
        k = 1
    st = _seed(Ni, ni, seed)
    start = _rnd(st, k)
    out = []
    v = start
    while len(out) < ni and v <= Ni:
        out.append(v)
        v += k
    lines = [_p(ni) + ' from 1..' + _p(Ni),
             'k = ' + _p(k) + '   start = ' + _p(start)]
    for ln in _chunk([_p(x) for x in out], 34):
        lines.append(ln)
    lines.append(_W('k = N/n = ' + _p(Ni) + '/' + _p(ni) + ' = ' +
                    _f(Ni / (ni * 1.0))))
    lines.append(_W('random start in 1..k, then every kth'))
    lines.append(_W('change the seed for another start'))
    if len(out) < ni:
        lines.append(_WARN('ran past N: only ' + _p(len(out)) + ' picked'))
    return lines


def t_strat(n, strata):
    ni = _int(n, 'n')
    if ni < 1:
        raise ValueError('n must be 1 or more')
    tot = 0.0
    for v in strata:
        if v < 0:
            raise ValueError('stratum sizes must be >= 0')
        tot += v
    if tot <= 0:
        raise ValueError('population is 0')
    if ni > tot:
        raise ValueError('n is bigger than the population')
    exact = []
    base = []
    got = 0
    for v in strata:
        e = ni * v / tot
        exact.append(e)
        fl = int(e)
        base.append(fl)
        got += fl
    left = ni - got
    while left > 0:
        bi = -1
        bf = -1.0
        i = 0
        while i < len(strata):
            fr = exact[i] - base[i]
            if fr > bf:
                bf = fr
                bi = i
            i += 1
        if bi < 0:
            break
        base[bi] += 1
        exact[bi] = base[bi] * 1.0
        left -= 1
    lines = ['N = ' + _f(tot) + '   n = ' + _p(ni)]
    i = 0
    while i < len(strata):
        lines.append(_p(i + 1) + ': N=' + _f(strata[i]) + ' -> ' + _p(base[i]))
        i += 1
    chk = 0
    for v in base:
        chk += v
    lines.append('total allocated = ' + _p(chk))
    lines.append(_W('n_i = n * N_i / N'))
    lines.append(_W('sampling fraction = ' + _f(ni / tot)))
    lines.append(_W('largest remainder settles the rounding'))
    return lines


# ---- L data presentation and interpretation ----------------------------------

def t_summary(data):
    n, mean, sdn, s1, sx, sxx, ss = _stats(data)
    srt = _srt(data)
    lo, q1, med, q3, hi = _five(srt)
    f1, f2, iqr = _fences(q1, q3)
    lines = ['n = ' + _p(n),
             'mean = ' + _f(mean),
             'sd (n) = ' + _f(sdn),
             'median = ' + _f(med),
             'Q1 = ' + _f(q1) + '   Q3 = ' + _f(q3),
             'IQR = ' + _f(iqr),
             'range = ' + _f(hi - lo),
             'min = ' + _f(lo) + '   max = ' + _f(hi),
             _W('sum x = ' + _f(sx) + '   sum x^2 = ' + _f(sxx)),
             _W('sd^2 = sum x^2/n - mean^2 = ' + _f(sdn * sdn)),
             _W('Sxx = ' + _f(ss) + '   s (n-1) = ' + _f(s1)),
             _W('Q at n/4 = ' + _f(n * 0.25) + ', 3n/4 = ' + _f(n * 0.75)),
             _W('1.5 IQR limits ' + _f(f1) + ' to ' + _f(f2))]
    if n < 2:
        lines.append(_WARN('s (n-1) needs n >= 2'))
    return lines


def t_fromsum(n, sumx, sumx2):
    ni = _int(n, 'n')
    if ni < 1:
        raise ValueError('n must be 1 or more')
    mean = sumx / ni
    vp = sumx2 / ni - mean * mean
    if vp < 0.0:
        raise ValueError('sum x^2 too small for that sum x')
    ss = sumx2 - sumx * sumx / ni
    if ss < 0.0:
        ss = 0.0
    lines = ['mean = ' + _f(mean),
             'sd (n) = ' + _f(math.sqrt(vp)),
             'var (n) = ' + _f(vp)]
    if ni > 1:
        lines.append('s (n-1) = ' + _f(math.sqrt(ss / (ni - 1))))
    else:
        lines.append(_WARN('s (n-1) needs n >= 2'))
    lines.append(_W('mean = ' + _f(sumx) + '/' + _p(ni) + ' = ' + _f(mean)))
    lines.append(_W('sd^2 = ' + _f(sumx2) + '/' + _p(ni) + ' - ' + _f(mean) +
                    '^2 = ' + _f(vp)))
    lines.append(_W('Sxx = sum x^2 - (sum x)^2/n = ' + _f(ss)))
    return lines


def _cf_at(cum, pos):
    for v, cf in cum:
        if pos <= cf:
            return v
    return cum[len(cum) - 1][0]


def _cf_q(cum, n, pos):
    # same n/4 rule as _qpos, walking a cumulative frequency column
    fl = int(math.floor(pos))
    if abs(pos - fl) < 1e-9 and fl >= 1 and fl < n:
        return (_cf_at(cum, fl) + _cf_at(cum, fl + 1)) / 2.0
    return _cf_at(cum, math.ceil(pos))


def t_freq(data):
    prs = _vf(data, 'freq')
    n, mean, sdn, s1, sx, sxx, ss = _wstats(prs)
    cum = []
    run = 0.0
    for v, fr in _srt(prs):
        run += fr
        cum.append((v, run))
    med = _cf_q(cum, n, n * 0.5)
    q1 = _cf_q(cum, n, n * 0.25)
    q3 = _cf_q(cum, n, n * 0.75)
    mode = cum[0][0]
    best = -1.0
    for v, fr in prs:
        if fr > best:
            best = fr
            mode = v
    return ['n = ' + _f(n),
            'mean = ' + _f(mean),
            'sd (n) = ' + _f(sdn),
            'median = ' + _f(med),
            'Q1 = ' + _f(q1) + '   Q3 = ' + _f(q3),
            'IQR = ' + _f(q3 - q1),
            'mode = ' + _f(mode),
            _W('sum fx = ' + _f(sx) + '   sum fx^2 = ' + _f(sxx)),
            _W('mean = ' + _f(sx) + '/' + _f(n) + ' = ' + _f(mean)),
            _W('sd^2 = sum fx^2/n - mean^2 = ' + _f(sdn * sdn)),
            _W('Sxx = ' + _f(ss) + '   s (n-1) = ' + _f(s1)),
            _W('quartiles by cumulative frequency')]


def t_grouped(data):
    cl = _tri(data)
    prs = []
    for lo, hi, fr in cl:
        prs.append(((lo + hi) / 2.0, fr))
    n, mean, sdn, s1, sx, sxx, ss = _wstats(prs)
    med = _cinterp(cl, n * 0.5)
    q1 = _cinterp(cl, n * 0.25)
    q3 = _cinterp(cl, n * 0.75)
    md = cl[0]
    bestd = -1.0
    for lo, hi, fr in cl:
        d = fr / (hi - lo)
        if d > bestd:
            bestd = d
            md = (lo, hi, fr)
    return ['n = ' + _f(n),
            'mean = ' + _f(mean),
            'sd (n) = ' + _f(sdn),
            'median = ' + _f(med),
            'Q1 = ' + _f(q1) + '   Q3 = ' + _f(q3),
            'IQR = ' + _f(q3 - q1),
            'modal class ' + _f(md[0]) + '-' + _f(md[1]),
            _W('midpoints: sum fx = ' + _f(sx)),
            _W('sum fx^2 = ' + _f(sxx)),
            _W('sd^2 = sum fx^2/n - mean^2 = ' + _f(sdn * sdn)),
            _W('Sxx = ' + _f(ss) + '   s (n-1) = ' + _f(s1)),
            _W('median at n/2 = ' + _f(n * 0.5) + ' by interpolation'),
            _W('modal class by frequency density'),
            _WARN('estimates: midpoints, not raw data')]


def t_coding(a, b, ybar, sdy):
    if b == 0:
        raise ValueError('b must not be 0')
    if sdy < 0:
        raise ValueError('sd of y must be >= 0')
    xb = a + b * ybar
    sdx = abs(b) * sdy
    return ['mean x = ' + _f(xb),
            'sd x = ' + _f(sdx),
            _W('y = (x - ' + _f(a) + ')/' + _f(b)),
            _W('so x = ' + _f(a) + ' + ' + _f(b) + 'y'),
            _W('mean x = a + b*mean y = ' + _f(xb)),
            _W('sd x = |b| * sd y = ' + _f(sdx))]


def t_outliers(data):
    n, mean, sdn, s1, sx, sxx, ss = _stats(data)
    srt = _srt(data)
    lo, q1, med, q3, hi = _five(srt)
    f1, f2, iqr = _fences(q1, q3)
    m1 = mean - 2.0 * sdn
    m2 = mean + 2.0 * sdn
    a = []
    b = []
    for v in srt:
        if v < f1 or v > f2:
            a.append(_f(v))
        if v < m1 or v > m2:
            b.append(_f(v))
    lines = ['1.5 IQR: ' + _f(f1) + ' to ' + _f(f2)]
    if a:
        for ln in _chunk(a, 26):
            lines.append('out: ' + ln)
    else:
        lines.append('1.5 IQR outliers: none')
    lines.append('2 sd: ' + _f(m1) + ' to ' + _f(m2))
    if b:
        for ln in _chunk(b, 26):
            lines.append('out: ' + ln)
    else:
        lines.append('2 sd outliers: none')
    lines.append(_W('Q1 = ' + _f(q1) + '  Q3 = ' + _f(q3) +
                    '  IQR = ' + _f(iqr)))
    lines.append(_W('mean = ' + _f(mean) + '   sd (n) = ' + _f(sdn)))
    lines.append(_WARN('an outlier can still be genuine data'))
    return lines


def t_hist(data):
    cl = _tri(data)
    import plot
    bars = []
    tot = 0.0
    for lo, hi, fr in cl:
        bars.append((lo, hi, fr / (hi - lo)))
        tot += fr
    plot.run(bars, cl[0][0], cl[len(cl) - 1][1], 'bars', 'Histogram')
    lines = ['total frequency = ' + _f(tot)]
    i = 0
    while i < len(cl):
        lines.append(_f(cl[i][0]) + '-' + _f(cl[i][1]) + ' f=' + _f(cl[i][2]) +
                     ' fd=' + _f(bars[i][2]))
        i += 1
    lines.append(_W('fd = frequency / class width'))
    lines.append(_W('area of a bar = frequency'))
    return lines


def t_box(data):
    srt = _srt(data)
    lo, q1, med, q3, hi = _five(srt)
    f1, f2, iqr = _fences(q1, q3)
    outs = []
    keep = []
    for v in srt:
        if v < f1 or v > f2:
            outs.append(v)
        else:
            keep.append(v)
    wlo = keep[0] if keep else lo
    whi = keep[len(keep) - 1] if keep else hi
    import plot
    pts = [(lo, 1.0), (q1, 1.0), (med, 1.0), (q3, 1.0), (hi, 1.0)]
    for v in outs:
        pts.append((v, 2.0))
    plot.run(pts, lo, hi, 'points', 'Box plot')
    lines = ['min = ' + _f(lo) + '   max = ' + _f(hi),
             'Q1 = ' + _f(q1),
             'median = ' + _f(med),
             'Q3 = ' + _f(q3),
             'IQR = ' + _f(iqr),
             'whiskers ' + _f(wlo) + ' to ' + _f(whi)]
    if outs:
        for ln in _chunk([_f(v) for v in outs], 26):
            lines.append('out: ' + ln)
    else:
        lines.append('outliers: none')
    lines.append(_W('1.5 IQR limits ' + _f(f1) + ' to ' + _f(f2)))
    lines.append(_W('plot row y=1 five figures, y=2 outliers'))
    return lines


def t_cumfreq(data):
    cl = _tri(data)
    cf = []
    run = 0.0
    for lo, hi, fr in cl:
        run += fr
        cf.append(run)
    tot = run
    med = _cinterp(cl, tot * 0.5)
    q1 = _cinterp(cl, tot * 0.25)
    q3 = _cinterp(cl, tot * 0.75)
    import plot
    pts = [(cl[0][0], 0.0)]
    i = 0
    while i < len(cl):
        pts.append((cl[i][1], cf[i]))
        i += 1
    plot.run(pts, cl[0][0], cl[len(cl) - 1][1], 'points', 'Cumulative freq')
    lines = ['total frequency = ' + _f(tot),
             'median = ' + _f(med),
             'Q1 = ' + _f(q1) + '   Q3 = ' + _f(q3),
             'IQR = ' + _f(q3 - q1)]
    i = 0
    while i < len(cl):
        lines.append(_W('<= ' + _f(cl[i][1]) + '   cf = ' + _f(cf[i])))
        i += 1
    lines.append(_W('read at n/4, n/2, 3n/4 of ' + _f(tot)))
    lines.append(_WARN('estimates: plot at upper boundaries'))
    return lines


def t_scatter(data):
    pts = _xy(data)
    a, b, r, dxx, dyy, dxy = _lin(pts)
    import plot
    plot.run(pts, 0.0, 1.0, 'points', 'Scatter')
    lines = [_yeq(a, b)]
    if r is None:
        lines.append(_WARN('all y equal: r undefined'))
    else:
        lines.append('r = ' + _f(r))
    lines.append('gradient b = ' + _f(b))
    lines.append('intercept a = ' + _f(a))
    lines.append('n = ' + _p(len(pts)))
    lines.append(_W('Sxx = ' + _f(dxx) + '   Syy = ' + _f(dyy)))
    lines.append(_W('Sxy = ' + _f(dxy)))
    lines.append(_W('b = Sxy/Sxx = ' + _f(b)))
    lines.append(_W('a = ybar - b*xbar = ' + _f(a)))
    if r is not None:
        lines.append(_W('r = Sxy/sqrt(Sxx*Syy) = ' + _f(r)))
    lines.append(_WARN('correlation is not causation'))
    return lines


def t_predict(x0, data):
    pts = _xy(data)
    a, b, r, dxx, dyy, dxy = _lin(pts)
    lo = pts[0][0]
    hi = pts[0][0]
    for x, y in pts:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    y0 = a + b * x0
    lines = ['y = ' + _f(y0) + ' at x = ' + _f(x0),
             _yeq(a, b),
             _W('data x range ' + _f(lo) + ' to ' + _f(hi)),
             _W('y = ' + _f(a) + ' + ' + _f(b) + '*' + _f(x0) +
                ' = ' + _f(y0))]
    if x0 < lo or x0 > hi:
        lines.append(_WARN('extrapolation: outside the data'))
    else:
        lines.append(_W('interpolation: inside the data'))
    if r is not None:
        lines.append(_W('r = ' + _f(r) + ': weak r weakens the estimate'))
    return lines


# ---- M probability -----------------------------------------------------------

def t_union(pA, pB, pAandB):
    _prob(pA, 'P(A)')
    _prob(pB, 'P(B)')
    _prob(pAandB, 'P(A and B)')
    if pAandB > pA or pAandB > pB:
        raise ValueError('P(A and B) exceeds P(A) or P(B)')
    u = pA + pB - pAandB
    ind = pA * pB
    lines = ['P(A or B) = ' + _f(u),
             "P(A') = " + _f(1.0 - pA),
             "P(not A and not B) = " + _f(1.0 - u)]
    if abs(ind - pAandB) < 1e-9:
        lines.append('independent: yes')
    else:
        lines.append('independent: no')
    if pAandB == 0.0:
        lines.append('mutually exclusive: yes')
    else:
        lines.append('mutually exclusive: no')
    lines.append(_W('P(AuB) = P(A)+P(B)-P(AnB) = ' + _f(u)))
    lines.append(_W('P(A)P(B) = ' + _f(ind) + ', P(AnB) = ' + _f(pAandB)))
    if pB > 0:
        lines.append(_W('P(A|B) = ' + _f(pAandB / pB)))
    if pA > 0:
        lines.append(_W('P(B|A) = ' + _f(pAandB / pA)))
    return lines


def t_cond(pAandB, pB):
    _prob(pAandB, 'P(A and B)')
    _prob(pB, 'P(B)')
    if pB <= 0.0:
        raise ValueError('P(B) must be > 0')
    if pAandB > pB:
        raise ValueError('P(A and B) exceeds P(B)')
    c = pAandB / pB
    return ['P(A|B) = ' + _f(c),
            "P(A'|B) = " + _f(1.0 - c),
            _W('P(A|B) = P(A and B)/P(B)'),
            _W('= ' + _f(pAandB) + '/' + _f(pB) + ' = ' + _f(c)),
            _W('rearranged: P(A and B) = P(A|B) P(B)')]


def t_twoway(nAB, nAnotB, nBnotA, nNeither):
    for v in (nAB, nAnotB, nBnotA, nNeither):
        if v < 0:
            raise ValueError('counts must be >= 0')
    tot = nAB + nAnotB + nBnotA + nNeither
    if tot <= 0:
        raise ValueError('total count is 0')
    pa = (nAB + nAnotB) / (tot * 1.0)
    pb = (nAB + nBnotA) / (tot * 1.0)
    pab = nAB / (tot * 1.0)
    lines = ['total = ' + _f(tot),
             'P(A) = ' + _p(pa) + '   P(B) = ' + _p(pb),
             'P(A and B) = ' + _p(pab),
             'P(A or B) = ' + _p(pa + pb - pab)]
    if nAB + nBnotA > 0:
        lines.append('P(A|B) = ' + _p(nAB / ((nAB + nBnotA) * 1.0)))
    if nAB + nAnotB > 0:
        lines.append('P(B|A) = ' + _p(nAB / ((nAB + nAnotB) * 1.0)))
    if abs(pa * pb - pab) < 1e-9:
        lines.append('independent: yes')
    else:
        lines.append('independent: no')
    lines.append(_W('regions ' + _f(nAB) + ', ' + _f(nAnotB) + ', ' +
                    _f(nBnotA) + ', ' + _f(nNeither)))
    lines.append(_W('P(A)P(B) = ' + _p(pa * pb)))
    lines.append(_W('P(A|B) = n(A and B)/n(B)'))
    return lines


def t_tree(pA, pB_A, pB_notA):
    _prob(pA, 'P(A)')
    _prob(pB_A, 'P(B|A)')
    _prob(pB_notA, "P(B|not A)")
    na = 1.0 - pA
    ab = pA * pB_A
    anb = pA * (1.0 - pB_A)
    nab = na * pB_notA
    nanb = na * (1.0 - pB_notA)
    pb = ab + nab
    lines = ['P(B) = ' + _f(pb),
             "P(B') = " + _f(1.0 - pb)]
    if pb > 0:
        lines.append('P(A|B) = ' + _f(ab / pb))
        lines.append("P(A'|B) = " + _f(nab / pb))
    else:
        lines.append(_WARN('P(B) = 0: P(A|B) undefined'))
    if pb < 1.0:
        lines.append("P(A|B') = " + _f(anb / (1.0 - pb)))
    lines.append(_W('P(A and B) = ' + _f(ab)))
    lines.append(_W("P(A and B') = " + _f(anb)))
    lines.append(_W("P(A' and B) = " + _f(nab)))
    lines.append(_W("P(A' and B') = " + _f(nanb)))
    lines.append(_W("P(B) = P(A)P(B|A) + P(A')P(B|A')"))
    lines.append(_W('P(A|B) = P(A and B)/P(B)'))
    return lines


# ---- N statistical distributions ---------------------------------------------

def t_bpmf(n, p, k):
    ni = _bin(n, p)
    ki = _int(k, 'k')
    pk = casutil.binom_pmf(ni, p, ki)
    lines = ['P(X = ' + _p(ki) + ') = ' + _f(pk)]
    if ki < 0 or ki > ni:
        lines.append(_WARN('k is outside 0..' + _p(ni)))
        return lines
    lines.append(_W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')'))
    lines.append(_W('nCk = ' + _p(casutil.ncr(ni, ki))))
    lines.append(_W('nCk p^k (1-p)^(n-k) = ' + _f(pk)))
    return lines


def t_bcdf(n, p, k):
    ni = _bin(n, p)
    ki = _int(k, 'k')
    c = casutil.binom_cdf(ni, p, ki)
    return ['P(X <= ' + _p(ki) + ') = ' + _f(c),
            'P(X < ' + _p(ki) + ') = ' + _f(casutil.binom_cdf(ni, p, ki - 1)),
            'P(X > ' + _p(ki) + ') = ' + _f(1.0 - c),
            _W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')'),
            _W('sum of P(X=0) .. P(X=' + _p(ki) + ')')]


def t_bge(n, p, k):
    ni = _bin(n, p)
    ki = _int(k, 'k')
    below = casutil.binom_cdf(ni, p, ki - 1)
    return ['P(X >= ' + _p(ki) + ') = ' + _f(1.0 - below),
            'P(X > ' + _p(ki) + ') = ' + _f(1.0 - casutil.binom_cdf(ni, p, ki)),
            _W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')'),
            _W('P(X >= k) = 1 - P(X <= k-1)'),
            _W('P(X <= ' + _p(ki - 1) + ') = ' + _f(below))]


def t_brange(n, p, a, b):
    ni = _bin(n, p)
    ai = _int(a, 'a')
    bi = _int(b, 'b')
    if bi < ai:
        raise ValueError('b must be at least a')
    lo = casutil.binom_cdf(ni, p, ai - 1)
    hi = casutil.binom_cdf(ni, p, bi)
    return ['P(' + _p(ai) + ' <= X <= ' + _p(bi) + ') = ' + _f(hi - lo),
            _W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')'),
            _W('P(X <= ' + _p(bi) + ') = ' + _f(hi)),
            _W('P(X <= ' + _p(ai - 1) + ') = ' + _f(lo)),
            _W('difference = ' + _f(hi - lo))]


def t_binv(n, p, prob):
    ni = _bin(n, p)
    if prob <= 0.0 or prob > 1.0:
        raise ValueError('prob must be between 0 and 1')
    acc = 0.0
    prev = 0.0
    k = 0
    while True:
        prev = acc
        acc += casutil.binom_pmf(ni, p, k)
        if acc >= prob - 1e-12 or k >= ni:
            break
        k += 1
    return ['least k with P(X<=k) >= ' + _f(prob),
            'k = ' + _p(k),
            'P(X <= ' + _p(k) + ') = ' + _f(acc),
            _W('P(X <= ' + _p(k - 1) + ') = ' + _f(prev)),
            _W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')')]


def t_bmv(n, p):
    ni = _bin(n, p)
    mean = ni * p
    var = ni * p * (1.0 - p)
    return ['mean = np = ' + _f(mean),
            'variance = np(1-p) = ' + _f(var),
            'sd = ' + _f(math.sqrt(var)),
            _W('X ~ B(' + _p(ni) + ', ' + _f(p) + ')'),
            _W('np = ' + _p(ni) + ' * ' + _f(p) + ' = ' + _f(mean)),
            _W('npq = ' + _f(mean) + ' * ' + _f(1.0 - p) + ' = ' + _f(var))]


def t_nlt(mu, sigma, x):
    _sd(sigma)
    z = (x - mu) / sigma
    return ['P(X < ' + _f(x) + ') = ' + _f(casutil.phi(z)),
            'z = ' + _f(z),
            _W('X ~ N(' + _f(mu) + ', ' + _f(sigma) + '^2)'),
            _W('z = (' + _f(x) + ' - ' + _f(mu) + ')/' + _f(sigma) +
               ' = ' + _f(z)),
            _W('P(X < x) = P(Z < z)')]


def t_ngt(mu, sigma, x):
    _sd(sigma)
    z = (x - mu) / sigma
    return ['P(X > ' + _f(x) + ') = ' + _f(1.0 - casutil.phi(z)),
            'z = ' + _f(z),
            _W('X ~ N(' + _f(mu) + ', ' + _f(sigma) + '^2)'),
            _W('P(X > x) = 1 - P(X < x)'),
            _W('P(X < ' + _f(x) + ') = ' + _f(casutil.phi(z)))]


def t_nbetween(mu, sigma, a, b):
    _sd(sigma)
    if b < a:
        raise ValueError('b must be at least a')
    za = (a - mu) / sigma
    zb = (b - mu) / sigma
    return ['P(a < X < b) = ' + _f(casutil.phi(zb) - casutil.phi(za)),
            'z(a) = ' + _f(za) + '   z(b) = ' + _f(zb),
            _W('X ~ N(' + _f(mu) + ', ' + _f(sigma) + '^2)'),
            _W('P(X < b) = ' + _f(casutil.phi(zb))),
            _W('P(X < a) = ' + _f(casutil.phi(za))),
            _W('subtract: ' + _f(casutil.phi(zb) - casutil.phi(za)))]


def t_ninv(mu, sigma, p):
    _sd(sigma)
    if p <= 0.0 or p >= 1.0:
        raise ValueError('p must be between 0 and 1')
    z = casutil.invphi(p)
    x = mu + z * sigma
    return ['x = ' + _f(x),
            'z = ' + _f(z),
            _W('P(X < x) = ' + _f(p)),
            _W('x = mu + z sigma'),
            _W('= ' + _f(mu) + ' + ' + _f(z) + ' * ' + _f(sigma) +
               ' = ' + _f(x))]


def t_std(mu, sigma, x):
    _sd(sigma)
    z = (x - mu) / sigma
    return ['z = ' + _f(z),
            'P(X < ' + _f(x) + ') = ' + _f(casutil.phi(z)),
            _W('z = (x - mu)/sigma'),
            _W('= (' + _f(x) + ' - ' + _f(mu) + ')/' + _f(sigma) +
               ' = ' + _f(z)),
            _W('z counts sd above the mean')]


def t_nfind(mu, sigma, x, p):
    if p is None or p <= 0.0 or p >= 1.0:
        raise ValueError('p must be between 0 and 1')
    if (mu is None) == (sigma is None):
        raise ValueError('type ? for exactly one of mu, sigma')
    z = casutil.invphi(p)
    if abs(z) < 1e-9:
        raise ValueError('p = 0.5 gives z = 0: no solution')
    if mu is None:
        _sd(sigma)
        v = x - z * sigma
        return ['mu = ' + _f(v),
                'z = ' + _f(z),
                _W('P(X < ' + _f(x) + ') = ' + _f(p) + ', z = ' + _f(z)),
                _W('mu = x - z sigma'),
                _W('= ' + _f(x) + ' - ' + _f(z) + ' * ' + _f(sigma) +
                   ' = ' + _f(v))]
    v = (x - mu) / z
    if v <= 0.0:
        raise ValueError('that p gives sigma <= 0')
    return ['sigma = ' + _f(v),
            'z = ' + _f(z),
            _W('P(X < ' + _f(x) + ') = ' + _f(p) + ', z = ' + _f(z)),
            _W('sigma = (x - mu)/z'),
            _W('= (' + _f(x) + ' - ' + _f(mu) + ')/' + _f(z) + ' = ' + _f(v))]


def t_nboth(x1, p1, x2, p2):
    if p1 <= 0.0 or p1 >= 1.0 or p2 <= 0.0 or p2 >= 1.0:
        raise ValueError('p must be between 0 and 1')
    z1 = casutil.invphi(p1)
    z2 = casutil.invphi(p2)
    if abs(z2 - z1) < 1e-9:
        raise ValueError('the two probabilities must differ')
    sig = (x2 - x1) / (z2 - z1)
    if sig <= 0.0:
        raise ValueError('that data gives sigma <= 0')
    mu = x1 - z1 * sig
    return ['mu = ' + _f(mu),
            'sigma = ' + _f(sig),
            _W('z1 = ' + _f(z1) + '   z2 = ' + _f(z2)),
            _W('x = mu + z sigma at both points'),
            _W('sigma = (x2-x1)/(z2-z1) = ' + _f(sig)),
            _W('mu = x1 - z1 sigma = ' + _f(mu))]


def t_ninfl(mu, sigma):
    _sd(sigma)
    return ['inflection at ' + _f(mu - sigma),
            'and at ' + _f(mu + sigma),
            _W('points of inflection are mu +/- sigma'),
            _W('P(mu-s < X < mu+s) = ' +
               _f(casutil.phi(1.0) - casutil.phi(-1.0)))]


def t_dunif(n):
    ni = _int(n, 'n')
    if ni < 1:
        raise ValueError('n must be 1 or more')
    mean = (ni + 1) / 2.0
    var = (ni * ni - 1) / 12.0
    return ['P(X = x) = ' + _p(1.0 / ni),
            'mean = ' + _f(mean),
            'variance = ' + _f(var),
            'sd = ' + _f(math.sqrt(var)),
            _W('X uniform on 1..' + _p(ni)),
            _W('mean = (n+1)/2, var = (n^2-1)/12')]


def t_drv(data):
    prs = _vf(data, 'p')
    tp = 0.0
    ex = 0.0
    ex2 = 0.0
    for v, pr in prs:
        if pr > 1.0:
            raise ValueError('each p must be between 0 and 1')
        tp += pr
        ex += v * pr
        ex2 += v * v * pr
    var = ex2 - ex * ex
    if var < 0.0:
        var = 0.0
    lines = ['E(X) = ' + _f(ex),
             'Var(X) = ' + _f(var),
             'sd = ' + _f(math.sqrt(var)),
             'sum p = ' + _f(tp),
             _W('E(X) = sum x P(X=x) = ' + _f(ex)),
             _W('E(X^2) = ' + _f(ex2)),
             _W('Var = E(X^2) - E(X)^2 = ' + _f(var))]
    if abs(tp - 1.0) > 1e-6:
        lines.append(_WARN('probabilities do not sum to 1'))
    return lines


# ---- O statistical hypothesis testing ----------------------------------------

def _htbin(n, p0, x, sig, tail):
    ni = _bin(n, p0)
    xi = _int(x, 'x')
    if xi < 0 or xi > ni:
        raise ValueError('x must be between 0 and n')
    if p0 <= 0.0 or p0 >= 1.0:
        raise ValueError('p0 must be strictly between 0 and 1')
    a = _alpha(sig)
    lo = casutil.binom_cdf(ni, p0, xi)
    up = 1.0 - casutil.binom_cdf(ni, p0, xi - 1)
    lines = []
    if tail == 'low':
        cr = _cr_low(ni, p0, a)
        rej = xi <= cr
        lines.append(_verdict(rej, sig))
        lines.append('p-value = ' + _f(lo))
        lines.append('CR: X <= ' + _p(cr) if cr >= 0 else 'CR: empty')
        lines.append(_W('H0: p = ' + _f(p0) + '   H1: p < ' + _f(p0)))
        lines.append(_W('p-value = P(X <= ' + _p(xi) + ') = ' + _f(lo)))
        lines.append(_W('compare with alpha = ' + _f(a)))
        if cr >= 0:
            lines.append(_W('P(X <= ' + _p(cr) + ') = ' +
                            _f(casutil.binom_cdf(ni, p0, cr))))
    elif tail == 'up':
        cr = _cr_up(ni, p0, a)
        rej = xi >= cr
        lines.append(_verdict(rej, sig))
        lines.append('p-value = ' + _f(up))
        lines.append('CR: X >= ' + _p(cr) if cr <= ni else 'CR: empty')
        lines.append(_W('H0: p = ' + _f(p0) + '   H1: p > ' + _f(p0)))
        lines.append(_W('p-value = P(X >= ' + _p(xi) + ') = ' + _f(up)))
        lines.append(_W('compare with alpha = ' + _f(a)))
        if cr <= ni:
            lines.append(_W('P(X >= ' + _p(cr) + ') = ' +
                            _f(1.0 - casutil.binom_cdf(ni, p0, cr - 1))))
    else:
        h = a / 2.0
        cl = _cr_low(ni, p0, h)
        cu = _cr_up(ni, p0, h)
        pv = 2.0 * (lo if lo < up else up)
        if pv > 1.0:
            pv = 1.0
        rej = (xi <= cl) or (xi >= cu)
        lines.append(_verdict(rej, sig))
        lines.append('p-value = ' + _f(pv))
        if cl < 0 and cu > ni:
            s = 'CR: empty'
        else:
            s = 'CR: '
            if cl >= 0:
                s += 'X <= ' + _p(cl)
                if cu <= ni:
                    s += ' or '
            if cu <= ni:
                s += 'X >= ' + _p(cu)
        lines.append(s)
        lines.append(_W('H0: p = ' + _f(p0) + '   H1: p =/= ' + _f(p0)))
        lines.append(_W('each tail uses alpha/2 = ' + _f(h)))
        lines.append(_W('P(X <= ' + _p(xi) + ') = ' + _f(lo)))
        lines.append(_W('P(X >= ' + _p(xi) + ') = ' + _f(up)))
        lines.append(_W('p-value = 2 * smaller tail = ' + _f(pv)))
    lines.append(_W('X ~ B(' + _p(ni) + ', ' + _f(p0) + '), x = ' + _p(xi)))
    lines.append(_WARN('significance = P(wrongly rejecting H0)'))
    return lines


def t_htb_low(n, p0, x, sig):
    return _htbin(n, p0, x, sig, 'low')


def t_htb_up(n, p0, x, sig):
    return _htbin(n, p0, x, sig, 'up')


def t_htb_two(n, p0, x, sig):
    return _htbin(n, p0, x, sig, 'two')


def _ztest(mu0, sigma, n, xbar, sig, tail):
    _sd(sigma)
    ni = _int(n, 'n')
    if ni < 1:
        raise ValueError('n must be 1 or more')
    a = _alpha(sig)
    se = sigma / math.sqrt(ni)
    z = (xbar - mu0) / se
    if tail == 'two':
        zc, tab = _zc(a / 2.0)
        pv = 2.0 * (1.0 - casutil.phi(abs(z)))
        rej = abs(z) >= zc
        crit = '+/- ' + _c(zc, 4)
        h1 = 'H1: mu =/= ' + _f(mu0)
    elif tail == 'low':
        zc, tab = _zc(a)
        pv = casutil.phi(z)
        rej = z <= -zc
        crit = '-' + _c(zc, 4)
        h1 = 'H1: mu < ' + _f(mu0)
    else:
        zc, tab = _zc(a)
        pv = 1.0 - casutil.phi(z)
        rej = z >= zc
        crit = _c(zc, 4)
        h1 = 'H1: mu > ' + _f(mu0)
    lines = [_verdict(rej, sig),
             'z = ' + _f(z),
             'p-value = ' + _f(pv),
             'critical z = ' + crit,
             _W('H0: mu = ' + _f(mu0) + '   ' + h1),
             _W('z = (xbar - mu)/(sigma/sqrt(n))'),
             _W('= (' + _f(xbar) + ' - ' + _f(mu0) + ')/' + _f(se) +
                ' = ' + _f(z)),
             _W('standard error = ' + _f(se))]
    if not tab:
        lines.append(_WARN('level not in tables: z from the cdf'))
    lines.append(_WARN('needs a Normal population, sigma known'))
    return lines


def t_htz_low(mu0, sigma, n, xbar, sig):
    return _ztest(mu0, sigma, n, xbar, sig, 'low')


def t_htz_up(mu0, sigma, n, xbar, sig):
    return _ztest(mu0, sigma, n, xbar, sig, 'up')


def t_htz_two(mu0, sigma, n, xbar, sig):
    return _ztest(mu0, sigma, n, xbar, sig, 'two')


def _htr(r, n, sig, tails):
    if r < -1.0 or r > 1.0:
        raise ValueError('r must be between -1 and 1')
    ni = _int(n, 'n')
    if ni < 3:
        raise ValueError('n must be 3 or more')
    a = _alpha(sig)
    q = a if tails == 1 else a / 2.0
    cv = tables.pmcc_crit(ni, q)
    if cv is None:
        return ['no critical value',
                'r = ' + _f(r) + '   n = ' + _p(ni),
                _W('table holds n = 4..30 at 5, 2.5, 1, 0.5%'),
                _WARN('no entry for n = ' + _p(ni) + ' at ' +
                      _f(q * 100.0) + '%')]
    ar = r if r >= 0 else -r
    lines = [_verdict(ar >= cv, sig),
             'r = ' + _f(r),
             'critical value = ' + _c(cv, 4),
             _W('H0: rho = 0 (no correlation)')]
    if tails == 1:
        if r >= 0:
            lines.append(_W('H1: rho > 0, one tail at ' + _f(sig) + '%'))
        else:
            lines.append(_W('H1: rho < 0, one tail at ' + _f(sig) + '%'))
        lines.append(_WARN('choose H1 before seeing r'))
    else:
        lines.append(_W('H1: rho =/= 0, two tail at ' + _f(sig) + '%'))
        lines.append(_W('table read at ' + _f(q * 100.0) + '% one tail'))
    lines.append(_W('compare |r| = ' + _f(ar) + ' with ' + _c(cv, 4)))
    lines.append(_WARN('a sample r tests the population rho'))
    return lines


def t_htr1(r, n, sig):
    return _htr(r, n, sig, 1)


def t_htr2(r, n, sig):
    return _htr(r, n, sig, 2)


def t_zcrit(sig):
    a = _alpha(sig)
    z1, t1 = _zc(a)
    z2, t2 = _zc(a / 2.0)
    lines = ['1 tail z = ' + _c(z1, 4),
             '2 tail z = +/- ' + _c(z2, 4),
             _W('one tail: P(Z > z) = ' + _f(a)),
             _W('two tail: P(Z > z) = ' + _f(a / 2.0))]
    if not (t1 and t2):
        lines.append(_WARN('not a tabulated level: z from the cdf'))
    return lines


def t_rcrit(n, sig):
    ni = _int(n, 'n')
    if ni < 3:
        raise ValueError('n must be 3 or more')
    a = _alpha(sig)
    c1 = tables.pmcc_crit(ni, a)
    c2 = tables.pmcc_crit(ni, a / 2.0)
    lines = []
    if c1 is None:
        lines.append('1 tail: no table entry')
    else:
        lines.append('1 tail r = ' + _c(c1, 4))
    if c2 is None:
        lines.append('2 tail: no table entry')
    else:
        lines.append('2 tail r = +/- ' + _c(c2, 4))
    lines.append(_W('n = ' + _p(ni) + ' at ' + _f(sig) + '%'))
    lines.append(_W('two tail reads the ' + _f(a * 50.0) + '% column'))
    if c1 is None or c2 is None:
        lines.append(_WARN('table holds n = 4..30 at 5, 2.5, 1, 0.5%'))
    return lines


SECTIONS = [
    ('K', 'Statistical sampling', [
        ('Simple random sample', 'N,n,seed?', t_srs),
        ('Systematic sample', 'N,n,seed?', t_systematic),
        ('Stratified sample', 'n,strata*', t_strat),
    ]),
    ('L', 'Data presentation', [
        ('Summary stats', 'data*', t_summary),
        ('Stats from summary', 'n,sumx,sumx2', t_fromsum),
        ('Frequency table', 'value freq pairs*', t_freq),
        ('Grouped table', 'lower upper freq*', t_grouped),
        ('Coding x from y', 'a,b,ybar,sdy', t_coding),
        ('Outliers', 'data*', t_outliers),
        ('Histogram', 'lower upper freq*', t_hist),
        ('Box plot', 'data*', t_box),
        ('Cumulative frequency', 'lower upper freq*', t_cumfreq),
        ('Scatter PMCC regress', 'x y pairs*', t_scatter),
        ('Regression predict', 'x0,x y pairs*', t_predict),
    ]),
    ('M', 'Probability', [
        ('P(A or B)', 'pA,pB,pAandB', t_union),
        ('Conditional P(A|B)', 'pAandB,pB', t_cond),
        ('Two-way table counts', 'nAB,nAnotB,nBnotA,nNeither', t_twoway),
        ('Tree two stage', 'pA,pB_A,pB_notA', t_tree),
    ]),
    ('N', 'Statistical distributions', [
        ('Binomial P(X=k)', 'n,p,k', t_bpmf),
        ('Binomial P(X<=k)', 'n,p,k', t_bcdf),
        ('Binomial P(X>=k)', 'n,p,k', t_bge),
        ('Binomial P(a<=X<=b)', 'n,p,a,b', t_brange),
        ('Binomial least k', 'n,p,prob', t_binv),
        ('Binomial mean var', 'n,p', t_bmv),
        ('Normal P(X<x)', 'mu,sigma,x', t_nlt),
        ('Normal P(X>x)', 'mu,sigma,x', t_ngt),
        ('Normal P(a<X<b)', 'mu,sigma,a,b', t_nbetween),
        ('Inverse Normal', 'mu,sigma,p', t_ninv),
        ('Standardise z', 'mu,sigma,x', t_std),
        ('Normal find mu or sd', 'mu,sigma,x,p', t_nfind),
        ('Normal mu and sd', 'x1,p1,x2,p2', t_nboth),
        ('Normal inflection', 'mu,sigma', t_ninfl),
        ('Discrete uniform', 'n', t_dunif),
        ('Discrete distribution', 'value prob pairs*', t_drv),
    ]),
    ('O', 'Hypothesis testing', [
        ('HT binomial lower', 'n,p0,x,sig', t_htb_low),
        ('HT binomial upper', 'n,p0,x,sig', t_htb_up),
        ('HT binomial two tail', 'n,p0,x,sig', t_htb_two),
        ('z test mean lower', 'mu0,sigma,n,xbar,sig', t_htz_low),
        ('z test mean upper', 'mu0,sigma,n,xbar,sig', t_htz_up),
        ('z test mean two tail', 'mu0,sigma,n,xbar,sig', t_htz_two),
        ('PMCC test 1 tail', 'r,n,sig', t_htr1),
        ('PMCC test 2 tail', 'r,n,sig', t_htr2),
        ('Critical z value', 'sig', t_zcrit),
        ('PMCC crit value', 'n,sig', t_rcrit),
    ]),
]
