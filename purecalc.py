# purecalc.py - OCR B MEI H640 Pure: functions and the calculus techniques that
# are about rewriting rather than about a single derivative or integral.
# pure640.py keeps the algebra and trig; the plain d/dx and integral live in the
# CAS section. What is here is composite and inverse functions, domain and
# range, the modulus function, graph transformations, parametric and implicit
# differentiation, integration by substitution, small-angle approximations and
# the exact trig values.
# Stock CASIO MicroPython 1.9.4: ASCII only, no f-strings, iterative only.
import math
import casui
import caslex
import caseng
import cascalc
import caspoly
import casutil

_asknum = casutil.asknum
_askexpr = casutil.askexpr
_fn = casutil.fmt
_show = casutil.show

def _ts(tree):
    return caseng.tostr(cascalc.tidy(tree))

def _tidy(tree):
    return cascalc.tidy(tree)

def _parse(prompt):
    # ask for an expression and report a parse failure rather than returning
    # silently, which reads as "the tool did nothing"
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        _show('Could not read that', ['"' + s + '" is not an expression',
                                      'this toolkit can read.'])
        return None
    return t

def _safe(tree, xv, env=None):
    try:
        v = caseng.evalf(tree, xv, False, env)
    except:
        return None
    if isinstance(v, complex) or v != v:
        return None
    if v > 1.7e308 or v < -1.7e308:
        return None
    return v

# 1. COMPOSITE FUNCTIONS ----------------------------------------------------
def t_composite():
    _show('Composite functions', ['Enter f(x) and g(x).',
                                  'You get fg(x) = f(g(x))', 'and gf(x) = g(f(x)).'])
    f = _parse('f(x) =')
    if f is None:
        return
    g = _parse('g(x) =')
    if g is None:
        return
    fg = _tidy(caseng.subst(f, 'x', g))
    gf = _tidy(caseng.subst(g, 'x', f))
    lines = ['f(x) = ' + _ts(f), 'g(x) = ' + _ts(g), '',
             'fg(x) = f(g(x))', '  = ' + caseng.tostr(fg), '',
             'gf(x) = g(f(x))', '  = ' + caseng.tostr(gf)]
    if caseng.tostr(fg) != caseng.tostr(gf):
        lines.append('')
        lines.append('fg and gf are different,')
        lines.append('as they usually are.')
    v = _asknum('check at x = (or cancel)')
    if v is not None:
        a = _safe(fg, v)
        b = _safe(gf, v)
        lines.append('')
        lines.append('at x = ' + _fn(v) + ':')
        lines.append('  fg = ' + ('undefined' if a is None else _fn(a)))
        lines.append('  gf = ' + ('undefined' if b is None else _fn(b)))
    _show('Composite', lines)

# 2. INVERSE FUNCTION -------------------------------------------------------
def t_inverse():
    _show('Inverse function', ['Enter f(x). If x appears once,',
                               'the inverse is found exactly by',
                               'undoing each step in turn.',
                               'Otherwise it is solved numerically.'])
    f = _parse('f(x) =')
    if f is None:
        return
    lines = ['f(x) = ' + _ts(f)]
    inv = caseng.invert(f, 'x', 'x')
    if inv is not None:
        inv = caseng.simplify(inv)
        lines.append('')
        lines.append('f-inverse(x) =')
        lines.append('  ' + caseng.tostr(inv))
        # a check the student can repeat: f(f-inverse(a)) should be a
        ok = True
        for a in (0.7, 1.9, 3.3):
            r = _safe(inv, a)
            if r is None:
                continue
            back = _safe(f, r)
            if back is None or abs(back - a) > 1e-6:
                ok = False
        lines.append('')
        lines.append('check f(f-inv(x)) = x: ' + ('yes' if ok else 'not everywhere'))
        if not ok:
            lines.append('(the inverse only holds on the')
            lines.append(' part of the domain where f is')
            lines.append(' one-to-one - state that domain)')
    else:
        lines.append('')
        lines.append('No exact inverse by undoing steps')
        lines.append('(x appears more than once, or f is')
        lines.append('not one-to-one). Solving instead.')
    v = _asknum('f-inverse of y = (or cancel)')
    if v is not None:
        if inv is not None:
            r = _safe(inv, v)
            if r is not None:
                lines.append('')
                lines.append('f-inverse(' + _fn(v) + ') = ' + _fn(r))
        else:
            roots = cascalc.solve(caseng.simplify(('-', f, ('n', v))), 'x')
            lines.append('')
            if roots:
                lines.append('f(x) = ' + _fn(v) + ' at:')
                for r in roots:
                    lines.append('  x = ' + _fn(r))
                if len(roots) > 1:
                    lines.append('more than one x gives this y,')
                    lines.append('so f has no inverse here.')
            else:
                lines.append('no x found with f(x) = ' + _fn(v))
    _show('Inverse', lines)

# 3. DOMAIN AND RANGE -------------------------------------------------------
def t_domain_range():
    _show('Domain and range', ['Enter f(x) and an interval.',
                               'The tool samples the interval,',
                               'reports where f is undefined,',
                               'and gives the range it reaches.'])
    f = _parse('f(x) =')
    if f is None:
        return
    a = _asknum('from x =')
    if a is None:
        return
    b = _asknum('to x =')
    if b is None:
        return
    if b < a:
        a, b = b, a
    n = 400
    lo = None
    hi = None
    gaps = []
    inside = False
    vals = []
    i = 0
    while i <= n:
        xv = a + (b - a) * i / float(n)
        v = _safe(f, xv)
        vals.append(v)
        if v is None:
            if inside:
                gaps.append(xv)
                inside = False
        else:
            inside = True
            if lo is None or v < lo:
                lo = v
            if hi is None or v > hi:
                hi = v
        i += 1
    lines = ['f(x) = ' + _ts(f), 'on ' + _fn(a) + ' <= x <= ' + _fn(b), '']
    if lo is None:
        lines.append('f is undefined everywhere on')
        lines.append('this interval.')
        _show('Domain and range', lines)
        return
    bad = 0
    for v in vals:
        if v is None:
            bad += 1
    if bad == 0:
        lines.append('domain: the whole interval')
    else:
        lines.append('undefined at ' + str(bad) + ' of ' + str(n + 1) + ' sample')
        lines.append('points - exclude those x values.')
        j = 0
        shown = 0
        while j <= n and shown < 4:
            if vals[j] is None:
                lines.append('  near x = ' + _fn(a + (b - a) * j / float(n)))
                shown += 1
                while j <= n and vals[j] is None:
                    j += 1
            j += 1
    lines.append('')
    lines.append('range reached: ' + _fn(lo) + ' to ' + _fn(hi))
    lines.append('(sampled, so a sharp spike between')
    lines.append(' samples could be missed)')
    _show('Domain and range', lines)

# 4. MODULUS FUNCTION -------------------------------------------------------
def t_modulus():
    _show('Modulus |f(x)|', ['Enter f(x), then a value k.',
                             'Solves |f(x)| = k by solving',
                             'f(x) = k and f(x) = -k,',
                             'and draws y = |f(x)|.'])
    f = _parse('f(x) =')
    if f is None:
        return
    k = _asknum('solve |f(x)| = k, k =')
    if k is None:
        return
    lines = ['|' + _ts(f) + '| = ' + _fn(k)]
    if k < 0:
        lines.append('')
        lines.append('A modulus is never negative,')
        lines.append('so there are no solutions.')
        _show('Modulus', lines)
        return
    roots = []
    for target in (k, -k):
        for r in cascalc.solve(caseng.simplify(('-', f, ('n', target))), 'x'):
            dup = False
            for e in roots:
                if abs(e - r) < 1e-6:
                    dup = True
            if not dup:
                roots.append(r)
    roots.sort()
    lines.append('')
    if roots:
        lines.append('from f(x) = ' + _fn(k) + ' and f(x) = ' + _fn(-k) + ':')
        for r in roots:
            lines.append('  x = ' + _fn(r))
    else:
        lines.append('no solutions found in the search')
        lines.append('range -20 <= x <= 20.')
    _show('Modulus', lines)
    casui.graph(caseng.simplify(('abs', f)))

# 5. GRAPH TRANSFORMATIONS --------------------------------------------------
def t_transform():
    _show('Graph transformations', ['From y = f(x) to y = a f(bx + c) + d.',
                                    'a stretches vertically (scale a),',
                                    'b stretches horizontally (scale 1/b),',
                                    'c translates left by c/b,',
                                    'd translates up by d.'])
    f = _parse('f(x) =')
    if f is None:
        return
    a = _asknum('a (vertical stretch) [1]')
    if a is None:
        a = 1.0
    b = _asknum('b (inside x coeff) [1]')
    if b is None:
        b = 1.0
    c = _asknum('c (inside constant) [0]')
    if c is None:
        c = 0.0
    d = _asknum('d (vertical shift) [0]')
    if d is None:
        d = 0.0
    if b == 0:
        _show('Transformations', ['b = 0 collapses the graph', 'to a horizontal line.'])
        return
    inner = ('+', ('*', ('n', b), ('v', 'x')), ('n', c))
    g = ('+', ('*', ('n', a), caseng.subst(f, 'x', inner)), ('n', d))
    g = caseng.simplify(g)
    lines = ['f(x) = ' + _ts(f), '', 'y = ' + _fn(a) + ' f(' + _fn(b) + 'x + ' + _fn(c) + ') + ' + _fn(d),
             '  = ' + caseng.tostr(g), '', 'in words, in this order:']
    if b != 1:
        lines.append('  stretch x by scale factor ' + _fn(1.0 / b))
    if c != 0:
        lines.append('  translate x by ' + _fn(-c / b))
    if a != 1:
        lines.append('  stretch y by scale factor ' + _fn(a))
    if d != 0:
        lines.append('  translate y by ' + _fn(d))
    if a == 1 and b == 1 and c == 0 and d == 0:
        lines.append('  nothing - the graph is unchanged')
    _show('Transformations', lines)
    casui.graph(g)

# 6. PARAMETRIC: DIFFERENTIATE ----------------------------------------------
def t_param_diff():
    _show('Parametric differentiation', ['Enter x(t) and y(t), typing t as t.',
                                         'dy/dx = (dy/dt) / (dx/dt), and',
                                         'd2y/dx2 = d/dt(dy/dx) / (dx/dt).'])
    x = _parse('x(t) =')
    if x is None:
        return
    y = _parse('y(t) =')
    if y is None:
        return
    try:
        dx = caseng.simplify(caseng.diff(x, 't'))
        dy = caseng.simplify(caseng.diff(y, 't'))
    except:
        _show('Parametric', ['Cannot differentiate one of these.'])
        return
    if dx == ('n', 0):
        _show('Parametric', ['dx/dt = 0, so dy/dx is not',
                             'defined - the curve has a',
                             'vertical tangent everywhere.'])
        return
    grad = _tidy(('/', dy, dx))
    lines = ['x(t) = ' + caseng.tostr(x), 'y(t) = ' + caseng.tostr(y), '',
             'dx/dt = ' + caseng.tostr(dx), 'dy/dt = ' + caseng.tostr(dy), '',
             'dy/dx = ' + caseng.tostr(grad)]
    try:
        second = _tidy(('/', caseng.simplify(caseng.diff(grad, 't')), dx))
        lines.append('')
        lines.append('d2y/dx2 = ' + caseng.tostr(second))
        lines.append('(note: divide by dx/dt, NOT by')
        lines.append(' (dx/dt) squared and not again')
        lines.append(' with respect to x)')
    except:
        second = None
    tv = _asknum('at t = (or cancel)')
    if tv is not None:
        env = {'t': tv}
        gv = _safe(grad, 0.0, env)
        xv = _safe(x, 0.0, env)
        yv = _safe(y, 0.0, env)
        lines.append('')
        lines.append('at t = ' + _fn(tv) + ':')
        if xv is not None and yv is not None:
            lines.append('  point (' + _fn(xv) + ', ' + _fn(yv) + ')')
        if gv is None:
            lines.append('  dy/dx undefined')
        else:
            lines.append('  dy/dx = ' + _fn(gv))
            if xv is not None and yv is not None:
                lines.append('  tangent: y - ' + _fn(yv) + ' =')
                lines.append('     ' + _fn(gv) + '(x - ' + _fn(xv) + ')')
                if gv != 0:
                    lines.append('  normal gradient ' + _fn(-1.0 / gv))
        if second is not None:
            sv = _safe(second, 0.0, env)
            if sv is not None:
                lines.append('  d2y/dx2 = ' + _fn(sv))
    _show('Parametric d/dx', lines)

# 7. PARAMETRIC: CONVERT AND SKETCH -----------------------------------------
def t_param_cartesian():
    _show('Parametric to Cartesian', ['Enter x(t) and y(t).',
                                      'If x(t) can be undone for t,',
                                      't is substituted into y(t).',
                                      'Then the curve is drawn.'])
    x = _parse('x(t) =')
    if x is None:
        return
    y = _parse('y(t) =')
    if y is None:
        return
    lines = ['x(t) = ' + caseng.tostr(x), 'y(t) = ' + caseng.tostr(y), '']
    tofx = caseng.invert(x, 't', 'x')
    if tofx is not None:
        cart = caseng.simplify(caseng.subst(y, 't', tofx))
        lines.append('t = ' + caseng.tostr(caseng.simplify(tofx)))
        lines.append('')
        lines.append('y = ' + caseng.tostr(cart))
    else:
        # the identity route: for x = a cos t, y = b sin t there is no single
        # inverse, but cos^2 + sin^2 = 1 gives the Cartesian form
        lines.append('x(t) cannot be undone for t on its')
        lines.append('own. If x and y are a cos t and')
        lines.append('b sin t, use cos^2 t + sin^2 t = 1:')
        lines.append('  (x/a)^2 + (y/b)^2 = 1')
        lines.append('For sec/tan use sec^2 - tan^2 = 1.')
    lo = _asknum('sketch: t from [0]')
    if lo is None:
        lo = 0.0
    hi = _asknum('t to [2pi]')
    if hi is None:
        hi = 2.0 * math.pi
    xs = []
    ys = []
    n = 240
    i = 0
    while i <= n:
        tv = lo + (hi - lo) * i / float(n)
        env = {'t': tv}
        xv = _safe(x, 0.0, env)
        yv = _safe(y, 0.0, env)
        xs.append(xv)
        ys.append(yv)
        i += 1
    _show('Parametric', lines)
    good = []
    for v in xs:
        if v is not None:
            good.append(v)
    goody = []
    for v in ys:
        if v is not None:
            goody.append(v)
    if not good or not goody:
        _show('Sketch', ['No plottable points in that', 'range of t.'])
        return
    xr = casutil.nice_range(good)
    yr = casutil.nice_range(goody)
    fr = casutil.frame(xr[0], xr[1], yr[0], yr[1])
    casutil.axes(fr, 'parametric curve', 'x', 'y')
    prev = None
    i = 0
    while i <= n:
        if xs[i] is None or ys[i] is None:
            prev = None
        else:
            if prev is not None:
                casutil.seg(fr, prev[0], prev[1], xs[i], ys[i], casui.ACC)
            prev = (xs[i], ys[i])
        i += 1
    casutil.chart_hold('t from ' + _fn(lo) + ' to ' + _fn(hi))

# 8. IMPLICIT DIFFERENTIATION -----------------------------------------------
def t_implicit():
    _show('Implicit differentiation', ['Enter the equation, using x and y,',
                                       'for example x^2+y^2=25 or',
                                       'x^3+y^3=6xy.',
                                       'dy/dx = -(dF/dx) / (dF/dy)',
                                       'where F is left side minus right.'])
    s = casui.input_expr('equation in x and y:')
    if s is None:
        return
    if '=' in s:
        parts = s.split('=', 1)
        lhs = caslex.parse(parts[0])
        rhs = caslex.parse(parts[1])
        if lhs is None or rhs is None:
            _show('Implicit', ['Could not read that equation.'])
            return
        F = ('-', lhs, rhs)
    else:
        F = caslex.parse(s)
        if F is None:
            _show('Implicit', ['Could not read that expression.'])
            return
    try:
        Fx = caseng.simplify(caseng.diff(F, 'x'))
        Fy = caseng.simplify(caseng.diff(F, 'y'))
    except:
        _show('Implicit', ['Cannot differentiate that.'])
        return
    if Fy == ('n', 0):
        _show('Implicit', ['dF/dy = 0: there is no y to',
                           'differentiate, so this is not',
                           'an implicit relation. Use the',
                           'CAS section instead.'])
        return
    grad = _tidy(('neg', ('/', Fx, Fy)))
    lines = ['F = ' + caseng.tostr(caseng.simplify(F)) + ' = 0', '',
             'dF/dx = ' + caseng.tostr(Fx), 'dF/dy = ' + caseng.tostr(Fy), '',
             'dy/dx = ' + caseng.tostr(grad)]
    xv = _asknum('at x = (or cancel)')
    if xv is not None:
        yv = _asknum('and y =')
        if yv is not None:
            env = {'x': xv, 'y': yv}
            chk = _safe(F, xv, env)
            gv = _safe(grad, xv, env)
            lines.append('')
            lines.append('at (' + _fn(xv) + ', ' + _fn(yv) + '):')
            if chk is not None and abs(chk) > 1e-6:
                lines.append('  WARNING: F = ' + _fn(chk) + ', not 0,')
                lines.append('  so this point is not on the curve.')
            if gv is None:
                lines.append('  dy/dx undefined (dF/dy = 0):')
                lines.append('  the tangent is vertical here.')
            else:
                lines.append('  dy/dx = ' + _fn(gv))
                lines.append('  tangent: y - ' + _fn(yv) + ' =')
                lines.append('     ' + _fn(gv) + '(x - ' + _fn(xv) + ')')
                if gv != 0:
                    lines.append('  normal gradient ' + _fn(-1.0 / gv))
    _show('Implicit d/dx', lines)

# 9. INTEGRATION BY SUBSTITUTION --------------------------------------------
def t_substitution():
    _show('Integration by substitution', ['Enter the integrand and your',
                                          'choice of u = g(x). Then',
                                          'du = g\'(x) dx, so the integral',
                                          'becomes f(x)/g\'(x) du - which',
                                          'is only progress if every x',
                                          'disappears into u.'])
    f = _parse('integrand f(x) =')
    if f is None:
        return
    g = _parse('u = g(x) =')
    if g is None:
        return
    try:
        dg = caseng.simplify(caseng.diff(g, 'x'))
    except:
        _show('Substitution', ['Cannot differentiate g(x).'])
        return
    if dg == ('n', 0):
        _show('Substitution', ['g\'(x) = 0, so u is constant',
                               'and the substitution cannot help.'])
        return
    lines = ['integrand: ' + _ts(f), 'u = ' + _ts(g), 'du/dx = ' + caseng.tostr(dg),
             'so dx = du / (' + caseng.tostr(dg) + ')', '']
    try:
        h = caspoly.cancel(caseng.simplify(('/', f, dg)))
    except:
        _show('Substitution', ['Could not divide by g\'(x).'])
        return
    gs = caseng.simplify(g)
    inu = caspoly.cancel(caseng.subst_tree(h, gs, ('v', 'u')))
    lines.append('f(x)/g\'(x) = ' + caseng.tostr(h))
    if caseng.count_var(inu, 'x'):
        lines.append('')
        lines.append('After substituting u there is still')
        lines.append('an x left, so this substitution')
        lines.append('does not clear the integral.')
        lines.append('Try a different u, or write g(x)')
        lines.append('in the integrand exactly as you')
        lines.append('typed it for u.')
        _show('Substitution', lines)
        return
    lines.append('in terms of u: ' + caseng.tostr(inu))
    F = cascalc.integ(inu, 'u')
    if F is None:
        lines.append('')
        lines.append('The u integral has no elementary')
        lines.append('form either.')
        _show('Substitution', lines)
        return
    F = cascalc.tidy(F)
    lines.append('')
    lines.append('integral in u = ' + caseng.tostr(F) + ' + C')
    back = cascalc.tidy(caseng.subst(F, 'u', g))
    lines.append('')
    lines.append('back-substituting u = ' + caseng.tostr(gs) + ':')
    lines.append('  ' + caseng.tostr(back) + ' + C')
    # differentiate the answer as a check the student can repeat
    try:
        chk = caseng.simplify(caseng.diff(back, 'x'))
        agree = True
        for xv in (0.43, 1.31, 2.17):
            a = _safe(chk, xv)
            b = _safe(f, xv)
            if a is None or b is None:
                continue
            if abs(a - b) > 1e-6 * (1.0 + abs(b)):
                agree = False
        lines.append('')
        lines.append('check by differentiating back: ' + ('agrees' if agree else 'DISAGREES'))
    except:
        pass
    _show('Substitution', lines)

# 10. SEPARATION OF VARIABLES -----------------------------------------------
def t_separable():
    _show('Separation of variables', ['For dy/dx = f(x) g(y):',
                                      '  integral 1/g(y) dy',
                                      '   = integral f(x) dx + C',
                                      'Enter f(x), then g(y) typed in y.',
                                      'For dy/dx = f(x) alone, put g(y) = 1.'])
    f = _parse('f(x) =')
    if f is None:
        return
    g = _parse('g(y) = (use y; 1 if none)')
    if g is None:
        return
    if caseng.count_var(g, 'x'):
        _show('Separable', ['g must be a function of y only.',
                            'If x and y will not separate,',
                            'this method does not apply -',
                            'try the integrating factor.'])
        return
    B = cascalc.integ(f, 'x')
    A = cascalc.integ(caseng.simplify(('/', ('n', 1), g)), 'y')
    lines = ['dy/dx = (' + _ts(f) + ')(' + _ts(g) + ')', '']
    if A is None or B is None:
        lines.append('One side has no elementary')
        lines.append('integral, so there is no formula')
        lines.append('to write down. Use Euler\'s method')
        lines.append('in Numerical Methods for values.')
        _show('Separable', lines)
        return
    A = cascalc.tidy(A)
    B = cascalc.tidy(B)
    lines.append('separate:  dy/g(y) = f(x) dx')
    lines.append('')
    lines.append('integral 1/g(y) dy = ' + caseng.tostr(A))
    lines.append('integral f(x) dx   = ' + caseng.tostr(B))
    lines.append('')
    lines.append('general solution (implicit):')
    lines.append('  ' + caseng.tostr(A) + ' = ' + caseng.tostr(B) + ' + C')
    x0 = _asknum('initial condition x = (or cancel)')
    if x0 is not None:
        y0 = _asknum('when y =')
        if y0 is not None:
            a0 = _safe(A, 0.0, {'y': y0})
            b0 = _safe(B, x0)
            if a0 is None or b0 is None:
                lines.append('')
                lines.append('That point is outside the domain')
                lines.append('of one of the integrals.')
            else:
                C = a0 - b0
                lines.append('')
                lines.append('at (' + _fn(x0) + ', ' + _fn(y0) + '):  C = ' + _fn(C))
                lines.append('  ' + caseng.tostr(A) + ' = ' + caseng.tostr(B) +
                             ' + ' + _fn(C))
                # make y explicit where A can be undone. ln|y| has to lose its
                # modulus first - the initial condition is what settles the
                # sign, and the check below confirms the branch is the right one.
                Aplain = caseng.strip_abs(A)
                if Aplain != A:
                    lines.append('  (y keeps the sign it has at the')
                    lines.append('   initial point, so the modulus goes)')
                inv = caseng.invert(Aplain, 'y', 'w')
                if inv is not None:
                    rhs = caseng.simplify(('+', B, ('n', C)))
                    expl = cascalc.tidy(caseng.subst(inv, 'w', rhs))
                    lines.append('')
                    lines.append('explicit:  y = ' + caseng.tostr(expl))
                    # check it satisfies the equation at the given point
                    yv = _safe(expl, x0)
                    if yv is not None and abs(yv - y0) < 1e-6:
                        lines.append('(checked: it passes through the')
                        lines.append(' initial point)')
                    else:
                        lines.append('(WARNING: this does not pass through')
                        lines.append(' the initial point - use the implicit')
                        lines.append(' form above)')
    _show('Separable', lines)

# 11. STATIONARY POINTS -----------------------------------------------------
def t_stationary():
    # Solve f'(x) = 0 and classify each root with f''. This is the single most
    # frequent calculus question and there was no route to it: the CAS could
    # differentiate and could solve, but nothing joined the two.
    f = _parse('f(x) =')
    if f is None:
        return
    try:
        d1 = caseng.simplify(caseng.diff(f, 'x'))
        d2 = caseng.simplify(caseng.diff(d1, 'x'))
    except:
        _show('Stationary points', ['Cannot differentiate that.'])
        return
    lines = ['f(x)   = ' + _ts(f), "f'(x)  = " + caseng.tostr(cascalc.tidy(d1)),
             "f''(x) = " + caseng.tostr(cascalc.tidy(d2)), '']
    if d1 == ('n', 0):
        lines.append("f'(x) = 0 everywhere: f is constant,")
        lines.append('so every point is stationary.')
        _show('Stationary points', lines)
        return
    roots = cascalc.solve(d1, 'x')
    if not roots:
        lines.append("f'(x) = 0 has no solution in the")
        lines.append('search range -20 <= x <= 20, so')
        lines.append('there are no stationary points there.')
        _show('Stationary points', lines)
        return
    lines.append("f'(x) = 0 at:")
    for r in roots:
        yv = _safe(f, r)
        s2 = _safe(d2, r)
        pt = '  x = ' + _fn(r)
        if yv is not None:
            pt += ',  y = ' + _fn(yv)
        lines.append(pt)
        # The verdict comes from the sign of f' either side, not from f''.
        # solve returns a root to about 1e-7, and at a degenerate point like
        # x^3 that error alone makes f'' come out slightly negative - which
        # reported a point of inflection as a maximum.
        h = 0.01 * (1.0 + (r if r >= 0 else -r))
        left = _safe(d1, r - h)
        right = _safe(d1, r + h)
        if s2 is not None:
            lines.append("    f'' = " + _fn(s2))
        if left is None or right is None:
            lines.append("    cannot test either side")
        elif left < 0 and right > 0:
            lines.append("    f' goes - to +: MINIMUM")
        elif left > 0 and right < 0:
            lines.append("    f' goes + to -: MAXIMUM")
        else:
            lines.append("    f' keeps its sign: POINT OF")
            lines.append('    INFLECTION (stationary)')
    # non-stationary points of inflection are where f'' changes sign
    infl = cascalc.solve(d2, 'x')
    if infl:
        lines.append('')
        lines.append("f''(x) = 0 at:")
        for r in infl:
            left = _safe(d2, r - 0.01)
            right = _safe(d2, r + 0.01)
            note = ''
            if left is not None and right is not None:
                if (left < 0) != (right < 0):
                    note = '  (f\'\' changes sign: inflection)'
                else:
                    note = '  (no sign change: not an inflection)'
            lines.append('  x = ' + _fn(r) + note)
    _show('Stationary points', lines)

# 12. CONSTANT OF INTEGRATION -----------------------------------------------
def t_constant():
    # Integrate f'(x) and fix the constant from a point on the curve. Small on
    # its own, but attached to almost every integration question.
    _show('Find the curve', ["Enter f'(x) and one point the",
                             'curve passes through. The constant',
                             'of integration is then fixed.'])
    d = _parse("f'(x) =")
    if d is None:
        return
    F = cascalc.integ(d, 'x')
    if F is None:
        _show('Find the curve', ["f'(x) has no elementary integral,",
                                 'so there is no formula for f(x).'])
        return
    F = cascalc.tidy(F)
    x0 = _asknum('curve passes through x =')
    if x0 is None:
        return
    y0 = _asknum('and y =')
    if y0 is None:
        return
    base = _safe(F, x0)
    if base is None:
        _show('Find the curve', ['The integral is undefined at',
                                 'x = ' + _fn(x0) + ', so that point cannot',
                                 'fix the constant.'])
        return
    c = y0 - base
    full = cascalc.tidy(('+', F, ('n', c)))
    lines = ["f'(x) = " + _ts(d), '',
             'integrating: f(x) = ' + caseng.tostr(F) + ' + C', '',
             'at (' + _fn(x0) + ', ' + _fn(y0) + '):',
             '  ' + _fn(y0) + ' = ' + _fn(base) + ' + C',
             '  C = ' + _fn(c), '',
             'f(x) = ' + caseng.tostr(full)]
    chk = _safe(full, x0)
    if chk is not None and abs(chk - y0) < 1e-6:
        lines.append('')
        lines.append('(checked: it passes through the point)')
    v = _asknum('evaluate f at x = (or cancel)')
    if v is not None:
        r = _safe(full, v)
        lines.append('')
        lines.append('f(' + _fn(v) + ') = ' + ('undefined' if r is None else _fn(r)))
    _show('Find the curve', lines)

# 13. VOLUMES OF REVOLUTION AND MEAN VALUE ----------------------------------
def _numint(tree, a, b, var='x'):
    return cascalc.defint(tree, a, b, False, 400, var)

def t_revolution():
    _show('Volume of revolution', ['About the x-axis: V = pi int y^2 dx',
                                   'About the y-axis: V = pi int x^2 dy',
                                   'Enter the curve and the limits.'])
    axis = casui.menu('Rotate about', ['the x-axis (y = f(x))',
                                       'the y-axis (x = g(y))'])
    if axis == -1:
        return
    var = 'x' if axis == 0 else 'y'
    f = _parse(('y = f(x) =' if axis == 0 else 'x = g(y) ='))
    if f is None:
        return
    a = _asknum(var + ' from')
    if a is None:
        return
    b = _asknum(var + ' to')
    if b is None:
        return
    if b < a:
        a, b = b, a
    sq = ('^', f, ('n', 2))
    lines = [('y = ' if axis == 0 else 'x = ') + _ts(f),
             'rotated about the ' + ('x' if axis == 0 else 'y') + '-axis',
             'from ' + var + ' = ' + _fn(a) + ' to ' + _fn(b), '']
    sym = cascalc.integ(caseng.simplify(sq), var)
    if sym is not None:
        sym = cascalc.tidy(sym)
        lines.append('int ' + ('y^2 dx' if axis == 0 else 'x^2 dy') + ' =')
        lines.append('  ' + caseng.tostr(sym))
        hi = _safe(sym, b, {var: b})
        lo = _safe(sym, a, {var: a})
        if hi is not None and lo is not None:
            val = hi - lo
            lines.append('  evaluated: ' + _fn(val))
            lines.append('')
            lines.append('V = pi x ' + _fn(val))
            lines.append('  = ' + _fn(math.pi * val))
            _show('Volume of revolution', lines)
            return
    val = _numint(caseng.simplify(sq), a, b, var)
    if val is None:
        lines.append('Could not integrate over that range')
        lines.append('(a singularity inside the limits?).')
        _show('Volume of revolution', lines)
        return
    lines.append('int ' + ('y^2 dx' if axis == 0 else 'x^2 dy') + ' = ' +
                 _fn(val) + '  (numerically)')
    lines.append('')
    lines.append('V = pi x ' + _fn(val) + ' = ' + _fn(math.pi * val))
    _show('Volume of revolution', lines)

def t_meanvalue():
    _show('Mean value of a function', ['The mean of f over [a, b] is',
                                       '  (1/(b-a)) int from a to b f dx.',
                                       'It is the height of the rectangle',
                                       'with the same area under it.'])
    f = _parse('f(x) =')
    if f is None:
        return
    a = _asknum('from x =')
    if a is None:
        return
    b = _asknum('to x =')
    if b is None:
        return
    if a == b:
        _show('Mean value', ['a and b are equal, so there is',
                             'no interval to average over.'])
        return
    if b < a:
        a, b = b, a
    area = None
    sym = cascalc.integ(f, 'x')
    exact = False
    if sym is not None:
        sym = cascalc.tidy(sym)
        hi = _safe(sym, b)
        lo = _safe(sym, a)
        if hi is not None and lo is not None:
            area = hi - lo
            exact = True
    if area is None:
        area = _numint(f, a, b)
    if area is None:
        _show('Mean value', ['Could not integrate f over that',
                             'interval.'])
        return
    mean = area / (b - a)
    lines = ['f(x) = ' + _ts(f), 'on ' + _fn(a) + ' <= x <= ' + _fn(b), '']
    if exact and sym is not None:
        lines.append('int f dx = ' + caseng.tostr(sym))
    lines.append('area under the curve = ' + _fn(area))
    lines.append('width = ' + _fn(b - a))
    lines.append('')
    lines.append('mean value = ' + _fn(area) + ' / ' + _fn(b - a))
    lines.append('           = ' + _fn(mean))
    # where the function actually takes its mean value
    hits = cascalc.solve(caseng.simplify(('-', f, ('n', mean))), 'x')
    inside = []
    for r in hits:
        if a - 1e-9 <= r <= b + 1e-9:
            inside.append(r)
    if inside:
        lines.append('')
        lines.append('f equals its mean value at:')
        for r in inside:
            lines.append('  x = ' + _fn(r))
    _show('Mean value', lines)

def _graded(f, a, b, var='x'):
    # Integral over [a, b] split into chunks that get much finer towards a.
    # One Simpson pass over [1, 40000] has a step of 100, which for 1/x^2 is
    # nonsense - it reported that a convergent integral diverges. Grading the
    # sub-intervals cubically towards the awkward end keeps the step
    # proportional to how fast the function is actually changing.
    total = 0.0
    n = 24
    prev = a
    i = 1
    while i <= n:
        u = float(i) / n
        pt = a + (b - a) * u * u * u
        part = cascalc.defint(f, prev, pt, False, 120, var)
        if part is None:
            return None
        total += part
        prev = pt
        i += 1
    return total

def _graded_right(f, a, b, var='x'):
    # the same, graded towards b
    total = 0.0
    n = 24
    prev = b
    i = 1
    while i <= n:
        u = float(i) / n
        pt = b - (b - a) * u * u * u
        part = cascalc.defint(f, pt, prev, False, 120, var)
        if part is None:
            return None
        total += part
        prev = pt
        i += 1
    return total

def t_improper():
    # An improper integral is a limit, not a number you can just evaluate.
    # Where there is an antiderivative the limit is taken on it exactly;
    # otherwise the partial integrals are computed and watched.
    _show('Improper integral', ['Improper because a limit is infinite,',
                                'or because f blows up at an end.',
                                'The value is a LIMIT: the tool',
                                'takes the limit and says whether',
                                'it converges.'])
    f = _parse('f(x) =')
    if f is None:
        return
    kind = casui.menu('Which end is improper', ['upper limit is infinity',
                                                'lower limit is -infinity',
                                                'f blows up at the lower limit',
                                                'f blows up at the upper limit'])
    if kind == -1:
        return
    lines = ['f(x) = ' + _ts(f), '']
    sym = cascalc.integ(f, 'x')
    if sym is not None:
        sym = cascalc.tidy(sym)
        lines.append('int f dx = ' + caseng.tostr(sym))
        lines.append('')
    if kind <= 1:
        a = _asknum('the finite limit is x =')
        if a is None:
            return
        steps = []
        t = 10.0
        i = 0
        while i < 7:
            b = a + t if kind == 0 else a - t
            if sym is not None:
                hi = _safe(sym, b)
                lo = _safe(sym, a)
                v = None if (hi is None or lo is None) else (hi - lo)
                if kind == 1 and v is not None:
                    v = -v
            elif kind == 0:
                v = _graded(f, a, b)
            else:
                v = _graded_right(f, b, a)
            steps.append((t, v))
            t *= 10.0
            i += 1
        lines.append('partial integrals as the limit grows:')
    else:
        a = _asknum('lower limit a =')
        if a is None:
            return
        b = _asknum('upper limit b =')
        if b is None:
            return
        if b < a:
            a, b = b, a
        steps = []
        eps = 0.1
        i = 0
        while i < 7:
            if sym is not None:
                if kind == 2:
                    hi = _safe(sym, b)
                    lo = _safe(sym, a + eps)
                else:
                    hi = _safe(sym, b - eps)
                    lo = _safe(sym, a)
                v = None if (hi is None or lo is None) else (hi - lo)
            elif kind == 2:
                v = _graded(f, a + eps, b)
            else:
                v = _graded_right(f, a, b - eps)
            steps.append((eps, v))
            eps /= 10.0
            i += 1
        lines.append('partial integrals as the gap closes:')
    good = []
    for t, v in steps:
        lines.append('  ' + ('%-12s' % _fn(t, 8)) +
                     ('failed' if v is None else _fn(v, 6)))
        if v is not None:
            good.append(v)
    lines.append('')
    if len(good) < 3:
        lines.append('Not enough of the partial integrals')
        lines.append('could be computed to decide.')
    else:
        # Judge convergence on how the SUCCESSIVE CHANGES behave, not on how
        # big the last change is. int 1/sqrt(x) from 0 to 1 converges to 2, but
        # slowly: the last step is still 0.0015, and an absolute threshold
        # called it divergent. The differences shrink by a constant factor when
        # it converges and stay put when it does not - which is also exactly
        # how the tail is argued on paper.
        diffs = []
        i = 1
        while i < len(good):
            diffs.append(good[i] - good[i - 1])
            i += 1
        last = good[len(good) - 1]
        d1 = diffs[len(diffs) - 1]
        d0 = diffs[len(diffs) - 2]
        ratio = None
        if abs(d0) > 1e-15:
            ratio = abs(d1 / d0)
        settled = abs(d1) <= 1e-10 * (1.0 + (last if last >= 0 else -last))
        if settled:
            lines.append('The partial integrals stop changing.')
            lines.append('It CONVERGES to about ' + _fn(last, 6))
            lines.append('')
            if sym is not None:
                lines.append('Write it out as a limit of')
                lines.append('[' + caseng.tostr(sym) + '] between the limits.')
            else:
                lines.append('This is numerical evidence, not a')
                lines.append('proof - write the limit out properly.')
            _show('Improper integral', lines)
            return
        if abs(last) > 1e8 or ratio is None or ratio > 0.9:
            lines.append('The steps are not shrinking:')
            lines.append('  last two changes ' + _fn(d0, 6) + ', ' + _fn(d1, 6))
            lines.append('This integral DIVERGES - there is')
            lines.append('no finite value.')
        else:
            # a geometric tail sums to d1*r/(1-r) beyond the last value
            limit = last + d1 * ratio / (1.0 - ratio)
            lines.append('The changes shrink by a factor of')
            lines.append('about ' + _fn(ratio, 3) + ' each step, so the tail')
            lines.append('is finite.')
            lines.append('It CONVERGES to about ' + _fn(limit, 6))
            lines.append('')
            if sym is not None:
                lines.append('Write it out as a limit of')
                lines.append('[' + caseng.tostr(sym) + '] between the limits.')
            else:
                lines.append('This is numerical evidence, not a')
                lines.append('proof - write the limit out properly.')
    _show('Improper integral', lines)

# 14. SMALL-ANGLE APPROXIMATIONS --------------------------------------------
def t_small_angle():
    _show('Small angles', ['For small x IN RADIANS:',
                           '  sin x = x', '  tan x = x',
                           '  cos x = 1 - x^2/2',
                           'These come from the Maclaurin',
                           'series with the later terms dropped.'])
    x = _asknum('x in radians =')
    if x is None:
        return
    lines = ['x = ' + _fn(x) + ' rad', '']
    for name, exact, approx in (('sin x', math.sin(x), x),
                                ('tan x', math.tan(x) if abs(math.cos(x)) > 1e-12 else None, x),
                                ('cos x', math.cos(x), 1.0 - x * x / 2.0)):
        if exact is None:
            lines.append(name + ': undefined here')
            continue
        err = approx - exact
        lines.append(name)
        lines.append('  exact  ' + _fn(exact, 6))
        lines.append('  approx ' + _fn(approx, 6))
        if abs(exact) > 1e-12:
            lines.append('  error  ' + _fn(err, 9) + ' (' +
                         _fn(100.0 * abs(err / exact), 4) + '%)')
        else:
            lines.append('  error  ' + _fn(err, 9))
    lines.append('')
    if abs(x) <= 0.1:
        lines.append('|x| <= 0.1: the approximations are')
        lines.append('good to about 0.2%.')
    elif abs(x) <= 0.5:
        lines.append('|x| <= 0.5: usable but the error is')
        lines.append('becoming visible.')
    else:
        lines.append('|x| > 0.5 is not a small angle -')
        lines.append('do not use these here.')
    _show('Small angles', lines)

# 12. EXACT TRIG VALUES -----------------------------------------------------
_EXACT = [
    ('0', '0', '0', '1', '0'),
    ('30', 'pi/6', '1/2', 'sqrt(3)/2', '1/sqrt(3)'),
    ('45', 'pi/4', '1/sqrt(2)', '1/sqrt(2)', '1'),
    ('60', 'pi/3', 'sqrt(3)/2', '1/2', 'sqrt(3)'),
    ('90', 'pi/2', '1', '0', 'undefined'),
    ('120', '2pi/3', 'sqrt(3)/2', '-1/2', '-sqrt(3)'),
    ('135', '3pi/4', '1/sqrt(2)', '-1/sqrt(2)', '-1'),
    ('150', '5pi/6', '1/2', '-sqrt(3)/2', '-1/sqrt(3)'),
    ('180', 'pi', '0', '-1', '0'),
    ('270', '3pi/2', '-1', '0', 'undefined'),
    ('360', '2pi', '0', '1', '0'),
]

def t_exact_trig():
    lines = ['deg   rad     sin    cos    tan']
    for d, r, s, c, t in _EXACT:
        lines.append(('%-5s' % d) + ('%-8s' % r) + ('%-7s' % s) + ('%-7s' % c) + t)
    lines.append('')
    lines.append('These are the values you are')
    lines.append('expected to know exactly. sqrt(3)/2')
    lines.append('is also written (root 3)/2.')
    lines.append('')
    lines.append('Useful identities:')
    lines.append('  sin^2 + cos^2 = 1')
    lines.append('  tan = sin / cos')
    lines.append('  1 + tan^2 = sec^2')
    lines.append('  1 + cot^2 = cosec^2')
    lines.append('  sin(A+B) = sinAcosB + cosAsinB')
    lines.append('  cos(A+B) = cosAcosB - sinAsinB')
    lines.append('  sin2A = 2 sinA cosA')
    lines.append('  cos2A = 1 - 2sin^2 A = 2cos^2 A - 1')
    _show('Exact trig values', lines)

TOOLS = [
    ('Composite fg(x)', t_composite),
    ('Inverse function', t_inverse),
    ('Domain & range', t_domain_range),
    ('Modulus |f(x)|', t_modulus),
    ('Graph transformations', t_transform),
    ('Parametric d/dx', t_param_diff),
    ('Parametric -> Cartesian', t_param_cartesian),
    ('Implicit d/dx', t_implicit),
    ('Integration by substitution', t_substitution),
    ('Separation of variables', t_separable),
    ('Stationary points', t_stationary),
    ('Constant of integration', t_constant),
    ('Volume of revolution', t_revolution),
    ('Mean value of f', t_meanvalue),
    ('Improper integral', t_improper),
    ('Small-angle approx', t_small_angle),
    ('Exact trig values', t_exact_trig),
]

def run():
    casutil.run_tools('Functions & calculus', TOOLS)
