# OCR B (MEI) Further Maths H645, Modelling with Algorithms (Y433): sorting,
# bin packing, graphs, networks, network flows, critical path analysis and
# linear programming (graphical, simplex, two-stage, big-M, post-optimal).
#
# One input encoding per kind of object, the same in every tool. Nodes and
# events are numbered 1, 2, 3, ...
#   from to*          edges (or arcs) as pairs:           1,2, 1,3, 2,3
#   from to w*        weighted edges/arcs as triples:     1,2,4, 1,3,2
#   from to dur*      activity-on-arc: start event, end event, duration
#   n,rows*           an n x n matrix row by row, 0 = no edge
#   a b rel c*        2-D constraint ax + by (rel) c
#   n,obj rows*       n objective coefficients, then each constraint row
# rel is 1 for <=, 0 for = and -1 for >=.
import math
import casutil

fmt = casutil.fmt
w = casutil.w
warn = casutil.warn

EPS = 1e-9
MAXN = 30          # nodes / events
MAXLIST = 40       # items to sort or pack

# ---- small shared helpers ---------------------------------------------------

def _int(v, name):
    iv = int(v)
    if iv != v:
        raise ValueError(name + ' must be a whole number')
    return iv

def _whole(v, name, lo, hi):
    if v < lo or v > hi:
        raise ValueError(name + ' must be ' + str(lo) + ' to ' + str(hi))
    return _int(v, name)

def _groups(data, k, what):
    if not data or len(data) % k:
        raise ValueError(what + ': values in groups of ' + str(k))
    out = []
    i = 0
    while i < len(data):
        out.append(data[i:i + k])
        i += k
    return out

def _wrap(head, items, width=34, sep=' '):
    # join items after head; continuation lines are indented two spaces
    out = []
    cur = head
    started = False
    for it in items:
        piece = sep + it if started else it
        if started and len(cur) + len(piece) > width:
            out.append(cur.rstrip())
            cur = '  ' + it
        else:
            cur = cur + piece
        started = True
    out.append(cur)
    return out

def _wwrap(head, items, sep=' '):
    return [w(s) for s in _wrap(head, items, 50, sep)]

def _row(lst):
    return [fmt(v) for v in lst]

def _nm(i):
    return str(i + 1)

def _arc(u, v):
    return _nm(u) + '-' + _nm(v)

def _set(flags):
    return '{' + ', '.join([_nm(i) for i in range(len(flags)) if flags[i]]) + '}'

def _items(data):
    if len(data) > MAXLIST:
        raise ValueError('at most ' + str(MAXLIST) + ' items')
    return list(data)

def _lin(coefs, names):
    s = ''
    for j in range(len(coefs)):
        v = coefs[j]
        if abs(v) < 1e-12:
            continue
        a = -v if v < 0 else v
        t = names[j] if abs(a - 1.0) < 1e-12 else fmt(a) + names[j]
        if s == '':
            s = ('-' if v < 0 else '') + t
        else:
            s = s + (' - ' if v < 0 else ' + ') + t
    return s if s else '0'

RELS = {1: '<=', 0: '=', -1: '>='}

def _rel(v):
    r = _int(v, 'rel')
    if r not in RELS:
        raise ValueError('rel must be 1 (<=), 0 (=) or -1 (>=)')
    return r

# ---- graphs and networks: reading edges ------------------------------------

def _node(v, name):
    return _whole(v, name, 1, MAXN) - 1

def _edges(data, k, what):
    # -> (n, [(u, v, w), ...]) with 0-based nodes; w = 1 when k == 2
    out = []
    n = 0
    for g in _groups(data, k, what):
        u = _node(g[0], 'node')
        v = _node(g[1], 'node')
        wt = g[2] if k > 2 else 1
        out.append((u, v, wt))
        if u + 1 > n:
            n = u + 1
        if v + 1 > n:
            n = v + 1
    return n, out

def _weights_ok(edges, what):
    for e in edges:
        if e[2] < 0:
            raise ValueError(what + ' must be >= 0')

def _matrix(n, data):
    n = _whole(n, 'n', 1, 12)
    if len(data) != n * n:
        raise ValueError('need n x n = ' + str(n * n) + ' values')
    return n, [data[i * n:(i + 1) * n] for i in range(n)]

# =============================================================================
# A  Algorithms: sorting, bin packing, complexity
# A4 complexity and problem size, A7 quick sort, A8 comparisons and swaps,
# A10 first fit / first fit decreasing, A11 comparisons in bin packing.
# N/A: AA1, A2, A3, A5, A6, A9 (reading, writing and reasoning about algorithms)
# =============================================================================

def _sorted_lines(a):
    return _wrap('sorted: ', _row(a))

def t_bubble(data):
    a = _items(data)
    n = len(a)
    lines = [w('start: ' + ' '.join(_row(a)))]
    comps = 0
    swaps = 0
    passes = 0
    last = n - 1
    while last > 0:
        passes += 1
        sw = 0
        j = 0
        while j < last:
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                sw += 1
            j += 1
        swaps += sw
        lines.extend(_wwrap('pass ' + str(passes) + ': ', _row(a)))
        if sw == 0:
            lines.append(w('no swaps in pass ' + str(passes) + ': stop'))
            break
        last -= 1
    out = _sorted_lines(a)
    out.append('comparisons = ' + str(comps))
    out.append('swaps = ' + str(swaps))
    out.append('passes = ' + str(passes))
    out.extend(lines)
    out.append(w('each pass one shorter; stop after a swap-free pass'))
    out.append(w('worst case n(n-1)/2 = ' + str(n * (n - 1) // 2) +
                 ' comparisons: O(n^2)'))
    return out

def t_shuttle(data):
    a = _items(data)
    n = len(a)
    lines = [w('start: ' + ' '.join(_row(a)))]
    comps = 0
    swaps = 0
    i = 1
    while i < n:
        j = i
        while j > 0:
            comps += 1
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                swaps += 1
                j -= 1
            else:
                break
        lines.extend(_wwrap('pass ' + str(i) + ': ', _row(a)))
        i += 1
    out = _sorted_lines(a)
    out.append('comparisons = ' + str(comps))
    out.append('swaps = ' + str(swaps))
    out.append('passes = ' + str(n - 1 if n > 1 else 0))
    out.extend(lines)
    out.append(w('pass k shuttles item k+1 back into place'))
    out.append(w('(insertion sort: swaps = shifts)'))
    out.append(w('worst case n(n-1)/2 = ' + str(n * (n - 1) // 2) +
                 ' comparisons: O(n^2)'))
    return out

def _qshow(a, fixed):
    parts = []
    for i in range(len(a)):
        parts.append('[' + fmt(a[i]) + ']' if fixed[i] else fmt(a[i]))
    return parts

def t_quick(data):
    a = _items(data)
    n = len(a)
    fixed = [False] * n
    lines = [w('start: ' + ' '.join(_row(a))),
             w('pivot = first item of each sub-list; [ ] = in place')]
    stack = [(0, n - 1)] if n > 1 else []
    if n == 1:
        fixed[0] = True
    comps = 0
    p = 0
    while stack and p <= 2 * n + 4:
        p += 1
        nxt = []
        for lo, hi in stack:
            piv = a[lo]
            left = []
            right = []
            k = lo + 1
            while k <= hi:
                comps += 1
                if a[k] <= piv:
                    left.append(a[k])
                else:
                    right.append(a[k])
                k += 1
            seq = left + [piv] + right
            for k in range(len(seq)):
                a[lo + k] = seq[k]
            pp = lo + len(left)
            fixed[pp] = True
            if pp - 1 > lo:
                nxt.append((lo, pp - 1))
            elif pp - 1 == lo:
                fixed[lo] = True
            if hi > pp + 1:
                nxt.append((pp + 1, hi))
            elif hi == pp + 1:
                fixed[hi] = True
        lines.extend(_wwrap('pass ' + str(p) + ': ', _qshow(a, fixed)))
        stack = nxt
    out = _sorted_lines(a)
    out.append('comparisons = ' + str(comps))
    out.append('passes = ' + str(p))
    out.extend(lines)
    out.append(w('items <= pivot go left, in their original order'))
    out.append(w('O(n log n) on average; worst n(n-1)/2 = ' +
                 str(n * (n - 1) // 2) + ', O(n^2)'))
    return out

def _pack(items, cap):
    bins = []
    comps = 0
    for it in items:
        placed = False
        for b in bins:
            comps += 1
            if b[0] + it <= cap + EPS:
                b[0] += it
                b[1].append(it)
                placed = True
                break
        if not placed:
            bins.append([it, [it]])
    return bins, comps

def _packlines(items, cap):
    if cap <= 0:
        raise ValueError('C must be > 0')
    tot = 0.0
    for it in items:
        if it <= 0:
            raise ValueError('sizes must be > 0')
        if it > cap + EPS:
            raise ValueError('item ' + fmt(it) + ' is bigger than C')
        tot += it
    bins, comps = _pack(items, cap)
    low = int(tot / cap)
    if low * cap < tot - EPS:
        low += 1
    out = ['bins used = ' + str(len(bins)),
           'comparisons = ' + str(comps)]
    for i in range(len(bins)):
        b = bins[i]
        out.extend(_wrap('bin ' + str(i + 1) + ': ', _row(b[1]) + ['(' + fmt(b[0]) + ')']))
    out.append('lower bound = ' + str(low) + ' bins')
    out.append(w('lower bound = ceil(total / C) = ceil(' + fmt(tot) + '/' + fmt(cap) + ')'))
    if len(bins) == low:
        out.append(w('meets the lower bound, so optimal'))
    out.append(w('comparison = one "does it fit this bin?" test'))
    return out

def t_firstfit(cap, data):
    items = _items(data)
    out = _packlines(items, cap)
    out.append(w('first fit: each item into the first bin it fits'))
    return out

def t_ffd(cap, data):
    items = _items(data)
    items = sorted(items, reverse=True)
    out = _packlines(items, cap)
    n = len(items)
    out.extend(_wwrap('sorted first: ', _row(items)))
    out.append(w('sorting adds up to n(n-1)/2 = ' + str(n * (n - 1) // 2) +
                 ' comparisons'))
    return out

def t_order(k, n1, t1, n2):
    if n1 <= 0 or n2 <= 0:
        raise ValueError('sizes must be > 0')
    if t1 < 0:
        raise ValueError('t1 must be >= 0')
    r = float(n2) / n1
    f = r ** k
    return ['t2 = ' + fmt(t1 * f),
            'factor = ' + fmt(f),
            w('order n^k: t2 = t1 x (n2/n1)^k'),
            w('= ' + fmt(t1) + ' x (' + fmt(n2) + '/' + fmt(n1) + ')^' + fmt(k)),
            w('O(n^2): bubble, shuttle, Prim, Dijkstra (matrix)')]

def t_order_nlogn(n1, t1, n2):
    if n1 <= 1 or n2 <= 1:
        raise ValueError('sizes must be > 1')
    if t1 < 0:
        raise ValueError('t1 must be >= 0')
    f = (n2 * math.log(n2)) / (n1 * math.log(n1))
    return ['t2 = ' + fmt(t1 * f),
            'factor = ' + fmt(f),
            w('t2 = t1 x (n2 ln n2)/(n1 ln n1)'),
            w('O(n log n): quick sort on average')]

# =============================================================================
# G  Graphs
# AN1 vocabulary, adjacency and incidence matrices; N3 directed/undirected.
# N/A: N2 (modelling with graphs)
# =============================================================================

def _connected(n, edges):
    seen = [False] * n
    if n == 0:
        return True
    seen[0] = True
    q = [0]
    h = 0
    while h < len(q):
        u = q[h]
        h += 1
        for a, b, x in edges:
            for s, t in ((a, b), (b, a)):
                if s == u and not seen[t]:
                    seen[t] = True
                    q.append(t)
    for s in seen:
        if not s:
            return False
    return True

def _reach(n, arcs, s):
    seen = [False] * n
    seen[s] = True
    q = [s]
    h = 0
    while h < len(q):
        u = q[h]
        h += 1
        for a, b, x in arcs:
            if a == u and not seen[b]:
                seen[b] = True
                q.append(b)
    return seen

def _matlines(rows):
    out = []
    for i in range(len(rows)):
        out.extend(_wrap(_nm(i) + ': ', rows[i]))
    return out

def _graph_report(n, edges):
    m = len(edges)
    deg = [0] * n
    adj = [[0] * n for i in range(n)]
    loops = 0
    for u, v, x in edges:
        deg[u] += 1
        deg[v] += 1
        if u == v:
            loops += 1
            adj[u][u] += 1
        else:
            adj[u][v] += 1
            adj[v][u] += 1
    multi = False
    for i in range(n):
        for j in range(n):
            if i != j and adj[i][j] > 1:
                multi = True
    odd = [_nm(i) for i in range(n) if deg[i] % 2]
    out = ['order = ' + str(n) + ' nodes', 'size = ' + str(m) + ' edges']
    out.extend(_wrap('degrees 1..n: ', [str(d) for d in deg]))
    out.extend(_wrap('odd nodes: ', odd if odd else ['none']))
    out.append('connected: ' + ('yes' if _connected(n, edges) else 'no'))
    out.append('simple: ' + ('no' if loops or multi else 'yes'))
    out.append(w('sum of degrees = ' + str(sum(deg)) + ' = 2 x ' + str(m)))
    if n > 1 and m == n * (n - 1) // 2 and not loops and not multi:
        out.append(w('complete graph K' + str(n)))
    if _connected(n, edges) and m == n - 1 and not loops:
        out.append(w('connected with n-1 edges: a tree'))
    out.append('adjacency (row i, col j):')
    out.extend(_matlines([[str(x) for x in r] for r in adj]))
    if loops:
        out.append(w('a loop: 1 on the diagonal, adds 2 to the degree'))
    out.append('incidence (row node, col edge):')
    out.extend(_wwrap('edges: ', ['e' + str(k + 1) + '=' + _arc(edges[k][0], edges[k][1])
                                  for k in range(m)]))
    rows = []
    for i in range(n):
        r = []
        for u, v, x in edges:
            r.append('2' if u == v == i else ('1' if u == i or v == i else '0'))
        rows.append(r)
    out.extend(_matlines(rows))
    return out

def _digraph_report(n, arcs):
    m = len(arcs)
    outd = [0] * n
    ind = [0] * n
    adj = [[0] * n for i in range(n)]
    for u, v, x in arcs:
        outd[u] += 1
        ind[v] += 1
        adj[u][v] += 1
    strong = True
    for s in range(n):
        for f in _reach(n, arcs, s):
            if not f:
                strong = False
    out = ['order = ' + str(n) + ' nodes', 'size = ' + str(m) + ' arcs']
    out.extend(_wrap('out 1..n: ', [str(d) for d in outd]))
    out.extend(_wrap('in 1..n: ', [str(d) for d in ind]))
    out.append('connected: ' + ('yes' if _connected(n, arcs) else 'no'))
    out.append('strongly connected: ' + ('yes' if strong else 'no'))
    out.append(w('sum out = sum in = ' + str(m) + ' arcs'))
    out.append('adjacency (arcs row -> col):')
    out.extend(_matlines([[str(x) for x in r] for r in adj]))
    out.append('incidence (row node, col arc):')
    out.extend(_wwrap('arcs: ', ['e' + str(k + 1) + '=' + _arc(arcs[k][0], arcs[k][1])
                                 for k in range(m)]))
    rows = []
    for i in range(n):
        r = []
        for u, v, x in arcs:
            r.append('0' if u == v == i else ('-1' if u == i else ('1' if v == i else '0')))
        rows.append(r)
    out.extend(_matlines(rows))
    out.append(w('-1 = arc leaves the node, 1 = arc enters it'))
    return out

def _nodes_n(n, top):
    n = _whole(n, 'n', 1, MAXN)
    if top > n:
        raise ValueError('node ' + str(top) + ' is more than n')
    return n

def t_graph(n, data):
    top, edges = _edges(data, 2, 'from to')
    return _graph_report(_nodes_n(n, top), edges)

def t_digraph(n, data):
    top, arcs = _edges(data, 2, 'from to')
    return _digraph_report(_nodes_n(n, top), arcs)

def t_adjacency(n, data):
    n, rows = _matrix(n, data)
    sym = True
    for i in range(n):
        for j in range(n):
            v = rows[i][j]
            if v < 0 or v != int(v) or v > 20:
                raise ValueError('entries must be whole numbers 0 to 20')
            if rows[i][j] != rows[j][i]:
                sym = False
    edges = []
    for i in range(n):
        for j in range(i if sym else 0, n):
            for k in range(int(rows[i][j])):
                edges.append((i, j, 1))
    if sym:
        out = ['undirected (matrix symmetric)']
        out.extend(_graph_report(n, edges))
        for i in range(n):
            if rows[i][i]:
                out.append(warn('diagonal read as loops; some books write 2'))
                break
        return out
    out = ['directed (matrix not symmetric)']
    out.extend(_digraph_report(n, edges))
    return out

# =============================================================================
# N  Networks: shortest path and minimum connector
# N3 weighted networks, N5 Kruskal (and Prim), N6 Dijkstra, N7 orders,
# L6 / N13 shortest path formulated as an LP.
# N/A: N4 (modelling with networks)
# =============================================================================

def _wmatrix(n, edges, directed):
    # least weight between each ordered pair; None = no edge
    m = [[None] * n for i in range(n)]
    for u, v, x in edges:
        if u == v:
            continue
        if m[u][v] is None or x < m[u][v]:
            m[u][v] = x
        if not directed and (m[v][u] is None or x < m[v][u]):
            m[v][u] = x
    return m

def _dijkstra(start, end, data, directed):
    top, edges = _edges(data, 3, 'from to w')
    _weights_ok(edges, 'weights')
    s = _node(start, 'start')
    n = top if top > s + 1 else s + 1
    t = -1
    if end != 0:
        t = _node(end, 'end')
        if t + 1 > n:
            n = t + 1
    m = _wmatrix(n, edges, directed)
    dist = [None] * n
    done = [False] * n
    prev = [-1] * n
    work = [[] for i in range(n)]
    order = []
    dist[s] = 0
    work[s].append(0)
    while True:
        u = -1
        for i in range(n):
            if not done[i] and dist[i] is not None and (u < 0 or dist[i] < dist[u]):
                u = i
        if u < 0:
            break
        done[u] = True
        order.append(u)
        for v in range(n):
            x = m[u][v]
            if x is not None and not done[v] and (dist[v] is None or dist[u] + x < dist[v]):
                dist[v] = dist[u] + x
                prev[v] = u
                work[v].append(dist[v])
    out = []
    if t >= 0:
        if dist[t] is None:
            out.append(warn('no route from ' + _nm(s) + ' to ' + _nm(t)))
        else:
            path = [t]
            u = t
            while u != s:
                u = prev[u]
                path.append(u)
            path.reverse()
            out.append('shortest ' + _nm(s) + ' to ' + _nm(t) + ' = ' + fmt(dist[t]))
            out.extend(_wrap('route: ', [_nm(v) for v in path], 34, '-'))
    out.append('final labels:')
    for i in range(n):
        if dist[i] is None:
            out.append('node ' + _nm(i) + ': unreachable')
        else:
            out.append('node ' + _nm(i) + ': ' + fmt(dist[i]) + ' (order ' +
                       str(order.index(i) + 1) + ')')
    for i in range(n):
        if work[i]:
            out.extend(_wwrap('node ' + _nm(i) + ' working: ', _row(work[i]), ', '))
    out.extend(_wwrap('permanent order: ', [_nm(v) for v in order], ', '))
    out.append(w('Dijkstra is O(n^2) for n nodes'))
    if directed:
        out.append(w('arcs one way only: from -> to'))
    return out

def t_dijkstra(start, end, data):
    return _dijkstra(start, end, data, False)

def t_dijkstra_d(start, end, data):
    return _dijkstra(start, end, data, True)

def _prim(n, m, s):
    intree = [False] * n
    intree[s] = True
    joined = [s]
    chosen = []
    total = 0
    while len(joined) < n:
        best = None
        for u in joined:
            for v in range(n):
                x = m[u][v]
                if not intree[v] and x is not None and (best is None or x < best[2]):
                    best = (u, v, x)
        if best is None:
            break
        intree[best[1]] = True
        joined.append(best[1])
        chosen.append(best)
        total += best[2]
    out = ['MST weight = ' + fmt(total)]
    for u, v, x in chosen:
        out.append(_arc(u, v) + '  (' + fmt(x) + ')')
    if len(joined) < n:
        out.append(warn('not connected: no spanning tree'))
    out.extend(_wwrap('nodes joined in order: ', [_nm(v) for v in joined], ', '))
    out.append(w('Prim: add the least arc from the tree to a new node'))
    out.append(w('Prim is O(n^2) for n nodes (matrix form)'))
    return out

def t_prim(start, data):
    top, edges = _edges(data, 3, 'from to w')
    s = _node(start, 'start')
    n = top if top > s + 1 else s + 1
    return _prim(n, _wmatrix(n, edges, False), s)

def t_prim_matrix(n, start, data):
    n, rows = _matrix(n, data)
    s = _node(start, 'start')
    if s >= n:
        raise ValueError('start must be 1 to n')
    m = [[None] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and rows[i][j] > 0:
                m[i][j] = rows[i][j]
    out = _prim(n, m, s)
    out.append(w('0 in the matrix = no edge'))
    return out

def _root(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i

def t_kruskal(data):
    n, edges = _edges(data, 3, 'from to w')
    idx = sorted(range(len(edges)), key=lambda k: (edges[k][2], k))
    parent = list(range(n))
    chosen = []
    notes = []
    total = 0
    for k in idx:
        u, v, x = edges[k]
        if len(chosen) == n - 1:
            break
        ru = _root(parent, u)
        rv = _root(parent, v)
        if ru == rv:
            notes.append(w('reject ' + _arc(u, v) + ' (' + fmt(x) + '): makes a cycle'))
        else:
            parent[ru] = rv
            chosen.append((u, v, x))
            notes.append(w('accept ' + _arc(u, v) + ' (' + fmt(x) + ')'))
            total += x
    out = ['MST weight = ' + fmt(total)]
    for u, v, x in chosen:
        out.append(_arc(u, v) + '  (' + fmt(x) + ')')
    if len(chosen) < n - 1:
        out.append(warn('not connected: no spanning tree'))
    out.extend(notes)
    out.append(w('Kruskal: arcs in weight order, skip any cycle'))
    out.append(w('Kruskal is O(m log m) for m arcs (the sort)'))
    return out

def _xname(u, v):
    if u < 9 and v < 9:
        return 'x' + _nm(u) + _nm(v)
    return 'x' + _nm(u) + '_' + _nm(v)

def _sumterms(terms):
    # terms: list of (sign, name) -> ['x12', '+ x13', '- x21']
    out = []
    for sg, nm in terms:
        if not out:
            out.append(('-' if sg < 0 else '') + nm)
        else:
            out.append(('- ' if sg < 0 else '+ ') + nm)
    return out

def t_splp(start, end, data):
    top, edges = _edges(data, 3, 'from to w')
    _weights_ok(edges, 'weights')
    s = _node(start, 'start')
    t = _node(end, 'end')
    if s == t:
        raise ValueError('start and end must differ')
    n = max(top, s + 1, t + 1)
    m = _wmatrix(n, edges, False)
    arcs = []
    for u in range(n):
        for v in range(n):
            if m[u][v] is not None:
                arcs.append((u, v, m[u][v]))
    out = []
    obj = []
    for u, v, x in arcs:
        obj.append((1, (fmt(x) if x != 1 else '') + _xname(u, v)))
    out.extend(_wrap('Minimise ', _sumterms(obj)))
    out.append('subject to (out - in):')
    for i in range(n):
        terms = []
        for u, v, x in arcs:
            if u == i:
                terms.append((1, _xname(u, v)))
        for u, v, x in arcs:
            if v == i:
                terms.append((-1, _xname(u, v)))
        if not terms:
            continue
        rhs = '1' if i == s else ('-1' if i == t else '0')
        out.extend(_wrap(_nm(i) + ': ', _sumterms(terms) + ['= ' + rhs]))
    out.append('each x = 0 or 1 (or >= 0)')
    res = _dijkstra(start, end, data, False)
    out.append(w('xij = 1 if the route uses arc i -> j'))
    out.append(w('each edge gives two arcs, one each way'))
    if isinstance(res[0], str):
        out.append(w('LP optimum = ' + res[0]))
    return out

# =============================================================================
# F  Network flows
# N10 sources and sinks, N11 cuts and capacity, N12 max flow / min cut and
# flow augmentation, L6 / N13 max flow formulated as an LP.
# =============================================================================

def _capnet(source, sink, data):
    top, arcs = _edges(data, 3, 'from to cap')
    _weights_ok(arcs, 'capacities')
    s = _node(source, 'source')
    t = _node(sink, 'sink')
    if s == t:
        raise ValueError('source and sink must differ')
    n = max(top, s + 1, t + 1)
    cap = [[0] * n for i in range(n)]
    for u, v, x in arcs:
        if u != v:
            cap[u][v] += x
    return n, s, t, cap

def _augment(cap, flow, s, t):
    n = len(cap)
    pred = [-1] * n
    seen = [False] * n
    seen[s] = True
    q = [s]
    h = 0
    while h < len(q):
        u = q[h]
        h += 1
        for v in range(n):
            if not seen[v] and cap[u][v] - flow[u][v] > EPS:
                seen[v] = True
                pred[v] = u
                if v == t:
                    return pred, seen
                q.append(v)
    return None, seen

def _maxflow(cap, s, t, notes):
    n = len(cap)
    flow = [[0] * n for i in range(n)]
    total = 0
    it = 0
    while it < 500:
        pred, seen = _augment(cap, flow, s, t)
        if pred is None:
            return flow, total, seen
        path = [t]
        u = t
        while u != s:
            u = pred[u]
            path.append(u)
        path.reverse()
        b = None
        for k in range(len(path) - 1):
            r = cap[path[k]][path[k + 1]] - flow[path[k]][path[k + 1]]
            if b is None or r < b:
                b = r
        for k in range(len(path) - 1):
            flow[path[k]][path[k + 1]] += b
            flow[path[k + 1]][path[k]] -= b
        total += b
        it += 1
        if notes is not None:
            notes.extend(_wwrap('path ' + str(it) + ' flow ' + fmt(b) + ': ',
                                [_nm(v) for v in path], '-'))
    raise ValueError('too many augmenting paths')

def t_maxflow(source, sink, data):
    n, s, t, cap = _capnet(source, sink, data)
    notes = []
    flow, total, seen = _maxflow(cap, s, t, notes)
    out = ['max flow = ' + fmt(total)]
    ccap = 0
    carcs = []
    for i in range(n):
        for j in range(n):
            if seen[i] and not seen[j] and cap[i][j] > 0:
                carcs.append(_arc(i, j))
                ccap += cap[i][j]
    out.append('min cut S = ' + _set(seen))
    out.append('T = ' + _set([not x for x in seen]))
    out.extend(_wrap('cut arcs: ', carcs if carcs else ['none']))
    out.append('cut capacity = ' + fmt(ccap))
    out.append('flows (flow/cap, * = saturated):')
    for i in range(n):
        for j in range(n):
            if cap[i][j] > 0:
                f = flow[i][j] if flow[i][j] > 0 else 0
                out.append(_arc(i, j) + ': ' + fmt(f) + '/' + fmt(cap[i][j]) +
                           (' *' if f >= cap[i][j] - EPS else ''))
    out.append(w('augmenting paths (shortest first):'))
    out.extend(notes)
    out.append(w('max flow = min cut = ' + fmt(total)))
    out.append(w('S = nodes still reachable by unsaturated arcs'))
    return out

def t_cut(source, sink, sdig, data):
    n, s, t, cap = _capnet(source, sink, data)
    k = _whole(sdig, 'S', 1, 999999999)
    inS = [False] * n
    for ch in str(k):
        d = int(ch)
        if d < 1 or d > n:
            raise ValueError('S digits must be nodes 1 to ' + str(min(n, 9)))
        inS[d - 1] = True
    if not inS[s]:
        raise ValueError('the source must be in S')
    if inS[t]:
        raise ValueError('the sink must not be in S')
    ccap = 0
    back = 0
    fw = []
    for i in range(n):
        for j in range(n):
            if cap[i][j] > 0 and inS[i] and not inS[j]:
                fw.append(_arc(i, j) + ' (' + fmt(cap[i][j]) + ')')
                ccap += cap[i][j]
            elif cap[i][j] > 0 and inS[j] and not inS[i]:
                back += cap[i][j]
    flow, total, seen = _maxflow(cap, s, t, None)
    out = ['cut capacity = ' + fmt(ccap),
           'S = ' + _set(inS),
           'T = ' + _set([not x for x in inS])]
    out.extend(_wrap('S to T: ', fw if fw else ['none']))
    out.append('max flow = ' + fmt(total))
    if abs(total - ccap) < EPS:
        out.append('this is a minimum cut')
    else:
        out.append('not minimum: ' + fmt(ccap - total) + ' over')
    out.append(w('only arcs S -> T count; T -> S total ' + fmt(back)))
    out.append(w('any cut capacity >= max flow'))
    return out

def t_flowlp(source, sink, data):
    n, s, t, cap = _capnet(source, sink, data)
    arcs = []
    for u in range(n):
        for v in range(n):
            if cap[u][v] > 0:
                arcs.append((u, v))
    obj = []
    for u, v in arcs:
        if u == s:
            obj.append((1, _xname(u, v)))
    for u, v in arcs:
        if v == s:
            obj.append((-1, _xname(u, v)))
    out = []
    out.extend(_wrap('Maximise F = ', _sumterms(obj) if obj else ['0']))
    out.append('subject to (in = out):')
    for i in range(n):
        if i == s or i == t:
            continue
        ins = [(1, _xname(u, v)) for u, v in arcs if v == i]
        outs = [(1, _xname(u, v)) for u, v in arcs if u == i]
        if not ins and not outs:
            continue
        out.extend(_wrap(_nm(i) + ': ', (_sumterms(ins) if ins else ['0']) + ['='] +
                         (_sumterms(outs) if outs else ['0'])))
    caps = [('0<=' + _xname(u, v) + '<=' + fmt(cap[u][v])) for u, v in arcs]
    out.extend(_wrap('', caps, 34, ', '))
    flow, total, seen = _maxflow(cap, s, t, None)
    out.append(w('F = net flow out of the source'))
    out.append(w('LP optimum = max flow = ' + fmt(total)))
    return out

# =============================================================================
# C  Critical path analysis
# N8 activity-on-arc networks (dummies are arcs of duration 0),
# N9 critical path, total / independent / interfering float, resourcing.
# =============================================================================

def _events(data):
    top, acts = _edges(data, 3, 'from to dur')
    _weights_ok(acts, 'durations')
    n = top
    for u, v, d in acts:
        if u == v:
            raise ValueError('an activity must join two events')
    # topological order (Kahn), refuse cycles
    indeg = [0] * n
    for u, v, d in acts:
        indeg[v] += 1
    order = [i for i in range(n) if indeg[i] == 0]
    h = 0
    while h < len(order):
        u = order[h]
        h += 1
        for a, b, d in acts:
            if a == u:
                indeg[b] -= 1
                if indeg[b] == 0:
                    order.append(b)
    if len(order) < n:
        raise ValueError('the network has a cycle')
    early = [0] * n
    for u in order:
        for a, b, d in acts:
            if a == u and early[a] + d > early[b]:
                early[b] = early[a] + d
    proj = max(early)
    late = [proj] * n
    for u in order[::-1]:
        for a, b, d in acts:
            if a == u and late[b] - d < late[a]:
                late[a] = late[b] - d
    return n, acts, early, late, proj

def t_cpa(data):
    n, acts, early, late, proj = _events(data)
    out = ['duration = ' + fmt(proj)]
    crit = []
    rows = []
    for u, v, d in acts:
        tf = late[v] - early[u] - d
        ind = early[v] - late[u] - d
        if ind < 0:
            ind = 0
        if abs(tf) < EPS:
            crit.append(_arc(u, v))
        rows.append(_arc(u, v) + ' d' + fmt(d) + ' TF ' + fmt(tf) +
                    ' IF ' + fmt(ind) + ' int ' + fmt(tf - ind))
    out.extend(_wrap('critical: ', crit if crit else ['none']))
    out.append('events: early, late')
    for i in range(n):
        out.append(_nm(i) + ': ' + fmt(early[i]) + ', ' + fmt(late[i]))
    out.append('activity d, TF, IF, interfering:')
    out.extend(rows)
    seen = {}
    for u, v, d in acts:
        key = (u, v)
        if key in seen:
            out.append(warn('two activities ' + _arc(u, v) + ': add a dummy'))
        seen[key] = True
    starts = [i for i in range(n) if not [1 for a, b, d in acts if b == i]]
    ends = [i for i in range(n) if not [1 for a, b, d in acts if a == i]]
    if len(starts) > 1 or len(ends) > 1:
        out.append(warn('more than one start or end event'))
    out.append(w('forward pass: early(j) = max early(i) + d'))
    out.append(w('backward pass: late(i) = min late(j) - d'))
    out.append(w('total float TF = late(j) - early(i) - d'))
    out.append(w('independent IF = max(0, early(j) - late(i) - d)'))
    out.append(w('interfering = TF - IF'))
    out.append(w('d0 = dummy'))
    return out

def _letter(i):
    return chr(65 + i) if i < 26 else 'A' + str(i + 1)

def t_cpa_table(data):
    acts = []
    i = 0
    while i < len(data):
        d = data[i]
        if i + 1 >= len(data):
            raise ValueError('each activity: dur, k, then k preds')
        k = _whole(data[i + 1], 'k', 0, 26)
        if i + 2 + k > len(data):
            raise ValueError('activity ' + _letter(len(acts)) + ' needs ' + str(k) + ' preds')
        if d < 0:
            raise ValueError('durations must be >= 0')
        acts.append((d, [_whole(p, 'pred', 1, 26) - 1 for p in data[i + 2:i + 2 + k]]))
        i += 2 + k
        if len(acts) > 26:
            raise ValueError('at most 26 activities')
    n = len(acts)
    for j in range(n):
        for p in acts[j][1]:
            if p >= n or p == j:
                raise ValueError('pred of ' + _letter(j) + ' must be 1 to ' +
                                 str(n) + ', not itself')
    # topological order (Kahn), refuse cycles
    cnt = [len(acts[j][1]) for j in range(n)]
    order = [j for j in range(n) if cnt[j] == 0]
    h = 0
    while h < len(order):
        u = order[h]
        h += 1
        for q in range(n):
            for p in acts[q][1]:
                if p == u:
                    cnt[q] -= 1
                    if cnt[q] == 0:
                        order.append(q)
    if len(order) < n:
        raise ValueError('the precedences form a cycle')
    es = [0] * n
    for j in order:
        for p in acts[j][1]:
            if es[p] + acts[p][0] > es[j]:
                es[j] = es[p] + acts[p][0]
    ef = [es[j] + acts[j][0] for j in range(n)]
    proj = max(ef)
    lf = [proj] * n
    for j in order[::-1]:
        for q in range(n):
            if j in acts[q][1] and lf[q] - acts[q][0] < lf[j]:
                lf[j] = lf[q] - acts[q][0]
    out = ['duration = ' + fmt(proj)]
    crit = [_letter(j) for j in range(n) if abs(lf[j] - ef[j]) < EPS]
    out.extend(_wrap('critical: ', crit if crit else ['none']))
    out.append('activity d, ES, LF, TF:')
    for j in range(n):
        out.append(_letter(j) + ' d' + fmt(acts[j][0]) + ' ES ' + fmt(es[j]) +
                   ' LF ' + fmt(lf[j]) + ' TF ' + fmt(lf[j] - ef[j]))
    out.append(w('input per activity: dur, k, then its k preds'))
    out.append(w('activities 1, 2, 3, ... shown as A, B, C, ...'))
    out.append(w('TF = LF - ES - d'))
    out.append(w('for IF and interfering use the activity-on-arc tool'))
    return out

def _profile(spans):
    # spans: (start, end, level) -> merged [(t0, t1, level)]
    pts = []
    for a, b, r in spans:
        if b > a:
            pts.append(a)
            pts.append(b)
    pts = sorted(set(pts))
    out = []
    for k in range(len(pts) - 1):
        t0 = pts[k]
        t1 = pts[k + 1]
        lev = 0
        for a, b, r in spans:
            if a <= t0 + EPS and b >= t1 - EPS:
                lev += r
        if out and abs(out[-1][2] - lev) < EPS:
            out[-1] = (out[-1][0], t1, lev)
        else:
            out.append((t0, t1, lev))
    return out

def t_resource(data):
    gs = _groups(data, 4, 'from to dur res')
    tri = []
    res = []
    for g in gs:
        tri.extend(g[:3])
        if g[3] < 0:
            raise ValueError('resources must be >= 0')
        res.append(g[3])
    n, acts, early, late, proj = _events(tri)
    es = []
    ls = []
    work = 0
    for k in range(len(acts)):
        u, v, d = acts[k]
        es.append((early[u], early[u] + d, res[k]))
        ls.append((late[v] - d, late[v], res[k]))
        work += d * res[k]
    pe = _profile(es)
    pl = _profile(ls)
    peak_e = max([p[2] for p in pe]) if pe else 0
    peak_l = max([p[2] for p in pl]) if pl else 0
    low = 0
    if proj > 0:
        low = int(work / proj)
        if low * proj < work - EPS:
            low += 1
    out = ['duration = ' + fmt(proj),
           'peak, all early = ' + fmt(peak_e),
           'peak, all late = ' + fmt(peak_l),
           'lower bound = ' + str(low) + ' workers']
    out.append('early start profile:')
    for a, b, r in pe:
        out.append('  ' + fmt(a) + ' to ' + fmt(b) + ': ' + fmt(r))
    out.append('late start profile:')
    for a, b, r in pl:
        out.append('  ' + fmt(a) + ' to ' + fmt(b) + ': ' + fmt(r))
    out.append(w('total work = sum d x res = ' + fmt(work)))
    out.append(w('workers >= ceil(work / duration) to finish in time'))
    out.append(w('levelling: move float activities between the two'))
    return out

def t_schedule(k, data):
    k = _whole(k, 'workers', 1, 10)
    n, acts, early, late, proj = _events(data)
    na = len(acts)
    start = [None] * na
    fin = [None] * na
    who = [None] * na
    free = [0] * k
    t = 0
    guard = 0
    while None in fin and guard < 4 * na + 10:
        guard += 1
        # an activity is ready when every activity into its start event is done
        ready = []
        for i in range(na):
            if start[i] is not None:
                continue
            ok = True
            for j in range(na):
                if acts[j][1] == acts[i][0] and (fin[j] is None or fin[j] > t + EPS):
                    ok = False
            if ok:
                ready.append(i)
        dummies = [i for i in ready if acts[i][2] == 0]
        if dummies:
            for i in dummies:
                start[i] = t
                fin[i] = t
            continue
        ready = sorted(ready, key=lambda i: (late[acts[i][1]] - acts[i][2], i))
        for wk in range(k):
            if free[wk] <= t + EPS and ready:
                i = ready.pop(0)
                start[i] = t
                fin[i] = t + acts[i][2]
                who[i] = wk
                free[wk] = fin[i]
        later = [f for f in fin if f is not None and f > t + EPS]
        if not later:
            if None in fin and not ready:
                break
            continue
        t = min(later)
    if None in fin:
        raise ValueError('could not schedule every activity')
    end = max(fin)
    out = ['finish time = ' + fmt(end),
           'critical path = ' + fmt(proj)]
    for wk in range(k):
        jobs = [i for i in range(na) if who[i] == wk]
        jobs = sorted(jobs, key=lambda i: start[i])
        out.extend(_wrap('W' + str(wk + 1) + ': ', [_arc(acts[i][0], acts[i][1]) + ' ' +
                                                  fmt(start[i]) + '-' + fmt(fin[i])
                                                  for i in jobs] or ['idle'], 34, ', '))
    if end > proj + EPS:
        out.append(w('late by ' + fmt(end - proj) + ': more workers needed'))
    out.append(w('when a worker is free, start the ready activity'))
    out.append(w('with the least latest start time (critical first)'))
    out.append(w('a heuristic: not always the best schedule'))
    return out

# =============================================================================
# L  Linear programming, graphical
# L5 / L10 integer solutions, L7 / L8 2-D graphical, L11 3-D vertices,
# L15 = as a pair of inequalities.
# N/A: AL1, L2, L17, L18 (language, modelling, interpreting output)
# =============================================================================

def _cons(data, k, names, limit):
    # rows of k numbers: coefficients, rel, rhs -> (<= rows, shown, notes)
    gs = _groups(data, k, 'a b rel c' if k == 4 else 'a b c rel d')
    if len(gs) > limit:
        raise ValueError('at most ' + str(limit) + ' constraints')
    cons = []
    shown = []
    notes = []
    for g in gs:
        a = g[:k - 2]
        r = _rel(g[k - 2])
        c = g[k - 1]
        shown.append(_lin(a, names) + ' ' + RELS[r] + ' ' + fmt(c))
        if r >= 0:
            cons.append((a, c))
        if r <= 0:
            cons.append(([-x for x in a], -c))
        if r == 0:
            notes.append(w('L15: ' + _lin(a, names) + ' = ' + fmt(c) + ' is <= and >='))
    for j in range(k - 2):
        e = [0] * (k - 2)
        e[j] = -1
        cons.append((e, 0))
    return cons, shown, notes

def _feas(cons, x, tol):
    for a, c in cons:
        s = 0
        for j in range(len(a)):
            s += a[j] * x[j]
        if s > c + tol:
            return False
    return True

def _solve(rows, rhs):
    # Gaussian elimination with partial pivoting; None if singular
    n = len(rows)
    m = [list(rows[i]) + [rhs[i]] for i in range(n)]
    for c in range(n):
        p = c
        for r in range(c + 1, n):
            if abs(m[r][c]) > abs(m[p][c]):
                p = r
        if abs(m[p][c]) < 1e-12:
            return None
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                for k in range(c, n + 1):
                    m[r][k] -= f * m[c][k]
    return [m[i][n] / m[i][i] for i in range(n)]

def _verts(cons, dim):
    idx = list(range(dim))
    vs = []
    while True:
        x = _solve([cons[i][0] for i in idx], [cons[i][1] for i in idx])
        if x is not None and _feas(cons, x, 1e-7):
            new = True
            for v in vs:
                if max([abs(v[j] - x[j]) for j in range(dim)]) < 1e-7:
                    new = False
            if new:
                vs.append([casutil.clean(t) if abs(t) > 1e-12 else 0 for t in x])
        # next combination of dim constraint indices
        k = dim - 1
        while k >= 0 and idx[k] == len(cons) - dim + k:
            k -= 1
        if k < 0:
            return vs
        idx[k] += 1
        for j in range(k + 1, dim):
            idx[j] = idx[j - 1] + 1

def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]

def _rays(cons, dim):
    # extreme directions of the recession cone {d : a.d <= 0}
    cands = []
    for j in range(dim):
        e = [0] * dim
        e[j] = 1
        cands.append(e)
    for i in range(len(cons)):
        a = cons[i][0]
        if dim == 2:
            cands.append([a[1], -a[0]])
            cands.append([-a[1], a[0]])
        else:
            for k in range(i + 1, len(cons)):
                c = _cross(a, cons[k][0])
                cands.append(c)
                cands.append([-t for t in c])
    out = []
    for d in cands:
        if max([abs(t) for t in d]) < 1e-12:
            continue
        ok = True
        for a, c in cons:
            s = 0
            for j in range(dim):
                s += a[j] * d[j]
            if s > 1e-9:
                ok = False
        if ok:
            out.append(d)
    return out

def _dot(a, b):
    s = 0
    for j in range(len(a)):
        s += a[j] * b[j]
    return s

def _pt(v):
    return '(' + ', '.join([fmt(t) for t in v]) + ')'

def _lp2(p, q, data, mx):
    cons, shown, notes = _cons(data, 4, ['x', 'y'], 10)
    nm = 'P' if mx else 'C'
    sg = 1 if mx else -1
    head = [w(('Maximise ' if mx else 'Minimise ') + nm + ' = ' + _lin([p, q], ['x', 'y']))]
    head.extend(_wwrap('subject to ', shown + ['x >= 0', 'y >= 0'], ', '))
    head.extend(notes)
    vs = _verts(cons, 2)
    if not vs:
        return [warn('the feasible region is empty')] + head
    cx = sum([v[0] for v in vs]) / len(vs)
    cy = sum([v[1] for v in vs]) / len(vs)
    vs = sorted(vs, key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
    obj = [p, q]
    rays = _rays(cons, 2)
    out = []
    for d in rays:
        if sg * _dot(obj, d) > 1e-9:
            out = [warn(nm + ' is unbounded on this region')]
            out.extend(head)
            return out
    best = None
    for v in vs:
        o = _dot(obj, v)
        if best is None or sg * o > sg * best[0] + 1e-9:
            best = (o, v)
    bo, bv = best
    out = [nm + ' = ' + fmt(bo), 'at x = ' + fmt(bv[0]) + ', y = ' + fmt(bv[1])]
    ties = [v for v in vs if abs(_dot(obj, v) - bo) < 1e-9 and v is not bv]
    for v in ties:
        out.append('also optimal at ' + _pt(v))
    if ties:
        out.append(w('every point on the edge between is optimal'))
    if rays:
        out.append(warn('the feasible region is unbounded'))
    out.append('vertices:')
    for v in vs:
        out.append(_pt(v) + ': ' + nm + ' = ' + fmt(_dot(obj, v)))
    # integer search (L5, L10)
    xs = [v[0] for v in vs]
    ys = [v[1] for v in vs]
    pad = 1
    if rays:
        pad = int(max(3, max(xs) - min(xs), max(ys) - min(ys))) + 1
    x0 = int(math.floor(min(xs))) - pad
    x1 = int(math.ceil(max(xs))) + pad
    y0 = int(math.floor(min(ys))) - pad
    y1 = int(math.ceil(max(ys))) + pad
    if (x1 - x0 + 1) * (y1 - y0 + 1) > 4000:
        out.append(warn('too many lattice points to search'))
    else:
        bi = None
        i = x0
        while i <= x1:
            j = y0
            while j <= y1:
                if _feas(cons, [i, j], 1e-9):
                    o = p * i + q * j
                    if bi is None or sg * o > sg * bi[0] + 1e-9:
                        bi = (o, i, j)
                j += 1
            i += 1
        if bi is None:
            out.append(warn('no integer point in the region'))
        else:
            out.append('integer: (' + str(bi[1]) + ', ' + str(bi[2]) + '), ' +
                       nm + ' = ' + fmt(bi[0]))
            if rays:
                out.append(w('integer search is near the vertices only'))
        if bv[0] != int(bv[0]) or bv[1] != int(bv[1]):
            out.append(w('rounding the vertex (L5):'))
            for i in sorted(set([int(math.floor(bv[0])), int(math.ceil(bv[0]))])):
                for j in sorted(set([int(math.floor(bv[1])), int(math.ceil(bv[1]))])):
                    ok = _feas(cons, [i, j], 1e-9)
                    out.append(w('  (' + str(i) + ', ' + str(j) + ') ' +
                                 (nm + ' = ' + fmt(p * i + q * j) if ok else 'not feasible')))
    out.extend(head)
    return out

def t_lp2max(p, q, data):
    return _lp2(p, q, data, True)

def t_lp2min(p, q, data):
    return _lp2(p, q, data, False)

def t_lp3(p, q, r, data):
    cons, shown, notes = _cons(data, 5, ['x', 'y', 'z'], 8)
    obj = [p, q, r]
    vs = _verts(cons, 3)
    head = [w('P = ' + _lin(obj, ['x', 'y', 'z']))]
    head.extend(_wwrap('subject to ', shown + ['x, y, z >= 0'], ', '))
    head.extend(notes)
    if not vs:
        return [warn('the feasible region is empty')] + head
    rays = _rays(cons, 3)
    up = False
    down = False
    for d in rays:
        g = _dot(obj, d)
        if g > 1e-9:
            up = True
        if g < -1e-9:
            down = True
    hi = None
    lo = None
    for v in vs:
        o = _dot(obj, v)
        if hi is None or o > hi[0] + 1e-9:
            hi = (o, v)
        if lo is None or o < lo[0] - 1e-9:
            lo = (o, v)
    out = []
    if up:
        out.append(warn('max: P is unbounded'))
    else:
        out.append('max P = ' + fmt(hi[0]))
        out.append('  at ' + _pt(hi[1]))
    if down:
        out.append(warn('min: P is unbounded'))
    else:
        out.append('min P = ' + fmt(lo[0]))
        out.append('  at ' + _pt(lo[1]))
    if rays:
        out.append(warn('the feasible region is unbounded'))
    out.append(str(len(vs)) + ' vertices:')
    for v in vs:
        out.append(_pt(v) + ' P=' + fmt(_dot(obj, v)))
    out.append(w('vertex = three planes meeting inside the region'))
    out.extend(head)
    return out

# =============================================================================
# S  Simplex
# L3 standard form, L4 slack form, L9 post-optimal (shadow prices, ranging),
# L12 simplex, L13 vertex path, L14 two-stage and big-M, L15 = split into
# two inequalities, L16 variables that may be negative.
# =============================================================================

def _vnames(n, upper=False):
    if n <= 4:
        v = ['x', 'y', 'z', 'w'][:n]
    else:
        v = ['x' + str(j + 1) for j in range(n)]
    return [s.upper() for s in v] if upper else v

def _read_lp(n, data, k):
    # data = n objective coefficients then rows of n + k values
    n = _whole(n, 'n', 1, 6)
    rl = n + k
    if len(data) < n + rl or (len(data) - n) % rl:
        raise ValueError('need ' + str(n) + ' objective values, then rows of ' + str(rl))
    rows = _groups(data[n:], rl, 'rows')
    if len(rows) > 8:
        raise ValueError('at most 8 constraints')
    return n, list(data[:n]), rows

def _pad(s, k):
    return ' ' * (k - len(s)) + s

def _mfmt(mc, c):
    if abs(mc) < EPS:
        return fmt(c)
    ms = 'M' if abs(mc - 1) < EPS else ('-M' if abs(mc + 1) < EPS else fmt(mc) + 'M')
    if abs(c) < EPS:
        return ms
    return fmt(c) + ('+' if mc > 0 else '') + ms

def _tabshow(lines, names, labels, basis, tab, nobj, bigm=False):
    cells = [[''] + names + ['RHS']]
    if bigm:
        cells.append([labels[1]] + [_mfmt(tab[0][j], tab[1][j]) for j in range(len(tab[0]))])
    else:
        for i in range(nobj):
            cells.append([labels[i]] + [fmt(x) for x in tab[i]])
    for i in range(nobj, len(tab)):
        cells.append([names[basis[i - nobj]]] + [fmt(x) for x in tab[i]])
    wd = [0] * len(cells[0])
    for r in cells:
        for j in range(len(r)):
            if len(r[j]) > wd[j]:
                wd[j] = len(r[j])
    for r in cells:
        lines.append(w(' '.join([_pad(r[j], wd[j]) for j in range(len(r))])))

def _pivot(tab, r, c):
    p = tab[r][c]
    tab[r] = [x / p for x in tab[r]]
    tab[r][c] = 1.0
    for i in range(len(tab)):
        if i != r:
            f = tab[i][c]
            if f != 0:
                tab[i] = [_tidy(tab[i][j] - f * tab[r][j]) for j in range(len(tab[r]))]
                tab[i][c] = 0.0

def _tidy(x):
    return 0.0 if abs(x) < 1e-11 else x

def _neg(tab, j, lexi):
    if lexi:
        if tab[0][j] < -EPS:
            return True
        return abs(tab[0][j]) <= EPS and tab[1][j] < -EPS
    return tab[0][j] < -EPS

def _better(tab, j, c, lexi):
    if c < 0:
        return True
    if lexi:
        if tab[0][j] < tab[0][c] - EPS:
            return True
        return abs(tab[0][j] - tab[0][c]) <= EPS and tab[1][j] < tab[1][c] - EPS
    return tab[0][j] < tab[0][c] - EPS

def _values(tab, nobj, basis):
    val = [0.0] * (len(tab[0]) - 1)
    for i in range(len(basis)):
        val[basis[i]] = tab[nobj + i][-1]
    return val

def _run(tab, nobj, basis, allowed, names, labels, lines, tag, lexi, path, nv, prow):
    it = 0
    while it < 60:
        c = -1
        for j in range(len(tab[0]) - 1):
            if allowed[j] and _neg(tab, j, lexi) and _better(tab, j, c, lexi):
                c = j
        if c < 0:
            return 'optimal'
        r = -1
        best = 0
        for i in range(nobj, len(tab)):
            if tab[i][c] > EPS:
                q = tab[i][-1] / tab[i][c]
                if r < 0 or q < best - 1e-12:
                    best = q
                    r = i
        if r < 0:
            lines.append(w(tag + names[c] + ' column has no positive entry'))
            return 'unbounded'
        it += 1
        lines.append(w(tag + 'pivot ' + str(it) + ': ' + names[c] + ' enters, ' +
                       names[basis[r - nobj]] + ' leaves'))
        lines.append(w('  ratio ' + fmt(best) + ', pivot ' + fmt(tab[r][c])))
        _pivot(tab, r, c)
        basis[r - nobj] = c
        _tabshow(lines, names, labels, basis, tab, nobj, lexi)
        if path is not None:
            path.append((_values(tab, nobj, basis), tab[prow][-1]))
    raise ValueError('no optimum after 60 pivots (cycling?)')

def _report(tab, nobj, basis, names, nv, nm, val_obj, extra_cols):
    val = _values(tab, nobj, basis)
    out = [nm + ' = ' + fmt(val_obj)]
    for j in range(nv):
        out.append(names[j] + ' = ' + fmt(val[j]))
    others = [names[j] + ' = ' + fmt(val[j]) for j in range(nv, nv + extra_cols)]
    out.extend(_wrap('', others, 34, ', '))
    bas = [names[b] for b in sorted(basis)]
    non = [names[j] for j in range(nv + extra_cols) if j not in basis]
    out.extend(_wwrap('basic: ', bas, ', '))
    out.extend(_wwrap('non-basic (= 0): ', non if non else ['none'], ', '))
    return out

def _pathlines(path, nm, sign, nv, a0=None):
    out = ['vertex path (L13):']
    bad = False
    for k in range(len(path)):
        v, o = path[k]
        tail = ''
        if a0 is not None and max([0] + v[a0:]) > EPS:
            tail = ' *'
            bad = True
        out.extend(_wrap(('start ' if k == 0 else str(k) + ': '),
                         [_pt(v[:nv]), nm + ' = ' + fmt(sign * o) + tail]))
    if bad:
        out.append(w('* artificial > 0: not a feasible vertex'))
    return out

def _simplex_core(n, data):
    n, obj, rows = _read_lp(n, data, 1)
    m = len(rows)
    V = _vnames(n)
    S = ['s' + str(i + 1) for i in range(m)]
    for i in range(m):
        if rows[i][n] < 0:
            raise ValueError('row ' + str(i + 1) + ' has b < 0: use Two-stage')
    names = V + S
    tab = [[-c for c in obj] + [0.0] * m + [0.0]]
    for i in range(m):
        r = list(rows[i][:n]) + [0.0] * m + [rows[i][n]]
        r[n + i] = 1.0
        tab.append(r)
    basis = [n + i for i in range(m)]
    lines = [w('standard form (L3): maximise P = ' + _lin(obj, V))]
    for i in range(m):
        lines.append(w('  ' + _lin(rows[i][:n], V) + ' <= ' + fmt(rows[i][n])))
    lines.append(w('  ' + ', '.join(V) + ' >= 0'))
    lines.append(w('slack form (L4):'))
    for i in range(m):
        lines.append(w('  ' + _lin(list(rows[i][:n]) + [1], V + [S[i]]) + ' = ' +
                       fmt(rows[i][n])))
    neg = _lin([-c for c in obj], V)
    lines.append(w('  objective row: P ' + ('- ' + neg[1:] if neg[0] == '-' else
                                           '+ ' + neg) + ' = 0'))
    lines.append(w('initial tableau:'))
    _tabshow(lines, names, ['P'], basis, tab, 1)
    path = [([0] * (n + m), 0)]
    st = _run(tab, 1, basis, [True] * (n + m), names, ['P'], lines, '', False, path, n, 0)
    return st, n, m, obj, rows, V, S, names, tab, basis, lines, path

def t_simplex(n, data):
    st, n, m, obj, rows, V, S, names, tab, basis, lines, path = _simplex_core(n, data)
    if st == 'unbounded':
        return [warn('P is unbounded')] + lines
    out = _report(tab, 1, basis, names, n, 'P', tab[0][-1], m)
    out.append('shadow prices:')
    out.extend(_wrap('', [S[i] + ': ' + fmt(tab[0][n + i]) for i in range(m)], 34, ', '))
    out.extend(_pathlines(path, 'P', 1, n))
    out.extend(lines)
    out.append(w('enter: most negative in the P row'))
    out.append(w('leave: least ratio RHS / column (positive only)'))
    out.append(w('shadow price = rise in P per unit rise in b'))
    return out

def _inf(v, neg):
    if v is None:
        return '-inf' if neg else 'inf'
    return fmt(v)

def t_sens(n, data):
    st, n, m, obj, rows, V, S, names, tab, basis, lines, path = _simplex_core(n, data)
    if st == 'unbounded':
        return [warn('P is unbounded')]
    val = _values(tab, 1, basis)
    out = ['P = ' + fmt(tab[0][-1]) + ' at ' + _pt(val[:n])]
    out.append('objective ranges (same vertex):')
    for j in range(n):
        lo = None
        hi = None
        if j in basis:
            r = 1 + basis.index(j)
            for k in range(n + m):
                if k in basis:
                    continue
                a = tab[r][k]
                rc = tab[0][k]
                if a > EPS:
                    d = -rc / a
                    if lo is None or d > lo:
                        lo = d
                elif a < -EPS:
                    d = rc / -a
                    if hi is None or d < hi:
                        hi = d
        else:
            hi = tab[0][j]
        clo = None if lo is None else obj[j] + lo
        chi = None if hi is None else obj[j] + hi
        out.append(_inf(clo, True) + ' <= c(' + V[j] + ') <= ' + _inf(chi, False))
    out.append('RHS ranges (same basis):')
    for i in range(m):
        col = n + i
        lo = None
        hi = None
        for r in range(1, m + 1):
            a = tab[r][col]
            if a > EPS:
                d = -tab[r][-1] / a
                if lo is None or d > lo:
                    lo = d
            elif a < -EPS:
                d = tab[r][-1] / -a
                if hi is None or d < hi:
                    hi = d
        b = rows[i][n]
        blo = None if lo is None else b + lo
        bhi = None if hi is None else b + hi
        if blo is not None and blo < 0:
            blo = 0
        out.append(_inf(blo, True) + ' <= b' + str(i + 1) + ' <= ' + _inf(bhi, False))
        out.append(w('  row ' + str(i + 1) + ': P changes by ' + fmt(tab[0][col]) +
                     ' per unit of b' + str(i + 1)))
    out.append(w('outside a range the optimal vertex changes:'))
    out.append(w('re-run the simplex with the new values'))
    out.append(w('c(x) range: x stays basic / non-basic'))
    return out

def _prep(A, rels, b, names, lines, split):
    rows = []
    for i in range(len(A)):
        a = list(A[i])
        r = rels[i]
        c = b[i]
        if c < 0:
            a = [-x for x in a]
            c = -c
            r = -r
            lines.append(w('row ' + str(i + 1) + ' x -1 so the RHS is >= 0'))
        if r == 0 and split:
            lines.append(w('L15: row ' + str(i + 1) + ' = split into <= and >='))
            rows.append((a, 1, c))
            rows.append((a, -1, c))
        else:
            rows.append((a, r, c))
    return rows

def _build(n, obj, rows, V, sign):
    # columns: V, slack/surplus per row, artificials; last = RHS
    extra = []
    arts = []
    for k in range(len(rows)):
        r = rows[k][1]
        if r == 1:
            extra.append(('s' + str(k + 1), k, 1.0))
        elif r == -1:
            extra.append(('u' + str(k + 1), k, -1.0))
        if r <= 0:
            arts.append(('a' + str(k + 1), k))
    names = V + [e[0] for e in extra] + [a[0] for a in arts]
    ncol = len(names) + 1
    cons = []
    basis = []
    for k in range(len(rows)):
        a, r, c = rows[k]
        row = list(a) + [0.0] * (ncol - n)
        row[-1] = c
        cons.append(row)
        basis.append(-1)
    for j in range(len(extra)):
        nm, k, s = extra[j]
        cons[k][n + j] = s
        if s > 0:
            basis[k] = n + j
    a0 = n + len(extra)
    arow = [0.0] * ncol
    for j in range(len(arts)):
        nm, k = arts[j]
        cons[k][a0 + j] = 1.0
        basis[k] = a0 + j
        arow = [arow[t] - cons[k][t] for t in range(ncol)]
        arow[a0 + j] = 0.0
    prow = [-sign * c for c in obj] + [0.0] * (ncol - n)
    return names, cons, basis, arow, prow, a0, len(extra), len(arts)

def _lp_setup(n, data):
    n, obj, rws = _read_lp(n, data, 2)
    V = _vnames(n)
    A = [r[:n] for r in rws]
    rels = [_rel(r[n]) for r in rws]
    b = [r[n + 1] for r in rws]
    return n, obj, A, rels, b, V

def _statement(obj, A, rels, b, V, mx, nm):
    lines = [w(('Maximise ' if mx else 'Minimise ') + nm + ' = ' + _lin(obj, V))]
    for i in range(len(A)):
        lines.append(w('  ' + _lin(A[i], V) + ' ' + RELS[rels[i]] + ' ' + fmt(b[i])))
    lines.append(w('  ' + ', '.join(V) + ' >= 0'))
    if not mx:
        lines.append(w('minimise ' + nm + ': maximise P = -' + nm))
    return lines

def _two_stage(n, obj, A, rels, b, V, mx, lines):
    sign = 1 if mx else -1
    rows = _prep(A, rels, b, V, lines, True)
    names, cons, basis, arow, prow, a0, ne, na = _build(n, obj, rows, V, sign)
    path = []
    if na:
        tab = [arow, prow] + cons
        lines.append(w('stage 1: minimise A = ' + ' + '.join(names[a0:])))
        lines.append(w('A row holds -A; P row carried along'))
        _tabshow(lines, names, ['A', 'P'], basis, tab, 2)
        allowed = [True] * len(names)
        _run(tab, 2, basis, allowed, names, ['A', 'P'], lines, 'S1 ', False, None, n, 1)
        if tab[0][-1] < -1e-7:
            return 'infeasible', names, tab, basis, ne, na, path
        for i in range(len(basis)):
            if basis[i] >= a0:
                for j in range(a0):
                    if abs(tab[2 + i][j]) > EPS:
                        lines.append(w(names[basis[i]] + ' = 0 but basic: pivot on ' +
                                       names[j] + ' in its row'))
                        _pivot(tab, 2 + i, j)
                        basis[i] = j
                        break
        tab = tab[1:]
        keep = True
        for bc in basis:
            if bc >= a0:
                keep = False
        if keep:
            tab = [r[:a0] + [r[-1]] for r in tab]
            names = names[:a0]
            na = 0
        lines.append(w('stage 1 done: A = 0, drop A and the artificials'))
    else:
        tab = [prow] + cons
    allowed = [j < a0 for j in range(len(names))]
    lines.append(w('stage 2 tableau:'))
    _tabshow(lines, names, ['P'], basis, tab, 1)
    path.append((_values(tab, 1, basis), tab[0][-1]))
    st = _run(tab, 1, basis, allowed, names, ['P'], lines, 'S2 ', False, path, n, 0)
    return st, names, tab, basis, ne, na, path

def _ts_tool(n, data, mx):
    n, obj, A, rels, b, V = _lp_setup(n, data)
    nm = 'P' if mx else 'C'
    lines = _statement(obj, A, rels, b, V, mx, nm)
    st, names, tab, basis, ne, na, path = _two_stage(n, obj, A, rels, b, V, mx, lines)
    if st == 'infeasible':
        return [warn('infeasible: stage 1 ends with A > 0')] + lines
    if st == 'unbounded':
        return [warn(nm + ' is unbounded')] + lines
    sign = 1 if mx else -1
    out = _report(tab, 1, basis, names, n, nm, sign * tab[0][-1], ne + na)
    out.extend(_pathlines(path, nm, sign, n))
    out.extend(lines)
    return out

def t_twostage_max(n, data):
    return _ts_tool(n, data, True)

def t_twostage_min(n, data):
    return _ts_tool(n, data, False)

def _bigm_tool(n, data, mx):
    n, obj, A, rels, b, V = _lp_setup(n, data)
    nm = 'P' if mx else 'C'
    sign = 1 if mx else -1
    lines = _statement(obj, A, rels, b, V, mx, nm)
    rows = _prep(A, rels, b, V, lines, False)
    names, cons, basis, arow, prow, a0, ne, na = _build(n, obj, rows, V, sign)
    if na:
        lines.append(w('maximise P = ' + _lin([sign * c for c in obj], V) + ' - M(' +
                       ' + '.join(names[a0:]) + ')'))
    tab = [arow, prow] + cons
    _tabshow(lines, names, ['M', 'P'], basis, tab, 2, True)
    path = [(_values(tab, 2, basis), tab[1][-1])]
    st = _run(tab, 2, basis, [True] * len(names), names, ['M', 'P'], lines, '', True,
              path, n, 1)
    val = _values(tab, 2, basis)
    for j in range(a0, len(names)):
        if val[j] > 1e-7:
            return [warn('infeasible: ' + names[j] + ' stays > 0')] + lines
    if st == 'unbounded':
        return [warn(nm + ' is unbounded')] + lines
    out = _report(tab, 2, basis, names, n, nm, sign * tab[1][-1], ne + na)
    out.extend(_pathlines(path, nm, sign, n, a0))
    out.extend(lines)
    out.append(w('M is a large number: compare M parts first'))
    out.append(w('= rows get an artificial only (no split)'))
    return out

def t_bigm_max(n, data):
    return _bigm_tool(n, data, True)

def t_bigm_min(n, data):
    return _bigm_tool(n, data, False)

def t_negvars(n, data):
    n = _whole(n, 'n', 1, 6)
    if len(data) < n:
        raise ValueError('need ' + str(n) + ' lower bounds first')
    low = list(data[:n])
    n, obj, A, rels, b, V = _lp_setup(n, data[n:])
    U = _vnames(n, True)
    b2 = []
    for i in range(len(A)):
        b2.append(b[i] - _dot(A[i], low))
    k = _dot(obj, low)
    lines = []
    for j in range(n):
        if low[j] != 0:
            lines.append(w(V[j] + ' >= ' + fmt(low[j]) + ': ' + V[j] + ' = ' + U[j] +
                           (' - ' + fmt(-low[j]) if low[j] < 0 else ' + ' + fmt(low[j])) +
                           ', ' + U[j] + ' >= 0'))
        else:
            lines.append(w(V[j] + ' >= 0: ' + U[j] + ' = ' + V[j]))
    lines.append(w('Maximise P = ' + _lin(obj, U) + (' + ' + fmt(k) if k >= 0 else
                                                     ' - ' + fmt(-k))))
    for i in range(len(A)):
        lines.append(w('  ' + _lin(A[i], U) + ' ' + RELS[rels[i]] + ' ' + fmt(b2[i])))
    lines.append(w('  ' + ', '.join(U) + ' >= 0'))
    st, names, tab, basis, ne, na, path = _two_stage(n, obj, A, rels, b2, U, True, lines)
    if st == 'infeasible':
        return [warn('infeasible')] + lines
    if st == 'unbounded':
        return [warn('P is unbounded')] + lines
    val = _values(tab, 1, basis)
    out = ['P = ' + fmt(tab[0][-1] + k)]
    for j in range(n):
        out.append(V[j] + ' = ' + fmt(val[j] + low[j]) + '  (' + U[j] + ' = ' +
                   fmt(val[j]) + ')')
    out.extend(lines)
    out.append(w('P = tableau value + ' + fmt(k) if k >= 0 else
                 'P = tableau value - ' + fmt(-k)))
    out.append(w('no lower bound known: x = x1 - x2, both >= 0'))
    return out

# =============================================================================

SECTIONS = [
    ('A', 'Sorting and packing', [
        ('Bubble sort', 'data*', t_bubble),
        ('Shuttle sort', 'data*', t_shuttle),
        ('Quick sort', 'data*', t_quick),
        ('First fit', 'C,sizes*', t_firstfit),
        ('First fit decreasing', 'C,sizes*', t_ffd),
        ('Order n^k scaling', 'k,n1,t1,n2', t_order),
        ('Order n log n scaling', 'n1,t1,n2', t_order_nlogn),
    ]),
    ('G', 'Graphs', [
        ('Graph from edges', 'n,from to*', t_graph),
        ('Digraph from arcs', 'n,from to*', t_digraph),
        ('Graph from adjacency', 'n,rows*', t_adjacency),
    ]),
    ('N', 'Networks', [
        ('Dijkstra', 'start,end or 0,from to w*', t_dijkstra),
        ('Dijkstra directed', 'start,end or 0,from to w*', t_dijkstra_d),
        ('Prim', 'start,from to w*', t_prim),
        ('Prim from matrix', 'n,start,rows*', t_prim_matrix),
        ('Kruskal', 'from to w*', t_kruskal),
        ('Shortest path as LP', 'start,end,from to w*', t_splp),
    ]),
    ('F', 'Network flows', [
        ('Max flow min cut', 'source,sink,from to cap*', t_maxflow),
        ('Cut capacity', 'source,sink,S digits,from to cap*', t_cut),
        ('Max flow as LP', 'source,sink,from to cap*', t_flowlp),
    ]),
    ('C', 'Critical path', [
        ('Activity on arc', 'from to dur*', t_cpa),
        ('Precedence table', 'dur k preds*', t_cpa_table),
        ('Resource histogram', 'from to dur res*', t_resource),
        ('Schedule k workers', 'k,from to dur*', t_schedule),
    ]),
    ('L', 'LP graphical', [
        ('LP 2-D maximise', 'p,q,a b rel c*', t_lp2max),
        ('LP 2-D minimise', 'p,q,a b rel c*', t_lp2min),
        ('LP 3-D vertices', 'p,q,r,a b c rel d*', t_lp3),
    ]),
    ('S', 'Simplex', [
        ('Simplex max <=', 'n,obj rows a b*', t_simplex),
        ('Sensitivity ranging', 'n,obj rows a b*', t_sens),
        ('Two-stage maximise', 'n,obj rows a rel b*', t_twostage_max),
        ('Two-stage minimise', 'n,obj rows a rel b*', t_twostage_min),
        ('Big-M maximise', 'n,obj rows a rel b*', t_bigm_max),
        ('Big-M minimise', 'n,obj rows a rel b*', t_bigm_min),
        ('Negative variables', 'n,lows obj rows a rel b*', t_negvars),
    ]),
]
