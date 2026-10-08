# Hardware test. Run it from the Python app; it needs no input until the
# summary, which pages with EXE. Photograph or copy the summary pages.
# Timings need a clock module; without one the lines say "no clock".
from casioplot import *

OUT = []
BAD = []
N = [0]

def say(s):
    OUT.append(s)
    print(s)

def ok(name, cond, detail=''):
    N[0] += 1
    if not cond:
        BAD.append(name + (' ' + str(detail) if detail != '' else ''))

def _clock():
    for name in ('time', 'utime'):
        try:
            m = __import__(name)
        except Exception:
            continue
        if hasattr(m, 'ticks_ms'):
            return m.ticks_ms, name + '.ticks_ms'
        if hasattr(m, 'monotonic'):
            return (lambda: int(m.monotonic() * 1000)), name + '.monotonic'
        if hasattr(m, 'time'):
            return (lambda: int(m.time() * 1000)), name + '.time'
    return None, 'none'

CLK, CLKNAME = _clock()

def ms(fn, reps=1):
    # milliseconds per call, or None without a clock
    if CLK is None:
        fn()
        return None
    t0 = CLK()
    i = 0
    while i < reps:
        fn()
        i += 1
    return (CLK() - t0) * 1.0 / reps

def fms(v):
    if v is None:
        return '-'
    return str(int(v + 0.5)) if v >= 10 else str(int(v * 10 + 0.5) / 10.0)

try:
    gc = __import__('gc')
except Exception:
    gc = None

def mem():
    if gc is None:
        return '-'
    try:
        gc.collect()
        return str(gc.mem_free() // 1024) + 'k'
    except Exception:
        return '?'

def status(msg):
    clear_screen()
    draw_string(6, 80, 'hwtest: ' + msg, (0, 0, 0), 'medium')
    show_screen()

# ---- 1 platform --------------------------------------------------------------

def platform():
    have = []
    for name in ('time', 'utime', 'gc', 'sys', 'os', 'micropython', 'array', 'struct', 'math', 'random'):
        try:
            __import__(name)
            have.append(name)
        except Exception:
            pass
    say('mods ' + ' '.join(have))
    say('clock ' + CLKNAME + '  mem ' + mem())
    try:
        sys = __import__('sys')     # probe: not on the documented module list
        say('py ' + str(sys.implementation.version) + ' ' + str(sys.platform))
    except Exception:
        pass
    wrote = 'no'
    try:
        f = open('hwlog.txt', 'w')
        f.write('ok\n')
        f.close()
        wrote = 'yes'
    except Exception as e:
        wrote = 'no (' + type(e).__name__ + ')'
    say('file write ' + wrote)
    got = []
    for v in 'abcd':
        try:
            m = __import__('mpy' + v)
            got.append(v + '=' + ('ok' if m.f(6, 7) == 43 else 'bad'))
        except Exception as e:
            got.append(v + '=' + type(e).__name__[:8])
    say('mpy ' + ' '.join(got))

# ---- 2 screen ------------------------------------------------------------------

def _ink(x0, y0, x1, y1):
    n = 0
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            p = get_pixel(x, y)
            if p is not None and tuple(p) != (255, 255, 255):
                n += 1
            x += 1
        y += 1
    return n

def _width(s, size):
    clear_screen()
    draw_string(0, 0, s, (0, 0, 0), size)
    x = 383
    while x > 0:
        y = 0
        while y < 30:
            p = get_pixel(x, y)
            if p is not None and tuple(p) != (255, 255, 255):
                return x + 1
            y += 1
        x -= 1
    return 0

def screen():
    status('screen speed')
    clear_screen()

    def px():
        sp = set_pixel
        c = (40, 120, 220)
        y = 0
        while y < 50:
            x = 0
            while x < 100:
                sp(x, y, c)
                x += 1
            y += 1
    t = ms(px)
    say('5000 set_pixel ' + fms(t) + 'ms')

    def txt():
        i = 0
        while i < 20:
            draw_string(0, i * 9, 'The quick brown fox 0123', (0, 0, 0), 'medium')
            i += 1
    say('20 draw_string ' + fms(ms(txt)) + 'ms')
    say('clear+show ' + fms(ms(lambda: (clear_screen(), show_screen()), 5)) + 'ms')
    # font check: the UI lays text out with these widths
    w1 = _width('mmmmmmmmmm', 'medium')
    w2 = _width('iiiiiiiiii', 'medium')
    w3 = _width('xxxxxxxxxx', 'medium')
    w4 = _width('xxxxxxxxxx', 'small')
    w5 = _width('xxxxxxxxxx', 'large')
    say('font m/i/x med ' + str(w1) + '/' + str(w2) + '/' + str(w3) +
        ' sm ' + str(w4) + ' lg ' + str(w5) + ' (want 120/80/100 70 180)')
    ok('medium x width', 94 <= w3 <= 104, w3)
    clear_screen()
    try:
        draw_string(10, 10, chr(0x3c0) + chr(0x221a) + chr(0xb2), (0, 0, 0), 'medium')
        u = _ink(8, 8, 60, 30)
    except Exception as e:
        u = type(e).__name__
    say('unicode glyph ink ' + str(u))

# ---- 3 loading -------------------------------------------------------------------

MODS = ('caslex', 'caseng', 'casutil', 'casrender', 'cascalc', 'caspoly',
        'casalg', 'cassolve', 'nat', 'casui', 'plot', 'tex', 'texg', 'tn_fb', 'tables',
        'mpure', 'mcalc', 'mstat', 'mmech', 'fcore', 'fcalc', 'fmech',
        'fstat', 'falgo', 'fnum', 'fxpure', 'ffpt')

def loading():
    line = ''
    total = 0.0
    try:
        mods = __import__('sys').modules
    except Exception:
        mods = {}
    for m in MODS:
        status('import ' + m)
        if m in mods:
            del mods[m]         # time a cold load even if maths.py ran first
        try:
            t = ms(lambda: __import__(m))
            if t is not None:
                total += t
            line += m[:6] + ' ' + fms(t) + '  '
        except MemoryError:
            line += m[:6] + ' MEM  '
            ok('import ' + m, False, 'MemoryError')
        except Exception as e:
            line += m[:6] + ' ERR  '
            ok('import ' + m, False, type(e).__name__ + ' ' + str(e)[:30])
        if len(line) > 40:
            say(line)
            line = ''
    if line:
        say(line)
    say('all imports ' + fms(total if CLK else None) + 'ms  mem ' + mem())

# ---- 4 maths ------------------------------------------------------------------------

def _flat(lines):
    import caseng
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            out.append(caseng.tostr(ln[1]) if ln[0] in ('m', 'mw') else str(ln[1]))
        else:
            out.append(str(ln))
    return '\n'.join(out)

ENGINE = (
    ('simplify', 'S', '(x^2-1)/(x-1)', 'x+1'),
    ('surd', 'S', 'sqrt(8)/(1/3+1/6)', '4*sqrt(2)'),
    ('complex', 'S', '(2+3i)/(1-i)', '-1/2+5i/2'),
    ('trig id', 'S', 'sin(x)^2+cos(x)^2', '1'),
    ('diff', 'D', 'x^3*sin(x)', None),
    ('integrate', 'I', 'x*e^x', None),
    ('parts', 'I', 'e^x*sin(x)', None),
    ('solve', 'Q', 'x^2-5x+6', '2, 3'),
    ('factor', 'F', 'x^3-6x^2+11x-6', None),
)

TOOLS = (
    ('mpure', 'A', 'Counterexample f>0', 'n^2-5n+3,1,10', 'counterexample n = 1'),
    ('mcalc', 'G', "Derivative f' and f''", 'x^3-2x+1', '3*x^2-2'),
    ('mstat', 'K', 'Simple random sample', '20,5', '5 from 1..20'),
    ('mmech', 'P', 'km/h to m/s', '72', 'v = 20 m/s'),
    ('fcore', 'P', 'Induction: sum', 'r^3, n^2(n+1)^2/4', 'Proved for all n >= 1'),
    ('fcalc', 'C', 'Integral to infinity', '1/x^2,1', 'integral = 1'),
    ('fmech', 'D', 'Name from M,L,T', '1,1,-2', 'M L T^-2'),
    ('fstat', 'D', 'DRV from table', '0,0.1,1,0.2,2,0.3,3,0.4', 'E(X) = 2'),
    ('falgo', 'A', 'Bubble sort', '3,1,2', 'sorted: 1 2 3'),
    ('fnum', 'U', 'Absolute/rel error', '22/7,pi', 'error = 0.00126'),
    ('fxpure', 'R', 'u(n+1) = a u(n)', '0.5, 8', 'u(n) = 8*(1/2)^n'),
    ('ffpt', 'C', 'Limit x -> a', 'sin(x)/x,0', 'limit = 1'),
)

def maths():
    import caslex
    import caseng
    import cascalc
    import caspoly
    import cassolve
    status('engine')
    slow = ''
    for name, op, text, want in ENGINE:
        tree = caslex.parse(text)
        res = [None]

        def go():
            if op == 'S':
                res[0] = caseng.tostr(caseng.simplify(tree))
            elif op == 'D':
                res[0] = caseng.tostr(cascalc.tidy(caseng.diff(tree)))
            elif op == 'I':
                r = cascalc.integ(tree)
                res[0] = None if r is None else caseng.tostr(r)
            elif op == 'Q':
                r = cassolve.solve_exact(tree, 'x')
                res[0] = ', '.join([caseng.tostr(x) for x in r]) if r else None
            else:
                r = caspoly.factor(tree)
                res[0] = None if r is None else caseng.tostr(r)
        try:
            t = ms(go)
            ok('engine ' + name, res[0] is not None and (want is None or res[0] == want), res[0])
            slow += name + ' ' + fms(t) + '  '
        except Exception as e:
            ok('engine ' + name, False, type(e).__name__ + ' ' + str(e)[:30])
        if len(slow) > 40:
            say(slow)
            slow = ''
    if slow:
        say(slow)
    import casutil
    status('tools')
    worst = 0
    for mod, code, label, text, needle in TOOLS:
        fn = None
        spec = None
        try:
            for c, t, tools in __import__(mod).SECTIONS:
                if c == code:
                    for tl in tools:
                        if tl[0] == label:
                            spec = tl[1]
                            fn = tl[2]
            vals = casutil.convert(spec, text)
            out = ['']

            def go():
                out[0] = _flat(casutil.call_tool(fn, vals))
            t = ms(go)
            if t is not None and t > worst:
                worst = t
            ok(mod + ' ' + label, needle in out[0], out[0][:40])
        except Exception as e:
            ok(mod + ' ' + label, False, type(e).__name__ + ' ' + str(e)[:30])
    tools = 0
    for m in MODS[13:]:
        for c, t, tl in __import__(m).SECTIONS:
            tools += len(tl)
    say('tools ' + str(tools) + ' in 12 modules, slowest case ' + fms(worst if CLK else None) + 'ms')

# ---- 5 editor + screens -------------------------------------------------------------

def editor():
    import nat
    import casutil
    import caslex
    status('editor')
    ed = nat.Ed()
    for k in (81, 42, 83, 25, 84, 43, 82):      # 1 [frac] 3 -> + [sqrt] 2
        nat.typed(ed, k, False, False) if k != 25 else ed.right()
    txt = nat.lin(ed.root)
    v = casutil.fmt(casutil.ev(caslex.parse(txt)))
    ok('editor 1/3+sqrt2', v == '1.75', txt + ' = ' + v)
    ed = nat.Ed()
    for k in (82, 45, 84, 46, 81):              # 2 [x^2] + [e^] 1
        nat.typed(ed, k, False, False)
    ok('editor x^2 e^', nat.lin(ed.root) == '2^2+e^1', nat.lin(ed.root))

def screens():
    import casui
    import nat
    import caslex
    status('screens')
    say('home grid ' + fms(ms(lambda: casui._draw_grid('Maths Toolkit', 'AQA', casui.HOME_TILES, 5), 2)) + 'ms')
    tiles = [(t, casui.badge(c, casui.ACC)) for c, t, m in casui.MATHS]
    say('section grid ' + fms(ms(lambda: casui._draw_grid('Maths', None, tiles, 1), 2)) + 'ms')
    opts = ['Tool number ' + str(i) for i in range(20)]
    say('list menu ' + fms(ms(lambda: casui._draw_menu('B Algebra', opts, 3, 0, 'EXE'), 3)) + 'ms')
    while casui.HIST:
        casui.HIST.pop()
    for text in ('((1)/(3))+sqrt(2)', '2^(10)', '(2+3i)/(1-i)'):
        e = [nat.from_text(text), casui._forms(text), 0]
        casui.HIST.append(e)
    casui.CALC.clear()
    casui.CALC['fresh'] = True
    ed = nat.Ed()
    say('calc screen ' + fms(ms(lambda: casui._draw_calc(ed, False, False), 2)) + 'ms')
    ed = nat.Ed()
    for k in (81, 42, 83, 25, 84, 43, 82):
        nat.typed(ed, k, False, False) if k != 25 else ed.right()
    say('editor ' + fms(ms(lambda: casui._draw_input('Quadratic', 'a,b,c', ed, False, False, ['a', 'b', 'c']), 3)) + 'ms')
    lines = ['x = 1/2 + i*sqrt(3)/2', ('m', caslex.parse('(1+sqrt(3)i)/2')),
             ('w', 'disc = b^2 - 4ac = -3'), ('!', 'no real roots')]
    say('result ' + fms(ms(lambda: casui._draw_result('Quadratic', '1,-1,1', casui._blocks(lines, 1), 0, 1, True), 3)) + 'ms')
    while casui.HIST:
        casui.HIST.pop()
    casui.CALC.clear()

# ---- run ------------------------------------------------------------------------------

def page():
    clear_screen()
    y = 2
    i = 0
    pages = []
    cur = []
    for s in OUT:
        cur.append(s)
        if len(cur) == 14:
            pages.append(cur)
            cur = []
    if cur:
        pages.append(cur)
    n = 0
    for pg in pages:
        clear_screen()
        draw_string(4, 2, 'hwtest ' + str(n + 1) + '/' + str(len(pages)) + '   EXE next', (40, 120, 220), 'small')
        y = 16
        for s in pg:
            draw_string(4, y, s[:62], (200, 40, 40) if s.startswith('FAIL') else (0, 0, 0), 'small')
            y += 12
        show_screen()
        while getkey() in (95, 24):
            pass
        k = None
        while k not in (95, 24, 22):
            k = getkey()
        if k == 22:
            return
        n += 1

def main():
    for step in (platform, screen, loading, maths, editor, screens):
        try:
            step()
        except Exception as e:
            BAD.append(step.__name__ + ' crashed: ' + type(e).__name__ + ' ' + str(e)[:40])
    say('checks ' + str(N[0]) + '  failed ' + str(len(BAD)) + '  mem ' + mem())
    for b in BAD:
        say('FAIL ' + b)
    try:
        f = open('hwlog.txt', 'w')
        f.write('\n'.join(OUT) + '\n')
        f.close()
    except Exception:
        pass
    page()

main()
