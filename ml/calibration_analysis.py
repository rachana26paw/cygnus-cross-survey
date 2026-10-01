"""
Cygnus — Calibration Analysis
================================
RECONSTRUCTION NOTE: This script reconstructs the calibration and additional
experiment analysis documented in results/phase5/phase5_report.md and
results/phase5/phase5_metrics.csv. It was not recovered from git history.

What this script does:
  1. Loads the TESS and Gaia prediction files.
  2. Computes Brier scores.
  3. Computes calibration gap (mean confidence − accuracy).
  4. Generates a reliability diagram (confidence bins vs. actual accuracy).
  5. Runs two additional experiments:
       - Experiment 1: period-only model (no eclipse duration)
       - Experiment 3: Gaia filtered to period >= 1 day
  6. Saves results to results/phase5/.

Run from the project root:
  python ml/calibration_analysis.py
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # no display needed
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, brier_score_loss,
)

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
TESS_FEAT = ROOT / "data" / "processed" / "tess_features.csv"
GAIA_FEAT = ROOT / "data" / "processed" / "gaia_features.csv"
RESULTS   = ROOT / "results"
PHASE5    = RESULTS / "phase5"
PHASE5.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42

# ── helpers ────────────────────────────────────────────────────────────────────
def group_split(df, id_col, test_frac=0.2, seed=RANDOM_STATE):
    """Split df by unique values of id_col using GroupShuffleSplit. Returns (train_df, test_df)."""
    gss = GroupShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)
    train_idx, test_idx = next(gss.split(df, groups=df[id_col]))
    return df.iloc[train_idx].copy(), df.iloc[test_idx].copy()

def calibration_bins(y_true, y_pred, conf):
    """Accuracy within fixed confidence bins."""
    edges = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.001)]
    rows = []
    correct = (y_true == y_pred)
    for lo, hi in edges:
        mask = (conf >= lo) & (conf < hi)
        n = int(mask.sum())
        if n == 0:
            continue
        nc = int(correct[mask].sum())
        rows.append({"lo": lo, "hi": hi, "mid": (lo + hi) / 2,
                     "n": n, "accuracy": nc / n})
    return rows

def brier(y_true, proba):
    """Brier score for binary classification using the positive-class probability."""
    # brier_score_loss expects probabilities for the positive class
    return float(brier_score_loss(y_true, proba[:, 1]))

def train_rf(X_tr, y_tr):
    rf = RandomForestClassifier(
        n_estimators=200, min_samples_leaf=2,
        class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1,
    )
    rf.fit(X_tr, y_tr)
    return rf

def run_experiment(label, tess_train, tess_test, gaia_complete, tess_cols, gaia_cols):
    """Train, evaluate on TESS test and Gaia. Returns a metrics dict."""
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(tess_train[tess_cols].values)
    X_te = scaler.transform(tess_test[tess_cols].values)
    X_ga = scaler.transform(gaia_complete[gaia_cols].values)
    y_tr = tess_train["tess_label"].values
    y_te = tess_test["tess_label"].values
    y_ga = gaia_complete["gaia_label"].values

    rf = train_rf(X_tr, y_tr)

    p_te = rf.predict_proba(X_te)
    p_ga = rf.predict_proba(X_ga)
    pred_te = rf.predict(X_te)
    pred_ga = rf.predict(X_ga)
    conf_te = p_te.max(axis=1)
    conf_ga = p_ga.max(axis=1)

    acc_te  = float(accuracy_score(y_te, pred_te))
    acc_ga  = float(accuracy_score(y_ga, pred_ga))
    f1_te   = float(f1_score(y_te, pred_te, average="weighted", zero_division=0))
    f1_ga   = float(f1_score(y_ga, pred_ga, average="weighted", zero_division=0))
    mean_c_te = float(conf_te.mean())
    mean_c_ga = float(conf_ga.mean())
    bs_te   = brier(y_te, p_te)
    bs_ga   = brier(y_ga, p_ga)

    # Calibration gap: mean confidence minus overall accuracy
    # Positive gap means overconfident (model claims more certainty than it earns)
    gap_te = round(mean_c_te - acc_te, 4)
    gap_ga = round(mean_c_ga - acc_ga, 4)

    # High-confidence subset (conf >= 0.90)
    hc_mask_ga = conf_ga >= 0.90
    hc_n_ga  = int(hc_mask_ga.sum())
    hc_acc_ga = float((y_ga[hc_mask_ga] == pred_ga[hc_mask_ga]).mean()) if hc_n_ga > 0 else 0.0

    hc_mask_te = conf_te >= 0.90
    hc_n_te   = int(hc_mask_te.sum())
    hc_acc_te = float((y_te[hc_mask_te] == pred_te[hc_mask_te]).mean()) if hc_n_te > 0 else 0.0

    return {
        "label":   label,
        "rf":      rf,
        "scaler":  scaler,
        "tess_cols": tess_cols,
        "gaia_cols": gaia_cols,
        # predictions (for saving)
        "tess_test":       tess_test,
        "gaia_complete":   gaia_complete,
        "pred_te":         pred_te,
        "pred_ga":         pred_ga,
        "conf_te":         conf_te,
        "conf_ga":         conf_ga,
        "proba_ga":        p_ga,
        "y_te":            y_te,
        "y_ga":            y_ga,
        # summary metrics
        "acc_te":    round(acc_te, 4),
        "f1_te":     round(f1_te, 4),
        "mean_c_te": round(mean_c_te, 4),
        "gap_te":    gap_te,
        "bs_te":     round(bs_te, 4),
        "hc_n_te":   hc_n_te,
        "hc_acc_te": round(hc_acc_te, 4),
        "acc_ga":    round(acc_ga, 4),
        "f1_ga":     round(f1_ga, 4),
        "mean_c_ga": round(mean_c_ga, 4),
        "gap_ga":    gap_ga,
        "bs_ga":     round(bs_ga, 4),
        "hc_n_ga":   hc_n_ga,
        "hc_acc_ga": round(hc_acc_ga, 4),
    }

# ── load and split ─────────────────────────────────────────────────────────────
print("Loading data …")
tess = pd.read_csv(TESS_FEAT)
gaia = pd.read_csv(GAIA_FEAT)
gaia_complete = gaia.dropna(subset=["derived_primary_ecl_duration"]).copy()

tess_train, tess_test = group_split(tess, "tess_id", test_frac=0.2, seed=RANDOM_STATE)
print(f"  TESS train: {len(tess_train):,}  test: {len(tess_test):,}")
print(f"  Gaia complete: {len(gaia_complete):,}")

# ── Phase 4 baseline (period + eclipse duration) ───────────────────────────────
print("\nPhase 4 baseline (period + eclipse duration) …")
p4 = run_experiment(
    "Phase 4 (period + ecl_dur)",
    tess_train, tess_test, gaia_complete,
    tess_cols=["period", "prim_width_pf"],
    gaia_cols=["period_days", "derived_primary_ecl_duration"],
)
print(f"  TESS  acc={p4['acc_te']:.4f}  gap={p4['gap_te']:.4f}  brier={p4['bs_te']:.4f}")
print(f"  Gaia  acc={p4['acc_ga']:.4f}  gap={p4['gap_ga']:.4f}  brier={p4['bs_ga']:.4f}")
print(f"  Gaia high-conf (>=0.90): n={p4['hc_n_ga']}  acc={p4['hc_acc_ga']:.4f}")

# ── Experiment 1: period-only model ───────────────────────────────────────────
print("\nExperiment 1 (period only) …")
e1 = run_experiment(
    "Exp 1 (period only)",
    tess_train, tess_test, gaia_complete,
    tess_cols=["period"],
    gaia_cols=["period_days"],
)
print(f"  TESS  acc={e1['acc_te']:.4f}  gap={e1['gap_te']:.4f}  brier={e1['bs_te']:.4f}")
print(f"  Gaia  acc={e1['acc_ga']:.4f}  gap={e1['gap_ga']:.4f}  brier={e1['bs_ga']:.4f}")

# ── Experiment 3: Gaia filtered to period >= 1 day ────────────────────────────
print("\nExperiment 3 (Gaia period >= 1 day filter) …")
gaia_filtered = gaia_complete[gaia_complete["period_days"] >= 1.0].copy()
print(f"  Gaia filtered to period >= 1d: {len(gaia_filtered):,}  (expected: ~162)")

# Re-run Phase 4 model on the filtered Gaia subset
# (Use the same trained Phase 4 model / scaler for a fair comparison)
scaler4 = StandardScaler().fit(tess_train[["period", "prim_width_pf"]].values)
X_gf = scaler4.transform(gaia_filtered[["period_days", "derived_primary_ecl_duration"]].values)
pred_gf  = p4["rf"].predict(X_gf)
proba_gf = p4["rf"].predict_proba(X_gf)
conf_gf  = proba_gf.max(axis=1)
y_gf     = gaia_filtered["gaia_label"].values

acc_gf    = float(accuracy_score(y_gf, pred_gf))
f1_gf     = float(f1_score(y_gf, pred_gf, average="weighted", zero_division=0))
mean_c_gf = float(conf_gf.mean())
bs_gf     = brier(y_gf, proba_gf)
gap_gf    = round(mean_c_gf - acc_gf, 4)

hc_mask = conf_gf >= 0.90
hc_n_gf  = int(hc_mask.sum())
hc_acc_gf = float((y_gf[hc_mask] == pred_gf[hc_mask]).mean()) if hc_n_gf > 0 else 0.0

print(f"  Gaia filtered: acc={acc_gf:.4f}  gap={gap_gf:.4f}  brier={bs_gf:.4f}")
print(f"  High-conf (>=0.90): n={hc_n_gf}  acc={hc_acc_gf:.4f}")

# ── save prediction CSVs ───────────────────────────────────────────────────────
def save_preds(exp, filename, is_gaia=True):
    if is_gaia:
        df = exp["gaia_complete"].copy()
        df["predicted_label"] = exp["pred_ga"]
        df["confidence"]      = exp["conf_ga"]
        df["correct"]         = (exp["y_ga"] == exp["pred_ga"]).astype(int)
    else:
        df = exp["tess_test"].copy()
        df["predicted_label"] = exp["pred_te"]
        df["confidence"]      = exp["conf_te"]
        df["correct"]         = (exp["y_te"] == exp["pred_te"]).astype(int)
    df.to_csv(PHASE5 / filename, index=False)

save_preds(p4, "period_only_tess_predictions.csv", is_gaia=False)
save_preds(e1, "period_only_gaia_predictions.csv", is_gaia=True)

# Save filtered Gaia
gaia_filt_out = gaia_filtered.copy()
gaia_filt_out["predicted_label"] = pred_gf
gaia_filt_out["confidence"]      = conf_gf
gaia_filt_out["correct"]         = (y_gf == pred_gf).astype(int)
gaia_filt_out.to_csv(PHASE5 / "period_range_gaia_predictions.csv", index=False)

# ── metrics CSV ────────────────────────────────────────────────────────────────
metrics_rows = [
    {
        "experiment": p4["label"],
        "features": "period, ecl_dur",
        "survey": "TESS test",
        "n": len(p4["tess_test"]),
        "accuracy": p4["acc_te"],
        "f1_weighted": p4["f1_te"],
        "mean_confidence": p4["mean_c_te"],
        "conf_ge_0.90_n": p4["hc_n_te"],
        "conf_ge_0.90_accuracy": p4["hc_acc_te"],
        "calibration_gap": p4["gap_te"],
        "brier_score": p4["bs_te"],
    },
    {
        "experiment": p4["label"],
        "features": "period, ecl_dur",
        "survey": "Gaia (proxy)",
        "n": len(gaia_complete),
        "accuracy": p4["acc_ga"],
        "f1_weighted": p4["f1_ga"],
        "mean_confidence": p4["mean_c_ga"],
        "conf_ge_0.90_n": p4["hc_n_ga"],
        "conf_ge_0.90_accuracy": p4["hc_acc_ga"],
        "calibration_gap": p4["gap_ga"],
        "brier_score": p4["bs_ga"],
    },
    {
        "experiment": e1["label"],
        "features": "period",
        "survey": "TESS test",
        "n": len(e1["tess_test"]),
        "accuracy": e1["acc_te"],
        "f1_weighted": e1["f1_te"],
        "mean_confidence": e1["mean_c_te"],
        "conf_ge_0.90_n": e1["hc_n_te"],
        "conf_ge_0.90_accuracy": e1["hc_acc_te"],
        "calibration_gap": e1["gap_te"],
        "brier_score": e1["bs_te"],
    },
    {
        "experiment": e1["label"],
        "features": "period",
        "survey": "Gaia (proxy)",
        "n": len(gaia_complete),
        "accuracy": e1["acc_ga"],
        "f1_weighted": e1["f1_ga"],
        "mean_confidence": e1["mean_c_ga"],
        "conf_ge_0.90_n": e1["hc_n_ga"],
        "conf_ge_0.90_accuracy": e1["hc_acc_ga"],
        "calibration_gap": e1["gap_ga"],
        "brier_score": e1["bs_ga"],
    },
    {
        "experiment": "Exp 3 (period >= 1d, 2-feat)",
        "features": "period, ecl_dur",
        "survey": "Gaia filtered (proxy)",
        "n": len(gaia_filtered),
        "accuracy": round(acc_gf, 4),
        "f1_weighted": round(f1_gf, 4),
        "mean_confidence": round(mean_c_gf, 4),
        "conf_ge_0.90_n": hc_n_gf,
        "conf_ge_0.90_accuracy": round(hc_acc_gf, 4),
        "calibration_gap": gap_gf,
        "brier_score": round(bs_gf, 4),
    },
]
pd.DataFrame(metrics_rows).to_csv(PHASE5 / "phase5_metrics.csv", index=False)
print(f"\nSaved: {PHASE5 / 'phase5_metrics.csv'}")

# ── reliability diagram ────────────────────────────────────────────────────────
tess_cal = calibration_bins(p4["y_te"], p4["pred_te"], p4["conf_te"])
gaia_cal = calibration_bins(p4["y_ga"], p4["pred_ga"], p4["conf_ga"])

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")

if tess_cal:
    ax.plot([r["mid"] for r in tess_cal], [r["accuracy"] for r in tess_cal],
            "o-", color="#4da6ff", lw=2, ms=7, label=f"TESS (Brier={p4['bs_te']:.3f})")
if gaia_cal:
    ax.plot([r["mid"] for r in gaia_cal], [r["accuracy"] for r in gaia_cal],
            "s-", color="#b47aff", lw=2, ms=7, label=f"Gaia proxy (Brier={p4['bs_ga']:.3f})")

ax.set_xlim(0.45, 1.05)
ax.set_ylim(0, 1.05)
ax.set_xlabel("Mean confidence in bin", fontsize=12)
ax.set_ylabel("Fraction correct (accuracy)", fontsize=12)
ax.set_title("Reliability Diagram — TESS vs Gaia cross-survey", fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PHASE5 / "reliability_diagram_tess_vs_gaia.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {PHASE5 / 'reliability_diagram_tess_vs_gaia.png'}")

print("\nCalibration summary:")
print(f"  TESS  — mean confidence: {p4['mean_c_te']:.4f}  accuracy: {p4['acc_te']:.4f}  "
      f"gap: {p4['gap_te']:.4f}  Brier: {p4['bs_te']:.4f}")
print(f"  Gaia  — mean confidence: {p4['mean_c_ga']:.4f}  accuracy: {p4['acc_ga']:.4f}  "
      f"gap: {p4['gap_ga']:.4f}  Brier: {p4['bs_ga']:.4f}")
print("Done.")
