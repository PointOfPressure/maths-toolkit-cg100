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
hours.

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
