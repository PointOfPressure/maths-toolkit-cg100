# Cases for fstat.py (AQA 7367 Statistics, sections SA to SH).
# Every number in a needle is checked by hand or against the AQA tables.
CASES = [
    # --- SA discrete random variables ---------------------------------------
    # P(X=x) = 0.1, 0.2, 0.3, 0.4 for x = 0..3: E = 2, E(X^2) = 5, Var = 1
    ('SA', 'DRV from table', '0,0.1,1,0.2,2,0.3,3,0.4',
     ['E(X) = 2', 'Var(X) = 1', 'SD = 1', 'mode = 3', 'median = 2']),
    # two equally likely values: cumulative hits 0.5 exactly, so median is 1.5
    ('SA', 'DRV from table', '1,0.5,2,0.5',
     ['E(X) = 3/2', 'Var(X) = 1/4', 'mode = 1, 2', 'median = 3/2']),
    # probabilities that do not sum to 1
    ('SA', 'DRV from table', '0,0.2,1,0.3', ['sum P = 1/2, not 1']),
    # P(X=x) = x/10 on x = 1..4: E = 3, E(X^2) = 10, Var = 1
    ('SA', 'DRV from formula', 'x/10,4',
     ['sum P = 1', 'E(X) = 3', 'Var(X) = 1']),
    # Y = 3X - 2 with E(X) = 5, Var(X) = 4
    ('SA', 'E and Var of aX+b', '3,-2,5,4',
     ['E(aX+b) = 13', 'Var(aX+b) = 36', 'SD(aX+b) = 6']),
    # g(X) = X^2 on X = 1, 2 each with p = 0.5: E = 2.5, E(g^2) = 8.5
    ('SA', 'E of g(X) from table', 'x^2,1,0.5,2,0.5',
     ['E(g(X)) = 5/2', 'E(g(X)^2) = 17/2', 'Var(g(X)) = 9/4']),
    # U on 1..6: E = 3.5, Var = 35/12
    ('SA', 'Discrete uniform 1-n', '6',
     ['P(X=x) = 1/6', 'E(X) = (n+1)/2 = 7/2', 'Var(X) = (n^2-1)/12 = 35/12',
      '(n^2-1)/12']),

    # --- SB Poisson ---------------------------------------------------------
    # Po(2): P(X=3) = 0.180, P(X<=3) = 0.857, P(X>=3) = 0.323
    ('SB', 'Poisson P(X=k)', '2,3',
     ['P(X=k) = 0.18', 'P(X<=k) = 0.857', 'P(X>=k) = 0.323',
      'mean = var = 2']),
    # Po(3): P(X<=4) - P(X<=1) = 0.8153 - 0.1991 = 0.616
    ('SB', 'Poisson a<=X<=b', '3,2,4',
     ['P(a<=X<=b) = 0.616', 'P(X<a) = 0.199']),
    # Po(4): P(X<=6) = 0.889, P(X<=7) = 0.949, so k = 7
    ('SB', 'Poisson inverse', '4,0.9',
     ['k = 7', 'P(X<=k) = 0.949', 'P(X<=k-1) = 0.889']),
    # Po(2) + Po(3) = Po(5): P(Y=5) = 0.175, P(Y<=5) = 0.616
    ('SB', 'Sum of Poissons', '5,2,3',
     ['Po(5)', 'P(Y=k) = 0.175', 'P(Y<=k) = 0.616']),
    # Po(5) upper tail 5%: P(X>=10) = 0.0318 <= 0.05 < P(X>=9); p = P(X>=11)
    ('SB', 'Poisson test upper', '5,11,5',
     ['critical region X >= 10', 'p = 0.0137', 'reject H0',
      'P(Type I) = 0.0318']),
    # Po(9) lower tail 5%: P(X<=3) = 0.0212 <= 0.05 < P(X<=4)
    ('SB', 'Poisson test lower', '9,3,5',
     ['critical region X <= 3', 'p = 0.0212', 'reject H0',
      'P(Type I) = 0.0212']),
    # Po(1) at 5%: even P(X=0) = 0.368 > 0.05, so nothing can reject H0
    ('SB', 'Poisson test lower', '1,0,5',
     ['critical region is empty', 'accept H0', 'P(Type I) = 0']),
    # 2,3,1,4,2,0,3,2: mean 2.125, s^2 = 10.875/7 = 1.554
    ('SB', 'Poisson model check', '2,3,1,4,2,0,3,2',
     ['mean = 2.12', 'variance = 1.55', 'var/mean = 0.731']),

    # --- SC Type I and Type II errors ---------------------------------------
    # B(20, 0.5): P(X<=5) = P(X>=15) = 0.0207, so alpha = 0.0414
    ('SC', 'Type I binomial', '20,0.5,5,15',
     ['reject if X <= 5 or X >= 15', 'P(Type I) = 0.0414', 'as a % = 4.14%']),
    # true p = 0.8: P(accept) = P(6<=X<=14) = 0.196
    ('SC', 'Type II binomial', '20,0.5,5,15,0.8',
     ['P(Type II) = 0.196', 'power = 0.804', 'P(Type I) = 0.0414']),
    # Po(5): P(X<=1) = 0.0404, P(X>=10) = 0.0318
    ('SC', 'Type I Poisson', '5,1,10',
     ['P(Type I) = 0.0723', 'P(X<=1) = 0.0404', 'P(X>=10) = 0.0318']),
    # upper tail only: P(X>=10) = 0.0318 for Po(5)
    ('SC', 'Type I Poisson', '5,?,10',
     ['reject if X >= 10', 'P(Type I) = 0.0318']),
    # true mu = 8: P(accept) = P(2<=X<=9) = 0.717 - 0.003 = 0.714
    ('SC', 'Type II Poisson', '5,1,10,8',
     ['P(Type II) = 0.714', 'power = 0.286']),
    # SE = 15/5 = 3 and the critical values are mu0 +/- 1.96*3, so alpha = 5%
    ('SC', 'Type I Normal', '100,15,25,94.12,105.88',
     ['P(Type I) = 0.05', 'SE = sigma/sqrt(n) = 3']),
    # true mu = 105: beta = Phi(0.293) - Phi(-3.63) = 0.615
    ('SC', 'Type II Normal', '100,15,25,94.12,105.88,105',
     ['P(Type II) = 0.615', 'power = 0.385']),

    # --- SD continuous random variables -------------------------------------
    # f(x) = 3x^2 on [0,1]: E = 3/4, E(X^2) = 3/5, Var = 3/80
    ('SD', 'pdf E Var and check', '3x^2,0,1',
     ['E(X) = 3/4', 'E(X^2) = 3/5', 'Var(X) = 0.0375', 'valid pdf: yes']),
    # x^2 integrates to 1/3, so it is not a pdf
    ('SD', 'pdf E Var and check', 'x^2,0,1',
     ['valid pdf: no', 'not a pdf: int f = 0.333']),
    # F(x) = x^3, so m = 0.5^(1/3) = 0.794, Q1 = 0.630, Q3 = 0.909
    ('SD', 'pdf median quartiles', '3x^2,0,1',
     ['median m = 0.794', 'Q1 = 0.63', 'Q3 = 0.909']),
    # f(x) = 6x(1-x) peaks at x = 0.5 where f = 1.5
    ('SD', 'Mode of a pdf', '6x(1-x),0,1',
     ['mode = 0.5', 'f(mode) = 1.5']),
    # F(x) = x^3 so F(0.5) = 0.125
    ('SD', 'cdf F(x) from a pdf', '3x^2,0,1,0.5',
     ['F(0.5) = 0.125', 'P(X>t) = 0.875', 'F(x) = x^3']),
    # 0.6^3 - 0.2^3 = 0.216 - 0.008 = 0.208
    ('SD', 'pdf P(c<X<d)', '3x^2,0,1,0.2,0.6', ['P(c<X<d) = 0.208']),
    # E(X^2) for f = 3x^2 is 3/5
    ('SD', 'E of g(X) from a pdf', 'x^2,3x^2,0,1', ['E(g(X)) = 3/5']),
    # triangular pdf x on [0,1], 2-x on [1,2]: E = 1, Var = 1/6, median 1
    ('SD', 'Piecewise pdf', 'x,2-x,0,1,2',
     ['E(X) = 1', 'Var(X) = 1/6', 'median = 1', 'valid pdf: yes']),
    # U(2,8): E = 5, Var = 36/12 = 3, P(3<X<5) = 2/6
    ('SD', 'Rectangular U(a,b)', '2,8,3,5',
     ['f(x) = 1/(b-a) = 1/6', 'E(X) = (a+b)/2 = 5',
      'Var(X) = (b-a)^2/12 = 3', 'P(c<X<d) = 1/3']),
    # no interval asked for
    ('SD', 'Rectangular U(a,b)', '2,8,?,?', ['E(X) = (a+b)/2 = 5']),
    # Y = 2X + 1 with E(X) = 10, Var(X) = 4
    ('SD', 'E and Var of aX+b', '2,1,10,4',
     ['E(aX+b) = 21', 'Var(aX+b) = 16']),
    # independent X, Y: variances add either way round
    ('SD', 'E and Var of X+Y', '3,2,5,4',
     ['E(X+Y) = 8', 'Var(X+Y) = 6', 'E(X-Y) = -2', 'Var(X-Y) = 6']),

    # --- SE chi squared for association -------------------------------------
    # 2x2 with E = 15, 20, 15, 20 and |O-E| = 5: Yates gives 4.5^2 * 0.35 = 4.725
    ('SE', 'Chi-sq association', '2,2,20,15,10,25',
     ['chi^2 = 4.72', 'df = 1', '5% crit = 3.84', '1% crit = 6.64',
      'reject H0: association', 'Yates', 'E r1: 15 20']),
    # 2x3: E row 1 = 12, 20, 28 and chi^2 = 0.794 with df = 2
    ('SE', 'Chi-sq association', '2,3,10,20,30,20,30,40',
     ['chi^2 = 0.794', 'df = 2', '5% crit = 5.99',
      'accept H0: no association', 'E r1: 12 20 28']),
    # small counts: E = 3.11, 3.89, 4.89, 6.11 so three cells are under 5
    ('SE', 'Chi-sq association', '2,2,3,4,5,6',
     ['3 cell(s) have E < 5', 'combine rows or columns first']),
    ('SE', 'Expected frequencies', '2,2,20,15,10,25',
     ['r1: 15 20', 'r2: 15 20', 'row totals: 35 35', 'col totals: 30 40']),
    # chi^2 table: 5% point for df = 3 is 7.815
    ('SE', 'Chi-sq from statistic', '7.5,3,5',
     ['crit = 7.82', 'p = 0.0576', 'accept H0 at 5%']),
    # the table stops at df = 100
    ('SE', 'Chi-sq from statistic', '160,120,5',
     ['no chi table entry for df = 120', 'reject H0 at 5%']),

    # --- SF exponential -----------------------------------------------------
    # L = 0.5: mean 2, Var 4, median ln2/0.5 = 1.386
    ('SF', 'Exponential Exp(L)', '0.5',
     ['mean = 1/L = 2', 'Var = 1/L^2 = 4', 'median = ln2/L = 1.39']),
    # F(1) = 1 - e^-0.5 = 0.393, F(3) = 1 - e^-1.5 = 0.777
    ('SF', 'Exponential probs', '0.5,1,3',
     ['P(X<a) = 0.393', 'P(X>a) = 0.607', 'P(a<X<b) = 0.383']),
    ('SF', 'Exponential probs', '0.5,1,?', ['P(X<a) = 0.393']),
    # 2 events per unit, t = 1.5: P(no event) = e^-3 = 0.0498
    ('SF', 'Waits from a rate', '2,1.5',
     ['P(T>t) = 0.0498', 'P(T<t) = 0.95', 'mean wait = 0.5']),
    # e^-0.8 = 0.449 both ways
    ('SF', 'Memoryless check', '0.4,3,2',
     ['P(X>s+t|X>s) = 0.449', 'P(X>t) = 0.449', 'equal: memoryless']),

    # --- SG one sample t ----------------------------------------------------
    # 11,12,9,10,13,11,12: xbar = 11.14, s = 1.345, t = 2.25, t(6, 2.5%) = 2.447
    ('SG', 't-test from data', '10,5,2,11,12,9,10,13,11,12',
     ['t = 2.25', 'df = 6', 'crit = +/-2.45', 'p = 0.0656',
      'accept H0 at 5%']),
    # n = 16, SE = 0.5, t = 3, t(15, 2.5%) = 2.131
    ('SG', 't-test from summary', '16,11.5,2,10,5,2',
     ['t = 3', 'df = 15', 'crit = +/-2.13', 'p = 0.00897',
      'reject H0 at 5%']),
    # same data one tail: t(15, 5%) = 1.753
    ('SG', 't-test from summary', '16,11.5,2,10,5,1',
     ['crit = 1.75', 'p = 0.00449', 'reject H0 at 5%']),

    # --- SH confidence intervals --------------------------------------------
    # 50 +/- 1.96*4/5 = 50 +/- 1.568
    ('SH', 'CI mean sigma known', '50,4,25,95',
     ['(48.4, 51.6)', 'z* = 1.96', 'SE = sigma/sqrt(n) = 0.8']),
    # n = 7 so t with df = 6: 11.14 +/- 2.447*0.5085 = 11.14 +/- 1.244
    ('SH', 'CI from data', '95,11,12,9,10,13,11,12',
     ['(9.9, 12.4)', 't* = 2.45 (df 6)']),
    # n = 40 >= 30 so z: 50 +/- 2.576*6/sqrt(40) = 50 +/- 2.44
    ('SH', 'CI from summary', '40,50,6,99',
     ['(47.6, 52.4)', 'z* = 2.58', 'n >= 30 so z with s for sigma']),
    # 92% is not a tabulated level
    ('SH', 'CI from summary', '10,50,6,92',
     ['t* = 1.97 (df 9)', 'table has no 92% entry']),
    ('SH', 'Is mu0 in the CI', '48.4,51.6,50',
     ['centre = 50', 'width = 3.2', 'mu0 inside the interval', 'accept H0']),
    # n >= (2*1.96*4/2)^2 = 61.5
    ('SH', 'Sample size for width', '4,2,95',
     ['n = 62', 'z* = 1.96', 'exact n = 61.5']),
]
