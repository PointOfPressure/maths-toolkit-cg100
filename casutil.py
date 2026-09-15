# Shared helpers for every tool: number formatting, field parsing, the tool
# runner, and the numeric/statistical primitives the old modules shared.
import math
import caslex
import caseng

PI = math.pi
FULL = False      # result screen toggles this for full precision
DEG = False       # angle mode for Calculate / CAS numeric operations

def w(text):
    return ('w', text)

def warn(text):
    return ('!', text)

def m(tree):
    return ('m', tree)

def mw(tree):
    return ('mw', tree)

# ---- numbers -> strings ----------------------------------------------------

def _sf(v, n):
    if v == 0:
        return '0'
    neg = v < 0
    av = -v if neg else v
    e = int(math.floor(math.log10(av)))
    mi = int(round(av / (10.0 ** (e - n + 1))))
    if mi >= 10 ** n:
        mi //= 10
        e += 1
    d = str(mi)
    if e >= n + 3 or e < -4:
        frac = d[1:].rstrip('0')
        s = d[0] + ('.' + frac if frac else '') + 'e' + str(e)
    elif e >= n - 1:
        s = d + '0' * (e - n + 1)
    elif e >= 0:
        s = (d[:e + 1] + '.' + d[e + 1:]).rstrip('0').rstrip('.')
    else:
        s = ('0.' + '0' * (-e - 1) + d).rstrip('0')
    return '-' + s if neg else s

def clean(v):
    # drop rounding noise: 2.0000000001j -> 2, 3.0 -> 3
    if isinstance(v, complex):
        re = v.real
        im = v.imag
        aim = im if im >= 0 else -im
        are = re if re >= 0 else -re
        if aim <= 1e-12 * (are if are > 1 else 1.0):
            v = re
        else:
            if are <= 1e-12 * (aim if aim > 1 else 1.0):
                re = 0.0
            return complex(re, im)
    if isinstance(v, float) and v == v and -1e15 < v < 1e15 and v == int(v):
        return int(v)
    return v

def fmt(v, sf=None):
    v = clean(v)
    if isinstance(v, bool):
        return 'yes' if v else 'no'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, complex):
        return caseng.cstr(v, lambda x: fmt(x, sf))
    if not isinstance(v, float):
        return str(v)
    if v != v:
        return 'undefined'
    if v > 1.7e308:
        return 'inf'
    if v < -1.7e308:
        return '-inf'
    if sf is None and not FULL:
        ex = caseng.exactstr(v, 1e-9)
        if ex is not None:
            return ex
    return _sf(v, sf if sf else (10 if FULL else 3))

def sf3(v):
    return fmt(v, 10 if FULL else 3)

def fmtv(seq):
    return '(' + ', '.join([fmt(x) for x in seq]) + ')'

def fmtm(rows):
    return ['[' + ' '.join([fmt(x) for x in r]) + ']' for r in rows]

def real(v):
    v = clean(v)
    if isinstance(v, complex):
        raise ValueError('not real')
    return v

# ---- evaluation -------------------------------------------------------------

def ev(tree, x=0.0, env=None):
    try:
        v = caseng.evalf(tree, x, DEG, env)
    except ValueError as e:
        raise ValueError(str(e))
    except ZeroDivisionError:
        raise ValueError('division by zero')
    except OverflowError:
        raise ValueError('too large')
    except Exception:
        raise ValueError('cannot evaluate')
    v = clean(v)
    if isinstance(v, float) and v != v:
        raise ValueError('undefined')
    return v

def evx(tree, x, env=None):
    # numeric sample for plotting/solving: None instead of an error, real only
    try:
        v = caseng.evalf(tree, x, DEG, env)
    except Exception:
        return None
    if isinstance(v, complex):
        return None
    if v != v or v > 1e300 or v < -1e300:
        return None
    return v

# ---- fields -----------------------------------------------------------------

def split_values(text):
    parts = []
    depth = 0
    cur = ''
    for ch in text:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth <= 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    parts.append(cur.strip())
    while parts and parts[len(parts) - 1] == '':
        parts.pop()
    return parts

def fields_of(spec):
    # 'a,b,f(x),data*,A[2x2],v[3],k?' -> [(name, kind, count, optional)]
    out = []
    for raw in spec.split(','):
        name = raw.strip()
        if not name:
            continue
        opt = name.endswith('?')
        if opt:
            name = name[:-1]
        if name.endswith('*'):
            out.append((name[:-1], 'l', 0, opt))
        elif '[' in name:
            base = name[:name.index('[')]
            dims = name[name.index('[') + 1:len(name) - 1]
            if 'x' in dims:
                rc = dims.split('x')
                out.append((base, 'm', (int(rc[0]), int(rc[1])), opt))
            else:
                out.append((base, 'v', int(dims), opt))
        elif '(' in name:
            out.append((name, 'e', 0, opt))
        else:
            out.append((name, 'n', 0, opt))
    return out

def _num(text, name):
    if text == '':
        raise ValueError(name + ' missing')
    t = caslex.parse(text)
    if t is None:
        raise ValueError('cannot read ' + name)
    for v in caseng.vars_in(t):
        if v != 'ans':
            raise ValueError(name + ': unknown ' + v)
    return ev(t)

def _realnum(text, name):
    v = _num(text, name)
    if isinstance(v, complex):
        raise ValueError(name + ' must be real')
    return v

def _allows_complex(name):
    return name[:1] == 'z' or name[:1] == 'w'

def convert(spec, text):
    parts = split_values(text)
    vals = []
    i = 0
    for name, kind, cnt, opt in fields_of(spec):
        if i >= len(parts):
            if opt:
                vals.append(None)
                continue
            raise ValueError(name + ' missing')
        if kind == 'n':
            if parts[i] == '?':
                vals.append(None)
                i += 1
                continue
            if _allows_complex(name):
                vals.append(_num(parts[i], name))
            else:
                vals.append(_realnum(parts[i], name))
            i += 1
        elif kind == 'e':
            t = caslex.parse(parts[i])
            if t is None:
                raise ValueError('cannot read ' + name)
            vals.append(t)
            i += 1
        elif kind == 'l':
            lst = [_realnum(p, name) for p in parts[i:]]
            i = len(parts)
            vals.append(lst)
        elif kind == 'v':
            if i + cnt > len(parts):
                raise ValueError(name + ' needs ' + str(cnt) + ' values')
            vals.append([_realnum(p, name) for p in parts[i:i + cnt]])
            i += cnt
        elif kind == 'm':
            r, c = cnt
            if i + r * c > len(parts):
                raise ValueError(name + ' needs ' + str(r * c) + ' values')
            flat = [_realnum(p, name) for p in parts[i:i + r * c]]
            vals.append([flat[k * c:(k + 1) * c] for k in range(r)])
            i += r * c
    if i < len(parts):
        raise ValueError('too many values')
    return vals

# ---- tool runner -------------------------------------------------------------

def call_tool(fn, vals):
    try:
        lines = fn(*vals)
    except ValueError as e:
        return [('!', str(e) or 'invalid input')]
    except ZeroDivisionError:
        return [('!', 'division by zero')]
    except OverflowError:
        return [('!', 'number too large')]
    except Exception as e:
        return [('!', 'error: ' + str(e))]
    if lines is None:
        return []
    return lines

def run_tool(label, spec, fn):
    import casui
    last = ''
    while True:
        if spec == '':
            casui.result(label, '', lambda: call_tool(fn, []))
            return
        text = casui.input_line(label, spec, last)
        if text is None:
            return
        last = text
        try:
            vals = convert(spec, text)
        except ValueError as e:
            casui.flash(str(e))
            continue
        casui.result(label, text, lambda: call_tool(fn, vals))

def pick(title, options):
    import casui
    i = casui.menu(title, options)
    return None if i < 0 else i

def ask(spec, label=''):
    import casui
    text = casui.input_line(label, spec, '')
    if text is None:
        return None
    return convert(spec, text)

# ---- numeric helpers ---------------------------------------------------------

def deg(r):
    return r * 180.0 / PI

def rad(d):
    return d * PI / 180.0

def acos_safe(c):
    if c > 1.0:
        c = 1.0
    if c < -1.0:
        c = -1.0
    return math.acos(c)

def gcd(a, b):
    a = abs(int(a))
    b = abs(int(b))
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    g = gcd(a, b)
    if g == 0:
        return 0
    return abs(int(a) // g * int(b))

def fact(n):
    if n < 0 or n > 500:
        return None
    r = 1
    i = 2
    while i <= n:
        r *= i
        i += 1
    return r

def ncr(n, r):
    if n < 0 or r < 0 or r > n:
        return 0
    if r > n - r:
        r = n - r
    c = 1
    i = 1
    while i <= r:
        c = c * (n - r + i) // i
        i += 1
    return c

def npr(n, r):
    if n < 0 or r < 0 or r > n:
        return 0
    p = 1
    i = 0
    while i < r:
        p *= (n - i)
        i += 1
    return p

def erf(x):
    s = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * x)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * math.exp(-x * x)
    return s * y

def phi(z):
    if z > 40.0:
        return 1.0
    if z < -40.0:
        return 0.0
    return 0.5 * (1.0 + erf(z / math.sqrt(2.0)))

def invphi(p):
    if p <= 0.0:
        return -9.0
    if p >= 1.0:
        return 9.0
    lo = -9.0
    hi = 9.0
    i = 0
    while i < 60:
        mid = 0.5 * (lo + hi)
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
        i += 1
    return 0.5 * (lo + hi)

def poisson_pmf(mu, k):
    if k < 0:
        return 0.0
    r = math.exp(-mu)
    i = 1
    while i <= k:
        r = r * mu / i
        i += 1
    return r

def poisson_cdf(mu, k):
    if k < 0:
        return 0.0
    r = math.exp(-mu)
    c = r
    i = 1
    while i <= k:
        r = r * mu / i
        c += r
        i += 1
    return c

def binom_pmf(n, p, k):
    if n < 0 or k < 0 or k > n:
        return 0.0
    q = 1.0 - p
    r = 1.0
    used = 0
    rest = n - k
    i = 1
    while i <= k:
        r = r * (n - k + i) / i * p
        while r > 1.0 and used < rest:
            r *= q
            used += 1
        i += 1
    while used < rest:
        r *= q
        used += 1
    return r

def binom_cdf(n, p, k):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    c = 0.0
    i = 0
    while i <= k:
        c += binom_pmf(n, p, i)
        i += 1
    if c > 1.0:
        c = 1.0
    return c

def nice_range(vals, pad=0.08, zero=False):
    lo = None
    hi = None
    for v in vals:
        if v is None or v != v:
            continue
        if lo is None or v < lo:
            lo = v
        if hi is None or v > hi:
            hi = v
    if lo is None:
        return (0.0, 1.0)
    if zero:
        if lo > 0.0:
            lo = 0.0
        if hi < 0.0:
            hi = 0.0
    span = hi - lo
    if span < 1e-12:
        span = abs(hi) if abs(hi) > 1e-12 else 1.0
    return (lo - span * pad, hi + span * pad)

def _check():
    assert fmt(0.5) == '1/3'.replace('3', '2'), fmt(0.5)
    assert fmt(2.0) == '2' and fmt(-1.5) == '-3/2'
    assert fmt(1234.5, 3) == '1230' and fmt(0.00123456, 3) == '0.00123'
    assert fmt(0.8660254037844386) == 'sqrt(3)/2'
    assert fmt(2.0943951023931953) == '2pi/3'
    assert fmt(0.123456) == '0.123' and fmt(1.5e-7, 3) == '1.5e-7'
    assert fmt(complex(2, -3)) == '2-3i' and fmt(complex(0, 1)) == 'i'
    assert fmt(complex(3, 1e-15)) == '3'
    assert fields_of('a,f(x),data*,A[2x2],v[3],k?') == [
        ('a', 'n', 0, False), ('f(x)', 'e', 0, False), ('data', 'l', 0, False),
        ('A', 'm', (2, 2), False), ('v', 'v', 3, False), ('k', 'n', 0, True)]
    assert convert('a,b,c', '1, -3, 2') == [1, -3, 2]
    assert convert('n,r', 'ncr(5,2), sqrt(4)') == [10, 2]
    assert convert('A[2x2],k?', '1,2,3,4') == [[[1, 2], [3, 4]], None]
    assert convert('u,v,a', '0,?,9.8') == [0, None, 9.8]
    assert convert('data*', '1,2,3.5') == [[1, 2, 3.5]]
    assert convert('z,w', '2+3i, 1-i') == [complex(2, 3), complex(1, -1)]
    for bad in ('1,2', '1,2,3,4', '1,x,3', '1,2+i,3'):
        try:
            convert('a,b,c', bad)
            assert False, bad
        except ValueError:
            pass
    assert call_tool(lambda a: [fmt(a * 2)], [3]) == ['6']
    assert call_tool(lambda a: 1 / 0, [3]) == [('!', 'division by zero')]
    print('casutil ok')

if __name__ == '__main__':
    _check()
