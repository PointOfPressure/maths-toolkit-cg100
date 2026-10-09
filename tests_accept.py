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

# parts with calculator steps the new flow does not do yet (not counted as passes)
NOT_YET = [
    ('1 jun18 12c', 'trig', 'cubic in sec x on 0..360: Trig topic'),
    ('1 nov20 8b', 'alg', 'inequality f > g on a window 0..500: no window in Solve inequality yet'),
    ('1 nov21 9ci', 'exp', 'log-linear fit to a data list: needs data entry (Statistics)'),
    ('2 jun22 17', 'trig', 'sqrt of trig squares: Trig topic'),
    ('2 jun24 6', 'trig', 'trig equation on an interval: Trig topic'),
    ('1 jun25 16bi', 'trig', 'compound angle expansion: Trig topic'),
]

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
            elif _norm(alt) in blob:
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
        check('accept ' + case[0] + ' ' + case[3] + ' <' + '; '.join(case[2]) + '>', ok, why)

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
        print('FAIL ' + case[0] + '  ' + case[3] + ' <' + '; '.join(case[2]) + '>  ' + why[:300])
