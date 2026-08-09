import math
import casui
import caslex
import casutil
import cascalc

_asknum = casutil.asknum
_fn = casutil.fmt
_show = casutil.show
_cstr = casutil.fmtc
_binom = casutil.ncr
_w = casutil.w
_warn = casutil.warn

def _ask_coeffs(prompts):
    out = []
    for p in prompts:
        v = _asknum(p)
        if v is None:
            return None
        out.append(v)
    return out

def t_vieta_quad():
    c = _ask_coeffs(['a:', 'b:', 'c:'])
    if c is None:
        return
    a, b, cc = c[0], c[1], c[2]
    if a == 0:
        _show('VIETA QUAD', ['a must not be 0'])
        return
    _show('VIETA a x^2+b x+c', ['sum  = -b/a = ' + _fn(-b / a), 'prod =  c/a = ' + _fn(cc / a)])

def t_vieta_cubic():
    c = _ask_coeffs(['a:', 'b:', 'c:', 'd:'])
    if c is None:
        return
    a, b, cc, d = c[0], c[1], c[2], c[3]
    if a == 0:
        _show('VIETA CUBIC', ['a must not be 0'])
        return
    _show('VIETA cubic', ['sum       = -b/a = ' + _fn(-b / a), 'sum pairs =  c/a = ' + _fn(cc / a), 'prod      = -d/a = ' + _fn(-d / a)])

def t_vieta_quartic():
    c = _ask_coeffs(['a:', 'b:', 'c:', 'd:', 'e:'])
    if c is None:
        return
    a, b, cc, d, e = c[0], c[1], c[2], c[3], c[4]
    if a == 0:
        _show('VIETA QUARTIC', ['a must not be 0'])
        return
    _show('VIETA quartic', ['sum     = -b/a = ' + _fn(-b / a), 'pairs   =  c/a = ' + _fn(cc / a), 'triples = -d/a = ' + _fn(-d / a), 'prod    =  e/a = ' + _fn(e / a)])

def t_quad_roots():
    c = _ask_coeffs(['a:', 'b:', 'c:'])
    if c is None:
        return
    a, b, cc = c[0], c[1], c[2]
    if a == 0:
        _show('QUAD ROOTS', ['a must not be 0'])
        return
    disc = b * b - 4 * a * cc
    lines = [_w('disc = b^2-4ac = ' + _fn(disc))]
    if disc >= 0:
        sq = math.sqrt(disc)
        r1 = (-b + sq) / (2 * a)
        r2 = (-b - sq) / (2 * a)
        lines.append('two real roots:')
        lines.append('x1 = ' + _fn(r1))
        lines.append('x2 = ' + _fn(r2))
    else:
        re = -b / (2 * a)
        im = math.sqrt(-disc) / (2 * abs(a))
        lines.append('complex conjugates:')
        lines.append('x1 = ' + _cstr(re, im))
        lines.append('x2 = ' + _cstr(re, -im))
    _show('QUAD ROOTS', lines)

def t_numeric_roots():
    s = casui.input_expr('poly in x = 0:')
    if s is None:
        return
    t = caslex.parse(s)
    if t is None:
        _show('NUMERIC ROOTS', ['could not parse'])
        return
    try:
        roots = cascalc.solve(t)
    except:
        roots = None
    if roots is None or len(roots) == 0:
        _show('NUMERIC ROOTS', [_warn('no real roots in'), _warn('[-20, 20]')])
        return
    roots = sorted(roots)
    lines = [_warn('real roots in [-20,20]:')]
    for r in roots:
        lines.append('x = ' + _fn(r))
    _show('NUMERIC ROOTS', lines)

def t_shift_roots():
    deg = _asknum('degree (1-4):')
    if deg is None:
        return
    n = int(round(deg))
    if n < 1 or n > 4:
        _show('SHIFT ROOTS', ['degree must be 1..4'])
        return
    names = ['a', 'b', 'c', 'd', 'e']
    prompts = []
    i = 0
    while i <= n:
        prompts.append(names[i] + ' (x^' + str(n - i) + '):')
        i += 1
    coeffs = _ask_coeffs(prompts)
    if coeffs is None:
        return
    if coeffs[0] == 0:
        _show('SHIFT ROOTS', ['leading coeff not 0'])
        return
    k = _asknum('shift k (roots+k):')
    if k is None:
        return
    new = [0.0] * (n + 1)
    i = 0
    while i <= n:
        ai = coeffs[i]
        p = n - i
        j = 0
        while j <= p:
            term = ai * _binom(p, j) * ((-k) ** (p - j))
            new[n - j] += term
            j += 1
        i += 1
    lines = [_w('new coeffs high->low:')]
    i = 0
    while i <= n:
        lines.append(names[i] + ' (x^' + str(n - i) + ') = ' + _fn(new[i]))
        i += 1
    _show('SHIFT BY ' + _fn(k), lines)

TOOLS = [('Vieta quadratic', t_vieta_quad), ('Vieta cubic', t_vieta_cubic), ('Vieta quartic', t_vieta_quartic), ('Quadratic roots', t_quad_roots), ('Numeric roots (x)', t_numeric_roots), ('Shift roots by k', t_shift_roots)]

def run():
    casutil.run_tools('ROOTS OF POLYNOMIALS', TOOLS)