# Text widths of the calculator's fonts, measured on the fx-CG100 by
# fontcal.py (2026-10-08): medium digits 12, most letters 10, i 8, l 7;
# small digits 8, most lower case 6. Large is an estimate.
# One character per code 32..126, width = code - 48; strings cost nothing to load.
_M = '46:;:?<688::6:<9<<<<<<<<<<779:99=::::::::89::<:;:;:::::<:::797:;6:;:;:9::89:7<::;;9:9::<::9868;'
_S = '65786884557848468888888888446867887877787667788787778788887565785666665664674866665656686665458'
_L = '>>BBBEB>>>BB>>>>B>BBBBBBBB>>BBBBEBBBBBBBB>BBBEBBBBBBBBBEBBB>B>BBB@@@@@>@@>>@>E@@@@>@>@@E@@@>>>B'
_T = {'medium': _M, 'small': _S, 'large': _L}

def cw(ch, size):
    o = ord(ch) - 32
    t = _T[size]
    return ord(t[o]) - 48 if 0 <= o < 95 else 12

def strw(s, size):
    t = _T[size]
    w = 0
    for ch in s:
        o = ord(ch) - 32
        w += ord(t[o]) - 48 if 0 <= o < 95 else 12
    return w
