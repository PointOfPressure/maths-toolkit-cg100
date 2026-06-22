import math
import casui
import caslex
import caseng

PI = math.pi
TWO_PI = 2.0 * math.pi


def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return _realf(caseng.evalf(t, 0.0))
    except:
        return None


def _fn(x):
    if x != x:
        return 'nan'
    if x > 1e308 or x < -1e308:
        if x > 0:
            return 'inf'
        return '-inf'
    r = round(x, 4)
    if r == int(r):
        return str(int(r))
    return str(r)


def _realf(v):
    if isinstance(v, complex):
        if v.imag != 0:
            return None
        return v.real
    return v


def _atan2(y, x):
    if x > 0:
        return math.atan(y / x)
    if x < 0:
        if y >= 0:
            return math.atan(y / x) + PI
        return math.atan(y / x) - PI
    if y > 0:
        return PI / 2.0
    if y < 0:
        return -PI / 2.0
    return 0.0


def _show(title, lines):
    casui.result_screen(title, lines)


def _askexpr(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    return caslex.parse(s)


def _line(x0, y0, x1, y1, col):
    dx = x1 - x0
    if dx < 0:
        dx = -dx
    dy = y1 - y0
    if dy < 0:
        dy = -dy
    sx = 1
    if x0 > x1:
        sx = -1
    sy = 1
    if y0 > y1:
        sy = -1
    err = dx - dy
    while True:
        if 0 <= x0 <= 383 and 0 <= y0 <= 191:
            casui.set_pixel(x0, y0, col)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err = err - dy
            x0 = x0 + sx
        if e2 < dx:
            err = err + dx
            y0 = y0 + sy


def t_topolar_xy():
    r = _asknum('r =')
    if r is None:
        return
    th = _asknum('theta (rad) =')
    if th is None:
        return
    x = r * math.cos(th)
    y = r * math.sin(th)
    _show('(r,theta) -> (x,y)', ['r = ' + _fn(r) + ', th = ' + _fn(th), 'x = ' + _fn(x), 'y = ' + _fn(y)])


def t_topolar_rt():
    x = _asknum('x =')
    if x is None:
        return
    y = _asknum('y =')
    if y is None:
        return
    r = math.sqrt(x * x + y * y)
    th = _atan2(y, x)
    deg = th * 180.0 / PI
    _show('(x,y) -> (r,theta)', ['x = ' + _fn(x) + ', y = ' + _fn(y), 'r = ' + _fn(r), 'theta = ' + _fn(th) + ' rad', '      = ' + _fn(deg) + ' deg'])


def _plot_tree(tree, title):
    n = 120
    xs = []
    ys = []
    step = TWO_PI / n
    i = 0
    while i <= n:
        th = step * i
        try:
            r = _realf(caseng.evalf(tree, th))
        except:
            r = None
        if r is not None:
            xs.append(r * math.cos(th))
            ys.append(r * math.sin(th))
        else:
            xs.append(None)
            ys.append(None)
        i += 1
    minx = None
    maxx = None
    miny = None
    maxy = None
    j = 0
    while j < len(xs):
        if xs[j] is not None:
            if minx is None or xs[j] < minx:
                minx = xs[j]
            if maxx is None or xs[j] > maxx:
                maxx = xs[j]
            if miny is None or ys[j] < miny:
                miny = ys[j]
            if maxy is None or ys[j] > maxy:
                maxy = ys[j]
        j += 1
    if minx is None:
        _show(title, ['No points to plot'])
        return
    if minx > 0:
        minx = 0.0
    if maxx < 0:
        maxx = 0.0
    if miny > 0:
        miny = 0.0
    if maxy < 0:
        maxy = 0.0
    spanx = maxx - minx
    spany = maxy - miny
    if spanx <= 0:
        spanx = 1.0
    if spany <= 0:
        spany = 1.0
    sx = 366.0 / spanx
    sy = 172.0 / spany
    sc = sx
    if sy < sc:
        sc = sy
    ox = 12 + (-minx) * sc + (366.0 - spanx * sc) / 2.0
    oy = 16 + (maxy) * sc + (172.0 - spany * sc) / 2.0
    casui.clear_screen()
    casui.draw_string(6, 4, title, casui.ACC, 'small')
    ay = int(round(oy))
    ax = int(round(ox))
    if 0 <= ay <= 191:
        casui.hline(0, 383, ay, casui.GREY)
    if 0 <= ax <= 383:
        k = 0
        while k <= 191:
            casui.set_pixel(ax, k, casui.GREY)
            k += 1
    m = 0
    px0 = None
    py0 = None
    while m < len(xs):
        if xs[m] is None:
            px0 = None
            py0 = None
            m += 1
            continue
        px = int(round(ox + xs[m] * sc))
        py = int(round(oy - ys[m] * sc))
        if px0 is not None:
            _line(px0, py0, px, py, casui.ACC)
        else:
            if 0 <= px <= 383 and 0 <= py <= 191:
                casui.set_pixel(px, py, casui.ACC)
        px0 = px
        py0 = py
        m += 1
    casui.show_screen()
    casui.wait_release()
    casui.wait_press()
    casui.wait_release()


def t_plot():
    tree = _askexpr('r(theta), use x=theta:')
    if tree is None:
        return
    _plot_tree(tree, 'r = ' + caseng.tostr(tree))


def t_preset():
    presets = [('Cardioid 1+cos', '1+cos(x)'), ('Rose cos(2x)', 'cos(2*x)'), ('Circle r=3', '3')]
    labels = [p[0] for p in presets]
    c = casui.menu('PRESET CURVES', labels)
    if c == -1:
        return
    tree = caslex.parse(presets[c][1])
    if tree is None:
        _show('PRESET', ['Parse failed'])
        return
    _plot_tree(tree, 'r = ' + presets[c][1])


def t_area():
    tree = _askexpr('r(theta), use x=theta:')
    if tree is None:
        return
    a = _asknum('lower limit a =')
    if a is None:
        return
    b = _asknum('upper limit b =')
    if b is None:
        return
    if a == b:
        _show('POLAR AREA', ['a equals b', 'Area = 0'])
        return
    n = 100
    h = (b - a) / n
    total = 0.0
    i = 0
    while i <= n:
        th = a + h * i
        try:
            r = _realf(caseng.evalf(tree, th))
        except:
            r = None
        if r is None:
            _show('POLAR AREA', ['Eval error at theta=' + _fn(th)])
            return
        f = r * r
        if i == 0 or i == n:
            w = 1.0
        elif i % 2 == 1:
            w = 4.0
        else:
            w = 2.0
        total = total + w * f
        i += 1
    integ = total * h / 3.0
    area = 0.5 * integ
    if area < 0:
        area = -area
    _show('POLAR AREA', ['A = 0.5 integ r^2 dtheta', 'a = ' + _fn(a) + ', b = ' + _fn(b), 'integ r^2 = ' + _fn(integ), 'Area = ' + _fn(area)])


TOOLS = [('(r,theta) -> (x,y)', t_topolar_xy), ('(x,y) -> (r,theta)', t_topolar_rt), ('Plot polar curve', t_plot), ('Preset curves', t_preset), ('Polar area', t_area)]


def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('POLAR COORDINATES', labels)
        if c == -1:
            return
        TOOLS[c][1]()