# OCR Y422 Statistics Major, June 2024 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 2 | E(X), Var(X) | `fstat » DRV from table » 0,0.05,1,0.1,2,0.25,3,0.3,4,0.15,5,0.1,6,0.05` | OK | ⇒ "Var(X) = 2.09" |
| 1b | 3 | 1000 + 500X | `fstat » E and Var of a+bX » 1000,500,2.9,2.09` | OK | ⇒ "SD(a+bX) = 723" |
| 2a | 2 | Poisson mean = 0.6^2 | — | none | trivial |
| 2b(i) | 1 | P(X = 1), Po(0.36) | `fstat » Poisson P(X=k) » 0.36,1` | OK | ⇒ "P(X=k) = 0.251" |
| 2b(ii) | 2 | P(X > 1) | `fstat » Poisson P(X=k) » 0.36,1` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 0.0512" |
| 2c | 2 | Po(7.2), P(< 5) | `fstat » Poisson P(X=k) » 7.2,4` | OK | ⇒ "P(X<=k) = 0.156" |
| 3a | 1 | P(drying > 50) | `fstat » Normal P(a<X<b) » 46,3.1,50,1000` | OK | ⇒ "P(a<X<b) = 0.0985" |
| 3b | 1 | 99th percentile | `fstat » Inverse Normal » 35,2.4,0.99` | OK | ⇒ "x = 40.6" |
| 3c | 3 | D - W - F < 0 | `fstat » Normal P(a<X<b) » -1,sqrt(20.21),-100,0` | AWKWARD | ⇒ "P(a<X<b) = 0.588"; three-variable combination done by hand (aX+bY+c has two variables only) |
| 3d | 3 | mean of 5 totals < 90 | `fstat » Normal P(a<X<b) » 93,sqrt(20.21/5),0,90` | AWKWARD | ⇒ "P(a<X<b) = 0.0678"; same three-variable assembly by hand |
| 4a | 2 | a | `fstat » pdf find k » x,0,50` | OK | ⇒ "k = 0.0008" (1/1250 only as a decimal) |
| 4b | 2 | P(X < 5) | `fstat » pdf P(c<X<d) » x/1250,0,50,0,5` | OK | ⇒ "P(c<X<d) = 0.01" |
| 4c | 3 | median | `fstat » pdf median quartiles » x/1250,0,50` | OK | ⇒ "median m = 35.4"; exact 25 sqrt2 not shown |
| 5a | 2 | CLT | — | none | |
| 5b | 2 | 0 not in CI | — | none | |
| 5c(i) | 1 | SE meaning | — | none | |
| 5c(ii) | 1 | SE | `fstat » CI mean from summary » 40,0.586,2.14,90` | OK | ⇒ "SE = s/sqrt(n) = 0.338" |
| 5d | 4 | 95% CI | `fstat » CI mean from summary » 40,0.586,2.14,95` | OK | ⇒ "(-0.0772, 1.25)" |
| 6a | 2 | explain | — | none | |
| 6b | 1 | random | — | none | |
| 6c | 8 | Spearman 1-tail | `fstat » Spearman test data » 5,1,22,38,29,46,36,42,39,49,53,37,57,47,60,36,71,33,76,34,82,24` | OK | ⇒ "rs = -0.721" |
| 7a | 2 | estimates | `fstat » Estimates from data » 6.20,10.72,11.42,16.32,15.33,10.56,8.83,9.21,7.78,14.32` | AWKWARD | ⇒ "s = 3.33"; xbar shown "11.1" (MS 11.07): 3 s.f. display too coarse for a mean |
| 7b | 3 | comment | — | none | |
| 7c | 1 | H0 | — | none | |
| 7d | 8 | one-sample t test, 2-tail | `fstat » CI mean from data » 95,6.20,10.72,11.42,16.32,15.33,10.56,8.83,9.21,7.78,14.32` | GAP | no t test for a mean; the t CI (8.69, 13.5) contains 9.4 (same conclusion) but statistic 1.585 / crit 2.262 not given |
| 7e | 2 | Wilcoxon | — | none | |
| 8a | 2 | label | — | none | |
| 8b | 5 | y on x from sums | `mstat » Stats from summary » 11,652.5,41987.35` | GAP | no Sxy / regression from sums (MS y = 4.6806x + 182.99) |
| 8c | 2 | predictions | — | GAP | depends on 8b |
| 8d | 3 | reliability | — | none | |
| 8e | 2 | x on y | — | none | |
| 9a | 2 | expected frequencies | `fstat » Chi-sq association » 2,3,5,2,21,19,13,47,18` | OK | ⇒ "E r2: 9.75 44.2 24" |
| 9b | 2 | contribution to 4 d.p. | `fstat » Chi-sq contributions » 2,3,2,21,19,13,47,18` | AWKWARD | "-1.52"; MS 1.5219 to 4 d.p. |
| 9c | 6 | test | `fstat » Chi-sq association » 2,3,5,2,21,19,13,47,18` | OK | ⇒ "chi^2 = 7.95" |
| 9d | 3 | interpret | `fstat » Chi-sq contributions » 2,3,2,21,19,13,47,18` | OK | ⇒ "r1: -2.01 -0.329 +2.83" |
| 10a | 2 | E(Z) | `fstat » E and Var of X+-Y » 3,3,2,4/3` | OK | ⇒ "E(X+Y) = 5" |
| 10b | 3 | variances | `fstat » E and Var of X+-Y » 3,3,2,4/3` | OK | ⇒ "Var(X+Y) = 13/3" (vs U[0,10] 25/3) |
| 10c | 1 | estimate | — | none | count |
| 10d | 3 | total of 40 > 210 | `fstat » nX vs X1+..+Xn » 5,13/3,40,210` | OK | ⇒ "P(sum<k) = 0.776"; complement 0.224 |
| 11a | 4 | P(X < (n+25)/2), n even/odd | — | GAP | symbolic n |
| 11b | 2 | Var of mean of 100 in n | `fstat » Discrete uniform » 25,75` | GAP | numeric only (n = 75: 650/3) |
| 11c | 5 | n = 75, mean of 100 < 48 | `fstat » Normal P(a<X<b) » 50,sqrt(2600/1200),0,47.995` | AWKWARD | ⇒ "P(a<X<b) = 0.0866"; continuity correction 47.995 and Var/100 by hand |
| 12a | 7 | a, b, c from F(20), F(30), F(25) then P(X > 27) | `CALC » Calculate » 1-(27^2+10*27-600)/600` | GAP | no solver for constants in a cdf from conditions; 3 linear equations by hand (a = 1/600, b = 10, c = -600) then ⇒ 0.335 |
| 12b | 2 | 90th percentile | `fstat » cdf median quartiles » (x^2+10x-600)/600,20,30,0.9` | OK | ⇒ "F(x) = p at x = 29.1" |

Parts: 44. Rows: OK 20, WRONG 0, AWKWARD 5, GAP 6, none 13.
