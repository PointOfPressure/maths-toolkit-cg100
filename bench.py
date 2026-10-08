# Speed test: about 20 seconds, no input until the results.
# Results also go to bench.txt if the calculator lets Python write files.
from casioplot import *

OUT = []

def say(s):
    OUT.append(s)
    print(s)

def _clock():
    for name in ('time', 'utime'):
        try:
            m = __import__(name)
        except Exception:
            continue
        if hasattr(m, 'ticks_ms'):
            return m.ticks_ms, name + '.ticks_ms'
        if hasattr(m, 'monotonic'):
            return (lambda: int(m.monotonic() * 1000)), name + '.monotonic'
        if hasattr(m, 'time'):
            return (lambda: int(m.time() * 1000)), name + '.time'
    return None, 'none'

CLK, CLKNAME = _clock()

def us(fn, n):
    # microseconds per call
    if CLK is None:
        return -1
    t0 = CLK()
    fn(n)
    return int((CLK() - t0) * 1000.0 / n)

def b_pixel(n):
    sp = set_pixel
    c = (40, 120, 220)
    i = 0
    while i < n:
        sp(i % 384, 100 + (i // 384) % 50, c)
        i += 1

def b_loop(n):
    i = 0
    while i < n:
        i += 1

def b_str(n):
    ds = draw_string
    i = 0
    while i < n:
        ds(10, 60, 'Calculate', (0, 0, 0), 'medium')
        i += 1

def b_strl(n):
    ds = draw_string
    i = 0
    while i < n:
        ds(10, 60, 'Calculate', (0, 0, 0), 'large')
        i += 1

def b_clear(n):
    i = 0
    while i < n:
        clear_screen()
        i += 1

def b_show(n):
    i = 0
    while i < n:
        show_screen()
        i += 1

def b_key(n):
    gk = getkey
    i = 0
    while i < n:
        gk()
        i += 1

def b_getpx(n):
    gp = get_pixel
    i = 0
    while i < n:
        gp(i % 384, 50)
        i += 1

def extent(s, size):
    # draw s at (20, 40), return (width, height, inked pixels)
    clear_screen()
    draw_string(20, 40, s, (0, 0, 0), size)
    x0 = 999; x1 = -1; y0 = 999; y1 = -1; ink = 0
    y = 30
    while y < 90:
        x = 10
        while x < 380:
            p = get_pixel(x, y)
            if p is not None and p[0] < 128:
                ink += 1
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
            x += 1
        y += 1
    if x1 < 0:
        return (0, 0, 0)
    return (x1 - x0 + 1, y1 - y0 + 1, ink, x0 - 20, y0 - 40)

def imp(name):
    if CLK is None:
        __import__(name)
        return -1
    t0 = CLK()
    __import__(name)
    return CLK() - t0

def main():
    clear_screen()
    draw_string(6, 80, 'speed test, wait...', (0, 0, 0), 'medium')
    show_screen()
    say('clock ' + CLKNAME)
    try:
        import gc
        gc.collect()
        say('free ' + str(gc.mem_free() // 1024) + 'k')
    except Exception:
        say('free ?')
    try:
        import sys
        say('py ' + str(sys.implementation) + ' ' + str(sys.version))
    except Exception:
        pass
    say('loop us ' + str(us(b_loop, 20000)))
    say('set_pixel us ' + str(us(b_pixel, 5000)))
    say('get_pixel us ' + str(us(b_getpx, 2000)))
    say('str med us ' + str(us(b_str, 300)))
    say('str large us ' + str(us(b_strl, 300)))
    say('clear us ' + str(us(b_clear, 20)))
    say('show us ' + str(us(b_show, 20)))
    say('getkey us ' + str(us(b_key, 2000)))
    for size in ('small', 'medium', 'large'):
        say(size + ' M10 ' + str(extent('MMMMMMMMMM', size)))
        say(size + ' i10 ' + str(extent('iiiiiiiiii', size)))
        say(size + ' 0x10 ' + str(extent('0000000000', size)))
        say(size + ' Ag ' + str(extent('Ag', size)))
    for ch in ('█', '√', 'π', '²', '▶', '→', '×', '−'):
        say('glyph ' + hex(ord(ch)) + ' ' + str(extent(ch * 3, 'medium')))
    got = []
    for v in 'abcd':
        try:
            __import__('mpy' + v)
            got.append(v)
        except Exception as e:
            got.append(v + ':' + str(e)[:12])
    say('mpy ' + ' '.join(got))
    say('import caslex ms ' + str(imp('caslex')))
    say('import caseng ms ' + str(imp('caseng')))
    say('import casui ms ' + str(imp('casui')))
    try:
        f = open('bench.txt', 'w')
        f.write('\n'.join(OUT) + '\n')
        f.close()
        say('wrote bench.txt')
    except Exception as e:
        say('no file write: ' + str(e))
    page = 0
    per = 9
    while True:
        clear_screen()
        i = page * per
        y = 2
        while i < len(OUT) and i < (page + 1) * per:
            draw_string(4, y, OUT[i][:46], (0, 0, 0), 'small')
            y += 20
            i += 1
        draw_string(4, 180, 'page ' + str(page + 1) + '  EXE next', (120, 120, 120), 'small')
        show_screen()
        k = getkey()
        while k:
            k = getkey()
        while not k:
            k = getkey()
        if k == 22:
            return
        page = (page + 1) % ((len(OUT) + per - 1) // per)

main()
