# Vectors actions (acts.py has the registry): one vector (magnitude and
# direction, unit vector), two (AB, distance, midpoint, sum and difference,
# parallel, the angle between, a + t b), and with nothing typed the
# quadrilateral and size-and-direction boxes.

def v_one(F):
    if F.kind != 'vec' or len(F.vecs) != 1:
        return []
    return [(1, ('Magnitude, direction', 'e_vec', 'magnitude', None, None)),
            (2, ('Unit vector', 'e_vec', 'unit', None, None))]

def v_two(F):
    if F.kind != 'vec' or len(F.vecs) != 2:
        return []
    out = [(1, ('AB and distance', 'e_vec', 'ab', None, None)),
           (2, ('Sum, difference', 'e_vec', 'sumdiff', None, None)),
           (3, ('Parallel?', 'e_vec', 'parallel', None, None)),
           (5, ('Midpoint', 'e_vec', 'midpoint', None, None)),
           (6, ('a + t b', 'e_vec', 'along', None, [('t =', 1, False)]))]
    if not F.letters:
        out.append((4, ('Angle between', 'e_vec', 'angle', None, None)))
    return out

def v_blank(F):
    if F.kind != 'blank':
        return []
    return [(1, ('Quadrilateral ABCD', 'e_vec', 'quad', None, ('boxes', ['A', 'B', 'C', 'D'], 2, 'raw'))),
            (2, ('From size, direction', 'e_vec', 'polar', None, ('boxes', ['size', 'angle'], 2)))]

ACTS = (v_blank, v_one, v_two)
