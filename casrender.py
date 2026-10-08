from casioplot import *

# Boxes: ('atom', text, size), ('row', [boxes]), ('frac', num, den, size),
# ('sup', base, exp, size), ('sub', base, sub, size), ('ss', base, sub, sup,
# size), ('root', box, size), ('paren', box, size), ('abs', box, size),
# ('bar', box, size), ('hat', box, size), ('g', glyph code, size) (texg.py),
# ('sp', width), ('dot', size), ('mat', [[box]], size). caseng is imported
# only by build(), so notes and plain answers never load the engine.

COLOR = (20, 20, 25)

ASC  = {'large': 18, 'medium': 13, 'small': 8}
DESC = {'large': 5, 'medium': 4, 'small': 2}
EM   = {'large': 18, 'medium': 17, 'small': 10}
AXIS = {'large': 5, 'medium': 4, 'small': 3}

from font import cw, strw

def numstr(v):
    import caseng
    if isinstance(v, int):
        return str(v)
    if isinstance(v, complex):
        return caseng.cstr(v, numstr)
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

_FNPOW = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot',
          'sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth', 'ln', 'log')

def build(n, lvl):
    import caseng
    t = n[0]
    sz = fsize(lvl)
    if t == 'n':
        return ('atom', numstr(n[1]), sz)
    if t == 'v':
        return ('atom', n[1], sz)
    if t == 'abs':
        return ('row', [('atom', '|', sz), build(n[1], lvl), ('atom', '|', sz)])
    if t in caseng.UFUNCS and t != 'exp' and t != 'sqrt':
        return ('row', [('atom', t, sz), ('paren', build(n[1], lvl), sz)])
    if t == 'exp' and n[1] == ('n', 1):
        return ('atom', 'e', sz)
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
    if t == '^' and n[1][0] in _FNPOW:
        # sin(x)^2 typesets as sin^2 x
        arg = n[1][1]
        inner = build(arg, lvl)
        if arg[0] not in ('n', 'v'):
            inner = ('paren', inner, sz)
        return ('row', [('atom', n[1][0], sz),
                        ('sup', ('atom', '', sz), build(n[2], lvl + 1), sz),
                        inner])
    if t == '^':
        bb = build(n[1], lvl)
        if n[1][0] in ('+', '-', '*', '/', 'neg', '^') or (n[1][0] == 'n' and caseng._neg(n[1][1])):
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
        if b[0] == 'n' and caseng._neg(b[1]):
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
        if b[0] == 'n' and caseng._neg(b[1]):
            return ('row', [ab, ('atom', ' + ', sz), ('atom', numstr(-b[1]), sz)])
        bb = build(b, lvl)
        if b[0] in ('+', '-'):
            bb = ('paren', bb, sz)
        return ('row', [ab, ('atom', ' - ', sz), bb])
    return ('atom', '?', sz)

_MCACHE = {}

def measure(b):
    # cached by id (text is cheap to measure again); the entry keeps its box
    # alive so an id is never reused
    if b[0] == 'atom':
        return (strw(b[1], b[2]), ASC[b[2]], DESC[b[2]])
    e = _MCACHE.get(id(b))
    if e is not None and e[0] is b:
        return e[1]
    if len(_MCACHE) > 600:
        _MCACHE.clear()
    v = _measure(b)
    _MCACHE[id(b)] = (b, v)
    return v

SUBD = {'large': 6, 'medium': 4, 'small': 2}     # subscript drop
XH = {'large': 12, 'medium': 9, 'small': 6}      # x-height: a bar over x sits lower than over X
_LOW = 'acegmnopqrsuvwxyz'

def glyph(code, sz):
    import texg
    return (texg.M if sz != 'small' else texg.S)[code]

def _accent(b):
    # height of the accent line over the box: lower over one small letter
    sz = b[2]
    inner = b[1]
    if inner[0] == 'atom' and len(inner[1]) == 1 and inner[1] in _LOW:
        return XH[sz] + 2
    if inner[0] == 'g':
        return glyph(inner[1], inner[2])[1] + 2
    return measure(inner)[1] + 1

def _mat(b):
    # column widths, row ascents and descents of a matrix
    rows = b[1]
    cws = []
    ras = []
    rds = []
    for r in rows:
        a = 0
        d = 0
        j = 0
        for c in r:
            w, ca, cd = measure(c)
            if j >= len(cws):
                cws.append(w)
            elif w > cws[j]:
                cws[j] = w
            if ca > a: a = ca
            if cd > d: d = cd
            j += 1
        ras.append(a)
        rds.append(d)
    return cws, ras, rds

def _measure(b):
    k = b[0]
    if k == 'atom':
        return (strw(b[1], b[2]), ASC[b[2]], DESC[b[2]])
    if k == 'g':
        sz = b[2]
        g = glyph(b[1], sz)
        return (g[0], g[1] if g[1] > ASC[sz] else ASC[sz], g[2] if g[2] > DESC[sz] else DESC[sz])
    if k == 'sp':
        return (b[1], 0, 0)
    if k == 'dot':
        return (8 if b[1] != 'small' else 6, ASC[b[1]], DESC[b[1]])
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
    if k == 'sub' or k == 'ss':
        sz = b[-1]
        bw, ba, bd = measure(b[1])
        sw, sa, sd = measure(b[2])
        drop = SUBD[sz]
        asc = ba
        desc = bd if bd > sd + drop else sd + drop
        if k == 'ss':
            ew, ea, ed = measure(b[3])
            shift = EM[sz] * 45 // 100
            if shift + ea > asc:
                asc = shift + ea
            if ew > sw:
                sw = ew
        return (bw + 1 + sw, asc, desc)
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
    if k == 'abs':
        cwd, ca, cd = measure(b[1])
        return (cwd + 6, ca + 1, cd + 1)
    if k == 'bar' or k == 'hat':
        cwd, ca, cd = measure(b[1])
        top = _accent(b) + (1 if k == 'bar' else 3)
        return (cwd, top if top > ca else ca, cd)
    if k == 'mat':
        cws, ras, rds = _mat(b)
        h = len(ras) * 2 - 2
        for i in range(len(ras)):
            h += ras[i] + rds[i]
        w = 12 + (len(cws) - 1) * (12 if b[2] != 'small' else 8)
        for c in cws:
            w += c
        axis = AXIS[b[2]]
        return (w, axis + h // 2 + 1, h - h // 2 - axis + 1)
    return (0, 0, 0)

# Pixel primitives. While record() runs, OPS is a list and each call is
# kept as an op for play() rather than drawn.
OPS = None

def hline(x0, x1, y):
    if OPS is not None:
        OPS.append((0, x0, x1, y))
        return
    sp = set_pixel
    c = COLOR
    for x in range(x0, x1 + 1):
        sp(x, y, c)

def vline(x, y0, y1):
    if OPS is not None:
        OPS.append((1, x, y0, y1))
        return
    sp = set_pixel
    c = COLOR
    for y in range(y0, y1 + 1):
        sp(x, y, c)

def drawline(x0, y0, x1, y1):
    if OPS is not None:
        OPS.append((2, x0, y0, x1, y1))
        return
    sp = set_pixel
    c = COLOR
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        sp(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy

def gly(code, sz, x, base):
    if OPS is not None:
        OPS.append((3, code, sz, x, base))
        return
    p = glyph(code, sz)[3]
    sp = set_pixel
    c = COLOR
    base -= 32
    for i in range(0, len(p), 2):
        sp(x + p[i], base + p[i + 1], c)

def pix(pts):
    # single pixels: x, y, x, y...
    if OPS is not None:
        OPS.append((4, pts))
        return
    sp = set_pixel
    c = COLOR
    for i in range(0, len(pts), 2):
        sp(pts[i], pts[i + 1], c)

def draw(b, x, base):
    k = b[0]
    if k == 'atom':
        if b[1].strip():
            draw_string(x, base - ASC[b[2]], b[1], COLOR, b[2])
        return
    if k == 'row':
        for ch in b[1]:
            draw(ch, x, base)
            x += measure(ch)[0]
        return
    if k == 'g':
        gly(b[1], b[2], x, base)
        return
    if k == 'dot':
        sz = b[1]
        cy = base - EM[sz] // 3
        cx = x + (3 if sz != 'small' else 2)
        pix((cx, cy, cx + 1, cy, cx, cy + 1, cx + 1, cy + 1))
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
    if k == 'sub' or k == 'ss':
        sz = b[-1]
        bw, ba, bd = measure(b[1])
        draw(b[1], x, base)
        draw(b[2], x + bw + 1, base + SUBD[sz])
        if k == 'ss':
            draw(b[3], x + bw + 1, base - EM[sz] * 45 // 100)
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
        draw(b[1], x + 4 + 1, base)
        vline(rcol, top + 2, bot - 2)
        pix((x + 1, top + 1, x + 2, top, x + 1, bot - 1, x + 2, bot,
             rcol - 1, top + 1, rcol - 2, top, rcol - 1, bot - 1, rcol - 2, bot))
        return
    if k == 'abs':
        cwd, ca, cd = measure(b[1])
        vline(x + 1, base - ca - 1, base + cd + 1)
        vline(x + cwd + 4, base - ca - 1, base + cd + 1)
        draw(b[1], x + 3, base)
        return
    if k == 'bar' or k == 'hat':
        cwd, ca, cd = measure(b[1])
        draw(b[1], x, base)
        y = base - _accent(b)
        if k == 'bar':
            hline(x + 1, x + cwd - 2, y)
        else:
            m = x + cwd // 2
            pix((m, y - 2, m - 1, y - 1, m + 1, y - 1, m - 2, y, m + 2, y))
        return
    if k == 'mat':
        sz = b[2]
        w, a, d = measure(b)
        cws, ras, rds = _mat(b)
        top = base - a
        bot = base + d - 1
        vline(x + 1, top, bot)
        hline(x + 2, x + 3, top); hline(x + 2, x + 3, bot)
        r = x + w - 2
        vline(r, top, bot)
        hline(r - 2, r - 1, top); hline(r - 2, r - 1, bot)
        gap = 12 if sz != 'small' else 8
        y = top + 1
        i = 0
        for row in b[1]:
            y += ras[i]
            cx = x + 6
            j = 0
            for c in row:
                cw0 = measure(c)[0]
                draw(c, cx + (cws[j] - cw0) // 2, y)
                cx += cws[j] + gap
                j += 1
            y += rds[i] + 2
            i += 1
        return

def flat(b):
    # nested rows flattened and neighbouring same-size text joined, so a
    # line costs one draw_string per run of text rather than one per atom
    k = b[0]
    if k == 'atom' or k == 'g' or k == 'sp' or k == 'dot':
        return b
    if k == 'row':
        out = []
        _join(b, out)
        if len(out) == 1:
            return out[0]
        return ('row', out)
    if k == 'mat':
        return ('mat', [[flat(c) for c in r] for r in b[1]], b[2])
    return (k,) + tuple([flat(c) if isinstance(c, tuple) else c for c in b[1:]])

def _join(b, out):
    for ch in b[1]:
        if ch[0] == 'row':
            _join(ch, out)
            continue
        ch = flat(ch)
        if ch[0] == 'row':
            _join(ch, out)
        elif ch[0] == 'atom' and out and out[-1][0] == 'atom' and out[-1][2] == ch[2]:
            out[-1] = ('atom', out[-1][1] + ch[1], ch[2])
        elif ch[0] != 'atom' or ch[1]:
            out.append(ch)

def shrink(b):
    # the same box one size down (medium -> small), for a piece too wide
    k = b[0]
    if k == 'atom':
        return ('atom', b[1], 'small')
    if k == 'g':
        return ('g', b[1], 'small')
    if k == 'dot':
        return ('dot', 'small')
    if k == 'sp':
        return ('sp', b[1] * 2 // 3)
    if k == 'row':
        return ('row', [shrink(c) for c in b[1]])
    if k == 'mat':
        return ('mat', [[shrink(c) for c in r] for r in b[1]], 'small')
    out = [k]
    for c in b[1:]:
        if isinstance(c, tuple):
            c = shrink(c)
        elif c == 'medium' or c == 'large':
            c = 'small'
        out.append(c)
    return tuple(out)

# ---- display lists: a box drawn once into strings and pixel ops, so a
# screen that redraws it (scrolling) pays only for the drawing itself

_STRS = []

def _rs(x, y, text, color=None, size=None):
    _STRS.append((x, y, text, size))

def record(b, x, base):
    # ([(x, y, text, size)], [pixel ops]) for b drawn at x, base
    global draw_string, OPS
    ds = draw_string
    del _STRS[:]
    OPS = []
    draw_string = _rs
    try:
        draw(b, x, base)
    finally:
        draw_string = ds
        ops = OPS
        OPS = None
    return list(_STRS), ops

def play(ops, x, y, color):
    # draw recorded pixel ops moved by x, y
    global COLOR
    COLOR = color
    for o in ops:
        k = o[0]
        if k == 0:
            hline(o[1] + x, o[2] + x, o[3] + y)
        elif k == 1:
            vline(o[1] + x, o[2] + y, o[3] + y)
        elif k == 2:
            drawline(o[1] + x, o[2] + y, o[3] + x, o[4] + y)
        elif k == 3:
            gly(o[1], o[2], o[3] + x, o[4] + y)
        elif x == 0 and y == 0:
            pix(o[1])
        else:
            p = o[1]
            q = []
            for i in range(0, len(p), 2):
                q.append(p[i] + x)
                q.append(p[i + 1] + y)
            pix(q)

def render(node, x0, y0, x1, y1, color):
    global COLOR
    COLOR = color
    box = None
    w = a = d = 0
    for lvl in (0, 1):
        _MCACHE.clear()
        box = flat(build(node, lvl))
        w, a, d = measure(box)
        if w <= (x1 - x0) and (a + d) <= (y1 - y0):
            x = x0 + ((x1 - x0) - w) // 2
            cy = (y0 + y1) // 2
            draw(box, x, cy + (a - d) // 2)
            _MCACHE.clear()
            return True
    _MCACHE.clear()
    return False
