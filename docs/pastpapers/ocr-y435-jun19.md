# OCR Y435 Extra Pure, June 2019 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 1 | eigenvalues of reflection | `fxpure » Eigen 2x2 » 0.6,0.8,0.8,-0.6` | OK | ⇒ "L1 = 1, v1 = (2, 1)" |
| 1b | 3 | eigenvectors | `fxpure » Eigen 2x2 » 0.6,0.8,0.8,-0.6` | OK | ⇒ "L2 = -1, v2 = (1, -2)" |
| 1c | 1 | mirror line | `fxpure » Eigen 2x2 » 0.6,0.8,0.8,-0.6` | OK | ⇒ "y = (1/2)x: points on it are invariant" |
| 2a | 2 | stationary point | `fxpure » Stationary points » 4x^2+4y^2-4x+8y+11` | OK | ⇒ "(1/2, -1, 6) min" |
| 2b(i) | 2 | contour z = 42 sketch | `fxpure » Contours z = c » 4x^2+4y^2-4x+8y+11,42` | AWKWARD | only axis crossings (x = -2.33, 3.33 …); no "circle centre (0.5,-1) radius 3" for a quadratic contour |
| 2b(ii) | 3 | deduce minimum | — | none | reasoning |
| 2c | 4 | section y = c, min z = 22 | `fxpure » Sections y = k » 4x^2+4y^2-4x+8y+11,c` | GAP | "k: unknown c"; sections need numbers; check with c = 1, -3 gives z = 4x^2-4x+23 (min 22 at x = ½) |
| 2c | | check | `fxpure » Sections y = k » 4x^2+4y^2-4x+8y+11,1,-3` | OK | ⇒ "y = 1: z = 4*x^2-4*x+23" |
| 3 | 8 | Cayley-Hamilton inverse | `fxpure » Cayley-Hamilton 3x3 » -1,2,4,0,-1,-25,-3,5,-1` | OK | ⇒ "M^-1 = (M^2 + 3M + 140I)/12" |
| 4a | 2 | identity from a·a = 2 | — | none | deduction |
| 4b | 3 | 1·3 | — | none | deduction (Latin-square argument) |
| 4c(i) | 2 | complete table | `fxpure » Group axioms » 4, 2,1,4,3, 1,2,3,4, 4,3,2,1, 3,4,1,2` | OK | ⇒ "G is a group of order 4"; verifies the finished table, does not complete a partial one |
| 4c(ii) | 1 | abelian | `fxpure » Group axioms » 4, 2,1,4,3, 1,2,3,4, 4,3,2,1, 3,4,1,2` | OK | ⇒ "abelian: yes" |
| 5a | 2 | form recurrence | — | none | modelling |
| 5b | 5 | solve L(n+1) = a L(n) + b with letters | `fxpure » 1st order a u + f(n) » a,b,C` | GAP | "a: unknown a"; recurrence solver is numeric only |
| 5c | 2 | deduce R > aC/100 | — | none | |
| 5d(i) | 3 | L(n) and n | `fxpure » 1st order a u + f(n) » 1.08,-3000,30000` | OK | ⇒ "u(n) = -7500*(27/25)^n + 37500" |
| 5d(i) | | L(n) < 0 | `CAS » solve exact f(x)=0 » 37500-7500*1.08^x` | OK | ⇒ "x = ln(5)/ln(27/25)"; n = 21 by hand |
| 5d(i) | | numeric solve | `CAS » solve f(x)=0 » 37500-7500*1.08^x` | WRONG | "no real roots found in the search range" (root 20.9 outside the fixed range) |
| 5d(ii) | 3 | L21 and total | `CALC » Calculate » 37500-7500*1.08^21` | OK | ⇒ "-253.7528652" |
| 5d(ii) | | total | `CALC » Calculate » 21*3000+(37500-7500*1.08^21)` | WRONG | value 62746.24713 is right, but the main line shows "sqrt(3937091530)" — a false surd match for a large decimal |
| 6a | 2 | proof | — | none | |
| 6b | 7 | proof group | — | none | |
| 6c | 2 | counterexample (1+sqrt7)^2 | `CALC » Calculate » (1+sqrt(7))^2` | OK | ⇒ "2*sqrt(7)+8" |
| 6d | 2 | {1, -1} | — | none | |

Parts: 21. Rows: OK 12, WRONG 2, AWKWARD 1, GAP 2, none 8.
