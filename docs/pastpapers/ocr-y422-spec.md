# OCR Y422 Statistics Major, specimen (SAM) — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1(i) | 1 | 3!/27 | `CALC » Calculate » 3*2*1/27` | OK | ⇒ "2/9" |
| 1(ii) | 1 | P(X = 6) = 1 - rest | — | none | trivial |
| 1(iii) | 5 | E(X), Var(X) | `fstat » DRV from table » 3,2/9,4,2/9,5,14/81,6,31/81` | OK | ⇒ "Var(X) = 1.41"; E(X) shown 4.72, exact 382/81 not given even though inputs are fractions |
| 2(i)(A) | 2 | sketch | — | none | |
| 2(i)(B) | 3 | a = 1/3 | `fstat » Piecewise pdf » 1/3,1/3+x^2,-1,0,1` | GAP | additive unknown a cannot be solved for; verifies a = 1/3 ("valid pdf: yes") |
| 2(ii)(A) | 2 | P(X < ½) = 13/24 | `CAS » definite integral a..b » 1/3+x^2 ; 1/2,1` | AWKWARD | ⇒ "11/24" for the upper piece; no P(c<X<d) across pieces, so 1/3 + int_0^½ assembled by hand |
| 2(ii)(B) | 2 | mean | `fstat » Piecewise pdf » 1/3,1/3+x^2,-1,0,1` | OK | ⇒ "E(X) = 1/4" |
| 2(iii) | 3 | median equation | `fstat » Piecewise pdf » 1/3,1/3+x^2,-1,0,1` | OK | ⇒ "median = 0.424"; equation 2m^3 + 2m - 1 = 0 by hand |
| 3(i) | 3 | residual at (24, 11) | `CALC » Calculate » 11-(17.138-0.3727*24)` | OK | ⇒ "2.8068"; point read from the graph |
| 3(ii) | 4 | predictions | `CALC » Calculate » -0.3727*26+17.138` | OK | ⇒ "7.4478" |
| 3(iii) | 2 | effect sizes | — | none | |
| 3(iv) | 2 | linear model | — | none | |
| 4(i) | 1 | first five on 4th | `fstat » Geometric P(X=r) » 1/6,4` | OK | ⇒ "P(X=r) = 0.0965" |
| 4(ii) | 2 | at least once in 4 | `fstat » Geometric P(X=r) » 1/6,4` | OK | ⇒ "P(X<=r) = 0.518" |
| 4(iii) | 2 | second five on 3rd roll | `fstat » Binomial P(X=k) » 2,1/6,1` | AWKWARD | ⇒ "P(X=k) = 0.278"; × 1/6 by hand (0.0463); no negative binomial |
| 4(iv) | 2 | at least 2 in 3 | `fstat » Binomial P(X=k) » 3,1/6,2` | OK | ⇒ "P(X>=k) = 0.0741" |
| 4(v) | 3 | expected rolls for 2 fives | `fstat » Geometric P(X=r) » 1/6,4` | AWKWARD | ⇒ "mean 1/p = 6"; doubled by hand |
| 5(i) | 3 | 5 small < 2550 | `fstat » nX vs X1+..+Xn » 508,10.89,5,2550` | OK | ⇒ "P(sum<k) = 0.912" |
| 5(ii) | 4 | L - 3S > 0 | `fstat » aX+bY+c » 1,-3,0,1515,22.09,508,10.89,0` | OK | ⇒ "P(W>k) = 0.206" |
| 6(i) | 2 | choose test | — | none | |
| 6(ii) | 1 | 1-tail | — | none | |
| 7(i) | 3 | choose t test | — | none | |
| 7(ii) | 8 | one-sample t test | `fstat » z test from data » 110.2,?,5,2,116.9,114.9,110.9,113.9,114.9,117.9,112.9,99.9,114.9,103.9,123.9,105.7,108.9,102.9,112.7` | GAP | statistic 0.891 matches but crit ±1.96 (z) not t14 = 2.145; also "H0: mu = 110" prints 110.2 at 3 s.f.; no t test |
| 8(i) | 2 | conditions | — | none | |
| 8(ii)(A) | 1 | P(0), Po(1.1) | `fstat » Poisson P(X=k) » 1.1,0` | OK | ⇒ "P(X=k) = 0.333" |
| 8(ii)(B) | 2 | Po(66), P(>= 60) | `fstat » Poisson P(X=k) » 66,60` | OK | ⇒ "P(X>=k) = 0.786" |
| 8(iii) | 3 | P(X > 8) × 1000 | `fstat » Poisson P(X=k) » 1.1,8` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 2.43e-6" |
| 8(iv) | 4 | Po(4.5), 1 - P(<= 8)^10 | `fstat » Poisson P(X=k) » 4.5,8` | OK | ⇒ "P(X<=k) = 0.96" |
| 8(iv) | | | `CALC » Calculate » 1-0.95974^10` | OK | ⇒ "0.3369657595" |
| 9(i) | 3 | n, test, hypotheses | — | none | |
| 9(ii) | 4 | D11, D17, C18 | `fstat » Chi-sq contributions » 4,4,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5` | OK | ⇒ "r3: -0.593 -1.25" |
| 9(iii) | 4 | test | `fstat » Chi-sq association » 4,4,5,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5` | OK | ⇒ "reject H0 at 5%" |
| 9(iv) | 3 | interpret | `fstat » Chi-sq contributions » 4,4,63,61,71,80,33,33,22,12,9,8,11,20,4,9,9,5` | OK | ⇒ "r2: +3.18 +2.82" |
| 10(i) | 2 | variance estimate | `fstat » Estimates from sums » 60,89.758,134.280` | AWKWARD | ⇒ "s^2 = 8.52e-5"; but "xbar = 1.5" (1.49597 to 3 s.f.) — reads as exactly the advertised 1.5 |
| 10(ii) | 4 | 95% CI | `fstat » CI mean from summary » 60,1.49597,sqrt(0.00008515),95` | AWKWARD | prints "(1.49, 1.5)" and "centre 1.5": at 3 s.f. the interval seems to touch 1.5, while MS (1.4936, 1.4983) excludes it |
| 10(iii) | 1 | conclusion | — | none | |
| 10(iv) | 2 | explain | — | none | |
| 10(v) | 1 | 285 | — | none | |
| 11(i) | 3 | P(H = 60) = (1/6)^10 | `CALC » Calculate » (1/6)^10` | OK | ⇒ "1/60466176" |
| 11(ii) | 1 | explain | — | none | |
| 11(iii) | 3 | discrete uniform | `fstat » Discrete uniform » 1,6` | OK | ⇒ "Var(X) = (n^2-1)/12 = 35/12" |
| 11(iv) | 5 | E, Var of L = 10X and H = sum | `fstat » nX vs X1+..+Xn » 3.5,35/12,10,40.5` | OK | ⇒ "Var(X1+..+Xn) = 175/6" |
| 11(v) | 2 | estimates from simulation | — | none | read off |
| 11(vi) | 2 | P(L <= 40) = 2/3 | — | none | trivial |
| 11(vii) | 3 | diagram | — | none | |
| 11(viii) | 4 | CLT P(H <= 40) with correction | `fstat » nX vs X1+..+Xn » 3.5,35/12,10,40.5` | AWKWARD | ⇒ "P(sum<k) = 0.846"; complement and continuity correction 40.5 by hand (MS 0.154) |

Parts: 45. Rows: OK 22, WRONG 0, AWKWARD 6, GAP 2, none 16.
