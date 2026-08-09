import math

SQ2 = math.sqrt(2.0)
SQ3 = math.sqrt(3.0)


def test_oblique(h):
    import fmmech

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
    h.has("wall: says the surface is smooth", out, "smooth surface")
    h.has("wall: says the tangential part is unchanged", out, "UNCHANGED")

    out = h.drive(fmmech.t_oblique_wall, ["10", "60", "0.5", None], [])
    h.num("wall: arctan(tan30/e) to the normal", out, "angle to normal = ",
          math.atan(math.tan(math.pi / 6.0) / 0.5) * 180.0 / math.pi, 1e-4)
    h.num("wall: 30 deg to the normal rebound speed", out, "speed = ",
          6.614378, 1e-4)

    out = h.drive(fmmech.t_oblique_wall, ["8", "40", "1", "3"], [])
    h.num("wall: e = 1 keeps the speed", out, "speed = ", 8.0, 1e-9)
    h.num("wall: e = 1 reflects the angle", out, "angle to surface = ",
          40.0, 1e-6)
    h.num("wall: e = 1 loses no KE", out, "KE lost = ", 0.0, 1e-9)

    out = h.drive(fmmech.t_oblique_wall, ["10", "30", "0", "2"], [])
    h.num("wall: e = 0 leaves only the tangential part", out, "speed = ",
          5.0 * SQ3, 1e-4)
    h.num("wall: e = 0 moves along the surface", out, "angle to surface = ",
          0.0, 1e-9)
    h.num("wall: e = 0 KE lost", out, "KE lost = ", 25.0, 1e-6)


def test_oblique_spheres(h):
    import fmmech

    out = h.drive(fmmech.t_oblique_spheres,
                  ["1", "4", "0", "1", "0", "0", "1"], [])
    h.num("spheres: equal masses e=1 exchange (v1)", out,
          "v1 along LOC = ", 0.0, 1e-9)
    h.num("spheres: equal masses e=1 exchange (v2)", out,
          "v2 along LOC = ", 4.0, 1e-9)
    h.num("spheres: e = 1 loses no KE", out, "KE lost = ", 0.0, 1e-9)

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
    h.close("spheres: momentum conserved along the LOC",
            2 * 0.5 + 3 * 3.0, 10.0, 1e-9)


def test_projectile_path(h):
    import fmmech

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

    out = h.drive(fmmech.t_proj_path, ["10", "30", "10", None], [])
    h.num("path: tan 30", out, "tan a = ", 1.0 / SQ3, 1e-4)
    h.num("path: x^2 coefficient at 30 deg", out, "g/(2u^2cos^2a) = ",
          1.0 / 15.0, 1e-3)
    h.num("path: range at 30 deg", out, "range = ", 5.0 * SQ3, 1e-4)
    h.num("path: height at 30 deg", out, "max height = ", 1.25, 1e-9)
    h.num("path: flight time at 30 deg", out, "time of flight = ", 1.0, 1e-9)
    h.num("path: bounding parabola apex", out, "y = ", 5.0, 1e-9)

    out = h.drive(fmmech.t_proj_path, ["20", "90", "9.8"], [])
    h.has("path: refuses a vertical launch", out, "vertical launch")


def test_projectile_incline(h):
    import fmmech

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

    out = h.drive(fmmech.t_proj_incline, ["20", "30", "-30", "9.8"], [])
    h.num("incline: best angle down a 30 deg slope", out, "best angle = ",
          30.0, 1e-9)
    h.num("incline: max range down a 30 deg slope", out, "max range = ",
          800.0 / 9.8, 1e-4)
    h.num("incline: range down the slope at the best angle", out,
          "range along plane = ", 800.0 / 9.8, 1e-4)
    h.num("incline: flight time down the slope", out, "time of flight = ",
          40.0 / 9.8, 1e-4)

    out = h.drive(fmmech.t_proj_incline, ["20", "20", "30", "9.8"], [])
    h.has("incline: rejects a launch below the slope", out, "need a > b")


def test_elastic(h):
    import fmmech

    out = h.drive(fmmech.t_elastic, ["2", "49", "1", "9.8"], [0])
    h.num("elastic: equilibrium extension", out, "extension x = ", 0.4, 1e-9)
    h.num("elastic: tension is the weight", out, "tension T = ", 19.6, 1e-9)
    h.num("elastic: total length", out, "total length = ", 1.4, 1e-9)
    h.num("elastic: EPE at equilibrium", out, "EPE there = ", 3.92, 1e-9)

    out = h.drive(fmmech.t_elastic, ["2", "49", "1", "0", "9.8"], [1])
    h.num("elastic: max extension from rest", out, "max extension x = ",
          0.8, 1e-9)
    h.num("elastic: GPE lost", out, "GPE lost = ", 15.68, 1e-6)
    h.num("elastic: EPE stored equals the GPE lost", out, "EPE stored = ",
          15.68, 1e-6)
    h.num("elastic: no KE at the start", out, "KE at that instant = ",
          0.0, 1e-9)
    h.num("elastic: total length at maximum extension", out,
          "total length = ", 1.8, 1e-9)

    out = h.drive(fmmech.t_elastic, ["2", "49", "1", "2.8", "9.8"], [1])
    h.num("elastic: max extension with initial KE", out,
          "max extension x = ", 0.4 + math.sqrt(0.48), 1e-4)
    h.num("elastic: initial KE", out, "KE at that instant = ", 7.84, 1e-6)
    h.num("elastic: energy equation balances", out, "EPE stored = ",
          7.84 + 19.6 * (0.4 + math.sqrt(0.48)), 1e-3)

    out = h.drive(fmmech.t_elastic, ["2", "1", "0.4", "9.8"], [2])
    h.num("elastic: modulus from the extension", out, "lambda = ", 49.0, 1e-6)
    h.num("elastic: stiffness", out, "stiffness k = lam/l = ", 49.0, 1e-6)


def test_com_calculus(h):
    import fmmech

    out = h.drive(fmmech.t_com_calculus, ["x^2", "0", "1"], [0])
    h.num("lamina: area under x^2", out, "area A = ", 1.0 / 3.0, 1e-3)
    h.num("lamina: x_bar under x^2", out, "x_bar = ", 0.75, 1e-6)
    h.num("lamina: y_bar under x^2", out, "y_bar = ", 0.3, 1e-6)

    out = h.drive(fmmech.t_com_calculus, ["sqrt(1-x^2)", "-1", "1"], [0])
    h.num("lamina: area of a unit semicircle", out, "area A = ",
          math.pi / 2.0, 1e-3)
    h.num("lamina: semicircle x_bar is zero", out, "x_bar = ", 0.0, 1e-6)
    h.num("lamina: semicircle y_bar is 4r/(3pi)", out, "y_bar = ",
          4.0 / (3.0 * math.pi), 1e-3)

    out = h.drive(fmmech.t_com_calculus, ["x", "0", "1"], [1])
    h.num("solid: volume of a unit cone", out, "volume V = ",
          math.pi / 3.0, 1e-4)
    h.num("solid: cone COM is 3h/4 from the apex", out, "x_bar = ",
          0.75, 1e-6)

    out = h.drive(fmmech.t_com_calculus, ["x/2", "0", "4"], [1])
    h.num("solid: volume of the r=2 h=4 cone", out, "volume V = ",
          math.pi * 16.0 / 3.0, 1e-3)
    h.num("solid: 3h/4 for h = 4", out, "x_bar = ", 3.0, 1e-6)

    out = h.drive(fmmech.t_com_calculus, ["sqrt(1-y^2)", "0", "1"], [2])
    h.num("solid: hemisphere volume", out, "volume V = ",
          2.0 * math.pi / 3.0, 1e-3)
    h.num("solid: hemisphere COM is 3r/8", out, "y_bar = ", 0.375, 1e-4)


def test_com_standard(h):
    import fmmech

    out = h.drive(fmmech.t_com_standard, ["4"], [8])
    h.num("standard: solid cone 3h/4", out, "distance = ", 3.0, 1e-9)
    h.has("standard: cone measured from the apex", out, "APEX")

    out = h.drive(fmmech.t_com_standard, ["3"], [5])
    h.num("standard: semicircular lamina 4r/(3pi)", out, "distance = ",
          4.0 / math.pi, 1e-3)

    out = h.drive(fmmech.t_com_standard, ["8"], [6])
    h.num("standard: solid hemisphere 3r/8", out, "distance = ", 3.0, 1e-9)
    out = h.drive(fmmech.t_com_standard, ["8"], [7])
    h.num("standard: hollow hemisphere r/2", out, "distance = ", 4.0, 1e-9)

    out = h.drive(fmmech.t_com_standard, ["1"], [3])
    h.num("standard: semicircular arc 2r/pi", out, "distance = ",
          2.0 / math.pi, 1e-3)
    out = h.drive(fmmech.t_com_standard, ["1", "90"], [2])
    h.num("standard: arc r sinA/A agrees at A = 90", out, "distance = ",
          2.0 / math.pi, 1e-3)

    out = h.drive(fmmech.t_com_standard, ["1", "90"], [4])
    h.num("standard: sector agrees with the semicircular lamina", out,
          "distance = ", 4.0 / (3.0 * math.pi), 1e-3)

    out = h.drive(fmmech.t_com_standard, ["7"], [0])
    h.num("standard: rod L/2", out, "distance = ", 3.5, 1e-9)
    out = h.drive(fmmech.t_com_standard, ["6"], [9])
    h.num("standard: hollow cone 2h/3", out, "distance = ", 4.0, 1e-9)

    out = h.drive(fmmech.t_com_standard, ["9"], [1])
    h.num("standard: triangular lamina h/3", out, "distance = ", 3.0, 1e-9)


def test_topple(h):
    import fmmech

    out = h.drive(fmmech.t_topple, ["0.5", "1", "0.4", "30"], [0])
    h.num("topple: toppling angle arctan(a/h)", out, "topple angle = ",
          26.565051, 1e-4)
    h.num("topple: sliding angle arctan(mu)", out, "slide angle = ",
          21.801409, 1e-4)
    h.has("topple: rough enough to topple means slide first", out,
          "slides first")
    h.has("topple: at 30 deg it topples", out, "  topples")
    h.has("topple: at 30 deg it slides", out, "  slides")

    out = h.drive(fmmech.t_topple, ["0.5", "1", "0.8", None], [0])
    h.num("topple: sliding angle for mu = 0.8", out, "slide angle = ",
          38.659808, 1e-4)
    h.has("topple: rough surface topples first", out, "topples first")

    out = h.drive(fmmech.t_topple, ["100", "0.3", "1.2", "0.5"], [1])
    h.num("push: force to slide", out, "P to slide = ", 50.0, 1e-9)
    h.num("push: force to topple", out, "P to topple = ", 25.0, 1e-9)
    h.has("push: topples before it slides", out, "topples first")


def test_couple(h):
    import fmmech

    out = h.drive(fmmech.t_couple, ["6", "2", "5"], [])
    h.num("couple: moment F d", out, "moment G = ", 12.0, 1e-9)
    h.num("couple: moment about x = 5", out, "moment about p = ", -12.0, 1e-9)
    h.has("couple: resultant force is zero", out, "resultant force = 0")
    out = h.drive(fmmech.t_couple, ["6", "2", "0"], [])
    h.num("couple: same moment about x = 0", out, "moment about p = ",
          -12.0, 1e-9)


def test_triangle_of_forces(h):
    import fmmech

    out = h.drive(fmmech.t_triangle_forces, ["3 4 5"], [0])
    h.num("triangle: 3 and 4 are perpendicular", out, "F1 to F2 = ",
          90.0, 1e-4)
    h.num("triangle: angle between 4 and 5", out, "F2 to F3 = ",
          143.130102, 1e-4)
    h.num("triangle: angle between 5 and 3", out, "F3 to F1 = ",
          126.869898, 1e-4)
    h.close("triangle: the three angles close at 360",
            90.0 + 143.130102 + 126.869898, 360.0, 1e-4)

    out = h.drive(fmmech.t_triangle_forces, ["5 12 13"], [0])
    h.num("triangle: 5-12-13 right angle", out, "F1 to F2 = ", 90.0, 1e-4)
    h.num("triangle: 5-12-13 second angle", out, "F2 to F3 = ",
          157.380135, 1e-4)
    h.num("triangle: 5-12-13 third angle", out, "F3 to F1 = ",
          112.619865, 1e-4)

    out = h.drive(fmmech.t_triangle_forces, ["1 2 5"], [0])
    h.has("triangle: rejects an impossible set", out, "cannot close")

    out = h.drive(fmmech.t_triangle_forces, ["3", "0", "4", "90"], [1])
    h.num("triangle: third force magnitude", out, "F3 = ", 5.0, 1e-6)
    h.num("triangle: third force direction", out, "direction = ",
          233.130102, 1e-4)


def test_units(h):
    import fmmech

    out = h.drive(fmmech.t_units, ["1 1 -2"], [0])
    h.has("units: force units", out, "kg m s^-2")
    h.has("units: names the quantity", out, "force")
    out = h.drive(fmmech.t_units, ["1 2 -2"], [0])
    h.has("units: energy units", out, "kg m^2 s^-2")
    h.has("units: names energy", out, "energy")
    out = h.drive(fmmech.t_units, ["0 0 0"], [0])
    h.has("units: recognises dimensionless", out, "dimensionless")

    out = h.drive(fmmech.t_units, ["0 1 -1", "20", "1 1000 3600"], [1])
    h.num("units: conversion factor", out, "factor = ", 1000.0 / 3600.0, 1e-3)
    h.num("units: 20 m/s is 72 km/h", out, "new value = ", 72.0, 1e-6)

    out = h.drive(fmmech.t_units, ["1 1 -2", "5", "0.001 0.01 1"], [1])
    h.num("units: 5 N is 5e5 dyne", out, "new value = ", 500000.0, 1e-3)


def test_relative(h):
    import fmmech

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

    out = h.drive(fmmech.t_relative,
                  ["0 0", "1 1", "3 4", "1 1", None], [])
    h.num("relative: constant separation", out, "distance now = ", 5.0, 1e-9)
    h.num("relative: zero relative speed", out, "rel speed = ", 0.0, 1e-9)
    h.has("relative: says the distance is constant", out, "never changes")

    out = h.drive(fmmech.t_relative, ["0 0 0", "1 1", "3 4", "1 1"], [])
    h.has("relative: rejects a 3-component vector", out, "two numbers")


def test_tangential(h):
    import fmmech

    out = h.drive(fmmech.t_circular, ["2", "3", "4"], [4])
    h.num("tangential: radial acceleration", out, "a_r = ", 18.0, 1e-9)
    h.num("tangential: tangential acceleration", out, "a_t = ", 8.0, 1e-9)
    h.num("tangential: resultant acceleration", out, "total a = ",
          math.sqrt(388.0), 1e-4)
    h.num("tangential: angle to the radius", out, "angle to radius = ",
          23.962489, 1e-4)
    h.num("tangential: speed", out, "v = omega r = ", 6.0, 1e-9)

    out = h.drive(fmmech.t_circular, ["2", "3", "0"], [4])
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
