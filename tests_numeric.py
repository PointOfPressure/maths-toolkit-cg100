import math

SQRT2 = 1.4142135623730951
COS1 = 0.5403023058681398
FPCOS = 0.7390851332151607
SINFP = 0.6736120291832148
E = 2.718281828459045
TWOPI = 6.283185307179586


def test_integ_error(h):
    import numeric

    out = h.drive(numeric.t_integ_error, ["x^2", "0", "1"], [])
    h.num("Simpson is exact for a quadratic", out, "S = ", 1.0 / 3.0, 1e-6)
    h.num("trapezium at h=1/64", out, "best T = ",
          1.0 / 3.0 + (1.0 / 64.0) ** 2 / 6.0, 1e-8)
    h.num("midpoint at h=1/64", out, "best M = ",
          1.0 / 3.0 - (1.0 / 64.0) ** 2 / 12.0, 1e-8)
    h.num("trapezium difference ratio is 4", out, "T ratio = ", 4.0, 1e-6)
    h.num("midpoint difference ratio is 4", out, "M ratio = ", 4.0, 1e-6)
    h.has("Simpson is built from M and T", out, "S=(2M+T)/3")
    h.num("Richardson on T equals Simpson", out, "Richardson (4T2-T1)/3 = ",
          1.0 / 3.0, 1e-9)

    out = h.drive(numeric.t_integ_error, ["x^4", "0", "1"], [])
    h.num("Simpson on a quartic", out, "best S = ", 0.2, 1e-8)
    h.num("Simpson difference ratio is 16", out, "S ratio = ", 16.0, 0.05)
    h.num("quartic trapezium ratio tends to 4", out, "T ratio = ", 4.0, 0.01)
    h.num("quartic midpoint ratio tends to 4", out, "M ratio = ", 4.0, 0.01)
    h.truthy("Simpson beats the trapezium on the quartic",
             _num_after(out, "best S = ") is not None and
             abs(_num_after(out, "best S = ") - 0.2) <
             abs(_num_after(out, "best T = ") - 0.2))

    out = h.drive(numeric.t_integ_error, [None], [])
    h.has("bad f(x) is reported", out, "Bad function")


def _num_after(lines, key):
    for ln in lines:
        p = ln.find(key)
        if p < 0:
            continue
        try:
            return float(ln[p + len(key):].split()[0])
        except:
            continue
    return None


def test_extrapolation(h):
    import numeric

    out = h.drive(numeric.t_richardson, ["0.5 0.375 0.34375", "2"], [])
    h.num("Richardson recovers 1/3 exactly", out, "best = ", 1.0 / 3.0, 1e-9)
    h.num("improvement on the last estimate", out,
          "improvement on last entry = ", 0.34375 - 1.0 / 3.0, 1e-9)
    h.has("the second column divides by 2^p - 1 = 3", out, "divide by 3")
    out = h.drive(numeric.t_richardson, ["0.5"], [])
    h.has("one estimate is refused", out, "Need at least two")

    out = h.drive(numeric.t_aitken, ["2 1.5 1.25 1.125"], [])
    h.num("Aitken finds the limit of a geometric sequence", out,
          "best = ", 1.0, 1e-12)
    h.num("first accelerated term", out, "y0 = ", 1.0, 1e-12)
    h.num("shift from the last raw term", out, "shift on last x = ",
          0.125, 1e-12)
    out = h.drive(numeric.t_aitken, ["1 2"], [])
    h.has("two terms are refused", out, "at least 3")


def test_diff_error(h):
    import numeric

    out = h.drive(numeric.t_diff_error, ["sin(x)", "1"], [])
    h.num("the exact derivative is printed", out, "exact = ", COS1, 1e-8)
    h.num("forward difference ratio is 2", out, "fwd ratio = ", 2.0, 0.05)
    h.num("central difference ratio is 4", out, "cen ratio = ", 4.0, 0.01)
    h.num("central extrapolation lands on cos(1)", out, "cen extrap = ",
          COS1, 1e-8)
    h.num("forward extrapolation improves too", out, "fwd extrap = ",
          COS1, 1e-4)
    raw = _num_after(out, "err(cen) = ")
    ext = _num_after(out, "err(cen extrap) = ")
    h.truthy("extrapolation beats the raw central difference",
             raw is not None and ext is not None and ext < raw / 100.0)

    out = h.drive(numeric.t_diff_error, ["x^3", "2"], [])
    h.num("cubic exact derivative", out, "exact = ", 12.0, 1e-9)
    h.num("cubic central ratio is 4", out, "cen ratio = ", 4.0, 1e-6)
    h.num("cubic central extrapolation is exact", out, "cen extrap = ",
          12.0, 1e-9)


def test_convergence_order(h):
    import numeric

    out = h.drive(numeric.t_conv_order, ["2 1.5 1.25 1.125 1.0625 1.03125"], [])
    h.num("constant ratio 0.5", out, "last ratio r = ", 0.5, 1e-12)
    h.num("order p = 1", out, "order p = ", 1.0, 1e-9)
    h.has("named as first order", out, "FIRST ORDER")

    newton = ("1 1.5 1.4166666666666665 1.4142156862745097 "
              "1.41421356237469 1.4142135623730951")
    out = h.drive(numeric.t_conv_order, [newton], [])
    h.num("Newton is second order", out, "order p = ", 2.0, 0.01)
    h.has("named as second order", out, "SECOND ORDER")

    out = h.drive(numeric.t_conv_order, ["1 2 4 8 16 32"], [])
    h.num("diverging ratio is 2", out, "last ratio r = ", 2.0, 1e-12)
    h.has("divergence is called out", out, "DIVERGES")

    out = h.drive(numeric.t_conv_order, ["1 2"], [])
    h.has("two iterates are refused", out, "at least 3")


def test_fixed_point_diagnosis(h):
    import numeric

    out = h.drive(numeric.t_fixed_diag, ["cos(x)", "1"], [])
    h.num("fixed point of x=cos x", out, "fixed pt x = ", FPCOS, 1e-8)
    h.num("|g'| at the fixed point", out, "|g'| = ", SINFP, 1e-7)
    h.has("converging case is named", out, "converges")
    h.has("fixed point iteration is first order", out, "FIRST ORDER")

    out = h.drive(numeric.t_fixed_diag, ["2x-3", "3.5"], [])
    h.num("|g'| = 2 for g = 2x-3", out, "|g'| = ", 2.0, 1e-9)
    h.has("divergence is diagnosed", out, "diverges")
    h.has("the cause is |g'| > 1", out, "|g'| > 1")

    out = h.drive(numeric.t_fixed_diag, ["(x+2/x)/2", "1"], [])
    h.num("Newton's sqrt map has a fixed point at sqrt 2", out,
          "fixed pt x = ", SQRT2, 1e-9)
    h.num("g' vanishes there", out, "|g'| = ", 0.0, 1e-9)
    h.has("second order is reported", out, "second order")


def test_relaxation(h):
    import numeric

    out = h.drive(numeric.t_relax, ["-3x+4", "5", "0.25"], [])
    h.num("relaxed iteration reaches the fixed point", out,
          "fixed pt x = ", 1.0, 1e-12)
    h.num("g' = -3", out, "g'(x) = ", -3.0, 1e-9)
    h.num("G' = 1 + L(g'-1) = 0", out, "G' = ", 0.0, 1e-12)
    h.num("optimal L = 1/(1-g') = 0.25", out, "suggested L = ", 0.25, 1e-12)
    h.has("this L is reported as convergent", out, "this L converges")

    out = h.drive(numeric.t_relax, ["-3x+4", "5", "1"], [])
    h.has("L=1 diverges here", out, "diverges with this L")
    h.num("G' = g' when L = 1", out, "G' = ", -3.0, 1e-9)
    h.num("the suggested L is still 0.25", out, "suggested L = ", 0.25, 1e-12)

    out = h.drive(numeric.t_relax, ["-3x+4", "5", "0.5"], [])
    h.num("L = 0.5 gives G' = -1", out, "G' = ", -1.0, 1e-9)
    h.has("L = 0.5 is reported as failing", out, "this L fails")


def test_cobweb(h):
    import numeric

    out = h.drive(numeric.t_cobweb, ["cos(x)", "1"], [])
    h.has("negative g' draws a cobweb", out, "COBWEB")
    h.num("g' is negative there", out, "g'(x) = ", -0.681944372, 1e-6)
    h.has("it converges", out, "converges")

    out = h.drive(numeric.t_cobweb, ["sqrt(2x+3)", "1"], [])
    h.has("positive g' draws a staircase", out, "STAIRCASE")
    h.num("the iterates climb towards 3", out, "x8 = ", 3.0, 5e-4)
    h.num("g'(3) = 1/3", out, "g'(x) = ", 1.0 / 3.0, 1e-3)


def test_forward_differences(h):
    import numeric

    out = h.drive(numeric.t_newton_fwd, ["0 1 4 9", "0", "1", "2.5"], [])
    h.has("first differences", out, "D1: 1 3 5")
    h.has("second differences are constant", out, "D2: 2 2")
    h.has("third differences vanish", out, "D3: 0")
    h.has("the interpolating polynomial is x^2", out, "p(x) = x^2")
    h.num("interpolated value", out, "p(2.5) = ", 6.25, 1e-12)
    h.num("s = (x - x0)/h", out, "s = ", 2.5, 1e-12)
    h.has("degree 2", out, "degree = 2")

    out = h.drive(numeric.t_newton_fwd, ["0 8 64 216 512", "0", "2", "3"], [])
    h.has("the s-form carries the step", out, "p(s) = 8*s^3")
    h.has("the x-form is x^3", out, "p(x) = x^3")
    h.num("cubic interpolation at x=3", out, "p(3) = ", 27.0, 1e-9)
    h.has("fourth differences vanish", out, "D4 = 0")

    out = h.drive(numeric.t_newton_fwd, ["0 1 4 9", "0", "1", "7"], [])
    h.has("extrapolation is flagged", out, "extrapolation")

    out = h.drive(numeric.t_newton_fwd, ["5"], [])
    h.has("a single y value is refused", out, "at least 2")


def test_error_propagation(h):
    import numeric

    out = h.drive(numeric.t_err_prop, ["10", "0.1", "5", "0.05"], [])
    h.num("relative error in a", out, "rel(a) = ", 0.01, 1e-12)
    h.num("relative error in b", out, "rel(b) = ", 0.01, 1e-12)
    h.num("a+b", out, "a+b = ", 15.0, 1e-12)
    h.num("absolute errors add in a sum", out, "err(a+b) = ", 0.15, 1e-12)
    h.num("relative error of the sum", out, "rel(a+b) = ", 0.01, 1e-12)
    h.num("a-b", out, "a-b = ", 5.0, 1e-12)
    h.num("absolute errors add in a difference", out, "err(a-b) = ",
          0.15, 1e-12)
    h.num("a difference has the worse relative error", out, "rel(a-b) = ",
          0.03, 1e-12)
    h.num("a*b", out, "a*b = ", 50.0, 1e-12)
    h.num("relative errors add in a product", out, "rel(a*b) = ", 0.02, 1e-12)
    h.num("absolute error of the product", out, "err(a*b) = ", 1.0, 1e-12)
    h.num("a/b", out, "a/b = ", 2.0, 1e-12)
    h.num("relative errors add in a quotient", out, "rel(a/b) = ",
          0.02, 1e-12)
    h.num("absolute error of the quotient", out, "err(a/b) = ", 0.04, 1e-12)

    out = h.drive(numeric.t_err_prop, ["10", "0.1", "9.99", "0.05"], [])
    h.num("cancellation leaves almost nothing", out, "a-b = ", 0.01, 1e-9)
    h.has("cancellation is warned about", out, "nearly")
    h.has("rearrangement is suggested", out, "Rearrange")


def test_error_in_fx(h):
    import numeric

    out = h.drive(numeric.t_err_fx, ["x^2", "3", "0.01"], [])
    h.num("f(3) = 9", out, "f(x) = ", 9.0, 1e-12)
    h.num("f'(3) = 6", out, "f'(x) = ", 6.0, 1e-9)
    h.num("estimated error |f'| dx", out, "abs err = ", 0.06, 1e-9)
    h.num("relative error 0.06/9", out, "rel err = ", 0.06 / 9.0, 1e-9)
    h.num("f(3.01)", out, "f(x+dx) = ", 9.0601, 1e-9)
    h.num("f(2.99)", out, "f(x-dx) = ", 8.9401, 1e-9)
    h.num("worst actual change", out, "largest actual change = ",
          0.0601, 1e-9)

    out = h.drive(numeric.t_err_fx, ["sqrt(x)", "100", "1"], [])
    h.num("sqrt(100) = 10", out, "f(x) = ", 10.0, 1e-12)
    h.num("derivative 1/(2 sqrt x) = 0.05", out, "f'(x) = ", 0.05, 1e-9)
    h.num("error in the root", out, "abs err = ", 0.05, 1e-9)
    h.num("a square root halves the relative error", out, "rel err = ",
          0.005, 1e-9)


def test_chop_round(h):
    import numeric

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

    out = h.drive(numeric.t_chop, ["-2.7", "0"], [])
    h.num("chopping truncates towards zero", out, "chop = ", -2.0, 1e-12)
    h.num("rounding goes to the nearer", out, "round = ", -3.0, 1e-12)


def test_accuracy_and_bounds(h):
    import numeric

    out = h.drive(numeric.t_bisect, ["x^2-2", "1", "2", "0.001"], [])
    h.has("the number of halvings is predicted", out, "steps needed = 10")
    h.num("the bound is 2^-10", out, "error bound <= ", 0.0009765625, 1e-9)
    h.num("the root is inside that bound", out, "root x=", SQRT2, 0.001)
    h.num("the target is echoed", out, "target accuracy ", 0.001, 1e-12)

    out = h.drive(numeric.t_bisect, ["x^2-2", "1", "2", "1e-6"], [])
    h.has("a tighter target needs more steps", out, "steps needed = 20")
    h.num("and gives a tighter bound", out, "error bound <= ",
          1.0 / 1048576.0, 1e-8)

    out = h.drive(numeric.t_newton, ["x^2-2", "1", "0.01"], [])
    h.num("Newton stops early with a loose target", out, "root x=",
          1.4142156862745097, 1e-6)
    h.num("and reports the step it stopped on", out, "error bound <= ",
          0.0024509803921568, 1e-9)
    out = h.drive(numeric.t_newton, ["x^2-2", "1"], [])
    h.num("default tolerance still converges", out, "root x=", SQRT2, 1e-5)
    h.num("default target is 1e-9", out, "target accuracy ", 1e-9, 1e-15)

    out = h.drive(numeric.t_fixed, ["(x+2/x)/2", "1"], [])
    h.num("fixed point still converges", out, "fixed pt x=", SQRT2, 1e-6)
    bound = _num_after(out, "error bound <= ")
    h.truthy("a positive bound is quoted", bound is not None and bound > 0)


def test_runge_kutta(h):
    import fpt

    out = h.drive(fpt.t_rk, ["y", "0", "1", "0.1", "10"], [])
    h.num("Euler at h=0.1 is (1.1)^10", out, "Euler y = ",
          1.1 ** 10, 1e-7)
    h.num("RK2 midpoint at h=0.1 is (1.105)^10", out, "RK2 y = ",
          1.105 ** 10, 1e-7)
    h.num("RK4 at h=0.1 matches e to 1e-5", out, "RK4 y = ", E, 1e-5)
    eu = _num_after(out, "Euler y = ")
    rk = _num_after(out, "RK4 y = ")
    h.truthy("Euler is a few percent out at this step",
             eu is not None and abs(eu - E) / E > 0.04)
    h.truthy("RK4 at the same step is not",
             rk is not None and abs(rk - E) / E < 1e-5)
    h.has("the four RK4 stages are shown", out, "k4 = f(x+h, y+h.k3)")
    h.has("the step-halving comparison is shown", out, "smaller h")

    out = h.drive(fpt.t_rk, ["x", "0", "0", "0.1", "10"], [])
    h.num("RK2 is exact for dy/dx = x", out, "RK2 y = ", 0.5, 1e-12)
    h.num("RK4 is exact for dy/dx = x", out, "RK4 y = ", 0.5, 1e-12)
    h.num("Euler is not", out, "Euler y = ", 0.45, 1e-12)


def test_arc_length(h):
    import fpt

    out = h.drive(fpt.t_arclen, ["x", "0", "1"], [0])
    h.num("straight line arc length", out, "arc length = ", SQRT2, 1e-7)

    out = h.drive(fpt.t_arclen, ["1", "0", "2pi"], [1])
    h.num("polar unit circle", out, "arc length = ", TWOPI, 1e-7)

    out = h.drive(fpt.t_arclen, ["cos(t)", "sin(t)", "0", "2pi"], [2])
    h.num("parametric unit circle", out, "arc length = ", TWOPI, 1e-7)

    out = h.drive(fpt.t_arclen, ["3cos(t)", "3sin(t)", "0", "2pi"], [2])
    h.num("parametric circle of radius 3", out, "arc length = ",
          3.0 * TWOPI, 1e-8)

    out = h.drive(fpt.t_arclen, [], [-1])
    h.check("cancelling the arc length menu shows nothing", out, [])


def test_number_theory(h):
    import fpt

    out = h.drive(fpt.t_totient, ["36"], [])
    h.num("phi(36) = 12", out, "phi(n) = ", 12.0, 1e-12)
    h.has("the distinct primes of 36", out, "distinct primes: 2 3")
    out = h.drive(fpt.t_totient, ["97"], [])
    h.num("phi(97) = 96", out, "phi(n) = ", 96.0, 1e-12)
    h.has("primes are called out", out, "n is prime")
    out = h.drive(fpt.t_totient, ["1"], [])
    h.num("phi(1) = 1", out, "phi(n) = ", 1.0, 1e-12)

    out = h.drive(fpt.t_pythag, ["30"], [])
    h.num("five primitive triples up to c = 30", out, "count = ", 5.0, 1e-12)
    h.has("3-4-5", out, "3, 4, 5")
    h.has("5-12-13", out, "5, 12, 13")
    h.has("8-15-17", out, "8, 15, 17")
    h.has("7-24-25", out, "7, 24, 25")
    h.has("20-21-29", out, "20, 21, 29")
    h.truthy("multiples are excluded",
             not [ln for ln in out if ln.startswith("6, 8, 10")])

    out = h.drive(fpt.t_pythag, ["120"], [])
    h.num("19 primitive triples up to c = 120", out, "count = ", 19.0, 1e-12)
    h.has("the largest one up to 120", out, "15, 112, 113")
    h.has("a middling one", out, "33, 56, 65")
    h.truthy("9*(3,4,5) is not primitive, so it is excluded",
             not [ln for ln in out if ln.startswith("27, 36, 45")])
    h.truthy("9*(5,12,13) is excluded too",
             not [ln for ln in out if ln.startswith("45, 108, 117")])

    out = h.drive(fpt.t_pell, ["2"], [])
    h.num("Pell x for n=2", out, "x = ", 3.0, 1e-12)
    h.num("Pell y for n=2", out, "y = ", 2.0, 1e-12)
    h.num("the solution checks out", out, "check x^2-n y^2 = ", 1.0, 1e-12)
    out = h.drive(fpt.t_pell, ["13"], [])
    h.num("Pell x for n=13", out, "x = ", 649.0, 1e-9)
    h.num("Pell y for n=13", out, "y = ", 180.0, 1e-9)
    out = h.drive(fpt.t_pell, ["61"], [])
    h.num("Pell x for n=61", out, "x = ", 1766319049.0, 1.0)
    h.num("Pell y for n=61", out, "y = ", 226153980.0, 1.0)
    out = h.drive(fpt.t_pell, ["9"], [])
    h.has("perfect squares are rejected", out, "perfect square")

    out = h.drive(fpt.t_fermat, ["7", "3"], [])
    h.num("Fermat's little theorem for p=7, a=3", out,
          "a^(p-1) mod p = ", 1.0, 1e-12)
    h.num("Wilson's theorem for p=7", out, "(p-1)! mod p = ", 6.0, 1e-12)
    h.num("and -1 mod 7 is 6", out, "-1 mod p = ", 6.0, 1e-12)
    h.has("Wilson confirms primality", out, "Wilson holds")
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
