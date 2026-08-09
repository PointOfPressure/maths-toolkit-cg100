from casioplot import *

COLOR = (20, 20, 25)

ASC  = {'large': 18, 'medium': 13, 'small': 8}
DESC = {'large': 5, 'medium': 4, 'small': 2}
EM   = {'large': 18, 'medium': 17, 'small': 10}
AXIS = {'large': 5, 'medium': 4, 'small': 3}

_WIDE = "mwMW@%"
_NARROW = " iIjl1tfr.,;:!'|()[]{}/-"

def cw(ch, size):
    if size == 'small':
        if ch in _WIDE:
            return 8
        if ch in _NARROW:
            return 5
        return 7
    if size == 'large':
        if ch in _WIDE:
            return 21
        if ch in _NARROW:
            return 14
        return 18
    if ch in _WIDE:
        return 12
    if ch in _NARROW:
        return 8
    return 10

def strw(s, size):
    w = 0
    for ch in s:
        w += cw(ch, size)
    return w

def numstr(v):
    if isinstance(v, int):
        return str(v)
    if v != v:
        return "undefined"
    if v > 1.7e308:
        return "inf"
    if v < -1.7e308:
        return "-inf"
    r = round(v, 6)
    if r == int(r):
        return str(int(r))
    return str(r)

def fsize(lvl):
    return 'medium' if lvl <= 0 else 'small'

def prec(n):
    t = n[0]
    if t in ('+', '-', 'neg'):
        return 1
    if t == '*':
        return 2
    if t == '^':
        return 4
    return 5

def starts_num(n):
    t = n[0]
    if t == 'n':
        return True
    if t == '^' or t == '*':
        return starts_num(n[1])
    return False

def build(n, lvl):
    t = n[0]
    sz = fsize(lvl)
    if t == 'n':
        return ('atom', numstr(n[1]), sz)
    if t == 'v':
        return ('atom', n[1], sz)
    if t in ('sin', 'cos', 'tan', 'ln', 'log', 'asin', 'acos', 'atan',
             'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh', 'abs'):
        return ('row', [('atom', t, sz), ('paren', build(n[1], lvl), sz)])
    if t == 'exp':
        return ('sup', ('atom', 'e', sz), build(n[1], lvl + 1), sz)
    if t == 'sqrt':
        return ('root', build(n[1], lvl), sz)
    if t == 'fact':
        cb = build(n[1], lvl)
        if n[1][0] in ('+', '-', '*', '/', 'neg', '^'):
            cb = ('paren', cb, sz)
        return ('row', [cb, ('atom', '!', sz)])
    if t in ('ncr', 'npr', 'logb'):
        nm = 'nCr' if t == 'ncr' else ('nPr' if t == 'npr' else 'logb')
        inner = ('row', [build(n[1], lvl), ('atom', ',', sz), build(n[2], lvl)])
        return ('row', [('atom', nm, sz), ('paren', inner, sz)])
    if t == 'neg':
        cb = build(n[1], lvl)
        if n[1][0] in ('+', '-'):
            cb = ('paren', cb, sz)
        return ('row', [('atom', '-', sz), cb])
    if t == '^':
        bb = build(n[1], lvl)
        if n[1][0] in ('+', '-', '*', '/', 'neg', '^') or (n[1][0] == 'n' and n[1][1] < 0):
            bb = ('paren', bb, sz)
        return ('sup', bb, build(n[2], lvl + 1), sz)
    if t == '/':
        return ('frac', build(n[1], lvl), build(n[2], lvl), sz)
    if t == '*':
        a = n[1]; b = n[2]
        ab = build(a, lvl)
        if prec(a) < 2:
            ab = ('paren', ab, sz)
        bb = build(b, lvl)
        if prec(b) < 2:
            bb = ('paren', bb, sz)
        if a[0] == 'n' and starts_num(b):
            return ('row', [ab, ('dot', sz), bb])
        return ('row', [ab, bb])
    if t == '+':
        a = n[1]; b = n[2]
        ab = build(a, lvl)
        if b[0] == 'neg':
            ib = build(b[1], lvl)
            if b[1][0] in ('+', '-'):
                ib = ('paren', ib, sz)
            return ('row', [ab, ('atom', ' - ', sz), ib])
        if b[0] == 'n' and b[1] < 0:
            return ('row', [ab, ('atom', ' - ', sz), ('atom', numstr(-b[1]), sz)])
        return ('row', [ab, ('atom', ' + ', sz), build(b, lvl)])
    if t == '-':
        a = n[1]; b = n[2]
        ab = build(a, lvl)
        if b[0] == 'neg':
            ib = build(b[1], lvl)
            if b[1][0] in ('+', '-'):
                ib = ('paren', ib, sz)
            return ('row', [ab, ('atom', ' + ', sz), ib])
        if b[0] == 'n' and b[1] < 0:
            return ('row', [ab, ('atom', ' + ', sz), ('atom', numstr(-b[1]), sz)])
        bb = build(b, lvl)
        if b[0] in ('+', '-'):
            bb = ('paren', bb, sz)
        return ('row', [ab, ('atom', ' - ', sz), bb])
    return ('atom', '?', sz)

_MCACHE = {}

def measure(b):
    key = id(b)
    v = _MCACHE.get(key)
    if v is None:
        v = _measure(b)
        _MCACHE[key] = v
    return v

def _measure(b):
    k = b[0]
    if k == 'atom':
        return (strw(b[1], b[2]), ASC[b[2]], DESC[b[2]])
    if k == 'dot':
        return (8, ASC[b[1]], DESC[b[1]])
    if k == 'row':
        w = 0; a = 0; d = 0
        for ch in b[1]:
            cwd, ca, cd = measure(ch)
            w += cwd
            if ca > a: a = ca
            if cd > d: d = cd
        return (w, a, d)
    if k == 'frac':
        sz = b[3]
        nw, na, nd = measure(b[1])
        dw, da, dd = measure(b[2])
        width = (nw if nw > dw else dw) + 4
        axis = AXIS[sz]
        asc = axis + 1 + 2 + na + nd
        desc = da + dd + 2 + 1 - axis
        if desc < DESC[sz]:
            desc = DESC[sz]
        return (width, asc, desc)
    if k == 'sup':
        sz = b[3]
        bw, ba, bd = measure(b[1])
        ew, ea, ed = measure(b[2])
        shift = EM[sz] * 45 // 100
        asc = ba
        if shift + ea > asc:
            asc = shift + ea
        return (bw + 1 + ew, asc, bd)
    if k == 'root':
        sz = b[2]
        rw, ra, rd = measure(b[1])
        surd = (ra + rd) * 6 // 10 + 5
        return (surd + rw + 2, ra + 2 + 1 + 1, rd)
    if k == 'paren':
        sz = b[2]
        cwd, ca, cd = measure(b[1])
        if ca + cd <= ASC[sz] + DESC[sz] + 2:
            return (cwd + 2 * strw('(', sz), ca if ca > ASC[sz] else ASC[sz], cd if cd > DESC[sz] else DESC[sz])
        return (cwd + 2 * 4 + 2, ca + 1, cd + 1)
    return (0, 0, 0)

def hline(x0, x1, y):
    sp = set_pixel
    x = x0
    while x <= x1:
        sp(x, y, COLOR)
        x += 1

def vline(x, y0, y1):
    sp = set_pixel
    y = y0
    while y <= y1:
        sp(x, y, COLOR)
        y += 1

def drawline(x0, y0, x1, y1):
    sp = set_pixel
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        sp(x0, y0, COLOR)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy

def draw(b, x, base):
    k = b[0]
    if k == 'atom':
        draw_string(x, base - ASC[b[2]], b[1], COLOR, b[2])
        return
    if k == 'dot':
        sz = b[1]
        cy = base - EM[sz] // 3
        set_pixel(x + 3, cy, COLOR); set_pixel(x + 4, cy, COLOR)
        set_pixel(x + 3, cy + 1, COLOR); set_pixel(x + 4, cy + 1, COLOR)
        return
    if k == 'row':
        cx = x
        for ch in b[1]:
            cwd, ca, cd = measure(ch)
            draw(ch, cx, base)
            cx += cwd
        return
    if k == 'frac':
        sz = b[3]
        nw, na, nd = measure(b[1])
        dw, da, dd = measure(b[2])
        width = (nw if nw > dw else dw) + 4
        axis = AXIS[sz]
        ybar = base - axis
        hline(x, x + width - 1, ybar)
        nx = x + (width - nw) // 2
        draw(b[1], nx, ybar - 2 - nd)
        dx = x + (width - dw) // 2
        draw(b[2], dx, ybar + 2 + da)
        return
    if k == 'sup':
        sz = b[3]
        bw, ba, bd = measure(b[1])
        shift = EM[sz] * 45 // 100
        draw(b[1], x, base)
        draw(b[2], x + bw + 1, base - shift)
        return
    if k == 'root':
        sz = b[2]
        rw, ra, rd = measure(b[1])
        surd = (ra + rd) * 6 // 10 + 5
        top = base - (ra + 2)
        bottom = base + rd
        rx = x + surd
        draw(b[1], rx + 1, base)
        hline(rx, x + surd + rw + 1, top)
        valx = x + surd * 45 // 100
        drawline(x + surd * 15 // 100, top + (bottom - top) // 2, valx, bottom)
        drawline(valx, bottom, rx, top)
        return
    if k == 'paren':
        sz = b[2]
        cwd, ca, cd = measure(b[1])
        if ca + cd <= ASC[sz] + DESC[sz] + 2:
            pwl = strw('(', sz)
            draw_string(x, base - ASC[sz], '(', COLOR, sz)
            draw(b[1], x + pwl, base)
            draw_string(x + pwl + cwd, base - ASC[sz], ')', COLOR, sz)
            return
        top = base - (ca + 1)
        bot = base + (cd + 1)
        rcol = x + cwd + 2 * 4 + 1
        vline(x, top + 2, bot - 2)
        set_pixel(x + 1, top + 1, COLOR); set_pixel(x + 2, top, COLOR)
        set_pixel(x + 1, bot - 1, COLOR); set_pixel(x + 2, bot, COLOR)
        draw(b[1], x + 4 + 1, base)
        vline(rcol, top + 2, bot - 2)
        set_pixel(rcol - 1, top + 1, COLOR); set_pixel(rcol - 2, top, COLOR)
        set_pixel(rcol - 1, bot - 1, COLOR); set_pixel(rcol - 2, bot, COLOR)
        return

def render(node, x0, y0, x1, y1, color):
    global COLOR
    COLOR = color
    box = None
    w = a = d = 0
    for lvl in (0, 1):
        _MCACHE.clear()
        box = build(node, lvl)
        w, a, d = measure(box)
        if w <= (x1 - x0) and (a + d) <= (y1 - y0):
            x = x0 + ((x1 - x0) - w) // 2
            cy = (y0 + y1) // 2
            draw(box, x, cy + (a - d) // 2)
            _MCACHE.clear()
            return True
    _MCACHE.clear()
    return False
