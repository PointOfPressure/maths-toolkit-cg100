import casui
import caslex
import caseng

BIG = 1000000

def _asknum(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    t = caslex.parse(s)
    if t is None:
        return None
    try:
        return caseng.evalf(t, 0.0)
    except:
        return None

def _askint(prompt):
    v = _asknum(prompt)
    if v is None:
        return None
    return int(round(v))

def _asklist(prompt):
    s = casui.input_expr(prompt)
    if s is None:
        return None
    out = []
    for p in s.replace(',', ' ').split():
        try:
            out.append(float(p))
        except:
            pass
    return out

def _askints(prompt):
    lst = _asklist(prompt)
    if lst is None:
        return None
    return [int(round(v)) for v in lst]

def _num(x):
    r = round(x, 4)
    if r == int(r):
        return str(int(r))
    return str(r)

def _row(lst):
    return ' '.join([_num(v) for v in lst])

def _show(title, lines):
    casui.result_screen(title, lines)

def _pages(title, lines):
    if not lines:
        _show(title, ['(nothing)'])
        return
    chunk = 6
    i = 0
    while i < len(lines):
        _show(title, lines[i:i + chunk])
        i += chunk

def _askmatrix(prompt):
    n = _askint('Size n (' + prompt + ')')
    if n is None or n < 1 or n > 8:
        return None
    m = []
    for i in range(n):
        row = _asklist('Row ' + str(i + 1) + ' (n nums)')
        if row is None or len(row) < n:
            return None
        m.append([row[j] for j in range(n)])
    return m

# ---- sorting ----

def bubble():
    a = _asklist('List (comma/space)')
    if not a:
        return
    lines = ['Start: ' + _row(a)]
    n = len(a)
    swaps = 0
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
        lines.append('Pass ' + str(i + 1) + ': ' + _row(a))
    lines.append('Swaps: ' + str(swaps))
    _pages('Bubble Sort', lines)

def insertion():
    a = _asklist('List (comma/space)')
    if not a:
        return
    lines = ['Start: ' + _row(a)]
    n = len(a)
    comps = 0
    for i in range(1, n):
        key = a[i]
        j = i - 1
        # each test of (j>=0 and a[j]>key) that inspects a[j] is one comparison
        while j >= 0:
            comps += 1
            if a[j] > key:
                a[j + 1] = a[j]
                j -= 1
            else:
                break
        a[j + 1] = key
        lines.append('Step ' + str(i) + ': ' + _row(a))
    lines.append('Comparisons: ' + str(comps))
    _pages('Insertion Sort', lines)

# ---- bin packing ----

def _firstfit(items, cap):
    bins = []
    for it in items:
        placed = False
        for b in bins:
            if b[0] + it <= cap + 1e-9:
                b[0] += it
                b[1].append(it)
                placed = True
                break
        if not placed:
            bins.append([it, [it]])
    return bins

def _packshow(title, items, cap):
    bins = _firstfit(items, cap)
    lines = ['Cap ' + _num(cap) + '  Items ' + str(len(items))]
    for i in range(len(bins)):
        lines.append('Bin ' + str(i + 1) + ': ' + _row(bins[i][1]) + ' =' + _num(bins[i][0]))
    lines.append('Bins used: ' + str(len(bins)))
    _pages(title, lines)

def firstfit():
    items = _asklist('Item sizes')
    if not items:
        return
    cap = _asknum('Bin capacity C')
    if cap is None or cap <= 0:
        return
    _packshow('First-Fit', items, cap)

def firstfitdec():
    items = _asklist('Item sizes')
    if not items:
        return
    cap = _asknum('Bin capacity C')
    if cap is None or cap <= 0:
        return
    items = sorted(items, reverse=True)
    _packshow('First-Fit Decr', items, cap)

# ---- Dijkstra ----

def dijkstra():
    m = _askmatrix('0=no edge')
    if m is None:
        return
    n = len(m)
    s = _askint('Start node (1..' + str(n) + ')')
    if s is None or s < 1 or s > n:
        return
    s -= 1
    dist = [BIG] * n
    done = [False] * n
    dist[s] = 0
    for _ in range(n):
        u = -1
        best = BIG
        for i in range(n):
            if not done[i] and dist[i] < best:
                best = dist[i]
                u = i
        if u == -1:
            break
        done[u] = True
        for v in range(n):
            w = m[u][v]
            if w > 0 and not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    lines = ['From node ' + str(s + 1) + ':']
    for i in range(n):
        d = 'unreachable' if dist[i] >= BIG else _num(dist[i])
        lines.append('Node ' + str(i + 1) + ': ' + d)
    _pages('Dijkstra', lines)

# ---- Prim MST ----

def prim():
    m = _askmatrix('0=no edge')
    if m is None:
        return
    n = len(m)
    intree = [False] * n
    intree[0] = True
    edges = []
    total = 0
    for _ in range(n - 1):
        bw = BIG
        bu = -1
        bv = -1
        for u in range(n):
            if intree[u]:
                for v in range(n):
                    w = m[u][v]
                    if not intree[v] and w > 0 and w < bw:
                        bw = w
                        bu = u
                        bv = v
        if bv == -1:
            break
        intree[bv] = True
        total += bw
        edges.append((bu, bv, bw))
    lines = ['Edges (start at node 1):']
    for e in edges:
        lines.append(str(e[0] + 1) + '-' + str(e[1] + 1) + '  w=' + _num(e[2]))
    lines.append('Total weight: ' + _num(total))
    if len(edges) < n - 1:
        lines.append('(graph not connected)')
    _pages('Prim MST', lines)

# ---- Kruskal MST ----

def _find(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i

def kruskal():
    m = _askmatrix('0=no edge')
    if m is None:
        return
    n = len(m)
    elist = []
    for i in range(n):
        for j in range(i + 1, n):
            if m[i][j] > 0:
                elist.append((m[i][j], i, j))
    elist = sorted(elist)
    parent = [i for i in range(n)]
    edges = []
    total = 0
    for w, u, v in elist:
        ru = _find(parent, u)
        rv = _find(parent, v)
        if ru != rv:
            parent[ru] = rv
            edges.append((u, v, w))
            total += w
    lines = ['Edges chosen:']
    for e in edges:
        lines.append(str(e[0] + 1) + '-' + str(e[1] + 1) + '  w=' + _num(e[2]))
    lines.append('Total weight: ' + _num(total))
    if len(edges) < n - 1:
        lines.append('(graph not connected)')
    _pages('Kruskal MST', lines)

# ---- Critical path ----

def critpath():
    n = _askint('How many activities')
    if n is None or n < 1 or n > 12:
        return
    dur = []
    preds = []
    for i in range(n):
        d = _asknum('Activity ' + str(i + 1) + ' duration')
        if d is None:
            return
        p = _askints('A' + str(i + 1) + ' preds (idx,0=none)')
        if p is None:
            p = []
        p = [x - 1 for x in p if 1 <= x <= n and x - 1 != i]
        dur.append(d)
        preds.append(p)
    es = [0.0] * n
    ef = [0.0] * n
    # forward pass: relax to a fixed point so any activity numbering works
    # (predecessors need not be lower-indexed); n passes suffice for n nodes
    for _ in range(n):
        for i in range(n):
            e = 0.0
            for q in preds[i]:
                if ef[q] > e:
                    e = ef[q]
            es[i] = e
            ef[i] = e + dur[i]
    proj = 0.0
    for i in range(n):
        if ef[i] > proj:
            proj = ef[i]
    succ = [[] for _ in range(n)]
    for i in range(n):
        for q in preds[i]:
            succ[q].append(i)
    lf = [proj] * n
    ls = [proj - dur[i] for i in range(n)]
    # backward pass: relax to a fixed point (successors need not be higher-indexed)
    for _ in range(n):
        for i in range(n - 1, -1, -1):
            if succ[i]:
                mn = BIG
                for s in succ[i]:
                    if ls[s] < mn:
                        mn = ls[s]
                lf[i] = mn
            else:
                lf[i] = proj
            ls[i] = lf[i] - dur[i]
    lines = ['Project duration: ' + _num(proj)]
    crit = []
    for i in range(n):
        fl = ls[i] - es[i]
        lines.append('A' + str(i + 1) + ' ES' + _num(es[i]) + ' EF' + _num(ef[i]) + ' F' + _num(fl))
        if abs(fl) < 1e-6:
            crit.append('A' + str(i + 1))
    lines.append('Critical: ' + (' '.join(crit) if crit else 'none'))
    _pages('Critical Path', lines)

TOOLS = [
    ('Bubble sort', bubble),
    ('Insertion sort', insertion),
    ('Bin: first-fit', firstfit),
    ('Bin: first-fit decr', firstfitdec),
    ('Dijkstra shortest', dijkstra),
    ('Prim MST', prim),
    ('Kruskal MST', kruskal),
    ('Critical path', critpath),
]

def run():
    labels = [t[0] for t in TOOLS]
    while True:
        c = casui.menu('Modelling w/ Algorithms', labels)
        if c == -1:
            return
        TOOLS[c][1]()
