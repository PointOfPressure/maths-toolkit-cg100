# tests_working_core.py - the answer / working / caveat split for the eight
# Core Pure modules: vcplx, matrix, vectors, polyroots, series, hyper, polar,
# diffeq.
#
# Each test drives one tool TWICE, once with casui.SHOW_WORKING off and once
# with it on, and asserts three things:
#
#   1. the ANSWER survives answer mode,
#   2. a named WORKING line does NOT,
#   3. a named CAVEAT DOES.
#
# The third is the one worth the file. Working that leaks into answer mode is
# untidy; a caveat that disappears turns a careful tool into a confidently
# wrong one, and no other test in the suite would notice.
#
# SHOW_WORKING is global state shared by every later test in the run, so every
# test restores it in a finally. Forgetting that poisons the rest of the run
# rather than failing here.


def _modes(h, fn, inputs, menus):
    # (answer-only lines, full lines) for one tool, with the setting restored
    # whatever happens in between.
    try:
        h.casui.SHOW_WORKING = False
        brief = h.drive(fn, inputs, menus)
        h.casui.SHOW_WORKING = True
        full = h.drive(fn, inputs, menus)
    finally:
        h.casui.SHOW_WORKING = True
    return brief, full


def _absent(lines, needle):
    return needle not in " ".join(lines)


def test_second_order_modes(h):
    import diffeq
    try:
        h.casui.SHOW_WORKING = False
        brief = h.drive(diffeq.t_second_order, ["-3", "2"], [])
        h.casui.SHOW_WORKING = True
        full = h.drive(diffeq.t_second_order, ["-3", "2"], [])
    finally:
        h.casui.SHOW_WORKING = True
    h.has("the solution survives answer mode", brief, "y = A e^(2x)")
    h.has("the roots survive answer mode", brief, "m1 = 2, m2 = 1")
    h.truthy("the auxiliary equation is working", "aux" not in " ".join(brief))
    h.truthy("the discriminant is working",
             _absent(brief, "disc = a^2 - 4b"))
    h.has("working mode still shows the auxiliary equation", full,
          "aux: m^2 + a m + b = 0")


def test_first_order_no_elementary_integral(h):
    # int P dx has no closed form, so the integrating factor cannot be written
    # down at all. That is the entire result and it must never be hidden.
    import diffeq
    brief, full = _modes(h, diffeq.t_first_order, ["sin(x)/x", "1"], [])
    h.has("the caveat survives answer mode", brief,
          "int P dx has no elementary form")
    h.has("and says the IF cannot be written down", brief,
          "so the integrating factor cannot be")
    h.truthy("restating P(x) is working", _absent(brief, "P(x) = sin(x)/x"))
    h.has("working mode restates P(x)", full, "P(x) = sin(x)/x")


def test_first_order_fitted_constant(h):
    # dy/dx + y/x = x with y(1) = 2. The particular solution is the answer,
    # "(checked at the given point)" is the caveat that says it was verified,
    # and "int IF*Q dx = ..." is working.
    import diffeq
    brief, full = _modes(h, diffeq.t_first_order, ["1/x", "x", "1", "2"], [])
    h.has("the integrating factor survives answer mode", brief, "IF = e^(ln(x))")
    h.has("the general solution survives answer mode", brief, "y = (x^3/3 + C)")
    h.has("the fitted constant survives answer mode", brief, "C = 1.6667")
    h.has("the check caveat survives answer mode", brief,
          "(checked at the given point)")
    h.has("the dropped-modulus caveat survives answer mode", brief,
          "any constant multiple of the IF")
    h.truthy("integrating IF*Q is working", _absent(brief, "int IF*Q dx = x^3/3"))
    h.has("working mode shows the integration", full, "int IF*Q dx = x^3/3")


def test_coupled_triangular(h):
    # b = 0 means the system never needed the coupled method, and the tool
    # cannot finish y for you. Both halves of that are caveats.
    import diffeq
    brief, full = _modes(h, diffeq.t_coupled, ["1", "0", "3", "2"], [])
    h.has("the x solution survives answer mode", brief, "x = A e^")
    h.has("the b = 0 caveat survives answer mode", brief,
          "b = 0, so the system is already")
    h.has("and so does the finish-it-by-hand caveat", brief,
          "integrating factor tool")
    h.truthy("eliminating y is working", _absent(brief, "eliminating y gives"))
    h.truthy("the auxiliary equation is working",
             _absent(brief, "auxiliary  m^2"))
    h.has("working mode shows the elimination", full, "eliminating y gives")


def test_coupled_initial_conditions(h):
    # The numeric self-check at t = 0 is what says the constants were fitted
    # correctly, so it is a caveat, not working.
    import diffeq
    brief, full = _modes(h, diffeq.t_coupled, ["1", "2", "3", "2", "1", "1"], [])
    h.has("the constants survive answer mode", brief, "A = 0.8, B = 0.2")
    h.has("the particular x survives answer mode", brief, "x = 0.8e^(4t)")
    h.has("the t = 0 self-check survives answer mode", brief,
          "(check at t = 0:")
    h.truthy("the simultaneous equations are working",
             _absent(brief, "A + B = 1"))
    h.truthy("restating the conditions is working",
             _absent(brief, "at t = 0:  x = 1, y = 1"))
    h.has("working mode shows the simultaneous equations", full, "A + B = 1")


def test_particular_integral_resonance(h):
    # p is a root of the auxiliary equation, so the trial had to be multiplied
    # by x. Hiding that leaves a PI that looks like it came from nowhere.
    import diffeq
    brief, full = _modes(h, diffeq.t_particular, ["-3", "2", "5", "2"], [1])
    h.has("the PI survives answer mode", brief, "PI: y = 5 x e^(2x)")
    h.has("the general solution survives answer mode", brief,
          "GENERAL SOLUTION = CF + PI")
    h.has("the resonance caveat survives answer mode", brief,
          "p is a root of the auxiliary equation")
    h.truthy("restating f(x) is working", _absent(brief, "f(x) = 5 e^(2x)"))
    h.truthy("the auxiliary line is working",
             _absent(brief, "auxiliary: m^2 + (-3)m"))
    h.has("working mode restates f(x)", full, "f(x) = 5 e^(2x)")


def test_shm_fit(h):
    import diffeq
    brief, full = _modes(h, diffeq.t_shm, ["2", "3", "4", "1"], [])
    h.has("the amplitude survives answer mode", brief, "amplitude R")
    h.has("the fitted motion survives answer mode", brief, "x = 3.6056 cos(")
    h.has("the v^2 identity check survives answer mode", brief,
          "check v^2 = w^2(R^2-x^2)")
    h.truthy("fitting C and D is working", _absent(brief, "x(0) = C = 3"))
    h.has("working mode shows the fit", full, "x(0) = C = 3")


def test_differences_self_check(h):
    # Method of differences: g(r) is the answer, the partial fractions are
    # working, and both the "(checked numerically)" line and the independent
    # direct sum are caveats - they are what makes the telescoped answer
    # trustworthy.
    import series
    brief, full = _modes(h, series.t_differences, ["1/(r(r+1))", "10"], [])
    h.has("g(r) survives answer mode", brief, "take g(r) = 1/r")
    h.has("the telescoped sum survives answer mode", brief, "S(n) = g(1) - [")
    h.has("the numeric value survives answer mode", brief, "S(10) = 0.9091")
    h.has("the numeric check caveat survives answer mode", brief,
          "(checked numerically)")
    h.has("the independent direct sum survives answer mode", brief,
          "direct sum  = 0.9091")
    h.truthy("the partial fractions are working",
             _absent(brief, "partial fractions:"))
    h.truthy("restating f(r) is working", _absent(brief, "f(r) = 1/(r*(r+1))"))
    h.has("working mode shows the partial fractions", full, "partial fractions:")


def test_differences_refusal(h):
    # When it does not telescope the refusal IS the answer, and it has to
    # survive both modes.
    import series
    brief, full = _modes(h, series.t_differences, ["1/(r(r+1)(r+2))"], [])
    h.has("the refusal survives answer mode", brief,
          "This does not split into two")
    h.has("and says why", brief, "sum does not telescope this way")
    h.truthy("full mode says the same", not _absent(full, "does not telescope"))


def test_maclaurin_modes(h):
    import series
    brief, full = _modes(h, series.t_maclaurin, ["sin(x)", "4"], [])
    h.has("the polynomial survives answer mode", brief, "P(x) = x")
    h.truthy("restating f(x) is working", _absent(brief, "f(x) = sin(x)"))
    h.has("working mode restates f(x)", full, "f(x) = sin(x)")


def test_skew_lines_parallel(h):
    # The two directions are parallel, so there is no shortest distance to
    # report and the tool says so. That refusal must survive answer mode.
    import vectors
    brief, full = _modes(h, vectors.t_skew,
                         ["0", "0", "0", "1", "0", "0",
                          "0", "1", "0", "2", "0", "0"], [])
    h.has("the parallel caveat survives answer mode", brief, "d1 x d2 ~ 0")
    h.has("and says they are not skew", brief, "not skew")
    # and the ordinary case: the distance is the answer, |d1 x d2| is working
    brief2, full2 = _modes(h, vectors.t_skew,
                           ["0", "0", "0", "1", "0", "0",
                            "0", "1", "0", "0", "0", "1"], [])
    h.has("the distance survives answer mode", brief2, "shortest dist = 1")
    h.truthy("the cross product magnitude is working",
             _absent(brief2, "|d1 x d2| = 1"))
    h.has("working mode shows |d1 x d2|", full2, "|d1 x d2| = 1")


def test_line_meets_plane_check(h):
    # "check n.p = ... (should be ...)" is the line that tells you the
    # intersection really is on the plane.
    import vectors
    brief, full = _modes(h, vectors.t_lineplane,
                         ["0", "0", "0", "1", "1", "1", "1", "0", "0", "5"], [])
    h.has("the intersection survives answer mode", brief, "they meet at (5, 5, 5)")
    h.has("the n.p check survives answer mode", brief, "check n.p = 5 (should be 5)")
    h.truthy("restating the line is working",
             _absent(brief, "line r = (0, 0, 0) + t(1, 1, 1)"))
    h.truthy("substituting into the plane is working",
             _absent(brief, "n.(a + t d) = k gives"))
    h.has("working mode shows the substitution", full, "n.(a + t d) = k gives")


def test_point_to_plane(h):
    import vectors
    brief, full = _modes(h, vectors.t_ptplane, ["1", "0", "0", "5", "2", "0", "0"], [])
    h.has("the distance survives answer mode", brief, "dist = 3")
    h.truthy("n.p is working", _absent(brief, "n.p = 2"))
    h.has("working mode shows n.p", full, "n.p = 2")
    # the degenerate normal is a caveat
    brief2, full2 = _modes(h, vectors.t_ptplane, ["0", "0", "0", "1", "1", "1", "1"], [])
    h.has("a zero normal is flagged in answer mode", brief2,
          "Normal is zero: undefined")


def test_loci_half_line(h):
    # "the point a itself is NOT included" and "only the half with x > ..."
    # both change what the answer means, so both are caveats.
    import vcplx
    brief, full = _modes(h, vcplx.t_loci, ["1", "2", "30"], [2])
    h.has("the locus survives answer mode", brief, "A HALF-LINE from 1 + 2i")
    h.has("the cartesian form survives answer mode", brief, "cartesian: y - 2 =")
    h.has("the excluded point caveat survives answer mode", brief,
          "NOT included - arg(0) is undefined")
    h.has("the half-only caveat survives answer mode", brief,
          "but only the half with x")
    h.truthy("restating the locus is working",
             _absent(brief, "arg(z - (1 + 2i)) = 30 deg"))
    h.has("working mode restates the locus", full, "arg(z - (1 + 2i)) = 30 deg")


def test_loci_bisector_degenerate(h):
    import vcplx
    brief, full = _modes(h, vcplx.t_loci, ["0", "0", "4", "2"], [1])
    h.has("the bisector survives answer mode", brief, "y = -2x + 5")
    h.has("the midpoint survives answer mode", brief, "midpoint (2, 1)")
    h.truthy("the bisector gradient is working",
             _absent(brief, "bisector gradient = -2"))
    h.has("working mode shows the gradients", full, "bisector gradient = -2")
    # a = b: no bisector exists, and that is a caveat
    brief2, full2 = _modes(h, vcplx.t_loci, ["1", "2", "1", "2"], [1])
    h.has("the degenerate case survives answer mode", brief2,
          "a and b are the same point")


def test_demoivre_numeric_check(h):
    # The expansion is the answer; the check at t = 0.7 is what says the
    # binomial bookkeeping came out right.
    import vcplx
    brief, full = _modes(h, vcplx.t_demoivre_id, ["3"], [])
    h.has("the cosine identity survives answer mode", brief, "cos 3t = c^3 - 3cs^2")
    h.has("the sine identity survives answer mode", brief, "sin 3t = 3c^2s - s^3")
    h.has("the legend survives answer mode", brief, "with c = cos t and s = sin t")
    h.has("the numeric check survives answer mode", brief, "check at t = 0.7 rad")
    h.has("with both sides of it", brief, "expansion  = -0.504846")
    h.truthy("restating de Moivre is working",
             _absent(brief, "by de Moivre. Expanding the left side"))
    h.has("working mode states de Moivre", full,
          "by de Moivre. Expanding the left side")


def test_matrix_singular_inverse(h):
    import matrix
    real = matrix.A
    try:
        matrix.A = [[1.0, 2.0], [2.0, 4.0]]
        brief, full = _modes(h, matrix.t_inv, [], [])
    finally:
        matrix.A = real
    h.has("the verdict survives answer mode", brief, "no inverse")
    h.has("the singular caveat survives answer mode", brief, "A is singular")
    h.truthy("det = 0 is working", _absent(brief, "det = 0"))
    h.has("working mode shows det = 0", full, "det = 0")


def test_matrix_eigenvalues(h):
    import matrix
    real = matrix.A
    try:
        matrix.A = [[1.0, 2.0], [3.0, 4.0]]
        brief, full = _modes(h, matrix.t_eig, [], [])
    finally:
        matrix.A = real
    h.has("the eigenvalues survive answer mode", brief, "L1 = 5.3723")
    h.has("both of them", brief, "L2 = -0.3723")
    h.truthy("the trace is working", _absent(brief, "trace = 5"))
    h.has("working mode shows the trace", full, "trace = 5")


def test_matrix_invariant(h):
    import matrix
    real = matrix.A
    try:
        matrix.A = [[1.0, 2.0], [0.0, 1.0]]
        brief, full = _modes(h, matrix.t_invariant, [], [])
    finally:
        matrix.A = real
    h.has("the line of invariant points survives answer mode", brief,
          "LINE of invariant points")
    h.has("the invariant line survives answer mode", brief, "y = 0 x")
    h.truthy("solving (A - I)p = 0 is working",
             _absent(brief, "solve (A - I)p = 0:"))
    h.truthy("the quadratic in m is working",
             _absent(brief, "b m^2 + (a - d)m - c = 0"))
    h.truthy("the closing teaching note is working",
             _absent(brief, "A line of invariant points is"))
    h.has("working mode shows the quadratic in m", full,
          "b m^2 + (a - d)m - c = 0")
    # a 3x3 A is refused, and the refusal is the whole output
    try:
        matrix.A = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        brief2, full2 = _modes(h, matrix.t_invariant, [], [])
    finally:
        matrix.A = real
    h.has("the 2x2-only refusal survives answer mode", brief2,
          "A must be 2x2 for this tool")


def test_quadratic_roots_discriminant(h):
    import polyroots
    brief, full = _modes(h, polyroots.t_quad_roots, ["1", "-3", "2"], [])
    h.has("the roots survive answer mode", brief, "x1 = 2")
    h.has("both roots survive", brief, "x2 = 1")
    h.truthy("the discriminant is working", _absent(brief, "disc = b^2-4ac"))
    h.has("working mode shows the discriminant", full, "disc = b^2-4ac = 1")
    # the search window is a caveat: "no real roots" is only true inside it
    brief2, full2 = _modes(h, polyroots.t_numeric_roots, ["x^2-4"], [])
    h.has("the search window survives answer mode", brief2,
          "real roots in [-20,20]")
    h.has("the roots survive answer mode", brief2, "x = -2")


def test_hyperbolic_inverse(h):
    import hyper
    brief, full = _modes(h, hyper.t_arsinh, ["1"], [])
    h.has("the value survives answer mode", brief, "arsinh x = 0.8814")
    h.truthy("the defining formula is working",
             _absent(brief, "ln(x+sqrt(x^2+1))"))
    h.truthy("restating x is working", _absent(brief, "x = 1"))
    h.has("working mode names the formula", full, "arsinh x = ln(x+sqrt(x^2+1))")
    # the domain error is a caveat and survives with the input hidden
    brief2, full2 = _modes(h, hyper.t_arcosh, ["0.5"], [])
    h.has("the domain error survives answer mode", brief2,
          "Error: domain is x >= 1")
    h.truthy("the echoed input is still working", _absent(brief2, "x = 0.5"))


def test_polar_area(h):
    import polar
    brief, full = _modes(h, polar.t_area, ["1+cos(x)", "0", "3.14159"], [])
    h.has("the area survives answer mode", brief, "Area = 2.3562")
    h.truthy("the formula is working", _absent(brief, "A = 0.5 integ r^2 dtheta"))
    h.truthy("the intermediate integral is working",
             _absent(brief, "integ r^2 ="))
    h.has("working mode names the formula", full, "A = 0.5 integ r^2 dtheta")
    # a = b: the zero is right but only because the limits coincide
    brief2, full2 = _modes(h, polar.t_area, ["1+cos(x)", "1", "1"], [])
    h.has("the zero area survives answer mode", brief2, "Area = 0")
    h.has("the equal-limits caveat survives answer mode", brief2, "a equals b")


def test_setting_is_restored(h):
    # Every test above restores SHOW_WORKING in a finally. If one of them ever
    # stops doing that, this catches it here rather than as a mystery failure
    # in whichever section happens to run next.
    h.check("SHOW_WORKING is back on", h.casui.SHOW_WORKING, True)


SECTIONS = [
    ("Core Pure answer/working split", test_second_order_modes),
    ("first order: no elementary IF", test_first_order_no_elementary_integral),
    ("first order: fitted constant", test_first_order_fitted_constant),
    ("coupled: b = 0 is triangular", test_coupled_triangular),
    ("coupled: initial conditions", test_coupled_initial_conditions),
    ("particular integral: resonance", test_particular_integral_resonance),
    ("SHM: fitting R and phi", test_shm_fit),
    ("differences: numeric self-check", test_differences_self_check),
    ("differences: refusal", test_differences_refusal),
    ("Maclaurin modes", test_maclaurin_modes),
    ("skew lines: parallel case", test_skew_lines_parallel),
    ("line meets plane: n.p check", test_line_meets_plane_check),
    ("point to plane", test_point_to_plane),
    ("loci: half-line exclusions", test_loci_half_line),
    ("loci: bisector and a = b", test_loci_bisector_degenerate),
    ("de Moivre: numeric check", test_demoivre_numeric_check),
    ("matrix: singular inverse", test_matrix_singular_inverse),
    ("matrix: eigenvalues", test_matrix_eigenvalues),
    ("matrix: invariant points and lines", test_matrix_invariant),
    ("polyroots: discriminant is working", test_quadratic_roots_discriminant),
    ("hyperbolic inverses", test_hyperbolic_inverse),
    ("polar area", test_polar_area),
    ("SHOW_WORKING restored", test_setting_is_restored),
]
