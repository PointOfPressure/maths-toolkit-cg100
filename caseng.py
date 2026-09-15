import math

UFUNCS = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot',
          'ln', 'log', 'exp', 'sqrt', 'asin', 'acos', 'atan',
          'sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth',
          'asinh', 'acosh', 'atanh', 'abs', 'arg', 'conj', 're', 'im')
BFUNCS = ('ncr', 'npr', 'logb')

PI = 3.141592653589793
E = 2.718281828459045
ANS = 0.0

# ---- complex helpers (the device has complex but no cmath) ----------------

def _cx(v):
    return isinstance(v, complex)

def _neg(v):
    return not _cx(v) and v < 0

def _cabs(z):
    return math.sqrt(z.real * z.real + z.imag * z.imag)

def _carg(z):
    return math.atan2(z.imag, z.real)

def _csqrt(z):
    r = _cabs(z)
    re = math.sqrt((r + z.real) / 2.0)
    im = math.sqrt((r - z.real) / 2.0)
    if z.imag < 0:
        im = -im
    return complex(re, im)

def _cexp(z):
    m = math.exp(z.real)
    return complex(m * math.cos(z.imag), m * math.sin(z.imag))

def _cln(z):
    if z == 0:
        raise ValueError("ln 0")
    return complex(math.log(_cabs(z)), _carg(z))

def _sh(x):
    return (math.exp(x) - math.exp(-x)) / 2.0

def _ch(x):
    return (math.exp(x) + math.exp(-x)) / 2.0

def _csin(z):
    return complex(math.sin(z.real) * _ch(z.imag), math.cos(z.real) * _sh(z.imag))

def _ccos(z):
    return complex(math.cos(z.real) * _ch(z.imag), -math.sin(z.real) * _sh(z.imag))

def _cpow(b, e):
    if not _cx(e) and float(e) == int(e) and -64 <= e <= 64:
        n = int(e)
        if n < 0:
            if b == 0:
                raise ValueError("0 to a negative power")
            b = 1 / b
            n = -n
        r = 1
        while n:
            if n & 1:
                r = r * b
            b = b * b
            n >>= 1
        return r
    if b == 0:
        return 0.0
    return _cexp(e * _cln(complex(b)))

def cstr(z, f=None):
    if f is None:
        f = _numstr
    re = z.real
    im = z.imag
    if im == 0:
        return f(re)
    if im == 1:
        ims = ''
    elif im == -1:
        ims = '-'
    else:
        ims = f(im)
    if re == 0:
        return ims + 'i'
    if im < 0:
        return f(re) + '-' + ims[1:] + 'i'
    return f(re) + '+' + ims + 'i'

# ---- exact trig at the standard angles (multiples of pi/12 that AQA lists)

_SIN12 = {0: ('n', 0), 2: ('/', ('n', 1), ('n', 2)),
          3: ('/', ('sqrt', ('n', 2)), ('n', 2)),
          4: ('/', ('sqrt', ('n', 3)), ('n', 2)), 6: ('n', 1)}
_TAN12 = {0: ('n', 0), 2: ('/', ('sqrt', ('n', 3)), ('n', 3)),
          3: ('n', 1), 4: ('sqrt', ('n', 3))}

def _pi_mult(a):
    # a == p/q * pi  ->  (p, q), else None
    if a == ('v', 'pi'):
        return (1, 1)
    t = a[0]
    if t == 'neg':
        r = _pi_mult(a[1])
        return None if r is None else (-r[0], r[1])
    if t == '*' and a[2] == ('v', 'pi'):
        c = a[1]
        if c[0] == 'n' and isinstance(c[1], int):
            return (c[1], 1)
        if (c[0] == '/' and c[1][0] == 'n' and c[2][0] == 'n' and
                isinstance(c[1][1], int) and isinstance(c[2][1], int) and c[2][1]):
            return (c[1][1], c[2][1])
        return None
    if t == '/' and a[2][0] == 'n' and isinstance(a[2][1], int) and a[2][1]:
        r = _pi_mult(a[1])
        return None if r is None else (r[0], r[1] * a[2][1])
    return None

def _pi_k(a):
    r = _pi_mult(a)
    if r is None:
        return None
    p, q = r
    if (12 * p) % q:
        return None
    return (12 * p) // q

def _exact_trig(t, a):
    k = _pi_k(a)
    if k is None:
        return None
    if t == 'tan':
        k %= 12
        neg = k > 6
        if neg:
            k = 12 - k
        v = _TAN12.get(k)
    else:
        if t == 'cos':
            k += 6
        k %= 24
        neg = k >= 12
        if neg:
            k -= 12
        if k > 6:
            k = 12 - k
        v = _SIN12.get(k)
    if v is None:
        return None
    if neg and v != ('n', 0):
        if v[0] == 'n':
            return ('n', -v[1])
        if v[0] == '/':
            top = v[1]
            return ('/', ('n', -top[1]) if top[0] == 'n' else ('neg', top), v[2])
        return ('neg', v)
    return v

def _torad(a, deg):
    return a * PI / 180.0 if deg else a

def _fromrad(a, deg):
    return a * 180.0 / PI if deg else a

def _factorial(k):  # no math.factorial on device
    if k < 0:
        raise ValueError("factorial of negative")
    if k > 2000:
        raise ValueError("factorial too large")
    r = 1
    i = 2
    while i <= k:
        r *= i
        i += 1
    return r

def _ncr(n, k):
    if n < 0 or k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    if k > 2000:
        raise ValueError("nCr too large")
    num = 1
    den = 1
    i = 1
    while i <= k:
        num *= (n - k + i)
        den *= i
        i += 1
    return num // den

def _npr(n, k):
    if n < 0 or k < 0 or k > n:
        return 0
    if k > 2000:
        raise ValueError("nPr too large")
    r = 1
    i = 0
    while i < k:
        r *= (n - i)
        i += 1
    return r

def gcd(a, b):
    a = abs(a); b = abs(b)
    while b:
        a, b = b, a % b
    return a

def _isnum(v):
    if isinstance(v, complex):
        return False
    if not isinstance(v, (int, float)):
        return False
    if isinstance(v, float):
        if v != v:
            return False
        av = v if v >= 0 else -v
        if av > 1.7e308:
            return False
    return True

def _fold_pow(a, b):
    if _cx(a) or _cx(b):
        try:
            return ('n', _cpow(a, b))
        except:
            return None
    if isinstance(a, int) and isinstance(b, int):
        if b >= 0:
            if b > 256 and a != 0 and a != 1 and a != -1:
                return None
            return ('n', a ** b)
        if a == 0:
            return None
        if -b > 256 and a != 1 and a != -1:
            return None
        return _fold_div(1, a ** (-b))
    if a < 0 and not (isinstance(b, int) or float(b) == int(b)):
        return None
    try:
        r = a ** b
    except:
        return None
    if not _isnum(r):
        return None
    return ('n', r)

def _sqrt_split(v):
    a = 1
    b = v
    d = 2
    while d * d <= b:
        while b % (d * d) == 0:
            b //= d * d
            a *= d
        d += 1 if d == 2 else 2
    return (a, b)

def _basepow(n):
    if n[0] == '^' and n[2][0] == 'n':
        return (n[1], n[2][1])
    return (n, 1)

def exactstr(v, tol=1e-12):
    # float -> 'p/q', 'sqrt(b)', '2sqrt(3)/5', 'pi', '2pi/3'; None if nothing close
    if v == 0:
        return '0'
    neg = v < 0
    av = -v if neg else v
    if av >= 1e6 or av < 1e-6:
        return None
    sgn = '-' if neg else ''
    t = tol * (av if av > 1 else 1.0)
    q = 1
    while q <= 64:
        p = int(round(av * q))
        if p and abs(p - av * q) < t * q:
            return sgn + (str(p) if q == 1 else str(p) + '/' + str(q))
        q += 1
    r = av / PI
    tr = tol * (r if r > 1 else 1.0)
    q = 1
    while q <= 12:
        p = int(round(r * q))
        if p and abs(p - r * q) < tr * q:
            num = 'pi' if p == 1 else str(p) + 'pi'
            return sgn + num + ('' if q == 1 else '/' + str(q))
        q += 1
    sq = av * av
    ts = tol * (sq if sq > 1 else 1.0) * 4
    q = 1
    while q <= 16:
        p = int(round(sq * q))
        if p and abs(p - sq * q) < ts * q:
            a, b = _sqrt_split(p * q)
            if b != 1:
                g = gcd(a, q)
                a //= g
                qq = q // g
                num = ('' if a == 1 else str(a)) + 'sqrt(' + str(b) + ')'
                return sgn + num + ('' if qq == 1 else '/' + str(qq))
        q += 1
    return None

def _fold_div(a, b):
    if isinstance(a, int) and isinstance(b, int) and b != 0:
        g = gcd(a, b)
        if g == 0:
            g = 1
        nu = a // g
        de = b // g
        if de < 0:
            nu = -nu
            de = -de
        if de == 1:
            return ('n', nu)
        return ('/', ('n', nu), ('n', de))
    if b == 0:
        return None
    return ('n', a / b)

def simplify(node):
    return _s(node)

def _s(node):
    t = node[0]
    if t == 'n' or t == 'v':
        return node
    if t == 'neg':
        a = _s(node[1])
        if a[0] == 'n':
            return ('n', -a[1])
        if a[0] == 'neg':
            return a[1]
        return ('neg', a)
    if t in UFUNCS:
        a = _s(node[1])
        if t == 'sin' or t == 'cos' or t == 'tan':
            ex = _exact_trig(t, a)
            if ex is not None:
                return ex
        if t == 'exp' and a[0] == 'ln':
            return a[1]
        if t == 'ln' and a[0] == 'exp':
            return a[1]
        if t == 'sqrt' and a[0] == '^' and a[2] == ('n', 2):
            return ('abs', a[1])
        if a[0] == 'n':
            v = a[1]
            if t == 'sin' and v == 0: return ('n', 0)
            if t == 'cos' and v == 0: return ('n', 1)
            if t == 'tan' and v == 0: return ('n', 0)
            if t == 'exp' and v == 0: return ('n', 1)
            if t == 'sec' and v == 0: return ('n', 1)
            if t == 'sech' and v == 0: return ('n', 1)
            if t == 'ln' and v == 1: return ('n', 0)
            if t == 'log' and v == 1: return ('n', 0)
            if t == 'sqrt' and v == 0: return ('n', 0)
            if t == 'sqrt' and v == 1: return ('n', 1)
            if t == 'sqrt' and isinstance(v, int) and 0 < v <= 1000000:
                sq_out, sq_in = _sqrt_split(v)
                if sq_in == 1:
                    return ('n', sq_out)
                if sq_out != 1:
                    return ('*', ('n', sq_out), ('sqrt', ('n', sq_in)))
            if t == 'sqrt' and isinstance(v, int) and -1000000 <= v < 0:
                inner = _s(('sqrt', ('n', -v)))
                if inner[0] == 'n':
                    return ('n', complex(0, inner[1]))
                if inner[0] == '*' and inner[1][0] == 'n':
                    return ('*', ('n', complex(0, inner[1][1])), inner[2])
                return ('*', ('n', 1j), inner)
            if t == 'abs': return ('n', abs(v))
        return (t, a)
    if t == 'fact':
        a = _s(node[1])
        if a[0] == 'n' and isinstance(a[1], int) and 0 <= a[1] <= 170:
            return ('n', _factorial(a[1]))
        return ('fact', a)
    if t in BFUNCS:
        a = _s(node[1])
        b = _s(node[2])
        if a[0] == 'n' and b[0] == 'n':
            try:
                if t == 'ncr':
                    return ('n', _ncr(int(a[1]), int(b[1])))
                if t == 'npr':
                    return ('n', _npr(int(a[1]), int(b[1])))
                if t == 'logb':
                    return ('n', math.log(b[1]) / math.log(a[1]))
            except:
                pass
        return (t, a, b)
    a = _s(node[1])
    b = _s(node[2])
    an = (a[0] == 'n')
    bn = (b[0] == 'n')
    if t == '+':
        if an and bn: return ('n', a[1] + b[1])
        if an and a[1] == 0: return b
        if bn and b[1] == 0: return a
        if a == b: return _s(('*', ('n', 2), a))
        if bn and _neg(b[1]): return ('-', a, ('n', -b[1]))
        if a[0] == 'neg': return ('-', b, a[1])
        if b[0] == 'neg': return ('-', a, b[1])
        return ('+', a, b)
    if t == '-':
        if an and bn: return ('n', a[1] - b[1])
        if bn and b[1] == 0: return a
        if an and a[1] == 0: return ('neg', b)
        if a == b: return ('n', 0)
        if bn and _neg(b[1]): return ('+', a, ('n', -b[1]))
        if b[0] == 'neg': return ('+', a, b[1])
        return ('-', a, b)
    if t == '*':
        if an and bn: return ('n', a[1] * b[1])
        if (an and a[1] == 0) or (bn and b[1] == 0): return ('n', 0)
        if an and a[1] == 1: return b
        if bn and b[1] == 1: return a
        if an and a[1] == -1: return _s(('neg', b))
        if bn and b[1] == -1: return _s(('neg', a))
        if a == b: return _s(('^', a, ('n', 2)))
        ba, ea = _basepow(a)
        bb, eb = _basepow(b)
        if ba == bb and ba[0] != 'n':
            return _s(('^', ba, ('n', ea + eb)))
        if bn and not an: return ('*', b, a)
        return ('*', a, b)
    if t == '/':
        if bn and b[1] == 1: return a
        if bn and b[1] == -1: return _s(('neg', a))
        if an and a[1] == 0: return ('n', 0)
        if an and bn:
            r = _fold_div(a[1], b[1])
            if r is not None:
                return r
        if a == b: return ('n', 1)
        ba, ea = _basepow(a)
        bb, eb = _basepow(b)
        if ba == bb and ba[0] != 'n':
            return _s(('^', ba, ('n', ea - eb)))
        if b[0] == '*' and b[1][0] == 'n' and b[1][1] != 0:
            return _s(('/', _s(('/', a, b[2])), b[1]))
        if bn and b[1] != 0:
            if a[0] == '*' and a[1][0] == 'n':
                r = _fold_div(a[1][1], b[1])
                if r is not None:
                    return _s(('*', r, a[2]))
            if a[0] == '/' and a[2][0] == 'n':
                return _s(('/', a[1], ('n', a[2][1] * b[1])))
        return ('/', a, b)
    if t == '^':
        if a == ('v', 'e'):
            return _s(('exp', b))
        if bn:
            if b[1] == 0: return ('n', 1)
            if b[1] == 1: return a
            if a[0] == 'sqrt' and b[1] == 2:
                return a[1]
            if a[0] == '^' and isinstance(b[1], int) and b[1] > 0 and a[2][0] == 'n':
                return _s(('^', a[1], ('n', a[2][1] * b[1])))
            if an:
                r = _fold_pow(a[1], b[1])
                if r is not None:
                    return r
                return ('^', a, b)
        if an and a[1] == 1: return ('n', 1)
        return ('^', a, b)
    return node

def diff(node, var='x'):
    return _d(node, var)

def _d(n, var):
    t = n[0]
    if t == 'n':
        return ('n', 0)
    if t == 'v':
        return ('n', 1) if n[1] == var else ('n', 0)
    if t == '+':
        return ('+', _d(n[1], var), _d(n[2], var))
    if t == '-':
        return ('-', _d(n[1], var), _d(n[2], var))
    if t == 'neg':
        return ('neg', _d(n[1], var))
    if t == '*':
        a = n[1]; b = n[2]
        return ('+', ('*', _d(a, var), b), ('*', a, _d(b, var)))
    if t == '/':
        a = n[1]; b = n[2]
        return ('/', ('-', ('*', _d(a, var), b), ('*', a, _d(b, var))), ('^', b, ('n', 2)))
    if t == '^':
        a = n[1]; b = n[2]
        if a == ('v', 'e'):
            return ('*', ('exp', b), _d(b, var))
        if b[0] == 'n':
            return ('*', ('*', b, ('^', a, ('n', b[1] - 1))), _d(a, var))
        if a[0] == 'n':
            return ('*', ('*', ('^', a, b), ('ln', a)), _d(b, var))
        return ('*', ('^', a, b), ('+', ('*', _d(b, var), ('ln', a)), ('/', ('*', b, _d(a, var)), a)))
    if t == 'sin':
        return ('*', ('cos', n[1]), _d(n[1], var))
    if t == 'cos':
        return ('neg', ('*', ('sin', n[1]), _d(n[1], var)))
    if t == 'tan':
        return ('*', ('+', ('n', 1), ('^', ('tan', n[1]), ('n', 2))), _d(n[1], var))
    if t == 'sec':
        return ('*', ('*', ('sec', n[1]), ('tan', n[1])), _d(n[1], var))
    if t == 'cosec':
        return ('neg', ('*', ('*', ('cosec', n[1]), ('cot', n[1])), _d(n[1], var)))
    if t == 'cot':
        return ('neg', ('*', ('^', ('cosec', n[1]), ('n', 2)), _d(n[1], var)))
    if t == 'sech':
        return ('neg', ('*', ('*', ('sech', n[1]), ('tanh', n[1])), _d(n[1], var)))
    if t == 'cosech':
        return ('neg', ('*', ('*', ('cosech', n[1]), ('coth', n[1])), _d(n[1], var)))
    if t == 'coth':
        return ('neg', ('*', ('^', ('cosech', n[1]), ('n', 2)), _d(n[1], var)))
    if t == 'exp':
        return ('*', ('exp', n[1]), _d(n[1], var))
    if t == 'ln':
        return ('/', _d(n[1], var), n[1])
    if t == 'log':
        return ('/', _d(n[1], var), ('*', n[1], ('ln', ('n', 10))))
    if t == 'sqrt':
        return ('/', _d(n[1], var), ('*', ('n', 2), ('sqrt', n[1])))
    if t == 'asin':
        return ('/', _d(n[1], var), ('sqrt', ('-', ('n', 1), ('^', n[1], ('n', 2)))))
    if t == 'acos':
        return ('neg', ('/', _d(n[1], var), ('sqrt', ('-', ('n', 1), ('^', n[1], ('n', 2))))))
    if t == 'atan':
        return ('/', _d(n[1], var), ('+', ('n', 1), ('^', n[1], ('n', 2))))
    if t == 'sinh':
        return ('*', ('cosh', n[1]), _d(n[1], var))
    if t == 'cosh':
        return ('*', ('sinh', n[1]), _d(n[1], var))
    if t == 'tanh':
        return ('*', ('-', ('n', 1), ('^', ('tanh', n[1]), ('n', 2))), _d(n[1], var))
    if t == 'asinh':
        return ('/', _d(n[1], var), ('sqrt', ('+', ('^', n[1], ('n', 2)), ('n', 1))))
    if t == 'acosh':
        return ('/', _d(n[1], var), ('sqrt', ('-', ('^', n[1], ('n', 2)), ('n', 1))))
    if t == 'atanh':
        return ('/', _d(n[1], var), ('-', ('n', 1), ('^', n[1], ('n', 2))))
    if t == 'abs':
        return ('*', ('/', n[1], ('abs', n[1])), _d(n[1], var))
    if t == 'logb':
        return ('/', _d(n[2], var), ('*', n[2], ('ln', n[1])))
    if t in ('fact', 'ncr', 'npr', 'arg', 'conj', 're', 'im'):
        if _hasvar(n, var):
            raise ValueError("cannot differentiate " + t)
        return ('n', 0)
    return ('n', 0)

def subst(n, var, repl):
    t = n[0]
    if t == 'v':
        return repl if n[1] == var else n
    if t == 'n':
        return n
    if len(n) == 2:
        return (t, subst(n[1], var, repl))
    if len(n) == 3:
        return (t, subst(n[1], var, repl), subst(n[2], var, repl))
    return n

def subst_tree(n, target, repl):
    if n == target:
        return repl
    t = n[0]
    if t == 'n' or t == 'v':
        return n
    if len(n) == 2:
        return (t, subst_tree(n[1], target, repl))
    if len(n) == 3:
        return (t, subst_tree(n[1], target, repl), subst_tree(n[2], target, repl))
    return n

def strip_abs(n):
    t = n[0]
    if t == 'abs':
        return strip_abs(n[1])
    if t == 'n' or t == 'v':
        return n
    if len(n) == 2:
        return (t, strip_abs(n[1]))
    if len(n) == 3:
        return (t, strip_abs(n[1]), strip_abs(n[2]))
    return n

def count_var(n, var):
    t = n[0]
    if t == 'n':
        return 0
    if t == 'v':
        return 1 if n[1] == var else 0
    if len(n) == 2:
        return count_var(n[1], var)
    if len(n) == 3:
        return count_var(n[1], var) + count_var(n[2], var)
    return 0

def vars_in(n, out=None):
    if out is None:
        out = []
    t = n[0]
    if t == 'v':
        if n[1] not in out and n[1] != 'pi' and n[1] != 'e':
            out.append(n[1])
        return out
    if t == 'n':
        return out
    if len(n) >= 2:
        vars_in(n[1], out)
    if len(n) >= 3:
        vars_in(n[2], out)
    return out

_INVFN = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan', 'asin': 'sin',
          'acos': 'cos', 'atan': 'tan', 'exp': 'ln', 'ln': 'exp',
          'sinh': 'asinh', 'cosh': 'acosh', 'tanh': 'atanh',
          'asinh': 'sinh', 'acosh': 'cosh', 'atanh': 'tanh'}

def invert(f, var='x', yname='y'):
    if count_var(f, var) != 1:
        return None
    lhs = f
    rhs = ('v', yname)
    guard = 0
    while guard < 40:
        guard += 1
        t = lhs[0]
        if t == 'v':
            return simplify(rhs) if lhs[1] == var else None
        if t == 'neg':
            lhs = lhs[1]
            rhs = ('neg', rhs)
            continue
        if t in _INVFN:
            rhs = (_INVFN[t], rhs)
            lhs = lhs[1]
            continue
        if t == 'sqrt':
            rhs = ('^', rhs, ('n', 2))
            lhs = lhs[1]
            continue
        if t == 'log':
            rhs = ('^', ('n', 10), rhs)
            lhs = lhs[1]
            continue
        if t == 'abs':
            return None
        if t in ('+', '-', '*', '/', '^'):
            a = lhs[1]
            b = lhs[2]
            ax = _hasvar(a, var)
            if ax and _hasvar(b, var):
                return None
            if ax:
                if t == '+':
                    rhs = ('-', rhs, b)
                elif t == '-':
                    rhs = ('+', rhs, b)
                elif t == '*':
                    rhs = ('/', rhs, b)
                elif t == '/':
                    rhs = ('*', rhs, b)
                else:
                    if b[0] != 'n':
                        return None
                    e = b[1]
                    if e == 0:
                        return None
                    rhs = ('^', rhs, ('/', ('n', 1), ('n', e)))
                lhs = a
                continue
            if t == '+':
                rhs = ('-', rhs, a)
            elif t == '-':
                rhs = ('-', a, rhs)
            elif t == '*':
                rhs = ('/', rhs, a)
            elif t == '/':
                rhs = ('/', a, rhs)
            else:
                rhs = ('/', ('ln', rhs), ('ln', a))
            lhs = b
            continue
        return None
    return None

def _hasvar(n, var):
    t = n[0]
    if t == 'n':
        return False
    if t == 'v':
        return n[1] == var
    if len(n) == 2:
        return _hasvar(n[1], var)
    return _hasvar(n[1], var) or _hasvar(n[2], var)

def evalf(n, x, deg=False, env=None):
    t = n[0]
    if t == 'n':
        return n[1]
    if t == 'v':
        # env before the positional x
        if env is not None and n[1] in env:
            return env[n[1]]
        if n[1] == 'x':
            return x
        if n[1] == 'pi':
            return PI
        if n[1] == 'e':
            return E
        if n[1] == 'ans':
            return ANS
        raise ValueError("unknown variable " + n[1])
    if t == 'neg':
        return -evalf(n[1], x, deg, env)
    if t == '+':
        return evalf(n[1], x, deg, env) + evalf(n[2], x, deg, env)
    if t == '-':
        return evalf(n[1], x, deg, env) - evalf(n[2], x, deg, env)
    if t == '*':
        return evalf(n[1], x, deg, env) * evalf(n[2], x, deg, env)
    if t == '/':
        return evalf(n[1], x, deg, env) / evalf(n[2], x, deg, env)
    if t == '^':
        base = evalf(n[1], x, deg, env)
        expo = evalf(n[2], x, deg, env)
        if _cx(base) or _cx(expo):
            return _cpow(base, expo)
        if base < 0 and float(expo) != int(expo):
            return _cpow(complex(base), expo)
        return base ** expo
    if t == 'fact':
        return _factorial(int(round(evalf(n[1], x, deg, env))))
    if t == 'ncr':
        return _ncr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'npr':
        return _npr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'logb':
        return math.log(evalf(n[2], x, deg, env)) / math.log(evalf(n[1], x, deg, env))
    a = evalf(n[1], x, deg, env)
    if t == 'arg':
        return _carg(a) if _cx(a) else (0.0 if a >= 0 else PI)
    if t == 'conj':
        return complex(a.real, -a.imag) if _cx(a) else a
    if t == 're':
        return a.real if _cx(a) else a
    if t == 'im':
        return a.imag if _cx(a) else 0
    if _cx(a):
        if t == 'sqrt':
            return _csqrt(a)
        if t == 'exp':
            return _cexp(a)
        if t == 'ln':
            return _cln(a)
        if t == 'abs':
            return _cabs(a)
        if t == 'sin':
            return _csin(a)
        if t == 'cos':
            return _ccos(a)
        if t == 'tan':
            return _csin(a) / _ccos(a)
        if t == 'sinh':
            return (_cexp(a) - _cexp(-a)) / 2
        if t == 'cosh':
            return (_cexp(a) + _cexp(-a)) / 2
        raise ValueError(t + " of a complex number")
    if t == 'sin':
        return math.sin(_torad(a, deg))
    if t == 'cos':
        return math.cos(_torad(a, deg))
    if t == 'tan':
        return math.tan(_torad(a, deg))
    if t == 'sec':
        c = math.cos(_torad(a, deg))
        if -1e-12 < c < 1e-12:
            raise ValueError("sec undefined here")
        return 1.0 / c
    if t == 'cosec':
        s = math.sin(_torad(a, deg))
        if -1e-12 < s < 1e-12:
            raise ValueError("cosec undefined here")
        return 1.0 / s
    if t == 'cot':
        r = _torad(a, deg)
        s = math.sin(r)
        if -1e-12 < s < 1e-12:
            raise ValueError("cot undefined here")
        return math.cos(r) / s
    if t == 'asin':
        return _fromrad(math.asin(a), deg)
    if t == 'acos':
        return _fromrad(math.acos(a), deg)
    if t == 'atan':
        return _fromrad(math.atan(a), deg)
    if t == 'exp':
        return math.exp(a)
    if t == 'ln':
        return math.log(a)
    if t == 'log':
        return math.log(a) / math.log(10)
    if t == 'sqrt':
        if a < 0:
            return complex(0, math.sqrt(-a))
        return math.sqrt(a)
    if t == 'abs':
        return abs(a)
    if t == 'sinh':
        return (math.exp(a) - math.exp(-a)) / 2.0
    if t == 'cosh':
        return (math.exp(a) + math.exp(-a)) / 2.0
    if t == 'tanh':
        if a > 350.0:
            return 1.0
        if a < -350.0:
            return -1.0
        e2 = math.exp(2.0 * a)
        return (e2 - 1.0) / (e2 + 1.0)
    if t == 'sech':
        return 2.0 / (math.exp(a) + math.exp(-a))
    if t == 'cosech':
        d = math.exp(a) - math.exp(-a)
        if -1e-12 < d < 1e-12:
            raise ValueError("cosech undefined at 0")
        return 2.0 / d
    if t == 'coth':
        d = math.exp(a) - math.exp(-a)
        if -1e-12 < d < 1e-12:
            raise ValueError("coth undefined at 0")
        return (math.exp(a) + math.exp(-a)) / d
    if t == 'asinh':
        sgn = -1.0 if a < 0 else 1.0
        aa = a if a >= 0 else -a
        return sgn * math.log(aa + math.sqrt(aa * aa + 1.0))
    if t == 'acosh':
        return math.log(a + math.sqrt(a * a - 1.0))
    if t == 'atanh':
        return 0.5 * math.log((1.0 + a) / (1.0 - a))
    return 0.0

OPPREC = {'+': 1, '-': 1, '*': 2, '/': 2, 'neg': 3, '^': 4}

def _numstr(v):
    if isinstance(v, int):
        return str(v)
    if _cx(v):
        return cstr(v)
    if not _isnum(v):
        if v != v:
            return "undefined"
        return "inf" if v > 0 else "-inf"
    ex = exactstr(v)
    if ex is not None:
        return ex
    r = round(v, 6)
    if r == int(r):
        return str(int(r))
    return str(r)

def tostr(n):
    return _str(n, 0, False)

def _str(n, parent, right):
    t = n[0]
    if t == 'n':
        s = _numstr(n[1])
        if (right or parent >= 3) and not (s.replace('.', '').isdigit() or s == 'pi'):
            return "(" + s + ")"
        return s
    if t == 'v':
        return n[1]
    if t == 'exp':
        return "e^(" + _str(n[1], 0, False) + ")"
    if t in UFUNCS:
        return t + "(" + _str(n[1], 0, False) + ")"
    if t == 'neg':
        s = "-" + _str(n[1], 3, False)
        return "(" + s + ")" if parent > 3 else s
    if t == 'fact':
        return _str(n[1], 5, False) + "!"
    if t in BFUNCS:
        nm = 'nCr' if t == 'ncr' else ('nPr' if t == 'npr' else 'logb')
        return nm + "(" + _str(n[1], 0, False) + "," + _str(n[2], 0, False) + ")"
    p = OPPREC[t]
    if t == '^':
        ls = _str(n[1], p + 1, False)
        rs = _str(n[2], p, True)
    elif t == '-' or t == '/':
        ls = _str(n[1], p, right)
        rs = _str(n[2], p + 1, True)
    else:
        ls = _str(n[1], p, right)
        rs = _str(n[2], p, True)
    s = ls + t + rs
    return "(" + s + ")" if p < parent else s
