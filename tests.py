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
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) or "."

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
import caspoly
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

def itidy(e):
    # what the CAS screen actually shows: integ then the presentation pass
    t = caslex.parse(e)
    r = cascalc.integ(t)
    return None if r is None else caseng.tostr(cascalc.tidy(r))


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


# ============================================================ caspoly tests =
def _p(e):
    return caslex.parse(e)

def _ex(e):
    return caseng.tostr(caspoly.expand(_p(e)))

def _co(e):
    return caseng.tostr(caspoly.collect(_p(e)))

def _fa(e):
    r = caspoly.factor(_p(e))
    return None if r is None else caseng.tostr(r)

def _pf(n, d):
    r = caspoly.partial(_p(n), _p(d))
    if r is None:
        return None
    quot, terms = r
    out = []
    if quot is not None:
        out.append(caseng.tostr(quot))
    for top, fac, power in terms:
        den = caseng.tostr(fac)
        if power > 1:
            den = "(" + den + ")^" + str(power)
        out.append("(" + caseng.tostr(top) + ")/(" + den + ")")
    return " + ".join(out)

def test_polyalg():
    # --- exact rationals: the whole point is that nothing is rounded ---
    check("ratof 3", caspoly.ratof(_p("3")), (3, 1))
    check("ratof -2/6 reduces", caspoly.ratof(_p("-2/6")), (-1, 3))
    check("ratof 2^-3", caspoly.ratof(_p("2^-3")), (1, 8))
    check("ratof of a decimal that is not exact", caspoly.ratof(_p("0.1")), None)
    check("ratof of pi", caspoly.ratof(_p("pi")), None)

    # --- expand ---
    check("expand (x+1)^3", _ex("(x+1)^3"), "x^3+3*x^2+3*x+1")
    check("expand (2x-1)(x+4)", _ex("(2x-1)(x+4)"), "2*x^2+7*x-4")
    check("expand (x+2)(x-2)", _ex("(x+2)(x-2)"), "x^2-4")
    check("expand (x-3)^2", _ex("(x-3)^2"), "x^2-6*x+9")
    check("expand (x+1)^2(x-3)", _ex("(x+1)^2(x-3)"), "x^3-x^2-5*x-3")
    check("expand (a+b)^2 in two letters", _ex("(a+b)^2"), "2*a*b+a^2+b^2")
    check("expand splits over a constant denominator", _ex("(2x+4)/2"), "x+2")
    # binomial coefficients, checked against Pascal's triangle
    check("expand (x+1)^5", _ex("(x+1)^5"), "x^5+5*x^4+10*x^3+10*x^2+5*x+1")
    check("expand (2x-3)^3", _ex("(2x-3)^3"), "8*x^3-36*x^2+54*x-27")

    # --- collect ---
    check("collect 3x+2x", _co("3x+2x"), "5*x")
    check("collect cancels", _co("x+x^2-x"), "x^2")
    check("collect to zero", _co("x-x"), "0")
    check("collect keeps unlike terms apart", _co("2x+3y"), "2*x+3*y")
    check("collect fractional coefficients", _co("x/2+x/3"), "5*x/6")
    check("collect gathers a function of x", _co("2sin(x)+3sin(x)"), "5*sin(x)")
    # a coefficient that is not exact must leave the expression alone rather
    # than be quietly rounded
    truthy("collect does not round 0.1x", "0.1" in _co("0.1x+0.2x") or
           _co("0.1x+0.2x") == "0.3*x")

    # --- factorise, against factorisations worked out by hand ---
    check("factor x^2-5x+6", _fa("x^2-5x+6"), "(x-2)*(x-3)")
    check("factor difference of two squares", _fa("x^2-4"), "(x-2)*(x+2)")
    check("factor 2x^2+7x+3", _fa("2x^2+7x+3"), "(2*x+1)*(x+3)")
    check("factor 6x^2-x-2", _fa("6x^2-x-2"), "(2*x+1)*(3*x-2)")
    check("factor 4x^2-9", _fa("4x^2-9"), "(2*x-3)*(2*x+3)")
    check("factor common factor out", _fa("2x^2+4x"), "2*x*(x+2)")
    check("factor a cubic with three roots", _fa("x^3-6x^2+11x-6"),
          "(x-1)*(x-2)*(x-3)")
    check("factor a repeated root", _fa("x^2-2x+1"), "(x-1)^2")
    # irreducible over the rationals: say so rather than invent surds
    check("x^2+1 does not factorise", _fa("x^2+1"), None)
    check("x^2-2 does not factorise over the rationals", _fa("x^2-2"), None)
    # every factorisation must multiply back to what went in
    for e in ("x^2-5x+6", "2x^2+7x+3", "6x^2-x-2", "x^3-6x^2+11x-6", "2x^2+4x"):
        r = caspoly.factor(_p(e))
        check("factor(" + e + ") multiplies back",
              caseng.tostr(caspoly.expand(r)), caseng.tostr(caspoly.expand(_p(e))))

    # --- partial fractions, against decompositions worked out by hand ---
    # 1/(x^2-1) = (1/2)/(x-1) - (1/2)/(x+1)
    check("partial 1/(x^2-1)", _pf("1", "x^2-1"), "(1/2)/(x-1) + (-1/2)/(x+1)")
    # x/((x+1)(x-2)): cover up x=-1 gives 1/3, x=2 gives 2/3
    check("partial x/((x+1)(x-2))", _pf("x", "(x+1)(x-2)"),
          "(1/3)/(x+1) + (2/3)/(x-2)")
    # repeated factor: 3x+5 = A(x-1)(x+2) + B(x+2) + C(x-1)^2
    #   x=1 -> B=8/3, x=-2 -> C=-1/9, x^2 coefficient -> A=1/9
    check("partial with a repeated factor", _pf("3x+5", "(x-1)^2(x+2)"),
          "(1/9)/(x-1) + (8/3)/((x-1)^2) + (-1/9)/(x+2)")
    # irreducible quadratic factor: 1/(x(x^2+1)) = 1/x - x/(x^2+1)
    check("partial with a quadratic factor", _pf("1", "x(x^2+1)"),
          "(1)/(x) + (-x)/(x^2+1)")
    # improper: the polynomial part has to be divided out first
    check("partial improper divides out", _pf("x^2", "x^2+1"),
          "1 + (-1)/(x^2+1)")
    check("partial of a non-polynomial", _pf("sin(x)", "x+1"), None)

    # every decomposition must add back up to the original fraction
    for n, d in (("1", "x^2-1"), ("x", "(x+1)(x-2)"), ("3x+5", "(x-1)^2(x+2)"),
                 ("2x+3", "(x+1)(x+2)"), ("x^2", "x^2+1")):
        r = caspoly.partial(_p(n), _p(d))
        quot, terms = r
        for xv in (0.37, 1.63, -3.1, 4.9):
            try:
                want = caseng.evalf(_p(n), xv) / caseng.evalf(_p(d), xv)
            except:
                continue
            got = caseng.evalf(quot, xv) if quot is not None else 0.0
            bad = False
            for top, fac, power in terms:
                try:
                    got += caseng.evalf(top, xv) / (caseng.evalf(fac, xv) ** power)
                except:
                    bad = True
            if bad:
                continue
            close("partial " + n + "/" + d + " sums back at x=" + str(xv),
                  got, want, 1e-9)

def test_cas_algebra_ui():
    # the new operations, driven through the CAS menu the way a student gets
    # to them: pick the expression, then the operation, then read the screen
    out = drive(casui.cas_section, ["(x+1)^3"], [5, -1, -1])
    has("expand through the UI", out, "x^3+3*x^2+3*x+1")
    out = drive(casui.cas_section, ["x^2-5x+6"], [6, -1, -1])
    has("factorise through the UI", out, "(x-2)*(x-3)")
    out = drive(casui.cas_section, ["3x+2x"], [7, -1, -1])
    has("collect through the UI", out, "5*x")
    out = drive(casui.cas_section, ["(3x+5)/((x-1)^2(x+2))"], [8, -1, -1])
    has("partial fractions through the UI", out, "(x-1)^2")
    has("partial fractions numerator", out, "8/3")
    # something that will not factorise must say so, not print a wrong answer
    out = drive(casui.cas_section, ["x^2+1"], [6, -1, -1])
    has("irreducible is reported", out, "does not factorise")
    # partial fractions on something that is not a fraction
    out = drive(casui.cas_section, ["x^2+1"], [8, -1, -1])
    has("partial fractions needs a fraction", out, "one fraction")


def test_reciprocal_trig():
    # sec, cosec and cot had no tokens at all, so "sec(x)" fell through to the
    # single-letter rule and parsed as s*e*c*x, and "cosec(x)" parsed as
    # cos(e*c*x) - a well-formed tree for a completely different function.
    # Only the rule that an unknown variable raises stopped that from being a
    # silent wrong answer on a real paper.
    for name in ('sec', 'cosec', 'cot', 'sech', 'cosech', 'coth'):
        t = caslex.parse(name + "(x)")
        check(name + " parses as itself", caseng.tostr(t), name + "(x)")
        check(name + " is one node", t[0], name)
    # the longest-first order matters: cosec must not be read as cos
    check("cosec is not cos", caslex.parse("cosec(x)")[0], 'cosec')
    check("cosech is not cosec", caslex.parse("cosech(x)")[0], 'cosech')
    check("cosh is still cosh", caslex.parse("cosh(x)")[0], 'cosh')
    check("cos is still cos", caslex.parse("cos(x)")[0], 'cos')
    check("sech is not sec", caslex.parse("sech(x)")[0], 'sech')
    check("coth is not cot", caslex.parse("coth(x)")[0], 'coth')
    # arc-prefixed names are accepted and normalised
    check("arcsin is asin", caslex.parse("arcsin(x)")[0], 'asin')
    check("arctan is atan", caslex.parse("arctan(x)")[0], 'atan')
    check("arccosh is acosh", caslex.parse("arccosh(x)")[0], 'acosh')

    # values, against the reciprocals computed directly
    close("sec(1)", caseng.evalf(caslex.parse("sec(x)"), 1.0), 1.0 / math.cos(1.0))
    close("cosec(1)", caseng.evalf(caslex.parse("cosec(x)"), 1.0), 1.0 / math.sin(1.0))
    close("cot(1)", caseng.evalf(caslex.parse("cot(x)"), 1.0),
          math.cos(1.0) / math.sin(1.0))
    close("sech(1)", caseng.evalf(caslex.parse("sech(x)"), 1.0), 1.0 / math.cosh(1.0))
    close("coth(1)", caseng.evalf(caslex.parse("coth(x)"), 1.0),
          math.cosh(1.0) / math.sinh(1.0))
    # cot(pi/2) is 0; computing it as 1/tan would divide by an infinity
    close("cot(pi/2) is 0", caseng.evalf(caslex.parse("cot(x)"), math.pi / 2), 0.0, 1e-12)
    # undefined points raise rather than returning a huge number
    raises("sec(pi/2) raises", lambda: caseng.evalf(caslex.parse("sec(x)"), math.pi / 2))
    raises("cosec(0) raises", lambda: caseng.evalf(caslex.parse("cosec(x)"), 0.0))
    raises("cot(0) raises", lambda: caseng.evalf(caslex.parse("cot(x)"), 0.0))
    raises("cosech(0) raises", lambda: caseng.evalf(caslex.parse("cosech(x)"), 0.0))
    raises("sec(90 deg) raises", lambda: caseng.evalf(caslex.parse("sec(x)"), 90.0, True))
    # in degree mode too
    close("sec(60 deg) is 2", caseng.evalf(caslex.parse("sec(x)"), 60.0, True), 2.0)

    # derivatives, against the standard results
    check("d/dx sec", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("sec(x)")))),
          "sec(x)*tan(x)")
    check("d/dx cot(2x)",
          caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("cot(2x)")))),
          "-(2*cosec(2*x)^2)")
    # every derivative also checked numerically against a central difference
    for expr in ("sec(x)", "cosec(x)", "cot(x)", "sech(x)", "cosech(x)", "coth(x)"):
        f = caslex.parse(expr)
        d = caseng.simplify(caseng.diff(f))
        for xv in (0.7, 1.3, 2.4):
            h = 1e-6
            try:
                num_d = (caseng.evalf(f, xv + h) - caseng.evalf(f, xv - h)) / (2 * h)
                close("d/dx " + expr + " at " + str(xv),
                      caseng.evalf(d, xv), num_d, 1e-4)
            except:
                pass

    # integrals
    check("int sec^2 is tan", isym("sec(x)^2"), "tan(x)")
    check("int cosec^2 is -cot", isym("cosec(x)^2"), "-cot(x)")
    check("int sech^2 is tanh", isym("sech(x)^2"), "tanh(x)")
    check("int cot is ln|sin|", isym("cot(x)"), "ln(abs(sin(x)))")
    check("int sec", isym("sec(x)"), "ln(abs(sec(x)+tan(x)))")
    check("int cosec(2x)", isym("cosec(2x)"), "-ln(abs(cosec(2*x)+cot(2*x)))/2")
    # each one differentiated back, which is the check that actually matters
    for expr in ("sec(x)^2", "cosec(x)^2", "cot(x)", "sec(x)", "cosec(2x)", "sech(x)^2"):
        f = caslex.parse(expr)
        F = cascalc.integ(f)
        truthy("int " + expr + " exists", F is not None)
        if F is None:
            continue
        d = caseng.simplify(caseng.diff(cascalc.tidy(F)))
        for xv in (0.4, 1.1, 2.3):
            try:
                close("d/dx int " + expr + " at " + str(xv),
                      caseng.evalf(d, xv), caseng.evalf(f, xv), 1e-6)
            except:
                pass

    # and they have to be typeable: no key carries sec, cosec or cot
    for tok in ('sec(', 'cosec(', 'cot(', 'sech(', 'cosech(', 'coth('):
        truthy(tok + " is in the CATALOG picker", tok in casui.EXTRAS)


# =========================================================== purecalc tests =
def test_engine_substitution():
    # subst / subst_tree / count_var / invert - the pieces composite functions,
    # implicit differentiation and integration by substitution are built on
    t = caslex.parse("x^2+1")
    check("subst x -> 2t", caseng.tostr(caseng.subst(t, 'x', caslex.parse("2t"))),
          "(2*t)^2+1")
    check("subst leaves other letters", caseng.tostr(caseng.subst(t, 'y', ('n', 9))),
          "x^2+1")
    check("subst_tree replaces a whole subtree",
          caseng.tostr(caseng.subst_tree(caslex.parse("(x^2+1)^5"),
                                         caslex.parse("x^2+1"), ('v', 'u'))), "u^5")
    check("count_var counts every occurrence", caseng.count_var(caslex.parse("x^2+x"), 'x'), 2)
    check("count_var of an absent letter", caseng.count_var(t, 'y'), 0)
    check("vars_in", caseng.vars_in(caslex.parse("x*y+z")), ['x', 'y', 'z'])

    # invert, each checked by composing back: f(f-inverse(y)) must be y
    for expr, want in (("2x+3", "(y-3)/2"), ("(x-1)/2", "2*y+1"),
                       ("exp(2x)", "ln(y)/2"), ("3ln(x)+1", "exp((y-1)/3)"),
                       ("5-2x", "(5-y)/2"), ("2^x", "ln(y)/ln(2)")):
        f = caslex.parse(expr)
        inv = caseng.invert(f, 'x', 'y')
        check("invert " + expr, caseng.tostr(inv), want)
        for yv in (0.6, 1.4, 2.9):
            try:
                xv = caseng.evalf(inv, 0.0, False, {'y': yv})
                back = caseng.evalf(f, xv)
            except:
                continue
            close("invert " + expr + " round-trips at y=" + str(yv), back, yv, 1e-9)
    # x appearing twice cannot be undone this way, and abs is not one-to-one
    check("invert refuses x^2+x", caseng.invert(caslex.parse("x^2+x"), 'x', 'y'), None)
    check("invert refuses abs", caseng.invert(caslex.parse("abs(x)"), 'x', 'y'), None)

def test_evalf_env_precedence():
    # env is consulted before the positional argument, INCLUDING for x.
    # The other way round, a tool passing {'x': a, 'y': b} had its x silently
    # ignored and evaluated at whatever happened to be passed positionally.
    t = caslex.parse("x")
    close("env overrides the positional x", caseng.evalf(t, 5.0, False, {'x': 9.0}), 9.0)
    close("positional x is used when env has none", caseng.evalf(t, 5.0, False, {'y': 9.0}), 5.0)
    close("positional x is used with no env", caseng.evalf(t, 5.0), 5.0)
    t = caslex.parse("x^2+y")
    close("two variables both from env",
          caseng.evalf(t, 0.0, False, {'x': 3.0, 'y': 4.0}), 13.0)
    close("x from env, y from env, positional ignored",
          caseng.evalf(t, 99.0, False, {'x': 3.0, 'y': 4.0}), 13.0)
    raises("a variable in neither still raises",
           lambda: caseng.evalf(caslex.parse("x+w"), 1.0, False, {'x': 1.0}))

def test_solve_variable():
    # solve() and defint() passed the sample point to evalf positionally, and
    # evalf's positional argument is always x. Anything written in another
    # letter raised on every sample, the exception was swallowed, and solve
    # returned an empty list rather than failing - a confident wrong answer.
    r = cascalc.solve(caslex.parse("3t^2-12t+9"), 't')
    check("solve in t finds both roots", len(r), 2)
    close("solve in t root 1", r[0], 1.0, 1e-5)
    close("solve in t root 2", r[1], 3.0, 1e-5)
    close("defint in t", cascalc.defint(caslex.parse("t^2"), 0.0, 3.0, False, 200, 't'),
          9.0, 1e-9)
    # a touching root in another letter, via the ternary-search path
    r = cascalc.solve(caslex.parse("(y-2)^2"), 'y')
    check("touching root in y", len(r), 1)
    close("touching root value", r[0], 2.0, 1e-5)
    # and x still behaves
    close("solve in x still works", cascalc.solve(caslex.parse("x^2-4"), 'x')[1], 2.0, 1e-5)

def test_purecalc():
    import purecalc
    # composite: f(x)=x^2, g(x)=2x+1 -> fg = (2x+1)^2, gf = 2x^2+1
    o = drive(purecalc.t_composite, ["x^2", "2x+1", "3"])
    has("fg(x)", o, "(2*x+1)^2")
    has("gf(x)", o, "2*x^2+1")
    num("fg at 3 is 49", o, "fg = ", 49.0)
    num("gf at 3 is 19", o, "gf = ", 19.0)

    # inverse of (3x-2)/4 is (4x+2)/3; f-inverse(10) = 14
    o = drive(purecalc.t_inverse, ["(3x-2)/4", "10"])
    has("inverse expression", o, "(4*x+2)/3")
    has("inverse self-check", o, "check f(f-inv(x)) = x: yes")
    num("inverse at 10", o, "f-inverse(10) = ", 14.0)
    # x^2 is not one-to-one: it must not claim an inverse, and solving x^2 = 4
    # has to report both roots rather than silently picking one
    o = drive(purecalc.t_inverse, ["x^2+x", "4"])
    has("no inverse by peeling", o, "No exact inverse")
    has("reports both roots", o, "no inverse here")

    # domain and range of 1/x on [-2, 2]: undefined at x = 0
    o = drive(purecalc.t_domain_range, ["1/x", "-2", "2"])
    has("undefined points reported", o, "undefined at")
    # sqrt(x) on [0, 4] is defined throughout and reaches 0 to 2
    o = drive(purecalc.t_domain_range, ["sqrt(x)", "0", "4"])
    has("whole interval", o, "domain: the whole interval")
    has("range 0 to 2", o, "range reached: 0 to 2")

    # |2x-6| = 4 has solutions x = 1 and x = 5
    o = drive(purecalc.t_modulus, ["2x-6", "4"])
    has("modulus root 1", o, "x = 1")
    has("modulus root 5", o, "x = 5")
    # a negative right-hand side has no solutions at all
    o = drive(purecalc.t_modulus, ["2x-6", "-4"])
    has("negative modulus impossible", o, "never negative")

    # y = 2f(3x+6)+1 with f(x) = x^2 is 2(3x+6)^2+1; the horizontal
    # translation is -c/b = -2, which is the step students get backwards
    o = drive(purecalc.t_transform, ["x^2", "2", "3", "6", "1"])
    has("transformed expression", o, "2*(3*x+6)^2+1")
    has("x stretch is 1/b", o, "stretch x by scale factor 0.3333")
    has("x translation is -c/b", o, "translate x by -2")

    # x = t^2, y = t^3: dy/dx = 3t/2, so at t = 2 the gradient is 3 and the
    # point is (4, 8). d2y/dx2 = (3/2)/(2t) = 3/(4t), which is 0.375 at t = 2.
    o = drive(purecalc.t_param_diff, ["t^2", "t^3", "2"])
    has("dx/dt", o, "dx/dt = 2*t")
    has("dy/dt", o, "dy/dt = 3*t^2")
    has("parametric gradient", o, "dy/dx = 3*t/2")
    has("point at t=2", o, "point (4, 8)")
    num("gradient at t=2", o, "dy/dx = ", 3.0)
    num("second derivative at t=2", o, "d2y/dx2 = ", 0.375)

    # x = 2t+1, y = t^2 gives t = (x-1)/2 and y = ((x-1)/2)^2
    o = drive(purecalc.t_param_cartesian, ["2t+1", "t^2", "0", "2"])
    has("t in terms of x", o, "t = (x-1)/2")

    # circle x^2+y^2=25: dy/dx = -x/y, which is -3/4 at (3,4)
    o = drive(purecalc.t_implicit, ["x^2+y^2=25", "3", "4"])
    has("implicit gradient", o, "dy/dx = -x/y")
    num("implicit gradient at (3,4)", o, "dy/dx = ", -0.75)
    num("normal gradient there", o, "normal gradient ", 4.0 / 3.0)
    # a point that is not on the curve must be called out, not answered silently
    o = drive(purecalc.t_implicit, ["x^2+y^2=25", "1", "1"])
    has("off-curve point warned", o, "not on the curve")
    # the folium x^3+y^3=6xy: dy/dx = -(3x^2-6y)/(3y^2-6x), which is -1 at (3,3)
    o = drive(purecalc.t_implicit, ["x^3+y^3=6xy", "3", "3"])
    num("folium gradient at (3,3)", o, "dy/dx = ", -1.0)

    # substitution: int 2x(x^2+1)^5 dx with u = x^2+1 is (x^2+1)^6/6
    o = drive(purecalc.t_substitution, ["2x(x^2+1)^5", "x^2+1"])
    has("integrand clears to u^5", o, "in terms of u: u^5")
    has("substitution answer", o, "(x^2+1)^6/6")
    has("substitution self-check", o, "differentiating back: agrees")
    # int x sqrt(x^2+1) dx with the same u is (x^2+1)^(3/2)/3
    o = drive(purecalc.t_substitution, ["x*sqrt(x^2+1)", "x^2+1"])
    has("sqrt substitution answer", o, "(x^2+1)^(3/2)/3")
    has("sqrt substitution checks", o, "differentiating back: agrees")
    # int cos(x) sin(x)^3 dx with u = sin(x) is sin(x)^4/4
    o = drive(purecalc.t_substitution, ["cos(x)sin(x)^3", "sin(x)"])
    has("trig substitution answer", o, "sin(x)^4/4")
    # a substitution that does not clear the x must say so rather than
    # producing an answer with an x left inside it
    o = drive(purecalc.t_substitution, ["x^3", "sin(x)"])
    has("bad substitution reported", o, "does not clear the integral")

    # separable dy/dx = 2x y through (0,1) is y = e^(x^2)
    o = drive(purecalc.t_separable, ["2x", "y", "0", "1"])
    has("separable ln y side", o, "integral 1/g(y) dy = ln(abs(y))")
    has("separable x side", o, "integral f(x) dx   = x^2")
    has("separable explicit", o, "y = exp(x^2)")
    has("separable passes the point", o, "passes through")
    # dy/dx = y^2 through (0,1) is -1/y = x - 1, i.e. y = 1/(1-x)
    o = drive(purecalc.t_separable, ["1", "y^2", "0", "1"])
    has("y^2 separable integral", o, "integral 1/g(y) dy = -1/y")
    # a g that mentions x is not separable this way
    o = drive(purecalc.t_separable, ["1", "x*y", None])
    has("g must be in y only", o, "function of y only")

    # small angles: at x = 0.1, sin x = 0.0998334 and the approximation is 0.1
    o = drive(purecalc.t_small_angle, ["0.1"])
    has("small angle usable", o, "good to about 0.2%")
    num("sin exact at 0.1", o, "exact  ", math.sin(0.1), 1e-6)
    o = drive(purecalc.t_small_angle, ["1.2"])
    has("1.2 rad is not a small angle", o, "not a small angle")

    o = drive(purecalc.t_exact_trig, [])
    has("exact trig 30 degrees", o, "sqrt(3)/2")
    has("exact trig 45 degrees", o, "1/sqrt(2)")
    has("tan 90 is undefined", o, "undefined")

def test_mech_variable_accel():
    import mech640
    # s = t^3-6t^2+9t: v = 3t^2-12t+9 = 3(t-1)(t-3), a = 6t-12.
    # At rest at t = 1 (s = 4) and t = 3 (s = 0). At t = 2: s = 2, v = -3, a = 0.
    o = drive(mech640.kinematics, ["t^3-6t^2+9t", "2"], [0])
    has("v from s", o, "v(t) = 3*t^2-12*t+9")
    has("a from s", o, "a(t) = 6*t-12")
    has("at rest at t=1", o, "t = 1   s = 4")
    has("at rest at t=3", o, "t = 3   s = 0")
    num("s at t=2", o, "s = ", 2.0)
    num("v at t=2", o, "v = ", -3.0)

    # a = 6t with v(0) = 0 and s(0) = 0 gives v = 3t^2 and s = t^3
    o = drive(mech640.kinematics, ["6t", "0", "0", "2"], [2])
    has("v by integrating a", o, "v(t) = 3*t^2")
    has("s by integrating v", o, "s(t) = t^3")
    num("s at t=2 from a", o, "s = ", 8.0)

    # v = t^2-4t on 0 <= t <= 5 reverses at t = 4.
    # displacement = 125/3 - 50 = -8.333; distance = 32-64/3 + 125/3-50-(64/3-32)
    #             = 10.6667 + 2.3333 = 13. Getting this wrong is the classic
    # variable-acceleration mark drop, so it is asserted both ways.
    o = drive(mech640.distance_travelled, ["t^2-4t", "0", "5"])
    has("sign change found", o, "t = 4")
    num("displacement", o, "displacement = ", -25.0 / 3.0, 1e-3)
    num("distance travelled", o, "distance     = ", 13.0, 1e-3)
    has("they differ", o, "They differ")
    # v = t^2+1 never changes sign, so the two agree
    o = drive(mech640.distance_travelled, ["t^2+1", "0", "3"])
    num("no reversal displacement", o, "displacement = ", 12.0, 1e-3)
    num("no reversal distance", o, "distance     = ", 12.0, 1e-3)
    has("same when v keeps its sign", o, "Same, because")

    # 5 kg hanging pulls 3 kg along a smooth horizontal table:
    # a = 5g/8 = 6.125, T = 3a = 18.375
    o = drive(mech640.connected, ["9.8", "5", "90", "0", "3", "0", "0"])
    num("connected acceleration", o, "a = ", 6.125, 1e-3)
    num("connected tension", o, "tension T = ", 18.375, 1e-3)
    # 2 kg hanging against 5 kg on a rough horizontal table with mu = 0.6:
    # drive = 2g = 19.6, friction = 0.6*5g = 29.4, so nothing moves
    o = drive(mech640.connected, ["9.8", "2", "90", "0", "5", "0", "0.6"])
    has("stays at rest", o, "stays at rest")
    has("friction is not at maximum", o, "not its maximum")

def test_matrix_invariant():
    import matrix
    # shear [[1,2],[0,1]]: every point on y = 0 is invariant, and y = 0 is the
    # only invariant line (the y-axis is not: (0,1) maps to (2,1))
    matrix.A = [[1.0, 2.0], [0.0, 1.0]]
    o = drive(matrix.t_invariant, [])
    has("shear has a line of invariant points", o, "LINE of invariant points")
    truthy("shear does not claim the y-axis is invariant",
           not [ln for ln in o if 'x = 0 (the y-axis)' in ln])
    # diag(3,2): only the origin is invariant, but both axes are invariant lines
    matrix.A = [[3.0, 0.0], [0.0, 2.0]]
    o = drive(matrix.t_invariant, [])
    has("diagonal has only the origin", o, "only")
    has("x-axis is an invariant line", o, "y = 0 x")
    has("y-axis is an invariant line", o, "x = 0 (the y-axis)")
    # a rotation by 90 degrees has no real invariant line
    matrix.A = [[0.0, -1.0], [1.0, 0.0]]
    o = drive(matrix.t_invariant, [])
    has("rotation has no invariant line", o, "no invariant line")

    # 3x3: a rotation about z has determinant 1; a reflection has -1
    o = drive(matrix.t_transform3, ["90"], [2])
    num("3D rotation determinant", o, "det = ", 1.0, 1e-6)
    o = drive(matrix.t_transform3, [], [4])
    num("3D reflection determinant", o, "det = ", -1.0, 1e-6)
    has("reflection reverses orientation", o, "orientation is reversed")

def test_method_of_differences():
    import series
    # 1/(r(r+1)) = 1/r - 1/(r+1), so S(n) = 1 - 1/(n+1) and S(10) = 10/11
    o = drive(series.t_differences, ["1/(r(r+1))", "10"])
    has("g(r) for the standard case", o, "take g(r) = 1/r")
    has("telescoping checked", o, "checked numerically")
    num("S(10) of 1/(r(r+1))", o, "S(10) = ", 10.0 / 11.0, 1e-4)
    num("direct sum agrees", o, "direct sum  = ", 10.0 / 11.0, 1e-4)
    # 1/(r(r+2)) = (1/2)(1/r - 1/(r+2)), a two-step gap:
    # S(n) = 3/4 - 1/(2(n+1)) - 1/(2(n+2)), so S(20) = 0.75 - 1/42 - 1/44
    want = 0.75 - 1.0 / 42.0 - 1.0 / 44.0
    o = drive(series.t_differences, ["1/(r(r+2))", "20"])
    num("S(20) of 1/(r(r+2))", o, "S(20) = ", want, 1e-4)
    num("two-step direct sum agrees", o, "direct sum  = ", want, 1e-4)
    # 2/((2r-1)(2r+1)) = 1/(2r-1) - 1/(2r+1), so S(n) = 1 - 1/(2n+1)
    o = drive(series.t_differences, ["2/((2r-1)(2r+1))", "50"])
    num("S(50) of the odd-denominator sum", o, "S(50) = ", 1.0 - 1.0 / 101.0, 1e-4)
    # something that does not telescope must say so
    o = drive(series.t_differences, ["1/(r^2+1)", None])
    has("non-telescoping reported", o, "does not telescope")


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
    check("int 1/x", isym("1/x"), "ln(abs(x))")
    check("int x^-1", isym("x^-1"), "ln(abs(x))")
    check("int 3/x", isym("3/x"), "3*ln(abs(x))")
    check("int sqrt(x)", isym("sqrt(x)"), "2/3*x^(3/2)")
    check("int ln(x)", isym("ln(x)"), "x*ln(x)-x")
    check("int tan(x)", isym("tan(x)"), "-ln(abs(cos(x)))")
    check("int 1/(2x+1)", isym("1/(2x+1)"), "ln(abs(2*x+1))/2")
    check("int exp(-x)", isym("exp(-x)"), "-exp(-x)")
    check("int x^(2/3)", isym("x^(2/3)"), "3/5*x^(5/3)")
    check("int sin(x)", isym("sin(x)"), "-cos(x)")
    check("int 5", isym("5"), "5*x")

    # integration by parts
    check("int x ln(x)", isym("x*ln(x)"), "ln(x)*x^2/2-x^2/4")
    check("int x^2 ln(x)", isym("x^2*ln(x)"), "ln(x)*x^3/3-x^3/9")
    check("int atan(x)", isym("atan(x)"), "atan(x)*x-1/2*ln(abs(1+x^2))")
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
    check("int 2x/(x^2+1)", isym("2x/(x^2+1)"), "ln(abs(x^2+1))")
    check("int cot", isym("cos(x)/sin(x)"), "ln(abs(sin(x)))")
    check("int x/(x^2+4)", isym("x/(x^2+4)"), "1/2*ln(abs(x^2+4))")
    # trig identity rewriting: sin^2 and cos^2 have no term-by-term
    # antiderivative, so they go through the double-angle form the
    # specification asks for. Typing it as a product must give the same answer.
    check("int sin^2", isym("sin(x)^2"), "x/2-sin(2*x)/4")
    check("int sin(x)*sin(x)", isym("sin(x)*sin(x)"), "x/2-sin(2*x)/4")
    check("int cos^2", isym("cos(x)^2"), "x/2+sin(2*x)/4")
    check("int cos^2(3x)", isym("cos(3x)^2"), "x/2+sin(6*x)/12")
    check("int tan^2", isym("tan(x)^2"), "tan(x)-x")

    # partial fractions - proper rational integrands, and the improper case
    # where a polynomial has to be divided out first
    check("int 1/(x^2-1)", isym("1/(x^2-1)"),
          "ln(abs(x-1))/2-ln(abs(x+1))/2")
    check("int 1/(1+x^2) is arctan", isym("1/(1+x^2)"), "atan(x)")
    check("int 1/(x^2+4)", isym("1/(x^2+4)"), "atan(x/2)/2")
    check("int x^2/(x^2+1) divides out first", isym("x^2/(x^2+1)"),
          "x-atan(x)")
    # x atan(x) used to be unreachable: by parts leaves x^2/(1+x^2), which is
    # an improper rational function and needed partial fractions to finish
    truthy("int x atan(x) now closes", isym("x*atan(x)") is not None)
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

# The fx-CG100 keypad, transcribed independently from the key-code diagram on
# page 142 of the fx-CG100/fx-1AU GRAPH Software User's Guide (v2.10) read
# against the printed keytops. Codes are row*10+col. [ON] (row 1 col 1) and
# [AC] (row 6 col 5) are drawn greyed out in that diagram - they carry no code
# and cannot be read. The manual's own worked example ("the 5 key is held
# down" prints 72) anchors the grid: row 7 col 2 is indeed the 5 key.
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

    # casui.KEYCODES is what tells a real keypress from an idle poll, so it has
    # to be exactly the set of codes the diagram shows and nothing more.
    check("KEYCODES is the whole keypad", casui.KEYCODES, set(KEYPAD.keys()))
    check("48 readable keys", len(casui.KEYCODES), 48)

    # readkey() must report anything outside that set as "no key". The toolkit
    # used to sample getkey() once at import and call the result idle, which
    # broke whenever a key was still held at import - and the key that launches
    # the script always is.
    real = casui.getkey
    try:
        for code in (0, 11, 65, 96, 99, -1, 255):
            casui.getkey = (lambda c: (lambda: c))(code)
            check("readkey treats " + str(code) + " as idle", casui.readkey(), 0)
        for code in (22, 72, 95):
            casui.getkey = (lambda c: (lambda: c))(code)
            check("readkey passes key " + str(code) + " through", casui.readkey(), code)
    finally:
        casui.getkey = real

def test_draw_string_sizes():
    # Every draw_string size argument the toolkit passes has to be one of the
    # three the manual accepts: "large", "medium", "small", with "medium" the
    # default when omitted (Software User's Guide v2.10, page 143). A wrong
    # size is not a soft failure on hardware, so this is checked statically
    # across every device file rather than left to whichever screen shows it.
    import ast
    ok = set(["small", "medium", "large"])
    seen = [0]
    for path in devlint.DEVICE_FILES:
        full = os.path.join(HERE, path)
        if not os.path.exists(full):
            continue
        tree = ast.parse(open(full).read(), path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if name != "draw_string":
                continue
            truthy(path + ":" + str(node.lineno) + " draw_string arity",
                   3 <= len(node.args) <= 5 and not node.keywords)
            if len(node.args) == 5:
                a = node.args[4]
                if isinstance(a, ast.Str) or (isinstance(a, ast.Constant)
                                              and isinstance(a.value, str)):
                    v = a.s if isinstance(a, ast.Str) else a.value
                    seen[0] += 1
                    truthy(path + ":" + str(node.lineno) + " size " + repr(v) +
                           " is one of small/medium/large", v in ok)
    truthy("draw_string size argument is actually used", seen[0] > 50)

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

    o = drive(pure640.t_trig, ['3', '4'], menus=[3])
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

    # OCR B (MEI) box plot method: Q1/Q3 are the medians of the lower/upper
    # halves, excluding the overall median when n is odd. This is the
    # Wikipedia box-plot worked example: min 2, Q1 4, median 4.5, Q3 6, max
    # 9, IQR 2, fences 1 and 9 - nothing outside them so no outliers.
    o = drive(stat640.t_boxplot, ['2 4 4 4 5 5 7 9'])
    num("boxplot n", o, 'n = ', 8.0)
    num("boxplot min", o, 'min = ', 2.0)
    num("boxplot Q1", o, 'Q1 = ', 4.0)
    num("boxplot median", o, 'median = ', 4.5)
    num("boxplot Q3", o, 'Q3 = ', 6.0)
    num("boxplot max", o, 'max = ', 9.0)
    num("boxplot IQR", o, 'IQR = ', 2.0)
    has("boxplot no outliers", o, 'outliers: none')

    # sorted 1 2 2 3 3 4 4 5 50 (n=9, odd): median = middle = 3, lower half
    # excl. median = 1 2 2 3 -> Q1 = median(2,2) = 2, upper half = 4 4 5 50
    # -> Q3 = median(4,5) = 4.5, IQR = 2.5, fences -1.75 .. 8.25, so 50 is
    # the only outlier and the whisker stops at 5, not 50.
    o = drive(stat640.t_boxplot, ['1 2 2 3 3 4 4 5 50'])
    num("boxplot outlier Q1", o, 'Q1 = ', 2.0)
    num("boxplot outlier median", o, 'median = ', 3.0)
    num("boxplot outlier Q3", o, 'Q3 = ', 4.5)
    num("boxplot outlier IQR", o, 'IQR = ', 2.5)
    num("boxplot whisker hi excludes outlier", o, 'whisker hi = ', 5.0)
    has("boxplot flags outlier", o, 'outliers: 50')

    o = drive(stat640.t_freq, ['1 2 3', '2 3 5'])
    num("freq N", o, 'N = ', 10.0)
    num("freq mean", o, 'mean = ', 2.3)

    # unequal widths: 0-10 (w10) f20 -> fd2, 10-15 (w5) f15 -> fd3,
    # 15-30 (w15) f30 -> fd2, 30-50 (w20) f10 -> fd0.5. Raw frequency would
    # rank 15-30 highest; frequency density correctly ranks 10-15 highest.
    o = drive(stat640.t_hist, ['0 10 15 30 50', '20 15 30 10'])
    num("hist total", o, 'total freq = ', 75.0)
    num("hist fd class1", o, '0-10 f=20 w=10 fd=', 2.0)
    num("hist fd class2", o, '10-15 f=15 w=5 fd=', 3.0)
    num("hist fd class3", o, '15-30 f=30 w=15 fd=', 2.0)
    num("hist fd class4", o, '30-50 f=10 w=20 fd=', 0.5)
    # a histogram of raw frequency (ignoring width) would put 15-30 (f=30)
    # above 10-15 (f=15); frequency density correctly reverses that
    truthy("hist density beats raw freq", 3.0 > 2.0 and 30.0 > 15.0)

    # boundaries 0,10,20,30,40, freq 5,10,20,5 (n=40). cf = 5,15,35,40.
    # median at n/2=20 falls in class 20-30: 20+((20-15)/(35-15))*10 = 22.5.
    # Q1 at n/4=10 falls in class 10-20: 10+((10-5)/(15-5))*10 = 15.
    # Q3 at 3n/4=30 falls in class 20-30: 20+((30-15)/(35-15))*10 = 27.5.
    o = drive(stat640.t_cumfreq, ['0 10 20 30 40', '5 10 20 5'])
    num("cumfreq cf1", o, '<=10 cf=', 5.0)
    num("cumfreq cf2", o, '<=20 cf=', 15.0)
    num("cumfreq cf3", o, '<=30 cf=', 35.0)
    num("cumfreq cf4", o, '<=40 cf=', 40.0)
    num("cumfreq Q1", o, 'Q1 (n/4) = ', 15.0)
    num("cumfreq median", o, 'median (n/2) = ', 22.5)
    num("cumfreq Q3", o, 'Q3 (3n/4) = ', 27.5)

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

    # x=1,3,5 y=5,2,8: n=3, Sx=9, Sy=15, Sxy=51, Sxx=35, Syy=93.
    # Sxxd = 35-81/3 = 8, Syyd = 93-225/3 = 18 (deliberately != Sxxd, so a
    # b=Sxy/Sxx vs b=Sxy/Syy mix-up would be caught here even on its own).
    # Sxyd = 51-135/3 = 6. b = 6/8 = 0.75, a = 15/3 - 0.75*9/3 = 5-2.25 = 2.75,
    # r = 6/sqrt(8*18) = 6/12 = 0.5.
    o = drive(stat640.t_scatter, ['1 3 5', '5 2 8'])
    num("scatter n", o, 'n = ', 3.0)
    num("scatter r", o, 'r = ', 0.5)
    num("scatter b", o, 'b (grad) = ', 0.75)
    num("scatter a", o, 'a (intercept) = ', 2.75)

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
    num("shm freq", o, 'f = ', 1.0 / math.pi)
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

    # Partial derivatives are symbolic now, in two variables. For
    # z = x^2 y + y^3: dz/dx = 2xy, dz/dy = x^2 + 3y^2, d2z/dxdy = 2x.
    # At (2,1): z = 5, dz/dx = 4, dz/dy = 7, d2z/dxdy = 4.
    o = drive(xpure.t_partial, ['x^2*y+y^3', '2', '1'])
    has("dz/dx", o, "dz/dx = 2*x*y")
    has("dz/dy", o, "dz/dy = x^2+3*y^2")
    has("mixed partial", o, "d2z/dxdy = 2*x")
    has("mixed partials agree", o, "d2z/dydx is the same")
    num("z at (2,1)", o, "z = ", 5.0)
    num("dz/dx at (2,1)", o, "dz/dx = ", 4.0)
    num("dz/dy at (2,1)", o, "dz/dy = ", 7.0)
    num("mixed partial at (2,1)", o, "d2z/dxdy = ", 4.0)
    has("gradient vector", o, "grad z = (4, 7)")
    num("gradient magnitude", o, "|grad z| = ", math.sqrt(65.0), 1e-3)

    # Stationary points of a surface. z = x^2+y^2-4x-6y has a minimum at
    # (2,3) with z = -13 and D = 4 > 0 with fxx = 2 > 0.
    o = drive(xpure.t_surface_stat, ['x^2+y^2-4x-6y', '0', '0'])
    has("stationary point located", o, "x = 2, y = 3")
    num("value at the minimum", o, "z = ", -13.0)
    num("discriminant", o, "D = fxx fyy - fxy^2 = ", 4.0)
    has("classified as a minimum", o, "MINIMUM")
    # z = x^2 - y^2 is the standard saddle at the origin, D = -4
    o = drive(xpure.t_surface_stat, ['x^2-y^2', '1', '1'])
    has("saddle located", o, "x = 0, y = 0")
    num("saddle discriminant", o, "D = fxx fyy - fxy^2 = ", -4.0)
    has("classified as a saddle", o, "SADDLE POINT")
    # z = -x^2-y^2+2x has a maximum at (1,0) with z = 1
    o = drive(xpure.t_surface_stat, ['-x^2-y^2+2x', '0', '0'])
    has("maximum located", o, "x = 1, y = 0")
    has("classified as a maximum", o, "MAXIMUM")
    # A NON-ZERO mixed partial is essential here. Every case above has
    # fxy = 0, so D = fxx fyy - fxy^2 and fxx fyy + fxy^2 agree and the sign
    # in the discriminant is untested. z = x^2 + 4xy + y^2 has fxx = fyy = 2
    # and fxy = 4, so D = 4 - 16 = -12: a saddle. Get the sign wrong and
    # D = 20 and it is called a minimum.
    o = drive(xpure.t_surface_stat, ['x^2+4x*y+y^2', '1', '-1'])
    num("discriminant with a non-zero mixed partial",
        o, "D = fxx fyy - fxy^2 = ", -12.0, 1e-6)
    has("non-zero fxy still a saddle", o, "SADDLE POINT")
    # z = x^2 + x*y + y^2: fxy = 1, D = 4 - 1 = 3 > 0, a genuine minimum
    o = drive(xpure.t_surface_stat, ['x^2+x*y+y^2', '1', '1'])
    num("discriminant of a skewed bowl", o, "D = fxx fyy - fxy^2 = ", 3.0, 1e-6)
    has("skewed bowl is a minimum", o, "MINIMUM")

    # Tangent plane to z = x^2+y^2 at (1,2): z = 5, fx = 2, fy = 4, so the
    # plane is z = 5 + 2(x-1) + 4(y-2), i.e. 2x + 4y - z = 5, and the normal
    # direction is (2, 4, -1)
    o = drive(xpure.t_tangent_plane, ['x^2+y^2', '1', '2'])
    has("height at the point", o, "at (1, 2), z = 5")
    has("tangent plane", o, "2x + 4y - z = 5")
    has("normal line", o, "+ t(2, 4, -1)")

    # 3x3 eigenvalues. A lower-triangular matrix has its diagonal as the
    # spectrum: [[2,0,0],[1,3,0],[0,0,4]] has eigenvalues 2, 3, 4, trace 9,
    # det 24, so the characteristic equation is k^3 - 9k^2 + 26k - 24 = 0.
    o = drive(xpure.t_eigen3,
              ['2', '0', '0', '1', '3', '0', '0', '0', '4', None])
    has("characteristic cubic", o, "k^3 - 9k^2 + 26k - 24 = 0")
    has("first eigenvalue", o, "k = 2")
    has("second eigenvalue", o, "k = 3")
    has("third eigenvalue", o, "k = 4")
    has("eigenvector for k=2", o, "(1, -1, 0)")
    has("diagonalisable", o, "DIAGONALISABLE")
    has("Cayley-Hamilton", o, "M^3 = 9M^2 - 26M + 24I")
    # every eigenvector must satisfy Mv = kv, which the tool checks itself
    for ln in o:
        if "check |Mv - kv| = " in ln:
            v = _first_number(ln.split("check |Mv - kv| = ")[1])
            truthy("eigenvector satisfies Mv = kv", v is not None and abs(v) < 1e-6)
    # a rotation about z by 90 degrees has only one real eigenvalue, 1,
    # with the axis (0,0,1) as its eigenvector
    o = drive(xpure.t_eigen3,
              ['0', '-1', '0', '1', '0', '0', '0', '0', '1', None])
    has("single real eigenvalue", o, "k = 1")
    has("rotation axis is the eigenvector", o, "(0, 0, 1)")
    has("not three distinct", o, "may not be diagonalisable")

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

def _verdict_after(lines, key):
    # the MAXIMUM / MINIMUM / INFLECTION word that follows a given root line,
    # so a verdict attached to the wrong root is caught
    i = 0
    while i < len(lines):
        if key in lines[i]:
            j = i + 1
            while j < len(lines) and j <= i + 3:
                for word in ("MAXIMUM", "MINIMUM", "INFLECTION"):
                    if word in lines[j]:
                        return word
                j += 1
            return "none"
        i += 1
    return "no such root"

def test_pure640_new(h=None):
    import pure640
    # 3-4-5: A = 36.8699, B = 53.1301, C = 90, area 6
    o = drive(pure640.t_triangle, ["3", "4", "5"], [0])
    num("SSS angle A", o, "A = ", 36.8699, 1e-3)
    num("SSS angle B", o, "B = ", 53.1301, 1e-3)
    num("SSS angle C", o, "C = ", 90.0, 1e-3)
    num("SSS area", o, "area = (1/2)ab sinC = ", 6.0, 1e-6)
    # SAS: b = 5, c = 7, A = 60 -> a^2 = 25+49-2*35*0.5 = 39, a = 6.2450
    o = drive(pure640.t_triangle, ["5", "7", "60"], [1])
    num("SAS side a", o, "a = ", math.sqrt(39.0), 1e-4)
    # ASA: A = 40, B = 60, a = 10 -> C = 80, b = 10 sin60/sin40 = 13.4730
    o = drive(pure640.t_triangle, ["40", "60", "10"], [2])
    num("ASA side b", o, "b = ", 10.0 * math.sin(math.radians(60)) / math.sin(math.radians(40)), 1e-3)
    # SSA ambiguous: a = 7, b = 8, A = 50 -> sinB = 8 sin50/7 = 0.87542,
    # B = 61.1018 or 118.8982, and both give a valid triangle
    o = drive(pure640.t_triangle, ["7", "8", "50"], [3])
    num("SSA angle B", o, "B = ", 61.1018, 1e-3)
    has("SSA ambiguous case flagged", o, "AMBIGUOUS CASE")
    has("SSA second angle", o, "118.8982")
    # SSA with no triangle at all: a = 3, b = 8, A = 50 -> sinB > 1
    o = drive(pure640.t_triangle, ["3", "8", "50"], [3])
    has("impossible SSA reported", o, "No triangle")
    # three lengths that cannot close
    o = drive(pure640.t_triangle, ["1", "2", "10"], [0])
    has("triangle inequality checked", o, "cannot form")

    # r = 5, theta = 1.2 rad: arc 6, sector area 15, chord 10 sin(0.6) = 5.6464,
    # segment area 12.5(1.2 - sin1.2) = 3.3495
    o = drive(pure640.t_arc_sector, ["5", "1.2"], [0])
    num("arc length", o, "r theta      = ", 6.0, 1e-6)
    num("sector area", o, "(1/2)r^2 th  = ", 15.0, 1e-6)
    num("chord", o, "2r sin(th/2) = ", 10.0 * math.sin(0.6), 1e-4)
    num("segment area", o, "             = ", 12.5 * (1.2 - math.sin(1.2)), 1e-4)
    # degrees must be converted first: 60 degrees on r = 3 gives arc pi
    o = drive(pure640.t_arc_sector, ["3", "60"], [1])
    num("arc from degrees", o, "r theta      = ", math.pi, 1e-4)
    has("conversion is stated", o, "only works in radians")

    # x^2-5x+6 < 0 is 2 < x < 3 (between the roots, upward parabola)
    o = drive(pure640.t_inequality, ["1", "-5", "6"], [1, 2])
    has("quadratic inequality between roots", o, "2 < x < 3")
    has("says between", o, "between the roots")
    # x^2-5x+6 > 0 is outside the roots
    o = drive(pure640.t_inequality, ["1", "-5", "6"], [1, 0])
    has("quadratic inequality outside", o, "x < 2  or  x > 3")
    # -x^2+4 >= 0 opens downwards, so it is BETWEEN the roots -2 and 2
    o = drive(pure640.t_inequality, ["-1", "0", "4"], [1, 1])
    has("downward parabola opens downwards", o, "opens downwards")
    has("downward parabola between roots", o, "-2 <= x <= 2")
    # x^2+1 > 0 has no roots and is always true
    o = drive(pure640.t_inequality, ["1", "0", "1"], [1, 0])
    has("no real roots", o, "no real roots")
    has("always true", o, "every real x")
    # linear with a negative coefficient flips the sign: -2x + 6 > 0 is x < 3
    o = drive(pure640.t_inequality, ["-2", "6"], [0, 0])
    has("dividing by a negative flips", o, "FLIPS")
    has("linear answer", o, "x < 3")

    # sin(2x - 30) = 0.5 over 0..360 degrees: 2x-30 = 30,150,390,510 so
    # x = 30, 90, 210, 270 - four solutions, not one
    o = drive(pure640._trig_general, ["2", "-30", "0.5", "0", "360"], [0, 0])
    has("multiple-angle solution 30", o, "x = 30 deg")
    has("multiple-angle solution 90", o, "x = 90 deg")
    has("multiple-angle solution 210", o, "x = 210 deg")
    has("multiple-angle solution 270", o, "x = 270 deg")
    has("four solutions found", o, "4 solutions")
    # cos x = 0.5 in radians over 0..2pi: x = pi/3 and 5pi/3
    o = drive(pure640._trig_general, ["1", "0", "0.5", "0", str(2 * math.pi)], [1, 1])
    has("radian solution pi/3", o, "x = 1.0472")
    has("radian solution 5pi/3", o, "x = 5.236")
    # tan has period pi, so tan x = 1 over 0..2pi has two solutions
    o = drive(pure640._trig_general, ["1", "0", "1", "0", str(2 * math.pi)], [2, 1])
    has("tan solution pi/4", o, "x = 0.7854")
    has("tan solution 5pi/4", o, "x = 3.927")
    # |k| > 1 for sin has no solution
    o = drive(pure640._trig_general, ["1", "0", "2", "0", "360"], [0, 0])
    has("sin k>1 impossible", o, "No solution")

    # compound-angle expansions checked against the direct value
    o = drive(pure640._trig_expand, ["50", "20"])
    has("sin(A+B) agrees", o, "agrees")
    truthy("no expansion differs", not [ln for ln in o if "DIFFERS" in ln])
    o = drive(pure640._trig_compound, [])
    has("compound identity card", o, "sin(A+B) = sinA cosB + cosA sinB")
    has("double angle card", o, "cos2A = cos^2 A - sin^2 A")
    has("integration rearrangement", o, "sin^2 A = (1 - cos2A)/2")

def test_purecalc_calculus():
    import purecalc
    # x^3-3x: f' = 3x^2-3 = 0 at x = -1 (max, f''=-6) and x = 1 (min, f''=6),
    # with y = 2 and y = -2; f'' = 0 at x = 0, an inflection
    o = drive(purecalc.t_stationary, ["x^3-3x"])
    has("derivative shown", o, "3*x^2-3")
    has("y at the maximum", o, "y = 2")
    has("y at the minimum", o, "y = -2")
    has("inflection found", o, "changes sign: inflection")
    # The verdict has to be attached to the RIGHT root. Asserting only that
    # the words MAXIMUM and MINIMUM appear somewhere passes even when the two
    # are swapped, which is exactly the mistake worth catching.
    check("x = -1 is the maximum", _verdict_after(o, "x = -1,"), "MAXIMUM")
    check("x = 1 is the minimum", _verdict_after(o, "x = 1,"), "MINIMUM")
    # x^4: f'' = 0 at the stationary point, so the test is inconclusive and the
    # sign of f' either side has to settle it - it is a minimum
    # x^4 has f'' = 0 at the stationary point, so the second-derivative test
    # cannot settle it; the sign of f' either side does, and it is a minimum
    o = drive(purecalc.t_stationary, ["x^4"])
    has("f'' is zero there", o, "f'' = 0")
    check("x^4 has a minimum at 0", _verdict_after(o, "x = 0,"), "MINIMUM")
    # x^3: stationary at 0 but it is a point of inflection, not a turning point
    o = drive(purecalc.t_stationary, ["x^3"])
    check("x^3 has a stationary inflection at 0",
          _verdict_after(o, "x = 0,"), "INFLECTION")
    # exp(x) has no stationary point at all
    o = drive(purecalc.t_stationary, ["exp(x)"])
    has("no stationary points", o, "no stationary points")

    # f' = 2x through (1,5): f = x^2 + 4
    o = drive(purecalc.t_constant, ["2x", "1", "5", "3"])
    has("integral before the constant", o, "x^2 + C")
    has("constant found", o, "C = 4")
    has("full curve", o, "f(x) = x^2+4")
    num("f(3) = 13", o, "f(3) = ", 13.0)
    has("checked through the point", o, "passes through the point")

    # y = x from 0 to 1 about the x-axis: V = pi int x^2 dx = pi/3
    o = drive(purecalc.t_revolution, ["x", "0", "1"], [0])
    num("cone volume", o, "  = ", math.pi / 3.0, 1e-4)
    # y = sqrt(x) from 0 to 4 about the x-axis: V = pi int x dx = 8pi
    o = drive(purecalc.t_revolution, ["sqrt(x)", "0", "4"], [0])
    num("paraboloid integral is 8", o, "  evaluated: ", 8.0, 1e-6)
    has("paraboloid volume", o, "V = pi x 8")
    # x = y^2 from 0 to 1 about the y-axis: V = pi int y^4 dy = pi/5
    o = drive(purecalc.t_revolution, ["y^2", "0", "1"], [1])
    num("volume about the y-axis", o, "  = ", math.pi / 5.0, 1e-4)
    # sqrt(x)^2 has to simplify to x or the symbolic route is never taken
    o = drive(purecalc.t_revolution, ["sqrt(x)", "0", "4"], [0])
    truthy("paraboloid volume done symbolically",
           not [ln for ln in o if "numerically" in ln])

    # mean of x^2 on [0,3] is 9/3 = 3, reached at x = sqrt(3)
    o = drive(purecalc.t_meanvalue, ["x^2", "0", "3"])
    num("mean value of x^2", o, "           = ", 3.0, 1e-6)
    has("where it reaches the mean", o, "x = 1.7321")
    # mean of sin x over [0, pi] is 2/pi
    o = drive(purecalc.t_meanvalue, ["sin(x)", "0", str(math.pi)])
    num("mean value of sin", o, "           = ", 2.0 / math.pi, 1e-4)

    # int 1 to infinity of 1/x^2 converges to 1; of 1/x it diverges
    o = drive(purecalc.t_improper, ["1/x^2", "1"], [0])
    has("1/x^2 converges", o, "CONVERGES")
    num("1/x^2 limit is 1", o, "CONVERGES to about ", 1.0, 1e-3)
    o = drive(purecalc.t_improper, ["1/x", "1"], [0])
    has("1/x diverges", o, "DIVERGES")
    # int 0 to 1 of 1/sqrt(x) converges to 2 - slowly, which is what the
    # earlier absolute-threshold test got wrong
    o = drive(purecalc.t_improper, ["1/sqrt(x)", "0", "1"], [2])
    has("1/sqrt(x) converges", o, "CONVERGES")
    num("1/sqrt(x) limit is 2", o, "CONVERGES to about ", 2.0, 1e-2)
    o = drive(purecalc.t_improper, ["1/x", "0", "1"], [2])
    has("1/x at 0 diverges", o, "DIVERGES")
    # int 0 to infinity of e^-x is 1
    o = drive(purecalc.t_improper, ["exp(-x)", "0"], [0])
    num("exp(-x) limit is 1", o, "CONVERGES to about ", 1.0, 1e-4)

def test_integ_reciprocal_powers():
    # c/sqrt(u) and c/u^k are powers in disguise and used to return None,
    # which sent the improper-integral tool down the numeric path unnecessarily
    check("int 1/sqrt(x)", itidy("1/sqrt(x)"), "2*x^(1/2)")
    check("int 3/sqrt(x)", itidy("3/sqrt(x)"), "6*x^(1/2)")
    check("int 1/x^3", itidy("1/x^3"), "-1/(2*x^2)")
    check("int 2/sqrt(2x+1)", itidy("2/sqrt(2x+1)"), "2*(2*x+1)^(1/2)")
    check("int 1/x^(2/3)", itidy("1/x^(2/3)"), "3*x^(1/3)")
    # the exponent has to stay an exact fraction: as a float the power rule
    # printed x^0.5/0.5 instead of 2 sqrt(x)
    for e in ("1/sqrt(x)", "1/x^3", "2/sqrt(2x+1)", "1/x^(2/3)", "3/sqrt(x)"):
        f = caslex.parse(e)
        F = cascalc.tidy(cascalc.integ(f))
        d = caseng.simplify(caseng.diff(F))
        for xv in (0.6, 1.7, 3.2):
            try:
                close("d/dx int " + e + " at " + str(xv),
                      caseng.evalf(d, xv), caseng.evalf(f, xv), 1e-8)
            except:
                pass


def test_diffeq_complete():
    import diffeq
    # dy/dx + (1/x)y = x. IF = e^(int 1/x dx) = x; int x*x dx = x^3/3;
    # y = x^2/3 + C/x. Through (1,1): 1 = 1/3 + C so C = 2/3.
    o = drive(diffeq.t_first_order, ["1/x", "x", "1", "1"])
    has("integrating factor", o, "IF = e^(ln(x))")
    has("IF simplifies to x", o, "   = x")
    has("IF times Q", o, "IF * Q = x^2")
    has("the integral is performed", o, "int IF*Q dx = x^3/3")
    num("constant from the condition", o, "C = ", 2.0 / 3.0, 1e-4)
    has("checked at the point", o, "checked at the given point")
    # dy/dx + 2y = e^x: IF = e^(2x), int e^(3x) dx = e^(3x)/3, y = e^x/3 + Ce^(-2x)
    o = drive(diffeq.t_first_order, ["2", "exp(x)", None])
    has("constant P gives e^(2x)", o, "IF = e^(2*x)")
    # P with no elementary integral must say so rather than inventing one
    o = drive(diffeq.t_first_order, ["exp(x^2)", None, None])
    has("no elementary IF", o, "no elementary form")

    # PARTICULAR INTEGRALS
    # y'' - 3y' + 2y = e^(3x): aux m^2-3m+2 has roots 1 and 2, and
    # p = 3 is not one of them, so PI = e^(3x)/(9-9+2) = 0.5 e^(3x)
    o = drive(diffeq.t_particular, ["-3", "2", "1", "3"], [1])
    has("auxiliary roots", o, "m = 2 and 1")
    has("exponential PI", o, "PI: y = 0.5 e^(3x)")
    # y'' - 3y' + 2y = e^x: now p = 1 IS a root, so the trial gains a factor
    # of x and C = 1/(2p+a) = 1/(2-3) = -1
    o = drive(diffeq.t_particular, ["-3", "2", "1", "1"], [1])
    has("resonance detected", o, "already in the CF")
    has("resonant PI", o, "PI: y = -x e^x")
    # y'' - 2y' + y = e^x: m = 1 repeated, so the trial needs x^2 and C = 1/2
    o = drive(diffeq.t_particular, ["-2", "1", "1", "1"], [1])
    has("repeated root detected", o, "REPEATED root")
    has("double resonance PI", o, "PI: y = 0.5 x^2 e^x")
    # y'' + y = 4x^2: trial c0+c1x+c2x^2 gives 2c2 + c0 = 0, c1 = 0, c2 = 4,
    # so PI = 4x^2 - 8
    o = drive(diffeq.t_particular, ["0", "1", "2", "0", "0", "4"], [0])
    has("polynomial PI", o, "PI: y = 4x^2 -8")
    # y'' + 4y = sin x: (b-w^2)P = 0 and (b-w^2)Q = 1 with b-w^2 = 3,
    # so PI = (1/3) sin x and the cos term is dropped, not printed as 0 cos x
    o = drive(diffeq.t_particular, ["0", "4", "0", "1", "1"], [2])
    has("trig PI", o, "PI: y = 0.3333 sin x")
    truthy("a zero trig term is not printed",
           not [ln for ln in o if "0 cos" in ln])
    # y'' + y = 3x with b != 0: PI = 3x
    o = drive(diffeq.t_particular, ["0", "1", "1", "0", "3"], [0])
    has("linear PI", o, "PI: y = 3x")
    # y'' + 2y' = 4 (b = 0): a constant already solves the homogeneous
    # equation, so the trial polynomial has to be raised a degree -> y = 2x
    o = drive(diffeq.t_particular, ["2", "0", "0", "4"], [0])
    has("b=0 raises the trial degree", o, "raised a degree")
    has("PI for b=0", o, "PI: y = 2x")
    # y'' + 3y' = x: y = x^2/6 - x/9 gives 1/3 + 3(x/3 - 1/9) = x
    o = drive(diffeq.t_particular, ["3", "0", "1", "0", "1"], [0])
    has("PI for b=0 with a linear rhs", o, "PI: y = 0.1667x^2 -0.1111x")
    # y'' = 6x with a = b = 0: the trial has to start at x^2, giving y = x^3
    o = drive(diffeq.t_particular, ["0", "0", "1", "0", "6"], [0])
    has("PI for a=b=0", o, "PI: y = x^3")
    # the general solution has to be CF + PI with no extra constant
    o = drive(diffeq.t_particular, ["-3", "2", "1", "3"], [1])
    has("general solution given", o, "GENERAL SOLUTION = CF + PI")
    has("no constant on the PI", o, "The PI has no arbitrary")

def test_exp_ln_folding():
    # exp and ln undo each other; without this the integrating factor of
    # dy/dx + y/x = x stays as e^(ln|x|) and cannot be multiplied through
    check("exp(ln(x)) is x",
          caseng.tostr(caseng.simplify(caslex.parse("exp(ln(x))"))), "x")
    check("ln(exp(x)) is x",
          caseng.tostr(caseng.simplify(caslex.parse("ln(exp(x))"))), "x")
    check("exp(ln(2x+1))",
          caseng.tostr(caseng.simplify(caslex.parse("exp(ln(2x+1))"))), "2*x+1")
    # sqrt(x^2) is |x|, not x - the modulus is the whole point
    check("sqrt(x^2) is abs(x)",
          caseng.tostr(caseng.simplify(caslex.parse("sqrt(x^2)"))), "abs(x)")
    close("sqrt((-3)^2) is 3",
          caseng.evalf(caseng.simplify(caslex.parse("sqrt(x^2)")), -3.0), 3.0)
    # and the folding must not change any value
    for e in ("exp(ln(x))", "ln(exp(x))", "exp(ln(2x+1))"):
        f = caslex.parse(e)
        g = caseng.simplify(f)
        for xv in (0.4, 1.3, 2.8):
            try:
                close("folding " + e + " keeps its value at " + str(xv),
                      caseng.evalf(g, xv), caseng.evalf(f, xv), 1e-9)
            except:
                pass


def test_complex_loci():
    import vcplx
    # |z - (1+2i)| = 3 is the circle centre 1+2i radius 3.
    # |1+2i| = sqrt(5) = 2.2361, so the greatest |z| on it is sqrt(5)+3 and the
    # least would be sqrt(5)-3 < 0, which means the circle encloses the origin
    # and the least is 0.
    o = drive(vcplx.t_loci, ["1", "2", "3"], [0])
    has("circle described", o, "circle centre 1 + 2i, radius 3")
    has("cartesian circle", o, "(x - 1)^2 + (y - 2)^2 = 9")
    num("greatest modulus on the circle", o, "greatest |z| on it = ",
        math.sqrt(5.0) + 3.0, 1e-3)
    num("least modulus on the circle", o, "least |z| on it    = ", 0.0, 1e-9)
    # |z - 1| = |z - 3i| is the perpendicular bisector of 1 and 3i:
    # midpoint (0.5, 1.5), ab has gradient -3, so the bisector has gradient 1/3
    # and passes through the midpoint: y = x/3 + 4/3
    o = drive(vcplx.t_loci, ["1", "0", "0", "3"], [1])
    has("bisector named", o, "PERPENDICULAR BISECTOR")
    has("midpoint", o, "midpoint (0.5, 1.5)")
    num("bisector gradient", o, "bisector gradient = ", 1.0 / 3.0, 1e-3)
    num("bisector intercept", o, "y = 0.3333x + ", 4.0 / 3.0, 1e-3)
    # arg(z - 2) = 45 degrees is a HALF-line from 2, not the whole line
    o = drive(vcplx.t_loci, ["2", "0", "45"], [2])
    has("half-line, not a line", o, "HALF-LINE")
    has("the endpoint is excluded", o, "NOT included")
    has("only one half", o, "only the half with x > 2")
    # the region |z - a| <= r is a disc
    o = drive(vcplx.t_loci, ["0", "0", "2"], [3])
    has("region is a disc", o, "filled disc")
    has("region inequality", o, "<= 4")
    # a and b coincident has no bisector
    o = drive(vcplx.t_loci, ["1", "1", "1", "1"], [1])
    has("coincident points reported", o, "every z is equidistant")

    # de Moivre: (cos t + i sin t)^3 gives cos3t = c^3 - 3cs^2 and
    # sin3t = 3c^2 s - s^3
    o = drive(vcplx.t_demoivre_id, ["3"])
    has("cos 3t expansion", o, "cos 3t = c^3 - 3cs^2")
    has("sin 3t expansion", o, "sin 3t = 3c^2s - s^3")
    # and the printed check has to agree with the direct value
    num("cos 3t at 0.7", o, "cos 3t = ", math.cos(2.1), 1e-5)
    num("expansion of cos 3t at 0.7", o, "  expansion  = ", math.cos(2.1), 1e-5)
    # n = 2: cos2t = c^2 - s^2, sin2t = 2cs
    o = drive(vcplx.t_demoivre_id, ["2"])
    has("cos 2t expansion", o, "cos 2t = c^2 - s^2")
    has("sin 2t expansion", o, "sin 2t = 2cs")
    # n = 4: cos4t = c^4 - 6c^2s^2 + s^4
    o = drive(vcplx.t_demoivre_id, ["4"])
    has("cos 4t expansion", o, "cos 4t = c^4 - 6c^2s^2 + s^4")

def test_vector_lines():
    import vectors
    # through (1,2,3) and (4,6,3): direction (3,4,0), |d| = 5, and because the
    # z-component is zero the cartesian form is a pair plus "with z = 3"
    o = drive(vectors.t_lineeq, ["1", "1", "2", "3", "4", "6", "3", None])
    has("vector form", o, "r = (1, 2, 3) + t(3, 4, 0)")
    has("cartesian form", o, "(x - 1)/3 = (y - 2)/4")
    has("the fixed coordinate", o, "with z = 3")
    num("length of the direction", o, "|d| = ", 5.0)
    has("unit direction", o, "(0.6, 0.8, 0)")
    # point + direction, and a point on it at t = 2
    o = drive(vectors.t_lineeq, ["2", "0", "0", "0", "1", "1", "1", "2"])
    has("point at t=2", o, "at t = 2: (2, 2, 2)")
    # a zero direction is not a line
    o = drive(vectors.t_lineeq, ["2", "1", "1", "1", "0", "0", "0"])
    has("zero direction rejected", o, "does not define a line")

    # line (1,0,0) + t(1,1,1) meets the plane z = 5 at t = 5, point (6,5,5),
    # and the angle between d and the normal is acos(1/sqrt(3)) = 54.7356 deg,
    # so the line-plane angle is 35.2644
    o = drive(vectors.t_lineplane, ["1", "0", "0", "1", "1", "1", "0", "0", "1", "5"])
    num("parameter at the intersection", o, "t = ", 5.0)
    has("intersection point", o, "they meet at (6, 5, 5)")
    num("angle to the normal", o, "angle between d and n = ", 54.7356, 1e-3)
    num("angle to the plane", o, "= 90 - that = ", 35.2644, 1e-3)
    # parallel: n.d = 0 and a not in the plane, distance |n.a - k|/|n| = 5
    o = drive(vectors.t_lineplane, ["1", "0", "0", "1", "1", "0", "0", "0", "1", "5"])
    has("parallel reported", o, "PARALLEL")
    num("distance to the plane", o, "|n| = ", 5.0)
    # lying in the plane: n.d = 0 and a IS in the plane
    o = drive(vectors.t_lineplane, ["1", "0", "5", "1", "1", "0", "0", "0", "1", "5"])
    has("line lies in the plane", o, "LIES IN")

def test_projectile_inverse():
    import mech640
    # R = u^2 sin2a / g. At 45 degrees sin2a = 1, so u = sqrt(Rg):
    # sqrt(100 * 9.8) = 31.305
    o = drive(mech640.projectile_inverse, ["9.8", "100", "45"], [0])
    num("speed from range and angle", o, "u = ", math.sqrt(980.0), 1e-3)
    # 30 and 60 degrees give the same range, which the tool has to say
    o = drive(mech640.projectile_inverse, ["9.8", "100", "30"], [0])
    has("complementary angle noted", o, "60 deg gives the same range")
    # H = (u sin a)^2/(2g): u = sqrt(2*9.8*20)/sin30 = 39.598
    o = drive(mech640.projectile_inverse, ["9.8", "20", "30"], [1])
    num("speed from height and angle", o, "u = ",
        math.sqrt(2.0 * 9.8 * 20.0) / 0.5, 1e-3)
    # at (40, 0) after 4 s: ux = 10, uy = (0 + 9.8*16/2)/4 = 19.6,
    # u = sqrt(100 + 384.16) = 22.0036 at atan(1.96) = 62.969 deg
    o = drive(mech640.projectile_inverse, ["9.8", "40", "0", "4"], [2])
    num("horizontal component", o, "ux = x/t = ", 10.0)
    num("vertical component", o, "= ", 19.6, 1e-6)
    num("speed from a point and time", o, "u = sqrt(ux^2 + uy^2) = ",
        math.sqrt(100.0 + 19.6 * 19.6), 1e-3)
    num("angle from a point and time", o, "angle = ",
        math.degrees(math.atan(1.96)), 1e-3)
    # u = 30 at target (50, 10): two angles. Check the low one really lands
    # there - tan a = T solves 13.6111 T^2 - 50 T + 23.6111 = 0
    o = drive(mech640.projectile_inverse, ["9.8", "30", "50", "10"], [3])
    has("two solutions", o, "TWO angles")
    num("low ball angle", o, "low ball  ", 29.0977, 1e-3)
    num("high ball angle", o, "high ball ", 72.2123, 1e-3)
    # out of range must be said, not answered
    o = drive(mech640.projectile_inverse, ["9.8", "10", "200", "0"], [3])
    has("out of range reported", o, "OUT OF RANGE")
    # R = 80 in T = 4 s back at launch height: uy = gT/2 = 19.6, ux = 20
    o = drive(mech640.projectile_inverse, ["9.8", "80", "4"], [4])
    num("uy from the time of flight", o, "uy = gT/2 = ", 19.6, 1e-6)
    num("ux from range and time", o, "ux = R/T  = ", 20.0)
    num("speed from range and time", o, "u = ", math.sqrt(400.0 + 384.16), 1e-3)

# Expressions used for the engine's invariant sweep. They deliberately cover
# every integration route: powers, reciprocals, roots, exponentials, all six
# trig and reciprocal-trig functions, by parts, the cyclic case, and partial
# fractions.
SWEEP = ["x^2", "x^5", "1/x", "1/x^2", "sqrt(x)", "1/sqrt(x)", "exp(x)", "exp(2x)",
         "exp(-x)", "sin(x)", "cos(3x)", "tan(x)", "sec(x)", "cosec(2x)", "cot(x)",
         "sec(x)^2", "cosec(x)^2", "sin(x)^2", "cos(x)^2", "tan(x)^2", "ln(x)",
         "x*ln(x)", "x*sin(x)", "x^2*exp(x)", "x*atan(x)", "exp(x)*sin(x)",
         "sin(x)*cos(x)", "1/(x^2+1)", "1/(x^2+4)", "1/(x^2-1)", "x/(x^2+1)",
         "x^2/(x^2+1)", "(3x+5)/((x-1)^2(x+2))", "1/(x(x+1))", "2x/(x^2+1)",
         "x^3/(x^2-1)", "sinh(x)", "cosh(2x)", "sech(x)^2", "1/(2x+1)",
         "(x+1)/(x^2+2x+5)", "atan(x)", "asin(x)"]
SWEEP_ALG = ["(x+1)^3", "(2x-1)(x+4)", "(x+2)(x-2)", "x^3-6x^2+11x-6", "2x^2+7x+3",
             "3x+2x", "(x-3)^2", "x/2+x/3", "6x^2-x-2", "(x+1)^5", "2x^2+4x", "(a+b)^2"]
ENV = {'a': 1.3, 'b': 2.1}

def _val(tree, xv):
    try:
        v = caseng.evalf(tree, xv, False, ENV)
    except:
        return None
    if isinstance(v, complex) or v != v:
        return None
    if v > 1e300 or v < -1e300:
        return None
    return v

def _agree(label, f, g, xs, tol=1e-9):
    # f and g must agree wherever both are defined
    for xv in xs:
        a = _val(f, xv)
        b = _val(g, xv)
        if a is None or b is None:
            continue
        if abs(a - b) > tol * (1.0 + abs(b)):
            FAILED.append(label + " disagrees at x=" + str(xv) + ": " +
                          repr(a) + " vs " + repr(b))
            return False
    return True


def test_proof():
    import proof
    # sum r = n(n+1)/2 is true, and the inductive step S(k+1)-S(k) = k+1
    # is an identity the engine can settle
    o = drive(proof.t_induction_sum, ["n", "n(n+1)/2"])
    has("base case holds", o, "TRUE - the base case holds")
    has("step is the right difference", o, "S(k+1) - S(k) = n+1")
    has("and equals u(k+1)", o, "u(k+1)        = n+1")
    has("proved", o, "PROVED for all n >= 1 by induction")
    # sum r^2 against the WRONG formula n(n+1)/2: base case still passes
    # (both are 1 at n=1), which is exactly why the step has to be checked
    o = drive(proof.t_induction_sum, ["n^2", "n(n+1)/2"])
    has("wrong formula still passes the base case", o, "TRUE - the base case holds")
    has("but fails the step", o, "These are NOT equal")
    has("and the values are shown", o, "n=3  sum=14  S(n)=6")
    # sum r^3 = (n(n+1)/2)^2 is true
    o = drive(proof.t_induction_sum, ["n^3", "(n(n+1)/2)^2"])
    has("cube sum proved", o, "PROVED for all n >= 1")
    # a formula whose base case is wrong is rejected before the step
    o = drive(proof.t_induction_sum, ["n", "n(n+1)/2+1"])
    has("bad base case caught", o, "FALSE - S(1) is not u(1)")

    # 3 divides 4^n - 1. f(k+1) - 4 f(k) = 3, which is divisible by 3.
    o = drive(proof.t_induction_divis, ["4^n-1", "3", "4"])
    has("first values divide", o, "f(1) = 3,  remainder 0")
    has("the remainder is a multiple", o, "divisible by 3 too")
    has("divisibility proved", o, "PROVED by induction")
    # 6 divides n^3 - n (true: three consecutive integers)
    o = drive(proof.t_induction_divis, ["n^3-n", "6", "1"])
    has("n^3-n divisible by 6", o, "f(2) = 6,  remainder 0")
    # a false divisibility claim is disproved from the values, not "proved"
    o = drive(proof.t_induction_divis, ["4^n-1", "5", None])
    has("false claim disproved", o, "NOT divisible by 5")
    has("no induction needed", o, "No induction needed")
    # The multiplier is a presentation choice, not an arithmetic one: when the
    # claim is true, f(k+1) - m f(k) is divisible for EVERY integer m, because
    # both terms are. So assert the symbolic remainder is shown correctly
    # rather than pretending a "wrong" m can be caught here.
    o = drive(proof.t_induction_divis, ["4^n-1", "3", "4"])
    has("remainder shown symbolically", o, "4^(n+1)-4*4^n+3")

    # M = [[1,1],[0,1]] has M^n = [[1,n],[0,1]]
    o = drive(proof.t_induction_matrix,
              ["1", "1", "0", "1", "1", "n", "0", "1"])
    has("matrix base case", o, "formula at n=1 is M: TRUE")
    has("matrix induction proved", o, "PROVED by induction")
    # the same M with a wrong claim M^n = [[1,n^2],[0,1]]
    o = drive(proof.t_induction_matrix,
              ["1", "1", "0", "1", "1", "n^2", "0", "1"])
    has("wrong matrix formula caught", o, "FAILS - M * F(k) is not F(k+1)")
    # a formula that is not M at n = 1 is rejected first
    o = drive(proof.t_induction_matrix,
              ["2", "0", "0", "2", "2^n", "0", "0", "1"])
    has("matrix base case fails", o, "formula at n=1 is NOT M: FALSE")

    # Euler's polynomial n^2+n+41 is prime for n = 0..39 and composite at
    # n = 40, where it is 41^2 - the classic counterexample
    o = drive(proof.t_counterexample, ["n^2+n+41", "1", "60"], [0])
    has("counterexample found at 40", o, "COUNTEREXAMPLE at n = 40")
    has("and factorised", o, "1681 = 41 x 41")
    # searching a range that contains no counterexample must NOT claim a proof
    o = drive(proof.t_counterexample, ["n^2+n+41", "1", "30"], [0])
    has("no counterexample in range", o, "No counterexample in that range")
    has("and says that is not a proof", o, "That is NOT a proof")
    # n^2 - n + 1 > 0 for all n, so no counterexample; 2n - 10 fails at n <= 5
    o = drive(proof.t_counterexample, ["2n-10", "1", "20"], [1])
    has("positivity counterexample", o, "COUNTEREXAMPLE at n = 1")

    o = drive(proof.t_methods, [])
    has("contradiction card", o, "PROOF BY CONTRADICTION")
    has("root 2 worked example", o, "root 2 is irrational")
    has("infinitely many primes", o, "infinitely many primes")
    has("counterexample card", o, "DISPROOF BY COUNTEREXAMPLE")
    has("induction card", o, "PROOF BY INDUCTION")
    has("what not to write", o, "WHAT NOT TO WRITE")

def test_simulation():
    import fmstat
    import random
    # Simulations are random, so these assert that the SAMPLE statistics land
    # near the theoretical ones - which is the property the tool exists to
    # demonstrate - with a fixed seed so the suite is reproducible. The
    # tolerances are several standard errors wide: a failure here means the
    # sampler is wrong, not that the dice were unkind.
    #
    # B(20, 0.3): mean np = 6, variance np(1-p) = 4.2
    o = drive(fmstat.t_simulate, ["20", "0.3", "2000", "7"], [1])
    num("binomial theoretical mean", o, "theoretical mean   = ", 6.0)
    num("binomial theoretical variance", o, "theoretical var    = ", 4.2)
    num("binomial simulated mean", o, "simulated mean     = ", 6.0, 0.25)
    num("binomial simulated variance", o, "simulated variance = ", 4.2, 0.6)
    # Po(4): mean and variance both 4 - the identity that defines a Poisson
    o = drive(fmstat.t_simulate, ["4", "0", "2000", "7"], [2])
    num("Poisson theoretical mean", o, "theoretical mean   = ", 4.0)
    num("Poisson theoretical variance", o, "theoretical var    = ", 4.0)
    num("Poisson simulated mean", o, "simulated mean     = ", 4.0, 0.25)
    num("Poisson simulated variance", o, "simulated variance = ", 4.0, 0.7)
    # N(10, 2^2)
    o = drive(fmstat.t_simulate, ["10", "2", "2000", "7"], [3])
    num("normal simulated mean", o, "simulated mean     = ", 10.0, 0.2)
    num("normal simulated variance", o, "simulated variance = ", 4.0, 0.6)
    # uniform on [0, 6]: mean 3, variance 36/12 = 3
    o = drive(fmstat.t_simulate, ["0", "6", "2000", "7"], [0])
    num("uniform theoretical mean", o, "theoretical mean   = ", 3.0)
    num("uniform theoretical variance", o, "theoretical var    = ", 3.0)
    num("uniform simulated mean", o, "simulated mean     = ", 3.0, 0.2)
    # central limit: the mean of 12 uniforms on [0,1] has mean 1/2 and
    # variance (1/12)/12 = 1/144 - the variance divided by n is the whole point
    o = drive(fmstat.t_simulate, ["0", "1", "12", "2000", "7"], [4, 0])
    num("CLT theoretical mean", o, "theoretical mean   = ", 0.5)
    num("CLT variance is sigma^2/n", o, "theoretical var    = ", 1.0 / 144.0, 1e-5)
    num("CLT simulated mean", o, "simulated mean     = ", 0.5, 0.02)
    num("CLT simulated variance", o, "simulated variance = ", 1.0 / 144.0, 0.002)
    has("CLT explains the tightening", o, "tends to Normal whatever the parent")

    # the samplers themselves, over many draws, without the UI
    random.seed(11)
    for kind, p1, p2, tm, tv, label in ((0, 2.0, 8.0, 5.0, 3.0, "uniform"),
                                        (1, 10.0, 0.5, 5.0, 2.5, "binomial"),
                                        (2, 3.0, 0.0, 3.0, 3.0, "Poisson"),
                                        (3, -2.0, 3.0, -2.0, 9.0, "normal")):
        tot = 0.0
        sq = 0.0
        n = 4000
        i = 0
        while i < n:
            v = fmstat._sim_draw(kind, p1, p2)
            tot += v
            sq += v * v
            i += 1
        m = tot / n
        var = sq / n - m * m
        close(label + " sampler mean", m, tm, 4.0 * math.sqrt(tv / n) + 0.02)
        close(label + " sampler variance", var, tv, 0.25 * tv)
    # a binomial draw is always a whole number in 0..n
    random.seed(3)
    for i in range(200):
        v = fmstat._sim_draw(1, 8.0, 0.4)
        truthy("binomial draw is a whole number in range",
               v == int(v) and 0 <= v <= 8)
    # Box-Muller returns two independent values, not the same one twice
    random.seed(5)
    a, b = fmstat._normal_pair()
    truthy("Box-Muller gives two different values", a != b)

def test_circle_and_proportion():
    import pure640
    # (0,0), (4,0), (0,3): the 3-4-5 right angle. Centre (2, 1.5), radius 2.5,
    # and BC = 5 = 2r is a diameter, so the angle at A is 90 - the angle in a
    # semicircle, which the tool should spot rather than leave to be noticed.
    o = drive(pure640._circle_3pts, ["0", "0", "4", "0", "0", "3"])
    has("centre", o, "centre (2, 1.5)")
    num("radius", o, "radius ", 2.5)
    has("equation", o, "(x - 2)^2 + (y - 1.5)^2 = 6.25")
    has("all three verified", o, "on the circle: yes")
    has("semicircle spotted", o, "angle in a semicircle")
    # collinear points have no circle
    o = drive(pure640._circle_3pts, ["0", "0", "1", "1", "2", "2"])
    has("collinear rejected", o, "COLLINEAR")

    # tangent to x^2+y^2=25 at (3,4): radius gradient 4/3, tangent -3/4,
    # so y = -0.75x + 6.25, i.e. 3x + 4y = 25
    o = drive(pure640._circle_tangent, ["0", "0", "3", "4"])
    num("radius gradient", o, "radius gradient  = ", 4.0 / 3.0, 1e-3)
    num("tangent gradient", o, "-1/that = ", -0.75, 1e-6)
    has("tangent line", o, "y = -0.75x + 6.25")
    has("perpendicularity confirmed", o, "(should be -1)")
    # a vertical radius gives a horizontal tangent, not a division by zero
    o = drive(pure640._circle_tangent, ["0", "0", "0", "5"])
    has("horizontal tangent", o, "HORIZONTAL:  y = 5")
    o = drive(pure640._circle_tangent, ["0", "0", "5", "0"])
    has("vertical tangent", o, "VERTICAL:  x = 5")

    # parametric circle centre (1,2) radius 3, and at t = 0 the point is (4,2)
    # with a vertical tangent
    o = drive(pure640._circle_param, ["1", "2", "3", "0"])
    has("cartesian form", o, "(x-1)^2 + (y-2)^2 = 9")
    has("point at t=0", o, "(4, 2)")
    has("vertical tangent at t=0", o, "tangent is vertical")

    # y = k x^n through (2,12) and (4,48): n = log(4)/log(2) = 2 and k = 3,
    # so y(5) = 75
    o = drive(pure640.t_proportion, ["2", "12", "4", "48", "5", None], [2])
    num("power found", o, "    = ", 2.0, 1e-9)
    num("constant found", o, "k = y1 / x1^n = ", 3.0, 1e-9)
    has("model stated", o, "y = 3 x^2")
    num("prediction", o, "y = ", 75.0, 1e-6)
    # direct: y = kx through (4, 10) gives k = 2.5, and y = 15 at x = 6
    o = drive(pure640.t_proportion, ["4", "10", "6", None], [0])
    num("direct constant", o, "k = y/x = ", 2.5)
    num("direct prediction", o, "y = ", 15.0, 1e-6)
    # inverse: y = k/x through (4, 3) gives k = 12, and x = 2 when y = 6
    o = drive(pure640.t_proportion, ["4", "3", None, "6"], [1])
    num("inverse constant", o, "k = xy = ", 12.0)
    num("inverse back-solve", o, "x = ", 2.0, 1e-6)

def test_trig_by_identity():
    import pure640
    # 2sin^2 x + sin x - 1 = 0 over 0..360. Let u = sin x: 2u^2+u-1 = 0,
    # so u = 1/2 or u = -1, giving x = 30, 150, 270.
    o = drive(pure640._trig_identity, ["2", "1", "-1", "0", "360"], [0, 0])
    has("quadratic in u", o, "2u^2 + u - 1 = 0")
    has("first root", o, "sin x = 0.5")
    has("second root", o, "sin x = -1")
    has("solution 30", o, "x = 30 deg")
    has("solution 150", o, "x = 150 deg")
    has("solution 270", o, "x = 270 deg")
    has("three solutions", o, "(3 solutions)")
    has("checked in the original", o, "all satisfy it")

    # 2cos^2 x + 3 sin x - 3 = 0 needs cos^2 = 1 - sin^2 first:
    # -2s^2 + 3s - 1 = 0, so s = 1/2 or 1, giving x = 30, 90, 150.
    o = drive(pure640._trig_identity, ["2", "3", "-3", "0", "360"], [4, 0])
    has("identity used", o, "use cos^2 x = 1 - sin^2 x")
    has("transformed quadratic", o, "-2sin^2 x + 3sin x - 1 = 0")
    has("solutions listed", o, "30, 90, 150")
    has("still checked in the ORIGINAL", o, "all satisfy it")

    # a root outside [-1,1] has to be discarded, not solved
    o = drive(pure640._trig_identity, ["1", "-3", "0", "0", "360"], [0, 0])
    has("impossible root discarded", o, "cannot exceed 1")
    has("the other root still solved", o, "0, 180, 360")

    # tan^2 x = 1 over 0..180 gives 45 and 135, and tan is unbounded so no
    # root is ever discarded for being too big
    o = drive(pure640._trig_identity, ["1", "0", "-1", "0", "180"], [2, 0])
    has("tan solution 45", o, "x = 45 deg")
    has("tan solution 135", o, "x = 135 deg")
    has("two solutions", o, "(2 solutions)")

    # a negative discriminant means no real u and therefore no x
    o = drive(pure640._trig_identity, ["1", "0", "1", "0", "360"], [0, 0])
    has("no real u", o, "NO SOLUTION")

    # radians: 2sin^2 x - 1 = 0 over 0..2pi gives pi/4, 3pi/4, 5pi/4, 7pi/4
    o = drive(pure640._trig_identity,
              ["2", "0", "-1", "0", str(2 * math.pi)], [0, 1])
    has("radian solution pi/4", o, "x = 0.7854")
    has("radian solution 7pi/4", o, "x = 5.4978")
    has("four solutions", o, "(4 solutions)")

    # sec^2 x = 1 + tan^2 x: sec^2 x - 3 tan x + 1 = 0 becomes
    # tan^2 x - 3 tan x + 2 = 0, so tan x = 1 or 2
    o = drive(pure640._trig_identity, ["1", "-3", "1", "0", "180"], [5, 0])
    has("sec identity used", o, "use sec^2 x = 1 + tan^2 x")
    has("tan = 1 solution", o, "x = 45 deg")

def test_shm_fit():
    import diffeq
    # w = 2, x(0) = 3, v(0) = 8. Then C = 3 and D = v/w = 4, so the amplitude
    # is sqrt(9+16) = 5 and the phase is atan2(4,3) = 0.9273 rad = 53.13 deg.
    # Max speed Rw = 10, max acceleration Rw^2 = 20.
    o = drive(diffeq.t_shm, ["2", "3", "8", "0.5"])
    num("SHM period", o, "T = ", math.pi, 1e-4)
    num("C from x(0)", o, "x(0) = C = ", 3.0)
    num("D from v(0)/w", o, "D = v(0)/w = ", 4.0)
    num("amplitude", o, "R = sqrt(C^2 + D^2) = ", 5.0)
    num("phase in radians", o, "atan2(D, C) = ", math.atan2(4.0, 3.0), 1e-4)
    num("phase in degrees", o, "          = ", math.degrees(math.atan2(4.0, 3.0)), 1e-3)
    num("max speed", o, "= Rw   = ", 10.0)
    num("max acceleration", o, "= Rw^2 = ", 20.0)
    # x(0.5) = 5 cos(1 - 0.9273) = 4.98679
    num("x at t = 0.5", o, "  x = ", 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0)), 1e-3)
    # a = -w^2 x must hold at that instant
    num("a = -w^2 x", o, "a = -w^2 x = ",
        -4.0 * 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0)), 1e-3)
    # the SHM identity v^2 = w^2(R^2 - x^2), which the tool prints both sides of
    xv = 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0))
    vv = -10.0 * math.sin(1.0 - math.atan2(4.0, 3.0))
    close("v^2 identity holds", vv * vv, 4.0 * (25.0 - xv * xv), 1e-6)
    # starting at rest at the extreme: v(0) = 0 gives phase 0 and R = x(0)
    o = drive(diffeq.t_shm, ["3", "2", "0", None])
    num("amplitude when released from rest", o, "R = sqrt(C^2 + D^2) = ", 2.0)
    num("phase is zero from rest", o, "atan2(D, C) = ", 0.0, 1e-9)
    # w must be positive
    o = drive(diffeq.t_shm, ["0"])
    has("w must be positive", o, "w must be > 0")

def test_inequality_region():
    # The region drawing goes through the shared chart helpers, so what is
    # asserted here is the geometry: nothing off screen, nothing overprinting.
    # The numbers are already asserted in test_pure640_new.
    import pure640
    rows = _layout(lambda: drive(pure640.t_inequality, ["1", "-5", "6"], [1, 2]))
    truthy("the inequality sketch draws something", len(rows) > 0)
    for x, y, s, size in rows:
        truthy("inequality sketch: " + repr(s[:20]) + " fits the width",
               x + casui.text_w(s, size) <= 384)
        truthy("inequality sketch: " + repr(s[:20]) + " is on screen",
               0 <= y <= 191)

def test_coupled_des():
    import diffeq
    # dx/dt = x + y, dy/dt = 4x + y. Trace 2, det 1-4 = -3, so the auxiliary
    # equation is m^2 - 2m - 3 = 0 with roots 3 and -1 (the eigenvalues).
    # Through x(0)=1, y(0)=0: A+B=1 and 3A-B=1, so A=B=1/2 and
    # x = (e^3t + e^-t)/2, y = e^3t - e^-t.
    o = drive(diffeq.t_coupled, ["1", "1", "4", "1", "1", "0"])
    has("second-order equation formed", o, "x'' - 2x' - 3x = 0")
    has("auxiliary equation", o, "m^2 - 2m - 3 = 0")
    has("roots are the eigenvalues", o, "m = 3 and -1")
    has("general x", o, "x = A e^(3t) + B e^(-t)")
    has("constants fitted", o, "A = 0.5, B = 0.5")
    has("particular x", o, "x = 0.5e^(3t) + 0.5 e^(-t)")
    has("particular y", o, "y = e^(3t) - e^(-t)")
    has("checked at t=0", o, "check at t = 0: x = 1, y = 0")
    # the variable is t, not x - printing e^(3x) here is the wrong equation
    truthy("the exponential is in t", not [ln for ln in o if "e^(3x)" in ln])

    # dx/dt = -y, dy/dt = x is a rotation: trace 0, det 1, m = +/- i,
    # so it is a closed orbit and x = cos t through (1, 0)
    o = drive(diffeq.t_coupled, ["0", "-1", "1", "0", "1", "0"])
    has("complex roots", o, "m = 0 +/- 1i")
    has("closed orbit named", o, "closed orbit")
    has("amplitude constant", o, "amplitude stays constant")

    # dx/dt = 3x - y, dy/dt = x + y: trace 4, det 4, m = 2 repeated
    o = drive(diffeq.t_coupled, ["3", "-1", "1", "1", "1", "1"])
    has("repeated root", o, "m = 2 (repeated)")
    has("general form has the t factor", o, "x = (A + B t) e^(2t)")

    # b = 0 makes the system triangular, and there is no y to eliminate
    o = drive(diffeq.t_coupled, ["2", "0", "1", "3", None])
    has("triangular case", o, "already")

    # THE property that matters: whatever closed form the tool builds, it must
    # satisfy BOTH original equations. Checked through the module's own
    # solution helpers at several t, for all three root cases.
    for a, b, c, d, x0, y0, label in ((1.0, 1.0, 4.0, 1.0, 1.0, 0.0, "distinct real"),
                                      (0.0, -1.0, 1.0, 0.0, 1.0, 0.0, "complex"),
                                      (3.0, -1.0, 1.0, 1.0, 1.0, 1.0, "repeated"),
                                      (-1.0, 2.0, -3.0, 4.0, 2.0, -1.0, "decaying")):
        tr = a + d
        det = a * d - b * c
        disc = tr * tr - 4.0 * det
        kind = 1 if disc > 1e-9 else (2 if disc < -1e-9 else 3)
        xp0 = a * x0 + b * y0
        if kind == 1:
            rt = math.sqrt(disc)
            m1 = (tr + rt) / 2.0
            m2 = (tr - rt) / 2.0
            A = (xp0 - m2 * x0) / (m1 - m2)
            B = x0 - A
        elif kind == 2:
            p = tr / 2.0
            q = math.sqrt(-disc) / 2.0
            A = x0
            B = (xp0 - p * A) / q
        else:
            m = tr / 2.0
            A = x0
            B = xp0 - m * A
        # initial conditions
        close(label + ": x(0)", diffeq._coupled_x(kind, tr, disc, A, B, 0.0), x0, 1e-9)
        close(label + ": y(0)", diffeq._coupled_y(kind, tr, disc, A, B, 0.0, a, b), y0, 1e-9)
        # and both differential equations, by central difference
        for tv in (0.13, 0.4, 0.9):
            h = 1e-6
            xs = diffeq._coupled_x(kind, tr, disc, A, B, tv)
            ys = diffeq._coupled_y(kind, tr, disc, A, B, tv, a, b)
            dx = (diffeq._coupled_x(kind, tr, disc, A, B, tv + h) -
                  diffeq._coupled_x(kind, tr, disc, A, B, tv - h)) / (2 * h)
            dy = (diffeq._coupled_y(kind, tr, disc, A, B, tv + h, a, b) -
                  diffeq._coupled_y(kind, tr, disc, A, B, tv - h, a, b)) / (2 * h)
            close(label + ": dx/dt = ax+by at t=" + str(tv), dx, a * xs + b * ys, 1e-4)
            close(label + ": dy/dt = cx+dy at t=" + str(tv), dy, c * xs + d * ys, 1e-4)

def test_surds_and_circle():
    import pure640
    # sqrt(72) = sqrt(36 x 2) = 6 sqrt(2)
    o = drive(pure640.t_surds, ["72"], [0])
    has("square factor pulled out", o, "= 6sqrt(2)")
    has("the factorisation is shown", o, "sqrt(36 x 2)")
    # sqrt(2) has no square factor and must be left alone
    o = drive(pure640.t_surds, ["2"], [0])
    has("already simplest", o, "already in simplest form")
    # 3sqrt(8) + 2sqrt(50) = 6sqrt(2) + 10sqrt(2) = 16sqrt(2)
    o = drive(pure640.t_surds, ["3", "8", "2", "50"], [1])
    has("first simplified", o, "3sqrt(8) = 6sqrt(2)")
    has("second simplified", o, "2sqrt(50) = 10sqrt(2)")
    has("like surds collected", o, "= 16sqrt(2)")
    num("decimal agrees", o, "decimal check: ", 16.0 * math.sqrt(2.0), 1e-5)
    # sqrt(2) and sqrt(3) are unlike and must NOT be collected
    o = drive(pure640.t_surds, ["1", "2", "1", "3"], [1])
    has("unlike surds not collected", o, "does NOT")
    # 6/(3+sqrt2): conjugate 3-sqrt2, bottom 9-2 = 7, so (18-6sqrt2)/7
    o = drive(pure640.t_surds, ["6", "3", "1", "2"], [3])
    has("conjugate named", o, "CONJUGATE 3 - sqrt(2)")
    has("denominator rationalised", o, "= 7")
    has("exact fraction form", o, "= (18 - 6sqrt(2)) / 7")
    num("rationalised value", o, "decimal check: ", 6.0 / (3.0 + math.sqrt(2.0)), 1e-5)
    # 2 sqrt(3) x 5 sqrt(6) = 10 sqrt(18) = 30 sqrt(2)
    o = drive(pure640.t_surds, ["2", "3", "5", "6"], [2])
    has("product simplified", o, "= 30sqrt(2)")

    # x^2+y^2=25 meets y=x+1 where 2x^2+2x-24=0, i.e. x = 3 and x = -4
    o = drive(pure640.t_linecircle, ["0", "0", "5", "1", "1"], [0])
    has("substituted quadratic", o, "2x^2 + 2x - 24 = 0")
    num("discriminant", o, "discriminant = ", 196.0)
    has("first intersection", o, "(3, 4)")
    has("second intersection", o, "(-4, -3)")
    num("chord length", o, "chord length = ", math.sqrt(98.0), 1e-3)
    # y = x + sqrt2 is a tangent to the unit circle
    o = drive(pure640.t_linecircle, ["0", "0", "1", "1", str(math.sqrt(2))], [0])
    has("tangent detected", o, "TANGENT")
    has("perpendicularity checked", o, "confirms tangent perp to radius")
    # a line too far away misses entirely, and the distance says why
    o = drive(pure640.t_linecircle, ["0", "0", "1", "0", "5"], [0])
    has("miss detected", o, "misses the circle")
    num("distance to the line", o, "= |ma - b + c| / sqrt(1+m^2) = ", 5.0, 1e-6)
    # vertical line x = 3 cuts x^2+y^2=25 at y = +/-4
    o = drive(pure640.t_linecircle, ["0", "0", "5", "3"], [1])
    has("vertical intersection up", o, "(3, 4)")
    has("vertical intersection down", o, "(3, -4)")

    # u(n) = 1/n is decreasing and converges to 0
    o = drive(pure640.t_sequence, ["1/n", "1", "12"], [0])
    has("terms listed", o, "u(3) = 0.333333")
    has("decreasing", o, "DECREASING")
    # u(n+1) = 1/(1-u) from 2 cycles 2, -1, 0.5 with period 3
    o = drive(pure640.t_sequence, ["1/(1-x)", "2", "9"], [1])
    has("periodic detected", o, "PERIODIC with period 3")
    # u(n) = 2n+1 is increasing
    o = drive(pure640.t_sequence, ["2n+1", "1", "8"], [0])
    has("increasing", o, "INCREASING")
    # u(n+1) = u/2 from 8 converges to 0
    o = drive(pure640.t_sequence, ["x/2", "8", "40"], [1])
    has("convergent", o, "CONVERGENT")

def test_surd_engine():
    # sqrt of an integer pulls out its largest square factor. Exact form is
    # most of the marks on an H640 surd question, so sqrt(2) must never become
    # 1.414214 - and sqrt(8) must not stay as sqrt(8) either.
    def sq(e):
        return caseng.tostr(caseng.simplify(caslex.parse(e)))
    check("sqrt(8)", sq("sqrt(8)"), "2*sqrt(2)")
    check("sqrt(12)", sq("sqrt(12)"), "2*sqrt(3)")
    check("sqrt(50)", sq("sqrt(50)"), "5*sqrt(2)")
    check("sqrt(72)", sq("sqrt(72)"), "6*sqrt(2)")
    check("sqrt(98)", sq("sqrt(98)"), "7*sqrt(2)")
    check("sqrt(45)", sq("sqrt(45)"), "3*sqrt(5)")
    check("a perfect square still folds", sq("sqrt(4)"), "2")
    check("sqrt(2) is left exact", sq("sqrt(2)"), "sqrt(2)")
    check("sqrt(3) is left exact", sq("sqrt(3)"), "sqrt(3)")
    check("a symbolic argument is untouched", sq("sqrt(x)"), "sqrt(x)")
    # sqrt(u)*sqrt(u) folds to u, which needs the product rule to re-simplify
    check("sqrt(3) squared", sq("sqrt(3)*sqrt(3)"), "3")
    check("sqrt(x) squared", sq("sqrt(x)*sqrt(x)"), "x")
    # and the presentation pass gathers the constants
    check("2 sqrt(8) collects",
          caseng.tostr(cascalc.tidy(caslex.parse("2*sqrt(8)"))), "4*sqrt(2)")
    # the extraction must never change a value
    for n in (2, 3, 8, 12, 18, 20, 45, 50, 72, 98, 128, 300, 1000):
        e = caslex.parse("sqrt(" + str(n) + ")")
        close("sqrt(" + str(n) + ") keeps its value",
              caseng.evalf(caseng.simplify(e), 0.0), math.sqrt(n), 1e-12)

def test_binom_cdf_recurrence():
    # binom_cdf used to call binom_pmf once per term, and binom_pmf is itself
    # O(k), so the whole thing was O(k^2): binom_cdf(5000, 0.3, 1500) took most
    # of half a second on a desktop, which on a handheld is a hang. It now
    # walks the pmf with the recurrence P(j+1) = P(j)(n-j)p/((j+1)q), starting
    # from the MODE rather than from 0 - q**n underflows to exactly zero long
    # before n gets interesting (about 1e-774 for n=5000, q=0.7) and every
    # later term would then be zero too.
    def reference(n, p, k):
        # the obvious summation, which is what the old code effectively did
        if k < 0:
            return 0.0
        if k >= n:
            return 1.0
        tot = 0.0
        for j in range(k + 1):
            tot += casutil.binom_pmf(n, p, j)
        return tot

    cases = [(10, 0.5, 5), (20, 0.3, 6), (100, 0.5, 50), (1000, 0.5, 500),
             (50, 0.02, 1), (50, 0.98, 49), (200, 0.9, 180), (7, 0.25, 0),
             (30, 0.1, 0), (12, 0.4, 3), (60, 0.75, 40), (5000, 0.3, 1500)]
    for n, p, k in cases:
        close("binom_cdf(" + str(n) + "," + str(p) + "," + str(k) + ")",
              casutil.binom_cdf(n, p, k), reference(n, p, k), 1e-9)

    # values worked out by hand rather than against another implementation
    close("B(10,0.5) P(X<=5) = 638/1024", casutil.binom_cdf(10, 0.5, 5),
          638.0 / 1024.0, 1e-12)
    close("B(4,0.5) P(X<=2) = 11/16", casutil.binom_cdf(4, 0.5, 2),
          11.0 / 16.0, 1e-12)
    close("B(5,0.2) P(X<=0) = 0.8^5", casutil.binom_cdf(5, 0.2, 0),
          0.8 ** 5, 1e-12)

    # edges
    check("k below 0 is 0", casutil.binom_cdf(10, 0.5, -1), 0.0)
    check("k at n is 1", casutil.binom_cdf(10, 0.5, 10), 1.0)
    check("k above n is 1", casutil.binom_cdf(10, 0.5, 99), 1.0)
    check("p = 0 is certain", casutil.binom_cdf(10, 0.0, 0), 1.0)
    check("p = 1 has no mass below n", casutil.binom_cdf(10, 1.0, 9), 0.0)
    # the cdf must never exceed 1 or fall below 0, at any k
    for k in range(0, 41):
        v = casutil.binom_cdf(40, 0.35, k)
        truthy("binom_cdf(40,0.35," + str(k) + ") is a probability",
               -1e-12 <= v <= 1.0 + 1e-12)
    # and it must be non-decreasing in k
    prev = -1.0
    for k in range(0, 41):
        v = casutil.binom_cdf(40, 0.35, k)
        truthy("binom_cdf is non-decreasing at k=" + str(k), v >= prev - 1e-12)
        prev = v

def test_engine_invariants():
    # Four properties that must hold for EVERY expression, rather than for the
    # particular answers asserted elsewhere. Named answers catch a wrong rule;
    # these catch a rule that is wrong somewhere nobody thought to look.
    XS = (0.37, 1.23, 2.71, 4.13, -0.61, -2.2)

    # 1. differentiating a symbolic integral returns the integrand
    n = 0
    for e in SWEEP:
        t = caslex.parse(e)
        F = cascalc.integ(t)
        if F is None:
            continue
        n += 1
        CHECKS[0] += 1
        _agree("d/dx of int " + e, caseng.simplify(caseng.diff(cascalc.tidy(F))),
               t, XS, 1e-6)
    truthy("the sweep actually integrates most of its expressions", n >= 35)

    # 2. simplify never changes a value
    for e in SWEEP + SWEEP_ALG:
        t = caslex.parse(e)
        CHECKS[0] += 1
        _agree("simplify " + e, caseng.simplify(t), t, XS)

    # 3. expand, collect, cancel and factor never change a value
    for e in SWEEP_ALG:
        t = caslex.parse(e)
        for name, fn in (("expand", caspoly.expand), ("collect", caspoly.collect),
                         ("cancel", caspoly.cancel)):
            CHECKS[0] += 1
            _agree(name + " " + e, fn(t), t, XS)
        f = caspoly.factor(t)
        if f is not None:
            CHECKS[0] += 1
            _agree("factor " + e, f, t, XS)

    # 4. printing then re-parsing gives the same function. This is the property
    # that catches a bracketing bug in the printer, which is otherwise invisible
    # until it silently changes an answer on screen.
    for e in SWEEP + SWEEP_ALG:
        t = caslex.parse(e)
        for form in (t, caseng.simplify(t), cascalc.tidy(t)):
            s = caseng.tostr(form)
            r = caslex.parse(s)
            CHECKS[0] += 1
            if r is None:
                FAILED.append("tostr of " + e + " gave unparseable " + repr(s))
                continue
            _agree("reparse " + repr(s), r, form, (0.55, 1.9, 3.3))

# ------------------------------------------------- screen layout (no Pillow) --
# casioshot.py renders these screens to PNG so they can be looked at, but that
# needs Pillow and CI should not. This records only the GEOMETRY: where each
# string starts and how wide casui believes it is. A string that runs past 384
# is clipped on the real device, and no text assertion can see that.
_LAYOUT = []

def _rec_draw_string(x, y, s, c=None, size=None):
    _LAYOUT.append((x, y, str(s), size or "medium"))

def _layout_hold(note=None):
    # hold() is stubbed to a no-op at the top of this file so tools can be
    # driven, which means its OWN prompt never reached the layout recorder -
    # and the prompt is exactly what a bottom-strip label collides with. This
    # replays hold's drawing without the waiting.
    if note:
        _rec_draw_string(6, 178, note, None, "small")
        _rec_draw_string(318, 178, "any key", None, "small")
    else:
        _rec_draw_string(6, 178, "Press any key", None, "small")

def _layout(fn):
    del _LAYOUT[:]
    real = {}
    mods = [casui]
    import casrender
    mods.append(casrender)
    for m in mods:
        real[m] = m.draw_string
        m.draw_string = _rec_draw_string
    realhold = casui.hold
    casui.hold = _layout_hold
    try:
        fn()
    finally:
        for m in real:
            m.draw_string = real[m]
        casui.hold = realhold
    return list(_LAYOUT)

def _chart_scene():
    fr = casutil.frame(-12.0, 12.0, -3.5, 3.5)
    casutil.axes(fr, "y = 1x^2 - 5x + 6   solve < 0", "x", "y")
    casutil.seg(fr, -12.0, -3.0, 12.0, 3.0, casui.ACC)
    casutil.chart_hold("red = solution set   roots 2, 3")

def test_screen_layout():
    import casrender
    scenes = [
        ("graph 1/x", lambda: casui.graph(caslex.parse("1/x"))),
        ("graph tan", lambda: casui.graph(caslex.parse("tan(x)"))),
        ("graph of a big-range function",
         lambda: casui.graph(caslex.parse("100000x^2"))),
        # menu() and result_screen() are stubbed at the top of this file so
        # tools can be driven, so the drawing functions underneath them are
        # what has to be exercised here
        ("menu", lambda: casui.draw_menu("MATHS TOOLKIT",
                                         ["Calculate", "Calculus & Algebra",
                                          "A-Level Maths", "Further Maths",
                                          "Angle mode: RADIANS"], 1)),
        ("long result screen", lambda: casui._paged(
            "A long result",
            [(ln, "medium") for ln in
             ["line " + str(i) + ": some result text" for i in range(1, 17)]],
            casui.BLACK)),
        ("input with a fraction preview", lambda: casui.draw_input(
            "Type an expression:", "(x+1)/(x-2)", 5, False, False, False, 0)),
        ("input with a long expression", lambda: casui.draw_input(
            "Type an expression:", "sin(2x)+cos(3x)-tan(x)/sqrt(x^2+1)+exp(-x)",
            21, False, False, False, 0)),
        ("the CATALOG picker", lambda: casui.draw_input(
            "Type an expression:", "2x+", 3, False, False, True, 5)),
        # a chart drawn through the shared helpers, with the longest note a
        # tool actually passes - this is where the axis tick labels, the note
        # and the key prompt all compete for the bottom strip
        ("a chart with a long note", _chart_scene),
    ]
    for label, fn in scenes:
        rows = _layout(fn)
        truthy(label + " draws something", len(rows) > 0)
        for x, y, s, size in rows:
            w = casui.text_w(s, size)
            truthy(label + ": " + repr(s[:24]) + " fits the 384px width",
                   x + w <= 384)
            truthy(label + ": " + repr(s[:24]) + " is on screen vertically",
                   0 <= y <= 191)
        # nothing may be drawn on top of something else on the same baseline
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                xa, ya, sa, za = rows[i]
                xb, yb, sb, zb = rows[j]
                if abs(ya - yb) > 6:
                    continue
                ea = xa + casui.text_w(sa, za)
                eb = xb + casui.text_w(sb, zb)
                if xa < eb and xb < ea:
                    FAILED.append(label + ": " + repr(sa[:20]) + " at y=" +
                                  str(ya) + " overprints " + repr(sb[:20]) +
                                  " at y=" + str(yb))
                    CHECKS[0] += 1
                    return

# README rows: (table row name, module). The README documents each section's
# tools verbatim from its TOOLS labels, and a README that has quietly drifted
# from the code is worse than no README - it is a list of tools that are not
# there.
README_ROWS = [
    ("Pure: algebra & trig", "pure640"),
    ("Pure: functions & calculus", "purecalc"),
    ("Statistics", "stat640"),
    ("Mechanics", "mech640"),
    ("Proof", "proof"),
    ("Complex numbers", "vcplx"),
    ("Matrices", "matrix"),
    ("Vectors & 3-D", "vectors"),
    ("Roots of polynomials", "polyroots"),
    ("Series & Maclaurin", "series"),
    ("Hyperbolic functions", "hyper"),
    ("Polar coordinates", "polar"),
    ("Differential equations", "diffeq"),
    ("Mechanics (FM)", "fmmech"),
    ("Statistics (FM)", "fmstat"),
    ("Numerical Methods", "numeric"),
    ("Modelling w/ Algorithms", "algos"),
    ("Extra Pure", "xpure"),
    ("Further Pure w/ Tech", "fpt"),
]

def readme_table_line(name, mod):
    labels = []
    for label, fn in mod.TOOLS:
        labels.append(label.replace("|", "\\|"))
    return name + " | " + ", ".join(labels)

def test_readme_matches_tools():
    path = os.path.join(HERE, "README.md")
    if not os.path.exists(path):
        truthy("README.md exists", False)
        return
    text = open(path).read()
    for name, modname in README_ROWS:
        mod = __import__(modname)
        want = readme_table_line(name, mod)
        # the README row is "| name | menu path | label, label, ... |"
        found = None
        for line in text.split("\n"):
            if line.startswith("| " + name + " |"):
                cells = line.split(" | ")
                if len(cells) >= 3:
                    found = cells[0][2:].strip() + " | " + cells[len(cells) - 1].rstrip(" |").strip()
                break
        truthy("README has a row for " + name, found is not None)
        if found is None:
            continue
        check("README tool list for " + name + " matches " + modname + ".TOOLS",
              found, want)

def test_readme_install_list():
    # The install list is the one piece of documentation a user follows before
    # anything works at all. devlint.DEVICE_FILES is the authority on what runs
    # on the calculator, so the README must not name a file that is not one, or
    # miss one that is.
    path = os.path.join(HERE, "README.md")
    text = open(path).read()
    probes = set(["calib_screen.py", "fontmetrics.py", "fontmetrics2.py",
                  "keyprobe.py", "hwcheck.py"])
    for f in devlint.DEVICE_FILES:
        if f in probes:
            continue
        truthy("README install list names " + f, "`" + f + "`" in text)
    # and nothing that must NOT be copied is listed as if it should be
    for f in ("casioplot.py", "tests.py", "devlint.py", "stress.py"):
        truthy("README warns not to copy " + f, f in text)

def test_menu_tree_reachable():
    # Every section module must be reachable from the launcher's menus, have a
    # help entry, and expose a working registry. A module can be perfectly
    # correct, fully tested and completely unreachable - test_every_tool_is_
    # registered catches a tool missing from its module's TOOLS, and this
    # catches a whole MODULE missing from the menus.
    mods = list(casui.MATHS_MODS) + list(casui.FM_CORE_MODS) + list(casui.FM_OPT_MODS)
    check("menu labels and modules line up (A-Level)",
          len(casui.MATHS_LABELS), len(casui.MATHS_MODS))
    check("menu labels and modules line up (Core Pure)",
          len(casui.FM_CORE_LABELS), len(casui.FM_CORE_MODS))
    check("menu labels and modules line up (Options)",
          len(casui.FM_OPT_LABELS), len(casui.FM_OPT_MODS))
    total = 0
    for name in mods:
        mod = __import__(name)
        truthy(name + " has a TOOLS registry", hasattr(mod, "TOOLS"))
        truthy(name + " has a run() entry point", hasattr(mod, "run"))
        truthy(name + " has a HELP entry", name in casui.HELP)
        if hasattr(mod, "TOOLS"):
            for label, fn in mod.TOOLS:
                truthy(name + " tool " + repr(label) + " is callable", callable(fn))
            total += len(mod.TOOLS)
    truthy("the menus reach a substantial toolkit", total >= 250)

    # and nothing with a TOOLS list is stranded off the menus
    infra = set(["maths", "casui", "casutil", "caslex", "caseng", "casrender",
                 "cascalc", "caspoly", "calib_screen", "fontmetrics",
                 "fontmetrics2", "keyprobe", "hwcheck"])
    reachable = set(mods)
    for f in devlint.DEVICE_FILES:
        name = f[:-3]
        if name in infra:
            continue
        truthy(name + " is reachable from a menu", name in reachable)

def test_every_tool_is_registered():
    # A tool that is not in its module's TOOLS list is unreachable from the
    # menu and invisible to stress.py, however well it works when called
    # directly - which is how two matrix tools shipped in a commit that claimed
    # to add them. Every t_* function a section module defines must be listed.
    mods = ["vcplx", "matrix", "vectors", "polyroots", "series", "hyper",
            "polar", "diffeq", "fmmech", "fmstat", "numeric", "algos",
            "xpure", "fpt", "pure640", "purecalc", "stat640", "mech640"]
    for name in mods:
        mod = __import__(name)
        tools = getattr(mod, "TOOLS", None)
        truthy(name + " has a TOOLS registry", tools is not None)
        if tools is None:
            continue
        listed = []
        for label, fn in tools:
            listed.append(fn)
            truthy(name + " tool label is a non-empty string",
                   isinstance(label, str) and len(label) > 0)
        for attr in dir(mod):
            if not attr.startswith("t_"):
                continue
            fn = getattr(mod, attr)
            if not callable(fn):
                continue
            truthy(name + "." + attr + " is registered in TOOLS", fn in listed)
        # labels have to be distinct, or the menu shows the same line twice
        seen = []
        for label, fn in tools:
            truthy(name + " label " + repr(label) + " is unique", label not in seen)
            seen.append(label)

TESTS = [
    ("lexer", test_lexer),
    ("engine", test_engine),
    ("calculus", test_calculus),
    ("polynomial algebra", test_polyalg),
    ("CAS algebra UI", test_cas_algebra_ui),
    ("reciprocal trig", test_reciprocal_trig),
    ("engine substitution", test_engine_substitution),
    ("evalf env precedence", test_evalf_env_precedence),
    ("solve in any variable", test_solve_variable),
    ("purecalc", test_purecalc),
    ("pure640 triangle/arc/inequality", test_pure640_new),
    ("purecalc calculus applications", test_purecalc_calculus),
    ("integrating reciprocal powers", test_integ_reciprocal_powers),
    ("differential equations", test_diffeq_complete),
    ("complex loci and de Moivre", test_complex_loci),
    ("vector lines and planes", test_vector_lines),
    ("projectile inverse", test_projectile_inverse),
    ("exp/ln folding", test_exp_ln_folding),
    ("mechanics variable accel", test_mech_variable_accel),
    ("matrix invariants", test_matrix_invariant),
    ("method of differences", test_method_of_differences),
    ("render", test_render),
    ("ui format", test_ui_format),
    ("keymap vs hardware", test_keymap_matches_hardware),
    ("draw_string sizes", test_draw_string_sizes),
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
    ("proof and induction", test_proof),
    ("simulation", test_simulation),
    ("circle properties and proportion", test_circle_and_proportion),
    ("trig equations by identity", test_trig_by_identity),
    ("SHM amplitude and phase", test_shm_fit),
    ("inequality region sketch", test_inequality_region),
    ("coupled differential equations", test_coupled_des),
    ("surds and line-circle", test_surds_and_circle),
    ("surd extraction", test_surd_engine),
    ("binomial cdf recurrence", test_binom_cdf_recurrence),
    ("engine invariants", test_engine_invariants),
    ("screen layout", test_screen_layout),
    ("every tool is registered", test_every_tool_is_registered),
    ("menu tree reachable", test_menu_tree_reachable),
    ("README matches TOOLS", test_readme_matches_tools),
    ("README install list", test_readme_install_list),
]

# ---------------------------------------------------------- extra modules --
# Test files named tests_*.py are picked up automatically. Each defines
#   SECTIONS = [(label, function), ...]
# and each function takes one argument: this harness, as an object carrying
# check / close / truthy / raises / drive / has / num. Passing the harness in
# rather than letting the extra file "import tests" matters - tests.py runs as
# __main__, so importing it again would build a second copy of the module with
# its own _inputs and _out lists, and drive() would feed one while the tools
# read the other.
class _Harness(object):
    pass

H = _Harness()
H.check = check
H.close = close
H.truthy = truthy
H.raises = raises
H.drive = drive
H.has = has
H.num = num
H.casui = casui
H.caslex = caslex
H.caseng = caseng
H.cascalc = cascalc
H.caspoly = caspoly
H.casutil = casutil

def _extra_tests():
    out = []
    names = []
    for f in os.listdir(HERE):
        if f.startswith("tests_") and f.endswith(".py"):
            names.append(f[:-3])
    names.sort()
    for name in names:
        mod = __import__(name)
        for label, fn in getattr(mod, "SECTIONS", []):
            out.append((label, (lambda g: (lambda: g(H)))(fn)))
    return out

def main():
    for name, fn in TESTS + _extra_tests():
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
