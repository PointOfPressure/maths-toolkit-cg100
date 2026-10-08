# Measures the width of every character in the small and medium fonts and
# saves them to fontcal.txt. About a minute; nothing to press until the end.
from casioplot import *

BLK = (0, 0, 0)
MID = {'small': 5, 'medium': 7}
START = {'small': 140, 'medium': 200}

def ink(x, y):
    p = get_pixel(x, y)
    return p is not None and p[0] < 160

def bar_x(s, size, start):
    # draw s then '|', return the x of the bar (rightmost ink on the middle row)
    clear_screen()
    draw_string(0, 0, s + '|', BLK, size)
    y = MID[size]
    x = start
    while x >= 0:
        if ink(x, y):
            return x
        x -= 1
    return -1

def note(s, y):
    draw_string(4, y, s, BLK, 'medium')
    show_screen()

def main():
    wrote = 'no'
    try:
        f = open('fontcal.txt', 'w')
        f.write('test\n')
        f.close()
        wrote = 'yes'
    except Exception as e:
        wrote = 'no: ' + str(e)[:20]
    out = ['write ' + wrote]
    for size in ('medium', 'small'):
        off = bar_x('', size, 30)
        codes = ''
        o = 32
        while o < 127:
            c = chr(o)
            x = bar_x(c * 10, size, START[size])
            w = (x - off + 5) // 10 if x >= 0 and off >= 0 else 0
            if w < 0:
                w = 0
            codes += chr(48 + w) if w < 75 else '?'
            o += 1
            if o % 8 == 0:
                clear_screen()
                note('measuring ' + size + ' ' + str(o - 32) + '/95', 80)
        out.append(size + ' ' + codes)
    try:
        f = open('fontcal.txt', 'w')
        f.write('\n'.join(out) + '\n')
        f.close()
    except Exception:
        pass
    clear_screen()
    y = 2
    for line in out:
        while line:
            draw_string(2, y, line[:46], BLK, 'small')
            line = line[46:]
            y += 13
    draw_string(2, 178, 'done - plug in, or photo this', BLK, 'small')
    show_screen()
    k = getkey()
    while k != 22:
        k = getkey()

main()
