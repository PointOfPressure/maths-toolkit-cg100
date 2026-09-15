# Drives every tool of every section module with a bank of odd inputs.
# Anything other than a clean result or a ValueError caveat is a failure.
import sys
import tests
import casutil

BANK = ['0', '1', '-1', '2', '1e9', '1e-9', '0.5', '3', '7', '-2.5']

def _inputs(spec):
    out = []
    n = 0
    lst = False
    for name, kind, cnt, opt in casutil.fields_of(spec):
        if kind == 'n':
            n += 1
        elif kind == 'e':
            n += 1
        elif kind == 'l':
            lst = True
        elif kind == 'v':
            n += cnt
        elif kind == 'm':
            n += cnt[0] * cnt[1]
    for base in BANK:
        vals = []
        i = 0
        for name, kind, cnt, opt in casutil.fields_of(spec):
            if kind == 'e':
                vals.append('x^2-' + base)
            elif kind == 'l':
                vals.extend([base, '1', '2', '3'])
            elif kind == 'v':
                vals.extend([base] * cnt)
            elif kind == 'm':
                vals.extend([base] * (cnt[0] * cnt[1]))
            else:
                vals.append(base)
        out.append(','.join(vals))
    out.append('')
    out.append('1')
    out.append(','.join(['x'] * (n + 1)))
    out.append(','.join(['2+3i'] * (n + 1)))
    return out

def main(mods):
    bad = 0
    count = 0
    for mname in mods:
        mod = __import__(mname)
        for code, title, tools in mod.SECTIONS:
            for label, spec, fn in tools:
                for text in _inputs(spec):
                    count += 1
                    try:
                        vals = casutil.convert(spec, text)
                    except ValueError:
                        continue
                    lines = casutil.call_tool(fn, vals)
                    for ln in lines:
                        if isinstance(ln, tuple) and ln[0] == '!' and ln[1].startswith('error: '):
                            bad += 1
                            print(mname + ' ' + label + ' <' + text + '>: ' + ln[1])
                            break
    print(str(count) + ' runs, ' + str(bad) + ' crashes')
    return bad

if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:] or tests.MODULES) else 0)
