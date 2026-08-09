# OCR B (MEI) H640 / H645 specification audit

Every content statement in the two specifications, mapped against what this
toolkit actually does.

## Sources

| Document | Source | Status |
|---|---|---|
| A Level Mathematics B (MEI) **H640**, Version 3 (October 2025) | `https://www.ocr.org.uk/Images/308740-specification-accredited-a-level-gce-mathematics-b-mei-h640.pdf` | Re-downloaded for this pass (HTTP 200, 2 622 684 bytes, 91 pages) and text-extracted with `pdftotext -layout`. Content section 2f, pp. 22-65. |
| A Level Further Mathematics B (MEI) **H645**, Version 2.1 (March 2026) | `https://www.ocr.org.uk/images/308768-specification-accredited-a-level-gce-further-mathematics-b-mei-h645.pdf` | Re-downloaded for this pass (HTTP 200, 10 380 364 bytes, 171 pages) and text-extracted with `pdftotext -layout`. Content sections 2c-2k, pp. 18-127. |

All eight optional papers are inside the single H645 document, not published
separately: Core Pure Y420 is section 2c, Mechanics Major Y421 is 2d,
Statistics Major Y422 is 2e, Mechanics Minor Y431 is 2f, Statistics Minor Y432
is 2g, Modelling with Algorithms Y433 is 2h, Numerical Methods Y434 is 2i,
Extra Pure Y435 is 2j and Further Pure with Technology Y436 is 2k. Nothing was
unreachable; nothing in this document is reconstructed from memory or from the
specification-at-a-glance pages.

Both documents are the same versions the previous pass used, and the statement
codes and wording were re-checked against the fresh extraction rather than
carried over. Items marked `*` in the Ref. column of the spec are unnumbered
assumed-knowledge/GCSE statements; they are listed here with the code `*` and a
bracketed topic.

Note on Y436: OCR is withdrawing Further Pure with Technology. The final first
teach date is September 2026 and the last assessment is Summer 2028, with no
resit. It is audited in full anyway, because it is still examinable.

## Snapshot

**This audit describes the working tree at 2026-08-09, commit `34fc5fd`.**

Every verdict below was derived while HEAD was `2755493`. Two commits landed
during the pass: `38b3d0b` "Make the README's install list a tested artefact
too" and `34fc5fd` "Render the screens on a PC, and fix the two layout faults
that showed up". Both were re-read afterwards. They touch `casui.py`,
`casrender.py`, `.gitignore`, `README.md`, `tests.py` and the new PC-only
`casioshot.py`, and they change font metrics, the symbol-picker layout, the
`hold()` prompt and the graph axis labels. No `TOOLS` list, no section module
and no CAS routine is altered by either, so no verdict moves.

The previous pass was written against commit `e1b6812`. Between the two,
roughly 120 tools landed across `pure640`, `purecalc`, `stat640`, `mech640`,
`vcplx`, `vectors`, `matrix`, `diffeq`, `fmmech`, `fmstat`, `numeric`, `algos`,
`xpure`, `fpt` and the new `proof` module, and every verdict below has been
re-derived from the current function bodies rather than edited from the old
file. The headline change: distinct MISSING statements fall from 148 to 37.

The defect the previous pass recorded is fixed. `matrix.t_invariant` and
`matrix.t_transform3` are now both in `matrix.TOOLS` and reachable from the
menu, which closes Core Pure `Pm6` and upgrades `m4`.

## Method and conventions

- **Toolkit capability** was read from the `TOOLS = [...]` registry and the
  function bodies of `pure640.py`, `purecalc.py`, `stat640.py`, `mech640.py`,
  `proof.py`, `vcplx.py`, `matrix.py`, `vectors.py`, `polyroots.py`,
  `series.py`, `hyper.py`, `polar.py`, `diffeq.py`, `fmmech.py`, `fmstat.py`,
  `numeric.py`, `algos.py`, `xpure.py`, `fpt.py`, plus the CAS
  (`caseng.simplify` / `diff` / `subst` / `invert`, `cascalc.integ` / `defint`
  / `solve`, `caspoly.expand` / `factor` / `collect` / `partial`) and the
  `casui.cas_section` operations menu.
- A function that exists but is not in a `TOOLS` list is treated as absent,
  because the user cannot reach it.
- A statement may be served by a module filed under another paper. That counts:
  the toolkit is one application and every menu is reachable from every other.
  Where the route is not the obvious one it is named in the row.
- Where the label was ambiguous the code was **executed** against test inputs
  rather than judged from its name. The findings that follow from that are
  recorded in "Facts established by test" below.
- Verdicts: `COVERED` a tool does this; `PARTIAL` a tool touches it but leaves
  a real gap (the gap is stated); `MISSING` nothing does this; `N/A` not a
  calculator task.

### Facts established by test

These were verified by running the modules against this tree, not inferred:

| Behaviour | Result |
|---|---|
| `cascalc.solve` search window | unchanged: real roots only, sampled over **[-20, 20]** (radian mode) or [-360, 360] (degree mode). `solve(x-100)` returns `[]`, `solve(x-19)` returns 19. This limit propagates into every tool that solves, including the stationary-point, modulus, mean-value and inverse-function tools. |
| CAS menu `Simplify` | now calls `cascalc.tidy`, not `caseng.simplify`, so numeric fractions do combine: `1/2+1/3` -> `5/6`. |
| Surds | still not reduced or rationalised: `sqrt(8)` stays `sqrt(8)` under both `simplify` and `tidy`. |
| `caspoly.cancel` | still does **not** cancel `(x^2-1)/(x-1)`. |
| `caseng.invert` | still returns `None` for `(x-1)/(x+2)`. |
| Inverse-trig integral forms | `1/(x^2+1)` -> `atan(x)` and `1/(x^2+4)` -> `atan(x/2)/2` both work. |
| Inverse-hyperbolic and arcsin integral forms | `1/sqrt(1-x^2)`, `1/sqrt(x^2+1)`, `1/sqrt(x^2-1)`, `1/sqrt(x^2+4)` and `tanh(x)` all still return `None`. |
| New `cascalc.integ` power-rewriting | `sqrt(x)` -> `2x^(3/2)/3`, `1/x^3` -> `-1/(2x^2)`, `3/sqrt(x)` -> `6x^(1/2)`. This is what makes the volume-of-revolution and centre-of-mass integrals come out exactly. |
| Automatic reverse chain rule, non-linear inner function | still **fails**: `cascalc.integ` returns `None` for `x e^(x^2)` and `x(1+x^2)^8`. `purecalc.t_substitution` handles both once the user supplies u. |
| `caseng.evalf` environment | `env` is now consulted before the positional `x`, so a two-variable tool can pin both x and y. This is what makes `xpure.t_partial` a real partial derivative rather than a one-variable difference quotient. |
| Cartesian tangents and normals | `purecalc.t_implicit` accepts `y = x^2` as an equation in x and y: dF/dx = -2x, dF/dy = 1, dy/dx = 2x, then the tangent and normal at a point. So the implicit tool is also the plain-cartesian tangent tool. |
| `caseng.diff` third variable | differentiates with respect to `z` and `evalf` binds it, but no registered tool asks for a third variable, so `g(x, y, z)` surfaces remain out of reach. |
| `casutil.FACT_MAX` | 500, but `fpt.t_fermat` computes `(p-1)! mod p` by reducing at every step, so the cap no longer bites for Wilson's theorem (its own limit is p <= 20000). |

---

## H640 Pure Mathematics (assessed across components 01, 02 and 03)

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `a10` | Use and manipulate surds | `tidy` now combines numeric fractions but there is still no exact-surd arithmetic; `sqrt(8)` stays `sqrt(8)` (tested) | MISSING |
| `a11` | Rationalise the denominator of a surd | No exact-surd engine | MISSING |
| `a14` | Understand and use proportional relationships (y = kx, y = k/x) | No tool finds k or handles proportion | MISSING |
| `g9` | Find the point(s) of intersection of a line and a circle | `pure640.t_simul` still offers only line + `y = px^2+qx+r`; the circle case is not built | MISSING |
| `g11` | Circle properties: angle in semicircle, perpendicular bisector of chord, tangent perpendicular to radius | No circle-geometry tool | MISSING |
| `g14` | Equation of a circle in parametric form | `pure640.t_circle` does centre+r and equation only; no parametric preset | MISSING |
| `s7` | Generate a sequence from a formula for the kth term or a recurrence | Only arithmetic/geometric closed forms; `xpure.t_recur` is 2nd-order linear only | MISSING |
| `s10` | Recognise increasing, decreasing and periodic sequences | No sequence-behaviour tool | MISSING |
| `E7` | Reduce y = a x^n and y = a b^x to linear form by taking logs | No log-transform of a data list; `t_regress` and `t_scatter` take raw x,y only | MISSING |
| `Ma7` | Solve linear inequalities in one variable; represent graphically | `pure640.t_inequality` solves the linear case and flips the sign correctly when a < 0, but nothing draws the region for a two-variable inequality such as y > x + 1. `algos.lpgraph` shades regions but always adds x >= 0 and y >= 0 and needs an objective, so it is not the general drawer | PARTIAL |
| `a8` | Solve quadratic inequalities; represent graphically | `t_inequality` now gives the solution interval explicitly, choosing between and outside the roots from the sign of a; the graphical representation is still described in words, not drawn | PARTIAL |
| `a12` | Laws of indices for all rational exponents | `tidy` folds numeric powers; no symbolic index-law manipulation | PARTIAL |
| `a13` | Negative, zero and fractional indices | Evaluable, and `integ` now handles them; not manipulable symbolically | PARTIAL |
| `a16` | Simplify rational expressions (factorise, cancel) | `Expand`, `Factorise` and `Collect like terms` all work, but `caspoly.cancel` still does not cancel `(x^2-1)/(x-1)` (tested) | PARTIAL |
| `*` (Algebra) | Change the subject of a formula | `caseng.invert`, behind `purecalc.t_inverse`, rearranges exactly when the variable occurs once; still `None` for `(x-1)/(x+2)` (tested), and there is no rearrange-for-any-symbol tool | PARTIAL |
| `Mf1` | Add, subtract, multiply and divide polynomials | `Expand brackets` and `Collect like terms` work; `caspoly.pdivmod` exists but is still not on any menu, so polynomial long division cannot be reached | PARTIAL |
| `f7` | Solve simple inequalities involving the modulus function | `purecalc.t_modulus` solves \|f(x)\| = k and graphs it, which gives the boundary points; the inequality itself is never stated | PARTIAL |
| `C2` | Find intersection points of two graphs | You must form f-g by hand and use `Solve`, limited to [-20, 20]; no two-curve tool | PARTIAL |
| `C4` | Sketch and interpret graphs of polynomial functions | `Graph` auto-scales and `t_stationary` now names the turning points, but the two are separate steps and the graph is not annotated | PARTIAL |
| `C6` | Sketch and interpret y = a/x and y = a/x^2 including asymptotes | `Graph` plots them; no asymptote detection or reporting | PARTIAL |
| `Mg8` | Point(s) of intersection of a line and a curve, or of two curves | `pure640._simul_linquad` still covers only line + `y = px^2+qx+r` | PARTIAL |
| `g13` | Convert between cartesian and parametric forms | `purecalc.t_param_cartesian` converts parametric -> cartesian when x(t) inverts and prints the sin^2+cos^2 route when it does not; the reverse direction is not implemented | PARTIAL |
| `s4` | Write (a+bx)^n as a^n(1+bx/a)^n and expand | `_binom_int` covers integer n; `_binom_real` only does `(1+x)^n`, so rational n with a != 1 is not supported | PARTIAL |
| `s5` | Use binomial expansions with n rational to approximate (a+bx)^n | Coefficients of `(1+x)^n` only; no substitution/evaluation step | PARTIAL |
| `s9` | Understand and use sigma notation | `series.py` has closed forms for Sum r, r^2, r^3 and the method of differences; no general Sigma evaluator | PARTIAL |
| `s11` | Convergent and divergent sequences/series | `t_geo` reports the \|r\|<1 condition and S(inf); `numeric.t_conv_order` classifies a numeric sequence; nothing tests a general series | PARTIAL |
| `t9` | Definitions, domains and ranges of arcsin, arccos, arctan | `asin`/`acos`/`atan` evaluate, graph and differentiate; `purecalc.t_domain_range` samples a range but nothing states the principal-value domains | PARTIAL |
| `t14` | Relationships between the graphs of sin/cos/tan and their reciprocal and inverse functions | All six functions graph; nothing reports domains, ranges or asymptote positions, or draws a pair together | PARTIAL |
| `t15` | Use tan^2 + 1 = sec^2 and cot^2 + 1 = cosec^2 | `_trig_compound` and `t_exact_trig` both print them and either side can be evaluated or graphed; there is still no symbolic identity manipulation to *apply* them | PARTIAL |
| `Mt16` | Identities for sin(A+-B), cos(A+-B), tan(A+-B) | `pure640._trig_compound` prints all six and `_trig_expand` checks each numerically at chosen A and B; nothing expands them symbolically | PARTIAL |
| `t17` | Identities for sin 2A, cos 2A, tan 2A | Same card, including the rearranged forms for integration and the half-angle t-formulae; still no symbolic expansion | PARTIAL |
| `t18` | Express a cos t +- b sin t as R cos(t +- alpha) / R sin(t +- alpha) | `_trig_rform` produces the `R sin(x + alpha)` form only; the cosine forms and the sketch are not produced | PARTIAL |
| `t19` | Use trigonometric identities to solve equations | `_trig_general` now solves `sin/cos/tan(px + q) = k` over any interval in either angle unit, which covers multiple angles; an equation that first has to be reduced by an identity (3 sin 2x = cos x, or a quadratic in sin x) still cannot be entered | PARTIAL |
| `E4` | Understand and apply the laws of logarithms | `_log_laws` is a reference card; it cannot combine or split logs | PARTIAL |
| `E11` | Solve problems involving exponential growth and decay | Evaluation, graphing and `t_separable` for the differential-equation form; no model-fitting from data (see `E7`) | PARTIAL |
| `c4` | Sketch the gradient function for a given curve | Differentiate then Graph, in two manual steps | PARTIAL |
| `c8` | Increasing and decreasing functions | `t_stationary` prints f'(x) and tests its sign either side of each stationary point; it does not report the increasing and decreasing intervals as such | PARTIAL |
| `c15` | Rates of change using the chain rule, dy/dx = 1/(dx/dy) | Chain rule differentiates; connected-rates problems are set up by hand | PARTIAL |
| `c17` | Concave upwards/downwards sections | `t_stationary` gives f''(x) and every root of f''=0 with a sign-change test, so the boundaries are found; the intervals themselves are not named | PARTIAL |
| `c23` | Area between a curve and the x-axis including regions below the axis | `Definite integral a..b` returns the signed value. `mech640.distance_travelled` does perform exactly this split-at-the-roots computation, but only for a v(t) in a mechanics context | PARTIAL |
| `c26` | Area between two curves; integration with respect to y | f-g must be formed by hand; y-integration works only by renaming the variable (as `t_revolution` does) | PARTIAL |
| `c35` | Use rectangles to find upper and lower bounds for an area | `numeric.t_integ` gives midpoint and trapezium and `t_integ_error` tabulates them as h halves; no explicit upper/lower rectangle sums | PARTIAL |
| `v2` | Add and subtract vectors, including using a diagram | `vectors.py` still has no add/subtract entry; `matrix.py` A+B works if vectors are entered as column matrices | PARTIAL |
| `v6` | Use vectors to solve problems in pure and applied contexts | The primitives exist and `fmmech.t_relative` does the 2-D kinematics case; general problem set-up is manual | PARTIAL |
| `a9` | Express solutions of inequalities using and/or or set notation | `t_inequality` prints exactly the forms the spec asks for: `lo <= x <= hi` between the roots, `x <= lo or x >= hi` outside them, with the strictness carried through | COVERED |
| `t3` | Area of a triangle = 1/2 ab sin C | `pure640.t_triangle` prints the area from (1/2)ab sin C in every one of its four cases | COVERED |
| `t4` | Sine rule and cosine rule | `pure640.t_triangle` solves SSS, SAS, ASA and SSA, names which rule it used, prints the common ratio for the sine rule, rejects impossible side triples, and flags the SSA ambiguous case with the second triangle | COVERED |
| `t11` | Arc length s = r*theta and sector area A = 1/2 r^2 theta | `pure640.t_arc_sector` gives arc, sector area, chord, segment area and sector perimeter, converting from degrees first and saying so | COVERED |
| `t7` | Solve simple trig equations in a given interval; principal values | `pure640._trig_general` takes any interval, degrees or radians, and a multiple angle, prints the principal value and the period in x, and lists every root | COVERED |
| `t13` | Definitions and graphs of sec, cosec and cot | All three are in `caslex.UFUNCS`: they parse, evaluate, graph, differentiate (`d/dx cot(x)` -> `-cosec(x)^2`, tested) and, for sec, integrate | COVERED |
| `*` (Trigonometry) | Solve right-angled triangles using trig ratios and Pythagoras | `t_triangle` handles them as SSS/SAS/ASA cases; the SSS branch rejects lengths that cannot form a triangle | COVERED |
| `c6` | Second derivative as rate of change of gradient | `purecalc.t_stationary` prints f''(x) symbolically; `t_param_diff` gives d2y/dx2 for a parametric curve | COVERED |
| `c7` | Use differentiation to find stationary points and classify them | `purecalc.t_stationary` solves f'(x)=0 and classifies each root from the sign of f' either side rather than from f'', which is what stops a degenerate point like x^3 being reported as a maximum | COVERED |
| `c9` | Equation of the tangent and normal to a curve | `purecalc.t_implicit` accepts `y = f(x)` and prints the tangent and normal at a point (tested); `t_param_diff` does the parametric case | COVERED |
| `c18` | Points of inflection | `t_stationary` solves f''(x)=0 and tests whether f'' actually changes sign there, reporting "no sign change: not an inflection" when it does not | COVERED |
| `c21` | Find the constant of integration from a given point | `purecalc.t_constant` integrates f'(x), fixes C from a point, prints the working line `y0 = F(x0) + C`, and checks the result passes through | COVERED |
| `C5` | Use stationary points when curve sketching | `t_stationary` gives the coordinates and the nature of every stationary point in the search range | COVERED |
| `C9` | Stationary points of inflection | `t_stationary` names them: when f' keeps its sign through a root of f' it reports POINT OF INFLECTION (stationary) | COVERED |
| `e5` | Understand that not all iterations converge; failure of Newton-Raphson | `numeric.t_cobweb` draws the staircase or cobweb and names which it is from the sign of g'; `t_fixed_diag` reports \|g'\| and says whether the iteration converges and why | COVERED |
| `p2` | Disprove a conjecture by counter-example | `proof.t_counterexample` searches a chosen range for a counterexample to four standard claim shapes and prints the sentence to write down; when it finds none it says plainly that this is not a proof | COVERED |
| `v5` | Calculate the distance between two points in 2-D/3-D | `pure640.t_coord` in 2-D; `vectors.t_lineeq` through two points prints \|d\|, which is the 3-D distance | COVERED |
| `a15` | Express algebraic fractions as partial fractions | CAS `Partial fractions` -> `caspoly.partial`; correct on distinct linear factors and on the repeated factor case | COVERED |
| `f4` | Understand and use composite functions gf(x) | `purecalc.t_composite` gives fg(x) and gf(x) and evaluates both | COVERED |
| `f5` | Understand and use inverse functions and their graphs | `purecalc.t_inverse` inverts exactly by undoing steps when x occurs once, falls back to numeric solving otherwise, and checks f(f-inv(x)) = x | COVERED |
| `t12` | Small angle approximations sin x ~ x, cos x ~ 1 - x^2/2, tan x ~ x | `purecalc.t_small_angle` prints exact against approximate with absolute and percentage error, and comments on validity | COVERED |
| `c16` | Differentiate a relation implicitly | `purecalc.t_implicit` gives dF/dx, dF/dy and dy/dx, then the tangent and normal at a point with an on-the-curve check | COVERED |
| `c28` | Integration by substitution in other (non-obvious) cases | `purecalc.t_substitution` changes variable, integrates in u, back-substitutes and verifies by differentiating | COVERED |
| `c32` | Find general/particular solutions of first order differential equations by separating variables | `purecalc.t_separable` integrates both sides, fixes C from an initial condition and makes y explicit where the y-integral inverts | COVERED |
| `f2` | Factor theorem; factorise cubics/quartics | CAS `Factorise` -> `caspoly.factor` over the rationals | COVERED |
| `f6` | Understand and use the modulus function | `purecalc.t_modulus` solves f(x) = k and f(x) = -k and graphs y = \|f(x)\| | COVERED |
| `MC1` | Understand and use graphs of functions | CAS `Graph` + `Table of values` | COVERED |
| `MC7` | Sketch curves y = f(x)+a, f(x+a), af(x), f(ax) | `purecalc.t_transform` builds y = a f(bx+c) + d, names the transformations in the correct order and graphs the result | COVERED |
| `C8` | Effect of combined transformations | `t_transform` takes all four parameters at once | COVERED |
| `g15` | Gradient of a curve defined parametrically | `purecalc.t_param_diff` gives dx/dt, dy/dt, dy/dx, d2y/dx2, the point, tangent and normal at a chosen t | COVERED |
| `c27` | Integration by substitution where the process reverses the chain rule | `t_substitution` handles these once the user names u; the automatic CAS `Integrate` still returns `None` for the same integrands | COVERED |
| `*` (Algebra) | Solve linear equations in one unknown | `pure640.t_quadratic` with a=0 | COVERED |
| `Ma2` | Solve quadratic equations | `t_quadratic` - roots, discriminant, completed square, vertex, complex roots | COVERED |
| `a3` | Find the discriminant and understand its significance | Same tool prints b^2-4ac and the root-nature conclusion | COVERED |
| `a4` | Solve linear simultaneous equations in two unknowns | `pure640._simul_linear` (Cramer, with singular detection) | COVERED |
| `a5` | Simultaneous equations, one linear one quadratic | `pure640._simul_linquad` | COVERED |
| `C3` | Completing the square; y = a(x+p)^2 + q | `t_quadratic` | COVERED |
| `*` (Coord geom) | Understand and use y = mx + c | `pure640.t_coord` | COVERED |
| `Mg1` | Gradient conditions for parallel and perpendicular lines | `t_coord` prints m and the perpendicular gradient | COVERED |
| `g2` | Distance between two points | `t_coord` | COVERED |
| `g3` | Coordinates of the midpoint of a line segment | `t_coord` | COVERED |
| `g4` | Form the equation of a straight line | `t_coord` | COVERED |
| `g5` | Draw a line given its equation | CAS `Graph` | COVERED |
| `g6` | Point of intersection of two lines | `_simul_linear` | COVERED |
| `g10` | Equation of a circle (x-a)^2 + (y-b)^2 = r^2 | `pure640.t_circle` both directions | COVERED |
| `Ms1` | Binomial expansion of (a+b)^n for positive integer n | `pure640._binom_int` | COVERED |
| `s2` | n! and nCr notation | `stat640.t_ncrfact` | COVERED |
| `s3` | Binomial expansion of (1+x)^n for rational n | `pure640._binom_real` | COVERED |
| `s12` | Arithmetic sequences and series | `pure640.t_arith` | COVERED |
| `s13` | Standard AP formulae for the nth term and sum | `t_arith` | COVERED |
| `s14` | Geometric sequences and series | `pure640.t_geo` | COVERED |
| `s15` | Standard GP formulae for the nth term and sum | `t_geo` | COVERED |
| `s16` | Condition for a GP to converge; sum to infinity | `t_geo` | COVERED |
| `Mt1` | Definitions of sin, cos, tan for any angle | Calculate section with the DEG/RAD toggle | COVERED |
| `t2` | Graphs of sin, cos, tan | CAS `Graph` | COVERED |
| `*` (Trig) | Exact values of sin, cos, tan for 0, 30, 45, 60, 90 degrees | `pure640._trig_exact` and `purecalc.t_exact_trig` | COVERED |
| `Mt8` | Exact values of sin, cos, tan for common angles | `purecalc.t_exact_trig` runs to 360 degrees with the radian column | COVERED |
| `t10` | Definition and use of the radian | Global DEG/RAD toggle; `casutil.rad`/`deg`; `t_arc_sector` insists on radians and converts | COVERED |
| `ME1` | The function y = a^x and its graph | CAS `Graph` | COVERED |
| `E2` | Convert between index and logarithmic form | `pure640.t_log` | COVERED |
| `E5` | Values of log_a a and log_a 1 | `_log_eval` and the reference card | COVERED |
| `E6` | Solve equations of the form a^x = b | `_log_solve` | COVERED |
| `ME8` | The function y = e^x and its graph | CAS `exp`, `Graph` | COVERED |
| `E9` | Gradient of e^kx is k e^kx | CAS `Differentiate` | COVERED |
| `E10` | The function y = ln x and its graph | CAS `ln`, `Graph` | COVERED |
| `Mc1` | Gradient of a curve at a point as the limit of chord gradients | CAS `Gradient at a point` (step scaled with \|x\|) | COVERED |
| `c2` | Gradient of the tangent equals the derivative | Same | COVERED |
| `c3` | Derivative of f(x) as the rate of change | CAS `Differentiate` | COVERED |
| `c5` | Differentiate y = kx^n and related sums/differences | CAS `Differentiate` | COVERED |
| `Mc10` | Differentiate e^kx, a^kx and ln x | CAS `Differentiate` | COVERED |
| `c11` | Differentiate trigonometric functions | CAS `Differentiate` | COVERED |
| `c12` | Product rule | `caseng._d` | COVERED |
| `c13` | Quotient rule | `caseng._d` | COVERED |
| `c14` | Chain rule for composite functions | `caseng._d` | COVERED |
| `Mc19` | Integration as the reverse of differentiation | CAS `Integrate (+ C)` | COVERED |
| `c20` | Integrate kx^n and related sums/differences | `cascalc.integ`, now including negative and fractional powers written as fractions or surds (tested) | COVERED |
| `c22` | Indefinite and definite integrals | Both operations exist | COVERED |
| `Mc24` | Integrate e^kx, 1/x, sin kx, cos kx and related sums | `cascalc.integ` | COVERED |
| `c29` | Integration by parts in simple cases | `cascalc._byparts` with a depth cap of 3, plus `_cyclic` for e^x sin x | COVERED |
| `c30` | Integrate using partial fractions | `cascalc.integ_rational` | COVERED |
| `Me1` | Locate roots of f(x)=0 by a change of sign | `numeric.t_bisect` reports the sign-change test and the number of halvings needed | COVERED |
| `e3` | Fixed point iteration after rearranging to x = g(x) | `numeric.t_fixed`, with `t_fixed_diag` and `t_cobweb` alongside | COVERED |
| `e4` | Newton-Raphson method | `numeric.t_newton` (shows f'(x), every iterate, an error bound and the next correction) | COVERED |
| `Mc34` | Approximate a definite integral by the trapezium rule | `numeric.t_integ` (trapezium, midpoint, Simpson) | COVERED |
| `v3` | Magnitude and direction of a vector | `vectors.t_mag` plus `polar.t_topolar_rt` | COVERED |
| `Mv7` | Vectors in three dimensions; unit vectors i, j, k | `vectors.py` is 3-D throughout | COVERED |
| `Mp1` | Structure of mathematical proof; deduction and exhaustion | Writing a proof. `proof.t_methods` prints the shape of each method, but the argument is the candidate's | N/A |
| `p3` | Proof by contradiction | Writing an argument (`t_methods` carries the root-2 and infinity-of-primes proofs as models) | N/A |
| `Ma1` | Vocabulary and notation (constant, coefficient, identity, ...) | Terminology only | N/A |
| `a6` | Significance of points of intersection in relation to solving equations | Conceptual link; the calculation itself is `Ma4`/`Ma5` | N/A |
| `f3` | Definition of a function; domain and range | Definitional (the computable part is handled by `purecalc.t_domain_range` by sampling) | N/A |
| `f8` | Use functions in modelling | Modelling judgement | N/A |
| `g7` | Use straight-line models | Modelling judgement | N/A |
| `g12` | Meaning of the terms parameter and parametric equations | Terminology only | N/A |
| `g16` | Use parametric equations in modelling | Modelling judgement | N/A |
| `Ms6` | What a sequence is; notation for terms | Terminology only | N/A |
| `s8` | A series is the sum of consecutive terms of a sequence | Definitional | N/A |
| `s17` | Use sequences and series in modelling | Modelling judgement | N/A |
| `t5` | tan(theta) = sin(theta)/cos(theta) | Identity to be quoted | N/A |
| `t6` | sin^2 + cos^2 = 1 | Identity to be quoted | N/A |
| `t20` | Construct proofs involving trigonometric functions | Proof writing | N/A |
| `t21` | Use trigonometric functions in context | Modelling judgement | N/A |
| `E3` | A logarithm is the inverse of the corresponding exponential | Definitional | N/A |
| `c25` | Integration as the limit of a sum | Conceptual foundation | N/A |
| `c31` | Formulate first order differential equations from a context | Modelling judgement | N/A |
| `c33` | Interpret the solution of a differential equation | Interpretation | N/A |
| `e2` | Circumstances under which change-of-sign methods fail | Conceptual; needs a discussion, not a calculation | N/A |
| `Me6` | Use numerical methods to solve problems in context | Modelling judgement | N/A |
| `Mv1` | Language of vectors in two dimensions | Terminology only | N/A |
| `v4` | Understand and use position vectors | Definitional; the arithmetic is `Mv1`-`v3` | N/A |

---

## H640 Statistics (assessed in component 02)

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `D4` | Describe frequency distributions (symmetric, unimodal, bimodal, skewed) | The histogram and box plot are drawn but nothing classifies the shape or reports a skew measure | MISSING |
| `D14` | Clean data: missing values, errors, outliers | No data-cleaning tool | MISSING |
| `u5` | Use Venn diagrams for up to three events | Not implemented; `t_prob` gives the probabilities but draws nothing | MISSING |
| `p24` | Use a variety of sampling techniques: simple random, systematic, stratified, quota, opportunity, cluster | `stat640.t_sampling` describes all six with the method, what each needs and where the bias comes from, and `t_stratsamp` performs proportional allocation by largest remainder and prints the systematic k = N/n; there is no random number source, so simple random and systematic samples cannot actually be drawn | PARTIAL |
| `*` (Probability) | Use tree diagrams and sample space diagrams | `stat640.t_tree` draws a labelled two-stage tree with all four end probabilities and the Bayes reversal; sample space (outcome grid) diagrams are not drawn | PARTIAL |
| `MD1` | Recognise categorical/discrete/continuous/ranked data; interpret bar charts, dot plots, histograms, vertical line charts, pie charts, stem-and-leaf, box plots, frequency charts | Box plots, histograms, cumulative frequency curves and scatter diagrams are drawn; bar charts, pie charts, dot plots, vertical line charts, stem-and-leaf and frequency charts are not | PARTIAL |
| `D7` | Recognise when a scatter diagram shows an outlier | `t_scatter` and `fmstat.t_pmcc` make a bivariate outlier visible; nothing identifies or flags one | PARTIAL |
| `p22` | Use samples to make informal inferences about the population | `t_summary` gives the statistics and `fmstat.t_tint` a confidence interval; the informal inference is written by the candidate | PARTIAL |
| `D11` | Simple measures of spread: range, percentiles, quartiles, IQR | `t_summary` gives range, Q1, Q3 and IQR; arbitrary percentiles are not offered | PARTIAL |
| `D13` | Understand the term outlier and identify outliers | `t_summary` and `t_boxplot` apply the 1.5*IQR fences and list the outliers; the "more than 2 standard deviations from the mean" rule is not implemented | PARTIAL |
| `*` (Probability) | Calculate the expected frequency of an event | `t_binom` prints np; there is no general n*P(event) tool | PARTIAL |
| `R5` | Calculate expected frequencies from a binomial distribution | Mean np is printed; a full table of expected frequencies is not produced | PARTIAL |
| `H9` | Identify the critical and acceptance regions for a test on a mean | `t_htmean` prints the critical z but not the critical value of the sample mean | PARTIAL |
| `H11` | Use a given correlation coefficient to carry out a hypothesis test for correlation | `fmstat.t_pmcc` takes alpha and the tail, looks up the critical r, states the rejection rule and the decision, and cross-checks with t = r sqrt((n-2)/(1-r^2)) and a p-value | COVERED |
| `*` (Probability) | Understand the concept of a complementary event | `t_tree` computes P(A'), P(B') and P(A'\|B) throughout and shows the four branch probabilities summing to 1 | COVERED |
| `D2` | Area of a histogram bar is proportional to frequency | `stat640.t_hist` computes the frequency density and draws area-correct bars | COVERED |
| `D3` | Interpret a cumulative frequency diagram | `stat640.t_cumfreq` plots at upper class boundaries and reads off the median and quartiles by linear interpolation | COVERED |
| `D6` | Interpret a scatter diagram and a regression line, including interpolation and extrapolation | `t_scatter` draws the points with the fitted line; `t_regress` predicts at a chosen x | COVERED |
| `D8` | Recognise and describe correlation | `t_scatter` gives the plot and r together | COVERED |
| `MD10` | Standard measures of central tendency: median, mode, mean | `stat640.t_summary` and `t_freq` | COVERED |
| `MD12` | Calculate and interpret variance and standard deviation; Sxx | `t_summary` gives Sxx, s (n-1) and sd (n) | COVERED |
| `Mu1` | Mutually exclusive events | `t_prob` addition rule | COVERED |
| `u2` | Add probabilities for mutually exclusive events | `t_prob` | COVERED |
| `u3` | Multiply probabilities for independent events | `t_prob`, and `t_tree` multiplies along branches | COVERED |
| `u4` | Mutually exclusive events (part 2) | `t_prob` | COVERED |
| `u6` | Calculate conditional probabilities P(A\|B) = P(A and B)/P(B) | `t_prob` and `t_tree` | COVERED |
| `u7` | P(B\|A) = P(B) if and only if A and B are independent | `t_prob` and `t_tree` both report an independence verdict | COVERED |
| `*` (Probability) | Calculate the probability of an event | `t_prob` | COVERED |
| `R3` | Calculate probabilities using the binomial distribution | `t_binom` (n <= 5000) | COVERED |
| `R4` | Understand and use mean = np | `t_binom` prints np and npq | COVERED |
| `R6` | Use probability functions given algebraically or in a table | `t_drv` | COVERED |
| `R7` | Calculate numerical probabilities for a discrete random variable | `t_drv` (with a sum-to-1 warning) | COVERED |
| `MR8` | Use the Normal distribution as a model | `t_normal` | COVERED |
| `R10` | Linear transformation of a Normal variable; standardising | `t_normal`, `fmstat.t_std` | COVERED |
| `R12` | Calculate and use probabilities from a Normal distribution | `t_normal`, `t_invnorm` | COVERED |
| `H2` | Understand when to apply 1-tail and 2-tail tests | Both `t_htbinom` and `t_htmean` ask for the tail and act on it | COVERED |
| `H5` | Conduct a hypothesis test at a given significance level | `t_htbinom`, `t_htmean` | COVERED |
| `H6` | Identify critical and acceptance regions | `t_htbinom` prints the critical region for all three tail choices | COVERED |
| `MH7` | Sample means from N(mu, sigma^2) are distributed N(mu, sigma^2/n) | `t_htmean` uses and prints SE = sigma/sqrt(n); `fmstat.t_nsum` spells out E(Xbar) and Var(Xbar) | COVERED |
| `H8` | Hypothesis test for a single mean | `t_htmean`, `fmstat.t_ztest` | COVERED |
| `MH10` | Correlation as a measure of how close points lie to a line; pmcc | `t_regress`, `fmstat.t_pmcc` | COVERED |
| `Mp21` | Understand and use the terms population and sample | Terminology only | N/A |
| `p23` | Concept of random sampling; simple random sampling | Conceptual; the mechanics are `p24` | N/A |
| `p25` | Select or evaluate sampling techniques and recognise sources of bias | Judgement in context (`t_sampling` supplies the bias notes to reason from) | N/A |
| `MD5` | Diagrams from unbiased samples approach theoretical distributions as n grows | Conceptual | N/A |
| `D9` | Select or critique data presentation techniques | Judgement | N/A |
| `MR1` | Recognise situations giving rise to a binomial distribution | Judgement | N/A |
| `R2` | Identify n and p for a binomial model | Judgement | N/A |
| `R9` | Shape of the Normal curve; area under it | Conceptual | N/A |
| `R11` | Line of symmetry of the Normal curve is x = mu | Conceptual | N/A |
| `R13` | Model with probability distributions; critique assumptions | Judgement | N/A |
| `MH1` | Understand the process of hypothesis testing; null and alternative hypotheses | Conceptual | N/A |
| `H3` | Understand that a sample is used to make an inference about a population | Conceptual | N/A |
| `H4` | Identify null and alternative hypotheses | Judgement | N/A |

---

## H640 Mechanics (assessed in component 01)

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `k4` | Draw and interpret kinematics graphs (position-time, velocity-time), including gradient and area | `mech640.distance_travelled` does the area-under-v-t job properly, splitting at the sign changes of v and separating distance from displacement; no s-t or v-t graph is drawn | PARTIAL |
| `k10` | Extend 1-D techniques (calculus and constant acceleration) to 2-D | The CAS is scalar; a position given as a vector function of t must be handled component by component | PARTIAL |
| `k12` | Use vectors to solve problems in kinematics | `fmmech.t_relative` covers relative position, relative velocity and closest approach in 2-D; a position vector given as a function of t still has to be differentiated one component at a time | PARTIAL |
| `F4` | Find the resultant of several concurrent forces | `mech640.resultant` takes exactly two (with direction); `equilibrium` sums up to 8 but reports only Sum Fx, Sum Fy and the resultant magnitude, not its direction | PARTIAL |
| `n7` | Formulate the equation of motion for a particle in two dimensions | `newton2` is scalar only | PARTIAL |
| `Mk9` | Language of 2-D kinematics; position vector, relative position | `fmmech.t_relative` gives r rel, v rel, the relative speed and direction, the time of closest approach and the least distance | COVERED |
| `k11` | Find the cartesian equation of the path of a particle | `fmmech.t_proj_path` eliminates t for a projectile and prints y = x tan a - g x^2/(2u^2cos^2a); `purecalc.t_param_cartesian` does the general elimination | COVERED |
| `y3` | Find the initial velocity (speed and angle) of a projectile from given information | `mech640.projectile_inverse` inverts from range+angle, height+angle, a position at a time, a target at a given speed (both trajectories) or range+time of flight | COVERED |
| `y4` | Eliminate time from the component equations to get the path equation | `fmmech.t_proj_path` shows the substitution t = x/(u cos a) and plots the resulting parabola | COVERED |
| `y5` | Solve simple problems involving projectiles, including maximum range | `fmmech.t_proj_incline` gives the best angle 2a - b = 90 and the maximum range u^2/(g(1+sin b)), and reduces to 45 degrees and u^2/g on level ground | COVERED |
| `F8` | Vectors representing a set of forces in equilibrium form a closed polygon | `fmmech.t_triangle_forces` draws the closed triangle head to tail and states that it closing is the resultant being zero | COVERED |
| `F9` | Formulate and solve equations for a particle in equilibrium (triangle of forces) | `t_triangle_forces` solves for the third force from two, or for the angles between three known magnitudes by the cosine rule, and refuses magnitudes that cannot close | COVERED |
| `n4` | Model a system as connected particles | `mech640.connected` (two masses over a smooth pulley, either hanging or on a plane at any angle, with friction on each) | COVERED |
| `n5` | Formulate the equations of motion for a connected system | `connected` prints the driving force, the maximum friction, the acceleration and the tension, and detects the stays-at-rest case | COVERED |
| `n6` | A system whose components all have the same acceleration | `connected` | COVERED |
| `k5` | Differentiate position and velocity with respect to time | `mech640.kinematics` | COVERED |
| `k6` | Integrate acceleration and velocity with respect to time | `mech640.kinematics` fixes each constant from the value at t = 0 | COVERED |
| `k7` | Recognise when constant acceleration applies; the suvat formulae | `mech640.suvat` | COVERED |
| `k8` | Solve kinematics problems with constant acceleration, including vertical motion under gravity | `suvat` + `casutil.askg` | COVERED |
| `My1` | Model motion under gravity in a vertical plane; projectile assumptions | `mech640.projectile` | COVERED |
| `y2` | Find the position and velocity of a projectile at any time | `projectile` | COVERED |
| `F2` | g is not a universal constant; g ~ 9.8 or 10 | `casutil.askg` prompts in every mechanics tool that needs it | COVERED |
| `F5` | Concept of equilibrium; the resultant of the forces is zero | `equilibrium` | COVERED |
| `MF6` | Resolve a force into components; select suitable directions | `resolve` | COVERED |
| `F7` | A particle is in equilibrium if and only if the resultant force is zero | `equilibrium` | COVERED |
| `F11` | Model friction by F <= mu R, with F = mu R when sliding | `friction_max`, `friction_horiz`, `friction_incline` | COVERED |
| `F12` | Apply Newton's laws to problems involving friction | `friction_horiz`, `friction_incline`, `connected` | COVERED |
| `n3` | Formulate the equation of motion for a particle | `newton2` | COVERED |
| `MF13` | Calculate the moment of a force about a point | `moments`; `fmmech.t_couple` for the couple case | COVERED |
| `F14` | A rigid body is in equilibrium when the resultant force and the resultant moment are both zero | `moments` reports both sums and can solve for an unknown reaction | COVERED |
| `Mp31` | Language of modelling assumptions: light, smooth, inextensible, particle, rigid | Terminology only | N/A |
| `p32` | Understand and use the particle model | Modelling judgement | N/A |
| `p33` | Fundamental quantities and units (m, s, kg) | Terminology only | N/A |
| `p34` | Derived quantities and units (m/s, m/s^2, N) | Terminology only | N/A |
| `p35` | Derived quantities and units (N m) | Terminology only | N/A |
| `Mk1` | Language of kinematics | Terminology only | N/A |
| `k2` | Difference between position, displacement and distance | Definitional (`distance_travelled` demonstrates it numerically) | N/A |
| `k3` | Difference between velocity and speed | Definitional | N/A |
| `MF1` | Language relating to forces (weight, tension, thrust, normal reaction) | Terminology only | N/A |
| `F3` | Identify the forces acting on a system; draw a force diagram | Diagram drawing / judgement | N/A |
| `F10` | The contact force resolves into a normal reaction and friction | Conceptual | N/A |
| `Mn1` | Newton's three laws of motion | Statement of law | N/A |
| `n2` | Understand the term equation of motion | Terminology only | N/A |
| `F15` | A system of forces can have a turning effect on a rigid body | Conceptual | N/A |
| `F16` | For moments, the weight of a uniform body acts at its centre of mass | Conceptual | N/A |

---

## H645 Core Pure (Y420) - mandatory paper, 50% of H645

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `c18` | Analyse and interpret coupled first order simultaneous differential equations (e.g. predator-prey) | Not implemented. Nothing eliminates one variable to produce the single second order equation the spec's own note describes | MISSING |
| `Pp4` | Construct a proof by induction for the nth term of a sequence, the sum of a series, or the nth power of a matrix | `proof.t_induction_sum` verifies the base case and then S(k+1) - S(k) = u(k+1) symbolically; `t_induction_matrix` checks the formula at n=1 and that M*F(k) = F(k+1) at five values of k, and both print the write-up to copy. The nth term of a sequence defined by a recurrence is not one of the three shapes offered, and the argument itself is still the candidate's | PARTIAL |
| `Pp5` | Construct a proof by induction generally (divisibility, de Moivre) | `proof.t_induction_divis` does the divisibility case in full, including choosing the multiplier m and showing what f(k+1) - m f(k) leaves; de Moivre by induction is not offered | PARTIAL |
| `*` (Proof) | Prove results by deduction and exhaustion; disprove by counter-example | The counter-example half is done by `proof.t_counterexample`; deduction and exhaustion are written arguments | PARTIAL |
| `a2` | Form a new equation whose roots are related to the original (2*alpha, alpha+k, 1/alpha, alpha^2) | `polyroots.t_shift_roots` covers only the +k substitution; scaling, reciprocal and squaring are not implemented | PARTIAL |
| `j3` | Complex roots occur in conjugate pairs; solve cubic and quartic equations with real coefficients | CAS `Factorise` peels off rational linear factors and `vcplx.t_quad` finishes the remaining quadratic, but nothing joins the two steps, and a cubic with no rational root still yields nothing complex | PARTIAL |
| `j8` | Multiply and divide complex numbers in modulus-argument form | `vcplx.t_arith` reports products and quotients in cartesian form only; nothing shows r1*r2 and theta1+theta2 | PARTIAL |
| `j10` | Represent sum, difference, product and quotient on an Argand diagram | `t_argand` plots points and `t_loci` draws loci; no parallelogram construction linking `t_arith` to a diagram | PARTIAL |
| `j19` | Represent the complex roots of unity on an Argand diagram | `t_roots` lists them and names the n-gon; plotting still needs each root retyped into `t_argand` | PARTIAL |
| `j20` | Apply complex numbers to geometrical problems (regular polygons) | Roots, moduli and loci are available; the geometry is assembled by hand | PARTIAL |
| `m2` | Understand and use the zero and identity matrices | No built-in I or 0; the user types them in | PARTIAL |
| `m4` | Find the matrix of a given 2-D transformation and vice versa; 3-D reflections in x=0/y=0/z=0 and rotations of multiples of 90 degrees about an axis | `matrix.t_transform` and `t_transform3` are both registered now and build every named 2-D and 3-D case; the matrix -> description direction is still not offered either way | PARTIAL |
| `m5` | Successive transformations and matrix multiplication | `A*B` works, but the composed matrix is not described as a transformation | PARTIAL |
| `m15` | Find the determinant and inverse of a 3x3 matrix without a calculator, possibly with algebraic terms | Numeric 3x3 only; algebraic entries are not supported | PARTIAL |
| `v2` | Form and use the vector and cartesian equation of a plane | Tools accept a plane as n.r = d; nothing forms the plane from three points or from a point and two directions | PARTIAL |
| `v4` | The different ways in which three distinct planes can intersect (point, line, sheaf, prism, parallel) | `matrix.t_solve` finds the unique point and reports "singular" otherwise, but never classifies the configuration | PARTIAL |
| `v11` | The different ways in which two lines can meet (intersect, parallel, skew) | `t_skew` detects parallel and gives the shortest distance; it does not confirm intersection or give the point | PARTIAL |
| `v12` | Determine whether two lines intersect | Inferable from `t_skew` distance = 0; the intersection point is never produced | PARTIAL |
| `s4` | A Maclaurin series may converge only for a restricted set of x | The reference card states the intervals of validity; nothing tests convergence | PARTIAL |
| `c6` | Recognise integrals giving arcsin and arctan forms | Tested: `1/(x^2+1)` -> `atan(x)` and `1/(x^2+4)` -> `atan(x/2)/2` work; `1/sqrt(1-x^2)` still returns `None` | PARTIAL |
| `a5` | Differentiate and integrate hyperbolic functions | Differentiation of sinh/cosh/tanh and the three inverses all present; `cascalc.integ` handles sinh and cosh but returns `None` for tanh (tested) | PARTIAL |
| `a8` | Recognise integrals of 1/sqrt(x^2+a^2) and 1/sqrt(x^2-a^2) giving arsinh and arcosh | `hyper.t_ref` prints these as a reference card; `cascalc.integ` returns `None` for both (tested) | PARTIAL |
| `p21` | Language of kinematics, including a = v dv/dx | The CAS can differentiate; the relation itself is not encoded | PARTIAL |
| `p22` | Use differential equations in modelling in kinematics | `diffeq.py` and `mech640.kinematics` supply the machinery; setting the equation up is manual | PARTIAL |
| `Pc15` | Solve the simple harmonic motion equation and relate the solution to the motion | `diffeq.t_shm` gives omega, T, f and both general forms, but does not fit A and phi (or C and D) from initial conditions, so the amplitude the spec's notation section asks for is never produced | PARTIAL |
| `j11` | Represent and interpret loci on an Argand diagram: \|z-a\| = r, \|z-a\| = \|z-b\|, arg(z-a) = theta, and regions | `vcplx.t_loci` does all four, prints the cartesian form of each, gives the greatest and least \|z\| on a circle, insists that arg(z-a) = theta is a HALF-line with a excluded, and draws every case (shading the disc for the region) | COVERED |
| `j13` | Apply de Moivre's theorem to trigonometric identities (cos n*theta, tan 4*theta) | `vcplx.t_demoivre_id` expands (cos t + i sin t)^n by the binomial theorem for n up to 8, separates real and imaginary parts into cos nt and sin nt as polynomials in c and s, and checks both numerically at t = 0.7 | COVERED |
| `Pm6` | Find invariant points and invariant lines of a linear transformation | `matrix.t_invariant` is now registered: invariant points from det(A-I), invariant lines from b m^2 + (a-d)m - c = 0, plus x = 0 when b = 0, and it spells out the difference between a line of invariant points and an invariant line | COVERED |
| `Pv14` | Find the intersection of a line and a plane | `vectors.t_lineplane` solves n.(a + td) = k, prints t and the point, checks n.p = k, and separates the two degenerate cases (line in the plane, line parallel to it with the distance) | COVERED |
| `v9` | Form and use the equation of a line in 2-D and 3-D, in vector and cartesian form | `vectors.t_lineeq` builds a line from two points or from a point and a direction, and prints the vector, parametric and cartesian forms, \|d\|, the unit direction and the point at any t | COVERED |
| `Pc1` | Evaluate improper integrals where a limit is infinite or the integrand is undefined at an endpoint | `purecalc.t_improper` handles all four cases, takes the limit on the antiderivative where there is one, otherwise integrates on a grid graded cubically towards the awkward end, and decides convergence from how the successive changes shrink rather than from their size | COVERED |
| `c2` | Derive formulae for and calculate volumes of revolution about the x- and y-axes | `purecalc.t_revolution` integrates y^2 dx or x^2 dy, exactly where `integ` can and numerically where it cannot; `fmmech.t_com_calculus` prints the same volume alongside the centre of mass | COVERED |
| `c8` | Recognise differential equations where the variables are separable | `purecalc.t_separable` checks that g is a function of y alone and says explicitly that if x and y will not separate the method does not apply and the integrating factor is the route | COVERED |
| `c14` | Find particular integrals in simple cases (polynomial, exponential, trigonometric f(x)) | `diffeq.t_particular` covers all three shapes, including the cases the spec singles out where the complementary function affects the trial: it raises the polynomial degree when b = 0, multiplies by x when p is a root (and by x^2 when it is repeated), and switches to x(P cos + Q sin) when wi is a root | COVERED |
| `c3` | Understand and evaluate the mean value of a function on [a, b] | `purecalc.t_meanvalue` gives the area, the width and the mean, and then solves f(x) = mean to say where the function actually attains it | COVERED |
| `c10` | Solve an equation using an integrating factor, including finding a particular solution | `diffeq.t_first_order` now carries the whole method through: int P dx, the IF with the modulus dropped and why, IF*Q, int IF*Q dx, y as a general solution, then C from a condition and a check at the given point | COVERED |
| `c13` | Solve y'' + a y' + b y = f(x) | `t_particular` prints the auxiliary roots, the complementary function, the particular integral and the general solution as CF + PI, and warns that the PI carries no arbitrary constant | COVERED |
| `m9` | The magnitude of a 3x3 determinant is the volume scale factor; the sign gives orientation | `matrix.t_transform3` prints \|det\| = volume scale factor and, when det < 0, that the orientation is reversed because a reflection is included | COVERED |
| `v15` | Calculate the angle between a line and a plane | `vectors.t_lineplane` prints the angle between d and n and then 90 minus it | COVERED |
| `Ps2` | Sum a series using partial fractions (method of differences) | `series.t_differences` splits f(r), builds g(r), verifies g(r)-g(r+1) = f(r) numerically, telescopes to g(1)-g(n+1) and cross-checks against a direct sum | COVERED |
| `Pj1` | Language of complex numbers | `vcplx.t_modarg` (prints the conjugate too) | COVERED |
| `j2` | Solve any quadratic equation with real coefficients | `vcplx.t_quad` | COVERED |
| `j4` | Add, subtract, multiply and divide complex numbers in x + yi form | `vcplx.t_arith` | COVERED |
| `j6` | Use radians in the context of complex numbers | `t_modarg` recognises exact multiples of pi | COVERED |
| `j7` | Represent a complex number in modulus-argument form and convert both ways | `t_modarg`, `t_topolar`, `t_frompolar` | COVERED |
| `j9` | Represent and interpret complex numbers on an Argand diagram | `vcplx.t_argand` (up to 8 points) | COVERED |
| `Pj12` | Understand and use de Moivre's theorem | `vcplx.t_power`, `t_demoivre_id`, `fpt.t_demoivre` | COVERED |
| `j14` | The definition e^(i theta) = cos theta + i sin theta; exponential form | `t_topolar` | COVERED |
| `j15` | Every non-zero complex number has n distinct nth roots | `vcplx.t_roots` | COVERED |
| `j16` | The distinct nth roots of r e^(i theta) | `t_roots`, `fpt.t_roots` | COVERED |
| `Pm1` | Add, subtract and multiply matrices up to 3x3 | `matrix.py` | COVERED |
| `m7` | Calculate the determinant of a 2x2 matrix (and 3x3 with a calculator) | `matrix.t_det` | COVERED |
| `m8` | The magnitude of a 2x2 determinant is the area scale factor | `t_transform` | COVERED |
| `m11` | Understand what is meant by an inverse matrix; singular matrices | `t_inv` | COVERED |
| `m12` | Calculate the inverse of a non-singular matrix | `t_inv` (closed form 2x2, adjugate 3x3) | COVERED |
| `m13` | Use the inverse of a matrix to solve a matrix equation | `t_solve` (Gauss-Jordan with partial pivoting) | COVERED |
| `Pv1` | Scalar product; test for perpendicularity; angle between vectors | `vectors.t_dot`, `t_angle`, `t_paraperp` | COVERED |
| `v3` | A vector perpendicular to two given vectors | `vectors.t_cross` | COVERED |
| `v5` | Solve three linear simultaneous equations using a matrix inverse | `matrix.t_solve` | COVERED |
| `v6` | The angle between two planes from their normals | `vectors.t_planeangle` | COVERED |
| `Pv7` | Use the vector product in solving problems | `vectors.t_cross` | COVERED |
| `v8` | The alternative form a x b = \|a\|\|b\| sin(theta) n-hat | `t_cross` and `t_unit` | COVERED |
| `v10` | Calculate the angle between two lines | `t_angle` on the direction vectors | COVERED |
| `v13` | Find the distance between two skew lines | `vectors.t_skew` | COVERED |
| `v16` | Find the distance from a point to a line | `vectors.t_ptline` (also the foot of the perpendicular) | COVERED |
| `v17` | Find the distance from a point to a plane | `vectors.t_ptplane` | COVERED |
| `Pa1` | Relationships between the roots and coefficients of quadratic, cubic and quartic equations | `polyroots.t_vieta_quad`, `t_vieta_cubic`, `t_vieta_quartic` | COVERED |
| `Ps1` | Standard formulae for Sum r, Sum r^2 and Sum r^3 | `series.t_sum_r`, `t_sum_r2`, `t_sum_r3` | COVERED |
| `s3` | Find the Maclaurin series of a function and use it for approximation | `series.t_maclaurin` and `t_approx` | COVERED |
| `s5` | Recognise and use the standard Maclaurin series and their intervals of validity | `series.t_reference` plus `t_maclaurin` | COVERED |
| `c4` | Use partial fractions in integration | `cascalc.integ_rational` | COVERED |
| `c5` | Differentiate inverse trigonometric functions | `caseng.diff` for asin, acos, atan | COVERED |
| `PP1` | Understand and use polar coordinates and convert to and from cartesian | `polar.t_topolar_xy`, `t_topolar_rt` | COVERED |
| `P2` | Sketch curves with simple polar equations | `polar.t_plot`, `t_preset` | COVERED |
| `P3` | Find the area enclosed by a polar curve | `polar.t_area` | COVERED |
| `Pa3` | Definitions of sinh, cosh, tanh and their graphs | `hyper.py`; `caslex` parses them so CAS `Graph` draws them | COVERED |
| `Pa6` | Definitions and domains of arsinh, arcosh, artanh | `hyper.t_arsinh`, `t_arcosh`, `t_artanh` | COVERED |
| `a7` | Derive and use the logarithmic forms of the inverse hyperbolic functions | Each inverse tool prints the logarithmic form | COVERED |
| `*` (Kinematics) | Newton's second law F = ma | `mech640.newton2` | COVERED |
| `c9` | Find an integrating factor and understand its use | `diffeq.t_first_order` | COVERED |
| `c11` | Solve a y'' + b y' + c y = 0 via the auxiliary equation | `diffeq.t_second_order` (all three discriminant cases) | COVERED |
| `c12` | Relationship between the discriminant of the auxiliary equation and the form of the solution | `t_second_order` prints the discriminant and branches on it | COVERED |
| `c16` | Model damped oscillations with second order differential equations | `diffeq.t_damping`, `t_second_order` | COVERED |
| `c17` | Interpret solutions as over-, under- or critically damped | `diffeq.t_damping` | COVERED |
| `*` (Proof) | Prove results by contradiction | Proof writing (`proof.t_methods` carries two worked models) | N/A |
| `j5` | A complex number is zero if and only if both parts are zero | Definitional | N/A |
| `j17` | Explain why the sum of all the nth roots of a complex number is zero | Explanation | N/A |
| `j18` | Multiplication by r e^(i theta) is a rotation and an enlargement | Geometric interpretation | N/A |
| `m3` | Matrix multiplication is associative but not commutative | Property to be quoted | N/A |
| `m10` | det(MN) = det M * det N | Property to be quoted | N/A |
| `m14` | (AB)^-1 = B^-1 A^-1 | Property to be quoted | N/A |
| `*` (Vectors) | Language of vectors in two and three dimensions | Terminology only | N/A |
| `*` (Series) | Difference between a sequence and a series | Definitional | N/A |
| `*` (Series) | The meaning of the word converge | Definitional | N/A |
| `*` (Calculus) | Definitions of the inverse trigonometric functions and their principal values | Definitional | N/A |
| `a4` | The identity cosh^2 x - sinh^2 x = 1 | Identity to be quoted (`hyper.t_ref` prints it) | N/A |
| `Pp19` | Introduce and define variables when setting up a model | Modelling judgement | N/A |
| `p20` | Relate first and second order derivatives to verbal descriptions of a situation | Interpretation | N/A |
| `Pc7` | Difference between a general and a particular solution | Definitional | N/A |

---

## H645 Mechanics Major (Y421) - major option

Toolkit modules in scope: `fmmech.py`, plus everything in `mech640.py`,
`diffeq.py`, `purecalc.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `v9` | Verify a general or particular solution of a differential equation of motion | No substitute-and-check tool anywhere. `caseng.subst` exists but is not exposed for this | MISSING |
| `Mq1` | Find the dimensions of a quantity in terms of M, L and T | `fmmech.t_units` names a quantity from its M L T powers against a table of 17, and `t_dim` checks a pair of triples; neither goes the other way, from a named quantity to its dimensions | PARTIAL |
| `q6` | Use dimensional analysis to determine unknown indices (e.g. period of a pendulum) | Requires solving simultaneous index equations; `matrix.t_solve` could be pressed into service by hand, but nothing does it | PARTIAL |
| `d7` | Find the resultant of several concurrent forces | `mech640.resultant` takes two with direction; `fmmech.t_triangle_forces` handles three; `equilibrium` sums up to 8 but gives magnitude only | PARTIAL |
| `w2` | Calculate the work done by a force, including a variable force (calculus) | `t_work` does W = F d only - no F cos(theta) d and no integral of F dx | PARTIAL |
| `w3` | Work done by a force in a given direction; scalar product | As `w2`; `vectors.t_dot` exists but is not wired to work | PARTIAL |
| `w6` | Conservation of mechanical energy | `t_elastic` option 2 does solve a full KE + GPE = EPE equation, but only for the elastic case; there is no general energy-equation solver | PARTIAL |
| `w7` | The work-energy principle | As `w6` | PARTIAL |
| `r4` | Model horizontal circular motion (conical pendulum, car on a bend) | Only the conical pendulum; banked tracks and friction-limited cornering are not built | PARTIAL |
| `r5` | Model circular motion with more than one force acting | As `r4` | PARTIAL |
| `r7` | Model motion in a vertical circle using conservation of energy | Only the minimum speed at the top, v = sqrt(gr) | PARTIAL |
| `r8` | Identify conditions under which a particle departs from circular motion | Implicit in the vertical-circle formula; no condition test | PARTIAL |
| `MG1` | Find the centre of mass of a system of particles in 1, 2 and 3 dimensions | `fmmech.t_com` does 1-D and 2-D only - no z coordinate | PARTIAL |
| `G9` | Use calculus to find the centre of mass of a uniform lamina or arc | `t_com_calculus` does the lamina under y = f(x) with x_bar and y_bar; a uniform arc (a wire along a curve) is not offered | PARTIAL |
| `G10` | Use the centre of mass in problems about the equilibrium of rigid bodies | `t_topple` covers the toppling and pushing cases; a body suspended from a point, hanging with its centre of mass below the pivot, is not | PARTIAL |
| `k2` | Extend kinematics techniques to 2-D using calculus and constant acceleration | Components are handled separately by hand; `t_relative` covers the constant-velocity case | PARTIAL |
| `v2` | Use acceleration, velocity and position to infer the force acting | `mech640.kinematics` differentiates and `newton2` multiplies by m; not joined up | PARTIAL |
| `v10` | Use boundary or initial conditions to determine constants | `diffeq.t_first_order` and `purecalc.t_separable` both apply an initial condition to a first order equation; the two constants of a second order or SHM solution are never fitted | PARTIAL |
| `v12` | Solve the SHM equation, including amplitude and period | `diffeq.t_shm` gives omega, T and f and both general forms; the amplitude is not computed from initial conditions | PARTIAL |
| `q2` | Understand that some quantities are dimensionless | `t_units` names the all-zero triple as dimensionless and says its value is the same in any consistent system | COVERED |
| `q3` | Determine the units of a quantity from its dimensions | `fmmech.t_units` turns M L T powers into kg/m/s units and names the quantity from a table of 17 | COVERED |
| `q4` | Change the units in which a quantity is measured | `t_units` option 2 takes the new unit sizes in kg, m and s and prints the conversion factor and the new value | COVERED |
| `d4` | Derive and use mu = tan(alpha) for a body on the point of slipping | `fmmech.t_topple` prints the slide angle arctan(mu) alongside the topple angle arctan(a/h) and says which happens first | COVERED |
| `d9` | A closed figure (triangle of forces) may be drawn to represent forces in equilibrium | `t_triangle_forces` draws the closed polygon and rejects magnitudes that cannot close | COVERED |
| `d10` | Formulate and solve equilibrium equations by resolving, or by a polygon of forces | `t_triangle_forces` solves for the third force from two (magnitude and direction), or for all three angles between three known magnitudes by the cosine rule, and names Lami's theorem | COVERED |
| `d13` | The meaning of the term couple | `fmmech.t_couple` gives G = F d, states the resultant is zero, and demonstrates that the moment is the same about any point the user names | COVERED |
| `d16` | Identify whether equilibrium is broken by sliding or by toppling | `t_topple` does both cases (tilting plane and horizontal push) and reports which threshold is reached first | COVERED |
| `Mi13` | Oblique impact and the modelling assumptions | `t_oblique_wall` and `t_oblique_spheres` both state the smoothness assumption and what follows from it before doing any arithmetic | COVERED |
| `i14` | Newton's Experimental Law for oblique impact (component along the line of centres) | `t_oblique_spheres` resolves along the line of centres, applies conservation and NEL there, and leaves the perpendicular components alone | COVERED |
| `i15` | Model oblique impact between a sphere and a surface | `t_oblique_wall` (speed and angle out, both to the surface and to the normal, plus tan(out) = tan(in)/e) | COVERED |
| `i16` | Model oblique impact between two spheres | `t_oblique_spheres` (both final speeds and directions) | COVERED |
| `i17` | Calculate the loss of kinetic energy in an oblique impact | Both oblique tools report it; the wall tool also gives the normal impulse m(1+e)u_n | COVERED |
| `i9` | Apply Newton's Experimental Law (e.g. between a particle and a wall) | `t_oblique_wall` is the wall case directly; a normal impact is the 90-degree case | COVERED |
| `r6` | Calculate tangential acceleration | `t_circular` option 5 gives a_r = omega^2 r, a_t = r alpha, the total and its angle to the radius | COVERED |
| `h3` | Calculate the stiffness or modulus of elasticity | `t_elastic` option 3 inverts mg = lambda x / l for lambda and prints k = lambda/l | COVERED |
| `h5` | Calculate the equilibrium position of a mass on an elastic string or spring | `t_elastic` option 1 (x = mgl/lambda, with T, total length and the EPE stored there) | COVERED |
| `h7` | Use energy principles with elastic strings/springs (e.g. maximum extension) | `t_elastic` option 2 solves 0.5mv^2 + mgx = lambda x^2/(2l) for x and notes that v = 0 gives twice the equilibrium extension | COVERED |
| `G3` | Know the positions of the centres of mass of standard uniform bodies | `t_com_standard` covers ten: rod, triangular lamina, circular arc, semicircular arc, circular sector, semicircular lamina, solid and hollow hemisphere, solid and hollow cone, each with the formula and the point it is measured from | COVERED |
| `G5` | Use the position of the centre of mass in problems about equilibrium and toppling | `t_topple` takes the height of the centre of mass and returns the critical angle, and will test a given plane angle | COVERED |
| `MG6` | Calculate the volume generated by rotating a region about the x- or y-axis | `t_com_calculus` prints V = pi int r^2; `purecalc.t_revolution` does the same about either axis | COVERED |
| `G7` | Use calculus to find the centre of mass of a uniform solid of revolution | `t_com_calculus` options 2 and 3 (about Ox and about Oy) | COVERED |
| `Mk1` | Language of 2-D kinematics; position vector, relative position | `t_relative` gives r rel, v rel, relative speed and direction, closest approach and the distance at any t | COVERED |
| `Mv3` | Eliminate a parameter from parametric equations | `t_proj_path` for the projectile; `purecalc.t_param_cartesian` in general | COVERED |
| `v4` | Interpret the resulting cartesian equation (e.g. a bounding parabola) | `t_proj_path` prints the bounding parabola y = u^2/(2g) - g x^2/(2u^2) alongside the path | COVERED |
| `v5` | Derive the cartesian equation of the path of a projectile | `t_proj_path` shows the substitution and plots the parabola | COVERED |
| `v6` | Find the range of a projectile up or down an inclined plane | `t_proj_incline` (range along the plane, horizontal range, rise, time of flight; b < 0 fires down the slope) | COVERED |
| `v7` | Find the maximum range of a projectile | `t_proj_incline` gives 2a - b = 90 and R_max = u^2/(g(1+sin b)) | COVERED |
| `q5` | Use dimensional analysis to check the consistency of a formula | `fmmech.t_dim` | COVERED |
| `d3` | Model friction by F <= mu R with F = mu R when sliding | `mech640.friction_max`, `friction_horiz`, `friction_incline` | COVERED |
| `d5` | Apply Newton's laws to situations involving friction | `friction_horiz`, `friction_incline`, `connected` | COVERED |
| `d6` | Resolve a force into components and select suitable directions | `mech640.resolve` | COVERED |
| `Md8` | A particle is in equilibrium if and only if the resultant of the concurrent forces is zero | `mech640.equilibrium` | COVERED |
| `d14` | Calculate moments about a fixed axis | `mech640.moments` | COVERED |
| `d15` | Conditions for the equilibrium of a rigid body | `moments` | COVERED |
| `w4` | Calculate kinetic energy | `fmmech.t_work` option 1 | COVERED |
| `w5` | Calculate gravitational potential energy | `t_work` option 2 | COVERED |
| `w8` | Power as force times the component of velocity | `t_work` options 4 and 5 | COVERED |
| `Mi1` | Calculate the impulse of a force | `fmmech.t_momentum` option 2 | COVERED |
| `i2` | Understand and use linear momentum | `t_momentum` | COVERED |
| `i3` | The impulse-momentum equation | `t_momentum` | COVERED |
| `i4` | Internal impulses cancel, so momentum is conserved | `t_momentum` option 1 | COVERED |
| `Mi6` | Apply conservation of linear momentum to direct impact | `t_momentum` option 1 | COVERED |
| `i7` | Newton's Experimental Law and the coefficient of restitution | `fmmech.t_restitution` | COVERED |
| `i8` | The significance of e = 0 (the bodies coalesce) | `t_restitution` with e = 0 | COVERED |
| `i10` | Model situations involving direct impact | `t_restitution` | COVERED |
| `i11` | The significance of e = 1 (perfectly elastic) | `t_restitution` with e = 1 reports zero KE loss | COVERED |
| `i12` | When e < 1 kinetic energy is not conserved | `t_restitution` prints the KE lost | COVERED |
| `r3` | Calculate the acceleration towards the centre, v^2/r and omega^2 r | `fmmech.t_circular` options 1 and 2 | COVERED |
| `h2` | Hooke's law models the tension in an elastic string or spring | `fmmech.t_hooke` | COVERED |
| `h4` | Calculate the tension in an elastic string or spring | `t_hooke` | COVERED |
| `h6` | Calculate the energy stored in a stretched string or spring | `t_hooke` and `t_elastic` | COVERED |
| `G4` | Find the centre of mass of a composite body | `fmmech.t_com` (negative masses model removed pieces) | COVERED |
| `G8` | Find the centre of mass of a compound body by treating parts as particles | `t_com` with `t_com_standard` for each part's own centre | COVERED |
| `Mv1` | Find acceleration, velocity and position by calculus (variable acceleration) | `mech640.kinematics` | COVERED |
| `v11` | Recognise and formulate the simple harmonic motion equation | `diffeq.t_shm`, `t_damping` | COVERED |
| `q7` | Use a model based on dimensional analysis | Modelling judgement | N/A |
| `*` (Forces) | Language relating to forces | Terminology only | N/A |
| `Md1` | Bodies in contact may be subject to friction as well as a normal contact force | Conceptual; force diagram | N/A |
| `d2` | The total contact force resolves into friction and a normal reaction | Conceptual | N/A |
| `d11` | Draw a force diagram for a rigid body | Diagram drawing | N/A |
| `d12` | A system of forces can have a turning effect on a rigid body | Conceptual | N/A |
| `Mw1` | Language of work, energy and power | Terminology only | N/A |
| `i5` | The term direct impact and its modelling assumptions | Terminology only | N/A |
| `Mr1` | Language of circular motion (tangential, radial, angular speed) | Terminology only | N/A |
| `r2` | Identify the forces acting on a body in circular motion | Force diagram / judgement | N/A |
| `Mh1` | Language of elasticity (modulus, stiffness, natural length) | Terminology only | N/A |
| `h8` | Understand when Hooke's law does not apply | Conceptual | N/A |
| `G2` | Locate a centre of mass by appeal to symmetry | Geometric reasoning | N/A |
| `Mv8` | Formulate differential equations of motion | Modelling judgement | N/A |

---

## H645 Mechanics Minor (Y431) - minor option

The Minor paper's content is a strict subset of Mechanics Major: `Mq1`-`q7`,
`Md1`-`d16`, `Mw1`-`w8`, `Mi1`-`i12` and `MG1`-`G5` (49 statements including
the one `*` item). Every verdict is identical to the Y421 row for the same
code. Nothing in this paper is now MISSING. Summarised:

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `Mq1`, `q6` | Dimensions of a named quantity; unknown indices | As Y421 | PARTIAL |
| `d7` | Resultant of several concurrent forces | As Y421 | PARTIAL |
| `w2`, `w3` | Work at an angle, and by a variable force | As Y421 | PARTIAL |
| `w6`, `w7` | Conservation of energy; the work-energy principle | As Y421 | PARTIAL |
| `MG1` | Centre of mass in 3-D | As Y421 (1-D and 2-D only) | PARTIAL |
| `q2`, `q3`, `q4`, `q5` | Dimensionless quantities; units from dimensions; changing units; consistency | `fmmech.t_units`, `t_dim` | COVERED |
| `d3`, `d5`, `d6`, `Md8`, `d14`, `d15` | Friction, Newton's laws with friction, resolving, equilibrium, moments | `mech640.py` | COVERED |
| `d4` | mu = tan(alpha) on the point of slipping | `fmmech.t_topple` | COVERED |
| `d9`, `d10` | Closed figure of forces; solving equilibrium by polygon | `fmmech.t_triangle_forces` | COVERED |
| `d13` | Couples | `fmmech.t_couple` | COVERED |
| `d16` | Sliding versus toppling | `fmmech.t_topple` | COVERED |
| `w4`, `w5`, `w8` | KE, GPE, power | `fmmech.t_work` | COVERED |
| `Mi1`-`i4`, `Mi6`-`i12` | Impulse, momentum, restitution, KE loss, the wall case | `fmmech.t_momentum`, `t_restitution`, `t_oblique_wall` | COVERED |
| `G3` | Centres of mass of standard bodies | `fmmech.t_com_standard` | COVERED |
| `G4` | Composite centre of mass | `fmmech.t_com` | COVERED |
| `G5` | Centre of mass in equilibrium and toppling problems | `fmmech.t_topple` | COVERED |
| `q7`, `*`, `Md1`, `d2`, `d11`, `d12`, `Mw1`, `i5` | Terminology, diagrams and modelling judgement | - | N/A |
| `G2` | Symmetry arguments | - | N/A |

---

## H645 Statistics Major (Y422) - major option

Toolkit modules in scope: `fmstat.py`, plus `stat640.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `SH5` | Carry out a hypothesis test for an average using the Wilcoxon signed rank test | Not implemented, and deliberately so. The test is decided against a printed table of critical values of W that the toolkit has no way to derive or check; the exact distribution of the signed-rank statistic is not computed anywhere. Every other test here is either computed from a distribution the toolkit implements or read from a table small enough to be transcribed and asserted in the test suite | MISSING |
| `Z2` | Use simulations to investigate distributions | No random number generator anywhere in the toolkit | MISSING |
| `R25` | Obtain a pdf from a given cdf by differentiation | CAS `Differentiate` will do it if F(x) is retyped as f(x); the continuous-rv tools all take a pdf as input and none accepts a cdf | PARTIAL |
| `R32` | Use the Normal distribution when the parameters have to be estimated from a sample | `stat640.t_summary` estimates mu and s, `t_normplot` reports the slope and intercept as estimates of sigma and mu, and `t_tint` uses t rather than z when sigma is estimated; nothing joins estimation to `t_norm` in one step | PARTIAL |
| `SR1` | Use probability functions given algebraically or in a table | `fmstat.t_drv` | COVERED |
| `R2` | Calculate the expectation (mean) of a discrete random variable | `t_drv` | COVERED |
| `R3` | Calculate the variance using Var(X) = E(X^2) - mu^2 | `t_drv` | COVERED |
| `R4` | Use E(a + bX) = a + bE(X) | `t_lincomb` with b = 0 gives E(aX + c) = aE(X) + c and states the rule | COVERED |
| `R5` | Use Var(a + bX) = b^2 Var(X) | `t_lincomb` prints Var(W) = a^2Var(X) + b^2Var(Y) and warns that Var(X-Y) adds the variances | COVERED |
| `SR6` | Find the expectation of a linear combination of random variables, E(X +- Y) | `t_lincomb` prints E(X+Y), E(X-Y), Var(X+Y) and Var(X-Y) explicitly | COVERED |
| `R7` | Recognise the discrete uniform distribution | `fmstat.t_dunif` | COVERED |
| `R8` | Calculate probabilities from a discrete uniform distribution | `t_dunif` (P = 1/n over a..b) | COVERED |
| `R9` | Mean and variance of a discrete uniform distribution | `t_dunif` gives (a+b)/2 and (n^2-1)/12 as closed forms | COVERED |
| `R12` | Recognise when the Poisson approximates the binomial | `t_bin` checks n >= 50 and p <= 0.1 and, when they hold, prints the Poisson values with mu = np alongside the exact binomial ones | COVERED |
| `R13` | Calculate probabilities using a Poisson distribution | `fmstat.t_pois` | COVERED |
| `R14` | Know and use the mean and variance of a Poisson distribution | `t_pois` prints both as lambda and says they are equal | COVERED |
| `R17` | Calculate probabilities within a geometric distribution | `fmstat.t_geom` gives P(X=r), P(X<=r) and P(X>r) with the formulae | COVERED |
| `R18` | Mean and variance of a geometric distribution | `t_geom` prints 1/p and (1-p)/p^2 | COVERED |
| `SR19` | Use a simple continuous random variable as a model | `fmstat.t_pdf` takes f(x) on [a, b], integrates exactly where `cascalc.integ` can and by Simpson where it cannot, and draws the density | COVERED |
| `R20` | The meaning of a probability density function, including piecewise pdfs | `t_pdf` and `t_pdfpw`, which takes 2 to 4 pieces and refuses ones that do not join up | COVERED |
| `R21` | Properties of a pdf (non-negative, integrates to 1) | `_validity` checks both, reports int f dx and whether it was exact, and names the x where f goes negative | COVERED |
| `SR22` | Find the mean and variance of a continuous random variable | `_moments_lines` gives E(X), E(X^2), Var(X) and SD from the integrals | COVERED |
| `R23` | Find the mode and median of a continuous random variable | `t_pdfmode` scans then ternary-searches, and says whether the mode is interior or at an endpoint (the case where f'(x) = 0 would miss it); the median comes from `t_cdf` | COVERED |
| `R24` | The meaning of a cumulative distribution function | `t_cdf` prints F(x) shifted so F(a) = 0 and plots the curve | COVERED |
| `R26` | Use a cdf to calculate the median and quartiles | `t_cdf` solves F(x) = p for Q1, the median and Q3, gives the IQR, and marks the median on the plot | COVERED |
| `R27` | Find the mean of a linear combination of random variables | `t_lincomb` | COVERED |
| `R29` | Use linear combinations of independent Normal random variables | `t_lincomb` computes E(W) and Var(W) and then P(W < w) on the Normal assumption, stating that the mean and variance hold for any independent X and Y but the Normality does not | COVERED |
| `R31` | Interpret a Normal probability plot | `t_normplot` plots the ordered data against z_i = invphi((i-0.5)/n), fits the line, reports r, and reads the slope and intercept as sigma and mu | COVERED |
| `SR28` | Use the Normal distribution as a model and calculate probabilities | `fmstat.t_norm`, `t_std`, `t_inv` | COVERED |
| `b2` | Use and interpret a scatter diagram, including looking for outliers by eye | `fmstat.t_pmcc` draws the scatter with the fitted line every time it computes r | COVERED |
| `b4` | Calculate the pmcc from raw data | `t_pmcc` (also Sxy, Sxx, Syy and r^2) | COVERED |
| `Sb6` | Carry out a hypothesis test for correlation using the pmcc | `t_pmcc` takes alpha and the tail, looks up the critical r, states the rejection rule and the decision, and confirms with the t statistic and a p-value that works past the end of the table | COVERED |
| `Sb8` | Calculate Spearman's rank correlation coefficient | `fmstat.t_spear` (pmcc of ranks, ties averaged) | COVERED |
| `b9` | Carry out a hypothesis test using Spearman's rank correlation coefficient | `t_spear` uses the exact rs table with the same alpha/tail interface, and warns that ties make the table approximate | COVERED |
| `Sb11` | Calculate the equation of the least squares regression line | `fmstat.t_reg`, `stat640.t_regress` | COVERED |
| `b12` | Use the regression line as a model; residuals | `t_reg` lists the residuals y - (a + bx) and the residual sum of squares | COVERED |
| `b13` | Calculate the equations of both regression lines (y on x and x on y) | `t_reg` prints both, with the means point they share | COVERED |
| `b14` | Check how well the model fits the data (visual inspection, pmcc^2) | `t_reg` gives r and r^2 and the residuals; `t_pmcc` gives the plot | COVERED |
| `b15` | The relationship between the two regression lines and which to use | `t_reg` prints both lines, notes they coincide only when r^2 = 1, and states that y on x predicts y and x on y predicts x | COVERED |
| `Sb16` | Interpret bivariate categorical data | `fmstat.t_assoc` takes the contingency table and prints every observed and expected cell | COVERED |
| `SH1` | Apply the chi-squared test for association in a contingency table | `t_assoc` computes E = row total * column total / grand total, uses df = (r-1)(c-1), warns about cells with E < 5, and states whether there is evidence of association | COVERED |
| `H2` | Interpret the results of a chi-squared test | `_chi_verdict` gives the critical value at any alpha and a p-value from `_chi2_sf`, shared by both chi-squared tools so they cannot disagree | COVERED |
| `H3` | Carry out a chi-squared goodness-of-fit test | `t_chi` asks how many parameters were estimated and uses df = cells - 1 - params, refusing the test when that leaves df < 1 | COVERED |
| `H4` | Interpret the results of a chi-squared goodness-of-fit test | As `H2`, plus the pool-the-classes warning | COVERED |
| `SI1` | Estimate a population mean from a sample | `stat640.t_summary`, `fmstat.t_tint` | COVERED |
| `I2` | Estimate a population variance using the divisor n - 1 | `t_summary` and `t_tint` both use and print s (n-1) | COVERED |
| `I4` | Calculate and interpret the standard error of the mean | `t_cimean`, `t_tint` and `t_ztest` all print SE | COVERED |
| `I9` | Construct and interpret a confidence interval for a population mean | `t_cimean` for a known sigma; `t_tint` for an estimated one, with the correct t* on n-1 degrees of freedom | COVERED |
| `I11` | Construct and interpret a confidence interval for a mean difference from paired data | `t_tint` on the list of differences, which is exactly the paired procedure, and its prompt says so | COVERED |
| `I13` | Use a confidence interval to test a hypothesis about a population mean | `t_tint` takes mu0, says whether it falls inside the interval, and gives the matching t statistic and two-tail p-value | COVERED |
| `H6` | Carry out a hypothesis test for a population mean using the Normal distribution | `fmstat.t_ztest` | COVERED |
| `Sx1` | Explain the importance of sample size | Explanation | N/A |
| `x2` | Explain why sampling may be necessary | Explanation | N/A |
| `x3` | Explain the advantage of a random sample | Explanation | N/A |
| `R10` | Recognise situations where the binomial distribution is appropriate | Modelling judgement | N/A |
| `SR11` | Recognise situations where the Poisson distribution is appropriate | Modelling judgement | N/A |
| `R15` | The sum of independent Poisson variables is Poisson | Property to be quoted | N/A |
| `SR16` | Recognise situations where the geometric distribution is appropriate | Modelling judgement | N/A |
| `Sb1` | Understand what bivariate data are; independent and dependent variables | Terminology only | N/A |
| `b3` | Interpret a scatter diagram produced by software | Interpretation of given output | N/A |
| `b5` | Know when it is appropriate to calculate the pmcc | Judgement | N/A |
| `b7` | Use the pmcc as an effect size | Judgement (r^2 is printed to reason from) | N/A |
| `b10` | Decide whether a test based on r or on rs is more appropriate | Judgement | N/A |
| `R30` | The Normal distribution as a useful model; when it is appropriate | Modelling judgement | N/A |
| `I3` | The sample mean is a random variable with a sampling distribution | Conceptual | N/A |
| `I5` | The sampling distribution of the mean when the parent is Normal | Conceptual | N/A |
| `I6` | How and when the Central Limit Theorem applies | Conceptual | N/A |
| `SI7` | The meaning of the term confidence interval | Definitional | N/A |
| `I8` | Factors affecting the width of a confidence interval | Conceptual | N/A |
| `I10` | Know when samples from two populations should be paired | Judgement | N/A |
| `SI12` | Interpret confidence intervals given by software | Interpretation of given output | N/A |
| `SZ1` | Know that spreadsheets can be used for statistical work | Spreadsheet skill, assessed on a computer | N/A |

---

## H645 Statistics Minor (Y432) - minor option

The Minor paper's content is a strict subset of Statistics Major: `Sx1`-`x3`,
`SR1`-`R18`, `Sb1`-`b16` and `SH1`-`H4` (41 statements). Verdicts are identical
to the Y422 rows for the same codes. Nothing in this paper is MISSING or
PARTIAL: the Wilcoxon test and simulation, the two Y422 gaps, are both outside
the Minor content, and so are the two Y422 PARTIALs.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `SR1`, `R2`, `R3` | Probability functions; expectation; variance | `fmstat.t_drv` | COVERED |
| `R4`, `R5`, `SR6` | E(a+bX), Var(a+bX), E(X +- Y) | `fmstat.t_lincomb` | COVERED |
| `R7`, `R8`, `R9` | Discrete uniform distribution | `fmstat.t_dunif` | COVERED |
| `R12`, `R13`, `R14` | Poisson probabilities, mean and variance; Poisson approximation to binomial | `fmstat.t_pois`, `t_bin` | COVERED |
| `R17`, `R18` | Geometric distribution | `fmstat.t_geom` | COVERED |
| `b2`, `b4` | Scatter diagram; pmcc from raw data | `fmstat.t_pmcc` | COVERED |
| `Sb6`, `b9` | Hypothesis tests for correlation, r and rs | `t_pmcc`, `t_spear` | COVERED |
| `Sb8` | Spearman's rank correlation coefficient | `fmstat.t_spear` | COVERED |
| `Sb11`, `b12`, `b13`, `b14`, `b15` | Least squares line, residuals, both lines, model fit | `fmstat.t_reg` | COVERED |
| `Sb16`, `SH1` | Contingency tables and the chi-squared test for association | `fmstat.t_assoc` | COVERED |
| `H2`, `H3`, `H4` | Chi-squared goodness of fit and interpretation | `fmstat.t_chi` | COVERED |
| `Sx1`, `x2`, `x3` | Sampling explanations | - | N/A |
| `R10`, `SR11`, `R15`, `SR16` | Recognising distributions; sum of Poissons | - | N/A |
| `Sb1`, `b3`, `b5`, `b7`, `b10` | Bivariate terminology and judgement | - | N/A |

---

## H645 Modelling with Algorithms (Y433) - minor option

Toolkit module in scope: `algos.py`.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `L5` | Recognise when an LP requires an integer solution | Nothing recognises it. `lpgraph` will find the best lattice point once you have decided the variables are discrete, but deciding that from the context is the statement | MISSING |
| `L6` | Formulate a range of network problems as LPs | The network tools and the LP tools exist side by side; nothing turns a network into a set of constraints | MISSING |
| `L11` | Use a visualisation of a 3-D LP | `lpgraph` is 2-D only; the screen is 384x192 and there is no 3-D projection anywhere in the toolkit | MISSING |
| `L16` | Handle variables which may be negative | Every LP tool assumes x, y, z, w >= 0; there is no x = u - v substitution | MISSING |
| `N13` | Explore network algorithms via LP formulations | Nothing links the two halves of the module | MISSING |
| `N8` | Model precedence problems with an activity-on-arc network | `critpath` takes activities with predecessor lists, which is activity-on-node; it does not build or read an activity-on-arc diagram and there are no dummy activities | PARTIAL |
| `N9` | Use critical path analysis and interpret outcomes; analyse float (total, independent and interfering), resourcing and scheduling | `critpath` gives the project duration, ES, EF, total float and the critical activities; independent and interfering float, cascade charts, resource histograms and scheduling are not produced | PARTIAL |
| `L9` | Consider the effect of modifying an LP (post-optimal analysis) | `simplex` prints the shadow price of every constraint, which answers the change-the-right-hand-side question; changing an objective coefficient or adding a constraint means re-entering the problem | PARTIAL |
| `L13` | Understand the geometric basis of the simplex algorithm | `_lpreport` names the basic and non-basic variables at the optimum, and `lpgraph` lists the vertices, but nothing states that a tableau is a vertex or walks the two side by side | PARTIAL |
| `L15` | Reformulate an equality constraint as a pair of inequalities | `simplex2` accepts an equality directly (rel = 0) and handles it with an artificial variable, which is the practical route; it does not demonstrate the replacement of x = 4 by x <= 4 and x >= 4 | PARTIAL |
| `A4` | Basic ideas of algorithmic complexity; worst case; size of problem | Every sort prints its order and the worst-case comparison count n(n-1)/2 for the n it was given; `dijkstra` and `prim` print O(n^2) and `kruskal` O(m log m) | COVERED |
| `A7` | Know and be able to use the quick sort algorithm | `algos.quicksort` splits every unsorted sub-list about its own first element at each pass, shows fixed pivots in brackets, and uses an explicit stack rather than recursion so the 38-frame ceiling cannot be reached | COVERED |
| `A8` | Count the comparisons and/or swaps used by a sorting algorithm | `bubble` counts both comparisons and swaps, `insertion` counts comparisons and shifts, `quicksort` counts comparisons and passes | COVERED |
| `A10` | Know and use the first fit and first fit decreasing bin-packing algorithms | `algos.firstfit`, `firstfitdec` with full bin contents | COVERED |
| `A11` | Count the comparisons needed by first fit and first fit decreasing | `_firstfit` counts every does-this-item-fit test and both tools report it, alongside the lower bound on the number of bins | COVERED |
| `AN1` | Graphs and associated vocabulary; adjacency and incidence matrices | `algos.graphinfo` takes an adjacency matrix and reports order, size, degrees (loops counted twice), the sum-of-degrees identity, the number of odd nodes, connectivity, and prints the incidence matrix | COVERED |
| `N3` | A network is a graph with weighted arcs; directed and undirected | `graphinfo` detects symmetry and reports directed or undirected, giving in- and out-degrees for the directed case | COVERED |
| `N5` | Solve minimum connector problems using Kruskal's algorithm | `algos.kruskal` (union-find) and `algos.prim`, both listing edges in order with the total weight | COVERED |
| `N6` | Model shortest path problems and solve using Dijkstra's algorithm | `algos.dijkstra` now prints the order in which nodes became permanent, the working values tried at each node, the final distances and, on request, the route itself | COVERED |
| `N7` | Know the order (complexity) of Kruskal's, Prim's and Dijkstra's algorithms | Each of the three prints its own order | COVERED |
| `N10` | Use a network to model a transmission problem; sources and sinks | `algos.maxflow` takes a capacity matrix with a chosen source and sink | COVERED |
| `N11` | Specify a cut and calculate its capacity | `algos.cutcap` takes the source-side node set, rejects sets that put the source or sink on the wrong side, counts only the S-to-T arcs (and says what the back arcs total), and reports whether the cut is minimum | COVERED |
| `N12` | Understand and use the maximum flow / minimum cut theorem; flow augmentation | `maxflow` lists each augmenting path and its flow, prints the flow on every arc with the saturated ones marked, finds the minimum cut from the residual reachability, and states max flow = min cut | COVERED |
| `L3` | Recognise when an LP is in standard form | `simplex` prints the standard form back and refuses a problem with a negative right-hand side, naming which constraint and pointing at the two-stage tool | COVERED |
| `L4` | Use slack variables to convert an LP to slack form | `simplex` prints the slack form and the objective row P - c.x = 0 | COVERED |
| `L7` | Graph inequalities in 2-D and identify the feasible region | `algos.lpgraph` shades the feasible region on a dot grid, draws every constraint line, marks the vertices, and reports an empty region | COVERED |
| `L8` | Solve a 2-D LP graphically | `lpgraph` lists every vertex with its objective value, detects an unbounded region and an unbounded objective separately, and marks the optimal vertex on the plot | COVERED |
| `L10` | Solve 2-D integer LP problems | `lpgraph` searches the lattice in the vertex bounding box (up to 4000 points) and reports the best integer point, or that there is none | COVERED |
| `L12` | Use the simplex algorithm on an LP in standard form | `simplex` shows the initial tableau, then for each pivot the entering column, the leaving row, the ratio and the pivot element, and the tableau after it | COVERED |
| `L14` | Handle >= constraints (two-stage simplex / big-M) | `simplex2` runs phase 1 to drive the artificials to zero, detects infeasibility, pivots any artificial that is still basic out, then runs phase 2, and handles minimisation by negating the objective | COVERED |
| `AA1` | An algorithm is a finite sequence of operations; initial state, input, output | Definitional | N/A |
| `A2` | Interpret and apply algorithms presented in flowcharts or pseudocode | Reading a given algorithm | N/A |
| `A3` | Repair, develop and adapt given algorithms | Writing an algorithm | N/A |
| `A5` | Algorithms can sometimes be proved correct | Proof | N/A |
| `A6` | Understand and know the importance of heuristics | Conceptual | N/A |
| `A9` | Reason about a given sorting algorithm | Explanation | N/A |
| `N2` | Model problems by using graphs | Modelling judgement | N/A |
| `N4` | Model problems by using networks | Modelling judgement | N/A |
| `AL1` | Language associated with linear programming | Terminology only | N/A |
| `L2` | Identify and define variables from a problem description | Modelling judgement | N/A |
| `L17` | Some LPs can be solved by other means | Conceptual | N/A |
| `L18` | Interpret the output from linear programming software | Interpretation of given output | N/A |

---

## H645 Numerical Methods (Y434) - minor option

Toolkit module in scope: `numeric.py`.

Note: this paper is assessed with the expectation that learners use a
**spreadsheet**. Statements `NQ1` and `Q2` are explicitly about spreadsheet use
and are marked N/A on that basis, not because they are uncomputable.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `U3` | Understand the effect on errors of changing the way a calculation is arranged | `t_err_prop` detects the one case that matters most - a - b subtracting nearly equal numbers - and says to rearrange; it does not take two arrangements of the same expression and compare their error | PARTIAL |
| `e3` | Understand the relative computational efficiency of different root-finding methods | `t_conv_order` reports the order of any sequence of iterates and `t_fixed_diag` names fixed-point iteration as first order, so the comparison can be made by running each method; nothing runs them side by side or counts the work | PARTIAL |
| `NU1` | Calculate errors in sums, differences, products and quotients | `t_err_prop` gives the absolute and relative error of a+b, a-b, a*b and a/b from the errors in a and b, and states the two rules | COVERED |
| `U2` | Calculate the error in f(x) when x is in error | `t_err_fx` gives \|f'(x)\|dx as the estimate and then f(x-dx) and f(x+dx) as the actual range, so the linear estimate can be checked against the truth | COVERED |
| `U6` | Understand rounding and chopping and their effects; maximum and average error | `t_chop` prints both results, both errors, and the maximum and mean error of each (u and u/2 chopping, u/2 and u/4 rounding), and notes that chopping biases a long sum | COVERED |
| `NU7` | Understand convergence and divergence, and the order of convergence, of an iterative sequence | `t_conv_order` tabulates the differences and their ratios, flags divergence when \|r\| >= 1, and estimates p from ln\|d(n+1)/d(n)\| / ln\|d(n)/d(n-1)\| | COVERED |
| `U8` | Use error analysis to produce an improved estimate | `t_richardson` builds the full extrapolation table for any order p; `t_aitken` accelerates a sequence by delta-squared; both integration and differentiation error tables extrapolate as well | COVERED |
| `Ne1` | Graphical interpretation of iterative methods, including staircase and cobweb diagrams | `t_cobweb` draws y = x, y = g(x) and the path, then names it a staircase or a cobweb from the sign of g' and says whether it converges from \|g'\| | COVERED |
| `e2` | Solve equations to any required accuracy and justify the accuracy claimed | All three root-finders now take the target accuracy; Newton reports the last step and the next correction, fixed-point reports a bound scaled by the ratio the steps shrink by, and bisection prints the number of halvings needed before it starts | COVERED |
| `e4` | Know that fixed point iteration is generally first order; comment on failure | `t_fixed_diag` computes g'(x) symbolically where it can, reports \|g'\|, and says whether the iteration converges, whether it is first or second order, and what to do when it diverges | COVERED |
| `e5` | Understand and apply relaxation to an iteration x(n+1) = g(x(n)) | `t_relax` runs x + L(g(x)-x), reports G'(x) = 1 + L(g'(x)-1), says whether that L converges, and suggests L = 1/(1-g') as the choice that makes the derivative zero | COVERED |
| `Nc1` | Estimate a derivative using forward and central differences with a suitable sequence of h | `t_diff_error` runs both over six halvings of h | COVERED |
| `c2` | Empirical and graphical understanding of the error in numerical differentiation | `t_diff_error` prints the ratio of successive differences, states that 2 means first order and 4 means second, extrapolates both, compares against the exact derivative, and warns that too small an h loses accuracy to cancellation | COVERED |
| `Nc3` | Evaluate a definite integral using the midpoint, trapezium and Simpson's rules | `numeric.t_integ` computes all three in one pass | COVERED |
| `c4` | Know the error behaviour of the integration rules | `t_integ_error` halves h six times for T, M and S, prints the ratio of successive differences for each, states that 4 means h^2 and 16 means h^4, builds Simpson as (2M+T)/3, and shows that (4T2-T1)/3 is the same thing | COVERED |
| `Nf1` | Use Newton's forward difference formula; difference tables | `t_newton_fwd` builds the full difference table and prints the leading differences | COVERED |
| `f2` | Construct the interpolating polynomial (formula given) | `t_newton_fwd` builds p(s) from the binomial coefficients, substitutes s = (x-x0)/h to give p(x), reports the degree, evaluates at any x and warns when that x is outside the table | COVERED |
| `NQ1` | Use a spreadsheet to implement numerical methods | Spreadsheet skill assessed on a computer | N/A |
| `Q2` | Use the iterative capability of a spreadsheet | Spreadsheet skill | N/A |
| `U4` | Understand that computers represent numbers to finite precision | Conceptual | N/A |
| `U5` | Understand the consequences of subtracting nearly equal numbers | Conceptual (`t_err_prop` and `t_diff_error` both demonstrate it) | N/A |

---

## H645 Extra Pure (Y435) - minor option

Toolkit module in scope: `xpure.py`, plus `matrix.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `s4` | Verify a given solution of a recurrence relation | No substitute-and-check tool | MISSING |
| `s6` | Solve first order linear non-homogeneous recurrence relations u(n+1) = a u(n) + f(n) | `t_recur` is the homogeneous constant-coefficient case only | MISSING |
| `s8` | Solve second order linear non-homogeneous recurrence relations u(n+2) = a u(n+1) + b u(n) + f(n) | No particular solution | MISSING |
| `XS1` | Language and notation of sets: subset, union, intersection, complement, empty set | No set tool at all | MISSING |
| `a5` | Understand and work with subgroups | `t_group` never enumerates subgroups | MISSING |
| `a8` | Specify an isomorphism between two groups of the same order | Nothing | MISSING |
| `c2` | Sketch contours and sections of a surface z = f(x, y) | No two-variable plotting; the graph routine takes one variable | MISSING |
| `s2` | Language of recurrence relations: limit, convergent, divergent, periodic | `t_recur` prints a0..a9 and the closed form, so the behaviour is visible; nothing classifies it | PARTIAL |
| `s3` | Investigate and comment on the behaviour of a recurrence relation | Terms a0..a9 only - no long-run behaviour, no limit | PARTIAL |
| `s5` | Solve first order linear homogeneous recurrence relations u(n+1) = a u(n) | Reachable by entering the second-order tool with q = 0, which produces a spurious second root at 0 | PARTIAL |
| `s9` | Investigate and comment on associated sequences and their limits | As `s3` | PARTIAL |
| `a6` | Know and use Lagrange's theorem | `t_group` prints the divisors of n and the order of every element, which is the consequence of Lagrange, but does not identify subgroups or their orders | PARTIAL |
| `m4` | Find powers of a 2x2 or 3x3 matrix using diagonalisation | `t_eigen3` states M^n = P D^n P-inverse, prints P and D and the numeric value of each eigenvalue to the nth power, but does not multiply the three matrices back out to give M^n | PARTIAL |
| `m6` | Understand the significance of eigenvalues and eigenvectors (invariant lines, geometric meaning) | `t_eigen`/`t_eigen3` give the eigenvectors and `matrix.t_invariant` gives the invariant lines, but nothing connects the two | PARTIAL |
| `c6` | Find grad g and evaluate it at a point to give a normal vector | `t_partial` prints grad z = (dz/dx, dz/dy) with its magnitude, and `t_tangent_plane` states that the surface normal is (fx, fy, -1) - which is the spec's own route when g can be written as z = f(x, y). A general g(x, y, z) cannot be entered: no registered tool asks for a third variable | PARTIAL |
| `c3` | Find first order partial derivatives | `xpure.t_partial` is now symbolic: dz/dx, dz/dy, both second derivatives, the mixed one, and a check that d2z/dxdy and d2z/dydx agree | COVERED |
| `c4` | Use dz/dx = 0 and dz/dy = 0 to find stationary points of z = f(x, y) | `t_surface_stat` solves both together by 2-D Newton from a starting guess and classifies with D = fxx fyy - fxy^2, naming the saddle case and saying what to do when D = 0 | COVERED |
| `c7` | Concepts of the tangent plane and the normal line to a surface | `t_tangent_plane` prints the tangent plane in both point form and px + qy - z = k form, and the normal line as r = point + t(fx, fy, -1) | COVERED |
| `m5` | Understand and use the Cayley-Hamilton theorem | `t_eigen3` prints M^3 = tr M^2 - m2 M + det I from the characteristic equation and says that is how to reduce a higher power by hand | COVERED |
| `Xm1` | Understand the meaning of eigenvalue and eigenvector | `xpure.t_eigen3` gives 3x3 eigenvalues and eigenvectors and prints \|Mv - kv\| as a check; `t_eigen` and `matrix.t_eig` do the 2x2 case | COVERED |
| `m2` | Form and solve the characteristic equation det(M - lambda I) = 0 | `t_eigen3` prints k^3 - (trace)k^2 + (sum of minors)k - det = 0 and solves the cubic exactly by the trigonometric/Cardano route | COVERED |
| `m3` | Form the matrix of eigenvectors P and the diagonal matrix D | `t_eigen3` prints P with the eigenvectors as columns and names D, and says when M is not diagonalisable over the reals | COVERED |
| `s7` | Solve second order linear homogeneous recurrence relations | `xpure.t_recur` (all three discriminant cases, fits A and B from a0 and a1, lists a0..a9) | COVERED |
| `Xa1` | Understand the group axioms | `xpure.t_group` checks closure, two-sided identity and all inverses from a Cayley table | COVERED |
| `a2` | Be familiar with examples of groups and use group tables | `t_group` takes any Cayley table up to order 8 | COVERED |
| `a3` | For finite groups, cyclic groups and generation by a single element | `t_group` reports whether the group is cyclic | COVERED |
| `a4` | The order of a finite group and the order of an element | `t_group` prints the order of every element | COVERED |
| `Xs1` | Model appropriate problems by recurrence relations | Modelling judgement | N/A |
| `S2` | The common number sets N, Z, Q, R, C | Notation only | N/A |
| `a7` | Different situations can give rise to isomorphic groups | Conceptual | N/A |
| `Xc1` | z = f(x, y) defines a surface | Definitional | N/A |
| `c5` | g(x, y, z) = c defines a surface | Definitional | N/A |

---

## H645 Further Pure with Technology (Y436) - minor option

Toolkit module in scope: `fpt.py`, plus the CAS, `polar.py`, `purecalc.py` and
`diffeq.py`.

Note: Y436 is sat **with a computer**, and the specification requires access to
graphing software with a slider, a CAS, and a programming language (section
5e). A handheld toolkit can only ever be a partial substitute for that
environment; the verdicts below judge the toolkit against the mathematical
content of each statement, not against the software requirement.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `C4` | Find, describe and generalise properties of a family of curves | No parameter sweeping and no family plotting | MISSING |
| `C9` | Understand the meaning of an envelope of a family of curves | Nothing | MISSING |
| `C10` | Use the limit of an expression | No limit operation in the CAS. `purecalc.t_improper` takes one specific kind of limit numerically, but there is no general one | MISSING |
| `C11` | Determine asymptotes, including oblique asymptotes | Nothing detects or reports an asymptote | MISSING |
| `C12` | Identify cusps by examining the limit of the gradient | Nothing | MISSING |
| `c2` | Use software to produce a tangent to a curve at a variable point | No dynamic tangent; the tangent tools take a fixed point | MISSING |
| `c4` | Verify a given solution of a differential equation | No substitute-and-check tool | MISSING |
| `c6` | Sketch a tangent field for a first order differential equation | Not implemented; this is one of the paper's signature techniques | MISSING |
| `T10` | Solve other Diophantine equations | Only Pell's equation is built; there is no general integer-solution search | MISSING |
| `TC1` | Plot a family of curves in graphing software | `fpt.t_plot` plots one f(x) over a chosen x range; there is no parameter, no slider and no overlay of several curves | PARTIAL |
| `C6` | Find the gradient of the tangent to a curve given in cartesian, polar or parametric form | Cartesian via CAS `Gradient at a point` and `purecalc.t_implicit`; parametric via `t_param_diff`; there is no dy/dx for a curve given as r(theta) | PARTIAL |
| `C7` | Find and work with equations of chords, tangents and normals | `purecalc.t_implicit` gives the tangent and normal for a cartesian or implicit curve and `t_param_diff` for a parametric one; nothing forms the chord between two points on a curve | PARTIAL |
| `Tc1` | Use software to produce analytical solutions of differential equations, with a slider | `diffeq.t_first_order` and `t_particular` now produce complete analytical solutions, but with fixed numeric coefficients: there is no parameter to vary and nothing redraws as it changes | PARTIAL |
| `C2` | Use CAS to work with equations of curves | The whole `Calculus & Algebra` section | COVERED |
| `C5` | Convert equations between cartesian and polar form | `polar.t_topolar_xy`, `t_topolar_rt`, `t_plot` | COVERED |
| `C8` | Calculate arc length using cartesian, polar and parametric forms | `fpt.t_arclen` does all three, differentiating symbolically and integrating by composite Simpson at 400 and 800 panels so the change on halving h is visible | COVERED |
| `c5` | Work with particular solutions and initial conditions | `diffeq.t_first_order` applies a condition and checks the result at the point; `purecalc.t_separable` and `t_constant` do the same for their equations | COVERED |
| `c7` | Solve a first order differential equation numerically by Euler's method | `fpt.t_euler`, `numeric.t_euler` | COVERED |
| `c8` | Understand that a smaller step length usually improves accuracy | `fpt.t_rk` walks the same interval three times with h, h/2 and h/4 and states that halving h divides the Euler error by about 2 and the RK4 error by about 16 | COVERED |
| `c9` | Understand the concepts underlying Runge-Kutta methods | `t_rk` prints k1 to k4 and their weights, and shows Euler, RK2 and RK4 side by side at every step so the effect of probing the slope more than once is visible | COVERED |
| `c10` | Solve first order differential equations using Runge-Kutta methods | `fpt.t_rk` (midpoint RK2 and classical RK4, to 8 decimal places) | COVERED |
| `T3` | Know and use the unique prime factorisation theorem | `fpt.t_factor`, `t_prime` | COVERED |
| `T4` | Solve problems using modular arithmetic | `fpt.t_powmod`, `t_modinv`, `t_gcdlcm`, `t_base`; also `xpure.t_mod` | COVERED |
| `T5` | Know and use Fermat's little theorem | `fpt.t_fermat` computes a^(p-1) mod p, checks gcd(a, p) first, and says what a result other than 1 proves | COVERED |
| `T6` | Know and use Euler's totient function phi(n) | `fpt.t_totient` factorises n, prints the product form n(1 - 1/p)... and the value, and states Euler's theorem | COVERED |
| `T7` | Know and use Wilson's theorem, (p-1)! = -1 (mod p) | `t_fermat` computes (p-1)! mod p by reducing at every step, so no huge integer is built and the `casutil.fact` cap never applies (its own limit is p <= 20000) | COVERED |
| `T8` | Find Pythagorean triples and use them | `fpt.t_pythag` generates every primitive triple with c <= a chosen limit by Euclid's parametrisation | COVERED |
| `T9` | Solve Pell's equation x^2 - n y^2 = 1 | `fpt.t_pell` finds the fundamental solution from the continued fraction of sqrt(n), checks it, and gives the next three solutions | COVERED |
| `C3` | Vocabulary associated with curves: asymptote, cusp, loop, bounded | Terminology only | N/A |
| `c3` | Construct, adapt or interpret a differential equation model | Modelling judgement | N/A |
| `TT1` | Write, adapt and interpret short programs | Programming skill assessed on a computer | N/A |
| `T2` | Identify the limitations of a short program | Discussion | N/A |

---

## Summary counts

Per component, counting each specification statement once. The two Minor papers
are shown with their true statement counts (their content is a strict subset of
the corresponding Major paper, so the audit tables above group them).

| Component | Statements | MISSING | PARTIAL | COVERED | N/A |
|---|---:|---:|---:|---:|---:|
| H640 Pure Mathematics | 154 | 9 | 35 | 86 | 24 |
| H640 Statistics | 54 | 3 | 10 | 28 | 13 |
| H640 Mechanics | 45 | 0 | 5 | 25 | 15 |
| **H640 total** | **253** | **12** | **50** | **139** | **52** |
| H645 Core Pure (Y420) | 99 | 1 | 24 | 59 | 15 |
| H645 Mechanics Major (Y421) | 89 | 1 | 18 | 56 | 14 |
| H645 Statistics Major (Y422) | 72 | 2 | 2 | 47 | 21 |
| H645 Mechanics Minor (Y431) | 49 | 0 | 8 | 32 | 9 |
| H645 Statistics Minor (Y432) | 41 | 0 | 0 | 29 | 12 |
| H645 Modelling with Algorithms (Y433) | 42 | 5 | 5 | 20 | 12 |
| H645 Numerical Methods (Y434) | 21 | 0 | 2 | 15 | 4 |
| H645 Extra Pure (Y435) | 32 | 7 | 8 | 12 | 5 |
| H645 Further Pure with Technology (Y436) | 32 | 9 | 4 | 15 | 4 |
| **H645 total** | **477** | **25** | **71** | **285** | **96** |
| **Grand total** | **730** | **37** | **121** | **424** | **148** |

Neither Minor paper contributes a MISSING statement of its own, so the number
of **distinct** MISSING statements is also **37** (it was 148 at `e1b6812`).

Percentages of the assessable (non-N/A) statements:

| Component | Assessable | COVERED | PARTIAL | MISSING |
|---|---:|---:|---:|---:|
| H640 (all three areas) | 201 | 69% | 25% | 6% |
| H645 Core Pure (Y420) | 84 | 70% | 29% | 1% |
| H645 Mechanics Major (Y421) | 75 | 75% | 24% | 1% |
| H645 Statistics Major (Y422) | 51 | 92% | 4% | 4% |
| H645 Mechanics Minor (Y431) | 40 | 80% | 20% | 0% |
| H645 Statistics Minor (Y432) | 29 | 100% | 0% | 0% |
| H645 Modelling with Algorithms (Y433) | 30 | 67% | 17% | 17% |
| H645 Numerical Methods (Y434) | 17 | 88% | 12% | 0% |
| H645 Extra Pure (Y435) | 27 | 44% | 30% | 26% |
| H645 Further Pure with Technology (Y436) | 28 | 54% | 14% | 32% |

The shape of the result has changed since the last pass. The three weakest
papers then - Modelling with Algorithms at 7% covered, Numerical Methods at 6%,
Statistics Major at 24% - are now at 67%, 88% and 92%. What is left concentrates
in two places: Extra Pure, where the non-homogeneous recurrence relations, sets
and subgroups are simply not built; and Further Pure with Technology, where most
of the remainder is curve-analysis work (limits, asymptotes, cusps, envelopes,
tangent fields) that wants a graphing environment with a slider rather than a
calculator, which is exactly the environment the paper assumes and this toolkit
is not.

---

## The MISSING list, ranked

All 37 distinct MISSING statements, ordered by my judgement of how many exam
marks are at stake. The ordering weighs three things: how many candidates meet
the topic (everyone sits H640; every Further Maths candidate sits Core Pure;
option papers are each a quarter of H645 and chosen by a fraction of the
cohort), how many marks the topic typically carries, and how completely a
calculator tool would convert to marks.

### Tier 1 - highest value

1. **H640 `g9`** Intersection of a line and a circle - a standard coordinate geometry question, met by every candidate, and `pure640._simul_linquad` already has the substitute-and-take-the-discriminant machinery for the parabola case.
2. **H640 `a10`** Use and manipulate surds - exact-answer marks turn up across the whole of H640 Pure, and `sqrt(8)` still does not reduce.
3. **H640 `a11`** Rationalise the denominator of a surd - the other half of the same missing exact-surd engine.
4. **Y420 `c18`** Coupled first order simultaneous differential equations - the only Core Pure statement with nothing behind it, worth 6-10 marks when it appears, and every Further Maths candidate sits this paper.
5. **H640 `E7`** Reduce y = a x^n and y = a b^x to linear form by taking logs - the log-linear regression question in H640/02, now that the scatter plot and the regression line both exist and only the log transform of the lists is missing.
6. **H640 `u5`** Venn diagrams for up to three events - a very common H640/02 question format, and the chart primitives to draw one already exist.
7. **H640 `s7`** Generate a sequence from a formula for the kth term or a recurrence - recurring, and the simplest possible tool.
8. **Y436 `c6`** Sketch a tangent field for a first order differential equation - a signature Y436 task, and the plotting primitives are there.
9. **Y435 `s6`** First order linear non-homogeneous recurrence relations - half of the Extra Pure recurrence topic.
10. **Y435 `s8`** Second order linear non-homogeneous recurrence relations - the other half.

### Tier 2 - high value

11. **H640 `g11`** Circle properties: angle in a semicircle, perpendicular bisector of a chord, tangent perpendicular to radius.
12. **Y435 `c2`** Contours and sections of a surface z = f(x, y) - the rest of the multivariable topic is now covered, so this is the visible gap in it.
13. **Y433 `L6`** Formulate a range of network problems as LPs - both halves of the module exist; nothing bridges them.
14. **Y422 `SH5`** Wilcoxon signed rank test - a named test with nothing implemented, and it needs a critical-value table the toolkit cannot derive.
15. **Y436 `C11`** Determine asymptotes, including oblique.
16. **Y435 `a5`** Subgroups - the natural next step for `t_group`, which already holds the Cayley table.
17. **H640 `D4`** Describe frequency distributions and skew - the histogram and box plot exist, so a shape comment is close.
18. **H640 `g14`** Equation of a circle in parametric form - the parametric tools exist; this is a preset away.
19. **H640 `s10`** Recognise increasing, decreasing and periodic sequences.
20. **Y436 `C10`** Use the limit of an expression - and the block behind it, since `C12` depends on it.

### Tier 3 - moderate

21. **Y435 `s4`** Verify a given solution of a recurrence relation.
22. **Y436 `c4`** Verify a given solution of a differential equation - the same substitute-and-check tool would serve item 21, item 25 and this.
23. **Y421 `v9`** Verify a general or particular solution of a differential equation of motion - likewise.
24. **Y435 `a8`** Specify an isomorphism between two groups of the same order.
25. **Y436 `C12`** Identify cusps by examining the limit of the gradient.
26. **Y436 `C4`** Find, describe and generalise properties of a family of curves.
27. **Y436 `C9`** Envelope of a family of curves.
28. **Y436 `c2`** A tangent to a curve at a variable point - wants a slider, not a calculator.
29. **Y433 `L11`** Use a visualisation of a 3-D LP - out of reach on a 384x192 screen.
30. **Y433 `L16`** Handle variables which may be negative.
31. **Y433 `N13`** Explore network algorithms via LP formulations.
32. **Y433 `L5`** Recognise when an LP requires an integer solution - the recognition is the statement, and it is a judgement.
33. **H640 `a14`** Understand and use proportional relationships.
34. **H640 `D14`** Clean data: missing values, errors, outliers.
35. **Y435 `XS1`** Set notation - low marks, but currently nothing at all.
36. **Y422 `Z2`** Use simulations to investigate distributions - needs a random number generator, which the toolkit lacks entirely.
37. **Y436 `T10`** Other Diophantine equations - open-ended, so a general tool is unlikely to convert to marks.

### A note on the PARTIALs

The MISSING list is now short enough that the PARTIALs are where most of the
remaining marks sit. The ones worth more than anything above:

- `H640 t19` - the trig equation solver takes `sin(px+q) = k` over any interval,
  but an equation that first has to be reduced by an identity (a quadratic in
  sin x, or 3 sin 2x = cos x) cannot be entered at all. This is a recurring
  multi-mark question.
- `H640 a8` / `Ma7` - the inequality solver now gives the solution set correctly,
  including the sign flip and the between-or-outside decision, but nothing draws
  the region. The graphical half is a third of the marks on these questions.
- `Y420 Pc15` and `Y421 v12` - SHM gives omega, T and f but never fits the
  amplitude and phase from initial conditions, which is where the marks are.
- `Y420 v2` - nothing forms a plane from three points, so most of the planes
  topic starts with a step the toolkit cannot take.
- `Y420 j3` - `Factorise` peels off rational roots and `t_quad` finishes a
  quadratic, but the two are not joined, so solving a real cubic for its complex
  roots is still a two-tool manual process.
- `Y420 a2` - only the +k root transformation exists; 2*alpha, 1/alpha and
  alpha^2 are all standard and all absent.
- `Y435 m4` - `t_eigen3` gets as far as P, D and the eigenvalue powers but never
  multiplies out M^n, which is the answer the question asks for.
- `Y433 N9` - total float is computed; independent and interfering float,
  resourcing and scheduling are all named in the statement and none is produced.
- `H640 Mf1` / `a16` - `caspoly.pdivmod` exists but is on no menu, and
  `caspoly.cancel` does not cancel common factors, so polynomial division and
  rational simplification both stop short.
- `Y422 R25` - every continuous-rv tool takes a pdf; none accepts a cdf, so the
  differentiate-the-cdf direction has to be done by retyping into the CAS.
