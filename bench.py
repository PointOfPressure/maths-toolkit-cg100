# Stopwatch speed test. Each test waits for EXE, runs, then says DONE.
# Time each one from EXE to DONE (roughly is fine).
from casioplot import *

BLK = (0, 0, 0)

def key():
    k = getkey()
    while k:
        k = getkey()
    while not k:
        k = getkey()
    return k

def screen(lines):
    clear_screen()
    y = 4
    for s in lines:
        draw_string(6, y, s, BLK, 'medium')
        y += 20
    show_screen()

def t_pixels():
    # 2000 single pixels, shown once
    sp = set_pixel
    c = (40, 120, 220)
    i = 0
    while i < 2000:
        sp(100 + i % 100, 100 + i // 100, c)
        i += 1
    show_screen()

def t_text():
    # 10 screens of 20 words
    n = 0
    while n < 10:
        clear_screen()
        y = 0
        while y < 20:
            draw_string(6 + n, y * 9, 'Coordinate geometry', BLK, 'medium')
            y += 1
        show_screen()
        n += 1

def t_show():
    n = 0
    while n < 50:
        show_screen()
        n += 1

def t_keys():
    n = 0
    while n < 1000:
        getkey()
        n += 1

def t_loop():
    i = 0
    while i < 20000:
        i += 1

def t_import():
    import caseng

TESTS = (('A', '2000 pixels', t_pixels), ('B', '10 screens of text', t_text),
         ('C', '50 show_screen', t_show), ('D', '1000 key reads', t_keys),
         ('E', '20000 empty loops', t_loop), ('F', 'load caseng', t_import))

def ink(x, y):
    p = get_pixel(x, y)
    return p is not None and p[0] < 160 and p[2] < 160

def col(x, y0, y1):
    out = []
    y = y0
    while y <= y1:
        if ink(x, y):
            out.append(y)
        y += 1
    return out

def row(y, x0, x1):
    n = 0
    first = -1
    last = -1
    x = x0
    while x <= x1:
        if ink(x, y):
            n += 1
            if first < 0:
                first = x
            last = x
        x += 1
    return (first, last, n)

def probes():
    res = []
    # does text paint a white background over what is there?
    clear_screen()
    set_pixel(105, 108, (255, 0, 0))
    draw_string(100, 100, '  ', BLK, 'medium')
    p = get_pixel(105, 108)
    res.append('opaque ' + str(p))
    for size in ('medium', 'small'):
        # solid block glyph
        clear_screen()
        draw_string(100, 100, '\xe2\x96\x88\xe2\x96\x88', BLK, size)
        c = col(103, 94, 126)
        r = row(108 if size == 'medium' else 104, 96, 140)
        res.append(size + ' block col ' + (str(c[0] - 100) + '..' + str(c[-1] - 100) if c else 'none') + ' row ' + str(r))
        # underscore line
        clear_screen()
        draw_string(100, 100, '_____', BLK, size)
        c = col(104, 94, 126)
        r = row(c[-1], 96, 170) if c else None
        res.append(size + ' _ y ' + str([v - 100 for v in c]) + ' row ' + str(r))
        # digits and lowercase widths: first..last ink on one row
        clear_screen()
        draw_string(100, 100, '0000000000', BLK, size)
        res.append(size + ' 0x10 ' + str(row(105 if size == 'medium' else 103, 96, 260)))
        clear_screen()
        draw_string(100, 100, 'aaaaaaaaaa', BLK, size)
        res.append(size + ' ax10 ' + str(row(108 if size == 'medium' else 105, 96, 260)))
    return res

def main():
    for code, name, fn in TESTS:
        screen(['Test ' + code + ': ' + name, '', 'EXE = start (start stopwatch)'])
        key()
        screen(['Test ' + code + ' running...'])
        fn()
        screen(['Test ' + code + ' DONE', '', 'note the time, EXE for next'])
        key()
    res = probes()
    got = []
    for v in 'abcd':
        try:
            __import__('mpy' + v)
            got.append(v + ' ok')
        except Exception as e:
            got.append(v + ' no')
    clear_screen()
    y = 4
    for s in ['All done. Precompiled: ' + ' '.join(got)] + res:
        draw_string(6, y, s[:46], BLK, 'small')
        y += 14
    draw_string(6, 178, 'photo this, EXIT to quit', BLK, 'small')
    show_screen()
    while key() != 22:
        pass

main()
