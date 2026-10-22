# Numbers as text, to the Decimals setting, for the engines that need no
# CAS (Statistics): eng.py uses the same functions, so a session that has
# loaded eng doesn't pay for them twice.
import math
import casui

def sf(v, n):
    # v to n significant figures, as text (casutil._sf, kept here so the
    # topic screens don't load casutil)
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

def boxs(pre, s, t=None):
    # boxed text with no decimal
    return ('=', pre, s, None, t)

def br(s):
    # a number in brackets when it starts with a minus
    return '(' + s + ')' if s[:1] == '-' else s
