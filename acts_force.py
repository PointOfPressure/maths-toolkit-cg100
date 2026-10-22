# Forces actions (acts.py has the registry): all box forms (nothing typed),
# each solving for whatever is ?: a block on a slope or surface, a pulley,
# towing, moments, and the resultant or equilibrium of forces.

def f_blank(F):
    if F.kind != 'blank':
        return []
    raw = 'raw'
    return [(1, ('Slope or surface', 'e_force', 'block', None,
                 ('boxes', ['m', 'slope', 'P', 'pull', 'mu', 'a', 'moving', 'g'], 2, raw))),
            (2, ('Pulley', 'e_force', 'pulley', None,
                 ('boxes', ['m1', 'slope', 'mu', 'm2', 'a', 'T', 'g'], 2, raw))),
            (3, ('Towing', 'e_force', 'towing', None,
                 ('boxes', ['m1', 'm2', 'D', 'R1', 'R2', 'a', 'T', 'g'], 2, raw))),
            (4, ('Moments', 'e_force', 'moments', None, ('boxes', ['down', 'up', 'g'], 1, raw))),
            (5, ('Forces', 'e_force', 'forces', None, ('boxes', ['forces', 'g'], 1, raw)))]

ACTS = (f_blank,)
