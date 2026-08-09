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
    "/Library/Fonts/Arial.ttf",
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
        import casui
        pen = x
        f = self.fonts.get(size, self.fonts["medium"])
        for ch in str(s):
            self.draw.text((pen, y), ch, font=f, fill=col)
            pen += casui.char_w(ch, size)
        end = pen
        if end > W:
            self.overflow.append((len(self.frames), y, str(s), end - W))

    def show(self):
        self.frames.append(self.img.copy())


SCREEN = Screen()
KEYS = []


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
    for mod in list(sys.modules.values()):
        if mod is None or mod is casioplot:
            continue
        f = getattr(mod, "__file__", None)
        if not f or not os.path.samefile(os.path.dirname(os.path.abspath(f)),
                                         os.path.dirname(os.path.abspath(__file__))):
            continue
        for name in PATCH:
            if hasattr(mod, name):
                setattr(mod, name, PATCH[name]())
    for name in extra:
        __import__(name)
        mod = sys.modules[name]
        for pname in PATCH:
            if hasattr(mod, pname):
                setattr(mod, pname, PATCH[pname]())


_TOGGLE = [False]

def _getkey():
    if KEYS:
        k = KEYS[0]
        if k is None:
            KEYS.pop(0)
            return 0
        KEYS[0] = None
        return k
    _TOGGLE[0] = not _TOGGLE[0]
    return 22 if _TOGGLE[0] else 0


def press(*codes):
    for c in codes:
        KEYS.append(c)
        KEYS.append(None)


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


def reset():
    _TOGGLE[0] = False
    SCREEN.frames = []
    SCREEN.overflow = []
    del KEYS[:]
    SCREEN.clear()


def _both_modes(show):
    import casui
    import proof
    real = casui.SHOW_WORKING
    ask = casui.input_expr
    casui.input_expr = lambda p: {"u(r) = (type r as n)": "n",
                                  "claimed S(n) =": "n(n+1)/2"}.get(p)
    casui.SHOW_WORKING = show
    try:
        proof.t_induction_sum()
    finally:
        casui.SHOW_WORKING = real
        casui.input_expr = ask


def _scenes():
    import casui
    import caslex
    return [
        ("graph-1overx", lambda: casui.graph(caslex.parse("1/x"))),
        ("graph-cubic", lambda: casui.graph(caslex.parse("x^3-3x"))),
        ("graph-tan", lambda: casui.graph(caslex.parse("tan(x)"))),
        ("menu", lambda: casui.menu("MATHS TOOLKIT",
                                    ["Calculate", "Calculus & Algebra",
                                     "A-Level Maths", "Further Maths",
                                     "Angle mode: RADIANS",
                                     "Working: SHOWN"])),
        ("menu-standard-bodies", lambda: casui.menu('Standard bodies',
            ['Rod, length L', 'Triangular lamina, height h',
             'Circular arc, r, half-angle A', 'Semicircular arc, r',
             'Circular sector, r, half-angle A', 'Semicircular lamina, r',
             'Solid hemisphere, r', 'Hollow hemisphere, r',
             'Solid cone or pyramid, height h', 'Hollow cone, height h'])),
        ("intro-recurrence", lambda: casui.result_screen(
            'First order recurrence',
            ['u(n+1) = a u(n) + f(n)',
             'Solved as A a^n plus a particular',
             'term whose shape follows f(n).'])),
        ("working-shown", lambda: _both_modes(True)),
        ("working-hidden", lambda: _both_modes(False)),
        ("result-paged", lambda: casui.result_screen(
            "A long result",
            ["line " + str(i) + ": some result text that is moderately long"
             for i in range(1, 17)])),
        ("preview-frac", lambda: casui.draw_input(
            "Type an expression:", "(x+1)/(x-2)", 5, False, False, False, 0)),
        ("preview-root", lambda: casui.draw_input(
            "Type an expression:", "sqrt(x^2+1)/3", 4, False, False, False, 0)),
        ("caret-long", lambda: casui.draw_input(
            "Type an expression:", "sin(2x)+cos(3x)-tan(x)/sqrt(x^2+1)+exp(-x)",
            21, False, False, False, 0)),
        ("picker", lambda: casui.draw_input(
            "Type an expression:", "2x+", 3, False, False, True, 5)),
    ]


def main(argv):
    install("casrender", "casui")
    scenes = _scenes()
    if "--list" in argv:
        for name, fn in scenes:
            print(name)
        return 0
    bad = 0
    for name, fn in scenes:
        reset()
        fn()
        if not SCREEN.frames:
            SCREEN.show()
        paths = save(name)
        note = ""
        if SCREEN.overflow:
            note = "  OVERFLOW " + str(SCREEN.overflow)
            bad += 1
        print("%-16s %d frame(s)  %s%s" % (name, len(paths), paths[0], note))
    print("")
    print("wrote " + str(len(scenes)) + " scenes to shots/" +
          ("" if not bad else "; " + str(bad) + " overflowed the 384px width"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv[1:]))
