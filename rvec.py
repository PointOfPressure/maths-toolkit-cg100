# Recognising Vectors (recog.py reads the other topics): each row a vector,
# as 3i + 4j (- k), or in brackets (3, 4) / (3, 4, -1); one row or two (a
# and b, or the position vectors of A and B).
import caslex
import recog
from recog import Form

def _z(x):
    # structurally zero (a letter times 0 is 0), or a number that is 0
    k = x[0]
    if k == 'n':
        return x[1] == 0
    if k == '*':
        return _z(x[1]) or _z(x[2])
    if k == '/' or k == 'neg':
        return _z(x[1])
    if k == '+' or k == '-':
        return _z(x[1]) and _z(x[2])
    return recog.numv(x) == 0

def _tidy(x):
    import eng
    if recog.hasfloat(x) and not recog.letters(x):
        v = recog.numv(x)
        return ('n', v) if v >= 0 else ('neg', ('n', -v))
    return eng.S(x)

def comps(t):
    # [i, j, k, scalar] coefficient trees of a tree in i, j and k (caslex
    # reads i as the imaginary unit), or None when it isn't one
    k = t[0]
    Z = ('n', 0)
    if k == 'n':
        v = t[1]
        if isinstance(v, complex):
            return [('n', v.imag if v.imag != int(v.imag) else int(v.imag)), Z, Z,
                    ('n', v.real if v.real != int(v.real) else int(v.real))]
        return [Z, Z, Z, t]
    if k == 'v':
        if t[1] == 'j':
            return [Z, ('n', 1), Z, Z]
        if t[1] == 'k':
            return [Z, Z, ('n', 1), Z]
        return [Z, Z, Z, t]
    if k in ('+', '-'):
        a = comps(t[1])
        b = comps(t[2])
        if a is None or b is None:
            return None
        return [(k, a[i], b[i]) for i in range(4)]
    if k == 'neg':
        a = comps(t[1])
        return None if a is None else [('neg', x) for x in a]
    if k in ('*', '/'):
        a = comps(t[1])
        b = comps(t[2])
        if a is None or b is None:
            return None
        av = [x for x in a[:3] if not _z(x)]
        bv = [x for x in b[:3] if not _z(x)]
        if k == '*' and not av:
            return [('*', a[3], x) for x in b]
        if not bv:
            return [(k, x, b[3]) for x in a]
        return None
    for c in t[1:]:
        if c[0] != 'n' and comps(c) is not None and [x for x in comps(c)[:3] if not _z(x)]:
            return None
    return [Z, Z, Z, t]

def parse_vec(s):
    # one vector as text -> [x, y, z] trees (z ('n', 0) in 2-D) and its size
    s = s.strip()
    if s[:1] == '(' and s[-1:] == ')' and ',' in s:
        parts = []
        d = 0
        cur = ''
        for c in s[1:-1]:
            if c == '(':
                d += 1
            elif c == ')':
                d -= 1
            if c == ',' and d == 0:
                parts.append(cur)
                cur = ''
            else:
                cur += c
        parts.append(cur)
        if len(parts) not in (2, 3):
            raise ValueError('a vector has 2 or 3 parts')
        out = []
        for p in parts:
            t = caslex.parse(p)
            if t is None:
                raise ValueError('cannot read ' + p)
            out.append(_tidy(t))
        return out + [('n', 0)] * (3 - len(out)), len(parts)
    t = caslex.parse(s)
    if t is None:
        raise ValueError('cannot read that')
    c = comps(t)
    import eng
    if c is None or not _z(eng.S(c[3])):
        raise ValueError('type a vector: 3i + 4j or (3, 4)')
    out = [_tidy(x) for x in c[:3]]
    return out, (3 if out[2] != ('n', 0) else 2)

def read(rows):
    F = Form()
    F.kind = 'vec'
    F.vecs = []
    F.dim = 2
    for s in rows:
        if not s.strip():
            continue
        try:
            v, d = parse_vec(s)
        except ValueError as e:
            F.err = ('row ' + str(len(F.vecs) + 1) + ': ' if len(rows) > 1 else '') + (str(e) or 'cannot read that')
            F.note = F.err
            return F
        F.vecs.append(v)
        if d == 3:
            F.dim = 3
    ls = []
    for v in F.vecs:
        for x in v:
            recog.letters(x, ls)
    F.letters = ls
    F.var = 't'
    n = len(F.vecs)
    F.note = ('one vector' if n == 1 else 'two vectors a, b (or points A, B)') + (', 3-D' if F.dim == 3 else '')
    if ls:
        F.note += ', ' + recog._and(ls) + ' unknown'
    return F
