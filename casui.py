# Screens: home grid, word grids for every menu, the natural-display editor,
# the result screen, Calculate (with history), CAS, Graph and Solve.
# Only casioplot is imported up front; the engine loads the first time a screen
# needs it, so the home screen appears straight away.
# Drawing is the slow part on the calculator, so screens redraw only what a
# key changed: moving in a grid repaints two tiles, not the screen.
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
INK = (24, 28, 36)
ACC = (0, 96, 200)
GREY = (110, 115, 125)
LGREY = (196, 202, 212)
BAR = (232, 236, 242)       # status bar
TILE = (244, 246, 250)      # unselected word tile
HL = (222, 232, 252)
RED = (200, 50, 50)
GREEN = (30, 150, 90)
ORANGE = (235, 130, 30)
PURPLE = (130, 70, 200)
TEAL = (20, 150, 160)
YEL = (250, 200, 30)

W = 384
H = 192
SBH = 20        # status bar height
TOP = 22        # first body pixel
BOT = 191       # last body pixel

DEG = False     # mirrors casutil.DEG so the home screen needs no engine

# ---- keys -------------------------------------------------------------------
# Arrows and DEL repeat while held, like the built-in apps.

def _clock():
    for name in ('time', 'utime'):
        try:
            m = __import__(name)
        except Exception:
            continue
        if hasattr(m, 'ticks_ms'):
            return m.ticks_ms
        if hasattr(m, 'monotonic'):
            return lambda: int(m.monotonic() * 1000)
    return None

_NOW = _clock()
REPEAT = (UP, DOWN, LEFT, RIGHT, DEL)
DELAY = 380     # ms before a held key repeats
RATE = 60       # ms between repeats
_HELD = [0, 0]  # key still down, time of its next repeat

def readkey():
    k = getkey()
    return k if k in KEYCODES else 0

def wait_release():
    while readkey():
        pass
    _HELD[0] = 0

def wait_key():
    k = readkey()
    while not k:
        k = readkey()
    return k

def next_key():
    k0 = _HELD[0]
    if k0:
        rep = k0 in REPEAT and _NOW is not None
        while True:
            k = readkey()
            if k != k0:
                break
            if rep and _NOW() >= _HELD[1]:
                _HELD[1] = _NOW() + RATE
                return k0
        if k and k != HOME:
            _HELD[0] = k
            _HELD[1] = _NOW() + DELAY if _NOW else 0
            return k
    k = wait_key()
    _HELD[0] = k
    _HELD[1] = _NOW() + DELAY if _NOW else 0
    if k == HOME:
        wait_release()
        raise Home()
    return k

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

def rbox(x0, y0, x1, y1, c):
    # filled, rounded corners
    hline(x0 + 2, x1 - 2, y0, c)
    hline(x0 + 1, x1 - 1, y0 + 1, c)
    rect(x0, y0 + 2, x1, y1 - 2, c)
    hline(x0 + 1, x1 - 1, y1 - 1, c)
    hline(x0 + 2, x1 - 2, y1, c)

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

# ---- status bar -----------------------------------------------------------------
# Title on the left, SHIFT / ALPHA / angle on the right, like the built-in apps.

_SB = ['', None]    # what the bar shows now, so a key that changes nothing redraws nothing

def _ind(shift, alpha):
    if shift:
        return 'S'
    if alpha:
        return 'A'
    return ''

def status(title, shift=False, alpha=False, right=None):
    rect(0, 0, W - 1, SBH - 1, BAR)
    hline(0, W - 1, SBH, LGREY)
    draw_string(6, 2, clip(title, 250, 'medium'), INK, 'medium')
    _status_right(_ind(shift, alpha), right)

def _status_right(ind, right):
    _SB[0] = ind
    _SB[1] = right
    x = W - 6
    s = right if right is not None else ('Deg' if DEG else 'Rad')
    rect(262, 0, W - 1, SBH - 1, BAR)
    x -= text_w(s, 'medium')
    draw_string(x, 2, s, GREY, 'medium')
    if ind:
        x -= 22
        rbox(x, 2, x + 15, 17, YEL if ind == 'S' else RED)
        ctext(x + 8, 2, ind, INK if ind == 'S' else WHITE, 'medium')

def status_mode(shift, alpha, right=None):
    # repaint only the indicator corner when SHIFT / ALPHA changes
    ind = _ind(shift, alpha)
    if ind != _SB[0] or right != _SB[1]:
        _status_right(ind, right)
        return True
    return False

def header(title, right=None):
    status(title, False, False, right)

def body_clear():
    rect(0, TOP, W - 1, BOT, WHITE)

# ---- popup ---------------------------------------------------------------------

def flash(msg):
    lines = wrap(msg, 320, 'medium')[:4]
    h = 18 + 19 * len(lines)
    y0 = 96 - h // 2
    rbox(28, y0 + 2, 359, y0 + h + 2, LGREY)     # shadow
    rbox(26, y0, 357, y0 + h, WHITE)
    box(26, y0, 357, y0 + h, RED)
    y = y0 + 9
    for ln in lines:
        ctext(192, y, ln, RED, 'medium')
        y += 19
    show_screen()
    next_key()
    wait_release()

class Home(BaseException):
    # HOME from anywhere: unwinds to the home grid, past tools' own handlers
    pass

# ---- grids ----------------------------------------------------------------------
# Every menu is a grid. Word tiles for lists of options, icon tiles for the home
# screen. Moving repaints the two tiles involved; scrolling repaints the body.

class Grid:
    def __init__(self, title, tiles, cols, rows, icons):
        self.title = title
        self.tiles = tiles
        self.cols = cols
        self.rows = rows
        self.icons = icons
        self.top = 0
        n = len(tiles)
        self.nrows = (n + cols - 1) // cols
        self.bar = self.nrows > rows
        self.tw = (W - (6 if self.bar else 0)) // cols
        self.th = (H - TOP) // rows
        self.lines = []
        if not icons:
            for label in tiles:
                ls = wrap(label, self.tw - 10, 'medium')
                if len(ls) > 2:
                    ls = [ls[0], clip(' '.join(ls[1:]), self.tw - 10, 'medium')]
                self.lines.append(ls)

    def xy(self, i):
        return ((i % self.cols) * self.tw, TOP + (i // self.cols - self.top) * self.th)

    def tile(self, i, on, full):
        x0, y0 = self.xy(i)
        x1 = x0 + self.tw - 1
        y1 = y0 + self.th - 1
        if self.icons:
            label, paint = self.tiles[i]
            if full:
                paint(x0 + self.tw // 2, y0 + 30)
            c = ACC if on else WHITE
            box(x0 + 2, y0 + 1, x1 - 2, y1 - 1, c)
            box(x0 + 3, y0 + 2, x1 - 3, y1 - 2, c)
            ctext(x0 + self.tw // 2, y0 + 58, label, ACC if on else INK, 'medium')
            return
        ls = self.lines[i]
        if on:
            rbox(x0 + 2, y0 + 2, x1 - 2, y1 - 2, ACC)
            c = WHITE
        else:
            if not full:
                rbox(x0 + 2, y0 + 2, x1 - 2, y1 - 2, WHITE)
            box(x0 + 2, y0 + 2, x1 - 2, y1 - 2, LGREY)
            c = INK
        y = y0 + (self.th - 18 * len(ls)) // 2
        for s in ls:
            ctext(x0 + self.tw // 2, y, s, c, 'medium')
            y += 18

    def scrollbar(self):
        if not self.bar:
            return
        x = W - 4
        rect(x, TOP, x + 2, BOT, BAR)
        span = BOT - TOP + 1
        t0 = TOP + span * self.top // self.nrows
        t1 = TOP + span * (self.top + self.rows) // self.nrows - 1
        rect(x, t0, x + 2, t1 if t1 <= BOT else BOT, ACC)

    def draw(self, sel):
        clear_screen()
        status(self.title)
        i = self.top * self.cols
        end = (self.top + self.rows) * self.cols
        while i < len(self.tiles) and i < end:
            self.tile(i, i == sel, True)
            i += 1
        self.scrollbar()

def grid_run(g, sel):
    n = len(g.tiles)
    if sel >= n or sel < 0:
        sel = 0
    cols = g.cols
    g.top = 0
    r = sel // cols
    if r >= g.rows:
        g.top = r - g.rows + 1
    g.draw(sel)
    show_screen()
    while True:
        k = next_key()
        old = sel
        if k == RIGHT:
            sel = (sel + 1) % n
        elif k == LEFT:
            sel = (sel - 1) % n
        elif k == DOWN:
            if sel + cols < n:
                sel += cols
            elif sel // cols < g.nrows - 1:
                sel = n - 1
            else:
                sel = sel % cols
        elif k == UP:
            if sel >= cols:
                sel -= cols
            else:
                sel = (g.nrows - 1) * cols + sel
                if sel >= n:
                    sel -= cols
        elif k == PAGEDOWN:
            sel = sel + cols * g.rows if sel + cols * g.rows < n else n - 1
        elif k == PAGEUP:
            sel = sel - cols * g.rows if sel >= cols * g.rows else sel % cols
        elif k == LINESTART:
            sel = 0
        elif k == LINEEND:
            sel = n - 1
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
        elif k == SETTINGS:
            settings()
            g.draw(sel)
            show_screen()
            continue
        else:
            d = DIGITS.get(k, None)
            if d is not None and 1 <= d <= n:
                wait_release()
                return d - 1
            continue
        if sel == old:
            continue
        r = sel // cols
        top = g.top
        if r < top:
            top = r
        elif r >= top + g.rows:
            top = r - g.rows + 1
        if top != g.top:
            g.top = top
            g.draw(sel)
        else:
            g.tile(old, False, False)
            g.tile(sel, True, False)
        show_screen()

def _cols_for(labels):
    # three across when every label fits on two lines, else two
    for s in labels:
        if len(wrap(s, 118, 'medium')) > 2:
            return 2
        for word in s.split(' '):
            if text_w(word, 'medium') > 118:
                return 2
    return 3

def menu(title, opts, sel=0, hint=None):
    if not opts:
        return -1
    return grid_run(Grid(title, opts, _cols_for(opts), 4, False), sel)

def grid(title, tiles, sel=0, right=None):
    return grid_run(Grid(title, tiles, 4, 2, True), sel)

def pick(title, labels, sel=0):
    # symbols: short labels, five across
    return grid_run(Grid(title, labels, 5, 5, False), sel)

def settings():
    global DEG
    i = menu('Settings: angle', ['Radians', 'Degrees'], 1 if DEG else 0)
    if i >= 0:
        DEG = i == 1
        try:
            import casutil
            casutil.DEG = DEG
        except ImportError:
            pass

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

# ---- natural-display editor ----------------------------------------------------------

_LAST = {}      # label|spec -> the row last typed there, so going back never loses it

def _fields(spec):
    import casutil
    names = []
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind != 'n' and kind != 'e':
            return None
        names.append(name)
    return names if len(names) > 1 else None

def _field_at(ed):
    # which comma-separated field the caret is in
    row = ed.root
    end = ed.stack[0][1] if ed.stack else ed.i
    n = 0
    i = 0
    while i < end and i < len(row):
        if row[i] == ',':
            n += 1
        i += 1
    return n

def _draw_input(label, spec, ed, shift, alpha, names):
    import nat
    clear_screen()
    status(label, shift, alpha)
    draw_string(8, TOP + 3, clip(spec.replace(',', ', '), 368, 'medium'), GREY, 'medium')
    w, a, d = nat.measure(ed.root, 0)
    base = TOP + 34 + (a - 13 if a > 13 else 0)
    box(3, TOP + 23, W - 4, base + d + 7, ACC)
    nat.draw(ed, ed.root, 10, base, 362)
    y = base + d + 14
    if names:
        parts = _split(nat.lin(ed.root)) if ed.root else []
        cur = _field_at(ed)
        i = 0
        x = 8
        while i < len(names) and y < BOT - 16:
            s = names[i] + ' = ' + (parts[i] if i < len(parts) else '')
            s = clip(s, 118, 'medium')
            draw_string(x, y, s, ACC if i == cur else (INK if i < len(parts) else LGREY), 'medium')
            x += 124
            i += 1
            if i % 3 == 0:
                x = 8
                y += 20
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
    elif k == MENU or k == TOOLS:
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
    dirty = True
    while True:
        if dirty:
            _draw_input(label, spec, ed, shift, alpha, names)
        dirty = True
        k = next_key()
        if k == SHIFT or k == ALPHA:
            if k == SHIFT:
                shift = not shift
                alpha = False
            else:
                alpha = not alpha
                shift = False
            status_mode(shift, alpha)
            show_screen()
            dirty = False
            continue
        if k == EXITK:
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return None
        if k == SETTINGS:
            settings()
            continue
        if k == OK or k == EXE:
            if not ed.root:
                dirty = False
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return nat.lin(ed.root)
        if not edit_key(ed, k, shift, alpha) and not shift and not alpha:
            dirty = False
            continue
        shift = False
        alpha = False

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
                if bw <= 368:
                    out.append((kind, b, ba + bd + 6))
                    continue
                kind = 'a' if kind == 'm' else 'w'
                text = caseng.tostr(ln[1])
            else:
                text = ln[1]
        else:
            kind = 'a'
            text = ln
            b = _typeset(text)
            if b is not None:
                bw, ba, bd = casrender.measure(b)
                if bw <= 368:
                    out.append(('m', b, ba + bd + 6))
                    continue
        for part in wrap(text, 368 if kind != 'w' else 360, 'medium'):
            out.append((kind, part, 20))
    return out

_MATHY = ('/', '^', 'sqrt(')

def _typeset(text):
    # 'x = 1/2 + i*sqrt(3)/2' -> 'x = ' then the expression as a fraction / root
    j = text.find(' = ')
    if j < 0 or j > 24 or '=' in text[j + 3:] or '  ' in text:
        return None
    rhs = text[j + 3:]
    hit = False
    for m in _MATHY:
        if m in rhs:
            hit = True
    if not hit:
        return None
    import caslex
    import casrender
    try:
        t = caslex.parse(rhs)
    except Exception:
        return None
    if t is None:
        return None
    return ('row', [('atom', text[:j + 3], 'medium'), casrender.build(t, 0)])

MODES = (None, 'working', 'full')

def _draw_result(title, sub, blocks, top, mode, more):
    import casrender
    clear_screen()
    status(title, False, False, MODES[mode] if more else '')
    y = TOP + 3
    if sub:
        draw_string(8, y, clip(sub, 368, 'medium'), GREY, 'medium')
        y += 20
        hline(8, W - 9, y - 2, BAR)
        y += 2
    i = top
    n = len(blocks)
    while i < n:
        kind, payload, h = blocks[i]
        if y + h > BOT + 2:
            break
        if kind == 'a':
            draw_string(8, y, payload, INK, 'medium')
        elif kind == 'w':
            draw_string(16, y, payload, GREY, 'medium')
        elif kind == '!':
            draw_string(8, y, payload, RED, 'medium')
        else:
            bw, ba, bd = casrender.measure(payload)
            casrender.COLOR = INK if kind == 'm' else GREY
            casrender.draw(payload, 8 if kind == 'm' else 16, y + 3 + ba)
        y += h
        i += 1
    if top > 0 or i < n:
        # scroll position, right edge
        span = BOT - TOP
        t0 = TOP + span * top // n
        t1 = TOP + span * i // n
        vline(W - 3, TOP, BOT, BAR)
        vline(W - 2, TOP, BOT, BAR)
        vline(W - 3, t0, t1, ACC)
        vline(W - 2, t0, t1, ACC)
    show_screen()
    return i

def result(label, text, lines_fn):
    # lines_fn: callable giving the lines (called again for full precision),
    # or a plain list for static content. Each form is worked out once.
    import casutil
    mode = 0
    top = 0
    more = not isinstance(lines_fn, list)
    raw = {}
    blocks = None
    try:
        while True:
            if blocks is None:
                full = mode == 2
                casutil.FULL = full
                if full not in raw:
                    raw[full] = lines_fn if not more else lines_fn()
                blocks = _blocks(raw[full], mode)
                if not blocks:
                    blocks = [('!', 'nothing to show', 20)]
            if top >= len(blocks):
                top = len(blocks) - 1
            end = _draw_result(label, text, blocks, top, mode, more)
            while True:
                k = next_key()
                if k == EXITK or k == OK or k == EXE:
                    wait_release()
                    return
                if k == DOWN and end < len(blocks):
                    top += 1
                elif k == UP and top > 0:
                    top -= 1
                elif k == PAGEDOWN and end < len(blocks):
                    top = end
                elif k == PAGEUP and top > 0:
                    top = top - 7 if top > 7 else 0
                elif k == FORMAT and more:
                    mode = (mode + 1) % 3
                    top = 0
                    blocks = None
                else:
                    continue
                break
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
    status('Calculate', shift, alpha)
    fresh = CALC.get('fresh')
    editing = CALC.get('editing')
    items = []
    hist = HIST if (fresh or not editing) else HIST[:-1]
    for e in hist:
        forms = e[1]
        note = None
        if e[2] != len(forms) - 1 and forms[-1][0] == 'a':
            note = clip('= ' + forms[-1][1], 372, 'medium')
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
            h += 18
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
                draw_string(378 - text_w(note, 'medium'), yb + ad + 2, note, GREY, 'medium')
        y += h
        n += 1
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
    dirty = True
    while True:
        if dirty:
            _draw_calc(ed, shift, alpha)
        dirty = True
        k = next_key()
        if k == SHIFT or k == ALPHA:
            if k == SHIFT:
                shift = not shift
                alpha = False
            else:
                alpha = not alpha
                shift = False
            status_mode(shift, alpha)
            show_screen()
            dirty = False
            continue
        if k == EXITK:
            wait_release()
            return
        if k == SETTINGS:
            settings()
            continue
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

def _tools(code, title, mod):
    for c, t, tools in __import__(mod).SECTIONS:
        if c == code and t == title:
            return tools
    return []

_SEL = {}       # grid title -> last tile picked, so coming back lands where you were

def remembered(title, opts):
    i = menu(title, opts, _SEL.get(title, 0))
    if i >= 0:
        _SEL[title] = i
    return i

def _tools_menu(code, title, mod):
    tools = _tools(code, title, mod)
    labels = [t[0] for t in tools]
    while True:
        sel = remembered(title, labels)
        if sel < 0:
            return
        label, spec, fn = tools[sel]
        try:
            import casutil
            casutil.run_tool(label, spec, fn)
        except Exception as e:
            flash('tool error: ' + str(e))

def qual_section(title, secs):
    labels = [t for c, t, m in secs]
    while True:
        sel = remembered(title, labels)
        if sel < 0:
            return
        _tools_menu(*secs[sel])

def paper_section(title, papers):
    labels = [name for name, code, secs in papers]
    while True:
        sel = remembered(title, labels)
        if sel < 0:
            return
        name, code, secs = papers[sel]
        qual_section(name, secs)

def formulae_section():
    import formulae
    sel = 0
    while True:
        sel = menu('Formulae', [s[0] for s in formulae.SHEETS], sel)
        if sel < 0:
            return
        title, lines = formulae.SHEETS[sel]
        show_lines(title, [('w', ln) for ln in lines])

HOME_TILES = [
    ('Calculate', ic_calc), ('CAS', ic_cas), ('Graph', ic_graph), ('Solve', ic_solve),
    ('Maths', ic_pi), ('Further', ic_argand), ('Formulae', ic_book), ('Settings', ic_angle),
]

def main():
    sel = 0
    while True:
        try:
            sel = grid('Maths Toolkit', HOME_TILES, sel)
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
                qual_section('Maths', MATHS)
            elif sel == 5:
                paper_section('Further', FURTHER)
            elif sel == 6:
                formulae_section()
            elif sel == 7:
                settings()
        except Home:
            pass
