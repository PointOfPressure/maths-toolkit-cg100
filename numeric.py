import math
import casui
import caseng
import casutil

_asknum = casutil.asknum
_askfn = casutil.askexpr
_asklist = casutil.asklist


def _ev(tree, x, env=None):
    return caseng.evalf(tree, x, False, env)


def _fn(x):
    return casutil.fmt(x, 6)


def _f8(x):
    return casutil.fmt(x, 8)


def _f9(x):
    if isinstance(x, float) and x == x and x != 0:
        if abs(x) < 1e-9:
            return str(_sig(x, 4))
    return casutil.fmt(x, 9)


def _sig(x, k):
    if x == 0:
        return 0.0
    if k < 1:
        k = 1
    neg = x < 0
    a = -x if neg else x
    d = 0
    t = a
    g = 0
    while t >= 10 and g < 400:
        t = t / 10.0
        d += 1
        g += 1
    g = 0
    while t < 1 and g < 400:
        t = t * 10.0
        d -= 1
        g += 1
    p = k - 1 - d
    f = 1.0
    if p >= 0:
        for i in range(p):
            f = f * 10.0
        r = round(a * f) / f
    else:
        for i in range(-p):
            f = f * 10.0
        r = round(a / f) * f
    return -r if neg else r


_show = casutil.show
_pages = casutil.show
_w = casutil.w
_warn = casutil.warn


def _bound(v, x):
    lim = 2.3e-16 * (1.0 + abs(x))
    return v if v > lim else lim


def t_newton():
    f = _askfn('f(x)=')
    if f is None:
        _show('Newton-Raphson', [_warn('Bad function')])
        return
    try:
        d = caseng.diff(f, 'x')
    except:
        _show('Newton-Raphson', [_warn('Cannot differentiate')])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    tol = _asknum('accuracy [1e-9]')
    if tol is None or tol <= 0:
        tol = 1e-9
    lines = [_w("f'(x)=" + caseng.tostr(d)), _w('target accuracy ' + _f9(tol))]
    x = x0
    dx = 0.0
    ok = False
    for it in range(1, 51):
        try:
            fx = _ev(f, x)
            dfx = _ev(d, x)
        except:
            lines.append(_warn('n' + str(it) + ': eval error'))
            break
        if dfx == 0:
            lines.append(_warn('n' + str(it) + ": f'=0, stop"))
            break
        nx = x - fx / dfx
        dx = nx - x
        lines.append(_w('n' + str(it) + ' x=' + _fn(nx)))
        x = nx
        if abs(dx) < tol:
            ok = True
            break
    if ok:
        lines.append('root x=' + _fn(x))
        lines.append(_w('last step |dx| = ' + _f9(abs(dx))))
        lines.append('error bound <= ' + _f9(_bound(abs(dx), x)))
        try:
            fv = _ev(f, x)
            dv = _ev(d, x)
            if dv != 0:
                lines.append(_w('next correction = ' + _f9(abs(fv / dv))))
        except:
            pass
    else:
        lines.append(_warn('no converge in 50'))
    _pages('Newton-Raphson', lines)


def t_fixed():
    g = _askfn('g(x)= (x=g(x))')
    if g is None:
        _show('Fixed-point', [_warn('Bad function')])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    tol = _asknum('accuracy [1e-9]')
    if tol is None or tol <= 0:
        tol = 1e-9
    lines = [_w('x=g(x) iteration'), _w('target accuracy ' + _f9(tol))]
    x = x0
    dx = 0.0
    pdx = None
    ok = False
    last = -1
    lasttxt = ''
    for it in range(1, 51):
        try:
            nx = _ev(g, x)
        except:
            lines.append(_warn('n' + str(it) + ': eval error'))
            break
        pdx = dx
        dx = nx - x
        lasttxt = 'n' + str(it) + ' x=' + _fn(nx)
        lines.append(_w(lasttxt))
        last = len(lines) - 1
        x = nx
        if abs(dx) < tol:
            ok = True
            break
        if abs(x) > 1e12:
            lines.append(_warn('diverged'))
            break
    if not ok and last >= 0:
        lines[last] = lasttxt
    if ok:
        lines.append('fixed pt x=' + _fn(x))
        bound = abs(dx)
        if pdx is not None and pdx != 0:
            r = abs(dx / pdx)
            if r < 1.0:
                bound = abs(dx) * r / (1.0 - r)
        lines.append(_w('last step |dx| = ' + _f9(abs(dx))))
        lines.append('error bound <= ' + _f9(_bound(bound, x)))
    _pages('Fixed-point', lines)


def t_bisect():
    f = _askfn('f(x)=')
    if f is None:
        _show('Bisection', [_warn('Bad function')])
        return
    a = _asknum('a=')
    if a is None:
        return
    b = _asknum('b=')
    if b is None:
        return
    if a == b:
        _show('Bisection', [_warn('a and b must differ')])
        return
    tol = _asknum('accuracy [1e-9]')
    if tol is None or tol <= 0:
        tol = 1e-9
    w0 = abs(b - a)
    try:
        fa = _ev(f, a)
        fb = _ev(f, b)
    except:
        _show('Bisection', [_warn('eval error')])
        return
    if (fa > 0 and fb > 0) or (fa < 0 and fb < 0):
        _show('Bisection', [_warn('No sign change'), _w('f(a)=' + _fn(fa)),
                            _w('f(b)=' + _fn(fb))])
        return
    lines = [_w('sign change OK'), _w('target accuracy ' + _f9(tol))]
    need = 0
    w = w0
    while w >= tol and need < 200:
        w = w / 2.0
        need += 1
    lines.append(_w('steps needed = ' + str(need)))
    m = a
    ok = False
    for it in range(1, 201):
        m = (a + b) / 2.0
        try:
            fm = _ev(f, m)
        except:
            lines.append(_warn('n' + str(it) + ': eval error'))
            break
        lines.append(_w('n' + str(it) + ' m=' + _fn(m)))
        if fm == 0 or abs(b - a) / 2.0 < tol:
            ok = True
            break
        if (fa < 0 and fm > 0) or (fa > 0 and fm < 0):
            b = m
            fb = fm
        else:
            a = m
            fa = fm
    if ok:
        lines.append('root x=' + _fn(m))
    else:
        lines.append('approx x=' + _fn(m))
    lines.append('error bound <= ' + _f9(abs(b - a) / 2.0))
    _pages('Bisection', lines)


def t_integ():
    f = _askfn('f(x)=')
    if f is None:
        _show('Integration', [_warn('Bad function')])
        return
    a = _asknum('a=')
    if a is None:
        return
    b = _asknum('b=')
    if b is None:
        return
    n = _asknum('strips n=')
    if n is None:
        return
    n = int(round(n))
    if n < 1:
        _show('Integration', [_warn('n must be >=1')])
        return
    if n > 2000:
        n = 2000
    h = (b - a) / n
    try:
        trap = _ev(f, a) + _ev(f, b)
        for i in range(1, n):
            trap += 2.0 * _ev(f, a + i * h)
        trap = trap * h / 2.0
        mid = 0.0
        for i in range(n):
            mid += _ev(f, a + (i + 0.5) * h)
        mid = mid * h
    except:
        _show('Integration', [_warn('eval error')])
        return
    lines = [_w('h=' + _fn(h)), 'trapezium=' + _fn(trap), 'midpoint=' + _fn(mid)]
    if n % 2 == 0:
        try:
            sm = _ev(f, a) + _ev(f, b)
            for i in range(1, n):
                c = 4.0 if (i % 2 == 1) else 2.0
                sm += c * _ev(f, a + i * h)
            sm = sm * h / 3.0
            lines.append('Simpson=' + _fn(sm))
        except:
            lines.append(_warn('Simpson: eval error'))
    else:
        lines.append(_warn('Simpson: need even n'))
    _pages('Integration', lines)


def t_diff():
    f = _askfn('f(x)=')
    if f is None:
        _show('Differentiation', [_warn('Bad function')])
        return
    x0 = _asknum('point x=')
    if x0 is None:
        return
    h = _asknum('step h=')
    if h is None or h == 0:
        _show('Differentiation', [_warn('h must be nonzero')])
        return
    try:
        fwd = (_ev(f, x0 + h) - _ev(f, x0)) / h
        cen = (_ev(f, x0 + h) - _ev(f, x0 - h)) / (2.0 * h)
    except:
        _show('Differentiation', [_warn('eval error')])
        return
    lines = [_w('at x=' + _fn(x0) + ' h=' + _fn(h)), 'forward=' + _fn(fwd),
             'central=' + _fn(cen)]
    try:
        d = caseng.diff(f, 'x')
        exact = _ev(d, x0)
        lines.append('exact=' + _fn(exact))
    except:
        pass
    _show('Differentiation', lines)


def t_euler():
    f = _askfn('dy/dx=f(x,y)')
    if f is None:
        _show('Euler', [_warn('Bad function')])
        return
    x0 = _asknum('x0=')
    if x0 is None:
        return
    y0 = _asknum('y0=')
    if y0 is None:
        return
    h = _asknum('step h=')
    if h is None:
        return
    nn = _asknum('steps N=')
    if nn is None:
        return
    nn = int(nn)
    if nn < 1:
        _show('Euler', [_warn('N must be >=1')])
        return
    if nn > 500:
        nn = 500
    lines = [_w('y(n+1) = y(n) + h f(x,y)'), _w('x0=' + _fn(x0) + ' y0=' + _fn(y0))]
    x = x0
    y = y0
    lines.append(_w('n0 x=' + _fn(x) + ' y=' + _fn(y)))
    ok = True
    for it in range(1, nn + 1):
        try:
            slope = _ev(f, x, {'y': y})
        except:
            lines.append(_warn('n' + str(it) + ': eval error'))
            ok = False
            break
        y = y + h * slope
        x = x + h
        lines.append(_w('n' + str(it) + ' x=' + _fn(x) + ' y=' + _fn(y)))
    if ok:
        lines.append('end y=' + _fn(y))
    _pages('Euler method', lines)


def t_error():
    ap = _asknum('approx=')
    if ap is None:
        return
    ex = _asknum('exact=')
    if ex is None:
        return
    absr = abs(ap - ex)
    lines = ['absolute=' + _fn(absr)]
    if ex != 0:
        lines.append('relative=' + _fn(absr / abs(ex)))
        lines.append('percent=' + _fn(100.0 * absr / abs(ex)) + '%')
    else:
        lines.append(_warn('relative: exact=0'))
    _show('Error', lines)


def t_round():
    v = _asknum('value=')
    if v is None:
        return
    k = _asknum('sig figs k=')
    if k is None:
        return
    k = int(k)
    if k < 1:
        k = 1
    if k > 12:
        k = 12
    r = _sig(v, k)
    _show('Round to s.f.', [_w('value=' + _fn(v)), str(k) + ' s.f. = ' + _fn(r)])


def _diffs(v):
    d = []
    k = 1
    while k < len(v):
        d.append(v[k] - v[k - 1])
        k += 1
    return d


def _ratios(d):
    r = []
    k = 1
    while k < len(d):
        if d[k] == 0:
            r.append(None)
        else:
            r.append(d[k - 1] / d[k])
        k += 1
    return r


def _shrink(d):
    r = []
    k = 1
    while k < len(d):
        if d[k - 1] == 0:
            r.append(None)
        else:
            r.append(d[k] / d[k - 1])
        k += 1
    return r


def _lastr(r):
    k = len(r) - 1
    while k >= 0:
        if r[k] is not None:
            return r[k]
        k -= 1
    return None


def _rstr(v):
    if v is None:
        return 'n/a'
    return _fn(v)


def _elide(rows, lines):
    n = len(rows)
    if n <= 14:
        k = 0
        while k < n:
            lines.append(_w(rows[k]))
            k += 1
        return
    k = 0
    while k < 3:
        lines.append(_w(rows[k]))
        k += 1
    lines.append(_w('  ... ' + str(n - 13) + ' rows omitted ...'))
    k = n - 10
    while k < n:
        lines.append(_w(rows[k]))
        k += 1


def _seqrows(d, r, lines):
    rows = []
    k = 0
    while k < len(d):
        s = 'd' + str(k) + '=' + _f8(d[k])
        if k >= 1:
            s += '  r' + str(k - 1) + '=' + _rstr(r[k - 1])
        rows.append(s)
        k += 1
    _elide(rows, lines)


def _errrows(labels, vals, lines):
    d = _diffs(vals)
    r = _ratios(d)
    k = 0
    while k < len(vals):
        s = labels[k] + ' ' + _f8(vals[k])
        if k >= 1:
            s += ' d=' + _f8(d[k - 1])
        if k >= 2:
            s += ' r=' + _rstr(r[k - 2])
        lines.append(_w(s))
        k += 1
    return _lastr(r)


LEVELS = 6


def _trapmid(f, a, b, n):
    h = (b - a) / n
    t = _ev(f, a) + _ev(f, b)
    i = 1
    while i < n:
        t += 2.0 * _ev(f, a + i * h)
        i += 1
    t = t * h / 2.0
    m = 0.0
    i = 0
    while i < n:
        m += _ev(f, a + (i + 0.5) * h)
        i += 1
    m = m * h
    return (h, t, m)


def t_integ_error():
    f = _askfn('f(x)=')
    if f is None:
        _show('Integration error', [_warn('Bad function')])
        return
    a = _asknum('a=')
    if a is None:
        return
    b = _asknum('b=')
    if b is None:
        return
    n0 = _asknum('start strips n [2]')
    if n0 is None:
        n0 = 2
    else:
        n0 = int(round(n0))
    if n0 < 1:
        n0 = 1
    if n0 > 32:
        n0 = 32
    ns = []
    ts = []
    ms = []
    ss = []
    labels = []
    n = n0
    try:
        k = 0
        while k < LEVELS:
            h, t, m = _trapmid(f, a, b, n)
            ns.append(n)
            ts.append(t)
            ms.append(m)
            ss.append((2.0 * m + t) / 3.0)
            labels.append('n=' + str(n))
            n = n * 2
            k += 1
    except:
        _show('Integration error', [_warn('eval error')])
        return
    lines = [_w('f(x)=' + caseng.tostr(f)), _w('a=' + _fn(a) + ' b=' + _fn(b)),
             _w('h halves down each column'),
             _w('-- trapezium T --')]
    rt = _errrows(labels, ts, lines)
    lines.append(_w('-- midpoint M --'))
    rm = _errrows(labels, ms, lines)
    lines.append(_w('-- Simpson S=(2M+T)/3 --'))
    rs = _errrows(labels, ss, lines)
    lines.append(_w('-- what the ratios mean --'))
    lines.append(_w('T ratio = ' + _rstr(rt)))
    lines.append(_w('M ratio = ' + _rstr(rm)))
    lines.append(_w('S ratio = ' + _rstr(rs)))
    lines.append(_w('ratio 4 => error ~ h^2 (2nd order)'))
    lines.append(_w('ratio 16 => error ~ h^4 (4th order)'))
    lines.append(_w('T and M are 2nd order,'))
    lines.append(_w('Simpson is 4th order.'))
    if len(ts) >= 2:
        lines.append('Richardson (4T2-T1)/3 = ' +
                     _f9((4.0 * ts[1] - ts[0]) / 3.0))
        lines.append(_w('  = Simpson on ' + str(2 * ns[0]) + ' strips'))
    lines.append('best T = ' + _f9(ts[len(ts) - 1]))
    lines.append('best M = ' + _f9(ms[len(ms) - 1]))
    lines.append('best S = ' + _f9(ss[len(ss) - 1]))
    _pages('Integration error', lines)


def t_richardson():
    vals = _asklist('A(h), A(h/2), A(h/4) ...')
    if vals is None or len(vals) < 2:
        _show('Richardson', [_warn('Need at least two'),
                             'estimates, each with h',
                             'half the one before.'])
        return
    p = _asknum('order p [2]')
    if p is None or p <= 0:
        p = 2.0
    lines = [_w('R(i,j) = R(i,j-1) +'),
             _w('  (R(i,j-1)-R(i-1,j-1))/(2^(pj)-1)'),
             _w('p = ' + _fn(p)),
             _w('column 0 (as entered):')]
    col = []
    k = 0
    while k < len(vals):
        col.append(vals[k])
        k += 1
    lines.append(_w('  ' + ' '.join([_f8(v) for v in col])))
    j = 1
    while j < len(vals):
        fac = 2.0 ** (p * j) - 1.0
        if fac == 0:
            break
        nxt = []
        i = 1
        while i < len(col):
            nxt.append(col[i] + (col[i] - col[i - 1]) / fac)
            i += 1
        col = nxt
        lines.append(_w('column ' + str(j) + ' (divide by ' + _fn(fac) + '):'))
        lines.append(_w('  ' + ' '.join([_f8(v) for v in col])))
        j += 1
    best = col[len(col) - 1]
    lines.append(_w('each column removes the next'))
    lines.append(_w('power of h from the error.'))
    lines.append('best = ' + _f9(best))
    if len(vals) >= 2:
        lines.append('improvement on last entry = ' +
                     _f9(abs(best - vals[len(vals) - 1])))
    _pages('Richardson', lines)


def t_aitken():
    xs = _asklist('sequence x0 x1 x2 ...')
    if xs is None or len(xs) < 3:
        _show('Aitken', [_warn('Need at least 3 terms.')])
        return
    lines = [_w("Aitken delta^2:"),
             _w("y = x - (dx)^2/(d2x)"),
             _w('given ' + str(len(xs)) + ' terms')]
    out = []
    k = 0
    while k + 2 < len(xs):
        d1 = xs[k + 1] - xs[k]
        d2 = xs[k + 2] - 2.0 * xs[k + 1] + xs[k]
        if d2 == 0:
            lines.append(_warn('y' + str(k) + ': second difference 0'))
        else:
            y = xs[k] - d1 * d1 / d2
            out.append(y)
            lines.append(_w('y' + str(k) + ' = ' + _f9(y)))
        k += 1
    if not out:
        lines.append(_warn('no accelerated value'))
        _pages('Aitken', lines)
        return
    lines.append(_w('the y sequence converges faster'))
    lines.append(_w('than the x sequence.'))
    lines.append('best = ' + _f9(out[len(out) - 1]))
    lines.append('shift on last x = ' +
                 _f9(abs(out[len(out) - 1] - xs[len(xs) - 1])))
    _pages('Aitken', lines)


def t_diff_error():
    f = _askfn('f(x)=')
    if f is None:
        _show('Derivative error', [_warn('Bad function')])
        return
    x0 = _asknum('point x=')
    if x0 is None:
        return
    h0 = _asknum('start h [0.4]')
    if h0 is None or h0 == 0:
        h0 = 0.4
    h0 = abs(h0)
    fwd = []
    cen = []
    labels = []
    h = h0
    try:
        k = 0
        while k < LEVELS:
            fwd.append((_ev(f, x0 + h) - _ev(f, x0)) / h)
            cen.append((_ev(f, x0 + h) - _ev(f, x0 - h)) / (2.0 * h))
            labels.append('h=' + _f8(h))
            h = h / 2.0
            k += 1
    except:
        _show('Derivative error', [_warn('eval error')])
        return
    lines = [_w('f(x)=' + caseng.tostr(f)), _w('at x=' + _fn(x0)),
             _w('-- forward (f(x+h)-f(x))/h --')]
    rf = _errrows(labels, fwd, lines)
    lines.append(_w('-- central (f(x+h)-f(x-h))/2h --'))
    rc = _errrows(labels, cen, lines)
    lines.append(_w('-- what the ratios mean --'))
    lines.append(_w('fwd ratio = ' + _rstr(rf)))
    lines.append(_w('cen ratio = ' + _rstr(rc)))
    lines.append(_w('ratio 2 => error ~ h (1st order)'))
    lines.append(_w('ratio 4 => error ~ h^2 (2nd order)'))
    nf = len(fwd)
    fe = 2.0 * fwd[nf - 1] - fwd[nf - 2]
    ce = (4.0 * cen[nf - 1] - cen[nf - 2]) / 3.0
    lines.append(_w('extrapolate: kill the leading'))
    lines.append(_w('error term from the last two.'))
    lines.append('fwd extrap = ' + _f9(fe))
    lines.append('cen extrap = ' + _f9(ce))
    try:
        d = caseng.diff(f, 'x')
        ex = _ev(d, x0)
        lines.append('exact = ' + _f9(ex))
        lines.append('err(fwd) = ' + _f9(abs(fwd[nf - 1] - ex)))
        lines.append('err(cen) = ' + _f9(abs(cen[nf - 1] - ex)))
        lines.append('err(cen extrap) = ' + _f9(abs(ce - ex)))
    except:
        pass
    lines.append(_warn('h too small: subtracting nearly'))
    lines.append(_warn('equal values loses accuracy.'))
    _pages('Derivative error', lines)


def _order_of(d):
    k = len(d) - 1
    while k >= 2:
        a = d[k - 2]
        b = d[k - 1]
        c = d[k]
        if a != 0 and b != 0 and c != 0:
            r1 = abs(b / a)
            r2 = abs(c / b)
            if r1 > 0 and r2 > 0 and r1 != 1.0:
                lo = math.log(r1)
                if lo != 0:
                    return math.log(r2) / lo
        k -= 1
    return None


def _verdict(r, lines):
    if r is None:
        lines.append(_warn('no usable ratio'))
        return
    lines.append('last ratio r = ' + _f9(r))
    if abs(r) >= 1.0:
        lines.append(_warn('|r| >= 1: the sequence'))
        lines.append(_warn('DIVERGES.'))
        return
    if abs(r) < 1e-3:
        lines.append('r collapsing towards 0:')
        lines.append('faster than first order')
        lines.append('(the error is squaring).')
        return
    lines.append('r settles to a constant, so')
    lines.append('the sequence is FIRST ORDER')
    lines.append('(linear), error x ' + _fn(abs(r)) + ' each step.')


def t_conv_order():
    xs = _asklist('iterates x0 x1 x2 ...')
    if xs is None or len(xs) < 3:
        _show('Order of convergence', [_warn('Need at least 3 iterates.')])
        return
    d = _diffs(xs)
    r = _shrink(d)
    lines = [_w('d(n) = x(n+1) - x(n)'),
             _w('r(n) = d(n+1)/d(n)')]
    _seqrows(d, r, lines)
    _verdict(_lastr(r), lines)
    p = _order_of(d)
    if p is None:
        lines.append(_warn('order p: not determined'))
    else:
        lines.append('order p = ' + _fn(p))
        if p > 1.5:
            lines.append('p near 2: SECOND ORDER,')
            lines.append('the error squares each step.')
        else:
            lines.append('p near 1: first order.')
    _pages('Order of convergence', lines)


def _gprime(g, x):
    try:
        d = caseng.diff(g, 'x')
        return _ev(d, x)
    except:
        pass
    try:
        h = 1e-5 * (1.0 + abs(x))
        return (_ev(g, x + h) - _ev(g, x - h)) / (2.0 * h)
    except:
        return None


def t_fixed_diag():
    g = _askfn('g(x)= (x=g(x))')
    if g is None:
        _show('Fixed-point diagnosis', [_warn('Bad function')])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    tol = _asknum('accuracy [1e-10]')
    if tol is None or tol <= 0:
        tol = 1e-10
    xs = [x0]
    x = x0
    ok = False
    blew = False
    it = 0
    while it < 60:
        try:
            nx = _ev(g, x)
        except:
            break
        if nx != nx:
            break
        xs.append(nx)
        dx = nx - x
        x = nx
        it += 1
        if abs(dx) < tol:
            ok = True
            break
        if abs(x) > 1e8:
            blew = True
            break
    lines = [_w('g(x)=' + caseng.tostr(g)), _w('x0=' + _fn(x0)),
             _w('steps taken = ' + str(it))]
    d = _diffs(xs)
    r = _shrink(d)
    _seqrows(d, r, lines)
    gp = _gprime(g, x)
    if ok:
        lines.append('fixed pt x = ' + _f9(x))
    elif blew:
        lines.append(_warn('no fixed point reached:'))
        lines.append(_warn('the iterates ran away.'))
    else:
        lines.append('stopped at x = ' + _f9(x))
    if gp is None:
        lines.append(_warn("g'(x) unavailable"))
    else:
        lines.append("g'(x) = " + _f9(gp))
        lines.append("|g'| = " + _f9(abs(gp)))
        if abs(gp) < 1.0:
            lines.append("|g'| < 1 so the iteration")
            lines.append('converges.')
            if abs(gp) < 1e-6:
                lines.append("g' = 0 here, so convergence")
                lines.append('is second order.')
            else:
                lines.append(_w('Fixed point iteration is'))
                lines.append(_w("FIRST ORDER: r tends to g'."))
        else:
            lines.append(_warn("|g'| > 1 so the iteration"))
            lines.append(_warn('diverges. Rearrange x=g(x)'))
            lines.append(_warn('a different way, or relax it.'))
    _pages('Fixed-point diagnosis', lines)


def t_relax():
    g = _askfn('g(x)= (x=g(x))')
    if g is None:
        _show('Relaxation', [_warn('Bad function')])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    lam = _asknum('relaxation L [1]')
    if lam is None:
        lam = 1.0
    tol = _asknum('accuracy [1e-10]')
    if tol is None or tol <= 0:
        tol = 1e-10
    lines = [_w('x(n+1) = x(n) + L(g(x(n))-x(n))'),
             _w('L = ' + _fn(lam) + ' (L=1 is plain iteration)')]
    x = x0
    xs = [x0]
    rows = []
    ok = False
    blew = False
    it = 0
    while it < 60:
        try:
            gx = _ev(g, x)
        except:
            break
        if gx != gx:
            break
        nx = x + lam * (gx - x)
        xs.append(nx)
        dx = nx - x
        x = nx
        it += 1
        rows.append('n' + str(it) + ' x=' + _fn(x))
        if abs(dx) < tol:
            ok = True
            break
        if abs(x) > 1e8:
            blew = True
            break
    _elide(rows, lines)
    if ok:
        lines.append('fixed pt x = ' + _f9(x))
    elif blew:
        lines.append(_warn('diverges with this L.'))
    else:
        lines.append('stopped at x = ' + _f9(x))
    gp = _gprime(g, x)
    if gp is not None:
        gg = 1.0 + lam * (gp - 1.0)
        lines.append("g'(x) = " + _f9(gp))
        lines.append("G(x) = x + L(g(x)-x), so")
        lines.append(_w("G'(x) = 1 + L(g'(x)-1)"))
        lines.append("G' = " + _f9(gg))
        if abs(gg) < 1.0:
            lines.append("|G'| < 1: this L converges.")
        else:
            lines.append(_warn("|G'| >= 1: this L fails."))
        if gp != 1.0:
            best = 1.0 / (1.0 - gp)
            lines.append('suggested L = ' + _f9(best))
            lines.append(_w('that choice makes the'))
            lines.append(_w('derivative zero: the fastest'))
            lines.append(_w('convergence available here.'))
        else:
            lines.append(_warn("g' = 1: no L helps."))
    _pages('Relaxation', lines)


def t_cobweb():
    g = _askfn('g(x)= (x=g(x))')
    if g is None:
        _show('Iteration diagram', [_warn('Bad function')])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    ns = _asknum('steps [8]')
    if ns is None:
        ns = 8
    else:
        ns = int(round(ns))
    if ns < 1:
        ns = 1
    if ns > 30:
        ns = 30
    xs = [x0]
    gs = []
    x = x0
    k = 0
    while k < ns:
        try:
            y = _ev(g, x)
        except:
            break
        if y != y or abs(y) > 1e6:
            break
        gs.append(y)
        xs.append(y)
        x = y
        k += 1
    if not gs:
        _show('Iteration diagram', [_warn('g(x0) could not be evaluated.')])
        return
    lo, hi = casutil.nice_range(xs, 0.15)
    fr = casutil.frame(lo, hi, lo, hi)
    casutil.axes(fr, 'x = g(x)', 'x', 'g(x)')
    casutil.seg(fr, lo, lo, hi, hi, casui.GREY)
    prev = None
    i = 0
    while i <= 120:
        xx = lo + (hi - lo) * i / 120.0
        yy = None
        try:
            yy = _ev(g, xx)
        except:
            yy = None
        if yy is not None and yy == yy and abs(yy) < 1e9:
            if prev is not None:
                casutil.seg(fr, prev[0], prev[1], xx, yy, casui.ACC)
            prev = (xx, yy)
        else:
            prev = None
        i += 1
    i = 0
    while i < len(gs):
        casutil.seg(fr, xs[i], xs[i], xs[i], gs[i], casui.RED)
        casutil.seg(fr, xs[i], gs[i], gs[i], gs[i], casui.RED)
        i += 1
    casutil.marker(fr, xs[0], xs[0], casui.BLACK, 2)
    casutil.chart_hold('grey y=x, blue y=g(x), red path')
    gp = _gprime(g, xs[len(xs) - 1])
    lines = [_w('g(x)=' + caseng.tostr(g)), _w('x0=' + _fn(x0)),
             _w('steps drawn = ' + str(len(gs)))]
    if gp is None:
        lines.append(_warn("g' unavailable, so the shape"))
        lines.append(_warn('cannot be named.'))
    else:
        lines.append("g'(x) = " + _f9(gp))
        if gp > 0:
            lines.append('STAIRCASE diagram:')
            lines.append(_w("g' > 0, so every step moves"))
            lines.append(_w('the same way and the path'))
            lines.append(_w('climbs like steps.'))
        elif gp < 0:
            lines.append('COBWEB diagram:')
            lines.append(_w("g' < 0, so the iterates"))
            lines.append(_w('alternate either side of the'))
            lines.append(_w('fixed point and the path'))
            lines.append(_w('spirals into a box.'))
        else:
            lines.append("g' = 0: one step lands on it.")
        if abs(gp) < 1.0:
            lines.append("|g'| < 1: the path closes in")
            lines.append('on the fixed point (converges).')
        else:
            lines.append(_warn("|g'| > 1: the path runs away"))
            lines.append(_warn('from it (diverges).'))
    rows = []
    i = 0
    while i < len(xs):
        rows.append('x' + str(i) + ' = ' + _fn(xs[i]))
        i += 1
    _elide(rows, lines)
    _pages('Iteration diagram', lines)


def _ptrim(p):
    k = len(p) - 1
    while k > 0 and p[k] == 0:
        p.pop()
        k -= 1
    return p


def _padd(a, b):
    n = len(a) if len(a) > len(b) else len(b)
    out = []
    k = 0
    while k < n:
        v = 0.0
        if k < len(a):
            v += a[k]
        if k < len(b):
            v += b[k]
        out.append(v)
        k += 1
    return out


def _pscale(a, s):
    out = []
    k = 0
    while k < len(a):
        out.append(a[k] * s)
        k += 1
    return out


def _plin(a, m, c):
    out = []
    k = 0
    while k < len(a) + 1:
        out.append(0.0)
        k += 1
    k = 0
    while k < len(a):
        out[k + 1] += a[k] * m
        out[k] += a[k] * c
        k += 1
    return out


def _polystr(c, var):
    parts = []
    k = len(c) - 1
    while k >= 0:
        s = _fn(c[k])
        if s == '0':
            k -= 1
            continue
        neg = s[0] == '-'
        if neg:
            s = s[1:]
        if k == 0:
            body = s
        else:
            body = '' if s == '1' else s + '*'
            body = body + (var if k == 1 else var + '^' + str(k))
        if not parts:
            parts.append(('-' if neg else '') + body)
        else:
            parts.append((' - ' if neg else ' + ') + body)
        k -= 1
    if not parts:
        return '0'
    return ''.join(parts)


def t_newton_fwd():
    ys = _asklist('y values (equal spacing)')
    if ys is None or len(ys) < 2:
        _show('Forward differences', [_warn('Need at least 2 y values.')])
        return
    if len(ys) > 10:
        ys = ys[:10]
    x0 = _asknum('x0 (first x)')
    if x0 is None:
        return
    h = _asknum('step h [1]')
    if h is None or h == 0:
        h = 1.0
    rows = [ys]
    k = 1
    while k < len(ys):
        prev = rows[k - 1]
        cur = []
        i = 1
        while i < len(prev):
            cur.append(prev[i] - prev[i - 1])
            i += 1
        if not cur:
            break
        rows.append(cur)
        k += 1
    lines = [_w('x0=' + _fn(x0) + ' h=' + _fn(h)),
             's = (x - x0)/h',
             _w('p = y0 + s.D1 + s(s-1)/2! D2 + ...'),
             _w('-- difference table --')]
    k = 0
    while k < len(rows):
        tag = 'y :' if k == 0 else 'D' + str(k) + ':'
        lines.append(_w(tag + ' ' + ' '.join([_fn(v) for v in rows[k]])))
        k += 1
    lines.append(_w('-- leading differences --'))
    k = 0
    while k < len(rows):
        nm = 'y0' if k == 0 else 'D' + str(k)
        lines.append(_w(nm + ' = ' + _fn(rows[k][0])))
        k += 1
    ps = [0.0]
    term = [1.0]
    k = 0
    while k < len(rows):
        ps = _padd(ps, _pscale(term, rows[k][0]))
        term = _pscale(_plin(term, 1.0, -1.0 * k), 1.0 / (k + 1))
        k += 1
    _ptrim(ps)
    px = [0.0]
    k = len(ps) - 1
    while k >= 0:
        px = _plin(px, 1.0 / h, -x0 / h)
        px = _padd(px, [ps[k]])
        k -= 1
    _ptrim(px)
    lines.append('p(s) = ' + _polystr(ps, 's'))
    lines.append('p(x) = ' + _polystr(px, 'x'))
    lines.append('degree = ' + str(len(px) - 1))
    xq = _asknum('estimate at x=')
    if xq is not None:
        s = (xq - x0) / h
        tot = 0.0
        cf = 1.0
        k = 0
        while k < len(rows):
            tot += rows[k][0] * cf
            cf = cf * (s - k) / (k + 1)
            k += 1
        lines.append(_w('s = ' + _fn(s)))
        lines.append('p(' + _fn(xq) + ') = ' + _f9(tot))
        if s < 0 or s > len(ys) - 1:
            lines.append(_warn('warning: that x is outside'))
            lines.append(_warn('the table (extrapolation).'))
    _pages('Forward differences', lines)


def t_err_prop():
    a = _asknum('a=')
    if a is None:
        return
    da = _asknum('error in a=')
    if da is None:
        return
    b = _asknum('b=')
    if b is None:
        return
    db = _asknum('error in b=')
    if db is None:
        return
    da = abs(da)
    db = abs(db)
    lines = [_w('a = ' + _fn(a) + ' +/- ' + _fn(da)),
             _w('b = ' + _fn(b) + ' +/- ' + _fn(db)),
             _w('sums/differences: ADD the'),
             _w('absolute errors.'),
             _w('products/quotients: ADD the'),
             _w('relative errors.')]
    ra = abs(da / a) if a != 0 else None
    rb = abs(db / b) if b != 0 else None
    lines.append('rel(a) = ' + (_f9(ra) if ra is not None else 'a=0'))
    lines.append('rel(b) = ' + (_f9(rb) if rb is not None else 'b=0'))
    es = da + db
    for tag, val in [('a+b', a + b), ('a-b', a - b)]:
        lines.append(tag + ' = ' + _f9(val))
        lines.append('err(' + tag + ') = ' + _f9(es))
        if val != 0:
            lines.append('rel(' + tag + ') = ' + _f9(abs(es / val)))
        else:
            lines.append(_warn('rel(' + tag + ') = infinite (result 0)'))
    if ra is not None and rb is not None:
        rr = ra + rb
        for tag, val in [('a*b', a * b), ('a/b', a / b if b != 0 else None)]:
            if val is None:
                lines.append(_warn(tag + ' = undefined (b=0)'))
                continue
            lines.append(tag + ' = ' + _f9(val))
            lines.append('err(' + tag + ') = ' + _f9(abs(val) * rr))
            lines.append('rel(' + tag + ') = ' + _f9(rr))
    else:
        lines.append(_warn('a or b is 0: no relative error'))
        lines.append(_warn('for the product or quotient.'))
    if abs(a - b) < 10.0 * es and es > 0:
        lines.append(_warn('WARNING: a-b subtracts nearly'))
        lines.append(_warn('equal numbers, so its relative'))
        lines.append(_warn('error is huge. Rearrange the'))
        lines.append(_warn('calculation to avoid it.'))
    _pages('Error propagation', lines)


def t_err_fx():
    f = _askfn('f(x)=')
    if f is None:
        _show('Error in f(x)', [_warn('Bad function')])
        return
    x0 = _asknum('x=')
    if x0 is None:
        return
    dx = _asknum('error in x=')
    if dx is None:
        return
    dx = abs(dx)
    try:
        fv = _ev(f, x0)
    except:
        _show('Error in f(x)', [_warn('eval error')])
        return
    gp = _gprime(f, x0)
    lines = [_w('f(x)=' + caseng.tostr(f)),
             _w('x = ' + _fn(x0) + ' +/- ' + _fn(dx)),
             'f(x) = ' + _f9(fv)]
    if gp is None:
        lines.append(_warn("f'(x) unavailable"))
    else:
        est = abs(gp) * dx
        lines.append("f'(x) = " + _f9(gp))
        lines.append(_w("error in f = |f'(x)| * dx"))
        lines.append('abs err = ' + _f9(est))
        if fv != 0:
            lines.append('rel err = ' + _f9(abs(est / fv)))
            lines.append('percent = ' + _fn(100.0 * abs(est / fv)) + '%')
    try:
        lo = _ev(f, x0 - dx)
        hi = _ev(f, x0 + dx)
        w = lo if lo < hi else hi
        z = hi if hi > lo else lo
        lines.append(_w('f(x-dx) = ' + _f9(lo)))
        lines.append(_w('f(x+dx) = ' + _f9(hi)))
        lines.append('actual range ' + _f9(w) + ' to ' + _f9(z))
        act = abs(hi - fv)
        if abs(lo - fv) > act:
            act = abs(lo - fv)
        lines.append('largest actual change = ' + _f9(act))
    except:
        lines.append(_warn('endpoints not evaluable'))
    _pages('Error in f(x)', lines)


def t_chop():
    v = _asknum('value=')
    if v is None:
        return
    dp = _asknum('decimal places d [3]')
    if dp is None:
        dp = 3
    dp = int(round(dp))
    if dp < 0:
        dp = 0
    if dp > 10:
        dp = 10
    u = 1.0
    k = 0
    while k < dp:
        u = u / 10.0
        k += 1
    scaled = v / u
    ch = math.floor(scaled) if v >= 0 else math.ceil(scaled)
    chop = ch * u
    rnd = round(v, dp)
    lines = [_w('value = ' + _f9(v)),
             _w('to ' + str(dp) + ' d.p., unit u = ' + _f9(u)),
             'chop = ' + _f9(chop),
             'round = ' + _f9(rnd),
             'chop error = ' + _f9(v - chop),
             'round error = ' + _f9(v - rnd),
             _w('chopping throws the rest away,'),
             _w('so its error is one-sided:'),
             'chop max err = ' + _f9(u),
             'chop mean err = ' + _f9(u / 2.0),
             _w('rounding goes to the nearer,'),
             _w('so its error is two-sided:'),
             'round max err = ' + _f9(u / 2.0),
             'round mean err = 0 (signed)',
             'round mean |err| = ' + _f9(u / 4.0),
             _w('chopping biases a long sum;'),
             _w('rounding does not.')]
    _pages('Chop vs round', lines)


TOOLS = [
    ('Newton-Raphson', t_newton),
    ('Fixed-point iteration', t_fixed),
    ('Fixed-point diagnosis', t_fixed_diag),
    ('Relaxation iteration', t_relax),
    ('Cobweb / staircase', t_cobweb),
    ('Order of convergence', t_conv_order),
    ('Bisection', t_bisect),
    ('Integration (trap/mid/Simp)', t_integ),
    ('Integration error table', t_integ_error),
    ('Richardson extrapolation', t_richardson),
    ('Aitken acceleration', t_aitken),
    ('Numerical derivative', t_diff),
    ('Derivative error table', t_diff_error),
    ('Newton forward differences', t_newton_fwd),
    ('Euler method', t_euler),
    ('Error abs/relative', t_error),
    ('Error propagation', t_err_prop),
    ('Error in f(x)', t_err_fx),
    ('Round to s.f.', t_round),
    ('Chop vs round', t_chop),
]


def run():
    casutil.run_tools('Numerical Methods', TOOLS)