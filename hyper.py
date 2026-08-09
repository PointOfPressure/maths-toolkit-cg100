# device has sinh/cosh/tanh but no asinh/acosh/atanh - inverses are built here
import math
import casutil

_asknum = casutil.asknum
_fn = casutil.fmt
_show = casutil.show
_w = casutil.w
_warn = casutil.warn

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

def _arsinh(x):
    a = x if x >= 0 else -x
    v = math.log(a + math.sqrt(a * a + 1.0))
    return v if x >= 0 else -v

def t_sinh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        r = _fn(_sinh(x))
    except:
        _show('SINH', [_w('x = ' + _fn(x)), 'Error: value too large'])
        return
    _show('SINH', [_w('x = ' + _fn(x)), 'sinh x = ' + r])

def t_cosh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        r = _fn(_cosh(x))
    except:
        _show('COSH', [_w('x = ' + _fn(x)), 'Error: value too large'])
        return
    _show('COSH', [_w('x = ' + _fn(x)), 'cosh x = ' + r])

def t_tanh():
    x = _asknum('x:')
    if x is None:
        return
    _show('TANH', [_w('x = ' + _fn(x)), 'tanh x = ' + _fn(_tanh(x))])

def t_all():
    x = _asknum('x:')
    if x is None:
        return
    try:
        rs = _fn(_sinh(x))
        rc = _fn(_cosh(x))
    except:
        _show('SINH COSH TANH', [_w('x = ' + _fn(x)), 'Error: value too large'])
        return
    _show('SINH COSH TANH', [_w('x = ' + _fn(x)), 'sinh x = ' + rs, 'cosh x = ' + rc, 'tanh x = ' + _fn(_tanh(x))])

def t_arsinh():
    x = _asknum('x:')
    if x is None:
        return
    try:
        v = _arsinh(x)
    except:
        _show('ARSINH', [_w('arsinh x = ln(x+sqrt(x^2+1))'), _w('x = ' + _fn(x)), 'Error: value too large'])
        return
    _show('ARSINH', [_w('arsinh x = ln(x+sqrt(x^2+1))'), _w('x = ' + _fn(x)), 'arsinh x = ' + _fn(v)])

def t_arcosh():
    x = _asknum('x (x>=1):')
    if x is None:
        return
    if x < 1:
        _show('ARCOSH', [_warn('Error: domain is x >= 1'), _w('x = ' + _fn(x))])
        return
    try:
        v = math.log(x + math.sqrt(x * x - 1))
    except:
        _show('ARCOSH', [_w('arcosh x = ln(x+sqrt(x^2-1))'), _w('x = ' + _fn(x)), 'Error: value too large'])
        return
    _show('ARCOSH', [_w('arcosh x = ln(x+sqrt(x^2-1))'), _w('x = ' + _fn(x)), 'arcosh x = ' + _fn(v)])

def t_artanh():
    x = _asknum('x (|x|<1):')
    if x is None:
        return
    if x <= -1 or x >= 1:
        _show('ARTANH', [_warn('Error: domain is |x| < 1'), _w('x = ' + _fn(x))])
        return
    v = 0.5 * math.log((1 + x) / (1 - x))
    _show('ARTANH', [_w('artanh x = 0.5 ln((1+x)/(1-x))'), _w('x = ' + _fn(x)), 'artanh x = ' + _fn(v)])

def t_ref():
    _show('REFERENCE CARD', ['cosh^2 x - sinh^2 x = 1', 'd/dx sinh x = cosh x', 'd/dx cosh x = sinh x', 'd/dx tanh x = 1 - tanh^2 x', 'Int 1/sqrt(x^2+a^2) dx', '  = arsinh(x/a) + C', 'Int 1/sqrt(x^2-a^2) dx', '  = arcosh(x/a) + C'])

TOOLS = [('Evaluate sinh', t_sinh), ('Evaluate cosh', t_cosh), ('Evaluate tanh', t_tanh), ('All three at x', t_all), ('arsinh (inverse)', t_arsinh), ('arcosh (inverse)', t_arcosh), ('artanh (inverse)', t_artanh), ('Reference card', t_ref)]

def run():
    casutil.run_tools('HYPERBOLIC FUNCTIONS', TOOLS)
