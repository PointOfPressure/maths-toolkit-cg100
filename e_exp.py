# Exp and logs actions: the log laws both ways, exact values of logs, a
# model through two points and its straight-line form, and dy/dx of an
# equation in x and y. Solving lives in e_solve (logs first, then the
# decimal).
import caseng
import caspoly
import eng
import recog
from eng import S, N, ZERO, ONE, txt, eq, val, has

def _side(F):
    r = F.rows[0]
    if r.rel and r.name is None:
        return [r.lhs, r.rhs]
    return [r.f]

def _first(F):
    r = F.rows[0]
    if r.rel and r.name is None:
        return eq(r.lhs, r.rhs)
    return txt(r.f)

# ---- log laws --------------------------------------------------------------------------------

def _combine1(t, lines, v):
    # one side's logs as one log: c log g -> log g^c, then + and -
    import e_solve
    logs, rest = e_solve.logterms(t, v)
    if not logs:
        return t
    bases = [b for c, b, g in logs]
    for b in bases:
        if b != bases[0]:
            raise ValueError('logs with different bases: ' + txt(bases[0]) + ' and ' + txt(b))
    b = bases[0]
    pw = []
    shown = False
    for c, bb, g in logs:
        n, a = eng.neg(c)
        if a != ONE:
            shown = True
        pw.append((eng.logto(b, g if a == ONE else ('^', g, a)), -1 if n else 1))
    if shown and len(logs) > 1:
        lines.append('= ' + txt(eng.build(pw + rest), False))
    G = e_solve.combine(logs)
    one = eng.logto(b, G)
    Gs = eng.nice(G)
    lines.append('= ' + txt(eng.build([(one, 1)] + rest), False))
    out = eng.logto(b, Gs)
    if txt(Gs) != txt(G):
        lines.append('= ' + txt(eng.build([(out, 1)] + rest), False))
    tl = eng.tidylog(out)
    if tl != out:
        out = tl
        lines.append('= ' + txt(eng.build([(out, 1)] + rest), False))
    return eng.build([(out, 1)] + rest)

def combine(F, arg, vals):
    v = F.var
    lines = [_first(F)]
    sides = _side(F)
    if len(sides) == 1:
        t = _combine1(sides[0], lines, v)
        if lines[-1][2:] == txt(t, False):
            lines.pop()
        lines.append(eng.box('', S(t)) if F.kind == 'num' else eng.boxs('', txt(t, False)))
        return lines
    sub = []
    a = _combine1(sides[0], sub, v)
    b = _combine1(sides[1], sub, v)
    lines.append(eng.boxs('', eq(a, b)))
    return lines

def _expand1(t, v):
    # log of a product, quotient or power -> sums of simple logs
    k = t[0]
    if k in ('ln', 'log', 'logb'):
        b = t[1] if k == 'logb' else (('v', 'e') if k == 'ln' else N(10))
        a = t[2] if k == 'logb' else t[1]
        out = []
        for f, e in recog.factors(a, 1, []):
            c = N(e)
            g = f
            if f[0] == '^' and not has(f[2], 'zz'):
                c = S(('*', N(e), f[2]))
                g = f[1]
            elif f[0] == 'sqrt':
                c = S(('*', N(e), ('/', ONE, N(2))))
                g = f[1]
            elif f[0] == 'exp' and b == ('v', 'e'):
                out.append((S(('*', N(e), f[1])), 1))
                continue
            lg = eng.tidylog(eng.logto(b, g))
            out.append((eng.mul(c, lg) if lg != ONE else c, 1))
        return eng.build(out)
    if k in ('+', '-', 'neg', '*'):
        return (k,) + tuple([_expand1(c, v) for c in t[1:]])
    return t

def expandlogs(F, arg, vals):
    v = F.var
    lines = [_first(F)]
    sides = _side(F)
    outs = [_expand1(s, v) for s in sides]
    t = outs[0] if len(outs) == 1 else None
    lines.append(eng.boxs('', txt(outs[0]) if len(outs) == 1 else eq(outs[0], outs[1])))
    return lines

def evaluate(F, arg, vals):
    f = F.rows[0].f
    lines = [txt(f)]
    t = f
    if F.logs:
        sub = []
        try:
            t = _combine1(f, sub, F.var)
            lines += sub
        except ValueError:
            pass
    t = eng.nice(eng.tidylog(t))
    if lines[-1] == '= ' + txt(t):
        lines.pop()
    lines.append(eng.box('= ', t))
    return lines

# ---- models --------------------------------------------------------------------------------

def model(F, arg, vals):
    r = F.rows[0]
    nm = r.name
    v = F.var
    c, k = F.consts
    (x1, y1), (x2, y2) = (vals[0], vals[1]), (vals[2], vals[3])
    lines = [nm + ' = ' + txt(r.f)]
    dec = F.dec
    for t in vals:
        if recog.hasfloat(t) or (t[0] == '^' and val(t) is not None and val(t) != int(val(t))):
            dec = True
    if dec:
        # decimals typed: the working in decimals (6 s.f.)
        x1, y1, x2, y2 = [_num(t) for t in vals]
    e1 = caseng.subst(caseng.subst(r.f, v, x1), nm, y1)
    e2 = caseng.subst(caseng.subst(r.f, v, x2), nm, y2)
    lines.append(txt(y1) + ' = ' + txt(e1))
    lines.append(txt(y2) + ' = ' + txt(e2))
    if F.model == 'aekt':
        dk = S(('-', x2, x1))
        ratio = S(('/', y2, y1)) if not dec else _num(S(('/', y2, y1)))
        lines.append(txt(ratio) + ' = e^(' + txt(eng.mul(dk, ('v', k))) + ')')
        kv = S(('/', ('ln', ratio), dk))
        co = _kco(_expo(r.f), k, v)
        if co != ONE:
            kv = S(('/', kv, co))
        lines.append(k + ' = ' + txt(kv if not dec else _num(kv)))
        cv = S(('/', y1, caseng.subst(caseng.subst(_expfac(r.f), k, kv), v, x1)))
    elif F.model == 'kbx':
        dx = S(('-', x2, x1))
        ratio = S(('/', y2, y1)) if not dec else _num(S(('/', y2, y1)))
        lines.append(k + '^' + _br(dx) + ' = ' + txt(ratio))
        bv = S(('^', ratio, ('/', ONE, dx)))
        lines.append(k + ' = ' + txt(bv if not dec else _num(bv)))
        kv = bv
        cv = S(('/', y1, ('^', bv, x1)))
    else:
        ry = S(('/', y2, y1)) if not dec else _num(S(('/', y2, y1)))
        rx = S(('/', x2, x1)) if not dec else _num(S(('/', x2, x1)))
        lines.append(_br(rx) + '^' + k + ' = ' + txt(ry))
        nv = S(('/', ('ln', ry), ('ln', rx)))
        lines.append(k + ' = ' + txt(nv if not dec else _num(nv)))
        kv = nv
        cv = S(('/', y1, ('^', x1, nv)))
    lines.append(c + ' = ' + txt(cv if not dec else _num(cv)))
    lines.append(eng.box(c + ' = ', cv, not dec))
    lines.append(eng.box(k + ' = ', kv, not dec))
    fit = caseng.subst(caseng.subst(r.f, c, _short(cv)), k, _short(kv))
    lines.append(nm + ' = ' + txt(fit))
    return lines

def _num(t):
    # a value to 6 s.f. as a number tree
    v = val(t)
    if v is None or isinstance(v, complex):
        return t
    if v == int(v) and abs(v) < 1e12:
        return N(int(v))
    return N(float(eng.sf(v, 6)))

def _short(t):
    # a fitted constant to 4 s.f. for the model line
    v = val(t)
    if v is None or isinstance(v, complex):
        return t
    if v == int(v):
        return N(int(v))
    return N(float(eng.sf(v, 4)))

def _br(t):
    s = txt(t)
    return s if eng._simple(s) else '(' + s + ')'

def _brt(t):
    return _br(t)

def _expo(f):
    for g, e in recog.factors(f, 1, []):
        if g[0] == 'exp':
            return g[1]
    return ONE

def _expfac(f):
    for g, e in recog.factors(f, 1, []):
        if g[0] == 'exp':
            return g
    return ONE

def _kco(E, k, v):
    # E = k v times a number (e^(2kt)): that number
    r = S(('/', E, ('*', ('v', k), ('v', v))))
    return r if not has(r, k) and not has(r, v) else ONE

def loglin(F, arg, vals):
    r = F.rows[0]
    nm = r.name
    v = F.var
    c, k = F.consts
    lines = [nm + ' = ' + txt(r.f)]
    if F.model == 'aekt':
        lines.append('ln ' + nm + ' = ln(' + c + ' e^(' + txt(_expo(r.f)) + '))')
        lines.append(eng.boxs('', 'ln ' + nm + ' = ' + txt(_expo(r.f)) + ' + ln ' + c))
        lines.append('ln ' + nm + ' against ' + v + ': a straight line, gradient ' +
                     txt(S(('/', _expo(r.f), ('v', v)))) + ', intercept ln ' + c)
    elif F.model == 'kbx':
        lines.append('log ' + nm + ' = log(' + c + ' ' + k + '^' + v + ')')
        lines.append(eng.boxs('', 'log ' + nm + ' = ' + v + ' log ' + k + ' + log ' + c))
        lines.append('log ' + nm + ' against ' + v + ': a straight line, gradient log ' + k +
                     ', intercept log ' + c)
    else:
        lines.append('log ' + nm + ' = log(' + c + ' ' + v + '^' + k + ')')
        lines.append(eng.boxs('', 'log ' + nm + ' = ' + k + ' log ' + v + ' + log ' + c))
        lines.append('log ' + nm + ' against log ' + v + ': a straight line, gradient ' + k +
                     ', intercept log ' + c)
    return lines

# ---- implicit dy/dx ---------------------------------------------------------------------------------

def implicit(F, arg, vals):
    import cascalc
    r = F.rows[0]
    x, y = F.vars2 if len(F.vars2) == 2 else ('x', 'y')
    E = S(('-', r.lhs, r.rhs))
    lines = [eq(r.lhs, r.rhs)]
    fx = cascalc.tidy(caseng.diff(E, x))
    fy = cascalc.tidy(caseng.diff(E, y))
    if fy == ZERO:
        raise ValueError('no ' + y + ' to differentiate')
    lines.append('d/d' + x + ': ' + txt(fx) + ' + (' + txt(fy) + ') dy/d' + x + ' = 0')
    d = cascalc.tidy(('neg', ('/', fx, fy)))
    lines.append(eng.boxs('dy/d' + x + ' = ', txt(eng.nice(d))))
    return lines
