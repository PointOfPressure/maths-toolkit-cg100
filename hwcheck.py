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
    # wait for a key without depending on the idle value
    while getkey() != 0:
        pass
    while getkey() == 0:
        pass
    while getkey() != 0:
        pass

def main():
    clear_screen()
    draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
    draw_string(6, 40, "Measuring the recursion ceiling.", BLACK, "small")
    draw_string(6, 58, "This may pause for a moment.", GREY, "small")
    show_screen()
    limit = recursion_limit()

    idle = getkey()
    w, h = screen_size()
    have, lack = math_members()

    page("Limits", [
        ("recursion ceiling", str(limit) + " frames"),
        ("getkey with nothing held", str(idle)),
        ("screen width", str(w)),
        ("screen height", str(h)),
    ], "README claims ~38 frames, 384x192")

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

    clear_screen()
    draw_string(6, 4, "HARDWARE CHECK", ACC, "medium")
    draw_string(6, 40, "Done. Write the recursion figure", BLACK, "small")
    draw_string(6, 56, "into the README device-facts table", BLACK, "small")
    draw_string(6, 72, "and the tests.py BUDGET constant.", BLACK, "small")
    draw_string(6, 100, "ceiling = " + str(limit), OK, "medium")
    draw_string(6, 124, "idle getkey = " + str(idle), OK, "medium")
    show_screen()

main()
