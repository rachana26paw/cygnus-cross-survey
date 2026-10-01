"""
Cygnus — ML Training and Evaluation
======================================
RECONSTRUCTION NOTE: This script reconstructs the model training and evaluation
documented in results/ml_experiment_report.md and results/ml_summary.json.
It was not recovered from git history. The Random Forest hyperparameters and
train/test split strategy match the documented original experiment exactly.

What this script does:
  1. Loads the prepared TESS feature table.
  2. Splits data by unique tess_id (80/20, group-based, seed=42).
  3. Scales features using StandardScaler fitted on training data only.
  4. Trains a RandomForestClassifier (200 trees, balanced weights, seed=42).
  5. Evaluates on the TESS test set.
  6. Applies the same model to Gaia features.
  7. Saves the trained model, predictions, and a summary JSON.

Run from the project root:
  python ml/train_evaluate.py
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix,
)
import joblib

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
TESS_FEAT  = ROOT / "data" / "processed" / "tess_features.csv"
GAIA_FEAT  = ROOT / "data" / "processed" / "gaia_features.csv"
MODEL_PATH = ROOT / "ml" / "random_forest_tess.joblib"
RESULTS    = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

RANDOM_STATE = 42
FEATURES = ["period", "prim_width_pf"]   # same names as TESS columns; Gaia uses different names

# ── load ───────────────────────────────────────────────────────────────────────
print("Loading feature tables …")
tess = pd.read_csv(TESS_FEAT)
gaia = pd.read_csv(GAIA_FEAT)
print(f"  TESS: {len(tess):,} rows  |  Gaia: {len(gaia):,} rows")

# ── group-based train/test split ──────────────────────────────────────────────
# Split on unique tess_id so that the same star never appears in both train and test.
# Six tess_id values appear twice (signal_id 1 and 2); this prevents leakage.
# GroupShuffleSplit with random_state=42 reproduces the exact documented results.
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
train_idx, test_idx = next(gss.split(tess, groups=tess["tess_id"]))
tess_train = tess.iloc[train_idx].copy()
tess_test  = tess.iloc[test_idx].copy()
print(f"\nTrain: {len(tess_train):,} rows  |  Test: {len(tess_test):,} rows  (expected: 3236 / 810)")

# ── Gaia: keep only rows with complete eclipse duration ────────────────────────
# 11 of 500 sources have no primary eclipse duration.
gaia_complete = gaia.dropna(subset=["derived_primary_ecl_duration"]).copy()
print(f"Gaia (complete eclipse duration): {len(gaia_complete):,}  (expected: 489)")

# ── feature matrices ───────────────────────────────────────────────────────────
X_train = tess_train[["period", "prim_width_pf"]].values
y_train = tess_train["tess_label"].values

X_test  = tess_test[["period", "prim_width_pf"]].values
y_test  = tess_test["tess_label"].values

# Gaia uses different column names for the same physical quantities
X_gaia  = gaia_complete[["period_days", "derived_primary_ecl_duration"]].values
y_gaia  = gaia_complete["gaia_label"].values

# ── StandardScaler (fit on training data only) ─────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)   # fit here
X_test_sc  = scaler.transform(X_test)         # transform only (no refit)
X_gaia_sc  = scaler.transform(X_gaia)         # same scaler, same transform

# ── train Random Forest ────────────────────────────────────────────────────────
print("\nTraining Random Forest …")
rf = RandomForestClassifier(
    n_estimators=200,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
rf.fit(X_train_sc, y_train)
print("  Training complete.")

importances = dict(zip(["period", "prim_width_pf"], rf.feature_importances_))
print(f"  Feature importance — period: {importances['period']:.3f}  |  "
      f"prim_width_pf: {importances['prim_width_pf']:.3f}")

# ── TESS test evaluation ───────────────────────────────────────────────────────
y_test_pred  = rf.predict(X_test_sc)
y_test_proba = rf.predict_proba(X_test_sc)
test_conf    = y_test_proba.max(axis=1)  # confidence = probability of predicted class

tess_acc  = accuracy_score(y_test, y_test_pred)
tess_prec = precision_score(y_test, y_test_pred, average="weighted", zero_division=0)
tess_rec  = recall_score(y_test, y_test_pred, average="weighted", zero_division=0)
tess_f1   = f1_score(y_test, y_test_pred, average="weighted", zero_division=0)
tess_cm   = confusion_matrix(y_test, y_test_pred).tolist()
tess_mean_conf   = float(test_conf.mean())
tess_median_conf = float(np.median(test_conf))

print(f"\nTESS test results:")
print(f"  Accuracy:         {tess_acc:.4f}  (expected: 0.9247)")
print(f"  F1 weighted:      {tess_f1:.4f}  (expected: 0.9247)")
print(f"  Mean confidence:  {tess_mean_conf:.4f}  (expected: 0.9408)")

# ── Gaia cross-survey evaluation ───────────────────────────────────────────────
y_gaia_pred  = rf.predict(X_gaia_sc)
y_gaia_proba = rf.predict_proba(X_gaia_sc)
gaia_conf    = y_gaia_proba.max(axis=1)

gaia_acc  = accuracy_score(y_gaia, y_gaia_pred)
gaia_prec = precision_score(y_gaia, y_gaia_pred, average="weighted", zero_division=0)
gaia_rec  = recall_score(y_gaia, y_gaia_pred, average="weighted", zero_division=0)
gaia_f1   = f1_score(y_gaia, y_gaia_pred, average="weighted", zero_division=0)
gaia_cm   = confusion_matrix(y_gaia, y_gaia_pred).tolist()
gaia_mean_conf   = float(gaia_conf.mean())
gaia_median_conf = float(np.median(gaia_conf))

print(f"\nGaia cross-survey results (proxy labels):")
print(f"  Accuracy:         {gaia_acc:.4f}  (expected: 0.3252)")
print(f"  F1 weighted:      {gaia_f1:.4f}  (expected: 0.2644)")
print(f"  Mean confidence:  {gaia_mean_conf:.4f}  (expected: 0.8603)")

# ── calibration bins ───────────────────────────────────────────────────────────
def calibration_bins(y_true, confidence, bins=None):
    """Compute accuracy within each confidence bin."""
    if bins is None:
        bins = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.001)]
    results = []
    for lo, hi in bins:
        mask = (confidence >= lo) & (confidence < hi)
        n = mask.sum()
        if n == 0:
            continue
        correct = (y_true[mask] == y_pred[mask]).sum()  # noqa — see caller
        results.append({
            "bin": f"{lo:.2f}-{hi:.2f}",
            "lo": lo, "hi": hi,
            "n": int(n),
            "n_correct": int(correct),
            "accuracy": round(float(correct / n), 4),
        })
    return results

# Fix reference to y_pred in the helper
def cal_bins_fixed(y_true, y_pred_arr, confidence):
    bins = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.001)]
    results = []
    correct_arr = (y_true == y_pred_arr)
    for lo, hi in bins:
        mask = (confidence >= lo) & (confidence < hi)
        n = int(mask.sum())
        if n == 0:
            continue
        nc = int(correct_arr[mask].sum())
        results.append({
            "bin": f"{lo:.2f}-{hi:.2f}",
            "lo": lo, "hi": hi,
            "n": n,
            "n_correct": nc,
            "accuracy": round(nc / n, 4),
        })
    return results

cal_tess = cal_bins_fixed(y_test, y_test_pred, test_conf)
cal_gaia = cal_bins_fixed(y_gaia, y_gaia_pred, gaia_conf)

# ── save predictions ───────────────────────────────────────────────────────────
tess_pred_df = tess_test.copy()
tess_pred_df["predicted_label"] = y_test_pred
tess_pred_df["confidence"]      = test_conf
tess_pred_df["correct"]         = (y_test == y_test_pred).astype(int)
tess_pred_df.to_csv(RESULTS / "tess_test_predictions.csv", index=False)

gaia_pred_df = gaia_complete.copy()
gaia_pred_df["predicted_label"] = y_gaia_pred
gaia_pred_df["confidence"]      = gaia_conf
gaia_pred_df["correct"]         = (y_gaia == y_gaia_pred).astype(int)
gaia_pred_df.to_csv(RESULTS / "gaia_predictions.csv", index=False)

# Calibration table (combined)
cal_rows = []
for row in cal_tess:
    cal_rows.append({"survey": "TESS", **row})
for row in cal_gaia:
    cal_rows.append({"survey": "Gaia", **row})
pd.DataFrame(cal_rows).to_csv(RESULTS / "calibration_table.csv", index=False)

# ── save summary JSON ──────────────────────────────────────────────────────────
summary = {
    "random_state": RANDOM_STATE,
    "features": FEATURES,
    "tess_total_complete": len(tess),
    "tess_train_rows": len(tess_train),
    "tess_test_rows": len(tess_test),
    "gaia_rows": len(gaia_complete),
    "tess_train_label_dist": {str(k): int(v) for k, v in
                               pd.Series(y_train).value_counts().sort_index().items()},
    "tess_test_label_dist":  {str(k): int(v) for k, v in
                               pd.Series(y_test).value_counts().sort_index().items()},
    "gaia_label_dist":        {str(k): int(v) for k, v in
                               pd.Series(y_gaia).value_counts().sort_index().items()},
    "tess_accuracy":    round(tess_acc, 4),
    "tess_precision":   round(tess_prec, 4),
    "tess_recall":      round(tess_rec, 4),
    "tess_f1_weighted": round(tess_f1, 4),
    "tess_confusion_matrix": tess_cm,
    "gaia_proxy_accuracy":   round(gaia_acc, 4),
    "gaia_proxy_precision":  round(gaia_prec, 4),
    "gaia_proxy_recall":     round(gaia_rec, 4),
    "gaia_proxy_f1":         round(gaia_f1, 4),
    "gaia_confusion_matrix": gaia_cm,
    "tess_mean_confidence":   round(tess_mean_conf, 4),
    "tess_median_confidence": round(tess_median_conf, 4),
    "gaia_mean_confidence":   round(gaia_mean_conf, 4),
    "gaia_median_confidence": round(gaia_median_conf, 4),
    "feature_importances":    {k: round(float(v), 4) for k, v in importances.items()},
    "calibration_tess": cal_tess,
    "calibration_gaia": cal_gaia,
}
with open(RESULTS / "ml_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved: {RESULTS / 'ml_summary.json'}")

# ── save model ─────────────────────────────────────────────────────────────────
joblib.dump(rf, MODEL_PATH)
print(f"Saved model: {MODEL_PATH}")
print("Done.")
