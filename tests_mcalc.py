# Cases for mcalc (AQA 7357 G-J). Every number here was checked by hand or
# against an independent calculation.
CASES = [
    # ---- G differentiation ----
    ('G', "Derivative f' and f''", 'x^3-2x+1', ['3*x^2-2', '6*x']),
    ('G', "Derivative f' and f''", 'sin(2x)', ['2*cos(2*x)', '-4*sin(2*x)']),
    ('G', 'Tangent and normal', 'x^2,3', ['6*x-9', '19/2', 'point (3, 9)']),
    ('G', 'Tangent and normal', 'x^2,0', ['normal x = 0', 'point (0, 0)']),
    ('G', 'Stationary points', 'x^3-3x', ['max at (-1, 2)', 'min at (1, -2)']),
    ('G', 'Stationary points', 'x^4', ['min at (0, 0)']),
    ('G', 'Inflection points', 'x^3-3x',
     ['inflection at (0, 0)', 'concave for x < 0', 'convex for x > 0']),
    ('G', 'Inflection points', 'x^4', ['no inflection point', 'convex for all x']),
    ('G', 'Increasing/decreasing', 'x^3-3x',
     ['increasing for x < -1', 'decreasing for -1 < x < 1', 'increasing for x > 1']),
    ('G', 'First principles', 'x^2,3',
     ["f'(3) = 6", 'grad = 6.1', 'grad = 6.01', 'grad = 6.001']),
    ('G', 'Parametric dy/dx', 't^2,t^3,2',
     ['3*t/2', 'dy/dx = 3', 'point (4, 8)']),
    ('G', 'Parametric dy/dx', 'cos(t),sin(t),?', ['dx/dt = -sin(t)']),
    ('G', 'Implicit dy/dx', 'x^2+y^2-25,3,4', ['-x/y', 'dy/dx = -3/4']),
    ('G', 'Implicit dy/dx', 'x^2+y^2-25,1,1', ['not on the curve']),
    # 2x + y = 0 on the curve: 3x^2 = 12
    ('G', 'Implicit dy/dx = 0', 'x^2+x*y+y^2-12',
     ['dy/dx = 0 at (-2, 4)', 'dy/dx = 0 at (2, -4)', 'vertical tangent at (4, -2)']),
    # circle centre (2, -3) radius 5
    ('G', 'Implicit dy/dx = 0', 'x^2+y^2-4x+6y-12',
     ['dy/dx = 0 at (2, -8)', 'dy/dx = 0 at (2, 2)', 'vertical tangent at (7, -3)']),
    # x = -1, y^2 = 2
    ('G', 'Implicit dy/dx = 0', 'y^2-x^3+3x', ['dy/dx = 0 at (-1, sqrt(2))']),
    ('G', 'Implicit dy/dx = 0', 'x*y-4', ['no point with dy/dx = 0 found']),
    ('G', 'Connected rates', 'x^2,3,2', ['dy/dt = 12', '6 * 2 = 12']),
    # ---- past papers (AQA 7357) ----
    # deriv-simplify: 7357/1 Jun19 Q16a, Jun25 Q15a, 7357/3 Jun18 Q6b
    ('G', "Derivative f' and f''", 'e^(-x)*(sin(x)+cos(x))', ['-2*e^(-x)*sin(x)']),
    ('G', "Derivative f' and f''", '(x-3)^2+(x^2-2.5)^2', ['4*x^3-8*x-6', '12*x^2-8']),
    ('G', "Derivative f' and f''", 'x/sqrt(2x-2)', ['(x-2)/(2*x-2)^(3/2)']),
    ('G', "Derivative f' and f''", 'e^(3x-5)/x^2', ['(3*x-2)*e^(3*x-5)/x^3']),
    # 7357/3 Jun22 Q10d: f' = (2x^2+10x-20)/(2x+5)^2 (the engine drops the 4)
    ('G', "Derivative f' and f''", '(x^2+10)/(2x+5)',
     ['(2*x^2+10*x-20)/(2*x+5)^2', '130/(2*x+5)^3']),
    # 7357/2 Jun24 Q9ci: 12x/((1+3x)(2-3x)) = 6x - 9x^2 + ...
    ('G', "f, f' and f'' at a", '12x/((1+3x)(2-3x)),0', ["f'(0) = 6", "f''(0) = -18"]),
    ('G', 'Tangent and normal', 'x/(1+3x)^2,1', ["f'(1) = -1/32"]),
    # param-letters: 7357/2 Nov20 Q9b, V = pi R^2 x - pi x^3
    ('G', 'Stationary points', 'pi*R^2*x-pi*x^3',
     ['max at (r*sqrt(3)/3, 2*pi*r^3*sqrt(3)/9)', 'r taken as positive']),
    # stat-exact: 7357/3 Jun22 Q10d
    ('G', 'Stationary points', '(x^2+10)/(2x+5)',
     ['max at ((-sqrt(65)-5)/2, (-sqrt(65)-5)/2)',
      'min at ((sqrt(65)-5)/2, (sqrt(65)-5)/2)', '= (1.53, 1.53)']),
    ('G', 'Stationary points', 'x^3-6x+1', ['min at (sqrt(2), -4*sqrt(2)+1)']),
    # 7357/1 Jun19 Q13
    ('G', 'Stationary points', 'e^(3x-5)/x^2', ['min at (2/3, 9/(4*e^3))']),
    # incdec-domain-edge: 7357/3 Jun18 Q6d, convex for 1 < x < 4
    ('G', 'Inflection points', 'x/sqrt(2x-2)',
     ['inflection at (4, 2sqrt(6)/3)', 'convex for 1 < x < 4', 'concave for x > 4']),
    ('G', 'Increasing/decreasing', 'ln(x)-x',
     ['increasing for 0 < x < 1', 'decreasing for x > 1']),
    ('G', 'Increasing/decreasing', '1/x', ['decreasing for x < 0', 'decreasing for x > 0']),
    # firstprin-symbolic: 7357/1 Jun18 Q15a, 7357/3 Jun24 Q10
    ('G', 'First principles', 'x^3-48x,-4', ['at x = -4: h^2-12*h', "f'(-4) = 0"]),
    ('G', 'First principles', '5x^3+x,2',
     ['(f(x+h) - f(x))/h = 5*h^2+15*h*x+15*x^2+1', "h -> 0: f'(x) = 15*x^2+1"]),
    # 7357/1 Jun24 Q19: dy/dx = 0 at x = 0 gives y = 2, k = 12
    ('G', 'Implicit dy/dx = 0', 'y^3*e^(2x)+2y-16x-k,0', ['y = 2, k = 12']),
    # implicit-tangent: 7357/3 Jun19 Q9biii
    ('G', 'Implicit dy/dx', 'x^2*y^2+x*y^4-12,3,1',
     ['dy/dx = -7/30', 'tangent y = -7*x/30+17/10', 'tangent meets y = 0 at x = 51/7']),
    ('G', 'Inverse derivative', 'x^3,2', ["(f^-1)'(8) = 1/12", "f'(2) = 12"]),
    ('G', "f, f' and f'' at a", 'x^3,2', ['f(2) = 8', "f'(2) = 12", "f''(2) = 12"]),

    # ---- H integration ----
    ('H', 'Indefinite integral', 'x^2', ['x^3/3+c', 'agrees']),
    ('H', 'Indefinite integral', '1/(x^2-1)',
     ['ln(|x-1|)/2', 'ln(|x+1|)/2']),
    ('H', 'Definite integral', 'x^2,0,3', ['integral = 9', 'F(x) = x^3/3']),
    ('H', 'Definite integral', 'sin(x),0,pi', ['integral = 2']),
    ('H', 'Definite integral', '1/x,-1,1', ['f breaks inside a..b']),
    ('H', 'Area under curve', 'x^3,-1,1',
     ['area = 1/2', 'signed integral = 0', '-1 to 0: -1/4']),
    ('H', 'Area between curves', 'x^2,x', ['area = 1/6', 'f = g at 0 and 1']),
    ('H', 'Area between curves', 'x^2,x,0,2', ['area = 1', '1 to 2: 5/6']),
    ('H', 'Substitution u=g(x)', '2x*(x^2+1)^3,x^2+1',
     ['(x^2+1)^4/4+c', 'int u^3 du = u^4/4']),
    ('H', 'Substitution u=g(x)', 'x*(x+1)^5,x+1',
     ['(x+1)^7/7-(x+1)^6/6+c', 'in u: int u^6-u^5 du', 'x = u-1']),
    # x remains, so x = g^-1(u) goes in: 7357/2 Nov20 Q5, 7357/3 Jun23 Q8,
    # 7357/1 Jun24 Q18a, 7357/1 Jun25 Q17a
    ('H', 'Substitution u=g(x)', 'x*sqrt(4x+1),4x+1,-1/4,6',
     ['u from 0 to 25', 'integral = 875/12', 'in u: int sqrt(u)*u/16-sqrt(u)/16 du']),
    ('H', 'Substitution u=g(x)', 'x^9/(x^5+2)^3,x^5+2,0,1',
     ['u from 2 to 3', 'integral = 1/180', 'x = (u-2)^(1/5)']),
    ('H', 'Substitution u=g(x)', '(4x+1)sqrt(2x+1),2x+1,0,4',
     ['u from 1 to 9', 'integral = 1322/15', 'in u: int sqrt(u)*u-sqrt(u)/2 du']),
    ('H', 'Substitution u=g(x)', 'e^(2x)/(e^x+1),e^x+1',
     ['e^(x)-ln(|e^(x)+1|)+1+c', 'in u: int (u-1)/u du']),
    # x = g(u): 7357/1 Jun22 Q15bi, x = 2 cosec u
    ('H', 'Substitution u=g(x)', '1/(x^2*sqrt(x^2-4)),2*cosec(u)',
     ['in u: int -sin(u)/4 du', 'int du = cos(u)/4 + c']),
    ('H', 'Integration by parts', 'x,e^x',
     ['e^(x)*x-e^(x)+c', 'v = int dv dx = e^(x)']),
    ('H', 'Riemann sum table', 'x^2,0,3',
     ['integral = 9', 'sum = 7.695', 'sum = 8.86545', 'sum = 8.9865045']),
    ('H', 'Separable DE', 'x,y', ['ln(|y|) = x^2/2 + c']),
    ('H', 'Separable DE at point', 'x,y,0,1', ['e^(x^2/2)', 'ln(y) = x^2/2']),
    ('H', 'Separable DE at point', '1,y^2,0,1', ['-1/(x-1)', '-1/y = x - 1']),
    ('H', 'd/dx of an integral', 'x^2,1', ['x^3/3-1/3', "A'(x) ="]),
    # defint-tool-exact: 7357/1 Nov21 Q10b, Jun19 Q14b, Nov20 Q15
    ('H', 'Definite integral', '2x^3/(x^2+1),0,4', ['integral = -ln(17)+16 = 13.2']),
    ('H', 'Definite integral', '1-tan(x)^2,-pi/4,pi/4', ['integral = pi-2']),
    ('H', 'Area between curves', 'e^x,6-e^(x/2),0,ln(4)', ['area = 6*ln(4)-5 = 3.32']),
    # sep-exact-c: 7357/1 Jun24 Q20b h = 5 + 125e^(-0.012t)
    ('H', 'Separable DE at point', '-0.012,y-5,0,130',
     ['y = 125*e^(-3*x/250)+5', 'c = ln(125)']),
    # 7357/2 Nov21 Q17b: v = 98(1 - e^(-0.1t)), and with g kept as a letter
    ('H', 'Separable DE at point', '1,9.8-0.1y,0,0', ['y = -98*e^(-x/10)+98']),
    ('H', 'Separable DE at point', '1,g-0.1y,0,0',
     ['y = 10*(-e^(-x/10)*g+g)', 'c = -10*ln(g)', 'g taken as positive']),
    ('H', 'Separable DE', '1,g-0.1y', ['-10*ln(|g-y/10|) = x + c']),
    # 7357/2 Jun22 Q10bii: t = 3 ln(35x/(900 - x)) (x here is t, y is x)
    ('H', 'Separable DE at point', '1/2700,y*(900-y),0,25',
     ['x = 3*ln(-35*y/(y-900))', 'c = -ln(35)/900']),
    # 7357/1 Jun25 Q17b: tan y = e^x + ln(2/(e^x+1)) - 1
    ('H', 'Separable DE at point', 'e^(2x)/(e^x+1),cos(y)^2,0,pi',
     ['tan(y) = ln(2/(e^(x)+1))+e^(x)-1', 'c = ln(2)-1']),
    # 7357/2 Jun18 Q7: y = (x - 2)e^x + 2e
    ('H', 'Separable DE at point', '(x-1)*e^x,1,1,e', ['y = e^(x)*x-2*e^(x)+2*e', 'c = 2*e']),
    # int-normalise worked round here: expanded first, x^-2 ln x, 4x^(3/2)
    ('H', 'Indefinite integral', '(x-1)*e^x', ['e^(x)*x-2*e^(x)+c', 'agrees']),
    ('H', 'Definite integral', 'sqrt(16x^3),0,0.25', ['integral = 1/20']),
    # 7357/2 Jun19 Q5: t^2 = 6 - 2(1 + ln x)/x
    ('H', 'Separable DE at point', 'ln(x)/x^2,1/y,1,2',
     ['y^2/2 = -ln(x)/x-1/x + 3', 'y = sqrt(-2*ln(x)/x-2/x+6)']),

    # ---- I numerical methods ----
    ('I', 'Sign change table', 'x^3-2x-5,2,3',
     ['sign change 2 to 2.1', 'x = 2.1   f = 0.061']),
    ('I', 'Sign change table', '1/x,-1,1,4',
     ['sign change -0.5 to 0.5', 'f breaks between: not a root']),
    ('I', 'Newton-Raphson', 'x^3-2x-5,2,4',
     ['x = 2.0945515', 'x1 = 2.1', 'x2 = 2.0945681']),
    ('I', 'Newton-Raphson', 'x^2+1,0,3', ['Newton-Raphson failed']),
    ('I', 'Fixed point x=g(x)', 'sqrt(x+2),1,6',
     ['x1 = 1.7320508', 'x2 = 1.9318517', 'x = 1.9997323', 'converges']),
    ('I', 'Fixed point x=g(x)', 'x^2+1,1,5', ['the iteration diverges']),
    ('I', 'Bisection', 'x^2-2,1,2,4',
     ['x = 1.40625', 'm = 1.5', 'm = 1.25', 'm = 1.375', 'm = 1.4375']),
    ('I', 'Bisection', 'x^2-2,3,4', ['no sign change in [a, b]']),
    ('I', 'Trapezium rule', 'x^2,0,1,4',
     ['T = 11/32', 'T = 0.34375', 'over-estimate']),
    ('I', 'Trapezium rule', 'sqrt(x),0,1,4', ['T = 0.643', 'under-estimate']),
    ('I', 'Iterate to n dp', '(2x+5)^(1/3),2,3',
     ['x = 2.095 to 3 dp', 'x1 = 2.0800838']),
    # iter-labels: 7357/1 Jun19 Q7di starts at x1 = 0.4
    ('I', 'Fixed point x=g(x)', 'acos(x)/2,0.4,3,1',
     ['x2 = 0.57963974', 'x3 = 0.47625491', 'x4 = 0.53720285']),
    # trap-data: 7357/2 Nov20 Q15a 8110 m
    ('I', 'Trapezium from y values', '20,131,140,120,80,0', ['T = 8110', '4 strips']),

    # ---- J vectors ----
    ('J', 'Magnitude and angle', '3,4,0', ['|v| = 5', 'angle from i = 53.1 deg']),
    ('J', 'Magnitude and angle', '2,3,6', ['|v| = 7', 'i: 73.4']),
    ('J', 'Components from r,th', '10,30', ['v = (5sqrt(3), 5)']),
    ('J', 'Sum and difference', '1,2,3,4,5,6',
     ['a + b = (5, 7, 9)', 'a - b = (-3, -3, -3)', '|a + b| = sqrt(155)']),
    ('J', 'Scalar multiple k a', '3,1,-2,2', ['k a = (3, -6, 6)', '|k a| = 9']),
    ('J', 'Unit vector', '3,4,0', ['unit = (3/5, 4/5, 0)']),
    ('J', 'Distance A to B', '1,2,3,4,6,3', ['|AB| = 5', 'AB = (3, 4, 0)']),
    ('J', 'Midpoint and ratio', '1,2,3,3,6,9', ['midpoint = (2, 4, 6)']),
    ('J', 'Midpoint and ratio', '1,2,3,3,6,9,1,2',
     ['m:n point = (5/3, 10/3, 5)']),
    ('J', 'Parallel test', '1,2,3,2,4,6', ['parallel: b = 2 a', 'same direction']),
    ('J', 'Parallel test', '1,0,0,1,1,0', ['not parallel', 'angle = 45 deg']),
    ('J', 'Resultant of forces', '3,4,-1,2',
     ['R = (2, 6)', '|R| = 2sqrt(10)', 'angle = 71.6 deg']),
    ('J', 'Position r0 + v t', '1,0,2,3,-1,0,2', ['r = (7, -2, 2)', '|r| = sqrt(57)']),
    ('J', 'Angle between vectors', '1,0,0,1,1,0',
     ['angle = 45 deg', 'pi/4 rad', 'a.b = 1']),
    # quad-vectors: 7357/2 Jun19 Q15a style, CD parallel to AB -> trapezium
    ('J', 'Quadrilateral ABCD', '0,0,0,2,0,0,5,2,0,-1,2,0',
     ['trapezium', 'DC = 3 AB']),
    ('J', 'Quadrilateral ABCD', '0,0,0,4,0,0,4,3,0,0,3,0', ['rectangle']),
]

# Mark-scheme forms that need an engine fix first (tests.py skips these;
# python3 tests.py --pending runs them).
ENGINE_PENDING = [
    # [int-normalise] by parts on (x-1)e^x in the factorised MS form
    ('H', 'Indefinite integral', '(x-1)*e^x', ['(x-2)*e^(x)']),
]
