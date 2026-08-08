# keyprobe.py - one-off hardware probe: report the getkey code of any key.
#
# Casio documents the scheme (the code is the row number followed by the column
# number) but publishes the full table only inside the fx-CG100 manual's
# casioplot section, so the toolkit's map in casui.py was decoded by hand on
# real hardware. This script is how you check it: press a key, read its code,
# and see what the toolkit currently believes that key is.
#
# Press every key in turn to audit the whole map. Anything reported as "not
# mapped" is a free code you can bind. [ON] and [AC] are assigned no key code
# by Casio at all, so getkey cannot see them - that is why the toolkit quits on
# EXIT rather than AC.
#
# Not part of the toolkit; a sibling of calib_screen.py and fontmetrics.py.
from casioplot import *
import casui

BLACK = (20, 20, 25)
GREY = (120, 120, 130)
ACC = (40, 120, 220)
RED = (205, 60, 60)

NAMED = [
    ("UP", casui.UP), ("DOWN", casui.DOWN), ("LEFT", casui.LEFT),
    ("RIGHT", casui.RIGHT), ("OK", casui.OK), ("EXE", casui.EXE),
    ("BACK/EXIT", casui.EXITK), ("DEL", casui.DEL), ("SHIFT", casui.SHIFT),
    ("CATALOG/picker", casui.MENU), ("ALPHA", casui.ALPHA),
    ("HOME", casui.HOME), ("line start", casui.LINESTART),
    ("line end", casui.LINEEND), ("page up", casui.PAGEUP),
    ("page down", casui.PAGEDOWN), ("VARIABLE", casui.VARIABLE),
    ("TOOLS", casui.TOOLS), ("SETTINGS", casui.SETTINGS),
    ("FORMAT", casui.FORMAT),
]

def roles(k):
    out = []
    for name, code in NAMED:
        if code == k:
            out.append("navigation: " + name)
    u = casui.UNSHIFT.get(k, None)
    if u is not None:
        out.append("plain  -> " + u)
    s = casui.SHIFTED.get(k, None)
    if s is not None:
        out.append("SHIFT  -> " + s)
    a = casui.ALPHADICT.get(k, None)
    if a is not None:
        out.append("ALPHA  -> " + a)
    d = casui.DIGITS.get(k, None)
    if d is not None:
        out.append("menu jump -> " + str(d))
    return out

def show(k, count):
    clear_screen()
    draw_string(6, 4, "KEY PROBE", ACC, "medium")
    draw_string(300, 8, str(count) + " keys", GREY, "small")
    draw_string(6, 34, "code = " + str(k), BLACK, "large")
    r = k // 10
    c = k % 10
    draw_string(6, 66, "row " + str(r) + ", column " + str(c), GREY, "medium")
    y = 92
    rs = roles(k)
    if not rs:
        draw_string(6, y, "not mapped - free to use", RED, "medium")
    else:
        for item in rs:
            draw_string(6, y, item, BLACK, "medium")
            y += 18
            if y > 158:
                break
    draw_string(6, 176, "press keys to probe; EXIT twice to stop", GREY, "small")
    show_screen()

def main():
    idle = getkey()
    clear_screen()
    draw_string(6, 4, "KEY PROBE", ACC, "medium")
    draw_string(6, 40, "Press any key to see its", BLACK, "medium")
    draw_string(6, 60, "getkey code and what the", BLACK, "medium")
    draw_string(6, 80, "toolkit maps it to.", BLACK, "medium")
    draw_string(6, 112, "ON and AC have no code and", GREY, "medium")
    draw_string(6, 132, "cannot be read at all.", GREY, "medium")
    draw_string(6, 176, "EXIT twice to stop", GREY, "small")
    show_screen()
    count = 0
    last = None
    while True:
        k = getkey()
        if k == idle:
            continue
        while getkey() != idle:
            pass                      # wait for release
        if k == casui.EXITK and last == casui.EXITK:
            clear_screen()
            draw_string(6, 40, "Probed " + str(count) + " key presses.", BLACK, "medium")
            draw_string(6, 70, "Correct casui.py if any key", GREY, "medium")
            draw_string(6, 90, "reported the wrong role.", GREY, "medium")
            show_screen()
            return
        count += 1
        last = k
        show(k, count)

main()
