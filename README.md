# Maths Toolkit for the Casio fx-CG100

A from-scratch visual mathematics toolkit for the Casio fx-CG100 graphing calculator, written in stock MicroPython with the built-in `casioplot` graphics module. It bundles three things in one app:

- an everyday scientific **Calculate** mode,
- a from-scratch **computer algebra system (CAS)** that differentiates, integrates, simplifies, solves and graphs, and
- full tool coverage of the **OCR B (MEI) A-Level Maths (H640)** and **Further Maths (H645)** specifications,

all driven by an on-screen keyboard and a custom 2D math typesetter (Desmos-style fractions, exponents and radicals).

![platform](https://img.shields.io/badge/platform-Casio%20fx--CG100-blue)
![runtime](https://img.shields.io/badge/MicroPython-1.9.4-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)
![tests](https://img.shields.io/badge/stress-243%20checks%2C%200%20errors-brightgreen)

Built and verified on real hardware. The whole toolkit also runs unmodified on a desktop under CPython (via a small `casioplot` stub) for development and testing.

## Quick start

1. Copy the device `.py` files to your fx-CG100 (everything **except** `casioplot.py`). See [Installing on the calculator](#installing-on-the-calculator).
2. In the calculator's Python app, run **`maths.py`**.
3. Navigate with the arrow keys and OK; EXIT goes back. Type expressions on the normal keys; use ALPHA or the MENU picker for letters and symbols.

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

The `Calculus & Algebra` mode (`cas_section`) works on a function of `x`. Type an expression (for example `x^2+3x` or `sin(x)`), press OK, then choose an operation from the menu. Variables other than `x` can be entered with ALPHA or the MENU picker. The differentiation, integration and simplify operations are fully symbolic; the rest are numeric and honour the home-menu angle mode.

- **Differentiate (d/dx)** - symbolic derivative with respect to `x`, then simplified. Full rule set: sum, difference, product, quotient and power/chain rules, plus derivatives of sin, cos, tan, exp, ln, log, sqrt, asin, acos, atan, the hyperbolics sinh/cosh/tanh, the inverse hyperbolics asinh/acosh/atanh, and abs.
- **Gradient at a point** (`do_gradient`) - numeric slope `f'(x)` at a value you supply, computed by a symmetric central difference.
- **Integrate (+ C)** - symbolic indefinite integral, simplified and shown with the constant of integration. If there is no elementary form it says so and points you to the definite integral for a numeric area.
- **Definite integral a..b** (`do_defint`) - numeric area between two limits you enter.
- **Simplify** - applies the engine's local algebraic simplification rules (folds constants, removes `*1`, `+0`, `^1`, `^0`, combines like terms, reduces fractions to lowest terms, etc.).
- **Solve f(x)=0** (`do_solve`) - finds real roots over a search range. Accepts either an expression (solved against zero) or a full equation with `=` (the two sides are subtracted first). Roots are listed; if none are found in range it says so.
- **Evaluate at x** (`do_eval`) - asks for a value of `x` and prints `f(x)`, formatted with the same smart number rules as Calculate.
- **Graph** - plots `y = f(x)` to the screen with axes, sampling the function across the view.
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
| Vectors & 3-D | Further Maths > Core Pure > Vectors & 3-D | Magnitude, Dot product a.b, Angle between, Cross product a x b, Unit vector, Scalar projection, Parallel / perp test, Point to plane dist, Angle between planes, Skew lines distance |
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
| Further Pure w/ Tech | Further Maths > Options > Further Pure w/ Tech | Plot f(x) curve, De Moivre z^n, nth roots of z, Euler dy/dx=f(x), gcd & lcm, Prime test, Prime factorise, a^b mod m, Modular inverse, Base -> bin/hex |

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
```

### The tuple node format

The whole system passes around immutable tuples whose first element is a tag:

- Leaves: `('n', num)` for a number (int kept exact where possible), `('v', name)` for a variable or symbolic constant.
- Binary ops: `('+', a, b)`, `('-', a, b)`, `('*', a, b)`, `('/', a, b)`, `('^', a, b)`, where `a` and `b` are themselves nodes.
- Unary: `('neg', a)`, plus one-argument functions `('sin', a)`, `('cos', a)`, `('ln', a)`, `('sqrt', a)`, `('exp', a)`, the inverse and hyperbolic trig, `('abs', a)`, and postfix factorial `('fact', a)`.
- Two-argument functions: `('ncr', a, b)`, `('npr', a, b)`, `('logb', a, b)`.

Because nodes are plain tuples, the engine tests structure with cheap `node[0]` tag checks and `len(n) == 2` to tell unary from binary, and equality (`a == b`) compares whole subtrees for free.

### caslex - tokenizer and iterative parser

`tokenize` scans the string left to right into tokens (numbers, function names matched longest-first so `asinh` beats `asin` beats `sin`, single letters as variables, operators, parens, comma, postfix `!`). `pi` and `e` are folded to numeric tokens at this stage. `_implicit` then inserts explicit `*` tokens wherever multiplication is implied (`2x`, `2(x)`, `)(`, `x sin(...)`).

`parse` does unary-minus marking, then a classic shunting-yard pass to Reverse Polish using a precedence table (`+ - < * / < unary < ^`, with `^` and unary right-associative). The RPN is turned into the tree by a second iterative pass over an explicit value stack: operands push leaves, operators pop their arguments and push a combined node. No recursion is used anywhere, so arbitrarily deep input cannot blow the stack. Malformed input returns `None` rather than raising.

### caseng - the engine over the trees

- `simplify` is a bottom-up rewrite (`_s`): it simplifies children first, then applies local rules (constant folding, identities like `x*1`, `x+0`, `x-x=0`, `a^0=1`, rational reduction via gcd in `_fold_div`, pulling constants to the front of products). Each rule returns a strictly simpler or equal node, so it terminates.
- `diff` (`_d`) is the full A-Level rule set: sum/product/quotient/chain rules, power rule (including variable exponents), and derivatives of every supported function. It emits an unsimplified tree that the caller then runs through `simplify`.
- `evalf` numerically evaluates a tree at a given `x`. A `deg` flag switches trig to degrees for the everyday calculator and CAS evaluate/graph; the Further Maths section modules call it without the flag and stay in radians. Functions the device lacks (`sinh`, `asinh`, `factorial`, etc.) are implemented here iteratively from `math` primitives.
- `tostr` (`_str`) is the precedence-aware linear printer used for plain-text output, inserting parentheses only where needed.

These walks recurse on expression depth, which is small, so they stay well under the frame ceiling.

### cascalc - integration and solving

- `integ` does symbolic integration: linearity over `+ - neg`, constant factor pull-out, the power rule, a small table (`sin`, `cos`, `exp`, `1/x -> ln x`), and a linear-argument substitution. `linear_coeff` detects `a*var + b` by sampling the argument at three points, and `has_var` decides which factor is constant. Anything it cannot integrate returns `None`, which is the signal for the UI to fall back to numerics.
- `defint` is a numeric definite integral by composite Simpson's rule (even panel count, evaluated through `evalf`), returning `None` on a domain error.
- `solve` finds numeric roots of `tree == 0` by scanning a grid (wider window in degree mode for the 360 period), detecting sign changes, and refining each with `_bisect` (60-iteration bisection). Duplicate roots within a tolerance are dropped.

### casrender - 2D math typesetter

`casrender` turns a tree into a Desmos-style 2D layout instead of a flat string. It is a two-phase box model. `build` converts the tree into layout boxes (`atom`, `row`, `frac`, `sup` for exponents and `e^x`, `root` for radicals, `paren`, `dot`), choosing a smaller font as nesting deepens and inserting parentheses by precedence. `measure` returns each box's `(width, ascent, descent)` relative to a baseline, with stacked fractions sized around an axis line. `draw` then paints pixels (`set_pixel`, Bresenham lines for the surd stroke, drawn parentheses for tall content) at computed coordinates. `render` centres the result in a box and, if it does not fit, retries one font size down before giving up. This is what produces the live input preview as you type.

### casui - the UI hub

`casui.py` is the front end. It owns the key map decoded from the physical keyboard (code = row*10+col, with shift/alpha layers and a MENU picker for symbols that have no obvious key), the main menus, the on-screen input editor that drives the live `casrender` preview, the global angle mode, and the pixel-based, word-wrapped result screens. Text layout is calibrated to the measured 384x192 screen using hand-tuned proportional-font width tables (`char_w` / `text_w`), so lines wrap by real pixel width rather than character count.

### Files at a glance

- `caslex.py` - tokenizer plus iterative shunting-yard parser; produces the tuple tree.
- `caseng.py` - engine: simplify, differentiate, numeric evaluate, plain-text print.
- `cascalc.py` - symbolic integration, numeric solve (grid scan + bisection), numeric definite integral (Simpson).
- `casrender.py` - 2D math typesetter (fractions, exponents, radicals) for the live preview.
- `casui.py` - UI hub: menus, keyboard input, angle mode, pixel-wrapped result screens.
- `maths.py` - launcher (imports `casui` and calls `casui.main()`).
- 17 section modules - the H640 / H645 specification tools.

---

## Installing on the calculator

Copy these `.py` files to the calculator's storage (the root of the device, where MicroPython looks for modules):

- Launcher: `maths.py`
- UI layer: `casui.py`
- Engine: `caslex.py`, `caseng.py`, `casrender.py`, `cascalc.py`
- The 17 section modules: `vcplx.py`, `matrix.py`, `vectors.py`, `polyroots.py`, `series.py`, `hyper.py`, `polar.py`, `diffeq.py`, `fmmech.py`, `fmstat.py`, `numeric.py`, `algos.py`, `xpure.py`, `fpt.py`, `pure640.py`, `stat640.py`, `mech640.py`

To launch the toolkit, run `maths.py` (it just imports `casui` and calls `casui.main()`; the engine and section modules are pulled in from there on demand).

**Do NOT copy `casioplot.py` from this repo to the device.** The repo's `casioplot.py` is a PC-only test stub (every function is a no-op). The fx-CG100 already has the real `casioplot` graphics module built in, and copying the stub would shadow it, breaking all drawing. The device runs stock MicroPython 1.9.4 with that built-in `casioplot`.

## Development and testing

The entire toolkit runs unmodified under desktop CPython. The only device-specific dependency is the `casioplot` graphics module, and the repo's `casioplot.py` stub satisfies that import with no-op drawing functions (`set_pixel`, `draw_string`, `clear_screen`, `show_screen`, `getkey`, etc.), so the code imports and executes on a PC.

`stress.py` is a non-interactive test harness. It stubs out the UI (canned input strings, no-op drawing, auto-exiting menus) so nothing blocks, then:

- imports all 17 section modules,
- calls every tool function in each module (every `t_*` callable),
- runs an engine battery over ~24 expressions, exercising `parse`, `evalf`, `diff`, `simplify`, `integ`, and `solve` on each,
- wraps every call so errors are logged rather than fatal, and reports a total check count and error count (currently **243 checks, 0 errors**).

Run it with `python stress.py`; on a PC it writes `stress_log.txt`, and on the device (no file writes) it prints progress instead.

`calib_screen.py`, `fontmetrics.py`, and `fontmetrics2.py` are one-off hardware probes that were run on the real device to measure its display. `calib_screen.py` walks black pixels off each edge to detect the screen size (found to be 384x192). `fontmetrics.py` measures per-character advance and glyph height for the small/medium/large fonts and how many characters fit across the 384px width. `fontmetrics2.py` measures proportional glyph widths (narrow `i`, normal `o`, wide `m`) plus a real-prose average. These are not part of the toolkit; they were used to calibrate the layout constants.

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
