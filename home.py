# Home: a grid of topics, one press to each (mockup A). Topics that are built
# open a topic screen (topic.py); the rest open their old tool menus until
# they are built, so nothing is unreachable. HOME from any screen lands here,
# and the caches that can be rebuilt are dropped on the way.
import casui
from casui import Home, Idle

# (label, what): 't:<id>' a topic screen, 'o:<codes>' old Maths sections by
# letter, 'f:<paper>:<codes>' old Further sections, or a named screen
MATHS = (
    ('Calculate', 'calc'),
    ('Algebra', 't:alg'),
    ('Coord geometry', 'geo'),
    ('Sequences, series', 'o:D'),
    ('Trig', 't:trig'),
    ('Exp and logs', 't:exp'),
    ('Calculus', 't:calc'),
    ('Numerical', 'o:I'),
    ('Vectors', 'o:J'),
    ('Statistics', 'o:KLMNO'),
    ('Kinematics', 'o:PQ'),
    ('Forces', 'o:RS'),
)
FURTHER = (
    ('Complex', 'f:0:J'),
    ('Matrices', 'f:0:M,5:M'),
    ('3-D vectors', 'f:0:V'),
    ('Polar', 'f:0:PO'),
    ('Hyperbolic', 'f:0:H'),
    ('Differential equations', 'f:0:D,6:D'),
    ('Groups, recurrences', 'f:5:G,5:R'),
    ('Surfaces', 'f:5:C'),
)
TAIL = (
    ('Graph', 'graph'),
    ('Notes', 'notes'),
    ('Settings', 'settings'),
)

def tiles():
    out = list(MATHS)
    if casui.SET['further']:
        out += list(FURTHER)
    return out + list(TAIL)

def old_sections(what):
    # the old (code, title, module) sections behind a home tile
    out = []
    if what[:2] == 'o:':
        for code in what[2:]:
            for s in casui.MATHS:
                if s[0] == code:
                    out.append(s)
    elif what[:2] == 'f:':
        for part in what[2:].split(','):
            p, code = part.split(':')
            for s in casui.FURTHER[int(p)][2]:
                if s[0] == code:
                    out.append(s)
    return out

def open_old(label, secs):
    if len(secs) == 1:
        casui._tools_menu(*secs[0])
    else:
        casui.qual_section(label, secs)

def go(label, what):
    if what[:2] == 't:':
        import topic
        topic.run(what[2:])
    elif what == 'geo':
        import coord
        coord.run()
    elif what == 'calc':
        casui.calc_section()
    elif what == 'graph':
        casui.graph_section()
    elif what == 'notes':
        casui.notes_section()
    elif what == 'settings':
        casui.settings()
    else:
        open_old(label, old_sections(what))

FREE = casui.FREE    # functions that drop a module's caches, added as modules load

def free():
    # everything that can be rebuilt; modules themselves can't be unloaded
    # (no sys on the calculator), so this is all a session can get back
    casui._free()

def _bare(lines):
    # last resort when even a popup can't be built: constant strings only
    from casioplot import clear_screen, show_screen, draw_string
    clear_screen()
    y = 60
    for s in lines:
        draw_string(10, y, s, casui.RED, 'medium')
        y += 22
    show_screen()
    casui.wait_release()
    k = casui.wait_key()
    while k not in (casui.EXE, casui.EXITK, casui.OK, casui.HOME):
        k = casui.wait_key()
    casui.wait_release()

def _idle():
    from casioplot import clear_screen, show_screen, draw_string
    clear_screen()
    draw_string(10, 70, 'Closed after about ' + str(casui.SET['sleep'] or 600) + ' minutes idle.',
                casui.INK, 'medium')
    draw_string(10, 95, 'Run maths.py to start again.', casui.INK, 'medium')
    show_screen()

def run():
    # (pass2-aqa's main() loop, for the topic grid)
    sel = 0
    msg = None
    oom = 0     # MemoryErrors in the home grid itself, in a row
    while True:
        # every exception lands here, including those from the popup itself,
        # so nothing ends the program with a dead screen showing
        showing = False
        ingrid = False
        try:
            if msg is not None:
                m = msg
                msg = None
                showing = True
                casui.flash(m)
                showing = False
            ingrid = True
            ts = tiles()
            sel = casui.menu('Maths Toolkit', [t[0] for t in ts], sel)
            ingrid = False
            oom = 0
            if sel < 0:
                return
            go(ts[sel][0], ts[sel][1])
            free()
        except Home:
            free()
        except Idle:
            _idle()
            return
        except MemoryError as e:
            free()
            if ingrid:
                oom += 1
            if oom >= 2:
                # not even the home grid fits now
                try:
                    _bare(['Out of memory.', 'Every topic opened stays loaded.',
                           'Press EXE, then run maths.py again.'])
                except Exception:
                    pass
                return
            msg = None if showing else casui.errtext(e)
        except Exception as e:
            # an error inside the popup itself is dropped, not shown again
            msg = None if showing else casui.errtext(e)
