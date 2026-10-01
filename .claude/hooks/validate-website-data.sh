#!/usr/bin/env bash
# Hook 3 — Website Data Consistency
# Runs after Write tool calls.
# When a file in frontend/public/data/ is modified, validates that:
#   - The file is valid JSON
#   - Key numeric values in stats.json and calibration.json have not changed
#     from the validated research outputs.
# Does NOT automatically rewrite scientific data.

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

# Only trigger for website data JSON files
case "$FILE_PATH_NORM" in
  *frontend/public/data/*.json)
    ;;
  *)
    exit 0
    ;;
esac

# Validate that the file is parseable JSON
python -c "
import json, sys

path = sys.argv[1]
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'JSON valid: {path}')
except json.JSONDecodeError as e:
    print(f'JSON ERROR in {path}: {e}', file=sys.stderr)
    sys.exit(1)
except FileNotFoundError:
    print(f'File not found: {path}', file=sys.stderr)
    sys.exit(1)

# Check validated key metrics in stats.json
filename = path.replace('\\\\', '/').split('/')[-1]

if filename == 'stats.json' or filename == 'phase6_dataset_stats.json':
    errors = []
    # These are the validated values
    checks = {
        ('tess', 'n_clean'):     4563,
        ('tess', 'n_train'):     3236,
        ('tess', 'n_test'):      810,
        ('gaia', 'n_usable'):    489,
        ('tess', 'accuracy'):    0.9247,
        ('gaia', 'proxy_agree'): 0.3252,
    }
    for (section, key), expected in checks.items():
        val = data.get(section, {}).get(key)
        if val is not None and abs(float(val) - float(expected)) > 0.001:
            errors.append(f'  {section}.{key}: expected {expected}, got {val}')
    if errors:
        print('DATA CONSISTENCY WARNING — validated values may have changed:', file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

print('Data consistency check PASSED.')
" "$FILE_PATH" 2>&1

EXIT=$?
if [ $EXIT -ne 0 ]; then
  exit 1
fi

exit 0
