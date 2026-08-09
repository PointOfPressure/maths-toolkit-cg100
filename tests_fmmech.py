# tests_fmmech.py - correctness tests for the Mechanics Major (Y421) tools
# added to fmmech.py: oblique impact, projectiles beyond level ground, elastic
# strings and springs, centres of mass by calculus, and the smaller items
# (tangential acceleration, couples, the triangle of forces, units, relative
# motion in 2-D).
#
# Every expected value below was worked by hand first and the working is in the
# comment above the assertion. Several checks are deliberately redundant with
# each other - the cone at 3h/4, the semicircular lamina at 4r/(3pi) and the
# hemisphere at 3r/8 are computed twice, once from the standard-bodies table
# and once by integration, so the two routes have to agree.
#
# `h` is the harness object from tests.py: check / close / truthy / raises /
# drive / has / num, plus the engine modules.

import math

SQ2 = math.sqrt(2.0)
SQ3 = math.sqrt(3.0)


# ============================================================ oblique impact =
def test_oblique(h):
    import fmmech

    # A ball of mass 2 kg strikes a smooth wall at 10 m/s at 30 degrees to the
    # SURFACE (so 60 degrees to the normal), e = 0.5.
    #   along the surface: 10 cos30 = 5*sqrt(3) = 8.660254, UNCHANGED (smooth)
    #   normal in        : 10 sin30 = 5
    #   normal out       : e * 5    = 2.5
    #   speed            : sqrt(75 + 6.25) = sqrt(81.25) = 9.013878
    #   angle to surface : arctan(2.5 / 8.660254) = 16.102114 deg
    #   KE lost          : 0.5*2*(100 - 81.25) = 18.75 J
    #   impulse          : m(1+e) * 5 = 2 * 1.5 * 5 = 15 N s
    out = h.drive(fmmech.t_oblique_wall, ["10", "30", "0.5", "2"], [])
    h.num("wall: component along the surface", out, "along surface = ",
          5.0 * SQ3, 1e-4)
    h.num("wall: normal component in", out, "normal in = ", 5.0, 1e-9)
    h.num("wall: NEL on the normal component", out, "normal out = ", 2.5, 1e-9)
    h.num("wall: rebound speed", out, "speed = ", 9.013878, 1e-4)
    h.num("wall: angle to the surface", out, "angle to surface = ",
          16.102114, 1e-4)
    h.num("wall: angle to the normal", out, "angle to normal = ",
          73.897886, 1e-4)
    h.num("wall: KE lost", out, "KE lost = ", 18.75, 1e-6)
    h.num("wall: impulse m(1+e)u_n", out, "impulse = ", 15.0, 1e-6)
    # Mi13: the modelling assumption has to be on the screen, not just in the
    # arithmetic - it is what the specification asks candidates to state.
    h.has("wall: says the surface is smooth", out, "smooth surface")
    h.has("wall: says the tangential part is unchanged", out, "UNCHANGED")

    # Same wall, but the standard textbook phrasing: 30 degrees to the NORMAL,
    # i.e. 60 degrees to the surface. Then tan(rebound to normal)
    #   = tan(30)/e = 0.5773503/0.5 = 1.1547005, so 49.106605 deg,
    # and the speed is sqrt((10cos60)^2 + (0.5*10sin60)^2)
    #   = sqrt(25 + 18.75) = 6.614378.
    out = h.drive(fmmech.t_oblique_wall, ["10", "60", "0.5", None], [])
    h.num("wall: arctan(tan30/e) to the normal", out, "angle to normal = ",
          math.atan(math.tan(math.pi / 6.0) / 0.5) * 180.0 / math.pi, 1e-4)
    h.num("wall: 30 deg to the normal rebound speed", out, "speed = ",
          6.614378, 1e-4)

    # e = 1: perfectly elastic, so the normal component is unchanged too. The
    # speed is unaltered and the ball rebounds at the angle of incidence.
    out = h.drive(fmmech.t_oblique_wall, ["8", "40", "1", "3"], [])
    h.num("wall: e = 1 keeps the speed", out, "speed = ", 8.0, 1e-9)
    h.num("wall: e = 1 reflects the angle", out, "angle to surface = ",
          40.0, 1e-6)
    h.num("wall: e = 1 loses no KE", out, "KE lost = ", 0.0, 1e-9)

    # e = 0: the normal component is destroyed, so the ball slides along the
    # surface at 10cos30 = 8.660254 and all the normal KE is lost:
    # 0.5*2*(10 sin30)^2 = 25 J.
    out = h.drive(fmmech.t_oblique_wall, ["10", "30", "0", "2"], [])
    h.num("wall: e = 0 leaves only the tangential part", out, "speed = ",
          5.0 * SQ3, 1e-4)
    h.num("wall: e = 0 moves along the surface", out, "angle to surface = ",
          0.0, 1e-9)
    h.num("wall: e = 0 KE lost", out, "KE lost = ", 25.0, 1e-6)


def test_oblique_spheres(h):
    import fmmech

    # Two equal smooth spheres, e = 1, DIRECT impact (both angles 0): the
    # standard result is that they exchange velocities.
    out = h.drive(fmmech.t_oblique_spheres,
                  ["1", "4", "0", "1", "0", "0", "1"], [])
    h.num("spheres: equal masses e=1 exchange (v1)", out,
          "v1 along LOC = ", 0.0, 1e-9)
    h.num("spheres: equal masses e=1 exchange (v2)", out,
          "v2 along LOC = ", 4.0, 1e-9)
    h.num("spheres: e = 1 loses no KE", out, "KE lost = ", 0.0, 1e-9)

    # Equal smooth spheres, e = 1, one at rest, the other striking at 45 deg to
    # the line of centres with speed 10:
    #   along LOC   : 10 cos45 = 7.0710678, perpendicular: 10 sin45 = 7.0710678
    #   along the LOC the two equal masses exchange, so v1 = 0, v2 = 7.0710678
    #   sphere 1 keeps only its perpendicular part -> 7.0710678 at 90 deg
    #   sphere 2 moves along the LOC -> 7.0710678 at 0 deg
    # so they separate at right angles, and no KE is lost.
    out = h.drive(fmmech.t_oblique_spheres,
                  ["1", "10", "45", "1", "0", "0", "1"], [])
    h.num("spheres: perpendicular part unchanged", out, "perp 1 = ",
          5.0 * SQ2, 1e-4)
    h.num("spheres: struck sphere takes the LOC part", out,
          "v2 along LOC = ", 5.0 * SQ2, 1e-4)
    h.num("spheres: striker speed after", out, "speed 1 = ", 5.0 * SQ2, 1e-4)
    h.num("spheres: striker turns to 90 deg to the LOC", out, "angle 1 = ",
          90.0, 1e-6)
    h.num("spheres: struck sphere along the LOC", out, "angle 2 = ",
          0.0, 1e-9)
    h.num("spheres: 45 deg elastic loses no KE", out, "KE lost = ", 0.0, 1e-9)
    h.has("spheres: names the smooth assumption", out, "smooth spheres")

    # m1 = 2 at 10 m/s, 60 deg to the LOC, hits m2 = 3 at rest, e = 0.5.
    #   along LOC: u1 = 10cos60 = 5, u2 = 0; perp: 10 sin60 = 8.6602540
    #   momentum  : 2*5 = 10;  separation = 0.5*(5-0) = 2.5
    #   5 v1 = 10 - 3*2.5 = 2.5  ->  v1 = 0.5,  v2 = 0.5 + 2.5 = 3
    #   speed 1   = sqrt(0.25 + 75) = sqrt(75.25) = 8.6746758
    #   angle 1   : tan = 8.6602540/0.5 = 10 sqrt(3), so 86.695695 deg
    #   KE lost   = 0.5*2*(25 - 0.25) + 0.5*3*(0 - 9) = 24.75 - 13.5 = 11.25 J
    out = h.drive(fmmech.t_oblique_spheres,
                  ["2", "10", "60", "3", "0", "0", "0.5"], [])
    h.num("spheres: momentum along the LOC", out, "momentum ", 10.0, 1e-9)
    h.num("spheres: v1 along the LOC", out, "v1 along LOC = ", 0.5, 1e-9)
    h.num("spheres: v2 along the LOC", out, "v2 along LOC = ", 3.0, 1e-9)
    h.num("spheres: speed 1 after", out, "speed 1 = ",
          math.sqrt(75.25), 1e-4)
    h.num("spheres: speed 2 after", out, "speed 2 = ", 3.0, 1e-9)
    h.num("spheres: direction 1 after", out, "angle 1 = ",
          math.atan(10.0 * SQ3) * 180.0 / math.pi, 1e-3)
    h.num("spheres: KE lost", out, "KE lost = ", 11.25, 1e-6)
    # momentum along the LOC must still balance: 2(0.5) + 3(3) = 10
    h.close("spheres: momentum conserved along the LOC",
            2 * 0.5 + 3 * 3.0, 10.0, 1e-9)


# ================================================================ projectiles =
def test_projectile_path(h):
    import fmmech

    # u = 20 at 45 deg, g = 9.8. Eliminating t:
    #   tan45 = 1 and g/(2u^2cos^2 45) = 9.8/(2*400*0.5) = 0.0245
    #   so y = x - 0.0245 x^2
    #   range = tan a / k = 1/0.0245 = 40.816327 (= u^2 sin2a / g = 400/9.8)
    #   max height = u^2 sin^2 a /(2g) = 400*0.5/19.6 = 10.204082
    #   time of flight = 2u sin a / g = 20*sqrt(2)/9.8 = 2.886192
    # At half the range the height must be the maximum height, so evaluating
    # the cartesian equation at x = 400/9.8/2 has to return 10.204082.
    out = h.drive(fmmech.t_proj_path, ["20", "45", "9.8", "400/9.8/2"], [])
    h.num("path: tan a", out, "tan a = ", 1.0, 1e-9)
    h.num("path: x^2 coefficient", out, "g/(2u^2cos^2a) = ", 0.0245, 1e-9)
    h.num("path: range", out, "range = ", 400.0 / 9.8, 1e-4)
    h.num("path: greatest height", out, "max height = ", 200.0 / 19.6, 1e-4)
    h.num("path: time of flight", out, "time of flight = ",
          20.0 * SQ2 / 9.8, 1e-4)
    h.num("path: y at half the range is the max height", out,
          "y(20.4082) = ", 200.0 / 19.6, 1e-3)
    h.has("path: shows the eliminated parameter", out, "t = x/(u cos a)")

    # u = 10 at 30 deg, g = 10 (clean numbers):
    #   tan30 = 0.5773503,  k = 10/(2*100*0.75) = 0.0666667
    #   range = 100 sin60/10 = 5 sqrt(3) = 8.660254
    #   max height = 100*0.25/20 = 1.25,  time of flight = 2*10*0.5/10 = 1
    out = h.drive(fmmech.t_proj_path, ["10", "30", "10", None], [])
    h.num("path: tan 30", out, "tan a = ", 1.0 / SQ3, 1e-4)
    h.num("path: x^2 coefficient at 30 deg", out, "g/(2u^2cos^2a) = ",
          1.0 / 15.0, 1e-3)
    h.num("path: range at 30 deg", out, "range = ", 5.0 * SQ3, 1e-4)
    h.num("path: height at 30 deg", out, "max height = ", 1.25, 1e-9)
    h.num("path: flight time at 30 deg", out, "time of flight = ", 1.0, 1e-9)
    # v4: the bounding (safety) parabola has apex u^2/(2g) = 100/20 = 5
    h.num("path: bounding parabola apex", out, "y = ", 5.0, 1e-9)

    # A vertical launch has no cartesian path: x is identically 0.
    out = h.drive(fmmech.t_proj_path, ["20", "90", "9.8"], [])
    h.has("path: refuses a vertical launch", out, "vertical launch")


def test_projectile_incline(h):
    import fmmech

    # Level ground (b = 0) must reproduce the familiar results:
    #   R = u^2 sin2a / g = 400/9.8 = 40.816327 at a = 45,
    #   best angle 45 deg, max range u^2/g = 40.816327.
    out = h.drive(fmmech.t_proj_incline, ["20", "45", "0", "9.8"], [])
    h.num("incline: level range at 45 deg", out, "range along plane = ",
          400.0 / 9.8, 1e-4)
    h.num("incline: level horizontal range", out, "horizontal range = ",
          400.0 / 9.8, 1e-4)
    h.num("incline: best angle on the level is 45", out, "best angle = ",
          45.0, 1e-9)
    h.num("incline: level max range is u^2/g", out, "max range = ",
          400.0 / 9.8, 1e-4)
    h.num("incline: level flight time", out, "time of flight = ",
          20.0 * SQ2 / 9.8, 1e-4)
    h.has("incline: names the level-ground case", out, "level ground")

    # Up a 30 deg slope at the optimal angle a = 45 + b/2 = 60:
    #   R = 2u^2 cos60 sin30 /(g cos^2 30) = 800*0.25/(9.8*0.75) = 200/7.35
    #     = 27.210884, which must equal R_max = u^2/(g(1+sin30)) = 400/14.7.
    #   time = 2u sin(a-b)/(g cos b) = 40*0.5/(9.8*cos30) = 2.356534
    #   rise along the plane = R sin30 = 13.605442
    out = h.drive(fmmech.t_proj_incline, ["20", "60", "30", "9.8"], [])
    h.num("incline: range up a 30 deg slope", out, "range along plane = ",
          200.0 / 7.35, 1e-4)
    h.num("incline: best angle up a 30 deg slope", out, "best angle = ",
          60.0, 1e-9)
    h.num("incline: max range up a 30 deg slope", out, "max range = ",
          400.0 / 14.7, 1e-4)
    h.num("incline: flight time up the slope", out, "time of flight = ",
          2.356534, 1e-4)
    h.num("incline: rise along the slope", out, "rise along plane = ",
          100.0 / 7.35, 1e-4)
    h.close("incline: firing at the best angle gives the max range",
            200.0 / 7.35, 400.0 / 14.7, 1e-9)

    # Down a 30 deg slope: best angle 45 + b/2 = 30, and
    #   R_max = u^2/(g(1 + sin(-30))) = 400/(9.8*0.5) = 81.632653.
    #   Firing at 30 deg gives R = 800 cos30 sin60/(9.8 cos^2 30)
    #                            = 800*0.75/7.35 = 81.632653 as well,
    #   and time = 2*20 sin60/(9.8 cos30) = 40/9.8 = 4.081633.
    out = h.drive(fmmech.t_proj_incline, ["20", "30", "-30", "9.8"], [])
    h.num("incline: best angle down a 30 deg slope", out, "best angle = ",
          30.0, 1e-9)
    h.num("incline: max range down a 30 deg slope", out, "max range = ",
          800.0 / 9.8, 1e-4)
    h.num("incline: range down the slope at the best angle", out,
          "range along plane = ", 800.0 / 9.8, 1e-4)
    h.num("incline: flight time down the slope", out, "time of flight = ",
          40.0 / 9.8, 1e-4)

    # Fired below the slope: it never travels up the plane at all.
    out = h.drive(fmmech.t_proj_incline, ["20", "20", "30", "9.8"], [])
    h.has("incline: rejects a launch below the slope", out, "need a > b")


# ================================================== elastic strings & springs =
def test_elastic(h):
    import fmmech

    # m = 2 kg on a string of natural length 1 m, modulus 49 N, g = 9.8.
    # Equilibrium: mg = lambda x / l  ->  x = mgl/lambda = 19.6/49 = 0.4 m,
    # T = mg = 19.6 N, total length 1.4 m, EPE = 49*0.16/2 = 3.92 J.
    out = h.drive(fmmech.t_elastic, ["1", "2", "49", "1", "9.8"], [])
    h.num("elastic: equilibrium extension", out, "extension x = ", 0.4, 1e-9)
    h.num("elastic: tension is the weight", out, "tension T = ", 19.6, 1e-9)
    h.num("elastic: total length", out, "total length = ", 1.4, 1e-9)
    h.num("elastic: EPE at equilibrium", out, "EPE there = ", 3.92, 1e-9)

    # Released from rest with the string just taut (v = 0): all the GPE lost
    # becomes EPE, mgx = lambda x^2/(2l), so x = 2mgl/lambda = 0.8 m -
    # exactly twice the equilibrium extension. GPE lost = 2*9.8*0.8 = 15.68 J
    # and EPE = 49*0.64/2 = 15.68 J, which must agree.
    out = h.drive(fmmech.t_elastic, ["2", "2", "49", "1", "0", "9.8"], [])
    h.num("elastic: max extension from rest", out, "max extension x = ",
          0.8, 1e-9)
    h.num("elastic: GPE lost", out, "GPE lost = ", 15.68, 1e-6)
    h.num("elastic: EPE stored equals the GPE lost", out, "EPE stored = ",
          15.68, 1e-6)
    h.num("elastic: no KE at the start", out, "KE at that instant = ",
          0.0, 1e-9)
    h.num("elastic: total length at maximum extension", out,
          "total length = ", 1.8, 1e-9)

    # Same string, but moving at 2.8 m/s when it becomes taut:
    #   0.5*2*2.8^2 + 2*9.8x = 49 x^2/2   ->   x^2 - 0.8x - 0.32 = 0
    #   x = 0.4 + sqrt(0.16 + 0.32) = 0.4 + sqrt(0.48) = 1.0928203
    #   KE 7.84 + GPE 21.4192783 = 29.2592783 = EPE 24.5 x^2
    out = h.drive(fmmech.t_elastic, ["2", "2", "49", "1", "2.8", "9.8"], [])
    h.num("elastic: max extension with initial KE", out,
          "max extension x = ", 0.4 + math.sqrt(0.48), 1e-4)
    h.num("elastic: initial KE", out, "KE at that instant = ", 7.84, 1e-6)
    h.num("elastic: energy equation balances", out, "EPE stored = ",
          7.84 + 19.6 * (0.4 + math.sqrt(0.48)), 1e-3)

    # Inverting the equilibrium relation: lambda = mgl/x = 19.6/0.4 = 49 N,
    # stiffness k = lambda/l = 49 N/m.
    out = h.drive(fmmech.t_elastic, ["3", "2", "1", "0.4", "9.8"], [])
    h.num("elastic: modulus from the extension", out, "lambda = ", 49.0, 1e-6)
    h.num("elastic: stiffness", out, "stiffness k = lam/l = ", 49.0, 1e-6)


# =================================================== centre of mass, calculus =
def test_com_calculus(h):
    import fmmech

    # Uniform lamina under y = x^2 from 0 to 1:
    #   A = int x^2 dx = 1/3
    #   x_bar = int x^3 dx / A = (1/4)/(1/3) = 0.75
    #   y_bar = int x^4/2 dx / A = (1/10)/(1/3) = 0.3
    out = h.drive(fmmech.t_com_calculus, ["1", "x^2", "0", "1"], [])
    h.num("lamina: area under x^2", out, "area A = ", 1.0 / 3.0, 1e-3)
    h.num("lamina: x_bar under x^2", out, "x_bar = ", 0.75, 1e-6)
    h.num("lamina: y_bar under x^2", out, "y_bar = ", 0.3, 1e-6)

    # Semicircular lamina, y = sqrt(1-x^2) from -1 to 1:
    #   A = pi/2 = 1.5707963
    #   x_bar = 0 by symmetry
    #   y_bar = int (1-x^2)/2 dx / A = (2/3)/(pi/2) = 4/(3pi) = 0.4244132
    # This is the standard 4r/(3pi) result, reached by integration.
    out = h.drive(fmmech.t_com_calculus, ["1", "sqrt(1-x^2)", "-1", "1"], [])
    h.num("lamina: area of a unit semicircle", out, "area A = ",
          math.pi / 2.0, 1e-3)
    h.num("lamina: semicircle x_bar is zero", out, "x_bar = ", 0.0, 1e-6)
    h.num("lamina: semicircle y_bar is 4r/(3pi)", out, "y_bar = ",
          4.0 / (3.0 * math.pi), 1e-3)

    # Solid cone: y = x from 0 to 1 rotated about Ox.
    #   V = pi int x^2 dx = pi/3 = 1.0471976 (= pi r^2 h/3 with r = h = 1)
    #   x_bar = int x^3 dx / int x^2 dx = (1/4)/(1/3) = 0.75 = 3h/4 from apex
    out = h.drive(fmmech.t_com_calculus, ["2", "x", "0", "1"], [])
    h.num("solid: volume of a unit cone", out, "volume V = ",
          math.pi / 3.0, 1e-4)
    h.num("solid: cone COM is 3h/4 from the apex", out, "x_bar = ",
          0.75, 1e-6)

    # A cone of base radius 2 and height 4: y = x/2 from 0 to 4.
    #   V = pi int x^2/4 dx = pi*16/3 = 16.755161 (= pi*4*4/3)
    #   x_bar = 16 / (16/3) = 3 = 3h/4
    out = h.drive(fmmech.t_com_calculus, ["2", "x/2", "0", "4"], [])
    h.num("solid: volume of the r=2 h=4 cone", out, "volume V = ",
          math.pi * 16.0 / 3.0, 1e-3)
    h.num("solid: 3h/4 for h = 4", out, "x_bar = ", 3.0, 1e-6)

    # Solid hemisphere of radius 1: x = sqrt(1-y^2) from y = 0 to 1 about Oy.
    #   V = pi int (1-y^2) dy = 2pi/3 = 2.0943951
    #   y_bar = int y(1-y^2) dy / int (1-y^2) dy = (1/4)/(2/3) = 3/8
    out = h.drive(fmmech.t_com_calculus, ["3", "sqrt(1-y^2)", "0", "1"], [])
    h.num("solid: hemisphere volume", out, "volume V = ",
          2.0 * math.pi / 3.0, 1e-3)
    h.num("solid: hemisphere COM is 3r/8", out, "y_bar = ", 0.375, 1e-4)


def test_com_standard(h):
    import fmmech

    # Solid cone, h = 4: 3h/4 = 3 from the apex (and h/4 = 1 above the base).
    out = h.drive(fmmech.t_com_standard, ["9", "4"], [])
    h.num("standard: solid cone 3h/4", out, "distance = ", 3.0, 1e-9)
    h.has("standard: cone measured from the apex", out, "APEX")

    # Semicircular lamina r = 3: 4r/(3pi) = 4/pi = 1.2732395
    out = h.drive(fmmech.t_com_standard, ["6", "3"], [])
    h.num("standard: semicircular lamina 4r/(3pi)", out, "distance = ",
          4.0 / math.pi, 1e-3)

    # Solid hemisphere r = 8: 3r/8 = 3.  Hollow hemisphere r = 8: r/2 = 4.
    out = h.drive(fmmech.t_com_standard, ["7", "8"], [])
    h.num("standard: solid hemisphere 3r/8", out, "distance = ", 3.0, 1e-9)
    out = h.drive(fmmech.t_com_standard, ["8", "8"], [])
    h.num("standard: hollow hemisphere r/2", out, "distance = ", 4.0, 1e-9)

    # Semicircular arc r = 1: 2r/pi = 0.6366198.  The general circular-arc
    # formula r sinA/A with A = 90 deg must give the same number.
    out = h.drive(fmmech.t_com_standard, ["4", "1"], [])
    h.num("standard: semicircular arc 2r/pi", out, "distance = ",
          2.0 / math.pi, 1e-3)
    out = h.drive(fmmech.t_com_standard, ["3", "1", "90"], [])
    h.num("standard: arc r sinA/A agrees at A = 90", out, "distance = ",
          2.0 / math.pi, 1e-3)

    # Circular sector 2r sinA/(3A) with A = 90 deg must give the semicircular
    # lamina result 4r/(3pi) = 0.4244132.
    out = h.drive(fmmech.t_com_standard, ["5", "1", "90"], [])
    h.num("standard: sector agrees with the semicircular lamina", out,
          "distance = ", 4.0 / (3.0 * math.pi), 1e-3)

    # Rod L = 7: L/2 = 3.5.  Hollow cone h = 6: 2h/3 = 4 from the apex.
    out = h.drive(fmmech.t_com_standard, ["1", "7"], [])
    h.num("standard: rod L/2", out, "distance = ", 3.5, 1e-9)
    out = h.drive(fmmech.t_com_standard, ["10", "6"], [])
    h.num("standard: hollow cone 2h/3", out, "distance = ", 4.0, 1e-9)

    # Triangular lamina, height 9: h/3 = 3 above the base.
    out = h.drive(fmmech.t_com_standard, ["2", "9"], [])
    h.num("standard: triangular lamina h/3", out, "distance = ", 3.0, 1e-9)


def test_topple(h):
    import fmmech

    # A body whose centre of mass is 1 m above the base and 0.5 m from the
    # tipping edge, mu = 0.4, on a plane that is slowly tilted:
    #   topples when tan th > a/h = 0.5  ->  26.565051 deg
    #   slides   when tan th > mu  = 0.4  ->  21.801409 deg
    # 21.8 < 26.6, so it slides first. At 30 deg (tan = 0.5774) both are
    # exceeded.
    out = h.drive(fmmech.t_topple, ["1", "0.5", "1", "0.4", "30"], [])
    h.num("topple: toppling angle arctan(a/h)", out, "topple angle = ",
          26.565051, 1e-4)
    h.num("topple: sliding angle arctan(mu)", out, "slide angle = ",
          21.801409, 1e-4)
    h.has("topple: rough enough to topple means slide first", out,
          "slides first")
    h.has("topple: at 30 deg it topples", out, "  topples")
    h.has("topple: at 30 deg it slides", out, "  slides")

    # Same shape but mu = 0.8: sliding needs 38.659808 deg, toppling only
    # 26.565051, so now it topples first.
    out = h.drive(fmmech.t_topple, ["1", "0.5", "1", "0.8", None], [])
    h.num("topple: sliding angle for mu = 0.8", out, "slide angle = ",
          38.659808, 1e-4)
    h.has("topple: rough surface topples first", out, "topples first")

    # A block of weight 100 N, half-width 0.3 m, pushed horizontally at a
    # height of 1.2 m, mu = 0.5:
    #   sliding needs P > mu W = 50 N
    #   toppling needs P y > W a, i.e. P > 100*0.3/1.2 = 25 N
    # so it topples first.
    out = h.drive(fmmech.t_topple, ["2", "100", "0.3", "1.2", "0.5"], [])
    h.num("push: force to slide", out, "P to slide = ", 50.0, 1e-9)
    h.num("push: force to topple", out, "P to topple = ", 25.0, 1e-9)
    h.has("push: topples before it slides", out, "topples first")


# ================================================================ small tools =
def test_couple(h):
    import fmmech

    # Forces of 6 N a distance 2 m apart: G = 12 N m, zero resultant. Taking
    # moments about x = 5 gives (0-5)(6) + (2-5)(-6) = -30 + 18 = -12, and
    # about x = 0 gives 0 + (2)(-6) = -12: the same, as it must be.
    out = h.drive(fmmech.t_couple, ["6", "2", "5"], [])
    h.num("couple: moment F d", out, "moment G = ", 12.0, 1e-9)
    h.num("couple: moment about x = 5", out, "moment about p = ", -12.0, 1e-9)
    h.has("couple: resultant force is zero", out, "resultant force = 0")
    out = h.drive(fmmech.t_couple, ["6", "2", "0"], [])
    h.num("couple: same moment about x = 0", out, "moment about p = ",
          -12.0, 1e-9)


def test_triangle_of_forces(h):
    import fmmech

    # Forces 3, 4, 5 in equilibrium draw a 3-4-5 triangle. The interior angle
    # opposite 5 is 90 deg, so the 3 N and 4 N forces are at 180-90 = 90 deg.
    # cos A = (16+25-9)/(2*4*5) = 0.8 -> A = 36.869898, so F2^F3 = 143.130102;
    # cos B = (25+9-16)/(2*5*3) = 0.6 -> B = 53.130102, so F3^F1 = 126.869898.
    # The three angles between the forces sum to 360.
    out = h.drive(fmmech.t_triangle_forces, ["1", "3 4 5"], [])
    h.num("triangle: 3 and 4 are perpendicular", out, "F1 to F2 = ",
          90.0, 1e-4)
    h.num("triangle: angle between 4 and 5", out, "F2 to F3 = ",
          143.130102, 1e-4)
    h.num("triangle: angle between 5 and 3", out, "F3 to F1 = ",
          126.869898, 1e-4)
    h.close("triangle: the three angles close at 360",
            90.0 + 143.130102 + 126.869898, 360.0, 1e-4)

    # Forces 5, 12, 13: cos A = (144+169-25)/312 = 0.9230769 -> 22.619865,
    # so F2^F3 = 157.380135; cos B = (169+25-144)/130 = 0.3846154 ->
    # 67.380135, so F3^F1 = 112.619865; and F1^F2 = 90.
    out = h.drive(fmmech.t_triangle_forces, ["1", "5 12 13"], [])
    h.num("triangle: 5-12-13 right angle", out, "F1 to F2 = ", 90.0, 1e-4)
    h.num("triangle: 5-12-13 second angle", out, "F2 to F3 = ",
          157.380135, 1e-4)
    h.num("triangle: 5-12-13 third angle", out, "F3 to F1 = ",
          112.619865, 1e-4)

    # 1, 2 and 5 cannot close: 1 + 2 < 5.
    out = h.drive(fmmech.t_triangle_forces, ["1", "1 2 5"], [])
    h.has("triangle: rejects an impossible set", out, "cannot close")

    # 3 N along Ox and 4 N along Oy have resultant 5 N at 53.130102 deg, so
    # the equilibriant is 5 N at 233.130102 deg.
    out = h.drive(fmmech.t_triangle_forces, ["2", "3", "0", "4", "90"], [])
    h.num("triangle: third force magnitude", out, "F3 = ", 5.0, 1e-6)
    h.num("triangle: third force direction", out, "direction = ",
          233.130102, 1e-4)


def test_units(h):
    import fmmech

    # M L T^-2 is a force, measured in kg m s^-2.
    out = h.drive(fmmech.t_units, ["1", "1 1 -2"], [])
    h.has("units: force units", out, "kg m s^-2")
    h.has("units: names the quantity", out, "force")
    # M L^2 T^-2 is work/energy/moment.
    out = h.drive(fmmech.t_units, ["1", "1 2 -2"], [])
    h.has("units: energy units", out, "kg m^2 s^-2")
    h.has("units: names energy", out, "energy")
    # All-zero powers: a dimensionless quantity such as e or mu.
    out = h.drive(fmmech.t_units, ["1", "0 0 0"], [])
    h.has("units: recognises dimensionless", out, "dimensionless")

    # 20 m/s in km/h: dimensions L T^-1, new units 1 kg, 1000 m, 3600 s, so
    # divide by 1000^1 * 3600^-1 = 0.2777778 -> 72 km/h.
    out = h.drive(fmmech.t_units, ["2", "0 1 -1", "20", "1 1000 3600"], [])
    h.num("units: conversion factor", out, "factor = ", 1000.0 / 3600.0, 1e-3)
    h.num("units: 20 m/s is 72 km/h", out, "new value = ", 72.0, 1e-6)

    # 5 N in g cm s^-2 (dynes): divide by 0.001 * 0.01 = 1e-5, giving 500000,
    # which is the textbook 1 N = 10^5 dyne.
    out = h.drive(fmmech.t_units, ["2", "1 1 -2", "5", "0.001 0.01 1"], [])
    h.num("units: 5 N is 5e5 dyne", out, "new value = ", 500000.0, 1e-3)


def test_relative(h):
    import fmmech

    # A at (0,0) moving (2,0); B at (10,5) moving (-3,0).
    #   r rel = (10,5), |r| = sqrt(125) = 11.180340
    #   v rel = (-5,0), speed 5, direction 180 deg
    #   closest at t = -(r.v)/|v|^2 = 50/25 = 2 s
    #   least distance = |(10-10, 5)| = 5
    #   at t = 1 the separation is |(5,5)| = 7.0710678
    out = h.drive(fmmech.t_relative,
                  ["0 0", "2 0", "10 5", "-3 0", "1"], [])
    h.num("relative: distance now", out, "distance now = ",
          math.sqrt(125.0), 1e-4)
    h.num("relative: relative speed", out, "rel speed = ", 5.0, 1e-9)
    h.num("relative: direction of the relative velocity", out,
          "direction = ", 180.0, 1e-6)
    h.num("relative: time of closest approach", out, "closest at t = ",
          2.0, 1e-6)
    h.num("relative: least distance", out, "least distance = ", 5.0, 1e-6)
    h.num("relative: separation at t = 1", out, "distance = ",
          5.0 * SQ2, 1e-4)

    # Equal velocities: the relative velocity is zero and the separation
    # |(3,4)| = 5 never changes.
    out = h.drive(fmmech.t_relative,
                  ["0 0", "1 1", "3 4", "1 1", None], [])
    h.num("relative: constant separation", out, "distance now = ", 5.0, 1e-9)
    h.num("relative: zero relative speed", out, "rel speed = ", 0.0, 1e-9)
    h.has("relative: says the distance is constant", out, "never changes")

    # Malformed input must be refused, not guessed at.
    out = h.drive(fmmech.t_relative, ["0 0 0", "1 1", "3 4", "1 1"], [])
    h.has("relative: rejects a 3-component vector", out, "two numbers")


def test_tangential(h):
    import fmmech

    # r = 2, omega = 3, alpha = 4:
    #   a_r = omega^2 r = 18,  a_t = r alpha = 8
    #   |a| = sqrt(324 + 64) = sqrt(388) = 19.697716
    #   angle to the radius = arctan(8/18) = 23.962489 deg
    #   v = omega r = 6
    out = h.drive(fmmech.t_circular, ["5", "2", "3", "4"], [])
    h.num("tangential: radial acceleration", out, "a_r = ", 18.0, 1e-9)
    h.num("tangential: tangential acceleration", out, "a_t = ", 8.0, 1e-9)
    h.num("tangential: resultant acceleration", out, "total a = ",
          math.sqrt(388.0), 1e-4)
    h.num("tangential: angle to the radius", out, "angle to radius = ",
          23.962489, 1e-4)
    h.num("tangential: speed", out, "v = omega r = ", 6.0, 1e-9)

    # alpha = 0 is uniform circular motion: no tangential component, so the
    # resultant is exactly the radial acceleration.
    out = h.drive(fmmech.t_circular, ["5", "2", "3", "0"], [])
    h.num("tangential: zero alpha gives no a_t", out, "a_t = ", 0.0, 1e-9)
    h.num("tangential: zero alpha leaves a = a_r", out, "total a = ",
          18.0, 1e-9)


SECTIONS = [
    ("Y421 oblique impact: sphere and surface", test_oblique),
    ("Y421 oblique impact: two spheres", test_oblique_spheres),
    ("Y421 projectile cartesian path", test_projectile_path),
    ("Y421 projectile on an inclined plane", test_projectile_incline),
    ("Y421 elastic strings and springs", test_elastic),
    ("Y421 centre of mass by calculus", test_com_calculus),
    ("Y421 standard centres of mass", test_com_standard),
    ("Y421 sliding versus toppling", test_topple),
    ("Y421 couples", test_couple),
    ("Y421 triangle of forces", test_triangle_of_forces),
    ("Y421 units and dimensions", test_units),
    ("Y421 relative motion in 2-D", test_relative),
    ("Y421 tangential acceleration", test_tangential),
]
