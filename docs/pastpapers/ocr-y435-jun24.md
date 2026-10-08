# OCR Y435 Extra Pure, June 2024 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 5 | stationary point | `fxpure » Stationary points » 12x-30y+6x*y` | OK | ⇒ "(5, -2, 60) saddle" |
| 1b | 3 | a, b with f(x, a) = 24x + b | `fxpure » Sections y = k » 12x-30y+6x*y,2` | AWKWARD | ⇒ "y = 2: z = 24*x-60"; letter a refused, so a = 2 is found by trial or by hand |
| 1c | 3 | asymptotes of contour z = 12 | `fxpure » Contours z = c » 12x-30y+6x*y,12` | GAP | only axis crossings ("cuts y=0 at x = 1"); no asymptotes of a contour (MS x = 5, y = -2) |
| 1d | 3 | tangent plane via grad g at (3, 2) | `fxpure » grad g, normal, plane » 12x-30y+6x*y-z,3,2,12` | OK | ⇒ "tangent plane: 24x - 12y - z = 36" |
| 1e | 3 | normal at A meets plane | `fxpure » grad g, normal, plane » 12x-30y+6x*y-z,0,4,-120` | OK | ⇒ "grad g = (36, -30, -1)" |
| 1e | | intersection | `fcore » Line meets plane » 0,4,-120,36,-30,-1,3,3,-2,52` | OK | ⇒ "meets at (-360, 304, -110)" |
| 2a | 2 | GS of 2u(n+2) - 7u(n+1) + 3u(n) = 0 | `fxpure » 2nd order homogeneous » 7/2,-3/2,0,1` | OK | ⇒ "roots 3, 1/2"; needs dummy u0, u1 to run; GS read from "CF: A r1^n + B r2^n" |
| 2b | 5 | GS with 20n^2 + 60n | `fxpure » 2nd order + f(n) » 7/2,-3/2,10n^2+30n,-9,-12` | OK | ⇒ "p(n) = -10*n^2 - 5"; divide through by 2 by hand |
| 2c | 3 | particular solution | `fxpure » 2nd order + f(n) » 7/2,-3/2,10n^2+30n,-9,-12` | OK | ⇒ "A = 2, B = -6" |
| 2d | 2 | least term | `fxpure » 2nd order + f(n) » 7/2,-3/2,10n^2+30n,-9,-12` | OK | ⇒ "-167/4" (u3 = -41.75) |
| 3a | 3 | compositions | `fxpure » Symmetries of n-gon » 3` | AWKWARD | ⇒ "D3: order 6, not abelian"; table uses r, s with lines at 0/60/120 deg, so matching Ma, Mb, Mc to the question's labels is by hand |
| 3b | 4 | complete table | `fxpure » Symmetries of n-gon » 3` | AWKWARD | table given in its own labels/order; no relabelling |
| 3c | 1 | no subgroup of order 4 | `fxpure » Subgroups, Lagrange » 6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0` | OK | ⇒ "1 2 3 6, index" |
| 3d | 3 | counter-claim | `fxpure » Subgroups, Lagrange » 6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0` | OK | ⇒ "{0,1,2} order 3"; all proper subgroups listed (orders 2, 3, so abelian) while G is not |
| 3e | 1 | no element of order 6 | `fxpure » Element orders » 6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0` | OK | ⇒ "not cyclic: no element of order 6" |
| 4a | 3 | characteristic equation | `fxpure » Eigen 3x3 » 1,7,8,-6,12,12,-2,4,8` | OK | ⇒ "char eq: L^3-21L^2+126L-216 = 0" |
| 4b(i) | 2 | verify eigenvector | `fxpure » Is v eigenvector 3x3 » 1,7,8,-6,12,12,-2,4,8,1,-2,2` | OK | ⇒ "yes: Mv = 3v, L = 3" |
| 4b(ii) | 3 | eigenvector for 6 with z = 5 | `fxpure » Eigen 3x3 » 1,7,8,-6,12,12,-2,4,8` | OK | ⇒ "L = 6, v = (3, 1, 1)"; scale by 5 |
| 4c(i) | 2 | E^-1 via C-H | `fxpure » Cayley-Hamilton 3x3 » 3,2,1,1,2,-2,1,1,2` | OK | ⇒ "M^-1 = (M^2 - 7M + 15I)/9" |
| 4c(ii) | 1 | E^-1 | `fxpure » Cayley-Hamilton 3x3 » 3,2,1,1,2,-2,1,1,2` | OK | ⇒ "[-4/9 5/9 7/9]" |
| 4c(iii) | 4 | D for the given E, P^4 | `fxpure » Diagonalise 3x3 M^n » 1,7,8,-6,12,12,-2,4,8,4` | OK | ⇒ "[-17550 22626 31320]"; but its own P gives D = diag(3, 6, 12), not diag(6, 12, 3) for the question's E; no way to supply E |
| 5a | 2 | proof | — | none | |
| 5b | 2 | deduce | — | none | |

Parts: 22. Rows: OK 17, WRONG 0, AWKWARD 3, GAP 1, none 2.
