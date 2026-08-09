from casioplot import set_pixel, get_pixel, clear_screen, show_screen, draw_string

BLACK = (0, 0, 0)

def span(horizontal):
    clear_screen()
    n = 0
    i = 0
    while i < 2000:
        try:
            if horizontal:
                set_pixel(i, 0, BLACK)
                px = get_pixel(i, 0)
            else:
                set_pixel(0, i, BLACK)
                px = get_pixel(0, i)
        except:
            break
        if px != BLACK:
            break
        n = i + 1
        i += 1
    return n

W = span(True)
H = span(False)
clear_screen()
draw_string(8, 8, "Screen detected:", BLACK, "medium")
draw_string(8, 40, "WIDTH  = " + str(W), BLACK, "medium")
draw_string(8, 70, "HEIGHT = " + str(H), BLACK, "medium")
draw_string(8, 108, "Tell me these two numbers.", (110, 110, 110), "small")
show_screen()
