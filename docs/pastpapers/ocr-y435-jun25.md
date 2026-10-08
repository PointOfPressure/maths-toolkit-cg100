# OCR Y435 Extra Pure, June 2025 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 2 | associativity of 3ab | — | none | proof |
| 1b | 2 | identity 1/3 | — | none | |
| 1c | 1 | closure | — | none | |
| 1d | 2 | 0 has no inverse | — | none | |
| 2a | 5 | GS with letter c | `fxpure » 2nd order + f(n) » 35/25,-12/25,c/25,20,70` | GAP | "f(n) uses c; only n": no letter constants in f(n); MS u = A(3/5)^n + B(4/5)^n + c/2 |
| 2b(i) | 3 | c = -10, u0 = 20, u1 = 70 | `fxpure » 2nd order + f(n) » 7/5,-12/25,-10/25,20,70` | OK | ⇒ "A = 300, B = -275"; divide by 25 by hand |
| 2b(ii) | 2 | peak value 89 | `fxpure » 2nd order + f(n) » 7/5,-12/25,-10/25,20,70` | OK | ⇒ "446/5" (u3 = 89.2) |
| 2b(iii) | 3 | u18 > 0 > u19 | `mpure » Terms of u(n) » 300*(4/5)^n-275*(3/5)^n-5,17,3` | OK | ⇒ "u(19) = -0.693" |
| 2c | 2 | c = 10: long-term k = 5 | `fxpure » 2nd order + f(n) » 7/5,-12/25,10/25,20,70` | AWKWARD | ⇒ "p(n) = 5"; the +f(n) tool prints no limit/behaviour line (the homogeneous one does), so k is inferred from roots 4/5, 3/5 |
| 3a | 1 | identity 0 | `fxpure » Z_n under + mod n » 9` | OK | ⇒ "identity 0" |
| 3b | 2 | Lagrange | — | none | |
| 3c | 2 | generators | `fxpure » Z_n under + mod n » 9` | OK | ⇒ "generators: 1, 2, 4, 5, 7, 8" |
| 3d(i) | 1 | H | `fxpure » Subgroups, Lagrange » 9, 0,1,2,3,4,5,6,7,8, 1,2,3,4,5,6,7,8,0, 2,3,4,5,6,7,8,0,1, 3,4,5,6,7,8,0,1,2, 4,5,6,7,8,0,1,2,3, 5,6,7,8,0,1,2,3,4, 6,7,8,0,1,2,3,4,5, 7,8,0,1,2,3,4,5,6, 8,0,1,2,3,4,5,6,7` | OK | ⇒ "{0,3,6} order 3"; whole 9x9 table must be typed (`Z_n under + mod n` prints it but subgroups need a separate tool) |
| 3d(ii) | 2 | only one subgroup | `fxpure » Subgroups, Lagrange » 9, 0,1,2,3,4,5,6,7,8, 1,2,3,4,5,6,7,8,0, 2,3,4,5,6,7,8,0,1, 3,4,5,6,7,8,0,1,2, 4,5,6,7,8,0,1,2,3, 5,6,7,8,0,1,2,3,4, 6,7,8,0,1,2,3,4,5, 7,8,0,1,2,3,4,5,6, 8,0,1,2,3,4,5,6,7` | OK | ⇒ "3 subgroups of G (order 9)" |
| 4a | 6 | other stationary points | `fxpure » Stationary points » x^3-12x*y^2+96y^2+30` | OK | ⇒ "(8, 4, 542) saddle" |
| 4b | 2 | section y = 0, nature of (0,0,30) | `fxpure » Sections y = k » x^3-12x*y^2+96y^2+30,0` | OK | ⇒ "y = 0: z = x^3+30" |
| 4c | 5 | normal at (3, 2) through (a, 482, 295) | `fxpure » Tangent plane z=f » x^3-12x*y^2+96y^2+30,3,2` | OK | ⇒ "r = (3, 2, 297) + t(-21, 240, -1)"; t = 2 gives a = -39 by hand |
| 4d | 3 | contour z = 542: curve part at x = 8 | `fxpure » Sections x = k » x^3-12x*y^2+96y^2+30,8` | GAP | "x = 8: z = 542" (the straight-line part); no contour factorisation; `Contours z = c` gives only axis cuts; y = ±4 by hand |
| 5a(i) | 3 | char eq in a, root 1 | `fxpure » Eigen 3x3 » 0.6,0.8,0,-0.8,0.6,0,0,0,1` | GAP | letters a, b refused; numeric example only ("L = 1, v = (0, 0, 1)") |
| 5a(ii) | 3 | other eigenvalues a ± sqrt(a^2-1) | — | GAP | symbolic |
| 5b | 2 | non-real | — | none | |
| 5c(i) | 2 | significance | — | none | |
| 5c(ii) | 2 | explain | — | none | |
| 5c(iii) | 2 | axis of rotation | `fxpure » Eigen 3x3 » 0.6,0.8,0,-0.8,0.6,0,0,0,1` | OK | ⇒ "line r = t(0, 0, 1): points on it are invariant" |
| 5c(iii) | | describe | `fcore » Describe a 3x3 » 0.6,0.8,0,-0.8,0.6,0,0,0,1` | GAP | "not a single standard map": only 90/180/270 deg rotations recognised, not a 53.1 deg rotation about the z-axis |

Parts: 24. Rows: OK 11, WRONG 0, AWKWARD 1, GAP 5, none 8.
