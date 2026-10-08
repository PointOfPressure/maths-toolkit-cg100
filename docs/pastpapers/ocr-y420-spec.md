# OCR Y420 Core Pure, specimen (SAM) — calculator audit

Tool column: `module » label » inputs`. `CAS » op » f(x) ; ask`, `CALC » Calculate » expr`. OK rows carry `⇒ "substring"` found in the output.

| Q | marks | calculator steps | tool(s) | result | note |
|---|---|---|---|---|---|
| 1 | 3 | acute angle between lines | `fcore » Angle between lines » 1,2,-1,3,1,-2` | OK | ⇒ "= 40.2 deg" |
| 2(i) | 2 | sketch half-line | `fcore » Locus arg(z-z1) = t » 4i,pi/4` | OK | ⇒ "half-line from 4i" |
| 2(ii) | 4 | radius = distance from 6+4i to y = x+4 | `fcore » Point to line dist » 6,4,0,0,4,0,1,1,0` | AWKWARD | ⇒ "distance = 3sqrt(2)"; only via a 3-D line with z = 0; no "point to half-line/2-D line distance" or "circle touching locus" tool |
| 3(i) | 2 | image of unit square | — | AWKWARD | no image-of-points tool; columns of M give (2,1), (3,4), sum (5,5) by hand |
| 3(ii)(A) | 2 | M(x, kx) = 5(x, kx) | `fcore » Invariant points/lines » 2,3,1,4` | OK | ⇒ "invariant line y = x" |
| 3(ii)(B) | 1 | invariant line | `fcore » Invariant points/lines » 2,3,1,4` | OK | ⇒ "invariant line y = x" |
| 3(ii)(C) | 1 | draw | — | none | |
| 4 | 5 | root 1+2i, find other roots and q | `fcore » Cubic real coeffs » 1,-5,?,-15,1+2i` | WRONG | raw Python error "int() argument must be … NoneType"; the known-root input cannot replace an unknown coefficient (GAP for "find q from a given root") |
| 4 | | check with q = 11 | `fcore » Cubic real coeffs » 1,-5,11,-15` | OK | ⇒ "z1 = 3" |
| 5(i) | 2 | partial fractions | `CAS » partial fractions » 2/((x+1)(x+3))` | OK | ⇒ "-1/(x+3)" |
| 5(ii) | 5 | sum as single fraction | `fcore » Method of differences » 2/((r+1)(r+3))` | OK | ⇒ "S(n) = 5/6 - (1/(n+2)+1/(n+3))" (sum of 2/…; halve) |
| 5(ii) | | single fraction | `CAS » single fraction » 5/6-1/(x+2)-1/(x+3)` | AWKWARD | ⇒ "(5*x^2/6+13*x/6)/((x+2)*(x+3))"; fractions left inside the numerator; MS (5n^2+13n)/(12(n+2)(n+3)) |
| 6(i) | 2 | eliminate t: xy = 1 | `mpure » Param to Cartesian » cosh(t)+sinh(t),cosh(t)-sinh(t)` | GAP | "cannot eliminate t"; no hyperbolic elimination (cosh^2 - sinh^2 = 1) |
| 6(ii) | 4 | min of 2x + 2/x | `CAS » stationary points » 2x+2/x` | OK | ⇒ "(1, 4)  min" |
| 7(i) | 2 | ln 1.5 from 3 terms | `fcore » Maclaurin approx » ln(1+x),3,0.5` | OK | ⇒ "series value 0.416667" |
| 7(ii)(A) | 1 | error | `fcore » Maclaurin approx » ln(1+x),3,0.5` | OK | ⇒ "error = -0.0112" |
| 7(ii)(B) | 1 | x = 2 invalid | `fcore » Maclaurin approx » ln(1+x),3,2` | OK | ⇒ "x = 2 is outside the interval" |
| 7(iii) | 2 | ln((1+x)/(1-x)) cubic | `fcore » Maclaurin series » ln((1+x)/(1-x)),3` | OK | ⇒ "2*x^3/3+2*x"; validity "not a standard form" (should be -1 < x < 1) |
| 7(iv)(A) | 3 | x = 0.2 and 0.5 | `fcore » Maclaurin approx » ln((1+x)/(1-x)),3,0.2` | OK | ⇒ "series value 0.405333" |
| 7(iv)(A) | | | `fcore » Maclaurin approx » ln((1+x)/(1-x)),3,0.5` | OK | ⇒ "series value 1.08333" |
| 7(iv)(B) | 2 | comment | — | none | |
| 8 | 5 | plane through 3 points | `fcore » Plane from 3 points » 1,0,-1,2,2,1,1,1,2` | OK | ⇒ "4x - 3y + z = 3" |
| 9(i) | 2 | sketch | — | none | |
| 9(ii) | 5 | loop area | `fcalc » Polar area » sin(3x),0,pi/3` | OK | ⇒ "area = pi/12" |
| 10(i) | 7 | x y' + 3y = 1/x, y(1) = 1 | `fcalc » Integrating factor » 3/x,1/x^2,1,1` | OK | ⇒ "(x^2/2+1/2)/x^3" |
| 10(ii) | 2 | y decreasing | `CAS » d/dx » (1+x^2)/(2x^3)` | OK | ⇒ "(-x^2/2-3/2)/x^4" |
| 11(i) | 2 | particular cases | `fcore » Sum f(r), r = a..b » (r-1)/r!,2,3` | AWKWARD | "f(r) must be a polynomial in r"; mpure Sigma sum works numerically |
| 11(ii) | 7 | induction | `fcore » Induction: sum » (r-1)/r!,1-1/n!` | OK | ⇒ "Proved for all n >= 1" |
| 12(i) | 3 | d/dx arctan | `fcalc » d/dx inverse trig » atan(x)` | OK | ⇒ "1/(x^2+1)" |
| 12(ii) | 3 | mean value | `fcalc » Mean value of f » 1/(1+x^2),-1,1` | OK | ⇒ "mean = pi/4" |
| 12(iii) | 7 | volume exact | `fcalc » Volume about x-axis » 1/(1+x^2),-1,1` | AWKWARD | "V = 4.04" decimal though the antiderivative atan(x)/2 + x/(2(x^2+1)) is shown; MS pi(pi+2)/4 |
| 13(i) | 2 | det | `fcore » Det 3x3 in terms of k » k,1,-5,2,3,-3,-1,2,2` | OK | ⇒ "12*k-36" |
| 13(ii) | 3 | solve for x^2, y^2, z^2 | `fcore » Solve 3 eqns by A^-1 » 4,1,-5,2,3,-3,-1,2,2,6,6,-6` | OK | ⇒ "x = -6"; then x = ±sqrt6 i by hand |
| 13(iii)(A) | 1 | verify | — | none | substitution |
| 13(iii)(B) | 4 | arrangement | `fcore » Three planes » 3,1,-5,1,2,3,-3,1,-1,2,2,0` | OK | ⇒ "sheaf: the planes share a line" |
| 13(iv) | 3 | 12(k-3) = ±6 | `CAS » solve f(x)=0 » abs(12(x-3))-6` | OK | ⇒ "x = 2.5, 3.5" |
| 14(i) | 4 | show | — | none | |
| 14(ii) | 4 | cos 6t in powers of cos | `fcore » cos nt, sin nt powers » 6` | AWKWARD | gives c^6-15c^4s^2+15c^2s^4-s^6; s not eliminated (MS 32c^6-48c^4+18c^2-1) |
| 14(iii) | 4 | cos^6 in multiple angles | `fcore » cos^n t, sin^n t » 6` | OK | ⇒ "(cos6t+6cos4t+15cos2t+10)/32" |
| 14(iv) | 3 | cos^6(pi/12) | `CALC » Calculate » cos(pi/12)^6` | AWKWARD | 0.812199408 equals (26+15sqrt3)/64 numerically; Calculate gives no exact form for cos(pi/12)^6 |
| 15 | 8 | int 0..2/3 arsinh 2x | `CAS » definite integral a..b » asinh(2x) ; 0,2/3` | AWKWARD | ⇒ "2*asinh(4/3)/3-1/3"; asinh(4/3) not turned into ln 3 |
| 16(i)(A) | 2 | x'' = -pi^2 x | `fcalc » SHM from omega » pi` | OK | ⇒ "period T = 2" |
| 16(i)(B) | 1 | GS | `fcalc » SHM from omega » pi` | OK | ⇒ "C*cos(pi*t)+D*sin(pi*t)" |
| 16(ii)(A) | 3 | GS with letter k | `fcalc » Second order homogen » 1,2k,k^2+9` | GAP | "b: unknown k"; numeric only (k = 0.1: e^(-t/10)(A cos 3t + B sin 3t)) |
| 16(ii)(B) | 2 | compare | — | none | |
| 16(iii) | 2 | e^(-2pi k/3) = 0.98 | `CAS » solve f(x)=0 » e^(-2pi*x/3)-0.98` | OK | ⇒ "x = 0.00965" |
| 16(iv) | 4 | x(0) = 0, x'(0) = 12 | `fcalc » Second order with IVs » 1,0.019292,9.000093,0,12` | OK | ⇒ "4*e^(-0.009646*x)*sin(3*x)"; b = 2k, c = k^2+9 typed as decimals |
| 16(v) | 2 | explain | — | none | |

Parts: 45. Rows: OK 30, WRONG 1, AWKWARD 8, GAP 2, none 7.
