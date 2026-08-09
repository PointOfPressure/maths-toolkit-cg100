def _layout_rows(h, fn, inputs=(), menus=()):
    rows = []

    def rec(x, y, s, c=None, size=None):
        rows.append((x, y, str(s), size or 'medium'))

    real = h.casui.draw_string
    h.casui.draw_string = rec
    try:
        h.drive(fn, inputs, menus)
    finally:
        h.casui.draw_string = real
    return rows


def _check_layout(h, label, rows):
    h.truthy(label + ": draws something", len(rows) > 0)
    over = []
    off = []
    for x, y, s, size in rows:
        if x < 0 or x + h.casui.text_w(s, size) > 384:
            over.append((x, s))
        if y < 0 or y > 191:
            off.append((y, s))
    h.check(label + ": every string fits the 384px width", over, [])
    h.check(label + ": every string is on screen vertically", off, [])
    clash = []
    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows):
            xa, ya, sa, za = rows[i]
            xb, yb, sb, zb = rows[j]
            if abs(ya - yb) <= 6:
                ea = xa + h.casui.text_w(sa, za)
                eb = xb + h.casui.text_w(sb, zb)
                if xa < eb and xb < ea:
                    clash.append((sa, sb, ya, yb))
            j += 1
        i += 1
    h.check(label + ": no two strings overprint", clash, [])


def test_venn2(h):
    import stat640
    out = h.drive(stat640.t_venn, ["30", "12", "15", "5"], [0])
    h.num("venn2 A only", out, "n(A only) = ", 7.0)
    h.num("venn2 overlap", out, "n(A and B) = ", 5.0)
    h.num("venn2 B only", out, "n(B only) = ", 10.0)
    h.num("venn2 neither", out, "n(neither) = ", 8.0)
    h.num("venn2 regions sum to the total", out, "regions sum = ", 30.0)
    h.num("venn2 P(A)", out, "P(A) = ", 12.0 / 30.0)
    h.num("venn2 P(B)", out, "P(B) = ", 15.0 / 30.0)
    h.num("venn2 P(A and B)", out, "P(A and B) = ", 5.0 / 30.0)
    h.num("venn2 P(A or B)", out, "P(A or B) = ", 22.0 / 30.0)
    h.num("venn2 P(A')", out, "P(A') = ", 18.0 / 30.0)
    h.num("venn2 P(A|B)", out, "P(A|B) = ", 1.0 / 3.0)
    h.num("venn2 P(B|A)", out, "P(B|A) = ", 5.0 / 12.0)
    h.num("venn2 P(A)P(B)", out, "P(A)P(B) = ", 0.2)
    h.has("venn2 not independent", out, "A,B independent: NO")
    h.has("venn2 not mutually exclusive", out, "mutually exclusive: NO")

    out = h.drive(stat640.t_venn, ["20", "10", "8", "4"], [0])
    h.num("venn2 independent P(A and B)", out, "P(A and B) = ", 0.2)
    h.num("venn2 independent P(A)P(B)", out, "P(A)P(B) = ", 0.2)
    h.has("venn2 independent verdict", out, "A,B independent: YES")
    h.has("venn2 independent is not exclusive", out, "mutually exclusive: NO")

    out = h.drive(stat640.t_venn, ["50", "20", "15", "0"], [0])
    h.num("venn2 exclusive union", out, "P(A or B) = ", 0.7)
    h.num("venn2 exclusive neither", out, "n(neither) = ", 15.0)
    h.has("venn2 exclusive verdict", out, "mutually exclusive: YES")
    h.has("venn2 exclusive is not independent", out, "A,B independent: NO")


def test_venn2_rejects(h):
    import stat640
    out = h.drive(stat640.t_venn, ["30", "20", "15", "2"], [0])
    h.has("venn2 says the counts do not add up", out, "DO NOT ADD UP")
    h.has("venn2 names the impossible region", out, "neither")
    h.has("venn2 reports what is needed", out, "33")
    rows = _layout_rows(h, stat640.t_venn, ["30", "20", "15", "2"], [0])
    h.check("venn2 draws no diagram when the counts fail", rows, [])
    out = h.drive(stat640.t_venn, ["30", "5", "15", "9"], [0])
    h.has("venn2 rejects an overlap bigger than A", out, "DO NOT ADD UP")
    out = h.drive(stat640.t_venn, ["30", "-5", "15", "2"], [0])
    h.has("venn2 rejects a negative count", out, "cannot be negative")
    out = h.drive(stat640.t_venn, ["0"], [0])
    h.has("venn2 rejects a zero total", out, "total > 0")


def test_venn3(h):
    import stat640
    out = h.drive(stat640.t_venn,
                  ["100", "50 40 30", "20 15 10", "5"], [1])
    h.num("venn3 A only", out, "n(A only) = ", 20.0)
    h.num("venn3 B only", out, "n(B only) = ", 15.0)
    h.num("venn3 C only", out, "n(C only) = ", 10.0)
    h.num("venn3 A and B only", out, "n(A and B only) = ", 15.0)
    h.num("venn3 A and C only", out, "n(A and C only) = ", 10.0)
    h.num("venn3 B and C only", out, "n(B and C only) = ", 5.0)
    h.num("venn3 all three", out, "n(all three) = ", 5.0)
    h.num("venn3 none", out, "n(none) = ", 20.0)
    h.num("venn3 eight regions sum to the total", out, "regions sum = ", 100.0)
    h.num("venn3 P(A)", out, "P(A) = ", 0.5)
    h.num("venn3 P(B)", out, "P(B) = ", 0.4)
    h.num("venn3 P(C)", out, "P(C) = ", 0.3)
    h.num("venn3 P(A and B)", out, "P(A and B) = ", 0.2)
    h.num("venn3 P(A and C)", out, "P(A and C) = ", 0.15)
    h.num("venn3 P(B and C)", out, "P(B and C) = ", 0.1)
    h.num("venn3 P(A and B and C)", out, "P(A and B and C) = ", 0.05)
    h.num("venn3 P(A or B)", out, "P(A or B) = ", 0.7)
    h.num("venn3 P(A or B or C)", out, "P(A or B or C) = ", 0.8)
    h.num("venn3 P(C')", out, "P(C') = ", 0.7)
    h.num("venn3 P(A|B)", out, "P(A|B) = ", 0.5)
    h.has("venn3 A,B independent", out, "A,B independent: YES")
    h.has("venn3 A,C independent", out, "A,C independent: YES")
    h.has("venn3 B,C not independent", out, "B,C independent: NO")
    h.has("venn3 not mutually exclusive", out, "mutually exclusive: NO")

    out = h.drive(stat640.t_venn, ["60", "30 20 5", "0 0 0", "0"], [1])
    h.num("venn3 exclusive none", out, "n(none) = ", 5.0)
    h.num("venn3 exclusive union", out, "P(A or B or C) = ", 55.0 / 60.0)
    h.has("venn3 exclusive verdict", out, "mutually exclusive: YES")

    out = h.drive(stat640.t_venn,
                  ["100", "50 40 30", "20 15 10", "25"], [1])
    h.has("venn3 rejects a triple bigger than a pair", out, "DO NOT ADD UP")
    h.has("venn3 names the impossible region", out, "A and B only")
    out = h.drive(stat640.t_venn, ["100", "50 40", "20 15 10", "5"], [1])
    h.has("venn3 needs three single counts", out, "exactly 3")


def test_venn_layout(h):
    import stat640
    rows = _layout_rows(h, stat640.t_venn, ["30", "12", "15", "5"], [0])
    _check_layout(h, "venn 2 events", rows)
    got = []
    for x, y, s, size in rows:
        got.append(s)
    h.check("venn2 label set", _sortstrs(got),
            _sortstrs(["Venn diagram: A, B", "n = 30", "A", "B",
                       "7", "5", "10", "8"]))
    rows = _layout_rows(h, stat640.t_venn,
                        ["100", "50 40 30", "20 15 10", "5"], [1])
    _check_layout(h, "venn 3 events", rows)
    got = []
    for x, y, s, size in rows:
        got.append(s)
    h.check("venn3 label set", _sortstrs(got),
            _sortstrs(["Venn diagram: A, B, C", "n = 100", "A", "B", "C",
                       "20", "15", "10", "15", "10", "5", "5", "20"]))
    rows = _layout_rows(h, stat640.t_venn,
                        ["1000", "500 400 300", "200 150 100", "50"], [1])
    _check_layout(h, "venn 3 events, 3-digit counts", rows)


def _sortstrs(a):
    b = list(a)
    i = 1
    while i < len(b):
        k = b[i]
        j = i - 1
        while j >= 0 and b[j] > k:
            b[j + 1] = b[j]
            j -= 1
        b[j + 1] = k
        i += 1
    return b


def test_loglin_fit(h):
    import math
    import stat640
    res = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 0)
    h.truthy("log-log fit succeeds", res is not None)
    tx, ty, ia, grad, r = res
    h.close("log-log recovers n = 2", grad, 2.0, 1e-9)
    h.close("log-log recovers ln a = ln 3", ia, math.log(3.0), 1e-9)
    h.close("log-log recovers a = 3", math.exp(ia), 3.0, 1e-9)
    h.close("log-log r = 1 on exact data", r, 1.0, 1e-9)
    h.close("log-log transforms x to ln x", tx[1], math.log(2.0), 1e-12)
    h.close("log-log transforms y to ln y", ty[1], math.log(12.0), 1e-12)

    res = stat640._loglin([0.0, 1.0, 2.0, 3.0], [5.0, 10.0, 20.0, 40.0], 1)
    h.truthy("semi-log fit succeeds", res is not None)
    tx, ty, ia, grad, r = res
    h.close("semi-log gradient is ln b = ln 2", grad, math.log(2.0), 1e-9)
    h.close("semi-log recovers b = 2", math.exp(grad), 2.0, 1e-9)
    h.close("semi-log recovers a = 5", math.exp(ia), 5.0, 1e-9)
    h.close("semi-log r = 1 on exact data", r, 1.0, 1e-9)
    h.close("semi-log leaves x alone", tx[2], 2.0, 1e-12)

    a = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 0)
    b = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 1)
    h.truthy("log-log and semi-log differ on the same data",
             abs(a[3] - b[3]) > 0.1)

    h.check("log-log refuses x <= 0",
            stat640._loglin([0.0, 1.0, 2.0], [1.0, 2.0, 4.0], 0), None)
    h.check("log-log refuses y <= 0",
            stat640._loglin([1.0, 2.0, 3.0], [1.0, -2.0, 4.0], 0), None)
    h.check("semi-log refuses y <= 0",
            stat640._loglin([1.0, 2.0, 3.0], [1.0, 0.0, 4.0], 1), None)


def test_loglin_tool(h):
    import math
    import stat640
    out = h.drive(stat640.t_loglin,
                  ["1 2 3 4", "3 12 27 48", None], [0])
    h.num("t_loglin points", out, "points n = ", 4.0)
    h.num("t_loglin gradient", out, "gradient = ", 2.0)
    h.num("t_loglin intercept", out, "intercept = ", math.log(3.0))
    h.num("t_loglin power n", out, "power n = gradient = ", 2.0)
    h.num("t_loglin a", out, "a = e^intercept = ", 3.0)
    h.has("t_loglin states the original model", out, "y = 3 x^2")
    h.has("t_loglin states the log form", out, "ln y = ln a + n ln x")
    h.num("t_loglin r", out, "r = ", 1.0)
    h.has("t_loglin says what r measures", out, "STRAIGHTENED")
    h.has("t_loglin says what r does not measure", out, "NOT the fit of the")

    out = h.drive(stat640.t_loglin,
                  ["1 2 3 4", "3 12 27 48", "5"], [0])
    h.num("t_loglin predicts from the original curve", out, "y = ", 75.0)

    out = h.drive(stat640.t_loglin,
                  ["0 1 2 3", "5 10 20 40", "4"], [1])
    h.num("t_loglin semi-log base b", out, "base b = e^gradient = ", 2.0)
    h.num("t_loglin semi-log a", out, "a = e^intercept = ", 5.0)
    h.has("t_loglin semi-log model", out, "y = 5 * 2^x")
    h.has("t_loglin semi-log log form", out, "ln y = ln a + x ln b")
    h.num("t_loglin semi-log prediction", out, "y = ", 80.0)

    out = h.drive(stat640.t_loglin, ["1 2 3 4", "2 6 10 16", None], [0])
    ok = [0]
    for ln in out:
        p = ln.find("r = ")
        if p == 0:
            v = float(ln[4:])
            if 0.9 < v < 1.0:
                ok[0] = 1
    h.check("t_loglin r is below 1 on inexact data", ok[0], 1)

    out = h.drive(stat640.t_loglin, ["1 2 3", "1 2"], [0])
    h.has("t_loglin catches a count mismatch", out, "Count mismatch")
    out = h.drive(stat640.t_loglin, ["0 1 2", "1 2 4", None], [0])
    h.has("t_loglin refuses x = 0 for log-log", out, "every x > 0")
    out = h.drive(stat640.t_loglin, ["1 2 3", "1 -2 4", None], [1])
    h.has("t_loglin refuses y < 0 for semi-log", out, "every y > 0")
    out = h.drive(stat640.t_loglin, ["1 2 3 4", "3 12 27 48", None], [-1])
    h.check("t_loglin backs out of the model menu", out, [])


def test_loglin_layout(h):
    import stat640
    rows = _layout_rows(h, stat640.t_loglin,
                        ["1 2 3 4", "3 12 27 48", None], [0])
    _check_layout(h, "log-log scatter", rows)
    rows = _layout_rows(h, stat640.t_loglin,
                        ["0 1 2 3", "5 10 20 40", None], [1])
    _check_layout(h, "semi-log scatter", rows)


def test_shape(h):
    import math
    import stat640
    out = h.drive(stat640.t_shape, ["1 2 2 3 3 3 4 4 5", None])
    h.num("shape N", out, "N = ", 9.0)
    h.num("shape distinct values", out, "distinct values = ", 5.0)
    h.num("shape mean", out, "mean = ", 3.0)
    h.num("shape median", out, "median = ", 3.0)
    h.has("shape mode", out, "mode(s) = 3")
    h.num("shape Sxx", out, "Sxx = ", 12.0)
    h.num("shape sd", out, "sd (n) = ", math.sqrt(12.0 / 9.0))
    h.num("shape peaks", out, "peaks = ", 1.0)
    h.has("shape unimodal", out, "modality: unimodal")
    h.num("shape Pearson skew", out, "Pearson skew = ", 0.0)
    h.num("shape moment skew", out, "moment skew = ", 0.0)
    h.has("shape symmetric", out, "skewness: symmetric")

    out = h.drive(stat640.t_shape, ["1 2 2 3 3 3 4 4 20", None])
    h.num("shape skewed mean", out, "mean = ", 42.0 / 9.0)
    h.num("shape skewed median", out, "median = ", 3.0)
    h.num("shape skewed Sxx", out, "Sxx = ", 272.0)
    h.num("shape skewed sd", out, "sd (n) = ", math.sqrt(272.0 / 9.0))
    h.num("shape skewed Pearson", out, "Pearson skew = ",
          3.0 * (42.0 / 9.0 - 3.0) / math.sqrt(272.0 / 9.0))
    h.has("shape skewed is still unimodal", out, "modality: unimodal")
    h.has("shape positive skew", out, "skewness: POSITIVE skew")
    h.has("shape positive skew names the tail", out, "tail to the RIGHT")

    out = h.drive(stat640.t_shape, ["1 17 17 18 18 18 19 19 20", None])
    h.num("shape negative median", out, "median = ", 18.0)
    h.has("shape negative skew", out, "skewness: NEGATIVE skew")
    h.has("shape negative skew names the tail", out, "tail to the LEFT")

    out = h.drive(stat640.t_shape, ["1 1 1 2 3 3 3", None])
    h.num("shape bimodal N", out, "N = ", 7.0)
    h.num("shape bimodal mean", out, "mean = ", 2.0)
    h.num("shape bimodal median", out, "median = ", 2.0)
    h.num("shape bimodal Sxx", out, "Sxx = ", 6.0)
    h.num("shape bimodal peaks", out, "peaks = ", 2.0)
    h.has("shape bimodal modality", out, "modality: bimodal")
    h.has("shape bimodal modes", out, "mode(s) = 1 3")
    h.num("shape bimodal Pearson", out, "Pearson skew = ", 0.0)
    h.has("shape bimodal is symmetric too", out, "skewness: symmetric")


def test_shape_grouped(h):
    import math
    import stat640
    out = h.drive(stat640.t_shape, ["1 2 3 4", "10 6 3 1"])
    h.num("grouped N", out, "N = ", 20.0)
    h.num("grouped mean", out, "mean = ", 1.75)
    h.num("grouped median", out, "median = ", 1.5)
    h.num("grouped Sxx", out, "Sxx = ", 15.75)
    h.num("grouped sd", out, "sd (n) = ", math.sqrt(15.75 / 20.0))
    h.num("grouped Pearson", out, "Pearson skew = ",
          3.0 * 0.25 / math.sqrt(15.75 / 20.0))
    h.num("grouped moment skew", out, "moment skew = ", 0.939060283, 1e-5)
    h.has("grouped mode", out, "mode(s) = 1")
    h.has("grouped unimodal", out, "modality: unimodal")
    h.has("grouped positive skew", out, "skewness: POSITIVE skew")

    out = h.drive(stat640.t_shape, ["1 2 3", "1 1 3"])
    h.num("grouped odd N", out, "N = ", 5.0)
    h.num("grouped odd mean", out, "mean = ", 2.4)
    h.num("grouped odd median", out, "median = ", 3.0)
    h.has("grouped odd negative skew", out, "skewness: NEGATIVE skew")

    out = h.drive(stat640.t_shape, ["1 2 3 4", "1 3 3 1"])
    h.num("plateau N", out, "N = ", 8.0)
    h.num("plateau mean", out, "mean = ", 2.5)
    h.num("plateau median", out, "median = ", 2.5)
    h.num("plateau Sxx", out, "Sxx = ", 6.0)
    h.num("plateau sd", out, "sd (n) = ", math.sqrt(6.0 / 8.0))
    h.num("plateau peaks", out, "peaks = ", 1.0)
    h.has("plateau is unimodal, not flat", out, "modality: unimodal")
    h.has("plateau has two modes", out, "mode(s) = 2 3")
    h.has("plateau is symmetric", out, "skewness: symmetric")

    out = h.drive(stat640.t_shape, ["1 2 3 4 5 6 7", "1 3 3 1 3 3 1"])
    h.num("twin plateau peaks", out, "peaks = ", 2.0)
    h.has("twin plateau modality", out, "modality: bimodal")

    out = h.drive(stat640.t_shape, ["1 2 3 4", "5 5 5 5"])
    h.has("uniform modality", out, "modality: uniform (flat)")
    h.num("uniform peaks", out, "peaks = ", 0.0)

    out = h.drive(stat640.t_shape, ["1 2 2", "1 3 4"])
    h.num("merged N", out, "N = ", 8.0)
    h.num("merged distinct values", out, "distinct values = ", 2.0)
    h.num("merged mean", out, "mean = ", 1.875)

    out = h.drive(stat640.t_shape, ["4 4 4 4", None])
    h.has("shape survives zero spread", out, "no shape")
    for ln in out:
        h.check("shape prints no skew when sd = 0",
                ln.find("Pearson skew") < 0, True)

    out = h.drive(stat640.t_shape, ["1 2 3", "1 2"])
    h.has("shape catches a count mismatch", out, "Count mismatch")
    out = h.drive(stat640.t_shape, ["1 2 3", "1 -2 3"])
    h.has("shape refuses a negative frequency", out, "must be >= 0")
    out = h.drive(stat640.t_shape, ["1 2 3", "0 0 0"])
    h.has("shape refuses a zero total frequency", out, "frequency is 0")


def test_shape_layout(h):
    import stat640
    rows = _layout_rows(h, stat640.t_shape, ["1 2 2 3 3 3 4 4 5", None])
    _check_layout(h, "frequency distribution chart", rows)


SECTIONS = [
    ("H640 u5 Venn, two events", test_venn2),
    ("H640 u5 Venn, impossible counts", test_venn2_rejects),
    ("H640 u5 Venn, three events", test_venn3),
    ("H640 u5 Venn diagram layout", test_venn_layout),
    ("H640 E7 log-linear fit", test_loglin_fit),
    ("H640 E7 reduce to linear form", test_loglin_tool),
    ("H640 E7 straightened scatter layout", test_loglin_layout),
    ("H640 D4 distribution shape", test_shape),
    ("H640 D4 shape from a frequency table", test_shape_grouped),
    ("H640 D4 distribution chart layout", test_shape_layout),
]
