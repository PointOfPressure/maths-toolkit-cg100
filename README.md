# Maths Toolkit for the Casio fx-CG100

A calculator app in stock MicroPython 1.9.4 using the built-in `casioplot`.
Three parts: an expression calculator, a computer algebra system, and 263 tools
mapped to OCR B (MEI) A-Level Maths (H640) and Further Maths (H645).

![tests](https://img.shields.io/badge/tests-6752%20checks%2C%200%20failures-brightgreen)
![smoke](https://img.shields.io/badge/smoke-443%20checks%2C%200%20errors-brightgreen)
![runtime](https://img.shields.io/badge/MicroPython-1.9.4-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

## Install

Copy to the root of the calculator's storage:

- `maths.py`, `casui.py`, `casutil.py`
- `caslex.py`, `caseng.py`, `casrender.py`, `cascalc.py`, `caspoly.py`
- `pure640.py`, `purecalc.py`, `stat640.py`, `mech640.py`, `proof.py`,
  `vcplx.py`, `matrix.py`, `vectors.py`, `polyroots.py`, `series.py`,
  `hyper.py`, `polar.py`, `diffeq.py`, `fmmech.py`, `fmstat.py`,
  `numeric.py`, `algos.py`, `xpure.py`, `fpt.py`

Do not copy `casioplot.py`. It is a PC stub; the calculator has the real module
built in and the stub would shadow it. Also skip tests.py, stress.py,
devlint.py and casioshot.py, which are desktop-only.

Run `maths.py`.

## Keys

| Menu | |
| --- | --- |
| up / down | move, wraps |
| 1-9 | jump to entry |
| page up / down | move seven |
| first / last | `\|<-` and `->\|` |
| OK, EXE | choose |
| back | up one level; leaves the app at the top |

| Expression entry | |
| --- | --- |
| left / right | move caret |
| start / end of line | `\|<-` and `->\|` |
| up | recall last entry |
| down | clear |
| DEL | delete back |
| back | clear; again on an empty line cancels |
| ALPHA | letters a-z |
| SHIFT | `sin^-1`, `cos^-1`, `tan^-1`, `ln`, `log`, `pi`, `=`, log to a base |
| CATALOG | `!`, `abs(`, `nCr(`, `nPr(`, `sec(`, `cosec(`, `cot(`, the hyperbolics and their inverses, `sech(`, `cosech(`, `coth(`, `logb(`, `pi`, `ans`, `,` |

## Settings

Both are on the home menu and last for the session; the calculator cannot write
files.

**Angle mode: DEGREES / RADIANS.** Applies to all trig.

**Working: SHOWN / HIDDEN.** Output lines are one of three kinds. Answers always
show. Working shows only in SHOWN. Caveats always show, in both modes: warnings,
domain restrictions, verification results, statements that a tool did not
finish. 1213 lines are marked working, 640 caveat. `tests.py` asserts for all
263 tools that HIDDEN output is a subset of SHOWN and never empty.

## Modes

**Calculate.** Type an expression, see a 2D preview, press OK. `ans` holds the
last result. Exact fractions are shown under the decimal. Non-finite results
report "undefined" or "overflow".

**Calculus & Algebra.** Enter `f(x)` once, then apply operations without
retyping: differentiate, integrate, simplify, expand, factorise, collect,
partial fractions, solve, definite integral, evaluate, table, graph. The first
seven are symbolic; the rest are numeric and use the angle mode.

**A-Level Maths** and **Further Maths** hold the section tools below.

## Tools

### A-Level Maths

| Section | n | Tools |
| --- | --- | --- |
| Pure: algebra & trig | 16 | Quadratic solver, Simultaneous eqns, Arithmetic seq/sum, Geometric seq/sum, Binomial expansion, Logarithms, Coord geometry, Circle, Trig tools, Solve a triangle, Arc length & sector, Inequalities, Surds & rationalising, Line meets circle, Sequences & behaviour, Proportion k x, k/x |
| Pure: functions & calculus | 17 | Composite fg(x), Inverse function, Domain & range, Modulus \|f(x)\|, Graph transformations, Parametric d/dx, Parametric -> Cartesian, Implicit d/dx, Integration by substitution, Separation of variables, Stationary points, Constant of integration, Volume of revolution, Mean value of f, Improper integral, Small-angle approx, Exact trig values |
| Statistics | 21 | Summary stats, Freq table mean/var, Discrete RV E,Var, Binomial B(n,p), Normal P(a<X<b), Inverse Normal, HT binomial prop, HT Normal mean z, PMCC + regression, Probability rules, Tree diagram + Bayes, Sampling methods, Stratified sample, Factorial / nCr, Box plot, Histogram, Cumulative freq, Scatter + regression, Venn diagram, Reduce to linear form, Distribution shape |
| Mechanics | 15 | SUVAT solver, Projectiles, Resultant of forces, Resolve a force, Equilibrium check, Newton II F=ma, Friction F=mu R, Friction horiz plane, Friction incline, Pulley (connected), Moments / reactions, Projectile: find the launch, Variable acceleration, Distance vs displacement, Connected particles |
| Proof | 5 | Induction: a sum, Induction: divisibility, Induction: M^n, Disprove by counterexample, Proof methods reference |

### Further Maths core

| Section | n | Tools |
| --- | --- | --- |
| Complex numbers | 10 | Arithmetic z, w, Modulus & argument, Polar / exp form, From polar (r,theta), Power z^n (De Moivre), nth roots of z, Quadratic complex roots, Argand plot, Loci in the Argand plane, de Moivre identities |
| Matrices | 15 | Enter A, Enter B, Show A and B, A + B, A - B, k * A, A * B, Transpose A, Determinant A, Inverse A, Solve A x = b, Eigenvalues 2x2, 2D transform builder, 3D transform builder, Invariant points/lines |
| Vectors & 3-D | 13 | Magnitude \|a\|, Dot product a.b, Angle between, Cross product a x b, Unit vector, Scalar projection, Parallel / perp test, Point to line dist, Equation of a line, Line meets plane, Point to plane dist, Angle between planes, Skew lines distance |
| Roots of polynomials | 6 | Vieta quadratic, Vieta cubic, Vieta quartic, Quadratic roots, Numeric roots (x), Shift roots by k |
| Series & Maclaurin | 7 | Sum of r, Sum of r^2, Sum of r^3, Maclaurin of f(x), Approx + error, Method of differences, Reference card |
| Hyperbolic functions | 8 | Evaluate sinh, Evaluate cosh, Evaluate tanh, All three at x, arsinh (inverse), arcosh (inverse), artanh (inverse), Reference card |
| Polar coordinates | 5 | (r,theta) -> (x,y), (x,y) -> (r,theta), Plot polar curve, Preset curves, Polar area |
| Differential equations | 6 | First-order linear (IF), Second-order const-coeff, Particular integral, Coupled dx/dt, dy/dt, SHM recogniser, Damping classifier |

### Further Maths options

| Section | n | Tools |
| --- | --- | --- |
| Mechanics (FM) | 19 | Momentum & impulse, Restitution, Oblique impact: wall, Oblique impact: spheres, Work/Energy/Power, Projectile path (cartesian), Projectile on an incline, Circular motion, Hookes law / EPE, Elastic equilibrium/energy, Centre of mass, COM by calculus, COM standard bodies, Slide or topple, Couple, Triangle of forces, Relative motion 2-D, Dimensional analysis, Units & conversion |
| Statistics (FM) | 25 | Discrete RV E/Var, Discrete uniform, Poisson pmf/cdf, Binomial pmf/cdf, Geometric dist, Continuous RV E/Var, cdf, median, quartiles, Mode of a pdf, Piecewise pdf, Normal P(a<X<b), Standardise z, Inverse Normal, aX+bY+c combination, nX vs X1+..+Xn, Normal prob plot, PMCC r + test, Spearman rs + test, Regression y=a+bx, Chi-squared GOF, Chi-sq association, CI for mean (z), t interval / paired, CI for proportion, z-test for mean, Simulation |
| Numerical Methods | 20 | Newton-Raphson, Fixed-point iteration, Fixed-point diagnosis, Relaxation iteration, Cobweb / staircase, Order of convergence, Bisection, Integration (trap/mid/Simp), Integration error table, Richardson extrapolation, Aitken acceleration, Numerical derivative, Derivative error table, Newton forward differences, Euler method, Error abs/relative, Error propagation, Error in f(x), Round to s.f., Chop vs round |
| Modelling w/ Algorithms | 15 | Bubble sort, Insertion sort, Quick sort, Bin: first-fit, Bin: first-fit decr, Graph: degrees/incidence, Dijkstra shortest, Prim MST, Kruskal MST, Max flow / min cut, Cut capacity, Critical path, Simplex (max, <=), Simplex 2-stage (>=, =), LP graph 2-D |
| Extra Pure | 16 | Recurrence relation, Recurrence 1st order, Recurrence 2nd order, Verify a recurrence, Recurrence behaviour, Sets and notation, Group theory, Subgroups & Lagrange, Group isomorphism, 2x2 Eigen/diag, Modular arithmetic, Partial derivatives, Surface stationary pts, Tangent plane / normal, Contours & sections, 3x3 Eigen/diag |
| Further Pure w/ Tech | 24 | Plot f(x) curve, De Moivre z^n, nth roots of z, Euler dy/dx=f(x), Runge-Kutta RK2/RK4, Tangent field, Verify a DE solution, Limit of f(x), Asymptotes incl oblique, Stationary pts & cusps, Family of curves, Envelope of a family, Arc length, gcd & lcm, Prime test, Prime factorise, Euler totient phi(n), a^b mod m, Modular inverse, Fermat & Wilson, Pythagorean triples, Pell x^2-n y^2=1, Linear Diophantine, Base -> bin/hex |

## Device facts

Measured on hardware with `hwcheck.py`, 2026-08-09.

| | |
| --- | --- |
| Recursion ceiling | 92 frames. `tests.py` caps at 38 as a margin. |
| `getkey()` idle | `None`, not 0, over 400 samples. `casui.readkey` treats anything outside `KEYCODES` as idle. |
| Screen | 384 x 192 |
| `math` members | 24 of 43 present. `atan2` yes; `factorial`, `asinh`, `acosh`, `atanh`, `log2`, `trunc`, `degrees`, `radians`, `isnan`, `isinf`, `isfinite`, `copysign` no. `devlint.MATH_OK` is pinned to the measured set. |
| Section modules | All 19 fit in RAM at once. `casui` still loads on demand. |
| Key codes | `row*10 + col`, 48 readable. `[ON]` and `[AC]` have no code. |
| `getkey()` cost | About 0 ms held, 8.3 ms idle ([TI-Planet](https://tiplanet.org/forum/viewtopic.php?t=27228)). Polling loops need no delay. |

Source: fx-CG100/fx-1AU GRAPH Software User's Guide v2.10, pages 141-143.

Screen layout is checked by `casioshot.py`, which renders any screen to PNG on
a PC using the toolkit's own `char_w` metric and flags overruns of the 384 px
width. It draws with a desktop font at matched advances, so it catches
overflow, not letterforms.

## Constraints

Stock MicroPython 1.9.4. No f-strings, walrus, type annotations, async or
`yield from`. ASCII only. Only `math`, `random` and `casioplot` are importable.
No file writes. Recursion is on expression nesting, never input length.
`devlint.py` enforces all of this.

## Structure

| File | |
| --- | --- |
| `maths.py` | launcher |
| `casui.py` | keys, menus, input editor, result screens, settings |
| `casrender.py` | 2D typesetter; owns the font metric |
| `caslex.py` | tokeniser and iterative parser |
| `caseng.py` | simplify, differentiate, evaluate, print |
| `cascalc.py` | integrate, solve, definite integral |
| `caspoly.py` | exact rational polynomial algebra |
| `casutil.py` | shared prompts, formatting, charts |
| 19 section modules | `TOOLS` list of `(label, function)` plus `run()` |

Expressions are tuples: `('n', 2)`, `('v', 'x')`, `('+', a, b)`, `('sin', a)`.
The parser is iterative shunting-yard. Rationals are `(numerator, denominator)`
pairs.

## Development

Runs unmodified under desktop CPython; `casioplot.py` stubs the graphics.

```
python3 tests.py       # 6752 checks
python3 stress.py      # 443 checks, drives every tool
python3 devlint.py     # MicroPython compliance, 32 files
```

`tests.py` auto-discovers `tests_*.py`, each exposing
`SECTIONS = [(label, fn)]` where `fn` takes the harness object.

Adding a tool: add it to the module's `TOOLS`, add assertions to `tests.py`,
add help text to `casui.HELP`, add it to the table above. Tests enforce the
first and the last.

## Not covered

`SPEC_AUDIT.md` checks all 730 H640 and H645 content statements against the
code. Nine have nothing behind them.

| Code | Statement | Reason |
| --- | --- | --- |
| `D14` | Clean data: missing values, errors, outliers | Not a calculator task |
| `SH5` | Hypothesis test for an average using the Wilcoxon signed rank test | Needs an exact critical-value table that could not be verified to the standard the PMCC and Spearman tables were held to |
| `L5` | Recognise when a linear programming problem requires an integer solution | Not a calculator task |
| `L6` | Formulate a range of network problems as linear programming problems | Not a calculator task |
| `N13` | Explore network algorithms through their LP formulations | Not a calculator task, for the same reason as `L6` |
| `L11` | Use a visualisation of a three-dimensional linear programming problem | Out of scope for the hardware |
| `L16` | Handle variables which may be negative | Not built |
| `c2` | Use software to produce a tangent to a curve at a variable point | Out of scope for the hardware |
| `T10` | Solve other Diophantine equations | Partly, and open-ended as stated |

## Probes

`hwcheck.py`, `keyprobe.py`, `calib_screen.py`, `fontmetrics.py` and
`fontmetrics2.py` are one-off hardware probes, not part of the app.

## License

MIT.
