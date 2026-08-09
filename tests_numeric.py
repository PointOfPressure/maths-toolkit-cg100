# tests_numeric.py - correctness tests for the Y434 Numerical Methods tools in
# numeric.py and the Y436 Further Pure with Technology tools in fpt.py.
#
# Every assertion below is against a value known in closed form, stated in the
# comment beside it. The theme of Y434 is error BEHAVIOUR, so most of these
# check the ratio of successive differences rather than the estimate itself:
# a rule whose error goes like h^2 must show a ratio of 4 when h is halved, and
# one whose error goes like h^4 must show 16. Getting the answer right by
# accident does not produce those ratios.

import math

SQRT2 = 1.4142135623730951        # sqrt(2)
COS1 = 0.5403023058681398         # cos(1), the exact d/dx sin(x) at x = 1
FPCOS = 0.7390851332151607        # the fixed point of x = cos(x)
SINFP = 0.6736120291832148        # sin(fixed point) = |g'| there
E = 2.718281828459045             # e
TWOPI = 6.283185307179586         # 2 pi


# --------------------------------------------------- c4: integration error --
def test_integ_error(h):
    import numeric

    # int_0^1 x^2 dx = 1/3. Simpson is EXACT for a quadratic (and for a cubic),
    # so its successive estimates never move at all.
    out = h.drive(numeric.t_integ_error, ["x^2", "0", "1"], [])
    h.num("Simpson is exact for a quadratic", out, "S = ", 1.0 / 3.0, 1e-6)
    # trapezium error for x^2 on [0,1] is exactly h^2/6, and the table ends at
    # n = 64, so T = 1/3 + (1/64)^2/6 = 0.3333740234375
    h.num("trapezium at h=1/64", out, "best T = ",
          1.0 / 3.0 + (1.0 / 64.0) ** 2 / 6.0, 1e-8)
    # midpoint error is -h^2/12, exactly half the trapezium error and opposite
    h.num("midpoint at h=1/64", out, "best M = ",
          1.0 / 3.0 - (1.0 / 64.0) ** 2 / 12.0, 1e-8)
    # halving h divides an h^2 error by 4, so successive differences are in
    # the ratio 4 - and for x^2 the h^2 term is the whole error, so exactly 4
    h.num("trapezium difference ratio is 4", out, "T ratio = ", 4.0, 1e-6)
    h.num("midpoint difference ratio is 4", out, "M ratio = ", 4.0, 1e-6)
    # S = (2M + T)/3 is Simpson on twice as many strips, which for x^2 is 1/3
    h.has("Simpson is built from M and T", out, "S=(2M+T)/3")
    # (4T2 - T1)/3 is Richardson on the trapezium and is the same number
    h.num("Richardson on T equals Simpson", out, "Richardson (4T2-T1)/3 = ",
          1.0 / 3.0, 1e-9)

    # int_0^1 x^4 dx = 1/5. Simpson is NOT exact here, so its differences are
    # non-zero and must shrink by 16 (error ~ h^4) while T and M shrink by 4.
    out = h.drive(numeric.t_integ_error, ["x^4", "0", "1"], [])
    h.num("Simpson on a quartic", out, "best S = ", 0.2, 1e-8)
    h.num("Simpson difference ratio is 16", out, "S ratio = ", 16.0, 0.05)
    h.num("quartic trapezium ratio tends to 4", out, "T ratio = ", 4.0, 0.01)
    h.num("quartic midpoint ratio tends to 4", out, "M ratio = ", 4.0, 0.01)
    # the fourth order rule must be much closer than the second order ones
    h.truthy("Simpson beats the trapezium on the quartic",
             _num_after(out, "best S = ") is not None and
             abs(_num_after(out, "best S = ") - 0.2) <
             abs(_num_after(out, "best T = ") - 0.2))

    # a cancelled function must not produce a result screen full of numbers
    out = h.drive(numeric.t_integ_error, [None], [])
    h.has("bad f(x) is reported", out, "Bad function")


def _num_after(lines, key):
    # the harness's num() asserts; this returns the value so a test can compare
    # two lines of the same output against each other
    for ln in lines:
        p = ln.find(key)
        if p < 0:
            continue
        try:
            return float(ln[p + len(key):].split()[0])
        except:
            continue
    return None


# ------------------------------------------- U8: improved estimates ---------
def test_extrapolation(h):
    import numeric

    # trapezium estimates of int_0^1 x^2 dx on 1, 2 and 4 strips are
    # 0.5, 0.375 and 0.34375. One Richardson step with p = 2 gives
    # (4*0.375 - 0.5)/3 = 1/3 exactly, which is the true value.
    out = h.drive(numeric.t_richardson, ["0.5 0.375 0.34375", "2"], [])
    h.num("Richardson recovers 1/3 exactly", out, "best = ", 1.0 / 3.0, 1e-9)
    h.num("improvement on the last estimate", out,
          "improvement on last entry = ", 0.34375 - 1.0 / 3.0, 1e-9)
    h.has("the second column divides by 2^p - 1 = 3", out, "divide by 3")
    # a single estimate cannot be extrapolated
    out = h.drive(numeric.t_richardson, ["0.5"], [])
    h.has("one estimate is refused", out, "Need at least two")

    # x_n = 1 + (1/2)^n has limit 1. Aitken on any three consecutive terms of a
    # geometric sequence returns the limit exactly: 2 - (-0.5)^2/0.25 = 1.
    out = h.drive(numeric.t_aitken, ["2 1.5 1.25 1.125"], [])
    h.num("Aitken finds the limit of a geometric sequence", out,
          "best = ", 1.0, 1e-12)
    h.num("first accelerated term", out, "y0 = ", 1.0, 1e-12)
    # 1.125 is still 0.125 from the limit; Aitken jumped the whole way
    h.num("shift from the last raw term", out, "shift on last x = ",
          0.125, 1e-12)
    out = h.drive(numeric.t_aitken, ["1 2"], [])
    h.has("two terms are refused", out, "at least 3")


# ------------------------------- Nc1 / c2: differentiation over a sequence --
def test_diff_error(h):
    import numeric

    # d/dx sin(x) at x = 1 is cos(1) = 0.5403023058681398.
    out = h.drive(numeric.t_diff_error, ["sin(x)", "1"], [])
    h.num("the exact derivative is printed", out, "exact = ", COS1, 1e-8)
    # forward difference error is (h/2)f''(x) + O(h^2): first order, so halving
    # h halves the error and successive differences are in the ratio 2
    h.num("forward difference ratio is 2", out, "fwd ratio = ", 2.0, 0.05)
    # central difference error is -(h^2/6)f'''(x): second order, ratio 4
    h.num("central difference ratio is 4", out, "cen ratio = ", 4.0, 0.01)
    # killing the leading error term with the last two estimates
    h.num("central extrapolation lands on cos(1)", out, "cen extrap = ",
          COS1, 1e-8)
    h.num("forward extrapolation improves too", out, "fwd extrap = ",
          COS1, 1e-4)
    # the extrapolated central value must beat the raw one by a long way
    raw = _num_after(out, "err(cen) = ")
    ext = _num_after(out, "err(cen extrap) = ")
    h.truthy("extrapolation beats the raw central difference",
             raw is not None and ext is not None and ext < raw / 100.0)

    # d/dx x^3 at x = 2 is 12; the central difference error term is
    # (h^2/6)f''' = h^2 exactly, so it must still show a ratio of 4
    out = h.drive(numeric.t_diff_error, ["x^3", "2"], [])
    h.num("cubic exact derivative", out, "exact = ", 12.0, 1e-9)
    h.num("cubic central ratio is 4", out, "cen ratio = ", 4.0, 1e-6)
    h.num("cubic central extrapolation is exact", out, "cen extrap = ",
          12.0, 1e-9)


# ---------------------------------- NU7 / e4: order of convergence ----------
def test_convergence_order(h):
    import numeric

    # x_n = 1 + (1/2)^n: every difference is exactly half the one before, so
    # r = 0.5 for ever. A constant ratio is the signature of first order.
    out = h.drive(numeric.t_conv_order, ["2 1.5 1.25 1.125 1.0625 1.03125"], [])
    h.num("constant ratio 0.5", out, "last ratio r = ", 0.5, 1e-12)
    h.num("order p = 1", out, "order p = ", 1.0, 1e-9)
    h.has("named as first order", out, "FIRST ORDER")

    # Newton-Raphson on x^2 - 2 from x0 = 1. The error squares each step, so
    # the ratios collapse and p comes out at 2.
    newton = ("1 1.5 1.4166666666666665 1.4142156862745097 "
              "1.41421356237469 1.4142135623730951")
    out = h.drive(numeric.t_conv_order, [newton], [])
    h.num("Newton is second order", out, "order p = ", 2.0, 0.01)
    h.has("named as second order", out, "SECOND ORDER")

    # x_n = 2^n: the differences double, so |r| = 2 and the sequence diverges
    out = h.drive(numeric.t_conv_order, ["1 2 4 8 16 32"], [])
    h.num("diverging ratio is 2", out, "last ratio r = ", 2.0, 1e-12)
    h.has("divergence is called out", out, "DIVERGES")

    out = h.drive(numeric.t_conv_order, ["1 2"], [])
    h.has("two iterates are refused", out, "at least 3")


def test_fixed_point_diagnosis(h):
    import numeric

    # x = cos(x) has the Dottie number 0.7390851332151607 as its fixed point,
    # where g'(x) = -sin(x) = -0.6736120291832148. |g'| < 1, so it converges,
    # and the ratio of successive differences tends to that g'.
    out = h.drive(numeric.t_fixed_diag, ["cos(x)", "1"], [])
    h.num("fixed point of x=cos x", out, "fixed pt x = ", FPCOS, 1e-8)
    h.num("|g'| at the fixed point", out, "|g'| = ", SINFP, 1e-7)
    h.has("converging case is named", out, "converges")
    h.has("fixed point iteration is first order", out, "FIRST ORDER")

    # g(x) = 2x - 3 has the fixed point 3 with g' = 2 everywhere, so from any
    # start other than 3 the iterates must run away: |g'| > 1.
    out = h.drive(numeric.t_fixed_diag, ["2x-3", "3.5"], [])
    h.num("|g'| = 2 for g = 2x-3", out, "|g'| = ", 2.0, 1e-9)
    h.has("divergence is diagnosed", out, "diverges")
    h.has("the cause is |g'| > 1", out, "|g'| > 1")

    # g(x) = (x + 2/x)/2 has g'(sqrt2) = 1/2 - 1/x^2 = 0 there, which is why
    # that rearrangement converges quadratically instead of linearly
    out = h.drive(numeric.t_fixed_diag, ["(x+2/x)/2", "1"], [])
    h.num("Newton's sqrt map has a fixed point at sqrt 2", out,
          "fixed pt x = ", SQRT2, 1e-9)
    h.num("g' vanishes there", out, "|g'| = ", 0.0, 1e-9)
    h.has("second order is reported", out, "second order")


# ------------------------------------------------------ e5: relaxation ------
def test_relaxation(h):
    import numeric

    # g(x) = -3x + 4 has the fixed point x = 1 and g' = -3, so plain iteration
    # (L = 1) diverges. Relaxation with L = 1/(1-g') = 1/4 gives
    # G(x) = x + 0.25(-3x + 4 - x) = 1 for every x, so it lands in one step.
    out = h.drive(numeric.t_relax, ["-3x+4", "5", "0.25"], [])
    h.num("relaxed iteration reaches the fixed point", out,
          "fixed pt x = ", 1.0, 1e-12)
    h.num("g' = -3", out, "g'(x) = ", -3.0, 1e-9)
    h.num("G' = 1 + L(g'-1) = 0", out, "G' = ", 0.0, 1e-12)
    h.num("optimal L = 1/(1-g') = 0.25", out, "suggested L = ", 0.25, 1e-12)
    h.has("this L is reported as convergent", out, "this L converges")

    # the same g with L = 1 is the unrelaxed iteration, which must diverge
    out = h.drive(numeric.t_relax, ["-3x+4", "5", "1"], [])
    h.has("L=1 diverges here", out, "diverges with this L")
    h.num("G' = g' when L = 1", out, "G' = ", -3.0, 1e-9)
    h.num("the suggested L is still 0.25", out, "suggested L = ", 0.25, 1e-12)

    # over-relaxing past the useful range fails as well: L = 1 is recovered
    # only at L = 1, and |1 + L(g'-1)| = |1 - 4L| >= 1 for L >= 0.5
    out = h.drive(numeric.t_relax, ["-3x+4", "5", "0.5"], [])
    h.num("L = 0.5 gives G' = -1", out, "G' = ", -1.0, 1e-9)
    h.has("L = 0.5 is reported as failing", out, "this L fails")


# ----------------------------------------- Ne1: staircase and cobweb --------
def test_cobweb(h):
    import numeric

    # g'(x) < 0 makes the iterates alternate either side of the fixed point:
    # that is the cobweb. g = cos(x) has g' = -sin(x) < 0 near x = 0.739.
    out = h.drive(numeric.t_cobweb, ["cos(x)", "1"], [])
    h.has("negative g' draws a cobweb", out, "COBWEB")
    h.num("g' is negative there", out, "g'(x) = ", -0.681944372, 1e-6)
    h.has("it converges", out, "converges")

    # g'(x) > 0 makes every step move the same way: that is the staircase.
    # g = sqrt(2x+3) has the fixed point 3 (9 = 6 + 3) and g'(3) = 1/3 > 0.
    out = h.drive(numeric.t_cobweb, ["sqrt(2x+3)", "1"], [])
    h.has("positive g' draws a staircase", out, "STAIRCASE")
    h.num("the iterates climb towards 3", out, "x8 = ", 3.0, 5e-4)
    h.num("g'(3) = 1/3", out, "g'(x) = ", 1.0 / 3.0, 1e-3)


# ------------------------------------- Nf1 / f2: forward differences --------
def test_forward_differences(h):
    import numeric

    # y = x^2 sampled at x = 0, 1, 2, 3 gives 0, 1, 4, 9. The difference table
    # is 1 3 5 / 2 2 / 0, so the interpolating polynomial is exactly x^2 and
    # p(2.5) = 6.25.
    out = h.drive(numeric.t_newton_fwd, ["0 1 4 9", "0", "1", "2.5"], [])
    h.has("first differences", out, "D1: 1 3 5")
    h.has("second differences are constant", out, "D2: 2 2")
    h.has("third differences vanish", out, "D3: 0")
    h.has("the interpolating polynomial is x^2", out, "p(x) = x^2")
    h.num("interpolated value", out, "p(2.5) = ", 6.25, 1e-12)
    h.num("s = (x - x0)/h", out, "s = ", 2.5, 1e-12)
    h.has("degree 2", out, "degree = 2")

    # y = x^3 sampled at x = 0, 2, 4, 6, 8 gives 0, 8, 64, 216, 512 with h = 2.
    # In terms of s the polynomial is 8s^3, and in x it is x^3, so p(3) = 27.
    out = h.drive(numeric.t_newton_fwd, ["0 8 64 216 512", "0", "2", "3"], [])
    h.has("the s-form carries the step", out, "p(s) = 8*s^3")
    h.has("the x-form is x^3", out, "p(x) = x^3")
    h.num("cubic interpolation at x=3", out, "p(3) = ", 27.0, 1e-9)
    h.has("fourth differences vanish", out, "D4 = 0")

    # extrapolating outside the table has to be flagged
    out = h.drive(numeric.t_newton_fwd, ["0 1 4 9", "0", "1", "7"], [])
    h.has("extrapolation is flagged", out, "extrapolation")

    out = h.drive(numeric.t_newton_fwd, ["5"], [])
    h.has("a single y value is refused", out, "at least 2")


# ------------------------------- NU1 / U2 / U3 / U6: error handling ---------
def test_error_propagation(h):
    import numeric

    # a = 10 +/- 0.1 (1%), b = 5 +/- 0.05 (1%).
    # sums and differences add ABSOLUTE errors: 0.1 + 0.05 = 0.15
    # products and quotients add RELATIVE errors: 1% + 1% = 2%
    out = h.drive(numeric.t_err_prop, ["10", "0.1", "5", "0.05"], [])
    h.num("relative error in a", out, "rel(a) = ", 0.01, 1e-12)
    h.num("relative error in b", out, "rel(b) = ", 0.01, 1e-12)
    h.num("a+b", out, "a+b = ", 15.0, 1e-12)
    h.num("absolute errors add in a sum", out, "err(a+b) = ", 0.15, 1e-12)
    h.num("relative error of the sum", out, "rel(a+b) = ", 0.01, 1e-12)
    h.num("a-b", out, "a-b = ", 5.0, 1e-12)
    h.num("absolute errors add in a difference", out, "err(a-b) = ",
          0.15, 1e-12)
    # the same 0.15 over a smaller result is a bigger relative error: 3%
    h.num("a difference has the worse relative error", out, "rel(a-b) = ",
          0.03, 1e-12)
    h.num("a*b", out, "a*b = ", 50.0, 1e-12)
    h.num("relative errors add in a product", out, "rel(a*b) = ", 0.02, 1e-12)
    h.num("absolute error of the product", out, "err(a*b) = ", 1.0, 1e-12)
    h.num("a/b", out, "a/b = ", 2.0, 1e-12)
    h.num("relative errors add in a quotient", out, "rel(a/b) = ",
          0.02, 1e-12)
    h.num("absolute error of the quotient", out, "err(a/b) = ", 0.04, 1e-12)

    # 10 - 9.99 = 0.01 with a combined error of 0.15: the answer is worthless,
    # which is exactly the rearrangement warning U3 asks for
    out = h.drive(numeric.t_err_prop, ["10", "0.1", "9.99", "0.05"], [])
    h.num("cancellation leaves almost nothing", out, "a-b = ", 0.01, 1e-9)
    h.has("cancellation is warned about", out, "nearly")
    h.has("rearrangement is suggested", out, "Rearrange")


def test_error_in_fx(h):
    import numeric

    # f(x) = x^2 at x = 3 with dx = 0.01. f'(3) = 6, so the error in f is
    # about |f'| dx = 0.06; the true worst case is f(3.01) - f(3) = 0.0601.
    out = h.drive(numeric.t_err_fx, ["x^2", "3", "0.01"], [])
    h.num("f(3) = 9", out, "f(x) = ", 9.0, 1e-12)
    h.num("f'(3) = 6", out, "f'(x) = ", 6.0, 1e-9)
    h.num("estimated error |f'| dx", out, "abs err = ", 0.06, 1e-9)
    h.num("relative error 0.06/9", out, "rel err = ", 0.06 / 9.0, 1e-9)
    h.num("f(3.01)", out, "f(x+dx) = ", 9.0601, 1e-9)
    h.num("f(2.99)", out, "f(x-dx) = ", 8.9401, 1e-9)
    h.num("worst actual change", out, "largest actual change = ",
          0.0601, 1e-9)

    # f(x) = sqrt(x) at x = 100 with dx = 1: f' = 1/20, so the error in f is
    # about 0.05 while the relative error falls from 1% to 0.5%
    out = h.drive(numeric.t_err_fx, ["sqrt(x)", "100", "1"], [])
    h.num("sqrt(100) = 10", out, "f(x) = ", 10.0, 1e-12)
    h.num("derivative 1/(2 sqrt x) = 0.05", out, "f'(x) = ", 0.05, 1e-9)
    h.num("error in the root", out, "abs err = ", 0.05, 1e-9)
    h.num("a square root halves the relative error", out, "rel err = ",
          0.005, 1e-9)


def test_chop_round(h):
    import numeric

    # 3.14159 to 3 d.p.: chopping throws away 0.00059, rounding goes up to
    # 3.142 and is 0.00041 the other side. The unit in the last place is
    # u = 0.001, so chopping can be wrong by up to u and averages u/2, while
    # rounding can be wrong by up to u/2 and averages zero.
    out = h.drive(numeric.t_chop, ["3.14159", "3"], [])
    h.num("chopped value", out, "chop = ", 3.141, 1e-9)
    h.num("rounded value", out, "round = ", 3.142, 1e-9)
    h.num("chop error", out, "chop error = ", 0.00059, 1e-9)
    h.num("round error", out, "round error = ", -0.00041, 1e-9)
    h.num("chop maximum error is u", out, "chop max err = ", 0.001, 1e-12)
    h.num("chop mean error is u/2", out, "chop mean err = ", 0.0005, 1e-12)
    h.num("round maximum error is u/2", out, "round max err = ",
          0.0005, 1e-12)
    h.num("round mean |error| is u/4", out, "round mean |err| = ",
          0.00025, 1e-12)
    h.has("the bias of chopping is stated", out, "biases")

    # a negative value must chop towards zero, not downwards: -2.7 to 0 d.p.
    # chops to -2 and rounds to -3
    out = h.drive(numeric.t_chop, ["-2.7", "0"], [])
    h.num("chopping truncates towards zero", out, "chop = ", -2.0, 1e-12)
    h.num("rounding goes to the nearer", out, "round = ", -3.0, 1e-12)


# ------------------------------- e2: accuracy chosen, bound reported --------
def test_accuracy_and_bounds(h):
    import numeric

    # bisection on x^2 - 2 over [1, 2]: the bracket is 1 wide, so after n
    # midpoints the error is at most 2^-n. For a target of 1e-3 that needs
    # n = 10 (2^-10 = 0.0009765625) and the answer is quoted with that bound.
    out = h.drive(numeric.t_bisect, ["x^2-2", "1", "2", "0.001"], [])
    h.has("the number of halvings is predicted", out, "steps needed = 10")
    h.num("the bound is 2^-10", out, "error bound <= ", 0.0009765625, 1e-9)
    h.num("the root is inside that bound", out, "root x=", SQRT2, 0.001)
    h.num("the target is echoed", out, "target accuracy ", 0.001, 1e-12)

    # a tighter target must take more steps and give a tighter bound
    out = h.drive(numeric.t_bisect, ["x^2-2", "1", "2", "1e-6"], [])
    h.has("a tighter target needs more steps", out, "steps needed = 20")
    # printed to 9 d.p., so the check is against the print, not the double
    h.num("and gives a tighter bound", out, "error bound <= ",
          1.0 / 1048576.0, 1e-8)

    # Newton stopped at 1e-2 lands on the third iterate 1.4142156862745097,
    # whose last correction was -0.0024509803921568 - that is the bound
    out = h.drive(numeric.t_newton, ["x^2-2", "1", "0.01"], [])
    h.num("Newton stops early with a loose target", out, "root x=",
          1.4142156862745097, 1e-6)
    h.num("and reports the step it stopped on", out, "error bound <= ",
          0.0024509803921568, 1e-9)
    # the default is still 1e-9 when nothing is entered, so the old behaviour
    # is unchanged
    out = h.drive(numeric.t_newton, ["x^2-2", "1"], [])
    h.num("default tolerance still converges", out, "root x=", SQRT2, 1e-5)
    h.num("default target is 1e-9", out, "target accuracy ", 1e-9, 1e-15)

    # fixed point: x = (x + 2/x)/2 converges to sqrt 2 and reports a bound
    out = h.drive(numeric.t_fixed, ["(x+2/x)/2", "1"], [])
    h.num("fixed point still converges", out, "fixed pt x=", SQRT2, 1e-6)
    bound = _num_after(out, "error bound <= ")
    h.truthy("a positive bound is quoted", bound is not None and bound > 0)


# ====================== Y436 Further Pure with Technology ==================
def test_runge_kutta(h):
    import fpt

    # dy/dx = y with y(0) = 1 has the solution y = e^x, so y(1) = e.
    # With h = 0.1 over 10 steps:
    #   Euler   gives (1 + h)^10       = 1.1^10   = 2.5937424601   (4.6% low)
    #   RK2     gives (1 + h + h^2/2)^10 = 1.105^10 = 2.714080846608224
    #   RK4     gives (1+h+h^2/2+h^3/6+h^4/24)^10 = 2.7182797441351627,
    #           which is e to about 2e-6.
    out = h.drive(fpt.t_rk, ["y", "0", "1", "0.1", "10"], [])
    h.num("Euler at h=0.1 is (1.1)^10", out, "Euler y = ",
          1.1 ** 10, 1e-7)
    h.num("RK2 midpoint at h=0.1 is (1.105)^10", out, "RK2 y = ",
          1.105 ** 10, 1e-7)
    h.num("RK4 at h=0.1 matches e to 1e-5", out, "RK4 y = ", E, 1e-5)
    # the whole point: at the SAME step size RK4 is four orders better
    eu = _num_after(out, "Euler y = ")
    rk = _num_after(out, "RK4 y = ")
    h.truthy("Euler is a few percent out at this step",
             eu is not None and abs(eu - E) / E > 0.04)
    h.truthy("RK4 at the same step is not",
             rk is not None and abs(rk - E) / E < 1e-5)
    h.has("the four RK4 stages are shown", out, "k4 = f(x+h, y+h.k3)")
    h.has("the step-halving comparison is shown", out, "smaller h")

    # dy/dx = x with y(0) = 0 has the solution y = x^2/2, a quadratic, so RK2
    # and RK4 are both exact while Euler is not: y(1) = 0.5 exactly, and Euler
    # gives h*(0 + 0.1 + ... + 0.9) = 0.45.
    out = h.drive(fpt.t_rk, ["x", "0", "0", "0.1", "10"], [])
    h.num("RK2 is exact for dy/dx = x", out, "RK2 y = ", 0.5, 1e-12)
    h.num("RK4 is exact for dy/dx = x", out, "RK4 y = ", 0.5, 1e-12)
    h.num("Euler is not", out, "Euler y = ", 0.45, 1e-12)


def test_arc_length(h):
    import fpt

    # y = x from 0 to 1 is the diagonal of a unit square: length sqrt(2).
    out = h.drive(fpt.t_arclen, ["x", "0", "1"], [0])
    h.num("straight line arc length", out, "arc length = ", SQRT2, 1e-7)

    # the semicircle y = sqrt(1 - x^2) is not exactly integrable by Simpson at
    # the endpoints, so use the circle in the other two forms instead:
    # r = 1 from 0 to 2pi is a unit circle, circumference 2 pi.
    out = h.drive(fpt.t_arclen, ["1", "0", "2pi"], [1])
    h.num("polar unit circle", out, "arc length = ", TWOPI, 1e-7)

    # x = cos t, y = sin t over one turn is the same circle
    out = h.drive(fpt.t_arclen, ["cos(t)", "sin(t)", "0", "2pi"], [2])
    h.num("parametric unit circle", out, "arc length = ", TWOPI, 1e-7)

    # x = 3cos t, y = 3sin t has radius 3, so 6 pi
    out = h.drive(fpt.t_arclen, ["3cos(t)", "3sin(t)", "0", "2pi"], [2])
    h.num("parametric circle of radius 3", out, "arc length = ",
          3.0 * TWOPI, 1e-8)

    # backing out of the menu must do nothing at all
    out = h.drive(fpt.t_arclen, [], [-1])
    h.check("cancelling the arc length menu shows nothing", out, [])


def test_number_theory(h):
    import fpt

    # phi(36) = 36(1 - 1/2)(1 - 1/3) = 12
    out = h.drive(fpt.t_totient, ["36"], [])
    h.num("phi(36) = 12", out, "phi(n) = ", 12.0, 1e-12)
    h.has("the distinct primes of 36", out, "distinct primes: 2 3")
    # phi(p) = p - 1 for a prime
    out = h.drive(fpt.t_totient, ["97"], [])
    h.num("phi(97) = 96", out, "phi(n) = ", 96.0, 1e-12)
    h.has("primes are called out", out, "n is prime")
    out = h.drive(fpt.t_totient, ["1"], [])
    h.num("phi(1) = 1", out, "phi(n) = ", 1.0, 1e-12)

    # the primitive triples with c <= 30 are exactly (3,4,5), (5,12,13),
    # (8,15,17), (7,24,25) and (20,21,29): five of them
    out = h.drive(fpt.t_pythag, ["30"], [])
    h.num("five primitive triples up to c = 30", out, "count = ", 5.0, 1e-12)
    h.has("3-4-5", out, "3, 4, 5")
    h.has("5-12-13", out, "5, 12, 13")
    h.has("8-15-17", out, "8, 15, 17")
    h.has("7-24-25", out, "7, 24, 25")
    h.has("20-21-29", out, "20, 21, 29")
    # 6, 8, 10 is a triple but not a primitive one, so it must not be listed
    h.truthy("multiples are excluded",
             not [ln for ln in out if ln.startswith("6, 8, 10")])

    # Euclid's formula only generates primitives when gcd(m,n) = 1 as well as
    # m-n odd. m=6, n=3 satisfies the parity test but not the coprime one, and
    # would produce 27, 36, 45 = 9*(3,4,5); m=9, n=6 would give
    # 45, 108, 117 = 9*(5,12,13). Counted by hand there are exactly 19
    # primitive triples with c <= 120, the last being 15, 112, 113.
    out = h.drive(fpt.t_pythag, ["120"], [])
    h.num("19 primitive triples up to c = 120", out, "count = ", 19.0, 1e-12)
    h.has("the largest one up to 120", out, "15, 112, 113")
    h.has("a middling one", out, "33, 56, 65")
    h.truthy("9*(3,4,5) is not primitive, so it is excluded",
             not [ln for ln in out if ln.startswith("27, 36, 45")])
    h.truthy("9*(5,12,13) is excluded too",
             not [ln for ln in out if ln.startswith("45, 108, 117")])

    # x^2 - 2y^2 = 1: the fundamental solution is (3, 2), 9 - 8 = 1
    out = h.drive(fpt.t_pell, ["2"], [])
    h.num("Pell x for n=2", out, "x = ", 3.0, 1e-12)
    h.num("Pell y for n=2", out, "y = ", 2.0, 1e-12)
    h.num("the solution checks out", out, "check x^2-n y^2 = ", 1.0, 1e-12)
    # x^2 - 13y^2 = 1: 649^2 - 13*180^2 = 421201 - 421200 = 1
    out = h.drive(fpt.t_pell, ["13"], [])
    h.num("Pell x for n=13", out, "x = ", 649.0, 1e-9)
    h.num("Pell y for n=13", out, "y = ", 180.0, 1e-9)
    # x^2 - 61y^2 = 1 is the famous hard one: (1766319049, 226153980)
    out = h.drive(fpt.t_pell, ["61"], [])
    h.num("Pell x for n=61", out, "x = ", 1766319049.0, 1.0)
    h.num("Pell y for n=61", out, "y = ", 226153980.0, 1.0)
    # a perfect square has no non-trivial solution
    out = h.drive(fpt.t_pell, ["9"], [])
    h.has("perfect squares are rejected", out, "perfect square")

    # Fermat: 3^6 = 729 = 104*7 + 1, so 3^6 mod 7 = 1.
    # Wilson: 6! = 720 = 102*7 + 6, so (p-1)! mod 7 = 6 = -1 mod 7.
    out = h.drive(fpt.t_fermat, ["7", "3"], [])
    h.num("Fermat's little theorem for p=7, a=3", out,
          "a^(p-1) mod p = ", 1.0, 1e-12)
    h.num("Wilson's theorem for p=7", out, "(p-1)! mod p = ", 6.0, 1e-12)
    h.num("and -1 mod 7 is 6", out, "-1 mod p = ", 6.0, 1e-12)
    h.has("Wilson confirms primality", out, "Wilson holds")
    # 9 is composite: 2^8 = 256 = 28*9 + 4, so Fermat's test gives 4, not 1,
    # and 8! contains 3*6 = 18, a multiple of 9, so Wilson gives 0
    out = h.drive(fpt.t_fermat, ["9", "2"], [])
    h.num("Fermat's test fails for 9", out, "a^(p-1) mod p = ", 4.0, 1e-12)
    h.num("Wilson gives 0 for a composite", out, "(p-1)! mod p = ",
          0.0, 1e-12)
    h.has("composite is reported", out, "not prime")


SECTIONS = [
    ("Y434 integration error behaviour", test_integ_error),
    ("Y434 extrapolation", test_extrapolation),
    ("Y434 differentiation error", test_diff_error),
    ("Y434 order of convergence", test_convergence_order),
    ("Y434 fixed point diagnosis", test_fixed_point_diagnosis),
    ("Y434 relaxation", test_relaxation),
    ("Y434 cobweb and staircase", test_cobweb),
    ("Y434 forward differences", test_forward_differences),
    ("Y434 error propagation", test_error_propagation),
    ("Y434 error in f(x)", test_error_in_fx),
    ("Y434 chopping and rounding", test_chop_round),
    ("Y434 accuracy and error bounds", test_accuracy_and_bounds),
    ("Y436 Runge-Kutta", test_runge_kutta),
    ("Y436 arc length", test_arc_length),
    ("Y436 number theory", test_number_theory),
]
