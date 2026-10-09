# Redesign: topics you type into, not 700 tools

Agreed with Sayer on 2026-10-09. Mockups: `docs/mockups/mockups.png` (1 to 10) and
`docs/mockups/mockups2.png` (A to I).

## Why

The old design was a list of single tools, each wanting values in a fixed comma
order. It had working CAS but was slow to navigate, rejected anything not in its
exact format (x^2 + 3x + k gave "no quadratic"), couldn't spot hidden forms, and
had gaps. Adding tools fixes the gaps. Only a new structure fixes the rest.

## The model

1. **Home** is a grid of topics (mockup A). One press to a topic.
   - Maths: Calculate, Algebra, Coord geometry, Sequences and series, Trig,
     Exp and logs, Calculus, Numerical, Vectors, Statistics, Kinematics, Forces,
     then Graph, Notes, Settings.
   - Further, only when the launch script switches it on: Complex, Matrices,
     3-D vectors (lines and planes), Polar, Hyperbolic, Differential equations,
     Groups and recurrences, Surfaces. Shared topics gain Further actions; for
     example, Calculus gets inverse trig and hyperbolic integrals, and Statistics
     gets the Y422 tests.
2. **In a topic you type the question as written** (mockups 1 to 4), in the
   natural editor. Letters are fine. Two rows are allowed, with DOWN adding a row,
   for pairs: simultaneous equations, f and g, a line and a curve.
3. **EXE**: the topic recognises what you typed. It shows what it found in grey
   ("quadratic in 2^x") and lists only the actions that fit. The 6 most likely
   actions show as tiles, and **More** has every action that fits (mockup I).
   Number keys pick tiles. Typing again edits the input.
4. **Labelled boxes only for what isn't one expression** (mockups 5, E): points,
   vectors, matrices, SUVAT, triangle sides and angles, AP/GP facts, forces. Fill
   in what you know and put `?` for what you want.
5. **An action asks only for what is missing** (mockup C), such as r for
   P(X >= r) or limits for a definite integral.
6. **Answer page**: the working in mark-scheme order, with the final answer boxed
   at the end (mockups 7 to 10). It scrolls when long.
   - One key hides or shows the working.
   - FORMAT flips the answer between exact and decimal.
   - Working is not a setting.
7. **Calculate** stays the type-anything screen. TOOLS there shows every action,
   from any topic, that fits the line.

### Rules that stop it going wrong (the physics-solver failure)

- Recognition is a **fixed list of forms**, each tested on real past-paper
  inputs. There is no guessing at intent.
- It always **shows what it detected**, and it never silently changes what you
  typed.
- **Nothing is unreachable**: More always lists everything that fits, and an
  action that can't apply is never shown.
- The calculator can't read the question. It works from the form of what you
  typed, so ambiguous cases list every reading.

## Recognised forms (first pass)

| Topic | Forms |
|---|---|
| Algebra | polynomial in x (any degree, letter coefficients); quadratic in f(x) (x^4, sqrt x, x^(2/3), 1/x); rational p/q; modulus; inequality; surd/index arithmetic (no x); two equations |
| Coord geometry | points; line (any form); circle (any form); parametric pair; two of these |
| Sequences | u_n formula; recurrence + u_1; AP/GP fact boxes; sigma sum; (a + bx)^n |
| Trig | equation in sin/cos/tan (+ interval asked); identity to check; a cos x + b sin x; triangle boxes; arc/sector boxes |
| Exp and logs | exponential equation (one base, two bases, quadratic in a^x); log equation; log expression; two unknowns (2^x + 3^y = 15); model from two points |
| Calculus | y = f(x); implicit F(x, y) = 0; parametric x(t), y(t); dy/dx = ... (DE); two curves (area between) |
| Numerical | f(x) = 0; x = g(x); y values (trapezium) |
| Vectors | vectors (i, j, k or column); points; two vectors |
| Statistics | data list; two lists (bivariate); B(n, p); N(mu, sigma^2); hypothesis test boxes |
| Kinematics | SUVAT boxes; v/s/a as a function of t (also vector); projectile boxes |
| Forces | forces list (resultant/equilibrium); slope, pulley and connected particles; beam (moments) |

## Actions

Each action reuses an existing tool function or CAS op as its engine (about 700
already tested, including 1,389 past-paper checks), wrapped so that:
- it takes the recognised form, not a comma list;
- it writes mark-scheme working;
- it accepts letters wherever the maths allows.

Trivial one-formula tools (moment = F x d and the like) are not offered as
actions; they become steps inside the forms that need them. The old tool menus
stay under More > All tools until every topic covers them, then they go.

Priority comes from the 48 audited past papers: the actions behind the most
calculator-assisted marks are done first, and each gets its step writer.

## Settings (mockup H)

- Angle
- Answers: exact, decimal or both
- Decimals: s.f. or d.p.
- Complex form: a + bi or polar
- Sleep time
- Key repeat

The calculator can't save files, so the **launch script holds the defaults**
(`maths.py` / `module.py`), including `FURTHER = False`. The Settings page
changes them until you exit.

## Limits we design around

- **Memory:** modules can't be unloaded (there is no `sys`), so everything loaded
  stays loaded. Topics must be small and lazy, and caches are dropped on HOME.
  Measure with `probe.py` before building.
- **Speed:** parsing costs about 150 ms per formula on the calculator. Recognition
  must run off the parse and nothing heavier. Heavy calculus may take seconds,
  with Busy shown.
- **Font:** mockups use a PC font; the calculator's differs a little.

## Testing each round

- **Laptop:** the existing suites, plus an acceptance suite that drives the new
  flow ("type X in topic T, pick action A, answer the missing-value prompt")
  for every calculator-assisted past-paper part, checked against the mark scheme.
- **Calculator:** a `selftest.py` run shows pass/fail per case and memory left
  (one photo). Then a 5-minute checklist of feel, speed and freezes.

## Build order

1. Framework: topic screen, recogniser, action registry, answer page, launch
   script settings. Then Algebra, Exp and logs, Coord geometry and Calculus,
   with working.
2. Trig, Sequences, Numerical, Vectors.
3. Statistics, Kinematics, Forces (forms).
4. The Further topics behind the switch.
5. Remove the old menus once nothing depends on them.
