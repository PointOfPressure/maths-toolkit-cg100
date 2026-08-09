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
_pages = casutil.show
_w = casutil.w
_warn = casutil.warn

def _row(lst):
    return ' '.join([_num(v) for v in lst])

def _padl(s, w):
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


def bubble():
    a = _asklist('List (comma/space)')
    if not a:
        return
    lines = [_w('Start: ' + _row(a))]
    n = len(a)
    swaps = 0
    comps = 0
    for i in range(n - 1):
        for j in range(n - 1 - i):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
        txt = 'Pass ' + str(i + 1) + ': ' + _row(a)
        lines.append(txt if i == n - 2 else _w(txt))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Swaps: ' + str(swaps))
    lines.append('Passes: ' + str(n - 1 if n > 1 else 0))
    lines.append('Order: O(n^2); worst n(n-1)/2 = ' + str(n * (n - 1) // 2))
    _pages('Bubble Sort', lines)

def insertion():
    a = _asklist('List (comma/space)')
    if not a:
        return
    lines = [_w('Start: ' + _row(a))]
    n = len(a)
    comps = 0
    shifts = 0
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        txt = 'Step ' + str(i) + ': ' + _row(a)
        lines.append(txt if i == n - 1 else _w(txt))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Shifts: ' + str(shifts))
    lines.append('Order: O(n^2); worst n(n-1)/2 = ' + str(n * (n - 1) // 2))
    _pages('Insertion Sort', lines)


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
    lines = [_w('Start: ' + _row(a))]
    lines.append(_w('Pivot = first item of each sub-list; [ ] = pivot in place'))
    stack = [(0, n - 1)]
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
        lines.append(_w('Pass ' + str(p) + ': ' + _qshow(a, fixed)))
        stack = nxt
        if p > 2 * n + 4:
            break
    lines.append('Sorted: ' + _row(a))
    lines.append('Passes: ' + str(p))
    lines.append('Comparisons: ' + str(comps))
    lines.append('Order: O(n log n) average, O(n^2) worst')
    _pages('Quick Sort', lines)


def _firstfit(items, cap):
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
    lines = [_w('Cap ' + _num(cap) + '  Items ' + str(len(items)))]
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


def dijkstra():
    m = _askmatrix('0=no edge')
    if m is None:
        return
    n = len(m)
    s = _askint('Start node (1..' + str(n) + ')', 1, n)
    if s is None:
        return
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
    lines = [_w('From node ' + str(s + 1) + ':')]
    lines.append(_w('Order of permanent labels:'))
    for k in range(len(order)):
        u = order[k]
        lines.append(_w('  ' + str(k + 1) + ': node ' + str(u + 1) +
                     ' perm ' + _num(dist[u])))
    lines.append(_w('Working values (in order tried):'))
    for i in range(n):
        if work[i]:
            lines.append(_w('  node ' + str(i + 1) + ': ' + ', '.join([_num(v) for v in work[i]])))
        else:
            lines.append(_w('  node ' + str(i + 1) + ': none'))
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
        lines.append(_warn('(graph not connected)'))
    lines.append('Order: O(n^2) on an n-node adjacency matrix')
    _pages('Prim MST', lines)


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
        lines.append(_warn('(graph not connected)'))
    lines.append('Order: O(m log m) for m arcs (the sort dominates)')
    _pages('Kruskal MST', lines)


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
                deg[a[0]] += 2
            else:
                deg[a[0]] += 1
                deg[a[1]] += 1
        tot = 0
        for i in range(n):
            lines.append('deg(' + str(i + 1) + ') = ' + str(deg[i]))
            tot += deg[i]
        lines.append(_w('Sum of degrees = ' + str(tot) + ' = 2 x ' + str(len(arcs))))
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
            lines.append(_w('Path ' + str(it) + ': ' +
                         ' - '.join([str(v + 1) for v in path]) +
                         '  flow ' + _num(b)))
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
    lines = [_w('Source ' + str(s + 1) + ', sink ' + str(t + 1))]
    lines.append(_w('Augmenting paths:'))
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
        _show('Cut capacity', [_warn('The source must be on the source side.')])
        return
    if inS[t]:
        _show('Cut capacity', [_warn('The sink must be on the sink side.')])
        return
    sset = []
    tset = []
    for i in range(n):
        if inS[i]:
            sset.append(str(i + 1))
        else:
            tset.append(str(i + 1))
    lines = [_w('S = {' + ', '.join(sset) + '}')]
    lines.append(_w('T = {' + ', '.join(tset) + '}'))
    ccap = 0.0
    back = 0.0
    lines.append(_w('Arcs from S to T (these count):'))
    any_f = False
    for i in range(n):
        for j in range(n):
            if cap[i][j] > 0 and inS[i] and not inS[j]:
                lines.append(_w('  ' + str(i + 1) + '-' + str(j + 1) + ': ' + _num(cap[i][j])))
                ccap += cap[i][j]
                any_f = True
            elif cap[i][j] > 0 and inS[j] and not inS[i]:
                back += cap[i][j]
    if not any_f:
        lines.append(_w('  none'))
    lines.append('Cut capacity = ' + _num(ccap))
    lines.append(_w('(arcs T to S total ' + _num(back) + ', not counted)'))
    flow, total = _runflow(cap, s, t, None)
    lines.append('Maximum flow = ' + _num(total))
    if abs(total - ccap) < 1e-9:
        lines.append('This IS a minimum cut (capacity = max flow).')
    else:
        lines.append('Not minimum: capacity exceeds max flow by ' + _num(ccap - total))
    _pages('Cut capacity', lines)


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


VN = ['x', 'y', 'z', 'w']

def _cterm(a, nm):
    if abs(a - 1.0) < 1e-12:
        return nm
    return _num(a) + nm

def _lin(coefs, nms):
    s = ''
    for j in range(len(coefs)):
        v = coefs[j]
        if abs(v) < 1e-12:
            continue
        if s == '':
            s = ('-' if v < 0 else '') + _cterm(abs(v), nms[j])
        else:
            s = s + (' - ' if v < 0 else ' + ') + _cterm(abs(v), nms[j])
    if s == '':
        s = '0'
    return s

def _blab(names, basis):
    out = []
    for i in range(len(basis)):
        out.append(names[basis[i]])
    return out

def _tabshow(lines, names, basis, tab, wid):
    hdr = _padl('', 4)
    for nm in names:
        hdr = hdr + _padl(nm, wid)
    lines.append(_w(hdr))
    lab = _blab(names, basis)
    for i in range(len(tab)):
        s = _padl(lab[i], 4)
        for v in tab[i]:
            s = s + _padl(_num(v, 3), wid)
        lines.append(_w(s))

def _pivot_on(tab, r, c):
    p = tab[r][c]
    for j in range(len(tab[r])):
        tab[r][j] = tab[r][j] / p
    tab[r][c] = 1.0
    for i in range(len(tab)):
        if i == r:
            continue
        f = tab[i][c]
        if f == 0.0:
            continue
        for j in range(len(tab[i])):
            tab[i][j] = tab[i][j] - f * tab[r][j]
        tab[i][c] = 0.0

def _simplex_run(tab, basis, allowed, names, wid, lines, tag):
    it = 0
    while it < 40:
        c = -1
        best = -EPS
        for j in range(1, len(tab[0]) - 1):
            if allowed[j] and tab[0][j] < best:
                best = tab[0][j]
                c = j
        if c < 0:
            return 'optimal'
        r = -1
        bestq = 0.0
        for i in range(1, len(tab)):
            if tab[i][c] > EPS:
                q = tab[i][-1] / tab[i][c]
                if r < 0 or q < bestq - 1e-12:
                    bestq = q
                    r = i
        if r < 0:
            return 'unbounded'
        it += 1
        if lines is not None:
            lines.append(_w(tag + 'Pivot ' + str(it) + ': column ' + names[c] +
                         ', row ' + names[basis[r]] + ', ratio ' + _num(bestq, 3)))
            lines.append(_w('  pivot element ' + _num(tab[r][c], 3) + '; ' +
                         names[c] + ' enters, ' + names[basis[r]] + ' leaves'))
        _pivot_on(tab, r, c)
        basis[r] = c
        if lines is not None:
            _tabshow(lines, names, basis, tab, wid)
    return 'optimal'

def _lpreport(lines, names, basis, tab, nv, nother, objname, sign):
    ncol = len(tab[0])
    val = [0.0] * ncol
    for i in range(1, len(tab)):
        val[basis[i]] = tab[i][-1]
    lines.append(_w('Optimal tableau reached.'))
    lines.append(objname + ' = ' + _num(sign * tab[0][-1]))
    for j in range(1, 1 + nv):
        lines.append(names[j] + ' = ' + _num(val[j]))
    for j in range(1 + nv, 1 + nv + nother):
        lines.append(names[j] + ' = ' + _num(val[j]))
    bas = []
    non = []
    for j in range(1, 1 + nv + nother):
        inb = False
        for i in range(1, len(tab)):
            if basis[i] == j:
                inb = True
        if inb:
            bas.append(names[j])
        else:
            non.append(names[j])
    lines.append(_w('Basic variables: ' + (', '.join(bas) if bas else 'none')))
    lines.append(_w('Non-basic (= 0): ' + (', '.join(non) if non else 'none')))

def simplex():
    n = _askint('How many variables (1..4)', 1, 4)
    if n is None:
        return
    m = _askint('How many <= constraints (1..4)', 1, 4)
    if m is None:
        return
    obj = _asklist('Objective coeffs (' + str(n) + ')')
    if obj is None or len(obj) < n:
        return
    obj = [obj[j] for j in range(n)]
    rows = []
    for i in range(m):
        r = _asklist('C' + str(i + 1) + ': ' + str(n) + ' coeffs then b')
        if r is None or len(r) < n + 1:
            return
        rows.append([r[j] for j in range(n + 1)])
    for i in range(m):
        if rows[i][n] < 0:
            _show('Simplex', [_warn('Standard form needs every b >= 0.'),
                              _warn('Constraint ' + str(i + 1) + ' has b < 0.'),
                              'Use the 2-stage tool instead.'])
            return
    vnames = [VN[j] for j in range(n)]
    snames = ['s' + str(i + 1) for i in range(m)]
    names = ['P'] + vnames + snames + ['RHS']
    ncol = 1 + n + m + 1
    tab = []
    o = [0.0] * ncol
    o[0] = 1.0
    for j in range(n):
        o[1 + j] = -obj[j]
    tab.append(o)
    for i in range(m):
        r = [0.0] * ncol
        for j in range(n):
            r[1 + j] = rows[i][j]
        r[1 + n + i] = 1.0
        r[ncol - 1] = rows[i][n]
        tab.append(r)
    basis = [0]
    for i in range(m):
        basis.append(1 + n + i)
    allowed = [True] * ncol
    lines = [_w('Standard form (L3):')]
    lines.append(_w('Maximise P = ' + _lin(obj, vnames)))
    for i in range(m):
        lines.append(_w('  ' + _lin(rows[i][0:n], vnames) + ' <= ' + _num(rows[i][n])))
    lines.append(_w('  ' + ', '.join(vnames) + ' >= 0'))
    lines.append(_w('Slack form (L4):'))
    for i in range(m):
        lines.append(_w('  ' + _lin(rows[i][0:n], vnames) + ' + ' + snames[i] +
                     ' = ' + _num(rows[i][n])))
    negobj = [-v for v in obj]
    orow = _lin(negobj, vnames)
    if orow[0] == '-':
        orow = '- ' + orow[1:]
    lines.append(_w('Objective row: P ' + orow + ' = 0'))
    lines.append(_w('Initial tableau:'))
    _tabshow(lines, names, basis, tab, 6)
    st = _simplex_run(tab, basis, allowed, names, 6, lines, '')
    if st == 'unbounded':
        lines.append(_warn('No leaving row: P is UNBOUNDED.'))
        _pages('Simplex', lines)
        return
    _lpreport(lines, names, basis, tab, n, m, 'P', 1.0)
    lines.append('Shadow prices (post-optimal, L9):')
    for i in range(m):
        lines.append('  C' + str(i + 1) + ' (' + snames[i] + '): ' +
                     _num(tab[0][1 + n + i]))
    _pages('Simplex', lines)

def simplex2():
    n = _askint('How many variables (1..4)', 1, 4)
    if n is None:
        return
    m = _askint('How many constraints (1..4)', 1, 4)
    if m is None:
        return
    mx = _askint('1 = maximise, 0 = minimise', 0, 1)
    if mx is None:
        return
    obj = _asklist('Objective coeffs (' + str(n) + ')')
    if obj is None or len(obj) < n:
        return
    obj = [obj[j] for j in range(n)]
    rows = []
    rels = []
    for i in range(m):
        r = _asklist('C' + str(i + 1) + ': ' + str(n) + ' coeffs, rel, b')
        if r is None or len(r) < n + 2:
            return
        rel = int(round(r[n]))
        if rel not in (-1, 0, 1):
            _show('2-stage simplex', [_warn('rel must be 1 (<=), 0 (=) or -1 (>=).')])
            return
        a = [r[j] for j in range(n)]
        b = r[n + 1]
        if b < 0:
            a = [-v for v in a]
            b = -b
            rel = -rel
        rows.append(a)
        rels.append(rel)
        rows[i].append(b)
    slack = []
    art = []
    nx = 0
    na = 0
    for i in range(m):
        if rels[i] == 1:
            slack.append(nx)
            nx += 1
            art.append(-1)
        elif rels[i] == -1:
            slack.append(nx)
            nx += 1
            art.append(na)
            na += 1
        else:
            slack.append(-1)
            art.append(na)
            na += 1
    vnames = [VN[j] for j in range(n)]
    xnames = []
    for i in range(m):
        if slack[i] >= 0:
            xnames.append(('s' if rels[i] == 1 else 'u') + str(i + 1))
    anames = []
    for i in range(m):
        if art[i] >= 0:
            anames.append('a' + str(i + 1))
    names = ['P'] + vnames + xnames + anames + ['RHS']
    ncol = 1 + n + nx + na + 1
    acol0 = 1 + n + nx
    tab = []
    tab.append([0.0] * ncol)
    for i in range(m):
        r = [0.0] * ncol
        for j in range(n):
            r[1 + j] = rows[i][j]
        if slack[i] >= 0:
            r[1 + n + slack[i]] = 1.0 if rels[i] == 1 else -1.0
        if art[i] >= 0:
            r[acol0 + art[i]] = 1.0
        r[ncol - 1] = rows[i][n]
        tab.append(r)
    basis = [0]
    for i in range(m):
        basis.append(acol0 + art[i] if art[i] >= 0 else 1 + n + slack[i])
    relstr = ['>=', '=', '<=']
    objname = 'P' if mx == 1 else 'C'
    lines = [_w(('Maximise ' if mx == 1 else 'Minimise ') + objname + ' = ' + _lin(obj, vnames))]
    for i in range(m):
        lines.append(_w('  ' + _lin(rows[i][0:n], vnames) + ' ' + relstr[rels[i] + 1] +
                     ' ' + _num(rows[i][n])))
    lines.append(_w('  ' + ', '.join(vnames) + ' >= 0'))
    allowed = [True] * ncol
    if na > 0:
        tab[0][0] = 1.0
        for j in range(na):
            tab[0][acol0 + j] = 1.0
        for i in range(1, m + 1):
            if art[i - 1] >= 0:
                for j in range(ncol):
                    tab[0][j] = tab[0][j] - tab[i][j]
        lines.append(_w('Phase 1: minimise ' + ' + '.join(anames)))
        _tabshow(lines, names, basis, tab, 6)
        _simplex_run(tab, basis, allowed, names, 6, lines, 'P1 ')
        if tab[0][ncol - 1] < -1e-7:
            lines.append(_warn('Phase 1 value ' + _num(-tab[0][ncol - 1]) + ' > 0:'))
            lines.append(_warn('the constraints are INFEASIBLE.'))
            _pages('2-stage simplex', lines)
            return
        for i in range(1, m + 1):
            if basis[i] >= acol0:
                for j in range(1, acol0):
                    if abs(tab[i][j]) > EPS:
                        _pivot_on(tab, i, j)
                        basis[i] = j
                        break
        for j in range(na):
            allowed[acol0 + j] = False
        lines.append(_w('Phase 1 done: all artificials are zero.'))
    sign = 1.0 if mx == 1 else -1.0
    o = [0.0] * ncol
    o[0] = 1.0
    for j in range(n):
        o[1 + j] = -sign * obj[j]
    tab[0] = o
    for i in range(1, m + 1):
        f = tab[0][basis[i]]
        if f != 0.0:
            for j in range(ncol):
                tab[0][j] = tab[0][j] - f * tab[i][j]
    lines.append(_w('Phase 2 tableau:'))
    _tabshow(lines, names, basis, tab, 6)
    st = _simplex_run(tab, basis, allowed, names, 6, lines, 'P2 ')
    if st == 'unbounded':
        lines.append(_warn('No leaving row: the objective is UNBOUNDED.'))
        _pages('2-stage simplex', lines)
        return
    _lpreport(lines, names, basis, tab, n, nx + na, objname, sign)
    _pages('2-stage simplex', lines)


def _feas(cons, x, y, tol):
    for cn in cons:
        if cn[0] * x + cn[1] * y > cn[2] + tol:
            return False
    return True

def _lpverts(cons):
    vs = []
    for i in range(len(cons)):
        for j in range(i + 1, len(cons)):
            a1 = cons[i][0]
            b1 = cons[i][1]
            c1 = cons[i][2]
            a2 = cons[j][0]
            b2 = cons[j][1]
            c2 = cons[j][2]
            det = a1 * b2 - a2 * b1
            if abs(det) < 1e-12:
                continue
            x = (c1 * b2 - c2 * b1) / det
            y = (a1 * c2 - a2 * c1) / det
            if not _feas(cons, x, y, 1e-7):
                continue
            dup = False
            for v in vs:
                if abs(v[0] - x) < 1e-7 and abs(v[1] - y) < 1e-7:
                    dup = True
            if not dup:
                vs.append((x, y))
    return vs

def _recession(cons):
    cands = [(1.0, 0.0), (0.0, 1.0)]
    for cn in cons:
        cands.append((cn[1], -cn[0]))
        cands.append((-cn[1], cn[0]))
    out = []
    for d in cands:
        if abs(d[0]) + abs(d[1]) < 1e-12:
            continue
        ok = True
        for cn in cons:
            if cn[0] * d[0] + cn[1] * d[1] > 1e-9:
                ok = False
        if ok:
            out.append(d)
    return out

def _lpline(fr, a, b, c, col):
    if abs(b) >= abs(a) and abs(b) > 1e-12:
        casutil.seg(fr, fr[4], (c - a * fr[4]) / b, fr[5], (c - a * fr[5]) / b, col)
    elif abs(a) > 1e-12:
        casutil.seg(fr, (c - b * fr[6]) / a, fr[6], (c - b * fr[7]) / a, fr[7], col)

def lpgraph():
    mx = _askint('1 = maximise, 0 = minimise', 0, 1)
    if mx is None:
        return
    obj = _asklist('Objective: p q  (for px + qy)')
    if obj is None or len(obj) < 2:
        return
    nle = _askint('How many <= constraints (0..6)', 0, 6)
    if nle is None:
        return
    cons = [(-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)]
    shown = []
    for i in range(nle):
        r = _asklist('C' + str(i + 1) + ' <=: a b c')
        if r is None or len(r) < 3:
            return
        cons.append((r[0], r[1], r[2]))
        shown.append(_lin([r[0], r[1]], ['x', 'y']) + ' <= ' + _num(r[2]))
    nge = _askint('How many >= constraints (0..6)', 0, 6)
    if nge is None:
        return
    for i in range(nge):
        r = _asklist('G' + str(i + 1) + ' >=: a b c')
        if r is None or len(r) < 3:
            return
        cons.append((-r[0], -r[1], -r[2]))
        shown.append(_lin([r[0], r[1]], ['x', 'y']) + ' >= ' + _num(r[2]))
    p = obj[0]
    q = obj[1]
    objname = 'P' if mx == 1 else 'C'
    lines = [_w(('Maximise ' if mx == 1 else 'Minimise ') + objname + ' = ' +
             _lin([p, q], ['x', 'y']))]
    lines.append(_w('subject to'))
    for s in shown:
        lines.append(_w('  ' + s))
    lines.append(_w('  x >= 0, y >= 0'))
    vs = _lpverts(cons)
    if not vs:
        lines.append(_warn('The feasible region is EMPTY.'))
        _pages('LP graph 2-D', lines)
        return
    cx = 0.0
    cy = 0.0
    for v in vs:
        cx += v[0]
        cy += v[1]
    cx = cx / len(vs)
    cy = cy / len(vs)
    ang = []
    for v in vs:
        ang.append((casutil.atan2(v[1] - cy, v[0] - cx), v[0], v[1]))
    ang = sorted(ang)
    vs = [(t[1], t[2]) for t in ang]
    rec = _recession(cons)
    lines.append(_w('Vertices of the feasible region:'))
    for v in vs:
        lines.append(_w('  (' + _num(v[0]) + ', ' + _num(v[1]) + ')  ' + objname +
                     ' = ' + _num(p * v[0] + q * v[1])))
    if rec:
        lines.append(_warn('Region is UNBOUNDED; recession directions exist.'))
    bad = False
    for d in rec:
        g = p * d[0] + q * d[1]
        if mx == 1 and g > 1e-9:
            bad = True
        if mx == 0 and g < -1e-9:
            bad = True
    if bad:
        lines.append(_warn(objname + ' is UNBOUNDED on this region.'))
        _pages('LP graph 2-D', lines)
        return
    bv = vs[0]
    bo = p * bv[0] + q * bv[1]
    for v in vs:
        o = p * v[0] + q * v[1]
        if (mx == 1 and o > bo) or (mx == 0 and o < bo):
            bo = o
            bv = v
    lines.append('Optimal vertex: x = ' + _num(bv[0]) + ', y = ' + _num(bv[1]))
    lines.append(objname + ' = ' + _num(bo))
    xlo = vs[0][0]
    xhi = vs[0][0]
    ylo = vs[0][1]
    yhi = vs[0][1]
    for v in vs:
        if v[0] < xlo:
            xlo = v[0]
        if v[0] > xhi:
            xhi = v[0]
        if v[1] < ylo:
            ylo = v[1]
        if v[1] > yhi:
            yhi = v[1]
    ix0 = int(xlo) - 1
    ix1 = int(xhi) + 1
    iy0 = int(ylo) - 1
    iy1 = int(yhi) + 1
    if (ix1 - ix0 + 1) * (iy1 - iy0 + 1) <= 4000:
        bix = None
        bio = 0.0
        i = ix0
        while i <= ix1:
            j = iy0
            while j <= iy1:
                if _feas(cons, i * 1.0, j * 1.0, 1e-9):
                    o = p * i + q * j
                    if bix is None or (mx == 1 and o > bio) or (mx == 0 and o < bio):
                        bio = o
                        bix = (i, j)
                j += 1
            i += 1
        if bix is None:
            lines.append(_warn('No integer point lies in the region.'))
        else:
            lines.append('Best integer point (L10): x = ' + str(bix[0]) +
                         ', y = ' + str(bix[1]) + ', ' + objname + ' = ' + _num(bio))
    _pages('LP graph 2-D', lines)
    xs = [v[0] for v in vs]
    ys = [v[1] for v in vs]
    xs.append(0.0)
    ys.append(0.0)
    gx = casutil.nice_range(xs, 0.12, True)
    gy = casutil.nice_range(ys, 0.12, True)
    fr = casutil.frame(gx[0], gx[1], gy[0], gy[1])
    casutil.axes(fr, 'Feasible region', 'x', 'y')
    nxg = 76
    nyg = 34
    i = 0
    while i <= nxg:
        x = fr[4] + (fr[5] - fr[4]) * i / nxg
        j = 0
        while j <= nyg:
            y = fr[6] + (fr[7] - fr[6]) * j / nyg
            if _feas(cons, x, y, 1e-9):
                casutil.dot(fr, x, y, casui.GREY)
            j += 1
        i += 1
    for cn in cons:
        _lpline(fr, cn[0], cn[1], cn[2], casui.BLACK)
    for v in vs:
        casutil.marker(fr, v[0], v[1], casui.ACC, 2)
    casutil.marker(fr, bv[0], bv[1], casui.RED, 3)
    casutil.chart_hold('optimum (' + _num(bv[0]) + ', ' + _num(bv[1]) + ')')

TOOLS = [
    ('Bubble sort', bubble),
    ('Insertion sort', insertion),
    ('Quick sort', quicksort),
    ('Bin: first-fit', firstfit),
    ('Bin: first-fit decr', firstfitdec),
    ('Graph: degrees/incidence', graphinfo),
    ('Dijkstra shortest', dijkstra),
    ('Prim MST', prim),
    ('Kruskal MST', kruskal),
    ('Max flow / min cut', maxflow),
    ('Cut capacity', cutcap),
    ('Critical path', critpath),
    ('Simplex (max, <=)', simplex),
    ('Simplex 2-stage (>=, =)', simplex2),
    ('LP graph 2-D', lpgraph),
]

def run():
    casutil.run_tools('Modelling w/ Algorithms', TOOLS)
