import math
import casui
import caslex
import caseng

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

def _fn(x):
    try:
        r = round(x, 4)
    except:
        return str(x)
    if r == int(r):
        return str(int(r))
    return str(r)

def _show(title, lines):
    casui.result_screen(title, lines)

def _sinh(x):
    return (math.exp(x) - math.exp(-x)) / 2

def _cosh(x):
    return (math.exp(x) + math.exp(-x)) / 2

def _tanh(x):
    if x > 20:
        return 1.0
    if x < -20:
        return -1.0
    e = math.exp(x)
    f = math.exp(-x)
    return (e - f) / (e + f)

def t_sinh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        r = _fn(_sinh(x))
    except:
        _show('SINH', ['x = ' + _fn(x), 'Error: value too large'])
        return
    _show('SINH', ['x = ' + _fn(x), 'sinh x = ' + r])

def t_cosh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        r = _fn(_cosh(x))
    except:
        _show('COSH', ['x = ' + _fn(x), 'Error: value too large'])
        return
    _show('COSH', ['x = ' + _fn(x), 'cosh x = ' + r])

def t_tanh():
    x = _asknum('x:')
    if x is None:
        return
    _show('TANH', ['x = ' + _fn(x), 'tanh x = ' + _fn(_tanh(x))])

def t_all():
    x = _asknum('x:')
    if x is None:
        return
    try:
        rs = _fn(_sinh(x))
        rc = _fn(_cosh(x))
    except:
        _show('SINH COSH TANH', ['x = ' + _fn(x), 'Error: value too large'])
        return
    _show('SINH COSH TANH', ['x = ' + _fn(x), 'sinh x = ' + rs, 'cosh x = ' + rc, 'tanh x = ' + _fn(_tanh(x))])

def t_arsinh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        v = math.log(x + math.sqrt(x * x + 1))
    except:
        _show('ARSINH', ['arsinh x = ln(x+sqrt(x^2+1))', 'x = ' + _fn(x), 'Error: value too large'])
        return
    _show('ARSINH', ['arsinh x = ln(x+sqrt(x^2+1))', 'x = ' + _fn(x), 'arsinh x = ' + _fn(v)])

def t_arcosh():
    x = _asknum('x (x>=1):')
    if x is None:
        return
    if x < 1:
        _show('ARCOSH', ['Error: domain is x >= 1', 'x = ' + _fn(x)])
        return
    try:
        v = math.log(x + math.sqrt(x * x - 1))
    except:
        _show('ARCOSH', ['arcosh x = ln(x+sqrt(x^2-1))', 'x = ' + _fn(x), 'Error: value too large'])
        return
    _show('ARCOSH', ['arcosh x = ln(x+sqrt(x^2-1))', 'x = ' + _fn(x), 'arcosh x = ' + _fn(v)])

def t_artanh():
    x = _asknum('x (|x|<1):')
    if x is None:
        return
    if x <= -1 or x >= 1:
        _show('ARTANH', ['Error: domain is |x| < 1', 'x = ' + _fn(x)])
        return
    v = 0.5 * math.log((1 + x) / (1 - x))
    _show('ARTANH', ['artanh x = 0.5 ln((1+x)/(1-x))', 'x = ' + _fn(x), 'artanh x = ' + _fn(v)])

def t_ref():
    _show('REFERENCE CARD', ['cosh^2 x - sinh^2 x = 1', 'd/dx sinh x = cosh x', 'd/dx cosh x = sinh x', 'd/dx tanh x = 1 - tanh^2 x', 'Int 1/sqrt(x^2+a^2) dx', '  = arsinh(x/a) + C', 'Int 1/sqrt(x^2-a^2) dx', '  = arcosh(x/a) + C'])

TOOLS = [('Evaluate sinh', t_sinh), ('Evaluate cosh', t_cosh), ('Evaluate tanh', t_tanh), ('All three at x', t_all), ('arsinh (inverse)', t_arsinh), ('arcosh (inverse)', t_arcosh), ('artanh (inverse)', t_artanh), ('Reference card', t_ref)]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('HYPERBOLIC FUNCTIONS', labels)
        if c == -1:
            return
        TOOLS[c][1]()
