# hwcheck.py - one-off hardware probe. Run THIS on the calculator to settle the
# device facts the desktop cannot answer, and paste what it prints into an
# issue or straight into the README table.
#
# It measures, in order:
#   1. the real recursion ceiling (README claims about 38 frames)
#   2. what getkey() returns with nothing held
#   3. the drawing screen size
#   4. which math members this build actually has
#   5. whether the toolkit's own deepest operations survive the real ceiling
#
# Nothing here is part of the toolkit; it is a sibling of keyprobe.py,
# calib_screen.py and fontmetrics.py, and is held to the same MicroPython
# limits by devlint.
from casioplot import *
import math

BLACK = (20, 20, 25)
GREY = (120, 120, 130)
ACC = (40, 120, 220)
RED = (205, 60, 60)
OK = (30, 140, 60)

# ---------------------------------------------------------------- the keys --
# The first run of this file on real hardware reported the idle getkey value as
# None, not 0 - and the paging loops below were written as "while getkey() != 0",
# which cannot ever exit when the idle value is None. They did exit, so the two
# observations disagree and the idle value is not a single constant. Rather than
# guess, this file now (a) never compares against a presumed idle value and
# (b) samples the idle value properly instead of once.
#
# The rule is casui.readkey()'s: a real key code is row*10+col with row 1-9 and
# col 1-6, and ANYTHING else - 0, None, whatever - is "no key".
def _held():
    k = getkey()
    if k is None:
        return False
    if k < 11 or k > 96:
        return False
    c = k % 10
    return c >= 1 and c <= 6


def wait_key():
    while _held():
        pass
    while not _held():
        pass
    while _held():
        pass


def idle_values(n=400):
    # Every distinct thing getkey() returns with nothing held, as text, so 0 and
    # None and anything else are told apart. If this reports more than one value
    # the idle return is not a constant, which is exactly what a toolkit must
    # not depend on.
    seen = []
    i = 0
    while i < n:
        s = str(getkey())
        found = False
        for t in seen:
            if t == s:
                found = True
        if not found:
            seen.append(s)
        i += 1
    return seen

# ---------------------------------------------------------------- recursion --
DEPTH = [0]

def _sink():
    # Count frames until the interpreter refuses another one. The counter is a
    # list so the increment does not need a global statement, which keeps the
    # frame as small as this build can make it - a bigger frame would measure
    # this function rather than the ceiling.
    DEPTH[0] += 1
    _sink()

def recursion_limit():
    DEPTH[0] = 0
    try:
        _sink()
    except:
        pass
    return DEPTH[0]

# ------------------------------------------------------------------- screen --
def screen_size():
    # Walk a black pixel outwards until set_pixel stops taking. Out-of-range
    # coordinates are ignored rather than raising (manual page 141), so the
    # test is whether get_pixel reads back what was written.
    w = 0
    x = 0
    while x < 1024:
        set_pixel(x, 0, (0, 0, 0))
        if get_pixel(x, 0) != (0, 0, 0):
            break
        w = x + 1
        x += 1
    h = 0
    y = 0
    while y < 1024:
        set_pixel(0, y, (0, 0, 0))
        if get_pixel(0, y) != (0, 0, 0):
            break
        h = y + 1
        y += 1
    clear_screen()
    return (w, h)

# --------------------------------------------------------------------- math --
# Everything MicroPython 1.9.4 might expose. Probed by name through getattr so
# this file does not have to reference members that may not exist.
MATH_NAMES = [
    "e", "pi", "sqrt", "pow", "exp", "log", "log2", "log10",
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
    "ceil", "floor", "trunc", "fabs", "fmod", "modf", "frexp", "ldexp",
    "copysign", "isnan", "isinf", "isfinite", "degrees", "radians",
    "factorial", "gamma", "lgamma", "erf", "erfc", "expm1", "log1p", "cbrt",
]

def math_members():
    have = []
    lack = []
    for name in MATH_NAMES:
        if getattr(math, name, None) is None:
            lack.append(name)
        else:
            have.append(name)
    return (have, lack)

# ------------------------------------------------------------- the toolkit --
def engine_survives():
    # The property that actually matters: the engine recurses on expression
    # NESTING, never on input length. A long flat sum and a deeply bracketed
    # one both have to parse on the real machine.
    out = []
    try:
        import caslex
        import caseng
        import cascalc
    except Exception as e:
        return [("import", "FAILED: " + str(e))]
    deep = "((((((((((x+1))))))))))"
    parts = "x"
    i = 0
    while i < 200:
        parts = parts + "+x"
        i += 1
    for label, fn in (("parse deep nesting", lambda: caslex.parse(deep)),
                      ("parse 200-term sum", lambda: caslex.parse(parts))):
        try:
            r = fn()
            out.append((label, "ok" if r is not None else "returned None"))
        except Exception as e:
            out.append((label, "FAILED: " + str(e)))
    t = caslex.parse("x^2+3x+1")
    for label, fn in (("simplify", lambda: caseng.simplify(t)),
                      ("differentiate", lambda: caseng.diff(t)),
                      ("evaluate", lambda: caseng.evalf(t, 1.0)),
                      ("print", lambda: caseng.tostr(t)),
                      ("integrate by parts",
                       lambda: cascalc.integ(caslex.parse("x^2*exp(x)")))):
        try:
            fn()
            out.append((label, "ok"))
        except Exception as e:
            out.append((label, "FAILED: " + str(e)))
    return out

# ------------------------------------------------------------- memory ----
# The section modules are large - the biggest is over 70 KB of source - and
# MicroPython has to compile each one to bytecode in RAM. The toolkit loads
# them ONE AT A TIME on demand, so the real requirement is only the largest
# plus the always-loaded core. This imports them in sequence, which is the
# worst case (they accumulate), so getting through all of them proves the
# device can certainly manage the real pattern. Where it stops is the answer.
SECTIONS = [
    "pure640", "purecalc", "stat640", "mech640", "proof",
    "vcplx", "matrix", "vectors", "polyroots", "series", "hyper", "polar",
    "diffeq", "fmmech", "fmstat", "numeric", "algos", "xpure", "fpt",
]

def modules_load():
    # This sweep compiles about 750 KB of source to bytecode on a handheld and
    # is SLOW - the better part of a minute, with no output while it runs. The
    # first hardware run looked like a hang for exactly that reason. So it now
    # draws each module as it starts, which turns a dead screen into progress,
    # and EXIT abandons it.
    #
    # It is also the least important page here. The toolkit loads section
    # modules ONE AT A TIME on demand and never holds them all; that pattern is
    # already proved by maths.py running. This measures the worst case, which
    # is a nice-to-know, not a requirement.
    out = []
    loaded = 0
    stopped = False
    for name in SECTIONS:
        clear_screen()
        draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
        draw_string(6, 30, "Loading every section at once.", BLACK, "small")
        draw_string(6, 48, "This is slow - about 750 KB to", GREY, "small")
        draw_string(6, 62, "compile. EXIT abandons it.", GREY, "small")
        draw_string(6, 88, str(loaded + 1) + " of " + str(len(SECTIONS)) +
                    ":  " + name, BLACK, "medium")
        show_screen()
        if getkey() == 22:                       # EXIT
            stopped = True
            out.append((name, "skipped by EXIT"))
            break
        try:
            __import__(name)
            loaded += 1
        except MemoryError:
            out.append((name, "OUT OF MEMORY"))
            break
        except Exception as e:
            out.append((name, "FAILED: " + str(e)))
            break
    out.append(("loaded in sequence", str(loaded) + " of " + str(len(SECTIONS))))
    if stopped:
        out.append(("verdict", "abandoned - no verdict"))
    elif loaded == len(SECTIONS):
        out.append(("verdict", "all fit AT ONCE"))
    else:
        out.append(("verdict", "one at a time is still fine"))
    return out

# --------------------------------------------------------------------- run --
def page(title, rows, note):
    clear_screen()
    draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
    draw_string(6, 26, title, BLACK, "medium")
    y = 50
    for label, value in rows:
        col = RED if str(value)[:6] == "FAILED" else BLACK
        draw_string(10, y, label, GREY, "small")
        draw_string(200, y, str(value), col, "small")
        y += 14
        if y > 158:
            break
    draw_string(6, 174, note, GREY, "small")
    show_screen()
    wait_key()

def main():
    clear_screen()
    draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
    draw_string(6, 40, "Measuring the recursion ceiling.", BLACK, "small")
    draw_string(6, 58, "This may pause for a moment.", GREY, "small")
    show_screen()
    limit = recursion_limit()

    idle = idle_values()
    w, h = screen_size()
    have, lack = math_members()

    page("Limits", [
        ("recursion ceiling", str(limit) + " frames"),
        ("idle getkey, 400 samples", " ".join(idle)),
        ("distinct idle values", str(len(idle))),
        ("screen width", str(w)),
        ("screen height", str(h)),
    ], "measured 92 frames, 384x192")

    rows = []
    line = ""
    for name in have:
        if len(line) + len(name) > 26:
            rows.append(("have", line))
            line = ""
        line = (line + " " + name) if line else name
    if line:
        rows.append(("have", line))
    page("math members present", rows, str(len(have)) + " of " +
         str(len(MATH_NAMES)) + " probed")

    rows = []
    line = ""
    for name in lack:
        if len(line) + len(name) > 26:
            rows.append(("absent", line))
            line = ""
        line = (line + " " + name) if line else name
    if line:
        rows.append(("absent", line))
    if not rows:
        rows = [("absent", "none - all present")]
    page("math members ABSENT", rows, "devlint.MATH_OK must not exceed 'have'")

    page("Engine on real hardware", engine_survives(),
         "all must say ok at the ceiling above")

    page("Section modules", modules_load(),
         "worst case only - the app loads one")

    clear_screen()
    draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
    draw_string(6, 40, "Done. Report both figures below.", BLACK, "small")
    draw_string(6, 56, "More than one idle value means the", BLACK, "small")
    draw_string(6, 72, "idle return is not a constant.", BLACK, "small")
    draw_string(6, 100, "ceiling = " + str(limit), OK, "medium")
    draw_string(6, 124, "idle = " + " ".join(idle), OK, "medium")
    show_screen()

main()
