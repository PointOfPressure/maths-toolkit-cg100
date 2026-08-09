# fpt.py - Further Pure with Technology (OCR B MEI Y436) section for the
# fx-CG100 maths toolkit. Curve plotter, complex investigation (De Moivre,
# nth roots), Euler numeric exploration, and an integer number-theory pack.
# Stock CASIO MicroPython 1.9.4: ASCII only, no f-strings, iterative only.
import math
import casui
import caseng
import casutil

def _finite(v):
    # True if v is a real finite float (no math.isfinite in this build)
    return v == v and v not in (float('inf'), float('-inf'))

_asknum = casutil.asknum
_askint = casutil.askint
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now
_atan2 = casutil.atan2
_gcd = casutil.gcd
_powmod = casutil.powmod

def _f8(x):
    # the point of RK4 is the digits Euler gets wrong, so the comparison
    # tables need more than the shared 4 d.p. default
    return casutil.fmt(x, 8)

def _fc(z):
    return casutil.fmtc(z.real, z.imag)

# ---- 1. CURVE-FAMILY PLOTTER ---------------------------------------------
def _line(x0, y0, x1, y1):
    # integer Bresenham, RED curve colour
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
        _show('Plot f(x)', ['Could not read f(x).'])
        return
    xlo = _asknum('x min (e.g. -5)')
    if xlo is None:
        return
    xhi = _asknum('x max (e.g. 5)')
    if xhi is None or xhi <= xlo:
        _show('Plot f(x)', ['Need x max > x min.'])
        return
    # sample for auto-scale on y
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
        _show('Plot f(x)', ['No finite values', 'in that range.'])
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

    # axes
    if xlo <= 0 <= xhi:
        ax = sx(0.0)
        yy = py0
        while yy <= py1:
            casui.set_pixel(ax, yy, casui.GREY)
            yy += 1
    if ylo <= 0 <= yhi:
        ay = sy(0.0)
        casui.hline(px0, px1, ay, casui.GREY)
    # curve: join consecutive finite samples
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

# ---- 2. COMPLEX: DE MOIVRE z^n -------------------------------------------
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
        _show('z^n  (De Moivre)', ['z = 0 with n <= 0', 'is undefined.'])
        return
    th = _atan2(z.imag, z.real)
    # De Moivre directly (avoids complex ** quirks): r^n (cos n.th + i sin n.th)
    rn = r ** n
    nth = n * th
    w = complex(rn * math.cos(nth), rn * math.sin(nth))
    _show('z^n  (De Moivre)', ['z = ' + _fc(z),
                               '|z|=' + _fn(r) + ' arg=' + _fn(th) + 'r',
                               'n = ' + str(n),
                               '|z|^n = ' + _fn(rn),
                               'n*arg = ' + _fn(nth) + ' rad',
                               'z^n = ' + _fc(w)])

# ---- 3. COMPLEX: nth ROOTS -----------------------------------------------
def t_roots():
    a = _asknum('Re(z)')
    if a is None:
        return
    b = _asknum('Im(z)')
    if b is None:
        return
    n = _askint('n (number of roots)')
    if n is None or n < 1:
        _show('nth roots', ['n must be >= 1.'])
        return
    z = complex(a, b)
    r = abs(z)
    th = _atan2(z.imag, z.real)
    rr = r ** (1.0 / n)
    lines = ['z = ' + _fc(z), 'each |root| = ' + _fn(rr), 'arg step = 2pi/' + str(n)]
    k = 0
    while k < n:
        ang = (th + 2 * math.pi * k) / n
        w = complex(rr * math.cos(ang), rr * math.sin(ang))
        lines.append('w' + str(k) + ' = ' + _fc(w))
        k += 1
    _pages('nth roots of z', lines)

# ---- 4. EULER NUMERIC EXPLORATION dy/dx=f(x) -----------------------------
def t_euler():
    tree = _askexpr('dy/dx = f(x,y)')
    if tree is None:
        _show('Euler', ['Could not read f(x).'])
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
    lines = ['y_n+1 = y_n + h.f(x_n,y_n)', '------------------', 'x      y']
    x = x0
    y = y0
    lines.append(_fn(x) + '   ' + _fn(y))
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
        lines.append(_fn(x) + '   ' + _fn(y))
        i += 1
    _pages('Euler method', lines)

# ---- 4b. RUNGE-KUTTA (c9, c10) -------------------------------------------
# Euler takes the slope at the left-hand end and believes it for the whole
# step. Runge-Kutta samples the slope more than once inside the step and takes
# a weighted mean, which is why the same h gives a far better answer.
def _slope(tree, x, y):
    v = caseng.evalf(tree, x, False, {'y': y})
    if not _finite(v):
        raise ValueError('slope not finite')
    return v

def _st_euler(tree, x, y, h):
    return y + h * _slope(tree, x, y)

def _st_rk2(tree, x, y, h):
    # midpoint method (RK2): one probe at the middle of the step
    k1 = _slope(tree, x, y)
    k2 = _slope(tree, x + h / 2.0, y + h * k1 / 2.0)
    return y + h * k2

def _st_rk4(tree, x, y, h):
    # classical RK4: two probes at the middle, one at the far end
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
        _show('Runge-Kutta', ['Could not read f(x,y).'])
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
    lines = ['k1 = f(x, y)',
             'k2 = f(x+h/2, y+h.k1/2)',
             'k3 = f(x+h/2, y+h.k2/2)',
             'k4 = f(x+h, y+h.k3)',
             'Euler: y + h.k1',
             'RK2 (midpoint): y + h.k2',
             'RK4: y + h(k1+2k2+2k3+k4)/6',
             '------------------',
             'x   Euler / RK2 / RK4']
    x = x0
    ye = y0
    y2 = y0
    y4 = y0
    lines.append(_fn(x) + '  ' + _f8(ye))
    ok = True
    i = 0
    while i < n:
        try:
            ye = _st_euler(tree, x, ye, h)
            y2 = _st_rk2(tree, x, y2, h)
            y4 = _st_rk4(tree, x, y4, h)
        except:
            lines.append('eval error at x=' + _fn(x))
            ok = False
            break
        x = x + h
        lines.append(_fn(x) + '  ' + _f8(ye))
        lines.append('    ' + _f8(y2) + ' / ' + _f8(y4))
        i += 1
    if not ok:
        _pages('Runge-Kutta', lines)
        return
    lines.append('------------------')
    lines.append('at x = ' + _fn(x))
    lines.append('Euler y = ' + _f8(ye))
    lines.append('RK2 y = ' + _f8(y2))
    lines.append('RK4 y = ' + _f8(y4))
    lines.append('RK4 - Euler = ' + _f8(y4 - ye))
    lines.append('RK4 - RK2 = ' + _f8(y4 - y2))
    # c8: the same interval, walked with a smaller step each time
    lines.append('-- same interval, smaller h --')
    hh = h
    nn = n
    j = 0
    while j < 3:
        try:
            e = _march(tree, x0, y0, hh, nn, _st_euler)
            r = _march(tree, x0, y0, hh, nn, _st_rk4)
        except:
            break
        lines.append('h=' + _fn(hh) + ' Euler=' + _f8(e))
        lines.append('        RK4=' + _f8(r))
        hh = hh / 2.0
        nn = nn * 2
        j += 1
    lines.append('halving h divides the Euler')
    lines.append('error by about 2 and the RK4')
    lines.append('error by about 16: Euler is')
    lines.append('first order, RK4 is fourth.')
    _pages('Runge-Kutta', lines)

# ---- 4c. ARC LENGTH (C8) --------------------------------------------------
def _simp(fn, a, b, n):
    # composite Simpson on an even number of panels
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
            _show('Arc length', ['Could not read f(x).'])
            return
        try:
            d = caseng.diff(tree, 'x')
        except:
            _show('Arc length', ['Cannot differentiate.'])
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

        head = ['s = integ sqrt(1 + (dy/dx)^2) dx',
                'dy/dx = ' + caseng.tostr(caseng.simplify(d))]
    elif c == 1:
        tree = _askexpr('r(theta), use x=theta:')
        if tree is None:
            _show('Arc length', ['Could not read r.'])
            return
        try:
            d = caseng.diff(tree, 'x')
        except:
            _show('Arc length', ['Cannot differentiate.'])
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

        head = ['s = integ sqrt(r^2 + (dr/dth)^2) dth',
                'dr/dth = ' + caseng.tostr(caseng.simplify(d))]
    else:
        xt = _askexpr('x(t), in t:')
        if xt is None:
            _show('Arc length', ['Could not read x(t).'])
            return
        yt = _askexpr('y(t), in t:')
        if yt is None:
            _show('Arc length', ['Could not read y(t).'])
            return
        try:
            dx = caseng.diff(xt, 't')
            dy = caseng.diff(yt, 't')
        except:
            _show('Arc length', ['Cannot differentiate.'])
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

        head = ["s = integ sqrt(x'^2 + y'^2) dt",
                "dx/dt = " + caseng.tostr(caseng.simplify(dx)),
                "dy/dt = " + caseng.tostr(caseng.simplify(dy))]
    if b == a:
        _show('Arc length', ['The two limits are equal.'])
        return
    try:
        s = _simp(g, a, b, 400)
        s2 = _simp(g, a, b, 800)
    except:
        _show('Arc length', ['The integrand is not defined',
                             'somewhere in that range.'])
        return
    lines = []
    for t in head:
        lines.append(t)
    lines.append('from ' + _fn(a) + ' to ' + _fn(b))
    lines.append('------------------')
    lines.append('400 panels: s = ' + _f8(s))
    lines.append('800 panels: s = ' + _f8(s2))
    lines.append('arc length = ' + _f8(s2))
    lines.append('change on halving h = ' + _f8(abs(s2 - s)))
    _pages('Arc length', lines)

# ---- 5. NUMBER THEORY PACK -----------------------------------------------
def t_gcdlcm():
    a = _askint('a (integer)')
    if a is None:
        return
    b = _askint('b (integer)')
    if b is None:
        return
    g = _gcd(a, b)
    l = casutil.lcm(a, b)
    _show('gcd & lcm', ['a = ' + str(a), 'b = ' + str(b),
                        'gcd(a,b) = ' + str(g), 'lcm(a,b) = ' + str(l)])

# trial division is O(sqrt n); past this the handheld would appear to hang
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
        _show('Prime test', ['n too large for trial', 'division (max ' + str(NT_MAX) + ').'])
        return
    if _isprime(n):
        msg = str(n) + ' is PRIME.'
    else:
        msg = str(n) + ' is NOT prime.'
    _show('Prime test', [msg, '(trial division', ' up to sqrt n)'])

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
        _show('Factorise', ['Need n >= 2.'])
        return
    if n > NT_MAX:
        _show('Factorise', ['n too large for trial', 'division (max ' + str(NT_MAX) + ').'])
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
    lines = ['n = ' + str(n), '------------------']
    parts = []
    for (p, e) in facs:
        if e == 1:
            parts.append(str(p))
        else:
            parts.append(str(p) + '^' + str(e))
    s = ' * '.join(parts)
    lines.append(s)
    _pages('Prime factors', lines)

def t_powmod():
    a = _askint('base a')
    if a is None:
        return
    b = _askint('exponent b (>=0)')
    if b is None or b < 0:
        _show('a^b mod m', ['Need b >= 0.'])
        return
    m = _askint('modulus m (>=1)')
    if m is None or m < 1:
        _show('a^b mod m', ['Need m >= 1.'])
        return
    r = _powmod(a, b, m)
    _show('a^b mod m', ['a = ' + str(a), 'b = ' + str(b), 'm = ' + str(m),
                        '------------------', 'a^b mod m = ' + str(r)])

def _egcd(a, b):
    # iterative extended Euclid -> (g, x, y) with a*x + b*y = g
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
        _show('mod inverse', ['Need m >= 2.'])
        return
    g, x, y = _egcd(a % m, m)
    if g != 1:
        _show('mod inverse', ['a = ' + str(a) + '  m = ' + str(m),
                              'gcd = ' + str(g) + ' (not 1)',
                              'no inverse exists.'])
        return
    inv = x % m
    _show('mod inverse', ['a = ' + str(a) + '  m = ' + str(m),
                          'a^-1 mod m = ' + str(inv),
                          'check: a*inv mod m',
                          '  = ' + str((a * inv) % m)])

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
    _show('Base convert', ['decimal: ' + str(n), 'binary:  ' + sign + b, 'hex:     ' + sign + h])

# ---- 6. MORE NUMBER THEORY (T5, T6, T7, T8, T9) ---------------------------
def t_totient():
    n = _askint('n >= 1')
    if n is None or n < 1:
        _show('Euler totient', ['Need n >= 1.'])
        return
    if n > NT_MAX:
        _show('Euler totient', ['n too large for trial',
                                'division (max ' + str(NT_MAX) + ').'])
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
    lines = ['n = ' + str(n),
             'phi(n) counts the integers in',
             '1..n that are coprime to n.',
             '------------------']
    if facs:
        lines.append('distinct primes: ' + ' '.join([str(p) for p in facs]))
        prod = 'n'
        for p in facs:
            prod = prod + ' * (1 - 1/' + str(p) + ')'
        lines.append('phi = ' + prod)
    lines.append('phi(n) = ' + str(r))
    if len(facs) == 1 and facs[0] == n:
        lines.append('n is prime, so phi(n) = n-1.')
    lines.append('a^phi(n) = 1 (mod n) when')
    lines.append('gcd(a, n) = 1 (Euler).')
    _pages('Euler totient', lines)

def t_pythag():
    lim = _askint('max hypotenuse c')
    if lim is None or lim < 5:
        _show('Pythagorean triples', ['Need c >= 5.'])
        return
    if lim > 2000:
        lim = 2000
    # Euclid: a = m^2-n^2, b = 2mn, c = m^2+n^2 with m > n > 0, coprime and of
    # opposite parity, generates every primitive triple exactly once
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
    lines = ['primitive triples with c <= ' + str(lim),
             'a^2 + b^2 = c^2',
             '------------------']
    for (c, a, b) in trs:
        lines.append(str(a) + ', ' + str(b) + ', ' + str(c))
    lines.append('count = ' + str(len(trs)))
    lines.append('every other triple is a whole')
    lines.append('multiple of one of these.')
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
        _show("Pell's equation", ['Need n >= 2.'])
        return
    if n > 100000:
        _show("Pell's equation", ['n too large (max 100000).'])
        return
    a0 = _isqrt(n)
    if a0 * a0 == n:
        _show("Pell's equation", [str(n) + ' is a perfect square,',
                                 'so x^2 - n y^2 = 1 has only',
                                 'the trivial solution x=1, y=0.'])
        return
    # fundamental solution from the continued fraction of sqrt(n)
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
        _show("Pell's equation", ['No solution found within',
                                 '4000 continued-fraction steps.'])
        return
    lines = ['x^2 - ' + str(n) + ' y^2 = 1',
             'sqrt(' + str(n) + ') = [' + str(a0) + '; ...]',
             'continued fraction steps: ' + str(steps),
             '------------------',
             'x = ' + str(h),
             'y = ' + str(k),
             'check x^2-n y^2 = ' + str(h * h - n * k * k),
             '------------------',
             'further solutions from',
             '(x + y sqrt n)^j :']
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
        _show('Fermat & Wilson', ['Need p >= 2.'])
        return
    a = _askint('a (base for Fermat)')
    if a is None:
        return
    isp = _isprime(p) if p <= NT_MAX else None
    fl = _powmod(a, p - 1, p)
    lines = ['p = ' + str(p), 'a = ' + str(a)]
    if isp is None:
        lines.append('p too large to test for')
        lines.append('primality here.')
    elif isp:
        lines.append('p is PRIME.')
    else:
        lines.append('p is NOT prime.')
    lines.append('------------------')
    lines.append('Fermat: a^(p-1) = 1 (mod p)')
    lines.append('for prime p not dividing a.')
    lines.append('a^(p-1) mod p = ' + str(fl))
    if _gcd(a, p) != 1:
        lines.append('but gcd(a,p) = ' + str(_gcd(a, p)) +
                     ', so Fermat does not apply.')
    elif fl == 1:
        lines.append('Fermat holds for this a.')
    else:
        lines.append('not 1, so p is COMPOSITE.')
    lines.append('------------------')
    lines.append('Wilson: (p-1)! = -1 (mod p)')
    lines.append('exactly when p is prime.')
    if p > WILSON_MAX:
        lines.append('p above ' + str(WILSON_MAX) + ': the factorial')
        lines.append('loop would be too slow.')
    else:
        # reduced at every step, so no huge integer is ever built and the
        # casutil.fact cap never applies
        w = 1
        i = 2
        while i <= p - 1:
            w = (w * i) % p
            i += 1
        lines.append('(p-1)! mod p = ' + str(w))
        lines.append('-1 mod p = ' + str(p - 1))
        if w == p - 1:
            lines.append('Wilson holds, so p is prime.')
        else:
            lines.append('Wilson fails, so p is not prime.')
    _pages('Fermat & Wilson', lines)

# ---- registry ------------------------------------------------------------
TOOLS = [
    ('Plot f(x) curve', t_plot),
    ('De Moivre z^n', t_demoivre),
    ('nth roots of z', t_roots),
    ('Euler dy/dx=f(x)', t_euler),
    ('Runge-Kutta RK2/RK4', t_rk),
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
    ('Base -> bin/hex', t_base),
]

def run():
    casutil.run_tools('Further Pure w/ Tech', TOOLS)
