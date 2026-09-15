# One or more cases for every bullet of docs/superpowers/specs/
# 2026-09-15-cas-engine-upgrade.md.  Called by tests.py.
import caslex
import caseng
import caspoly
import cascalc
import casalg
import cassolve
import casrender

P = caslex.parse
TS = caseng.tostr

def S(e):
    return TS(caseng.simplify(P(e)))

def EX(e):
    return TS(casalg.expand(P(e)))

def FA(e, surds=False):
    r = casalg.factorise(P(e), 'x', surds)
    return None if r is None else TS(r)

def IN(e, v='x'):
    r = cascalc.integ(P(e), v)
    return None if r is None else TS(cascalc.tidy(r))

def DI(e, v='x'):
    return TS(cascalc.tidy(caseng.diff(P(e), v)))

def SO(e, v='x'):
    return [TS(r) for r in cassolve.solve_exact(P(e), v)]

# ---- canonical form -------------------------------------------------------

CANON = [
    # exact rational constants
    ('1/3+1/6', '1/2'), ('(2/3)^2', '4/9'), ('0.25', '1/4'),
    ('1/2-1/3', '1/6'), ('2/4', '1/2'), ('0.125+0.375', '1/2'),
    # flattened, collected, ordered by degree, coefficient first
    ('1-2x+3x^2', '3*x^2-2*x+1'), ('x*y^2+x^2*y', 'x^2*y+x*y^2'),
    ('x+x+x', '3*x'), ('2x-5x', '-3*x'), ('x^2+3-x^2', '3'),
    # products, same base powers combined
    ('x^(1/2)*x^(3/2)', 'x^2'), ('2x*3x', '6*x^2'), ('x^3/x^2', 'x'),
    ('(x*y)^3', 'x^3*y^3'),
    # negative and fractional powers
    ('x^(-2)', '1/x^2'), ('x^(1/2)', 'sqrt(x)'), ('x^(3/2)', 'x*sqrt(x)'),
    ('x^(-1/2)', '1/sqrt(x)'),
    # rational expressions over a common denominator, gcd cancelled
    ('(x^2-1)/(x-1)', 'x+1'), ('(x^2+3x+2)/(x^2-4)', '(x+1)/(x-2)'),
    ('x+1/x', '(x^2+1)/x'), ('x/(x^2+1)^2', 'x/(x^2+1)^2'),
    # surds
    ('sqrt(8)', '2*sqrt(2)'), ('sqrt(2)*sqrt(6)', '2*sqrt(3)'),
    ('sqrt(a)/sqrt(b)', 'sqrt(a/b)'), ('2sqrt(3)+5sqrt(3)', '7*sqrt(3)'),
    ('sqrt(x^2)', '|x|'), ('(sqrt(2)+1)(sqrt(2)-1)', '1'),
    ('1/sqrt(2)', 'sqrt(2)/2'), ('(3+sqrt(5))/(2-sqrt(5))', '-5*sqrt(5)-11'),
    ('sqrt(50)/sqrt(2)', '5'),
    # logs
    ('ln(e^x)', 'x'), ('e^(ln(x))', 'x'), ('ln(1)', '0'), ('ln(e)', '1'),
    ('log(100)', '2'), ('logb(2,8)', '3'), ('ln(8)/ln(2)', '3'),
    ('ln(sqrt(x))', 'ln(x)/2'), ('e^(2ln(x))', 'x^2'),
    # exponentials
    ('e^a*e^b', 'e^(a+b)'), ('(e^x)^2', 'e^(2*x)'), ('2^x*2^y', '2^(x+y)'),
    ('e^x*e^(-x)', '1'),
    # trig identities and symmetries
    ('sin(x)^2+cos(x)^2', '1'), ('1+tan(x)^2', 'sec(x)^2'),
    ('sin(x)/cos(x)', 'tan(x)'), ('2sin(x)cos(x)', 'sin(2*x)'),
    ('cos(x)^2-sin(x)^2', 'cos(2*x)'), ('sin(-x)', '-sin(x)'),
    ('cos(-x)', 'cos(x)'), ('sin(x+2pi)', 'sin(x)'), ('sin(pi-x)', 'sin(x)'),
    ('cos(pi/2-x)', 'sin(x)'), ('sin(pi/3)', 'sqrt(3)/2'),
    ('sec(x)*cos(x)', '1'), ('cot(x)*tan(x)', '1'), ('cosec(x)*sin(x)', '1'),
    ('1/sec(x)', 'cos(x)'), ('sech(x)*cosh(x)', '1'),
    ('cos(2pi/3)', '-1/2'), ('tan(pi/4)', '1'), ('1/cos(x)', 'sec(x)'),
    ('1/sin(x)', 'cosec(x)'), ('cos(x)/sin(x)', 'cot(x)'),
    ('asin(1/2)', 'pi/6'), ('atan(1)', 'pi/4'), ('acos(-1)', 'pi'),
    ('asin(-sqrt(3)/2)', '-pi/3'),
    # hyperbolic
    ('cosh(x)^2-sinh(x)^2', '1'), ('1+sinh(x)^2', 'cosh(x)^2'),
    ('cosh(0)', '1'), ('sinh(0)', '0'), ('sinh(-x)', '-sinh(x)'),
    ('cosh(-x)', 'cosh(x)'),
    # complex, exact
    ('(2+3i)/(1-i)', '-1/2+5i/2'), ('i^7', '-i'), ('(1+i)^8', '16'),
    ('conj(2-i)', '2+i'), ('mod(3+4i)', '5'), ('arg(1+i)', 'pi/4'),
    ('abs(2+3i)^2', '13'), ('sqrt(-12)', '2i*sqrt(3)'), ('e^(i*pi)', '-1'),
    ('2*(cos(pi/3)+i*sin(pi/3))', 'i*sqrt(3)+1'),
    # factorials and binomials
    ('5!', '120'), ('ncr(6,2)', '15'), ('npr(5,2)', '20'),
    ('x!/(x-1)!', 'x'), ('(x+1)!/x!', 'x+1'), ('ncr(n,2)', 'n*(n-1)/2'),
    # modulus
    ('abs(x^2)', 'x^2'), ('abs(-x)', '|x|'), ('abs(2x)', '2*|x|'),
    ('abs(x)^2', 'x^2'), ('abs(-3)', '3'),
    # printing
    ('x/2', 'x/2'), ('-x/2', '-x/2'), ('2*sqrt(3)', '2*sqrt(3)'),
    ('pi/4', 'pi/4'), ('2pi/3', '2*pi/3'), ('e^(2x)', 'e^(2*x)'),
    ('1*x', 'x'), ('x^1', 'x'), ('x+(-3)', 'x-3'), ('-1/2', '-1/2'),
    ('(x+1)/(x-2)', '(x+1)/(x-2)'), ('sin(x)^2', 'sin(x)^2'),
    ('1/x', '1/x'),
]

EXPAND = [
    ('(x+2)(x-3)', 'x^2-x-6'),
    ('(a+b)^4', 'a^4+4*a^3*b+6*a^2*b^2+4*a*b^3+b^4'),
    ('(1+i)*(2-i)', '3+i'),
    ('(sqrt(2)+1)*(sqrt(3)-1)', 'sqrt(6)-sqrt(2)+sqrt(3)-1'),
    ('sin(a+b)', 'cos(a)*sin(b)+cos(b)*sin(a)'),
    ('cos(a-b)', 'cos(a)*cos(b)+sin(a)*sin(b)'),
    ('cos(2x)', 'cos(x)^2-sin(x)^2'),
    ('sin(2x)', '2*cos(x)*sin(x)'),
    ('tan(a-b)', '(tan(a)-tan(b))/(tan(a)*tan(b)+1)'),
    ('sin(x+pi/6)', 'cos(x)/2+sin(x)*sqrt(3)/2'),
    ('ln(a*b)', 'ln(a)+ln(b)'),
    ('ln(x*y^2)', 'ln(x)+2*ln(y)'),
    ('ln(x^2)', '2*ln(x)'),
    ('log(x/y)', 'log(x)-log(y)'),
    ('sin(pi/12)', 'sqrt(6)/4-sqrt(2)/4'),
    ('cos(pi/12)', 'sqrt(2)/4+sqrt(6)/4'),
    ('sin(5pi/12)', 'sqrt(6)/4+sqrt(2)/4'),
    ('tan(pi/12)', '-sqrt(3)+2'),
]

FACTOR = [
    ('x^2-5x+6', False, '(x-2)*(x-3)'),
    ('2x^2+4x', False, '2*x*(x+2)'),
    ('6x^2+9x', False, '3*(2*x+3)*x'),
    ('x^4-16', False, '(x+2)*(x-2)*(x^2+4)'),
    ('x^3+8', False, '(x+2)*(x^2-2*x+4)'),
    ('x^3-27', False, '(x-3)*(x^2+3*x+9)'),
    ('x^3+x^2+x+1', False, '(x+1)*(x^2+1)'),
    ('e^(2x)-3e^x+2', False, '(e^(x)-1)*(e^(x)-2)'),
    ('sin(x)^2-sin(x)', False, 'sin(x)*(sin(x)-1)'),
    ('x^2-2', True, '(x+sqrt(2))*(x-sqrt(2))'),
    ('x^2-3', True, '(x+sqrt(3))*(x-sqrt(3))'),
]

DIFF = [
    ('x^2*sin(x)', 'cos(x)*x^2+2*sin(x)*x'),
    ('ln(sin(x))', 'cot(x)'),
    ('(2x+1)/(x-1)', '-3/(x-1)^2'),
    ('asin(2x)', '2/sqrt(-4*x^2+1)'),
    ('2^x', '2^x*ln(2)'),
    ('atanh(x)', '1/(-x^2+1)'),
    ('asinh(x)', '1/sqrt(x^2+1)'),
    ('e^(2x)', '2*e^(2*x)'),
]

INTEG = [
    ('x^3', 'x^4/4'), ('1/x', 'ln(|x|)'), ('e^(3x)', 'e^(3*x)/3'),
    ('2^x', '2^x/ln(2)'), ('sin(2x)', '-cos(2*x)/2'), ('cos(x)', 'sin(x)'),
    ('tan(x)', '-ln(|cos(x)|)'), ('sec(x)^2', 'tan(x)'),
    ('cosec(x)^2', '-cot(x)'), ('sec(x)*tan(x)', 'sec(x)'),
    ('cosec(x)*cot(x)', '-cosec(x)'),
    ('sec(x)', 'ln(|sec(x)+tan(x)|)'),
    ('cosec(x)', '-ln(|cosec(x)+cot(x)|)'),
    ('sinh(x)', 'cosh(x)'), ('cosh(x)', 'sinh(x)'), ('tanh(x)', 'ln(cosh(x))'),
    ('sech(x)^2', 'tanh(x)'),
    ('1/(x^2+4)', 'atan(x/2)/2'),
    ('1/sqrt(4-x^2)', 'asin(x/2)'),
    ('1/sqrt(x^2+9)', 'asinh(x/3)'),
    ('1/sqrt(x^2-4)', 'acosh(x/2)'),
    ('1/(4-x^2)', 'ln(|x+2|)/4-ln(|x-2|)/4'),
    ('(2x+3)/(x^2+3x+1)', 'ln(|x^2+3*x+1|)'),
    ('2x*(x^2+1)^3', '(x^2+1)^4/2'),
    ('x*e^(x^2)', 'e^(x^2)/2'),
    ('cos(x)*sin(x)^4', 'sin(x)^5/5'),
    ('sin(x)^2', 'x/2-sin(2*x)/4'),
    ('cos(3x)^2', 'sin(6*x)/12+x/2'),
    ('sin(x)^3', 'cos(x)^3/3-cos(x)'),
    ('tan(x)^2', 'tan(x)-x'),
    ('tan(x)^3', 'sec(x)^2/2+ln(|cos(x)|)'),
    ('sin(3x)cos(2x)', '-cos(5*x)/10-cos(x)/2'),
    ('x*e^x', 'e^(x)*x-e^(x)'),
    ('e^x*sin(x)', '(-cos(x)+sin(x))*e^(x)/2'),
    ('ln(x)', 'ln(x)*x-x'),
    ('x*ln(x)', 'ln(x)*x^2/2-x^2/4'),
    ('asin(x)', 'asin(x)*x+sqrt(-x^2+1)'),
    ('1/(x^2+2x+5)', 'atan((x+1)/2)/2'),
    ('1/(x^2+1)^2', 'atan(x)/2+x/(2*(x^2+1))'),
    ('1/(x*ln(x))', 'ln(|ln(x)|)'),
    ('x/sqrt(1-x^2)', '-sqrt(-x^2+1)'),
]

SOLVE = [
    ('2x-6', ['3']),
    ('x^2-5x+6', ['2', '3']),
    ('x^2-2x-1', ['-sqrt(2)+1', 'sqrt(2)+1']),
    ('x^2+2x+5', ['-1+2i', '-1-2i']),
    ('x^3-2x^2-5x+6', ['-2', '1', '3']),
    ('x^4-5x^2+4', ['-2', '-1', '1', '2']),
    ('e^(2x)-3e^x+2', ['0', 'ln(2)']),
    ('sin(x)^2-1/4', ['-pi/6', 'pi/6', '5*pi/6', '7*pi/6']),
    ('2^x-8', ['3']),
    ('3^(2x+1)-5', ['ln(5/3)/(2*ln(3))']),
    ('ln(x)+ln(x-1)-ln(6)', ['3']),
    ('sqrt(2x+3)-x', ['3']),
    ('sqrt(x+4)-sqrt(x-1)-1', ['5']),
    ('abs(2x-1)-(x+2)', ['-1/3', '3']),
    ('1/x+1/(x+1)-1', ['(-sqrt(5)+1)/2', '(sqrt(5)+1)/2']),
    ('3cosh(x)+2sinh(x)-5', ['ln((-2*sqrt(5)+5)/5)', 'ln((2*sqrt(5)+5)/5)']),
    ('tanh(x)-1/2', ['ln(3)/2']),
]

def run(check):
    for src, want in CANON:
        got = S(src)
        check('cas canonical ' + src, got == want, got)
    for src, want in EXPAND:
        got = EX(src)
        check('cas expand ' + src, got == want, got)
    for src, surds, want in FACTOR:
        got = FA(src, surds)
        check('cas factorise ' + src, got == want, got)
    for src, want in DIFF:
        got = DI(src)
        check('cas diff ' + src, got == want, got)
    for src, want in INTEG:
        got = IN(src)
        check('cas integ ' + src, got == want, got)
    for src, want in SOLVE:
        got = SO(src)
        check('cas solve ' + src, got == want, got)
    _algebra(check)
    _calculus(check)
    _solving(check)
    _printing(check)
    _limits(check)
    _menu(check)

def _algebra(check):
    # combine logs, change of base, hyperbolic definitions
    check('cas combine log', TS(casalg.combine_log(P('ln(a)+ln(b)'))) == 'ln(a*b)')
    check('cas combine 2ln', TS(casalg.combine_log(P('2ln(x)+ln(y)'))) == 'ln(x^2*y)')
    check('cas logbase 4^x', TS(casalg.logbase(P('4^x'), 2)) == '2^(2*x)')
    got = TS(casalg.to_exp(P('sinh(x)')))
    check('cas sinh to exp', got == '(e^(x)-e^(-x))/2', got)
    got = TS(casalg.to_exp(P('asinh(x)')))
    check('cas arsinh to log', got == 'ln(x+sqrt(x^2+1))', got)
    # complete the square
    got = TS(casalg.complete_square(P('2x^2+8x+3')))
    check('cas complete square', got == '2*(x+2)^2-5', got)
    got = TS(casalg.complete_square(P('x^2+2x+5')))
    check('cas complete square 2', got == '(x+1)^2+4', got)
    # polynomial division and the remainder / factor theorem
    q, r = casalg.divide(P('x^3-2x+1'), P('x-1'))
    check('cas divide q', TS(q) == 'x^2+x-1', TS(q))
    check('cas divide r', TS(r) == '0', TS(r))
    q, r = casalg.divide(P('2x^3+3x^2-1'), P('x+2'))
    check('cas divide q2', TS(q) == '2*x^2-x+2', TS(q))
    check('cas divide r2', TS(r) == '-5', TS(r))
    check('cas remainder theorem',
          TS(casalg.remainder(P('2x^3+3x^2-1'), P('-2'))) == '-5')
    # partial fractions
    res = caspoly.partial(P('3x+5'), P('(x-1)*(x+2)'))
    check('cas partial linear',
          [(TS(a), TS(b), c) for a, b, c in res[1]] ==
          [('8/3', 'x-1', 1), ('1/3', 'x+2', 1)])
    res = caspoly.partial(P('1'), P('(x-1)^2*(x+1)'))
    check('cas partial repeated',
          [(TS(a), TS(b), c) for a, b, c in res[1]] ==
          [('-1/4', 'x-1', 1), ('1/2', 'x-1', 2), ('1/4', 'x+1', 1)])
    res = caspoly.partial(P('3x+1'), P('(x-1)*(x^2+1)'))
    check('cas partial quadratic',
          [(TS(a), TS(b), c) for a, b, c in res[1]] ==
          [('2', 'x-1', 1), ('-2*x+1', 'x^2+1', 1)])
    res = caspoly.partial(P('x^3'), P('(x-1)*(x+1)'))
    check('cas partial improper', TS(res[0]) == 'x', TS(res[0]))
    # single fraction and rationalising
    got = TS(casalg.single_fraction(P('1/x+1/(x+1)')))
    check('cas single fraction', got == '(2*x+1)/(x*(x+1))', got)
    got = TS(casalg.single_fraction(P('2/(x-2)+3/(x+2)')))
    check('cas single fraction 2', got == '(5*x-2)/((x+2)*(x-2))', got)
    got = TS(casalg.rationalise(P('1/(sqrt(x)+1)')))
    check('cas rationalise symbolic', got == '(sqrt(x)-1)/(x-1)', got)
    got = TS(casalg.rationalise(P('1/(2-sqrt(3))')))
    check('cas rationalise numeric', got == 'sqrt(3)+2', got)
    # substitution, exact
    got = TS(casalg.subst_exact(P('sin(x)+cos(x)'), 'x', P('pi/3')))
    check('cas subst pi/3', got == 'sqrt(3)/2+1/2', got)
    check('cas subst 1+i', TS(casalg.subst_exact(P('x^2+1'), 'x', P('1+i'))) == '1+2i')
    got = TS(casalg.subst_exact(P('x^2-2x'), 'x', P('sqrt(2)')))
    check('cas subst sqrt2', got == '-2*sqrt(2)+2', got)
    # rearrange / make the subject
    got = TS(casalg.rearrange(P('(2x+1)/(x-3)')))
    check('cas rearrange', got == '(3*y+1)/(y-2)', got)
    got = TS(casalg.make_subject(P('v'), P('u+a*t'), 't'))
    check('cas make subject', got == '(-u+v)/a', got)
    # series
    got = TS(casalg.maclaurin(P('e^x'), 'x', 5))
    check('cas maclaurin exp', got == 'x^4/24+x^3/6+x^2/2+x+1', got)
    got = TS(casalg.maclaurin(P('sin(x)'), 'x', 6))
    check('cas maclaurin sin', got == 'x^5/120-x^3/6+x', got)
    got = TS(casalg.maclaurin(P('ln(1+x)'), 'x', 5))
    check('cas maclaurin ln', got == '-x^4/4+x^3/3-x^2/2+x', got)
    got = TS(casalg.binom_series(P('1'), P('-1'), 4))
    check('cas binomial -1', got == '-x^3+x^2-x+1', got)
    got = TS(casalg.binom_series(P('2'), P('1/2'), 4))
    check('cas binomial half', got == 'x^3/2-x^2/2+x+1', got)
    check('cas binomial validity', TS(casalg.binom_validity(P('3'))) == '1/3')

def _limits(check):
    cases = [('(x^2-4)/(x-2)', '2', '4'),
             ('(1-cos(x))/x^2', '0', '1/2'),
             ('sin(3x)/x', '0', '3'),
             ('(e^x-1)/x', '0', '1'),
             ('x^2-1', '3', '8')]
    for e, a, want in cases:
        r = casalg.limit(P(e), 'x', P(a))
        got = None if r is None else TS(r)
        check('cas limit ' + e, got == want, got)
    r = casalg.limit(P('(2x^3-x)/(5x^3+1)'), 'x', None, 1)
    check('cas limit inf', r is not None and TS(r) == '2/5')
    r = casalg.limit(P('1/x'), 'x', None, 1)
    check('cas limit inf zero', r is not None and TS(r) == '0')

def _calculus(check):
    got = TS(cascalc.diff_implicit(P('x^2+y^2'), P('25')))
    check('cas implicit', got == '-x/y', got)
    got = TS(cascalc.diff_param(P('t^2'), P('t^3')))
    check('cas parametric', got == '3*t/2', got)
    got = TS(cascalc.diff_param(P('cos(t)'), P('sin(t)')))
    check('cas parametric trig', got == '-cot(t)', got)
    got = TS(cascalc.tidy(caseng.diff(caseng.diff(P('sin(x)')))))
    check('cas second derivative', got == '-sin(x)', got)
    for e, a, b, want in [('sin(x)', '0', 'pi', '2'),
                          ('1/(1+x^2)', '0', '1', 'pi/4'),
                          ('x^3', '0', '2', '4'),
                          ('e^x', '0', '1', 'e-1')]:
        r = cascalc.defint_exact(P(e), P(a), P(b))
        got = None if r is None else TS(r)
        check('cas defint ' + e, got == want, got)
    r = cascalc.defint_exact(P('1/x^2'), P('1'), 'inf')
    check('cas improper 1/x^2', r is not None and TS(r) == '1')
    r = cascalc.defint_exact(P('1/sqrt(x)'), P('0'), P('1'))
    check('cas improper 1/sqrt x', r is not None and TS(r) == '2')
    r = cascalc.defint_exact(P('e^(-x)'), P('0'), 'inf')
    check('cas improper e^-x', r is not None and TS(r) == '1')
    div = False
    try:
        cascalc.defint_exact(P('1/x'), P('1'), 'inf')
    except ValueError:
        div = True
    check('cas divergence detected', div)
    check('cas volume', TS(cascalc.volume(P('x'), P('0'), P('1'))) == 'pi/3')
    check('cas volume sqrt', TS(cascalc.volume(P('sqrt(x)'), P('0'), P('4'))) == '8*pi')
    check('cas mean value', TS(cascalc.meanvalue(P('x^2'), P('0'), P('3'))) == '3')
    check('cas arc length cosh',
          TS(cascalc.arclength(P('cosh(x)'), P('0'), P('1'))) == 'sinh(1)')

def _solving(check):
    got = [TS(r) for r in cassolve.general_trig(P('2sin(2x)-1'))]
    check('cas general sin', got == ['n*pi+pi/12', 'n*pi+5*pi/12'], got)
    got = [TS(r) for r in cassolve.general_trig(P('tan(x)-1'))]
    check('cas general tan', got == ['n*pi+pi/4'], got)
    got = [TS(r) for r in cassolve.general_trig(P('cos(x)-1/2'))]
    check('cas general cos', got == ['2*n*pi+pi/3', '2*n*pi-pi/3'], got)
    got = [TS(r) for r in cassolve.solve_interval(P('2sin(2x)-1'), 'x', P('0'), P('2pi'))]
    check('cas interval', got == ['pi/12', '5*pi/12', '13*pi/12', '17*pi/12'], got)
    got = [TS(r) for r in cassolve.solve_interval(P('sin(x)^2-1/4'), 'x', P('0'), P('2pi'))]
    check('cas interval sq', got == ['pi/6', '5*pi/6', '7*pi/6', '11*pi/6'], got)
    got = [TS(r) for r in cassolve.simultaneous([P('2x+3y-13'), P('x-y+1')], ['x', 'y'])]
    check('cas simultaneous 2', got == ['2', '3'], got)
    got = [TS(r) for r in cassolve.simultaneous(
        [P('x+y+z-6'), P('2x-y+z-3'), P('x+2y-z-2')], ['x', 'y', 'z'])]
    check('cas simultaneous 3', got == ['1', '2', '3'], got)
    got = [(TS(a), TS(b)) for a, b in
           cassolve.linear_quadratic(P('y-x-1'), P('x^2+y^2-25'))]
    check('cas linear+quadratic', got == [('-4', '-3'), ('3', '4')], got)
    for e, op, want in [('x^2-2x-3', '>', 'x < -1 or x > 3'),
                        ('x^2-4', '<', '-2 < x < 2'),
                        ('2x-6', '>=', 'x >= 3'),
                        ('(x-1)/(x+2)', '>', 'x < -2 or x > 1'),
                        ('abs(x-1)-3', '<', '-2 < x < 4'),
                        ('x^3-x', '>', '-1 < x < 0 or x > 1')]:
        got = cassolve.ineq_str(cassolve.solve_ineq(P(e), op))
        check('cas inequality ' + e + op, got == want, got)
    got = cassolve.ineq_set(cassolve.solve_ineq(P('x^2-2x-3'), '>'))
    check('cas inequality set', got == '(-inf, -1) U (3, inf)', got)
    roots, exact = cassolve.solve_any(P('x-cos(x)'))
    check('cas numeric fallback flagged', (not exact) and len(roots) == 1)
    roots, exact = cassolve.solve_any(P('x^2-4'))
    check('cas exact preferred', exact and [TS(r) for r in roots] == ['-2', '2'])

def _printing(check):
    check('cas print no 1*', '1*' not in S('1*x*y'))
    check('cas print no ^1', '^1' not in S('x^1*y'))
    check('cas print no + -', '+-' not in S('x+(-3)'))
    check('cas print ln abs', IN('1/x') == 'ln(|x|)')
    box = casrender.build(P('sin(x)^2'), 0)
    check('cas typeset sin^2 x', box[0] == 'row' and box[1][0] == ('atom', 'sin', 'medium')
          and box[1][2] == ('atom', 'x', 'medium'))
    box = casrender.build(P('abs(x)'), 0)
    check('cas typeset bars', box[0] == 'row' and box[1][0][1] == '|')
    w, a, d = casrender.measure(casrender.build(P('ln(abs(x))+c'), 0))
    check('cas typeset measures', w > 0 and a > 0)


def _menu(check):
    # the CAS screen: every new operation returns lines the result screen can show
    import casui
    import casutil
    check('cas menu length', len(casui.CAS_OPS) == 25, len(casui.CAS_OPS))
    for want in ('complete the square', 'rationalise', 'single fraction',
                 'expand trig / log', 'solve exact f(x)=0',
                 'general solution (trig)', 'series (Maclaurin)',
                 'limit x -> a', 'substitute x = a', 'rearrange for x'):
        check('cas menu has ' + want, want in casui.CAS_OPS)
    for label in casui.CAS_OPS:
        check('cas menu label fits: ' + label, len(label) <= 26, len(label))
    old = casutil.ask
    answers = {}

    def ask(spec, label=''):
        return answers.get(spec)
    casutil.ask = ask
    try:
        def op(i, tree):
            return casui._cas_op(i, P(tree), tree)
        lines = op(16, '2x^2+8x+3')
        check('cas menu complete square', TS(lines[0][1]) == '2*(x+2)^2-5')
        lines = op(17, '1/(2-sqrt(3))')
        check('cas menu rationalise', TS(lines[0][1]) == 'sqrt(3)+2', TS(lines[0][1]))
        lines = op(18, '1/x+1/(x+1)')
        check('cas menu single fraction', TS(lines[0][1]) == '(2*x+1)/(x*(x+1))',
              TS(lines[0][1]))
        lines = op(15, 'cos(2x)')
        check('cas menu expand trig', TS(lines[0][1]) == 'cos(x)^2-sin(x)^2')
        lines = op(19, 'x^2-2')
        check('cas menu solve exact', lines[0] == 'x = -sqrt(2)', lines[0])
        lines = op(20, '2sin(2x)-1')
        check('cas menu general solution', lines[0] == 'x = n*pi+pi/12', lines[0])
        answers['terms'] = [5]
        lines = op(21, 'e^x')
        check('cas menu series', TS(lines[0][1]) == 'x^4/24+x^3/6+x^2/2+x+1')
        answers['a(x)'] = [P('1')]
        lines = op(22, '(x^2-1)/(x-1)')
        check('cas menu limit', TS(lines[0][1]) == '2', TS(lines[0][1]))
        check('cas parse inf', P('inf') == ('v', 'inf'))
        answers['a(x)'] = [P('inf')]
        lines = op(22, '(2x^3-x)/(5x^3+1)')
        check('cas menu limit inf', TS(lines[0][1]) == '2/5', lines)
        answers['a(x)'] = [P('pi/3')]
        lines = op(23, 'sin(x)+cos(x)')
        check('cas menu substitute', TS(lines[0][1]) == 'sqrt(3)/2+1/2')
        lines = op(2, '1/x')
        check('cas menu integral + c', lines[1] == '+ c', lines)
        answers['a,b'] = [0.0, 1.0]
        lines = op(3, '1/(1+x^2)')
        check('cas menu definite exact', TS(lines[0][1]) == 'pi/4', lines)
        answers.clear()
        lines = op(24, '(2x+1)/(x-3)')
        check('cas menu rearrange', TS(lines[0][1]) == '(3*y+1)/(y-2)')
        answers.clear()
        i = 0
        while i < len(casui.CAS_OPS):
            try:
                casui._cas_op(i, P('x^2-1'), 'x^2-1')
                ok = True
            except ValueError:
                ok = True
            except Exception as e:
                ok = repr(e)
            check('cas menu op ' + str(i) + ' runs', ok is True, ok)
            i += 1
    finally:
        casutil.ask = old
