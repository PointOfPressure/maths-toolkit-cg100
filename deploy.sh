#!/bin/sh
# Usage: ./deploy.sh /media/sayer/disk   (the calculator's storage root)
# Precompiles every module to .mpy (the calculator loads those several times
# faster than .py) and copies them with the two launchers, maths.py and
# module.py. Deletes every other .py / .mpy in the root first.
# Needs mpy-cross from MicroPython 1.9.4; the calculator takes the build
# without unicode and without cached map lookups (variant b of hw/).
set -e
DEST="$1"
[ -d "$DEST" ] || { echo "mount point not found: $DEST"; exit 1; }
cd "$(dirname "$0")"
MPYCROSS="${MPYCROSS:-$HOME/dev/cg100/bin/mpy-cross-1.9.4}"
[ -x "$MPYCROSS" ] || { echo "mpy-cross 1.9.4 not found: $MPYCROSS"; exit 1; }
LAUNCH="maths.py module.py"
MODS=$(python3 -c "import devlint; print(' '.join(f[:-3] for f in devlint.DEVICE_FILES if f not in ('maths.py', 'module.py')))")
rm -rf build && mkdir build
for m in $MODS; do "$MPYCROSS" -mno-unicode -o "build/$m.mpy" "$m.py"; done
for f in "$DEST"/*.py "$DEST"/*.mpy; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    keep=0
    for l in $LAUNCH; do [ "$b" = "$l" ] && keep=1; done
    for m in $MODS; do [ "$b" = "$m.mpy" ] && keep=1; done
    [ $keep = 1 ] || { echo "delete $b"; rm -f "$f"; }
done
for l in $LAUNCH; do cp "$l" "$DEST/$l"; done
for m in $MODS; do cp "build/$m.mpy" "$DEST/$m.mpy"; done
sync
bad=0
for l in $LAUNCH; do cmp -s "$l" "$DEST/$l" || { echo "MISMATCH $l"; bad=1; }; done
for m in $MODS; do cmp -s "build/$m.mpy" "$DEST/$m.mpy" || { echo "MISMATCH $m.mpy"; bad=1; }; done
[ $bad = 0 ] || exit 1
echo "done: $(echo $LAUNCH $MODS | wc -w) files, verified"
