# AQA 7357 past papers: toolkit gaps, pass 2

Second audit of the native-ui toolkit (commit 0618767) against the same 24 AQA 7357 papers: Paper 1, 2 and 3 for Jun18, Jun19, Nov20, Nov21, Jun22, Jun23, Jun24 and Jun25. Every calculator step was run again on the laptop through `tests_pastpapers.output`, with the input specs as they are now ('?' unknowns, optional fields, letters). Per-paper tables: `aqa-7357<n>-<series>.md` in this folder, with a "pass1 → pass2" column.

How pass 2 was done:

- Every pass-1 OK row was re-run through its regression cases in `tests_pastpapers_aqa.CASES` (777 checks, 0 failures) and its output was read again for form and readability.
- Every pass-1 AWKWARD, WRONG and GAP row (143) was re-run with the best tool that exists now, often a new one.
- Every pass-1 "none" row was checked against the new tools; 5 now have a tool that helps.
- Tools that changed were probed for regressions beyond the paper cases (binomial precision, trig root filtering, '?' handling, the vector-motion side lines).
- Rows added in pass 2 have "- → X" in the pass1 → pass2 column: they record a second route that fails.

## Totals

| | OK | none | AWKWARD | WRONG | GAP | rows |
|---|---|---|---|---|---|---|
| pass 1, all rows | 551 | 227 | 98 | 27 | 18 | 921 |
| pass 2, all rows | 676 | 222 | 21 | 8 | 1 | 928 |
| pass 1, main part rows | 544 | 227 | 95 | 21 | 18 | 905 |
| pass 2, main part rows | 661 | 222 | 20 | 1 | 1 | 905 |

Main part rows are the first row of each part (all 2400 marks); the other rows are second routes. Pass 2 adds 7 such rows: 1 AWKWARD and 6 WRONG.

Transitions (all pass-1 rows):

| pass 1 → pass 2 | rows |
|---|---|
| OK → OK | 548 |
| OK → AWKWARD | 3 (stricter readability; same output as in pass 1) |
| AWKWARD → OK | 84 |
| AWKWARD → AWKWARD | 14 |
| WRONG → OK | 25 |
| WRONG → WRONG | 2 |
| GAP → OK | 14 |
| GAP → AWKWARD | 3 |
| GAP → GAP | 1 |
| none → OK | 5 |
| none → none | 222 |

Pass-1 problems fixed: **123 of the 143 non-OK rows are now OK** (84 of 98 AWKWARD, 25 of 27 WRONG, 14 of 18 GAP). 3 GAP rows are now AWKWARD. 17 rows are unchanged: 14 AWKWARD, 2 WRONG and 1 GAP.

Of the 74 pass-1 fix keys, 54 are fully fixed, 10 are partly fixed and 10 are untouched (list at the end of this file).

## Correctness problems (fix first)

These give a wrong answer, a crash or a misleading line, not just an inconvenient one.

1. **[eq-sign-multiplies] '=' in a Maths tool field is read as multiplication.** NEW FINDING, PRE-EXISTING (the pass-1 lexer does the same). `caslex` skips characters it does not know ('=', '<', '>') and then inserts an implicit multiplication. The CAS screen and Solve split on '=' first (`casui._parse_eq`), but the Maths tool fields go through `casutil.convert` and do not. The answers come out confident and wrong:
   - F/Evaluate log expr <logb(2,x^3)-logb(2,y^2)=9> prints "x = y^6". MS for 7357/2 Jun22 Q9 is x = 8y^(2/3); typing "-9" instead of "=9" gives that.
   - B/Factorise <x^2-4=0> prints "x^2, = 0 at x = 0".
   - G/Implicit dy/dx <x^2+y^2=25,3,4> prints "dy/dx = -0.03" (it differentiates 25x^2 + y^2); the right answer is -3/4.
   - B/Simultaneous non-linear <x+5y=25,...> returns surds of 14009801 instead of (-55, 16), (-5, 6).
   
   Fix: in `casutil.convert`, rewrite an 'e' field with one '=' as (l)-(r), the way `_parse_eq` does. Make `caslex` raise "cannot read '='" (or '<', '>') rather than dropping the character. Test cases: the four calls above should give x = 8*y^(2/3) (Jun22/2 Q9), (x-2)*(x+2), dy/dx = -3/4 and (x, y) = (-55, 16) (Jun18/1 Q9b).
2. **[vec-parallel-negative-t] REGRESSION.** `mmech._zeros` clamps a negative root to 0 before it tests t >= 0 (commit dd88d00). So Q/Vector a(t) to v, r <6t,7,0,4,0,0,2> prints "v parallel to i at t = 0" although v(0) = 4j: the root of 7t + 4 is t = -4/7. The same line appears in Vector r(t) to v, a and Vector v(t) to r, a. 7357/2 Jun25 Q19b. Fix: test `r >= -1e-6` first and clamp only for printing, as the pass-1 code did. Test: the call above must not contain "parallel to i"; Q/Vector r(t) to v, a <t^3-5t^2,8t-t^2,2> must still list t = 4 (i) and t = 0, 3.33 (j).
3. **[solve-overflow] 5^(x-2) = 7^1570.** CAS solve exact says "no solutions found, searched -10^6 <= x <= 10^6", although the root 1900.2 is inside that range: 7^1570 overflows a float. F/Solve a^x = b <5,7^1570> says "too large". 7357/2 Jun24 Q4, MS x = 2 + 1570 log5 7 = 1900.2. Fix: in cassolve, treat c1 a^(p x + q) = c2 b^(r x + s) by taking ln of both sides symbolically before any evaluation (this also covers [solve-exp-exact]). F/Solve a^x = b should accept b as a power and use ln b = 1570 ln 7. Never print "no solutions" after an overflow; say "overflow" instead. Test: CAS[solve exact] <5^(x-2)=7^1570> should give x = 1900.23 (with the exact 2 + 1570 ln7/ln5).
4. **[defint-symbolic-limits] limits like ln 4 become decimals inside e^().** CAS definite integral <6-e^(x/2)-e^x> ask=0,ln(4) prints "-e^(1.386294)-2e^(0.693147)+11.317766" on the exact line. The simplest case, <e^x> ask=0,ln(4), prints "e^(1.386294)-1" where it should print 3. 7357/1 Nov20 Q15 (H/Area between curves already gives 6ln(4) - 5, so the main row is OK). Fix: substitute the limits as exact trees (`casalg.subst_exact`) and simplify e^(k ln a) = a^k. Tests: <e^x> 0,ln(4) gives 3; <6-e^(x/2)-e^x> 0,ln(4) gives 6ln(4) - 5 (MS 6ln4 - 5 = 3.318).
5. **[rearrange-y-input] CAS "rearrange for x" ignores a y that is already in the input.** It always solves y = (input) for x. So <x*y+5x-3y-27> gives (4y+27)/(y+5) (right: (3y+27)/(y+5)), and <y=36/(x-3)-5> gives 51/5. PRE-EXISTING. 7357/1 Jun18 Q5b route. Fix: when the input holds y or '=', solve input = 0 for x. Tests: <x*y+5x-3y-27> gives (3y+27)/(y+5); <y=36/(x-3)-5> gives (3y+51)/(y+5).
6. **[plus-minus-print] B/Simplify surd expr prints "+-".** <(5-sqrt(x))/x^2> gives "(5+-sqrt(x))/x^2", which reads as plus-or-minus. New tool code. 7357/3 Jun23 Q4. Fix: print a sum with a negative term as "-", and use the shared tostr. Test: no "+-" in the output; ideally 5x^-2 - x^(-3/2) (see [surd-power-simplify]).
7. **['?' crashes] S/Beam on two supports and M/Three-set Venn crash on '?'.** Python errors leak to the screen ("'<' not supported between instances of 'NoneType' and 'int'", "unsupported operand type(s) for -"). 7357/2 Jun23 Q17ai (Beam <7,?,1.4,5,0,0>) and 7357/3 Jun25 Q19b (Venn <0.38,0.38,0.12,0.11,0,?,0,1>). Fix: Beam should refuse '?' with a pointer to S/Moments: find unknown, or solve for one unknown given a reaction. Three-set Venn should take an optional "none" value and solve one '?' from it. Test: Venn with BC = ? and none = 0.3 gives BC = 0.07, regions 0.27, 0.2, 0.05, 0.11, 0, 0.07, 0 (MS).

## Regressions

- **[vec-parallel-negative-t]** (above, item 2): the only regression found. It does not show in the regression suite, because the pass-1 row with this tool (Jun25/2 Q19b) was AWKWARD, so it had no case.
- The 777 pass-1 regression checks all pass, and the pass-1 OK outputs read the same or better. Probes on changed code found nothing else: binomial probabilities match exact values to 10 s.f. (B(30,0.2), B(13,0.344), B(48,0.175), B(1000,0.001)); the trig solver keeps tan, sec and cosec roots while dropping undefined ones; sig 0.1 is read as 10% and says so.
- Three pass-1 OK rows are now AWKWARD, with the **same** output. The audit is stricter about readability here, so these are not regressions: 7357/1 Nov21 Q11 (y = -1/(x^3/18 - 2/9)), 7357/1 Jun23 Q16bii (ln(-y+4/3)), 7357/2 Nov20 Q19a (v = -1/(-x/10 - 1/4)). See [solved-form-tidy].

## Ranked list of what is still WRONG, AWKWARD or GAP

The 7 correctness items above come first. After them, items are ranked by marks at stake (each part counted once), then by how often the problem shows in OK rows as a readability note. "Form" items have the right answer in a poor form. Each item gives the proposed fix, the paper references, and worked test cases with the mark-scheme answer.

| rank | fix | worst | parts | marks | references |
|---|---|---|---|---|---|
| 1 | eq-sign-multiplies | WRONG | 1 (any field) | - | 7357/2 Jun22 Q9 (second route) |
| 2 | vec-parallel-negative-t | WRONG (regression) | 1 | 6 | 7357/2 Jun25 Q19b |
| 3 | solve-overflow | WRONG | 1 | 3 | 7357/2 Jun24 Q4 |
| 4 | defint-symbolic-limits | WRONG | 1 | 10 | 7357/1 Nov20 Q15 (second route) |
| 5 | rearrange-y-input | WRONG | 1 | 3 | 7357/1 Jun18 Q5b (second route) |
| 6 | plus-minus-print | WRONG | 1 | 2 | 7357/3 Jun23 Q4 (second route) |
| 7 | question-mark-crash (Beam, Three-set Venn) | WRONG | 2 | 6 | 7357/2 Jun23 Q17ai; 7357/3 Jun25 Q19b |
| 8 | solved-form-tidy (frac-in-frac, ln-tidy) | AWKWARD | 4 | 24 | 7357/1 Nov21 Q11; 7357/2 Nov20 Q19a; 7357/1 Jun23 Q16bii; 7357/2 Jun22 Q10bii |
| 9 | subst-trig-tidy + int-trig-sub | AWKWARD | 2 | 9 | 7357/1 Jun22 Q15bi, Q15bii |
| 10 | exp-form | GAP | 2 | 8 | 7357/3 Nov20 Q8bi; 7357/1 Jun19 Q16ciii |
| 11 | trig-simplify-factor | AWKWARD | 1 | 7 | 7357/2 Jun22 Q17 |
| 12 | surd-power-simplify | AWKWARD | 2 | 6 | 7357/3 Jun22 Q8a; 7357/3 Jun23 Q4 |
| 13 | solve-decimal | AWKWARD | 1 (+8 OK-row notes) | 5 | 7357/2 Jun24 Q18a; notes on 7357/1 Jun24 Q20c, Jun25 Q10c; 7357/2 Jun18 Q9ci, Q15a, Jun19 Q8c, Jun23 Q20; 7357/3 Jun24 Q8ci |
| 14 | solve-exp-exact | AWKWARD | 1 | 4 | 7357/2 Nov21 Q6 |
| 15 | implicit-tangent-exact | AWKWARD | 1 | 4 | 7357/1 Nov20 Q12biii |
| 16 | vt-unknown-time | AWKWARD | 1 | 4 | 7357/2 Jun22 Q15 |
| 17 | proj-relation | AWKWARD | 1 | 4 | 7357/2 Nov21 Q18b |
| 18 | display-precision (sf-integer-look, deg-1dp) | form | (notes) | - | 7357/3 Jun22 Q8a, Jun23 Q7bi; 7357/1 Jun24 Q15bii |
| 19 | venn3-unknown | AWKWARD | 1 | 3 | 7357/3 Jun25 Q19b |
| 20 | param-cart-simplify | AWKWARD | 1 | 3 | 7357/1 Jun18 Q5b |
| 21 | pf-tool-junk | AWKWARD | 1 | 3 | 7357/1 Jun23 Q16a (second route) |
| 22 | binom-exact (x^m and letters) | AWKWARD | 1 (+4 notes) | 2 | 7357/2 Jun19 Q9b; notes 7357/1 Jun18 Q6b, Jun24 Q8a; 7357/2 Jun19 Q9a, Nov20 Q3 |
| 23 | int-factor | AWKWARD | 1 | 2 | 7357/2 Jun18 Q5 |
| 24 | int-mod | AWKWARD | 1 | 2 | 7357/2 Jun22 Q6a |
| 25 | small readability items | form | (notes) | - | see list |

### 8. [solved-form-tidy] Clear nested fractions and tidy logs in solved forms (AWKWARD, 4 parts, 24 marks)
H/Separable DE at point now finds c exactly and solves for y and for x. But the solved forms are double fractions, or logs with monic arguments and flipped signs. The same printer gives B/Divide its 4x + 23/3 + 136/3/(3x-5) and Composite/Inverse their fractions inside a numerator.
Proposed: after solving, multiply the top and bottom of a nested fraction by the LCD of the inner denominators (-1/(x^3/18 - 2/9) -> 18/(4 - x^3)). Write ln(y + 4/3) as ln|3y + 4| and absorb the constant into c. Normalise a log argument so that the leading coefficients are positive ((-3y-4)/(3y-4) -> (3y+4)/(4-3y)). Use the same normaliser in B/Divide (quotient + r/d with r/d as one fraction) and in Composite, Inverse.
- 7357/1 Nov21 Q11: H/Separable DE at point <x^2/6,y^2,1,6> should give y = 18/(4-x^3); MS (0, 9/2) via y = 18/(4 - x^3).
- 7357/2 Nov20 Q19a: <-0.1,y^2,0,4> should give y = 20/(2x+5); MS v = 20/(5 + 2t).
- 7357/1 Jun23 Q16bii: <1/100,16-9y^2,0,0> should give x = 25ln((3y+4)/(4-3y))/6; MS t = (25/6) ln((4+3V)/(4-3V)).
- 7357/2 Jun22 Q10bii: <1/2700,y*(900-y),0,25> should give x = 3ln(35y/(900-y)); MS t = 3 ln(35x/(900-x)).
- Readability notes with the same root: 7357/1 Jun24 Q3 (B/Divide), 7357/1 Nov20 Q13c ((-x^2+29x/2+24)/(x-2)^2, MS (48+29x-2x^2)/(2(x-2)^2)), 7357/2 Jun23 Q7c ((5x^2-1/2)/x^2, MS 5 - 1/(2x^2)), 7357/3 Nov21 Q6bi ((7t/20-9/4)/t).

### 9. [subst-trig-tidy] + [int-trig-sub] Finish the x = g(u) substitution (AWKWARD, 2 parts, 9 marks)
H/Substitution now takes x = 2/sin(u) and integrates in u. But it prints the integrand as -cos(u)tan(u)/4 and stops at cos(u)/4 + c.
Proposed: simplify the u-integrand with the trig rules (cos u tan u -> sin u). Then back-substitute through the right triangle of x = g(u): sin u = 2/x gives cos u = sqrt(x^2-4)/x for x > 2. Let CAS integrate try the trig substitution itself for 1/(x^2 sqrt(x^2 - a^2)).
- 7357/1 Jun22 Q15bi: H/Substitution u=g(x) <1/(x^2*sqrt(x^2-4)),2/sin(u)> should show int -sin(u)/4 du; MS k = -1/4.
- 7357/1 Jun22 Q15bii: same call (or CAS integrate <1/(x^2*sqrt(x^2-4))>) should end at sqrt(x^2-4)/(4x) + c; MS sqrt(x^2-4)/(4x) + c.

### 10. [exp-form] Rewrite exponentials (GAP, 2 parts, 8 marks)
Proposed: a "rewrite in prime powers" step in simplify: a rational base to a linear power becomes primes to linear powers, so 24(3/4)^(n-1) -> 3^n/2^(2n-5). A "clear negative exponentials" step multiplies the top and bottom by e^(k) to remove e^(-k). D/Geometric should give S(inf) exactly when a and r involve e.
- 7357/3 Nov20 Q8bi: CAS simplify <24*(3/4)^(x-1)> should give 3^x/2^(2x-5); MS u_n = 3^n/2^(2n-5).
- 7357/1 Jun19 Q16ciii: CAS simplify <((1+e^(-pi))/2)/(1-e^(-pi))> should give (e^pi+1)/(2(e^pi-1)); MS (1+e^pi)/(2(e^pi-1)) = 0.5452.

### 11. [trig-simplify-factor] sin^2 + cos^2 under a common factor (AWKWARD, 7 marks)
Proposed: in simplify, factor out the common factor of a sum before applying sin^2 + cos^2 = 1, then take sqrt of a perfect square (sqrt(4e^(2x)) = 2e^x). Add |a| (and |v|) as a symbolic line in Q/Vector r(t) to v, a.
- 7357/2 Jun22 Q17: CAS simplify <sqrt((-2e^x*sin(x))^2+(2e^x*cos(x))^2)> should give 2e^x; MS |a| = 2e^t.

### 12. [surd-power-simplify] Split and simplify powers (AWKWARD, 2 parts, 6 marks)
B/Simplify surd expr now does x^(8/15) (Jun19/2 Q2 fixed), but two cases remain.
Proposed: split a fraction over a monomial denominator term by term, with fractional powers. Simplify a product of rational powers of pi and integers into the form k (m pi)^(1/3) by factoring the integers into primes.
- 7357/3 Jun23 Q4: B/Simplify surd expr or CAS expand <(5-sqrt(x))/x^2> should give 5x^(-2) - x^(-3/2); MS 5x^-2 - x^(-3/2).
- 7357/3 Jun22 Q8a: CAS simplify <pi/4*(288/pi)^(2/3)> should give 6(6pi)^(1/3); MS dV/dh = 6 cbrt(6 pi) = 15.97.

### 13. [solve-decimal] Decimal under exact roots in CAS solve (AWKWARD, 1 part, plus 8 OK rows that need Calculate)
CAS definite integral now prints a decimal; CAS solve exact and the Solve screen still do not.
Proposed: under each root that is not rational, print its decimal, as Definite integral does.
- 7357/2 Jun24 Q18a: CAS solve exact <-0.04*x*e^(-0.6)=-1.8> gives 45e^(3/5) and should also give 81.99; MS q = 82.0.
- 7357/1 Jun24 Q20c: <5+125e^(-0.012x)=65> gives -250ln(12/25)/3 and should give 61.16; MS 61 minutes.
- 7357/3 Jun24 Q8ci: <20(11-10e^(-x))=86> gives -ln(67/100) and should give 0.4005; MS k = 0.4005.

### 14. [solve-exp-exact] Two different bases (AWKWARD, 4 marks)
Proposed: c1 a^(px+q) = c2 b^(rx+s) -> take ln of both sides -> linear in x. This is the same code path as [solve-overflow].
- 7357/2 Nov21 Q6: CAS solve exact <5^x=3^(x+4)> should give x = 4ln3/(ln5 - ln3) = 8.6026; MS ln 81/(ln 5 - ln 3).

### 15. [implicit-tangent-exact] Exact tangent and intercepts (AWKWARD, 4 marks)
G/Implicit dy/dx now prints the tangent, normal and axis crossings, but in decimals.
Proposed: when x, y and dy/dx are exact, build the line and its intercepts in exact arithmetic (caseng), as the gradient already is.
- 7357/1 Nov20 Q12biii: G/Implicit dy/dx <x^3*sin(y)+cos(y)-2x,sqrt(3),pi/6> should give "tangent meets y = 0 at x = sqrt(3)+4pi/15"; MS sqrt(3) + 4pi/15.

### 16. [vt-unknown-time] One unknown breakpoint in v-t graph points (AWKWARD, 4 marks)
Proposed: allow one '?' time plus a given total displacement (a new optional field) and solve the area equation.
- 7357/2 Jun22 Q15: points (0,0), (5,4), (?,0), (10,-4), (15,-4) with displacement -7 should give t = 33/4; MS 8.25 s.

### 17. [proj-relation] Two projectiles with related speeds and angles (AWKWARD, 4 marks)
It is now possible in three steps: Calc, then Q/Projectile find u, then Q/Projectile launch. Low priority. A "time of flight for u, angle" line in Projectile find u, from the same u, would cut it to two steps.
- 7357/2 Nov21 Q18b: cos 2theta = 1/8, t_P = 0.4 should give t_Q = 1.2 s; MS 1.2 s.

### 18. [display-precision] 3 s.f. defaults that mislead (form)
- [sf-integer-look]: a value rounded to 3 s.f. that lands on an integer prints like an exact value: "= 16" for 15.968 in B/Simplify surd expr (7357/3 Jun22 Q8a, a show-that), and "(pi/3, 12)" for 11.96 (7357/3 Jun23 Q7bi). Print at least one decimal (16.0) or mark it with "~".
- [deg-1dp]: angles in degrees default to 3 s.f., so 104.48 prints as "104 deg" where the MS wants 104.5 (7357/1 Jun24 Q15bii; also 138 deg in Jun19/1 Q12b). Print degrees to 1 d.p.

### 19. [venn3-unknown] Three-set Venn from a "none" value (AWKWARD, 3 marks)
The same fix as the crash in item 7. Also print every region in one format; today it mixes 0.27 with 1/5 and 1/20 [venn3-mixed-format].
- 7357/3 Jun25 Q19b: <0.38,0.38,0.12,0.11,0,?,0,1> with none = 0.3 should give BC = 0.07 and regions 0.27, 0.2, 0.05, 0.11, 0, 0.07, 0; MS Venn values as listed.

### 20. [param-cart-simplify] Simplify a^(k ln u/ln a) (AWKWARD, 3 marks)
Proposed: simplify b^(c ln(u)/ln(b)) -> u^c. Offer the implicit polynomial form by clearing denominators.
- 7357/1 Jun18 Q5b: C/Param to Cartesian <4*2^(-t)+3,3*2^t-5> should give y = 12/(x-3) - 5 and xy + 5x - 3y = 27; MS xy + 5x - 3y = 27.

### 21. [pf-tool-junk] B/Partial fractions with fractional numerators (AWKWARD, 3 marks)
It prints "1/8/(4-3*x)+1/8/(3*x+4)", the double-fraction form named in the brief.
Proposed: print k/(ax+b) with a fractional k as num/(den(ax+b)).
- 7357/1 Jun23 Q16a: B/Partial fractions <1,16-9x^2> should give 1/(8(4-3x)) + 1/(8(3x+4)); MS A = B = 1/8.

### 22. [binom-exact] (a + b x^m)^n and letters in D/Binomial (AWKWARD, 2 marks, plus 4 OK-row notes)
- 7357/2 Jun19 Q9b: (4 - 2x^2)^(1/2) should be valid for |x| < sqrt(2); MS |x| < sqrt 2.
- 7357/1 Jun24 Q8a: D/Binomial (a+bx)^n <2,k,5> fails with "b: unknown k". It should give 32 + 80kx + 80k^2x^2 (MS). CAS expand already does.

### 23. [int-factor] Integer factorisation and primality (AWKWARD, 2 marks)
- 7357/2 Jun18 Q5: factor(23) should say "prime; tested 2, 3 (up to sqrt 23 = 4.80)"; MS 23 is prime.

### 24. [int-mod] mod, floor and digit functions (AWKWARD, 2 marks)
- 7357/2 Jun22 Q6a: A/Counterexample f=g <mod(n^2,10),mod(floor(n/10)+mod(n,10),10),10,99> should give n = 12 (144: 1 + 2 = 3, not 4); MS any counterexample such as 12^2 = 144.

### 25. Small readability items (noted in OK rows)
- [cas-deriv-collect]: CAS d/dx leaves like terms uncollected, e.g. (cos x - sin x)e^-x - (cos x + sin x)e^-x and 4x(x^2-5/2) + 2(x-3). G/Derivative f' and f'' collects them (Jun19/1 Q16a, Jun25/1 Q15a). Route CAS d/dx through the same collector.
- [calc-decimal-power]: Calculate prints an "exact" line for a decimal power: 10*10^(22/25) for 10^1.88, e^(919/250) for e^3.676, 31log(1/4)/5 + 86/25 (Nov21/1 Q9cii, Jun25/1 Q10bi, Jun23/2 Q6ai, Jun24/2 Q8b, Jun22/3 Q7aii). Skip the exact line when the input had a decimal exponent.
- [calc-long-fraction]: Calculate still prints a 30-digit fraction under 467.8918345 for 57.5*1.14^16 (Jun23/2 Q6ci).
- [complex-format]: "-9/8+sqrt(15)/8i" reads as division by 8i (Nov20/3 Q4bi). CAS solve prints "(4i*sqrt(3)-4)/4" uncancelled [complex-root-cancel] (Jun24/1 Q19).
- [neg-one-coef]: "f'(x) = -1*e^(x-1)" (Nov20/2 Q1).
- [line-decimal-form]: C/Line through 2 points prints "(51/20)x - (17/10)y - 1.19 = 0" as its "integer form" (Jun22/3 Q7ai).
- [g-name-clash]: H/Separable DE prints "int 1/g(y) dy" when g is also the user's letter (Nov21/2 Q17b).
- [log-solve-other-var]: F/Evaluate log expr solves only for x; typed with y as in the paper, it combines the logs but does not solve (Jun18/3 Q7a).
- [inverse-domain-text]: B/Inverse function says "domain all real x" for (x^2+10)/(2x+5) (Jun22/3 Q10b).
- [cas-rationalise-surd] / [rationalise-cancel]: CAS rationalise leaves sqrt(16x^2) and does not cancel (4-2sqrt3)/4. B/Rationalise and B/Simplify surd expr already get these right (Jun24/1 Q7, Jun18/2 Q8b).
- [nr-labels]: Newton-Raphson has no i0 field, so its labels are one off from the MS (Jun18/1 Q8b).
- Letters are lowercased in answers (W -> w, R -> r, T -> t): Nov20/2 Q9b, Q13a; Jun22/2 Q14a.

## Status of the 74 pass-1 fix keys

- **Fixed (54):** param-letters, sep-exact-c (c exact; see solved-form-tidy for the form), mech-solve-unknown, solve-range, simul-nonlin, subst-x-remains, log-symbolic (see eq-sign-multiplies), moments-unknown, int-normalise, range-infinite, foot-perp, surd-algebra (B tool), domain, log-combine, exactstr-silly, slope-angled-force, firstprin-symbolic, trig-exact-other, inverse-one-one, defint-decimal, sigma-symbolic, simplify-monic-power, tri-radians, defint-tool-exact, limit-inf-exp, vec-a-to-v, trap-data, quad-vectors, stat-exact, line-integer-form, proj-landing-speed, vec-exact-speed, slope-moving-up, pmcc-table-n, identity-domain, circle-centre-line, gp-exact, inverse-mobius, stats-sxx-input, arc-exact, linquad-exact, snap-zero, range-corner, loglin-base, factor-thm-float, beam-no-loads, solve-crash-power, cbrt-negative, circle-axes, trig-undefined-root, recur-converge, recur-n-limit, vec-suvat-symbolic, incdec-domain-edge.
- **Partly fixed (10):** pf-monic (B tool junk for fractional numerators), deriv-simplify (G only, not CAS), surd-power-simplify (1 of 3 parts), vt-cumulative (cumulative s done, unknown time not), proj-unknown-u (Jun18/2 Q16a done, Nov21/2 Q18b in 3 steps), venn3 (Jun22/3 Q16a done, Jun25/3 Q19b needs a value by hand), binom-exact (exact coefficients done, x^m not), rationalise-cancel (B tool right, CAS not), subst-reverse (accepted, output untidy), implicit-tangent (tangent there, decimals only).
- **Untouched (10):** solve-decimal, exp-form, defint-symbolic-limits, trig-simplify-factor, solve-exp-exact, param-cart-simplify, int-trig-sub, solve-overflow, int-factor, int-mod.

Smaller items that pass 1 had only as notes are also fixed: expmodel-predict, circle-point, circle-area, hist-fd-input, ap-first-last, beam-g, sig-percent-trap, outlier-given-q, iter-labels (Fixed point i0).

## New OK cases (JSON lines)

Format as `tests_pastpapers_aqa.CASES`: [paper, q, module, label, inputs, expected substring, ask, deg, full]. 174 cases, one for each new or changed OK row, each checked against the current output. CAS follow-up answers are in the ask field.

```
["73571-jun18", "6a", "mpure:D", "Binomial rational n", "4,1,-1/2", "x^2: 3/256", null, false, false]
["73571-jun18", "6c", "casui:CAS", "definite integral a..b", "1/2+x^3/16+3x^6/256", "0.5172991071", "0,1", false, true]
["73571-jun18", "6c", "mcalc:H", "Definite integral", "1/2+x^3/16+3x^6/256,0,1", "927/1792", null, false, false]
["73571-jun18", "9b", "mpure:B", "Simultaneous non-linear", "x+5y-25,4x+70y-4x^2-20x*y-25y^2", "(x, y) = (-55, 16)", null, false, false]
["73571-jun18", "9b", "mpure:B", "Solve f(x)=g(x)", "4x+14(25-x),4x^2+4x(25-x)+(25-x)^2", "(-55, 900)", null, false, false]
["73571-jun18", "10a", "mpure:F", "N = A e^(kt) 2 pts", "0,400,5.7,200,4", "N(4) = 246", null, false, false]
["73571-jun18", "10b", "mpure:F", "N = A e^(kt) 2 pts", "0,400,5.7,200,?,280", "N = 280 at t = 2.93", null, false, false]
["73571-jun18", "11b", "mpure:B", "Solve f(x)=g(x)", "10+100(x/30)^3-50(x/30)^4,4.5*1.063^x", "49.00908623", null, false, true]
["73571-jun18", "12a", "mpure:B", "Factor theorem", "30x^3-7x^2-7x+2,-1/2", "(2x + 1) is a factor", null, false, false]
["73571-jun18", "15a", "mcalc:G", "First principles", "x^3-48x,-4", "at x = -4: h^2-12*h", null, false, false]
["73571-jun18", "7bii", "mpure:C", "Point and circle", "3,5,13,-8,-2", "outside the circle", null, false, false]
["73571-jun19", "6a", "mpure:B", "Range of f on [a,b]", "(x^2+1)/2,0,?", "range: f(x) >= 1/2", null, false, false]
["73571-jun19", "6bi", "mpure:B", "Inverse function", "(x^2+1)/2,0,?", "domain of f-1: x >= 1/2", null, false, false]
["73571-jun19", "7di", "mcalc:I", "Fixed point x=g(x)", "acos(x)/2,0.4,3,1", "x2 = 0.57963974", null, false, false]
["73571-jun19", "12b", "mpure:E", "Exact ratios from one", "2/3,?,?,2", "tan x = -2*sqrt(5)/5", null, false, false]
["73571-jun19", "12b", "casui:CAS", "solve exact f(x)=0", "4/sin(x)^2-4/sin(x)-3", "x = -asin(2/3)+pi", null, false, false]
["73571-jun19", "13", "mcalc:G", "Stationary points", "e^(3x-5)/x^2", "f'(x) = (3*x-2)*e^(3*x-5)/x^3", null, false, false]
["73571-jun19", "15ai", "casui:Calculate", "Calculate", "3-2*(0-3)^(1/3)", "5.884499141", null, false, false]
["73571-jun19", "15ai", "casui:CAS", "evaluate at x", "3-2*(x-3)^(1/3)", "f(0) = 5.88", "0", false, false]
["73571-jun19", "16a", "mcalc:G", "Derivative f' and f''", "e^(-x)*(sin(x)+cos(x))", "f'(x) = -2*e^(-x)*sin(x)", null, false, false]
["73571-jun19", "14b", "mcalc:H", "Definite integral", "2x^3/(x^2+1),0,4", "integral = -ln(17)+16", null, false, false]
["73571-nov20", "7aii", "mpure:D", "Recurrence u(n+1)", "3-u^2,2,50", "u(50) = -1", null, false, false]
["73571-nov20", "8b", "mpure:B", "Inequality f(x) > g(x)", "3.87sin(2pi(x+101.75)/365)+11.7,14,0,500", "300.220275 < x < 408.779725", null, false, true]
["73571-nov20", "8b", "mpure:B", "Inequality f(x) > g(x)", "3.87sin(2pi(x+101.75)/365)+11.7,14", "too many crossings", null, false, false]
["73571-nov20", "10bi", "mpure:D", "Sigma sum f(r) a..b", "b*r+c,10,100", "sum = 5005*b+91*c", null, false, false]
["73571-nov20", "13ai", "mpure:B", "Inverse function", "(2x+3)/(x-2)", "f-1(x) = (2*x+3)/(x-2)", null, false, false]
["73571-nov20", "13c", "mpure:B", "Composite fg and gf", "(2x+3)/(x-2),(2x^2-5x)/2,?", "(-x^2+29*x/2+24)/(x-2)^2", null, false, false]
["73571-nov20", "15", "casui:CAS", "solve exact f(x)=0", "e^x=6-e^(x/2)", "x = 2*ln(2)", null, false, false]
["73571-nov20", "15", "mcalc:H", "Area between curves", "e^x,6-e^(x/2),0,ln(4)", "area = 6*ln(4)-5", null, false, false]
["73571-nov21", "5b", "mpure:C", "Foot of perpendicular", "-4,3,21,15,2", "foot (3, 11)", null, false, false]
["73571-nov21", "5b", "mpure:C", "Foot of perpendicular", "-4,3,21,15,2", "distance = 15", null, false, false]
["73571-nov21", "9ci", "mpure:F", "Log-lin fit y=kb^x", "0,75,5,94,10,120,15,156,20,206,25,260", "log10: gradient = 0.0219", null, false, false]
["73571-nov21", "13a", "mpure:B", "Factor theorem", "125x^3+150x^2+55x+6,-1/5", "(5x + 1) is a factor", null, false, false]
["73571-nov21", "15b", "casui:CAS", "definite integral a..b", "sqrt(16x^3)", "integral = 1/20", "0,0.25", false, false]
["73571-nov21", "10b", "mcalc:H", "Area between curves", "1,tan(x)^2,-pi/4,pi/4", "area = pi-2", null, false, false]
["73571-jun22", "8ai", "mpure:C", "Foot of perpendicular", "5,3,83,0,5", "foot (10, 11)", null, false, false]
["73571-jun22", "8ai", "mpure:C", "Foot of perpendicular", "5,3,83,0,5", "distance = 2*sqrt(34)", null, false, false]
["73571-jun22", "10ciii", "mcalc:G", "f, f' and f'' at a", "x-sin(2x),pi/6", "f'(pi/6) = 0", null, false, false]
["73571-jun22", "15aiii", "mpure:E", "Identity check (rad)", "sqrt(1/sin(x)^2-1)*sin(x),cos(x),0,pi/2", "holds at every x tested", null, false, false]
["73571-jun23", "7a", "mpure:B", "Simplify surd expr", "7/(3+5sqrt(x))-7/(5sqrt(x)-3)", "-42/(25*x-9)", null, false, false]
["73571-jun23", "9aii", "mpure:C", "Perpendicular bisect", "-6,15,12,19", "9x + 2y - 61 = 0", null, false, false]
["73571-jun23", "9bi", "mpure:C", "Circle, centre on line", "-6,15,12,19,2,-5,-30", "(x - 5)^2 + (y - 8)^2 = 170", null, false, false]
["73571-jun23", "9bii", "mpure:C", "Circle, centre on line", "-6,15,12,19,2,-5,-30", "meets the y axis at y = 8-sqrt(145), sqrt(145)+8", null, false, false]
["73571-jun23", "10bii", "mpure:E", "Exact ratios from one", "-3/7,?,?,3", "cos x = -2*sqrt(10)/7", null, false, false]
["73571-jun23", "14bii", "mpure:D", "Geometric a,r,n", "sqrt(2)/4,sqrt(2)/2,8", "S(8) = 15*sqrt(2)/32+15/32", null, false, false]
["73571-jun23", "16a", "casui:CAS", "partial fractions", "1/(16-9x^2)", "1/(8*(3*x+4))", null, false, false]
["73571-jun24", "3", "mpure:B", "Divide p(x) by d(x)", "12x^2+3x+7,3x-5", "quotient = 4*x+23/3", null, false, false]
["73571-jun24", "7", "mpure:B", "Simplify surd expr", "(3+sqrt(8x))/(1+sqrt(2x))", "(4*x-3+sqrt(2*x))/(2*x-1)", null, false, false]
["73571-jun24", "10a", "mpure:D", "AP sum, first and last", "300,-7,32", "S(300) = 3750", null, false, false]
["73571-jun24", "15bii", "mpure:E", "Solve trig eqn (deg)", "sin(2x)/sin(x)+cos(2x)/cos(x)-3,0,360", "2 root(s) in 0 to 360", null, false, true]
["73571-jun24", "15bii", "mpure:E", "Solve trig eqn (deg)", "sin(2x)/sin(x)+cos(2x)/cos(x)-3,0,360", "x = 255.5224878 deg", null, false, true]
["73571-jun24", "16", "mcalc:I", "Trapezium from y values", "0.4,-3,-2.943,-2.752,-2.353,-1.572,0", "T = -4.448", null, false, false]
["73571-jun24", "17a", "mpure:B", "Range of f on [a,b]", "abs(x)+1,?,?", "range: f(x) >= 1", null, false, false]
["73571-jun24", "17a", "mpure:B", "Range of f on [a,b]", "abs(x)+1,-10,10", "range: 1 <= f(x) <= 11", null, false, false]
["73571-jun24", "17b", "mpure:B", "Domain of f(x)", "ln(x)", "domain: x > 0", null, false, false]
["73571-jun24", "17cii", "mpure:B", "Inverse function", "ln(abs(x)+1)", "many-to-one: no inverse", null, false, false]
["73571-jun24", "18a", "mcalc:H", "Substitution u=g(x)", "(4x+1)sqrt(2x+1),2x+1,0,4", "in u: int sqrt(u)*u-sqrt(u)/2 du", null, false, false]
["73571-jun24", "18a", "mcalc:H", "Substitution u=g(x)", "(4x+1)sqrt(2x+1),2x+1,0,4", "integral = 1322/15", null, false, false]
["73571-jun24", "19", "mcalc:G", "Implicit dy/dx = 0", "y^3*e^(2x)+2y-16x-k,0", "y = 2, k = 12", null, false, false]
["73571-jun24", "20b", "mcalc:H", "Separable DE at point", "-0.012,y-5,0,130", "y = 125*e^(-3*x/250)+5", null, false, false]
["73571-jun25", "2", "mpure:D", "Recurrence u(n+1)", "-u/4,32,6", "converges to L = 0", null, false, false]
["73571-jun25", "3", "mpure:F", "Evaluate log expr", "logb(3,2x)-logb(3,x)", "= logb(3,2)", null, false, false]
["73571-jun25", "12a", "mpure:B", "Range of f on [a,b]", "x^2+5,?,?", "range: f(x) >= 5", null, false, false]
["73571-jun25", "12b", "mpure:B", "Inverse function", "x^2+5", "f(-1) = f(1) = 6", null, false, false]
["73571-jun25", "12dii", "mpure:B", "Range of f on [a,b]", "sqrt(x^2+5),?,?", "range: f(x) >= sqrt(5)", null, false, false]
["73571-jun25", "15a", "mcalc:G", "Derivative f' and f''", "(x-3)^2+(x^2-2.5)^2", "f'(x) = 4*x^3-8*x-6", null, false, false]
["73571-jun25", "17a", "mcalc:H", "Substitution u=g(x)", "e^(2x)/(e^x+1),e^x+1", "in u: int (u-1)/u du", null, false, false]
["73571-jun25", "17b", "mcalc:H", "Separable DE at point", "e^(2x)/(e^x+1),cos(y)^2,0,pi", "tan(y) = ln(2/(e^(x)+1))+e^(x)-1", null, false, false]
["73572-jun18", "7", "mcalc:H", "Indefinite integral", "(x-1)e^x", "e^(x)*x-2*e^(x)+c", null, false, false]
["73572-jun18", "7", "mcalc:H", "Separable DE at point", "(x-1)e^x,1,1,e", "c = 2*e", null, false, false]
["73572-jun18", "8bi", "mpure:B", "Rationalise", "1,0,1,4,2,3", "(2-sqrt(3))/2", null, false, false]
["73572-jun18", "8bii", "mpure:B", "Rationalise", "1,0,1,4,-2,3", "(2+sqrt(3))/2", null, false, false]
["73572-jun18", "12b", "mmech:Q", "v-t graph points", "0,0,4,-2,6,2,11,2,12,0,13,-4,16,-4,20,0", "back at s = 0 at t = 8, 14.25", null, false, false]
["73572-jun18", "16a", "mmech:Q", "Projectile find u", "35,1.5,?,?,9.81", "u = 25.6548196 m/s", null, false, true]
["73572-jun18", "17ai", "mmech:R", "Tow bar in a line", "410,72,300,140,?,0.2", "R2 = 63.6 N", null, false, false]
["73572-jun18", "14b", "mcalc:J", "Quadrilateral ABCD", "3,5,1,-1,2,7,0,7,6,4,10,0", "parallelogram", null, false, false]
["73572-jun19", "2", "mpure:B", "Simplify surd expr", "sqrt(x^(2/3)*x^(2/5))", "x^(8/15)", null, false, false]
["73572-jun19", "3", "mpure:B", "Inverse function", "x^2", "many-to-one: no inverse", null, false, false]
["73572-jun19", "5", "mcalc:H", "Separable DE at point", "ln(x)/x^2,1/y,1,2", "y^2/2 = -ln(x)/x-1/x + 3", null, false, false]
["73572-jun19", "6", "mpure:B", "Simultaneous non-linear", "x^2+y^2-16,sqrt(3)/2*x+y/2-2sqrt(3)", "(x, y) = (2, 2sqrt(3))", null, false, false]
["73572-jun19", "7bi", "mpure:B", "Factorise", "3x^2+6p*x", "= 0 at x = 0, -2*p", null, false, false]
["73572-jun19", "7bi", "mcalc:G", "Stationary points", "x^3+3*p*x^2+q", "max at (-2*p, 4*p^3+q)", null, false, false]
["73572-jun19", "8b", "mpure:F", "y = k b^x from 2 pts", "0,10^3.9,40,10^5.28", "7943.282347*1.08268^x", null, false, false]
["73572-jun19", "9c", "casui:CAS", "definite integral a..b", "1-x^2/4", "integral = 0.3946666667", "0,0.4", false, true]
["73572-jun19", "14a", "mmech:S", "Moments: find unknown", "0.28*0.03,F*0.04", "f = 0.21", null, false, false]
["73572-jun19", "14b", "mmech:S", "Moments: find unknown", "0.21*0.04,0.048*n*0.05", "n = 3.5", null, false, false]
["73572-jun19", "15a", "mcalc:J", "Quadrilateral ABCD", "410,710,0,-210,530,0,-340,-310,0,590,-40,0", "AB parallel to DC, DC = 3/2 AB", null, false, false]
["73572-nov20", "1", "mcalc:G", "Increasing/decreasing", "-e^(x-1)", "decreasing for all x", null, false, false]
["73572-nov20", "5", "mcalc:H", "Substitution u=g(x)", "x*sqrt(4x+1),4x+1,-1/4,6", "in u: int sqrt(u)*u/16-sqrt(u)/16 du", null, false, false]
["73572-nov20", "5", "mcalc:H", "Substitution u=g(x)", "x*sqrt(4x+1),4x+1,-1/4,6", "integral = 875/12", null, false, false]
["73572-nov20", "6a", "mpure:C", "Foot of perpendicular", "12,5,298,7,9", "foot (19, 14)", null, false, false]
["73572-nov20", "6a", "mpure:C", "Foot of perpendicular", "12,5,298,7,9", "distance = 13", null, false, false]
["73572-nov20", "9b", "mcalc:G", "Stationary points", "pi*R^2*x-pi*x^3", "max at (r*sqrt(3)/3, 2*pi*r^3*sqrt(3)/9)", null, false, false]
["73572-nov20", "13a", "mmech:S", "Moments: find unknown", "2*W,1.5*4*g", "w = 3*g", null, false, false]
["73572-nov20", "14a", "mmech:Q", "Vector r(t) to v, a", "t^3-5t^2,8t-t^2,2", "speed = 4sqrt(5) m/s", null, false, false]
["73572-nov20", "18a", "mmech:R", "Slope and pulley", "0.2,16.26020471,?,2,9.81,543*9.81/625", "mu = 0.17", null, false, false]
["73572-nov20", "18bi", "mmech:R", "Rough slope", "0.2,16.26020471,0.17,0,9.81,?,0.5", "stops after 0.115 s, 0.0288 m up", null, false, false]
["73572-nov20", "15a", "mcalc:I", "Trapezium from y values", "20,131,140,120,80,0", "T = 8110", null, false, false]
["73572-nov21", "5", "mpure:B", "Partial fractions", "5(x-3),(2x-11)(4-3x)", "1/(4-3*x)-1/(2*x-11)", null, false, false]
["73572-nov21", "7ai", "mpure:C", "Circle from general", "-6,-8,-p", "centre (3, 4)", null, false, false]
["73572-nov21", "7aii", "mpure:C", "Circle from general", "-6,-8,-p", "radius = sqrt(p+25)", null, false, false]
["73572-nov21", "10a", "mpure:B", "Domain of f(x)", "sqrt(x)/(x-3)", "domain: x >= 0, x != 3", null, false, false]
["73572-nov21", "17b", "mcalc:H", "Separable DE at point", "1,g-0.1y,0,0", "y = 10*(-e^(-x/10)*g+g)", null, false, false]
["73572-nov21", "18b", "mmech:Q", "Projectile find u", "acos(1/8)/2,0.2,?,?,9.8", "u = 2.96 m/s", null, true, false]
["73572-nov21", "18b", "mmech:Q", "Projectile launch", "5.92296,82.81924422,0,9.8", "time of flight = 1.2 s", null, false, false]
["73572-nov21", "17c", "casui:CAS", "limit x -> a", "10*9.8*(1-e^(-0.1x))", "98", "inf", false, false]
["73572-jun22", "9", "mpure:F", "Evaluate log expr", "logb(2,x^3)-logb(2,y^2)-9", "f = 0: x = 8*y^(2/3)", null, false, false]
["73572-jun22", "14a", "mmech:S", "Moments: find unknown", "12*66,80*T", "t = 9.9", null, false, false]
["73572-jun22", "16bi", "mmech:Q", "Vector SUVAT", "-4,5,0,0,3,-4,?", "r = (3*t^2/2-4, -2*t^2+5)", null, false, false]
["73572-jun22", "19a", "mmech:R", "Rough slope", "20,25,?,230,9.8,1.2", "mu = 0.693", null, false, false]
["73572-jun23", "6ci", "casui:Calculate", "Calculate", "57.5*1.14^16", "467.8918345", null, false, false]
["73572-jun23", "7b", "mpure:B", "Domain of f(x)", "1/sqrt(10-2x)", "domain: x < 5", null, false, false]
["73572-jun23", "8b", "mpure:B", "Range of f on [a,b]", "2/sin(x)^2,0,pi", "range: f(x) >= 2", null, false, false]
["73572-jun23", "14", "mmech:Q", "a(t) to v and s", "3k*t^2-2k*t+1,1,0,3", "v(3) = 18*k+4 m/s", null, false, false]
["73572-jun23", "15", "mmech:R", "Friction horizontal", "0.65/9.8,0.4,?,0,9.8,0.91", "P = 0.32 N", null, false, false]
["73572-jun23", "17ai", "mmech:S", "Moments: find unknown", "4*g*3.6,M*g*1.5", "m = 9.6", null, false, false]
["73572-jun23", "17ai", "mmech:S", "Beam on two supports", "7,9.6,1.4,5", "R at 1.4 m = 39.2 N = 4g", null, false, false]
["73572-jun23", "19a", "mmech:R", "Tow bar in a line", "1.5,0.7,2cos(40),0.8,?,0.06", "R2 = 0.6 N", null, true, false]
["73572-jun24", "4", "casui:Calculate", "Calculate", "2+1570*logb(5,7)", "1900.22727", null, false, false]
["73572-jun24", "7bi", "mpure:D", "Geometric a,r,n", "50.1,1.002,120", "S(120) = 6790", null, false, false]
["73572-jun24", "9b", "mpure:B", "Partial fractions", "36x,(1+3x)(2-3x)", "-4/(1+3*x)+8/(2-3*x)", null, false, false]
["73572-jun24", "9ci", "casui:CAS", "series (Maclaurin)", "12x/((1+3x)(2-3x))", "-9*x^2+6*x", "3", false, false]
["73572-jun25", "9di", "mpure:C", "Triangle 3 vertices", "6,10,12,-8,18,10", "in rad: A = 1.25, B = 0.644, C = 1.25", null, false, false]
["73572-jun25", "14", "mmech:Q", "Projectile launch", "sqrt(40^2+25^2),atan(25/40),2.5,9.8", "speed 47.7 m/s", null, true, false]
["73572-jun25", "16a", "mmech:R", "Slope, pull at angle", "10,20,30,?,0,0,15,9.8", "P = 56 N", null, false, false]
["73572-jun25", "16b", "mmech:R", "Slope, pull at angle", "10,20,30,54,0.2,?,0,9.8", "a = 0.0229 m/s^2", null, false, false]
["73572-jun25", "19a", "mmech:Q", "Vector r(t) to v, a", "2t^3,2t^2+q*t,?", "v = (6*t^2)i + (q+4*t)j", null, false, false]
["73572-jun25", "19b", "mmech:Q", "Vector a(t) to v, r", "6t,7,0,4,0,0,2", "v(2) = (12, 18) m/s", null, false, false]
["73572-jun25", "19b", "casui:CAS", "solve exact f(x)=0", "24/12=(8+x)/18", "x = 28", null, false, false]
["73572-jun25", "18a", "mmech:S", "Beam on two supports", "2.5,400/9.81,0,0.6,2.3,30,9.81", "R at 0.6 m = 1960 N", null, false, false]
["73573-jun18", "1", "mpure:C", "Circle centre+radius", "0,0,3", "area = 9pi", null, false, false]
["73573-jun18", "6a", "mpure:B", "Domain of f(x)", "x/sqrt(2x-2)", "domain: x > 1", null, false, false]
["73573-jun18", "6b", "mcalc:G", "Derivative f' and f''", "x/sqrt(2x-2)", "f'(x) = (x-2)/(2*x-2)^(3/2)", null, false, false]
["73573-jun18", "6d", "mcalc:G", "Inflection points", "x/sqrt(2x-2)", "convex for 1 < x < 4", null, false, false]
["73573-jun18", "7a", "mpure:F", "Evaluate log expr", "logb(a,x)-2logb(a,7)-logb(a,4)-1/2", "f = 0: x = 196*sqrt(a)", null, false, false]
["73573-jun18", "9b", "mpure:D", "Geometric a,r,n", "1,1/sqrt(2),10", "S(inf) = sqrt(2)+2", null, false, false]
["73573-jun18", "12", "mstat:L", "Grouped from fd", "155,160,0.8,160,170,2.4,170,180,2,180,190,1", "median = 170", null, false, false]
["73573-jun18", "17a", "mstat:O", "HT binomial two tail", "10,0.5,7,0.1", "sig 0.1 read as 10%", null, false, false]
["73573-jun19", "8a", "mpure:B", "Simultaneous non-linear", "5*(4+x)-75,5*(4+x*e^(-2*y))-68", "(x, y) = (11, -ln(48/55)/2)", null, false, false]
["73573-jun19", "8a", "casui:Calculate", "Calculate", "5(4+11e^(-15*0.0680660))", "39.8", null, false, false]
["73573-jun19", "8bi", "casui:CAS", "limit x -> a", "5(4+11e^(-0.068066x))", "20", "inf", false, false]
["73573-jun19", "8bii", "casui:CAS", "solve exact f(x)=0", "5(4+11e^(-0.068066x))=21", "x = 58.874228", null, false, false]
["73573-jun19", "9bii", "mcalc:G", "Implicit dy/dx = 0", "x^2*y^2+x*y^4-12", "no point with dy/dx = 0 found", null, false, false]
["73573-jun19", "9biii", "mcalc:G", "Implicit dy/dx", "x^2*y^2+x*y^4-12,3,1", "tangent y = -7*x/30+17/10", null, false, false]
["73573-jun19", "1", "mpure:B", "Domain of f(x)", "asin(x)", "domain: -1 <= x <= 1", null, false, false]
["73573-nov20", "5a", "casui:CAS", "solve exact f(x)=0", "e^(-0.0435935x)=0.1", "x = 52.819459", null, false, false]
["73573-nov20", "8a", "mpure:B", "Simultaneous non-linear", "x/(1-y)-96,x*y-18", "(x, y) = (72, 1/4)", null, false, false]
["73573-nov20", "8bii", "mpure:F", "Evaluate log expr", "logb(3,3^x/2^(2x-5))", "= x-(2*x-5)*logb(3,2)", null, false, false]
["73573-nov21", "6", "mpure:B", "Simplify surd expr", "(10+5x-2sqrt(x)-x^(3/2))/(5-sqrt(x))", "x+2", null, false, false]
["73573-nov21", "7d", "mpure:D", "Geometric a,r,n", "30,0.98,15", "S(inf) = 1500", null, false, false]
["73573-jun22", "7b", "mpure:B", "Solve f(x)=g(x)", "0.2*x^1.5,60000", "(4480, 60000)", null, false, false]
["73573-jun22", "7b", "casui:CAS", "solve exact f(x)=0", "0.2*x^1.5=60000", "x = 4481.404747", null, false, false]
["73573-jun22", "10d", "mcalc:G", "Stationary points", "(x^2+10)/(2x+5)", "min at ((sqrt(65)-5)/2, (sqrt(65)-5)/2)", null, false, false]
["73573-jun22", "10e", "mpure:B", "Range of f on [a,b]", "(x^2+10)/(2x+5),?,?", "range: f(x) <= (-5-sqrt(65))/2 or f(x) >= (sqrt(65)-5)/2", null, false, false]
["73573-jun22", "16a", "mstat:M", "Three-set Venn", "153,70,45,48,21,32,17,240", "only A = 101", null, false, false]
["73573-jun22", "16a", "mstat:M", "Three-set Venn", "153,70,45,48,21,32,17,240", "none = 56", null, false, false]
["73573-jun22", "18c", "mstat:L", "Stats from summary", "40,69.2,?,2.81", "sd (n) = 0.265", null, false, false]
["73573-jun22", "10a", "mpure:B", "Domain of f(x)", "(x^2+10)/(2x+5)", "domain: x != -5/2", null, false, false]
["73573-jun22", "10b", "mpure:B", "Inverse function", "(x^2+10)/(2x+5)", "f(-7) = f(-55/9) = -59/9", null, false, false]
["73573-jun23", "8", "mcalc:H", "Substitution u=g(x)", "x^9/(x^5+2)^3,x^5+2,0,1", "in u: int (u/5-2/5)/u^3 du", null, false, false]
["73573-jun23", "8", "mcalc:H", "Substitution u=g(x)", "x^9/(x^5+2)^3,x^5+2,0,1", "integral = 1/180", null, false, false]
["73573-jun23", "15ai", "mstat:L", "Outlier limits", "1167,1393,1570", "median -+ 1.5 IQR = 788.5 to 1997.5", null, false, false]
["73573-jun24", "5", "mpure:E", "Arc and sector (rad)", "18,pi/6", "segment area = 27*pi-81", null, false, false]
["73573-jun24", "7b", "mpure:B", "Line meets quadratic", "-1,1,-2,3,2", "((2-sqrt(6))/2, sqrt(6)/2)", null, false, false]
["73573-jun24", "9d", "mpure:C", "Triangle 3 vertices", "-4,6,0,9,9,-3", "in rad: A = 1.25", null, false, false]
["73573-jun24", "10", "mcalc:G", "First principles", "5x^3+x,0", "(f(x+h) - f(x))/h = 5*h^2+15*h*x+15*x^2+1", null, false, false]
["73573-jun24", "11", "casui:CAS", "definite integral a..b", "(x^2-8x)ln(x)", "-256*ln(2)+623/9", "1,8", false, false]
["73573-jun24", "16", "mstat:O", "PMCC test 1 tail", "-0.45,50,2.5", "critical value = 0.2787", null, false, false]
["73573-jun25", "4b", "mpure:F", "Evaluate log expr", "logb(a,sqrt(a))-logb(a,1/a^2)", "= 5/2", null, false, false]
["73573-jun25", "7", "mpure:D", "Sigma sum f(r) a..b", "a*r+5,1,3", "sum = 6*a+15", null, false, false]
["73573-jun25", "8a", "mpure:B", "Partial fractions", "x,2x^2+3x+1", "1/(x+1)-1/(2*x+1)", null, false, false]
["73573-jun25", "8b", "casui:CAS", "definite integral a..b", "x/(2x^2+3x+1)", "ln(5/3)", "0,4", false, false]
["73573-jun25", "9b", "mpure:B", "Domain of f(x)", "3/(x-4)", "domain: x != 4", null, false, false]
["73573-jun25", "9c", "mcalc:I", "Sign change table", "3/(x-4)-x,3,5,2", "f undefined at x = 4", null, false, false]
```
