# casutil.py - helpers shared by every section module.
# Before this file each of the 17 sections carried its own copy of _asknum,
# _fn, _show, _pages, _atan2, _deg/_rad, gcd, nCr and (twice) a whole normal
# distribution. The copies had drifted apart and only some of them were correct,
# so they now live here once.
# Stock CASIO MicroPython 1.9.4: ASCII only, no f-strings, iterative only,
# only math / random / casioplot importable.
import math
import casui
import caslex
import caseng

PI = math.pi

# ---------------------------------------------------------------- input ----
def asknum(prompt):
    # Ask for an expression and evaluate it to a number.
    # None means "cancelled, unreadable, or not a number" - callers treat that
    # as "no value given".
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        v = caseng.evalf(t, 0.0)
    except:
        return None
    if isinstance(v, complex):
        return None
    return v

def askint(prompt, lo=None, hi=None):
    # Whole number in [lo, hi]. Out-of-range returns None rather than silently
    # clamping, so the caller can say what it wanted.
    v = asknum(prompt)
    if v is None or v != v:
        return None
    try:
        n = int(round(v))
    except:
        return None
    if lo is not None and n < lo:
        return None
    if hi is not None and n > hi:
        return None
    return n

def asklist(prompt):
    # Space- or comma-separated numbers. None on cancel, [] if nothing parsed.
    s = casui.input_expr(prompt)
    if s is None:
        return None
    out = []
    for p in s.replace(',', ' ').split():
        try:
            out.append(float(p))
        except:
            return None  # a junk entry is an error, not something to skip
    return out

def askints(prompt):
    lst = asklist(prompt)
    if lst is None:
        return None
    return [int(round(v)) for v in lst]

def askexpr(prompt):
    # Parse tree, or None for cancelled/unreadable.
    s = casui.input_expr(prompt)
    if s is None:
        return None
    return caslex.parse(s)

def askg(default=9.8):
    v = asknum('g [' + fmt(default) + ']')
    if v is None:
        return default
    return v

# --------------------------------------------------------------- output ----
def fmt(x, dp=4):
    # Safe numeric format. Guards nan/inf because int() raises on both and that
    # would take out the whole result screen.
    if isinstance(x, complex):
        return fmtc(x.real, x.imag, dp)
    if not isinstance(x, (int, float)):
        return str(x)
    if x != x:
        return 'undefined'
    if x > 1.7e308:
        return 'inf'
    if x < -1.7e308:
        return '-inf'
    r = round(x, dp)
    if r == 0:
        r = 0.0          # kill "-0"
    if r == int(r):
        return str(int(r))
    return str(r)

def fmtc(re, im, dp=4):
    # a + bi, dropping a zero part
    if abs(im) < 1e-12:
        return fmt(re, dp)
    if abs(re) < 1e-12:
        return fmt(im, dp) + 'i'
    if im < 0:
        return fmt(re, dp) + ' - ' + fmt(-im, dp) + 'i'
    return fmt(re, dp) + ' + ' + fmt(im, dp) + 'i'

def show(title, lines):
    # casui.result_screen pages by itself now, so the old per-module _pages
    # chunking helpers are no longer needed.
    casui.result_screen(title, lines)

def run_tools(title, tools):
    # The identical run() loop every section ended with.
    labels = [t[0] for t in tools]
    while True:
        c = casui.menu(title, labels)
        if c == -1:
            return
        tools[c][1]()

# --------------------------------------------------------------- charts ----
# Shared drawing frame for every diagram in the toolkit. Before this, each
# plotting tool carried its own copy of "work out the scale, draw the axes,
# clip the line", and the copies disagreed about the margins.
#
# A frame is (x0, y0, x1, y1, xlo, xhi, ylo, yhi): the pixel box on the 384x192
# screen and the data range mapped onto it. The screen's y axis points down and
# a graph's points up, so fy inverts.
SCREEN_W = 384
SCREEN_H = 192

def frame(xlo, xhi, ylo, yhi, x0=26, y0=16, x1=378, y1=170):
    # a zero-width range would divide by zero; widen it around its own value
    if xhi - xlo < 1e-12:
        xlo -= 1.0
        xhi += 1.0
    if yhi - ylo < 1e-12:
        ylo -= 1.0
        yhi += 1.0
    return (x0, y0, x1, y1, xlo, xhi, ylo, yhi)

def fx(fr, x):
    return int(fr[0] + (x - fr[4]) * (fr[2] - fr[0]) / (fr[5] - fr[4]))

def fy(fr, y):
    return int(fr[3] - (y - fr[6]) * (fr[3] - fr[1]) / (fr[7] - fr[6]))

def _clip(fr, x, y):
    return fr[0] <= x <= fr[2] and fr[1] <= y <= fr[3]

def dot(fr, x, y, c=None):
    px = fx(fr, x)
    py = fy(fr, y)
    if _clip(fr, px, py):
        casui.set_pixel(px, py, casui.BLACK if c is None else c)

def marker(fr, x, y, c=None, r=2):
    # a filled blob, so a scatter point is visible at all
    px = fx(fr, x)
    py = fy(fr, y)
    c = casui.BLACK if c is None else c
    dy = -r
    while dy <= r:
        dx = -r
        while dx <= r:
            if dx * dx + dy * dy <= r * r + 1 and _clip(fr, px + dx, py + dy):
                casui.set_pixel(px + dx, py + dy, c)
            dx += 1
        dy += 1

def seg(fr, xa, ya, xb, yb, c=None):
    # data-space line segment, Bresenham in pixel space, clipped to the frame
    c = casui.BLACK if c is None else c
    x0 = fx(fr, xa)
    y0 = fy(fr, ya)
    x1 = fx(fr, xb)
    y1 = fy(fr, yb)
    dx = x1 - x0 if x1 >= x0 else x0 - x1
    dy = y1 - y0 if y1 >= y0 else y0 - y1
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    n = 0
    while n <= dx + dy + 2:
        if _clip(fr, x0, y0):
            casui.set_pixel(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
        n += 1

def box(fr, xa, ya, xb, yb, c=None, fill=False):
    c = casui.BLACK if c is None else c
    if fill:
        pa = fx(fr, xa)
        pb = fx(fr, xb)
        qa = fy(fr, yb)
        qb = fy(fr, ya)
        if pa > pb:
            pa, pb = pb, pa
        if qa > qb:
            qa, qb = qb, qa
        y = qa
        while y <= qb:
            x = pa
            while x <= pb:
                if _clip(fr, x, y):
                    casui.set_pixel(x, y, c)
                x += 1
            y += 1
        return
    seg(fr, xa, ya, xb, ya, c)
    seg(fr, xb, ya, xb, yb, c)
    seg(fr, xb, yb, xa, yb, c)
    seg(fr, xa, yb, xa, ya, c)

def axes(fr, title=None, xlab=None, ylab=None, ticks=True):
    # draw the frame's axes with the data range printed along the edges
    casui.clear_screen()
    if title is not None:
        casui.draw_string(4, 2, title, casui.ACC, 'small')
    x0, y0, x1, y1, xlo, xhi, ylo, yhi = fr
    casui.hline(x0, x1, y1, casui.GREY)
    yy = y0
    while yy <= y1:
        casui.set_pixel(x0, yy, casui.GREY)
        yy += 1
    # an axis line through zero as well, when zero is inside the range
    if ylo < 0.0 < yhi:
        casui.hline(x0, x1, fy(fr, 0.0), casui.GREY)
    if xlo < 0.0 < xhi:
        zx = fx(fr, 0.0)
        yy = y0
        while yy <= y1:
            casui.set_pixel(zx, yy, casui.GREY)
            yy += 1
    if ticks:
        casui.draw_string(x0 - 22, y1 - 6, fmt(ylo, 1), casui.GREY, 'small')
        casui.draw_string(x0 - 22, y0 - 2, fmt(yhi, 1), casui.GREY, 'small')
        casui.draw_string(x0, y1 + 3, fmt(xlo, 1), casui.GREY, 'small')
        s = fmt(xhi, 1)
        casui.draw_string(x1 - 6 * len(s), y1 + 3, s, casui.GREY, 'small')
    if xlab is not None:
        casui.draw_string(x0 + (x1 - x0) // 2 - 12, y1 + 3, xlab, casui.GREY, 'small')
    if ylab is not None:
        casui.draw_string(2, y0 - 12, ylab, casui.GREY, 'small')

def chart_hold(note=None):
    if note is not None:
        casui.draw_string(4, SCREEN_H - 12, note, casui.GREY, 'small')
    casui.show_screen()
    casui.hold()

def nice_range(vals, pad=0.08, zero=False):
    # data range widened a little so points do not sit on the frame edge
    lo = None
    hi = None
    for v in vals:
        if v is None or v != v:
            continue
        if lo is None or v < lo:
            lo = v
        if hi is None or v > hi:
            hi = v
    if lo is None:
        return (0.0, 1.0)
    if zero:
        if lo > 0.0:
            lo = 0.0
        if hi < 0.0:
            hi = 0.0
    span = hi - lo
    if span < 1e-12:
        span = abs(hi) if abs(hi) > 1e-12 else 1.0
    return (lo - span * pad, hi + span * pad)

# ------------------------------------------------------------ geometry ----
def atan2(y, x):
    # math.atan2 is missing from this build
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

def deg(r):
    return r * 180.0 / PI

def rad(d):
    return d * PI / 180.0

def acos_safe(c):
    # rounding can push a cosine a hair outside [-1, 1]
    if c > 1.0:
        c = 1.0
    if c < -1.0:
        c = -1.0
    return math.acos(c)

# -------------------------------------------------------- number theory ----
def gcd(a, b):
    a = abs(int(a))
    b = abs(int(b))
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    g = gcd(a, b)
    if g == 0:
        return 0
    return abs(int(a) // g * int(b))

def powmod(a, e, m):
    if m == 1:
        return 0
    r = 1
    a = a % m
    while e > 0:
        if e & 1:
            r = (r * a) % m
        a = (a * a) % m
        e >>= 1
    return r

def modinv(a, m):
    # iterative extended Euclid; None when gcd(a, m) != 1
    if m == 0:
        return None
    m = abs(m)
    old_r, r = a % m, m
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:
        return None
    return old_s % m

FACT_MAX = 500  # above this the handheld stalls building the integer

def fact(n):
    # exact factorial, None outside 0..FACT_MAX
    if n < 0 or n > FACT_MAX:
        return None
    r = 1
    i = 2
    while i <= n:
        r *= i
        i += 1
    return r

def ncr(n, r):
    # exact, built multiplicatively so no huge factorial is ever formed
    if n < 0 or r < 0 or r > n:
        return 0
    if r > n - r:
        r = n - r
    c = 1
    i = 1
    while i <= r:
        c = c * (n - r + i) // i
        i += 1
    return c

def npr(n, r):
    if n < 0 or r < 0 or r > n:
        return 0
    p = 1
    i = 0
    while i < r:
        p *= (n - i)
        i += 1
    return p

# ------------------------------------------------------- distributions ----
def erf(x):
    # Abramowitz & Stegun 7.1.26; |error| < 1.5e-7, well inside 4 s.f.
    s = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * math.exp(-x * x)
    return s * y

def phi(z):
    # standard normal cdf
    if z > 40.0:
        return 1.0
    if z < -40.0:
        return 0.0
    return 0.5 * (1.0 + erf(z / math.sqrt(2.0)))

def invphi(p):
    # inverse standard normal by bisection; 60 halvings of [-9, 9] is already
    # past double precision (the old copies used 80 and 200 iterations)
    if p <= 0.0:
        return -9.0
    if p >= 1.0:
        return 9.0
    lo = -9.0
    hi = 9.0
    i = 0
    while i < 60:
        mid = 0.5 * (lo + hi)
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
        i += 1
    return 0.5 * (lo + hi)

def poisson_pmf(mu, k):
    # exp(-mu) * mu^k / k!, accumulated one factor at a time. Computing mu**k
    # and k! separately overflowed a float for mu around 150 and crashed.
    if k < 0:
        return 0.0
    r = math.exp(-mu)
    i = 1
    while i <= k:
        r = r * mu / i
        i += 1
    return r

def poisson_cdf(mu, k):
    if k < 0:
        return 0.0
    r = math.exp(-mu)
    c = r
    i = 1
    while i <= k:
        r = r * mu / i
        c += r
        i += 1
    return c

def binom_pmf(n, p, k):
    # C(n,k) p^k q^(n-k), folding the q factors in as soon as the running
    # product exceeds 1 so it can neither overflow nor underflow early
    if n < 0 or k < 0 or k > n:
        return 0.0
    q = 1.0 - p
    r = 1.0
    used = 0
    rest = n - k
    i = 1
    while i <= k:
        r = r * (n - k + i) / i * p
        while r > 1.0 and used < rest:
            r *= q
            used += 1
        i += 1
    while used < rest:
        r *= q
        used += 1
    return r

def binom_cdf(n, p, k):
    # Sum of the pmf up to k, but walked with the recurrence
    #   P(j+1) = P(j) * (n-j)/(j+1) * p/q
    # rather than by calling binom_pmf k times. Each binom_pmf call is O(k)
    # itself, so the old loop was O(k^2): binom_cdf(5000, 0.3, 1500) took most
    # of half a second on a desktop, which on a handheld is a hang.
    #
    # The walk starts at the MODE, not at zero, because q**n underflows to
    # exactly 0 long before n gets interesting - for n = 5000 and q = 0.7 it is
    # about 1e-774 - and every subsequent term would then be 0 too. Starting
    # from the largest term and going outwards keeps every ratio near 1.
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    q = 1.0 - p
    m = int((n + 1) * p)
    if m > k:
        m = k
    if m < 0:
        m = 0
    pm = binom_pmf(n, p, m)
    if pm <= 0.0:
        # underflowed even at the mode: the whole tail is negligible either way
        return 0.0 if k < (n * p) else 1.0
    total = pm
    # down from the mode to 0
    t = pm
    j = m
    while j > 0:
        t = t * j / (n - j + 1) * q / p
        total += t
        j -= 1
    # up from the mode to k
    t = pm
    j = m
    while j < k:
        t = t * (n - j) / (j + 1) * p / q
        total += t
        j += 1
    if total > 1.0:
        total = 1.0
    return total
