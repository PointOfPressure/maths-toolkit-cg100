# Memory probe: how much Python memory is free, and how much each part of
# the toolkit takes once loaded. About a minute. Photo the last screen.
from casioplot import *

BLK = (0, 0, 0)
OUT = []

def free_kb():
    # fill memory with 1 KB blocks until it runs out, then let them go
    blocks = []
    try:
        while True:
            blocks.append(bytearray(1024))
    except MemoryError:
        pass
    n = len(blocks)
    blocks = None
    return n

def biggest_kb():
    # largest single block that fits
    lo = 0
    hi = 4096
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            b = bytearray(mid * 1024)
            b = None
            lo = mid
        except MemoryError:
            hi = mid - 1
    return lo

def note(s):
    OUT.append(s)
    clear_screen()
    y = 2
    for ln in OUT[-13:]:
        draw_string(4, y, ln, BLK, 'small')
        y += 14
    show_screen()

note('start  free ' + str(free_kb()) + ' KB  biggest ' + str(biggest_kb()) + ' KB')
for name in ('font', 'casui', 'nat', 'caslex', 'caseng', 'casutil', 'cascalc',
             'caspoly', 'casrender', 'tex', 'mpure', 'mcalc'):
    try:
        __import__(name)
        note(name + '  free ' + str(free_kb()) + ' KB')
    except MemoryError:
        note(name + '  MEMORY ERROR')
        break
    except Exception as e:
        note(name + '  error ' + str(e)[:24])
note('biggest block now ' + str(biggest_kb()) + ' KB')
note('done - photo this, EXIT to quit')
k = getkey()
while k != 22:
    k = getkey()
