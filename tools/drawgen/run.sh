#!/bin/sh
# Run drawgen in its own Python environment (requirements.txt), made on first use in a per-user cache
# (about 700 MB: OCC and its VTK). Override the place with DRAWGEN_VENV. Needs python3 3.10-3.12; uses uv when
# it is installed, else python -m venv and pip. Nothing is installed system-wide.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
VENV="${DRAWGEN_VENV:-$HOME/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2}"
if [ ! -x "$VENV/bin/python" ]; then
  PY="${DRAWGEN_PYTHON:-python3}"
  mkdir -p "$(dirname "$VENV")"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python "$PY" "$VENV"
    VIRTUAL_ENV="$VENV" uv pip install --only-binary :all: -r "$HERE/requirements.txt"
  else
    "$PY" -m venv "$VENV"
    "$VENV/bin/pip" install --only-binary :all: -r "$HERE/requirements.txt"
  fi
fi
exec "$VENV/bin/python" "$HERE/drawgen.py" "$@"
