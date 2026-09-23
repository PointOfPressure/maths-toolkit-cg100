# Cases for falgo.py (MEI H645 Modelling with Algorithms, Y433).
# Every number in a needle is worked by hand (working in the comment) or is a
# textbook result carried over from the old main tests_algos.py.
NET5 = '1,2,4,1,3,2,2,3,1,2,4,5,3,4,8,3,5,10,4,5,2'
FLOW4 = '1,2,3,1,3,2,2,3,1,2,4,2,3,4,3'
FLOW5 = '1,2,6,1,3,4,2,4,3,2,5,2,3,4,5,4,5,7'
# A 1-2 d3, B 1-3 d2, C 2-4 d4, D 3-4 d2, E 3-5 d3, F 4-6 d2, G 5-6 d1, H 1-6 d4
AOA = '1,2,3,1,3,2,2,4,4,3,4,2,3,5,3,4,6,2,5,6,1,1,6,4'
CASES = [
    # --- A sorting and packing ------------------------------------------------
    # 3 1 2: pass 1 compares 2 pairs, swaps both; pass 2 one compare, no swap
    ('A', 'Bubble sort', '3,1,2',
     ['sorted: 1 2 3', 'comparisons = 3', 'swaps = 2', 'passes = 2',
      'n(n-1)/2 = 3']),
    # already sorted: one pass of 3 comparisons and stop
    ('A', 'Bubble sort', '1,2,3,4',
     ['comparisons = 3', 'swaps = 0', 'passes = 1', 'no swaps in pass 1']),
    # 5 3 8 1: 1 + 1 + 3 comparisons, 1 + 0 + 3 swaps
    ('A', 'Shuttle sort', '5,3,8,1',
     ['sorted: 1 3 5 8', 'comparisons = 5', 'swaps = 4', 'passes = 3',
      'pass 1: 3 5 8 1']),
    # old main quick sort case: 6 + 4 + 1 = 11 comparisons over 3 passes
    ('A', 'Quick sort', '5,3,8,1,9,2,7',
     ['pass 1: 3 1 2 [5] 8 9 7', 'pass 2: 1 2 [3] [5] [7] [8] [9]',
      'sorted: 1 2 3 5 7 8 9', 'comparisons = 11', 'passes = 3']),
    # sorted input is the worst case: 3 + 2 + 1 = 6
    ('A', 'Quick sort', '1,2,3,4', ['comparisons = 6', 'passes = 3']),
    ('A', 'Quick sort', '7', ['sorted: 7', 'comparisons = 0', 'passes = 0']),
    # 4, 5 (fit test with bin 1: no), 3 (bin 1: 9 + 3 > 10 no, bin 2 yes) = 2
    ('A', 'First fit', '10,4,5,3',
     ['bins used = 2', 'comparisons = 2', 'bin 1: 4 5 (9)', 'bin 2: 3 (3)',
      'lower bound = 2 bins']),
    ('A', 'First fit', '10,4,11', ['item 11 is bigger than C']),
    ('A', 'First fit decreasing', '10,4,5,3',
     ['bin 1: 5 4 (9)', 'comparisons = 2', 'sorted first: 5 4 3']),
    # 8 7 6 5 4 into 10: 8 | 7 | 6 4 | 5; total 30 so the bound is 3
    ('A', 'First fit decreasing', '10,5,7,4,8,6',
     ['bins used = 4', 'bin 1: 8 (8)', 'bin 3: 6 4 (10)', 'lower bound = 3 bins']),
    # O(n^2): 3 s for n = 100 -> 3 x 5^2 = 75 s for n = 500
    ('A', 'Order n^k scaling', '2,100,3,500', ['t2 = 75', 'factor = 25']),
    # 1000 ln 1000 / (100 ln 100) = 10 x 3/2 = 15, so 2 s -> 30 s
    ('A', 'Order n log n scaling', '100,2,1000', ['t2 = 30', 'factor = 15']),

    # --- G graphs -------------------------------------------------------------
    ('G', 'Graph from edges', '3,1,2,1,3,2,3',
     ['order = 3 nodes', 'size = 3 edges', 'degrees 1..n: 2 2 2',
      'odd nodes: none', 'connected: yes', 'sum of degrees = 6 = 2 x 3',
      'complete graph K3', '1: 0 1 1', '1: 1 1 0', '3: 0 1 1']),
    # loop at 1 (degree +2) and a double edge 1-2; two components
    ('G', 'Graph from edges', '4,1,1,1,2,1,2,3,4',
     ['degrees 1..n: 4 2 1 1', 'odd nodes: 3 4', 'connected: no',
      'simple: no', '1: 1 2 0 0', '1: 2 1 1 0']),
    ('G', 'Digraph from arcs', '3,1,2,2,3',
     ['size = 2 arcs', 'out 1..n: 1 1 0', 'in 1..n: 0 1 1',
      'strongly connected: no', '2: 1 -1']),
    ('G', 'Digraph from arcs', '3,1,2,2,3,3,1', ['strongly connected: yes']),
    ('G', 'Graph from adjacency', '4,0,1,0,0,1,0,0,0,0,0,0,1,0,0,1,0',
     ['undirected', 'size = 2 edges', 'odd nodes: 1 2 3 4', 'connected: no']),
    ('G', 'Graph from adjacency', '3,0,1,0,0,0,1,0,0,0',
     ['directed', 'size = 2 arcs', 'out 1..n: 1 1 0']),

    # --- N networks -------------------------------------------------------------
    # old main 5-node case: permanent 1(0) 3(2) 2(3) 4(8) 5(10)
    ('N', 'Dijkstra', '1,5,' + NET5,
     ['shortest 1 to 5 = 10', 'route: 1-3-2-4-5', 'node 2: 3 (order 3)',
      'node 5: 10 (order 5)', 'node 2 working: 4, 3', 'node 5 working: 12, 10',
      'node 4 working: 10, 8', 'O(n^2)']),
    ('N', 'Dijkstra', '1,3,1,2,1', ['no route from 1 to 3', 'node 3: unreachable']),
    ('N', 'Dijkstra', '1,0,1,2,1,2,3,2,1,3,4',
     ['node 3: 3 (order 3)', 'node 3 working: 4, 3']),
    # arcs 1->2 (1), 2->3 (1), 3->1 (1): 1 to 3 is 2 one way round
    ('N', 'Dijkstra directed', '1,3,1,2,1,2,3,1,3,1,1',
     ['shortest 1 to 3 = 2', 'route: 1-2-3']),
    ('N', 'Dijkstra directed', '3,2,1,2,1,2,3,1,3,1,1', ['shortest 3 to 2 = 2']),
    # MST 2-3 (1) + 1-3 (2) + 4-5 (2) + 2-4 (5) = 10
    ('N', 'Prim', '1,' + NET5,
     ['MST weight = 10', '1-3  (2)', '3-2  (1)', '2-4  (5)', '4-5  (2)',
      'nodes joined in order: 1, 3, 2, 4, 5']),
    ('N', 'Prim', '1,1,2,3,3,4,1', ['MST weight = 3', 'not connected']),
    ('N', 'Prim from matrix',
     '5,1,0,4,2,0,0,4,0,1,5,0,2,1,0,8,10,0,5,8,0,2,0,0,10,2,0',
     ['MST weight = 10', 'nodes joined in order: 1, 3, 2, 4, 5']),
    ('N', 'Kruskal', NET5,
     ['MST weight = 10', 'accept 2-3 (1)', 'reject 1-2 (4): makes a cycle',
      'accept 2-4 (5)', 'O(m log m)']),
    ('N', 'Kruskal', '1,2,1,3,4,1', ['MST weight = 2', 'not connected']),
    # 1-2 (1), 2-3 (2), 1-3 (4): shortest 1 to 3 = 3 via 2
    ('N', 'Shortest path as LP', '1,3,1,2,1,2,3,2,1,3,4',
     ['Minimise x12 + 4x13 + x21 + 2x23', '1: x12 + x13 - x21 - x31 = 1',
      '3: x31 + x32 - x13 - x23 = -1', 'shortest 1 to 3 = 3']),

    # --- F network flows ----------------------------------------------------------
    # old main FLOWNET: max flow 5, cut {1} | {2,3,4} of capacity 3 + 2
    ('F', 'Max flow min cut', '1,4,' + FLOW4,
     ['max flow = 5', 'min cut S = {1}', 'T = {2, 3, 4}', 'cut arcs: 1-2 1-3',
      'cut capacity = 5', '1-2: 3/3 *', '3-4: 3/3 *',
      'path 1 flow 2: 1-2-4', 'path 3 flow 1: 1-2-3-4']),
    ('F', 'Max flow min cut', '1,5,' + FLOW5,
     ['max flow = 9', 'min cut S = {1, 2}', 'cut arcs: 1-3 2-4 2-5',
      '1-2: 5/6', '4-5: 7/7 *']),
    ('F', 'Max flow min cut', '1,3,2,3,5', ['max flow = 0', 'cut arcs: none']),
    # S = {1, 3}: 1-2 (3) + 3-4 (3) = 6; back arc 2-3 (1) not counted
    ('F', 'Cut capacity', '1,4,13,' + FLOW4,
     ['cut capacity = 6', 'S = {1, 3}', 'T = {2, 4}', 'max flow = 5',
      'not minimum: 1 over', 'T -> S total 1']),
    ('F', 'Cut capacity', '1,4,12,' + FLOW4,
     ['cut capacity = 5', 'this is a minimum cut']),
    ('F', 'Cut capacity', '1,4,23,' + FLOW4, ['the source must be in S']),
    ('F', 'Cut capacity', '1,4,14,' + FLOW4, ['the sink must not be in S']),
    ('F', 'Max flow as LP', '1,4,' + FLOW4,
     ['Maximise F = x12 + x13', '2: x12 = x23 + x24', '3: x13 + x23 = x34',
      '0<=x12<=3', 'LP optimum = max flow = 5']),

    # --- C critical path ---------------------------------------------------------
    # early 0 3 2 7 5 9, late 0 3 5 7 8 9; B 1-3: TF 5-0-2 = 3, IF 0;
    # H 1-6: TF 9-0-4 = 5, IF 9-0-4 = 5, interfering 0
    ('C', 'Activity on arc', AOA,
     ['duration = 9', 'critical: 1-2 2-4 4-6', '3: 2, 5', '5: 5, 8',
      '1-3 d2 TF 3 IF 0 int 3', '1-6 d4 TF 5 IF 5 int 0', '2-4 d4 TF 0 IF 0 int 0']),
    # 1-2 d5, 2-3 d1, 1-3 d2, 3-4 d1, 1-4 d20: early 0 5 6 20, late 0 18 19 20
    # 1-3: TF = 19 - 0 - 2 = 17, IF = 6 - 0 - 2 = 4, interfering 13
    ('C', 'Activity on arc', '1,2,5,2,3,1,1,3,2,3,4,1,1,4,20',
     ['duration = 20', 'critical: 1-4', '1-3 d2 TF 17 IF 4 int 13',
      '3-4 d1 TF 13 IF 0 int 13', '2: 5, 18']),
    ('C', 'Activity on arc', '1,2,1,2,1,1', ['the network has a cycle']),
    # A 3, B 2, C 4 after A, D 2 after B, E 3 after B, F 2 after C, G 1 after E
    ('C', 'Precedence table', '3,0,2,0,4,1,1,2,1,2,3,1,2,2,1,3,1,1,5',
     ['duration = 9', 'critical: A C F', 'B d2 ES 0 LF 5 TF 3',
      'D d2 ES 2 LF 9 TF 5', 'G d1 ES 5 LF 9 TF 3']),
    ('C', 'Precedence table', '1,1,2,1,1,1', ['the precedences form a cycle']),
    # AOA minus H, resources A2 B1 C1 D3 E1 F2 G1: work 26, ceil(26/9) = 3
    ('C', 'Resource histogram',
     '1,2,3,2,1,3,2,1,2,4,4,1,3,4,2,3,3,5,3,1,4,6,2,2,5,6,1,1',
     ['duration = 9', 'peak, all early = 6', 'peak, all late = 5',
      'lower bound = 3 workers', '2 to 3: 6', '4 to 6: 2', '5 to 7: 5',
      'total work = sum d x res = 26']),

    # A 1-2 d3, B 1-3 d2, C 2-4 d4, D 3-4 d2; latest starts A 0, B 3, C 3, D 5
    # one worker: A 0-3, B 3-5 (tie with C, input order), C 5-9, D 9-11
    ('C', 'Schedule k workers', '1,1,2,3,1,3,2,2,4,4,3,4,2',
     ['finish time = 11', 'critical path = 7', 'W1: 1-2 0-3, 1-3 3-5, 2-4 5-9',
      '3-4 9-11', 'late by 4']),
    # two workers: W2 takes B 0-2 then D 2-4; W1 A 0-3 then C 3-7
    ('C', 'Schedule k workers', '2,1,2,3,1,3,2,2,4,4,3,4,2',
     ['finish time = 7', 'W1: 1-2 0-3, 2-4 3-7', 'W2: 1-3 0-2, 3-4 2-4']),
    # dummy 2-3 makes D wait for A as well: D 3-5
    ('C', 'Schedule k workers', '2,1,2,3,1,3,2,2,4,4,3,4,2,2,3,0',
     ['finish time = 7', 'W2: 1-3 0-2, 3-4 3-5']),

    # --- L graphical LP ----------------------------------------------------------
    # old main: vertices (0,0) (4,0) (3,1.5) (0,3); P = 21 at (3, 3/2)
    ('L', 'LP 2-D maximise', '5,4,6,4,1,24,1,2,1,6',
     ['P = 21', 'at x = 3, y = 3/2', '(4, 0): P = 20', '(0, 3): P = 12',
      'integer: (4, 0), P = 20', '(3, 1) P = 19', '(3, 2) not feasible']),
    # 2x + 2y <= 5: whole edge optimal at 5/2; integer best 2
    ('L', 'LP 2-D maximise', '1,1,2,2,1,5,1,0,1,3,0,1,1,3',
     ['P = 5/2', 'also optimal at (0, 5/2)', 'integer: (0, 2), P = 2']),
    ('L', 'LP 2-D maximise', '1,1,1,0,-1,1', ['P is unbounded on this region']),
    # x + y = 4 as two inequalities (L15), x <= 3: max x + 2y at (0, 4)
    ('L', 'LP 2-D maximise', '1,2,1,1,0,4,1,0,1,3',
     ['P = 8', 'at x = 0, y = 4', 'L15: x + y = 4 is <= and >=']),
    ('L', 'LP 2-D minimise', '2,3,1,0,1,5,0,1,1,5,1,1,-1,4',
     ['C = 8', 'at x = 4, y = 0', '(5, 5): C = 25', '(0, 4): C = 12']),
    ('L', 'LP 2-D minimise', '2,3,1,1,-1,4',
     ['C = 8', 'the feasible region is unbounded']),
    ('L', 'LP 2-D minimise', '1,1,1,1,1,1,1,1,-1,5', ['the feasible region is empty']),
    # same LP as the 3-variable simplex case: max 21/2 at (5/2, 3/2, 0)
    ('L', 'LP 3-D vertices', '3,2,4,1,1,2,1,4,2,0,3,1,5',
     ['max P = 21/2', 'at (5/2, 3/2, 0)', 'min P = 0', '6 vertices',
      '(0, 2/3, 5/3) P=8']),
    ('L', 'LP 3-D vertices', '1,1,1,1,1,1,-1,1',
     ['max: P is unbounded', 'min P = 1']),

    # --- S simplex ----------------------------------------------------------------
    # old main: P = 21 at (3, 1.5), shadow prices 3/4 and 1/2
    ('S', 'Simplex max <=', '2,5,4,6,4,24,1,2,6',
     ['P = 21', 'x = 3', 'y = 3/2', 's1 = 0, s2 = 0', 's1: 3/4, s2: 1/2',
      'objective row: P - 5x - 4y = 0', '6x + 4y + s1 = 24',
      'pivot 1: x enters, s1 leaves', 'ratio 3/2, pivot 4/3',
      'start (0, 0) P = 0', '1: (4, 0) P = 20', '2: (3, 3/2) P = 21']),
    # old main B: P = 24 at (3, 4), s3 = 1; duals 2u+v = 4, u+3v = 3
    ('S', 'Simplex max <=', '2,4,3,2,1,10,1,3,15,1,0,4',
     ['P = 24', 'x = 3', 'y = 4', 's3 = 1', 's1: 9/5, s2: 2/5, s3: 0',
      'basic: x, y, s3']),
    ('S', 'Simplex max <=', '3,3,2,4,1,1,2,4,2,0,3,5',
     ['P = 21/2', 'x = 5/2', 'z = 0', 's1: 2, s2: 1/2', '1: (0, 0, 5/3) P = 20/3']),
    ('S', 'Simplex max <=', '2,1,1,1,-1,1', ['P is unbounded']),
    ('S', 'Simplex max <=', '2,1,1,1,1,-3', ['row 1 has b < 0']),
    # optimum at 6x+4y=24, x+2y=6: c(x)/4 in [1/2, 3/2]; b1 from 12 to 36
    ('S', 'Sensitivity ranging', '2,5,4,6,4,24,1,2,6',
     ['P = 21 at (3, 3/2)', '2 <= c(x) <= 6', '10/3 <= c(y) <= 10',
      '12 <= b1 <= 36', '4 <= b2 <= 12', 'P changes by 3/4 per unit of b1']),
    # x stays 0 at (0, 5) for max x + 2y, x + y <= 5, while c(x) <= 2
    ('S', 'Sensitivity ranging', '2,1,2,1,1,5',
     ['P = 10 at (0, 5)', '-inf <= c(x) <= 2', '0 <= b1 <= inf']),
    # x + y = 4 split into <= and >= (L15), x <= 3: max x + 2y = 8 at (0, 4)
    ('S', 'Two-stage maximise', '2,1,2,1,1,0,4,1,0,1,3',
     ['P = 8', 'x = 0', 'y = 4', 'L15: row 1 = split into <= and >=',
      'stage 1: minimise A = a2']),
    # max 2x + 3y, x + y <= 6, x >= 1, y <= 4 -> (2, 4), P = 16
    ('S', 'Two-stage maximise', '2,2,3,1,1,1,6,1,0,-1,1,0,1,1,4',
     ['P = 16', 'x = 2', 'y = 4']),
    # -x - y >= -4 is x + y <= 4: max 3x + 2y = 12 at (4, 0)
    ('S', 'Two-stage maximise', '2,3,2,-1,-1,-1,-4',
     ['P = 12', 'x = 4', 'row 1 x -1 so the RHS is >= 0']),
    ('S', 'Two-stage maximise', '2,3,2,1,1,7,4', ['rel must be 1 (<=), 0 (=) or -1 (>=)']),
    # old main: min 2x + 3y, x + y >= 4, x + 3y >= 6 -> C = 9 at (3, 1)
    ('S', 'Two-stage minimise', '2,2,3,1,1,-1,4,1,3,-1,6',
     ['C = 9', 'x = 3', 'y = 1', 'u1 = 0, u2 = 0', 'minimise C: maximise P = -C',
      'stage 1 done']),
    ('S', 'Two-stage minimise', '2,1,1,1,1,1,2,1,1,-1,5',
     ['infeasible: stage 1 ends with A > 0']),
    ('S', 'Big-M maximise', '2,2,3,1,1,1,6,1,0,-1,1,0,1,1,4',
     ['P = 16', 'x = 2', 'y = 4', 'a2 = 0', 'maximise P = 2x + 3y - M(a2)']),
    ('S', 'Big-M minimise', '2,2,3,1,1,-1,4,1,3,-1,6',
     ['C = 9', 'x = 3', 'y = 1', '2-2M', '3-4M', '-10M',
      'start (0, 0) C = 0 *', '2: (3, 1) C = 9', 'not a feasible vertex']),
    ('S', 'Big-M minimise', '2,1,1,1,1,1,1,1,1,-1,5', ['infeasible: a2 stays > 0']),
    # x >= -3 (L16): X = x + 3; max -x + y, x + y <= 5, y <= 4 -> x = -3, y = 4
    ('S', 'Negative variables', '2,-3,0,-1,1,1,1,1,5,0,1,1,4',
     ['P = 7', 'x = -3  (X = 0)', 'y = 4', 'x >= -3: x = X - 3, X >= 0',
      'X + Y <= 8', 'Maximise P = -X + Y + 3']),
]
