# OCR Y422 Statistics Major, June 2022 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 1 | Po(1.2), P(X = 2) | `fstat » Poisson P(X=k) » 1.2,2` | OK | ⇒ "P(X=k) = 0.217" |
| 1b | 2 | P(X > 3) | `fstat » Poisson P(X=k) » 1.2,3` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 0.0338" |
| 1c | 2 | Po(12), P(X <= 8) | `fstat » Poisson P(X=k) » 12,8` | OK | ⇒ "P(X<=k) = 0.155" |
| 1d | 2 | interpret | — | none | |
| 2a | 3 | sum of 5 A >= 120 | `fstat » nX vs X1+..+Xn » 23,7.84,5,120` | OK | ⇒ "P(sum<k) = 0.788"; complement 0.212 |
| 2b | 3 | 3A - 2B > 0 | `fstat » aX+bY+c » 1,-1,0,69,23.52,70,25.92,0` | AWKWARD | ⇒ "P(W>k) = 0.443"; sums of 3 A's and 2 B's pre-combined by hand |
| 2c | 1 | independence | — | none | |
| 3a | 3 | a, b from E(X) = 1.8 | `fstat » DRV from table » 0,0.2,1,0.2,2,0.24,3,0.32,4,0.04` | GAP | unknown probabilities cannot be solved for (b + 0.48 + 0.96 + 4b^2 = 1.8); table only checks a = b = 0.2 |
| 3b | 3 | E(Y), Var(Y), Y = 10 - 3X | `fstat » E and Var of a+bX » 10,-3,1.8,1.44` | OK | ⇒ "Var(a+bX) = 324/25" |
| 4a | 2 | P(X >= 10) in k | — | GAP | symbolic k |
| 4b | 3 | 2nd success within 4 draws | `fstat » Binomial P(X=k) » 4,0.4,2` | OK | ⇒ "P(X>=k) = 0.525" (as "at least 2 in 4") |
| 5a | 2 | regression to 4 s.f. | `fstat » Regression y on x » 20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192` | AWKWARD | "y = 1.79 + 0.0115x": 3 s.f. only; question asks 4 s.f. (0.01145, 1.786); exact b = 2.75/240 shown |
| 5b | 3 | residuals at 28, 36 | `fstat » Residuals » 20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192` | OK | ⇒ "x=36: e = -0.00604" |
| 5c | 2 | comment | — | none | |
| 5d | 2 | predictions at 25, 10 to 3 d.p. | `fstat » Predict y from x » 25,20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192` | AWKWARD | "y = 2.07" and "y = 1.9": 3 s.f., not the 3 d.p. asked (2.072, 1.900) |
| 5e | 2 | reliability | `fstat » Predict y from x » 10,20,2.012,22,2.036,24,2.065,26,2.074,28,2.114,30,2.140,32,2.149,34,2.176,36,2.192` | OK | ⇒ "extrapolation: x outside data" |
| 6a | 6 | CI from sums | `fstat » Estimates from sums » 40,491.84,6050.3` | OK | ⇒ "s^2 = 0.0676" |
| 6a | | CI | `fstat » CI mean from summary » 40,12.296,0.25994,95` | AWKWARD | ends printed "(12.2, 12.4)" at 3 s.f. — hides that 12.2 is outside (12.215, 12.377); xbar must also be retyped at full precision (shown as 12.3) |
| 6b | 1 | 12.2 outside CI | `fstat » CI to test mu0 » 12.2155,12.3765,12.2` | OK | ⇒ "mu0 outside the CI" (only if full-precision ends are typed) |
| 6c | 1 | random | — | none | |
| 6d | 3 | mean and n from CI [1.202, 1.398] | `fstat » Sample size for width » 0.5,0.196,95` | OK | ⇒ "n = 100"; mean 1.3 by hand |
| 7a | 2 | geometric P(X = 5) | `fstat » Geometric P(X=r) » 0.3,5` | OK | ⇒ "P(X=r) = 0.072" |
| 7b | 3 | B(6, 0.343), P(>= 4) | `fstat » Binomial P(X=k) » 6,0.343,4` | OK | ⇒ "P(X>=k) = 0.11"; 0.7^3 from `Geometric P(X=r) » 0.3,3` "P(X>r)" |
| 7c | 3 | (1-p)p = 28/121 | `CAS » solve exact f(x)=0 » (1-x)*x-28/121` | OK | ⇒ "x = 4/11" |
| 8a | 2 | explain | — | none | |
| 8b | 2 | explain | — | none | |
| 8c | 8 | Spearman test | `fstat » Spearman test data » 5,2,30.26,28.19,30.41,29.59,31.36,29.07,31.56,29.99,31.68,29.28,31.69,29.60,31.77,30.18,32.14,29.20,32.16,29.12,35.63,32.69,36.24,33.85` | OK | ⇒ "rs = 0.591" |
| 8d | 2 | comment | — | none | |
| 9a | 1 | P(X <= 7) | `fstat » Discrete uniform » 0,20,0,7` | OK | ⇒ "P(c<=X<=d) = 8/21" |
| 9b | 3 | E, Var | `fstat » Discrete uniform » 0,20,0,7` | OK | ⇒ "Var(X) = (n^2-1)/12 = 110/3" |
| 9c | 1 | estimate | — | none | count |
| 9d | 2 | explain | — | none | |
| 9e | 4 | mean of 30, with continuity correction | `fstat » Normal P(a<X<b) » 10,sqrt(110/3/30),-100,7.0167` | AWKWARD | ⇒ "P(a<X<b) = 0.00348"; continuity correction (7 + 1/60) and Var/30 by hand; no CLT tool for a discrete mean |
| 10a | 2 | expected frequencies | `fstat » Chi-sq association » 2,3,5,9,18,5,3,13,12` | OK | ⇒ "E r1: 6.4 16.5 9.07" |
| 10b | 2 | contribution to 4 d.p. | `fstat » Chi-sq contributions » 2,3,9,18,5,3,13,12` | AWKWARD | prints "-1.82", MS 1.8240 to 4 d.p.: 3 s.f. display |
| 10c | 6 | test at 5% | `fstat » Chi-sq association » 2,3,5,9,18,5,3,13,12` | OK | ⇒ "reject H0 at 5%" |
| 10d | 3 | interpret | `fstat » Chi-sq contributions » 2,3,9,18,5,3,13,12` | OK | ⇒ "r2: -1.21 -0.149 +2.08" |
| 11a | 3 | choose test | — | none | |
| 11b | 7 | Wilcoxon median 1, 1-tail | `fstat » Wilcoxon single sample » 1,5,1,-0.84,-0.76,-0.16,0.43,1.31,1.32,1.47,1.64,1.93,2.14` | OK | ⇒ "crit: reject if T <= 10" |
| 11c | 3 | alternative t test | — | none | |
| 12a | 7 | median in terms of a | `fstat » cdf median quartiles » (10x-0.5x^2)/50,0,10` | GAP | letter a refused; a = 10 check gives "median = 2.93" (= a(1 - 1/sqrt2)) |
| 12b | 7 | P(within 1 sd), a = 10 | `fstat » pdf from a cdf » (10x-0.5x^2)/50,0,10` | OK | ⇒ "SD = 2.36" |
| 12b | | | `fstat » pdf P(c<X<d) » (10-x)/50,0,10,3.333-2.357,3.333+2.357` | OK | ⇒ "P(c<X<d) = 0.629"; mu ± sigma retyped |

Parts: 41. Rows: OK 23, WRONG 0, AWKWARD 6, GAP 3, none 11.
