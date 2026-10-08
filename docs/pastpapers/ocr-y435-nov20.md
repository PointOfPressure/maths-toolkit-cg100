# OCR Y435 Extra Pure, November 2020 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 5 | eigenvalues, eigenvectors | `fxpure » Eigen 2x2 » 0,2,3,-1` | OK | ⇒ "L2 = -3, v2 = (2, -3)" |
| 2 | 5 | find a, b with t(n) = a/(n+b)! | `fxpure » Verify u(n+1)=F(n,u) » u/(n+3),48/(n+2)!` | AWKWARD | ⇒ "u(n) satisfies the recurrence"; verifies once a = 48, b = 2 are guessed; no "fit constants in a given form" |
| 3a | 7 | u(n+2) = 4u(n+1) - 5u(n) | `fxpure » 2nd order homogeneous » 4,-5,0,1` | OK | ⇒ "u(n) = (sqrt(5))^n*sin(n*0.464)"; theta printed 0.464, not as arctan ½ |
| 3b | 5 | v(n) = a^(n/2) u(n) for a = 0.1, 0.2, 1 | `fxpure » Associated sequence » 4v-5u,0,u` | GAP | "F uses v; only n, u": associated sequence only for 1st-order recurrences |
| 3b | | workaround | `mpure » Terms of u(n) » (sqrt(0.2*5))^n*sin(n*atan(1/2)),1,8` | AWKWARD | ⇒ "u(4) = 24/25"; closed form typed by hand, behaviour read from terms |
| 4a(i) | 3 | axioms for odd integers under + | — | none | reasoning |
| 4a(ii) | 3 | a + b sqrt2 under x | — | none | reasoning |
| 4a(iii) | 3 | reals under x | — | none | reasoning |
| 4b(i) | 3 | remaining matrices (complex entries) | `fcore » AB and BA (2x2) » 0,i,i,0,0,i,i,0` | GAP | "A must be real": matrix tools reject complex entries |
| 4b(ii) | 1 | isomorphic? | — | none | element-order reasoning |
| 5a | 4 | f perpendicular to e is an eigenvector | `fxpure » Eigen 3x3 » 1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3` | OK | ⇒ "repeated: eigenspace is 2D" |
| 5a | | | `fxpure » Is v eigenvector 3x3 » 1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3,1,-1,0` | OK | ⇒ "yes: Mv = 1v, L = 1" |
| 5b | 1 | eigenvalue 1 | `fxpure » Eigen 3x3 » 1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3` | OK | ⇒ "L = 1 (x2)" |
| 5c | 2 | significance | — | none | |
| 5d | 1 | plane of reflection x + y + z = 0 | `fcore » Describe a 3x3 » 1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3` | GAP | "not a single standard map": only reflections in x/y/z = 0 are recognised; needs reflection in n.r = 0 from the -1 eigenvector |
| 6a(i) | 4 | one stationary point | `fxpure » Stationary points » 4x^4+4y^4-17x^2*y^2` | OK | ⇒ "1 stationary point" |
| 6a(ii) | 1 | s | `fxpure » Stationary points » 4x^4+4y^4-17x^2*y^2` | OK | ⇒ "(0, 0, 0) D = 0, test fails" |
| 6a(iii) | 3 | factorise f(x, y), contour z = 0 | `mpure » Factorise » 4x^4+4-17x^2` | AWKWARD | ⇒ "(2*x+1)*(2*x-1)*(x+2)*(x-2)"; only by setting y = 1; no two-variable factorise; `Contours z = c` at 0 lists "322 segments", not the four lines y = ±2x, ±x/2 |
| 6a(iv) | 1 | saddle | — | none | |
| 6b(i) | 3 | tangent plane at (a, a) | `fxpure » Tangent plane z=f » 4x^4+4y^4-17x^2*y^2,a,a` | GAP | "a: unknown a"; numeric only (a = 1 gives z = -18x - 18y + 27) |
| 6b(i) | | a = 1 check | `fxpure » Tangent plane z=f » 4x^4+4y^4-17x^2*y^2,1,1` | OK | ⇒ "z = -18x - 18y + 27" |
| 6b(ii) | 3 | d/a limit | — | GAP | symbolic distance and limit as a -> inf not available |
| 6b(iii) | 1 | above/below | — | none | |

Parts: 20. Rows: OK 8, WRONG 0, AWKWARD 3, GAP 5, none 7.
