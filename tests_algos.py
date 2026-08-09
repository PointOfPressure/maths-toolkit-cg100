# tests_algos.py - correctness tests for the Modelling with Algorithms (Y433)
# tools added to algos.py: quick sort, the graph/flow block, and the linear
# programming block, plus the labelling and route that Dijkstra now reports.
#
# Every problem below is worked by hand in the comment above it, so what is
# asserted is a known answer and not merely "the tool produced something".
# Picked up automatically by tests.py through the SECTIONS hook; the harness
# object `h` is passed in rather than importing tests.py again.


# ============================================================ sorting =====
def test_quicksort(h):
    import algos
    # Quick sort of 5 3 8 1 9 2 7, pivot = first item of each sub-list.
    # Pass 1  pivot 5: less 3,1,2 | greater 8,9,7  ->  3 1 2 [5] 8 9 7   (6 comps)
    # Pass 2  sub-lists {3,1,2} pivot 3 -> 1 2 [3]           (2 comps)
    #                   {8,9,7} pivot 8 -> 7 [8] 9           (2 comps)
    #         7, 9 are then single-item sub-lists, so they are in place too
    # Pass 3  sub-list {1,2} pivot 1 -> [1] 2, and 2 is a singleton (1 comp)
    # Sorted 1 2 3 5 7 8 9 after 3 passes and 6+2+2+1 = 11 comparisons.
    out = h.drive(algos.quicksort, ["5 3 8 1 9 2 7"])
    h.has("quicksort pass 1", out, "Pass 1: 3 1 2 [5] 8 9 7")
    h.has("quicksort pass 2", out, "Pass 2: 1 2 [3] [5] [7] [8] [9]")
    h.has("quicksort pass 3", out, "Pass 3: [1] [2] [3] [5] [7] [8] [9]")
    h.has("quicksort sorted", out, "Sorted: 1 2 3 5 7 8 9")
    h.has("quicksort passes", out, "Passes: 3")
    h.has("quicksort comparisons", out, "Comparisons: 11")

    # Already sorted 1 2 3 4 is quick sort's worst case with a first-item
    # pivot: pass 1 pivot 1 (3 comps), pass 2 pivot 2 (2), pass 3 pivot 3 (1),
    # 6 comparisons = n(n-1)/2, and the list never moves.
    out = h.drive(algos.quicksort, ["1 2 3 4"])
    h.has("quicksort sorted input", out, "Sorted: 1 2 3 4")
    h.has("quicksort worst case comps", out, "Comparisons: 6")
    h.has("quicksort worst case passes", out, "Passes: 3")

    # Reversed 4 3 2 1 is the other worst case: pivot 4 sends 3,2,1 left
    # (3 comps) giving 3 2 1 [4]; then pivot 3 -> 2 1 [3] (2); then 1 [2] (1).
    out = h.drive(algos.quicksort, ["4 3 2 1"])
    h.has("quicksort reversed pass 1", out, "Pass 1: 3 2 1 [4]")
    h.has("quicksort reversed", out, "Sorted: 1 2 3 4")
    h.has("quicksort reversed comps", out, "Comparisons: 6")

    # a single item is already sorted and needs no comparison
    out = h.drive(algos.quicksort, ["7"])
    h.has("quicksort singleton", out, "Sorted: 7")
    h.has("quicksort singleton comps", out, "Comparisons: 0")

    # cancelled input must not produce a result screen at all
    out = h.drive(algos.quicksort, [None])
    h.check("quicksort cancel", out, [])


def test_sort_counts(h):
    import algos
    # Bubble sort of 3 1 2. Pass 1: compare (3,1) swap -> 1 3 2, compare (3,2)
    # swap -> 1 2 3. Pass 2: compare (1,2), no swap. So 3 comparisons,
    # 2 swaps, 2 passes, and n(n-1)/2 = 3 comparisons in the worst case.
    out = h.drive(algos.bubble, ["3 1 2"])
    h.has("bubble comparisons", out, "Comparisons: 3")
    h.has("bubble swaps", out, "Swaps: 2")
    h.has("bubble worst case", out, "n(n-1)/2 = 3")

    # Insertion sort of 3 1 2: key 1 compares with 3 and shifts it (1 comp,
    # 1 shift); key 2 compares with 3 and shifts it, then compares with 1 and
    # stops (2 comps, 1 shift). Total 3 comparisons and 2 shifts.
    out = h.drive(algos.insertion, ["3 1 2"])
    h.has("insertion comparisons", out, "Comparisons: 3")
    h.has("insertion shifts", out, "Shifts: 2")

    # First fit, items 4 5 3 into bins of 10.
    #   4 -> no bin exists, open bin 1                       (0 comparisons)
    #   5 -> 4+5 = 9 <= 10, goes in bin 1                    (1 comparison)
    #   3 -> 9+3 = 12 > 10, so open bin 2                    (1 comparison)
    # 2 bins, 2 comparisons. Total size 12, so at least ceil(12/10) = 2 bins.
    out = h.drive(algos.firstfit, ["4 5 3", "10"])
    h.has("firstfit bins", out, "Bins used: 2")
    h.has("firstfit comparisons", out, "Comparisons: 2")
    h.has("firstfit lower bound", out, "Lower bound: 2 bins")

    # First fit decreasing sorts to 5 4 3 first: 5 opens bin 1, 4 fits
    # (1 comparison), 3 does not (1 comparison) and opens bin 2.
    out = h.drive(algos.firstfitdec, ["4 5 3", "10"])
    h.has("ffd order", out, "Bin 1: 5 4")
    h.has("ffd comparisons", out, "Comparisons: 2")


# ============================================================= graphs =====
def test_graphinfo(h):
    import algos
    # K3, the triangle: nodes 1,2,3 all joined. Order 3, size 3, every degree
    # 2, sum of degrees 6 = 2 x 3 (handshake), no odd nodes, connected.
    # Incidence matrix over the edges 1-2, 1-3, 2-3 is
    #   node 1: 1 1 0     node 2: 1 0 1     node 3: 0 1 1
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

    # Path 1 -> 2 -> 3 as a digraph: 2 arcs, node 1 has out 1 / in 0,
    # node 2 has out 1 / in 1, node 3 has out 0 / in 1. Incidence uses
    # -1 for the tail and +1 for the head.
    out = h.drive(algos.graphinfo, ["3", "0 1 0", "0 0 1", "0 0 0"])
    h.has("digraph size", out, "Size (arcs): 2")
    h.has("digraph directed", out, "Type: directed")
    h.has("digraph node 1", out, "node 1: out 1  in 0")
    h.has("digraph node 3", out, "node 3: out 0  in 1")
    h.has("digraph incidence", out, "2: 1 -1")

    # Two isolated edges 1-2 and 3-4 form a disconnected graph with four
    # odd (degree 1) nodes.
    out = h.drive(algos.graphinfo,
                  ["4", "0 1 0 0", "1 0 0 0", "0 0 0 1", "0 0 1 0"])
    h.has("disconnected", out, "Connected: no")
    h.has("disconnected odd", out, "Odd nodes: 4")


def test_dijkstra_route(h):
    import algos
    # Triangle 1-2 = 1, 2-3 = 2, 1-3 = 4, starting at node 1.
    #   label 1 permanently at 0; working values 1 -> 2 (via 1-2) and 4 -> 3
    #   label 2 permanently at 1; 1 + 2 = 3 beats 4, so 3's working value is 3
    #   label 3 permanently at 3
    # Shortest route 1 to 3 is 1 - 2 - 3 of length 3, NOT the direct arc of 4.
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

    # 0 for the end node means "no route wanted"; the distances still appear.
    out = h.drive(algos.dijkstra, ["3", "0 1 4", "1 0 2", "4 2 0", "1", "0"])
    h.has("dij no route distances", out, "Node 3: 3")
    for ln in out:
        h.truthy("dij no route line", "Route 1 to" not in ln)

    # Five-node network (undirected), start 1, end 5:
    #   1-2 = 4, 1-3 = 2, 2-3 = 1, 2-4 = 5, 3-4 = 8, 3-5 = 10, 4-5 = 2
    # By hand: perm 1 at 0; 3 at 2 (via 1-3); 2 at 3 (2+1 beats the direct 4);
    # 4 at 8 (3+5 beats 2+8 = 10); 5 at 10 (8+2 beats 2+10 = 12).
    # Shortest route 1 to 5 is 1 - 3 - 2 - 4 - 5 of length 10.
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

    # node 3 is cut off from 1 and 2, so it stays unreachable and has no route
    out = h.drive(algos.dijkstra, ["3", "0 1 0", "1 0 0", "0 0 0", "1", "3"])
    h.has("dij unreachable", out, "Node 3: unreachable")
    h.has("dij no path", out, "Route 1 to 3: none")


# ====================================================== flow networks =====
# Network used by both flow tests, all arcs directed:
#   1->2 cap 3, 1->3 cap 2, 2->3 cap 1, 2->4 cap 2, 3->4 cap 3
# Source 1, sink 4. By hand the augmenting paths are
#   1-2-4 (bottleneck min(3,2) = 2), 1-3-4 (min(2,3) = 2),
#   1-2-3-4 (min(1,1,1) = 1)  ->  maximum flow 5.
# Everything out of node 1 is then saturated, so the residual network reaches
# nothing from 1: the minimum cut is S = {1}, T = {2,3,4} with capacity
# 3 + 2 = 5, and max flow = min cut = 5.
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

    # A second network with an interior cut. Nodes 1..5, arcs
    #   1->2 = 6, 1->3 = 4, 2->4 = 3, 3->4 = 5, 2->5 = 2, 4->5 = 7
    # Into the sink 5 the total capacity is 2 + 7 = 9, so the flow cannot beat
    # 9; 9 is achievable - send 2 along 1-2-5, 3 along 1-2-4-5 and 4 along
    # 1-3-4-5, which uses 5 of the 6 on 1->2, all 4 of 1->3, and saturates
    # 2->4, 2->5 and 4->5. This network has TWO minimum cuts of capacity 9:
    #   S = {1,2}:      1->3 (4) + 2->4 (3) + 2->5 (2) = 9
    #   S = {1,2,3,4}:  2->5 (2) + 4->5 (7)            = 9
    # The residual network reaches only 1 and 2 (1->3, 2->4, 2->5 are all
    # saturated), so the tool must report the first of the two.
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

    # the other minimum cut of the same network, checked through cutcap
    out = h.drive(algos.cutcap, NET2 + ["1", "5", "1 2 3 4"])
    h.has("net2 other cut capacity", out, "Cut capacity = 9")
    h.has("net2 other cut is minimal", out, "This IS a minimum cut")

    # No route from source to sink at all: maximum flow 0 and the cut is empty.
    out = h.drive(algos.maxflow, ["3", "0 0 0", "0 0 5", "0 0 0", "1", "3"])
    h.has("no path max flow", out, "Maximum flow = 0")
    h.has("no path cut", out, "cut arcs: none")

    # source = sink is rejected without a result screen
    out = h.drive(algos.maxflow, FLOWNET + ["1", "1"])
    h.check("maxflow rejects s = t", out, [])


def test_cutcap(h):
    import algos
    # Same network. The cut S = {1,3}, T = {2,4} crosses on 1->2 (3) and
    # 3->4 (3), so its capacity is 6. Arc 2->3 runs backwards across the cut
    # and is NOT counted, though its capacity is 1. 6 > 5 = max flow, so this
    # cut is not minimal, and the excess is exactly 1.
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 3"])
    h.has("cut S set", out, "S = {1, 3}")
    h.has("cut T set", out, "T = {2, 4}")
    h.has("cut arc 1-2", out, "1-2: 3")
    h.has("cut arc 3-4", out, "3-4: 3")
    h.has("cut capacity 6", out, "Cut capacity = 6")
    h.has("cut backward arcs", out, "arcs T to S total 1, not counted")
    h.has("cut vs max flow", out, "Maximum flow = 5")
    h.has("cut not minimum", out, "Not minimum: capacity exceeds max flow by 1")

    # The cut S = {1} has capacity 3 + 2 = 5, which equals the maximum flow,
    # so this one IS a minimum cut.
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1"])
    h.has("min cut capacity", out, "Cut capacity = 5")
    h.has("min cut recognised", out, "This IS a minimum cut")

    # S = {1,2} crosses on 1->3 (2), 2->3 (1) and 2->4 (2): capacity 5, also
    # a minimum cut for this network.
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 2"])
    h.has("second min cut", out, "Cut capacity = 5")
    h.has("second min cut recognised", out, "This IS a minimum cut")

    # a cut has to separate the source from the sink
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "2 3"])
    h.has("cut needs source", out, "source must be on the source side")
    out = h.drive(algos.cutcap, FLOWNET + ["1", "4", "1 4"])
    h.has("cut needs sink outside", out, "sink must be on the sink side")


# ================================================ linear programming =====
def test_simplex(h):
    import algos
    # Maximise P = 5x + 4y subject to 6x + 4y <= 24, x + 2y <= 6, x, y >= 0.
    # By hand the vertices are (0,0) P = 0, (4,0) P = 20, (0,3) P = 12 and
    # the intersection of the two lines: x = 6 - 2y in 6x + 4y = 24 gives
    # 36 - 8y = 24, y = 1.5, x = 3, P = 15 + 6 = 21. So the optimum is 21.
    # Simplex, entering on the most negative objective entry:
    #   pivot 1  column x, ratios 24/6 = 4 and 6/1 = 6, so s1 leaves on 4
    #   pivot 2  column y, ratios 4/(2/3) = 6 and 2/(4/3) = 1.5, s2 leaves
    # Final: P = 21, x = 3, y = 1.5, s1 = s2 = 0, basic variables x and y.
    # Shadow price of C1 is 0.75 (raising b1 to 25 gives P = 21.75) and of
    # C2 is 0.5.
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

    # Maximise P = 4x + 3y subject to 2x + y <= 10, x + 3y <= 15, x <= 4.
    # Vertices: (0,0) 0, (4,0) 16, (4,2) 22, (3,4) 24, (0,5) 15 - the point
    # (3,4) is where 2x + y = 10 meets x + 3y = 15. So P = 24 at x = 3, y = 4,
    # and the third constraint is slack there: s3 = 4 - 3 = 1.
    # Simplex takes three pivots: x enters on ratio 4 (s3 leaves), y enters on
    # ratio 2 (s1 leaves), then s3 re-enters on ratio 1 (s2 leaves).
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

    # Three variables: maximise P = 3x + 2y + 4z subject to x + y + 2z <= 4
    # and 2x + 3z <= 5, x, y, z >= 0. Checked against the dual, which is
    # minimise 4u + 5v subject to u + 2v >= 3, u >= 2, 2u + 3v >= 4: u must be
    # at least 2, and then v >= 0.5, giving 4(2) + 5(0.5) = 10.5. The primal
    # point x = 2.5, y = 1.5, z = 0 attains 7.5 + 3 = 10.5 and uses both
    # constraints fully (2.5 + 1.5 = 4 and 2(2.5) = 5), so 10.5 is optimal
    # and z stays out of the basis.
    out = h.drive(algos.simplex, ["3", "2", "3 2 4", "1 1 2 4", "2 0 3 5"])
    h.has("simplex 3-var P", out, "P = 10.5")
    h.num("simplex 3-var x", out, "x = ", 2.5)
    h.num("simplex 3-var y", out, "y = ", 1.5)
    h.has("simplex 3-var z", out, "z = 0")
    h.has("simplex 3-var basic", out, "Basic variables: x, y")
    h.has("simplex 3-var non-basic", out, "Non-basic (= 0): z, s1, s2")
    # the dual values read off the objective row are u = 2 and v = 0.5
    h.num("simplex 3-var shadow C1", out, "C1 (s1): ", 2.0)
    h.num("simplex 3-var shadow C2", out, "C2 (s2): ", 0.5)

    # Unbounded: maximise P = x + y with only x - y <= 1. y can grow for ever,
    # so after x enters there is no leaving row in the y column.
    out = h.drive(algos.simplex, ["2", "1", "1 1", "1 -1 1"])
    h.has("simplex unbounded", out, "P is UNBOUNDED")

    # A negative right-hand side is not standard form and must be refused.
    out = h.drive(algos.simplex, ["2", "1", "1 1", "1 1 -3"])
    h.has("simplex needs b >= 0", out, "Standard form needs every b >= 0.")

    # cancelling at the first prompt shows nothing
    out = h.drive(algos.simplex, [None])
    h.check("simplex cancel", out, [])


def test_simplex2(h):
    import algos
    # Minimise C = 2x + 3y subject to x + y >= 4, x + 3y >= 6, x, y >= 0.
    # By hand the feasible vertices are (6,0) C = 12, (0,4) C = 12 and the
    # intersection of x + y = 4 with x + 3y = 6: subtracting, 2y = 2 so y = 1
    # and x = 3, C = 6 + 3 = 9. The minimum is C = 9 at (3, 1).
    # Both constraints are >=, so each needs a surplus u and an artificial a;
    # phase 1 drives a1 + a2 to zero, phase 2 then minimises C.
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

    # The same tool on an all-<= maximisation must reproduce the standard
    # simplex answer of the previous test: P = 21 at (3, 1.5), no phase 1.
    out = h.drive(algos.simplex2,
                  ["2", "2", "1", "5 4", "6 4 1 24", "1 2 1 6"])
    h.has("simplex2 max P", out, "P = 21")
    h.num("simplex2 max x", out, "x = ", 3.0)
    h.num("simplex2 max y", out, "y = ", 1.5)
    for ln in out:
        h.truthy("simplex2 skips phase 1 when unneeded", "Phase 1" not in ln)

    # An equality constraint (L15). Maximise P = x + 2y subject to
    # x + y = 4 and x <= 3, x, y >= 0. On the line x + y = 4 the objective is
    # x + 2(4 - x) = 8 - x, so it is largest at x = 0: P = 8 at (0, 4).
    out = h.drive(algos.simplex2,
                  ["2", "2", "1", "1 2", "1 1 0 4", "1 0 1 3"])
    h.has("simplex2 equality P", out, "P = 8")
    h.num("simplex2 equality x", out, "x = ", 0.0)
    h.num("simplex2 equality y", out, "y = ", 4.0)

    # Inconsistent constraints: x + y <= 2 and x + y >= 5 cannot both hold,
    # so phase 1 cannot drive the artificial to zero.
    out = h.drive(algos.simplex2,
                  ["2", "2", "0", "1 1", "1 1 1 2", "1 1 -1 5"])
    h.has("simplex2 infeasible", out, "the constraints are INFEASIBLE.")

    # A negative right-hand side is legal here: -x - y >= -4 is the same as
    # x + y <= 4, so maximising P = 3x + 2y gives P = 12 at (4, 0).
    out = h.drive(algos.simplex2, ["2", "1", "1", "3 2", "-1 -1 -1 -4"])
    h.has("simplex2 flipped row", out, "x + y <= 4")
    h.has("simplex2 flipped P", out, "P = 12")

    # a relation code that is not 1, 0 or -1 is rejected
    out = h.drive(algos.simplex2, ["2", "1", "1", "3 2", "1 1 7 4"])
    h.has("simplex2 bad relation", out, "rel must be 1 (<=), 0 (=) or -1 (>=).")


def test_lpgraph(h):
    import algos
    # Maximise P = 5x + 4y subject to 6x + 4y <= 24 and x + 2y <= 6.
    # The feasible region is the quadrilateral (0,0), (4,0), (3,1.5), (0,3):
    #   6x + 4y = 24 meets the x axis at (4,0) and x + 2y = 6 at (3,1.5)
    #   x + 2y = 6 meets the y axis at (0,3)
    # P is 0, 20, 21, 12 at those points, so the optimum is P = 21 at (3,1.5).
    # The best INTEGER point is (4,0) with P = 20; (3,1) gives 19 and (2,2)
    # gives 18.
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

    # Minimise C = 2x + 3y subject to x <= 5, y <= 5 and x + y >= 4.
    # Vertices: (4,0), (5,0), (5,5), (0,5), (0,4) with C = 8, 10, 25, 15, 12.
    # The minimum is C = 8 at (4, 0).
    out = h.drive(algos.lpgraph,
                  ["0", "2 3", "2", "1 0 5", "0 1 5", "1", "1 1 4"])
    h.has("lp min statement", out, "Minimise C = 2x + 3y")
    h.has("lp min ge constraint", out, "x + y >= 4")
    h.has("lp min vertex", out, "(4, 0)  C = 8")
    h.has("lp min vertex 5,5", out, "(5, 5)  C = 25")
    h.has("lp min optimum", out, "Optimal vertex: x = 4, y = 0")
    h.has("lp min value", out, "C = 8")

    # Integer LP that differs from the continuous answer. Maximise P = x + y
    # subject to 2x + 2y <= 5, x <= 3, y <= 3. The binding constraint is
    # x + y <= 2.5, so the continuous optimum is P = 2.5 all along that edge
    # and the vertices are (0,0), (2.5,0), (0,2.5). No integer point reaches
    # 2.5: the best integer value is P = 2, attained at (0,2), (1,1) and
    # (2,0). Scanning x upwards from 0 and keeping the first best, the tool
    # must report (0, 2).
    out = h.drive(algos.lpgraph,
                  ["1", "1 1", "3", "2 2 5", "1 0 3", "0 1 3", "0"])
    h.has("lp integer LP vertex", out, "(2.5, 0)  P = 2.5")
    h.num("lp integer LP continuous", out, "P = ", 2.5)
    h.has("lp integer LP best", out, "Best integer point (L10): x = 0, y = 2, P = 2")

    # Unbounded region AND unbounded objective: maximise P = x + y with only
    # x >= 1. Nothing stops x or y growing.
    out = h.drive(algos.lpgraph, ["1", "1 1", "0", "1", "1 0 1"])
    h.has("lp unbounded region", out, "Region is UNBOUNDED")
    h.has("lp unbounded objective", out, "P is UNBOUNDED on this region.")

    # Unbounded region but a bounded MINIMUM: minimise C = 2x + 3y subject to
    # x + y >= 4 only. The region runs off to infinity, but C is smallest at
    # the vertex (4, 0) with C = 8.
    out = h.drive(algos.lpgraph, ["0", "2 3", "0", "1", "1 1 4"])
    h.has("lp unbounded but min exists", out, "Region is UNBOUNDED")
    h.has("lp min on unbounded region", out, "Optimal vertex: x = 4, y = 0")
    h.has("lp min on unbounded value", out, "C = 8")

    # Empty region: x + y <= 1 and x + y >= 5 have no common point.
    out = h.drive(algos.lpgraph, ["0", "1 1", "1", "1 1 1", "1", "1 1 5"])
    h.has("lp empty region", out, "The feasible region is EMPTY.")

    # cancelling at the first prompt shows nothing
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
