# Keys, menus, the one-line editor, the result screen, Calculate, CAS, home.
from casioplot import *
import caslex
import caseng
import casrender
import cascalc
import caspoly
import casutil

KEYCODES = set([
    12, 13, 14, 15, 16,
    21, 22, 23, 24, 25, 26,
    31, 32, 33, 34, 35, 36,
    41, 42, 43, 44, 45, 46,
    51, 52, 53, 54, 55, 56,
    61, 62, 63, 64,
    71, 72, 73, 74, 75,
    81, 82, 83, 84, 85,
    91, 92, 93, 94, 95,
])

HOME = 12; LINESTART = 13; UP = 14; LINEEND = 15; PAGEUP = 16
SETTINGS = 21; EXITK = 22; LEFT = 23; OK = 24; RIGHT = 25; PAGEDOWN = 26
SHIFT = 31; ALPHA = 32; VARIABLE = 33; DOWN = 34; MENU = 35; TOOLS = 36
DEL = 64; FORMAT = 94; EXE = 95; PLUS = 84; MINUS = 85; ZERO = 91

UNSHIFT = {
    91: '0', 81: '1', 82: '2', 83: '3', 71: '4', 72: '5', 73: '6',
    61: '7', 62: '8', 63: '9', 92: '.',
    84: '+', 85: '-', 74: '*', 75: '/', 44: '^', 55: '(', 56: ')',
    41: 'x', 33: 'x', 42: '/', 45: '^2', 46: 'e^(', 93: '*10^',
    52: 'sin(', 53: 'cos(', 54: 'tan(', 43: 'sqrt(',
    51: ',',
}
SHIFTED = {
    55: '=', 46: 'ln(', 45: 'log(', 61: 'pi', 63: 'i',
    52: 'asin(', 53: 'acos(', 54: 'atan(', 44: 'logb(', 41: 'ans',
}
DIGITS = {81: 1, 82: 2, 83: 3, 71: 4, 72: 5, 73: 6, 61: 7, 62: 8, 63: 9, 91: 0}
ALPHADICT = {
    41: 'a', 42: 'b', 43: 'c', 44: 'd', 45: 'e', 46: 'f',
    51: 'g', 52: 'h', 53: 'i', 54: 'j', 55: 'k', 56: 'l',
    61: 'm', 62: 'n', 63: 'o',
    71: 'p', 72: 'q', 73: 'r', 74: 's', 75: 't',
    81: 'u', 82: 'v', 83: 'w', 84: 'x', 85: 'y',
    91: 'z', 92: ' ',
}
SYMBOLS = ['!', 'abs(', 'nCr(', 'nPr(', 'sec(', 'cosec(', 'cot(', 'sinh(',
           'cosh(', 'tanh(', 'asinh(', 'acosh(', 'atanh(', 'sech(', 'cosech(',
           'coth(', 'arg(', 'conj(', 're(', 'im(', 'logb(', 'exp(', 'pi', 'e',
           'i', 'ans', 't', 'y', 'n', 'r']

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACC = (40, 120, 220)
GREY = (120, 120, 120)
RED = (205, 60, 60)

W = 384

# ---- keys -------------------------------------------------------------------

def readkey():
    k = getkey()
    return k if k in KEYCODES else 0

def wait_release():
    while readkey():
        pass

def wait_key():
    k = readkey()
    while not k:
        k = readkey()
    return k

# ---- text metrics ------------------------------------------------------------

char_w = casrender.cw

def text_w(s, size):
    w = 0
    for c in s:
        w += char_w(c, size)
    return w

def clip(s, maxpx, size):
    if text_w(s, size) <= maxpx:
        return s
    dots = text_w('..', size)
    out = ''
    w = 0
    for c in s:
        cw = char_w(c, size)
        if w + cw + dots > maxpx:
            break
        out += c
        w += cw
    return out + '..'

def cursor_fit(s, cpos, maxpx, size):
    if text_w(s, size) <= maxpx:
        return s
    if cpos > len(s):
        cpos = len(s)
    lo = cpos
    hi = cpos + 1 if cpos < len(s) else cpos
    w = char_w(s[cpos], size) if cpos < len(s) else 0
    while True:
        grew = False
        if hi < len(s) and w + char_w(s[hi], size) <= maxpx:
            w += char_w(s[hi], size)
            hi += 1
            grew = True
        if lo > 0 and w + char_w(s[lo - 1], size) <= maxpx:
            lo -= 1
            w += char_w(s[lo], size)
            grew = True
        if not grew:
            return s[lo:hi]

def hline(x0, x1, y, c):
    sp = set_pixel
    x = x0
    while x <= x1:
        sp(x, y, c)
        x += 1

def _header(title, right=None):
    draw_string(4, 2, clip(title, 300 if right else 376, 'small'), GREY, 'small')
    if right:
        draw_string(W - 4 - text_w(right, 'small'), 2, right, GREY, 'small')

# ---- menu ----------------------------------------------------------------------

ROWS = 13
PITCH = 13

def _draw_menu(title, opts, sel, top):
    clear_screen()
    n = len(opts)
    _header(title, str(sel + 1) + '/' + str(n) if n > ROWS else None)
    r = 0
    while r < ROWS and top + r < n:
        i = top + r
        y = 16 + r * PITCH
        pre = str(i + 1) + ' ' if i < 9 else '  '
        if i == sel:
            draw_string(4, y, '>', ACC, 'small')
            draw_string(16, y, pre + clip(opts[i], 350, 'small'), ACC, 'small')
        else:
            draw_string(16, y, pre + clip(opts[i], 350, 'small'), BLACK, 'small')
        r += 1
    show_screen()

def menu(title, opts, sel=0):
    if not opts:
        return -1
    n = len(opts)
    top = 0
    while True:
        if sel < top:
            top = sel
        if sel >= top + ROWS:
            top = sel - ROWS + 1
        _draw_menu(title, opts, sel, top)
        wait_release()
        k = wait_key()
        if k == UP:
            sel = (sel - 1) % n
        elif k == DOWN:
            sel = (sel + 1) % n
        elif k == LEFT or k == LINESTART:
            sel = 0
        elif k == RIGHT or k == LINEEND:
            sel = n - 1
        elif k == PAGEUP:
            sel = sel - ROWS if sel >= ROWS else 0
        elif k == PAGEDOWN:
            sel = sel + ROWS if sel + ROWS < n else n - 1
        elif k == OK or k == EXE:
            wait_release()
            return sel
        elif k == EXITK:
            wait_release()
            return -1
        else:
            d = DIGITS.get(k, None)
            if d is not None and 1 <= d <= n:
                wait_release()
                return d - 1

# ---- messages ------------------------------------------------------------------

def flash(msg):
    draw_string(4, 180, clip(msg, 376, 'small'), RED, 'small')
    show_screen()
    wait_release()
    wait_key()
    wait_release()

# ---- one-line editor -------------------------------------------------------------

_LAST = {}

def _grid_cols(spec):
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind == 'm':
            return cnt[1]
        if kind == 'v':
            return cnt
    return 0

def _draw_input(label, spec, ex, cur, shift, alpha, cols):
    clear_screen()
    mode = 'SHIFT' if shift else ('ALPHA' if alpha else ('DEG' if casutil.DEG else 'RAD'))
    _header(label, mode)
    draw_string(4, 16, clip(spec.replace(',', ', '), 376, 'small'), BLACK, 'small')
    s = ''.join(ex)
    raw = ''.join(ex[:cur]) + '|' + ''.join(ex[cur:])
    draw_string(4, 34, cursor_fit(raw, len(''.join(ex[:cur])), 376, 'medium'), BLACK, 'medium')
    hline(0, 383, 58, GREY)
    draw_string(4, 62, 'UP recall  DOWN clear  MENU symbols  OK run', GREY, 'small')
    if s:
        parts = casutil.split_values(s)
        n = cols if cols else 6
        x = 4
        y = 80
        i = 0
        while i < len(parts) and y < 176:
            draw_string(x, y, clip(parts[i], 56, 'small'), GREY, 'small')
            x += 62
            i += 1
            if i % n == 0:
                x = 4
                y += 12
    show_screen()

def input_line(label, spec, last=''):
    ex = []
    cur = 0
    shift = False
    alpha = False
    cols = _grid_cols(spec)
    key = label + '|' + spec
    while True:
        _draw_input(label, spec, ex, cur, shift, alpha, cols)
        wait_release()
        k = wait_key()
        if k == SHIFT:
            shift = not shift
            alpha = False
        elif k == ALPHA:
            alpha = not alpha
            shift = False
        elif k == MENU:
            i = menu('symbols', SYMBOLS)
            if i >= 0:
                ex.insert(cur, SYMBOLS[i])
                cur += 1
        elif k == LEFT:
            if cur > 0:
                cur -= 1
        elif k == RIGHT:
            if cur < len(ex):
                cur += 1
        elif k == LINESTART:
            cur = 0
        elif k == LINEEND:
            cur = len(ex)
        elif k == UP:
            prev = _LAST.get(key, last)
            if prev:
                ex = list(prev)
                cur = len(ex)
        elif k == DOWN:
            ex = []
            cur = 0
        elif k == DEL:
            if cur > 0:
                ex.pop(cur - 1)
                cur -= 1
        elif k == EXITK:
            if not ex:
                wait_release()
                return None
            ex = []
            cur = 0
        elif k == OK or k == EXE:
            if ex:
                wait_release()
                s = ''.join(ex)
                _LAST[key] = s
                return s
        else:
            if alpha:
                tok = ALPHADICT.get(k, None)
            elif shift:
                tok = SHIFTED.get(k, None)
            else:
                tok = UNSHIFT.get(k, None)
            if tok is not None:
                ex.insert(cur, tok)
                cur += 1
            shift = False
            alpha = False

# ---- result screen -----------------------------------------------------------------

def _blocks(lines, mode):
    out = []
    for ln in lines:
        if isinstance(ln, tuple):
            kind = ln[0]
            if (kind == 'w' or kind == 'mw') and mode == 0:
                continue
            if kind == 'm' or kind == 'mw':
                box = casrender.build(ln[1], 0)
                bw, ba, bd = casrender.measure(box)
                if bw <= 376:
                    out.append((kind, box, ba + bd + 4))
                else:
                    text = caseng.tostr(ln[1])
                    out.append(('a' if kind == 'm' else 'w', text, 18 if kind == 'm' else 12))
            else:
                out.append((kind, ln[1], 12))
        else:
            out.append(('a', ln, 18))
    return out

def _draw_result(title, blocks, top, mode, more):
    clear_screen()
    _header(title)
    y = 16
    i = top
    n = len(blocks)
    while i < n:
        kind, payload, h = blocks[i]
        if y + h > 178:
            break
        if kind == 'a':
            draw_string(4, y, clip(payload, 376, 'medium'), BLACK, 'medium')
        elif kind == 'w':
            draw_string(8, y, clip(payload, 372, 'small'), GREY, 'small')
        elif kind == '!':
            draw_string(4, y, clip(payload, 376, 'small'), RED, 'small')
        else:
            bw, ba, bd = casrender.measure(payload)
            casrender.COLOR = BLACK if kind == 'm' else GREY
            casrender.draw(payload, 4 if kind == 'm' else 8, y + 2 + ba)
        y += h
        i += 1
    foot = ['FORMAT working', 'FORMAT digits', 'FORMAT less'][mode]
    if not more:
        foot = ''
    if i < n or top > 0:
        foot += '   ' + str(top + 1) + '-' + str(i) + '/' + str(n)
    draw_string(4, 180, foot, GREY, 'small')
    show_screen()
    return i

def result(label, text, lines_fn):
    # lines_fn: callable giving the lines (called again for full precision),
    # or a plain list for static content
    title = (label + '  ' + text) if text else label
    mode = 0
    top = 0
    more = not isinstance(lines_fn, list)
    casutil.FULL = False
    try:
        while True:
            lines = lines_fn if isinstance(lines_fn, list) else lines_fn()
            blocks = _blocks(lines, mode)
            if not blocks:
                blocks = [('!', 'nothing to show', 12)]
            if top >= len(blocks):
                top = len(blocks) - 1
            end = _draw_result(title, blocks, top, mode, more)
            wait_release()
            k = wait_key()
            if k == EXITK or k == OK or k == EXE:
                wait_release()
                return
            if k == DOWN:
                if end < len(blocks):
                    top += 1
            elif k == UP:
                if top > 0:
                    top -= 1
            elif k == PAGEDOWN:
                if end < len(blocks):
                    top = end
            elif k == PAGEUP:
                top = top - 8 if top > 8 else 0
            elif k == FORMAT and more:
                mode = (mode + 1) % 3
                casutil.FULL = (mode == 2)
                top = 0
    finally:
        casutil.FULL = False

def show_lines(title, lines):
    result(title, '', lines)

# ---- Calculate -------------------------------------------------------------------

def _calc_lines(tree, val):
    lines = [('m', tree)]
    lines.append(casutil.fmt(val))
    try:
        simp = caseng.simplify(tree)
        ex = caseng.tostr(simp)
        if not caseng.vars_in(simp) and ex != casutil.fmt(val) and len(ex) <= 40 and ex != casutil.sf3(val):
            lines.append(('w', 'exact ' + ex))
    except Exception:
        pass
    if isinstance(val, complex):
        lines.append(('w', 'mod ' + casutil.fmt(caseng._cabs(val)) + '  arg ' + casutil.fmt(caseng._carg(val))))
    elif isinstance(val, float):
        lines.append(('w', casutil.sf3(val) + ' (3 s.f.)'))
    return lines

def calc_section():
    while True:
        s = input_line('Calculate', 'expression', '')
        if s is None:
            return
        tree = caslex.parse(s)
        if tree is None:
            flash('cannot read that')
            continue
        try:
            val = casutil.ev(tree)
        except ValueError as e:
            flash(str(e))
            continue
        if isinstance(val, float) and (val > 1.7e308 or val < -1.7e308):
            flash('too large')
            continue
        caseng.ANS = val
        result('Calculate', s, lambda: _calc_lines(tree, val))

# ---- CAS ---------------------------------------------------------------------------

def _tidy(t):
    return cascalc.tidy(t)

def _cas_op(op, tree, s):
    if op == 0:
        return [('m', _tidy(caseng.diff(tree)))]
    if op == 1:
        return [('m', _tidy(caseng.diff(_tidy(caseng.diff(tree)))))]
    if op == 2:
        r = cascalc.integ(tree)
        if r is None:
            return [('!', 'no elementary integral; use definite')]
        return [('m', _tidy(r)), ('w', '+ c')]
    if op == 3:
        v = casutil.ask('a,b', 'limits')
        if v is None:
            return None
        r = cascalc.defint(tree, v[0], v[1], casutil.DEG)
        if r is None:
            return [('!', 'cannot evaluate over that range')]
        return ['integral = ' + casutil.fmt(r), ('w', 'from ' + casutil.fmt(v[0]) + ' to ' + casutil.fmt(v[1]))]
    if op == 4:
        v = casutil.ask('a', 'at x =')
        if v is None:
            return None
        a = v[0]
        y = casutil.ev(tree, a)
        g = casutil.ev(caseng.diff(tree), a)
        lines = ['y = ' + casutil.fmt(y) + '  dy/dx = ' + casutil.fmt(g)]
        lines.append('tangent y = ' + casutil.fmt(g) + 'x + ' + casutil.fmt(y - g * a))
        if g != 0:
            lines.append('normal y = ' + casutil.fmt(-1.0 / g) + 'x + ' + casutil.fmt(y + a / g))
        else:
            lines.append('normal x = ' + casutil.fmt(a))
        return lines
    if op == 5:
        d1 = _tidy(caseng.diff(tree))
        roots = cascalc.solve(d1)
        if not roots:
            return [('!', 'no stationary points found in the search range')]
        d2 = _tidy(caseng.diff(d1))
        lines = []
        for r in roots:
            y = casutil.ev(tree, r)
            c = casutil.evx(d2, r)
            kind = 'min' if (c is not None and c > 1e-9) else ('max' if (c is not None and c < -1e-9) else 'inflection?')
            lines.append('(' + casutil.fmt(r) + ', ' + casutil.fmt(y) + ')  ' + kind)
        lines.append(('mw', d1))
        return lines
    if op == 6:
        return [('m', _tidy(tree))]
    if op == 7:
        return [('m', caspoly.expand(tree))]
    if op == 8:
        r = caspoly.factor(tree)
        if r is None:
            return [('!', 'does not factorise over the rationals')]
        return [('m', r)]
    if op == 9:
        if tree[0] != '/':
            return [('!', 'type it as one fraction, e.g. (3x+5)/((x-1)(x+2))')]
        try:
            r = caspoly.partial(tree[1], tree[2])
        except Exception:
            r = None
        if r is None:
            return [('!', 'cannot split: need polynomials with linear/quadratic factors')]
        quot, terms = r
        lines = []
        if quot is not None:
            lines.append(('m', quot))
        for top, fac, power in terms:
            den = fac
            if power > 1:
                den = ('^', fac, ('n', power))
            lines.append(('m', ('/', top, den)))
        if not terms:
            lines.append(('w', 'divides exactly'))
        return lines
    if op == 10 or op == 11:
        target = tree
        if op == 11:
            v = casutil.ask('k', 'f(x) = k')
            if v is None:
                return None
            target = ('-', tree, ('n', v[0]))
        roots = cascalc.solve(target, deg=casutil.DEG)
        if not roots:
            return [('!', 'no real roots found in the search range')]
        return ['x = ' + ', '.join([casutil.fmt(r) for r in roots])]
    if op == 12:
        v = casutil.ask('x', 'evaluate at')
        if v is None:
            return None
        return ['f(' + casutil.fmt(v[0]) + ') = ' + casutil.fmt(casutil.ev(tree, v[0]))]
    if op == 13:
        v = casutil.ask('start,step', 'table')
        if v is None:
            return None
        lines = []
        i = 0
        while i < 12:
            xv = v[0] + i * v[1]
            y = casutil.evx(tree, xv)
            lines.append(('w', 'x=' + casutil.fmt(xv) + '   f(x)=' + ('undefined' if y is None else casutil.fmt(y))))
            i += 1
        lines.insert(0, 'table of f(x)')
        return lines
    if op == 14:
        import plot
        plot.run([tree], -6.0, 6.0, 'y', 'y = ' + s)
        return None
    return None

CAS_OPS = ['d/dx', 'd2/dx2', 'integrate', 'definite integral a..b',
           'tangent + normal at x=a', 'stationary points', 'simplify', 'expand',
           'factorise', 'partial fractions', 'solve f(x)=0', 'solve f(x)=k',
           'evaluate at x', 'table', 'plot']

def cas_section():
    while True:
        s = input_line('CAS', 'f(x)', '')
        if s is None:
            return
        tree = caslex.parse(s)
        if tree is None:
            flash('cannot read that')
            continue
        op = 0
        while True:
            op = menu('f(x) = ' + s, CAS_OPS, op)
            if op < 0:
                break
            try:
                lines = _cas_op(op, tree, s)
            except ValueError as e:
                lines = [('!', str(e))]
            except Exception as e:
                lines = [('!', 'error: ' + str(e))]
            if lines is not None:
                result(CAS_OPS[op], s, lines)

# ---- sections ------------------------------------------------------------------------

MATHS = ('mpure', 'mcalc', 'mstat', 'mmech')
FURTHER = ('fcore', 'fcalc', 'fmech', 'fstat')

def _sections(mods):
    out = []
    for name in mods:
        for code, title, tools in __import__(name).SECTIONS:
            out.append((code, title, tools))
    return out

def _tools_menu(code, title, tools):
    sel = 0
    while True:
        sel = menu(code + ' ' + title, [t[0] for t in tools], sel)
        if sel < 0:
            return
        label, spec, fn = tools[sel]
        try:
            casutil.run_tool(label, spec, fn)
        except Exception as e:
            flash('tool error: ' + str(e))

def qual_section(title, mods):
    secs = _sections(mods)
    labels = [c + '  ' + t for c, t, tools in secs]
    sel = 0
    while True:
        sel = menu(title, labels, sel)
        if sel < 0:
            return
        code, stitle, tools = secs[sel]
        _tools_menu(code, stitle, tools)

def formulae_section():
    import formulae
    sel = 0
    while True:
        sel = menu('Formulae', [s[0] for s in formulae.SHEETS], sel)
        if sel < 0:
            return
        title, lines = formulae.SHEETS[sel]
        show_lines(title, [('w', ln) for ln in lines])

def main():
    sel = 0
    while True:
        angle = 'Angle: DEG' if casutil.DEG else 'Angle: RAD'
        sel = menu('MATHS TOOLKIT  AQA 7357 + 7367',
                   ['Calculate', 'CAS  f(x)', 'Maths 7357', 'Further 7367',
                    'Formulae', angle], sel)
        if sel < 0:
            return
        if sel == 0:
            calc_section()
        elif sel == 1:
            cas_section()
        elif sel == 2:
            qual_section('MATHS 7357', MATHS)
        elif sel == 3:
            qual_section('FURTHER 7367', FURTHER)
        elif sel == 4:
            formulae_section()
        elif sel == 5:
            casutil.DEG = not casutil.DEG
