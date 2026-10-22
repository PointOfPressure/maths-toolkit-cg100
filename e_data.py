# Statistics actions on data and from boxes: summary statistics, quartiles
# (the AQA position rule), outliers (1.5 IQR and 2 sd), a frequency table,
# x and y lists (PMCC, regression line), statistics from sums or Sxx, the
# PMCC test (critical values worked out, so any n), two-event probability
# (Venn, conditional, independence), mu and sigma from two probabilities,
# a stratified sample, and fences from given quartiles.
import math
import fmt
from e_stat import box, _s, _v, sig, pct, invphi

def _stats(xs, fs=None):
    if fs is None:
        fs = [1] * len(xs)
    n = 0.0
    sx = 0.0
    sxx = 0.0
    for x, f in zip(xs, fs):
        n += f
        sx += f * x
        sxx += f * x * x
    if n <= 0:
        raise ValueError('no data')
    m = sx / n
    ss = sxx - sx * sx / n
    if ss < 0:
        ss = 0.0
    return n, sx, sxx, m, ss

def _qpos(srt, pos):
    # AQA rule: a whole position takes the mean of it and the next value,
    # otherwise the position is rounded up
    n = len(srt)
    fl = int(math.floor(pos))
    if abs(pos - fl) < 1e-9:
        if fl < 1:
            return srt[0]
        if fl >= n:
            return srt[-1]
        return (srt[fl - 1] + srt[fl]) / 2.0
    i = int(math.ceil(pos))
    return srt[min(max(i, 1), n) - 1]

def _expand(xs, fs):
    out = []
    for x, f in zip(xs, fs):
        if f != int(f) or f < 0:
            raise ValueError('frequencies must be whole numbers')
        out += [x] * int(f)
    out.sort()
    return out

def _summary(xs, fs, lines):
    n, sx, sxx, m, ss = _stats(xs, fs)
    w = 'f' if fs is not None else ''
    lines.append('n = ' + _s(n) + ',  sum ' + w + 'x = ' + _s(sx) + ',  sum ' + w + 'x^2 = ' + _s(sxx))
    lines.append('mean = ' + _s(sx) + '/' + _s(n))
    lines.append(box('mean = ', m))
    lines.append('Sxx = sum ' + w + 'x^2 - (sum ' + w + 'x)^2/n = ' + _s(ss))
    lines.append(box('sd = ', math.sqrt(ss / n)))
    if n > 1:
        lines.append(('w', 'sd = sqrt(Sxx/n);  with n - 1: s = ' + _s(math.sqrt(ss / (n - 1)))))
    return m, math.sqrt(ss / n)

def _quart(srt, lines):
    n = len(srt)
    q1 = _qpos(srt, n * 0.25)
    md = _qpos(srt, n * 0.5)
    q3 = _qpos(srt, n * 0.75)
    lines.append(('w', 'positions n/4 = ' + _s(n * 0.25) + ', n/2 = ' + _s(n * 0.5) + ', 3n/4 = ' +
                  _s(n * 0.75) + ' (whole: halfway to the next)'))
    lines.append(box('median = ', md))
    lines.append(box('Q1 = ', q1))
    lines.append(box('Q3 = ', q3))
    lines.append(box('IQR = ', q3 - q1))
    return q1, md, q3

def summary(F, arg, vals):
    lines = []
    _summary(F.data, None, lines)
    srt = sorted(F.data)
    lines.append('min ' + _s(srt[0]) + ', max ' + _s(srt[-1]) + ', range ' + _s(srt[-1] - srt[0]))
    return lines

def quartiles(F, arg, vals):
    srt = sorted(F.data)
    lines = ['in order: ' + ', '.join([_s(x) for x in srt[:12]]) + (', ...' if len(srt) > 12 else '')]
    _quart(srt, lines)
    return lines

def outliers(F, arg, vals):
    srt = sorted(F.data)
    lines = []
    q1, md, q3 = _quart(srt, [])
    i = q3 - q1
    lo, hi = q1 - 1.5 * i, q3 + 1.5 * i
    lines.append('Q1 = ' + _s(q1) + ', Q3 = ' + _s(q3) + ', IQR = ' + _s(i))
    lines.append('1.5 IQR fences: ' + _s(lo) + ' and ' + _s(hi))
    out = [x for x in srt if x < lo or x > hi]
    lines.append(fmt.boxs('1.5 IQR outliers: ', ', '.join([_s(x) for x in out]) or 'none'))
    n, sx, sxx, m, ss = _stats(F.data)
    sd = math.sqrt(ss / n)
    lines.append('mean +- 2 sd: ' + _s(m - 2 * sd) + ' and ' + _s(m + 2 * sd))
    out = [x for x in srt if x < m - 2 * sd or x > m + 2 * sd]
    lines.append(fmt.boxs('2 sd outliers: ', ', '.join([_s(x) for x in out]) or 'none'))
    lines.append(('w', 'the question says which rule; an outlier may still be genuine'))
    return lines

def freq(F, arg, vals):
    xs, fs = F.data, F.data2
    lines = ['values ' + ', '.join([_s(x) for x in xs]) + ';  frequencies ' + ', '.join([_s(f) for f in fs])]
    _summary(xs, fs, lines)
    srt = _expand(xs, fs)
    _quart(srt, lines)
    best = max(fs)
    lines.append('mode ' + ', '.join([_s(x) for x, f in zip(xs, fs) if f == best]))
    return lines

def bivariate(F, arg, vals):
    xs, ys = F.data, F.data2
    n = len(xs)
    if n < 3:
        raise ValueError('at least 3 pairs')
    nx, sx, sxx, mx, ssx = _stats(xs)
    ny, sy, syy, my, ssy = _stats(ys)
    sxy = 0.0
    for x, y in zip(xs, ys):
        sxy += x * y
    sp = sxy - sx * sy / n
    if ssx == 0 or ssy == 0:
        raise ValueError('one list is constant: no correlation')
    r = sp / math.sqrt(ssx * ssy)
    b = sp / ssx
    a = my - b * mx
    lines = ['n = ' + str(n) + ',  Sxx = ' + _s(ssx) + ',  Syy = ' + _s(ssy) + ',  Sxy = ' + _s(sp),
             'r = Sxy/sqrt(Sxx Syy)', box('r = ', r),
             'y on x: b = Sxy/Sxx = ' + _s(b) + ',  a = ybar - b xbar = ' + _s(a),
             fmt.boxs('y = ', _s(a) + (' + ' if b >= 0 else ' - ') + _s(abs(b)) + 'x')]
    lines.append(('w', 'first list x, second y'))
    return lines

# ---- from boxes --------------------------------------------------------------------------------

def fromsums(F, arg, vals):
    n = _v(vals[0], 'n')
    sx = _v(vals[1], 'sum x')
    lines = []
    if vals[2] is not None:
        sxx = _v(vals[2], 'sum x^2')
        ss = sxx - sx * sx / n
        lines.append('Sxx = sum x^2 - (sum x)^2/n = ' + _s(sxx) + ' - ' + _s(sx) + '^2/' + _s(n) + ' = ' + _s(ss))
    elif vals[3] is not None:
        ss = _v(vals[3], 'Sxx')
    else:
        raise ValueError('fill in sum x^2 or Sxx')
    if ss < 0:
        raise ValueError('sum x^2 is too small for that sum x')
    lines.append('mean = ' + _s(sx) + '/' + _s(n))
    lines.append(box('mean = ', sx / n))
    lines.append(box('variance = ', ss / n))
    lines.append(box('sd = ', math.sqrt(ss / n)))
    if n > 1:
        lines.append(('w', 'with n - 1: s^2 = ' + _s(ss / (n - 1)) + ', s = ' + _s(math.sqrt(ss / (n - 1)))))
    return lines

def rcrit(n, a):
    # P(R > c) = a under H0 (rho = 0): R has density ~ (1 - r^2)^((n-4)/2);
    # with r = sin u that is cos(u)^(n-3), integrated by Simpson's rule
    e = n - 3
    m = 200
    h = (math.pi / 2) / m
    cum = [0.0]
    for i in range(m):
        u = i * h
        cum.append(cum[-1] + h * (math.cos(u) ** e + 4 * math.cos(u + h / 2) ** e + math.cos(u + h) ** e) / 6)
    target = (1 - 2 * a) * cum[m]
    for i in range(m):
        if cum[i + 1] >= target:
            lo, hi = i * h, (i + 1) * h
            for j in range(40):
                mid = (lo + hi) / 2
                u = i * h
                part = cum[i] + (mid - u) * (math.cos(u) ** e + 4 * math.cos((u + mid) / 2) ** e +
                                             math.cos(mid) ** e) / 6
                if part < target:
                    lo = mid
                else:
                    hi = mid
            return math.sin((lo + hi) / 2)
    return 1.0

def pmcc(F, arg, vals):
    r = _v(vals[0], 'r')
    n = int(_v(vals[1], 'n'))
    a = sig(vals[2])
    tails = 1 if vals[3] is None else int(_v(vals[3], 'tails'))
    if n < 4:
        raise ValueError('n must be 4 or more')
    if abs(r) > 1:
        raise ValueError('r is between -1 and 1')
    if tails not in (1, 2):
        raise ValueError('tails: 1 or 2')
    aa = a if tails == 1 else a / 2
    c = rcrit(n, aa)
    lines = []
    if tails == 1:
        sg = '>' if r >= 0 else '<'
        lines.append('H0: rho = 0,  H1: rho ' + sg + ' 0  (one-tail, the side r is on)')
    else:
        lines.append('H0: rho = 0,  H1: rho != 0  (two-tail, ' + pct(aa) + ' each side)')
    lines.append('n = ' + str(n) + ', ' + pct(a) + ':  critical value ' + ('-' if r < 0 and tails == 1 else '') +
                 fmt.sf(c, 4) + (' (and -' + fmt.sf(c, 4) + ')' if tails == 2 else ''))
    rej = abs(r) >= round(c, 4)
    lines.append('|r| = ' + _s(abs(r)) + (' >= ' if rej else ' < ') + fmt.sf(c, 4))
    lines.append(fmt.boxs('', 'reject H0' if rej else 'do not reject H0'))
    lines.append(('w', ('sufficient' if rej else 'insufficient') + ' evidence of ' +
                  ('positive' if r >= 0 else 'negative') + ' correlation' + (' (in context)')))
    return lines

def venn(F, arg, vals):
    # any two of P(A), P(B), P(A and B), P(A or B) (and P(A|B)): the rest
    names = ['P(A)', 'P(B)', 'P(A and B)', 'P(A or B)', 'P(A|B)']
    k = {}
    for i in range(5):
        if vals[i] is not None and vals[i] != '?':
            k[i] = _v(vals[i], names[i])
            if k[i] < 0 or k[i] > 1:
                raise ValueError(names[i] + ' is a probability: 0 to 1')
    lines = []
    for step in range(4):
        if 2 not in k and 4 in k and 1 in k:
            k[2] = k[4] * k[1]
            lines.append('P(A and B) = P(A|B) P(B) = ' + _s(k[2]))
        if 2 not in k and 0 in k and 1 in k and 3 in k:
            k[2] = k[0] + k[1] - k[3]
            lines.append('P(A and B) = P(A) + P(B) - P(A or B) = ' + _s(k[2]))
        if 3 not in k and 0 in k and 1 in k and 2 in k:
            k[3] = k[0] + k[1] - k[2]
            lines.append('P(A or B) = P(A) + P(B) - P(A and B) = ' + _s(k[3]))
        if 0 not in k and 1 in k and 2 in k and 3 in k:
            k[0] = k[3] - k[1] + k[2]
            lines.append('P(A) = P(A or B) - P(B) + P(A and B) = ' + _s(k[0]))
        if 1 not in k and 0 in k and 2 in k and 3 in k:
            k[1] = k[3] - k[0] + k[2]
            lines.append('P(B) = P(A or B) - P(A) + P(A and B) = ' + _s(k[1]))
        if 1 not in k and 4 in k and 2 in k and k[4] > 0:
            k[1] = k[2] / k[4]
            lines.append('P(B) = P(A and B)/P(A|B) = ' + _s(k[1]))
        if 4 not in k and 1 in k and 2 in k and k[1] > 0:
            k[4] = k[2] / k[1]
            lines.append('P(A|B) = P(A and B)/P(B) = ' + _s(k[4]))
    if 2 not in k or 0 not in k or 1 not in k:
        raise ValueError('fill in more: two of P(A), P(B), P(A and B), P(A or B), P(A|B) with P(A) and P(B)')
    for i in range(5):
        if i in k and (vals[i] is None or vals[i] == '?'):
            lines.append(box(names[i] + ' = ', k[i]))
    lines.append('only A ' + _s(k[0] - k[2]) + ', only B ' + _s(k[1] - k[2]) + ', both ' + _s(k[2]) +
                 ', neither ' + _s(1 - k[0] - k[1] + k[2]))
    if k[0] - k[2] < -1e-12 or k[1] - k[2] < -1e-12 or 1 - k[0] - k[1] + k[2] < -1e-12:
        lines.append(('!', 'a region is negative: these probabilities are impossible together'))
    pp = k[0] * k[1]
    ind = abs(pp - k[2]) < 1e-9
    lines.append('P(A) x P(B) = ' + _s(pp) + (' = ' if ind else ' != ') + 'P(A and B) = ' + _s(k[2]))
    lines.append(fmt.boxs('', 'independent' if ind else 'not independent'))
    return lines

def twopct(F, arg, vals):
    # mu and sigma from P(X < x1) = p1 and P(X < x2) = p2
    x1 = _v(vals[0], 'x1')
    p1 = _v(vals[1], 'P(X < x1)')
    x2 = _v(vals[2], 'x2')
    p2 = _v(vals[3], 'P(X < x2)')
    z1 = invphi(p1)
    z2 = invphi(p2)
    if abs(z1 - z2) < 1e-12:
        raise ValueError('the two probabilities give the same z')
    lines = ['z1 = ' + _s(z1) + ',  z2 = ' + _s(z2),
             _s(x1) + ' = mu + ' + fmt.br(_s(z1)) + ' sigma', _s(x2) + ' = mu + ' + fmt.br(_s(z2)) + ' sigma']
    sd = (x2 - x1) / (z2 - z1)
    if sd <= 0:
        raise ValueError('sigma comes out negative: check the probabilities')
    mu = x1 - z1 * sd
    lines.append(box('mu = ', mu))
    lines.append(box('sigma = ', sd))
    lines.append(('w', 'P(X > x) = p is P(X < x) = 1 - p'))
    return lines

def strat(F, arg, vals):
    import rstat
    if not vals[0]:
        raise ValueError('fill in the sample size')
    n = rstat._num(vals[0])
    if not vals[1]:
        raise ValueError('fill in the stratum sizes, with commas')
    ns = rstat._list(vals[1])
    tot = 0.0
    for x in ns:
        tot += x
    lines = ['total ' + _s(tot)]
    out = []
    for x in ns:
        v = n * x / tot
        lines.append(_s(x) + '/' + _s(tot) + ' x ' + _s(n) + ' = ' + _s(v))
        out.append(str(int(math.floor(v + 0.5))))
    lines.append(fmt.boxs('sample: ', ', '.join(out)))
    lines.append(('w', 'rounded; check they add up to the sample size'))
    return lines

def fences(F, arg, vals):
    q1 = _v(vals[0], 'Q1')
    q3 = _v(vals[2], 'Q3')
    k = 1.5 if vals[3] is None else _v(vals[3], 'k')
    i = q3 - q1
    lines = ['IQR = ' + _s(q3) + ' - ' + _s(q1) + ' = ' + _s(i)]
    lines.append(box('Q1 - ' + _s(k) + ' IQR = ', q1 - k * i))
    lines.append(box('Q3 + ' + _s(k) + ' IQR = ', q3 + k * i))
    if vals[1] is not None:
        md = _v(vals[1], 'the median')
        lines.append(box('median - ' + _s(k) + ' IQR = ', md - k * i))
        lines.append(box('median + ' + _s(k) + ' IQR = ', md + k * i))
    lines.append(('w', 'the question says which fences'))
    return lines
