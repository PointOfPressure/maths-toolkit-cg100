# OCR Y420 Core Pure, June 2025 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 4 | z + 2i z* + 1 - 4i = 0 | `fcore » Solve az + bz* = c » 1,2i,-1+4i` | OK | ⇒ "z = 3-2i" |
| 2 | 4 | angle between planes | `fcore » Angle between planes » 2,-1,2,1,2,1` | OK | ⇒ "= 74.2 deg" |
| 3 | 5 | sum r(r+2) | `fcore » Sum f(r), r = a..b » r(r+2),1` | OK | ⇒ "n^3/3+3*n^2/2+7*n/6" |
| 3 | | factorise, a = 2, b = 7 | `CAS » factorise » x^3/3+3x^2/2+7x/6` | AWKWARD | ⇒ "(2*x+7)*x*(x+1)/6"; retype |
| 4a | 1 | rule | — | none | |
| 4b | 6 | verify (MN)^-1 = N^-1 M^-1 with a, b | `fcore » Inverse 2x2 » a,1,0,1` | GAP | "A: unknown a"; symbolic 2x2 algebra missing; only numeric spot checks |
| 5 | 4 | roots ½(a+1) | `fcore » Roots p a + q » 1/2,1/2,2,0,-3,4` | AWKWARD | gives 2x^3-3x^2+(3/4)x+(5/8); MS 16y^3-24y^2+6y+5 = 0: not scaled to integer coefficients |
| 6a | 3 | cartesian -> polar | — | GAP | no curve-equation conversion (x = r cos t, y = r sin t) |
| 6b | 2 | max r | `fcalc » Plot r = f(theta) » sqrt(sin(2x)/2)` | OK | ⇒ "= sqrt(2)/2 at th = pi/4" |
| 6c | 4 | loop area | `fcalc » Polar area » sqrt(sin(2x)/2),0,pi/2` | OK | ⇒ "area = 1/4" |
| 7 | 8 | partial fractions | `CAS » partial fractions » 1/(x^2-4)` | AWKWARD | "1/4/(x-2)", "-1/4/(x+2)": odd nested-fraction display |
| 7 | | int 3..inf = ¼ ln 5 | `fcalc » Integral to infinity » 1/(x^2-4),3` | AWKWARD | "integral = 0.402" numeric; antiderivative shown but log limit not taken exactly |
| 8a | 4 | induction on nth derivative | `fcore » Induction: sum » (-1)^(r+1)*(r-1)!,1` | GAP | no "induction: nth derivative" tool; CAS d/dx of the formula with n works (-(-1)^(n+1)(n-1)!(x+1)^(-n-1) n) but not simplified |
| 8b | 3 | Maclaurin from f^(n)(0) | `fcore » Maclaurin series » ln(1+x),5` | OK | ⇒ "term r: (-1)^(r+1) x^r/r" |
| 9a(i) | 1 | w^2, w^3, w^4 | — | none | |
| 9a(ii) | 1 | z^5 = 1 | — | none | |
| 9a(iii) | 2 | sum zero | `fcore » Roots of unity » 5` | OK | ⇒ "1 + w + ... + w^4 = 0" |
| 9b(i) | 1 | w | `fcore » Roots of unity » 5` | OK | ⇒ "w = e^(2pi i/5)" |
| 9b(ii) | 5 | side = 2 sin(pi/5) | `fcore » Polygon: centre+vertex » 0,1,5` | AWKWARD | ⇒ "side = 1.18"; decimal only, matches 2sin(pi/5) = 1.1756 numerically |
| 10 | 4 | int 0..½ 2/(x^2-x+1) | `CAS » definite integral a..b » 2/(x^2-x+1) ; 0,1/2` | OK | ⇒ "2*pi*sqrt(3)/9" |
| 11a | 6 | a from perpendicular, then b, then point | `fcore » Intersect two lines » 3,-1,2,2,-10,1,2,1,3,-1,0,2` | GAP | letters a, b refused; only checks a = 2, b = -10 once found ⇒ (13/5, 1, 9/5) |
| 11b(i) | 3 | a, b for parallel | — | none | by inspection |
| 11b(ii) | 5 | distance between parallel lines | `fcore » Distance two lines » 3,-1,2,-1/2,2,1,2,1,3,-1,4,2` | OK | ⇒ "distance = 0.488"; decimal (MS sqrt(5/21)) |
| 12 | 8 | roots a, 2/a, b, -b, c and d | `fcore » Quartic real coeffs » 1,-1,11,-9,18` | GAP | no root-relationship tool; only checks c = 11, d = -9 ⇒ ±3i, (1±sqrt7 i)/2 |
| 13a | 3 | IF x^-2 | `fcalc » Integrating factor » -2/x,(2+x^2)/x,1,0` | OK | ⇒ "1/x^2" |
| 13b | 8 | y, then stationary point exact | `fcalc » Integrating factor » -2/x,(2+x^2)/x,1,0` | OK | ⇒ "(ln(\|x\|)-1/x^2+1)*x^2" |
| 13b | | 2x ln x + 3x = 0 | `CAS » solve exact f(x)=0 » 2x*ln(x)+3x` | AWKWARD | "x = 0.22313, numeric roots - no exact form"; MS e^(-3/2) |
| 14a | 2 | identity | `fcalc » Identity check at x » 0.7` | AWKWARD | numeric only |
| 14b | 6 | rhombus, unit area | `fcore » Determinant 2x2 » cosh(0.7),sinh(0.7),sinh(0.7),cosh(0.7)` | AWKWARD | ⇒ "det A = 1"; numeric x only; no image-of-square / side-length tool |
| 14c | 2 | cosh 2x = 4 | `CAS » solve exact f(x)=0 » cosh(2x)-4` | OK | ⇒ "x = ln(sqrt(15)+4)/2" |
| 15a | 2 | (3-e^4it)(3-e^-4it) | `CAS » expand » (3-e^(4i*x))*(3-e^(-4i*x))` | AWKWARD | -3e^(4ix)-3e^(-4ix)+10; not 10-6cos 4t |
| 15b | 4 | C + iS as GP | — | GAP | no complex GP sum |
| 15c | 3 | real part | `mpure » Sigma sum f(r) a..b » cos((4r+1)*0.5)/3^r,0,40` | AWKWARD | ⇒ "sum = 0.615"; numeric check at t = 0.5 only |
| 16a | 6 | area int 0..4 (x+3)/sqrt(x^2+9) = 2 + ln 27 | `CAS » definite integral a..b » (x+3)/sqrt(x^2+9) ; 0,4` | AWKWARD | "integral = 5.3, numeric (Simpson)"; no arsinh antiderivative for x/sqrt + 3/sqrt split |
| 16b | 6 | volume pi(4 + 3 ln(25/9)) | `CAS » definite integral a..b » (x+3)^2/(x^2+9) ; 0,4` | AWKWARD | ⇒ "3*ln(25)-3*ln(9)+4"; logs not combined; `Volume about x-axis` prints V = 22.2 only |
| 17a(i) | 1 | DE | — | none | |
| 17a(ii) | 1 | dh/dt = 0 | — | none | |
| 17a(iii) | 4 | solve, h(0) = 0 | `fcalc » Integrating factor » 0.2,4,0,0` | OK | ⇒ "(20*e^(x/5)-20)*e^(-x/5)" |
| 17a(iii) | | separable route | `fcalc » Separable DE » 0.2,20-y,0,0` | AWKWARD | y = -e^(-(-ln(20)+x/5))+20; not simplified to 20(1-e^(-x/5)) |
| 17a(iv) | 2 | h(5) | `CALC » Calculate » 20(1-e^(-1))` | OK | ⇒ "12.64241118" |
| 17b(i) | 4 | h'' + 0.3h' + 0.02h = 0.4 | `fcalc » PI polynomial RHS » 1,0.3,0.02,0.4` | WRONG | "f(x) must be a polynomial in x" for the constant 0.4 (2/5 works); decimal RHS rejected |
| 17b(i) | | with 2/5 | `fcalc » PI polynomial RHS » 1,0.3,0.02,2/5` | OK | ⇒ "A*e^(-x/10)+B*e^(-x/5)+20" |
| 17b(ii) | 1 | limit 20 | — | none | |
| 17b(iii) | 5 | h(0) = 0, h'(0) = 2.9, h(5) | `fcalc » PI for k e^(px) » 1,0.3,0.02,0.4,0,0,2.9` | OK | ⇒ "-11*e^(-x/10)-9*e^(-x/5)+20"; (constant RHS via p = 0; shows "f(x) = 2/5 1") |
| 17b(iii) | | h(5) | `CALC » Calculate » 20-11e^(-0.5)-9e^(-1)` | OK | ⇒ "10.01724777" |

Parts: 39. Rows: OK 18, WRONG 1, AWKWARD 13, GAP 6, none 7.
