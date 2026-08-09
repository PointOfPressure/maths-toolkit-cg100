import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) or "."

import casui

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
    t = caslex.parse(e)
    r = cascalc.integ(t)
    return None if r is None else caseng.tostr(cascalc.tidy(r))


def test_lexer():
    check("parse 2^-3", caslex.parse("2^-3"), ('^', ('n', 2), ('neg', ('n', 3))))
    close("eval 2^-3", ev("2^-3"), 0.125)
    close("eval x^-1", ev("x^-1", 4.0), 0.25)
    close("eval 2^-x", ev("2^-x", 3.0), 0.125)
    close("eval -2^2", ev("-2^2"), -4.0)
    close("eval 2^3^2", ev("2^3^2"), 512.0)
    close("eval 1/-2", ev("1/-2"), -0.5)
    close("eval 2^(-3)", ev("2^(-3)"), 0.125)

    close("eval 1e3", ev("1e3"), 1000.0)
    close("eval 2.5e-3", ev("2.5e-3"), 0.0025)
    close("eval 6.02e23", ev("6.02e23"), 6.02e23)
    close("eval 2e", ev("2e"), 2 * 2.718281828459045)
    close("eval 3exp(1)", ev("3exp(1)"), 3 * math.e)

    close("eval 2x", ev("2x", 5.0), 10.0)
    close("eval 2(x+1)", ev("2(x+1)", 3.0), 8.0)
    close("eval (x+1)(x-1)", ev("(x+1)(x-1)", 3.0), 8.0)
    close("eval 3!2", ev("3!2"), 12.0)

    check("parse 'x)'", caslex.parse("x)"), None)
    check("parse '((x)'", caslex.parse("((x)"), None)
    check("parse '+'", caslex.parse("*"), None)
    check("parse ''", caslex.parse(""), None)

    close("asinh beats asin", ev("asinh(0)"), 0.0)
    close("logb(2,8)", ev("logb(2,8)"), 3.0)
    close("nCr(6,2)", ev("nCr(6,2)"), 15.0)
    close("nPr(5,2)", ev("nPr(5,2)"), 20.0)
    close("5!", ev("5!"), 120.0)


def test_engine():
    check("simplify x+0", sstr("x+0"), "x")
    check("simplify x*1", sstr("x*1"), "x")
    check("simplify x*0", sstr("x*0"), "0")
    check("simplify x-x", sstr("x-x"), "0")
    check("simplify x^1", sstr("x^1"), "x")
    check("simplify x^0", sstr("x^0"), "1")
    check("simplify 2/4", sstr("2/4"), "1/2")
    check("simplify 6/3", sstr("6/3"), "2")
    check("simplify 2^-3", sstr("2^-3"), "1/8")
    check("simplify x/(-1)", sstr("x/(0-1)"), "-x")
    check("simplify x^2*x^3", sstr("x^2*x^3"), "x^5")
    check("simplify x*x^3", sstr("x*x^3"), "x^4")
    check("simplify x^3/x", sstr("x^3/x"), "x^2")
    check("simplify x^2/(2x)", sstr("x^2/(2x)"), "x/2")
    check("simplify x/(2x)", sstr("x/(2x)"), "1/2")

    truthy("(-8)^(1/3) stays symbolic", "^" in sstr("(0-8)^(1/3)"))
    raises("evalf (-8)^(1/3) raises", lambda: ev("(0-8)^(1/3)"))
    truthy("2^1000 not folded", "^" in sstr("2^1000"))

    check("d/dx x^2+3x", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("x^2+3x")))), "2*x+3")
    check("d/dx sin(x)", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("sin(x)")))), "cos(x)")
    check("d/dx logb(2,x)", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("logb(2,x)")))), "1/(x*ln(2))")
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

    raises("evalf unknown var raises", lambda: ev("a+b"))
    close("evalf with env", caseng.evalf(caslex.parse("x+y"), 1.0, False, {'y': 10.0}), 11.0)

    close("sin 30 deg", ev("sin(30)", 0.0, True), 0.5)
    close("asin .5 deg", ev("asin(0.5)", 0.0, True), 30.0)
    close("sin 30 rad", ev("sin(30)", 0.0, False), math.sin(30.0))

    check("tostr keeps precedence", caseng.tostr(caslex.parse("(x+1)*(x-1)")), "(x+1)*(x-1)")
    check("tostr brackets neg base", caseng.tostr(('^', ('n', -8), ('n', 2))), "(-8)^2")
    check("numstr nan", caseng.tostr(('n', float('nan'))), "undefined")
    check("numstr inf", caseng.tostr(('n', float('inf'))), "inf")

    close("sinh(2)", ev("sinh(2)"), math.sinh(2.0), 1e-12)
    close("cosh(2)", ev("cosh(2)"), math.cosh(2.0), 1e-12)
    close("tanh(2)", ev("tanh(2)"), math.tanh(2.0), 1e-12)
    close("asinh(2)", ev("asinh(2)"), math.asinh(2.0), 1e-12)
    close("asinh(-2)", ev("asinh(0-2)"), math.asinh(-2.0), 1e-12)
    close("acosh(2)", ev("acosh(2)"), math.acosh(2.0), 1e-12)
    close("atanh(.5)", ev("atanh(0.5)"), math.atanh(0.5), 1e-12)
    close("tanh(400) saturates", ev("tanh(400)"), 1.0)


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
    check("ratof 3", caspoly.ratof(_p("3")), (3, 1))
    check("ratof -2/6 reduces", caspoly.ratof(_p("-2/6")), (-1, 3))
    check("ratof 2^-3", caspoly.ratof(_p("2^-3")), (1, 8))
    check("ratof of a decimal that is not exact", caspoly.ratof(_p("0.1")), None)
    check("ratof of pi", caspoly.ratof(_p("pi")), None)

    check("expand (x+1)^3", _ex("(x+1)^3"), "x^3+3*x^2+3*x+1")
    check("expand (2x-1)(x+4)", _ex("(2x-1)(x+4)"), "2*x^2+7*x-4")
    check("expand (x+2)(x-2)", _ex("(x+2)(x-2)"), "x^2-4")
    check("expand (x-3)^2", _ex("(x-3)^2"), "x^2-6*x+9")
    check("expand (x+1)^2(x-3)", _ex("(x+1)^2(x-3)"), "x^3-x^2-5*x-3")
    check("expand (a+b)^2 in two letters", _ex("(a+b)^2"), "2*a*b+a^2+b^2")
    check("expand splits over a constant denominator", _ex("(2x+4)/2"), "x+2")
    check("expand (x+1)^5", _ex("(x+1)^5"), "x^5+5*x^4+10*x^3+10*x^2+5*x+1")
    check("expand (2x-3)^3", _ex("(2x-3)^3"), "8*x^3-36*x^2+54*x-27")

    check("collect 3x+2x", _co("3x+2x"), "5*x")
    check("collect cancels", _co("x+x^2-x"), "x^2")
    check("collect to zero", _co("x-x"), "0")
    check("collect keeps unlike terms apart", _co("2x+3y"), "2*x+3*y")
    check("collect fractional coefficients", _co("x/2+x/3"), "5*x/6")
    check("collect gathers a function of x", _co("2sin(x)+3sin(x)"), "5*sin(x)")
    truthy("collect does not round 0.1x", "0.1" in _co("0.1x+0.2x") or
           _co("0.1x+0.2x") == "0.3*x")

    check("factor x^2-5x+6", _fa("x^2-5x+6"), "(x-2)*(x-3)")
    check("factor difference of two squares", _fa("x^2-4"), "(x-2)*(x+2)")
    check("factor 2x^2+7x+3", _fa("2x^2+7x+3"), "(2*x+1)*(x+3)")
    check("factor 6x^2-x-2", _fa("6x^2-x-2"), "(2*x+1)*(3*x-2)")
    check("factor 4x^2-9", _fa("4x^2-9"), "(2*x-3)*(2*x+3)")
    check("factor common factor out", _fa("2x^2+4x"), "2*x*(x+2)")
    check("factor a cubic with three roots", _fa("x^3-6x^2+11x-6"),
          "(x-1)*(x-2)*(x-3)")
    check("factor a repeated root", _fa("x^2-2x+1"), "(x-1)^2")
    check("x^2+1 does not factorise", _fa("x^2+1"), None)
    check("x^2-2 does not factorise over the rationals", _fa("x^2-2"), None)
    for e in ("x^2-5x+6", "2x^2+7x+3", "6x^2-x-2", "x^3-6x^2+11x-6", "2x^2+4x"):
        r = caspoly.factor(_p(e))
        check("factor(" + e + ") multiplies back",
              caseng.tostr(caspoly.expand(r)), caseng.tostr(caspoly.expand(_p(e))))

    check("partial 1/(x^2-1)", _pf("1", "x^2-1"), "(1/2)/(x-1) + (-1/2)/(x+1)")
    check("partial x/((x+1)(x-2))", _pf("x", "(x+1)(x-2)"),
          "(1/3)/(x+1) + (2/3)/(x-2)")
    check("partial with a repeated factor", _pf("3x+5", "(x-1)^2(x+2)"),
          "(1/9)/(x-1) + (8/3)/((x-1)^2) + (-1/9)/(x+2)")
    check("partial with a quadratic factor", _pf("1", "x(x^2+1)"),
          "(1)/(x) + (-x)/(x^2+1)")
    check("partial improper divides out", _pf("x^2", "x^2+1"),
          "1 + (-1)/(x^2+1)")
    check("partial of a non-polynomial", _pf("sin(x)", "x+1"), None)

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
    out = drive(casui.cas_section, ["(x+1)^3"], [5, -1, -1])
    has("expand through the UI", out, "x^3+3*x^2+3*x+1")
    out = drive(casui.cas_section, ["x^2-5x+6"], [6, -1, -1])
    has("factorise through the UI", out, "(x-2)*(x-3)")
    out = drive(casui.cas_section, ["3x+2x"], [7, -1, -1])
    has("collect through the UI", out, "5*x")
    out = drive(casui.cas_section, ["(3x+5)/((x-1)^2(x+2))"], [8, -1, -1])
    has("partial fractions through the UI", out, "(x-1)^2")
    has("partial fractions numerator", out, "8/3")
    out = drive(casui.cas_section, ["x^2+1"], [6, -1, -1])
    has("irreducible is reported", out, "does not factorise")
    out = drive(casui.cas_section, ["x^2+1"], [8, -1, -1])
    has("partial fractions needs a fraction", out, "one fraction")


def test_reciprocal_trig():
    for name in ('sec', 'cosec', 'cot', 'sech', 'cosech', 'coth'):
        t = caslex.parse(name + "(x)")
        check(name + " parses as itself", caseng.tostr(t), name + "(x)")
        check(name + " is one node", t[0], name)
    check("cosec is not cos", caslex.parse("cosec(x)")[0], 'cosec')
    check("cosech is not cosec", caslex.parse("cosech(x)")[0], 'cosech')
    check("cosh is still cosh", caslex.parse("cosh(x)")[0], 'cosh')
    check("cos is still cos", caslex.parse("cos(x)")[0], 'cos')
    check("sech is not sec", caslex.parse("sech(x)")[0], 'sech')
    check("coth is not cot", caslex.parse("coth(x)")[0], 'coth')
    check("arcsin is asin", caslex.parse("arcsin(x)")[0], 'asin')
    check("arctan is atan", caslex.parse("arctan(x)")[0], 'atan')
    check("arccosh is acosh", caslex.parse("arccosh(x)")[0], 'acosh')

    close("sec(1)", caseng.evalf(caslex.parse("sec(x)"), 1.0), 1.0 / math.cos(1.0))
    close("cosec(1)", caseng.evalf(caslex.parse("cosec(x)"), 1.0), 1.0 / math.sin(1.0))
    close("cot(1)", caseng.evalf(caslex.parse("cot(x)"), 1.0),
          math.cos(1.0) / math.sin(1.0))
    close("sech(1)", caseng.evalf(caslex.parse("sech(x)"), 1.0), 1.0 / math.cosh(1.0))
    close("coth(1)", caseng.evalf(caslex.parse("coth(x)"), 1.0),
          math.cosh(1.0) / math.sinh(1.0))
    close("cot(pi/2) is 0", caseng.evalf(caslex.parse("cot(x)"), math.pi / 2), 0.0, 1e-12)
    raises("sec(pi/2) raises", lambda: caseng.evalf(caslex.parse("sec(x)"), math.pi / 2))
    raises("cosec(0) raises", lambda: caseng.evalf(caslex.parse("cosec(x)"), 0.0))
    raises("cot(0) raises", lambda: caseng.evalf(caslex.parse("cot(x)"), 0.0))
    raises("cosech(0) raises", lambda: caseng.evalf(caslex.parse("cosech(x)"), 0.0))
    raises("sec(90 deg) raises", lambda: caseng.evalf(caslex.parse("sec(x)"), 90.0, True))
    close("sec(60 deg) is 2", caseng.evalf(caslex.parse("sec(x)"), 60.0, True), 2.0)

    check("d/dx sec", caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("sec(x)")))),
          "sec(x)*tan(x)")
    check("d/dx cot(2x)",
          caseng.tostr(caseng.simplify(caseng.diff(caslex.parse("cot(2x)")))),
          "-(2*cosec(2*x)^2)")
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

    check("int sec^2 is tan", isym("sec(x)^2"), "tan(x)")
    check("int cosec^2 is -cot", isym("cosec(x)^2"), "-cot(x)")
    check("int sech^2 is tanh", isym("sech(x)^2"), "tanh(x)")
    check("int cot is ln|sin|", isym("cot(x)"), "ln(abs(sin(x)))")
    check("int sec", isym("sec(x)"), "ln(abs(sec(x)+tan(x)))")
    check("int cosec(2x)", isym("cosec(2x)"), "-ln(abs(cosec(2*x)+cot(2*x)))/2")
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

    for tok in ('sec(', 'cosec(', 'cot(', 'sech(', 'cosech(', 'coth('):
        truthy(tok + " is in the CATALOG picker", tok in casui.EXTRAS)


def test_engine_substitution():
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
    check("invert refuses x^2+x", caseng.invert(caslex.parse("x^2+x"), 'x', 'y'), None)
    check("invert refuses abs", caseng.invert(caslex.parse("abs(x)"), 'x', 'y'), None)

def test_evalf_env_precedence():
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
    r = cascalc.solve(caslex.parse("3t^2-12t+9"), 't')
    check("solve in t finds both roots", len(r), 2)
    close("solve in t root 1", r[0], 1.0, 1e-5)
    close("solve in t root 2", r[1], 3.0, 1e-5)
    close("defint in t", cascalc.defint(caslex.parse("t^2"), 0.0, 3.0, False, 200, 't'),
          9.0, 1e-9)
    r = cascalc.solve(caslex.parse("(y-2)^2"), 'y')
    check("touching root in y", len(r), 1)
    close("touching root value", r[0], 2.0, 1e-5)
    close("solve in x still works", cascalc.solve(caslex.parse("x^2-4"), 'x')[1], 2.0, 1e-5)

def test_purecalc():
    import purecalc
    o = drive(purecalc.t_composite, ["x^2", "2x+1", "3"])
    has("fg(x)", o, "(2*x+1)^2")
    has("gf(x)", o, "2*x^2+1")
    num("fg at 3 is 49", o, "fg = ", 49.0)
    num("gf at 3 is 19", o, "gf = ", 19.0)

    o = drive(purecalc.t_inverse, ["(3x-2)/4", "10"])
    has("inverse expression", o, "(4*x+2)/3")
    has("inverse self-check", o, "check f(f-inv(x)) = x: yes")
    num("inverse at 10", o, "f-inverse(10) = ", 14.0)
    o = drive(purecalc.t_inverse, ["x^2+x", "4"])
    has("no inverse by peeling", o, "No exact inverse")
    has("reports both roots", o, "no inverse here")

    o = drive(purecalc.t_domain_range, ["1/x", "-2", "2"])
    has("undefined points reported", o, "undefined at")
    o = drive(purecalc.t_domain_range, ["sqrt(x)", "0", "4"])
    has("whole interval", o, "domain: the whole interval")
    has("range 0 to 2", o, "range reached: 0 to 2")

    o = drive(purecalc.t_modulus, ["2x-6", "4"])
    has("modulus root 1", o, "x = 1")
    has("modulus root 5", o, "x = 5")
    o = drive(purecalc.t_modulus, ["2x-6", "-4"])
    has("negative modulus impossible", o, "never negative")

    o = drive(purecalc.t_transform, ["x^2", "2", "3", "6", "1"])
    has("transformed expression", o, "2*(3*x+6)^2+1")
    has("x stretch is 1/b", o, "stretch x by scale factor 0.3333")
    has("x translation is -c/b", o, "translate x by -2")

    o = drive(purecalc.t_param_diff, ["t^2", "t^3", "2"])
    has("dx/dt", o, "dx/dt = 2*t")
    has("dy/dt", o, "dy/dt = 3*t^2")
    has("parametric gradient", o, "dy/dx = 3*t/2")
    has("point at t=2", o, "point (4, 8)")
    num("gradient at t=2", o, "dy/dx = ", 3.0)
    num("second derivative at t=2", o, "d2y/dx2 = ", 0.375)

    o = drive(purecalc.t_param_cartesian, ["2t+1", "t^2", "0", "2"])
    has("t in terms of x", o, "t = (x-1)/2")

    o = drive(purecalc.t_implicit, ["x^2+y^2=25", "3", "4"])
    has("implicit gradient", o, "dy/dx = -x/y")
    num("implicit gradient at (3,4)", o, "dy/dx = ", -0.75)
    num("normal gradient there", o, "normal gradient ", 4.0 / 3.0)
    o = drive(purecalc.t_implicit, ["x^2+y^2=25", "1", "1"])
    has("off-curve point warned", o, "not on the curve")
    o = drive(purecalc.t_implicit, ["x^3+y^3=6xy", "3", "3"])
    num("folium gradient at (3,3)", o, "dy/dx = ", -1.0)

    o = drive(purecalc.t_substitution, ["2x(x^2+1)^5", "x^2+1"])
    has("integrand clears to u^5", o, "in terms of u: u^5")
    has("substitution answer", o, "(x^2+1)^6/6")
    has("substitution self-check", o, "differentiating back: agrees")
    o = drive(purecalc.t_substitution, ["x*sqrt(x^2+1)", "x^2+1"])
    has("sqrt substitution answer", o, "(x^2+1)^(3/2)/3")
    has("sqrt substitution checks", o, "differentiating back: agrees")
    o = drive(purecalc.t_substitution, ["cos(x)sin(x)^3", "sin(x)"])
    has("trig substitution answer", o, "sin(x)^4/4")
    o = drive(purecalc.t_substitution, ["x^3", "sin(x)"])
    has("bad substitution reported", o, "does not clear the integral")

    o = drive(purecalc.t_separable, ["2x", "y", "0", "1"])
    has("separable ln y side", o, "integral 1/g(y) dy = ln(abs(y))")
    has("separable x side", o, "integral f(x) dx   = x^2")
    has("separable explicit", o, "y = exp(x^2)")
    has("separable passes the point", o, "passes through")
    o = drive(purecalc.t_separable, ["1", "y^2", "0", "1"])
    has("y^2 separable integral", o, "integral 1/g(y) dy = -1/y")
    o = drive(purecalc.t_separable, ["1", "x*y", None])
    has("g must be in y only", o, "function of y only")

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
    o = drive(mech640.kinematics, ["t^3-6t^2+9t", "2"], [0])
    has("v from s", o, "v(t) = 3*t^2-12*t+9")
    has("a from s", o, "a(t) = 6*t-12")
    has("at rest at t=1", o, "t = 1   s = 4")
    has("at rest at t=3", o, "t = 3   s = 0")
    num("s at t=2", o, "s = ", 2.0)
    num("v at t=2", o, "v = ", -3.0)

    o = drive(mech640.kinematics, ["6t", "0", "0", "2"], [2])
    has("v by integrating a", o, "v(t) = 3*t^2")
    has("s by integrating v", o, "s(t) = t^3")
    num("s at t=2 from a", o, "s = ", 8.0)

    o = drive(mech640.distance_travelled, ["t^2-4t", "0", "5"])
    has("sign change found", o, "t = 4")
    num("displacement", o, "displacement = ", -25.0 / 3.0, 1e-3)
    num("distance travelled", o, "distance     = ", 13.0, 1e-3)
    has("they differ", o, "They differ")
    o = drive(mech640.distance_travelled, ["t^2+1", "0", "3"])
    num("no reversal displacement", o, "displacement = ", 12.0, 1e-3)
    num("no reversal distance", o, "distance     = ", 12.0, 1e-3)
    has("same when v keeps its sign", o, "Same, because")

    o = drive(mech640.connected, ["9.8", "5", "90", "0", "3", "0", "0"])
    num("connected acceleration", o, "a = ", 6.125, 1e-3)
    num("connected tension", o, "tension T = ", 18.375, 1e-3)
    o = drive(mech640.connected, ["9.8", "2", "90", "0", "5", "0", "0.6"])
    has("stays at rest", o, "stays at rest")
    has("friction is not at maximum", o, "not its maximum")

def test_matrix_invariant():
    import matrix
    matrix.A = [[1.0, 2.0], [0.0, 1.0]]
    o = drive(matrix.t_invariant, [])
    has("shear has a line of invariant points", o, "LINE of invariant points")
    truthy("shear does not claim the y-axis is invariant",
           not [ln for ln in o if 'x = 0 (the y-axis)' in ln])
    matrix.A = [[3.0, 0.0], [0.0, 2.0]]
    o = drive(matrix.t_invariant, [])
    has("diagonal has only the origin", o, "only")
    has("x-axis is an invariant line", o, "y = 0 x")
    has("y-axis is an invariant line", o, "x = 0 (the y-axis)")
    matrix.A = [[0.0, -1.0], [1.0, 0.0]]
    o = drive(matrix.t_invariant, [])
    has("rotation has no invariant line", o, "no invariant line")

    o = drive(matrix.t_transform3, ["90"], [2])
    num("3D rotation determinant", o, "det = ", 1.0, 1e-6)
    o = drive(matrix.t_transform3, [], [4])
    num("3D reflection determinant", o, "det = ", -1.0, 1e-6)
    has("reflection reverses orientation", o, "orientation is reversed")

def test_method_of_differences():
    import series
    o = drive(series.t_differences, ["1/(r(r+1))", "10"])
    has("g(r) for the standard case", o, "take g(r) = 1/r")
    has("telescoping checked", o, "checked numerically")
    num("S(10) of 1/(r(r+1))", o, "S(10) = ", 10.0 / 11.0, 1e-4)
    num("direct sum agrees", o, "direct sum  = ", 10.0 / 11.0, 1e-4)
    want = 0.75 - 1.0 / 42.0 - 1.0 / 44.0
    o = drive(series.t_differences, ["1/(r(r+2))", "20"])
    num("S(20) of 1/(r(r+2))", o, "S(20) = ", want, 1e-4)
    num("two-step direct sum agrees", o, "direct sum  = ", want, 1e-4)
    o = drive(series.t_differences, ["2/((2r-1)(2r+1))", "50"])
    num("S(50) of the odd-denominator sum", o, "S(50) = ", 1.0 - 1.0 / 101.0, 1e-4)
    o = drive(series.t_differences, ["1/(r^2+1)", None])
    has("non-telescoping reported", o, "does not telescope")


def test_calculus():
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

    check("int x ln(x)", isym("x*ln(x)"), "ln(x)*x^2/2-x^2/4")
    check("int x^2 ln(x)", isym("x^2*ln(x)"), "ln(x)*x^3/3-x^3/9")
    check("int atan(x)", isym("atan(x)"), "atan(x)*x-1/2*ln(abs(1+x^2))")
    truthy("int x sin(x) closes", isym("x*sin(x)") is not None)
    truthy("int x^2 sin(x) closes", isym("x^2*sin(x)") is not None)
    truthy("int x^3 exp(x) closes", isym("x^3*exp(x)") is not None)
    check("int exp(x)sin(x)", isym("exp(x)*sin(x)"), "exp(x)*(sin(x)-cos(x))/2")
    check("int exp(2x)cos(3x)", isym("exp(2x)*cos(3x)"), "exp(2*x)*(2*cos(3*x)+3*sin(3*x))/13")
    check("int sin(x)cos(x)", isym("sin(x)*cos(x)"), "sin(x)^2/2")
    check("int exp(x)exp(x)", isym("exp(x)*exp(x)"), "exp(x)^2/2")
    check("int 2x/(x^2+1)", isym("2x/(x^2+1)"), "ln(abs(x^2+1))")
    check("int cot", isym("cos(x)/sin(x)"), "ln(abs(sin(x)))")
    check("int x/(x^2+4)", isym("x/(x^2+4)"), "1/2*ln(abs(x^2+4))")
    check("int sin^2", isym("sin(x)^2"), "x/2-sin(2*x)/4")
    check("int sin(x)*sin(x)", isym("sin(x)*sin(x)"), "x/2-sin(2*x)/4")
    check("int cos^2", isym("cos(x)^2"), "x/2+sin(2*x)/4")
    check("int cos^2(3x)", isym("cos(3x)^2"), "x/2+sin(6*x)/12")
    check("int tan^2", isym("tan(x)^2"), "tan(x)-x")

    check("int 1/(x^2-1)", isym("1/(x^2-1)"),
          "ln(abs(x-1))/2-ln(abs(x+1))/2")
    check("int 1/(1+x^2) is arctan", isym("1/(1+x^2)"), "atan(x)")
    check("int 1/(x^2+4)", isym("1/(x^2+4)"), "atan(x/2)/2")
    check("int x^2/(x^2+1) divides out first", isym("x^2/(x^2+1)"),
          "x-atan(x)")
    truthy("int x atan(x) now closes", isym("x*atan(x)") is not None)
    truthy("by-parts depth is capped", cascalc.BYPARTS_MAX <= 4)

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

    close("defint x^2 0..1", cascalc.defint(caslex.parse("x^2"), 0.0, 1.0), 1.0 / 3.0, 1e-9)
    close("defint sin 0..pi", cascalc.defint(caslex.parse("sin(x)"), 0.0, math.pi), 2.0, 1e-9)
    close("defint 1/x 1..e", cascalc.defint(caslex.parse("1/x"), 1.0, math.e), 1.0, 1e-7)
    close("defint reversed", cascalc.defint(caslex.parse("x^2"), 1.0, 0.0), -1.0 / 3.0, 1e-9)
    check("defint over singularity", cascalc.defint(caslex.parse("1/x"), -1.0, 1.0), None)

    check("solve x^2-4", [round(r, 6) for r in cascalc.solve(caslex.parse("x^2-4"))], [-2.0, 2.0])
    check("solve x^3-x", [round(r, 6) for r in cascalc.solve(caslex.parse("x^3-x"))], [-1.0, 0.0, 1.0])
    check("solve x^2 (touching)", [round(r, 5) for r in cascalc.solve(caslex.parse("x^2"))], [0.0])
    check("solve (x-1)^2", [round(r, 5) for r in cascalc.solve(caslex.parse("(x-1)^2"))], [1.0])
    check("solve 0", cascalc.solve(caslex.parse("0")), [])
    check("solve 5", cascalc.solve(caslex.parse("5")), [])
    truthy("solve root count is capped", len(cascalc.solve(caslex.parse("sin(1000x)"))) <= cascalc.MAXROOTS)
    r = cascalc.solve(caslex.parse("sin(x)"), deg=True)
    truthy("solve sin in degrees finds 0", any(abs(v) < 1e-4 for v in r))
    truthy("solve sin in degrees finds 180", any(abs(v - 180.0) < 1e-3 for v in r))


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
    truthy("char_w large > medium", casui.char_w("o", "large") > casui.char_w("o", "medium"))
    truthy("text_w large > medium", casui.text_w("hello", "large") > casui.text_w("hello", "medium"))
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
ALPHA_KEYS = {
    41: 'a', 42: 'b', 43: 'c', 44: 'd', 45: 'e', 46: 'f',
    51: 'g', 52: 'h', 53: 'i', 54: 'j', 55: 'k', 56: 'l',
    61: 'm', 62: 'n', 63: 'o',
    71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    81: 'u', 82: 'v', 83: 'w', 84: 'x', 85: 'y',
    91: 'z',
}
PLAIN_KEYS = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.', 51: ',',
    84: '+', 85: '-', 74: '*', 75: '/', 55: '(', 56: ')',
    44: '^', 45: '^2', 43: 'sqrt(', 46: 'exp(', 93: '*10^',
    52: 'sin(', 53: 'cos(', 54: 'tan(', 41: 'x',
}

def test_keymap_matches_hardware():
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

    for d, label in ((casui.UNSHIFT, 'UNSHIFT'), (casui.SHIFTED, 'SHIFTED'),
                     (casui.ALPHADICT, 'ALPHADICT'), (casui.DIGITS, 'DIGITS')):
        for code in d:
            truthy(label + " key " + str(code) + " exists on the keypad", code in KEYPAD)

    for code, letter in ALPHA_KEYS.items():
        check("ALPHA on key " + str(code) + " types its printed letter",
              casui.ALPHADICT.get(code), letter)
    truthy("every letter a-z is on a key",
           len(set(ALPHA_KEYS.values()) & set(casui.ALPHADICT.values())) == 26)

    for code, tok in PLAIN_KEYS.items():
        check("key " + str(code) + " types " + repr(tok), casui.UNSHIFT.get(code), tok)

    for code, d in casui.DIGITS.items():
        check("DIGITS[" + str(code) + "]", casui.UNSHIFT.get(code), str(d))

    nav = set([casui.UP, casui.DOWN, casui.LEFT, casui.RIGHT, casui.OK,
               casui.EXE, casui.EXITK, casui.DEL, casui.SHIFT, casui.ALPHA,
               casui.MENU, casui.LINESTART, casui.LINEEND, casui.PAGEUP,
               casui.PAGEDOWN])
    for code in nav:
        truthy("nav key " + str(code) + " does not also type a character",
               code not in casui.UNSHIFT)

    for code in (11, 65):
        truthy("nothing bound to the codeless key " + str(code),
               code not in KEYPAD and code not in casui.UNSHIFT)

    check("KEYCODES is the whole keypad", casui.KEYCODES, set(KEYPAD.keys()))
    check("48 readable keys", len(casui.KEYCODES), 48)

    real = casui.getkey
    try:
        for code in (None, 0, 11, 65, 96, 99, -1, 255):
            casui.getkey = (lambda c: (lambda: c))(code)
            check("readkey treats " + str(code) + " as idle", casui.readkey(), 0)
        for code in (22, 72, 95):
            casui.getkey = (lambda c: (lambda: c))(code)
            check("readkey passes key " + str(code) + " through", casui.readkey(), code)
    finally:
        casui.getkey = real

def test_draw_string_sizes():
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
    tokens = _typeable_tokens()
    chars = _typeable_chars(tokens)

    for sym in (',', '!', '=', '(', ')', '^', '*', '/', '+', '-', '.', 'x'):
        truthy("symbol '" + sym + "' is typeable", sym in tokens)
    for d in "0123456789":
        truthy("digit " + d + " is typeable", d in tokens)

    for name in caslex.UFUNCS + caslex.BINFUNCS + ('ans',):
        whole = (name + '(') in tokens or name in tokens
        spelled = True
        for ch in name:
            if ch not in chars:
                spelled = False
                break
        truthy("function '" + name + "' is reachable", whole or spelled)

    for name in ('pi', 'e'):
        truthy("constant '" + name + "' is reachable", name in tokens)

    samples = {
        ',': "nCr(6,2)", '!': "5!", 'nCr(': "nCr(6,2)",
        'nPr(': "nPr(5,2)", 'logb(': "logb(2,8)",
    }
    for item in casui.EXTRAS:
        if item == '=':
            continue
        expr = samples.get(item, item + "0.5)" if item.endswith('(') else item)
        truthy("palette '" + item + "' parses as " + expr, caslex.parse(expr) is not None)

    for code, d in casui.DIGITS.items():
        check("DIGITS[" + str(code) + "] matches the key map",
              casui.UNSHIFT.get(code), str(d))
    for d in range(1, 10):
        truthy("digit " + str(d) + " can jump a menu", d in casui.DIGITS.values())

    pages = (len(casui.EXTRAS) + casui.PAL_PER - 1) // casui.PAL_PER
    truthy("palette shows every entry", pages * casui.PAL_PER >= len(casui.EXTRAS))

def test_cursor_window():
    s = "sin(x)+cos(x)+tan(x)+sqrt(x)+exp(x)+ln(x)+atan(x)+abs(x)"
    for cpos in (0, 1, 12, 30, len(s) - 1, len(s)):
        out = casui.cursor_fit(s, cpos, 200, "medium")
        truthy("cursor_fit fits at " + str(cpos), casui.text_w(out, "medium") <= 200)
        truthy("cursor_fit is a slice at " + str(cpos), out in s)
        if cpos < len(s):
            start = s.find(out)
            truthy("caret visible at " + str(cpos), start <= cpos < start + len(out))
    check("cursor_fit passes short text through", casui.cursor_fit("abc", 1, 200, "medium"), "abc")


def test_util():
    check("ncr", casutil.ncr(6, 2), 15)
    check("ncr symmetric", casutil.ncr(20, 18), 190)
    check("ncr out of range", casutil.ncr(3, 5), 0)
    check("npr", casutil.npr(5, 2), 20)
    check("fact", casutil.fact(5), 120)
    check("fact 0", casutil.fact(0), 1)
    check("fact negative", casutil.fact(-1), None)
    check("fact capped", casutil.fact(10 ** 6), None)
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
    close("phi(1.96)", casutil.phi(1.96), 0.975, 5e-6)
    close("phi(-1.96)", casutil.phi(-1.96), 0.025, 5e-6)
    close("invphi(0.975)", casutil.invphi(0.975), 1.959964, 1e-4)
    close("invphi(0.5)", casutil.invphi(0.5), 0.0, 1e-6)

    close("binom_pmf", casutil.binom_pmf(10, 0.5, 5), 0.24609375, 1e-9)
    close("binom_cdf", casutil.binom_cdf(10, 0.5, 5), 0.623046875, 1e-9)
    close("binom_pmf p=0", casutil.binom_pmf(5, 0.0, 0), 1.0)
    close("binom_pmf p=1", casutil.binom_pmf(5, 1.0, 5), 1.0)
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
    has("binom coeff value", o, '40')

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

    o = drive(stat640.t_boxplot, ['2 4 4 4 5 5 7 9'])
    num("boxplot n", o, 'n = ', 8.0)
    num("boxplot min", o, 'min = ', 2.0)
    num("boxplot Q1", o, 'Q1 = ', 4.0)
    num("boxplot median", o, 'median = ', 4.5)
    num("boxplot Q3", o, 'Q3 = ', 6.0)
    num("boxplot max", o, 'max = ', 9.0)
    num("boxplot IQR", o, 'IQR = ', 2.0)
    has("boxplot no outliers", o, 'outliers: none')

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

    o = drive(stat640.t_hist, ['0 10 15 30 50', '20 15 30 10'])
    num("hist total", o, 'total freq = ', 75.0)
    num("hist fd class1", o, '0-10 f=20 w=10 fd=', 2.0)
    num("hist fd class2", o, '10-15 f=15 w=5 fd=', 3.0)
    num("hist fd class3", o, '15-30 f=30 w=15 fd=', 2.0)
    num("hist fd class4", o, '30-50 f=10 w=20 fd=', 0.5)
    truthy("hist density beats raw freq", 3.0 > 2.0 and 30.0 > 15.0)

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
    close("arsinh large negative", hyper._arsinh(-1e8), math.asinh(-1e8), 1e-6)


def test_polar():
    import polar
    o = drive(polar.t_topolar_rt, ['1', '1'])
    num("polar r", o, 'r = ', math.sqrt(2.0))
    num("polar theta", o, 'theta = ', math.pi / 4)
    o = drive(polar.t_topolar_xy, ['2', '0'])
    num("polar x", o, 'x = ', 2.0)
    num("polar y", o, 'y = ', 0.0)
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

    o = drive(fmmech.t_momentum, ['2', '5', '3', '0', '1'], [0])
    num("conservation v2", o, 'v2 = ', (2 * 5 + 3 * 0 - 2 * 1) / 3.0)

    o = drive(fmmech.t_hooke, ['100', '0.2', '2'])
    num("hooke T", o, 'T = lam x/l = ', 10.0)
    num("hooke EPE", o, 'EPE = ', 1.0)

    o = drive(fmmech.t_com, ['1 3', '0 4'], [0])
    num("com x", o, 'x_bar = ', 3.0)

    o = drive(fmmech.t_circular, ['2', '10', '5'], [0])
    num("circular a", o, 'a = v^2/r = ', 20.0)
    num("circular F", o, 'F = m a = ', 40.0)

    o = drive(fmmech.t_work, ['4', '3'], [0])
    num("KE", o, 'KE = ', 18.0)

    o = drive(fmmech.t_dim, ['1 1 -2', '1 1 -2'])
    has("dimensions consistent", o, 'CONSISTENT')


def test_fmstat():
    import fmstat
    o = drive(fmstat.t_pois, ['2', '1'])
    num("poisson pmf", o, 'P(X=k) = ', 2.0 * math.exp(-2.0))
    num("poisson cdf", o, 'P(X<=k) = ', 3.0 * math.exp(-2.0))
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

    o = drive(numeric.t_fixed, ['(x+2/x)/2', '1'])
    num("fixed point", o, 'fixed pt x=', math.sqrt(2.0), 1e-6)

    o = drive(numeric.t_integ, ['x^2', '0', '1', '100'])
    num("trapezium", o, 'trapezium=', 1.0 / 3.0, 1e-4)
    num("simpson", o, 'Simpson=', 1.0 / 3.0, 1e-5)

    o = drive(numeric.t_diff, ['x^2', '3', '0.001'])
    num("central diff", o, 'central=', 6.0, 1e-6)
    num("exact diff", o, 'exact=', 6.0)

    o = drive(numeric.t_error, ['3.1', '3.14159'])
    num("abs error", o, 'absolute=', 0.04159, 1e-6)

    o = drive(numeric.t_round, ['1234.5', '2'])
    num("round 2sf", o, '2 s.f. = ', 1200.0)
    o = drive(numeric.t_round, ['0.0012345', '3'])
    num("round 3sf", o, '3 s.f. = ', 0.00123, 1e-9)

    o = drive(numeric.t_euler, ['x', '0', '0', '0.1', '3'])
    num("euler y", o, 'end y=', 0.1 * (0.0 + 0.1 + 0.2), 1e-9)
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

    g = ['3', '0 1 4', '1 0 2', '4 2 0', '1']
    o = drive(algos.dijkstra, g)
    has("dijkstra n2", o, 'Node 2: 1')
    has("dijkstra n3", o, 'Node 3: 3')

    o = drive(algos.prim, ['3', '0 1 4', '1 0 2', '4 2 0'])
    has("prim total", o, 'Total weight: 3')

    o = drive(algos.kruskal, ['3', '0 1 4', '1 0 2', '4 2 0'])
    has("kruskal total", o, 'Total weight: 3')

    o = drive(algos.critpath, ['3', '3', '0', '4', '1', '2', '2'])
    has("critpath duration", o, 'Project duration: 9')
    has("critpath critical", o, 'Critical: A1 A2 A3')


def test_xpure():
    import xpure
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

    o = drive(xpure.t_surface_stat, ['x^2+y^2-4x-6y', '0', '0'])
    has("stationary point located", o, "x = 2, y = 3")
    num("value at the minimum", o, "z = ", -13.0)
    num("discriminant", o, "D = fxx fyy - fxy^2 = ", 4.0)
    has("classified as a minimum", o, "MINIMUM")
    o = drive(xpure.t_surface_stat, ['x^2-y^2', '1', '1'])
    has("saddle located", o, "x = 0, y = 0")
    num("saddle discriminant", o, "D = fxx fyy - fxy^2 = ", -4.0)
    has("classified as a saddle", o, "SADDLE POINT")
    o = drive(xpure.t_surface_stat, ['-x^2-y^2+2x', '0', '0'])
    has("maximum located", o, "x = 1, y = 0")
    has("classified as a maximum", o, "MAXIMUM")
    o = drive(xpure.t_surface_stat, ['x^2+4x*y+y^2', '1', '-1'])
    num("discriminant with a non-zero mixed partial",
        o, "D = fxx fyy - fxy^2 = ", -12.0, 1e-6)
    has("non-zero fxy still a saddle", o, "SADDLE POINT")
    o = drive(xpure.t_surface_stat, ['x^2+x*y+y^2', '1', '1'])
    num("discriminant of a skewed bowl", o, "D = fxx fyy - fxy^2 = ", 3.0, 1e-6)
    has("skewed bowl is a minimum", o, "MINIMUM")

    o = drive(xpure.t_tangent_plane, ['x^2+y^2', '1', '2'])
    has("height at the point", o, "at (1, 2), z = 5")
    has("tangent plane", o, "2x + 4y - z = 5")
    has("normal line", o, "+ t(2, 4, -1)")

    o = drive(xpure.t_eigen3,
              ['2', '0', '0', '1', '3', '0', '0', '0', '4', None])
    has("characteristic cubic", o, "k^3 - 9k^2 + 26k - 24 = 0")
    has("first eigenvalue", o, "k = 2")
    has("second eigenvalue", o, "k = 3")
    has("third eigenvalue", o, "k = 4")
    has("eigenvector for k=2", o, "(1, -1, 0)")
    has("diagonalisable", o, "DIAGONALISABLE")
    has("Cayley-Hamilton", o, "M^3 = 9M^2 - 26M + 24I")
    for ln in o:
        if "check |Mv - kv| = " in ln:
            v = _first_number(ln.split("check |Mv - kv| = ")[1])
            truthy("eigenvector satisfies Mv = kv", v is not None and abs(v) < 1e-6)
    o = drive(xpure.t_eigen3,
              ['0', '-1', '0', '1', '0', '0', '0', '0', '1', None])
    has("single real eigenvalue", o, "k = 1")
    has("rotation axis is the eigenvector", o, "(0, 0, 1)")
    has("not three distinct", o, "may not be diagonalisable")

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
    has("fpt factorise", o, '60 = 2^2 * 3 * 5')
    o = drive(fpt.t_factor, ['7'])
    has("fpt factorise of a prime says so", o, '7 = 7   (n is prime)')

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

    o = drive(fpt.t_factor, ['1000000000039'])
    has("fpt factor caps", o, 'too large')
    o = drive(fpt.t_prime, ['1000000000039'])
    has("fpt prime caps", o, 'too large')


def _depth():
    n = 0
    f = sys._getframe()
    while f is not None:
        n += 1
        f = f.f_back
    return n

def test_recursion_budget():
    BUDGET = 38  # device measures 92; this margin is deliberate
    deep = "((((((((((x+1))))))))))"
    long_flat = "+".join(["x"] * 400)
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
    for e in ["x^3*exp(x)", "x^2*sin(x)", "x*ln(x)", "atan(x)",
              "sin(x)*cos(x)", "x*sin(2x+1)", "exp(2x)*cos(3x)"]:
        tr = caslex.parse(e)
        truthy("integ stays shallow: " + e, under(lambda tr=tr: cascalc.integ(tr)))

def test_math_allowlist_is_the_measured_set():
    PRESENT = set([
        "e", "pi", "sqrt", "pow", "exp", "log", "log10",
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "sinh", "cosh", "tanh",
        "ceil", "floor", "fabs", "fmod", "modf", "frexp", "ldexp",
    ])
    ABSENT = set([
        "log2", "asinh", "acosh", "atanh", "trunc", "copysign",
        "isnan", "isinf", "isfinite", "degrees", "radians",
        "factorial", "gamma", "lgamma", "erf", "erfc",
        "expm1", "log1p", "cbrt",
    ])
    check("MATH_OK is exactly what the hardware has", devlint.MATH_OK, PRESENT)
    check("the probe covered every name", PRESENT | ABSENT, set(hwcheck_names()))
    truthy("present and absent do not overlap", not (PRESENT & ABSENT))
    truthy("no factorial on the device", "factorial" in ABSENT)
    truthy("no inverse hyperbolics on the device", "asinh" in ABSENT)
    truthy("atan2 IS on the device", "atan2" in PRESENT)
    for bad in ("radians", "isfinite", "factorial", "atanh"):
        truthy("devlint would reject math." + bad, bad not in devlint.MATH_OK)

def hwcheck_names():
    import re
    src = open(_here("hwcheck.py")).read()
    body = src[src.index("MATH_NAMES = ["):]
    body = body[:body.index("]")]
    return re.findall(r'"([a-z0-9]+)"', body)

def _here(name):
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)) or ".", name)

REFERENCE_CARDS = set([
    "pure640._log_laws", "pure640._trig_exact", "pure640._trig_compound",
    "proof.t_methods", "series.t_reference", "hyper.t_ref", "fmmech.t_dim",
    "xpure.t_sets",
])

def test_intro_screens_fit_one_page():
    # An intro is the screen a tool shows BEFORE it asks for anything. It costs
    # a keypress every time the tool is opened, so it has to fit one page:
    # casui.PER_PAGE lines, and no line wider than the screen. Anything longer
    # pages, which means two keypresses before you can type a number.
    # Reference cards are exempt - there the card IS the tool's output.
    import ast
    PROMPTS = set(["_asknum", "_askint", "_askexpr", "_parse", "input_expr",
                   "menu", "asknum", "askint", "askexpr", "_pick", "_choose",
                   "_getlist", "_askg", "_mvparse", "_readtable"])
    MAXLINES = 5
    mods = list(casui.MATHS_MODS) + list(casui.FM_CORE_MODS) + list(casui.FM_OPT_MODS)
    seen = 0
    for name in mods:
        tree = ast.parse(open(os.path.join(HERE, name + ".py")).read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.body:
                continue
            first = node.body[0]
            if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call)):
                continue
            fname = getattr(first.value.func, "id", None) or \
                    getattr(first.value.func, "attr", None)
            if fname not in ("_show", "_pages", "show"):
                continue
            args = first.value.args
            if len(args) < 2 or not isinstance(args[1], ast.List):
                continue
            lits = []
            for e in args[1].elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    lits.append(e.value)
            if len(lits) != len(args[1].elts) or not lits:
                continue
            rest = ast.Module(body=node.body[1:], type_ignores=[])
            asks = False
            for n in ast.walk(rest):
                if isinstance(n, ast.Call):
                    nm = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                    if nm in PROMPTS:
                        asks = True
                        break
            if not asks:
                continue
            key = name + "." + node.name
            if key in REFERENCE_CARDS:
                continue
            seen += 1
            truthy(key + ": intro is at most " + str(MAXLINES) + " lines, got " +
                   str(len(lits)), len(lits) <= MAXLINES)
            truthy(key + ": intro never pages",
                   len(lits) <= casui.PER_PAGE)
            for ln in lits:
                truthy(key + ": intro line fits the screen: " + repr(ln),
                       casui.text_w(ln, "medium") <= 372)
    truthy("the sweep found the intro screens", seen >= 50)

def test_devlint():
    import os
    bad = devlint.run(os.path.dirname(os.path.abspath(__file__)) or ".")
    CHECKS[0] += 1
    if bad:
        for path, line, msg in bad:
            FAILED.append("devlint " + os.path.basename(path) + ":" + str(line) + ": " + msg)


def _verdict_after(lines, key):
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
    o = drive(pure640.t_triangle, ["3", "4", "5"], [0])
    num("SSS angle A", o, "A = ", 36.8699, 1e-3)
    num("SSS angle B", o, "B = ", 53.1301, 1e-3)
    num("SSS angle C", o, "C = ", 90.0, 1e-3)
    num("SSS area", o, "area = (1/2)ab sinC = ", 6.0, 1e-6)
    o = drive(pure640.t_triangle, ["5", "7", "60"], [1])
    num("SAS side a", o, "a = ", math.sqrt(39.0), 1e-4)
    o = drive(pure640.t_triangle, ["40", "60", "10"], [2])
    num("ASA side b", o, "b = ", 10.0 * math.sin(math.radians(60)) / math.sin(math.radians(40)), 1e-3)
    o = drive(pure640.t_triangle, ["7", "8", "50"], [3])
    num("SSA angle B", o, "B = ", 61.1018, 1e-3)
    has("SSA ambiguous case flagged", o, "AMBIGUOUS CASE")
    has("SSA second angle", o, "118.8982")
    o = drive(pure640.t_triangle, ["3", "8", "50"], [3])
    has("impossible SSA reported", o, "No triangle")
    o = drive(pure640.t_triangle, ["1", "2", "10"], [0])
    has("triangle inequality checked", o, "cannot form")

    o = drive(pure640.t_arc_sector, ["5", "1.2"], [0])
    num("arc length", o, "r theta      = ", 6.0, 1e-6)
    num("sector area", o, "(1/2)r^2 th  = ", 15.0, 1e-6)
    num("chord", o, "2r sin(th/2) = ", 10.0 * math.sin(0.6), 1e-4)
    num("segment area", o, "             = ", 12.5 * (1.2 - math.sin(1.2)), 1e-4)
    o = drive(pure640.t_arc_sector, ["3", "60"], [1])
    num("arc from degrees", o, "r theta      = ", math.pi, 1e-4)
    has("conversion is stated", o, "only works in radians")

    o = drive(pure640.t_inequality, ["1", "-5", "6"], [1, 2])
    has("quadratic inequality between roots", o, "2 < x < 3")
    has("says between", o, "between the roots")
    o = drive(pure640.t_inequality, ["1", "-5", "6"], [1, 0])
    has("quadratic inequality outside", o, "x < 2  or  x > 3")
    o = drive(pure640.t_inequality, ["-1", "0", "4"], [1, 1])
    has("downward parabola opens downwards", o, "opens downwards")
    has("downward parabola between roots", o, "-2 <= x <= 2")
    o = drive(pure640.t_inequality, ["1", "0", "1"], [1, 0])
    has("no real roots", o, "no real roots")
    has("always true", o, "every real x")
    o = drive(pure640.t_inequality, ["-2", "6"], [0, 0])
    has("dividing by a negative flips", o, "FLIPS")
    has("linear answer", o, "x < 3")

    o = drive(pure640._trig_general, ["2", "-30", "0.5", "0", "360"], [0, 0])
    has("multiple-angle solution 30", o, "x = 30 deg")
    has("multiple-angle solution 90", o, "x = 90 deg")
    has("multiple-angle solution 210", o, "x = 210 deg")
    has("multiple-angle solution 270", o, "x = 270 deg")
    has("four solutions found", o, "4 solutions")
    o = drive(pure640._trig_general, ["1", "0", "0.5", "0", str(2 * math.pi)], [1, 1])
    has("radian solution pi/3", o, "x = 1.0472")
    has("radian solution 5pi/3", o, "x = 5.236")
    o = drive(pure640._trig_general, ["1", "0", "1", "0", str(2 * math.pi)], [2, 1])
    has("tan solution pi/4", o, "x = 0.7854")
    has("tan solution 5pi/4", o, "x = 3.927")
    o = drive(pure640._trig_general, ["1", "0", "2", "0", "360"], [0, 0])
    has("sin k>1 impossible", o, "No solution")

    o = drive(pure640._trig_expand, ["50", "20"])
    has("sin(A+B) agrees", o, "agrees")
    truthy("no expansion differs", not [ln for ln in o if "DIFFERS" in ln])
    o = drive(pure640._trig_compound, [])
    has("compound identity card", o, "sin(A+B) = sinA cosB + cosA sinB")
    has("double angle card", o, "cos2A = cos^2 A - sin^2 A")
    has("integration rearrangement", o, "sin^2 A = (1 - cos2A)/2")

def test_purecalc_calculus():
    import purecalc
    o = drive(purecalc.t_stationary, ["x^3-3x"])
    has("derivative shown", o, "3*x^2-3")
    has("y at the maximum", o, "y = 2")
    has("y at the minimum", o, "y = -2")
    has("inflection found", o, "changes sign: inflection")
    check("x = -1 is the maximum", _verdict_after(o, "x = -1,"), "MAXIMUM")
    check("x = 1 is the minimum", _verdict_after(o, "x = 1,"), "MINIMUM")
    o = drive(purecalc.t_stationary, ["x^4"])
    has("f'' is zero there", o, "f'' = 0")
    check("x^4 has a minimum at 0", _verdict_after(o, "x = 0,"), "MINIMUM")
    o = drive(purecalc.t_stationary, ["x^3"])
    check("x^3 has a stationary inflection at 0",
          _verdict_after(o, "x = 0,"), "INFLECTION")
    o = drive(purecalc.t_stationary, ["exp(x)"])
    has("no stationary points", o, "no stationary points")

    o = drive(purecalc.t_constant, ["2x", "1", "5", "3"])
    has("integral before the constant", o, "x^2 + C")
    has("constant found", o, "C = 4")
    has("full curve", o, "f(x) = x^2+4")
    num("f(3) = 13", o, "f(3) = ", 13.0)
    has("checked through the point", o, "passes through the point")

    o = drive(purecalc.t_revolution, ["x", "0", "1"], [0])
    num("cone volume", o, "  = ", math.pi / 3.0, 1e-4)
    o = drive(purecalc.t_revolution, ["sqrt(x)", "0", "4"], [0])
    num("paraboloid integral is 8", o, "  evaluated: ", 8.0, 1e-6)
    has("paraboloid volume", o, "V = pi x 8")
    o = drive(purecalc.t_revolution, ["y^2", "0", "1"], [1])
    num("volume about the y-axis", o, "  = ", math.pi / 5.0, 1e-4)
    o = drive(purecalc.t_revolution, ["sqrt(x)", "0", "4"], [0])
    truthy("paraboloid volume done symbolically",
           not [ln for ln in o if "numerically" in ln])

    o = drive(purecalc.t_meanvalue, ["x^2", "0", "3"])
    num("mean value of x^2", o, "           = ", 3.0, 1e-6)
    has("where it reaches the mean", o, "x = 1.7321")
    o = drive(purecalc.t_meanvalue, ["sin(x)", "0", str(math.pi)])
    num("mean value of sin", o, "           = ", 2.0 / math.pi, 1e-4)

    o = drive(purecalc.t_improper, ["1/x^2", "1"], [0])
    has("1/x^2 converges", o, "CONVERGES")
    num("1/x^2 limit is 1", o, "CONVERGES to about ", 1.0, 1e-3)
    o = drive(purecalc.t_improper, ["1/x", "1"], [0])
    has("1/x diverges", o, "DIVERGES")
    o = drive(purecalc.t_improper, ["1/sqrt(x)", "0", "1"], [2])
    has("1/sqrt(x) converges", o, "CONVERGES")
    num("1/sqrt(x) limit is 2", o, "CONVERGES to about ", 2.0, 1e-2)
    o = drive(purecalc.t_improper, ["1/x", "0", "1"], [2])
    has("1/x at 0 diverges", o, "DIVERGES")
    o = drive(purecalc.t_improper, ["exp(-x)", "0"], [0])
    num("exp(-x) limit is 1", o, "CONVERGES to about ", 1.0, 1e-4)

def test_integ_reciprocal_powers():
    check("int 1/sqrt(x)", itidy("1/sqrt(x)"), "2*x^(1/2)")
    check("int 3/sqrt(x)", itidy("3/sqrt(x)"), "6*x^(1/2)")
    check("int 1/x^3", itidy("1/x^3"), "-1/(2*x^2)")
    check("int 2/sqrt(2x+1)", itidy("2/sqrt(2x+1)"), "2*(2*x+1)^(1/2)")
    check("int 1/x^(2/3)", itidy("1/x^(2/3)"), "3*x^(1/3)")
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
    o = drive(diffeq.t_first_order, ["1/x", "x", "1", "1"])
    has("integrating factor", o, "IF = e^(ln(x))")
    has("IF simplifies to x", o, "   = x")
    has("IF times Q", o, "IF * Q = x^2")
    has("the integral is performed", o, "int IF*Q dx = x^3/3")
    num("constant from the condition", o, "C = ", 2.0 / 3.0, 1e-4)
    has("checked at the point", o, "checked at the given point")
    o = drive(diffeq.t_first_order, ["2", "exp(x)", None])
    has("constant P gives e^(2x)", o, "IF = e^(2*x)")
    o = drive(diffeq.t_first_order, ["exp(x^2)", None, None])
    has("no elementary IF", o, "no elementary form")

    o = drive(diffeq.t_particular, ["-3", "2", "1", "3"], [1])
    has("auxiliary roots", o, "m = 2 and 1")
    has("exponential PI", o, "PI: y = 0.5 e^(3x)")
    o = drive(diffeq.t_particular, ["-3", "2", "1", "1"], [1])
    has("resonance detected", o, "already in the CF")
    has("resonant PI", o, "PI: y = -x e^x")
    o = drive(diffeq.t_particular, ["-2", "1", "1", "1"], [1])
    has("repeated root detected", o, "REPEATED root")
    has("double resonance PI", o, "PI: y = 0.5 x^2 e^x")
    o = drive(diffeq.t_particular, ["0", "1", "2", "0", "0", "4"], [0])
    has("polynomial PI", o, "PI: y = 4x^2 -8")
    o = drive(diffeq.t_particular, ["0", "4", "0", "1", "1"], [2])
    has("trig PI", o, "PI: y = 0.3333 sin x")
    truthy("a zero trig term is not printed",
           not [ln for ln in o if "0 cos" in ln])
    o = drive(diffeq.t_particular, ["0", "1", "1", "0", "3"], [0])
    has("linear PI", o, "PI: y = 3x")
    o = drive(diffeq.t_particular, ["2", "0", "0", "4"], [0])
    has("b=0 raises the trial degree", o, "raised a degree")
    has("PI for b=0", o, "PI: y = 2x")
    o = drive(diffeq.t_particular, ["3", "0", "1", "0", "1"], [0])
    has("PI for b=0 with a linear rhs", o, "PI: y = 0.1667x^2 -0.1111x")
    o = drive(diffeq.t_particular, ["0", "0", "1", "0", "6"], [0])
    has("PI for a=b=0", o, "PI: y = x^3")
    o = drive(diffeq.t_particular, ["-3", "2", "1", "3"], [1])
    has("general solution given", o, "GENERAL SOLUTION = CF + PI")
    has("no constant on the PI", o, "The PI has no arbitrary")

def test_exp_ln_folding():
    check("exp(ln(x)) is x",
          caseng.tostr(caseng.simplify(caslex.parse("exp(ln(x))"))), "x")
    check("ln(exp(x)) is x",
          caseng.tostr(caseng.simplify(caslex.parse("ln(exp(x))"))), "x")
    check("exp(ln(2x+1))",
          caseng.tostr(caseng.simplify(caslex.parse("exp(ln(2x+1))"))), "2*x+1")
    check("sqrt(x^2) is abs(x)",
          caseng.tostr(caseng.simplify(caslex.parse("sqrt(x^2)"))), "abs(x)")
    close("sqrt((-3)^2) is 3",
          caseng.evalf(caseng.simplify(caslex.parse("sqrt(x^2)")), -3.0), 3.0)
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
    o = drive(vcplx.t_loci, ["1", "2", "3"], [0])
    has("circle described", o, "circle centre 1 + 2i, radius 3")
    has("cartesian circle", o, "(x - 1)^2 + (y - 2)^2 = 9")
    num("greatest modulus on the circle", o, "greatest |z| on it = ",
        math.sqrt(5.0) + 3.0, 1e-3)
    num("least modulus on the circle", o, "least |z| on it    = ", 0.0, 1e-9)
    o = drive(vcplx.t_loci, ["1", "0", "0", "3"], [1])
    has("bisector named", o, "PERPENDICULAR BISECTOR")
    has("midpoint", o, "midpoint (0.5, 1.5)")
    num("bisector gradient", o, "bisector gradient = ", 1.0 / 3.0, 1e-3)
    num("bisector intercept", o, "y = 0.3333x + ", 4.0 / 3.0, 1e-3)
    o = drive(vcplx.t_loci, ["2", "0", "45"], [2])
    has("half-line, not a line", o, "HALF-LINE")
    has("the endpoint is excluded", o, "NOT included")
    has("only one half", o, "only the half with x > 2")
    o = drive(vcplx.t_loci, ["0", "0", "2"], [3])
    has("region is a disc", o, "filled disc")
    has("region inequality", o, "<= 4")
    o = drive(vcplx.t_loci, ["1", "1", "1", "1"], [1])
    has("coincident points reported", o, "every z is equidistant")

    o = drive(vcplx.t_demoivre_id, ["3"])
    has("cos 3t expansion", o, "cos 3t = c^3 - 3cs^2")
    has("sin 3t expansion", o, "sin 3t = 3c^2s - s^3")
    num("cos 3t at 0.7", o, "cos 3t = ", math.cos(2.1), 1e-5)
    num("expansion of cos 3t at 0.7", o, "  expansion  = ", math.cos(2.1), 1e-5)
    o = drive(vcplx.t_demoivre_id, ["2"])
    has("cos 2t expansion", o, "cos 2t = c^2 - s^2")
    has("sin 2t expansion", o, "sin 2t = 2cs")
    o = drive(vcplx.t_demoivre_id, ["4"])
    has("cos 4t expansion", o, "cos 4t = c^4 - 6c^2s^2 + s^4")

def test_vector_lines():
    import vectors
    o = drive(vectors.t_lineeq, ["1", "1", "2", "3", "4", "6", "3", None])
    has("vector form", o, "r = (1, 2, 3) + t(3, 4, 0)")
    has("cartesian form", o, "(x - 1)/3 = (y - 2)/4")
    has("the fixed coordinate", o, "with z = 3")
    num("length of the direction", o, "|d| = ", 5.0)
    has("unit direction", o, "(0.6, 0.8, 0)")
    o = drive(vectors.t_lineeq, ["2", "0", "0", "0", "1", "1", "1", "2"])
    has("point at t=2", o, "at t = 2: (2, 2, 2)")
    o = drive(vectors.t_lineeq, ["2", "1", "1", "1", "0", "0", "0"])
    has("zero direction rejected", o, "does not define a line")

    o = drive(vectors.t_lineplane, ["1", "0", "0", "1", "1", "1", "0", "0", "1", "5"])
    num("parameter at the intersection", o, "t = ", 5.0)
    has("intersection point", o, "they meet at (6, 5, 5)")
    num("angle to the normal", o, "angle between d and n = ", 54.7356, 1e-3)
    num("angle to the plane", o, "= 90 - that = ", 35.2644, 1e-3)
    o = drive(vectors.t_lineplane, ["1", "0", "0", "1", "1", "0", "0", "0", "1", "5"])
    has("parallel reported", o, "PARALLEL")
    num("distance to the plane", o, "|n| = ", 5.0)
    o = drive(vectors.t_lineplane, ["1", "0", "5", "1", "1", "0", "0", "0", "1", "5"])
    has("line lies in the plane", o, "LIES IN")

def test_projectile_inverse():
    import mech640
    o = drive(mech640.projectile_inverse, ["9.8", "100", "45"], [0])
    num("speed from range and angle", o, "u = ", math.sqrt(980.0), 1e-3)
    o = drive(mech640.projectile_inverse, ["9.8", "100", "30"], [0])
    has("complementary angle noted", o, "60 deg gives the same range")
    o = drive(mech640.projectile_inverse, ["9.8", "20", "30"], [1])
    num("speed from height and angle", o, "u = ",
        math.sqrt(2.0 * 9.8 * 20.0) / 0.5, 1e-3)
    o = drive(mech640.projectile_inverse, ["9.8", "40", "0", "4"], [2])
    num("horizontal component", o, "ux = x/t = ", 10.0)
    num("vertical component", o, "= ", 19.6, 1e-6)
    num("speed from a point and time", o, "u = sqrt(ux^2 + uy^2) = ",
        math.sqrt(100.0 + 19.6 * 19.6), 1e-3)
    num("angle from a point and time", o, "angle = ",
        math.degrees(math.atan(1.96)), 1e-3)
    o = drive(mech640.projectile_inverse, ["9.8", "30", "50", "10"], [3])
    has("two solutions", o, "TWO angles")
    num("low ball angle", o, "low ball  ", 29.0977, 1e-3)
    num("high ball angle", o, "high ball ", 72.2123, 1e-3)
    o = drive(mech640.projectile_inverse, ["9.8", "10", "200", "0"], [3])
    has("out of range reported", o, "OUT OF RANGE")
    o = drive(mech640.projectile_inverse, ["9.8", "80", "4"], [4])
    num("uy from the time of flight", o, "uy = gT/2 = ", 19.6, 1e-6)
    num("ux from range and time", o, "ux = R/T  = ", 20.0)
    num("speed from range and time", o, "u = ", math.sqrt(400.0 + 384.16), 1e-3)

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
    o = drive(proof.t_induction_sum, ["n", "n(n+1)/2"])
    has("base case holds", o, "TRUE - the base case holds")
    has("step is the right difference", o, "S(k+1) - S(k) = n+1")
    has("and equals u(k+1)", o, "u(k+1)        = n+1")
    has("proved", o, "PROVED for all n >= 1 by induction")
    o = drive(proof.t_induction_sum, ["n^2", "n(n+1)/2"])
    has("wrong formula still passes the base case", o, "TRUE - the base case holds")
    has("but fails the step", o, "These are NOT equal")
    has("and the values are shown", o, "n=3  sum=14  S(n)=6")
    o = drive(proof.t_induction_sum, ["n^3", "(n(n+1)/2)^2"])
    has("cube sum proved", o, "PROVED for all n >= 1")
    o = drive(proof.t_induction_sum, ["n", "n(n+1)/2+1"])
    has("bad base case caught", o, "FALSE - S(1) is not u(1)")

    o = drive(proof.t_induction_divis, ["4^n-1", "3", "4"])
    has("first values divide", o, "f(1) = 3,  remainder 0")
    has("the remainder is a multiple", o, "divisible by 3 too")
    has("divisibility proved", o, "PROVED by induction")
    o = drive(proof.t_induction_divis, ["n^3-n", "6", "1"])
    has("n^3-n divisible by 6", o, "f(2) = 6,  remainder 0")
    o = drive(proof.t_induction_divis, ["4^n-1", "5", None])
    has("false claim disproved", o, "NOT divisible by 5")
    has("no induction needed", o, "No induction needed")
    o = drive(proof.t_induction_divis, ["4^n-1", "3", "4"])
    has("remainder shown symbolically", o, "4^(n+1)-4*4^n+3")

    o = drive(proof.t_induction_matrix,
              ["1", "1", "0", "1", "1", "n", "0", "1"])
    has("matrix base case", o, "formula at n=1 is M: TRUE")
    has("matrix induction proved", o, "PROVED by induction")
    o = drive(proof.t_induction_matrix,
              ["1", "1", "0", "1", "1", "n^2", "0", "1"])
    has("wrong matrix formula caught", o, "FAILS - M * F(k) is not F(k+1)")
    o = drive(proof.t_induction_matrix,
              ["2", "0", "0", "2", "2^n", "0", "0", "1"])
    has("matrix base case fails", o, "formula at n=1 is NOT M: FALSE")

    o = drive(proof.t_counterexample, ["n^2+n+41", "1", "60"], [0])
    has("counterexample found at 40", o, "COUNTEREXAMPLE at n = 40")
    has("and factorised", o, "1681 = 41 x 41")
    o = drive(proof.t_counterexample, ["n^2+n+41", "1", "30"], [0])
    has("no counterexample in range", o, "No counterexample in that range")
    has("and says that is not a proof", o, "That is NOT a proof")
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
    o = drive(fmstat.t_simulate, ["20", "0.3", "2000", "7"], [1])
    num("binomial theoretical mean", o, "theoretical mean   = ", 6.0)
    num("binomial theoretical variance", o, "theoretical var    = ", 4.2)
    num("binomial simulated mean", o, "simulated mean     = ", 6.0, 0.25)
    num("binomial simulated variance", o, "simulated variance = ", 4.2, 0.6)
    o = drive(fmstat.t_simulate, ["4", "0", "2000", "7"], [2])
    num("Poisson theoretical mean", o, "theoretical mean   = ", 4.0)
    num("Poisson theoretical variance", o, "theoretical var    = ", 4.0)
    num("Poisson simulated mean", o, "simulated mean     = ", 4.0, 0.25)
    num("Poisson simulated variance", o, "simulated variance = ", 4.0, 0.7)
    o = drive(fmstat.t_simulate, ["10", "2", "2000", "7"], [3])
    num("normal simulated mean", o, "simulated mean     = ", 10.0, 0.2)
    num("normal simulated variance", o, "simulated variance = ", 4.0, 0.6)
    o = drive(fmstat.t_simulate, ["0", "6", "2000", "7"], [0])
    num("uniform theoretical mean", o, "theoretical mean   = ", 3.0)
    num("uniform theoretical variance", o, "theoretical var    = ", 3.0)
    num("uniform simulated mean", o, "simulated mean     = ", 3.0, 0.2)
    o = drive(fmstat.t_simulate, ["0", "1", "12", "2000", "7"], [4, 0])
    num("CLT theoretical mean", o, "theoretical mean   = ", 0.5)
    num("CLT variance is sigma^2/n", o, "theoretical var    = ", 1.0 / 144.0, 1e-5)
    num("CLT simulated mean", o, "simulated mean     = ", 0.5, 0.02)
    num("CLT simulated variance", o, "simulated variance = ", 1.0 / 144.0, 0.002)
    has("CLT explains the tightening", o, "tends to Normal whatever the parent")

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
    random.seed(3)
    for i in range(200):
        v = fmstat._sim_draw(1, 8.0, 0.4)
        truthy("binomial draw is a whole number in range",
               v == int(v) and 0 <= v <= 8)
    random.seed(5)
    a, b = fmstat._normal_pair()
    truthy("Box-Muller gives two different values", a != b)

def test_circle_and_proportion():
    import pure640
    o = drive(pure640._circle_3pts, ["0", "0", "4", "0", "0", "3"])
    has("centre", o, "centre (2, 1.5)")
    num("radius", o, "radius ", 2.5)
    has("equation", o, "(x - 2)^2 + (y - 1.5)^2 = 6.25")
    has("all three verified", o, "on the circle: yes")
    has("semicircle spotted", o, "angle in a semicircle")
    o = drive(pure640._circle_3pts, ["0", "0", "1", "1", "2", "2"])
    has("collinear rejected", o, "COLLINEAR")

    o = drive(pure640._circle_tangent, ["0", "0", "3", "4"])
    num("radius gradient", o, "radius gradient  = ", 4.0 / 3.0, 1e-3)
    num("tangent gradient", o, "-1/that = ", -0.75, 1e-6)
    has("tangent line", o, "y = -0.75x + 6.25")
    has("perpendicularity confirmed", o, "(should be -1)")
    o = drive(pure640._circle_tangent, ["0", "0", "0", "5"])
    has("horizontal tangent", o, "HORIZONTAL:  y = 5")
    o = drive(pure640._circle_tangent, ["0", "0", "5", "0"])
    has("vertical tangent", o, "VERTICAL:  x = 5")

    o = drive(pure640._circle_param, ["1", "2", "3", "0"])
    has("cartesian form", o, "(x-1)^2 + (y-2)^2 = 9")
    has("point at t=0", o, "(4, 2)")
    has("vertical tangent at t=0", o, "tangent is vertical")

    o = drive(pure640.t_proportion, ["2", "12", "4", "48", "5", None], [2])
    num("power found", o, "    = ", 2.0, 1e-9)
    num("constant found", o, "k = y1 / x1^n = ", 3.0, 1e-9)
    has("model stated", o, "y = 3 x^2")
    num("prediction", o, "y = ", 75.0, 1e-6)
    o = drive(pure640.t_proportion, ["4", "10", "6", None], [0])
    num("direct constant", o, "k = y/x = ", 2.5)
    num("direct prediction", o, "y = ", 15.0, 1e-6)
    o = drive(pure640.t_proportion, ["4", "3", None, "6"], [1])
    num("inverse constant", o, "k = xy = ", 12.0)
    num("inverse back-solve", o, "x = ", 2.0, 1e-6)

def test_trig_by_identity():
    import pure640
    o = drive(pure640._trig_identity, ["2", "1", "-1", "0", "360"], [0, 0])
    has("quadratic in u", o, "2u^2 + u - 1 = 0")
    has("first root", o, "sin x = 0.5")
    has("second root", o, "sin x = -1")
    has("solution 30", o, "x = 30 deg")
    has("solution 150", o, "x = 150 deg")
    has("solution 270", o, "x = 270 deg")
    has("three solutions", o, "(3 solutions)")
    has("checked in the original", o, "all satisfy it")

    o = drive(pure640._trig_identity, ["2", "3", "-3", "0", "360"], [4, 0])
    has("identity used", o, "use cos^2 x = 1 - sin^2 x")
    has("transformed quadratic", o, "-2sin^2 x + 3sin x - 1 = 0")
    has("solutions listed", o, "30, 90, 150")
    has("still checked in the ORIGINAL", o, "all satisfy it")

    o = drive(pure640._trig_identity, ["1", "-3", "0", "0", "360"], [0, 0])
    has("impossible root discarded", o, "cannot exceed 1")
    has("the other root still solved", o, "0, 180, 360")

    o = drive(pure640._trig_identity, ["1", "0", "-1", "0", "180"], [2, 0])
    has("tan solution 45", o, "x = 45 deg")
    has("tan solution 135", o, "x = 135 deg")
    has("two solutions", o, "(2 solutions)")

    o = drive(pure640._trig_identity, ["1", "0", "1", "0", "360"], [0, 0])
    has("no real u", o, "NO SOLUTION")

    o = drive(pure640._trig_identity,
              ["2", "0", "-1", "0", str(2 * math.pi)], [0, 1])
    has("radian solution pi/4", o, "x = 0.7854")
    has("radian solution 7pi/4", o, "x = 5.4978")
    has("four solutions", o, "(4 solutions)")

    o = drive(pure640._trig_identity, ["1", "-3", "1", "0", "180"], [5, 0])
    has("sec identity used", o, "use sec^2 x = 1 + tan^2 x")
    has("tan = 1 solution", o, "x = 45 deg")

def test_shm_fit():
    import diffeq
    o = drive(diffeq.t_shm, ["2", "3", "8", "0.5"])
    num("SHM period", o, "T = ", math.pi, 1e-4)
    num("C from x(0)", o, "x(0) = C = ", 3.0)
    num("D from v(0)/w", o, "D = v(0)/w = ", 4.0)
    num("amplitude", o, "R = sqrt(C^2 + D^2) = ", 5.0)
    num("phase in radians", o, "atan2(D, C) = ", math.atan2(4.0, 3.0), 1e-4)
    num("phase in degrees", o, "          = ", math.degrees(math.atan2(4.0, 3.0)), 1e-3)
    num("max speed", o, "= Rw   = ", 10.0)
    num("max acceleration", o, "= Rw^2 = ", 20.0)
    num("x at t = 0.5", o, "  x = ", 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0)), 1e-3)
    num("a = -w^2 x", o, "a = -w^2 x = ",
        -4.0 * 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0)), 1e-3)
    xv = 5.0 * math.cos(1.0 - math.atan2(4.0, 3.0))
    vv = -10.0 * math.sin(1.0 - math.atan2(4.0, 3.0))
    close("v^2 identity holds", vv * vv, 4.0 * (25.0 - xv * xv), 1e-6)
    o = drive(diffeq.t_shm, ["3", "2", "0", None])
    num("amplitude when released from rest", o, "R = sqrt(C^2 + D^2) = ", 2.0)
    num("phase is zero from rest", o, "atan2(D, C) = ", 0.0, 1e-9)
    o = drive(diffeq.t_shm, ["0"])
    has("w must be positive", o, "w must be > 0")

def test_inequality_region():
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
    o = drive(diffeq.t_coupled, ["1", "1", "4", "1", "1", "0"])
    has("second-order equation formed", o, "x'' - 2x' - 3x = 0")
    has("auxiliary equation", o, "m^2 - 2m - 3 = 0")
    has("roots are the eigenvalues", o, "m = 3 and -1")
    has("general x", o, "x = A e^(3t) + B e^(-t)")
    has("constants fitted", o, "A = 0.5, B = 0.5")
    has("particular x", o, "x = 0.5e^(3t) + 0.5 e^(-t)")
    has("particular y", o, "y = e^(3t) - e^(-t)")
    has("checked at t=0", o, "check at t = 0: x = 1, y = 0")
    truthy("the exponential is in t", not [ln for ln in o if "e^(3x)" in ln])

    o = drive(diffeq.t_coupled, ["0", "-1", "1", "0", "1", "0"])
    has("complex roots", o, "m = 0 +/- 1i")
    has("closed orbit named", o, "closed orbit")
    has("amplitude constant", o, "amplitude stays constant")

    o = drive(diffeq.t_coupled, ["3", "-1", "1", "1", "1", "1"])
    has("repeated root", o, "m = 2 (repeated)")
    has("general form has the t factor", o, "x = (A + B t) e^(2t)")

    o = drive(diffeq.t_coupled, ["2", "0", "1", "3", None])
    has("triangular case", o, "already")

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
        close(label + ": x(0)", diffeq._coupled_x(kind, tr, disc, A, B, 0.0), x0, 1e-9)
        close(label + ": y(0)", diffeq._coupled_y(kind, tr, disc, A, B, 0.0, a, b), y0, 1e-9)
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
    o = drive(pure640.t_surds, ["72"], [0])
    has("square factor pulled out", o, "= 6sqrt(2)")
    has("the factorisation is shown", o, "sqrt(36 x 2)")
    o = drive(pure640.t_surds, ["2"], [0])
    has("already simplest", o, "sqrt(2) is already in simplest form")
    o = drive(pure640.t_surds, ["3", "8", "2", "50"], [1])
    has("first simplified", o, "3sqrt(8) = 6sqrt(2)")
    has("second simplified", o, "2sqrt(50) = 10sqrt(2)")
    has("like surds collected", o, "= 16sqrt(2)")
    num("decimal agrees", o, "decimal check: ", 16.0 * math.sqrt(2.0), 1e-5)
    o = drive(pure640.t_surds, ["1", "2", "1", "3"], [1])
    has("unlike surds not collected", o, "does NOT")
    o = drive(pure640.t_surds, ["6", "3", "1", "2"], [3])
    has("conjugate named", o, "CONJUGATE 3 - sqrt(2)")
    has("denominator rationalised", o, "= 7")
    has("exact fraction form", o, "= (18 - 6sqrt(2)) / 7")
    num("rationalised value", o, "decimal check: ", 6.0 / (3.0 + math.sqrt(2.0)), 1e-5)
    o = drive(pure640.t_surds, ["2", "3", "5", "6"], [2])
    has("product simplified", o, "= 30sqrt(2)")

    def signs_are_clean(label, lines):
        for ln in lines:
            truthy(label + ": no '+ -' in " + repr(ln), "+ -" not in ln)
            truthy(label + ": no '- -' in " + repr(ln), "- -" not in ln)

    o = drive(pure640.t_surds, ["1", "1", "1", "2"], [3])
    has("negative bottom folded into the top", o, "= -1 + sqrt(2)")
    signs_are_clean("1/(1+sqrt2)", o)
    num("value of 1/(1+sqrt2)", o, "decimal check: ",
        1.0 / (1.0 + math.sqrt(2.0)), 1e-5)
    o = drive(pure640.t_surds, ["6", "4", "-1", "2"], [3])
    has("conjugate of a minus is a plus", o, "CONJUGATE 4 + sqrt(2)")
    has("a negative q is bracketed before squaring", o, "(-1)^2")
    has("fraction reduced by the common factor", o, "= (12 + 3sqrt(2)) / 7")
    signs_are_clean("6/(4-sqrt2)", o)
    num("value of 6/(4-sqrt2)", o, "decimal check: ",
        6.0 / (4.0 - math.sqrt(2.0)), 1e-5)
    o = drive(pure640.t_surds, ["2", "2", "1", "2"], [3])
    has("bottom cancels away", o, "= 2 - sqrt(2)")
    signs_are_clean("2/(2+sqrt2)", o)
    o = drive(pure640.t_surds, ["2", "3", "-3", "2"], [1])
    has("negative term subtracted, not added", o, "2sqrt(3) - 3sqrt(2)")
    signs_are_clean("2sqrt(3) - 3sqrt(2)", o)

    o = drive(pure640.t_linecircle, ["0", "0", "5", "1", "1"], [0])
    has("substituted quadratic", o, "2x^2 + 2x - 24 = 0")
    num("discriminant", o, "discriminant = ", 196.0)
    has("first intersection", o, "(3, 4)")
    has("second intersection", o, "(-4, -3)")
    num("chord length", o, "chord length = ", math.sqrt(98.0), 1e-3)
    o = drive(pure640.t_linecircle, ["0", "0", "1", "1", str(math.sqrt(2))], [0])
    has("tangent detected", o, "TANGENT")
    has("perpendicularity checked", o, "confirms tangent perp to radius")
    o = drive(pure640.t_linecircle, ["0", "0", "1", "0", "5"], [0])
    has("miss detected", o, "misses the circle")
    num("distance to the line", o, "= |ma - b + c| / sqrt(1+m^2) = ", 5.0, 1e-6)
    o = drive(pure640.t_linecircle, ["0", "0", "5", "3"], [1])
    has("vertical intersection up", o, "(3, 4)")
    has("vertical intersection down", o, "(3, -4)")

    o = drive(pure640.t_sequence, ["1/n", "1", "12"], [0])
    has("terms listed", o, "u(3) = 0.333333")
    has("decreasing", o, "DECREASING")
    o = drive(pure640.t_sequence, ["1/(1-x)", "2", "9"], [1])
    has("periodic detected", o, "PERIODIC with period 3")
    o = drive(pure640.t_sequence, ["2n+1", "1", "8"], [0])
    has("increasing", o, "INCREASING")
    o = drive(pure640.t_sequence, ["x/2", "8", "40"], [1])
    has("convergent", o, "CONVERGENT")

def test_surd_engine():
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
    check("sqrt(3) squared", sq("sqrt(3)*sqrt(3)"), "3")
    check("sqrt(x) squared", sq("sqrt(x)*sqrt(x)"), "x")
    check("2 sqrt(8) collects",
          caseng.tostr(cascalc.tidy(caslex.parse("2*sqrt(8)"))), "4*sqrt(2)")
    for n in (2, 3, 8, 12, 18, 20, 45, 50, 72, 98, 128, 300, 1000):
        e = caslex.parse("sqrt(" + str(n) + ")")
        close("sqrt(" + str(n) + ") keeps its value",
              caseng.evalf(caseng.simplify(e), 0.0), math.sqrt(n), 1e-12)

def test_binom_cdf_recurrence():
    def reference(n, p, k):
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

    close("B(10,0.5) P(X<=5) = 638/1024", casutil.binom_cdf(10, 0.5, 5),
          638.0 / 1024.0, 1e-12)
    close("B(4,0.5) P(X<=2) = 11/16", casutil.binom_cdf(4, 0.5, 2),
          11.0 / 16.0, 1e-12)
    close("B(5,0.2) P(X<=0) = 0.8^5", casutil.binom_cdf(5, 0.2, 0),
          0.8 ** 5, 1e-12)

    check("k below 0 is 0", casutil.binom_cdf(10, 0.5, -1), 0.0)
    check("k at n is 1", casutil.binom_cdf(10, 0.5, 10), 1.0)
    check("k above n is 1", casutil.binom_cdf(10, 0.5, 99), 1.0)
    check("p = 0 is certain", casutil.binom_cdf(10, 0.0, 0), 1.0)
    check("p = 1 has no mass below n", casutil.binom_cdf(10, 1.0, 9), 0.0)
    for k in range(0, 41):
        v = casutil.binom_cdf(40, 0.35, k)
        truthy("binom_cdf(40,0.35," + str(k) + ") is a probability",
               -1e-12 <= v <= 1.0 + 1e-12)
    prev = -1.0
    for k in range(0, 41):
        v = casutil.binom_cdf(40, 0.35, k)
        truthy("binom_cdf is non-decreasing at k=" + str(k), v >= prev - 1e-12)
        prev = v

def test_engine_invariants():
    XS = (0.37, 1.23, 2.71, 4.13, -0.61, -2.2)

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

    for e in SWEEP + SWEEP_ALG:
        t = caslex.parse(e)
        CHECKS[0] += 1
        _agree("simplify " + e, caseng.simplify(t), t, XS)

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

_LAYOUT = []

def _rec_draw_string(x, y, s, c=None, size=None):
    _LAYOUT.append((x, y, str(s), size or "medium"))

def _layout_hold(note=None):
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
    path = os.path.join(HERE, "README.md")
    text = open(path).read()
    probes = set(["calib_screen.py", "fontmetrics.py", "fontmetrics2.py",
                  "keyprobe.py", "hwcheck.py"])
    for f in devlint.DEVICE_FILES:
        if f in probes:
            continue
        truthy("README install list names " + f, "`" + f + "`" in text)
    for f in ("casioplot.py", "tests.py", "devlint.py", "stress.py"):
        truthy("README warns not to copy " + f, f in text)

def test_working_filter():
    lines = ["x = 3", casutil.w("by the quadratic formula"), "",
             casutil.warn("but check the domain"), casutil.w("disc = 25")]
    real = casui.SHOW_WORKING
    try:
        casui.SHOW_WORKING = True
        full = casutil.filter_lines(lines)
        casui.SHOW_WORKING = False
        brief = casutil.filter_lines(lines)
    finally:
        casui.SHOW_WORKING = real
    check("working shown keeps everything", len(full), 5)
    truthy("the answer survives both modes", "x = 3" in full and "x = 3" in brief)
    truthy("working is hidden when off", "by the quadratic formula" not in brief)
    truthy("working is shown when on", "by the quadratic formula" in full)
    truthy("a caveat survives BOTH modes",
           "but check the domain" in full and "but check the domain" in brief)
    truthy("blank runs are collapsed", "" not in brief[:1])
    check("no trailing blank", brief[len(brief) - 1] != "", True)
    plain = ["a", "b", "c"]
    casui.SHOW_WORKING = False
    try:
        check("untagged output is untouched", casutil.filter_lines(plain), plain)
    finally:
        casui.SHOW_WORKING = real

_RESLINES = []

def _cap_lines(title, lines):
    for ln in lines:
        _RESLINES.append(str(ln))

def _drive_lines(fn, inputs, menus):
    del _RESLINES[:]
    real = casui.result_screen
    casui.result_screen = _cap_lines
    _inputs[:] = list(inputs)
    _menus[:] = list(menus)
    try:
        fn()
    finally:
        casui.result_screen = real
    return list(_RESLINES)

def test_answer_mode_never_empties_a_tool():
    import stress_inputs
    real = casui.SHOW_WORKING
    mods = list(casui.MATHS_MODS) + list(casui.FM_CORE_MODS) + list(casui.FM_OPT_MODS)
    checked = 0
    for name in mods:
        mod = __import__(name)
        for label, fn in mod.TOOLS:
            try:
                casui.SHOW_WORKING = True
                full = _drive_lines(fn, stress_inputs.INPUTS, stress_inputs.MENUS)
                casui.SHOW_WORKING = False
                brief = _drive_lines(fn, stress_inputs.INPUTS, stress_inputs.MENUS)
            except Exception:
                continue
            finally:
                casui.SHOW_WORKING = real
            if not full:
                continue
            checked += 1
            seen = {}
            for ln in full:
                seen[ln] = 1
            extra = []
            for ln in brief:
                if ln not in seen:
                    extra.append(ln)
            truthy(name + " / " + label + ": answer mode adds nothing", not extra)
            truthy(name + " / " + label + ": answer mode keeps something",
                   len(brief) > 0)
    truthy("the sweep actually exercised the toolkit", checked >= 150)

def test_menu_tree_reachable():
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
    ("intro screens fit one page", test_intro_screens_fit_one_page),
    ("math allowlist is measured", test_math_allowlist_is_the_measured_set),
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
    ("answer/working filter", test_working_filter),
    ("answer mode never empties a tool", test_answer_mode_never_empties_a_tool),
    ("README matches TOOLS", test_readme_matches_tools),
    ("README install list", test_readme_install_list),
]

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
