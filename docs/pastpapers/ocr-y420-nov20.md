# OCR Y420 Core Pure, November 2020 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 6 | sum r(r+1)(r+3) | `fcore » Sum f(r), r = a..b » r(r+1)(r+3),1` | OK | ⇒ "n^4/4+11*n^3/6+15*n^2/4+13*n/6" |
| 1 | | factorise | `CAS » factorise » x^4/4+11x^3/6+15x^2/4+13x/6` | AWKWARD | ⇒ "(3*x+13)*x*(x+1)*(x+2)/12"; retype S(n) with x for n; Sum tool never factorises |
| 2a | 5 | MN = I with M 2x3, N 3x2, unknowns | — | GAP | matrix tools are square only (2x2/3x3) and numeric; three equations by hand |
| 2b | 1 | reason | — | none | |
| 3 | 4 | int 0..1/3 1/sqrt(4-9x^2) | `CAS » definite integral a..b » 1/sqrt(4-9x^2) ; 0,1/3` | OK | ⇒ "pi/18" |
| 3 | | standard form | `fcalc » Int 1/sqrt(a2-x2) » 2,0,1/3` | AWKWARD | only a^2 - x^2; no coefficient on x^2 (needs 1/sqrt(a^2-b^2x^2)), gives a different integral |
| 4a | 4 | sum 1/alpha | `fcore » Vieta root sums » 2,0,-5,7` | OK | ⇒ "sum of 1/root = 5/7" |
| 4b | 4 | roots 2a-1 | `fcore » Roots p a + q » 2,-1,2,0,-5,7` | OK | ⇒ "2*x^3+6*x^2-14*x+38"; not divided by 2 (MS x^3+3x^2-7x+19 = 0), no "= 0" |
| 5a | 2 | polar coords A, B | — | none | read from r = a(3+2cos t) at t = 0, pi/2; trivial |
| 5b | 2 | explain symmetry | — | none | |
| 5c | 4 | area ½ int r^2, -pi..pi | `fcalc » Polar area » 3+2cos(x),-pi,pi` | OK | ⇒ "area = 11pi"; a = 1, times a^2 |
| 6 | 4 | z^2 - 4i z* + 11 = 0 | `fcore » Quadratic roots » 1,-4i,11` | GAP | "b must be real"; Solve az + bz* = c is linear only; no tool for equations in z^2 and z* (split Re/Im) |
| 7 | 6 | induction sum r.r! | `fcore » Induction: sum » r*r!,(n+1)!-1` | OK | ⇒ "Proved for all n >= 1" |
| 8a | 5 | find k so lines meet | `fcore » Intersect two lines » 0,2,2,-1,1,3,-1,2,3,2,3,4` | GAP | vector fields refuse k; only checks k = 3 once known ("they meet at (-3/5, 13/5, 19/5)") |
| 8b | 4 | acute angle | `fcore » Angle between lines » -1,1,3,2,3,4` | OK | ⇒ "= 43.3 deg" |
| 9a | 5 | m with no invariant lines | `fcore » Invariant points/lines » 1,-2,1,3` | GAP | matrix fields refuse m; invariant-line quadratic 2g^2 + 2g + m = 0 needs a discriminant in m (MS m > ½) |
| 9b | 3 | det = -5 gives m = -4 | `fcore » Det 3x3 in terms of k » 1,-2,0,k,3,0,0,0,1` | AWKWARD | ⇒ "2*k+3"; 2x2 det with a letter only via 3x3 padding; no "Det 2x2 in terms of k" |
| 9b | | invariant lines | `fcore » Invariant points/lines » 1,-2,-4,3` | OK | ⇒ "invariant line y = -2x" |
| 10 | 7 | V = pi int x^2 dy, x^2 = 2 arcosh y | `fcalc » Volume about y-axis » sqrt(2acosh(y)),1,2` | AWKWARD | "V = 5.67" decimal; MS exact 2pi(2ln(2+sqrt3)-sqrt3) |
| 10 | | exact | `CAS » definite integral a..b » 2*pi*acosh(x) ; 1,2` | AWKWARD | ⇒ "2*(2*acosh(2)-sqrt(3))*pi"; acosh not turned into ln form |
| 11a | 2 | sixth roots of 64 in r e^(it) | `fcore » nth roots of z » 64,6` | AWKWARD | roots in a+bi (1+sqrt(3)i ...); r e^(i k pi/3) form not listed per root |
| 11b | 4 | midpoint G, w = G/A | `fcore » Modulus-argument » 3/4+sqrt(3)i/4` | OK | ⇒ "z = sqrt(3)/2e^(i pi/6)"; G/A typed by hand (or `Arithmetic z, w`) |
| 11c | 2 | G^6 | `fcore » De Moivre z^n » 3/2+sqrt(3)i/2,6` | OK | ⇒ "z^6 = -27" |
| 12a | 2 | z^n + 1/z^n, z^n - 1/z^n | `fcore » cos^n t, sin^n t » 3` | OK | ⇒ "z - 1/z = 2i sin t, z^m + 1/z^m = 2cos mt" |
| 12b | 6 | sin^3 cos^3 in sin 6t, sin 2t | `CAS » expand » (x+1/x)^3*(x-1/x)^3` | GAP | gives (x^12-3x^8+3x^4-1)/x^6 only; no tool for sin^m t cos^n t in multiple angles (MS A = -1/32, B = 3/32) |
| 13a | 2 | sinh 2x = 2 sinh cosh | `fcalc » Identity check at x » 0.7` | AWKWARD | ⇒ "sinh2x = 1.9, 2sc = 1.9"; numeric check only, no exponential working |
| 13b | 2 | f'' of sinh^2 x | `CAS » d2/dx2 » sinh(x)^2` | AWKWARD | gives 2(cosh^2 x + sinh^2 x); simplify won't reach 2cosh 2x |
| 13c | 2 | explain | — | none | |
| 13d | 3 | coefficient of x^n | `fcore » Maclaurin series » sinh(x)^2,8` | GAP | ⇒ "x^8/315+2*x^6/45+x^4/3+x^2" correct terms but no general term 2^(n-1)/n! |
| 14 | 11 | coupled DEs | `fcalc » Coupled equations » -2,4,-3,5,0,1` | OK | ⇒ "4*e^(2*t)-4*e^(t)"; y shown as (8e^(2t)-6e^t)/2, not reduced |
| 15a | 3 | det in m | `fcore » Det 3x3 in terms of k » 1,k,3,2,1,5,1,-2,2` | OK | ⇒ "singular when k = 3" |
| 15b | 3 | solve by inverse | `fcore » Solve 3 eqns by A^-1 » 1,-2,3,2,1,5,1,-2,2,-12,-11,-9` | OK | ⇒ "x = 1" |
| 15c | 2 | vector equation | `fcore » Line from two points » 1,1,-2,3,0,-4` | OK | ⇒ "r = (1, 1, -2) + t(2, -1, -2)"; no "cartesian -> vector" input, needs a second point |
| 15d | 4 | P to l | `fcore » Point to line dist » 1,2,-3,1,1,-2,2,-1,-2` | OK | ⇒ "distance = sqrt(17)/3" |
| 15e(i) | 3 | l parallel to plane | `fcore » Line meets plane » 1,1,-2,2,-1,-2,1,-2,2,-9` | OK | ⇒ "parallel, never meets" |
| 15e(ii) | 2 | distance | `fcore » Point to plane dist » 1,1,-2,1,-2,2,-9` | OK | ⇒ "distance = 4/3" |
| 16a(i) | 1 | model | — | none | |
| 16a(ii) | 3 | verify P = A(1-e^-kt) | `CAS » d/dx » A*(1-e^(-k*x))` | AWKWARD | gives a*e^(-k*x)*k (A lowercased); substitution into the DE by hand |
| 16b | 8 | integrating factor | `fcalc » Integrating factor » -1/(x(1+x^2)),0` | AWKWARD | IF printed e^(-ln(x)+ln(x^2+1)/2); never simplified to sqrt(1+t^2)/t; CAS simplify leaves it too |
| 16b | | partial fractions | `CAS » partial fractions » 1/(x*(1+x^2))` | OK | ⇒ "-x/(x^2+1)" |
| 16c(i) | 4 | Q = 0 solution, long-term A | `fcalc » Integrating factor » -1/(x(1+x^2)),0,1,1/sqrt(2)` | AWKWARD | y = C e^(-(-ln x + ...)) unsimplified; long-term condition (limit) not an input |
| 16c(ii) | 2 | t/sqrt(1+t^2) = ½ | `CAS » solve f(x)=0 » x/sqrt(1+x^2)-1/2` | OK | ⇒ "x = 0.577"; x 60 = 35 min |
| 16d | 5 | IF with Q = t e^-t / sqrt(1+t^2) | `fcalc » Integrating factor » -1/(x(1+x^2)),x*e^(-x)/sqrt(1+x^2)` | WRONG | "int (IF)Q dx is not elementary" but IF·Q = e^(-t); the unsimplified e^(ln...) IF blocks the integral |
| 16e | 2 | P at 37 min, both models | `CALC » Calculate » 10*(37/60)/sqrt(1+(37/60)^2)` | OK | ⇒ "5.25" |
| 16e | | | `CALC » Calculate » (10*(37/60)-(37/60)*e^(-37/60))/sqrt(1+(37/60)^2)` | OK | ⇒ "4.97" |

Parts: 39. Rows: OK 22, WRONG 1, AWKWARD 11, GAP 6, none 5.
