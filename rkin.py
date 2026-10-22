# Recognising Kinematics (recog.py reads the other topics): v = f(t),
# s = f(t) (or x =, r =) and a = f(t), as numbers or as vectors in i and j;
# or two lists, times and velocities, read off a v-t graph.
import recog
from recog import Form, letters, has

KQ = {'v': 'v', 's': 's', 'x': 's', 'r': 's', 'a': 'a'}

def _ij(t):
    # i (read as the imaginary unit) or j in it: a vector
    k = t[0]
    if k == 'n':
        return isinstance(t[1], complex)
    if k == 'v':
        return t[1] == 'j'
    for c in t[1:]:
        if _ij(c):
            return True
    return False

def read(rows):
    texts = [t for t in rows if t.strip()]
    if len(texts) == 2 and ',' in texts[0] and ',' in texts[1]:
        import rstat
        F = Form()
        F.kind = 'vt'
        try:
            F.ts = rstat._list(texts[0].replace(' ', ''))
            F.vs = rstat._list(texts[1].replace(' ', ''))
        except ValueError as e:
            F.err = str(e)
            F.note = F.err
            return F
        if len(F.ts) != len(F.vs) or len(F.ts) < 2:
            F.err = 'times and velocities: two lists of the same length'
        elif [1 for i in range(len(F.ts) - 1) if F.ts[i + 1] <= F.ts[i]]:
            F.err = 'the times must increase'
        F.note = F.err or 'v-t graph through ' + str(len(F.ts)) + ' points'
        return F
    F = recog.form(texts)
    if F.err or F.pair or F.kind == 'blank':
        return F
    r = F.rows[0]
    q = KQ.get(r.name) if r.name is not None and len(r.name) == 1 else None
    if q is None:
        F.err = 'type v = ..., s = ... or a = ... (a function of t)'
        F.note = F.err
        return F
    F.kq = q
    F.f = r.f
    F.var = 't'
    F.vec = None
    import rvec
    c = rvec.comps(r.f) if _ij(r.f) else None
    if c is not None:
        import eng
        if eng.S(c[3]) != ('n', 0):
            F.err = 'a vector needs every term in i or j'
            F.note = F.err
            return F
        F.vec = [eng.S(c[0]), eng.S(c[1])]
    ls = letters(r.f)
    F.letters = [c for c in ls if c != 't' and (c != 'j' or F.vec is None)]
    name = {'v': 'velocity', 's': 'displacement', 'a': 'acceleration'}[q]
    F.kind = 'kin'
    F.note = name + (' vector' if F.vec else '') + ' as a function of t'
    if F.letters:
        F.note += ', ' + recog._and(F.letters) + ' unknown'
    return F
