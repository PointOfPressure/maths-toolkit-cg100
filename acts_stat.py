# Statistics actions (acts.py has the registry): B(n, p) (mockup B),
# N(mu, sigma^2), data lists, two lists, and with nothing typed the boxes:
# from sums, PMCC test, two events, mu and sigma from two, stratified
# sample, outlier fences.

def s_binom(F):
    if F.kind != 'binom':
        return []
    r = [('r =', 1, False)]
    return [(1, ('P(X = r)', 'e_stat', 'bprob', 'eq', r)),
            (2, ('P(X <= r)', 'e_stat', 'bprob', 'le', r)),
            (3, ('P(X >= r)', 'e_stat', 'bprob', 'ge', r)),
            (4, ('P(a <= X <= b)', 'e_stat', 'bprob', 'range', [('a =', 1, False), ('b =', 1, False)])),
            (5, ('Mean, var, sd', 'e_stat', 'bmean', None, None)),
            (6, ('Test for p', 'e_stat', 'btest', None,
                 ('choose+', ['lower tail (H1: p < p0)', 'upper tail (H1: p > p0)', 'two-tail (H1: p != p0)'],
                  [('observed x =', 1, False), ('sig level % =', 1, False)]))),
            (7, ('Critical region', 'e_stat', 'bcrit', None,
                 ('choose+', ['lower tail', 'upper tail', 'two-tail'], [('sig level % =', 1, False)])))]

def s_normal(F):
    if F.kind != 'normal':
        return []
    if F.mu is None or F.sd is None:
        nm = 'mu' if F.mu is None else 'sigma'
        return [(1, ('Find ' + nm, 'e_stat', 'nfind', None,
                     ('choose+', ['from P(X < x) = p', 'from P(X > x) = p'],
                      [('x =', 1, False), ('p =', 1, False)])))]
    return [(1, ('P(X < x)', 'e_stat', 'nprob', 'lt', [('x =', 1, False)])),
            (2, ('P(X > x)', 'e_stat', 'nprob', 'gt', [('x =', 1, False)])),
            (3, ('P(a < X < b)', 'e_stat', 'nprob', 'between', [('a =', 1, False), ('b =', 1, False)])),
            (4, ('x from P(X < x)', 'e_stat', 'ninv', None, [('P(X < x) =', 1, False)])),
            (5, ('Test for mean', 'e_stat', 'ztest', None,
                 ('choose+', ['lower tail (H1: mu < mu0)', 'upper tail (H1: mu > mu0)', 'two-tail (H1: mu != mu0)'],
                  [('n =', 1, False), ('sample mean =', 1, False), ('sig level % =', 1, False)])))]

def s_data(F):
    if F.kind == 'data':
        return [(1, ('Summary stats', 'e_data', 'summary', None, None)),
                (2, ('Quartiles, IQR', 'e_data', 'quartiles', None, None)),
                (3, ('Outliers', 'e_data', 'outliers', None, None))]
    if F.kind == 'two':
        return [(1, ('Frequency table', 'e_data', 'freq', None, None)),
                (2, ('x and y: PMCC, line', 'e_data', 'bivariate', None, None))]
    return []

def s_blank(F):
    if F.kind != 'blank':
        return []
    return [(1, ('From sums', 'e_data', 'fromsums', None, ('boxes', ['n', 'sum x', 'sum x^2', 'Sxx'], 2))),
            (2, ('PMCC test', 'e_data', 'pmcc', None, ('boxes', ['r', 'n', 'sig %', 'tails'], 2))),
            (3, ('Two events', 'e_data', 'venn', None,
                 ('boxes', ['P(A)', 'P(B)', 'P(A and B)', 'P(A or B)', 'P(A|B)'], 2))),
            (4, ('mu, sigma from two', 'e_data', 'twopct', None,
                 ('boxes', ['x1', 'P(X<x1)', 'x2', 'P(X<x2)'], 2))),
            (5, ('Stratified sample', 'e_data', 'strat', None, ('boxes', ['sample', 'strata'], 1, 'raw'))),
            (6, ('Outlier fences', 'e_data', 'fences', None, ('boxes', ['Q1', 'median', 'Q3', 'k'], 2)))]

ACTS = (s_blank, s_binom, s_normal, s_data)
