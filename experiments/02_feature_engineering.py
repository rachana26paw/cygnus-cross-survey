"""
Cygnus — Step 2: Feature Engineering
=======================================
RECONSTRUCTION NOTE: This script reconstructs the feature extraction steps
documented in results/data_preparation_report.md and results/ml_experiment_report.md.
It was not recovered from git history. It reproduces the feature CSV files
used in the original experiment.

What this script does:
  1. Extracts two shared features from the cleaned TESS data:
       - period (days)
       - prim_width_pf (primary eclipse duration, phase fraction)
  2. Drops records with missing values in either feature (keeps 4,046 of 4,563).
  3. Builds the Gaia feature table from raw catalog files:
       - period_days = 1 / frequency
       - derived_primary_ecl_duration (already in phase fraction)
       - gaia_label from model_type
  4. Saves:
       - data/processed/tess_features.csv
       - data/processed/gaia_features.csv

Run from the project root:
  python experiments/02_feature_engineering.py
"""

import pandas as pd
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TESS_CLEAN   = ROOT / "data" / "processed" / "tess_clean.csv"
GAIA_EB      = ROOT / "data" / "raw" / "gaia" / "catalog" / "gaia_vari_eclipsing_binary.csv"
TESS_FEAT    = ROOT / "data" / "processed" / "tess_features.csv"
GAIA_FEAT    = ROOT / "data" / "processed" / "gaia_features.csv"

# ── TESS features ──────────────────────────────────────────────────────────────
print("Building TESS feature table …")
tess = pd.read_csv(TESS_CLEAN)

# Select only the columns we need
tess_feat = tess[["tess_id", "signal_id", "period", "prim_width_pf", "tess_label"]].copy()

# Drop rows that are missing either feature.
# prim_width_pf is NaN for 517 records (the TESS pipeline failed to fit the eclipse width).
# Using only complete cases keeps the feature set clean and avoids imputation assumptions.
tess_feat = tess_feat.dropna(subset=["period", "prim_width_pf"])
print(f"  Rows with both features complete: {len(tess_feat):,}  (expected: 4,046)")

label_counts = tess_feat["tess_label"].value_counts().sort_index()
print(f"  Label 0 (detached): {label_counts[0]:,}")
print(f"  Label 1 (contact):  {label_counts[1]:,}")

tess_feat.to_csv(TESS_FEAT, index=False)
print(f"  Saved: {TESS_FEAT}")

# ── Gaia features ──────────────────────────────────────────────────────────────
print("\nBuilding Gaia feature table …")
gaia_eb = pd.read_csv(GAIA_EB)
print(f"  Raw Gaia EB catalog: {len(gaia_eb):,} sources")

# Orbital period: the catalog stores frequency (cycles/day), so period = 1 / frequency.
gaia_eb["period_days"] = 1.0 / gaia_eb["frequency"]

# Eclipse duration: already in phase fraction (0–1).
# Note: a hard cap at exactly 0.400 appears for many sources; this is a Gaia pipeline limit.

# Proxy label from model_type:
#   TWOGAUSSIANS or ONEGAUSSIAN → label 0 (detached-like; two distinct dips)
#   ELLIPSOIDAL or any cosine variant → label 1 (contact-like; continuous variation)
def assign_gaia_label(model_type):
    if isinstance(model_type, str):
        model_type = model_type.strip().upper()
        if model_type in ("TWOGAUSSIANS", "ONEGAUSSIAN"):
            return 0
        else:
            return 1
    return None  # unexpected null

gaia_eb["gaia_label"] = gaia_eb["model_type"].apply(assign_gaia_label)

# Select the output columns
gaia_feat = gaia_eb[[
    "source_id",
    "period_days",
    "derived_primary_ecl_duration",
    "gaia_label",
]].copy()

# Report on missing eclipse duration
missing_ecl = gaia_feat["derived_primary_ecl_duration"].isna().sum()
print(f"  Sources with complete eclipse duration: {len(gaia_feat) - missing_ecl}  (expected: 489)")
print(f"  Sources missing eclipse duration: {missing_ecl}  (expected: 11)")

label_counts = gaia_feat["gaia_label"].value_counts().sort_index()
print(f"  Label 0 (detached-like): {label_counts[0]:,}  (expected: 363)")
print(f"  Label 1 (contact-like):  {label_counts[1]:,}  (expected: 137)")

gaia_feat.to_csv(GAIA_FEAT, index=False)
print(f"  Saved: {GAIA_FEAT}")

# ── distribution comparison ────────────────────────────────────────────────────
print("\nFeature distribution comparison:")
print(f"  Period — TESS median: {tess_feat['period'].median():.2f} days  |  "
      f"Gaia median: {gaia_feat['period_days'].median():.2f} days")
print(f"  Eclipse duration — TESS median: {tess_feat['prim_width_pf'].median():.3f}  |  "
      f"Gaia median: {gaia_feat['derived_primary_ecl_duration'].median():.3f}")
print("  NOTE: These distributions are very different — this is the core challenge of the experiment.")
print("Done.")
