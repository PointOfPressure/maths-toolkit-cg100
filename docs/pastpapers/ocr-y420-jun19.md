# OCR Y420 Core Pure, June 2019 — calculator audit

Tool column: `module » label » inputs` (inputs exactly as typed). `CAS » op » f(x) ; ask` and `CALC » Calculate » expr` are the home-screen apps. OK rows carry `⇒ "substring"` that the output contains.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 4 | sum of 2r^2-1 | `fcore » Sum f(r), r = a..b » 2r^2-1,1` | OK | ⇒ "2*n^3/3+n^2-2*n/3" |
| 1 | | factorise S(n) | `CAS » factorise » 2x^3/3+x^2-2x/3` | AWKWARD | ⇒ "(2*x-1)*x*(x+2)/3"; Sum tool gives expanded form only, retype into CAS; b=n rejected ("b: unknown n") |
| 2 | 3 | n1.n2 = 0 with unknown c | `fcore » Angle between planes » 1,2,c,2,-c,6` | GAP | vectors refuse letters ("n1: unknown c"); hand dot product then `CAS » solve f(x)=0 » 2-2x+6x` gives -0.5 (decimal, MS ½) |
| 3a | 5 | AB, (AB)^-1, B^-1 A^-1 with k | `fcore » Inverse 2x2 » k,1,2,0` | GAP | matrix fields refuse a letter ("A: unknown k"); only numeric k can be checked |
| 3a | | A^-1 | `fcore » Inverse 2x2 » 3,1,2,1` | OK | ⇒ "[1 -1]" |
| 3b | 2 | AB vs BA in k | `fcore » AB and BA (2x2) » 3,1,2,1,5,1,2,0` | GAP | needs symbolic k to find k = 2; numeric only |
| 4 | 3 | volume pi int sec^2(x/2) | `fcalc » Volume about x-axis » sec(x/2),0,pi/2` | OK | ⇒ "V = 2pi" |
| 5 | 5 | sin^2 x series | `fcore » Maclaurin series » sin(x)^2,6` | OK | ⇒ "2*x^6/45-x^4/3+x^2"; MS route via cos 2x not shown |
| 6 | 4 | int 2..inf 1/(4+x^2) | `fcalc » Integral to infinity » 1/(4+x^2),2` | OK | ⇒ "integral = pi/8" |
| 7a | 2 | cartesian -> polar equation | — | GAP | no tool substitutes x = r cos t, y = r sin t into an equation |
| 7b | 3 | sketch | — | none | sketch |
| 7c | 3 | area of loop, r^2 = c^2 sin 2t | `fcalc » Polar area » sqrt(sin(2x)),0,pi/2` | OK | ⇒ "area = 1/2"; c = 1, times c^2 by hand |
| 8a | 6 | roots a, 1/a, b: product gives b = 2, then solve | `fcore » Cubic real coeffs » 1,-1,-1,-2` | AWKWARD | ⇒ "z2 = -1/2+sqrt(3)i/2"; no "roots a, 1/a" tool, k must be found by hand first; `Cubic real coeffs » 1,-1,?,-2` gives raw Python error "int() argument must be ... NoneType" |
| 8b | 2 | k from Vieta | `fcore » Vieta root sums » 1,-1,k,-2` | GAP | coeffs refuse letters; k = -1 by hand |
| 9 | 7 | induction 5^n + 2x11^n div by 3 | `fcore » Induction: divisor » 5^n+2*11^n,3` | OK | ⇒ "3 divides f(n): proved" |
| 10a | 3 | (-1+i)^3 | `fcore » De Moivre z^n » -1+i,3` | OK | ⇒ "z^3 = 2+2i" |
| 10b | 4 | cube roots of 2+2i in r e^(i t) | `fcore » nth roots of z » 2+2i,3` | AWKWARD | mod w = sqrt(2) and "args (pi/4 + 2pi k)/3" exact, but each root printed as decimal a+bi (1.37+0.366i); MS wants sqrt2 e^(i pi/12) etc. per root |
| 10c | 1 | explain | — | none | |
| 11a | 4 | describe M1, M2 | `fcore » Describe a 2x2 » 3/5,-4/5,4/5,3/5` | OK | ⇒ "rotation 53.1 deg about O" |
| 11a | | | `fcore » Describe a 2x2 » 1,0,0,-1` | OK | ⇒ "reflection in the x-axis" |
| 11b | 5 | M3 = M1 M2, mirror line | `fcore » A then B (2x2) » 1,0,0,-1,3/5,-4/5,4/5,3/5` | OK | ⇒ "[3/5 4/5]"; says "y = x tan 26.6 deg" |
| 11b | | mirror line exact | `fcore » Invariant points/lines » 3/5,4/5,4/5,-3/5` | OK | ⇒ "line of invariant points y = 1/2x" |
| 11c | 3 | M4 = M2 M1, its line | `fcore » Describe a 2x2 » 3/5,-4/5,-4/5,-3/5` | OK | ⇒ "reflection in y = x tan -26.6 deg" |
| 12 | 9 | three intersections | `fcore » Intersect two lines » 0,0,0,2,3,1,1,2,-4,1,1,5` | OK | ⇒ "they meet at (2, 3, 1)" |
| 12 | | | `fcore » Intersect two lines » 0,0,0,1,2,-4,1,2,-4,1,1,5` | OK | ⇒ "they meet at (1, 2, -4)" |
| 12 | | triangle area | `fcore » Area of triangle » 0,0,0,2,3,1,1,2,-4` | OK | ⇒ "area = sqrt(278)/2" |
| 13a | 5 | d/dx arcosh from ln form | `CAS » d/dx » ln(x+sqrt(x^2-1))` | AWKWARD | gives (x/sqrt(x^2-1)+1)/(x+sqrt(x^2-1)); `simplify` leaves it unchanged, never reaches 1/sqrt(x^2-1) |
| 13a | | | `fcalc » d/dx hyperbolic » acosh(x)` | OK | ⇒ "1/sqrt(x^2-1)" (result only) |
| 13b | 5 | int 1..2 arcosh x | `CAS » definite integral a..b » acosh(x) ; 1,2` | AWKWARD | ⇒ "2*acosh(2)-sqrt(3)"; MS wants log form 2ln(2+sqrt3)-sqrt3; no acosh->ln conversion |
| 13c | 1 | explain | — | none | |
| 14a(i) | 4 | det in a and b | `fcore » Det 3x3 in terms of k » -1,a,0,2,3,1,1,k,1` | GAP | one letter only ("use one letter, e.g. k"); needs two parameters |
| 14a(ii) | 3 | c for a sheaf | `fcore » Three planes » -1,1,0,2,2,3,1,-3,1,4,1,-1` | AWKWARD | ⇒ "sheaf: the planes share a line"; only by trying a numeric a and guessing c; no symbolic consistency condition |
| 14b | 6 | intersection in terms of a | `fcore » Three planes » -1,2,0,2,2,3,1,-3,1,2,1,1` | AWKWARD | ⇒ "(-10/3, -2/3, 17/3)"; numeric a = 2 checks MS ((-6-2a)/3, -2/3, (4a+9)/3) but no symbolic answer |
| 15 | 8 | int 1/sqrt(4x^2-4x+2), exact | `CAS » definite integral a..b » 1/sqrt(4x^2-4x+2) ; 3/4,3/2` | AWKWARD | "integral = 0.481, numeric (Simpson)"; matches ½ln((3+sqrt5)/2) only numerically |
| 15 | | complete the square | `CAS » complete the square » 4x^2-4x+2` | OK | ⇒ "4*(x-1/2)^2+1" |
| 15 | | arsinh after u = 2x-1 | `fcalc » Int 1/sqrt(x2+a2) » 1,1/2,2` | AWKWARD | "integral = 0.962" decimal; shows arsinh(2) - arsinh(1/2) but not the ln form or the ½ |
| 16a | 3 | (2-e^it)(2-e^-it) | `CAS » expand » (2-e^(i*x))*(2-e^(-i*x))` | AWKWARD | gives -2e^(ix)-2e^(-ix)+5; no e^(ix)+e^(-ix) = 2cos x step |
| 16b | 9 | C + iS as a GP, real part | `mpure » Sigma sum f(r) a..b » cos(r)/2^r,1,5` | AWKWARD | ⇒ "sum = 0.0104"; numeric check of the formula at t = 1, n = 5 only (`fcore » Sum f(r)` refuses: "f(r) must be a polynomial in r"); no complex GP sum tool |
| 17a | 1 | explain | — | none | |
| 17b | 1 | N2L | — | none | |
| 17c(i) | 5 | dv/dt + 0.1v = -2, v(10) = 0 | `fcalc » Integrating factor » 0.1,-2,10,0` | AWKWARD | ⇒ "C = 54.4"; constant decimal, MS 20e (v = 20(e^(1-0.1t)-1)); variable must be x |
| 17c(ii) | 1 | v(5) | `CALC » Calculate » 20*(e^0.5-1)` | OK | ⇒ "12.97442541" |
| 17d | 1 | N2L | — | none | |
| 17e(i) | 5 | dv/dt + 0.1v = k t, v(0) = 0 | `fcalc » Integrating factor » 0.1,k*x,0,0` | WRONG | GS right but initial condition fails: "the point is outside the domain" when Q has a letter |
| 17e(i) | | with k = 1 | `fcalc » Integrating factor » 1/10,x,0,0` | OK | ⇒ "C = 100" |
| 17e(ii) | 2 | solve for lambda | `CAS » solve f(x)=0 » 20*(e^0.5-1)-10x*(5-10+10*e^(-0.5))` | OK | ⇒ "x = 1.22" |
| 17f | 6 | distance: two integrals | `CAS » definite integral a..b » 20*(e^(1-0.1x)-1) ; 5,10` | OK | ⇒ "200*sqrt(e)-300"; with s1 = 22.49 from the other integral, total 52 m |

Parts: 37. Rows: OK 22, WRONG 1, AWKWARD 12, GAP 6, none 6.
