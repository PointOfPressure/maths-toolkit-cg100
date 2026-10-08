# Maths Toolkit for the Casio fx-CG100 (AQA 7357 + MEI H645)

A calculator app in stock MicroPython 1.9.4 using the built-in `casioplot`.
An expression calculator with complex numbers, a CAS (simplify, expand,
factorise, solve, differentiate, integrate, series, limits), a plotter,
revision notes (the AQA formulae booklet plus notes for every paper sat), and
663 tools mapped section by section to two specifications:

- A-level Mathematics: **AQA 7357**
- A-level Further Mathematics: **OCR B (MEI) H645**, every paper: Core Pure
  (Y420), Mechanics Major/Minor (Y421/Y431), Statistics Major/Minor
  (Y422/Y432), Modelling with Algorithms (Y433), Numerical Methods (Y434),
  Extra Pure (Y435) and Further Pure with Technology (Y436).

## Install

Run `./deploy.sh <mountpoint>` with the calculator connected as a USB drive.
It precompiles every module to `.mpy` with MicroPython 1.9.4's `mpy-cross`
(`-mno-unicode`, the only build the fx-CG100 loads; path in `$MPYCROSS`,
default `~/dev/cg100/bin/mpy-cross-1.9.4`), deletes every other `.py`/`.mpy`
in the storage root, copies the launchers `maths.py` and `module.py` and the
modules in, and checks each file byte for byte. Device files:
`maths.py`, `module.py`, `font.py`, `casui.py`, `nat.py`, `casutil.py`, `caslex.py`, `caseng.py`, `casrender.py`, `cascalc.py`, `caspoly.py`, `casalg.py`, `cassolve.py`, `plot.py`, `formulae.py`, `notesui.py`, `notes_ix.py`, `notes_mp1.py`, `notes_mp2.py`, `notes_mp3.py`, `notes_ms.py`, `notes_mm.py`, `notes_cp1.py`, `notes_cp2.py`, `notes_cp3.py`, `notes_st1.py`, `notes_st2.py`, `notes_xp.py`, `tables.py`, `mpure.py`, `mcalc.py`, `mstat.py`, `mmech.py`, `fcore.py`, `fcalc.py`, `fmech.py`, `fstat.py`, `falgo.py`, `fnum.py`, `fxpure.py`, `ffpt.py`, `ix_mpure.py`, `ix_mcalc.py`, `ix_mstat.py`, `ix_mmech.py`, `ix_fcore.py`, `ix_fcalc.py`, `ix_fmech.py`, `ix_fstat.py`, `ix_falgo.py`, `ix_fnum.py`, `ix_fxpure.py`, `ix_ffpt.py`.

Then on the calculator: Python app > `maths.py` (or `module.py`) > Run.

## Screens

Built for how the fx-CG100 actually performs (no clock, ~4 ms per text call,
Python ~300x slower than a laptop): no large fills, and only what a key
changed is redrawn.

Home is an icon grid: Calculate, CAS, Graph, Solve, Maths (AQA 7357),
Further (MEI H645), Notes, Settings. Every menu below it is a grid of word
tiles that remembers where you were. The status bar shows the screen, a
yellow S / red A for SHIFT / ALPHA, Rad/Deg, and Busy while something slow runs.

| Anywhere | |
| --- | --- |
| arrows | move (held arrows and DEL repeat) |
| OK, EXE | choose |
| EXIT | back |
| HOME | straight to the home grid |
| SETTINGS | Rad / Deg |
| 1-9 | jump to a tile |

| Typing (natural display) | |
| --- | --- |
| fraction key, divide | fraction; takes the term before it as the top |
| ^, x^2, e^x, sqrt | power / root boxes; SHIFT sqrt nth root, SHIFT ^ log base |
| sin, cos, tan, SHIFT log, SHIFT ln, ( | bracket pair round the cursor, sized to fit; `)` at the end steps out |
| arrows | move between boxes; up/down between top and bottom of a fraction |
| MENU | symbols |
| SHIFT DEL | clear |
| tool fields | values separated by commas in the order shown; `?` = unknown |

| Calculate | |
| --- | --- |
| EXE | answer under the line; history stays |
| FORMAT | exact / decimal |
| TOOLS | CAS operations on the line (d/dx, integrate, factorise, solve, plot...) |
| UP | recall earlier lines; + - x / continue from Ans |

| Result screen | |
| --- | --- |
| FORMAT | cycle: answer only / with working / full precision |
| up / down | scroll |

The toolkit quits by itself after roughly 10-15 minutes without a key, so a
forgotten session can't keep the calculator awake.

| Plot | |
| --- | --- |
| arrows | pan |
| + / - | zoom |
| OK | trace (left/right move, up/down switch curve) |
| 0 | reset |

Answers are exact when the maths is exact (`1/2`, `2sqrt(3)`, `pi/4`,
`2-3i`) and 3 s.f. otherwise; FORMAT shows 10 s.f.

## Notes

Notes > paper > topic > page. Short plain notes of what the formula booklet
leaves out: definitions, results to learn, method steps, conditions and test
wording, common traps. `label = formula` lines are typeset as fractions and
powers when they read exactly as written; set-in grey lines are details. The
topic menus come from the small `notes_ix.py`, and each `notes_*.py` loads only
when one of its topics is opened (`python3 tests_notes.py write` regenerates
the index).

| Paper | Topics |
| --- | --- |
| Formula booklet | Binomial expansion; Arithmetic series; Geometric series; Small angles; Trig identities; Differentiation; Diff from first princ.; Integration 1; Integration 2; Newton-Raphson; Numerical integration; Complex numbers; Matrix transformations; Summations; Maclaurin series; Vectors; Area of a sector; Hyperbolic functions; Conics; Further num. integ.; Numerical solution ODE; Arc length; Surface area of revol.; Constant acceleration; Centres of mass; Probability; Standard deviation; Discrete distributions; Sampling distributions; Contingency tables; Not in the booklet |
| Pure 7357 | Proof; Indices and surds; Quadratics; Inequalities; Polynomials; Graphs; Graph transforms; Functions; Partial fractions; Lines; Circles; Parametric; Binomial expansion; Sequences; Arithmetic series; Geometric series; Radians and triangles; Exact values; Trig graphs; Sec, cosec, cot; Inverse trig; Trig identities; R cos / R sin form; Solving trig eqns; Exponentials and logs; Log graphs, models; Derivative basics; Standard derivatives; Product, chain rule; Stationary points; Implicit, parametric; Integration; Definite integrals; Integration methods; Differential equations; Roots: sign change; Iteration, N-R; Trapezium rule; Vectors |
| Stats 7357 | Sampling; Averages and spread; Diagrams and outliers; Correlation; Probability; Binomial; Normal distribution; Normal approx to B; Choosing a model; Hypothesis testing; Test conclusions; Normal mean test; Correlation test |
| Mechanics 7357 | Units, modelling; Kinematics graphs; SUVAT; Variable acceleration; Projectiles; Newton's laws; Connected particles; Friction; Moments |
| Core Pure Y420 | Induction; Complex numbers; Mod-arg form; Argand diagram; Loci; Roots and coefficients; Related roots; De Moivre; nth roots; Matrices; 3x3 det and inverse; Matrix transforms; Invariant points, lines; 3 equations, 3 planes; Products of vectors; Lines in 3-D; Planes; Distances; Series; Maclaurin series; Inverse trig calculus; Partial fractions; Improper integrals; Volumes, mean value; Polar coordinates; Hyperbolic functions; Inverse hyperbolic; First order DEs; Second order DEs; Particular integrals; SHM, damping; Coupled DEs, modelling |
| Stats Y422 | Discrete RVs; Discrete uniform; Binomial; Poisson; Geometric; Continuous RVs; Cumulative distribution; Uniform U(a, b); Normal; Normal model; Bivariate data; PMCC; Spearman; Correlation tests; Regression; Chi-sq association; Goodness of fit; Estimation, CLT; Confidence intervals; Test for a mean; Wilcoxon signed rank; Test essentials; Sampling, simulation |
| Extra Pure Y435 | Sets; Recurrence: 1st order; Recurrence: 2nd order; Recurrence behaviour; Groups; Order, subgroups; Isomorphism; Eigenvalues; Diagonal form; Cayley Hamilton; Surfaces, contours; Partial derivatives |

## Tools: Maths (AQA 7357)

| Section | Tools |
| --- | --- |
| A Proof | Counterexample f>0, Counterexample prime, Counterexample d|f(n), Counterexample f=g |
| B Algebra and functions | Index a^(p/q), Simplify sqrt(n), Simplify surd expr, Rationalise, Quadratic, Quadratic in f(x), Simultaneous 2 linear, Line meets quadratic, Solve f(x)=g(x), Linear inequality, Quadratic inequality, Inequality f(x) > g(x), Discriminant in k, Expand, Factorise, Divide p(x) by d(x), Factor theorem, Simplify f(x)/g(x), Partial fractions, Composite fg and gf, Inverse function, Range of f on [a,b], Transform af(bx+c)+d, Solve |ax+b|=cx+d, Proportion y=kx^n, Plot f(x) |
| C Coordinate geometry | Line through 2 points, Perpendicular bisect, Parallel through pt, Perpendicular thru pt, Intersect y=mx+c, Triangle 3 vertices, Circle from general, Circle centre+radius, Circle through 3 pts, Line meets circle, Tangent to circle, Param to Cartesian, Param point at t, Plot parametric |
| D Sequences and series | Arithmetic a,d,n, Geometric a,r,n, AP: n for Sn > k, GP: n for Sn > k, AP from 2 terms, AP from term and sum, GP from 2 terms, Binomial (a+bx)^n, Binomial rational n, Sigma sum f(r) a..b, Recurrence u(n+1), Recurrence sum to N, Terms of u(n), nCr and nPr |
| E Trigonometry | Exact trig at x deg, Triangle SSS, Triangle SAS, Triangle ASA, Triangle SSA, Area (1/2)ab sinC, Arc and sector (rad), Arc and sector (deg), Degrees to radians, Radians to degrees, Solve trig eqn (deg), Solve trig eqn (rad), Quad in sin x (deg), Quad in cos x (deg), Quad in tan x (deg), R form a sin + b cos, Small angle (rad), Compound angle (deg), Double angle (deg), sec cosec cot (deg), arcsin arccos arctan, Identity check (rad) |
| F Exponentials and logs | Solve a^x = b, Solve log_a x = c, log base a of x, Evaluate log expr, y = a x^n from 2 pts, y = k b^x from 2 pts, Log-log fit y=ax^n, Log-lin fit y=kb^x, N = A e^(kt) 2 pts, Evaluate A e^(kt), Compound interest |
| G Differentiation | Derivative f' and f'', Tangent and normal, Stationary points, Inflection points, Increasing/decreasing, First principles, Parametric dy/dx, Implicit dy/dx, Implicit dy/dx = 0, Connected rates, Inverse derivative, f, f' and f'' at a |
| H Integration | Indefinite integral, Definite integral, Area under curve, Area between curves, Substitution u=g(x), Integration by parts, Riemann sum table, Separable DE, Separable DE at point, d/dx of an integral |
| I Numerical methods | Sign change table, Newton-Raphson, Fixed point x=g(x), Bisection, Trapezium rule, Iterate to n dp |
| J Vectors | Magnitude and angle, Components from r,th, Sum and difference, Scalar multiple k a, Unit vector, Distance A to B, Midpoint and ratio, Parallel test, Resultant of forces, Position r0 + v t, Angle between vectors |
| K Statistical sampling | Simple random sample, Systematic sample, Stratified sample |
| L Data presentation | Summary stats, Stats from summary, Frequency table, Grouped table, Coding x from y, Combine two groups, Outliers, Histogram, Box plot, Cumulative frequency, Scatter PMCC regress, Regression predict |
| M Probability | P(A or B), Conditional P(A|B), Two-way table counts, Tree two stage, Venn: find the ? |
| N Statistical distributions | Binomial P(X=k), Binomial P(X<=k), Binomial P(X>=k), Binomial P(a<=X<=b), Binomial least k, Binomial least n, Binomial mean var, Normal P(X<x), Normal P(X>x), Normal P(a<X<b), Inverse Normal, Normal approx to B, Normal conditional, Standardise z, Normal find mu or sd, Normal mu and sd, Normal inflection, Discrete uniform, Discrete distribution |
| O Hypothesis testing | HT binomial lower, HT binomial upper, HT binomial two tail, z test mean lower, z test mean upper, z test mean two tail, PMCC test 1 tail, PMCC test 2 tail, Critical z value, PMCC crit value |
| P Quantities and units | km/h to m/s, m/s to km/h, Weight and SI units |
| Q Kinematics | SUVAT, Vertical under gravity, v-t graph points, s-t graph points, s(t) to v and a, v(t) to s and a, a(t) to v and s, Distance from v(t), Vector SUVAT, Vector r(t) to v, a, Vector v(t) to r, a, Two particles meet, Projectile launch, Projectile at time t, Projectile angle, Projectile to a point |
| R Forces and Newton laws | Resolve a force, Resultant of forces, Equilibrium check, Two unknown forces, Newton II F = ma, Plane dynamics, Pulley over a peg, Tow bar in a line, Lift reaction, Friction horizontal, Rough slope, Mass on rough table, Slope and pulley |
| S Moments | Moments about a point, Beam on two supports, Tilting point, Ladder, smooth wall |

## Tools: Further Maths (OCR B MEI H645)

### Core Pure (Y420)

| Section | Tools |
| --- | --- |
| P Proof | Induction: sum, Induction: recurrence, Induction: M^n, Induction: divisor, Induction: de Moivre, Counterexample: prime, Counterexample: f > g |
| J Complex numbers | Arithmetic z, w, Solve az + bz* = c, Argand sum/product, Modulus-argument, From mod-arg form, Multiply in mod-arg, De Moivre z^n, nth roots of z, Roots of unity, Polygon: centre+vertex, Polygon: two vertices, Quadratic roots, Cubic real coeffs, Quartic real coeffs, Argand plot, Locus |z-z1| = r, Locus arg(z-z1) = t, Locus |z-z1|=|z-z2|, cos nt, sin nt powers, cos^n t, sin^n t |
| M Matrices, transformations | pA + qB (2x2), pA + qB (3x3), AB and BA (2x2), AB and BA (3x3), Determinant 2x2, Determinant 3x3, Det 3x3 in terms of k, Inverse 2x2, Inverse 3x3, Solve 3 eqns by A^-1, Rotation 2D (deg), Reflect in y=x tan t, Stretch or enlarge 2D, Shear 2D, Describe a 2x2, 2x2 from 2 images, A then B (2x2), Rotation 3D (axis), Reflect 3D in plane, Describe a 3x3, A then B (3x3), Invariant points/lines |
| V Vectors and 3-D | Scalar product, angle, Perpendicular check, Vector product, Area of triangle, Line from two points, Line to cartesian, Is p on (r-a)xb=0, Plane from 3 points, Plane point + normal, Plane pt + 2 dirs, Plane cartesian->vec, Three planes, Angle between lines, Angle line and plane, Angle between planes, Two planes meet, Intersect two lines, Distance two lines, Line meets plane, Point to line dist, Point to plane dist |
| A Roots of polynomials | Vieta root sums, Power sums of roots, Roots p a + q, Roots 1/a, Roots a^2, Cubic roots in AP, Cubic roots in GP, One root twice another |
| S Series, Maclaurin | Sum r, r^2, r^3, Sum f(r), r = a..b, Method of differences, Maclaurin series, Maclaurin approx, Binomial (1+x)^p |
| C Calculus | Integral to infinity, Singular endpoint int, Volume about x-axis, Volume about y-axis, Volume between curves, Mean value of f, Integrate by partials, d/dx inverse trig, Int 1/sqrt(a2-x2), Int 1/(a2+x2) |
| PO Polar coordinates | Polar to cartesian, Cartesian to polar, Plot r = f(theta), Polar area |
| H Hyperbolic functions | Six hyperbolics at x, Inverse hyperbolics, Solve a cosh+b sinh=c, Identity check at x, Plot sinh cosh tanh, d/dx hyperbolic, Integrate hyperbolic, Int 1/sqrt(x2+a2), Int 1/sqrt(x2-a2) |
| D Differential equations | Separable DE, Integrating factor, Second order homogen, Second order with IVs, PI polynomial RHS, PI for k e^(px), PI for m cos + n sin, SHM from omega, Hooke law SHM, Damping classify, Coupled equations, a = v dv/dx = f(x), a = f(v): dist, time |

### Mechanics (Y421/Y431)

| Section | Tools |
| --- | --- |
| D Dimensional analysis | Dimensions list, Name from M,L,T, Dims of a product, Check consistency, Find powers a,b,c, Change of units |
| F Forces and friction | Resultant of forces, Resolve along a line, Two unknown forces, Triangle of forces, mu = tan(angle), Rough slope, force F, Force range to hold, Friction, level ground |
| M Moments and rigid bodies | Forces and moments, Couple, Beam on two supports, Ladder, smooth wall, Rod, hinge and string, Slide or topple, slope, Push a block |
| W Work, energy and power | Work F d cos th, Work F.d vectors, Work of F(x), KE and GPE change, Speed after a drop, Energy vs resistance, Power P = F v, Power, F at an angle, Max speed on a slope, Accel at speed v |
| I Impulse and momentum | Conservation 1D, Coalesce, one mass, Direct impact, e, Find e, Ball bouncing, Wall: speed and angle, Wall: velocity vector, Oblique: vectors, Oblique: speed, angle, Impulse 1D, Impulse 2D, Impulse of F(t), Three in a line |
| G Centre of mass | COM in a line m,x, COM of parts m,x,y, COM in 3-D m,x,y,z, Standard centroids, Arc/sector centroid, Lamina under y = f(x), Lamina between curves, Wire along y = f(x), Solid of revolution Ox, Solid of revolution Oy, Suspend a lamina |
| C Circular motion | Angular speed units, Rev per min to rad/s, Circle from v and r, Circle from om and r, Tangential accel, Circle: vectors r,v,a, Conical: angle given, Conical: omega given, Conical, two strings, Banked track speeds, Banked: friction at v, Rough flat bend, Vert circle: string, Vert circle: rod, Outside a sphere |
| H Hooke's law | Hooke and EPE: k, Hooke and EPE: lam, Hooke: find unknown, Modulus from hanging, Elastic equilibrium, Elastic max extension, Spring: speed at x |
| V Vectors, variable forces | r(t) to v and a, a(t) to v and r, Vector suvat, Force from r(t), Relative motion, a = f(v): t and x, Projectile path, Angle to hit (x,y), Bounding parabola, Projectile on incline, Max range on incline, SHM from x0, v0, SHM speed at x, Verify x'' = f(x,v,t), Verify x' = f(x,t), Fit a,b from x0,v0, Fit c from x(t0) |

### Statistics (Y422/Y432)

| Section | Tools |
| --- | --- |
| D Discrete random vars | DRV from table, DRV from formula, DRV find k, E(g(X)) from table, E and Var of a+bX, E and Var of X+-Y, Discrete uniform |
| B Binomial and Poisson | Poisson P(X=k), Poisson a<=X<=b, Poisson least k, Poisson mu, P(X=k), Poisson mu, P(X<=k), Sum of Poissons, Poisson approx to B, Poisson model check, Binomial P(X=k), Binomial least n |
| G Geometric distribution | Geometric P(X=r), Geometric a<=X<=b, Geometric least r |
| C Continuous random vars | pdf E Var and check, pdf find k, pdf median quartiles, Mode of a pdf, cdf F(x) from a pdf, pdf from a cdf, cdf median quartiles, pdf P(c<X<d), E of g(X) from a pdf, Piecewise pdf, Rectangular U(a,b) |
| N Normal distribution | Normal P(a<X<b), Inverse Normal, Normal fit to data, Normal P from sample, aX+bY+c, nX vs X1+..+Xn, Normal prob plot |
| R Bivariate data | Scatter diagram, PMCC r, PMCC test from data, PMCC test from r, Spearman rs, Spearman test data, Spearman test from rs, Regression y on x, Regression x on y, Both regression lines, Residuals, Predict y from x, Predict x from y |
| H Chi-squared tests | Chi-sq association, Chi-sq contributions, Expected frequencies, GOF given probs, GOF given expected, GOF uniform, GOF binomial, GOF Poisson, Chi-sq crit and p |
| I Inference | Estimates from data, Estimates from sums, z test for a mean, z test from data, CI mean sigma known, CI mean from data, CI mean from summary, CI paired data, CI to test mu0, Sample size for width |
| W Wilcoxon signed rank | Wilcoxon single sample, Wilcoxon paired, Wilcoxon crit value, Wilcoxon from T |
| Z Simulation | Simulate binomial, Simulate Poisson, Simulate geometric, Simulate Normal, Simulate U(a,b), Simulate sample means, Simulate a DRV |

### Algorithms (Y433)

| Section | Tools |
| --- | --- |
| A Sorting and packing | Bubble sort, Shuttle sort, Quick sort, First fit, First fit decreasing, Order n^k scaling, Order n log n scaling |
| G Graphs | Graph from edges, Digraph from arcs, Graph from adjacency |
| N Networks | Dijkstra, Dijkstra directed, Prim, Prim from matrix, Kruskal, Shortest path as LP |
| F Network flows | Max flow min cut, Cut capacity, Max flow as LP |
| C Critical path | Activity on arc, Precedence table, Resource histogram, Schedule k workers |
| L LP graphical | LP 2-D maximise, LP 2-D minimise, LP 3-D vertices |
| S Simplex | Simplex max <=, Sensitivity ranging, Two-stage maximise, Two-stage minimise, Big-M maximise, Big-M minimise, Negative variables |

### Numerical (Y434)

| Section | Tools |
| --- | --- |
| U Errors | Absolute/rel error, Error in a+b, a-b, Error in ab, a/b, Error in f(x), Chop vs round d.p., Chop vs round s.f., k s.f. arithmetic, Two forms compared |
| E Solving equations | Bisection, False position, Secant method, Newton-Raphson, Fixed point x=g(x), Relaxation, Staircase/cobweb, Order from iterates, Compare methods, Justify root to d dp |
| D Numerical differentiation | Forward and central, Derivative h table, Error vs h plot |
| N Numerical integration | Midpoint rule, Trapezium rule, Simpson's rule, Integration table |
| A Approximating functions | Forward diff table, Newton fwd estimate, Lagrange polynomial |
| I Improved estimates | Richardson, Aitken delta squared, Limit from ratio r |

### Extra Pure (Y435)

| Section | Tools |
| --- | --- |
| R Recurrence relations | u(n+1) = a u(n), 1st order a u + f(n), 2nd order homogeneous, 2nd order + f(n), Verify u(n+1)=F(n,u), Verify u(n+2)=F(n,u,v), Behaviour u(n+1)=F, Associated sequence, Ratio u(n+1)/u(n) |
| G Sets and groups | Sets A, B in E, Subsets of a set, Group axioms, Element orders, Subgroups, Lagrange, Isomorphism G to H, Identify group (n<=10), Z_n under + mod n, Units under x mod n, Set under x mod n, Set under + mod n, Symmetries of n-gon |
| M Matrices: eigenvalues | Eigen 2x2, Eigen 3x3, Diagonalise 2x2 M^n, Diagonalise 3x3 M^n, Cayley-Hamilton 2x2, Cayley-Hamilton 3x3, Is v eigenvector 2x2, Is v eigenvector 3x3 |
| C Multivariable calculus | Partial derivatives, Stationary points, Tangent plane z=f, grad g, normal, plane, Contours z = c, Sections y = k, Sections x = k |

### Pure + Tech (Y436)

| Section | Tools |
| --- | --- |
| C Curves: plots and limits | Plot y = f(x), Family y = f(x, a), Family polar r(t, a), Family parametric, Envelope of family, Limit x -> a, Limit x -> +infinity, Limit x -> -infinity, Asymptotes, Graph (ax+b)/(cx+d), Graph quad / linear, Graph quad / quad, Stationary points, Cusps (gradient limit) |
| T Curves: tangents, arcs | Tangent, normal y=f(x), Tangent at variable p, Tangent parametric, Tangent polar, Tangent implicit, Chord of y = f(x), Cartesian to polar, Polar to cartesian, Arc length y=f(x), Arc length parametric, Arc length polar |
| D Differential equations | Tangent field, Verify a DE solution, Particular solution, Solution family, Euler step by step, Euler: halving h, RK2 (modified Euler), RK2 (midpoint), RK4, Euler, RK2, RK4 |
| N Number theory | gcd and lcm, Euclid and Bezout, Prime test, Prime factorise, Euler totient phi(n), a^b mod m, Modular inverse, Solve ax = b (mod m), Chinese remainder, Fermat's little thm, Wilson's theorem, Pythagorean triples, Triple from m, n, Pell x^2-ny^2=1, Linear ax+by=c, Integer solutions, Decimal to base b, Base b to decimal |

## Development

Runs unmodified under desktop CPython; `casioplot.py` stubs the graphics.

```
python3 tests.py       # engine checks + every tool case
python3 stress.py      # every tool with odd inputs, must not crash
python3 tests_notes.py # Notes: line widths, typesetting, index current
python3 devlint.py     # MicroPython 1.9.4 compliance for the device files
python3 casioshot.py   # renders screens to shots/*.png
python3 mkreadme.py    # regenerates this file
```

Design and contracts: `docs/superpowers/specs/`.
