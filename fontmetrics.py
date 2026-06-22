# fontmetrics.py - measure the REAL draw_string font sizes on this fx-CG100.
# Draws 10 wide glyphs per font size at the top-left, scans pixels to find the
# true rendered width and height, then reports per-char advance, glyph height,
# and how many characters actually fit across the 384px screen.
# Tell me the three lines it prints.
from casioplot import get_pixel, clear_screen, show_screen, draw_string

WHITE = (255, 255, 255)

def is_black(x, y):
    try:
        p = get_pixel(x, y)
    except:
        return False
    return (p is not None) and (p != WHITE)

def measure(size):
    clear_screen()
    draw_string(0, 0, "WWWWWWWWWW", (0, 0, 0), size)  # 10 wide glyphs, top-left
    # rightmost black column = total text width (scan from the right)
    width = 0
    x = 380
    while x >= 0:
        y = 0
        hit = False
        while y <= 34:
            if is_black(x, y):
                hit = True
                break
            y += 2
        if hit:
            width = x + 1
            break
        x -= 1
    # bottom-most black row = glyph height (scan from the bottom)
    height = 0
    yy = 44
    while yy >= 0:
        x = 0
        hit = False
        while x <= width:
            if is_black(x, yy):
                hit = True
                break
            x += 2
        if hit:
            height = yy + 1
            break
        yy -= 1
    return width, height

rows = []
for sz in ["small", "medium", "large"]:
    w, h = measure(sz)
    adv = w / 10.0
    per = int(384 // adv) if adv > 0 else 0
    rows.append((sz, adv, h, per))

clear_screen()
y = 4
for sz, adv, h, per in rows:
    line = sz[0].upper() + ": w/char=" + str(round(adv, 1)) + " h=" + str(h) + " fit=" + str(per)
    draw_string(2, y, line, (0, 0, 0), "small")
    y += 24
draw_string(2, y + 8, "Tell me these three lines.", (120, 120, 120), "small")
show_screen()
