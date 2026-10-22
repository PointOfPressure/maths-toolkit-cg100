# Kinematics actions (acts.py has the registry): v, s or a as a function of
# t (mockup G), a v-t graph from two lists, and with nothing typed the
# SUVAT (mockup F) and projectile boxes.

def k_fn(F):
    if F.kind != 'kin':
        return []
    q = F.kq
    out = []
    if q == 's':
        out += [(1, ('Velocity', 'e_kin', 'deriv', 'v', None)),
                (2, ('Acceleration', 'e_kin', 'deriv', 'a', None))]
    if q == 'v':
        out += [(1, ('Acceleration', 'e_kin', 'deriv', 'a', None)),
                (2, ('Displacement', 'e_kin', 'integ', 's', [('s at t = 0:', 1, True)]))]
    if q == 'a':
        out += [(1, ('Velocity', 'e_kin', 'integ', 'v', [('v at t = 0:', 1, True)])),
                (2, ('Displacement', 'e_kin', 'integ', 's', [('v at t = 0:', 1, True), ('s at t = 0:', 1, True)]))]
    out.append((5, ('At time t', 'e_kin', 'at', None, [('t =', 1, False)])))
    if q in ('s', 'v'):
        out.append((3, ('When at rest', 'e_kin', 'rest', None, None)))
        if F.vec is None and not F.letters:
            out += [(4, ('Distance', 'e_kin', 'distance', None, [('from t =', 1, True), ('to t =', 1, False)])),
                    (6, ('Max / min v', 'e_kin', 'extreme', None, None))]
    return out

def k_vt(F):
    if F.kind == 'vt':
        return [(1, ('v-t graph', 'e_suvat', 'vtgraph', None, None))]
    return []

def k_blank(F):
    if F.kind != 'blank':
        return []
    return [(1, ('SUVAT', 'e_suvat', 'suvat', None, ('boxes', ['s', 'u', 'v', 'a', 't'], 2))),
            (2, ('Projectile', 'e_suvat', 'projectile', None,
                 ('boxes', ['u', 'angle', 'height', 'g', 'time', 'range'], 2)))]

ACTS = (k_blank, k_fn, k_vt)
