# Maths Toolkit for the Casio fx-CG100

A from-scratch visual mathematics toolkit for the Casio fx-CG100 graphing calculator, written in stock MicroPython with the built-in `casioplot` graphics module. It bundles three things in one app:

- an everyday scientific **Calculate** mode,
- a from-scratch **computer algebra system (CAS)** that differentiates, integrates, simplifies, solves and graphs, and
- full tool coverage of the **OCR B (MEI) A-Level Maths (H640)** and **Further Maths (H645)** specifications,

all driven by an on-screen keyboard and a custom 2D math typesetter (Desmos-style fractions, exponents and radicals).

![platform](https://img.shields.io/badge/platform-Casio%20fx--CG100-blue)
![runtime](https://img.shields.io/badge/MicroPython-1.9.4-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)
![tests](https://img.shields.io/badge/tests-1250%20checks%2C%200%20failures-brightgreen)
![smoke](https://img.shields.io/badge/smoke-343%20checks%2C%200%20errors-brightgreen)

Built and verified on real hardware. The whole toolkit also runs unmodified on a desktop under CPython (via a small `casioplot` stub) for development and testing.

## Quick start

1. Copy the device `.py` files to your fx-CG100 (everything **except** `casioplot.py`, `stress.py`, `devlint.py` and any `tests*.py`). See [Installing on the calculator](#installing-on-the-calculator).
2. In the calculator's Python app, run **`maths.py`**.
3. Navigate with the arrow keys and OK; the curved-arrow back key goes back. Type expressions on the normal keys; use ALPHA for letters and the CATALOG key for the few symbols with no key of their own.

### Keys

| In a menu | |
| --- | --- |
| up / down | move the selection (wraps) |
| **1-9** | jump straight to that entry |
| page up / page down | move seven at a time |
| `\|<-` / `->\|` | first / last entry |
| OK or EXE | choose |
| back (the curved arrow) | back; at the top menu, leave the app |

| When typing an expression | |
| --- | --- |
| left / right | move the caret |
| `\|<-` / `->\|` | jump to the start / end of the line |
| **up** | recall your last entry (instead of retyping it) |
| down | clear the line |
| DEL | delete backwards |
| back | clear the line; press again on an empty line to cancel |
| ALPHA | the orange letter printed on the key (all of a-z) |
| SHIFT | the green legend: `sin^-1`, `cos^-1`, `tan^-1`, `ln`, `log`, `pi`, `=`, and a log to a given base |
| **CATALOG** (the book key) | the symbol picker - see below |

**The CATALOG picker** holds the handful of tokens the keypad has no key for at all: `!`, `abs(`, `nCr(`, `nPr(`, the three hyperbolics and their three inverses, plus `ans` and `,` for convenience. One page; arrows move, OK inserts, back closes. Everything else comes off a real key. `tests.py` asserts every documented function stays reachable one way or the other.

> The key map in `casui.py` had drifted from the hardware. ALPHA ran a whole row out of step - key 42 produced `a` when the key is printed **B** - so 17 of the 26 letters came out as the wrong letter or had no key at all, and `i`, `h`, `g`-`l`, `u` and `y` were unreachable. "EXIT" was bound to code 13, which is the jump-to-line-start key rather than back. And the comma, which has its own key at code 51, was simply never bound, which is what made `nCr`, `nPr` and `logb` impossible to type. `tests.py` now carries the keypad table transcribed independently from Casio's key-code diagram and asserts every binding against it.

In **Calculus & Algebra** you enter `f(x)` once and then keep picking operations on it - differentiate, then integrate, then graph - without retyping. "New expression" or EXIT returns to the editor.

---

## Features

### Calculate - everyday scientific calculator

The `Calculate` mode (`calc_section`) is a free-form expression calculator. Type any expression on the calculator's own keys, see a live 2D preview of it as you type, and press OK to evaluate.

- **Any expression at once.** The whole line is parsed and evaluated in one go (no operator-at-a-time entry). Arithmetic, brackets, powers, functions and constants can all be combined.
- **`ans` memory.** Every successful result is stored. Type `ans` in the next calculation to reuse your last answer.
- **Degree / radian toggle.** A shared angle mode (shown as `DEG` or `RAD` on the result screen) is switched from the home menu and applies to all trig in Calculate and in the CAS evaluate/graph/table tools.
- **Smart number formatting** (`_fmt_num`):
  - Whole-number results print as plain integers.
  - Ordinary decimals round to a sensible number of digits.
  - Very large or very small magnitudes (>= 1e12 or < 1e-5) switch to scientific notation (e.g. `1.23e15`).
  - Bad results are caught and reported: non-finite, NaN, or overflow values (> 1e308) show "undefined" / "overflow" rather than a garbage number.
- **Exact form.** When the simplified expression is an exact fraction or rational that differs from the decimal answer, it is shown beneath the result as `exact: ...` (for example a fraction kept in lowest terms instead of a rounded decimal).
- Math errors (bad brackets, out-of-domain inputs) are reported with a clear message instead of crashing.

### Calculus & Algebra (CAS)

The `Calculus & Algebra` mode (`cas_section`) works on a function of `x`. Type an expression (for example `x^2+3x` or `sin(x)`), press OK, then choose an operation from the menu. Variables other than `x` can be entered with ALPHA (every letter a-z has a key). The differentiation, integration and simplify operations are fully symbolic; the rest are numeric and honour the home-menu angle mode.

- **Differentiate (d/dx)** - symbolic derivative with respect to `x`, then simplified. Full rule set: sum, difference, product, quotient and power/chain rules, plus derivatives of sin, cos, tan, exp, ln, log, sqrt, asin, acos, atan, the hyperbolics sinh/cosh/tanh, the inverse hyperbolics asinh/acosh/atanh, and abs.
- **Gradient at a point** (`do_gradient`) - numeric slope `f'(x)` at a value you supply, computed by a symmetric central difference whose step scales with the size of `x`.
- **Integrate (+ C)** - symbolic indefinite integral, simplified and shown with the constant of integration. Covers powers (including negative and rational exponents), `1/x` and `c/(px+q)` as logarithms, anything of the form `f'(x)/f(x)`, and `sin`, `cos`, `tan`, `exp`, `sqrt`, `ln`, `sinh` and `cosh`, each also with a linear argument. **Integration by parts** handles the products: `x sin x`, `x^2 e^x`, `x ln x`, `x^3 e^x`, `atan x` and so on, including the two that would otherwise cycle forever - `e^(ax) sin(bx)` and `sin x cos x`. If there is no elementary form it says so and points you to the definite integral for a numeric area.
- **Definite integral a..b** (`do_defint`) - numeric area between two limits you enter.
- **Simplify** - applies the engine's local algebraic simplification rules (folds constants, removes `*1`, `+0`, `^1`, `^0`, combines like terms, reduces fractions to lowest terms, etc.).
- **Solve f(x)=0** (`do_solve`) - finds real roots over a search range, including roots the curve only touches without crossing (such as `x^2` or `(x-1)^2`). Accepts either an expression (solved against zero) or a full equation with `=` (the two sides are subtracted first). Roots are listed in order; if none are found in range it says so.
- **Evaluate at x** (`do_eval`) - asks for a value of `x` and prints `f(x)`, formatted with the same smart number rules as Calculate.
- **Graph** - plots `y = f(x)` over `-12 <= x <= 12` with axes, joining consecutive samples into a continuous curve. The y-axis autoscales to the sampled values, trimming the extreme 5% at each end so a single asymptote (as in `1/x` or `tan x`) cannot squash the rest of the curve into one pixel row. The x and y ranges are printed along the bottom.
- **Table of values** (`do_table`) - asks for a start `x` and a step, then prints 8 rows of `x` and `f(x)`; out-of-domain rows show "undefined".

Each operation is guarded: expressions that nest too deep for the handheld's small call stack report "Too complex" rather than failing hard.

### Supported functions and operators

The expression parser (`caslex.py`) and engine (`caseng.py`) accept the following, typeable directly on the calculator keys:

**Arithmetic and structure**
- `+`, `-`, `*`, `/` and unary minus.
- `^` for powers (right-associative), and a `^2` square key.
- Round brackets `( )` for grouping, with correct operator precedence.
- **Implicit multiplication** - `2x`, `2(x+1)`, `(x+1)(x-1)` and `x sin(x)` all insert the `*` automatically.
- Decimal numbers and integers (integer arithmetic is kept exact where possible, so fractions stay exact).
- **Scientific notation** in a number literal: `1e3`, `2.5e-3`, `6.02e23`. This is what lets a result shown as `1.23e15` be typed straight back in. A bare `e` not followed by digits is still Euler's number, so `2e` is `2 x 2.71828...`; write `2*e+3` if you mean that rather than `2e+3`.

**Functions**
- `sqrt(...)` - square root.
- Trig: `sin`, `cos`, `tan` (take degrees or radians per the angle mode).
- Inverse trig: `asin`, `acos`, `atan` (return degrees or radians per the angle mode).
- `ln` (natural log), `log` (base 10), `exp` (e^x).
- `logb(a, b)` - logarithm of `b` to base `a`.
- `abs(...)` - absolute value.
- `n!` - factorial, entered as a postfix `!` (iterative, capped to keep the device responsive).
- `nCr(n, r)` and `nPr(n, r)` - combinations and permutations.
- Hyperbolics: `sinh`, `cosh`, `tanh`.
- Inverse hyperbolics: `asinh`, `acosh`, `atanh`.

**Constants and memory**
- `pi` (3.141592653589793) and `e` (2.718281828459045).
- `ans` - the last Calculate result.

Function names are matched longest-first (so `asinh` beats `asin` beats `sin`), and any single letter other than `x` is treated as a symbolic variable.

---

## Specification coverage

Every tool below is reached by launching the toolkit and choosing the menu path shown. The top menu is `MATHS TOOLKIT` with entries `Calculate`, `Calculus & Algebra`, `A-Level Maths`, `Further Maths`, and `Angle mode`. The tables list each section module, the menu path to it, and the exact tools it provides (taken verbatim from each module's `TOOLS` labels).

### A-Level Maths (H640)

Reached via `Maths Toolkit > A-Level Maths`, then `Pure`, `Statistics`, or `Mechanics`.

| Section | Menu path | Tools provided |
| --- | --- | --- |
| Pure | A-Level Maths > Pure | Quadratic solver, Simultaneous eqns, Arithmetic seq/sum, Geometric seq/sum, Binomial expansion, Logarithms, Coord geometry, Circle, Trig tools |
| Statistics | A-Level Maths > Statistics | Summary stats, Freq table mean/var, Discrete RV E,Var, Binomial B(n,p), Normal P(a<X<b), Inverse Normal, HT binomial prop, HT Normal mean z, PMCC + regression, Probability rules, Factorial / nCr |
| Mechanics | A-Level Maths > Mechanics | SUVAT solver, Projectiles, Resultant of forces, Resolve a force, Equilibrium check, Newton II F=ma, Friction F=mu R, Friction horiz plane, Friction incline, Pulley (connected), Moments / reactions |

Some Pure and Mechanics entries open their own sub-menus: `Simultaneous eqns` offers `Two linear` and `Linear + quadratic`; `Binomial expansion` offers `(a+bx)^n list terms`, `(1+x)^n real n`, `one coeff of x^k`; `Logarithms` offers `Solve a^x = b`, `log base c of v`, `Log-law reference`; `Circle` offers `Centre+r -> equation` and `Equation -> centre+r`; `Trig tools` offers `Solve sin/cos/tan`, `R-form a sin+b cos`, `Exact-value table`. Calculus (differentiation, integration, definite integrals, graphing, tables) is not in these modules; it lives in the `Calculus & Algebra` CAS section off the main menu.

### Further Maths Core Pure (H645)

Reached via `Maths Toolkit > Further Maths > Core Pure (compulsory)`.

| Section | Menu path | Tools provided |
| --- | --- | --- |
| Complex numbers | Further Maths > Core Pure > Complex numbers | Arithmetic z, w, Modulus & argument, Polar / exp form, From polar (r,theta), Power z^n (De Moivre), nth roots of z, Quadratic complex roots, Argand plot |
| Matrices | Further Maths > Core Pure > Matrices | Enter A, Enter B, Show A and B, A + B, A - B, k * A, A * B, Transpose A, Determinant A, Inverse A, Solve A x = b, Eigenvalues 2x2, 2D transform builder |
| Vectors & 3-D | Further Maths > Core Pure > Vectors & 3-D | Magnitude, Dot product a.b, Angle between, Cross product a x b, Unit vector, Scalar projection, Parallel / perp test, Point to line dist, Point to plane dist, Angle between planes, Skew lines distance |
| Roots of polynomials | Further Maths > Core Pure > Roots of polynomials | Vieta quadratic, Vieta cubic, Vieta quartic, Quadratic roots, Numeric roots (x), Shift roots by k |
| Series & Maclaurin | Further Maths > Core Pure > Series & Maclaurin | Sum of r, Sum of r^2, Sum of r^3, Maclaurin of f(x), Approx + error, Reference card |
| Hyperbolic functions | Further Maths > Core Pure > Hyperbolic functions | Evaluate sinh, Evaluate cosh, Evaluate tanh, All three at x, arsinh (inverse), arcosh (inverse), artanh (inverse), Reference card |
| Polar coordinates | Further Maths > Core Pure > Polar coordinates | (r,theta) -> (x,y), (x,y) -> (r,theta), Plot polar curve, Preset curves, Polar area |
| Differential equations | Further Maths > Core Pure > Differential equations | First-order linear (IF), Second-order const-coeff, SHM recogniser, Damping classifier |

The Matrices `2D transform builder` opens a further sub-menu (`Rotation`, `Reflect x-axis`, `Reflect y-axis`, `Reflect y=x`, `Enlargement`, `Stretch`, `Shear`). The Polar `Preset curves` tool offers `Cardioid 1+cos`, `Rose cos(2x)`, `Circle r=3`.

### Further Maths Options (H645)

Reached via `Maths Toolkit > Further Maths > Options`.

| Section | Menu path | Tools provided |
| --- | --- | --- |
| Mechanics (FM) | Further Maths > Options > Mechanics (FM) | Momentum & impulse, Restitution, Work/Energy/Power, Circular motion, Hookes law / EPE, Centre of mass, Dimensional analysis |
| Statistics (FM) | Further Maths > Options > Statistics (FM) | Discrete RV E/Var, Poisson pmf/cdf, Binomial pmf/cdf, Normal P(a<X<b), Standardise z, Inverse Normal, PMCC r, Spearman rank, Regression y=a+bx, Chi-squared GOF, CI for mean, CI for proportion, z-test for mean |
| Numerical Methods | Further Maths > Options > Numerical Methods | Newton-Raphson, Fixed-point iteration, Bisection, Integration (trap/mid/Simp), Numerical derivative, Euler method, Error abs/relative, Round to s.f. |
| Modelling w/ Algorithms | Further Maths > Options > Modelling w/ Algorithms | Bubble sort, Insertion sort, Bin: first-fit, Bin: first-fit decr, Dijkstra shortest, Prim MST, Kruskal MST, Critical path |
| Extra Pure | Further Maths > Options > Extra Pure | Recurrence relation, Group theory, 2x2 Eigen/diag, Modular arithmetic, Partial deriv (num) |
| Further Pure w/ Tech | Further Maths > Options > Further Pure w/ Tech | Plot f(x) curve, De Moivre z^n, nth roots of z, Euler dy/dx=f(x,y), gcd & lcm, Prime test, Prime factorise, a^b mod m, Modular inverse, Base -> bin/hex |

In Extra Pure, `Modular arithmetic` opens its own sub-menu (`a mod m`, `a^b mod m`, `gcd(a,b)`, `modular inverse`).

---

## How it works (architecture)

The CAS is a small pipeline of single-purpose modules. A typed string becomes a tuple expression tree, the engine transforms that tree (simplify / differentiate / evaluate / print), and a separate typesetter draws it as real 2D maths on the screen. Every module is built around one hard constraint: stock MicroPython 1.9.4 on the fx-CG100 dies at roughly a 38-frame call-stack ceiling, so the parser is iterative and the tree walks are kept shallow (depth = expression nesting, never input length).

```
keys -> caslex.tokenize -> caslex.parse -> tuple tree
                                              |
        caseng (simplify / diff / evalf / tostr)
        cascalc (integrate / solve / definite integral)
                                              |
              casrender.render -> 2D typeset preview

  casui  = menus, keyboard, angle mode, paged result screens
  casutil = the helpers all 17 section modules share
```

### The tuple node format

The whole system passes around immutable tuples whose first element is a tag:

- Leaves: `('n', num)` for a number (int kept exact where possible), `('v', name)` for a variable or symbolic constant.
- Binary ops: `('+', a, b)`, `('-', a, b)`, `('*', a, b)`, `('/', a, b)`, `('^', a, b)`, where `a` and `b` are themselves nodes.
- Unary: `('neg', a)`, plus one-argument functions `('sin', a)`, `('cos', a)`, `('ln', a)`, `('sqrt', a)`, `('exp', a)`, the inverse and hyperbolic trig, `('abs', a)`, and postfix factorial `('fact', a)`.
- Two-argument functions: `('ncr', a, b)`, `('npr', a, b)`, `('logb', a, b)`.

Because nodes are plain tuples, the engine tests structure with cheap `node[0]` tag checks and `len(n) == 2` to tell unary from binary, and equality (`a == b`) compares whole subtrees for free.

### caslex - tokenizer and iterative parser

`tokenize` scans the string left to right into tokens (numbers, function names matched longest-first so `asinh` beats `asin` beats `sin`, single letters as variables, operators, parens, comma, postfix `!`). A number literal may carry a scientific-notation exponent (`1e3`, `2.5e-3`), consumed only when digits actually follow the `e`, so a bare `e` stays Euler's number. `pi` and `e` are folded to numeric tokens at this stage. `_implicit` then inserts explicit `*` tokens wherever multiplication is implied (`2x`, `2(x)`, `)(`, `x sin(...)`, `3!x`).

`parse` does unary-minus marking, then a classic shunting-yard pass to Reverse Polish using a precedence table (`+ - < * / < unary < ^`, with `^` and unary right-associative). A prefix unary minus is pushed straight onto the operator stack without popping: it binds only what follows it, so in `2^-3` the `^` has to stay pending until its right operand `-3` has been built. Popping there is what used to make every `a^-b` fail to parse. The RPN is turned into the tree by a second iterative pass over an explicit value stack: operands push leaves, operators pop their arguments and push a combined node. No recursion is used anywhere, so arbitrarily deep input cannot blow the stack. Malformed input - including an unbalanced `)` - returns `None` rather than raising.

### caseng - the engine over the trees

- `simplify` is a bottom-up rewrite (`_s`): it simplifies children first, then applies local rules (constant folding, identities like `x*1`, `x+0`, `x-x=0`, `a^0=1`, rational reduction via gcd in `_fold_div`, pulling constants to the front of products, folding `(k*X)/m` and `(p/q)/m` so an integral's constant lands in lowest terms, combining like powers `x^p * x^q -> x^(p+q)` and `x^p / x^q -> x^(p-q)`, and lifting a constant out of a denominator so `x^2/(2x)` reaches the power rule and becomes `x/2`. Those last three exist because integration by parts leans on them: without them an intermediate such as `(x^2/2) * (1/x)` never cancels and the method stalls one step short of closing). `_fold_pow` will not fold a power whose value cannot live in a tree: a fractional power of a negative base is complex, and a huge integer power would allocate megabytes on the handheld, so both are left symbolic. `2^-3` folds to the exact `1/8`. Each rule returns a strictly simpler or equal node, so it terminates.
- `diff` (`_d`) is the full A-Level rule set: sum/product/quotient/chain rules, power rule (including variable exponents), and derivatives of every supported function, `logb` included. It emits an unsimplified tree that the caller then runs through `simplify`. Where no elementary derivative exists and the argument really does involve the variable (`x!`, `nCr(x,2)`) it raises rather than returning a misleading `0`.
- `evalf` numerically evaluates a tree at a given `x`. A `deg` flag switches trig to degrees for the everyday calculator and the CAS evaluate/gradient/definite-integral/graph/table tools; the Further Maths section modules call it without the flag and stay in radians. An optional `env` map supplies values for variables other than `x`, which is how Euler's method evaluates `dy/dx = f(x, y)` on a one-variable engine. A variable with no value raises rather than evaluating to `0`, so a mistyped entry is reported instead of quietly becoming a wrong answer, and a power that would come out complex (such as `(-8)^(1/3)`) raises as a domain error rather than returning a complex number. Functions the device lacks (`sinh`, `asinh`, `factorial`, etc.) are implemented here iteratively from `math` primitives.
- `tostr` (`_str`) is the precedence-aware linear printer used for plain-text output, inserting parentheses only where needed.

These walks recurse on expression depth, which is small, so they stay well under the frame ceiling.

### cascalc - integration and solving

- `integ` does symbolic integration: linearity over `+ - neg`, constant factor pull-out, the power rule (with exact rational exponents, so `x^(2/3)` integrates to `3/5 x^(5/3)` rather than a decimal), the `-1` case as a logarithm, `c/(px+q) -> c ln(px+q)/p`, `f'(x)/f(x) -> ln f(x)` (decided by dividing the numerator by the derivative of the denominator and asking whether the variable has gone), and a table covering `sin`, `cos`, `exp`, `tan`, `sqrt`, `ln`, `sinh` and `cosh` - each of which also accepts a linear argument by substitution. Anything it cannot integrate returns `None`, which is the signal for the UI to fall back to numerics.
- **Integration by parts** (`_byparts`) applies `int u dv = uv - int v du`, picking `u` by LIATE. Two things make it terminate on a handheld. Products are flattened first, so `-cos(x) * (2*x)` is seen as a constant and two moving factors rather than as an opaque pair. And when the remaining integral turns out to be a constant multiple `k` of the one we started with - which is what happens to `sin x cos x`, where naive recursion never closes - it solves `I = uv - kI` for `I` instead of recursing. `e^(ax) sin(bx)` and its cosine form are handled by a direct closed form because their `k` is negative and the general trick is less accurate there. Depth is capped at `BYPARTS_MAX = 3`; the deepest real case measured is 8 stack frames against the device's ~38-frame ceiling, and `tests.py` asserts it.
- `linear_coeff` decides whether an argument is `a*var + b` **structurally**, by walking the tree. It used to sample the argument at `x = 0, 1, 2` and compare, which accepted anything that happened to agree with a straight line at those three points - `x^3-3x^2+3x` among them - so every integral built on that substitution came out silently wrong. `has_var` decides which factor is constant.
- `defint` is a numeric definite integral by composite Simpson's rule (even panel count, evaluated through `evalf`), returning `None` on a domain error or a non-finite total (a singularity inside the interval is reported rather than printed as junk).
- `solve` finds numeric roots of `tree == 0` over a computed grid of 800 samples (a wider window in degree mode for the 360 period). Sign changes are refined by bisection; a grid point that is a local minimum of `|f|` without a sign change is refined by ternary search, which is what finds roots the curve only touches, such as `x^2` or `(x-1)^2`. A constant expression returns no roots rather than one per grid point, duplicates within a tolerance are dropped, and the list is capped at `MAXROOTS`.

### casrender - 2D math typesetter

`casrender` turns a tree into a Desmos-style 2D layout instead of a flat string. It is a two-phase box model. `build` converts the tree into layout boxes (`atom`, `row`, `frac`, `sup` for exponents and `e^x`, `root` for radicals, `paren`, `dot`), choosing a smaller font as nesting deepens and inserting parentheses by precedence. `measure` returns each box's `(width, ascent, descent)` relative to a baseline, with stacked fractions sized around an axis line. `draw` then paints pixels (`set_pixel`, Bresenham lines for the surd stroke, drawn parentheses for tall content) at computed coordinates. `render` centres the result in a box and, if it does not fit, retries one font size down before giving up. This is what produces the live input preview as you type.

### casui - the UI hub

`casui.py` is the front end. It owns the key map decoded from the physical keyboard (code = row*10+col, with shift/alpha layers and a CATALOG picker for the few tokens no key produces; `tests.py` holds Casio's keypad table independently and asserts every binding against it, including that no code is claimed by both a navigation key and a character key), the main menus, the on-screen input editor that drives the live `casrender` preview, the global angle mode (shown on the input screen, since it changes what `sin(30)` means), and the pixel-based, word-wrapped result screens. Text layout is calibrated to the measured 384x192 screen using hand-tuned proportional-font width tables (`char_w` / `text_w`), so lines wrap by real pixel width rather than character count. The edit line is windowed around the caret by `cursor_fit`, so moving back into a long expression keeps the caret on screen instead of scrolling it away. Result screens page rather than truncate: output longer than seven lines shows a page counter, any key advances and EXIT stops. A fault inside a section tool is caught and reported, so it returns to the menu instead of dropping the whole toolkit back to the Python shell.

### Files at a glance

- `casutil.py` - helpers every section module shares: value entry, safe number and complex formatting, atan2/degrees/radians, gcd/lcm/modular arithmetic, exact nCr/nPr/factorial, and the normal, binomial and Poisson distributions.
- `caslex.py` - tokenizer plus iterative shunting-yard parser; produces the tuple tree.
- `caseng.py` - engine: simplify, differentiate, numeric evaluate, plain-text print.
- `cascalc.py` - symbolic integration, numeric solve (grid scan + bisection), numeric definite integral (Simpson).
- `casrender.py` - 2D math typesetter (fractions, exponents, radicals) for the live preview.
- `casui.py` - UI hub: menus, keyboard input, angle mode, pixel-wrapped result screens.
- `maths.py` - launcher (imports `casui` and calls `casui.main()`).
- 17 section modules - the H640 / H645 specification tools. Each one is a registry of `(label, function)` pairs in `TOOLS` plus a `run()` that hands it to `casutil.run_tools`; the test harnesses drive that registry, so a new tool is covered the moment it is listed.
- `tests.py`, `stress.py`, `devlint.py` - the PC-side harnesses (see [Development and testing](#development-and-testing)).

---

## Installing on the calculator

Copy these `.py` files to the calculator's storage (the root of the device, where MicroPython looks for modules):

- Launcher: `maths.py`
- UI layer: `casui.py`
- Engine: `caslex.py`, `caseng.py`, `casrender.py`, `cascalc.py`
- Shared section helpers: `casutil.py`
- The 17 section modules: `vcplx.py`, `matrix.py`, `vectors.py`, `polyroots.py`, `series.py`, `hyper.py`, `polar.py`, `diffeq.py`, `fmmech.py`, `fmstat.py`, `numeric.py`, `algos.py`, `xpure.py`, `fpt.py`, `pure640.py`, `stat640.py`, `mech640.py`

To launch the toolkit, run `maths.py` (it just imports `casui` and calls `casui.main()`; the engine and section modules are pulled in from there on demand).

**Do NOT copy `casioplot.py` from this repo to the device.** The repo's `casioplot.py` is a PC-only test stub (every function is a no-op). The fx-CG100 already has the real `casioplot` graphics module built in, and copying the stub would shadow it, breaking all drawing. The device runs stock MicroPython 1.9.4 with that built-in `casioplot`.

## Development and testing

The entire toolkit runs unmodified under desktop CPython. The only device-specific dependency is the `casioplot` graphics module, and the repo's `casioplot.py` stub satisfies that import with no-op drawing functions (`set_pixel`, `draw_string`, `clear_screen`, `show_screen`, `getkey`, etc.), so the code imports and executes on a PC.

There are three harnesses, all PC-side. Run them together before any change lands:

```
python3 tests.py       # correctness: 1250 checks, 0 failures
python3 stress.py      # smoke: 343 checks, 0 errors
python3 devlint.py     # device compliance: 0 problems in 30 files
```

All three run on every push and pull request via `.github/workflows/ci.yml`, along with a `compileall` pass over the whole repo. No dependencies beyond CPython.

**`tests.py` - correctness.** Every check compares against a value worked out
independently, so it catches wrong answers rather than only crashes. It covers
the tokenizer and parser, simplification, the full differentiation rule set,
symbolic and numeric integration (each symbolic integral is also re-checked
against Simpson's rule over the same interval), root finding, the typesetter,
the UI's number formatting and word wrap, all of `casutil`, and every section
module driven through its real entry points with scripted key input - so what
is asserted is what a student would see on screen. It finishes with a
recursion-depth guard that caps the interpreter at the handheld's ~38-frame
ceiling and confirms the engine still runs inside it.

**`stress.py` - smoke.** Stubs the UI (canned input, no-op drawing, auto-exiting
menus) so nothing blocks, then calls every tool in all 17 sections via each
module's `TOOLS` registry and hammers the engine over ~30 expressions. It proves
nothing crashes; it does not check that any answer is right. On a PC it writes
`stress_log.txt`; on the device (no file writes) it prints progress instead.

**`devlint.py` - device compliance.** Parses each of the 30 device files and
reports anything the calculator's MicroPython 1.9.4 cannot run: f-strings,
non-ASCII bytes, imports beyond `math`/`random`/`casioplot`, `math` members the
build lacks (`factorial`, `atan2`, the hyperbolics), annotations, walrus,
`async`, `yield from`, and newer string methods. Everything is an allowlist, so
a new dependency has to be added to `devlint.py` deliberately. `tests.py` runs
it too, so a change that would only fail on real hardware fails on the PC first.

`tests.py`, the `tests_*.py` modules and `devlint.py` are desktop-only (they use
`ast` and `sys._getframe`) and must not be copied to the calculator. `tests.py`
picks up any `tests_*.py` file automatically: each defines
`SECTIONS = [(label, function)]` and each function takes the harness object as
its only argument, which is how several areas can be worked on at once without
fighting over one file.

`calib_screen.py`, `fontmetrics.py`, and `fontmetrics2.py` are one-off hardware probes that were run on the real device to measure its display. `calib_screen.py` walks black pixels off each edge to detect the screen size (found to be 384x192). `fontmetrics.py` measures per-character advance and glyph height for the small/medium/large fonts and how many characters fit across the 384px width. `fontmetrics2.py` measures proportional glyph widths (narrow `i`, normal `o`, wide `m`) plus a real-prose average. These are not part of the toolkit; they were used to calibrate the layout constants.

### Device facts, and how each one was settled

Several constants in this repo used to be assumptions written without hardware
or documentation to hand. Where they have been settled, this is the evidence.
The source is the **fx-CG100/fx-1AU GRAPH Software User's Guide, version 2.10**
(CASIO, published 12/2025), [available from
CASIO](https://support.casio.com/global/en/calc/manual/fx-CG100_1AUGRAPH_en/);
the `casioplot` chapter is pages 141-143.

| Assumption | Status | Evidence |
| --- | --- | --- |
| `draw_string` size argument | **Confirmed** | Page 143: *"Specifies one of the following as the character size: 'large', 'medium', 'small'. 'medium' is applied when this argument is omitted."* The manual's own example passes `"large"`. `tests.py` now walks every device file with `ast` and asserts every literal size argument is one of the three. |
| Colour argument format | **Confirmed** | Page 143: *"The color argument specifies the drawing color in 256 shades of RGB... to specify black, input (0,0,0) or [0,0,0)."* Tuples of 0-255 are correct, and `(0,0,0)` is the default when omitted. |
| Key codes are `row*10+col` | **Confirmed** | Page 142 prints the grid: 9 rows, columns 1-6, with row 1 col 1 (`[ON]`) and row 6 col 5 (`[AC]`) greyed out as codeless, and rows 7-9 stopping at column 5. 48 readable keys. The manual's worked example holds the `5` key and prints `72`, which anchors the grid to the physical keypad. |
| Which key each code is | **Confirmed** | The page-142 diagram is a blank keypad outline, so the codes were matched to the printed keytops against a full-resolution photograph of the fx-CG100 front panel. Every binding in `casui.py` agrees: the cursor cross is 14/23/25/34 around `OK` 24, `EXIT` is the back-arrow at 22 (13 is jump-to-line-start), and the ALPHA letters run A-F on 41-46, G-L on 51-56, M-O on 61-63, P-T on 71-75, U-Y on 81-85, Z on 91, with `Ans` on 94. `tests.py` holds that table independently and asserts `casui` matches it. |
| `getkey()` idle value | **No longer relied on** | The manual documents `getkey()` as *"returns the key code of the calculator key pressed at the time this function is executed"* and its example polls it in a bare `while True`, so it is non-blocking - but it never states the idle return. The toolkit no longer needs to know: `casui.KEYCODES` is the set of codes the keypad can produce and `casui.readkey()` reports anything else as "no key". This also fixed a real bug - the old code sampled `getkey()` once at import and called that the idle value, but the key that launches the script is still held at import, which made that key unreadable for the whole session. |
| `math` members available | **Partly settled - `hwcheck.py` enumerates them** | The manual does not enumerate the `math` module; it is browsable on the device under `CATALOG > [math]`. What the manual does document (page 125, Python-mode key input) is `sqrt()`, `exp()`, `log()` (natural), `log10()`, `asin()`, `acos()`, `atan()` and `pi`. `devlint.MATH_OK` has deliberately **not** been widened past what the toolkit uses and the manual attests. |
| Recursion ceiling (~38 frames) | **Unverified - run `hwcheck.py`** | Needs the device. `tests.py` caps CPython at 38 frames and asserts parse/simplify/diff/evalf/integ still run, which is the property that matters (recursion on expression nesting, never on input length), but the true figure has not been measured. `hwcheck.py` measures it by counting frames until the interpreter refuses another, and also re-runs the engine's deepest operations at that real ceiling. |
| Pixel-level screen layout | **Unverified** | The autoscaling graph, the paged result screens, the CATALOG picker grid and caret windowing in long expressions were written from measured font metrics, not from screenshots. |

**`hwcheck.py` settles the three remaining rows in one run.** Copy it to the
calculator and run it: it measures the recursion ceiling by counting frames
until the interpreter refuses another, reports what `getkey()` returns with
nothing held, walks the screen bounds, enumerates which of 43 possible `math`
members this build has (and which it lacks), and finally re-runs the engine's
deepest operations - deeply nested parse, a 200-term flat sum, simplify,
differentiate, evaluate, print and integration by parts - at that real ceiling.
Write the figure it prints into the table above and into `tests.py`'s `BUDGET`
constant.

`keyprobe.py` re-checks the key map on hardware and flags any code outside
`casui.KEYCODES`; `calib_screen.py`, `fontmetrics.py` and `fontmetrics2.py`
measured the display.

### Device constraints the code works around

The fx-CG100's MicroPython 1.9.4 is a restricted build, so the code avoids:

- no f-strings (string building uses `+` and `str(...)`),
- ASCII-only text (no Unicode glyphs),
- only `math`, `random`, and `casioplot` are importable,
- no `math.factorial`, `math.atan2`, or `math.sinh`/hyperbolics (these are hand-implemented),
- a shallow recursion limit (~38 frames),
- the `complex` type has no `.conjugate()` method,
- file writes are blocked on the device.

## License

Released under the [MIT License](LICENSE).
