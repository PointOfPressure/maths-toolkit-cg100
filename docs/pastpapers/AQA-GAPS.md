# AQA 7357 past papers: toolkit gaps

Audit of the native-ui toolkit (Maths sections A-S plus Calculate, CAS, Graph, Solve) against all 24 AQA 7357 papers: Paper 1, 2 and 3 for Jun18, Jun19, Nov20, Nov21, Jun22, Jun23, Jun24 and Jun25. Every calculator-doable step was run on the laptop with the paper's numbers and compared with the mark scheme. Per-paper tables: `aqa-7357<n>-<series>.md` in this folder.

## Totals

- Table rows: 921 (one per question part or calculator step; 905 main part rows covering all 2400 marks, 16 extra rows for alternative routes, usually a second tool that failed).
- All rows: OK 551, none 227, AWKWARD 98, WRONG 27, GAP 18.
- Main part rows: OK 544, none 227, AWKWARD 95, WRONG 21, GAP 18. Some "none" rows group two to four adjacent parts (proofs, sketches, explanations).
- 74 distinct fixes below; score = occurrences x marks at stake (each part counted once per fix, alternative-route rows merged into their part).
- 756 OK cases are listed as JSON lines at the end for regression tests.

## Correctness bugs (fix first, whatever their score)

These give a wrong answer, a misleading verdict or a crash, rather than an inconvenient one.

- **[simplify-monic-power]** caseng.simplify bug: N(x)/(ax+b)^k with k >= 2 and non-constant N becomes N/(x+b/a)^k, dropping a^k (x/(1+3x)^2 -> x/(x+1/3)^2, 9 times too big; x/(2x+1)^2 -> 4 times). Breaks CAS simplify, d/dx, G/f' at a, G/Tangent, printed f' in Stationary points, Maclaurin. Fix the monic normalisation (multiply by a^k) and add a numeric spot-check of simplify against the input. Seen in: 7357/2 Jun24 Q9ci; 7357/3 Jun22 Q10d.
- **[factor-thm-float]** B/Factor theorem: evaluate p(a) exactly (rational arithmetic); p(-1/5) = 8.88e-16 is reported as 'not a factor'. Seen in: 7357/1 Nov21 Q13a.
- **[incdec-domain-edge]** G/Increasing/decreasing and G/Inflection points drop or merge the interval next to a domain edge or pole: ln(x)-x gives 'decreasing for all x'; x/sqrt(2x-2) omits 'convex for 1 < x < 4'. Split segments at poles of f'/f'' and at domain edges, and skip undefined stretches. Seen in: 7357/3 Jun18 Q6d.
- **[solve-range]** Numeric solving (B/Solve f(x)=g(x), B/Inequality, Solve screen, CAS solve) searches only -20..20 (+-12 for inequalities). Widen automatically (expanding/log-scaled scan to |x| ~ 1e4) and/or add optional lo,hi fields; polynomial and single-exponential equations should go to the exact solver first. B/Inequality must not claim 'every x' from a partial scan. Seen in: 7357/1 Jun18 Q9b; 7357/1 Jun18 Q11b; 7357/1 Nov20 Q8b; 7357/3 Jun19 Q8bii; 7357/3 Jun22 Q7b; 7357/3 Nov20 Q5a.
- **[inverse-one-one]** B/Inverse function: take a domain (or test one-to-one on it) and say 'many-to-one, no inverse' with a witness f(-1) = f(1); today x^2 and x^2+5 on R get sqrt answers. Seen in: 7357/1 Jun24 Q17cii; 7357/1 Jun25 Q12b; 7357/2 Jun19 Q3.
- **[exactstr-silly]** casutil/caseng.exactstr: do not label a decimal as sqrt(N)/d for large N (31sqrt(47935), sqrt(32497773)/3, sqrt(252382938)/2); cap N (say <= 1000) and denominators. Seen in: 7357/2 Jun23 Q6ci; 7357/2 Jun24 Q4; 7357/2 Jun24 Q7bi.
- **[limit-inf-exp]** CAS limit at inf: handle exponentials (e^(-kx) -> 0, e^(kx) -> inf) for long-run model values. Seen in: 7357/3 Jun19 Q8bi; 7357/3 Jun24 Q8b.
- **[cbrt-negative]** Real cube roots: (-3)^(1/3) evaluates to the complex principal root (1.56-2.5i) while the exact line shows the real root; add cbrt() and use the real branch for odd-denominator powers. Seen in: 7357/1 Jun19 Q15ai.
- **[range-corner]** B/Range of f: include non-differentiable points (|x| corners) and endpoints when finding extremes; |x|+1 on [-10,10] gives '11 <= f <= 11'. Seen in: 7357/1 Jun24 Q17a.
- **[subst-x-remains]** H/Substitution u=g(x): when x survives, invert u = g(x) (casalg.rearrange) and substitute, giving the full integrand in u and new limits. Seen in: 7357/1 Jun24 Q18a; 7357/1 Jun25 Q17a; 7357/2 Nov20 Q5; 7357/3 Jun23 Q8.
- **[int-normalise]** Integrator: normalise before pattern matching (expand (x-1)e^x, rewrite ln x/x^2 as x^-2 ln x, sqrt(16x^3) as 4x^(3/2)) so by-parts and power rules fire in H/Indefinite, CAS integrate, Separable DE. Seen in: 7357/1 Nov21 Q15b; 7357/2 Jun18 Q7; 7357/2 Jun19 Q5.
- **[defint-symbolic-limits]** CAS definite integral: keep symbolic limits (ln 4, pi/3) exact; today ln 4 becomes 1.386294 inside e^(...) and is printed as 'exact'. Seen in: 7357/1 Nov20 Q15.
- **[trig-undefined-root]** E/Solve trig eqn: drop roots where the original expression is undefined (0/0 at x = 360 with sin2x/sin x). Seen in: 7357/1 Jun24 Q15bii.
- **[solve-crash-power]** Solve screen crashes ('<=' complex vs int) on x^1.5 = k / x^(3/2) = k. Seen in: 7357/3 Jun22 Q7b.
- **[solve-overflow]** Solve with huge powers (7^1570): take logs symbolically before evaluating; F/Solve a^x=b should accept b given as a power. Seen in: 7357/2 Jun24 Q4.
- **[inverse-mobius]** B/Inverse function: handle (ax+b)/(cx+d) (use casalg.rearrange as CAS 'rearrange for x' already does). Seen in: 7357/1 Nov20 Q13ai.

## Ranked fixes

| rank | fix | score | parts | marks | worst | proposed fix | occurrences |
|---|---|---|---|---|---|---|---|
| 1 | param-letters | 272 | 8 | 34 | GAP | Let numeric tools carry extra letters as symbolic constants: Solve / B/Factorise / B/Quadratic / C/Circle from general / G/Stationary points / H/Separable DE / Q/Vector r(t) / Q/a(t) to v and s should accept p, q, k, R, g etc. (the CAS core already expands, differentiates and integrates with letters). Minimum: Solve and Factorise over x with parameters. | 7357/1 Jun24 Q19; 7357/2 Jun19 Q7bi; 7357/2 Jun23 Q14; 7357/2 Jun25 Q19a; 7357/2 Nov20 Q9b; 7357/2 Nov21 Q7ai; 7357/2 Nov21 Q7aii; 7357/2 Nov21 Q17b |
| 2 | sep-exact-c | 150 | 5 | 30 | AWKWARD | H/Separable DE at point: evaluate c exactly (caseng exact substitution, e.g. c = 2e, ln 125, ln2 - 1) and offer the solved form y = ... / t = ... with the constant folded in. | 7357/1 Jun24 Q20b; 7357/1 Jun25 Q17b; 7357/2 Jun18 Q7; 7357/2 Jun22 Q10bii; 7357/2 Nov21 Q17b |
| 3 | mech-solve-unknown | 130 | 5 | 26 | AWKWARD | Allow one '?' in R/Rough slope (mu or F), R/Slope and pulley (mu or a mass), R/Friction horizontal (P from a), R/Tow bar (add an a field; solve D, R1 or R2). Today '?' crashes with a Python TypeError. | 7357/2 Jun18 Q17ai; 7357/2 Jun22 Q19a; 7357/2 Jun23 Q15; 7357/2 Jun23 Q19a; 7357/2 Nov20 Q18a |
| 4 | solve-range | 126 | 6 | 21 | WRONG | Numeric solving (B/Solve f(x)=g(x), B/Inequality, Solve screen, CAS solve) searches only -20..20 (+-12 for inequalities). Widen automatically (expanding/log-scaled scan to \|x\| ~ 1e4) and/or add optional lo,hi fields; polynomial and single-exponential equations should go to the exact solver first. B/Inequality must not claim 'every x' from a partial scan. | 7357/1 Jun18 Q9b; 7357/1 Jun18 Q11b; 7357/1 Nov20 Q8b; 7357/3 Jun19 Q8bii; 7357/3 Jun22 Q7b; 7357/3 Nov20 Q5a |
| 5 | simul-nonlin | 92 | 4 | 23 | AWKWARD | New tool B/'Simultaneous non-linear' <f(x,y),g(x,y)> (or two equations in two named unknowns) returning all real solution pairs; substitution + exact solve where possible. | 7357/1 Jun18 Q9b; 7357/2 Jun19 Q6; 7357/3 Jun19 Q8a; 7357/3 Nov20 Q8a |
| 6 | subst-x-remains | 92 | 4 | 23 | WRONG | H/Substitution u=g(x): when x survives, invert u = g(x) (casalg.rearrange) and substitute, giving the full integrand in u and new limits. | 7357/1 Jun24 Q18a; 7357/1 Jun25 Q17a; 7357/2 Nov20 Q5; 7357/3 Jun23 Q8 |
| 7 | log-symbolic | 70 | 5 | 14 | GAP | Log laws for a letter base: combine/split logb(a, .), logb(a,a)=1, logb(a,a^k)=k, and solve log equations for y in terms of a (and two-variable rearrangements like x^3/y^2 = 2^9). | 7357/1 Jun25 Q3; 7357/2 Jun22 Q9; 7357/3 Jun18 Q7a; 7357/3 Jun25 Q4b; 7357/3 Nov20 Q8bii |
| 8 | moments-unknown | 70 | 5 | 14 | AWKWARD | S/Moments about a point and S/Beam: allow one '?' (a force, mass or distance) and solve the moment equation; Beam should accept no extra loads and report reactions as multiples of g. | 7357/2 Jun19 Q14a; 7357/2 Jun19 Q14b; 7357/2 Jun22 Q14a; 7357/2 Jun23 Q17ai; 7357/2 Nov20 Q13a |
| 9 | int-normalise | 57 | 3 | 19 | WRONG | Integrator: normalise before pattern matching (expand (x-1)e^x, rewrite ln x/x^2 as x^-2 ln x, sqrt(16x^3) as 4x^(3/2)) so by-parts and power rules fire in H/Indefinite, CAS integrate, Separable DE. | 7357/1 Nov21 Q15b; 7357/2 Jun18 Q7; 7357/2 Jun19 Q5 |
| 10 | pf-monic | 48 | 4 | 12 | AWKWARD | Partial fractions: keep the user's factors (2x-11), (4-3x), (2x+1) and print integer/rational numerators A/(2x-11) instead of monic -1/2/(x-11/2). | 7357/1 Jun23 Q16a; 7357/2 Jun24 Q9b; 7357/2 Nov21 Q5; 7357/3 Jun25 Q8a |
| 11 | range-infinite | 45 | 5 | 9 | AWKWARD | B/Range of f: allow inf / -inf endpoints and domains split by asymptotes (report y <= m or y >= M). | 7357/1 Jun19 Q6a; 7357/1 Jun25 Q12a; 7357/1 Jun25 Q12dii; 7357/2 Jun23 Q8b; 7357/3 Jun22 Q10e |
| 12 | foot-perp | 42 | 3 | 14 | AWKWARD | New tool C/'Foot of perpendicular' <a,b,c,px,py> (line ax+by=c, point P): foot, distance, reflection; also covers tangent point from a circle centre. | 7357/1 Jun22 Q8ai; 7357/1 Nov21 Q5b; 7357/2 Nov20 Q6a |
| 13 | surd-algebra | 33 | 3 | 11 | GAP | Simplify/factorise/rationalise in sqrt(x): substitute u = sqrt(x) internally, factorise, substitute back; collect sqrt(16x^2) -> 4x, sqrt(8x) -> 2sqrt(2x). | 7357/1 Jun23 Q7a; 7357/1 Jun24 Q7; 7357/3 Nov21 Q6 |
| 14 | deriv-simplify | 30 | 3 | 10 | AWKWARD | After d/dx, collect like terms and combine into one fraction (expand + single fraction), e.g. (cos x - sin x)e^-x - (cos x + sin x)e^-x -> -2e^-x sin x. | 7357/1 Jun19 Q16a; 7357/1 Jun25 Q15a; 7357/3 Jun18 Q6b |
| 15 | domain | 28 | 4 | 7 | GAP | New tool B/'Domain of f(x)': sqrt arguments >= 0, logs > 0, denominators != 0, in set notation. | 7357/1 Jun24 Q17b; 7357/2 Jun23 Q7b; 7357/2 Nov21 Q10a; 7357/3 Jun18 Q6a |
| 16 | log-combine | 28 | 2 | 14 | AWKWARD | Collect logs: ln 8 -> 3 ln 2 and sums of logs into one ln (ln5 - ln2/2 - ln(9/2)/2 -> ln(5/3)). | 7357/3 Jun24 Q11; 7357/3 Jun25 Q8b |
| 17 | exactstr-silly | 24 | 3 | 8 | WRONG | casutil/caseng.exactstr: do not label a decimal as sqrt(N)/d for large N (31sqrt(47935), sqrt(32497773)/3, sqrt(252382938)/2); cap N (say <= 1000) and denominators. | 7357/2 Jun23 Q6ci; 7357/2 Jun24 Q4; 7357/2 Jun24 Q7bi |
| 18 | solve-decimal | 24 | 2 | 12 | AWKWARD | Solve screen / CAS solve exact: add a decimal line under each exact root (ln(25000/397)/ln(27/25) = 53.82). | 7357/2 Jun24 Q18a; 7357/3 Jun19 Q8a |
| 19 | slope-angled-force | 22 | 2 | 11 | AWKWARD | R/Rough slope: add the pull angle to the slope (force at theta above the line of greatest slope), so the normal reaction is mg cos a - F sin theta. | 7357/2 Jun25 Q16a; 7357/2 Jun25 Q16b |
| 20 | surd-power-simplify | 21 | 3 | 7 | AWKWARD | Simplify powers under roots and split fractions: sqrt(x^(16/15)) -> x^(8/15), (5-sqrt x)/x^2 -> 5x^-2 - x^(-3/2), exact 6 cbrt(6 pi). | 7357/2 Jun19 Q2; 7357/3 Jun22 Q8a; 7357/3 Jun23 Q4 |
| 21 | firstprin-symbolic | 18 | 2 | 9 | AWKWARD | G/First principles: also show the symbolic (f(a+h)-f(a))/h simplified in h (cancel the h), then its limit. | 7357/1 Jun18 Q15a; 7357/3 Jun24 Q10 |
| 22 | trig-exact-other | 16 | 2 | 8 | AWKWARD | New tool E/'Exact trig ratios' <given ratio, value, quadrant>: e.g. sin x = 2/3 obtuse -> tan x = -2sqrt5/5; Calc exactstr should recognise k sqrt(n)/m for small n. | 7357/1 Jun19 Q12b; 7357/1 Jun23 Q10bii |
| 23 | exp-form | 16 | 2 | 8 | GAP | Rewrite/simplify exponentials: multiply through by e^pi, write 24(3/4)^(n-1) as 3^n/2^(2n-5) (prime-power form). | 7357/1 Jun19 Q16ciii; 7357/3 Nov20 Q8bi |
| 24 | vt-cumulative | 16 | 2 | 8 | AWKWARD | Q/v-t graph points: list cumulative displacement at each point and the times where displacement returns to 0 (and allow one unknown breakpoint time). | 7357/2 Jun18 Q12b; 7357/2 Jun22 Q15 |
| 25 | inverse-one-one | 15 | 3 | 5 | WRONG | B/Inverse function: take a domain (or test one-to-one on it) and say 'many-to-one, no inverse' with a witness f(-1) = f(1); today x^2 and x^2+5 on R get sqrt answers. | 7357/1 Jun24 Q17cii; 7357/1 Jun25 Q12b; 7357/2 Jun19 Q3 |
| 26 | defint-decimal | 14 | 2 | 7 | AWKWARD | CAS definite integral: add a decimal line under the exact value. | 7357/1 Jun18 Q6c; 7357/2 Jun19 Q9c |
| 27 | sigma-symbolic | 14 | 2 | 7 | AWKWARD | D/Sigma: accept letter coefficients and give the closed form (sum of ar+5, r=1..3 -> 6a+15). | 7357/1 Nov20 Q10bi; 7357/3 Jun25 Q7 |
| 28 | proj-unknown-u | 14 | 2 | 7 | AWKWARD | Projectile tools: allow u = '?' with a given time to top, range or point; return u and angle. | 7357/2 Jun18 Q16a; 7357/2 Nov21 Q18b |
| 29 | simplify-monic-power | 14 | 2 | 7 | WRONG | caseng.simplify bug: N(x)/(ax+b)^k with k >= 2 and non-constant N becomes N/(x+b/a)^k, dropping a^k (x/(1+3x)^2 -> x/(x+1/3)^2, 9 times too big; x/(2x+1)^2 -> 4 times). Breaks CAS simplify, d/dx, G/f' at a, G/Tangent, printed f' in Stationary points, Maclaurin. Fix the monic normalisation (multiply by a^k) and add a numeric spot-check of simplify against the input. | 7357/2 Jun24 Q9ci; 7357/3 Jun22 Q10d |
| 30 | venn3 | 12 | 2 | 6 | GAP | New tool M/'Three-set Venn' from the seven counts or from totals and intersections (inclusion-exclusion), with region values and conditional probabilities. | 7357/3 Jun22 Q16a; 7357/3 Jun25 Q19b |
| 31 | binom-exact | 10 | 2 | 5 | AWKWARD | D/Binomial rational n: exact coefficients beyond x^2 (3/256 not 0.0117) and an (a+bx^m)^n form with validity \|x^m\| < \|a/b\|. | 7357/1 Jun18 Q6a; 7357/2 Jun19 Q9b |
| 32 | tri-radians | 10 | 2 | 5 | AWKWARD | Triangle tools: print angles in radians as well as degrees. | 7357/2 Jun25 Q9di; 7357/3 Jun24 Q9d |
| 33 | defint-tool-exact | 10 | 1 | 10 | AWKWARD | H/Definite integral and H/Area between curves: show the exact value the CAS already finds (16 - ln 17, 6ln4 - 5). | 7357/1 Nov20 Q15 |
| 34 | defint-symbolic-limits | 10 | 1 | 10 | WRONG | CAS definite integral: keep symbolic limits (ln 4, pi/3) exact; today ln 4 becomes 1.386294 inside e^(...) and is printed as 'exact'. | 7357/1 Nov20 Q15 |
| 35 | limit-inf-exp | 8 | 2 | 4 | WRONG | CAS limit at inf: handle exponentials (e^(-kx) -> 0, e^(kx) -> inf) for long-run model values. | 7357/3 Jun19 Q8bi; 7357/3 Jun24 Q8b |
| 36 | trig-simplify-factor | 7 | 1 | 7 | AWKWARD | Apply sin^2 + cos^2 = 1 after factoring out a common factor (4e^(2x)(sin^2 + cos^2) -> 4e^(2x)), then sqrt. | 7357/2 Jun22 Q17 |
| 37 | rationalise-cancel | 6 | 2 | 3 | AWKWARD | CAS rationalise: cancel the common integer factor ((4-2sqrt3)/4 -> (2-sqrt3)/2). | 7357/2 Jun18 Q8bi; 7357/2 Jun18 Q8bii |
| 38 | subst-reverse | 6 | 1 | 6 | GAP | H/Substitution: accept x = g(u) substitutions (x = 2 cosec u) as well as u = g(x). | 7357/1 Jun22 Q15bi |
| 39 | vec-a-to-v | 6 | 1 | 6 | AWKWARD | New/extended tool Q/'Vector a(t) to v and r' with initial v0, r0. | 7357/2 Jun25 Q19b |
| 40 | trap-data | 5 | 1 | 5 | AWKWARD | I/Trapezium rule: accept a list of ordinates (h, y0..yn) instead of f(x). | 7357/1 Jun24 Q16 |
| 41 | quad-vectors | 5 | 1 | 5 | AWKWARD | New tool J/'Quadrilateral from 4 points': side vectors, lengths, parallel pairs, parallelogram/rhombus/trapezium verdict. | 7357/2 Jun19 Q15a |
| 42 | stat-exact | 5 | 1 | 5 | WRONG | G/Stationary points: give exact coordinates when the roots of f' are surds ((-5 +- sqrt65)/2). | 7357/3 Jun22 Q10d |
| 43 | line-integer-form | 4 | 1 | 4 | AWKWARD | Line tools: always print ax + by = c with integer a, b, c (as C/Perpendicular thru pt already does). | 7357/1 Jun23 Q9aii |
| 44 | implicit-tangent | 4 | 1 | 4 | AWKWARD | G/Implicit dy/dx at a point: add the tangent and normal equations and their axis intercepts. | 7357/1 Nov20 Q12biii |
| 45 | proj-landing-speed | 4 | 1 | 4 | AWKWARD | Projectile tools: print landing velocity components, speed and angle. | 7357/2 Jun25 Q14 |
| 46 | vec-exact-speed | 4 | 1 | 4 | AWKWARD | Q/Vector r(t): exact speed (4sqrt5) alongside the decimal. | 7357/2 Nov20 Q14a |
| 47 | slope-moving-up | 4 | 1 | 4 | AWKWARD | R/Rough slope: initial direction of motion (moving up / down the slope) so friction direction is right after a string breaks. | 7357/2 Nov20 Q18bi |
| 48 | solve-exp-exact | 4 | 1 | 4 | AWKWARD | Exact solver: equations a^(px+q) = b^(rx+s) -> x = ... in ln form. | 7357/2 Nov21 Q6 |
| 49 | pmcc-table-n | 4 | 1 | 4 | AWKWARD | PMCC critical values: extend the table beyond n = 30 (or compute from the t distribution). | 7357/3 Jun24 Q16 |
| 50 | param-cart-simplify | 3 | 1 | 3 | AWKWARD | C/Param to Cartesian: simplify a^(k ln u / ln a) -> u^k and offer implicit forms (xy + 5x - 3y = 27). | 7357/1 Jun18 Q5b |
| 51 | identity-domain | 3 | 1 | 3 | AWKWARD | E/Identity check: optional interval (0 < x < pi/2). | 7357/1 Jun22 Q15aiii |
| 52 | int-trig-sub | 3 | 1 | 3 | GAP | Integrator: trig/hyperbolic substitution for 1/(x^2 sqrt(x^2-a^2)) type integrals. | 7357/1 Jun22 Q15bii |
| 53 | circle-centre-line | 3 | 1 | 3 | AWKWARD | C/Circle through 2 points with centre on a line <x1,y1,x2,y2,a,b,c>. | 7357/1 Jun23 Q9bi |
| 54 | gp-exact | 3 | 1 | 3 | AWKWARD | D/Geometric: exact S(n) when a, r are surds (15(1+sqrt2)/32). | 7357/1 Jun23 Q14bii |
| 55 | inverse-mobius | 3 | 1 | 3 | WRONG | B/Inverse function: handle (ax+b)/(cx+d) (use casalg.rearrange as CAS 'rearrange for x' already does). | 7357/1 Nov20 Q13ai |
| 56 | solve-overflow | 3 | 1 | 3 | WRONG | Solve with huge powers (7^1570): take logs symbolically before evaluating; F/Solve a^x=b should accept b given as a power. | 7357/2 Jun24 Q4 |
| 57 | stats-sxx-input | 3 | 1 | 3 | AWKWARD | L/Stats from summary: accept Sxx (sum (x-xbar)^2) as an alternative to sum x^2. | 7357/3 Jun22 Q18c |
| 58 | arc-exact | 3 | 1 | 3 | AWKWARD | E/Arc and sector: exact segment area and chord when theta is a nice multiple of pi (27(pi-3)). | 7357/3 Jun24 Q5 |
| 59 | linquad-exact | 3 | 1 | 3 | AWKWARD | B/Line meets quadratic: exact x as well as y (x = (2-sqrt6)/2). | 7357/3 Jun24 Q7b |
| 60 | snap-zero | 2 | 1 | 2 | AWKWARD | Snap \|v\| < 1e-12 to 0 in printed values (f'(pi/6) = -2.22e-16, sin(n pi/2) = 1.22e-16). | 7357/1 Jun22 Q10ciii |
| 61 | range-corner | 2 | 1 | 2 | WRONG | B/Range of f: include non-differentiable points (\|x\| corners) and endpoints when finding extremes; \|x\|+1 on [-10,10] gives '11 <= f <= 11'. | 7357/1 Jun24 Q17a |
| 62 | loglin-base | 2 | 1 | 2 | AWKWARD | F/Log-lin fit: also report log10 gradient/intercept (AQA uses log10 V = log10 a + N log10 b). | 7357/1 Nov21 Q9ci |
| 63 | factor-thm-float | 2 | 1 | 2 | WRONG | B/Factor theorem: evaluate p(a) exactly (rational arithmetic); p(-1/5) = 8.88e-16 is reported as 'not a factor'. | 7357/1 Nov21 Q13a |
| 64 | int-factor | 2 | 1 | 2 | AWKWARD | New Calculate/A helper: integer prime factorisation / primality (23 is prime: test 2, 3 up to sqrt 23). | 7357/2 Jun18 Q5 |
| 65 | int-mod | 2 | 1 | 2 | AWKWARD | Expression parser: integer mod / floor / digit functions so A/Counterexample can search digit claims. | 7357/2 Jun22 Q6a |
| 66 | beam-no-loads | 2 | 1 | 2 | AWKWARD | S/Beam on two supports: make the load list optional; g input; reactions as multiples of g. | 7357/2 Jun23 Q17ai |
| 67 | solve-crash-power | 2 | 1 | 2 | WRONG | Solve screen crashes ('<=' complex vs int) on x^1.5 = k / x^(3/2) = k. | 7357/3 Jun22 Q7b |
| 68 | cbrt-negative | 1 | 1 | 1 | WRONG | Real cube roots: (-3)^(1/3) evaluates to the complex principal root (1.56-2.5i) while the exact line shows the real root; add cbrt() and use the real branch for odd-denominator powers. | 7357/1 Jun19 Q15ai |
| 69 | circle-axes | 1 | 1 | 1 | AWKWARD | Circle tools: list x- and y-axis intersections. | 7357/1 Jun23 Q9bii |
| 70 | trig-undefined-root | 1 | 1 | 1 | WRONG | E/Solve trig eqn: drop roots where the original expression is undefined (0/0 at x = 360 with sin2x/sin x). | 7357/1 Jun24 Q15bii |
| 71 | recur-converge | 1 | 1 | 1 | AWKWARD | D/Recurrence: report convergence and the limit L = f(L). | 7357/1 Jun25 Q2 |
| 72 | recur-n-limit | 1 | 1 | 1 | AWKWARD | D/Recurrence: allow n up to e.g. 1000 (u50 refused: 'n must be 2 to 30'). | 7357/1 Nov20 Q7aii |
| 73 | vec-suvat-symbolic | 1 | 1 | 1 | AWKWARD | Q/Vector SUVAT: '?' for t to return r(t) as an expression. | 7357/2 Jun22 Q16bi |
| 74 | incdec-domain-edge | 1 | 1 | 1 | WRONG | G/Increasing/decreasing and G/Inflection points drop or merge the interval next to a domain edge or pole: ln(x)-x gives 'decreasing for all x'; x/sqrt(2x-2) omits 'convex for 1 < x < 4'. Split segments at poles of f'/f'' and at domain edges, and skip undefined stretches. | 7357/3 Jun18 Q6d |

## Top fixes in detail, with test cases from the papers

Each case gives the paper reference, what to type (in today's input conventions where possible) and the mark-scheme answer the tool should reach.

### 1. [param-letters] Letters as parameters in the numeric tools (GAP, 8 parts, 34 marks)
Today the CAS core expands, differentiates and integrates with extra letters, but Solve, Factorise, B/Quadratic, C/Circle from general, G/Stationary points, H/Separable DE, Q/a(t), Q/Vector r(t) and G/Implicit reject or mishandle them ("unknown p", "unexpected r", "no solutions found", "use t as the variable").
Proposed: parse other letters as constants; solve/factorise over x with parameters; let G/Stationary and Separable DE carry them through.

| ref | input | expected (MS) |
|---|---|---|
| 7357/2 Jun19 Q7bi | Solve `3x^2+6p*x=0` | x = 0, x = -2p |
| 7357/2 Nov20 Q9b | G/Stationary points `pi*R^2*x-pi*x^3` | max at x = R/sqrt3, V = 2sqrt3 pi R^3/9 |
| 7357/2 Nov21 Q7a | C/Circle from general `-6,-8,-p` | centre (3, 4), radius sqrt(25+p) |
| 7357/2 Nov21 Q17b | H/Separable DE at point `1,g-0.1y,0,0` | v = 10g(1 - e^(-0.1t)) |
| 7357/2 Jun23 Q14 | Q/a(t) to v and s `3k*t^2-2k*t+1,1,?,?` then v(3) = 10 | v = kt^3 - kt^2 + t + 1, k = 1/3 |
| 7357/2 Jun25 Q19a | Q/Vector r(t) to v, a `2t^3,2t^2+q*t,?` | v = 6t^2 i + (4t + q) j |
| 7357/1 Jun24 Q19 | G/Implicit dy/dx = 0 `y^3*e^(2x)+2y-16x-k` with x = 0 | y = 2, k = 12 |

### 2. [sep-exact-c] Separable DE: exact constant and solved form (AWKWARD, 5 parts, 30 marks)
The constant is printed as a decimal (2.72, 4.83, -0.307, -22.8, -0.00395) and the answer is left in the integrated implicit form.

| ref | input | expected (MS) |
|---|---|---|
| 7357/2 Jun18 Q7 | H/Separable DE at point `(x-1)e^x,1,1,e` (also needs [int-normalise]) | y = (x - 2)e^x + 2e |
| 7357/2 Jun22 Q10bii | H/Separable DE at point `1/2700,y*(900-y),0,25` | t = 3 ln(35x/(900 - x)) |
| 7357/1 Jun24 Q20b | H/Separable DE at point `-0.012,y-5,0,130` | h = 5 + 125 e^(-0.012t) |
| 7357/1 Jun25 Q17b | H/Separable DE at point `e^(2x)/(e^x+1),cos(y)^2,0,pi` | tan y = e^x + ln(2/(e^x+1)) - 1 |
| 7357/2 Nov21 Q17b | H/Separable DE at point `1,9.8-0.1y,0,0` | v = 98(1 - e^(-0.1t)) |

### 3. [mech-solve-unknown] Mechanics tools that cannot solve backwards (AWKWARD, 5 parts, 26 marks)
R/Rough slope, R/Slope and pulley and R/Tow bar crash on '?' ("'<' not supported between instances of 'NoneType' and 'int'", "unsupported operand"); R/Friction horizontal only goes from P to a; Tow bar has no a field.

| ref | input (proposed) | expected (MS) |
|---|---|---|
| 7357/2 Jun22 Q19a | R/Rough slope `20,25,?,230,9.8` with a = 1.2 | mu = 0.693 |
| 7357/2 Nov20 Q18a | R/Slope and pulley `0.2,16.26,?,2,9.81` with a = 543g/625 | mu = 0.17 |
| 7357/2 Jun18 Q17ai | R/Tow bar `410,72,300,140,?` with a = 0.2 | R = 63.6 N (then T = 78 N) |
| 7357/2 Jun23 Q15 | R/Friction horizontal `0.65/9.8,0.4,?` with a = 0.91 | D = 0.32 N |
| 7357/2 Jun23 Q19a | towed system: D = 2cos40, R1 = 0.8, a = 0.06, masses 1.5, 0.7 | R2 = 0.600 N |

### 4. [solve-range] Numeric solving only searches -20..20 (WRONG, 6 parts, 21 marks)
B/Solve f(x)=g(x), B/Inequality (+-12), the Solve screen and CAS solve all scan a fixed window and silently return the wrong root, "no solutions found", or (B/Inequality) "f > g: every x".

| ref | input | today | expected (MS) |
|---|---|---|---|
| 7357/1 Jun18 Q11b | B/Solve f(x)=g(x) `10+100(x/30)^3-50(x/30)^4,4.5*1.063^x` | only x = -12.08 | t = 49.009 (year 2029) |
| 7357/1 Jun18 Q9b | B/Solve f(x)=g(x) `4x+14(25-x),4x^2+4x(25-x)+(25-x)^2` | only x = -5 | a = -55 (and -5) |
| 7357/3 Jun19 Q8bii | Solve `5(4+11e^(-0.068066x))=21` | no solutions found | t = 58.87 |
| 7357/3 Nov20 Q5a | Solve `e^(-0.0435935x)=0.1` | no solutions found | t = 52.8 h |
| 7357/3 Jun22 Q7b | B/Solve f(x)=g(x) `0.2*x^1.5,60000` | no crossing | d = 4481 |
| 7357/1 Nov20 Q8b | B/Inequality `3.87sin(2pi(x+101.75)/365)+11.7,14` | "f > g: every x" | 300.22 < t < 408.78 (108 days) |

### 5. [simul-nonlin] Two equations, one non-linear (AWKWARD, 4 parts, 23 marks)
Proposed new tool B/"Simultaneous non-linear" `f(x,y)=0, g(x,y)=0`.

| ref | equations | expected (MS) |
|---|---|---|
| 7357/1 Jun18 Q9b | a + 5d = 25; 4a + 70d = 4a^2 + 20ad + 25d^2 | (a, d) = (-5, 6), (-55, 16); smallest a = -55 |
| 7357/2 Jun19 Q6 | a^2 + b^2 = 16; (sqrt3/2)a + b/2 = 2sqrt3 | a = 2, b = 2sqrt3 (or a = 4, b = 0) |
| 7357/3 Nov20 Q8a | a/(1-r) = 96; ar = 18 | a = 24, r = 3/4 (a < 30) |
| 7357/3 Jun19 Q8a | 5(4 + L) = 75; 5(4 + L e^(-2k)) = 68 | L = 11, k = 0.068066 |

### 6. [subst-x-remains] H/Substitution stops at "x remains" (WRONG, 4 parts, 23 marks)
The tool never rewrites the leftover x through x = g^-1(u).

| ref | input | expected (MS) |
|---|---|---|
| 7357/2 Nov20 Q5 | `x*sqrt(4x+1),4x+1` | (1/16) int (u^(3/2) - u^(1/2)) du on [0, 25] = 875/12 |
| 7357/3 Jun23 Q8 | `x^9/(x^5+2)^3,x^5+2` | (1/5) int (u - 2)/u^3 du on [2, 3] = 1/180 |
| 7357/1 Jun24 Q18a | `(4x+1)sqrt(2x+1),2x+1` | (1/2) int (2u^(3/2) - u^(1/2)) du on [1, 9]; a = 1; value 1322/15 |
| 7357/1 Jun25 Q17a | `e^(2x)/(e^x+1),e^x+1` | int (u - 1)/u du = e^x - ln(e^x + 1) + k |

### 7. [log-symbolic] Logs with a letter base, two-variable log rearranging (GAP, 5 parts, 14 marks)
CAS "expand trig / log" and F/Evaluate log expr return logb(a, ...) unchanged.

| ref | input | expected (MS) |
|---|---|---|
| 7357/3 Jun18 Q7a | `2*logb(a,7)+logb(a,4)+1/2` = log_a y | y = 196 sqrt(a) |
| 7357/1 Jun25 Q3 | `logb(3,2x)-logb(3,x)` | log3 2 |
| 7357/3 Jun25 Q4b | `logb(a,sqrt(a))-logb(a,1/a^2)` | 5/2 |
| 7357/2 Jun22 Q9 | `logb(2,x^3)-logb(2,y^2)=9` | x = 8 y^(2/3) |
| 7357/3 Nov20 Q8bii | `logb(3,3^n/2^(2n-5))` | n(1 - 2log3 2) + 5 log3 2 |

### 8. [moments-unknown] Moments with one unknown (AWKWARD, 5 parts, 14 marks)

| ref | set-up | expected (MS) |
|---|---|---|
| 7357/2 Jun19 Q14a | rod 20 cm, pivot A at 14 cm, 0.28 kg at 17 cm, rod mass m at 10 cm | m = 0.21 |
| 7357/2 Jun19 Q14b | same rod, n x 0.048 kg at 19 cm | n = 3.5 -> 3 |
| 7357/2 Jun22 Q14a | 12 g at 66 mm one side, m at 80 mm other side | m = 9.9 g |
| 7357/2 Nov20 Q13a | rod 7 m, 4 kg, pivot 2 m from A, W at A | W = 3g |
| 7357/2 Jun23 Q17ai | S/Beam `7,?,1.4,5` with R_X = 4g | M = 9.6 kg; R_Y = 5.6g |

### 9. [int-normalise] Integrator misses equivalent forms (WRONG, 3 parts, 19 marks)

| ref | input | today | expected (MS) |
|---|---|---|---|
| 7357/2 Jun18 Q7 | CAS integrate `(x-1)e^x` | no elementary integral | (x - 2)e^x + c |
| 7357/2 Jun19 Q5 | H/Separable DE at point `ln(x)/x^2,1/y,1,2` | no standard integral (works as `x^(-2)*ln(x)`) | t^2 = 6 - 2(1 + ln x)/x |
| 7357/1 Nov21 Q15b | CAS definite integral `sqrt(16x^3)` 0..0.25 | numeric 0.05 | 1/20 = 2^-2 5^-1 |

### 10. [pf-monic] Partial fractions printed over monic factors (AWKWARD, 4 parts, 12 marks)

| ref | input | today | expected (MS) |
|---|---|---|---|
| 7357/2 Nov21 Q5 | `5(x-3),(2x-11)(4-3x)` | -1/3/(x-4/3) + (-1)/2/(x-11/2) | -1/(2x-11) + 1/(4-3x) |
| 7357/1 Jun23 Q16a | `1,16-9x^2` | -1/24/(x-4/3) + 1/24/(x+4/3) | (1/8)/(4-3x) + (1/8)/(4+3x) |
| 7357/2 Jun24 Q9b | `36x,(1+3x)(2-3x)` | -4/3/(x+1/3) + (-8)/3/(x-2/3) | 8/(2-3x) - 4/(1+3x) |
| 7357/3 Jun25 Q8a | `x,2x^2+3x+1` | 1/(x+1) + (-1)/2/(x+1/2) | 1/(x+1) - 1/(2x+1) |

### 11. [range-infinite] Range over an unbounded domain (AWKWARD, 5 parts, 9 marks)

| ref | input | expected (MS) |
|---|---|---|
| 7357/1 Jun19 Q6a | `(x^2+1)/2` on x >= 0 | y >= 1/2 |
| 7357/1 Jun25 Q12a | `x^2+5` on R | y >= 5 |
| 7357/1 Jun25 Q12dii | `sqrt(x^2+5)` on R | y >= sqrt5 |
| 7357/2 Jun23 Q8b | `2/sin(x)^2` | A >= 2 |
| 7357/3 Jun22 Q10e | `(x^2+10)/(2x+5)`, x != -2.5 | y <= (-5-sqrt65)/2 or y >= (-5+sqrt65)/2 |

### 12. [foot-perp] Foot of perpendicular / distance from a point to a line (AWKWARD, 3 parts, 14 marks)
Proposed C/"Foot of perpendicular" `a,b,c,px,py` for the line ax + by = c.

| ref | input | expected (MS) |
|---|---|---|
| 7357/1 Nov21 Q5b | `-4,3,21,15,2` | foot (3, 11), distance 15 |
| 7357/1 Jun22 Q8ai | `5,3,83,0,5` | Q = (10, 11), PQ = 2sqrt34 |
| 7357/2 Nov20 Q6a | `12,5,298,7,9` | (19, 14), r = 13 |

### 13. [surd-algebra] Algebra in sqrt(x) (GAP, 3 parts, 11 marks)

| ref | input | expected (MS) |
|---|---|---|
| 7357/3 Nov21 Q6 | simplify `(10+5x-2sqrt(x)-x^(3/2))/(5-sqrt(x))` | 2 + x |
| 7357/1 Jun23 Q7a | single fraction `7/(3+5sqrt(x))-7/(5sqrt(x)-3)` | -42/(25n - 9) |
| 7357/1 Jun24 Q7 | rationalise `(3+sqrt(8x))/(1+sqrt(2x))` | (4n - 3 + sqrt(2n))/(2n - 1) |

### 14. [deriv-simplify] Derivatives left uncollected (AWKWARD, 3 parts, 10 marks)

| ref | input | today | expected (MS) |
|---|---|---|---|
| 7357/1 Jun19 Q16a | d/dx `e^(-x)*(sin(x)+cos(x))` | (cos x - sin x)e^-x - (cos x + sin x)e^-x | -2e^-x sin x |
| 7357/1 Jun25 Q15a | d/dx `(x-3)^2+(x^2-2.5)^2` | 4x(x^2 - 5/2) + 2(x - 3) | 4x^3 - 8x - 6 |
| 7357/3 Jun18 Q6b | d/dx `x/sqrt(2x-2)` | (sqrt(2x-2) - x/sqrt(2x-2))/(2x-2) | (x - 2)/(2x - 2)^(3/2) |

### 15. [domain] Natural domain (GAP, 4 parts, 7 marks) and [log-combine] (AWKWARD, 2 parts, 14 marks), tied on score

| ref | input | expected (MS) |
|---|---|---|
| 7357/3 Jun18 Q6a | domain of `x/sqrt(2x-2)` | x > 1 |
| 7357/2 Nov21 Q10a | domain of `sqrt(x)/(x-3)` | {x : x >= 0, x != 3} |
| 7357/2 Jun23 Q7b | domain of `1/sqrt(10-2x)` | x < 5 |
| 7357/1 Jun24 Q17b | domain of `ln(x)` | x > 0 |
| 7357/3 Jun24 Q11 | CAS definite integral `(x^2-8x)ln(x)` 1..8 | -256ln8/3 + 623/9 -> area 256 ln 2 - 623/9 |
| 7357/3 Jun25 Q8b | CAS definite integral `x/(2x^2+3x+1)` 0..4 | ln(5/3) |

## Also noted in OK rows (suggestions, not counted in the scores)

The step worked, but the note in the paper table points at a smaller improvement.

- **[solve-decimal]** Solve screen / CAS solve exact: add a decimal line under each exact root (ln(25000/397)/ln(27/25) = 53.82). (7: 1-jun24 Q20c, 1-jun25 Q10c, 2-jun18 Q9ci, 2-jun18 Q15a, 2-jun19 Q8c, 2-jun23 Q20, 3-jun24 Q8ci)
- **[binom-exact]** D/Binomial rational n: exact coefficients beyond x^2 (3/256 not 0.0117) and an (a+bx^m)^n form with validity |x^m| < |a/b|. (3: 1-jun18 Q6b, 2-jun19 Q9a, 2-nov20 Q3)
- **[iter-labels]** Iteration tools: let the user say the start is x1 or x0 so labels match the paper. (2: 1-jun19 Q7di, 1-nov21 Q7c)
- **[defint-tool-exact]** H/Definite integral and H/Area between curves: show the exact value the CAS already finds (16 - ln 17, 6ln4 - 5). (2: 1-jun19 Q14b, 1-nov21 Q10b)
- **[snap-zero]** Snap |v| < 1e-12 to 0 in printed values (f'(pi/6) = -2.22e-16, sin(n pi/2) = 1.22e-16). (1: 1-jun18 Q3)
- **[circle-point]** Circle tools: point inside/on/outside test. (1: 1-jun18 Q7bii)
- **[expmodel-predict]** F/N = A e^(kt) 2 pts: add 'N at t' and 't for N' fields so k is not retyped. (1: 1-jun18 Q10a)
- **[deriv-simplify]** After d/dx, collect like terms and combine into one fraction (expand + single fraction), e.g. (cos x - sin x)e^-x - (cos x + sin x)e^-x -> -2e^-x sin x. (1: 1-jun19 Q13)
- **[param-letters]** Let numeric tools carry extra letters as symbolic constants: Solve / B/Factorise / B/Quadratic / C/Circle from general / G/Stationary points / H/Separable DE / Q/Vector r(t) / Q/a(t) to v and s should accept p, q, k, R, g etc. (the CAS core already expands, differentiates and integrates with letters). Minimum: Solve and Factorise over x with parameters. (1: 1-jun24 Q8a)
- **[ap-first-last]** D/Arithmetic: sum from n, first and last term. (1: 1-jun24 Q10a)
- **[quad-vectors]** New tool J/'Quadrilateral from 4 points': side vectors, lengths, parallel pairs, parallelogram/rhombus/trapezium verdict. (1: 2-jun18 Q14b)
- **[exactstr-silly]** casutil/caseng.exactstr: do not label a decimal as sqrt(N)/d for large N (31sqrt(47935), sqrt(32497773)/3, sqrt(252382938)/2); cap N (say <= 1000) and denominators. (1: 2-jun19 Q8b)
- **[beam-g]** S/Beam: g input (question used 9.81, tool fixes 9.8). (1: 2-jun25 Q18a)
- **[trap-data]** I/Trapezium rule: accept a list of ordinates (h, y0..yn) instead of f(x). (1: 2-nov20 Q15a)
- **[circle-area]** Circle tools: area and circumference. (1: 3-jun18 Q1)
- **[hist-fd-input]** Histogram/grouped tools: accept frequency densities (fd x width). (1: 3-jun18 Q12)
- **[sig-percent-trap]** HT tools: when sig < 1, ask/assume it is a proportion (0.1 -> 10%); today 0.1 is silently 0.1%. (1: 3-jun18 Q17a)
- **[implicit-tangent]** G/Implicit dy/dx at a point: add the tangent and normal equations and their axis intercepts. (1: 3-jun19 Q9biii)
- **[outlier-given-q]** L/Outliers: allow given quartiles/median instead of sample ones. (1: 3-jun23 Q15ai)
- **[twoway-2x3]** M/Two-way table: allow 2x3 and larger tables. (1: 3-nov20 Q13b)
- **[ztest-raw]** z tests: accept raw data (compute xbar). (1: 3-nov20 Q14)

## Other observations

- HT tools read sig as a percentage; typing 0.1 for "10%" silently tests at 0.1% (found on 7357/3 Jun18 Q17-18 before switching to 10).
- N/Binomial least k answers P(X <= k) >= p, so an upper-tail critical value is k + 1 (7357/3 Jun18 Q17b: tool 13, MS 14). O/HT binomial upper gives the CR directly.
- Result screens hide working lines and show 3 s.f. until FORMAT is pressed; answers asked to 4-7 s.f. are there in the full-precision view.
- The Solve screen keeps exact roots only (no decimal); B/Solve f(x)=g(x) shows decimals but has the -20..20 limit, so for big roots neither is good today.

## Regression cases (JSON lines)

One line per checked output from an OK row. Fields: paper, q, module (file:section, or casui:CAS / casui:Calculate), tool (label or CAS op), inputs (typed text), expect (substring of the flattened output, all lines including working). CAS rows add `ask` (the follow-up prompt text) and `deg`; Calculate rows add `deg`; `full: true` means the result was read with FORMAT on full precision (casutil.FULL = True). The harness used is `tests.run_case`-style: casutil.convert(spec, inputs) then casutil.call_tool; CAS ops via casui._cas_op(op_index, tree, text) with casutil.ask patched to return `ask`; Calculate via casui._forms(expr).

```jsonl
{"paper": "73571-jun18", "q": "1", "module": "casui:CAS", "tool": "d/dx", "inputs": "1/x^2", "expect": "-2/x^3", "ask": null, "deg": false}
{"paper": "73571-jun18", "q": "2", "module": "mpure:B", "tool": "Transform af(bx+c)+d", "inputs": "5^x,5,1,0,0", "expect": "5*5^x"}
{"paper": "73571-jun18", "q": "3", "module": "mpure:D", "tool": "Terms of u(n)", "inputs": "sin(n*pi/2),1,8", "expect": "period 4"}
{"paper": "73571-jun18", "q": "4", "module": "mpure:B", "tool": "Inverse function", "inputs": "e^(x-4)", "expect": "ln(x)+4"}
{"paper": "73571-jun18", "q": "5a", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "4*2^(-t)+3,3*2^t-5,?", "expect": "2^(2*t)"}
{"paper": "73571-jun18", "q": "6b", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "(4-x^3)^(-1/2)", "expect": "3*x^6/256", "ask": "7", "deg": false}
{"paper": "73571-jun18", "q": "6dii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "4^(1/3)", "expect": "1.587", "deg": false}
{"paper": "73571-jun18", "q": "7a", "module": "mpure:C", "tool": "Triangle 3 vertices", "inputs": "8,17,15,10,-2,-7", "expect": "right angle at B"}
{"paper": "73571-jun18", "q": "7bii", "module": "mpure:C", "tool": "Circle through 3 pts", "inputs": "8,17,15,10,-2,-7", "expect": "13"}
{"paper": "73571-jun18", "q": "7bii", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "3,5,0,-8,-2,0", "expect": "sqrt(170)"}
{"paper": "73571-jun18", "q": "8b", "module": "mcalc:I", "tool": "Newton-Raphson", "inputs": "x-2sin(x),pi,2", "expect": "1.91322"}
{"paper": "73571-jun18", "q": "8c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(1.91322-1.89549)/1.89549*100", "expect": "0.935", "deg": false}
{"paper": "73571-jun18", "q": "9a", "module": "mpure:B", "tool": "Expand", "inputs": "36a+630d-(6a+15d)^2", "expect": "-36*a^2"}
{"paper": "73571-jun18", "q": "9a", "module": "casui:CAS", "tool": "expand", "inputs": "(6a+15d)^2", "expect": "36*a^2", "ask": null, "deg": false}
{"paper": "73571-jun18", "q": "10a", "module": "mpure:F", "tool": "N = A e^(kt) 2 pts", "inputs": "0,400,5.7,200", "expect": "0.1216"}
{"paper": "73571-jun18", "q": "10a", "module": "mpure:F", "tool": "Evaluate A e^(kt)", "inputs": "400,-0.1216047,4", "expect": "N = 246"}
{"paper": "73571-jun18", "q": "10b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "400*e^(-0.1216047x)=280", "expect": "2.933", "ask": null, "deg": false}
{"paper": "73571-jun18", "q": "11aii", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "(60x^2+162000/x)^(1/3),38,3", "expect": "53.504"}
{"paper": "73571-jun18", "q": "11b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "10+100(x/30)^3-50(x/30)^4-4.5*1.063^x,49,50", "expect": "sign change 49 to 49.1"}
{"paper": "73571-jun18", "q": "12a", "module": "mpure:B", "tool": "Factor theorem", "inputs": "30x^3-7x^2-7x+2,-1/2", "expect": "0"}
{"paper": "73571-jun18", "q": "12b", "module": "mpure:B", "tool": "Factorise", "inputs": "30x^3-7x^2-7x+2", "expect": "(2*x+1)"}
{"paper": "73571-jun18", "q": "12c", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "30sec(x)^2+2cos(x)-7(sec(x)+1),0,360", "expect": "no solution"}
{"paper": "73571-jun18", "q": "13", "module": "mcalc:G", "tool": "Stationary points", "inputs": "4x*sqrt(16-x^2)", "expect": "32"}
{"paper": "73571-jun18", "q": "15a", "module": "mcalc:G", "tool": "First principles", "inputs": "x^3-48x,-4", "expect": "f'(-4) = 0"}
{"paper": "73571-jun18", "q": "15a", "module": "casui:CAS", "tool": "simplify", "inputs": "((-4+x)^3-48(-4+x)-128)/x", "expect": "x^2-12*x", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "1", "module": "casui:CAS", "tool": "expand trig / log", "inputs": "-4*log(sqrt(x))", "expect": "-2*log(x)", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "1", "module": "casui:CAS", "tool": "expand trig / log", "inputs": "-2*log(1/x)", "expect": "2*log(x)", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "2", "module": "casui:CAS", "tool": "d/dx", "inputs": "e^(k*x)", "expect": "e^(k*x)*k", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "3", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "4,0.8", "expect": "sector area = 32/5"}
{"paper": "73571-jun19", "q": "4", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5*(-1)+4x=17", "expect": "11/2", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "4", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5*3+4x=17", "expect": "1/2", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "4", "module": "mpure:C", "tool": "Perpendicular bisect", "inputs": "-1,11/2,3,1/2", "expect": "11"}
{"paper": "73571-jun19", "q": "5b", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "4,30,65,60,1770,315", "expect": "x = 20"}
{"paper": "73571-jun19", "q": "5b", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "4,30,65,60,1770,315", "expect": "y = -1/2"}
{"paper": "73571-jun19", "q": "5b", "module": "mpure:D", "tool": "Arithmetic a,d,n", "inputs": "20,-0.5,41", "expect": "410"}
{"paper": "73571-jun19", "q": "6bi", "module": "mpure:B", "tool": "Inverse function", "inputs": "(x^2+1)/2", "expect": "sqrt(2*x-1)"}
{"paper": "73571-jun19", "q": "6d", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "(x^2+1)/2,sqrt(2x-1)", "expect": "(1, 1)"}
{"paper": "73571-jun19", "q": "7b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "1/x-sec(2x),0.4,0.6,2", "expect": "1.06"}
{"paper": "73571-jun19", "q": "7b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "1/x-sec(2x),0.4,0.6,2", "expect": "-1.09"}
{"paper": "73571-jun19", "q": "7di", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "acos(x)/2,0.4,3", "expect": "x1 = 0.57963974"}
{"paper": "73571-jun19", "q": "7di", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "acos(x)/2,0.4,3", "expect": "x2 = 0.47625491"}
{"paper": "73571-jun19", "q": "7di", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "acos(x)/2,0.4,3", "expect": "x3 = 0.53720285"}
{"paper": "73571-jun19", "q": "8a", "module": "mpure:D", "tool": "Sigma sum f(r) a..b", "inputs": "r^3,0,3", "expect": "36"}
{"paper": "73571-jun19", "q": "8a", "module": "mpure:D", "tool": "Sigma sum f(r) a..b", "inputs": "r^3,0,10", "expect": "3025"}
{"paper": "73571-jun19", "q": "8b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(1.25*10^8)^(1/3)", "expect": "500", "deg": false}
{"paper": "73571-jun19", "q": "10", "module": "casui:CAS", "tool": "d/dx", "inputs": "4/3*pi*x^3", "expect": "4*pi*x^2", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "11", "module": "casui:CAS", "tool": "limit x -> a", "inputs": "sin(x)/x", "expect": "1", "ask": "0", "deg": false}
{"paper": "73571-jun19", "q": "11", "module": "casui:CAS", "tool": "limit x -> a", "inputs": "(cos(x)-1)/x", "expect": "0", "ask": "0", "deg": false}
{"paper": "73571-jun19", "q": "12b", "module": "mpure:B", "tool": "Quadratic", "inputs": "4,-4,-3", "expect": "x = -1/2"}
{"paper": "73571-jun19", "q": "12b", "module": "mpure:B", "tool": "Quadratic", "inputs": "4,-4,-3", "expect": "x = 3/2"}
{"paper": "73571-jun19", "q": "12b", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "1/sin(x)-3/2,90,180", "expect": "138"}
{"paper": "73571-jun19", "q": "12b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "tan(180-asin(2/3))", "expect": "-2sqrt(5)/5", "deg": true}
{"paper": "73571-jun19", "q": "13", "module": "mcalc:G", "tool": "Stationary points", "inputs": "e^(3x-5)/x^2", "expect": "2/3"}
{"paper": "73571-jun19", "q": "14aii", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "2x^3/(x^2+1),0,4,4", "expect": "13.36"}
{"paper": "73571-jun19", "q": "14b", "module": "mcalc:H", "tool": "Definite integral", "inputs": "2x^3/(x^2+1),0,4", "expect": "F(x) = x^2-ln(x^2+1)"}
{"paper": "73571-jun19", "q": "14b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "2x^3/(x^2+1)", "expect": "ln(17)", "ask": "0,4", "deg": false}
{"paper": "73571-jun19", "q": "15ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "3+2*3^(1/3)", "expect": "5.88", "deg": false}
{"paper": "73571-jun19", "q": "15aii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "4-(2x/3-2)^2=0", "expect": "x = 0", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "15aii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "4-(2x/3-2)^2=0", "expect": "x = 6", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "15aiii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "3-2*(6-3)^(1/3)", "expect": "0.115", "deg": false}
{"paper": "73571-jun19", "q": "15b", "module": "mcalc:G", "tool": "Stationary points", "inputs": "4-(2x/3-2)^2", "expect": "(3, 4)"}
{"paper": "73571-jun19", "q": "16a", "module": "casui:CAS", "tool": "expand", "inputs": "(cos(x)-sin(x))*e^(-x)-(cos(x)+sin(x))*e^(-x)", "expect": "-2*e^(-x)*sin(x)", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "16b", "module": "casui:CAS", "tool": "integrate", "inputs": "e^(-x)*sin(x)", "expect": "(-cos(x)-sin(x))*e^(-x)/2", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "16ci", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "e^(-x)*sin(x)", "expect": "e^(-pi)", "ask": "0,pi", "deg": false}
{"paper": "73571-jun19", "q": "16cii", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "e^(-x)*sin(x)", "expect": "e^(-2*pi)", "ask": "pi,2*pi", "deg": false}
{"paper": "73571-jun19", "q": "16ciii", "module": "casui:CAS", "tool": "simplify", "inputs": "((1+e^(-pi))/2)/(1-e^(-pi))", "expect": "(e^(-pi)+1)/(2*(-e^(-pi)+1))", "ask": null, "deg": false}
{"paper": "73571-jun19", "q": "16ciii", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "(1+e^(-pi))/2,e^(-pi),5", "expect": "0.545"}
{"paper": "73571-jun22", "q": "1", "module": "mpure:C", "tool": "Param to Cartesian", "inputs": "cos(t),sin(t)", "expect": "x^2 + y^2 = 1"}
{"paper": "73571-jun22", "q": "2", "module": "mpure:D", "tool": "Terms of u(n)", "inputs": "(-1)^n,1,4", "expect": "period 2"}
{"paper": "73571-jun22", "q": "3", "module": "mpure:B", "tool": "Transform af(bx+c)+d", "inputs": "logb(4,x),2,1,0,0", "expect": "2*logb(4,x)"}
{"paper": "73571-jun22", "q": "5", "module": "mcalc:G", "tool": "Tangent and normal", "inputs": "(x-2)^4,0", "expect": "-32*x+16"}
{"paper": "73571-jun22", "q": "6a", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-1/2,1/2", "expect": "x^0: 1"}
{"paper": "73571-jun22", "q": "6a", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-1/2,1/2", "expect": "x^1: -1/4"}
{"paper": "73571-jun22", "q": "6b", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "sin(4x)+sqrt(cos(x))", "expect": "-x^2/4+4*x+1", "ask": "3", "deg": false}
{"paper": "73571-jun22", "q": "8ai", "module": "mpure:C", "tool": "Perpendicular thru pt", "inputs": "-5/3,0,5", "expect": "3/5"}
{"paper": "73571-jun22", "q": "8ai", "module": "mpure:C", "tool": "Intersect y=mx+c", "inputs": "3/5,5,-5/3,83/3", "expect": "(10, 11)"}
{"paper": "73571-jun22", "q": "8aii", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "0,5,0,10,11,0", "expect": "2sqrt(34)"}
{"paper": "73571-jun22", "q": "8bi", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5x+3*(-17)=49", "expect": "20", "ask": null, "deg": false}
{"paper": "73571-jun22", "q": "8bii", "module": "mpure:C", "tool": "Circle centre+radius", "inputs": "20,-17,sqrt(34)", "expect": "= 34"}
{"paper": "73571-jun22", "q": "9a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5x+1-(2x+5)=6x+7-(5x+1)", "expect": "5", "ask": null, "deg": false}
{"paper": "73571-jun22", "q": "9c", "module": "mpure:D", "tool": "AP: n for Sn > k", "inputs": "15,11,100000", "expect": "134"}
{"paper": "73571-jun22", "q": "10b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x-sin(2x),pi/5,2pi/5,1", "expect": "-0.32"}
{"paper": "73571-jun22", "q": "10b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x-sin(2x),pi/5,2pi/5,1", "expect": "0.668"}
{"paper": "73571-jun22", "q": "10ci", "module": "mcalc:I", "tool": "Newton-Raphson", "inputs": "x-sin(2x),pi/5,2", "expect": "1.041"}
{"paper": "73571-jun22", "q": "11a", "module": "casui:CAS", "tool": "substitute x = a", "inputs": "x^3+(b+2)x^2+2(b+2)x+8", "expect": "0", "ask": "-2", "deg": false}
{"paper": "73571-jun22", "q": "11bii", "module": "mpure:B", "tool": "Discriminant in k", "inputs": "1,k,4", "expect": "k = -4, 4"}
{"paper": "73571-jun22", "q": "12ai", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "1,1/2,10", "expect": "S(inf) = 2"}
{"paper": "73571-jun22", "q": "12aii", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "1/2,1/2,10", "expect": "S(inf) = 1"}
{"paper": "73571-jun22", "q": "12b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "1/(1-cos(x))-(2-sqrt(2)),0,2pi", "expect": "x = 3pi/4"}
{"paper": "73571-jun22", "q": "13a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "16^2=x*sqrt(16)", "expect": "64", "ask": null, "deg": false}
{"paper": "73571-jun22", "q": "13b", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "x^2+y^2-64sqrt(x)+y", "expect": "dy/dx = 0 at (6.35, 10.5)"}
{"paper": "73571-jun22", "q": "14a", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "(2x-8)ln(x),1,4,4", "expect": "5.28"}
{"paper": "73571-jun22", "q": "14b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "(2x-8)ln(x)", "expect": "-16*ln(4)+33/2", "ask": "1,4", "deg": false}
{"paper": "73571-jun22", "q": "15aii", "module": "casui:CAS", "tool": "d/dx", "inputs": "1/sin(x)", "expect": "-cos(x)*cosec(x)^2", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "1", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "-3,2,7", "expect": "x^7: 128"}
{"paper": "73571-jun23", "q": "2", "module": "casui:CAS", "tool": "d/dx", "inputs": "2x^3", "expect": "6*x^2", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "3", "module": "mpure:B", "tool": "Transform af(bx+c)+d", "inputs": "ln(x),1,1/2,0,0", "expect": "ln(x/2)"}
{"paper": "73571-jun23", "q": "4", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "cos(2x)", "expect": "-2*x^2+1", "ask": "3", "deg": false}
{"paper": "73571-jun23", "q": "5a", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "5/(e^x-1),1,4,5", "expect": "2.3315"}
{"paper": "73571-jun23", "q": "5b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "4*2.3315", "expect": "9.326", "deg": false}
{"paper": "73571-jun23", "q": "6", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "2log(x)=log(4)+log(x+8)", "expect": "8", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "6", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,-4,-32", "expect": "x = -4"}
{"paper": "73571-jun23", "q": "6", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,-4,-32", "expect": "x = 8"}
{"paper": "73571-jun23", "q": "8", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "x*sin(4x)", "expect": "-pi/8", "ask": "0,pi/2", "deg": false}
{"paper": "73571-jun23", "q": "9a", "module": "mpure:C", "tool": "Perpendicular bisect", "inputs": "-6,15,12,19", "expect": "midpoint (3, 17)"}
{"paper": "73571-jun23", "q": "9a", "module": "mpure:C", "tool": "Perpendicular bisect", "inputs": "-6,15,12,19", "expect": "y = -(9/2)x + 61/2"}
{"paper": "73571-jun23", "q": "10ai", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "sin(x)-0.5,-360,0", "expect": "-330"}
{"paper": "73571-jun23", "q": "10ai", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "sin(x)-0.5,-360,0", "expect": "-210"}
{"paper": "73571-jun23", "q": "10bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "cos(180+asin(3/7))", "expect": "-0.9035079029", "deg": true}
{"paper": "73571-jun23", "q": "11bi", "module": "casui:CAS", "tool": "expand", "inputs": "x(400x+70)+70-382", "expect": "400*x^2+70*x-312", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "11bii", "module": "mpure:B", "tool": "Quadratic", "inputs": "200,35,-156", "expect": "x = -39/40"}
{"paper": "73571-jun23", "q": "11bii", "module": "mpure:B", "tool": "Quadratic", "inputs": "200,35,-156", "expect": "x = 4/5"}
{"paper": "73571-jun23", "q": "11bii", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "0.8u+70,400,5", "expect": "u(4) = 1878/5"}
{"paper": "73571-jun23", "q": "11bii", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "0.8u+70,400,5", "expect": "u(5) = 9262/25"}
{"paper": "73571-jun23", "q": "11cii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "x=0.8x+70", "expect": "350", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "12b", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "-4,1", "expect": "R = sqrt(17)"}
{"paper": "73571-jun23", "q": "12b", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "-4,1", "expect": "be = -76 deg"}
{"paper": "73571-jun23", "q": "12c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "7-sqrt(17)", "expect": "2.876", "deg": false}
{"paper": "73571-jun23", "q": "13c", "module": "mcalc:I", "tool": "Newton-Raphson", "inputs": "x-cos(x),0,3", "expect": "0.7391"}
{"paper": "73571-jun23", "q": "14ai", "module": "casui:CAS", "tool": "d/dx", "inputs": "2^x", "expect": "2^x*ln(2)", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "14aii", "module": "casui:CAS", "tool": "integrate", "inputs": "2^x", "expect": "2^x/ln(2)", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "14bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.5*2^(-1/2)", "expect": "sqrt(2)/4", "deg": false}
{"paper": "73571-jun23", "q": "14bii", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "sqrt(2)/4,sqrt(2)/2,8", "expect": "S(8) = 1.13"}
{"paper": "73571-jun23", "q": "14biii", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "2^x", "expect": "15/(16*ln(2))", "ask": "-4,0", "deg": false}
{"paper": "73571-jun23", "q": "15", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "x^2+2y^3-4x*y", "expect": "(4, 2)"}
{"paper": "73571-jun23", "q": "16a", "module": "mpure:B", "tool": "Partial fractions", "inputs": "1,16-9x^2", "expect": "-1/24/(x-4/3)+1/24/(x+4/3)"}
{"paper": "73571-jun23", "q": "16bi", "module": "casui:CAS", "tool": "expand", "inputs": "0.16-0.36(x/2)^2", "expect": "-9*x^2/100+4/25", "ask": null, "deg": false}
{"paper": "73571-jun23", "q": "16bii", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "1/100,16-9y^2,0,0", "expect": "ln(|y+4/3|)/24-ln(|y-4/3|)/24 = x/100"}
{"paper": "73571-jun23", "q": "16biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "25/6*ln(7)", "expect": "8.1", "deg": false}
{"paper": "73571-jun24", "q": "1", "module": "casui:CAS", "tool": "expand", "inputs": "(4x^3-5x^2+3x-2)(x^5+4x+1)", "expect": "-5*x", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "2", "module": "mpure:B", "tool": "Inverse function", "inputs": "e^x+1", "expect": "ln(x-1)"}
{"paper": "73571-jun24", "q": "3", "module": "mpure:B", "tool": "Divide p(x) by d(x)", "inputs": "12x^2+3x+7,3x-5", "expect": "4*x"}
{"paper": "73571-jun24", "q": "5", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "sin(x)^2-1,0,360", "expect": "90"}
{"paper": "73571-jun24", "q": "5", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "sin(x)^2-1,0,360", "expect": "270"}
{"paper": "73571-jun24", "q": "6", "module": "casui:CAS", "tool": "d/dx", "inputs": "(x^3+5x)^7", "expect": "7*(3*x^2+5)*(x^3+5*x)^6", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "8a", "module": "casui:CAS", "tool": "expand", "inputs": "(2+k*x)^5", "expect": "80*k^2*x^2", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "8b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "80x=4*80x^2", "expect": "0", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "8b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "80x=4*80x^2", "expect": "1/4", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "9a", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "cos(4x)+2sin(3x)-tan(2x)", "expect": "-8*x^2+4*x+1", "ask": "3", "deg": false}
{"paper": "73571-jun24", "q": "9b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1+4*0.07-8*0.07^2", "expect": "1.2408", "deg": false}
{"paper": "73571-jun24", "q": "10a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "300/2*(-7+32)", "expect": "3750", "deg": false}
{"paper": "73571-jun24", "q": "10b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "9/2*(x+6x)=1260", "expect": "40", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "12a", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "-6/u,3,4", "expect": "u(2) = -2"}
{"paper": "73571-jun24", "q": "12a", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "-6/u,3,4", "expect": "u(3) = 3"}
{"paper": "73571-jun24", "q": "12a", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "-6/u,3,4", "expect": "u(4) = -2"}
{"paper": "73571-jun24", "q": "12a", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "-6/u,3,4", "expect": "period 2"}
{"paper": "73571-jun24", "q": "12c", "module": "mpure:D", "tool": "Recurrence sum to N", "inputs": "-6/u,3,101", "expect": "53"}
{"paper": "73571-jun24", "q": "13a", "module": "mpure:B", "tool": "Factor theorem", "inputs": "4x^3+8x^2+11x+4,-1/2", "expect": "is a factor"}
{"paper": "73571-jun24", "q": "13b", "module": "mpure:B", "tool": "Divide p(x) by d(x)", "inputs": "4x^3+8x^2+11x+4,2x+1", "expect": "2*x^2+3*x+4"}
{"paper": "73571-jun24", "q": "14a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x^3-e^(6-2x),0,4,1", "expect": "-403"}
{"paper": "73571-jun24", "q": "14a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x^3-e^(6-2x),0,4,1", "expect": "63.8"}
{"paper": "73571-jun24", "q": "14ci", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "3-1.5ln(x),4,3", "expect": "0.92055", "full": true}
{"paper": "73571-jun24", "q": "14ci", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "3-1.5ln(x),4,3", "expect": "3.12416", "full": true}
{"paper": "73571-jun24", "q": "14ci", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "3-1.5ln(x),4,3", "expect": "1.29125", "full": true}
{"paper": "73571-jun24", "q": "15a", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "sin(2x)/sin(x)+cos(2x)/cos(x),4cos(x)-1/cos(x)", "expect": "holds"}
{"paper": "73571-jun24", "q": "16", "module": "mmech:Q", "tool": "v-t graph points", "inputs": "0,-3,0.4,-2.943,0.8,-2.752,1.2,-2.353,1.6,-1.572,2,0", "expect": "displacement = -4.448", "full": true}
{"paper": "73571-jun24", "q": "16", "module": "casui:Calculate", "tool": "Calculate", "inputs": "2*4.448*150", "expect": "1334.4", "deg": false}
{"paper": "73571-jun24", "q": "17ci", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "ln(x),abs(x)+1,?", "expect": "ln(|x|+1)"}
{"paper": "73571-jun24", "q": "18b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "(4x+1)sqrt(2x+1)", "expect": "1322/15", "ask": "0,4", "deg": false}
{"paper": "73571-jun24", "q": "19", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "y^3*e^(2x)+2y-16x,?,?", "expect": "(-2*e^(2*x)*y^3+16)/(3*e^(2*x)*y^2+2)"}
{"paper": "73571-jun24", "q": "19", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "2x^3-16=0", "expect": "2", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "19", "module": "casui:Calculate", "tool": "Calculate", "inputs": "2^3+2*2", "expect": "12", "deg": false}
{"paper": "73571-jun24", "q": "20a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1.5/125", "expect": "0.012", "deg": false}
{"paper": "73571-jun24", "q": "20b", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "-0.012,y-5,0,130", "expect": "ln(|y-5|) = -3*x/250 + 4.83"}
{"paper": "73571-jun24", "q": "20c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5+125e^(-0.012x)=65", "expect": "-250*ln(12/25)/3", "ask": null, "deg": false}
{"paper": "73571-jun24", "q": "20c", "module": "mpure:F", "tool": "Solve a^x = b", "inputs": "e^(-0.012),60/125", "expect": "x = 61.16", "full": true}
{"paper": "73571-jun25", "q": "1", "module": "casui:CAS", "tool": "d/dx", "inputs": "3e^x", "expect": "3*e^(x)", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "4", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-8,1/2", "expect": "x^1: -4"}
{"paper": "73571-jun25", "q": "4", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-8,1/2", "expect": "x^2: -8"}
{"paper": "73571-jun25", "q": "4", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-8,1/2", "expect": "valid for |x| < 1/8"}
{"paper": "73571-jun25", "q": "5", "module": "casui:CAS", "tool": "integrate", "inputs": "4x-3+x^(-1/2)", "expect": "2*x^2+2*sqrt(x)-3*x", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "6", "module": "mpure:D", "tool": "Arithmetic a,d,n", "inputs": "3,-0.5,250", "expect": "S(250) = -29625/2"}
{"paper": "73571-jun25", "q": "8", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "(4+sin(5x)-3cos(2x))/(1+2tan(x))", "expect": "3*x+1", "ask": "2", "deg": false}
{"paper": "73571-jun25", "q": "9a", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "300,0.2,5", "expect": "9372/25"}
{"paper": "73571-jun25", "q": "9bii", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x-x^2", "expect": "max at (1/2, 1/4)"}
{"paper": "73571-jun25", "q": "9biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "60/(1/4)", "expect": "240", "deg": false}
{"paper": "73571-jun25", "q": "10bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "e^3.676", "expect": "39.5", "deg": false}
{"paper": "73571-jun25", "q": "10bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "3.676/19.98", "expect": "0.184", "deg": false}
{"paper": "73571-jun25", "q": "10biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "21-e^3.676", "expect": "-18.5", "deg": false}
{"paper": "73571-jun25", "q": "10c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "21-39.5e^(-0.184x)=4", "expect": "-125*ln(34/79)/23", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "10c", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "21-39.5e^(-0.184x),4", "expect": "4.58"}
{"paper": "73571-jun25", "q": "11a", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "x^2*y+4y^3-8x", "expect": "dy/dx = 0 at (2sqrt(2), sqrt(2))"}
{"paper": "73571-jun25", "q": "11a", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "x^2*y+4y^3-8x", "expect": "dy/dx = 0 at (-2sqrt(2), -sqrt(2))"}
{"paper": "73571-jun25", "q": "12a", "module": "mpure:B", "tool": "Range of f on [a,b]", "inputs": "x^2+5,-100,100", "expect": "5 <= f(x)"}
{"paper": "73571-jun25", "q": "12dii", "module": "mpure:B", "tool": "Range of f on [a,b]", "inputs": "sqrt(x^2+5),-100,100", "expect": "sqrt(5) <= f(x)"}
{"paper": "73571-jun25", "q": "12di", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "sqrt(x),x^2+5,?", "expect": "sqrt(x^2+5)"}
{"paper": "73571-jun25", "q": "13a", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "4(4t+1)^2,e^(-4t),0", "expect": "-1/8"}
{"paper": "73571-jun25", "q": "13b", "module": "mpure:C", "tool": "Param point at t", "inputs": "4(4t+1)^2,e^(-4t),0", "expect": "y = -(1/8)x + 3/2"}
{"paper": "73571-jun25", "q": "13c", "module": "mpure:C", "tool": "Param to Cartesian", "inputs": "4(4t+1)^2,e^(-4t)", "expect": "y = e^(-(sqrt(x/4)-1))"}
{"paper": "73571-jun25", "q": "14", "module": "mcalc:H", "tool": "Area under curve", "inputs": "4x*sin(2x),0,pi", "expect": "area = 4pi"}
{"paper": "73571-jun25", "q": "14", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "4x*sin(2x)", "expect": "pi", "ask": "0,pi/2", "deg": false}
{"paper": "73571-jun25", "q": "14", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "4x*sin(2x)", "expect": "-3*pi", "ask": "pi/2,pi", "deg": false}
{"paper": "73571-jun25", "q": "15a", "module": "casui:CAS", "tool": "d/dx", "inputs": "(x-3)^2+(x^2-2.5)^2", "expect": "4*x*(x^2-5/2)+2*(x-3)", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "15b", "module": "casui:CAS", "tool": "simplify", "inputs": "x-(2x^3-4x-3)/(6x^2-4)", "expect": "(2*x^3+3/2)/(3*x^2-2)", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "15c", "module": "mcalc:I", "tool": "Newton-Raphson", "inputs": "2x^3-4x-3,3,3", "expect": "x3 = 1.709452"}
{"paper": "73571-jun25", "q": "15d", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "1.709,1.709^2,0,3,2.5,0", "expect": "1.36"}
{"paper": "73571-jun25", "q": "16bi", "module": "casui:CAS", "tool": "expand trig / log", "inputs": "sin(2pi/3-x)/sin(x)", "expect": "-(-cot(x)*sqrt(3)/2-1/2)", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "16bii", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "(sqrt(3)/tan(x)+1)/2-(sqrt(3)+1)/2,0,2pi/3", "expect": "pi/4"}
{"paper": "73571-jun25", "q": "17a", "module": "casui:CAS", "tool": "integrate", "inputs": "e^(2x)/(e^x+1)", "expect": "e^(x)-ln(|e^(x)+1|)", "ask": null, "deg": false}
{"paper": "73571-jun25", "q": "17b", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "e^(2x)/(e^x+1),cos(y)^2,0,pi", "expect": "tan(y) = e^(x)-ln(|e^(x)+1|) - 0.307"}
{"paper": "73571-nov20", "q": "1", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "9,2,1/2", "expect": "x^0: 3"}
{"paper": "73571-nov20", "q": "1", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "9,2,1/2", "expect": "x^1: 1/3"}
{"paper": "73571-nov20", "q": "1", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "9,2,1/2", "expect": "valid for |x| < 9/2"}
{"paper": "73571-nov20", "q": "2", "module": "mcalc:I", "tool": "Sign change table", "inputs": "1/x,-1,1,4", "expect": "f breaks between: not a root"}
{"paper": "73571-nov20", "q": "3", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "2*2+2x=6", "expect": "x = 1", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "4b", "module": "mpure:B", "tool": "Inequality f(x) > g(x)", "inputs": "4-abs(2x-6),2", "expect": "2 < x < 4"}
{"paper": "73571-nov20", "q": "5", "module": "mpure:A", "tool": "Counterexample f>0", "inputs": "2^(n+2)-3^n,0,3", "expect": "no counterexample"}
{"paper": "73571-nov20", "q": "7ai", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "3-u^2,2,3", "expect": "u(3) = 2"}
{"paper": "73571-nov20", "q": "7ai", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "3-u^2,2,3", "expect": "periodic, period 2"}
{"paper": "73571-nov20", "q": "7b", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "3-u^2,-2,3", "expect": "u(2) = -1"}
{"paper": "73571-nov20", "q": "7b", "module": "mpure:D", "tool": "Recurrence u(n+1)", "inputs": "3-u^2,-2,3", "expect": "u(3) = 2"}
{"paper": "73571-nov20", "q": "8a", "module": "mpure:B", "tool": "Range of f on [a,b]", "inputs": "3.87sin(2pi(x+101.75)/365)+11.7,0,365", "expect": "7.83"}
{"paper": "73571-nov20", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "3.87sin(2pi(x+101.75)/365)+11.7-14,0,500", "expect": "x = 300.220275", "full": true}
{"paper": "73571-nov20", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "3.87sin(2pi(x+101.75)/365)+11.7-14,0,500", "expect": "x = 408.779725", "full": true}
{"paper": "73571-nov20", "q": "9ai", "module": "mpure:A", "tool": "Counterexample f=g", "inputs": "(2n^2+n)/((n+1)(n+2)^2),1/(n+1)-6/(n+2)^2,0,3", "expect": "counterexample"}
{"paper": "73571-nov20", "q": "9b", "module": "mpure:B", "tool": "Partial fractions", "inputs": "2x^2+x,(x+1)(x+2)^2", "expect": "1/(x+1)+1/(x+2)+(-6)/(x+2)^2"}
{"paper": "73571-nov20", "q": "10a", "module": "mpure:D", "tool": "Sigma sum f(r) a..b", "inputs": "4r+1,5,20", "expect": "16 terms"}
{"paper": "73571-nov20", "q": "10a", "module": "mpure:D", "tool": "Sigma sum f(r) a..b", "inputs": "4r+1,5,20", "expect": "21, 25"}
{"paper": "73571-nov20", "q": "10bi", "module": "casui:CAS", "tool": "expand", "inputs": "91/2*(2*(10b+c)+90b)", "expect": "5005*b", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "10bii", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "55,1,85,5,-3,0", "expect": "x = 3/2"}
{"paper": "73571-nov20", "q": "10bii", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "55,1,85,5,-3,0", "expect": "y = 5/2"}
{"paper": "73571-nov20", "q": "11a", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "ln(8-x),1,6,1", "expect": "6.5976"}
{"paper": "73571-nov20", "q": "11b", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "ln(8-x),1,6,5", "expect": "7.2056"}
{"paper": "73571-nov20", "q": "11b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "4*7.205633*0.2*10.5", "expect": "60.5", "deg": false}
{"paper": "73571-nov20", "q": "12a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(sqrt(3)^3*sin(pi/6)+cos(pi/6))/sqrt(3)", "expect": "2", "deg": false}
{"paper": "73571-nov20", "q": "12bi", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "x^3*sin(y)+cos(y)-2x,?,?", "expect": ""}
{"paper": "73571-nov20", "q": "12bii", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "x^3*sin(y)+cos(y)-2x,sqrt(3),pi/6", "expect": "-5/8"}
{"paper": "73571-nov20", "q": "12biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "sqrt(3)+(pi/6)*8/5", "expect": "sqrt(3)+4*pi/15", "deg": false}
{"paper": "73571-nov20", "q": "13ai", "module": "casui:CAS", "tool": "rearrange for x", "inputs": "(2x+3)/(x-2)", "expect": "(2*y+3)/(y-2)", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "13aii", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "(2x+3)/(x-2),(2x+3)/(x-2),?", "expect": "x"}
{"paper": "73571-nov20", "q": "13bi", "module": "mpure:B", "tool": "Range of f on [a,b]", "inputs": "(2x^2-5x)/2,0,4", "expect": "-25/16"}
{"paper": "73571-nov20", "q": "13bi", "module": "mpure:B", "tool": "Range of f on [a,b]", "inputs": "(2x^2-5x)/2,0,4", "expect": "6"}
{"paper": "73571-nov20", "q": "13bii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(2x^2-5x)/2=0", "expect": "x = 0", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "13bii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(2x^2-5x)/2=0", "expect": "x = 5/2", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "13c", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "(2x+3)/(x-2),(2x^2-5x)/2,?", "expect": "(-x^2+29*x/2+24)/(x-2)^2"}
{"paper": "73571-nov20", "q": "13c", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "(2x+3)/(x-2),(2x^2-5x)/2,?", "expect": "(4*x^2-10*x+6)/(2*x^2-5*x-4)"}
{"paper": "73571-nov20", "q": "13d", "module": "mpure:B", "tool": "Quadratic", "inputs": "2,-5,-4", "expect": "sqrt(57)"}
{"paper": "73571-nov20", "q": "14a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "3^x*sqrt(x)-1,0,1,1", "expect": "-1"}
{"paper": "73571-nov20", "q": "14a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "3^x*sqrt(x)-1,0,1,1", "expect": "2"}
{"paper": "73571-nov20", "q": "14bi", "module": "casui:CAS", "tool": "d/dx", "inputs": "3^x*sqrt(x)-1", "expect": "3^x*ln(3)*sqrt(x)+3^x/(2*sqrt(x))", "ask": null, "deg": false}
{"paper": "73571-nov20", "q": "14bii", "module": "mcalc:I", "tool": "Newton-Raphson", "inputs": "3^x*sqrt(x)-1,1,2", "expect": "x2 = 0.42465361"}
{"paper": "73571-nov21", "q": "1", "module": "mpure:B", "tool": "Inequality f(x) > g(x)", "inputs": "(x-3)(2x+7),0", "expect": "x < -7/2 or x > 3"}
{"paper": "73571-nov21", "q": "2", "module": "casui:CAS", "tool": "d/dx", "inputs": "ln(5x)", "expect": "1/x", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "5a", "module": "mpure:C", "tool": "Perpendicular thru pt", "inputs": "4/3,15,2", "expect": "53/4"}
{"paper": "73571-nov21", "q": "6a", "module": "mpure:D", "tool": "AP from term and sum", "inputs": "9,3,21,42", "expect": "a = 7"}
{"paper": "73571-nov21", "q": "6a", "module": "mpure:D", "tool": "AP from term and sum", "inputs": "9,3,21,42", "expect": "d = -1/2"}
{"paper": "73571-nov21", "q": "6a", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,8,3,1,10,2", "expect": "x = 7"}
{"paper": "73571-nov21", "q": "6a", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,8,3,1,10,2", "expect": "y = -1/2"}
{"paper": "73571-nov21", "q": "6b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "x/2*(14-0.5(x-1))=x/2*(-36+0.75(x-1))", "expect": "41", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "7a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x^3-x^2+x-3,1.5,1.6,1", "expect": "-0.375"}
{"paper": "73571-nov21", "q": "7a", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x^3-x^2+x-3,1.5,1.6,1", "expect": "0.136"}
{"paper": "73571-nov21", "q": "7c", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "sqrt(x-1+3/x),1.5,3", "expect": "x1 = 1.5811388"}
{"paper": "73571-nov21", "q": "7c", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "sqrt(x-1+3/x),1.5,3", "expect": "x2 = 1.574327"}
{"paper": "73571-nov21", "q": "7c", "module": "mcalc:I", "tool": "Fixed point x=g(x)", "inputs": "sqrt(x-1+3/x),1.5,3", "expect": "x3 = 1.5747708"}
{"paper": "73571-nov21", "q": "7d", "module": "mcalc:I", "tool": "Sign change table", "inputs": "x^3-x^2+x-3,1.574,1.575,1", "expect": "sign change"}
{"paper": "73571-nov21", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(x)^2+sin(2x)-8,0,2pi", "expect": "1.11"}
{"paper": "73571-nov21", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(x)^2+sin(2x)-8,0,2pi", "expect": "1.82"}
{"paper": "73571-nov21", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(x)^2+sin(2x)-8,0,2pi", "expect": "4.25"}
{"paper": "73571-nov21", "q": "8b", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(x)^2+sin(2x)-8,0,2pi", "expect": "4.96"}
{"paper": "73571-nov21", "q": "8c", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(2x-pi/4)^2+sin(4x-pi/2)-8,0,pi/2", "expect": "0.946"}
{"paper": "73571-nov21", "q": "8c", "module": "mpure:E", "tool": "Solve trig eqn (rad)", "inputs": "9sin(2x-pi/4)^2+sin(4x-pi/2)-8,0,pi/2", "expect": "1.3"}
{"paper": "73571-nov21", "q": "9bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "log(156)", "expect": "2.19", "deg": false}
{"paper": "73571-nov21", "q": "9bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "log(260)", "expect": "2.41", "deg": false}
{"paper": "73571-nov21", "q": "9ci", "module": "mpure:F", "tool": "Log-lin fit y=kb^x", "inputs": "0,75,5,94,10,120,15,156,20,206,25,260", "expect": "73.718381*1.051764^x"}
{"paper": "73571-nov21", "q": "9ci", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(2.41-1.88)/25", "expect": "0.0212", "deg": false}
{"paper": "73571-nov21", "q": "9cii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10^1.88", "expect": "75.9", "deg": false}
{"paper": "73571-nov21", "q": "9d", "module": "casui:Calculate", "tool": "Calculate", "inputs": "75*10^(0.02*50)", "expect": "750", "deg": false}
{"paper": "73571-nov21", "q": "9e", "module": "mpure:F", "tool": "Solve a^x = b", "inputs": "10^0.02,8000/75", "expect": "101"}
{"paper": "73571-nov21", "q": "10a", "module": "casui:CAS", "tool": "d/dx", "inputs": "sin(x)/cos(x)", "expect": "sec(x)^2", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "10b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "1-tan(x)^2", "expect": "pi-2", "ask": "-pi/4,pi/4", "deg": false}
{"paper": "73571-nov21", "q": "11", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "x^2/6,y^2,1,6", "expect": "-1/y = x^3/18 - 2/9"}
{"paper": "73571-nov21", "q": "11", "module": "casui:CAS", "tool": "evaluate at x", "inputs": "-1/(x^3/18-2/9)", "expect": "f(0) = 9/2", "ask": "0", "deg": false}
{"paper": "73571-nov21", "q": "12a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(x+0)^2=2x+8", "expect": "x = -2", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "12a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(x+0)^2=2x+8", "expect": "x = 4", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "12a", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "(x+y)^2-4y-2x-8,4,0", "expect": "-3/2"}
{"paper": "73571-nov21", "q": "12b", "module": "mpure:C", "tool": "Perpendicular thru pt", "inputs": "-3/2,4,0", "expect": "2x - 3y"}
{"paper": "73571-nov21", "q": "13b", "module": "mpure:B", "tool": "Factorise", "inputs": "125x^3+150x^2+55x+6", "expect": "(5*x+1)*(5*x+2)*(5*x+3)"}
{"paper": "73571-nov21", "q": "13c", "module": "mpure:A", "tool": "Counterexample d|f(n)", "inputs": "250n^3+300n^2+110n+12,12,1,100", "expect": "no counterexample"}
{"paper": "73571-nov21", "q": "14a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "4x^2-x^3=0", "expect": "0", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "14a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "4x^2-x^3=0", "expect": "4", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "14a", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "t^2+t,4t^2-t^3,4", "expect": "-16/9"}
{"paper": "73571-nov21", "q": "14bi", "module": "mpure:C", "tool": "Param point at t", "inputs": "t^2+t,4t^2-t^3,4", "expect": "(20, 0)"}
{"paper": "73571-nov21", "q": "14bii", "module": "casui:CAS", "tool": "expand", "inputs": "(4x^2-x^3)(2x+1)", "expect": "-2*x^4+7*x^3+4*x^2", "ask": null, "deg": false}
{"paper": "73571-nov21", "q": "14biii", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "4x^2+7x^3-2x^4", "expect": "1856/15", "ask": "0,4", "deg": false}
{"paper": "73571-nov21", "q": "15a", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "sin(x)-sin(x)*cos(2x)", "expect": "2*x^3", "ask": "4", "deg": false}
{"paper": "73571-nov21", "q": "15b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "sqrt(16x^3)", "expect": "integral = 0.05", "ask": "0,0.25", "deg": false}
{"paper": "73572-jun18", "q": "2", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "1,2,7", "expect": "84"}
{"paper": "73572-jun18", "q": "3", "module": "mcalc:H", "tool": "Area under curve", "inputs": "x^3,-2,4", "expect": "68"}
{"paper": "73572-jun18", "q": "4b", "module": "mpure:B", "tool": "Discriminant in k", "inputs": "1,-6,k", "expect": "k < 9"}
{"paper": "73572-jun18", "q": "6", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "(x+y-2)^2-e^y+1", "expect": "(2, 0)"}
{"paper": "73572-jun18", "q": "7", "module": "mcalc:H", "tool": "Integration by parts", "inputs": "x-1,e^x", "expect": "e^(x)*(x-1)-e^(x)+c"}
{"paper": "73572-jun18", "q": "8a", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "sqrt(3),-3", "expect": "R = 2sqrt(3)"}
{"paper": "73572-jun18", "q": "8a", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "sqrt(3),-3", "expect": "al = -60 deg"}
{"paper": "73572-jun18", "q": "9a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "72*336/(8-2)", "expect": "4032", "deg": false}
{"paper": "73572-jun18", "q": "9b", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "4032(8-x),1/y,2,336", "expect": "y^2/2 = 4032*(-x^2/2+8*x)"}
{"paper": "73572-jun18", "q": "9b", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "4032(8-x),1/y,2,336", "expect": "c = 56448 - 56448 = 0"}
{"paper": "73572-jun18", "q": "9ci", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "168(8-x)=sqrt(4032x(16-x))", "expect": "x = -2*sqrt(2)+8", "ask": null, "deg": false}
{"paper": "73572-jun18", "q": "9ci", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,-16,56", "expect": "5.17"}
{"paper": "73572-jun18", "q": "10", "module": "mmech:Q", "tool": "SUVAT", "inputs": "0,0.0128,?,?,1.8", "expect": "0.00711"}
{"paper": "73572-jun18", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "4*0.6/1.5", "expect": "1.6", "deg": false}
{"paper": "73572-jun18", "q": "12a", "module": "mmech:Q", "tool": "v-t graph points", "inputs": "0,0,4,-2,6,2,11,2,12,0,13,-4,16,-4,20,0", "expect": "seg 5: a = -4"}
{"paper": "73572-jun18", "q": "13a", "module": "mmech:R", "tool": "Friction horizontal", "inputs": "20,0.85,150,0,9.8", "expect": "does not move", "full": true}
{"paper": "73572-jun18", "q": "13a", "module": "mmech:R", "tool": "Friction horizontal", "inputs": "20,0.85,150,0,9.8", "expect": "F max = mu R = 166.6", "full": true}
{"paper": "73572-jun18", "q": "13b", "module": "mmech:R", "tool": "Friction horizontal", "inputs": "20,0.85,150,15,9.8", "expect": "it moves", "full": true}
{"paper": "73572-jun18", "q": "13b", "module": "mmech:R", "tool": "Friction horizontal", "inputs": "20,0.85,150,15,9.8", "expect": "F max = mu R = 133.6", "full": true}
{"paper": "73572-jun18", "q": "14a", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "3,5,1,-1,2,7", "expect": "sqrt(61)"}
{"paper": "73572-jun18", "q": "14b", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "4,10,0,0,7,6", "expect": "AB = (-4, -3, 6)"}
{"paper": "73572-jun18", "q": "14b", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "3,5,1,4,10,0", "expect": "|AB| = 3sqrt(3)"}
{"paper": "73572-jun18", "q": "15a", "module": "mmech:Q", "tool": "a(t) to v and s", "inputs": "0.138t^2,0,0,?", "expect": "s = 23*t^4/2000"}
{"paper": "73572-jun18", "q": "15a", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "0.0115x^4,100", "expect": "(9.656628", "full": true}
{"paper": "73572-jun18", "q": "15b", "module": "mmech:Q", "tool": "a(t) to v and s", "inputs": "0.024t^3,0,0,?", "expect": "s = 3*t^5/2500"}
{"paper": "73572-jun18", "q": "15b", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "0.0012x^5,100", "expect": "(9.64", "full": true}
{"paper": "73572-jun18", "q": "16b", "module": "mmech:Q", "tool": "Projectile launch", "inputs": "25.65,35,10,9.81", "expect": "3.57"}
{"paper": "73572-jun18", "q": "17ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "300-140-482*0.2", "expect": "63.6", "deg": false}
{"paper": "73572-jun18", "q": "17aii", "module": "mmech:R", "tool": "Tow bar in a line", "inputs": "410,72,300,140,63.6", "expect": "78"}
{"paper": "73572-jun18", "q": "17ci", "module": "mmech:R", "tool": "Newton II F = ma", "inputs": "-63.6,72,?", "expect": "-0.883"}
{"paper": "73572-jun18", "q": "17ci", "module": "mmech:Q", "tool": "SUVAT", "inputs": "6,0,-0.88333,?,?", "expect": "20.4"}
{"paper": "73572-jun19", "q": "4", "module": "casui:CAS", "tool": "substitute x = a", "inputs": "x^2+b*x+c", "expect": "-2*b+c+4", "ask": "-2", "deg": false}
{"paper": "73572-jun19", "q": "5", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "x^(-2)*ln(x),1/y,1,2", "expect": "y^2/2 = -ln(x)/x-1/x + 3"}
{"paper": "73572-jun19", "q": "7bi", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^3+3*p*x^2+q", "expect": "6*p*x+3*x^2", "ask": null, "deg": false}
{"paper": "73572-jun19", "q": "7bii", "module": "casui:CAS", "tool": "substitute x = a", "inputs": "x^3+3*p*x^2+q", "expect": "4*p^3+q", "ask": "-2*p", "deg": false}
{"paper": "73572-jun19", "q": "8b", "module": "mpure:F", "tool": "y = k b^x from 2 pts", "inputs": "0,10^3.9,40,10^5.28", "expect": "7943.282347*1.08268^x"}
{"paper": "73572-jun19", "q": "8c", "module": "mpure:F", "tool": "Solve a^x = b", "inputs": "1.08,500000/7940", "expect": "53.8"}
{"paper": "73572-jun19", "q": "9a", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "sqrt(4-2x^2)", "expect": "-x^2/2+2", "ask": "3", "deg": false}
{"paper": "73572-jun19", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "600/0.6", "expect": "1000", "deg": false}
{"paper": "73572-jun19", "q": "13b", "module": "mmech:Q", "tool": "SUVAT", "inputs": "0,?,9.8,18,?", "expect": "18.8"}
{"paper": "73572-jun19", "q": "15b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "850/50", "expect": "17", "deg": false}
{"paper": "73572-jun19", "q": "16a", "module": "mcalc:G", "tool": "Stationary points", "inputs": "11.71-11.68e^(-0.9x)-0.03e^(0.3x)", "expect": "max at (5.885873469, 11.47615898)", "full": true}
{"paper": "73572-jun19", "q": "16b", "module": "mmech:Q", "tool": "v(t) to s and a", "inputs": "11.71-11.68e^(-0.9t)-0.03e^(0.3t),0,9.8", "expect": "s = 584*e^(-9*t/10)/45+1171*t/100-e^(3*t/10)/10-1159/90"}
{"paper": "73572-jun19", "q": "16b", "module": "mmech:Q", "tool": "v(t) to s and a", "inputs": "11.71-11.68e^(-0.9t)-0.03e^(0.3t),0,9.8", "expect": "s(9.8) = 100 m"}
{"paper": "73572-jun22", "q": "1", "module": "mpure:C", "tool": "Circle centre+radius", "inputs": "4,-5,6", "expect": "(x - 4)^2 + (y + 5)^2 = 36"}
{"paper": "73572-jun22", "q": "2", "module": "casui:CAS", "tool": "limit x -> a", "inputs": "(sin(pi+x)-sin(pi))/x", "expect": "-1", "ask": "0", "deg": false}
{"paper": "73572-jun22", "q": "4", "module": "mpure:E", "tool": "Triangle SSA", "inputs": "6.1,8.7,38", "expect": "ambiguous: B = 119 also works"}
{"paper": "73572-jun22", "q": "5a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "2,5,4", "expect": "x^0: 16"}
{"paper": "73572-jun22", "q": "5a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "2,5,4", "expect": "x^2: 600"}
{"paper": "73572-jun22", "q": "5b", "module": "casui:CAS", "tool": "expand", "inputs": "(2+5x)^4-(2-5x)^4", "expect": "2000*x^3+320*x", "ask": null, "deg": false}
{"paper": "73572-jun22", "q": "5c", "module": "casui:CAS", "tool": "integrate", "inputs": "(2+5x)^4-(2-5x)^4", "expect": "(-5*x+2)^5/25+(5*x+2)^5/25", "ask": null, "deg": false}
{"paper": "73572-jun22", "q": "6c", "module": "mpure:D", "tool": "Terms of u(n)", "inputs": "n^2,0,10", "expect": "u(9) = 81"}
{"paper": "73572-jun22", "q": "7a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "15-x^2=0", "expect": "sqrt(15)", "ask": null, "deg": false}
{"paper": "73572-jun22", "q": "7b", "module": "mcalc:G", "tool": "Stationary points", "inputs": "15x-x^3", "expect": "max at (sqrt(5), 10sqrt(5))"}
{"paper": "73572-jun22", "q": "8b", "module": "mpure:B", "tool": "Transform af(bx+c)+d", "inputs": "1/x^2,1,1/3,0,0", "expect": "9/x^2"}
{"paper": "73572-jun22", "q": "10ai", "module": "mpure:F", "tool": "Compound interest", "inputs": "25,32,5", "expect": "A = 100.187"}
{"paper": "73572-jun22", "q": "10bi", "module": "mpure:B", "tool": "Partial fractions", "inputs": "2700,x(900-x)", "expect": "3/x+(-3)/(x-900)"}
{"paper": "73572-jun22", "q": "10bii", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "1/2700,y*(900-y),0,25", "expect": "ln(|y|)/900-ln(|y-900|)/900 = x/2700 - 0.00395"}
{"paper": "73572-jun22", "q": "10biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "3*ln(35*450/(900-450))", "expect": "10.666", "deg": false}
{"paper": "73572-jun22", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "345/212", "expect": "1.63", "deg": false}
{"paper": "73572-jun22", "q": "13b", "module": "mmech:Q", "tool": "Projectile launch", "inputs": "7,60,0,9.8", "expect": "max height = 1.875", "full": true}
{"paper": "73572-jun22", "q": "14a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "12*66/80", "expect": "9.9", "deg": false}
{"paper": "73572-jun22", "q": "15", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "2x+7=2(10-x)+20", "expect": "33/4", "ask": null, "deg": false}
{"paper": "73572-jun22", "q": "16a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "9/3=(x+1)/(-4)", "expect": "-13", "ask": null, "deg": false}
{"paper": "73572-jun22", "q": "16bii", "module": "mcalc:J", "tool": "Parallel test", "inputs": "5,-6,0,3,-4,0", "expect": "not parallel"}
{"paper": "73572-jun22", "q": "17", "module": "mmech:Q", "tool": "Vector r(t) to v, a", "inputs": "e^t*cos(t),e^t*sin(t),?", "expect": "a = (-2*e^(t)*sin(t))i + (2*cos(t)*e^(t))j"}
{"paper": "73572-jun22", "q": "18a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "asin(0.6/0.8)", "expect": "48.59", "deg": true}
{"paper": "73572-jun22", "q": "18a", "module": "mmech:R", "tool": "Two unknown forces", "inputs": "131.40962,30,1,270", "expect": "P = 0.883 N"}
{"paper": "73572-jun22", "q": "18a", "module": "mmech:R", "tool": "Two unknown forces", "inputs": "131.40962,30,1,270", "expect": "Q = 0.675 N"}
{"paper": "73572-jun22", "q": "18b", "module": "mmech:R", "tool": "Two unknown forces", "inputs": "131.40962,270,19.6,30", "expect": "Q = 29 N"}
{"paper": "73572-jun22", "q": "19a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(230-196*sin(25)-20*1.2)/(196*cos(25))", "expect": "0.69", "deg": true}
{"paper": "73572-jun22", "q": "19bi", "module": "mmech:Q", "tool": "SUVAT", "inputs": "0,?,1.2,?,3.8", "expect": "8.66"}
{"paper": "73572-jun22", "q": "19bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10-8.664", "expect": "1.336", "deg": false}
{"paper": "73572-jun23", "q": "4a", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^2/8+4sqrt(x)", "expect": "x/4+2/sqrt(x)", "ask": null, "deg": false}
{"paper": "73572-jun23", "q": "4b", "module": "mcalc:G", "tool": "Tangent and normal", "inputs": "x^2/8+4sqrt(x),4", "expect": "2*x+2"}
{"paper": "73572-jun23", "q": "4c", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x^2/8+4sqrt(x)", "expect": "none in -20 <= x <= 20"}
{"paper": "73572-jun23", "q": "5bi", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "25(10+4(x-1))=3000", "expect": "57/2", "ask": null, "deg": false}
{"paper": "73572-jun23", "q": "5bii", "module": "mpure:D", "tool": "Arithmetic a,d,n", "inputs": "10,4,29", "expect": "1914"}
{"paper": "73572-jun23", "q": "5bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1914*25", "expect": "47850", "deg": false}
{"paper": "73572-jun23", "q": "6ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10^1.76", "expect": "57.5", "deg": false}
{"paper": "73572-jun23", "q": "6aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10^0.057", "expect": "1.14", "deg": false}
{"paper": "73572-jun23", "q": "7a", "module": "mpure:B", "tool": "Composite fg and gf", "inputs": "1/x,sqrt(10-2x),?", "expect": "1/sqrt(-2*x+10)"}
{"paper": "73572-jun23", "q": "7c", "module": "mpure:B", "tool": "Inverse function", "inputs": "1/sqrt(10-2x)", "expect": "(5*x^2-1/2)/x^2"}
{"paper": "73572-jun23", "q": "8a", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "1/(1-cos(x))+1/(1+cos(x)),2/sin(x)^2", "expect": "holds"}
{"paper": "73572-jun23", "q": "8c", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "1/(1-cos(x))+1/(1+cos(x))-16,90,180", "expect": "159"}
{"paper": "73572-jun23", "q": "8c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1/tan(180-asin(1/sqrt(8)))", "expect": "-sqrt(7)", "deg": true}
{"paper": "73572-jun23", "q": "9a", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,1,-1/2", "expect": "x^1: -1/2"}
{"paper": "73572-jun23", "q": "9a", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,1,-1/2", "expect": "x^2: 3/8"}
{"paper": "73572-jun23", "q": "9c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.5*(1+1/8+3/128)", "expect": "0.574", "deg": false}
{"paper": "73572-jun23", "q": "10a", "module": "casui:CAS", "tool": "expand", "inputs": "(a-b)^2", "expect": "a^2-2*a*b+b^2", "ask": null, "deg": false}
{"paper": "73572-jun23", "q": "10b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "-2+1/(-2)", "expect": "-5/2", "deg": false}
{"paper": "73572-jun23", "q": "16", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(5x-5)/12=(1.6+x)/3.2", "expect": "44/5", "ask": null, "deg": false}
{"paper": "73572-jun23", "q": "17a", "module": "mmech:S", "tool": "Beam on two supports", "inputs": "7,9.6,1.4,5,0,0", "expect": "R at 1.4 m = 39.2 N"}
{"paper": "73572-jun23", "q": "17a", "module": "mmech:S", "tool": "Beam on two supports", "inputs": "7,9.6,1.4,5,0,0", "expect": "R at 5 m = 54.9 N"}
{"paper": "73572-jun23", "q": "17b", "module": "mmech:S", "tool": "Beam on two supports", "inputs": "7,9.6,1.4,5.6,0,0", "expect": "R at 5.6 m = 47 N"}
{"paper": "73572-jun23", "q": "18a", "module": "mcalc:J", "tool": "Magnitude and angle", "inputs": "3,sqrt(3),0", "expect": "2sqrt(3)"}
{"paper": "73572-jun23", "q": "18b", "module": "mcalc:J", "tool": "Angle between vectors", "inputs": "-3,-sqrt(3),0,-3,sqrt(3),0", "expect": "60"}
{"paper": "73572-jun23", "q": "18c", "module": "mcalc:J", "tool": "Position r0 + v t", "inputs": "1,0,0,-3,sqrt(3),0,3", "expect": "-8"}
{"paper": "73572-jun23", "q": "19bi", "module": "mmech:R", "tool": "Tow bar in a line", "inputs": "1.5,0.7,0,0.8,0.6", "expect": "a = -0.636"}
{"paper": "73572-jun23", "q": "19bi", "module": "mmech:R", "tool": "Tow bar in a line", "inputs": "1.5,0.7,0,0.8,0.6", "expect": "T = 0.155 N"}
{"paper": "73572-jun23", "q": "19bii", "module": "mmech:Q", "tool": "SUVAT", "inputs": "0.5,0,-7/11,?,?", "expect": "0.196"}
{"paper": "73572-jun23", "q": "20", "module": "mmech:Q", "tool": "Projectile launch", "inputs": "14,60,1.5,9.8", "expect": "2.59"}
{"paper": "73572-jun23", "q": "20", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "0.5*x*(2.592-0.2)^2=18.144", "expect": "567000/89401", "ask": null, "deg": false}
{"paper": "73572-jun23", "q": "20", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "0.5*x*(2.592-0.2)^2,18.144", "expect": "6.34"}
{"paper": "73572-jun24", "q": "3", "module": "mpure:B", "tool": "Quadratic inequality", "inputs": "-1,5,-4", "expect": "x < 1 or x > 4"}
{"paper": "73572-jun24", "q": "5", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^3/sin(x)", "expect": "(-cos(x)*x^3+3*sin(x)*x^2)*cosec(x)^2", "ask": null, "deg": false}
{"paper": "73572-jun24", "q": "6", "module": "casui:CAS", "tool": "expand", "inputs": "(2sin(x)+3cos(x))^2+(6sin(x)-cos(x))^2", "expect": "10*cos(x)^2+40*sin(x)^2", "ask": null, "deg": false}
{"paper": "73572-jun24", "q": "6", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "(2sin(x)+3cos(x))^2+(6sin(x)-cos(x))^2-30,90,180", "expect": "125"}
{"paper": "73572-jun24", "q": "6", "module": "casui:Calculate", "tool": "Calculate", "inputs": "sin(180-asin(sqrt(2/3)))", "expect": "sqrt(6)/3", "deg": true}
{"paper": "73572-jun24", "q": "8a", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,log(3),6.4,1,log(24),12", "expect": "x = 3.44"}
{"paper": "73572-jun24", "q": "8a", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,log(3),6.4,1,log(24),12", "expect": "y = 6.2"}
{"paper": "73572-jun24", "q": "8aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "5.6/log(8)", "expect": "6.2", "deg": false}
{"paper": "73572-jun24", "q": "8b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "3.44+6.2*log(0.25)", "expect": "-0.29", "deg": false}
{"paper": "73572-jun24", "q": "9ai", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,3,-1", "expect": "x^1: -3"}
{"paper": "73572-jun24", "q": "9ai", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,3,-1", "expect": "x^2: 9"}
{"paper": "73572-jun24", "q": "9aii", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "2,-3,-1", "expect": "x^0: 1/2"}
{"paper": "73572-jun24", "q": "9aii", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "2,-3,-1", "expect": "x^1: 3/4"}
{"paper": "73572-jun24", "q": "9aii", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "2,-3,-1", "expect": "x^2: 9/8"}
{"paper": "73572-jun24", "q": "10", "module": "mcalc:G", "tool": "Inflection points", "inputs": "x^2+2cos(x)", "expect": "no inflection point"}
{"paper": "73572-jun24", "q": "12", "module": "mmech:R", "tool": "Newton II F = ma", "inputs": "6,2,?", "expect": "a = 3"}
{"paper": "73572-jun24", "q": "14a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "6*4-2*4^2", "expect": "-8", "deg": false}
{"paper": "73572-jun24", "q": "14b", "module": "mpure:B", "tool": "Quadratic inequality", "inputs": "-2,6,0", "expect": "0 < x < 3"}
{"paper": "73572-jun24", "q": "15", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,-12,-4,-3,1,-23", "expect": "x = 8"}
{"paper": "73572-jun24", "q": "15", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "1,-12,-4,-3,1,-23", "expect": "y = 1"}
{"paper": "73572-jun24", "q": "16", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.5*9.8*(0.6^2-0.5^2)", "expect": "0.539", "deg": false}
{"paper": "73572-jun24", "q": "18b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "5+81.99", "expect": "87", "deg": false}
{"paper": "73572-jun24", "q": "19ai", "module": "mmech:Q", "tool": "Vertical under gravity", "inputs": "7,?,9.8", "expect": "max height = 2.5"}
{"paper": "73572-jun24", "q": "19b", "module": "mmech:Q", "tool": "Projectile launch", "inputs": "7,79,0,9.8", "expect": "2.41"}
{"paper": "73572-jun24", "q": "20a", "module": "mcalc:J", "tool": "Parallel test", "inputs": "3,4,0,9,12,0", "expect": "parallel"}
{"paper": "73572-jun24", "q": "20c", "module": "mpure:E", "tool": "Triangle SSS", "inputs": "12,5,13", "expect": "90"}
{"paper": "73572-jun24", "q": "21c", "module": "mmech:R", "tool": "Slope and pulley", "inputs": "50,60,1,80,9.8", "expect": "a = 0.882"}
{"paper": "73572-jun24", "q": "21c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(11-5sqrt(3))*9.8/26", "expect": "0.88", "deg": false}
{"paper": "73572-jun25", "q": "3", "module": "mpure:B", "tool": "Quadratic inequality", "inputs": "1,-5,-14", "expect": "x < -2 or x > 7"}
{"paper": "73572-jun25", "q": "4", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "5^(x-1)=20", "expect": "x = ln(100)/ln(5)", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "5", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "8,1.4", "expect": "224/5"}
{"paper": "73572-jun25", "q": "6ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "e^3.2/3.4", "expect": "7.215450058", "deg": false}
{"paper": "73572-jun25", "q": "6a", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "e^(x/2)/(x-3),4,8,5", "expect": "T = 30.026008"}
{"paper": "73572-jun25", "q": "6a", "module": "mcalc:I", "tool": "Trapezium rule", "inputs": "e^(x/2)/(x-3),4,8,5", "expect": "convex: T is an over-estimate"}
{"paper": "73572-jun25", "q": "7a", "module": "casui:CAS", "tool": "substitute x = a", "inputs": "x^3+p*x^2+q*x+12-37", "expect": "25*p-5*q-150", "ask": "-5", "deg": false}
{"paper": "73572-jun25", "q": "7b", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^3+p*x^2+q*x+12", "expect": "2*p*x+3*x^2+q", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "7c", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "5,-1,30,10,-1,75", "expect": "x = 9"}
{"paper": "73572-jun25", "q": "7c", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "5,-1,30,10,-1,75", "expect": "y = 15"}
{"paper": "73572-jun25", "q": "7d", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x^3+9x^2+15x+12", "expect": "(-1, 5)"}
{"paper": "73572-jun25", "q": "7d", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x^3+9x^2+15x+12", "expect": "(-5, 37)"}
{"paper": "73572-jun25", "q": "8b", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "(3/cos(x)+5tan(x))(5/cos(x)-3tan(x))-16tan(x)/cos(x),15", "expect": "holds"}
{"paper": "73572-jun25", "q": "9c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(x-12)^2+64=100", "expect": "6", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "9c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(x-12)^2+64=100", "expect": "18", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "9di", "module": "mpure:C", "tool": "Triangle 3 vertices", "inputs": "6,10,12,-8,18,10", "expect": "B = 36.9"}
{"paper": "73572-jun25", "q": "9di", "module": "casui:Calculate", "tool": "Calculate", "inputs": "2*atan(1/3)", "expect": "0.6435", "deg": false}
{"paper": "73572-jun25", "q": "9dii", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "10,2*0.6435", "expect": "12.9"}
{"paper": "73572-jun25", "q": "10a", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^k*ln(x)", "expect": "k*ln(x)*x^(k-1)+x^(k-1)", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "10b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "1+k*ln(x)=0", "expect": "x = e^(-1/k)", "ask": null, "deg": false}
{"paper": "73572-jun25", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "40/125", "expect": "0.32", "deg": false}
{"paper": "73572-jun25", "q": "13a", "module": "mmech:Q", "tool": "SUVAT", "inputs": "?,30,2,225,?", "expect": "u = 0"}
{"paper": "73572-jun25", "q": "15a", "module": "mmech:R", "tool": "Resultant of forces", "inputs": "17,0,26,140", "expect": "R = 17 N"}
{"paper": "73572-jun25", "q": "15a", "module": "mmech:R", "tool": "Resultant of forces", "inputs": "17,0,26,140", "expect": "direction = 99.9 deg"}
{"paper": "73572-jun25", "q": "17a", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "-3,5,1,5,4,-2", "expect": "(8, -1, -3)"}
{"paper": "73572-jun25", "q": "17a", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "-3,5,1,5,4,-2", "expect": "sqrt(74)"}
{"paper": "73572-jun25", "q": "17b", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "5,4,-2,1,-1,0", "expect": "3sqrt(5)"}
{"paper": "73572-jun25", "q": "17b", "module": "mcalc:J", "tool": "Distance A to B", "inputs": "-3,5,1,1,-1,0", "expect": "sqrt(53)"}
{"paper": "73572-jun25", "q": "18a", "module": "mmech:S", "tool": "Beam on two supports", "inputs": "2.5,400/9.81,0,0.6,2.3,30", "expect": "R at 0.6 m = 1960 N"}
{"paper": "73572-jun25", "q": "18a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(2.3*30*9.81+1.25*400)/0.6", "expect": "1961", "deg": false}
{"paper": "73572-nov20", "q": "1", "module": "mcalc:G", "tool": "Increasing/decreasing", "inputs": "-e^(x-1)", "expect": "decreasing for all x"}
{"paper": "73572-nov20", "q": "3", "module": "casui:CAS", "tool": "expand", "inputs": "(2x-3/x)^8", "expect": "-48384*x^2", "ask": null, "deg": false}
{"paper": "73572-nov20", "q": "4", "module": "casui:CAS", "tool": "limit x -> a", "inputs": "x*tan(5x)/(cos(4x)-1)", "expect": "-5/8", "ask": "0", "deg": false}
{"paper": "73572-nov20", "q": "5", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "x*sqrt(4x+1)", "expect": "875/12", "ask": "-1/4,6", "deg": false}
{"paper": "73572-nov20", "q": "6b", "module": "mpure:C", "tool": "Circle centre+radius", "inputs": "7,9,13", "expect": "169"}
{"paper": "73572-nov20", "q": "8a", "module": "mpure:C", "tool": "Param to Cartesian", "inputs": "t^2,2t", "expect": "y = 2*sqrt(x)"}
{"paper": "73572-nov20", "q": "8bi", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "t^2,2t,?", "expect": "1/t"}
{"paper": "73572-nov20", "q": "8biii", "module": "casui:CAS", "tool": "simplify", "inputs": "(2/x)/(1-1/x^2)", "expect": "2*x/((x+1)*(x-1))", "ask": null, "deg": false}
{"paper": "73572-nov20", "q": "11", "module": "mcalc:J", "tool": "Sum and difference", "inputs": "6,-3,0,8,-5,0", "expect": "(-2, 2, 0)"}
{"paper": "73572-nov20", "q": "12", "module": "casui:Calculate", "tool": "Calculate", "inputs": "8/(-12)*9", "expect": "-6", "deg": false}
{"paper": "73572-nov20", "q": "13a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1.5*4/2", "expect": "3", "deg": false}
{"paper": "73572-nov20", "q": "14a", "module": "mmech:Q", "tool": "Vector r(t) to v, a", "inputs": "t^3-5t^2,8t-t^2,2", "expect": "v(2) = (-8, 4) m/s"}
{"paper": "73572-nov20", "q": "14a", "module": "mmech:Q", "tool": "Vector r(t) to v, a", "inputs": "t^3-5t^2,8t-t^2,2", "expect": "speed = 8.94 m/s"}
{"paper": "73572-nov20", "q": "14b", "module": "mmech:Q", "tool": "Vector r(t) to v, a", "inputs": "t^3-5t^2,8t-t^2,?", "expect": "a = (6*t-10)i + (-2)j"}
{"paper": "73572-nov20", "q": "15a", "module": "mmech:Q", "tool": "v-t graph points", "inputs": "20,131,40,140,60,120,80,80,100,0", "expect": "8110"}
{"paper": "73572-nov20", "q": "18a", "module": "mmech:R", "tool": "Slope and pulley", "inputs": "0.2,16.26020471,0.17,2,9.81", "expect": "a = 8.52 m/s^2"}
{"paper": "73572-nov20", "q": "18a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "543/625*9.81", "expect": "8.52", "deg": false}
{"paper": "73572-nov20", "q": "18bi", "module": "mmech:Q", "tool": "SUVAT", "inputs": "0.5,0,-4.347792,?,?", "expect": "0.0288"}
{"paper": "73572-nov20", "q": "19a", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "-0.1,y^2,0,4", "expect": "-1/y = -x/10 - 1/4"}
{"paper": "73572-nov20", "q": "19b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "-0.1*(20/(5+2*5.5))^2", "expect": "-0.15625", "deg": false}
{"paper": "73572-nov21", "q": "3", "module": "mpure:D", "tool": "Recurrence sum to N", "inputs": "-u,1,95", "expect": "sum u(1..95) = 1"}
{"paper": "73572-nov21", "q": "4b", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "abs(3x-6),abs(2x)", "expect": "(6/5, 12/5)"}
{"paper": "73572-nov21", "q": "4b", "module": "mpure:B", "tool": "Solve f(x)=g(x)", "inputs": "abs(3x-6),abs(2x)", "expect": "(6, 12)"}
{"paper": "73572-nov21", "q": "7b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "sqrt(25+x)=4", "expect": "-9", "ask": null, "deg": false}
{"paper": "73572-nov21", "q": "7b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "sqrt(25+x)=5", "expect": "0", "ask": null, "deg": false}
{"paper": "73572-nov21", "q": "9b", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "cos(x)+sin(2x-pi/2),1+cos(x)-2cos(x)^2", "expect": "holds"}
{"paper": "73572-nov21", "q": "9c", "module": "casui:CAS", "tool": "complete the square", "inputs": "1+x-2x^2", "expect": "9/8", "ask": null, "deg": false}
{"paper": "73572-nov21", "q": "9d", "module": "casui:Calculate", "tool": "Calculate", "inputs": "sqrt(1+1-2*1/4)", "expect": "sqrt(6)/2", "deg": false}
{"paper": "73572-nov21", "q": "10b", "module": "mcalc:I", "tool": "Sign change table", "inputs": "sqrt(x)/(x-3),1,4,3", "expect": "not a root"}
{"paper": "73572-nov21", "q": "10c", "module": "mcalc:G", "tool": "Stationary points", "inputs": "sqrt(x)/(x-3)", "expect": "none in -20 <= x <= 20"}
{"paper": "73572-nov21", "q": "11", "module": "casui:CAS", "tool": "d/dx", "inputs": "3e^(0.5x)", "expect": "3*e^(x/2)/2", "ask": null, "deg": false}
{"paper": "73572-nov21", "q": "12", "module": "mcalc:J", "tool": "Components from r,th", "inputs": "6,30", "expect": "v = (3sqrt(3), 3)"}
{"paper": "73572-nov21", "q": "13", "module": "mmech:Q", "tool": "SUVAT", "inputs": "13,17,?,40,?", "expect": "a = 1.5"}
{"paper": "73572-nov21", "q": "13", "module": "mmech:R", "tool": "Newton II F = ma", "inputs": "?,1200,1.5", "expect": "1800"}
{"paper": "73572-nov21", "q": "14", "module": "mmech:Q", "tool": "v-t graph points", "inputs": "12,5.8,18,5.2,25,6.2,30,6,36,3.8", "expect": "displacement = 133 m"}
{"paper": "73572-nov21", "q": "19aii", "module": "mcalc:J", "tool": "Magnitude and angle", "inputs": "2.24,7.68,0", "expect": "8"}
{"paper": "73572-nov21", "q": "19b", "module": "mcalc:J", "tool": "Position r0 + v t", "inputs": "2,-7,0,2.24,7.68,0,4", "expect": "r = (274/25, 593/25, 0)"}
{"paper": "73572-nov21", "q": "19c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "sqrt(5^2-((40-32)/2)^2)", "expect": "3", "deg": false}
{"paper": "73573-jun18", "q": "2", "module": "mcalc:G", "tool": "f, f' and f'' at a", "inputs": "x^5+4x^3+7x+5,0", "expect": "f'(0) = 7"}
{"paper": "73573-jun18", "q": "3", "module": "mpure:C", "tool": "Perpendicular thru pt", "inputs": "-2/3,0,0", "expect": "3/2"}
{"paper": "73573-jun18", "q": "5", "module": "casui:CAS", "tool": "series (Maclaurin)", "inputs": "5+4sin(x/2)+12tan(x/3)", "expect": "6*x+5", "ask": "2", "deg": false}
{"paper": "73573-jun18", "q": "6c", "module": "mcalc:G", "tool": "Inflection points", "inputs": "x/sqrt(2x-2)", "expect": "inflection at (4, 2sqrt(6)/3)"}
{"paper": "73573-jun18", "q": "8a", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "sin(2x)/(1+tan(x)^2),2sin(x)cos(x)^3", "expect": "holds at every x tested"}
{"paper": "73573-jun18", "q": "8b", "module": "casui:CAS", "tool": "integrate", "inputs": "4sin(4x)/(1+tan(2x)^2)", "expect": "-cos(2*x)^4", "ask": null, "deg": false}
{"paper": "73573-jun18", "q": "9b", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "1,1/sqrt(2),10", "expect": "S(inf) = 3.41"}
{"paper": "73573-jun18", "q": "11", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "x+2x+4x+2x+x=1", "expect": "1/10", "ask": null, "deg": false}
{"paper": "73573-jun18", "q": "12", "module": "mstat:L", "tool": "Grouped table", "inputs": "155,160,4,160,170,24,170,180,20,180,190,10", "expect": "median = 170"}
{"paper": "73573-jun18", "q": "14a", "module": "mstat:M", "tool": "Two-way table counts", "inputs": "4,8,4,8", "expect": "independent: yes"}
{"paper": "73573-jun18", "q": "14b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1/5*3/8", "expect": "3/40", "deg": false}
{"paper": "73573-jun18", "q": "14b", "module": "mstat:M", "tool": "Venn: find the ?", "inputs": "1/5,1/6,3/40,?", "expect": "7/24"}
{"paper": "73573-jun18", "q": "15b", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "6,0.15,6", "expect": "1.14"}
{"paper": "73573-jun18", "q": "15c", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "6,0.15,2", "expect": "0.224"}
{"paper": "73573-jun18", "q": "15d", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "6,0.15", "expect": "0.9"}
{"paper": "73573-jun18", "q": "16a", "module": "mstat:L", "tool": "Stats from summary", "inputs": "120,165.6,261.8", "expect": "mean = 1.38"}
{"paper": "73573-jun18", "q": "16a", "module": "mstat:L", "tool": "Stats from summary", "inputs": "120,165.6,261.8", "expect": "0.527"}
{"paper": "73573-jun18", "q": "16bi", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "1.38,0.527,0.5,1.5", "expect": "0.543"}
{"paper": "73573-jun18", "q": "16c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1.38-3*0.527", "expect": "-0.201", "deg": false}
{"paper": "73573-jun18", "q": "16d", "module": "mstat:N", "tool": "Normal find mu or sd", "inputs": "?,0.21,0.75,0.9", "expect": "0.481"}
{"paper": "73573-jun18", "q": "17a", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "10,0.5,7,10", "expect": "do not reject H0 at 10%"}
{"paper": "73573-jun18", "q": "17a", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "10,0.5,7,10", "expect": "P(X >= 7) = 0.172"}
{"paper": "73573-jun18", "q": "17a", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "10,0.5,7,10", "expect": "CR: X <= 1 or X >= 9"}
{"paper": "73573-jun18", "q": "17b", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "20,0.5,14,10", "expect": "CR: X >= 14"}
{"paper": "73573-jun18", "q": "17b", "module": "mstat:N", "tool": "Binomial least k", "inputs": "20,0.5,0.9", "expect": "k = 13"}
{"paper": "73573-jun18", "q": "18b", "module": "mstat:O", "tool": "z test mean lower", "inputs": "66.5,21.2,750,65.4,10", "expect": "reject H0 at 10%"}
{"paper": "73573-jun18", "q": "18b", "module": "mstat:O", "tool": "z test mean lower", "inputs": "66.5,21.2,750,65.4,10", "expect": "z = -1.42"}
{"paper": "73573-jun18", "q": "18b", "module": "mstat:O", "tool": "z test mean lower", "inputs": "66.5,21.2,750,65.4,10", "expect": "critical z = -1.282"}
{"paper": "73573-jun19", "q": "2", "module": "casui:Calculate", "tool": "Calculate", "inputs": "100!/(98!*3!)", "expect": "1650", "deg": false}
{"paper": "73573-jun19", "q": "3", "module": "mpure:D", "tool": "Terms of u(n)", "inputs": "2-0.9^(n-1),1,5", "expect": "increasing"}
{"paper": "73573-jun19", "q": "5", "module": "mpure:C", "tool": "Circle from general", "inputs": "-6,-8,-264", "expect": "(3, 4)"}
{"paper": "73573-jun19", "q": "5", "module": "mpure:C", "tool": "Circle from general", "inputs": "-6,-8,-264", "expect": "17"}
{"paper": "73573-jun19", "q": "5", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "17,0.9", "expect": "16.9"}
{"paper": "73573-jun19", "q": "7a", "module": "mpure:B", "tool": "Partial fractions", "inputs": "4x+3,(x-1)^2", "expect": "4/(x-1)"}
{"paper": "73573-jun19", "q": "7a", "module": "mpure:B", "tool": "Partial fractions", "inputs": "4x+3,(x-1)^2", "expect": "7/(x-1)^2"}
{"paper": "73573-jun19", "q": "7b", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "(4x+3)/(x-1)^2", "expect": "7/6", "ask": "3,4", "deg": false}
{"paper": "73573-jun19", "q": "8bii", "module": "mpure:F", "tool": "Solve a^x = b", "inputs": "e^(-0.068066),1/55", "expect": "x = 58.87", "full": true}
{"paper": "73573-jun19", "q": "9bi", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "x^2*y^2+x*y^4-12,?,?", "expect": "(-y^4-2*x*y^2)/(4*x*y^3+2*x^2*y)"}
{"paper": "73573-jun19", "q": "9bii", "module": "mcalc:G", "tool": "Implicit dy/dx = 0", "inputs": "x^2*y^2+x*y^4-12", "expect": "no point"}
{"paper": "73573-jun19", "q": "9biii", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,1,-12", "expect": "x = 3"}
{"paper": "73573-jun19", "q": "9biii", "module": "mcalc:G", "tool": "Implicit dy/dx", "inputs": "x^2*y^2+x*y^4-12,3,1", "expect": "-7/30"}
{"paper": "73573-jun19", "q": "12a", "module": "mstat:L", "tool": "Outliers", "inputs": "162,169,172,156,146,161,159,164,157,160", "expect": "146"}
{"paper": "73573-jun19", "q": "12b", "module": "mstat:L", "tool": "Summary stats", "inputs": "162,169,172,156,161,159,164,157,160", "expect": "mean = 162.2", "full": true}
{"paper": "73573-jun19", "q": "12b", "module": "mstat:L", "tool": "Summary stats", "inputs": "162,169,172,156,161,159,164,157,160", "expect": "sd (n) = 5.028", "full": true}
{"paper": "73573-jun19", "q": "13a", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "30,0.2", "expect": "mean = np = 6"}
{"paper": "73573-jun19", "q": "13a", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "30,0.2", "expect": "variance = np(1-p) = 4.8"}
{"paper": "73573-jun19", "q": "13bi", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "30,0.2,10", "expect": "0.0355"}
{"paper": "73573-jun19", "q": "13bii", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "30,0.2,5", "expect": "0.745"}
{"paper": "73573-jun19", "q": "13ci", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.7448^5", "expect": "0.229", "deg": false}
{"paper": "73573-jun19", "q": "14ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10/120", "expect": "1/12", "deg": false}
{"paper": "73573-jun19", "q": "14aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "12/120", "expect": "1/10", "deg": false}
{"paper": "73573-jun19", "q": "14aiii", "module": "mstat:M", "tool": "Conditional P(A|B)", "inputs": "38/120,50/120", "expect": "P(A|B) = 0.76"}
{"paper": "73573-jun19", "q": "15", "module": "mstat:O", "tool": "PMCC test 1 tail", "inputs": "0.567,10,5", "expect": "0.549"}
{"paper": "73573-jun19", "q": "15", "module": "mstat:O", "tool": "PMCC test 1 tail", "inputs": "0.567,10,5", "expect": "reject"}
{"paper": "73573-jun19", "q": "16b", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "78.9,25,918,80.4,5", "expect": "1.82"}
{"paper": "73573-jun19", "q": "16b", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "78.9,25,918,80.4,5", "expect": "1.96"}
{"paper": "73573-jun19", "q": "16b", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "78.9,25,918,80.4,5", "expect": "do not reject"}
{"paper": "73573-jun19", "q": "17a", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "30,0.1,32.5,0.2", "expect": "mu = 37.3"}
{"paper": "73573-jun19", "q": "17a", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "30,0.1,32.5,0.2", "expect": "sigma = 5.68"}
{"paper": "73573-jun19", "q": "17bii", "module": "mstat:N", "tool": "Normal P(X<x)", "inputs": "37.3,5.70,35", "expect": "0.34"}
{"paper": "73573-jun19", "q": "17c", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "13,0.344,3", "expect": "0.294"}
{"paper": "73573-jun22", "q": "1", "module": "mpure:D", "tool": "Binomial rational n", "inputs": "1,-1/4,1/2", "expect": "valid for |x| < 4"}
{"paper": "73573-jun22", "q": "2", "module": "casui:CAS", "tool": "simplify", "inputs": "(7-2x)-(x^2-7x+7)", "expect": "-x^2+5*x", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "3", "module": "mpure:B", "tool": "Inverse function", "inputs": "2x+1", "expect": "(x-1)/2"}
{"paper": "73573-jun22", "q": "3", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "2x+1=(x-1)/2", "expect": "-1", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "4", "module": "casui:CAS", "tool": "integrate", "inputs": "sqrt(x)+x^2", "expect": "x^3/3+2*sqrt(x)*x/3", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "6a", "module": "mpure:C", "tool": "Param point at t", "inputs": "-2t^2,9t-0.7t^2,9.5", "expect": "(-361/2, 893/40)"}
{"paper": "73573-jun22", "q": "6bi", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "-2t^2,9t-0.7t^2,?", "expect": "(7*t/20-9/4)/t"}
{"paper": "73573-jun22", "q": "6bii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "9-1.4x=0", "expect": "45/7", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "6bii", "module": "mpure:C", "tool": "Param point at t", "inputs": "-2t^2,9t-0.7t^2,45/7", "expect": "(-4050/49, 405/14)"}
{"paper": "73573-jun22", "q": "7ai", "module": "mpure:C", "tool": "Line through 2 points", "inputs": "1.76,1.94,3.46,4.49", "expect": "y = (3/2)x - 7/10"}
{"paper": "73573-jun22", "q": "7aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "10^(-0.7)", "expect": "0.2", "deg": false}
{"paper": "73573-jun22", "q": "7b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(60000/0.2)^(1/1.5)", "expect": "4481", "deg": false}
{"paper": "73573-jun22", "q": "7a", "module": "mpure:F", "tool": "y = a x^n from 2 pts", "inputs": "10^1.76,10^1.94,10^3.46,10^4.49", "expect": "n = 3/2"}
{"paper": "73573-jun22", "q": "7a", "module": "mpure:F", "tool": "y = a x^n from 2 pts", "inputs": "10^1.76,10^1.94,10^3.46,10^4.49", "expect": "a = 0.2"}
{"paper": "73573-jun22", "q": "8b", "module": "mcalc:G", "tool": "Connected rates", "inputs": "(12x/pi)^(1/3),24,8", "expect": "0.501"}
{"paper": "73573-jun22", "q": "10ci", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "(x^2+10)/(2x+5)=x", "expect": "sqrt(65)", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "10d", "module": "mcalc:G", "tool": "Stationary points", "inputs": "(x^2+10)/(2x+5)", "expect": "min at (1.53, 1.53)"}
{"paper": "73573-jun22", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "sqrt(0.35)", "expect": "0.59", "deg": false}
{"paper": "73573-jun22", "q": "14bi", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "20,0.3,1", "expect": "0.00684"}
{"paper": "73573-jun22", "q": "14bii", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "20,0.3,3", "expect": "0.107"}
{"paper": "73573-jun22", "q": "14biii", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "20,0.3,10", "expect": "0.048"}
{"paper": "73573-jun22", "q": "14c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "10x(1-x)=2.25", "expect": "sqrt(10)", "ask": null, "deg": false}
{"paper": "73573-jun22", "q": "16bi", "module": "casui:Calculate", "tool": "Calculate", "inputs": "101/240", "expect": "101/240", "deg": false}
{"paper": "73573-jun22", "q": "16bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "67/240", "expect": "67/240", "deg": false}
{"paper": "73573-jun22", "q": "16biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "139/195", "expect": "0.713", "deg": false}
{"paper": "73573-jun22", "q": "16c", "module": "mstat:M", "tool": "Venn: find the ?", "inputs": "153/240,45/240,21/240,?", "expect": "independent: no"}
{"paper": "73573-jun22", "q": "17", "module": "mstat:O", "tool": "z test mean upper", "inputs": "34,4.5,30,36.2,2.5", "expect": "2.68"}
{"paper": "73573-jun22", "q": "17", "module": "mstat:O", "tool": "z test mean upper", "inputs": "34,4.5,30,36.2,2.5", "expect": "1.96"}
{"paper": "73573-jun22", "q": "17", "module": "mstat:O", "tool": "z test mean upper", "inputs": "34,4.5,30,36.2,2.5", "expect": "reject H0"}
{"paper": "73573-jun22", "q": "18a", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "1.78,0.23,1.33,2.22", "expect": "0.947"}
{"paper": "73573-jun22", "q": "18bii", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "1.78,0.23,1.70,1.90", "expect": "0.335"}
{"paper": "73573-jun22", "q": "18biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.3352^2", "expect": "0.112", "deg": false}
{"paper": "73573-jun22", "q": "18c", "module": "mstat:L", "tool": "Stats from summary", "inputs": "40,69.2,2.81+69.2^2/40", "expect": "1.73"}
{"paper": "73573-jun22", "q": "18c", "module": "mstat:L", "tool": "Stats from summary", "inputs": "40,69.2,2.81+69.2^2/40", "expect": "0.265"}
{"paper": "73573-jun22", "q": "19", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "35,0.42,18,10", "expect": "0.169"}
{"paper": "73573-jun22", "q": "19", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "35,0.42,18,10", "expect": "X >= 19"}
{"paper": "73573-jun22", "q": "19", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "35,0.42,18,10", "expect": "do not reject"}
{"paper": "73573-jun23", "q": "5", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "3e^(2x)=10", "expect": "x = ln(10/3)/2", "ask": null, "deg": false}
{"paper": "73573-jun23", "q": "5", "module": "mcalc:G", "tool": "f, f' and f'' at a", "inputs": "3e^(2x),ln(10/3)/2", "expect": "f'(0.602) = 20"}
{"paper": "73573-jun23", "q": "6bi", "module": "casui:CAS", "tool": "substitute x = a", "inputs": "x^2(2x+a)+36", "expect": "9*(a-6)+36", "ask": "-3", "deg": false}
{"paper": "73573-jun23", "q": "7bi", "module": "mcalc:G", "tool": "Stationary points", "inputs": "25/8*(pi-x+2sin(x))", "expect": "max at (pi/3, 12)"}
{"paper": "73573-jun23", "q": "7bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "25/8*(pi-pi/3+2sin(pi/3))", "expect": "25*(2*pi/3+sqrt(3))/8", "deg": false}
{"paper": "73573-jun23", "q": "8", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "x^9/(x^5+2)^3", "expect": "1/180", "ask": "0,1", "deg": false}
{"paper": "73573-jun23", "q": "9a", "module": "mpure:C", "tool": "Param point at t", "inputs": "t-1/t+4.8,t+2/t,0.2", "expect": "51/5"}
{"paper": "73573-jun23", "q": "9a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(0.2+2/0.2)-(3+2/3)", "expect": "6.53", "deg": false}
{"paper": "73573-jun23", "q": "9bi", "module": "mcalc:G", "tool": "Parametric dy/dx", "inputs": "t-1/t+4.8,t+2/t,3", "expect": "7/10"}
{"paper": "73573-jun23", "q": "9bii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "1-2/x^2=0", "expect": "sqrt(2)", "ask": null, "deg": false}
{"paper": "73573-jun23", "q": "9bii", "module": "mpure:C", "tool": "Param point at t", "inputs": "t-1/t+4.8,t+2/t,sqrt(2)", "expect": "2sqrt(2)"}
{"paper": "73573-jun23", "q": "9biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "atan(0.7)", "expect": "34.99", "deg": true}
{"paper": "73573-jun23", "q": "12b", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "32,0.4,7", "expect": "0.0157"}
{"paper": "73573-jun23", "q": "12c", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "32,0.4,16", "expect": "0.908"}
{"paper": "73573-jun23", "q": "12d", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "32,0.4,13", "expect": "0.538"}
{"paper": "73573-jun23", "q": "12e", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "32,0.4", "expect": "12.8"}
{"paper": "73573-jun23", "q": "12e", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "32,0.4", "expect": "sd = 2.77"}
{"paper": "73573-jun23", "q": "13a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.2^2+0.8^2", "expect": "0.68", "deg": false}
{"paper": "73573-jun23", "q": "13b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.04/0.36", "expect": "1/9", "deg": false}
{"paper": "73573-jun23", "q": "14b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "641520/24", "expect": "26730", "deg": false}
{"paper": "73573-jun23", "q": "14b", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "24500,5200,24,26730,5", "expect": "2.1"}
{"paper": "73573-jun23", "q": "14b", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "24500,5200,24,26730,5", "expect": "reject H0"}
{"paper": "73573-jun23", "q": "15ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1393-1.5*(1570-1167)", "expect": "788.5", "deg": false}
{"paper": "73573-jun23", "q": "15ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1393+1.5*(1570-1167)", "expect": "1997.5", "deg": false}
{"paper": "73573-jun23", "q": "15b", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "0.76+3x=1", "expect": "2/25", "ask": null, "deg": false}
{"paper": "73573-jun23", "q": "15b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.37+0.9*0.08+0.25+0.4*0.08", "expect": "0.724", "deg": false}
{"paper": "73573-jun23", "q": "16ai", "module": "mstat:N", "tool": "Normal P(X<x)", "inputs": "6.5,0.73,5.2", "expect": "0.0375"}
{"paper": "73573-jun23", "q": "16aii", "module": "mstat:N", "tool": "Normal P(X>x)", "inputs": "6.5,0.73,7", "expect": "0.247"}
{"paper": "73573-jun23", "q": "16aiii", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "6.5,0.73,5,8", "expect": "0.96"}
{"paper": "73573-jun23", "q": "16b", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "5.9,0.6,6.1,0.8", "expect": "5.81"}
{"paper": "73573-jun23", "q": "16b", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "5.9,0.6,6.1,0.8", "expect": "0.34"}
{"paper": "73573-jun23", "q": "17", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "25,0.7,21,2.5", "expect": "0.0905"}
{"paper": "73573-jun23", "q": "17", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "25,0.7,21,2.5", "expect": "do not reject"}
{"paper": "73573-jun24", "q": "2", "module": "mpure:B", "tool": "Discriminant in k", "inputs": "4,k,9", "expect": "k = -12, 12"}
{"paper": "73573-jun24", "q": "4", "module": "casui:CAS", "tool": "d/dx", "inputs": "x^4+2^x", "expect": "4*x^3+2^x*ln(2)", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "6a", "module": "casui:CAS", "tool": "integrate", "inputs": "6x^2-5/sqrt(x)", "expect": "2*x^3-10*sqrt(x)", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "6b", "module": "mcalc:H", "tool": "Separable DE at point", "inputs": "6x^2-5/sqrt(x),1,4,90", "expect": "2*x^3-10*sqrt(x)-18"}
{"paper": "73573-jun24", "q": "8ci", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "20(11-10e^(-x))=86", "expect": "x = -ln(67/100)", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "8ci", "module": "casui:Calculate", "tool": "Calculate", "inputs": "-ln(67/100)", "expect": "0.4004", "deg": false}
{"paper": "73573-jun24", "q": "8cii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "20(11-10e^(-0.4005x))=219", "expect": "13.2", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "9a", "module": "mpure:C", "tool": "Circle from general", "inputs": "8,-12,27", "expect": "(x + 4)^2 + (y - 6)^2 = 25"}
{"paper": "73573-jun24", "q": "9a", "module": "mpure:C", "tool": "Circle from general", "inputs": "8,-12,27", "expect": "centre (-4, 6)"}
{"paper": "73573-jun24", "q": "9c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "16+(x-6)^2=25", "expect": "3", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "9c", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "16+(x-6)^2=25", "expect": "9", "ask": null, "deg": false}
{"paper": "73573-jun24", "q": "12", "module": "mstat:L", "tool": "Frequency table", "inputs": "0,1,1,4,2,18,3,16,4,5,5,37,6,2,7,1", "expect": "IQR = 3"}
{"paper": "73573-jun24", "q": "14", "module": "mstat:L", "tool": "Stats from summary", "inputs": "350,945000,2607500000", "expect": "mean = 2700"}
{"paper": "73573-jun24", "q": "14", "module": "mstat:L", "tool": "Stats from summary", "inputs": "350,945000,2607500000", "expect": "sd (n) = 400"}
{"paper": "73573-jun24", "q": "15ab", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "48,0.175", "expect": "8.4"}
{"paper": "73573-jun24", "q": "15ab", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "48,0.175", "expect": "6.93"}
{"paper": "73573-jun24", "q": "15c", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "48,0.175,9", "expect": "0.674"}
{"paper": "73573-jun24", "q": "15d", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "48,0.175,6", "expect": "P(X >= 6) = 0.868"}
{"paper": "73573-jun24", "q": "15e", "module": "mstat:N", "tool": "Binomial P(a<=X<=b)", "inputs": "48,0.175,9,15", "expect": "0.462"}
{"paper": "73573-jun24", "q": "17c", "module": "mstat:N", "tool": "Normal P(X>x)", "inputs": "50,4,56", "expect": "0.0668"}
{"paper": "73573-jun24", "q": "17d", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "50,4,40,60", "expect": "0.988"}
{"paper": "73573-jun24", "q": "17e", "module": "mstat:N", "tool": "Inverse Normal", "inputs": "50,4,0.05", "expect": "43.4"}
{"paper": "73573-jun24", "q": "17f", "module": "mstat:O", "tool": "z test mean upper", "inputs": "50,4,40,51.5,10", "expect": "p-value = 0.00885"}
{"paper": "73573-jun24", "q": "17f", "module": "mstat:O", "tool": "z test mean upper", "inputs": "50,4,40,51.5,10", "expect": "reject H0"}
{"paper": "73573-jun24", "q": "18aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1-0.21", "expect": "0.79", "deg": false}
{"paper": "73573-jun24", "q": "18aiii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.07/0.61", "expect": "7/61", "deg": false}
{"paper": "73573-jun24", "q": "18b", "module": "mstat:M", "tool": "Venn: find the ?", "inputs": "0.39,0.28,0.21,?", "expect": "independent: no"}
{"paper": "73573-jun24", "q": "19aii", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "25,0.8,18,10", "expect": "X <= 16"}
{"paper": "73573-jun24", "q": "19aii", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "25,0.8,18,10", "expect": "X >= 24"}
{"paper": "73573-jun24", "q": "19aii", "module": "mstat:O", "tool": "HT binomial two tail", "inputs": "25,0.8,18,10", "expect": "do not reject"}
{"paper": "73573-jun25", "q": "1", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1/sqrt(2)*sqrt(6)", "expect": "sqrt(3)", "deg": false}
{"paper": "73573-jun25", "q": "6a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "2,-3,5", "expect": "x^1: -240"}
{"paper": "73573-jun25", "q": "6a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "2,-3,5", "expect": "x^2: 720"}
{"paper": "73573-jun25", "q": "6a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "2,-3,5", "expect": "x^3: -1080"}
{"paper": "73573-jun25", "q": "6b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "32-240*0.02+720*0.02^2-1080*0.02^3", "expect": "27.47936", "deg": false}
{"paper": "73573-jun25", "q": "9a", "module": "mpure:B", "tool": "Transform af(bx+c)+d", "inputs": "1/x,3,1,-4,0", "expect": "3/(x-4)"}
{"paper": "73573-jun25", "q": "10a", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "2,5", "expect": "R = sqrt(29)"}
{"paper": "73573-jun25", "q": "10a", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "2,5", "expect": "al = 68.2 deg"}
{"paper": "73573-jun25", "q": "10bi", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "2,5", "expect": "max sqrt(29) at x = 21.8 deg"}
{"paper": "73573-jun25", "q": "10bii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "14.2+sqrt(29)", "expect": "19.6", "deg": false}
{"paper": "73573-jun25", "q": "10biii", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "14.2-(2sin(x)+5cos(x))-15,0,365", "expect": "x = 120.3", "full": true}
{"paper": "73573-jun25", "q": "10biii", "module": "mpure:E", "tool": "Solve trig eqn (deg)", "inputs": "14.2-(2sin(x)+5cos(x))-15,0,365", "expect": "x = 283.2", "full": true}
{"paper": "73573-jun25", "q": "10biii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "(283.26-120.34)/7", "expect": "23.3", "deg": false}
{"paper": "73573-jun25", "q": "11a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "7/(28*16)", "expect": "0.015625", "deg": false}
{"paper": "73573-jun25", "q": "11b", "module": "casui:CAS", "tool": "d/dx", "inputs": "8x^3", "expect": "24*x^2", "ask": null, "deg": false}
{"paper": "73573-jun25", "q": "11ci", "module": "casui:Calculate", "tool": "Calculate", "inputs": "-0.4375/24", "expect": "-7/384", "deg": false}
{"paper": "73573-jun25", "q": "14", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "9,1.5,6,12", "expect": "0.954"}
{"paper": "73573-jun25", "q": "15ai", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "25,0.2,0", "expect": "0.00378"}
{"paper": "73573-jun25", "q": "15aii", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "25,0.2,5", "expect": "0.617"}
{"paper": "73573-jun25", "q": "15aiii", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "25,0.2,9", "expect": "0.0468"}
{"paper": "73573-jun25", "q": "16ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "340/17*9.5", "expect": "190", "deg": false}
{"paper": "73573-jun25", "q": "17ab", "module": "mstat:L", "tool": "Summary stats", "inputs": "2,4,3,1,4,5,2,3", "expect": "mean = 3"}
{"paper": "73573-jun25", "q": "17ab", "module": "mstat:L", "tool": "Summary stats", "inputs": "2,4,3,1,4,5,2,3", "expect": "sd^2 = sum x^2/n - mean^2 = 1.5"}
{"paper": "73573-jun25", "q": "17c", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "30,0.1", "expect": "mean = np = 3"}
{"paper": "73573-jun25", "q": "17c", "module": "mstat:N", "tool": "Binomial mean var", "inputs": "30,0.1", "expect": "variance = np(1-p) = 2.7"}
{"paper": "73573-jun25", "q": "18a", "module": "mstat:N", "tool": "Inverse Normal", "inputs": "5.7,1.2,0.25", "expect": "4.89"}
{"paper": "73573-jun25", "q": "18a", "module": "mstat:N", "tool": "Inverse Normal", "inputs": "5.7,1.2,0.75", "expect": "6.51"}
{"paper": "73573-jun25", "q": "18b", "module": "mstat:O", "tool": "z test mean lower", "inputs": "5.7,1.2,160,5.6,5", "expect": "0.146"}
{"paper": "73573-jun25", "q": "18b", "module": "mstat:O", "tool": "z test mean lower", "inputs": "5.7,1.2,160,5.6,5", "expect": "do not reject"}
{"paper": "73573-jun25", "q": "19a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.5-0.38", "expect": "0.12", "deg": false}
{"paper": "73573-jun25", "q": "19e", "module": "mstat:M", "tool": "Venn: find the ?", "inputs": "0.38,0.12,0.07,?", "expect": "independent: no"}
{"paper": "73573-jun25", "q": "20a", "module": "mstat:N", "tool": "Normal P(X<x)", "inputs": "0.41,0.07,0.39", "expect": "0.388"}
{"paper": "73573-jun25", "q": "20b", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "0.41,0.07,0.3,0.5", "expect": "0.843"}
{"paper": "73573-jun25", "q": "20ci", "module": "mstat:N", "tool": "Normal P(X>x)", "inputs": "0.41,0.07,0.6", "expect": "0.0033"}
{"paper": "73573-nov20", "q": "2", "module": "mpure:E", "tool": "R form a sin + b cos", "inputs": "8,6", "expect": "R = 10"}
{"paper": "73573-nov20", "q": "4a", "module": "mpure:B", "tool": "Factor theorem", "inputs": "4x^3-15x^2-48x-36,6", "expect": "p(6) = 0"}
{"paper": "73573-nov20", "q": "4bi", "module": "mpure:B", "tool": "Divide p(x) by d(x)", "inputs": "4x^3-15x^2-48x-36,x-6", "expect": "4*x^2+9*x+6"}
{"paper": "73573-nov20", "q": "4bi", "module": "mpure:B", "tool": "Quadratic", "inputs": "4,9,6", "expect": "disc = -15"}
{"paper": "73573-nov20", "q": "4bi", "module": "mpure:B", "tool": "Quadratic", "inputs": "4,9,6", "expect": "no real roots"}
{"paper": "73573-nov20", "q": "4bii", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "4x^3-15x^2-48x-36=0", "expect": "x = 6", "ask": null, "deg": false}
{"paper": "73573-nov20", "q": "5a", "module": "mpure:F", "tool": "N = A e^(kt) 2 pts", "inputs": "0,1,15.9,0.5", "expect": "e^(-0.043594*t)"}
{"paper": "73573-nov20", "q": "5a", "module": "mpure:F", "tool": "Solve a^x = b", "inputs": "e^(-0.0435935),0.1", "expect": "52.8"}
{"paper": "73573-nov20", "q": "5b", "module": "mpure:F", "tool": "Evaluate A e^(kt)", "inputs": "100,-0.0435935,168", "expect": "N = 0.066"}
{"paper": "73573-nov20", "q": "7bi", "module": "casui:CAS", "tool": "simplify", "inputs": "2*(x!/(24*(x-4)!))/(51*(x!/(2*(x-2)!)))", "expect": "(x-2)*(x-3)/306", "ask": null, "deg": false}
{"paper": "73573-nov20", "q": "7bii", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,-5,-300", "expect": "x = -15"}
{"paper": "73573-nov20", "q": "7bii", "module": "mpure:B", "tool": "Quadratic", "inputs": "1,-5,-300", "expect": "x = 20"}
{"paper": "73573-nov20", "q": "9a", "module": "mpure:E", "tool": "Identity check (rad)", "inputs": "1/sin(2x)+1/tan(2x),1/tan(x)", "expect": "holds"}
{"paper": "73573-nov20", "q": "10", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1-(0.12+0.05+0.18+0.30+0.24)", "expect": "0.11", "deg": false}
{"paper": "73573-nov20", "q": "11", "module": "mstat:L", "tool": "Summary stats", "inputs": "-17,-16,-14,-9,-2,2,6,5,-3,-4,-11,-18", "expect": "8.24"}
{"paper": "73573-nov20", "q": "13ai", "module": "casui:Calculate", "tool": "Calculate", "inputs": "144/200", "expect": "18/25", "deg": false}
{"paper": "73573-nov20", "q": "13aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "153/200", "expect": "153/200", "deg": false}
{"paper": "73573-nov20", "q": "13b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "47/56", "expect": "47/56", "deg": false}
{"paper": "73573-nov20", "q": "13c", "module": "casui:Calculate", "tool": "Calculate", "inputs": "109/200*108/199*107/198", "expect": "0.16", "deg": false}
{"paper": "73573-nov20", "q": "14", "module": "mstat:L", "tool": "Summary stats", "inputs": "4.25,3.90,4.15,3.95,4.20,4.15,5.00,3.85,4.25,4.05,3.80,3.95", "expect": "mean = 4.125", "full": true}
{"paper": "73573-nov20", "q": "14", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "4,0.8,12,4.125,10", "expect": "0.541"}
{"paper": "73573-nov20", "q": "14", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "4,0.8,12,4.125,10", "expect": "do not reject"}
{"paper": "73573-nov20", "q": "15a", "module": "mstat:K", "tool": "Stratified sample", "inputs": "70,4735,8565", "expect": "25"}
{"paper": "73573-nov20", "q": "15a", "module": "mstat:K", "tool": "Stratified sample", "inputs": "70,4735,8565", "expect": "45"}
{"paper": "73573-nov20", "q": "16", "module": "mstat:O", "tool": "PMCC test 1 tail", "inputs": "0.379,25,1", "expect": "0.4622"}
{"paper": "73573-nov20", "q": "16", "module": "mstat:O", "tool": "PMCC test 1 tail", "inputs": "0.379,25,1", "expect": "do not reject"}
{"paper": "73573-nov20", "q": "17aii", "module": "mstat:N", "tool": "Normal P(a<X<b)", "inputs": "8,1.5,6,10", "expect": "0.818"}
{"paper": "73573-nov20", "q": "17b", "module": "mstat:N", "tool": "Inverse Normal", "inputs": "8,1.5,0.1", "expect": "6.08"}
{"paper": "73573-nov20", "q": "17c", "module": "mstat:N", "tool": "Normal find mu or sd", "inputs": "7,?,5,0.25", "expect": "2.97"}
{"paper": "73573-nov20", "q": "18ai", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "30,0.25,5", "expect": "0.105"}
{"paper": "73573-nov20", "q": "18aii", "module": "mstat:N", "tool": "Binomial P(X<=k)", "inputs": "30,0.4,14", "expect": "0.825"}
{"paper": "73573-nov20", "q": "18aiii", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "30,0.7,20", "expect": "P(X >= 20) = 0.73"}
{"paper": "73573-nov20", "q": "18b", "module": "mstat:O", "tool": "HT binomial lower", "inputs": "60,0.3,13,5", "expect": "X <= 11"}
{"paper": "73573-nov20", "q": "18b", "module": "mstat:O", "tool": "HT binomial lower", "inputs": "60,0.3,13,5", "expect": "do not reject"}
{"paper": "73573-nov21", "q": "2", "module": "mpure:B", "tool": "Simplify f(x)/g(x)", "inputs": "(x+3)(6-2x),(x-3)(3+x)", "expect": "-2"}
{"paper": "73573-nov21", "q": "3", "module": "casui:CAS", "tool": "d/dx", "inputs": "3x^2", "expect": "6*x", "ask": null, "deg": false}
{"paper": "73573-nov21", "q": "4a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "-3,2,10", "expect": "1024*x^10"}
{"paper": "73573-nov21", "q": "4a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "-3,2,10", "expect": "-15360*x^9"}
{"paper": "73573-nov21", "q": "4a", "module": "mpure:D", "tool": "Binomial (a+bx)^n", "inputs": "-3,2,10", "expect": "103680*x^8"}
{"paper": "73573-nov21", "q": "4b", "module": "casui:CAS", "tool": "expand", "inputs": "(2x-3/x)^10", "expect": "-1959552", "ask": null, "deg": false}
{"paper": "73573-nov21", "q": "5a", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "5,0.7", "expect": "sector area = 35/4"}
{"paper": "73573-nov21", "q": "5a", "module": "mpure:E", "tool": "Arc and sector (rad)", "inputs": "5,0.7", "expect": "sector perimeter = 27/2"}
{"paper": "73573-nov21", "q": "5aii", "module": "casui:Calculate", "tool": "Calculate", "inputs": "13.5*1.80", "expect": "24.3", "deg": false}
{"paper": "73573-nov21", "q": "5bii", "module": "mcalc:G", "tool": "Stationary points", "inputs": "18/5*(20/x+x)", "expect": "min at (2sqrt(5)"}
{"paper": "73573-nov21", "q": "7a", "module": "casui:Calculate", "tool": "Calculate", "inputs": "30*0.98", "expect": "29.4", "deg": false}
{"paper": "73573-nov21", "q": "7c", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "30,0.98,15", "expect": "392"}
{"paper": "73573-nov21", "q": "7d", "module": "mpure:D", "tool": "Geometric a,r,n", "inputs": "30,0.98,15", "expect": "S(inf) = 1500"}
{"paper": "73573-nov21", "q": "8", "module": "casui:CAS", "tool": "definite integral a..b", "inputs": "x*cos(x)", "expect": "pi*sqrt(3)/6-pi*sqrt(2)/8-sqrt(2)/2+1/2", "ask": "pi/4,pi/3", "deg": false}
{"paper": "73573-nov21", "q": "9ai", "module": "casui:CAS", "tool": "d2/dx2", "inputs": "x^4+5x^3", "expect": "12*x^2+30*x", "ask": null, "deg": false}
{"paper": "73573-nov21", "q": "9aii", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x^4+5x^3", "expect": "min at (-15/4"}
{"paper": "73573-nov21", "q": "9aii", "module": "mcalc:G", "tool": "Stationary points", "inputs": "x^4+5x^3", "expect": "(0, 0)"}
{"paper": "73573-nov21", "q": "9b", "module": "mcalc:G", "tool": "Increasing/decreasing", "inputs": "x^4+5x^3", "expect": "increasing for x > -15/4"}
{"paper": "73573-nov21", "q": "9cii", "module": "mcalc:G", "tool": "Increasing/decreasing", "inputs": "x^4-5x^3", "expect": "increasing for x > 15/4"}
{"paper": "73573-nov21", "q": "11", "module": "casui:Calculate", "tool": "Calculate", "inputs": "1-144/225", "expect": "0.36", "deg": false}
{"paper": "73573-nov21", "q": "12", "module": "mstat:K", "tool": "Systematic sample", "inputs": "8000,100", "expect": "k = 80"}
{"paper": "73573-nov21", "q": "13ai", "module": "mstat:L", "tool": "Summary stats", "inputs": "154,146,138,159,138,130,146,146,192,122,175,140,146", "expect": "mean = 149"}
{"paper": "73573-nov21", "q": "13ai", "module": "mstat:L", "tool": "Summary stats", "inputs": "154,146,138,159,138,130,146,146,192,122,175,140,146", "expect": "sd (n) = 17.8"}
{"paper": "73573-nov21", "q": "13aii", "module": "mstat:L", "tool": "Outliers", "inputs": "154,146,138,159,138,130,146,146,192,122,175,140,146", "expect": "192"}
{"paper": "73573-nov21", "q": "14a", "module": "casui:CAS", "tool": "solve exact f(x)=0", "inputs": "x+2x-0.1=0.8", "expect": "3/10", "ask": null, "deg": false}
{"paper": "73573-nov21", "q": "14b", "module": "mstat:M", "tool": "Conditional P(A|B)", "inputs": "0.1,0.3", "expect": "P(A|B) = 0.333"}
{"paper": "73573-nov21", "q": "14b", "module": "casui:Calculate", "tool": "Calculate", "inputs": "0.1/0.3", "expect": "1/3", "deg": false}
{"paper": "73573-nov21", "q": "14c", "module": "mstat:M", "tool": "Venn: find the ?", "inputs": "0.3,0.6,0.1,?", "expect": "independent: no"}
{"paper": "73573-nov21", "q": "15", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "65,11.3,100,67.8,2", "expect": "2.48"}
{"paper": "73573-nov21", "q": "15", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "65,11.3,100,67.8,2", "expect": "2.326"}
{"paper": "73573-nov21", "q": "15", "module": "mstat:O", "tool": "z test mean two tail", "inputs": "65,11.3,100,67.8,2", "expect": "reject H0"}
{"paper": "73573-nov21", "q": "16b", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "16,1,1,1,1,5/8", "expect": "x = 1/40"}
{"paper": "73573-nov21", "q": "16b", "module": "mpure:B", "tool": "Simultaneous 2 linear", "inputs": "16,1,1,1,1,5/8", "expect": "y = 3/5"}
{"paper": "73573-nov21", "q": "17b", "module": "mstat:N", "tool": "Binomial P(X=k)", "inputs": "10,0.6,4", "expect": "0.111"}
{"paper": "73573-nov21", "q": "17c", "module": "mstat:N", "tool": "Binomial P(X>=k)", "inputs": "10,0.6,4", "expect": "0.945"}
{"paper": "73573-nov21", "q": "17d", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "15,0.6,12,5", "expect": "0.0905"}
{"paper": "73573-nov21", "q": "17d", "module": "mstat:O", "tool": "HT binomial upper", "inputs": "15,0.6,12,5", "expect": "do not reject"}
{"paper": "73573-nov21", "q": "18aii", "module": "mstat:N", "tool": "Normal P(X>x)", "inputs": "372,3.5,368", "expect": "0.873"}
{"paper": "73573-nov21", "q": "18bi", "module": "mstat:N", "tool": "Inverse Normal", "inputs": "0,1,0.975", "expect": "1.96"}
{"paper": "73573-nov21", "q": "18bii", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "346,0.975,336,0.14", "expect": "340"}
{"paper": "73573-nov21", "q": "18bii", "module": "mstat:N", "tool": "Normal mu and sd", "inputs": "346,0.975,336,0.14", "expect": "3.29"}
```
