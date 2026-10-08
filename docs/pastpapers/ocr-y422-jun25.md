# OCR Y422 Statistics Major, June 2025 — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1a | 1 | P(X > 4) | `fstat » Discrete uniform » 1,8,5,8` | OK | ⇒ "P(c<=X<=d) = 1/2" |
| 1b | 3 | E, Var | `fstat » Discrete uniform » 1,8,5,8` | OK | ⇒ "Var(X) = (n^2-1)/12 = 21/4" |
| 1c | 3 | 3 × 3/8 × (1/2)^2 exact | `CALC » Calculate » 3*(3/8)*(1/2)^2` | OK | ⇒ "9/32" |
| 2a | 1 | P(R < 19) | `fstat » Normal P(a<X<b) » 20,0.8,0,19` | OK | ⇒ "P(a<X<b) = 0.106" |
| 2b | 4 | 5R + 5Y + 5G >= 495 | `fstat » Normal P(a<X<b) » 500,sqrt(14.45),495,1000` | AWKWARD | ⇒ "P(a<X<b) = 0.906"; 15-block sum assembled by hand (three types) |
| 2c | 3 | 3R - 2Y > 1 | `fstat » aX+bY+c » 1,-1,0,60,1.92,60,1.62,1` | AWKWARD | ⇒ "P(W>k) = 0.298"; sums of 3 and 2 copies pre-combined |
| 3a | 1 | SE | `fstat » CI mean from summary » 50,24.878,0.5664,95` | OK | ⇒ "SE = s/sqrt(n) = 0.0801" |
| 3b | 1 | CI | `fstat » CI mean from summary » 50,24.878,0.5664,95` | AWKWARD | printed "(24.7, 25)" — 3 s.f. makes the upper end 25.035 look like 25 exactly; MS 24.721 < mu < 25.035 |
| 3c | 1 | 25 in CI | — | none | |
| 3d | 4 | 90% CI | `fstat » CI mean from summary » 50,24.878,0.5664,90` | AWKWARD | "(24.7, 25)" again: whether 25 is inside (upper 25.010) cannot be read from the display; centre ± 0.132 must be added by hand |
| 4a(i) | 1 | geometric P(X = 5) | `fstat » Geometric P(X=r) » 0.4,5` | OK | ⇒ "P(X=r) = 0.0518" |
| 4a(ii) | 1 | P(X > 5) | `fstat » Geometric P(X=r) » 0.4,5` | OK | ⇒ "P(X>r) = 0.0778" |
| 4b | 5 | within 1 sd of mean | `fstat » Geometric a<=X<=b » 0.4,1,4` | OK | ⇒ "P(a<=X<=b) = 0.87"; bounds 2.5 ± 1.936 -> 1..4 by hand |
| 4c | 2 | B(20, 0.4), P(>= 5) | `fstat » Binomial P(X=k) » 20,0.4,5` | OK | ⇒ "P(X>=k) = 0.949" |
| 4d | 2 | 5th on 20th | `fstat » Binomial P(X=k) » 19,0.4,4` | AWKWARD | ⇒ "P(X=k) = 0.0467"; × 0.4 by hand; no negative binomial |
| 4e | 1 | validity | — | none | |
| 5a | 2 | Var of U[-4, 2] | `fstat » Rectangular U(a,b) » -4,2,-4,0` | OK | ⇒ "Var(X) = (b-a)^2/12 = 3" |
| 5b | 2 | 2 × (2/3)(1/3) | `fstat » Rectangular U(a,b) » -4,2,-4,0` | AWKWARD | ⇒ "P(c<X<d) = 2/3"; 2·p·(1-p) by hand |
| 6a | 1 | random variable | — | none | |
| 6b | 1 | explain | — | none | |
| 6c | 2 | estimates at 50, 200 | `fstat » Predict y from x » 50,0,100.03,20,100.49,40,101.15,60,101.41,80,102.04,100,102.44` | AWKWARD | "y = 101" and line "y = 100 + 0.0242x": 3 s.f. turns the intercept 100.0486 into 100 and the estimate 101.26 into 101 (MS 101.3) |
| 6d | 2 | reliability | — | none | |
| 6e | 2 | residual at 60 | `fstat » Residuals » 0,100.03,20,100.49,40,101.15,60,101.41,80,102.04,100,102.44` | OK | ⇒ "x=60: e = -0.0923" (MS -0.0906 from the rounded line) |
| 7a | 4 | r from sums | — | GAP | no PMCC from summary sums (MS r = -0.2744) |
| 7b | 5 | test | `fstat » PMCC test from r » -0.2744,30,5,2` | OK | ⇒ "crit = +/-0.361" |
| 7c | 2 | large sample | — | none | |
| 7d | 2 | effect sizes | — | none | |
| 8a | 1 | explain | — | none | |
| 8b | 1 | paired | — | none | |
| 8c | 10 | paired z test from sums | `fstat » Estimates from sums » 40,72.2,1510` | AWKWARD | ⇒ "s^2 = 35.4"; xbar shown "1.8" (1.805); s must be retyped |
| 8c | | | `fstat » z test for a mean » 0,5.9478,40,1.805,5,1` | OK | ⇒ "z = 1.92" |
| 8d | 1 | problem | — | none | |
| 9a | 2 | lambda from table | `mstat » Frequency table » 0,23,1,42,2,46,3,45,4,20,5,15,6,7,7,2` | OK | ⇒ "mean = 480/200 = 2.4" |
| 9b | 4 | C3, D3, E3 | `fstat » GOF Poisson » ?,5,23,42,46,45,20,15,7,2` | OK | ⇒ "1: O 42, E 43.5, 0.0548" |
| 9c | 1 | pooling | — | none | |
| 9d | 6 | GOF, mu estimated | `fstat » GOF Poisson » ?,5,23,42,46,45,20,15,7,2` | OK | ⇒ "chi^2 = 4.59" |
| 10a | 4 | P(T = 5), T = X - (Y1+Y2) | `fstat » Binomial P(X=k) » 6,0.4,5` | GAP | no distribution of a sum/difference of discrete RVs; terms 0.036864 × 0.046656 + 0.004096 × 0.186624 by hand (MS 0.002484) |
| 10b | 1 | estimate | — | none | read off |
| 10c | 8 | CLT for mean of 100 T | `fstat » E and Var of X+-Y » 2.4,1.44,2.4,1.44` | OK | ⇒ "Var(X-Y) = 72/25" |
| 10c | | | `fstat » Normal P(a<X<b) » 0,sqrt(0.0288),0.255,100` | AWKWARD | ⇒ "P(a<X<b) = 0.0665"; continuity correction 0.255 and Var/100 by hand |
| 11a | 3 | a = 24, b = 20 | `mpure » Simultaneous 2 linear » 1,1,44,2.5,1,80` | AWKWARD | ⇒ "x = 24"; equations from F(1), F(2.5) formed by hand |
| 11b(i) | 1 | F(0) = 0 | — | none | |
| 11b(ii) | 3 | F non-decreasing | `CAS » d/dx » (24x+20)/(9x+15)-4/3` | WRONG | gives "20/(x+5/3)^2"; correct F'(x) = 180/(9x+15)^2 = (20/9)/(x+5/3)^2 — a factor of 9 lost when the quotient is made monic |
| 11c(i) | 1 | F(5) = 1 | — | none | |
| 11c(ii) | 1 | | — | none | |
| 11d | 3 | upper quartile exact | `CAS » solve exact f(x)=0 » (24x+20)/(9x+15)-4/3-3/4` | OK | ⇒ "x = 15/7" |
| 11e | 2 | E(X) | `fstat » pdf from a cdf » (24x+20)/(9x+15)-4/3,0,5` | WRONG | f(x) = 20/(x+5/3)^2 (×9 too big) so "E(X) = 12.7", "Var(X) = -129", "SD = 0"; MS E(X) = 1.414 |
| 11e | | workaround with correct pdf | `fstat » pdf E Var and check » 180/(9x+15)^2,0,5` | OK | ⇒ "E(X) = 1.41" |
| 11f | 2 | mode | `fstat » Mode of a pdf » 180/(9x+15)^2,0,5` | OK | ⇒ "mode = 0" |
| 12 | 6 | prove mean, sd of B(64, 0.1) | — | none | proof |

Parts: 47. Rows: OK 20, WRONG 2, AWKWARD 10, GAP 2, none 16.
