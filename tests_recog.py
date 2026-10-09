# Unit tests for the recogniser (recog.py): every form, and the near-misses
# that must not be taken for it. Then the tiles the mockups show, and a sweep
# that runs every action offered for every input here: an offered action must
# work (the spec: an action that can't apply is never shown).

# (rows, kind, {attribute: value}, words the grey line must have)
FORMS = [
    # polynomials, letters as constants
    (['x^2+3x+k'], 'poly', {'deg': 2, 'letters': ['k']}, 'quadratic in x, k unknown'),
    (['2x+3'], 'poly', {'deg': 1}, 'linear in x'),
    (['30x^3-7x^2-7x+2'], 'poly', {'deg': 3}, 'cubic in x'),
    (['x^5+1'], 'poly', {'deg': 5}, 'degree 5'),
    (['x^2+3x+2=0'], 'poly', {'deg': 2}, 'quadratic equation'),
    (['x^2+3x+2>0'], 'poly', {'deg': 2}, 'quadratic inequality'),
    (['kx^2+4x+k'], 'poly', {'deg': 2, 'letters': ['k']}, 'k unknown'),
    (['x^2+bx+c'], 'poly', {'deg': 2, 'letters': ['b', 'c']}, 'b and c unknown'),
    (['(2+kx)^5'], 'poly', {'deg': 5, 'expand': True}, 'degree 5'),
    (['(x-3)(2x+7)'], 'poly', {'deg': 2, 'expand': True}, 'quadratic'),
    # near-miss: brackets that cancel are not the degree they look
    (['(x+1)^2-x^2'], 'poly', {'deg': 1}, 'linear'),
    (['(x+1)^2-(x-1)^2-4x'], 'num', {}, 'numbers'),
    (['y=x^2+3x'], 'poly', {'deg': 2}, 'quadratic in x'),
    (['f(x)=2x+3'], 'poly', {'deg': 1}, 'linear in x'),
    (['t^2-4t'], 'poly', {'var': 't', 'deg': 2}, 'quadratic in t'),
    (['p(400p+70)+70=382'], 'poly', {'var': 'p', 'deg': 2}, 'in p'),
    # quadratic in something else
    (['x^4-5x^2+4'], 'poly', {'qin': True, 'ushow': 'x^2'}, 'quadratic in x^2'),
    (['x-5sqrt(x)+6=0'], 'qpow', {'qin': True, 'ushow': 'sqrt x'}, 'quadratic in sqrt x'),
    (['x^(2/3)-5x^(1/3)+4=0'], 'qpow', {'qin': True, 'ushow': 'x^(1/3)'}, 'quadratic in x^(1/3)'),
    (['1/x^2+1/x-6=0'], 'qpow', {'qin': True, 'ushow': '1/x'}, 'quadratic in 1/x'),
    (['4^x-3*2^x+2=0'], 'exp', {'qin': True, 'ushow': '2^x'}, 'quadratic in 2^x'),
    (['9^x-4*3^(x+1)+27=0'], 'exp', {'qin': True, 'ushow': '3^x'}, 'quadratic in 3^x'),
    (['3^(2x+1)-28*3^x+9=0'], 'exp', {'qin': True, 'ushow': '3^x'}, 'quadratic in 3^x'),
    (['e^(2x)-5e^x+6=0'], 'exp', {'qin': True, 'ushow': 'e^x'}, 'quadratic in e^x'),
    (['2^x+2^(-x)=5/2'], 'exp', {'qin': True, 'recip': True, 'ushow': '2^x'}, 'quadratic in 2^x'),
    (['e^x=6-e^(x/2)'], 'exp', {'qin': True, 'ushow': 'e^(x/2)'}, 'quadratic in e^(x/2)'),
    (['2^(0.5x)-3*2^(0.25x)+2=0'], 'exp', {'qin': True}, 'quadratic in 2^(0.25x)'),
    # near-misses: not quadratic in anything
    (['x^4+x^3+1'], 'poly', {'qin': False, 'deg': 4}, 'quartic'),
    (['x^4-5x^2+4x'], 'poly', {'qin': False}, 'quartic'),
    (['x-5sqrt(x)+6x^2'], 'power', {'qin': False}, 'powers of x'),
    (['8^x-2^x=0'], 'exp', {'qin': False}, 'exponential equation, base 2'),
    (['4^x-3*3^x+2=0'], 'exp2', {'qin': False}, 'bases 2 and 3'),
    (['x+1/x'], 'rat', {'qin': False}, 'fraction'),
    (['log(x)^2-3log(x)+2=0'], 'log', {'qin': True, 'ushow': 'log x'}, 'quadratic in log x'),
    (['ln(x)^2=ln(x)+6'], 'log', {'qin': True, 'ushow': 'ln x'}, 'quadratic in ln x'),
    (['2sin(x)^2-sin(x)=1'], 'trig', {'qin': True, 'ushow': 'sin x'}, 'quadratic in sin x'),
    # near-miss: ln x and ln(x + 1) are different things
    (['ln(x)^2+ln(x+1)=0'], 'log', {'qin': False}, 'log equation'),
    # exponentials
    (['2^x+3=15'], 'exp', {'qin': False, 'bases': [2]}, 'exponential equation, base 2'),
    (['8^x=4^(x+1)'], 'exp', {'bases': [2]}, 'base 2'),
    (['5^x=3^(x+4)'], 'exp2', {}, 'bases 5 and 3'),
    (['400e^(-0.1216047x)=280'], 'exp', {'dec': True}, 'base e'),
    (['1.08^t=500000/7940'], 'exp', {'var': 't'}, 'base 1.08'),
    (['5^(x-2)=7^1570'], 'exp', {}, 'base 5'),
    (['y=2^x+3'], 'exp', {}, 'exponential, base 2'),
    # two unknowns, models
    (['2^x+3^y=15'], 'xy', {'vars2': ['x', 'y']}, 'equation in x and y'),
    (['x^2+y^2=25'], 'xy', {}, 'x and y'),
    (['N=Ae^(kt)'], 'model', {'model': 'aekt', 'consts': ['a', 'k'], 'var': 't'}, 'a and k unknown'),
    (['m=Ae^(-kt)'], 'model', {'model': 'aekt'}, 'model'),
    (['y=kb^x'], 'model', {'model': 'kbx'}, 'model'),
    (['y=ax^n'], 'model', {'model': 'axn', 'var': 'x'}, 'model'),
    # near-miss: one unknown constant is not a two-point model
    (['N=400e^(kt)'], 'exp', {'model': ''}, ''),
    # logs, modulus, fractions, the rest
    (['2log(x)=log(4)+log(x+8)'], 'log', {}, 'log equation in x'),
    (['logb(3,2x)-logb(3,x)'], 'log', {}, 'log expression'),
    (['ln(x)+3'], 'log', {}, 'log expression'),
    (['abs(2x-3)<5'], 'abs', {}, 'modulus inequality'),
    (['abs(3x-6)=abs(2x)'], 'abs', {}, 'modulus equation'),
    (['(3x+5)/((x-1)(x+2))'], 'rat', {}, 'fraction in x'),
    (['(x^2+10)/(2x+5)=x'], 'rat', {}, 'equation with fractions'),
    (['sin(x)=0.5'], 'trig', {}, 'trig equation'),
    (['x*e^x'], 'func', {}, 'function of x'),
    (['x^(3/2)=8'], 'power', {}, 'equation in x'),
    (['sqrt(x)/(x-3)'], 'func', {}, 'function of x'),
    # no x at all
    (['sqrt(12)+sqrt(27)'], 'num', {'surd': True}, 'surds'),
    (['2+3*4'], 'num', {'surd': False, 'logs': False}, 'numbers'),
    (['logb(2,8)+logb(2,4)'], 'num', {'logs': True}, 'logs'),
    (['(6a+15d)^2'], 'const', {'expand': True}, 'a and d'),
    # two rows
    (['x+2y=5', '3x-y=1'], 'pair', {'pair': 'simul', 'vars2': ['x', 'y']}, 'two equations in x and y'),
    (['y=x^2', 'y=2x+1'], 'pair', {'pair': 'simul'}, 'two equations'),
    (['a+5d=25', '4a+70d=4a^2+20ad+25d^2'], 'pair', {'pair': 'simul', 'vars2': ['a', 'd']}, 'a and d'),
    (['x^2+1', '2x-3'], 'pair', {'pair': 'fg'}, 'f and g'),
    (['f(x)=x^2', 'g(x)=2x+1'], 'pair', {'pair': 'fg'}, 'f and g'),
]

# Coord geometry: (points in the boxes, rows), items, words
GEO = [
    ([('1', '2'), ('5', '-6')], [], [], '2 points A and B'),
    ([('8', '17'), ('15', '10'), ('-2', '-7')], [], [], '3 points A, B and C'),
    ([('1', '2')], ['y=3x+1'], ['line'], 'line and point A'),
    ([], ['2x+3y=6'], ['line'], 'line'),
    ([], ['x=4'], ['line'], 'line'),
    ([], ['x^2+y^2-6x+4y=12'], ['circle'], 'circle'),
    ([], ['(x-3)^2+(y+2)^2=25'], ['circle'], 'circle'),
    ([], ['x^2+y^2+4x-6y=k'], ['circle'], 'k unknown'),
    # near-misses: not circles
    ([], ['x^2+2y^2=25'], ['curve'], 'curve'),
    ([], ['x^2+y^2+xy=1'], ['curve'], 'curve'),
    ([], ['y=x^2'], ['curve'], 'curve'),
    ([], ['y=2x+1', 'x^2+y^2=25'], ['line', 'circle'], 'line and circle'),
    ([], ['x=t^2+1', 'y=2t'], ['param'], 'parametric'),
    ([], ['t^2+1', '2t'], ['param'], 'parametric'),
]
GEO_ERR = [([('1', '')], [], 'fill in both'), ([('1', '2+')], [], 'A:'), ([], ['x+y='], 'nothing after')]

# typing mistakes: read as errors, never guessed at
ERRORS = [
    (['x=1=2'], 'one'),
    (['2x+'], 'cannot read'),
    (['x>'], 'nothing after'),
    (['=3'], 'nothing before'),
    (['x$2'], 'cannot read'),
    ([''], 'type something'),
]

# the tiles the mockups show, in order (docs/mockups)
TILES = [
    ('alg', ['x^2+3x+k'], ['Complete square', 'Factorise', 'Roots', 'Discriminant', 'Vertex', 'Graph']),
    ('exp', ['4^x-3*2^x+2=0'], ['Solve', 'Sub u = 2^x', 'Factorise', 'Graph']),
    ('exp', ['2^x+3=15'], ['Solve', 'Rearrange for x', 'Take logs', 'Graph']),
    ('exp', ['2^x+3^y=15'], ['Rearrange for y', 'Rearrange for x', 'Implicit dy/dx', 'Graph']),
]

# what an action asks gets these answers in the sweep
ANSWER = {'Factor theorem': ['1'], 'Divide': ['x-1'], 'Graph': ['2', '3', '4'],
          'Range on an interval': ['0', '3'], 'Transform': ['2', '1', '0', '0'],
          'Inequality': [0], 'From two points': ['1', '2', '3', '7', '']}

def run(check):
    import recog
    import acts
    import topic
    import caslex
    import plot
    plot.run = lambda *a, **k: None
    for rows, kind, attrs, words in FORMS:
        F = recog.form(rows)
        key = 'recog <' + '; '.join(rows) + '>'
        check(key + ' reads', F.err is None, F.err)
        check(key + ' is ' + kind, F.kind == kind, F.kind + ': ' + F.note)
        for a in attrs:
            got = getattr(F, a)
            want = attrs[a]
            check(key + ' ' + a + ' = ' + repr(want), got == want, repr(got))
        check(key + ' says ' + repr(words), words in F.note, F.note)
    for pts, eqs, items, words in GEO:
        F = recog.geo(pts, eqs)
        key = 'recog geo ' + repr(pts) + ' ' + repr(eqs)
        check(key + ' reads', F.err is None, F.err)
        check(key + ' items', F.items == items, F.items)
        check(key + ' says ' + repr(words), words in F.note, F.note)
        for o in acts.offers(F, 'geo'):
            label, mod, fn, arg, ask = o
            vals = [caslex.parse('2')] if ask else None
            lines = topic.engine(mod, fn, F, arg, vals)
            bad = [ln[1] for ln in (lines or []) if isinstance(ln, tuple) and ln[0] == '!' and 'error' in ln[1]]
            check('offered geo ' + label + ' ' + key + ' runs', not bad, bad)
    for pts, eqs, words in GEO_ERR:
        F = recog.geo(pts, eqs)
        check('recog geo refuses ' + repr(pts) + repr(eqs), F.err is not None and words in F.err, F.err)
    for rows, words in ERRORS:
        F = recog.form(rows)
        check('recog refuses <' + '; '.join(rows) + '>', F.err is not None and words in F.err, F.err)
    for tid, rows, want in TILES:
        got = [o[0] for o in acts.offers(recog.form(rows), tid)][:len(want)]
        check('tiles ' + tid + ' <' + rows[0] + '> as the mockup', got == want, got)
    # every offered action runs, in both topics
    for rows, kind, attrs, words in FORMS:
        F = recog.form(rows)
        for tid in ('alg', 'exp'):
            for o in acts.offers(F, tid):
                label, mod, fn, arg, ask = o
                vals = None
                if ask:
                    if ask[0] == 'choose':
                        vals = [0]
                    else:
                        n = sum([ln[1] for ln in ask])
                        a = ANSWER.get(label, ['1'] * n)
                        vals = [None if (x == '' or x == '?') else
                                (x if isinstance(x, int) else caslex.parse(x)) for x in a[:n]]
                        while len(vals) < n:
                            vals.append(caslex.parse('2'))
                lines = topic.engine(mod, fn, F, arg, vals)
                bad = [ln[1] for ln in (lines or []) if isinstance(ln, tuple) and ln[0] == '!'
                       and 'error' in ln[1]]
                check('offered ' + tid + ' ' + label + ' <' + '; '.join(rows) + '> runs', not bad, bad)
                if lines is not None:
                    boxed = [ln for ln in lines if isinstance(ln, tuple) and ln[0] == '=']
                    warned = [ln for ln in lines if isinstance(ln, tuple) and ln[0] == '!']
                    check('offered ' + tid + ' ' + label + ' <' + '; '.join(rows) + '> answers',
                          boxed or warned, lines[-3:])
                    for b in boxed:
                        for view in ('exact', 'decimal', 'both'):
                            s = topic.shown(b, view)
                            check('boxed text <' + '; '.join(rows) + '> ' + label,
                                  isinstance(s, str) and s.strip() != '', b)

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    fails = []
    n = [0]

    def check(label, ok, detail=''):
        n[0] += 1
        if not ok:
            fails.append(label + '  [' + str(detail) + ']')
    run(check)
    for f in fails:
        print('FAIL ' + f)
    print(str(n[0]) + ' checks, ' + str(len(fails)) + ' failures')
