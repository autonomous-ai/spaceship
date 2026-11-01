#!/bin/sh
# Read back and redraw every committed generator sheet with the code in this tree (drawgen_audit.py), in drawgen's
# own Python environment: the one tools/drawgen/run.sh makes and uses (DRAWGEN_VENV moves it), made on first use.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
RUN="$HERE/../drawgen/run.sh"
# the environment's place is run.sh's own default, read from it so the two never part
DEFAULT=$(sed -n 's/^VENV="\${DRAWGEN_VENV:-\(.*\)}"$/\1/p' "$RUN")
VENV="${DRAWGEN_VENV:-$(eval echo "$DEFAULT")}"
if [ -z "$VENV" ]; then
  echo "drawgen_audit: can't find drawgen's environment in $RUN" >&2
  exit 2
fi
if [ ! -x "$VENV/bin/python" ]; then
  "$RUN" stale >/dev/null 2>&1 || true            # run.sh makes the environment on its first run
fi
exec "$VENV/bin/python" -I "$HERE/drawgen_audit.py" "$@"
