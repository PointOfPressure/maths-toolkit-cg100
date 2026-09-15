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
    for c in codes:
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
    import casutil
    import plot
    quad = ('Quadratic', 'a,b,c', lambda a, b, c: [
        'x = 1/2 + i*sqrt(3)/2', 'x = 1/2 - i*sqrt(3)/2',
        ('m', caslex.parse('(1+sqrt(3)i)/2')),
        ('!', 'no real roots'),
        ('w', 'disc = b^2 - 4ac = -3'), ('w', 'vertex (1/2, 3/4)')])
    tools = [quad, ('Simultaneous', 'a1,b1,c1,a2,b2,c2', None), ('Inequality', 'a,b,c', None)]
    sections = [(chr(65 + i), 'Section title number ' + str(i + 1), tools) for i in range(19)]

    def result_scene(mode):
        import casioshot
        casioshot.press(*([94] * mode))
        casui.result('Quadratic', '1,-1,1', lambda: quad[2](1, -1, 1))

    def input_scene(text, spec, label):
        import casioshot
        keys = []
        for ch in text:
            for code in casui.UNSHIFT:
                if casui.UNSHIFT[code] == ch:
                    keys.append(code)
                    break
        casioshot.press(*keys)
        casui.input_line(label, spec, '')

    return [
        ("home", lambda: casui.menu('MATHS TOOLKIT  AQA 7357 + 7367',
                                    ['Calculate', 'CAS  f(x)', 'Maths 7357', 'Further 7367', 'Formulae', 'Angle: RAD'])),
        ("sections", lambda: casui.menu('MATHS 7357', [c + '  ' + t for c, t, tl in sections], 4)),
        ("tools", lambda: casui.menu('B Algebra and functions', [t[0] for t in tools])),
        ("input-empty", lambda: input_scene('', 'a,b,c', 'Quadratic')),
        ("input-values", lambda: input_scene('1,-3,2', 'a,b,c', 'Quadratic')),
        ("input-matrix", lambda: input_scene('1,2,3,4,5,6,7,8,9', 'A[3x3]', 'Determinant')),
        ("result-answer", lambda: result_scene(0)),
        ("result-working", lambda: result_scene(1)),
        ("result-full", lambda: result_scene(2)),
        ("calc", lambda: casui.result('Calculate', '(2+3i)/(1-i)',
                                      lambda: casui._calc_lines(caslex.parse('(2+3i)/(1-i)'), casutil.ev(caslex.parse('(2+3i)/(1-i)'))))),
        ("calc-frac", lambda: casui.result('Calculate', 'sqrt(8)/(1/3+1/6)',
                                           lambda: casui._calc_lines(caslex.parse('sqrt(8)/(1/3+1/6)'), casutil.ev(caslex.parse('sqrt(8)/(1/3+1/6)'))))),
        ("cas-int", lambda: casui.result('integrate', 'x*e^x', casui._cas_op(2, caslex.parse('x*e^x'), 'x*e^x'))),
        ("cas-partial", lambda: casui.result('partial fractions', '(3x+5)/((x-1)(x+2))',
                                             casui._cas_op(9, caslex.parse('(3x+5)/((x-1)(x+2))'), ''))),
        ("plot-cubic", lambda: plot.run([caslex.parse('x^3-3x')], -4, 4, 'y', 'y = x^3-3x')),
        ("plot-trace", lambda: (press(24, 25, 25, 25), plot.run([caslex.parse('sin(x)'), caslex.parse('cos(x)')], -6, 6, 'y', 'sin, cos'))),
        ("plot-polar", lambda: plot.run([caslex.parse('1+cos(x)')], 0, 1, 'polar', 'r = 1+cos(th)')),
        ("plot-points", lambda: plot.run([(1, 2), (2, 3.5), (3, 3), (4, 5), (5, 6.2)], 0, 1, 'points', 'scatter')),
        ("flash", lambda: (casui._draw_input('Quadratic', 'a,b,c', list('1,x'), 3, False, False, 0), casui.flash('b: unknown x'))),
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
