# casioshot.py - DESKTOP ONLY. Renders the toolkit's screens to PNG files so
# their layout can be inspected without the calculator.
#
# The repo's casioplot.py is a no-op stub, which is what the test harnesses
# want: they assert what a screen SAYS, and drawing would only slow them down.
# But several screens were written from measured font metrics and never looked
# at - the autoscaling graph, the paged result screens, the CATALOG picker grid
# and the caret windowing in a long expression - and layout faults (text off the
# right edge, a row clipped at the bottom, a caret scrolled out of view) are
# invisible to a text assertion.
#
# This module installs a real framebuffer over casioplot, drives a screen with
# scripted key input, and writes each show_screen() to a numbered PNG.
#
#   python3 casioshot.py            # render the standard set into shots/
#   python3 casioshot.py --list     # list the scenes it knows about
#
# It needs Pillow, runs only on a PC, and is NEVER copied to the calculator.
# The glyph widths are matched to casui.char_w rather than to any particular
# font file, so what you see here is what the toolkit BELIEVES it is drawing.
# A string that overflows on screen overflows here too - which is the whole
# point - but the letterforms are not Casio's.
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("casioshot needs Pillow:  pip install pillow")
    sys.exit(2)

W = 384
H = 192
SCALE = 3                     # PNGs are written at 3x so text is readable

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]

# glyph pixel heights that go with casui's small/medium/large advance widths
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
        # the manual: out-of-range coordinates are ignored, not an error
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
        # Advance per character comes from casui.char_w, NOT from the font
        # metrics, so the rendering reproduces what the toolkit thinks the
        # width is. That is what makes an overflow here a real overflow.
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
    # Every module that does "from casioplot import *" gets its OWN module-level
    # binding for each drawing function, so patching casioplot alone is not
    # enough - casrender does exactly that, and the live 2D preview rendered
    # into the no-op stub while everything else drew into the framebuffer. The
    # screen looked blank and the fault was in this file, not the toolkit.
    # So: patch casioplot, then sweep every already-imported project module
    # that has a binding of the same name.
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
    # Each queued key is delivered once and then released, so wait_release and
    # wait_press both terminate. Once the queue runs out, alternate between a
    # held EXIT and nothing: a wait_press that never sees a key, and a
    # wait_release that never sees one released, are both infinite loops, and a
    # renderer that hangs is useless. EXIT also unwinds whatever menu it is in.
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
    # drive one induction proof with the Working setting either way
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


# ------------------------------------------------------------------ scenes --
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
        # the same tool in both modes, so the setting can be looked at rather
        # than only asserted on. Induction is the clearest case: the spot-check
        # caveat under "PROVED" must be in BOTH pictures.
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
