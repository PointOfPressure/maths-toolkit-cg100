# Notes screens below the paper menu (casui.notes_section): a paper's topic
# grid from the small index notes_ix.py, then a page. Pages come typeset and
# line-broken from tn_*.py (mknotes.py builds them from notes_*.py); a
# module is imported only when one of its topics is opened.
from casui import remembered, show_lines, busy

def topics(name):
    # [(topic, module, index in its NOTES)] for one paper
    import notes_ix
    out = []
    for p, mods in notes_ix.T:
        if p == name:
            for m, ts in mods:
                for i in range(len(ts)):
                    out.append((ts[i], m, i))
    return out

def lines(page):
    # a page of mknotes.py display lines -> ('d', block) lines for
    # show_lines; a block is unpacked only when it is first drawn
    out = []
    for s in page.split('\n'):
        out.append(('d', [s[0], None, (), ord(s[1]) - 32, None, s]))
    return out

def unpack(blk):
    # fill in a block's strings and pixel ops from its display line:
    # \x01 x y size length text, or \x02 and an op (see mknotes.encode);
    # numbers are two characters, base 90 from 32
    s = blk[5]
    strs = []
    ops = []
    n = len(s)
    i = 2
    while i < n:
        c = s[i]
        x = (ord(s[i + 2]) - 32) * 90 + ord(s[i + 3]) - 32
        if c == '\x01':
            x = (ord(s[i + 1]) - 32) * 90 + ord(s[i + 2]) - 32
            k = i + 6 + ord(s[i + 5]) - 32
            strs.append((x, ord(s[i + 3]) - 32, s[i + 6:k], 'medium' if s[i + 4] == 'm' else 'small'))
            i = k
            continue
        k = s[i + 1]
        if k == '3':
            ops.append((3, s[i + 2], 'medium' if s[i + 3] == 'm' else 'small',
                        (ord(s[i + 4]) - 32) * 90 + ord(s[i + 5]) - 32, (ord(s[i + 6]) - 32) * 90 + ord(s[i + 7]) - 32))
            i += 8
            continue
        if k == '4':
            m = ord(s[i + 2]) - 32
            i += 3
            p = []
            while m > 0:
                p.append((ord(s[i]) - 32) * 90 + ord(s[i + 1]) - 32)
                i += 2
                m -= 1
            ops.append((4, p))
            continue
        y = (ord(s[i + 4]) - 32) * 90 + ord(s[i + 5]) - 32
        z = (ord(s[i + 6]) - 32) * 90 + ord(s[i + 7]) - 32
        if k == '2':
            ops.append((2, x, y, z, (ord(s[i + 8]) - 32) * 90 + ord(s[i + 9]) - 32))
            i += 10
        else:
            ops.append((ord(k) - 48, x, y, z))
            i += 8
    blk[1] = strs
    blk[4] = ops

def show(title, page):
    show_lines(title, lines(page))

def paper(name):
    tops = topics(name)
    labels = [t[0] for t in tops]
    while True:
        sel = remembered(name, labels)
        if sel < 0:
            return
        title, mod, i = tops[sel]
        busy()
        show(title, __import__('tn' + mod[5:]).N[i])
