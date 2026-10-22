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
# the stage 2 topics' own awkward inputs (run through those topics only)
TYPED_NEW = ['u=u', 'u=1/u', 'u=u^2+n', 'u(n+1)=u(n)+1/0', '(1+x)^(1/0)', '(1+x)^100',
             '(2+x)^(-3/2)', 'n!', 'r^r', 'sin(x)=2', 'tan(x)=0', 'sin(x)cos(x)=0', 'sin(x^2)=0.5',
             'sin(x)+cos(2x)+tan(3x)=1', 'sec(x)=0', 'sin(x)=sin(x)', 'sin(x)^2+cos(x)^2', 'cos(x)=k',
             'sin(2x)=cos(x)', 'tan(x)=1/0', 'x=x', 'x=x+1', 'x=1/x', 'x=x^2', '1/(x-1)', 'x^2+1',
             '1, 2, 3', '1,,2', '1, x', 'sqrt(-1-x^2)', '0i+0j', '(0,0)', 'i', '(1,2,3,4)', 'i*j', '(x,y)',
             'k', '(1/0, 2)', 'b(0,0.5)', 'b(5,1)', 'b(5,0)', 'b(1000,0.5)', 'b(2.5,0.3)', 'b(5,2)', 'n(0,0)',
             'n(?,?)', 'n(1,1/0)', 'n(0,1)', '1', '5,5,5,5', '1,2', '1,2,3', 'x,2', 'v=0', 's=1/t', 'a=ln(t)',
             'v=e^(t^2)', 'v=1/(t-1)', 'r=t*i', 'v=j', 'v=sqrt(-t)', 'v=t*i+t*j+t*k']
TYPED = ['(x+y)^3', '0', '1/0', 'x/x', 'x^2=-1', 'ln(0)', 'x^20+1', 'e^(e^x)=2', '2^x=-1',
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
NEWT = ('trig', 'seq', 'num', 'vec', 'stat', 'kin', 'force')     # the stage 2 topics, typed rows as the others
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
    ('seq', 'AP facts', ['', '', '', '', '']), ('seq', 'AP facts', ['1', '0', '?', '', '10']),
    ('seq', 'AP facts', ['1', '1', '0', '', '']), ('seq', 'AP facts', ['1', '2', '1.5', '', '']),
    ('seq', 'AP facts', ['', '', '10', '5', '?']), ('seq', 'AP facts', ['k', '2', '5', '', '?']),
    ('seq', 'GP facts', ['1', '1', '5', '', '?', '?']), ('seq', 'GP facts', ['0', '2', '', '', '', '?']),
    ('seq', 'GP facts', ['2', '-3', '?', '', '1000', '']), ('seq', 'GP facts', ['?', '?', '?', '?', '?', '?']),
    ('seq', 'GP facts', ['', '0.5', '', '', '', '10']), ('seq', 'GP facts', ['3', '', '4', '24', '', '?']),
    ('vec', 'From size, direction', ['', '']), ('vec', 'From size, direction', ['k', '30']),
    ('vec', 'From size, direction', ['0', '0']),
    ('stat', 'From sums', ['0', '5', '3', '']), ('stat', 'From sums', ['5', '10', '1', '']),
    ('stat', 'From sums', ['5', '10', '', '']), ('stat', 'PMCC test', ['2', '10', '5', '1']),
    ('stat', 'PMCC test', ['0.5', '3', '5', '']), ('stat', 'PMCC test', ['0.5', '200', '0.1', '2']),
    ('stat', 'PMCC test', ['0.5', '10', '5', '3']), ('stat', 'Two events', ['', '', '', '', '']),
    ('stat', 'Two events', ['0.9', '0.9', '0.1', '', '']), ('stat', 'Two events', ['2', '0.5', '0.1', '', '']),
    ('stat', 'Two events', ['0.5', '', '', '0.7', '0.4']), ('stat', 'mu, sigma from two', ['1', '0.5', '1', '0.5']),
    ('stat', 'mu, sigma from two', ['1', '0.9', '2', '0.1']), ('stat', 'mu, sigma from two', ['1', '0', '2', '1']),
    ('stat', 'Outlier fences', ['', '', '', '']), ('stat', 'Outlier fences', ['5', '', '3', '2']),
    ('kin', 'SUVAT', ['', '', '', '', '']), ('kin', 'SUVAT', ['1', '0', '0', '?', '']),
    ('kin', 'SUVAT', ['10', '0', '', '0', '?']), ('kin', 'SUVAT', ['1', '?', '?', '?', '1']),
    ('kin', 'SUVAT', ['-5', '1', '', '1', '?']), ('kin', 'SUVAT', ['1', '2', '3', '4', '5']),
    ('kin', 'SUVAT', ['5', '', '', '0', '0']), ('kin', 'Projectile', ['', '', '', '', '', '']),
    ('kin', 'Projectile', ['10', '0', '-5', '', '', '']), ('kin', 'Projectile', ['?', '45', '', '', '', '10']),
    ('kin', 'Projectile', ['?', '45', '', '', '3', '']), ('kin', 'Projectile', ['?', '-30', '', '', '', '10']),
    ('kin', 'Projectile', ['0', '30', '', '', '', '']), ('kin', 'Projectile', ['5', '30', '', '0', '', '']),
]
RAWBOXES = [
    ('force', 'Slope or surface', ['', '', '', '', '', '', '', '']), ('force', 'Slope or surface', ['?', '?', '?', '', '', '?', '', '']),
    ('force', 'Slope or surface', ['5', '90', '', '', '0.5', '', '', '']), ('force', 'Slope or surface', ['5', '30', '', '', '', '?', 'sideways', '']),
    ('force', 'Slope or surface', ['0', '0', '0', '0', '0', '', '', '']), ('force', 'Slope or surface', ['5', '', '1', '', '?', '0', '', '0']),
    ('force', 'Pulley', ['', '', '', '', '', '', '']), ('force', 'Pulley', ['0', '0', '0', '0', '', '', '']),
    ('force', 'Pulley', ['1', '0', '5', '1', '', '', '']), ('force', 'Pulley', ['?', '?', '', '1', '', '', '']),
    ('force', 'Towing', ['', '', '', '', '', '', '', '']), ('force', 'Towing', ['0', '0', '0', '', '', '', '', '']),
    ('force', 'Towing', ['1', '1', '?', '?', '?', '', '', '']), ('force', 'Moments', ['', '', '']),
    ('force', 'Moments', ['5', '', '']), ('force', 'Moments', ['5@1', '?@1, ?@1', '']), ('force', 'Moments', ['a@b', 'c@d', '']),
    ('force', 'Moments', ['5@1', '5@1', '']), ('force', 'Forces', ['', '']), ('force', 'Forces', ['1@0, ?@?', '']),
    ('force', 'Forces', ['3i+4j', '']), ('force', 'Forces', ['3i+4j, ?@0, ?@90', '']), ('force', 'Forces', ['x@y, z', '']),
    ('stat', 'Stratified sample', ['', '']), ('stat', 'Stratified sample', ['10', '0,0']),
    ('stat', 'Stratified sample', ['10', 'a,b']), ('stat', 'Stratified sample', ['10', '5']),
    ('vec', 'Quadrilateral ABCD', ['(0,0)', '(0,0)', '(0,0)', '(0,0)']),
    ('vec', 'Quadrilateral ABCD', ['(0,0)', '(1,1)', '', '(2,3)']),
    ('vec', 'Quadrilateral ABCD', ['(0,0)', '(2,0)', '(3,1)', '(1,1)']), ('vec', 'Quadrilateral ABCD', ['x', 'y', 'z', 'w']),
    ('vec', 'Quadrilateral ABCD', ['(0,0)', '(2,1)', '(4,0)', '(2,-3)']),
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
    for rows in [[t] for t in TYPED + TYPED_NEW] + PAIRS:
        F = recog.form(rows)
        if F.err:
            continue
        for tid in ('alg', 'exp', 'calc') + NEWT:
            if rows[0] in TYPED_NEW and tid not in NEWT:
                continue
            if tid in NEWT:
                F = recog.read(tid, rows)
                if F.err:
                    continue
            for label, mod, fn, arg, ask in acts.offers(F, tid):
                vals = None
                if ask:
                    if ask[0] == 'choose':
                        vals = [1]
                    elif ask[0] == 'boxes':
                        continue
                    elif ask[0] == 'choose+':
                        vals = [2] + [caslex.parse(x) for x in ('3', '20', '5')[:len(ask[2])]]
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
    for tid, label, texts in BOXES + RAWBOXES:
        F = recog.read(tid, [''])
        for o in acts.offers(F, tid):
            if o[0] != label:
                continue
            count += 1
            lines = topic.engine(o[1], o[2], F, o[3], topic.readboxes(o[4][1], texts) if len(o[4]) < 4
                                 else [t or None for t in texts])
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
