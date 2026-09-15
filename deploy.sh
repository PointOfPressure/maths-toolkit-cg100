#!/bin/sh
# Usage: ./deploy.sh /media/sayer/CASIO   (the calculator's storage root)
# Deletes every *.py in the root that is not part of the toolkit, then copies
# the toolkit in. The device file list is the one devlint.py checks.
set -e
DEST="$1"
[ -d "$DEST" ] || { echo "mount point not found: $DEST"; exit 1; }
cd "$(dirname "$0")"
FILES=$(python3 -c "import devlint; print(' '.join(devlint.DEVICE_FILES))")
for f in "$DEST"/*.py; do
    [ -e "$f" ] || continue
    keep=0
    for d in $FILES; do [ "$(basename "$f")" = "$d" ] && keep=1; done
    [ $keep = 1 ] || { echo "delete $(basename "$f")"; rm -f "$f"; }
done
for d in $FILES; do echo "copy $d"; cp "$d" "$DEST/$d"; done
sync
echo "done: $(echo $FILES | wc -w) files"
