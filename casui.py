# casui.py - front end for the visual Maths Toolkit (Casio fx-CG100, stock
# MicroPython). Type on the real keys; see a live 2D preview (Desmos-style).
# Then Differentiate / Integrate / Simplify / Solve / Evaluate / Graph.
# Imports caslex, caseng, casrender, cascalc. EXIT at the top menu quits.
#
# Key codes are row*10+col, which is Casio's documented scheme. The map below
# is the key-code diagram on page 142 of the fx-CG100 Software User's Guide
# (v2.10) read against the printed keytops; keyprobe.py re-checks it on a
# device. Note that [ON] and [AC] are assigned no key code at all, so getkey
# cannot see them - quitting has to be on EXIT.
from casioplot import *
import caslex
import caseng
import casrender
import cascalc
import caspoly

# Every code the keypad can produce (page 142's diagram: 9 rows, cols 1-6, with
# row 1 col 1 = [ON] and row 6 col 5 = [AC] carrying no code, and rows 7-9
# stopping at col 5). The manual does not state what getkey returns when no key
# is held, so the toolkit does not depend on knowing: anything outside this set
# is idle. Sampling getkey() once at import to learn the idle value was wrong
# twice over - the key that launched the script is still down at import, which
# made that key permanently unreadable for the rest of the session.
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

def readkey():
    # the code of the key held now, or 0 for none
    k = getkey()
    return k if k in KEYCODES else 0

WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
ACC   = (40, 120, 220)
GREY  = (150, 150, 160)
HL    = (225, 232, 250)
RED   = (205, 60, 60)

# Key codes are row*10+col. Taken from the key-code diagram in Casio's fx-CG100
# manual, cross-referenced against the printed keypad; tests.py holds the same
# table independently and asserts these maps agree with it. [ON] (row 1 col 1)
# and [AC] (row 6 col 5) are assigned no code at all and cannot be read.
HOME = 12; LINESTART = 13; UP = 14; LINEEND = 15; PAGEUP = 16
SETTINGS = 21; EXITK = 22; LEFT = 23; OK = 24; RIGHT = 25; PAGEDOWN = 26
SHIFT = 31; ALPHA = 32; VARIABLE = 33; DOWN = 34; MENU = 35; TOOLS = 36
DEL = 64; FORMAT = 94; EXE = 95
UNSHIFT = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.',
    84: '+', 85: '-', 74: '*', 75: '/', 44: '^', 55: '(', 56: ')',
    41: 'x', 33: 'x', 42: '/', 45: '^2', 46: 'exp(', 93: '*10^',
    52: 'sin(', 53: 'cos(', 54: 'tan(', 43: 'sqrt(',
    51: ',',            # the comma has its own key - it was simply never bound
}
# green SHIFT legends: sin^-1 / cos^-1 / tan^-1 sit above the trig keys, and
# the power key's shifted form is a log to a given base
SHIFTED = {
    55: '=', 46: 'ln(', 45: 'log(', 61: 'pi',
    52: 'asin(', 53: 'acos(', 54: 'atan(', 44: 'logb(',
}
# digit keys, for jumping straight to a numbered menu entry
DIGITS = {81: 1, 82: 2, 83: 3, 71: 4, 72: 5, 73: 6, 61: 7, 62: 8, 63: 9, 91: 0}
# ALPHA + key -> the orange letter printed on that key. This ran a whole row out
# of step: 42 gave 'a' when the key is printed B, so every letter from B to F and
# V to X came out as its neighbour, and A, G-L, U and Y had no key at all.
ALPHADICT = {
    41: 'a', 42: 'b', 43: 'c', 44: 'd', 45: 'e', 46: 'f',
    51: 'g', 52: 'h', 53: 'i', 54: 'j', 55: 'k', 56: 'l',
    61: 'm', 62: 'n', 63: 'o',
    71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    81: 'u', 82: 'v', 83: 'w', 84: 'x', 85: 'y',
    91: 'z', 94: 'ans',
}
# CATALOG picker - a paged grid for the tokens the keypad genuinely has no key
# for: factorial, abs, nCr/nPr and the six hyperbolic names. Everything else now
# comes off a real key, so the picker stays down to a single page.
# tests.py asserts every documented token stays reachable one way or another.
PAL_COLS = 4
PAL_ROWS = 3
PAL_PER = PAL_COLS * PAL_ROWS
EXTRAS = [
    '!', 'abs(', 'nCr(', 'nPr(',
    'sec(', 'cosec(', 'cot(', 'ans',
    'sinh(', 'cosh(', 'tanh(', ',',
    'asinh(', 'acosh(', 'atanh(', 'logb(',
    'sech(', 'cosech(', 'coth(', 'pi',
]

# global angle mode for Calculate + CAS evaluate/graph/table (FM modules stay radians)
ANGLE_DEG = False

def wait_release():
    while readkey():
        pass

def wait_press():
    while not readkey():
        pass

def rect(x0, y0, x1, y1, c):
    sp = set_pixel
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            sp(x, y, c)
            x += 1
        y += 1

def hline(x0, x1, y, c):
    sp = set_pixel
    x = x0
    while x <= x1:
        sp(x, y, c)
        x += 1

def frame(x0, y0, x1, y1, c):
    hline(x0, x1, y0, c)
    hline(x0, x1, y1, c)
    yy = y0
    while yy <= y1:
        set_pixel(x0, yy, c)
        set_pixel(x1, yy, c)
        yy += 1

def fmt(v):
    if v != v:
        return "undefined"       # int() raises on nan/inf
    if v > 1.7e308:
        return "inf"
    if v < -1.7e308:
        return "-inf"
    r = round(v, 6)
    if r == int(r):
        return str(int(r))
    return str(r)

# ---------- proportional font metrics (measured on the fx-CG100) ----------
# medium: narrow glyph ~8px, normal ~10px, wide ~12px, prose avg ~8.8px/char.
# small is ~0.68 of that. Slightly conservative so a line never overflows.
_WIDE = "mwMW@%"
_NARROW = " iIjl1tfr.,;:!'|()[]{}/-"

def char_w(c, size):
    if size == "small":
        if c in _WIDE:
            return 8
        if c in _NARROW:
            return 5
        return 7
    if size == "large":
        # large glyphs are ~1.75x medium; without this branch every "large"
        # measurement silently used medium widths and under-measured the line
        if c in _WIDE:
            return 21
        if c in _NARROW:
            return 14
        return 18
    if c in _WIDE:
        return 12
    if c in _NARROW:
        return 8
    return 10

def text_w(s, size):
    w = 0
    for c in s:
        w += char_w(c, size)
    return w

def tail_fit(s, maxpx, size):
    # drop leading chars until the string fits in maxpx (for scrolling input)
    while s and text_w(s, size) > maxpx:
        s = s[1:]
    return s

def cursor_fit(s, cpos, maxpx, size):
    # Window s so the character at cpos stays on screen. Trimming only from the
    # left (tail_fit) scrolled the cursor off as soon as you moved back into a
    # long line, leaving you editing blind.
    if text_w(s, size) <= maxpx:
        return s
    if cpos > len(s):
        cpos = len(s)
    lo = cpos
    hi = cpos + 1 if cpos < len(s) else cpos
    w = char_w(s[cpos], size) if cpos < len(s) else 0
    while True:
        grew = False
        if hi < len(s) and w + char_w(s[hi], size) <= maxpx:
            w += char_w(s[hi], size)
            hi += 1
            grew = True
        if lo > 0 and w + char_w(s[lo - 1], size) <= maxpx:
            lo -= 1
            w += char_w(s[lo], size)
            grew = True
        if not grew:
            return s[lo:hi]

def wrap_px(s, maxpx, size):
    # greedy WORD wrap to a pixel width; hard-splits any single word too long.
    out = []
    line = ""
    lw = 0
    sw = char_w(" ", size)
    for word in s.split(" "):
        ww = text_w(word, size)
        if line == "":
            if ww <= maxpx:
                line = word
                lw = ww
            else:
                part = ""
                pw = 0
                for c in word:
                    cw = char_w(c, size)
                    if pw + cw > maxpx and part:
                        out.append(part)
                        part = ""
                        pw = 0
                    part += c
                    pw += cw
                line = part
                lw = pw
        elif lw + sw + ww <= maxpx:
            line += " " + word
            lw += sw + ww
        else:
            out.append(line)
            line = word
            lw = ww
    if line:
        out.append(line)
    return out

# ---------- input with live 2D preview ----------
def draw_palette(psel):
    page = psel // PAL_PER
    pages = (len(EXTRAS) + PAL_PER - 1) // PAL_PER
    rect(4, 100, 379, 190, HL)
    frame(4, 100, 379, 190, ACC)
    draw_string(10, 103, "pick a symbol", ACC, "small")
    draw_string(250, 103, "EXIT closes   " + str(page + 1) + "/" + str(pages), GREY, "small")
    i = page * PAL_PER
    last = i + PAL_PER
    while i < len(EXTRAS) and i < last:
        r = (i - page * PAL_PER) // PAL_COLS
        c = (i - page * PAL_PER) % PAL_COLS
        x = 10 + c * 92
        y = 120 + r * 23
        if i == psel:
            rect(x - 4, y - 3, x + 86, y + 18, (198, 214, 246))
            frame(x - 4, y - 3, x + 86, y + 18, ACC)
        draw_string(x, y, EXTRAS[i], BLACK, "medium")
        i += 1

def draw_input(prompt, ex, cur, shift, alpha, palette, psel):
    clear_screen()
    draw_string(6, 3, prompt, GREY, "small")
    if shift:
        draw_string(322, 3, "SHIFT", ACC, "small")
    elif alpha:
        draw_string(322, 3, "ALPHA", (210, 120, 30), "small")
    else:
        # the angle mode changes what sin(30) means, so keep it in sight
        draw_string(340, 3, "DEG" if ANGLE_DEG else "RAD", GREY, "small")
    s = "".join(ex)
    tree = None
    if s:
        try:
            tree = caslex.parse(s)
        except:
            tree = None
    if tree is not None:
        if not casrender.render(tree, 8, 18, 376, 96, BLACK):
            draw_string(8, 50, tail_fit(s, 368, "medium"), BLACK, "medium")
    elif s:
        draw_string(8, 50, tail_fit(s, 368, "medium"), GREY, "medium")
    else:
        draw_string(8, 50, "...", GREY, "medium")
    hline(0, 383, 108, GREY)
    raw = "".join(ex[:cur]) + "|" + "".join(ex[cur:])
    draw_string(8, 120, cursor_fit(raw, len("".join(ex[:cur])), 368, "medium"), BLACK, "medium")
    draw_string(6, 178, "OK run  DEL del  UP last  CATALOG symbols", GREY, "small")
    if palette:
        draw_palette(psel)
    show_screen()

_last_expr = []   # most recent submitted entry, recalled with UP

def input_expr(prompt):
    global _last_expr
    ex = []
    cur = 0
    shift = False
    alpha = False
    palette = False
    psel = 0
    draw_input(prompt, ex, cur, shift, alpha, palette, psel)
    while True:
        k = readkey()
        if not k:
            continue
        if palette:
            if k == LEFT:
                psel = (psel - 1) % len(EXTRAS)
            elif k == RIGHT:
                psel = (psel + 1) % len(EXTRAS)
            elif k == UP:
                psel = (psel - PAL_COLS) % len(EXTRAS)
            elif k == DOWN:
                psel = (psel + PAL_COLS) % len(EXTRAS)
            elif k == PAGEUP:
                psel = (psel - PAL_PER) % len(EXTRAS)
            elif k == PAGEDOWN:
                psel = (psel + PAL_PER) % len(EXTRAS)
            elif k == OK or k == EXE:
                ex.insert(cur, EXTRAS[psel]); cur += 1; palette = False
            elif k == MENU or k == EXITK:
                palette = False
            wait_release()
            draw_input(prompt, ex, cur, shift, alpha, palette, psel)
            continue
        if k == SHIFT:
            shift = not shift; alpha = False
        elif k == ALPHA:
            alpha = not alpha; shift = False
        elif k == MENU:
            palette = True; psel = 0
        elif k == LEFT:
            if cur > 0:
                cur -= 1
        elif k == RIGHT:
            if cur < len(ex):
                cur += 1
        elif k == LINESTART:
            cur = 0            # the key is printed |<-, so it does what it says
        elif k == LINEEND:
            cur = len(ex)      # and ->|
        elif k == UP:
            # recall the last entry instead of retyping a long expression
            if _last_expr:
                ex = list(_last_expr); cur = len(ex)
        elif k == DOWN:
            ex = []; cur = 0
        elif k == DEL:
            if cur > 0:
                ex.pop(cur - 1); cur -= 1
        elif k == EXITK:
            if not ex:
                wait_release()
                return None
            ex = []; cur = 0
        elif k == OK or k == EXE:
            if ex:
                wait_release()
                _last_expr = list(ex)
                return "".join(ex)
        else:
            if alpha:
                tok = ALPHADICT.get(k, None)
            elif shift:
                tok = SHIFTED.get(k, None)
            else:
                tok = UNSHIFT.get(k, None)
            if tok is not None:
                ex.insert(cur, tok); cur += 1
            shift = False
            alpha = False
        wait_release()
        draw_input(prompt, ex, cur, shift, alpha, palette, psel)

# ---------- menu ----------
def draw_menu(title, opts, sel):
    clear_screen()
    draw_string(8, 6, title, ACC, "medium")
    hline(0, 383, 26, GREY)
    n = len(opts)
    per = 7
    half = per // 2
    if n <= per:
        top = 0
    elif sel < half:
        top = 0
    elif sel > n - 1 - half:
        top = n - per
    else:
        top = sel - half
    r = 0
    while r < per and top + r < n:
        i = top + r
        y = 30 + r * 20
        if i == sel:
            rect(6, y - 1, 372, y + 16, HL)
            frame(6, y - 1, 372, y + 16, ACC)
        # number each visible row so it can be jumped to with a digit key
        draw_string(14, y, str(i + 1) + "  " + opts[i] if i < 9 else "   " + opts[i],
                    BLACK, "medium")
        r += 1
    draw_string(8, 178, "EXIT back   1-9 jump", GREY, "small")
    if n > per:
        draw_string(318, 178, str(sel + 1) + "/" + str(n), GREY, "small")
        if top > 0:
            draw_string(366, 30, "^", ACC, "medium")
        if top + per < n:
            draw_string(366, 150, "v", ACC, "medium")
    show_screen()

def menu(title, opts):
    if not opts:
        return -1  # nothing to choose: never divide by len(opts) == 0
    sel = 0
    draw_menu(title, opts, sel)
    while True:
        k = readkey()
        if not k:
            continue
        if k == UP:
            sel = (sel - 1) % len(opts)
        elif k == DOWN:
            sel = (sel + 1) % len(opts)
        elif k == LEFT or k == LINESTART:
            sel = 0
        elif k == RIGHT or k == LINEEND:
            sel = len(opts) - 1
        elif k == PAGEUP:
            sel = sel - 7 if sel >= 7 else 0
        elif k == PAGEDOWN:
            sel = sel + 7 if sel + 7 < len(opts) else len(opts) - 1
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
        else:
            # a digit key picks that entry outright - a 13-tool section took
            # twelve presses of DOWN to reach the last item
            d = DIGITS.get(k, None)
            if d is not None and 1 <= d <= len(opts):
                wait_release()
                return d - 1
        wait_release()
        draw_menu(title, opts, sel)

# ---------- results ----------
def hold():
    draw_string(6, 178, "Press any key", GREY, "small")
    show_screen()
    wait_release()
    wait_press()
    wait_release()

def hold_page():
    # like hold(), but reports whether the user asked to stop paging
    draw_string(6, 178, "any key = more   EXIT = stop", GREY, "small")
    show_screen()
    wait_release()
    k = readkey()
    while not k:
        k = readkey()
    wait_release()
    return k == EXITK

PER_PAGE = 7

def _paged(title, segs, color):
    # Draw already-wrapped lines a screenful at a time. Long output used to be
    # cut off at the 8th line with nothing to say it had been truncated.
    if not segs:
        segs = [""]
    total = len(segs)
    pages = (total + PER_PAGE - 1) // PER_PAGE
    p = 0
    while p < pages:
        clear_screen()
        draw_string(6, 6, title, ACC, "medium")
        hline(0, 383, 26, GREY)
        y = 34
        i = p * PER_PAGE
        last = i + PER_PAGE
        while i < total and i < last:
            draw_string(6, y, segs[i], color, "medium")
            y += 18
            i += 1
        if pages > 1:
            draw_string(322, 178, str(p + 1) + "/" + str(pages), GREY, "small")
        p += 1
        if p < pages:
            if hold_page():
                return
        else:
            hold()

def show_text(title, body, color):
    _paged(title, wrap_px(body, 372, "medium"), color)

def result_screen(title, lines):
    # shared result view for the section modules: full-width pixel wrap, paged
    segs = []
    for ln in lines:
        for seg in wrap_px(ln, 372, "medium"):
            segs.append(seg)
    _paged(title, segs, BLACK)

def show_math(title, tree):
    clear_screen()
    draw_string(6, 6, title, ACC, "medium")
    hline(0, 383, 26, GREY)
    if not casrender.render(tree, 6, 32, 378, 162, BLACK):
        # too big to typeset: fall back to the paged plain-text form
        show_text(title, caseng.tostr(tree), BLACK)
        return
    hold()

GTOP = 14      # first pixel row below the header
GBOT = 172     # last pixel row above the footer

def _gline(x0, y0, x1, y1, c):
    # Bresenham, clipped to the plot band
    dx = x1 - x0 if x1 >= x0 else x0 - x1
    dy = y1 - y0 if y1 >= y0 else y0 - y1
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    err = dx - dy
    while True:
        if 0 <= x0 <= 383 and GTOP <= y0 <= GBOT:
            set_pixel(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def _yrange(vals):
    # robust y window: trim the extreme 5% at each end so a single asymptote
    # (1/x, tan x) cannot flatten the whole curve into one pixel row
    vs = sorted(vals)
    n = len(vs)
    lo = vs[n // 20]
    hi = vs[n - 1 - n // 20]
    if hi - lo < 1e-9:
        lo -= 1.0
        hi += 1.0
    pad = (hi - lo) * 0.08
    return lo - pad, hi + pad

def graph(tree):
    XLO = -12.0
    XHI = 12.0
    xs = []
    ys = []
    px = 0
    while px < 384:
        xv = XLO + (XHI - XLO) * px / 383.0
        try:
            yv = caseng.evalf(tree, xv, ANGLE_DEG)
            if yv != yv or yv > 1e300 or yv < -1e300:
                yv = None
        except:
            yv = None
        xs.append(px)
        ys.append(yv)
        px += 1
    fin = [v for v in ys if v is not None]
    if not fin:
        show_text("Graph", "f(x) has no plottable values on -12 <= x <= 12.", RED)
        return
    ylo, yhi = _yrange(fin)
    span = yhi - ylo
    clear_screen()
    # axes
    if ylo <= 0.0 <= yhi:
        ay = int(GBOT - (0.0 - ylo) / span * (GBOT - GTOP))
        hline(0, 383, ay, GREY)
    axx = int((0.0 - XLO) / (XHI - XLO) * 383.0)
    yy = GTOP
    while yy <= GBOT:
        set_pixel(axx, yy, GREY)
        yy += 1
    # curve, joining consecutive finite samples
    prev = None
    i = 0
    while i < len(xs):
        v = ys[i]
        if v is None:
            prev = None
            i += 1
            continue
        cy = int(GBOT - (v - ylo) / span * (GBOT - GTOP))
        if cy < GTOP - 40 or cy > GBOT + 40:
            prev = None      # far off-screen: do not draw a false vertical join
            i += 1
            continue
        if prev is not None:
            _gline(prev[0], prev[1], xs[i], cy, ACC)
        elif GTOP <= cy <= GBOT:
            set_pixel(xs[i], cy, ACC)
        prev = (xs[i], cy)
        i += 1
    draw_string(4, 1, "y = f(x)   " + ("DEG" if ANGLE_DEG else "RAD"), GREY, "small")
    draw_string(4, 176, "x[-12,12]  y[" + fmt(ylo) + "," + fmt(yhi) + "]", GREY, "small")
    hold()

def do_solve(s):
    if '=' in s:
        p = s.split('=', 1)
        l = caslex.parse(p[0])
        r = caslex.parse(p[1])
        t = ('-', l, r) if (l is not None and r is not None) else None
    else:
        t = caslex.parse(s)
    if t is None:
        show_text("Solve", "Could not read equation", RED)
        return
    roots = cascalc.solve(t, deg=ANGLE_DEG)
    if not roots:
        show_text("Solve", "No real roots found in the search range.", BLACK)
        return
    parts = []
    for rt in roots:
        parts.append(fmt(rt))
    show_text("Solve  f(x)=0", "x = " + ",  ".join(parts), BLACK)

def do_eval(tree):
    xv = _ask_value("Value for x:")
    if xv is None:
        return
    try:
        res = caseng.evalf(tree, xv, ANGLE_DEG)
        show_text("Evaluate", "f(" + fmt(xv) + ") = " + _fmt_num(res), BLACK)
    except:
        show_text("Evaluate", "Math error (domain?)", RED)

# ---------- per-section help (shown once per session) ----------
HELP = {
    "calc": "Everyday calculator. Type any sum and press OK for the answer. Works: + - * /, ^, brackets, sqrt, sin/cos/tan and asin/acos/atan, ln, log, exp, abs, n! (factorial), nCr(n,r), nPr(n,r), pi, e. Use 'ans' for your last answer. Switch DEG/RAD from the home menu (Angle mode).",
    "cas": "Algebra & calculus on a function of x. Type e.g. x^2+3x or sin(x), press OK, then pick: d/dx, gradient at a point, integrate (products like x sin(x) and x ln(x) are done by parts, and proper fractions like x/((x+1)(x-2)) by partial fractions), definite integral a..b, simplify, expand brackets, factorise, collect like terms, partial fractions (type it as one fraction), solve f(x)=0, evaluate, graph, or a table of values. Type letters other than x with ALPHA; the CATALOG key gives the symbols with no key of their own. Evaluate/graph/table/solve follow the home-menu angle mode; calculus uses radians.",
    "vcplx": "Complex numbers a+bi. Enter the real then imaginary part. Tools: + - * /, modulus & argument, polar form, powers, nth roots, Argand.",
    "matrix": "Matrices up to 3x3. First Enter A (give the size, then each number). Then pick add, multiply, determinant, inverse, solve Ax=b, eigenvalues.",
    "vectors": "Vectors in 3-D. Enter components (use 0 for 2-D). Tools: magnitude, dot, angle, cross product, projection, distance to a line or plane.",
    "polyroots": "Roots of polynomials. Enter the coefficients. Vieta gives the sums/products of roots; also quadratic roots and numeric roots.",
    "series": "Series & Maclaurin. Sums of r, r^2, r^3 up to n. Maclaurin expands a function (e.g. sin(x)) to N terms, with the approximation and error.",
    "hyper": "Hyperbolic functions. Evaluate sinh, cosh, tanh and their inverses at a value, plus a reference card of identities and integrals.",
    "polar": "Polar coordinates. Convert (r,theta) and (x,y). Plot r=f(theta) - type theta as x, e.g. 1+cos(x). Area = half integral of r^2 dtheta.",
    "diffeq": "Differential equations. Integrating factor (1st order). 2nd order: enter a,b for the equation to get the complementary function. SHM, damping.",
    "fmmech": "Further Mechanics. Momentum & impulse, collisions (e), work/energy/power, circular motion, Hooke's law, centre of mass, dimensions.",
    "fmstat": "Further Statistics. Poisson, binomial, Normal; PMCC, Spearman, regression; chi-squared test; confidence intervals; z-test.",
    "numeric": "Numerical Methods. Solve f(x)=0 (Newton-Raphson, bisection). Integrate (trapezium, Simpson). Numerical differentiation, Euler's method.",
    "algos": "Algorithms. Sort a list, bin-packing, shortest path (Dijkstra), minimum spanning tree (Prim/Kruskal), critical path. Enter the data asked.",
    "xpure": "Extra Pure. Recurrence relations, group theory (Cayley tables), 2x2 eigenvalues/vectors, modular arithmetic (gcd, mod power, inverse).",
    "fpt": "Further Pure with Tech. Plot curves, complex De Moivre & roots, Euler's method, number theory (gcd, primes, factorising, modular).",
    "pure640": "Pure (A-Level). Quadratics, simultaneous equations, sequences & series, binomial, logs, coordinate geometry & circles, trig and R-form.",
    "stat640": "Statistics (A-Level). Summary stats, frequency tables, discrete random variables, binomial & Normal, hypothesis tests, PMCC & regression.",
    "purecalc": "Pure functions and calculus techniques. Composite fg(x) and inverse functions, domain and range, the modulus function, graph transformations, parametric and implicit differentiation, integration by substitution (you choose u), small-angle approximations and the exact trig values. Type t as t and y as y with ALPHA.",
    "proof": "Proof. A calculator cannot write a proof, but it can check the step you are about to claim. Induction for sums, divisibility and M^n: it verifies the base case and then the inductive step symbolically. Disproof by counterexample searches a range for one. Plus a reference card for direct proof, exhaustion, contradiction and induction.",
    "mech640": "Mechanics (A-Level). SUVAT (enter any 3 of u,v,a,s,t), projectiles, forces & resolving, friction on slopes, pulleys, moments.",
}
_helped = []

def show_help(key):
    if key in _helped:
        return
    _helped.append(key)
    h = HELP.get(key, None)
    if h is not None:
        show_text("How to use", h, BLACK)

# ---------- calculate (everyday scientific calculator) ----------
def _bad_result(v):
    # reject anything that is not a finite real number (complex, NaN, inf, overflow)
    if not isinstance(v, (int, float)):
        return True
    if isinstance(v, float):
        if v != v:
            return True
        av = v if v >= 0 else -v
        if av > 1e308:
            return True
    return False

def _sci(v):
    neg = v < 0
    if neg:
        v = -v
    e = 0
    while v >= 10.0 and e < 400:
        v /= 10.0
        e += 1
    while v != 0 and v < 1.0 and e > -400:
        v *= 10.0
        e -= 1
    out = str(round(v, 6)) + "e" + str(e)
    return "-" + out if neg else out

def _fmt_num(v):
    if not isinstance(v, (int, float)):
        return "undefined"
    if isinstance(v, int):
        return str(v)
    if v != v:
        return "undefined"
    av = v if v >= 0 else -v
    if av > 1e308:
        return "overflow"
    if av != 0 and (av >= 1e12 or av < 1e-5):
        return _sci(v)
    r = round(v, 9)
    if r == int(r):
        return str(int(r))
    return str(round(v, 10))

def _ask_value(prompt):
    s = input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0, ANGLE_DEG)
    except:
        return None

def _calc_result(s, tree, val):
    clear_screen()
    draw_string(6, 6, "Calculate", ACC, "medium")
    draw_string(330, 8, "DEG" if ANGLE_DEG else "RAD", GREY, "small")
    hline(0, 383, 26, GREY)
    if not casrender.render(tree, 6, 32, 378, 84, BLACK):
        draw_string(6, 44, tail_fit(s, 368, "medium"), GREY, "medium")
    hline(0, 383, 92, GREY)
    ans = _fmt_num(val)
    exact = None
    try:
        simp = caseng.simplify(tree)
        es = caseng.tostr(simp)
        if (simp[0] == '/' or simp[0] == 'n') and es != ans and len(es) <= 28:
            exact = es
    except:
        exact = None
    draw_string(6, 104, "=", ACC, "medium")
    if text_w(ans, "large") <= 350:
        draw_string(28, 104, ans, BLACK, "large")
    elif text_w(ans, "medium") <= 350:
        draw_string(28, 108, ans, BLACK, "medium")
    else:
        yy = 104
        for ln in wrap_px(ans, 356, "medium"):
            draw_string(28, yy, ln, BLACK, "medium")
            yy += 18
    if exact is not None:
        draw_string(6, 150, "exact: " + exact, GREY, "medium")
    hold()

def calc_section():
    show_help("calc")
    while True:
        s = input_expr("Calculate (ans = last):")
        if s is None:
            return
        tree = caslex.parse(s)
        if tree is None:
            show_text("Calculate", "Could not read: " + s, RED)
            continue
        try:
            val = caseng.evalf(tree, 0.0, ANGLE_DEG)
        except:
            show_text("Calculate", "Math error - check brackets and that values are in the function's domain.", RED)
            continue
        if _bad_result(val):
            show_text("Calculate", "Result is undefined or too large.", RED)
            continue
        caseng.ANS = val
        _calc_result(s, tree, val)

def do_gradient(tree):
    a = _ask_value("Gradient at x =")
    if a is None:
        return
    # scale the step with |a|: a fixed 1e-5 vanishes into the rounding of a
    # large x (a + h == a), which silently reported a gradient of 0
    h = 1e-5 * (abs(a) if abs(a) > 1.0 else 1.0)
    try:
        g = (caseng.evalf(tree, a + h, ANGLE_DEG) - caseng.evalf(tree, a - h, ANGLE_DEG)) / (2 * h)
        show_text("Gradient (slope)", "f'(" + fmt(a) + ") = " + _fmt_num(g), BLACK)
    except:
        show_text("Gradient", "Math error (domain?)", RED)

def do_defint(tree):
    a = _ask_value("Lower limit a =")
    if a is None:
        return
    b = _ask_value("Upper limit b =")
    if b is None:
        return
    v = cascalc.defint(tree, a, b, ANGLE_DEG)
    if v is None:
        show_text("Definite integral", "Could not evaluate (check the domain over a..b).", RED)
    else:
        show_text("Definite integral", "Area from " + fmt(a) + " to " + fmt(b) + " = " + _fmt_num(v), BLACK)

def do_table(tree):
    start = _ask_value("Table: start x =")
    if start is None:
        return
    step = _ask_value("Table: step =")
    if step is None:
        return
    lines = []
    i = 0
    while i < 8:
        xv = start + i * step
        try:
            yv = caseng.evalf(tree, xv, ANGLE_DEG)
            lines.append("x = " + fmt(xv) + "    f(x) = " + _fmt_num(yv))
        except:
            lines.append("x = " + fmt(xv) + "    f(x) = undefined")
        i += 1
    result_screen("Table of values", lines)

def do_partial(tree):
    # Split a rational function into partial fractions. H640 Pure asks for
    # denominators that are products of distinct linear factors or have a
    # repeated linear factor; the engine also does an irreducible quadratic.
    if tree[0] != '/':
        show_text("Partial fractions",
                  "Type this as one fraction, for example (3x+5)/((x-1)(x+2)).", RED)
        return
    try:
        res = caspoly.partial(tree[1], tree[2])
    except:
        res = None
    if res is None:
        show_text("Partial fractions",
                  "Cannot split this exactly. The top and bottom must both be "
                  "polynomials with whole-number or fractional coefficients, and "
                  "the bottom must factorise into linear or quadratic factors.", RED)
        return
    quot, terms = res
    lines = []
    if quot is not None:
        lines.append("whole part:  " + caseng.tostr(quot))
    if not terms:
        lines.append("(divides exactly - no fractions left)")
    for top, fac, power in terms:
        den = caseng.tostr(fac)
        if power > 1:
            den = "(" + den + ")^" + str(power)
        lines.append("  " + caseng.tostr(top) + "  /  " + den)
    result_screen("Partial fractions", lines)

# ---------- main ----------
def cas_section():
    show_help("cas")
    while True:
        s = input_expr("Type an expression:")
        if s is None:
            return
        tree = caslex.parse(s)
        if tree is None:
            show_text("Parse error", "Could not read: " + s, RED)
            continue
        # Stay on the same f(x) until the user asks for a new one. Returning to
        # the editor after every operation meant retyping the expression to
        # differentiate it and then integrate it.
        while True:
            op = menu("f(x) = " + s, ["Differentiate  d/dx", "Gradient at a point",
                                       "Integrate (+ C)", "Definite integral a..b",
                                       "Simplify", "Expand brackets", "Factorise",
                                       "Collect like terms", "Partial fractions",
                                       "Solve  f(x)=0", "Evaluate at x",
                                       "Graph", "Table of values", "New expression"])
            if op == -1 or op == 13:
                break
            if op == 0:
                try:
                    show_math("d/dx =", cascalc.tidy(caseng.diff(tree)))
                except ValueError as e:
                    show_text("Differentiate", str(e) + " - there is no elementary derivative for this.", RED)
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 1:
                do_gradient(tree)
            elif op == 2:
                try:
                    r = cascalc.integ(tree)
                    if r is None:
                        show_text("Integrate", "No elementary form - try the Definite integral for a numeric area.", RED)
                    else:
                        show_math("Integral (+ C)", cascalc.tidy(r))
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 3:
                do_defint(tree)
            elif op == 4:
                try:
                    show_math("Simplified", cascalc.tidy(tree))
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 5:
                try:
                    show_math("Expanded", caspoly.expand(tree))
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 6:
                try:
                    r = caspoly.factor(tree)
                    if r is None:
                        show_text("Factorise", "This does not factorise over the rationals - it may still factorise with surds.", RED)
                    else:
                        show_math("Factorised", r)
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 7:
                try:
                    show_math("Collected", caspoly.collect(tree))
                except:
                    show_text("Too complex", "Nests too deep", RED)
            elif op == 8:
                do_partial(tree)
            elif op == 9:
                do_solve(s)
            elif op == 10:
                do_eval(tree)
            elif op == 11:
                graph(tree)
            elif op == 12:
                do_table(tree)

# proof.py appears in both menus on purpose: induction is Core Pure, but
# contradiction and disproof by counterexample are H640, and a student should
# not have to know which paper a proof technique belongs to in order to find it.
FM_CORE_LABELS = ["Complex numbers", "Matrices", "Vectors & 3-D", "Roots of polynomials",
                  "Series & Maclaurin", "Hyperbolic functions", "Polar coordinates",
                  "Differential equations", "Proof & induction"]
FM_CORE_MODS = ["vcplx", "matrix", "vectors", "polyroots", "series", "hyper", "polar",
                "diffeq", "proof"]
FM_OPT_LABELS = ["Mechanics (FM)", "Statistics (FM)", "Numerical Methods",
                 "Modelling w/ Algorithms", "Extra Pure", "Further Pure w/ Tech"]
FM_OPT_MODS = ["fmmech", "fmstat", "numeric", "algos", "xpure", "fpt"]

def _submenu(title, labels, mods):
    while True:
        c = menu(title, labels)
        if c == -1:
            return
        show_help(mods[c])
        # a fault inside one tool must not drop the whole toolkit back to the
        # Python shell - report it and stay in the menu
        try:
            __import__(mods[c]).run()
        except Exception as e:
            show_text("Tool error", "That tool stopped: " + str(e) +
                      ". Returning to the menu.", RED)

def fm_section():
    while True:
        c = menu("FURTHER MATHS", ["Core Pure (compulsory)", "Options"])
        if c == -1:
            return
        if c == 0:
            _submenu("FM CORE PURE", FM_CORE_LABELS, FM_CORE_MODS)
        elif c == 1:
            _submenu("FM OPTIONS", FM_OPT_LABELS, FM_OPT_MODS)

MATHS_LABELS = ["Pure: algebra & trig", "Pure: functions & calculus",
                "Statistics", "Mechanics", "Proof"]
MATHS_MODS = ["pure640", "purecalc", "stat640", "mech640", "proof"]

def maths_section():
    _submenu("A-LEVEL MATHS", MATHS_LABELS, MATHS_MODS)

def main():
    global ANGLE_DEG
    clear_screen()
    draw_string(70, 28, "MATHS", BLACK, "large")
    draw_string(52, 58, "TOOLKIT", BLACK, "large")
    draw_string(34, 104, "OCR B Maths + Further", GREY, "medium")
    draw_string(70, 134, "Press any key", BLACK, "small")
    show_screen()
    wait_release()
    wait_press()
    wait_release()
    while True:
        mode = "Angle mode: DEGREES" if ANGLE_DEG else "Angle mode: RADIANS"
        c = menu("MATHS TOOLKIT", ["Calculate", "Calculus & Algebra",
                                    "A-Level Maths", "Further Maths", mode])
        if c == -1:
            return  # EXIT at the top level leaves the app, as the key implies
        if c == 0:
            calc_section()
        elif c == 1:
            cas_section()
        elif c == 2:
            maths_section()
        elif c == 3:
            fm_section()
        elif c == 4:
            ANGLE_DEG = not ANGLE_DEG
