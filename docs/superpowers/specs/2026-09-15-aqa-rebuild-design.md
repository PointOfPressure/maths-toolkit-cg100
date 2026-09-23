# AQA rebuild of the fx-CG100 Maths Toolkit — design and module contract

Date: 2026-09-15. Branch `aqa`. Replaces the OCR B (MEI) toolkit with one
mapped to **AQA A-level Mathematics 7357** and **AQA A-level Further
Mathematics 7367 (Mechanics + Statistics options)**.

Decisions taken with Sayer (2026-09-15):

| Topic | Decision |
|---|---|
| Scope | Keep the engine (parser, CAS, typesetter). Rebuild the topic tree, every tool screen, and the shared UI. Drop MEI-only tools. |
| Formatting faults | Text ran off the edge, ugly decimals, misaligned 2D preview, too few lines per screen. |
| Slowness | Keypress/redraw lag, one value per prompt, menu depth, "any key = more" paging. |
| Text | No help/intro screens, no prose in results. Working kept but hidden by default. |
| Input | One line, comma-separated values per tool. |
| Answers | Exact when the maths is exact (fractions, surds, pi multiples, a+bi), else 3 s.f. |
| Build order | Shared UI first, then everything. |
| Density | Small font for lists/working, medium for answer lines. |
| Menu tree | Home > qualification > AQA section > tool. |
| Old files | Delete everything the new toolkit replaces from the calculator. |
| Repo | Branch `aqa` in `PointOfPressure/maths-toolkit-cg100`, checked out at `~/dev/cg100/toolkit`. Push only when Sayer says. |
| Testing | PC only; Sayer copies files to the calculator himself. |
| Calculate + CAS modes | Kept, same clean-up. Calculate understands `i`. |
| Working reveal | FORMAT key on the result screen cycles: answer / +working / +full precision. |
| Additions | Matrix entry as a grid preview, plot with pan/zoom/trace (cartesian, polar, parametric, points), AQA formulae booklet browsable on the calculator. |
| Coverage | Every 7357 and 7367 (Core Pure + Mechanics + Statistics) spec point a calculator can help with. |

Exam mode hides storage memory, so the toolkit is a homework and revision
tool by construction. Nothing here targets exam use.

## Hardware and runtime facts (measured, from SPEC_AUDIT.md and the manual)

- MicroPython 1.9.4. Importable modules: `math`, `random`, `casioplot`, and
  our own files. No f-strings, no walrus, no annotations, no `yield from`,
  ASCII only. `devlint.py` enforces this and pins the `math` members that exist.
- Screen 384 x 192. `casioplot`: `set_pixel`, `get_pixel`, `draw_string(x, y,
  s, color, size)` with sizes small/medium/large, `clear_screen`,
  `show_screen`, `getkey()` (idle returns None; codes `row*10+col`).
- There is **no fill-rectangle primitive**. A filled highlight is thousands of
  `set_pixel` calls. Rule: no filled rectangles anywhere. Selection is a `>`
  marker plus accent-coloured text.
- `draw_string` widths: `casrender.cw(ch, size)` is the one metric (measured on
  hardware). Small ~7 px/char average (54 chars per line), medium ~10 px.
- Recursion ceiling 92 frames. Python `complex` exists on the device (the
  keypad inputs `1j`), `cmath` does not.
- Files transferred over USB may exceed 300 lines; only the on-device editor
  has that limit.

## Files on the device

| File | Role |
|---|---|
| `maths.py` | launcher: `import casui; casui.main()` |
| `casui.py` | keys, menus, line editor, result screen, home |
| `casutil.py` | tool runner, field parsing, `fmt`, numeric/stat helpers, chart primitives |
| `caslex.py` | tokeniser + parser (now with `i`, symbolic `pi` and `e`) |
| `caseng.py` | simplify (with exact trig at standard angles), differentiate, evalf (complex-aware), tostr |
| `cascalc.py` | integrate, solve, definite integral |
| `caspoly.py` | exact rational polynomial algebra, factor, partial fractions |
| `casrender.py` | 2D typesetter |
| `plot.py` | cartesian / polar / parametric / point plotter with pan, zoom, trace |
| `formulae.py` | AQA formulae booklet as data |
| `tables.py` | critical-value tables (Normal percentage points, t, chi-squared, PMCC) with lookup functions |
| `mpure.py` | 7357 sections A–F |
| `mcalc.py` | 7357 sections G–J |
| `mstat.py` | 7357 sections K–O |
| `mmech.py` | 7357 sections P–S |
| `fcore.py` | 7367 sections A–D |
| `fcalc.py` | 7367 sections E–J |
| `fmech.py` | 7367 sections MA–ME |
| `fstat.py` | 7367 sections SA–SH |

PC-only: `casioplot.py` (stub), `casioshot.py` (PNG renderer), `tests.py`,
`tests_*.py`, `stress.py`, `devlint.py`, `deploy.sh`.

Everything else in the old repo root (MEI modules, probes, June-era files)
is deleted from the repo and from the calculator.

## Section module contract

Every section module exposes exactly one public name:

```python
SECTIONS = [
    ('B', 'Algebra and functions', [
        ('Quadratic', 'a,b,c', t_quadratic),
        ('Simultaneous 2 linear', 'a1,b1,c1,a2,b2,c2', t_simul2),
        ('Solve f(x)=g(x)', 'f(x),g(x)', t_meet),
        ('Summary stats', 'data*', t_summary),
        ('Determinant', 'A[3x3]', t_det),
    ]),
    ('C', 'Coordinate geometry', [ ... ]),
]
```

A tool is `(label, fields, fn)`.

- `label`: <= 22 characters, plain ASCII, no code letters.
- `fields`: the prompt the user sees and the parse spec. Comma-separated
  names. The user types comma-separated values on one line. Types by name:
  - `a` (plain name): a number. Parsed with `caslex.parse`, evaluated with
    `caseng.evalf`; may be `int`, `float` or `complex` (the user can type
    `2+3i`, `pi/4`, `sqrt(2)`). Tools that need a real number get one:
    the runner raises "a must be real" for complex input unless the name ends
    in `z` or is `z`, `w`, `z1`, `z2`.
  - `f(x)`, `g(x)`, `r(t)`, `x(t)`, `y(t)`, `f(x,y)`, `p(x)`: any name containing
    `(` is an **expression** and is passed as a parse tree, unevaluated.
  - `data*` (name ending `*`): a **list** of numbers; consumes all remaining
    values. Must be the last field. Minimum one value.
  - `A[2x2]`, `A[3x3]`, `v[3]`, `v[2]`: a **matrix** (list of row lists) or
    **vector** (list); consumes 4/9/3/2 numbers. The editor shows a live
    grid preview while these are typed.
  - `g?` (name ending `?`): optional; `None` if the user stops early. Only
    trailing fields may be optional.
- `fn(*values)`: called with one positional argument per field, in order. It
  returns a **list of lines** (may be empty). It may raise `ValueError(msg)`;
  the runner shows `msg` in red. Any other exception is shown as
  `error: <text>`. `fn` must be pure: the runner calls it again to re-render
  at full precision.

Line kinds:

- `'text'`: an **answer** line. Medium font, black. The first answer line is
  the headline.
- `('w', 'text')`: a **working** line. Small font, grey. Hidden until the user
  presses FORMAT.
- `('!', 'text')`: a **caveat**. Small font, red. Always shown. Use for domain
  restrictions, "no real roots", "table has no entry for n = 3".
- `('m', tree)`: an answer typeset by `casrender` (fractions, powers, roots).
  Falls back to `caseng.tostr` when it does not fit.
- `('mw', tree)`: a typeset working line.

Lines are never wrapped by hand. Keep answer lines under 36 characters and
working lines under 52; the result screen scrolls vertically if there is
more than fits, and the runner truncates with `..` rather than wrap.

Formatting numbers inside lines: always `casutil.fmt(v)`. Never `str(v)`,
never `round`. `fmt` returns exact forms when it can (`1/3`, `2*sqrt(2)`,
`pi/4`, `3+2i`) and 3 s.f. otherwise; in full-precision mode it returns up to
10 s.f. `casutil.fmt(v, sf)` overrides the significant figures. Use
`casutil.fmtv([1,2,3])` for a vector `(1, 2, 3)` and `casutil.fmtm(rows)` for
matrix rows (one line per row, `[a b c]`).

Plots: a tool that draws calls `plot.run(...)` (see below) and returns the
lines to show afterwards (usually the numbers behind the plot). Charts that
are not curves (histogram, box plot, Argand points) use `plot.run` with
`kind='points'` or `kind='bars'`.

Tools needing a second decision (e.g. "which transformation?") use
`casutil.pick(title, options)` which returns an index or `None`, or split
into several tools. Prefer several tools.

Tool functions live in the module as `t_<name>`. Helpers are private
(`_name`). No module-level state except constants and tables.

## Shared API (casutil)

```python
fmt(v, sf=None)        # exact-or-3sf string for int/float/complex
fmtv(seq)              # "(1, 2, 3)"
fmtm(rows)             # ["[1 2]", "[3 4]"]
sf3(v)                 # plain 3 s.f. decimal, never exact
w(text)                # ('w', text)
warn(text)             # ('!', text)
m(tree)                # ('m', tree)
pick(title, options)   # menu inside a tool; index or None
ask(fields)            # prompt for one more line; returns converted values or None
ev(tree, x=0.0, env=None)   # evalf with pi/e/ans; raises ValueError on maths errors
real(tree_or_value)    # float or raise ValueError('not real')
# numeric helpers kept from the old casutil: gcd, lcm, fact, ncr, npr, erf, phi,
# invphi, poisson_pmf/cdf, binom_pmf/cdf, atan2, nice_range
```

`casutil.FULL` is the full-precision flag the runner toggles; `fmt` reads it.

## plot API

```python
plot.run(curves, xlo=-6.0, xhi=6.0, kind='y', title='')
# kind='y':      curves = [tree, ...]              y = f(x)
# kind='polar':  curves = [tree, ...]              r = f(x), x is theta, 0..2pi
# kind='param':  curves = [(xtree, ytree, tlo, thi), ...]
# kind='points': curves = [(x, y), ...]            markers only
# kind='bars':   curves = [(xlo, xhi, height), ...]
# kind='lines':  curves = [[(x, y), (x, y), None, (x, y), ...], ...]
#                each list is one colour; points joined, None breaks the line
```

Keys inside a plot: arrows pan a quarter of the range, `+`/`-` zoom by 2,
OK/EXE toggles trace (then left/right move the cursor and the header shows
x and y), `0` resets, EXIT returns. Axes drawn with end labels only.

## Screens (casui)

Colours: text black `(0,0,0)`, accent `(40,120,220)`, grey `(120,120,120)`,
red `(205,60,60)`, white background (a dark background would be a 73k-pixel
fill).

Menu: title small grey at (4,2); right-aligned hint `n/N` when scrolling.
Rows small font from y=16, pitch 13, 13 rows visible. Selected row: `>` at
x=4 in accent, label in accent. Rows 1–9 prefixed with their digit for digit
jump. Keys: up/down (wrap), page up/down, `|<-`/`->|` first/last, digits, OK/EXE
choose, EXIT back. Section menus show `B Algebra and functions`.

Input: line 1 small grey: tool label. Line 2 small black: the field list
(`a, b, c`). Typed text medium at y=38 with `|` caret, windowed horizontally
around the caret. Line at y=64 small grey: `UP recall  MENU symbols`. Grid
preview (matrix/vector fields) or the parsed value list from y=80 in small.
Keys as before: digits/operators, ALPHA letters, SHIFT functions, MENU opens
the symbol list (a plain menu, not a palette), UP recalls the last entry for
this tool, DOWN clears, DEL deletes, EXIT clears then cancels, OK/EXE submits.
No re-parse on every keystroke: the preview updates only the parsed value
list, which is a split on commas.

Result: line 1 small grey: `label  values` (values as typed, windowed).
Body from y=16: answer lines medium (pitch 18), typeset trees at their
measured height, caveats small red (pitch 12), working small grey (pitch 12)
when revealed. Footer y=180 small grey: `FORMAT working` / `FORMAT digits` /
`FORMAT less` per state, and `k/N` pager when scrolling. Keys: up/down
scroll one row, FORMAT cycles state, EXIT/OK/EXE back to the input for the
same tool (so the user can re-run with new values), EXIT again to the menu.

Home: `Calculate`, `CAS f(x)`, `Maths 7357`, `Further 7367`, `Formulae`,
`Angle: RAD`. Angle mode applies to trig in Calculate, CAS numeric
operations and tools that say so; calculus is always radians.

Calculate: input (`ans` holds the last value), result shows the typeset input,
the answer in medium (exact form first, decimal under it when different).
Complex results as `a+bi`, and mod/arg on a working line.

CAS: input f(x), then a menu: d/dx, d2/dx2, integrate, definite a..b,
tangent+normal at a, stationary points, simplify, expand, factorise, partial
fractions, solve f(x)=0, solve f(x)=k, evaluate, table, plot. Each shows a
result screen and returns to the menu.

## Engine changes

- `caslex`: `i` -> `('n', 1j)`; `pi` -> `('v','pi')`; `e` -> `('v','e')`;
  new unary functions `arg`, `conj`, `re`, `im` (and `mod` as an alias of
  `abs`). Word list stays longest-first.
- `caseng.evalf`: `pi`/`e` resolve to constants; complex arithmetic native;
  `sqrt`, `exp`, `ln`, `sin`, `cos`, `abs`, `^` handle complex inputs by hand
  (polar form). `arg`, `conj`, `re`, `im` implemented. `sqrt` of a negative
  real returns a complex. Angle mode affects only real trig.
- `caseng.simplify`: constant rules skip complex constants; `e^x` becomes
  `exp(x)`; `sin`/`cos`/`tan` of a rational multiple of `pi` with denominator
  1, 2, 3, 4 or 6 fold to the exact value (`sqrt(3)/2`, `1/2`, `-1`, ...);
  `tan` at odd multiples of `pi/2` becomes a caveat at evaluation, not a fold.
- `caseng.tostr`: `('v','pi')` prints `pi`, `exp(x)` prints `e^x`,
  complex constants print `a+bi`.
- `casrender`: unchanged except: `pi` as an atom, complex atoms, and a fix
  for the superscript/fraction vertical alignment (verify with PNGs).

## Tests and checks

- `tests.py` runs engine checks plus, for every section module, the cases in
  `tests_<module>.py`:
  ```python
  CASES = [
      ('B', 'Quadratic', '1,-3,2', ['x = 1', 'x = 2']),
      ('B', 'Quadratic', '1,2,5', ['-1+2i', '-1-2i']),
  ]
  ```
  Each case runs the tool through the real field parser and asserts every
  needle appears in the joined output (answers + working + caveats). A tool
  with no case fails the suite. `tests.py` also asserts every `fn` is pure
  (same output twice) and every label fits.
- `stress.py` drives every tool with a fixed bank of odd inputs (zeros,
  negatives, huge, tiny, complex, wrong arity) and fails on anything other
  than a clean `ValueError`.
- `devlint.py` checks MicroPython compliance for the device file list.
- `casioshot.py` renders named scenes to `shots/*.png` for review.
- `deploy.sh <mountpoint>` deletes every `*.py` in the calculator root that is
  not in the device list and copies the device files in.

## Coverage plan (tools per section)

Every spec point that a calculator can help with gets at least one tool. The
module author reads the spec points (`docs/spec-7357.txt`,
`docs/spec-7367.txt`) and the old MEI modules for reusable maths, then writes
the tools. Points that are pure reasoning (e.g. 7357 K1 sampling, M3
modelling critique) get no tool, and `SPEC_AUDIT.md` lists them.
