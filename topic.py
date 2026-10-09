# Topic screens (docs/redesign.md, mockups 1-4, C, I, 7-10).
# Type the question as written (DOWN adds a second row for pairs); EXE reads
# its form (recog.py), shows what it found in grey and the actions that fit
# (acts.py) as up to 6 numbered tiles; TOOLS lists every one (More). An
# action asks only for what is missing, then the answer page shows the
# working in mark-scheme order with the answer boxed: TOOLS hides or shows
# the working, FORMAT flips the answer between exact and decimal.
from casioplot import set_pixel, draw_string, clear_screen, show_screen
import casui
import nat
from casui import (W, TOP, BOT, INK, ACC, GREY, LGREY, WHITE, RED, BAR,
                   UP, DOWN, LEFT, RIGHT, OK, EXE, EXITK, SETTINGS, SHIFT, ALPHA,
                   TOOLS, MENU, DEL, FORMAT, PAGEUP, PAGEDOWN, LINESTART, LINEEND,
                   DIGITS, box, hline, vline, ctext, clip, text_w)

# id -> (title, example shown faintly while the input is empty, old sections)
TOPICS = {
    'alg': ('Algebra', 'x^2 + 3x + k   or  2 rows', 'B'),
    'exp': ('Exp and logs', '4^x - 3*2^x + 2 = 0', 'F'),
    'geo': ('Coord geometry', 'line or circle', 'C'),
    'calc': ('Calculus', 'y = x^3 - 3x  or  dy/dx = ...', 'GH'),
}

STATE = {}      # topic id -> {'rows': [...], 'sel': tile, 'key': text, 'F': form, 'offers': [...]}

def free():
    for st in STATE.values():
        st.pop('F', None)
        st.pop('offers', None)
        st.pop('key', None)

def _reg():
    import home
    if free not in home.FREE:
        home.FREE.append(free)

# ---- layout -------------------------------------------------------------------------------

def _layout(eds):
    # [(baseline, asc, desc)] for the rows, and the y of the line under them
    out = []
    y = TOP + 8
    for ed in eds:
        w, a, d = nat.measure(ed.root, 0)
        base = y + a
        out.append((base, a, d))
        y = base + d + 8
    sep = y - 2 if y - 2 > 62 else 62
    return out, sep

def _rows(eds, cur, lay, editing):
    i = 0
    for ed in eds:
        base = lay[i][0]
        nat.draw(ed if (editing and i == cur) else None, ed.root, 8, base, 368)
        if i == cur and editing:
            ed.shown = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], lay[i][1], lay[i][2])
        i += 1

def _hint(tid, eds, sep):
    if len(eds) == 1 and not eds[0].root:
        draw_string(16, TOP + 8, TOPICS[tid][1], LGREY, 'medium')

# ---- tiles --------------------------------------------------------------------------------

def _grid(n, ty):
    # rows of 2 tiles that fit below ty, and their height
    h = BOT + 1 - ty
    rows = (n + 1) // 2
    if rows > 3:
        rows = 3
    while rows > 1 and h // rows < 26:
        rows -= 1
    if rows < 1:
        rows = 1
    th = h // rows
    if th > 35:
        th = 35
    return rows, th

def _tile(i, label, on, ty, th, full=False):
    # full: on a cleared screen, so there is no old highlight to rub out
    tw = W // 2
    x0 = (i % 2) * tw
    y0 = ty + (i // 2) * th
    x1 = x0 + tw - 1
    y1 = y0 + th - 1
    if on:
        box(x0 + 2, y0 + 2, x1 - 2, y1 - 2, ACC)
        box(x0 + 3, y0 + 3, x1 - 3, y1 - 3, ACC)
    else:
        box(x0 + 2, y0 + 2, x1 - 2, y1 - 2, LGREY)
        if not full:
            box(x0 + 3, y0 + 3, x1 - 3, y1 - 3, WHITE)
    draw_string(x0 + 8, y0 + (th - 18) // 2, str(i + 1), LGREY if not on else ACC, 'small')
    if text_w(label, 'medium') <= tw - 30:
        ctext(x0 + tw // 2 + 4, y0 + (th - 18) // 2, label, ACC if on else INK, 'medium')
    else:
        # a long label in the small font rather than cut short
        ctext(x0 + tw // 2 + 6, y0 + (th - 12) // 2, clip(label, tw - 28, 'small'),
              ACC if on else INK, 'small')

def _draw(tid, eds, cur, mode, st, shift=False, alpha=False):
    clear_screen()
    casui.status(TOPICS[tid][0], shift, alpha)
    lay, sep = _layout(eds)
    _hint(tid, eds, sep)
    _rows(eds, cur, lay, mode == 'edit')
    hline(0, W - 1, sep, LGREY)
    st['sep'] = sep
    if mode == 'act' and st.get('F') is not None:
        draw_act(st, sep)
    show_screen()

def draw_act(st, sep):
    # the grey detected line and the tiles under the input
    F = st['F']
    if True:
        y = sep + 4
        more = 'TOOLS more'
        mw = text_w(more, 'medium')
        if F.err:
            draw_string(8, y, clip(F.err, W - 16, 'medium'), RED, 'medium')
        else:
            draw_string(8, y, clip(F.note, W - 28 - mw, 'medium'), GREY, 'medium')
            draw_string(W - 8 - mw, y, more, LGREY, 'medium')
        offers = st['offers']
        ty = sep + 22
        n = len(offers)
        if n == 0 and not F.err:
            draw_string(8, ty + 6, 'nothing in this topic fits;', GREY, 'medium')
            draw_string(8, ty + 26, 'TOOLS for every tool', GREY, 'medium')
        rows, th = _grid(n, ty)
        st['grid'] = (ty, th, min(n, rows * 2))
        i = 0
        while i < n and i < rows * 2:
            _tile(i, offers[i][0], i == st['sel'], ty, th, True)
            i += 1

def _fast(eds, cur, st):
    # typing that only changed the row being typed: undraw it, draw it again
    ed = eds[cur]
    sh = getattr(ed, 'shown', None)
    if sh is None:
        return False
    row, base, dx, caret, a0, d0 = sh
    w, a, d = nat.measure(ed.root, 0)
    if a != a0 or d != d0 or not row or not ed.root:
        return False
    nat.undraw(row, 8, base, dx, caret, WHITE)
    nat.draw(ed, ed.root, 8, base, 368)
    ed.shown = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d)
    casui.status_mode(False, False)
    show_screen()
    return True

# ---- recognising ----------------------------------------------------------------------------

def texts(eds):
    return [nat.lin(ed.root) for ed in eds if ed.root]

def recognise(tid, eds, st):
    key = '|'.join(texts(eds))
    if st.get('key') == key and st.get('F') is not None:
        return st['F']
    casui.busy()
    import recog
    import acts
    st['rows'] = [nat.copy(ed.root) for ed in eds]
    F = recog.form(texts(eds))
    st['F'] = None
    st['offers'] = []
    st['F'] = F
    st['offers'] = [] if F.err else acts.offers(F, tid)
    st['key'] = key
    st['sel'] = 0
    return F

# ---- the screen -------------------------------------------------------------------------------

def run(tid):
    _reg()
    st = STATE.get(tid)
    if st is None:
        st = {'rows': [[]], 'sel': 0}
        STATE[tid] = st
    eds = [nat.Ed(nat.copy(r)) for r in st['rows']]
    cur = len(eds) - 1
    mode = 'edit'
    shift = False
    alpha = False
    redraw = 'full'     # 'full', 'fast' (only the typed row) or None
    try:
        while True:
            if redraw == 'fast' and mode == 'edit' and _fast(eds, cur, st):
                pass
            elif redraw:
                _draw(tid, eds, cur, mode, st, shift, alpha)
            redraw = 'full'
            k = casui.next_key()
            if k == SETTINGS:
                casui.settings()
                continue
            if mode == 'act':
                r = _act_key(tid, eds, st, k)
                if r == 'stay':
                    continue
                if r == 'none':
                    redraw = None
                    continue
                mode = 'edit'
                cur = len(eds) - 1
                eds[cur].end()
                if r == 'type':
                    # this key starts the edit
                    if k == SHIFT:
                        shift = True
                    elif k == ALPHA:
                        alpha = True
                    else:
                        casui.edit_key(eds[cur], k, False, False)
                continue
            if k == SHIFT or k == ALPHA:
                if k == SHIFT:
                    shift = not shift
                    alpha = False
                else:
                    alpha = not alpha
                    shift = False
                casui.status_mode(shift, alpha)
                show_screen()
                redraw = None
                continue
            if k == EXITK:
                if len(eds) > 1 and not eds[-1].root:
                    eds.pop()
                    cur = 0
                    continue
                casui.wait_release()
                return
            if k == OK or k == EXE or k == TOOLS:
                if not texts(eds):
                    redraw = None
                    continue
                hole = False
                for ed in eds:
                    if nat.empty_hole(ed.root):
                        hole = True
                if hole:
                    casui.flash('fill in the empty box')
                    continue
                F = recognise(tid, eds, st)
                shift = False
                alpha = False
                mode = 'act'
                if F.err:
                    # the reason in red under the input; typing carries on
                    _draw(tid, eds, cur, mode, st)
                    mode = 'edit'
                    redraw = None
                elif k == TOOLS:
                    _draw(tid, eds, cur, mode, st)
                    more(tid, st)
                continue
            ed = eds[cur]
            if k == DOWN or k == UP:
                if ed.vert(k == UP):
                    redraw = 'fast'
                elif k == DOWN and cur == 0:
                    if len(eds) == 1:
                        eds.append(nat.Ed())
                    cur = 1
                elif k == UP and cur == 1:
                    cur = 0
                    if not eds[1].root:
                        eds.pop()
                else:
                    redraw = None
                continue
            if casui.edit_key(ed, k, shift, alpha):
                redraw = 'fast' if k != MENU else 'full'
            elif not shift and not alpha:
                redraw = None
            shift = False
            alpha = False
    finally:
        st['rows'] = [nat.copy(ed.root) for ed in eds]

def _act_key(tid, eds, st, k):
    # a key while the tiles show: 'stay' (redraw), 'none' (nothing to do),
    # 'edit' (back to typing), 'type' (back to typing with this key)
    offers = st['offers']
    ty, th, shown = st.get('grid', (0, 0, 0))
    sel = st['sel']
    if k == EXITK:
        return 'edit'
    if k == TOOLS:
        more(tid, st)
        return 'stay'
    if (k == OK or k == EXE) and shown:
        run_offer(tid, st, offers[sel])
        return 'stay'
    d = DIGITS.get(k)
    if d is not None and 1 <= d <= shown:
        st['sel'] = d - 1
        run_offer(tid, st, offers[d - 1])
        return 'stay'
    if k in (LEFT, RIGHT, UP, DOWN) and shown:
        new = sel
        if k == LEFT and sel % 2 == 1:
            new = sel - 1
        elif k == RIGHT and sel % 2 == 0 and sel + 1 < shown:
            new = sel + 1
        elif k == DOWN and sel + 2 < shown:
            new = sel + 2
        elif k == DOWN and sel + 2 >= shown and sel // 2 < (shown - 1) // 2:
            new = shown - 1
        elif k == UP and sel >= 2:
            new = sel - 2
        elif k == UP:
            return 'edit'
        if new != sel:
            _tile(sel, offers[sel][0], False, ty, th)
            _tile(new, offers[new][0], True, ty, th)
            st['sel'] = new
            show_screen()
        return 'none'
    if k == UP:
        return 'edit'
    if k in (LEFT, RIGHT, DOWN, OK, EXE, FORMAT, PAGEUP, PAGEDOWN):
        return 'none'
    if k == DEL or k == SHIFT or k == ALPHA or k == MENU or k == LINESTART or k == LINEEND:
        return 'type'
    if nat.typed(nat.Ed(), k, False, False):
        return 'type'
    return 'none'

# ---- More ----------------------------------------------------------------------------------

def more(tid, st):
    # every action that fits, then the old tool menus
    offers = st.get('offers') or []
    labels = [o[0] for o in offers] + ['All tools']
    sel = 0
    while True:
        sel = casui.menu(TOPICS[tid][0] + '  More', labels, sel)
        if sel < 0:
            return
        if sel == len(offers):
            all_tools(tid)
        else:
            run_offer(tid, st, offers[sel])

def all_tools(tid):
    import home
    secs = home.old_sections('o:' + TOPICS[tid][2])
    labels = [s[1] for s in secs] + ['Every tool (old home)']
    sel = 0
    while True:
        sel = casui.menu('All tools', labels, sel)
        if sel < 0:
            return
        if sel < len(secs):
            casui._tools_menu(*secs[sel])
        else:
            casui.classic()

# ---- running an action ---------------------------------------------------------------------

def run_offer(tid, st, off):
    F = st['F']
    label, mod, fn, arg, ask = off
    vals = None
    if ask:
        vals = prompt(tid, st, label, ask)
        if vals is None:
            return
    casui.busy()
    lines = engine(mod, fn, F, arg, vals)
    if lines is not None:
        answer(label, lines)

def engine(mod, fn, F, arg, vals):
    # one action's lines; errors become a warning line, never a crash
    m = __import__(mod)
    try:
        return getattr(m, fn)(F, arg, vals)
    except MemoryError:
        raise
    except ValueError as e:
        return [('!', str(e) or 'cannot do that')]
    except ZeroDivisionError:
        return [('!', 'division by zero')]
    except OverflowError:
        return [('!', 'number too large')]
    except (casui.Home, casui.Idle):
        raise
    except Exception as e:
        return [('!', 'error: ' + str(e))]

# ---- prompts (mockup C): only what is missing ------------------------------------------------
# ask is a list of lines (label, fields, open) with fields 1 or 2 boxes; open
# lets '?' mean "no limit". A choice is ('choose', [options]).

def prompt(tid, st, label, ask):
    if ask[0] == 'choose':
        i = casui.menu(label, ask[1])
        return None if i < 0 else [i]
    eds = []
    for ln in ask:
        for j in range(ln[1]):
            eds.append(nat.Ed())
    cur = 0
    shift = False
    alpha = False
    while True:
        _draw_prompt(tid, st, label, ask, eds, cur, shift, alpha)
        k = casui.next_key()
        if k == SHIFT or k == ALPHA:
            if k == SHIFT:
                shift = not shift
                alpha = False
            else:
                alpha = not alpha
                shift = False
            continue
        if k == EXITK:
            casui.wait_release()
            return None
        if k == SETTINGS:
            casui.settings()
            continue
        if k == DOWN and not eds[cur].vert(False):
            cur = (cur + 1) % len(eds)
            continue
        if k == UP and not eds[cur].vert(True):
            cur = (cur - 1) % len(eds)
            continue
        if k == OK or k == EXE:
            empty = [i for i in range(len(eds)) if not eds[i].root and not _open(ask, i)]
            if empty:
                # EXE with a box still empty: go to it (a box that may stay
                # empty, like "then at t =", doesn't stop it)
                cur = empty[0]
                continue
            vals = _read(ask, eds)
            if vals is None:
                continue
            casui.wait_release()
            return vals
        if casui.edit_key(eds[cur], k, shift, alpha):
            shift = False
            alpha = False

def _open(ask, i):
    # box i may be left empty
    for ln in ask:
        if i < ln[1]:
            return ln[2]
        i -= ln[1]
    return False

def _read(ask, eds):
    import caslex
    out = []
    i = 0
    for ln in ask:
        for j in range(ln[1]):
            s = nat.lin(eds[i].root)
            i += 1
            if (s.strip() == '?' or not s.strip()) and ln[2]:
                out.append(None)
                continue
            try:
                t = caslex.parse(s)
            except ValueError as e:
                casui.flash(ln[0] + ': ' + str(e))
                return None
            if t is None:
                casui.flash(ln[0] + ': cannot read that')
                return None
            out.append(t)
    return out

def _field(x, y, w, ed, on):
    wd, a, d = nat.measure(ed.root, 0)
    h = a + d + 6 if a + d + 6 > 22 else 22
    box(x, y, x + w, y + h, ACC if on else LGREY)
    if on:
        box(x + 1, y + 1, x + w - 1, y + h - 1, ACC)
    nat.draw(ed if on else None, ed.root, x + 6, y + 3 + a, w - 10)
    return h

def _draw_prompt(tid, st, label, ask, eds, cur, shift, alpha):
    clear_screen()
    casui.status(TOPICS[tid][0], shift, alpha)
    if 'header' in st:
        # a topic with its own input layout (Coord geometry's point boxes)
        sep = st['header']()
    else:
        rows = [nat.Ed(r) for r in st['rows'] if r]
        lay, sep = _layout(rows)
        _rows(rows, -1, lay, False)
    hline(0, W - 1, sep, LGREY)
    y = sep + 6
    draw_string(8, y, clip(label, W - 16, 'medium'), ACC, 'medium')
    y += 26
    i = 0
    for ln in ask:
        name, n, opn = ln
        draw_string(8, y + 3, name, INK, 'medium')
        x = 16 + text_w(name, 'medium')
        if n == 2:
            draw_string(x, y + 3, '(', INK, 'medium')
            x += 10
            h = _field(x, y, 80, eds[i], i == cur)
            draw_string(x + 86, y + 3, ',', INK, 'medium')
            h2 = _field(x + 96, y, 80, eds[i + 1], i + 1 == cur)
            draw_string(x + 182, y + 3, ')', INK, 'medium')
            h = h if h > h2 else h2
        else:
            h = _field(x, y, 120, eds[i], i == cur)
        if opn and n == 1:
            draw_string(x + 130, y + 3, 'may be empty', LGREY, 'medium')
        i += n
        y += h + 6
    if y + 18 <= BOT:
        draw_string(8, y + 2, 'EXE to work out', GREY, 'medium')
    show_screen()

# ---- the answer page (mockups 7-10, D) ------------------------------------------------------

def _worth(ex):
    for s in ('sqrt', 'log', 'ln', 'pi', 'e^', '/', '^('):
        if s in ex:
            return True
    return False

def shown(item, view):
    # one boxed answer as text for the view: 'exact', 'decimal' or 'both'
    pre, ex, dc = item[1], item[2], item[3]
    if ex is None:
        return pre + (dc or '')
    if dc is None or view == 'exact':
        return pre + ex
    if view == 'decimal':
        return pre + dc
    if pre == '' and ' = ' in dc:
        # a pair of values: the exact pair, then the decimals under it
        return ex + '\n' + dc
    if _worth(ex) and (pre == '' or pre[-2:] == '= '):
        return pre + ex + ' = ' + dc
    return pre + ex

def _typeset(s):
    # one line -> display blocks (tex.py), broken to the screen width
    return casui._blocks([s], 1)

def layout(lines, work, view):
    # -> items: ('l', block, colour) and ('b', [blocks]) for a box
    items = []
    seen_box = False
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if isinstance(ln, tuple) and ln[0] == '=':
            group = []
            while i < n and isinstance(lines[i], tuple) and lines[i][0] == '=':
                for part in shown(lines[i], view).split('\n'):
                    group += _typeset(part)
                i += 1
            items.append(('b', group))
            seen_box = True
            continue
        i += 1
        if not work and not seen_box and not (isinstance(ln, tuple) and ln[0] == '!'):
            continue
        if isinstance(ln, tuple) and ln[0] in ('w', '!'):
            c = GREY if ln[0] == 'w' else RED
            for b in _typeset(ln[1]):
                items.append(('l', b, c))
        else:
            for b in casui._blocks([ln], 1):
                items.append(('l', b, INK))
    return items

def _h(it):
    if it[0] == 'b':
        h = 6
        for b in it[1]:
            h += b[3]
        return h
    return it[1][3]

def _draw_answer(title, items, top, work):
    clear_screen()
    casui.status(title, False, False, 'working' if work else 'answer')
    y = TOP + 3
    i = top
    n = len(items)
    while i < n:
        it = items[i]
        h = _h(it)
        if y + h > BOT + 2 and i > top:
            break
        if it[0] == 'b':
            box(2, y + 1, W - 9, y + h - 1, ACC)
            yy = y + 3
            for b in it[1]:
                casui.play(b, 2, yy, ACC)
                yy += b[3]
            y += h + 2
        else:
            casui.play(it[1], 0, y, it[2])
            y += h
        i += 1
    if top > 0 or i < n:
        span = BOT - TOP
        t0 = TOP + span * top // n
        t1 = TOP + span * i // n
        vline(W - 3, TOP, BOT, BAR)
        vline(W - 2, TOP, BOT, BAR)
        vline(W - 3, t0, t1, ACC)
        vline(W - 2, t0, t1, ACC)
    show_screen()
    return i

NEXT = {'both': 'exact', 'exact': 'decimal', 'decimal': 'both'}

def answer(title, lines):
    work = True
    view = casui.SET['answers']
    start = view
    cache = {}
    top = 0
    while True:
        key = (work, view)
        items = cache.get(key)
        if items is None:
            items = layout(lines, work, view)
            if not items:
                items = [('l', _typeset('nothing to show')[0], RED)]
            cache[key] = items
        if top >= len(items):
            top = len(items) - 1
        end = _draw_answer(title, items, top, work)
        while True:
            k = casui.next_key()
            if k == EXITK or k == OK or k == EXE:
                casui.wait_release()
                return
            if k == DOWN and end < len(items):
                top += 1
            elif k == UP and top > 0:
                top -= 1
            elif k == PAGEDOWN and end < len(items):
                top = end
            elif k == PAGEUP and top > 0:
                top = top - 6 if top > 6 else 0
            elif k == TOOLS:
                work = not work
                top = 0
            elif k == FORMAT:
                # both -> exact -> decimal -> both; exact <-> decimal otherwise
                if start == 'both':
                    view = NEXT[view]
                else:
                    view = 'decimal' if view == 'exact' else 'exact'
                top = 0
            elif k == SETTINGS:
                casui.settings()
            else:
                continue
            break
