# PC-only: regenerates README.md from the module registries.
import casui
import devlint
import tests

def table(secs):
    out = ['| Section | Tools |', '| --- | --- |']
    for code, title, mod in secs:
        tools = casui._tools(code, title, mod)
        out.append('| ' + code + ' ' + title + ' | ' + ', '.join(t[0] for t in tools) + ' |')
    return '\n'.join(out)

def papers(papers):
    out = []
    for name, code, secs in papers:
        out.append('### ' + name + ' (' + code + ')\n\n' + table(secs))
    return '\n\n'.join(out)

n = sum(len(t) for m in tests.MODULES for c, ti, t in __import__(m).SECTIONS)
device = ', '.join('`' + f + '`' for f in devlint.DEVICE_FILES)
txt = '''# Maths Toolkit for the Casio fx-CG100 (AQA 7357 + MEI H645)

A calculator app in stock MicroPython 1.9.4 using the built-in `casioplot`.
An expression calculator with complex numbers, a CAS (simplify, expand,
factorise, solve, differentiate, integrate, series, limits), a plotter, the
AQA formulae booklet, and %d tools mapped section by section to two
specifications:

- A-level Mathematics: **AQA 7357**
- A-level Further Mathematics: **OCR B (MEI) H645**, every paper: Core Pure
  (Y420), Mechanics Major/Minor (Y421/Y431), Statistics Major/Minor
  (Y422/Y432), Modelling with Algorithms (Y433), Numerical Methods (Y434),
  Extra Pure (Y435) and Further Pure with Technology (Y436).

## Install

Run `./deploy.sh <mountpoint>` with the calculator connected as a USB drive.
It precompiles every module to `.mpy` with MicroPython 1.9.4's `mpy-cross`
(`-mno-unicode`, the only build the fx-CG100 loads; path in `$MPYCROSS`,
default `~/dev/cg100/bin/mpy-cross-1.9.4`), deletes every other `.py`/`.mpy`
in the storage root, copies the launchers `maths.py` and `module.py` and the
modules in, and checks each file byte for byte. Device files:
%s.

Then on the calculator: Python app > `maths.py` (or `module.py`) > Run.

## Screens

Built for how the fx-CG100 actually performs (no clock, ~4 ms per text call,
Python ~300x slower than a laptop): no large fills, and only what a key
changed is redrawn.

Home is an icon grid: Calculate, CAS, Graph, Solve, Maths (AQA 7357),
Further (MEI H645), Formulae, Settings. Every menu below it is a grid of word
tiles that remembers where you were. The status bar shows the screen, a
yellow S / red A for SHIFT / ALPHA, Rad/Deg, and Busy while something slow runs.

| Anywhere | |
| --- | --- |
| arrows | move (held arrows and DEL repeat) |
| OK, EXE | choose |
| EXIT | back |
| HOME | straight to the home grid |
| SETTINGS | Rad / Deg |
| 1-9 | jump to a tile |

| Typing (natural display) | |
| --- | --- |
| fraction key, divide | fraction; takes the term before it as the top |
| ^, x^2, e^x, sqrt | power / root boxes; SHIFT sqrt nth root, SHIFT ^ log base |
| sin, cos, tan, SHIFT log, SHIFT ln, ( | bracket pair round the cursor, sized to fit; `)` at the end steps out |
| arrows | move between boxes; up/down between top and bottom of a fraction |
| MENU | symbols |
| SHIFT DEL | clear |
| tool fields | values separated by commas in the order shown; `?` = unknown |

| Calculate | |
| --- | --- |
| EXE | answer under the line; history stays |
| FORMAT | exact / decimal |
| TOOLS | CAS operations on the line (d/dx, integrate, factorise, solve, plot...) |
| UP | recall earlier lines; + - x / continue from Ans |

| Result screen | |
| --- | --- |
| FORMAT | cycle: answer only / with working / full precision |
| up / down | scroll |

The toolkit quits by itself after roughly 10-15 minutes without a key, so a
forgotten session can't keep the calculator awake.

| Plot | |
| --- | --- |
| arrows | pan |
| + / - | zoom |
| OK | trace (left/right move, up/down switch curve) |
| 0 | reset |

Answers are exact when the maths is exact (`1/2`, `2sqrt(3)`, `pi/4`,
`2-3i`) and 3 s.f. otherwise; FORMAT shows 10 s.f.

## Tools: Maths (AQA 7357)

%s

## Tools: Further Maths (OCR B MEI H645)

%s

## Development

Runs unmodified under desktop CPython; `casioplot.py` stubs the graphics.

```
python3 tests.py       # engine checks + every tool case
python3 stress.py      # every tool with odd inputs, must not crash
python3 devlint.py     # MicroPython 1.9.4 compliance for the device files
python3 casioshot.py   # renders screens to shots/*.png
python3 mkreadme.py    # regenerates this file
```

Design and contracts: `docs/superpowers/specs/`.
''' % (n, device, table(casui.MATHS), papers(casui.FURTHER))
open('README.md', 'w').write(txt)
print('README', len(txt), 'bytes,', n, 'tools')
