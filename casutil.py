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
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    c = 0.0
    j = 0
    while j <= k:
        c += binom_pmf(n, p, j)
        j += 1
    return c
