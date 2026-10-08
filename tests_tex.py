# Checks for the display typesetter (tex.py), its glyphs (texg.py), line
# breaking, the display lists casui draws and the precompiled notes.
#   python3 tests_tex.py
# tests.py-style entry point: run(check).
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) or '.'
sys.path.insert(0, HERE)

import tex
import texg
import casrender
import casui
import font
import mkglyph

M = 'medium'
S = 'small'


def A(s, sz=M):
    return ('atom', s, sz)


# input -> the box it must typeset to
CASES = [
    ('speed = 3.61 m/s', A('speed = 3.61 m/s')),
    ('x^2', ('sup', A('x'), A('2', S), M)),
    ('e^(kt)', ('sup', A('e'), A('kt', S), M)),
    ('e^kt', ('row', [('sup', A('e'), A('k', S), M), A('t')])),
    ('x_1 + S_n', ('row', [('sub', A('x'), A('1', S), M), A(' + '), ('sub', A('S'), A('n', S), M)])),
    ('u_(n+1)', ('sub', A('u'), A('n+1', S), M)),
    ('S_inf', ('sub', A('S'), ('g', 'i', S), M)),
    ('a1b1', ('row', [('sub', A('a'), A('1', S), M), ('sub', A('b'), A('1', S), M)])),
    ('2x2 matrix', A('2x2 matrix')),
    ('1/2', ('frac', A('1'), A('2'), M)),
    ('(a+b)/(c+d)', ('frac', A('a + b'), A('c + d'), M)),
    ('1/2 n', ('row', [('frac', A('1'), A('2'), M), A(' n')])),
    ('n(n+1)/2', ('frac', A('n(n + 1)'), A('2'), M)),
    ('a(1 - r^n) / (1 - r)', ('frac', ('row', [A('a(1 - '), ('sup', A('r'), A('n', S), M), A(')')]),
                              A('1 - r'), M)),
    ('ln 2/|k|', ('frac', A('ln 2'), A('|k|'), M)),
    ('sqrt(3)', ('root', A('3'), M)),
    ('sqrt a/sqrt b', ('frac', ('root', A('a'), M), ('root', A('b'), M), M)),
    ('|x| < 1', A('|x| < 1')),
    ('P(B | A)', A('P(B | A)')),
    ('theta', ('g', 't', M)),
    ('sin theta ~= theta', ('row', [A('sin '), ('g', 't', M), A(' '), ('g', '~', M), A(' '), ('g', 't', M)])),
    ('x <= 2', ('row', [A('x '), ('g', '<', M), A(' 2')])),
    ('x != 0', ('row', [A('x '), ('g', '#', M), A(' 0')])),
    ('h->0', ('row', [A('h '), ('g', '-', M), A(' 0')])),
    ('x=2', A('x = 2')),
    ('n^2-5*n+3', ('row', [('sup', A('n'), A('2', S), M), A(' - 5n + 3')])),
    ('3-4', A('3-4')),
    ('1-2i', A('1 - 2i')),
    ('x-axis', A('x-axis')),
    ('2*x', A('2x')),
    ('3*2^n', ('row', [A('3'), ('dot', M), ('sup', A('2'), A('n', S), M)])),
    ('A*cos(x)', A('A cos(x)')),
    ('a * b', ('row', [A('a '), ('g', 'x', M), A(' b')])),
    ('z* = x - yi', ('row', [('sup', A('z'), A('*', S), M), A(' = x - yi')])),
    ('a.b', ('row', [A('a'), ('dot', M), A('b')])),
    ('i.e. to 2 d.p.', A('i.e. to 2 d.p.')),
    ('sin^2 x', ('row', [('sup', A('sin'), A('2', S), M), A(' x')])),
    ('f^-1(x)', ('row', [('sup', A('f'), A('-1', S), M), A('(x)')])),
    ("f^(r)(0)", ('row', [('sup', A('f'), A('(r)', S), M), A('(0)')])),
    ('nCr', ('row', [('sup', A(''), A('n', S), M), ('sub', A('C'), A('r', S), M)])),
    ('xbar', ('bar', A('x'), M)),
    ('that', A('that')),
    ('1e-8', ('row', [A('1'), ('g', 'x', M), ('sup', A('10'), A('-8', S), M)])),
    ('sum_{r=1}^{n} r', ('row', [('ss', ('g', 'Z', M), A('r=1', S), A('n', S), M), A(' r')])),
    ('sum of terms', A('sum of terms')),
    ('int 1/x dx', ('row', [('g', 'I', M), A(' '), ('frac', A('1'), A('x'), M), A(' dx')])),
    ('int from a to b', A('int from a to b')),
    ('dy/dx = (dy/du)(du/dx)', ('row', [('frac', A('dy'), A('dx'), M), A(' = '), ('frac', A('dy'), A('du'), M),
                                        ('frac', A('du'), A('dx'), M)])),
    ('(1/k)e^(kx)', ('row', [('frac', A('1'), A('k'), M), ('sup', A('e'), A('kx', S), M)])),
    ('f(x/2)', ('row', [A('f'), ('paren', ('frac', A('x'), A('2'), M), M)])),
    ('dy/dx = -(dF/dx) / (dF/dy)', ('row', [('frac', A('dy'), A('dx'), M), A(' = -'),
                                            ('frac', A('dF/dx'), A('dF/dy'), M)])),
    ('d2y/dx2', ('frac', ('row', [('sup', A('d'), A('2', S), M), A('y')]), ('sup', A('dx'), A('2', S), M), M)),
    ('dr/dtheta', ('frac', A('dr'), ('row', [A('d'), ('g', 't', M)]), M)),
    ('flow/cap', A('flow/cap')),
    ('5%: 1.6449 / 1.9600', A('5%: 1.6449 / 1.9600')),
    ('e^(2 pi i k / n)', ('sup', A('e'), ('row', [A('2', S), ('g', 'p', S), A('ik/n', S)]), M)),
    ('[a b; c d]', ('mat', [[A('a'), A('b')], [A('c'), A('d')]], M)),
    ('[cos t  -sin t; sin t  cos t]', ('mat', [[A('cos t'), A('-sin t')], [A('sin t'), A('cos t')]], M)),
    ('rank [A|b] = 2', A('rank [A|b] = 2')),
    ('A \\ B', A('A \\ B')),
    ('a\\*b', A('a*b')),
    ('\\partial f/\\partial x', ('frac', ('row', [('g', 'q', M), A('f')]), ('row', [('g', 'q', M), A('x')]), M)),
    ('(x', A('(x')),
    ('x)', A('x)')),
    ('|x', A('|x')),
    ('a^', A('a^')),
]

# glyph code -> the name it came from, to read a box back as text
NAMES = {'Z': 'sum', 'I': 'int', 'q': 'partial', 'U': 'cup', 'N': 'cap', 'E': 'in'}
for _k in tex.GREEK:
    NAMES[tex.GREEK[_k]] = _k


def text_of(b):
    k = b[0]
    if k == 'atom':
        return b[1]
    if k == 'g':
        return NAMES.get(b[1], ' ')
    if k == 'row':
        return ''.join([text_of(c) for c in b[1]])
    if k == 'mat':
        return ';'.join([' '.join([text_of(c) for c in r]) for r in b[1]])
    if k in ('bar', 'hat'):
        return text_of(b[1]) + k
    if k == 'root':
        return 'sqrt' + text_of(b[1])
    if k in ('dot', 'sp'):
        return ' '
    return ' '.join([text_of(c) for c in b[1:-1]])


def alnum(s):
    s = re.sub(r'(\d)e([-+]?)(\d)', r'\1 10 \3', s)    # 1e-8 -> 1 x 10^-8
    s = re.sub(r'\\(times|pm)', ' ', s)
    return re.sub(r'[^A-Za-z0-9]', '', s)


def keeps_text(check, label, s, b):
    check('tex: no character lost: ' + label + repr(s), alnum(s) == alnum(text_of(b)),
          alnum(text_of(b)))


def fits(rows, width):
    # rows from tex.lines all fit, unless a single piece had to be shrunk
    bad = 0
    for r, dx in rows:
        if dx + casrender.measure(r)[0] > width:
            bad += 1
    return bad


def corpus():
    # every tool output line of the tests' cases, and every notes line
    import tests
    import casutil
    lines = []
    for m in tests.MODULES:
        mod = __import__(m)
        tools = {}
        for code, title, ts in mod.SECTIONS:
            for t in ts:
                tools[code + '/' + t[0]] = t
        for code, label, text, needles in __import__('tests_' + m).CASES:
            t = tools.get(code + '/' + label)
            if t is None:
                continue
            try:
                vals = casutil.convert(t[1], text)
            except ValueError:
                continue
            lines.append((m + ' ' + label, casutil.call_tool(t[2], vals)))
    return lines


def run(check):
    # glyphs: every code drawn in both sizes, from the generator
    check('tex: texg.py is current (python3 mkglyph.py)', open(os.path.join(HERE, 'texg.py')).read() == mkglyph.source())
    codes = set(tex.GREEK.values()) | set(tex.SYMG.values()) | set(tex.CMD.values()) | set('ZIx')
    for c in sorted(codes):
        for t, sz in ((texg.M, M), (texg.S, S)):
            check('tex: glyph ' + c + ' ' + sz, c in t and len(t[c][3]) > 0 and len(t[c][3]) % 2 == 0)
            if c in t:
                adv, asc, desc, pix = t[c]
                xs = pix[0::2]
                check('tex: glyph inside its advance ' + c + ' ' + sz, max(xs) < adv, (max(xs), adv))
                check('tex: glyph small ' + c + ' ' + sz, len(pix) // 2 <= 70, len(pix) // 2)
    # structure
    for s, want in CASES:
        got = tex.row(s)
        check('tex: typesets ' + repr(s), casrender.flat(got) == casrender.flat(want), got)
        keeps_text(check, '', s, got)
    # the fast path never changes what a line becomes
    for s, want in CASES:
        if tex.plain(s):
            items, i, ok = tex.seq(tex.tokens(s), 0, M, 0, None)
            check('tex: plain() only for plain lines: ' + repr(s), tex.pack(items, M) == A(s))
    # matrix rows from casutil.fmtm are joined into one matrix line
    rows = casui._matrows(['A^-1 = [1 2]', '       [3 4]', 'det = -2', ('w', 'M = [1 0]'), ('w', '    [0 1]')])
    check('tex: matrix rows joined', rows == ['A^-1 = [1 2; 3 4]', 'det = -2', ('w', 'M = [1 0; 0 1]')], rows)
    # breaking: long lines split within the width and keep their text
    long = ['x^8 + 8x^7 + 28x^6 + 56x^5 + 70x^4 + 56x^3 + 28x^2 + 8x + 1 = (x + 1)^8 for every x',
            'the tangent at P is perpendicular to the radius, so the gradient is -1/m and y - b = m(x - a)',
            'a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, and so on',
            'sum_{r=1}^{n} r^3 = (1/4) n^2 (n + 1)^2 = (sum_{r=1}^{n} r)^2, so the sums are squares of triangles']
    for s in long:
        b = tex.row(s)
        for w in (368, 250, 160):
            rows = tex.lines(b, w)
            check('tex: breaks within ' + str(w) + ': ' + s[:30], fits(rows, w) == 0 and len(rows) > 1,
                  [casrender.measure(r)[0] for r, dx in rows])
            joined = ''.join([text_of(r) for r, dx in rows])
            check('tex: breaking keeps the text: ' + s[:30], alnum(joined) == alnum(text_of(b)))
            check('tex: continuation set in: ' + s[:30], rows[0][1] == 0 and all(dx == 16 for r, dx in rows[1:]))
    # pieces wider than any line: a long number is cut, a wide matrix goes a row a line
    for s in ('n = ' + '1234567890' * 20, 'A = [' + ' '.join(['2000000000000000000'] * 3) + '; 1 2 3]'):
        rows = tex.lines(tex.row(s), 368)
        check('tex: over-wide piece fits: ' + s[:20], fits(rows, 368) == 0, len(rows))
    # display lists: merging joins strings on one baseline without moving text far
    blk = casui.block('a', tex.row('u_(n+1) > u_n for all n, x^2 + y^2 = r^2'), 8)
    check('tex: display list merges strings', len(blk[1]) <= 4, blk[1])
    # precompiled notes lines read back the same as the block they came from
    import mknotes
    import notesui
    for s in ('S_n = a(1 - r^n)/(1 - r)', 'sin theta ~= theta, |x| < 1', '[a b; c d] [x; y]'):
        blk = casui.block('w', tex.row(s), 16)
        back = notesui.lines(mknotes.encode(blk))[0][1]
        notesui.unpack(back)
        check('tex: notes line strings round trip: ' + s, back[1] == blk[1] and back[3] == blk[3])
        check('tex: notes line pixels round trip: ' + s, mknotes.runs_of(back[4]) == mknotes.runs_of(blk[4]))
    # fuzz: every tool output and notes line typesets, keeps its text, fits
    n = 0
    over = []
    for where, lines in corpus():
        try:
            blocks = casui._blocks(lines, 1)
        except Exception as e:
            check('tex: result typesets: ' + where, False, repr(e))
            continue
        for ln in lines:
            if isinstance(ln, tuple) and ln[0] in ('m', 'mw'):
                b = casrender.flat(casrender.build(ln[1], 0))
            else:
                s = ln if isinstance(ln, str) else ln[1]
                b = tex.row(s)
                keeps_text(check, where + ': ', s, b)
                n += 1
            x = 16 if isinstance(ln, tuple) and ln[0] in ('w', 'mw') else 8
            if fits(tex.lines(b, 376 - x), 376 - x):
                over.append(where)
        for blk in blocks:
            for sx, sy, text, size in blk[1]:
                if sx + font.strw(text.rstrip(), size) > 384:
                    over.append(where + ': ' + text)
    check('tex: tool output lines fit the screen', not over, over[:5])
    import casui as cu
    for name, mods in cu.NOTE_PAPERS:
        for m in mods:
            for topic, lines in __import__(m).NOTES:
                for s in lines:
                    keeps_text(check, m + ': ', s.strip(), tex.row(s.strip()))
                    n += 1
    check('tex: corpus size', n > 5000, n)
    return n


if __name__ == '__main__':
    fails = []
    count = [0]

    def check(label, cond, detail=''):
        count[0] += 1
        if not cond:
            fails.append(label + ('  [' + str(detail) + ']' if detail != '' else ''))
    n = run(check)
    for f in fails:
        print('FAIL  ' + f)
    print('tests_tex: ' + str(count[0]) + ' checks, ' + str(len(fails)) + ' failures, ' + str(n) + ' lines')
    sys.exit(1 if fails else 0)
