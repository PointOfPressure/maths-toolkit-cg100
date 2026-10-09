# Maths toolkit launcher. The calculator can't save settings, so they live
# here: change a value, save, and it is the default from then on. The
# Settings page (SETTINGS key) changes them until you exit.
FURTHER = False     # True adds the Further Maths topics (H645) to the home grid
ANGLE = 'rad'       # 'rad' or 'deg'
ANSWERS = 'both'    # 'exact', 'decimal' or 'both'
DECIMALS = '3sf'    # '3sf' '4sf' '5sf' '6sf' or '1dp' '2dp' '3dp' '4dp'
COMPLEX = 'a+bi'    # 'a+bi' or 'polar'
SLEEP = 10          # minutes with no key before it closes (0 = 10 hours)
REPEAT = 'normal'   # held arrow keys: 'off', 'slow', 'normal' or 'fast'
import casui
casui.main(further=FURTHER, angle=ANGLE, answers=ANSWERS, decimals=DECIMALS,
           complex=COMPLEX, sleep=SLEEP, repeat=REPEAT)
