# Numerical methods actions (acts.py has the registry): sign changes,
# Newton-Raphson, bisection, the trapezium rule on f(x) or on y values, and
# iteration of x = g(x).

def _n(F):
    return getattr(F, 'num', '')

def n_root(F):
    if _n(F) not in ('root', 'fn', 'iter'):
        return []
    v = F.var
    p = 0 if _n(F) == 'root' else 4
    return [(p + 1, ('Sign change', 'e_num', 'signs', None,
                     [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, False), ('steps', 1, True)])),
            (p + 2, ('Newton-Raphson', 'e_num', 'newton', None, [(v + '(1) =', 1, False), ('steps', 1, True)])),
            (p + 6, ('Bisection', 'e_num', 'bisect', None,
                     [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, False), ('steps', 1, True)]))]

def n_trap(F):
    if _n(F) == 'fn':
        v = F.var
        return [(1, ('Trapezium rule', 'e_num', 'trap', None,
                     [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, False), ('strips', 1, False)]))]
    if F.kind == 'data':
        return [(1, ('Trapezium rule', 'e_num', 'trapdata', None, [('strip width h =', 1, False)]))]
    return []

def n_iter(F):
    if _n(F) == 'iter':
        v = F.var
        return [(1, ('Iterate', 'e_num', 'iterate', None, [(v + '(1) =', 1, False), ('steps', 1, True)]))]
    return []

ACTS = (n_iter, n_trap, n_root)
