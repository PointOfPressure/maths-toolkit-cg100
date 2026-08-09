import math


def _table(out):
    rows = []
    for ln in out:
        if ln.startswith('n=') and ' u=' in ln and ' closed=' in ln:
            n = ln.split('n=')[1].split(' ')[0]
            u = ln.split(' u=')[1].split(' ')[0]
            c = ln.split(' closed=')[1].split(' ')[0]
            rows.append((int(n), float(u), float(c)))
    return rows


def _seq1(a, f, u0, terms):
    out = [u0]
    n = 0
    while n < terms - 1:
        out.append(a * out[n] + f(n))
        n += 1
    return out


def _seq2(a, b, f, u0, u1, terms):
    out = [u0, u1]
    n = 0
    while n < terms - 2:
        out.append(a * out[n + 1] + b * out[n] + f(n))
        n += 1
    return out


def _check_table(h, label, out, want):
    rows = _table(out)
    h.check(label + ': 11 rows printed', len(rows), 11)
    i = 0
    while i < len(rows) and i < len(want):
        tol = 1e-4 * (1.0 + abs(want[i]))
        h.close(label + ': u(' + str(i) + ') from the recurrence',
                rows[i][1], want[i], tol)
        h.close(label + ': u(' + str(i) + ') from the closed form',
                rows[i][2], want[i], tol)
        i += 1


def test_recur_nonhom(h):
    import xpure

    o = h.drive(xpure.t_recur_nonhom, ["2", "3", "1"])
    h.has("closed form", o, "u(n) = ")
    h.has("2u+3 closed form", o, "u(n) = 4*2^n - 3")
    h.has("2u+3 particular", o, "p(n) = -3")
    h.has("2u+3 constant forcing named", o, "f(n) is a constant.")
    h.has("2u+3 fits A", o, "u(0) = 1 fixes A = 4")
    h.has("2u+3 at n=5", o, "n=5  u=125  closed=125")
    h.has("2u+3 at n=10", o, "n=10  u=4093  closed=4093")
    h.has("2u+3 check passed", o, "checked against the recurrence")
    _check_table(h, "2u+3", o, _seq1(2.0, lambda n: 3.0, 1.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["2", "1", "1"])
    h.has("2u+1 closed form", o, "u(n) = 2*2^n - 1")
    h.has("2u+1 at n=5", o, "n=5  u=63  closed=63")
    _check_table(h, "2u+1", o, _seq1(2.0, lambda n: 1.0, 1.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["2", "3*2^n", "1"])
    h.has("resonance spotted", o, "RESONANCE")
    h.has("resonant trial carries n", o, "trial p(n) = C n 2^n")
    h.has("resonant particular", o, "p(n) = 1.5*n*2^n")
    h.has("resonant closed form", o, "u(n) = 2^n + 1.5*n*2^n")
    h.has("resonant at n=3", o, "n=3  u=44  closed=44")
    h.has("resonant at n=10", o, "n=10  u=16384  closed=16384")
    _check_table(h, "3*2^n", o,
                 _seq1(2.0, lambda n: 3.0 * 2.0 ** n, 1.0, 11))

    h.truthy("resonant answer is not the naive C 2^n",
             "u(n) = 2^n + 1.5*2^n" not in o)

    o = h.drive(xpure.t_recur_nonhom, ["1", "n", "0"])
    h.has("a=1 is resonant for a polynomial", o, "RESONANCE")
    h.has("triangular numbers", o, "u(n) = 0.5*n^2 - 0.5*n")
    h.has("triangular at n=10", o, "n=10  u=45  closed=45")
    _check_table(h, "u+n", o, _seq1(1.0, lambda n: float(n), 0.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["3", "n^2", "0"])
    h.has("quadratic forcing named", o, "f(n) is a polynomial of degree 2.")
    h.has("quadratic trial", o, "trial p(n) = (C0 + C1 n + C2 n^2)")
    h.has("quadratic particular", o, "p(n) = -0.5*n^2 - 0.5*n - 0.5")
    h.has("quadratic at n=5", o, "n=5  u=106  closed=106")
    _check_table(h, "3u+n^2", o,
                 _seq1(3.0, lambda n: float(n) * n, 0.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["0.5", "0", "8"])
    h.has("homogeneous first order", o, "u(n) = 8*0.5^n")
    h.has("halving at n=3", o, "n=3  u=1  closed=1")
    _check_table(h, "0.5u", o, _seq1(0.5, lambda n: 0.0, 8.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["-1", "(-1)^n", "1"])
    h.has("negative base resonance", o, "RESONANCE")
    h.has("negative base closed form", o, "u(n) = (-1)^n - n*(-1)^n")
    h.has("negative base at n=4", o, "n=4  u=-3  closed=-3")
    _check_table(h, "-u+(-1)^n", o,
                 _seq1(-1.0, lambda n: (-1.0) ** n, 1.0, 11))

    o = h.drive(xpure.t_recur_nonhom, ["2", "3", "13", "2"])
    h.has("indexing from n0 = 2", o, "u(2) = 13 fixes A = 4")
    h.has("n0 = 2 closed form", o, "u(n) = 4*2^n - 3")
    h.has("n0 = 2 starts at n=2", o, "n=2  u=13  closed=13")

    o = h.drive(xpure.t_recur_nonhom, ["2", "sin(n)", "0"])
    h.has("unrecognised forcing is admitted", o, "not a constant, a")
    h.has("summation form offered", o, "sum a^(n-1-k) f(k)")
    h.truthy("no closed form is claimed for sin(n)",
             not [ln for ln in o if ln.startswith("u(n) = ")])

    o = h.drive(xpure.t_recur_nonhom, ["2", "t^2", "1"])
    h.has("an unknown letter is refused", o, 'uses the letter "t"')


def test_recur_nonhom2(h):
    import xpure

    o = h.drive(xpure.t_recur_nonhom2, ["1", "1", "0", "1", "1"])
    h.has("Fibonacci closed form", o, "u(n) = ")
    h.has("Fibonacci golden ratio", o, "r1 = 1.618")
    h.has("Fibonacci second root", o, "r2 = -0.618")
    h.has("Fibonacci u(10) = 89", o, "n=10  u=89  closed=89")
    h.has("Fibonacci u(5) = 8", o, "n=5  u=8  closed=8")
    _check_table(h, "Fibonacci", o,
                 _seq2(1.0, 1.0, lambda n: 0.0, 1.0, 1.0, 11))
    h.num("Fibonacci constant A", o, "A = ", 0.723607, 1e-4)

    o = h.drive(xpure.t_recur_nonhom2, ["3", "-2", "1", "0", "0"])
    h.has("2nd order roots 2 and 1", o, "r1 = 2, r2 = 1")
    h.has("2nd order resonance", o, "RESONANCE")
    h.has("2nd order resonant trial", o, "trial p(n) = C n")
    h.has("2nd order particular", o, "p(n) = -n")
    h.has("2nd order closed form", o, "u(n) = 2^n - 1 - n")
    h.has("2nd order at n=4", o, "n=4  u=11  closed=11")
    h.has("2nd order at n=10", o, "n=10  u=1013  closed=1013")
    _check_table(h, "3u-2u+1", o,
                 _seq2(3.0, -2.0, lambda n: 1.0, 0.0, 0.0, 11))

    o = h.drive(xpure.t_recur_nonhom2, ["4", "-4", "0", "1", "4"])
    h.has("repeated root found", o, "repeated root r = 2")
    h.has("repeated root CF", o, "CF = (A + B n)(2)^n")
    h.has("repeated root closed form", o, "u(n) = 2^n + n*2^n")
    h.has("repeated root at n=5", o, "n=5  u=192  closed=192")
    h.has("repeated root at n=10", o, "n=10  u=11264  closed=11264")
    _check_table(h, "repeated root", o,
                 _seq2(4.0, -4.0, lambda n: 0.0, 1.0, 4.0, 11))

    o = h.drive(xpure.t_recur_nonhom2, ["0", "-1", "0", "1", "0"])
    h.has("complex roots reported", o, "complex roots")
    h.has("modulus is 1", o, "modulus R = 1")
    h.num("argument is pi/2", o, "argument t = ", math.pi / 2.0, 1e-3)
    h.has("complex closed form", o, "u(n) = cos(1.5708n)")
    h.has("complex at n=10", o, "n=10  u=-1  closed=-1")
    _check_table(h, "u(n+2)=-u(n)", o,
                 _seq2(0.0, -1.0, lambda n: 0.0, 1.0, 0.0, 11))

    o = h.drive(xpure.t_recur_nonhom2, ["1", "-1", "0", "2", "1"])
    h.num("argument is pi/3", o, "argument t = ", math.pi / 3.0, 1e-3)
    h.has("period six closed form", o, "u(n) = 2*cos(1.0472n)")
    _check_table(h, "period six", o,
                 _seq2(1.0, -1.0, lambda n: 0.0, 2.0, 1.0, 11))

    o = h.drive(xpure.t_recur_nonhom2, ["3", "-2", "2^n", "0", "0"])
    h.has("exponential resonance", o, "RESONANCE")
    h.has("exponential resonant trial", o, "trial p(n) = C n 2^n")
    h.has("exponential particular", o, "p(n) = 0.5*n*2^n")
    h.has("exponential at n=10", o, "n=10  u=4097  closed=4097")
    _check_table(h, "3u-2u+2^n", o,
                 _seq2(3.0, -2.0, lambda n: 2.0 ** n, 0.0, 0.0, 11))

    o = h.drive(xpure.t_recur_nonhom2, ["1", "1", "0", "1", "2", "1"])
    h.has("2nd order from n0 = 1", o, "n=1  u=1  closed=1")
    h.has("2nd order n0 = 1 at n=10", o, "n=10  u=89  closed=89")


def test_recur_verify(h):
    import xpure

    o = h.drive(xpure.t_recur_verify, ["2u+1", "2^(n+1)-1"], [0])
    h.has("verified solution", o, "SATISFIES")
    h.has("verify at n=0", o, "n=0  LHS=3  RHS=3  diff=0")
    h.has("verify at n=5", o, "n=5  LHS=127  RHS=127  diff=0")
    h.has("verify shows the substitution", o, "substituting the candidate")

    o = h.drive(xpure.t_recur_verify, ["2u+1", "2^n"], [0])
    h.has("rejected solution", o, "does NOT")
    h.has("rejection at n=0", o, "n=0  LHS=2  RHS=3  diff=1")

    o = h.drive(xpure.t_recur_verify, ["3v-2u", "2^n"], [1])
    h.has("2nd order verification", o, "SATISFIES")
    h.has("2nd order verify at n=0", o, "n=0  LHS=4  RHS=4  diff=0")

    o = h.drive(xpure.t_recur_verify, ["v+u", "n"], [1])
    h.has("2nd order rejection", o, "does NOT")
    h.has("2nd order rejection at n=0", o, "n=0  LHS=2  RHS=1  diff=1")

    o = h.drive(xpure.t_recur_verify,
                ["v+u", "((1+sqrt(5))/2)^n/sqrt(5)-((1-sqrt(5))/2)^n/sqrt(5)"],
                [1])
    h.has("Binet satisfies Fibonacci", o, "SATISFIES")

    o = h.drive(xpure.t_recur_verify, [], [-1])
    h.check("verify backs out of its menu", len(o), 0)


def test_recur_behave(h):
    import xpure

    o = h.drive(xpure.t_recur_behave, ["0.5u+3", "0"])
    h.has("convergent sequence", o, "CONVERGENT: u(n) -> 6")
    h.has("increasing", o, "INCREASING")
    h.has("fixed point 6 attracts", o, "ATTRACTING")
    h.num("gradient at the fixed point", o, "f'= ", 0.5)
    h.has("second term", o, "u(1) = 3")
    h.has("third term", o, "u(2) = 4.5")

    o = h.drive(xpure.t_recur_behave, ["0.5u", "8"])
    h.has("decreasing to zero", o, "CONVERGENT: u(n) -> 0")
    h.has("decreasing", o, "DECREASING")

    o = h.drive(xpure.t_recur_behave, ["2u", "1"])
    h.has("divergent sequence", o, "DIVERGENT")
    h.has("fixed point 0 repels", o, "REPELLING")
    h.has("doubling terms", o, "u(10) = 1024")

    o = h.drive(xpure.t_recur_behave, ["-u", "3"])
    h.has("periodic sequence", o, "PERIODIC with period 2")
    h.has("oscillating", o, "OSCILLATES")
    h.has("borderline fixed point", o, "the test decides nothing")

    o = h.drive(xpure.t_recur_behave, ["sqrt(u+6)", "0"])
    h.has("surd iteration converges", o, "CONVERGENT: u(n) -> 3")
    h.num("gradient 1/6 at the limit", o, "f'= ", 1.0 / 6.0, 1e-3)
    h.has("surd iteration attracts", o, "ATTRACTING")

    o = h.drive(xpure.t_recur_behave, ["3.2u(1-u)", "0.2"])
    h.has("logistic 2-cycle", o, "PERIODIC with period 2")
    h.has("logistic fixed point", o, "u = 0.6875")
    h.num("logistic gradient", o, "f'= ", -1.2, 1e-3)
    h.has("logistic fixed point repels", o, "REPELLING")


def test_sets(h):
    import xpure

    o = h.drive(xpure.t_sets, ["1 2 3 4 5 6", "1 2 3", "3 4 5", "2 3 4"])
    h.has("union", o, "A u B = {1, 2, 3, 4, 5}")
    h.has("intersection", o, "A n B = {3}")
    h.has("complement of A", o, "A' = {4, 5, 6}")
    h.has("complement of B", o, "B' = {1, 2, 6}")
    h.has("difference", o, "A \\ B = {1, 2}")
    h.has("reverse difference", o, "B \\ A = {4, 5}")
    h.has("symmetric difference", o, "A (+) B = {1, 2, 4, 5}")
    h.has("cardinality of A", o, "|A| = 3")
    h.has("inclusion-exclusion", o, "3 + 3 - 1 = 5")
    h.has("inclusion-exclusion agrees", o, "(agrees)")
    h.has("A is not a subset of B", o, "A c B: no")
    h.has("A does not equal B", o, "A = B: no")
    h.has("power set size", o, "|P(A)| = 2^3 = 8")
    h.has("de Morgan for the union", o, "(A u B)' = {6}")
    h.has("de Morgan right hand side", o, "A' n B'  = {6}")
    h.has("de Morgan for the intersection", o, "(A n B)' = {1, 2, 4, 5, 6}")
    h.has("three-set union", o, "A u B u C = {1, 2, 3, 4, 5}")
    h.has("three-set intersection", o, "A n B n C = {3}")
    h.has("distributive law", o, "(A u B) n C = {2, 3, 4}")
    h.has("notation is explained", o, "union: in A or B or both")

    o = h.drive(xpure.t_sets, ["1 2 3 4", "1 2", "1 2 3", None])
    h.has("subset detected", o, "A c B: YES")
    h.has("superset not detected", o, "B c A: no")
    h.has("empty difference", o, "A \\ B = { }")
    h.has("power set of a pair", o, "|P(A)| = 2^2 = 4")
    h.has("power set listed", o, "P(A) = { { }, {1}, {2}, {1, 2} }")

    o = h.drive(xpure.t_sets, ["1 2 3 4", "1 2", "3 4", None])
    h.has("disjoint sets", o, "A and B disjoint (A n B = { }): YES")
    h.has("empty intersection", o, "A n B = { }")

    o = h.drive(xpure.t_sets, ["1 2 3", "3 1 1 2", "1", None])
    h.has("repeats dropped", o, "A = {1, 2, 3}   |A| = 3")
    h.has("subset of a bigger set", o, "B c A: YES")


def test_subgroups(h):
    import xpure

    klein = ["4", "0 1 2 3", "1 0 3 2", "2 3 0 1", "3 2 1 0"]
    o = h.drive(xpure.t_subgroups, klein)
    h.has("Klein identity", o, "|G| = 4, identity e = 0")
    h.has("Klein <1>", o, "<1> = {0, 1}   order 2")
    h.has("Klein <2>", o, "<2> = {0, 2}   order 2")
    h.has("Klein <3>", o, "<3> = {0, 3}   order 2")
    h.has("Klein has five subgroups", o, "ALL SUBGROUPS H <= G: 5 of them")
    h.has("Klein has three of order 2", o, "subgroups of order 2: 3  (4/2 = 2)")
    h.has("Klein trivial subgroup", o, "subgroups of order 1: 1")
    h.has("Klein whole group", o, "subgroups of order 4: 1")
    h.has("Lagrange holds for Klein", o, "every |H| divides |G| = 4: YES")
    h.has("Klein is elementary abelian", o, "Every element is its own inverse")
    h.has("index printed", o, "{0, 1}   |H| = 2,  [G:H] = 2")
    h.truthy("Klein has no element of order 4",
             not [ln for ln in o if "ord(" in ln and ") = 4" in ln])

    z4 = ["4", "0 1 2 3", "1 2 3 0", "2 3 0 1", "3 0 1 2"]
    o = h.drive(xpure.t_subgroups, z4)
    h.has("Z4 generator", o, "<1> = {0, 1, 2, 3}   order 4")
    h.has("Z4 element of order 2", o, "<2> = {0, 2}   order 2")
    h.has("Z4 has three subgroups", o, "ALL SUBGROUPS H <= G: 3 of them")
    h.has("Z4 has one subgroup of order 2",
          o, "subgroups of order 2: 1  (4/2 = 2)")
    h.has("Lagrange holds for Z4", o, "every |H| divides |G| = 4: YES")

    z6 = ["6", "0 1 2 3 4 5", "1 2 3 4 5 0", "2 3 4 5 0 1",
          "3 4 5 0 1 2", "4 5 0 1 2 3", "5 0 1 2 3 4"]
    o = h.drive(xpure.t_subgroups, z6)
    h.has("Z6 has four subgroups", o, "ALL SUBGROUPS H <= G: 4 of them")
    h.has("Z6 subgroup of order 3", o, "{0, 2, 4}   |H| = 3,  [G:H] = 2")
    h.has("Z6 subgroup of order 2", o, "{0, 3}   |H| = 2,  [G:H] = 3")
    h.has("Z6 element of order 6", o, "ord(1) = 6")
    h.has("Z6 element of order 3", o, "ord(2) = 3")
    h.has("Z6 divisors", o, "divisors of 6: 1 2 3 6")
    h.has("Lagrange holds for Z6", o, "every |H| divides |G| = 6: YES")

    o = h.drive(xpure.t_subgroups, ["2", "0 0", "0 0"])
    h.has("no identity is refused", o, "no two-sided")
    o = h.drive(xpure.t_subgroups, ["3", "0 1 2", "1 2 0"])
    h.has("a short table is refused", o, "Each row needs 3 entries,")


def _s3_table():
    perms = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                if a != b and b != c and a != c:
                    perms.append((a, b, c))
    T = []
    for p in perms:
        row = []
        for q in perms:
            row.append(perms.index(tuple([p[q[i]] for i in range(3)])))
        T.append(row)
    return T


def _relabel(T, tau):
    n = len(T)
    inv = [0] * n
    for k in range(n):
        inv[tau[k]] = k
    return [[inv[T[tau[i]][tau[j]]] for j in range(n)] for i in range(n)]


def _rows(T):
    return [' '.join([str(v) for v in row]) for row in T]


def test_isomorphism(h):
    import xpure

    z4 = [[0, 1, 2, 3], [1, 2, 3, 0], [2, 3, 0, 1], [3, 0, 1, 2]]
    z4b = _relabel(z4, [0, 2, 1, 3])
    o = h.drive(xpure.t_isomorph, ["4"] + _rows(z4) + _rows(z4b))
    h.has("relabelled Z4 is isomorphic", o, "ISOMORPHIC")
    h.has("isomorphism verified", o, "mismatches = 0")
    h.has("order 2 goes to order 2", o, "2 -> 1")
    h.has("identity goes to identity", o, "0 -> 0")
    h.has("all products checked", o, "for all 16 products")

    klein = [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]]
    o = h.drive(xpure.t_isomorph, ["4"] + _rows(z4) + _rows(klein))
    h.has("Z4 is not Klein", o, "NOT isomorphic")
    h.has("orders of Z4", o, "element orders in G: 1 4 2 4")
    h.has("orders of Klein", o, "element orders in H: 1 2 2 2")

    s3 = _s3_table()
    s3b = _relabel(s3, [3, 0, 5, 2, 4, 1])
    o = h.drive(xpure.t_isomorph, ["6"] + _rows(s3) + _rows(s3b))
    h.has("relabelled S3 is isomorphic", o, "ISOMORPHIC")
    h.has("S3 isomorphism verified", o, "mismatches = 0")
    h.has("S3 products checked", o, "for all 36 products")

    v8 = [[i ^ j for j in range(8)] for i in range(8)]
    v8b = _relabel(v8, [0, 1, 2, 4, 3, 5, 6, 7])
    o = h.drive(xpure.t_isomorph, ["8"] + _rows(v8) + _rows(v8b))
    h.has("relabelled 2x2x2 is isomorphic", o, "ISOMORPHIC")
    h.has("2x2x2 isomorphism verified", o, "mismatches = 0")
    h.has("2x2x2 products checked", o, "for all 64 products")

    z6 = [[(i + j) % 6 for j in range(6)] for i in range(6)]
    o = h.drive(xpure.t_isomorph, ["6"] + _rows(s3) + _rows(z6))
    h.has("S3 is not Z6", o, "NOT isomorphic")


def test_contours(h):
    import xpure

    o = h.drive(xpure.t_contours, ["x^2+y^2", "-3", "3", "-3", "3"])
    h.has("z range of a paraboloid", o, "z runs from 0 to 18")
    h.has("contour levels", o, "contour levels: 3, 6, 9, 12, 15")
    h.has("sections chosen", o, "sections drawn at y = -1.5, 0, 1.5")
    h.has("section at the far left", o, "x = -3   z = 9")
    h.has("section at the centre", o, "x = 0   z = 0")
    h.has("contours explained", o, "Closed contours around a point")

    o = h.drive(xpure.t_contours, ["x^2-y^2", "-3", "3", "-3", "3"])
    h.has("z range of a saddle", o, "z runs from -9 to 9")
    h.has("saddle levels", o, "contour levels: -6, -3, 0, 3, 6")

    o = h.drive(xpure.t_contours, ["2x+3y", "0", "1", "0", "1"])
    h.has("z range of a plane", o, "z runs from 0 to 5")

    o = h.drive(xpure.t_contours, ["7", "-1", "1", "-1", "1"])
    h.has("constant surface", o, "z is constant here")


SECTIONS = [
    ("Y435 first order non-homogeneous recurrences", test_recur_nonhom),
    ("Y435 second order non-homogeneous recurrences", test_recur_nonhom2),
    ("Y435 verifying a recurrence solution", test_recur_verify),
    ("Y435 behaviour of a recurrence", test_recur_behave),
    ("Y435 set notation", test_sets),
    ("Y435 subgroups and Lagrange", test_subgroups),
    ("Y435 group isomorphism", test_isomorphism),
    ("Y435 contours and sections", test_contours),
]
