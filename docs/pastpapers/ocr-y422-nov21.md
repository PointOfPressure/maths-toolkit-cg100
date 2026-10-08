# OCR Y422 Statistics Major, November 2021 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output. No examiners' report for this series.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 4 | 95% CI, n = 50 | `fstat » CI mean from summary » 50,34.711,1.530,95` | OK | ⇒ "centre 34.7 +/- 0.424"; ends shown 3 s.f. "(34.3, 35.1)", MS (34.287, 35.135) |
| 1b | 2 | CLT | — | none | |
| 2a | 2 | P(X = 0) | `CALC » Calculate » 6/216` | none | trivial arithmetic |
| 2b | 2 | graph | — | none | |
| 2c | 1 | shape | — | none | |
| 2d | 5 | E(X), Var(X) | `fstat » DRV from table » 0,1/36,1,5/36,2,2/9,3,1/4,4,2/9,5,5/36` | OK | ⇒ "E(X) = 35/12" |
| 2e | 1 | Var(30X) | `fstat » E and Var of a+bX » 0,30,35/12,1.7986` | OK | ⇒ "Var(a+bX) = 80937/50" (1618.7) |
| 2f | 2 | k = 100 | `fstat » E and Var of a+bX » 0,30,35/12,1.7986` | OK | ⇒ "E(a+bX) = 175/2"; + 12.5 by hand |
| 3a | 2 | B(50, 0.04), P(X = 2) | `fstat » Binomial P(X=k) » 50,0.04,2` | OK | ⇒ "P(X=k) = 0.276" |
| 3b | 1 | geometric, 10th first | `fstat » Geometric P(X=r) » 0.04,10` | OK | ⇒ "P(X=r) = 0.0277" |
| 3c | 1 | none in 20 | `fstat » Binomial P(X=k) » 20,0.04,0` | OK | ⇒ "P(X=k) = 0.442" |
| 3d | 3 | expected trials for 3rd | `fstat » Geometric P(X=r) » 0.04,10` | AWKWARD | ⇒ "mean 1/p = 25"; x3 by hand; no negative-binomial (r-th success) tool |
| 3e | 3 | 3rd misunderstood is 60th | `fstat » Binomial P(X=k) » 59,0.04,2` | AWKWARD | ⇒ "P(X=k) = 0.267"; × 0.04 by hand (MS 0.0107) |
| 4a | 3 | explain | — | none | |
| 4b | 3 | Po(5): P(X = 6), P(X > 6) | `fstat » Poisson P(X=k) » 5,6` | OK | ⇒ "P(X>k) = 1-P(X<=k) = 0.238" |
| 4c | 2 | Po(50), P(X >= 60) | `fstat » Poisson P(X=k) » 50,60` | OK | ⇒ "P(X>=k) = 0.0923" |
| 5a | 3 | A1 + A2 + B >= 16 | `fstat » aX+bY+c » 1,1,0,7.8,0.2048,7.8,0.1681,16` | AWKWARD | ⇒ "P(W>k) = 0.256"; A1+A2 pre-combined (mean 7.8, var 2×0.32^2); entering a = 2 gives 2A (Var ×4, P = 0.299) — no "sum of n copies" input |
| 5b | 3 | C within 1 of B1+..+B4 | `fstat » Normal P(a<X<b) » 1,sqrt(4*0.1681+0.4096),-1,1` | AWKWARD | ⇒ "P(a<X<b) = 0.473"; 4B - C variance (4×0.41^2 + 0.64^2) combined by hand |
| 5c | 11 | t test from sums, n = 10 | `fstat » Estimates from sums » 10,299.6,8981.0` | AWKWARD | ⇒ "s^2 = 0.554"; but xbar shown as "30" (29.96 to 3 s.f.), which would wreck the test statistic if copied |
| 5c | | t test | `fstat » z test for a mean » 30.2,0.744,10,29.96,5,2` | GAP | no one-sample t test for a mean: the z test gives crit ±1.96, MS uses t9 = 2.262 (statistic -1.02 matches) |
| 6a | 3 | mean, variance from frequency table | `mstat » Frequency table » 0,34,1,65,2,55,3,24,4,14,5,6,6,2` | AWKWARD | ⇒ "sum fx = 345"; mean shown "1.72" (1.725), variance only with divisor n (1.76) while MS uses 1.768; `fstat » Poisson model check` takes raw data only |
| 6b | 4 | C3, D3, E3 | `fstat » GOF Poisson » 1.7,5,34,65,55,24,14,6,2` | OK | ⇒ "1: O 65, E 62.1, 0.134" |
| 6c | 1 | pooling | — | none | |
| 6d | 6 | GOF at 5% | `fstat » GOF Poisson » 1.7,5,34,65,55,24,14,6,2` | OK | ⇒ "chi^2 = 2.43" |
| 7a | 2 | explain | — | none | |
| 7b | 2 | assumptions | — | none | |
| 7c | 1 | 2 in CI | — | none | |
| 7d(i) | 3 | mean and sd from CI (1.94, 2.84), n = 100 | `fstat » CI to test mu0 » 1.94,2.84,2` | AWKWARD | ⇒ "half width = 0.45"; sd = 0.45·10/1.96 by hand; no "CI -> xbar, s" back-solver |
| 7d(ii) | 2 | random sample | — | none | |
| 8a(i) | 1 | predict at 50 | `CALC » Calculate » 0.6978*50+15.656` | OK | ⇒ "50.546" |
| 8a(ii) | 2 | reliability | — | none | |
| 8a(iii) | 1 | lines meet | `mpure » Simultaneous 2 linear » -0.6978,1,15.656,1,-0.7565,10.493` | OK | ⇒ "x = 47.3" |
| 8a(iv) | 1 | means | — | none | |
| 8b(i) | 2 | elliptical | — | none | |
| 8b(ii) | 4 | r from sums | `mstat » Stats from summary » 20,80.37,324.71` | GAP | no PMCC from Σt, Σv, Σt^2, Σv^2, Σtv; only Stt (MS r = -0.4255) |
| 8b(iii) | 5 | 1-tail test | `fstat » PMCC test from r » -0.4255,20,5,1` | OK | ⇒ "crit = -0.378" |
| 9a | 3 | P(X > n/2) in n | — | GAP | discrete uniform tool numeric only |
| 9b | 3 | Var of sum of 10 in n | `fstat » Discrete uniform » -3,3` | GAP | numeric n only (Var = 4 for n = 3); no symbolic (MS 10(n^2+n)/3) |
| 10a | 2 | read simulation | — | none | |
| 10b | 5 | E(T), Var(T), P(W <= 56) | `fstat » Normal P(a<X<b) » 61,sqrt(94/3),0,56` | AWKWARD | ⇒ "P(a<X<b) = 0.186"; mean 61 and variance 94/3 (two uniforms + two Normals) assembled by hand; no multi-term E/Var tool |
| 10c | 2 | explain | — | none | |
| 11a | 5 | a, b from int = 1 and E(X) = 2 | `fstat » Piecewise pdf » x^2/8,2(3-x)^2,0,2,3` | GAP | unknown constants a, b cannot be solved for; checks once a = 1/8, b = 2 are known ("E(X) = 2") |
| 11b | 3 | median | `fstat » Piecewise pdf » x^2/8,2(3-x)^2,0,2,3` | OK | ⇒ "median = 2.09" |
| 11c | 3 | mean of 50 < 1.9 | `fstat » Normal P(a<X<b) » 2,sqrt(0.2/50),0,1.9` | OK | ⇒ "P(a<X<b) = 0.0569" |

Parts: 43. Rows: OK 16, WRONG 0, AWKWARD 8, GAP 5, none 15.
