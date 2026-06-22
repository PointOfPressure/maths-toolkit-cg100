import math
import casui
import caslex
import caseng


def _fact(k):
    r = 1
    i = 2
    while i <= k:
        r = r * i
        i = i + 1
    return r


def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None


def _askint(prompt):
    v = _asknum(prompt)
    if v is None:
        return None
    if v != v or v == float('inf') or v == float('-inf'):
        return None
    return int(round(v))


def _fn(x):
    if x != x:
        return 'nan'
    if x == float('inf'):
        return 'inf'
    if x == float('-inf'):
        return '-inf'
    r = round(x, 4)
    if r == int(r):
        return str(int(r))
    return str(r)


def _show(title, lines):
    casui.result_screen(title, lines)


def t_sum_r():
    n = _askint('n (Sum r, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r', ['n must be >= 0'])
        return
    s = n * (n + 1) / 2.0
    _show('SUM r, r=1..n', ['Sum r = n(n+1)/2', 'n = ' + _fn(n), '= ' + _fn(s)])


def t_sum_r2():
    n = _askint('n (Sum r^2, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r^2', ['n must be >= 0'])
        return
    s = n * (n + 1) * (2 * n + 1) / 6.0
    _show('SUM r^2, r=1..n', ['Sum r^2 =', ' n(n+1)(2n+1)/6', 'n = ' + _fn(n), '= ' + _fn(s)])


def t_sum_r3():
    n = _askint('n (Sum r^3, r=1..n):')
    if n is None:
        return
    if n < 0:
        _show('SUM r^3', ['n must be >= 0'])
        return
    h = n * (n + 1) / 2.0
    s = h * h
    _show('SUM r^3, r=1..n', ['Sum r^3 =', ' (n(n+1)/2)^2', 'n = ' + _fn(n), '= ' + _fn(s)])


def _build_terms(f):
    # Iteratively build Maclaurin coefficients c_k for k = 0..5.
    # k-th coefficient = (k-th derivative at 0) / k!. Derivatives are taken
    # by repeatedly applying caseng.diff then caseng.simplify - NO recursion.
    terms = []
    d = f
    k = 0
    while k < 6:
        try:
            v = caseng.evalf(d, 0.0)
        except:
            break
        terms.append(v / _fact(k))
        try:
            d = caseng.simplify(caseng.diff(d, 'x'))
        except:
            break
        k = k + 1
    return terms


def _poly_lines(terms):
    lines = []
    first = True
    k = 0
    while k < len(terms):
        c = terms[k]
        if abs(c) < 1e-7:
            k = k + 1
            continue
        sign = '+'
        m = c
        if c < 0:
            sign = '-'
            m = -c
        ct = _fn(m)
        if k == 0:
            term = ct
        elif k == 1:
            term = 'x' if ct == '1' else ct + 'x'
        else:
            term = ('x^' + str(k)) if ct == '1' else (ct + 'x^' + str(k))
        if first:
            lines.append('P(x) = ' + ('-' if sign == '-' else '') + term)
            first = False
        else:
            lines.append('       ' + sign + ' ' + term)
        k = k + 1
    if first:
        lines.append('P(x) = 0')
    return lines


def _getN():
    n = _askint('terms N (1..6):')
    if n is None:
        return None
    if n < 1:
        n = 1
    if n > 6:
        n = 6
    return n


def t_maclaurin():
    s = casui.input_expr('f(x):')
    if s is None:
        return
    f = caslex.parse(s)
    if f is None:
        _show('MACLAURIN', ['Could not parse f(x)'])
        return
    n = _getN()
    if n is None:
        return
    terms = _build_terms(f)[:n]
    try:
        head = 'f(x) = ' + caseng.tostr(f)
    except:
        head = 'f(x)'
    lines = [head]
    for ln in _poly_lines(terms):
        lines.append(ln)
    _show('MACLAURIN (N=' + str(n) + ')', lines)


def t_approx():
    s = casui.input_expr('f(x):')
    if s is None:
        return
    f = caslex.parse(s)
    if f is None:
        _show('APPROX', ['Could not parse f(x)'])
        return
    n = _getN()
    if n is None:
        return
    xv = _asknum('x value:')
    if xv is None:
        return
    terms = _build_terms(f)[:n]
    approx = 0.0
    p = 1.0
    k = 0
    while k < len(terms):
        approx = approx + terms[k] * p
        p = p * xv
        k = k + 1
    try:
        exact = caseng.evalf(f, xv)
        err = exact - approx
        lines = ['x = ' + _fn(xv), 'series ~ ' + _fn(approx), 'f(x) = ' + _fn(exact), 'error = ' + _fn(err)]
    except:
        lines = ['x = ' + _fn(xv), 'series ~ ' + _fn(approx), 'f(x) undefined here']
    _show('APPROX (N=' + str(n) + ')', lines)


def t_reference():
    _show('MACLAURIN SERIES', [
        'e^x = 1+x+x^2/2!+...',
        '   (all x)',
        'ln(1+x)=x-x^2/2+x^3/3',
        '   (-1<x<=1)',
        'sin x = x-x^3/3!+x^5/5!',
        'cos x = 1-x^2/2!+x^4/4!',
        '(1+x)^n = 1+nx+',
        ' n(n-1)x^2/2!+... |x|<1'])


TOOLS = [
    ('Sum of r', t_sum_r),
    ('Sum of r^2', t_sum_r2),
    ('Sum of r^3', t_sum_r3),
    ('Maclaurin of f(x)', t_maclaurin),
    ('Approx + error', t_approx),
    ('Reference card', t_reference),
]


def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Series & Maclaurin', labels)
        if c == -1:
            return
        TOOLS[c][1]()
