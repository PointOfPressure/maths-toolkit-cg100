# Notes screens below the paper menu (casui.notes_section): a paper's topic
# grid from the small index notes_ix.py, then a page. A notes module is
# imported only when one of its topics is opened.
from casui import remembered, show_lines, busy

_PLAIN = 'abcdefghijklmnopqrstuvwxyz0123456789+-*/^().! '
_WORDS = ('sum', 'int', 'mu', 'nu', 'phi', 'var', 'and', 'nth')

def as_written(rhs):
    # typeset 'label = b' only when caslex reads b as written: lower case,
    # letters as products (ut, 2as), function names with a bracket, nothing
    # it would drop, and no f(x) or a(2x) that would print without a bracket
    for ch in rhs:
        if ch not in _PLAIN:
            return False
    s = rhs.replace(' ', '')
    if '+-' in s or '-+' in s or '--' in s:
        return False
    import caslex
    n = len(s)
    i = 0
    while i < n:
        c = s[i]
        if 'a' <= c <= 'z':
            j = i
            while j < n and 'a' <= s[j] <= 'z':
                j += 1
            w = s[i:j]
            if w in caslex.FUNCS or w in caslex.ALIAS:
                if j == n or s[j] != '(':
                    return False
                i = j + 1
                continue
            if len(w) > 1 and w != 'pi':
                # a short product of letters, never a word or dx after '/'
                if len(w) > 3 or w in _WORDS or w[0] == 'd' or (i and s[i - 1] == '/'):
                    return False
            i = j
            continue
        if c == '(' and i and s[i - 1] not in '+-*/^(':
            # a bracket after a factor prints only round a sum
            d = 0
            k = i
            sign = False
            while k < n:
                if s[k] == '(':
                    d += 1
                elif s[k] == ')':
                    d -= 1
                    if d == 0:
                        break
                elif d == 1 and (s[k] == '+' or s[k] == '-'):
                    sign = True
                k += 1
            if not sign:
                return False
        i += 1
    return True

def lines(raw):
    # an indented line is a detail: grey, set in. 'label = b' is typeset by
    # show_lines when the label is plain words and b reads as written
    out = []
    for ln in raw:
        if ln[:2] == '  ':
            out.append(('w', ln.strip()))
            continue
        j = ln.find(' = ')
        if j >= 0:
            lhs = ln[:j]
            if '^' in lhs or '/' in lhs or 'sqrt' in lhs or not as_written(ln[j + 3:]):
                ln = ('a', ln)
        out.append(ln)
    return out

def topics(name):
    # [(topic, module, index in its NOTES)] for one paper
    import notes_ix
    out = []
    for p, mods in notes_ix.T:
        if p == name:
            for m, ts in mods:
                for i in range(len(ts)):
                    out.append((ts[i], m, i))
    return out

def paper(name):
    tops = topics(name)
    labels = [t[0] for t in tops]
    while True:
        sel = remembered(name, labels)
        if sel < 0:
            return
        title, mod, i = tops[sel]
        busy()
        show_lines(title, lines(__import__(mod).NOTES[i][1]))
