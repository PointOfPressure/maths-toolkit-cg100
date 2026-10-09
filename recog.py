# Recogniser: which of a fixed list of forms was typed (docs/redesign.md).
# Each row is parsed once with caslex; everything after that is structural:
# walks over the tree for the letters, the degree in x, the powers of x, the
# bases of exponentials, logs and moduli. Nothing here guesses at intent: a
# form is named only when the structure says so, anything else is the
# general form, and the grey line always says what was found.
import caslex

REL = ('<=', '>=', '<', '>', '=')
CONST = ('pi', 'e', 'ans')

class Row:
    # one typed row: rel '' or one of REL; lhs, rhs trees; name when the left
    # side only names the right ('y = ...', 'f(x) = ...'); f the tree to read
    def __init__(self, text):
        self.text = text
        self.rel = ''
        self.lhs = None
        self.rhs = None
        self.name = None
        self.f = None
        self.err = None

class Form:
    def __init__(self):
        self.rows = []
        self.kind = 'none'
        self.var = 'x'
        self.letters = []     # other letters: unknown constants
        self.deg = None       # degree in var when a polynomial
        self.poly = False
        self.qin = False      # quadratic in u
        self.u = None         # the u tree, ushow its text, uk its power of x
        self.ushow = ''
        self.uk = None
        self.recip = False    # u + 1/u: quadratic once times u
        self.bases = []       # root bases of the exponentials ('e', 2, 3, letter)
        self.expand = False   # brackets that expand
        self.pair = ''        # two rows: 'simul' or 'fg'
        self.model = ''       # 'aekt', 'kbx', 'axn' for a two-constant model
        self.consts = []      # the model's unknown constants
        self.note = ''
        self.err = None
        self.dec = False      # a decimal was typed
        self.vars2 = []       # the two unknowns of an equation in x and y
        self.surd = False
        self.logs = False

# ---- splitting a row -------------------------------------------------------------

def split_rel(s):
    # (lhs text, rel, rhs text); one relation at bracket depth 0 at most
    depth = 0
    found = None
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0 and (c == '<' or c == '>' or c == '='):
            r = c
            if c != '=' and i + 1 < n and s[i + 1] == '=':
                r = c + '='
            if found is not None:
                raise ValueError('one =, < or > only')
            found = (i, r)
            i += len(r)
            continue
        i += 1
    if found is None:
        return (s, '', None)
    i, r = found
    return (s[:i], r, s[i + len(r):])

def _name(l):
    # 'y', 'N', 'f(x)' on the left: names what is on the right
    l = l.replace(' ', '').lower()
    if len(l) == 1 and l.isalpha() and l != 'e' and l != 'i':
        return l
    if len(l) == 4 and l[0].isalpha() and l[1] == '(' and l[2].isalpha() and l[3] == ')':
        return l
    return None

def parse_row(text):
    r = Row(text)
    try:
        l, rel, rt = split_rel(text)
        if rel and not rt.strip():
            raise ValueError('nothing after ' + rel)
        if not l.strip():
            raise ValueError('nothing before ' + (rel or '='))
        r.lhs = caslex.parse(l)
        if r.lhs is None:
            raise ValueError('cannot read that')
        if rel:
            r.rhs = caslex.parse(rt)
            if r.rhs is None:
                raise ValueError('cannot read the right side')
        r.rel = rel
    except ValueError as e:
        r.err = str(e) or 'cannot read that'
        return r
    if rel == '=':
        nm = _name(l)
        if nm is not None and nm[0] not in letters(r.rhs):
            r.name = nm
            r.f = r.rhs
            return r
    r.f = ('-', r.lhs, r.rhs) if rel else r.lhs
    return r

# ---- small structural helpers ------------------------------------------------------

def letters(t, out=None):
    if out is None:
        out = []
    k = t[0]
    if k == 'v':
        if t[1] not in out and t[1] not in CONST:
            out.append(t[1])
        return out
    if k == 'n':
        return out
    for c in t[1:]:
        letters(c, out)
    return out

def has(t, v):
    k = t[0]
    if k == 'v':
        return t[1] == v
    if k == 'n':
        return False
    for c in t[1:]:
        if has(c, v):
            return True
    return False

def hasfn(t, names, v):
    # a function from names applied to something holding v
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k in names and has(t, v):
        return True
    for c in t[1:]:
        if hasfn(c, names, v):
            return True
    return False

def hasfloat(t):
    k = t[0]
    if k == 'n':
        return isinstance(t[1], float)
    if k == 'v':
        return False
    for c in t[1:]:
        if hasfloat(c):
            return True
    return False

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a if a >= 0 else -a

def rat(t):
    # exact rational value of a number tree as (p, q), else None
    k = t[0]
    if k == 'n':
        v = t[1]
        if isinstance(v, int):
            return (v, 1)
        return None
    if k == 'neg':
        r = rat(t[1])
        return None if r is None else (-r[0], r[1])
    if k in ('+', '-', '*', '/'):
        a = rat(t[1])
        b = rat(t[2])
        if a is None or b is None:
            return None
        if k == '+':
            p, q = a[0] * b[1] + b[0] * a[1], a[1] * b[1]
        elif k == '-':
            p, q = a[0] * b[1] - b[0] * a[1], a[1] * b[1]
        elif k == '*':
            p, q = a[0] * b[0], a[1] * b[1]
        else:
            if b[0] == 0:
                return None
            p, q = a[0] * b[1], a[1] * b[0]
        if q < 0:
            p, q = -p, -q
        g = _gcd(p, q) or 1
        return (p // g, q // g)
    if k == '^':
        a = rat(t[1])
        b = rat(t[2])
        if a is None or b is None or b[1] != 1 or b[0] > 64 or b[0] < -64:
            return None
        e = b[0]
        if e < 0:
            if a[0] == 0:
                return None
            a = (a[1], a[0]) if a[0] > 0 else (-a[1], -a[0])
            e = -e
        return (a[0] ** e, a[1] ** e)
    return None

def numv(t):
    # float value of a constant tree (no letters), else None
    import math
    k = t[0]
    try:
        if k == 'n':
            v = t[1]
            return None if isinstance(v, complex) else float(v)
        if k == 'v':
            return math.pi if t[1] == 'pi' else (math.e if t[1] == 'e' else None)
        if k == 'neg':
            a = numv(t[1])
            return None if a is None else -a
        if k in ('+', '-', '*', '/', '^', 'logb'):
            a = numv(t[1])
            b = numv(t[2])
            if a is None or b is None:
                return None
            if k == '+':
                return a + b
            if k == '-':
                return a - b
            if k == '*':
                return a * b
            if k == '/':
                return a / b
            if k == '^':
                return a ** b
            return math.log(b) / math.log(a)
        a = numv(t[1])
        if a is None:
            return None
        if k == 'sqrt':
            return math.sqrt(a)
        if k == 'exp':
            return math.exp(a)
        if k == 'ln':
            return math.log(a)
        if k == 'log':
            return math.log10(a)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None
    return None

def lin(t, v):
    # t = p v + q with p, q constant trees free of v; -> (p, q) or None
    k = t[0]
    if not has(t, v):
        return (('n', 0), t)
    if k == 'v':
        return (('n', 1), ('n', 0))
    if k == '+' or k == '-':
        a = lin(t[1], v)
        b = lin(t[2], v)
        if a is None or b is None:
            return None
        return ((k, a[0], b[0]), (k, a[1], b[1]))
    if k == 'neg':
        a = lin(t[1], v)
        return None if a is None else (('neg', a[0]), ('neg', a[1]))
    if k == '*':
        if not has(t[1], v):
            b = lin(t[2], v)
            return None if b is None else (('*', t[1], b[0]), ('*', t[1], b[1]))
        if not has(t[2], v):
            a = lin(t[1], v)
            return None if a is None else (('*', a[0], t[2]), ('*', a[1], t[2]))
        return None
    if k == '/' and not has(t[2], v):
        a = lin(t[1], v)
        return None if a is None else (('/', a[0], t[2]), ('/', a[1], t[2]))
    return None

# ---- degree in v ---------------------------------------------------------------------

def pdeg(t, v, ex):
    # degree of t as a polynomial in v (letters are constants), else None;
    # ex[0] is set when brackets multiply out
    k = t[0]
    if k == 'n':
        return 0
    if k == 'v':
        return 1 if t[1] == v else 0
    if k == '+' or k == '-':
        a = pdeg(t[1], v, ex)
        if a is None:
            return None
        b = pdeg(t[2], v, ex)
        if b is None:
            return None
        return a if a > b else b
    if k == 'neg':
        return pdeg(t[1], v, ex)
    if k == '*':
        a = pdeg(t[1], v, ex)
        if a is None:
            return None
        b = pdeg(t[2], v, ex)
        if b is None:
            return None
        if (a and t[1][0] in ('+', '-')) or (b and t[2][0] in ('+', '-')) or \
                (a and t[2][0] in ('+', '-')) or (b and t[1][0] in ('+', '-')):
            ex[0] = True
        return a + b
    if k == '/':
        if has(t[2], v):
            return None
        return pdeg(t[1], v, ex)
    if k == '^':
        if not has(t, v):
            return 0
        if has(t[2], v):
            return None
        e = t[2]
        if e[0] != 'n' or not isinstance(e[1], int) or e[1] < 0:
            return None
        d = pdeg(t[1], v, ex)
        if d is None:
            return None
        if d and t[1][0] not in ('v', 'n'):
            ex[0] = True
        return d * e[1]
    return None if has(t, v) else 0

# ---- additive terms, and each term's x-part ------------------------------------------

def terms(t, sg, out):
    k = t[0]
    if k == '+':
        terms(t[1], sg, out)
        terms(t[2], sg, out)
    elif k == '-':
        terms(t[1], sg, out)
        terms(t[2], -sg, out)
    elif k == 'neg':
        terms(t[1], -sg, out)
    else:
        out.append((t, sg))
    return out

def factors(t, e, out):
    # a product as (factor, +1 / -1) pairs; a minus is the factor -1
    k = t[0]
    if k == '*':
        factors(t[1], e, out)
        factors(t[2], e, out)
    elif k == '/':
        factors(t[1], e, out)
        factors(t[2], -e, out)
    elif k == 'neg':
        out.append((('n', -1), 1))
        factors(t[1], e, out)
    else:
        out.append((t, e))
    return out

def _rmul(a, b):
    # multipliers are (p, q) rationals, or (value, 0) once a decimal is in
    if a[1] == 0 or b[1] == 0:
        return (_pq(a) * _pq(b), 0)
    p = a[0] * b[0]
    q = a[1] * b[1]
    g = _gcd(p, q) or 1
    return (p // g, q // g)

def _radd(a, b):
    if a[1] == 0 or b[1] == 0:
        return (_pq(a) + _pq(b), 0)
    p = a[0] * b[1] + b[0] * a[1]
    q = a[1] * b[1]
    g = _gcd(p, q) or 1
    return (p // g, q // g)

def _pq(r):
    return r[0] if r[1] == 0 else r[0] / float(r[1])

def _same(a, b):
    x = _pq(a)
    y = _pq(b)
    return abs(x - y) <= 1e-9 * (abs(x) + abs(y) + 1e-300)

def rootbase(a):
    # 8 -> (2, 3); 1/9 -> (3, -2); e -> ('e', 1); anything else as itself
    r = rat(a)
    if r is None:
        if a == ('v', 'e'):
            return ('e', 1)
        if a[0] == 'v':
            return (a[1], 1)
        v = numv(a)
        if v is None:
            return None
        return (('f', v), 1)
    p, q = r
    sg = 1
    if p == 1 and q > 1:
        p = q
        sg = -1
    elif q != 1 or p < 2:
        return (('f', p / float(q)), 1)
    b = 2
    while b * b <= p:
        m = 0
        x = p
        while x % b == 0:
            x //= b
            m += 1
        if x == 1 and m > 1:
            return (b, sg * m)
        b += 1
    return (p, sg)

def xpart(t, v):
    # the v-part of one factor: ('p', r) for v^r, ('x', base, m) for base^(m v),
    # ('c',) for a constant, ('o',) for anything else; r and m are (p, q)
    k = t[0]
    if not has(t, v):
        return ('c',)
    if k == 'v':
        return ('p', (1, 1))
    if k == 'sqrt':
        a = xpart(t[1], v)
        if a[0] == 'p':
            return ('p', _rmul(a[1], (1, 2)))
        if a[0] == 'x':
            return ('x', a[1], _rmul(a[2], (1, 2)))
        return ('o',)
    if k == 'exp' or (k == '^' and not has(t[1], v)):
        e = t[1] if k == 'exp' else t[2]
        rb = ('e', 1) if k == 'exp' else rootbase(t[1])
        pq = lin(e, v)
        if pq is None or rb is None:
            return ('o',)
        m = rat(pq[0])
        if m is None:
            m = numv(pq[0])
            if m is None:
                # a letter times v up there (e^(kt)): still an exponential
                return ('x', rb[0], None)
            m = (m, 0)
        return ('x', rb[0], _rmul(m, (rb[1], 1)))
    if k == '^' and not has(t[2], v):
        r = rat(t[2])
        a = xpart(t[1], v)
        if r is None or a[0] == 'o' or a[0] == 'c':
            return ('o',)
        if a[0] == 'p':
            return ('p', _rmul(a[1], r))
        if a[0] == 'f':
            return ('f', a[1], _rmul(a[2], r))
        if a[2] is None:
            return ('o',)
        return ('x', a[1], _rmul(a[2], r))
    if k in FATOMS and t[-1] == ('v', v) and (k != 'logb' or not has(t[1], v)):
        # ln x, log x, sin x ...: u for a quadratic in it
        return ('f', t, (1, 1))
    return ('o',)

FATOMS = ('ln', 'log', 'logb', 'sin', 'cos', 'tan')

def tpart(t, v):
    # one additive term's v-part: ('c',), ('p', r), ('x', base, m) or ('o',)
    acc = ('c',)
    for f, e in factors(t, 1, []):
        a = xpart(f, v)
        if a[0] == 'c':
            continue
        if a[0] == 'o' or (a[0] == 'p' and f[0] in ('+', '-')):
            return ('o',)
        if a[0] == 'x' and a[2] is None:
            if acc[0] != 'c':
                return ('o',)
            acc = a
            continue
        if acc[0] == 'x' and acc[2] is None:
            return ('o',)
        if a[0] == 'f':
            if e < 0:
                a = ('f', a[1], _rmul(a[2], (-1, 1)))
            if acc[0] == 'c':
                acc = a
            elif acc[0] == 'f' and acc[1] == a[1]:
                acc = ('f', a[1], _radd(acc[2], a[2]))
            else:
                return ('o',)
            continue
        if acc[0] == 'f':
            return ('o',)
        if e < 0:
            a = (a[0], _rmul(a[1], (-1, 1))) if a[0] == 'p' else ('x', a[1], _rmul(a[2], (-1, 1)))
        if acc[0] == 'c':
            acc = a
        elif acc[0] == 'p' and a[0] == 'p':
            acc = ('p', _radd(acc[1], a[1]))
        elif acc[0] == 'x' and a[0] == 'x' and acc[1] == a[1]:
            acc = ('x', acc[1], _radd(acc[2], a[2]))
        else:
            return ('o',)
    return acc

# ---- the forms ---------------------------------------------------------------------------

def _pickvar(ls, name):
    if name is not None and len(name) == 4:
        return name[2]
    for v in ('x', 't', 'n'):
        if v in ls:
            return v
    if len(ls) == 1:
        return ls[0]
    return 'x'

def _quadin(parts):
    # the non-zero powers {k, 2k} (or {k, -k}): -> (k, recip) or None
    ks = []
    for p in parts:
        if _pq(p) == 0:
            continue
        new = True
        for q in ks:
            if _same(p, q):
                new = False
        if new:
            ks.append(p)
    if len(ks) != 2:
        return None
    a, b = ks
    if abs(_pq(a)) > abs(_pq(b)):
        a, b = b, a
    if _same(b, _rmul(a, (2, 1))):
        return (a, False)
    if _same(b, _rmul(a, (-1, 1))):
        return (a if _pq(a) > 0 else b, True)
    return None

def _ushow_pow(k, v):
    p, q = k
    if (p, q) == (1, 2):
        return 'sqrt ' + v
    if (p, q) == (-1, 1):
        return '1/' + v
    if p < 0:
        return '1/' + _ushow_pow((-p, q), v)
    if q == 1:
        return v + '^' + str(p)
    return v + '^(' + str(p) + '/' + str(q) + ')'

def _utree_pow(k, v):
    p, q = k
    if (p, q) == (1, 2):
        return ('sqrt', ('v', v))
    if q == 1:
        e = ('n', p) if p > 0 else ('neg', ('n', -p))
    else:
        e = ('/', ('n', p), ('n', q)) if p > 0 else ('neg', ('/', ('n', -p), ('n', q)))
    if p < 0:
        return ('/', ('n', 1), _utree_pow((-p, q), v))
    return ('^', ('v', v), e)

def _bshow(b):
    if isinstance(b, tuple):
        return _fnum(b[1])
    return str(b)

def _btree(b):
    if b == 'e':
        return ('v', 'e')
    if isinstance(b, tuple):
        return ('n', b[1])
    if isinstance(b, str):
        return ('v', b)
    return ('n', b)

def _fnum(x):
    s = repr(x)
    return s[:-2] if s[-2:] == '.0' else s

def _ushow_exp(b, k, v):
    p, q = k
    if q == 0:
        return _bshow(b) + '^(' + _fnum(p) + v + ')'
    if p == 1 and q > 1:
        return _bshow(b) + '^(' + v + '/' + str(q) + ')'
    e = v if (p, q) == (1, 1) else (str(p) + v if q == 1 else '(' + str(p) + v + '/' + str(q) + ')')
    if q == 1 and p != 1:
        e = '(' + e + ')'
    return _bshow(b) + '^' + e

def _utree_exp(b, k, v):
    p, q = k
    e = ('v', v)
    if (p, q) != (1, 1):
        c = ('n', p) if q <= 1 else ('/', ('n', p), ('n', q))
        e = ('*', c, e)
    if b == 'e':
        return ('exp', e)
    return ('^', _btree(b), e)

def brackets(t, v):
    # something to multiply out: a product or power of a sum, or a sum over
    # a power of v ((5 - sqrt x)/x^2 -> 5x^-2 - x^(-3/2))
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k == '^' and t[1][0] in ('+', '-') and t[2][0] == 'n':
        return True
    if k == '*' and (t[1][0] in ('+', '-') or t[2][0] in ('+', '-')):
        return True
    if (k == '-' and t[2][0] in ('+', '-')) or (k == 'neg' and t[1][0] in ('+', '-')):
        return True
    if k == '/' and t[1][0] in ('+', '-') and has(t[2], v) and \
            (t[2] == ('v', v) or (t[2][0] == '^' and t[2][1] == ('v', v))):
        return True
    for c in t[1:]:
        if brackets(c, v):
            return True
    return False

def analyse(F, f, v):
    # sets kind and its details on F from the tree f in v
    ex = [False]
    d = pdeg(f, v, ex)
    F.expand = ex[0] or brackets(f, v)
    if d is not None and ex[0] and d > 0 and not F.letters:
        # brackets can cancel: (x + 1)^2 - x^2 is linear
        import caspoly
        p = caspoly.poly(f, v)
        if p is not None:
            d = len(p) - 1 if p else 0
    if d is not None:
        if d <= 0:
            F.kind = 'num' if not F.letters else 'const'
            return
        F.poly = True
        F.deg = d
        F.kind = 'poly'
        if d >= 4:
            ks = []
            for t, sg in terms(f, 1, []):
                a = tpart(t, v)
                if a[0] == 'p':
                    ks.append(a[1])
            q = _quadin(ks)
            if q is not None and not q[1] and q[0][1] == 1 and q[0][0] > 1 and not F.expand:
                F.qin = True
                F.uk = q[0]
                F.u = _utree_pow(q[0], v)
                F.ushow = _ushow_pow(q[0], v)
        return
    fp = [tpart(t, v) for t, sg in terms(f, 1, [])]
    fk = [a for a in fp if a[0] != 'c']
    if fk and fk[0][0] == 'f' and [1 for a in fk if a[0] != 'f' or a[1] != fk[0][1]] == []:
        # every term a power of one ln x, log x, sin x: quadratic in it?
        q = _quadin([a[2] for a in fk])
        if q is not None and not q[1] and q[0] == (1, 1):
            key = fk[0][1]
            F.kind = 'trig' if key[0] in ('sin', 'cos', 'tan') else 'log'
            F.qin = True
            F.uk = (1, 1)
            F.u = key
            F.ushow = (key[0] if key[0] != 'logb' else 'log_' + _bshow(key[1][1] if key[1][0] == 'n'
                                                                       else key[1][1])) + ' ' + v
            return
    if hasfn(f, ('ln', 'log', 'logb'), v):
        F.kind = 'log'
        return
    if hasfn(f, ('abs',), v):
        F.kind = 'abs'
        return
    if hasfn(f, ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot'), v):
        F.kind = 'trig'
        return
    parts = []
    for t, sg in terms(f, 1, []):
        parts.append(tpart(t, v))
    kinds = []
    for a in parts:
        if a[0] not in kinds and a[0] != 'c':
            kinds.append(a[0])
    if kinds == ['x']:
        bases = []
        for a in parts:
            if a[0] == 'x' and a[1] not in bases:
                bases.append(a[1])
        F.bases = bases
        if len(bases) > 1:
            F.kind = 'exp2'
            return
        ms = [a[2] for a in parts if a[0] == 'x']
        q = None if None in ms else _quadin(ms)
        F.kind = 'exp'
        if q is not None:
            F.qin = True
            F.recip = q[1]
            F.uk = q[0]
            F.u = _utree_exp(bases[0], q[0], v)
            F.ushow = _ushow_exp(bases[0], q[0], v)
        return
    if kinds == ['p']:
        q = _quadin([a[1] for a in parts if a[0] == 'p'])
        if q is not None and not q[1]:
            F.kind = 'qpow'
            F.qin = True
            F.uk = q[0]
            F.u = _utree_pow(q[0], v)
            F.ushow = _ushow_pow(q[0], v)
            return
        neg = False
        for a in parts:
            if a[0] == 'p' and a[1][0] < 0:
                neg = True
        if neg and _ratfn(f, v):
            F.kind = 'rat'
            return
        F.kind = 'power'
        return
    if _ratfn(f, v):
        F.kind = 'rat'
        return
    F.kind = 'func'

def _ratfn(t, v):
    # a rational function of v: polynomials joined by + - * / and whole powers
    k = t[0]
    if k == 'n' or k == 'v':
        return True
    if k in ('+', '-', '*', '/'):
        return _ratfn(t[1], v) and _ratfn(t[2], v)
    if k == 'neg':
        return _ratfn(t[1], v)
    if k == '^':
        e = t[2]
        if not has(t, v):
            return True
        return e[0] == 'n' and isinstance(e[1], int) and _ratfn(t[1], v)
    return not has(t, v)

def _model(F, r):
    # name = C g(var) with one or two unknown constants: N = A e^(kt),
    # y = k b^x, y = a x^n
    ls = letters(r.f)
    v = F.var
    if v not in ls:
        return
    cs = [c for c in ls if c != v]
    if len(cs) != 2:
        return
    fs = factors(r.f, 1, [])
    if len(fs) != 2:
        return
    a, b = fs
    if a[1] < 0 or b[1] < 0:
        return
    a = a[0]
    b = b[0]
    if a[0] != 'v' or a[1] not in cs:
        a, b = b, a
    if a[0] != 'v' or a[1] not in cs:
        return
    c = a[1]
    k = cs[0] if cs[1] == c else cs[1]
    if b[0] == 'exp' and len(letters(b[1])) == 2 and has(b[1], k) and has(b[1], v):
        if lin(b[1], v) is not None:
            F.model = 'aekt'
    elif b[0] == '^' and b[1] == ('v', k) and b[2] == ('v', v):
        F.model = 'kbx'
    elif b[0] == '^' and b[1] == ('v', v) and b[2] == ('v', k):
        F.model = 'axn'
    if F.model:
        F.kind = 'model'
        F.consts = [c, k]

# ---- detected text ------------------------------------------------------------------------

DEGN = {1: 'linear', 2: 'quadratic', 3: 'cubic', 4: 'quartic'}

def _and(ls):
    if len(ls) < 2:
        return ''.join(ls)
    return ', '.join(ls[:-1]) + ' and ' + ls[-1]

def describe(F):
    if F.err:
        return F.err
    r = F.rows[0]
    v = F.var
    ls = F.letters
    k = F.kind
    if F.pair == 'simul':
        return 'two equations in ' + _and(F.vars2)
    if F.pair == 'fg':
        return 'f and g, functions of ' + v
    if F.pair == 'two':
        return 'two rows'
    eq = r.rel == '=' and r.name is None
    ineq = r.rel and r.rel != '='
    if k == 'num':
        return 'numbers: ' + ('surds and powers' if F.surd else ('logs' if F.logs else 'no letters'))
    if k == 'const':
        return 'expression in ' + _and(ls)
    if k == 'xy':
        return 'equation in ' + _and(F.vars2)
    if k == 'model':
        return 'model, ' + _and(F.consts) + ' unknown'
    if F.qin:
        s = 'quadratic in ' + F.ushow
    elif k == 'poly':
        s = DEGN.get(F.deg, 'degree ' + str(F.deg))
        s += (' inequality' if ineq else (' equation' if eq else '')) + ' in ' + v
    elif k == 'exp':
        s = 'exponential' + (' equation' if eq else '') + ', base ' + _bshow(F.bases[0])
    elif k == 'exp2':
        s = 'exponentials, bases ' + _and([_bshow(b) for b in F.bases])
    elif k == 'log':
        s = 'log ' + ('equation in ' + v if eq else ('inequality' if ineq else 'expression'))
    elif k == 'abs':
        s = 'modulus ' + ('equation' if eq else ('inequality' if ineq else 'function of ' + v))
    elif k == 'rat':
        s = 'fraction in ' + v if not eq else 'equation with fractions in ' + v
    elif k == 'trig':
        s = 'trig ' + ('equation' if eq else 'function') + ' in ' + v
    elif k == 'power':
        s = ('equation in ' if eq else 'powers of ') + v
    else:
        s = ('equation in ' if eq else ('inequality in ' if ineq else 'function of ')) + v
    if ineq and k != 'poly':
        s += ' (' + r.rel + ')'
    if ls:
        s += ', ' + _and(ls) + ' unknown'
    return s

# ---- entry point ------------------------------------------------------------------------

def form(texts):
    # texts: one or two typed rows -> Form
    F = Form()
    for t in texts:
        if t.strip():
            F.rows.append(parse_row(t))
    if not F.rows:
        F.err = 'type something first'
        return F
    for r in F.rows:
        if r.err:
            F.err = r.err if len(F.rows) == 1 else 'row ' + str(F.rows.index(r) + 1) + ': ' + r.err
            F.note = F.err
            return F
    for r in F.rows:
        if hasfloat(r.f):
            F.dec = True
    if len(F.rows) == 2:
        _pair(F)
    else:
        _one(F, F.rows[0])
    F.note = describe(F)
    return F

def _one(F, r):
    ls = letters(r.f)
    F.var = _pickvar(ls, r.name)
    F.vars2 = []
    if r.name is None and 'x' in ls and 'y' in ls and r.rel:
        F.kind = 'xy'
        F.var = 'x'
        F.vars2 = ['x', 'y']
        F.letters = [c for c in ls if c != 'x' and c != 'y']
        return
    F.letters = [c for c in ls if c != F.var]
    if r.name is not None and len(r.name) == 1 and r.rel == '=':
        _model(F, r)
        if F.model:
            return
    analyse(F, r.f, F.var)
    if F.kind == 'num':
        F.surd = anyfn(r.f, ('sqrt',)) or _fracpow(r.f)
        F.logs = anyfn(r.f, ('ln', 'log', 'logb'))

def _fracpow(t):
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k == '^' and rat(t[2]) is not None and rat(t[2])[1] != 1:
        return True
    for c in t[1:]:
        if _fracpow(c):
            return True
    return False

def anyfn(t, names):
    k = t[0]
    if k == 'n' or k == 'v':
        return False
    if k in names:
        return True
    for c in t[1:]:
        if anyfn(c, names):
            return True
    return False

def _pair(F):
    a, b = F.rows
    la = letters(a.f) + ([a.name] if a.name and len(a.name) == 1 else [])
    lb = letters(b.f) + ([b.name] if b.name and len(b.name) == 1 else [])
    ls = []
    for c in la + lb:
        if c not in ls:
            ls.append(c)
    fa = a.rel == '' or (a.name is not None and len(a.name) == 4)
    fb = b.rel == '' or (b.name is not None and len(b.name) == 4)
    F.vars2 = []
    if fa and fb:
        F.pair = 'fg'
        F.var = _pickvar(ls, a.name)
        F.letters = [c for c in ls if c != F.var]
        F.kind = 'pair'
        return
    if a.rel == '=' and b.rel == '=':
        vs = [c for c in ('x', 'y') if c in ls]
        if len(vs) < 2:
            vs = ls[:2]
        F.pair = 'simul'
        F.vars2 = vs
        F.var = vs[0] if vs else 'x'
        F.letters = [c for c in ls if c not in vs]
        F.kind = 'pair'
        return
    F.pair = 'two'
    F.kind = 'pair'
    F.letters = ls

def eqtree(r):
    # the row as one tree that is 0: name = f is name - f, l = r is l - r
    if r.name is not None and len(r.name) == 1:
        return ('-', ('v', r.name), r.f)
    return r.f

def from_trees(L, R):
    # an equation L = R built by an engine (f = g from two rows), read the same way
    F = Form()
    r = Row('')
    r.rel = '='
    r.lhs = L
    r.rhs = R
    r.f = ('-', L, R)
    F.rows = [r]
    F.dec = hasfloat(r.f)
    _one(F, r)
    F.note = describe(F)
    return F

# ---- Coord geometry: points in boxes, rows for lines and circles ------------------------

def tdeg(t, vs):
    # total degree in the letters vs (x and y), else None
    k = t[0]
    if k == 'n':
        return 0
    if k == 'v':
        return 1 if t[1] in vs else 0
    if k == '+' or k == '-':
        a = tdeg(t[1], vs)
        b = tdeg(t[2], vs)
        if a is None or b is None:
            return None
        return a if a > b else b
    if k == 'neg':
        return tdeg(t[1], vs)
    if k == '*':
        a = tdeg(t[1], vs)
        b = tdeg(t[2], vs)
        if a is None or b is None:
            return None
        return a + b
    if k == '/':
        if tdeg(t[2], vs) != 0:
            return None
        return tdeg(t[1], vs)
    if k == '^':
        e = t[2]
        d = tdeg(t[1], vs)
        if d == 0 and tdeg(e, vs) == 0:
            return 0
        if d is None or e[0] != 'n' or not isinstance(e[1], int) or e[1] < 0:
            return None
        return d * e[1]
    for v in vs:
        if has(t, v):
            return None
    return 0

def _geokind(r, F):
    # a row: 'line', 'circle', 'curve', or 'x(t)' / 'y(t)' / 'expr' for a
    # parametric pair
    if r.rel != '=':
        return 'expr'
    if r.name in ('x', 'y'):
        ls = letters(r.f)
        if [c for c in ls if c not in ('x', 'y')] and 'x' not in ls and 'y' not in ls:
            return r.name + '(t)'
    E = recog_eq(r)
    d = tdeg(E, ('x', 'y'))
    if d is not None and d <= 1:
        return 'line'
    if d == 2:
        import eng
        cx = eng.coeffs(E, 'x')
        cy = eng.coeffs(E, 'y')
        if cx is not None and cy is not None and len(cx) == 3 and len(cy) == 3:
            if not has(cx[1], 'y') and not has(cy[1], 'x') and \
                    eng.S(('-', cx[2], cy[2])) == ('n', 0) and not has(cx[2], 'y'):
                return 'circle'
    return 'curve'

def recog_eq(r):
    # the row as one tree that is 0
    if r.name is not None and len(r.name) == 1:
        return ('-', ('v', r.name), r.f)
    return ('-', r.lhs, r.rhs) if r.rel else r.f

def geo(pts, eqs):
    # pts: [(x text, y text)] from the boxes A, B, C; eqs: typed rows
    F = Form()
    F.kind = 'geo'
    F.points = []
    F.items = []
    for i in range(len(pts)):
        xs, ys = pts[i]
        nm = 'ABC'[i]
        if not xs.strip() and not ys.strip():
            continue
        if not xs.strip() or not ys.strip():
            F.err = nm + ': fill in both boxes'
            F.note = F.err
            return F
        try:
            xt = caslex.parse(xs)
            yt = caslex.parse(ys)
        except ValueError as e:
            F.err = nm + ': ' + str(e)
            F.note = F.err
            return F
        if xt is None or yt is None:
            F.err = nm + ': cannot read that'
            F.note = F.err
            return F
        F.points.append((nm, xt, yt))
    for t in eqs:
        r = parse_row(t)
        if r.err:
            F.err = r.err
            F.note = F.err
            return F
        F.rows.append(r)
    for r in F.rows:
        F.items.append(_geokind(r, F))
        if hasfloat(r.f):
            F.dec = True
    ks = F.items
    if len(ks) == 2 and sorted([k[0] for k in ks if k in ('x(t)', 'y(t)')]) == ['x', 'y'] or \
            ks == ['expr', 'expr']:
        F.items = ['param']
    ls = []
    for p in F.points:
        letters(p[1], ls)
        letters(p[2], ls)
    for r in F.rows:
        letters(r.f, ls)
        if r.name is not None and len(r.name) == 1 and r.name not in ls:
            ls.append(r.name)
    if F.items == ['param']:
        tv = [c for c in ls if c not in ('x', 'y')]
        F.var = tv[0] if tv else 't'
        F.letters = [c for c in tv if c != F.var]
    else:
        F.var = 'x'
        F.letters = [c for c in ls if c not in ('x', 'y')]
    for p in F.points:
        if hasfloat(p[1]) or hasfloat(p[2]):
            F.dec = True
    F.note = _geonote(F)
    return F

def _geonote(F):
    n = len(F.points)
    names = [p[0] for p in F.points]
    parts = []
    if F.items == ['param']:
        parts.append('parametric x(' + F.var + '), y(' + F.var + ')')
    else:
        for k in F.items:
            parts.append({'line': 'line', 'circle': 'circle', 'curve': 'curve',
                          'expr': 'curve y = f(x)'}.get(k, k))
        if len(parts) == 2 and parts[0] == parts[1]:
            parts = ['two ' + parts[0] + 's']
    if n == 1:
        parts.append('point ' + names[0])
    elif n > 1:
        parts.append(str(n) + ' points ' + _and(names))
    if not parts:
        return 'nothing filled in'
    s = _and(parts)
    if F.letters:
        s += ', ' + _and(F.letters) + ' unknown'
    return s
