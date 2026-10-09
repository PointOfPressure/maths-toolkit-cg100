# PC-only: renders screens to shots/*.png with the toolkit's own char_w metric.
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("casioshot needs Pillow:  pip install pillow")
    sys.exit(2)

W = 384
H = 192
SCALE = 3
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]
FONT_PX = {"small": 11, "medium": 15, "large": 26}


def _load_font(px):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


class Screen(object):
    def __init__(self):
        self.img = Image.new("RGB", (W, H), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)
        self.fonts = {}
        for name in FONT_PX:
            self.fonts[name] = _load_font(FONT_PX[name])
        self.frames = []
        self.overflow = []
        self.mark = None    # frames drawn before the scripted keys ran out

    def clear(self):
        self.draw.rectangle([0, 0, W - 1, H - 1], fill=(255, 255, 255))

    def set_pixel(self, x, y, c=None):
        if not (0 <= x <= W - 1 and 0 <= y <= H - 1):
            return
        self.img.putpixel((int(x), int(y)), tuple(c) if c else (0, 0, 0))

    def get_pixel(self, x, y):
        if not (0 <= x <= W - 1 and 0 <= y <= H - 1):
            return None
        return self.img.getpixel((int(x), int(y)))

    def draw_string(self, x, y, s, c=None, size=None):
        if not (0 <= x <= W - 1 and 0 <= y <= H - 1):
            return
        size = size or "medium"
        col = tuple(c) if c else (0, 0, 0)
        import casrender
        pen = x
        f = self.fonts.get(size, self.fonts["medium"])
        # put the stand-in font's baseline where casrender expects the device's
        dy = casrender.ASC[size] - f.getmetrics()[0]
        for ch in str(s):
            adv = casrender.cw(ch, size)
            # centred in the device advance, as a fixed-cell font draws it
            x0, y0, x1, y1 = f.getbbox(ch)
            off = (adv - (x1 - x0)) // 2 - x0 if ch != ' ' else 0
            self.draw.text((pen + off, y + dy), ch, font=f, fill=col)
            pen += adv
        if pen > W:
            self.overflow.append((len(self.frames), y, str(s), pen - W))

    def show(self):
        self.frames.append(self.img.copy())


SCREEN = Screen()
KEYS = []
_TOGGLE = [False]


def _getkey():
    if KEYS:
        k = KEYS[0]
        if k is None:
            KEYS.pop(0)
            return 0
        KEYS[0] = None
        return k
    # out of scripted keys: alternate EXIT / idle so every loop exits
    if SCREEN.mark is None:
        SCREEN.mark = len(SCREEN.frames)
    _TOGGLE[0] = not _TOGGLE[0]
    return 22 if _TOGGLE[0] else 0


PATCH = {
    "set_pixel": lambda: SCREEN.set_pixel,
    "get_pixel": lambda: SCREEN.get_pixel,
    "draw_string": lambda: SCREEN.draw_string,
    "clear_screen": lambda: SCREEN.clear,
    "show_screen": lambda: SCREEN.show,
    "getkey": lambda: _getkey,
}


def install(*extra):
    import casioplot
    for name in PATCH:
        setattr(casioplot, name, PATCH[name]())
    here = os.path.dirname(os.path.abspath(__file__))
    for name in list(sys.modules.keys()):
        mod = sys.modules[name]
        f = getattr(mod, "__file__", None)
        if not f or os.path.dirname(os.path.abspath(f)) != here:
            continue
        for pname in PATCH:
            if hasattr(mod, pname):
                setattr(mod, pname, PATCH[pname]())


def press(*codes):
    # idle, key, idle: the UI waits for release before reading the next key
    for c in codes:
        KEYS.append(None)
        KEYS.append(c)
        KEYS.append(None)


def reset():
    _TOGGLE[0] = False
    SCREEN.frames = []
    SCREEN.overflow = []
    SCREEN.mark = None
    del KEYS[:]
    SCREEN.clear()


def save(prefix, outdir="shots"):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    paths = []
    for i in range(len(SCREEN.frames)):
        im = SCREEN.frames[i]
        big = im.resize((W * SCALE, H * SCALE), Image.NEAREST)
        p = os.path.join(outdir, prefix + "-" + str(i + 1) + ".png")
        big.save(p)
        paths.append(p)
    return paths


X2_3X_K = (41, 45, 84, 83, 41, 84, 32, 55)
HIDDEN = (71, 44, 41, 25, 85, 83, 74, 82, 44, 41, 25, 84, 82, 31, 55, 91)
TWO_X = (82, 44, 41, 25, 84, 83, 31, 55, 81, 72)
XY = (82, 44, 41, 25, 84, 83, 44, 32, 85, 25, 31, 55, 81, 72)
# 2 log(x) = log(4) + log(x + 8)
LOGEQ = (82, 31, 45, 41, 56, 31, 55, 31, 45, 71, 56, 84, 31, 45, 41, 84, 62, 56)


AB_KEYS = (81, 25, 82, 34, 85, 73, 23, 23, 23, 72)
# y = x^3 - 3x;  y = x e^x
CUBIC_Y = (32, 85, 31, 55, 41, 44, 83, 25, 85, 83, 41)
XEX = (32, 85, 31, 55, 41, 46, 41, 25)


def geo_scene(keys):
    import topic
    import coord
    topic.STATE.clear()
    press(*keys)
    coord.run()


def topic_scene(tid, keys):
    import topic
    topic.STATE.clear()
    press(*keys)
    topic.run(tid)


def _scenes():
    import casui
    import caslex
    import plot
    quad = ('Quadratic', 'a,b,c', lambda a, b, c: [
        'x = 1/2 + i*sqrt(3)/2', 'x = 1/2 - i*sqrt(3)/2',
        ('m', caslex.parse('(1+sqrt(3)i)/2')),
        ('!', 'no real roots'),
        ('w', 'disc = b^2 - 4ac = -3'), ('w', 'vertex (1/2, 3/4)')])

    def result_scene(mode):
        press(*([94] * mode))
        casui.result('Quadratic', '1,-1,1', lambda: quad[2](1, -1, 1))

    def calc(*keys):
        casui.HIST[:] = []
        casui.CALC.clear()
        press(*keys)
        casui.calc_section()

    def tool_input(*keys):
        casui._LAST.clear()
        press(*keys)
        casui.input_line('Quadratic', 'a,b,c', '')

    def tool(mod, label, text, *keys):
        # a tool's result screen; keys: 94 cycles the form, 26 pages down
        import casutil
        m = __import__(mod)
        for code, title, tools in m.SECTIONS:
            for t in tools:
                if t[0] == label:
                    vals = casutil.convert(t[1], text)
                    press(*keys)
                    casui.result(label, text, lambda: casutil.call_tool(t[2], vals))
                    return

    def notes(mod, i, *keys):
        import notesui
        press(*keys)
        notesui.show(__import__(mod).NOTES[i][0], __import__('tn' + mod[5:]).N[i])

    def booklet(i, *keys):
        import notesui
        import tn_fb
        press(*keys)
        notesui.show(tn_fb.T[i], tn_fb.N[i])

    return [
        ("tex-expand", lambda: tool('mpure', 'Expand', '(x+1)^8', 94)),
        ("tex-maclaurin", lambda: tool('fcore', 'Maclaurin series', 'ln(1+x),6', 94)),
        ("tex-partial", lambda: tool('mpure', 'Partial fractions', '3x+5,(x+1)(x+3)', 94)),
        ("tex-byparts", lambda: tool('mcalc', 'Integration by parts', 'x,e^x', 94)),
        ("tex-defint", lambda: tool('mcalc', 'Definite integral', 'x*e^x,0,1', 94)),
        ("tex-inverse", lambda: tool('fcore', 'Inverse 3x3', '2,0,1,1,3,2,1,1,2', 94)),
        ("tex-normal", lambda: tool('mstat', 'Normal P(a<X<b)', '50,10,45,62', 94)),
        ("tex-binomial", lambda: tool('mpure', 'Binomial (a+bx)^n', '2,3,5', 94, 26)),
        ("tex-notes-geo", lambda: notes('notes_mp2', 3, 34)),
        ("tex-notes-trig", lambda: notes('notes_mp2', 9, 26)),
        ("tex-notes-complex", lambda: notes('notes_cp1', 2)),
        ("tex-notes-stats", lambda: notes('notes_ms', 8)),
        ("tex-notes-matrix", lambda: notes('notes_cp2', 0)),
        ("tex-booklet-binom", lambda: booklet(0)),
        ("tex-booklet-maclaurin", lambda: booklet(14, 26)),
        ("tex-booklet-diff", lambda: booklet(5)),
        ("home", lambda: casui.main()),
        ("home-sel", lambda: (press(25, 25, 34), casui.main())),
        ("home-further", lambda: (press(26, 26), casui.main(further=True))),
        # the redesign (docs/redesign.md): type, EXE, tiles, answer page
        ("t-alg-type", lambda: topic_scene('alg', X2_3X_K)),
        ("t-alg-tiles", lambda: topic_scene('alg', X2_3X_K + (95,))),
        ("t-alg-csq", lambda: topic_scene('alg', X2_3X_K + (95, 81))),
        ("t-alg-csq-scroll", lambda: topic_scene('alg', X2_3X_K + (95, 81, 34, 34, 34, 34))),
        ("t-alg-csq-answer", lambda: topic_scene('alg', X2_3X_K + (95, 81, 36))),
        ("t-alg-more", lambda: topic_scene('alg', X2_3X_K + (95, 36))),
        ("t-alg-disc", lambda: topic_scene('alg', X2_3X_K + (95, 71))),
        # 3x^3 - x + 2, TOOLS, Factor theorem (row 3 of More), x = -1
        ("t-alg-prompt", lambda: topic_scene('alg', (83, 41, 44, 83, 25, 85, 41, 84, 82, 95,
                                                       36, 25, 25, 95, 85, 81))),
        ("t-alg-prompt-answer", lambda: topic_scene('alg', (83, 41, 44, 83, 25, 85, 41, 84, 82, 95,
                                                              36, 25, 25, 95, 85, 81, 95))),
        ("t-alg-pair", lambda: topic_scene('alg', (41, 84, 82, 32, 85, 31, 55, 72, 34,
                                                      83, 41, 85, 32, 85, 31, 55, 81, 95))),
        ("t-alg-pair-solve", lambda: topic_scene('alg', (41, 84, 82, 32, 85, 31, 55, 72, 34,
                                                            83, 41, 85, 32, 85, 31, 55, 81, 95, 81))),
        ("t-exp-hidden", lambda: topic_scene('exp', HIDDEN + (95,))),
        ("t-exp-hidden-solve", lambda: topic_scene('exp', HIDDEN + (95, 81))),
        ("t-exp-subu", lambda: topic_scene('exp', HIDDEN + (95, 82))),
        ("t-exp-solve", lambda: topic_scene('exp', TWO_X + (95, 81))),
        ("t-exp-solve-tiles", lambda: topic_scene('exp', TWO_X + (95,))),
        ("t-exp-solve-format", lambda: topic_scene('exp', TWO_X + (95, 81, 94))),
        ("t-exp-xy", lambda: topic_scene('exp', XY + (95,))),
        ("t-exp-xy-rearr", lambda: topic_scene('exp', XY + (95, 81))),
        ("t-exp-log", lambda: topic_scene('exp', LOGEQ + (95, 81))),
        ("t-error", lambda: topic_scene('alg', (41, 84, 31, 55, 31, 55, 95))),
        ("t-settings", lambda: (press(34), __import__('cfg').page())),
        ("t-calc-tiles", lambda: topic_scene('calc', CUBIC_Y + (95,))),
        ("t-calc-stat", lambda: topic_scene('calc', CUBIC_Y + (95, 82))),
        ("t-calc-diff", lambda: topic_scene('calc', XEX + (95, 81))),
        ("t-calc-tangent", lambda: topic_scene('calc', CUBIC_Y + (95, 83, 82, 95))),
        ("t-geo-boxes", lambda: geo_scene(AB_KEYS)),
        ("t-geo-tiles", lambda: geo_scene(AB_KEYS + (95,))),
        ("t-geo-perpbis", lambda: geo_scene(AB_KEYS + (95, 81))),
        ("t-geo-more", lambda: geo_scene(AB_KEYS + (95, 36))),
        ("t-geo-line", lambda: geo_scene((81, 25, 82, 34, 34, 32, 85, 31, 55, 83, 41, 95))),
        ("t-geo-circle", lambda: geo_scene((34, 34, 34, 41, 45, 84, 32, 85, 45, 85, 73, 41, 84, 71,
                                             32, 85, 31, 55, 81, 82, 95, 81))),
        ("maths", lambda: casui.qual_section('Maths  AQA 7357', casui.MATHS)),
        ("maths-p3", lambda: (press(26, 26, 25), casui.qual_section('Maths  AQA 7357', casui.MATHS))),
        ("further", lambda: casui.paper_section('Further  MEI H645', casui.FURTHER)),
        ("tools", lambda: (press(25, 34, 95), casui.qual_section('Maths  AQA 7357', casui.MATHS))),
        # 1 frac 3 right + sqrt 2 right EXE
        ("calc-frac", lambda: calc(81, 42, 83, 25, 84, 43, 82, 25, 95)),
        # x^2 key after a number, e^, then a second line
        ("calc-hist", lambda: calc(82, 45, 84, 83, 95, 81, 42, 82, 25, 84, 46, 81, 25, 95, 94,
                                   85, 82, 95, 82)),
        # type, EXIT, come back: the line and the history are still there
        ("calc-return", lambda: (calc(81, 42, 83, 25, 84, 43, 82, 25, 95, 23, 64, 64), casui.calc_section())),
        # cos( pi frac 3 ) + log_2 16, then sin-1( 0.5 and log( 1000 ) on the next line
        ("calc-funcs", lambda: calc(53, 31, 61, 42, 83, 25, 56, 84, 31, 44, 82, 25, 81, 73, 25, 95,
                                    31, 52, 91, 92, 72, 56, 84, 31, 45, 81, 91, 91, 91)),
        ("calc-edit", lambda: calc(81, 42, 83, 25, 84, 43, 82, 25, 95, 23)),
        ("calc-complex", lambda: calc(55, 82, 84, 83, 31, 63, 56, 75, 55, 81, 85, 31, 63, 56, 95)),
        ("input-empty", lambda: tool_input()),
        ("input-values", lambda: tool_input(81, 51, 85, 83, 51, 82)),
        ("symbols", lambda: (press(35, 25, 34), casui.input_line('CAS', 'f(x)', ''))),
        ("result-answer", lambda: result_scene(0)),
        ("result-working", lambda: result_scene(1)),
        ("cas-int", lambda: casui.result('integrate', 'f(x) = x*e^x', casui._cas_op(2, caslex.parse('x*e^x'), 'x*e^x'))),
        ("flash", lambda: casui.flash('b: unknown x')),
        ("notes", lambda: casui.notes_section()),
        # Pure 7357 > Geometric series (typeset lines), then Core Pure > first topic
        ("notes-page", lambda: (casui._SEL.clear(), press(25, 24, 34, 34, 34, 34, 34, 24),
                                casui.notes_section())),
        ("notes-detail", lambda: (casui._SEL.clear(), press(34, 25, 24, 34, 34, 24, 34, 34),
                                  casui.notes_section())),
        ("plot-cubic", lambda: plot.run([caslex.parse('x^3-3x')], -4, 4, 'y', 'y = x^3-3x')),
    ]


if __name__ == "__main__":
    install()
    want = sys.argv[1:]
    out = []
    for name, fn in _scenes():
        if want and name not in want:
            continue
        reset()
        try:
            fn()
        except Exception as e:
            print(name + ": ERROR " + repr(e))
            import traceback
            traceback.print_exc()
            continue
        paths = save(name)
        flag = ""
        if SCREEN.overflow:
            flag = "  OVERFLOW " + repr(SCREEN.overflow[:3])
        print(name + ": " + str(len(paths)) + " frame(s)" + flag)
        out.extend(paths)
