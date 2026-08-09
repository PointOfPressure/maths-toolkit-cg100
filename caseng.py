# caseng.py - the CAS engine: simplify, differentiate, numeric eval, printer.
# Operates on the tuple trees from caslex.py. Tree walks are recursive but
# depth = expression nesting (small), so they stay under the ~38-frame ceiling.
import math

# unary funcs rendered as name(arg); 'fact' (postfix !) and the BFUNCS are
# handled separately. Inverse-trig answers honour the deg flag in evalf.
UFUNCS = ('sin', 'cos', 'tan', 'sec', 'cosec', 'cot',
          'ln', 'log', 'exp', 'sqrt', 'asin', 'acos', 'atan',
          'sinh', 'cosh', 'tanh', 'sech', 'cosech', 'coth',
          'asinh', 'acosh', 'atanh', 'abs')
BFUNCS = ('ncr', 'npr', 'logb')

PI = 3.141592653589793
ANS = 0.0  # last Calculate result, reachable as the token "ans"

def _torad(a, deg):
    return a * PI / 180.0 if deg else a

def _fromrad(a, deg):
    return a * 180.0 / PI if deg else a

def _factorial(k):
    # iterative (device has no math.factorial and a ~38-frame recursion ceiling)
    if k < 0:
        raise ValueError("factorial of negative")
    if k > 2000:
        raise ValueError("factorial too large")  # keep the handheld responsive
    r = 1
    i = 2
    while i <= k:
        r *= i
        i += 1
    return r

def _ncr(n, k):
    # stable multiplicative form - avoids building huge factorials
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
    # real, finite number? (bool is an int subclass but never appears in trees)
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
    # constant-fold a ** b, but only when the answer is a real finite number we
    # can keep in a tree. Returns None to leave ('^', a, b) unevaluated.
    if isinstance(a, int) and isinstance(b, int):
        if b >= 0:
            # a huge integer power would allocate megabytes on the handheld
            if b > 256 and a != 0 and a != 1 and a != -1:
                return None
            return ('n', a ** b)
        # negative integer power of an integer stays exact as a fraction
        if a == 0:
            return None
        if -b > 256 and a != 1 and a != -1:
            return None
        return _fold_div(1, a ** (-b))
    if a < 0 and not (isinstance(b, int) or float(b) == int(b)):
        return None  # fractional power of a negative -> complex, leave symbolic
    try:
        r = a ** b
    except:
        return None
    if not _isnum(r):
        return None
    return ('n', r)

def _sqrt_split(v):
    # v = a*a*b with b square-free: sqrt(v) = a sqrt(b). Trial division to the
    # square root of v, which for the sizes a student types is instant.
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
    # view a node as (base, numeric exponent) so like powers can be combined
    if n[0] == '^' and n[2][0] == 'n':
        return (n[1], n[2][1])
    return (n, 1)

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

# ---------- simplify (bottom-up, local rules; terminating) ----------
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
        # exp and ln undo each other. Without this the integrating factor of
        # dy/dx + y/x = x stays as e^(ln|x|) and cannot be multiplied through,
        # which is the most standard first-order question there is.
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
                # Pull the largest square factor out: sqrt(8) is 2 sqrt(2), and
                # sqrt(4) is 2 as a special case of it. Never turn sqrt(2) into
                # 1.414214 - "give your answer in exact form" is most of the
                # marks on an H640 surd question.
                # deliberately not named a/b: `a` is the simplified argument
                # node in this scope, and shadowing it returned ('sqrt', 1)
                sq_out, sq_in = _sqrt_split(v)
                if sq_in == 1:
                    return ('n', sq_out)
                if sq_out != 1:
                    return ('*', ('n', sq_out), ('sqrt', ('n', sq_in)))
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
        # x + (-1) is x - 1: adding a negative reads badly on a result screen
        if bn and b[1] < 0: return ('-', a, ('n', -b[1]))
        if a[0] == 'neg': return ('-', b, a[1])
        if b[0] == 'neg': return ('-', a, b[1])
        return ('+', a, b)
    if t == '-':
        if an and bn: return ('n', a[1] - b[1])
        if bn and b[1] == 0: return a
        if an and a[1] == 0: return ('neg', b)
        if a == b: return ('n', 0)
        if bn and b[1] < 0: return ('+', a, ('n', -b[1]))
        if b[0] == 'neg': return ('+', a, b[1])
        return ('-', a, b)
    if t == '*':
        if an and bn: return ('n', a[1] * b[1])
        if (an and a[1] == 0) or (bn and b[1] == 0): return ('n', 0)
        if an and a[1] == 1: return b
        if bn and b[1] == 1: return a
        # -1*X is -X: without this a partial-fraction numerator prints as
        # "-1*x" where a student would write "-x"
        if an and a[1] == -1: return _s(('neg', b))
        if bn and b[1] == -1: return _s(('neg', a))
        # re-simplified, so sqrt(3)*sqrt(3) folds to 3 via the sqrt(u)^2 rule
        # rather than stopping at sqrt(3)^2
        if a == b: return _s(('^', a, ('n', 2)))
        # x^p * x^q -> x^(p+q); integration by parts leans on this to close
        ba, ea = _basepow(a)
        bb, eb = _basepow(b)
        if ba == bb and ba[0] != 'n':
            return _s(('^', ba, ('n', ea + eb)))
        if bn and not an: return ('*', b, a)  # constant to the front
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
        # x^p / x^q -> x^(p-q)
        ba, ea = _basepow(a)
        bb, eb = _basepow(b)
        if ba == bb and ba[0] != 'n':
            return _s(('^', ba, ('n', ea - eb)))
        # A/(k*B) -> (A/B)/k: lifting the constant out of a denominator is what
        # lets x^2/(2x) reach the power rule above and collapse to x/2
        if b[0] == '*' and b[1][0] == 'n' and b[1][1] != 0:
            return _s(('/', _s(('/', a, b[2])), b[1]))
        if bn and b[1] != 0:
            # (k*X)/m -> (k/m)*X, so an integral's constant lands in lowest terms
            if a[0] == '*' and a[1][0] == 'n':
                r = _fold_div(a[1][1], b[1])
                if r is not None:
                    return _s(('*', r, a[2]))
            # (p/q)/m -> p/(q*m) instead of a stack of divisions
            if a[0] == '/' and a[2][0] == 'n':
                return _s(('/', a[1], ('n', a[2][1] * b[1])))
        return ('/', a, b)
    if t == '^':
        if bn:
            if b[1] == 0: return ('n', 1)
            if b[1] == 1: return a
            # sqrt(u)^2 is u - true wherever sqrt(u) is defined at all, and
            # without it the volume-of-revolution integrand pi*sqrt(x)^2 has
            # no symbolic integral
            if a[0] == 'sqrt' and b[1] == 2:
                return a[1]
            # (u^p)^q folds when q is a whole number; for a fractional q it
            # does not ((x^2)^(1/2) is |x|, not x), so that case is left alone
            if a[0] == '^' and isinstance(b[1], int) and b[1] > 0 and a[2][0] == 'n':
                return _s(('^', a[1], ('n', a[2][1] * b[1])))
            if an:
                r = _fold_pow(a[1], b[1])
                if r is not None:
                    return r
                return ('^', a, b)
        # 1^anything is 1; 0^x is left symbolic because 0^0 is 1, not 0
        if an and a[1] == 1: return ('n', 1)
        return ('^', a, b)
    return node

# ---------- differentiate (full rule set, then caller simplifies) ----------
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
        # d/dx log_a(u) = u' / (u ln a); the base is treated as constant
        return ('/', _d(n[2], var), ('*', n[2], ('ln', n[1])))
    # fact/ncr/npr have no elementary derivative: 0 is right only when the
    # argument does not involve the variable at all.
    if t in ('fact', 'ncr', 'npr'):
        if _hasvar(n, var):
            raise ValueError("cannot differentiate " + t)
        return ('n', 0)
    return ('n', 0)

def subst(n, var, repl):
    # replace every ('v', var) with the tree repl. Composite functions, implicit
    # differentiation and integration by substitution all need this.
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
    # replace every occurrence of the subtree `target` with `repl`. This is how
    # a substitution u = g(x) is checked: rewrite, then see whether any x is
    # left. Compared structurally, so g(x) has to be written the same way it
    # appears in the integrand - which is what a student does anyway.
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
    # drop every abs(...) wrapper. Used where the caller can settle the sign
    # itself: separating variables gives ln|y| = ..., and the initial condition
    # says which side of zero y is on, which is exactly the step a student
    # writes as "y > 0 here, so drop the modulus".
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
    # how many times var appears; 1 means an expression can be inverted by
    # peeling operations off the outside one at a time
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
    # the variable names an expression mentions, in first-seen order
    if out is None:
        out = []
    t = n[0]
    if t == 'v':
        if n[1] not in out:
            out.append(n[1])
        return out
    if t == 'n':
        return out
    if len(n) >= 2:
        vars_in(n[1], out)
    if len(n) >= 3:
        vars_in(n[2], out)
    return out

# ---------- invert y = f(x) by peeling operations off the outside ----------
# Only valid when x occurs exactly once; with two occurrences the inverse is
# not obtainable this way and the caller falls back to solving numerically.
_INVFN = {'sin': 'asin', 'cos': 'acos', 'tan': 'atan', 'asin': 'sin',
          'acos': 'cos', 'atan': 'tan', 'exp': 'ln', 'ln': 'exp',
          'sinh': 'asinh', 'cosh': 'acosh', 'tanh': 'atanh',
          'asinh': 'sinh', 'acosh': 'cosh', 'atanh': 'tanh'}

def invert(f, var='x', yname='y'):
    # x as a function of y, or None
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
            return None       # not one-to-one: no single inverse
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
            # the variable is on the right of the operator
            if t == '+':
                rhs = ('-', rhs, a)
            elif t == '-':
                rhs = ('-', a, rhs)
            elif t == '*':
                rhs = ('/', rhs, a)
            elif t == '/':
                rhs = ('/', a, rhs)
            else:
                # a^x = y  ->  x = ln y / ln a
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

# ---------- numeric evaluation ----------
def evalf(n, x, deg=False, env=None):
    # deg=True makes trig take/return degrees (Calculate + CAS honour the mode;
    # the FM section modules call evalf without deg, so they stay in radians).
    # env is an optional {name: value} map for variables other than x - it is
    # what lets Euler's method evaluate dy/dx = f(x, y) on a one-variable engine.
    # An unknown variable raises rather than silently evaluating to 0, so a
    # mistyped entry is reported instead of quietly becoming a wrong answer.
    t = n[0]
    if t == 'n':
        return n[1]
    if t == 'v':
        # env is consulted FIRST, including for x. Checking the positional
        # argument first made env['x'] silently ignored, so a two-variable
        # tool that passed {'x': a, 'y': b} evaluated at whatever had been
        # passed positionally instead - which is how the surface stationary
        # point tool searched with x pinned at 0 and still reported an answer.
        if env is not None and n[1] in env:
            return env[n[1]]
        if n[1] == 'x':
            return x
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
        r = base ** expo
        if isinstance(r, complex):
            # e.g. (-8)^(1/3): real-valued engine, so report a domain error
            raise ValueError("complex result")
        return r
    if t == 'fact':
        return _factorial(int(round(evalf(n[1], x, deg, env))))
    if t == 'ncr':
        return _ncr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'npr':
        return _npr(int(round(evalf(n[1], x, deg, env))), int(round(evalf(n[2], x, deg, env))))
    if t == 'logb':
        return math.log(evalf(n[2], x, deg, env)) / math.log(evalf(n[1], x, deg, env))
    a = evalf(n[1], x, deg, env)
    if t == 'sin':
        return math.sin(_torad(a, deg))
    if t == 'cos':
        return math.cos(_torad(a, deg))
    if t == 'tan':
        return math.tan(_torad(a, deg))
    if t == 'sec':
        # Tested against a tolerance, not against exact zero: cos(pi/2) is
        # 6.1e-17 in floating point, so an exact test would hand back 1.6e16
        # and print it as an answer. At an asymptote "undefined" is the answer,
        # and the graph code already draws a gap where evaluation raises.
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
        # cos/sin, not 1/tan: tan is infinite at pi/2 where cot is simply 0
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

# ---------- expression -> string (precedence-aware) ----------
OPPREC = {'+': 1, '-': 1, '*': 2, '/': 2, 'neg': 3, '^': 4}

def _numstr(v):
    if isinstance(v, int):
        return str(v)
    if not _isnum(v):
        # int() would raise on nan/inf, taking the whole result screen with it
        if v != v:
            return "undefined"
        return "inf" if v > 0 else "-inf"
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
        # A bare negative literal needs brackets when it is a right operand
        # ("x+(-3)"), the operand of a unary minus, or the base of a power -
        # otherwise (-8)^(1/3) would print as -8^(1/3), which reads as
        # -(8^(1/3)). As a leading left operand it does not: "-1/2" is both
        # correct and what a student would write, where "(-1)/2" is neither.
        if (right or parent >= 3) and s[:1] == '-':
            return "(" + s + ")"
        return s
    if t == 'v':
        return n[1]
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
