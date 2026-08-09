def test_quicksort(h):
    import algos
    out = h.drive(algos.quicksort, ["5 3 8 1 9 2 7"])
    h.has("quicksort pass 1", out, "Pass 1: 3 1 2 [5] 8 9 7")
    h.has("quicksort pass 2", out, "Pass 2: 1 2 [3] [5] [7] [8] [9]")
    h.has("quicksort pass 3", out, "Pass 3: [1] [2] [3] [5] [7] [8] [9]")
    h.has("quicksort sorted", out, "Sorted: 1 2 3 5 7 8 9")
    h.has("quicksort passes", out, "Passes: 3")
    h.has("quicksort comparisons", out, "Comparisons: 11")

    out = h.drive(algos.quicksort, ["1 2 3 4"])
    h.has("quicksort sorted input", out, "Sorted: 1 2 3 4")
    h.has("quicksort worst case comps", out, "Comparisons: 6")
    h.has("quicksort worst case passes", out, "Passes: 3")

    out = h.drive(algos.quicksort, ["4 3 2 1"])
    h.has("quicksort reversed pass 1", out, "Pass 1: 3 2 1 [4]")
    h.has("quicksort reversed", out, "Sorted: 1 2 3 4")
    h.has("quicksort reversed comps", out, "Comparisons: 6")

    out = h.drive(algos.quicksort, ["7"])
    h.has("quicksort singleton", out, "Sorted: 7")
    h.has("quicksort singleton comps", out, "Comparisons: 0")

    out = h.drive(algos.quicksort, [None])
    h.check("quicksort cancel", out, [])


def test_sort_counts(h):
    import algos
    out = h.drive(algos.bubble, ["3 1 2"])
    h.has("bubble comparisons", out, "Comparisons: 3")
    h.has("bubble swaps", out, "Swaps: 2")
    h.has("bubble worst case", out, "n(n-1)/2 = 3")

    out = h.drive(algos.insertion, ["3 1 2"])
    h.has("insertion comparisons", out, "Comparisons: 3")
    h.has("insertion shifts", out, "Shifts: 2")

    out = h.drive(algos.firstfit, ["4 5 3", "10"])
    h.has("firstfit bins", out, "Bins used: 2")
    h.has("firstfit comparisons", out, "Comparisons: 2")
    h.has("firstfit lower bound", out, "Lower bound: 2 bins")

    out = h.drive(algos.firstfitdec, ["4 5 3", "10"])
    h.has("ffd order", out, "Bin 1: 5 4")
    h.has("ffd comparisons", out, "Comparisons: 2")


def test_graphinfo(h):
    import algos
    out = h.drive(algos.graphinfo, ["3", "0 1 1", "1 0 1", "1 1 0"])
    h.has("K3 order", out, "Order (nodes): 3")
    h.has("K3 size", out, "Size (edges): 3")
    h.has("K3 undirected", out, "Type: undirected")
    h.has("K3 degree", out, "deg(2) = 2")
    h.has("K3 handshake", out, "Sum of degrees = 6 = 2 x 3")
    h.has("K3 odd nodes", out, "Odd nodes: 0")
    h.has("K3 connected", out, "Connected: yes")
    h.has("K3 incidence row 1", out, "1: 1 1 0")
    h.has("K3 incidence row 3", out, "0 1 1")

    out = h.drive(algos.graphinfo, ["3", "0 1 0", "0 0 1", "0 0 0"])
    h.has("digraph size", out, "Size (arcs): 2")
    h.has("digraph directed", out, "Type: directed")
    h.has("digraph node 1", out, "node 1: out 1  in 0")
    h.has("digraph node 3", out, "node 3: out 0  in 1")
    h.has("digraph incidence", out, "2: 1 -1")

    out = h.drive(algos.graphinfo,
                  ["4", "0 1 0 0", "1 0 0 0", "0 0 0 1", "0 0 1 0"])
    h.has("disconnected", out, "Connected: no")
    h.has("disconnected odd", out, "Odd nodes: 4")


def test_dijkstra_route(h):
    import algos
    out = h.drive(algos.dijkstra,
                  ["3", "0 1 4", "1 0 2", "4 2 0", "1", "3"])
    h.has("dij label order 1", out, "1: node 1 perm 0")
    h.has("dij label order 2", out, "2: node 2 perm 1")
    h.has("dij label order 3", out, "3: node 3 perm 3")
    h.has("dij working values", out, "node 3: 4, 3")
    h.has("dij final n3", out, "Node 3: 3")
    h.has("dij route", out, "Route 1 to 3: 1 - 2 - 3")
    h.has("dij route length", out, "Route length: 3")
    h.has("dij order", out, "O(n^2)")

    out = h.drive(algos.dijkstra, ["3", "0 1 4", "1 0 2", "4 2 0", "1", "0"])
    h.has("dij no route distances", out, "Node 3: 3")
    for ln in out:
        h.truthy("dij no route line", "Route 1 to" not in ln)

    g = ["5",
         "0 4 2 0 0",
         "4 0 1 5 0",
         "2 1 0 8 10",
         "0 5 8 0 2",
         "0 0 10 2 0",
         "1", "5"]
    out = h.drive(algos.dijkstra, g)
    h.has("dij5 perm 2nd", out, "2: node 3 perm 2")
    h.has("dij5 perm 3rd", out, "3: node 2 perm 3")
    h.has("dij5 perm 5th", out, "5: node 5 perm 10")
    h.has("dij5 working 2", out, "node 2: 4, 3")
    h.has("dij5 working 5", out, "node 5: 12, 10")
    h.has("dij5 route", out, "Route 1 to 5: 1 - 3 - 2 - 4 - 5")
    h.has("dij5 length", out, "Route length: 10")

    out = h.drive(algos.dijkstra, ["3", "0 1 0", "1 0 0", "0 0 0", "1", "3"])
    h.has("dij unreachable", out, "Node 3: unreachable")
    h.has("dij no path", out, "Route 1 to 3: none")


FLOWNET = ["4", "0 3 2 0", "0 0 1 2", "0 0 0 3", "0 0 0 0"]


def test_maxflow(h):
    import algos
    out = h.drive(algos.maxflow, FLOWNET + ["1", "4"])
    h.has("flow path 1", out, "Path 1: 1 - 2 - 4  flow 2")
    h.has("flow path 2", out, "Path 2: 1 - 3 - 4  flow 2")
    h.has("flow path 3", out, "Path 3: 1 - 2 - 3 - 4  flow 1")
    h.has("max flow value", out, "Maximum flow = 5")
    h.has("flow arc 1-2 saturated", out, "1-2: 3 / 3 (saturated)")
    h.has("flow arc 3-4 saturated", out, "3-4: 3 / 3 (saturated)")
    h.has("min cut S", out, "S = {1}")
    h.has("min cut T", out, "T = {2, 3, 4}")
    h.has("min cut arcs", out, "cut arcs: 1-2 (3) 1-3 (2)")
    h.has("min cut capacity", out, "Cut capacity = 5")
    h.has("max flow min cut", out, "Max flow = min cut = 5")
    h.num("max flow number", out, "Maximum flow = ", 5.0)

    NET2 = ["5",
            "0 6 4 0 0",
            "0 0 0 3 2",
            "0 0 0 5 0",
            "0 0 0 0 7",
            "0 0 0 0 0"]
    out = h.drive(algos.maxflow, NET2 + ["1", "5"])
    h.has("net2 max flow", out, "Maximum flow = 9")
    h.has("net2 cut S", out, "S = {1, 2}")
    h.has("net2 cut T", out, "T = {3, 4, 5}")
    h.has("net2 cut arcs", out, "cut arcs: 1-3 (4) 2-4 (3) 2-5 (2)")
    h.has("net2 cut capacity", out, "Cut capacity = 9")
    h.has("net2 arc 4-5", out, "4-5: 7 / 7 (saturated)")
    h.has("net2 arc 1-2 unsaturated", out, "1-2: 5 / 6")
    h.has("net2 equality", out, "Max flow = min cut = 9")

    out = h.drive(algos.cutcap, NET2 + ["1", "5", "1 2 3 4"])
    h.has("net2 other cut capacity", out, "Cut capacity = 9")
    h.has("net2 other cut is minimal", out, "This IS a minimum cut")

    out = h.drive(algos.maxflow, ["3", "0 0 0", "0 0 5", "0 0 0", "1", "3"])
    h.has("no path max flow", out, "Maximum flow = 0")
    h.has("no path cut", out, "cut arcs: none")

    out = h.drive(algos.maxflow, FLOWNET + ["1", "1"])
    h.check("maxflow rejects s = t", out, [])


def test_cutcap(h):
    import algos
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 3"])
    h.has("cut S set", out, "S = {1, 3}")
    h.has("cut T set", out, "T = {2, 4}")
    h.has("cut arc 1-2", out, "1-2: 3")
    h.has("cut arc 3-4", out, "3-4: 3")
    h.has("cut capacity 6", out, "Cut capacity = 6")
    h.has("cut backward arcs", out, "arcs T to S total 1, not counted")
    h.has("cut vs max flow", out, "Maximum flow = 5")
    h.has("cut not minimum", out, "Not minimum: capacity exceeds max flow by 1")

    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1"])
    h.has("min cut capacity", out, "Cut capacity = 5")
    h.has("min cut recognised", out, "This IS a minimum cut")

    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 2"])
    h.has("second min cut", out, "Cut capacity = 5")
    h.has("second min cut recognised", out, "This IS a minimum cut")

    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "2 3"])
    h.has("cut needs source", out, "source must be on the source side")
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 4"])
    h.has("cut needs sink outside", out, "sink must be on the sink side")


def test_simplex(h):
    import algos
    out = h.drive(algos.simplex, ["2", "2", "5 4", "6 4 24", "1 2 6"])
    h.has("simplex standard form", out, "Maximise P = 5x + 4y")
    h.has("simplex slack form", out, "6x + 4y + s1 = 24")
    h.has("simplex objective row", out, "Objective row: P - 5x - 4y = 0")
    h.has("simplex pivot 1", out, "Pivot 1: column x, row s1, ratio 4")
    h.has("simplex pivot 2", out, "Pivot 2: column y, row s2, ratio 1.5")
    h.has("simplex enters/leaves", out, "y enters, s2 leaves")
    h.has("simplex optimal", out, "Optimal tableau reached.")
    h.has("simplex P", out, "P = 21")
    h.num("simplex x", out, "x = ", 3.0)
    h.num("simplex y", out, "y = ", 1.5)
    h.has("simplex s1", out, "s1 = 0")
    h.has("simplex s2", out, "s2 = 0")
    h.has("simplex basic", out, "Basic variables: x, y")
    h.has("simplex non-basic", out, "Non-basic (= 0): s1, s2")
    h.num("simplex shadow price C1", out, "C1 (s1): ", 0.75)
    h.num("simplex shadow price C2", out, "C2 (s2): ", 0.5)

    out = h.drive(algos.simplex,
                  ["2", "3", "4 3", "2 1 10", "1 3 15", "1 0 4"])
    h.has("simplex B pivot 1", out, "Pivot 1: column x, row s3, ratio 4")
    h.has("simplex B pivot 3", out, "Pivot 3: column s3, row s2, ratio 1")
    h.has("simplex B P", out, "P = 24")
    h.num("simplex B x", out, "x = ", 3.0)
    h.num("simplex B y", out, "y = ", 4.0)
    h.has("simplex B slack s3", out, "s3 = 1")
    h.has("simplex B basic", out, "Basic variables: x, y, s3")
    h.has("simplex B non-basic", out, "Non-basic (= 0): s1, s2")

    out = h.drive(algos.simplex, ["3", "2", "3 2 4", "1 1 2 4", "2 0 3 5"])
    h.has("simplex 3-var P", out, "P = 10.5")
    h.num("simplex 3-var x", out, "x = ", 2.5)
    h.num("simplex 3-var y", out, "y = ", 1.5)
    h.has("simplex 3-var z", out, "z = 0")
    h.has("simplex 3-var basic", out, "Basic variables: x, y")
    h.has("simplex 3-var non-basic", out, "Non-basic (= 0): z, s1, s2")
    h.num("simplex 3-var shadow C1", out, "C1 (s1): ", 2.0)
    h.num("simplex 3-var shadow C2", out, "C2 (s2): ", 0.5)

    out = h.drive(algos.simplex, ["2", "1", "1 1", "1 -1 1"])
    h.has("simplex unbounded", out, "P is UNBOUNDED")

    out = h.drive(algos.simplex, ["2", "1", "1 1", "1 1 -3"])
    h.has("simplex needs b >= 0", out, "Standard form needs every b >= 0.")

    out = h.drive(algos.simplex, [None])
    h.check("simplex cancel", out, [])


def test_simplex2(h):
    import algos
    out = h.drive(algos.simplex2,
                  ["2", "2", "0", "2 3", "1 1 -1 4", "1 3 -1 6"])
    h.has("simplex2 statement", out, "Minimise C = 2x + 3y")
    h.has("simplex2 constraint", out, "x + 3y >= 6")
    h.has("simplex2 phase 1", out, "Phase 1: minimise a1 + a2")
    h.has("simplex2 phase 1 done", out, "Phase 1 done: all artificials are zero.")
    h.has("simplex2 phase 2", out, "Phase 2 tableau:")
    h.has("simplex2 C", out, "C = 9")
    h.num("simplex2 x", out, "x = ", 3.0)
    h.num("simplex2 y", out, "y = ", 1.0)
    h.has("simplex2 surplus", out, "u1 = 0")
    h.has("simplex2 artificial", out, "a1 = 0")
    h.has("simplex2 basic", out, "Basic variables: x, y")

    out = h.drive(algos.simplex2,
                  ["2", "2", "1", "5 4", "6 4 1 24", "1 2 1 6"])
    h.has("simplex2 max P", out, "P = 21")
    h.num("simplex2 max x", out, "x = ", 3.0)
    h.num("simplex2 max y", out, "y = ", 1.5)
    for ln in out:
        h.truthy("simplex2 skips phase 1 when unneeded", "Phase 1" not in ln)

    out = h.drive(algos.simplex2,
                  ["2", "2", "1", "1 2", "1 1 0 4", "1 0 1 3"])
    h.has("simplex2 equality P", out, "P = 8")
    h.num("simplex2 equality x", out, "x = ", 0.0)
    h.num("simplex2 equality y", out, "y = ", 4.0)

    out = h.drive(algos.simplex2,
                  ["2", "2", "0", "1 1", "1 1 1 2", "1 1 -1 5"])
    h.has("simplex2 infeasible", out, "the constraints are INFEASIBLE.")

    out = h.drive(algos.simplex2, ["2", "1", "1", "3 2", "-1 -1 -1 -4"])
    h.has("simplex2 flipped row", out, "x + y <= 4")
    h.has("simplex2 flipped P", out, "P = 12")

    out = h.drive(algos.simplex2, ["2", "1", "1", "3 2", "1 1 7 4"])
    h.has("simplex2 bad relation", out, "rel must be 1 (<=), 0 (=) or -1 (>=).")


def test_lpgraph(h):
    import algos
    out = h.drive(algos.lpgraph, ["1", "5 4", "2", "6 4 24", "1 2 6", "0"])
    h.has("lp statement", out, "Maximise P = 5x + 4y")
    h.has("lp constraint listed", out, "6x + 4y <= 24")
    h.has("lp vertex origin", out, "(0, 0)  P = 0")
    h.has("lp vertex 4,0", out, "(4, 0)  P = 20")
    h.has("lp vertex 3,1.5", out, "(3, 1.5)  P = 21")
    h.has("lp vertex 0,3", out, "(0, 3)  P = 12")
    h.has("lp optimal vertex", out, "Optimal vertex: x = 3, y = 1.5")
    h.has("lp optimal value", out, "P = 21")
    h.has("lp integer point", out, "Best integer point (L10): x = 4, y = 0, P = 20")

    out = h.drive(algos.lpgraph,
                  ["0", "2 3", "2", "1 0 5", "0 1 5", "1", "1 1 4"])
    h.has("lp min statement", out, "Minimise C = 2x + 3y")
    h.has("lp min ge constraint", out, "x + y >= 4")
    h.has("lp min vertex", out, "(4, 0)  C = 8")
    h.has("lp min vertex 5,5", out, "(5, 5)  C = 25")
    h.has("lp min optimum", out, "Optimal vertex: x = 4, y = 0")
    h.has("lp min value", out, "C = 8")

    out = h.drive(algos.lpgraph,
                  ["1", "1 1", "3", "2 2 5", "1 0 3", "0 1 3", "0"])
    h.has("lp integer LP vertex", out, "(2.5, 0)  P = 2.5")
    h.num("lp integer LP continuous", out, "P = ", 2.5)
    h.has("lp integer LP best", out, "Best integer point (L10): x = 0, y = 2, P = 2")

    out = h.drive(algos.lpgraph, ["1", "1 1", "0", "1", "1 0 1"])
    h.has("lp unbounded region", out, "Region is UNBOUNDED")
    h.has("lp unbounded objective", out, "P is UNBOUNDED on this region.")

    out = h.drive(algos.lpgraph, ["0", "2 3", "0", "1", "1 1 4"])
    h.has("lp unbounded but min exists", out, "Region is UNBOUNDED")
    h.has("lp min on unbounded region", out, "Optimal vertex: x = 4, y = 0")
    h.has("lp min on unbounded value", out, "C = 8")

    out = h.drive(algos.lpgraph, ["0", "1 1", "1", "1 1 1", "1", "1 1 5"])
    h.has("lp empty region", out, "The feasible region is EMPTY.")

    out = h.drive(algos.lpgraph, [None])
    h.check("lpgraph cancel", out, [])


SECTIONS = [
    ("Y433 quick sort", test_quicksort),
    ("Y433 sort/pack counts", test_sort_counts),
    ("Y433 graph info", test_graphinfo),
    ("Y433 Dijkstra labels and route", test_dijkstra_route),
    ("Y433 maximum flow", test_maxflow),
    ("Y433 cut capacity", test_cutcap),
    ("Y433 simplex", test_simplex),
    ("Y433 two-stage simplex", test_simplex2),
    ("Y433 LP graphically", test_lpgraph),
]
