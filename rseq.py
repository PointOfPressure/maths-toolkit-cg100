# Recognising Sequences and series (recog.py reads the other topics): a
# recurrence (u(n+1) = f(u(n)), or u = f(u) for short), (a + bx)^n, or a
# formula in n, r or k (a u(n) formula or the term of a sigma sum). Two
# rows are read as in Algebra (a and d from two facts: Solve).
import recog
from recog import letters, has

def _rec_text(s):
    # u(n+1) -> u and u(n) -> u, for a letter that isn't the end of a name
    out = ''
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isalpha() and c != 'n' and (i == 0 or not s[i - 1].isalpha()):
            for tail in ('(n+1)', '(n)', '_(n+1)', '_n'):
                if s[i + 1:i + 1 + len(tail)] == tail and (i + 1 + len(tail) >= n or not s[i + 1 + len(tail)].isalpha()):
                    out += c
                    i += 1 + len(tail)
                    break
            else:
                out += c
                i += 1
            continue
        out += c
        i += 1
    return out

def read(rows):
    texts = [_rec_text(t.replace(' ', '')) for t in rows if t.strip()]
    F = recog.form(texts)
    F.seq = ''
    if F.err or F.pair:
        return F
    r = F.rows[0]
    if r.rel == '=' and r.lhs[0] == 'v' and r.lhs[1] not in ('n', 'e') and has(r.rhs, r.lhs[1]):
        u = r.lhs[1]
        F.seq = 'rec'
        F.kind = 'rec'
        F.u = u
        F.g = r.rhs
        F.var = 'n'
        F.letters = [c for c in letters(r.rhs) if c not in (u, 'n')]
        F.note = 'recurrence ' + u + '(n+1) = f(' + u + '(n))'
        if F.letters:
            F.note += ', ' + recog._and(F.letters) + ' unknown'
        return F
    if r.rel and r.name is None:
        return F
    f = r.f
    ls = letters(f)
    if f[0] == '^' and recog.rat(f[2]) is not None and len(letters(f[1])) >= 1:
        v = 'x' if 'x' in ls else ls[0]
        p = recog.pdeg(f[1], v, [False])
        if p is not None and p >= 1 and len(recog.terms(f[1], 1, [])) == 2 and not has(f[2], v):
            F.seq = 'binom'
            F.kind = 'binom'
            F.var = v
            F.letters = [c for c in ls if c != v]
            q = recog.rat(f[2])
            F.note = 'binomial, power ' + str(q[0]) + ('/' + str(q[1]) if q[1] != 1 else '')
            if F.letters:
                F.note += ', ' + recog._and(F.letters) + ' unknown'
            return F
    for v in ('n', 'r', 'k', 'i'):
        if v in ls:
            break
    else:
        v = F.var if F.var in ls else (ls[0] if ls else 'n')
    F.seq = 'term'
    F.var = v
    F.letters = [c for c in ls if c != v]
    F.note = 'term in ' + v
    if F.letters:
        F.note += ', ' + recog._and(F.letters) + ' unknown'
    return F
