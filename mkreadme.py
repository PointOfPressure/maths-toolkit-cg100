# PC-only: regenerates README.md from the module registries.
import casui
import devlint
import tests

def table(mods):
    out = ['| Section | Tools |', '| --- | --- |']
    for m in mods:
        for code, title, tools in __import__(m).SECTIONS:
            out.append('| ' + code + ' ' + title + ' | ' + ', '.join(t[0] for t in tools) + ' |')
    return '\n'.join(out)

def papers(groups):
    out = []
    for title, mods in groups:
        out.append('### ' + ' '.join(title.split()) + '\n\n' + table(mods))
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
It deletes every other `.py` in the storage root and copies these in:
%s.

Then on the calculator: Python app > File > Open > `maths.py` > Run.

## Screens

Home: Calculate, CAS f(x), Maths AQA 7357, Further MEI H645, Formulae AQA, Angle.
Further opens a paper menu first, then sections, then tools.

| Menus | |
| --- | --- |
| up / down | move, wraps |
| 1-9 | jump to entry |
| page up / down | move a screen |
| OK, EXE | choose |
| EXIT | back |

| Input line | |
| --- | --- |
| type values separated by commas in the order the field list shows | `1,-3,2` |
| `?` | unknown, where a tool solves for it (e.g. SUVAT `0,?,9.8,?,3`) |
| `data*` fields | as many values as you like, last field |
| `A[3x3]` fields | nine numbers row by row; the screen shows the grid as you type |
| `f(x)` fields | an expression; `x`, `t`, `y`, `pi`, `e`, `i`, `sqrt(`, `ln(`, `e^(` all work |
| SHIFT | `=`, `ln(`, `log(`, `pi`, `i`, inverse trig, `logb(`, `ans` |
| ALPHA | letters |
| MENU | symbol list |
| UP | recall the last entry for this tool |
| DEL / DOWN / EXIT | delete / clear / cancel |

| Result screen | |
| --- | --- |
| FORMAT | cycle: answer only / with working / full precision |
| up / down | scroll |
| EXIT, OK | back to the input line for the same tool |

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
