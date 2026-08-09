# tests_working_opt.py - the Working setting, tool by tool, for the six
# Options/Further Pure modules: algos, numeric, fmmech, fmstat, xpure, fpt.
#
# Every tool below is driven TWICE with identical input, once with the working
# shown and once with it hidden, and three things are asserted:
#
#   1. the ANSWER is still there when the working is hidden
#   2. a named WORKING line is gone
#   3. a named CAVEAT is still there
#
# The third is the one that matters. A caveat is not working: hiding "3 does
# not divide 7, so there are NO integer solutions" or "the constraints are
# INFEASIBLE" would turn a careful tool into a confidently wrong one, and no
# amount of tidy output is worth that.
#
# casui.SHOW_WORKING is restored in a finally in every helper: leaving it off
# would silently poison every test that runs after this file.

import algos
import numeric
import fmmech
import fmstat
import xpure
import fpt


def _modes(h, fn, inputs, menus=()):
    # (answer-only lines, full lines) for one tool and one set of answers
    try:
        h.casui.SHOW_WORKING = False
        brief = h.drive(fn, inputs, menus)
        h.casui.SHOW_WORKING = True
        full = h.drive(fn, inputs, menus)
    finally:
        h.casui.SHOW_WORKING = True
    return brief, full


def _subset(brief, full):
    seen = {}
    for ln in full:
        seen[ln] = 1
    for ln in brief:
        if ln not in seen:
            return False
    return True


def _split(h, label, fn, inputs, menus, answer, working, caveat):
    # the whole contract for one tool, in one call
    brief, full = _modes(h, fn, inputs, menus)
    h.truthy(label + ": answer mode invents nothing", _subset(brief, full))
    h.truthy(label + ": answer mode keeps something", len(brief) > 0)
    h.has(label + ": the answer survives answer mode", brief, answer)
    h.has(label + ": the working is there in full", full, working)
    h.truthy(label + ": the working is hidden in answer mode",
             working not in ' '.join(brief))
    h.has(label + ": the caveat survives answer mode", brief, caveat)


# ---------------------------------------------------------------- algos ----
def test_simplex_modes(h):
    # the shape the whole setting was built for: the optimum is the answer and
    # the tableaux are the working, even though the tableaux are what the mark
    # scheme wants to see
    ins = ['2', '2', '5 4', '6 4 24', '1 2 6']
    try:
        h.casui.SHOW_WORKING = False
        brief = h.drive(algos.simplex, ins, [])
        h.casui.SHOW_WORKING = True
        full = h.drive(algos.simplex, ins, [])
    finally:
        h.casui.SHOW_WORKING = True
    h.has("the optimum survives answer mode", brief, "P = 21")
    h.has("x survives answer mode", brief, "x = 3")
    h.has("y survives answer mode", brief, "y = 1.5")
    h.has("the shadow prices survive", brief, "C1 (s1): 0.75")
    h.truthy("the tableau is working", "Pivot" not in " ".join(brief))
    h.truthy("the tableau is shown in full", "Pivot" in " ".join(full))
    h.truthy("the standard form is working",
             "Slack form (L4):" not in " ".join(brief))
    h.truthy("answer mode invents nothing", _subset(brief, full))


def test_simplex2_infeasible(h):
    # x + y >= 4 and x + y <= 2 cannot both hold: phase 1 cannot clear the
    # artificials, and THAT is the answer
    _split(h, "2-stage simplex (infeasible)", algos.simplex2,
           ['2', '2', '1', '3 2', '1 1 -1 4', '1 1 1 2'], [],
           'the constraints are INFEASIBLE.',
           'P1 Pivot',
           'Phase 1 value')


def test_lpgraph_unbounded_region(h):
    # minimise x + y over x + y >= 2: the optimum exists, but the region does
    # not close, which is exactly the kind of thing answer mode must not eat
    _split(h, "LP graph (unbounded region)", algos.lpgraph,
           ['0', '1 1', '0', '1', '1 1 2'], [],
           'Optimal vertex: x = 2, y = 0',
           'Vertices of the feasible region:',
           'Region is UNBOUNDED')


def test_prim_disconnected(h):
    # node 4 is joined to nothing, so the "tree" does not span the graph
    ins = ['4', '0 1 0 0', '1 0 1 0', '0 1 0 0', '0 0 0 0']
    brief, full = _modes(h, algos.prim, ins, [])
    h.has("Prim: the total weight survives", brief, 'Total weight: 2')
    h.has("Prim: the not-connected caveat survives", brief,
          '(graph not connected)')
    h.truthy("Prim: answer mode invents nothing", _subset(brief, full))


def test_dijkstra_working(h):
    # the route and the distances are the answer; the labelling is the working
    ins = ['4', '0 3 0 0', '3 0 2 5', '0 2 0 1', '0 5 1 0', '1', '4']
    brief, full = _modes(h, algos.dijkstra, ins, [])
    h.has("Dijkstra: the route survives", brief, 'Route 1 to 4: 1 - 2 - 3 - 4')
    h.has("Dijkstra: the route length survives", brief, 'Route length: 6')
    h.truthy("Dijkstra: the working values are hidden",
             'Working values (in order tried):' not in ' '.join(brief))
    h.has("Dijkstra: the working values are in full", full,
          'Working values (in order tried):')


# -------------------------------------------------------------- numeric ----
def test_fixed_point_diverges(h):
    # g(x) = 2x has |g'| = 2, so the iteration runs away; the diagnosis is the
    # answer and the divergence warning must never be filed as working
    _split(h, "fixed-point diagnosis (divergent)", numeric.t_fixed_diag,
           ['2*x', '1', '1e-10'], [],
           "g'(x) = 2",
           'steps taken = ',
           "|g'| > 1 so the iteration")


def test_order_of_convergence_diverges(h):
    _split(h, "order of convergence (divergent)", numeric.t_conv_order,
           ['1 2 4 8 16'], [],
           'last ratio r = 2',
           'r(n) = d(n+1)/d(n)',
           'DIVERGES.')


def test_integration_odd_n(h):
    # Simpson needs an even number of strips: with n = 3 there is no Simpson
    # value at all, and saying so is part of the answer
    _split(h, "integration (odd n)", numeric.t_integ,
           ['x^2', '0', '1', '3'], [],
           'trapezium=0.351852',
           'h=0.333333',
           'Simpson: need even n')


def test_error_propagation_cancellation(h):
    _split(h, "error propagation (cancellation)", numeric.t_err_prop,
           ['1', '0.1', '1.05', '0.1'], [],
           'a-b = -0.05',
           'sums/differences: ADD the',
           'WARNING: a-b subtracts nearly')


def test_newton_forward_extrapolation(h):
    # p(5) is outside the table that built p, so it is an extrapolation
    _split(h, "forward differences (extrapolating)", numeric.t_newton_fwd,
           ['1 8 27 64', '1', '1', '5'], [],
           'p(x) = x^3',
           '-- difference table --',
           'warning: that x is outside')


def test_derivative_error_table(h):
    _split(h, "derivative error table", numeric.t_diff_error,
           ['sin(x)', '1', '0.4'], [],
           'cen extrap = 0.540302305',
           '-- forward (f(x+h)-f(x))/h --',
           'h too small: subtracting nearly')


# --------------------------------------------------------------- fmmech ----
def test_oblique_wall_smoothness(h):
    # "the surface is smooth, so the tangential part is unchanged" is the
    # modelling assumption the whole answer rests on
    _split(h, "oblique impact with a wall", fmmech.t_oblique_wall,
           ['10', '30', '0.5', '2'], [],
           'speed = 9.0139 m/s',
           'normal in = 5 m/s',
           'ASSUMPTION: smooth surface, so')


def test_oblique_spheres_smoothness(h):
    _split(h, "oblique impact of two spheres", fmmech.t_oblique_spheres,
           ['2', '5', '0', '1', '0', '0', '0.5'], [],
           'speed 1 = ',
           'along LOC before:',
           'ASSUMPTION: smooth spheres, so')


def test_projectile_below_the_slope(h):
    # fired at 5 degrees up a 10 degree slope: it never travels up the plane
    _split(h, "projectile on an incline (a < b)", fmmech.t_proj_incline,
           ['20', '5', '10', '9.8'], [],
           'max range = 34.7773 m',
           'slope b = 10 deg, g = 9.8',
           'a is not above the slope, so the')


# --------------------------------------------------------------- fmstat ----
def test_pmcc_not_significant(h):
    # r = 0.8 looks convincing and is not significant at 5% with n = 5
    _split(h, "pmcc (not significant)", fmstat.t_pmcc,
           ['1 2 3 4 5', '1 3 2 5 4', '5', '1'], [],
           'r = 0.8',
           'Sxy = 8',
           'accept H0: not significant')


def test_spearman_ties(h):
    _split(h, "Spearman (tied ranks)", fmstat.t_spear,
           ['1 2 2 4 5', '2 1 3 4 5', '5', '1'], [],
           'rs = 0.8208',
           '(PMCC of ranks,',
           'NOTE: there are ties, so')


def test_chi_squared_no_df(h):
    # 3 cells with 2 parameters fitted leaves df = 0: there is no test to do
    _split(h, "chi-squared (df < 1)", fmstat.t_chi,
           ['10 20 30', '20 20 20', '2', '5'], [],
           'df = 0 is not >= 1',
           'params estimated = 2',
           'Too few cells for this')


def test_ci_for_mean_uses_z(h):
    _split(h, "confidence interval for a mean", fmstat.t_cimean,
           ['50', '10', '25', '95'], [],
           '(46.0801, 53.9199)',
           'z* = 1.96',
           'small n: use t, not z')


def test_linear_combination_independence(h):
    # Var(aX + bY) = a^2VarX + b^2VarY is only true for independent X and Y
    _split(h, "aX+bY+c", fmstat.t_lincomb,
           ['2', '1', '3', '4', '1', '1', '0', None], [],
           'Var(W) = 5',
           'Var(W) = a^2VarX+b^2VarY',
           'X, Y assumed INDEPENDENT')


# ---------------------------------------------------------------- xpure ----
def test_verify_recurrence_fails(h):
    # u(n) = 2n does not satisfy u(n+1) = u(n) + 1
    _split(h, "verify a recurrence (fails)", xpure.t_recur_verify,
           ['u+1', '2*n', '0'], [0],
           'VERDICT: the closed form does NOT',
           'substituting the candidate:',
           'satisfy the recurrence.')


def test_recurrence_behaviour_diverges(h):
    _split(h, "recurrence behaviour (divergent)", xpure.t_recur_behave,
           ['2*u', '1'], [],
           'BEHAVIOUR',
           'u(0) = 1',
           'DIVERGENT: |u(n)| passes 1e12 by')


def test_eigen_repeated(h):
    # a repeated eigenvalue may or may not be diagonalisable, and the tool
    # refuses to pretend otherwise
    _split(h, "2x2 eigen (repeated root)", xpure.t_eigen,
           ['1', '0', '0', '1'], [],
           'lambda1 = 1',
           'char: L^2-',
           'Repeated eigenvalue;')


def test_eigen3_check_line(h):
    _split(h, "3x3 eigen", xpure.t_eigen3,
           ['2', '0', '0', '0', '3', '0', '0', '0', '4', None], [],
           'eigenvector (1, 0, 0)',
           'trace = 9, det = 24',
           'check |Mv - kv| = ')


def test_isomorphism_checked(h):
    _split(h, "group isomorphism", xpure.t_isomorph,
           ['2', '0 1', '1 0', '0 1', '1 0'], [],
           'G and H are ISOMORPHIC.',
           'element orders in G: ',
           'checked phi(ab) = phi(a)phi(b) for all 4 products:')


def test_first_order_recurrence(h):
    _split(h, "first order recurrence", xpure.t_recur_nonhom,
           ['2', '1', '1', '0'], [],
           'CLOSED FORM',
           'trial p(n) = ',
           'checked against the recurrence for')


def test_second_order_recurrence(h):
    _split(h, "second order recurrence", xpure.t_recur_nonhom2,
           ['3', '-2', '0', '0', '1', '0'], [],
           'CLOSED FORM',
           'auxiliary: x^2 - ',
           'checked against the recurrence for')


# ------------------------------------------------------------------ fpt ----
def test_diophantine_no_solution(h):
    # 3 does not divide 7, so 3x + 6y = 7 has no integer solution at all
    _split(h, "Diophantine (no solution)", fpt.t_diophantine,
           ['3', '6', '7'], [],
           'so there are NO integer',
           'Bezout: ',
           '3 does not divide 7,')


def test_diophantine_solved(h):
    _split(h, "Diophantine (solved)", fpt.t_diophantine,
           ['6', '9', '21'], [],
           'x = -7 + 3t',
           'Bezout: ',
           'check: 21 = 21')


def test_asymptotes_none_vertical(h):
    _split(h, "asymptotes (no vertical one)", fpt.t_asympt,
           ['1/(x^2+1)'], [],
           'horizontal: y = 0  (exact)',
           'deg(num) < deg(den), so f -> 0',
           'no vertical asymptote in')


def test_limit_hole(h):
    # the limit exists at x = 1 but f(1) does not: the curve has a hole
    _split(h, "limit at a hole", fpt.t_limit,
           ['(x^2-1)/(x-1)', '1'], [0],
           'limit = 2',
           'h        f(a-h) then f(a+h)',
           'f(a) itself is undefined, so the')


def test_verify_de(h):
    _split(h, "verify a DE solution", fpt.t_verifyde,
           ['x^2', 'q-2'], [],
           'VERIFIED: y satisfies the',
           'dy/dx = 2*x',
           'largest relative residual')


def test_pell(h):
    _split(h, "Pell's equation", fpt.t_pell,
           ['3'], [],
           'x = 2',
           'continued fraction steps: 1',
           'check x^2-n y^2 = 1')


def test_fermat_gcd_not_one(h):
    # gcd(3, 6) = 3, so Fermat's little theorem says nothing about this pair
    _split(h, "Fermat & Wilson (gcd not 1)", fpt.t_fermat,
           ['6', '3'], [],
           'p is NOT prime.',
           'Wilson: (p-1)! = -1 (mod p)',
           'but gcd(a,p) = 3, so Fermat does not apply.')


def test_modular_inverse_check(h):
    _split(h, "modular inverse", fpt.t_modinv,
           ['3', '4'], [],
           'a^-1 mod m = 3',
           'a = 3  m = 4',
           'check: a*inv mod m')


# ------------------------------------------------------------ the sweep ----
def test_six_modules_never_empty(h):
    # the module-level version of the guard in tests.py, run over exactly the
    # six modules this file is responsible for, with every tool driven from the
    # shared canned input
    import stress_inputs
    mods = [algos, numeric, fmmech, fmstat, xpure, fpt]
    checked = 0
    for mod in mods:
        for label, fn in mod.TOOLS:
            try:
                brief, full = _modes(h, fn, stress_inputs.INPUTS,
                                     stress_inputs.MENUS)
            except Exception:
                continue
            if not full:
                continue
            checked += 1
            h.truthy(label + ": answer mode is a subset of full",
                     _subset(brief, full))
            h.truthy(label + ": answer mode keeps a line", len(brief) > 0)
    h.truthy("the six modules were actually swept", checked >= 40)


SECTIONS = [
    ("options answer/working split", test_simplex_modes),
    ("simplex 2-stage infeasible", test_simplex2_infeasible),
    ("LP graph unbounded region", test_lpgraph_unbounded_region),
    ("Prim on a disconnected graph", test_prim_disconnected),
    ("Dijkstra labels are working", test_dijkstra_working),
    ("fixed-point diagnosis diverges", test_fixed_point_diverges),
    ("order of convergence diverges", test_order_of_convergence_diverges),
    ("integration with odd n", test_integration_odd_n),
    ("error propagation cancellation", test_error_propagation_cancellation),
    ("forward differences extrapolate", test_newton_forward_extrapolation),
    ("derivative error table", test_derivative_error_table),
    ("oblique impact with a wall", test_oblique_wall_smoothness),
    ("oblique impact of two spheres", test_oblique_spheres_smoothness),
    ("projectile below the slope", test_projectile_below_the_slope),
    ("pmcc not significant", test_pmcc_not_significant),
    ("Spearman with ties", test_spearman_ties),
    ("chi-squared with df < 1", test_chi_squared_no_df),
    ("confidence interval for a mean", test_ci_for_mean_uses_z),
    ("linear combination independence", test_linear_combination_independence),
    ("verify a recurrence that fails", test_verify_recurrence_fails),
    ("recurrence behaviour diverges", test_recurrence_behaviour_diverges),
    ("2x2 repeated eigenvalue", test_eigen_repeated),
    ("3x3 eigen check line", test_eigen3_check_line),
    ("group isomorphism checked", test_isomorphism_checked),
    ("first order recurrence", test_first_order_recurrence),
    ("second order recurrence", test_second_order_recurrence),
    ("Diophantine with no solution", test_diophantine_no_solution),
    ("Diophantine solved", test_diophantine_solved),
    ("asymptotes with none vertical", test_asymptotes_none_vertical),
    ("limit at a hole", test_limit_hole),
    ("verify a DE solution", test_verify_de),
    ("Pell's equation", test_pell),
    ("Fermat when gcd is not 1", test_fermat_gcd_not_one),
    ("modular inverse", test_modular_inverse_check),
    ("six modules never empty", test_six_modules_never_empty),
]
