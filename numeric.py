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


def _askfn(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    return caslex.parse(s)


def _ev(tree, x):
    return caseng.evalf(tree, x)


def _fn(x):
    try:
        r = round(x, 6)
    except:
        return str(x)
    if r != r:
        return 'nan'
    if r > 1e300 or r < -1e300:
        return 'inf' if r > 0 else '-inf'
    try:
        if r == int(r):
            return str(int(r))
    except:
        return str(r)
    return str(r)


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


def _show(title, lines):
    casui.result_screen(title, lines)


def _pages(title, lines):
    if not lines:
        _show(title, ['(no rows)'])
        return
    per = 6
    i = 0
    n = len(lines)
    while i < n:
        chunk = lines[i:i + per]
        more = (i + per) < n
        ttl = title
        if n > per:
            ttl = title + ' (' + str(i // per + 1) + ')'
        if more:
            chunk = chunk + ['...more...']
        _show(ttl, chunk)
        i += per


def t_newton():
    f = _askfn('f(x)=')
    if f is None:
        _show('Newton-Raphson', ['Bad function'])
        return
    try:
        d = caseng.diff(f, 'x')
    except:
        _show('Newton-Raphson', ['Cannot differentiate'])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    lines = ["f'(x)=" + caseng.tostr(d)]
    x = x0
    ok = False
    for it in range(1, 51):
        try:
            fx = _ev(f, x)
            dfx = _ev(d, x)
        except:
            lines.append('n' + str(it) + ': eval error')
            break
        if dfx == 0:
            lines.append('n' + str(it) + ": f'=0, stop")
            break
        nx = x - fx / dfx
        dx = nx - x
        lines.append('n' + str(it) + ' x=' + _fn(nx))
        x = nx
        if abs(dx) < 1e-9:
            ok = True
            break
    if ok:
        lines.append('root x=' + _fn(x))
    else:
        lines.append('no converge in 50')
    _pages('Newton-Raphson', lines)


def t_fixed():
    g = _askfn('g(x)= (x=g(x))')
    if g is None:
        _show('Fixed-point', ['Bad function'])
        return
    x0 = _asknum('start x0=')
    if x0 is None:
        return
    lines = ['x=g(x) iteration']
    x = x0
    ok = False
    for it in range(1, 51):
        try:
            nx = _ev(g, x)
        except:
            lines.append('n' + str(it) + ': eval error')
            break
        dx = nx - x
        lines.append('n' + str(it) + ' x=' + _fn(nx))
        x = nx
        if abs(dx) < 1e-9:
            ok = True
            break
        if abs(x) > 1e12:
            lines.append('diverged')
            break
    if ok:
        lines.append('fixed pt x=' + _fn(x))
    _pages('Fixed-point', lines)


def t_bisect():
    f = _askfn('f(x)=')
    if f is None:
        _show('Bisection', ['Bad function'])
        return
    a = _asknum('a=')
    if a is None:
        return
    b = _asknum('b=')
    if b is None:
        return
    if a == b:
        _show('Bisection', ['a and b must differ'])
        return
    try:
        fa = _ev(f, a)
        fb = _ev(f, b)
    except:
        _show('Bisection', ['eval error'])
        return
    if fa * fb > 0:
        _show('Bisection', ['No sign change', 'f(a)=' + _fn(fa), 'f(b)=' + _fn(fb)])
        return
    lines = ['sign change OK']
    m = a
    ok = False
    for it in range(1, 51):
        m = (a + b) / 2.0
        try:
            fm = _ev(f, m)
        except:
            lines.append('n' + str(it) + ': eval error')
            break
        lines.append('n' + str(it) + ' m=' + _fn(m))
        if fm == 0 or abs(b - a) / 2.0 < 1e-9:
            ok = True
            break
        if fa * fm < 0:
            b = m
            fb = fm
        else:
            a = m
            fa = fm
    if ok:
        lines.append('root x=' + _fn(m))
    else:
        lines.append('approx x=' + _fn(m))
    _pages('Bisection', lines)


def t_integ():
    f = _askfn('f(x)=')
    if f is None:
        _show('Integration', ['Bad function'])
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
    n = int(n)
    if n < 1:
        _show('Integration', ['n must be >=1'])
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
        _show('Integration', ['eval error'])
        return
    lines = ['h=' + _fn(h), 'trapezium=' + _fn(trap), 'midpoint=' + _fn(mid)]
    if n % 2 == 0:
        try:
            sm = _ev(f, a) + _ev(f, b)
            for i in range(1, n):
                c = 4.0 if (i % 2 == 1) else 2.0
                sm += c * _ev(f, a + i * h)
            sm = sm * h / 3.0
            lines.append('Simpson=' + _fn(sm))
        except:
            lines.append('Simpson: eval error')
    else:
        lines.append('Simpson: need even n')
    _pages('Integration', lines)


def t_diff():
    f = _askfn('f(x)=')
    if f is None:
        _show('Differentiation', ['Bad function'])
        return
    x0 = _asknum('point x=')
    if x0 is None:
        return
    h = _asknum('step h=')
    if h is None or h == 0:
        _show('Differentiation', ['h must be nonzero'])
        return
    try:
        fwd = (_ev(f, x0 + h) - _ev(f, x0)) / h
        cen = (_ev(f, x0 + h) - _ev(f, x0 - h)) / (2.0 * h)
    except:
        _show('Differentiation', ['eval error'])
        return
    lines = ['at x=' + _fn(x0) + ' h=' + _fn(h), 'forward=' + _fn(fwd), 'central=' + _fn(cen)]
    try:
        d = caseng.diff(f, 'x')
        exact = _ev(d, x0)
        lines.append('exact=' + _fn(exact))
    except:
        pass
    _show('Differentiation', lines)


def t_euler():
    f = _askfn('dy/dx=f(x)')
    if f is None:
        _show('Euler', ['Bad function'])
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
        _show('Euler', ['N must be >=1'])
        return
    if nn > 500:
        nn = 500
    lines = ['f uses x only (1 var)', 'x0=' + _fn(x0) + ' y0=' + _fn(y0)]
    x = x0
    y = y0
    lines.append('n0 x=' + _fn(x) + ' y=' + _fn(y))
    ok = True
    for it in range(1, nn + 1):
        try:
            slope = _ev(f, x)
        except:
            lines.append('n' + str(it) + ': eval error')
            ok = False
            break
        y = y + h * slope
        x = x + h
        lines.append('n' + str(it) + ' x=' + _fn(x) + ' y=' + _fn(y))
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
        lines.append('relative: exact=0')
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
    _show('Round to s.f.', ['value=' + _fn(v), str(k) + ' s.f. = ' + _fn(r)])


TOOLS = [
    ('Newton-Raphson', t_newton),
    ('Fixed-point iteration', t_fixed),
    ('Bisection', t_bisect),
    ('Integration (trap/mid/Simp)', t_integ),
    ('Numerical derivative', t_diff),
    ('Euler method', t_euler),
    ('Error abs/relative', t_error),
    ('Round to s.f.', t_round),
]


def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Numerical Methods', labels)
        if c == -1:
            return
        TOOLS[c][1]()