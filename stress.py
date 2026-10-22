# Drives every tool of every section module with a bank of odd inputs.
# Anything other than a clean result or a ValueError caveat is a failure.
import sys
import tests
import casutil

BANK = ['0', '1', '-1', '2', '1e9', '1e-9', '0.5', '3', '7', '-2.5']

def _inputs(spec):
    out = []
    n = 0
    lst = False
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind == 'n':
            n += 1
        elif kind == 'e':
            n += 1
        elif kind == 'l':
            lst = True
        elif kind == 'v':
            n += cnt
        elif kind == 'm':
            n += cnt[0] * cnt[1]
    for base in BANK:
        vals = []
        i = 0
        for name, kind, cnt, opt in casutil.fields_of(spec):
            if kind == 'e':
                vals.append('x^2-' + base)
            elif kind == 'l':
                vals.extend([base, '1', '2', '3'])
            elif kind == 'v':
                vals.extend([base] * cnt)
            elif kind == 'm':
                vals.extend([base] * (cnt[0] * cnt[1]))
            else:
                vals.append(base)
        out.append(','.join(vals))
    out.append('')
    out.append('1')
    out.append(','.join(['x'] * (n + 1)))
    out.append(','.join(['2+3i'] * (n + 1)))
    return out

def main(mods):
    bad = 0
    count = 0
    for mname in mods:
        mod = __import__(mname)
        for code, title, tools in mod.SECTIONS:
            for label, spec, fn in tools:
                for text in _inputs(spec):
                    count += 1
                    try:
                        vals = casutil.convert(spec, text)
                    except ValueError:
                        continue
                    lines = casutil.call_tool(fn, vals)
                    for ln in lines:
                        if isinstance(ln, tuple) and ln[0] == '!' and ln[1].startswith('error: '):
                            bad += 1
                            print(mname + ' ' + label + ' <' + text + '>: ' + ln[1])
                            break
    print(str(count) + ' runs, ' + str(bad) + ' crashes')
    return bad

# the redesign: odd things typed into a topic, every action that is offered
TYPED = ['sin(x)=2', 'tan(x)=0', 'sin(x)cos(x)=0', 'sin(x^2)=0.5', 'sin(x)+cos(2x)+tan(3x)=1',
         'sec(x)=0', 'sin(x)=sin(x)', 'sin(x)^2+cos(x)^2', 'cos(x)=k', 'sin(2x)=cos(x)', 'tan(x)=1/0',
         '0', '1/0', 'x/x', 'x^2=-1', 'ln(0)', 'x^20+1', 'e^(e^x)=2', '2^x=-1',
         'logb(1,x)=2', 'sqrt(-x)=3', 'abs(x)=-1', '1/(x-x)', 'x^2+y^2', 'k', 'x=x',
         'pi^x=e', '0^x=0', 'x^x=4', '(x-1)^-1', 'x^(1/3)=-2', '1e9x^2+1e-9', '2^x+2^(2x)',
         'ln(x)=ln(-x)', 'x+y+z=1', 'sin(x)^2+cos(x)^2', 'log(x)^2-3log(x)+2=0',
         'y=1/x', 'y=x^3', 'x>x', '2<1', '(2+3i)x=1', 'x^2+(k+1)x+k', '0.1x^2-0.3x=0',
         'e^x=0', 'x^2=4', 'sqrt(x)=x-2', 'x^4+4', '1/(x^2+1)', 'y=e^(2x)+e^x',
         'dy/dx=0', 'dy/dx=y', 'dy/dx=x+y', 'dy/dx=sin(x)/y', 'dy/dx=1/(x-1)', 'tan(x)', '1/x',
         'abs(x)', 'x^x', 'e^(x^2)', 'ln(ln(x))']
PAIRS = [['x=1', 'x=2'], ['x+y=1', 'x+y=1'], ['x+y=1', 'x+y=2'], ['x^2+y^2=1', 'x^2+y^2=4'],
         ['0', '0'], ['x', 'y'], ['y=x', 'y=x^2'], ['e^x', 'ln(x)']]
STOCK = ['2', '3', '1', '5', '']
NEWT = ('trig',)     # the stage 2 topics, typed rows as the others
BOXES = [
    ('trig', 'Triangle', ['1', '2', '5', '', '', '', '']), ('trig', 'Triangle', ['', '', '', '30', '40', '50', '']),
    ('trig', 'Triangle', ['3', '', '', '', '', '', '']), ('trig', 'Triangle', ['3', '4', '', '', '', '', '20']),
    ('trig', 'Triangle', ['3', '4', '', '', '', '', '6']), ('trig', 'Triangle', ['2', '5', '', '30', '', '', '']),
    ('trig', 'Triangle', ['5', '2', '', '30', '', '', '']), ('trig', 'Triangle', ['0', '-1', 'k', '', '', '', '']),
    ('trig', 'Triangle', ['3', '', '', '100', '90', '', '']), ('trig', 'Triangle', ['?', '?', '?', '?', '?', '?', '?']),
    ('trig', 'Arc and sector', ['', '', '', '', '', '']), ('trig', 'Arc and sector', ['5', '', '', '', '', '']),
    ('trig', 'Arc and sector', ['5', '9', '', '', '', '']), ('trig', 'Arc and sector', ['', '', '', '10', '13', '']),
    ('trig', 'Arc and sector', ['', '', '', '100', '10', '']), ('trig', 'Arc and sector', ['', '', '4', '6', '', '']),
    ('trig', 'Arc and sector', ['k', '1', '', '', '', '']), ('trig', 'Arc and sector', ['2', '', '', '', '3', '?']),
]

def topics():
    import recog
    import acts
    import topic
    import caslex
    import plot
    plot.run = lambda *a, **k: None
    bad = 0
    count = 0
    for rows in [[t] for t in TYPED] + PAIRS:
        F = recog.form(rows)
        if F.err:
            continue
        for tid in ('alg', 'exp', 'calc') + NEWT:
            for label, mod, fn, arg, ask in acts.offers(F, tid):
                vals = None
                if ask:
                    if ask[0] == 'choose':
                        vals = [1]
                    elif ask[0] == 'boxes':
                        continue
                    else:
                        n = sum([ln[1] for ln in ask])
                        vals = [None if not STOCK[i % 5] else caslex.parse(STOCK[i % 5])
                                for i in range(n)]
                count += 1
                lines = topic.engine(mod, fn, F, arg, vals)
                for ln in lines or []:
                    if isinstance(ln, tuple) and ln[0] == '!' and ln[1].startswith('error'):
                        bad += 1
                        print('topic ' + tid + ' ' + label + ' <' + '; '.join(rows) + '>: ' + ln[1])
                        break
    # box forms with impossible, missing and awkward values
    for tid, label, texts in BOXES:
        F = recog.read(tid, [''])
        for o in acts.offers(F, tid):
            if o[0] != label:
                continue
            count += 1
            lines = topic.engine(o[1], o[2], F, o[3], topic.readboxes(o[4][1], texts))
            for ln in lines or []:
                if isinstance(ln, tuple) and ln[0] == '!' and ln[1].startswith('error'):
                    bad += 1
                    print('box ' + tid + ' ' + label + ' ' + repr(texts) + ': ' + ln[1])
                    break
    # Coord geometry: the same points, vertical lines, circles that aren't
    GEO = [([('0', '0'), ('0', '0')], []), ([('1', '1'), ('1', '5')], []), ([('1', '1'), ('4', '1')], []),
           ([('0', '0'), ('1', '1'), ('2', '2')], []), ([], ['x^2+y^2=-4']), ([], ['x^2+y^2=0']),
           ([('5', '5')], ['x^2+y^2=1']), ([('0', '0')], ['x=3']), ([('0', '0')], ['y=2']),
           ([], ['y=x', 'y=x+1']), ([], ['x=1', 'x=2']), ([], ['x^2+y^2=1', 'x^2+y^2=4']),
           ([], ['x=sin(t)', 'y=cos(t)']), ([], ['x=e^t', 'y=e^(2t)']), ([('k', '2'), ('3', 'k')], []),
           ([('1e9', '0'), ('0', '1e-9')], []), ([('2+3i', '0'), ('1', '1')], [])]
    for pts, eqs in GEO:
        F = recog.geo(pts, eqs)
        if F.err:
            continue
        for label, mod, fn, arg, ask in acts.offers(F, 'geo'):
            vals = [caslex.parse('2')] if ask else None
            count += 1
            lines = topic.engine(mod, fn, F, arg, vals)
            for ln in lines or []:
                if isinstance(ln, tuple) and ln[0] == '!' and ln[1].startswith('error'):
                    bad += 1
                    print('geo ' + label + ' ' + repr(pts) + repr(eqs) + ': ' + ln[1])
                    break
    print(str(count) + ' topic actions, ' + str(bad) + ' crashes')
    return bad

if __name__ == '__main__':
    bad = main(sys.argv[1:] or tests.MODULES)
    if not sys.argv[1:]:
        bad += topics()
    sys.exit(1 if bad else 0)
