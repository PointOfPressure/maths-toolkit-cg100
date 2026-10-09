# Runs the engine checks, then every CASES entry of every tests_<module>.py
# through the real field parser. A tool with no case fails the suite.
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) or "."
sys.path.insert(0, HERE)

import caslex
import caseng
import cascalc
import caspoly
import casutil
import plot
PLOT_RUN = plot.run
plot.run = lambda *a, **k: None
casutil.pick = lambda *a, **k: None
casutil.ask = lambda *a, **k: None

FAILS = []
COUNT = [0]
PENDING = [False]

def check(label, cond, detail=''):
    COUNT[0] += 1
    if not cond:
        FAILS.append(label + ('  [' + str(detail) + ']' if detail != '' else ''))

def flat(lines):
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            if ln[0] in ('m', 'mw'):
                out.append(caseng.tostr(ln[1]))
            else:
                out.append(str(ln[1]))
        else:
            out.append(str(ln))
    return out

def run_case(tools, label, text, needles, code=''):
    fn = None
    spec = None
    for t in tools:
        if t[0] == label:
            spec = t[1]
            fn = t[2]
    if fn is None:
        check(code + ' ' + label + ': tool exists', False, 'no such tool')
        return
    try:
        vals = casutil.convert(spec, text)
    except ValueError as e:
        check(code + ' ' + label + ' <' + text + '>: parses', False, str(e))
        return
    lines = casutil.call_tool(fn, vals)
    again = casutil.call_tool(fn, vals)
    check(code + ' ' + label + ' <' + text + '>: pure', flat(lines) == flat(again))
    text_out = '\n'.join(flat(lines))
    for nd in needles:
        check(code + ' ' + label + ' <' + text + '>: has ' + repr(nd), nd in text_out,
              text_out.replace('\n', ' | ')[:300])

def module_cases(modname):
    try:
        mod = __import__(modname)
    except Exception as e:
        check(modname + ' imports', False, repr(e))
        return
    tname = 'tests_' + modname
    try:
        tmod = __import__(tname)
        cases = tmod.CASES
    except Exception as e:
        check(tname + ' loads', False, repr(e))
        cases = []
    # ENGINE_PENDING: mark-scheme cases waiting on an engine fix; skipped
    # unless run with --pending
    pending = getattr(tmod, 'ENGINE_PENDING', []) if cases else []
    if PENDING[0]:
        cases = pending
    seen = {}
    for code, title, tools in mod.SECTIONS:
        check(modname + ' section ' + code + ' has tools', len(tools) > 0)
        for label, spec, fn in tools:
            check(modname + ' label fits: ' + label, len(label) <= 24, len(label))
            check(modname + ' spec parses: ' + spec, casutil.fields_of(spec) != [] or spec == '')
            key = code + '/' + label
            check(modname + ' unique label ' + key, key not in seen)
            seen[key] = (tools, code)
    covered = {}
    for c in cases:
        code, label, text, needles = c
        key = code + '/' + label
        if key not in seen:
            check(modname + ' case names a real tool: ' + key, False)
            continue
        covered[key] = True
        run_case(seen[key][0], label, text, needles, code)
    if PENDING[0]:
        return
    for key in seen:
        check(modname + ' has a case for ' + key, key in covered)

def engine():
    def sstr(e):
        return caseng.tostr(caseng.simplify(caslex.parse(e)))
    def ev(e, x=0.0):
        return caseng.evalf(caslex.parse(e), x)
    check('parse i', ev('i*i') == -1)
    check('complex product', ev('(2+3i)(1-i)') == complex(5, 1))
    check('complex division', ev('2i/(1+i)') == complex(1, 1))
    check('sqrt(-4)', ev('sqrt(-4)') == 2j and sstr('sqrt(-4)') == '2i')
    check('sqrt(-12)', sstr('sqrt(-12)') == '2i*sqrt(3)')
    check('mod/arg/conj', ev('mod(3+4i)') == 5 and abs(ev('arg(i)') - 1.5707963) < 1e-6 and ev('conj(2-i)') == complex(2, 1))
    check('re/im', ev('re(2-i)') == 2 and ev('im(2-i)') == -1)
    check('exp(i pi)', abs(ev('exp(i*pi)') + 1) < 1e-9)
    check('(1+i)^8', ev('(1+i)^8') == 16)
    check('(-8)^(1/3) real, as on the calculator', ev('(-8)^(1/3)') == -2 and ev('cbrt(-27)') == -3)
    check('(-8)^(1/2) complex', abs(ev('(-8)^(1/2)') - complex(0, 2.8284271)) < 1e-6)
    check('nCr key 10C4', ev('1/10C4') == 1.0 / 210 and ev('5P2') == 20 and ev('2C4') == 0)
    check('pi symbolic', sstr('pi/4') == 'pi/4' and abs(ev('pi/4') - 0.785398163) < 1e-9)
    check('e symbolic', abs(ev('e^2') - 7.389056) < 1e-5 and sstr('e^x') == 'e^(x)')
    check('exact sin', sstr('sin(pi/3)') == 'sqrt(3)/2')
    check('exact cos', sstr('cos(2pi/3)') == '-1/2')
    check('exact tan', sstr('tan(-pi/6)') == '-sqrt(3)/3' and sstr('tan(pi/4)') == '1')
    check('exact sin 5pi/6', sstr('sin(5pi/6)') == '1/2')
    check('exact cos pi', sstr('cos(pi)') == '-1')
    check('tan pi/2 unfolded', sstr('tan(pi/2)') == 'tan(pi/2)')
    check('non standard angle unfolded', sstr('sin(pi/12)') == 'sin(pi/12)')
    check('surds', sstr('sqrt(8)') == '2*sqrt(2)')
    check('fractions', sstr('2/6') == '1/3')
    check('ln e^2', sstr('ln(e^2)') == '2')
    d = lambda e: caseng.tostr(cascalc.tidy(caseng.diff(caslex.parse(e))))
    it = lambda e: caseng.tostr(cascalc.tidy(cascalc.integ(caslex.parse(e))))
    check('diff e^(2x)', d('e^(2x)') == '2*e^(2*x)')
    check('diff x^3 sin x', d('x^3*sin(x)') == 'cos(x)*x^3+3*sin(x)*x^2')
    check('int e^(3x)', it('e^(3x)') == 'e^(3*x)/3')
    check('int sin(pi x)', it('sin(pi*x)') == '-cos(pi*x)/pi')
    check('int x e^x', it('x*e^x') == 'e^(x)*x-e^(x)')
    check('factor', caseng.tostr(caspoly.factor(caslex.parse('x^2-5x+6'))) == '(x-2)*(x-3)')
    check('exactstr', caseng.exactstr(0.8660254037844386) == 'sqrt(3)/2' and caseng.exactstr(2.0943951023931953) == '2pi/3')
    check('fmt', casutil.fmt(1234.5, 3) == '1230' and casutil.fmt(0.5) == '1/2' and casutil.fmt(complex(2, -3)) == '2-3i')
    check('fmt full', casutil._sf(1.0 / 3, 10) == '0.3333333333')
    check('solve', [round(r, 6) for r in cascalc.solve(caslex.parse('x^2-pi^2'))] == [-3.141593, 3.141593])
    check('render complex', casrender_ok())
    # canonical form added by the CAS engine upgrade
    check('exact rational sum', sstr('1/3+1/6') == '1/2')
    check('decimal to fraction', sstr('0.25') == '1/4')
    check('ordered by degree', sstr('1-2x+3x^2') == '3*x^2-2*x+1')
    check('powers combined', sstr('x^(1/2)*x^(3/2)') == 'x^2')
    check('negative power', sstr('x^(-2)') == '1/x^2')
    check('rational cancelled', sstr('(x^2-1)/(x-1)') == 'x+1')
    check('surd rationalised', sstr('1/sqrt(2)') == 'sqrt(2)/2')
    check('pythagoras', sstr('sin(x)^2+cos(x)^2') == '1')
    check('ln abs printing', caseng.tostr(caslex.parse('ln(abs(x))')) == 'ln(|x|)')
    check('complex exact quotient', sstr('(2+3i)/(1-i)') == '-1/2+5i/2')
    check('modulus rule', sstr('abs(2x)') == '2*|x|')
    check('factorial ratio', sstr('x!/(x-1)!') == 'x')

def eq_fields():
    # '=' in a tool field: l = r is l - r where the tool solves or takes an
    # equation; 'y =' / 'f(x) =' names the field; anything else is an error
    def bad(text):
        try:
            caslex.parse(text)
        except ValueError as e:
            return str(e)
        return None
    check('lexer rejects =', bad('x^2-4=0') == "cannot read '='")
    check('lexer rejects < > ? $', bad('x<1') and bad('x>1') and bad('?') and bad('2$'))
    check('eq_text l=r', casutil.eq_text('x^2=4', 'f(x)') == '(x^2)-(4)')
    check('eq_text l=0', casutil.eq_text('x^2-4=0', 'f(x)') == 'x^2-4')
    check('eq_text y=', casutil.eq_text('y = x^2', 'f(x)', False) == ' x^2')
    check('eq_text f(x)=', casutil.eq_text('f(x)=x^2', 'f(x)', False) == 'x^2')
    check('eq_text y in F(xy)', casutil.eq_text('y=x^2', 'F(xy)') == '(y)-(x^2)')
    for t in ('x=1=2', 'x^2=4'):
        try:
            casutil.eq_text(t, 'f(x)', False)
            check('eq_text refuses ' + t, False)
        except ValueError:
            check('eq_text refuses ' + t, True)
    import tests_pastpapers
    import casui
    o = tests_pastpapers.output
    check('= in Factorise', '= 0 at x = -2, 2' in o('mpure:B', 'Factorise', 'x^2-4=0'))
    check('= in Implicit dy/dx', 'dy/dx = -3/4' in o('mcalc:G', 'Implicit dy/dx', 'x^2+y^2=25,3,4'))
    check('= in Newton-Raphson', 'x = 1.4142136' in o('mcalc:I', 'Newton-Raphson', 'x^2=2,1'))
    check('= in Solve trig', 'x = 30 deg' in o('mpure:E', 'Solve trig eqn (deg)', 'sin(x)=1/2,0,90', deg=True))
    check('= in a function field', "no '=' in f(x)" in o('mcalc:G', 'Stationary points', 'x^3=3x'))
    check('y = in a function field', 'min at (1, -2)' in o('mcalc:G', 'Stationary points', 'y=x^3-3x'))
    check('< in a field', "cannot read '<'" in o('mpure:B', 'Factorise', 'x^2<4'))
    check('Graph y = f', casui._parse_eq('y = x^2', 'f(x)')[0] == ' x^2')
    check('CAS l = r', casui._parse_eq('x^2=4')[0] == '(x^2)-(4)')
    check('Calculate refuses =', casui._forms('2=2')[0] == ('!', "cannot read '='"))
    # every tool with an expression field, through its own first case
    for modname in MODULES:
        mod = __import__(modname)
        first = {}
        for c in __import__('tests_' + modname).CASES:
            first.setdefault(c[0] + '/' + c[1], c[2])
        for code, title, tools in mod.SECTIONS:
            for label, spec, fn in tools:
                text = first.get(code + '/' + label)
                fields = casutil.fields_of(spec)
                if text is None or not fields or fields[0][1] not in ('e', 'q'):
                    continue
                parts = casutil.split_values(text)
                if not parts or '=' in parts[0]:
                    continue
                name, kind = fields[0][0], fields[0][1]
                key = modname + ' ' + code + '/' + label + ' <' + text + '>'
                want = '\n'.join(flat(casutil.call_tool(fn, casutil.convert(spec, text))))
                def out(first_part):
                    vals = casutil.convert(spec, ','.join([first_part] + parts[1:]))
                    return '\n'.join(flat(casutil.call_tool(fn, vals)))
                if casutil._names('y', name):
                    check(key + ': y = f', out('y=' + parts[0]) == want)
                if kind == 'q':
                    check(key + ': f = 0', out(parts[0] + '=0') == want)
                else:
                    try:
                        out('(' + parts[0] + ')+1=1')
                        check(key + ': = refused', False)
                    except ValueError as e:
                        check(key + ': = refused', "'='" in str(e), str(e))

def home_keys():
    # HOME and memory: nothing may end main() with a dead screen showing
    import casui
    import casioplot
    import font
    check('font tables built at import', sorted(font._B.keys()) == ['large', 'medium', 'small'])
    saved = (casui.grid, casui.flash, casui.wait_key, casui.wait_release)
    def script(steps):
        # steps: what each grid() call does in turn
        it = list(steps)
        def grid(title, tiles, sel=0, right=None):
            s = it.pop(0)
            if isinstance(s, BaseException) or s is MemoryError:
                raise s
            return s
        return grid
    shown = []
    def flash_home(msg):
        shown.append(msg)
        raise casui.Home()
    try:
        casui.wait_release = lambda: None
        # MemoryError, then HOME pressed on the popup: back to the grid, not out
        casui.grid = script([MemoryError(), -1])
        casui.flash = flash_home
        try:
            casui.main()
            ok = True
        except BaseException as e:
            ok = repr(e)
        check('HOME on the out-of-memory popup stays in main', ok is True, ok)
        check('out-of-memory popup says restart', shown and 'run maths.py again' in shown[0], shown)
        # the popup itself running out of memory: dropped, grid again
        def flash_oom(msg):
            raise MemoryError()
        casui.grid = script([MemoryError(), -1])
        casui.flash = flash_oom
        try:
            casui.main()
            ok = True
        except BaseException as e:
            ok = repr(e)
        check('MemoryError inside the popup stays in main', ok is True, ok)
        # an error inside the popup is not shown again forever
        n = [0]
        def flash_err(msg):
            n[0] += 1
            raise ValueError('x')
        casui.grid = script([ValueError('boom'), -1])
        casui.flash = flash_err
        casui.main()
        check('error inside the popup shown once', n[0] == 1, n[0])
        # the home grid itself out of memory twice: bare message, clean exit
        casui.grid = script([MemoryError(), MemoryError(), -1])
        casui.flash = lambda msg: None
        casui.wait_key = lambda: casui.EXE
        try:
            casui.main()
            ok = True
        except BaseException as e:
            ok = repr(e)
        check('home grid out of memory ends cleanly', ok is True, ok)
        # Idle anywhere ends main quietly
        casui.grid = script([casui.Idle()])
        try:
            casui.main()
            ok = True
        except BaseException as e:
            ok = repr(e)
        check('Idle ends main', ok is True, ok)
    finally:
        casui.grid, casui.flash, casui.wait_key, casui.wait_release = saved
    # messages for a full heap and for a half-loaded module
    check('errtext memory', 'Out of memory' in casui.errtext(MemoryError()))
    check('errtext half-loaded module',
          'did not finish loading' in casui.errtext(AttributeError("'module' object has no attribute 'Ed'")))
    check('errtext other', casui.errtext(ValueError('bad')) == 'error: bad')
    def oom():
        raise MemoryError()
    check('call_tool out of memory', 'Out of memory' in str(casutil.call_tool(oom, [])))
    # label wraps are capped
    casui._WRAPS.clear()
    for i in range(300):
        casui._label_lines('label number ' + str(i), 118)
    check('wrap cache capped', len(casui._WRAPS) <= 120, len(casui._WRAPS))
    casui._WRAPS.clear()
    # a held HOME during simplify / evaluation unwinds to the home grid
    real = casioplot.getkey
    big = caslex.parse('(x+1)^12*(x-2)^7+sin(x)^2*(x+3)^5')
    try:
        casioplot.getkey = lambda: 12
        try:
            for i in range(300):
                caseng.simplify(big)
            ok = 'no Home'
        except casui.Home:
            ok = True
        check('HOME interrupts simplify', ok is True, ok)
        try:
            for i in range(100):
                casutil.evx(big, 0.5)
            ok = 'no Home'
        except casui.Home:
            ok = True
        check('HOME interrupts evaluation', ok is True, ok)
    finally:
        casioplot.getkey = real
        caseng._TICK[0] = 0
    check('no HOME: simplify runs', caseng.tostr(caseng.simplify(caslex.parse('x+x'))) == '2*x')
    # the graph screen passes HOME on (it used to redraw the graph) and lets go
    # of its sample memo when it closes
    try:
        casui.wait_key = lambda: casui.HOME
        casui.wait_release = lambda: None
        try:
            PLOT_RUN([caslex.parse('x^2')], -6.0, 6.0, 'y', 'y = x^2')
            ok = 'returned'
        except casui.Home:
            ok = True
        check('HOME in a graph goes home', ok is True, ok)
        check('graph memo freed', plot._YC[0] is None and plot._YC[1] == [], plot._YC[0])
    finally:
        casui.grid, casui.flash, casui.wait_key, casui.wait_release = saved
    # CAS ops show Busy before they start
    marks = []
    rb = (casui.busy, casui.result)
    try:
        casui.busy = lambda: marks.append('busy')
        casui.result = lambda *a: marks.append('result')
        casui._run_op(6, caslex.parse('x+x'), 'x+x')
    finally:
        casui.busy, casui.result = rb
    check('CAS op shows Busy first', marks == ['busy', 'result'], marks)

def further_switch():
    # FURTHER = False in the launchers hides Further Maths from every menu
    import casui
    import nat
    import tn_fb
    src = open(os.path.join(HERE, 'maths.py')).read()
    check('launchers match', src == open(os.path.join(HERE, 'module.py')).read())
    check('launcher: Further off by default', 'FURTHER = False' in src and
          'casui.main(further=FURTHER)' in src, src)
    seen = []
    saved = (casui.grid, casui.menu, casui.pick, casui.remembered, casui.FURTHER_ON)
    def grid(title, tiles, sel=0, right=None):
        seen.append([t[0] for t in tiles])
        return -1
    try:
        casui.grid = grid
        casui.main()
        casui.main(further=True)
        check('home without Further', seen[0] == ['Calculate', 'CAS', 'Graph', 'Solve', 'Maths',
                                                  'Notes', 'Settings'], seen[0])
        check('home with Further', 'Further' in seen[1] and len(seen[1]) == 8, seen[1])
        for flag in (False, True):
            casui.FURTHER_ON = flag
            got = []
            def menu(title, labels, sel=0, hint=None):
                got.append(list(labels))
                return labels.index('limit x -> a') if 'limit x -> a' in labels else -1
            casui.menu = menu
            casui.pick = menu
            op = casui.pick_shown('Tools', casui.CAS_OPS, casui.OPS_FURTHER, 0)
            check('CAS ops Maclaurin shown only with Further ' + str(flag),
                  ('series (Maclaurin)' in got[0]) == flag, got[0])
            check('CAS op picked by label ' + str(flag), casui.CAS_OPS[op] == 'limit x -> a', op)
            casui.pick_shown('Symbols', nat.SYMBOLS, casui.SYM_FURTHER, 0, casui.pick)
            check('symbols: complex and hyperbolic only with Further ' + str(flag),
                  (('sinh(' in got[1]) and ('i' in got[1])) == flag and 'pi' in got[1], got[1])
            labels = []
            def remembered(title, opts):
                labels.append(list(opts))
                return -1
            casui.remembered = remembered
            casui.notes_section()
            casui._booklet('Formula booklet')
            check('notes papers: Further only with Further ' + str(flag),
                  ('Core Pure Y420' in labels[0]) == flag and 'Pure 7357' in labels[0], labels[0])
            check('booklet: Further pages only with Further ' + str(flag),
                  ('Arc length' in labels[1]) == flag and 'Binomial expansion' in labels[1] and
                  'Not in the booklet' in labels[1], labels[1])
    finally:
        casui.grid, casui.menu, casui.pick, casui.remembered, casui.FURTHER_ON = saved
    for t in casui.FB_FURTHER:
        check('booklet page exists: ' + t, t in tn_fb.T)
    for t in casui.SYM_FURTHER:
        check('symbol exists: ' + t, t in nat.SYMBOLS)
    for t in casui.OPS_FURTHER:
        check('CAS op exists: ' + t, t in casui.CAS_OPS)
    for t in casui.NOTES_FURTHER:
        check('notes paper exists: ' + t, t in [p[0] for p in casui.NOTE_PAPERS])

def casrender_ok():
    import casrender
    box = casrender.build(caslex.parse('(2+3i)/(1-i)'), 0)
    w, a, d = casrender.measure(box)
    return w > 0 and a > 0

MODULES = ['mpure', 'mcalc', 'mstat', 'mmech',
           'fcore', 'fcalc', 'fmech', 'fstat', 'falgo', 'fnum', 'fxpure', 'ffpt']

def cas_engine():
    import tests_cas
    tests_cas.run(check)
    import tests_nat
    tests_nat.run(check)
    import tests_notes
    tests_notes.run(check)
    import tests_pastpapers
    tests_pastpapers.run(check)
    import tests_pastpapers_aqa
    tests_pastpapers_aqa.run(check)
    import tests_tex
    tests_tex.run(check)
    _depth_check()

def _depth_check():
    # a 40-token expression must stay well under the device's 92-frame ceiling
    expr = '(3x^2+2x-1)*(x-4)/(x^2-16)+sin(2x+pi/3)*e^(-x)-sqrt(12)/(1+sqrt(3))'
    tree = caslex.parse(expr)
    check('cas token count', len(caslex.tokenize(expr)) >= 40)
    worst = [0]

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
    sys.setprofile(prof)
    try:
        out = caseng.simplify(tree)
        caseng.tostr(out)
        cascalc.tidy(caseng.diff(tree))
    finally:
        sys.setprofile(None)
    check('cas recursion under 40 frames', worst[0] - base < 40, worst[0] - base)

if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if a != '--pending']
    if '--pending' in sys.argv:
        # only the ENGINE_PENDING cases: see which engine fixes have landed
        PENDING[0] = True
        for mname in (only or MODULES):
            module_cases(mname)
        for f in FAILS:
            print('PENDING  ' + f)
        print(str(COUNT[0]) + ' pending checks, ' + str(len(FAILS)) +
              ' still failing')
        sys.exit(0)
    engine()
    eq_fields()
    home_keys()
    further_switch()
    cas_engine()
    for mname in (only or MODULES):
        module_cases(mname)
    for f in FAILS:
        print('FAIL  ' + f)
    print(str(COUNT[0]) + ' checks, ' + str(len(FAILS)) + ' failures')
    sys.exit(1 if FAILS else 0)
