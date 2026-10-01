"""
Cygnus — Step 1: Data Preparation
===================================
RECONSTRUCTION NOTE: This script reconstructs the data-preparation steps
documented in results/data_preparation_report.md. It was not recovered from
git history (no original source code exists in the repository). It is
written to reproduce the same cleaned output files as were used in the
original experiment.

What this script does:
  1. Loads the raw TESS catalog.
  2. Removes 21 invalid records (NaN period, out-of-range morph_coeff, bad depth).
  3. Creates the TESS binary label from morph_coeff.
  4. Saves the cleaned dataset to data/processed/tess_clean.csv.

Run from the project root:
  python experiments/01_data_preparation.py
"""

import pandas as pd
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TESS_RAW  = ROOT / "data" / "raw" / "tess" / "NASA TESS Dataset.csv"
TESS_CLEAN = ROOT / "data" / "processed" / "tess_clean.csv"

TESS_CLEAN.parent.mkdir(parents=True, exist_ok=True)

# ── load ───────────────────────────────────────────────────────────────────────
print("Loading raw TESS data …")
tess = pd.read_csv(TESS_RAW)
print(f"  Raw records: {len(tess):,}  |  Columns: {tess.shape[1]}")

# ── cleaning ───────────────────────────────────────────────────────────────────
original_count = len(tess)

# Rule 1: remove records with NaN period
# Two records have period=NaN and morph_coeff=-1 (failed pipeline fits).
before = len(tess)
tess = tess[tess["period"].notna()].copy()
removed_period = before - len(tess)
print(f"  Removed {removed_period} records: period is NaN (failed fit)")

# Rule 2: remove records with morph_coeff outside [0, 1]
# morph_coeff is the classification target; values outside [0,1] cannot be labelled.
before = len(tess)
tess = tess[(tess["morph_coeff"] >= 0) & (tess["morph_coeff"] <= 1)].copy()
removed_morph = before - len(tess)
print(f"  Removed {removed_morph} records: morph_coeff outside [0, 1]")

# Rule 3: remove records with prim_depth_pf > 100
# Eclipse depth is a fractional flux drop (max physically possible = 1.0).
# Values above 100 are measurement errors or pipeline failures.
before = len(tess)
tess = tess[~(tess["prim_depth_pf"] > 100)].copy()
removed_depth = before - len(tess)
print(f"  Removed {removed_depth} records: prim_depth_pf > 100 (impossible value)")

total_removed = original_count - len(tess)
print(f"\n  Total removed: {total_removed}  (expected: 21)")
print(f"  Clean records: {len(tess):,}  (expected: 4,563)")

# ── label ──────────────────────────────────────────────────────────────────────
# morph_coeff < 0.5  → label 0 (detached-like: sharp eclipses)
# morph_coeff >= 0.5 → label 1 (contact-like: smooth, rounded light curve)
tess["tess_label"] = (tess["morph_coeff"] >= 0.5).astype(int)

label_counts = tess["tess_label"].value_counts().sort_index()
print(f"\n  Label 0 (detached): {label_counts[0]:,}  ({100*label_counts[0]/len(tess):.1f}%)")
print(f"  Label 1 (contact):  {label_counts[1]:,}  ({100*label_counts[1]/len(tess):.1f}%)")

# ── save ───────────────────────────────────────────────────────────────────────
tess.to_csv(TESS_CLEAN, index=False)
print(f"\nSaved: {TESS_CLEAN}  ({len(tess):,} rows × {tess.shape[1]} cols)")

# ── quick sanity check ─────────────────────────────────────────────────────────
print("\nSanity checks:")
print(f"  morph_coeff range: [{tess['morph_coeff'].min():.4f}, {tess['morph_coeff'].max():.4f}]")
print(f"  period range: [{tess['period'].min():.3f}, {tess['period'].max():.3f}] days")
print(f"  NaN in period: {tess['period'].isna().sum()}")
print(f"  NaN in prim_width_pf: {tess['prim_width_pf'].isna().sum()} (expected ~517)")
print("Done.")
