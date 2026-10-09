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

# Settings. The calculator can't save files, so the launch script (maths.py /
# module.py) holds the defaults and passes them to main(); the Settings page
# (cfg.py) changes them until the program ends.
SET = {'further': False, 'angle': 'rad', 'answers': 'both', 'decimals': '3sf',
       'complex': 'a+bi', 'sleep': 10, 'repeat': 'normal'}
CASUTIL = [False]   # casutil has loaded: an angle change must reach it too

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
    # SETTINGS from any screen
    import cfg
    cfg.page()

KEYRATE = {'off': (0, 0), 'slow': (4500, 600), 'normal': (3000, 400), 'fast': (1800, 200)}

def configure():
    # SET -> the globals that act on it
    global DEG, IDLE, DELAY, RATE, REPEAT
    DEG = SET['angle'] == 'deg'
    if CASUTIL[0]:
        import casutil
        casutil.DEG = DEG
    m = SET['sleep']
    IDLE = 600000 * m if m > 0 else 600000 * 600
    d, r = KEYRATE.get(SET['repeat'], (3000, 400))
    DELAY = d
    RATE = r
    REPEAT = (UP, DOWN, LEFT, RIGHT, DEL) if d else ()

# ---- natural-display editor ----------------------------------------------------------

_LAST = {}      # label|spec -> the row last typed there, so going back never loses it

_INP = {}       # what the input screen shows now, for repainting only what changed

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

# ---- Calculate: history, answers stay on screen, nothing is lost going back -----------

HIST = []       # [row, forms, which form is shown]
ANS = [('n', 0)]  # last answer as an exact tree, so Ans - 2 stays exact
CALC = {}       # 'ed', 'fresh' (showing the answer to the last line), 'pos'

CAS_OPS = ['d/dx', 'd2/dx2', 'integrate', 'definite integral a..b',
           'tangent + normal at x=a', 'stationary points', 'simplify', 'expand',
           'factorise', 'partial fractions', 'solve f(x)=0', 'solve f(x)=k',
           'evaluate at x', 'table', 'plot',
           'expand trig / log', 'complete the square', 'rationalise',
           'single fraction', 'solve exact f(x)=0', 'general solution (trig)',
           'series (Maclaurin)', 'limit x -> a', 'substitute x = a',
           'rearrange for x']

# ---- the old screens (casold.py, loaded on first use) -------------------------------------
# Calculate, CAS, Solve, Graph, the tool input line and result screen, Notes
# and the old icon home live in casold.py; these names stay here so callers
# don't change. Their data (HIST, ANS, CALC, _LAST, _INP) stays here too.

def _old(name):
    import casold
    return getattr(casold, name)

def input_line(label, spec, last=''):
    return _old('input_line')(label, spec, last)

def result(label, text, lines_fn):
    return _old('result')(label, text, lines_fn)

def show_lines(title, lines):
    return _old('show_lines')(title, lines)

def calc_section():
    return _old('calc_section')()

def cas_section():
    return _old('cas_section')()

def solve_section():
    return _old('solve_section')()

def graph_section():
    return _old('graph_section')()

def notes_section():
    return _old('notes_section')()

def classic():
    return _old('classic')()

def _forms(text):
    return _old('_forms')(text)

def _cas_op(op, tree, s):
    return _old('_cas_op')(op, tree, s)

def _parse_eq(s, name=None):
    return _old('_parse_eq')(s, name)

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

_OPTS = {'angle': ('rad', 'deg'), 'answers': ('exact', 'decimal', 'both'),
         'decimals': ('3sf', '4sf', '5sf', '6sf', '1dp', '2dp', '3dp', '4dp'),
         'complex': ('a+bi', 'polar'), 'repeat': ('off', 'slow', 'normal', 'fast')}

def main(further=False, angle='rad', answers='both', decimals='3sf',
         complex='a+bi', sleep=10, repeat='normal'):
    # called by the launch script with its settings; a value it doesn't know
    # keeps the default, so a typo there can't stop the program
    got = {'angle': angle, 'answers': answers, 'decimals': decimals,
           'complex': complex, 'repeat': repeat}
    for k in got:
        v = str(got[k]).lower().replace(' ', '')
        if v in _OPTS[k]:
            SET[k] = v
    SET['further'] = further is True
    if isinstance(sleep, int) and 0 <= sleep <= 600:
        SET['sleep'] = sleep
    configure()
    import home
    home.run()
