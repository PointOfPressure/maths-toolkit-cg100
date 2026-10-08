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

# There is no clock on the calculator, so a held key is timed in key polls
# (each getkey is roughly 0.1 ms there).
REPEAT = (UP, DOWN, LEFT, RIGHT, DEL)
DELAY = 3000    # polls before a held key starts repeating
RATE = 400      # polls between repeats
_HELD = [0]     # key still down from the last press

def readkey():
    k = getkey()
    return k if k in KEYCODES else 0

def wait_release():
    while readkey():
        pass
    _HELD[0] = 0

# No key for this many polls (roughly 10-15 minutes) quits, so a forgotten
# session can't keep the calculator awake and drain the battery.
IDLE = 6000000

class Idle(BaseException):
    pass

def wait_key():
    k = readkey()
    n = 0
    while not k:
        n += 1
        if n > IDLE:
            raise Idle()
        k = readkey()
    return k

def next_key():
    k0 = _HELD[0]
    if k0:
        wait = DELAY if k0 > 0 else RATE
        k0 = abs(k0)
        rep = k0 in REPEAT
        n = 0
        while True:
            k = readkey()
            if k != k0:
                break
            n += 1
            if rep and n >= wait:
                _HELD[0] = -k0      # repeating: next gap is RATE
                return k0
        if k and k != HOME:
            _HELD[0] = k
            return k
    k = wait_key()
    _HELD[0] = k
    if k == HOME:
        wait_release()
        raise Home()
    return k

# ---- drawing ------------------------------------------------------------------

from font import cw as char_w, strw as text_w

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

# Each set_pixel costs tens of microseconds on the calculator, so: range loops,
# outlines rather than fills, and nothing big repainted per key.

def hline(x0, x1, y, c):
    sp = set_pixel
    for x in range(x0, x1 + 1):
        sp(x, y, c)

def vline(x, y0, y1, c):
    sp = set_pixel
    for y in range(y0, y1 + 1):
        sp(x, y, c)

def rect(x0, y0, x1, y1, c):
    # small fills only (indicator chips, icon details)
    sp = set_pixel
    r = range(x0, x1 + 1)
    for y in range(y0, y1 + 1):
        for x in r:
            sp(x, y, c)

def box(x0, y0, x1, y1, c):
    # rounded outline
    hline(x0 + 2, x1 - 2, y0, c)
    hline(x0 + 2, x1 - 2, y1, c)
    vline(x0, y0 + 2, y1 - 2, c)
    vline(x1, y0 + 2, y1 - 2, c)
    set_pixel(x0 + 1, y0 + 1, c); set_pixel(x1 - 1, y0 + 1, c)
    set_pixel(x0 + 1, y1 - 1, c); set_pixel(x1 - 1, y1 - 1, c)

def rbox(x0, y0, x1, y1, c):
    # filled, rounded corners; small areas only
    hline(x0 + 1, x1 - 1, y0, c)
    rect(x0, y0 + 1, x1, y1 - 1, c)
    hline(x0 + 1, x1 - 1, y1, c)

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
    hline(0, W - 1, SBH, LGREY)
    draw_string(6, 2, clip(title, 250, 'medium'), INK, 'medium')
    _SB[0] = ''
    _SB[1] = ''
    _status_right(_ind(shift, alpha), right)

CHIPX = 262

def _status_right(ind, right):
    s = right if right is not None else ('Deg' if DEG else 'Rad')
    if s != _SB[1]:
        if _SB[1]:
            draw_string(W - 6 - text_w(_SB[1], 'medium'), 2, _SB[1], WHITE, 'medium')
        draw_string(W - 6 - text_w(s, 'medium'), 2, s, ORANGE if s == 'Busy' else GREY, 'medium')
    if ind != _SB[0]:
        if ind:
            rbox(CHIPX, 2, CHIPX + 15, 17, YEL if ind == 'S' else RED)
            ctext(CHIPX + 8, 2, ind, INK if ind == 'S' else WHITE, 'medium')
        else:
            rbox(CHIPX, 2, CHIPX + 15, 17, WHITE)
    _SB[0] = ind
    _SB[1] = s

def busy():
    # top-right marker while something slow runs, like the built-in apps
    _status_right(_SB[0], 'Busy')
    show_screen()

def status_mode(shift, alpha, right=None):
    # repaint only the indicator corner when SHIFT / ALPHA changes
    ind = _ind(shift, alpha)
    s = right if right is not None else ('Deg' if DEG else 'Rad')
    if ind != _SB[0] or s != _SB[1]:
        _status_right(ind, right)
        return True
    return False

def header(title, right=None):
    status(title, False, False, right)

# ---- popup ---------------------------------------------------------------------

def flash(msg):
    # a message on its own screen; the caller redraws after
    lines = wrap(msg, 340, 'medium')[:5]
    clear_screen()
    y = 96 - 10 * len(lines)
    box(14, y - 12, W - 15, y + 20 * len(lines) + 8, RED)
    for ln in lines:
        ctext(192, y, ln, RED, 'medium')
        y += 20
    show_screen()
    next_key()
    wait_release()

class Home(BaseException):
    # HOME from anywhere: unwinds to the home grid, past tools' own handlers
    pass

# ---- grids ----------------------------------------------------------------------
# Every menu is a grid. Word tiles for lists of options, icon tiles for the home
# screen. Moving repaints the two tiles involved; scrolling repaints the body.

_WRAPS = {}     # (label, width) -> lines; wrapping is slow on the calculator

def _label_lines(label, width):
    key = (label, width)
    ls = _WRAPS.get(key)
    if ls is None:
        ls = wrap(label, width, 'medium')
        if len(ls) > 2:
            ls = [ls[0], clip(' '.join(ls[1:]), width, 'medium')]
        _WRAPS[key] = ls
    return ls

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
                self.lines.append(_label_lines(label, self.tw - 10))

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
            box(x0 + 2, y0 + 2, x1 - 2, y1 - 2, ACC)
            box(x0 + 3, y0 + 3, x1 - 3, y1 - 3, ACC)
            c = ACC
        else:
            box(x0 + 2, y0 + 2, x1 - 2, y1 - 2, LGREY)
            if not full:
                box(x0 + 3, y0 + 3, x1 - 3, y1 - 3, WHITE)
            c = INK
        y = y0 + (self.th - 18 * len(ls)) // 2
        for s in ls:
            ctext(x0 + self.tw // 2, y, s, c, 'medium')
            y += 18

    def scrollbar(self):
        if not self.bar:
            return
        x = W - 3
        vline(x, TOP, BOT, LGREY)
        span = BOT - TOP + 1
        t0 = TOP + span * self.top // self.nrows
        t1 = TOP + span * (self.top + self.rows) // self.nrows - 1
        t1 = t1 if t1 <= BOT else BOT
        vline(x, t0, t1, ACC)
        vline(x + 1, t0, t1, ACC)

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

_COLS = {}

def _cols_for(labels):
    # three across when every label fits on two lines, else two
    key = labels[0] + labels[-1] + str(len(labels))
    c = _COLS.get(key)
    if c is None:
        c = _cols3(labels)
        _COLS[key] = c
    return c

def _cols3(labels):
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
    box(x0, y0, x0 + 30, y0 + 40, (60, 70, 90))
    box(x0 + 1, y0 + 1, x0 + 29, y0 + 39, (60, 70, 90))
    box(x0 + 4, y0 + 4, x0 + 26, y0 + 13, GREEN)
    for r in range(3):
        for c in range(3):
            kx = x0 + 5 + c * 8
            ky = y0 + 18 + r * 7
            rect(kx, ky, kx + 4, ky + 3, ORANGE if (r == 2 and c == 2) else GREY)

def ic_cas(cx, cy):
    box(cx - 21, cy - 16, cx + 21, cy + 16, PURPLE)
    box(cx - 20, cy - 15, cx + 20, cy + 15, PURPLE)
    ctext(cx, cy - 14, 'd', PURPLE, 'medium')
    hline(cx - 11, cx + 11, cy + 1, PURPLE)
    ctext(cx, cy + 2, 'dx', PURPLE, 'medium')

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
    box(cx - 21, cy - 14, cx + 21, cy + 14, TEAL)
    box(cx - 20, cy - 13, cx + 20, cy + 13, TEAL)
    ctext(cx, cy - 8, 'x=?', TEAL, 'medium')

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
    box(cx - 16, cy - 19, cx + 16, cy + 19, ORANGE)
    box(cx - 15, cy - 18, cx + 15, cy + 18, ORANGE)
    vline(cx - 10, cy - 18, cy + 18, ORANGE)
    for y in (cy - 10, cy - 4, cy + 2, cy + 8):
        hline(cx - 6, cx + 10, y, (190, 140, 80))

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

_INP = {}       # what the input screen shows now, for repainting only what changed

def _chips(ed, names, y):
    # (x, y, text, colour) for the field values under the editor
    import nat
    out = []
    if not names:
        return out
    parts = _split(nat.lin(ed.root)) if ed.root else []
    cur = _field_at(ed)
    i = 0
    x = 8
    while i < len(names) and y < BOT:
        s = clip(names[i] + ' = ' + (parts[i] if i < len(parts) else ''), 118, 'medium')
        out.append((x, y, s, ACC if i == cur else (INK if i < len(parts) else LGREY)))
        x += 124
        i += 1
        if i % 3 == 0:
            x = 8
            y += 20
    return out

def _input_base(ed):
    import nat
    w, a, d = nat.measure(ed.root, 0)
    return TOP + 8 + a, a, d

def _draw_input(label, spec, ed, shift, alpha, names):
    import nat
    clear_screen()
    status(label, shift, alpha)
    base, a, d = _input_base(ed)
    if not ed.root:
        # faint hint of what goes here, gone once typing starts
        draw_string(16, base - 13, clip(spec.replace(',', ', '), 356, 'medium'), LGREY, 'medium')
    nat.draw(ed, ed.root, 8, base, 368)
    chips = _chips(ed, names, BOT - 18 - 20 * ((len(names) - 1) // 3) if names else 0)
    for x, y, t, c in chips:
        draw_string(x, y, t, c, 'medium')
    _INP['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d, chips)
    show_screen()

def _input_fast(ed, names):
    # only the typed row and changed field values are repainted
    import nat
    sh = _INP.get('shown')
    if sh is None:
        return False
    row, base, dx, caret, a0, d0, chips = sh
    w, a, d = nat.measure(ed.root, 0)
    if a != a0 or d != d0 or not row or not ed.root:
        return False
    nat.undraw(row, 8, base, dx, caret, WHITE)
    new = _chips(ed, names, chips[0][1] if chips else 0)
    i = 0
    while i < len(new):
        if i >= len(chips) or chips[i] != new[i]:
            if i < len(chips):
                x, y, t, c = chips[i]
                draw_string(x, y, t, WHITE, 'medium')
            x, y, t, c = new[i]
            draw_string(x, y, t, c, 'medium')
        i += 1
    nat.draw(ed, ed.root, 8, base, 368)
    _INP['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d, new)
    status_mode(False, False)
    show_screen()
    return True

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
    quick = False
    while True:
        if dirty and not (quick and _input_fast(ed, names)):
            _draw_input(label, spec, ed, shift, alpha, names)
        dirty = True
        quick = False
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
        quick = k != MENU and k != TOOLS
        if not edit_key(ed, k, shift, alpha) and not shift and not alpha:
            dirty = False
            continue
        shift = False
        alpha = False

# ---- result screen -------------------------------------------------------------------

def _blocks(lines, mode):
    # each line typeset (tex.py), broken to the screen width and drawn once
    # into a display list (block below).
    # ('d', block) lines come ready made (the notes, see notesui).
    import tex
    import casrender
    out = []
    for ln in _matrows(lines):
        if isinstance(ln, tuple):
            kind = ln[0]
            if (kind == 'w' or kind == 'mw') and mode == 0:
                continue
            if kind == 'd':
                out.append(ln[1])
                continue
            if kind == 'm' or kind == 'mw':
                b = casrender.flat(casrender.build(ln[1], 0))
                kind = 'a' if kind == 'm' else 'w'
            else:
                b = tex.row(ln[1])
        else:
            kind = 'a'
            b = tex.row(ln)
        x = 16 if kind == 'w' else 8
        for r, dx in tex.lines(b, 376 - x):
            out.append(block(kind, r, x + dx))
    return out

def block(kind, b, x):
    # (kind, strings, pixel runs, height, pixel ops): b drawn once into a
    # display list, so a redraw costs only the drawing
    import casrender
    if b[0] == 'atom':
        return (kind, [(x, 1, b[1], b[2])], (), 20, None)
    w, a, d = casrender.measure(b)
    if a < 13:
        a = 13
    if d < 4:
        d = 4
    strs, ops = casrender.record(b, x, a + 1)
    return (kind, merge(strs), (), a + d + 3, ops)

def merge(strs):
    # strings on one baseline in one size become one, the gaps filled with
    # spaces (moving the later text by at most 2 px): draw_string costs ~4 ms
    # however long the text, and it draws no background
    if len(strs) < 2:
        return strs
    out = []
    end = []
    last = {}
    for s in strs:
        k = s[1] * 2 + (s[3] == 'small')
        j = last.get(k)
        w = text_w(s[2], s[3])
        if j is not None:
            p = out[j]
            g = s[0] - end[j]
            sw = 4 if p[3] != 'small' else 6
            n = (g + sw - 2) // sw
            if n >= 0 and -1 <= n * sw - g <= 2:
                out[j] = (p[0], p[1], p[2] + ' ' * n + s[2], p[3])
                end[j] += n * sw + w
                continue
        last[k] = len(out)
        out.append(s)
        end.append(s[0] + w)
    return out

def play(blk, x, y, color):
    # draw a block at x, y: strings, then pixel runs (precompiled notes:
    # x, y, down, length...) or pixel ops (casrender.record)
    if blk[1] is None:
        import notesui
        notesui.unpack(blk)
    strs = blk[1]
    runs = blk[2]
    if blk[4]:
        import casrender
        casrender.play(blk[4], x, y, color)
    ds = draw_string
    for s in strs:
        ds(x + s[0], y + s[1], s[2], color, s[3])
    sp = set_pixel
    n = len(runs)
    i = 0
    while i < n:
        px = x + runs[i]
        py = y + runs[i + 1]
        k = runs[i + 3]
        if runs[i + 2]:
            for j in range(py, py + k):
                sp(px, j, color)
        else:
            for j in range(px, px + k):
                sp(j, py, color)
        i += 4

def _matrows(lines):
    # 'A = [1 2]' and then '    [3 4]' (casutil.fmtm) become one line
    # 'A = [1 2; 3 4]' that typesets as a matrix
    out = []
    for ln in lines:
        s = ln if isinstance(ln, str) else ln[1]
        if out and isinstance(s, str) and s[:1] == ' ' and s[-1:] == ']' and s.lstrip()[:1] == '[':
            p = out[-1]
            ps = p if isinstance(p, str) else p[1]
            if isinstance(ps, str) and ps[-1:] == ']' and '[' in ps and \
                    isinstance(p, str) == isinstance(ln, str) and (isinstance(p, str) or p[0] == ln[0]):
                m = ps[:-1] + '; ' + s.strip()[1:]
                out[-1] = m if isinstance(p, str) else (p[0], m)
                continue
        out.append(ln)
    return out

MODES = (None, 'working', 'full')

def _draw_result(title, sub, blocks, top, mode, more):
    clear_screen()
    status(title, False, False, MODES[mode] if more else '')
    y = TOP + 3
    i = top
    n = len(blocks)
    while i < n:
        blk = blocks[i]
        kind = blk[0]
        h = blk[3]
        if y + h > BOT + 2:
            break
        play(blk, 0, y, INK if kind == 'a' else (GREY if kind == 'w' else RED))
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
                    if more:
                        busy()
                    raw[full] = lines_fn if not more else lines_fn()
                blocks = _blocks(raw[full], mode if more else 1)
                if not blocks:
                    blocks = [('!', [(8, 1, 'nothing to show', 'medium')], (), 20, None)]
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
        return [('m', simp)]
    try:
        val = casutil.ev(tree)
    except ValueError as e:
        return [('!', str(e))]
    if isinstance(val, float) and (val > 1.7e308 or val < -1.7e308):
        return [('!', 'too large')]
    caseng.ANS = val
    ANS[0] = simp if simp is not None else ('n', val)
    seen = []
    v = casutil.clean(val)
    if simp is not None and isinstance(v, float) and caseng._ratval(simp) is not None \
            and len(caseng.tostr(simp)) > 12:
        # a long exact fraction: the plain number reads better first
        s = casutil._sf(v, 10)
        forms.append(('a', s))
        seen.append(s)
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
    clear_screen()
    status('Calculate', shift, alpha)
    fresh = CALC.get('fresh')
    editing = CALC.get('editing')
    hist = HIST if (fresh or not editing) else HIST[:-1]
    # lay out from the newest entry upwards; only what fits is measured, and a
    # history entry's layout is worked out once and kept with it
    blocks = []
    total = 0
    if not fresh:
        w, a, d = nat.measure(ed.root, 0)
        blocks.append((ed.root, None, ed, None, a, d, a + d + 4))
        total = a + d + 4
    j = len(hist) - 1
    while j >= 0:
        e = hist[j]
        if len(e) < 4:
            e.append({})
        c = e[3]
        lay = c.get(e[2])
        if lay is None:
            forms = e[1]
            note = None
            ans = _ans_box(forms[e[2]])
            w, a, d = nat.measure(e[0], 0)
            h = a + d + 4 + ans[3] + ans[4] + 4 + (18 if note else 0)
            lay = (ans, note, a, d, h)
            c[e[2]] = lay
        ans, note, a, d, h = lay
        if blocks and total + h > BOT - TOP - 2:
            break
        blocks.insert(0, (e[0], ans, None, note, a, d, h))
        total += h
        j -= 1
    y = TOP + 2
    if total > BOT - TOP - 2:
        y = BOT - total
    n = 0
    CALC['shown'] = None
    for row, ans, e, note, a, d, h in blocks:
        last = n == len(blocks) - 1
        if n:
            for x in range(6, 378, 3):
                set_pixel(x, y - 2, LGREY)
        nat.draw(e, row, 6, y + a, 370, BLACK if (e is not None or last) else GREY)
        if e is not None:
            CALC['shown'] = (nat.copy(row), y + a, nat.LAST[0], nat.LAST[1], a, d)
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

def _calc_fast(ed):
    # a key that only changed the line being typed: undraw it, draw it again
    import nat
    sh = CALC.get('shown')
    if sh is None or CALC.get('fresh'):
        return False
    row, base, dx, caret, a0, d0 = sh
    w, a, d = nat.measure(ed.root, 0)
    if a != a0 or d != d0:
        return False
    nat.undraw(row, 6, base, dx, caret, WHITE)
    nat.draw(ed, ed.root, 6, base, 370, BLACK)
    CALC['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d)
    status_mode(False, False)
    show_screen()
    return True

def calc_section():
    busy()
    import nat
    ed = CALC.get('ed')
    if ed is None:
        ed = nat.Ed()
        CALC['ed'] = ed
        CALC['pos'] = 0
    shift = False
    alpha = False
    dirty = True
    quick = False
    while True:
        if dirty and not (quick and _calc_fast(ed)):
            _draw_calc(ed, shift, alpha)
        dirty = True
        quick = False
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
        if k == TOOLS:
            # operations on the line being typed, or on the last one worked out
            row = ed.root if (ed.root and not fresh) else (HIST[-1][0] if HIST else None)
            if row and not nat.empty_hole(row):
                calc_tools(nat.lin(row))
            shift = False
            alpha = False
            continue
        if k == OK or k == EXE:
            if fresh or not ed.root:
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            busy()
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
                quick = True
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
        quick = k != MENU and k != TOOLS
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
            out = [('m', ex)]
            try:
                d = casutil.ev(ex)
                if not isinstance(d, complex):
                    out.append('integral = ' + casutil.sf3(d))
            except ValueError:
                pass
            return out + [('w', 'exact: F(b) - F(a)'),
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
        roots = cascalc.solve(d1, wide=True)
        if not roots:
            return [('!', 'no stationary points found'), ('w', cascalc.range_str())]
        d2 = _tidy(caseng.diff(d1))
        lines = []
        for r in roots:
            y = casutil.ev(tree, r)
            c = casutil.evx(d2, r)
            kind = 'min' if (c is not None and c > 1e-9) else ('max' if (c is not None and c < -1e-9) else 'inflection?')
            lines.append('(' + casutil.fmt(r) + ', ' + casutil.fmt(y) + ')  ' + kind)
        lines.append(('mw', d1))
        lines.append(('w', cascalc.range_str()))
        return lines
    if op == 6:
        return [('m', _tidy(tree))]
    if op == 7:
        return [('m', caspoly.expand(tree))]
    if op == 8:
        r = caspoly.factor(tree)
        if r is None:
            import cassolve
            r = cassolve.factor_sym(tree, 'x')
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
            top, fac = caspoly.intfactor(top, fac, power)
            den = fac
            if power > 1:
                den = ('^', fac, ('n', power))
            r = caseng._ratval(top)
            if r is not None and r[1] > 1:
                # 1/(8(3x+4)), not 1/8/(3x+4)
                top = ('n', r[0])
                den = ('*', ('n', r[1]), den)
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
        roots = cascalc.solve(target, deg=casutil.DEG, wide=True)
        if not roots:
            return [('!', 'no real roots found'), ('w', cascalc.range_str())]
        return ['x = ' + ', '.join([casutil.fmt(r) for r in roots]), ('w', cascalc.range_str())]
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
        import cascalc
        if not roots:
            return [('!', 'no solutions found'), ('w', cascalc.range_str())]
        return _roots_lines(roots, exact) + [('w', cascalc.range_str())]
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
    while True:
        s = input_line(label, spec, '')
        if s is None:
            return None
        s, tree = _parse_eq(s)
        if tree is None:
            flash('cannot read that')
            continue
        return s, tree

def _parse_eq(s):
    # 'l = r' -> l - r, the form the solvers take
    import caslex
    if '=' in s:
        l, r = s.split('=', 1)
        s = '(' + l + ')-(' + r + ')'
    return s, caslex.parse(s)

_TOOLSEL = [0]

def calc_tools(text):
    s, tree = _parse_eq(text)
    if tree is None:
        flash('cannot read that')
        return
    while True:
        op = menu('Tools', CAS_OPS, _TOOLSEL[0])
        if op < 0:
            return
        _TOOLSEL[0] = op
        _run_op(op, tree, s)

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
    busy()
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
    busy()
    while True:
        got = _read('Solve', 'equation in x (= allowed)')
        if got is None:
            return
        _run_op(19, got[1], got[0])

def graph_section():
    busy()
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
    # (label, spec) pairs from the module's small index file
    for c, t, tools in __import__('ix_' + mod).T:
        if c == code and t == title:
            return tools
    return []

def _tool_fn(code, title, mod, i):
    # the tool's function; the module itself loads on first use
    def run(*vals):
        busy()
        for c, t, tools in __import__(mod).SECTIONS:
            if c == code and t == title:
                return tools[i][2](*vals)
        raise ValueError('tool missing')
    return run

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
        label, spec = tools[sel]
        try:
            import casutil
            casutil.run_tool(label, spec, _tool_fn(code, title, mod, sel))
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

# Notes: the AQA formula booklet, then revision notes per paper. Paper names
# and their modules live here so the first menu needs no import; the topic
# menus and pages are in notesui.py (with the index notes_ix.py), and a notes
# module loads only when one of its topics is opened.
NOTE_PAPERS = (
    ('Formula booklet', ()),
    ('Pure 7357', ('notes_mp1', 'notes_mp2', 'notes_mp3')),
    ('Stats 7357', ('notes_ms',)),
    ('Mechanics 7357', ('notes_mm',)),
    ('Core Pure Y420', ('notes_cp1', 'notes_cp2', 'notes_cp3')),
    ('Stats Y422', ('notes_st1', 'notes_st2')),
    ('Extra Pure Y435', ('notes_xp',)),
)

def notes_section():
    labels = [p[0] for p in NOTE_PAPERS]
    while True:
        sel = remembered('Notes', labels)
        if sel < 0:
            return
        name, mods = NOTE_PAPERS[sel]
        if mods:
            busy()
            import notesui
            notesui.paper(name)
        else:
            _booklet(name)

def _booklet(name):
    busy()
    import tn_fb
    import notesui
    while True:
        sel = remembered(name, tn_fb.T)
        if sel < 0:
            return
        notesui.show(tn_fb.T[sel], tn_fb.N[sel])

HOME_TILES = [
    ('Calculate', ic_calc), ('CAS', ic_cas), ('Graph', ic_graph), ('Solve', ic_solve),
    ('Maths', ic_pi), ('Further', ic_argand), ('Notes', ic_book), ('Settings', ic_angle),
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
                notes_section()
            elif sel == 7:
                settings()
        except Home:
            pass
        except Idle:
            clear_screen()
            show_screen()
            return
        except MemoryError:
            del HIST[:-3]
            _WRAPS.clear()
            flash('out of memory - cleared history')
        except Exception as e:
            flash('error: ' + str(e))
