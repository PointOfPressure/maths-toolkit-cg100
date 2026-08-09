def _both(h, fn, inputs, menus):
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
    _split(h, "triangle SSA", pure640.t_triangle, ["7", "8", "50"], [3],
           "a = 7   A = 50 deg", "sine rule: a/sinA", "AMBIGUOUS CASE")
    _split(h, "trig by identity", pure640._trig_identity,
           ["2", "1", "-1", "0", "360"], [0, 0],
           "ALL SOLUTIONS in order:", "let u = sin x",
           "checked back in the original")
    _split(h, "impossible trig root", pure640._trig_identity,
           ["1", "-3", "0", "0", "360"], [0, 0],
           "0, 180, 360", "let u = sin x", "cannot exceed 1")
    _split(h, "tangent to a circle", pure640._circle_tangent,
           ["0", "0", "3", "4"], [],
           "y = -0.75x + 6.25", "radius gradient  = 1.3333", "(should be -1)")
    _split(h, "circle through 3 points", pure640._circle_3pts,
           ["0", "0", "4", "0", "0", "3"], [],
           "centre (2, 1.5)", "angle in a semicircle",
           "all three points on the circle: yes")
    _split(h, "binomial with real n", pure640.t_binom, ["0.5", "4"], [1],
           "x^1: 0.5", "(1 + x)^0.5", "valid for |x| < 1")
    _split(h, "rationalise a denominator", pure640.t_surds,
           ["1", "1", "1", "2"], [3],
           "= -1 + sqrt(2)", "CONJUGATE 1 - sqrt(2)")


def test_purecalc_modes(h):
    import purecalc
    _split(h, "implicit d/dx off the curve", purecalc.t_implicit,
           ["x^2+y^2=25", "1", "1"], [],
           "dy/dx = -x/y", "dF/dx = 2*x", "so this point is not on the curve.")
    _split(h, "integration by substitution", purecalc.t_substitution,
           ["2x(x^2+1)^5", "x^2+1"], [],
           "(x^2+1)^6/6 + C", "du/dx = 2*x",
           "check by differentiating back: agrees")
    _split(h, "domain and range", purecalc.t_domain_range,
           ["1/x", "-2", "2"], [],
           "range reached:", "on -2 <= x <= 2",
           "(sampled, so a sharp spike between")
    _split(h, "inverse function", purecalc.t_inverse,
           ["(3x-2)/4", "10"], [],
           "f-inverse(10) = 14", "f(x) = (3*x-2)/4",
           "check f(f-inv(x)) = x: yes")
    _split(h, "small-angle approximation", purecalc.t_small_angle,
           ["1.2"], [],
           "approx 1.2", "x = 1.2 rad", "not a small angle")
    _split(h, "stationary points", purecalc.t_stationary,
           ["x^3-3x"], [],
           "f' goes - to +: MINIMUM", "f''(x) = 6*x")
    _split(h, "separation of variables", purecalc.t_separable,
           ["1", "1", "0", "1"], [],
           "general solution (implicit):", "separate:  dy/g(y) = f(x) dx",
           "(checked: it passes through the")


def test_stat640_modes(h):
    import stat640
    _split(h, "tree diagram", stat640.t_tree, ["0.3", "0.8", "0.4"], [],
           "P(A and B)   = 0.24", "multiply along a branch:",
           "these four sum to 1")
    _split(h, "Venn, two events", stat640.t_venn,
           ["30", "12", "15", "5"], [0],
           "n(A only) = 7", "total = 30", "regions sum = 30")
    _split(h, "Venn with impossible figures", stat640.t_venn,
           ["30", "20", "15", "2"], [0],
           "THESE FIGURES DO NOT ADD UP.", "stated total = 30",
           "neither (total-n(A or B)) = -3")
    _split(h, "reduce to linear form", stat640.t_loglin,
           ["1 2 3 4", "3 12 27 48", None], [0],
           "model: y = 3 x^2", "so plot ln y against ln x", "STRAIGHTENED")
    _split(h, "discrete RV", stat640.t_drv, ["1 2 3", "0.2 0.2 0.2"], [],
           "E[X] = ", "sum p = ", "WARN: sum p not 1")


def test_mech640_modes(h):
    import mech640
    brief, full = _both(h, mech640.suvat, ["2", None, "3", "4", None], [])
    h.has("suvat answer survives answer mode", brief, "v = 5.2915")
    h.has("suvat CAVEAT survives answer mode", brief, "(sqrt step: positive root")
    h.has("suvat caveat is in full output too", full, "(sqrt step: positive root")
    _split(h, "projectile: find the launch", mech640.projectile_inverse,
           ["9.8", "100", "30"], [0],
           "u = 33.6394 m/s at 30 deg", "u = sqrt(Rg / sin 2a)",
           "gives the same range")
    _split(h, "distance vs displacement", mech640.distance_travelled,
           ["t^2-4t", "0", "5"], [],
           "distance     = 13", "so the motion reverses",
           "They differ because v changes sign.")
    _split(h, "variable acceleration", mech640.kinematics,
           ["t^2-4t", "0", None], [1],
           "v(t) = t^2-4*t", "fixes the constant",
           "these are the turning points of s")


def test_proof_modes(h):
    import proof
    _split(h, "disproof by counterexample", proof.t_counterexample,
           ["n^2+n+41", "1", "30"], [0],
           "No counterexample in that range.", "tested for n = 1 to 30",
           "That is NOT a proof.")
    _split(h, "induction on a sum", proof.t_induction_sum,
           ["n", "n(n+1)/2"], [],
           "PROVED for all n >= 1 by induction.", "INDUCTIVE STEP")
    brief, full = _both(h, proof.t_induction_sum, ["n^2", "n(n+1)/2"], [])
    h.has("a wrong formula is called out in answer mode", brief,
          "S(n) is wrong")
    h.truthy("the failing algebra itself is working",
             "S(k+1) - S(k) = " not in ' '.join(brief))
    h.truthy("the failing algebra is shown in full",
             "S(k+1) - S(k) = " in ' '.join(full))
    _split(h, "induction on M^n", proof.t_induction_matrix,
           ["1", "1", "0", "1", "1", "n", "0", "1"], [],
           "PROVED by induction", "BASE CASE n = 1",
           "holds at k = 1, 2, 3, 5 and 8.")
    _split(h, "induction on divisibility", proof.t_induction_divis,
           ["4^n-1", "3", "4"], [],
           "PROVED by induction.", "f(k+1) - 4 f(k) =")


def test_setting_is_restored(h):
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
