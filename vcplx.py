# vcplx.py - VISUAL Complex Numbers section for the Maths Toolkit (Further Maths
# Core Pure). casioplot graphics, reuses casui's menu/keyboard/draw helpers and
# the builtin complex type. Argand plot is native (no screen flip). run() is the
# section entry; EXIT returns to the home menu.
import math
import casui
import caslex
import caseng

def _atan2(y, x):
    if x > 0:
        return math.atan(y / x)
    if x < 0:
        if y >= 0:
            return math.atan(y / x) + math.pi
        return math.atan(y / x) - math.pi
    if y > 0:
        return math.pi / 2
    if y < 0:
        return -math.pi / 2
    return 0.0

_PIFRAC = [
    (0.0, "0"), (1.0, "pi"), (-1.0, "-pi"), (0.5, "pi/2"), (-0.5, "-pi/2"),
    (1.0 / 3, "pi/3"), (-1.0 / 3, "-pi/3"), (2.0 / 3, "2pi/3"), (-2.0 / 3, "-2pi/3"),
    (0.25, "pi/4"), (-0.25, "-pi/4"), (0.75, "3pi/4"), (-0.75, "-3pi/4"),
    (1.0 / 6, "pi/6"), (-1.0 / 6, "-pi/6"), (5.0 / 6, "5pi/6"), (-5.0 / 6, "-5pi/6"),
]

def _argpi(th):
    f = th / math.pi
    for v, lab in _PIFRAC:
        if abs(f - v) < 1e-4:
            return lab
    return ""

def _fn(x):
    r = round(x, 4)
    if r == int(r):
        return str(int(r))
    return str(r)

def _fc(z):
    a = z.real
    b = z.imag
    if abs(b) < 1e-9:
        return _fn(a)
    if abs(a) < 1e-9:
        return _fn(b) + "i"
    sgn = "+" if b >= 0 else "-"
    return _fn(a) + sgn + _fn(abs(b)) + "i"

def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None

def _askz(name):
    a = _asknum(name + " real part:")
    if a is None:
        return None
    b = _asknum(name + " imag part:")
    if b is None:
        return None
    return complex(a, b)

def _show(title, lines):
    casui.result_screen(title, lines)

def t_arith():
    z = _askz("z")
    if z is None:
        return
    w = _askz("w")
    if w is None:
        return
    lines = ["z = " + _fc(z), "w = " + _fc(w),
             "z+w = " + _fc(z + w), "z-w = " + _fc(z - w),
             "z*w = " + _fc(z * w)]
    if w != 0:
        lines.append("z/w = " + _fc(z / w))
    _show("z and w", lines)

def t_modarg():
    z = _askz("z")
    if z is None:
        return
    r = abs(z)
    th = _atan2(z.imag, z.real)
    lines = ["z = " + _fc(z), "|z| = " + _fn(r), "arg = " + _fn(th) + " rad"]
    lab = _argpi(th)
    if lab:
        lines.append("    = " + lab)
    lines.append("    = " + _fn(th * 180 / math.pi) + " deg")
    lines.append("conj = " + _fc(complex(z.real, -z.imag)))
    _show("modulus & argument", lines)

def t_topolar():
    z = _askz("z")
    if z is None:
        return
    r = abs(z)
    th = _atan2(z.imag, z.real)
    lines = ["z = " + _fc(z), "r = " + _fn(r), "theta = " + _fn(th) + " rad"]
    lab = _argpi(th)
    if lab:
        lines.append("   = " + lab)
    lines.append("z = r(cos t + i sin t)")
    lines.append("z = r e^(i t)")
    _show("polar / exp form", lines)

def t_frompolar():
    r = _asknum("r (modulus):")
    if r is None:
        return
    th = _asknum("theta in radians:")
    if th is None:
        return
    z = complex(r * math.cos(th), r * math.sin(th))
    _show("from polar", ["r = " + _fn(r), "theta = " + _fn(th), "z = " + _fc(z)])

def t_power():
    z = _askz("z")
    if z is None:
        return
    n = _asknum("power n:")
    if n is None:
        return
    n = int(round(n))
    r = abs(z)
    if r == 0 and n <= 0:
        return
    th = _atan2(z.imag, z.real)
    rn = r ** n
    zn = complex(rn * math.cos(n * th), rn * math.sin(n * th))
    _show("z^n  (De Moivre)", ["z = " + _fc(z), "z^" + str(n) + " = " + _fc(zn),
                               "r^n = " + _fn(rn), "n*theta = " + _fn(n * th) + " rad"])

def t_roots():
    z = _askz("z")
    if z is None:
        return
    n = _asknum("n (number of roots):")
    if n is None:
        return
    n = int(round(n))
    if n < 1:
        return
    r = abs(z)
    th = _atan2(z.imag, z.real)
    rr = r ** (1.0 / n)
    lines = ["z = " + _fc(z), "each |root| = " + _fn(rr)]
    k = 0
    while k < n:
        ang = (th + 2 * math.pi * k) / n
        lines.append(str(k) + ": " + _fc(complex(rr * math.cos(ang), rr * math.sin(ang))))
        k += 1
    _show("nth roots (" + str(n) + "-gon)", lines)

def t_quad():
    a = _asknum("a (z^2 coeff):")
    if a is None or a == 0:
        return
    b = _asknum("b (z coeff):")
    if b is None:
        return
    c = _asknum("c (constant):")
    if c is None:
        return
    disc = b * b - 4 * a * c
    if disc >= 0:
        s = math.sqrt(disc)
        _show("a z^2 + b z + c = 0", ["real roots:", "z1 = " + _fn((-b + s) / (2 * a)),
                                      "z2 = " + _fn((-b - s) / (2 * a))])
    else:
        s = math.sqrt(-disc)
        re = -b / (2 * a)
        im = s / (2 * a)
        _show("a z^2 + b z + c = 0", ["complex conj roots:", "z1 = " + _fc(complex(re, im)),
                                      "z2 = " + _fc(complex(re, -im))])

def t_argand():
    pts = []
    while True:
        z = _askz("point " + str(len(pts) + 1))
        if z is None:
            break
        pts.append(z)
        if len(pts) >= 8:
            break
    if not pts:
        return
    sp = casui.set_pixel
    mx = 1.0
    for z in pts:
        if abs(z.real) > mx:
            mx = abs(z.real)
        if abs(z.imag) > mx:
            mx = abs(z.imag)
    scl = 84.0 / mx
    cx = 192
    cy = 96
    casui.clear_screen()
    x = 0
    while x < 384:
        sp(x, cy, (170, 170, 180))
        x += 1
    y = 0
    while y < 192:
        sp(cx, y, (170, 170, 180))
        y += 1
    casui.draw_string(2, 2, "Argand   Re ->,  Im up", casui.ACC, "small")
    for z in pts:
        px = int(cx + z.real * scl)
        py = int(cy - z.imag * scl)
        dx = -2
        while dx <= 2:
            dy = -2
            while dy <= 2:
                xx = px + dx
                yy = py + dy
                if 0 <= xx < 384 and 0 <= yy < 192:
                    sp(xx, yy, (210, 60, 60))
                dy += 1
            dx += 1
    casui.draw_string(2, 178, "any key to return", casui.GREY, "small")
    casui.show_screen()
    casui.wait_release()
    casui.wait_press()
    casui.wait_release()

TOOLS = [
    ("Arithmetic z, w", t_arith),
    ("Modulus & argument", t_modarg),
    ("Polar / exp form", t_topolar),
    ("From polar (r,theta)", t_frompolar),
    ("Power z^n (De Moivre)", t_power),
    ("nth roots of z", t_roots),
    ("Quadratic complex roots", t_quad),
    ("Argand plot", t_argand),
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu("COMPLEX NUMBERS", labels)
        if c == -1:
            return
        TOOLS[c][1]()
