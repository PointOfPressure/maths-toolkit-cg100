import math
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

def t_regress():
    xs = _getlist('X values:')
    if xs is None or len(xs) < 2:
        _show('Regression', ['Need >=2 X.'])
        return
    ys = _getlist('Y values:')
    if ys is None or len(ys) != len(xs):
        _show('Regression', ['Count mismatch.'])
        return
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
        _show('Regression', ['Degenerate data.'])
        return
    den = math.sqrt(sxxd * syyd)
    r = sxyd / den
    b = sxyd / sxxd
    a = sy / n - b * sx / n
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
    ('Factorial / nCr', t_ncrfact),
]

def run():
    casutil.run_tools('STATISTICS', TOOLS)
