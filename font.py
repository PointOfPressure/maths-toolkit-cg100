# Text widths of the calculator's fonts, measured on the fx-CG100:
# medium digits and capitals 12 px, lower case 10, narrow letters 8;
# small digits and capitals 8, lower case 6, narrow 4; large 18.
# One character per code 32..126, width = code - 48; strings cost nothing to load.
_M = '88<<<<<888<<8888<8<<<<<<<<88<<<<<<<<<<<<<8<<<<<<<<<<<<<<<<<8<8<<<:::::8::88:8<::::8:8::<:::888<'
_S = '44888884448844448488888888448888888888888488888888888888888484888666664664464866664646686664448'
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
