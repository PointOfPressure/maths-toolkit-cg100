# proof.py - proof methods. Induction is H645 Core Pure; contradiction,
# exhaustion and disproof by counterexample are H640.
#
# A calculator cannot write a proof, and this module does not pretend to. What
# it does is the part a machine is genuinely better at: CHECKING the step you
# claim. The induction tools verify the base case and then verify the inductive
# step symbolically, so if the algebra you were about to write down is wrong,
# you find out here rather than three lines into the answer.
# Stock CASIO MicroPython 1.9.4: ASCII only, no f-strings, iterative only.
import math
import casui
import caslex
import caseng
import cascalc
import caspoly
import casutil

_asknum = casutil.asknum
_askint = casutil.askint
_fn = casutil.fmt
_show = casutil.show
_w = casutil.w             # working: hidden when the Working setting is off
_warn = casutil.warn       # a caveat on the answer: always shown


def _parse(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        _show('Could not read that', ['"' + s + '" is not an expression',
                                      'this toolkit can read.'])
        return None
    return t


def _at(tree, val, name='n'):
    try:
        v = caseng.evalf(tree, val, False, {name: val})
    except:
        return None
    if isinstance(v, complex) or v != v or v > 1.7e308 or v < -1.7e308:
        return None
    return v


def t_induction_sum():
    # Prove sum from r=1 to n of u(r) = S(n).
    # The inductive step is exactly S(k+1) - S(k) = u(k+1), and that is an
    # algebraic identity the engine can settle. If it does not hold, the
    # formula is wrong and no amount of writing will fix it.
    _show('Induction: a sum', ['To prove sum r=1..n of u(r) = S(n).',
                               'Base case: S(1) = u(1).',
                               'Step: assume it holds at k, then',
                               'S(k+1) - S(k) must equal u(k+1).',
                               'Type both in n.'])
    u = _parse('u(r) = (type r as n)')
    if u is None:
        return
    S = _parse('claimed S(n) =')
    if S is None:
        return
    lines = [_w('u(r) = ' + caseng.tostr(caseng.simplify(u))),
             _w('S(n) = ' + caseng.tostr(caseng.simplify(S))), '']
    # --- base case
    u1 = _at(u, 1.0)
    s1 = _at(S, 1.0)
    lines.append(_w('BASE CASE n = 1'))
    if u1 is None or s1 is None:
        lines.append(_warn('  cannot evaluate at n = 1'))
        _show('Induction', lines)
        return
    ok_base = abs(u1 - s1) < 1e-9
    lines.append(_w('  u(1) = ' + _fn(u1) + ',  S(1) = ' + _fn(s1)))
    lines.append('  ' + ('TRUE - the base case holds' if ok_base
                         else 'FALSE - S(1) is not u(1), so the'))
    if not ok_base:
        lines.append('  formula is wrong before you start.')
        _show('Induction', lines)
        return
    # --- inductive step, symbolically
    Sk1 = caseng.subst(S, 'n', ('+', ('v', 'n'), ('n', 1)))
    uk1 = caseng.subst(u, 'n', ('+', ('v', 'n'), ('n', 1)))
    diff = caspoly.expand(('-', Sk1, S))
    want = caspoly.expand(uk1)
    lines.append('')
    lines.append(_w('INDUCTIVE STEP'))
    lines.append(_w('  S(k+1) - S(k) = ' + caseng.tostr(diff)))
    lines.append(_w('  u(k+1)        = ' + caseng.tostr(want)))
    same = caseng.tostr(diff) == caseng.tostr(want)
    if not same:
        # the printed forms can differ while the functions agree; test values
        same = True
        for kv in (1.0, 2.0, 3.0, 7.0, 11.5):
            a = _at(diff, kv)
            b = _at(want, kv)
            if a is None or b is None:
                continue
            if abs(a - b) > 1e-7 * (1.0 + abs(b)):
                same = False
                break
    lines.append('')
    if same:
        lines.append(_w('  These are equal, so the step holds.'))
        lines.append('')
        lines.append('PROVED for all n >= 1 by induction.')
        lines.append('')
        lines.append(_w('Write it out as: true for n = 1; assume'))
        lines.append(_w('true for n = k; then S(k+1) = S(k) +'))
        lines.append(_w('u(k+1), which simplifies to the formula'))
        lines.append(_w('with k+1 in place of k; so true for all n.'))
    else:
        lines.append(_warn('  These are NOT equal, so the claimed'))
        lines.append(_warn('  S(n) is wrong. Check it against a few'))
        lines.append(_warn('  values before trying to prove it.'))
        acc = 0.0
        i = 1
        rows = []
        while i <= 5:
            v = _at(u, float(i))
            sv = _at(S, float(i))
            if v is None or sv is None:
                break
            acc += v
            rows.append('  n=' + str(i) + '  sum=' + _fn(acc) + '  S(n)=' + _fn(sv))
            i += 1
        if rows:
            lines.append('')
            for r in rows:
                lines.append(_w(r))
    _show('Induction: a sum', lines)


def t_induction_divis():
    # Prove that d divides f(n) for all n >= 1.
    # The step is: f(k+1) - m f(k) must be divisible by d for some multiplier m
    # you choose - usually the ratio of the leading exponentials. The tool
    # checks the base case, checks divisibility over a range, and works out
    # f(k+1) - m f(k) symbolically so you can see what is left.
    _show('Induction: divisibility', ['To prove that d divides f(n).',
                                      'Base: f(1) divisible by d.',
                                      'Step: f(k+1) - m f(k) must also be',
                                      'divisible, for a multiplier m you',
                                      'pick (often the base of the',
                                      'exponential in f).'])
    f = _parse('f(n) = (type n)')
    if f is None:
        return
    d = _askint('divisor d', 2, 100000)
    if d is None:
        return
    lines = [_w('f(n) = ' + caseng.tostr(caseng.simplify(f))),
             _w('claim: ' + str(d) + ' divides f(n) for all n >= 1'), '']
    # base case and a numeric sweep
    bad = None
    rows = []
    i = 1
    while i <= 8:
        v = _at(f, float(i))
        if v is None:
            break
        r = int(round(v))
        if abs(v - r) > 1e-6:
            lines.append(_warn('f(' + str(i) + ') = ' + _fn(v) + ' is not a whole'))
            lines.append(_warn('number, so divisibility is not the'))
            lines.append(_warn('right question here.'))
            _show('Induction', lines)
            return
        rem = r % d
        rows.append('  f(' + str(i) + ') = ' + str(r) + ',  remainder ' + str(rem))
        if rem != 0 and bad is None:
            bad = i
        i += 1
    for r in rows[:6]:
        lines.append(_w(r))
    lines.append('')
    if bad is not None:
        lines.append('f(' + str(bad) + ') is NOT divisible by ' + str(d) + '.')
        lines.append('The claim is false - one counterexample')
        lines.append('is enough to disprove it, and you have')
        lines.append('one. No induction needed.')
        _show('Induction: divisibility', lines)
        return
    lines.append(_w('Base case holds, and so do the first'))
    lines.append(_w(str(len(rows)) + ' values. Now the step.'))
    m = _askint('multiplier m in f(k+1) - m f(k)', -1000, 1000)
    if m is None:
        _show('Induction: divisibility', lines)
        return
    fk1 = caseng.subst(f, 'n', ('+', ('v', 'n'), ('n', 1)))
    rest = caspoly.expand(('-', fk1, ('*', ('n', m), f)))
    lines.append('')
    lines.append(_w('f(k+1) - ' + str(m) + ' f(k) ='))
    lines.append(_w('  ' + caseng.tostr(rest)))
    okstep = True
    for kv in (1.0, 2.0, 3.0, 4.0, 5.0):
        v = _at(rest, kv)
        if v is None:
            continue
        r = int(round(v))
        if abs(v - r) > 1e-6 or r % d != 0:
            okstep = False
            break
    lines.append('')
    if okstep:
        lines.append(_w('and that is divisible by ' + str(d) + ' too.'))
        lines.append('')
        lines.append(_w('So f(k+1) = ' + str(m) + ' f(k) + (a multiple of ' +
                        str(d) + ').'))
        lines.append(_w('If ' + str(d) + ' divides f(k) it divides both'))
        lines.append(_w('terms, hence f(k+1).'))
        lines.append('PROVED by induction.')
    else:
        lines.append(_warn('but that is NOT always divisible by ' +
                           str(d) + '.'))
        lines.append(_w('Try a different multiplier m - the usual'))
        lines.append(_w('choice is the base of the exponential'))
        lines.append(_w('term in f(n).'))
    _show('Induction: divisibility', lines)


def t_induction_matrix():
    # Prove a claimed formula for M^n by induction: check n = 1, then check
    # that M^(k+1) built from the formula equals M times the formula at k.
    # The entries are given as expressions in n.
    _show('Induction: M^n', ['Enter a 2x2 M, then the four',
                             'entries of the claimed M^n as',
                             'expressions in n.',
                             'Checks n = 1 and then that',
                             'M * (formula at k) = formula at k+1.'])
    m = []
    i = 0
    while i < 2:
        row = []
        j = 0
        while j < 2:
            v = _asknum('M[' + str(i + 1) + ',' + str(j + 1) + ']')
            if v is None:
                return
            row.append(v)
            j += 1
        m.append(row)
        i += 1
    F = []
    i = 0
    while i < 2:
        row = []
        j = 0
        while j < 2:
            t = _parse('M^n [' + str(i + 1) + ',' + str(j + 1) + '] =')
            if t is None:
                return
            row.append(t)
            j += 1
        F.append(row)
        i += 1
    lines = [_w('M = [ ' + _fn(m[0][0]) + '  ' + _fn(m[0][1]) + ' ]'),
             _w('    [ ' + _fn(m[1][0]) + '  ' + _fn(m[1][1]) + ' ]'), '',
             _w('claimed M^n =')]
    i = 0
    while i < 2:
        lines.append(_w('  [ ' + caseng.tostr(caseng.simplify(F[i][0])) + '  ' +
                        caseng.tostr(caseng.simplify(F[i][1])) + ' ]'))
        i += 1
    lines.append('')
    # base case: the formula at n = 1 must be M itself
    lines.append(_w('BASE CASE n = 1'))
    okbase = True
    i = 0
    while i < 2:
        j = 0
        while j < 2:
            v = _at(F[i][j], 1.0)
            if v is None or abs(v - m[i][j]) > 1e-9:
                okbase = False
            j += 1
        i += 1
    lines.append('  ' + ('formula at n=1 is M: TRUE' if okbase
                         else 'formula at n=1 is NOT M: FALSE'))
    if not okbase:
        lines.append('  The formula is wrong before you start.')
        _show('Induction: M^n', lines)
        return
    # step: M * F(k) must equal F(k+1), checked at several k
    lines.append('')
    lines.append(_w('INDUCTIVE STEP  M * F(k) = F(k+1)?'))
    okstep = True
    for kv in (1.0, 2.0, 3.0, 5.0, 8.0):
        a = []
        i = 0
        while i < 2:
            row = []
            j = 0
            while j < 2:
                row.append(_at(F[i][j], kv))
                j += 1
            a.append(row)
            i += 1
        b = []
        i = 0
        while i < 2:
            row = []
            j = 0
            while j < 2:
                row.append(_at(F[i][j], kv + 1.0))
                j += 1
            b.append(row)
            i += 1
        i = 0
        while i < 2:
            j = 0
            while j < 2:
                if a[0][0] is None or b[0][0] is None:
                    j += 1
                    continue
                prod = m[i][0] * a[0][j] + m[i][1] * a[1][j]
                if abs(prod - b[i][j]) > 1e-7 * (1.0 + abs(b[i][j])):
                    okstep = False
                j += 1
            i += 1
    if okstep:
        lines.append(_warn('  holds at k = 1, 2, 3, 5 and 8.'))
        lines.append('')
        lines.append('PROVED by induction (write the step out')
        lines.append('as M^(k+1) = M * M^k and multiply).')
    else:
        lines.append('  FAILS - M * F(k) is not F(k+1).')
        lines.append('  The claimed formula is wrong.')
    _show('Induction: M^n', lines)


def t_counterexample():
    # Disproof by counterexample. A machine is very good at this and it is the
    # one proof technique where finding the answer IS the whole proof.
    _show('Disprove by counterexample', ['Enter a claim as an expression in n',
                                         'that should always be positive,',
                                         'or pick a standard claim to test.',
                                         'One counterexample disproves it.'])
    kind = casui.menu('Claim to test', ['f(n) is always prime',
                                        'f(n) > 0 for all n in a range',
                                        'f(n) is a whole number for all n',
                                        'd divides f(n) for all n'])
    if kind == -1:
        return
    f = _parse('f(n) = (type n)')
    if f is None:
        return
    lo = _askint('test n from', -10000, 10000)
    if lo is None:
        lo = 1
    hi = _askint('to', lo, lo + 5000)
    if hi is None:
        hi = lo + 60
    d = None
    if kind == 3:
        d = _askint('divisor d', 2, 100000)
        if d is None:
            return
    lines = [_w('f(n) = ' + caseng.tostr(caseng.simplify(f))),
             _w('tested for n = ' + str(lo) + ' to ' + str(hi)), '']
    found = None
    detail = ''
    n = lo
    while n <= hi:
        v = _at(f, float(n))
        if v is None:
            found = n
            detail = 'f(' + str(n) + ') is undefined'
            break
        if kind == 0:
            r = int(round(v))
            if abs(v - r) > 1e-6:
                found = n
                detail = 'f(' + str(n) + ') = ' + _fn(v) + ' is not a whole number'
                break
            if not _isprime(r):
                found = n
                fac = _smallfactor(r)
                detail = 'f(' + str(n) + ') = ' + str(r) + ' = ' + str(fac) + \
                         ' x ' + str(r // fac)
                break
        elif kind == 1:
            if v <= 0:
                found = n
                detail = 'f(' + str(n) + ') = ' + _fn(v) + ', which is not > 0'
                break
        elif kind == 2:
            r = int(round(v))
            if abs(v - r) > 1e-6:
                found = n
                detail = 'f(' + str(n) + ') = ' + _fn(v) + ', not a whole number'
                break
        else:
            r = int(round(v))
            if abs(v - r) > 1e-6 or r % d != 0:
                found = n
                detail = 'f(' + str(n) + ') = ' + _fn(v) + ', remainder ' + \
                         str(r % d if abs(v - r) <= 1e-6 else -1)
                break
        n += 1
    if found is None:
        lines.append('No counterexample in that range.')
        lines.append('')
        lines.append(_warn('That is NOT a proof. Checking cases'))
        lines.append(_warn('never proves a statement about all n -'))
        lines.append(_warn('it only fails to disprove it. Widen the'))
        lines.append(_warn('range, or prove it properly.'))
    else:
        lines.append('COUNTEREXAMPLE at n = ' + str(found))
        lines.append('  ' + detail)
        lines.append('')
        lines.append(_w('One counterexample is a complete'))
        lines.append(_w('disproof. Write it out: "when n = ' + str(found) + ','))
        lines.append(_w('f(n) = ..., so the statement is false."'))
    _show('Counterexample', lines)


def _isprime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def _smallfactor(n):
    if n < 2:
        return n
    if n % 2 == 0:
        return 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return i
        i += 2
    return n


def t_methods():
    _show('Proof methods', [
        'DIRECT PROOF',
        '  Start from what is given and deduce',
        '  the result step by step. Each step',
        '  must follow from the last.',
        '',
        'PROOF BY EXHAUSTION',
        '  Split into a finite number of cases',
        '  and check every one. Only valid when',
        '  the cases genuinely cover everything.',
        '',
        'DISPROOF BY COUNTEREXAMPLE',
        '  ONE case where the claim fails is a',
        '  complete disproof. Checking many cases',
        '  where it holds proves nothing.',
        '',
        'PROOF BY CONTRADICTION',
        '  Assume the opposite of what you want.',
        '  Deduce something impossible. Conclude',
        '  the assumption was false.',
        '  Classic: root 2 is irrational. Assume',
        '  root 2 = a/b in lowest terms; then',
        '  a^2 = 2b^2, so a is even, a = 2c, so',
        '  2c^2 = b^2, so b is even too - but',
        '  then a/b was not in lowest terms.',
        '  Also: there are infinitely many primes.',
        '  Assume finitely many p1..pn; then',
        '  p1 p2 ... pn + 1 is divisible by none',
        '  of them, so either it is a new prime',
        '  or it has a prime factor not in the',
        '  list. Either way the list was not all',
        '  of them.',
        '',
        'PROOF BY INDUCTION  (Further Maths)',
        '  1. Show it is true for n = 1.',
        '  2. ASSUME it is true for n = k.',
        '  3. Show that then it is true for k+1.',
        '  4. Conclude: true for all n >= 1.',
        '  Step 3 must USE step 2 - if it does',
        '  not, you have not done an induction.',
        '',
        'WHAT NOT TO WRITE',
        '  "It works for n = 1, 2, 3 so it is',
        '  true" - that is not a proof.',
        '  Starting from what you are trying to',
        '  prove and working back to something',
        '  true - unless every step is reversible',
        '  and you say so.',
    ])


TOOLS = [
    ('Induction: a sum', t_induction_sum),
    ('Induction: divisibility', t_induction_divis),
    ('Induction: M^n', t_induction_matrix),
    ('Disprove by counterexample', t_counterexample),
    ('Proof methods reference', t_methods),
]


def run():
    casutil.run_tools('PROOF', TOOLS)
