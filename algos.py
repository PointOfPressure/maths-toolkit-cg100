import casui
import casutil

BIG = 1000000
EPS = 1e-9

_asknum = casutil.asknum
_askint = casutil.askint
_asklist = casutil.asklist
_askints = casutil.askints
_num = casutil.fmt
_show = casutil.show
_pages = casutil.show      # result_screen pages by itself now

def _row(lst):
    return ' '.join([_num(v) for v in lst])

def _padl(s, w):
    # right-align in a fixed field so a tableau lines up as columns
    while len(s) < w:
        s = ' ' + s
    return s

def _askmatrix(prompt):
    n = _askint('Size n (' + prompt + ')', 1, 8)
    if n is None:
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
    comps = 0
    for i in range(n - 1):
        for j in range(n - 1 - i):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
        lines.append('Pass ' + str(i + 1) + ': ' + _row(a))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Swaps: ' + str(swaps))
    lines.append('Passes: ' + str(n - 1 if n > 1 else 0))
    lines.append('Order: O(n^2); worst n(n-1)/2 = ' + str(n * (n - 1) // 2))
    _pages('Bubble Sort', lines)

def insertion():
    a = _asklist('List (comma/space)')
    if not a:
        return
    lines = ['Start: ' + _row(a)]
    n = len(a)
    comps = 0
    shifts = 0
    for i in range(1, n):
        key = a[i]
        j = i - 1
        # each test of (j>=0 and a[j]>key) that inspects a[j] is one comparison
        while j >= 0:
            comps += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        lines.append('Step ' + str(i) + ': ' + _row(a))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Shifts: ' + str(shifts))
    lines.append('Order: O(n^2); worst n(n-1)/2 = ' + str(n * (n - 1) // 2))
    _pages('Insertion Sort', lines)

# ---- quick sort ----
# The specification names quick sort explicitly. Written the way the mark
# scheme wants it read: at each pass EVERY unsorted sub-list is split about
# its own first element, and the pivots fixed so far are shown in [ ].
# The handheld's call stack is about 38 frames deep, so this must not recurse
# on the list length: the pending sub-lists live in an explicit stack instead.

def _qshow(a, fixed):
    parts = []
    for i in range(len(a)):
        if fixed[i]:
            parts.append('[' + _num(a[i]) + ']')
        else:
            parts.append(_num(a[i]))
    return ' '.join(parts)

def quicksort():
    a = _asklist('List (comma/space)')
    if not a:
        return
    n = len(a)
    fixed = [False] * n
    lines = ['Start: ' + _row(a)]
    lines.append('Pivot = first item of each sub-list; [ ] = pivot in place')
    stack = [(0, n - 1)]          # explicit stack of sub-lists still to split
    comps = 0
    p = 0
    while stack:
        p += 1
        nxt = []
        for seg in stack:
            lo = seg[0]
            hi = seg[1]
            if lo >= hi:
                if lo == hi:
                    fixed[lo] = True
                continue
            piv = a[lo]
            left = []
            right = []
            for k in range(lo + 1, hi + 1):
                comps += 1
                if a[k] <= piv:
                    left.append(a[k])
                else:
                    right.append(a[k])
            k = lo
            for v in left:
                a[k] = v
                k += 1
            ppos = k
            a[k] = piv
            fixed[k] = True
            k += 1
            for v in right:
                a[k] = v
                k += 1
            if ppos - 1 > lo:
                nxt.append((lo, ppos - 1))
            elif ppos - 1 == lo:
                fixed[lo] = True
            if hi > ppos + 1:
                nxt.append((ppos + 1, hi))
            elif hi == ppos + 1:
                fixed[hi] = True
        lines.append('Pass ' + str(p) + ': ' + _qshow(a, fixed))
        stack = nxt
        if p > 2 * n + 4:
            break
    lines.append('Sorted: ' + _row(a))
    lines.append('Passes: ' + str(p))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Order: O(n log n) average, O(n^2) worst')
    _pages('Quick Sort', lines)

# ---- bin packing ----

def _firstfit(items, cap):
    # comps counts every "does this item fit in this bin?" test, which is what
    # the specification asks to be counted for first fit / first fit decreasing
    bins = []
    comps = 0
    for it in items:
        placed = False
        for b in bins:
            comps += 1
            if b[0] + it <= cap + 1e-9:
                b[0] += it
                b[1].append(it)
                placed = True
                break
        if not placed:
            bins.append([it, [it]])
    return bins, comps

def _packshow(title, items, cap):
    bins, comps = _firstfit(items, cap)
    lines = ['Cap ' + _num(cap) + '  Items ' + str(len(items))]
    tot = 0.0
    for i in range(len(bins)):
        lines.append('Bin ' + str(i + 1) + ': ' + _row(bins[i][1]) + ' =' + _num(bins[i][0]))
        tot += bins[i][0]
    lines.append('Bins used: ' + str(len(bins)))
    lines.append('Comparisons: ' + str(comps))
    low = int(tot / cap)
    if low * cap < tot - 1e-9:
        low += 1
    lines.append('Lower bound: ' + str(low) + ' bins (total ' + _num(tot) + ')')
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
    s = _askint('Start node (1..' + str(n) + ')', 1, n)
    if s is None:
        return
    # optional: the mark scheme asks for the route as well as the distance.
    # A cancelled or 0 answer just leaves the route out.
    e = _askint('End node for route (0=none)', 0, n)
    s -= 1
    dist = [BIG] * n
    done = [False] * n
    prev = [-1] * n
    work = []
    for i in range(n):
        work.append([])
    order = []
    dist[s] = 0
    work[s].append(0)
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
        order.append(u)
        for v in range(n):
            w = m[u][v]
            if w > 0 and not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                work[v].append(dist[v])
    lines = ['From node ' + str(s + 1) + ':']
    lines.append('Order of permanent labels:')
    for k in range(len(order)):
        u = order[k]
        lines.append('  ' + str(k + 1) + ': node ' + str(u + 1) +
                     ' perm ' + _num(dist[u]))
    lines.append('Working values (in order tried):')
    for i in range(n):
        if work[i]:
            lines.append('  node ' + str(i + 1) + ': ' + ', '.join([_num(v) for v in work[i]]))
        else:
            lines.append('  node ' + str(i + 1) + ': none')
    lines.append('Final distances:')
    for i in range(n):
        d = 'unreachable' if dist[i] >= BIG else _num(dist[i])
        lines.append('Node ' + str(i + 1) + ': ' + d)
    if e is not None and e >= 1:
        t = e - 1
        if dist[t] >= BIG:
            lines.append('Route ' + str(s + 1) + ' to ' + str(e) + ': none')
        else:
            path = [t]
            u = t
            guard = 0
            while u != s and prev[u] >= 0 and guard <= n:
                u = prev[u]
                path.append(u)
                guard += 1
            path.reverse()
            lines.append('Route ' + str(s + 1) + ' to ' + str(e) + ': ' +
                         ' - '.join([str(v + 1) for v in path]))
            lines.append('Route length: ' + _num(dist[t]))
    lines.append('Order: O(n^2) on an n-node adjacency matrix')
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
    lines.append('Order: O(n^2) on an n-node adjacency matrix')
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
    lines.append('Order: O(m log m) for m arcs (the sort dominates)')
    _pages('Kruskal MST', lines)

# ---- graph vocabulary: degrees, incidence matrix, directedness ----

def graphinfo():
    m = _askmatrix('0=no arc')
    if m is None:
        return
    n = len(m)
    sym = True
    for i in range(n):
        for j in range(n):
            if m[i][j] != m[j][i]:
                sym = False
    arcs = []
    if sym:
        for i in range(n):
            for j in range(i, n):
                if m[i][j] > 0:
                    arcs.append((i, j))
    else:
        for i in range(n):
            for j in range(n):
                if m[i][j] > 0:
                    arcs.append((i, j))
    lines = ['Order (nodes): ' + str(n)]
    lines.append('Size (' + ('edges' if sym else 'arcs') + '): ' + str(len(arcs)))
    lines.append('Type: ' + ('undirected' if sym else 'directed'))
    if sym:
        deg = [0] * n
        for a in arcs:
            if a[0] == a[1]:
                deg[a[0]] += 2      # a loop contributes 2 to its degree
            else:
                deg[a[0]] += 1
                deg[a[1]] += 1
        tot = 0
        for i in range(n):
            lines.append('deg(' + str(i + 1) + ') = ' + str(deg[i]))
            tot += deg[i]
        lines.append('Sum of degrees = ' + str(tot) + ' = 2 x ' + str(len(arcs)))
        odd = 0
        for i in range(n):
            if deg[i] % 2 == 1:
                odd += 1
        lines.append('Odd nodes: ' + str(odd))
    else:
        for i in range(n):
            outd = 0
            ind = 0
            for j in range(n):
                if m[i][j] > 0:
                    outd += 1
                if m[j][i] > 0:
                    ind += 1
            lines.append('node ' + str(i + 1) + ': out ' + str(outd) + '  in ' + str(ind))
    # connectivity of the underlying undirected graph
    seen = [False] * n
    seen[0] = True
    q = [0]
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for v in range(n):
            if not seen[v] and (m[u][v] > 0 or m[v][u] > 0):
                seen[v] = True
                q.append(v)
    conn = True
    for i in range(n):
        if not seen[i]:
            conn = False
    lines.append('Connected: ' + ('yes' if conn else 'no'))
    lines.append('Incidence matrix (rows nodes, cols arcs):')
    lab = []
    for a in arcs:
        lab.append(str(a[0] + 1) + ('-' if sym else '>') + str(a[1] + 1))
    lines.append('arcs: ' + ' '.join(lab))
    for i in range(n):
        cells = []
        for a in arcs:
            if sym:
                if a[0] == a[1] and a[0] == i:
                    cells.append('2')
                elif a[0] == i or a[1] == i:
                    cells.append('1')
                else:
                    cells.append('0')
            else:
                if a[0] == i and a[1] == i:
                    cells.append('0')
                elif a[0] == i:
                    cells.append('-1')
                elif a[1] == i:
                    cells.append('1')
                else:
                    cells.append('0')
        lines.append(str(i + 1) + ': ' + ' '.join(cells))
    _pages('Graph info', lines)

# ---- maximum flow / minimum cut ----
# Flow augmentation by breadth-first search on the residual network, so the
# path chosen is always a shortest one and the loop is provably finite.
# flow[u][v] is signed: sending f along u->v also sets flow[v][u] = -f, which
# is what makes "cancel some flow back" fall out of the same test.

def _res(cap, flow, u, v):
    return cap[u][v] - flow[u][v]

def _flow_reach(cap, flow, s):
    n = len(cap)
    seen = [False] * n
    seen[s] = True
    q = [s]
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for v in range(n):
            if not seen[v] and _res(cap, flow, u, v) > EPS:
                seen[v] = True
                q.append(v)
    return seen

def _aug_path(cap, flow, s, t):
    n = len(cap)
    pred = [-1] * n
    seen = [False] * n
    seen[s] = True
    q = [s]
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for v in range(n):
            if not seen[v] and _res(cap, flow, u, v) > EPS:
                seen[v] = True
                pred[v] = u
                if v == t:
                    return pred
                q.append(v)
    return None

def _zeros(n):
    z = []
    for i in range(n):
        z.append([0.0] * n)
    return z

def _runflow(cap, s, t, lines):
    n = len(cap)
    flow = _zeros(n)
    total = 0.0
    it = 0
    while it < 200:
        pred = _aug_path(cap, flow, s, t)
        if pred is None:
            break
        path = [t]
        u = t
        while u != s:
            u = pred[u]
            path.append(u)
        path.reverse()
        b = BIG
        for k in range(len(path) - 1):
            r = _res(cap, flow, path[k], path[k + 1])
            if r < b:
                b = r
        for k in range(len(path) - 1):
            a = path[k]
            c = path[k + 1]
            flow[a][c] += b
            flow[c][a] -= b
        total += b
        it += 1
        if lines is not None:
            lines.append('Path ' + str(it) + ': ' +
                         ' - '.join([str(v + 1) for v in path]) +
                         '  flow ' + _num(b))
    return flow, total

def maxflow():
    cap = _askmatrix('capacity, 0=no arc')
    if cap is None:
        return
    n = len(cap)
    s = _askint('Source node (1..' + str(n) + ')', 1, n)
    if s is None:
        return
    t = _askint('Sink node (1..' + str(n) + ')', 1, n)
    if t is None or t == s:
        return
    s -= 1
    t -= 1
    lines = ['Source ' + str(s + 1) + ', sink ' + str(t + 1)]
    lines.append('Augmenting paths:')
    flow, total = _runflow(cap, s, t, lines)
    lines.append('Maximum flow = ' + _num(total))
    lines.append('Flow on each arc:')
    for i in range(n):
        for j in range(n):
            if cap[i][j] > 0:
                sat = ' (saturated)' if flow[i][j] >= cap[i][j] - EPS else ''
                lines.append('  ' + str(i + 1) + '-' + str(j + 1) + ': ' +
                             _num(flow[i][j] if flow[i][j] > 0 else 0.0) +
                             ' / ' + _num(cap[i][j]) + sat)
    seen = _flow_reach(cap, flow, s)
    sset = []
    tset = []
    for i in range(n):
        if seen[i]:
            sset.append(str(i + 1))
        else:
            tset.append(str(i + 1))
    lines.append('Minimum cut:')
    lines.append('  S = {' + ', '.join(sset) + '}')
    lines.append('  T = {' + ', '.join(tset) + '}')
    ccap = 0.0
    carcs = []
    for i in range(n):
        for j in range(n):
            if seen[i] and not seen[j] and cap[i][j] > 0:
                carcs.append(str(i + 1) + '-' + str(j + 1) + ' (' + _num(cap[i][j]) + ')')
                ccap += cap[i][j]
    lines.append('  cut arcs: ' + (' '.join(carcs) if carcs else 'none'))
    lines.append('Cut capacity = ' + _num(ccap))
    lines.append('Max flow = min cut = ' + _num(total))
    _pages('Max flow / min cut', lines)

def cutcap():
    cap = _askmatrix('capacity, 0=no arc')
    if cap is None:
        return
    n = len(cap)
    s = _askint('Source node (1..' + str(n) + ')', 1, n)
    if s is None:
        return
    t = _askint('Sink node (1..' + str(n) + ')', 1, n)
    if t is None or t == s:
        return
    sel = _askints('Source-side nodes of the cut')
    if not sel:
        return
    s -= 1
    t -= 1
    inS = [False] * n
    for v in sel:
        if 1 <= v <= n:
            inS[v - 1] = True
    if not inS[s]:
        _show('Cut capacity', ['The source must be on the source side.'])
        return
    if inS[t]:
        _show('Cut capacity', ['The sink must be on the sink side.'])
        return
    sset = []
    tset = []
    for i in range(n):
        if inS[i]:
            sset.append(str(i + 1))
        else:
            tset.append(str(i + 1))
    lines = ['S = {' + ', '.join(sset) + '}']
    lines.append('T = {' + ', '.join(tset) + '}')
    ccap = 0.0
    back = 0.0
    lines.append('Arcs from S to T (these count):')
    any_f = False
    for i in range(n):
        for j in range(n):
            if cap[i][j] > 0 and inS[i] and not inS[j]:
                lines.append('  ' + str(i + 1) + '-' + str(j + 1) + ': ' + _num(cap[i][j]))
                ccap += cap[i][j]
                any_f = True
            elif cap[i][j] > 0 and inS[j] and not inS[i]:
                back += cap[i][j]
    if not any_f:
        lines.append('  none')
    lines.append('Cut capacity = ' + _num(ccap))
    lines.append('(arcs T to S total ' + _num(back) + ', not counted)')
    flow, total = _runflow(cap, s, t, None)
    lines.append('Maximum flow = ' + _num(total))
    if abs(total - ccap) < 1e-9:
        lines.append('This IS a minimum cut (capacity = max flow).')
    else:
        lines.append('Not minimum: capacity exceeds max flow by ' + _num(ccap - total))
    _pages('Cut capacity', lines)

# ---- Critical path ----

def critpath():
    n = _askint('How many activities', 1, 12)
    if n is None:
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
    casutil.run_tools('Modelling w/ Algorithms', TOOLS)
