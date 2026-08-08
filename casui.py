# cas.py - visual Computer Algebra System for Casio fx-CG100 (stock MicroPython).
# Type on the real keys; see a live 2D preview (Desmos-style). Then
# Differentiate / Integrate / Simplify / Solve / Evaluate / Graph.
# Imports caslex, caseng, casrender, cascalc. AC quits.
from casioplot import *
import caslex
import caseng
import casrender
import cascalc

IDLE = getkey()

WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
ACC   = (40, 120, 220)
GREY  = (150, 150, 160)
HL    = (225, 232, 250)
RED   = (205, 60, 60)

UP = 14; DOWN = 34; LEFT = 23; RIGHT = 25; OK = 24; EXE = 95
EXITK = 13; DEL = 64; SHIFT = 31; MENU = 35; ALPHA = 32
# Full key map decoded from the keyboard (codes follow a row*10+col grid).
UNSHIFT = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.',
    84: '+', 85: '-', 74: '*', 75: '/', 44: '^', 55: '(', 56: ')',
    41: 'x', 33: 'x', 42: '/', 45: '^2', 46: 'exp(', 93: '*10^',
    52: 'sin(', 53: 'cos(', 54: 'tan(', 43: 'sqrt(',
}
SHIFTED = {55: '=', 46: 'ln(', 45: 'log(', 61: 'pi'}
# ALPHA + key -> a letter variable (lowercase). Letters other than x are
# treated as symbolic constants by the engine. Letters are printed on the keys.
ALPHADICT = {
    42: 'a', 43: 'b', 44: 'c', 45: 'd', 46: 'e',
    61: 'm', 62: 'n', 63: 'o', 71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    82: 'u', 83: 'v', 84: 'w', 91: 'z',
}
# MENU picker (reliable on every unit) - y first since it has no obvious key.
EXTRAS = ['y', 'a', 'b', 'c', 'n', 'pi', 'e', 'exp(']

# global angle mode for Calculate + CAS evaluate/graph/table (FM modules stay radians)
ANGLE_DEG = False

def wait_release():
    while getkey() != IDLE:
        pass

def wait_press():
    while getkey() == IDLE:
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
def draw_input(prompt, ex, cur, shift, alpha, palette, psel):
    clear_screen()
    draw_string(6, 3, prompt, GREY, "small")
    if shift:
        draw_string(322, 3, "SHIFT", ACC, "small")
    elif alpha:
        draw_string(322, 3, "ALPHA", (210, 120, 30), "small")
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
    raw = tail_fit(raw, 368, "medium")
    draw_string(8, 120, raw, BLACK, "medium")
    draw_string(6, 178, "OK run  DEL del  ALPHA letter  MENU more", GREY, "small")
    if palette:
        rect(6, 146, 378, 174, HL)
        frame(6, 146, 378, 174, ACC)
        x = 18
        i = 0
        while i < len(EXTRAS):
            w = len(EXTRAS[i]) * 11 + 8
            if i == psel:
                rect(x - 3, 150, x + w, 172, (198, 214, 246))
            draw_string(x, 152, EXTRAS[i], BLACK, "medium")
            x += w + 14
            i += 1
    show_screen()

def input_expr(prompt):
    ex = []
    cur = 0
    shift = False
    alpha = False
    palette = False
    psel = 0
    draw_input(prompt, ex, cur, shift, alpha, palette, psel)
    while True:
        k = getkey()
        if k == IDLE:
            continue
        if palette:
            if k == LEFT:
                psel = (psel - 1) % len(EXTRAS)
            elif k == RIGHT:
                psel = (psel + 1) % len(EXTRAS)
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
        draw_string(14, y, opts[i], BLACK, "medium")
        r += 1
    draw_string(8, 178, "EXIT = back", GREY, "small")
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
        k = getkey()
        if k == IDLE:
            continue
        if k == UP:
            sel = (sel - 1) % len(opts)
        elif k == DOWN:
            sel = (sel + 1) % len(opts)
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
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
    k = getkey()
    while k == IDLE:
        k = getkey()
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
    "cas": "Algebra & calculus on a function of x. Type e.g. x^2+3x or sin(x), press OK, then pick: d/dx, gradient at a point, integrate (products like x sin(x) and x ln(x) are done by parts), definite integral a..b, simplify, solve f(x)=0, evaluate, graph, or a table of values. Type letters other than x with ALPHA or the MENU picker. Evaluate/graph/table/solve follow the home-menu angle mode; calculus uses radians.",
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
        op = menu("f(x) = " + s, ["Differentiate  d/dx", "Gradient at a point",
                                   "Integrate (+ C)", "Definite integral a..b",
                                   "Simplify", "Solve  f(x)=0", "Evaluate at x",
                                   "Graph", "Table of values", "New expression"])
        if op == -1 or op == 9:
            continue
        if op == 0:
            try:
                show_math("d/dx =", caseng.simplify(caseng.diff(tree)))
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
                    show_math("Integral (+ C)", caseng.simplify(r))
            except:
                show_text("Too complex", "Nests too deep", RED)
        elif op == 3:
            do_defint(tree)
        elif op == 4:
            try:
                show_math("Simplified", caseng.simplify(tree))
            except:
                show_text("Too complex", "Nests too deep", RED)
        elif op == 5:
            do_solve(s)
        elif op == 6:
            do_eval(tree)
        elif op == 7:
            graph(tree)
        elif op == 8:
            do_table(tree)

FM_CORE_LABELS = ["Complex numbers", "Matrices", "Vectors & 3-D", "Roots of polynomials",
                  "Series & Maclaurin", "Hyperbolic functions", "Polar coordinates",
                  "Differential equations"]
FM_CORE_MODS = ["vcplx", "matrix", "vectors", "polyroots", "series", "hyper", "polar", "diffeq"]
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

MATHS_LABELS = ["Pure", "Statistics", "Mechanics"]
MATHS_MODS = ["pure640", "stat640", "mech640"]

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
