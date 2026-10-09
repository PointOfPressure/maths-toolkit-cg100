# The old screens, loaded only when one is opened: Calculate with its history,
# the CAS menu, Solve and Graph by typing, the input line and result screen of
# the old tool menus, Notes, and the old icon home grid (More > All tools).
# They lived in casui.py; out here the new home and topic screens don't carry
# them, as nothing can be unloaded on the calculator. casui keeps their names
# (small wrappers) and their data (HIST, ANS, CALC, _LAST, _INP).
from casioplot import *
import casui
from casui import *
from casui import _INP, _LAST, _blocks

# their caches (HIST, _INP) are casui's, and casui._free drops them

# ---- icons ---------------------------------------------------------------------------

def ic_calc(cx, cy):
    x0 = cx - 15
    y0 = cy - 20
    box(x0, y0, x0 + 30, y0 + 40, (60, 70, 90))
    box(x0 + 1, y0 + 1, x0 + 29, y0 + 39, (60, 70, 90))
    box(x0 + 4, y0 + 4, x0 + 26, y0 + 13, GREEN)
    for r in range(3):
        for c in range(3):
            kx = x0 + 5 + c * 8
            ky = y0 + 18 + r * 7
            rect(kx, ky, kx + 4, ky + 3, ORANGE if (r == 2 and c == 2) else GREY)

def ic_cas(cx, cy):
    box(cx - 21, cy - 16, cx + 21, cy + 16, PURPLE)
    box(cx - 20, cy - 15, cx + 20, cy + 15, PURPLE)
    ctext(cx, cy - 14, 'd', PURPLE, 'medium')
    hline(cx - 11, cx + 11, cy + 1, PURPLE)
    ctext(cx, cy + 2, 'dx', PURPLE, 'medium')

def ic_graph(cx, cy):
    vline(cx - 16, cy - 19, cy + 19, GREY)
    hline(cx - 20, cx + 20, cy + 12, GREY)
    px = None
    x = -18
    while x <= 18:
        y = cy + 12 - (324 - x * x) * 30 // 324 + 6
        if px is not None:
            line(cx + px[0], px[1], cx + x, y, RED)
            line(cx + px[0], px[1] + 1, cx + x, y + 1, RED)
        px = (x, y)
        x += 3

def ic_solve(cx, cy):
    box(cx - 21, cy - 14, cx + 21, cy + 14, TEAL)
    box(cx - 20, cy - 13, cx + 20, cy + 13, TEAL)
    ctext(cx, cy - 8, 'x=?', TEAL, 'medium')

def ic_pi(cx, cy):
    rect(cx - 17, cy - 15, cx + 17, cy - 11, ACC)
    rect(cx - 10, cy - 11, cx - 6, cy + 16, ACC)
    rect(cx + 5, cy - 11, cx + 9, cy + 12, ACC)
    rect(cx + 9, cy + 12, cx + 13, cy + 16, ACC)

def ic_argand(cx, cy):
    hline(cx - 20, cx + 20, cy, GREY)
    vline(cx, cy - 20, cy + 20, GREY)
    disc(cx, cy, 15, GREEN, False)
    disc(cx, cy, 14, GREEN, False)
    line(cx, cy, cx + 10, cy - 11, GREEN)
    line(cx + 1, cy, cx + 11, cy - 11, GREEN)
    disc(cx + 10, cy - 11, 3, GREEN, True)
    draw_string(cx + 12, cy + 2, 'z', GREEN, 'medium')

def ic_book(cx, cy):
    box(cx - 16, cy - 19, cx + 16, cy + 19, ORANGE)
    box(cx - 15, cy - 18, cx + 15, cy + 18, ORANGE)
    vline(cx - 10, cy - 18, cy + 18, ORANGE)
    for y in (cy - 10, cy - 4, cy + 2, cy + 8):
        hline(cx - 6, cx + 10, y, (190, 140, 80))

def ic_angle(cx, cy):
    ox = cx - 16
    oy = cy + 14
    hline(ox, ox + 34, oy, BLACK)
    hline(ox, ox + 34, oy + 1, BLACK)
    line(ox, oy, ox + 26, oy - 26, BLACK)
    line(ox + 1, oy, ox + 27, oy - 26, BLACK)
    x = 0
    while x <= 18:
        y = 18 * 18 - x * x
        r = 0
        while r * r < y:
            r += 1
        set_pixel(ox + x, oy - r, ORANGE)
        set_pixel(ox + r, oy - x, ORANGE)
        x += 1
    ctext(cx + 6, cy - 22, 'DEG' if DEG else 'RAD', ORANGE, 'small')

def _fields(spec):
    import casutil
    names = []
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind != 'n' and kind != 'e' and kind != 'q':
            return None
        names.append(name)
    return names if len(names) > 1 else None

def _field_at(ed):
    # which comma-separated field the caret is in
    row = ed.root
    end = ed.stack[0][1] if ed.stack else ed.i
    n = 0
    i = 0
    while i < end and i < len(row):
        if row[i] == ',':
            n += 1
        i += 1
    return n

def _chips(ed, names, y):
    # (x, y, text, colour) for the field values under the editor
    import nat
    out = []
    if not names:
        return out
    parts = _split(nat.lin(ed.root)) if ed.root else []
    cur = _field_at(ed)
    i = 0
    x = 8
    while i < len(names) and y < BOT:
        s = clip(names[i] + ' = ' + (parts[i] if i < len(parts) else ''), 118, 'medium')
        out.append((x, y, s, ACC if i == cur else (INK if i < len(parts) else LGREY)))
        x += 124
        i += 1
        if i % 3 == 0:
            x = 8
            y += 20
    return out

def _input_base(ed):
    import nat
    w, a, d = nat.measure(ed.root, 0)
    return TOP + 8 + a, a, d

def _draw_input(label, spec, ed, shift, alpha, names):
    import nat
    clear_screen()
    status(label, shift, alpha)
    base, a, d = _input_base(ed)
    if not ed.root:
        # faint hint of what goes here, gone once typing starts
        hint = (spec + ',').replace('=,', ',')[:-1]
        draw_string(16, base - 13, clip(hint.replace(',', ', '), 356, 'medium'), LGREY, 'medium')
    nat.draw(ed, ed.root, 8, base, 368)
    chips = _chips(ed, names, BOT - 18 - 20 * ((len(names) - 1) // 3) if names else 0)
    for x, y, t, c in chips:
        draw_string(x, y, t, c, 'medium')
    _INP['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d, chips)
    show_screen()

def _input_fast(ed, names):
    # only the typed row and changed field values are repainted
    import nat
    sh = _INP.get('shown')
    if sh is None:
        return False
    row, base, dx, caret, a0, d0, chips = sh
    w, a, d = nat.measure(ed.root, 0)
    if a != a0 or d != d0 or not row or not ed.root:
        return False
    nat.undraw(row, 8, base, dx, caret, WHITE)
    new = _chips(ed, names, chips[0][1] if chips else 0)
    i = 0
    while i < len(new):
        if i >= len(chips) or chips[i] != new[i]:
            if i < len(chips):
                x, y, t, c = chips[i]
                draw_string(x, y, t, WHITE, 'medium')
            x, y, t, c = new[i]
            draw_string(x, y, t, c, 'medium')
        i += 1
    nat.draw(ed, ed.root, 8, base, 368)
    _INP['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d, new)
    status_mode(False, False)
    show_screen()
    return True

def _split(text):
    import casutil
    return casutil.split_values(text)

def input_line(label, spec, last=''):
    import nat
    key = label + '|' + spec
    row = _LAST.get(key)
    if row is not None:
        ed = nat.Ed(nat.copy(row))
    else:
        ed = nat.Ed(nat.from_text(last) if last else [])
    shift = False
    alpha = False
    names = _fields(spec)
    dirty = True
    quick = False
    while True:
        if dirty and not (quick and _input_fast(ed, names)):
            _draw_input(label, spec, ed, shift, alpha, names)
        dirty = True
        quick = False
        k = next_key()
        if k == SHIFT or k == ALPHA:
            if k == SHIFT:
                shift = not shift
                alpha = False
            else:
                alpha = not alpha
                shift = False
            status_mode(shift, alpha)
            show_screen()
            dirty = False
            continue
        if k == EXITK:
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return None
        if k == SETTINGS:
            settings()
            continue
        if k == OK or k == EXE:
            if not ed.root:
                dirty = False
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            _LAST[key] = nat.copy(ed.root)
            wait_release()
            return nat.lin(ed.root)
        quick = k != MENU and k != TOOLS
        if not edit_key(ed, k, shift, alpha) and not shift and not alpha:
            dirty = False
            continue
        shift = False
        alpha = False

MODES = (None, 'working', 'full')

def _draw_result(title, sub, blocks, top, mode, more):
    clear_screen()
    status(title, False, False, MODES[mode] if more else '')
    y = TOP + 3
    i = top
    n = len(blocks)
    while i < n:
        blk = blocks[i]
        kind = blk[0]
        h = blk[3]
        if y + h > BOT + 2:
            break
        play(blk, 0, y, INK if kind == 'a' else (GREY if kind == 'w' else RED))
        y += h
        i += 1
    if top > 0 or i < n:
        # scroll position, right edge
        span = BOT - TOP
        t0 = TOP + span * top // n
        t1 = TOP + span * i // n
        vline(W - 3, TOP, BOT, BAR)
        vline(W - 2, TOP, BOT, BAR)
        vline(W - 3, t0, t1, ACC)
        vline(W - 2, t0, t1, ACC)
    show_screen()
    return i

def result(label, text, lines_fn):
    # lines_fn: callable giving the lines (called again for full precision),
    # or a plain list for static content. Each form is worked out once.
    import casutil
    mode = 0
    top = 0
    more = not isinstance(lines_fn, list)
    raw = {}
    blocks = None
    try:
        while True:
            if blocks is None:
                full = mode == 2
                casutil.FULL = full
                if full not in raw:
                    if more:
                        busy()
                    raw[full] = lines_fn if not more else lines_fn()
                blocks = _blocks(raw[full], mode if more else 1)
                if not blocks:
                    blocks = [('!', [(8, 1, 'nothing to show', 'medium')], (), 20, None)]
            if top >= len(blocks):
                top = len(blocks) - 1
            end = _draw_result(label, text, blocks, top, mode, more)
            while True:
                k = next_key()
                if k == EXITK or k == OK or k == EXE:
                    wait_release()
                    return
                if k == DOWN and end < len(blocks):
                    top += 1
                elif k == UP and top > 0:
                    top -= 1
                elif k == PAGEDOWN and end < len(blocks):
                    top = end
                elif k == PAGEUP and top > 0:
                    top = top - 7 if top > 7 else 0
                elif k == FORMAT and more:
                    mode = (mode + 1) % 3
                    top = 0
                    blocks = None
                else:
                    continue
                break
    finally:
        casutil.FULL = False

def show_lines(title, lines):
    result(title, '', lines)

def _calc_lines(tree, val):
    import caseng
    import casutil
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

def _forms(text):
    # every way to show the answer; FORMAT cycles through them
    import caslex
    import caseng
    import casutil
    try:
        tree = caslex.parse(text)
    except ValueError as e:
        return [('!', str(e))]
    if tree is None:
        return [('!', 'cannot read that')]
    tree = _sub_ans(tree, ANS[0])
    forms = []
    try:
        simp = caseng.simplify(tree)
    except Exception:
        simp = None
    if simp is not None and caseng.vars_in(simp):
        return [('m', simp)]
    try:
        val = casutil.ev(tree)
    except ValueError as e:
        return [('!', str(e))]
    if isinstance(val, float) and (val > 1.7e308 or val < -1.7e308):
        return [('!', 'too large')]
    caseng.ANS = val
    ANS[0] = simp if simp is not None else ('n', val)
    seen = []
    v = casutil.clean(val)
    if simp is not None and isinstance(v, float) and caseng._ratval(simp) is not None \
            and len(caseng.tostr(simp)) > 12:
        # a long exact fraction: the plain number reads better first
        s = casutil._sf(v, 10)
        forms.append(('a', s))
        seen.append(s)
    if simp is not None and len(caseng.tostr(simp)) <= 60:
        ex = caseng.tostr(simp)
        # re-read the printed form so a complex/rational constant typesets as fractions
        t2 = caslex.parse(ex) if simp[0] == 'n' else None
        forms.append(('m', t2 if t2 is not None else simp))
        seen.append(ex)
        if 'sin' in ex or 'cos' in ex or 'tan' in ex:
            # cos(pi/12)^6 as surds: (15sqrt(3)+26)/64
            try:
                import casalg
                ts = casalg.trigsurd(simp)
            except Exception:
                ts = None
            if ts is not None and len(caseng.tostr(ts)) <= 60 and caseng.tostr(ts) not in seen:
                forms.append(('m', ts))
                seen.append(caseng.tostr(ts))
    s = casutil.fmt(val)
    if s not in seen:
        forms.append(('a', s))
        seen.append(s)
    v = casutil.clean(val)
    if isinstance(v, float):
        s = casutil._sf(v, 10)
        if s not in seen:
            forms.append(('a', s))
    elif isinstance(v, complex):
        forms.append(('a', 'r=' + casutil.fmt(caseng._cabs(v)) + '  arg=' + casutil.fmt(caseng._carg(v))))
    return forms

def _sub_ans(t, r):
    if t == ('v', 'ans'):
        return r
    if isinstance(t, tuple) and len(t) > 1 and t[0] != 'n' and t[0] != 'v':
        return (t[0],) + tuple([_sub_ans(c, r) for c in t[1:]])
    return t

def _ans_box(form):
    import casrender
    kind, p = form
    if kind == 'm':
        b = casrender.build(p, 0)
        w, a, d = casrender.measure(b)
        if w <= 372:
            return ('m', b, w, a, d)
        import caseng
        p = caseng.tostr(p)
    s = clip(p, 372, 'medium')
    return (kind, s, text_w(s, 'medium'), 13, 4)

def _draw_calc(ed, shift, alpha):
    import nat
    import casrender
    clear_screen()
    status('Calculate', shift, alpha)
    fresh = CALC.get('fresh')
    editing = CALC.get('editing')
    hist = HIST if (fresh or not editing) else HIST[:-1]
    # lay out from the newest entry upwards; only what fits is measured, and a
    # history entry's layout is worked out once and kept with it
    blocks = []
    total = 0
    if not fresh:
        w, a, d = nat.measure(ed.root, 0)
        blocks.append((ed.root, None, ed, None, a, d, a + d + 4))
        total = a + d + 4
    j = len(hist) - 1
    while j >= 0:
        e = hist[j]
        if len(e) < 4:
            e.append({})
        c = e[3]
        lay = c.get(e[2])
        if lay is None:
            forms = e[1]
            note = None
            ans = _ans_box(forms[e[2]])
            w, a, d = nat.measure(e[0], 0)
            h = a + d + 4 + ans[3] + ans[4] + 4 + (18 if note else 0)
            lay = (ans, note, a, d, h)
            c[e[2]] = lay
        ans, note, a, d, h = lay
        if blocks and total + h > BOT - TOP - 2:
            break
        blocks.insert(0, (e[0], ans, None, note, a, d, h))
        total += h
        j -= 1
    y = TOP + 2
    if total > BOT - TOP - 2:
        y = BOT - total
    n = 0
    CALC['shown'] = None
    for row, ans, e, note, a, d, h in blocks:
        last = n == len(blocks) - 1
        if n:
            for x in range(6, 378, 3):
                set_pixel(x, y - 2, LGREY)
        nat.draw(e, row, 6, y + a, 370, BLACK if (e is not None or last) else GREY)
        if e is not None:
            CALC['shown'] = (nat.copy(row), y + a, nat.LAST[0], nat.LAST[1], a, d)
        if ans is not None:
            kind, p, w, aa, ad = ans
            yb = y + a + d + 4 + aa
            if kind == 'm':
                casrender.COLOR = BLACK if last else GREY
                casrender.draw(p, 378 - w, yb)
            else:
                draw_string(378 - w, yb - 13, p, RED if kind == '!' else (BLACK if last else GREY), 'medium')
            if note:
                draw_string(378 - text_w(note, 'medium'), yb + ad + 2, note, GREY, 'medium')
        y += h
        n += 1
    casrender._MCACHE.clear()
    show_screen()

def _calc_fast(ed):
    # a key that only changed the line being typed: undraw it, draw it again
    import nat
    sh = CALC.get('shown')
    if sh is None or CALC.get('fresh'):
        return False
    row, base, dx, caret, a0, d0 = sh
    w, a, d = nat.measure(ed.root, 0)
    if a != a0 or d != d0:
        return False
    nat.undraw(row, 6, base, dx, caret, WHITE)
    nat.draw(ed, ed.root, 6, base, 370, BLACK)
    CALC['shown'] = (nat.copy(ed.root), base, nat.LAST[0], nat.LAST[1], a, d)
    status_mode(False, False)
    show_screen()
    return True

def calc_section():
    busy()
    import nat
    ed = CALC.get('ed')
    if ed is None:
        ed = nat.Ed()
        CALC['ed'] = ed
        CALC['pos'] = 0
    shift = False
    alpha = False
    dirty = True
    quick = False
    while True:
        if dirty and not (quick and _calc_fast(ed)):
            _draw_calc(ed, shift, alpha)
        dirty = True
        quick = False
        k = next_key()
        if k == SHIFT or k == ALPHA:
            if k == SHIFT:
                shift = not shift
                alpha = False
            else:
                alpha = not alpha
                shift = False
            status_mode(shift, alpha)
            show_screen()
            dirty = False
            continue
        if k == EXITK:
            wait_release()
            return
        if k == SETTINGS:
            settings()
            continue
        fresh = CALC.get('fresh')
        if k == TOOLS:
            # operations on the line being typed, or on the last one worked out
            row = ed.root if (ed.root and not fresh) else (HIST[-1][0] if HIST else None)
            if row and not nat.empty_hole(row):
                calc_tools(nat.lin(row))
            shift = False
            alpha = False
            continue
        if k == OK or k == EXE:
            if fresh or not ed.root:
                continue
            if nat.empty_hole(ed.root):
                flash('fill in the empty box')
                continue
            busy()
            forms = _forms(nat.lin(ed.root))
            entry = [nat.copy(ed.root), forms, 0]
            if CALC.get('editing') and HIST:
                HIST[-1] = entry
            else:
                HIST.append(entry)
                if len(HIST) > 30:
                    HIST.pop(0)
            CALC['fresh'] = True
            CALC['editing'] = True
            CALC['pos'] = len(HIST)
            continue
        if k == FORMAT and fresh and HIST:
            e = HIST[-1]
            e[2] = (e[2] + 1) % len(e[1])
            continue
        if fresh:
            if k in (LEFT, RIGHT, DEL, LINESTART, LINEEND):
                CALC['fresh'] = False
                if k == DEL and not shift:
                    ed.end()
                    ed.dele()
                elif k == DEL:
                    ed.clear()
                    CALC['editing'] = False
                elif k == LEFT or k == LINEEND:
                    ed.end()
                    if k == LEFT:
                        ed.left()
                else:
                    ed.home()
                shift = False
                continue
            if k != UP and k != DOWN and k != MENU:
                start = ['ans'] if nat.starts_op(k, shift, alpha) else []
                ed.set(start)
                if edit_key(ed, k, shift, alpha):
                    CALC['fresh'] = False
                    CALC['editing'] = False
                shift = False
                alpha = False
                continue
            if k == MENU:
                ed.set([])
                CALC['fresh'] = False
                CALC['editing'] = False
        if k == UP or k == DOWN:
            if not fresh and ed.vert(k == UP):
                quick = True
                continue
            if not fresh and ed.root:
                continue    # never swap out a line that is being typed
            pos = CALC.get('pos', len(HIST))
            pos = pos - 1 if k == UP else pos + 1
            if 0 <= pos < len(HIST):
                CALC['pos'] = pos
                ed.set(nat.copy(HIST[pos][0]))
                CALC['fresh'] = False
                CALC['editing'] = False
            continue
        quick = k != MENU and k != TOOLS
        if edit_key(ed, k, shift, alpha):
            CALC['fresh'] = False
        shift = False
        alpha = False

# ---- CAS ---------------------------------------------------------------------------

def _tidy(t):
    import cascalc
    return cascalc.tidy(t)

def _cas_op(op, tree, s):
    import caseng
    import cascalc
    import caspoly
    import casutil
    if op == 0:
        return [('m', _tidy(caseng.diff(tree)))]
    if op == 1:
        return [('m', _tidy(caseng.diff(_tidy(caseng.diff(tree)))))]
    if op == 2:
        r = cascalc.integ(tree)
        if r is None:
            return [('!', 'no elementary integral; use definite')]
        return [('m', _tidy(r)), '+ c']
    if op == 3:
        v = casutil.ask('a,b', 'limits')
        if v is None:
            return None
        lo = ('n', v[0])
        hi = ('n', v[1])
        try:
            ex = cascalc.defint_exact(tree, lo, hi)
        except ValueError as e:
            return [('!', str(e))]
        except Exception:
            ex = None
        if ex is not None:
            out = [('m', ex)]
            lf = _lnform(ex)
            if lf is not None:
                out.append(('m', lf))
            try:
                d = casutil.ev(ex)
                if not isinstance(d, complex):
                    if casutil.fmt(d) == caseng.tostr(ex).replace('*', ''):
                        out.append(('w', 'integral = ' + casutil.fmt(d)))
                    out.append('integral = ' + casutil.sf3(d))
            except ValueError:
                pass
            return out + [('w', 'exact: F(b) - F(a)'),
                          ('w', 'from ' + casutil.fmt(v[0]) + ' to ' + casutil.fmt(v[1]))]
        r = cascalc.defint(tree, v[0], v[1], casutil.DEG)
        if r is None:
            return [('!', 'cannot evaluate over that range')]
        return ['integral = ' + casutil.fmt(r),
                ('!', 'numeric (Simpson) - no exact antiderivative'),
                ('w', 'from ' + casutil.fmt(v[0]) + ' to ' + casutil.fmt(v[1]))]
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
        roots = cascalc.solve(d1, wide=True)
        if not roots:
            return [('!', 'no stationary points found'), ('w', cascalc.range_str())]
        d2 = _tidy(caseng.diff(d1))
        lines = []
        for r in roots:
            y = casutil.ev(tree, r)
            c = casutil.evx(d2, r)
            kind = 'min' if (c is not None and c > 1e-9) else ('max' if (c is not None and c < -1e-9) else 'inflection?')
            lines.append('(' + casutil.fmt(r) + ', ' + casutil.fmt(y) + ')  ' + kind)
        lines.append(('mw', d1))
        lines.append(('w', cascalc.range_str()))
        return lines
    if op == 6:
        return [('m', _tidy(tree))]
    if op == 7:
        import casalg
        e = caspoly.expand(tree)
        p = casalg.expairs(e)
        return [('m', e)] if p == e else [('m', e), ('m', p), ('w', 'e^(ix) + e^(-ix) = 2cos x')]
    if op == 8:
        r = caspoly.factor(tree)
        if r is None:
            import cassolve
            r = cassolve.factor_sym(tree, 'x')
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
            top, fac = caspoly.intfactor(top, fac, power)
            den = fac
            if power > 1:
                den = ('^', fac, ('n', power))
            r = caseng._ratval(top)
            if r is not None and r[1] > 1:
                # 1/(8(3x+4)), not 1/8/(3x+4)
                top = ('n', r[0])
                den = ('*', ('n', r[1]), den)
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
        roots = cascalc.solve(target, deg=casutil.DEG, wide=True)
        if not roots:
            return [('!', 'no real roots found'), ('w', cascalc.range_str())]
        return ['x = ' + ', '.join([casutil.fmt(r) for r in roots]), ('w', cascalc.range_str())]
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
    return _cas_op2(op, tree, s)

def _lnform(ex):
    # the log form of an exact constant when it differs: 2acosh(2) - sqrt3 ->
    # 2ln(2+sqrt3) - sqrt3, ln2 + ln5/2 - ln10/2 -> ln(2)/2
    import caseng
    import casalg
    s = caseng.tostr(ex)
    if 'ln' not in s and 'asinh' not in s and 'acosh' not in s and 'atanh' not in s:
        return None
    try:
        lf = casalg.lnform(ex)
    except Exception:
        return None
    return None if caseng.tostr(lf) == s else lf

def _roots_lines(roots, exact):
    import caseng
    lines = ['x = ' + caseng.tostr(r) for r in roots]
    for r in roots:
        lines.append(('mw', r))
    if not exact:
        lines.append(('!', 'numeric roots - no exact form found'))
    return lines

def _cas_op2(op, tree, s):
    import caseng
    import casutil
    import casalg
    import cassolve
    if op == 15:
        return [('m', casalg.expand(tree)), ('w', 'compound angles and log laws used')]
    if op == 16:
        r = casalg.csq_lines(tree)
        if r is None:
            return [('!', 'not a quadratic in x: a x^2 + b x + c, letters allowed in a, b, c')]
        return r
    if op == 17:
        r = casalg.rationalise(tree)
        if r is None:
            return [('!', 'nothing to rationalise')]
        return [('m', r), ('w', 'multiplied top and bottom by the conjugate')]
    if op == 18:
        r = casalg.single_fraction(tree)
        if r is None:
            return [('!', 'cannot write as one fraction')]
        return [('m', r), ('w', 'over a common denominator, cancelled')]
    if op == 19:
        roots = cassolve.solve_exact(tree, 'x')
        if roots:
            return _roots_lines(roots, True)
        roots, exact = cassolve.solve_any(tree, 'x', casutil.DEG)
        import cascalc
        if not roots:
            return [('!', 'no solutions found'), ('w', cascalc.range_str())]
        return _roots_lines(roots, exact) + [('w', cascalc.range_str())]
    if op == 20:
        g = cassolve.general_trig(tree, 'x', 'n')
        if not g:
            return [('!', 'not a trig equation in one angle')]
        lines = ['x = ' + caseng.tostr(r) for r in g]
        lines.append(('w', 'n is any integer'))
        return lines
    if op == 21:
        v = casutil.ask('terms', 'how many terms')
        if v is None:
            return None
        r = casalg.maclaurin(tree, 'x', int(v[0]))
        if r is None:
            return [('!', 'no Maclaurin series at x = 0')]
        return [('m', r), ('w', 'sum f(k)(0) x^k / k!')]
    if op == 22:
        v = casutil.ask('a(x)', 'x -> (or inf)')
        if v is None:
            return None
        a = v[0]
        if a == ('v', 'inf'):
            r = casalg.limit(tree, 'x', None, 1)
        elif a == ('neg', ('v', 'inf')):
            r = casalg.limit(tree, 'x', None, -1)
        else:
            r = casalg.limit(tree, 'x', a)
        if r is None:
            return [('!', 'limit not found')]
        return [('m', r), ('w', 'limit as x -> ' + caseng.tostr(a))]
    if op == 23:
        v = casutil.ask('a(x)', 'x =')
        if v is None:
            return None
        return [('m', casalg.subst_exact(tree, 'x', v[0])),
                ('w', 'x = ' + caseng.tostr(v[0]))]
    if op == 24:
        r = casalg.rearrange(tree, 'x', 'y')
        if r is not None:
            return [('m', r), ('w', 'from y = f(x)')]
        br = cassolve.solve_exact(('-', tree, ('v', 'y')), 'x')
        if br:
            return [('m', b) for b in br] + [('w', 'from y = f(x), both branches')]
        return [('!', 'cannot make x the subject')]
    return None

def _read(label, spec, name=None):
    # editor -> (text, tree); None when the user backs out
    while True:
        s = input_line(label, spec, '')
        if s is None:
            return None
        try:
            s, tree = _parse_eq(s, name)
        except ValueError as e:
            flash(str(e))
            continue
        if tree is None:
            flash('cannot read that')
            continue
        return s, tree

def _parse_eq(s, name=None):
    # 'l = r' -> l - r, the form the solvers take; 'y = f' -> f for a name
    import caslex
    import casutil
    s = casutil.eq_text(s, name, name is None)
    return s, caslex.parse(s)

_TOOLSEL = [0]

# Further-only entries of the old screens, hidden while FURTHER_ON is False
OPS_FURTHER = ('series (Maclaurin)',)
NOTES_FURTHER = ('Core Pure Y420', 'Stats Y422', 'Extra Pure Y435')
# booklet pages for Further only (the A-level Maths booklet has none of them)
FB_FURTHER = ('Complex numbers', 'Matrix transformations', 'Summations',
              'Maclaurin series', 'Vectors', 'Area of a sector', 'Hyperbolic functions',
              'Conics', 'Further num. integ.', 'Numerical solution ODE', 'Arc length',
              'Surface area of revol.', 'Centres of mass', 'Contingency tables')

def calc_tools(text):
    try:
        s, tree = _parse_eq(text)
    except ValueError as e:
        flash(str(e))
        return
    if tree is None:
        flash('cannot read that')
        return
    while True:
        op = pick_shown('Tools', CAS_OPS, OPS_FURTHER, _TOOLSEL[0])
        if op < 0:
            return
        _TOOLSEL[0] = op
        _run_op(op, tree, s)

def _run_op(op, tree, s):
    # Busy first: an op can take seconds, and the menu left showing looked hung
    busy()
    try:
        lines = _cas_op(op, tree, s)
    except ValueError as e:
        lines = [('!', str(e))]
    except Exception as e:
        lines = [('!', errtext(e))]
    if lines is not None:
        result(CAS_OPS[op], 'f(x) = ' + s, lines)

def cas_section():
    busy()
    op = 0
    while True:
        got = _read('CAS', 'f(x)')
        if got is None:
            return
        s, tree = got
        while True:
            op = pick_shown('f(x) = ' + s, CAS_OPS, OPS_FURTHER, op)
            if op < 0:
                op = 0
                break
            _run_op(op, tree, s)

def solve_section():
    busy()
    while True:
        got = _read('Solve', 'equation in x (= allowed)')
        if got is None:
            return
        _run_op(19, got[1], got[0])

def graph_section():
    busy()
    import plot
    while True:
        got = _read('Graph', 'y = f(x)', 'f(x)')
        if got is None:
            return
        plot.run([got[1]], -6.0, 6.0, 'y', 'y = ' + got[0])

def notes_section():
    idx = shown([p[0] for p in NOTE_PAPERS], NOTES_FURTHER)
    labels = [NOTE_PAPERS[i][0] for i in idx]
    while True:
        sel = remembered('Notes', labels)
        if sel < 0:
            return
        name, mods = NOTE_PAPERS[idx[sel]]
        if mods:
            busy()
            import notesui
            notesui.paper(name)
        else:
            _booklet(name)

def _booklet(name):
    busy()
    import tn_fb
    import notesui
    idx = shown(tn_fb.T, FB_FURTHER)
    labels = [tn_fb.T[i] for i in idx]
    while True:
        sel = remembered(name, labels)
        if sel < 0:
            return
        notesui.show(labels[sel], tn_fb.N[idx[sel]])

HOME_TILES = [
    ('Calculate', ic_calc), ('CAS', ic_cas), ('Graph', ic_graph), ('Solve', ic_solve),
    ('Maths', ic_pi), ('Further', ic_argand), ('Notes', ic_book), ('Settings', ic_angle),
]

def classic():
    # the old home grid, for More > All tools; HOME goes to the new home.
    # The Further tile only with the launcher's FURTHER switch on
    tiles = [t for t in HOME_TILES if casui.FURTHER_ON or t[0] != 'Further']
    sel = 0
    while True:
        sel = grid('All tools', tiles, sel)
        if sel < 0:
            return
        name = tiles[sel][0]
        if name == 'Calculate':
            calc_section()
        elif name == 'CAS':
            cas_section()
        elif name == 'Graph':
            graph_section()
        elif name == 'Solve':
            solve_section()
        elif name == 'Maths':
            qual_section('Maths', MATHS)
        elif name == 'Further':
            paper_section('Further', FURTHER)
        elif name == 'Notes':
            notes_section()
        elif name == 'Settings':
            settings()

