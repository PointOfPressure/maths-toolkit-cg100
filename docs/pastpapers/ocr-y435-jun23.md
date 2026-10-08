# OCR Y435 Extra Pure, June 2023 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 7 | stationary points | `fxpure » Stationary points » 3x^3+6x*y+y^2` | OK | ⇒ "(2, -6, -12) min" |
| 2a | 7 | 4t(n+1) - t(n) = 15n + 17, t1 = 2 | `fxpure » 1st order a u + f(n) » 1/4,(15n+17)/4,2,1` | OK | ⇒ "u(n) = -8*(1/4)^n + 5*n - 1" |
| 2b(i) | 1 | explain non-linear | — | none | |
| 2b(ii) | 5 | find a, b; verify u = an + b/n | `fxpure » Verify u(n+1)=F(n,u) » (u^2+2n-1/n^2)/(n+1),n+1/n` | AWKWARD | ⇒ "LHS - RHS simplifies to 0 exactly"; verifies once a = b = 1 are guessed; no "fit a, b in a given form" |
| 2c | 2 | lim t(n)/u(n) = 5 | `fxpure » Associated sequence » (u+15n+17)/4,2,u/(n+1/n)` | AWKWARD | "w(n) does not settle by n = 400" (w(400) = 5); `CAS limit` on (5x-1-8·4^-x)/(x+1/x) "limit not found" |
| 3 | 8 | normal at (1,1,-1/9) | `fxpure » grad g, normal, plane » 2x^3-x^2*y+2x*y^2+27z,1,1,-1/9` | OK | ⇒ "grad g = (6, 3, 27)" |
| 3 | | tangent plane at (3,3,-3) | `fxpure » grad g, normal, plane » 2x^3-x^2*y+2x*y^2+27z,3,3,-3` | OK | ⇒ "tangent plane: 2x + y + z = 6" |
| 3 | | intersection P | `fcore » Line meets plane » 1,1,-1/9,6,3,27,2,1,1,6` | OK | ⇒ "meets at (13/9, 11/9, 17/9)" |
| 4a | 5 | group proof | — | none | |
| 4b(i) | 2 | closure of A_n | — | none | symbolic n; numeric product A1 A2 = A3 only a spot check |
| 4b(ii) | 2 | subgroup? | — | none | |
| 4c(i) | 2 | {I, -I} | `fcore » AB and BA (2x2) » -1,0,0,-1,-1,0,0,-1` | OK | ⇒ "AB = [1 0]" |
| 4c(ii) | 2 | uniqueness | — | none | |
| 4d | 2 | example | — | none | |
| 5a | 8 | eigenvectors in a, angle pi/4 | `fxpure » Eigen 2x2 » 1,0,2,3` | GAP | letter a refused; only checks a = 1 and a = 5 after solving a^2 - 6a + 13 = 8 by hand |
| 5a | | check angle | `fcore » Angle between lines » 1,1,0,0,1,0` | OK | ⇒ "angle = pi/4 rad" |
| 5b(i) | 4 | C-H gives a = -1/3, r = -8/3 | `fxpure » Cayley-Hamilton 2x2 » -1/3,0,2,3,4` | GAP | a must be known; once a = -1/3: ⇒ M^2 = (8/3)M + I |
| 5b(ii) | 3 | P^4 = sI + tP | `fxpure » Cayley-Hamilton 2x2 » -1/3,0,2,3,4` | OK | ⇒ "M^4 = (656/27)M + (73/9)I" |

Parts: 15. Rows: OK 8, WRONG 0, AWKWARD 2, GAP 2, none 6.
