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
plot.run = lambda *a, **k: None
casutil.pick = lambda *a, **k: None
casutil.ask = lambda *a, **k: None

FAILS = []
COUNT = [0]

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
    check('(-8)^(1/3) complex', abs(ev('(-8)^(1/3)') - complex(1, 1.7320508)) < 1e-6)
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

def casrender_ok():
    import casrender
    box = casrender.build(caslex.parse('(2+3i)/(1-i)'), 0)
    w, a, d = casrender.measure(box)
    return w > 0 and a > 0

MODULES = ['mpure', 'mcalc', 'mstat', 'mmech', 'fcore', 'fcalc', 'fmech', 'fstat']

if __name__ == '__main__':
    only = sys.argv[1:]
    engine()
    for mname in (only or MODULES):
        module_cases(mname)
    for f in FAILS:
        print('FAIL  ' + f)
    print(str(COUNT[0]) + ' checks, ' + str(len(FAILS)) + ' failures')
    sys.exit(1 if FAILS else 0)
