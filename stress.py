# stress.py - non-interactive smoke test for the Maths Toolkit.
# Stubs the UI (canned input, no-op drawing, auto-exit menus) then imports every
# section and calls EVERY tool in its TOOLS registry, plus hammers the engine.
# Each call is wrapped so errors are logged, never fatal. Progress is flushed to
# a log file when possible (PC), else printed (device).
#
# This proves nothing crashes. It does NOT check that any answer is right -
# tests.py does that. Run both.

import casui

INPUTS = ["3", "4", "2", "5 6 7 8", "1", "0.5", "2", "sin(x)", "3",
          "2 3 4", "6", "4", "1", "x^2", "9"]
_ic = [0]

def _stub_input(prompt):
    _ic[0] += 1
    if _ic[0] <= 18:
        return INPUTS[(_ic[0] - 1) % len(INPUTS)]
    if _ic[0] <= 22:
        return None
    raise Exception("stress: input exhausted (unbounded input loop?)")

def _noop(*a, **k):
    return None

def _stub_menu(*a, **k):
    return -1

def _stub_hold_page(*a, **k):
    return True  # "EXIT" - stop paging immediately

casui.input_expr = _stub_input
casui.menu = _stub_menu
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
casui.show_text = _noop
casui.show_math = _noop
casui.result_screen = _noop
casui.hold = _noop
casui.hold_page = _stub_hold_page

import caslex
import caseng
import cascalc

LOGF = None
try:
    LOGF = open("stress_log.txt", "w")
except:
    LOGF = None

def out(s):
    if LOGF is not None:
        LOGF.write(s + "\n")
        LOGF.flush()
    else:
        print(s)

def prog(s):
    # progress: written to the log file on PC, silent on the device (no file)
    if LOGF is not None:
        LOGF.write(s + "\n")
        LOGF.flush()

ERRORS = []
COUNT = [0]

def _try(label, fn):
    COUNT[0] += 1
    try:
        fn()
    except Exception as e:
        ERRORS.append(label + " -> " + repr(e))

EXPRS = ["x^2+3x", "sin(x)", "1/(x+1)", "exp(x)", "sqrt(x)", "ln(x)",
         "x^3-x", "(x+1)(x-1)", "cos(x^2)", "tan(x)", "2x^2-4x+1",
         "x/(x-2)", "3", "sin(x)+cos(x)", "x^4-5x^2+4",
         "atan(x)", "abs(x-3)", "sinh(x)", "tanh(x)", "5!+x",
         "nCr(6,2)+x", "nPr(5,2)-x", "logb(2,x+4)", "atan(x)*180/pi",
         "2^-x", "x^-1", "1e3*x", "sqrt(2x+1)", "1/(2x+1)", "x^(2/3)"]

def _engine():
    for ex in EXPRS:
        prog("engine: " + ex)
        tr = None
        try:
            tr = caslex.parse(ex)
        except Exception as e:
            ERRORS.append("parse " + ex + " -> " + repr(e))
            continue
        if tr is None:
            ERRORS.append("parse None: " + ex)
            continue
        _try("evalf " + ex, lambda tr=tr: caseng.evalf(tr, 1.5))
        _try("diff " + ex, lambda tr=tr: caseng.tostr(caseng.simplify(caseng.diff(tr, 'x'))))
        _try("simplify " + ex, lambda tr=tr: caseng.tostr(caseng.simplify(tr)))
        _try("integ " + ex, lambda tr=tr: cascalc.integ(tr))
        _try("solve " + ex, lambda tr=tr: cascalc.solve(tr))
        _try("render " + ex, lambda tr=tr: _render(tr))

def _render(tr):
    import casrender
    casrender.render(tr, 0, 0, 384, 120, (0, 0, 0))

MODNAMES = ["vcplx", "matrix", "vectors", "polyroots", "series", "hyper",
            "polar", "diffeq", "fmmech", "fmstat", "numeric", "algos",
            "xpure", "fpt", "pure640", "purecalc", "stat640", "mech640",
            "proof"]

def _sections():
    # Drive the TOOLS registry, not a "t_" name prefix. The old prefix scan
    # silently tested 0 of mech640's 11 tools and 0 of algos' 8, because those
    # two modules never used the prefix.
    for mn in MODNAMES:
        prog("import: " + mn)
        mod = None
        try:
            mod = __import__(mn)
        except Exception as e:
            ERRORS.append("IMPORT " + mn + " -> " + repr(e))
            continue
        tools = getattr(mod, "TOOLS", None)
        if not tools:
            ERRORS.append("NO TOOLS REGISTRY: " + mn)
            continue
        for entry in tools:
            label = entry[0]
            fn = entry[1]
            if not callable(fn):
                ERRORS.append("not callable: " + mn + "." + str(label))
                continue
            prog("  tool: " + mn + " / " + label)
            _ic[0] = 0
            _try(mn + " / " + label, fn)

out("STRESS TEST START")
_ic[0] = 0
_engine()
_sections()
out("checks run: " + str(COUNT[0]))
out("errors: " + str(len(ERRORS)))
out("--------------------")
i = 0
while i < len(ERRORS):
    out(ERRORS[i])
    i += 1
out("--------------------")
out("STRESS TEST DONE")
if LOGF is not None:
    LOGF.close()
print("stress: " + str(COUNT[0]) + " checks, " + str(len(ERRORS)) + " errors")
