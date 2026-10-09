# Shared helpers for the topic engines (e_*.py): trees as calculator text
# (log_2 12, 9 - 4k), the boxed answer and its decimal, coefficients, and a
# step-by-step rearranger whose steps are the working lines.
# An engine returns a list of lines for topic.answer(): str or ('m', tree)
# working; ('w', s) a grey note; ('!', s) a warning; ('=', pre, exact,
# decimal) a boxed answer; lines after the box follow it (vertex and so on).
import caseng
import caspoly
import casui

X = ('v', 'x')
ZERO = ('n', 0)
ONE = ('n', 1)

def N(v):
    return ('n', v)

def S(t):
    # caseng.simplify, but exact logs stay exact: it would make log_2 3 a
    # decimal, so they are hidden as letters while it works
    hid = []
    t2 = _hide(t, hid)
    r = caseng.simplify(t2)
    return _unhide(r, hid) if hid else r

def E_(t):
    return E(t)

def E(t):
    # caspoly.expand with exact logs kept, as S
    hid = []
    t2 = _hide(t, hid)
    r = caspoly.expand(t2)
    return _unhide(r, hid) if hid else r

def _floaty(t):
    k = t[0]
    if k == 'n':
        return isinstance(t[1], float)
    if k == 'v':
        return False
    for c in t[1:]:
        if _floaty(c):
            return True
    return False

def _hide(t, hid):
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if (k == 'logb' or k == 'log') and not _hasvar(t):
        if t in hid:
            return ('v', 'zl' + str(hid.index(t)))
        hid.append(t)
        return ('v', 'zl' + str(len(hid) - 1))
    return (k,) + tuple([_hide(c, hid) for c in t[1:]])

def _unhide(t, hid):
    k = t[0]
    if k == 'v' and t[1][:2] == 'zl':
        return hid[int(t[1][2:])]
    if k == 'n' or k == 'v':
        return t
    return (k,) + tuple([_unhide(c, hid) for c in t[1:]])

def R(p, q=1):
    # rational as a tree: 3/2, -3/2
    if q == 1:
        return ('n', p)
    if p < 0:
        return ('neg', ('/', ('n', -p), ('n', q)))
    return ('/', ('n', p), ('n', q))

# ---- trees -> text ------------------------------------------------------------------------

def neg(t):
    # (True, |t|) when t prints with a leading minus
    k = t[0]
    if k == 'n':
        v = t[1]
        if not isinstance(v, complex) and v < 0:
            return (True, ('n', -v))
        return (False, t)
    if k == 'neg':
        return (True, t[1])
    if k == '*' or k == '/':
        a = neg(t[1])
        if a[0]:
            if a[1] == ONE and k == '*':
                return (True, t[2])
            return (True, (k, a[1], t[2]))
    if k == '+' or k == '-':
        # every term negative: -k - 1 is -(k + 1)
        ts = sumterms(t, 1, [])
        out = []
        for a, sg in ts:
            n, b = neg(a)
            if (sg > 0) == n:
                out.append((b, 1))
            else:
                return (False, t)
        return (True, build(out))
    return (False, t)

def sumterms(t, sg, out):
    k = t[0]
    if k == '+':
        sumterms(t[1], sg, out)
        sumterms(t[2], sg, out)
    elif k == '-':
        sumterms(t[1], sg, out)
        sumterms(t[2], -sg, out)
    elif k == 'neg' and out:
        sumterms(t[1], -sg, out)
    else:
        out.append((t, sg))
    return out

def build(ts):
    # [(term, sign)] -> tree, a minus for each negative term
    out = None
    for t, sg in ts:
        n, a = neg(t)
        if n:
            sg = -sg
            t = a
        if out is None:
            out = t if sg > 0 else ('neg', t)
        else:
            out = ('+' if sg > 0 else '-', out, t)
    return ZERO if out is None else out

def _isnum(t):
    k = t[0]
    if k == 'n':
        return True
    if k == '/' or k == '*':
        return _isnum(t[1]) and _isnum(t[2])
    return False

def _const(t):
    # a log or root of numbers: goes after a letter in a product (x ln 5)
    k = t[0]
    return k in ('ln', 'log', 'logb', 'sqrt') and not _hasvar(t)

def order(t, top=True):
    # a positive term first (9 - 4k, not -4k + 9); in a sum of numbers the
    # plain number first (2 + log_2 3, 5 - sqrt 57); x ln 5 not ln 5 x.
    # top False keeps the outer sum in the order it was built.
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    if k == 'exp':
        return ('^', ('v', 'e'), order(t[1]))
    if k == '+' or k == '-':
        ts = sumterms(t, 1, [])
        ts = [(order(a), s) for a, s in ts]
        sg = []
        for a, s in ts:
            n, b = neg(a)
            sg.append((b, -s if n else s))
        if not _hasvar(t):
            for i in range(len(sg)):
                if _isnum(sg[i][0]):
                    pos = [x for x in sg if x[1] > 0]
                    if sg[i][1] > 0 or not pos:
                        sg.insert(0, sg.pop(i))
                    break
        if sg[0][1] < 0 and top:
            i = 1
            while i < len(sg) and sg[i][1] < 0:
                i += 1
            if i < len(sg):
                sg.insert(0, sg.pop(i))
        return build(sg)
    if k == '*' and _const(t[1]) and _hasvar(t[2]) and not _const(t[2]):
        return ('*', order(t[2]), order(t[1]))
    return (k,) + tuple([order(c) for c in t[1:]])

def _close(s, i):
    # index after the bracket opened at s[i]
    d = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return i + 1
        i += 1
    return n

def _comma(s, i, j):
    d = 0
    while i < j:
        c = s[i]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif c == ',' and d == 0:
            return i
        i += 1
    return -1

def _simple(a):
    # a number or one letter: needs no brackets after a log
    if not a:
        return False
    if a.isalpha() and (len(a) == 1 or a == 'pi'):
        return True
    for c in a:
        if not (c.isdigit() or c == '.'):
            return False
    return True

_AFTER = ('', ' ', ')', '+', '-', '=', ',')   # ln 12 needs no brackets before these

def _pows(s):
    # e^(x) -> e^x, 2^(3) -> 2^3
    out = ''
    i = 0
    n = len(s)
    while i < n:
        if s.startswith('^(', i):
            j = _close(s, i + 1)
            a = s[i + 2:j - 1]
            if _simple(a):
                out += '^' + a
                i = j
                continue
        out += s[i]
        i += 1
    return out

def _logs(s):
    # logb(2,12) -> log_2 12; ln(12) -> ln 12; log(x+1) stays
    out = ''
    i = 0
    n = len(s)
    while i < n:
        if s.startswith('logb(', i):
            j = _close(s, i + 4)
            c = _comma(s, i + 5, j - 1)
            if c > 0:
                b = s[i + 5:c]
                a = s[c + 1:j - 1]
                if b == 'e':
                    out += 'ln'
                elif b == '10':
                    out += 'log'
                else:
                    out += 'log_' + (b if _simple(b) else '(' + b + ')')
                if _simple(a) and s[j:j + 1] in _AFTER:
                    out += ' ' + a
                else:
                    out += '(' + _logs(a) + ')'
                i = j
                continue
        for f in ('ln(', 'log('):
            if s.startswith(f, i) and (i == 0 or not s[i - 1].isalpha()):
                j = _close(s, i + len(f) - 1)
                a = s[i + len(f):j - 1]
                if _simple(a) and s[j:j + 1] in _AFTER:
                    out += f[:-1] + ' ' + a
                    i = j
                    break
        else:
            out += s[i]
            i += 1
    return out

def _fhide(t, fl):
    # decimals print as typed (to 7 s.f.), not tostr's 6
    k = t[0]
    if k == 'n':
        v = t[1]
        if isinstance(v, float):
            if v < 0:
                return ('neg', _fhide(('n', -v), fl))
            fl.append(v)
            return ('v', 'zf' + str(len(fl) - 1))
        return t
    if k == 'v':
        return t
    return (k,) + tuple([_fhide(c, fl) for c in t[1:]])

def txt(t, top=True):
    fl = []
    s = caseng.tostr(_fhide(order(t, top), fl))
    if fl:
        i = len(fl) - 1
        while i >= 0:
            s = s.replace('zf' + str(i), sf(fl[i], 7))
            i -= 1
    if 'log' in s or 'ln' in s:
        s = _logs(s)
    if '^(' in s:
        s = _pows(s)
    return _spaced(s)

def _spaced(s):
    # binary + and - with spaces round them, as the mark scheme writes them
    # (the typesetter gives 2^x+3 no room); not inside a power's brackets
    out = ''
    i = 0
    n = len(s)
    exp = []        # bracket depths that belong to powers
    d = 0
    while i < n:
        c = s[i]
        if c == '(':
            d += 1
            if i > 0 and s[i - 1] == '^':
                exp.append(d)
        elif c == ')':
            if exp and exp[-1] == d:
                exp.pop()
            d -= 1
        elif (c == '+' or c == '-') and not exp and i > 0 and \
                ((s[i - 1].isalpha() or s[i - 1].isdigit()) or s[i - 1] == ')' or s[i - 1] == '.') and i + 1 < n and s[i + 1] != ' ':
            if s[i - 1] == 'e' and i > 1 and s[i - 2].isdigit():
                out += c
                i += 1
                continue
            out += ' ' + c + ' '
            i += 1
            continue
        out += c
        i += 1
    return out

def eq(l, r):
    return txt(l) + ' = ' + txt(r)

# ---- numbers ---------------------------------------------------------------------------

def val(t, env=None):
    # numeric value of a tree without letters (or with env), else None
    try:
        v = caseng.evalf(t, 0.0, casui.DEG, env)
    except Exception:
        return None
    if isinstance(v, complex):
        if abs(v.imag) > 1e-12 * (1 + abs(v.real)):
            return v
        v = v.real
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

def sf(v, n):
    # v to n significant figures, as text (casutil._sf, kept here so the
    # topic screens don't load casutil)
    import math
    if v == 0:
        return '0'
    neg = v < 0
    av = -v if neg else v
    e = int(math.floor(math.log10(av)))
    # half up, as taught: 180.5 to 3 s.f. is 181
    mi = int(math.floor(av / (10.0 ** (e - n + 1)) + 0.5 + 1e-9))
    if mi >= 10 ** n:
        mi //= 10
        e += 1
    d = str(mi)
    if e >= n + 3 or e < -4:
        frac = d[1:].rstrip('0')
        s = d[0] + ('.' + frac if frac else '') + 'e' + str(e)
    elif e >= n - 1:
        s = d + '0' * (e - n + 1)
    elif e >= 0:
        s = (d[:e + 1] + '.' + d[e + 1:]).rstrip('0').rstrip('.')
    else:
        s = ('0.' + '0' * (-e - 1) + d).rstrip('0')
    return '-' + s if neg else s

def dec(v):
    # decimal per the Decimals setting: '3.58 (3 s.f.)'
    d = casui.SET['decimals']
    n = int(d[0])
    if isinstance(v, complex):
        return caseng.cstr(v, lambda x: sf(x, n))
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    s10 = sf(v, 10)
    digs = len(s10.replace('-', '').replace('.', '').lstrip('0'))
    if 'e' not in s10 and (digs <= n if d[1:] == 'sf' else len(s10.split('.')[1]) <= n):
        return s10
    if 'e' not in s10 and digs <= n + 1 and d[1:] == 'sf':
        # an exact decimal one digit longer (180.5 at 3 s.f.): all of it
        return s10
    if d[1:] == 'sf':
        s = sf(v, n)
        if 'e' not in s:
            # the trailing zeros count: 49.0 to 3 s.f., not 49
            digs = len(s.replace('-', '').replace('.', '').lstrip('0'))
            if digs < n:
                s += ('' if '.' in s else '.') + '0' * (n - digs)
        return s + ' (' + str(n) + ' s.f.)'
    s = ('%.' + str(n) + 'f') % v
    return s + ' (' + str(n) + ' d.p.)'

def box(pre, t, exact=True):
    # boxed answer pre + t: the exact text and, when t has a value, its
    # decimal; a typed decimal (exact False) leaves the decimal only
    ex = txt(t)
    v = val(t)
    dc = None
    if v is not None:
        dc = dec(v)
        if dc == ex:
            dc = None
    if dc is not None and ('.' in ex or not exact):
        ex = None
    return ('=', pre, ex, dc, t)

def boxt(pre, t, top=True):
    # boxed tree, no decimal (an expression with letters)
    return ('=', pre, txt(t, top), None, t)

def pair(names, vals, exact=True):
    # x = 11, y = -ln(48/55)/2, with the decimals when they say more
    ex = ',  '.join([n + ' = ' + txt(t) for n, t in zip(names, vals)])
    ds = []
    more = False
    for n, t in zip(names, vals):
        v = val(t)
        d = dec(v) if v is not None else None
        if d is not None and d != txt(t):
            more = True
        ds.append(n + ' = ' + (d if d is not None else txt(t)))
    dc = ',  '.join(ds) if more else None
    if dc is not None and ('.' in ex or not exact):
        ex = None
    return ('=', '', ex, dc, None)

def boxs(pre, s, t=None):
    # boxed text with no decimal (t: the tree it shows, when there is one)
    return ('=', pre, s, None, t)

def powlog(b, R):
    # b^R with b's logs in R undone: 2^(9 + log_2 y^2) = 512 y^2,
    # a^(2 log_a 7 + 1/2) = 49 sqrt a; None when R has no such log
    import recog
    got = []
    rest = []
    for t, sg in sumterms(R, 1, []):
        lg = None
        c = []
        for f, e in recog.factors(t, 1, []):
            fb = None
            if f[0] == 'logb':
                fb, fa = f[1], f[2]
            elif f[0] == 'ln':
                fb, fa = ('v', 'e'), f[1]
            elif f[0] == 'log':
                fb, fa = N(10), f[1]
            if fb is not None and fb == b and e > 0 and lg is None:
                lg = fa
            else:
                c.append((f, e))
        if lg is None:
            rest.append((t, sg))
            continue
        ct = N(sg)
        for f, e in c:
            ct = ('*', ct, f) if e > 0 else ('/', ct, f)
        got.append(('^', lg, S(ct)))
    if not got:
        return None
    out = got[0]
    for g in got[1:]:
        out = ('*', out, g)
    if rest:
        out = ('*', out, ('^', b, build(rest)) if b != ('v', 'e') else ('exp', build(rest)))
    return S(out)

# ---- polynomials ----------------------------------------------------------------------------

def coeffs(f, v):
    # [c0, c1, ..] as trees (letters allowed), or None. Like
    # cassolve.pcoeffs, but here so a quadratic in x with a k in it doesn't
    # load cassolve (and cascalc with it)
    p = caspoly.poly(f, v)
    if p is not None:
        out = [caspoly.ratnode(c) for c in p]
        return out if out else [ZERO]
    g = S(f)
    if g[0] == '/' and not has(g[2], v):
        co = coeffs(g[1], v)
        return None if co is None else [S(('/', c, g[2])) for c in co]
    g = caspoly.expand(g)
    co = {}
    top = 0
    for t, sg in sumterms(g, 1, []):
        r = caspoly.term_of(t)
        if r is None:
            return None
        c, facs = r
        k = 0
        rest = []
        for key, base, e in facs:
            if base == ('v', v):
                k += e
            elif has(base, v):
                return None
            else:
                rest.append((key, base, e))
        if k < 0 or k > 12 or k != int(k):
            return None
        k = int(k)
        term = caspoly.term_node(c if sg > 0 else caspoly.rneg(c), rest)
        if k in co:
            co[k].append((term, 1))
        else:
            co[k] = [(term, 1)]
        if k > top:
            top = k
    out = [S(build(co[i])) if i in co else ZERO for i in range(top + 1)]
    while len(out) > 1 and out[-1] == ZERO:
        out.pop()
    return out

def ptree(co, v):
    # coefficient trees -> a x^2 + b x + c, highest power first
    ts = []
    i = len(co) - 1
    V = ('v', v) if isinstance(v, str) else v
    while i >= 0:
        c = co[i]
        if c != ZERO:
            if i == 0:
                ts.append((c, 1))
            else:
                p = V if i == 1 else ('^', V, N(i))
                n, a = neg(c)
                if a == ONE:
                    t = p
                elif a[0] in ('+', '-'):
                    t = ('*', a, p)
                else:
                    t = ('*', a, p)
                ts.append((t, -1 if n else 1))
        i -= 1
    return build(ts)

def mul(a, b):
    if a == ONE:
        return b
    if b == ONE:
        return a
    return ('*', a, b)

def add(a, b):
    # a + b written a - |b| when b is negative
    n, c = neg(b)
    if c == ZERO:
        return a
    return ('-', a, c) if n else ('+', a, c)

def sq(t):
    return ('^', t, N(2))

def decimal(c):
    # 9/100 -> 0.09 when the question was typed in decimals
    r = caspoly.ratof(c)
    if r is None or r[1] == 1:
        return c
    q = r[1]
    while q % 2 == 0:
        q //= 2
    while q % 5 == 0:
        q //= 5
    return N(r[0] / float(r[1])) if q == 1 else c

# ---- rearranging, one inverse operation a line ------------------------------------------------

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

def count(t, v):
    k = t[0]
    if k == 'v':
        return 1 if t[1] == v else 0
    if k == 'n':
        return 0
    n = 0
    for c in t[1:]:
        n += count(c, v)
    return n

def logto(b, r):
    # log base b of r as a tree: ln for e, log for 10; log a^n = n log a
    if r[0] == '^' and not _hasvar(r):
        return mul(r[2], logto(b, r[1]))
    if b == ('v', 'e'):
        return ('ln', r)
    if b == ('n', 10):
        return ('log', r)
    return ('logb', b, r)

def _prodfac(t, v, out):
    k = t[0]
    if k == '*':
        _prodfac(t[1], v, out)
        _prodfac(t[2], v, out)
    else:
        out.append(t)
    return out

class Stuck(Exception):
    pass

def isolate(L, Rt, v, lines, depth=0):
    # L = Rt with v once in L: undo the outer operation a line at a time.
    # Returns the list of answers (two after an even root); lines gets
    # each step as 'L = R'.
    if depth > 30:
        raise Stuck()
    if L == ('v', v):
        n = nice(Rt)
        if n != Rt and lines and txt(n) != txt(Rt):
            lines.append(eq(L, n))
        return [n]
    k = L[0]
    if k == '+' or k == '-' or (k == 'neg' and L[1][0] in ('+', '-')):
        ts = sumterms(L, 1, [])
        keep = [(t, s) for t, s in ts if has(t, v)]
        move = [(t, -s) for t, s in ts if not has(t, v)]
        if len(keep) != 1:
            raise Stuck()
        if move:
            t, sg = keep[0]
            rt = sumterms(Rt, 1, []) if Rt != ZERO else []
            if sg > 0:
                R2 = S(build(rt + move))
            else:
                # 10 - 2x = c: 2x = 10 - c
                R2 = S(build([(a, -b) for a, b in move] + [(a, -b) for a, b in rt]))
            lines.append(eq(t, R2))
            return isolate(t, R2, v, lines, depth + 1)
        L = keep[0][0] if keep[0][1] > 0 else ('neg', keep[0][0])
        k = L[0]
    if k == 'neg':
        R2 = S(('neg', Rt))
        lines.append(eq(L[1], R2))
        return isolate(L[1], R2, v, lines, depth + 1)
    if k == '*':
        fs = _prodfac(L, v, [])
        keep = [f for f in fs if has(f, v)]
        c = [f for f in fs if not has(f, v)]
        if len(keep) != 1:
            raise Stuck()
        cc = c[0]
        for f in c[1:]:
            cc = ('*', cc, f)
        R2 = S(('/', Rt, cc))
        lines.append(eq(keep[0], R2))
        return isolate(keep[0], R2, v, lines, depth + 1)
    if k == '/':
        a, b = L[1], L[2]
        if has(a, v) and not has(b, v):
            R2 = S(('*', Rt, b))
            lines.append(eq(a, R2))
            return isolate(a, R2, v, lines, depth + 1)
        if has(b, v) and not has(a, v):
            R2 = S(('/', a, Rt))
            lines.append(eq(b, R2))
            return isolate(b, R2, v, lines, depth + 1)
        raise Stuck()
    if k == 'exp':
        _pos(Rt)
        R2 = S(('ln', Rt))
        lines.append(eq(L[1], ('ln', Rt)))
        return isolate(L[1], R2, v, lines, depth + 1)
    if k == '^':
        b, e = L[1], L[2]
        if not has(b, v):
            _pos(Rt)
            R2 = logto(b, Rt)
            lines.append(eq(e, R2))
            return isolate(e, R2, v, lines, depth + 1)
        if not has(e, v):
            ev = val(e)
            if ev is not None and ev == int(ev) and int(ev) % 2 == 0 and ev != 0:
                _pos(Rt, True)
                root = ('^', Rt, S(('/', ONE, e))) if ev != 2 else ('sqrt', Rt)
                root = S(root)
                lines.append(txt(b) + ' = +-' + _br(txt(root)))
                out = []
                for r in (root, S(('neg', root))):
                    out += isolate(b, r, v, lines, depth + 1)
                return out
            R2 = S(('^', Rt, S(('/', ONE, e))))
            lines.append(eq(b, R2))
            return isolate(b, R2, v, lines, depth + 1)
        raise Stuck()
    if k == 'sqrt':
        _pos(Rt, True)
        R2 = S(('^', Rt, N(2)))
        lines.append(eq(L[1], R2))
        return isolate(L[1], R2, v, lines, depth + 1)
    if k == 'ln' or k == 'log' or (k == 'logb' and not has(L[1], v)):
        b = ('v', 'e') if k == 'ln' else (N(10) if k == 'log' else L[1])
        g = L[1] if k != 'logb' else L[2]
        raw = ('exp', Rt) if k == 'ln' else ('^', b, Rt)
        R2 = powlog(b, Rt) or S(raw)
        if txt(R2) != txt(raw) and k == 'logb':
            lines.append(eq(g, raw))
        lines.append(eq(g, R2))
        return isolate(g, R2, v, lines, depth + 1)
    raise Stuck()

def _br(s):
    if _simple(s):
        return s
    i = s.find('(')
    if i > 0 and s[:i].isalpha() and _close(s, i) == len(s):
        return s
    return '(' + s + ')'

class NoRoot(Exception):
    pass

def _pos(t, zero=False):
    # a^x = t, sqrt = t, even power = t need t > 0 (>= 0): refuse at once
    v = val(t)
    if v is None or isinstance(v, complex):
        return
    if v < 0 or (v == 0 and not zero):
        raise NoRoot(txt(t))

def _lcm(a, b):
    import recog
    return a * b // recog._gcd(a, b)

def _intscale(ts):
    # the number that clears the fractions from rational coefficients, or 1
    import recog
    m = 1
    for t, sg in ts:
        for f, e in recog.factors(t, 1, []):
            r = caspoly.ratof(f)
            if r is None:
                continue
            q = r[1] if e > 0 else abs(r[0])
            if q > 1:
                m = _lcm(m, q)
    return m

def _hasvar(t):
    k = t[0]
    if k == 'v':
        return t[1] not in ('pi', 'e')
    if k == 'n':
        return False
    for c in t[1:]:
        if _hasvar(c):
            return True
    return False

def clearfrac(L, Rt, v, lines):
    # v in a denominator: multiply up (y = (2x+3)/(x-2) -> y(x - 2) = 2x + 3)
    changed = False
    if Rt[0] == '/' and has(Rt[2], v):
        L = ('*', L, Rt[2]) if L[0] not in ('+', '-') else ('*', Rt[2], L)
        Rt = Rt[1]
        changed = True
    if L[0] == '/' and has(L[2], v):
        Rt = ('*', Rt, L[2]) if Rt[0] not in ('+', '-') else ('*', L[2], Rt)
        L = L[1]
        changed = True
    if changed:
        lines.append(eq(L, Rt))
    return L, Rt

def linin(E, v):
    # E = a v + b with a, b free of v: (a, b), else None. The coefficients
    # first (no casalg needed), casalg.linin when they hold logs and the like
    co = coeffs(E, v)
    if co is not None:
        if len(co) == 2:
            return (co[1], co[0])
        if len(co) == 1:
            return (ZERO, co[0])
        return None
    import casalg
    return casalg.linin(E, v)

def collect(L, Rt, v, lines):
    # v in several places but linear: gather the v terms, take v out, divide
    E = E_(S(('-', L, Rt)))
    r = linin(E, v)
    if r is None or r[0] == ZERO or has(r[0], v) or has(r[1], v):
        raise Stuck()
    a = S(r[0])
    b = S(('neg', r[1]))
    flip = neg(a)[0] or (neg(b)[0] and caspoly.ratof(a) is None)
    if flip:
        a = S(('neg', a))
        b = S(('neg', b))
    m = _intscale(sumterms(a, 1, []) + sumterms(b, 1, []))
    if m != 1:
        a = S(('*', N(m), a))
        b = S(('*', N(m), b))
    ts = sumterms(E, 1, [])
    vt = [(t, -s if flip else s) for t, s in ts if has(t, v)]
    V = ('v', v)
    if len(vt) > 1 and m == 1:
        lines.append(txt(build(vt)) + ' = ' + txt(b))
    if a[0] in ('+', '-'):
        lines.append(txt(('*', V, a)) + ' = ' + txt(b))
    else:
        lines.append(txt(mul(a, V) if a != ONE else V) + ' = ' + txt(b))
    out = S(('/', b, a))
    if a != ONE:
        lines.append(txt(V) + ' = ' + txt(out))
    return [out]

def solve_for(L, Rt, v, lines):
    # rearrange L = Rt for v, writing the steps; -> answers
    if has(Rt, v) and not has(L, v):
        L, Rt = Rt, L
        lines.append(eq(L, Rt))
    if not has(Rt, v) and count(L, v) == 1:
        return isolate(L, Rt, v, lines)
    L, Rt = clearfrac(L, Rt, v, lines)
    try:
        return collect(L, Rt, v, lines)
    except Stuck:
        pass
    E = S(('-', L, Rt))
    if count(E, v) == 1:
        lines.append(eq(E, ZERO))
        return isolate(E, ZERO, v, lines)
    raise Stuck()

def _hassq(t):
    k = t[0]
    if k == 'sqrt':
        return True
    if k in ('n', 'v'):
        return False
    for c in t[1:]:
        if _hassq(c):
            return True
    return False

def _nested(t):
    # a fraction inside a numerator: (5y^2 - 1/2)/y^2
    if t[0] == '/':
        return _hasfrac(t[1])
    for c in t[1:]:
        if isinstance(c, tuple) and c[0] not in ('n', 'v') and _nested(c):
            return True
    return False

def _hasfrac(t):
    k = t[0]
    if k == '/':
        return True
    if k == 'n' or k == 'v':
        return False
    for c in t[1:]:
        if _hasfrac(c):
            return True
    return False

def tidylog(t):
    # exact logs: log_2 12 -> 2 + log_2 3, log_2 1 -> 0, log_a a^p -> p,
    # and 2^(-log_2 A) -> 1/A
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    t = (k,) + tuple([tidylog(c) for c in t[1:]])
    if k == '^' and not _hasvar(t[1]) and _haslogs(t[2]):
        p = powlog(t[1], t[2])
        if p is not None:
            return p
    if k == 'exp' and _haslogs(t[1]):
        p = powlog(('v', 'e'), t[1])
        if p is not None:
            return p
    if k == 'logb' or k == 'ln' or k == 'log':
        b = t[1] if k == 'logb' else (('v', 'e') if k == 'ln' else N(10))
        a = t[2] if k == 'logb' else t[1]
        if a == ONE:
            return ZERO
        if a == b:
            return ONE
        if a[0] == '^' and a[1] == b and not has(a[2], 'x'):
            return a[2]
        if a[0] == 'exp' and b == ('v', 'e'):
            return a[1]
        p = _powof(a, b)
        if p is not None:
            return p
        if k == 'logb':
            r = lograt(t)
            if r is not None:
                return r
    return t

def _haslogs(t):
    k = t[0]
    if k in ('ln', 'log', 'logb'):
        return True
    if k in ('n', 'v'):
        return False
    for c in t[1:]:
        if _haslogs(c):
            return True
    return False

def _powof(a, b):
    # a as a power of b (b^2 sqrt b -> 5/2), else None
    import recog
    tot = ZERO
    for f, e in recog.factors(S(a), 1, []):
        if f == b:
            p = ONE
        elif f[0] == '^' and f[1] == b and not _hasvar(f[2]):
            p = f[2]
        elif f[0] == 'sqrt' and f[1] == b:
            p = ('/', ONE, N(2))
        elif f[0] == 'exp' and b == ('v', 'e'):
            p = f[1]
        else:
            return None
        tot = ('+', tot, p) if e > 0 else ('-', tot, p)
    return S(tot)

def _powdist(t):
    # (512 y^2)^(1/3) -> 8 y^(2/3): a fractional power of a product, factor
    # by factor
    import recog
    k = t[0]
    if k == 'n' or k == 'v':
        return t
    t = (k,) + tuple([_powdist(c) for c in t[1:]])
    if k == 'sqrt' and t[1][0] == '^' and recog.rat(t[1][2]) is not None:
        return S(('^', t[1][1], S(('/', t[1][2], N(2)))))
    if k == '^' and t[1][0] == '^' and recog.rat(t[2]) is not None and recog.rat(t[1][2]) is not None:
        # (y^2)^(1/3) -> y^(2/3), as the mark scheme writes it
        return S(('^', t[1][1], S(('*', t[1][2], t[2]))))
    if k == '^' and t[1][0] in ('*', '/') and recog.rat(t[2]) is not None:
        out = None
        for f, e in recog.factors(t[1], 1, []):
            g = S(('^', f, t[2]))
            if g[0] == '^' and g[1][0] == '^' and recog.rat(g[1][2]) is not None:
                g = S(('^', g[1][1], S(('*', g[1][2], t[2]))))
            out = g if out is None else (('*', out, g) if e > 0 else ('/', out, g))
        if e < 0 and out is not None and len(recog.factors(t[1], 1, [])) == 1:
            out = ('/', ONE, out)
        return S(out)
    return t

def nice(t):
    # the tidiest of a few equal forms: no fraction inside a numerator, then
    # the shortest (5 - 1/(2y^2) over (5y^2 - 1/2)/y^2)
    t = S(tidylog(t))
    cands = [t]
    pd = _powdist(t)
    if pd != t:
        cands.append(pd)
    if t[0] == '/' and t[2][0] not in ('+', '-'):
        ts = sumterms(t[1], 1, [])
        if len(ts) > 1:
            cands.append(build([(S(('/', a, t[2])), b) for a, b in ts]))
    if t[0] == '/' and _hasvar(t):
        e = E(t)
        if e != t:
            cands.append(e)
    elif t[0] in ('*', '+', '-'):
        cands.append(S(E(t)))
    if t[0] == '/' and not _hasvar(t) and _hassq(t[2]):
        import casalg
        try:
            r = casalg.rationalise(t)
            if r is not None:
                cands.append(S(r))
        except Exception:
            pass
    if t[0] == '/' and _hasfrac(t[1]):
        m = _intscale(sumterms(t[1], 1, []))
        if m > 1:
            cands.append(('/', caspoly.expand(S(('*', N(m), t[1]))), S(('*', N(m), t[2]))))
    best = None
    exact = not _floaty(t)
    for c in cands:
        if exact and _floaty(c):
            continue    # a form that went to decimals is not the same answer
        key = (_nested(c), len(txt(c)))
        if best is None or key < best[0]:
            best = (key, c)
    return best[1]

# ---- exact logs ------------------------------------------------------------------------------

def _ipow(n, b):
    # n = b^k m: -> (k, m)
    k = 0
    while n % b == 0 and n > 1:
        n //= b
        k += 1
    return (k, n)

def logsplit(b, r):
    # log_b of a rational r as k + log_b(rest): log_2 12 = 2 + log_2 3;
    # None when nothing comes out
    if b < 2 or r is None:
        return None
    p, q = r
    if p <= 0:
        return None
    k1, p2 = _ipow(p, b)
    k2, q2 = _ipow(q, b)
    k = k1 - k2
    if k == 0:
        return None
    rest = R(p2, q2) if q2 != 1 else N(p2)
    if (p2, q2) == (1, 1):
        return N(k)
    return add(N(k), ('logb', N(b), rest)) if k > 0 else \
        ('-', ('logb', N(b), rest), N(-k))

def lograt(t):
    # log_b r with b an integer base and r rational: the split form, else None
    if t[0] != 'logb':
        return None
    b = caspoly.ratof(t[1])
    r = caspoly.ratof(t[2])
    if b is None or b[1] != 1 or r is None:
        return None
    # log_8 2 = 1/3 and log_4 8 = 3/2: both powers of one base
    import recog
    rb = recog.rootbase(t[1])
    rr = recog.rootbase(t[2])
    if rb and rr and rb[0] == rr[0] and isinstance(rb[0], int) and r[1] == 1:
        return S(R(rr[1], rb[1]))
    return logsplit(b[0], r)
