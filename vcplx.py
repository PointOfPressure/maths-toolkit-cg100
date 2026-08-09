# vcplx.py - VISUAL Complex Numbers section for the Maths Toolkit (Further Maths
# Core Pure). casioplot graphics, reuses casui's menu/keyboard/draw helpers and
# the builtin complex type. Argand plot is native (no screen flip). run() is the
# section entry; EXIT returns to the home menu.
import math
import casui
import casutil

_atan2 = casutil.atan2

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

_fn = casutil.fmt
_asknum = casutil.asknum

def _fc(z):
    return casutil.fmtc(z.real, z.imag)

def _askz(name):
    a = _asknum(name + " real part:")
    if a is None:
        return None
    b = _asknum(name + " imag part:")
    if b is None:
        return None
    return complex(a, b)

_show = casutil.show
_w = casutil.w
_warn = casutil.warn

def t_arith():
    z = _askz("z")
    if z is None:
        return
    w = _askz("w")
    if w is None:
        return
    lines = [_w("z = " + _fc(z)), _w("w = " + _fc(w)),
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
    lines = [_w("z = " + _fc(z)), "|z| = " + _fn(r), "arg = " + _fn(th) + " rad"]
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
    lines = [_w("z = " + _fc(z)), "r = " + _fn(r), "theta = " + _fn(th) + " rad"]
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
    _show("from polar", [_w("r = " + _fn(r)), _w("theta = " + _fn(th)), "z = " + _fc(z)])

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
    _show("z^n  (De Moivre)", [_w("z = " + _fc(z)), "z^" + str(n) + " = " + _fc(zn),
                               _w("r^n = " + _fn(rn)), _w("n*theta = " + _fn(n * th) + " rad")])

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
    lines = [_w("z = " + _fc(z)), "each |root| = " + _fn(rr)]
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

def t_loci():
    # Loci and regions in the Argand diagram. The three the specification
    # names are |z - a| = r (a circle), |z - a| = |z - b| (the perpendicular
    # bisector of a and b), and arg(z - a) = theta (a HALF-line, not a whole
    # line - the half that matters is the one the argument actually points
    # along, which is the detail most often lost).
    kind = casui.menu('Locus of z', ['|z - a| = r        circle',
                                     '|z - a| = |z - b|  bisector',
                                     'arg(z - a) = th    half-line',
                                     '|z - a| <= r       region'])
    if kind == -1:
        return
    lines = []
    a = _askz('a')
    if a is None:
        return
    cx = a.real
    cy = a.imag
    r = 0.0
    b = None
    th = 0.0
    if kind == 0 or kind == 3:
        r = casutil.asknum('r (radius)')
        if r is None or r < 0:
            _show('Loci', [_warn('The radius must be at least 0.')])
            return
        lines.append(_w('|z - (' + _fc(a) + ')| ' + ('<=' if kind == 3 else '=') +
                     ' ' + casutil.fmt(r)))
        lines.append('')
        lines.append(_w('This is the set of points whose'))
        lines.append(_w('distance from ' + _fc(a) + ' is ' +
                     ('at most ' if kind == 3 else 'exactly ') + casutil.fmt(r) + '.'))
        lines.append('')
        lines.append('circle centre ' + _fc(a) + ', radius ' + casutil.fmt(r))
        lines.append('cartesian: (x - ' + casutil.fmt(cx) + ')^2 + (y - ' +
                     casutil.fmt(cy) + ')^2 ' + ('<=' if kind == 3 else '=') +
                     ' ' + casutil.fmt(r * r))
        if kind == 3:
            lines.append(_warn('(a filled disc, boundary included)'))
        d = math.sqrt(cx * cx + cy * cy)
        lines.append('')
        lines.append('greatest |z| on it = ' + casutil.fmt(d + r))
        lines.append('least |z| on it    = ' + casutil.fmt(d - r if d > r else 0.0))
    elif kind == 1:
        b = _askz('b')
        if b is None:
            return
        if abs(b - a) < 1e-12:
            _show('Loci', [_warn('a and b are the same point, so'),
                           _warn('every z is equidistant from them.')])
            return
        mx = (a.real + b.real) / 2.0
        my = (a.imag + b.imag) / 2.0
        dx = b.real - a.real
        dy = b.imag - a.imag
        lines.append(_w('|z - (' + _fc(a) + ')| = |z - (' + _fc(b) + ')|'))
        lines.append('')
        lines.append(_w('The points equidistant from a and b:'))
        lines.append('the PERPENDICULAR BISECTOR of the')
        lines.append('line joining them.')
        lines.append('')
        lines.append('midpoint (' + casutil.fmt(mx) + ', ' + casutil.fmt(my) + ')')
        if abs(dy) < 1e-12:
            lines.append('vertical line x = ' + casutil.fmt(mx))
        else:
            m = -dx / dy
            c = my - m * mx
            lines.append(_w('gradient of ab = ' + casutil.fmt(dy / dx)) if abs(dx) > 1e-12
                         else _w('ab is vertical'))
            lines.append(_w('bisector gradient = ' + casutil.fmt(m)))
            lines.append('y = ' + casutil.fmt(m) + 'x + ' + casutil.fmt(c))
    else:
        thd = casutil.asknum('theta (degrees)')
        if thd is None:
            return
        th = casutil.rad(thd)
        lines.append(_w('arg(z - (' + _fc(a) + ')) = ' + casutil.fmt(thd) + ' deg'))
        lines.append('')
        lines.append('A HALF-LINE from ' + _fc(a) + ', at')
        lines.append(casutil.fmt(thd) + ' degrees to the positive real')
        lines.append(_warn('direction. The point ' + _fc(a) + ' itself is'))
        lines.append(_warn('NOT included - arg(0) is undefined.'))
        lines.append('')
        if abs(math.cos(th)) < 1e-12:
            lines.append('cartesian: x = ' + casutil.fmt(cx) +
                         (', y > ' if math.sin(th) > 0 else ', y < ') + casutil.fmt(cy))
        else:
            m = math.tan(th)
            lines.append('cartesian: y - ' + casutil.fmt(cy) + ' = ' +
                         casutil.fmt(m) + '(x - ' + casutil.fmt(cx) + ')')
            lines.append(_warn('but only the half with x ' +
                         ('>' if math.cos(th) > 0 else '<') + ' ' + casutil.fmt(cx)))
    _show('Locus', lines)
    # ---- draw it ----
    span = 1.0
    for v in (abs(cx), abs(cy), r):
        if v > span:
            span = v
    if b is not None:
        for v in (abs(b.real), abs(b.imag)):
            if v > span:
                span = v
    span *= 1.6
    fr = casutil.frame(-span, span, -span, span)
    casutil.axes(fr, 'Argand diagram', 'Re', 'Im')
    if kind == 0 or kind == 3:
        n = 180
        i = 0
        prev = None
        while i <= n:
            t = 2.0 * math.pi * i / n
            px = cx + r * math.cos(t)
            py = cy + r * math.sin(t)
            if prev is not None:
                casutil.seg(fr, prev[0], prev[1], px, py, casui.ACC)
            prev = (px, py)
            i += 1
        if kind == 3:
            # shade the interior with a coarse grid of dots
            i = -12
            while i <= 12:
                j = -12
                while j <= 12:
                    px = cx + r * i / 12.0
                    py = cy + r * j / 12.0
                    if (px - cx) ** 2 + (py - cy) ** 2 <= r * r:
                        casutil.dot(fr, px, py, casui.HL)
                    j += 1
                i += 1
        casutil.marker(fr, cx, cy, casui.RED, 2)
    elif kind == 1:
        casutil.marker(fr, a.real, a.imag, casui.RED, 2)
        casutil.marker(fr, b.real, b.imag, casui.RED, 2)
        casutil.seg(fr, a.real, a.imag, b.real, b.imag, casui.GREY)
        mx = (a.real + b.real) / 2.0
        my = (a.imag + b.imag) / 2.0
        dx = b.real - a.real
        dy = b.imag - a.imag
        L = math.sqrt(dx * dx + dy * dy)
        ux = -dy / L
        uy = dx / L
        k = 4.0 * span
        casutil.seg(fr, mx - ux * k, my - uy * k, mx + ux * k, my + uy * k, casui.ACC)
    else:
        k = 4.0 * span
        casutil.seg(fr, cx, cy, cx + k * math.cos(th), cy + k * math.sin(th), casui.ACC)
        casutil.marker(fr, cx, cy, casui.RED, 2)
    casutil.chart_hold('Re right, Im up')


def t_demoivre_id():
    # de Moivre gives the multiple-angle identities: expanding (cos t + i sin t)^n
    # by the binomial theorem and matching real and imaginary parts turns
    # cos(nt) and sin(nt) into polynomials in cos t and sin t.
    n = casutil.askint('n in (cos t + i sin t)^n', 2, 8)
    if n is None:
        return
    lines = [_w('(cos t + i sin t)^' + str(n) + ' = cos ' + str(n) + 't + i sin ' + str(n) + 't'),
             _w('by de Moivre. Expanding the left side'),
             _w('with the binomial theorem and matching'),
             _w('real and imaginary parts:'), '']
    cos_terms = []
    sin_terms = []
    k = 0
    while k <= n:
        c = casutil.ncr(n, k)
        # i^k cycles 1, i, -1, -i
        m = k % 4
        body = ''
        if n - k > 0:
            body += 'c^' + str(n - k) if n - k > 1 else 'c'
        if k > 0:
            body += ('s^' + str(k) if k > 1 else 's')
        if body == '':
            body = '1'
        piece = (str(c) + body) if c != 1 else body
        if m == 0:
            cos_terms.append(('+', piece))
        elif m == 1:
            sin_terms.append(('+', piece))
        elif m == 2:
            cos_terms.append(('-', piece))
        else:
            sin_terms.append(('-', piece))
        k += 1

    def join(ts):
        out = ''
        for sign, piece in ts:
            if out == '':
                out = ('-' + piece) if sign == '-' else piece
            else:
                out += ' ' + sign + ' ' + piece
        return out if out else '0'

    lines.append('cos ' + str(n) + 't = ' + join(cos_terms))
    lines.append('sin ' + str(n) + 't = ' + join(sin_terms))
    lines.append('')
    lines.append('with c = cos t and s = sin t.')
    lines.append('')
    lines.append(_w('Use s^2 = 1 - c^2 to write cos ' + str(n) + 't'))
    lines.append(_w('in cosines alone.'))
    # numeric check at one angle, so the expansion can be trusted
    t = 0.7
    c = math.cos(t)
    s = math.sin(t)
    cv = 0.0
    sv = 0.0
    k = 0
    while k <= n:
        term = casutil.ncr(n, k) * (c ** (n - k)) * (s ** k)
        m = k % 4
        if m == 0:
            cv += term
        elif m == 1:
            sv += term
        elif m == 2:
            cv -= term
        else:
            sv -= term
        k += 1
    lines.append('')
    lines.append(_warn('check at t = 0.7 rad:'))
    lines.append(_warn('  cos ' + str(n) + 't = ' + casutil.fmt(math.cos(n * t), 6)))
    lines.append(_warn('  expansion  = ' + casutil.fmt(cv, 6)))
    lines.append(_warn('  sin ' + str(n) + 't = ' + casutil.fmt(math.sin(n * t), 6)))
    lines.append(_warn('  expansion  = ' + casutil.fmt(sv, 6)))
    _show('de Moivre identities', lines)


TOOLS = [
    ("Arithmetic z, w", t_arith),
    ("Modulus & argument", t_modarg),
    ("Polar / exp form", t_topolar),
    ("From polar (r,theta)", t_frompolar),
    ("Power z^n (De Moivre)", t_power),
    ("nth roots of z", t_roots),
    ("Quadratic complex roots", t_quad),
    ("Argand plot", t_argand),
    ("Loci in the Argand plane", t_loci),
    ("de Moivre identities", t_demoivre_id),
]

def run():
    casutil.run_tools("COMPLEX NUMBERS", TOOLS)
