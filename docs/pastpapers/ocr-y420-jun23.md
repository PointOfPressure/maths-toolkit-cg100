# OCR Y420 Core Pure, June 2023 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a(i) | 1 | z* | — | none | symbolic a + ib, trivial |
| 1a(ii) | 2 | Re(iz) | — | none | symbolic, trivial |
| 1b(i) | 2 | w = (5+sqrt3 i)/(2-sqrt3 i) | `fcore » Arithmetic z, w » 5+sqrt(3)i,2-sqrt(3)i` | OK | ⇒ "z/w = 1+sqrt(3)i" |
| 1b(ii) | 2 | mod-arg | `fcore » Modulus-argument » 1+sqrt(3)i` | OK | ⇒ "z = 2(cos pi/3 + i sin pi/3)" |
| 2 | 5 | angle vector and plane | `fcore » Angle line and plane » 3,2,1,-1,3,2` | OK | ⇒ "= 20.9 deg" |
| 3a | 5 | sum 1/(r(r+2)) | `fcore » Method of differences » 1/(r(r+2))` | OK | ⇒ "S(n) = 3/4 - (1/(2*n+2)+1/(2*n+4))" |
| 3a | | target form, a = 2, b = 3 | `CAS » single fraction » 1/(2x+2)+1/(2x+4)` | AWKWARD | ⇒ "(x+3/2)/((x+1)*(x+2))"; retype the tail; = (2n+3)/(2(n+1)(n+2)) by hand |
| 3b | 1 | sum to infinity | `fcore » Method of differences » 1/(r(r+2))` | OK | ⇒ "S(n) -> 3/4" |
| 4a(i) | 2 | f', f'' | `CAS » d2/dx2 » sqrt(1+2x)` | OK | ⇒ "-1/((2*x+1)*sqrt(2*x+1))" |
| 4a(ii) | 2 | Maclaurin to x^2 | `fcore » Maclaurin series » sqrt(1+2x),2` | OK | ⇒ "-x^2/2+x+1" |
| 4b | 2 | sqrt5 ~ 143/64 using x = 1/8 | `CALC » Calculate » 2*(1+1/8-1/128)` | OK | ⇒ "143/64"; choosing x = 1/8 (sqrt5 = 2 sqrt(1+1/4)) is the hand step |
| 5a | 4 | sixth roots of -64 in r e^(it) | `fcore » nth roots of z » -64,6` | AWKWARD | roots in a+bi; MS 2e^(i pi/6) …; per-root exponential form missing |
| 5b | 3 | Argand diagram | — | none | sketch (Argand plot exists but this is drawing) |
| 6a | 3 | MN vs NM | `fcore » AB and BA (2x2) » 0,1,1,0,2,0,0,1` | OK | ⇒ "AB is not BA" |
| 6b(i) | 1 | describe M | `fcore » Describe a 2x2 » 0,1,1,0` | OK | ⇒ "reflection in y = x" |
| 6b(ii) | 2 | describe N | `fcore » Describe a 2x2 » 2,0,0,1` | OK | ⇒ "stretch parallel to x-axis, sf 2" |
| 6c | 1 | significance | — | none | |
| 6d | 2 | lines y = c invariant | `fcore » Invariant points/lines » 2,0,0,1` | AWKWARD | lists only lines through O (y = 0, x = 0); invariant lines y = mx + c not covered |
| 7a | 3 | r, t at A, B, C | `fcalc » Plot r = f(theta) » 1-2sin(x)` | OK | ⇒ "r(3pi/2) = 3"; r(pi/2) = -1 for B |
| 7b | 3 | inner loop r < 0 | `CAS » general solution (trig) » 1-2sin(x)` | OK | ⇒ "x = 2*n*pi+5*pi/6"; pi/6 < t < 5pi/6 read off |
| 8 | 5 | induction 8^n - 3^n | `fcore » Induction: divisor » 8^n-3^n,5` | OK | ⇒ "5 divides f(n): proved" |
| 9 | 6 | RMS: mean of sin^2 nt | `fcalc » Mean value of f » sin(2x)^2,0,pi` | OK | ⇒ "mean = 1/2"; n = 2, a = 1 only; RMS = a/sqrt2 by hand |
| 10a | 6 | roots a, b, a+b with c unknown | `fcore » Cubic real coeffs » 1,-4,7,-6` | GAP | needs root relationship (a+b = 2 so 2 is a root); tool only after c = -6 known: ⇒ 1±sqrt2 i |
| 10b | 1 | c | — | GAP | no "roots -> coefficient" / Vieta in reverse |
| 11 | 7 | IF, y(0) = 1 | `fcalc » Integrating factor » -2tanh(x),1,0,1` | OK | ⇒ "cosh(x)^2*(tanh(x)+1)" |
| 12 | 7 | sin^5 in multiple angles | `fcore » cos^n t, sin^n t » 5` | OK | ⇒ "sin^5 t = (sin5t-5sin3t+10sin t)/16" |
| 13a(i) | 3 | sketch | — | none | |
| 13a(ii) | 3 | sketch | — | none | |
| 13b | 8 | bisector meets circle | `fcore » Locus \|z-z1\|=\|z-z2\| » -2+4i,2+6i` | OK | ⇒ "y = -2x + 5" |
| 13b | | tangent point | `mpure » Line meets circle » -2,5,0,0,sqrt(5)` | OK | ⇒ "tangent at (2, 1)" |
| 14a | 5 | det never zero | `fcore » Det 3x3 in terms of k » k,0,-1,-1,k,2,2k,2,3` | OK | ⇒ "no real k makes it singular" |
| 14b | 8 | intersection in terms of k | `fcore » Det 3x3 in terms of k » k,0,-1,-1,k,2,2k,2,3` | AWKWARD | adjugate in k is printed, but adj·b / det by hand; `Solve 3 eqns by A^-1` numeric only (k = 1 check gives (-4/3, 19/3, -10/3)) |
| 15 | 5 | int 1..2 1/sqrt(1+2x-x^2) | `fcalc » Int 1/sqrt(a2-x2) » sqrt(2),0,1` | OK | ⇒ "integral = pi/4"; completing the square and u = x-1 by hand |
| 15 | | direct | `CAS » definite integral a..b » 1/sqrt(1+2x-x^2) ; 1,2` | OK | ⇒ "integral = pi/4" (Simpson value recognised) |
| 16 | 10 | b so distances equal | `fcore » Point to line dist » 4,1,0,3,1,-5,2,2,3` | GAP | vector fields refuse b; only checks b = 2 (both distances 3); no "solve for parameter" |
| 16 | | plane distance | `fcore » Point to plane dist » 4,1,0,2,1,2,0` | OK | ⇒ "distance = 3" |
| 17a(i) | 6 | GS with k, a, b letters | — | GAP | Coupled equations needs numbers |
| 17a(ii) | 2 | y GS | — | GAP | as above |
| 17b(i) | 3 | x with x0, y0 | `fcalc » Coupled equations » 0.015,-0.04,-0.01,0.015,500,300` | AWKWARD | ⇒ "550*e^(-t/200)-50*e^(7*t/200)"; letters x0, y0 not allowed, numeric check only |
| 17b(ii) | 1 | y | `fcalc » Coupled equations » 0.015,-0.04,-0.01,0.015,500,300` | AWKWARD | y printed unexpanded "-25*(-3*(11e…)/4 …)"; CAS expand gives 25e^(7t/200)+275e^(-t/200) |
| 17c(i) | 2 | numbers at t = 25 | `CALC » Calculate » -50e^(0.035*25)+550e^(-0.005*25)` | OK | ⇒ "365.4295317" |
| 17c(i) | | | `CALC » Calculate » 275e^(-0.005*25)+25e^(0.035*25)` | OK | ⇒ "302.6585306" |
| 17c(ii) | 4 | x = y | `CAS » solve f(x)=0 » -50e^(0.035x)+550e^(-0.005x)-275e^(-0.005x)-25e^(0.035x)` | WRONG | "no real roots found in the search range"; root t = 32.5 lies outside the fixed range; `solve exact` also "no solutions" (exact ln(11/3)/0.04) |
| 17c(ii) | | workaround | `mcalc » Newton-Raphson » -75e^(0.035x)+275e^(-0.005x),30` | OK | ⇒ "x = 32.482075" |
| 17c(iii) | 3 | sign of terms | — | none | reasoning |
| 17d(i) | 1 | x0 = 2y0 | — | none | |
| 17d(ii) | 2 | explain | — | none | |

Parts: 41. Rows: OK 26, WRONG 1, AWKWARD 6, GAP 5, none 9.
