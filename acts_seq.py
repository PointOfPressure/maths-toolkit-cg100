# Sequences and series actions (acts.py has the registry): a u(n) formula or
# the term of a sum, a recurrence, (a + bx)^n, two facts as equations
# (Solve, from Algebra), and with nothing typed the AP and GP boxes.
from acts import a_solve

def _seq(F):
    return getattr(F, 'seq', '')

def s_term(F):
    if _seq(F) != 'term' or F.kind in ('blank',):
        return []
    v = F.var
    out = [(1, ('Terms', 'e_seq', 'terms', None, [('from ' + v + ' =', 1, True), ('how many', 1, True)])),
           (2, ('Sum (sigma)', 'e_seq', 'sum_', None, [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, True)]))]
    if not F.letters:
        out.append((3, ('Which term is', 'e_seq', 'which', None, [('value', 1, False)])))
    return out

def s_rec(F):
    if _seq(F) != 'rec':
        return []
    u = F.u
    out = [(1, ('Terms', 'e_seq', 'rterms', None, [(u + '(1) =', 1, False), ('how many', 1, True)])),
           (2, ('Sum of terms', 'e_seq', 'rsum', None, [(u + '(1) =', 1, False), ('number of terms', 1, False)]))]
    import recog
    if not recog.has(F.g, 'n'):
        out.append((3, ('Limit', 'e_seq', 'limit', None, None)))
    return out

def s_binom(F):
    if _seq(F) != 'binom':
        return []
    v = F.var
    return [(1, ('Expand', 'e_seq', 'expand', None, [('how many terms', 1, True)])),
            (2, ('Coefficient of ' + v + '^k', 'e_seq', 'coefficient', None, [('k =', 1, False)]))]

def s_blank(F):
    if F.kind != 'blank':
        return []
    return [(1, ('AP facts', 'e_seqbox', 'facts', 'AP', ('boxes', ['a', 'd', 'n', 'u(n)', 'S(n)'], 2))),
            (2, ('GP facts', 'e_seqbox', 'facts', 'GP', ('boxes', ['a', 'r', 'n', 'u(n)', 'S(n)', 'S(inf)'], 2)))]

def s_solve(F):
    if F.kind == 'blank' or _seq(F) == 'rec':
        return []
    return a_solve(F)

ACTS = (s_blank, s_rec, s_binom, s_term, s_solve)
