# OCR Y422 Statistics Major, November 2020 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 2 | P(all 4) = 1/210 | `mpure » nCr and nPr » 10,4` | OK | ⇒ "nCr = 210" |
| 1a | | in Calculate as 10C4 | `CALC » Calculate » 10C4` | WRONG | silently read as "40*c" (10·C·4 with C a variable); nCr(10,4) works, but the textbook nCr key notation is misparsed with no warning |
| 1b | 2 | E(X), Var(X) | `fstat » DRV from table » 0,1/14,1,8/21,2,3/7,3,4/35,4,1/210` | OK | ⇒ "Var(X) = 16/25" |
| 1c | 3 | loss 1 - 0.4X | `fstat » E and Var of a+bX » 1,-0.4,1.6,0.64` | OK | ⇒ "SD(a+bX) = 0.32" |
| 1d | 2 | new rule with £100 bonus | `fstat » DRV from table » 1,1/14,0.75,8/21,0.5,3/7,0.25,4/35,-100,1/210` | AWKWARD | ⇒ "E(X) = 0.124"; loss table rebuilt by hand; `E(g(X)) from table` cannot take a piecewise g (x==4 is misread) |
| 2a(i) | 3 | explain | — | none | |
| 2a(ii) | 3 | P(X = 3), P(X > 3), B(1200, 1/4000) | `fstat » Poisson approx to B » 1200,0.00025,3` | WRONG | "n must be 1 to 1000": refuses n = 1200, the very case the tool is for |
| 2a(ii) | | Po(0.3) | `fstat » Poisson P(X=k) » 0.3,3` | OK | ⇒ "P(X=k) = 0.00333" |
| 2b | 3 | at most 5000 tested | `fstat » Poisson P(X=k) » 1.25,1` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 0.355"; `Binomial P(X=k)` with n = 5000 also refused ("n must be 1 to 1000") |
| 3a | 3 | mean of 2 large >= 200 | `fstat » Normal P(a<X<b) » 201.3,1.7/sqrt(2),200,1000` | OK | ⇒ "P(a<X<b) = 0.86" |
| 3b | 5 | 8 small - (2 medium + large) > 0 | `fstat » aX+bY+c » 1,-1,0,412,9.68,402.7,8.01,0` | AWKWARD | ⇒ "P(W>k) = 0.986"; three-type sums pre-combined by hand (8×51.5, 8×1.1^2, …) |
| 4a | 2 | CLT | — | none | |
| 4b | 1 | CI | `fstat » CI mean sigma known » 0.1173,0.5766,60,95` | OK | ⇒ "(-0.0286, 0.263)" |
| 4c | 1 | SE | `fstat » CI mean sigma known » 0.1173,0.5766,60,95` | OK | ⇒ "SE = sigma/sqrt(n) = 0.0744" |
| 4d | 2 | comment | — | none | |
| 5a | 2 | explain | — | none | |
| 5b | 5 | y on x from sums | `mstat » Stats from summary » 16,198,2936.92` | GAP | no regression from Σx, Σy, Σx^2, Σy^2, Σxy; only Sxx is available (MS y = 0.4515x + 6.207) |
| 5c | 2 | predictions | — | GAP | depends on 5b |
| 5d | 2 | reliability | — | none | |
| 5e | 2 | outlier | — | none | |
| 6a | 5 | PMCC test r = 0.3231, n = 60, 10% | `fstat » PMCC test from r » 0.3231,60,10,2` | OK | ⇒ "crit = +/-0.215" |
| 6b | 1 | condition | — | none | |
| 6c | 2 | large sample | — | none | |
| 6d | 2 | effect size | — | none | |
| 7a | 1 | assumption | — | none | |
| 7b | 1 | plot | — | none | |
| 7c | 7 | t CI | `fstat » CI mean from data » 95,271,293,306,287,264,290` | OK | ⇒ "centre 285 +/- 16.1" |
| 8 | 10 | estimates from sums | `fstat » Estimates from sums » 40,51.92,70.57` | OK | ⇒ "s^2 = 0.0815" |
| 8 | | z test | `fstat » z test for a mean » 1.25,0.2855,40,1.298,5,2` | OK | ⇒ "z = 1.06"; s must be retyped from the estimates tool; no "z test from sums" |
| 9a | 2 | p estimate | `fstat » GOF binomial » 10,?,1,39,39,33,19,8,8,4,0,0,0,0` | OK | ⇒ "p estimated: xbar/n = 0.172"; the ">= 7" class must be split into 7, 8, 9, 10 zeros by hand |
| 9b | 4 | C2, D2, E2 | `fstat » GOF binomial » 10,?,1,39,39,33,19,8,8,4,0,0,0,0` | OK | ⇒ "0: O 39, E 22.7, 11.7" |
| 9c | 1 | pooling | — | none | |
| 9d | 6 | test at 1% | `fstat » GOF binomial » 10,?,1,39,39,33,19,8,8,4,0,0,0,0` | OK | ⇒ "reject H0 at 1%" |
| 9e | 3 | comment | `fstat » GOF binomial » 10,?,1,39,39,33,19,8,8,4,0,0,0,0` | OK | ⇒ "4-10: O 20, E 11.5, 6.22" |
| 10a | 2 | estimates from simulation | — | none | counting |
| 10b | 1 | improve | — | none | |
| 10c | 9 | W mean of 50 values of X - 2Y | `fstat » E and Var of X+-Y » 6,4.2,6,12` | OK | ⇒ "Var = 21/5 + 12 = 81/5" |
| 10c | | P(W > 1) | `fstat » Normal P(a<X<b) » 0,sqrt(16.2/50),1,100` | AWKWARD | 0.0395 without continuity correction; MS 0.0380 uses 1.01; no CLT-for-discrete-sum tool with correction |
| 11a | 1 | k = 1/40 | `fstat » pdf from a cdf » (8x^2-x^3-24)/40,2,4` | OK | ⇒ "F(a) = 0, F(b) = 1" |
| 11b | 2 | P(2.5 < T < 3.5) | `fstat » pdf P(c<X<d) » (16x-3x^2)/40,2,4,2.5,3.5` | OK | ⇒ "P(c<X<d) = 0.519" |
| 11c | 2 | show cubic | — | none | algebra |
| 11d | 2 | median 2.95 | `fstat » cdf median quartiles » (8x^2-x^3-24)/40,2,4` | OK | ⇒ "median = 2.95" |
| 11e | 7 | P(mu-sigma < T < mu+sigma) | `fstat » pdf E Var and check » (16x-3x^2)/40,2,4` | OK | ⇒ "SD = 0.565" |
| 11e | | | `fstat » pdf P(c<X<d) » (16x-3x^2)/40,2,4,2.402,3.531` | OK | ⇒ "P(c<X<d) = 0.586"; mu ± sigma retyped |
| 11f | 2 | sketch | — | none | |
| 11g | 2 | compare | — | none | |

Parts: 41. Rows: OK 22, WRONG 2, AWKWARD 3, GAP 2, none 17.
