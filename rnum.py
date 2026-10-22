# Recognising Numerical methods (recog.py reads the other topics): x = g(x)
# for iteration, f(x) or f(x) = 0 (an equation is moved to one side), or a
# list of y values (commas) for the trapezium rule.
import caslex
import recog
from recog import Form, has

def _commas(s):
    d = 0
    for c in s:
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif c == ',' and d == 0:
            return True
    return False

def _split(s):
    out = []
    d = 0
    cur = ''
    for c in s:
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        if c == ',' and d == 0:
            out.append(cur)
            cur = ''
        else:
            cur += c
    out.append(cur)
    return out

def read(rows):
    texts = [t for t in rows if t.strip()]
    if len(texts) == 1 and _commas(texts[0]):
        F = Form()
        F.kind = 'data'
        F.data = []
        for p in _split(texts[0]):
            try:
                t = caslex.parse(p)
            except ValueError as e:
                t = None
            if t is None or recog.numv(t) is None:
                F.err = 'y values: numbers only, with commas between'
                F.note = F.err
                return F
            F.data.append(t)
        F.note = str(len(F.data)) + ' y values'
        return F
    F = recog.form(texts)
    F.num = ''
    if F.err or F.pair:
        return F
    r = F.rows[0]
    v = F.var
    if r.rel == '=' and r.lhs == ('v', v) and has(r.rhs, v):
        F.num = 'iter'
        F.g = r.rhs
        F.note = v + ' = g(' + v + '): iteration'
    elif r.rel == '=' and r.name is None:
        F.num = 'root'
        F.fx = ('-', r.lhs, r.rhs)
        F.note = 'f(' + v + ') = 0 with f(' + v + ') = left - right'
    elif r.rel == '' or r.name is not None:
        F.num = 'fn'
        F.fx = r.f
        F.note = 'f(' + v + ')'
    if F.num and F.letters:
        F.err = 'numbers only here: ' + recog._and(F.letters) + ' unknown'
        F.note = F.err
    return F
