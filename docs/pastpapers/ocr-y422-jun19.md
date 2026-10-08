# OCR Y422 Statistics Major, June 2019 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 1 | table of k(127-39r+3r^2) | `fstat » DRV find k » 127-39x+3x^2,1,6` | OK | ⇒ "k * 216 = 1"; g(r) values 91, 61, 37, 19, 7, 1 implied |
| 1b | 2 | k = 1/216 | `fstat » DRV find k » 127-39x+3x^2,1,6` | AWKWARD | prints "k = 0.00463" as a decimal (exact 1/216 only in "k * 216 = 1") |
| 1c | 2 | graph | — | none | |
| 1d | 1 | shape | — | none | |
| 1e | 5 | E(X), Var(X) | `fstat » DRV from formula » (127-39x+3x^2)/216,1,6` | OK | ⇒ "E(X) = 49/24"; Var 1.31 (MS 1.308) |
| 2a | 2 | conditions | — | none | |
| 2b | 2 | P(X >= 2), Po(1.6) | `fstat » Poisson P(X=k) » 1.6,2` | OK | ⇒ "P(X>=k) = 0.475" |
| 2c | 2 | P(X <= 10), Po(8) | `fstat » Poisson P(X=k) » 8,10` | OK | ⇒ "P(X<=k) = 0.816" |
| 2d | 3 | P(X = 1), Po(3.2) | `fstat » Poisson P(X=k) » 3.2,1` | OK | ⇒ "P(X=k) = 0.13" (MS 0.1304) |
| 3a | 2 | sum of 5 bananas >= 1000 | `fstat » nX vs X1+..+Xn » 205,121,5,1000` | OK | ⇒ "P(sum<k) = 0.155"; complement 0.845 by hand |
| 3b | 3 | 0.65X <= 150 | `fstat » E and Var of a+bX » 0,0.65,205,121` | OK | ⇒ "Var(a+bX) = 51.1" |
| 3b | | | `fstat » Normal P(a<X<b) » 133.25,7.15,0,150` | OK | ⇒ "P(a<X<b) = 0.99" |
| 3c | 4 | 2 peeled bananas + 20 strawberries < 700 | `fstat » aX+bY+c » 1,1,0,266.5,102.245,450,145.8,700` | AWKWARD | ⇒ "P(W<k) = 0.147"; sums of n1 X's and n2 Y's must be pre-computed (2×133.25, 2×51.12, 20×22.5, 20×7.29) by hand; no "n1 X + n2 Y" tool |
| 3c | | tempting 2X + 20Y entry | `fstat » aX+bY+c » 2,20,0,133.25,51.1225,22.5,7.29,700` | WRONG | Var shown as "sqrt(350548482)/6" (it is 3120.49): false surd format for a decimal; the 2X/20Y model itself is the student's error |
| 4a | 1 | assumption | — | none | |
| 4b | 1 | CI | `fstat » CI mean from data » 95,2.36,2.97,2.69,3.00,2.51,2.45,2.21,2.63` | OK | ⇒ "(2.37, 2.84)" |
| 4c | 2 | SE | `fstat » CI mean from summary » 8,2.6025,0.2793,95` | OK | ⇒ "SE = s/sqrt(n) = 0.0987" |
| 4d | 2 | t* x SE | `fstat » CI mean from summary » 8,2.6025,0.2793,95` | OK | ⇒ "t* = 2.37 (df 7)" |
| 4e | 1 | wider CI | — | none | |
| 5a | 4 | B11, C10, C14 | `fstat » Chi-sq contributions » 3,3,8,52,178,10,40,68,5,47,92` | OK | ⇒ "E r3: 6.62 40 97.3" |
| 5b | 6 | test at 1% | `fstat » Chi-sq association » 3,3,1,8,52,178,10,40,68,5,47,92` | OK | ⇒ "reject H0 at 1%" |
| 5c | 3 | interpret | `fstat » Chi-sq contributions » 3,3,8,52,178,10,40,68,5,47,92` | OK | ⇒ "r1: -0.794 -3.03 +1.82" |
| 6a(i) | 5 | x on y from column sums | `fstat » Regression x on y » 90,102,94,97,99,101` | GAP | only raw pairs accepted; question gives n, sums of x, y, x^2, y^2, xy; no regression-from-summary tool (MS x = 0.8537y + 6.962) |
| 6a(ii) | 2 | predictions | — | GAP | depends on 6a(i) |
| 6a(iii) | 2 | reliability | — | none | |
| 6b(i) | 2 | explain | — | none | |
| 6b(ii) | 2 | PMCC | `fstat » PMCC r » 4.2,18,7.1,26,5.6,42,3.5,76,8.6,15,6.5,43,2.7,84,5.9,53,6.7,66,4.1,36` | OK | ⇒ "r = -0.564" |
| 6b(iii) | 5 | test 5% 2-tail | `fstat » PMCC test from data » 5,2,4.2,18,7.1,26,5.6,42,3.5,76,8.6,15,6.5,43,2.7,84,5.9,53,6.7,66,4.1,36` | OK | ⇒ "crit = +/-0.632" |
| 7a | 4 | 95% CI, n = 40 | `fstat » CI mean from summary » 40,0.1442,0.2580,95` | OK | ⇒ "(0.0642, 0.224)" |
| 7b | 2 | 0.2 inside | `fstat » CI to test mu0 » 0.0642,0.2242,0.2` | OK | ⇒ "mu0 inside the CI" |
| 7c | 2 | CLT | — | none | |
| 7d | 3 | n for width 0.12 | `fstat » Sample size for width » 0.2580,0.12,95` | OK | ⇒ "n = 72" |
| 8a | 3 | choose test from Normality output | `fstat » Normal prob plot » 26,28,29,30,31,32,34,42,49,54,55,56,61` | OK | ⇒ "curved: Normal is doubtful" (K-S p-value given in the question) |
| 8b | 3 | flaws | — | none | |
| 8c | 7 | Wilcoxon vs 33.5 | `fstat » Wilcoxon single sample » 33.5,5,1,26,28,29,30,31,32,34,42,49,54,55,56,61` | OK | ⇒ "crit: reject if T <= 21" |
| 9a | 1 | U(0,5), P(X >= 3) | `fstat » Rectangular U(a,b) » 0,5,3,5` | OK | ⇒ "P(c<X<d) = 2/5" |
| 9b | 3 | P(X <= 6), piecewise pdf | `fstat » Piecewise pdf » x/25,(10-x)/25,0,5,10` | AWKWARD | gives E, Var, median, P per piece; no P(c<X<d) across pieces (0.68 by adding 0.5 + CAS int 5..6) |
| 9c | 1 | estimate from simulation | — | none | count |
| 9d | 1 | better estimate | — | none | |
| 9e | 3 | E(T), Var(T) | `fstat » nX vs X1+..+Xn » 2.5,25/12,5,18` | OK | ⇒ "Var(X1+..+Xn) = 125/12" |
| 9f | 2 | CLT P(T > 18) | `fstat » nX vs X1+..+Xn » 2.5,25/12,5,18` | OK | ⇒ "P(sum<k) = 0.956"; complement 0.044 |
| 9g | 1 | comment | — | none | |
| 9h | 3 | 200 days > 510 | `fstat » nX vs X1+..+Xn » 2.5,25/12,200,510` | OK | ⇒ "P(sum<k) = 0.688"; complement 0.312 |
| 10a | 3 | k in terms of a, m | — | GAP | pdf tools need numbers; no symbolic k |
| 10b | 3 | cdf in x, a, m | — | GAP | symbolic |
| 10c(i) | 4 | show 2p^2 - 10p + 5 = 0 | — | GAP | symbolic |
| 10c(ii) | 2 | m | `CAS » solve f(x)=0 » 2x^2-10x+5` | OK | ⇒ "x = 0.564, 4.44" |
| 10c(ii) | | | `CALC » Calculate » ln(4.4365)/ln(2)` | OK | ⇒ "2.149421968" |

Parts: 45. Rows: OK 27, WRONG 1, AWKWARD 3, GAP 5, none 12.
