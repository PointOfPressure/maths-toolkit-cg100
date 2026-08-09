# tests_fpt2.py - correctness tests for the Y436 (Further Pure with Technology)
# tools added to fpt.py: tangent fields, limits, asymptotes, stationary points
# and cusps, families of curves, envelopes, verifying a solution of a
# differential equation, and linear Diophantine equations.
#
# Every check below is against a value worked out by hand and written in a
# comment next to it. Nothing here asserts "it did not crash".
#
# Picked up automatically by tests.py through SECTIONS at the bottom; the
# harness `h` carries check / close / truthy / raises / drive / has / num plus
# the engine modules.
import math


# ------------------------------------------------------------- capture ----
def _drawn(h, fn, inputs, menus=()):
    # Run a tool with casui.draw_string and casui.set_pixel recorded, so a
    # drawing tool can be asserted on what it actually put on the screen.
    # tests.py replaces both with no-ops, so they are wrapped and put back.
    casui = h.casui
    strings = []
    pixels = []

    def rec_string(x, y, s, colour=None, size="medium"):
        strings.append((x, y, s, size))

    def rec_pixel(x, y, colour=None):
        pixels.append((x, y, colour))

    old_s = casui.draw_string
    old_p = casui.set_pixel
    casui.draw_string = rec_string
    casui.set_pixel = rec_pixel
    try:
        out = h.drive(fn, inputs, menus)
    finally:
        casui.draw_string = old_s
        casui.set_pixel = old_p
    return out, strings, pixels


def _line_with(lines, needle):
    for ln in lines:
        if needle in ln:
            return ln
    return None


# =========================================================== tangent field ==
def test_tangent_field(h):
    import fpt
    casutil = h.casutil

    # --- the dash geometry, which is the whole point of a tangent field ---
    # casutil.frame's default pixel box is 352 across by 142 down, so a data
    # gradient of 1 is NOT 45 degrees on screen: the dash has to slant the way
    # the curve itself would be drawn on those same axes, which is m*sy/sx,
    # while its LENGTH stays fixed in pixels whatever the gradient.
    fr = casutil.frame(-3.0, 3.0, -3.0, 3.0)
    sx, sy = fpt._scale(fr)
    h.truthy("the default frame really is not square in pixels",
             abs(sx - sy) > 1.0)

    def dash(frame, m, length=9.0):
        e = fpt._fseg(frame, 0.0, 1.0, m, length)
        ax, ay = fpt._scale(frame)
        dxp = (e[2] - e[0]) * ax          # pixel run
        dyp = -(e[3] - e[1]) * ay         # pixel rise, screen y downwards
        return e, dxp, dyp

    # dy/dx = y has gradient exactly 1 at (0, 1)
    tree = h.caslex.parse("y")
    h.close("field slope of dy/dx=y at (0,1)", fpt._slope(tree, 0.0, 1.0), 1.0)

    # on a frame whose pixel box IS square (142 x 142) over a square data
    # window, gradient 1 must come out at exactly 45 degrees on screen
    sq = casutil.frame(-3.0, 3.0, -3.0, 3.0, 26, 16, 168, 158)
    qx, qy = fpt._scale(sq)
    h.close("the square test frame is square in pixels", qx, qy, 1e-9)
    e, dxp, dyp = dash(sq, 1.0)
    h.close("gradient 1 dash is 45 degrees on a square frame", dxp, -dyp, 1e-9)
    h.close("and is 9 px long", math.sqrt(dxp * dxp + dyp * dyp), 9.0, 1e-9)

    e, dxp, dyp = dash(fr, 1.0)
    h.close("gradient 1 dash is 9 px long on the default frame",
            math.sqrt(dxp * dxp + dyp * dyp), 9.0, 1e-9)
    h.close("dash is centred on its grid point in x", (e[0] + e[2]) / 2.0,
            0.0, 1e-12)
    h.close("dash is centred on its grid point in y", (e[1] + e[3]) / 2.0,
            1.0, 1e-12)

    # same length whatever the gradient - that is what makes the field readable
    for m in (0.0, 0.5, 1.0, -2.0, 7.0, -100.0, 1e6):
        e, dxp, dyp = dash(fr, m)
        h.close("dash of gradient " + str(m) + " is still 9 px",
                math.sqrt(dxp * dxp + dyp * dyp), 9.0, 1e-9)
        # and it still slants the right way: screen rise / run = m * sy / sx
        h.close("dash of gradient " + str(m) + " has the right screen slant",
                -dyp / dxp, m * sy / sx, 1e-6 * (1.0 + abs(m) * sy / sx))
    # a dash of gradient 0 is exactly horizontal, and 9 px of pure run
    e0, dx0, dy0 = dash(fr, 0.0)
    h.close("gradient 0 dash is horizontal", dy0, 0.0, 1e-9)
    h.close("gradient 0 dash is all run", dx0, 9.0, 1e-9)

    # --- the tool itself -------------------------------------------------
    # dy/dx = y through (0, 1) is y = e^x exactly, so y(1) = e = 2.718281828
    # and y(-1) = 1/e = 0.367879441.
    out, strings, pixels = _drawn(
        h, fpt.t_tangentfield, ["y", "-1", "1", "-3", "3", "0", "1"])
    h.has("drew a field", out, "tangent field")
    h.num("RK4 forwards reaches e at x=1", out, "y(1) = ", 2.718281828, 1e-5)
    h.num("RK4 backwards reaches 1/e at x=-1", out, "y(-1) = ",
          0.367879441, 1e-5)
    # dy/dx = y is finite at every one of the 15 x 11 cell centres
    h.has("every grid cell got a dash", out, "dashes: 165")
    h.truthy("the field put pixels on the screen", len(pixels) > 500)
    # the solution curves are drawn in red, the dashes in the accent colour
    reds = 0
    accs = 0
    for px in pixels:
        if px[2] == h.casui.RED:
            reds += 1
        elif px[2] == h.casui.ACC:
            accs += 1
    h.truthy("dashes are drawn in the accent colour", accs > 300)
    h.truthy("solution curves are drawn in red", reds > 50)

    # x^2 + y^2 = 4 solves dy/dx = -x/y, so through (0, 2) the curve is that
    # circle and y(1) = y(-1) = sqrt(3) = 1.7320508.
    o = h.drive(fpt.t_tangentfield, ["-x/y", "-1", "1", "-3", "3", "0", "2"])
    h.num("circle field forwards to sqrt(3)", o, "y(1) = ", 1.7320508, 1e-5)
    h.num("circle field backwards to sqrt(3)", o, "y(-1) = ", 1.7320508, 1e-5)
    # the cell centres at y = 0 (one whole row of 15) have no gradient there,
    # so 165 - 15 = 150 dashes can be drawn
    h.has("the undefined row is skipped, not faked", o, "dashes: 150")

    # logistic: dy/dx = y(1-y) through (0, 0.5) is y = 1/(1+e^-x), so
    # y(2) = 0.880797078 and y(-2) = 0.119202922.
    o = h.drive(fpt.t_tangentfield,
                ["y*(1-y)", "-2", "2", "-0.5", "1.5", "0", "0.5"])
    h.num("logistic field forwards", o, "y(2) = ", 0.880797078, 1e-5)
    h.num("logistic field backwards", o, "y(-2) = ", 0.119202922, 1e-5)

    # no solution curve asked for: the field is still drawn
    o = h.drive(fpt.t_tangentfield, ["x*y", "-3", "3", "-3", "3"])
    h.has("field alone is allowed", o, "no solution curve")
    # a reversed window is refused rather than drawn inside out
    o = h.drive(fpt.t_tangentfield, ["y", "3", "-3"])
    h.has("reversed x window refused", o, "Need x max > x min.")
    o = h.drive(fpt.t_tangentfield, ["y", "-3", "3", "3", "-3"])
    h.has("reversed y window refused", o, "Need y max > y min.")

    # --- layout: nothing off the screen, nothing overprinted -------------
    for x, y, s, size in strings:
        w = h.casui.text_w(s, size)
        h.truthy("tangent field: " + repr(s[:24]) + " fits 384px", x + w <= 384)
        h.truthy("tangent field: " + repr(s[:24]) + " is on screen",
                 0 <= y <= 191)
    bad = None
    i = 0
    while i < len(strings):
        j = i + 1
        while j < len(strings):
            xa, ya, sa, za = strings[i]
            xb, yb, sb, zb = strings[j]
            j += 1
            if abs(ya - yb) > 6:
                continue
            if xa < xb + h.casui.text_w(sb, zb) and \
                    xb < xa + h.casui.text_w(sa, za):
                bad = repr(sa[:20]) + " overprints " + repr(sb[:20])
        i += 1
    h.truthy("tangent field screen has no overprinting: " + str(bad),
             bad is None)


# ==================================================================== C10 ==
def test_limits(h):
    import fpt
    # lim sin(x)/x as x -> 0 is 1 (the standard small-angle limit)
    o = h.drive(fpt.t_limit, ["sin(x)/x", "0"], [0])
    h.has("sin(x)/x -> 1 from below", o, "from below: 1")
    h.has("sin(x)/x -> 1 from above", o, "from above: 1")
    h.num("lim sin(x)/x at 0", o, "limit = ", 1.0, 1e-6)
    h.has("and 0 is a hole, not a value", o, "hole in the curve")

    # lim (1 - cos x)/x^2 as x -> 0 is 1/2
    o = h.drive(fpt.t_limit, ["(1-cos(x))/x^2", "0"], [0])
    h.num("lim (1-cos x)/x^2 at 0", o, "limit = ", 0.5, 1e-4)

    # (x^2-1)/(x-1) = x+1 away from x = 1, so the limit is 2 and there is a
    # removable discontinuity there
    o = h.drive(fpt.t_limit, ["(x^2-1)/(x-1)", "1"], [0])
    h.num("lim (x^2-1)/(x-1) at 1", o, "limit = ", 2.0, 1e-4)

    # |x|/x is -1 below 0 and +1 above it, so there is no limit at 0
    o = h.drive(fpt.t_limit, ["abs(x)/x", "0"], [0])
    h.has("|x|/x from below is -1", o, "from below: -1")
    h.has("|x|/x from above is 1", o, "from above: 1")
    h.has("|x|/x has no limit at 0", o, "limit does not exist")

    # 1/x^2 -> +infinity from both sides, which is a vertical asymptote
    o = h.drive(fpt.t_limit, ["1/x^2", "0"], [0])
    h.has("1/x^2 diverges at 0", o, "limit = +infinity")
    h.has("and that is a vertical asymptote", o, "vertical")

    # (2x+1)/(x-3) -> 2 at both ends: divide through by x
    o = h.drive(fpt.t_limit, ["(2x+1)/(x-3)"], [1])
    h.num("lim (2x+1)/(x-3) at +inf", o, "limit = ", 2.0, 1e-5)
    h.has("so y = 2 is horizontal", o, "horizontal")
    o = h.drive(fpt.t_limit, ["(2x+1)/(x-3)"], [2])
    h.num("lim (2x+1)/(x-3) at -inf", o, "limit = ", 2.0, 1e-5)

    # (3x^2+1)/(x^2-5) -> 3 at +infinity (ratio of leading coefficients)
    o = h.drive(fpt.t_limit, ["(3x^2+1)/(x^2-5)"], [1])
    h.num("lim (3x^2+1)/(x^2-5) at +inf", o, "limit = ", 3.0, 1e-5)

    # x^3 has no limit at +infinity
    o = h.drive(fpt.t_limit, ["x^3"], [1])
    h.has("x^3 diverges at +infinity", o, "limit = +infinity")

    # cancelling on EXIT must not print a half-computed answer
    o = h.drive(fpt.t_limit, ["sin(x)"], [-1])
    h.check("cancelling the limit menu prints nothing", o, [])


# ==================================================================== C11 ==
def test_asymptotes(h):
    import fpt
    # y = (x^2+1)/x = x + 1/x: vertical x = 0, oblique y = x. The oblique one
    # is the quotient of the long division, which caspoly.pdivmod gives
    # exactly: x^2+1 = x.x + 1.
    o = h.drive(fpt.t_asympt, ["(x^2+1)/x"])
    h.has("(x^2+1)/x has a vertical asymptote at 0", o, "vertical: x = 0")
    h.has("(x^2+1)/x falls to -inf below 0", o, "from below f -> -infinity")
    h.has("(x^2+1)/x rises to +inf above 0", o, "from above f -> +infinity")
    h.has("(x^2+1)/x has the oblique asymptote y = x", o, "oblique: y = x")
    h.has("the oblique asymptote is exact", o, "(exact)")
    h.has("with remainder 1", o, "r = 1")

    # the same curve written out as x + 1/x: no top-level quotient, so the
    # numeric route has to find y = x on its own
    o = h.drive(fpt.t_asympt, ["x+1/x"])
    h.has("x+1/x has a vertical asymptote at 0", o, "vertical: x = 0")
    h.has("x+1/x has oblique y = x at +inf", o, "oblique as x->+inf: y = x")
    h.has("x+1/x has oblique y = x at -inf", o, "oblique as x->-inf: y = x")
    h.num("gradient of the oblique asymptote", o, "m = lim f(x)/x = ", 1.0, 1e-5)
    h.num("intercept of the oblique asymptote", o, "c = lim f(x) - mx = ",
          0.0, 1e-5)

    # y = (2x+1)/(x-3): vertical x = 3, horizontal y = 2 (leading coefficients)
    o = h.drive(fpt.t_asympt, ["(2x+1)/(x-3)"])
    h.has("(2x+1)/(x-3) has a vertical asymptote at 3", o, "vertical: x = 3")
    h.has("(2x+1)/(x-3) has horizontal y = 2", o, "horizontal: y = 2")
    h.has("and that is exact", o, "(exact)")

    # deg(num) < deg(den) so f -> 0
    o = h.drive(fpt.t_asympt, ["1/(x-3)"])
    h.has("1/(x-3) has horizontal y = 0", o, "horizontal: y = 0")
    h.has("1/(x-3) has a vertical asymptote at 3", o, "vertical: x = 3")

    # sqrt(x^2+1) is not rational: y = x at +infinity and y = -x at -infinity,
    # since sqrt(x^2+1) - |x| -> 0.
    o = h.drive(fpt.t_asympt, ["sqrt(x^2+1)"])
    h.has("sqrt(x^2+1) has no vertical asymptote", o, "no vertical asymptote")
    h.has("sqrt(x^2+1) has oblique y = x at +inf", o,
          "oblique as x->+inf: y = x")
    h.has("sqrt(x^2+1) has oblique y = -x at -inf", o,
          "oblique as x->-inf: y = -x")

    # deg(num) - deg(den) = 2, so no straight-line asymptote at all
    o = h.drive(fpt.t_asympt, ["(x^3+1)/(x-1)"])
    h.has("(x^3+1)/(x-1) is degree 2 over", o, "deg(num) - deg(den) = 2")
    h.has("so no horizontal or oblique asymptote", o, "no horizontal or")
    h.has("(x^3+1)/(x-1) has a vertical asymptote at 1", o, "vertical: x = 1")

    # a polynomial has no asymptotes of any kind
    o = h.drive(fpt.t_asympt, ["x^2-4"])
    h.has("x^2-4 has no vertical asymptote", o, "no vertical asymptote")
    h.has("x^2-4 has no asymptote at +inf", o, "no asymptote as x->+inf")

    # tan x has vertical asymptotes at odd multiples of pi/2; pi/2 = 1.5708
    o = h.drive(fpt.t_asympt, ["tan(x)"])
    h.has("tan has a vertical asymptote at pi/2", o, "vertical: x = 1.5708")
    h.has("tan has one at -pi/2 too", o, "vertical: x = -1.5708")
    # 3pi/2 = 4.712389
    h.has("tan has one at 3pi/2", o, "vertical: x = 4.7124")

    # exp(-x) -> 0 at +infinity: a horizontal asymptote found numerically
    o = h.drive(fpt.t_asympt, ["exp(-x)"])
    h.num("exp(-x) -> 0 at +infinity", o, "horizontal as x->+inf: y = ",
          0.0, 1e-6)


# ==================================================================== C12 ==
def test_stationary_and_cusps(h):
    import fpt
    # y = x^3 - 3x: f' = 3x^2-3 = 0 at x = -1 and x = 1. f'' = 6x, so x = -1
    # is a maximum with y = -1+3 = 2 and x = 1 a minimum with y = 1-3 = -2.
    o = h.drive(fpt.t_statcusp, ["x^3-3x"])
    h.has("x^3-3x has a maximum at (-1, 2)", o, "x = -1  y = 2  MAXIMUM")
    h.has("x^3-3x has a minimum at (1, -2)", o, "x = 1  y = -2  MINIMUM")
    h.has("f'' = -6 is quoted at the maximum", o, "f'' = -6")
    h.has("f'' = 6 is quoted at the minimum", o, "f'' = 6")
    h.has("but f'' is only supporting evidence", o, "supporting only")
    h.has("x^3-3x has no cusp", o, "no cusp")

    # y = x^4: f' = 4x^3 = 0 at x = 0 only, f'' = 0 there too, so the sign of
    # f' either side decides it - it is a minimum.
    o = h.drive(fpt.t_statcusp, ["x^4"])
    h.has("x^4 has a minimum at the origin", o, "x = 0  y = 0  MINIMUM")

    # y = x^3: f' = 3x^2 = 0 at x = 0, f'' = 0, and f' does not change sign,
    # so it is a stationary point of inflection. cascalc.solve locates that
    # root to about 5e-8, where f'' = 6x is a small NEGATIVE number, so a
    # classification taken from the sign of f'' would say MAXIMUM here.
    o = h.drive(fpt.t_statcusp, ["x^3"])
    h.has("x^3 has a point of inflection at the origin", o,
          "x = 0  y = 0  INFLECTION")
    h.has("even though f'' rounds to 0 there", o, "f'' = 0")

    # y = (x^2-1)^2: f' = 4x(x^2-1) = 0 at x = -1, 0, 1. Minima of 0 at
    # x = +-1 (f'' = 8) and a maximum of 1 at x = 0 (f'' = -4). The three
    # roots are close enough that the step either side must not reach the
    # next one.
    o = h.drive(fpt.t_statcusp, ["(x^2-1)^2"])
    h.has("(x^2-1)^2 has a minimum at (-1, 0)", o, "x = -1  y = 0  MINIMUM")
    h.has("(x^2-1)^2 has a maximum at (0, 1)", o, "x = 0  y = 1  MAXIMUM")
    h.has("(x^2-1)^2 has a minimum at (1, 0)", o, "x = 1  y = 0  MINIMUM")

    # y = (x^2)^(1/3) = x^(2/3). f' = (2/3)x^(-1/3), which tends to -infinity
    # as x -> 0 from below and +infinity from above while y stays at 0: a cusp.
    o = h.drive(fpt.t_statcusp, ["(x^2)^(1/3)"])
    h.has("x^(2/3) has a cusp at the origin", o, "CUSP at x = 0, y = 0")
    h.has("its gradient runs to -infinity from below", o,
          "f' from below -> -infinity")
    h.has("its gradient runs to +infinity from above", o,
          "f' from above -> +infinity")

    # y = |x-2| + 1 has a corner, not a cusp: the gradient is -1 then +1, both
    # finite, and the vertex is at (2, 1).
    o = h.drive(fpt.t_statcusp, ["abs(x-2)+1"])
    h.has("|x-2|+1 has a corner at (2, 1)", o, "CORNER at x = 2, y = 1")
    h.has("gradient -1 to the left", o, "f' from below -> -1")
    h.has("gradient +1 to the right", o, "f' from above -> 1")

    # 1/x has an infinite gradient at 0 but the curve does not carry on
    # through it, so it is an asymptote and must NOT be called a cusp
    o = h.drive(fpt.t_statcusp, ["1/x"])
    h.has("a pole is not a cusp", o, "no cusp")
    h.has("and 1/x has no stationary point", o, "no stationary point")

    # 1/x^2 is the harder version of the same thing: f' = -2/x^3 really does
    # run to +infinity on one side and -infinity on the other, and f takes the
    # same enormous value at -1e-6 and +1e-6, so it looks continuous. It is a
    # pole, so it is still not a cusp.
    o = h.drive(fpt.t_statcusp, ["1/x^2"])
    h.has("a double pole is not a cusp either", o, "no cusp")

    # tan x: gradient 1+tan^2 blows up at pi/2 but so does the curve
    o = h.drive(fpt.t_statcusp, ["tan(x)"])
    h.has("tan has no cusp either", o, "no cusp")


# ===================================================================== C4 ==
def test_family(h):
    import fpt
    # y = x^2 + a on -3 <= x <= 3. For a = -4 the roots are x = -2 and x = 2,
    # the least value is -4 at x = 0 and the greatest is 9-4 = 5 at x = +-3.
    o = h.drive(fpt.t_family, ["x^2+a", "-3", "3", "-4 -1 0"])
    h.has("a=-4 has roots -2 and 2", o, "a=-4 roots: -2, 2")
    h.has("a=-4 spans -4 to 5", o, "a=-4 y in [-4, 5]")
    h.has("a=-1 has roots -1 and 1", o, "a=-1 roots: -1, 1")
    h.has("a=-1 spans -1 to 8", o, "a=-1 y in [-1, 8]")
    h.has("a=0 has the repeated root 0", o, "a=0 roots: 0")
    h.has("three members drawn", o, "members drawn: 3")

    # y = a/x: no member crosses the axis, and every one has a pole at 0
    o = h.drive(fpt.t_family, ["a/x", "1", "4", "1 2"])
    h.has("a/x never meets y=0 on [1,4]", o, "a=1 roots: none in range")
    # a=2 runs from 2/4 = 0.5 to 2/1 = 2
    h.has("a=2 spans 0.5 to 2", o, "a=2 y in [0.5, 2]")

    # bad input is refused
    o = h.drive(fpt.t_family, ["x^2+a", "3", "-3"])
    h.has("reversed x window refused", o, "Need x max > x min.")
    o = h.drive(fpt.t_family, ["x^2+a", "-3", "3", ""])
    h.has("an empty list of a is refused", o, "at least one value of a")


# ===================================================================== C9 ==
def test_envelope(h):
    import fpt
    # The family y = 2ax - a^2 is the set of tangents to y = x^2: df/da =
    # 2x - 2a = 0 gives a = x, and then y = 2x.x - x^2 = x^2. So the envelope
    # is exactly y = x^2 and at x = k the touching member is a = k, y = k^2.
    o = h.drive(fpt.t_envelope, ["2*a*x-a^2", "-2", "2", "-3", "3"])
    h.has("envelope of the tangents to y=x^2 at x=-2", o, "x=-2 a=-2 y=4")
    h.has("envelope at x=-1", o, "x=-1 a=-1 y=1")
    h.has("envelope at x=0", o, "x=0 a=0 y=0")
    h.has("envelope at x=1", o, "x=1 a=1 y=1")
    h.has("envelope at x=2", o, "x=2 a=2 y=4")
    h.has("df/da is reported", o, "df/da")

    # y = ax + 1/a: df/da = x - 1/a^2 = 0 gives a = 1/sqrt(x), and then
    # y = sqrt(x) + sqrt(x) = 2 sqrt(x). At x = 4, a = 0.5 and y = 4;
    # at x = 0.25, a = 2 and y = 1; at x = 2.125, y = 2 sqrt(2.125) = 2.9155.
    o = h.drive(fpt.t_envelope, ["a*x+1/a", "0.25", "4", "0.1", "3"])
    h.has("envelope y=2sqrt(x) at x=0.25", o, "x=0.25 a=2 y=1")
    h.has("envelope y=2sqrt(x) at x=4", o, "x=4 a=0.5 y=4")
    h.num("envelope y=2sqrt(x) at x=2.125", o, "x=2.125 a=0.686 y=", 2.9155,
          1e-3)

    # y = x + a is a family of parallel lines: df/da = 1 is never zero, so
    # there is no envelope at all.
    o = h.drive(fpt.t_envelope, ["x+a", "-2", "2", "-3", "3"])
    h.has("parallel lines have no envelope", o, "no envelope")

    o = h.drive(fpt.t_envelope, ["2*a*x-a^2", "-2", "2", "3", "-3"])
    h.has("reversed a window refused", o, "Need a max > a min.")


# ===================================================================== c4 ==
def test_verify_de(h):
    import fpt
    # y = e^2x has y' = 2e^2x and y'' = 4e^2x, so
    # y'' - 3y' + 2y = (4 - 6 + 2)e^2x = 0: it IS a solution.
    o = h.drive(fpt.t_verifyde, ["exp(2x)", "q-3p+2y"])
    h.has("e^2x solves y''-3y'+2y=0", o, "VERIFIED")
    h.num("with a zero residual", o, "= ", 0.0, 1e-9)

    # y = e^3x gives (9 - 9 + 2)e^3x = 2e^3x, which is not zero
    o = h.drive(fpt.t_verifyde, ["exp(3x)", "q-3p+2y"])
    h.has("e^3x does not solve y''-3y'+2y=0", o, "NOT a solution")

    # y = e^x solves y' = y
    o = h.drive(fpt.t_verifyde, ["exp(x)", "p-y"])
    h.has("e^x solves y'=y", o, "VERIFIED")
    # y = e^2x does not
    o = h.drive(fpt.t_verifyde, ["exp(2x)", "p-y"])
    h.has("e^2x does not solve y'=y", o, "NOT a solution")

    # y = sin 2x has y'' = -4 sin 2x, so y'' + 4y = 0
    o = h.drive(fpt.t_verifyde, ["sin(2x)", "q+4y"])
    h.has("sin 2x solves y''+4y=0", o, "VERIFIED")
    # but y'' + y = -3 sin 2x is not zero
    o = h.drive(fpt.t_verifyde, ["sin(2x)", "q+y"])
    h.has("sin 2x does not solve y''+y=0", o, "NOT a solution")

    # y = x^2 solves dy/dx = 2x, and the derivatives are reported
    o = h.drive(fpt.t_verifyde, ["x^2", "p-2x"])
    h.has("x^2 solves y'=2x", o, "VERIFIED")
    h.has("dy/dx is shown", o, "dy/dx = 2*x")
    h.has("d2y/dx2 is shown", o, "d2y/dx2 = 2")

    # y = x^2 + 3 also solves y' = 2x (the constant differentiates away)
    o = h.drive(fpt.t_verifyde, ["x^2+3", "p-2x"])
    h.has("x^2+3 solves y'=2x as well", o, "VERIFIED")

    # unreadable input is reported, not guessed at
    o = h.drive(fpt.t_verifyde, ["x^2", None])
    h.has("a cancelled equation is reported", o, "Could not read")


# ==================================================================== T10 ==
def test_diophantine(h):
    import fpt
    # 6x + 15y = 12. gcd(6,15) = 3 and 3 | 12, so solutions exist.
    # 6(-2) + 15(1) = 3, scaled by 4: x0 = -8, y0 = 4, and 6(-8)+15(4) = 12.
    # The general solution is x = -8 + 5t, y = 4 - 2t; t = 2 gives (2, 0).
    o = h.drive(fpt.t_diophantine, ["6", "15", "12"])
    h.has("gcd(6,15) = 3", o, "gcd(6, 15) = 3")
    h.has("particular solution (-8, 4)", o, "x0 = -8, y0 = 4")
    h.has("which checks out", o, "check: 12 = 12")
    h.has("general x = -8 + 5t", o, "x = -8 + 5t")
    h.has("general y = 4 - 2t", o, "y = 4 - 2t")
    h.has("least non-negative x is 2", o, "x = 2, y = 0")

    # 6x + 15y = 7: gcd 3 does not divide 7, so there is no solution at all
    o = h.drive(fpt.t_diophantine, ["6", "15", "7"])
    h.has("3 does not divide 7", o, "does not divide 7")
    h.has("so there is no solution", o, "NO integer")

    # 17x + 5y = 1: gcd 1. 17(-2) + 5(7) = -34 + 35 = 1.
    o = h.drive(fpt.t_diophantine, ["17", "5", "1"])
    h.has("gcd(17,5) = 1", o, "gcd(17, 5) = 1")
    h.has("particular solution (-2, 7)", o, "x0 = -2, y0 = 7")
    h.has("which checks out", o, "check: 1 = 1")

    # a negative coefficient: -3x + 7y = 2 has -3(4) + 7(2) = -12 + 14 = 2
    o = h.drive(fpt.t_diophantine, ["-3", "7", "2"])
    h.has("negative a is handled", o, "-3x + 7y = 2")
    h.has("and still checks out", o, "check: 2 = 2")
    h.has("general x = 4 + 7t", o, "x = 4 + 7t")

    # 6x - 15y = 12: 6(-8) - 15(-4) = -48 + 60 = 12
    o = h.drive(fpt.t_diophantine, ["6", "-15", "12"])
    h.has("negative b prints as a subtraction", o, "6x - 15y = 12")
    h.has("and still checks out", o, "check: 12 = 12")
    h.has("with x = -8 - 5t", o, "x = -8 - 5t")

    # the degenerate all-zero case
    o = h.drive(fpt.t_diophantine, ["0", "0", "0"])
    h.has("0=0 is solved by everything", o, "every (x, y)")
    o = h.drive(fpt.t_diophantine, ["0", "0", "5"])
    h.has("0=5 is solved by nothing", o, "no solutions")


# ============================================================ shared parts ==
def test_limit_machinery(h):
    # The numeric limit is the engine under the asymptote, cusp and limit
    # tools, so its verdicts are asserted directly rather than only through
    # what a screen happened to print.
    import fpt
    # a sequence settling on 2 with a 1/n tail: 2 + 1/n at n = 1e4, 1e5, 1e6
    k = fpt._verdict([2.0001, 2.00001, 2.000001])
    h.check("a settling sequence is a limit", k[0], "num")
    h.close("and Richardson removes the 1/n tail", k[1], 2.0, 1e-9)
    # a sequence multiplying by ten every step diverges
    k = fpt._verdict([1e5, 1e6, 1e7])
    h.check("a growing sequence diverges", k[0], "inf")
    h.close("in the positive direction", k[1], 1.0)
    k = fpt._verdict([-1e5, -1e6, -1e7])
    h.check("and can diverge downwards", k[1], -1.0)
    # an oscillation is neither
    h.check("an oscillation has no limit",
            fpt._verdict([1.0, -1.0, 1.0])[0], "none")
    # a missing sample means no verdict rather than a guess
    h.check("an undefined sample gives no verdict",
            fpt._verdict([1.0, None, 1.0])[0], "none")
    # ln x grows without bound but far too slowly to be called divergent from
    # five samples, so it is reported as no limit found rather than infinity
    tree = h.caslex.parse("ln(x)")
    h.check("ln(x) has no horizontal asymptote",
            fpt._verdict(fpt._samples(tree, fpt._inf_pts(1.0)))[0], "none")

    # _blowup is what separates a pole from a jump
    h.truthy("1/x blows up at 0",
             fpt._blowup(h.caslex.parse("1/x"), 0.0, 1.0))
    h.truthy("-ln(x) blows up at 0 even though it stays small",
             fpt._blowup(h.caslex.parse("-ln(x)"), 0.0, 1.0))
    h.truthy("sqrt(x) does not blow up at 0",
             not fpt._blowup(h.caslex.parse("sqrt(x)"), 0.0, 1.0))
    h.truthy("|x|/x does not blow up at 0",
             not fpt._blowup(h.caslex.parse("abs(x)/x"), 0.0, 1.0))

    # _trim keeps a runaway solution curve out of the pixel converter
    c = fpt._trim(0.0, 0.0, 1.0, 100.0, -3.0, 3.0)
    h.close("a segment leaving the window is cut at the edge", c[3], 3.0, 1e-12)
    h.close("at the right x", c[2], 0.03, 1e-12)
    h.truthy("a segment wholly above the window is dropped",
             fpt._trim(0.0, 50.0, 1.0, 60.0, -3.0, 3.0) is None)
    c = fpt._trim(0.0, -1.0, 1.0, 1.0, -3.0, 3.0)
    h.close("a segment inside the window is kept whole", c[0], 0.0, 1e-12)
    h.close("both ends", c[3], 1.0, 1e-12)


SECTIONS = [
    ("Y436 tangent field", test_tangent_field),
    ("Y436 limits (C10)", test_limits),
    ("Y436 asymptotes (C11)", test_asymptotes),
    ("Y436 stationary points and cusps (C12)", test_stationary_and_cusps),
    ("Y436 family of curves (C4)", test_family),
    ("Y436 envelope of a family (C9)", test_envelope),
    ("Y436 verify a DE solution (c4)", test_verify_de),
    ("Y436 linear Diophantine (T10)", test_diophantine),
    ("Y436 limit machinery", test_limit_machinery),
]
