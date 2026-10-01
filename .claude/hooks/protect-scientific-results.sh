#!/usr/bin/env bash
# Hook 1 — Scientific Result Protection
# Runs before Write or Edit tool calls.
# Warns when a tool targets validated scientific output files.
# These files contain results that have been verified and should not be
# changed accidentally. This hook outputs a warning but does NOT block —
# intentional changes are allowed after the warning is acknowledged.

INPUT=$(cat)

# Extract the file path from the tool input JSON.
# Works for both Write (file_path) and Edit (file_path).
FILE_PATH=$(echo "$INPUT" | python -c "
import json, sys
data = json.load(sys.stdin)
# Tool input may be nested under 'tool_input' or at the top level
tool_input = data.get('tool_input', data)
print(tool_input.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalise path separators
FILE_PATH_NORM=$(echo "$FILE_PATH" | tr '\\' '/')

# Protected patterns
PROTECTED=0
REASON=""

case "$FILE_PATH_NORM" in
  *results/*)
    PROTECTED=1
    REASON="results/ contains validated scientific outputs (reports, metrics, predictions)"
    ;;
  *data/processed/*)
    PROTECTED=1
    REASON="data/processed/ contains cleaned datasets used in the validated experiment"
    ;;
  *ml/random_forest_tess.joblib*)
    PROTECTED=1
    REASON="ml/random_forest_tess.joblib is the validated trained model"
    ;;
esac

if [ "$PROTECTED" -eq 1 ]; then
  echo "⚠  SCIENTIFIC RESULT PROTECTION" >&2
  echo "   File: $FILE_PATH" >&2
  echo "   Reason: $REASON" >&2
  echo "   This file is part of the validated CYGNUS research outputs." >&2
  echo "   If this change is intentional, proceed carefully." >&2
  echo "   If this change is accidental, cancel and use the correct file." >&2
fi

# Exit 0 — warn but do not block. The user can still proceed.
exit 0
