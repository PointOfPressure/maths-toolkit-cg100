# Calculus's actions (acts.py has the registry and the others).
from acts import _fn, a_graph

# ---- Calculus ----------------------------------------------------------------------------------

def _cfn(F):
    # a function of the variable to differentiate or integrate
    return _fn(F) and F.kind not in ('num', 'const') and not F.letters

def c_diff(F):
    if _cfn(F) or (_fn(F) and F.letters and F.kind != 'num'):
        out = [(1, ('Differentiate', 'e_calc', 'differentiate', None, None)),
               (5, ('Second derivative', 'e_calc', 'second', None, None))]
        v = F.var
        out.append((2, ('Stationary points', 'e_calc', 'stationary', None, None)))
        out.append((10, ('First principles', 'e_calc', 'firstp', None, None)))
        if not F.letters:
            out += [(11, ('Inflection points', 'e_calc', 'inflection', None, None)),
                    (3, ('Tangent at ' + v + ' =', 'e_calc', 'tangent', None, [(v + ' =', 1, False)])),
                    (6, ('Normal at ' + v + ' =', 'e_calc', 'normal', None, [(v + ' =', 1, False)])),
                    (8, ('Increasing where?', 'e_calc', 'increasing', None, None))]
        return out
    return []

def c_integ(F):
    if _fn(F) and F.kind not in ('num',):
        v = F.var
        out = [(4, ('Integrate', 'e_calc', 'integrate', None, None))]
        if not F.letters:
            out += [(7, ('Definite integral', 'e_calc', 'definite', None,
                         [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, False)])),
                    (9, ('Area under curve', 'e_calc', 'area', None,
                         [('from ' + v + ' =', 1, False), ('to ' + v + ' =', 1, False)]))]
        return out
    return []

def c_implicit(F):
    if F.kind == 'xy' and not F.pair:
        return [(1, ('dy/dx (implicit)', 'e_calc', 'implicit', None, None)),
                (4, ('Where dy/dx = 0', 'e_calc', 'flat', None, None)),
                (2, ('Gradient at a point', 'e_calc', 'implicit', 'point', [('(x, y) =', 2, False)])),
                (3, ('Tangent at a point', 'e_calc', 'implicit', 'tangent', [('(x, y) =', 2, False)]))]
    return []

def c_param(F):
    if F.pair == 'param' or (F.pair == 'fg' and F.var not in ('x', 'y')):
        t = F.var
        return [(1, ('dy/dx (parametric)', 'e_calc', 'parametric', None, None)),
                (2, ('Gradient at ' + t + ' =', 'e_calc', 'parametric', 'point', [(t + ' =', 1, False)])),
                (3, ('Tangent at ' + t + ' =', 'e_calc', 'parametric', 'tangent', [(t + ' =', 1, False)]))]
    return []

def c_de(F):
    if F.kind == 'de':
        y, x = F.rows[0].de
        return [(1, ('Solve (separate)', 'e_calc', 'de', None, None)),
                (2, ('Solve with a point', 'e_calc', 'de', None,
                     [('(' + x + ', ' + y + ') =', 2, False)]))]
    return []

def c_between(F):
    if F.pair == 'fg' and F.var == 'x':
        return [(1, ('Area between', 'e_calc', 'between', None, None)),
                (2, ('Area between, limits', 'e_calc', 'between', None,
                     [('from x =', 1, False), ('to x =', 1, False)])),
                (3, ('Where they meet', 'e_fn', 'meet', None, None))]
    return []

CALC = (c_diff, c_integ, c_implicit, c_param, c_de, c_between, a_graph)
ACTS = CALC
