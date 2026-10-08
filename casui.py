# Screens: home grid, section grids, tool lists, the natural-display editor,
# the result screen, Calculate (with history), CAS, Graph and Solve.
# Only casioplot is imported up front; the engine loads the first time a screen
# needs it, so the home screen appears straight away.
from casioplot import *

KEYCODES = set([
    12, 13, 14, 15, 16,
    21, 22, 23, 24, 25, 26,
    31, 32, 33, 34, 35, 36,
    41, 42, 43, 44, 45, 46,
    51, 52, 53, 54, 55, 56,
    61, 62, 63, 64,
    71, 72, 73, 74, 75,
    81, 82, 83, 84, 85,
    91, 92, 93, 94, 95,
])

HOME = 12; LINESTART = 13; UP = 14; LINEEND = 15; PAGEUP = 16
SETTINGS = 21; EXITK = 22; LEFT = 23; OK = 24; RIGHT = 25; PAGEDOWN = 26
SHIFT = 31; ALPHA = 32; VARIABLE = 33; DOWN = 34; MENU = 35; TOOLS = 36
DEL = 64; FORMAT = 94; EXE = 95; PLUS = 84; MINUS = 85; ZERO = 91

DIGITS = {81: 1, 82: 2, 83: 3, 71: 4, 72: 5, 73: 6, 61: 7, 62: 8, 63: 9, 91: 0}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACC = (40, 120, 220)
GREY = (120, 120, 130)
LGREY = (200, 205, 215)
HL = (222, 232, 252)
RED = (205, 60, 60)
GREEN = (30, 150, 90)
ORANGE = (235, 130, 30)
PURPLE = (130, 70, 200)
TEAL = (20, 150, 160)

W = 384
TOP = 26        # first body pixel under the header
BOT = 177       # last body pixel above the footer

DEG = False     # mirrors casutil.DEG so the home screen needs no engine

# ---- keys -------------------------------------------------------------------

def readkey():
    k = getkey()
    return k if k in KEYCODES else 0

def wait_release():
    while readkey():
        pass

def wait_key():
    k = readkey()
    while not k:
        k = readkey()
    return k

def next_key():
    wait_release()
    return wait_key()

# ---- drawing ------------------------------------------------------------------

_WIDE = "mwMW@%"
_NARROW = " iIjl1tfr.,;:!'|()[]{}/-"

def char_w(ch, size):
    if size == 'small':
        return 8 if ch in _WIDE else (5 if ch in _NARROW else 7)
    if size == 'large':
        return 21 if ch in _WIDE else (14 if ch in _NARROW else 18)
    return 12 if ch in _WIDE else (8 if ch in _NARROW else 10)

def text_w(s, size):
    w = 0
    for c in s:
        w += char_w(c, size)
    return w

def clip(s, maxpx, size):
    if text_w(s, size) <= maxpx:
        return s
    dots = text_w('..', size)
    out = ''
    w = 0
    for c in s:
        cw = char_w(c, size)
        if w + cw + dots > maxpx:
            break
        out += c
        w += cw
    return out + '..'

def wrap(s, maxpx, size):
    # word wrap; a word wider than the line is cut
    out = []
    line = ''
    for word in s.split(' '):
        t = word if not line else line + ' ' + word
        if text_w(t, size) <= maxpx:
            line = t
            continue
        if line:
            out.append(line)
        while text_w(word, size) > maxpx:
            cut = clip(word, maxpx, size)[:-2]
            if not cut:
                break
            out.append(cut)
            word = word[len(cut):]
        line = word
    if line or not out:
        out.append(line)
    return out

def hline(x0, x1, y, c):
    sp = set_pixel
    while x0 <= x1:
        sp(x0, y, c)
        x0 += 1

def vline(x, y0, y1, c):
    sp = set_pixel
    while y0 <= y1:
        sp(x, y0, c)
        y0 += 1

def rect(x0, y0, x1, y1, c):
    sp = set_pixel
    while y0 <= y1:
        x = x0
        while x <= x1:
            sp(x, y0, c)
            x += 1
        y0 += 1

def box(x0, y0, x1, y1, c):
    # rounded outline
    hline(x0 + 2, x1 - 2, y0, c)
    hline(x0 + 2, x1 - 2, y1, c)
    vline(x0, y0 + 2, y1 - 2, c)
    vline(x1, y0 + 2, y1 - 2, c)
    set_pixel(x0 + 1, y0 + 1, c); set_pixel(x1 - 1, y0 + 1, c)
    set_pixel(x0 + 1, y1 - 1, c); set_pixel(x1 - 1, y1 - 1, c)

def line(x0, y0, x1, y1, c):
    dx = x1 - x0 if x1 > x0 else x0 - x1
    dy = -(y1 - y0 if y1 > y0 else y0 - y1)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_pixel(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def disc(cx, cy, r, c, fill):
    # midpoint circle; fill draws spans
    x = r
    y = 0
    e = 1 - r
    while x >= y:
        if fill:
            hline(cx - x, cx + x, cy + y, c); hline(cx - x, cx + x, cy - y, c)
            hline(cx - y, cx + y, cy + x, c); hline(cx - y, cx + y, cy - x, c)
        else:
            for px, py in ((x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)):
                set_pixel(cx + px, cy + py, c)
        y += 1
        if e < 0:
            e += 2 * y + 1
        else:
            x -= 1
            e += 2 * (y - x) + 1

def ctext(cx, y, s, c, size):
    draw_string(cx - text_w(s, size) // 2, y, s, c, size)

def header(title, right=None):
    draw_string(6, 4, clip(title, 290 if right else 372, 'medium'), ACC, 'medium')
    if right:
        draw_string(W - 6 - text_w(right, 'small'), 8, right, GREY, 'small')
    hline(0, W - 1, 23, LGREY)

def footer(s):
    hline(0, W - 1, 178, LGREY)
    draw_string(6, 181, clip(s, 372, 'small'), GREY, 'small')

def flash(msg):
    lines = wrap(msg, 340, 'medium')[:3]
    h = 14 + 18 * len(lines)
    y0 = 96 - h // 2
    rect(20, y0, 363, y0 + h, WHITE)
    box(20, y0, 363, y0 + h, RED)
    box(21, y0 + 1, 362, y0 + h - 1, RED)
    y = y0 + 8
    for ln in lines:
        ctext(192, y, ln, RED, 'medium')
        y += 18
    show_screen()
    next_key()
    wait_release()

# ---- list menu ------------------------------------------------------------------

ROWS = 7
PITCH = 21

def _draw_menu(title, opts, sel, top, hint):
    clear_screen()
    n = len(opts)
    header(title, str(sel + 1) + '/' + str(n) if n > ROWS else None)
    r = 0
    while r < ROWS and top + r < n:
        i = top + r
        y = TOP + 1 + r * PITCH
        if i == sel:
            rect(3, y, 376, y + PITCH - 3, HL)
            vline(3, y, y + PITCH - 3, ACC)
            vline(4, y, y + PITCH - 3, ACC)
        if i < 9:
            draw_string(10, y + 3, str(i + 1), ACC if i == sel else GREY, 'small')
        draw_string(26, y + 1, clip(opts[i], 345, 'medium'), BLACK, 'medium')
        r += 1
    if top > 0:
        ctext(372, TOP - 1, '^', GREY, 'small')
    if top + ROWS < n:
        ctext(372, 168, 'v', GREY, 'small')
    footer(hint)
    show_screen()

def menu(title, opts, sel=0, hint='EXE open   EXIT back   1-9 jump'):
    if not opts:
        return -1
    n = len(opts)
    if sel >= n:
        sel = 0
    top = 0
    while True:
        if sel < top:
            top = sel
        if sel >= top + ROWS:
            top = sel - ROWS + 1
        _draw_menu(title, opts, sel, top, hint)
        k = next_key()
        if k == UP:
            sel = (sel - 1) % n
        elif k == DOWN:
            sel = (sel + 1) % n
        elif k == LINESTART:
            sel = 0
        elif k == LINEEND:
            sel = n - 1
        elif k == PAGEUP or k == LEFT:
            sel = sel - ROWS if sel >= ROWS else 0
        elif k == PAGEDOWN or k == RIGHT:
            sel = sel + ROWS if sel + ROWS < n else n - 1
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
        else:
            d = DIGITS.get(k, None)
            if d is not None and 1 <= d <= n:
                wait_release()
                return d - 1

# ---- icon grid ----------------------------------------------------------------------
# A tile is (label, painter). painter(cx, cy) draws a ~44px icon centred there.

GCOLS = 4
GROWS = 2

def _draw_grid(title, right, tiles, sel):
    clear_screen()
    per = GCOLS * GROWS
    page = sel // per
    pages = (len(tiles) + per - 1) // per
    if pages > 1:
        right = (right + '  ' if right else '') + str(page + 1) + '/' + str(pages)
    header(title, right)
    tw = W // GCOLS
    th = (192 - TOP) // GROWS
    big = True
    for label, paint in tiles[page * per:(page + 1) * per]:
        if text_w(label, 'medium') > tw - 6:
            big = False
    i = page * per
    while i < len(tiles) and i < (page + 1) * per:
        c = (i - page * per) % GCOLS
        r = (i - page * per) // GCOLS
        x0 = c * tw
        y0 = TOP + r * th
        label, paint = tiles[i]
        if i == sel:
            rect(x0 + 3, y0 + 1, x0 + tw - 4, y0 + th - 3, HL)
            box(x0 + 2, y0, x0 + tw - 3, y0 + th - 2, ACC)
            box(x0 + 3, y0 + 1, x0 + tw - 4, y0 + th - 3, ACC)
        paint(x0 + tw // 2, y0 + 28)
        lines = [label] if big else wrap(label, tw - 2, 'small')
        if len(lines) == 1:
            ctext(x0 + tw // 2, y0 + (56 if big else 60), lines[0], ACC if i == sel else BLACK,
                  'medium' if big else 'small')
        else:
            ctext(x0 + tw // 2, y0 + 55, lines[0], ACC if i == sel else BLACK, 'small')
            ctext(x0 + tw // 2, y0 + 66, clip(lines[1], tw - 2, 'small'), ACC if i == sel else BLACK, 'small')
        i += 1
    show_screen()

def grid(title, tiles, sel=0, right=None):
    n = len(tiles)
    if sel >= n:
        sel = 0
    per = GCOLS * GROWS
    while True:
        _draw_grid(title, right() if right else None, tiles, sel)
        k = next_key()
        if k == RIGHT:
            sel = (sel + 1) % n
        elif k == LEFT:
            sel = (sel - 1) % n
        elif k == DOWN:
            sel = sel + GCOLS if sel + GCOLS < n else (sel % GCOLS if sel // per == (n - 1) // per else n - 1)
        elif k == UP:
            sel = sel - GCOLS if sel >= GCOLS else sel
        elif k == PAGEDOWN:
            sel = sel + per if sel + per < n else n - 1
        elif k == PAGEUP:
            sel = sel - per if sel >= per else 0
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
        else:
            d = DIGITS.get(k, None)
            if d is not None and d >= 1:
                j = (sel // per) * per + d - 1
                if j < n:
                    wait_release()
                    return j

# ---- icons ---------------------------------------------------------------------------

def ic_calc(cx, cy):
    x0 = cx - 15
    y0 = cy - 20
    rect(x0, y0, x0 + 30, y0 + 40, (60, 70, 90))
    rect(x0 + 4, y0 + 4, x0 + 26, y0 + 13, (190, 225, 200))
    draw_string(x0 + 14, y0 + 3, '42', (30, 60, 40), 'small')
    r = 0
    while r < 3:
        c = 0
        while c < 3:
            kx = x0 + 4 + c * 8
            ky = y0 + 18 + r * 7
            rect(kx, ky, kx + 5, ky + 4, ORANGE if (r == 2 and c == 2) else (220, 222, 230))
            c += 1
        r += 1

def ic_cas(cx, cy):
    rect(cx - 21, cy - 16, cx + 21, cy + 16, PURPLE)
    ctext(cx, cy - 13, 'd', WHITE, 'medium')
    hline(cx - 12, cx + 12, cy + 1, WHITE)
    ctext(cx, cy + 2, 'dx', WHITE, 'medium')

def ic_graph(cx, cy):
    vline(cx - 16, cy - 19, cy + 19, GREY)
    hline(cx - 20, cx + 20, cy + 12, GREY)
    px = None
    x = -18
    while x <= 18:
        y = cy + 12 - (324 - x * x) * 30 // 324 + 6
        if px is not None:
            line(cx + px[0], px[1], cx + x, y, RED)
            line(cx + px[0], px[1] + 1, cx + x, y + 1, RED)
        px = (x, y)
        x += 3

def ic_solve(cx, cy):
    rect(cx - 21, cy - 14, cx + 21, cy + 14, TEAL)
    ctext(cx, cy - 8, 'x=?', WHITE, 'medium')

def ic_pi(cx, cy):
    rect(cx - 17, cy - 15, cx + 17, cy - 11, ACC)
    rect(cx - 10, cy - 11, cx - 6, cy + 16, ACC)
    rect(cx + 5, cy - 11, cx + 9, cy + 12, ACC)
    rect(cx + 9, cy + 12, cx + 13, cy + 16, ACC)

def ic_argand(cx, cy):
    hline(cx - 20, cx + 20, cy, GREY)
    vline(cx, cy - 20, cy + 20, GREY)
    disc(cx, cy, 15, GREEN, False)
    disc(cx, cy, 14, GREEN, False)
    line(cx, cy, cx + 10, cy - 11, GREEN)
    line(cx + 1, cy, cx + 11, cy - 11, GREEN)
    disc(cx + 10, cy - 11, 3, GREEN, True)
    draw_string(cx + 12, cy + 2, 'z', GREEN, 'medium')

def ic_book(cx, cy):
    rect(cx - 16, cy - 19, cx + 16, cy + 19, ORANGE)
    rect(cx - 11, cy - 16, cx + 13, cy + 16, (255, 245, 225))
    for y in (cy - 10, cy - 4, cy + 2, cy + 8):
        hline(cx - 7, cx + 9, y, (190, 140, 80))

def ic_angle(cx, cy):
    ox = cx - 16
    oy = cy + 14
    hline(ox, ox + 34, oy, BLACK)
    hline(ox, ox + 34, oy + 1, BLACK)
    line(ox, oy, ox + 26, oy - 26, BLACK)
    line(ox + 1, oy, ox + 27, oy - 26, BLACK)
    x = 0
    while x <= 18:
        y = 18 * 18 - x * x
        r = 0
        while r * r < y:
            r += 1
        set_pixel(ox + x, oy - r, ORANGE)
        set_pixel(ox + r, oy - x, ORANGE)
        x += 1
    ctext(cx + 6, cy - 22, 'DEG' if DEG else 'RAD', ORANGE, 'small')

def badge(code, color):
    def paint(cx, cy):
        disc(cx, cy - 2, 20, color, True)
        size = 'large' if len(code) == 1 else 'medium'
        ctext(cx, cy - 2 - (10 if size == 'large' else 7), code, WHITE, size)
    return paint

# ---- natural-display editor ----------------------------------------------------------

_LAST = {}      # label|spec -> the row last typed there, so going back never loses it

def _mode(shift, alpha):
    if shift:
        return 'SHIFT'
    if alpha:
        return 'ALPHA'
    return 'DEG' if DEG else 'RAD'

def _fields(spec):
    import casutil
    names = []
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind != 'n' and kind != 'e':
            return None
        names.append(name)
    return names if len(names) > 1 else None

def _draw_input(label, spec, ed, shift, alpha, names):
    import nat
    clear_screen()
    header(label, _mode(shift, alpha))
    draw_string(6, TOP + 2, clip(spec.replace(',', ', '), 372, 'medium'), GREY, 'medium')
    w, a, d = nat.measure(ed.root, 0)
    base = 72 if a <= 24 else 50 + a - 2
    box(2, 46, 381, base + d + 8, LGREY)
    nat.draw(ed, ed.root, 8, base, 368)
    y = base + d + 14
    if names and ed.root:
        parts = _split(nat.lin(ed.root))
        i = 0
        x = 6
        while i < len(names) and y < 166:
            s = names[i] + ' = ' + (parts[i] if i < len(parts) else '')
            s = clip(s, 118, 'small')
            draw_string(x, y, s, GREY if i < len(parts) else LGREY, 'small')
            x += 124
            i += 1
            if i % 3 == 0:
                x = 6
                y += 13
    footer('EXE run   MENU symbols   SHIFT DEL clear   EXIT back')
    show_screen()

def _split(text):
    import casutil
    return casutil.split_values(text)

def symbols(ed):
    import nat
    i = pick('Symbols', nat.SYMBOLS)
    if i >= 0:
        nat.symbol(ed, nat.SYMBOLS[i])

def edit_key(ed, k, shift, alpha):
    # shared editing keys; returns True if the key was used
    import nat
    if k == LEFT:
        ed.left()
    elif k == RIGHT:
        ed.right()
    elif k == UP:
        return ed.vert(True)
    elif k == DOWN:
        return ed.vert(False)
    elif k == LINESTART:
        ed.home()
    elif k == LINEEND:
        ed.end()
    elif k == DEL:
        if shift:
            ed.clear()
        else:
            ed.dele()
    elif k == MENU:
        symbols(ed)
    else:
        return nat.typed(ed, k, shift, alpha)
    return True

def input_line(label, spec, last=''):
    import nat
    key = label + '|' + spec
    row = _LAST.get(key)
    if row is not None:
        ed = nat.Ed(nat.copy(row))
    else:
        ed = nat.Ed(nat.from_text(last) if last else [])
    shift = False
    alpha = False
    names = _fields(spec)
    while True:
        _draw_input(label, spec, ed, shift, alpha, names)
        k = next_key()
        if k == SHIFT:
            shift = not shift
            alpha = False
            continue
        if k == ALPHA:
            alpha = not alpha
            shift = False
            continue
        if k == EXITK:
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return None
        if k == OK or k == EXE:
            if not ed.root:
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return nat.lin(ed.root)
        edit_key(ed, k, shift, alpha)
        shift = False
        alpha = False

# ---- small grid picker (symbols) ------------------------------------------------------

def pick(title, labels, sel=0):
    cols = 4
    rows = 6
    per = cols * rows
    n = len(labels)
    while True:
        clear_screen()
        page = sel // per
        header(title, str(page + 1) + '/' + str((n + per - 1) // per))
        i = page * per
        while i < n and i < (page + 1) * per:
            c = (i - page * per) % cols
            r = (i - page * per) // cols
            x0 = c * 96
            y0 = TOP + r * 25
            if i == sel:
                rect(x0 + 3, y0 + 1, x0 + 92, y0 + 22, HL)
                box(x0 + 2, y0, x0 + 93, y0 + 23, ACC)
            ctext(x0 + 48, y0 + 4, labels[i], ACC if i == sel else BLACK, 'medium')
            i += 1
        show_screen()
        k = next_key()
        if k == RIGHT:
            sel = (sel + 1) % n
        elif k == LEFT:
            sel = (sel - 1) % n
        elif k == DOWN:
            sel = sel + cols if sel + cols < n else sel
        elif k == UP:
            sel = sel - cols if sel >= cols else sel
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1

# ---- result screen -------------------------------------------------------------------

def _blocks(lines, mode):
    import casrender
    import caseng
    casrender._MCACHE.clear()   # keyed by id(); stale entries from freed boxes overlap text
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            kind = ln[0]
            if (kind == 'w' or kind == 'mw') and mode == 0:
                continue
            if kind == 'm' or kind == 'mw':
                b = casrender.build(ln[1], 0)
                bw, ba, bd = casrender.measure(b)
                if bw <= 372:
                    out.append((kind, b, ba + bd + 6))
                    continue
                kind = 'a' if kind == 'm' else 'w'
                text = caseng.tostr(ln[1])
            else:
                text = ln[1]
        else:
            kind = 'a'
            text = ln
        for part in wrap(text, 372 if kind != 'w' else 364, 'medium'):
            out.append((kind, part, 19))
    return out

def _draw_result(title, sub, blocks, top, mode, more):
    import casrender
    clear_screen()
    header(title)
    y = TOP + 1
    if sub:
        draw_string(6, y, clip(sub, 372, 'small'), GREY, 'small')
        y += 14
    i = top
    n = len(blocks)
    while i < n:
        kind, payload, h = blocks[i]
        if y + h > BOT + 1:
            break
        if kind == 'a':
            draw_string(6, y, payload, BLACK, 'medium')
        elif kind == 'w':
            draw_string(14, y, payload, GREY, 'medium')
        elif kind == '!':
            draw_string(6, y, payload, RED, 'medium')
        else:
            bw, ba, bd = casrender.measure(payload)
            casrender.COLOR = BLACK if kind == 'm' else GREY
            casrender.draw(payload, 6 if kind == 'm' else 14, y + 3 + ba)
        y += h
        i += 1
    foot = ['FORMAT show working', 'FORMAT full precision', 'FORMAT answer only'][mode] if more else ''
    if i < n or top > 0:
        foot += '   ^v scroll ' + str(top + 1) + '-' + str(i) + '/' + str(n)
    footer(foot + '   EXIT back')
    show_screen()
    return i

def result(label, text, lines_fn):
    # lines_fn: callable giving the lines (called again for full precision),
    # or a plain list for static content
    import casutil
    mode = 0
    top = 0
    more = not isinstance(lines_fn, list)
    casutil.FULL = False
    try:
        while True:
            lines = lines_fn if isinstance(lines_fn, list) else lines_fn()
            blocks = _blocks(lines, mode)
            if not blocks:
                blocks = [('!', 'nothing to show', 19)]
            if top >= len(blocks):
                top = len(blocks) - 1
            end = _draw_result(label, text, blocks, top, mode, more)
            k = next_key()
            if k == EXITK or k == OK or k == EXE:
                wait_release()
                return
            if k == DOWN:
                if end < len(blocks):
                    top += 1
            elif k == UP:
                if top > 0:
                    top -= 1
            elif k == PAGEDOWN:
                if end < len(blocks):
                    top = end
            elif k == PAGEUP:
                top = top - 7 if top > 7 else 0
            elif k == FORMAT and more:
                mode = (mode + 1) % 3
                casutil.FULL = (mode == 2)
                top = 0
    finally:
        casutil.FULL = False

def show_lines(title, lines):
    result(title, '', lines)

# ---- Calculate: history, answers stay on screen, nothing is lost going back -----------

HIST = []       # [row, forms, which form is shown]
ANS = [('n', 0)]  # last answer as an exact tree, so Ans - 2 stays exact
CALC = {}       # 'ed', 'fresh' (showing the answer to the last line), 'pos'

def _calc_lines(tree, val):
    import caseng
    import casutil
    lines = [('m', tree)]
    lines.append(casutil.fmt(val))
    try:
        simp = caseng.simplify(tree)
        ex = caseng.tostr(simp)
        if not caseng.vars_in(simp) and ex != casutil.fmt(val) and len(ex) <= 40 and ex != casutil.sf3(val):
            lines.append(('w', 'exact ' + ex))
    except Exception:
        pass
    if isinstance(val, complex):
        lines.append(('w', 'mod ' + casutil.fmt(caseng._cabs(val)) + '  arg ' + casutil.fmt(caseng._carg(val))))
    elif isinstance(val, float):
        lines.append(('w', casutil.sf3(val) + ' (3 s.f.)'))
    return lines

def _forms(text):
    # every way to show the answer; FORMAT cycles through them
    import caslex
    import caseng
    import casutil
    tree = caslex.parse(text)
    if tree is None:
        return [('!', 'cannot read that')]
    tree = _sub_ans(tree, ANS[0])
    forms = []
    try:
        simp = caseng.simplify(tree)
    except Exception:
        simp = None
    if simp is not None and caseng.vars_in(simp):
        return [('m', simp), ('!', 'has a variable - use CAS for x')]
    try:
        val = casutil.ev(tree)
    except ValueError as e:
        return [('!', str(e))]
    if isinstance(val, float) and (val > 1.7e308 or val < -1.7e308):
        return [('!', 'too large')]
    caseng.ANS = val
    ANS[0] = simp if simp is not None else ('n', val)
    seen = []
    if simp is not None and len(caseng.tostr(simp)) <= 60:
        ex = caseng.tostr(simp)
        # re-read the printed form so a complex/rational constant typesets as fractions
        t2 = caslex.parse(ex) if simp[0] == 'n' else None
        forms.append(('m', t2 if t2 is not None else simp))
        seen.append(ex)
    s = casutil.fmt(val)
    if s not in seen:
        forms.append(('a', s))
        seen.append(s)
    v = casutil.clean(val)
    if isinstance(v, float):
        s = casutil._sf(v, 10)
        if s not in seen:
            forms.append(('a', s))
    elif isinstance(v, complex):
        forms.append(('a', 'r=' + casutil.fmt(caseng._cabs(v)) + '  arg=' + casutil.fmt(caseng._carg(v))))
    return forms

def _sub_ans(t, r):
    if t == ('v', 'ans'):
        return r
    if isinstance(t, tuple) and len(t) > 1 and t[0] != 'n' and t[0] != 'v':
        return (t[0],) + tuple([_sub_ans(c, r) for c in t[1:]])
    return t

def _ans_box(form):
    import casrender
    kind, p = form
    if kind == 'm':
        b = casrender.build(p, 0)
        w, a, d = casrender.measure(b)
        if w <= 372:
            return ('m', b, w, a, d)
        import caseng
        p = caseng.tostr(p)
    s = clip(p, 372, 'medium')
    return (kind, s, text_w(s, 'medium'), 13, 4)

def _draw_calc(ed, shift, alpha):
    import nat
    import casrender
    casrender._MCACHE.clear()
    clear_screen()
    header('Calculate', _mode(shift, alpha))
    fresh = CALC.get('fresh')
    editing = CALC.get('editing')
    items = []
    hist = HIST if (fresh or not editing) else HIST[:-1]
    for e in hist:
        forms = e[1]
        note = None
        if e[2] != len(forms) - 1 and forms[-1][0] == 'a':
            note = clip('= ' + forms[-1][1], 372, 'small')
        items.append((e[0], _ans_box(forms[e[2]]), None, note))
    if not fresh:
        items.append((ed.root, None, ed, None))
    # lay out from the newest entry upwards
    blocks = []
    total = 0
    j = len(items) - 1
    while j >= 0:
        row, ans, e, note = items[j]
        w, a, d = nat.measure(row, 0)
        h = a + d + 4
        if ans is not None:
            h += ans[3] + ans[4] + 4
        if note:
            h += 12
        if blocks and total + h > BOT - TOP - 2:
            break
        blocks.insert(0, (row, ans, e, note, a, d, h))
        total += h
        j -= 1
    y = TOP + 2
    if total > BOT - TOP - 2:
        y = BOT - total
    n = 0
    for row, ans, e, note, a, d, h in blocks:
        last = n == len(blocks) - 1
        if n:
            hline(6, 377, y - 2, (235, 236, 240))
        nat.draw(e, row, 6, y + a, 370, BLACK if (e is not None or last) else GREY)
        if ans is not None:
            kind, p, w, aa, ad = ans
            yb = y + a + d + 4 + aa
            if kind == 'm':
                casrender.COLOR = BLACK if last else GREY
                casrender.draw(p, 378 - w, yb)
            else:
                draw_string(378 - w, yb - 13, p, RED if kind == '!' else (BLACK if last else GREY), 'medium')
            if note:
                draw_string(378 - text_w(note, 'small'), yb + ad + 2, note, GREY, 'small')
        y += h
        n += 1
    if fresh and HIST and len(HIST[-1][1]) > 1:
        footer('FORMAT other form   UP recall   EXIT back')
    else:
        footer('EXE =   UP recall   SHIFT DEL clear   EXIT back')
    show_screen()

def calc_section():
    import nat
    ed = CALC.get('ed')
    if ed is None:
        ed = nat.Ed()
        CALC['ed'] = ed
        CALC['pos'] = 0
    shift = False
    alpha = False
    while True:
        _draw_calc(ed, shift, alpha)
        k = next_key()
        if k == SHIFT:
            shift = not shift
            alpha = False
            continue
        if k == ALPHA:
            alpha = not alpha
            shift = False
            continue
        if k == EXITK:
            wait_release()
            return
        fresh = CALC.get('fresh')
        if k == OK or k == EXE:
            if fresh or not ed.root:
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            forms = _forms(nat.lin(ed.root))
            entry = [nat.copy(ed.root), forms, 0]
            if CALC.get('editing') and HIST:
                HIST[-1] = entry
            else:
                HIST.append(entry)
                if len(HIST) > 30:
                    HIST.pop(0)
            CALC['fresh'] = True
            CALC['editing'] = True
            CALC['pos'] = len(HIST)
            continue
        if k == FORMAT and fresh and HIST:
            e = HIST[-1]
            e[2] = (e[2] + 1) % len(e[1])
            continue
        if fresh:
            if k in (LEFT, RIGHT, DEL, LINESTART, LINEEND):
                CALC['fresh'] = False
                if k == DEL and not shift:
                    ed.end()
                    ed.dele()
                elif k == DEL:
                    ed.clear()
                    CALC['editing'] = False
                elif k == LEFT or k == LINEEND:
                    ed.end()
                    if k == LEFT:
                        ed.left()
                else:
                    ed.home()
                shift = False
                continue
            if k != UP and k != DOWN and k != MENU:
                start = ['ans'] if nat.starts_op(k, shift, alpha) else []
                ed.set(start)
                if edit_key(ed, k, shift, alpha):
                    CALC['fresh'] = False
                    CALC['editing'] = False
                shift = False
                alpha = False
                continue
            if k == MENU:
                ed.set([])
                CALC['fresh'] = False
                CALC['editing'] = False
        if k == UP or k == DOWN:
            if not fresh and ed.vert(k == UP):
                continue
            if not fresh and ed.root:
                continue    # never swap out a line that is being typed
            pos = CALC.get('pos', len(HIST))
            pos = pos - 1 if k == UP else pos + 1
            if 0 <= pos < len(HIST):
                CALC['pos'] = pos
                ed.set(nat.copy(HIST[pos][0]))
                CALC['fresh'] = False
                CALC['editing'] = False
            continue
        if edit_key(ed, k, shift, alpha):
            CALC['fresh'] = False
        shift = False
        alpha = False

# ---- CAS ---------------------------------------------------------------------------

def _tidy(t):
    import cascalc
    return cascalc.tidy(t)

def _cas_op(op, tree, s):
    import caseng
    import cascalc
    import caspoly
    import casutil
    if op == 0:
        return [('m', _tidy(caseng.diff(tree)))]
    if op == 1:
        return [('m', _tidy(caseng.diff(_tidy(caseng.diff(tree)))))]
    if op == 2:
        r = cascalc.integ(tree)
        if r is None:
            return [('!', 'no elementary integral; use definite')]
        return [('m', _tidy(r)), '+ c']
    if op == 3:
        v = casutil.ask('a,b', 'limits')
        if v is None:
            return None
        lo = ('n', v[0])
        hi = ('n', v[1])
        try:
            ex = cascalc.defint_exact(tree, lo, hi)
        except ValueError as e:
            return [('!', str(e))]
        except Exception:
            ex = None
        if ex is not None:
            return [('m', ex), ('w', 'exact: F(b) - F(a)'),
                    ('w', 'from ' + casutil.fmt(v[0]) + ' to ' + casutil.fmt(v[1]))]
        r = cascalc.defint(tree, v[0], v[1], casutil.DEG)
        if r is None:
            return [('!', 'cannot evaluate over that range')]
        return ['integral = ' + casutil.fmt(r),
                ('!', 'numeric (Simpson) - no exact antiderivative'),
                ('w', 'from ' + casutil.fmt(v[0]) + ' to ' + casutil.fmt(v[1]))]
    if op == 4:
        v = casutil.ask('a', 'at x =')
        if v is None:
            return None
        a = v[0]
        y = casutil.ev(tree, a)
        g = casutil.ev(caseng.diff(tree), a)
        lines = ['y = ' + casutil.fmt(y) + '  dy/dx = ' + casutil.fmt(g)]
        lines.append('tangent y = ' + casutil.fmt(g) + 'x + ' + casutil.fmt(y - g * a))
        if g != 0:
            lines.append('normal y = ' + casutil.fmt(-1.0 / g) + 'x + ' + casutil.fmt(y + a / g))
        else:
            lines.append('normal x = ' + casutil.fmt(a))
        return lines
    if op == 5:
        d1 = _tidy(caseng.diff(tree))
        roots = cascalc.solve(d1)
        if not roots:
            return [('!', 'no stationary points found in the search range')]
        d2 = _tidy(caseng.diff(d1))
        lines = []
        for r in roots:
            y = casutil.ev(tree, r)
            c = casutil.evx(d2, r)
            kind = 'min' if (c is not None and c > 1e-9) else ('max' if (c is not None and c < -1e-9) else 'inflection?')
            lines.append('(' + casutil.fmt(r) + ', ' + casutil.fmt(y) + ')  ' + kind)
        lines.append(('mw', d1))
        return lines
    if op == 6:
        return [('m', _tidy(tree))]
    if op == 7:
        return [('m', caspoly.expand(tree))]
    if op == 8:
        r = caspoly.factor(tree)
        if r is None:
            return [('!', 'does not factorise over the rationals')]
        return [('m', r)]
    if op == 9:
        if tree[0] != '/':
            return [('!', 'type it as one fraction, e.g. (3x+5)/((x-1)(x+2))')]
        try:
            r = caspoly.partial(tree[1], tree[2])
        except Exception:
            r = None
        if r is None:
            return [('!', 'cannot split: need polynomials with linear/quadratic factors')]
        quot, terms = r
        lines = []
        if quot is not None:
            lines.append(('m', quot))
        for top, fac, power in terms:
            den = fac
            if power > 1:
                den = ('^', fac, ('n', power))
            lines.append(('m', ('/', top, den)))
        if not terms:
            lines.append(('w', 'divides exactly'))
        return lines
    if op == 10 or op == 11:
        target = tree
        if op == 11:
            v = casutil.ask('k', 'f(x) = k')
            if v is None:
                return None
            target = ('-', tree, ('n', v[0]))
        roots = cascalc.solve(target, deg=casutil.DEG)
        if not roots:
            return [('!', 'no real roots found in the search range')]
        return ['x = ' + ', '.join([casutil.fmt(r) for r in roots])]
    if op == 12:
        v = casutil.ask('x', 'evaluate at')
        if v is None:
            return None
        return ['f(' + casutil.fmt(v[0]) + ') = ' + casutil.fmt(casutil.ev(tree, v[0]))]
    if op == 13:
        v = casutil.ask('start,step', 'table')
        if v is None:
            return None
        lines = []
        i = 0
        while i < 12:
            xv = v[0] + i * v[1]
            y = casutil.evx(tree, xv)
            lines.append(('w', 'x=' + casutil.fmt(xv) + '   f(x)=' + ('undefined' if y is None else casutil.fmt(y))))
            i += 1
        lines.insert(0, 'table of f(x)')
        return lines
    if op == 14:
        import plot
        plot.run([tree], -6.0, 6.0, 'y', 'y = ' + s)
        return None
    return _cas_op2(op, tree, s)

def _roots_lines(roots, exact):
    import caseng
    lines = ['x = ' + caseng.tostr(r) for r in roots]
    for r in roots:
        lines.append(('mw', r))
    if not exact:
        lines.append(('!', 'numeric roots - no exact form found'))
    return lines

def _cas_op2(op, tree, s):
    import caseng
    import casutil
    import casalg
    import cassolve
    if op == 15:
        return [('m', casalg.expand(tree)), ('w', 'compound angles and log laws used')]
    if op == 16:
        r = casalg.complete_square(tree)
        if r is None:
            return [('!', 'not a quadratic in x')]
        return [('m', r), ('w', 'a(x + b/2a)^2 + (c - b^2/4a)')]
    if op == 17:
        r = casalg.rationalise(tree)
        if r is None:
            return [('!', 'nothing to rationalise')]
        return [('m', r), ('w', 'multiplied top and bottom by the conjugate')]
    if op == 18:
        r = casalg.single_fraction(tree)
        if r is None:
            return [('!', 'cannot write as one fraction')]
        return [('m', r), ('w', 'over a common denominator, cancelled')]
    if op == 19:
        roots = cassolve.solve_exact(tree, 'x')
        if roots:
            return _roots_lines(roots, True)
        roots, exact = cassolve.solve_any(tree, 'x', casutil.DEG)
        if not roots:
            return [('!', 'no solutions found')]
        return _roots_lines(roots, exact)
    if op == 20:
        g = cassolve.general_trig(tree, 'x', 'n')
        if not g:
            return [('!', 'not a trig equation in one angle')]
        lines = ['x = ' + caseng.tostr(r) for r in g]
        lines.append(('w', 'n is any integer'))
        return lines
    if op == 21:
        v = casutil.ask('terms', 'how many terms')
        if v is None:
            return None
        r = casalg.maclaurin(tree, 'x', int(v[0]))
        if r is None:
            return [('!', 'no Maclaurin series at x = 0')]
        return [('m', r), ('w', 'sum f(k)(0) x^k / k!')]
    if op == 22:
        v = casutil.ask('a(x)', 'x -> (or inf)')
        if v is None:
            return None
        a = v[0]
        if a == ('v', 'inf'):
            r = casalg.limit(tree, 'x', None, 1)
        elif a == ('neg', ('v', 'inf')):
            r = casalg.limit(tree, 'x', None, -1)
        else:
            r = casalg.limit(tree, 'x', a)
        if r is None:
            return [('!', 'limit not found')]
        return [('m', r), ('w', 'limit as x -> ' + caseng.tostr(a))]
    if op == 23:
        v = casutil.ask('a(x)', 'x =')
        if v is None:
            return None
        return [('m', casalg.subst_exact(tree, 'x', v[0])),
                ('w', 'x = ' + caseng.tostr(v[0]))]
    if op == 24:
        r = casalg.rearrange(tree, 'x', 'y')
        if r is not None:
            return [('m', r), ('w', 'from y = f(x)')]
        br = cassolve.solve_exact(('-', tree, ('v', 'y')), 'x')
        if br:
            return [('m', b) for b in br] + [('w', 'from y = f(x), both branches')]
        return [('!', 'cannot make x the subject')]
    return None

CAS_OPS = ['d/dx', 'd2/dx2', 'integrate', 'definite integral a..b',
           'tangent + normal at x=a', 'stationary points', 'simplify', 'expand',
           'factorise', 'partial fractions', 'solve f(x)=0', 'solve f(x)=k',
           'evaluate at x', 'table', 'plot',
           'expand trig / log', 'complete the square', 'rationalise',
           'single fraction', 'solve exact f(x)=0', 'general solution (trig)',
           'series (Maclaurin)', 'limit x -> a', 'substitute x = a',
           'rearrange for x']

def _read(label, spec):
    # editor -> (text, tree); None when the user backs out
    import caslex
    while True:
        s = input_line(label, spec, '')
        if s is None:
            return None
        if '=' in s:
            l, r = s.split('=', 1)
            s = '(' + l + ')-(' + r + ')'
        tree = caslex.parse(s)
        if tree is None:
            flash('cannot read that')
            continue
        return s, tree

def _run_op(op, tree, s):
    try:
        lines = _cas_op(op, tree, s)
    except ValueError as e:
        lines = [('!', str(e))]
    except Exception as e:
        lines = [('!', 'error: ' + str(e))]
    if lines is not None:
        result(CAS_OPS[op], 'f(x) = ' + s, lines)

def cas_section():
    op = 0
    while True:
        got = _read('CAS', 'f(x)')
        if got is None:
            return
        s, tree = got
        while True:
            op = menu('f(x) = ' + s, CAS_OPS, op)
            if op < 0:
                break
            _run_op(op, tree, s)

def solve_section():
    while True:
        got = _read('Solve', 'equation in x (= allowed)')
        if got is None:
            return
        _run_op(19, got[1], got[0])

def graph_section():
    import plot
    while True:
        got = _read('Graph', 'y = f(x)')
        if got is None:
            return
        plot.run([got[1]], -6.0, 6.0, 'y', 'y = ' + got[0])

# ---- sections ------------------------------------------------------------------------
# Static index so a section grid shows without importing the (large) tool modules;
# tests.py checks it against each module's SECTIONS.

MATHS = (
    ('A', 'Proof', 'mpure'), ('B', 'Algebra and functions', 'mpure'),
    ('C', 'Coordinate geometry', 'mpure'), ('D', 'Sequences and series', 'mpure'),
    ('E', 'Trigonometry', 'mpure'), ('F', 'Exponentials and logs', 'mpure'),
    ('G', 'Differentiation', 'mcalc'), ('H', 'Integration', 'mcalc'),
    ('I', 'Numerical methods', 'mcalc'), ('J', 'Vectors', 'mcalc'),
    ('K', 'Statistical sampling', 'mstat'), ('L', 'Data presentation', 'mstat'),
    ('M', 'Probability', 'mstat'), ('N', 'Statistical distributions', 'mstat'),
    ('O', 'Hypothesis testing', 'mstat'),
    ('P', 'Quantities and units', 'mmech'), ('Q', 'Kinematics', 'mmech'),
    ('R', 'Forces and Newton laws', 'mmech'), ('S', 'Moments', 'mmech'),
)

# A-level Maths is AQA 7357; Further Maths is OCR B (MEI) H645, grouped by paper.
FURTHER = (
    ('Core Pure', 'Y420', (
        ('P', 'Proof', 'fcore'), ('J', 'Complex numbers', 'fcore'),
        ('M', 'Matrices, transformations', 'fcore'), ('V', 'Vectors and 3-D', 'fcore'),
        ('A', 'Roots of polynomials', 'fcore'), ('S', 'Series, Maclaurin', 'fcore'),
        ('C', 'Calculus', 'fcalc'), ('PO', 'Polar coordinates', 'fcalc'),
        ('H', 'Hyperbolic functions', 'fcalc'), ('D', 'Differential equations', 'fcalc'))),
    ('Mechanics', 'Y421/Y431', (
        ('D', 'Dimensional analysis', 'fmech'), ('F', 'Forces and friction', 'fmech'),
        ('M', 'Moments and rigid bodies', 'fmech'), ('W', 'Work, energy and power', 'fmech'),
        ('I', 'Impulse and momentum', 'fmech'), ('G', 'Centre of mass', 'fmech'),
        ('C', 'Circular motion', 'fmech'), ('H', "Hooke's law", 'fmech'),
        ('V', 'Vectors, variable forces', 'fmech'))),
    ('Statistics', 'Y422/Y432', (
        ('D', 'Discrete random vars', 'fstat'), ('B', 'Binomial and Poisson', 'fstat'),
        ('G', 'Geometric distribution', 'fstat'), ('C', 'Continuous random vars', 'fstat'),
        ('N', 'Normal distribution', 'fstat'), ('R', 'Bivariate data', 'fstat'),
        ('H', 'Chi-squared tests', 'fstat'), ('I', 'Inference', 'fstat'),
        ('W', 'Wilcoxon signed rank', 'fstat'), ('Z', 'Simulation', 'fstat'))),
    ('Algorithms', 'Y433', (
        ('A', 'Sorting and packing', 'falgo'), ('G', 'Graphs', 'falgo'),
        ('N', 'Networks', 'falgo'), ('F', 'Network flows', 'falgo'),
        ('C', 'Critical path', 'falgo'), ('L', 'LP graphical', 'falgo'),
        ('S', 'Simplex', 'falgo'))),
    ('Numerical', 'Y434', (
        ('U', 'Errors', 'fnum'), ('E', 'Solving equations', 'fnum'),
        ('D', 'Numerical differentiation', 'fnum'), ('N', 'Numerical integration', 'fnum'),
        ('A', 'Approximating functions', 'fnum'), ('I', 'Improved estimates', 'fnum'))),
    ('Extra Pure', 'Y435', (
        ('R', 'Recurrence relations', 'fxpure'), ('G', 'Sets and groups', 'fxpure'),
        ('M', 'Matrices: eigenvalues', 'fxpure'), ('C', 'Multivariable calculus', 'fxpure'))),
    ('Pure + Tech', 'Y436', (
        ('C', 'Curves: plots and limits', 'ffpt'), ('T', 'Curves: tangents, arcs', 'ffpt'),
        ('D', 'Differential equations', 'ffpt'), ('N', 'Number theory', 'ffpt'))),
)

MODCOL = {'mpure': ACC, 'mcalc': PURPLE, 'mstat': GREEN, 'mmech': ORANGE,
          'fcore': ACC, 'fcalc': PURPLE, 'fmech': ORANGE, 'fstat': GREEN,
          'falgo': TEAL, 'fnum': RED, 'fxpure': (90, 90, 160), 'ffpt': (160, 90, 60)}

def _tools(code, title, mod):
    for c, t, tools in __import__(mod).SECTIONS:
        if c == code and t == title:
            return tools
    return []

def _tools_menu(code, title, mod):
    tools = _tools(code, title, mod)
    sel = 0
    while True:
        sel = menu(code + '  ' + title, [t[0] for t in tools], sel)
        if sel < 0:
            return
        label, spec, fn = tools[sel]
        try:
            import casutil
            casutil.run_tool(label, spec, fn)
        except Exception as e:
            flash('tool error: ' + str(e))

def qual_section(title, secs):
    tiles = [(t, badge(c, MODCOL.get(m, ACC))) for c, t, m in secs]
    sel = 0
    while True:
        sel = grid(title, tiles, sel)
        if sel < 0:
            return
        _tools_menu(*secs[sel])

PAPERCOL = (ACC, ORANGE, GREEN, TEAL, RED, (90, 90, 160), (160, 90, 60))

def paper_section(title, papers):
    tiles = []
    i = 0
    for name, code, secs in papers:
        tiles.append((name, badge(code.split('/')[0][1:], PAPERCOL[i % len(PAPERCOL)])))
        i += 1
    sel = 0
    while True:
        sel = grid(title, tiles, sel)
        if sel < 0:
            return
        name, code, secs = papers[sel]
        qual_section(name + '  ' + code, secs)

def formulae_section():
    import formulae
    sel = 0
    while True:
        sel = menu('Formulae', [s[0] for s in formulae.SHEETS], sel)
        if sel < 0:
            return
        title, lines = formulae.SHEETS[sel]
        show_lines(title, [('w', ln) for ln in lines])

def _toggle_angle():
    global DEG
    import casutil
    casutil.DEG = not casutil.DEG
    DEG = casutil.DEG

HOME_TILES = [
    ('Calculate', ic_calc), ('CAS', ic_cas), ('Graph', ic_graph), ('Solve', ic_solve),
    ('Maths', ic_pi), ('Further', ic_argand), ('Formulae', ic_book), ('Angle', ic_angle),
]

def main():
    sel = 0
    while True:
        sel = grid('Maths Toolkit', HOME_TILES, sel, lambda: 'AQA 7357 + MEI H645')
        if sel < 0:
            return
        if sel == 0:
            calc_section()
        elif sel == 1:
            cas_section()
        elif sel == 2:
            graph_section()
        elif sel == 3:
            solve_section()
        elif sel == 4:
            qual_section('Maths  AQA 7357', MATHS)
        elif sel == 5:
            paper_section('Further  MEI H645', FURTHER)
        elif sel == 6:
            formulae_section()
        elif sel == 7:
            _toggle_angle()
