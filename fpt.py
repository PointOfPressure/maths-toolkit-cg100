import math
import casui
import caseng
import cascalc
import caspoly
import casutil

def _finite(v):  # no math.isfinite on device
    return v == v and v not in (float('inf'), float('-inf'))

_asknum = casutil.asknum
_askint = casutil.askint
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show
_pages = casutil.show
_w = casutil.w
_warn = casutil.warn
_atan2 = casutil.atan2
_gcd = casutil.gcd
_powmod = casutil.powmod

def _f8(x):
    return casutil.fmt(x, 8)

def _f6(x):
    return casutil.fmt(x, 6)

def _fc(z):
    return casutil.fmtc(z.real, z.imag)

def _line(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sxs = 1 if x1 >= x0 else -1
    sys = 1 if y1 >= y0 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < 384 and 0 <= y0 < 192:
            casui.set_pixel(x0, y0, casui.RED)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sxs
        if e2 < dx:
            err += dx
            y0 += sys

def t_plot():
    tree = _askexpr('f(x) to plot')
    if tree is None:
        _show('Plot f(x)', [_warn('Could not read f(x).')])
        return
    xlo = _asknum('x min (e.g. -5)')
    if xlo is None:
        return
    xhi = _asknum('x max (e.g. 5)')
    if xhi is None or xhi <= xlo:
        _show('Plot f(x)', [_warn('Need x max > x min.')])
        return
    N = 240
    xs = []
    ys = []
    i = 0
    while i <= N:
        x = xlo + (xhi - xlo) * i / N
        try:
            y = caseng.evalf(tree, x)
        except:
            y = None
        if y is not None and _finite(y) and abs(y) < 1e9:
            xs.append(x)
            ys.append(y)
        else:
            xs.append(x)
            ys.append(None)
        i += 1
    fin = [y for y in ys if y is not None]
    if not fin:
        _show('Plot f(x)', [_warn('No finite values'), _warn('in that range.')])
        return
    ylo = min(fin)
    yhi = max(fin)
    if yhi - ylo < 1e-9:
        ylo -= 1.0
        yhi += 1.0
    px0 = 0
    px1 = 383
    py0 = 12
    py1 = 191
    casui.clear_screen()
    casui.draw_string(4, 0, 'y=' + caseng.tostr(tree)[:58], casui.ACC, 'small')

    def sx(x):
        return int(px0 + (x - xlo) / (xhi - xlo) * (px1 - px0))

    def sy(y):
        return int(py1 - (y - ylo) / (yhi - ylo) * (py1 - py0))

    if xlo <= 0 <= xhi:
        ax = sx(0.0)
        yy = py0
        while yy <= py1:
            casui.set_pixel(ax, yy, casui.GREY)
            yy += 1
    if ylo <= 0 <= yhi:
        ay = sy(0.0)
        casui.hline(px0, px1, ay, casui.GREY)
    prev = None
    k = 0
    while k < len(xs):
        y = ys[k]
        if y is None:
            prev = None
            k += 1
            continue
        cx = sx(xs[k])
        cy = sy(y)
        if cy < py0:
            cy = py0
        if cy > py1:
            cy = py1
        if prev is None:
            casui.set_pixel(cx, cy, casui.RED)
        else:
            _line(prev[0], prev[1], cx, cy)
        prev = (cx, cy)
        k += 1
    casui.draw_string(4, 178, 'x[' + _fn(xlo) + ',' + _fn(xhi) + '] y[' + _fn(ylo) + ',' + _fn(yhi) + ']', casui.GREY, 'small')
    casui.show_screen()
    casui.wait_release()
    casui.wait_press()
    casui.wait_release()

def t_demoivre():
    a = _asknum('Re(z)')
    if a is None:
        return
    b = _asknum('Im(z)')
    if b is None:
        return
    n = _askint('power n (integer)')
    if n is None:
        return
    z = complex(a, b)
    r = abs(z)
    if r == 0 and n <= 0:
        _show('z^n  (De Moivre)', [_warn('z = 0 with n <= 0'),
                                   _warn('is undefined.')])
        return
    th = _atan2(z.imag, z.real)
    rn = r ** n
    nth = n * th
    w = complex(rn * math.cos(nth), rn * math.sin(nth))
    _show('z^n  (De Moivre)', [_w('z = ' + _fc(z)),
                               _w('|z|=' + _fn(r) + ' arg=' + _fn(th) + 'r'),
                               _w('n = ' + str(n)),
                               _w('|z|^n = ' + _fn(rn)),
                               _w('n*arg = ' + _fn(nth) + ' rad'),
                               'z^n = ' + _fc(w)])

def t_roots():
    a = _asknum('Re(z)')
    if a is None:
        return
    b = _asknum('Im(z)')
    if b is None:
        return
    n = _askint('n (number of roots)')
    if n is None or n < 1:
        _show('nth roots', [_warn('n must be >= 1.')])
        return
    z = complex(a, b)
    r = abs(z)
    th = _atan2(z.imag, z.real)
    rr = r ** (1.0 / n)
    lines = [_w('z = ' + _fc(z)), 'each |root| = ' + _fn(rr),
             _w('arg step = 2pi/' + str(n))]
    k = 0
    while k < n:
        ang = (th + 2 * math.pi * k) / n
        w = complex(rr * math.cos(ang), rr * math.sin(ang))
        lines.append('w' + str(k) + ' = ' + _fc(w))
        k += 1
    _pages('nth roots of z', lines)

def t_euler():
    tree = _askexpr('dy/dx = f(x,y)')
    if tree is None:
        _show('Euler', [_warn('Could not read f(x).')])
        return
    x0 = _asknum('x0 (start)')
    if x0 is None:
        return
    y0 = _asknum('y0 = y(x0)')
    if y0 is None:
        return
    h = _asknum('step h')
    if h is None or h == 0:
        return
    n = _askint('steps (<=12)')
    if n is None or n < 1:
        return
    if n > 12:
        n = 12
    lines = [_w('y_n+1 = y_n + h.f(x_n,y_n)'), _w('------------------'),
             'x      y']
    x = x0
    y = y0
    lines.append(_w(_fn(x) + '   ' + _fn(y)))
    i = 0
    while i < n:
        try:
            slope = caseng.evalf(tree, x, False, {'y': y})
        except:
            slope = 0.0
        if not _finite(slope):
            slope = 0.0
        y = y + h * slope
        x = x + h
        txt = _fn(x) + '   ' + _fn(y)
        lines.append(txt if i == n - 1 else _w(txt))
        i += 1
    _pages('Euler method', lines)

def _slope(tree, x, y):
    v = caseng.evalf(tree, x, False, {'y': y})
    if not _finite(v):
        raise ValueError('slope not finite')
    return v

def _st_euler(tree, x, y, h):
    return y + h * _slope(tree, x, y)

def _st_rk2(tree, x, y, h):
    k1 = _slope(tree, x, y)
    k2 = _slope(tree, x + h / 2.0, y + h * k1 / 2.0)
    return y + h * k2

def _st_rk4(tree, x, y, h):
    k1 = _slope(tree, x, y)
    k2 = _slope(tree, x + h / 2.0, y + h * k1 / 2.0)
    k3 = _slope(tree, x + h / 2.0, y + h * k2 / 2.0)
    k4 = _slope(tree, x + h, y + h * k3)
    return y + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

def _march(tree, x0, y0, h, n, step):
    x = x0
    y = y0
    i = 0
    while i < n:
        y = step(tree, x, y, h)
        x = x + h
        i += 1
    return y

def t_rk():
    tree = _askexpr('dy/dx = f(x,y)')
    if tree is None:
        _show('Runge-Kutta', [_warn('Could not read f(x,y).')])
        return
    x0 = _asknum('x0 (start)')
    if x0 is None:
        return
    y0 = _asknum('y0 = y(x0)')
    if y0 is None:
        return
    h = _asknum('step h')
    if h is None or h == 0:
        return
    n = _askint('steps (<=50)')
    if n is None or n < 1:
        return
    if n > 50:
        n = 50
    lines = [_w('k1 = f(x, y)'),
             _w('k2 = f(x+h/2, y+h.k1/2)'),
             _w('k3 = f(x+h/2, y+h.k2/2)'),
             _w('k4 = f(x+h, y+h.k3)'),
             _w('Euler: y + h.k1'),
             _w('RK2 (midpoint): y + h.k2'),
             _w('RK4: y + h(k1+2k2+2k3+k4)/6'),
             _w('------------------'),
             _w('x   Euler / RK2 / RK4')]
    x = x0
    ye = y0
    y2 = y0
    y4 = y0
    lines.append(_w(_fn(x) + '  ' + _f8(ye)))
    ok = True
    i = 0
    while i < n:
        try:
            ye = _st_euler(tree, x, ye, h)
            y2 = _st_rk2(tree, x, y2, h)
            y4 = _st_rk4(tree, x, y4, h)
        except:
            lines.append(_warn('eval error at x=' + _fn(x)))
            ok = False
            break
        x = x + h
        lines.append(_w(_fn(x) + '  ' + _f8(ye)))
        lines.append(_w('    ' + _f8(y2) + ' / ' + _f8(y4)))
        i += 1
    if not ok:
        _pages('Runge-Kutta', lines)
        return
    lines.append(_w('------------------'))
    lines.append('at x = ' + _fn(x))
    lines.append('Euler y = ' + _f8(ye))
    lines.append('RK2 y = ' + _f8(y2))
    lines.append('RK4 y = ' + _f8(y4))
    lines.append('RK4 - Euler = ' + _f8(y4 - ye))
    lines.append('RK4 - RK2 = ' + _f8(y4 - y2))
    lines.append(_w('-- same interval, smaller h --'))
    hh = h
    nn = n
    j = 0
    while j < 3:
        try:
            e = _march(tree, x0, y0, hh, nn, _st_euler)
            r = _march(tree, x0, y0, hh, nn, _st_rk4)
        except:
            break
        lines.append(_w('h=' + _fn(hh) + ' Euler=' + _f8(e)))
        lines.append(_w('        RK4=' + _f8(r)))
        hh = hh / 2.0
        nn = nn * 2
        j += 1
    lines.append(_w('halving h divides the Euler'))
    lines.append(_w('error by about 2 and the RK4'))
    lines.append(_w('error by about 16: Euler is'))
    lines.append(_w('first order, RK4 is fourth.'))
    _pages('Runge-Kutta', lines)

def _simp(fn, a, b, n):
    if n % 2:
        n += 1
    h = (b - a) / n
    s = fn(a) + fn(b)
    i = 1
    while i < n:
        s += (4.0 if (i % 2) else 2.0) * fn(a + i * h)
        i += 1
    return s * h / 3.0

def t_arclen():
    c = casui.menu('Arc length', ['Cartesian y=f(x)',
                                  'Polar r(theta)',
                                  'Parametric x(t), y(t)'])
    if c < 0:
        return
    if c == 0:
        tree = _askexpr('y = f(x)')
        if tree is None:
            _show('Arc length', [_warn('Could not read f(x).')])
            return
        try:
            d = caseng.diff(tree, 'x')
        except:
            _show('Arc length', [_warn('Cannot differentiate.')])
            return
        a = _asknum('x from')
        if a is None:
            return
        b = _asknum('x to')
        if b is None:
            return

        def g(t):
            v = caseng.evalf(d, t)
            return math.sqrt(1.0 + v * v)

        head = [_w('s = integ sqrt(1 + (dy/dx)^2) dx'),
                _w('dy/dx = ' + caseng.tostr(caseng.simplify(d)))]
    elif c == 1:
        tree = _askexpr('r(theta), use x=theta:')
        if tree is None:
            _show('Arc length', [_warn('Could not read r.')])
            return
        try:
            d = caseng.diff(tree, 'x')
        except:
            _show('Arc length', [_warn('Cannot differentiate.')])
            return
        a = _asknum('theta from')
        if a is None:
            return
        b = _asknum('theta to')
        if b is None:
            return

        def g(t):
            r = caseng.evalf(tree, t)
            dr = caseng.evalf(d, t)
            return math.sqrt(r * r + dr * dr)

        head = [_w('s = integ sqrt(r^2 + (dr/dth)^2) dth'),
                _w('dr/dth = ' + caseng.tostr(caseng.simplify(d)))]
    else:
        xt = _askexpr('x(t), in t:')
        if xt is None:
            _show('Arc length', [_warn('Could not read x(t).')])
            return
        yt = _askexpr('y(t), in t:')
        if yt is None:
            _show('Arc length', [_warn('Could not read y(t).')])
            return
        try:
            dx = caseng.diff(xt, 't')
            dy = caseng.diff(yt, 't')
        except:
            _show('Arc length', [_warn('Cannot differentiate.')])
            return
        a = _asknum('t from')
        if a is None:
            return
        b = _asknum('t to')
        if b is None:
            return

        def g(t):
            u = caseng.evalf(dx, t, False, {'t': t})
            v = caseng.evalf(dy, t, False, {'t': t})
            return math.sqrt(u * u + v * v)

        head = [_w("s = integ sqrt(x'^2 + y'^2) dt"),
                _w("dx/dt = " + caseng.tostr(caseng.simplify(dx))),
                _w("dy/dt = " + caseng.tostr(caseng.simplify(dy)))]
    if b == a:
        _show('Arc length', [_warn('The two limits are equal.')])
        return
    try:
        s = _simp(g, a, b, 400)
        s2 = _simp(g, a, b, 800)
    except:
        _show('Arc length', [_warn('The integrand is not defined'),
                             _warn('somewhere in that range.')])
        return
    lines = []
    for t in head:
        lines.append(t)
    lines.append(_w('from ' + _fn(a) + ' to ' + _fn(b)))
    lines.append(_w('------------------'))
    lines.append(_w('400 panels: s = ' + _f8(s)))
    lines.append(_w('800 panels: s = ' + _f8(s2)))
    lines.append('arc length = ' + _f8(s2))
    lines.append('change on halving h = ' + _f8(abs(s2 - s)))
    _pages('Arc length', lines)

def t_gcdlcm():
    a = _askint('a (integer)')
    if a is None:
        return
    b = _askint('b (integer)')
    if b is None:
        return
    g = _gcd(a, b)
    l = casutil.lcm(a, b)
    _show('gcd & lcm', [_w('a = ' + str(a)), _w('b = ' + str(b)),
                        'gcd(a,b) = ' + str(g), 'lcm(a,b) = ' + str(l)])

NT_MAX = 100000000

def _isprime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def t_prime():
    n = _askint('n (integer)')
    if n is None:
        return
    if n > NT_MAX:
        _show('Prime test', [_warn('n too large for trial'),
                             _warn('division (max ' + str(NT_MAX) + ').')])
        return
    if _isprime(n):
        msg = str(n) + ' is PRIME.'
    else:
        msg = str(n) + ' is NOT prime.'
    _show('Prime test', [msg, _w('(trial division'), _w(' up to sqrt n)')])

def _chunk(s, n):
    out = []
    i = 0
    while i < len(s):
        out.append(s[i:i + n])
        i += n
    if not out:
        out = ['1']
    return out

def t_factor():
    n = _askint('n >= 2')
    if n is None:
        return
    if n < 2:
        _show('Factorise', [_warn('Need n >= 2.')])
        return
    if n > NT_MAX:
        _show('Factorise', [_warn('n too large for trial'),
                            _warn('division (max ' + str(NT_MAX) + ').')])
        return
    m = n
    facs = []
    d = 2
    while d * d <= m:
        e = 0
        while m % d == 0:
            m //= d
            e += 1
        if e > 0:
            facs.append((d, e))
        d = 3 if d == 2 else d + 2
    if m > 1:
        facs.append((m, 1))
    lines = [_w('n = ' + str(n)), _w('------------------')]
    parts = []
    for (p, e) in facs:
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(str(p) + '^' + str(e))
    s = ' * '.join(parts)
    if len(facs) == 1 and facs[0][1] == 1:
        lines.append(str(n) + ' = ' + s + '   (n is prime)')
    else:
        lines.append(str(n) + ' = ' + s)
    _pages('Prime factors', lines)

def t_powmod():
    a = _askint('base a')
    if a is None:
        return
    b = _askint('exponent b (>=0)')
    if b is None or b < 0:
        _show('a^b mod m', [_warn('Need b >= 0.')])
        return
    m = _askint('modulus m (>=1)')
    if m is None or m < 1:
        _show('a^b mod m', [_warn('Need m >= 1.')])
        return
    r = _powmod(a, b, m)
    _show('a^b mod m', [_w('a = ' + str(a)), _w('b = ' + str(b)),
                        _w('m = ' + str(m)),
                        _w('------------------'), 'a^b mod m = ' + str(r)])

def _egcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t

def t_modinv():
    a = _askint('a')
    if a is None:
        return
    m = _askint('modulus m (>=2)')
    if m is None or m < 2:
        _show('mod inverse', [_warn('Need m >= 2.')])
        return
    g, x, y = _egcd(a % m, m)
    if g != 1:
        _show('mod inverse', [_w('a = ' + str(a) + '  m = ' + str(m)),
                              _warn('gcd = ' + str(g) + ' (not 1)'),
                              _warn('no inverse exists.')])
        return
    inv = x % m
    _show('mod inverse', [_w('a = ' + str(a) + '  m = ' + str(m)),
                          'a^-1 mod m = ' + str(inv),
                          _warn('check: a*inv mod m'),
                          _warn('  = ' + str((a * inv) % m))])

def t_base():
    n = _askint('decimal n')
    if n is None:
        return
    neg = n < 0
    v = abs(n)
    if v == 0:
        b = '0'
        h = '0'
    else:
        b = ''
        t = v
        while t > 0:
            b = str(t & 1) + b
            t >>= 1
        digs = '0123456789ABCDEF'
        h = ''
        t = v
        while t > 0:
            h = digs[t & 15] + h
            t >>= 4
    sign = '-' if neg else ''
    _show('Base convert', [_w('decimal: ' + str(n)),
                           'binary:  ' + sign + b, 'hex:     ' + sign + h])

def t_totient():
    n = _askint('n >= 1')
    if n is None or n < 1:
        _show('Euler totient', [_warn('Need n >= 1.')])
        return
    if n > NT_MAX:
        _show('Euler totient', [_warn('n too large for trial'),
                                _warn('division (max ' + str(NT_MAX) + ').')])
        return
    m = n
    r = n
    facs = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            facs.append(d)
            while m % d == 0:
                m //= d
            r = r // d * (d - 1)
        d = 3 if d == 2 else d + 2
    if m > 1:
        facs.append(m)
        r = r // m * (m - 1)
    lines = [_w('n = ' + str(n)),
             _w('phi(n) counts the integers in'),
             _w('1..n that are coprime to n.'),
             _w('------------------')]
    if facs:
        lines.append('distinct primes: ' + ' '.join([str(p) for p in facs]))
        prod = 'n'
        for p in facs:
            prod = prod + ' * (1 - 1/' + str(p) + ')'
        lines.append(_w('phi = ' + prod))
    lines.append('phi(n) = ' + str(r))
    if len(facs) == 1 and facs[0] == n:
        lines.append('n is prime, so phi(n) = n-1.')
    lines.append(_w('a^phi(n) = 1 (mod n) when'))
    lines.append(_w('gcd(a, n) = 1 (Euler).'))
    _pages('Euler totient', lines)

def t_pythag():
    lim = _askint('max hypotenuse c')
    if lim is None or lim < 5:
        _show('Pythagorean triples', [_warn('Need c >= 5.')])
        return
    if lim > 2000:
        lim = 2000
    trs = []
    m = 2
    while m * m + 1 <= lim:
        n = 1
        while n < m:
            if (m - n) % 2 == 1 and _gcd(m, n) == 1:
                c = m * m + n * n
                if c <= lim:
                    a = m * m - n * n
                    b = 2 * m * n
                    if a > b:
                        a, b = b, a
                    trs.append((c, a, b))
            n += 1
        m += 1
    trs.sort()
    lines = [_w('primitive triples with c <= ' + str(lim)),
             _w('a^2 + b^2 = c^2'),
             _w('------------------')]
    for (c, a, b) in trs:
        lines.append(str(a) + ', ' + str(b) + ', ' + str(c))
    lines.append('count = ' + str(len(trs)))
    lines.append(_w('every other triple is a whole'))
    lines.append(_w('multiple of one of these.'))
    _pages('Pythagorean triples', lines)

def _isqrt(n):
    if n < 2:
        return n
    x = int(math.sqrt(n))
    while x * x > n:
        x -= 1
    while (x + 1) * (x + 1) <= n:
        x += 1
    return x

def t_pell():
    n = _askint('n (not a perfect square)')
    if n is None or n < 2:
        _show("Pell's equation", [_warn('Need n >= 2.')])
        return
    if n > 100000:
        _show("Pell's equation", [_warn('n too large (max 100000).')])
        return
    a0 = _isqrt(n)
    if a0 * a0 == n:
        _show("Pell's equation", [_warn(str(n) + ' is a perfect square,'),
                                 _warn('so x^2 - n y^2 = 1 has only'),
                                 _warn('the trivial solution x=1, y=0.')])
        return
    m = 0
    d = 1
    a = a0
    hp = 1
    h = a0
    kp = 0
    k = 1
    steps = 0
    while h * h - n * k * k != 1 and steps < 4000:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        h, hp = a * h + hp, h
        k, kp = a * k + kp, k
        steps += 1
    if h * h - n * k * k != 1:
        _show("Pell's equation", [_warn('No solution found within'),
                                 _warn('4000 continued-fraction steps.')])
        return
    lines = [_w('x^2 - ' + str(n) + ' y^2 = 1'),
             _w('sqrt(' + str(n) + ') = [' + str(a0) + '; ...]'),
             _w('continued fraction steps: ' + str(steps)),
             _w('------------------'),
             'x = ' + str(h),
             'y = ' + str(k),
             _warn('check x^2-n y^2 = ' + str(h * h - n * k * k)),
             _w('------------------'),
             _w('further solutions from'),
             _w('(x + y sqrt n)^j :')]
    x1 = h
    y1 = k
    xx = h
    yy = k
    j = 2
    while j <= 4:
        xx, yy = x1 * xx + n * y1 * yy, x1 * yy + y1 * xx
        lines.append('j=' + str(j) + ' x=' + str(xx))
        lines.append('    y=' + str(yy))
        j += 1
    _pages("Pell's equation", lines)

WILSON_MAX = 20000

def t_fermat():
    p = _askint('p (>=2)')
    if p is None or p < 2:
        _show('Fermat & Wilson', [_warn('Need p >= 2.')])
        return
    a = _askint('a (base for Fermat)')
    if a is None:
        return
    isp = _isprime(p) if p <= NT_MAX else None
    fl = _powmod(a, p - 1, p)
    lines = [_w('p = ' + str(p)), _w('a = ' + str(a))]
    if isp is None:
        lines.append(_warn('p too large to test for'))
        lines.append(_warn('primality here.'))
    elif isp:
        lines.append('p is PRIME.')
    else:
        lines.append('p is NOT prime.')
    lines.append(_w('------------------'))
    lines.append(_w('Fermat: a^(p-1) = 1 (mod p)'))
    lines.append(_w('for prime p not dividing a.'))
    lines.append('a^(p-1) mod p = ' + str(fl))
    if _gcd(a, p) != 1:
        lines.append(_warn('but gcd(a,p) = ' + str(_gcd(a, p)) +
                     ', so Fermat does not apply.'))
    elif fl == 1:
        lines.append('Fermat holds for this a.')
    else:
        lines.append('not 1, so p is COMPOSITE.')
    lines.append(_w('------------------'))
    lines.append(_w('Wilson: (p-1)! = -1 (mod p)'))
    lines.append(_w('exactly when p is prime.'))
    if p > WILSON_MAX:
        lines.append(_warn('p above ' + str(WILSON_MAX) + ': the factorial'))
        lines.append(_warn('loop would be too slow.'))
    else:
        w = 1
        i = 2
        while i <= p - 1:
            w = (w * i) % p
            i += 1
        lines.append('(p-1)! mod p = ' + str(w))
        lines.append(_w('-1 mod p = ' + str(p - 1)))
        if w == p - 1:
            lines.append('Wilson holds, so p is prime.')
        else:
            lines.append('Wilson fails, so p is not prime.')
    _pages('Fermat & Wilson', lines)

FIELD_NX = 15
FIELD_NY = 11
FIELD_LEN = 9.0
FIELD_STEPS = 120
SLOPE_CAP = 1e6

def _scale(fr):
    return ((fr[2] - fr[0]) / (fr[5] - fr[4]),
            (fr[3] - fr[1]) / (fr[7] - fr[6]))

def _fseg(fr, x, y, m, length):
    sx, sy = _scale(fr)
    ux = sx
    uy = -sy * m
    n = math.sqrt(ux * ux + uy * uy)
    if n <= 0.0 or not _finite(n):
        return None
    ux = ux * length / (2.0 * n)
    uy = uy * length / (2.0 * n)
    dx = ux / sx
    dy = -uy / sy
    return (x - dx, y - dy, x + dx, y + dy)

def _field(fr, tree, nx, ny, colour):
    drawn = 0
    j = 0
    while j < ny:
        y = fr[6] + (fr[7] - fr[6]) * (j + 0.5) / ny
        i = 0
        while i < nx:
            x = fr[4] + (fr[5] - fr[4]) * (i + 0.5) / nx
            try:
                m = _slope(tree, x, y)
            except:
                m = None
            if m is not None and _finite(m):
                if m > SLOPE_CAP:
                    m = SLOPE_CAP
                if m < -SLOPE_CAP:
                    m = -SLOPE_CAP
                e = _fseg(fr, x, y, m, FIELD_LEN)
                if e is not None:
                    casutil.seg(fr, e[0], e[1], e[2], e[3], colour)
                    drawn += 1
            i += 1
        j += 1
    return drawn

def _rkpath(tree, x0, y0, xend, n):
    pts = [(x0, y0)]
    if n < 1 or xend == x0:
        return pts
    h = (xend - x0) / n
    y = y0
    i = 0
    while i < n:
        xa = x0 + (xend - x0) * i / n
        try:
            y = _st_rk4(tree, xa, y, h)
        except:
            break
        if not _finite(y) or y > 1e12 or y < -1e12:
            break
        pts.append((x0 + (xend - x0) * (i + 1) / n, y))
        i += 1
    return pts

def _trim(xa, ya, xb, yb, lo, hi):
    t0 = 0.0
    t1 = 1.0
    d = yb - ya
    if d == 0.0:
        if ya < lo or ya > hi:
            return None
    else:
        ta = (lo - ya) / d
        tb = (hi - ya) / d
        if ta > tb:
            ta, tb = tb, ta
        if ta > t0:
            t0 = ta
        if tb < t1:
            t1 = tb
        if t0 > t1:
            return None
    return (xa + (xb - xa) * t0, ya + d * t0,
            xa + (xb - xa) * t1, ya + d * t1)

def _drawpath(fr, pts, colour):
    i = 1
    while i < len(pts):
        c = _trim(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1],
                  fr[6], fr[7])
        if c is not None:
            casutil.seg(fr, c[0], c[1], c[2], c[3], colour)
        i += 1

MAX_CURVES = 4

def t_tangentfield():
    tree = _askexpr('dy/dx = f(x,y)')
    if tree is None:
        _show('Tangent field', [_warn('Could not read f(x,y).')])
        return
    xlo = _asknum('x min')
    if xlo is None:
        return
    xhi = _asknum('x max')
    if xhi is None or xhi <= xlo:
        _show('Tangent field', [_warn('Need x max > x min.')])
        return
    ylo = _asknum('y min')
    if ylo is None:
        return
    yhi = _asknum('y max')
    if yhi is None or yhi <= ylo:
        _show('Tangent field', [_warn('Need y max > y min.')])
        return
    starts = []
    while len(starts) < MAX_CURVES:
        x0 = _asknum('solution through x0 (EXIT=no more)')
        if x0 is None:
            break
        y0 = _asknum('y0 = y(x0)')
        if y0 is None:
            break
        starts.append((x0, y0))
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'dy/dx = ' + caseng.tostr(tree)[:40], 'x', 'y')
    drawn = _field(fr, tree, FIELD_NX, FIELD_NY, casui.ACC)
    lines = [_w('tangent field of'),
             _w('dy/dx = ' + caseng.tostr(tree)),
             _w('x in [' + _fn(xlo) + ', ' + _fn(xhi) + ']'),
             _w('y in [' + _fn(ylo) + ', ' + _fn(yhi) + ']'),
             _w('grid ' + str(FIELD_NX) + ' x ' + str(FIELD_NY) +
             ', dashes: ' + str(drawn)),
             _w('every dash is the same length,'),
             _w('so only its slant carries f.'),
             _w('------------------')]
    k = 0
    while k < len(starts):
        x0, y0 = starts[k]
        fwd = _rkpath(tree, x0, y0, xhi, FIELD_STEPS)
        bwd = _rkpath(tree, x0, y0, xlo, FIELD_STEPS)
        _drawpath(fr, fwd, casui.RED)
        _drawpath(fr, bwd, casui.RED)
        k += 1
        lines.append('curve ' + str(k) + ' through (' + _fn(x0) + ', ' +
                     _fn(y0) + ')')
        lines.append('  y(' + _fn(bwd[len(bwd) - 1][0]) + ') = ' +
                     _f6(bwd[len(bwd) - 1][1]))
        lines.append('  y(' + _fn(fwd[len(fwd) - 1][0]) + ') = ' +
                     _f6(fwd[len(fwd) - 1][1]))
    if not starts:
        lines.append('no solution curve was asked for.')
    else:
        lines.append(_w('curves are RK4, forwards from'))
        lines.append(_w('the point and backwards.'))
    casutil.chart_hold('RK4 solution curves in red')
    _pages('Tangent field', lines)

LIM_H = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
LIM_HS = ['1e-1', '1e-2', '1e-3', '1e-4', '1e-5']
LIM_X = [1e2, 1e3, 1e4, 1e5, 1e6]
LIM_XS = ['1e2', '1e3', '1e4', '1e5', '1e6']

def _ev(tree, x):
    v = caseng.evalf(tree, x)
    if isinstance(v, complex) or not _finite(v):
        raise ValueError('not a real finite value')
    return v

def _samples(tree, pts):
    out = []
    i = 0
    while i < len(pts):
        try:
            out.append(_ev(tree, pts[i]))
        except:
            out.append(None)
        i += 1
    return out

def _at_pts(a, sgn):
    out = []
    i = 0
    while i < len(LIM_H):
        out.append(a + sgn * LIM_H[i])
        i += 1
    return out

def _inf_pts(sgn):
    out = []
    i = 0
    while i < len(LIM_X):
        out.append(sgn * LIM_X[i])
        i += 1
    return out

def _verdict(vals):
    n = len(vals)
    if n < 3:
        return ('none', None)
    a = vals[n - 3]
    b = vals[n - 2]
    c = vals[n - 1]
    if a is None or b is None or c is None:
        return ('none', None)
    d1 = abs(c - b)
    d2 = abs(b - a)
    if d1 <= 1e-3 * (1.0 + abs(c)) and d2 <= 1e-2 * (1.0 + abs(b)):
        L = (10.0 * c - b) / 9.0
        if abs(L - c) > 10.0 * d1 + 1e-9:
            L = c
        return ('num', _snap(L))
    if abs(c) > 1e4 and abs(c) >= 3.0 * abs(b) and abs(b) >= 3.0 * abs(a) \
            and (c < 0) == (b < 0):
        return ('inf', 1.0 if c > 0 else -1.0)
    return ('none', None)

def _snap(v):
    if v != v or abs(v) > 1e12:
        return v
    r = float(int(round(v)))
    if abs(v - r) < 1e-6:
        return r
    return v

def _vstr(k):
    if k[0] == 'num':
        return _f6(k[1])
    if k[0] == 'inf':
        return '+infinity' if k[1] > 0 else '-infinity'
    return 'no limit found'

def _limtable(lines, labels, la, lb):
    lines.append(_w('h        f(a-h) then f(a+h)'))
    i = 0
    while i < len(labels):
        sa = 'undefined' if la[i] is None else _f6(la[i])
        sb = 'undefined' if lb[i] is None else _f6(lb[i])
        lines.append(_w(labels[i] + ' below ' + sa))
        lines.append(_w('     above ' + sb))
        i += 1

def t_limit():
    tree = _askexpr('f(x)')
    if tree is None:
        _show('Limit of f(x)', [_warn('Could not read f(x).')])
        return
    c = casui.menu('Limit of f(x)', ['x -> a  (a finite)',
                                     'x -> +infinity',
                                     'x -> -infinity'])
    if c < 0:
        return
    lines = [_w('f(x) = ' + caseng.tostr(tree)), _w('------------------')]
    if c == 0:
        a = _asknum('a')
        if a is None:
            return
        lv = _samples(tree, _at_pts(a, -1.0))
        rv = _samples(tree, _at_pts(a, 1.0))
        kl = _verdict(lv)
        kr = _verdict(rv)
        lines.append(_w('x -> ' + _fn(a)))
        _limtable(lines, LIM_HS, lv, rv)
        lines.append(_w('------------------'))
        lines.append('from below: ' + _vstr(kl))
        lines.append('from above: ' + _vstr(kr))
        if kl[0] == 'num' and kr[0] == 'num' and \
                abs(kl[1] - kr[1]) <= 1e-6 * (1.0 + abs(kr[1])):
            L = (kl[1] + kr[1]) / 2.0
            lines.append('limit = ' + _f6(_snap(L)))
            try:
                fa = _ev(tree, a)
                if abs(fa - L) <= 1e-6 * (1.0 + abs(L)):
                    lines.append('f(a) = ' + _f6(fa) + ', so f is')
                    lines.append('continuous at x = ' + _fn(a) + '.')
                else:
                    lines.append(_warn('but f(a) = ' + _f6(fa) + ', so there'))
                    lines.append(_warn('is a removable discontinuity.'))
            except:
                lines.append(_warn('f(a) itself is undefined, so the'))
                lines.append(_warn('point is a hole in the curve.'))
        elif kl[0] == 'inf' and kr[0] == 'inf' and kl[1] == kr[1]:
            lines.append('limit = ' + ('+infinity' if kl[1] > 0 else '-infinity'))
            lines.append('so x = ' + _fn(a) + ' is a vertical')
            lines.append('asymptote.')
        elif kl[0] == 'inf' or kr[0] == 'inf':
            lines.append(_warn('the two sides disagree, so there'))
            lines.append(_warn('is no limit: x = ' + _fn(a) + ' is a'))
            lines.append(_warn('vertical asymptote.'))
        else:
            lines.append(_warn('the two sides disagree, so the'))
            lines.append(_warn('limit does not exist.'))
    else:
        sgn = 1.0 if c == 1 else -1.0
        vv = _samples(tree, _inf_pts(sgn))
        k = _verdict(vv)
        lines.append(_w('x -> ' + ('+' if sgn > 0 else '-') + 'infinity'))
        i = 0
        while i < len(LIM_XS):
            s = 'undefined' if vv[i] is None else _f6(vv[i])
            lines.append(_w(('x=' if sgn > 0 else 'x=-') + LIM_XS[i] +
                         '  f = ' + s))
            i += 1
        lines.append(_w('------------------'))
        lines.append('limit = ' + _vstr(k))
        if k[0] == 'num':
            lines.append('so y = ' + _f6(k[1]) + ' is a horizontal')
            lines.append('asymptote in that direction.')
    _pages('Limit of f(x)', lines)

VA_LO = -20.0
VA_HI = 20.0
VA_N = 400

def _absev(tree, x):
    try:
        return abs(_ev(tree, x))
    except:
        return 1e300

def _peak(tree, lo, hi):
    i = 0
    while i < 90 and (hi - lo) > 1e-11:
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        if _absev(tree, m1) < _absev(tree, m2):
            lo = m1
        else:
            hi = m2
        i += 1
    return _snap((lo + hi) / 2.0)

def _blowup(tree, c, sgn):
    ds = [1e-2, 1e-4, 1e-6, 1e-8]
    prev = None
    i = 0
    while i < len(ds):
        try:
            v = abs(_ev(tree, c + sgn * ds[i]))
        except:
            return False
        if prev is not None and v <= prev * 1.2:
            return False
        prev = v
        i += 1
    return prev > 10.0

def _brackets(tree, lo, hi, n):
    xs = []
    vs = []
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / n
        xs.append(x)
        try:
            vs.append(_ev(tree, x))
        except:
            vs.append(None)
        i += 1
    out = []
    i = 1
    while i < n:
        a = vs[i - 1]
        b = vs[i]
        d = vs[i + 1]
        hit = False
        if b is None and (a is not None or d is not None):
            hit = True
        elif b is not None and abs(b) > 50.0:
            if (a is None or abs(b) > 5.0 * abs(a)) or \
                    (d is None or abs(b) > 5.0 * abs(d)):
                hit = True
        if not hit and b is not None and d is not None:
            if abs(b) > 10.0 and abs(d) > 10.0 and ((b < 0) != (d < 0)):
                out.append((xs[i], xs[i + 1]))
        if hit:
            out.append((xs[i - 1], xs[i + 1]))
        i += 1
    return out

def _gridundef(tree, lo, hi, n):
    out = []
    prev = True
    i = 0
    while i <= n:
        x = lo + (hi - lo) * i / n
        try:
            _ev(tree, x)
            ok = True
        except:
            ok = False
        if not ok and prev:
            out.append(x)
        prev = ok
        i += 1
    return out

def _addnear(vals, v, tol):
    for w in vals:
        if abs(w - v) < tol:
            return
    vals.append(v)

MAX_VA = 12

def _verticals(tree, lo, hi):
    out = []
    for br in _brackets(tree, lo, hi, VA_N):
        if len(out) >= MAX_VA:
            break
        c = _peak(tree, br[0], br[1])
        if c < lo or c > hi:
            continue
        if _blowup(tree, c, 1.0) or _blowup(tree, c, -1.0):
            _addnear(out, c, 1e-3)
    out.sort()
    return out

def _side(tree, c, sgn):
    k = _verdict(_samples(tree, _at_pts(c, sgn)))
    if k[0] != 'none':
        return _vstr(k)
    if _blowup(tree, c, sgn):
        try:
            v = _ev(tree, c + sgn * 1e-8)
        except:
            return 'no limit found'
        return '+infinity' if v > 0 else '-infinity'
    return 'no limit found'

def _linstr(m, b):
    s = 'y = '
    if m == 1.0:
        s += 'x'
    elif m == -1.0:
        s += '-x'
    else:
        s += _f6(m) + 'x'
    if abs(b) < 1e-9:
        return s
    if b < 0:
        return s + ' - ' + _f6(-b)
    return s + ' + ' + _f6(b)

def _numden(tree):
    if tree[0] == '/':
        return (tree[1], tree[2])
    return (tree, ('n', 1))

def _rval(r):
    return float(r[0]) / float(r[1])

def t_asympt():
    tree = _askexpr('f(x)')
    if tree is None:
        _show('Asymptotes', [_warn('Could not read f(x).')])
        return
    lines = [_w('f(x) = ' + caseng.tostr(tree)), _w('------------------')]
    vs = _verticals(tree, VA_LO, VA_HI)
    if vs:
        for c in vs:
            lines.append('vertical: x = ' + _fn(c))
            lines.append('  from below f -> ' + _side(tree, c, -1.0))
            lines.append('  from above f -> ' + _side(tree, c, 1.0))
    else:
        lines.append(_warn('no vertical asymptote in'))
        lines.append(_warn('[' + _fn(VA_LO) + ', ' + _fn(VA_HI) + '].'))
    lines.append(_w('------------------'))
    num, den = _numden(tree)
    pn = caspoly.poly(num, 'x')
    pd = caspoly.poly(den, 'x')
    done = False
    if pn is not None and pd is not None and len(pd) >= 2:
        qr = caspoly.pdivmod(pn, pd)
        if qr is not None:
            q = qr[0]
            if len(q) <= 1:
                v = 0.0 if not q else _rval(q[0])
                lines.append('horizontal: y = ' + _fn(v) + '  (exact)')
                if not q:
                    lines.append(_w('deg(num) < deg(den), so f -> 0'))
                    lines.append(_w('at both ends.'))
                else:
                    lines.append(_w('deg(num) = deg(den), so f tends'))
                    lines.append(_w('to the ratio of the leading'))
                    lines.append(_w('coefficients at both ends.'))
                done = True
            elif len(q) == 2:
                lines.append('oblique: y = ' +
                             caseng.tostr(caspoly.ptree(q, 'x')) + '  (exact)')
                lines.append(_w('num = q(x).den + r(x) with'))
                lines.append(_w('r = ' + caseng.tostr(caspoly.ptree(qr[1], 'x'))))
                lines.append(_w('and r/den -> 0, so y = q(x).'))
                done = True
            else:
                lines.append(_warn('deg(num) - deg(den) = ' + str(len(q) - 1) + ','))
                lines.append(_warn('so there is no horizontal or'))
                lines.append(_warn('oblique asymptote.'))
                done = True
    kp = _verdict(_samples(tree, _inf_pts(1.0)))
    km = _verdict(_samples(tree, _inf_pts(-1.0)))
    lines.append('lim x->+inf f = ' + _vstr(kp))
    lines.append('lim x->-inf f = ' + _vstr(km))
    if not done:
        i = 0
        while i < 2:
            sgn = 1.0 if i == 0 else -1.0
            k = kp if i == 0 else km
            name = '+inf' if i == 0 else '-inf'
            i += 1
            if k[0] == 'num':
                lines.append('horizontal as x->' + name + ': y = ' + _f6(k[1]))
                continue
            mk = _verdict(_samples(('/', tree, ('v', 'x')), _inf_pts(sgn)))
            if mk[0] != 'num' or abs(mk[1]) < 1e-9:
                lines.append(_warn('no asymptote as x->' + name + '.'))
                continue
            m = _snap(mk[1])
            bk = _verdict(_samples(('-', tree, ('*', ('n', m), ('v', 'x'))),
                                   _inf_pts(sgn)))
            if bk[0] == 'num':
                lines.append('oblique as x->' + name + ': ' +
                             _linstr(m, _snap(bk[1])))
                lines.append(_w('  m = lim f(x)/x = ' + _f6(m)))
                lines.append(_w('  c = lim f(x) - mx = ' + _f6(_snap(bk[1]))))
            else:
                lines.append(_warn('no asymptote as x->' + name + '.'))
    _pages('Asymptotes', lines)

def t_statcusp():
    tree = _askexpr('f(x)')
    if tree is None:
        _show('Stationary pts & cusps', [_warn('Could not read f(x).')])
        return
    try:
        d1 = caseng.diff(tree, 'x')
    except:
        _show('Stationary pts & cusps', [_warn('Cannot differentiate f.')])
        return
    try:
        d2 = caseng.diff(d1, 'x')
    except:
        d2 = None
    lines = [_w('f(x) = ' + caseng.tostr(tree)),
             _w("f'(x) = " + caseng.tostr(caseng.simplify(d1))),
             _w('------------------')]
    roots = cascalc.solve(d1, 'x')
    if roots:
        for r in roots:
            try:
                y = _ev(tree, r)
            except:
                continue
            word = None
            dd = 0.01 * (1.0 + abs(r))
            for rr in roots:
                if rr != r and abs(rr - r) / 3.0 < dd:
                    dd = abs(rr - r) / 3.0
            try:
                la = _ev(d1, r - dd)
                rb = _ev(d1, r + dd)
                if la < 0.0 and rb > 0.0:
                    word = 'MINIMUM'
                elif la > 0.0 and rb < 0.0:
                    word = 'MAXIMUM'
                elif (la > 0.0 and rb > 0.0) or (la < 0.0 and rb < 0.0):
                    word = 'INFLECTION'
            except:
                word = None
            if word is None and d2 is not None:
                try:
                    s = _ev(d2, r)
                    if s > 0.0:
                        word = 'MINIMUM'
                    elif s < 0.0:
                        word = 'MAXIMUM'
                except:
                    word = None
            if word is None:
                word = 'INFLECTION'
            lines.append('x = ' + _fn(r) + '  y = ' + _fn(y) + '  ' + word)
            if d2 is not None:
                try:
                    lines.append(_w("  f'' = " + _fn(_ev(d2, r)) +
                                 ' (supporting only)'))
                except:
                    pass
    else:
        lines.append(_warn('no stationary point in'))
        lines.append(_warn('[' + _fn(VA_LO) + ', ' + _fn(VA_HI) + '].'))
    lines.append(_w('------------------'))
    found = 0
    cands = []
    for br in _brackets(d1, VA_LO, VA_HI, VA_N):
        c = _peak(d1, br[0], br[1])
        if VA_LO <= c <= VA_HI:
            _addnear(cands, c, 1e-3)
    for c in _gridundef(d1, VA_LO, VA_HI, VA_N):
        _addnear(cands, c, 1e-3)
    cands.sort()
    for c in cands:
        try:
            fa = _ev(tree, c - 1e-6)
            fb = _ev(tree, c + 1e-6)
        except:
            continue
        if abs(fa - fb) > 1e-3 * (1.0 + abs(fa)):
            continue
        if _blowup(tree, c, 1.0) or _blowup(tree, c, -1.0):
            continue
        sl = _side(d1, c, -1.0)
        sr = _side(d1, c, 1.0)
        if sl == sr:
            continue
        if sl == 'no limit found' and sr == 'no limit found':
            continue
        try:
            fc = _ev(tree, c)
        except:
            fc = (fa + fb) / 2.0
        if 'infinity' in sl and 'infinity' in sr:
            word = 'CUSP'
        elif 'infinity' in sl or 'infinity' in sr:
            word = 'VERTICAL TANGENT ONE SIDE'
        else:
            word = 'CORNER'
        found += 1
        lines.append(word + ' at x = ' + _fn(c) + ', y = ' + _fn(fc))
        lines.append("  f' from below -> " + sl)
        lines.append("  f' from above -> " + sr)
    if found == 0:
        lines.append(_warn('no cusp: the gradient has the'))
        lines.append(_warn('same finite limit from both'))
        lines.append(_warn('sides everywhere it was tested.'))
    else:
        lines.append(_w('a cusp is where f carries on but'))
        lines.append(_w("f' does not: the two one-sided"))
        lines.append(_w('limits of the gradient differ.'))
    _pages('Stationary pts & cusps', lines)

FAM_N = 120
FAM_MAX = 6
FAM_COLS = [casui.BLACK, casui.RED, casui.ACC, casui.GREY]

def _fam_ev(tree, x, a):
    v = caseng.evalf(tree, x, False, {'x': x, 'a': a})
    if isinstance(v, complex) or not _finite(v):
        raise ValueError('not a real finite value')
    return v

def _fam_curve(tree, a, xlo, xhi, n):
    pts = []
    i = 0
    while i <= n:
        x = xlo + (xhi - xlo) * i / n
        try:
            pts.append((x, _fam_ev(tree, x, a)))
        except:
            pts.append((x, None))
        i += 1
    return pts

def t_family():
    tree = _askexpr('family y = f(x,a), in x and a')
    if tree is None:
        _show('Family of curves', [_warn('Could not read f(x,a).')])
        return
    xlo = _asknum('x min')
    if xlo is None:
        return
    xhi = _asknum('x max')
    if xhi is None or xhi <= xlo:
        _show('Family of curves', [_warn('Need x max > x min.')])
        return
    avs = casutil.asklist('values of a (e.g. -2 0 2)')
    if not avs:
        _show('Family of curves', [_warn('Give at least one value of a.')])
        return
    if len(avs) > FAM_MAX:
        avs = avs[:FAM_MAX]
    curves = []
    ys = []
    for a in avs:
        pts = _fam_curve(tree, a, xlo, xhi, FAM_N)
        curves.append(pts)
        for p in pts:
            if p[1] is not None:
                ys.append(p[1])
    if not ys:
        _show('Family of curves', [_warn('No finite values in that'),
                                   _warn('x range.')])
        return
    ylo, yhi = casutil.nice_range(ys, 0.08)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'y = ' + caseng.tostr(tree)[:40], 'x', 'y')
    lines = [_w('family y = ' + caseng.tostr(tree)),
             _w('x in [' + _fn(xlo) + ', ' + _fn(xhi) + ']'),
             _w('------------------')]
    k = 0
    while k < len(curves):
        colour = FAM_COLS[k % len(FAM_COLS)]
        pts = curves[k]
        i = 1
        while i < len(pts):
            if pts[i - 1][1] is not None and pts[i][1] is not None:
                c = _trim(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1],
                          ylo, yhi)
                if c is not None:
                    casutil.seg(fr, c[0], c[1], c[2], c[3], colour)
            i += 1
        a = avs[k]
        k += 1
        fin = [p[1] for p in pts if p[1] is not None]
        lines.append('a=' + _fn(a) + ' y in [' + _fn(min(fin)) + ', ' +
                     _fn(max(fin)) + ']')
        try:
            sub = caseng.subst(tree, 'a', ('n', a))
            rts = [r for r in cascalc.solve(sub, 'x') if xlo <= r <= xhi]
        except:
            rts = []
        if rts:
            lines.append('a=' + _fn(a) + ' roots: ' +
                         ', '.join([_fn(r) for r in rts]))
        else:
            lines.append('a=' + _fn(a) + ' roots: none in range')
    lines.append(_w('------------------'))
    lines.append(_w('members drawn: ' + str(len(curves))))
    lines.append(_w('changing a moves the whole'))
    lines.append(_w('curve; what stays the same is'))
    lines.append(_w('the property of the family.'))
    casutil.chart_hold('one curve per value of a')
    _pages('Family of curves', lines)

ENV_NX = 41
ENV_NA = 40
ENV_EVERY = 10

def t_envelope():
    tree = _askexpr('family y = f(x,a), in x and a')
    if tree is None:
        _show('Envelope', [_warn('Could not read f(x,a).')])
        return
    try:
        g = caseng.diff(tree, 'a')
    except:
        _show('Envelope', [_warn('Cannot differentiate in a.')])
        return
    xlo = _asknum('x min')
    if xlo is None:
        return
    xhi = _asknum('x max')
    if xhi is None or xhi <= xlo:
        _show('Envelope', [_warn('Need x max > x min.')])
        return
    alo = _asknum('a min')
    if alo is None:
        return
    ahi = _asknum('a max')
    if ahi is None or ahi <= alo:
        _show('Envelope', [_warn('Need a max > a min.')])
        return
    env = []
    i = 0
    while i < ENV_NX:
        x = xlo + (xhi - xlo) * i / (ENV_NX - 1)
        col = i
        i += 1
        for a in _aroots(g, x, alo, ahi):
            try:
                env.append((x, a, _fam_ev(tree, x, a), col))
            except:
                pass
    if not env:
        _show('Envelope', [_warn('df/da = 0 has no solution'),
                           _warn('for a in that range, so this'),
                           _warn('family has no envelope here.')])
        return
    ys = [p[2] for p in env]
    ylo, yhi = casutil.nice_range(ys, 0.12)
    fr = casutil.frame(xlo, xhi, ylo, yhi)
    casutil.axes(fr, 'envelope of y = ' + caseng.tostr(tree)[:30], 'x', 'y')
    k = 0
    while k < 7:
        a = alo + (ahi - alo) * k / 6.0
        k += 1
        pts = _fam_curve(tree, a, xlo, xhi, 60)
        j = 1
        while j < len(pts):
            if pts[j - 1][1] is not None and pts[j][1] is not None:
                c = _trim(pts[j - 1][0], pts[j - 1][1], pts[j][0], pts[j][1],
                          ylo, yhi)
                if c is not None:
                    casutil.seg(fr, c[0], c[1], c[2], c[3], casui.GREY)
            j += 1
    for p in env:
        casutil.marker(fr, p[0], p[2], casui.RED, 1)
    lines = [_w('family y = ' + caseng.tostr(tree)),
             _w('df/da = ' + caseng.tostr(caseng.simplify(g))),
             _w('envelope: df/da = 0 and y = f(x,a)'),
             _w('a in [' + _fn(alo) + ', ' + _fn(ahi) + ']'),
             _w('------------------')]
    j = 0
    while j < len(env):
        p = env[j]
        j += 1
        if p[3] % ENV_EVERY:
            continue
        lines.append('x=' + _fn(p[0]) + ' a=' + _fn(p[1]) + ' y=' + _fn(p[2]))
    lines.append(_w('------------------'))
    lines.append('envelope points found: ' + str(len(env)))
    lines.append(_w('each one is where the member'))
    lines.append(_w('touches the envelope, so the'))
    lines.append(_w('family only reaches it once.'))
    casutil.chart_hold('members grey, envelope red')
    _pages('Envelope', lines)

def _gev(g, x, a):
    v = caseng.evalf(g, 0.0, False, {'x': x, 'a': a})
    if isinstance(v, complex) or not _finite(v):
        raise ValueError('not a real finite value')
    return v

def _aroots(g, x, alo, ahi):
    vals = []
    i = 0
    while i <= ENV_NA:
        a = alo + (ahi - alo) * i / ENV_NA
        try:
            vals.append(_gev(g, x, a))
        except:
            vals.append(None)
        i += 1
    out = []
    i = 1
    while i <= ENV_NA and len(out) < 3:
        pv = vals[i - 1]
        v = vals[i]
        if pv is None or v is None:
            i += 1
            continue
        if pv == 0.0:
            _addnear(out, alo + (ahi - alo) * (i - 1) / ENV_NA, 1e-6)
        elif (pv < 0) != (v < 0):
            lo = alo + (ahi - alo) * (i - 1) / ENV_NA
            hi = alo + (ahi - alo) * i / ENV_NA
            flo = pv
            j = 0
            while j < 60 and (hi - lo) > 1e-12:
                mid = (lo + hi) / 2.0
                try:
                    fm = _gev(g, x, mid)
                except:
                    break
                if fm == 0.0:
                    lo = mid
                    hi = mid
                    break
                if (fm < 0) == (flo < 0):
                    lo = mid
                    flo = fm
                else:
                    hi = mid
                j += 1
            _addnear(out, _snap((lo + hi) / 2.0), 1e-6)
        i += 1
    if vals[ENV_NA] == 0.0:
        _addnear(out, ahi, 1e-6)
    return out

VDE_X = [-1.3, -0.4, 0.35, 0.9, 1.7]

def t_verifyde():
    y = _askexpr('proposed y, in x')
    if y is None:
        _show('Verify a DE solution', [_warn('Could not read y.')])
        return
    res = _askexpr('DE as expr = 0, y p=dy/dx q=d2y/dx2')
    if res is None:
        _show('Verify a DE solution', [_warn('Could not read the equation.')])
        return
    try:
        d1 = caseng.diff(y, 'x')
        d2 = caseng.diff(d1, 'x')
    except:
        _show('Verify a DE solution', [_warn('Cannot differentiate y.')])
        return
    lines = [_w('y = ' + caseng.tostr(y)),
             _w('dy/dx = ' + caseng.tostr(caseng.simplify(d1))),
             _w('d2y/dx2 = ' + caseng.tostr(caseng.simplify(d2))),
             _w('equation (must be 0):'),
             _w('  ' + caseng.tostr(res)),
             _w('------------------')]
    sym = None
    try:
        s = caseng.subst(res, 'q', d2)
        s = caseng.subst(s, 'p', d1)
        s = caseng.subst(s, 'y', y)
        s = caseng.simplify(s)
        sym = caseng.tostr(s)
        try:
            sym = caseng.tostr(caspoly.collect(s))
        except:
            pass
    except:
        sym = None
    if sym is not None:
        lines.append(_w('after substituting:'))
        lines.append(_w('  ' + sym[:60]))
    worst = 0.0
    tested = 0
    ok = True
    i = 0
    while i < len(VDE_X):
        xv = VDE_X[i]
        i += 1
        try:
            yv = _ev(y, xv)
            pv = _ev(d1, xv)
            qv = _ev(d2, xv)
            rv = caseng.evalf(res, xv, False,
                              {'x': xv, 'y': yv, 'p': pv, 'q': qv})
        except:
            continue
        if not _finite(rv):
            continue
        scale = 1.0 + abs(yv) + abs(pv) + abs(qv)
        rel = abs(rv) / scale
        if rel > worst:
            worst = rel
        tested += 1
    if tested == 0:
        ok = False
    lines.append(_w('------------------'))
    lines.append(_warn('checked at ' + str(tested) + ' values of x'))
    lines.append(_warn('largest relative residual'))
    lines.append(_warn('  = ' + _f6(worst)))
    if ok and worst < 1e-9:
        lines.append('VERIFIED: y satisfies the')
        lines.append('differential equation.')
    elif not ok:
        lines.append(_warn('NOT CHECKED: the equation could'))
        lines.append(_warn('not be evaluated anywhere.'))
    else:
        lines.append(_warn('NOT a solution: the equation'))
        lines.append(_warn('does not balance.'))
    _pages('Verify a DE solution', lines)

def _tterm(v):
    if v == 0:
        return ''
    if v < 0:
        return ' - ' + (str(-v) if v != -1 else '') + 't'
    return ' + ' + (str(v) if v != 1 else '') + 't'

def t_diophantine():
    a = _askint('a in a x + b y = c')
    if a is None:
        return
    b = _askint('b')
    if b is None:
        return
    c = _askint('c')
    if c is None:
        return
    sb = ' + ' + str(b) if b >= 0 else ' - ' + str(-b)
    lines = [_w(str(a) + 'x' + sb + 'y = ' + str(c)),
             _w('------------------')]
    if a == 0 and b == 0:
        if c == 0:
            lines.append('every (x, y) is a solution.')
        else:
            lines.append(_warn('no solutions: 0 = ' + str(c) + ' is false.'))
        _pages('Linear Diophantine', lines)
        return
    g, u, v = _egcd(a, b)
    if g < 0:
        g, u, v = -g, -u, -v
    lines.append(_w('gcd(' + str(a) + ', ' + str(b) + ') = ' + str(g)))
    lines.append(_w('Bezout: ' + str(a) + '*' + str(u) + ' + ' + str(b) + '*' +
                 str(v) + ' = ' + str(g)))
    if c % g != 0:
        lines.append(_warn(str(g) + ' does not divide ' + str(c) + ','))
        lines.append(_warn('so there are NO integer'))
        lines.append(_warn('solutions.'))
        _pages('Linear Diophantine', lines)
        return
    k = c // g
    x0 = u * k
    y0 = v * k
    bg = b // g
    ag = a // g
    lines.append(_w(str(g) + ' divides ' + str(c) + ', so solutions'))
    lines.append(_w('exist. Scaling Bezout by ' + str(k) + ':'))
    lines.append('x0 = ' + str(x0) + ', y0 = ' + str(y0))
    lines.append(_warn('check: ' + str(a * x0 + b * y0) + ' = ' + str(c)))
    lines.append(_w('------------------'))
    lines.append('general solution, t integer:')
    lines.append('x = ' + str(x0) + _tterm(bg))
    lines.append('y = ' + str(y0) + _tterm(-ag))
    if bg != 0:
        t = -x0 // bg
        best = None
        j = -2
        while j <= 2:
            xx = x0 + bg * (t + j)
            yy = y0 - ag * (t + j)
            if xx >= 0 and (best is None or xx < best[0]):
                best = (xx, yy, t + j)
            j += 1
        if best is not None:
            lines.append('smallest x >= 0: t = ' + str(best[2]))
            lines.append('  x = ' + str(best[0]) + ', y = ' + str(best[1]))
    _pages('Linear Diophantine', lines)

TOOLS = [
    ('Plot f(x) curve', t_plot),
    ('De Moivre z^n', t_demoivre),
    ('nth roots of z', t_roots),
    ('Euler dy/dx=f(x)', t_euler),
    ('Runge-Kutta RK2/RK4', t_rk),
    ('Tangent field', t_tangentfield),
    ('Verify a DE solution', t_verifyde),
    ('Limit of f(x)', t_limit),
    ('Asymptotes incl oblique', t_asympt),
    ('Stationary pts & cusps', t_statcusp),
    ('Family of curves', t_family),
    ('Envelope of a family', t_envelope),
    ('Arc length', t_arclen),
    ('gcd & lcm', t_gcdlcm),
    ('Prime test', t_prime),
    ('Prime factorise', t_factor),
    ('Euler totient phi(n)', t_totient),
    ('a^b mod m', t_powmod),
    ('Modular inverse', t_modinv),
    ('Fermat & Wilson', t_fermat),
    ('Pythagorean triples', t_pythag),
    ("Pell x^2-n y^2=1", t_pell),
    ('Linear Diophantine', t_diophantine),
    ('Base -> bin/hex', t_base),
]

def run():
    casutil.run_tools('Further Pure w/ Tech', TOOLS)
