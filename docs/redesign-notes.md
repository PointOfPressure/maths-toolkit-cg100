# Redesign: decisions where the spec is silent

Companion to `docs/redesign.md`. Each entry is the simplest robust choice made
while building; change any of them by saying so.

## Keys

- **Topic screen, typing:** the natural editor as before (MENU = symbols).
  DOWN on the first row (outside a fraction) opens or moves to a second row;
  UP goes back, and an empty second row disappears. EXE reads the form.
  TOOLS reads the form and opens More straight away. EXIT leaves the topic
  (the typed rows are kept for next time).
- **Topic screen, tiles showing:** number keys 1-6 run that tile; arrows move
  between tiles; EXE/OK runs the selected one; TOOLS opens More. UP from the
  top row of tiles, EXIT, DEL or any typing key goes back to editing (the key
  is applied). Digits beyond the tiles shown also go back to typing.
- **Answer page:** UP/DOWN scroll a line, PAGEUP/PAGEDOWN a screen.
  **TOOLS hides or shows the working** (the status bar says `working` or
  `answer`). **FORMAT** flips the boxed answer: with Answers = exact + decimal
  it goes both -> exact -> decimal -> both; otherwise exact <-> decimal.
  EXE, OK or EXIT go back. Working is shown each time a page opens.
- **Prompts (mockup C):** UP/DOWN move between boxes, EXE works it out (or
  jumps to the first empty box). `?` (from MENU) means "no limit" where a box
  says so.
- **SETTINGS** opens the Settings page from any screen; **HOME** goes home from
  any screen.
- **Coord geometry:** the point boxes A and B (mockup 5). LEFT/RIGHT at the
  end of a box move to the other box of the point; UP/DOWN move between rows
  (keeping the x or y column). **MENU on a point row adds a point** (C, at
  most three); DEL in the empty boxes of the last point removes it. Below
  the points, a row for a line or circle typed as written; DOWN from it
  adds a second row. EXE, the tiles, More and the answer page as in every
  topic.
- **Fact boxes (Trig, and later Sequences and Vectors):** EXE with nothing
  typed shows the box forms as tiles (Triangle, Arc and sector). A box form
  is a grid of labelled boxes (mockup F): fill in what you know, `?` (from
  MENU) for what you want, empty for neither. LEFT/RIGHT at the end of a box
  and UP/DOWN move between boxes; EXE works it out. With no `?`, every
  value not given is boxed.
- **Sequences and series:** typed like Algebra. A recurrence is
  `u(n+1) = 3 - u(n)^2` or just `u = 3 - u^2` (u on both sides); u(1) is
  asked by the action. A formula in n, r or k is a u(n) formula or the term
  of a sum; `(a + bx)^n` a binomial expansion. Nothing typed: AP facts and
  GP facts boxes.
- **Numerical:** typed like Algebra: f(x), an equation (moved to one side),
  x = g(x) (x on both sides: iteration), or y values with commas between
  (the trapezium rule asks for h). The start value is x(1); iterates are
  x(2), x(3), ...
- **Vectors:** a row is a vector, `3i + 4j - k` (ALPHA i, j, k) or in
  brackets with the comma key, `(3, 4)`, `(3, 4, -1)`; DOWN adds a second
  (a and b, or the position vectors of A and B). Nothing typed: the
  Quadrilateral ABCD boxes (each point as (x, y)) and size-and-direction
  boxes (angle anticlockwise from i, in the Angle setting).
- **Statistics:** type `b(20, 0.3)` or `n(5.7, 1.2^2)` (`?` for an unknown
  mu or sigma; `x~` in front is fine), a data list with commas, or two
  lists on two rows (both readings offered: values and frequencies, or x
  and y). A test first asks the tail (a menu), then its boxes. Nothing
  typed: From sums, PMCC test, Two events, mu and sigma from two,
  Stratified sample, Outlier fences.
- **Kinematics:** type `v = ...`, `s = ...` (or `x =`, `r =`) or `a = ...`
  in t, numbers or vectors in i and j (mockup G); or two rows of times and
  velocities read off a v-t graph. Nothing typed: SUVAT boxes (mockup F:
  any three, `?` for what you want) and Projectile boxes (u, angle, height
  above the landing level, g (9.8 when empty), time, range; `?` for u
  finds it from the time or range).
- **Forces:** box forms only (EXE with nothing typed): Slope or surface,
  Pulley, Towing, Moments, Forces. Every box takes a number, `?` for what
  is wanted, or a letter for an unknown; at most two unknowns. Moments and
  Forces take lists: `F@x, F@x` (x from one end) and `F@angle, ai + bj`
  (angles anticlockwise from i). Masses can be typed as `4g`; the g box is
  9.8 when empty, or type g to keep it as a letter. Angles are degrees.
- **Calculus:** typed like Algebra: `y = f(x)` or an expression, `F(x, y) = 0`,
  two rows `x = f(t)` and `y = g(t)`, two curves, or `dy/dx = ...` (dy over
  dx with the fraction key, or typed in a line).

## Screens

- Tiles carry their number in small grey type, top left, so the number keys
  are discoverable. The grey "detected" line ends with `TOOLS more`.
- More lists every action that fits, in the same order as the tiles, then
  `All tools`: the old section menus for this topic, then the old home grid
  (Calculate, CAS, Graph, Solve, Maths, Further, Notes, Settings).
- Home topics not built yet open their old section menus (Trig opens the old
  Trigonometry tools, Statistics a grid of the five old stats sections, and
  so on), so nothing that worked before is lost. Further topics map to the
  old Further sections the same way.
- Settings page: Angle, Answers, Decimals (3-6 s.f. or 1-4 d.p.), Complex
  (a + bi or r, theta), Sleep after, Key repeat, and Further Maths shown as
  "on/off in launch script" (it can't change there: the topic list is fixed
  at start). Mockup H's "Working" row is left out, as the spec says.

## Launch script

`maths.py` and `module.py` (identical) hold the defaults and call
`casui.main(further=FURTHER, angle=ANGLE, answers=ANSWERS, decimals=DECIMALS,
complex=COMPLEX, sleep=SLEEP, repeat=REPEAT)`. A value main() doesn't know
keeps its default, so a typo can't stop the program. `SLEEP = 0` means 10
hours. devlint checks that the two launchers match, that `FURTHER` is True
or False, and that every setting the launcher assigns is passed to main()
by its own name (pass2-aqa's check, widened for the extra settings).

## Answers

- An engine's lines are working (black), notes (grey), warnings (red), then
  the boxed answer, then follow-ups after the box (vertex, line of symmetry).
- Exact + decimal shows `x = 2 + log_2 3 = 3.58 (3 s.f.)` in the box when the
  exact form has a surd, log, pi, e or fraction in it; an integer shows once.
  A decimal that is exact in fewer digits than the setting (0.5) shows without
  "(3 s.f.)".
- When the question was typed with decimals, the box shows the decimal only:
  an "exact" form built from 0.1216047 is not exact.
- Letters: the calculator's ALPHA keys type lower case, so every letter is
  lower case (N = A e^(kt) reads as n = a e^(kt)).

## Topics on home

Calculate, Algebra, Coord geometry, Exp and logs, Calculus, Trig,
Sequences and series, Numerical, Vectors, Statistics, Kinematics and
Forces are the new screens.
Kinematics, Forces and the Further topics still open their old section menus.
Graph and Notes are the old screens.

## Recognition

- One pass of caslex per row, then tree walks only. Degree in x is
  structural; brackets that multiply out are checked with caspoly when there
  are no other letters (so (x + 1)^2 - x^2 is linear).
- `y = ...` and `f(x) = ...` name the right-hand side: it is a function, not an
  equation. A row with both x and y and an `=` is an equation in x and y.
- Rearrange for a letter is offered only when the row has `=` (mockup I shows
  "Rearrange for k" for an expression; with no `=` there is nothing to
  rearrange), and only for a letter that appears once or linearly, so it
  can always be done.
- Inverse is offered only where y = f(x) rearranges (x once, linear in x,
  or (ax + b)/(cx + d)); a quadratic gets it too, to show why it is
  many-to-one.

## Engines

- Solve picks its method from the form: factors or the formula (quadratic),
  the factor theorem then the quadratic (cubic and up), u-substitution
  (hidden quadratics in x^2, sqrt x, 1/x, a^x, e^x, including u + 1/u), logs
  (one base: rearranged and log_a kept exact; two bases: ln both sides), log
  laws then the algebra with invalid roots rejected (log equations), cases
  (modulus), multiplying up with excluded roots (fractions). Anything else
  goes to the old CAS solver, and the page says "solved by the CAS".
- Exact logs are kept exact through simplification (caseng.simplify would
  turn log_2 3 into a decimal) and tidied: log_2 12 = 2 + log_2 3,
  log_4 8 = 3/2, log_a(a^2 sqrt a) = 5/2.
- Partial fractions keep the factors as typed (2 - 3x stays 2 - 3x); a
  denominator typed unfactorised is factorised with one factor turned round
  if that avoids a minus sign outside (16 - 9x^2 -> (3x + 4)(4 - 3x)).
- Range works on the domain pieces: stationary points (exact where the CAS
  solves f' = 0, conjugate surd pairs evaluated exactly), end values and end
  limits (numerical, snapped to exact numbers). Inverse gives the domain of
  f^-1 as the range of f.
- Graph with letters asks for their values first.

## Memory (MicroPython 1.9.4 unix port, .mpy with -mcache-lookup-bc)

Each module's own size once loaded, in the order a session loads them:

| part | KB |
|---|---|
| casui (keys, drawing, grids, settings; old screens moved to casold) | 37 |
| home | 4 |
| nat (editor) + topic | 17 + 12 |
| caslex + recog | 4 + 21 |
| acts | 10 |
| tex + texg + casrender (answer page) | 17 + 13 + 11 |
| caseng + caspoly (first action) | 44 + 17 |
| eng (+ the action's engine: e_alg 25, e_solve 17, e_fn 21, e_exp 7) | 22 |
| Coord: coord + rgeo + acts_geo + e_geo | 6 + 3 + 4 + 21 |
| Calculus: acts_calc + e_calc | 3 + 22 |
| Sequences: rseq + acts_seq, then e_seq or e_seqbox (+ e_solve, e_fn for unknowns) | 2 + 2, then 15 or 10 |
| Numerical: rnum + acts_num, then e_num | 2 + 1, then 9 |
| Vectors: rvec + acts_vec, then e_vec | 4 + 2, then 11 |
| Statistics: rstat + acts_stat, then e_stat or e_data (+ fmt; no CAS) | 3 + 4, then 13 or 14 |
| Kinematics: rkin + acts_kin, then e_suvat (boxes, v-t graph) or e_kin (+ e_calc, cascalc, e_solve) | 3 + 2, then 11 or 9 (+ 46 + 17) |
| Forces: acts_force, then e_force (+ e_solve) | 1, then 13 (+ 17) |
| Trig: acts_trig, then e_trig (expressions, identities) + e_tsolve (equations) or e_tri (boxes) | 5, then 14 + 15 or 12 |
| casalg (fractions, logs in coefficients) | 32 |
| cassolve + cascalc (letters in factorising, inequalities, domain, range, CAS fallback) | 21 + 23 |
| casold (Calculate, CAS, old tools; only via All tools / Calculate) | 25 |

- Home alone: about 40 KB. A topic with the tiles showing: about 125 KB.
- Every engine of Algebra and Exp and logs loaded: about 375 KB (all four
  topics: about 430 KB), so the whole set needs a
  heap of about 420 KB to keep 40 KB for working. A 500 KB heap runs the
  50-case self test with 85 KB to spare at its lowest.
- On a 400 KB heap the first Algebra actions fit (complete square,
  factorise, roots) and the fourth runs out. For comparison the old flow, one
  Maths tool from section B (casui + mpure + engine + tex), needs about
  450 KB, and it has been in use on the calculator, so the real heap is
  probably bigger than 400 KB. `selftest.py` prints the free memory at
  start: that photo settles it.
- If the heap turns out to be about 400 KB: next savings are Algebra's
  inequality, discriminant and domain without cassolve (44 KB with
  cascalc), and trimming recog/acts.
- After merging pass2-aqa (9 Oct): code is about 8 KB bigger (font tables
  built at import, errtext and the Further lists in casui, casalg's
  complete-the-square and power expansion), but the render caches are now
  dropped after drawing. A 20-action Algebra + Exp session keeps about
  110 KB free on a 500 KB heap (before: out of memory from the 8th action)
  and runs 19 of 20 actions on a 400 KB heap (before: 2). Self test: 50/50
  at 500 KB, lowest 69 KB free (before 80); 48/50 at 450 KB (before 49);
  26/50 at 400 KB (before 34). Its log rows are allocated up front, so on a
  full heap it still finishes and shows its summary (the merged build first
  stopped at 400 KB with a MemoryError while writing a row).

- Stage 2 (22 Oct): Trig, Sequences, Numerical and Vectors with their tiles
  showing take 125-127 KB (the screens were 125 KB; topic and recog grew
  3 KB). Their engines are 10-15 KB modules each; a Trig equation also
  loads casalg and e_solve as Algebra does. They don't reuse the old
  section modules as engines: mpure loads 226 KB and mcalc 94 KB.
- Self test, now two runs with a restart between (every topic in one run
  needs more than a 500 KB heap: modules stay loaded): `selftest.py`, the
  50 stage 1 parts: 50/50 at 500 KB, lowest 66 KB free (was 69); 25/50 at
  400 KB (was 26). `selftest2.py`, 12 stage 2 parts (three per topic):
  12/12 at 500 KB, lowest 79 KB free; 6/12 at 400 KB (Trig and Sequences
  fit, Numerical and Vectors run out). Measured on the MicroPython 1.9.4
  unix port from .mpy.

- Stage 3 (22 Oct): Statistics, Kinematics and Forces with tiles showing
  take 124-130 KB; the screens themselves grew 5 KB over stage 2 (the box
  and menu-then-boxes prompts in topic, recog.read). A Statistics session
  is about 210 KB (no CAS); Kinematics on a function of t loads the
  Calculus engine (about 350 KB with an answer page); Forces about 290 KB.
- Self test, three runs with a restart between (each run's cases in its
  own module, so a run doesn't hold the others'): `selftest.py` 50/50 at
  500 KB, lowest 70 KB free; 27/50 at 400 KB. `selftest2.py` 12/12 at
  500 KB, lowest 79 KB; 6/12 at 400 KB. `selftest3.py` (Statistics,
  Kinematics, Forces, three each) 9/9 at 500 KB, lowest 95 KB; 6/9 at
  400 KB (Forces runs out after Kinematics' CAS). MicroPython 1.9.4 unix
  port, from .mpy.

## Speed (estimated: laptop us x 0.29 + 4 ms per draw_string)

| screen | device |
|---|---|
| home grid, first draw / move | 1.2 s / 0.1 s |
| typing a key in a topic | 0.1 s |
| EXE, first time (loads recog, acts) | 1.7 s |
| EXE again (parse + recognise + tiles) | 0.5-0.7 s |
| moving between tiles | 0.14 s |
| first answer page (loads the CAS, engine, typesetter) | 4.5-6.5 s |
| later answer pages | about 1.5 s |
| More grid | 0.5 s |
| Settings page / move | 1.1 s / 0.1 s |
| Coord: first answer (perpendicular bisector, loads the CAS) | 4.9 s |
| Calculus: stationary points, first / again | 7.6 s / 2.5 s |
| self test, all 50 cases | about 4 min |
| self test part 2, 12 cases (estimated) | about 1 min |

## Trig choices

- Two Solve actions, degrees and radians, the Angle setting's one first: the
  unit of an equation can't be read from it. The interval may be left empty
  (0 to 360, 0 to 2pi); its ends count as in, and a root on an end gets a
  note to drop it if the interval is strict.
- Equations are turned into a polynomial in one ratio of one angle A
  (sec, cosec, cot as 1/cos ...; sin 2A and cos 2A by the double angle
  formulas, cos 2A in whichever of sin or cos is there; sin^2 = 1 - cos^2;
  a sin A + b cos A = 0 as tan; a sin^2 + b sin cos + c cos^2 = k over
  cos^2; a sin A + b cos A = k by R sin(A + a)), solved with the Algebra
  quadratic/cubic working, then every angle from the principal value.
  Anything else is solved numerically (sign changes and touching roots on
  720 steps), and the page says so. Roots where the equation is undefined
  (sin x = 0 under sin 2x / sin x) are rejected with a line saying why.
- Exact angles when they are standard (pi/4, 150), decimals otherwise.
- Identity? checks numerically at nine values (plus exact simplification when
  the CAS gets 0) and gives a counterexample when it fails; the proof is
  still the student's. Simplify spots a constant (the 15 in 2 jun25 8b).
- Small angle approximations replace sin A, tan A, cos A and keep terms to
  x^2 (or to the first non-zero one, up to x^4), from the CAS's Maclaurin
  coefficients, which agree with sin x ~ x, cos x ~ 1 - x^2/2 to that order.
- Triangle boxes: angle A opposite side a; three values with a side, or
  two sides and the area (both angles C when they work); SSA gives both
  triangles when both work. Angles in the Angle setting's unit, the other
  unit in grey. Arc and sector: any two of r, angle, arc, area, perimeter.
- The old Trigonometry tools are not used as engines: mpure loads 226 KB.

## Sequences choices

- A sum of terms that form an AP or GP uses the formula, so letters are fine
  (sum of br + c, r = 10 to 100, is 5005b + 91c); other sums add the terms
  (in pairs: a long chain of + would pass the calculator's call depth).
  An empty "to" box is a sum to infinity (GP only).
- Terms say what the sequence does: arithmetic (a, d), geometric (a, r),
  periodic (period p), increasing/decreasing, settling to a value.
- AP and GP boxes: each formula with one unknown left is solved by the
  Algebra solver (its working), so n can come from S(n) or u(n); when n
  isn't whole the page gives S(n) on both sides (n for S(n) > k).
  Decimals typed: the answers are decimal unless short and exact
  (374.88).
- Binomial: whole n expands in the order typed ((2x - 3)^10 from 1024x^10,
  as 3 nov21 4a); any other n takes the number term out first, with
  where it is valid.

## Numerical choices

- Working values to 7 s.f. (as the mark schemes quote them); the box shows
  them too, and FORMAT gives the Decimals setting.
- Sign change also checks f is continuous between the ends (400 samples):
  1/x on -1 to 1 changes sign but is not a root, and the page says so.
- Newton-Raphson and iteration say where they go when carried on
  (converges to, staircase or cobweb, or diverges); the trapezium rule says
  over or under from the sign of f'' on the interval.
- Trig here is in radians whatever the Angle setting.

## Vectors choices

- The angle between two vectors is worked by the cosine rule on |a|, |b|
  and |a - b| (7357 has no scalar product); it isn't offered with letters.
- Parallel: b = k a with the same k for every component, else not.
- The quadrilateral names itself from parallel pairs and equal sides and
  diagonals (square, rectangle, rhombus, parallelogram, trapezium,
  isosceles trapezium, kite).

## Statistics choices

- No CAS: the engines use floats and fmt.py (sf, dec), so a Statistics
  session with an answer page is about 210 KB (eng and caseng would add 85).
- A significance level of 1 or more is a percentage, below 1 a proportion
  (5 and 0.05 are both 5%).
- Binomial tests give the probability of the observed value or more extreme,
  the comparison, and the critical region with its actual significance; a
  two-tail test compares with half the level in the tail the value is in.
- PMCC critical values are worked out from the distribution of r under H0
  (Simpson's rule), so any n works; for n = 4 to 30 they match the booklet
  table to 4 d.p. (all 108 checked), and n = 50 at 2.5% gives 0.2787.
- sd divides by n (the booklet's sigma); s with n - 1 is in grey.
  Quartiles use the AQA position rule (as the old tools).

## Kinematics choices

- SUVAT uses the equation without the value nobody asked for, solved by the
  Algebra solver (so t from a quadratic shows its working); two roots: the
  first t >= 0, or the positive speed, with the other in grey.
- Integrating up asks for the value at t = 0 (empty is 0); letters are
  kept (a = 3kt^2 - 2kt + 1 gives v = kt^3 - kt^2 + t + 1).
- Distance splits where v = 0 inside the interval; a vector's speed and |a|
  use sin^2 + cos^2 = 1 and roots of products (|a| = 2e^t, 2 jun22 17).
- v-t graph: straight lines between the points; gradients, areas, running
  displacement and the times it is back at the start (2 jun18 12b).

## Forces choices

- Each form writes its equations (resolving along and across the slope,
  each particle of a pulley or a towed pair, up = down and moments about
  the end) and solves them for the unknowns: one equation with one unknown
  by the Algebra solver, two linear ones together. So mu, P, a mass or a
  reaction can be the one asked for (the old tools crashed on ?).
- Slope or surface: with a empty and nothing unknown it says whether the
  block moves (push along the slope against mu R) and with what a. The
  moving box (up, down; empty is up) sets the direction of friction, so a
  block sliding up after the string breaks decelerates (2 nov20 18bi).
- Pulley: m2 hangs and falls; m1 lies on a table (slope 0), a slope, or
  hangs (slope 90). Tilting about a support: type 0 for the other reaction.
- Masses and forces with g kept as a letter give answers in g
  ((11 - 5 sqrt 3)g/26, 2 jun24 21c).
- Algebra's simultaneous equations got x wrong when one equation had no y
  (2x = 6, x + y = 5 gave x = 11/3): x now comes from that equation.

## Coord geometry and Calculus choices

- A circle from its centre and radius is not an action: it is writing
  (x - a)^2 + (y - b)^2 = r^2 (the spec: no one-formula tools).
- Three points offer the circle through them and the triangle first, then
  the two-point actions for AB, BC and AC (in More).
- A definite integral is refused when the function is undefined inside
  the interval (F(b) - F(a) would be wrong); undefined exactly at an end is
  allowed when the integral has a limit there, and the page says so.
- Stationary points with letters take the letters as positive to decide
  max or min, and say so. Increasing joins up across a lone stationary
  point (x^4 + 5x^3 increases for x > -15/4).
- The calculus variable is x, else t, else n, else the only letter; with
  two or more letters and none of those, type it in x.
