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
        for ch in str(s):
            self.draw.text((pen, y), ch, font=f, fill=col)
            pen += casrender.cw(ch, size)
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

    return [
        ("home", lambda: casui.main()),
        ("home-sel", lambda: (press(25, 25, 34), casui.main())),
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
