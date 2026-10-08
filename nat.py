# Natural-display editor: fractions, powers, roots and logs are typed straight
# into 2D boxes, and lin() turns the result into the text caslex parses.
# A row is a list. An item is a str token or a template [kind, slot, slot...]:
# F fraction [num, den], P power [exp], R sqrt [arg], N nth root [idx, arg],
# L log base [base, arg], A modulus [arg].
# A kind ending in '(' is a bracket pair round one box, like the calculator's
# own: '(' plain, 'sin(' a function, and so on. ')' at the end steps out.
from casioplot import *

NSLOT = {'F': 2, 'P': 1, 'R': 1, 'N': 2, 'L': 2, 'A': 1}

def nslot(kind):
    return NSLOT.get(kind, 1)

ASC = {'medium': 13, 'small': 8}
DESC = {'medium': 4, 'small': 2}
AXIS = {'medium': 5, 'small': 3}

from font import cw, strw

INK = (0, 0, 0)
HOLE = (150, 160, 190)
CARET = (40, 120, 220)

SHOW = {'*': '', 'ans': 'Ans', 'asin(': 'sin-1(', 'acos(': 'cos-1(',
        'atan(': 'tan-1(', '=': ' = ', '+': ' + ', '-': ' - ', ',': ', '}
_UNARY = ('+', '-', '*', ',', '=')

def new(kind):
    t = [kind]
    n = nslot(kind)
    while n > 0:
        t.append([])
        n -= 1
    return t

def copy(row):
    out = []
    for it in row:
        if isinstance(it, str):
            out.append(it)
        else:
            t = [it[0]]
            for s in it[1:]:
                t.append(copy(s))
            out.append(t)
    return out

def empty_hole(row):
    for it in row:
        if not isinstance(it, str):
            for s in it[1:]:
                if not s or empty_hole(s):
                    return True
    return False

def _plain(row):
    # digits or one name: needs no brackets round it
    if not row:
        return False
    for it in row:
        if not isinstance(it, str) or not (it.isdigit() or it == '.'):
            return len(row) == 1 and isinstance(row[0], str) and row[0].isalpha()
    return True

def lin(row):
    out = ''
    opens = 0
    for it in row:
        if isinstance(it, str):
            out += it
            opens += it.count('(') - it.count(')')
            continue
        k = it[0]
        if k == 'F':
            if _plain(it[1]) and _plain(it[2]):
                out += '(' + lin(it[1]) + '/' + lin(it[2]) + ')'
            else:
                out += '((' + lin(it[1]) + ')/(' + lin(it[2]) + '))'
        elif k == 'P':
            out += '^' + lin(it[1]) if _plain(it[1]) else '^(' + lin(it[1]) + ')'
        elif k == 'R':
            out += 'sqrt(' + lin(it[1]) + ')'
        elif k == 'N':
            out += '((' + lin(it[2]) + ')^(1/(' + lin(it[1]) + ')))'
        elif k == 'L':
            out += 'logb(' + lin(it[1]) + ',' + lin(it[2]) + ')'
        elif k[-1] == '(':
            out += k + lin(it[1]) + ')'
        else:
            out += 'abs(' + lin(it[1]) + ')'
    while opens > 0:
        out += ')'
        opens -= 1
    return out

def from_text(s):
    # recalled plain text: one token per character, still valid linear input
    return [c for c in s]

# ---- editing ------------------------------------------------------------------

class Ed:
    def __init__(self, row=None):
        self.set(row if row is not None else [])

    def set(self, row):
        self.root = row
        self.stack = []     # (parent row, template index, slot number)
        self.row = row
        self.i = len(row)

    def ins(self, tok):
        self.row.insert(self.i, tok)
        self.i += 1

    def _enter(self, pos, slot, at_end):
        self.stack.append((self.row, pos, slot))
        self.row = self.row[pos][1 + slot]
        self.i = len(self.row) if at_end else 0

    def _leave(self, after):
        parent, pos, slot = self.stack.pop()
        self.row = parent
        self.i = pos + 1 if after else pos

    def tmpl(self, kind, fill=None, grab=False, out=False):
        t = new(kind)
        row = self.row
        if grab:
            j = self.i
            depth = 0
            while j > 0:
                it = row[j - 1]
                if isinstance(it, str):
                    if depth == 0 and it in ('+', '-', ',', '='):
                        break
                    if it == ')':
                        depth += 1
                    elif it.endswith('('):
                        if depth == 0:
                            break
                        depth -= 1
                j -= 1
            while self.i > j:
                self.i -= 1
                t[1].insert(0, row.pop(self.i))
            # (a+b) over something: the fraction bar replaces the brackets
            g = t[1]
            if len(g) == 1 and not isinstance(g[0], str) and g[0][0] == '(':
                t[1] = g = g[0][1]
            elif len(g) > 2 and g[0] == '(' and g[-1] == ')':
                depth = 0
                n = 0
                while n < len(g) - 1:
                    if isinstance(g[n], str):
                        if g[n].endswith('('):
                            depth += 1
                        elif g[n] == ')':
                            depth -= 1
                    if depth == 0:
                        break
                    n += 1
                if n == len(g) - 1:
                    g.pop()
                    g.pop(0)
        if fill:
            for tok in fill:
                t[1].append(tok)
        row.insert(self.i, t)
        if out:
            self.i += 1
        elif grab and t[1]:
            self._enter(self.i, 1, False)
        else:
            self._enter(self.i, 0, bool(fill))

    def right(self):
        row = self.row
        if self.i < len(row):
            if isinstance(row[self.i], str):
                self.i += 1
            else:
                self._enter(self.i, 0, False)
        elif self.stack:
            parent, pos, slot = self.stack[-1]
            t = parent[pos]
            if slot + 1 < nslot(t[0]):
                self.stack[-1] = (parent, pos, slot + 1)
                self.row = t[slot + 2]
                self.i = 0
            else:
                self._leave(True)

    def left(self):
        row = self.row
        if self.i > 0:
            it = row[self.i - 1]
            if isinstance(it, str):
                self.i -= 1
            else:
                self._enter(self.i - 1, nslot(it[0]) - 1, True)
        elif self.stack:
            parent, pos, slot = self.stack[-1]
            if slot > 0:
                t = parent[pos]
                self.stack[-1] = (parent, pos, slot - 1)
                self.row = t[slot]
                self.i = len(self.row)
            else:
                self._leave(False)

    def home(self):
        self.stack = []
        self.row = self.root
        self.i = 0

    def end(self):
        self.stack = []
        self.row = self.root
        self.i = len(self.root)

    def vert(self, up):
        # fraction: up to the numerator / down to the denominator
        n = len(self.stack) - 1
        while n >= 0:
            parent, pos, slot = self.stack[n]
            t = parent[pos]
            if t[0] == 'F' and slot == (1 if up else 0):
                while len(self.stack) > n + 1:
                    self.stack.pop()
                self.stack[n] = (parent, pos, 1 - slot)
                self.row = t[2 - slot]
                self.i = len(self.row)
                return True
            n -= 1
        return False

    def dele(self):
        row = self.row
        if self.i > 0:
            it = row[self.i - 1]
            if isinstance(it, str):
                row.pop(self.i - 1)
                self.i -= 1
                return
            filled = False
            for s in it[1:]:
                if s:
                    filled = True
            if filled:
                self._enter(self.i - 1, nslot(it[0]) - 1, True)
            else:
                row.pop(self.i - 1)
                self.i -= 1
            return
        if not self.stack:
            return
        parent, pos, slot = self.stack[-1]
        t = parent[pos]
        if slot > 0:
            self.stack[-1] = (parent, pos, slot - 1)
            self.row = t[slot]
            self.i = len(self.row)
            return
        # at the start of the first box: unwrap the template, keep what was in it
        self.stack.pop()
        parent.pop(pos)
        at = pos
        n = 0
        for s in t[1:]:
            if n and t[0] == 'F' and s:
                parent.insert(at, '/')
                at += 1
            for it in s:
                parent.insert(at, it)
                at += 1
            n += 1
        self.row = parent
        self.i = pos

    def close(self):
        # ')' at the end of a bracket's box (or of boxes ending inside one)
        # steps out past the bracket instead of typing a stray ')'
        row = self.row
        at_end = self.i == len(row)
        n = len(self.stack) - 1
        while n >= 0 and at_end:
            parent, pos, slot = self.stack[n]
            t = parent[pos]
            if slot + 1 != nslot(t[0]):
                break
            if t[0][-1] == '(':
                while len(self.stack) > n + 1:
                    self.stack.pop()
                self._leave(True)
                return True
            at_end = pos == len(parent) - 1
            n -= 1
        return False

    def clear(self):
        self.set([])

# ---- layout and drawing ------------------------------------------------------------

def _sz(lvl):
    return 'medium' if lvl <= 0 else 'small'

def _tok(tok, prev):
    # a sign after an operator, comma or bracket is unary: no spaces round it
    if (tok == '-' or tok == '+') and (prev is None or (isinstance(prev, str) and
                                        (prev in _UNARY or prev.endswith('(')))):
        return tok
    return SHOW.get(tok, tok)

_MC = [None]    # measure cache, live only during one draw (rows change between keys)

def measure(row, lvl):
    mc = _MC[0]
    if mc is not None:
        v = mc.get((id(row), lvl))
        if v is None:
            v = _measure(row, lvl)
            mc[(id(row), lvl)] = v
        return v
    return _measure(row, lvl)

def _measure(row, lvl):
    sz = _sz(lvl)
    if not row:
        return (8, ASC[sz], DESC[sz])
    w = 0
    a = ASC[sz]
    d = DESC[sz]
    prev = None
    for it in row:
        iw, ia, idd = mitem(it, lvl, prev)
        prev = it
        w += iw
        if ia > a:
            a = ia
        if idd > d:
            d = idd
    return (w, a, d)

_SW = {}        # (shown token, size) -> width

_INV = ('asin(', 'acos(', 'atan(', 'asinh(', 'acosh(', 'atanh(')

def _fname(kind):
    # name before a bracket and its raised -1 for inverse functions
    if kind in _INV:
        return kind[1:-1], '-1'
    return kind[:-1], ''

def _fw(name, sup, sz):
    return strw(name, sz) + (strw(sup, 'small') + 1 if sup else 0)

def _bw(sz, aa, ad):
    # bracket widths: text brackets for one line, drawn ones round a fraction
    if aa > ASC[sz] + 3 or ad > DESC[sz] + 1:
        return 5, 5, True
    return cw('(', sz), cw(')', sz), False

def _flat(row):
    for it in row:
        if not isinstance(it, str) or it == '*':
            return False
    return len(row) > 0

def mitem(it, lvl, prev=None):
    sz = _sz(lvl)
    if isinstance(it, str):
        if it == '*':
            return (7, ASC[sz], DESC[sz])
        t = _tok(it, prev)
        key = (t, sz)
        w = _SW.get(key)
        if w is None:
            w = strw(t, sz)
            _SW[key] = w
        return (w, ASC[sz], DESC[sz])
    k = it[0]
    if k == 'F':
        nw, na, nd = measure(it[1], lvl)
        dw, da, dd = measure(it[2], lvl)
        ax = AXIS[sz]
        return ((nw if nw > dw else dw) + 6, ax + 3 + na + nd, da + dd + 3 - ax)
    if k == 'P':
        ew, ea, ed = measure(it[1], lvl + 1)
        up = 7 if sz == 'medium' else 4
        a = up + ea
        return (ew + 1, a if a > ASC[sz] else ASC[sz], DESC[sz])
    if k == 'R' or k == 'N':
        rw, ra, rd = measure(it[-1], lvl)
        extra = 0
        a = ra + 3
        if k == 'N':
            iw, ia, idd = measure(it[1], lvl + 1)
            extra = iw - 3 if iw > 3 else 0
            if 6 + ia > a:
                a = 6 + ia
        return (extra + 9 + rw + 2, a, rd)
    if k == 'L':
        bw, ba, bd = measure(it[1], lvl + 1)
        aw, aa, ad = measure(it[2], lvl)
        lw, rw, tall = _bw(sz, aa, ad)
        if tall:
            aa += 1
            ad += 1
        dn = 4 + bd
        return (strw('log', sz) + bw + 1 + lw + aw + rw, aa, ad if ad > dn else dn)
    if k[-1] == '(':
        name, sup = _fname(k)
        aw, aa, ad = measure(it[1], lvl)
        lw, rw, tall = _bw(sz, aa, ad)
        a = aa + 1 if tall else aa
        if sup:
            up = (7 if sz == 'medium' else 4) + ASC['small']
            if up > a:
                a = up
        return (_fw(name, sup, sz) + lw + aw + rw, a, ad + 1 if tall else ad)
    aw, aa, ad = measure(it[1], lvl)
    return (aw + 8, aa + 1, ad + 1)

class Pen:
    # dx scrolls the line; caret gets (x, top, bottom) when the edited row is met
    def __init__(self, ed, dx, color):
        self.ed = ed
        self.dx = dx
        self.color = color
        self.caret = None
        self.dry = False
        self.hole = HOLE

def _text(pen, x, y, s, sz, c):
    x += pen.dx
    if pen.dry or x > 383:
        return
    while s and x < 0:
        x += cw(s[0], sz)
        s = s[1:]
    end = x + strw(s, sz)
    while s and end > 384:
        end -= cw(s[-1], sz)
        s = s[:-1]
    if s:
        draw_string(x, y, s, c, sz)

def _px(pen, x, y, c):
    x += pen.dx
    if not pen.dry and 0 <= x <= 383:
        set_pixel(x, y, c)

def _hl(pen, x0, x1, y, c):
    if pen.dry:
        return
    x0 += pen.dx
    x1 += pen.dx
    if x0 < 0:
        x0 = 0
    if x1 > 383:
        x1 = 383
    sp = set_pixel
    for x in range(x0, x1 + 1):
        sp(x, y, c)

def _vl(pen, x, y0, y1, c):
    x += pen.dx
    if pen.dry or x < 0 or x > 383:
        return
    sp = set_pixel
    for y in range(y0, y1 + 1):
        sp(x, y, c)

def _line(pen, x0, y0, x1, y1, c):
    dx = x1 - x0 if x1 > x0 else x0 - x1
    dy = -(y1 - y0 if y1 > y0 else y0 - y1)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _px(pen, x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def _paren(pen, x, base, aa, ad, right, c):
    # a bracket the height of what it holds, in a 5 pixel cell
    top = base - aa
    bot = base + ad
    i, o = (3, 1) if right else (1, 3)
    _line(pen, x + o, top, x + i, top + 2, c)
    _vl(pen, x + i, top + 2, bot - 2, c)
    _line(pen, x + i, bot - 2, x + o, bot, c)

def _bracket(pen, it, x, base, lvl, c):
    sz = _sz(lvl)
    k = it[0]
    name, sup = _fname(k)
    aw, aa, ad = measure(it[1], lvl)
    lw, rw, tall = _bw(sz, aa, ad)
    y = base - ASC[sz]
    if sup:
        _text(pen, x, y, name, sz, c)
        x += strw(name, sz)
        _text(pen, x, base - (7 if sz == 'medium' else 4) - ASC['small'], sup, 'small', c)
        x += strw(sup, 'small') + 1
        name = ''
    if tall:
        if name:
            _text(pen, x, y, name, sz, c)
            x += strw(name, sz)
        _paren(pen, x, base, aa, ad, False, c)
        _paren(pen, x + lw + aw, base, aa, ad, True, c)
    else:
        _text(pen, x, y, name + '(', sz, c)
        x += strw(name, sz)
        _text(pen, x + lw + aw, y, ')', sz, c)
    draw_row(pen, it[1], x + lw, base, lvl)

def draw_row(pen, row, x, base, lvl):
    sz = _sz(lvl)
    w, a, d = measure(row, lvl)
    ws = []
    prev = None
    for it in row:
        ws.append(mitem(it, lvl, prev)[0])
        prev = it
    if pen.ed is not None and row is pen.ed.row:
        cx = x
        n = 0
        while n < pen.ed.i:
            cx += ws[n]
            n += 1
        if not row:
            cx += 3
        pen.caret = (cx, base - a, base + d)
    if not row:
        c = pen.hole
        top = base - ASC[sz]
        _hl(pen, x + 1, x + 6, top, c)
        _hl(pen, x + 1, x + 6, base + DESC[sz] - 1, c)
        _vl(pen, x + 1, top, base + DESC[sz] - 1, c)
        _vl(pen, x + 6, top, base + DESC[sz] - 1, c)
        return
    # runs of plain tokens go out as one string: each draw_string is slow
    buf = ''
    bx = x
    prev = None
    n = 0
    ed = pen.ed.row if pen.ed is not None else None
    for it in row:
        if isinstance(it, str) and it != '*':
            if not buf:
                bx = x
            buf += _tok(it, prev)
        elif (not isinstance(it, str) and it[0][-1] == '(' and it[0] not in _INV
              and it[1] is not ed and _flat(it[1])):
            # a bracket holding plain text joins the run: one draw call
            if not buf:
                bx = x
            buf += it[0]
            p = None
            for t in it[1]:
                buf += _tok(t, p)
                p = t
            buf += ')'
        else:
            if buf:
                _text(pen, bx, base - ASC[sz], buf, sz, pen.color)
                buf = ''
            draw_item(pen, it, x, base, lvl, prev)
        prev = it
        x += ws[n]
        n += 1
    if buf:
        _text(pen, bx, base - ASC[sz], buf, sz, pen.color)

def draw_item(pen, it, x, base, lvl, prev=None):
    sz = _sz(lvl)
    c = pen.color
    if isinstance(it, str):
        if it == '*':
            y = base - AXIS[sz] - 1
            _px(pen, x + 3, y, c); _px(pen, x + 4, y, c)
            _px(pen, x + 3, y + 1, c); _px(pen, x + 4, y + 1, c)
            return
        _text(pen, x, base - ASC[sz], _tok(it, prev), sz, c)
        return
    k = it[0]
    if k == 'F':
        nw, na, nd = measure(it[1], lvl)
        dw, da, dd = measure(it[2], lvl)
        w = (nw if nw > dw else dw) + 6
        ybar = base - AXIS[sz]
        _hl(pen, x + 1, x + w - 2, ybar, c)
        draw_row(pen, it[1], x + (w - nw) // 2, ybar - 2 - nd, lvl)
        draw_row(pen, it[2], x + (w - dw) // 2, ybar + 2 + da, lvl)
        return
    if k == 'P':
        up = 7 if sz == 'medium' else 4
        draw_row(pen, it[1], x + 1, base - up, lvl + 1)
        return
    if k == 'R' or k == 'N':
        rw, ra, rd = measure(it[-1], lvl)
        if k == 'N':
            iw, ia, idd = measure(it[1], lvl + 1)
            draw_row(pen, it[1], x, base - 6, lvl + 1)
            x += iw - 3 if iw > 3 else 0
        top = base - ra - 2
        bot = base + rd
        _line(pen, x, base - 3, x + 2, base - 4, c)
        _line(pen, x + 2, base - 4, x + 4, bot, c)
        _line(pen, x + 4, bot, x + 8, top, c)
        _hl(pen, x + 8, x + 9 + rw + 1, top, c)
        draw_row(pen, it[1] if k == 'R' else it[2], x + 10, base, lvl)
        return
    if k == 'L':
        _text(pen, x, base - ASC[sz], 'log', sz, c)
        x += strw('log', sz)
        bw, ba, bd = measure(it[1], lvl + 1)
        draw_row(pen, it[1], x, base + 4, lvl + 1)
        x += bw + 1
        _bracket(pen, ['(', it[2]], x, base, lvl, c)
        return
    if k[-1] == '(':
        _bracket(pen, it, x, base, lvl, c)
        return
    aw, aa, ad = measure(it[1], lvl)
    _vl(pen, x + 2, base - aa - 1, base + ad, c)
    draw_row(pen, it[1], x + 4, base, lvl)
    _vl(pen, x + aw + 5, base - aa - 1, base + ad, c)

LAST = [0, None]    # scroll and caret of the last draw, so it can be undrawn

def draw(ed, row, x, base, maxw, color=INK, dx=None):
    # draws a row, scrolled so the caret stays in view; returns (w, asc, desc).
    # dx given: draw at that scroll with no caret (used to undraw in white)
    if not row:
        # an empty line is just the caret, no placeholder box
        a = ASC['medium']
        d = DESC['medium']
        caret = None
        if ed is not None and dx is None:
            caret = (x, base - a, base + d)
            for y in range(base - a - 1, base + d + 1):
                set_pixel(x, y, CARET)
                set_pixel(x + 1, y, CARET)
        LAST[0] = 0
        LAST[1] = caret
        return (0, a, d)
    _MC[0] = {}
    w, a, d = measure(row, 0)
    pen = Pen(ed, 0, color)
    if dx is not None:
        pen.dx = dx
        pen.ed = None
        pen.hole = color
    elif ed is not None and w > maxw:
        pen.dry = True
        draw_row(pen, row, x, base, 0)
        cx = pen.caret[0] if pen.caret else x + w
        if cx - x > maxw - 12:
            pen.dx = maxw - 12 - (cx - x)
        pen.dry = False
    draw_row(pen, row, x, base, 0)
    caret = None
    if pen.caret is not None:
        cx, top, bot = pen.caret
        caret = (cx + pen.dx, top, bot)
        _vl(pen, cx, top - 1, bot, CARET)
        _vl(pen, cx + 1, top - 1, bot, CARET)
    LAST[0] = pen.dx
    LAST[1] = caret
    _MC[0] = None
    return (w, a, d)

def undraw(row, x, base, dx, caret, bg):
    # paint over a row drawn earlier, in the background colour
    draw(None, row, x, base, 9999, bg, dx)
    if caret is not None:
        cx, top, bot = caret
        y = top - 1
        while y <= bot:
            set_pixel(cx, y, bg)
            set_pixel(cx + 1, y, bg)
            y += 1

# ---- keys -------------------------------------------------------------------------

UNSHIFT = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.',
    84: '+', 85: '-', 74: '*', 55: '(', 56: ')',
    41: 'x', 33: 'x', 51: ',',
    52: 'sin(', 53: 'cos(', 54: 'tan(',
}
SHIFTED = {
    55: '=', 46: 'ln(', 45: 'log(', 61: 'pi', 63: 'i',
    52: 'asin(', 53: 'acos(', 54: 'atan(', 41: 'ans',
}
ALPHADICT = {
    41: 'a', 42: 'b', 43: 'c', 44: 'd', 45: 'e', 46: 'f',
    51: 'g', 52: 'h', 53: 'i', 54: 'j', 55: 'k', 56: 'l',
    61: 'm', 62: 'n', 63: 'o',
    71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    81: 'u', 82: 'v', 83: 'w', 84: 'x', 85: 'y',
    91: 'z',
}
OPS = ('+', '-', '*', '=')

def typed(ed, k, shift, alpha):
    # one key into the editor; returns True if it inserted something
    if alpha:
        tok = ALPHADICT.get(k)
        if tok is None:
            return False
        put(ed, tok)
        return True
    if shift:
        if k == 44:
            ed.tmpl('L')
            return True
        if k == 43:
            ed.tmpl('N')
            return True
        tok = SHIFTED.get(k)
    else:
        if k == 42 or k == 75:
            ed.tmpl('F', grab=True)
            return True
        if k == 44:
            ed.tmpl('P')
            return True
        if k == 45:
            ed.tmpl('P', fill=['2'], out=True)
            return True
        if k == 46:
            ed.ins('e')
            ed.tmpl('P')
            return True
        if k == 43:
            ed.tmpl('R')
            return True
        if k == 93:
            ed.ins('*')
            ed.ins('1')
            ed.ins('0')
            ed.tmpl('P')
            return True
        tok = UNSHIFT.get(k)
    if tok is None:
        return False
    put(ed, tok)
    return True

def put(ed, tok):
    # functions and '(' open a bracket pair; ')' steps out of one
    if tok[-1] == '(':
        ed.tmpl(tok)
    elif tok != ')' or not ed.close():
        ed.ins(tok)

def starts_op(k, shift, alpha):
    # keys that continue from Ans after a result: + - x / ^ x^2
    if alpha or shift:
        return False
    return k in (84, 85, 74, 75, 44, 45)

SYMBOLS = ['Abs', 'nroot', 'log_b', '!', 'nCr(', 'nPr(', 'pi', 'e', 'i',
           'ans', 'sec(', 'cosec(', 'cot(', 'sinh(', 'cosh(', 'tanh(',
           'asinh(', 'acosh(', 'atanh(', 'arg(', 'conj(', 're(', 'im(',
           'exp(', 'y', 'n', 'r', 't', '=', '?']

def symbol(ed, s):
    if s == 'Abs':
        ed.tmpl('A')
    elif s == 'nroot':
        ed.tmpl('N')
    elif s == 'log_b':
        ed.tmpl('L')
    else:
        put(ed, s)
