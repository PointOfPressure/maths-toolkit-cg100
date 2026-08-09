from casioplot import get_pixel, clear_screen, show_screen, draw_string

WHITE = (255, 255, 255)

def is_black(x, y):
    try:
        p = get_pixel(x, y)
    except:
        return False
    return (p is not None) and (p != WHITE)

def text_width(s, size):
    clear_screen()
    draw_string(0, 0, s, (0, 0, 0), size)
    x = 383
    while x >= 0:
        y = 0
        while y <= 20:
            if is_black(x, y):
                return x + 1
            y += 2
        x -= 1
    return 0

mi = text_width("iiiiiiiiiiiiiiiiiiii", "medium") / 20.0
mo = text_width("oooooooooooooooooooo", "medium") / 20.0
mm = text_width("mmmmmmmmmmmmmmmmmmmm", "medium") / 20.0
PROSE = "The quick brown fox jumps over a lazy dog."
mp = text_width(PROSE, "medium") / 42.0
sp = text_width(PROSE, "small") / 42.0

clear_screen()
draw_string(2, 4,  "MEDIUM font:", (0, 0, 0), "small")
draw_string(2, 26, "i=" + str(round(mi, 1)) + "  o=" + str(round(mo, 1)) + "  m=" + str(round(mm, 1)), (0, 0, 0), "small")
draw_string(2, 48, "prose avg = " + str(round(mp, 2)), (0, 0, 0), "small")
draw_string(2, 78, "SMALL prose avg = " + str(round(sp, 2)), (0, 0, 0), "small")
draw_string(2, 110, "Send me these numbers.", (120, 120, 120), "small")
show_screen()
