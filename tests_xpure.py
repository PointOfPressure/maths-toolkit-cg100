# tests_xpure.py - correctness tests for the Extra Pure (Y435) tools added to
# xpure.py: the non-homogeneous recurrence solvers, the solution verifier, the
# sequence-behaviour classifier, set notation, subgroups and Lagrange, group
# isomorphism, and contours and sections of a surface.
#
# Every expected value below was worked out by hand and the working is in the
# comment above it. Where a tool prints a closed form, the table it prints is
# also checked term by term against the recurrence re-run independently here,
# which is the assertion that actually matters: a closed form that reproduces
# the sequence is right whatever it looks like.
#
# tests.py picks this file up automatically and passes in the harness.

import math


def _table(out):
    # the "n=..  u=..  closed=.." rows the recurrence tools print
    rows = []
    for ln in out:
        if ln.startswith('n=') and ' u=' in ln and ' closed=' in ln:
            n = ln.split('n=')[1].split(' ')[0]
            u = ln.split(' u=')[1].split(' ')[0]
            c = ln.split(' closed=')[1].split(' ')[0]
            rows.append((int(n), float(u), float(c)))
    return rows


def _seq1(a, f, u0, terms):
    # u(n+1) = a u(n) + f(n), iterated here rather than read off the screen
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


# ------------------------------------------------------------------ s5, s6 --
def test_recur_nonhom(h):
    import xpure

    # u(n+1) = 2u(n) + 3, u(0) = 1.
    # Particular: constant C with C = 2C + 3, so C = -3.
    # A + (-3) = 1 gives A = 4, so u(n) = 4*2^n - 3.
    # u(5) = 128 - 3 = 125 and u(10) = 4096 - 3 = 4093.
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

    # u(n+1) = 2u(n) + 1, u(0) = 1: C = 2C + 1 gives C = -1, A = 2, so
    # u(n) = 2*2^n - 1 = 2^(n+1) - 1 and u(5) = 63.
    o = h.drive(xpure.t_recur_nonhom, ["2", "1", "1"])
    h.has("2u+1 closed form", o, "u(n) = 2*2^n - 1")
    h.has("2u+1 at n=5", o, "n=5  u=63  closed=63")
    _check_table(h, "2u+1", o, _seq1(2.0, lambda n: 1.0, 1.0, 11))

    # THE RESONANT CASE. u(n+1) = 2u(n) + 3*2^n, u(0) = 1. C*2^n is already a
    # solution of u(n+1) = 2u(n), so the trial term must be C n 2^n:
    #   C(n+1)2^(n+1) - 2C n 2^n = C 2^(n+1) = 2C 2^n, so 2C = 3, C = 1.5.
    # A = 1 - 0 = 1, so u(n) = 2^n + 1.5 n 2^n.
    # u(3) = 8 + 1.5*3*8 = 44 and u(10) = 1024 + 1.5*10*1024 = 16384.
    o = h.drive(xpure.t_recur_nonhom, ["2", "3*2^n", "1"])
    h.has("resonance spotted", o, "RESONANCE")
    h.has("resonant trial carries n", o, "trial p(n) = C n 2^n")
    h.has("resonant particular", o, "p(n) = 1.5*n*2^n")
    h.has("resonant closed form", o, "u(n) = 2^n + 1.5*n*2^n")
    h.has("resonant at n=3", o, "n=3  u=44  closed=44")
    h.has("resonant at n=10", o, "n=10  u=16384  closed=16384")
    _check_table(h, "3*2^n", o,
                 _seq1(2.0, lambda n: 3.0 * 2.0 ** n, 1.0, 11))

    # Without the extra n the answer is wrong, so check the tool does not just
    # print C 2^n: 1.5*2^n would give u(1) = 2*1.5*2 = 6, not 5.
    h.truthy("resonant answer is not the naive C 2^n",
             "u(n) = 2^n + 1.5*2^n" not in o)

    # a = 1 is resonance for a polynomial too: u(n+1) = u(n) + n, u(0) = 0 is
    # the triangular numbers, u(n) = n(n-1)/2 = 0.5n^2 - 0.5n, u(10) = 45.
    o = h.drive(xpure.t_recur_nonhom, ["1", "n", "0"])
    h.has("a=1 is resonant for a polynomial", o, "RESONANCE")
    h.has("triangular numbers", o, "u(n) = 0.5*n^2 - 0.5*n")
    h.has("triangular at n=10", o, "n=10  u=45  closed=45")
    _check_table(h, "u+n", o, _seq1(1.0, lambda n: float(n), 0.0, 11))

    # A quadratic forcing term with no resonance. u(n+1) = 3u(n) + n^2,
    # u(0) = 0. Try p = -(n^2 + n + 1)/2:
    #   p(n+1) - 3p(n) = -((n+1)^2+(n+1)+1)/2 + 3(n^2+n+1)/2
    #                  = (-(n^2+3n+3) + 3n^2+3n+3)/2 = n^2.
    # A = 0 - p(0) = 0.5, so u(n) = 0.5*3^n - 0.5n^2 - 0.5n - 0.5 and
    # u(5) = 121.5 - 12.5 - 2.5 - 0.5 = 106.
    o = h.drive(xpure.t_recur_nonhom, ["3", "n^2", "0"])
    h.has("quadratic forcing named", o, "f(n) is a polynomial of degree 2.")
    h.has("quadratic trial", o, "trial p(n) = (C0 + C1 n + C2 n^2)")
    h.has("quadratic particular", o, "p(n) = -0.5*n^2 - 0.5*n - 0.5")
    h.has("quadratic at n=5", o, "n=5  u=106  closed=106")
    _check_table(h, "3u+n^2", o,
                 _seq1(3.0, lambda n: float(n) * n, 0.0, 11))

    # s5, the homogeneous first order case: u(n+1) = 0.5u(n), u(0) = 8, so
    # u(n) = 8*0.5^n and u(3) = 1.
    o = h.drive(xpure.t_recur_nonhom, ["0.5", "0", "8"])
    h.has("homogeneous first order", o, "u(n) = 8*0.5^n")
    h.has("halving at n=3", o, "n=3  u=1  closed=1")
    _check_table(h, "0.5u", o, _seq1(0.5, lambda n: 0.0, 8.0, 11))

    # Resonance with a negative base: u(n+1) = -u(n) + (-1)^n, u(0) = 1.
    # b = a = -1, so the trial term is C n (-1)^n:
    #   C(n+1)(-1)^(n+1) + C n (-1)^n = C(-1)^n(-(n+1)+n) = -C(-1)^n,
    # so -C = 1 and C = -1. A = 1, u(n) = (-1)^n - n(-1)^n = (1-n)(-1)^n.
    # u(4) = (1-4)(1) = -3.
    o = h.drive(xpure.t_recur_nonhom, ["-1", "(-1)^n", "1"])
    h.has("negative base resonance", o, "RESONANCE")
    h.has("negative base closed form", o, "u(n) = (-1)^n - n*(-1)^n")
    h.has("negative base at n=4", o, "n=4  u=-3  closed=-3")
    _check_table(h, "-u+(-1)^n", o,
                 _seq1(-1.0, lambda n: (-1.0) ** n, 1.0, 11))

    # A first term that is not u(0): u(n+1) = 2u(n) + 3 with u(2) = 13 is the
    # same sequence as the first case, so A is still 4.
    o = h.drive(xpure.t_recur_nonhom, ["2", "3", "13", "2"])
    h.has("indexing from n0 = 2", o, "u(2) = 13 fixes A = 4")
    h.has("n0 = 2 closed form", o, "u(n) = 4*2^n - 3")
    h.has("n0 = 2 starts at n=2", o, "n=2  u=13  closed=13")

    # f(n) outside the standard shapes falls back to the summation form rather
    # than inventing a closed form. sin(n) is not P(n) b^n.
    o = h.drive(xpure.t_recur_nonhom, ["2", "sin(n)", "0"])
    h.has("unrecognised forcing is admitted", o, "not a constant, a")
    h.has("summation form offered", o, "sum a^(n-1-k) f(k)")
    h.truthy("no closed form is claimed for sin(n)",
             not [ln for ln in o if ln.startswith("u(n) = ")])

    # a letter the tool does not bind is refused rather than read as x = 0
    o = h.drive(xpure.t_recur_nonhom, ["2", "t^2", "1"])
    h.has("an unknown letter is refused", o, 'uses the letter "t"')


# ------------------------------------------------------------------ s7, s8 --
def test_recur_nonhom2(h):
    import xpure

    # Fibonacci: u(n+2) = u(n+1) + u(n), u(0) = u(1) = 1, so the terms are
    # 1 1 2 3 5 8 13 21 34 55 89 and u(10) = 89. The auxiliary equation is
    # x^2 - x - 1 = 0 with roots (1 +/- sqrt5)/2 = 1.618 and -0.618.
    o = h.drive(xpure.t_recur_nonhom2, ["1", "1", "0", "1", "1"])
    h.has("Fibonacci closed form", o, "u(n) = ")
    h.has("Fibonacci golden ratio", o, "r1 = 1.618")
    h.has("Fibonacci second root", o, "r2 = -0.618")
    h.has("Fibonacci u(10) = 89", o, "n=10  u=89  closed=89")
    h.has("Fibonacci u(5) = 8", o, "n=5  u=8  closed=8")
    _check_table(h, "Fibonacci", o,
                 _seq2(1.0, 1.0, lambda n: 0.0, 1.0, 1.0, 11))
    # A = (1+sqrt5)/(2 sqrt5) = 0.7236 and B = 1 - A = 0.2764 for u0 = u1 = 1
    h.num("Fibonacci constant A", o, "A = ", 0.723607, 1e-4)

    # u(n+2) = 3u(n+1) - 2u(n) + 1, u(0) = u(1) = 0. Auxiliary x^2 - 3x + 2 = 0
    # has roots 2 and 1; the forcing constant matches the root 1, so the trial
    # solution is C n: (n+2) - 3(n+1) + 2n = -1, so C = -1 and p(n) = -n.
    # A + B = 0 and 2A + B - 1 = 0 give A = 1, B = -1: u(n) = 2^n - 1 - n.
    # u(4) = 16 - 1 - 4 = 11 and u(10) = 1024 - 1 - 10 = 1013.
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

    # REPEATED ROOT. u(n+2) = 4u(n+1) - 4u(n), u(0) = 1, u(1) = 4.
    # x^2 - 4x + 4 = (x-2)^2, so the CF is (A + Bn)2^n. A = 1 and
    # (1+B)2 = 4 gives B = 1, so u(n) = (1+n)2^n.
    # u(5) = 6*32 = 192 and u(10) = 11*1024 = 11264.
    o = h.drive(xpure.t_recur_nonhom2, ["4", "-4", "0", "1", "4"])
    h.has("repeated root found", o, "repeated root r = 2")
    h.has("repeated root CF", o, "CF = (A + B n)(2)^n")
    h.has("repeated root closed form", o, "u(n) = 2^n + n*2^n")
    h.has("repeated root at n=5", o, "n=5  u=192  closed=192")
    h.has("repeated root at n=10", o, "n=10  u=11264  closed=11264")
    _check_table(h, "repeated root", o,
                 _seq2(4.0, -4.0, lambda n: 0.0, 1.0, 4.0, 11))

    # COMPLEX ROOTS. u(n+2) = -u(n), u(0) = 1, u(1) = 0: x^2 + 1 = 0 with
    # roots +/- i, modulus 1 and argument pi/2 = 1.5708. u(n) = cos(n pi/2),
    # so the sequence is 1 0 -1 0 1 ... and u(10) = cos(5 pi) = -1.
    o = h.drive(xpure.t_recur_nonhom2, ["0", "-1", "0", "1", "0"])
    h.has("complex roots reported", o, "complex roots")
    h.has("modulus is 1", o, "modulus R = 1")
    h.num("argument is pi/2", o, "argument t = ", math.pi / 2.0, 1e-3)
    h.has("complex closed form", o, "u(n) = cos(1.5708n)")
    h.has("complex at n=10", o, "n=10  u=-1  closed=-1")
    _check_table(h, "u(n+2)=-u(n)", o,
                 _seq2(0.0, -1.0, lambda n: 0.0, 1.0, 0.0, 11))

    # Complex roots on the unit circle with a period of 6.
    # u(n+2) = u(n+1) - u(n), u(0) = 2, u(1) = 1: roots 0.5 +/- 0.866i,
    # modulus 1, argument pi/3, so u(n) = 2 cos(n pi/3) and u(10) = -1.
    o = h.drive(xpure.t_recur_nonhom2, ["1", "-1", "0", "2", "1"])
    h.num("argument is pi/3", o, "argument t = ", math.pi / 3.0, 1e-3)
    h.has("period six closed form", o, "u(n) = 2*cos(1.0472n)")
    _check_table(h, "period six", o,
                 _seq2(1.0, -1.0, lambda n: 0.0, 2.0, 1.0, 11))

    # An exponential forcing term that resonates with one root.
    # u(n+2) = 3u(n+1) - 2u(n) + 2^n, u(0) = u(1) = 0. 2 is a root, so the
    # trial term is C n 2^n: C[(n+2)2^(n+2) - 3(n+1)2^(n+1) + 2n 2^n]
    # = C 2^n[4n + 8 - 6n - 6 + 2n] = 2C 2^n, so C = 0.5.
    # A + B = 0 and 2A + B + 1 = 0 give A = -1, B = 1:
    # u(n) = 1 - 2^n + 0.5 n 2^n, and u(10) = 1 - 1024 + 5120 = 4097.
    o = h.drive(xpure.t_recur_nonhom2, ["3", "-2", "2^n", "0", "0"])
    h.has("exponential resonance", o, "RESONANCE")
    h.has("exponential resonant trial", o, "trial p(n) = C n 2^n")
    h.has("exponential particular", o, "p(n) = 0.5*n*2^n")
    h.has("exponential at n=10", o, "n=10  u=4097  closed=4097")
    _check_table(h, "3u-2u+2^n", o,
                 _seq2(3.0, -2.0, lambda n: 2.0 ** n, 0.0, 0.0, 11))

    # A first term that is not u(0): the Fibonacci numbers from u(1) = 1,
    # u(2) = 2 run 1 2 3 5 8 13 21 34 55 89 144, so the row at n = 10 is 89.
    o = h.drive(xpure.t_recur_nonhom2, ["1", "1", "0", "1", "2", "1"])
    h.has("2nd order from n0 = 1", o, "n=1  u=1  closed=1")
    h.has("2nd order n0 = 1 at n=10", o, "n=10  u=89  closed=89")


# ---------------------------------------------------------------------- s4 --
def test_recur_verify(h):
    import xpure

    # u(n+1) = 2u(n) + 1 with u(n) = 2^(n+1) - 1:
    #   LHS = 2^(n+2) - 1, RHS = 2(2^(n+1) - 1) + 1 = 2^(n+2) - 1. It holds.
    # At n = 0: LHS = u(1) = 3 and RHS = 2*1 + 1 = 3.
    o = h.drive(xpure.t_recur_verify, ["2u+1", "2^(n+1)-1"], [0])
    h.has("verified solution", o, "SATISFIES")
    h.has("verify at n=0", o, "n=0  LHS=3  RHS=3  diff=0")
    h.has("verify at n=5", o, "n=5  LHS=127  RHS=127  diff=0")
    h.has("verify shows the substitution", o, "substituting the candidate")

    # The same recurrence with u(n) = 2^n, which is the solution of the
    # HOMOGENEOUS equation and is out by exactly 1 at every step.
    o = h.drive(xpure.t_recur_verify, ["2u+1", "2^n"], [0])
    h.has("rejected solution", o, "does NOT")
    h.has("rejection at n=0", o, "n=0  LHS=2  RHS=3  diff=1")

    # Second order: u(n+2) = 3u(n+1) - 2u(n) with u(n) = 2^n.
    #   LHS = 2^(n+2) = 4*2^n, RHS = 3*2^(n+1) - 2*2^n = 6*2^n - 2*2^n. Holds.
    o = h.drive(xpure.t_recur_verify, ["3v-2u", "2^n"], [1])
    h.has("2nd order verification", o, "SATISFIES")
    h.has("2nd order verify at n=0", o, "n=0  LHS=4  RHS=4  diff=0")

    # u(n+2) = u(n+1) + u(n) with u(n) = n, which fails: n+2 is not
    # (n+1) + n = 2n+1 except at n = 1.
    o = h.drive(xpure.t_recur_verify, ["v+u", "n"], [1])
    h.has("2nd order rejection", o, "does NOT")
    h.has("2nd order rejection at n=0", o, "n=0  LHS=2  RHS=1  diff=1")

    # Binet's formula really does solve the Fibonacci recurrence, and the
    # numeric check is the only way this toolkit can see that.
    o = h.drive(xpure.t_recur_verify,
                ["v+u", "((1+sqrt(5))/2)^n/sqrt(5)-((1-sqrt(5))/2)^n/sqrt(5)"],
                [1])
    h.has("Binet satisfies Fibonacci", o, "SATISFIES")

    # cancelling out of the menu does nothing at all
    o = h.drive(xpure.t_recur_verify, [], [-1])
    h.check("verify backs out of its menu", len(o), 0)


# -------------------------------------------------------------- s2, s3, s9 --
def test_recur_behave(h):
    import xpure

    # u(n+1) = 0.5u(n) + 3 from u(0) = 0. The fixed point is L = 0.5L + 3,
    # so L = 6, and f'(u) = 0.5 everywhere, so it attracts. The terms
    # 0, 3, 4.5, 5.25, ... climb to 6 from below.
    o = h.drive(xpure.t_recur_behave, ["0.5u+3", "0"])
    h.has("convergent sequence", o, "CONVERGENT: u(n) -> 6")
    h.has("increasing", o, "INCREASING")
    h.has("fixed point 6 attracts", o, "ATTRACTING")
    h.num("gradient at the fixed point", o, "f'= ", 0.5)
    h.has("second term", o, "u(1) = 3")
    h.has("third term", o, "u(2) = 4.5")

    # u(n+1) = 0.5u(n) from u(0) = 8 falls 8, 4, 2, 1, ... to 0.
    o = h.drive(xpure.t_recur_behave, ["0.5u", "8"])
    h.has("decreasing to zero", o, "CONVERGENT: u(n) -> 0")
    h.has("decreasing", o, "DECREASING")

    # u(n+1) = 2u(n) from u(0) = 1 doubles for ever; the fixed point 0 has
    # f' = 2, so it repels.
    o = h.drive(xpure.t_recur_behave, ["2u", "1"])
    h.has("divergent sequence", o, "DIVERGENT")
    h.has("fixed point 0 repels", o, "REPELLING")
    h.has("doubling terms", o, "u(10) = 1024")

    # u(n+1) = -u(n) from u(0) = 3 is 3, -3, 3, ...: period 2, oscillating,
    # with f' = -1 at the fixed point 0, which the linear test cannot decide.
    o = h.drive(xpure.t_recur_behave, ["-u", "3"])
    h.has("periodic sequence", o, "PERIODIC with period 2")
    h.has("oscillating", o, "OSCILLATES")
    h.has("borderline fixed point", o, "the test decides nothing")

    # u(n+1) = sqrt(u(n) + 6) from 0. L = sqrt(L+6) gives L^2 - L - 6 = 0,
    # so L = 3 (the root -2 is outside the range of a square root).
    # f'(u) = 1/(2 sqrt(u+6)), and at u = 3 that is 1/6 = 0.1667.
    o = h.drive(xpure.t_recur_behave, ["sqrt(u+6)", "0"])
    h.has("surd iteration converges", o, "CONVERGENT: u(n) -> 3")
    h.num("gradient 1/6 at the limit", o, "f'= ", 1.0 / 6.0, 1e-3)
    h.has("surd iteration attracts", o, "ATTRACTING")

    # The logistic map at r = 3.2 from 0.2. The non-zero fixed point is
    # 1 - 1/r = 0.6875 with f'(u) = r - 2ru, so f'(0.6875) = 3.2 - 4.4 = -1.2:
    # it repels, and the sequence settles into a 2-cycle instead.
    o = h.drive(xpure.t_recur_behave, ["3.2u(1-u)", "0.2"])
    h.has("logistic 2-cycle", o, "PERIODIC with period 2")
    h.has("logistic fixed point", o, "u = 0.6875")
    h.num("logistic gradient", o, "f'= ", -1.2, 1e-3)
    h.has("logistic fixed point repels", o, "REPELLING")


# --------------------------------------------------------------------- XS1 --
def test_sets(h):
    import xpure

    # E = {1..6}, A = {1,2,3}, B = {3,4,5}, C = {2,3,4}.
    # A u B = {1,2,3,4,5}, A n B = {3}, A' = {4,5,6}, B' = {1,2,6},
    # A \ B = {1,2}, B \ A = {4,5}, A (+) B = {1,2,4,5}.
    # |A| + |B| - |A n B| = 3 + 3 - 1 = 5 = |A u B|.
    # (A u B)' = {6} = A' n B' and (A n B)' = {1,2,4,5,6} = A' u B'.
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

    # A = {1,2} inside B = {1,2,3}: A c B is true, A n B = A, A u B = B,
    # A \ B = { } and P(A) has 2^2 = 4 members.
    o = h.drive(xpure.t_sets, ["1 2 3 4", "1 2", "1 2 3", None])
    h.has("subset detected", o, "A c B: YES")
    h.has("superset not detected", o, "B c A: no")
    h.has("empty difference", o, "A \\ B = { }")
    h.has("power set of a pair", o, "|P(A)| = 2^2 = 4")
    h.has("power set listed", o, "P(A) = { { }, {1}, {2}, {1, 2} }")

    # Disjoint sets: A n B is empty and |A u B| = |A| + |B|.
    o = h.drive(xpure.t_sets, ["1 2 3 4", "1 2", "3 4", None])
    h.has("disjoint sets", o, "A and B disjoint (A n B = { }): YES")
    h.has("empty intersection", o, "A n B = { }")

    # Repeats are dropped and order does not matter, so {3,1,1,2} is {1,2,3}.
    o = h.drive(xpure.t_sets, ["1 2 3", "3 1 1 2", "1", None])
    h.has("repeats dropped", o, "A = {1, 2, 3}   |A| = 3")
    h.has("subset of a bigger set", o, "B c A: YES")


# ----------------------------------------------------------------- a5, a6 --
def test_subgroups(h):
    import xpure

    # The Klein four-group, with 0 as the identity and every element its own
    # inverse. Its subgroups are {0}, {0,1}, {0,2}, {0,3} and the whole group:
    # five in all, three of them of order 2, and 2 divides 4.
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
    # Klein has no element of order 4, so no subgroup of order 4 is cyclic
    h.truthy("Klein has no element of order 4",
             not [ln for ln in o if "ord(" in ln and ") = 4" in ln])

    # Z4 = {0,1,2,3} under addition. <1> is the whole group, so Z4 is cyclic,
    # and its only subgroups are {0}, {0,2} and Z4 itself.
    z4 = ["4", "0 1 2 3", "1 2 3 0", "2 3 0 1", "3 0 1 2"]
    o = h.drive(xpure.t_subgroups, z4)
    h.has("Z4 generator", o, "<1> = {0, 1, 2, 3}   order 4")
    h.has("Z4 element of order 2", o, "<2> = {0, 2}   order 2")
    h.has("Z4 has three subgroups", o, "ALL SUBGROUPS H <= G: 3 of them")
    h.has("Z4 has one subgroup of order 2",
          o, "subgroups of order 2: 1  (4/2 = 2)")
    h.has("Lagrange holds for Z4", o, "every |H| divides |G| = 4: YES")

    # Z6 has exactly one subgroup for each divisor of 6: {0}, {0,3},
    # {0,2,4} and the whole group.
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

    # a table with no identity is not a group and is refused. Every entry of
    # this one is 0, so no row is the identity row.
    o = h.drive(xpure.t_subgroups, ["2", "0 0", "0 0"])
    h.has("no identity is refused", o, "no two-sided")
    # a row of the wrong length is refused rather than half-read
    o = h.drive(xpure.t_subgroups, ["3", "0 1 2", "1 2 0"])
    h.has("a short table is refused", o, "Each row needs 3 entries,")


# ---------------------------------------------------------------------- a8 --
def _s3_table():
    # S3 as composition of the six permutations of three letters, built here
    # so the test does not depend on the tool's own arithmetic
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
    # the same group with its elements renamed: H[i][j] = tau^-1(T[tau i][tau j])
    n = len(T)
    inv = [0] * n
    for k in range(n):
        inv[tau[k]] = k
    return [[inv[T[tau[i]][tau[j]]] for j in range(n)] for i in range(n)]


def _rows(T):
    return [' '.join([str(v) for v in row]) for row in T]


def test_isomorphism(h):
    import xpure

    # Z4 and the same group with elements 1 and 2 swapped. An isomorphism has
    # to send the element of order 2 to the element of order 2, so phi must be
    # 0 -> 0, 2 -> 1, and 1 and 3 go to 2 and 3 in some order.
    z4 = [[0, 1, 2, 3], [1, 2, 3, 0], [2, 3, 0, 1], [3, 0, 1, 2]]
    z4b = _relabel(z4, [0, 2, 1, 3])
    o = h.drive(xpure.t_isomorph, ["4"] + _rows(z4) + _rows(z4b))
    h.has("relabelled Z4 is isomorphic", o, "ISOMORPHIC")
    h.has("isomorphism verified", o, "mismatches = 0")
    h.has("order 2 goes to order 2", o, "2 -> 1")
    h.has("identity goes to identity", o, "0 -> 0")
    h.has("all products checked", o, "for all 16 products")

    # Z4 and the Klein four-group are not isomorphic: Z4 has an element of
    # order 4 and every non-identity element of Klein has order 2.
    klein = [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]]
    o = h.drive(xpure.t_isomorph, ["4"] + _rows(z4) + _rows(klein))
    h.has("Z4 is not Klein", o, "NOT isomorphic")
    h.has("orders of Z4", o, "element orders in G: 1 4 2 4")
    h.has("orders of Klein", o, "element orders in H: 1 2 2 2")

    # S3, which is not abelian, against a relabelling of itself. This is the
    # case that needs the search: order alone leaves 2 x 3! = 12 candidates.
    s3 = _s3_table()
    s3b = _relabel(s3, [3, 0, 5, 2, 4, 1])
    o = h.drive(xpure.t_isomorph, ["6"] + _rows(s3) + _rows(s3b))
    h.has("relabelled S3 is isomorphic", o, "ISOMORPHIC")
    h.has("S3 isomorphism verified", o, "mismatches = 0")
    h.has("S3 products checked", o, "for all 36 products")

    # The elementary abelian group of order 8 (bit strings under XOR) against
    # a relabelling of itself. Every non-identity element has order 2, so the
    # order test rules nothing out and all 7! = 5040 bijections are candidates;
    # only 168 of them are isomorphisms, so this is the case that really
    # depends on checking the products as the search goes.
    v8 = [[i ^ j for j in range(8)] for i in range(8)]
    # this relabelling is deliberately not linear over GF(2) - swapping just
    # 3 and 4 - so the identity map is NOT an isomorphism and the search has
    # to find a real one instead of stumbling on it first try
    v8b = _relabel(v8, [0, 1, 2, 4, 3, 5, 6, 7])
    o = h.drive(xpure.t_isomorph, ["8"] + _rows(v8) + _rows(v8b))
    h.has("relabelled 2x2x2 is isomorphic", o, "ISOMORPHIC")
    h.has("2x2x2 isomorphism verified", o, "mismatches = 0")
    h.has("2x2x2 products checked", o, "for all 64 products")

    # S3 and Z6 both have order 6 and are not isomorphic: Z6 is cyclic and S3
    # is not, which shows up in the element orders.
    z6 = [[(i + j) % 6 for j in range(6)] for i in range(6)]
    o = h.drive(xpure.t_isomorph, ["6"] + _rows(s3) + _rows(z6))
    h.has("S3 is not Z6", o, "NOT isomorphic")


# ---------------------------------------------------------------------- c2 --
def test_contours(h):
    import xpure

    # z = x^2 + y^2 on [-3,3] x [-3,3]. The grid includes (0,0), where z = 0,
    # and the corners, where z = 9 + 9 = 18. Five levels evenly spaced inside
    # that range are 0 + 18k/6 for k = 1..5, so 3, 6, 9, 12, 15.
    # The middle section is at y = -3 + 6*2/4 = 0, where z = x^2, so
    # z = 9 at x = -3 and z = 0 at x = 0.
    o = h.drive(xpure.t_contours, ["x^2+y^2", "-3", "3", "-3", "3"])
    h.has("z range of a paraboloid", o, "z runs from 0 to 18")
    h.has("contour levels", o, "contour levels: 3, 6, 9, 12, 15")
    h.has("sections chosen", o, "sections drawn at y = -1.5, 0, 1.5")
    h.has("section at the far left", o, "x = -3   z = 9")
    h.has("section at the centre", o, "x = 0   z = 0")
    h.has("contours explained", o, "Closed contours around a point")

    # z = x^2 - y^2 is the saddle: z runs from -9 (x = 0, y = +/-3) to
    # 9 (y = 0, x = +/-3), so the levels are -9 + 18k/6 = -6, -3, 0, 3, 6.
    o = h.drive(xpure.t_contours, ["x^2-y^2", "-3", "3", "-3", "3"])
    h.has("z range of a saddle", o, "z runs from -9 to 9")
    h.has("saddle levels", o, "contour levels: -6, -3, 0, 3, 6")

    # A plane: z = 2x + 3y over [0,1]^2 runs from 0 to 5.
    o = h.drive(xpure.t_contours, ["2x+3y", "0", "1", "0", "1"])
    h.has("z range of a plane", o, "z runs from 0 to 5")

    # A constant surface has nothing to draw and says so rather than dividing
    # by a zero range.
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
