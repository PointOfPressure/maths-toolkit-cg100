# OCR Y420 Core Pure, November 2021 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 3 | partial fractions | `CAS » partial fractions » 1/((2x-1)(2x+1))` | AWKWARD | prints "1/4/(x-1/2)" and "-1/4/(x+1/2)"; MS ½/(2r-1) - ½/(2r+1): leading coefficient pulled out of the factor |
| 1b | 4 | telescoping sum | `fcore » Method of differences » 1/((2r-1)(2r+1))` | AWKWARD | "S(n) = 1/2 - (1/(4*n+2))"; MS asks single fraction n/(2n+1) |
| 1b | | single fraction | `CAS » single fraction » 1/2-1/(4x+2)` | OK | ⇒ "x/(2*x+1)" |
| 2 | 4 | gradient of 6 arcsin 2x at 1/4 | `fcalc » d/dx inverse trig » 6asin(2x),1/4` | OK | ⇒ "f'(1/4) = 8sqrt(3)" |
| 3a | 2 | mod, arg of -2+2i | `fcore » Modulus-argument » -2+2i` | OK | ⇒ "arg z = 3pi/4 rad" |
| 3b | 4 | z1/z2 mod-arg | `fcore » Multiply in mod-arg » sqrt(8),3pi/4,2,pi/6` | OK | ⇒ "z/w: r = sqrt(2), arg = 7pi/12" |
| 4 | 4 | mean value of 1/(1+4x^2) | `fcalc » Mean value of f » 1/(1+4x^2),-1,1` | OK | ⇒ "mean = 0.554" |
| 5a | 1 | ln(1+2x) to x^2 | `fcore » Maclaurin series » ln(1+2x),2` | OK | ⇒ "-2*x^2+2*x" |
| 5b | 3 | percentage error at x = 0.1 | `fcore » Maclaurin approx » ln(1+2x),2,0.1` | AWKWARD | ⇒ "error = 0.00232"; absolute error only, % error (-1.27%) by hand |
| 5c | 2 | validity at x = 1 | `fcore » Maclaurin approx » ln(1+2x),2,1` | OK | ⇒ "x = 1 is outside the interval" |
| 6 | 4 | invariant lines y = mx | `fcore » Invariant points/lines » 1,2,2,-2` | OK | ⇒ "invariant line y = -2x" |
| 7 | 6 | induction sum r/2^(r-1) | `fcore » Induction: sum » r/2^(r-1),4-(n+2)/2^(n-1)` | OK | ⇒ "Proved for all n >= 1" |
| 8a | 5 | roots a, -a, b, 1/b with p, q unknown | `fcore » Quartic real coeffs » 4,-4,-5,9,-9` | GAP | no tool uses root relationships with unknown coefficients; only checks once p = -5, q = 9 are known (gives ±3/2, (1±sqrt3 i)/2) |
| 8b | 4 | p, q | `fcore » Vieta root sums » 4,-4,-5,9,-9` | GAP | coeffs refuse letters; Vieta in reverse (roots -> coefficients) missing |
| 9a | 2 | image of unit square | `fcore » AB and BA (2x2) » -1,0,-2,1,1,1,0,1` | AWKWARD | no "image of points" tool; AB with a 2x2 of two vertices at a time, read columns |
| 9b(i) | 1 | det M | `fcore » Determinant 2x2 » -1,0,-2,1` | OK | ⇒ "det A = -1" |
| 9b(ii) | 2 | meaning | `fcore » Determinant 2x2 » -1,0,-2,1` | OK | ⇒ "det < 0: orientation is reversed" |
| 9c(i) | 3 | split M into two transformations | `fcore » Describe a 2x2 » -1,0,-2,1` | GAP | "not a standard transformation"; no decomposition (reflection then shear) |
| 9c(ii) | 3 | verify product | `fcore » A then B (2x2) » -1,0,0,1,1,0,2,1` | OK | ⇒ "[-2 1]" |
| 10a | 2 | cube roots of unity | `fcore » Roots of unity » 3` | OK | ⇒ "w^1 = -1/2+sqrt(3)i/2" |
| 10b(i) | 5 | z^3 = 1 + sqrt3 i in r e^(it), -pi < t <= pi | `fcore » nth roots of z » 1+sqrt(3)i,3` | AWKWARD | roots printed as decimals; "args (pi/3 + 2pi k)/3" gives 13pi/9 not -5pi/9; r shown as 2^(1/3) |
| 10b(ii) | 2 | rotation + enlargement | — | none | read from 10b(i) |
| 10b(iii) | 2 | sum of roots | `fcore » nth roots of z » 1+sqrt(3)i,3` | OK | ⇒ "sum = 0" |
| 10b(iv) | 2 | hence trig identity | — | none | |
| 11a(i) | 1 | u.v in m | `fcore » Scalar product, angle » k,1,-3,1,2,-2` | GAP | "a: unknown k"; no symbolic vector entries |
| 11a(ii) | 2 | u x v in m | — | GAP | as 11a(i) |
| 11b(i) | 3 | angle between planes | `fcore » Angle between planes » 2,1,-3,1,2,-2` | OK | ⇒ "= 27 deg" |
| 11b(ii) | 3 | skew lines distance | `fcore » Distance two lines » 3,0,2,3,1,-3,0,4,-2,1,2,-2` | OK | ⇒ "distance = 2sqrt(2)" |
| 12 | 4 | proof | — | none | |
| 13 | 7 | y'' + 2y' - 3y = 2e^x | `fcalc » PI for k e^(px) » 1,2,-3,2,1` | OK | ⇒ "A*e^(x)+B*e^(-3*x)+e^(x)*x/2" |
| 14a | 7 | max of r = a(cos t + 2 sin t) | `fcalc » Plot r = f(theta) » cos(x)+2sin(x)` | OK | ⇒ "= 2.24 at th = 1.1"; a = 1; R-form tool gives the angle only in degrees (63.4) |
| 14b(i) | 6 | polar -> cartesian circle | `mpure » Circle from general » -1,-2,0` | AWKWARD | ⇒ "radius = sqrt(5)/2"; converting r = a(cos+2sin) to x^2+y^2 = ax+2ay is by hand (no polar-equation -> cartesian tool) |
| 14b(ii) | 1 | centre in polar | `fcalc » Cartesian to polar » 1/2,1` | OK | ⇒ "r = sqrt(5)/2" |
| 15 | 6 | sheaf: det = 0 gives k | `fcore » Det 3x3 in terms of k » -4,k,7,1,-2,5,2,3,1` | OK | ⇒ "singular when k = -13" |
| 15 | | consistency gives l | `fcore » Three planes » -4,-13,7,4,1,-2,5,5,2,3,1,2` | AWKWARD | ⇒ "sheaf: the planes share a line"; l = 5 only by trial; no "value of the constant for consistency" |
| 16a | 4 | cosh 2u = 1 + 2 sinh^2 u | `fcalc » Identity check at x » 0.7` | AWKWARD | numeric only, no exponential working |
| 16b | 10 | int 0..2 x^2/sqrt(4+x^2) | `CAS » definite integral a..b » x^2/sqrt(4+x^2) ; 0,2` | AWKWARD | "integral = 1.07" numeric only; matches 2sqrt2 - 2ln(1+sqrt2) = 1.0657 |
| 16b | | antiderivative | `fcalc » Integrate hyperbolic » x^2/sqrt(4+x^2),0,2` | GAP | says "no elementary integral" (false: x sqrt(x^2+4)/2 - 2 arsinh(x/2)); no x = a sinh u substitution |
| 17a(i) | 2 | show | — | none | |
| 17a(ii) | 2 | show | — | none | |
| 17b(i) | 4 | dx/dt + ax = a, x(0) = 0 | `fcalc » Separable DE » 1,1-y,0,0` | OK | ⇒ "-e^(-x)+1"; a = 1 only |
| 17b(i) | | with letter a | `fcalc » Integrating factor » a,a,0,0` | WRONG | "int (IF)Q dx is not elementary" for int a e^(ax) dx; integrator fails with a letter constant in the exponent |
| 17b(ii) | 2 | 1 - e^-a = ½ | `CAS » solve f(x)=0 » 1-e^(-x)-1/2` | OK | ⇒ "x = 0.693" |
| 17c(i) | 1 | explain | — | none | |
| 17c(ii) | 9 | IF solution, maximum | `fcalc » Integrating factor » 2/(1-x),1,0,0` | OK | ⇒ "-x^2+x"; a = 1 (max independent of a) |
| 17c(ii) | | maximum | `CAS » stationary points » x(1-x)` | OK | ⇒ "(0.5, 1/4)  max" |

Parts: 41. Rows: OK 24, WRONG 1, AWKWARD 9, GAP 6, none 6.
