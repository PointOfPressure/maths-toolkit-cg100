import math
import casui
import casutil

_asknum = casutil.asknum
_getlist = casutil.asklist
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now
_fact = casutil.fact
_ncr = casutil.ncr
_bpmf = casutil.binom_pmf
_bcdf = casutil.binom_cdf
_erf = casutil.erf
_phi = casutil.phi
_inv_phi = casutil.invphi

def _fn(x):
    return casutil.fmt(x, 5)

def _sorted(a):
    b = list(a)
    n = len(b)
    i = 1
    while i < n:
        key = b[i]
        j = i - 1
        while j >= 0 and b[j] > key:
            b[j + 1] = b[j]
            j -= 1
        b[j + 1] = key
        i += 1
    return b

def _quant(srt, pos):
    n = len(srt)
    if n == 1:
        return srt[0]
    if pos < 1.0:
        pos = 1.0
    if pos > n:
        pos = float(n)
    lo = int(pos)
    if lo >= n:
        return srt[n - 1]
    frac = pos - lo
    return srt[lo - 1] + frac * (srt[lo] - srt[lo - 1])

def _median_of(srt):
    # median of an already-sorted list, None for an empty one
    m = len(srt)
    if m == 0:
        return None
    mid = m // 2
    if m % 2 == 1:
        return srt[mid]
    return (srt[mid - 1] + srt[mid]) / 2.0

def _quartiles_split(srt):
    # OCR B (MEI) quartile method for a raw data list: Q1 is the median of
    # the lower half of the sorted data and Q3 the median of the upper half,
    # with the overall median itself excluded from both halves when n is odd.
    n = len(srt)
    mid = n // 2
    if n % 2 == 1:
        lower = srt[0:mid]
        upper = srt[mid + 1:]
    else:
        lower = srt[0:mid]
        upper = srt[mid:]
    return (_median_of(lower), _median_of(srt), _median_of(upper))

def t_summary():
    a = _getlist('Data list:')
    if a is None or len(a) == 0:
        _show('Summary', ['Need data.'])
        return
    n = len(a)
    srt = _sorted(a)
    tot = 0.0
    for v in a:
        tot += v
    mean = tot / n
    med = _quant(srt, (n + 1) * 0.5)
    q1 = _quant(srt, (n + 1) * 0.25)
    q3 = _quant(srt, (n + 1) * 0.75)
    iqr = q3 - q1
    rng = srt[n - 1] - srt[0]
    ss = 0.0
    for v in a:
        ss += (v - mean) * (v - mean)
    varp = ss / n
    sdp = math.sqrt(varp)
    if n > 1:
        vars_ = ss / (n - 1)
        sds = math.sqrt(vars_)
    else:
        vars_ = 0.0
        sds = 0.0
    lf = q1 - 1.5 * iqr
    uf = q3 + 1.5 * iqr
    lines = []
    lines.append('n = ' + str(n))
    lines.append('mean = ' + _fn(mean))
    lines.append('median = ' + _fn(med))
    lines.append('Q1 = ' + _fn(q1) + '  Q3 = ' + _fn(q3))
    lines.append('IQR = ' + _fn(iqr))
    lines.append('range = ' + _fn(rng))
    lines.append('min = ' + _fn(srt[0]) + ' max = ' + _fn(srt[n - 1]))
    lines.append('Sxx = ' + _fn(ss))
    lines.append('s (n-1) sd = ' + _fn(sds))
    lines.append('sd (n) = ' + _fn(sdp))
    lines.append('var (n) = ' + _fn(varp))
    lines.append('fences ' + _fn(lf) + ' .. ' + _fn(uf))
    outs = []
    for v in srt:
        if v < lf or v > uf:
            outs.append(_fn(v))
    if outs:
        lines.append('outliers ' + ' '.join(outs))
    else:
        lines.append('outliers: none')
    _pages('Summary stats', lines)

def t_boxplot():
    a = _getlist('Data list:')
    if a is None or len(a) == 0:
        _show('Box plot', ['Need data.'])
        return
    srt = _sorted(a)
    n = len(srt)
    q1, med, q3 = _quartiles_split(srt)
    if q1 is None or q3 is None:
        _show('Box plot', ['Need more data (n>=2).'])
        return
    iqr = q3 - q1
    lf = q1 - 1.5 * iqr
    uf = q3 + 1.5 * iqr
    # outliers are beyond the fences; the whiskers stop at the most extreme
    # point that is NOT an outlier, not at the true min/max
    outs = []
    keep = []
    i = 0
    while i < n:
        v = srt[i]
        if v < lf or v > uf:
            outs.append(v)
        else:
            keep.append(v)
        i += 1
    if keep:
        wlo = keep[0]
        whi = keep[len(keep) - 1]
    else:
        wlo = srt[0]
        whi = srt[n - 1]
    lines = []
    lines.append('n = ' + str(n))
    lines.append('min = ' + _fn(srt[0]) + '  max = ' + _fn(srt[n - 1]))
    lines.append('Q1 = ' + _fn(q1))
    lines.append('median = ' + _fn(med))
    lines.append('Q3 = ' + _fn(q3))
    lines.append('IQR = ' + _fn(iqr))
    lines.append('fences ' + _fn(lf) + ' .. ' + _fn(uf))
    lines.append('whisker lo = ' + _fn(wlo) + '  whisker hi = ' + _fn(whi))
    outstr = []
    j = 0
    while j < len(outs):
        outstr.append(_fn(outs[j]))
        j += 1
    if outstr:
        lines.append('outliers: ' + ' '.join(outstr))
    else:
        lines.append('outliers: none')
    _pages('Box plot', lines)
    xlo, xhi = casutil.nice_range(srt)
    fr = casutil.frame(xlo, xhi, 0.0, 10.0)
    casutil.axes(fr, 'Box plot', 'value', None)
    midy = 5.0
    half = 2.5
    cap = 1.25
    casutil.seg(fr, wlo, midy, q1, midy, casui.BLACK)
    casutil.seg(fr, q3, midy, whi, midy, casui.BLACK)
    casutil.seg(fr, wlo, midy - cap, wlo, midy + cap, casui.BLACK)
    casutil.seg(fr, whi, midy - cap, whi, midy + cap, casui.BLACK)
    casutil.box(fr, q1, midy - half, q3, midy + half, casui.BLACK, False)
    casutil.seg(fr, med, midy - half, med, midy + half, casui.ACC)
    k = 0
    while k < len(outs):
        casutil.marker(fr, outs[k], midy, casui.RED, 2)
        k += 1
    casutil.chart_hold('EXIT to go back')

def t_freq():
    xs = _getlist('Values list:')
    if xs is None or len(xs) == 0:
        _show('Freq table', ['Need values.'])
        return
    fs = _getlist('Frequencies:')
    if fs is None or len(fs) != len(xs):
        _show('Freq table', ['Counts mismatch.'])
        return
    nf = 0.0
    sx = 0.0
    i = 0
    while i < len(xs):
        nf += fs[i]
        sx += fs[i] * xs[i]
        i += 1
    if nf == 0:
        _show('Freq table', ['Total freq 0.'])
        return
    mean = sx / nf
    ss = 0.0
    i = 0
    while i < len(xs):
        ss += fs[i] * (xs[i] - mean) * (xs[i] - mean)
        i += 1
    varp = ss / nf
    lines = []
    lines.append('N = ' + _fn(nf))
    lines.append('sum fx = ' + _fn(sx))
    lines.append('mean = ' + _fn(mean))
    lines.append('Sxx = ' + _fn(ss))
    if nf > 1:
        lines.append('s (n-1) sd = ' + _fn(math.sqrt(ss / (nf - 1.0))))
    lines.append('sd (n) = ' + _fn(math.sqrt(varp)))
    lines.append('var (n) = ' + _fn(varp))
    _pages('Freq mean/var', lines)

def _cf_interp(bnds, cf, target):
    # cumulative frequency is plotted at the UPPER class boundary; read off a
    # target (n/4, n/2, 3n/4) by linear interpolation across the class it
    # falls in
    n = len(cf)
    prev = 0.0
    i = 0
    while i < n:
        if target <= cf[i]:
            denom = cf[i] - prev
            if denom <= 0:
                return bnds[i + 1]
            frac = (target - prev) / denom
            return bnds[i] + frac * (bnds[i + 1] - bnds[i])
        prev = cf[i]
        i += 1
    return bnds[n]

def t_hist():
    bnds = _getlist('Class boundaries (n+1):')
    if bnds is None or len(bnds) < 2:
        _show('Histogram', ['Need >=2 boundaries.'])
        return
    fs = _getlist('Frequencies (n):')
    if fs is None or len(fs) != len(bnds) - 1:
        _show('Histogram', ['Freq count mismatch.'])
        return
    n = len(fs)
    i = 0
    while i < n:
        if bnds[i + 1] <= bnds[i]:
            _show('Histogram', ['Boundaries must increase.'])
            return
        if fs[i] < 0:
            _show('Histogram', ['Frequencies must be >=0.'])
            return
        i += 1
    # frequency density = frequency / class width, so the bar AREA (not its
    # height) is the frequency - plotting raw frequency against unequal
    # widths would be misleading, which is the whole point of this tool
    widths = []
    dens = []
    tot = 0.0
    i = 0
    while i < n:
        w = bnds[i + 1] - bnds[i]
        widths.append(w)
        dens.append(fs[i] / w)
        tot += fs[i]
        i += 1
    lines = []
    lines.append('n classes = ' + str(n))
    lines.append('total freq = ' + _fn(tot))
    i = 0
    while i < n:
        lines.append(_fn(bnds[i]) + '-' + _fn(bnds[i + 1]) + ' f=' + _fn(fs[i]) +
                     ' w=' + _fn(widths[i]) + ' fd=' + _fn(dens[i]))
        i += 1
    _pages('Histogram', lines)
    maxd = dens[0]
    i = 1
    while i < n:
        if dens[i] > maxd:
            maxd = dens[i]
        i += 1
    yhi = maxd * 1.15 if maxd > 0.0 else 1.0
    fr = casutil.frame(bnds[0], bnds[n], 0.0, yhi)
    casutil.axes(fr, 'Histogram', 'value', 'freq density')
    i = 0
    while i < n:
        casutil.box(fr, bnds[i], 0.0, bnds[i + 1], dens[i], casui.ACC, True)
        casutil.box(fr, bnds[i], 0.0, bnds[i + 1], dens[i], casui.BLACK, False)
        i += 1
    casutil.chart_hold('EXIT to go back')

def t_cumfreq():
    bnds = _getlist('Class boundaries (n+1):')
    if bnds is None or len(bnds) < 2:
        _show('Cumulative freq', ['Need >=2 boundaries.'])
        return
    fs = _getlist('Frequencies (n):')
    if fs is None or len(fs) != len(bnds) - 1:
        _show('Cumulative freq', ['Freq count mismatch.'])
        return
    n = len(fs)
    i = 0
    while i < n:
        if bnds[i + 1] <= bnds[i]:
            _show('Cumulative freq', ['Boundaries must increase.'])
            return
        if fs[i] < 0:
            _show('Cumulative freq', ['Frequencies must be >=0.'])
            return
        i += 1
    cf = []
    run = 0.0
    i = 0
    while i < n:
        run += fs[i]
        cf.append(run)
        i += 1
    tot = run
    if tot <= 0:
        _show('Cumulative freq', ['Total freq is 0.'])
        return
    # plotted at the upper class boundary; median/quartiles read off by
    # linear interpolation at n/2 and n/4, 3n/4
    med = _cf_interp(bnds, cf, tot * 0.5)
    q1 = _cf_interp(bnds, cf, tot * 0.25)
    q3 = _cf_interp(bnds, cf, tot * 0.75)
    lines = []
    lines.append('n classes = ' + str(n))
    lines.append('total freq = ' + _fn(tot))
    i = 0
    while i < n:
        lines.append('<=' + _fn(bnds[i + 1]) + ' cf=' + _fn(cf[i]))
        i += 1
    lines.append('Q1 (n/4) = ' + _fn(q1))
    lines.append('median (n/2) = ' + _fn(med))
    lines.append('Q3 (3n/4) = ' + _fn(q3))
    lines.append('IQR = ' + _fn(q3 - q1))
    _pages('Cumulative freq', lines)
    xlo = bnds[0]
    xhi = bnds[n]
    fr = casutil.frame(xlo, xhi, 0.0, tot * 1.05)
    casutil.axes(fr, 'Cumulative freq', 'value', 'cum freq')
    px = bnds[0]
    py = 0.0
    i = 0
    while i < n:
        nx = bnds[i + 1]
        ny = cf[i]
        casutil.seg(fr, px, py, nx, ny, casui.ACC)
        casutil.marker(fr, nx, ny, casui.ACC, 1)
        px = nx
        py = ny
        i += 1
    casutil.seg(fr, xlo, tot * 0.25, q1, tot * 0.25, casui.RED)
    casutil.seg(fr, q1, 0.0, q1, tot * 0.25, casui.RED)
    casutil.seg(fr, xlo, tot * 0.5, med, tot * 0.5, casui.RED)
    casutil.seg(fr, med, 0.0, med, tot * 0.5, casui.RED)
    casutil.seg(fr, xlo, tot * 0.75, q3, tot * 0.75, casui.RED)
    casutil.seg(fr, q3, 0.0, q3, tot * 0.75, casui.RED)
    casutil.chart_hold('EXIT to go back')

def t_drv():
    xs = _getlist('X values:')
    if xs is None or len(xs) == 0:
        _show('Discrete RV', ['Need values.'])
        return
    ps = _getlist('Probabilities:')
    if ps is None or len(ps) != len(xs):
        _show('Discrete RV', ['Count mismatch.'])
        return
    tp = 0.0
    ex = 0.0
    ex2 = 0.0
    i = 0
    while i < len(xs):
        tp += ps[i]
        ex += xs[i] * ps[i]
        ex2 += xs[i] * xs[i] * ps[i]
        i += 1
    varx = ex2 - ex * ex
    lines = []
    lines.append('sum p = ' + _fn(tp))
    if abs(tp - 1.0) > 0.001:
        lines.append('WARN: sum p not 1')
    lines.append('E[X] = ' + _fn(ex))
    lines.append('E[X^2] = ' + _fn(ex2))
    lines.append('Var[X] = ' + _fn(varx))
    lines.append('sd = ' + _fn(math.sqrt(abs(varx))))
    _show('E[X], Var[X]', lines)

def t_binom():
    n = _asknum('n =')
    p = _asknum('p =')
    k = _asknum('k =')
    if n is None or p is None or k is None:
        return
    ni = int(round(n))
    ki = int(round(k))
    if ni < 0 or p < 0 or p > 1:
        _show('Binomial', ['Bad n or p.'])
        return
    if ni > 5000:
        # the cdf sum is O(k^2) - anything this size would stall the handheld
        _show('Binomial', ['n too large (max 5000).'])
        return
    pk = _bpmf(ni, p, ki)
    cum = _bcdf(ni, p, ki)
    lines = []
    lines.append('B(' + str(ni) + ', ' + _fn(p) + ')')
    lines.append('mean np = ' + _fn(ni * p))
    lines.append('var npq = ' + _fn(ni * p * (1.0 - p)))
    lines.append('P(X=' + str(ki) + ') = ' + _fn(pk))
    lines.append('P(X<=' + str(ki) + ') = ' + _fn(cum))
    lines.append('P(X>=' + str(ki) + ') = ' + _fn(1.0 - cum + pk))
    _show('Binomial', lines)

def t_normal():
    mu = _asknum('mu =')
    sd = _asknum('sd =')
    if mu is None or sd is None or sd <= 0:
        _show('Normal', ['Need mu, sd>0.'])
        return
    a = _asknum('lower a (blank -inf):')
    b = _asknum('upper b (blank +inf):')
    if a is None:
        a = mu - 1.0e6 * sd
    if b is None:
        b = mu + 1.0e6 * sd
    za = (a - mu) / sd
    zb = (b - mu) / sd
    pr = _phi(zb) - _phi(za)
    lines = []
    lines.append('N(' + _fn(mu) + ', sd ' + _fn(sd) + ')')
    lines.append('z(a) = ' + _fn(za))
    lines.append('z(b) = ' + _fn(zb))
    lines.append('P(a<X<b) = ' + _fn(pr))
    lines.append('P(X<b) = ' + _fn(_phi(zb)))
    lines.append('P(X>a) = ' + _fn(1.0 - _phi(za)))
    _show('Normal prob', lines)

def t_invnorm():
    mu = _asknum('mu =')
    sd = _asknum('sd =')
    p = _asknum('P(X<x) = p =')
    if mu is None or sd is None or p is None:
        return
    if sd <= 0 or p <= 0 or p >= 1:
        _show('Inv Normal', ['Need 0<p<1, sd>0.'])
        return
    z = _inv_phi(p)
    x = mu + z * sd
    lines = []
    lines.append('p = ' + _fn(p))
    lines.append('z = ' + _fn(z))
    lines.append('x = ' + _fn(x))
    _show('Inverse Normal', lines)

def t_htbinom():
    n = _asknum('n =')
    p0 = _asknum('p0 (H0) =')
    x = _asknum('observed x =')
    if n is None or p0 is None or x is None:
        return
    if p0 <= 0 or p0 >= 1 or n <= 0:
        _show('HT binomial', ['Need 0<p0<1.'])
        return
    al = _asknum('alpha % (e.g. 5):')
    if al is None:
        return
    ni = int(round(n))
    xi = int(round(x))
    a = al / 100.0
    tail = _asknum('tail 1=lower 2=upper 3=two:')
    if tail is None:
        return
    ti = int(round(tail))
    lo = _bcdf(ni, p0, xi)
    up = 1.0 - _bcdf(ni, p0, xi - 1)
    lines = []
    lines.append('B(' + str(ni) + ', ' + _fn(p0) + ') x=' + str(xi))
    if ti == 1:
        c = 0
        while c <= ni and _bcdf(ni, p0, c) <= a:
            c += 1
        cr = c - 1
        lines.append('lower 1-tail a=' + _fn(a))
        lines.append('p-value = ' + _fn(lo))
        if cr < 0:
            lines.append('CR: none')
        else:
            lines.append('CR: X<=' + str(cr))
        lines.append('reject H0: ' + ('YES' if lo <= a else 'NO'))
    elif ti == 2:
        c = ni
        while c >= 0 and (1.0 - _bcdf(ni, p0, c - 1)) <= a:
            c -= 1
        cr = c + 1
        lines.append('upper 1-tail a=' + _fn(a))
        lines.append('p-value = ' + _fn(up))
        if cr > ni:
            lines.append('CR: none')
        else:
            lines.append('CR: X>=' + str(cr))
        lines.append('reject H0: ' + ('YES' if up <= a else 'NO'))
    else:
        pv = 2.0 * min(lo, up)
        if pv > 1.0:
            pv = 1.0
        ah = a / 2.0
        cl = 0
        while cl <= ni and _bcdf(ni, p0, cl) <= ah:
            cl += 1
        cl -= 1
        cu = ni
        while cu >= 0 and (1.0 - _bcdf(ni, p0, cu - 1)) <= ah:
            cu -= 1
        cu += 1
        lines.append('two-tail a=' + _fn(a))
        lines.append('p-value = ' + _fn(pv))
        s = 'CR: '
        if cl < 0:
            s += 'none'
        else:
            s += 'X<=' + str(cl)
        if cu > ni:
            s += ' / none'
        else:
            s += ' / X>=' + str(cu)
        lines.append(s)
        rej = (xi <= cl) or (xi >= cu)
        lines.append('reject H0: ' + ('YES' if rej else 'NO'))
    _pages('HT binomial', lines)

def t_htmean():
    mu0 = _asknum('mu0 (H0) =')
    sig = _asknum('pop sd =')
    xb = _asknum('sample mean =')
    n = _asknum('sample n =')
    if mu0 is None or sig is None or xb is None or n is None:
        return
    if sig <= 0 or n <= 0:
        _show('z-test', ['Need sd,n>0.'])
        return
    al = _asknum('alpha % (e.g. 5):')
    if al is None:
        return
    tail = _asknum('tail 1=low 2=up 3=two:')
    if tail is None:
        return
    a = al / 100.0
    ti = int(round(tail))
    se = sig / math.sqrt(n)
    z = (xb - mu0) / se
    pl = _phi(z)
    pu = 1.0 - _phi(z)
    lines = []
    lines.append('test z = ' + _fn(z))
    lines.append('SE = ' + _fn(se))
    if ti == 1:
        zc = _inv_phi(a)
        lines.append('p-value = ' + _fn(pl))
        lines.append('crit z = ' + _fn(zc))
        lines.append('reject: ' + ('YES' if z <= zc else 'NO'))
    elif ti == 2:
        zc = _inv_phi(1.0 - a)
        lines.append('p-value = ' + _fn(pu))
        lines.append('crit z = ' + _fn(zc))
        lines.append('reject: ' + ('YES' if z >= zc else 'NO'))
    else:
        pv = 2.0 * min(pl, pu)
        if pv > 1.0:
            pv = 1.0
        zc = _inv_phi(1.0 - a / 2.0)
        lines.append('p-value = ' + _fn(pv))
        lines.append('crit z = +/-' + _fn(zc))
        lines.append('reject: ' + ('YES' if abs(z) >= zc else 'NO'))
    _pages('z-test mean', lines)

def _linreg(xs, ys):
    # least-squares y on x: b = Sxy/Sxx, a = ybar - b*xbar, plus PMCC r.
    # Shared by t_regress and t_scatter so the two tools cannot drift apart.
    # Returns None for degenerate data (zero spread in x or y).
    n = len(xs)
    sx = 0.0
    sy = 0.0
    sxy = 0.0
    sxx = 0.0
    syy = 0.0
    i = 0
    while i < n:
        sx += xs[i]
        sy += ys[i]
        sxy += xs[i] * ys[i]
        sxx += xs[i] * xs[i]
        syy += ys[i] * ys[i]
        i += 1
    sxxd = sxx - sx * sx / n
    syyd = syy - sy * sy / n
    sxyd = sxy - sx * sy / n
    if sxxd <= 0 or syyd <= 0:
        return None
    den = math.sqrt(sxxd * syyd)
    r = sxyd / den
    b = sxyd / sxxd
    a = sy / n - b * sx / n
    return (a, b, r)

def t_regress():
    xs = _getlist('X values:')
    if xs is None or len(xs) < 2:
        _show('Regression', ['Need >=2 X.'])
        return
    ys = _getlist('Y values:')
    if ys is None or len(ys) != len(xs):
        _show('Regression', ['Count mismatch.'])
        return
    res = _linreg(xs, ys)
    if res is None:
        _show('Regression', ['Degenerate data.'])
        return
    a, b, r = res
    n = len(xs)
    lines = []
    lines.append('n = ' + str(n))
    lines.append('r = ' + _fn(r))
    lines.append('b (grad) = ' + _fn(b))
    lines.append('a (intercept) = ' + _fn(a))
    if b < 0:
        lines.append('y = ' + _fn(a) + ' - ' + _fn(-b) + 'x')
    else:
        lines.append('y = ' + _fn(a) + ' + ' + _fn(b) + 'x')
    _show('PMCC + regression', lines)
    px = _asknum('predict at x (blank skip):')
    if px is not None:
        _show('Prediction', ['x = ' + _fn(px), 'y = ' + _fn(a + b * px)])

def t_scatter():
    xs = _getlist('X values:')
    if xs is None or len(xs) < 2:
        _show('Scatter + regression', ['Need >=2 X.'])
        return
    ys = _getlist('Y values:')
    if ys is None or len(ys) != len(xs):
        _show('Scatter + regression', ['Count mismatch.'])
        return
    res = _linreg(xs, ys)
    if res is None:
        _show('Scatter + regression', ['Degenerate data.'])
        return
    a, b, r = res
    n = len(xs)
    lines = []
    lines.append('n = ' + str(n))
    lines.append('r = ' + _fn(r))
    lines.append('b (grad) = ' + _fn(b))
    lines.append('a (intercept) = ' + _fn(a))
    if b < 0:
        lines.append('y = ' + _fn(a) + ' - ' + _fn(-b) + 'x')
    else:
        lines.append('y = ' + _fn(a) + ' + ' + _fn(b) + 'x')
    _show('Scatter + regression', lines)
    xlo, xhi = casutil.nice_range(xs)
    ylo, yhi = casutil.nice_range(ys)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'Scatter + regression', 'x', 'y')
    i = 0
    while i < n:
        casutil.marker(fr, xs[i], ys[i], casui.BLACK, 2)
        i += 1
    casutil.seg(fr, xlo, a + b * xlo, xhi, a + b * xhi, casui.ACC)
    casutil.chart_hold('EXIT to go back')

def t_prob():
    pa = _asknum('P(A) =')
    pb = _asknum('P(B) =')
    pab = _asknum('P(A and B) =')
    if pa is None or pb is None or pab is None:
        return
    lines = []
    lines.append('P(AorB) = ' + _fn(pa + pb - pab))
    if pb != 0:
        lines.append('P(A|B) = ' + _fn(pab / pb))
    else:
        lines.append('P(A|B) undef')
    if pa != 0:
        lines.append('P(B|A) = ' + _fn(pab / pa))
    else:
        lines.append('P(B|A) undef')
    indep = pa * pb
    lines.append('P(A)P(B) = ' + _fn(indep))
    if abs(indep - pab) < 0.0001:
        lines.append('independent: YES')
    else:
        lines.append('independent: NO')
    _show('Probability rules', lines)

_SAMPLING = [
    ('Simple random',
     ['Every possible sample of size',
      'n is equally likely; every',
      'member equally likely.',
      'How: number the population',
      '1..N, draw n distinct random',
      'numbers.',
      'Needs: a full sampling frame.',
      'Bias: none in principle. In',
      ' practice non-response and an',
      ' incomplete frame bias it.']),
    ('Systematic',
     ['Take every k-th member after',
      'a random start, k = N/n.',
      'How: random start r in 1..k,',
      'then r, r+k, r+2k, ...',
      'Needs: an ordered frame.',
      'Bias: BAD if the list has a',
      ' periodic pattern with period',
      ' k - e.g. every 4th house is',
      ' a corner house. Then the',
      ' sample is systematically',
      ' unrepresentative.']),
    ('Stratified',
     ['Split into strata (groups that',
      'differ), sample each in',
      'proportion to its size.',
      'How: n_i = n * N_i / N, then',
      'sample randomly within each.',
      'Needs: strata known for every',
      ' member.',
      'Bias: low, and more precise',
      ' than simple random when the',
      ' strata really do differ.',
      ' Biased if strata are wrong.']),
    ('Cluster',
     ['Split into clusters (groups',
      'each like the whole), pick',
      'whole clusters at random.',
      'How: choose clusters, then',
      'survey all of them (or sample',
      'within them).',
      'Needs: a list of clusters only',
      ' - cheap, no full frame.',
      'Bias: BAD if clusters are',
      ' internally alike and differ',
      ' from each other; less',
      ' precise than simple random.']),
    ('Quota',
     ['Interviewer fills fixed quotas',
      'by category (e.g. 20 men,',
      '20 women) choosing whom to',
      'ask.',
      'Needs: no sampling frame -',
      ' its main advantage.',
      'Bias: BAD. Non-random: the',
      ' interviewer picks, so who is',
      ' approachable, awake and in',
      ' that street decides. Not a',
      ' probability sample, so no',
      ' proper margin of error.']),
    ('Opportunity',
     ['Also called convenience: take',
      'whoever is available.',
      'How: ask the first 30 people',
      'you meet.',
      'Needs: nothing. Cheapest and',
      ' quickest.',
      'Bias: WORST. The sample is',
      ' whoever was in that place at',
      ' that time, so it need not',
      ' represent anything. Cannot',
      ' be generalised safely.']),
]

def t_sampling():
    labels = []
    i = 0
    while i < len(_SAMPLING):
        labels.append(str(i + 1) + ' ' + _SAMPLING[i][0])
        i += 1
    c = _asknum('method 1-6 (0 = list):')
    if c is None:
        return
    k = int(round(c))
    if k < 1 or k > len(_SAMPLING):
        lines = ['Pick a number for detail:']
        i = 0
        while i < len(_SAMPLING):
            lines.append(labels[i])
            i += 1
        lines.append('')
        lines.append('Random methods (1,2,3,4)')
        lines.append('support inference; quota')
        lines.append('and opportunity (5,6) do')
        lines.append('not - they are not random.')
        _pages('Sampling methods', lines)
        return
    name, body = _SAMPLING[k - 1]
    _pages(name + ' sampling', body)

def t_stratsamp():
    ns = _getlist('Stratum sizes:')
    if ns is None or len(ns) < 2:
        _show('Stratified sample', ['Need >=2 stratum sizes.'])
        return
    n = _asknum('total sample size n:')
    if n is None:
        return
    want = int(round(n))
    if want <= 0:
        _show('Stratified sample', ['n must be > 0.'])
        return
    tot = 0.0
    i = 0
    while i < len(ns):
        if ns[i] < 0:
            _show('Stratified sample', ['Sizes must be >= 0.'])
            return
        tot += ns[i]
        i += 1
    if tot <= 0:
        _show('Stratified sample', ['Population is 0.'])
        return
    if want > tot:
        _show('Stratified sample', ['n is bigger than the', 'population.'])
        return
    # proportional allocation n_i = n * N_i / N. Rounding each one separately
    # usually misses the target total, so the whole numbers are taken first and
    # the leftover places handed out by largest remainder - the total is then
    # exactly n, which is what the mark scheme wants.
    exact = []
    base = []
    i = 0
    got = 0
    while i < len(ns):
        e = want * ns[i] / tot
        exact.append(e)
        f = int(e)
        base.append(f)
        got += f
        i += 1
    left = want - got
    while left > 0:
        bi = -1
        bf = -1.0
        i = 0
        while i < len(ns):
            fr = exact[i] - base[i]
            if fr > bf:
                bf = fr
                bi = i
            i += 1
        if bi < 0:
            break
        base[bi] += 1
        exact[bi] = base[bi] * 1.0   # do not win the same place twice
        left -= 1
    lines = ['population N = ' + _fn(tot),
             'sample n = ' + str(want),
             'n_i = n * N_i / N']
    i = 0
    while i < len(ns):
        lines.append('stratum ' + str(i + 1) + ': N=' + _fn(ns[i]) +
                     ' -> ' + str(base[i]))
        i += 1
    chk = 0
    i = 0
    while i < len(base):
        chk += base[i]
        i += 1
    lines.append('total allocated = ' + str(chk))
    lines.append('sampling fraction = ' + _fn(want / tot))
    k = tot / want
    lines.append('systematic would use')
    lines.append(' k = N/n = ' + _fn(k))
    lines.append(' random start 1..' + str(int(k)) if k >= 1 else ' k < 1')
    _pages('Stratified sample', lines)

def t_tree():
    pa = _asknum('P(A) =')
    if pa is None or pa < 0 or pa > 1:
        _show('Tree diagram', ['Need 0 <= P(A) <= 1.'])
        return
    pba = _asknum('P(B|A) =')
    if pba is None or pba < 0 or pba > 1:
        _show('Tree diagram', ['Need 0 <= P(B|A) <= 1.'])
        return
    pbna = _asknum("P(B|not A) =")
    if pbna is None or pbna < 0 or pbna > 1:
        _show('Tree diagram', ['Need 0 <= P(B|A\') <= 1.'])
        return
    pna = 1.0 - pa
    # the four end-of-branch probabilities: multiply ALONG a branch
    ab = pa * pba
    anb = pa * (1.0 - pba)
    nab = pna * pbna
    nanb = pna * (1.0 - pbna)
    pb = ab + nab                 # add ACROSS the branches that end in B
    pnb = anb + nanb
    lines = ['P(A) = ' + _fn(pa) + '  P(A\') = ' + _fn(pna),
             'multiply along a branch:',
             'P(A and B)   = ' + _fn(ab),
             "P(A and B')  = " + _fn(anb),
             "P(A' and B)  = " + _fn(nab),
             "P(A' and B') = " + _fn(nanb),
             'these four sum to ' + _fn(ab + anb + nab + nanb),
             'add across branches:',
             'P(B) = ' + _fn(pb),
             "P(B') = " + _fn(pnb)]
    # the reverse conditional, which is what Bayes is for
    lines.append('reverse by Bayes:')
    lines.append('P(A|B) = P(A and B)/P(B)')
    if pb > 0:
        lines.append('P(A|B) = ' + _fn(ab) + '/' + _fn(pb))
        lines.append('P(A|B) = ' + _fn(ab / pb))
        lines.append("P(A'|B) = " + _fn(nab / pb))
    else:
        lines.append('P(A|B) undefined: P(B)=0')
    if pnb > 0:
        lines.append("P(A|B') = " + _fn(anb / pnb))
    if pa > 0 and pb > 0:
        if abs(ab - pa * pb) < 1e-9:
            lines.append('A and B are INDEPENDENT')
            lines.append(' (P(B|A) = P(B))')
        else:
            lines.append('A and B are NOT independent')
    _pages('Tree diagram', lines)
    # draw the two-stage tree with the branch probabilities on it
    fr = casutil.frame(0.0, 10.0, 0.0, 10.0)
    casutil.axes(fr, 'Two-stage tree', None, None, False)
    casutil.seg(fr, 1.0, 5.0, 4.0, 8.0, casui.ACC)
    casutil.seg(fr, 1.0, 5.0, 4.0, 2.0, casui.ACC)
    casutil.seg(fr, 4.5, 8.0, 7.5, 9.5, casui.BLACK)
    casutil.seg(fr, 4.5, 8.0, 7.5, 6.5, casui.BLACK)
    casutil.seg(fr, 4.5, 2.0, 7.5, 3.5, casui.BLACK)
    casutil.seg(fr, 4.5, 2.0, 7.5, 0.5, casui.BLACK)
    _lab(fr, 2.2, 7.2, 'A ' + _fn(pa))
    _lab(fr, 2.2, 3.0, "A' " + _fn(pna))
    _lab(fr, 5.9, 9.3, 'B ' + _fn(pba))
    _lab(fr, 5.9, 7.0, "B' " + _fn(1.0 - pba))
    _lab(fr, 5.9, 3.6, 'B ' + _fn(pbna))
    _lab(fr, 5.9, 1.2, "B' " + _fn(1.0 - pbna))
    _lab(fr, 8.0, 9.5, '= ' + _fn(ab))
    _lab(fr, 8.0, 6.5, '= ' + _fn(anb))
    _lab(fr, 8.0, 3.5, '= ' + _fn(nab))
    _lab(fr, 8.0, 0.5, '= ' + _fn(nanb))
    casutil.chart_hold('EXIT to go back')

def _lab(fr, x, y, s):
    casui.draw_string(casutil.fx(fr, x), casutil.fy(fr, y), s,
                      casui.BLACK, 'small')

def t_ncrfact():
    n = _asknum('n =')
    if n is None:
        return
    ni = int(round(n))
    r = _asknum('r (blank for n! only):')
    lines = []
    f = _fact(ni)
    if f is None:
        # an uncapped n! locked the calculator up on a mistyped entry
        if ni < 0:
            lines.append('n! undefined for n < 0')
        else:
            lines.append('n too large for n!')
            lines.append('(max ' + str(casutil.FACT_MAX) + ')')
    else:
        lines.append(str(ni) + '! = ' + str(f))
    if r is not None:
        ri = int(round(r))
        c = _ncr(ni, ri)
        lines.append(str(ni) + 'C' + str(ri) + ' = ' + str(c))
        fr = _fact(ni - ri)
        if f is not None and fr is not None and fr != 0 and ni - ri >= 0:
            lines.append(str(ni) + 'P' + str(ri) + ' = ' + str(f // fr))
    _show('Factorial / nCr', lines)

TOOLS = [
    ('Summary stats', t_summary),
    ('Freq table mean/var', t_freq),
    ('Discrete RV E,Var', t_drv),
    ('Binomial B(n,p)', t_binom),
    ('Normal P(a<X<b)', t_normal),
    ('Inverse Normal', t_invnorm),
    ('HT binomial prop', t_htbinom),
    ('HT Normal mean z', t_htmean),
    ('PMCC + regression', t_regress),
    ('Probability rules', t_prob),
    ('Tree diagram + Bayes', t_tree),
    ('Sampling methods', t_sampling),
    ('Stratified sample', t_stratsamp),
    ('Factorial / nCr', t_ncrfact),
    ('Box plot', t_boxplot),
    ('Histogram', t_hist),
    ('Cumulative freq', t_cumfreq),
    ('Scatter + regression', t_scatter),
]

def run():
    casutil.run_tools('STATISTICS', TOOLS)
