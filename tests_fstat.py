# Cases for fstat.py (OCR B (MEI) H645 Statistics Major Y422 / Minor Y432).
# Every number in a needle is checked by hand, by an independent script
# (exact enumeration, series for chi^2) or against standard tables.
CASES = [
    # --- D discrete random variables ----------------------------------------
    # P(X=x) = 0.1, 0.2, 0.3, 0.4 for x = 0..3: E = 2, E(X^2) = 5, Var = 1
    ('D', 'DRV from table', '0,0.1,1,0.2,2,0.3,3,0.4',
     ['E(X) = 2', 'Var(X) = 1', 'SD = 1', 'mode = 3', 'median = 2']),
    # two equally likely values: cumulative hits 0.5 exactly, so median is 1.5
    ('D', 'DRV from table', '1,0.5,2,0.5',
     ['E(X) = 3/2', 'Var(X) = 1/4', 'mode = 1, 2', 'median = 3/2']),
    ('D', 'DRV from table', '0,0.2,1,0.3', ['sum P = 1/2, not 1']),
    # P(X=x) = x/10 on x = 1..4: E = 3, E(X^2) = 10, Var = 1
    ('D', 'DRV from formula', 'x/10,1,4',
     ['sum P = 1', 'E(X) = 3', 'Var(X) = 1', 'E(X^2) = sum x^2*p = 10']),
    # P(X=x) = kx^2 on 1..3: k = 1/14, E = 36/14, E(X^2) = 98/14 = 7
    ('D', 'DRV find k', 'x^2,1,3',
     ['k = 1/14', 'E(X) = 18/7', 'Var(X) = 19/49']),
    ('D', 'E(g(X)) from table', 'x^2,1,0.5,2,0.5',
     ['E(g(X)) = 5/2', 'E(g(X)^2) = 17/2', 'Var(g(X)) = 9/4']),
    # Y = -2 + 3X with E(X) = 5, Var(X) = 4
    ('D', 'E and Var of a+bX', '-2,3,5,4',
     ['E(a+bX) = 13', 'Var(a+bX) = 36', 'SD(a+bX) = 6']),
    ('D', 'E and Var of X+-Y', '3,2,5,4',
     ['E(X+Y) = 8', 'E(X-Y) = -2', 'Var(X+Y) = 6', 'Var(X-Y) = 6']),
    # fair die: E = 7/2, Var = 35/12, P(2<=X<=4) = 3/6
    ('D', 'Discrete uniform', '1,6,2,4',
     ['P(X=x) = 1/n = 1/6', 'E(X) = (a+b)/2 = 7/2',
      'Var(X) = (n^2-1)/12 = 35/12', 'P(c<=X<=d) = 1/2']),
    # 3..10: n = 8, Var = 63/12
    ('D', 'Discrete uniform', '3,10',
     ['P(X=x) = 1/n = 1/8', 'E(X) = (a+b)/2 = 13/2',
      'Var(X) = (n^2-1)/12 = 21/4']),

    # --- B binomial and Poisson ---------------------------------------------
    # Po(2): P(X=3) = 0.180, P(X<=3) = 0.857, P(X>=3) = 0.323
    ('B', 'Poisson P(X=k)', '2,3',
     ['P(X=k) = 0.18', 'P(X<=k) = 0.857', 'P(X>=k) = 0.323',
      'mean = var = 2']),
    # Po(3): P(X<=4) - P(X<=1) = 0.8153 - 0.1991 = 0.616
    ('B', 'Poisson a<=X<=b', '3,2,4',
     ['P(a<=X<=b) = 0.616', 'P(X<a) = 0.199']),
    # Po(4): P(X<=6) = 0.889, P(X<=7) = 0.949, so k = 7
    ('B', 'Poisson least k', '4,0.9',
     ['k = 7', 'P(X<=k) = 0.949', 'P(X<=k-1) = 0.889']),
    # Po(2) + Po(3) = Po(5): P(Y=5) = 0.175, P(Y<=5) = 0.616
    ('B', 'Sum of Poissons', '5,2,3',
     ['Po(5)', 'P(Y=k) = 0.175', 'P(Y<=k) = 0.616']),
    # B(100, 0.03): P(X=2) = 4950*0.0009*0.97^98 = 0.225; Po(3): 4.5e^-3 = 0.224
    ('B', 'Poisson approx to B', '100,0.03,2',
     ['Po(3) approximates B', 'Po P(X=k) = 0.224', 'B  P(X=k) = 0.225',
      'Po P(X<=k) = 0.423', 'B  P(X<=k) = 0.42']),
    # B(10, 0.5) is not a Poisson situation
    ('B', 'Poisson approx to B', '10,0.5,5',
     ['n not large or p not small:', 'B  P(X=k) = 0.246']),
    # 2,3,1,4,2,0,3,2: mean 2.125, s^2 = 10.875/7 = 1.554
    ('B', 'Poisson model check', '2,3,1,4,2,0,3,2',
     ['mean = 2.12', 'variance = 1.55', 'var/mean = 0.731',
      'Po plausible']),
    # B(10, 0.3): P(X=3) = 120*0.027*0.7^7 = 0.267, P(X<=3) = 0.650
    ('B', 'Binomial P(X=k)', '10,0.3,3',
     ['P(X=k) = 0.267', 'P(X<=k) = 0.65', 'mean np = 3',
      'var np(1-p) = 2.1']),

    # --- G geometric --------------------------------------------------------
    # p = 0.2: P(X=3) = 0.8^2*0.2 = 0.128, P(X>3) = 0.512
    ('G', 'Geometric P(X=r)', '0.2,3',
     ['P(X=r) = 0.128', 'P(X<=r) = 0.488', 'P(X>r) = 0.512',
      'mean 1/p = 5', 'var (1-p)/p^2 = 20']),
    # p = 1/2: P(2<=X<=4) = 1/2 - 1/16
    ('G', 'Geometric a<=X<=b', '0.5,2,4',
     ['P(a<=X<=b) = 7/16', 'mean 1/p = 2', 'var (1-p)/p^2 = 2']),
    # 0.8^10 = 0.107 > 0.1 >= 0.8^11 = 0.0859, so r = 11
    ('G', 'Geometric least r', '0.2,0.9',
     ['r = 11', 'P(X<=r) = 0.914', 'P(X<=r-1) = 0.893']),

    # --- C continuous random variables --------------------------------------
    # f(x) = 3x^2 on [0,1]: E = 3/4, E(X^2) = 3/5, Var = 3/80
    ('C', 'pdf E Var and check', '3x^2,0,1',
     ['E(X) = 3/4', 'E(X^2) = 3/5', 'Var(X) = 0.0375', 'valid pdf: yes']),
    ('C', 'pdf E Var and check', 'x^2,0,1',
     ['valid pdf: no', 'not a pdf: int f = 0.333']),
    # F(x) = x^3, so m = 0.5^(1/3) = 0.794, Q1 = 0.630, Q3 = 0.909
    ('C', 'pdf median quartiles', '3x^2,0,1',
     ['median m = 0.794', 'Q1 = 0.63', 'Q3 = 0.909']),
    # f(x) = 6x(1-x) peaks at x = 0.5 where f = 1.5
    ('C', 'Mode of a pdf', '6x(1-x),0,1', ['mode = 0.5', 'f(mode) = 1.5']),
    ('C', 'Mode of a pdf', '2x,0,1',
     ['mode = 1', 'mode is at an end of the range']),
    ('C', 'cdf F(x) from a pdf', '3x^2,0,1,0.5',
     ['F(0.5) = 0.125', 'P(X>t) = 0.875', 'F(x) = x^3']),
    # R25: F = (x^2+2x)/8 on [0,2] -> f = (x+1)/4, E = 7/6, E(X^2) = 5/3
    ('C', 'pdf from a cdf', '(x^2+2x)/8,0,2',
     ['f(x) = (x+1)/4', 'E(X) = 7/6', 'E(X^2) = 5/3', 'Var(X) = 11/36']),
    ('C', 'pdf from a cdf', 'x^3,0,1', ['f(x) = 3*x^2', 'E(X) = 3/4']),
    ('C', 'pdf from a cdf', 'x^2,0,2',
     ['F(b) = 4, should be 1', 'not a cdf on [a, b]: no E(X)']),
    # F = x^2/4 on [0,2]: m = sqrt2, Q1 = 1, Q3 = sqrt3
    ('C', 'cdf median quartiles', 'x^2/4,0,2',
     ['median = 1.41', 'Q1 = 1', 'Q3 = 1.73', 'IQR = 0.732']),
    # F = x^3: 90th percentile 0.9^(1/3) = 0.965
    ('C', 'cdf median quartiles', 'x^3,0,1,0.9',
     ['median = 0.794', 'F(x) = p at x = 0.965']),
    # 0.6^3 - 0.2^3 = 0.216 - 0.008 = 0.208
    ('C', 'pdf P(c<X<d)', '3x^2,0,1,0.2,0.6', ['P(c<X<d) = 0.208']),
    ('C', 'E of g(X) from a pdf', 'x^2,3x^2,0,1', ['E(g(X)) = 3/5']),
    # triangular pdf x on [0,1], 2-x on [1,2]: E = 1, Var = 1/6, median 1
    ('C', 'Piecewise pdf', 'x,2-x,0,1,2',
     ['E(X) = 1', 'Var(X) = 1/6', 'median = 1', 'valid pdf: yes']),
    # U(2,8): E = 5, Var = 36/12 = 3, P(3<X<5) = 2/6
    ('C', 'Rectangular U(a,b)', '2,8,3,5',
     ['f(x) = 1/(b-a) = 1/6', 'E(X) = (a+b)/2 = 5',
      'Var(X) = (b-a)^2/12 = 3', 'P(c<X<d) = 1/3']),

    # --- N Normal -----------------------------------------------------------
    # N(50, 10^2): Phi(1.5) - Phi(-1) = 0.9332 - 0.1587 = 0.7745
    ('N', 'Normal P(a<X<b)', '50,10,40,65',
     ['P(a<X<b) = 0.775', 'P(X<a) = 0.159', 'P(X>b) = 0.0668']),
    ('N', 'Inverse Normal', '50,10,0.975', ['x = 69.6', 'z = 1.96']),
    # 4..8: xbar = 6, s^2 = 10/4 = 2.5, s = 1.58; 3 of 5 within 1 s
    ('N', 'Normal fit to data', '4,5,6,7,8',
     ['mu est = xbar = 6', 'sigma est = s = 1.58', 'within 1 s: 60%',
      'within 2 s: 100%']),
    # (5-6)/1.581 = -0.632: P = 1 - 2*0.2635 = 0.473
    ('N', 'Normal P from sample', '5,7,4,5,6,7,8',
     ['P(a<X<b) = 0.473', 'P(X<a) = 0.264', 'small sample']),
    # X - Y with X ~ N(50, 9), Y ~ N(40, 16): W ~ N(10, 25), P(W<0) = Phi(-2)
    ('N', 'aX+bY+c', '1,-1,0,50,9,40,16,0',
     ['E(W) = 10', 'Var(W) = 25', 'SD(W) = 5', 'P(W<k) = 0.0228']),
    ('N', 'aX+bY+c', '2,3,1,10,4,5,1,?',
     ['E(W) = 36', 'Var(W) = 25']),
    # n = 5, Var(X) = 4: Var(5X) = 100, Var(sum) = 20; P(sum<55) = Phi(1.118)
    ('N', 'nX vs X1+..+Xn', '10,4,5,55',
     ['E(nX) = E(sum) = 50', 'Var(nX) = n^2Var(X) = 100',
      'Var(X1+..+Xn) = 20', 'Var(Xbar) = Var(X)/n = 4/5',
      'P(nX<k) = 0.691', 'P(sum<k) = 0.868']),
    ('N', 'Normal prob plot', '2.1,3.4,1.9,2.8,3.0,2.5,2.2,3.7,2.9,2.6',
     ['r of plot = 0.99', 'close to a line']),
    # strongly skewed data bend away from the line
    ('N', 'Normal prob plot', '1,1,1,1,1,1,2,2,3,50',
     ['curved: Normal is doubtful']),

    # --- R bivariate data ---------------------------------------------------
    # (1,2) (2,4) (3,5) (4,4) (5,5): Sxx = 10, Syy = 6, Sxy = 6, r = 6/sqrt60
    ('R', 'Scatter diagram', '1,2,2,4,3,5,4,4,5,5',
     ['n = 5', 'r = 0.775', 'means (3, 4)']),
    ('R', 'PMCC r', '1,2,2,4,3,5,4,4,5,5',
     ['r = 0.775', 'r^2 = 0.6', 'Sxx = 10, Syy = 6', 'Sxy = 6']),
    # n = 5, 5% one tail: table crit 0.8054 > 0.775
    ('R', 'PMCC test from data', '5,1,1,2,2,4,3,5,4,4,5,5',
     ['r = 0.775', 'crit = 0.805', 'do not reject H0 at 5%']),
    # n = 10: 5% one tail 0.5494, 5% two tail 0.6319 (table)
    ('R', 'PMCC test from r', '0.6,10,5,1',
     ['crit = 0.549', 'reject H0 at 5%', 'p = 0.0333']),
    ('R', 'PMCC test from r', '0.6,10,5,2',
     ['crit = +/-0.632', 'do not reject H0 at 5%']),
    # n = 40 is past the table: t(38, 2.5%) = 2.024, 2.024/sqrt(2.024^2+38)
    ('R', 'PMCC test from r', '-0.3,40,5,2',
     ['crit = +/-0.312', 'do not reject H0 at 5%', 'crit = t/sqrt']),
    ('R', 'PMCC test from r', '-0.6,10,5,1', ['crit = -0.549', 'rho < 0']),
    # ranks swapped in pairs: sum d^2 = 8, rs = 1 - 48/504 = 0.905
    ('R', 'Spearman rs', '1,2,2,1,3,4,4,3,5,6,6,5,7,8,8,7',
     ['rs = 0.905', 'sum d^2 = 8, n = 8']),
    # ties: rs is the PMCC of the ranks (1.5,1.5,3,4 against 1,2,3,4)
    ('R', 'Spearman rs', '1,1,1,2,2,3,3,4', ['rs = 0.949', 'ties']),
    # n = 8 exact 5% one tail: D <= 30, rs >= 1 - 180/504 = 0.643
    ('R', 'Spearman test data', '5,1,1,2,2,1,3,4,4,3,5,6,6,5,7,8,8,7',
     ['rs = 0.905', 'crit = 0.643', 'reject H0 at 5%']),
    # standard exact value: n = 10, 5% one tail -> D <= 72, rs >= 0.5636
    ('R', 'Spearman test from rs', '0.55,10,5,1',
     ['crit = 0.564', 'do not reject H0 at 5%']),
    # n = 20 is the last exact row: D <= 824, rs >= 1 - 4944/7980 = 0.380
    ('R', 'Spearman test from rs', '0.4,20,5,1',
     ['crit = 0.38', 'reject H0 at 5%']),
    # n = 25 is past the exact table: t(23, 5%) = 1.714 -> 0.337 (flagged)
    ('R', 'Spearman test from rs', '0.4,25,5,1',
     ['crit = 0.337', 'reject H0 at 5%', 'approx crit from t']),
    # n = 5 two tail 5%: only rs = 1 is extreme enough (P = 1/120)
    ('R', 'Spearman test from rs', '0.9,5,5,2',
     ['crit = +/-1', 'do not reject H0 at 5%']),
    # n = 4 two tail 5%: even rs = 1 has P = 1/24 > 0.025
    ('R', 'Spearman test from rs', '1,4,5,2',
     ['too small for this level']),
    # b = 6/10, a = 4 - 0.6*3 = 2.2; residuals -0.8 0.6 1 -0.6 -0.2
    ('R', 'Regression y on x', '1,2,2,4,3,5,4,4,5,5',
     ['y = 2.2 + 0.6x', 'r^2 = 0.6', 'resid -0.8',
      'sum of squared residuals = 2.4']),
    # d = Sxy/Syy = 1, c = 3 - 4 = -1
    ('R', 'Regression x on y', '1,2,2,4,3,5,4,4,5,5',
     ['x = -1 + 1y', 'd = 1', 'c = -1']),
    ('R', 'Both regression lines', '1,2,2,4,3,5,4,4,5,5',
     ['y = 2.2 + 0.6x', 'x = -1 + 1y', 'meet at (3, 4)',
      'b*d = r^2 = 0.6']),
    ('R', 'Residuals', '1,2,2,4,3,5,4,4,5,5',
     ['x=1: e = -0.8', 'x=3: e = 1', 'sum e^2 = 2.4',
      'biggest at x = 3']),
    ('R', 'Predict y from x', '7,1,2,2,4,3,5,4,4,5,5',
     ['y = 6.4', 'extrapolation']),
    ('R', 'Predict x from y', '4.5,1,2,2,4,3,5,4,4,5,5',
     ['x = 3.5', 'interpolation']),

    # --- H chi-squared ------------------------------------------------------
    # 2x3: E row 1 = 12, 20, 28 and chi^2 = 0.794 with df = 2
    ('H', 'Chi-sq association', '2,3,5,10,20,30,20,30,40',
     ['chi^2 = 0.794', 'df = 2', 'crit = 5.99', 'p = 0.672',
      'do not reject H0 at 5%', 'E r1: 12 20 28']),
    # 2x2, no Yates (MEI): 25*(1/15+1/20)*2 = 5.83 > 3.84
    ('H', 'Chi-sq association', '2,2,5,20,15,10,25',
     ['chi^2 = 5.83', 'df = 1', 'crit = 3.84', 'p = 0.0157',
      'reject H0 at 5%', 'evidence of association', 'no Yates']),
    # small counts: E = 3.11, 3.89, 4.89, 6.11 so three cells are under 5
    ('H', 'Chi-sq association', '2,2,5,3,4,5,6',
     ['3 cell(s) have E < 5']),
    ('H', 'Chi-sq contributions', '2,2,20,15,10,25',
     ['r1: +1.67 -1.25', 'r2: -1.67 +1.25', 'chi^2 = 5.83']),
    ('H', 'Expected frequencies', '2,2,20,15,10,25',
     ['r1: 15 20', 'r2: 15 20', 'row totals: 35 35', 'col totals: 30 40']),
    # E = 25, 50, 25: chi^2 = 1 + 0 + 1 = 2; df 2 so p = e^-1 = 0.368
    ('H', 'GOF given probs', '5,30,0.25,50,0.5,20,0.25',
     ['chi^2 = 2', 'df = 2', 'p = 0.368', 'do not reject H0 at 5%']),
    ('H', 'GOF given probs', '5,30,0.5,50,0.4', ['sum to 0.9, not 1']),
    # same with one estimated parameter: df = 1, p = 0.157
    ('H', 'GOF given expected', '5,1,30,25,50,50,20,25',
     ['chi^2 = 2', 'df = 1', 'crit = 3.84', 'p = 0.157']),
    # die: (4+4+1+1+16+16)/10 = 4.2, df 5, crit 11.07, p = 0.521
    ('H', 'GOF uniform', '5,8,12,9,11,6,14',
     ['chi^2 = 4.2', 'df = 5', 'crit = 11.1', 'p = 0.521']),
    # B(4, 0.5) given: E = 6.25, 25, 37.5, 25, 6.25; chi^2 = 4.67, df 4
    ('H', 'GOF binomial', '4,0.5,5,10,30,35,20,5',
     ['chi^2 = 4.67', 'df = 4', 'crit = 9.49', 'p = 0.323']),
    # p estimated 180/400 = 0.45; E(4) = 4.10 pooled with x = 3; df = 4-1-1
    ('H', 'GOF binomial', '4,?,5,10,30,35,20,5',
     ['chi^2 = 0.193', 'df = 2', 'p = 0.908', 'xbar/n = 0.45',
      'pooled 5 cells into 4', '3-4: O 25, E 24.1']),
    # Po(1) given, cells 0,1,2,3+ after pooling: chi^2 = 2.16, df 3
    ('H', 'GOF Poisson', '1,5,30,40,20,7,3',
     ['chi^2 = 2.16', 'df = 3', 'crit = 7.82', 'p = 0.541',
      '3-4+: O 10, E 8.03']),
    # mu estimated as 113/100 = 1.13: chi^2 = 0.549, df = 4-1-1 = 2
    ('H', 'GOF Poisson', '?,5,30,40,20,7,3',
     ['chi^2 = 0.549', 'df = 2', 'p = 0.76', 'mu estimated: xbar = 1.13']),
    # chi^2 table: 5% point for df = 3 is 7.815
    ('H', 'Chi-sq crit and p', '7.5,3,5',
     ['crit = 7.82', 'p = 0.0576', 'do not reject H0 at 5%']),
    # 7% is not tabulated: solve P(chi^2_3 > c) = 0.07
    ('H', 'Chi-sq crit and p', '7.5,3,7',
     ['crit = 7.06', 'reject H0 at 7%', 'not in the table']),

    # --- I inference --------------------------------------------------------
    # 2,4,4,4,5,5,7,9: xbar 5, Sxx 32, s^2 = 32/7 = 4.57
    ('I', 'Estimates from data', '2,4,4,4,5,5,7,9',
     ['xbar = 5', 's^2 = 4.57', 's = 2.14', 'SE = s/sqrt(n) = 0.756',
      'divisor n would give 4']),
    # Sxx = 270 - 2500/10 = 20, s^2 = 20/9
    ('I', 'Estimates from sums', '10,50,270',
     ['xbar = 5', 's^2 = 2.22', 'SE = s/sqrt(n) = 0.471']),
    # SE = 3, z = 2: two tail p = 0.0455
    ('I', 'z test for a mean', '100,15,25,106,5,2',
     ['z = 2', 'crit = +/-1.96', 'p = 0.0455', 'reject H0 at 5%']),
    # z = -5/3: one tail p = 0.0478 < 0.05
    ('I', 'z test for a mean', '100,15,25,95,5,1',
     ['z = -1.67', 'crit = -1.64', 'p = 0.0478', 'mu < 100']),
    # xbar = 78/7, sigma = 1.2: z = (8/7)/(1.2/sqrt7) = 2.52
    ('I', 'z test from data', '10,1.2,5,1,11,12,9,10,13,11,12',
     ['z = 2.52', 'crit = 1.64', 'p = 0.00587', 'reject H0 at 5%']),
    # sigma unknown and n = 7: s = 1.345 used, with a caveat
    ('I', 'z test from data', '10,?,5,2,11,12,9,10,13,11,12',
     ['z = 2.25', 'n < 30: s for sigma is rough']),
    # 50 +/- 1.96*4/5 = 50 +/- 1.568
    ('I', 'CI mean sigma known', '50,4,25,95',
     ['(48.4, 51.6)', 'z* = 1.96', 'SE = sigma/sqrt(n) = 0.8']),
    # n = 7 so t with df = 6: 11.14 +/- 2.447*0.5085
    ('I', 'CI mean from data', '95,11,12,9,10,13,11,12',
     ['(9.9, 12.4)', 't* = 2.45 (df 6)']),
    # n = 40 >= 30 so z: 50 +/- 2.576*6/sqrt(40) = 50 +/- 2.44
    ('I', 'CI mean from summary', '40,50,6,99',
     ['(47.6, 52.4)', 'z* = 2.58', 'n >= 30 so z']),
    ('I', 'CI mean from summary', '10,50,6,92',
     ['t* = 1.97 (df 9)', 'not in the table: computed']),
    # d = 2,1,2,3,1: dbar 1.8, s = sqrt(0.7), t(4) = 2.776: 1.8 +/- 1.04
    ('I', 'CI paired data', '95,12,10,15,14,11,9,14,11,13,12',
     ['(0.761, 2.84)', 't* = 2.78 (df 4)', 'dbar = 1.8']),
    ('I', 'CI to test mu0', '48.4,51.6,50',
     ['mu0 inside the CI', 'do not reject H0', 'centre = 50']),
    ('I', 'CI to test mu0', '48.4,51.6,52', ['mu0 outside the CI']),
    # n >= (2*1.96*4/2)^2 = 61.5
    ('I', 'Sample size for width', '4,2,95',
     ['n = 62', 'z* = 1.96', 'exact n = 61.5']),

    # --- W Wilcoxon (critical values from the exact subset-sum count) -------
    # d = x - 5.5 has no ties; negative ranks 2, 3, 7 so T = 12;
    # P(T <= 12) = 67/1024 = 0.0654 by enumerating all 2^10 sign patterns
    ('W', 'Wilcoxon single sample',
     '5.5,5,1,5.2,6.8,4.9,7.4,6.15,5.7,7.9,6.6,8.3,4.1',
     ['T = 12', 'W+ = 43, W- = 12', 'crit: reject if T <= 10',
      'p = 0.0654', 'do not reject H0 at 5%']),
    # ties at |d| = 0.4 and 1.3: T = 1.5 + 5.5 + 3 = 10 <= 10
    ('W', 'Wilcoxon single sample',
     '12.5,5,1,12.1,13.5,11.2,14.8,15.1,12.9,13.8,16.2,11.9,14.4',
     ['T = 10', 'reject H0 at 5%', 'tied ranks']),
    # only d = -0.3 is negative, rank 1: T = 1, two tail p = 2*2/1024
    ('W', 'Wilcoxon paired',
     '5,2,20,15.5,18,18.3,25,19,16,14.2,22,17.1,19,13.4,21,16.8,17,15.9,'
     '23,22.1,24,17.3',
     ['T = 1', 'W+ = 54, W- = 1', 'crit: reject if T <= 8',
      'p = 0.00391', 'reject H0 at 5%']),
    # one pair with d = 0 is dropped
    ('W', 'Wilcoxon paired', '5,1,3,3,5,4,6,4,8,5',
     ['1 zero difference(s) dropped', 'n = 3 non-zero']),
    # standard values: n = 10 two tail 5% -> 8; n = 20 one tail 5% -> 60
    ('W', 'Wilcoxon crit value', '10,5,2',
     ['reject if T <= 8', 'P(T<=8) = 0.0244', 'P(T<=9) = 0.0322']),
    ('W', 'Wilcoxon crit value', '20,5,1', ['reject if T <= 60']),
    # n = 5: P(T = 0) = 1/32 > 0.025
    ('W', 'Wilcoxon crit value', '5,5,2',
     ['no critical value', 'P(T=0) = 0.0312']),
    # n = 10: P(T <= 8) = 25/1024, two tail 0.0488
    ('W', 'Wilcoxon from T', '8,10,5,2',
     ['crit: reject if T <= 8', 'p = 0.0488', 'reject H0 at 5%']),
    # W+ = 47 means T = 55 - 47 = 8
    ('W', 'Wilcoxon from T', '47,10,5,2', ['T = 8']),

    # --- Z simulation (fixed seeds, so the counts are reproducible) ---------
    ('Z', 'Simulate binomial', '10,0.3,1000,42',
     ['sim mean = 2.97 (3)', 'sim var = 2.07 (2.1)', 'seed 42']),
    ('Z', 'Simulate Poisson', '3,2000,7',
     ['sim mean = 3 (3)', 'sim var = 3.05 (3)']),
    ('Z', 'Simulate geometric', '0.25,1000,1', ['(4)', '(12)', 'x=1: 246']),
    ('Z', 'Simulate Normal', '50,10,2000,3',
     ['sim mean = 49.9 (50)', 'sim var = 97.9 (100)',
      'within 1.96 sd: 95.5%']),
    ('Z', 'Simulate U(a,b)', '0,6,2000,5', ['sim mean = 3 (3)', '(3)']),
    # Var of a mean of 12 U(0,1) = 1/144 = 0.00694
    ('Z', 'Simulate sample means', '0,1,12,1000,9',
     ['sim var = 0.00695 (0.00694)']),
    ('Z', 'Simulate a DRV', '1000,4,1,0.2,2,0.5,3,0.3',
     ['(2.1)', '(0.49)', 'x=2: 509']),
]
