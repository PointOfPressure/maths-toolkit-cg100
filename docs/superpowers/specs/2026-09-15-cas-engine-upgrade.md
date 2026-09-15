# CAS engine upgrade — every symbolic step the syllabus can ask for

Goal: `caseng.simplify`, `caspoly`, `cascalc` and the CAS menu must handle
every feasible symbolic step in AQA 7357 + 7367, exactly, in canonical form.
The user knows the maths; the engine's job is to do the step correctly and
print it the way a mark scheme would. Public API stays (parse trees, tostr,
simplify, diff, integ, defint, solve, factor, expand, partial, tidy), new
functions are added, and every section-module test must still pass.

Reference: the June-era monolith `/home/sayer/dev/cg100/backup-20260910/cas.py`
already has exact rational constants, n-ary sums/products and a broader
integration table; mine it.

## Canonical form (what `simplify` returns and `tostr` prints)

- Rational constants exact: `1/3 + 1/6 = 1/2`, `(2/3)^2 = 4/9`, `0.25 = 1/4`
  when the input was typed as a decimal that is a simple fraction.
- Sums flattened, like terms collected, ordered by degree descending, numeric
  coefficient first: `3x^2 - 2x + 1`, `x^2*y + x*y^2`.
- Products flattened, same base powers combined: `x^(1/2) * x^(3/2) = x^2`,
  `2x * 3x = 6x^2`, `(ab)^n = a^n b^n` when expanding.
- Negative and fractional powers: `x^(-2)` prints as `1/x^2`, `x^(1/2)` prints
  as `sqrt(x)` (typeset as a root), `x^(3/2)` as `x*sqrt(x)`.
- Rational expressions over a common denominator with common polynomial
  factors cancelled: `(x^2-1)/(x-1) = x+1`, `1/x + 1/(x+1) = (2x+1)/(x(x+1))`,
  `(x^2+3x+2)/(x^2-4) = (x+1)/(x-2)`.
- Surds: `sqrt(8) = 2sqrt(2)`, `sqrt(2)*sqrt(6) = 2sqrt(3)`, `sqrt(a)/sqrt(b)`
  combined, `2sqrt(3) + 5sqrt(3) = 7sqrt(3)`, `sqrt(x^2) = |x|`,
  `(sqrt(2)+1)(sqrt(2)-1) = 1`, `1/sqrt(2) = sqrt(2)/2`,
  `(3+sqrt(5))/(2-sqrt(5)) = -11-5sqrt(5)` (rationalise on request or when
  the denominator is a pure surd expression).
- Logs: `ln(a) + ln(b) = ln(ab)`, `2ln(x) = ln(x^2)` (combine on request),
  `ln(x^2) = 2ln(x)` (expand on request), `ln(e^x) = x`, `e^(ln x) = x`,
  `ln(1) = 0`, `ln(e) = 1`, `log(100) = 2`, `logb(2, 8) = 3`,
  `ln(8)/ln(2) = 3`, `ln(sqrt(x)) = ln(x)/2`.
- Exponentials: `e^a * e^b = e^(a+b)`, `(e^x)^2 = e^(2x)`, `2^x * 2^y = 2^(x+y)`,
  `4^x = 2^(2x)` on request, `e^(x)*e^(-x) = 1`.
- Trig: `sin^2 x + cos^2 x = 1`, `1 + tan^2 x = sec^2 x`, `sin x / cos x = tan x`,
  `2 sin x cos x = sin 2x`, `cos^2 x - sin^2 x = cos 2x`, `sin(-x) = -sin x`,
  `cos(-x) = cos x`, `sin(x + 2pi) = sin x`, `sin(pi - x) = sin x`,
  `cos(pi/2 - x) = sin x`, exact values at multiples of pi/6 and pi/4 (done),
  `sin(pi/12)` and `cos(75 deg)`-type values via compound angles on request
  (`(sqrt(6) - sqrt(2))/4`), `sec = 1/cos`, `cosec`, `cot` definitions,
  `asin(1/2) = pi/6`, `atan(1) = pi/4`, `acos(-1) = pi`.
- Hyperbolic: `cosh^2 x - sinh^2 x = 1`, `sinh x = (e^x - e^-x)/2` on request,
  `arsinh x = ln(x + sqrt(x^2+1))` on request, `cosh(0) = 1`.
- Complex exact: `(2+3i)/(1-i) = -1/2 + 5i/2`, `i^7 = -i`, `(1+i)^8 = 16`,
  `conj`, `mod(3+4i) = 5`, `arg(1+i) = pi/4`, `|z|^2 = z z*`, `sqrt(-12) = 2i sqrt(3)`,
  `e^(i pi) = -1`, mod-arg form `2(cos(pi/3) + i sin(pi/3))` = `1 + i sqrt(3)`.
- Factorials and binomials: `5! = 120`, `nCr(6,2) = 15`, `n!/(n-1)! = n`,
  `(n+1)!/n! = n+1`, `nCr(n,2) = n(n-1)/2`.
- Modulus: `|x^2| = x^2`, `|-x| = |x|`, `|2x| = 2|x|`, `|x|^2 = x^2`.

## Algebra operations (each a CAS menu entry and a callable)

- expand: polynomials, `(a+b)^n` via binomial, products with surds and i,
  `sin(A+B)` / `cos(2x)` / `tan(A-B)` compound angles, `ln(ab)`, `(x+1)^(-1)`
  as a binomial series to a given order (`series` below).
- factorise: over the rationals (done); common factor first (`2x^2+4x = 2x(x+2)`);
  difference of two squares including surds on request (`x^2 - 2 = (x-sqrt2)(x+sqrt2)`);
  sum/difference of cubes; quadratics in a function (`e^(2x) - 3e^x + 2 = (e^x-1)(e^x-2)`,
  `sin^2 x - sin x = sin x (sin x - 1)`); complete the square
  (`2x^2 + 8x + 3 = 2(x+2)^2 - 5`); grouping (`x^3 + x^2 + x + 1`).
- polynomial division: quotient and remainder, factor/remainder theorem.
- partial fractions: linear, repeated linear, irreducible quadratic factors
  (Further E4), improper fractions (divide first).
- common denominator / single fraction; rationalise denominator.
- substitute: x = a exact (`f(pi/3)`, `f(1+i)`, `f(sqrt(2))` all exact),
  or x = another expression.
- rearrange / make subject: `invert` extended to multi-step (`y = (2x+1)/(x-3)` -> `x = (3y+1)/(y-2)`).
- series: Maclaurin of f(x) to n terms exact, binomial series `(1+ax)^n` any
  rational n with validity, general term where standard.
- limit: `lim x->a f(x)` via substitution, cancellation, l'Hopital, series;
  `x->inf`.

## Solve exactly (`solve_exact(tree, var)` returns a list of exact trees, plus
a general-solution form for trig)

- linear, quadratic (surd/complex exact), cubic/quartic with a rational root
  then quadratic exact, polynomial in a function (`e^(2x) - 3e^x + 2 = 0` ->
  `x = 0, ln 2`; `sin^2 x = 1/4`), exponential `a^x = b` -> `ln b / ln a`,
  `3^(2x+1) = 5`, log equations (`ln(x) + ln(x-1) = ln 6` -> `x = 3`, reject
  `x = -2` with domain check), surd equations with extraneous-root check,
  modulus `|2x-1| = x+2`, rational `1/x + 1/(x+1) = 1`, trig on an interval
  exact (`2sin(2x) = 1` on `[0, 2pi)`) and general solution
  (`x = pi/12 + n pi, 5pi/12 + n pi`), hyperbolic (`3cosh x + 2sinh x = 5` exact ln forms),
  simultaneous linear (2 and 3 unknowns exact), linear + quadratic exact,
  inequalities: linear, quadratic, polynomial, rational, modulus -> exact
  interval sets printed as `x < -1 or x > 3` and set notation.
- numeric fallback (existing `solve`) only when exact fails, flagged.

## Calculus exact

- diff: product/quotient/chain results collected and simplified
  (`d/dx x^2 sin x = 2x sin x + x^2 cos x`, `d/dx ln(sin x) = cot x`,
  `d/dx (2x+1)/(x-1) = -3/(x-1)^2`), second derivatives, implicit
  (`x^2 + y^2 = 25` -> `dy/dx = -x/y`), parametric (`dy/dx = (dy/dt)/(dx/dt)` simplified),
  inverse trig/hyperbolic (`d/dx arcsin(2x) = 2/sqrt(1-4x^2)`), `a^x ln a`.
- integrate: standard forms table complete for the spec: `x^n`, `1/x`, `e^(kx)`,
  `a^x`, `sin/cos/tan/sec^2/cosec^2/sec tan/cosec cot`, `sec x` and `cosec x`
  (ln forms), `sinh/cosh/tanh/sech^2`, `1/(a^2+x^2)`, `1/sqrt(a^2-x^2)`,
  `1/sqrt(x^2+a^2)`, `1/sqrt(x^2-a^2)`, `1/(a^2-x^2)` via partial fractions,
  `f'(x)/f(x)`, `f'(x) f(x)^n`, `f'(x) e^f`, `f'(x) sin f`, trig powers
  (`sin^2`, `cos^2`, `sin^3`, `tan^2`, `cos^2 3x`) via identities, products
  `sin ax cos bx` via factor formulae, by parts (repeated, and the cyclic
  `e^x sin x` case), substitution when the pattern is `g'(x) h(g(x))`, partial
  fractions including quadratic factors (`arctan` results), rational functions
  generally, `ln x`, `x ln x`, `arcsin x`, reduction formulae for `I_n` families
  on request, `1/(x^2+2x+5)` by completing the square.
- definite exact: `int_0^pi sin x dx = 2`, `int_0^1 1/(1+x^2) dx = pi/4`,
  improper `int_1^inf 1/x^2 dx = 1` and `int_0^1 1/sqrt(x) dx = 2`, divergence detected.
- volumes of revolution, mean value, arc length symbolic when the integrand
  simplifies (`y = cosh x` -> `sinh` forms).
- differential equations exact: separable (`dy/dx = ky` -> `y = Ae^(kx)`, with
  particular solution), integrating factor, second-order constant-coefficient
  homogeneous and with polynomial/exponential/trig right-hand side, particular
  solutions from initial conditions, all printed in the mark-scheme form.

## Printing (`tostr`, typesetter)

- Coefficient before variable, `2sqrt(3)`, `pi/4`, `2pi/3`, `-x/2` not `(-1/2)*x`,
  `x/2` not `1/2*x`, `(x+1)/(x-2)`, `e^(2x)`, `sin^2(x)` printed as `sin(x)^2`
  and typeset as sin²x, `|x|`, `ln|x| + c` for integrals of `1/x`.
- Integrals end with ` + c`; general solutions use `A`, `B`, `n` where the
  mark scheme does.
- Fractions with negative numerators: `-1/2`, never `-(1/2)`; no `1*`, no `x^1`,
  no `+ -3`.

## Tests

A `tests_cas.py` in the harness style: each line above is at least one case
(input string -> expected canonical string, or expected set of solutions).
Every existing `tests.py` engine check and every section-module test keeps
passing. `python3 devlint.py` clean. Recursion under 40 frames on every
expression of the size a student would type (up to ~40 tokens).
