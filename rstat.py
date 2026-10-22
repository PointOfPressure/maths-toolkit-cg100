# Recognising Statistics (recog.py reads the other topics): B(n, p), N(mu,
# sigma^2) (? for an unknown mu or sigma), a data list with commas, or two
# lists (values and frequencies, or x and y: both readings are offered).
import caslex
import recog
from recog import Form

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

def _num(s):
    t = caslex.parse(s)
    if t is None:
        raise ValueError('cannot read ' + s)
    v = recog.numv(t)
    if v is None:
        raise ValueError(s + ' is not a number')
    return v

def _list(s):
    return [_num(p) for p in _split(s)]

def _dist(s):
    # 'b(20,0.3)' or 'x~n(5,2^2)' -> ('b' or 'n', [two parts as text])
    if '~' in s:
        s = s[s.index('~') + 1:]
    if len(s) > 4 and s[0] in 'bn' and s[1] == '(' and s[-1] == ')':
        ps = _split(s[2:-1])
        if len(ps) == 2:
            return s[0], ps
    return None

def read(rows):
    texts = [t.replace(' ', '').lower() for t in rows if t.strip()]
    F = Form()
    F.kind = 'stat'
    try:
        if len(texts) == 1 and _dist(texts[0]) is not None:
            k, ps = _dist(texts[0])
            if k == 'b':
                n = _num(ps[0])
                p = _num(ps[1])
                if n != int(n) or n < 1 or not 0 <= p <= 1:
                    raise ValueError('B(n, p): n a whole number, p from 0 to 1')
                F.kind = 'binom'
                F.n = int(n)
                F.p = p
                F.note = 'binomial n = ' + str(F.n) + ', p = ' + recog._fnum(p)
                return F
            F.kind = 'normal'
            F.mu = None if ps[0] == '?' else _num(ps[0])
            if ps[1] == '?':
                F.sd = None
            else:
                t = caslex.parse(ps[1])
                v = recog.numv(t) if t is not None else None
                if v is None or v <= 0:
                    raise ValueError('N(mu, sigma^2): the variance must be positive')
                F.sd = v ** 0.5
            if F.mu is None and F.sd is None:
                raise ValueError('only one of mu and sigma can be ?')
            F.note = 'normal, ' + ('mu unknown' if F.mu is None else 'mu = ' + recog._fnum(F.mu)) + ', ' + \
                ('sigma unknown' if F.sd is None else 'sigma = ' + recog._fnum(round(F.sd, 10)))
            return F
        if texts and ',' in texts[0]:
            ls = [_list(t) for t in texts]
            if len(ls) == 1:
                F.kind = 'data'
                F.data = ls[0]
                F.note = 'data, ' + str(len(ls[0])) + ' values'
                return F
            if len(ls) == 2:
                if len(ls[0]) != len(ls[1]):
                    raise ValueError('the two lists need the same length')
                F.kind = 'two'
                F.data = ls[0]
                F.data2 = ls[1]
                F.note = 'two lists of ' + str(len(ls[0])) + ': values and frequencies, or x and y'
                return F
    except ValueError as e:
        F.err = str(e) or 'cannot read that'
        F.note = F.err
        return F
    return recog.form(rows)
