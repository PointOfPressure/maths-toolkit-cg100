# Settings page (mockup H). The defaults come from the launch script; a change
# here lasts until the program ends. Working is not a setting: the answer page
# has its own key for it.
from casioplot import draw_string, show_screen, clear_screen
import casui
from casui import W, INK, ACC, GREY, WHITE, LGREY, UP, DOWN, LEFT, RIGHT, OK, EXE, EXITK, SETTINGS

ROWS = (
    ('Angle', 'angle', ('rad', 'deg'), ('Radians', 'Degrees')),
    ('Answers', 'answers', ('exact', 'decimal', 'both'), ('Exact', 'Decimal', 'Exact + decimal')),
    ('Decimals', 'decimals', ('3sf', '4sf', '5sf', '6sf', '1dp', '2dp', '3dp', '4dp'),
     ('3 s.f.', '4 s.f.', '5 s.f.', '6 s.f.', '1 d.p.', '2 d.p.', '3 d.p.', '4 d.p.')),
    ('Complex', 'complex', ('a+bi', 'polar'), ('a + bi', 'r, theta')),
    ('Sleep after', 'sleep', (5, 10, 15, 20, 30, 60, 0), ('5 min', '10 min', '15 min', '20 min',
                                                         '30 min', '60 min', '10 hours')),
    ('Key repeat', 'repeat', ('off', 'slow', 'normal', 'fast'), ('Off', 'Slow', 'Normal', 'Fast')),
    ('Further Maths', 'further', (False, True), ('off in launch script', 'on in launch script')),
)
Y0 = 26
DY = 23

def _shown(i):
    name, key, vals, labels = ROWS[i]
    v = casui.SET[key]
    return labels[vals.index(v)] if v in vals else str(v)

def _row(i, on, val=None):
    y = Y0 + i * DY
    c = ACC if on else WHITE
    casui.box(2, y - 2, W - 3, y + 19, c)
    s = _shown(i) if val is None else val
    if not on:
        # off: the blue value goes first, so no blue edge is left
        draw_string(W - 12 - casui.text_w(s, 'medium'), y, s, WHITE, 'medium')
    draw_string(10, y, ROWS[i][0], INK, 'medium')
    draw_string(W - 12 - casui.text_w(s, 'medium'), y, s,
                ACC if on else GREY, 'medium')

def _draw(sel):
    clear_screen()
    casui.status('Settings')
    for i in range(len(ROWS)):
        _row(i, i == sel)
    show_screen()

def page():
    sel = 1
    _draw(sel)
    while True:
        k = casui.next_key()
        old = sel
        if k == EXITK or k == SETTINGS:
            casui.wait_release()
            return
        if k == UP:
            sel = (sel - 1) % len(ROWS)
        elif k == DOWN:
            sel = (sel + 1) % len(ROWS)
        elif k in (LEFT, RIGHT, OK, EXE):
            name, key, vals, labels = ROWS[sel]
            if key == 'further':
                continue
            v = casui.SET[key]
            i = vals.index(v) if v in vals else 0
            i = (i - 1) % len(vals) if k == LEFT else (i + 1) % len(vals)
            was = _shown(sel)
            y = Y0 + sel * DY
            draw_string(W - 12 - casui.text_w(was, 'medium'), y, was, WHITE, 'medium')
            casui.SET[key] = vals[i]
            casui.configure()
            _row(sel, True)
            if key == 'angle':
                casui.status_mode(False, False)
            show_screen()
            continue
        else:
            continue
        if sel != old:
            _row(old, False)
            _row(sel, True)
            show_screen()
