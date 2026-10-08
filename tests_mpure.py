# Cases for mpure.py (AQA 7357 sections A-F).
# (section code, tool label, typed input, needles that must appear)
CASES = [
    # ---- A  Proof ----------------------------------------------------------
    ('A', 'Counterexample f>0', 'n^2-5n+3,1,10',
     ['counterexample n = 1', 'f(1) = -1']),
    ('A', 'Counterexample f>0', 'n^2+1,1,20',
     ['no counterexample found', 'not a proof']),
    ('A', 'Counterexample prime', 'n^2+n+41,1,50',
     ['counterexample n = 40', 'f(40) = 41 x 41']),
    ('A', 'Counterexample prime', 'n^2+n+17,1,10',
     ['no counterexample found']),
    ('A', 'Counterexample d|f(n)', 'n^3-n,3,1,20',
     ['no counterexample found']),
    ('A', 'Counterexample d|f(n)', 'n^2+1,3,1,5',
     ['counterexample n = 1', 'rem 2']),
    ('A', 'Counterexample f=g', '(n+1)^2,n^2+2n+1,1,10',
     ['no counterexample found']),
    ('A', 'Counterexample f=g', 'n^2,2n,1,5',
     ['counterexample n = 1', 'f = 1, g = 2']),

    # ---- B  Algebra and functions -----------------------------------------
    ('B', 'Index a^(p/q)', '8,2,3', ['= 4', 'root 3 of 8 = 2']),
    ('B', 'Index a^(p/q)', '16,-3,4', ['= 1/8', 'decimal = 0.125']),
    ('B', 'Index a^(p/q)', '-4,1,2', ['not real']),
    ('B', 'Simplify sqrt(n)', '12', ['sqrt(12) = 2*sqrt(3)', 'decimal = 3.46']),
    ('B', 'Simplify sqrt(n)', '49', ['sqrt(49) = 7']),
    ('B', 'Simplify surd expr', 'sqrt(8)+sqrt(18)', ['= 5sqrt(2)', '7.07']),
    # 7357/3 Nov21 Q6, 7357/1 Jun23 Q7a, 7357/1 Jun24 Q7
    ('B', 'Simplify surd expr', '(10+5x-2sqrt(x)-x^(3/2))/(5-sqrt(x))', ['= x+2']),
    ('B', 'Simplify surd expr', '7/(3+5sqrt(x))-7/(5sqrt(x)-3)', ['= -42/(25*x-9)']),
    ('B', 'Simplify surd expr', '(3+sqrt(8x))/(1+sqrt(2x))',
     ['= (4*x-3+sqrt(2*x))/(2*x-1)', 'u = sqrt(2x)']),
    ('B', 'Simplify surd expr', 'sqrt(16x^2)', ['= 4*x', 'x > 0 assumed']),
    ('B', 'Simplify surd expr', 'sqrt(x^(16/15))', ['= x^(8/15)']),
    ('B', 'Rationalise', '1,0,1,1,1,2', ['= sqrt(2)-1', 'decimal = 0.414']),
    ('B', 'Rationalise', '3,2,5,1,-1,5', ['(-13-5*sqrt(5))/4', '-6.05']),
    ('B', 'Quadratic', '1,-3,2', ['x = 1', 'x = 2', 'disc = 1',
                                  'vertex (3/2, -1/4)']),
    ('B', 'Quadratic', '1,2,5', ['-1+2i', '-1-2i', 'no real roots']),
    ('B', 'Quadratic', '1,-2,-1', ['x = 1-sqrt(2)', 'x = 1+sqrt(2)',
                                   'disc = 8']),
    ('B', 'Quadratic', '1,-4,4', ['x = 2 (repeated)', 'disc = 0']),
    ('B', 'Quadratic', '2,3,1', ['x = -1', 'x = -1/2', 'vertex (-3/4, -1/8)']),
    ('B', 'Quadratic', '0,2,-6', ['x = 3', 'this is linear']),
    # param-letters: 7357/2 Jun19 Q7bi 3x^2 + 6px = 0
    ('B', 'Quadratic', '3,6p,0', ['x = 0', 'x = -2*p', 'disc = 36*p^2']),
    ('B', 'Quadratic', '1,2k,k^2-1', ['x = -k-1', 'x = -k+1', 'disc = 4']),
    ('B', 'Quadratic in f(x)', '1,-5,4,x^2',
     ['u = f(x) = 1', 'u = f(x) = 4', 'x = -2', 'x = 2']),
    ('B', 'Simultaneous 2 linear', '2,3,8,1,-1,1', ['x = 11/5', 'y = 6/5']),
    ('B', 'Simultaneous 2 linear', '1,1,2,2,2,5',
     ['no solution', 'parallel']),
    ('B', 'Line meets quadratic', '1,1,1,0,-1', ['(-1, 0)', '(2, 3)']),
    ('B', 'Solve f(x)=g(x)', 'x^2,x+2', ['(-1, 1)', '(2, 4)']),
    # 7357/1 Jun18 Q11b: t = 49.009, outside -20..20
    ('B', 'Solve f(x)=g(x)', '10+100(x/30)^3-50(x/30)^4,4.5*1.063^x',
     ['(-12.1, 2.15)', '(49, 89.9)']),
    # 7357/1 Jun18 Q9b: a = -55 and -5
    ('B', 'Solve f(x)=g(x)', '4x+14(25-x),4x^2+4x(25-x)+(25-x)^2',
     ['(-55, 900)', '(-5, 400)']),
    # 7357/3 Jun19 Q8bii t = 58.87; Nov20 Q5a t = 52.8; Jun22 Q7b d = 4481
    ('B', 'Solve f(x)=g(x)', '5(4+11e^(-0.068066x)),21', ['(58.9, 21)']),
    ('B', 'Solve f(x)=g(x)', 'e^(-0.0435935x),0.1', ['(52.8, 1/10)']),
    ('B', 'Solve f(x)=g(x)', '0.2*x^1.5,60000', ['(4480, 60000)']),
    ('B', 'Solve f(x)=g(x)', 'sin(x),0.5,0,7',
     ['(pi/6, 1/2)', '(5pi/6, 1/2)', '(13pi/6, 1/2)', 'in 0..7']),
    ('B', 'Solve f(x)=g(x)', '(x-1)^2*e^x,0', ['(1, 0)', '1 crossing(s)']),
    # 7357/1 Jun18 Q9b: a + 5d = 25 with the sum condition (a=x, d=y)
    ('B', 'Simultaneous non-linear', 'x+5y-25,4x+70y-4x^2-20x*y-25y^2',
     ['(x, y) = (-55, 16)', '(x, y) = (-5, 6)']),
    # 7357/2 Jun19 Q6: a = 2, b = 2sqrt3 (or 4, 0)
    ('B', 'Simultaneous non-linear', 'x^2+y^2-16,sqrt(3)/2*x+y/2-2sqrt(3)',
     ['(x, y) = (2, 2sqrt(3))', '(x, y) = (4, 0)']),
    # 7357/3 Nov20 Q8a: a/(1-r) = 96, ar = 18 -> a = 24, r = 3/4 (or 72, 1/4)
    ('B', 'Simultaneous non-linear', 'x/(1-y)-96,x*y-18',
     ['(x, y) = (24, 3/4)', '(x, y) = (72, 1/4)']),
    # 7357/3 Jun19 Q8a: L = 11, k = 0.068066
    ('B', 'Simultaneous non-linear', '5(4+x)-75,5(4+x*e^(-2y))-68',
     ['(x, y) = (11, -ln(48/55)/2)', '= (11, 0.0681)']),
    ('B', 'Simultaneous non-linear', 'x^2+y,y^2+x', ['(-1, -1)', '(0, 0)']),
    ('B', 'Linear inequality', '2,-6', ['> 0: x > 3', '< 0: x < 3']),
    ('B', 'Linear inequality', '-2,6', ['> 0: x < 3', '< 0: x > 3']),
    ('B', 'Quadratic inequality', '1,-3,2',
     ['f > 0: x < 1 or x > 2', 'f < 0: 1 < x < 2']),
    ('B', 'Quadratic inequality', '1,0,1',
     ['f > 0: every x', 'f < 0: no x', 'no real roots']),
    ('B', 'Inequality f(x) > g(x)', 'x^2-4x,5',
     ['f > g: x < -1 or x > 5', 'f < g: -1 < x < 5', 'f = g at x = -1, 5']),
    # (x+1)/(x-2) - 3 = (7-2x)/(x-2): positive between 2 and 7/2
    ('B', 'Inequality f(x) > g(x)', '(x+1)/(x-2),3',
     ['f > g: 2 < x < 7/2', 'f < g: x < 2 or x > 7/2', 'undefined at x = 2']),
    ('B', 'Inequality f(x) > g(x)', 'x^3,4x',
     ['f > g: -2 < x < 0 or x > 2', 'f < g: x < -2 or 0 < x < 2']),
    ('B', 'Inequality f(x) > g(x)', 'sqrt(x-1),2', ['f > g: x > 5', 'f < g: 1 < x < 5']),
    # 7357/1 Nov20 Q8b: 300.22 < t < 408.78
    ('B', 'Inequality f(x) > g(x)', '3.87sin(2pi(x+101.75)/365)+11.7,14,0,500',
     ['f > g: 0 < x < 43.8 or 300 < x < 409', 'only 0 < x < 500']),
    ('B', 'Inequality f(x) > g(x)', 'e^(0.01x),5', ['f > g: x > 161']),
    ('B', 'Inequality f(x) > g(x)', 'tan(x),0,0,3',
     ['f > g: 0 < x < pi/2', 'undefined at x = pi/2']),
    # x^2 + kx + 4: D = k^2 - 16
    ('B', 'Discriminant in k', '1,k,4',
     ['equal roots: k = -4, 4', 'real roots: k <= -4 or k >= 4',
      'distinct: k < -4 or k > 4', 'no real roots: -4 < k < 4', '(k+4)*(k-4)']),
    # (k-1)x^2 + 4x + (k+2): D = 16 - 4(k-1)(k+2) = -4(k+3)(k-2)
    ('B', 'Discriminant in k', 'k-1,4,k+2',
     ['equal roots: k = -3, 2', 'distinct: -3 < k < 2',
      'no real roots: k < -3 or k > 2', 'k = 1 makes a = 0']),
    # 2x^2 + (k-3)x + k: D = k^2 - 14k + 9, k = 7 +- 2 sqrt 10
    ('B', 'Discriminant in k', '2,k-3,k',
     ['equal roots: k = 7-2*sqrt(10), 2*sqrt(10)+7', 'k = 0.675, 13.3']),
    # kx^2 + (k+3)x + 1: D = k^2 + 2k + 9 > 0 always
    ('B', 'Discriminant in k', 'k,k+3,1',
     ['equal roots: no k', 'distinct: every k', 'no real roots: no k']),
    ('B', 'Discriminant in k', '1,2,3', ['no real roots for any k']),
    ('B', 'Expand', '(2x-1)(x+3)', ['2*x^2+5*x-3']),
    ('B', 'Factorise', 'x^2-5x+6', ['(x-2)*(x-3)']),
    ('B', 'Factorise', 'x^2+1', ['no rational factorisation']),
    # 7357/2 Jun19 Q7bi: 3x^2 + 6px = 0 at x = 0, -2p
    ('B', 'Factorise', '3x^2+6p*x', ['3*x*(x+2*p)', '= 0 at x = 0, -2*p']),
    ('B', 'Factorise', 'x^2-k^2', ['(x+k)*(x-k)', '= 0 at x = -k, k']),
    ('B', 'Factorise', '2x^2-5k*x+2k^2', ['(2*x-k)*(x-2*k)']),
    ('B', 'Factorise', 'x^2+2a*x+a^2', ['(x+a)^2']),
    ('B', 'Factorise', 'x^2-5x+6', ['= 0 at x = 2, 3']),
    ('B', 'Divide p(x) by d(x)', 'x^3-2x^2-5x+6,x-1',
     ['quotient = x^2-x-6', 'remainder = 0', '(x-1) is a factor']),
    ('B', 'Divide p(x) by d(x)', 'x^2+1,x-2',
     ['quotient = x+2', 'remainder = 5']),
    ('B', 'Factor theorem', 'x^3-2x^2-5x+6,1',
     ['p(1) = 0', '(x - 1) is a factor']),
    ('B', 'Factor theorem', 'x^3-2x^2-5x+6,2',
     ['p(2) = -4', 'is not a factor']),
    # 7357/1 Nov21 Q13a: p(-1/5) = 0 exactly
    ('B', 'Factor theorem', '125x^3+150x^2+55x+6,-1/5',
     ['p(-1/5) = 0', '(5x + 1) is a factor']),
    ('B', 'Simplify f(x)/g(x)', 'x^2-1,x^2+2x+1',
     ['(x-1)/(x+1)', 'x != -1']),
    ('B', 'Partial fractions', '3x+2,(x+1)(x+2)',
     ['-1/(x+1)+4/(x+2)', '-1 / (x+1)', '4 / (x+2)']),
    # the user's own factors and whole numerators: 7357/2 Nov21 Q5,
    # 7357/1 Jun23 Q16a, 7357/2 Jun24 Q9b, 7357/3 Jun25 Q8a
    ('B', 'Partial fractions', '5(x-3),(2x-11)(4-3x)', ['= 1/(4-3*x)-1/(2*x-11)']),
    ('B', 'Partial fractions', '1,16-9x^2', ['(1/8) / (4-3*x)', '(1/8) / (3*x+4)']),
    ('B', 'Partial fractions', '36x,(1+3x)(2-3x)', ['= -4/(1+3*x)+8/(2-3*x)']),
    ('B', 'Partial fractions', 'x,2x^2+3x+1', ['= 1/(x+1)-1/(2*x+1)']),
    ('B', 'Composite fg and gf', '2x+1,x^2,3',
     ['2*x^2+1', '4*x^2+4*x+1', 'fg(3) = 19', 'gf(3) = 49']),
    ('B', 'Inverse function', '2x+3', ['f-1(x) = (x-3)/2']),
    ('B', 'Inverse function', 'x^2+x', ['many-to-one', 'f(-3/2) = f(1/2) = 3/4']),
    ('B', 'Inverse function', 'x^3+x', ['no inverse formula found']),
    # 7357/2 Jun19 Q3: x^2 has no inverse; 7357/1 Jun25 Q12b: f(-1) = f(1)
    ('B', 'Inverse function', 'x^2', ['many-to-one: no inverse', 'f(-1) = f(1) = 1']),
    ('B', 'Inverse function', 'x^2+5', ['many-to-one: no inverse', 'f(-1) = f(1) = 6']),
    # 7357/1 Jun24 Q17cii: h(-1) = h(1)
    ('B', 'Inverse function', 'ln(abs(x)+1)', ['many-to-one', 'f(-1) = f(1)']),
    ('B', 'Inverse function', 'x^2,0,?', ['f-1(x) = sqrt(x)', 'domain of f-1: x >= 0']),
    ('B', 'Inverse function', 'x^2,?,0', ['f-1(x) = -sqrt(x)']),
    # 7357/1 Nov20 Q13ai: f is self-inverse
    ('B', 'Inverse function', '(2x+3)/(x-2)',
     ['f-1(x) = (2*x+3)/(x-2)', 'domain of f-1: x < 2 or x > 2']),
    ('B', 'Inverse function', 'e^x+2', ['f-1(x) = ln(x-2)', 'domain of f-1: x > 2']),
    # (x-3)^2 + 1: least 1 at x = 3
    ('B', 'Range of f on [a,b]', 'x^2-6x+10,0,5', ['range: 1 <= f(x) <= 10', "f' = 0 at x = 3"]),
    ('B', 'Range of f on [a,b]', 'x^2-6x+10,4,?', ['range: f(x) >= 2']),
    ('B', 'Range of f on [a,b]', 'e^(-x)+2,0,?', ['range: 2 < f(x) <= 3']),
    ('B', 'Range of f on [a,b]', 'x^3-3x,?,?', ['range: all real values']),
    ('B', 'Range of f on [a,b]', '1/x,-1,1', ['range: f(x) <= -1 or f(x) >= 1']),
    # 7357/1 Jun19 Q6a, Jun25 Q12a, Q12dii
    ('B', 'Range of f on [a,b]', '(x^2+1)/2,0,?', ['range: f(x) >= 1/2']),
    ('B', 'Range of f on [a,b]', 'x^2+5,?,?', ['range: f(x) >= 5']),
    ('B', 'Range of f on [a,b]', 'sqrt(x^2+5),?,?', ['range: f(x) >= sqrt(5)']),
    # 7357/2 Jun23 Q8b: A = 2cosec^2 x >= 2, on 0 < x < pi
    ('B', 'Range of f on [a,b]', '2/sin(x)^2,0,pi', ['range: f(x) >= 2']),
    # 7357/3 Jun22 Q10e: split by the asymptote x = -5/2
    ('B', 'Range of f on [a,b]', '(x^2+10)/(2x+5),?,?',
     ['range: f(x) <= (-5-sqrt(65))/2 or f(x) >= (sqrt(65)-5)/2']),
    # 7357/1 Jun24 Q17a: the corner at x = 0
    ('B', 'Range of f on [a,b]', 'abs(x)+1,-10,10', ['range: 1 <= f(x) <= 11']),
    ('B', 'Range of f on [a,b]', 'abs(x)+1,?,?', ['range: f(x) >= 1']),
    ('B', 'Range of f on [a,b]', 'ln(x)-x,?,?', ['range: f(x) <= -1']),
    ('B', 'Range of f on [a,b]', 'atan(x),?,?', ['range: -pi/2 < f(x) < pi/2']),
    ('B', 'Range of f on [a,b]', 'sqrt(x-1),?,?', ['range: f(x) >= 0']),
    ('B', 'Domain of f(x)', 'x/sqrt(2x-2)', ['domain: x > 1']),
    # 7357/3 Jun18 Q6a, 7357/2 Nov21 Q10a, Jun23 Q7b, 7357/1 Jun24 Q17b
    ('B', 'Domain of f(x)', 'sqrt(x)/(x-3)', ['{x : x >= 0, x != 3}']),
    ('B', 'Domain of f(x)', '1/sqrt(10-2x)', ['domain: x < 5']),
    ('B', 'Domain of f(x)', 'ln(x)', ['domain: x > 0']),
    ('B', 'Domain of f(x)', 'x^2+1', ['domain: all real x']),
    ('B', 'Domain of f(x)', 'sqrt(x^2-4)', ['domain: x <= -2 or x >= 2']),
    ('B', 'Domain of f(x)', '1/(x^2-4)', ['domain: x != -2, 2']),
    ('B', 'Transform af(bx+c)+d', 'x^2,2,1,0,3', ['2*x^2+3']),
    ('B', 'Solve |ax+b|=cx+d', '1,-2,0,4', ['x = -2', 'x = 6']),
    ('B', 'Solve |ax+b|=cx+d', '1,0,0,-1', ['no solution']),
    ('B', 'Proportion y=kx^n', '2,3,18', ['k = 2', '2*x^2']),
    ('B', 'Plot f(x)', 'x^2-4,-3,3',
     ['y(0) = -4', 'root x = -2', 'root x = 2']),

    # ---- C  Coordinate geometry -------------------------------------------
    ('C', 'Line through 2 points', '1,2,3,8',
     ['y = 3x - 1', '3x - y - 1 = 0', 'midpoint (2, 5)',
      'length = 2sqrt(10)']),
    ('C', 'Line through 2 points', '2,1,2,5', ['x = 2', 'length = 4']),
    ('C', 'Perpendicular bisect', '1,2,5,4',
     ['y = -2x + 9', 'midpoint (3, 3)']),
    ('C', 'Parallel through pt', '3,1,2', ['y = 3x - 1']),
    ('C', 'Perpendicular thru pt', '2,4,1',
     ['y = -(1/2)x + 3', 'x + 2y - 6 = 0']),
    ('C', 'Intersect y=mx+c', '2,1,-1,4', ['(1, 3)']),
    ('C', 'Intersect y=mx+c', '2,1,2,4', ['no intersection', 'parallel']),
    ('C', 'Triangle 3 vertices', '0,0,4,0,0,3',
     ['area = 6', 'AB = 4, BC = 5, CA = 3', 'right angle at A', 'B = 36.9']),
    # shoelace |1(8-1) + 5(1-2) + 7(2-8)|/2 = 20
    ('C', 'Triangle 3 vertices', '1,2,5,8,7,1',
     ['area = 20', 'AB = 2sqrt(13)', 'AB^2 = 52, BC^2 = 53, CA^2 = 37']),
    ('C', 'Circle from general', '-2,4,-4',
     ['centre (1, -2)', 'radius = 3', '(x - 1)^2 + (y + 2)^2 = 9']),
    ('C', 'Circle from general', '0,0,4', ['not a real circle']),
    # 7357/2 Nov21 Q7a: centre (3, 4), radius sqrt(25 + p)
    ('C', 'Circle from general', '-6,-8,-p',
     ['centre (3, 4)', 'radius = sqrt(p+25)', 'needs p+25 > 0']),
    # 7357/1 Nov21 Q5b, Jun22 Q8ai, 7357/2 Nov20 Q6a
    ('C', 'Foot of perpendicular', '-4,3,21,15,2', ['foot (3, 11)', 'distance = 15']),
    ('C', 'Foot of perpendicular', '5,3,83,0,5', ['foot (10, 11)', 'distance = 2*sqrt(34)']),
    ('C', 'Foot of perpendicular', '12,5,298,7,9', ['foot (19, 14)', 'distance = 13']),
    ('C', 'Circle centre+radius', '1,-2,3',
     ['(x - 1)^2 + (y + 2)^2 = 9', 'x^2 + y^2 - 2x + 4y - 4 = 0']),
    ('C', 'Circle through 3 pts', '0,0,4,0,0,3',
     ['centre (2, 3/2)', 'radius = 5/2', 'one chord is a diameter']),
    ('C', 'Circle through 3 pts', '0,0,1,1,2,2', ['no circle', 'collinear']),
    ('C', 'Line meets circle', '1,0,0,0,2',
     ['(-sqrt(2), -sqrt(2))', '(sqrt(2), sqrt(2))']),
    ('C', 'Line meets circle', '0,5,0,0,2', ['no intersection']),
    ('C', 'Tangent to circle', '0,0,3,4',
     ['3x + 4y - 25 = 0', 'radius = 5']),
    ('C', 'Param to Cartesian', '2t,t^2', ['y = x^2/4']),
    ('C', 'Param to Cartesian', '3cos(t),3sin(t)', ['x^2 + y^2 = 9']),
    ('C', 'Param point at t', 't^2,t^3,2',
     ['(4, 8)', 'dy/dx = 3', 'y = 3x - 4']),
    ('C', 'Plot parametric', 'cos(t),sin(t),0,6.28318530718',
     ['start (1, 0)', 'end (1, 0)']),

    # ---- D  Sequences and series ------------------------------------------
    ('D', 'Arithmetic a,d,n', '3,5,10', ['u(10) = 48', 'S(10) = 255']),
    ('D', 'Geometric a,r,n', '2,3,5',
     ['u(5) = 162', 'S(5) = 242', 'no sum to infinity']),
    ('D', 'Geometric a,r,n', '4,1/2,6',
     ['u(6) = 1/8', 'S(6) = 63/8', 'S(inf) = 8']),
    ('D', 'AP: n for Sn > k', '3,5,100', ['n = 7', 'S(7) = 126']),
    ('D', 'GP: n for Sn > k', '2,3,100', ['n = 5', 'S(5) = 242']),
    ('D', 'GP: n for Sn > k', '4,1/2,20', ['no such n', 'S(inf) = 8']),
    # u5 = 18, u12 = 46: 7d = 28
    ('D', 'AP from 2 terms', '5,18,12,46',
     ['a = 2', 'd = 4', 'u(n) = 4n - 2', 'S(n) = 2n^2']),
    # a + 4d = 18, 10a + 45d = 175 -> d = -1, a = 22
    ('D', 'AP from term and sum', '5,18,10,175', ['a = 22', 'd = -1', 'u(n) = -n + 23']),
    ('D', 'GP from 2 terms', '3,12,6,96', ['r = 2, a = 3', 'r^3 = 8']),
    ('D', 'GP from 2 terms', '2,6,4,1.5',
     ['r = 1/2, a = 12, S(inf) = 24', 'r = -1/2, a = -12, S(inf) = -8']),
    ('D', 'Binomial (a+bx)^n', '2,3,4',
     ['x^0: 16', 'x^1: 96', 'x^2: 216', 'x^4: 81']),
    ('D', 'Binomial (a+bx)^n', '1,-1,3', ['x^1: -3', 'x^3: -1']),
    ('D', 'Binomial rational n', '1,1,1/2',
     ['x^1: 1/2', 'x^2: -1/8', 'x^3: 1/16', 'valid for |x| < 1']),
    ('D', 'Binomial rational n', '4,-1,-1',
     ['x^0: 1/4', 'x^1: 1/16', 'valid for |x| < 4']),
    ('D', 'Sigma sum f(r) a..b', 'r^2,1,10', ['sum = 385', '10 terms']),
    ('D', 'Recurrence u(n+1)', 'u^2-1,2,5',
     ['u(2) = 3', 'u(4) = 63', 'increasing']),
    ('D', 'Recurrence u(n+1)', '1/u,2,6', ['periodic, period 2']),
    # 2, -3, -1/2, 1/3 repeat: 25 cycles of -7/6 then u(1) = 2
    ('D', 'Recurrence sum to N', '(1+u)/(1-u),2,101',
     ['sum u(1..101) = -163/6', 'period 4', '101 = 25 x 4 + 1']),
    ('D', 'Recurrence sum to N', '-1/u,2,100', ['sum u(1..100) = 75']),
    # u(n) = 2^n + 1, sum = 2^11 - 2 + 10
    ('D', 'Recurrence sum to N', '2u-1,3,10', ['sum u(1..10) = 2056']),
    # u(n) = 2 + 2(1/2)^(n-1): sum 300 + 4(1 - 2^-150)
    ('D', 'Recurrence sum to N', '0.5u+1,4,150', ['sum u(1..150) = 304']),
    ('D', 'Terms of u(n)', '3n-1,1,5',
     ['u(1) = 2', 'u(5) = 14', 'increasing']),
    ('D', 'nCr and nPr', '5,2', ['nCr = 10', 'nPr = 20', 'n! = 120']),

    # ---- E  Trigonometry ---------------------------------------------------
    ('E', 'Exact trig at x deg', '30',
     ['sin 30 = 1/2', 'cos 30 = sqrt(3)/2', 'tan 30 = sqrt(3)/3']),
    ('E', 'Exact trig at x deg', '15',
     ['sin 15 = (sqrt(6)-sqrt(2))/4', 'tan 15 = 2-sqrt(3)']),
    ('E', 'Exact trig at x deg', '90', ['cos 90 = 0', 'tan 90 is undefined']),
    ('E', 'Triangle SSS', '3,4,5',
     ['A = 36.9 deg', 'C = 90 deg', 'area = 6']),
    ('E', 'Triangle SSS', '1,2,9', ['cannot make a triangle']),
    ('E', 'Triangle SAS', '5,7,60', ['a = sqrt(39)', 'area = 35sqrt(3)/4']),
    ('E', 'Triangle ASA', '30,60,5', ['b = 5sqrt(3)', 'c = 10']),
    ('E', 'Triangle SSA', '4,5,30', ['B = 38.7 deg', 'ambiguous']),
    ('E', 'Triangle SSA', '1,5,30', ['no triangle']),
    ('E', 'Area (1/2)ab sinC', '4,5,30', ['area = 5']),
    ('E', 'Arc and sector (rad)', '5,1.2',
     ['arc = 6', 'sector area = 15', 'chord = 5.65']),
    ('E', 'Arc and sector (deg)', '6,60',
     ['arc = 2pi', 'sector area = 6pi', 'chord = 6']),
    ('E', 'Degrees to radians', '60', ['60 deg = pi/3 rad']),
    ('E', 'Radians to degrees', 'pi/3', ['rad = 60 deg']),
    ('E', 'Solve trig eqn (deg)', 'sin(x)-1/2,0,360',
     ['x = 30 deg', 'x = 150 deg']),
    ('E', 'Solve trig eqn (rad)', '2cos(x)+1,0,6.2831853',
     ['x = 2pi/3', 'x = 4pi/3']),
    ('E', 'Quad in sin x (deg)', '2,-1,-1,0,360',
     ['sin x = -1/2', 'x = 210 deg', 'x = 330 deg', 'sin x = 1']),
    ('E', 'Quad in cos x (deg)', '1,0,-1,0,360',
     ['cos x = -1', 'x = 180 deg', 'x = 0 deg']),
    ('E', 'Quad in tan x (deg)', '1,-1,0,0,360',
     ['tan x = 1', 'x = 45 deg', 'x = 225 deg']),
    ('E', 'Quad in sin x (deg)', '1,0,4,0,360', ['no solution']),
    ('E', 'R form a sin + b cos', '3,4',
     ['R = 5', 'al = 53.1 deg', 'max 5 at x = 36.9 deg']),
    ('E', 'Small angle (rad)', '0.1',
     ['sin: approx 0.1, exact 0.0998', 'cos: approx 0.995']),
    ('E', 'Compound angle (deg)', '45,30',
     ['sin(45+30) = (sqrt(2)+sqrt(6))/4', 'cos(45+30) = (sqrt(6)-sqrt(2))/4',
      'tan(45+30) = sqrt(3)+2']),
    ('E', 'Double angle (deg)', '30',
     ['sin 60 = sqrt(3)/2', 'cos 60 = 1/2', 'tan 60 = sqrt(3)']),
    ('E', 'sec cosec cot (deg)', '60',
     ['sec = 1/cos = 2', 'cosec = 1/sin = 2sqrt(3)/3']),
    ('E', 'sec cosec cot (deg)', '90', ['sec is undefined']),
    ('E', 'arcsin arccos arctan', '0.5',
     ['arcsin = 30 deg', 'arccos = 60 deg', 'arctan = 26.6 deg']),
    ('E', 'arcsin arccos arctan', '2', ['|v| > 1']),
    ('E', 'Identity check (rad)', 'sin(x)^2+cos(x)^2,1',
     ['holds at every x tested']),
    ('E', 'Identity check (rad)', 'sin(2x),2sin(x)', ['not an identity']),

    # ---- F  Exponentials and logarithms -----------------------------------
    ('F', 'Solve a^x = b', '2,8', ['x = 3']),
    ('F', 'Solve a^x = b', '2,5', ['x = 2.32']),
    ('F', 'Solve a^x = b', '2,-1', ['no real solution']),
    ('F', 'Solve log_a x = c', '3,4', ['x = 81']),
    ('F', 'log base a of x', '2,32', ['log_2 32 = 5']),
    ('F', 'Evaluate log expr', 'ln(e^3)', ['= 3']),
    # 7357/3 Jun18 Q7a: log_a y with y = 196 sqrt(a)
    ('F', 'Evaluate log expr', '2*logb(a,7)+logb(a,4)+1/2', ['= logb(a,196*sqrt(a))']),
    # 7357/1 Jun25 Q3, 7357/3 Jun25 Q4b
    ('F', 'Evaluate log expr', 'logb(3,2x)-logb(3,x)', ['= logb(3,2)']),
    ('F', 'Evaluate log expr', 'logb(a,sqrt(a))-logb(a,1/a^2)', ['= 5/2']),
    # 7357/2 Jun22 Q9: x = 8 y^(2/3)
    ('F', 'Evaluate log expr', 'logb(2,x^3)-logb(2,y^2)-9',
     ['= logb(2,x^3/y^2)-9', 'f = 0: x = 8*y^(2/3)']),
    # 7357/3 Nov20 Q8bii: n - (2n - 5) log3 2
    ('F', 'Evaluate log expr', 'logb(3,3^n/2^(2n-5))', ['= n-(2*n-5)*logb(3,2)']),
    # collecting logs: 7357/3 Jun25 Q8b ln(5/3), Jun24 Q11 256 ln 2
    ('F', 'Evaluate log expr', 'ln(5)-ln(2)/2-ln(9/2)/2', ['= ln(5/3)']),
    ('F', 'Evaluate log expr', '-256*ln(8)/3+623/9', ['= -256*ln(2)+623/9']),
    ('F', 'Evaluate log expr', 'ln(8)', ['= 3*ln(2)']),
    ('F', 'y = a x^n from 2 pts', '2,12,4,48', ['n = 2', 'a = 3', '3*x^2']),
    ('F', 'y = k b^x from 2 pts', '0,3,2,12', ['b = 2', 'k = 3', '3*2^x']),
    ('F', 'Log-log fit y=ax^n', '1,3,2,12,3,27,4,48',
     ['n = 2', 'a = 3', '4 points']),
    ('F', 'Log-lin fit y=kb^x', '0,3,1,6,2,12,3,24',
     ['b = 2', 'k = 3', '4 points']),
    ('F', 'N = A e^(kt) 2 pts', '0,100,10,50',
     ['A = 100', 'k = -0.0693', 'half-life = 10']),
    ('F', 'Evaluate A e^(kt)', '100,-0.0693147,10',
     ['N = 50', 'half-life = 10']),
    ('F', 'Compound interest', '1000,5,5',
     ['A = 1276.28', 'interest = 276.282', 'continuous = 1284.03']),

    # ---- more past-paper fixes ----
    # line-integer-form: 7357/1 Jun23 Q9aii perpendicular bisector
    ('C', 'Perpendicular bisect', '12,19,-6,15', ['9x + 2y - 61 = 0']),
    # circle-centre-line: Jun23 Q9bi centre on 2x - 5y = -30, r^2 = 170
    ('C', 'Circle, centre on line', '12,19,-6,15,2,-5,-30',
     ['centre (5, 8)', 'radius = sqrt(170)', '(x - 5)^2 + (y - 8)^2 = 170']),
    # circle-axes, circle-area: Jun23 Q9bii, 7357/3 Jun18 Q1 (9 pi)
    ('C', 'Circle centre+radius', '5,8,sqrt(170)',
     ['meets the x axis at x = 5-sqrt(106), sqrt(106)+5']),
    ('C', 'Circle centre+radius', '0,0,3', ['area = 9pi']),
    ('C', 'Circle from general', '-2,4,-4', ['meets the y axis at y = -2-2*sqrt(2)']),
    # circle-point: 7357/1 Jun18 Q7bii, sqrt(170) > 13
    ('C', 'Point and circle', '3,5,13,-8,-2',
     ['outside the circle', 'distance from centre = sqrt(170)']),
    # linquad-exact: 7357/3 Jun24 Q7b x = (2 - sqrt6)/2
    ('B', 'Line meets quadratic', '-1,1,-2,3,2', ['((2-sqrt(6))/2, sqrt(6)/2)']),
    # sigma-symbolic: 7357/3 Jun25 Q7 6a + 15, 7357/1 Nov20 Q10bi 5005b + 91c
    ('D', 'Sigma sum f(r) a..b', 'a*r+5,1,3', ['sum = 6*a+15']),
    ('D', 'Sigma sum f(r) a..b', 'b*r+c,10,100', ['sum = 5005*b+91*c']),
    # ap-first-last: 7357/1 Jun24 Q10a S300 = 3750
    ('D', 'AP sum, first and last', '300,-7,32', ['S(300) = 3750']),
    # gp-exact: 7357/1 Jun23 Q14bii 15(1 + sqrt2)/32
    ('D', 'Geometric a,r,n', 'sqrt(2)/4,sqrt(2)/2,8', ['S(8) = 15*sqrt(2)/32+15/32']),
    # binom-exact: 7357/1 Jun18 Q6a x^2 coefficient 3/256
    ('D', 'Binomial rational n', '4,1,-1/2', ['x^2: 3/256', 'x^3: -5/2048']),
    # recur-converge: 7357/1 Jun25 Q2; recur-n-limit: 7357/1 Nov20 Q7aii u50 = -1
    ('D', 'Recurrence u(n+1)', '-u/4,32,6', ['converges to L = 0']),
    ('D', 'Recurrence u(n+1)', '3-u^2,2,50', ['u(50) = -1', 'periodic, period 2']),
    # snap-zero: 7357/2 Jun18 Q3 sin(n pi/2)
    ('D', 'Terms of u(n)', 'sin(n*pi/2),1,8', ['u(2) = 0', 'periodic, period 4']),
    # trig-exact-other: 7357/1 Jun19 Q12b, Jun23 Q10bii
    ('E', 'Exact ratios from one', '2/3,?,?,2',
     ['cos x = -sqrt(5)/3', 'tan x = -2*sqrt(5)/5']),
    ('E', 'Exact ratios from one', '-3/7,?,?,3', ['cos x = -2*sqrt(10)/7']),
    ('E', 'Exact ratios from one', '?,?,-3/4,4', ['sin x = -3/5', 'cos x = 4/5']),
    # trig-undefined-root: 7357/1 Jun24 Q15bii, 360 is not a root
    ('E', 'Solve trig eqn (deg)', 'sin(2x)/sin(x)+cos(2x)/cos(x)-3,0,360',
     ['x = 104 deg', 'x = 256 deg', '2 root(s)']),
    # identity-domain: 7357/1 Jun22 Q15aiii on 0 < t < pi/2
    ('E', 'Identity check (rad)', 'sqrt(1/sin(x)^2-1)*sin(x),cos(x),0,pi/2',
     ['holds at every x tested']),
    ('E', 'Identity check (rad)', 'sqrt(1/sin(x)^2-1)*sin(x),cos(x)', ['not an identity']),
    # tri-radians: 7357/2 Jun25 Q9di 0.644 rad, 7357/3 Jun24 Q9d 1.25 rad
    ('C', 'Triangle 3 vertices', '6,10,12,-8,18,10', ['in rad: A = 1.25, B = 0.644']),
    ('E', 'Triangle SSS', '3,4,5', ['in rad: A = 0.644']),
    # arc-exact: 7357/3 Jun24 Q5 segment 27(pi - 3)
    ('E', 'Arc and sector (rad)', '18,pi/6', ['segment area = 27*pi-81']),
    # loglin-base: 7357/1 Nov21 Q9ci log10 gradient 0.021
    ('F', 'Log-lin fit y=kb^x', '0,75,5,97,10,123,15,160,20,204,25,260',
     ['log10: gradient = 0.0216']),
    # expmodel-predict: 7357/1 Jun18 Q10a m(4) = 245.9
    ('F', 'N = A e^(kt) 2 pts', '0,400,5.7,200,4', ['N(4) = 246']),
    ('F', 'N = A e^(kt) 2 pts', '0,400,5.7,200,?,100', ['N = 100 at t = 11.4']),
]

# Mark-scheme answers that need an engine fix first (tests.py skips these;
# run `python3 tests.py --pending` to see which now pass).
ENGINE_PENDING = [
    # [exactstr-silly] the root shows as sqrt(80331954)/2 until exactstr
    # stops matching large radicands; 7357/3 Jun22 Q7b d = 4481
    ('B', 'Solve f(x)=g(x)', '0.2*x^1.5,60000', ['(4480, 60000)']),
    # [exactstr-silly] 7357/2 Jun23 Q7bi S(120) = 6787.16, shown as
    # 31sqrt(47935) by fmt today
    ('D', 'Geometric a,r,n', '50.1,1.002,120', ['S(120) = 6790']),
    # [exactstr-silly] 7357/2 Jun24 Q7bi style: k from 10^3.9 shows as a
    # fake surd; MS k = 7940
    ('F', 'y = k b^x from 2 pts', '0,10^3.9,40,10^5.28', ['k = 7940']),
]
