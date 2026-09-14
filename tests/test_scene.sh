#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TMP=$(mktemp -d)

cleanup() {
    rm -rf "$TMP"
}
trap cleanup EXIT

cp "$ROOT/scene.py" "$TMP/scene.py"
cp "$ROOT/scene.example.json" "$TMP/scene.json"

blender --factory-startup -b -P "$TMP/scene.py" >"$TMP/blender.log" 2>&1
RC=$?

if [ "$RC" -ne 0 ]; then
    cat "$TMP/blender.log"
    printf 'BLENDER_EXIT_FAIL=%s\n' "$RC" >&2
    exit 1
fi

if [ ! -s "$TMP/render.png" ]; then
    printf 'MISSING_RENDER\n' >&2
    exit 1
fi

if [ ! -s "$TMP/scene.blend" ]; then
    printf 'MISSING_BLEND\n' >&2
    exit 1
fi

if grep -Ei 'DeprecationWarning|use_nodes|Traceback|Error:' "$TMP/blender.log" >/dev/null 2>&1; then
    cat "$TMP/blender.log"
    printf 'RELEVANT_WARNING_OR_ERROR\n' >&2
    exit 1
fi

printf 'ok\n'
