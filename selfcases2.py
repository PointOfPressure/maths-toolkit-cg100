# The self test's stage 2 cases (selftest2.py): Trig, Sequences and series,
# Numerical, Vectors, each engine once. Copies of tests_accept.py cases, kept
# apart so the other runs don't hold them in memory.
CASES = (
    ('1 jun23 10ai', 'trig', ['sin(x)=0.5'], 'Solve (degrees)', ['-360', '0'], ['x=-330', 'x=-210']),
    ('2 jun22 4', 'trig', [''], 'Triangle', ['6.1', '8.7', '', '38', '?', '', ''], ['b=61.4', 'b=119'], {'angle': 'deg'}),
    ('3 jun25 10a', 'trig', ['2sin(x)+5cos(x)'], 'R form', ['0'], ['r=sqrt(29)', 'a=68.2'], {'angle': 'deg'}),
    ('1 jun24 12c', 'seq', ['u(n+1)=-6/u(n)'], 'Sum of terms', ['3', '101'], ['sumof101terms=53']),
    ('1 jun22 9c', 'seq', [''], 'AP facts', ['15', '11', '?', '', '100000'], ['s(133)=98553', 's(134)=100031']),
    ('1 jun18 6a', 'seq', ['(4+x)^(-1/2)'], 'Expand', ['3'], ['~1/2-x/16+3x^2/256']),
    ('1 jun18 8b', 'num', ['x-2sin(x)'], 'Newton-Raphson', ['pi', '2'], ['x(3)=1.913223']),
    ('1 jun19 14aii', 'num', ['2x^3/(x^2+1)'], 'Trapezium rule', ['0', '4', '4'], ['area~13.36']),
    ('1 nov21 7c', 'num', ['x=sqrt(x-1+3/x)'], 'Iterate', ['1.5', '3'], ['1.5811', '1.5743', '1.57477']),
    ('2 jun18 14a', 'vec', ['(3,5,1)', '(-1,2,7)'], 'AB and distance', None, ['ab=-4i-3j+6k', '|ab|=sqrt(61)']),
    ('2 jun23 18b', 'vec', ['-3i-sqrt(3)j', '-3i+sqrt(3)j'], 'Angle between', None, ['angle=60'], {'angle': 'deg'}),
    ('2 nov21 12', 'vec', [''], 'From size, direction', ['6', '30'], ['3sqrt(3)i+3j'], {'angle': 'deg'}),
)
