# Numerical methods: sign change (with a check that f is continuous there),
# Newton-Raphson, bisection, iteration of x = g(x) (converging or not,
# staircase or cobweb), the trapezium rule on f(x) (over or under estimate
# from the curvature) or on typed y values. Working values to 7 s.f., the
# answer to the Decimals setting. Trig in radians, as the course uses here.
import caseng
import eng
import recog
from eng import S, N, txt

def _f(t, v, x):
    try:
        y = caseng.evalf(t, x, False, {v: x})
    except Exception:
        return None
    if isinstance(y, complex):
        if abs(y.imag) > 1e-12:
            return None
        y = y.real
    if y != y or abs(y) > 1e200:
        return None
    return y

def _x(t, name):
    if t is None:
        return None
    x = recog.numv(t)
    if x is None:
        x = eng.val(t)
    if x is None or isinstance(x, complex):
        raise ValueError(name + ' must be a number')
    return x

def _steps(t, d, hi=50):
    if t is None:
        return d
    n = _x(t, 'steps')
    if n != int(n) or n < 1 or n > hi:
        raise ValueError('steps: 1 to ' + str(hi))
    return int(n)

def _s(x):
    return eng.sf(x, 7) if x is not None else 'undefined'

def _rad(F, lines):
    if F.rows and recog.anyfn(F.rows[0].f if F.rows[0].f else F.rows[0].lhs,
                              ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot')):
        lines.append(('w', 'trig in radians'))

def box(pre, x):
    # 7 s.f. as the working, the Decimals setting when FORMAT asks
    d = eng.dec(x)
    return ('=', pre, _s(x), d if d != _s(x) else None, N(x) if x >= 0 else ('neg', N(-x)))

def _fx(F):
    return F.fx if hasattr(F, 'fx') else ('-', ('v', F.var), F.g)

def _ftext(F):
    return 'f(' + F.var + ') = ' + txt(S(_fx(F)))

def _gap(f, v, a, b):
    # where f is undefined or jumps between a and b, else None
    n = 400
    prev = _f(f, v, a)
    big = abs(prev or 0) + abs(_f(f, v, b) or 0) + 1
    for k in range(1, n + 1):
        x = a + (b - a) * k / n
        y = _f(f, v, x)
        if y is None:
            return x
        if prev is not None and (y > 0) != (prev > 0) and abs(y - prev) > 50 * big:
            return x
        prev = y
    return None

def signs(F, arg, vals):
    v = F.var
    f = _fx(F)
    a = _x(vals[0], 'from')
    b = _x(vals[1], 'to')
    if a >= b:
        raise ValueError('from must be less than to')
    lines = [_ftext(F)]
    _rad(F, lines)
    n = _steps(vals[2], 1, 20)
    pts = [a + (b - a) * k / n for k in range(n + 1)]
    for x in pts:
        lines.append('f(' + _s(x) + ') = ' + _s(_f(f, v, x)))
    ya = _f(f, v, a)
    yb = _f(f, v, b)
    if ya is None or yb is None:
        lines.append(eng.boxs('', 'f is undefined at an end'))
        return lines
    g = _gap(f, v, a, b)
    if (ya > 0) != (yb > 0):
        if g is not None:
            lines.append('f is not continuous: it breaks near ' + v + ' = ' + eng.sf(g, 4))
            lines.append(eng.boxs('', 'sign change, but f breaks between: not a root'))
            return lines
        lines.append('f(' + _s(a) + ') ' + ('< 0' if ya < 0 else '> 0') + ', f(' + _s(b) + ') ' +
                     ('< 0' if yb < 0 else '> 0') + ', and f is continuous there')
        for i in range(n):
            y1 = _f(f, v, pts[i])
            y2 = _f(f, v, pts[i + 1])
            if y1 is not None and y2 is not None and (y1 > 0) != (y2 > 0):
                lines.append(eng.boxs('', 'sign change: a root between ' + _s(pts[i]) + ' and ' + _s(pts[i + 1])))
        return lines
    lines.append(eng.boxs('', 'no sign change between ' + _s(a) + ' and ' + _s(b)))
    lines.append(('w', 'there may still be an even number of roots, or a touching one'))
    return lines

def newton(F, arg, vals):
    v = F.var
    f = S(_fx(F))
    d = S(caseng.diff(f, v))
    x = _x(vals[0], v + '(1)')
    n = _steps(vals[1], 3)
    lines = [_ftext(F), "f'(" + v + ') = ' + txt(d)]
    _rad(F, lines)
    lines.append(v + '(n+1) = ' + v + '(n) - f(' + v + '(n))/f\'(' + v + '(n))')
    xs = [x]
    for k in range(1, n + 1):
        fx = _f(f, v, x)
        dx = _f(d, v, x)
        if fx is None or dx is None:
            raise ValueError('f or f\' is undefined at ' + v + ' = ' + _s(x))
        if abs(dx) < 1e-14:
            raise ValueError("f'(" + _s(x) + ') = 0: the tangent is flat, the method fails')
        x = x - fx / dx
        lines.append(v + '(' + str(k + 1) + ') = ' + _s(xs[-1]) + ' - (' + _s(fx) + ')/(' + _s(dx) + ') = ' + _s(x))
        xs.append(x)
    lines.append(box(v + '(' + str(n + 1) + ') = ', x))
    y = x
    for k in range(40):
        fy = _f(f, v, y)
        dy = _f(d, v, y)
        if fy is None or dy is None or abs(dy) < 1e-14:
            break
        y = y - fy / dy
    fy = _f(f, v, y)
    if fy is not None and abs(fy) < 1e-9:
        lines.append(('w', 'carried on, it settles at ' + v + ' = ' + _s(y)))
    return lines

def bisect(F, arg, vals):
    v = F.var
    f = _fx(F)
    a = _x(vals[0], 'from')
    b = _x(vals[1], 'to')
    n = _steps(vals[2], 5)
    lines = [_ftext(F)]
    _rad(F, lines)
    ya = _f(f, v, a)
    yb = _f(f, v, b)
    if ya is None or yb is None or (ya > 0) == (yb > 0):
        raise ValueError('f(from) and f(to) need opposite signs')
    for k in range(n):
        m = (a + b) / 2
        ym = _f(f, v, m)
        if ym is None:
            raise ValueError('f is undefined at ' + _s(m))
        lines.append('f(' + _s(m) + ') = ' + _s(ym) + ': root in [' + (_s(a) + ', ' + _s(m) if (ym > 0) != (ya > 0)
                                                                     else _s(m) + ', ' + _s(b)) + ']')
        if (ym > 0) != (ya > 0):
            b = m
        else:
            a, ya = m, ym
    lines.append(eng.boxs('', _s(a) + ' < ' + v + ' < ' + _s(b)))
    return lines

def iterate(F, arg, vals):
    v = F.var
    g = F.g
    x = _x(vals[0], v + '(1)')
    n = _steps(vals[1], 3)
    lines = [v + '(n+1) = ' + txt(g)]
    _rad(F, lines)
    for k in range(1, n + 1):
        y = _f(g, v, x)
        if y is None:
            raise ValueError('g is undefined at ' + v + ' = ' + _s(x))
        lines.append(v + '(' + str(k + 1) + ') = ' + _s(y))
        x = y
    lines.append(box(v + '(' + str(n + 1) + ') = ', x))
    # where it goes
    y = x
    ys = []
    for k in range(200):
        z = _f(g, v, y)
        if z is None or abs(z) > 1e12:
            ys = None
            break
        ys.append(z)
        y = z
    if ys is None or abs(ys[-1] - ys[-2]) > 1e-9 * (1 + abs(ys[-1])):
        lines.append(('w', 'carried on, it does not settle: it diverges (or cycles)'))
        return lines
    L = ys[-1]
    d = _f(S(caseng.diff(g, v)), v, L)
    shape = ''
    if d is not None:
        shape = ': staircase' if d > 0 else ': cobweb'
    lines.append(('w', 'carried on, it converges to ' + _s(L) + shape))
    return lines

def _trap(xs, ys, h, lines):
    n = len(ys) - 1
    mid = 0.0
    for y in ys[1:-1]:
        mid += y
    lines.append('h = ' + _s(h))
    lines.append('y: ' + ', '.join([_s(y) for y in ys]))
    lines.append('area ~ h/2 (y0 + y' + str(n) + ' + 2(y1 + ... + y' + str(n - 1) + '))' if n > 1
                 else 'area ~ h/2 (y0 + y1)')
    r = h / 2 * (ys[0] + ys[-1] + 2 * mid)
    lines.append('= ' + _s(h / 2) + ' (' + _s(ys[0]) + ' + ' + _s(ys[-1]) + (' + 2(' + _s(mid) + ')' if n > 1 else '')
                 + ') = ' + _s(r))
    return r

def trap(F, arg, vals):
    v = F.var
    f = F.fx
    a = _x(vals[0], 'from')
    b = _x(vals[1], 'to')
    n = _steps(vals[2], 4, 200)
    h = (b - a) / n
    xs = [a + h * k for k in range(n + 1)]
    ys = []
    for x in xs:
        y = _f(f, v, x)
        if y is None:
            raise ValueError('f is undefined at ' + v + ' = ' + _s(x))
        ys.append(y)
    lines = ['f(' + v + ') = ' + txt(f)]
    _rad(F, lines)
    lines.append(v + ': ' + ', '.join([_s(x) for x in xs]))
    r = _trap(xs, ys, h, lines)
    lines.append(box('area ~ ', r))
    # over or under: the curvature between a and b
    try:
        d2 = S(caseng.diff(S(caseng.diff(f, v)), v))
        cs = [_f(d2, v, a + (b - a) * (k + 0.5) / 20) for k in range(20)]
        if None not in cs and min(cs) > 0:
            lines.append(('w', "f'' > 0 there (convex): the trapezia lie above, an over-estimate"))
        elif None not in cs and max(cs) < 0:
            lines.append(('w', "f'' < 0 there (concave): the trapezia lie below, an under-estimate"))
    except Exception:
        pass
    if min(ys) < 0:
        lines.append(('w', 'some y are negative: the curve is below the axis there'))
    return lines

def trapdata(F, arg, vals):
    h = _x(vals[0], 'h')
    ys = [recog.numv(t) for t in F.data]
    if len(ys) < 2:
        raise ValueError('at least two y values')
    lines = [str(len(ys) - 1) + ' strips']
    r = _trap(None, ys, h, lines)
    lines.append(box('area ~ ', r))
    return lines
