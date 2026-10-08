# OCR Y435 Extra Pure, June 2022 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 7 | behaviour of a(n) | `fxpure » Behaviour u(n+1)=F » 2+3/(2-u),3` | OK | ⇒ "periodic, period 2" |
| 1 | | b(n) | `fxpure » Behaviour u(n+1)=F » -u/2+3,1.5` | OK | ⇒ "convergent: u(n) -> 2" |
| 1 | | c(n) with c(n+1) = c(n)^2/n + 1, c1 = 2.5 | `fxpure » Behaviour u(n+1)=F » u^2/n+1,2.5` | AWKWARD | "F undefined at u(0)": sequence always starts at n = 0, no start index; shifting to u^2/(n+1)+1 by hand gives "divergent … increasing" |
| 2a | 3 | characteristic equation | `fxpure » Eigen 3x3 » 10,12,-8,-1,2,4,3,6,2` | OK | ⇒ "char eq: L^3-14L^2+56L-64 = 0" |
| 2b | 5 | Cayley-Hamilton inverse | `fxpure » Cayley-Hamilton 3x3 » 10,12,-8,-1,2,4,3,6,2` | OK | ⇒ "M^-1 = (M^2 - 14M + 56I)/64" |
| 2c | 4 | D | `fxpure » Diagonalise 3x3 M^n » 10,12,-8,-1,2,4,3,6,2` | OK | ⇒ "D = diag(2, 4, 8)" |
| 3a | 6 | 5t(n+1) - 4t(n) = 3n^2 + 28n + 6 | `fxpure » 1st order a u + f(n) » 4/5,(3n^2+28n+6)/5,7` | OK | ⇒ "u(n) = 6*(4/5)^n + 3*n^2 - 2*n + 1"; divide by 5 by hand |
| 3b(i) | 1 | lim t(n)/n^3 | `CAS » limit x -> a » (6*0.8^x+3x^2-2x+1)/x^3 ; inf` | AWKWARD | "limit not found"; 0 by inspection |
| 3b(ii) | 1 | lim t(n)/n^2 | `fxpure » Associated sequence » (4u+3n^2+28n+6)/5,7,u/n^2` | AWKWARD | "w(n) does not settle by n = 400" though w(400) = 3; CAS limit also "limit not found" |
| 3b(iii) | 1 | t(n)/n diverges | — | AWKWARD | by inspection; no limit tool succeeds on 0.8^n + polynomial |
| 4a | 5 | find k1, k2, k3 | — | none | algebraic deduction |
| 4b | 1 | e = -2 | — | none | |
| 4c | 1 | commutative | — | none | |
| 4d | 6 | group axioms for a + b + 2 on R | — | GAP | group tools need a finite table; no check for an infinite set with a formula operation |
| 4e | 3 | subsets | — | none | |
| 5a(i) | 1 | df/dx | `fxpure » Partial derivatives » y*e^(-(x^2+2x+2)y)` | OK | ⇒ "dz/dx = -(2*x+2)*e^(-(x^2+2*x+2)*y)*y^2" |
| 5a(ii) | 1 | df/dy | `fxpure » Partial derivatives » y*e^(-(x^2+2x+2)y)` | OK | ⇒ "dz/dy =" (unfactorised; MS -(x^2y+2xy+2y-1)e^(…)) |
| 5a(iii) | 4 | stationary points | `fxpure » Stationary points » y*e^(-(x^2+2x+2)y)` | WRONG | ⇒ "(-1, 1, 0.368) max" correct, but also lists a false point "(6.86, 7.27, 0) D = 0" where the gradient has only underflowed |
| 5b | 2 | transformations of e^(-x^2) | — | none | |
| 5c | 1 | sketch section y = 1 | `fxpure » Sections y = k » y*e^(-(x^2+2x+2)y),1` | OK | ⇒ "y = 1: z = e^(-(x^2+2*x+2))" |
| 5d | 2 | classify | `fxpure » Stationary points » y*e^(-(x^2+2x+2)y)` | OK | ⇒ "max" |
| 5e | 4 | tangent plane where z = 0 | `fxpure » Tangent plane z=f » y*e^(-(x^2+2x+2)y),0,0` | OK | ⇒ "z = y" |
| 5f | 1 | line of intersection | — | none | read off |

Parts: 21. Rows: OK 11, WRONG 1, AWKWARD 4, GAP 1, none 6.
