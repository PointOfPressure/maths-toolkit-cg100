# OCR Y420 Core Pure, June 2022 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 3 | sum 3r^2+3r+1 | `fcore » Sum f(r), r = a..b » 3r^2+3r+1,1` | OK | ⇒ "n^3+3*n^2+3*n"; the (r+1)^3 - r^3 telescoping argument not shown |
| 1b | 4 | sum r(r+1) | `fcore » Sum f(r), r = a..b » r(r+1),1` | OK | ⇒ "n^3/3+n^2+2*n/3" |
| 1b | | factorise | `CAS » factorise » x^3/3+x^2+2x/3` | AWKWARD | ⇒ "x*(x+1)*(x+2)/3"; retype with x for n |
| 2 | 5 | int 3..inf 1/(x^2-4x+5) | `fcalc » Integral to infinity » 1/(x^2-4x+5),3` | OK | ⇒ "integral = pi/4" |
| 3 | 6 | 3cosh x = 2sinh^2 x, exact ln | `CAS » solve exact f(x)=0 » 3cosh(x)-2sinh(x)^2` | AWKWARD | "x = ±1.316958, numeric roots - no exact form"; MS ±ln(2+sqrt3); no quadratic-in-cosh solver |
| 3 | | | `fcalc » Solve a cosh+b sinh=c » 3,0,0` | AWKWARD | linear a cosh + b sinh = c only; cannot take sinh^2 |
| 4a | 3 | det = 0 in m | `fcore » Det 3x3 in terms of k » k,2,1,0,1,-2,2,0,3` | OK | ⇒ "singular when k = 10/3" |
| 4b | 4 | det M in k, (3k+1)(4k+3) = 2 | `fcore » Det 3x3 in terms of k » k,1,0,-3,4,0,0,0,1` | AWKWARD | ⇒ "4*k+3"; 2x2 det with a letter only by padding to 3x3 |
| 4b | | solve | `CAS » solve f(x)=0 » (3x+1)(4x+3)-2` | AWKWARD | "x = -1, -0.0833"; MS -1/12 exact (solve exact would be needed) |
| 5a | 2 | sketch | — | none | |
| 5b | 5 | area of cardioid | `fcalc » Polar area » 1-cos(x),0,2pi` | OK | ⇒ "area = 3pi/2"; a = 1, times a^2 |
| 6 | 5 | induction M^n | `fcore » Induction: M^n » 2,0,-1,1,2^n,0,1-2^n,1` | OK | ⇒ "Proved for all n >= 1" |
| 7 | 9 | partial fractions | `CAS » partial fractions » (x+1)/((x-1)(x^2+1))` | OK | ⇒ "-x/(x^2+1)" |
| 7 | | exact integral = ½ ln 2 | `CAS » definite integral a..b » (x+1)/((x-1)(x^2+1)) ; 2,3` | AWKWARD | ⇒ "ln(2)+ln(5)/2-ln(10)/2"; log terms not combined to ½ln 2 |
| 8a | 4 | sketch loci | `fcore » Locus arg(z-z1) = t » 10,3pi/4` | OK | ⇒ "y = -(x-10)"; gives 10i on the imaginary axis |
| 8b | 7 | k, then intersections | `fcore » Modulus-argument » -3+4i` | OK | ⇒ "z = 5(cos"; k = 5 from mod(10i - (3+6i)) |
| 8b | | line meets circle | `mpure » Line meets circle » -1,10,3,6,5` | OK | ⇒ "(7, 3)" |
| 9a | 2 | explain domain | — | none | |
| 9b(i) | 2 | f'(x) | `fcalc » d/dx hyperbolic » ln(1+sinh(x))` | OK | ⇒ "cosh(x)/(sinh(x)+1)" |
| 9b(ii) | 3 | f''(x) as (a sinh x + b)/(1+sinh x)^2 | `CAS » d2/dx2 » ln(1+sinh(x))` | AWKWARD | gives (-cosh^2 x + sinh x (sinh x + 1))/(…)^2; cosh^2 = 1 + sinh^2 not applied, a, b not read off |
| 9c | 3 | quadratic approximation | `fcore » Maclaurin series » ln(1+sinh(x)),2` | OK | ⇒ "-x^2/2+x" |
| 9d | 2 | % error at 0.1 | `fcore » Maclaurin approx » ln(1+sinh(x)),2,0.1` | AWKWARD | ⇒ "error = 0.000462"; no percentage (MS 0.48%) |
| 10a | 6 | roots a, 2/a, b, 3b with a, b unknown | `fcore » Quartic real coeffs » 4,16,27,22,6` | GAP | no tool for given root relationships; only checks once a = 27, b = 22 known |
| 10b | 4 | a, b | `fcore » Vieta root sums » 4,16,27,22,6` | GAP | no roots -> coefficients tool |
| 11a(i) | 2 | plot B, C | — | none | sketch |
| 11a(ii) | 2 | z1 + z2 + z3 = 0 | — | none | show |
| 11b | 4 | cube roots of 8i | `fcore » nth roots of z » 8i,3` | OK | ⇒ "w0 = sqrt(3)+i" |
| 12 | 9 | (4-x^2)y' - xy = 1, y(0) = 1 | `fcalc » Integrating factor » -x/(4-x^2),1/(4-x^2),0,1` | OK | ⇒ "(asin(x/2)+2)/sqrt(-x^2+4)"; standard form P, Q by hand |
| 13a | 4 | angle AB and P1 | `fcore » Angle line and plane » 6,4,-2,1,-2,0` | OK | ⇒ "= 6.86 deg" |
| 13b | 5 | AB meets P1 and P2 | `fcore » Line meets plane » 4,0,-1,6,4,-2,1,-2,0,5` | OK | ⇒ "meets at (1, -2, 0)" |
| 13b | | | `fcore » Line meets plane » 4,0,-1,6,4,-2,2,3,-1,-4` | OK | ⇒ "meets at (1, -2, 0)" |
| 13c(i) | 1 | cross product | `fcore » Vector product » 1,-2,0,2,3,-1` | OK | ⇒ "a x b = (2, 1, 7)" |
| 13c(ii) | 3 | angle between planes | `fcore » Angle between planes » 1,-2,0,2,3,-1` | OK | ⇒ "= 61.4 deg" |
| 13c(iii) | 4 | line of intersection, A to it | `fcore » Two planes meet » 1,-2,0,5,2,3,-1,-4` | OK | ⇒ "r = (1, -2, 0) + t(2, 1, 7)" |
| 13c(iii) | | | `fcore » Point to line dist » 4,0,-1,1,-2,0,2,1,7` | OK | ⇒ "distance = 3.74" |
| 14a | 2 | (3-e^2it)(3-e^-2it) | `CAS » expand » (3-e^(2i*x))*(3-e^(-2i*x))` | AWKWARD | gives -3e^(2ix)-3e^(-2ix)+10; not 10 - 6cos 2t |
| 14b | 6 | infinite series as complex GP | `mpure » Sigma sum f(r) a..b » sin((2r+1)*0.7)/3^r,0,40` | AWKWARD | ⇒ "sum = 0.861"; numeric check at t = 0.7 against 6sin t/(5-3cos 2t) only; no C + iS / GP-sum tool |
| 15a(i) | 1 | N2L | — | none | |
| 15a(ii) | 1 | state SHM | — | none | |
| 15a(iii) | 1 | period | `fcalc » SHM from omega » sqrt(2),2,1` | OK | ⇒ "period T = 4.44"; MS 2pi/sqrt2 |
| 15a(iv) | 4 | x(t) | `fcalc » Second order with IVs » 1,0,2,2,1` | OK | ⇒ "2*cos(sqrt(2)*x)+(sqrt(2)/2)*sin(sqrt(2)*x)" |
| 15a(v) | 2 | amplitude | `fcalc » SHM from omega » sqrt(2),2,1` | OK | ⇒ "amplitude R = 3sqrt(2)/2" |
| 15b(i) | 1 | show | — | none | |
| 15b(ii) | 1 | damping type | `fcalc » Damping classify » 1,2,2` | OK | ⇒ "light damping" |
| 15b(iii) | 3 | GS | `fcalc » Second order homogen » 1,2,2` | OK | ⇒ "(A*cos(x)+B*sin(x))*e^(-x)" |
| 15c(i) | 7 | forced, with ICs | `fcalc » PI for m cos + n sin » 1,2,2,2,0,2,2,1` | OK | ⇒ "(11*cos(x)/5+12*sin(x)/5)*e^(-x)+2*sin(2*x)/5-cos(2*x)/5" |
| 15c(ii) | 2 | long-term period pi | — | none | read from PI |

Parts: 40. Rows: OK 27, WRONG 0, AWKWARD 10, GAP 2, none 8.
