# OCR Y435 Extra Pure, November 2021 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 4 | section x = 2, turning point, intercepts | `fxpure » Sections x = k » x^3+x^2*y-2y^2,2` | OK | ⇒ "x = 2: z = -2*y^2+4*y+8" |
| 1a | | turning point | `CAS » stationary points » 8+4x-2x^2` | OK | ⇒ "(1, 10)  max"; retype section with x for y |
| 1a | | intercepts | `CAS » solve exact f(x)=0 » 8+4x-2x^2` | OK | ⇒ "x = sqrt(5)+1" |
| 1b | 7 | stationary points of x^3 + x^2 y - 2y^2 | `fxpure » Stationary points » x^3+x^2*y-2y^2` | WRONG | reports "1 stationary point (0, 0, 0)"; misses (-6, 9, -54) although it lies inside the stated search box (x, y within ±10) |
| 2a | 1 | Lagrange | — | none | |
| 2b | 2 | generators of order-4 subgroup | `fxpure » Z_n under + mod n » 8` | OK | ⇒ "ord(2)=4"; g^2, g^6 read from ord(2) = ord(6) = 4 |
| 2c | 4 | all isomorphisms Z8 -> G | `fxpure » Z_n under + mod n » 8` | AWKWARD | ⇒ "generators: 1, 3, 5, 7"; `Isomorphism G to H` gives one map only; the four maps g -> 1, 3, 5, 7 by hand |
| 3a | 3 | characteristic equation | `fxpure » Eigen 3x3 » 3,3,0,0,2,2,1,3,4` | OK | ⇒ "char eq: L^3-9L^2+20L-12 = 0" |
| 3b | 1 | verify 1, 2, 6 | `fxpure » Eigen 3x3 » 3,3,0,0,2,2,1,3,4` | OK | ⇒ "L = 6, v = (1, 1, 2)" |
| 3c | 4 | eigenvectors | `fxpure » Eigen 3x3 » 3,3,0,0,2,2,1,3,4` | OK | ⇒ "L = 1, v = (3, -2, 1)" |
| 3d | 6 | A^n as one matrix in n | `fxpure » Diagonalise 3x3 M^n » 3,3,0,0,2,2,1,3,4` | AWKWARD | ⇒ "D = diag(1, 2, 6)"; gives P, D, P^-1 and numeric M^k, but never P D^n P^-1 with n left as a letter |
| 4a | 6 | general solution | `fxpure » 2nd order + f(n) » 3,10,24n-10,6,10` | OK | ⇒ "p(n) = -2*n + 1"; GS shown via CF A r1^n + B r2^n |
| 4b | 3 | particular solution | `fxpure » 2nd order + f(n) » 3,10,24n-10,6,10` | OK | ⇒ "u(n) = 3*5^n + 2*(-2)^n - 2*n + 1" |
| 4c | 1 | u2 check | `fxpure » Verify u(n+2)=F(n,u,v) » 3v+10u+24n-10,1-2n+3*5^n+2*(-2)^n` | OK | ⇒ "n=0: LHS 80, RHS 80" |
| 4d | 4 | p = 5, q = 3 | `fxpure » Ratio u(n+1)/u(n) » 3,10,6,10` | OK | ⇒ "u(n+1)/u(n) -> 5" |
| 4d | | q as limit | `CAS » limit x -> a » (1-2x+3*5^x+2*(-2)^x)/5^x ; inf` | AWKWARD | "limit not found"; q = 3 read off the coefficient by hand |
| 5 | 6 | tangent planes at angle pi/3 lie in z = 3 | `fxpure » grad g, normal, plane » x^2+y^2+2z^2,3,9,3` | GAP | grad at one numeric point only; no tool to solve the angle condition over the surface (MS z = 3) |
| 6a | 3 | geometric series bound | — | none | proof |
| 6b | 2 | S not integer | — | none | |
| 6c | 3 | e irrational | — | none | |

Parts: 17. Rows: OK 11, WRONG 1, AWKWARD 3, GAP 1, none 4.
