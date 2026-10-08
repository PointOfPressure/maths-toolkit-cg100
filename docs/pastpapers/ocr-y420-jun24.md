# OCR Y420 Core Pure, June 2024 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 4 | single fraction, telescoping | `CAS » single fraction » 1/(x+1)-1/(x+2)` | OK | ⇒ "1/((x+1)*(x+2))" |
| 1 | | sum | `fcore » Method of differences » 1/((r+1)(r+2))` | OK | ⇒ "S(n) = 1/2 - (1/(n+2))" |
| 2a(i) | 1 | u - v | `fcore » Arithmetic z, w » -1+i,-2-i` | OK | ⇒ "z-w = 1+2i" |
| 2a(ii) | 3 | u/v | `fcore » Arithmetic z, w » -1+i,-2-i` | OK | ⇒ "z/w = 1/5-3i/5" |
| 2b | 3 | mod-arg of u | `fcore » Modulus-argument » -1+i` | OK | ⇒ "z = sqrt(2)(cos 3pi/4 + i sin 3pi/4)" |
| 3 | 4 | sum of squares of roots | `fcore » Vieta root sums » 2,-2,8,-15` | OK | ⇒ "sum of squares = e1^2 - 2e2 = -7" |
| 4 | 4 | V = pi int 0..k 1/(k^2+x^2) = 1, find k | `fcalc » Volume about x-axis » 1/sqrt(k^2+x^2),0,k` | GAP | "b: unknown k"; no volume with a parameter; hand pi^2/(4k) = 1 then `CAS solve` gives 2.47 (MS exact pi^2/4) |
| 5a | 3 | u x v with a, b | `fcore » Vector product » -2,1,2,-3,0,1` | GAP | letters refused; only checks a = -3 ⇒ (1, -4, 3) |
| 5b | 3 | angle via cross product | `fcore » Scalar product, angle » -2,1,2,-3,0,1` | OK | ⇒ "= 32.5 deg" |
| 6a | 3 | sketch | — | none | |
| 6b | 3 | sketch | — | none | |
| 7a | 1 | explain improper | — | none | |
| 7b | 4 | int 1..2 (x-2)^(-1/3) | `fcalc » Singular endpoint int » 1/(x-2)^(1/3),1,2` | WRONG | "both ends undefined"; x = 1 is fine (real cube root -1); the tool rejects negative bases with fractional powers |
| 7b | | | `CAS » definite integral a..b » (x-2)^(-1/3) ; 1,2` | OK | ⇒ "-3/2"; no limit argument shown |
| 8a | 2 | shear | `fcore » Describe a 2x2 » 1,3,0,1` | OK | ⇒ "shear, x-axis fixed, factor 3"; m = 3 standing in for m |
| 8b(i) | 1 | det | `fcore » Determinant 2x2 » 1,3,0,1` | OK | ⇒ "det A = 1" |
| 8b(ii) | 2 | properties | `fcore » Determinant 2x2 » 1,3,0,1` | OK | ⇒ "det > 0: orientation is preserved" |
| 8c | 4 | induction M^n with letter m | `fcore » Induction: M^n » 1,m,0,1,1,n*m,0,1` | AWKWARD | "A: unknown m"; works only with numeric m (`1,3,0,1,1,3n,0,1` proved) |
| 8d | 1 | shear factor nm | — | none | |
| 9a | 3 | sketch | — | none | |
| 9b | 5 | one loop of r = a sin 3t | `fcalc » Polar area » sin(3x),0,pi/3` | OK | ⇒ "area = pi/12"; a = 1 |
| 10a | 1 | ln(1+x^3) three terms | `fcore » Maclaurin series » ln(1+x^3),9` | WRONG | "n is 1..8": cap stops at x^8, so the x^9 term is lost (with n = 8 only x^3 - x^6/2) |
| 10a | | | `CAS » series (Maclaurin) » ln(1+x^3) ; 10` | OK | ⇒ "x^9/3-x^6/2+x^3" |
| 10b | 3 | x = 1/2 | `CALC » Calculate » 1/8-1/128+1/1536` | OK | ⇒ "181/1536" |
| 10c | 2 | explain | — | none | |
| 11a | 2 | distance P to plane | `fcore » Point to plane dist » 8,4,5,2,-1,2,4` | OK | ⇒ "distance = 6" |
| 11b | 2 | P on L | `fcore » Is p on (r-a)xb=0 » 2,0,-3,3,2,4,8,4,5` | OK | ⇒ "p is on the line" |
| 11c | 3 | L meets plane | `fcore » Line meets plane » 2,0,-3,3,2,4,2,-1,2,4` | OK | ⇒ "meets at (7/2, 1, -1)" |
| 11d | 4 | angle | `fcore » Angle line and plane » 3,2,4,2,-1,2` | OK | ⇒ "= 48 deg" |
| 11e | 3 | PQ sin(angle) = 6 | `CALC » Calculate » sqrt((8-7/2)^2+3^2+6^2)*sin(48.0*pi/180)` | OK | ⇒ "6.002936041" |
| 12a(i) | 4 | cosh t = 2 sinh t | `CAS » solve exact f(x)=0 » cosh(x)-2sinh(x)` | OK | ⇒ "x = ln(3)/2" |
| 12a(i) | | | `fcalc » Solve a cosh+b sinh=c » 1,-2,0` | AWKWARD | "x = ln((0 - sqrt(3))/-1)" — right value, unsimplified log |
| 12a(ii) | 2 | x at A | `CALC » Calculate » 2cosh(ln(3)/2)+sinh(ln(3)/2)` | OK | ⇒ "2.886751346" |
| 12b | 6 | tangent at t = 0 | `mcalc » Parametric dy/dx » 2cosh(t)+sinh(t),cosh(t)-2sinh(t),0` | OK | ⇒ "at t = 0: dy/dx = -2"; gives point (2, 1); line y = -2x + 5 by hand |
| 13a(i) | 1 | ratio | — | none | |
| 13a(ii) | 1 | angle | — | none | |
| 13b(i) | 2 | (3-e^it)(3-e^-it) | `CAS » expand » (3-e^(i*x))*(3-e^(-i*x))` | AWKWARD | gives -3e^(ix)-3e^(-ix)+10; no 10 - 6cos t |
| 13b(ii) | 6 | sum of GP, imaginary part | `mpure » Sigma sum f(r) a..b » sin(r*0.9)/3^r,1,40` | AWKWARD | ⇒ "sum = 0.375"; numeric check only at t = 0.9 |
| 14a | 7 | y'' + y' - 2y = 12e^-x | `fcalc » PI for k e^(px) » 1,1,-2,12,-1` | OK | ⇒ "A*e^(x)+B*e^(-2*x)-6*e^(-x)" |
| 14b | 5 | B = 0 (y -> 0), y'(0) = 0, then y = 0 | `fcalc » PI for k e^(px) » 1,1,-2,12,-1,?,?` | AWKWARD | conditions y -> 0 at infinity and y'(0) = 0 alone are not inputs (needs y0 and v0); A = 3 by hand |
| 14b | | solve | `CAS » solve exact f(x)=0 » 3e^(-2x)-6e^(-x)` | OK | ⇒ "x = -ln(2)" |
| 15a | 4 | det in k | `fcore » Det 3x3 in terms of k » 1,k,3,3,4,2,1,3,-1` | OK | ⇒ "singular when k = -1" |
| 15b | 6 | y independent of k | `fcore » Solve 3 eqns by A^-1 » 1,2,3,3,4,2,1,3,-1,1,3,-2` | AWKWARD | ⇒ "y = -7/5"; numeric k only (k = 2, 5 both give -7/5); symbolic solve missing, adjugate in k printed by the det tool |
| 16 | 6 | int 0..1 1/sqrt(x^2+x+1) = ln((a+b sqrt3)/c) | `fcalc » Int 1/sqrt(x2+a2) » sqrt(3)/2,1/2,3/2` | AWKWARD | "integral = 0.768"; arsinh(sqrt3) - arsinh(sqrt3/3) shown, not combined into ln((3+2sqrt3)/3) |
| 17a(i) | 1 | show | — | none | |
| 17a(ii) | 3 | show | — | none | |
| 17b | 8 | IF solution | `fcalc » Integrating factor » 1/(200-x),10,0,0` | AWKWARD | right curve but "C = 53" (= 10 ln 200) decimal; not in the form 10(200-t)ln(200/(200-t)) |
| 17c(i) | 2 | t = 100 | `CALC » Calculate » 10*100*ln(2)` | OK | ⇒ "693.1471806" |
| 17c(ii) | 5 | max of x(t) | `CAS » stationary points » 10(200-x)ln(200/(200-x))` | WRONG | "no stationary points found in the search range" (fixed -20..20); max at t = 126.4; mcalc Stationary points same ("none in -20 <= x <= 20") |
| 17c(ii) | | workaround | `mcalc » Newton-Raphson » -10ln(200/(200-x))+10,100` | OK | ⇒ "x = 126.42411" |
| 17d | 1 | suggest | — | none | |

Parts: 45. Rows: OK 27, WRONG 3, AWKWARD 8, GAP 2, none 11.
