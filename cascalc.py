# cascalc.py - integration + equation solving for the CAS.
# Symbolic integration (linearity, power rule, table, linear-argument sub) with
# a numeric solver (grid scan + bisection) as the general fallback. Uses
# caseng.evalf for all numeric work. Imported by cas.py.
import caseng

def has_var(n, var):
    t = n[0]
    if t == 'n':
        return False
    if t == 'v':
        return n[1] == var
    if len(n) == 2:
        return has_var(n[1], var)
    return has_var(n[1], var) or has_var(n[2], var)

def linear_coeff(arg, var):
    # returns (a, b) if arg == a*var + b (a,b constant), else None
    try:
        f0 = caseng.evalf(arg, 0.0)
        f1 = caseng.evalf(arg, 1.0)
        f2 = caseng.evalf(arg, 2.0)
    except:
        return None
    a = f1 - f0
    b = f0
    if abs((2 * a + b) - f2) < 1e-5:
        ai = round(a)
        bi = round(b)
        if abs(ai - a) < 1e-6:
            a = ai
        if abs(bi - b) < 1e-6:
            b = bi
        return (a, b)
    return None

def integ(n, var='x'):
    t = n[0]
    if t == 'n':
        return ('*', n, ('v', var))
    if t == 'v':
        if n[1] == var:
            return ('/', ('^', ('v', var), ('n', 2)), ('n', 2))
        return ('*', n, ('v', var))
    if t == '+':
        a = integ(n[1], var); b = integ(n[2], var)
        return ('+', a, b) if a is not None and b is not None else None
    if t == '-':
        a = integ(n[1], var); b = integ(n[2], var)
        return ('-', a, b) if a is not None and b is not None else None
    if t == 'neg':
        a = integ(n[1], var)
        return ('neg', a) if a is not None else None
    if t == '*':
        a = n[1]; b = n[2]
        if not has_var(a, var):
            ib = integ(b, var)
            return ('*', a, ib) if ib is not None else None
        if not has_var(b, var):
            ia = integ(a, var)
            return ('*', b, ia) if ia is not None else None
        return None
    if t == '/':
        a = n[1]; b = n[2]
        if not has_var(b, var):
            ia = integ(a, var)
            return ('/', ia, b) if ia is not None else None
        if a == ('n', 1) and b == ('v', var):
            return ('ln', ('v', var))
        return None
    if t == '^':
        a = n[1]; b = n[2]
        if b[0] == 'n' and b[1] != -1:
            if a == ('v', var):
                p = b[1] + 1
                return ('/', ('^', ('v', var), ('n', p)), ('n', p))
            lc = linear_coeff(a, var)
            if lc is not None and lc[0] != 0:
                p = b[1] + 1
                return ('/', ('^', a, ('n', p)), ('n', p * lc[0]))
        return None
    arg = n[1]
    if arg == ('v', var):
        if t == 'sin':
            return ('neg', ('cos', ('v', var)))
        if t == 'cos':
            return ('sin', ('v', var))
        if t == 'exp':
            return ('exp', ('v', var))
    lc = linear_coeff(arg, var)
    if lc is not None and lc[0] != 0:
        if t == 'sin':
            F = ('neg', ('cos', arg))
        elif t == 'cos':
            F = ('sin', arg)
        elif t == 'exp':
            F = ('exp', arg)
        else:
            F = None
        if F is not None:
            return ('/', F, ('n', lc[0]))
    return None

def defint(tree, a, b, deg=False, n=200):
    # numeric definite integral by composite Simpson's rule; None on domain error
    if n % 2:
        n += 1
    h = (b - a) / n
    try:
        s = caseng.evalf(tree, a, deg) + caseng.evalf(tree, b, deg)
        i = 1
        while i < n:
            v = caseng.evalf(tree, a + i * h, deg)
            s += (4 if (i % 2) else 2) * v
            i += 1
    except:
        return None
    return s * h / 3.0

def _bisect(tree, a, b, deg=False):
    try:
        fa = caseng.evalf(tree, a, deg)
        fb = caseng.evalf(tree, b, deg)
    except:
        return None
    if (fa < 0 and fb < 0) or (fa > 0 and fb > 0):
        return None
    i = 0
    while i < 60:
        m = (a + b) / 2
        try:
            fm = caseng.evalf(tree, m, deg)
        except:
            return None
        if fm == 0 or (b - a) < 1e-7:
            return m
        if (fa < 0 and fm < 0) or (fa > 0 and fm > 0):
            a = m; fa = fm
        else:
            b = m; fb = fm
        i += 1
    return (a + b) / 2

def solve(tree, var='x', deg=False):
    # numeric roots of tree == 0; degrees needs a wider window (trig period 360)
    roots = []
    hi = 360.0 if deg else 20.0
    x = -hi
    prev = None
    while x <= hi + 0.0001:
        try:
            y = caseng.evalf(tree, x, deg)
        except:
            prev = None
            x += 0.1
            continue
        if prev is not None and ((prev <= 0 and y >= 0) or (prev >= 0 and y <= 0)):
            r = _bisect(tree, x - 0.1, x, deg)
            if r is not None:
                dup = False
                for rr in roots:
                    if abs(rr - r) < 1e-4:
                        dup = True
                if not dup:
                    roots.append(r)
        prev = y
        x += 0.1
    return roots
