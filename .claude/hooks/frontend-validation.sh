#!/usr/bin/env bash
# Hook 2 — Frontend Validation
# Runs after Write or Edit tool calls.
# When a file inside frontend/src/ or frontend/index.html is changed,
# runs `vite build` to surface compile/import errors immediately.
# Does NOT modify files to hide errors — errors are reported as-is.

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python -c "
import json, sys
data = json.load(sys.stdin)
tool_input = data.get('tool_input', data)
print(tool_input.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

FILE_PATH_NORM=$(echo "$FILE_PATH" | tr '\\' '/')

# Only trigger for frontend source files (not public assets or data files)
case "$FILE_PATH_NORM" in
  *frontend/src/*|*frontend/index.html)
    ;;
  *)
    exit 0
    ;;
esac

# Find the frontend directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
  echo "Frontend validation: package.json not found, skipping build check." >&2
  exit 0
fi

echo "Running frontend build check (vite build)..." >&2

# Run the build with a timeout. Suppress normal output; only show errors.
cd "$FRONTEND_DIR"
BUILD_OUTPUT=$(npm run build 2>&1)
BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
  echo "FRONTEND BUILD FAILED after editing $FILE_PATH" >&2
  echo "$BUILD_OUTPUT" >&2
  exit 1
else
  echo "Frontend build check PASSED." >&2
fi

exit 0
