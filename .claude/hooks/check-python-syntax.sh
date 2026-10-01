#!/usr/bin/env bash
# Hook 4 — Python Syntax Check
# Runs after Write or Edit tool calls on Python files.
# Runs `python -m py_compile` on the changed file to catch syntax errors immediately.
# Lightweight — does not execute the script, only checks syntax.

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

# Only trigger for Python files in experiments/ or ml/
case "$FILE_PATH_NORM" in
  *experiments/*.py|*ml/*.py)
    ;;
  *)
    exit 0
    ;;
esac

python -m py_compile "$FILE_PATH" 2>&1
EXIT=$?

if [ $EXIT -ne 0 ]; then
  echo "SYNTAX ERROR in $FILE_PATH — fix before running the script." >&2
  exit 1
else
  echo "Syntax check PASSED: $FILE_PATH" >&2
fi

exit 0
