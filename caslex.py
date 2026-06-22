# caslex.py - tokenizer + ITERATIVE shunting-yard parser for the CAS.
# Turns "2x^2+sin(x)" into a tuple expression tree. Iterative on purpose:
# MicroPython's call stack dies around ~38 frames, so no recursive-descent.
# Tree nodes (tuples): ('n',num) ('v',name) ('+',a,b) ('-',a,b) ('*',a,b)
#   ('/',a,b) ('^',a,b) ('neg',a) ('sin',a) ('cos',a) ('tan',a)
#   ('ln',a) ('log',a) ('exp',a) ('sqrt',a) ('asin',a) ('acos',a) ('atan',a)
#   ('abs',a) ('sinh',a) ('cosh',a) ('tanh',a) ('asinh',a) ('acosh',a)
#   ('atanh',a) ('fact',a)=a!  and 2-arg ('ncr',a,b) ('npr',a,b) ('logb',a,b)

# unary functions that take one bracketed argument
UFUNCS = ("sqrt", "asinh", "acosh", "atanh", "asin", "acos", "atan",
          "sinh", "cosh", "tanh", "sin", "cos", "tan", "log", "exp", "ln", "abs")
# two-argument functions: f(a, b)
BINFUNCS = ("ncr", "npr", "logb")
FUNCS = UFUNCS + BINFUNCS
# matched longest-first so "asinh" beats "asin" beats "sin"; single letters = vars
WORDS = ["asinh", "acosh", "atanh", "sqrt", "asin", "acos", "atan", "sinh",
         "cosh", "tanh", "logb", "ncr", "npr", "abs", "log", "exp", "sin",
         "cos", "tan", "ans", "ln", "pi", "e", "x", "y"]

def tokenize(s):
    toks = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == ' ':
            i += 1
            continue
        if c in "0123456789.":
            j = i
            dot = 0
            while j < n and (s[j] in "0123456789" or s[j] == '.'):
                if s[j] == '.':
                    if dot >= 1:
                        break  # a second '.' starts a new token (2.3.4 -> 2.3, .4)
                    dot += 1
                j += 1
            txt = s[i:j]
            if dot:
                try:
                    toks.append(('num', float(txt)))
                except:
                    pass  # malformed run like a lone '.' - skip, never raise
            else:
                toks.append(('num', int(txt)))
            i = j
            continue
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            matched = None
            for w in WORDS:
                if s[i:i + len(w)].lower() == w:
                    matched = w
                    break
            if matched is None:
                matched = c.lower()
            if matched in FUNCS:
                toks.append(('fn', matched))
            elif matched == 'pi':
                toks.append(('num', 3.141592653589793))
            elif matched == 'e':
                toks.append(('num', 2.718281828459045))
            else:
                toks.append(('var', matched))
            i += len(matched)
            continue
        if c in "+-*/^":
            toks.append(('op', c))
            i += 1
            continue
        if c == '!':
            toks.append(('post', '!'))
            i += 1
            continue
        if c == ',':
            toks.append(('comma',))
            i += 1
            continue
        if c == '(':
            toks.append(('lp',))
            i += 1
            continue
        if c == ')':
            toks.append(('rp',))
            i += 1
            continue
        i += 1  # ignore anything else
    return _implicit(toks)

def _implicit(toks):
    # insert '*' where multiplication is implied: 2x, 2(x), )(, x sin(...
    out = []
    prev = None
    for t in toks:
        if prev is not None:
            lend = prev[0] in ('num', 'var', 'rp')
            rstart = t[0] in ('num', 'var', 'fn', 'lp')
            if lend and rstart:
                out.append(('op', '*'))
        out.append(t)
        prev = t
    return out

PREC = {'+': 2, '-': 2, '*': 3, '/': 3, 'u': 4, '^': 5}
RIGHT = {'^': True, 'u': True}

def parse(s):
    toks = tokenize(s)
    if not toks:
        return None
    # mark unary minus as op 'u'
    marked = []
    prev = None
    for t in toks:
        if t == ('op', '-') and (prev is None or prev[0] in ('op', 'lp', 'comma')):
            marked.append(('op', 'u'))
            prev = ('op', 'u')
            continue
        marked.append(t)
        prev = t
    # shunting-yard -> RPN
    rpn = []
    ops = []
    for t in marked:
        k = t[0]
        if k == 'num' or k == 'var':
            rpn.append(t)
        elif k == 'fn':
            ops.append(t)
        elif k == 'post':
            rpn.append(t)
        elif k == 'comma':
            while ops and ops[-1][0] != 'lp':
                rpn.append(ops.pop())
        elif k == 'op':
            o1 = t[1]
            while ops and ops[-1][0] == 'op':
                o2 = ops[-1][1]
                if PREC[o2] > PREC[o1] or (PREC[o2] == PREC[o1] and not RIGHT.get(o1, False)):
                    rpn.append(ops.pop())
                else:
                    break
            ops.append(t)
        elif k == 'lp':
            ops.append(t)
        elif k == 'rp':
            while ops and ops[-1][0] != 'lp':
                rpn.append(ops.pop())
            if ops and ops[-1][0] == 'lp':
                ops.pop()
            if ops and ops[-1][0] == 'fn':
                rpn.append(ops.pop())
    while ops:
        if ops[-1][0] == 'lp':
            return None  # mismatched parens
        rpn.append(ops.pop())
    # RPN -> tree (iterative, explicit value stack)
    st = []
    for t in rpn:
        k = t[0]
        if k == 'num':
            st.append(('n', t[1]))
        elif k == 'var':
            st.append(('v', t[1]))
        elif k == 'fn':
            name = t[1]
            if name in BINFUNCS:
                if len(st) < 2:
                    return None
                b = st.pop()
                a = st.pop()
                st.append((name, a, b))
            else:
                if not st:
                    return None
                st.append((name, st.pop()))
        elif k == 'post':
            if not st:
                return None
            st.append(('fact', st.pop()))
        elif k == 'op':
            o = t[1]
            if o == 'u':
                if not st:
                    return None
                st.append(('neg', st.pop()))
            else:
                if len(st) < 2:
                    return None
                b = st.pop()
                a = st.pop()
                st.append((o, a, b))
    if len(st) != 1:
        return None
    return st[0]
