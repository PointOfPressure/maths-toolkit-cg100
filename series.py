import casui
import caslex
import caseng
import caspoly
import cascalc
import casutil

_fact = casutil.fact
_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_show = casutil.show
_w = casutil.w
_warn = casutil.warn


def t_sum_r():
    n = _askint('n (Sum r, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r', [_warn('n must be >= 0')])
        return
    s = n * (n + 1) / 2.0
    _show('SUM r, r=1..n', [_w('Sum r = n(n+1)/2'), 'n = ' + _fn(n), '= ' + _fn(s)])


def t_sum_r2():
    n = _askint('n (Sum r^2, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r^2', [_warn('n must be >= 0')])
        return
    s = n * (n + 1) * (2 * n + 1) / 6.0
    _show('SUM r^2, r=1..n', [_w('Sum r^2 ='), _w(' n(n+1)(2n+1)/6'), 'n = ' + _fn(n), '= ' + _fn(s)])


def t_sum_r3():
    n = _askint('n (Sum r^3, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r^3', [_warn('n must be >= 0')])
        return
    h = n * (n + 1) / 2.0
    s = h * h
    _show('SUM r^3, r=1..n', [_w('Sum r^3 ='), _w(' (n(n+1)/2)^2'), 'n = ' + _fn(n), '= ' + _fn(s)])


def _build_terms(f):
    terms = []
    d = f
    k = 0
    while k < 6:
        try:
            v = caseng.evalf(d, 0.0)
        except:
            break
        terms.append(v / _fact(k))
        try:
            d = caseng.simplify(caseng.diff(d, 'x'))
        except:
            break
        k = k + 1
    return terms


def _poly_lines(terms):
    lines = []
    first = True
    k = 0
    while k < len(terms):
        c = terms[k]
        if abs(c) < 1e-7:
            k = k + 1
            continue
        sign = '+'
        m = c
        if c < 0:
            sign = '-'
            m = -c
        ct = _fn(m)
        if k == 0:
            term = ct
        elif k == 1:
            term = 'x' if ct == '1' else ct + 'x'
        else:
            term = ('x^' + str(k)) if ct == '1' else (ct + 'x^' + str(k))
        if first:
            lines.append('P(x) = ' + ('-' if sign == '-' else '') + term)
            first = False
        else:
            lines.append('       ' + sign + ' ' + term)
        k = k + 1
    if first:
        lines.append('P(x) = 0')
    return lines


def _getN():
    n = _askint('terms N (1..6):')
    if n is None:
        return None
    if n < 1:
        n = 1
    if n > 6:
        n = 6
    return n


def t_maclaurin():
    s = casui.input_expr('f(x):')
    if s is None:
        return
    f = caslex.parse(s)
    if f is None:
        _show('MACLAURIN', [_warn('Could not parse f(x)')])
        return
    n = _getN()
    if n is None:
        return
    terms = _build_terms(f)[:n]
    try:
        head = 'f(x) = ' + caseng.tostr(f)
    except:
        head = 'f(x)'
    lines = [_w(head)]
    for ln in _poly_lines(terms):
        lines.append(ln)
    _show('MACLAURIN (N=' + str(n) + ')', lines)


def t_approx():
    s = casui.input_expr('f(x):')
    if s is None:
        return
    f = caslex.parse(s)
    if f is None:
        _show('APPROX', [_warn('Could not parse f(x)')])
        return
    n = _getN()
    if n is None:
        return
    xv = _asknum('x value:')
    if xv is None:
        return
    terms = _build_terms(f)[:n]
    approx = 0.0
    p = 1.0
    k = 0
    while k < len(terms):
        approx = approx + terms[k] * p
        p = p * xv
        k = k + 1
    try:
        exact = caseng.evalf(f, xv)
        err = exact - approx
        lines = [_w('x = ' + _fn(xv)), 'series ~ ' + _fn(approx), 'f(x) = ' + _fn(exact), 'error = ' + _fn(err)]
    except:
        lines = [_w('x = ' + _fn(xv)), 'series ~ ' + _fn(approx), _warn('f(x) undefined here')]
    _show('APPROX (N=' + str(n) + ')', lines)


def t_reference():
    _show('MACLAURIN SERIES', [
        'e^x = 1+x+x^2/2!+...',
        '   (all x)',
        'ln(1+x)=x-x^2/2+x^3/3',
        '   (-1<x<=1)',
        'sin x = x-x^3/3!+x^5/5!',
        'cos x = 1-x^2/2!+x^4/4!',
        '(1+x)^n = 1+nx+',
        ' n(n-1)x^2/2!+... |x|<1'])


def t_differences():
    _show('Method of differences', ['Enter the term f(r), typed in r,',
                                    'for example 1/(r(r+1)).',
                                    'If it splits as g(r) - g(r+1) the',
                                    'sum telescopes to g(1) - g(n+1).'])
    s = casui.input_expr('f(r) =')
    if s is None:
        return
    f = caslex.parse(s)
    if f is None:
        _show('Differences', [_warn('Could not read that.')])
        return
    if f[0] != '/':
        _show('Differences', [_warn('Type f(r) as a single fraction,'),
                              _warn('for example 1/(r(r+2)) or'),
                              _warn('2/((2r-1)(2r+1)).')])
        return
    res = None
    try:
        res = caspoly.partial(f[1], f[2], 'r')
    except:
        res = None
    if res is None or res[0] is not None or len(res[1]) != 2:
        _show('Differences', [_warn('This does not split into two'),
                              _warn('simple fractions in r, so the'),
                              _warn('sum does not telescope this way.')])
        return
    terms = res[1]
    coefs = []
    shifts = []
    ok = True
    for top, fac, power in terms:
        if power != 1:
            ok = False
            break
        p = caspoly.poly(fac, 'r')
        c = caspoly.ratof(top)
        if p is None or len(p) != 2 or c is None:
            ok = False
            break
        coefs.append(c)
        shifts.append(p)
    if not ok:
        _show('Differences', [_warn('The two pieces are not both'),
                              _warn('simple linear fractions.')])
        return
    if caspoly.radd(coefs[0], coefs[1]) != caspoly.R0:
        _show('Differences', [_warn('The two numerators are not equal'),
                              _warn('and opposite, so the terms do not'),
                              _warn('cancel in pairs.')])
        return
    if shifts[0][1] != shifts[1][1]:
        _show('Differences', [_warn('The two denominators have'),
                              _warn('different coefficients of r,'),
                              _warn('so nothing cancels.')])
        return
    k = shifts[0][1]
    if coefs[0][0] < 0:
        coefs = [coefs[1], coefs[0]]
        shifts = [shifts[1], shifts[0]]
    A = coefs[0]
    ca = caspoly.rdiv(shifts[0][0], k)
    cb = caspoly.rdiv(shifts[1][0], k)
    gap = caspoly.rsub(cb, ca)
    d = caspoly.rint(gap)
    if d is None or d < 1 or d > 6:
        _show('Differences', [_warn('The gap between the two'),
                              _warn('denominators is not a small whole'),
                              _warn('number of steps, so the sum does'),
                              _warn('not telescope.')])
        return
    Ak = caspoly.rdiv(A, k)
    pieces = []
    j = 0
    while j < d:
        off = caspoly.radd(ca, (j, 1))
        if caspoly.rzero(off):
            den = ('v', 'r')
        elif off[0] < 0:
            den = ('-', ('v', 'r'), caspoly.ratnode(caspoly.rneg(off)))
        else:
            den = ('+', ('v', 'r'), caspoly.ratnode(off))
        pieces.append(('/', caspoly.ratnode(Ak), den))
        j += 1
    g = pieces[0]
    i = 1
    while i < len(pieces):
        g = ('+', g, pieces[i])
        i += 1
    g = cascalc.tidy(g)
    lines = [_w('f(r) = ' + caseng.tostr(caseng.simplify(f))), '',
             _w('partial fractions:')]
    for top, fac, power in terms:
        lines.append(_w('  ' + caseng.tostr(top) + ' / (' + caseng.tostr(fac) + ')'))
    lines.append('')
    lines.append('take g(r) = ' + caseng.tostr(g))
    lines.append(_w('then f(r) = g(r) - g(r+1)'))
    bad = False
    for rv in (1.0, 2.0, 3.5, 7.0):
        try:
            lhs = caseng.evalf(f, 0.0, False, {'r': rv})
            g1 = caseng.evalf(g, 0.0, False, {'r': rv})
            g2 = caseng.evalf(g, 0.0, False, {'r': rv + 1.0})
        except:
            continue
        if abs(lhs - (g1 - g2)) > 1e-9 * (1.0 + abs(lhs)):
            bad = True
    if bad:
        lines.append('')
        lines.append(_warn('CHECK FAILED: g(r) - g(r+1) does not'))
        lines.append(_warn('reproduce f(r). Do not use this.'))
        _show('Differences', lines)
        return
    lines.append(_warn('(checked numerically)'))
    lines.append('')
    lines.append(_w('sum from r=1 to n telescopes:'))
    lines.append('  S(n) = g(1) - g(n+1)')
    gn = caseng.subst(g, 'r', ('+', ('v', 'n'), ('n', 1)))
    try:
        g1v = caseng.evalf(g, 0.0, False, {'r': 1.0})
        lines.append(_w('  g(1) = ' + _fn(g1v)))
    except:
        pass
    lines.append('  S(n) = g(1) - [' + caseng.tostr(cascalc.tidy(gn)) + ']')
    n = _askint('evaluate at n = (or cancel)', 1, 100000)
    if n is not None:
        try:
            tot = caseng.evalf(g, 0.0, False, {'r': 1.0}) - \
                  caseng.evalf(g, 0.0, False, {'r': float(n) + 1.0})
            lines.append('')
            lines.append('S(' + str(n) + ') = ' + _fn(tot))
            if n <= 2000:
                acc = 0.0
                i = 1
                while i <= n:
                    acc += caseng.evalf(f, 0.0, False, {'r': float(i)})
                    i += 1
                lines.append(_warn('direct sum  = ' + _fn(acc)))
        except:
            lines.append('')
            lines.append(_warn('Could not evaluate at that n.'))
    lines.append('')
    lines.append(_w('As n grows, S(n) tends to g(1) when'))
    lines.append(_w('g(n+1) tends to 0.'))
    _show('Method of differences', lines)


TOOLS = [
    ('Sum of r', t_sum_r),
    ('Sum of r^2', t_sum_r2),
    ('Sum of r^3', t_sum_r3),
    ('Maclaurin of f(x)', t_maclaurin),
    ('Approx + error', t_approx),
    ('Method of differences', t_differences),
    ('Reference card', t_reference),
]


def run():
    casutil.run_tools('Series & Maclaurin', TOOLS)
