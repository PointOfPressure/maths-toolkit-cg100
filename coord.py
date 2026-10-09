# Coord geometry (docs/redesign.md, mockup 5): points in labelled boxes,
# A ( x , y ), and a row for a line or circle typed as written (DOWN adds a
# second one, for a line and a circle or two curves). EXE reads what is
# filled in and shows the actions that fit, as every topic does (topic.py
# draws the tiles, More, the prompts and the answer page).
from casioplot import draw_string, clear_screen, show_screen
import casui
import nat
import topic
from casui import (W, TOP, INK, LGREY, GREY, UP, DOWN, LEFT, RIGHT, OK, EXE, EXITK,
                   SETTINGS, SHIFT, ALPHA, TOOLS, MENU, DEL, hline, text_w)

NAMES = 'ABC'
PH = 27          # a point row's height
BX = 90          # a box's width

def _state():
    st = topic.STATE.get('geo')
    if st is None:
        st = {'pts': [[[], []], [[], []]], 'eqs': [[]], 'sel': 0}
        topic.STATE['geo'] = st
    return st

class Cell:
    # one box: ('p', point, 0 or 1) or ('e', row)
    def __init__(self, kind, i, j, row):
        self.kind = kind
        self.i = i
        self.j = j
        self.ed = nat.Ed(nat.copy(row))

def _cells(st):
    out = []
    for i in range(len(st['pts'])):
        out.append(Cell('p', i, 0, st['pts'][i][0]))
        out.append(Cell('p', i, 1, st['pts'][i][1]))
    for i in range(len(st['eqs'])):
        out.append(Cell('e', i, 0, st['eqs'][i]))
    return out

def _save(st, cells):
    pts = []
    eqs = []
    for c in cells:
        if c.kind == 'p':
            if c.j == 0:
                pts.append([nat.copy(c.ed.root), []])
            else:
                pts[-1][1] = nat.copy(c.ed.root)
        else:
            eqs.append(nat.copy(c.ed.root))
    st['pts'] = pts
    st['eqs'] = eqs or [[]]

def _draw_input(cells, cur):
    # the boxes and rows, the caret in cell cur (-1: none); -> the y under them
    y = TOP + 4
    npts = len([c for c in cells if c.kind == 'p']) // 2
    for c in cells:
        if c.kind != 'p':
            continue
        if c.j == 0:
            draw_string(8, y + 3, NAMES[c.i], INK, 'medium')
            draw_string(26, y + 3, '(', INK, 'medium')
            topic._field(36, y, BX, c.ed, cells.index(c) == cur)
            draw_string(36 + BX + 5, y + 3, ',', INK, 'medium')
        else:
            topic._field(46 + BX, y, BX, c.ed, cells.index(c) == cur)
            draw_string(52 + 2 * BX, y + 3, ')', INK, 'medium')
            if c.i == npts - 1 and npts < 3:
                draw_string(70 + 2 * BX, y + 3, '+ point: MENU', LGREY, 'medium')
            y += PH
    eqs = [c for c in cells if c.kind == 'e']
    for c in eqs:
        k = cells.index(c)
        if not c.ed.root and k != cur:
            draw_string(16, y + 4, 'line or circle (as written)', LGREY, 'medium')
            y += 24
            continue
        w, a, d = nat.measure(c.ed.root, 0)
        base = y + 6 + a
        nat.draw(c.ed if k == cur else None, c.ed.root, 8, base, 368)
        y = base + d + 6
    return y + 2

def _draw(st, cells, cur, mode, shift=False, alpha=False):
    clear_screen()
    casui.status(topic.TOPICS['geo'][0], shift, alpha)
    sep = _draw_input(cells, cur if mode == 'edit' else -1)
    hline(0, W - 1, sep, LGREY)
    st['sep'] = sep
    if mode == 'act' and st.get('F') is not None:
        topic.draw_act(st, sep)
    show_screen()

def texts(cells):
    pts = []
    eqs = []
    for c in cells:
        s = nat.lin(c.ed.root)
        if c.kind == 'p':
            if c.j == 0:
                pts.append([s, ''])
            else:
                pts[-1][1] = s
        elif s:
            eqs.append(s)
    return pts, eqs

def recognise(st, cells):
    pts, eqs = texts(cells)
    key = repr(pts) + '|' + '|'.join(eqs)
    if st.get('key') == key and st.get('F') is not None:
        return st['F']
    casui.busy()
    import recog
    import acts
    F = recog.geo(pts, eqs)
    st['F'] = F
    st['offers'] = [] if F.err else acts.offers(F, 'geo')
    st['key'] = key
    st['sel'] = 0
    return F

def _move(cells, cur, k):
    # UP/DOWN between rows, keeping the column in point rows
    c = cells[cur]
    if k == DOWN:
        j = cur + (2 - c.j if c.kind == 'p' else 1)
        if c.kind == 'p' and j < len(cells) and cells[j].kind == 'p':
            return j + c.j
        return j if j < len(cells) else cur
    if c.kind == 'p':
        j = cur - 2
        return j if j >= 0 else cur
    j = cur - 1
    if j >= 0 and cells[j].kind == 'p':
        return j - 1
    return j if j >= 0 else cur

def run():
    st = _state()
    topic._reg()
    st['header'] = lambda: _draw_input(cells, -1)
    cells = _cells(st)
    cur = 0
    mode = 'edit'
    shift = False
    alpha = False
    redraw = True
    try:
        while True:
            if redraw:
                _draw(st, cells, cur, mode, shift, alpha)
            redraw = True
            k = casui.next_key()
            if k == SETTINGS:
                casui.settings()
                continue
            if mode == 'act':
                r = topic._act_key('geo', None, st, k)
                if r == 'stay':
                    continue
                if r == 'none':
                    redraw = False
                    continue
                mode = 'edit'
                if r == 'type':
                    if k == SHIFT:
                        shift = True
                    elif k == ALPHA:
                        alpha = True
                    elif k != MENU:
                        casui.edit_key(cells[cur].ed, k, False, False)
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
                redraw = False
                continue
            if k == EXITK:
                casui.wait_release()
                return
            if k in (OK, EXE, TOOLS):
                pts, eqs = texts(cells)
                if not eqs and not [p for p in pts if p[0] or p[1]]:
                    redraw = False
                    continue
                for c in cells:
                    if nat.empty_hole(c.ed.root):
                        casui.flash('fill in the empty box')
                        break
                else:
                    F = recognise(st, cells)
                    shift = False
                    alpha = False
                    mode = 'act'
                    if F.err:
                        _draw(st, cells, cur, mode)
                        mode = 'edit'
                        redraw = False
                    elif k == TOOLS:
                        _draw(st, cells, cur, mode)
                        topic.more('geo', st)
                continue
            c = cells[cur]
            ed = c.ed
            if k == MENU and c.kind == 'p':
                # + point (A, B, C at most)
                npts = len([x for x in cells if x.kind == 'p']) // 2
                if npts < 3:
                    at = 2 * npts
                    cells.insert(at, Cell('p', npts, 1, []))
                    cells.insert(at, Cell('p', npts, 0, []))
                    cur = at
                continue
            if k == DEL and c.kind == 'p' and not ed.root:
                other = cells[cur + 1] if c.j == 0 else cells[cur - 1]
                npts = len([x for x in cells if x.kind == 'p']) // 2
                if not other.ed.root and c.i == npts - 1 and npts > 1:
                    first = cur - c.j
                    del cells[first:first + 2]
                    cur = first - 2
                    continue
                if c.j == 1:
                    cur -= 1
                    continue
            if k == LEFT and c.kind == 'p' and c.j == 1 and not ed.stack and ed.i == 0:
                cur -= 1
                continue
            if k == RIGHT and c.kind == 'p' and c.j == 0 and not ed.stack and ed.i == len(ed.root):
                cur += 1
                continue
            if k == UP or k == DOWN:
                if ed.vert(k == UP):
                    continue
                if k == DOWN and c.kind == 'e' and cur == len(cells) - 1 and ed.root and \
                        len([x for x in cells if x.kind == 'e']) < 2:
                    cells.append(Cell('e', 1, 0, []))
                    cur = len(cells) - 1
                    continue
                if k == UP and c.kind == 'e' and c.i == 1 and not ed.root:
                    cells.pop()
                    cur -= 1
                    continue
                n = _move(cells, cur, k)
                if n == cur:
                    redraw = False
                cur = n
                continue
            if casui.edit_key(ed, k, shift, alpha):
                shift = False
                alpha = False
            elif not shift and not alpha:
                redraw = False
            else:
                shift = False
                alpha = False
    finally:
        _save(st, cells)
        st.pop('header', None)
