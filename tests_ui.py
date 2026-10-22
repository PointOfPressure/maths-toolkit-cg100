# The redesign's screens driven by key presses, as on the calculator: type
# into a topic, EXE, pick a tile by number, by arrows or from More, answer a
# prompt, and the answer page keys. Uses casioshot's stand-in screen (needs
# Pillow); topic.answer is wrapped to record what each action shows.

# typing: x = 41, ^ = 44 (then RIGHT out), x^2 = 45, digits, + 84, - 85,
# x 74, ( 55, ) 56, = SHIFT 55, ALPHA k = 32 55, ALPHA y = 32 85, DOWN 34
X2_3X_K = (41, 45, 84, 83, 41, 84, 32, 55)
TWO_X = (82, 44, 41, 25, 84, 83, 31, 55, 81, 72)
HIDDEN = (71, 44, 41, 25, 85, 83, 74, 82, 44, 41, 25, 84, 82, 31, 55, 91)
PAIR = (41, 84, 82, 32, 85, 31, 55, 72, 34, 83, 41, 85, 32, 85, 31, 55, 81)
CUBIC = (83, 41, 44, 83, 25, 85, 41, 84, 82)     # 3x^3 - x + 2

EXE = 95
TOOLS = 36
DOWN = 34
UP = 14
RIGHT = 25
EXITK = 22
FORMAT = 94

def _drive(tid, keys):
    import casioshot
    import topic
    got = []

    def rec(title, lines):
        got.append((title, lines))
    real = topic.answer
    topic.answer = rec
    topic.STATE.clear()
    casioshot.reset()
    casioshot.press(*keys)
    try:
        if tid == 'geo':
            import coord
            coord.run()
        else:
            topic.run(tid)
    finally:
        topic.answer = real
    return got

# Coord geometry: A = (1, 2) (RIGHT out of the x box), DOWN to B's y box,
# -6, LEFT to its x box, 5
AB = (81, 25, 82, 34, 85, 73, 23, 23, 23, 72)

def _text(lines):
    import topic
    out = []
    for ln in lines:
        if isinstance(ln, tuple) and ln[0] == '=':
            out.append(topic.shown(ln, 'both'))
        elif isinstance(ln, tuple):
            out.append(str(ln[1]))
        else:
            out.append(ln)
    return ' | '.join(out).replace(' ', '').replace('*', '')

def run(check):
    try:
        import casioshot
    except SystemExit:
        check('tests_ui needs Pillow', False)
        return
    casioshot.install()
    import topic
    import casui
    import plot
    plot.run = lambda *a, **k: None

    def case(name, tid, keys, title, needles):
        try:
            got = _drive(tid, keys)
        except Exception as e:
            check('ui ' + name, False, repr(e))
            return
        check('ui ' + name + ': an answer page', len(got) == 1, [g[0] for g in got])
        if got:
            check('ui ' + name + ': ' + title, got[0][0] == title, got[0][0])
            t = _text(got[0][1])
            for nd in needles:
                hit = [a for a in nd.split('|') if a.replace(' ', '') in t]
                check('ui ' + name + ' has ' + nd, hit, t[:300])

    # tile 1 by its number key, and by EXE on the first tile
    case('alg csq by 1', 'alg', X2_3X_K + (EXE, 81), 'Complete square', ['(x+3/2)^2+k-9/4'])
    case('alg csq by EXE', 'alg', X2_3X_K + (EXE, EXE), 'Complete square', ['k-9/4'])
    # arrows: RIGHT to Factorise, DOWN to Discriminant
    case('alg arrows', 'alg', X2_3X_K + (EXE, RIGHT, DOWN, EXE), 'Discriminant', ['9-4k'])
    case('exp solve', 'exp', TWO_X + (EXE, 81), 'Solve', ['x=2+log_23=3.58'])
    case('exp sub u', 'exp', HIDDEN + (EXE, 82), 'Sub u = 2^x', ['u^2-3u+2=0'])
    case('pair solve', 'alg', PAIR + (EXE, 81), 'Solve', ['x=1', 'y=2'])
    # More (TOOLS) lists every action; Factor theorem asks for x
    import recog
    import acts
    offs = [o[0] for o in acts.offers(recog.form(['3x^3-x+2']), 'alg')]
    i = offs.index('Factor theorem')
    nav = (DOWN,) * (i // 3) + (RIGHT,) * (i % 3)
    case('more + prompt', 'alg', CUBIC + (EXE, TOOLS) + nav + (EXE, 85, 81, EXE), 'Factor theorem',
         ['f(-1)=0', '(x+1)isafactor'])
    # typing after EXE goes back to editing: + 1 then EXE reads the new row
    case('type again', 'alg', X2_3X_K + (EXE, 84, 81, EXE, 81), 'Complete square', ['k+1-9/4|k-5/4'])
    # Coord geometry: point boxes, then a tile
    case('geo perp bisector', 'geo', AB + (EXE, 81), 'Perp bisector', ['midpoint(3,-2)', 'x-2y-7=0'])
    case('geo distance', 'geo', AB + (EXE, 71), 'Distance', ['AB=4sqrt(5)'])
    # MENU adds C; DOWN past the points reaches the line row
    case('geo circle ABC', 'geo', AB + (35, 85, 72, 25, 85, 72, EXE, 81), 'Circle ABC', [])
    case('geo point and line', 'geo', (81, 25, 82, 34, 34, 32, 85, 31, 55, 83, 41, EXE, 82),
         'Perpendicular thru A', ['x+3y-7=0'])
    # Calculus: y = x^3 - 3x, Stationary points (tile 2); dy/dx = x y with a point
    case('calc stationary', 'calc', (32, 85, 31, 55, 41, 44, 83, 25, 85, 83, 41, EXE, 82),
         'Stationary points', ['maximum', 'minimum'])
    # Trig: EXE with nothing typed offers the boxes; Arc and sector, r = 5,
    # RIGHT to the angle, 1 (radians), EXE
    case('trig sector boxes', 'trig', (EXE, 82, 72, RIGHT, 81, EXE), 'Arc and sector', ['arc=5', 'area=25/2'])
    # Sequences: EXE with nothing typed, AP facts, a = 3, RIGHT, d = 2,
    # RIGHT, n = 5, EXE: u(n) and S(n)
    case('seq AP boxes', 'seq', (EXE, 81, 83, RIGHT, 82, RIGHT, 72, EXE), 'AP facts', ['u(n)=11', 'S(n)=35'])
    # an error stays on the editing screen, no answer
    got = _drive('alg', (41, 84, 31, 55, 31, 55, EXE, EXE))
    check('ui error: no action runs', got == [], got)
    # the answer page: TOOLS hides the working, FORMAT flips the box
    lines = [('w', 'note'), '2^x = 12', 'x = log_2 12', ('=', 'x = ', '2 + log_2 3', '3.58 (3 s.f.)', None)]
    full = topic.layout(lines, True, 'both')
    bare = topic.layout(lines, False, 'both')
    check('answer: working shown', len(full) == 4, len(full))
    check('answer: working hidden leaves the box', len(bare) == 1 and bare[0][0] == 'b', bare)
    check('answer: exact view', topic.shown(lines[-1], 'exact') == 'x = 2 + log_2 3')
    check('answer: decimal view', topic.shown(lines[-1], 'decimal') == 'x = 3.58 (3 s.f.)')
    check('answer: both view', topic.shown(lines[-1], 'both') == 'x = 2 + log_2 3 = 3.58 (3 s.f.)')
    check('answer: integer once', topic.shown(('=', 'x = ', '4', None), 'both') == 'x = 4')
    # the page itself: keys move between the views without errors
    casioshot.reset()
    casioshot.press(DOWN, FORMAT, FORMAT, TOOLS, TOOLS, FORMAT, EXITK)
    topic.answer('Solve', lines)
    check('answer page draws', len(casioshot.SCREEN.frames) >= 5, len(casioshot.SCREEN.frames))
    # HOME from the answer page leaves through every screen
    casioshot.reset()
    casioshot.press(casui.HOME)
    try:
        topic.answer('Solve', lines)
        check('HOME from the answer page', False)
    except casui.Home:
        check('HOME from the answer page', True)
    # the Settings page changes the settings until exit
    import cfg
    was = dict(casui.SET)
    casioshot.reset()
    casioshot.press(RIGHT, DOWN, RIGHT, EXITK)
    cfg.page()
    check('settings: answers changed', casui.SET['answers'] != was['answers'], casui.SET)
    check('settings: decimals changed', casui.SET['decimals'] != was['decimals'], casui.SET)
    casui.SET.clear()
    casui.SET.update(was)
    casui.configure()
    # the launch script's values reach the settings; unknown ones keep the default
    import home
    real = home.run
    home.run = lambda: None
    try:
        casui.main(further=True, angle='deg', answers='exact', decimals='4dp', complex='polar',
                   sleep=5, repeat='fast')
        check('main: further on', casui.SET['further'] is True)
        check('main: settings', casui.SET['angle'] == 'deg' and casui.DEG and casui.SET['decimals'] == '4dp'
              and casui.SET['answers'] == 'exact' and casui.SET['sleep'] == 5, casui.SET)
        casui.main(angle='degrees?', decimals=7)
        check('main: bad values keep defaults', casui.SET['angle'] == 'rad' and casui.SET['decimals'] == '3sf'
              and not casui.SET['further'], casui.SET)
    finally:
        home.run = real
        casui.SET.clear()
        casui.SET.update(was)
        casui.configure()
    # Further topics appear only when switched on
    casui.SET['further'] = False
    a = [t[0] for t in home.tiles()]
    casui.SET['further'] = True
    b = [t[0] for t in home.tiles()]
    casui.SET['further'] = was['further']
    check('home: no Further topics by default', 'Complex' not in a and 'Algebra' in a, a)
    check('home: Further topics when on', 'Complex' in b and 'Matrices' in b, b)
    check('home: Graph, Notes, Settings last', a[-3:] == ['Graph', 'Notes', 'Settings'], a[-3:])

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    fails = []
    n = [0]

    def check(label, ok, detail=''):
        n[0] += 1
        if not ok:
            fails.append(label + '  [' + str(detail) + ']')
    run(check)
    for f in fails:
        print('FAIL ' + f)
    print(str(n[0]) + ' checks, ' + str(len(fails)) + ' failures')
