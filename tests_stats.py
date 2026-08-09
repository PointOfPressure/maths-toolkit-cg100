# tests_stats.py - correctness tests for the statistics work: the chi-squared
# degrees-of-freedom fix, continuous random variables, linear combinations of
# random variables, the contingency-table test, the correlation tests, and the
# H640 sampling / tree-diagram reference tools.
#
# Picked up automatically by tests.py through the tests_*.py hook; each section
# function takes the harness as its only argument.
#
# Every expected value below is worked out by hand in the comment above it.
# "It does not crash" is not a test: each assertion is a number or a decision
# that a wrong implementation would get wrong.


# =========================================================== chi-squared ====
def test_chi_df(h):
    import fmstat

    # O = 10, 20, 30 against E = 20, 20, 20:
    #   chi^2 = 100/20 + 0/20 + 100/20 = 5 + 0 + 5 = 10
    # With 3 cells and NO estimated parameters, df = 3 - 1 - 0 = 2.
    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "0", "5"], [])
    h.num("gof chi^2 = 10", out, "chi^2 = ", 10.0)
    h.num("gof df = 2 when nothing estimated", out, "df = ", 2.0)
    # 5% critical value on 2 df is 5.991 (standard chi-squared table)
    h.num("gof 5% crit on 2 df", out, "crit = ", 5.991, 2e-3)
    h.has("gof rejects", out, "reject H0")

    # THE BUG. The old code computed df = cells - 1 unconditionally. Fitting one
    # parameter from the data (a Poisson mean, a binomial p) costs a degree of
    # freedom, so df must be 3 - 1 - 1 = 1, not 2. This assertion FAILS against
    # the old behaviour, which reported df = 2 here.
    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "1", "5"], [])
    h.num("df drops to 1 when ONE parameter is estimated", out, "df = ", 1.0)
    h.num("crit follows df to 3.841", out, "crit = ", 3.841, 2e-3)
    h.has("params estimated is reported", out, "params estimated = 1")

    # Two estimated parameters on 3 cells leaves df = 0, which is not a test at
    # all. The old code would have carried on and quoted the df = 2 critical
    # value; the fixed code refuses.
    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "2", "5"], [])
    h.has("df = 0 is refused, not tested", out, "is not >= 1")

    # Expected frequencies below 5 make the chi-squared approximation poor.
    # E = 2, 2, 2 sums to 6 with O = 1, 2, 3: chi^2 = 1/2 + 0 + 1/2 = 1.
    out = h.drive(fmstat.t_chi, ["1 2 3", "2 2 2", "0", "5"], [])
    h.num("small-cell chi^2 = 1", out, "chi^2 = ", 1.0)
    h.has("small expected frequencies are flagged", out, "E<5")

    # A goodness-of-fit test that should ACCEPT: O = 19, 20, 21 vs E = 20 each
    # gives chi^2 = 1/20 + 0 + 1/20 = 0.1, well under 5.991 on 2 df.
    out = h.drive(fmstat.t_chi, ["19 20 21", "20 20 20", "0", "5"], [])
    h.num("close fit chi^2 = 0.1", out, "chi^2 = ", 0.1)
    h.has("close fit accepts H0", out, "accept H0")


def test_chi_assoc(h):
    import fmstat

    # 2x2 table   20 30 | row 50
    #             30 20 | row 50
    #        col  50 50 | total 100
    # Every expected value is 50*50/100 = 25, so
    #   chi^2 = 4 * (5^2 / 25) = 4 * 1 = 4,  df = (2-1)(2-1) = 1.
    # 4 > 3.841 so this REJECTS.
    # Note the flat goodness-of-fit tool on the same four cells would use
    # df = 4 - 1 = 3, critical value 7.815, and would ACCEPT - the wrong
    # answer. That is exactly the gap this tool closes.
    out = h.drive(fmstat.t_assoc, ["2", "2", "20 30", "30 20", "5"], [])
    h.num("2x2 expected frequency is 25", out, "E[1,1] = ", 25.0)
    h.num("2x2 chi^2 = 4", out, "chi^2 = ", 4.0)
    h.num("2x2 df = (r-1)(c-1) = 1", out, "df = (r-1)(c-1) = ", 1.0)
    h.num("2x2 crit on 1 df", out, "crit = ", 3.841, 2e-3)
    h.has("2x2 rejects independence", out, "reject H0")
    h.has("2x2 states the conclusion", out, "evidence of association")
    h.has("2x2 mentions Yates", out, "Yates")

    # 2x3 table   10 20 30 | row 60
    #             30 20 10 | row 60
    #        col  40 40 40 | total 120
    # Every expected value is 60*40/120 = 20, so
    #   chi^2 = 100/20 + 0 + 100/20 + 100/20 + 0 + 100/20 = 5+5+5+5 = 20
    #   df = (2-1)(3-1) = 2
    out = h.drive(fmstat.t_assoc,
                  ["2", "3", "10 20 30", "30 20 10", "5"], [])
    h.num("2x3 expected frequency is 20", out, "E[1,1] = ", 20.0)
    h.num("2x3 chi^2 = 20", out, "chi^2 = ", 20.0)
    h.num("2x3 df = 2", out, "df = (r-1)(c-1) = ", 2.0)
    h.has("2x3 rejects independence", out, "reject H0")

    # A table with NO association: rows are exact multiples of each other, so
    # every observed equals its expected and chi^2 is exactly 0.
    #   10 20 | 30        E[1,1] = 30*30/90 = 10
    #   20 40 | 60        E[1,2] = 30*60/90 = 20
    #   30 60 | 90
    out = h.drive(fmstat.t_assoc, ["2", "2", "10 20", "20 40", "5"], [])
    h.num("proportional table gives chi^2 = 0", out, "chi^2 = ", 0.0)
    h.has("proportional table accepts H0", out, "accept H0")
    h.has("proportional table says no association", out, "no evidence")

    # a ragged row must be rejected rather than silently reshaped
    out = h.drive(fmstat.t_assoc, ["2", "3", "1 2", "3 4 5", "5"], [])
    h.has("wrong row length is refused", out, "expected 3")


def test_chi_dist(h):
    import fmstat
    # The chi-squared survivor function against published critical values:
    # P(X > 3.841) = 0.05 on 1 df, P(X > 5.991) = 0.05 on 2 df, and
    # P(X > 18.307) = 0.05 on 10 df (standard chi-squared tables).
    h.close("chi2 sf at the 1 df 5% point", fmstat._chi2_sf(3.841, 1), 0.05, 1e-4)
    h.close("chi2 sf at the 2 df 5% point", fmstat._chi2_sf(5.991, 2), 0.05, 1e-4)
    h.close("chi2 sf at the 10 df 5% point", fmstat._chi2_sf(18.307, 10), 0.05, 1e-4)
    # P(X > x) on 2 df is exactly exp(-x/2): at x = 2 that is exp(-1).
    import math
    h.close("chi2 sf on 2 df is exp(-x/2)",
            fmstat._chi2_sf(2.0, 2), math.exp(-1.0), 1e-9)
    # inverting it must return the published critical values
    h.close("chi2 crit 1 df 5%", fmstat._chi2_crit(1, 0.05), 3.841, 2e-3)
    h.close("chi2 crit 4 df 5%", fmstat._chi2_crit(4, 0.05), 9.488, 2e-3)
    h.close("chi2 crit 3 df 1%", fmstat._chi2_crit(3, 0.01), 11.345, 2e-3)
    h.close("chi2 crit 6 df 10%", fmstat._chi2_crit(6, 0.10), 10.645, 2e-3)

    # Student t against published one-tail critical values
    h.close("t crit 1 df 5%", fmstat._t_crit(1, 0.05), 6.314, 2e-3)
    h.close("t crit 10 df 5%", fmstat._t_crit(10, 0.05), 1.812, 2e-3)
    h.close("t crit 10 df 2.5%", fmstat._t_crit(10, 0.025), 2.228, 2e-3)
    h.close("t crit 20 df 1%", fmstat._t_crit(20, 0.01), 2.528, 2e-3)
    h.close("t crit 7 df 2.5%", fmstat._t_crit(7, 0.025), 2.365, 2e-3)
    # a t on 1 df is Cauchy, so P(T > 1) = 1/4 exactly
    h.close("t sf on 1 df at t=1 is 0.25", fmstat._t_sf(1.0, 1), 0.25, 1e-9)
    h.close("t sf is symmetric at 0", fmstat._t_sf(0.0, 5), 0.5, 1e-12)

    # The embedded pmcc table must agree with the identity it was built from,
    # r = t / sqrt(t^2 + n - 2) on n - 2 degrees of freedom. Checked at both
    # ends of the table and at a middle row.
    for n, col, a in [(4, 0, 0.05), (10, 0, 0.05), (10, 1, 0.025),
                      (20, 2, 0.01), (30, 3, 0.005)]:
        tc = fmstat._t_crit(n - 2, a)
        want = tc / (tc * tc + n - 2) ** 0.5
        h.close("pmcc table row n=" + str(n) + " col " + str(col),
                fmstat._RCRIT[n - fmstat._RCRIT_MIN][col], want, 1e-4)
    # spot values against the printed pmcc table
    h.close("pmcc crit n=10 5% is 0.5494",
            fmstat._RCRIT[10 - fmstat._RCRIT_MIN][0], 0.5494, 1e-4)
    h.close("pmcc crit n=20 2.5% is 0.4438",
            fmstat._RCRIT[20 - fmstat._RCRIT_MIN][1], 0.4438, 1e-4)
    # spot values against the printed Spearman table
    h.close("spearman crit n=10 5% is 0.5636",
            fmstat._SCRIT[10 - fmstat._SCRIT_MIN][0], 0.5636, 1e-4)
    h.close("spearman crit n=7 1% is 0.8929",
            fmstat._SCRIT[7 - fmstat._SCRIT_MIN][2], 0.8929, 1e-4)
    # both tables must be monotone decreasing in n at every level: a bigger
    # sample can only make it easier to reach significance
    for tab, name in [(fmstat._RCRIT, "pmcc"), (fmstat._SCRIT, "spearman")]:
        ok = True
        col = 0
        while col < 4:
            i = 1
            while i < len(tab):
                a = tab[i - 1][col]
                b = tab[i][col]
                if a is not None and b is not None and b > a + 1e-12:
                    ok = False
                i += 1
            col += 1
        h.truthy(name + " table decreases as n grows", ok)


# ============================================== continuous random variables =
def test_continuous_rv(h):
    import fmstat

    # f(x) = 3x^2 on [0, 1].
    #   int 3x^2 dx = x^3, so int over [0,1] = 1 -> it IS a pdf
    #   E(X)   = int 3x^3 = 3/4 x^4 |0..1 = 3/4  = 0.75
    #   E(X^2) = int 3x^4 = 3/5 x^5 |0..1 = 3/5  = 0.6
    #   Var    = 3/5 - (3/4)^2 = 3/5 - 9/16 = 48/80 - 45/80 = 3/80 = 0.0375
    #   SD     = sqrt(3/80) = 0.19365
    out = h.drive(fmstat.t_pdf, ["3x^2", "0", "1"], [])
    h.num("integral of the pdf is 1", out, "int f dx = ", 1.0)
    h.has("3x^2 on [0,1] is a valid pdf", out, "valid pdf: YES")
    h.num("E(X) is 3/4", out, "E(X) = ", 0.75)
    h.num("E(X^2) is 3/5", out, "E(X^2) = ", 0.6)
    h.num("Var is 3/80", out, "Var(X) = ", 0.0375)
    h.num("SD is sqrt(3/80)", out, "SD = ", 0.193649, 1e-4)

    # The cdf of the same pdf is F(x) = x^3 on [0,1], so
    #   median  = 0.5^(1/3)  = 0.793701
    #   Q1      = 0.25^(1/3) = 0.629961
    #   Q3      = 0.75^(1/3) = 0.908560
    #   F(0.5)  = 0.125
    out = h.drive(fmstat.t_cdf, ["3x^2", "0", "1", "0.5"], [])
    h.has("cdf is found symbolically as x^3", out, "F(x) = x^3")
    h.num("median is the cube root of 0.5", out, "median = ", 0.793701, 1e-4)
    h.num("Q1 is the cube root of 0.25", out, "Q1 = ", 0.629961, 1e-4)
    h.num("Q3 is the cube root of 0.75", out, "Q3 = ", 0.908560, 1e-4)
    h.num("F(0.5) = 0.5^3 = 0.125", out, "F(0.5) = ", 0.125, 1e-4)
    h.num("P(X>0.5) = 1 - 0.125", out, "P(X>t) = ", 0.875, 1e-4)

    # 3x^2 increases on [0,1], so its mode is the right endpoint x = 1 with
    # f(1) = 3. There is no interior stationary point at all, which is why the
    # mode is found by maximising rather than by solving f'(x) = 0.
    out = h.drive(fmstat.t_pdfmode, ["3x^2", "0", "1"], [])
    h.num("mode of 3x^2 on [0,1] is at x = 1", out, "mode = ", 1.0, 1e-3)
    h.num("f at the mode is 3", out, "f(mode) = ", 3.0, 1e-3)
    h.has("the mode is reported as an endpoint", out, "endpoint")

    # f(x) = (3/4)(1 - x^2) on [-1, 1] - a symmetric pdf with an INTERIOR mode.
    #   int = (3/4)[x - x^3/3] from -1 to 1 = (3/4)(2 - 2/3) = (3/4)(4/3) = 1
    #   E(X) = 0 by symmetry
    #   E(X^2) = (3/4) * 2 * (1/3 - 1/5) = (3/2)(2/15) = 1/5 = 0.2
    #   Var = 0.2 - 0 = 0.2
    #   mode at x = 0 with f(0) = 3/4 = 0.75
    out = h.drive(fmstat.t_pdf, ["(3/4)(1-x^2)", "-1", "1"], [])
    h.has("(3/4)(1-x^2) is a valid pdf", out, "valid pdf: YES")
    h.num("symmetric pdf has E(X) = 0", out, "E(X) = ", 0.0, 1e-6)
    h.num("E(X^2) is 1/5", out, "E(X^2) = ", 0.2, 1e-6)
    h.num("Var is 1/5", out, "Var(X) = ", 0.2, 1e-6)
    out = h.drive(fmstat.t_pdfmode, ["(3/4)(1-x^2)", "-1", "1"], [])
    h.num("interior mode is at x = 0", out, "mode = ", 0.0, 1e-3)
    h.num("f at the interior mode is 0.75", out, "f(mode) = ", 0.75, 1e-4)
    h.has("interior mode is labelled as such", out, "interior")
    # by symmetry the median of this pdf is 0
    out = h.drive(fmstat.t_cdf, ["(3/4)(1-x^2)", "-1", "1", None], [])
    h.num("symmetric pdf has median 0", out, "median = ", 0.0, 1e-4)

    # A uniform pdf on [2, 6]: f(x) = 1/4.
    #   E(X) = (a+b)/2 = 4, Var = (b-a)^2/12 = 16/12 = 4/3 = 1.33333
    #   median = 4, Q1 = 3, Q3 = 5
    out = h.drive(fmstat.t_pdf, ["1/4", "2", "6"], [])
    h.has("uniform on [2,6] is a valid pdf", out, "valid pdf: YES")
    h.num("uniform mean is 4", out, "E(X) = ", 4.0, 1e-6)
    h.num("uniform variance is 4/3", out, "Var(X) = ", 4.0 / 3.0, 1e-4)
    out = h.drive(fmstat.t_cdf, ["1/4", "2", "6", None], [])
    h.num("uniform median is 4", out, "median = ", 4.0, 1e-4)
    h.num("uniform Q1 is 3", out, "Q1 = ", 3.0, 1e-4)
    h.num("uniform Q3 is 5", out, "Q3 = ", 5.0, 1e-4)


def test_pdf_validity(h):
    import fmstat

    # f(x) = x on [0, 1] integrates to 1/2, NOT 1, so it is not a pdf.
    out = h.drive(fmstat.t_pdf, ["x", "0", "1"], [])
    h.num("integral of x on [0,1] is 0.5", out, "int f dx = ", 0.5)
    h.has("x on [0,1] is rejected as a pdf", out, "valid pdf: NO")
    h.has("the reason given is the integral", out, "integral is not 1")

    # f(x) = x - 0.5 on [0, 2] DOES integrate to 1:
    #   [x^2/2 - x/2] from 0 to 2 = (2 - 1) - 0 = 1
    # but it is negative on [0, 0.5), so it is still not a pdf. A check that
    # only tested the integral would wave this through.
    out = h.drive(fmstat.t_pdf, ["x-0.5", "0", "2"], [])
    h.num("x-0.5 on [0,2] does integrate to 1", out, "int f dx = ", 1.0)
    h.has("but it is still rejected", out, "valid pdf: NO")
    h.has("the reason given is negativity", out, "which is < 0")

    # b <= a must be refused rather than producing a negative "probability"
    out = h.drive(fmstat.t_pdf, ["3x^2", "1", "0"], [])
    h.has("reversed limits are refused", out, "Need b > a")


def test_piecewise_pdf(h):
    import fmstat

    # Triangular pdf: f(x) = x on [0,1] and f(x) = 2 - x on [1,2].
    #   int = 1/2 + [2x - x^2/2] from 1 to 2 = 1/2 + (2 - 1.5) = 1  -> valid
    #   E(X) = int_0^1 x^2 + int_1^2 x(2-x)
    #        = 1/3 + [x^2 - x^3/3] from 1 to 2
    #        = 1/3 + ((4 - 8/3) - (1 - 1/3)) = 1/3 + (4/3 - 2/3) = 1
    #   E(X^2) = int_0^1 x^3 + int_1^2 x^2(2-x)
    #        = 1/4 + [2x^3/3 - x^4/4] from 1 to 2
    #        = 1/4 + ((16/3 - 4) - (2/3 - 1/4)) = 1/4 + 11/12 = 7/6 = 1.16667
    #   Var = 7/6 - 1 = 1/6 = 0.166667,  SD = 0.408248
    #   median = 1 by symmetry
    #   Q1: on [0,1] F(x) = x^2/2, so x^2/2 = 1/4 gives x = sqrt(0.5) = 0.707107
    #   Q3 = 2 - 0.707107 = 1.292893 by symmetry
    out = h.drive(fmstat.t_pdfpw,
                  ["2", "x", "0", "1", "2-x", "1", "2"], [])
    h.num("triangular pdf integrates to 1", out, "int f dx = ", 1.0, 1e-6)
    h.has("triangular pdf is valid", out, "valid pdf: YES")
    h.num("triangular E(X) = 1", out, "E(X) = ", 1.0, 1e-6)
    h.num("triangular E(X^2) = 7/6", out, "E(X^2) = ", 7.0 / 6.0, 1e-4)
    h.num("triangular Var = 1/6", out, "Var(X) = ", 1.0 / 6.0, 1e-4)
    h.num("triangular SD", out, "SD = ", 0.408248, 1e-4)
    h.num("triangular median = 1", out, "median = ", 1.0, 1e-4)
    h.num("triangular Q1 = sqrt(0.5)", out, "Q1 = ", 0.707107, 1e-4)
    h.num("triangular Q3 = 2 - sqrt(0.5)", out, "Q3 = ", 1.292893, 1e-4)

    # Two-piece uniform that is NOT a pdf: 1/4 on [0,1] then 1/4 on [1,2]
    # integrates to 1/2.
    out = h.drive(fmstat.t_pdfpw,
                  ["2", "1/4", "0", "1", "1/4", "1", "2"], [])
    h.num("piecewise integral is 0.5", out, "int f dx = ", 0.5, 1e-6)
    h.has("piecewise non-pdf is rejected", out, "valid pdf: NO")

    # Pieces that do not join up are a user error and must be reported, not
    # silently integrated over a gap.
    out = h.drive(fmstat.t_pdfpw,
                  ["2", "x", "0", "1", "2-x", "1.5", "2"], [])
    h.has("a gap between pieces is refused", out, "must join up")

    # A three-piece pdf: 1/4 on [0,1], 1/2 on [1,2], 1/4 on [2,3].
    #   int = 1/4 + 1/2 + 1/4 = 1  -> valid
    #   E(X) = 1/4*(1/2) + 1/2*(3/2) + 1/4*(5/2) = 0.125 + 0.75 + 0.625 = 1.5
    #   E(X^2) = int x^2/4 (0..1) + int x^2/2 (1..2) + int x^2/4 (2..3)
    #          = (1/4)(1/3) + (1/2)(7/3) + (1/4)(19/3)
    #          = 1/12 + 7/6 + 19/12 = 1/12 + 14/12 + 19/12 = 34/12 = 2.833333
    #   Var = 34/12 - 2.25 = 2.833333 - 2.25 = 0.583333
    #   median = 1.5 by symmetry
    out = h.drive(fmstat.t_pdfpw,
                  ["3", "1/4", "0", "1", "1/2", "1", "2", "1/4", "2", "3"], [])
    h.has("three-piece pdf is valid", out, "valid pdf: YES")
    h.num("three-piece E(X) = 1.5", out, "E(X) = ", 1.5, 1e-6)
    h.num("three-piece E(X^2) = 34/12", out, "E(X^2) = ", 34.0 / 12.0, 1e-4)
    h.num("three-piece Var = 7/12", out, "Var(X) = ", 7.0 / 12.0, 1e-4)
    h.num("three-piece median = 1.5", out, "median = ", 1.5, 1e-4)


# ============================================ linear combinations of rvs ====
def test_linear_combinations(h):
    import fmstat

    # X has E = 10, Var = 4; Y has E = 5, Var = 9; W = 2X - 3Y + 1.
    #   E(W)   = 2(10) - 3(5) + 1 = 20 - 15 + 1 = 6
    #   Var(W) = 2^2(4) + (-3)^2(9) = 16 + 81 = 97
    #   SD(W)  = sqrt(97) = 9.848858
    # and the sum and difference:
    #   E(X+Y) = 15, E(X-Y) = 5, and BOTH have variance 4 + 9 = 13.
    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", None], [])
    h.num("E(2X-3Y+1) = 6", out, "E(W) = ", 6.0)
    h.num("Var(2X-3Y+1) = 97", out, "Var(W) = ", 97.0)
    h.num("SD(W) = sqrt(97)", out, "SD(W) = ", 9.848858, 1e-4)
    h.num("E(X+Y) = 15", out, "E(X+Y) = ", 15.0)
    h.num("E(X-Y) = 5", out, "E(X-Y) = ", 5.0)
    # both the sum and the difference have variance 4 + 9 = 13. These are
    # asserted separately, under their own labels: a single shared "Var = "
    # label let a wrong Var(X-Y) hide behind the correct Var(X+Y).
    h.num("Var(X+Y) = 13", out, "Var(X+Y) = ", 13.0)
    h.num("Var(X-Y) = 13, NOT 4 - 9", out, "Var(X-Y) = ", 13.0)
    h.has("the difference variance ADDS", out, "Var(X-Y) ADDS")
    h.has("independence is stated", out, "INDEPENDENT")
    # the coefficients must print with real signs, not "+ -3Y"
    h.has("negative coefficient prints as a subtraction", out, "- 3Y")

    # P(W < w) with W ~ N(6, 97): at w = 6 the answer is exactly 0.5, and at
    # one standard deviation above, w = 6 + sqrt(97) = 15.848858, it is 0.8413.
    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", "6"], [])
    h.num("P(W < mean) = 0.5", out, "P(W<w) = ", 0.5, 1e-4)
    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", "15.848858"], [])
    h.num("P(W < mean + 1sd) = 0.8413", out, "P(W<w) = ", 0.841345, 1e-4)

    # E(a + bX) and Var(a + bX) fall out by setting b = 0: with X as above and
    # W = 3X + 0Y + 2, E = 32 and Var = 9*4 = 36.
    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "3", "0", "2", None], [])
    h.num("E(3X+2) = 32", out, "E(W) = ", 32.0)
    h.num("Var(3X+2) = 36", out, "Var(W) = ", 36.0)


def test_n_copies(h):
    import fmstat

    # X has E = 10, Var = 4, and n = 5. The distinction students lose marks on:
    #   nX      : E = 5(10) = 50, Var = 5^2(4) = 100, SD = 10
    #   X1+..+X5: E = 5(10) = 50, Var = 5(4)   = 20,  SD = sqrt(20) = 4.472136
    #   Xbar    : E = 10,         Var = 4/5    = 0.8, SD = 0.894427
    # Same mean, different variance - the ratio of the variances is n.
    out = h.drive(fmstat.t_nsum, ["10", "4", "5"], [])
    h.num("E(nX) = 50", out, "E(nX) = nE(X) = ", 50.0)
    h.num("Var(nX) = n^2 Var(X) = 100", out, "Var(nX) = ", 100.0)
    h.num("SD(nX) = 10", out, "SD(nX) = ", 10.0)
    h.num("E(sum) = 50, the same mean", out, "E(sum) = nE(X) = ", 50.0)
    h.num("Var(sum) = n Var(X) = 20", out, "Var(sum) = ", 20.0)
    h.num("SD(sum) = sqrt(20)", out, "SD(sum) = ", 4.472136, 1e-4)
    h.num("the variances differ by a factor n", out,
          "ratio Var(nX)/Var(sum) = ", 5.0)
    h.num("E(Xbar) = 10", out, "E(Xbar) = ", 10.0)
    h.num("Var(Xbar) = Var(X)/n = 0.8", out, "Var(Xbar) = Var(X)/n = ", 0.8)
    h.num("SD(Xbar)", out, "SD(Xbar) = ", 0.894427, 1e-4)
    h.has("the tool says which one it is doing", out, "ONE X, scaled")
    h.has("and names the other", out, "n INDEP")

    # n = 1 collapses the two: Var(1*X) = Var(X1) = 4.
    out = h.drive(fmstat.t_nsum, ["10", "4", "1"], [])
    h.num("n=1 gives Var(nX) = 4", out, "Var(nX) = ", 4.0)
    h.num("n=1 gives Var(sum) = 4", out, "Var(sum) = ", 4.0)


# ============================================== correlation hypothesis tests =
def test_correlation_tests(h):
    import fmstat

    # x = 1,2,3,4,5 and y = 2,4,5,4,5.
    #   sum x = 15, sum y = 20, sum xy = 2+8+15+16+25 = 66
    #   Sxy = 66 - 15*20/5 = 6
    #   sum x^2 = 55, Sxx = 55 - 225/5 = 10
    #   sum y^2 = 86, Syy = 86 - 400/5 = 6
    #   r = 6 / sqrt(10*6) = 6/sqrt(60) = 0.774597,  r^2 = 0.6
    # With n = 5 the one-tail 5% critical value is 0.8054, and 0.7746 < 0.8054,
    # so this does NOT reach significance despite looking like a strong r.
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "5", "1"], [])
    h.num("Sxy = 6", out, "Sxy = ", 6.0)
    h.num("Sxx = 10", out, "Sxx = ", 10.0)
    h.num("Syy = 6", out, "Syy = ", 6.0)
    h.num("r = 6/sqrt(60)", out, "r = ", 0.774597, 1e-4)
    h.num("r^2 = 0.6", out, "r^2 = ", 0.6, 1e-4)
    h.num("crit r at n=5, 5% one-tail", out, "crit r = ", 0.8054, 1e-4)
    h.has("r below the critical value accepts H0", out, "accept H0")
    # the equivalent t statistic: t = r sqrt((n-2)/(1-r^2))
    #   = 0.774597 * sqrt(3/0.4) = 0.774597 * 2.738613 = 2.121320
    h.num("t statistic agrees with r", out, "t = ", 2.121320, 1e-4)

    # A two-tail test at 5% uses the 2.5% one-tail column: 0.8783 at n = 5.
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "5", "3"], [])
    h.num("two-tail 5% uses the 2.5% column", out, "crit r = ", 0.8783, 1e-4)
    h.has("two-tail states the level used", out, "one-tail level used = 2.5")

    # Perfect positive correlation, n = 5: r = 1 >= 0.8054, so REJECT.
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 6 8 10", "5", "1"], [])
    h.num("perfect correlation gives r = 1", out, "r = ", 1.0)
    h.has("perfect correlation is significant", out, "REJECT H0")

    # Perfect negative correlation with a lower-tail alternative: r = -1 and
    # the rule is reject if r <= -0.8054.
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "10 8 6 4 2", "5", "2"], [])
    h.num("negative perfect correlation", out, "r = ", -1.0)
    h.has("lower tail rejects", out, "REJECT H0")
    # ...but a POSITIVE one-tail test on the same data must NOT reject
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "10 8 6 4 2", "5", "1"], [])
    h.has("upper tail on negative data accepts", out, "accept H0")

    # A significance level with no table column must say so rather than guess.
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "7", "1"], [])
    h.has("an untabulated level is reported", out, "No table column")

    # Skipping the test still reports r (the pre-existing behaviour).
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", None], [])
    h.num("r is still reported with no test", out, "r = ", 0.774597, 1e-4)


def test_spearman_test(h):
    import fmstat

    # Same data: x = 1,2,3,4,5 and y = 2,4,5,4,5.
    # Ranks of x are 1,2,3,4,5. For y = 2,4,5,4,5 the sorted values are
    # 2,4,4,5,5, so rank(2) = 1, the two 4s share ranks 2 and 3 -> 2.5, and the
    # two 5s share ranks 4 and 5 -> 4.5. So ry = 1, 2.5, 4.5, 2.5, 4.5.
    #   sum rx*ry = 1 + 5 + 13.5 + 10 + 22.5 = 52
    #   sum rx = 15, sum ry = 15, Sxy = 52 - 15*15/5 = 7
    #   Sxx = 55 - 45 = 10
    #   sum ry^2 = 1 + 6.25 + 20.25 + 6.25 + 20.25 = 54, Syy = 54 - 45 = 9
    #   rs = 7 / sqrt(90) = 0.737865
    # The n = 5 one-tail 5% critical value is 0.9, so this accepts H0.
    out = h.drive(fmstat.t_spear, ["1 2 3 4 5", "2 4 5 4 5", "5", "1"], [])
    h.num("rs = 7/sqrt(90)", out, "rs = ", 0.737865, 1e-4)
    h.num("crit rs at n=5, 5% one-tail is 0.9", out, "crit rs = ", 0.9, 1e-4)
    h.has("rs below the critical value accepts", out, "accept H0")
    h.has("ties are flagged", out, "there are ties")

    # Perfectly monotone but NOT linear data: rs = 1 exactly while r < 1.
    # x = 1,2,3,4,5 and y = 1,4,9,16,25 (y = x^2) is strictly increasing, so
    # every rank matches and rs = 1. At n = 5, 5% one-tail crit 0.9 -> reject.
    out = h.drive(fmstat.t_spear, ["1 2 3 4 5", "1 4 9 16 25", "5", "1"], [])
    h.num("monotone data gives rs = 1", out, "rs = ", 1.0, 1e-9)
    h.has("rs = 1 is significant at n=5", out, "REJECT H0")
    h.has("untied data is not flagged for ties", out, "crit rs = ")
    # and the pmcc on the same data is strictly less than 1, which is the whole
    # reason Spearman exists
    out2 = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "1 4 9 16 25", None], [])
    got = None
    for ln in out2:
        p = ln.find("r = ")
        if p >= 0:
            try:
                got = float(ln[p + 4:])
            except:
                pass
    h.truthy("pmcc on curved data is below 1 while rs = 1",
             got is not None and got < 0.9999)

    # n = 6, perfectly reversed ranks: rs = -1, lower-tail 5% crit -0.8286.
    out = h.drive(fmstat.t_spear,
                  ["1 2 3 4 5 6", "6 5 4 3 2 1", "5", "2"], [])
    h.num("reversed ranks give rs = -1", out, "rs = ", -1.0, 1e-9)
    h.num("crit rs at n=6 is 0.8286", out, "crit rs = ", 0.8286, 1e-4)
    h.has("reversed ranks reject on the lower tail", out, "REJECT H0")

    # n = 4 has no 2.5% one-tail point at all (only 24 rankings exist, so the
    # smallest achievable one-tail probability is 1/24 = 0.0417). The tool must
    # say the level is unreachable rather than invent a critical value.
    out = h.drive(fmstat.t_spear, ["1 2 3 4", "1 2 3 4", "5", "3"], [])
    h.has("an unreachable level is reported", out, "unreachable")

    # n = 40 is off the end of the table and must be reported as such.
    xs = []
    i = 0
    while i < 40:
        xs.append(str(i + 1))
        i += 1
    s = " ".join(xs)
    out = h.drive(fmstat.t_spear, [s, s, "5", "1"], [])
    h.has("n beyond the table is reported", out, "outside the")


# ================================================== other closed audit gaps =
def test_misc_distributions(h):
    import fmstat

    # Geometric with p = 0.25 and r = 3:
    #   P(X=3)  = 0.75^2 * 0.25 = 0.5625 * 0.25 = 0.140625
    #   P(X<=3) = 1 - 0.75^3 = 1 - 0.421875 = 0.578125
    #   P(X>3)  = 0.421875
    #   mean = 1/0.25 = 4,  var = 0.75/0.0625 = 12,  SD = sqrt(12) = 3.464102
    out = h.drive(fmstat.t_geom, ["0.25", "3"], [])
    h.num("geometric P(X=3)", out, "P(X=r) = ", 0.140625, 1e-4)
    h.num("geometric P(X<=3)", out, "P(X<=r) = ", 0.578125, 1e-4)
    h.num("geometric P(X>3)", out, "P(X>r) = ", 0.421875, 1e-4)
    h.num("geometric mean 1/p", out, "mean 1/p = ", 4.0)
    h.num("geometric variance", out, "var (1-p)/p^2 = ", 12.0)

    # Discrete uniform on 1..6 (a fair die):
    #   P(X=x) = 1/6 = 0.166667, mean = 3.5, var = (36-1)/12 = 35/12 = 2.916667
    out = h.drive(fmstat.t_dunif, ["1", "6"], [])
    h.num("die P(X=x) = 1/6", out, "P(X=x) = 1/n = ", 1.0 / 6.0, 1e-4)
    h.num("die mean 3.5", out, "mean (a+b)/2 = ", 3.5)
    h.num("die variance 35/12", out, "var (n^2-1)/12 = ", 35.0 / 12.0, 1e-4)

    # Poisson mean and variance are both mu (mu = 4 here), which the audit
    # flagged as never printed.
    out = h.drive(fmstat.t_pois, ["4", "2"], [])
    h.num("poisson mean is mu", out, "mean = ", 4.0)
    h.num("poisson variance is mu", out, "variance = ", 4.0)
    h.num("poisson SD is sqrt(mu)", out, "SD = ", 2.0)

    # Binomial with n = 100, p = 0.02 meets the n>=50, p<=0.1 rule, so the
    # Poisson approximation with mu = np = 2 is offered.
    #   exact  P(X=1) = C(100,1) 0.02 * 0.98^99 = 0.270606
    #   Poisson P(X=1) = 2 e^-2 = 0.270671
    out = h.drive(fmstat.t_bin, ["100", "0.02", "1"], [])
    h.num("binomial mean np = 2", out, "mean np = ", 2.0, 1e-9)
    h.has("the Poisson approximation is offered", out, "Poisson")
    import math
    h.num("Poisson approx P(X=1) = 2e^-2", out, "Pois P(X=k) = ",
          2.0 * math.exp(-2.0), 1e-4)
    # ...and is NOT offered when the conditions fail (n = 10, p = 0.5)
    out = h.drive(fmstat.t_bin, ["10", "0.5", "5"], [])
    h.num("binomial pmf is unchanged", out, "P(X=k) = ", 0.246094, 1e-4)
    miss = True
    for ln in out:
        if "Pois" in ln:
            miss = False
    h.truthy("no Poisson approximation when p = 0.5", miss)


def test_regression_extras(h):
    import fmstat

    # x = 1,2,3,4,5 and y = 2,4,5,4,5 again (Sxy = 6, Sxx = 10, Syy = 6).
    #   y on x: b = Sxy/Sxx = 0.6, a = ybar - b xbar = 4 - 0.6*3 = 2.2
    #   x on y: d = Sxy/Syy = 1.0, c = xbar - d ybar = 3 - 1*4 = -1
    #   r^2 = 0.6
    # Residuals from y = 2.2 + 0.6x at x = 1..5 are
    #   2 - 2.8 = -0.8, 4 - 3.4 = 0.6, 5 - 4.0 = 1.0, 4 - 4.6 = -0.6,
    #   5 - 5.2 = -0.2, and their squares sum to
    #   0.64 + 0.36 + 1.0 + 0.36 + 0.04 = 2.4
    out = h.drive(fmstat.t_reg, ["1 2 3 4 5", "2 4 5 4 5", None], [])
    h.num("y on x gradient", out, "b = ", 0.6, 1e-9)
    h.num("y on x intercept", out, "a = ", 2.2, 1e-9)
    h.num("r^2 of the fit", out, "r^2 = ", 0.6, 1e-9)
    h.num("x on y gradient", out, "d = ", 1.0, 1e-9)
    h.num("x on y intercept", out, "c = ", -1.0, 1e-9)
    h.num("residual sum of squares", out, "sum of e^2 = ", 2.4, 1e-6)
    h.has("both lines pass through the means point", out, "means point (3, 4)")
    h.has("guidance on which line to use", out, "x on y to predict x")

    # prediction at x = 6 is 2.2 + 0.6*6 = 5.8
    out = h.drive(fmstat.t_reg, ["1 2 3 4 5", "2 4 5 4 5", "6"], [])
    h.num("prediction at x = 6", out, "y=", 5.8, 1e-9)


def test_t_interval(h):
    import fmstat

    # data 2,4,4,4,5,5,7,9: n = 8, sum = 40, mean = 5.
    #   deviations -3,-1,-1,-1,0,0,2,4 -> squares 9,1,1,1,0,0,4,16, sum 32
    #   s^2 = 32/7 = 4.571429, s = 2.138090
    #   SE = s/sqrt(8) = 0.755929
    #   df = 7, t* at 2.5% one-tail = 2.364624
    #   margin = 2.364624 * 0.755929 = 1.787460
    #   interval = (3.212540, 6.787460)
    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", None], [])
    h.num("t interval mean", out, "mean = ", 5.0)
    h.num("t interval s (n-1)", out, "s (n-1) = ", 2.138090, 1e-4)
    h.num("t interval SE", out, "SE = s/sqrt(n) = ", 0.755929, 1e-4)
    h.num("t interval df", out, "df = ", 7.0)
    h.num("t* on 7 df at 95%", out, "t* = ", 2.364624, 1e-4)
    h.num("t interval margin", out, "mean +/- ", 1.787460, 1e-4)

    # mu0 = 5 is the sample mean, so it is inside any interval and t = 0.
    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", "5"], [])
    h.has("mu0 at the mean is inside", out, "mu0 inside the interval")
    h.num("t statistic is 0 at mu0 = mean", out, "t = ", 0.0, 1e-9)
    # mu0 = 8 is outside (3.2125, 6.7875), so it must be rejected.
    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", "8"], [])
    h.has("mu0 = 8 is outside the interval", out, "mu0 outside the interval")

    # A paired example: differences 1,2,3,4,5 have mean 3, s = 1.581139,
    # SE = 0.707107, df = 4, t* at 2.5% = 2.776445, margin = 1.963243.
    out = h.drive(fmstat.t_tint, ["1 2 3 4 5", "95", None], [])
    h.num("paired mean difference", out, "mean = ", 3.0)
    h.num("paired s", out, "s (n-1) = ", 1.581139, 1e-4)
    h.num("paired t*", out, "t* = ", 2.776445, 1e-4)
    h.num("paired margin", out, "mean +/- ", 1.963243, 1e-4)


def test_normal_plot(h):
    import fmstat
    # Data that is exactly a linear function of the normal scores must plot as
    # a perfect straight line, so r = 1. Using the tool's own scores
    # z_i = invphi((i-0.5)/5) and taking the data to be 10 + 2 z_i does that.
    zs = []
    i = 0
    while i < 5:
        zs.append(10.0 + 2.0 * h.casutil.invphi((i + 0.5) / 5.0))
        i += 1
    parts = []
    for v in zs:
        parts.append(repr(v))
    out = h.drive(fmstat.t_normplot, [" ".join(parts)], [])
    h.num("a perfectly normal sample plots straight", out, "r of plot = ",
          1.0, 1e-6)
    h.num("the slope recovers the sd", out, "slope ~ sd = ", 2.0, 1e-6)
    h.num("the intercept recovers the mean", out, "intercept ~ mean = ",
          10.0, 1e-6)
    h.has("a straight plot supports the model", out, "Normal looks reasonable")

    # A strongly skewed sample must not look straight: r drops well below 1.
    out = h.drive(fmstat.t_normplot, ["1 1 1 1 1 1 1 1 2 40"], [])
    got = None
    for ln in out:
        p = ln.find("r of plot = ")
        if p >= 0:
            try:
                got = float(ln[p + 12:])
            except:
                pass
    h.truthy("a skewed sample gives a curved plot",
             got is not None and got < 0.95)


# ================================================== H640 leftovers (stat640) =
def test_tree_bayes(h):
    import stat640

    # P(A) = 0.3, P(B|A) = 0.8, P(B|A') = 0.4. Multiplying along the branches:
    #   P(A and B)   = 0.3 * 0.8 = 0.24
    #   P(A and B')  = 0.3 * 0.2 = 0.06
    #   P(A' and B)  = 0.7 * 0.4 = 0.28
    #   P(A' and B') = 0.7 * 0.6 = 0.42     (these four sum to 1)
    # Adding across: P(B) = 0.24 + 0.28 = 0.52, P(B') = 0.48.
    # Reversing by Bayes:
    #   P(A|B)  = 0.24/0.52 = 0.4615385
    #   P(A'|B) = 0.28/0.52 = 0.5384615
    #   P(A|B') = 0.06/0.48 = 0.125
    out = h.drive(stat640.t_tree, ["0.3", "0.8", "0.4"], [])
    h.num("P(A and B)", out, "P(A and B)   = ", 0.24, 1e-9)
    h.num("P(A and B')", out, "P(A and B')  = ", 0.06, 1e-9)
    h.num("P(A' and B)", out, "P(A' and B)  = ", 0.28, 1e-9)
    h.num("P(A' and B')", out, "P(A' and B') = ", 0.42, 1e-9)
    h.num("the four branches sum to 1", out, "these four sum to ", 1.0, 1e-9)
    h.num("P(B) by the law of total probability", out, "P(B) = ", 0.52, 1e-9)
    h.num("P(A|B) by Bayes", out, "P(A|B) = ", 0.4615385, 1e-5)
    h.num("P(A'|B) by Bayes", out, "P(A'|B) = ", 0.5384615, 1e-5)
    h.num("P(A|B') by Bayes", out, "P(A|B') = ", 0.125, 1e-9)
    h.has("dependence is detected", out, "NOT independent")

    # When P(B|A) = P(B|A') the events are independent and P(A|B) = P(A).
    # With P(A) = 0.3 and both conditionals 0.5: P(B) = 0.5 and
    # P(A|B) = 0.15/0.5 = 0.3 = P(A).
    out = h.drive(stat640.t_tree, ["0.3", "0.5", "0.5"], [])
    h.num("independent case P(B) = 0.5", out, "P(B) = ", 0.5, 1e-9)
    h.num("independent case P(A|B) = P(A)", out, "P(A|B) = ", 0.3, 1e-9)
    h.has("independence is detected", out, "INDEPENDENT")

    # A probability outside [0,1] must be refused.
    out = h.drive(stat640.t_tree, ["1.5", "0.5", "0.5"], [])
    h.has("an impossible probability is refused", out, "Need 0 <= P(A) <= 1")


def test_sampling(h):
    import stat640

    # Proportional allocation: strata 200, 300, 500 (N = 1000) with n = 50
    # gives 50*200/1000 = 10, 50*300/1000 = 15, 50*500/1000 = 25, total 50.
    out = h.drive(stat640.t_stratsamp, ["200 300 500", "50"], [])
    h.has("stratum 1 takes 10", out, "N=200 -> 10")
    h.has("stratum 2 takes 15", out, "N=300 -> 15")
    h.has("stratum 3 takes 25", out, "N=500 -> 25")
    h.num("the allocation totals n", out, "total allocated = ", 50.0)
    h.num("sampling fraction n/N", out, "sampling fraction = ", 0.05, 1e-9)
    h.num("systematic interval k = N/n", out, "k = N/n = ", 20.0, 1e-9)

    # A case where naive rounding does NOT total n: strata 7, 11, 13 (N = 31)
    # with n = 10 gives exact shares 2.258, 3.548, 4.194. Rounding each to the
    # nearest whole number gives 2 + 4 + 4 = 10 here, but taking floors gives
    # 2 + 3 + 4 = 9, so one place is handed to the largest remainder (0.548,
    # the second stratum) -> 2, 4, 4. The total must be exactly 10.
    out = h.drive(stat640.t_stratsamp, ["7 11 13", "10"], [])
    h.has("largest remainder goes to stratum 2", out, "N=11 -> 4")
    h.num("the allocation still totals n", out, "total allocated = ", 10.0)

    # A sample bigger than the population is impossible.
    out = h.drive(stat640.t_stratsamp, ["5 5", "20"], [])
    h.has("oversized sample is refused", out, "bigger than the")

    # The reference card: each numbered method returns its own description,
    # and each must say something about bias.
    for k, needle in [("1", "Simple random"), ("2", "Systematic"),
                      ("3", "Stratified"), ("4", "Cluster"),
                      ("5", "Quota"), ("6", "Opportunity")]:
        out = h.drive(stat640.t_sampling, [k], [])
        h.has("sampling card " + k + " names " + needle, out, needle)
        h.has("sampling card " + k + " covers bias", out, "Bias")
    # 0 lists them all and separates the random methods from the rest
    out = h.drive(stat640.t_sampling, ["0"], [])
    h.has("the index lists quota", out, "Quota")
    h.has("the index warns which are not random", out, "not random")


SECTIONS = [
    ("chi-squared degrees of freedom", test_chi_df),
    ("chi-squared association", test_chi_assoc),
    ("chi-squared and t distributions", test_chi_dist),
    ("continuous random variables", test_continuous_rv),
    ("pdf validity", test_pdf_validity),
    ("piecewise pdfs", test_piecewise_pdf),
    ("linear combinations of rvs", test_linear_combinations),
    ("nX versus X1+..+Xn", test_n_copies),
    ("pmcc hypothesis test", test_correlation_tests),
    ("Spearman hypothesis test", test_spearman_test),
    ("geometric/uniform/Poisson extras", test_misc_distributions),
    ("regression extras", test_regression_extras),
    ("t confidence interval", test_t_interval),
    ("normal probability plot", test_normal_plot),
    ("tree diagrams and Bayes", test_tree_bayes),
    ("sampling methods", test_sampling),
]
