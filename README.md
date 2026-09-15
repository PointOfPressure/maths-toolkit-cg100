# Maths Toolkit for the Casio fx-CG100 (AQA 7357 + 7367)

A calculator app in stock MicroPython 1.9.4 using the built-in `casioplot`.
An expression calculator with complex numbers, a CAS (simplify, expand,
factorise, solve, differentiate, integrate, series, limits), a plotter, the
AQA formulae booklet, and 417 tools mapped section by section to AQA A-level
Mathematics 7357 and Further Mathematics 7367 (Core Pure + Mechanics +
Statistics options).

## Install

Run `./deploy.sh <mountpoint>` with the calculator connected as a USB drive.
It deletes every other `.py` in the storage root and copies these in:
`maths.py`, `casui.py`, `casutil.py`, `caslex.py`, `caseng.py`, `casrender.py`, `cascalc.py`, `caspoly.py`, `casalg.py`, `cassolve.py`, `plot.py`, `formulae.py`, `tables.py`, `mpure.py`, `mcalc.py`, `mstat.py`, `mmech.py`, `fcore.py`, `fcalc.py`, `fmech.py`, `fstat.py`.

Then on the calculator: Python app > File > Open > `maths.py` > Run.

## Screens

Home: Calculate, CAS f(x), Maths 7357, Further 7367, Formulae, Angle.

| Menus | |
| --- | --- |
| up / down | move, wraps |
| 1-9 | jump to entry |
| page up / down | move a screen |
| OK, EXE | choose |
| EXIT | back |

| Input line | |
| --- | --- |
| type values separated by commas in the order the field list shows | `1,-3,2` |
| `?` | unknown, where a tool solves for it (e.g. SUVAT `0,?,9.8,?,3`) |
| `data*` fields | as many values as you like, last field |
| `A[3x3]` fields | nine numbers row by row; the screen shows the grid as you type |
| `f(x)` fields | an expression; `x`, `t`, `y`, `pi`, `e`, `i`, `sqrt(`, `ln(`, `e^(` all work |
| SHIFT | `=`, `ln(`, `log(`, `pi`, `i`, inverse trig, `logb(`, `ans` |
| ALPHA | letters |
| MENU | symbol list |
| UP | recall the last entry for this tool |
| DEL / DOWN / EXIT | delete / clear / cancel |

| Result screen | |
| --- | --- |
| FORMAT | cycle: answer only / with working / full precision |
| up / down | scroll |
| EXIT, OK | back to the input line for the same tool |

| Plot | |
| --- | --- |
| arrows | pan |
| + / - | zoom |
| OK | trace (left/right move, up/down switch curve) |
| 0 | reset |

Answers are exact when the maths is exact (`1/2`, `2sqrt(3)`, `pi/4`,
`2-3i`) and 3 s.f. otherwise; FORMAT shows 10 s.f.

## Tools: Maths 7357

| Section | Tools |
| --- | --- |
| A Proof | Counterexample f>0, Counterexample prime, Counterexample d|f(n), Counterexample f=g |
| B Algebra and functions | Index a^(p/q), Simplify sqrt(n), Simplify surd expr, Rationalise, Quadratic, Quadratic in f(x), Simultaneous 2 linear, Line meets quadratic, Solve f(x)=g(x), Linear inequality, Quadratic inequality, Expand, Factorise, Divide p(x) by d(x), Factor theorem, Simplify f(x)/g(x), Partial fractions, Composite fg and gf, Inverse function, Transform af(bx+c)+d, Solve |ax+b|=cx+d, Proportion y=kx^n, Plot f(x) |
| C Coordinate geometry | Line through 2 points, Perpendicular bisect, Parallel through pt, Perpendicular thru pt, Intersect y=mx+c, Circle from general, Circle centre+radius, Circle through 3 pts, Line meets circle, Tangent to circle, Param to Cartesian, Param point at t, Plot parametric |
| D Sequences and series | Arithmetic a,d,n, Geometric a,r,n, AP: n for Sn > k, GP: n for Sn > k, Binomial (a+bx)^n, Binomial rational n, Sigma sum f(r) a..b, Recurrence u(n+1), Terms of u(n), nCr and nPr |
| E Trigonometry | Exact trig at x deg, Triangle SSS, Triangle SAS, Triangle ASA, Triangle SSA, Area (1/2)ab sinC, Arc and sector (rad), Arc and sector (deg), Degrees to radians, Radians to degrees, Solve trig eqn (deg), Solve trig eqn (rad), Quad in sin x (deg), Quad in cos x (deg), Quad in tan x (deg), R form a sin + b cos, Small angle (rad), Compound angle (deg), Double angle (deg), sec cosec cot (deg), arcsin arccos arctan, Identity check (rad) |
| F Exponentials and logs | Solve a^x = b, Solve log_a x = c, log base a of x, Evaluate log expr, y = a x^n from 2 pts, y = k b^x from 2 pts, Log-log fit y=ax^n, Log-lin fit y=kb^x, N = A e^(kt) 2 pts, Evaluate A e^(kt), Compound interest |
| G Differentiation | Derivative f' and f'', Tangent and normal, Stationary points, Inflection points, Increasing/decreasing, First principles, Parametric dy/dx, Implicit dy/dx, Connected rates, Inverse derivative, f, f' and f'' at a |
| H Integration | Indefinite integral, Definite integral, Area under curve, Area between curves, Substitution u=g(x), Integration by parts, Riemann sum table, Separable DE, Separable DE at point, d/dx of an integral |
| I Numerical methods | Sign change table, Newton-Raphson, Fixed point x=g(x), Bisection, Trapezium rule, Iterate to n dp |
| J Vectors | Magnitude and angle, Components from r,th, Sum and difference, Scalar multiple k a, Unit vector, Distance A to B, Midpoint and ratio, Parallel test, Resultant of forces, Position r0 + v t, Angle between vectors |
| K Statistical sampling | Simple random sample, Systematic sample, Stratified sample |
| L Data presentation | Summary stats, Stats from summary, Frequency table, Grouped table, Coding x from y, Outliers, Histogram, Box plot, Cumulative frequency, Scatter PMCC regress, Regression predict |
| M Probability | P(A or B), Conditional P(A|B), Two-way table counts, Tree two stage |
| N Statistical distributions | Binomial P(X=k), Binomial P(X<=k), Binomial P(X>=k), Binomial P(a<=X<=b), Binomial least k, Binomial mean var, Normal P(X<x), Normal P(X>x), Normal P(a<X<b), Inverse Normal, Standardise z, Normal find mu or sd, Normal mu and sd, Normal inflection, Discrete uniform, Discrete distribution |
| O Hypothesis testing | HT binomial lower, HT binomial upper, HT binomial two tail, z test mean lower, z test mean upper, z test mean two tail, PMCC test 1 tail, PMCC test 2 tail, Critical z value, PMCC crit value |
| P Quantities and units | km/h to m/s, m/s to km/h, Weight and SI units |
| Q Kinematics | SUVAT, Vertical under gravity, v-t graph points, s-t graph points, s(t) to v and a, v(t) to s and a, a(t) to v and s, Distance from v(t), Vector SUVAT, Projectile launch, Projectile at time t, Projectile angle, Projectile to a point |
| R Forces and Newton laws | Resolve a force, Resultant of forces, Equilibrium check, Newton II F = ma, Plane dynamics, Pulley over a peg, Tow bar in a line, Lift reaction, Friction horizontal, Rough slope, Mass on rough table |
| S Moments | Moments about a point, Beam on two supports, Tilting point |

## Tools: Further 7367

| Section | Tools |
| --- | --- |
| A Proof | Induction: sum, Induction: divisor, Induction: M^n |
| B Complex numbers | Arithmetic z, w, Modulus-argument, From mod-arg form, Multiply in mod-arg, De Moivre z^n, nth roots of z, Roots of unity, Quadratic roots, Cubic real coeffs, Quartic real coeffs, Argand plot, Locus |z-z1| = r, Locus arg(z-z1) = t, Locus |z-z1|=|z-z2|, cos nt, sin nt powers, cos^n t, sin^n t, Complex geometric sum |
| C Matrices | pA + qB (2x2), pA + qB (3x3), AB and BA (2x2), AB and BA (3x3), Determinant 2x2, Determinant 3x3, Inverse 2x2, Inverse 3x3, Solve 3 eqns by A^-1, Rotation 2D (deg), Reflect in y=x tan t, Stretch or enlarge 2D, Describe a 2x2, Rotation 3D (axis), Reflect 3D in plane, Invariant points/lines, Eigen 2x2, Eigen 3x3, Diagonalise 2x2 M^n, Diagonalise 3x3 M^n |
| D Further algebra and functions | Vieta root sums, Power sums of roots, Roots p a + q, Roots 1/a, Roots a^2, Sum r, r^2, r^3, Sum f(r), r = a..b, Method of differences, Maclaurin series, Binomial (1+x)^p, Limit as x -> a, Solve f(x) > g(x), Solve f(x) < g(x), Graph (ax+b)/(cx+d), Graph quad / linear, Graph quad / quad, Graph f, |f|, f(|x|), Parabola y^2 = 4ax, Ellipse x2/a2+y2/b2, Hyperbola x2/a2-y2/b2, Rect hyperbola xy=c^2, Transform y = f(x) |
| E Further calculus | Integral to infinity, Singular endpoint int, Volume about x-axis, Volume about y-axis, Mean value of f, Integrate by partials, d/dx inverse trig, Int 1/sqrt(a2-x2), Int 1/(a2+x2), Arc length y=f(x), Arc length parametric, Surface area x-axis, Surface area param, Reduction x^n e^x, Reduction sin^n, Reduction cos^n, Reduction tan^n, Reduction (ln x)^n, Limit x^k e^-x, Limit x^k ln x |
| F Further vectors | Line from two points, Line to cartesian, Plane from 3 points, Plane point + normal, Angle between lines, Angle line and plane, Angle between planes, Perpendicular check, Vector product, Area of triangle, Is p on (r-a)xb=0, Intersect two lines, Distance two lines, Line meets plane, Point to line dist, Point to plane dist |
| G Polar coordinates | Polar to cartesian, Cartesian to polar, Plot r = f(theta), Polar area, Tangent para to axis, Tangent perp to axis |
| H Hyperbolic functions | Six hyperbolics at x, Inverse hyperbolics, Solve a cosh+b sinh=c, Identity check at x, Plot sinh cosh tanh, d/dx hyperbolic, Integrate hyperbolic, Int 1/sqrt(x2+a2), Int 1/sqrt(x2-a2) |
| I Differential equations | Integrating factor, Second order homogen, Second order with IVs, PI polynomial RHS, PI for k e^(px), PI for m cos + n sin, SHM from omega, Hooke law SHM, Damping classify, Coupled equations |
| J Numerical methods | Mid-ordinate rule, Simpson's rule, Compare rules, Euler step by step, Improved Euler |
| MA Dimensional analysis | Dimensions list, Name from M,L,T, Check consistency, Find powers a,b,c |
| MB Momentum and collisions | Conservation 1D, Coalesce, one mass, Direct impact, e, Wall: speed and angle, Wall: velocity vector, Oblique, two spheres, Impulse 1D, Impulse 2D, Impulse of F(t), Three in a line |
| MC Work, energy and power | Work F d cos th, KE and GPE change, Energy vs resistance, Hooke and EPE: k, Hooke and EPE: lam, Work of F(x), Power P = F v, Max speed on a slope, Accel at speed v, Elastic equilibrium, Elastic max extension |
| MD Circular motion | Angular speed units, Rev per min to rad/s, Circle from v and r, Circle from om and r, Circle: vectors r,v,a, Conical: angle given, Conical: omega given, Conical, two strings, Banked track speeds, Banked: friction at v, Rough table circle, Vert circle: string, Vert circle: rod, Outside a sphere |
| ME Centres of mass and moments | COM of parts m,x,y, Standard centroids, Arc/sector centroid, Lamina under y = f(x), Lamina between curves, Solid of revolution Ox, Slide or topple, slope, Push a block, Suspend a lamina, Ladder, smooth wall, Beam on two supports, Rod, hinge and string, Forces and moments |
| SA Discrete random variables | DRV from table, DRV from formula, E and Var of aX+b, E of g(X) from table, Discrete uniform 1-n |
| SB Poisson distribution | Poisson P(X=k), Poisson a<=X<=b, Poisson inverse, Sum of Poissons, Poisson test upper, Poisson test lower, Poisson model check |
| SC Type I and Type II errors | Type I binomial, Type II binomial, Type I Poisson, Type II Poisson, Type I Normal, Type II Normal |
| SD Continuous random vars | pdf E Var and check, pdf median quartiles, Mode of a pdf, cdf F(x) from a pdf, pdf P(c<X<d), E of g(X) from a pdf, Piecewise pdf, Rectangular U(a,b), E and Var of aX+b, E and Var of X+Y |
| SE Chi squared association | Chi-sq association, Expected frequencies, Chi-sq from statistic |
| SF Exponential distribution | Exponential Exp(L), Exponential probs, Waits from a rate, Memoryless check |
| SG Inference one sample t | t-test from data, t-test from summary |
| SH Confidence intervals | CI mean sigma known, CI from data, CI from summary, Is mu0 in the CI, Sample size for width |

## Development

Runs unmodified under desktop CPython; `casioplot.py` stubs the graphics.

```
python3 tests.py       # engine checks + every tool case
python3 stress.py      # every tool with odd inputs, must not crash
python3 devlint.py     # MicroPython 1.9.4 compliance for the device files
python3 casioshot.py   # renders screens to shots/*.png
python3 mkreadme.py    # regenerates this file
```

Design and contracts: `docs/superpowers/specs/`.
