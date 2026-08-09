# tests_working_h640.py - the answer/working split for the five H640 modules
# pure640, purecalc, stat640, mech640 and proof.
#
# Every assertion here is the same shape, because the contract is:
#   * an ANSWER line survives with the Working setting off,
#   * a WORKING line does not,
#   * a CAVEAT line survives ANYWAY, in both modes.
# The third is the one that matters. Hiding a caveat turns a careful tool into
# a confident wrong one, so each tool below that has a real warning - the point
# off the curve, the ambiguous triangle, the substitution self-check, the
# counterexample that is not a proof, the Venn whose figures do not add up - is
# asserted on by name.
#
# SHOW_WORKING is global state, so every helper restores it in a finally. A
# leaked False would silently strip the working out of every later test in the
# whole run.


def _both(h, fn, inputs, menus):
    # (answer-only output, full output) for one tool and one set of inputs
    real = h.casui.SHOW_WORKING
    try:
        h.casui.SHOW_WORKING = False
        brief = h.drive(fn, inputs, menus)
        h.casui.SHOW_WORKING = True
        full = h.drive(fn, inputs, menus)
    finally:
        h.casui.SHOW_WORKING = real
    return (brief, full)


def _split(h, label, fn, inputs, menus, answer, working, caveat=None):
    brief, full = _both(h, fn, inputs, menus)
    btext = ' '.join(brief)
    ftext = ' '.join(full)
    h.has(label + ': the answer survives answer mode', brief, answer)
    h.truthy(label + ': ' + repr(working) + ' is working, so it is hidden',
             working not in btext)
    h.truthy(label + ': ' + repr(working) + ' is still there in full',
             working in ftext)
    h.truthy(label + ': answer mode adds nothing of its own',
             len(brief) <= len(full))
    if caveat is not None:
        h.has(label + ': the CAVEAT survives answer mode', brief, caveat)
        h.has(label + ': the caveat is in full output too', full, caveat)
    return (brief, full)


# --------------------------------------------------------------- pure640 ----
def test_quadratic_modes(h):
    import pure640
    h.casui.SHOW_WORKING = False
    brief = h.drive(pure640.t_quadratic, ["1", "-5", "6"], [])
    h.casui.SHOW_WORKING = True
    full = h.drive(pure640.t_quadratic, ["1", "-5", "6"], [])
    h.has("the roots survive answer mode", brief, "x = 3")
    h.truthy("the discriminant is working", "disc" not in " ".join(brief))
    h.truthy("the discriminant is shown in full", "disc" in " ".join(full))


def test_pure640_modes(h):
    import pure640
    # SSA is the ambiguous case: a second triangle exists and the warning about
    # it must never be filtered out with the sine rule working.
    _split(h, "triangle SSA", pure640.t_triangle, ["7", "8", "50"], [3],
           "a = 7   A = 50 deg", "sine rule: a/sinA", "AMBIGUOUS CASE")
    # 2sin^2 x + sin x - 1 = 0: the substitution is working, the solutions are
    # the answer, the substitute-back check is a caveat.
    _split(h, "trig by identity", pure640._trig_identity,
           ["2", "1", "-1", "0", "360"], [0, 0],
           "ALL SOLUTIONS in order:", "let u = sin x",
           "checked back in the original")
    # sin^2 x - 3 sin x = 0 has a root u = 3, which no x can produce
    _split(h, "impossible trig root", pure640._trig_identity,
           ["1", "-3", "0", "0", "360"], [0, 0],
           "0, 180, 360", "let u = sin x", "cannot exceed 1")
    # tangent at (3,4) to x^2+y^2=25: the perpendicularity check is a caveat
    _split(h, "tangent to a circle", pure640._circle_tangent,
           ["0", "0", "3", "4"], [],
           "y = -0.75x + 6.25", "radius gradient  = 1.3333", "(should be -1)")
    # circle through 3 points: "all three points on the circle" is the check
    # that the centre really works, so it is a caveat, not working
    _split(h, "circle through 3 points", pure640._circle_3pts,
           ["0", "0", "4", "0", "0", "3"], [],
           "centre (2, 1.5)", "angle in a semicircle",
           "all three points on the circle: yes")
    # (1+x)^0.5 only converges for |x| < 1, which is a condition on the answer
    _split(h, "binomial with real n", pure640.t_binom, ["0.5", "4"], [1],
           "x^1: 0.5", "(1 + x)^0.5", "valid for |x| < 1")
    # rationalising: the conjugate step is working, the surd form is the answer
    _split(h, "rationalise a denominator", pure640.t_surds,
           ["1", "1", "1", "2"], [3],
           "= -1 + sqrt(2)", "CONJUGATE 1 - sqrt(2)")


# -------------------------------------------------------------- purecalc ----
def test_purecalc_modes(h):
    import purecalc
    # (1,1) is not on x^2+y^2=25, so dy/dx there is meaningless. That warning
    # is the whole reason the caveat category exists.
    _split(h, "implicit d/dx off the curve", purecalc.t_implicit,
           ["x^2+y^2=25", "1", "1"], [],
           "dy/dx = -x/y", "dF/dx = 2*x", "so this point is not on the curve.")
    # integration by substitution: the check differentiates the answer back
    _split(h, "integration by substitution", purecalc.t_substitution,
           ["2x(x^2+1)^5", "x^2+1"], [],
           "(x^2+1)^6/6 + C", "du/dx = 2*x",
           "check by differentiating back: agrees")
    # the range is found by sampling, which can miss a spike
    _split(h, "domain and range", purecalc.t_domain_range,
           ["1/x", "-2", "2"], [],
           "range reached:", "on -2 <= x <= 2",
           "(sampled, so a sharp spike between")
    # f(f-inverse(x)) = x is the check on an inverse
    _split(h, "inverse function", purecalc.t_inverse,
           ["(3x-2)/4", "10"], [],
           "f-inverse(10) = 14", "f(x) = (3*x-2)/4",
           "check f(f-inv(x)) = x: yes")
    # 1.2 rad is not a small angle and the tool has to say so
    _split(h, "small-angle approximation", purecalc.t_small_angle,
           ["1.2"], [],
           "approx 1.2", "x = 1.2 rad", "not a small angle")
    # stationary points: f' and f'' are the method, the classification is the
    # answer
    _split(h, "stationary points", purecalc.t_stationary,
           ["x^3-3x"], [],
           "f' goes - to +: MINIMUM", "f''(x) = 6*x")
    # separation of variables: the two integrals are working, the general
    # solution is the answer, and "it passes through the initial point" is the
    # check on the constant
    _split(h, "separation of variables", purecalc.t_separable,
           ["1", "1", "0", "1"], [],
           "general solution (implicit):", "separate:  dy/g(y) = f(x) dx",
           "(checked: it passes through the")


# --------------------------------------------------------------- stat640 ----
def test_stat640_modes(h):
    import stat640
    # a tree diagram: the branch products are the answer, "these four sum to 1"
    # is the check that no branch was lost
    _split(h, "tree diagram", stat640.t_tree, ["0.3", "0.8", "0.4"], [],
           "P(A and B)   = 0.24", "multiply along a branch:",
           "these four sum to 1")
    # a Venn whose regions all work out: "regions sum" is the arithmetic check
    _split(h, "Venn, two events", stat640.t_venn,
           ["30", "12", "15", "5"], [0],
           "n(A only) = 7", "total = 30", "regions sum = 30")
    # and one whose figures do not add up at all: 20 + 15 - 2 = 33 > 30
    _split(h, "Venn with impossible figures", stat640.t_venn,
           ["30", "20", "15", "2"], [0],
           "THESE FIGURES DO NOT ADD UP.", "stated total = 30",
           "neither (total-n(A or B)) = -3")
    # reduce to linear form: r is the fit of the STRAIGHTENED points, which is
    # a caveat on how r may be quoted
    _split(h, "reduce to linear form", stat640.t_loglin,
           ["1 2 3 4", "3 12 27 48", None], [0],
           "model: y = 3 x^2", "so plot ln y against ln x", "STRAIGHTENED")
    # a discrete random variable whose probabilities do not total 1
    _split(h, "discrete RV", stat640.t_drv, ["1 2 3", "0.2 0.2 0.2"], [],
           "E[X] = ", "sum p = ", "WARN: sum p not 1")


# --------------------------------------------------------------- mech640 ----
def test_mech640_modes(h):
    import mech640
    # v^2 = u^2 + 2as gives plus-or-minus the root and only the positive one is
    # printed, so the direction has to be checked by hand
    brief, full = _both(h, mech640.suvat, ["2", None, "3", "4", None], [])
    h.has("suvat answer survives answer mode", brief, "v = 5.2915")
    h.has("suvat CAVEAT survives answer mode", brief, "(sqrt step: positive root")
    h.has("suvat caveat is in full output too", full, "(sqrt step: positive root")
    # a projectile range is reached at two angles, a and 90 - a
    _split(h, "projectile: find the launch", mech640.projectile_inverse,
           ["9.8", "100", "30"], [0],
           "u = 33.6394 m/s at 30 deg", "u = sqrt(Rg / sin 2a)",
           "gives the same range")
    # distance is not displacement once v changes sign
    _split(h, "distance vs displacement", mech640.distance_travelled,
           ["t^2-4t", "0", "5"], [],
           "distance     = 13", "so the motion reverses",
           "They differ because v changes sign.")
    # variable acceleration: v = 0 marks the turning points of s
    _split(h, "variable acceleration", mech640.kinematics,
           ["t^2-4t", "0", None], [1],
           "v(t) = t^2-4*t", "fixes the constant",
           "these are the turning points of s")


# ----------------------------------------------------------------- proof ----
def test_proof_modes(h):
    import proof
    # no counterexample in a finite range is not a proof, and saying so is the
    # single most important line the module prints
    _split(h, "disproof by counterexample", proof.t_counterexample,
           ["n^2+n+41", "1", "30"], [0],
           "No counterexample in that range.", "tested for n = 1 to 30",
           "That is NOT a proof.")
    # a sum proved by induction: the algebra is working, the verdict is the
    # answer
    _split(h, "induction on a sum", proof.t_induction_sum,
           ["n", "n(n+1)/2"], [],
           "PROVED for all n >= 1 by induction.", "INDUCTIVE STEP")
    # a claimed S(n) that is wrong must say so in both modes
    brief, full = _both(h, proof.t_induction_sum, ["n^2", "n(n+1)/2"], [])
    h.has("a wrong formula is called out in answer mode", brief,
          "S(n) is wrong")
    h.truthy("the failing algebra itself is working",
             "S(k+1) - S(k) = " not in ' '.join(brief))
    h.truthy("the failing algebra is shown in full",
             "S(k+1) - S(k) = " in ' '.join(full))
    # M^n by induction: the step is checked at five values of k, not proved
    # symbolically, and that limitation is a caveat on "PROVED"
    _split(h, "induction on M^n", proof.t_induction_matrix,
           ["1", "1", "0", "1", "1", "n", "0", "1"], [],
           "PROVED by induction", "BASE CASE n = 1",
           "holds at k = 1, 2, 3, 5 and 8.")
    # divisibility: the remainder sweep is working, the verdict is the answer
    _split(h, "induction on divisibility", proof.t_induction_divis,
           ["4^n-1", "3", "4"], [],
           "PROVED by induction.", "f(k+1) - 4 f(k) =")


def test_setting_is_restored(h):
    # the guard on this file itself: every helper above restores SHOW_WORKING,
    # so by the time the section ends the setting must be back on. If this ever
    # fails, every test that runs after this file is being run in answer mode.
    h.truthy("SHOW_WORKING is left on", h.casui.SHOW_WORKING)


SECTIONS = [
    ("H640 answer/working split", test_quadratic_modes),
    ("H640 pure: answer, working, caveat", test_pure640_modes),
    ("H640 functions and calculus: answer, working, caveat", test_purecalc_modes),
    ("H640 statistics: answer, working, caveat", test_stat640_modes),
    ("H640 mechanics: answer, working, caveat", test_mech640_modes),
    ("H640 proof: answer, working, caveat", test_proof_modes),
    ("the Working setting is restored", test_setting_is_restored),
]
