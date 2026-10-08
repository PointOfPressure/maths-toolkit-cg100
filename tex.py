# Display typesetter. row(text) turns one line of calculator notation, words
# and maths mixed, into a casrender box without caslex (which costs 100-200
# ms a formula on the calculator): a/b fractions, ^ and _ scripts, sqrt,
# |x|, Greek and symbol names as drawn glyphs, [a b; c d] matrices. The text
# stays as written; whatever it cannot read is left as plain text.
# lines() breaks a row wider than the screen. mknotes.py runs the same code on
# the PC to precompile the notes.
from casrender import measure, shrink

M = 'medium'
LET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOW = 'abcdefghijklmnopqrstuvwxyz'
DIG = '0123456789'
START = LET + DIG + '(|\\.{['   # what a maths unit can start with

# names drawn as glyphs (codes in mkglyph.py / texg.py)
GREEK = {'alpha': 'a', 'beta': 'b', 'gamma': 'g', 'delta': 'd', 'epsilon': 'e',
         'theta': 't', 'lambda': 'l', 'mu': 'm', 'nu': 'n', 'pi': 'p', 'rho': 'r',
         'sigma': 's', 'tau': 'u', 'phi': 'f', 'chi': 'c', 'omega': 'w', 'psi': 'y',
         'Sigma': 'S', 'Phi': 'P', 'Delta': 'D', 'Omega': 'W', 'Gamma': 'G',
         'Lambda': 'L', 'Theta': 'T', 'inf': 'i'}
SYMS = ('<=>', '+/-', '<=', '>=', '!=', '~=', '->', '=>', '+-')
SYMG = {'<=>': '%', '+/-': '+', '<=': '<', '>=': '>', '!=': '#', '~=': '~',
        '->': '-', '=>': '=', '+-': '+'}
CMD = {'cup': 'U', 'cap': 'N', 'in': 'E', 'times': 'x', 'pm': '+', 'partial': 'q'}   # \cup etc
REL = '<>#~-=%'        # glyphs a line may break before
FN = {'sin': 1, 'cos': 1, 'tan': 1, 'sec': 1, 'cosec': 1, 'csc': 1, 'cot': 1,
      'sinh': 1, 'cosh': 1, 'tanh': 1, 'sech': 1, 'cosech': 1, 'coth': 1,
      'arcsin': 1, 'arccos': 1, 'arctan': 1, 'asin': 1, 'acos': 1, 'atan': 1,
      'arsinh': 1, 'arcosh': 1, 'artanh': 1, 'ln': 1, 'log': 1, 'exp': 1,
      'lim': 1, 'det': 1, 'Re': 1, 'Im': 1, 'arg': 1, 'Var': 1, 'tr': 1}
W2 = ('of', 'to', 'in', 'is', 'or', 'if', 'at', 'on', 'by', 'as', 'an', 'be',
      'so', 'no', 'up', 'it', 'we', 'do', 'Of', 'To', 'In', 'Is', 'Or', 'If',
      'At', 'On', 'By', 'As', 'An', 'So', 'No', 'It')
UNITL = ('m', 'km', 'cm', 'mm', 'rad', 'rev', 'kg', 'N', 'J', 'W')
UNITR = ('s', 'h', 'min', 'm', 'kg')

def A(s, sz):
    return ('atom', s, sz)

def isword(t):
    # English rather than maths: 'from', 'of'; not 'dy', 'Sxx', 'nth'
    if len(t) < 2 or t in FN or t in GREEK:
        return False
    if len(t) == 2:
        return t in W2
    l = t.lower()
    return 'a' in l or 'e' in l or 'i' in l or 'o' in l or 'u' in l

# byte classes: 1 letter, 2 digit, 3 space, 4 '.', 0 anything else
CL = (b'\x00' * 32 + b'\x03' + b'\x00' * 13 + b'\x04\x00' + b'\x02' * 10 + b'\x00' * 7 +
      b'\x01' * 26 + b'\x00' * 6 + b'\x01' * 26 + b'\x00' * 133)

def tokens(s):
    # walks bytes(s): ints cost far less than one-character strings
    out = []
    b = bytes(s, 'ascii')
    cl = CL
    n = len(b)
    i = 0
    while i < n:
        k = cl[b[i]]
        j = i + 1
        if k == 1:
            while j < n and cl[b[j]] == 1:
                j += 1
        elif k == 2 or (k == 4 and j < n and cl[b[j]] == 2):
            while j < n and cl[b[j]] == 2:
                j += 1
            if j + 1 < n and b[j] == 46 and cl[b[j + 1]] == 2:
                j += 2
                while j < n and cl[b[j]] == 2:
                    j += 1
            if j + 1 < n and b[j] == 101:
                # 1e-8, but not 2e^x or 3ex
                m = j + 1
                if b[m] == 45 or b[m] == 43:
                    m += 1
                if m < n and cl[b[m]] == 2:
                    while m < n and cl[b[m]] == 2:
                        m += 1
                    if m >= n or cl[b[m]] != 1:
                        j = m
        elif k == 3:
            while j < n and b[j] == 32:
                j += 1
        elif k == 4:
            if s.startswith('...', i):
                j = i + 3
        else:
            c = b[i]
            if c == 92 and j < n:
                # \cup, \*
                if cl[b[j]] == 1:
                    while j < n and cl[b[j]] == 1:
                        j += 1
                elif b[j] != 32:
                    j += 1
            elif c == 60 or c == 62 or c == 33 or c == 126 or c == 45 or c == 43 or c == 61:
                for m in SYMS:
                    if s.startswith(m, i):
                        j = i + len(m)
                        break
        out.append(s[i:j])
        i = j
    return out

def row(s, sz='medium'):
    if plain(s):
        return A(s, sz)
    if 'm/s2' in s:
        s = s.replace('m/s2', 'm/s^2')
    items, i, ok = seq(tokens(s), 0, sz, 0, None)
    return pack(items, sz)

# fast test that a line typesets as itself, mostly in C (str.find and in)
TRIG = ('/', '^', '_', '|', '*', '[', '{', '\\', '!', '~', '<', '>')
NAMES = ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'theta', 'lambda', 'mu', 'nu',
         'pi', 'rho', 'sigma', 'tau', 'phi', 'chi', 'omega', 'psi', 'Sigma', 'Phi',
         'Delta', 'Omega', 'Gamma', 'Lambda', 'Theta', 'inf', 'sqrt', 'sum', 'int',
         'bar', 'hat')

def plain(s):
    for c in TRIG:
        if c in s:
            return False
    b = bytes(s, 'ascii')
    t = PL
    n = len(b)
    for c in NAMES:
        # a name on its own, or after one letter (dtheta, xbar), not in pivot
        j = s.find(c)
        while j >= 0:
            e = j + len(c)
            if (e >= n or t[b[e]] != 1) and (j < 2 or t[b[j - 2]] != 1 or t[b[j - 1]] != 1):
                return False
            j = s.find(c, j + 1)
    for c in 'CP':
        # nCr, nC2
        j = s.find(c)
        while j >= 0:
            if 0 < j < n - 1 and 97 <= b[j - 1] <= 122 and (97 <= b[j + 1] <= 122 or t[b[j + 1]] == 2):
                return False
            j = s.find(c, j + 1)
    for c in (61, 43, 45, 46):
        # = + - unspaced between terms are spaced; a.b is a dot product
        j = s.find(chr(c))
        while j >= 0:
            if j > 0 and j + 1 < n:
                p = t[b[j - 1]]
                q = t[b[j + 1]]
                if c == 46:
                    if (p == 1 or p == 7) and (q == 1 or b[j + 1] == 40):
                        return False
                elif p == 6 or q == 6 or ((p == 1 or p == 2 or p == 7) and q != 3):
                    return False
            j = s.find(chr(c), j + 1)
    for c in DIG:
        # x1, H0: subscripts; 1e-5: a power of ten
        j = s.find(c)
        while j >= 0:
            if j > 0 and t[b[j - 1]] == 1:
                return False
            if j + 1 < n and b[j + 1] == 101:
                return False
            j = s.find(c, j + 1)
    return True

# byte classes for plain(): 1 letter, 2 digit, 3 space, 4 '.', 6 = + -, 7 ) ]
PL = (b'\x00' * 32 + b'\x03\x05\x00\x00\x00\x00\x00\x00\x00\x07\x05\x06\x00\x06\x04\x05' +
      b'\x02' * 10 + b'\x00\x00\x05\x06\x05\x00\x00' + b'\x01' * 26 + b'\x05\x05\x07\x05\x05\x00' +
      b'\x01' * 26 + b'\x05\x05\x00\x05\x00' + b'\x00' * 128)


# An item is [box, class, kind, data, size]. Class: U maths unit, N number,
# F function name, T word, S space, O operator or punctuation, / a slash.
# Groups (kind '(' '[' '{' '|') and fractions keep their parts so a bracket
# can be dropped later; their box is made when packed.

def seq(T, i, sz, lvl, close):
    out = []
    n = len(T)
    sl = False
    while i < n:
        t = T[i]
        c = t[0]
        if t == close:
            if sl:
                fracs(out, sz)
            return out, i + 1, True
        if c in LET:
            i = ident(T, i, out, sz, lvl)
        elif c in DIG or (c == '.' and len(t) > 1):
            out.append([num(t, sz), 'N', t])
            i += 1
        elif c == ' ':
            # scripts drop the spaces between terms, as TeX does
            if lvl == 0 or (out and (out[-1][1] == 'T' or out[-1][1] == 'F')) or \
                    (i + 1 < n and (isword(T[i + 1]) or T[i + 1] in FN)):
                out.append([A(t, sz), 'S', t])
            i += 1
        elif c == '(' or c == '[' or c == '{':
            cl = ')' if c == '(' else (']' if c == '[' else '}')
            inner, j, ok = seq(T, i + 1, sz, lvl, cl)
            if ok:
                out.append(group(c, inner, cl, sz))
                i = j
            else:
                out.append([A(c, sz), 'O', None])
                i += 1
        elif c == ')' or c == ']' or c == '}':
            if close is not None:
                return out, i, False
            out.append([A(t, sz), 'O', None])
            i += 1
        elif c == '|':
            if i + 1 < n and T[i + 1][0] != ' ':
                inner, j, ok = seq(T, i + 1, sz, lvl, '|')
                if ok and inner:
                    out.append([None, 'U', '|', inner, sz])
                    i = j
                    continue
            out.append([A('|', sz), 'O', None])
            i += 1
        elif c == '^' or c == '_':
            i = script(T, i, out, sz, lvl)
        elif c == '/':
            sp = (i > 0 and T[i - 1][0] == ' ') or (i + 1 < n and T[i + 1][0] == ' ')
            out.append([None, '/', sp])
            sl = sl or lvl == 0
            i += 1
        elif c == '*':
            i = star(T, i, out, sz)
        elif t == '...':
            out.append([A(t, sz), 'U', None])
            i += 1
        elif t == '.':
            i = dot(T, i, out, sz)
        elif t in SYMG or c == '+' or c == '-' or c == '=' or c == '<' or c == '>':
            i = op(T, i, out, sz, lvl)
        elif c == '!' or c == "'":
            out.append([A(t, sz), 'U' if out and out[-1][1] in 'UNF' else 'O', None])
            i += 1
        elif c == '\\' and len(t) > 1:
            g = CMD.get(t[1:])
            if g is not None:
                out.append([('g', g, sz), 'U' if g == 'q' else 'O', None])
                if g == 'q' and i + 1 < n and T[i + 1] == ' ':
                    i += 1      # \partial f: no space
            else:
                out.append([A(t[1:] if len(t) == 2 else t, sz), 'U', None])
            i += 1
        else:
            out.append([A(t, sz), 'O', None])
            i += 1
    if sl:
        fracs(out, sz)
    return out, i, close is None

def group(c, inner, cl, sz):
    if c == '[':
        for it in inner:
            if it[1] == 'O' and it[0] == ('atom', ';', sz):
                return [matrix(inner, sz), 'U', None]
    return [None, 'U', c, (inner, cl), sz]

def matrix(inner, sz):
    # [a b; c d]: rows split at ';', cells at spaces (at runs of two or more
    # spaces when a cell has a space in it: [cos t  -sin t; ...])
    rows = [[]]
    wide = False
    for it in inner:
        if it[1] == 'O' and it[0][1] == ';':
            rows.append([])
        else:
            rows[-1].append(it)
            if it[1] == 'S' and len(it[2]) > 1:
                wide = True
    out = []
    for r in rows:
        cells = [[]]
        for it in strip(r):
            if it[1] == 'S' and (len(it[2]) > 1 or not wide):
                if cells[-1]:
                    cells.append([])
            else:
                cells[-1].append(it)
        out.append([pack(c, sz) for c in cells])
    m = 0
    for r in out:
        if len(r) > m:
            m = len(r)
    for r in out:
        while len(r) < m:
            r.append(A('', sz))
    return ('mat', out, sz)

def strip(its):
    i = 0
    j = len(its)
    while i < j and its[i][1] == 'S':
        i += 1
    while j > i and its[j - 1][1] == 'S':
        j -= 1
    return its[i:j]

def num(t, sz):
    j = t.find('e')
    if j < 0:
        return A(t, sz)
    e = t[j + 1:]
    if e[0] == '+':
        e = e[1:]
    return ('row', [A(t[:j], sz), ('g', 'x', sz), ('sup', A('10', sz), A(e, 'small'), sz)])

def mathnext(T, j):
    # does a maths term follow? ('sum x', 'int 1/x', not 'sum of')
    if j >= len(T):
        return False
    t = T[j]
    c = t[0]
    if t == '_' or t == '^' or c == '(' or c in DIG:
        return True
    if t == ' ' and j + 1 < len(T):
        t = T[j + 1]
        c = t[0]
        if c in DIG or c == '(' or c == '|':
            return True
        if c in LET:
            return not isword(t)
    return False

def ident(T, i, out, sz, lvl):
    t = T[i]
    n = len(T)
    nx = T[i + 1] if i + 1 < n else ' '
    cls = 'U'
    g = GREEK.get(t)
    if len(t) == 1:
        b = A(t, sz)
    elif g is not None:
        b = ('g', g, sz)
    elif t == 'sqrt':
        r = rootarg(T, i + 1, sz, lvl)
        if r is not None:
            out.append([('root', r[0], sz), 'U', None])
            return r[1]
        b = A(t, sz)
    elif (t == 'sum' or t == 'int') and mathnext(T, i + 1):
        out.append([('g', 'Z' if t == 'sum' else 'I', sz), 'F', None])
        return i + 1
    elif len(t) == 4 and (t[1:] == 'bar' or (t[1:] == 'hat' and t[0] in 'ijknruvxyz')):
        b = (t[1:], A(t[0], sz), sz)
    elif t[0] == 'd' and t[1:] in GREEK:
        b = ('row', [A('d', sz), ('g', GREEK[t[1:]], sz)])
    elif len(t) == 3 and (t[1] == 'C' or t[1] == 'P') and t[0] in LOW and t[2] in LOW and nx != '(':
        # nCr as in the booklet: n raised before, r lowered after
        b = ('row', [('sup', A('', sz), A(t[0], 'small'), sz), ('sub', A(t[1], sz), A(t[2], 'small'), sz)])
    elif len(t) == 2 and (t[1] == 'C' or t[1] == 'P') and t[0] in LOW and nx.isdigit():
        out.append([('row', [('sup', A('', sz), A(t[0], 'small'), sz), ('sub', A(t[1], sz), A(nx, 'small'), sz)]), 'U', None])
        return i + 2
    else:
        b = A(t, sz)
        if t in FN:
            cls = 'F'
        elif isword(t):
            cls = 'F' if nx == '(' else 'T'
    if cls == 'U' and nx.isdigit() and len(nx) <= 2 and (i == 0 or T[i - 1][0] not in DIG or
                                                      (i > 1 and T[i - 2][0] in LET)):
        after = T[i + 2][0] if i + 2 < n else ' '
        if t == 'd' and len(nx) == 1 and after in LET:
            # d2y/dx2: second derivatives
            out.append([('sup', b, A(nx, 'small'), sz), 'U', None])
            return i + 2
        if len(t) == 2 and t[0] == 'd' and len(nx) == 1 and after not in LET:
            out.append([('sup', b, A(nx, 'small'), sz), 'U', None])
            return i + 2
        if len(t) == 1 or g is not None:
            # x1, a2, H0: a subscript
            out.append([('sub', b, A(nx, 'small'), sz), 'U', None])
            return i + 2
    out.append([b, cls, None])
    return i + 1

def rootarg(T, j, sz, lvl):
    n = len(T)
    if j < n and T[j] == '(':
        inner, k, ok = seq(T, j + 1, sz, lvl, ')')
        if ok and inner:
            return pack(strip(inner), sz), k
        return None
    if j + 1 < n and T[j] == ' ':
        b, k = prim(T, j + 1, sz, lvl, True)
        if b is not None:
            return b, k
    return None

def prim(T, i, sz, lvl, whole):
    # one script or root argument: 2, -1, x, theta, (n+1), {r=1}, |x|
    n = len(T)
    i0 = i
    if i >= n:
        return None, i0
    t = T[i]
    c = t[0]
    sign = None
    if (t == '-' or t == '+') and i + 1 < n:
        sign = t
        i += 1
        t = T[i]
        c = t[0]
    if c in DIG or (c == '.' and len(t) > 1):
        b = num(t, sz)
        i += 1
    elif c in LET:
        if not whole and len(t) > 1 and t not in GREEK and t not in FN and not isword(t):
            # e^kt is e^k t, as the calculator reads it
            T[i] = t[1:]
            b = A(t[0], sz)
        else:
            tmp = []
            i = ident(T, i, tmp, sz, lvl + 1)
            b = pack(tmp, sz)
    elif c == '(' or c == '{':
        inner, k, ok = seq(T, i + 1, sz, lvl + 1, ')' if c == '(' else '}')
        if not ok or not inner:
            return None, i0
        b = pack(strip(inner), sz)
        if c == '(' and k < n and T[k] == '(':
            out = [A('(', sz)]                          # f^(r)(0): a derivative
            put(out, b)
            put(out, A(')', sz))
            b = out[0] if len(out) == 1 else ('row', out)
        i = k
    elif c == '|':
        inner, k, ok = seq(T, i + 1, sz, lvl + 1, '|')
        if not ok or not inner:
            return None, i0
        b = gbox([None, 'U', '|', inner, sz], False)
        i = k
    elif c == '*':
        b = A('*', sz)
        i += 1
    else:
        return None, i0
    if sign is not None:
        out = [A(sign, sz)]
        put(out, b)
        b = out[0] if len(out) == 1 else ('row', out)
    return b, i

def script(T, i, out, sz, lvl):
    c = T[i]
    if out and out[-1][1] in 'UNF':
        base = out.pop()
    else:
        base = None
    e, j = prim(T, i + 1, 'small', lvl + 1, c == '_')
    if e is None:
        if base is not None:
            out.append(base)
        out.append([A(c, sz), 'O', None])
        return i + 1
    if base is None:
        bb = A('', sz)
        cls = 'U'
    else:
        bb = base[0] if base[0] is not None else gbox(base, False)
        cls = base[1]
    if c == '^':
        nb = ('ss', bb[1], bb[2], e, sz) if bb[0] == 'sub' else ('sup', bb, e, sz)
    else:
        nb = ('ss', bb[1], e, bb[2], sz) if bb[0] == 'sup' else ('sub', bb, e, sz)
    out.append([nb, cls, None])
    return j

def star(T, i, out, sz):
    n = len(T)
    nx = T[i + 1] if i + 1 < n else ' '
    c = nx[0]
    prev = out[-1][1] if out else 'O'
    if prev in 'UNF':
        if c in DIG or c == '.' or out[-1][0] == ('atom', '...', sz):
            out.append([('dot', sz), 'U', None])     # 3*2^n: a dot between numbers
            return i + 1
        if c in LET or c == '(' or c == '|' or c == '\\':
            if c in LET and (nx in FN or (len(nx) > 1 and nx not in GREEK and nx != 'sqrt')):
                out.append([A(' ', sz), 'U', None])   # A*cos(x): A cos(x)
            return i + 1                             # 2*x: 2x
        if c in ' ,;:)]}=':
            # z*: the conjugate
            base = out.pop()
            bb = base[0] if base[0] is not None else gbox(base, False)
            out.append([('sup', bb, A('*', 'small'), sz), 'U', None])
            return i + 1
    elif prev == 'S' and len(out) > 1 and out[-2][1] in 'UNFT' and c == ' ' and i + 2 < n and T[i + 2][0] in START:
        out.append([('g', 'x', sz), 'O', None])      # a * b: a times sign
        return i + 1
    out.append([A('*', sz), 'O', None])
    return i + 1

def dot(T, i, out, sz):
    # a.b, (r - a).n: a centred dot; i.e., d.p. and full stops stay
    n = len(T)
    nx = T[i + 1] if i + 1 < n else ' '
    if out and out[-1][1] == 'U' and (nx[0] in LET or nx == '(') and \
            not (len(nx) == 1 and i + 2 < n and T[i + 2] == '.') and not (i > 1 and T[i - 2] == '.'):
        out.append([('dot', sz), 'U', None])
    else:
        out.append([A('.', sz), 'O', None])
    return i + 1

def op(T, i, out, sz, lvl):
    t = T[i]
    g = SYMG.get(t)
    b = ('g', g, sz) if g is not None else A(t, sz)
    n = len(T)
    nx = T[i + 1] if i + 1 < n else ' '
    c = nx[0]
    if lvl == 0 and out and out[-1][1] in 'UNF' and c != ' ':
        # x=2, n^2-5n+3: spaced like the rest of the line
        pad = c in START
        if t == '+' or t == '-':
            if out[-1][1] == 'N' and c in DIG:
                pad = i + 2 < n and T[i + 2][0] in LET    # 1-2i, but 3-4 is a range
            elif c in LET and isword(nx):
                pad = False                                # x-axis
        elif c == '-' or c == '+':
            pad = True
        if pad:
            out.append([A(' ', sz), 'S', ' '])
            out.append([b, 'O', None])
            out.append([A(' ', sz), 'S', ' '])
            return i + 1
    out.append([b, 'O', None])
    return i + 1

# ---- fractions -------------------------------------------------------------------

def fracs(items, sz):
    k = 0
    while k < len(items):
        it = items[k]
        if it[1] != '/':
            k += 1
            continue
        a, b = span(items, k, it[2])
        if a < 0:
            items[k] = [A('/', sz), 'O', None]
            k += 1
            continue
        num = items[a:k]
        den = items[k + 1:b]
        box = ('frac', operand(num, sz), operand(den, sz), sz)
        items[a:b] = [[box, 'U', '/', (num, den), sz]]
        k = a + 1

def span(items, k, spaced):
    # the numerator items[a:k] and denominator items[k+1:b] of the slash at k
    n = len(items)
    a = k
    b = k + 1
    if spaced:
        # a(1 - r^n) / (1 - r): whole products either side, up to an operator
        if a > 0 and items[a - 1][1] == 'S':
            a -= 1
        while a > 0 and (items[a - 1][1] in 'UNF' or (items[a - 1][1] == 'S' and items[a - 1][2] == ' ')):
            a -= 1
        while a < k and items[a][1] == 'S':
            a += 1
        if b < n and items[b][1] == 'S':
            b += 1
        while b < n and (items[b][1] in 'UNF' or (items[b][1] == 'S' and items[b][2] == ' ')):
            b += 1
        while b > k + 1 and items[b - 1][1] == 'S':
            b -= 1
    else:
        while a > 0 and items[a - 1][1] in 'UNF':
            a -= 1
        if a < k and a > 1 and items[a - 1][1] == 'S' and items[a - 1][2] == ' ' and items[a - 2][1] == 'F' \
                and items[a - 2][0] != ('g', 'I', items[a - 2][0][-1]):
            a -= 2      # ln 2/|k|, sum x/n: the function goes on top (not int)
        if b + 2 < n and items[b][1] == 'F' and items[b + 1][1] == 'S' and items[b + 1][2] == ' ' \
                and items[b + 2][1] in 'UN':
            b += 2      # a/sin A
        while b < n and items[b][1] in 'UNF':
            b += 1
    if a == k or b == k + 1 or (a < k and items[a][1] == 'S') or items[k + 1][1] == 'S' and not spaced:
        return -1, -1
    if spaced:
        l = strip(items[a:k])
        r = strip(items[k + 1:b])
        if len(l) == 1 and len(r) == 1 and l[0][1] == 'N' and r[0][1] == 'N' and '.' in l[0][2] and '.' in r[0][2]:
            return -1, -1   # 1.6449 / 1.9600: a list, not a quotient
    if b == k + 2 and a == k - 1:
        # m/s, km/h: units stay inline
        l = items[a][0]
        r = items[k + 1][0]
        if r is not None and r[0] == 'sup':
            r = r[1]
        if l is not None and r is not None and l[0] == 'atom' and r[0] == 'atom' and \
                l[1] in UNITL and r[1] in UNITR:
            return -1, -1
    return a, b

def operand(its, sz):
    its = strip(its)
    if len(its) == 1 and its[0][2] == '(':
        its = strip(its[0][3][0])      # (a + b)/(c + d): the brackets go
    if len(its) == 1 and its[0][2] == '/':
        f = its[0][3]                  # a fraction in a fraction stays a slash
        its = f[0] + [[A('/', sz), 'O', None]] + f[1]
    return pack(its, sz)

# ---- boxes ----------------------------------------------------------------------

def tall(b):
    k = b[0]
    if k == 'frac' or k == 'mat' or k == 'paren' or k == 'abs':
        return True
    if k == 'root':
        return tall(b[1])
    if k == 'row':
        for c in b[1]:
            if tall(c):
                return True
        return False
    if k == 'sup' or k == 'sub' or k == 'ss' or k == 'bar' or k == 'hat':
        return tall(b[1])
    if k == 'g':
        return b[1] == 'Z' or b[1] == 'I'
    return False

def onefrac(its):
    its = strip(its)
    if len(its) == 1 and its[0][2] == '/':
        return its[0][0]
    return None

def gbox(it, free):
    kind = it[2]
    sz = it[4]
    if kind == '|':
        inner = pack(it[3], sz)
        if tall(inner):
            return ('abs', inner, sz)
        return ('row', [A('|', sz), inner, A('|', sz)])
    inner, cl = it[3]
    if kind == '(' and free:
        f = onefrac(inner)
        if f is not None:
            return f        # (1/2) n: the brackets go
    inner = pack(inner, sz)
    if kind == '(' and tall(inner):
        return ('paren', inner, sz)
    return ('row', [A(kind, sz), inner, A(cl, sz)])

def put(out, b):
    # add b to a row, joining text of one size into one atom (one draw_string)
    k = b[0]
    if k == 'row':
        for c in b[1]:
            put(out, c)
    elif k == 'atom':
        if out and out[-1][0] == 'atom' and out[-1][2] == b[2]:
            out[-1] = ('atom', out[-1][1] + b[1], b[2])
        elif b[1]:
            out.append(b)
    else:
        out.append(b)

def pack(items, sz):
    out = []
    n = len(items)
    for k in range(n):
        it = items[k]
        b = it[0]
        if b is None:
            if it[1] == '/':
                b = A('/', sz)
            else:
                # (1/2) n, (dy/du)(du/dx): the brackets go; not f(x/2), (u/v)'
                free = k == 0 or items[k - 1][1] in 'SO' or items[k - 1][2] == '(' or items[k - 1][2] == '/'
                if free and k + 1 < n:
                    nb = items[k + 1][0]
                    free = nb is None or nb[0] != 'atom' or nb[1][:1] not in "'!"
                b = gbox(it, free)
        put(out, b)
    if not out:
        return A('', sz)
    if len(out) == 1:
        return out[0]
    return ('row', out)

# ---- line breaking ------------------------------------------------------------------

def pieces(b):
    # [box, width, width without trailing spaces, may break before, good break]
    from font import strw
    kids = b[1] if b[0] == 'row' else [b]
    out = []
    after = False       # the last piece ended in a space
    punct = False       # ... and its text in , ; or :
    for c in kids:
        if c[0] != 'atom':
            w = measure(c)[0]
            out.append([c, w, w, after, after and c[0] == 'g' and c[1] in REL])
            after = False
            punct = False
            continue
        s = c[1]
        sz = c[2]
        L = len(s)
        k = 0
        while k < L:
            j = s.find(' ', k)
            if j < 0:
                j = L
            e = j
            while e < L and s[e] == ' ':
                e += 1
            word = s[k:j]
            good = after and (punct or (word != '' and word[0] in '+-=<>'))
            out.append([A(s[k:e], sz), strw(s[k:e], sz), strw(word, sz), after, good])
            if word:
                punct = word[-1] in ',;:'
            after = e > j
            k = e
    return out

def _line(ps):
    out = []
    for p in ps:
        put(out, p[0])
    if out and out[-1][0] == 'atom':
        out[-1] = A(out[-1][1].rstrip(), out[-1][2])
    if len(out) == 1:
        return out[0]
    return ('row', out)

def lines(b, width, indent=16):
    # [(row, x offset)]: b broken at spaces, by preference before + - = and
    # relations or after a comma; continuation lines are set in by indent
    if measure(b)[0] <= width:
        return [(b, 0)]
    ps = pieces(b)
    n = len(ps)
    out = []
    start = 0
    lim = width
    x = 0
    while start < n:
        if out:
            while start < n and ps[start][2] == 0 and ps[start][0][0] == 'atom':
                start += 1
            if start == n:
                break
        w = 0
        e = start
        while e < n and w + ps[e][2] <= lim:
            w += ps[e][1]
            e += 1
        if e == n:
            out.append((_line(ps[start:]), x))
            break
        best = -1
        good = -1
        w = 0
        for j in range(start, e + 1):
            if j > start and ps[j][3]:
                best = j
                if ps[j][4] and w * 3 >= lim:
                    good = j
            w += ps[j][1]
        j = good if good > 0 else best
        if j < 0:
            if e == start:
                # one piece wider than the line: a size down, on its own;
                # text still too wide (a 200 digit number) is cut
                b = shrink(ps[start][0])
                if b[0] == 'atom' and measure(b)[0] > lim:
                    from font import cw
                    t = ps[start][0][1].rstrip()
                    while t:
                        k = 1
                        w = cw(t[0], b[2])
                        while k < len(t) and w + cw(t[k], b[2]) <= lim:
                            w += cw(t[k], b[2])
                            k += 1
                        out.append((A(t[:k], b[2]), x))
                        t = t[k:]
                        x = indent
                        lim = width - indent
                elif b[0] == 'mat' and measure(b)[0] > lim:
                    # a matrix too wide even small: one bracketed row a line
                    for r in ps[start][0][1]:
                        rb = [A('[', M)]
                        for c in r:
                            put(rb, c)
                            put(rb, A(' ', M))
                        rb[-1] = A(rb[-1][1].rstrip() + ']', M) if rb[-1][0] == 'atom' else rb[-1]
                        for rr, dx in lines(('row', rb), lim, 0):
                            out.append((rr, x))
                        x = indent
                        lim = width - indent
                else:
                    out.append((b, x))
                start += 1
                x = indent
                lim = width - indent
                continue
            j = e
        out.append((_line(ps[start:j]), x))
        start = j
        x = indent
        lim = width - indent
    return out
