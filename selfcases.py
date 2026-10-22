# The self test's cases and runner (selftest.py starts it). 50 past-paper
# parts from tests_accept.py, run through the new topic flow exactly as the
# screens do (recognise, the action from the tiles, its engine) without
# drawing the answers; each shows pass or fail and the free memory, then one
# summary screen to photograph. tests.py checks these match tests_accept.py.
from casioplot import clear_screen, draw_string, show_screen, getkey

CASES = (
    ('1 jun18 4', 'exp', ['e^(x-4)'], 'Inverse', None, ['~ln(x)+4', 'x>0']),
    ('1 jun18 5b', 'alg', ['xy+5x-3y=27'], 'Rearrange for x', None, ['~(3y+27)/(y+5)']),
    ('1 jun18 9a', 'alg', ['(6a+15d)^2'], 'Expand', None, ['36a^2+180ad+225d^2']),
    ('1 jun18 9b', 'alg', ['a+5d=25', '4a+70d=4a^2+20ad+25d^2'], 'Solve', None, ['a=-55,d=16', 'a=-5,d=6']),
    ('1 jun18 10b', 'exp', ['400e^(-0.1216047t)=280'], 'Solve', None, ['t=2.93']),
    ('1 jun18 12a', 'alg', ['30x^3-7x^2-7x+2'], 'Factor theorem', ['-1/2'], ['(2x+1)isafactor']),
    ('1 jun18 12b', 'alg', ['30x^3-7x^2-7x+2'], 'Factorise', None, ['(2x+1)(3x-1)(5x-2)']),
    ('1 jun19 6bi', 'alg', ['(x^2+1)/2'], 'Inverse', None, ['sqrt(2x-1)']),
    ('1 jun19 12b', 'alg', ['4c^2-4c-3=0'], 'Solve', None, ['c=-1/2', 'c=3/2']),
    ('1 jun22 11bii', 'alg', ['x^2+bx+4'], 'Discriminant', None, ['equalroots:b=-4or4']),
    ('1 jun23 6', 'exp', ['2log(x)=log(4)+log(x+8)'], 'Solve', None, ['x=8', 'reject']),
    ('1 jun23 7a', 'alg', ['7/(3+5sqrt(x))-7/(5sqrt(x)-3)'], 'Simplify', None, ['~-42/(25x-9)']),
    ('1 jun23 16a', 'alg', ['1/(16-9x^2)'], 'Partial fractions', None, ['1/(8(4-3x))', '1/(8(3x+4))|1/(8(4+3x))']),
    ('1 jun24 3', 'alg', ['12x^2+3x+7'], 'Divide', ['3x-5'], ['quotient4x+23/3']),
    ('1 jun24 7', 'alg', ['(3+sqrt(8x))/(1+sqrt(2x))'], 'Rationalise', None, ['~(4x-3+sqrt(2x))/(2x-1)', '/(2x-1)']),
    ('1 jun24 8a', 'alg', ['(2+kx)^5'], 'Expand', None, ['32+80kx+80k^2x^2']),
    ('1 jun24 17a', 'alg', ['abs(x)+1'], 'Range', None, ['f(x)>=1']),
    ('1 jun24 17b', 'alg', ['ln(x)'], 'Domain', None, ['x>0']),
    ('1 jun24 17ci', 'alg', ['f(x)=ln(x)', 'g(x)=abs(x)+1'], 'fg and gf', None, ['fg(x)=ln(|x|+1)']),
    ('1 jun25 3', 'exp', ['logb(3,2x)-logb(3,x)'], 'Combine logs', None, ['log_32']),
    ('1 jun25 10c', 'exp', ['21-39.5e^(-0.184t)=4'], 'Solve', None, ['t=4.58']),
    ('1 nov20 4b', 'alg', ['4-abs(2x-6)>2'], 'Solve inequality', None, ['2<x<4']),
    ('1 nov20 9b', 'alg', ['(2x^2+x)/((x+1)(x+2)^2)'], 'Partial fractions', None, ['1/(x+1)', '1/(x+2)', '6/(x+2)^2']),
    ('1 nov20 13ai', 'alg', ['(2x+3)/(x-2)'], 'Inverse', None, ['~(2x+3)/(x-2)']),
    ('1 nov20 13c', 'alg', ['f(x)=(2x+3)/(x-2)', 'g(x)=(2x^2-5x)/2'], 'fg and gf', None, ['~gf=(48+29x-2x^2)/(2(x-2)^2)']),
    ('1 nov20 13d', 'alg', ['2x^2-5x-4=0'], 'Solve', None, ['(5+sqrt(57))/4', '(5-sqrt(57))/4']),
    ('1 nov20 15', 'exp', ['e^x=6-e^(x/2)'], 'Solve', None, ['~2ln(2)']),
    ('1 nov21 1', 'alg', ['(x-3)(2x+7)>0'], 'Solve inequality', None, ['x<-7/2orx>3']),
    ('1 nov21 9e', 'exp', ['75*10^(0.02t)=8000'], 'Solve', None, ['t=101']),
    ('2 jun18 4b', 'alg', ['x^2-6x+k'], 'Discriminant', None, ['twodistinctrealroots:k<9']),
    ('2 jun18 8bi', 'alg', ['1/(2sqrt(3)+4)'], 'Rationalise', None, ['~(2-sqrt(3))/2']),
    ('2 jun19 6', 'alg', ['a^2+b^2=16', 'sqrt(3)/2*a+b/2=2sqrt(3)'], 'Solve', None, ['a=2,b=2sqrt(3)', 'a=4,b=0']),
    ('2 jun19 8b', 'exp', ['y=kb^x'], 'From two points', ['0', '10^3.9', '40', '10^5.28', ''], ['k=7940', 'b=1.08']),
    ('2 jun22 9', 'exp', ['logb(2,x^3)-logb(2,y^2)=9'], 'Rearrange for x', None, ['x=8y^(2/3)']),
    ('2 jun22 10bi', 'alg', ['2700/(x(900-x))'], 'Partial fractions', None, ['3/x', '3/(900-x)']),
    ('2 jun23 7c', 'alg', ['1/sqrt(10-2x)'], 'Inverse', None, ['~5-1/(2x^2)']),
    ('2 jun24 4', 'exp', ['5^(x-2)=7^1570'], 'Solve', None, ['x=1900']),
    ('2 jun24 9b', 'alg', ['36x/((1+3x)(2-3x))'], 'Partial fractions', None, ['8/(2-3x)', '4/(1+3x)']),
    ('2 jun25 4', 'exp', ['5^(x-1)=20'], 'Solve', None, ['~1+log(20)/log(5)', 'log_5']),
    ('2 nov21 6', 'exp', ['5^x=3^(x+4)'], 'Solve', None, ['~ln(81)/(ln(5)-ln(3))', 'x=8.60|x=8.6']),
    ('2 nov21 9c', 'alg', ['1+c-2c^2'], 'Complete square', None, ['9/8', '(c-1/4)^2']),
    ('2 nov21 10a', 'alg', ['sqrt(x)/(x-3)'], 'Domain', None, ['x>=0,x!=3']),
    ('3 jun18 7a', 'exp', ['logb(a,y)=2logb(a,7)+logb(a,4)+1/2'], 'Rearrange for y', None, ['y=196sqrt(a)']),
    ('3 jun19 8a', 'exp', ['5(4+x)=75', '5(4+x*e^(-2y))=68'], 'Solve', None, ['x=11', '0.068']),
    ('3 jun22 10e', 'alg', ['(x^2+10)/(2x+5)'], 'Range', None, ['sqrt(65)', 'or']),
    ('3 jun22 7aii', 'exp', ['y=k*x^n'], 'From two points', ['10^1.76', '10^1.94', '10^3.46', '10^4.49', ''], ['k=0.2', 'n=1.5']),
    ('3 jun25 4b', 'exp', ['logb(a,sqrt(a))-logb(a,1/a^2)'], 'Combine logs', None, ['5/2']),
    ('3 nov20 8bii', 'exp', ['logb(3,3^n/2^(2n-5))'], 'Expand logs', None, ['~n-(2n-5)logb(3,2)']),
    ('3 nov21 6', 'alg', ['(10+5x-2sqrt(x)-x^(3/2))/(5-sqrt(x))'], 'Simplify', None, ['x+2']),
    ('1 jun18 2', 'exp', ['5^x'], 'Transform', ['5', '1', '0', '0'], ['~5^(x+1)']),
)

INK = (24, 28, 36)
GREY = (110, 115, 125)
GREEN = (30, 150, 90)
RED = (200, 50, 50)
ORANGE = (235, 130, 30)

# The log rows exist before any case runs: on a full heap a row's text may not
# fit (NOMEM is written instead), but writing a row and the summary never
# needs memory the cases used up.
ROWS = 56
TXT = [None] * ROWS
COL = [GREY] * ROWS
NLOG = [0]
BAD = [0] * ROWS    # numbers of the failed cases
NOMEM = '(no memory left to write this row)'

def log(s, c):
    i = NLOG[0]
    if i < ROWS:
        TXT[i] = s
        COL[i] = c
        NLOG[0] = i + 1

def rows():
    # the log as (text, colour) pairs (laptop runs print it)
    return [(TXT[i], COL[i]) for i in range(NLOG[0])]

def _clobber(n):
    # old pointers left on the stack can keep the probe's blocks alive (the
    # collector is conservative): a few calls with fresh locals write over them
    a = b = c = d = None
    if n:
        _clobber(n - 1)

def free_kb():
    # fill memory with 16 KB strings, then 1 KB ones, until it runs out, then
    # let them go: the free memory in KB (no gc module on the calculator)
    _clobber(8)
    blocks = []
    n = 0
    for size in (16, 1):
        try:
            while True:
                blocks.append('x' * (1024 * size))
                n += size
        except MemoryError:
            pass
    del blocks[:]
    blocks = None
    _clobber(8)
    return n

def show(now):
    clear_screen()
    draw_string(4, 2, 'Self test', INK, 'small')
    y = 18
    i = NLOG[0] - 11 if NLOG[0] > 11 else 0
    while i < NLOG[0]:
        draw_string(4, y, TXT[i], COL[i], 'small')
        y += 14
        i += 1
    draw_string(4, 176, now, ORANGE, 'small')
    show_screen()

def _norm(s):
    return s.lower().replace(' ', '').replace('*', '')

def _text(lines):
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            if ln[0] == '=':
                pre, ex, dc = ln[1], ln[2], ln[3]
                out.append(pre + (ex or ''))
                if dc:
                    out.append(pre + dc)
            else:
                out.append(str(ln[1]))
        else:
            out.append(str(ln))
    return out

def _same(t, want):
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

def check(case):
    # '' when it passes, else why not
    import recog
    import acts
    import topic
    import caslex
    ref, tid, rows, label, ask, needles = case[:6]
    import casui
    keep = dict(casui.SET)
    kdeg = casui.DEG
    try:
        if len(case) > 6:
            casui.SET.update(case[6])
            casui.DEG = casui.SET['angle'] == 'deg'
        return _check(tid, rows, label, ask, needles)
    finally:
        casui.SET.clear()
        casui.SET.update(keep)
        casui.DEG = kdeg

def _check(tid, rows, label, ask, needles):
    import recog
    import acts
    import topic
    import caslex
    F = recog.read(tid, rows)
    if F.err:
        return 'not read'
    off = None
    for o in acts.offers(F, tid):
        if o[0] == label:
            off = o
    if off is None:
        return 'not offered'
    vals = None
    if off[4] and off[4][0] == 'boxes':
        vals = topic.readboxes(off[4][1], ask)
    elif off[4]:
        vals = []
        for a in ask:
            a = a.strip()
            vals.append(None if a in ('', '?') else caslex.parse(a))
    lines = topic.engine(off[1], off[2], F, off[3], vals)
    if lines is None:
        return ''
    for ln in lines:
        if isinstance(ln, tuple) and ln[0] == '!' and 'error' in ln[1]:
            return ln[1][:30]
    blob = _norm(' | '.join(_text(lines)))
    trees = [ln[4] for ln in lines if isinstance(ln, tuple) and ln[0] == '=' and len(ln) > 4
             and ln[4] is not None]
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
            return 'missing ' + nd[:24]
    return ''

def _summary(ok, n, start, ui, low, end, nb):
    clear_screen()
    draw_string(4, 4, 'Self test: ' + str(ok) + ' / ' + str(n) + ' pass', GREEN if ok == n else RED, 'medium')
    draw_string(4, 30, 'free KB: start ' + str(start) + ', with screens ' + str(ui), INK, 'small')
    draw_string(4, 46, 'lowest after a case ' + str(low) + ', at the end ' + str(end), INK, 'small')
    y = 66
    if nb:
        draw_string(4, y, 'failed:', RED, 'small')
        y += 14
        s = ''
        for j in range(nb):
            b = CASES[BAD[j] - 1][0]
            if len(s) + len(b) > 44:
                draw_string(4, y, s, RED, 'small')
                y += 14
                s = ''
            s += b + ', '
        if s:
            draw_string(4, y, s[:-2], RED, 'small')
            y += 14
    draw_string(4, 176, 'photo this screen, then EXE', GREY, 'small')
    show_screen()

def run():
    NLOG[0] = 0
    start = free_kb()
    log('free at start ' + str(start) + ' KB', GREY)
    show('loading the topic screens')
    import casui
    import topic
    import recog
    import acts
    ui = free_kb()
    log('after the screens ' + str(ui) + ' KB', GREY)
    low = ui
    ok = 0
    nb = 0
    n = len(CASES)
    i = 0
    for case in CASES:
        i += 1
        try:
            show('case ' + str(i) + '/' + str(n) + '  ' + case[0] + '  ' + case[3] + ' ...')
        except MemoryError:
            pass
        try:
            why = check(case)
        except MemoryError:
            why = 'OUT OF MEMORY'
        except Exception as e:
            why = 'error ' + str(e)[:24]
        f = free_kb()
        if f < low:
            low = f
        if why:
            BAD[nb] = i
            nb += 1
        else:
            ok += 1
        try:
            if why:
                s = str(i) + ' FAIL ' + case[0] + ' ' + case[3] + ': ' + why + '  ' + str(f) + ' KB'
            else:
                s = str(i) + ' pass ' + case[0] + ' ' + case[3] + '  ' + str(f) + ' KB'
        except MemoryError:
            s = NOMEM
        log(s, RED if why else GREEN)
    end = free_kb()
    try:
        _summary(ok, n, start, ui, low, end, nb)
    except MemoryError:
        # constant strings only
        clear_screen()
        draw_string(4, 4, 'Self test: out of memory', RED, 'medium')
        draw_string(4, 30, 'for the summary. Run it again', INK, 'small')
        draw_string(4, 46, 'after restarting the calculator.', INK, 'small')
        show_screen()
    k = getkey()
    while k != 95 and k != 22 and k != 24:
        k = getkey()
