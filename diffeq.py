import math
import casui
import caslex
import caseng
import casutil
import cascalc

_asknum = casutil.asknum
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show

def t_first_order():
    s = casui.input_expr('P(x):')
    if s is None:
        return                      # cancelled - say nothing
    P = caslex.parse(s)
    if P is None:
        _show('FIRST ORDER LINEAR', ['Could not read P(x).'])
        return
    ip = cascalc.integ(P)
    lines = ['dy/dx + P(x)y = Q(x)', 'P(x) = ' + caseng.tostr(P)]
    if ip is None:
        lines.append('integral P dx: not found')
        lines.append('IF = e^(integral P dx)')
    else:
        ips = caseng.tostr(ip)
        lines.append('integral P dx = ' + ips)
        lines.append('IF = e^(' + ips + ')')
    lines.append('Multiply through by IF:')
    lines.append('d/dx(IF*y) = IF*Q(x)')
    lines.append('y = (1/IF) integral IF*Q dx')
    _show('FIRST ORDER LINEAR', lines)

def t_second_order():
    a = _asknum("a in y'' + a y' + b y = 0:")
    if a is None:
        return
    b = _asknum('b:')
    if b is None:
        return
    disc = a * a - 4.0 * b
    lines = ["y'' + a y' + b y = 0", 'aux: m^2 + a m + b = 0', 'm^2 + (' + _fn(a) + ')m + (' + _fn(b) + ') = 0', 'disc = a^2 - 4b = ' + _fn(disc)]
    if disc > 1e-9:
        rt = math.sqrt(disc)
        m1 = (-a + rt) / 2.0
        m2 = (-a - rt) / 2.0
        lines.append('Real roots:')
        lines.append('m1 = ' + _fn(m1) + ', m2 = ' + _fn(m2))
        lines.append('y = A e^(' + _fn(m1) + 'x)')
        lines.append('  + B e^(' + _fn(m2) + 'x)')
    elif disc < -1e-9:
        p = -a / 2.0
        q = math.sqrt(-disc) / 2.0
        lines.append('Complex roots p +/- q i:')
        lines.append('p = ' + _fn(p) + ', q = ' + _fn(q))
        lines.append('y = e^(' + _fn(p) + 'x) *')
        lines.append('  (A cos(' + _fn(q) + 'x)')
        lines.append('   + B sin(' + _fn(q) + 'x))')
    else:
        m = -a / 2.0
        lines.append('Repeated root m = ' + _fn(m))
        lines.append('y = (A + B x) e^(' + _fn(m) + 'x)')
    _show('SECOND ORDER CF', lines)

def t_shm():
    w = _asknum('angular freq w (>0):')
    if w is None:
        return
    if w <= 0:
        _show('SHM', ['w must be > 0.'])
        return
    T = 2.0 * math.pi / w
    f = w / (2.0 * math.pi)
    lines = ["x'' = -w^2 x", 'Simple harmonic motion', 'w = ' + _fn(w), 'Period T = 2 pi / w', 'T = ' + _fn(T), 'Frequency f = 1/T = ' + _fn(f), 'x = A cos(w t - phi)', '  = C cos(w t) + D sin(w t)']
    _show('SHM', lines)

def t_damping():
    a = _asknum("damping a in x'' + a x' + b x = 0:")
    if a is None:
        return
    b = _asknum('stiffness b:')
    if b is None:
        return
    disc = a * a - 4.0 * b
    lines = ["x'' + a x' + b x = 0", 'disc = a^2 - 4b = ' + _fn(disc)]
    if disc > 1e-9:
        lines.append('OVER-DAMPED (disc > 0)')
        lines.append('Two real roots; returns to')
        lines.append('rest with no oscillation.')
    elif disc < -1e-9:
        lines.append('UNDER-DAMPED (disc < 0)')
        lines.append('Complex roots; oscillates')
        lines.append('with decaying amplitude.')
    else:
        lines.append('CRITICAL (disc = 0)')
        lines.append('Repeated root; fastest')
        lines.append('return, no overshoot.')
    _show('DAMPING CLASSIFIER', lines)

TOOLS = [('First-order linear (IF)', t_first_order), ('Second-order const-coeff', t_second_order), ('SHM recogniser', t_shm), ('Damping classifier', t_damping)]

def run():
    casutil.run_tools('DIFFERENTIAL EQUATIONS', TOOLS)