import sys, os
T = '/home/sayer/dev/cg100/toolkit-9yewby'
sys.path.insert(0, T)
os.chdir(T)
import casioshot
casioshot.install()
import casui, nat
casioshot.install()
from casui import *
OUT = '/tmp/claude-1000/-/e06b2709-f4b5-44ed-8982-bf7458a8d2c5/scratchpad/mock'

def tiles(labels, y0, sel=0, cols=2, th=36):
    tw = W // cols
    for i, lab in enumerate(labels):
        x0 = (i % cols) * tw
        y = y0 + (i // cols) * th
        x1 = x0 + tw - 1
        y1 = y + th - 1
        if i == sel:
            box(x0 + 2, y + 2, x1 - 2, y1 - 2, ACC); box(x0 + 3, y + 3, x1 - 3, y1 - 3, ACC)
            c = ACC
        else:
            box(x0 + 2, y + 2, x1 - 2, y1 - 2, LGREY); c = INK
        ctext(x0 + tw // 2, y + (th - 18) // 2, lab, c, 'medium')

def expr(row, base=46):
    ed = nat.Ed(row)
    nat.draw(ed, ed.root, 8, base, 368)

def P(e): return ['P', list(e)]

def workspace(title, row, note, labels, sel=0, base=46):
    clear_screen(); status(title)
    expr(row, base)
    hline(0, W - 1, 62, LGREY)
    if note:
        draw_string(8, 66, note, GREY, 'medium')
        tiles(labels, 86, sel, th=35)
    else:
        tiles(labels, 66, sel, th=42)
    show_screen()

def page(title, lines, answer, right='working', bar=None):
    clear_screen(); status(title, False, False, right)
    y = TOP + 3
    for blk in casui._blocks(lines, 1):
        kind = blk[0]
        play(blk, 6, y, INK if kind == 'a' else GREY)
        y += blk[3]
    for blk in casui._blocks(answer, 1):
        h = blk[3]
        box(2, y + 1, W - 9, y + h + 1, ACC)
        play(blk, 8, y + 2, ACC)
        y += h + 4
    if bar:
        vline(W - 3, TOP, BOT, BAR); vline(W - 2, TOP, BOT, BAR)
        vline(W - 3, TOP, TOP + bar, ACC); vline(W - 2, TOP, TOP + bar, ACC)
    show_screen()

def field(x, y, w, s, on):
    box(x, y, x + w, y + 22, ACC if on else LGREY)
    if on:
        box(x + 1, y + 1, x + w - 1, y + 22 - 1, ACC)
    draw_string(x + 6, y + 3, s, INK, 'medium')
    if on:
        cx = x + 6 + text_w(s, 'medium') + 1
        vline(cx, y + 4, y + 18, ACC); vline(cx + 1, y + 4, y + 18, ACC)

casioshot.reset()
# 1 Algebra: type, then only fitting actions
workspace('Algebra', ['x', P('2'), '+', '3', 'x', '+', 'k'], 'quadratic in x, k unknown',
          ['Complete square', 'Factorise', 'Roots', 'Discriminant', 'Vertex', 'Graph'])
# 2 hidden quadratic
workspace('Exp and logs', ['4', P('x'), '-', '3', '*', '2', P('x'), '+', '2', '=', '0'],
          'quadratic in 2^x', ['Solve', 'Sub u = 2^x', 'Factorise', 'Graph'])
# 3 exponential equation: Solve vs Rearrange
workspace('Exp and logs', ['2', P('x'), '+', '3', '=', '1', '5'], 'equation in x',
          ['Solve', 'Rearrange for x', 'Take logs', 'Graph'], sel=1)
# 4 two unknowns
workspace('Exp and logs', ['2', P('x'), '+', '3', P('y'), '=', '1', '5'], 'equation in x and y',
          ['Rearrange for y', 'Rearrange for x', 'Implicit dy/dx', 'Graph'])
# 5 boxes where it is not one expression: coordinate geometry
clear_screen(); status('Coord geometry')
draw_string(8, 30, 'A', INK, 'medium'); draw_string(28, 30, '(', INK, 'medium')
field(40, 27, 70, '1', False); draw_string(116, 30, ',', INK, 'medium'); field(126, 27, 70, '2', False)
draw_string(202, 30, ')', INK, 'medium')
draw_string(8, 58, 'B', INK, 'medium'); draw_string(28, 58, '(', INK, 'medium')
field(40, 55, 70, '5', False); draw_string(116, 58, ',', INK, 'medium'); field(126, 55, 70, '-6', True)
draw_string(202, 58, ')', INK, 'medium')
draw_string(222, 44, '+ point', GREY, 'medium')
hline(0, W - 1, 84, LGREY)
tiles(['Perp bisector', 'Midpoint', 'Gradient', 'Distance', 'Line AB', 'Circle diam AB'], 86, th=35)
show_screen()
# 6 the alternative: Casio boxes for a quadratic too
clear_screen(); status('Quadratic  ax^2+bx+c')
for i, (n, v) in enumerate((('a', '1'), ('b', '3'), ('c', 'k'))):
    x = 8 + i * 125
    draw_string(x, 30, n, INK, 'medium'); field(x + 16, 27, 92, v, i == 2)
hline(0, W - 1, 58, LGREY)
tiles(['Complete square', 'Factorise', 'Roots', 'Discriminant', 'Vertex', 'Graph'], 62, th=42)
show_screen()
# 7 working: complete the square
page('Complete square', ['x^2 + 3x + k', '= (x + 3/2)^2 - (3/2)^2 + k', '= (x + 3/2)^2 - 9/4 + k'],
     ['(x + 3/2)^2 + k - 9/4'], bar=None)
# 8 working page continues (scrolled)
page('Complete square', ['vertex (-3/2, k - 9/4)', 'min value k - 9/4 at x = -3/2',
                         'line of symmetry x = -3/2'], [], bar=60)
# 9 working: solve 2^x + 3 = 15
page('Solve', ['2^x + 3 = 15', '2^x = 12', 'x = log_2 12', 'x = 2 + log_2 3'],
     ['x = 3.58 (3 s.f.)'])
# 10 rearrange 2^x + 3^y = 15 for y
page('Rearrange for y', ['2^x + 3^y = 15', '3^y = 15 - 2^x'], ['y = log_3(15 - 2^x)'])
paths = casioshot.save('m', OUT)
print(paths)
