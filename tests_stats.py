def test_chi_df(h):
    import fmstat

    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "0", "5"], [])
    h.num("gof chi^2 = 10", out, "chi^2 = ", 10.0)
    h.num("gof df = 2 when nothing estimated", out, "df = ", 2.0)
    h.num("gof 5% crit on 2 df", out, "crit = ", 5.991, 2e-3)
    h.has("gof rejects", out, "reject H0")

    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "1", "5"], [])
    h.num("df drops to 1 when ONE parameter is estimated", out, "df = ", 1.0)
    h.num("crit follows df to 3.841", out, "crit = ", 3.841, 2e-3)
    h.has("params estimated is reported", out, "params estimated = 1")

    out = h.drive(fmstat.t_chi, ["10 20 30", "20 20 20", "2", "5"], [])
    h.has("df = 0 is refused, not tested", out, "is not >= 1")

    out = h.drive(fmstat.t_chi, ["1 2 3", "2 2 2", "0", "5"], [])
    h.num("small-cell chi^2 = 1", out, "chi^2 = ", 1.0)
    h.has("small expected frequencies are flagged", out, "E<5")

    out = h.drive(fmstat.t_chi, ["19 20 21", "20 20 20", "0", "5"], [])
    h.num("close fit chi^2 = 0.1", out, "chi^2 = ", 0.1)
    h.has("close fit accepts H0", out, "accept H0")


def test_chi_assoc(h):
    import fmstat

    out = h.drive(fmstat.t_assoc, ["2", "2", "20 30", "30 20", "5"], [])
    h.num("2x2 expected frequency is 25", out, "E[1,1] = ", 25.0)
    h.num("2x2 chi^2 = 4", out, "chi^2 = ", 4.0)
    h.num("2x2 df = (r-1)(c-1) = 1", out, "df = (r-1)(c-1) = ", 1.0)
    h.num("2x2 crit on 1 df", out, "crit = ", 3.841, 2e-3)
    h.has("2x2 rejects independence", out, "reject H0")
    h.has("2x2 states the conclusion", out, "evidence of association")
    h.has("2x2 mentions Yates", out, "Yates")

    out = h.drive(fmstat.t_assoc,
                  ["2", "3", "10 20 30", "30 20 10", "5"], [])
    h.num("2x3 expected frequency is 20", out, "E[1,1] = ", 20.0)
    h.num("2x3 chi^2 = 20", out, "chi^2 = ", 20.0)
    h.num("2x3 df = 2", out, "df = (r-1)(c-1) = ", 2.0)
    h.has("2x3 rejects independence", out, "reject H0")

    out = h.drive(fmstat.t_assoc, ["2", "2", "10 20", "20 40", "5"], [])
    h.num("proportional table gives chi^2 = 0", out, "chi^2 = ", 0.0)
    h.has("proportional table accepts H0", out, "accept H0")
    h.has("proportional table says no association", out, "no evidence")

    out = h.drive(fmstat.t_assoc, ["2", "3", "1 2", "3 4 5", "5"], [])
    h.has("wrong row length is refused", out, "expected 3")


def test_chi_dist(h):
    import fmstat
    h.close("chi2 sf at the 1 df 5% point", fmstat._chi2_sf(3.841, 1), 0.05, 1e-4)
    h.close("chi2 sf at the 2 df 5% point", fmstat._chi2_sf(5.991, 2), 0.05, 1e-4)
    h.close("chi2 sf at the 10 df 5% point", fmstat._chi2_sf(18.307, 10), 0.05, 1e-4)
    import math
    h.close("chi2 sf on 2 df is exp(-x/2)",
            fmstat._chi2_sf(2.0, 2), math.exp(-1.0), 1e-9)
    h.close("chi2 crit 1 df 5%", fmstat._chi2_crit(1, 0.05), 3.841, 2e-3)
    h.close("chi2 crit 4 df 5%", fmstat._chi2_crit(4, 0.05), 9.488, 2e-3)
    h.close("chi2 crit 3 df 1%", fmstat._chi2_crit(3, 0.01), 11.345, 2e-3)
    h.close("chi2 crit 6 df 10%", fmstat._chi2_crit(6, 0.10), 10.645, 2e-3)

    h.close("t crit 1 df 5%", fmstat._t_crit(1, 0.05), 6.314, 2e-3)
    h.close("t crit 10 df 5%", fmstat._t_crit(10, 0.05), 1.812, 2e-3)
    h.close("t crit 10 df 2.5%", fmstat._t_crit(10, 0.025), 2.228, 2e-3)
    h.close("t crit 20 df 1%", fmstat._t_crit(20, 0.01), 2.528, 2e-3)
    h.close("t crit 7 df 2.5%", fmstat._t_crit(7, 0.025), 2.365, 2e-3)
    h.close("t sf on 1 df at t=1 is 0.25", fmstat._t_sf(1.0, 1), 0.25, 1e-9)
    h.close("t sf is symmetric at 0", fmstat._t_sf(0.0, 5), 0.5, 1e-12)

    for n, col, a in [(4, 0, 0.05), (10, 0, 0.05), (10, 1, 0.025),
                      (20, 2, 0.01), (30, 3, 0.005)]:
        tc = fmstat._t_crit(n - 2, a)
        want = tc / (tc * tc + n - 2) ** 0.5
        h.close("pmcc table row n=" + str(n) + " col " + str(col),
                fmstat._RCRIT[n - fmstat._RCRIT_MIN][col], want, 1e-4)
    h.close("pmcc crit n=10 5% is 0.5494",
            fmstat._RCRIT[10 - fmstat._RCRIT_MIN][0], 0.5494, 1e-4)
    h.close("pmcc crit n=20 2.5% is 0.4438",
            fmstat._RCRIT[20 - fmstat._RCRIT_MIN][1], 0.4438, 1e-4)
    h.close("spearman crit n=10 5% is 0.5636",
            fmstat._SCRIT[10 - fmstat._SCRIT_MIN][0], 0.5636, 1e-4)
    h.close("spearman crit n=7 1% is 0.8929",
            fmstat._SCRIT[7 - fmstat._SCRIT_MIN][2], 0.8929, 1e-4)
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


def test_continuous_rv(h):
    import fmstat

    out = h.drive(fmstat.t_pdf, ["3x^2", "0", "1"], [])
    h.num("integral of the pdf is 1", out, "int f dx = ", 1.0)
    h.has("3x^2 on [0,1] is a valid pdf", out, "valid pdf: YES")
    h.num("E(X) is 3/4", out, "E(X) = ", 0.75)
    h.num("E(X^2) is 3/5", out, "E(X^2) = ", 0.6)
    h.num("Var is 3/80", out, "Var(X) = ", 0.0375)
    h.num("SD is sqrt(3/80)", out, "SD = ", 0.193649, 1e-4)

    out = h.drive(fmstat.t_cdf, ["3x^2", "0", "1", "0.5"], [])
    h.has("cdf is found symbolically as x^3", out, "F(x) = x^3")
    h.num("median is the cube root of 0.5", out, "median = ", 0.793701, 1e-4)
    h.num("Q1 is the cube root of 0.25", out, "Q1 = ", 0.629961, 1e-4)
    h.num("Q3 is the cube root of 0.75", out, "Q3 = ", 0.908560, 1e-4)
    h.num("F(0.5) = 0.5^3 = 0.125", out, "F(0.5) = ", 0.125, 1e-4)
    h.num("P(X>0.5) = 1 - 0.125", out, "P(X>t) = ", 0.875, 1e-4)

    out = h.drive(fmstat.t_pdfmode, ["3x^2", "0", "1"], [])
    h.num("mode of 3x^2 on [0,1] is at x = 1", out, "mode = ", 1.0, 1e-3)
    h.num("f at the mode is 3", out, "f(mode) = ", 3.0, 1e-3)
    h.has("the mode is reported as an endpoint", out, "endpoint")

    out = h.drive(fmstat.t_pdf, ["(3/4)(1-x^2)", "-1", "1"], [])
    h.has("(3/4)(1-x^2) is a valid pdf", out, "valid pdf: YES")
    h.num("symmetric pdf has E(X) = 0", out, "E(X) = ", 0.0, 1e-6)
    h.num("E(X^2) is 1/5", out, "E(X^2) = ", 0.2, 1e-6)
    h.num("Var is 1/5", out, "Var(X) = ", 0.2, 1e-6)
    out = h.drive(fmstat.t_pdfmode, ["(3/4)(1-x^2)", "-1", "1"], [])
    h.num("interior mode is at x = 0", out, "mode = ", 0.0, 1e-3)
    h.num("f at the interior mode is 0.75", out, "f(mode) = ", 0.75, 1e-4)
    h.has("interior mode is labelled as such", out, "interior")
    out = h.drive(fmstat.t_cdf, ["(3/4)(1-x^2)", "-1", "1", None], [])
    h.num("symmetric pdf has median 0", out, "median = ", 0.0, 1e-4)

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

    out = h.drive(fmstat.t_pdf, ["x", "0", "1"], [])
    h.num("integral of x on [0,1] is 0.5", out, "int f dx = ", 0.5)
    h.has("x on [0,1] is rejected as a pdf", out, "valid pdf: NO")
    h.has("the reason given is the integral", out, "integral is not 1")

    out = h.drive(fmstat.t_pdf, ["x-0.5", "0", "2"], [])
    h.num("x-0.5 on [0,2] does integrate to 1", out, "int f dx = ", 1.0)
    h.has("but it is still rejected", out, "valid pdf: NO")
    h.has("the reason given is negativity", out, "which is < 0")

    out = h.drive(fmstat.t_pdf, ["3x^2", "1", "0"], [])
    h.has("reversed limits are refused", out, "Need b > a")


def test_piecewise_pdf(h):
    import fmstat

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

    out = h.drive(fmstat.t_pdfpw,
                  ["2", "1/4", "0", "1", "1/4", "1", "2"], [])
    h.num("piecewise integral is 0.5", out, "int f dx = ", 0.5, 1e-6)
    h.has("piecewise non-pdf is rejected", out, "valid pdf: NO")

    out = h.drive(fmstat.t_pdfpw,
                  ["2", "x", "0", "1", "2-x", "1.5", "2"], [])
    h.has("a gap between pieces is refused", out, "must join up")

    out = h.drive(fmstat.t_pdfpw,
                  ["3", "1/4", "0", "1", "1/2", "1", "2", "1/4", "2", "3"], [])
    h.has("three-piece pdf is valid", out, "valid pdf: YES")
    h.num("three-piece E(X) = 1.5", out, "E(X) = ", 1.5, 1e-6)
    h.num("three-piece E(X^2) = 34/12", out, "E(X^2) = ", 34.0 / 12.0, 1e-4)
    h.num("three-piece Var = 7/12", out, "Var(X) = ", 7.0 / 12.0, 1e-4)
    h.num("three-piece median = 1.5", out, "median = ", 1.5, 1e-4)


def test_linear_combinations(h):
    import fmstat

    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", None], [])
    h.num("E(2X-3Y+1) = 6", out, "E(W) = ", 6.0)
    h.num("Var(2X-3Y+1) = 97", out, "Var(W) = ", 97.0)
    h.num("SD(W) = sqrt(97)", out, "SD(W) = ", 9.848858, 1e-4)
    h.num("E(X+Y) = 15", out, "E(X+Y) = ", 15.0)
    h.num("E(X-Y) = 5", out, "E(X-Y) = ", 5.0)
    h.num("Var(X+Y) = 13", out, "Var(X+Y) = ", 13.0)
    h.num("Var(X-Y) = 13, NOT 4 - 9", out, "Var(X-Y) = ", 13.0)
    h.has("the difference variance ADDS", out, "Var(X-Y) ADDS")
    h.has("independence is stated", out, "INDEPENDENT")
    h.has("negative coefficient prints as a subtraction", out, "- 3Y")

    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", "6"], [])
    h.num("P(W < mean) = 0.5", out, "P(W<w) = ", 0.5, 1e-4)
    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "2", "-3", "1", "15.848858"], [])
    h.num("P(W < mean + 1sd) = 0.8413", out, "P(W<w) = ", 0.841345, 1e-4)

    out = h.drive(fmstat.t_lincomb,
                  ["10", "4", "5", "9", "3", "0", "2", None], [])
    h.num("E(3X+2) = 32", out, "E(W) = ", 32.0)
    h.num("Var(3X+2) = 36", out, "Var(W) = ", 36.0)


def test_n_copies(h):
    import fmstat

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

    out = h.drive(fmstat.t_nsum, ["10", "4", "1"], [])
    h.num("n=1 gives Var(nX) = 4", out, "Var(nX) = ", 4.0)
    h.num("n=1 gives Var(sum) = 4", out, "Var(sum) = ", 4.0)


def test_correlation_tests(h):
    import fmstat

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "5", "1"], [])
    h.num("Sxy = 6", out, "Sxy = ", 6.0)
    h.num("Sxx = 10", out, "Sxx = ", 10.0)
    h.num("Syy = 6", out, "Syy = ", 6.0)
    h.num("r = 6/sqrt(60)", out, "r = ", 0.774597, 1e-4)
    h.num("r^2 = 0.6", out, "r^2 = ", 0.6, 1e-4)
    h.num("crit r at n=5, 5% one-tail", out, "crit r = ", 0.8054, 1e-4)
    h.has("r below the critical value accepts H0", out, "accept H0")
    h.num("t statistic agrees with r", out, "t = ", 2.121320, 1e-4)

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "5", "3"], [])
    h.num("two-tail 5% uses the 2.5% column", out, "crit r = ", 0.8783, 1e-4)
    h.has("two-tail states the level used", out, "one-tail level used = 2.5")

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 6 8 10", "5", "1"], [])
    h.num("perfect correlation gives r = 1", out, "r = ", 1.0)
    h.has("perfect correlation is significant", out, "REJECT H0")

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "10 8 6 4 2", "5", "2"], [])
    h.num("negative perfect correlation", out, "r = ", -1.0)
    h.has("lower tail rejects", out, "REJECT H0")
    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "10 8 6 4 2", "5", "1"], [])
    h.has("upper tail on negative data accepts", out, "accept H0")

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", "7", "1"], [])
    h.has("an untabulated level is reported", out, "No table column")

    out = h.drive(fmstat.t_pmcc, ["1 2 3 4 5", "2 4 5 4 5", None], [])
    h.num("r is still reported with no test", out, "r = ", 0.774597, 1e-4)


def test_spearman_test(h):
    import fmstat

    out = h.drive(fmstat.t_spear, ["1 2 3 4 5", "2 4 5 4 5", "5", "1"], [])
    h.num("rs = 7/sqrt(90)", out, "rs = ", 0.737865, 1e-4)
    h.num("crit rs at n=5, 5% one-tail is 0.9", out, "crit rs = ", 0.9, 1e-4)
    h.has("rs below the critical value accepts", out, "accept H0")
    h.has("ties are flagged", out, "there are ties")

    out = h.drive(fmstat.t_spear, ["1 2 3 4 5", "1 4 9 16 25", "5", "1"], [])
    h.num("monotone data gives rs = 1", out, "rs = ", 1.0, 1e-9)
    h.has("rs = 1 is significant at n=5", out, "REJECT H0")
    h.has("untied data is not flagged for ties", out, "crit rs = ")
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

    out = h.drive(fmstat.t_spear,
                  ["1 2 3 4 5 6", "6 5 4 3 2 1", "5", "2"], [])
    h.num("reversed ranks give rs = -1", out, "rs = ", -1.0, 1e-9)
    h.num("crit rs at n=6 is 0.8286", out, "crit rs = ", 0.8286, 1e-4)
    h.has("reversed ranks reject on the lower tail", out, "REJECT H0")

    out = h.drive(fmstat.t_spear, ["1 2 3 4", "1 2 3 4", "5", "3"], [])
    h.has("an unreachable level is reported", out, "unreachable")

    xs = []
    i = 0
    while i < 40:
        xs.append(str(i + 1))
        i += 1
    s = " ".join(xs)
    out = h.drive(fmstat.t_spear, [s, s, "5", "1"], [])
    h.has("n beyond the table is reported", out, "outside the")


def test_misc_distributions(h):
    import fmstat

    out = h.drive(fmstat.t_geom, ["0.25", "3"], [])
    h.num("geometric P(X=3)", out, "P(X=r) = ", 0.140625, 1e-4)
    h.num("geometric P(X<=3)", out, "P(X<=r) = ", 0.578125, 1e-4)
    h.num("geometric P(X>3)", out, "P(X>r) = ", 0.421875, 1e-4)
    h.num("geometric mean 1/p", out, "mean 1/p = ", 4.0)
    h.num("geometric variance", out, "var (1-p)/p^2 = ", 12.0)

    out = h.drive(fmstat.t_dunif, ["1", "6"], [])
    h.num("die P(X=x) = 1/6", out, "P(X=x) = 1/n = ", 1.0 / 6.0, 1e-4)
    h.num("die mean 3.5", out, "mean (a+b)/2 = ", 3.5)
    h.num("die variance 35/12", out, "var (n^2-1)/12 = ", 35.0 / 12.0, 1e-4)

    out = h.drive(fmstat.t_pois, ["4", "2"], [])
    h.num("poisson mean is mu", out, "mean = ", 4.0)
    h.num("poisson variance is mu", out, "variance = ", 4.0)
    h.num("poisson SD is sqrt(mu)", out, "SD = ", 2.0)

    out = h.drive(fmstat.t_bin, ["100", "0.02", "1"], [])
    h.num("binomial mean np = 2", out, "mean np = ", 2.0, 1e-9)
    h.has("the Poisson approximation is offered", out, "Poisson")
    import math
    h.num("Poisson approx P(X=1) = 2e^-2", out, "Pois P(X=k) = ",
          2.0 * math.exp(-2.0), 1e-4)
    out = h.drive(fmstat.t_bin, ["10", "0.5", "5"], [])
    h.num("binomial pmf is unchanged", out, "P(X=k) = ", 0.246094, 1e-4)
    miss = True
    for ln in out:
        if "Pois" in ln:
            miss = False
    h.truthy("no Poisson approximation when p = 0.5", miss)


def test_regression_extras(h):
    import fmstat

    out = h.drive(fmstat.t_reg, ["1 2 3 4 5", "2 4 5 4 5", None], [])
    h.num("y on x gradient", out, "b = ", 0.6, 1e-9)
    h.num("y on x intercept", out, "a = ", 2.2, 1e-9)
    h.num("r^2 of the fit", out, "r^2 = ", 0.6, 1e-9)
    h.num("x on y gradient", out, "d = ", 1.0, 1e-9)
    h.num("x on y intercept", out, "c = ", -1.0, 1e-9)
    h.num("residual sum of squares", out, "sum of e^2 = ", 2.4, 1e-6)
    h.has("both lines pass through the means point", out, "means point (3, 4)")
    h.has("guidance on which line to use", out, "x on y to predict x")

    out = h.drive(fmstat.t_reg, ["1 2 3 4 5", "2 4 5 4 5", "6"], [])
    h.num("prediction at x = 6", out, "y=", 5.8, 1e-9)


def test_t_interval(h):
    import fmstat

    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", None], [])
    h.num("t interval mean", out, "mean = ", 5.0)
    h.num("t interval s (n-1)", out, "s (n-1) = ", 2.138090, 1e-4)
    h.num("t interval SE", out, "SE = s/sqrt(n) = ", 0.755929, 1e-4)
    h.num("t interval df", out, "df = ", 7.0)
    h.num("t* on 7 df at 95%", out, "t* = ", 2.364624, 1e-4)
    h.num("t interval margin", out, "mean +/- ", 1.787460, 1e-4)

    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", "5"], [])
    h.has("mu0 at the mean is inside", out, "mu0 inside the interval")
    h.num("t statistic is 0 at mu0 = mean", out, "t = ", 0.0, 1e-9)
    out = h.drive(fmstat.t_tint, ["2 4 4 4 5 5 7 9", "95", "8"], [])
    h.has("mu0 = 8 is outside the interval", out, "mu0 outside the interval")

    out = h.drive(fmstat.t_tint, ["1 2 3 4 5", "95", None], [])
    h.num("paired mean difference", out, "mean = ", 3.0)
    h.num("paired s", out, "s (n-1) = ", 1.581139, 1e-4)
    h.num("paired t*", out, "t* = ", 2.776445, 1e-4)
    h.num("paired margin", out, "mean +/- ", 1.963243, 1e-4)


def test_normal_plot(h):
    import fmstat
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


def test_tree_bayes(h):
    import stat640

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

    out = h.drive(stat640.t_tree, ["0.3", "0.5", "0.5"], [])
    h.num("independent case P(B) = 0.5", out, "P(B) = ", 0.5, 1e-9)
    h.num("independent case P(A|B) = P(A)", out, "P(A|B) = ", 0.3, 1e-9)
    h.has("independence is detected", out, "INDEPENDENT")

    out = h.drive(stat640.t_tree, ["1.5", "0.5", "0.5"], [])
    h.has("an impossible probability is refused", out, "Need 0 <= P(A) <= 1")


def test_sampling(h):
    import stat640

    out = h.drive(stat640.t_stratsamp, ["200 300 500", "50"], [])
    h.has("stratum 1 takes 10", out, "N=200 -> 10")
    h.has("stratum 2 takes 15", out, "N=300 -> 15")
    h.has("stratum 3 takes 25", out, "N=500 -> 25")
    h.num("the allocation totals n", out, "total allocated = ", 50.0)
    h.num("sampling fraction n/N", out, "sampling fraction = ", 0.05, 1e-9)
    h.num("systematic interval k = N/n", out, "k = N/n = ", 20.0, 1e-9)

    out = h.drive(stat640.t_stratsamp, ["7 11 13", "10"], [])
    h.has("largest remainder goes to stratum 2", out, "N=11 -> 4")
    h.num("the allocation still totals n", out, "total allocated = ", 10.0)

    out = h.drive(stat640.t_stratsamp, ["5 5", "20"], [])
    h.has("oversized sample is refused", out, "bigger than the")

    for k, needle in [("1", "Simple random"), ("2", "Systematic"),
                      ("3", "Stratified"), ("4", "Cluster"),
                      ("5", "Quota"), ("6", "Opportunity")]:
        out = h.drive(stat640.t_sampling, [k], [])
        h.has("sampling card " + k + " names " + needle, out, needle)
        h.has("sampling card " + k + " covers bias", out, "Bias")
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
