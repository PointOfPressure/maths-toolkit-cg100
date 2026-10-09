# Acceptance suite for the redesign (docs/redesign.md): every Algebra and Exp
# and logs question part with calculator steps in the past-paper audits
# (docs/pastpapers, AQA 7357 papers 1-3, pass 1 and pass 2), put through the
# new flow the way a student would: the topic, the rows as typed, the action
# picked from the tiles or More, the answers to its prompt, and what the
# mark scheme needs to see.
#
# A needle is text that must appear in the page (spaces and * ignored; a|b
# for either), or ~expr: some boxed answer equals expr (checked by value at
# sample points). Choice prompts take the option number.
#
# python3 tests_accept.py prints the numbers per topic and every failure;
# tests.py runs the cases not in PENDING.

C = [
    # ---- AQA 7357/1 June 2018
    ('1 jun18 2', 'exp', ['5^x'], 'Transform', ['5', '1', '0', '0'], ['~5^(x+1)']),
    ('1 jun18 4', 'exp', ['e^(x-4)'], 'Inverse', None, ['~ln(x)+4', 'x>0']),
    ('1 jun18 5b', 'alg', ['xy+5x-3y=27'], 'Rearrange for x', None, ['~(3y+27)/(y+5)']),
    ('1 jun18 9a', 'alg', ['(6a+15d)^2'], 'Expand', None, ['36a^2+180ad+225d^2']),
    ('1 jun18 9b', 'alg', ['a+5d=25', '4a+70d=4a^2+20ad+25d^2'], 'Solve', None,
     ['a=-55,d=16', 'a=-5,d=6']),
    ('1 jun18 10a', 'exp', ['m=Ae^(-kt)'], 'From two points', ['0', '400', '5.7', '200', '4'],
     ['a=400', 'k=0.122', 'm(4)=246']),
    ('1 jun18 10b', 'exp', ['400e^(-0.1216047t)=280'], 'Solve', None, ['t=2.93']),
    ('1 jun18 11b', 'alg', ['10+100(x/30)^3-50(x/30)^4=4.5*1.063^x'], 'Solve', None, ['x=49.0']),
    ('1 jun18 12a', 'alg', ['30x^3-7x^2-7x+2'], 'Factor theorem', ['-1/2'], ['(2x+1)isafactor']),
    ('1 jun18 12b', 'alg', ['30x^3-7x^2-7x+2'], 'Factorise', None, ['(2x+1)(3x-1)(5x-2)']),
    ('1 jun18 15a', 'alg', ['((-4+h)^3-48(-4+h)-128)/h'], 'Simplify', None, ['~h^2-12h']),
    # ---- 7357/1 June 2019
    ('1 jun19 1', 'exp', ['-4log(sqrt(x))'], 'Expand logs', None, ['-2logx']),
    ('1 jun19 1b', 'exp', ['-2log(1/x)'], 'Expand logs', None, ['2logx']),
    ('1 jun19 4', 'alg', ['5(-1)+4x=17'], 'Solve', None, ['x=11/2']),
    ('1 jun19 4b', 'alg', ['5*3+4x=17'], 'Solve', None, ['x=1/2']),
    ('1 jun19 5b', 'alg', ['4a+30d=65', '60a+1770d=315'], 'Solve', None, ['a=20', 'd=-1/2']),
    ('1 jun19 6a', 'alg', ['(x^2+1)/2'], 'Range on an interval', ['0', '?'], ['f(x)>=1/2']),
    ('1 jun19 6bi', 'alg', ['(x^2+1)/2'], 'Inverse', None, ['sqrt(2x-1)']),
    ('1 jun19 6d', 'alg', ['(x^2+1)/2', 'sqrt(2x-1)'], 'Solve f = g', None, ['x=1', '(1,1)']),
    ('1 jun19 12b', 'alg', ['4c^2-4c-3=0'], 'Solve', None, ['c=-1/2', 'c=3/2']),
    ('1 jun19 15aii', 'alg', ['4-(2t/3-2)^2=0'], 'Solve', None, ['t=0', 't=6']),
    ('1 jun19 16ciii', 'exp', ['((1+e^(-pi))/2)/(1-e^(-pi))'], 'Simplify', None,
     ['~(1+e^pi)/(2(e^pi-1))', '(e^pi+1)/(2(e^pi-1))|(1+e^pi)/(2(e^pi-1))']),
    # ---- 7357/1 June 2022
    ('1 jun22 3', 'exp', ['logb(4,x)'], 'Transform', ['2', '1', '0', '0'], ['~2logb(4,x)']),
    ('1 jun22 8bi', 'alg', ['5x+3(-17)=49'], 'Solve', None, ['x=20']),
    ('1 jun22 9a', 'alg', ['5x+1-(2x+5)=6x+7-(5x+1)'], 'Solve', None, ['x=5']),
    ('1 jun22 11bii', 'alg', ['x^2+bx+4'], 'Discriminant', None, ['equalroots:b=-4or4']),
    ('1 jun22 13a', 'alg', ['16^2=x*sqrt(16)'], 'Solve', None, ['x=64']),
    # ---- 7357/1 June 2023
    ('1 jun23 3', 'exp', ['ln(x)'], 'Transform', ['1', '1/2', '0', '0'], ['~ln(x/2)']),
    ('1 jun23 6', 'exp', ['2log(x)=log(4)+log(x+8)'], 'Solve', None, ['x=8', 'reject']),
    ('1 jun23 7a', 'alg', ['7/(3+5sqrt(x))-7/(5sqrt(x)-3)'], 'Simplify', None, ['~-42/(25x-9)']),
    ('1 jun23 11bi', 'alg', ['p(400p+70)+70=382'], 'Solve', None, ['p=4/5', 'p=-39/40']),
    ('1 jun23 11bii', 'alg', ['200p^2+35p-156=0'], 'Solve', None, ['p=4/5', 'p=-39/40']),
    ('1 jun23 11cii', 'alg', ['l=0.8l+70'], 'Solve', None, ['l=350']),
    ('1 jun23 16a', 'alg', ['1/(16-9x^2)'], 'Partial fractions', None,
     ['1/(8(4-3x))', '1/(8(3x+4))|1/(8(4+3x))']),
    ('1 jun23 16bi', 'alg', ['0.16-0.36(v/2)^2'], 'Expand', None, ['0.09v^2|9v^2/100']),
    # ---- 7357/1 June 2024
    ('1 jun24 1', 'alg', ['(4x^3-5x^2+3x-2)(x^5+4x+1)'], 'Expand', None, ['-5x-2']),
    ('1 jun24 2', 'exp', ['e^x+1'], 'Inverse', None, ['~ln(x-1)']),
    ('1 jun24 3', 'alg', ['12x^2+3x+7'], 'Divide', ['3x-5'], ['quotient4x+23/3']),
    ('1 jun24 7', 'alg', ['(3+sqrt(8x))/(1+sqrt(2x))'], 'Rationalise', None,
     ['~(4x-3+sqrt(2x))/(2x-1)', '/(2x-1)']),
    ('1 jun24 8a', 'alg', ['(2+kx)^5'], 'Expand', None, ['32+80kx+80k^2x^2']),
    ('1 jun24 8b', 'alg', ['80k=4*80k^2'], 'Solve', None, ['k=0', 'k=1/4']),
    ('1 jun24 10b', 'alg', ['9/2(a+6a)=1260'], 'Solve', None, ['a=40']),
    ('1 jun24 13a', 'alg', ['4x^3+8x^2+11x+4'], 'Factor theorem', ['-1/2'], ['f(-1/2)=0']),
    ('1 jun24 13b', 'alg', ['4x^3+8x^2+11x+4'], 'Divide', ['2x+1'], ['quotient2x^2+3x+4']),
    ('1 jun24 17a', 'alg', ['abs(x)+1'], 'Range', None, ['f(x)>=1']),
    ('1 jun24 17b', 'alg', ['ln(x)'], 'Domain', None, ['x>0']),
    ('1 jun24 17ci', 'alg', ['f(x)=ln(x)', 'g(x)=abs(x)+1'], 'fg and gf', None, ['fg(x)=ln(|x|+1)']),
    ('1 jun24 17cii', 'alg', ['ln(abs(x)+1)'], 'Inverse', None, ['many-to-one']),
    ('1 jun24 20c', 'exp', ['e^(-0.012t)=60/125'], 'Solve', None, ['t=61.2']),
    # ---- 7357/1 June 2025
    ('1 jun25 3', 'exp', ['logb(3,2x)-logb(3,x)'], 'Combine logs', None, ['log_32']),
    ('1 jun25 10c', 'exp', ['21-39.5e^(-0.184t)=4'], 'Solve', None, ['t=4.58']),
    ('1 jun25 12a', 'alg', ['x^2+5'], 'Range', None, ['f(x)>=5']),
    ('1 jun25 12b', 'alg', ['x^2+5'], 'Inverse', None, ['many-to-one']),
    ('1 jun25 12di', 'alg', ['f(x)=sqrt(x)', 'g(x)=x^2+5'], 'fg and gf', None, ['fg(x)=sqrt(x^2+5)']),
    ('1 jun25 12dii', 'alg', ['sqrt(x^2+5)'], 'Range', None, ['f(x)>=sqrt(5)']),
    ('1 jun25 15b', 'alg', ['x-(2x^3-4x-3)/(6x^2-4)'], 'Simplify', None, ['~(4x^3+3)/(6x^2-4)']),
    # ---- 7357/1 November 2020
    ('1 nov20 3', 'alg', ['2*2+2x=6'], 'Solve', None, ['x=1']),
    ('1 nov20 4b', 'alg', ['4-abs(2x-6)>2'], 'Solve inequality', None, ['2<x<4']),
    ('1 nov20 8a', 'alg', ['3.87sin(2pi(x+101.75)/365)+11.7'], 'Range on an interval', ['0', '365'],
     ['7.83']),
    ('1 nov20 9b', 'alg', ['(2x^2+x)/((x+1)(x+2)^2)'], 'Partial fractions', None,
     ['1/(x+1)', '1/(x+2)', '6/(x+2)^2']),
    ('1 nov20 10bii', 'alg', ['55b+c=85', '5b-3c=0'], 'Solve', None, ['b=3/2', 'c=5/2']),
    ('1 nov20 13ai', 'alg', ['(2x+3)/(x-2)'], 'Inverse', None, ['~(2x+3)/(x-2)']),
    ('1 nov20 13aii', 'alg', ['(2x+3)/(x-2)', '(2x+3)/(x-2)'], 'fg and gf', None, ['fg(x)=x']),
    ('1 nov20 13bi', 'alg', ['(2x^2-5x)/2'], 'Range on an interval', ['0', '4'], ['-25/16<=f(x)<=6']),
    ('1 nov20 13bii', 'alg', ['(2x^2-5x)/2=0'], 'Solve', None, ['x=0', 'x=5/2']),
    ('1 nov20 13c', 'alg', ['f(x)=(2x+3)/(x-2)', 'g(x)=(2x^2-5x)/2'], 'fg and gf', None,
     ['~gf=(48+29x-2x^2)/(2(x-2)^2)']),
    ('1 nov20 13d', 'alg', ['2x^2-5x-4=0'], 'Solve', None, ['(5+sqrt(57))/4', '(5-sqrt(57))/4']),
    ('1 nov20 15', 'exp', ['e^x=6-e^(x/2)'], 'Solve', None, ['~2ln(2)']),
    # ---- 7357/1 November 2021
    ('1 nov21 1', 'alg', ['(x-3)(2x+7)>0'], 'Solve inequality', None, ['x<-7/2orx>3']),
    ('1 nov21 6b', 'alg', ['n/2(14-0.5(n-1))=n/2(-36+0.75(n-1))'], 'Solve', None, ['n=0', 'n=41']),
    ('1 nov21 9e', 'exp', ['75*10^(0.02t)=8000'], 'Solve', None, ['t=101']),
    ('1 nov21 12a', 'alg', ['x^2=2x+8'], 'Solve', None, ['x=4', 'x=-2']),
    ('1 nov21 13a', 'alg', ['125x^3+150x^2+55x+6'], 'Factor theorem', ['-1/5'], ['(5x+1)isafactor']),
    ('1 nov21 13b', 'alg', ['125x^3+150x^2+55x+6'], 'Factorise', None, ['(5x+1)(5x+2)(5x+3)']),
    ('1 nov21 14a', 'alg', ['4t^2-t^3=0'], 'Solve', None, ['t=0', 't=4']),
    ('1 nov21 14bii', 'alg', ['(4t^2-t^3)(2t+1)'], 'Expand', None, ['-2t^4+7t^3+4t^2']),
    # ---- 7357/2 June 2018
    ('2 jun18 4b', 'alg', ['x^2-6x+k'], 'Discriminant', None, ['twodistinctrealroots:k<9']),
    ('2 jun18 8bi', 'alg', ['1/(2sqrt(3)+4)'], 'Rationalise', None, ['~(2-sqrt(3))/2']),
    ('2 jun18 8bii', 'alg', ['1/(4-2sqrt(3))'], 'Rationalise', None, ['~(2+sqrt(3))/2']),
    ('2 jun18 9ci', 'alg', ['168(8-t)=sqrt(4032t(16-t))'], 'Solve', None, ['5.17']),
    ('2 jun18 9ci b', 'alg', ['t^2-16t+56=0'], 'Solve', None, ['8-2sqrt(2)|8-sqrt(8)']),
    ('2 jun18 15a', 'alg', ['0.0115t^4=100'], 'Solve', None, ['t=9.66']),
    ('2 jun18 15b', 'alg', ['0.0012t^5=100'], 'Solve', None, ['t=9.64']),
    # ---- 7357/2 June 2019
    ('2 jun19 2', 'alg', ['sqrt(a^(2/3)*a^(2/5))'], 'Simplify', None, ['a^(8/15)']),
    ('2 jun19 3', 'alg', ['x^2'], 'Inverse', None, ['many-to-one']),
    ('2 jun19 6', 'alg', ['a^2+b^2=16', 'sqrt(3)/2*a+b/2=2sqrt(3)'], 'Solve', None,
     ['a=2,b=2sqrt(3)', 'a=4,b=0']),
    ('2 jun19 7bi', 'alg', ['3x^2+6px'], 'Factorise', None, ['3x(x+2p)']),
    ('2 jun19 8b', 'exp', ['y=kb^x'], 'From two points', ['0', '10^3.9', '40', '10^5.28', ''],
     ['k=7940', 'b=1.08']),
    ('2 jun19 8c', 'exp', ['7940*1.08^t=500000'], 'Solve', None, ['t=53.8']),
    # ---- 7357/2 June 2022
    ('2 jun22 5b', 'alg', ['(2+5x)^4-(2-5x)^4'], 'Expand', None, ['320x', '2000x^3']),
    ('2 jun22 7a', 'alg', ['15-x^2=0'], 'Solve', None, ['x=sqrt(15)']),
    ('2 jun22 8b', 'alg', ['1/x^2'], 'Transform', ['1', '1/3', '0', '0'], ['~9/x^2']),
    ('2 jun22 9', 'exp', ['logb(2,x^3)-logb(2,y^2)=9'], 'Rearrange for x', None, ['x=8y^(2/3)']),
    ('2 jun22 10ai', 'exp', ['25*1.32^5'], 'Evaluate', None, ['100.18']),
    ('2 jun22 10bi', 'alg', ['2700/(x(900-x))'], 'Partial fractions', None, ['3/x', '3/(900-x)']),
    ('2 jun22 15', 'alg', ['2t+7=2(10-t)+20'], 'Solve', None, ['t=33/4']),
    ('2 jun22 16a', 'alg', ['9/3=(k+1)/(-4)'], 'Solve', None, ['k=-13']),
    # ---- 7357/2 June 2023
    ('2 jun23 5bi', 'alg', ['25(10+4(n-1))=3000'], 'Solve', None, ['n=57/2']),
    ('2 jun23 7a', 'alg', ['f(x)=1/x', 'g(x)=sqrt(10-2x)'], 'fg and gf', None, ['fg(x)=1/sqrt(10-2x)']),
    ('2 jun23 7b', 'alg', ['1/sqrt(10-2x)'], 'Domain', None, ['x<5']),
    ('2 jun23 7c', 'alg', ['1/sqrt(10-2x)'], 'Inverse', None, ['~5-1/(2x^2)']),
    ('2 jun23 8b', 'alg', ['2/sin(x)^2'], 'Range on an interval', ['0', 'pi'], ['f(x)>=2']),
    ('2 jun23 10a', 'alg', ['(a-b)^2'], 'Expand', None, ['a^2-2ab+b^2']),
    ('2 jun23 16', 'alg', ['(5k-5)/12=(1.6+k)/3.2'], 'Solve', None, ['k=44/5|k=8.8']),
    ('2 jun23 20', 'alg', ['0.5a(2.592-0.2)^2=18.144'], 'Solve', None, ['a=6.34']),
    # ---- 7357/2 June 2024
    ('2 jun24 3', 'alg', ['(1-x)(x-4)<0'], 'Solve inequality', None, ['x<1orx>4']),
    ('2 jun24 4', 'exp', ['5^(x-2)=7^1570'], 'Solve', None, ['x=1900']),
    ('2 jun24 8aii', 'exp', ['a+log(3)b=6.4', 'a+log(24)b=12'], 'Solve', None, ['a=3.44', 'b=6.2']),
    ('2 jun24 9b', 'alg', ['36x/((1+3x)(2-3x))'], 'Partial fractions', None, ['8/(2-3x)', '4/(1+3x)']),
    ('2 jun24 14b', 'alg', ['-2t^2+6t>0'], 'Solve inequality', None, ['0<t<3']),
    ('2 jun24 15', 'alg', ['a-12b=-4', '-3a+b=-23'], 'Solve', None, ['a=8', 'b=1']),
    ('2 jun24 18a', 'exp', ['-0.04q*e^(-0.6)=-1.8'], 'Solve', None, ['q=82.0|q=82']),
    # ---- 7357/2 June 2025
    ('2 jun25 3', 'alg', ['(x+2)(x-7)>0'], 'Solve inequality', None, ['x<-2orx>7']),
    ('2 jun25 4', 'exp', ['5^(x-1)=20'], 'Solve', None, ['~1+log(20)/log(5)', 'log_5']),
    ('2 jun25 7c', 'alg', ['5p-q=30', '10p-q=75'], 'Solve', None, ['p=9', 'q=15']),
    ('2 jun25 9c', 'alg', ['(a-12)^2+64=100'], 'Solve', None, ['a=6', 'a=18']),
    ('2 jun25 10b', 'exp', ['1+k*ln(x)=0'], 'Rearrange for x', None, ['x=e^(-1/k)']),
    ('2 jun25 19b', 'alg', ['24/12=(8+q)/18'], 'Solve', None, ['q=28']),
    # ---- 7357/2 November 2020
    ('2 nov20 3', 'alg', ['(2x-3/x)^8'], 'Expand', None, ['-48384x^2']),
    ('2 nov20 8biii', 'alg', ['(2/a)/(1-1/a^2)'], 'Simplify', None, ['~2a/(a^2-1)']),
    # ---- 7357/2 November 2021
    ('2 nov21 4b', 'alg', ['abs(3x-6)=abs(2x)'], 'Solve', None, ['x=6/5', 'x=6']),
    ('2 nov21 5', 'alg', ['5(x-3)/((2x-11)(4-3x))'], 'Partial fractions', None, ['1/(4-3x)', '1/(2x-11)']),
    ('2 nov21 6', 'exp', ['5^x=3^(x+4)'], 'Solve', None, ['~ln(81)/(ln(5)-ln(3))', 'x=8.60|x=8.6']),
    ('2 nov21 7b', 'alg', ['sqrt(25+p)=4'], 'Solve', None, ['p=-9']),
    ('2 nov21 7b b', 'alg', ['sqrt(25+p)=5'], 'Solve', None, ['p=0']),
    ('2 nov21 9c', 'alg', ['1+c-2c^2'], 'Complete square', None, ['9/8', '(c-1/4)^2']),
    ('2 nov21 10a', 'alg', ['sqrt(x)/(x-3)'], 'Domain', None, ['x>=0,x!=3']),
    # ---- 7357/3 June 2018
    ('3 jun18 6a', 'alg', ['x/sqrt(2x-2)'], 'Domain', None, ['x>1']),
    ('3 jun18 7a', 'exp', ['logb(a,y)=2logb(a,7)+logb(a,4)+1/2'], 'Rearrange for y', None,
     ['y=196sqrt(a)']),
    ('3 jun18 11', 'alg', ['k+2k+4k+2k+k=1'], 'Solve', None, ['k=1/10']),
    # ---- 7357/3 June 2019
    ('3 jun19 1', 'alg', ['asin(x)'], 'Domain', None, ['-1<=x<=1']),
    ('3 jun19 7a', 'alg', ['(4x+3)/(x-1)^2'], 'Partial fractions', None, ['4/(x-1)', '7/(x-1)^2']),
    ('3 jun19 8a', 'exp', ['5(4+x)=75', '5(4+x*e^(-2y))=68'], 'Solve', None, ['x=11', '0.068']),
    ('3 jun19 8bii', 'exp', ['5(4+11e^(-0.068066t))=21'], 'Solve', None, ['t=58.9']),
    ('3 jun19 9biii', 'alg', ['x^2+x-12=0'], 'Solve', None, ['x=3', 'x=-4']),
    # ---- 7357/3 June 2022
    ('3 jun22 2', 'alg', ['(7-2x)-(x^2-7x+7)'], 'Expand', None, ['5x-x^2|-x^2+5x']),
    ('3 jun22 3', 'alg', ['2x+1'], 'Inverse', None, ['~(x-1)/2']),
    ('3 jun22 3b', 'alg', ['2x+1', '(x-1)/2'], 'Solve f = g', None, ['x=-1']),
    ('3 jun22 6bii', 'alg', ['9-1.4t=0'], 'Solve', None, ['t=6.43|t=45/7']),
    ('3 jun22 7aii', 'exp', ['y=k*x^n'], 'From two points', ['10^1.76', '10^1.94', '10^3.46', '10^4.49', ''],
     ['k=0.2', 'n=1.5']),
    ('3 jun22 7b', 'exp', ['0.2d^1.5=60000'], 'Solve', None, ['d=4480']),
    ('3 jun22 10a', 'alg', ['(x^2+10)/(2x+5)'], 'Domain', None, ['x!=-5/2']),
    ('3 jun22 10b', 'alg', ['(x^2+10)/(2x+5)'], 'Inverse', None, ['many-to-one']),
    ('3 jun22 10ci', 'alg', ['(x^2+10)/(2x+5)=x'], 'Solve', None, ['~(-5+sqrt(65))/2', '~(-5-sqrt(65))/2']),
    ('3 jun22 10e', 'alg', ['(x^2+10)/(2x+5)'], 'Range', None, ['sqrt(65)', 'or']),
    ('3 jun22 14c', 'alg', ['10p(1-p)=2.25'], 'Solve', None, ['p=0.342', 'p=0.658']),
    # ---- 7357/3 June 2023
    ('3 jun23 4', 'alg', ['(5-sqrt(x))/x^2'], 'Expand', None, ['~5x^(-2)-x^(-3/2)', '3/2']),
    ('3 jun23 5', 'exp', ['3e^(2x)=10'], 'Solve', None, ['~ln(10/3)/2']),
    ('3 jun23 9bii', 'alg', ['1-2/t^2=0'], 'Solve', None, ['t=sqrt(2)']),
    ('3 jun23 15b', 'alg', ['0.76+3k=1'], 'Solve', None, ['k=0.08|k=2/25']),
    # ---- 7357/3 June 2024
    ('3 jun24 2', 'alg', ['4x^2+kx+9'], 'Discriminant', None, ['equalroots:k=-12or12']),
    ('3 jun24 7b', 'alg', ['y=-x+1', 'y=-2x^2+3x+2'], 'Solve', None, ['sqrt(6)/2']),
    ('3 jun24 8ci', 'exp', ['20(11-10e^(-k))=86'], 'Solve', None, ['k=0.401|k=0.4']),
    ('3 jun24 8cii', 'exp', ['20(11-10e^(-0.4005t))=219'], 'Solve', None, ['t=13.2']),
    ('3 jun24 9c', 'alg', ['16+(x-6)^2=25'], 'Solve', None, ['x=3', 'x=9']),
    # ---- 7357/3 June 2025
    ('3 jun25 4b', 'exp', ['logb(a,sqrt(a))-logb(a,1/a^2)'], 'Combine logs', None, ['5/2']),
    ('3 jun25 8a', 'alg', ['x/(2x^2+3x+1)'], 'Partial fractions', None, ['1/(x+1)', '1/(2x+1)']),
    ('3 jun25 9a', 'alg', ['1/x'], 'Transform', ['3', '1', '-4', '0'], ['~3/(x-4)']),
    ('3 jun25 9b', 'alg', ['3/(x-4)'], 'Domain', None, ['x!=4']),
    # ---- 7357/3 November 2020
    ('3 nov20 4a', 'alg', ['4x^3-15x^2-48x-36'], 'Factor theorem', ['6'], ['f(6)=0']),
    ('3 nov20 4bi', 'alg', ['4x^3-15x^2-48x-36'], 'Divide', ['x-6'], ['quotient4x^2+9x+6']),
    ('3 nov20 4bii', 'alg', ['4x^3-15x^2-48x-36=0'], 'Solve', None, ['x=6']),
    ('3 nov20 5a', 'exp', ['m=a*e^(-kt)'], 'From two points', ['0', '1', '15.9', '0.5', ''], ['k=0.0436']),
    ('3 nov20 5a b', 'exp', ['e^(-0.0435935t)=0.1'], 'Solve', None, ['t=52.8']),
    ('3 nov20 5b', 'exp', ['100e^(-0.0435935*168)'], 'Evaluate', None, ['0.0659|0.066']),
    ('3 nov20 7bi', 'alg', ['2*(n!/(24*(n-4)!))/(51*(n!/(2*(n-2)!)))'], 'Simplify', None,
     ['~(n-2)(n-3)/306']),
    ('3 nov20 7bii', 'alg', ['n^2-5n-300=0'], 'Solve', None, ['n=-15', 'n=20']),
    ('3 nov20 8a', 'alg', ['a/(1-r)=96', 'a*r=18'], 'Solve', None, ['a=72,r=1/4', 'a=24,r=3/4']),
    ('3 nov20 8bi', 'exp', ['24*(3/4)^(n-1)'], 'Simplify', None, ['3^n/2^(2n-5)']),
    ('3 nov20 8bii', 'exp', ['logb(3,3^n/2^(2n-5))'], 'Expand logs', None, ['~n-(2n-5)logb(3,2)']),
    # ---- 7357/3 November 2021
    ('3 nov21 2', 'alg', ['(x+3)(6-2x)/((x-3)(3+x))'], 'Simplify', None, ['=-2']),
    ('3 nov21 4b', 'alg', ['(2x-3/x)^10'], 'Expand', None, ['-1959552']),
    ('3 nov21 6', 'alg', ['(10+5x-2sqrt(x)-x^(3/2))/(5-sqrt(x))'], 'Simplify', None, ['x+2']),
    ('3 nov21 14a', 'alg', ['p+2p-0.1=0.8'], 'Solve', None, ['p=0.3|p=3/10']),
    ('3 nov21 16b', 'alg', ['16c+k=1', 'c+k=5/8'], 'Solve', None, ['c=1/40', 'k=3/5']),
]

# Coord geometry: points as ('x', 'y') in the boxes, rows as typed
C += [
    ('1 jun18 5b g', 'geo', ['x=4*2^(-t)+3', 'y=3*2^t-5'], 'Cartesian equation', None,
     ['~12/(y+5)+3|~12/(x-3)-5']),
    ('1 jun18 7a', 'geo', [('8', '17'), ('15', '10'), ('-2', '-7')], 'Triangle ABC', None,
     ['rightangleatb', 'ab^2=98']),
    ('1 jun18 7bii', 'geo', [('8', '17'), ('15', '10'), ('-2', '-7')], 'Circle ABC', None,
     ['centre(3,5)', 'radius13']),
    ('1 jun18 7bii b', 'geo', [('-8', '-2'), 'x^2+y^2-6x-10y=135'], 'A inside or outside?', None,
     ['aisoutside', 'sqrt(170)']),
    ('1 jun19 4 g', 'geo', [('-1', '11/2'), ('3', '1/2')], 'Perp bisector', None,
     ['~4/5x+11/5', '4x-5y+11=0', 'midpoint(1,3)']),
    ('1 jun22 1 g', 'geo', ['x=cos(t)', 'y=sin(t)'], 'Cartesian equation', None, ['x^2+y^2=1']),
    ('1 jun22 8ai', 'geo', [('0', '5'), '5x+3y=83'], 'Foot of perpendicular', None,
     ['(10,11)', 'distance=2sqrt(34)']),
    ('1 jun23 9ai', 'geo', [('-6', '15'), ('12', '19')], 'Midpoint', None, ['midpoint(3,17)']),
    ('1 jun23 9bi', 'geo', [('-6', '15'), ('12', '19'), '2x-5y=-30'], 'Circle, centre on line', None,
     ['centre(5,8)', '(x-5)^2+(y-8)^2=170']),
    ('1 jun25 13c', 'geo', ['x=4(4t+1)^2', 'y=e^(-4t)'], 'Cartesian equation', None,
     ['~4(1-ln(y))^2|~e^(1-sqrt(x)/2)']),
    ('1 nov21 5a', 'geo', [('15', '2'), 'y=4/3x'], 'Perpendicular thru A', None, ['3x+4y-53=0']),
    ('1 nov21 5b', 'geo', [('15', '2'), '-4x+3y=21'], 'Foot of perpendicular', None, ['(3,11)', 'distance=15']),
    ('1 nov21 12b', 'geo', [('4', '0'), 'y=-3/2x'], 'Perpendicular thru A', None, ['2x-3y-8=0']),
    ('1 nov21 14bi', 'geo', ['x=t^2+t', 'y=4t^2-t^3'], 'Point at t', ['4'], ['x=20,y=0']),
    ('2 jun25 9di', 'geo', [('6', '10'), ('12', '-8'), ('18', '10')], 'Triangle ABC', None, ['angleb=0.644']),
    ('2 nov20 6a', 'geo', [('7', '9'), '12x+5y=298'], 'Foot of perpendicular', None, ['(19,14)', 'distance=13']),
    ('2 nov20 8a', 'geo', ['x=t^2', 'y=2t'], 'Cartesian equation', None, ['~y^2/4']),
    ('2 nov21 7ai', 'geo', ['x^2+y^2-6x-8y=p'], 'Centre and radius', None,
     ['centre(3,4)', 'p+25', 'p>-25']),
    ('3 jun18 3', 'geo', [('0', '0'), 'y=-2/3x'], 'Perpendicular thru A', None, ['3x-2y=0']),
    ('3 jun19 5', 'geo', ['x^2+y^2-6x-8y-264=0'], 'Centre and radius', None, ['radius=17']),
    ('3 jun22 6a', 'geo', ['x=-2t^2', 'y=9t-0.7t^2'], 'Point at t', ['9.5'], ['x=-180.5']),
    ('3 jun22 7ai g', 'geo', [('1.76', '1.94'), ('3.46', '4.49')], 'Line AB', None, ['~1.5x-0.7']),
    ('3 jun23 9a', 'geo', ['x=t-1/t+4.8', 'y=t+2/t'], 'Point at t', ['0.2'], ['x=0,y=10.2|x=0,y=51/5']),
    ('3 jun24 9a', 'geo', ['x^2+y^2+8x-12y+27=0'], 'Centre and radius', None,
     ['(x+4)^2+(y-6)^2=25', 'centre(-4,6)', 'radius=5']),
    ('3 jun24 9d', 'geo', [('-4', '6'), ('0', '9'), ('9', '-3')], 'Triangle ABC', None,
     ['anglea=1.25', 'rightangleatb']),
]

# Calculus
C += [
    ('1 jun18 1', 'calc', ['1/x^2'], 'Differentiate', None, ['~-2/x^3']),
    ('1 jun18 5a', 'calc', ['x=4*2^(-t)+3', 'y=3*2^t-5'], 'dy/dx (parametric)', None, ['~-3*2^(2t)/4']),
    ('1 jun18 6c', 'calc', ['1/2+x^3/16+3x^6/256'], 'Definite integral', ['0', '1'], ['927/1792']),
    ('1 jun18 13', 'calc', ['4x*sqrt(16-x^2)'], 'Stationary points', None, ['x=2sqrt(2),y=32', 'maximum']),
    ('1 jun18 15a', 'calc', ['x^3-48x'], 'First principles', None, ['h^2+3xh+3x^2-48', '~3x^2-48']),
    ('1 jun19 2', 'calc', ['e^(kx)'], 'Differentiate', None, ['~k*e^(kx)']),
    ('1 jun19 10', 'calc', ['4/3*pi*r^3'], 'Differentiate', None, ['~4pi*r^2']),
    ('1 jun19 13', 'calc', ['e^(3x-5)/x^2'], 'Stationary points', None, ['x=2/3', 'minimum']),
    ('1 jun19 14b', 'calc', ['2x^3/(x^2+1)'], 'Definite integral', ['0', '4'], ['~16-ln(17)']),
    ('1 jun19 15b', 'calc', ['4-(2x/3-2)^2'], 'Stationary points', None, ['x=3,y=4', 'maximum']),
    ('1 jun19 16a', 'calc', ['e^(-x)*(sin(x)+cos(x))'], 'Differentiate', None, ['~-2e^(-x)*sin(x)']),
    ('1 jun19 16b', 'calc', ['e^(-x)*sin(x)'], 'Integrate', None, ['~-(cos(x)+sin(x))*e^(-x)/2']),
    ('1 jun19 16ci', 'calc', ['e^(-x)*sin(x)'], 'Definite integral', ['0', 'pi'], ['~(1+e^(-pi))/2']),
    ('1 jun22 5', 'calc', ['(x-2)^4'], 'Tangent at x =', ['0'], ['~-32x+16']),
    ('1 jun22 10ciii', 'calc', ['x-sin(2x)'], 'Tangent at x =', ['pi/6'], ['dy/dx=0']),
    ('1 jun22 14b', 'calc', ['(2x-8)ln(x)'], 'Definite integral', ['1', '4'], ['~33/2-32ln(2)']),
    ('1 jun22 15aii', 'calc', ['1/sin(x)'], 'Differentiate', None, ['~-cos(x)/sin(x)^2']),
    ('1 jun23 2', 'calc', ['2x^3'], 'Differentiate', None, ['~6x^2']),
    ('1 jun23 8', 'calc', ['x*sin(4x)'], 'Definite integral', ['0', 'pi/2'], ['~-pi/8']),
    ('1 jun23 14ai', 'calc', ['2^x'], 'Differentiate', None, ['~2^x*ln(2)']),
    ('1 jun23 14aii', 'calc', ['2^x'], 'Integrate', None, ['~2^x/ln(2)']),
    ('1 jun23 14biii', 'calc', ['2^x'], 'Definite integral', ['-4', '0'], ['~15/(16ln(2))']),
    ('1 jun24 6', 'calc', ['(x^3+5x)^7'], 'Differentiate', None, ['~7(3x^2+5)(x^3+5x)^6', 'chainrule']),
    ('1 jun24 18b', 'calc', ['(4x+1)sqrt(2x+1)'], 'Definite integral', ['0', '4'], ['1322/15']),
    ('1 jun24 20b', 'calc', ['dy/dx=-0.012(y-5)'], 'Solve with a point', ['0', '130'],
     ['~125e^(-0.012x)+5']),
    ('1 jun25 1', 'calc', ['3e^x'], 'Differentiate', None, ['~3e^x']),
    ('1 jun25 5', 'calc', ['4x-3+x^(-1/2)'], 'Integrate', None, ['~2x^2-3x+2sqrt(x)']),
    ('1 jun25 9bii', 'calc', ['x-x^2'], 'Stationary points', None, ['x=1/2,y=1/4', 'maximum']),
    ('1 jun25 13a', 'calc', ['x=4(4t+1)^2', 'y=e^(-4t)'], 'dy/dx (parametric)', None,
     ['~-e^(-4t)/(8(4t+1))']),
    ('1 jun25 14', 'calc', ['4x*sin(2x)'], 'Area under curve', ['0', 'pi'], ['~4pi']),
    ('1 jun25 15a', 'calc', ['(x-3)^2+(x^2-2.5)^2'], 'Differentiate', None, ['~4x^3-8x-6']),
    ('1 nov20 12bi', 'calc', ['x^3*sin(y)+cos(y)=2x'], 'dy/dx (implicit)', None,
     ['~(2-3x^2*sin(y))/(x^3*cos(y)-sin(y))']),
    ('1 nov20 12bii', 'calc', ['x^3*sin(y)+cos(y)=2x'], 'Gradient at a point', ['sqrt(3)', 'pi/6'],
     ['~-5/8']),
    ('1 nov20 14bi', 'calc', ['3^x*sqrt(x)-1'], 'Differentiate', None,
     ['~3^x*ln(3)*sqrt(x)+3^x/(2sqrt(x))']),
    ('1 nov20 15 c', 'calc', ['e^x', '6-e^(x/2)'], 'Area between, limits', ['0', 'ln(4)'], ['~6ln(4)-5']),
    ('1 nov21 2', 'calc', ['ln(5x)'], 'Differentiate', None, ['~1/x']),
    ('1 nov21 10a', 'calc', ['sin(x)/cos(x)'], 'Differentiate', None, ['~1/cos(x)^2', 'quotientrule']),
    ('1 nov21 10b', 'calc', ['1-tan(x)^2'], 'Definite integral', ['-pi/4', 'pi/4'], ['~pi-2']),
    ('1 nov21 11', 'calc', ['dy/dx=x^2*y^2/6'], 'Solve with a point', ['1', '6'], ['~18/(4-x^3)']),
    ('1 nov21 12a', 'calc', ['(x+y)^2=4y+2x+8'], 'Gradient at a point', ['4', '0'], ['~-3/2']),
    ('1 nov21 14a', 'calc', ['x=t^2+t', 'y=4t^2-t^3'], 'Gradient at t =', ['4'], ['~-16/9']),
    ('1 nov21 14biii', 'calc', ['4x^2+7x^3-2x^4'], 'Definite integral', ['0', '4'], ['1856/15']),
    ('1 nov21 15b', 'calc', ['sqrt(16x^3)'], 'Definite integral', ['0', '0.25'], ['1/20|0.05']),
    ('2 jun18 3', 'calc', ['x^3'], 'Area under curve', ['-2', '4'], ['area=68']),
    ('2 jun18 7', 'calc', ['(x-1)e^x'], 'Integrate', None, ['~(x-2)e^x']),
    ('2 jun19 5', 'calc', ['dy/dx=ln(x)/(x^2*y)'], 'Solve with a point', ['1', '2'],
     ['~sqrt(6-2(1+ln(x))/x)']),
    ('2 jun19 9c', 'calc', ['1-x^2/4'], 'Definite integral', ['0', '0.4'], ['0.395|148/375']),
    ('2 jun19 16a', 'calc', ['11.71-11.68e^(-0.9x)-0.03e^(0.3x)'], 'Stationary points', None,
     ['x=5.89', 'maximum']),
    ('2 jun22 7b', 'calc', ['15x-x^3'], 'Stationary points', None, ['x=sqrt(5),y=10sqrt(5)', 'maximum']),
    ('2 jun23 4a', 'calc', ['x^2/8+4sqrt(x)'], 'Differentiate', None, ['~x/4+2/sqrt(x)']),
    ('2 jun23 4b', 'calc', ['x^2/8+4sqrt(x)'], 'Tangent at x =', ['4'], ['~2x+2']),
    ('2 jun24 5', 'calc', ['x^3/sin(x)'], 'Differentiate', None, ['~(3x^2*sin(x)-x^3*cos(x))/sin(x)^2']),
    ('2 jun25 7b', 'calc', ['x^3+p*x^2+q*x+12'], 'Differentiate', None, ['~3x^2+2px+q']),
    ('2 jun25 7d', 'calc', ['x^3+9x^2+15x+12'], 'Stationary points', None, ['x=-1,y=5', 'minimum']),
    ('2 jun25 10a', 'calc', ['x^k*ln(x)'], 'Differentiate', None, ['~x^(k-1)*(1+k*ln(x))']),
    ('2 nov20 1', 'calc', ['-e^(x-1)'], 'Increasing where?', None, ['increasing(dy/dx>0):nowhere']),
    ('2 nov20 5', 'calc', ['x*sqrt(4x+1)'], 'Definite integral', ['-1/4', '6'], ['875/12']),
    ('2 nov20 8bi', 'calc', ['x=t^2', 'y=2t'], 'dy/dx (parametric)', None, ['~1/t']),
    ('2 nov20 9b', 'calc', ['pi*r^2*x-pi*x^3'], 'Stationary points', None, ['maximum', 'sqrt(3)']),
    ('2 nov20 19a', 'calc', ['dv/dt=-0.1v^2'], 'Solve with a point', ['0', '4'], ['~20/(5+2t)']),
    ('2 nov21 11', 'calc', ['3e^(0.5x)'], 'Differentiate', None, ['~1.5e^(0.5x)']),
    ('2 nov21 17b', 'calc', ['dy/dx=g-0.1y'], 'Solve with a point', ['0', '0'], ['~10g(1-e^(-0.1x))']),
    ('3 jun18 2', 'calc', ['x^5+4x^3+7x+5'], 'Tangent at x =', ['0'], ['dy/dx=7']),
    ('3 jun18 6b', 'calc', ['x/sqrt(2x-2)'], 'Differentiate', None, ['(x-2)/(2x-2)^(3/2)']),
    ('3 jun18 6c', 'calc', ['x/sqrt(2x-2)'], 'Inflection points', None, ['x=4', 'concave', 'x>4']),
    ('3 jun19 7b', 'calc', ['(4x+3)/(x-1)^2'], 'Definite integral', ['3', '4'], ['~4ln(3)-4ln(2)+7/6']),
    ('3 jun19 9bi', 'calc', ['x^2*y^2+x*y^4=12'], 'dy/dx (implicit)', None,
     ['~(-y^4-2x*y^2)/(4x*y^3+2x^2*y)']),
    ('3 jun19 9bii', 'calc', ['x^2*y^2+x*y^4=12'], 'Where dy/dx = 0', None, ['norealsolutions']),
    ('3 jun19 9biii', 'calc', ['x^2*y^2+x*y^4=12'], 'Tangent at a point', ['3', '1'], ['~-7x/30+17/10']),
    ('3 jun22 4', 'calc', ['sqrt(x)+x^2'], 'Integrate', None, ['~x^3/3+2x^(3/2)/3']),
    ('3 jun22 6bi', 'calc', ['x=-2t^2', 'y=9t-0.7t^2'], 'dy/dx (parametric)', None, ['~(9-1.4t)/(-4t)']),
    ('3 jun23 9bi', 'calc', ['x=t-1/t+4.8', 'y=t+2/t'], 'dy/dx (parametric)', None,
     ['~(t^2-2)/(t^2+1)']),
    ('3 jun24 4', 'calc', ['x^4+2^x'], 'Differentiate', None, ['~4x^3+2^x*ln(2)']),
    ('3 jun24 6a', 'calc', ['6x^2-5/sqrt(x)'], 'Integrate', None, ['~2x^3-10sqrt(x)']),
    ('3 jun24 6b', 'calc', ['dy/dx=6x^2-5/sqrt(x)'], 'Solve with a point', ['4', '90'],
     ['~2x^3-10sqrt(x)-18']),
    ('3 jun24 10', 'calc', ['5x^3+x'], 'First principles', None, ['~15x^2+1']),
    ('3 jun24 11', 'calc', ['(x^2-8x)ln(x)'], 'Definite integral', ['1', '8'], ['~-256ln(2)+623/9']),
    ('3 jun25 8b', 'calc', ['x/(2x^2+3x+1)'], 'Definite integral', ['0', '4'], ['~ln(5/3)']),
    ('3 jun25 11b', 'calc', ['8x^3'], 'Differentiate', None, ['~24x^2']),
    ('3 nov21 5bii', 'calc', ['18/5*(20/x+x)'], 'Stationary points', None, ['x=2sqrt(5)', 'minimum']),
    ('3 nov21 8', 'calc', ['x*cos(x)'], 'Definite integral', ['pi/4', 'pi/3'],
     ['~pi*sqrt(3)/6-pi*sqrt(2)/8-sqrt(2)/2+1/2']),
    ('3 nov21 9aii', 'calc', ['x^4+5x^3'], 'Stationary points', None, ['x=-15/4', 'minimum']),
    ('3 nov21 9b', 'calc', ['x^4+5x^3'], 'Increasing where?', None, ['x>-15/4']),
    ('1 jun22 13b', 'calc', ['x^2+y^2-64sqrt(x)+y=0'], 'Where dy/dx = 0', None, ['x=6.35', 'y=10.5']),
    ('1 jun23 15a', 'calc', ['x^2+2y^3=4x*y'], 'Where dy/dx = 0', None, ['x=4,y=2']),
    ('2 jun18 6', 'calc', ['(x+y-2)^2=e^y-1'], 'Where dy/dx = 0', None, ['x=2,y=0']),
    ('1 jun25 11a', 'calc', ['x^2*y+4y^3=8x'], 'Where dy/dx = 0', None, ['sqrt(2)']),
]

# parts with calculator steps the new flow does not do yet (not counted as passes)
NOT_YET = [
    ('1 jun18 12c', 'trig', 'cubic in sec x on 0..360: Trig topic'),
    ('1 nov20 8b', 'alg', 'inequality f > g on a window 0..500: no window in Solve inequality yet'),
    ('1 nov21 9ci', 'exp', 'log-linear fit to a data list: needs data entry (Statistics)'),
    ('2 jun22 17', 'trig', 'sqrt of trig squares: Trig topic'),
    ('2 jun24 6', 'trig', 'trig equation on an interval: Trig topic'),
    ('1 jun25 16bi', 'trig', 'compound angle expansion: Trig topic'),
    ('1 jun22 15b', 'calc', 'integration by substitution with the steps (u = 2/sin x): not an action yet'),
    ('1 jun24 18a', 'calc', 'integration by substitution with the steps: not an action yet'),
    ('1 jun25 17a', 'calc', 'integration by substitution with the steps: not an action yet'),
    ('2 jun18 7b', 'calc', 'integration by parts with the steps: the answer only'),
    ('3 jun22 8b', 'calc', 'connected rates of change: not an action yet'),
    ('1 jun23 16bii', 'calc', 'a DE needing partial fractions to integrate: not yet'),
    ('2 jun22 10bii', 'calc', 'a DE needing partial fractions to integrate: not yet'),
    ('1 jun25 17b', 'calc', 'a DE with cos^2 y: not yet'),
]
C += [('1 jun25 13b', 'calc', ['x=4(4t+1)^2', 'y=e^(-4t)'], 'Tangent at t =', ['0'], ['~-x/8+3/2'])]
# by design (spec: no one-formula tools): a circle from its centre and radius
# is just writing (x - a)^2 + (y - b)^2 = r^2; 1 jun22 8bii, 2 jun22 1, 2 nov20 6b, 3 jun18 1

PENDING = []    # refs failing now, kept out of tests.py (python3 tests_accept.py shows them)

import caslex

def _norm(s):
    return s.lower().replace(' ', '').replace('*', '')

def _flat(lines):
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            if ln[0] == '=':
                pre, ex, dc = ln[1], ln[2], ln[3]
                out.append(pre + (ex or ''))
                if dc:
                    out.append(pre + dc)
                if ex and dc:
                    out.append(pre + ex + ' = ' + dc)
            elif ln[0] in ('m', 'mw'):
                import caseng
                out.append(caseng.tostr(ln[1]))
            else:
                out.append(str(ln[1]))
        else:
            out.append(str(ln))
    return out

def _trees(lines):
    return [ln[4] for ln in lines if isinstance(ln, tuple) and ln[0] == '=' and len(ln) > 4
            and ln[4] is not None]

def _same(t, want):
    # equal by value at a few points for every letter in either
    import caseng
    import recog
    vs = recog.letters(t)
    for v in recog.letters(want):
        if v not in vs:
            vs.append(v)
    pts = (0.37, 1.29, 2.71, 3.83, 4.4, -0.61, -2.3)
    agree = 0
    for k in range(len(pts)):
        env = {}
        for i in range(len(vs)):
            env[vs[i]] = pts[(i + k) % len(pts)]
        try:
            a = caseng.evalf(t, env.get('x', 0.0), False, env)
            b = caseng.evalf(want, env.get('x', 0.0), False, env)
        except Exception:
            continue
        if isinstance(a, complex) or isinstance(b, complex):
            continue
        if abs(a - b) > 1e-6 * (1 + abs(b)):
            return False
        agree += 1
    return agree >= 2

def run_case(case):
    # -> (ok, detail)
    import recog
    import acts
    import topic
    ref, tid, rows, label, ask, needles = case
    if tid == 'geo':
        F = recog.geo([r for r in rows if isinstance(r, tuple)], [r for r in rows if not isinstance(r, tuple)])
    else:
        F = recog.form(rows)
    if F.err:
        return False, 'not read: ' + F.err
    offers = acts.offers(F, tid)
    off = None
    for o in offers:
        if o[0] == label:
            off = o
    if off is None:
        return False, 'not offered (' + F.note + '): ' + ', '.join([o[0] for o in offers])
    vals = None
    if off[4]:
        if off[4][0] == 'choose':
            vals = [int(ask[0])]
        else:
            vals = []
            for a in ask:
                a = a.strip()
                vals.append(None if a in ('', '?') else caslex.parse(a))
    lines = topic.engine(off[1], off[2], F, off[3], vals)
    if lines is None:
        return True, ''
    text = _flat(lines)
    for ln in lines:
        if isinstance(ln, tuple) and ln[0] == '!' and 'error' in ln[1]:
            return False, ln[1]
    blob = _norm(' | '.join(text))
    trees = _trees(lines)
    for nd in needles:
        hit = False
        for alt in nd.split('|'):
            if alt[:1] == '~':
                want = caslex.parse(alt[1:].split('=')[-1])
                for t in trees:
                    if _same(t, want):
                        hit = True
            elif _norm(alt) in blob or _norm(alt) in blob.replace('*', ''):
                hit = True
        if not hit:
            return False, 'missing ' + repr(nd) + ' in: ' + ' | '.join(text)[:400]
    return True, ''

def run(check):
    # the calculator's self test runs a copy of 50 of these: still the same
    import selfcases
    byref = {}
    for c in C:
        byref[c[0]] = c
    check('selfcases has 50 cases', len(selfcases.CASES) == 50, len(selfcases.CASES))
    for c in selfcases.CASES:
        check('selfcases ' + c[0] + ' matches tests_accept', byref.get(c[0]) == c, c)
    for case in C:
        if case[0] in PENDING:
            continue
        ok, why = run_case(case)
        check('accept ' + case[0] + ' ' + case[3] + ' <' + '; '.join([str(r) for r in case[2]]) + '>', ok, why)
    _csq(check)
    _depth(check)

CSQ = ('x^2+3x+k', '2x^2-12x+5', '1+x-2x^2', 'x^2+b*x+4', 'k*x^2+4x+1', '3x^2+6p*x+q',
       'a*x^2+b*x+c', 'x^2-6x+9', 'x^2+4x', '2x^2+3x', '-x^2+2x+1', 'x^2-2k*x+k^2+1',
       '5x^2-3x+1', 'x^2+x+1/4', '4x^2-12x+p')

def _csq(check):
    # the Algebra action and the old tools (casalg.csq_lines: CAS op, Pure
    # tool) complete the square to the same form and turning point
    import caslex
    import caseng
    import casalg
    import recog
    import e_alg
    for s in CSQ:
        old = casalg.csq_lines(caslex.parse(s))
        new = e_alg.csq(recog.form([s]), None, None)
        box = [l for l in new if isinstance(l, tuple) and l[0] == '=']
        a = caseng.tostr(old[0][1]).replace('*', '')
        b = box[0][2].replace(' ', '').replace('*', '') if box else None
        check('complete the square same both ways: ' + s, a == b, (a, b))
        vx = [l for l in new if isinstance(l, str) and l.startswith('vertex ')]
        tp = old[1][old[1].index('('):]
        check('turning point same both ways: ' + s, vx and vx[0][7:].replace(' ', '') == tp.replace(' ', ''),
              (vx, tp))

def _depth(check):
    # the calculator stops at about 92 nested calls: every case, with its
    # answer page laid out, must stay well under that
    import sys
    import topic
    worst = [0, '']

    def prof(frame, event, arg):
        if event == 'call':
            d = 0
            f = frame
            while f is not None:
                d += 1
                f = f.f_back
            if d > worst[0]:
                worst[0] = d
        return None
    base = 0
    f = sys._getframe()
    while f is not None:
        base += 1
        f = f.f_back
    deepest = (0, '')
    for case in C:
        worst[0] = 0
        sys.setprofile(prof)
        try:
            run_case(case)
        finally:
            sys.setprofile(None)
        if worst[0] - base > deepest[0]:
            deepest = (worst[0] - base, case[0])
    check('accept: calls nest under 45 deep', deepest[0] < 45, deepest)

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plot
    plot.run = lambda *a, **k: None
    tot = {}
    bad = []
    for case in C:
        ok, why = run_case(case)
        t = case[1]
        n, p = tot.get(t, (0, 0))
        tot[t] = (n + 1, p + (1 if ok else 0))
        if not ok:
            bad.append((case, why))
    for t in sorted(tot):
        n, p = tot[t]
        print('%-4s %3d / %3d pass' % (t, p, n))
    print('not yet in the new flow: ' + str(len(NOT_YET)) + ' parts (' +
          ', '.join([r for r, t, w in NOT_YET]) + ')')
    for case, why in bad:
        print('FAIL ' + case[0] + '  ' + case[3] + ' <' + '; '.join([str(r) for r in case[2]]) + '>  ' + why[:300])
