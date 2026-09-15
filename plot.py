# Curve / point / bar plotter with pan, zoom and trace. One screen, no fills.
from casioplot import *
import math
import casui
import casutil

W = 384
TOP = 14
BOT = 176
COLS = [(40, 120, 220), (205, 60, 60), (30, 150, 60), (150, 60, 200)]
GREY = (120, 120, 120)
BLACK = (0, 0, 0)

def _line(x0, y0, x1, y1, c):
    dx = x1 - x0 if x1 >= x0 else x0 - x1
    dy = y1 - y0 if y1 >= y0 else y0 - y1
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    err = dx - dy
    sp = set_pixel
    while True:
        if 0 <= x0 < W and TOP <= y0 <= BOT:
            sp(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def _mark(x, y, c):
    sp = set_pixel
    for d in (-2, -1, 0, 1, 2):
        if TOP <= y <= BOT and 0 <= x + d < W:
            sp(x + d, y, c)
        if TOP <= y + d <= BOT and 0 <= x < W:
            sp(x, y + d, c)

def _px(st, x):
    return int((x - st[0]) / (st[1] - st[0]) * (W - 1) + 0.5)

def _py(st, y):
    return int(BOT - (y - st[2]) / (st[3] - st[2]) * (BOT - TOP) + 0.5)

def _samples(curves, kind, st):
    # -> list of point lists in world coords; None marks a break
    out = []
    if kind == 'y':
        for tree in curves:
            pts = []
            px = 0
            while px < W:
                x = st[0] + (st[1] - st[0]) * px / (W - 1.0)
                y = casutil.evx(tree, x)
                pts.append(None if y is None else (x, y))
                px += 1
            out.append(pts)
    elif kind == 'polar':
        for tree in curves:
            pts = []
            i = 0
            while i <= 360:
                th = 2.0 * math.pi * i / 360.0
                r = casutil.evx(tree, th)
                pts.append(None if r is None else (r * math.cos(th), r * math.sin(th), th))
                i += 1
            out.append(pts)
    elif kind == 'param':
        for xt, yt, tlo, thi in curves:
            pts = []
            i = 0
            while i <= 240:
                t = tlo + (thi - tlo) * i / 240.0
                x = casutil.evx(xt, t)
                y = casutil.evx(yt, t)
                pts.append(None if (x is None or y is None) else (x, y, t))
                i += 1
            out.append(pts)
    elif kind == 'points':
        out.append([(p[0], p[1]) for p in curves])
    elif kind == 'bars':
        out.append([(b[0], 0.0) for b in curves] + [(b[1], b[2]) for b in curves])
    return out

def _yrange(samps, kind):
    ys = []
    xs = []
    for pts in samps:
        for p in pts:
            if p is not None:
                xs.append(p[0])
                ys.append(p[1])
    if not ys:
        return None
    if kind == 'y':
        ys.sort()
        n = len(ys)
        lo = ys[n // 20]
        hi = ys[n - 1 - n // 20]
        if hi - lo < 1e-9:
            lo -= 1.0
            hi += 1.0
        pad = (hi - lo) * 0.08
        return (None, None, lo - pad, hi + pad)
    xlo, xhi = casutil.nice_range(xs, 0.1, kind == 'bars')
    ylo, yhi = casutil.nice_range(ys, 0.1, kind == 'bars')
    if kind != 'bars':
        # equal scale so circles look round: 384 px wide, 162 px tall
        ux = (xhi - xlo) / (W - 1.0)
        uy = (yhi - ylo) / (BOT - TOP)
        u = ux if ux > uy else uy
        cx = (xlo + xhi) / 2.0
        cy = (ylo + yhi) / 2.0
        xlo = cx - u * (W - 1) / 2.0
        xhi = cx + u * (W - 1) / 2.0
        ylo = cy - u * (BOT - TOP) / 2.0
        yhi = cy + u * (BOT - TOP) / 2.0
    return (xlo, xhi, ylo, yhi)

def _axes(st):
    if st[2] <= 0.0 <= st[3]:
        y0 = _py(st, 0.0)
        x = 0
        while x < W:
            set_pixel(x, y0, GREY)
            x += 1
    if st[0] <= 0.0 <= st[1]:
        x0 = _px(st, 0.0)
        y = TOP
        while y <= BOT:
            set_pixel(x0, y, GREY)
            y += 1
    f = casutil.sf3
    draw_string(2, BOT - 11, f(st[0]), GREY, 'small')
    s = f(st[1])
    draw_string(W - 2 - casui.text_w(s, 'small'), BOT - 11, s, GREY, 'small')
    draw_string(2, TOP + 1, f(st[3]), GREY, 'small')
    draw_string(2, BOT - 22, f(st[2]), GREY, 'small')

def _draw_curve(pts, st, c, kind):
    prev = None
    for p in pts:
        if p is None:
            prev = None
            continue
        x = _px(st, p[0])
        y = _py(st, p[1])
        if kind == 'points':
            _mark(x, y, c)
            continue
        if prev is not None and abs(y - prev[1]) < 400:
            _line(prev[0], prev[1], x, y, c)
        elif kind != 'y' or prev is None:
            if TOP <= y <= BOT and 0 <= x < W:
                set_pixel(x, y, c)
        prev = (x, y)

def _draw_bars(curves, st, c):
    for xlo, xhi, h in curves:
        x0 = _px(st, xlo)
        x1 = _px(st, xhi)
        y0 = _py(st, 0.0)
        y1 = _py(st, h)
        _line(x0, y0, x0, y1, c)
        _line(x1, y0, x1, y1, c)
        _line(x0, y1, x1, y1, c)
        _line(x0, y0, x1, y0, GREY)

def run(curves, xlo=-6.0, xhi=6.0, kind='y', title='', ylo=None, yhi=None):
    if not curves:
        return
    auto = (ylo is None)
    st = [float(xlo), float(xhi), ylo, yhi]
    trace = False
    ti = 0
    tc = 0
    while True:
        samps = _samples(curves, kind, st)
        if auto:
            r = _yrange(samps, kind)
            if r is None:
                casui.flash('nothing to plot')
                return
            if kind != 'y':
                st[0], st[1] = r[0], r[1]
            st[2], st[3] = r[2], r[3]
        clear_screen()
        _axes(st)
        if kind == 'bars':
            _draw_bars(curves, st, COLS[0])
        else:
            i = 0
            for pts in samps:
                _draw_curve(pts, st, COLS[i % len(COLS)], kind)
                i += 1
        hint = 'arrows pan  +/- zoom  OK trace  0 reset'
        head = title
        if trace:
            pts = samps[tc % len(samps)]
            if ti >= len(pts):
                ti = len(pts) - 1
            if ti < 0:
                ti = 0
            p = pts[ti]
            if p is None:
                head = 'undefined here'
            else:
                _mark(_px(st, p[0]), _py(st, p[1]), BLACK)
                head = 'x=' + casutil.sf3(p[0]) + '  y=' + casutil.sf3(p[1])
                if len(p) > 2:
                    head = ('t=' if kind == 'param' else 'th=') + casutil.sf3(p[2]) + '  ' + head
            hint = 'left/right move  up/down curve  OK stop'
        draw_string(2, 1, head, BLACK if trace else GREY, 'small')
        draw_string(2, 180, hint, GREY, 'small')
        show_screen()
        casui.wait_release()
        k = casui.wait_key()
        span = st[1] - st[0]
        if k == casui.EXITK:
            return
        if k == casui.OK or k == casui.EXE:
            trace = not trace
            if trace:
                ti = len(samps[0]) // 2
        elif trace:
            step = len(samps[tc % len(samps)]) // 60 + 1
            if k == casui.LEFT:
                ti -= step
            elif k == casui.RIGHT:
                ti += step
            elif k == casui.UP or k == casui.DOWN:
                tc += 1
        elif k == casui.LEFT or k == casui.RIGHT:
            d = span / 4 if k == casui.RIGHT else -span / 4
            st[0] += d
            st[1] += d
            if kind != 'y':
                auto = False
        elif k == casui.UP or k == casui.DOWN:
            d = (st[3] - st[2]) / 4
            if k == casui.DOWN:
                d = -d
            st[2] += d
            st[3] += d
            auto = False
        elif k == casui.PLUS or k == casui.MINUS:
            f = 0.25 if k == casui.PLUS else 1.0
            cx = (st[0] + st[1]) / 2
            st[0] = cx - span * f
            st[1] = cx + span * f
            if kind != 'y' or not auto:
                cy = (st[2] + st[3]) / 2
                sy = st[3] - st[2]
                st[2] = cy - sy * f
                st[3] = cy + sy * f
                auto = False
        elif k == casui.ZERO:
            st = [float(xlo), float(xhi), ylo, yhi]
            auto = (ylo is None)
