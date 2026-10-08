# OCR Y422 Statistics Major, June 2023 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 1 | (1/6)^4 | `CALC » Calculate » (1/6)^4` | OK | ⇒ "1/1296" |
| 1b | 3 | explain | — | none | |
| 1c | 3 | Po(10000/1296): P(X = 10), P(X > 10) | `fstat » Poisson P(X=k) » 10000/1296,10` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 0.157" |
| 1c | | approximation tool | `fstat » Poisson approx to B » 10000,1/1296,10` | WRONG | "n must be 1 to 1000": refuses n = 10000 |
| 1d | 3 | p = 1 - (1295/1296)^20, B(50, p), P(<= 2) | `CALC » Calculate » 1-(1295/1296)^20` | OK | ⇒ "0.01531949967" |
| 1d | | | `fstat » Binomial P(X=k) » 50,0.015319,2` | OK | ⇒ "P(X<=k) = 0.959" |
| 2a | 2 | predictions | `CALC » Calculate » -10.26*5+1013` | OK | ⇒ "961.7" |
| 2b | 3 | reliability | — | none | |
| 3a | 1 | none in 3 | `fstat » Binomial P(X=k) » 3,0.55,0` | OK | ⇒ "P(X=k) = 0.0911" |
| 3b | 2 | B(20, 0.55), P(>= 10) | `fstat » Binomial P(X=k) » 20,0.55,10` | OK | ⇒ "P(X>=k) = 0.751" |
| 3c | 2 | first on 5th | `fstat » Geometric P(X=r) » 0.55,5` | OK | ⇒ "P(X=r) = 0.0226" |
| 3d | 2 | 5th success on 10th | `fstat » Binomial P(X=k) » 9,0.55,4` | AWKWARD | ⇒ "P(X=k) = 0.213"; × 0.55 by hand (0.117); no negative-binomial tool |
| 3e | 3 | p(1-p) = 0.2496, p^2 < 0.25 | `CAS » solve exact f(x)=0 » x*(1-x)-0.2496` | OK | ⇒ "x = 12/25" (choose 0.48) |
| 4a | 3 | sum of 10 < 31 | `fstat » nX vs X1+..+Xn » 3.125,0.0009,10,31` | OK | ⇒ "P(sum<k) = 0.0042" |
| 4b | 2 | 10 × one sheet < 31 | `fstat » nX vs X1+..+Xn » 3.125,0.0009,10,31` | OK | ⇒ "P(nX<k) = 0.202" |
| 4c | 3 | A + B + C >= 9.4 | `fstat » Normal P(a<X<b) » 9.351,sqrt(0.0027),9.4,100` | AWKWARD | ⇒ "P(a<X<b) = 0.173"; three-term sum combined by hand; `aX+bY+c` takes only two variables (a constant c loses the third variance: 0.124) |
| 4d | 3 | 10A - 10B < 0 | `fstat » aX+bY+c » 1,-1,0,31.25,0.009,31.17,0.009,0` | AWKWARD | ⇒ "P(W<k) = 0.275"; sums of 10 pre-combined |
| 5a | 6 | CI from sums | `fstat » Estimates from sums » 40,765,15065` | OK | ⇒ "s^2 = 11.1" |
| 5a | | | `fstat » CI mean from summary » 40,19.125,sqrt(11.138),95` | OK | ⇒ "centre 19.1 +/- 1.03" (MS 19.125 ± 1.034) |
| 5b | 2 | comments | — | none | |
| 5c | 2 | n = 10 | — | none | |
| 5d | 1 | interval | — | none | read off |
| 5e | 2 | comments | — | none | |
| 6a | 2 | elliptical | — | none | |
| 6b | 4 | r from sums | — | GAP | no PMCC from Σx, Σy, Σx^2, Σy^2, Σxy (MS r = 0.211) |
| 6c | 5 | test | `fstat » PMCC test from r » 0.211,20,5,2` | OK | ⇒ "crit = +/-0.444" |
| 6d | 1 | explain | — | none | |
| 7a | 3 | choose t test | — | none | |
| 7b | 10 | one-sample t test, 1-tail | `fstat » z test from data » 1.0,?,5,1,1.087,1.171,1.047,0.846,0.909,1.052,1.042,0.893,1.021,1.085,1.096,0.931` | GAP | statistic 0.53 matches but crit 1.64 (z) not t11 = 1.796; no one-sample t test (the CI tool has t* but no test) |
| 8a | 2 | 2 × 0.3 × 0.7 | `fstat » Rectangular U(a,b) » 0,10,0,3` | AWKWARD | ⇒ "P(c<X<d) = 3/10"; the 2·p·(1-p) step by hand |
| 8b | 1 | P(T <= 25) = 0.5 | — | none | symmetry |
| 8c | 2 | estimates | — | none | read off |
| 8d | 7 | mean of 100 T's | `fstat » Normal P(a<X<b) » 25,sqrt(5*25/3/100),26,100` | OK | ⇒ "P(a<X<b) = 0.0607"; Var(T)/100 by hand |
| 9a | 9 | 2x2 association | `fstat » Chi-sq association » 2,2,5,12,11,157,70` | OK | ⇒ "chi^2 = 2.75" |
| 9b | 1 | bias | — | none | |
| 10a | 4 | cdf in terms of a | — | GAP | letter a refused in pdf tools |
| 10b | 2 | find a | `fstat » pdf find k » a/x^2+3x^2-7/2,1,2` | GAP | "cannot integrate g(x)": only a multiplying constant k can be found, not an additive unknown (MS a = 1/2) |
| 10c | 2 | show quartic | — | none | algebra |
| 10d | 2 | median 1.74 | `fstat » cdf median quartiles » (4/15)*(-1/(2x)+x^3-7x/2+3),1,2` | OK | ⇒ "median = 1.74" |
| 10e | 2 | E(X) | `fstat » pdf E Var and check » (4/15)*(1/(2x^2)+3x^2-7/2),1,2` | OK | ⇒ "E(X) = 1.69" |
| 10f | 3 | mode | `fstat » Mode of a pdf » (4/15)*(1/(2x^2)+3x^2-7/2),1,2` | OK | ⇒ "mode = 2" |
| 11a | 3 | E, Var of Bernoulli in p | `fstat » DRV from table » 0,0.8,1,0.2` | GAP | symbolic p not accepted; numeric p = 0.2 only |
| 11b | 6 | prove mean 10, variance 8 | `fstat » Binomial P(X=k) » 50,0.2,10` | OK | ⇒ "var np(1-p) = 8"; proof itself by hand |

Parts: 40. Rows: OK 20, WRONG 1, AWKWARD 4, GAP 5, none 13.
