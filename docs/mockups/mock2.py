import sys, os
T = '/home/sayer/dev/cg100/toolkit-9yewby'
sys.path.insert(0, T); os.chdir(T)
import casioshot
casioshot.install()
import casui, nat
casioshot.install()
from casui import *
exec(open('/tmp/claude-1000/-/e06b2709-f4b5-44ed-8982-bf7458a8d2c5/scratchpad/mock/mock.py').read().split('casioshot.reset()')[0].split('from casui import *')[1])
OUT = '/tmp/claude-1000/-/e06b2709-f4b5-44ed-8982-bf7458a8d2c5/scratchpad/mock'
casioshot.reset()
# A home: topic grid
g = Grid('Maths Toolkit', ['Calculate', 'Algebra', 'Coord geometry', 'Sequences, series', 'Trig', 'Exp and logs',
                           'Calculus', 'Numerical', 'Vectors', 'Statistics', 'Kinematics', 'Forces',
                           'Graph', 'Notes', 'Settings'], 3, 4, False)
g.draw(1); show_screen()
# B statistics: typed distribution
workspace('Statistics', ['B', '(', '2', '0', ',', ' ', '0', '.', '3', ')'], 'binomial  n = 20, p = 0.3',
          ['P(X = r)', 'P(X <= r)', 'P(X >= r)', 'P(a <= X <= b)', 'Mean, var, sd', 'Test for p'], sel=2)
# C after picking an action: it asks only for what is missing
clear_screen(); status('Statistics')
expr(['B', '(', '2', '0', ',', ' ', '0', '.', '3', ')'])
hline(0, W - 1, 62, LGREY)
draw_string(8, 72, 'P(X >= r)', ACC, 'medium')
draw_string(8, 104, 'r', INK, 'medium'); field(28, 101, 90, '4', True)
draw_string(8, 140, 'EXE to work out', GREY, 'medium')
show_screen()
page('P(X >= 4)', ['X ~ B(20, 0.3)', 'P(X >= 4) = 1 - P(X <= 3)', '= 1 - 0.10709'], ['P(X >= 4) = 0.893 (3 s.f.)'])
# D statistics: data typed
workspace('Statistics', ['2', ',', '3', ',', '5', ',', '7', ',', '8', ',', '9', ',', '1', '1', ',', '1', '4'],
          'data, 8 values', ['Summary stats', 'Quartiles, IQR', 'Outliers', 'Box plot', 'Coding', 'Add y list'])
# E kinematics: SUVAT boxes, fill any three
clear_screen(); status('Kinematics')
for i, (n, v) in enumerate((('s', ''), ('u', '3'), ('v', '?'), ('a', '9.8'), ('t', '2'))):
    y = 26 + i * 27
    draw_string(10, y + 3, n, INK, 'medium'); field(30, y, 110, v, i == 2)
draw_string(160, 30, 'fill any three,', GREY, 'medium')
draw_string(160, 50, '? = find', GREY, 'medium')
draw_string(160, 90, 's = 25.6', ACC, 'medium')
draw_string(160, 112, 'v = 22.6', ACC, 'medium')
draw_string(160, 150, 'EXE for working', GREY, 'medium')
show_screen()
# F kinematics typed: variable acceleration
workspace('Kinematics', ['v', '=', '3', 't', P('2'), '-', '4', 't'], 'velocity as a function of t',
          ['Acceleration', 'Displacement', 'When at rest', 'Distance 0 to T', 'Max / min v', 'Graph v-t'])
# G settings
clear_screen(); status('Settings')
rows = [('Angle', 'Radians'), ('Answers', 'Exact + decimal'), ('Decimals', '3 s.f.'),
        ('Working', 'Shown'), ('Complex', 'a + bi'), ('Sleep after', '10 min'), ('Further Maths', 'in launch script')]
for i, (k, v) in enumerate(rows):
    y = 26 + i * 23
    if i == 1:
        box(2, y - 2, W - 3, y + 19, ACC)
    draw_string(10, y, k, INK, 'medium')
    draw_string(W - 12 - text_w(v, 'medium'), y, v, ACC if i == 1 else GREY, 'medium')
show_screen()
# H "More": every action for what was typed, grouped
clear_screen(); status('Algebra  More')
items = ['Expand', 'Factorise', 'Complete square', 'Roots', 'Discriminant', 'Vertex',
         'Sketch points', 'Inequality < 0', 'Rearrange for k', 'Divide by (x - a)', 'Partial fractions', 'Graph']
g = Grid('Algebra  More', items, 3, 4, False); g.draw(8); show_screen()
paths = casioshot.save('n', OUT); print(len(paths))
