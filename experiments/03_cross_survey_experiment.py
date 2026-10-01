"""
Cygnus — Step 3: Cross-Survey Experiment (end-to-end runner)
==============================================================
RECONSTRUCTION NOTE: This script is a convenience wrapper that runs the full
experiment pipeline in order. It calls the individual scripts from experiments/
and ml/ rather than duplicating their logic. Run this to reproduce all results
from scratch after running the data preparation steps.

Execution order:
  1. 01_data_preparation.py  — cleans TESS data, saves tess_clean.csv
  2. 02_feature_engineering.py — builds feature tables, saves *_features.csv
  3. ml/train_evaluate.py     — trains RF, evaluates, saves ml_summary.json
  4. ml/calibration_analysis.py — Brier scores, reliability diagram, phase5/

Run from the project root:
  python experiments/03_cross_survey_experiment.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ROOT / "experiments" / "01_data_preparation.py",
    ROOT / "experiments" / "02_feature_engineering.py",
    ROOT / "ml" / "train_evaluate.py",
    ROOT / "ml" / "calibration_analysis.py",
]

print("=" * 60)
print("CYGNUS — Full Cross-Survey Experiment Pipeline")
print("=" * 60)

for step in STEPS:
    print(f"\n>>> Running: {step.name}")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable, str(step)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print(f"\nERROR: {step.name} failed (exit code {result.returncode}).")
        print("Fix the error above and re-run.")
        sys.exit(result.returncode)

print("\n" + "=" * 60)
print("Pipeline complete. Check results/ and results/phase5/ for outputs.")
print("=" * 60)
