# OCR H645 Further Maths (Y420, Y422, Y435) — calculator gaps

Audit of toolkit-9yewby (branch native-ui) against 24 OCR papers: Y420 Core Pure, Y422 Statistics Major and Y435 Extra Pure for jun19, nov20, nov21, jun22, jun23, jun24, jun25 and the specimen. Per-paper tables are in `ocr-y4xx-<series>.md` in this folder; every OK row there was re-run by script and its expected substring found in the output.

## Totals

| | parts | OK | WRONG | AWKWARD | GAP | none |
|---|---|---|---|---|---|---|
| by part (worst row in the part) | 832 | 380 | 19 | 132 | 84 | 217 |
| by row (one row per calculator step) | 916 rows | 455 | 19 | 141 | 84 | 217 |

"none" = explanation, proof, sketch or reading a given output. Score below = sum of the marks of every part the fix touches (occurrences × marks at stake). A part can appear under more than one fix.

## Ranked fixes

| rank | id | fix | parts | marks | wrong |
|---|---|---|---|---|---|
| 1 | A1 | Matrices with a letter (k, a, m) and 2-letter determinants | 15 | 71 | 0 |
| 2 | I | Statistics results shown to 3 s.f. — means, CI ends, regression coefficients, predictions, contributions | 16 | 63 | 0 |
| 3 | C2 | Exact answers left as acosh/asinh, or with uncombined logs | 9 | 61 | 0 |
| 4 | B | Polynomial roots with a given relationship / unknown coefficients (reverse Vieta) | 10 | 47 | 1 |
| 5 | L | Linear combinations of several Normals and of n independent copies | 12 | 42 | 1 |
| 6 | A2 | Vectors, lines and planes with an unknown: "find the constant so that …" | 9 | 39 | 0 |
| 7 | P2 | Symbolic parameters in distribution tools (n, a, m, p as letters) | 11 | 38 | 0 |
| 8 | F | Complex-exponential series (C + iS) and (a - e^(iθ))(a - e^(-iθ)) | 9 | 37 | 0 |
| 9 | J | No one-sample t test for a mean | 4 | 37 | 0 |
| 10 | K | PMCC and regression from summary sums | 9 | 33 | 0 |
| 11 | M | CLT for a sum or mean of discrete values, with continuity correction | 5 | 30 | 0 |
| 12 | C1 | Integrator: x^n/sqrt(quadratic) and coefficient forms are left to Simpson | 4 | 28 | 0 |
| 13 | R2 | Letter constants in calculus and DE tools | 7 | 27 | 2 |
| 14 | P1 | Distributions with unknown constants fixed by conditions | 6 | 23 | 0 |
| 15 | C3 | Volume tools print a decimal although the antiderivative is exact | 3 | 20 | 0 |
| 16 | V1 | Sum f(r) gives an expanded polynomial; never factorised; n not accepted as b | 4 | 19 | 0 |
| 17 | R3 | DE answers with decimal constants or unsimplified forms | 4 | 18 | 0 |
| 18 | R1 | Integrating factor not simplified (e^(ln…)) — blocks the integral | 3 | 17 | 1 |
| 19 | G | nth roots printed as a+bi decimals; exponential form per root missing | 4 | 15 | 0 |
| 20 | N | Negative binomial: r-th success on trial n, expected trials | 6 | 15 | 0 |
| 21 | E | `solve exact` falls back to decimals for standard exact cases | 2 | 14 | 0 |
| 22 | V2 | Method of differences not as a single fraction | 3 | 14 | 0 |
| 23 | AG2 | Letters in multivariable tools (sections, tangent plane) | 4 | 13 | 0 |
| 24 | D | Fixed -20..20 search range: roots and stationary points beyond it are "not found" | 3 | 12 | 3 |
| 25 | AB | Multivariable stationary points: missed and spurious points | 2 | 11 | 2 |
| 26 | AG1 | Contours: no centre/radius, asymptotes or line factors | 4 | 11 | 0 |
| 27 | H | Cartesian ↔ polar curve equations | 3 | 11 | 0 |
| 28 | W | Partial fractions printed as "1/4/(x-1/2)" | 2 | 11 | 0 |
| 29 | AD | No "image of points/shape under a matrix" tool | 3 | 10 | 0 |
| 30 | AF2 | Recurrence solvers need numbers (letters a, b, c, C) | 2 | 10 | 0 |
| 31 | AF3 | No fitting of constants in a given closed form | 2 | 10 | 0 |
| 32 | S1 | Hyperbolic simplification | 3 | 10 | 0 |
| 33 | T | Products of powers sin^m cos^n in multiple angles; cos nt in cos only | 2 | 10 | 0 |
| 34 | AE1 | Isomorphism tool gives only one map | 2 | 9 | 0 |
| 35 | AF1 | Limits at infinity with exponentials and polynomials fail | 5 | 9 | 0 |
| 36 | R4 | DE conditions other than y(0), y'(0) | 2 | 9 | 0 |
| 37 | AQ | Exact surd forms of trig values | 2 | 8 | 0 |
| 38 | S2 | Identity proofs only checked numerically | 3 | 8 | 0 |
| 39 | X1 | False surd display for large decimals (fmt) | 2 | 7 | 2 |
| 40 | AE2 | Symmetries of n-gon table cannot be relabelled | 2 | 7 | 0 |
| 41 | AF4 | Behaviour tool always starts at n = 0 | 1 | 7 | 0 |
| 42 | O | Binomial / Poisson-approximation refuse n > 1000 | 2 | 6 | 2 |
| 43 | AE3 | Group axioms only for finite tables | 1 | 6 | 0 |
| 44 | AG3 | Partial derivatives for g(x, y, z) | 2 | 6 | 0 |
| 45 | AG4 | Surface locus from an angle condition | 1 | 6 | 0 |
| 46 | AH | M^n with n as a letter | 1 | 6 | 0 |
| 47 | AA | CAS loses a factor when making a quotient monic (d/dx, simplify) | 2 | 5 | 2 |
| 48 | AF5 | Associated sequence only for first-order recurrences | 1 | 5 | 0 |
| 49 | AJ | Only square matrices | 1 | 5 | 0 |
| 50 | Q | Piecewise pdf: probabilities across the join | 2 | 5 | 0 |
| 51 | U2 | Maclaurin approx gives absolute error only | 2 | 5 | 0 |
| 52 | Y | Singular endpoint integral rejects negative base with fractional power | 1 | 4 | 1 |
| 53 | Z | `PI polynomial RHS` rejects a decimal constant | 1 | 4 | 1 |
| 54 | AC | Describe a 3x3 recognises only coordinate-axis maps | 3 | 4 | 0 |
| 55 | AK | Complex equations in z² and z* | 1 | 4 | 0 |
| 56 | AM | Roots p a + q not scaled to integer coefficients | 1 | 4 | 0 |
| 57 | AO | No induction tool for nth derivatives | 1 | 4 | 0 |
| 58 | AP | 2-D point-to-line distance / circle tangent to a locus | 1 | 4 | 0 |
| 59 | AT | Distribution of sums/differences of discrete RVs | 1 | 4 | 0 |
| 60 | AX | Two independent values: one below, one above | 2 | 4 | 0 |
| 61 | AC2 | Describe a 2x2 cannot split a matrix into two standard transformations | 1 | 3 | 0 |
| 62 | AI | Matrix tools reject complex entries | 1 | 3 | 0 |
| 63 | AR | No "verify a DE solution" tool | 1 | 3 | 0 |
| 64 | AV | Stats tools want raw data, not a frequency table | 1 | 3 | 0 |
| 65 | AW | No CI back-solver | 1 | 3 | 0 |
| 66 | U3 | No general term for Maclaurin series | 1 | 3 | 0 |
| 67 | X2 | nCr written as 10C4 is misread as 10·C·4 | 1 | 2 | 1 |
| 68 | AD2 | Invariant lines not through the origin | 1 | 2 | 0 |
| 69 | AF6 | 2nd order + f(n) prints no limit line | 1 | 2 | 0 |
| 70 | AU | E(g(X)) cannot take a piecewise g | 1 | 2 | 0 |
| 71 | H2 | Parametric elimination with hyperbolic identities | 1 | 2 | 0 |
| 72 | V3 | Sum f(r) refuses non-polynomial f | 1 | 2 | 0 |
| 73 | U1 | Maclaurin series capped at n = 8 | 1 | 1 | 1 |

## Wrong answers and crashes

Every WRONG row, whatever its rank above:

- Y420 jun19 Q17e(i) — `Integrating factor`: GS right but initial condition fails: "the point is outside the domain" when Q has a letter
- Y420 jun23 Q17c(ii) — `solve f(x)=0`: "no real roots found in the search range"; root t = 32.5 lies outside the fixed range; `solve exact` also "no solutions" (exact ln(11/3)/0.04)
- Y420 jun24 Q10a — `Maclaurin series`: "n is 1..8": cap stops at x^8, so the x^9 term is lost (with n = 8 only x^3 - x^6/2)
- Y420 jun24 Q17c(ii) — `stationary points`: "no stationary points found in the search range" (fixed -20..20); max at t = 126.4; mcalc Stationary points same ("none in -20 <= x <= 20")
- Y420 jun24 Q7b — `Singular endpoint int`: "both ends undefined"; x = 1 is fine (real cube root -1); the tool rejects negative bases with fractional powers
- Y420 jun25 Q17b(i) — `PI polynomial RHS`: "f(x) must be a polynomial in x" for the constant 0.4 (2/5 works); decimal RHS rejected
- Y420 nov20 Q16d — `Integrating factor`: "int (IF)Q dx is not elementary" but IF·Q = e^(-t); the unsimplified e^(ln...) IF blocks the integral
- Y420 nov21 Q17b(i) — `Integrating factor`: "int (IF)Q dx is not elementary" for int a e^(ax) dx; integrator fails with a letter constant in the exponent
- Y420 spec Q4 — `Cubic real coeffs`: raw Python error "int() argument must be … NoneType"; the known-root input cannot replace an unknown coefficient (GAP for "find q from a given root")
- Y422 jun19 Q3c — `aX+bY+c`: Var shown as "sqrt(350548482)/6" (it is 3120.49): false surd format for a decimal; the 2X/20Y model itself is the student's error
- Y422 jun23 Q1c — `Poisson approx to B`: "n must be 1 to 1000": refuses n = 10000
- Y422 jun25 Q11b(ii) — `d/dx`: gives "20/(x+5/3)^2"; correct F'(x) = 180/(9x+15)^2 = (20/9)/(x+5/3)^2 — a factor of 9 lost when the quotient is made monic
- Y422 jun25 Q11e — `pdf from a cdf`: f(x) = 20/(x+5/3)^2 (×9 too big) so "E(X) = 12.7", "Var(X) = -129", "SD = 0"; MS E(X) = 1.414
- Y422 nov20 Q1a — `Calculate`: silently read as "40*c" (10·C·4 with C a variable); nCr(10,4) works, but the textbook nCr key notation is misparsed with no warning
- Y422 nov20 Q2a(ii) — `Poisson approx to B`: "n must be 1 to 1000": refuses n = 1200, the very case the tool is for
- Y435 jun19 Q5d(i) — `solve f(x)=0`: "no real roots found in the search range" (root 20.9 outside the fixed range)
- Y435 jun19 Q5d(ii) — `Calculate`: value 62746.24713 is right, but the main line shows "sqrt(3937091530)" — a false surd match for a large decimal
- Y435 jun22 Q5a(iii) — `Stationary points`: ⇒ "(-1, 1, 0.368) max" correct, but also lists a false point "(6.86, 7.27, 0) D = 0" where the gradient has only underflowed
- Y435 nov21 Q1b — `Stationary points`: reports "1 stationary point (0, 0, 0)"; misses (-6, 9, -54) although it lies inside the stated search box (x, y within ±10)

## Fix details (in rank order)

### 1. A1 — Matrices with a letter (k, a, m) and 2-letter determinants

**Proposed fix.** Let `A[2x2]`/`A[3x3]` fields hold one or two letters and compute entries with casalg. Add `fcore » Det 2x2 in terms of k` (`a(k),b(k),c(k),d(k)`), let `Det 3x3 in terms of k` take two letters, and give `Inverse 2x2`, `AB and BA (2x2)`, `Three planes`, `Invariant points/lines`, `Eigen 2x2/3x3`, `Cayley-Hamilton 2x2` and `Induction: M^n` symbolic output. `Three planes` in k should print the point as adj(M)·b/det.

**Occurrences** (15 parts, 71 marks): Y420 jun19 Q3a [5, GAP]; Y420 jun19 Q3b [2, GAP]; Y420 jun19 Q14a(i) [4, GAP]; Y420 jun19 Q14b [6, AWKWARD]; Y420 nov20 Q9a [5, GAP]; Y420 nov20 Q9b [3, AWKWARD]; Y420 jun22 Q4b [4, AWKWARD]; Y420 jun23 Q14b [8, AWKWARD]; Y420 jun24 Q8c [4, AWKWARD]; Y420 jun24 Q15b [6, AWKWARD]; Y420 jun25 Q4b [6, GAP]; Y435 jun23 Q5a [8, GAP]; Y435 jun23 Q5b(i) [4, GAP]; Y435 jun25 Q5a(i) [3, GAP]; Y435 jun25 Q5a(ii) [3, GAP]

**Test cases (mark scheme answers):**

- Y420 jun23 Q14b: planes kx - z = 2, -x + ky + 2z = 1, 2kx + 2y + 3z = 0 → point ((6k-10)/(5k²-4k+2), (13k+6)/(…), (-4k²-2k-4)/(…)); k = 1 gives (-4/3, 19/3, -10/3)
- Y420 nov20 Q9b: det [[1,-2],[m,3]] = 3 + 2m = -5 → m = -4; invariant lines y = x, y = -2x
- Y420 jun19 Q14a(i): det [[-1,a,0],[2,3,1],[1,b,1]] = b - 3 - a → b = a + 3
- Y435 jun23 Q5a: P = [[a,0],[2,3]], eigenvectors (0,1), (a-3, 2); angle pi/4 → a = 1 or 5

### 2. I — Statistics results shown to 3 s.f. — means, CI ends, regression coefficients, predictions, contributions

**Proposed fix.** Format statistics outputs at 4–5 s.f. (means, s, CI limits, regression a and b, predictions, chi-squared contributions at 4 d.p.) and keep the 3 s.f. line as an extra. A CI whose rounded end equals mu0 must not look like it contains it; print limits to enough digits to separate them from round numbers.

**Occurrences** (16 parts, 63 marks): Y422 jun19 Q1b [2, AWKWARD]; Y422 jun22 Q5a [2, AWKWARD]; Y422 jun22 Q5d [2, AWKWARD]; Y422 jun22 Q6a [6, AWKWARD]; Y422 jun22 Q10b [2, AWKWARD]; Y422 jun24 Q7a [2, AWKWARD]; Y422 jun24 Q9b [2, AWKWARD]; Y422 jun25 Q3b [1, AWKWARD]; Y422 jun25 Q3d [4, AWKWARD]; Y422 jun25 Q6c [2, AWKWARD]; Y422 jun25 Q8c [10, AWKWARD]; Y422 nov21 Q5c [11, GAP]; Y422 nov21 Q6a [3, AWKWARD]; Y422 spec Q7(ii) [8, GAP]; Y422 spec Q10(i) [2, AWKWARD]; Y422 spec Q10(ii) [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 jun22 Q6a: n = 40, Σx = 491.84, Σx² = 6050.3 → CI (12.215, 12.377), excludes 12.2 (tool prints "(12.2, 12.4)")
- Y422 spec Q10: n = 60, Σx = 89.758, Σx² = 134.280 → xbar 1.49597, CI (1.4936, 1.4983) (tool: "xbar = 1.5", "(1.49, 1.5)")
- Y422 jun25 Q6c: regression y = 0.0242x + 100.0486, y(50) = 101.26 (tool: "y = 100 + 0.0242x", "y = 101")
- Y422 jun22 Q5a: P = 0.01145t + 1.786 to 4 s.f. (tool: 1.79 + 0.0115x)

### 3. C2 — Exact answers left as acosh/asinh, or with uncombined logs

**Proposed fix.** Add an output form "ln form" that rewrites arsinh t = ln(t + sqrt(t²+1)) and arcosh t = ln(t + sqrt(t²-1)), then a log-combining pass (ln a + ln b → ln ab, k ln a → ln a^k, surd denominators rationalised). Apply it in `definite integral a..b`, `Int 1/sqrt(x2+a2)`, `Integral to infinity` (take the log limit exactly), `Solve a cosh+b sinh=c` and the Volume tools.

**Occurrences** (9 parts, 61 marks): Y420 jun19 Q13b [5, AWKWARD]; Y420 jun19 Q15 [8, AWKWARD]; Y420 nov20 Q10 [7, AWKWARD]; Y420 jun22 Q7 [9, AWKWARD]; Y420 jun24 Q12a(i) [4, AWKWARD]; Y420 jun24 Q16 [6, AWKWARD]; Y420 jun25 Q7 [8, AWKWARD]; Y420 jun25 Q16b [6, AWKWARD]; Y420 spec Q15 [8, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun19 Q13b: ∫ arcosh x dx, 1..2 = 2 ln(2+√3) - √3 (tool: 2acosh(2) - √3)
- Y420 jun22 Q7: ∫ (x+1)/((x-1)(x²+1)) dx, 2..3 = ½ ln 2 (tool: ln2 + ln5/2 - ln10/2)
- Y420 jun25 Q7: ∫ 1/(x²-4) dx, 3..∞ = ¼ ln 5 (tool: 0.402)
- Y420 spec Q15: ∫ arsinh 2x dx, 0..2/3 = (2/3) ln 3 - 1/3 (tool: 2asinh(4/3)/3 - 1/3)

### 4. B — Polynomial roots with a given relationship / unknown coefficients (reverse Vieta)

**Proposed fix.** Add `fcore » Roots with a relation` (`coeffs with ?,relation`) where relation is one of `a,1/a`, `a,-a`, `a,-a,b,1/b`, `a,b,a+b`, `a,2/a,b,3b`, `root z` and the `?` coefficients are solved from Vieta. Fix `Cubic real coeffs` so `?` in a coefficient with a known root z solves for it instead of raising "int() argument … NoneType".

**Occurrences** (10 parts, 47 marks): Y420 jun19 Q8a [6, AWKWARD]; Y420 jun19 Q8b [2, GAP]; Y420 jun22 Q10a [6, GAP]; Y420 jun22 Q10b [4, GAP]; Y420 jun23 Q10a [6, GAP]; Y420 jun23 Q10b [1, GAP]; Y420 nov21 Q8a [5, GAP]; Y420 nov21 Q8b [4, GAP]; Y420 jun25 Q12 [8, GAP]; Y420 spec Q4 [5, WRONG]

**Test cases (mark scheme answers):**

- Y420 jun19 Q8: x³ - x² + kx - 2 = 0, roots a, 1/a, b → b = 2, k = -1, roots 2, -½ ± (√3/2)i
- Y420 nov21 Q8: 4x⁴ - 4x³ + px² + qx - 9 = 0, roots a, -a, b, 1/b → ±3/2, (1 ± √3 i)/2, p = -5, q = 9
- Y420 jun25 Q12: z⁴ - z³ + cz² + dz + 18, roots a, 2/a, b, -b → ±3i, (1 ± √7 i)/2, c = 11, d = -9
- Y420 spec Q4: z³ - 5z² + qz - 15 = 0 has root 1+2i → roots 1±2i, 3; q = 11

### 5. L — Linear combinations of several Normals and of n independent copies

**Proposed fix.** Add `fstat » Sum of Normals` (`k?,terms*` with terms `coef,count,mean,sd`) giving E, Var, P(W<k), P(W>k). Make the help line of `aX+bY+c` say "a = 2 means 2X, not X1 + X2".

**Occurrences** (12 parts, 42 marks): Y422 jun19 Q3c [4, WRONG]; Y422 nov20 Q3b [5, AWKWARD]; Y422 nov21 Q5a [3, AWKWARD]; Y422 nov21 Q5b [3, AWKWARD]; Y422 nov21 Q10b [5, AWKWARD]; Y422 jun22 Q2b [3, AWKWARD]; Y422 jun23 Q4c [3, AWKWARD]; Y422 jun23 Q4d [3, AWKWARD]; Y422 jun24 Q3c [3, AWKWARD]; Y422 jun24 Q3d [3, AWKWARD]; Y422 jun25 Q2b [4, AWKWARD]; Y422 jun25 Q2c [3, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 nov20 Q3b: 8 small N(51.5, 1.1²) - 2 medium N(100.7, 1.6²) - 1 large N(201.3, 1.7²) > 0 → N(9.3, 17.69), P = 0.9865
- Y422 jun24 Q3c: D - W - F with N(46,3.1²), N(35,2.4²), N(12,2.2²) → N(-1, 20.21), P(<0) = 0.5880
- Y422 jun25 Q2b: 5R + 5Y + 5G ≥ 495 → N(500, 14.45), P = 0.9058
- Y422 nov21 Q5a: 2A + B ≥ 16 with A1, A2 independent → N(15.6, 0.3729), P = 0.256

### 6. A2 — Vectors, lines and planes with an unknown: "find the constant so that …"

**Proposed fix.** Accept one letter in `a[3]` fields and add `fcore » Find k: vectors` with spec `condition,a[3],b[3],…` (conditions: perpendicular, lines meet, parallel, distances equal, planes consistent). Output the value(s) of k exactly (solve_exact), then rerun the normal tool with it.

**Occurrences** (9 parts, 39 marks): Y420 jun19 Q2 [3, GAP]; Y420 jun19 Q14a(ii) [3, AWKWARD]; Y420 nov20 Q8a [5, GAP]; Y420 nov21 Q11a(i) [1, GAP]; Y420 nov21 Q11a(ii) [2, GAP]; Y420 nov21 Q15 [6, AWKWARD]; Y420 jun23 Q16 [10, GAP]; Y420 jun24 Q5a [3, GAP]; Y420 jun25 Q11a [6, GAP]

**Test cases (mark scheme answers):**

- Y420 jun19 Q2: (1,2,c)·(2,-c,6) = 0 → c = ½
- Y420 nov20 Q8a: r = (0,2,2)+λ(-1,1,3), r = (-1,2,k)+μ(2,3,4) meet → k = 3, point (-3/5, 13/5, 19/5)
- Y420 jun23 Q16: P(4,1,0) equidistant (3) from 2x+y+2z = 0 and (x-3)/2 = (y-1)/b = (z+5)/3 → b = 2
- Y420 nov21 Q15: -4x+ky+7z = 4, x-2y+5z = l, 2x+3y+z = 2 sheaf → k = -13, l = 5

### 7. P2 — Symbolic parameters in distribution tools (n, a, m, p as letters)

**Proposed fix.** Allow one letter in `pdf find k`, `cdf F(x) from a pdf`, `cdf median quartiles`, `Discrete uniform`, `DRV from table` using casalg integration, so results come out in terms of the letter.

**Occurrences** (11 parts, 38 marks): Y422 jun19 Q10a [3, GAP]; Y422 jun19 Q10b [3, GAP]; Y422 jun19 Q10c(i) [4, GAP]; Y422 jun22 Q4a [2, GAP]; Y422 jun22 Q12a [7, GAP]; Y422 jun23 Q10a [4, GAP]; Y422 jun23 Q11a [3, GAP]; Y422 nov21 Q9a [3, GAP]; Y422 nov21 Q9b [3, GAP]; Y422 jun24 Q11a [4, GAP]; Y422 jun24 Q11b [2, GAP]

**Test cases (mark scheme answers):**

- Y422 jun22 Q12a: F = k(ax - 0.5x²) on [0, a] → median a(1 - 1/√2)
- Y422 nov21 Q9b: X uniform on -n..n, Var of sum of 10 = 10(n² + n)/3

### 8. F — Complex-exponential series (C + iS) and (a - e^(iθ))(a - e^(-iθ))

**Proposed fix.** In CAS `expand trig / log`, rewrite e^(ikx) + e^(-ikx) → 2cos kx (and the sine pair). Add `fcore » C + iS series` with spec `a,r,step,start` (terms a·r^k·e^(i(start+k·step)θ)) giving the GP sum, the realised denominator and C, S in closed form, with a numeric check at a chosen θ.

**Occurrences** (9 parts, 37 marks): Y420 jun19 Q16a [3, AWKWARD]; Y420 jun19 Q16b [9, AWKWARD]; Y420 jun22 Q14a [2, AWKWARD]; Y420 jun22 Q14b [6, AWKWARD]; Y420 jun24 Q13b(i) [2, AWKWARD]; Y420 jun24 Q13b(ii) [6, AWKWARD]; Y420 jun25 Q15a [2, AWKWARD]; Y420 jun25 Q15b [4, GAP]; Y420 jun25 Q15c [3, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun22 Q14: (3-e^(2iθ))(3-e^(-2iθ)) = 10 - 6cos 2θ; Σ sin((2r+1)θ)/3^r = 6 sin θ/(5 - 3cos 2θ)
- Y420 jun24 Q13b: (3-e^(iθ))(3-e^(-iθ)) = 10 - 6cos θ; Σ sin(rθ)/3^r = 3 sin θ/(10 - 6cos θ)
- Y420 jun25 Q15: C = Σ cos((4r+1)θ)/3^r = (9cos θ - 3cos 3θ)/(10 - 6cos 4θ)

### 9. J — No one-sample t test for a mean

**Proposed fix.** Add `fstat » t test for a mean` (`mu0,s,n,xbar,sig%,tail`) and `fstat » t test from data` (`mu0,sig%,tail,data*`), printing t, df, critical t and p. The z tools should warn "n < 30 and sigma unknown: use t".

**Occurrences** (4 parts, 37 marks): Y422 nov21 Q5c [11, GAP]; Y422 jun23 Q7b [10, GAP]; Y422 jun24 Q7d [8, GAP]; Y422 spec Q7(ii) [8, GAP]

**Test cases (mark scheme answers):**

- Y422 nov21 Q5c: n = 10, Σx = 299.6, Σx² = 8981.0, mu0 = 30.2 → t = -1.020, crit t9 = ±2.262, do not reject
- Y422 jun23 Q7b: 12 shampoo values, mu0 = 1.0, 1-tail → t = 0.530, crit 1.796
- Y422 jun24 Q7d: 10 carrot values, mu0 = 9.4, 2-tail → t = 1.585, crit 2.262
- Y422 spec Q7(ii): 15 petrol prices, mu0 = 110.2 → t = 0.891, crit 2.145

### 10. K — PMCC and regression from summary sums

**Proposed fix.** Add `fstat » Bivariate from sums` (`n,sumx,sumy,sumx2,sumy2,sumxy`) printing Sxx, Syy, Sxy, r, y-on-x and x-on-y lines (4 s.f.), plus an optional x0 for prediction.

**Occurrences** (9 parts, 33 marks): Y422 jun19 Q6a(i) [5, GAP]; Y422 jun19 Q6a(ii) [2, GAP]; Y422 nov20 Q5b [5, GAP]; Y422 nov20 Q5c [2, GAP]; Y422 nov21 Q8b(ii) [4, GAP]; Y422 jun23 Q6b [4, GAP]; Y422 jun24 Q8b [5, GAP]; Y422 jun24 Q8c [2, GAP]; Y422 jun25 Q7a [4, GAP]

**Test cases (mark scheme answers):**

- Y422 jun19 Q6a(i): n = 12, Σx = 1131, Σy = 1227, Σx² = 107783, Σy² = 126725, Σxy = 116724 → x = 0.8537y + 6.962
- Y422 nov20 Q5b: n = 16, Σx = 198.0, Σx² = 2936.92, Σy = 188.7, Σy² = 2605.35, Σxy = 2554.87 → y = 0.4515x + 6.207
- Y422 nov21 Q8b(ii): n = 20, Σt = 80.37, Σv = 970.86, Σt² = 324.71, Σv² = 47829.24, Σtv = 3886.53 → r = -0.4255
- Y422 jun25 Q7a: n = 30, Σx = 2.219, Σy = 357.7, Σx² = 0.2368, Σy² = 4648, Σxy = 25.01 → r = -0.2744

### 11. M — CLT for a sum or mean of discrete values, with continuity correction

**Proposed fix.** Add `fstat » CLT sum/mean` (`mean,var,n,k,step?,sum|mean`) that applies the continuity correction (half a step on the sum scale) and prints both corrected and uncorrected probabilities.

**Occurrences** (5 parts, 30 marks): Y422 nov20 Q10c [9, AWKWARD]; Y422 jun22 Q9e [4, AWKWARD]; Y422 jun24 Q11c [5, AWKWARD]; Y422 jun25 Q10c [8, AWKWARD]; Y422 spec Q11(viii) [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 nov20 Q10c: mean W of 50 values of X - 2Y, E = 0, Var = 16.2 → P(W > 1) with 1.01 = 0.0380
- Y422 jun22 Q9e: mean of 30 from U{0..20} → P(W ≤ 7) with 7 + 1/60 = 0.00348
- Y422 jun24 Q11c: mean of 100 from U{25..75} → P(< 48) with 47.995 = 0.0866
- Y422 jun25 Q10c: mean of 100 T, Var(T) = 2.88 → P(> 0.25) with 0.255 = 0.0665

### 12. C1 — Integrator: x^n/sqrt(quadratic) and coefficient forms are left to Simpson

**Proposed fix.** Teach cascalc.integ the substitutions x = a sinh u, completing the square for 1/sqrt(ax²+bx+c), and 1/sqrt(a²-b²x²). `Integrate hyperbolic` must stop claiming "no elementary integral" when the substitution exists. `Int 1/sqrt(a2-x2)` should take `a,b,p,q` for 1/sqrt(a²-b²x²).

**Occurrences** (4 parts, 28 marks): Y420 jun19 Q15 [8, AWKWARD]; Y420 nov20 Q3 [4, AWKWARD]; Y420 nov21 Q16b [10, GAP]; Y420 jun25 Q16a [6, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun19 Q15: ∫ 1/sqrt(4x²-4x+2) dx, 3/4..3/2 = ½ ln((3+√5)/2) = 0.4812
- Y420 nov21 Q16b: ∫ x²/sqrt(4+x²) dx, 0..2 = 2√2 - 2 ln(1+√2) = 1.0657
- Y420 jun25 Q16a: ∫ (x+3)/sqrt(x²+9) dx, 0..4 = 2 + ln 27 = 5.2958

### 13. R2 — Letter constants in calculus and DE tools

**Proposed fix.** Allow letter constants (a, k, lambda) in `Integrating factor`, `Separable DE`, `Second order …`, `Coupled equations` and the Volume tools: integrate e^(ax) with a letter, apply initial conditions symbolically.

**Occurrences** (7 parts, 27 marks): Y420 jun19 Q17e(i) [5, WRONG]; Y420 nov21 Q17b(i) [4, WRONG]; Y420 spec Q16(ii)(A) [3, GAP]; Y420 jun23 Q17a(i) [6, GAP]; Y420 jun23 Q17a(ii) [2, GAP]; Y420 jun23 Q17b(i) [3, AWKWARD]; Y420 jun24 Q4 [4, GAP]

**Test cases (mark scheme answers):**

- Y420 nov21 Q17b(i): dx/dt + ax = a, x(0) = 0 → x = 1 - e^(-at) (tool: "int (IF)Q dx is not elementary")
- Y420 jun19 Q17e(i): dv/dt + 0.1v = λt, v(0) = 0 → v = 10λ(t - 10 + 10e^(-0.1t)) (tool: "the point is outside the domain")
- Y420 spec Q16(ii)(A): x'' + 2kx' + (k²+9)x = 0 → e^(-kt)(A cos 3t + B sin 3t)

### 14. P1 — Distributions with unknown constants fixed by conditions

**Proposed fix.** Add `fstat » Solve for constants` (`f(x) or table with a,b; conditions*`) where conditions are `total=1`, `E=v`, `F(x0)=p`; solve the linear/quadratic system, then hand the fitted pdf/cdf to the usual tools. `pdf find k` should accept an additive unknown.

**Occurrences** (6 parts, 23 marks): Y422 jun22 Q3a [3, GAP]; Y422 jun23 Q10b [2, GAP]; Y422 nov21 Q11a [5, GAP]; Y422 spec Q2(i)(B) [3, GAP]; Y422 jun24 Q12a [7, GAP]; Y422 jun25 Q11a [3, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 jun22 Q3a: P = a, b, 0.24, 0.32, b² with E(X) = 1.8 → a = b = 0.2
- Y422 nov21 Q11a: ax² on [0,2), b(3-x)² on [2,3], E(X) = 2 → a = 1/8, b = 2
- Y422 jun24 Q12a: F = a(x²+bx+c) on [20,30], P(X<25) = 11/24 → a = 1/600, b = 10, c = -600; P(X>27) = 0.335

### 15. C3 — Volume tools print a decimal although the antiderivative is exact

**Proposed fix.** In `Volume about x-axis`/`Volume about y-axis`, evaluate the shown antiderivative with defint_exact and print "V = <exact>" before the decimal (as `Polar area` already does).

**Occurrences** (3 parts, 20 marks): Y420 nov20 Q10 [7, AWKWARD]; Y420 spec Q12(iii) [7, AWKWARD]; Y420 jun25 Q16b [6, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 spec Q12(iii): pi ∫ 1/(1+x²)² dx, -1..1 = pi(pi+2)/4 = 4.04
- Y420 nov20 Q10: pi ∫ 2 arcosh y dy, 1..2 = 2pi(2 ln(2+√3) - √3) = 5.67

### 16. V1 — Sum f(r) gives an expanded polynomial; never factorised; n not accepted as b

**Proposed fix.** In `Sum f(r), r = a..b`, factorise S(n) (caspoly.factor) and print the factorised line first; accept `b = n`.

**Occurrences** (4 parts, 19 marks): Y420 jun19 Q1 [4, AWKWARD]; Y420 nov20 Q1 [6, AWKWARD]; Y420 jun22 Q1b [4, AWKWARD]; Y420 jun25 Q3 [5, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov20 Q1: Σ r(r+1)(r+3) = n(n+1)(n+2)(3n+13)/12
- Y420 jun25 Q3: Σ r(r+2) = n(n+1)(2n+7)/6

### 17. R3 — DE answers with decimal constants or unsimplified forms

**Proposed fix.** Print constants exactly (C = 20e, C = 10 ln 200) via exact evaluation of the initial condition, and simplify e^(-(c + x/5)) forms; expand the coupled-equation y.

**Occurrences** (4 parts, 18 marks): Y420 jun19 Q17c(i) [5, AWKWARD]; Y420 jun24 Q17b [8, AWKWARD]; Y420 jun25 Q17a(iii) [4, AWKWARD]; Y420 jun23 Q17b(ii) [1, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun19 Q17c(i): v' + 0.1v = -2, v(10) = 0 → v = 20(e^(1-0.1t) - 1)
- Y420 jun24 Q17b: x' + x/(200-t) = 10, x(0) = 0 → x = 10(200-t) ln(200/(200-t))

### 18. R1 — Integrating factor not simplified (e^(ln…)) — blocks the integral

**Proposed fix.** Simplify e^(∫P) with log laws (e^(a ln x + b ln y) → x^a y^b) before forming IF·Q; print the IF in that form. Then IF·Q = e^(-t) integrates.

**Occurrences** (3 parts, 17 marks): Y420 nov20 Q16b [8, AWKWARD]; Y420 nov20 Q16c(i) [4, AWKWARD]; Y420 nov20 Q16d [5, WRONG]

**Test cases (mark scheme answers):**

- Y420 nov20 Q16b: P = -1/(t(1+t²)) → IF = sqrt(1+t²)/t
- Y420 nov20 Q16d: Q = t e^(-t)/sqrt(1+t²) → P = (At - t e^(-t))/sqrt(1+t²)

### 19. G — nth roots printed as a+bi decimals; exponential form per root missing

**Proposed fix.** In `nth roots of z`, print each root as r e^(iθ) with exact r and θ in (-pi, pi] (e.g. "w2 = 2^(1/3) e^(-5i pi/9)"), then the a+bi form; same for `Roots of unity`.

**Occurrences** (4 parts, 15 marks): Y420 jun19 Q10b [4, AWKWARD]; Y420 nov20 Q11a [2, AWKWARD]; Y420 nov21 Q10b(i) [5, AWKWARD]; Y420 jun23 Q5a [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun19 Q10b: z³ = 2+2i → √2 e^(i pi/12), √2 e^(3i pi/4), √2 e^(-7i pi/12)
- Y420 nov21 Q10b(i): z³ = 1+√3 i → 2^(1/3) e^(i pi/9), 2^(1/3) e^(7i pi/9), 2^(1/3) e^(-5i pi/9)
- Y420 jun23 Q5a: z⁶ = -64 → 2e^(±i pi/6), 2e^(±i pi/2), 2e^(±5i pi/6)

### 20. N — Negative binomial: r-th success on trial n, expected trials

**Proposed fix.** Add `fstat » r-th success on trial n` (`p,r,n`) printing C(n-1, r-1) p^r (1-p)^(n-r) and E = r/p.

**Occurrences** (6 parts, 15 marks): Y422 nov21 Q3d [3, AWKWARD]; Y422 nov21 Q3e [3, AWKWARD]; Y422 jun23 Q3d [2, AWKWARD]; Y422 jun25 Q4d [2, AWKWARD]; Y422 spec Q4(iii) [2, AWKWARD]; Y422 spec Q4(v) [3, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 nov21 Q3e: p = 0.04, 3rd on 60th → 0.0107; Q3d: E = 75
- Y422 jun23 Q3d: p = 0.55, 5th on 10th → 0.117
- Y422 jun25 Q4d: p = 0.4, 5th on 20th → 0.01866

### 21. E — `solve exact` falls back to decimals for standard exact cases

**Proposed fix.** Extend cassolve.solve_exact: quadratics in cosh/sinh/e^x (substitute u), a·e^(px) = b·e^(qx), and x(2 ln x + 3) = 0 style factor-then-log. Return ln forms.

**Occurrences** (2 parts, 14 marks): Y420 jun22 Q3 [6, AWKWARD]; Y420 jun25 Q13b [8, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun22 Q3: 3 cosh x = 2 sinh² x → x = ±ln(2+√3)
- Y420 jun25 Q13b: 2x ln x + 3x = 0 → x = e^(-3/2)

### 22. V2 — Method of differences not as a single fraction

**Proposed fix.** Print S(n) also as one fraction with integer numerator and factorised denominator.

**Occurrences** (3 parts, 14 marks): Y420 nov21 Q1b [4, AWKWARD]; Y420 jun23 Q3a [5, AWKWARD]; Y420 spec Q5(ii) [5, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov21 Q1b: Σ 1/((2r-1)(2r+1)) = n/(2n+1)
- Y420 jun23 Q3a: Σ 1/(r(r+2)) = 3/4 - (2n+3)/(2(n+1)(n+2))

### 23. AG2 — Letters in multivariable tools (sections, tangent plane)

**Proposed fix.** Accept a letter for k in `Sections y = k`/`x = k` and for the point in `Tangent plane z=f`.

**Occurrences** (4 parts, 13 marks): Y435 jun19 Q2c [4, GAP]; Y435 jun24 Q1b [3, AWKWARD]; Y435 nov20 Q6b(i) [3, GAP]; Y435 nov20 Q6b(ii) [3, GAP]

### 24. D — Fixed -20..20 search range: roots and stationary points beyond it are "not found"

**Proposed fix.** In cascalc.solve, mcalc `Stationary points` and CAS `stationary points`, widen the scan adaptively (e.g. doubling to ±10⁴ when nothing is found, plus a log-spaced scan) and add an optional range field `lo?,hi?`. Never print "no real roots" without saying the range searched.

**Occurrences** (3 parts, 12 marks): Y420 jun23 Q17c(ii) [4, WRONG]; Y420 jun24 Q17c(ii) [5, WRONG]; Y435 jun19 Q5d(i) [3, WRONG]

**Test cases (mark scheme answers):**

- Y420 jun23 Q17c(ii): -75e^(0.035t) + 275e^(-0.005t) = 0 → t = 32.48 (exact ln(11/3)/0.04)
- Y420 jun24 Q17c(ii): max of 10(200-t) ln(200/(200-t)) at t = 200(1 - 1/e) = 126.4
- Y435 jun19 Q5d(i): 37500 - 7500·1.08^n = 0 → n = ln 5/ln 1.08 = 20.9

### 25. AB — Multivariable stationary points: missed and spurious points

**Proposed fix.** Seed Newton from a wider grid and from points where one partial vanishes analytically; drop candidates where |grad| is tiny only because z underflows (check scaled gradient).

**Occurrences** (2 parts, 11 marks): Y435 nov21 Q1b [7, WRONG]; Y435 jun22 Q5a(iii) [4, WRONG]

**Test cases (mark scheme answers):**

- Y435 nov21 Q1b: x³ + x²y - 2y² → (0,0,0) and (-6, 9, -54)
- Y435 jun22 Q5a(iii): y e^(-(x²+2x+2)y) → only (-1, 1, e^-1)

### 26. AG1 — Contours: no centre/radius, asymptotes or line factors

**Proposed fix.** Classify contour z = c of a quadratic/rational f (circle centre/radius, hyperbola asymptotes, factorised line pairs).

**Occurrences** (4 parts, 11 marks): Y435 jun19 Q2b(i) [2, AWKWARD]; Y435 jun24 Q1c [3, GAP]; Y435 nov20 Q6a(iii) [3, AWKWARD]; Y435 jun25 Q4d [3, GAP]

**Test cases (mark scheme answers):**

- Y435 jun24 Q1c: 12x - 30y + 6xy = 12 → asymptotes x = 5, y = -2

### 27. H — Cartesian ↔ polar curve equations

**Proposed fix.** Add `fcalc » Cartesian eqn to polar` (`F(x,y)`) substituting x = r cos t, y = r sin t and simplifying (r² = … form), and `fcalc » Polar eqn to cartesian` (`r(t)`) multiplying by r and completing squares (circle centre/radius).

**Occurrences** (3 parts, 11 marks): Y420 jun19 Q7a [2, GAP]; Y420 jun25 Q6a [3, GAP]; Y420 nov21 Q14b(i) [6, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun19 Q7a: (x²+y²)² = 2c²xy → r² = c² sin 2θ
- Y420 jun25 Q6a: (x²+y²)² = xy → r² = ½ sin 2θ
- Y420 nov21 Q14b(i): r = a(cos θ + 2 sin θ) → (x - a/2)² + (y - a)² = 5a²/4, radius (√5/2)a

### 28. W — Partial fractions printed as "1/4/(x-1/2)"

**Proposed fix.** Keep integer linear factors: ½/(2r-1) rather than (1/4)/(x - 1/2).

**Occurrences** (2 parts, 11 marks): Y420 nov21 Q1a [3, AWKWARD]; Y420 jun25 Q7 [8, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov21 Q1a: 1/((2r-1)(2r+1)) = ½/(2r-1) - ½/(2r+1)

### 29. AD — No "image of points/shape under a matrix" tool

**Proposed fix.** Add `fcore » Image of points` (`A[2x2],points*`) listing images, area scale and orientation (unit square default).

**Occurrences** (3 parts, 10 marks): Y420 nov21 Q9a [2, AWKWARD]; Y420 spec Q3(i) [2, AWKWARD]; Y420 jun25 Q14b [6, AWKWARD]

### 30. AF2 — Recurrence solvers need numbers (letters a, b, c, C)

**Proposed fix.** Allow letters in `1st order a u + f(n)` and `2nd order + f(n)` and give the closed form in them.

**Occurrences** (2 parts, 10 marks): Y435 jun19 Q5b [5, GAP]; Y435 jun25 Q2a [5, GAP]

### 31. AF3 — No fitting of constants in a given closed form

**Proposed fix.** Add `fxpure » Fit constants` (`F(n,u),form with a,b`) solving from the first terms, then verifying.

**Occurrences** (2 parts, 10 marks): Y435 nov20 Q2 [5, AWKWARD]; Y435 jun23 Q2b(ii) [5, AWKWARD]

**Test cases (mark scheme answers):**

- Y435 nov20 Q2: t(n+1) = t(n)/(n+3), t1 = 8 → t(n) = 48/(n+2)!

### 32. S1 — Hyperbolic simplification

**Proposed fix.** Add cosh² - sinh² = 1, 2 sinh cosh = sinh 2x, cosh² + sinh² = cosh 2x to CAS simplify.

**Occurrences** (3 parts, 10 marks): Y420 jun19 Q13a [5, AWKWARD]; Y420 jun22 Q9b(ii) [3, AWKWARD]; Y420 nov20 Q13b [2, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov20 Q13b: d²/dx² sinh² x = 2 cosh 2x
- Y420 jun22 Q9b(ii): f'' = (sinh x - 1)/(1 + sinh x)²

### 33. T — Products of powers sin^m cos^n in multiple angles; cos nt in cos only

**Proposed fix.** Add `fcore » sin^m t cos^n t` (`m,n`) via (z ± 1/z) expansion, and make `cos nt, sin nt powers` also print cos nt as a polynomial in cos t.

**Occurrences** (2 parts, 10 marks): Y420 nov20 Q12b [6, GAP]; Y420 spec Q14(ii) [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov20 Q12b: sin³θ cos³θ = -sin 6θ/32 + 3 sin 2θ/32
- Y420 spec Q14(ii): cos 6θ = 32c⁶ - 48c⁴ + 18c² - 1

### 34. AE1 — Isomorphism tool gives only one map

**Proposed fix.** List all isomorphisms (for cyclic groups: one per generator).

**Occurrences** (2 parts, 9 marks): Y435 nov21 Q2c [4, AWKWARD]; Y435 spec Q1(iii) [5, AWKWARD]

### 35. AF1 — Limits at infinity with exponentials and polynomials fail

**Proposed fix.** Teach casalg.limit dominant-term rules (a^n vs polynomials) and let `Associated sequence` report a limit from a closed form.

**Occurrences** (5 parts, 9 marks): Y435 jun22 Q3b(i) [1, AWKWARD]; Y435 jun22 Q3b(ii) [1, AWKWARD]; Y435 jun22 Q3b(iii) [1, AWKWARD]; Y435 jun23 Q2c [2, AWKWARD]; Y435 nov21 Q4d [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y435 jun22 Q3b: t(n) = 6(0.8)^n + 3n² - 2n + 1: lim t/n³ = 0, lim t/n² = 3, t/n diverges

### 36. R4 — DE conditions other than y(0), y'(0)

**Proposed fix.** Let the second-order and IF tools take conditions like `y->0 as x->inf`, `y'(0)=0` alone, or a long-term value, and solve for the constants that remain.

**Occurrences** (2 parts, 9 marks): Y420 jun24 Q14b [5, AWKWARD]; Y420 nov20 Q16c(i) [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun24 Q14b: y = Ae^(-2x) + Be^x - 6e^(-x), y → 0 and y'(0) = 0 → y = 3e^(-2x) - 6e^(-x), zero at x = -ln 2

### 37. AQ — Exact surd forms of trig values

**Proposed fix.** Recognise cos(pi/12)^6 and 2 sin(pi/5) style values in Calculate.

**Occurrences** (2 parts, 8 marks): Y420 spec Q14(iv) [3, AWKWARD]; Y420 jun25 Q9b(ii) [5, AWKWARD]

### 38. S2 — Identity proofs only checked numerically

**Proposed fix.** Make `Identity check at x` take an identity `lhs,rhs` and show the exponential expansion, reducing both sides.

**Occurrences** (3 parts, 8 marks): Y420 nov20 Q13a [2, AWKWARD]; Y420 nov21 Q16a [4, AWKWARD]; Y420 jun25 Q14a [2, AWKWARD]

### 39. X1 — False surd display for large decimals (fmt)

**Proposed fix.** In casutil.fmt, only accept a surd match when the squared value is within a relative 1e-12 and the radicand is small (say < 10⁴); otherwise print the decimal.

**Occurrences** (2 parts, 7 marks): Y435 jun19 Q5d(ii) [3, WRONG]; Y422 jun19 Q3c [4, WRONG]

**Test cases (mark scheme answers):**

- Y435 jun19 Q5d(ii): 21×3000 + (37500 - 7500·1.08²¹) = 62746.25 (shown as sqrt(3937091530))

### 40. AE2 — Symmetries of n-gon table cannot be relabelled

**Proposed fix.** Let the user name the elements (I, Ma, Mb, Mc, R120, R240) and print the table in that order.

**Occurrences** (2 parts, 7 marks): Y435 jun24 Q3a [3, AWKWARD]; Y435 jun24 Q3b [4, AWKWARD]

### 41. AF4 — Behaviour tool always starts at n = 0

**Proposed fix.** Add `n0?` to `Behaviour u(n+1)=F`.

**Occurrences** (1 parts, 7 marks): Y435 jun22 Q1 [7, AWKWARD]

### 42. O — Binomial / Poisson-approximation refuse n > 1000

**Proposed fix.** Lift the n ≤ 1000 cap in `Binomial P(X=k)`, `Poisson approx to B`, `Binomial least n` (use lgamma / log-space terms).

**Occurrences** (2 parts, 6 marks): Y422 nov20 Q2a(ii) [3, WRONG]; Y422 jun23 Q1c [3, WRONG]

**Test cases (mark scheme answers):**

- Y422 nov20 Q2a(ii): B(1200, 1/4000) ≈ Po(0.3): P(X=3) = 0.0033, P(X>3) = 0.0003
- Y422 jun23 Q1c: B(10000, 1/1296) ≈ Po(7.716): P(X=10) = 0.0919, P(X>10) = 0.157

### 43. AE3 — Group axioms only for finite tables

**Proposed fix.** Add a check for formula operations on infinite sets (identity/inverse solved symbolically).

**Occurrences** (1 parts, 6 marks): Y435 jun22 Q4d [6, GAP]

### 44. AG3 — Partial derivatives for g(x, y, z)

**Proposed fix.** Let `Partial derivatives` take three variables and factorise the results.

**Occurrences** (2 parts, 6 marks): Y435 spec Q4(i) [2, AWKWARD]; Y435 spec Q4(ii) [4, GAP]

### 45. AG4 — Surface locus from an angle condition

**Proposed fix.** Solve grad conditions over a surface (angle between tangent plane and a fixed plane).

**Occurrences** (1 parts, 6 marks): Y435 nov21 Q5 [6, GAP]

### 46. AH — M^n with n as a letter

**Proposed fix.** Print P D^n P^-1 multiplied out with n symbolic.

**Occurrences** (1 parts, 6 marks): Y435 nov21 Q3d [6, AWKWARD]

### 47. AA — CAS loses a factor when making a quotient monic (d/dx, simplify)

**Proposed fix.** In the quotient simplifier, when (9x+15)² is rewritten as 81(x+5/3)², divide the numerator by 81 not 9 (the leading coefficient must be raised to the power). Add a numeric spot-check after simplify in debug builds.

**Occurrences** (2 parts, 5 marks): Y422 jun25 Q11b(ii) [3, WRONG]; Y422 jun25 Q11e [2, WRONG]

**Test cases (mark scheme answers):**

- Y422 jun25 Q11: F = (24x+20)/(9x+15) - 4/3 → f = 180/(9x+15)², E(X) = 1.414 (tool: f = 20/(x+5/3)², E = 12.7, Var = -129)
- Also: d/dx (2x+1)/(3x+5) = 7/(3x+5)² (tool: 7/(x+5/3)²); mcalc f'(1) of (24x+20)/(9x+15) = 5/16 (tool: 45/16)

### 48. AF5 — Associated sequence only for first-order recurrences

**Proposed fix.** Allow F(n,u,v) in `Associated sequence`.

**Occurrences** (1 parts, 5 marks): Y435 nov20 Q3b [5, GAP]

### 49. AJ — Only square matrices

**Proposed fix.** Allow 2x3 × 3x2 products and unknown entries.

**Occurrences** (1 parts, 5 marks): Y420 nov20 Q2a [5, GAP]

### 50. Q — Piecewise pdf: probabilities across the join

**Proposed fix.** Add c, d inputs to `Piecewise pdf` (`f(x),g(x),a,b,c,lo?,hi?`) printing P(lo<X<hi).

**Occurrences** (2 parts, 5 marks): Y422 jun19 Q9b [3, AWKWARD]; Y422 spec Q2(ii)(A) [2, AWKWARD]

**Test cases (mark scheme answers):**

- Y422 jun19 Q9b: x/25 on [0,5], (10-x)/25 on (5,10] → P(X ≤ 6) = 0.68
- Y422 spec Q2(ii)(A): 1/3 on [-1,0], 1/3 + x² on [0,1] → P(X < ½) = 13/24

### 51. U2 — Maclaurin approx gives absolute error only

**Proposed fix.** Add "% error = 100(series - f)/f" to `Maclaurin approx`.

**Occurrences** (2 parts, 5 marks): Y420 nov21 Q5b [3, AWKWARD]; Y420 jun22 Q9d [2, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 nov21 Q5b: ln 1.2 by 2x - 2x² at x = 0.1 → -1.27%
- Y420 jun22 Q9d: ln(1+sinh x) by x - x²/2 at 0.1 → 0.48%

### 52. Y — Singular endpoint integral rejects negative base with fractional power

**Proposed fix.** Use the real cube root for odd-denominator powers in the evaluator used by `Singular endpoint int`.

**Occurrences** (1 parts, 4 marks): Y420 jun24 Q7b [4, WRONG]

**Test cases (mark scheme answers):**

- Y420 jun24 Q7b: ∫ (x-2)^(-1/3) dx, 1..2 = -3/2

### 53. Z — `PI polynomial RHS` rejects a decimal constant

**Proposed fix.** Treat numeric constants (0.4) as degree-0 polynomials.

**Occurrences** (1 parts, 4 marks): Y420 jun25 Q17b(i) [4, WRONG]

**Test cases (mark scheme answers):**

- Y420 jun25 Q17b(i): h'' + 0.3h' + 0.02h = 0.4 → h = Ae^(-0.1t) + Be^(-0.2t) + 20

### 54. AC — Describe a 3x3 recognises only coordinate-axis maps

**Proposed fix.** Use eigenvalues: det 1 with axis v (eigenvalue 1) and angle from trace (cos θ = (tr - 1)/2) → rotation about v; det -1 with -1 eigenvector n → reflection in n·r = 0.

**Occurrences** (3 parts, 4 marks): Y435 nov20 Q5d [1, GAP]; Y435 jun25 Q5c(iii) [2, GAP]; Y435 spec Q5(v) [1, GAP]

**Test cases (mark scheme answers):**

- Y435 nov20 Q5d: reflection in x + y + z = 0
- Y435 spec Q5(v): rotation 90° about (1, 0, 1)

### 55. AK — Complex equations in z² and z*

**Proposed fix.** Add `fcore » Solve in z, z*` splitting into real equations and solving.

**Occurrences** (1 parts, 4 marks): Y420 nov20 Q6 [4, GAP]

**Test cases (mark scheme answers):**

- Y420 nov20 Q6: z² - 4iz* + 11 = 0, Re z > 0 → z = 1 + 2i

### 56. AM — Roots p a + q not scaled to integer coefficients

**Proposed fix.** Multiply through by the LCD.

**Occurrences** (1 parts, 4 marks): Y420 jun25 Q5 [4, AWKWARD]

**Test cases (mark scheme answers):**

- Y420 jun25 Q5: 16y³ - 24y² + 6y + 5 = 0

### 57. AO — No induction tool for nth derivatives

**Proposed fix.** Add `fcore » Induction: nth derivative` (`f(x),g(n,x)`).

**Occurrences** (1 parts, 4 marks): Y420 jun25 Q8a [4, GAP]

### 58. AP — 2-D point-to-line distance / circle tangent to a locus

**Proposed fix.** Add a 2-D distance tool for loci (point to half-line).

**Occurrences** (1 parts, 4 marks): Y420 spec Q2(ii) [4, AWKWARD]

### 59. AT — Distribution of sums/differences of discrete RVs

**Proposed fix.** Add a convolution tool for small discrete distributions (B, Po) giving P(T = t).

**Occurrences** (1 parts, 4 marks): Y422 jun25 Q10a [4, GAP]

**Test cases (mark scheme answers):**

- Y422 jun25 Q10a: X ~ B(6,0.4), T = X - (Y1+Y2), Y ~ B(3,0.4) → P(T = 5) = 0.002484

### 60. AX — Two independent values: one below, one above

**Proposed fix.** Add P(one < c < other) = 2p(1-p) to `Rectangular U(a,b)`.

**Occurrences** (2 parts, 4 marks): Y422 jun23 Q8a [2, AWKWARD]; Y422 jun25 Q5b [2, AWKWARD]

### 61. AC2 — Describe a 2x2 cannot split a matrix into two standard transformations

**Proposed fix.** Offer a decomposition (reflection/rotation × shear/stretch) when the matrix is not standard.

**Occurrences** (1 parts, 3 marks): Y420 nov21 Q9c(i) [3, GAP]

**Test cases (mark scheme answers):**

- Y420 nov21 Q9c: [[-1,0],[-2,1]] = shear [[1,0],[2,1]] after reflection in the y-axis

### 62. AI — Matrix tools reject complex entries

**Proposed fix.** Allow complex entries in 2x2 products/inverses.

**Occurrences** (1 parts, 3 marks): Y435 nov20 Q4b(i) [3, GAP]

### 63. AR — No "verify a DE solution" tool

**Proposed fix.** Add `fcalc » Verify DE solution` (`DE,y(x)`) substituting and simplifying; keep letter case (A was lowercased).

**Occurrences** (1 parts, 3 marks): Y420 nov20 Q16a(ii) [3, AWKWARD]

### 64. AV — Stats tools want raw data, not a frequency table

**Proposed fix.** Accept value-frequency pairs in `Poisson model check` and print s² with divisor n-1.

**Occurrences** (1 parts, 3 marks): Y422 nov21 Q6a [3, AWKWARD]

### 65. AW — No CI back-solver

**Proposed fix.** Add `CI -> xbar, s` (`lo,hi,n,conf%`).

**Occurrences** (1 parts, 3 marks): Y422 nov21 Q7d(i) [3, AWKWARD]

### 66. U3 — No general term for Maclaurin series

**Proposed fix.** Print a general term when the derivatives follow a pattern (sinh² x: 2^(n-1)/n! for even n).

**Occurrences** (1 parts, 3 marks): Y420 nov20 Q13d [3, GAP]

### 67. X2 — nCr written as 10C4 is misread as 10·C·4

**Proposed fix.** Parse `nCr`/`nPr` infix (10C4) or reject with a message; also reject unknown function names like cbrt instead of turning them into variable products.

**Occurrences** (1 parts, 2 marks): Y422 nov20 Q1a [2, WRONG]

**Test cases (mark scheme answers):**

- Y422 nov20 Q1a: 1/10C4 = 1/210

### 68. AD2 — Invariant lines not through the origin

**Proposed fix.** Report families y = mx + c invariant (e.g. all lines y = c for a stretch parallel to x).

**Occurrences** (1 parts, 2 marks): Y420 jun23 Q6d [2, AWKWARD]

### 69. AF6 — 2nd order + f(n) prints no limit line

**Proposed fix.** Print convergence and the limit (as the homogeneous tool does).

**Occurrences** (1 parts, 2 marks): Y435 jun25 Q2c [2, AWKWARD]

### 70. AU — E(g(X)) cannot take a piecewise g

**Proposed fix.** Allow per-value g entries.

**Occurrences** (1 parts, 2 marks): Y422 nov20 Q1d [2, AWKWARD]

### 71. H2 — Parametric elimination with hyperbolic identities

**Proposed fix.** Teach `Param to Cartesian` cosh² - sinh² = 1 and (cosh+sinh)(cosh-sinh) = 1.

**Occurrences** (1 parts, 2 marks): Y420 spec Q6(i) [2, GAP]

**Test cases (mark scheme answers):**

- Y420 spec Q6(i): x = cosh t + sinh t, y = cosh t - sinh t → xy = 1

### 72. V3 — Sum f(r) refuses non-polynomial f

**Proposed fix.** Fall back to numeric summation (as mpure Sigma sum does) instead of "f(r) must be a polynomial in r".

**Occurrences** (1 parts, 2 marks): Y420 spec Q11(i) [2, AWKWARD]

### 73. U1 — Maclaurin series capped at n = 8

**Proposed fix.** Raise the cap (or let n mean "number of non-zero terms") so ln(1+x³) to x⁹ works.

**Occurrences** (1 parts, 1 marks): Y420 jun24 Q10a [1, WRONG]

**Test cases (mark scheme answers):**

- Y420 jun24 Q10a: ln(1+x³) ≈ x³ - x⁶/2 + x⁹/3

## Regression cases from OK rows

One JSON object per line: paper, q, module (`CAS` and `CALC` are the home-screen apps; CAS inputs are `f(x) ; ask`), label, inputs as typed, and a substring the output must contain. All 455 lines were re-run against the current code and pass.

```jsonl
{"paper": "y420-jun19", "q": "1", "module": "fcore", "label": "Sum f(r), r = a..b", "inputs": "2r^2-1,1", "expected": "2*n^3/3+n^2-2*n/3"}
{"paper": "y420-jun19", "q": "3a", "module": "fcore", "label": "Inverse 2x2", "inputs": "3,1,2,1", "expected": "[1 -1]"}
{"paper": "y420-jun19", "q": "4", "module": "fcalc", "label": "Volume about x-axis", "inputs": "sec(x/2),0,pi/2", "expected": "V = 2pi"}
{"paper": "y420-jun19", "q": "5", "module": "fcore", "label": "Maclaurin series", "inputs": "sin(x)^2,6", "expected": "2*x^6/45-x^4/3+x^2"}
{"paper": "y420-jun19", "q": "6", "module": "fcalc", "label": "Integral to infinity", "inputs": "1/(4+x^2),2", "expected": "integral = pi/8"}
{"paper": "y420-jun19", "q": "7c", "module": "fcalc", "label": "Polar area", "inputs": "sqrt(sin(2x)),0,pi/2", "expected": "area = 1/2"}
{"paper": "y420-jun19", "q": "9", "module": "fcore", "label": "Induction: divisor", "inputs": "5^n+2*11^n,3", "expected": "3 divides f(n): proved"}
{"paper": "y420-jun19", "q": "10a", "module": "fcore", "label": "De Moivre z^n", "inputs": "-1+i,3", "expected": "z^3 = 2+2i"}
{"paper": "y420-jun19", "q": "11a", "module": "fcore", "label": "Describe a 2x2", "inputs": "3/5,-4/5,4/5,3/5", "expected": "rotation 53.1 deg about O"}
{"paper": "y420-jun19", "q": "11a", "module": "fcore", "label": "Describe a 2x2", "inputs": "1,0,0,-1", "expected": "reflection in the x-axis"}
{"paper": "y420-jun19", "q": "11b", "module": "fcore", "label": "A then B (2x2)", "inputs": "1,0,0,-1,3/5,-4/5,4/5,3/5", "expected": "[3/5 4/5]"}
{"paper": "y420-jun19", "q": "11b", "module": "fcore", "label": "Invariant points/lines", "inputs": "3/5,4/5,4/5,-3/5", "expected": "line of invariant points y = 1/2x"}
{"paper": "y420-jun19", "q": "11c", "module": "fcore", "label": "Describe a 2x2", "inputs": "3/5,-4/5,-4/5,-3/5", "expected": "reflection in y = x tan -26.6 deg"}
{"paper": "y420-jun19", "q": "12", "module": "fcore", "label": "Intersect two lines", "inputs": "0,0,0,2,3,1,1,2,-4,1,1,5", "expected": "they meet at (2, 3, 1)"}
{"paper": "y420-jun19", "q": "12", "module": "fcore", "label": "Intersect two lines", "inputs": "0,0,0,1,2,-4,1,2,-4,1,1,5", "expected": "they meet at (1, 2, -4)"}
{"paper": "y420-jun19", "q": "12", "module": "fcore", "label": "Area of triangle", "inputs": "0,0,0,2,3,1,1,2,-4", "expected": "area = sqrt(278)/2"}
{"paper": "y420-jun19", "q": "13a", "module": "fcalc", "label": "d/dx hyperbolic", "inputs": "acosh(x)", "expected": "1/sqrt(x^2-1)"}
{"paper": "y420-jun19", "q": "15", "module": "CAS", "label": "complete the square", "inputs": "4x^2-4x+2", "expected": "4*(x-1/2)^2+1"}
{"paper": "y420-jun19", "q": "17c(ii)", "module": "CALC", "label": "Calculate", "inputs": "20*(e^0.5-1)", "expected": "12.97442541"}
{"paper": "y420-jun19", "q": "17e(i)", "module": "fcalc", "label": "Integrating factor", "inputs": "1/10,x,0,0", "expected": "C = 100"}
{"paper": "y420-jun19", "q": "17e(ii)", "module": "CAS", "label": "solve f(x)=0", "inputs": "20*(e^0.5-1)-10x*(5-10+10*e^(-0.5))", "expected": "x = 1.22"}
{"paper": "y420-jun19", "q": "17f", "module": "CAS", "label": "definite integral a..b", "inputs": "20*(e^(1-0.1x)-1) ; 5,10", "expected": "200*sqrt(e)-300"}
{"paper": "y420-jun22", "q": "1a", "module": "fcore", "label": "Sum f(r), r = a..b", "inputs": "3r^2+3r+1,1", "expected": "n^3+3*n^2+3*n"}
{"paper": "y420-jun22", "q": "1b", "module": "fcore", "label": "Sum f(r), r = a..b", "inputs": "r(r+1),1", "expected": "n^3/3+n^2+2*n/3"}
{"paper": "y420-jun22", "q": "2", "module": "fcalc", "label": "Integral to infinity", "inputs": "1/(x^2-4x+5),3", "expected": "integral = pi/4"}
{"paper": "y420-jun22", "q": "4a", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "k,2,1,0,1,-2,2,0,3", "expected": "singular when k = 10/3"}
{"paper": "y420-jun22", "q": "5b", "module": "fcalc", "label": "Polar area", "inputs": "1-cos(x),0,2pi", "expected": "area = 3pi/2"}
{"paper": "y420-jun22", "q": "6", "module": "fcore", "label": "Induction: M^n", "inputs": "2,0,-1,1,2^n,0,1-2^n,1", "expected": "Proved for all n >= 1"}
{"paper": "y420-jun22", "q": "7", "module": "CAS", "label": "partial fractions", "inputs": "(x+1)/((x-1)(x^2+1))", "expected": "-x/(x^2+1)"}
{"paper": "y420-jun22", "q": "8a", "module": "fcore", "label": "Locus arg(z-z1) = t", "inputs": "10,3pi/4", "expected": "y = -(x-10)"}
{"paper": "y420-jun22", "q": "8b", "module": "fcore", "label": "Modulus-argument", "inputs": "-3+4i", "expected": "z = 5(cos"}
{"paper": "y420-jun22", "q": "8b", "module": "mpure", "label": "Line meets circle", "inputs": "-1,10,3,6,5", "expected": "(7, 3)"}
{"paper": "y420-jun22", "q": "9b(i)", "module": "fcalc", "label": "d/dx hyperbolic", "inputs": "ln(1+sinh(x))", "expected": "cosh(x)/(sinh(x)+1)"}
{"paper": "y420-jun22", "q": "9c", "module": "fcore", "label": "Maclaurin series", "inputs": "ln(1+sinh(x)),2", "expected": "-x^2/2+x"}
{"paper": "y420-jun22", "q": "11b", "module": "fcore", "label": "nth roots of z", "inputs": "8i,3", "expected": "w0 = sqrt(3)+i"}
{"paper": "y420-jun22", "q": "12", "module": "fcalc", "label": "Integrating factor", "inputs": "-x/(4-x^2),1/(4-x^2),0,1", "expected": "(asin(x/2)+2)/sqrt(-x^2+4)"}
{"paper": "y420-jun22", "q": "13a", "module": "fcore", "label": "Angle line and plane", "inputs": "6,4,-2,1,-2,0", "expected": "= 6.86 deg"}
{"paper": "y420-jun22", "q": "13b", "module": "fcore", "label": "Line meets plane", "inputs": "4,0,-1,6,4,-2,1,-2,0,5", "expected": "meets at (1, -2, 0)"}
{"paper": "y420-jun22", "q": "13b", "module": "fcore", "label": "Line meets plane", "inputs": "4,0,-1,6,4,-2,2,3,-1,-4", "expected": "meets at (1, -2, 0)"}
{"paper": "y420-jun22", "q": "13c(i)", "module": "fcore", "label": "Vector product", "inputs": "1,-2,0,2,3,-1", "expected": "a x b = (2, 1, 7)"}
{"paper": "y420-jun22", "q": "13c(ii)", "module": "fcore", "label": "Angle between planes", "inputs": "1,-2,0,2,3,-1", "expected": "= 61.4 deg"}
{"paper": "y420-jun22", "q": "13c(iii)", "module": "fcore", "label": "Two planes meet", "inputs": "1,-2,0,5,2,3,-1,-4", "expected": "r = (1, -2, 0) + t(2, 1, 7)"}
{"paper": "y420-jun22", "q": "13c(iii)", "module": "fcore", "label": "Point to line dist", "inputs": "4,0,-1,1,-2,0,2,1,7", "expected": "distance = 3.74"}
{"paper": "y420-jun22", "q": "15a(iii)", "module": "fcalc", "label": "SHM from omega", "inputs": "sqrt(2),2,1", "expected": "period T = 4.44"}
{"paper": "y420-jun22", "q": "15a(iv)", "module": "fcalc", "label": "Second order with IVs", "inputs": "1,0,2,2,1", "expected": "2*cos(sqrt(2)*x)+(sqrt(2)/2)*sin(sqrt(2)*x)"}
{"paper": "y420-jun22", "q": "15a(v)", "module": "fcalc", "label": "SHM from omega", "inputs": "sqrt(2),2,1", "expected": "amplitude R = 3sqrt(2)/2"}
{"paper": "y420-jun22", "q": "15b(ii)", "module": "fcalc", "label": "Damping classify", "inputs": "1,2,2", "expected": "light damping"}
{"paper": "y420-jun22", "q": "15b(iii)", "module": "fcalc", "label": "Second order homogen", "inputs": "1,2,2", "expected": "(A*cos(x)+B*sin(x))*e^(-x)"}
{"paper": "y420-jun22", "q": "15c(i)", "module": "fcalc", "label": "PI for m cos + n sin", "inputs": "1,2,2,2,0,2,2,1", "expected": "(11*cos(x)/5+12*sin(x)/5)*e^(-x)+2*sin(2*x)/5-cos(2*x)/5"}
{"paper": "y420-jun23", "q": "1b(i)", "module": "fcore", "label": "Arithmetic z, w", "inputs": "5+sqrt(3)i,2-sqrt(3)i", "expected": "z/w = 1+sqrt(3)i"}
{"paper": "y420-jun23", "q": "1b(ii)", "module": "fcore", "label": "Modulus-argument", "inputs": "1+sqrt(3)i", "expected": "z = 2(cos pi/3 + i sin pi/3)"}
{"paper": "y420-jun23", "q": "2", "module": "fcore", "label": "Angle line and plane", "inputs": "3,2,1,-1,3,2", "expected": "= 20.9 deg"}
{"paper": "y420-jun23", "q": "3a", "module": "fcore", "label": "Method of differences", "inputs": "1/(r(r+2))", "expected": "S(n) = 3/4 - (1/(2*n+2)+1/(2*n+4))"}
{"paper": "y420-jun23", "q": "3b", "module": "fcore", "label": "Method of differences", "inputs": "1/(r(r+2))", "expected": "S(n) -> 3/4"}
{"paper": "y420-jun23", "q": "4a(i)", "module": "CAS", "label": "d2/dx2", "inputs": "sqrt(1+2x)", "expected": "-1/((2*x+1)*sqrt(2*x+1))"}
{"paper": "y420-jun23", "q": "4a(ii)", "module": "fcore", "label": "Maclaurin series", "inputs": "sqrt(1+2x),2", "expected": "-x^2/2+x+1"}
{"paper": "y420-jun23", "q": "4b", "module": "CALC", "label": "Calculate", "inputs": "2*(1+1/8-1/128)", "expected": "143/64"}
{"paper": "y420-jun23", "q": "6a", "module": "fcore", "label": "AB and BA (2x2)", "inputs": "0,1,1,0,2,0,0,1", "expected": "AB is not BA"}
{"paper": "y420-jun23", "q": "6b(i)", "module": "fcore", "label": "Describe a 2x2", "inputs": "0,1,1,0", "expected": "reflection in y = x"}
{"paper": "y420-jun23", "q": "6b(ii)", "module": "fcore", "label": "Describe a 2x2", "inputs": "2,0,0,1", "expected": "stretch parallel to x-axis, sf 2"}
{"paper": "y420-jun23", "q": "7a", "module": "fcalc", "label": "Plot r = f(theta)", "inputs": "1-2sin(x)", "expected": "r(3pi/2) = 3"}
{"paper": "y420-jun23", "q": "7b", "module": "CAS", "label": "general solution (trig)", "inputs": "1-2sin(x)", "expected": "x = 2*n*pi+5*pi/6"}
{"paper": "y420-jun23", "q": "8", "module": "fcore", "label": "Induction: divisor", "inputs": "8^n-3^n,5", "expected": "5 divides f(n): proved"}
{"paper": "y420-jun23", "q": "9", "module": "fcalc", "label": "Mean value of f", "inputs": "sin(2x)^2,0,pi", "expected": "mean = 1/2"}
{"paper": "y420-jun23", "q": "11", "module": "fcalc", "label": "Integrating factor", "inputs": "-2tanh(x),1,0,1", "expected": "cosh(x)^2*(tanh(x)+1)"}
{"paper": "y420-jun23", "q": "12", "module": "fcore", "label": "cos^n t, sin^n t", "inputs": "5", "expected": "sin^5 t = (sin5t-5sin3t+10sin t)/16"}
{"paper": "y420-jun23", "q": "13b", "module": "fcore", "label": "Locus |z-z1|=|z-z2|", "inputs": "-2+4i,2+6i", "expected": "y = -2x + 5"}
{"paper": "y420-jun23", "q": "13b", "module": "mpure", "label": "Line meets circle", "inputs": "-2,5,0,0,sqrt(5)", "expected": "tangent at (2, 1)"}
{"paper": "y420-jun23", "q": "14a", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "k,0,-1,-1,k,2,2k,2,3", "expected": "no real k makes it singular"}
{"paper": "y420-jun23", "q": "15", "module": "fcalc", "label": "Int 1/sqrt(a2-x2)", "inputs": "sqrt(2),0,1", "expected": "integral = pi/4"}
{"paper": "y420-jun23", "q": "15", "module": "CAS", "label": "definite integral a..b", "inputs": "1/sqrt(1+2x-x^2) ; 1,2", "expected": "integral = pi/4"}
{"paper": "y420-jun23", "q": "16", "module": "fcore", "label": "Point to plane dist", "inputs": "4,1,0,2,1,2,0", "expected": "distance = 3"}
{"paper": "y420-jun23", "q": "17c(i)", "module": "CALC", "label": "Calculate", "inputs": "-50e^(0.035*25)+550e^(-0.005*25)", "expected": "365.4295317"}
{"paper": "y420-jun23", "q": "17c(i)", "module": "CALC", "label": "Calculate", "inputs": "275e^(-0.005*25)+25e^(0.035*25)", "expected": "302.6585306"}
{"paper": "y420-jun23", "q": "17c(ii)", "module": "mcalc", "label": "Newton-Raphson", "inputs": "-75e^(0.035x)+275e^(-0.005x),30", "expected": "x = 32.482075"}
{"paper": "y420-jun24", "q": "1", "module": "CAS", "label": "single fraction", "inputs": "1/(x+1)-1/(x+2)", "expected": "1/((x+1)*(x+2))"}
{"paper": "y420-jun24", "q": "1", "module": "fcore", "label": "Method of differences", "inputs": "1/((r+1)(r+2))", "expected": "S(n) = 1/2 - (1/(n+2))"}
{"paper": "y420-jun24", "q": "2a(i)", "module": "fcore", "label": "Arithmetic z, w", "inputs": "-1+i,-2-i", "expected": "z-w = 1+2i"}
{"paper": "y420-jun24", "q": "2a(ii)", "module": "fcore", "label": "Arithmetic z, w", "inputs": "-1+i,-2-i", "expected": "z/w = 1/5-3i/5"}
{"paper": "y420-jun24", "q": "2b", "module": "fcore", "label": "Modulus-argument", "inputs": "-1+i", "expected": "z = sqrt(2)(cos 3pi/4 + i sin 3pi/4)"}
{"paper": "y420-jun24", "q": "3", "module": "fcore", "label": "Vieta root sums", "inputs": "2,-2,8,-15", "expected": "sum of squares = e1^2 - 2e2 = -7"}
{"paper": "y420-jun24", "q": "5b", "module": "fcore", "label": "Scalar product, angle", "inputs": "-2,1,2,-3,0,1", "expected": "= 32.5 deg"}
{"paper": "y420-jun24", "q": "7b", "module": "CAS", "label": "definite integral a..b", "inputs": "(x-2)^(-1/3) ; 1,2", "expected": "-3/2"}
{"paper": "y420-jun24", "q": "8a", "module": "fcore", "label": "Describe a 2x2", "inputs": "1,3,0,1", "expected": "shear, x-axis fixed, factor 3"}
{"paper": "y420-jun24", "q": "8b(i)", "module": "fcore", "label": "Determinant 2x2", "inputs": "1,3,0,1", "expected": "det A = 1"}
{"paper": "y420-jun24", "q": "8b(ii)", "module": "fcore", "label": "Determinant 2x2", "inputs": "1,3,0,1", "expected": "det > 0: orientation is preserved"}
{"paper": "y420-jun24", "q": "9b", "module": "fcalc", "label": "Polar area", "inputs": "sin(3x),0,pi/3", "expected": "area = pi/12"}
{"paper": "y420-jun24", "q": "10a", "module": "CAS", "label": "series (Maclaurin)", "inputs": "ln(1+x^3) ; 10", "expected": "x^9/3-x^6/2+x^3"}
{"paper": "y420-jun24", "q": "10b", "module": "CALC", "label": "Calculate", "inputs": "1/8-1/128+1/1536", "expected": "181/1536"}
{"paper": "y420-jun24", "q": "11a", "module": "fcore", "label": "Point to plane dist", "inputs": "8,4,5,2,-1,2,4", "expected": "distance = 6"}
{"paper": "y420-jun24", "q": "11b", "module": "fcore", "label": "Is p on (r-a)xb=0", "inputs": "2,0,-3,3,2,4,8,4,5", "expected": "p is on the line"}
{"paper": "y420-jun24", "q": "11c", "module": "fcore", "label": "Line meets plane", "inputs": "2,0,-3,3,2,4,2,-1,2,4", "expected": "meets at (7/2, 1, -1)"}
{"paper": "y420-jun24", "q": "11d", "module": "fcore", "label": "Angle line and plane", "inputs": "3,2,4,2,-1,2", "expected": "= 48 deg"}
{"paper": "y420-jun24", "q": "11e", "module": "CALC", "label": "Calculate", "inputs": "sqrt((8-7/2)^2+3^2+6^2)*sin(48.0*pi/180)", "expected": "6.002936041"}
{"paper": "y420-jun24", "q": "12a(i)", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "cosh(x)-2sinh(x)", "expected": "x = ln(3)/2"}
{"paper": "y420-jun24", "q": "12a(ii)", "module": "CALC", "label": "Calculate", "inputs": "2cosh(ln(3)/2)+sinh(ln(3)/2)", "expected": "2.886751346"}
{"paper": "y420-jun24", "q": "12b", "module": "mcalc", "label": "Parametric dy/dx", "inputs": "2cosh(t)+sinh(t),cosh(t)-2sinh(t),0", "expected": "at t = 0: dy/dx = -2"}
{"paper": "y420-jun24", "q": "14a", "module": "fcalc", "label": "PI for k e^(px)", "inputs": "1,1,-2,12,-1", "expected": "A*e^(x)+B*e^(-2*x)-6*e^(-x)"}
{"paper": "y420-jun24", "q": "14b", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "3e^(-2x)-6e^(-x)", "expected": "x = -ln(2)"}
{"paper": "y420-jun24", "q": "15a", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "1,k,3,3,4,2,1,3,-1", "expected": "singular when k = -1"}
{"paper": "y420-jun24", "q": "17c(i)", "module": "CALC", "label": "Calculate", "inputs": "10*100*ln(2)", "expected": "693.1471806"}
{"paper": "y420-jun24", "q": "17c(ii)", "module": "mcalc", "label": "Newton-Raphson", "inputs": "-10ln(200/(200-x))+10,100", "expected": "x = 126.42411"}
{"paper": "y420-jun25", "q": "1", "module": "fcore", "label": "Solve az + bz* = c", "inputs": "1,2i,-1+4i", "expected": "z = 3-2i"}
{"paper": "y420-jun25", "q": "2", "module": "fcore", "label": "Angle between planes", "inputs": "2,-1,2,1,2,1", "expected": "= 74.2 deg"}
{"paper": "y420-jun25", "q": "3", "module": "fcore", "label": "Sum f(r), r = a..b", "inputs": "r(r+2),1", "expected": "n^3/3+3*n^2/2+7*n/6"}
{"paper": "y420-jun25", "q": "6b", "module": "fcalc", "label": "Plot r = f(theta)", "inputs": "sqrt(sin(2x)/2)", "expected": "= sqrt(2)/2 at th = pi/4"}
{"paper": "y420-jun25", "q": "6c", "module": "fcalc", "label": "Polar area", "inputs": "sqrt(sin(2x)/2),0,pi/2", "expected": "area = 1/4"}
{"paper": "y420-jun25", "q": "8b", "module": "fcore", "label": "Maclaurin series", "inputs": "ln(1+x),5", "expected": "term r: (-1)^(r+1) x^r/r"}
{"paper": "y420-jun25", "q": "9a(iii)", "module": "fcore", "label": "Roots of unity", "inputs": "5", "expected": "1 + w + ... + w^4 = 0"}
{"paper": "y420-jun25", "q": "9b(i)", "module": "fcore", "label": "Roots of unity", "inputs": "5", "expected": "w = e^(2pi i/5)"}
{"paper": "y420-jun25", "q": "10", "module": "CAS", "label": "definite integral a..b", "inputs": "2/(x^2-x+1) ; 0,1/2", "expected": "2*pi*sqrt(3)/9"}
{"paper": "y420-jun25", "q": "11b(ii)", "module": "fcore", "label": "Distance two lines", "inputs": "3,-1,2,-1/2,2,1,2,1,3,-1,4,2", "expected": "distance = 0.488"}
{"paper": "y420-jun25", "q": "13a", "module": "fcalc", "label": "Integrating factor", "inputs": "-2/x,(2+x^2)/x,1,0", "expected": "1/x^2"}
{"paper": "y420-jun25", "q": "13b", "module": "fcalc", "label": "Integrating factor", "inputs": "-2/x,(2+x^2)/x,1,0", "expected": "(ln(|x|)-1/x^2+1)*x^2"}
{"paper": "y420-jun25", "q": "14c", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "cosh(2x)-4", "expected": "x = ln(sqrt(15)+4)/2"}
{"paper": "y420-jun25", "q": "17a(iii)", "module": "fcalc", "label": "Integrating factor", "inputs": "0.2,4,0,0", "expected": "(20*e^(x/5)-20)*e^(-x/5)"}
{"paper": "y420-jun25", "q": "17a(iv)", "module": "CALC", "label": "Calculate", "inputs": "20(1-e^(-1))", "expected": "12.64241118"}
{"paper": "y420-jun25", "q": "17b(i)", "module": "fcalc", "label": "PI polynomial RHS", "inputs": "1,0.3,0.02,2/5", "expected": "A*e^(-x/10)+B*e^(-x/5)+20"}
{"paper": "y420-jun25", "q": "17b(iii)", "module": "fcalc", "label": "PI for k e^(px)", "inputs": "1,0.3,0.02,0.4,0,0,2.9", "expected": "-11*e^(-x/10)-9*e^(-x/5)+20"}
{"paper": "y420-jun25", "q": "17b(iii)", "module": "CALC", "label": "Calculate", "inputs": "20-11e^(-0.5)-9e^(-1)", "expected": "10.01724777"}
{"paper": "y420-nov20", "q": "1", "module": "fcore", "label": "Sum f(r), r = a..b", "inputs": "r(r+1)(r+3),1", "expected": "n^4/4+11*n^3/6+15*n^2/4+13*n/6"}
{"paper": "y420-nov20", "q": "3", "module": "CAS", "label": "definite integral a..b", "inputs": "1/sqrt(4-9x^2) ; 0,1/3", "expected": "pi/18"}
{"paper": "y420-nov20", "q": "4a", "module": "fcore", "label": "Vieta root sums", "inputs": "2,0,-5,7", "expected": "sum of 1/root = 5/7"}
{"paper": "y420-nov20", "q": "4b", "module": "fcore", "label": "Roots p a + q", "inputs": "2,-1,2,0,-5,7", "expected": "2*x^3+6*x^2-14*x+38"}
{"paper": "y420-nov20", "q": "5c", "module": "fcalc", "label": "Polar area", "inputs": "3+2cos(x),-pi,pi", "expected": "area = 11pi"}
{"paper": "y420-nov20", "q": "7", "module": "fcore", "label": "Induction: sum", "inputs": "r*r!,(n+1)!-1", "expected": "Proved for all n >= 1"}
{"paper": "y420-nov20", "q": "8b", "module": "fcore", "label": "Angle between lines", "inputs": "-1,1,3,2,3,4", "expected": "= 43.3 deg"}
{"paper": "y420-nov20", "q": "9b", "module": "fcore", "label": "Invariant points/lines", "inputs": "1,-2,-4,3", "expected": "invariant line y = -2x"}
{"paper": "y420-nov20", "q": "11b", "module": "fcore", "label": "Modulus-argument", "inputs": "3/4+sqrt(3)i/4", "expected": "z = sqrt(3)/2e^(i pi/6)"}
{"paper": "y420-nov20", "q": "11c", "module": "fcore", "label": "De Moivre z^n", "inputs": "3/2+sqrt(3)i/2,6", "expected": "z^6 = -27"}
{"paper": "y420-nov20", "q": "12a", "module": "fcore", "label": "cos^n t, sin^n t", "inputs": "3", "expected": "z - 1/z = 2i sin t, z^m + 1/z^m = 2cos mt"}
{"paper": "y420-nov20", "q": "14", "module": "fcalc", "label": "Coupled equations", "inputs": "-2,4,-3,5,0,1", "expected": "4*e^(2*t)-4*e^(t)"}
{"paper": "y420-nov20", "q": "15a", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "1,k,3,2,1,5,1,-2,2", "expected": "singular when k = 3"}
{"paper": "y420-nov20", "q": "15b", "module": "fcore", "label": "Solve 3 eqns by A^-1", "inputs": "1,-2,3,2,1,5,1,-2,2,-12,-11,-9", "expected": "x = 1"}
{"paper": "y420-nov20", "q": "15c", "module": "fcore", "label": "Line from two points", "inputs": "1,1,-2,3,0,-4", "expected": "r = (1, 1, -2) + t(2, -1, -2)"}
{"paper": "y420-nov20", "q": "15d", "module": "fcore", "label": "Point to line dist", "inputs": "1,2,-3,1,1,-2,2,-1,-2", "expected": "distance = sqrt(17)/3"}
{"paper": "y420-nov20", "q": "15e(i)", "module": "fcore", "label": "Line meets plane", "inputs": "1,1,-2,2,-1,-2,1,-2,2,-9", "expected": "parallel, never meets"}
{"paper": "y420-nov20", "q": "15e(ii)", "module": "fcore", "label": "Point to plane dist", "inputs": "1,1,-2,1,-2,2,-9", "expected": "distance = 4/3"}
{"paper": "y420-nov20", "q": "16b", "module": "CAS", "label": "partial fractions", "inputs": "1/(x*(1+x^2))", "expected": "-x/(x^2+1)"}
{"paper": "y420-nov20", "q": "16c(ii)", "module": "CAS", "label": "solve f(x)=0", "inputs": "x/sqrt(1+x^2)-1/2", "expected": "x = 0.577"}
{"paper": "y420-nov20", "q": "16e", "module": "CALC", "label": "Calculate", "inputs": "10*(37/60)/sqrt(1+(37/60)^2)", "expected": "5.25"}
{"paper": "y420-nov20", "q": "16e", "module": "CALC", "label": "Calculate", "inputs": "(10*(37/60)-(37/60)*e^(-37/60))/sqrt(1+(37/60)^2)", "expected": "4.97"}
{"paper": "y420-nov21", "q": "1b", "module": "CAS", "label": "single fraction", "inputs": "1/2-1/(4x+2)", "expected": "x/(2*x+1)"}
{"paper": "y420-nov21", "q": "2", "module": "fcalc", "label": "d/dx inverse trig", "inputs": "6asin(2x),1/4", "expected": "f'(1/4) = 8sqrt(3)"}
{"paper": "y420-nov21", "q": "3a", "module": "fcore", "label": "Modulus-argument", "inputs": "-2+2i", "expected": "arg z = 3pi/4 rad"}
{"paper": "y420-nov21", "q": "3b", "module": "fcore", "label": "Multiply in mod-arg", "inputs": "sqrt(8),3pi/4,2,pi/6", "expected": "z/w: r = sqrt(2), arg = 7pi/12"}
{"paper": "y420-nov21", "q": "4", "module": "fcalc", "label": "Mean value of f", "inputs": "1/(1+4x^2),-1,1", "expected": "mean = 0.554"}
{"paper": "y420-nov21", "q": "5a", "module": "fcore", "label": "Maclaurin series", "inputs": "ln(1+2x),2", "expected": "-2*x^2+2*x"}
{"paper": "y420-nov21", "q": "5c", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln(1+2x),2,1", "expected": "x = 1 is outside the interval"}
{"paper": "y420-nov21", "q": "6", "module": "fcore", "label": "Invariant points/lines", "inputs": "1,2,2,-2", "expected": "invariant line y = -2x"}
{"paper": "y420-nov21", "q": "7", "module": "fcore", "label": "Induction: sum", "inputs": "r/2^(r-1),4-(n+2)/2^(n-1)", "expected": "Proved for all n >= 1"}
{"paper": "y420-nov21", "q": "9b(i)", "module": "fcore", "label": "Determinant 2x2", "inputs": "-1,0,-2,1", "expected": "det A = -1"}
{"paper": "y420-nov21", "q": "9b(ii)", "module": "fcore", "label": "Determinant 2x2", "inputs": "-1,0,-2,1", "expected": "det < 0: orientation is reversed"}
{"paper": "y420-nov21", "q": "9c(ii)", "module": "fcore", "label": "A then B (2x2)", "inputs": "-1,0,0,1,1,0,2,1", "expected": "[-2 1]"}
{"paper": "y420-nov21", "q": "10a", "module": "fcore", "label": "Roots of unity", "inputs": "3", "expected": "w^1 = -1/2+sqrt(3)i/2"}
{"paper": "y420-nov21", "q": "10b(iii)", "module": "fcore", "label": "nth roots of z", "inputs": "1+sqrt(3)i,3", "expected": "sum = 0"}
{"paper": "y420-nov21", "q": "11b(i)", "module": "fcore", "label": "Angle between planes", "inputs": "2,1,-3,1,2,-2", "expected": "= 27 deg"}
{"paper": "y420-nov21", "q": "11b(ii)", "module": "fcore", "label": "Distance two lines", "inputs": "3,0,2,3,1,-3,0,4,-2,1,2,-2", "expected": "distance = 2sqrt(2)"}
{"paper": "y420-nov21", "q": "13", "module": "fcalc", "label": "PI for k e^(px)", "inputs": "1,2,-3,2,1", "expected": "A*e^(x)+B*e^(-3*x)+e^(x)*x/2"}
{"paper": "y420-nov21", "q": "14a", "module": "fcalc", "label": "Plot r = f(theta)", "inputs": "cos(x)+2sin(x)", "expected": "= 2.24 at th = 1.1"}
{"paper": "y420-nov21", "q": "14b(ii)", "module": "fcalc", "label": "Cartesian to polar", "inputs": "1/2,1", "expected": "r = sqrt(5)/2"}
{"paper": "y420-nov21", "q": "15", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "-4,k,7,1,-2,5,2,3,1", "expected": "singular when k = -13"}
{"paper": "y420-nov21", "q": "17b(i)", "module": "fcalc", "label": "Separable DE", "inputs": "1,1-y,0,0", "expected": "-e^(-x)+1"}
{"paper": "y420-nov21", "q": "17b(ii)", "module": "CAS", "label": "solve f(x)=0", "inputs": "1-e^(-x)-1/2", "expected": "x = 0.693"}
{"paper": "y420-nov21", "q": "17c(ii)", "module": "fcalc", "label": "Integrating factor", "inputs": "2/(1-x),1,0,0", "expected": "-x^2+x"}
{"paper": "y420-nov21", "q": "17c(ii)", "module": "CAS", "label": "stationary points", "inputs": "x(1-x)", "expected": "(0.5, 1/4)  max"}
{"paper": "y420-spec", "q": "1", "module": "fcore", "label": "Angle between lines", "inputs": "1,2,-1,3,1,-2", "expected": "= 40.2 deg"}
{"paper": "y420-spec", "q": "2(i)", "module": "fcore", "label": "Locus arg(z-z1) = t", "inputs": "4i,pi/4", "expected": "half-line from 4i"}
{"paper": "y420-spec", "q": "3(ii)(A)", "module": "fcore", "label": "Invariant points/lines", "inputs": "2,3,1,4", "expected": "invariant line y = x"}
{"paper": "y420-spec", "q": "3(ii)(B)", "module": "fcore", "label": "Invariant points/lines", "inputs": "2,3,1,4", "expected": "invariant line y = x"}
{"paper": "y420-spec", "q": "4", "module": "fcore", "label": "Cubic real coeffs", "inputs": "1,-5,11,-15", "expected": "z1 = 3"}
{"paper": "y420-spec", "q": "5(i)", "module": "CAS", "label": "partial fractions", "inputs": "2/((x+1)(x+3))", "expected": "-1/(x+3)"}
{"paper": "y420-spec", "q": "5(ii)", "module": "fcore", "label": "Method of differences", "inputs": "2/((r+1)(r+3))", "expected": "S(n) = 5/6 - (1/(n+2)+1/(n+3))"}
{"paper": "y420-spec", "q": "6(ii)", "module": "CAS", "label": "stationary points", "inputs": "2x+2/x", "expected": "(1, 4)  min"}
{"paper": "y420-spec", "q": "7(i)", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln(1+x),3,0.5", "expected": "series value 0.416667"}
{"paper": "y420-spec", "q": "7(ii)(A)", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln(1+x),3,0.5", "expected": "error = -0.0112"}
{"paper": "y420-spec", "q": "7(ii)(B)", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln(1+x),3,2", "expected": "x = 2 is outside the interval"}
{"paper": "y420-spec", "q": "7(iii)", "module": "fcore", "label": "Maclaurin series", "inputs": "ln((1+x)/(1-x)),3", "expected": "2*x^3/3+2*x"}
{"paper": "y420-spec", "q": "7(iv)(A)", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln((1+x)/(1-x)),3,0.2", "expected": "series value 0.405333"}
{"paper": "y420-spec", "q": "7(iv)(A)", "module": "fcore", "label": "Maclaurin approx", "inputs": "ln((1+x)/(1-x)),3,0.5", "expected": "series value 1.08333"}
{"paper": "y420-spec", "q": "8", "module": "fcore", "label": "Plane from 3 points", "inputs": "1,0,-1,2,2,1,1,1,2", "expected": "4x - 3y + z = 3"}
{"paper": "y420-spec", "q": "9(ii)", "module": "fcalc", "label": "Polar area", "inputs": "sin(3x),0,pi/3", "expected": "area = pi/12"}
{"paper": "y420-spec", "q": "10(i)", "module": "fcalc", "label": "Integrating factor", "inputs": "3/x,1/x^2,1,1", "expected": "(x^2/2+1/2)/x^3"}
{"paper": "y420-spec", "q": "10(ii)", "module": "CAS", "label": "d/dx", "inputs": "(1+x^2)/(2x^3)", "expected": "(-x^2/2-3/2)/x^4"}
{"paper": "y420-spec", "q": "11(ii)", "module": "fcore", "label": "Induction: sum", "inputs": "(r-1)/r!,1-1/n!", "expected": "Proved for all n >= 1"}
{"paper": "y420-spec", "q": "12(i)", "module": "fcalc", "label": "d/dx inverse trig", "inputs": "atan(x)", "expected": "1/(x^2+1)"}
{"paper": "y420-spec", "q": "12(ii)", "module": "fcalc", "label": "Mean value of f", "inputs": "1/(1+x^2),-1,1", "expected": "mean = pi/4"}
{"paper": "y420-spec", "q": "13(i)", "module": "fcore", "label": "Det 3x3 in terms of k", "inputs": "k,1,-5,2,3,-3,-1,2,2", "expected": "12*k-36"}
{"paper": "y420-spec", "q": "13(ii)", "module": "fcore", "label": "Solve 3 eqns by A^-1", "inputs": "4,1,-5,2,3,-3,-1,2,2,6,6,-6", "expected": "x = -6"}
{"paper": "y420-spec", "q": "13(iii)(B)", "module": "fcore", "label": "Three planes", "inputs": "3,1,-5,1,2,3,-3,1,-1,2,2,0", "expected": "sheaf: the planes share a line"}
{"paper": "y420-spec", "q": "13(iv)", "module": "CAS", "label": "solve f(x)=0", "inputs": "abs(12(x-3))-6", "expected": "x = 2.5, 3.5"}
{"paper": "y420-spec", "q": "14(iii)", "module": "fcore", "label": "cos^n t, sin^n t", "inputs": "6", "expected": "(cos6t+6cos4t+15cos2t+10)/32"}
{"paper": "y420-spec", "q": "16(i)(A)", "module": "fcalc", "label": "SHM from omega", "inputs": "pi", "expected": "period T = 2"}
{"paper": "y420-spec", "q": "16(i)(B)", "module": "fcalc", "label": "SHM from omega", "inputs": "pi", "expected": "C*cos(pi*t)+D*sin(pi*t)"}
{"paper": "y420-spec", "q": "16(iii)", "module": "CAS", "label": "solve f(x)=0", "inputs": "e^(-2pi*x/3)-0.98", "expected": "x = 0.00965"}
{"paper": "y420-spec", "q": "16(iv)", "module": "fcalc", "label": "Second order with IVs", "inputs": "1,0.019292,9.000093,0,12", "expected": "4*e^(-0.009646*x)*sin(3*x)"}
{"paper": "y422-jun19", "q": "1a", "module": "fstat", "label": "DRV find k", "inputs": "127-39x+3x^2,1,6", "expected": "k * 216 = 1"}
{"paper": "y422-jun19", "q": "1e", "module": "fstat", "label": "DRV from formula", "inputs": "(127-39x+3x^2)/216,1,6", "expected": "E(X) = 49/24"}
{"paper": "y422-jun19", "q": "2b", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.6,2", "expected": "P(X>=k) = 0.475"}
{"paper": "y422-jun19", "q": "2c", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "8,10", "expected": "P(X<=k) = 0.816"}
{"paper": "y422-jun19", "q": "2d", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "3.2,1", "expected": "P(X=k) = 0.13"}
{"paper": "y422-jun19", "q": "3a", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "205,121,5,1000", "expected": "P(sum<k) = 0.155"}
{"paper": "y422-jun19", "q": "3b", "module": "fstat", "label": "E and Var of a+bX", "inputs": "0,0.65,205,121", "expected": "Var(a+bX) = 51.1"}
{"paper": "y422-jun19", "q": "3b", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "133.25,7.15,0,150", "expected": "P(a<X<b) = 0.99"}
{"paper": "y422-jun19", "q": "4b", "module": "fstat", "label": "CI mean from data", "inputs": "95,2.36,2.97,2.69,3.00,2.51,2.45,2.21,2.63", "expected": "(2.37, 2.84)"}
{"paper": "y422-jun19", "q": "4c", "module": "fstat", "label": "CI mean from summary", "inputs": "8,2.6025,0.2793,95", "expected": "SE = s/sqrt(n) = 0.0987"}
{"paper": "y422-jun19", "q": "4d", "module": "fstat", "label": "CI mean from summary", "inputs": "8,2.6025,0.2793,95", "expected": "t* = 2.37 (df 7)"}
{"paper": "y422-jun19", "q": "5a", "module": "fstat", "label": "Chi-sq contributions", "inputs": "3,3,8,52,178,10,40,68,5,47,92", "expected": "E r3: 6.62 40 97.3"}
{"paper": "y422-jun19", "q": "5b", "module": "fstat", "label": "Chi-sq association", "inputs": "3,3,1,8,52,178,10,40,68,5,47,92", "expected": "reject H0 at 1%"}
{"paper": "y422-jun19", "q": "5c", "module": "fstat", "label": "Chi-sq contributions", "inputs": "3,3,8,52,178,10,40,68,5,47,92", "expected": "r1: -0.794 -3.03 +1.82"}
{"paper": "y422-jun19", "q": "6b(ii)", "module": "fstat", "label": "PMCC r", "inputs": "4.2,18,7.1,26,5.6,42,3.5,76,8.6,15,6.5,43,2.7,84,5.9,53,6.7,66,4.1,36", "expected": "r = -0.564"}
{"paper": "y422-jun19", "q": "6b(iii)", "module": "fstat", "label": "PMCC test from data", "inputs": "5,2,4.2,18,7.1,26,5.6,42,3.5,76,8.6,15,6.5,43,2.7,84,5.9,53,6.7,66,4.1,36", "expected": "crit = +/-0.632"}
{"paper": "y422-jun19", "q": "7a", "module": "fstat", "label": "CI mean from summary", "inputs": "40,0.1442,0.2580,95", "expected": "(0.0642, 0.224)"}
{"paper": "y422-jun19", "q": "7b", "module": "fstat", "label": "CI to test mu0", "inputs": "0.0642,0.2242,0.2", "expected": "mu0 inside the CI"}
{"paper": "y422-jun19", "q": "7d", "module": "fstat", "label": "Sample size for width", "inputs": "0.2580,0.12,95", "expected": "n = 72"}
{"paper": "y422-jun19", "q": "8a", "module": "fstat", "label": "Normal prob plot", "inputs": "26,28,29,30,31,32,34,42,49,54,55,56,61", "expected": "curved: Normal is doubtful"}
{"paper": "y422-jun19", "q": "8c", "module": "fstat", "label": "Wilcoxon single sample", "inputs": "33.5,5,1,26,28,29,30,31,32,34,42,49,54,55,56,61", "expected": "crit: reject if T <= 21"}
{"paper": "y422-jun19", "q": "9a", "module": "fstat", "label": "Rectangular U(a,b)", "inputs": "0,5,3,5", "expected": "P(c<X<d) = 2/5"}
{"paper": "y422-jun19", "q": "9e", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "2.5,25/12,5,18", "expected": "Var(X1+..+Xn) = 125/12"}
{"paper": "y422-jun19", "q": "9f", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "2.5,25/12,5,18", "expected": "P(sum<k) = 0.956"}
{"paper": "y422-jun19", "q": "9h", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "2.5,25/12,200,510", "expected": "P(sum<k) = 0.688"}
{"paper": "y422-jun19", "q": "10c(ii)", "module": "CAS", "label": "solve f(x)=0", "inputs": "2x^2-10x+5", "expected": "x = 0.564, 4.44"}
{"paper": "y422-jun19", "q": "10c(ii)", "module": "CALC", "label": "Calculate", "inputs": "ln(4.4365)/ln(2)", "expected": "2.149421968"}
{"paper": "y422-jun22", "q": "1a", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.2,2", "expected": "P(X=k) = 0.217"}
{"paper": "y422-jun22", "q": "1b", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.2,3", "expected": "P(X>k) = 1-P(X<=k) = 0.0338"}
{"paper": "y422-jun22", "q": "1c", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "12,8", "expected": "P(X<=k) = 0.155"}
{"paper": "y422-jun22", "q": "2a", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "23,7.84,5,120", "expected": "P(sum<k) = 0.788"}
{"paper": "y422-jun22", "q": "3b", "module": "fstat", "label": "E and Var of a+bX", "inputs": "10,-3,1.8,1.44", "expected": "Var(a+bX) = 324/25"}
{"paper": "y422-jun22", "q": "4b", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "4,0.4,2", "expected": "P(X>=k) = 0.525"}
{"paper": "y422-jun22", "q": "5b", "module": "fstat", "label": "Residuals", "inputs": "20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192", "expected": "x=36: e = -0.00604"}
{"paper": "y422-jun22", "q": "5e", "module": "fstat", "label": "Predict y from x", "inputs": "10,20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192", "expected": "extrapolation: x outside data"}
{"paper": "y422-jun22", "q": "6a", "module": "fstat", "label": "Estimates from sums", "inputs": "40,491.84,6050.3", "expected": "s^2 = 0.0676"}
{"paper": "y422-jun22", "q": "6b", "module": "fstat", "label": "CI to test mu0", "inputs": "12.2155,12.3765,12.2", "expected": "mu0 outside the CI"}
{"paper": "y422-jun22", "q": "6d", "module": "fstat", "label": "Sample size for width", "inputs": "0.5,0.196,95", "expected": "n = 100"}
{"paper": "y422-jun22", "q": "7a", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "0.3,5", "expected": "P(X=r) = 0.072"}
{"paper": "y422-jun22", "q": "7b", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "6,0.343,4", "expected": "P(X>=k) = 0.11"}
{"paper": "y422-jun22", "q": "7c", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "(1-x)*x-28/121", "expected": "x = 4/11"}
{"paper": "y422-jun22", "q": "8c", "module": "fstat", "label": "Spearman test data", "inputs": "5,2,30.26,28.19,30.41,29.59,31.36,29.07,31.56,29.99,31.68,29.28,31.69,29.60,31.77,30.18,32.14,29.20,32.16,29.12,35.63,32.69,36.24,33.85", "expected": "rs = 0.591"}
{"paper": "y422-jun22", "q": "9a", "module": "fstat", "label": "Discrete uniform", "inputs": "0,20,0,7", "expected": "P(c<=X<=d) = 8/21"}
{"paper": "y422-jun22", "q": "9b", "module": "fstat", "label": "Discrete uniform", "inputs": "0,20,0,7", "expected": "Var(X) = (n^2-1)/12 = 110/3"}
{"paper": "y422-jun22", "q": "10a", "module": "fstat", "label": "Chi-sq association", "inputs": "2,3,5,9,18,5,3,13,12", "expected": "E r1: 6.4 16.5 9.07"}
{"paper": "y422-jun22", "q": "10c", "module": "fstat", "label": "Chi-sq association", "inputs": "2,3,5,9,18,5,3,13,12", "expected": "reject H0 at 5%"}
{"paper": "y422-jun22", "q": "10d", "module": "fstat", "label": "Chi-sq contributions", "inputs": "2,3,9,18,5,3,13,12", "expected": "r2: -1.21 -0.149 +2.08"}
{"paper": "y422-jun22", "q": "11b", "module": "fstat", "label": "Wilcoxon single sample", "inputs": "1,5,1,-0.84,-0.76,-0.16,0.43,1.31,1.32,1.47,1.64,1.93,2.14", "expected": "crit: reject if T <= 10"}
{"paper": "y422-jun22", "q": "12b", "module": "fstat", "label": "pdf from a cdf", "inputs": "(10x-0.5x^2)/50,0,10", "expected": "SD = 2.36"}
{"paper": "y422-jun22", "q": "12b", "module": "fstat", "label": "pdf P(c<X<d)", "inputs": "(10-x)/50,0,10,3.333-2.357,3.333+2.357", "expected": "P(c<X<d) = 0.629"}
{"paper": "y422-jun23", "q": "1a", "module": "CALC", "label": "Calculate", "inputs": "(1/6)^4", "expected": "1/1296"}
{"paper": "y422-jun23", "q": "1c", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "10000/1296,10", "expected": "P(X>k) = 1-P(X<=k) = 0.157"}
{"paper": "y422-jun23", "q": "1d", "module": "CALC", "label": "Calculate", "inputs": "1-(1295/1296)^20", "expected": "0.01531949967"}
{"paper": "y422-jun23", "q": "1d", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "50,0.015319,2", "expected": "P(X<=k) = 0.959"}
{"paper": "y422-jun23", "q": "2a", "module": "CALC", "label": "Calculate", "inputs": "-10.26*5+1013", "expected": "961.7"}
{"paper": "y422-jun23", "q": "3a", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "3,0.55,0", "expected": "P(X=k) = 0.0911"}
{"paper": "y422-jun23", "q": "3b", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "20,0.55,10", "expected": "P(X>=k) = 0.751"}
{"paper": "y422-jun23", "q": "3c", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "0.55,5", "expected": "P(X=r) = 0.0226"}
{"paper": "y422-jun23", "q": "3e", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "x*(1-x)-0.2496", "expected": "x = 12/25"}
{"paper": "y422-jun23", "q": "4a", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "3.125,0.0009,10,31", "expected": "P(sum<k) = 0.0042"}
{"paper": "y422-jun23", "q": "4b", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "3.125,0.0009,10,31", "expected": "P(nX<k) = 0.202"}
{"paper": "y422-jun23", "q": "5a", "module": "fstat", "label": "Estimates from sums", "inputs": "40,765,15065", "expected": "s^2 = 11.1"}
{"paper": "y422-jun23", "q": "5a", "module": "fstat", "label": "CI mean from summary", "inputs": "40,19.125,sqrt(11.138),95", "expected": "centre 19.1 +/- 1.03"}
{"paper": "y422-jun23", "q": "6c", "module": "fstat", "label": "PMCC test from r", "inputs": "0.211,20,5,2", "expected": "crit = +/-0.444"}
{"paper": "y422-jun23", "q": "8d", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "25,sqrt(5*25/3/100),26,100", "expected": "P(a<X<b) = 0.0607"}
{"paper": "y422-jun23", "q": "9a", "module": "fstat", "label": "Chi-sq association", "inputs": "2,2,5,12,11,157,70", "expected": "chi^2 = 2.75"}
{"paper": "y422-jun23", "q": "10d", "module": "fstat", "label": "cdf median quartiles", "inputs": "(4/15)*(-1/(2x)+x^3-7x/2+3),1,2", "expected": "median = 1.74"}
{"paper": "y422-jun23", "q": "10e", "module": "fstat", "label": "pdf E Var and check", "inputs": "(4/15)*(1/(2x^2)+3x^2-7/2),1,2", "expected": "E(X) = 1.69"}
{"paper": "y422-jun23", "q": "10f", "module": "fstat", "label": "Mode of a pdf", "inputs": "(4/15)*(1/(2x^2)+3x^2-7/2),1,2", "expected": "mode = 2"}
{"paper": "y422-jun23", "q": "11b", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "50,0.2,10", "expected": "var np(1-p) = 8"}
{"paper": "y422-jun24", "q": "1a", "module": "fstat", "label": "DRV from table", "inputs": "0,0.05,1,0.1,2,0.25,3,0.3,4,0.15,5,0.1,6,0.05", "expected": "Var(X) = 2.09"}
{"paper": "y422-jun24", "q": "1b", "module": "fstat", "label": "E and Var of a+bX", "inputs": "1000,500,2.9,2.09", "expected": "SD(a+bX) = 723"}
{"paper": "y422-jun24", "q": "2b(i)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "0.36,1", "expected": "P(X=k) = 0.251"}
{"paper": "y422-jun24", "q": "2b(ii)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "0.36,1", "expected": "P(X>k) = 1-P(X<=k) = 0.0512"}
{"paper": "y422-jun24", "q": "2c", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "7.2,4", "expected": "P(X<=k) = 0.156"}
{"paper": "y422-jun24", "q": "3a", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "46,3.1,50,1000", "expected": "P(a<X<b) = 0.0985"}
{"paper": "y422-jun24", "q": "3b", "module": "fstat", "label": "Inverse Normal", "inputs": "35,2.4,0.99", "expected": "x = 40.6"}
{"paper": "y422-jun24", "q": "4a", "module": "fstat", "label": "pdf find k", "inputs": "x,0,50", "expected": "k = 0.0008"}
{"paper": "y422-jun24", "q": "4b", "module": "fstat", "label": "pdf P(c<X<d)", "inputs": "x/1250,0,50,0,5", "expected": "P(c<X<d) = 0.01"}
{"paper": "y422-jun24", "q": "4c", "module": "fstat", "label": "pdf median quartiles", "inputs": "x/1250,0,50", "expected": "median m = 35.4"}
{"paper": "y422-jun24", "q": "5c(ii)", "module": "fstat", "label": "CI mean from summary", "inputs": "40,0.586,2.14,90", "expected": "SE = s/sqrt(n) = 0.338"}
{"paper": "y422-jun24", "q": "5d", "module": "fstat", "label": "CI mean from summary", "inputs": "40,0.586,2.14,95", "expected": "(-0.0772, 1.25)"}
{"paper": "y422-jun24", "q": "6c", "module": "fstat", "label": "Spearman test data", "inputs": "5,1,22,38,29,46,36,42,39,49,53,37,57,47,60,36,71,33,76,34,82,24", "expected": "rs = -0.721"}
{"paper": "y422-jun24", "q": "9a", "module": "fstat", "label": "Chi-sq association", "inputs": "2,3,5,2,21,19,13,47,18", "expected": "E r2: 9.75 44.2 24"}
{"paper": "y422-jun24", "q": "9c", "module": "fstat", "label": "Chi-sq association", "inputs": "2,3,5,2,21,19,13,47,18", "expected": "chi^2 = 7.95"}
{"paper": "y422-jun24", "q": "9d", "module": "fstat", "label": "Chi-sq contributions", "inputs": "2,3,2,21,19,13,47,18", "expected": "r1: -2.01 -0.329 +2.83"}
{"paper": "y422-jun24", "q": "10a", "module": "fstat", "label": "E and Var of X+-Y", "inputs": "3,3,2,4/3", "expected": "E(X+Y) = 5"}
{"paper": "y422-jun24", "q": "10b", "module": "fstat", "label": "E and Var of X+-Y", "inputs": "3,3,2,4/3", "expected": "Var(X+Y) = 13/3"}
{"paper": "y422-jun24", "q": "10d", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "5,13/3,40,210", "expected": "P(sum<k) = 0.776"}
{"paper": "y422-jun24", "q": "12b", "module": "fstat", "label": "cdf median quartiles", "inputs": "(x^2+10x-600)/600,20,30,0.9", "expected": "F(x) = p at x = 29.1"}
{"paper": "y422-jun25", "q": "1a", "module": "fstat", "label": "Discrete uniform", "inputs": "1,8,5,8", "expected": "P(c<=X<=d) = 1/2"}
{"paper": "y422-jun25", "q": "1b", "module": "fstat", "label": "Discrete uniform", "inputs": "1,8,5,8", "expected": "Var(X) = (n^2-1)/12 = 21/4"}
{"paper": "y422-jun25", "q": "1c", "module": "CALC", "label": "Calculate", "inputs": "3*(3/8)*(1/2)^2", "expected": "9/32"}
{"paper": "y422-jun25", "q": "2a", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "20,0.8,0,19", "expected": "P(a<X<b) = 0.106"}
{"paper": "y422-jun25", "q": "3a", "module": "fstat", "label": "CI mean from summary", "inputs": "50,24.878,0.5664,95", "expected": "SE = s/sqrt(n) = 0.0801"}
{"paper": "y422-jun25", "q": "4a(i)", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "0.4,5", "expected": "P(X=r) = 0.0518"}
{"paper": "y422-jun25", "q": "4a(ii)", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "0.4,5", "expected": "P(X>r) = 0.0778"}
{"paper": "y422-jun25", "q": "4b", "module": "fstat", "label": "Geometric a<=X<=b", "inputs": "0.4,1,4", "expected": "P(a<=X<=b) = 0.87"}
{"paper": "y422-jun25", "q": "4c", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "20,0.4,5", "expected": "P(X>=k) = 0.949"}
{"paper": "y422-jun25", "q": "5a", "module": "fstat", "label": "Rectangular U(a,b)", "inputs": "-4,2,-4,0", "expected": "Var(X) = (b-a)^2/12 = 3"}
{"paper": "y422-jun25", "q": "6e", "module": "fstat", "label": "Residuals", "inputs": "0,100.03,20,100.49,40,101.15,60,101.41,80,102.04,100,102.44", "expected": "x=60: e = -0.0923"}
{"paper": "y422-jun25", "q": "7b", "module": "fstat", "label": "PMCC test from r", "inputs": "-0.2744,30,5,2", "expected": "crit = +/-0.361"}
{"paper": "y422-jun25", "q": "8c", "module": "fstat", "label": "z test for a mean", "inputs": "0,5.9478,40,1.805,5,1", "expected": "z = 1.92"}
{"paper": "y422-jun25", "q": "9a", "module": "mstat", "label": "Frequency table", "inputs": "0,23,1,42,2,46,3,45,4,20,5,15,6,7,7,2", "expected": "mean = 480/200 = 2.4"}
{"paper": "y422-jun25", "q": "9b", "module": "fstat", "label": "GOF Poisson", "inputs": "?,5,23,42,46,45,20,15,7,2", "expected": "1: O 42, E 43.5, 0.0548"}
{"paper": "y422-jun25", "q": "9d", "module": "fstat", "label": "GOF Poisson", "inputs": "?,5,23,42,46,45,20,15,7,2", "expected": "chi^2 = 4.59"}
{"paper": "y422-jun25", "q": "10c", "module": "fstat", "label": "E and Var of X+-Y", "inputs": "2.4,1.44,2.4,1.44", "expected": "Var(X-Y) = 72/25"}
{"paper": "y422-jun25", "q": "11d", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "(24x+20)/(9x+15)-4/3-3/4", "expected": "x = 15/7"}
{"paper": "y422-jun25", "q": "11e", "module": "fstat", "label": "pdf E Var and check", "inputs": "180/(9x+15)^2,0,5", "expected": "E(X) = 1.41"}
{"paper": "y422-jun25", "q": "11f", "module": "fstat", "label": "Mode of a pdf", "inputs": "180/(9x+15)^2,0,5", "expected": "mode = 0"}
{"paper": "y422-nov20", "q": "1a", "module": "mpure", "label": "nCr and nPr", "inputs": "10,4", "expected": "nCr = 210"}
{"paper": "y422-nov20", "q": "1b", "module": "fstat", "label": "DRV from table", "inputs": "0,1/14,1,8/21,2,3/7,3,4/35,4,1/210", "expected": "Var(X) = 16/25"}
{"paper": "y422-nov20", "q": "1c", "module": "fstat", "label": "E and Var of a+bX", "inputs": "1,-0.4,1.6,0.64", "expected": "SD(a+bX) = 0.32"}
{"paper": "y422-nov20", "q": "2a(ii)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "0.3,3", "expected": "P(X=k) = 0.00333"}
{"paper": "y422-nov20", "q": "2b", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.25,1", "expected": "P(X>k) = 1-P(X<=k) = 0.355"}
{"paper": "y422-nov20", "q": "3a", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "201.3,1.7/sqrt(2),200,1000", "expected": "P(a<X<b) = 0.86"}
{"paper": "y422-nov20", "q": "4b", "module": "fstat", "label": "CI mean sigma known", "inputs": "0.1173,0.5766,60,95", "expected": "(-0.0286, 0.263)"}
{"paper": "y422-nov20", "q": "4c", "module": "fstat", "label": "CI mean sigma known", "inputs": "0.1173,0.5766,60,95", "expected": "SE = sigma/sqrt(n) = 0.0744"}
{"paper": "y422-nov20", "q": "6a", "module": "fstat", "label": "PMCC test from r", "inputs": "0.3231,60,10,2", "expected": "crit = +/-0.215"}
{"paper": "y422-nov20", "q": "7c", "module": "fstat", "label": "CI mean from data", "inputs": "95,271,293,306,287,264,290", "expected": "centre 285 +/- 16.1"}
{"paper": "y422-nov20", "q": "8", "module": "fstat", "label": "Estimates from sums", "inputs": "40,51.92,70.57", "expected": "s^2 = 0.0815"}
{"paper": "y422-nov20", "q": "8", "module": "fstat", "label": "z test for a mean", "inputs": "1.25,0.2855,40,1.298,5,2", "expected": "z = 1.06"}
{"paper": "y422-nov20", "q": "9a", "module": "fstat", "label": "GOF binomial", "inputs": "10,?,1,39,39,33,19,8,8,4,0,0,0,0", "expected": "p estimated: xbar/n = 0.172"}
{"paper": "y422-nov20", "q": "9b", "module": "fstat", "label": "GOF binomial", "inputs": "10,?,1,39,39,33,19,8,8,4,0,0,0,0", "expected": "0: O 39, E 22.7, 11.7"}
{"paper": "y422-nov20", "q": "9d", "module": "fstat", "label": "GOF binomial", "inputs": "10,?,1,39,39,33,19,8,8,4,0,0,0,0", "expected": "reject H0 at 1%"}
{"paper": "y422-nov20", "q": "9e", "module": "fstat", "label": "GOF binomial", "inputs": "10,?,1,39,39,33,19,8,8,4,0,0,0,0", "expected": "4-10: O 20, E 11.5, 6.22"}
{"paper": "y422-nov20", "q": "10c", "module": "fstat", "label": "E and Var of X+-Y", "inputs": "6,4.2,6,12", "expected": "Var = 21/5 + 12 = 81/5"}
{"paper": "y422-nov20", "q": "11a", "module": "fstat", "label": "pdf from a cdf", "inputs": "(8x^2-x^3-24)/40,2,4", "expected": "F(a) = 0, F(b) = 1"}
{"paper": "y422-nov20", "q": "11b", "module": "fstat", "label": "pdf P(c<X<d)", "inputs": "(16x-3x^2)/40,2,4,2.5,3.5", "expected": "P(c<X<d) = 0.519"}
{"paper": "y422-nov20", "q": "11d", "module": "fstat", "label": "cdf median quartiles", "inputs": "(8x^2-x^3-24)/40,2,4", "expected": "median = 2.95"}
{"paper": "y422-nov20", "q": "11e", "module": "fstat", "label": "pdf E Var and check", "inputs": "(16x-3x^2)/40,2,4", "expected": "SD = 0.565"}
{"paper": "y422-nov20", "q": "11e", "module": "fstat", "label": "pdf P(c<X<d)", "inputs": "(16x-3x^2)/40,2,4,2.402,3.531", "expected": "P(c<X<d) = 0.586"}
{"paper": "y422-nov21", "q": "1a", "module": "fstat", "label": "CI mean from summary", "inputs": "50,34.711,1.530,95", "expected": "centre 34.7 +/- 0.424"}
{"paper": "y422-nov21", "q": "2d", "module": "fstat", "label": "DRV from table", "inputs": "0,1/36,1,5/36,2,2/9,3,1/4,4,2/9,5,5/36", "expected": "E(X) = 35/12"}
{"paper": "y422-nov21", "q": "2e", "module": "fstat", "label": "E and Var of a+bX", "inputs": "0,30,35/12,1.7986", "expected": "Var(a+bX) = 80937/50"}
{"paper": "y422-nov21", "q": "2f", "module": "fstat", "label": "E and Var of a+bX", "inputs": "0,30,35/12,1.7986", "expected": "E(a+bX) = 175/2"}
{"paper": "y422-nov21", "q": "3a", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "50,0.04,2", "expected": "P(X=k) = 0.276"}
{"paper": "y422-nov21", "q": "3b", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "0.04,10", "expected": "P(X=r) = 0.0277"}
{"paper": "y422-nov21", "q": "3c", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "20,0.04,0", "expected": "P(X=k) = 0.442"}
{"paper": "y422-nov21", "q": "4b", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "5,6", "expected": "P(X>k) = 1-P(X<=k) = 0.238"}
{"paper": "y422-nov21", "q": "4c", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "50,60", "expected": "P(X>=k) = 0.0923"}
{"paper": "y422-nov21", "q": "6b", "module": "fstat", "label": "GOF Poisson", "inputs": "1.7,5,34,65,55,24,14,6,2", "expected": "1: O 65, E 62.1, 0.134"}
{"paper": "y422-nov21", "q": "6d", "module": "fstat", "label": "GOF Poisson", "inputs": "1.7,5,34,65,55,24,14,6,2", "expected": "chi^2 = 2.43"}
{"paper": "y422-nov21", "q": "8a(i)", "module": "CALC", "label": "Calculate", "inputs": "0.6978*50+15.656", "expected": "50.546"}
{"paper": "y422-nov21", "q": "8a(iii)", "module": "mpure", "label": "Simultaneous 2 linear", "inputs": "-0.6978,1,15.656,1,-0.7565,10.493", "expected": "x = 47.3"}
{"paper": "y422-nov21", "q": "8b(iii)", "module": "fstat", "label": "PMCC test from r", "inputs": "-0.4255,20,5,1", "expected": "crit = -0.378"}
{"paper": "y422-nov21", "q": "11b", "module": "fstat", "label": "Piecewise pdf", "inputs": "x^2/8,2(3-x)^2,0,2,3", "expected": "median = 2.09"}
{"paper": "y422-nov21", "q": "11c", "module": "fstat", "label": "Normal P(a<X<b)", "inputs": "2,sqrt(0.2/50),0,1.9", "expected": "P(a<X<b) = 0.0569"}
{"paper": "y422-spec", "q": "1(i)", "module": "CALC", "label": "Calculate", "inputs": "3*2*1/27", "expected": "2/9"}
{"paper": "y422-spec", "q": "1(iii)", "module": "fstat", "label": "DRV from table", "inputs": "3,2/9,4,2/9,5,14/81,6,31/81", "expected": "Var(X) = 1.41"}
{"paper": "y422-spec", "q": "2(ii)(B)", "module": "fstat", "label": "Piecewise pdf", "inputs": "1/3,1/3+x^2,-1,0,1", "expected": "E(X) = 1/4"}
{"paper": "y422-spec", "q": "2(iii)", "module": "fstat", "label": "Piecewise pdf", "inputs": "1/3,1/3+x^2,-1,0,1", "expected": "median = 0.424"}
{"paper": "y422-spec", "q": "3(i)", "module": "CALC", "label": "Calculate", "inputs": "11-(17.138-0.3727*24)", "expected": "2.8068"}
{"paper": "y422-spec", "q": "3(ii)", "module": "CALC", "label": "Calculate", "inputs": "-0.3727*26+17.138", "expected": "7.4478"}
{"paper": "y422-spec", "q": "4(i)", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "1/6,4", "expected": "P(X=r) = 0.0965"}
{"paper": "y422-spec", "q": "4(ii)", "module": "fstat", "label": "Geometric P(X=r)", "inputs": "1/6,4", "expected": "P(X<=r) = 0.518"}
{"paper": "y422-spec", "q": "4(iv)", "module": "fstat", "label": "Binomial P(X=k)", "inputs": "3,1/6,2", "expected": "P(X>=k) = 0.0741"}
{"paper": "y422-spec", "q": "5(i)", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "508,10.89,5,2550", "expected": "P(sum<k) = 0.912"}
{"paper": "y422-spec", "q": "5(ii)", "module": "fstat", "label": "aX+bY+c", "inputs": "1,-3,0,1515,22.09,508,10.89,0", "expected": "P(W>k) = 0.206"}
{"paper": "y422-spec", "q": "8(ii)(A)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.1,0", "expected": "P(X=k) = 0.333"}
{"paper": "y422-spec", "q": "8(ii)(B)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "66,60", "expected": "P(X>=k) = 0.786"}
{"paper": "y422-spec", "q": "8(iii)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "1.1,8", "expected": "P(X>k) = 1-P(X<=k) = 2.43e-6"}
{"paper": "y422-spec", "q": "8(iv)", "module": "fstat", "label": "Poisson P(X=k)", "inputs": "4.5,8", "expected": "P(X<=k) = 0.96"}
{"paper": "y422-spec", "q": "8(iv)", "module": "CALC", "label": "Calculate", "inputs": "1-0.95974^10", "expected": "0.3369657595"}
{"paper": "y422-spec", "q": "9(ii)", "module": "fstat", "label": "Chi-sq contributions", "inputs": "4,4,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5", "expected": "r3: -0.593 -1.25"}
{"paper": "y422-spec", "q": "9(iii)", "module": "fstat", "label": "Chi-sq association", "inputs": "4,4,5,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5", "expected": "reject H0 at 5%"}
{"paper": "y422-spec", "q": "9(iv)", "module": "fstat", "label": "Chi-sq contributions", "inputs": "4,4,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5", "expected": "r2: +3.18 +2.82"}
{"paper": "y422-spec", "q": "11(i)", "module": "CALC", "label": "Calculate", "inputs": "(1/6)^10", "expected": "1/60466176"}
{"paper": "y422-spec", "q": "11(iii)", "module": "fstat", "label": "Discrete uniform", "inputs": "1,6", "expected": "Var(X) = (n^2-1)/12 = 35/12"}
{"paper": "y422-spec", "q": "11(iv)", "module": "fstat", "label": "nX vs X1+..+Xn", "inputs": "3.5,35/12,10,40.5", "expected": "Var(X1+..+Xn) = 175/6"}
{"paper": "y435-jun19", "q": "1a", "module": "fxpure", "label": "Eigen 2x2", "inputs": "0.6,0.8,0.8,-0.6", "expected": "L1 = 1, v1 = (2, 1)"}
{"paper": "y435-jun19", "q": "1b", "module": "fxpure", "label": "Eigen 2x2", "inputs": "0.6,0.8,0.8,-0.6", "expected": "L2 = -1, v2 = (1, -2)"}
{"paper": "y435-jun19", "q": "1c", "module": "fxpure", "label": "Eigen 2x2", "inputs": "0.6,0.8,0.8,-0.6", "expected": "y = (1/2)x: points on it are invariant"}
{"paper": "y435-jun19", "q": "2a", "module": "fxpure", "label": "Stationary points", "inputs": "4x^2+4y^2-4x+8y+11", "expected": "(1/2, -1, 6) min"}
{"paper": "y435-jun19", "q": "2c", "module": "fxpure", "label": "Sections y = k", "inputs": "4x^2+4y^2-4x+8y+11,1,-3", "expected": "y = 1: z = 4*x^2-4*x+23"}
{"paper": "y435-jun19", "q": "3", "module": "fxpure", "label": "Cayley-Hamilton 3x3", "inputs": "-1,2,4,0,-1,-25,-3,5,-1", "expected": "M^-1 = (M^2 + 3M + 140I)/12"}
{"paper": "y435-jun19", "q": "4c(i)", "module": "fxpure", "label": "Group axioms", "inputs": "4, 2,1,4,3, 1,2,3,4, 4,3,2,1, 3,4,1,2", "expected": "G is a group of order 4"}
{"paper": "y435-jun19", "q": "4c(ii)", "module": "fxpure", "label": "Group axioms", "inputs": "4, 2,1,4,3, 1,2,3,4, 4,3,2,1, 3,4,1,2", "expected": "abelian: yes"}
{"paper": "y435-jun19", "q": "5d(i)", "module": "fxpure", "label": "1st order a u + f(n)", "inputs": "1.08,-3000,30000", "expected": "u(n) = -7500*(27/25)^n + 37500"}
{"paper": "y435-jun19", "q": "5d(i)", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "37500-7500*1.08^x", "expected": "x = ln(5)/ln(27/25)"}
{"paper": "y435-jun19", "q": "5d(ii)", "module": "CALC", "label": "Calculate", "inputs": "37500-7500*1.08^21", "expected": "-253.7528652"}
{"paper": "y435-jun19", "q": "6c", "module": "CALC", "label": "Calculate", "inputs": "(1+sqrt(7))^2", "expected": "2*sqrt(7)+8"}
{"paper": "y435-jun22", "q": "1", "module": "fxpure", "label": "Behaviour u(n+1)=F", "inputs": "2+3/(2-u),3", "expected": "periodic, period 2"}
{"paper": "y435-jun22", "q": "1", "module": "fxpure", "label": "Behaviour u(n+1)=F", "inputs": "-u/2+3,1.5", "expected": "convergent: u(n) -> 2"}
{"paper": "y435-jun22", "q": "2a", "module": "fxpure", "label": "Eigen 3x3", "inputs": "10,12,-8,-1,2,4,3,6,2", "expected": "char eq: L^3-14L^2+56L-64 = 0"}
{"paper": "y435-jun22", "q": "2b", "module": "fxpure", "label": "Cayley-Hamilton 3x3", "inputs": "10,12,-8,-1,2,4,3,6,2", "expected": "M^-1 = (M^2 - 14M + 56I)/64"}
{"paper": "y435-jun22", "q": "2c", "module": "fxpure", "label": "Diagonalise 3x3 M^n", "inputs": "10,12,-8,-1,2,4,3,6,2", "expected": "D = diag(2, 4, 8)"}
{"paper": "y435-jun22", "q": "3a", "module": "fxpure", "label": "1st order a u + f(n)", "inputs": "4/5,(3n^2+28n+6)/5,7", "expected": "u(n) = 6*(4/5)^n + 3*n^2 - 2*n + 1"}
{"paper": "y435-jun22", "q": "5a(i)", "module": "fxpure", "label": "Partial derivatives", "inputs": "y*e^(-(x^2+2x+2)y)", "expected": "dz/dx = -(2*x+2)*e^(-(x^2+2*x+2)*y)*y^2"}
{"paper": "y435-jun22", "q": "5a(ii)", "module": "fxpure", "label": "Partial derivatives", "inputs": "y*e^(-(x^2+2x+2)y)", "expected": "dz/dy ="}
{"paper": "y435-jun22", "q": "5c", "module": "fxpure", "label": "Sections y = k", "inputs": "y*e^(-(x^2+2x+2)y),1", "expected": "y = 1: z = e^(-(x^2+2*x+2))"}
{"paper": "y435-jun22", "q": "5d", "module": "fxpure", "label": "Stationary points", "inputs": "y*e^(-(x^2+2x+2)y)", "expected": "max"}
{"paper": "y435-jun22", "q": "5e", "module": "fxpure", "label": "Tangent plane z=f", "inputs": "y*e^(-(x^2+2x+2)y),0,0", "expected": "z = y"}
{"paper": "y435-jun23", "q": "1", "module": "fxpure", "label": "Stationary points", "inputs": "3x^3+6x*y+y^2", "expected": "(2, -6, -12) min"}
{"paper": "y435-jun23", "q": "2a", "module": "fxpure", "label": "1st order a u + f(n)", "inputs": "1/4,(15n+17)/4,2,1", "expected": "u(n) = -8*(1/4)^n + 5*n - 1"}
{"paper": "y435-jun23", "q": "3", "module": "fxpure", "label": "grad g, normal, plane", "inputs": "2x^3-x^2*y+2x*y^2+27z,1,1,-1/9", "expected": "grad g = (6, 3, 27)"}
{"paper": "y435-jun23", "q": "3", "module": "fxpure", "label": "grad g, normal, plane", "inputs": "2x^3-x^2*y+2x*y^2+27z,3,3,-3", "expected": "tangent plane: 2x + y + z = 6"}
{"paper": "y435-jun23", "q": "3", "module": "fcore", "label": "Line meets plane", "inputs": "1,1,-1/9,6,3,27,2,1,1,6", "expected": "meets at (13/9, 11/9, 17/9)"}
{"paper": "y435-jun23", "q": "4c(i)", "module": "fcore", "label": "AB and BA (2x2)", "inputs": "-1,0,0,-1,-1,0,0,-1", "expected": "AB = [1 0]"}
{"paper": "y435-jun23", "q": "5a", "module": "fcore", "label": "Angle between lines", "inputs": "1,1,0,0,1,0", "expected": "angle = pi/4 rad"}
{"paper": "y435-jun23", "q": "5b(ii)", "module": "fxpure", "label": "Cayley-Hamilton 2x2", "inputs": "-1/3,0,2,3,4", "expected": "M^4 = (656/27)M + (73/9)I"}
{"paper": "y435-jun24", "q": "1a", "module": "fxpure", "label": "Stationary points", "inputs": "12x-30y+6x*y", "expected": "(5, -2, 60) saddle"}
{"paper": "y435-jun24", "q": "1d", "module": "fxpure", "label": "grad g, normal, plane", "inputs": "12x-30y+6x*y-z,3,2,12", "expected": "tangent plane: 24x - 12y - z = 36"}
{"paper": "y435-jun24", "q": "1e", "module": "fxpure", "label": "grad g, normal, plane", "inputs": "12x-30y+6x*y-z,0,4,-120", "expected": "grad g = (36, -30, -1)"}
{"paper": "y435-jun24", "q": "1e", "module": "fcore", "label": "Line meets plane", "inputs": "0,4,-120,36,-30,-1,3,3,-2,52", "expected": "meets at (-360, 304, -110)"}
{"paper": "y435-jun24", "q": "2a", "module": "fxpure", "label": "2nd order homogeneous", "inputs": "7/2,-3/2,0,1", "expected": "roots 3, 1/2"}
{"paper": "y435-jun24", "q": "2b", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "7/2,-3/2,10n^2+30n,-9,-12", "expected": "p(n) = -10*n^2 - 5"}
{"paper": "y435-jun24", "q": "2c", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "7/2,-3/2,10n^2+30n,-9,-12", "expected": "A = 2, B = -6"}
{"paper": "y435-jun24", "q": "2d", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "7/2,-3/2,10n^2+30n,-9,-12", "expected": "-167/4"}
{"paper": "y435-jun24", "q": "3c", "module": "fxpure", "label": "Subgroups, Lagrange", "inputs": "6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0", "expected": "1 2 3 6, index"}
{"paper": "y435-jun24", "q": "3d", "module": "fxpure", "label": "Subgroups, Lagrange", "inputs": "6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0", "expected": "{0,1,2} order 3"}
{"paper": "y435-jun24", "q": "3e", "module": "fxpure", "label": "Element orders", "inputs": "6, 0,1,2,3,4,5, 1,2,0,4,5,3, 2,0,1,5,3,4, 3,5,4,0,2,1, 4,3,5,1,0,2, 5,4,3,2,1,0", "expected": "not cyclic: no element of order 6"}
{"paper": "y435-jun24", "q": "4a", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1,7,8,-6,12,12,-2,4,8", "expected": "char eq: L^3-21L^2+126L-216 = 0"}
{"paper": "y435-jun24", "q": "4b(i)", "module": "fxpure", "label": "Is v eigenvector 3x3", "inputs": "1,7,8,-6,12,12,-2,4,8,1,-2,2", "expected": "yes: Mv = 3v, L = 3"}
{"paper": "y435-jun24", "q": "4b(ii)", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1,7,8,-6,12,12,-2,4,8", "expected": "L = 6, v = (3, 1, 1)"}
{"paper": "y435-jun24", "q": "4c(i)", "module": "fxpure", "label": "Cayley-Hamilton 3x3", "inputs": "3,2,1,1,2,-2,1,1,2", "expected": "M^-1 = (M^2 - 7M + 15I)/9"}
{"paper": "y435-jun24", "q": "4c(ii)", "module": "fxpure", "label": "Cayley-Hamilton 3x3", "inputs": "3,2,1,1,2,-2,1,1,2", "expected": "[-4/9 5/9 7/9]"}
{"paper": "y435-jun24", "q": "4c(iii)", "module": "fxpure", "label": "Diagonalise 3x3 M^n", "inputs": "1,7,8,-6,12,12,-2,4,8,4", "expected": "[-17550 22626 31320]"}
{"paper": "y435-jun25", "q": "2b(i)", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "7/5,-12/25,-10/25,20,70", "expected": "A = 300, B = -275"}
{"paper": "y435-jun25", "q": "2b(ii)", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "7/5,-12/25,-10/25,20,70", "expected": "446/5"}
{"paper": "y435-jun25", "q": "2b(iii)", "module": "mpure", "label": "Terms of u(n)", "inputs": "300*(4/5)^n-275*(3/5)^n-5,17,3", "expected": "u(19) = -0.693"}
{"paper": "y435-jun25", "q": "3a", "module": "fxpure", "label": "Z_n under + mod n", "inputs": "9", "expected": "identity 0"}
{"paper": "y435-jun25", "q": "3c", "module": "fxpure", "label": "Z_n under + mod n", "inputs": "9", "expected": "generators: 1, 2, 4, 5, 7, 8"}
{"paper": "y435-jun25", "q": "3d(i)", "module": "fxpure", "label": "Subgroups, Lagrange", "inputs": "9, 0,1,2,3,4,5,6,7,8, 1,2,3,4,5,6,7,8,0, 2,3,4,5,6,7,8,0,1, 3,4,5,6,7,8,0,1,2, 4,5,6,7,8,0,1,2,3, 5,6,7,8,0,1,2,3,4, 6,7,8,0,1,2,3,4,5, 7,8,0,1,2,3,4,5,6, 8,0,1,2,3,4,5,6,7", "expected": "{0,3,6} order 3"}
{"paper": "y435-jun25", "q": "3d(ii)", "module": "fxpure", "label": "Subgroups, Lagrange", "inputs": "9, 0,1,2,3,4,5,6,7,8, 1,2,3,4,5,6,7,8,0, 2,3,4,5,6,7,8,0,1, 3,4,5,6,7,8,0,1,2, 4,5,6,7,8,0,1,2,3, 5,6,7,8,0,1,2,3,4, 6,7,8,0,1,2,3,4,5, 7,8,0,1,2,3,4,5,6, 8,0,1,2,3,4,5,6,7", "expected": "3 subgroups of G (order 9)"}
{"paper": "y435-jun25", "q": "4a", "module": "fxpure", "label": "Stationary points", "inputs": "x^3-12x*y^2+96y^2+30", "expected": "(8, 4, 542) saddle"}
{"paper": "y435-jun25", "q": "4b", "module": "fxpure", "label": "Sections y = k", "inputs": "x^3-12x*y^2+96y^2+30,0", "expected": "y = 0: z = x^3+30"}
{"paper": "y435-jun25", "q": "4c", "module": "fxpure", "label": "Tangent plane z=f", "inputs": "x^3-12x*y^2+96y^2+30,3,2", "expected": "r = (3, 2, 297) + t(-21, 240, -1)"}
{"paper": "y435-jun25", "q": "5c(iii)", "module": "fxpure", "label": "Eigen 3x3", "inputs": "0.6,0.8,0,-0.8,0.6,0,0,0,1", "expected": "line r = t(0, 0, 1): points on it are invariant"}
{"paper": "y435-nov20", "q": "1", "module": "fxpure", "label": "Eigen 2x2", "inputs": "0,2,3,-1", "expected": "L2 = -3, v2 = (2, -3)"}
{"paper": "y435-nov20", "q": "3a", "module": "fxpure", "label": "2nd order homogeneous", "inputs": "4,-5,0,1", "expected": "u(n) = (sqrt(5))^n*sin(n*0.464)"}
{"paper": "y435-nov20", "q": "5a", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3", "expected": "repeated: eigenspace is 2D"}
{"paper": "y435-nov20", "q": "5a", "module": "fxpure", "label": "Is v eigenvector 3x3", "inputs": "1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3,1,-1,0", "expected": "yes: Mv = 1v, L = 1"}
{"paper": "y435-nov20", "q": "5b", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1/3,-2/3,-2/3,-2/3,1/3,-2/3,-2/3,-2/3,1/3", "expected": "L = 1 (x2)"}
{"paper": "y435-nov20", "q": "6a(i)", "module": "fxpure", "label": "Stationary points", "inputs": "4x^4+4y^4-17x^2*y^2", "expected": "1 stationary point"}
{"paper": "y435-nov20", "q": "6a(ii)", "module": "fxpure", "label": "Stationary points", "inputs": "4x^4+4y^4-17x^2*y^2", "expected": "(0, 0, 0) D = 0, test fails"}
{"paper": "y435-nov20", "q": "6b(i)", "module": "fxpure", "label": "Tangent plane z=f", "inputs": "4x^4+4y^4-17x^2*y^2,1,1", "expected": "z = -18x - 18y + 27"}
{"paper": "y435-nov21", "q": "1a", "module": "fxpure", "label": "Sections x = k", "inputs": "x^3+x^2*y-2y^2,2", "expected": "x = 2: z = -2*y^2+4*y+8"}
{"paper": "y435-nov21", "q": "1a", "module": "CAS", "label": "stationary points", "inputs": "8+4x-2x^2", "expected": "(1, 10)  max"}
{"paper": "y435-nov21", "q": "1a", "module": "CAS", "label": "solve exact f(x)=0", "inputs": "8+4x-2x^2", "expected": "x = sqrt(5)+1"}
{"paper": "y435-nov21", "q": "2b", "module": "fxpure", "label": "Z_n under + mod n", "inputs": "8", "expected": "ord(2)=4"}
{"paper": "y435-nov21", "q": "3a", "module": "fxpure", "label": "Eigen 3x3", "inputs": "3,3,0,0,2,2,1,3,4", "expected": "char eq: L^3-9L^2+20L-12 = 0"}
{"paper": "y435-nov21", "q": "3b", "module": "fxpure", "label": "Eigen 3x3", "inputs": "3,3,0,0,2,2,1,3,4", "expected": "L = 6, v = (1, 1, 2)"}
{"paper": "y435-nov21", "q": "3c", "module": "fxpure", "label": "Eigen 3x3", "inputs": "3,3,0,0,2,2,1,3,4", "expected": "L = 1, v = (3, -2, 1)"}
{"paper": "y435-nov21", "q": "4a", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "3,10,24n-10,6,10", "expected": "p(n) = -2*n + 1"}
{"paper": "y435-nov21", "q": "4b", "module": "fxpure", "label": "2nd order + f(n)", "inputs": "3,10,24n-10,6,10", "expected": "u(n) = 3*5^n + 2*(-2)^n - 2*n + 1"}
{"paper": "y435-nov21", "q": "4c", "module": "fxpure", "label": "Verify u(n+2)=F(n,u,v)", "inputs": "3v+10u+24n-10,1-2n+3*5^n+2*(-2)^n", "expected": "n=0: LHS 80, RHS 80"}
{"paper": "y435-nov21", "q": "4d", "module": "fxpure", "label": "Ratio u(n+1)/u(n)", "inputs": "3,10,6,10", "expected": "u(n+1)/u(n) -> 5"}
{"paper": "y435-spec", "q": "1(i)", "module": "fxpure", "label": "Set under x mod n", "inputs": "19,1,4,5,6,7,9,11,16,17", "expected": "cyclic, generators 4, 5, 6, 9, 16, 17"}
{"paper": "y435-spec", "q": "1(ii)", "module": "fxpure", "label": "Set under x mod n", "inputs": "19,1,4,5,6,7,9,11,16,17", "expected": "ord(5)=9"}
{"paper": "y435-spec", "q": "2", "module": "fxpure", "label": "Group axioms", "inputs": "5, 0,1,2,3,4, 1,0,3,4,2, 2,4,0,1,3, 3,2,4,0,1, 4,3,1,2,0", "expected": "not associative: (1*1)*2 != 1*(1*2)"}
{"paper": "y435-spec", "q": "3(i)", "module": "fxpure", "label": "2nd order homogeneous", "inputs": "8,-16,1,2", "expected": "repeated root 4: CF (A + Bn)4^n"}
{"paper": "y435-spec", "q": "3(ii)(B)", "module": "fxpure", "label": "Behaviour u(n+1)=F", "inputs": "8-16/u,5", "expected": "fixed point 4, attracting"}
{"paper": "y435-spec", "q": "3(iii)", "module": "fxpure", "label": "Ratio u(n+1)/u(n)", "inputs": "8,-16,1,2", "expected": "u(n+1)/u(n) -> 4"}
{"paper": "y435-spec", "q": "4(iv)", "module": "fxpure", "label": "grad g, normal, plane", "inputs": "(y-2x)*(y+z)^2-18,1,4,-7", "expected": "tangent plane: 6x + y + 4z = -18"}
{"paper": "y435-spec", "q": "4(v)", "module": "fcore", "label": "Two planes meet", "inputs": "6,1,4,-18,6,-7,-4,-18", "expected": "r = (-3, 0, 0) + t(1, 2, -2)"}
{"paper": "y435-spec", "q": "5(ii)", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1/2,-1/sqrt(2),1/2,1/sqrt(2),0,-1/sqrt(2),1/2,1/sqrt(2),1/2", "expected": "L = 1, v = (1, 0, 1)"}
{"paper": "y435-spec", "q": "5(iii)", "module": "fxpure", "label": "Eigen 3x3", "inputs": "1/2,-1/sqrt(2),1/2,1/sqrt(2),0,-1/sqrt(2),1/2,1/sqrt(2),1/2", "expected": "char eq: L^3-L^2+1L-1 = 0"}
{"paper": "y435-spec", "q": "5(iv)", "module": "fxpure", "label": "Cayley-Hamilton 3x3", "inputs": "1/2,-1/sqrt(2),1/2,1/sqrt(2),0,-1/sqrt(2),1/2,1/sqrt(2),1/2,4", "expected": "M^4 = I"}
```
