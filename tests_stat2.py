# tests_stat2.py - correctness tests for the three statistics tools added for
# H640 u5 (Venn diagrams), E7 (reduce to linear form by taking logs) and
# D4 (describe the shape of a frequency distribution).
#
# Every expected number below was worked out by hand first and the working is
# in the comment above the assertion. Picked up automatically by tests.py's
# tests_*.py hook; `h` is the harness (check / close / truthy / raises / drive
# / has / num plus the engine modules).


# --------------------------------------------------------------- layout ----
# tests.py records where each string is drawn for a fixed list of scenes, but
# a section module's own charts are not in that list. These do the same thing
# for the charts added here: nothing may run off the 384px width, nothing may
# be drawn off screen vertically, and no two strings may overprint on the same
# baseline. A Venn diagram is nine labels packed into one screen, so this is
# where that would go wrong.
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


# ----------------------------------------------------- u5: Venn diagrams ----
def test_venn2(h):
    import stat640
    # n = 30, |A| = 12, |B| = 15, |A and B| = 5.
    #   A only  = 12 - 5 = 7
    #   B only  = 15 - 5 = 10
    #   neither = 30 - (12 + 15 - 5) = 30 - 22 = 8
    #   7 + 5 + 10 + 8 = 30, so the four regions do account for everyone.
    #   P(A) = 12/30 = 0.4          P(B) = 15/30 = 0.5
    #   P(A and B) = 5/30 = 1/6     P(A or B) = 22/30 = 11/15
    #   P(A') = 18/30 = 0.6         P(A|B) = (5/30)/(15/30) = 5/15 = 1/3
    #   P(B|A) = 5/12
    #   P(A)P(B) = 0.4*0.5 = 0.2, and 1/6 != 0.2, so NOT independent.
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

    # A deliberately independent pair: n = 20, |A| = 10, |B| = 8,
    # |A and B| = 4. P(A) = 0.5, P(B) = 0.4, P(A)P(B) = 0.2 = 4/20. So the
    # verdict must flip to YES on data that differs from the case above only
    # in the overlap - which is what a hard-coded "NO" would not do.
    out = h.drive(stat640.t_venn, ["20", "10", "8", "4"], [0])
    h.num("venn2 independent P(A and B)", out, "P(A and B) = ", 0.2)
    h.num("venn2 independent P(A)P(B)", out, "P(A)P(B) = ", 0.2)
    h.has("venn2 independent verdict", out, "A,B independent: YES")
    h.has("venn2 independent is not exclusive", out, "mutually exclusive: NO")

    # Mutually exclusive: n = 50, |A| = 20, |B| = 15, overlap 0.
    # P(A or B) = 35/50 = 0.7, and since P(A)P(B) = 0.4*0.3 = 0.12 != 0,
    # exclusive events are NOT independent - both lines must say so.
    out = h.drive(stat640.t_venn, ["50", "20", "15", "0"], [0])
    h.num("venn2 exclusive union", out, "P(A or B) = ", 0.7)
    h.num("venn2 exclusive neither", out, "n(neither) = ", 15.0)
    h.has("venn2 exclusive verdict", out, "mutually exclusive: YES")
    h.has("venn2 exclusive is not independent", out, "A,B independent: NO")


def test_venn2_rejects(h):
    import stat640
    # n = 30 but |A| = 20 and |B| = 15 with an overlap of only 2:
    # 20 + 15 - 2 = 33 people are needed and only 30 exist, so the "neither"
    # region would be -3. The tool must refuse rather than draw it.
    out = h.drive(stat640.t_venn, ["30", "20", "15", "2"], [0])
    h.has("venn2 says the counts do not add up", out, "DO NOT ADD UP")
    h.has("venn2 names the impossible region", out, "neither")
    h.has("venn2 reports what is needed", out, "33")
    # and nothing at all is drawn on the impossible data
    rows = _layout_rows(h, stat640.t_venn, ["30", "20", "15", "2"], [0])
    h.check("venn2 draws no diagram when the counts fail", rows, [])
    # an overlap larger than one of the events is impossible too
    out = h.drive(stat640.t_venn, ["30", "5", "15", "9"], [0])
    h.has("venn2 rejects an overlap bigger than A", out, "DO NOT ADD UP")
    # a negative count is rejected before any arithmetic
    out = h.drive(stat640.t_venn, ["30", "-5", "15", "2"], [0])
    h.has("venn2 rejects a negative count", out, "cannot be negative")
    # a zero or missing total is rejected
    out = h.drive(stat640.t_venn, ["0"], [0])
    h.has("venn2 rejects a zero total", out, "total > 0")


def test_venn3(h):
    import stat640
    # 100 students. |A| = 50, |B| = 40, |C| = 30,
    # |A and B| = 20, |A and C| = 15, |B and C| = 10, |A and B and C| = 5.
    #   all three   = 5
    #   A and B only = 20 - 5 = 15
    #   A and C only = 15 - 5 = 10
    #   B and C only = 10 - 5 = 5
    #   A only = 50 - 20 - 15 + 5 = 20
    #   B only = 40 - 20 - 10 + 5 = 15
    #   C only = 30 - 15 - 10 + 5 = 10
    #   inside = 50+40+30-20-15-10+5 = 80  (inclusion-exclusion)
    #   none   = 100 - 80 = 20
    #   check: 20+15+10+15+10+5+5+20 = 100
    #   P(A and B) = 0.2 = 0.5*0.4 = P(A)P(B)   -> A,B independent
    #   P(A and C) = 0.15 = 0.5*0.3 = P(A)P(C)  -> A,C independent
    #   P(B and C) = 0.10 != 0.4*0.3 = 0.12     -> B,C NOT independent
    #   P(A|B) = 0.2/0.4 = 0.5 = P(A), consistent with independence.
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

    # Three mutually exclusive events: 60 = 30 + 20 + 5 with 5 left over and
    # every intersection empty.
    out = h.drive(stat640.t_venn, ["60", "30 20 5", "0 0 0", "0"], [1])
    h.num("venn3 exclusive none", out, "n(none) = ", 5.0)
    h.num("venn3 exclusive union", out, "P(A or B or C) = ", 55.0 / 60.0)
    h.has("venn3 exclusive verdict", out, "mutually exclusive: YES")

    # |A and B| = 20 but |A and B and C| = 25 is impossible: the triple is a
    # subset of the pair, so "A and B only" comes out at -5.
    out = h.drive(stat640.t_venn,
                  ["100", "50 40 30", "20 15 10", "25"], [1])
    h.has("venn3 rejects a triple bigger than a pair", out, "DO NOT ADD UP")
    h.has("venn3 names the impossible region", out, "A and B only")
    # wrong number of values in a list is refused, not silently padded
    out = h.drive(stat640.t_venn, ["100", "50 40", "20 15 10", "5"], [1])
    h.has("venn3 needs three single counts", out, "exactly 3")


def test_venn_layout(h):
    import stat640
    rows = _layout_rows(h, stat640.t_venn, ["30", "12", "15", "5"], [0])
    _check_layout(h, "venn 2 events", rows)
    # the drawn labels are the four region counts, the two event letters and
    # the total: seven strings plus the title
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
    # three-digit counts must still not collide
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


# --------------------------------------- E7: reduce to linear form by logs --
def test_loglin_fit(h):
    import math
    import stat640
    # y = 3 x^2 sampled exactly at x = 1,2,3,4 -> y = 3,12,27,48.
    # ln y = ln 3 + 2 ln x is an exact straight line, so the least-squares fit
    # must return gradient 2, intercept ln 3 = 1.0986122886681098 and r = 1.
    # Recovering a = e^(ln 3) must give exactly 3.
    res = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 0)
    h.truthy("log-log fit succeeds", res is not None)
    tx, ty, ia, grad, r = res
    h.close("log-log recovers n = 2", grad, 2.0, 1e-9)
    h.close("log-log recovers ln a = ln 3", ia, math.log(3.0), 1e-9)
    h.close("log-log recovers a = 3", math.exp(ia), 3.0, 1e-9)
    h.close("log-log r = 1 on exact data", r, 1.0, 1e-9)
    h.close("log-log transforms x to ln x", tx[1], math.log(2.0), 1e-12)
    h.close("log-log transforms y to ln y", ty[1], math.log(12.0), 1e-12)

    # y = 5 * 2^x at x = 0,1,2,3 -> y = 5,10,20,40.
    # ln y = ln 5 + x ln 2, so gradient = ln 2 = 0.6931471805599453,
    # intercept = ln 5 = 1.6094379124341003, b = e^ln2 = 2, a = e^ln5 = 5.
    res = stat640._loglin([0.0, 1.0, 2.0, 3.0], [5.0, 10.0, 20.0, 40.0], 1)
    h.truthy("semi-log fit succeeds", res is not None)
    tx, ty, ia, grad, r = res
    h.close("semi-log gradient is ln b = ln 2", grad, math.log(2.0), 1e-9)
    h.close("semi-log recovers b = 2", math.exp(grad), 2.0, 1e-9)
    h.close("semi-log recovers a = 5", math.exp(ia), 5.0, 1e-9)
    h.close("semi-log r = 1 on exact data", r, 1.0, 1e-9)
    h.close("semi-log leaves x alone", tx[2], 2.0, 1e-12)

    # The two transforms are genuinely different: on the SAME data the
    # log-log gradient and the semi-log gradient must not agree, or one of
    # them is not taking logs of x.
    a = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 0)
    b = stat640._loglin([1.0, 2.0, 3.0, 4.0], [3.0, 12.0, 27.0, 48.0], 1)
    h.truthy("log-log and semi-log differ on the same data",
             abs(a[3] - b[3]) > 0.1)

    # out of range for a logarithm: refused, not silently skipped
    h.check("log-log refuses x <= 0",
            stat640._loglin([0.0, 1.0, 2.0], [1.0, 2.0, 4.0], 0), None)
    h.check("log-log refuses y <= 0",
            stat640._loglin([1.0, 2.0, 3.0], [1.0, -2.0, 4.0], 0), None)
    h.check("semi-log refuses y <= 0",
            stat640._loglin([1.0, 2.0, 3.0], [1.0, 0.0, 4.0], 1), None)


def test_loglin_tool(h):
    import math
    import stat640
    # same y = 3 x^2 data, driven through the tool. Printed to 5 dp, so
    # ln 3 shows as 1.09861.
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

    # prediction uses the ORIGINAL model: y = 3 x^2 at x = 5 is 75, which a
    # tool that predicted from the straight line without converting back
    # would report as ln y = 4.317 or as 3*5*2 = 30.
    out = h.drive(stat640.t_loglin,
                  ["1 2 3 4", "3 12 27 48", "5"], [0])
    h.num("t_loglin predicts from the original curve", out, "y = ", 75.0)

    # semi-log: y = 5 * 2^x, and the prediction at x = 4 is 5*16 = 80.
    out = h.drive(stat640.t_loglin,
                  ["0 1 2 3", "5 10 20 40", "4"], [1])
    h.num("t_loglin semi-log base b", out, "base b = e^gradient = ", 2.0)
    h.num("t_loglin semi-log a", out, "a = e^intercept = ", 5.0)
    h.has("t_loglin semi-log model", out, "y = 5 * 2^x")
    h.has("t_loglin semi-log log form", out, "ln y = ln a + x ln b")
    h.num("t_loglin semi-log prediction", out, "y = ", 80.0)

    # r is reported on the transformed data. y = 2 x^1.5 with one point moved
    # off the curve must give r < 1 but still close to it.
    out = h.drive(stat640.t_loglin, ["1 2 3 4", "2 6 10 16", None], [0])
    ok = [0]
    for ln in out:
        p = ln.find("r = ")
        if p == 0:
            v = float(ln[4:])
            if 0.9 < v < 1.0:
                ok[0] = 1
    h.check("t_loglin r is below 1 on inexact data", ok[0], 1)

    # bad input paths
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


# ------------------------------- D4: shape of a frequency distribution ------
def test_shape(h):
    import math
    import stat640
    # Raw data 1,2,2,3,3,3,4,4,5. Tallied: values 1,2,3,4,5 with frequencies
    # 1,2,3,2,1. N = 9, sum fx = 1+4+9+8+5 = 27 so mean = 3; the 5th value is
    # 3 so the median is 3; the mode is 3.
    # Sxx = 1*4 + 2*1 + 3*0 + 2*1 + 1*4 = 12, sd(n) = sqrt(12/9) = 1.154700.
    # mean = median, so Pearson skew 3(3-3)/sd = 0 -> symmetric.
    # The frequency run 1,2,3,2,1 rises once and falls once -> one peak.
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

    # Same distribution with the 5 replaced by 20: values 1,2,3,4,20 with the
    # same frequencies 1,2,3,2,1. N = 9, sum fx = 1+4+9+8+20 = 42, mean =
    # 42/9 = 4.66667. The 5th value is still 3, so median = 3.
    # sum fx^2 = 1+8+27+32+400 = 468, Sxx = 468 - 42^2/9 = 468-196 = 272,
    # sd(n) = sqrt(272/9) = 5.497474.
    # Pearson = 3(42/9 - 3)/sd = 3*(5/3)/5.497474 = 5/5.497474 = 0.909509.
    # Still one peak, so this is unimodal AND positively skewed - the two
    # descriptions are independent and both must be reported.
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

    # Mirror image: 20,19,19,18,18,18,17,17,16. mean = 18 - 5/3 = 16.33333,
    # median 18, so mean < median and the skew is negative.
    out = h.drive(stat640.t_shape, ["1 17 17 18 18 18 19 19 20", None])
    h.num("shape negative median", out, "median = ", 18.0)
    h.has("shape negative skew", out, "skewness: NEGATIVE skew")
    h.has("shape negative skew names the tail", out, "tail to the LEFT")

    # Bimodal and symmetric at once: 1,1,1,2,3,3,3. Values 1,2,3 with
    # frequencies 3,1,3. N = 7, sum fx = 3+2+9 = 14, mean = 2; the 4th value
    # is 2 so the median is 2; Pearson skew = 0. But 3,1,3 has TWO peaks and
    # two modes, so "symmetric" alone would not describe it.
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
    # Values 1,2,3,4 with frequencies 10,6,3,1 (given, not tallied).
    # N = 20, sum fx = 10+12+9+4 = 35, mean = 1.75.
    # N is even, so the median is the mean of the 10th and 11th values;
    # the cumulative frequencies are 10,16,19,20 so those are 1 and 2 and the
    # median is 1.5.
    # Sxx = 10(0.75^2) + 6(0.25^2) + 3(1.25^2) + 1(2.25^2)
    #     = 5.625 + 0.375 + 4.6875 + 5.0625 = 15.75
    # sd(n) = sqrt(15.75/20) = sqrt(0.7875) = 0.8874120.
    # Pearson = 3(1.75-1.5)/0.8874120 = 0.75/0.8874120 = 0.845154.
    # sum f(x-mean)^3 = -4.21875 + 0.09375 + 5.859375 + 11.390625 = 13.125,
    # moment skew = (13.125/20)/0.8874120^3 = 0.65625/0.698837 = 0.939060.
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

    # An odd N with frequencies: values 1,2,3 frequencies 1,1,3 gives N = 5,
    # so the median is the 3rd value = 3, mean = (1+2+9)/5 = 2.4, and the
    # mean is BELOW the median -> negative skew.
    out = h.drive(stat640.t_shape, ["1 2 3", "1 1 3"])
    h.num("grouped odd N", out, "N = ", 5.0)
    h.num("grouped odd mean", out, "mean = ", 2.4)
    h.num("grouped odd median", out, "median = ", 3.0)
    h.has("grouped odd negative skew", out, "skewness: NEGATIVE skew")

    # A flat TOP is still one peak: values 1,2,3,4 with frequencies 1,3,3,1.
    # Comparing each frequency with its immediate neighbours finds no peak at
    # all here (3 is not greater than 3), so the run of equal frequencies has
    # to be collapsed first. N = 8, sum fx = 1+6+9+4 = 20 so mean = 2.5; the
    # 4th and 5th values are 2 and 3 so the median is 2.5 as well.
    # Sxx = 1(1.5^2) + 3(0.5^2) + 3(0.5^2) + 1(1.5^2) = 6, sd = sqrt(6/8).
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

    # Two separated humps with flat tops: 1,3,3,1,3,3,1 must be bimodal.
    out = h.drive(stat640.t_shape, ["1 2 3 4 5 6 7", "1 3 3 1 3 3 1"])
    h.num("twin plateau peaks", out, "peaks = ", 2.0)
    h.has("twin plateau modality", out, "modality: bimodal")

    # A flat distribution has no peak at all and must not be called unimodal.
    out = h.drive(stat640.t_shape, ["1 2 3 4", "5 5 5 5"])
    h.has("uniform modality", out, "modality: uniform (flat)")
    h.num("uniform peaks", out, "peaks = ", 0.0)

    # Repeated values in the value list are merged, not counted twice:
    # 2 appears with frequency 3 and again with 4, so N = 1+3+4 = 8 and the
    # distribution is 1 (once) and 2 (seven times), mean = (1+14)/8 = 1.875.
    out = h.drive(stat640.t_shape, ["1 2 2", "1 3 4"])
    h.num("merged N", out, "N = ", 8.0)
    h.num("merged distinct values", out, "distinct values = ", 2.0)
    h.num("merged mean", out, "mean = ", 1.875)

    # every value identical: sd = 0, so Pearson skew would divide by zero
    out = h.drive(stat640.t_shape, ["4 4 4 4", None])
    h.has("shape survives zero spread", out, "no shape")
    for ln in out:
        h.check("shape prints no skew when sd = 0",
                ln.find("Pearson skew") < 0, True)

    # bad input paths
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
