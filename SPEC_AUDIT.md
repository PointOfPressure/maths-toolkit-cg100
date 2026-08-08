# OCR B (MEI) H640 / H645 specification audit

Every content statement in the two specifications, mapped against what this
toolkit actually does.

## Sources

| Document | Source | Status |
|---|---|---|
| A Level Mathematics B (MEI) **H640**, Version 3 (October 2025) | `https://www.ocr.org.uk/Images/308740-specification-accredited-a-level-gce-mathematics-b-mei-h640.pdf` | PDF downloaded and text-extracted with `pdftotext -layout`. Content section 2f, pp. 22-65. |
| A Level Further Mathematics B (MEI) **H645**, Version 2.1 (2026) | `https://www.ocr.org.uk/images/308768-specification-accredited-a-level-gce-further-mathematics-b-mei-h645.pdf` | PDF downloaded and text-extracted with `pdftotext -layout`. Content sections 2c-2k, pp. 18-127. |

Both PDFs were reachable; nothing in this document is reconstructed from
memory or from the specification-at-a-glance pages. Statement codes and
wording are as printed in the specifications. Items marked `*` in the Ref.
column of the spec are unnumbered assumed-knowledge/GCSE statements; they are
listed here with the code `*` and a bracketed topic.

## Method and conventions

- **Toolkit capability** was read from the `TOOLS = [...]` registry and the
  function bodies of `pure640.py`, `stat640.py`, `mech640.py`, `matrix.py`,
  `vectors.py`, `vcplx.py`, `polyroots.py`, `series.py`, `hyper.py`,
  `polar.py`, `diffeq.py`, `fmmech.py`, `fmstat.py`, `numeric.py`,
  `algos.py`, `xpure.py`, `fpt.py`, plus the CAS (`caseng.simplify` /
  `caseng.diff`, `cascalc.integ` / `cascalc.defint` / `cascalc.solve`) and the
  `casui.cas_section` operations menu.
- Where the label was ambiguous the CAS was **executed** against test inputs
  rather than judged from its name. The findings that follow from that are
  recorded in "CAS facts established by test" below.
- Verdicts: `COVERED` a tool does this; `PARTIAL` a tool touches it but leaves
  a real gap (the gap is stated); `MISSING` nothing does this; `N/A` not a
  calculator task.

### CAS facts established by test

These were verified by running the modules, not inferred:

| Behaviour | Result |
|---|---|
| `cascalc.solve` search window | real roots only, sampled over **[-20, 20]** (radian mode) or [-360, 360] (degree mode). `solve(x-100)` returns `[]`. |
| Integration by partial fractions | **works** for distinct linear factors: `(3x+1)/((x-1)(x+2))` -> `5/3 ln\|x+2\| + 4/3 ln\|x-1\|`. |
| Reverse chain rule, non-linear inner function | **fails**: `x(1+x^2)^8` and `x e^(x^2)` both return `None`. Only linear inner functions and `k f'(x)/f(x)` work. |
| Inverse-trig integral forms | `1/(x^2+1)` -> `atan(x)` works; `1/sqrt(1-x^2)`, `1/sqrt(x^2+1)`, `1/sqrt(x^2-1)` all return `None`. |
| `caseng.simplify` | does **not** expand brackets, does **not** rationalise or reduce surds (`sqrt(8)` stays `sqrt(8)`), does **not** combine numeric fractions (`1/2+1/3` stays as-is), does **not** cancel `(x^2-1)/(x-1)`. |
| `sec`, `cosec`, `cot` | **not in the parser's function list**. `sec(x)` silently parses as the product `s*e*c*x` - a wrong-answer hazard, not just a gap. |
| Second derivative | no `d2/dx2` operation; the CAS menu keeps the original `f(x)`, so the first derivative must be retyped by hand. |
| `casutil.FACT_MAX` | 500. |

---

## H640 Pure Mathematics (assessed across components 01, 02 and 03)

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `*` (Algebra) | Change the subject of a formula | Nothing rearranges symbolically; `caseng.simplify` will not even expand brackets | MISSING |
| `Ma7` | Solve linear inequalities in one variable; represent graphically | No inequality solver anywhere; CAS `Solve` handles equations only | MISSING |
| `a9` | Express solutions of inequalities using and/or or set notation | No inequality output at all | MISSING |
| `a10` | Use and manipulate surds | `simplify` leaves `sqrt(8)` as `sqrt(8)`; no exact surd arithmetic | MISSING |
| `a11` | Rationalise the denominator of a surd | No exact-surd engine | MISSING |
| `a14` | Understand and use proportional relationships (y = kx, y = k/x) | No tool finds k or handles proportion | MISSING |
| `a15` | Express algebraic fractions as partial fractions | `cascalc.integ_rational` decomposes internally but the decomposition is never surfaced as a tool; no standalone partial-fraction output | MISSING |
| `a16` | Simplify rational expressions (factorise, cancel) | `simplify` does not cancel `(x^2-1)/(x-1)` (tested) | MISSING |
| `Mf1` | Add, subtract, multiply and divide polynomials | `simplify` does not expand brackets or collect terms; no polynomial division | MISSING |
| `f4` | Understand and use composite functions gf(x) | No function-composition tool | MISSING |
| `f5` | Understand and use inverse functions and their graphs | No inverse-function tool | MISSING |
| `f7` | Solve simple inequalities involving the modulus function | No modulus inequality solver | MISSING |
| `g9` | Find the point(s) of intersection of a line and a circle | `pure640.t_simul` only handles line + `y=px^2+qx+r`; the circle case is not offered | MISSING |
| `g11` | Circle properties: angle in semicircle, perpendicular bisector of chord, tangent perpendicular to radius | No circle-geometry tool | MISSING |
| `g13` | Convert between cartesian and parametric forms | No parametric handling anywhere | MISSING |
| `g14` | Equation of a circle in parametric form | Not offered by `pure640.t_circle` | MISSING |
| `s7` | Generate a sequence from a formula for the kth term or a recurrence | Only arithmetic/geometric closed forms; `xpure.t_recur` is 2nd-order linear only, in the FM section | MISSING |
| `s10` | Recognise increasing, decreasing and periodic sequences | No sequence-behaviour tool | MISSING |
| `t3` | Area of a triangle = 1/2 ab sin C | No triangle tool at all | MISSING |
| `t4` | Sine rule and cosine rule | No triangle solver anywhere in the toolkit | MISSING |
| `t11` | Arc length s = r*theta and sector area A = 1/2 r^2 theta | No circular-measure tool | MISSING |
| `t12` | Small angle approximations sin x ~ x, cos x ~ 1 - x^2/2, tan x ~ x | Not implemented | MISSING |
| `t13` | Definitions and graphs of sec, cosec and cot | Not in `caslex.UFUNCS`; `sec(x)` silently parses as the product `s*e*c*x` (tested) - actively unsafe | MISSING |
| `t14` | Relationships between the graphs of sin/cos/tan and their reciprocal and inverse functions | No reciprocal trig at all | MISSING |
| `t15` | Use tan^2 + 1 = sec^2 and cot^2 + 1 = cosec^2 | Reciprocal trig functions do not exist in the CAS | MISSING |
| `Mt16` | Identities for sin(A+-B), cos(A+-B), tan(A+-B) | No symbolic trig expansion | MISSING |
| `t17` | Identities for sin 2A, cos 2A, tan 2A | No symbolic trig expansion | MISSING |
| `t19` | Use trigonometric identities to solve equations | `pure640._trig_solve` only handles the bare forms sin/cos/tan x = k | MISSING |
| `E7` | Reduce y = a x^n and y = a b^x to linear form by taking logs | No log-transform of a data list; `t_regress` takes raw x,y only | MISSING |
| `c16` | Differentiate a relation implicitly | CAS is explicit single-variable only | MISSING |
| `c18` | Points of inflection | No second-derivative or inflection tool | MISSING |
| `c21` | Find the constant of integration from a given point | `Integrate` prints "+ C"; no particular-solution step | MISSING |
| `c28` | Integration by substitution in other (non-obvious) cases | Tested: `x(1+x^2)^8`, `x e^(x^2)` both return `None` | MISSING |
| `c32` | Find general/particular solutions of first order differential equations by separating variables | `diffeq.py` does integrating factors and 2nd-order CFs only - separation of variables is not implemented | MISSING |
| `*` (Trigonometry) | Solve right-angled triangles using trig ratios and Pythagoras | Trig values are evaluable in Calculate, but there is no triangle solver | PARTIAL |
| `a8` | Solve quadratic inequalities; represent graphically | `pure640.t_quadratic` gives the roots, which is the hard part, but nothing states the solution interval or shades a region | PARTIAL |
| `a12` | Laws of indices for all rational exponents | `simplify` folds numeric powers only; no symbolic index-law manipulation | PARTIAL |
| `a13` | Negative, zero and fractional indices | Evaluable; not manipulable symbolically | PARTIAL |
| `f2` | Factor theorem; factorise cubics/quartics | `polyroots.t_numeric_roots` / CAS `Solve` give numeric real roots but only in [-20, 20], and never a factorised form | PARTIAL |
| `f6` | Understand and use the modulus function | `abs()` is in the parser, graphable and differentiable; no solving of `\|f(x)\| = k` | PARTIAL |
| `MC1` | Understand and use graphs of functions | CAS `Graph` + `Table of values` plot any parsed f(x) | COVERED |
| `C2` | Find intersection points of two graphs | You must form f-g by hand and use `Solve`, which is limited to [-20, 20]; no two-curve tool | PARTIAL |
| `C4` | Sketch and interpret graphs of polynomial functions | `Graph` plots with auto-scaling; roots, turning points and shape are not annotated | PARTIAL |
| `C5` | Use stationary points when curve sketching | No stationary-point finder; requires Differentiate (retyped) then Solve, range-limited | PARTIAL |
| `C6` | Sketch and interpret y = a/x and y = a/x^2 including asymptotes | `Graph` plots them; no asymptote detection or reporting | PARTIAL |
| `MC7` | Sketch curves y = f(x)+a, f(x+a), af(x), f(ax) | Any transformed expression can be typed and graphed, but there is no transformation tool and no before/after comparison | PARTIAL |
| `C8` | Effect of combined transformations | As `MC7`: manual only | PARTIAL |
| `C9` | Stationary points of inflection | Second derivative must be retyped by hand; no test | PARTIAL |
| `Mg8` | Point(s) of intersection of a line and a curve, or of two curves | `pure640._simul_linquad` covers only line + `y = px^2+qx+r` | PARTIAL |
| `g15` | Gradient of a curve defined parametrically, dy/dx = (dy/dt)/(dx/dt) | Achievable by differentiating each component separately (calling t "x") and dividing by hand; no parametric support | PARTIAL |
| `s4` | Write (a+bx)^n as a^n(1+bx/a)^n and expand | `_binom_int` covers integer n; `_binom_real` only does `(1+x)^n`, so rational n with a != 1 is not supported | PARTIAL |
| `s5` | Use binomial expansions with n rational to approximate (a+bx)^n | Coefficients of `(1+x)^n` only; no substitution/evaluation step, no `(a+bx)^n` for rational n | PARTIAL |
| `s9` | Understand and use sigma notation | `series.py` has closed forms for Sum r, r^2, r^3 only; no general Sigma evaluator | PARTIAL |
| `s11` | Convergent and divergent sequences/series | `t_geo` reports the \|r\|<1 condition and S(inf); nothing else tests convergence | PARTIAL |
| `t7` | Solve simple trig equations in a given interval; principal values | `_trig_solve` is fixed to 0-360 degrees, bare sin/cos/tan only - no arbitrary interval, no radians, no multiple angles (sin 2x) | PARTIAL |
| `t9` | Definitions, domains and ranges of arcsin, arccos, arctan | `asin`/`acos`/`atan` evaluate and differentiate; no domain/range reporting | PARTIAL |
| `t18` | Express a cos t +- b sin t as R cos(t +- alpha) / R sin(t +- alpha) | `pure640._trig_rform` produces the `R sin(x + alpha)` form only; the cosine forms and the sketch are not produced | PARTIAL |
| `E4` | Understand and apply the laws of logarithms | `_log_laws` is a static reference card - it prints the laws but cannot combine or split logs | PARTIAL |
| `E11` | Solve problems involving exponential growth and decay | Evaluation and graphing available; no model-fitting from data | PARTIAL |
| `c4` | Sketch the gradient function for a given curve | Differentiate then Graph, in two manual steps | PARTIAL |
| `c6` | Second derivative as rate of change of gradient | No `d2/dx2`; the first derivative must be retyped | PARTIAL |
| `c7` | Use differentiation to find stationary points and classify them | Nothing solves f'(x)=0 or applies the second-derivative test | PARTIAL |
| `c8` | Increasing and decreasing functions | Sign of f' only by evaluating at chosen points | PARTIAL |
| `c9` | Equation of the tangent and normal to a curve | `Gradient at a point` gives m; the line equation is formed by hand | PARTIAL |
| `c15` | Rates of change using the chain rule, dy/dx = 1/(dx/dy) | Chain rule differentiates; connected-rates problems are manual | PARTIAL |
| `c17` | Concave upwards/downwards sections | Requires a second derivative that has to be retyped | PARTIAL |
| `c23` | Area between a curve and the x-axis including regions below the axis | `Definite integral a..b` returns the signed value; nothing splits at the roots to give a true area | PARTIAL |
| `c26` | Area between two curves; integration with respect to y | f-g must be formed by hand; y-integration works only by renaming the variable | PARTIAL |
| `c27` | Integration by substitution where the process reverses the chain rule | Works for linear inner functions and `k f'/f`; tested failures on `x(1+x^2)^8` and `x e^(x^2)` | PARTIAL |
| `e5` | Understand that not all iterations converge; failure of Newton-Raphson | `numeric.py` lists every iterate and flags divergence, but there is no cobweb/staircase diagram | PARTIAL |
| `c35` | Use rectangles to find upper and lower bounds for an area | `numeric.t_integ` gives midpoint and trapezium; no explicit upper/lower rectangle sums | PARTIAL |
| `v2` | Add and subtract vectors, including using a diagram | `vectors.py` has no add/subtract entry at all; `matrix.py` A+B works if vectors are entered as column matrices | PARTIAL |
| `v5` | Calculate the distance between two points in 2-D/3-D | `pure640.t_coord` does 2-D; there is no two-point 3-D distance tool (only point-to-line and point-to-plane) | PARTIAL |
| `v6` | Use vectors to solve problems in pure and applied contexts | The primitives exist; problem set-up is manual | PARTIAL |
| `*` (Algebra) | Solve linear equations in one unknown | `pure640.t_quadratic` with a=0 solves bx+c=0 exactly | COVERED |
| `Ma2` | Solve quadratic equations | `pure640.t_quadratic` - roots, discriminant, completed square, vertex, complex roots | COVERED |
| `a3` | Find the discriminant and understand its significance | Same tool prints b^2-4ac and the root-nature conclusion | COVERED |
| `a4` | Solve linear simultaneous equations in two unknowns | `pure640._simul_linear` (Cramer, with singular detection) | COVERED |
| `a5` | Simultaneous equations, one linear one quadratic | `pure640._simul_linquad` | COVERED |
| `C3` | Completing the square; y = a(x+p)^2 + q | `t_quadratic` prints the completed-square form and vertex | COVERED |
| `*` (Coord geom) | Understand and use y = mx + c | `pure640.t_coord` | COVERED |
| `Mg1` | Gradient conditions for parallel and perpendicular lines | `t_coord` prints m and the perpendicular gradient | COVERED |
| `g2` | Distance between two points | `t_coord` | COVERED |
| `g3` | Coordinates of the midpoint of a line segment | `t_coord` | COVERED |
| `g4` | Form the equation of a straight line | `t_coord` prints y = mx + c | COVERED |
| `g5` | Draw a line given its equation | CAS `Graph` | COVERED |
| `g6` | Point of intersection of two lines | `_simul_linear` | COVERED |
| `g10` | Equation of a circle (x-a)^2 + (y-b)^2 = r^2 | `pure640.t_circle` both directions, including completing the square | COVERED |
| `Ms1` | Binomial expansion of (a+b)^n for positive integer n | `pure640._binom_int` lists every term | COVERED |
| `s2` | n! and nCr notation | `stat640.t_ncrfact` (n!, nCr, nPr, with a cap) | COVERED |
| `s3` | Binomial expansion of (1+x)^n for rational n | `pure640._binom_real` | COVERED |
| `s12` | Arithmetic sequences and series | `pure640.t_arith` | COVERED |
| `s13` | Standard AP formulae for the nth term and sum | `t_arith` | COVERED |
| `s14` | Geometric sequences and series | `pure640.t_geo` | COVERED |
| `s15` | Standard GP formulae for the nth term and sum | `t_geo` | COVERED |
| `s16` | Condition for a GP to converge; sum to infinity | `t_geo` prints the \|r\|<1 test and a/(1-r) | COVERED |
| `Mt1` | Definitions of sin, cos, tan for any angle | Calculate section with the DEG/RAD toggle | COVERED |
| `t2` | Graphs of sin, cos, tan | CAS `Graph` | COVERED |
| `*` (Trig) | Exact values of sin, cos, tan for 0, 30, 45, 60, 90 degrees | `pure640._trig_exact` reference table | COVERED |
| `Mt8` | Exact values of sin, cos, tan for common angles | `_trig_exact` | COVERED |
| `t10` | Definition and use of the radian | Global DEG/RAD toggle; `casutil.rad`/`deg` | COVERED |
| `ME1` | The function y = a^x and its graph | CAS `Graph` | COVERED |
| `E2` | Convert between index and logarithmic form | `pure640.t_log` (`Solve a^x=b`, `log base c of v`) | COVERED |
| `E5` | Values of log_a a and log_a 1 | `_log_eval` and the reference card | COVERED |
| `E6` | Solve equations of the form a^x = b | `_log_solve` | COVERED |
| `ME8` | The function y = e^x and its graph | CAS `exp`, `Graph` | COVERED |
| `E9` | Gradient of e^kx is k e^kx | CAS `Differentiate` | COVERED |
| `E10` | The function y = ln x and its graph | CAS `ln`, `Graph` | COVERED |
| `Mc1` | Gradient of a curve at a point as the limit of chord gradients | CAS `Gradient at a point` | COVERED |
| `c2` | Gradient of the tangent equals the derivative | Same | COVERED |
| `c3` | Derivative of f(x) as the rate of change | CAS `Differentiate` | COVERED |
| `c5` | Differentiate y = kx^n and related sums/differences | CAS `Differentiate` | COVERED |
| `Mc10` | Differentiate e^kx, a^kx and ln x | CAS `Differentiate` | COVERED |
| `c11` | Differentiate trigonometric functions | CAS `Differentiate` | COVERED |
| `c12` | Product rule | `caseng._d` product rule | COVERED |
| `c13` | Quotient rule | `caseng._d` quotient rule | COVERED |
| `c14` | Chain rule for composite functions | `caseng._d` chain rule throughout | COVERED |
| `Mc19` | Integration as the reverse of differentiation | CAS `Integrate (+ C)` | COVERED |
| `c20` | Integrate kx^n and related sums/differences | `cascalc.integ` power rule | COVERED |
| `c22` | Indefinite and definite integrals | Both operations exist | COVERED |
| `Mc24` | Integrate e^kx, 1/x, sin kx, cos kx and related sums | `cascalc.integ` handles all of these (tested) | COVERED |
| `c29` | Integration by parts in simple cases | `cascalc._byparts` with a depth cap of 3, plus `_cyclic` for e^x sin x | COVERED |
| `c30` | Integrate using partial fractions | `cascalc.integ_rational`; tested `(3x+1)/((x-1)(x+2))` -> correct log form | COVERED |
| `Me1` | Locate roots of f(x)=0 by a change of sign | `numeric.t_bisect` reports the sign-change test explicitly | COVERED |
| `e3` | Fixed point iteration after rearranging to x = g(x) | `numeric.t_fixed` | COVERED |
| `e4` | Newton-Raphson method | `numeric.t_newton` (shows f'(x) and every iterate) | COVERED |
| `Mc34` | Approximate a definite integral by the trapezium rule | `numeric.t_integ` (trapezium, midpoint, Simpson) | COVERED |
| `v3` | Magnitude and direction of a vector; magnitude-direction form | `vectors.t_mag` plus `polar.t_topolar_rt` for (x,y) -> (r,theta) | COVERED |
| `Mv7` | Vectors in three dimensions; unit vectors i, j, k | `vectors.py` is 3-D throughout | COVERED |
| `Mp1` | Structure of mathematical proof; deduction and exhaustion | Writing a proof, no computable content | N/A |
| `p2` | Disprove a conjecture by counter-example | Requires constructing an argument | N/A |
| `p3` | Proof by contradiction | Requires constructing an argument | N/A |
| `Ma1` | Vocabulary and notation (constant, coefficient, identity, ...) | Terminology only | N/A |
| `a6` | Significance of points of intersection in relation to solving equations | Conceptual link; the intersection calculation itself is `Ma4`/`Ma5` | N/A |
| `f3` | Definition of a function; domain and range | Definitional | N/A |
| `f8` | Use functions in modelling | Modelling judgement | N/A |
| `g7` | Use straight-line models | Modelling judgement | N/A |
| `g12` | Meaning of the terms parameter and parametric equations | Terminology only | N/A |
| `g16` | Use parametric equations in modelling | Modelling judgement | N/A |
| `Ms6` | What a sequence is; notation for terms | Terminology only | N/A |
| `s8` | A series is the sum of consecutive terms of a sequence | Definitional | N/A |
| `s17` | Use sequences and series in modelling | Modelling judgement | N/A |
| `t5` | tan(theta) = sin(theta)/cos(theta) | Identity to be quoted, nothing to compute | N/A |
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
| `p24` | Use a variety of sampling techniques: simple random, systematic, stratified, quota, opportunity, cluster | No sampler and no random-number generator anywhere in the toolkit | MISSING |
| `MD1` | Recognise categorical/discrete/continuous/ranked data; interpret bar charts, dot plots, histograms, vertical line charts, pie charts, stem-and-leaf, box plots, frequency charts | No statistical charting of any kind - `stat640` produces numbers only | MISSING |
| `D2` | Area of a histogram bar is proportional to frequency; calculate frequency from frequency density | No histogram/frequency-density tool | MISSING |
| `D3` | Interpret a cumulative frequency diagram | Not implemented | MISSING |
| `D4` | Describe frequency distributions (symmetric, unimodal, bimodal, skewed) | No shape/skew classifier | MISSING |
| `D7` | Recognise when a scatter diagram shows an outlier | 1-D IQR fences only; nothing bivariate | MISSING |
| `D14` | Clean data: missing values, errors, outliers | No data-cleaning tool | MISSING |
| `*` (Probability) | Use tree diagrams and sample space diagrams | No diagram tools | MISSING |
| `u5` | Use Venn diagrams for up to three events | Not implemented | MISSING |
| `p22` | Use samples to make informal inferences about the population | `t_summary` gives the sample statistics; inference is by hand | PARTIAL |
| `D6` | Interpret a scatter diagram and a regression line, including interpolation and extrapolation | `t_regress` computes the line and predicts at a given x, but there is no scatter plot to interpret | PARTIAL |
| `D8` | Recognise and describe correlation | `t_regress` prints r; no plot and no verbal classification | PARTIAL |
| `D11` | Simple measures of spread: range, percentiles, quartiles, IQR | `t_summary` gives range, Q1, Q3, IQR - but not arbitrary percentiles | PARTIAL |
| `D13` | Understand the term outlier and identify outliers | 1.5*IQR fences are implemented; the "more than 2 standard deviations from the mean" rule is not | PARTIAL |
| `*` (Probability) | Understand the concept of a complementary event | `t_prob` gives P(A or B), P(A\|B), P(B\|A); the complement must be formed as 1-P by hand | PARTIAL |
| `*` (Probability) | Calculate the expected frequency of an event | `t_binom` prints the binomial mean np; there is no general n*P(event) tool | PARTIAL |
| `R5` | Calculate expected frequencies from a binomial distribution | Mean np is printed; a full table of expected frequencies is not produced | PARTIAL |
| `H9` | Identify the critical and acceptance regions for a test on a mean | `t_htmean` prints the critical z but not the critical value of the sample mean | PARTIAL |
| `H11` | Use a given correlation coefficient to carry out a hypothesis test for correlation | `t_regress` computes r; no critical values for r and no test decision (contrast `t_htbinom`, which does print a CR) | PARTIAL |
| `MD10` | Standard measures of central tendency: median, mode, mean | `stat640.t_summary` and `t_freq` | COVERED |
| `MD12` | Calculate and interpret variance and standard deviation; Sxx | `t_summary` gives Sxx, s (n-1) and sd (n); `t_freq` the same from a frequency table | COVERED |
| `Mu1` | Mutually exclusive events | `t_prob` addition rule | COVERED |
| `u2` | Add probabilities for mutually exclusive events | `t_prob` | COVERED |
| `u3` | Multiply probabilities for independent events | `t_prob` prints P(A)P(B) and an independence verdict | COVERED |
| `u4` | Mutually exclusive events (part 2) | `t_prob` | COVERED |
| `u6` | Calculate conditional probabilities P(A\|B) = P(A and B)/P(B) | `t_prob` | COVERED |
| `u7` | P(B\|A) = P(B) if and only if A and B are independent | `t_prob` independence check | COVERED |
| `*` (Probability) | Calculate the probability of an event | `t_prob` | COVERED |
| `R3` | Calculate probabilities using the binomial distribution | `t_binom` gives P(X=k), P(X<=k), P(X>=k) (n <= 5000) | COVERED |
| `R4` | Understand and use mean = np | `t_binom` prints np and npq | COVERED |
| `R6` | Use probability functions given algebraically or in a table | `t_drv` | COVERED |
| `R7` | Calculate numerical probabilities for a discrete random variable | `t_drv` (with a sum-to-1 warning) | COVERED |
| `MR8` | Use the Normal distribution as a model | `t_normal` | COVERED |
| `R10` | Linear transformation of a Normal variable; standardising | `t_normal` prints z(a), z(b); `fmstat.t_std` standardises directly | COVERED |
| `R12` | Calculate and use probabilities from a Normal distribution | `t_normal`, `t_invnorm` | COVERED |
| `H2` | Understand when to apply 1-tail and 2-tail tests | Both `t_htbinom` and `t_htmean` ask for the tail and act on it | COVERED |
| `H5` | Conduct a hypothesis test at a given significance level (binomial and Normal) | `t_htbinom`, `t_htmean` | COVERED |
| `H6` | Identify critical and acceptance regions | `t_htbinom` prints the critical region explicitly for all three tail choices | COVERED |
| `MH7` | Sample means from N(mu, sigma^2) are distributed N(mu, sigma^2/n) | `t_htmean` uses SE = sigma/sqrt(n) and prints it | COVERED |
| `H8` | Hypothesis test for a single mean | `t_htmean` | COVERED |
| `MH10` | Correlation as a measure of how close points lie to a line; pmcc | `t_regress` | COVERED |
| `Mp21` | Understand and use the terms population and sample | Terminology only | N/A |
| `p23` | Concept of random sampling; simple random sampling | Conceptual; the mechanics are `p24` | N/A |
| `p25` | Select or evaluate sampling techniques and recognise sources of bias | Judgement | N/A |
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
| `k4` | Draw and interpret kinematics graphs (position-time, velocity-time), including gradient and area | No kinematics graphing; CAS `Graph` plots a typed f(x) but nothing computes area under a v-t graph as displacement | MISSING |
| `Mk9` | Language of 2-D kinematics; position vector, relative position | No relative-position or 2-D kinematics tool | MISSING |
| `k11` | Find the cartesian equation of the path of a particle | No parameter elimination anywhere | MISSING |
| `y3` | Find the initial velocity (speed and angle) of a projectile from given information | `mech640.projectile` runs forward only: it needs u and the angle as inputs and cannot be inverted | MISSING |
| `y4` | Eliminate time from the component equations to get the path equation | Not implemented | MISSING |
| `F8` | Vectors representing a set of forces in equilibrium form a closed polygon | No polygon/triangle of forces drawing | MISSING |
| `k10` | Extend 1-D techniques (calculus and constant acceleration) to 2-D | CAS is scalar; components must be handled separately by hand | PARTIAL |
| `k12` | Use vectors to solve problems in kinematics | `vectors.py` primitives exist; nothing kinematic | PARTIAL |
| `y5` | Solve simple problems involving projectiles, including maximum range | `projectile` gives range for a given angle; no maximum-range or optimal-angle calculation | PARTIAL |
| `F4` | Find the resultant of several concurrent forces | `resultant` takes exactly two forces; `equilibrium` sums up to 8 but reports only Sum Fx, Sum Fy and the resultant magnitude - no direction | PARTIAL |
| `F9` | Formulate and solve equations for a particle in equilibrium (triangle of forces) | `equilibrium` only tests a given set of forces; it does not solve for unknown magnitudes or angles | PARTIAL |
| `n4` | Model a system as connected particles | `pulley` handles only two masses over a smooth pulley; particle-on-table, lift and train systems are not offered | PARTIAL |
| `n5` | Formulate the equations of motion for a connected system | As `n4` | PARTIAL |
| `n6` | A system whose components all have the same acceleration | As `n4` | PARTIAL |
| `n7` | Formulate the equation of motion for a particle in two dimensions | `newton2` is scalar only | PARTIAL |
| `k5` | Differentiate position and velocity with respect to time | CAS `Differentiate` (using x for t) | COVERED |
| `k6` | Integrate acceleration and velocity with respect to time | CAS `Integrate` | COVERED |
| `k7` | Recognise when constant acceleration applies; the suvat formulae | `mech640.suvat` (fixed-point solver over all five suvat relations) | COVERED |
| `k8` | Solve kinematics problems with constant acceleration, including vertical motion under gravity | `suvat` + `casutil.askg` | COVERED |
| `My1` | Model motion under gravity in a vertical plane; projectile assumptions | `mech640.projectile` | COVERED |
| `y2` | Find the position and velocity of a projectile at any time | `projectile` prints x, y, speed and direction at a chosen t | COVERED |
| `F2` | g is not a universal constant; g ~ 9.8 or 10 | `casutil.askg` prompts for g in every mechanics tool that needs it | COVERED |
| `F5` | Concept of equilibrium; the resultant of the forces is zero | `equilibrium` | COVERED |
| `MF6` | Resolve a force into components; select suitable directions | `resolve` | COVERED |
| `F7` | A particle is in equilibrium if and only if the resultant force is zero | `equilibrium` | COVERED |
| `F11` | Model friction by F <= mu R, with F = mu R when sliding | `friction_max`, `friction_horiz`, `friction_incline` all apply the limiting condition correctly | COVERED |
| `F12` | Apply Newton's laws to problems involving friction | `friction_horiz`, `friction_incline` (each decides static vs sliding and gives a) | COVERED |
| `n3` | Formulate the equation of motion for a particle | `newton2` (solves for any one of F, m, a) | COVERED |
| `MF13` | Calculate the moment of a force about a point | `moments` | COVERED |
| `F14` | A rigid body is in equilibrium when the resultant force and the resultant moment are both zero | `moments` reports both sums and can solve for an unknown reaction | COVERED |
| `Mp31` | Language of modelling assumptions: light, smooth, inextensible, particle, rigid | Terminology only | N/A |
| `p32` | Understand and use the particle model | Modelling judgement | N/A |
| `p33` | Fundamental quantities and units (m, s, kg) | Terminology only | N/A |
| `p34` | Derived quantities and units (m/s, m/s^2, N) | Terminology only | N/A |
| `p35` | Derived quantities and units (N m) | Terminology only | N/A |
| `Mk1` | Language of kinematics | Terminology only | N/A |
| `k2` | Difference between position, displacement and distance | Definitional | N/A |
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
| `Pp4` | Construct a proof by induction for the nth term of a sequence, the sum of a series, or the nth power of a matrix | No induction support; `matrix.py` has no M^n operation either | MISSING |
| `Pp5` | Construct a proof by induction generally (divisibility, de Moivre) | Nothing | MISSING |
| `j11` | Represent and interpret loci on an Argand diagram: \|z-a\| = r, \|z-a\| = \|z-b\|, arg(z-a) = theta, and regions | `t_argand` plots isolated points only; no loci and no regions | MISSING |
| `j13` | Apply de Moivre's theorem to trigonometric identities (cos n*theta, tan 4*theta) | No symbolic trig expansion in the CAS | MISSING |
| `Pm6` | Find invariant points and invariant lines of a linear transformation | Not implemented anywhere | MISSING |
| `Pv14` | Find the intersection of a line and a plane | No tool; `vectors.py` has distances and angles only | MISSING |
| `v9` | Form and use the equation of a line in 2-D and 3-D, in vector and cartesian form | `t_ptline`/`t_skew` consume a line as (point, direction) but nothing forms the equation from two points or converts to cartesian | MISSING |
| `Ps2` | Sum a series using partial fractions (method of differences) | Not implemented; `series.py` has Sum r, r^2, r^3 and Maclaurin only | MISSING |
| `Pc1` | Evaluate improper integrals where a limit is infinite or the integrand is undefined at an endpoint | `cascalc.defint` is composite Simpson on a finite interval; it cannot take a limit | MISSING |
| `c2` | Derive formulae for and calculate volumes of revolution about the x- and y-axes | No volume-of-revolution tool | MISSING |
| `c8` | Recognise differential equations where the variables are separable | No separable-DE handling | MISSING |
| `c14` | Find particular integrals in simple cases (polynomial, exponential, trigonometric f(x)) | `diffeq.t_second_order` produces the complementary function only | MISSING |
| `c18` | Analyse and interpret coupled first order simultaneous differential equations (e.g. predator-prey) | Not implemented | MISSING |
| `a2` | Form a new equation whose roots are related to the original (2*alpha, alpha+k, 1/alpha, alpha^2) | `polyroots.t_shift_roots` covers only the +k substitution; scaling, reciprocal and squaring are not implemented | PARTIAL |
| `j3` | Complex roots occur in conjugate pairs; solve cubic and quartic equations with real coefficients | `polyroots.t_numeric_roots` gives real roots only, in [-20, 20]; no complex root extraction beyond the quadratic case | PARTIAL |
| `j8` | Multiply and divide complex numbers in modulus-argument form | `vcplx.t_arith` multiplies and divides but reports the answer in cartesian form only; nothing shows r1*r2 and theta1+theta2 | PARTIAL |
| `j10` | Represent sum, difference, product and quotient on an Argand diagram | `t_argand` plots points; no vector/parallelogram construction and no link to `t_arith` | PARTIAL |
| `j19` | Represent the complex roots of unity on an Argand diagram | `t_roots` lists them; plotting requires retyping each root into `t_argand` | PARTIAL |
| `j20` | Apply complex numbers to geometrical problems (regular polygons) | Roots and moduli available; the geometry is manual | PARTIAL |
| `m2` | Understand and use the zero and identity matrices | No built-in I or 0; the user types them in | PARTIAL |
| `m4` | Find the matrix of a given 2-D transformation and vice versa; 3-D reflections in x=0/y=0/z=0 and rotations of multiples of 90 degrees about an axis | `matrix.t_transform` builds 2-D matrices only; the 3-D transformations named in the spec are absent, and there is no matrix -> description direction | PARTIAL |
| `m5` | Successive transformations and matrix multiplication | `A*B` works, but the composed matrix is not described as a transformation | PARTIAL |
| `m9` | The magnitude of a 3x3 determinant is the volume scale factor; the sign gives orientation | `t_det` computes a 3x3 determinant; only the 2-D tool mentions the area/scale interpretation, and orientation is never reported | PARTIAL |
| `m15` | Find the determinant and inverse of a 3x3 matrix without a calculator, possibly with algebraic terms | Numeric 3x3 only; algebraic entries are not supported | PARTIAL |
| `v2` | Form and use the vector and cartesian equation of a plane | Tools accept a plane as n.r = d; nothing forms the plane from three points or a point and two directions | PARTIAL |
| `v4` | The different ways in which three distinct planes can intersect (point, line, sheaf, prism, parallel) | `matrix.t_solve` finds the unique point and reports "singular" otherwise, but never classifies the configuration | PARTIAL |
| `v11` | The different ways in which two lines can meet (intersect, parallel, skew) | `t_skew` detects parallel and gives the skew distance; it does not confirm intersection or give the point | PARTIAL |
| `v12` | Determine whether two lines intersect | Inferable from `t_skew` distance = 0, but the intersection point is never produced | PARTIAL |
| `v15` | Calculate the angle between a line and a plane | `t_angle` on direction and normal then 90 - theta by hand; `t_planeangle` is plane-to-plane only | PARTIAL |
| `s4` | A Maclaurin series may converge only for a restricted set of x | The reference card states the intervals of validity; nothing tests convergence | PARTIAL |
| `c3` | Understand and evaluate the mean value of a function on [a, b] | `Definite integral a..b` then divide by (b-a) by hand; no mean-value tool | PARTIAL |
| `c6` | Recognise integrals giving arcsin and arctan forms | Tested: `1/(x^2+1)` -> `atan(x)` works; `1/sqrt(1-x^2)` returns `None` | PARTIAL |
| `a5` | Differentiate and integrate hyperbolic functions | Differentiation of sinh/cosh/tanh/arsinh/arcosh/artanh all present; `cascalc.integ` handles sinh and cosh but returns `None` for tanh (tested) | PARTIAL |
| `a8` | Recognise integrals of 1/sqrt(x^2+a^2) and 1/sqrt(x^2-a^2) giving arsinh and arcosh | `hyper.t_ref` prints these as a reference card, but `cascalc.integ` returns `None` for both (tested) | PARTIAL |
| `p21` | Language of kinematics, including a = v dv/dx | CAS can differentiate; the relation itself is not encoded | PARTIAL |
| `p22` | Use differential equations in modelling in kinematics | `diffeq.py` primitives exist; set-up is manual | PARTIAL |
| `c10` | Solve an equation using an integrating factor, including finding a particular solution | `diffeq.t_first_order` computes int P dx and shows the IF and the method, but it never performs int (IF * Q) dx and never applies an initial condition - the answer is not produced | PARTIAL |
| `c13` | Solve a y'' + b y' + c y = f(x) | `t_second_order` gives the complementary function only; no particular integral, so the general solution is never completed | PARTIAL |
| `Pc15` | Solve the simple harmonic motion equation and relate the solution to the motion | `diffeq.t_shm` gives omega, T, f and both general forms, but does not fit A and phi (or C and D) from initial conditions | PARTIAL |
| `Pj1` | Language of complex numbers: real part, imaginary part, conjugate, modulus, argument | `vcplx.t_modarg` (prints the conjugate too) | COVERED |
| `j2` | Solve any quadratic equation with real coefficients | `vcplx.t_quad` (real and complex cases) | COVERED |
| `j4` | Add, subtract, multiply and divide complex numbers in x + yi form | `vcplx.t_arith` | COVERED |
| `j6` | Use radians in the context of complex numbers | `t_modarg` works in radians and recognises exact multiples of pi | COVERED |
| `j7` | Represent a complex number in modulus-argument form and convert both ways | `t_modarg`, `t_topolar`, `t_frompolar` | COVERED |
| `j9` | Represent and interpret complex numbers on an Argand diagram | `vcplx.t_argand` (up to 8 points, native plot) | COVERED |
| `Pj12` | Understand and use de Moivre's theorem | `vcplx.t_power`, `fpt.t_demoivre` | COVERED |
| `j14` | The definition e^(i theta) = cos theta + i sin theta; exponential form | `t_topolar` prints `z = r e^(i t)` | COVERED |
| `j15` | Every non-zero complex number has n distinct nth roots | `vcplx.t_roots` | COVERED |
| `j16` | The distinct nth roots of r e^(i theta) | `t_roots` (also `fpt.t_roots`, which prints the 2pi/n argument step) | COVERED |
| `Pm1` | Add, subtract and multiply matrices up to 3x3 | `matrix.py` (`A+B`, `A-B`, `kA`, `A*B`, transpose) | COVERED |
| `m7` | Calculate the determinant of a 2x2 matrix (and 3x3 with a calculator) | `matrix.t_det` (1x1, 2x2, 3x3) | COVERED |
| `m8` | The magnitude of a 2x2 determinant is the area scale factor | `t_transform` prints `\|det\| = area scale` | COVERED |
| `m11` | Understand what is meant by an inverse matrix; singular matrices | `t_inv` detects \|det\| < 1e-9 and reports singular | COVERED |
| `m12` | Calculate the inverse of a non-singular matrix (2x2 by hand, 3x3 with a calculator) | `t_inv` (closed form for 2x2, adjugate for 3x3) | COVERED |
| `m13` | Use the inverse of a matrix to solve a matrix equation | `t_solve` (Gauss-Jordan with partial pivoting) | COVERED |
| `Pv1` | Scalar product; test for perpendicularity; angle between vectors | `vectors.t_dot`, `t_angle`, `t_paraperp` | COVERED |
| `v3` | A vector perpendicular to two given vectors | `vectors.t_cross` | COVERED |
| `v5` | Solve three linear simultaneous equations using a matrix inverse | `matrix.t_solve` with a 3x3 A | COVERED |
| `v6` | The angle between two planes from their normals | `vectors.t_planeangle` (takes the acute angle) | COVERED |
| `Pv7` | Use the vector product in solving problems | `vectors.t_cross` | COVERED |
| `v8` | The alternative form a x b = \|a\|\|b\| sin(theta) n-hat | `t_cross` gives the vector and its magnitude; `t_unit` normalises it | COVERED |
| `v10` | Calculate the angle between two lines | `t_angle` applied to the direction vectors | COVERED |
| `v13` | Find the distance between two skew lines | `vectors.t_skew` | COVERED |
| `v16` | Find the distance from a point to a line | `vectors.t_ptline` (also gives the foot of the perpendicular) | COVERED |
| `v17` | Find the distance from a point to a plane | `vectors.t_ptplane` | COVERED |
| `Pa1` | Relationships between the roots and coefficients of quadratic, cubic and quartic equations | `polyroots.t_vieta_quad`, `t_vieta_cubic`, `t_vieta_quartic` | COVERED |
| `Ps1` | Standard formulae for Sum r, Sum r^2 and Sum r^3 | `series.t_sum_r`, `t_sum_r2`, `t_sum_r3` | COVERED |
| `s3` | Find the Maclaurin series of a function and use it for approximation | `series.t_maclaurin` (up to 6 terms, by repeated `caseng.diff`) and `t_approx` (value plus error) | COVERED |
| `s5` | Recognise and use the standard Maclaurin series and their intervals of validity | `series.t_reference` plus `t_maclaurin` | COVERED |
| `c4` | Use partial fractions in integration | `cascalc.integ_rational`; tested correct on distinct linear factors | COVERED |
| `c5` | Differentiate inverse trigonometric functions | `caseng.diff` for asin, acos, atan | COVERED |
| `PP1` | Understand and use polar coordinates and convert to and from cartesian | `polar.t_topolar_xy`, `t_topolar_rt` | COVERED |
| `P2` | Sketch curves with simple polar equations | `polar.t_plot` (any r(theta)) and `t_preset` (cardioid, rose, circle) | COVERED |
| `P3` | Find the area enclosed by a polar curve | `polar.t_area` (Simpson on 1/2 * int r^2 d(theta)) | COVERED |
| `Pa3` | Definitions of sinh, cosh, tanh and their graphs | `hyper.py` evaluates all three; `caslex` parses them so CAS `Graph` draws them | COVERED |
| `Pa6` | Definitions and domains of arsinh, arcosh, artanh | `hyper.t_arsinh`, `t_arcosh`, `t_artanh` (with domain checks) | COVERED |
| `a7` | Derive and use the logarithmic forms of the inverse hyperbolic functions | Each inverse tool prints the logarithmic form alongside the value | COVERED |
| `*` (Kinematics) | Newton's second law F = ma | `mech640.newton2` | COVERED |
| `c9` | Find an integrating factor and understand its use | `diffeq.t_first_order` computes int P dx and the IF e^(int P dx) | COVERED |
| `c11` | Solve a y'' + b y' + c y = 0 via the auxiliary equation | `diffeq.t_second_order` (all three discriminant cases) | COVERED |
| `c12` | Relationship between the discriminant of the auxiliary equation and the form of the solution | `t_second_order` prints the discriminant and branches on it | COVERED |
| `c16` | Model damped oscillations with second order differential equations | `diffeq.t_damping` and `t_second_order` | COVERED |
| `c17` | Interpret solutions as over-, under- or critically damped | `diffeq.t_damping` names the case and describes the motion | COVERED |
| `*` (Proof) | Prove results by deduction and exhaustion; disprove by counter-example | Proof writing | N/A |
| `*` (Proof) | Prove results by contradiction | Proof writing | N/A |
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
`diffeq.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `q3` | Determine the units of a quantity from its dimensions | `fmmech.t_dim` only compares two dimension triples that the user has already worked out | MISSING |
| `q4` | Change the units in which a quantity is measured | No unit conversion anywhere | MISSING |
| `d9` | A closed figure (triangle of forces) may be drawn to represent forces in equilibrium | No force-polygon construction | MISSING |
| `d13` | The meaning of the term couple | No couple calculation | MISSING |
| `d16` | Identify whether equilibrium is broken by sliding or by toppling | Not implemented; `friction_incline` decides slide/no-slide but never tests toppling | MISSING |
| `Mi13` | Oblique impact and the modelling assumptions | Nothing oblique - `t_restitution` is 1-D only | MISSING |
| `i14` | Newton's Experimental Law for oblique impact (component along the line of centres) | Nothing | MISSING |
| `i15` | Model oblique impact between a sphere and a surface | Nothing | MISSING |
| `i16` | Model oblique impact between two spheres | Nothing | MISSING |
| `i17` | Calculate the loss of kinetic energy in an oblique impact | Nothing (the 1-D tool does report KE lost) | MISSING |
| `r6` | Calculate tangential acceleration | `t_circular` gives radial quantities only | MISSING |
| `h5` | Calculate the equilibrium position of a mass on an elastic string or spring | `t_hooke` computes T and EPE from lambda, x, l; it does not solve mg = lambda x / l for x | MISSING |
| `h7` | Use energy principles with elastic strings/springs (e.g. maximum extension) | No energy-equation solver | MISSING |
| `G3` | Know the positions of the centres of mass of standard uniform bodies | No reference table | MISSING |
| `G5` | Use the position of the centre of mass in problems about equilibrium and toppling | Not implemented | MISSING |
| `MG6` | Calculate the volume generated by rotating a region about the x- or y-axis | No solid-of-revolution tool | MISSING |
| `G7` | Use calculus to find the centre of mass of a uniform solid of revolution | Nothing | MISSING |
| `G9` | Use calculus to find the centre of mass of a uniform lamina or arc | Nothing | MISSING |
| `G10` | Use the centre of mass in problems about the equilibrium of rigid bodies | Nothing | MISSING |
| `Mk1` | Language of 2-D kinematics; position vector, relative position | No relative-motion tool | MISSING |
| `Mv3` | Eliminate a parameter from parametric equations | Not implemented | MISSING |
| `v4` | Interpret the resulting cartesian equation (e.g. a bounding parabola) | Nothing | MISSING |
| `v5` | Derive the cartesian equation of the path of a projectile | Nothing | MISSING |
| `v6` | Find the range of a projectile up or down an inclined plane | `mech640.projectile` is level-ground only | MISSING |
| `v7` | Find the maximum range of a projectile | No optimisation | MISSING |
| `v9` | Verify a general or particular solution of a differential equation of motion | No substitution/verification tool | MISSING |
| `v10` | Use boundary or initial conditions to determine constants | Not implemented in any DE tool | MISSING |
| `Mq1` | Find the dimensions of a quantity in terms of M, L and T | `t_dim` checks a pair of triples for consistency; it cannot derive the dimensions of a named quantity | PARTIAL |
| `q2` | Understand that some quantities are dimensionless | Falls out of `t_dim` (all-zero triple) but is never named | PARTIAL |
| `q6` | Use dimensional analysis to determine unknown indices (e.g. period of a pendulum) | Requires solving simultaneous index equations; `matrix.t_solve` could be pressed into service manually, but nothing does it | PARTIAL |
| `d4` | Derive and use mu = tan(alpha) for a body on the point of slipping | `friction_incline` decides slide vs rest for a given angle; it never returns the critical angle | PARTIAL |
| `d7` | Find the resultant of several concurrent forces | `mech640.resultant` takes two; `equilibrium` sums up to 8 but gives magnitude only, not direction | PARTIAL |
| `d10` | Formulate and solve equilibrium equations by resolving, or by a polygon of forces | `equilibrium` tests a known set of forces; it does not solve for unknowns | PARTIAL |
| `w2` | Calculate the work done by a force, including a variable force (calculus) | `t_work` does W = F d only - no F cos(theta) d and no integral of F dx | PARTIAL |
| `w3` | Work done by a force in a given direction; scalar product | As `w2`; `vectors.t_dot` exists but is not wired to work | PARTIAL |
| `w6` | Conservation of mechanical energy | KE and GPE are computed separately; there is no energy-equation solver | PARTIAL |
| `w7` | The work-energy principle | As `w6` | PARTIAL |
| `i9` | Apply Newton's Experimental Law (e.g. between a particle and a wall) | `t_restitution` requires two finite masses; the wall case needs the user to fake m2 as very large | PARTIAL |
| `r4` | Model horizontal circular motion (conical pendulum, car on a bend) | Only the conical pendulum is implemented; banked tracks and friction-limited cornering are not | PARTIAL |
| `r5` | Model circular motion with more than one force acting | As `r4` | PARTIAL |
| `r7` | Model motion in a vertical circle using conservation of energy | Only the minimum speed at the top, v = sqrt(gr) | PARTIAL |
| `r8` | Identify conditions under which a particle departs from circular motion | Implicit in the vertical-circle formula; no condition test | PARTIAL |
| `h3` | Calculate the stiffness or modulus of elasticity | `t_hooke` runs forward from lambda, x, l; it cannot be inverted for lambda or k | PARTIAL |
| `MG1` | Find the centre of mass of a system of particles in 1, 2 and 3 dimensions | `fmmech.t_com` does 1-D and 2-D only - no z coordinate | PARTIAL |
| `k2` | Extend kinematics techniques to 2-D using calculus and constant acceleration | Components must be handled separately by hand | PARTIAL |
| `v2` | Use acceleration, velocity and position to infer the force acting | CAS differentiates; `newton2` multiplies by m; not joined up | PARTIAL |
| `v12` | Solve the SHM equation, including amplitude and period | `diffeq.t_shm` gives omega, T, f and the general forms but does not compute the amplitude from initial conditions | PARTIAL |
| `q5` | Use dimensional analysis to check the consistency of a formula | `fmmech.t_dim` | COVERED |
| `d3` | Model friction by F <= mu R with F = mu R when sliding | `mech640.friction_max`, `friction_horiz`, `friction_incline` | COVERED |
| `d5` | Apply Newton's laws to situations involving friction | `friction_horiz`, `friction_incline` | COVERED |
| `d6` | Resolve a force into components and select suitable directions | `mech640.resolve` | COVERED |
| `Md8` | A particle is in equilibrium if and only if the resultant of the concurrent forces is zero | `mech640.equilibrium` | COVERED |
| `d14` | Calculate moments about a fixed axis | `mech640.moments` | COVERED |
| `d15` | Conditions for the equilibrium of a rigid body | `moments` (sum of forces and sum of moments, plus an unknown reaction) | COVERED |
| `w4` | Calculate kinetic energy | `fmmech.t_work` option 1 | COVERED |
| `w5` | Calculate gravitational potential energy | `t_work` option 2 (prompts for g) | COVERED |
| `w8` | Power as force times the component of velocity | `t_work` options 4 and 5 (P = Fv and P = W/t) | COVERED |
| `Mi1` | Calculate the impulse of a force | `fmmech.t_momentum` option 2 | COVERED |
| `i2` | Understand and use linear momentum | `t_momentum` prints total p | COVERED |
| `i3` | The impulse-momentum equation | `t_momentum` (J = m(v-u)) | COVERED |
| `i4` | Internal impulses cancel, so momentum is conserved | `t_momentum` option 1 solves m1u1+m2u2 = m1v1+m2v2 | COVERED |
| `Mi6` | Apply conservation of linear momentum to direct impact | `t_momentum` option 1 | COVERED |
| `i7` | Newton's Experimental Law and the coefficient of restitution | `fmmech.t_restitution` (solves both final velocities) | COVERED |
| `i8` | The significance of e = 0 (the bodies coalesce) | `t_restitution` with e = 0 gives the common velocity | COVERED |
| `i10` | Model situations involving direct impact | `t_restitution` | COVERED |
| `i11` | The significance of e = 1 (perfectly elastic) | `t_restitution` with e = 1 reports zero KE loss | COVERED |
| `i12` | When e < 1 kinetic energy is not conserved | `t_restitution` prints the KE lost | COVERED |
| `r3` | Calculate the acceleration towards the centre, v^2/r and omega^2 r | `fmmech.t_circular` options 1 and 2 (also gives omega and F) | COVERED |
| `h2` | Hooke's law models the tension in an elastic string or spring | `fmmech.t_hooke` | COVERED |
| `h4` | Calculate the tension in an elastic string or spring | `t_hooke` (T = lambda x / l) | COVERED |
| `h6` | Calculate the energy stored in a stretched string or spring | `t_hooke` (EPE = lambda x^2 / (2l)) | COVERED |
| `G4` | Find the centre of mass of a composite body | `fmmech.t_com` (negative masses model removed pieces) | COVERED |
| `G8` | Find the centre of mass of a compound body by treating parts as particles | `t_com` | COVERED |
| `Mv1` | Find acceleration, velocity and position by calculus (variable acceleration) | CAS `Differentiate` / `Integrate` | COVERED |
| `v11` | Recognise and formulate the simple harmonic motion equation | `diffeq.t_shm` and `t_damping` | COVERED |
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
the one `*` item). Every verdict is therefore identical to the Y421 row for
the same code. Summarised:

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `q3` | Determine the units of a quantity | As Y421 | MISSING |
| `q4` | Change units | As Y421 | MISSING |
| `d9` | Triangle/closed figure of forces | As Y421 | MISSING |
| `d13` | Couples | As Y421 | MISSING |
| `d16` | Sliding versus toppling | As Y421 | MISSING |
| `G3` | Centres of mass of standard bodies | As Y421 | MISSING |
| `G5` | Centre of mass in equilibrium/toppling problems | As Y421 | MISSING |
| `Mq1`, `q2`, `q6` | Dimensional analysis (derive dimensions; unknown indices) | As Y421 | PARTIAL |
| `d4`, `d7`, `d10` | Critical slipping angle; resultant of many forces; solving equilibrium | As Y421 | PARTIAL |
| `w2`, `w3`, `w6`, `w7` | Work at an angle / variable force; energy conservation; work-energy | As Y421 | PARTIAL |
| `i9` | NEL against a wall | As Y421 | PARTIAL |
| `MG1` | Centre of mass in 3-D | As Y421 (1-D and 2-D only) | PARTIAL |
| `q5` | Dimensional consistency check | `fmmech.t_dim` | COVERED |
| `d3`, `d5`, `d6`, `Md8`, `d14`, `d15` | Friction, Newton's laws with friction, resolving, equilibrium, moments | `mech640.py` | COVERED |
| `w4`, `w5`, `w8` | KE, GPE, power | `fmmech.t_work` | COVERED |
| `Mi1`-`i4`, `Mi6`-`i8`, `i10`-`i12` | Impulse, momentum, restitution, KE loss | `fmmech.t_momentum`, `t_restitution` | COVERED |
| `G4` | Composite centre of mass | `fmmech.t_com` | COVERED |
| `q7`, `*`, `Md1`, `d2`, `d11`, `d12`, `Mw1`, `i5` | Terminology, diagrams and modelling judgement | - | N/A |
| `G2` | Symmetry arguments | - | N/A |

---

## H645 Statistics Major (Y422) - major option

Toolkit modules in scope: `fmstat.py`, plus `stat640.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `SR6` | Find the expectation of a linear combination of random variables, E(X +- Y) | Not implemented | MISSING |
| `R17` | Calculate probabilities within a geometric distribution, P(X=r) = (1-p)^(r-1) p | No geometric distribution anywhere in `fmstat.py` | MISSING |
| `R18` | Mean and variance of a geometric distribution | Nothing | MISSING |
| `b2` | Use and interpret a scatter diagram, including looking for outliers by eye | No scatter plot; `fmstat` is numeric only | MISSING |
| `Sb6` | Carry out a hypothesis test for correlation using the pmcc | `t_pmcc` returns r only; there are no critical values for r and no test decision | MISSING |
| `b9` | Carry out a hypothesis test using Spearman's rank correlation coefficient | `t_spear` returns rs only; no critical values, no decision | MISSING |
| `b15` | The relationship between the two regression lines and which to use | Only the y-on-x line exists | MISSING |
| `Sb16` | Interpret bivariate categorical data | Nothing | MISSING |
| `SH1` | Apply the chi-squared test for association in a contingency table | `t_chi` is goodness-of-fit only: it takes O and E as flat lists, uses df = cells - 1, and never computes expected values from row/column totals or uses (r-1)(c-1) | MISSING |
| `SR19` | Use a simple continuous random variable as a model | No continuous-rv machinery at all | MISSING |
| `R20` | The meaning of a probability density function, including piecewise pdfs | Nothing | MISSING |
| `R21` | Properties of a pdf (non-negative, integrates to 1) | Nothing | MISSING |
| `R23` | Find the mode and median of a continuous random variable | Nothing | MISSING |
| `R24` | The meaning of a cumulative distribution function | Nothing | MISSING |
| `R26` | Use a cdf to calculate the median and quartiles | Nothing | MISSING |
| `R27` | Find the mean of a linear combination of random variables | Nothing | MISSING |
| `R29` | Use linear combinations of independent Normal random variables | No aX +- bY combination tool | MISSING |
| `R31` | Interpret a Normal probability plot | No plotting of any kind | MISSING |
| `I11` | Construct and interpret a confidence interval for a mean difference from paired data | `t_cimean` is single-sample only | MISSING |
| `SH5` | Carry out a hypothesis test for an average using the Wilcoxon signed rank test | Not implemented; no rank-sum statistic and no critical values | MISSING |
| `Z2` | Use simulations to investigate distributions | No random-number generator anywhere | MISSING |
| `R4` | Use E(a + bX) = a + bE(X) | `t_drv` gives E(X); the transformation is applied by hand | PARTIAL |
| `R5` | Use Var(a + bX) = b^2 Var(X) | As `R4` | PARTIAL |
| `R7` | Recognise the discrete uniform distribution | Modelled only by typing equal probabilities into `t_drv` | PARTIAL |
| `R8` | Calculate probabilities from a discrete uniform distribution | As `R7` | PARTIAL |
| `R9` | Mean and variance of a discrete uniform distribution | Falls out of `t_drv`; no closed-form tool | PARTIAL |
| `R12` | Recognise when the Poisson approximates the binomial | Both distributions exist; no comparison or approximation-validity check | PARTIAL |
| `R14` | Know and use the mean and variance of a Poisson distribution (both equal lambda) | `t_pois` prints pmf and cdf but never the mean or variance | PARTIAL |
| `b12` | Use the regression line as a model; residuals | `t_reg` predicts at a given x but does not compute residuals | PARTIAL |
| `b13` | Calculate the equations of both regression lines (y on x and x on y) | Only y on x | PARTIAL |
| `b14` | Check how well the model fits the data (visual inspection, pmcc^2) | r is available from `t_pmcc`; r^2 is not reported and there is no plot | PARTIAL |
| `H2` | Interpret the results of a chi-squared test | `t_chi` reports a reject/accept decision, but only against a hard-coded 5% table for df 1-10 - no p-value and no other significance levels | PARTIAL |
| `H3` | Carry out a chi-squared goodness-of-fit test | `t_chi` computes the statistic, but expected frequencies must be supplied by hand and df is always cells - 1, so any distribution with estimated parameters gets the wrong df | PARTIAL |
| `H4` | Interpret the results of a chi-squared goodness-of-fit test | As `H2` | PARTIAL |
| `SR22` | Find the mean and variance of a continuous random variable | Achievable only by typing x*f(x) into the CAS `Definite integral`; nothing statistical does it | PARTIAL |
| `R25` | Obtain a pdf from a given cdf by differentiation | CAS `Differentiate` will do it if the cdf is typed as f(x); no statistical wrapper | PARTIAL |
| `R32` | Use the Normal distribution when the parameters have to be estimated from a sample | `t_summary` estimates mu and s; `t_norm` then takes them, but nothing links the two or adjusts for estimation | PARTIAL |
| `I9` | Construct and interpret a confidence interval for a population mean | `fmstat.t_cimean` uses z with a known sigma and warns "small n: use t, not z" - there is no t distribution in the toolkit | PARTIAL |
| `I13` | Use a confidence interval to test a hypothesis about a population mean | `t_cimean` gives the interval; the comparison is done by eye | PARTIAL |
| `SR1` | Use probability functions given algebraically or in a table | `fmstat.t_drv` | COVERED |
| `R2` | Calculate the expectation (mean) of a discrete random variable | `t_drv` | COVERED |
| `R3` | Calculate the variance using Var(X) = E(X^2) - mu^2 | `t_drv` (prints E[X], E[X^2], Var[X], SD) | COVERED |
| `R13` | Calculate probabilities using a Poisson distribution | `fmstat.t_pois` (pmf, cdf, upper tail, single-pass cdf) | COVERED |
| `b4` | Calculate the pmcc from raw data | `fmstat.t_pmcc` (also prints Sxy, Sxx, Syy) | COVERED |
| `Sb8` | Calculate Spearman's rank correlation coefficient | `fmstat.t_spear` (pmcc of ranks, ties averaged) | COVERED |
| `Sb11` | Calculate the equation of the least squares regression line | `fmstat.t_reg`, `stat640.t_regress` | COVERED |
| `SR28` | Use the Normal distribution as a model and calculate probabilities | `fmstat.t_norm`, `t_std`, `t_inv` | COVERED |
| `SI1` | Estimate a population mean from a sample | `stat640.t_summary` | COVERED |
| `I2` | Estimate a population variance using the divisor n - 1 | `t_summary` prints s (n-1) alongside the population sd | COVERED |
| `I4` | Calculate and interpret the standard error of the mean | `t_cimean` and `t_ztest` both print SE = sigma/sqrt(n) | COVERED |
| `H6` | Carry out a hypothesis test for a population mean using the Normal distribution | `fmstat.t_ztest` (1- and 2-tail critical values and a p-value) | COVERED |
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
| `b7` | Use the pmcc as an effect size | Judgement | N/A |
| `b10` | Decide whether a test based on r or on rs is more appropriate | Judgement | N/A |
| `R30` | The Normal distribution as a useful model; when it is appropriate | Modelling judgement | N/A |
| `I3` | The sample mean is a random variable with a sampling distribution | Conceptual | N/A |
| `I5` | The sampling distribution of the mean when the parent is Normal | Conceptual | N/A |
| `I6` | How and when the Central Limit Theorem applies | Conceptual | N/A |
| `SI7` | The meaning of the term confidence interval | Definitional | N/A |
| `I8` | Factors affecting the width of a confidence interval | Conceptual | N/A |
| `I10` | Know when samples from two populations should be paired | Judgement | N/A |
| `SI12` | Interpret confidence intervals given by software | Interpretation of given output | N/A |
| `SZ1` | Know that spreadsheets can be used for statistical work | Spreadsheet skill, assessed on a computer, not a calculator task | N/A |

---

## H645 Statistics Minor (Y432) - minor option

The Minor paper's content is a strict subset of Statistics Major: `Sx1`-`x3`,
`SR1`-`R18`, `Sb1`-`b16` and `SH1`-`H4` (41 statements). Verdicts are
identical to the Y422 rows for the same codes.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `SR6` | Expectation of a linear combination | As Y422 | MISSING |
| `R17`, `R18` | Geometric distribution probabilities, mean and variance | As Y422 | MISSING |
| `b2` | Scatter diagram | As Y422 | MISSING |
| `Sb6` | Hypothesis test for correlation using the pmcc | As Y422 | MISSING |
| `b9` | Hypothesis test using Spearman's rs | As Y422 | MISSING |
| `b15` | Relationship between the two regression lines | As Y422 | MISSING |
| `Sb16` | Interpret bivariate categorical data | As Y422 | MISSING |
| `SH1` | Chi-squared test for association (contingency table) | As Y422 | MISSING |
| `R4`, `R5` | E(a+bX) and Var(a+bX) | As Y422 | PARTIAL |
| `R7`, `R8`, `R9` | Discrete uniform distribution | As Y422 | PARTIAL |
| `R12`, `R14` | Poisson approximation to binomial; Poisson mean and variance | As Y422 | PARTIAL |
| `b12`, `b13`, `b14` | Residuals; both regression lines; goodness of fit | As Y422 | PARTIAL |
| `H2`, `H3`, `H4` | Chi-squared goodness of fit and interpretation | As Y422 | PARTIAL |
| `SR1`, `R2`, `R3` | Probability functions; expectation; variance | `fmstat.t_drv` | COVERED |
| `R13` | Poisson probabilities | `fmstat.t_pois` | COVERED |
| `b4` | pmcc from raw data | `fmstat.t_pmcc` | COVERED |
| `Sb8` | Spearman's rank correlation coefficient | `fmstat.t_spear` | COVERED |
| `Sb11` | Least squares regression line | `fmstat.t_reg` | COVERED |
| `Sx1`, `x2`, `x3` | Sampling explanations | - | N/A |
| `R10`, `SR11`, `R15`, `SR16` | Recognising distributions; sum of Poissons | - | N/A |
| `Sb1`, `b3`, `b5`, `b7`, `b10` | Bivariate terminology and judgement | - | N/A |

---

## H645 Modelling with Algorithms (Y433) - minor option

Toolkit module in scope: `algos.py`.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `A7` | Know and be able to use the quick sort algorithm | `algos.py` implements bubble and insertion sort. Quick sort - the algorithm the specification actually names - is absent | MISSING |
| `A11` | Count the comparisons needed by first fit and first fit decreasing | The bin-packing tools report bins used and their contents but no comparison count | MISSING |
| `N7` | Know the order (complexity) of Kruskal's, Prim's and Dijkstra's algorithms | Not reported anywhere | MISSING |
| `N10` | Use a network to model a transmission problem; sources and sinks | No flow model at all | MISSING |
| `N11` | Specify a cut and calculate its capacity | Nothing | MISSING |
| `N12` | Understand and use the maximum flow / minimum cut theorem; flow augmentation | Nothing | MISSING |
| `N13` | Explore network algorithms via LP formulations | Nothing | MISSING |
| `L3` | Recognise when an LP is in standard form | No LP support of any kind | MISSING |
| `L4` | Use slack variables to convert an LP to slack form | Nothing | MISSING |
| `L5` | Recognise when an LP requires an integer solution | Nothing | MISSING |
| `L6` | Formulate a range of network problems as LPs | Nothing | MISSING |
| `L7` | Graph inequalities in 2-D and identify the feasible region | Nothing; there is no inequality plotting anywhere in the toolkit | MISSING |
| `L8` | Solve a 2-D LP graphically | Nothing | MISSING |
| `L9` | Consider the effect of modifying an LP (post-optimal analysis) | Nothing | MISSING |
| `L10` | Solve 2-D integer LP problems | Nothing | MISSING |
| `L11` | Use a visualisation of a 3-D LP | Nothing | MISSING |
| `L12` | Use the simplex algorithm on an LP in standard form | Nothing - no tableau, no pivoting | MISSING |
| `L13` | Understand the geometric basis of the simplex algorithm | Nothing to interpret | MISSING |
| `L14` | Handle >= constraints (two-stage simplex / big-M) | Nothing | MISSING |
| `L15` | Reformulate an equality constraint as a pair of inequalities | Nothing | MISSING |
| `L16` | Handle variables which may be negative | Nothing | MISSING |
| `A4` | Basic ideas of algorithmic complexity; worst case; size of problem | `insertion` reports comparisons and `bubble` reports swaps, but nothing relates these to problem size or reports an order | PARTIAL |
| `A8` | Count the comparisons and/or swaps used by a sorting algorithm | `bubble` counts swaps but not comparisons; `insertion` counts comparisons but not shifts; quick sort is absent | PARTIAL |
| `AN1` | Graphs and associated vocabulary; adjacency and incidence matrices | An adjacency matrix is the input format for `dijkstra`/`prim`/`kruskal`, but no degrees, order, or incidence-matrix handling is exposed | PARTIAL |
| `N3` | A network is a graph with weighted arcs; directed and undirected | The matrix input supports both, but nothing distinguishes or reports directedness | PARTIAL |
| `N6` | Model shortest path problems and solve using Dijkstra's algorithm | `algos.dijkstra` returns final distances only - no working values, no permanent-label order, and no route. Exam questions ask for the labelling and the path | PARTIAL |
| `N8` | Model precedence problems with an activity-on-arc network | `critpath` takes activities with predecessor lists (activity-on-node style) and produces ES/EF/float; it does not build or interpret an activity-on-arc diagram, and there are no dummy activities | PARTIAL |
| `N9` | Use critical path analysis and interpret the results | `critpath` gives the project duration, ES, EF, float and the critical activities, but no cascade chart, resource histogram or scheduling | PARTIAL |
| `A10` | Know and use the first fit and first fit decreasing bin-packing algorithms | `algos.firstfit`, `firstfitdec` (full bin contents shown) | COVERED |
| `N5` | Solve minimum connector problems using Kruskal's algorithm | `algos.kruskal` (with union-find) and `algos.prim`, both listing edges in order and the total weight | COVERED |
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
**spreadsheet**. Statements `NQ1` and `Q2` are explicitly about spreadsheet
use and are marked N/A on that basis, not because they are uncomputable.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `U2` | Calculate the error in f(x) when x is in error | Not implemented; `t_error` compares two given numbers only | MISSING |
| `U3` | Understand the effect on errors of changing the way a calculation is arranged | Nothing | MISSING |
| `U8` | Use error analysis to produce an improved estimate | No extrapolation of any kind (no Aitken, no Richardson) | MISSING |
| `Ne1` | Graphical interpretation of iterative methods, including staircase and cobweb diagrams | The iterates are listed but never plotted | MISSING |
| `e3` | Understand the relative computational efficiency of different root-finding methods | Nothing compares methods | MISSING |
| `e5` | Understand and apply relaxation to an iteration x(n+1) = g(x(n)) | Not implemented | MISSING |
| `c2` | Empirical and graphical understanding of the error in numerical differentiation | Nothing | MISSING |
| `c4` | Know the error behaviour of the integration rules (halving h divides the error by about 4 for trapezium/midpoint, 16 for Simpson) | `t_integ` gives one estimate for one n; there is no h-halving table, no ratio of differences, and no Simpson-from-midpoint-and-trapezium construction. This is a core Y434 technique | MISSING |
| `Nf1` | Use Newton's forward difference formula; difference tables | Not implemented | MISSING |
| `f2` | Construct the interpolating polynomial (formula given) | Not implemented | MISSING |
| `NU1` | Calculate errors in sums, differences, products and quotients | `t_error` gives absolute and relative error for a single approximation; there are no propagation rules | PARTIAL |
| `U6` | Understand rounding and chopping and their effects; maximum and average error | `t_round` rounds to k significant figures; chopping is not implemented and no error bound is produced | PARTIAL |
| `NU7` | Understand convergence and divergence, and the order of convergence, of an iterative sequence | Every iterate is listed and divergence is flagged, but there is no ratio-of-differences analysis and no statement of first- or second-order convergence | PARTIAL |
| `e2` | Solve equations to any required accuracy and justify the accuracy claimed | All three root-finders run to a fixed 1e-9 tolerance; the user cannot set a target accuracy and no error bound is reported | PARTIAL |
| `e4` | Know that fixed point iteration is generally first order; comment on failure | `t_fixed` shows the iterates and detects divergence, but does not report the order or diagnose \|g'(x)\| > 1 | PARTIAL |
| `Nc1` | Estimate a derivative using forward and central differences with a suitable sequence of h | `t_diff` gives forward and central differences for a single h (and the exact value); there is no sequence of h and no extrapolation | PARTIAL |
| `Nc3` | Evaluate a definite integral using the midpoint, trapezium and Simpson's rules | `numeric.t_integ` computes all three in one pass (and refuses Simpson for odd n) | COVERED |
| `NQ1` | Use a spreadsheet to implement numerical methods | Spreadsheet skill assessed on a computer; the calculator is not the tool | N/A |
| `Q2` | Use the iterative capability of a spreadsheet | Spreadsheet skill | N/A |
| `U4` | Understand that computers represent numbers to finite precision | Conceptual | N/A |
| `U5` | Understand the consequences of subtracting nearly equal numbers | Conceptual | N/A |

---

## H645 Extra Pure (Y435) - minor option

Toolkit module in scope: `xpure.py`, plus `matrix.py` and the CAS.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `s4` | Verify a given solution of a recurrence relation | No substitution/verification tool | MISSING |
| `s6` | Solve first order linear non-homogeneous recurrence relations u(n+1) = a u(n) + f(n) | `t_recur` handles the homogeneous constant-coefficient case only | MISSING |
| `s8` | Solve second order linear non-homogeneous recurrence relations u(n+2) = a u(n+1) + b u(n) + f(n) | No particular solution | MISSING |
| `XS1` | Language and notation of sets: subset, union, intersection, complement, empty set | No set tool at all | MISSING |
| `a5` | Understand and work with subgroups | `t_group` never enumerates subgroups | MISSING |
| `a8` | Specify an isomorphism between two groups of the same order | Nothing | MISSING |
| `m4` | Find powers of a 2x2 or 3x3 matrix using diagonalisation | No M^n; `t_eigen` stops at P and D being described in words | MISSING |
| `m5` | Understand and use the Cayley-Hamilton theorem | Nothing | MISSING |
| `c2` | Sketch contours and sections of a surface z = f(x, y) | No two-variable plotting | MISSING |
| `c4` | Use dz/dx = 0 and dz/dy = 0 to find stationary points of z = f(x, y) | Nothing; `t_partial` cannot even form dz/dy | MISSING |
| `c6` | Find grad g and evaluate it at a point | Nothing | MISSING |
| `c7` | Concepts of the tangent plane and the normal line to a surface | Nothing | MISSING |
| `s2` | Language of recurrence relations: limit, convergent, divergent, periodic | `t_recur` prints a0..a9 and the closed form, so behaviour is visible, but nothing classifies it | PARTIAL |
| `s3` | Investigate and comment on the behaviour of a recurrence relation | Terms a0..a9 only - no long-run behaviour, no limit | PARTIAL |
| `s5` | Solve first order linear homogeneous recurrence relations u(n+1) = a u(n) | Reachable by entering the second-order tool with q = 0, which produces a spurious second root at 0 | PARTIAL |
| `s9` | Investigate and comment on associated sequences and their limits | As `s3` | PARTIAL |
| `a6` | Know and use Lagrange's theorem | `t_group` prints the divisors of n and the order of every element, which is the consequence of Lagrange, but does not identify subgroups or their orders | PARTIAL |
| `Xm1` | Understand the meaning of eigenvalue and eigenvector | `xpure.t_eigen` and `matrix.t_eig` are **2x2 only**; the specification requires 3x3 work as well | PARTIAL |
| `m2` | Form and solve the characteristic equation det(M - lambda I) = 0 | 2x2 only | PARTIAL |
| `m3` | Form the matrix of eigenvectors P and the diagonal matrix D | 2x2, distinct real eigenvalues only; P and D are described but never printed as matrices | PARTIAL |
| `m6` | Understand the significance of eigenvalues and eigenvectors (invariant lines, geometric meaning) | `t_eigen` prints the eigenvectors and notes diagonalisability; there is no invariant-line output | PARTIAL |
| `c3` | Find first order partial derivatives | `t_partial` is a single-variable central difference and says so in its own output: the engine has one variable x, so dz/dy cannot be taken without manually substituting a number for the other variable | PARTIAL |
| `s7` | Solve second order linear homogeneous recurrence relations u(n+2) = a u(n+1) + b u(n) | `xpure.t_recur` (all three discriminant cases, fits A and B from a0 and a1, then lists a0..a9) | COVERED |
| `Xa1` | Understand the group axioms: closure, associativity, identity, inverses | `xpure.t_group` checks closure, two-sided identity and all inverses from a Cayley table | COVERED |
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

Toolkit module in scope: `fpt.py`, plus the CAS, `polar.py` and `diffeq.py`.

Note: Y436 is sat **with a computer**, and the specification requires access
to graphing software with a slider, a CAS, and a programming language
(section 5e). A handheld toolkit can only ever be a partial substitute for
that environment; the verdicts below judge the toolkit against the
mathematical content of each statement, not against the software requirement.

| Code | Content statement | Toolkit coverage | Verdict |
|---|---|---|---|
| `C4` | Find, describe and generalise properties of a family of curves | No parameter sweeping and no family plotting | MISSING |
| `C7` | Find and work with equations of chords, tangents and normals | Nothing forms a line equation; `Gradient at a point` gives m only | MISSING |
| `C8` | Calculate arc length using cartesian, polar and parametric forms | Not implemented (`polar.t_area` does area, not arc length) | MISSING |
| `C9` | Understand the meaning of an envelope of a family of curves | Nothing | MISSING |
| `C10` | Use the limit of an expression | No limit operation in the CAS | MISSING |
| `C11` | Determine asymptotes, including oblique asymptotes | Nothing | MISSING |
| `C12` | Identify cusps by examining the limit of the gradient | Nothing | MISSING |
| `Tc1` | Use software to produce analytical solutions of differential equations, with a slider | `diffeq.py` gives the complementary function only, with no parameter control | MISSING |
| `c2` | Use software to produce a tangent to a curve at a variable point | No dynamic tangent | MISSING |
| `c4` | Verify a given solution of a differential equation | No substitution/verification tool | MISSING |
| `c5` | Work with particular solutions and initial conditions | No DE tool applies an initial condition | MISSING |
| `c6` | Sketch a tangent field for a first order differential equation | Not implemented; this is one of the paper's signature techniques | MISSING |
| `c9` | Understand the concepts underlying Runge-Kutta methods | Nothing | MISSING |
| `c10` | Solve first order differential equations using Runge-Kutta methods (formulae given) | Only Euler exists (`fpt.t_euler`, `numeric.t_euler`); no RK2 or RK4 | MISSING |
| `T6` | Know and use Euler's totient function phi(n) | Not implemented; `fpt.py` has gcd, lcm, primality, factorisation, powmod and modular inverse but no totient | MISSING |
| `T8` | Find Pythagorean triples and use them | Not implemented | MISSING |
| `T9` | Solve Pell's equation x^2 - n y^2 = 1 | Not implemented | MISSING |
| `T10` | Solve other Diophantine equations | Not implemented | MISSING |
| `TC1` | Plot a family of curves in graphing software | `fpt.t_plot` plots one f(x) over a chosen x range; there is no parameter, no slider and no overlay of several curves | PARTIAL |
| `C6` | Find the gradient of the tangent to a curve given in cartesian, polar or parametric form | CAS `Gradient at a point` is cartesian only | PARTIAL |
| `c8` | Understand that a smaller step length usually improves accuracy | Euler can be rerun with a different h, but nothing tabulates or compares the results | PARTIAL |
| `T5` | Know and use Fermat's little theorem | `fpt.t_powmod` computes a^(p-1) mod p, so the theorem can be checked by hand, but there is no tool for it | PARTIAL |
| `T7` | Know and use Wilson's theorem, (p-1)! = -1 (mod p) | `casutil.fact` (capped at 500) and `t_powmod` exist separately; nothing computes (p-1)! mod p, and the factorial cap bites for p > 501 | PARTIAL |
| `C2` | Use CAS to work with equations of curves: solve equations, evaluate derivatives and integrals | The whole `Calculus & Algebra` section: Differentiate, Integrate, Definite integral, Simplify, Solve, Evaluate, Graph, Table | COVERED |
| `C5` | Convert equations between cartesian and polar form | `polar.t_topolar_xy`, `t_topolar_rt`; `polar.t_plot` for r(theta) | COVERED |
| `c7` | Solve a first order differential equation numerically by Euler's method | `fpt.t_euler` and `numeric.t_euler` (both support f(x, y)) | COVERED |
| `T3` | Know and use the unique prime factorisation theorem | `fpt.t_factor` (trial division to 1e8) and `t_prime` | COVERED |
| `T4` | Solve problems using modular arithmetic | `fpt.t_powmod`, `t_modinv`, `t_gcdlcm`, `t_base`; also `xpure.t_mod` | COVERED |
| `C3` | Vocabulary associated with curves: asymptote, cusp, loop, bounded | Terminology only | N/A |
| `c3` | Construct, adapt or interpret a differential equation model | Modelling judgement | N/A |
| `TT1` | Write, adapt and interpret short programs | Programming skill assessed on a computer | N/A |
| `T2` | Identify the limitations of a short program | Discussion | N/A |

---

## Summary counts

Per component. The two Minor papers are shown with their true statement counts
(their content is a strict subset of the corresponding Major paper, so the
audit tables above group them; the counts here are per statement).

| Component | Statements | MISSING | PARTIAL | COVERED | N/A |
|---|---:|---:|---:|---:|---:|
| H640 Pure Mathematics | 154 | 34 | 39 | 56 | 25 |
| H640 Statistics | 54 | 9 | 10 | 22 | 13 |
| H640 Mechanics | 45 | 6 | 9 | 15 | 15 |
| **H640 total** | **253** | **49** | **58** | **93** | **53** |
| H645 Core Pure (Y420) | 99 | 13 | 26 | 44 | 16 |
| H645 Mechanics Major (Y421) | 89 | 27 | 20 | 28 | 14 |
| H645 Statistics Major (Y422) | 72 | 21 | 18 | 12 | 21 |
| H645 Mechanics Minor (Y431) | 49 | 7 | 12 | 21 | 9 |
| H645 Statistics Minor (Y432) | 41 | 9 | 13 | 7 | 12 |
| H645 Modelling with Algorithms (Y433) | 42 | 21 | 7 | 2 | 12 |
| H645 Numerical Methods (Y434) | 21 | 10 | 6 | 1 | 4 |
| H645 Extra Pure (Y435) | 32 | 12 | 10 | 5 | 5 |
| H645 Further Pure with Technology (Y436) | 32 | 18 | 5 | 5 | 4 |
| **H645 total** | **477** | **138** | **117** | **125** | **97** |
| **Grand total** | **730** | **187** | **175** | **218** | **150** |

Because the Minor papers duplicate Major content, the number of **distinct**
MISSING statements is **171** (187 minus the 7 Y431 and 9 Y432 duplicates).

Percentages of the assessable (non-N/A) statements:

| Component | Assessable | COVERED | PARTIAL | MISSING |
|---|---:|---:|---:|---:|
| H640 (all three areas) | 200 | 47% | 29% | 24% |
| H645 Core Pure (Y420) | 83 | 53% | 31% | 16% |
| H645 Mechanics Major (Y421) | 75 | 37% | 27% | 36% |
| H645 Statistics Major (Y422) | 51 | 24% | 35% | 41% |
| H645 Modelling with Algorithms (Y433) | 30 | 7% | 23% | 70% |
| H645 Numerical Methods (Y434) | 17 | 6% | 35% | 59% |
| H645 Extra Pure (Y435) | 27 | 19% | 37% | 44% |
| H645 Further Pure with Technology (Y436) | 28 | 18% | 18% | 64% |

The shape of the result: H640 and Core Pure are in reasonable health; the
Modelling with Algorithms, Numerical Methods and Further Pure with Technology
options are largely unserved, and Statistics Major is missing two whole topics
(continuous random variables, and correlation/association hypothesis testing).

---

## The MISSING list, ranked

All 171 distinct MISSING statements, ordered by my judgement of how many exam
marks are at stake. The ordering weighs three things: how many candidates meet
the topic (everyone sits H640; every Further Maths candidate sits Core Pure;
option papers are each 1/4 of H645), how many marks the topic typically
carries, and how completely a calculator tool would convert to marks (a
sine-rule solver hands over the answer; a "sketch the tangent field" tool only
assists).

### Tier 1 - highest value

1. **H640 `t4`** Sine rule and cosine rule - appears in essentially every H640 pure paper, 4-8 marks, and a triangle solver is the cheapest tool in this whole list to write.
2. **H640 `Mt16`** Compound angle identities sin(A+-B), cos(A+-B), tan(A+-B) - recurring 6+ mark questions, and they gate R-form, proof and equation solving.
3. **H640 `t17`** Double angle identities - same frequency as `Mt16`, and additionally gate the integration of sin^2/cos^2 and half-angle substitutions.
4. **H640 `c16`** Implicit differentiation - a 5-7 mark question in almost every series, and there is currently no route to it at all.
5. **H640 `c32`** Solve first order differential equations by separating variables - a standard 6-8 mark question; the toolkit can integrate but has no DE path for H640.
6. **H640 `t13`** sec, cosec and cot - not merely absent: `sec(x)` silently parses as `s*e*c*x`, so the toolkit currently returns confidently wrong answers. Correctness risk on top of mark loss.
7. **Y420 `c14`** Particular integrals - without them `diffeq.t_second_order` can never finish a general solution; the 2nd-order DE question is typically 8-12 marks and is on every Core Pure paper.
8. **H640 `a15`** Partial fractions - 4-5 marks in its own right, and the gateway to `c30`, `Ps2` and much of rational integration.
9. **Y420 `j11`** Loci and regions on an Argand diagram - a recurring 6-10 mark Core Pure question; the toolkit plots isolated points only.
10. **H640 `y3`** Find the initial velocity of a projectile - the projectile question is on H640/01 most years and the "find u and the angle" direction is the common one; `mech640.projectile` runs only forwards.
11. **H640 `t11`** Arc length and sector area - recurring 3-5 marks, and among the easiest possible tools to add.
12. **Y433 `L12`** The simplex algorithm - the single largest unserved block anywhere: with `L3`-`L16` it is roughly a third of Modelling with Algorithms.
13. **Y433 `L8`** Solve a 2-D LP graphically - paired with `L7`; typically 8-12 marks of Y433 and a natural fit for the plotting code that already exists.
14. **Y420 `c2`** Volumes of revolution - a recurring standalone Core Pure question worth 6-8 marks; `defint` already provides the numeric machinery.
15. **Y422 `SR19`** Use a simple continuous random variable as a model - the head of an entire missing topic (`SR19`-`R26`) that carries perhaps 20+ marks of Statistics Major.

### Tier 2 - high value

16. **H640 `Ma7`** Solve linear inequalities - recurring, and the base for `a8`/`a9`, which are currently only half-served.
17. **H640 `t19`** Use trigonometric identities to solve equations - the payoff topic for items 2 and 3; multi-mark.
18. **Y420 `Ps2`** Sum a series using partial fractions (method of differences) - a recurring 5-8 mark Core Pure question.
19. **Y420 `Pm6`** Invariant points and invariant lines - a recurring 5-8 mark matrices question.
20. **Y433 `L7`** Graph inequalities in 2-D and identify the feasible region - the drawing half of the graphical LP question.
21. **H640 `c21`** Find the constant of integration from a given point - small in itself but attached to almost every integration question.
22. **Y420 `Pv14`** Intersection of a line and a plane - a standard Core Pure vectors mark-earner.
23. **Y420 `v9`** Form the equation of a line in vector and cartesian form - the toolkit consumes lines but cannot build one; needed before most of the vectors topic.
24. **H640 `Mf1`** Polynomial arithmetic (expand, collect, divide) - low marks directly, but it underpins factorising, curve sketching and partial fractions.
25. **H640 `MD1`** Statistical diagrams: histogram, box plot, cumulative frequency, stem-and-leaf - a large slice of H640/02 that the toolkit does not touch at all.
26. **Y422 `SH1`** Chi-squared test for association in a contingency table - a full hypothesis-test question in Statistics Major; `t_chi` cannot do the contingency case.
27. **Y422 `Sb6`** Hypothesis test for correlation using the pmcc - the toolkit computes r but stops one step short of the marks.
28. **Y422 `b9`** Hypothesis test using Spearman's rs - same pattern as 27.
29. **Y434 `c4`** Error behaviour of the integration rules (ratio of differences, Simpson from midpoint and trapezium) - a core Numerical Methods technique that appears on every paper.
30. **Y436 `c10`** Runge-Kutta methods for first order differential equations - a signature Y436 technique; only Euler exists.

### Tier 3 - substantial

31. **Y421 `Mi13`** Oblique impact and its modelling assumptions - the head of the `Mi13`-`i17` block, a full Mechanics Major question.
32. **Y421 `i14`** Newton's Experimental Law for oblique impact.
33. **Y421 `i15`** Oblique impact between a sphere and a surface.
34. **Y421 `i16`** Oblique impact between two spheres.
35. **Y421 `i17`** Loss of kinetic energy in an oblique impact.
36. **Y422 `R20`** The meaning of a pdf, including piecewise pdfs - part of the missing continuous-rv topic.
37. **Y422 `R24`** Cumulative distribution function - same topic.
38. **Y422 `R26`** Use a cdf to find the median and quartiles - same topic, and directly examinable.
39. **Y422 `R23`** Mode and median of a continuous random variable - same topic.
40. **Y422 `R21`** Properties of a pdf - same topic.
41. **Y422 `R29`** Linear combinations of independent Normal random variables - a standard multi-mark question.
42. **Y433 `N12`** Maximum flow / minimum cut theorem - the head of the network-flow block, a full Y433 question.
43. **Y433 `N10`** Model a transmission problem as a network with sources and sinks.
44. **Y433 `N11`** Specify a cut and calculate its capacity.
45. **Y433 `A7`** Quick sort - the specification names it explicitly and the module implements two other sorts instead.
46. **Y420 `Pc1`** Improper integrals - a recognisable Core Pure question type.
47. **Y420 `c8`** Recognise separable differential equations - pairs with H640 `c32`.
48. **Y420 `j13`** Use de Moivre to derive trigonometric identities - a recurring Core Pure question.
49. **Y421 `v6`** Range of a projectile on an inclined plane - a standard Mechanics Major question.
50. **Y421 `v7`** Maximum range of a projectile.
51. **Y421 `MG6`** Volume generated by rotating a region - shared machinery with item 14.
52. **Y421 `G7`** Centre of mass of a solid of revolution by calculus.
53. **Y421 `G9`** Centre of mass of a lamina or arc by calculus.
54. **Y421 `d16`** Sliding versus toppling - a classic Mechanics Major discriminator.
55. **Y421 `G5`** Centre of mass in equilibrium and toppling problems.
56. **Y421 `G10`** Centre of mass in rigid-body equilibrium.
57. **Y435 `m4`** Powers of a matrix by diagonalisation - the payoff of the whole Extra Pure eigenvalue topic.
58. **Y435 `c4`** Stationary points of z = f(x, y) - the payoff of the multivariable calculus topic.
59. **Y435 `s6`** First order non-homogeneous recurrence relations.
60. **Y435 `s8`** Second order non-homogeneous recurrence relations.
61. **Y434 `Nf1`** Newton's forward difference formula and difference tables - a whole Y434 topic.
62. **Y434 `f2`** Construct the interpolating polynomial - the other half of that topic.
63. **Y434 `U8`** Error analysis to produce an improved estimate (extrapolation) - a recurring Y434 technique.
64. **Y434 `e5`** Relaxation applied to a fixed point iteration - directly named in the specification.
65. **Y436 `c6`** Sketch a tangent field for a first order differential equation - a signature Y436 task.
66. **Y436 `c9`** Concepts underlying Runge-Kutta - pairs with item 30.
67. **Y436 `C8`** Arc length in cartesian, polar and parametric form.
68. **Y436 `T9`** Pell's equation - explicitly named, and mechanical to implement.
69. **Y436 `T6`** Euler's totient function - explicitly named, trivial to implement given the existing factoriser.
70. **Y436 `T8`** Pythagorean triples - explicitly named.

### Tier 4 - moderate

71. **H640 `c28`** Integration by substitution in non-obvious cases - the tested failure on `x e^(x^2)` is a common exam integrand.
72. **H640 `c18`** Points of inflection.
73. **H640 `g9`** Intersection of a line and a circle - a standard coordinate geometry question.
74. **H640 `g11`** Circle properties (semicircle, chord, tangent).
75. **H640 `f5`** Inverse functions and their graphs.
76. **H640 `f4`** Composite functions.
77. **H640 `f7`** Inequalities involving the modulus function.
78. **H640 `a10`** Manipulate surds.
79. **H640 `a11`** Rationalise the denominator.
80. **H640 `a16`** Simplify rational expressions.
81. **H640 `E7`** Reduce y = a x^n and y = a b^x to linear form by taking logs - the log-linear regression question in H640/02.
82. **H640 `t3`** Area of a triangle = 1/2 ab sin C - pairs with item 1 and costs almost nothing to add.
83. **H640 `t12`** Small angle approximations.
84. **H640 `t14`** Graphs of the reciprocal and inverse trigonometric functions.
85. **H640 `t15`** tan^2 + 1 = sec^2 and cot^2 + 1 = cosec^2 - blocked behind item 6.
86. **H640 `g13`** Convert between cartesian and parametric forms.
87. **H640 `g14`** Circle in parametric form.
88. **H640 `s7`** Generate a sequence from a kth-term formula or a recurrence.
89. **H640 `s10`** Recognise increasing, decreasing and periodic sequences.
90. **H640 `a9`** Express solutions of inequalities in set notation - blocked behind item 16.
91. **H640 `a14`** Proportional relationships.
92. **H640 `*`** (Algebra) Change the subject of a formula.
93. **H640 `k4`** Draw and interpret kinematics graphs - recurring in H640/01, and area-under-graph is directly worth marks.
94. **H640 `y4`** Eliminate time to get the path equation of a projectile.
95. **H640 `k11`** Cartesian equation of the path of a particle.
96. **H640 `Mk9`** 2-D kinematics language and relative position.
97. **H640 `F8`** Closed polygon of forces.
98. **H640 `D2`** Histogram area and frequency density.
99. **H640 `D3`** Interpret a cumulative frequency diagram.
100. **H640 `u5`** Venn diagrams for up to three events - a very common H640/02 question format.
101. **H640 `*`** (Probability) Tree and sample space diagrams.
102. **H640 `D4`** Describe frequency distributions and skew.
103. **H640 `D7`** Recognise an outlier on a scatter diagram.
104. **H640 `p24`** Sampling techniques - would need a random number source.
105. **H640 `D14`** Data cleaning.
106. **Y420 `Pp4`** Proof by induction for sequences, series and matrix powers - high marks, but the marks are for the written argument; a tool could only supply M^n and the numerical check.
107. **Y420 `Pp5`** Proof by induction generally - same caveat.
108. **Y420 `c18`** Coupled first order simultaneous differential equations.
109. **Y421 `h7`** Energy principles with elastic strings (maximum extension).
110. **Y421 `h5`** Equilibrium position of a mass on a spring.
111. **Y421 `r6`** Tangential acceleration.
112. **Y421 `d9`** Triangle of forces.
113. **Y421 `d13`** Couples.
114. **Y421 `G3`** Centres of mass of standard uniform bodies - a reference table would do it.
115. **Y421 `Mv3`** Eliminate a parameter from parametric equations.
116. **Y421 `v5`** Cartesian equation of a projectile path.
117. **Y421 `v4`** Interpret the resulting equation (bounding parabola).
118. **Y421 `v9`** Verify a solution of a differential equation of motion.
119. **Y421 `v10`** Apply boundary or initial conditions.
120. **Y421 `Mk1`** 2-D kinematics language and relative position.
121. **Y421 `q3`** Determine units from dimensions.
122. **Y421 `q4`** Change units.
123. **Y422 `R17`** Geometric distribution probabilities - a named distribution with nothing implemented.
124. **Y422 `R18`** Mean and variance of a geometric distribution.
125. **Y422 `SH5`** Wilcoxon signed rank test - a named test with nothing implemented, and it needs its own critical-value table.
126. **Y422 `I11`** Confidence interval for a paired mean difference.
127. **Y422 `R27`** Mean of a linear combination of random variables.
128. **Y422 `SR6`** Expectation of a linear combination.
129. **Y422 `b15`** Relationship between the two regression lines.
130. **Y422 `b2`** Scatter diagram.
131. **Y422 `R31`** Normal probability plot.
132. **Y422 `Sb16`** Interpret bivariate categorical data.
133. **Y422 `Z2`** Simulation - needs a random number generator, which the toolkit lacks entirely.
134. **Y433 `L4`** Slack variables.
135. **Y433 `L14`** Two-stage simplex / big-M for >= constraints.
136. **Y433 `L10`** Integer LP in two dimensions.
137. **Y433 `L13`** Geometric basis of the simplex algorithm.
138. **Y433 `L3`** Recognise standard form.
139. **Y433 `L5`** Recognise when an integer solution is required.
140. **Y433 `L6`** Formulate network problems as LPs.
141. **Y433 `L9`** Post-optimal analysis.
142. **Y433 `L11`** 3-D LP visualisation.
143. **Y433 `L15`** Reformulate an equality constraint.
144. **Y433 `L16`** Variables that may be negative.
145. **Y433 `N13`** Explore network algorithms via LP.
146. **Y433 `N7`** Order of Kruskal, Prim and Dijkstra.
147. **Y433 `A11`** Count comparisons in bin packing.
148. **Y434 `Ne1`** Staircase and cobweb diagrams - directly examinable and the plotting primitives already exist.
149. **Y434 `U2`** Error in f(x) when x is in error.
150. **Y434 `U3`** Effect of rearranging a calculation on the error.
151. **Y434 `e3`** Relative computational efficiency of root-finding methods.
152. **Y434 `c2`** Error in numerical differentiation.
153. **Y435 `a5`** Subgroups - the natural next step for `t_group`, which already has the Cayley table.
154. **Y435 `m5`** Cayley-Hamilton theorem.
155. **Y435 `c6`** grad g at a point.
156. **Y435 `c7`** Tangent plane and normal line.
157. **Y435 `c2`** Contours and sections of a surface.
158. **Y435 `a8`** Isomorphism between two groups.
159. **Y435 `s4`** Verify a given solution of a recurrence relation.
160. **Y435 `XS1`** Set notation - low marks, but currently nothing at all.
161. **Y436 `C11`** Determine asymptotes, including oblique.
162. **Y436 `C7`** Equations of chords, tangents and normals.
163. **Y436 `C10`** Limits.
164. **Y436 `C12`** Identify cusps from the limit of the gradient.
165. **Y436 `C4`** Generalise properties of a family of curves.
166. **Y436 `C9`** Envelope of a family of curves.
167. **Y436 `Tc1`** Analytical solutions of differential equations with a parameter slider.
168. **Y436 `c5`** Particular solutions and initial conditions for a differential equation.
169. **Y436 `c4`** Verify a given solution of a differential equation.
170. **Y436 `c2`** Dynamic tangent at a variable point.
171. **Y436 `T10`** Other Diophantine equations - open-ended, so a general tool is unlikely to convert to marks.

### A note on the PARTIALs

Several `PARTIAL` verdicts are worth more marks than most of the tail of this
list, because they sit one small step away from a complete answer:

- `Y420 c10` - `diffeq.t_first_order` finds the integrating factor and then
  stops. Performing `int (IF * Q) dx` and applying an initial condition would
  finish an 8-10 mark Core Pure question.
- `Y420 c13` / `Pc15` - the complementary function is produced but the general
  solution never is (see MISSING item 7), and SHM constants are never fitted.
- `H640 t7` - the trig equation solver is locked to 0-360 degrees and to bare
  `sin x = k` forms; arbitrary intervals, radians and multiple angles would
  convert directly into marks.
- `H640 c7` - nothing solves `f'(x) = 0`, so stationary points, the single most
  frequent calculus question type, need three manual steps.
- `Y433 N6` - Dijkstra returns final distances but not the labelling or the
  route, which is what the mark scheme asks for.
- `Y422 H3` - the chi-squared statistic is computed with `df = cells - 1`
  always, which is silently wrong whenever parameters have been estimated.
- `Y435 Xm1`/`m2`/`m3` - eigenvalues are 2x2 only; Extra Pure requires 3x3.
- `Y420 m4` - the transformation builder is 2-D only; the specification names
  specific 3-D reflections and rotations.








