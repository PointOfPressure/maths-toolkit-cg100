# Natural-display editor and the static section index. Called by tests.py.
import caslex
import casutil
import casui
import nat

K = {'frac': 42, 'pow': 44, 'sq': 45, 'exp': 46, 'sqrt': 43}

def typed(*keys):
    ed = nat.Ed()
    for k in keys:
        if k == 'R':
            ed.right()
        elif k == 'D':
            ed.dele()
        elif k == 'down':
            ed.vert(False)
        elif isinstance(k, tuple):
            nat.typed(ed, k[1], k[0] == 'shift', k[0] == 'alpha')
        elif k in K:
            nat.typed(ed, K[k], False, False)
        else:
            ed.ins(k)
    return ed

def val(ed):
    return casutil.fmt(casutil.ev(caslex.parse(nat.lin(ed.root))))

def run(check):
    check('nat 1/2 via fraction key', val(typed('1', 'frac', '2')) == '1/2')
    check('nat fraction grabs the term before it', val(typed('1', '+', '3', 'frac', '2')) == '5/2')
    check('nat fraction grab drops outer brackets',
          typed('(', '1', '+', '2', ')', 'frac').root == [['F', ['1', '+', '2'], []]])
    check('nat empty fraction: numerator first', val(typed('frac', '3', 'down', '4')) == '3/4')
    check('nat power over a fraction', val(typed('frac', '1', 'down', '2', 'R', 'sq')) == '1/4')
    check('nat x^2 key', val(typed('3', 'sq', '+', '1')) == '10')
    check('nat power key', val(typed('2', 'pow', '1', '0', 'R', '-', '1')) == '1023')
    check('nat e^ key', nat.lin(typed('exp', '1').root) == 'e^1')
    check('nat plain fraction text', nat.lin(typed('1', 'frac', '3', 'R', 'sq').root) == '(1/3)^2')
    check('nat power of a sum keeps brackets', nat.lin(typed('2', 'pow', 'x', '+', '1').root) == '2^(x+1)')
    check('nat sqrt', val(typed('sqrt', '8')) == '2sqrt(2)')
    check('nat nth root', val(typed(('shift', 43), '3', 'R', '8')) == '2')
    check('nat log base', val(typed(('shift', 44), '2', 'R', '8')) == '3')
    ed = nat.Ed()
    nat.symbol(ed, '|x|')
    ed.ins('-')
    ed.ins('3')
    check('nat modulus', val(ed) == '3')
    check('nat open bracket closes itself', val(typed('sin(', '0')) == '0')
    check('nat empty box detected', nat.empty_hole(typed('1', 'frac').root))
    check('nat no hole when filled', not nat.empty_hole(typed('1', 'frac', '2').root))
    ed = typed('frac', '1', 'down', '2')
    ed.home()
    ed.right()
    ed.dele()
    check('nat DEL at box start unwraps', ed.root == ['1', '/', '2'], repr(ed.root))
    ed = typed('sqrt', '9')
    ed.right()
    ed.dele()
    check('nat DEL enters a filled box', ed.root == [['R', ['9']]] and ed.row == ['9'])
    ed.dele()
    ed.dele()
    check('nat DEL removes an emptied box', ed.root == [], repr(ed.root))
    check('nat unary minus has no spaces', nat._tok('-', ',') == '-' and nat._tok('-', '2') == ' - ')
    ed = typed('1', 'frac', '2')
    w, a, d = nat.measure(ed.root, 0)
    check('nat fraction is taller than a line', a + d > 30, (w, a, d))
    # recalled text rows stay valid linear input
    check('nat text round trip', val(nat.Ed(nat.from_text('(1+2)^2'))) == '9')

    # Calculate keeps exact answers and chains Ans exactly
    casui.ANS[0] = ('n', 0)
    f = casui._forms('((1)/(3))+sqrt(2)')
    check('calc exact first', f[0][0] == 'm', repr(f))
    check('calc decimal form offered', f[-1][1].startswith('1.7475'), repr(f))
    f = casui._forms('ans-sqrt(2)')
    check('calc Ans stays exact', f[0][0] == 'm' and caslex.parse('1/3') is not None and
          casutil.fmt(casutil.ev(f[0][1])) == '1/3', repr(f))
    f = casui._forms('(2+3i)/(1-i)')
    check('calc complex as fractions', f[0][0] == 'm' and f[0][1][0] != 'n', repr(f))
    check('calc bad input', casui._forms('1+')[0][0] == '!')

    # the generated tool index files are current
    import mkindex
    for path, src in mkindex.files():
        check('index file current ' + path, open(path).read() == src)

    # the static section index matches the modules
    for code, title, mod in casui.MATHS:
        check('index ' + mod + ' ' + code, casui._tools(code, title, mod) != [])
    n = 0
    for mod in ('mpure', 'mcalc', 'mstat', 'mmech'):
        n += len(__import__(mod).SECTIONS)
    check('index covers every Maths section', n == len(casui.MATHS), n)
    fmods = {}
    for name, code, secs in casui.FURTHER:
        for c, t, mod in secs:
            check('index ' + mod + ' ' + c, casui._tools(c, t, mod) != [])
            fmods[mod] = fmods.get(mod, 0) + 1
    for mod in fmods:
        check('index covers every ' + mod + ' section', fmods[mod] == len(__import__(mod).SECTIONS))
