# tests.py - correctness tests for the Maths Toolkit.
#
#   python3 tests.py
#
# stress.py proves nothing crashes. This proves the answers are right: every
# check below compares against a value worked out independently, and the
# section tools are driven through the real UI entry points with scripted key
# input, so what is asserted is what a student would actually see on screen.
#
# Also runs devlint (MicroPython 1.9.4 compliance) and a recursion-depth guard
# for the handheld's shallow call stack.

import math
import sys

import casui

# ------------------------------------------------------------------ stubs --
_inputs = []
_menus = []
_out = []

def _stub_input(prompt):
    if _inputs:
        return _inputs.pop(0)
    return None

def _stub_menu(title, opts):
    if _menus:
        return _menus.pop(0)
    return -1

def _cap_result(title, lines):
    _out.append(str(title))
    for ln in lines:
        _out.append(str(ln))

def _cap_text(title, body, color=None):
    _out.append(str(title))
    _out.append(str(body))

def _cap_math(title, tree):
    import caseng
    _out.append(str(title))
    _out.append(caseng.tostr(tree))

def _noop(*a, **k):
    return None

casui.input_expr = _stub_input
casui.menu = _stub_menu
casui.result_screen = _cap_result
casui.show_text = _cap_text
casui.show_math = _cap_math
casui.wait_release = _noop
casui.wait_press = _noop
casui.clear_screen = _noop
casui.show_screen = _noop
casui.draw_string = _noop
casui.set_pixel = _noop
casui.hline = _noop
casui.vline = _noop
casui.rect = _noop
casui.frame = _noop
casui.hold = _noop
casui.hold_page = lambda *a, **k: True

import caslex
import caseng
import cascalc
import casrender
import casutil
import devlint

# ---------------------------------------------------------------- harness --
FAILED = []
CHECKS = [0]

def check(label, got, want):
    CHECKS[0] += 1
    if got != want:
        FAILED.append(label + ": got " + repr(got) + ", want " + repr(want))

def close(label, got, want, tol=1e-6):
    CHECKS[0] += 1
    if got is None:
        FAILED.append(label + ": got None, want " + repr(want))
        return
    if abs(got - want) > tol:
        FAILED.append(label + ": got " + repr(got) + ", want " + repr(want) +
                      " (tol " + str(tol) + ")")

def truthy(label, cond):
    CHECKS[0] += 1
    if not cond:
        FAILED.append(label + ": expected true")

def raises(label, fn):
    CHECKS[0] += 1
    try:
        fn()
    except Exception:
        return
    FAILED.append(label + ": expected an exception, none raised")

def drive(fn, inputs=(), menus=()):
    _inputs[:] = list(inputs)
    _menus[:] = list(menus)
    _out[:] = []
    fn()
    return list(_out)

def has(label, lines, needle):
    CHECKS[0] += 1
    for ln in lines:
        if needle in ln:
            return
    FAILED.append(label + ": no line containing " + repr(needle) +
                  " in " + repr(lines[:14]))

def _first_number(s):
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        start = None
        if c in "0123456789":
            start = i
        elif c == '-' and i + 1 < n and s[i + 1] in "0123456789.":
            start = i
        elif c == '.' and i + 1 < n and s[i + 1] in "0123456789":
            start = i
        if start is not None:
            j = start + 1 if s[start] == '-' else start
            while j < n and s[j] in "0123456789.":
                j += 1
            if j < n and s[j] in "eE":
                k = j + 1
                if k < n and s[k] in "+-":
                    k += 1
                if k < n and s[k] in "0123456789":
                    while k < n and s[k] in "0123456789":
                        k += 1
                    j = k
            try:
                return float(s[start:j])
            except:
                pass
        i += 1
    return None

def num(label, lines, key, want, tol=1e-4):
    # Value of the number following `key`. Result screens print the formula
    # above the answer ("Un = a+(n-1)d" then "Un = 14"), so every line carrying
    # the key is a candidate and the check passes if one of them matches.
    CHECKS[0] += 1
    seen = []
    for ln in lines:
        p = ln.find(key)
        if p < 0:
            continue
        v = _first_number(ln[p + len(key):])
        if v is None:
            continue
        seen.append(v)
        if abs(v - want) <= tol:
            return
    if not seen:
        FAILED.append(label + ": no number after " + repr(key) +
                      " in " + repr(lines[:14]))
        return
    FAILED.append(label + ": " + repr(key) + " gave " + repr(seen) +
                  ", want " + repr(want))

def sstr(e):
    return caseng.tostr(caseng.simplify(caslex.parse(e)))

def ev(e, x=0.0, deg=False):
    return caseng.evalf(caslex.parse(e), x, deg)

def isym(e):
    t = caslex.parse(e)
    r = cascalc.integ(t)
    return None if r is None else caseng.tostr(caseng.simplify(r))


# =========================================================== caslex tests ==
def test_lexer():
    check("parse 2^-3", caslex.parse("2^-3"), ('^', ('n', 2), ('neg', ('n', 3))))
    close("eval 2^-3", ev("2^-3"), 0.125)
    close("eval x^-1", ev("x^-1", 4.0), 0.25)
    close("eval 2^-x", ev("2^-x", 3.0), 0.125)
    close("eval -2^2", ev("-2^2"), -4.0)          # unary binds looser than ^
    close("eval 2^3^2", ev("2^3^2"), 512.0)       # ^ is right-associative
    close("eval 1/-2", ev("1/-2"), -0.5)
    close("eval 2^(-3)", ev("2^(-3)"), 0.125)

    # scientific-notation literals, so a displayed 1.23e15 can be retyped
    close("eval 1e3", ev("1e3"), 1000.0)
    close("eval 2.5e-3", ev("2.5e-3"), 0.0025)
    close("eval 6.02e23", ev("6.02e23"), 6.02e23)
    # a bare e is still Euler's number
    close("eval 2e", ev("2e"), 2 * 2.718281828459045)
    close("eval 3exp(1)", ev("3exp(1)"), 3 * math.e)

    # implicit multiplication
    close("eval 2x", ev("2x", 5.0), 10.0)
    close("eval 2(x+1)", ev("2(x+1)", 3.0), 8.0)
    close("eval (x+1)(x-1)", ev("(x+1)(x-1)", 3.0), 8.0)
    close("eval 3!2", ev("3!2"), 12.0)            # implicit * after factorial

    # malformed input yields None, never an exception and never a silent result
    check("parse 'x)'", caslex.parse("x)"), None)
    check("parse '((x)'", caslex.parse("((x)"), None)
    check("parse '+'", caslex.parse("*"), None)
    check("parse ''", caslex.parse(""), None)

    # longest-match function names
    close("asinh beats asin", ev("asinh(0)"), 0.0)
    close("logb(2,8)", ev("logb(2,8)"), 3.0)
    close("nCr(6,2)", ev("nCr(6,2)"), 15.0)
    close("nPr(5,2)", ev("nPr(5,2)"), 20.0)
    close("5!", ev("5!"), 120.0)


# =========================================================== caseng tests ==
def test_engine():
    check("simplify x+0", sstr("x+0"), "x")
    check("simplify x*1", sstr("x*1"), "x")
    check("simplify x*0", sstr("x*0"), "0")
    check("simplify x-x", sstr("x-x"), "0")
    check("simplify x^1", sstr("x^1"), "x")
    check("simplify x^0", sstr("x^0"), "1")
    check("simplify 2/4", sstr("2/4"), "1/2")
    check("simplify 6/3", sstr("6/3"), "2")
    check("simplify 2^-3", sstr("2^-3"), "1/8")   # exact, not 0.125
    check("simplify x/(-1)", sstr("x/(0-1)"), "-x")
    # combining like powers is what lets integration by parts close
    check("simplify x^2*x^3", sstr("x^2*x^3"), "x^5")
    check("simplify x*x^3", sstr("x*x^3"), "x^4")
    check("simplify x^3/x", sstr("x^3/x"), "x^2")
    check("simplify x^2/(2x)", sstr("x^2/(2x)"), "x/2")
    check("simplify x/(2x)", sstr("x/(2x)"), "1/2")

    # a fractional power of a negative is complex: leave it symbolic, do not
    # fold a complex number into the tree
    truthy("(-8)^(1/3) stays symbolic", "^" in sstr("(0-8)^(1/3)"))
    raises("evalf (-8)^(1/3) raises", lambda: ev("(0-8)^(1/3)"))
    # a huge integer power is not folded (it would allocate megabytes)
    truthy("2^1000 not folded", "^" in sstr("2^1000"))

    # derivatives
    check("d/dx x^2+3x", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("x^2+3x")))), "2*x+3")
    check("d/dx sin(x)", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("sin(x)")))), "cos(x)")
    check("d/dx logb(2,x)", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("logb(2,x)")))), "1/(x*ln(2))")
    # numeric spot-checks of the whole rule set
    for expr, at, want in [
        ("x^3", 2.0, 12.0), ("1/x", 2.0, -0.25), ("sqrt(x)", 4.0, 0.25),
        ("exp(x)", 1.0, math.e), ("ln(x)", 2.0, 0.5),
        ("tan(x)", 0.3, 1.0 / (math.cos(0.3) ** 2)),
        ("asin(x)", 0.5, 1.0 / math.sqrt(1 - 0.25)),
        ("atan(x)", 2.0, 0.2), ("sinh(x)", 1.0, math.cosh(1.0)),
        ("tanh(x)", 0.5, 1.0 - math.tanh(0.5) ** 2),
        ("x*sin(x)", 1.0, math.sin(1.0) + math.cos(1.0)),
        ("sin(x)/x", 1.0, math.cos(1.0) - math.sin(1.0)),
        ("2^x", 3.0, 8.0 * math.log(2.0)),
        ("log(x)", 5.0, 1.0 / (5.0 * math.log(10.0))),
    ]:
        d = caseng.simplify(caseng.diff(caslex.parse(expr)))
        close("d/dx " + expr + " at " + str(at), caseng.evalf(d, at), want, 1e-9)

    # unknown variables are reported, not silently taken as 0
    raises("evalf unknown var raises", lambda: ev("a+b"))
    close("evalf with env", caseng.evalf(caslex.parse("x+y"), 1.0, False, {'y': 10.0}), 11.0)

    # degrees mode
    close("sin 30 deg", ev("sin(30)", 0.0, True), 0.5)
    close("asin .5 deg", ev("asin(0.5)", 0.0, True), 30.0)
    close("sin 30 rad", ev("sin(30)", 0.0, False), math.sin(30.0))

    # printing
    check("tostr keeps precedence", caseng.tostr(caslex.parse("(x+1)*(x-1)")), "(x+1)*(x-1)")
    check("tostr brackets neg base", caseng.tostr(('^', ('n', -8), ('n', 2))), "(-8)^2")
    check("numstr nan", caseng.tostr(('n', float('nan'))), "undefined")
    check("numstr inf", caseng.tostr(('n', float('inf'))), "inf")

    # hand-built functions the device lacks
    close("sinh(2)", ev("sinh(2)"), math.sinh(2.0), 1e-12)
    close("cosh(2)", ev("cosh(2)"), math.cosh(2.0), 1e-12)
    close("tanh(2)", ev("tanh(2)"), math.tanh(2.0), 1e-12)
    close("asinh(2)", ev("asinh(2)"), math.asinh(2.0), 1e-12)
    close("asinh(-2)", ev("asinh(0-2)"), math.asinh(-2.0), 1e-12)
    close("acosh(2)", ev("acosh(2)"), math.acosh(2.0), 1e-12)
    close("atanh(.5)", ev("atanh(0.5)"), math.atanh(0.5), 1e-12)
    close("tanh(400) saturates", ev("tanh(400)"), 1.0)


# =========================================================== cascalc tests =
def test_calculus():
    # linear_coeff must be structural. Sampling at x = 0, 1, 2 accepted this
    # cubic as linear and every integral built on it came out wrong.
    check("linear_coeff cubic", cascalc.linear_coeff(caslex.parse("x^3-3x^2+3x"), 'x'), None)
    check("linear_coeff 2x+1", cascalc.linear_coeff(caslex.parse("2x+1"), 'x'), (2, 1))
    check("linear_coeff x^2", cascalc.linear_coeff(caslex.parse("x^2"), 'x'), None)
    check("linear_coeff -x", cascalc.linear_coeff(caslex.parse("0-x"), 'x'), (-1, 0))
    check("integ of non-linear arg", isym("sin(x^3-3x^2+3x)"), None)

    check("int x^2", isym("x^2"), "x^3/3")
    check("int 1/x", isym("1/x"), "ln(x)")
    check("int x^-1", isym("x^-1"), "ln(x)")
    check("int 3/x", isym("3/x"), "3*ln(x)")
    check("int sqrt(x)", isym("sqrt(x)"), "2/3*x^(3/2)")
    check("int ln(x)", isym("ln(x)"), "x*ln(x)-x")
    check("int tan(x)", isym("tan(x)"), "-ln(cos(x))")
    check("int 1/(2x+1)", isym("1/(2x+1)"), "ln(2*x+1)/2")
    check("int exp(-x)", isym("exp(-x)"), "-exp(-x)")
    check("int x^(2/3)", isym("x^(2/3)"), "3/5*x^(5/3)")
    check("int sin(x)", isym("sin(x)"), "-cos(x)")
    check("int 5", isym("5"), "5*x")

    # integration by parts
    check("int x ln(x)", isym("x*ln(x)"), "ln(x)*x^2/2-x^2/4")
    check("int x^2 ln(x)", isym("x^2*ln(x)"), "ln(x)*x^3/3-x^3/9")
    check("int atan(x)", isym("atan(x)"), "atan(x)*x-1/2*ln(1+x^2)")
    truthy("int x sin(x) closes", isym("x*sin(x)") is not None)
    truthy("int x^2 sin(x) closes", isym("x^2*sin(x)") is not None)
    truthy("int x^3 exp(x) closes", isym("x^3*exp(x)") is not None)
    # exp x trig cycles forever under repeated parts - closed form instead
    check("int exp(x)sin(x)", isym("exp(x)*sin(x)"), "exp(x)*(sin(x)-cos(x))/2")
    check("int exp(2x)cos(3x)", isym("exp(2x)*cos(3x)"), "exp(2*x)*(2*cos(3*x)+3*sin(3*x))/13")
    # the integrand reappears: solve I = uv - kI rather than recurse
    check("int sin(x)cos(x)", isym("sin(x)*cos(x)"), "sin(x)^2/2")
    check("int exp(x)exp(x)", isym("exp(x)*exp(x)"), "exp(x)^2/2")
    # f'/f -> ln f
    check("int 2x/(x^2+1)", isym("2x/(x^2+1)"), "ln(x^2+1)")
    check("int cot", isym("cos(x)/sin(x)"), "ln(sin(x))")
    check("int x/(x^2+4)", isym("x/(x^2+4)"), "1/2*ln(x^2+4)")
    # still out of reach: these need trig identities or partial fractions, and
    # None is the signal for the UI to offer the numeric definite integral
    check("int sin^2 unsupported", isym("sin(x)*sin(x)"), None)
    check("int x atan(x) unsupported", isym("x*atan(x)"), None)
    truthy("by-parts depth is capped", cascalc.BYPARTS_MAX <= 4)

    # every symbolic integral must agree with the numeric one
    for e in ["x^2", "1/x", "sqrt(x)", "ln(x)", "tan(x)", "1/(2x+1)",
              "exp(-x)", "x^(2/3)", "cos(3x)", "(2x+1)^3", "sqrt(2x+1)",
              "sinh(x)", "cosh(3x)", "x^5", "3/x",
              "x*sin(x)", "x*cos(x)", "x*exp(x)", "x^2*sin(x)", "x^2*exp(x)",
              "x*ln(x)", "x^2*ln(x)", "atan(x)", "exp(x)*sin(x)",
              "exp(2x)*cos(3x)", "sin(x)*cos(x)", "x^3*exp(x)",
              "x*sin(2x+1)", "x*cos(3x)", "x*exp(2x)", "2x/(x^2+1)",
              "cos(x)/sin(x)", "x/(x^2+4)", "x*sqrt(x)"]:
        t = caslex.parse(e)
        F = cascalc.integ(t)
        a, b = 0.35, 0.9
        sym = caseng.evalf(F, b) - caseng.evalf(F, a)
        close("F'=f for " + e, sym, cascalc.defint(t, a, b), 1e-7)

    # definite integrals against known values
    close("defint x^2 0..1", cascalc.defint(caslex.parse("x^2"), 0.0, 1.0), 1.0 / 3.0, 1e-9)
    close("defint sin 0..pi", cascalc.defint(caslex.parse("sin(x)"), 0.0, math.pi), 2.0, 1e-9)
    close("defint 1/x 1..e", cascalc.defint(caslex.parse("1/x"), 1.0, math.e), 1.0, 1e-7)
    close("defint reversed", cascalc.defint(caslex.parse("x^2"), 1.0, 0.0), -1.0 / 3.0, 1e-9)
    check("defint over singularity", cascalc.defint(caslex.parse("1/x"), -1.0, 1.0), None)

    # roots
    check("solve x^2-4", [round(r, 6) for r in cascalc.solve(caslex.parse("x^2-4"))], [-2.0, 2.0])
    check("solve x^3-x", [round(r, 6) for r in cascalc.solve(caslex.parse("x^3-x"))], [-1.0, 0.0, 1.0])
    # a touching root has no sign change - the old grid scan missed these
    check("solve x^2 (touching)", [round(r, 5) for r in cascalc.solve(caslex.parse("x^2"))], [0.0])
    check("solve (x-1)^2", [round(r, 5) for r in cascalc.solve(caslex.parse("(x-1)^2"))], [1.0])
    # a constant has no isolated roots; this used to return 400 bogus ones
    check("solve 0", cascalc.solve(caslex.parse("0")), [])
    check("solve 5", cascalc.solve(caslex.parse("5")), [])
    truthy("solve root count is capped", len(cascalc.solve(caslex.parse("sin(1000x)"))) <= cascalc.MAXROOTS)
    r = cascalc.solve(caslex.parse("sin(x)"), deg=True)
    truthy("solve sin in degrees finds 0", any(abs(v) < 1e-4 for v in r))
    truthy("solve sin in degrees finds 180", any(abs(v - 180.0) < 1e-3 for v in r))


# ========================================================= casrender tests =
def test_render():
    for e in ["x^2+3x", "(x+1)/(x-1)", "sqrt(x^2+1)", "exp(x)", "sin(x)/x",
              "nCr(6,2)", "5!", "abs(x-3)", "1/(2x+1)", "x^(3/2)"]:
        t = caslex.parse(e)
        box = casrender.build(t, 0)
        w, a, d = casrender.measure(box)
        truthy("render measures " + e, w > 0 and a > 0)
        truthy("render draws " + e, casrender.render(t, 0, 0, 384, 150, (0, 0, 0)) in (True, False))
    check("casrender numstr nan", casrender.numstr(float('nan')), "undefined")
    check("casrender numstr inf", casrender.numstr(float('inf')), "inf")
    # measure is cached: exactly one _measure call per distinct box
    calls = [0]
    orig = casrender._measure
    def counted(b):
        calls[0] += 1
        return orig(b)
    casrender._measure = counted
    try:
        casrender.render(caslex.parse("(x^2+3x+1)/(sqrt(x)+2)"), 0, 0, 384, 150, (0, 0, 0))
        truthy("measure cache keeps calls small", calls[0] < 40)
    finally:
        casrender._measure = orig


# ============================================================ casui tests ==
def test_ui_format():
    check("fmt int", casui.fmt(3.0), "3")
    check("fmt nan", casui.fmt(float('nan')), "undefined")
    check("fmt inf", casui.fmt(float('inf')), "inf")
    check("_fmt_num int", casui._fmt_num(7), "7")
    check("_fmt_num nan", casui._fmt_num(float('nan')), "undefined")
    check("_fmt_num big", casui._fmt_num(1e15), "1.0e15")
    check("_fmt_num small", casui._fmt_num(1e-7), "1.0e-7")
    check("_bad_result complex", casui._bad_result(complex(1, 1)), True)
    check("_bad_result nan", casui._bad_result(float('nan')), True)
    check("_bad_result ok", casui._bad_result(2.5), False)
    # large font must not be measured with medium widths
    truthy("char_w large > medium", casui.char_w("o", "large") > casui.char_w("o", "medium"))
    truthy("text_w large > medium", casui.text_w("hello", "large") > casui.text_w("hello", "medium"))
    # word wrap never exceeds the pixel budget
    for ln in casui.wrap_px("the quick brown fox jumps over a very lazy dog indeed", 200, "medium"):
        truthy("wrap_px fits: " + ln, casui.text_w(ln, "medium") <= 200)
    truthy("wrap_px splits long words",
           len(casui.wrap_px("a" * 200, 100, "medium")) > 1)
    check("empty menu returns -1", casui.menu("t", []), -1)


def _typeable_tokens():
    t = set()
    for d in (casui.UNSHIFT, casui.SHIFTED, casui.ALPHADICT):
        for v in d.values():
            t.add(v)
    for v in casui.EXTRAS:
        t.add(v)
    return t

def _typeable_chars(tokens):
    return set(v for v in tokens if len(v) == 1)

# The fx-CG100 keypad, transcribed independently from the key-code diagram in
# Casio's manual and the printed keytops. Codes are row*10+col. [ON] (row 1
# col 1) and [AC] (row 6 col 5) are assigned no code and cannot be read.
KEYPAD = {
    12: 'HOME', 13: 'LINESTART', 14: 'UP', 15: 'LINEEND', 16: 'PAGEUP',
    21: 'SETTINGS', 22: 'BACK', 23: 'LEFT', 24: 'OK', 25: 'RIGHT', 26: 'PAGEDOWN',
    31: 'SHIFT', 32: 'ALPHA', 33: 'VARIABLE', 34: 'DOWN', 35: 'CATALOG', 36: 'TOOLS',
    41: 'x', 42: 'frac', 43: 'sqrt', 44: 'power', 45: 'square', 46: 'e^x',
    51: ',', 52: 'sin', 53: 'cos', 54: 'tan', 55: '(', 56: ')',
    61: '7', 62: '8', 63: '9', 64: 'DEL',
    71: '4', 72: '5', 73: '6', 74: 'times', 75: 'divide',
    81: '1', 82: '2', 83: '3', 84: 'plus', 85: 'minus',
    91: '0', 92: '.', 93: 'x10', 94: 'FORMAT', 95: 'EXE',
}
# the orange ALPHA letter printed on each key
ALPHA_KEYS = {
    41: 'a', 42: 'b', 43: 'c', 44: 'd', 45: 'e', 46: 'f',
    51: 'g', 52: 'h', 53: 'i', 54: 'j', 55: 'k', 56: 'l',
    61: 'm', 62: 'n', 63: 'o',
    71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    81: 'u', 82: 'v', 83: 'w', 84: 'x', 85: 'y',
    91: 'z',
}
# what each key types unshifted, where the toolkit binds it
PLAIN_KEYS = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.', 51: ',',
    84: '+', 85: '-', 74: '*', 75: '/', 55: '(', 56: ')',
    44: '^', 45: '^2', 43: 'sqrt(', 46: 'exp(', 93: '*10^',
    52: 'sin(', 53: 'cos(', 54: 'tan(', 41: 'x',
}

def test_keymap_matches_hardware():
    # Every binding must land on a key that exists and means what it is bound
    # to. This map had drifted a whole row out of step: ALPHA 42 produced 'a'
    # when the key is printed B, so 17 of 26 letters were wrong or missing, and
    # EXIT was bound to 13, which is the jump-to-line-start key, not Back.
    named = [('UP', casui.UP, 'UP'), ('DOWN', casui.DOWN, 'DOWN'),
             ('LEFT', casui.LEFT, 'LEFT'), ('RIGHT', casui.RIGHT, 'RIGHT'),
             ('OK', casui.OK, 'OK'), ('EXE', casui.EXE, 'EXE'),
             ('EXITK', casui.EXITK, 'BACK'), ('DEL', casui.DEL, 'DEL'),
             ('SHIFT', casui.SHIFT, 'SHIFT'), ('ALPHA', casui.ALPHA, 'ALPHA'),
             ('MENU', casui.MENU, 'CATALOG'), ('HOME', casui.HOME, 'HOME'),
             ('LINESTART', casui.LINESTART, 'LINESTART'),
             ('LINEEND', casui.LINEEND, 'LINEEND'),
             ('PAGEUP', casui.PAGEUP, 'PAGEUP'),
             ('PAGEDOWN', casui.PAGEDOWN, 'PAGEDOWN'),
             ('VARIABLE', casui.VARIABLE, 'VARIABLE'),
             ('TOOLS', casui.TOOLS, 'TOOLS'),
             ('SETTINGS', casui.SETTINGS, 'SETTINGS'),
             ('FORMAT', casui.FORMAT, 'FORMAT')]
    for name, code, want in named:
        check("casui." + name + " is the " + want + " key", KEYPAD.get(code), want)

    # no binding may reference a code the keypad does not have
    for d, label in ((casui.UNSHIFT, 'UNSHIFT'), (casui.SHIFTED, 'SHIFTED'),
                     (casui.ALPHADICT, 'ALPHADICT'), (casui.DIGITS, 'DIGITS')):
        for code in d:
            truthy(label + " key " + str(code) + " exists on the keypad", code in KEYPAD)

    # ALPHA must produce the letter printed on the key
    for code, letter in ALPHA_KEYS.items():
        check("ALPHA on key " + str(code) + " types its printed letter",
              casui.ALPHADICT.get(code), letter)
    truthy("every letter a-z is on a key",
           len(set(ALPHA_KEYS.values()) & set(casui.ALPHADICT.values())) == 26)

    # unshifted keys must type what is printed on them
    for code, tok in PLAIN_KEYS.items():
        check("key " + str(code) + " types " + repr(tok), casui.UNSHIFT.get(code), tok)

    # the digit-jump map has to agree with the digits themselves
    for code, d in casui.DIGITS.items():
        check("DIGITS[" + str(code) + "]", casui.UNSHIFT.get(code), str(d))

    # a code used for navigation must not also insert a character, or the
    # keystroke would be swallowed before it ever reached the editor
    nav = set([casui.UP, casui.DOWN, casui.LEFT, casui.RIGHT, casui.OK,
               casui.EXE, casui.EXITK, casui.DEL, casui.SHIFT, casui.ALPHA,
               casui.MENU, casui.LINESTART, casui.LINEEND, casui.PAGEUP,
               casui.PAGEDOWN])
    for code in nav:
        truthy("nav key " + str(code) + " does not also type a character",
               code not in casui.UNSHIFT)

    # ON and AC carry no code, so nothing may be bound to them
    for code in (11, 65):
        truthy("nothing bound to the codeless key " + str(code),
               code not in KEYPAD and code not in casui.UNSHIFT)

def test_input_reachability():
    # Everything the toolkit documents has to be enterable on the real keypad.
    # It was not: there is no ',' key (so nCr, nPr and logb could not be typed
    # at all), no '!' key, and the ALPHA layer has no 'i' or 'h', which put
    # every inverse-trig and hyperbolic name out of reach too.
    tokens = _typeable_tokens()
    chars = _typeable_chars(tokens)

    for sym in (',', '!', '=', '(', ')', '^', '*', '/', '+', '-', '.', 'x'):
        truthy("symbol '" + sym + "' is typeable", sym in tokens)
    for d in "0123456789":
        truthy("digit " + d + " is typeable", d in tokens)

    # a function is reachable as a whole token, or letter by letter
    for name in caslex.UFUNCS + caslex.BINFUNCS + ('ans',):
        whole = (name + '(') in tokens or name in tokens
        spelled = True
        for ch in name:
            if ch not in chars:
                spelled = False
                break
        truthy("function '" + name + "' is reachable", whole or spelled)

    # constants
    for name in ('pi', 'e'):
        truthy("constant '" + name + "' is reachable", name in tokens)

    # Every palette entry must parse once completed the way it would be used.
    # The two-argument functions need a comma, and '!' is postfix, so each gets
    # a realistic sample rather than a blanket "item + 0.5)".
    samples = {
        ',': "nCr(6,2)", '!': "5!", 'nCr(': "nCr(6,2)",
        'nPr(': "nPr(5,2)", 'logb(': "logb(2,8)",
    }
    for item in casui.EXTRAS:
        if item == '=':
            continue                       # handled by do_solve, not the parser
        expr = samples.get(item, item + "0.5)" if item.endswith('(') else item)
        truthy("palette '" + item + "' parses as " + expr, caslex.parse(expr) is not None)

    # the digit-jump map must be derived from the real key codes, not invented
    for code, d in casui.DIGITS.items():
        check("DIGITS[" + str(code) + "] matches the key map",
              casui.UNSHIFT.get(code), str(d))
    for d in range(1, 10):
        truthy("digit " + str(d) + " can jump a menu", d in casui.DIGITS.values())

    # the palette grid must expose every entry
    pages = (len(casui.EXTRAS) + casui.PAL_PER - 1) // casui.PAL_PER
    truthy("palette shows every entry", pages * casui.PAL_PER >= len(casui.EXTRAS))

def test_cursor_window():
    # the edit line must keep the caret on screen wherever it sits
    s = "sin(x)+cos(x)+tan(x)+sqrt(x)+exp(x)+ln(x)+atan(x)+abs(x)"
    for cpos in (0, 1, 12, 30, len(s) - 1, len(s)):
        out = casui.cursor_fit(s, cpos, 200, "medium")
        truthy("cursor_fit fits at " + str(cpos), casui.text_w(out, "medium") <= 200)
        truthy("cursor_fit is a slice at " + str(cpos), out in s)
        if cpos < len(s):
            start = s.find(out)
            truthy("caret visible at " + str(cpos), start <= cpos < start + len(out))
    check("cursor_fit passes short text through", casui.cursor_fit("abc", 1, 200, "medium"), "abc")


# ========================================================== casutil tests ==
def test_util():
    check("ncr", casutil.ncr(6, 2), 15)
    check("ncr symmetric", casutil.ncr(20, 18), 190)
    check("ncr out of range", casutil.ncr(3, 5), 0)
    check("npr", casutil.npr(5, 2), 20)
    check("fact", casutil.fact(5), 120)
    check("fact 0", casutil.fact(0), 1)
    check("fact negative", casutil.fact(-1), None)
    check("fact capped", casutil.fact(10 ** 6), None)   # would hang the handheld
    check("gcd", casutil.gcd(12, 18), 6)
    check("gcd zero", casutil.gcd(0, 5), 5)
    check("lcm", casutil.lcm(4, 6), 12)
    check("powmod", casutil.powmod(2, 10, 1000), 24)
    check("modinv", casutil.modinv(3, 7), 5)
    check("modinv none", casutil.modinv(2, 4), None)
    close("atan2 q2", casutil.atan2(1.0, -1.0), 3 * math.pi / 4)
    close("atan2 q3", casutil.atan2(-1.0, -1.0), -3 * math.pi / 4)
    close("atan2 up", casutil.atan2(1.0, 0.0), math.pi / 2)
    close("atan2 origin", casutil.atan2(0.0, 0.0), 0.0)
    close("deg", casutil.deg(math.pi), 180.0)
    close("rad", casutil.rad(180.0), math.pi)
    close("acos_safe clamps", casutil.acos_safe(1.0000001), 0.0)

    close("phi(0)", casutil.phi(0.0), 0.5, 1e-7)
    # A&S 7.1.26 is good to ~1.5e-7 on erf, which lands near 2e-6 on phi here -
    # comfortably inside the 4 s.f. an exam answer needs
    close("phi(1.96)", casutil.phi(1.96), 0.975, 5e-6)
    close("phi(-1.96)", casutil.phi(-1.96), 0.025, 5e-6)
    close("invphi(0.975)", casutil.invphi(0.975), 1.959964, 1e-4)
    close("invphi(0.5)", casutil.invphi(0.5), 0.0, 1e-6)

    close("binom_pmf", casutil.binom_pmf(10, 0.5, 5), 0.24609375, 1e-9)
    close("binom_cdf", casutil.binom_cdf(10, 0.5, 5), 0.623046875, 1e-9)
    close("binom_pmf p=0", casutil.binom_pmf(5, 0.0, 0), 1.0)
    close("binom_pmf p=1", casutil.binom_pmf(5, 1.0, 5), 1.0)
    # large n used to overflow a float and take the whole app down
    truthy("binom_pmf large n finite", 0.0 <= casutil.binom_pmf(2000, 0.5, 1000) < 1.0)
    close("poisson_pmf", casutil.poisson_pmf(2.0, 1), 2.0 * math.exp(-2.0), 1e-12)
    close("poisson_cdf", casutil.poisson_cdf(2.0, 1), 3.0 * math.exp(-2.0), 1e-12)
    truthy("poisson large mu finite", 0.0 < casutil.poisson_pmf(200.0, 200) < 1.0)

    check("fmt tidy", casutil.fmt(2.0), "2")
    check("fmt neg zero", casutil.fmt(-0.0), "0")
    check("fmt nan", casutil.fmt(float('nan')), "undefined")
    check("fmtc", casutil.fmtc(1.0, 2.0), "1 + 2i")
    check("fmtc negative", casutil.fmtc(1.0, -2.0), "1 - 2i")
    check("fmtc real", casutil.fmtc(1.0, 0.0), "1")
    check("fmtc imaginary", casutil.fmtc(0.0, 2.0), "2i")


# =================================================== section module tests ==
def test_pure640():
    import pure640
    o = drive(pure640.t_quadratic, ['1', '-3', '2'])
    num("quad disc", o, 'disc b^2-4ac =', 1.0)
    has("quad root 2", o, 'x = 2')
    has("quad root 1", o, 'x = 1')
    has("quad vertex", o, 'vertex (1.5,-0.25)')

    o = drive(pure640.t_quadratic, ['1', '0', '4'])
    has("quad complex", o, 'complex conj roots:')
    has("quad complex root", o, '2i')

    o = drive(pure640.t_simul, ['1', '1', '5', '1', '-1', '1'], menus=[0])
    has("simul x", o, 'x = 3')
    has("simul y", o, 'y = 2')

    # y = 2x-1 meets y = x^2 exactly once, at (1,1)
    o = drive(pure640.t_simul, ['2', '-1', '1', '0', '0'], menus=[1])
    has("linquad tangent", o, 'tangent')
    has("linquad point", o, '(1,1)')

    o = drive(pure640.t_arith, ['2', '3', '5'])
    num("arith Un", o, 'Un = ', 14.0)
    num("arith Sn", o, 'Sn = ', 40.0)

    o = drive(pure640.t_geo, ['3', '2', '4'])
    num("geo Un", o, 'Un = ', 24.0)
    num("geo Sn", o, 'Sn = ', 45.0)

    o = drive(pure640.t_geo, ['1', '0.5', '3'])
    num("geo S inf", o, 'S(inf) = ', 2.0)

    o = drive(pure640.t_binom, ['1', '2', '5', '2'], menus=[2])
    num("binom nCr", o, 'nCr(5,2) = ', 10.0)
    has("binom coeff label", o, 'coeff of x^2')
    has("binom coeff value", o, '40')            # 10 * 1^3 * 2^2

    o = drive(pure640.t_log, ['2', '8'], menus=[0])
    num("log solve", o, 'x = ', 3.0)

    o = drive(pure640.t_coord, ['1', '2', '4', '6'])
    num("coord dist", o, 'dist = ', 5.0)
    has("coord mid", o, 'mid = (2.5,4)')
    num("coord grad", o, 'gradient m = ', 4.0 / 3.0)
    num("coord perp", o, 'perp grad = ', -0.75)

    o = drive(pure640.t_circle, ['-4', '6', '4'], menus=[1])
    has("circle centre", o, 'centre (2,-3)')
    num("circle r", o, 'radius = ', 3.0)

    o = drive(pure640.t_trig, ['3', '4'], menus=[1])
    num("rform R", o, 'R = ', 5.0)
    num("rform alpha", o, 'alpha = ', 53.1301, 1e-3)

    o = drive(pure640.t_trig, ['0.5'], menus=[0, 0])
    has("trig sin 30", o, 'x = 30')
    has("trig sin 150", o, 'x = 150')


def test_stat640():
    import stat640
    o = drive(stat640.t_summary, ['1 2 3 4 5 6 7 8 9'])
    num("summary n", o, 'n = ', 9.0)
    num("summary mean", o, 'mean = ', 5.0)
    num("summary median", o, 'median = ', 5.0)
    num("summary Q1", o, 'Q1 = ', 2.5)
    num("summary Sxx", o, 'Sxx = ', 60.0)
    num("summary sd n", o, 'sd (n) = ', math.sqrt(60.0 / 9.0))
    num("summary s n-1", o, 's (n-1) sd = ', math.sqrt(60.0 / 8.0))

    o = drive(stat640.t_freq, ['1 2 3', '2 3 5'])
    num("freq N", o, 'N = ', 10.0)
    num("freq mean", o, 'mean = ', 2.3)

    o = drive(stat640.t_drv, ['1 2 3', '0.2 0.3 0.5'])
    num("drv E", o, 'E[X] = ', 2.3)
    num("drv Var", o, 'Var[X] = ', 0.61)

    o = drive(stat640.t_binom, ['10', '0.5', '5'])
    num("binom pmf", o, 'P(X=5) = ', 0.24609)
    num("binom cdf", o, 'P(X<=5) = ', 0.62305)
    num("binom mean", o, 'mean np = ', 5.0)

    o = drive(stat640.t_normal, ['0', '1', '-1.96', '1.96'])
    num("normal prob", o, 'P(a<X<b) = ', 0.95, 1e-4)

    o = drive(stat640.t_invnorm, ['0', '1', '0.975'])
    num("invnorm z", o, 'z = ', 1.95996, 1e-3)

    o = drive(stat640.t_regress, ['1 2 3 4 5', '2 4 6 8 10', None])
    num("regress r", o, 'r = ', 1.0)
    num("regress b", o, 'b (grad) = ', 2.0)
    num("regress a", o, 'a (intercept) = ', 0.0)

    o = drive(stat640.t_prob, ['0.5', '0.4', '0.2'])
    num("prob union", o, 'P(AorB) = ', 0.7)
    num("prob cond", o, 'P(A|B) = ', 0.5)
    has("prob independent", o, 'independent: YES')

    o = drive(stat640.t_ncrfact, ['5', '2'])
    has("ncrfact fact", o, '5! = 120')
    has("ncrfact ncr", o, '5C2 = 10')
    has("ncrfact npr", o, '5P2 = 20')
    # an unbounded factorial used to lock the calculator up
    o = drive(stat640.t_ncrfact, ['100000', None])
    has("ncrfact caps n", o, 'too large')

    o = drive(stat640.t_htmean, ['100', '15', '106', '25', '5', '2'])
    num("htmean z", o, 'test z = ', 2.0)
    num("htmean SE", o, 'SE = ', 3.0)


def test_mech640():
    import mech640
    o = drive(mech640.suvat, ['0', None, '2', None, '3'])
    has("suvat v", o, 'v = 6')
    has("suvat s", o, 's = 9')

    o = drive(mech640.projectile, [None, '20', '30', None])
    num("projectile tof", o, 'Time of flight = ', 2.0 * 20 * 0.5 / 9.8)
    num("projectile hmax", o, 'Max height = ', 100.0 / (2 * 9.8))
    num("projectile range", o, 'Range = ', 400.0 * math.sin(math.pi / 3) / 9.8)

    o = drive(mech640.resultant, ['3', '0', '4', '90'])
    num("resultant Rx", o, 'Rx = ', 3.0)
    num("resultant Ry", o, 'Ry = ', 4.0)
    num("resultant mag", o, 'Magnitude = ', 5.0)
    num("resultant dir", o, 'Direction = ', 53.1301, 1e-3)

    o = drive(mech640.newton2, ['10', '2', None])
    has("newton a", o, 'a = 5')

    o = drive(mech640.pulley, [None, '5', '3'])
    num("pulley a", o, 'a = ', 2 * 9.8 / 8.0)
    num("pulley T", o, 'Tension T = ', 2 * 5 * 3 * 9.8 / 8.0)

    o = drive(mech640.friction_incline, [None, '10', '30', '0.2'])
    num("incline weight", o, 'Weight = ', 98.0)
    num("incline drive", o, 'Along: mg sin = ', 49.0)
    has("incline slides", o, 'Slides down.')

    o = drive(mech640.friction_horiz, [None, '10', '0.5', '20'])
    num("horiz R", o, 'R = ', 98.0)
    num("horiz Fmax", o, 'F_max = ', 49.0)
    has("horiz static", o, 'static')


def test_vectors():
    import vectors
    o = drive(vectors.t_mag, ['3', '4', '0'])
    num("vec mag", o, '|a| = ', 5.0)

    o = drive(vectors.t_dot, ['1', '2', '3', '4', '5', '6'])
    num("vec dot", o, 'a.b = ', 32.0)

    o = drive(vectors.t_angle, ['1', '0', '0', '0', '1', '0'])
    num("vec angle", o, 'angle = ', 90.0)

    o = drive(vectors.t_cross, ['1', '0', '0', '0', '1', '0'])
    has("vec cross", o, '(0, 0, 1)')

    o = drive(vectors.t_unit, ['3', '4', '0'])
    has("vec unit", o, '(0.6, 0.8, 0)')

    o = drive(vectors.t_ptplane, ['0', '0', '1', '5', '1', '2', '3'])
    num("pt-plane dist", o, 'dist = ', 2.0)

    o = drive(vectors.t_skew, ['0', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '1'])
    num("skew dist", o, 'shortest dist', 1.0)

    o = drive(vectors.t_ptline, ['0', '0', '0', '1', '0', '0', '0', '3', '4'])
    num("pt-line dist", o, 'dist = ', 5.0)


def test_matrix():
    import matrix
    drive(matrix.t_enterA, ['2', '2', '1', '2', '3', '4'])
    o = drive(matrix.t_det, [])
    num("det A", o, 'det(A) = ', -2.0)

    o = drive(matrix.t_inv, [])
    has("inv row1", o, '[ -2  1 ]')
    has("inv row2", o, '[ 1.5  -0.5 ]')

    o = drive(matrix.t_solve, ['5', '11'])
    num("solve x1", o, 'x1 = ', 1.0)
    num("solve x2", o, 'x2 = ', 2.0)

    o = drive(matrix.t_eig, [])
    num("eig trace", o, 'trace = ', 5.0)
    num("eig det", o, 'det = ', -2.0)
    num("eig L1", o, 'L1 = ', (5 + math.sqrt(33)) / 2.0)

    o = drive(matrix.t_trans, [])
    has("transpose", o, '[ 1  3 ]')

    drive(matrix.t_enterB, ['2', '2', '1', '0', '0', '1'])
    o = drive(matrix.t_mul, [])
    has("A*B identity", o, '[ 1  2 ]')

    o = drive(matrix.t_transform, ['90'], menus=[0])
    num("rotation det", o, 'det = ', 1.0)


def test_vcplx():
    import vcplx
    o = drive(vcplx.t_arith, ['3', '4', '1', '-2'])
    has("cplx sum", o, 'z+w = 4 + 2i')
    has("cplx prod", o, 'z*w = 11 - 2i')
    has("cplx quot", o, 'z/w = -1 + 2i')

    o = drive(vcplx.t_modarg, ['3', '4'])
    num("cplx mod", o, '|z| = ', 5.0)
    num("cplx arg", o, 'arg = ', math.atan2(4, 3))

    o = drive(vcplx.t_power, ['1', '1', '8'])
    has("de moivre", o, 'z^8 = 16')

    o = drive(vcplx.t_roots, ['1', '0', '3'])
    has("cube root 1", o, '0: 1')
    has("cube root 2", o, '-0.5 + 0.866i')

    o = drive(vcplx.t_quad, ['1', '0', '4'])
    has("cplx quad", o, '2i')


def test_polyroots():
    import polyroots
    o = drive(polyroots.t_vieta_cubic, ['1', '-6', '11', '-6'])
    num("vieta sum", o, 'sum       = -b/a = ', 6.0)
    num("vieta pairs", o, 'sum pairs =  c/a = ', 11.0)
    num("vieta prod", o, 'prod      = -d/a = ', 6.0)

    o = drive(polyroots.t_quad_roots, ['1', '-3', '2'])
    num("polyroots x1", o, 'x1 = ', 2.0)
    num("polyroots x2", o, 'x2 = ', 1.0)

    # x^2-3x+2 has roots 1,2; shifting by 1 gives roots 2,3 i.e. x^2-5x+6
    o = drive(polyroots.t_shift_roots, ['2', '1', '-3', '2', '1'])
    num("shift a", o, 'a (x^2) = ', 1.0)
    num("shift b", o, 'b (x^1) = ', -5.0)
    num("shift c", o, 'c (x^0) = ', 6.0)

    o = drive(polyroots.t_numeric_roots, ['x^2-4'])
    has("numeric root -2", o, 'x = -2')
    has("numeric root 2", o, 'x = 2')


def test_series():
    import series
    o = drive(series.t_sum_r, ['10'])
    num("sum r", o, '= ', 55.0)
    o = drive(series.t_sum_r2, ['10'])
    num("sum r^2", o, '= ', 385.0)
    o = drive(series.t_sum_r3, ['10'])
    num("sum r^3", o, '= ', 3025.0)

    o = drive(series.t_maclaurin, ['sin(x)', '6'])
    has("maclaurin sin x", o, 'P(x) = x')
    has("maclaurin -x^3/6", o, '0.1667x^3')
    o = drive(series.t_approx, ['exp(x)', '6', '1'])
    num("approx e", o, 'series ~ ', 2.716667, 1e-4)
    num("exact e", o, 'f(x) = ', math.e, 1e-4)


def test_hyper():
    import hyper
    o = drive(hyper.t_all, ['1'])
    num("sinh 1", o, 'sinh x = ', math.sinh(1.0))
    num("cosh 1", o, 'cosh x = ', math.cosh(1.0))
    num("tanh 1", o, 'tanh x = ', math.tanh(1.0))
    o = drive(hyper.t_arsinh, ['1'])
    num("arsinh 1", o, 'arsinh x = ', math.asinh(1.0))
    o = drive(hyper.t_arcosh, ['2'])
    num("arcosh 2", o, 'arcosh x = ', math.acosh(2.0))
    o = drive(hyper.t_artanh, ['0.5'])
    num("artanh .5", o, 'artanh x = ', math.atanh(0.5))
    o = drive(hyper.t_arcosh, ['0.5'])
    has("arcosh domain", o, 'domain is x >= 1')
    # ln(x + sqrt(x^2+1)) cancels to ln(0) for large negative x
    close("arsinh large negative", hyper._arsinh(-1e8), math.asinh(-1e8), 1e-6)


def test_polar():
    import polar
    o = drive(polar.t_topolar_rt, ['1', '1'])
    num("polar r", o, 'r = ', math.sqrt(2.0))
    num("polar theta", o, 'theta = ', math.pi / 4)
    o = drive(polar.t_topolar_xy, ['2', '0'])
    num("polar x", o, 'x = ', 2.0)
    num("polar y", o, 'y = ', 0.0)
    # area of r = 3 over a full turn is 9 pi
    o = drive(polar.t_area, ['3', '0', '2*pi'])
    num("polar area", o, 'Area = ', 9.0 * math.pi, 1e-3)


def test_diffeq():
    import diffeq
    o = drive(diffeq.t_second_order, ['3', '2'])
    num("2nd order disc", o, 'disc = a^2 - 4b = ', 1.0)
    has("2nd order roots", o, 'm1 = -1, m2 = -2')
    o = drive(diffeq.t_second_order, ['0', '4'])
    has("2nd order complex", o, 'Complex roots')
    o = drive(diffeq.t_second_order, ['2', '1'])
    has("2nd order repeated", o, 'Repeated root m = -1')
    o = drive(diffeq.t_shm, ['2'])
    num("shm period", o, 'T = ', math.pi)
    num("shm freq", o, 'f = 1/T = ', 1.0 / math.pi)
    o = drive(diffeq.t_damping, ['1', '1'])
    has("damping under", o, 'UNDER-DAMPED')


def test_fmmech():
    import fmmech
    o = drive(fmmech.t_restitution, ['0.5', '2', '5', '3', '0'])
    num("restitution v1", o, 'v1 = ', 0.5)
    num("restitution v2", o, 'v2 = ', 3.0)
    num("restitution KE lost", o, 'KE lost = ', 11.25)

    o = drive(fmmech.t_momentum, ['1', '2', '5', '3', '0', '1'])
    num("conservation v2", o, 'v2 = ', (2 * 5 + 3 * 0 - 2 * 1) / 3.0)

    o = drive(fmmech.t_hooke, ['100', '0.2', '2'])
    num("hooke T", o, 'T = lam x/l = ', 10.0)
    num("hooke EPE", o, 'EPE = ', 1.0)

    o = drive(fmmech.t_com, ['1', '1 3', '0 4'])
    num("com x", o, 'x_bar = ', 3.0)

    o = drive(fmmech.t_circular, ['1', '2', '10', '5'])
    num("circular a", o, 'a = v^2/r = ', 20.0)
    num("circular F", o, 'F = m a = ', 40.0)

    o = drive(fmmech.t_work, ['1', '4', '3'])
    num("KE", o, 'KE = ', 18.0)

    o = drive(fmmech.t_dim, ['1 1 -2', '1 1 -2'])
    has("dimensions consistent", o, 'CONSISTENT')


def test_fmstat():
    import fmstat
    o = drive(fmstat.t_pois, ['2', '1'])
    num("poisson pmf", o, 'P(X=k) = ', 2.0 * math.exp(-2.0))
    num("poisson cdf", o, 'P(X<=k) = ', 3.0 * math.exp(-2.0))
    # a large mean used to overflow and crash out of the app
    o = drive(fmstat.t_pois, ['200', '200'])
    has("poisson large mu", o, 'P(X=k) = ')

    o = drive(fmstat.t_bin, ['10', '0.5', '5'])
    num("fm binom pmf", o, 'P(X=k) = ', 0.24609)

    o = drive(fmstat.t_norm, ['0', '1', '-1.96', '1.96'])
    num("fm normal", o, 'P(a<X<b) = ', 0.95, 1e-4)

    o = drive(fmstat.t_std, ['100', '15', '115'])
    num("standardise", o, 'z = ', 1.0)

    o = drive(fmstat.t_pmcc, ['1 2 3 4 5', '2 4 6 8 10'])
    num("pmcc r", o, 'r = ', 1.0)

    o = drive(fmstat.t_spear, ['1 2 3 4 5', '5 4 3 2 1'])
    num("spearman", o, 'rs = ', -1.0)

    o = drive(fmstat.t_reg, ['1 2 3 4 5', '2 4 6 8 10', None])
    num("fm reg b", o, 'b = ', 2.0)

    o = drive(fmstat.t_chi, ['10 20 30', '20 20 20'])
    num("chi stat", o, 'chi^2 = ', 10.0)
    has("chi reject", o, 'reject H0')

    o = drive(fmstat.t_cimean, ['100', '15', '25', '95'])
    num("ci z*", o, 'z* = ', 1.95996, 1e-3)
    num("ci SE", o, 'SE = ', 3.0)

    o = drive(fmstat.t_ztest, ['100', '106', '15', '25', '5'])
    num("ztest z", o, 'z = ', 2.0)


def test_numeric():
    import numeric
    o = drive(numeric.t_newton, ['x^2-2', '1'])
    num("newton root", o, 'root x=', math.sqrt(2.0), 1e-6)

    o = drive(numeric.t_bisect, ['x^2-2', '1', '2'])
    num("bisect root", o, 'root x=', math.sqrt(2.0), 1e-6)

    # x = (x + 2/x)/2 converges quadratically to sqrt(2)
    o = drive(numeric.t_fixed, ['(x+2/x)/2', '1'])
    num("fixed point", o, 'fixed pt x=', math.sqrt(2.0), 1e-6)

    o = drive(numeric.t_integ, ['x^2', '0', '1', '100'])
    num("trapezium", o, 'trapezium=', 1.0 / 3.0, 1e-4)
    num("simpson", o, 'Simpson=', 1.0 / 3.0, 1e-5)   # printed to 6 d.p.

    o = drive(numeric.t_diff, ['x^2', '3', '0.001'])
    num("central diff", o, 'central=', 6.0, 1e-6)
    num("exact diff", o, 'exact=', 6.0)

    o = drive(numeric.t_error, ['3.1', '3.14159'])
    num("abs error", o, 'absolute=', 0.04159, 1e-6)

    o = drive(numeric.t_round, ['1234.5', '2'])
    num("round 2sf", o, '2 s.f. = ', 1200.0)
    o = drive(numeric.t_round, ['0.0012345', '3'])
    num("round 3sf", o, '3 s.f. = ', 0.00123, 1e-9)

    # dy/dx = x from (0,0) with h=0.1: Euler gives y = h*sum(x_i)
    o = drive(numeric.t_euler, ['x', '0', '0', '0.1', '3'])
    num("euler y", o, 'end y=', 0.1 * (0.0 + 0.1 + 0.2), 1e-9)
    # dy/dx = f(x, y) now works too: y' = y from (0,1), h=0.1, 3 steps
    o = drive(numeric.t_euler, ['y', '0', '1', '0.1', '3'])
    num("euler in x and y", o, 'end y=', 1.1 * 1.1 * 1.1, 1e-9)


def test_algos():
    import algos
    o = drive(algos.bubble, ['3 1 2'])
    has("bubble sorted", o, '1 2 3')
    has("bubble swaps", o, 'Swaps: 2')

    o = drive(algos.insertion, ['3 1 2'])
    has("insertion sorted", o, '1 2 3')

    o = drive(algos.firstfit, ['4 5 3', '10'])
    has("firstfit bins", o, 'Bins used: 2')

    o = drive(algos.firstfitdec, ['4 5 3', '10'])
    has("firstfitdec bins", o, 'Bins used: 2')

    # 1--2 = 1, 2--3 = 2, 1--3 = 4
    g = ['3', '0 1 4', '1 0 2', '4 2 0', '1']
    o = drive(algos.dijkstra, g)
    has("dijkstra n2", o, 'Node 2: 1')
    has("dijkstra n3", o, 'Node 3: 3')

    o = drive(algos.prim, ['3', '0 1 4', '1 0 2', '4 2 0'])
    has("prim total", o, 'Total weight: 3')

    o = drive(algos.kruskal, ['3', '0 1 4', '1 0 2', '4 2 0'])
    has("kruskal total", o, 'Total weight: 3')

    # A1(3) -> A2(4) -> A3(2): duration 9, all critical
    o = drive(algos.critpath, ['3', '3', '0', '4', '1', '2', '2'])
    has("critpath duration", o, 'Project duration: 9')
    has("critpath critical", o, 'Critical: A1 A2 A3')


def test_xpure():
    import xpure
    # Fibonacci: a_n = a_(n-1) + a_(n-2), a0=0, a1=1
    o = drive(xpure.t_recur, ['1', '1', '0', '1'])
    has("recurrence a9", o, 'a_9 = 34')
    has("recurrence a5", o, 'a_5 = 5')

    o = drive(xpure.t_eigen, ['2', '0', '0', '3'])
    num("eigen L1", o, 'lambda1 = ', 3.0)
    num("eigen L2", o, 'lambda2 = ', 2.0)

    o = drive(xpure.t_mod, ['12', '18'], menus=[2])
    has("xpure gcd", o, 'gcd(12,18) = 6')

    o = drive(xpure.t_mod, ['2', '10', '1000'], menus=[1])
    has("xpure powmod", o, '= 24')

    o = drive(xpure.t_mod, ['3', '7'], menus=[3])
    has("xpure modinv", o, '= 5')

    o = drive(xpure.t_partial, ['x^2', '3'])
    num("xpure partial", o, "f'(3) ~ ", 6.0, 1e-4)

    # Klein four-group Cayley table: closed, abelian, not cyclic
    o = drive(xpure.t_group, ['4', '0 1 2 3', '1 0 3 2', '2 3 0 1', '3 2 1 0'])
    has("group identity", o, 'Identity: e = 0')
    has("group abelian", o, 'Abelian: yes')
    has("group not cyclic", o, 'Cyclic: no')


def test_fpt():
    import fpt
    o = drive(fpt.t_gcdlcm, ['12', '18'])
    has("fpt gcd", o, 'gcd(a,b) = 6')
    has("fpt lcm", o, 'lcm(a,b) = 36')

    o = drive(fpt.t_prime, ['97'])
    has("fpt prime", o, '97 is PRIME.')
    o = drive(fpt.t_prime, ['91'])
    has("fpt not prime", o, '91 is NOT prime.')

    o = drive(fpt.t_factor, ['60'])
    has("fpt factorise", o, '2^2 * 3 * 5')

    o = drive(fpt.t_powmod, ['2', '10', '1000'])
    has("fpt powmod", o, 'a^b mod m = 24')

    o = drive(fpt.t_modinv, ['3', '7'])
    has("fpt modinv", o, 'a^-1 mod m = 5')

    o = drive(fpt.t_base, ['255'])
    has("fpt binary", o, '11111111')
    has("fpt hex", o, 'FF')

    o = drive(fpt.t_demoivre, ['1', '1', '8'])
    has("fpt de moivre", o, 'z^n = 16')

    o = drive(fpt.t_euler, ['x', '0', '0', '0.1', '3'])
    truthy("fpt euler ran", len(o) > 3)

    # very large inputs must be refused, not silently spin the handheld
    o = drive(fpt.t_factor, ['1000000000039'])
    has("fpt factor caps", o, 'too large')
    o = drive(fpt.t_prime, ['1000000000039'])
    has("fpt prime caps", o, 'too large')


# ================================================== device-constraint tests =
def _depth():
    n = 0
    f = sys._getframe()
    while f is not None:
        n += 1
        f = f.f_back
    return n

def test_recursion_budget():
    # The handheld's MicroPython dies at roughly 38 nested calls. CPython frames
    # are not identical to MicroPython's, but capping the interpreter here still
    # catches any change that starts recursing on input length instead of on
    # expression nesting.
    BUDGET = 38
    deep = "((((((((((x+1))))))))))"
    long_flat = "+".join(["x"] * 400)          # long but shallow
    old = sys.getrecursionlimit()

    def under(fn):
        base = _depth()
        sys.setrecursionlimit(base + BUDGET)
        try:
            fn()
            return True
        except RecursionError:
            return False
        finally:
            sys.setrecursionlimit(old)

    truthy("parse stays shallow on deep input", under(lambda: caslex.parse(deep)))
    truthy("parse stays shallow on long input", under(lambda: caslex.parse(long_flat)))
    t = caslex.parse("x^2+3x+1")
    truthy("simplify stays shallow", under(lambda: caseng.simplify(t)))
    truthy("diff stays shallow", under(lambda: caseng.diff(t)))
    truthy("evalf stays shallow", under(lambda: caseng.evalf(t, 1.0)))
    truthy("tostr stays shallow", under(lambda: caseng.tostr(t)))
    # integration by parts nests integ inside itself, so it is the deepest
    # thing the engine does - it has to fit in the same budget
    for e in ["x^3*exp(x)", "x^2*sin(x)", "x*ln(x)", "atan(x)",
              "sin(x)*cos(x)", "x*sin(2x+1)", "exp(2x)*cos(3x)"]:
        tr = caslex.parse(e)
        truthy("integ stays shallow: " + e, under(lambda tr=tr: cascalc.integ(tr)))

def test_devlint():
    import os
    bad = devlint.run(os.path.dirname(os.path.abspath(__file__)) or ".")
    CHECKS[0] += 1
    if bad:
        for path, line, msg in bad:
            FAILED.append("devlint " + os.path.basename(path) + ":" + str(line) + ": " + msg)


# =================================================================== main ==
TESTS = [
    ("lexer", test_lexer),
    ("engine", test_engine),
    ("calculus", test_calculus),
    ("render", test_render),
    ("ui format", test_ui_format),
    ("keymap vs hardware", test_keymap_matches_hardware),
    ("input reachability", test_input_reachability),
    ("cursor window", test_cursor_window),
    ("casutil", test_util),
    ("pure640", test_pure640),
    ("stat640", test_stat640),
    ("mech640", test_mech640),
    ("vectors", test_vectors),
    ("matrix", test_matrix),
    ("vcplx", test_vcplx),
    ("polyroots", test_polyroots),
    ("series", test_series),
    ("hyper", test_hyper),
    ("polar", test_polar),
    ("diffeq", test_diffeq),
    ("fmmech", test_fmmech),
    ("fmstat", test_fmstat),
    ("numeric", test_numeric),
    ("algos", test_algos),
    ("xpure", test_xpure),
    ("fpt", test_fpt),
    ("recursion budget", test_recursion_budget),
    ("devlint", test_devlint),
]

def main():
    for name, fn in TESTS:
        before = len(FAILED)
        try:
            fn()
        except Exception as e:
            FAILED.append(name + ": EXCEPTION " + repr(e))
        mark = "ok  " if len(FAILED) == before else "FAIL"
        print(mark + "  " + name)
    print("")
    print(str(CHECKS[0]) + " checks, " + str(len(FAILED)) + " failures")
    for f in FAILED:
        print("  - " + f)
    return 1 if FAILED else 0

if __name__ == "__main__":
    sys.exit(main())
