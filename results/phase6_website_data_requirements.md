# Phase 6 — Website Data Requirements

**Project:** Cygnus  
**Author:** rachana.s@atriauniversity.edu.in  
**Date:** 2026-09-30  
**Purpose:** Specify exactly what data the future Cygnus frontend will need, and which existing files provide it.

---

## Design Principle

Reuse existing result files wherever possible. Do not duplicate data unnecessarily. The website should read from a small set of clean, stable JSON or CSV files. These files should never contain raw data or internal column names that are not needed for display.

---

## Data Category 1 — Core Metrics (Page 4 and Page 5)

### What is needed

The key performance comparison numbers: accuracy, F1, mean confidence, calibration gap, Brier score for TESS and Gaia.

### Existing source

`results/phase5/phase5_metrics.csv`

This file contains all five evaluation rows with all needed metrics. It is already in clean CSV format.

**Rows needed:**

| Row | Use |
|-----|-----|
| Phase 4 (period + ecl_dur), TESS test | Primary TESS result |
| Phase 4 (period + ecl_dur), Gaia proxy | Primary Gaia result |
| Exp 1 (period only), TESS test | Experiment A |
| Exp 1 (period only), Gaia proxy | Experiment B |
| Exp 3 (period ≥ 1d, 2-feat), Gaia filtered | Experiment C |

**Action for Phase 7:** Read `phase5_metrics.csv` directly. No new file needed.

---

## Data Category 2 — High-Confidence Comparison (Page 4)

### What is needed

The TESS 0.90–1.00 bin: N=653, accuracy=0.9663  
The Gaia 0.90–1.00 bin: N=236, proxy accuracy=0.4873

### Existing source

`results/ml_summary.json` — contains `calibration_tess` and `calibration_gaia` arrays with all five bins.

**Action for Phase 7:** Read from `ml_summary.json`. No new file needed.

---

## Data Category 3 — Calibration Table for Reliability Diagram (Page 5)

### What is needed

Full five-bin calibration data for all experiments (TESS and Gaia), to reproduce or display the reliability diagram.

### Existing sources

- `results/calibration_table.csv` — Phase 4 baseline, both surveys
- `results/ml_summary.json` — same data in JSON format

For the Phase 5 experiments, the calibration bin data is embedded in the prediction CSVs:
- `results/phase5/period_only_tess_predictions.csv` — confidence + correct columns, can be re-binned
- `results/phase5/period_only_gaia_predictions.csv` — confidence + proxy_correct columns
- `results/phase5/period_range_gaia_predictions.csv` — confidence + proxy_correct columns

**Action for Phase 7:** Either compute calibration bins server-side from the prediction CSVs, OR pre-compute a combined calibration JSON file for all 5 evaluation sets. Pre-computing is simpler for the frontend.

**Suggested file to create in Phase 7:**

`results/phase6_calibration_all.json`

Format:
```json
{
  "phase4_tess": [
    {"bin": "0.50-0.59", "mid": 0.545, "n": 19, "accuracy": 0.5789},
    ...
  ],
  "phase4_gaia": [...],
  "period_only_tess": [...],
  "period_only_gaia": [...],
  "period_range_gaia": [...]
}
```

---

## Data Category 4 — Reliability Diagram Image (Page 5)

### What is needed

A PNG image showing the reliability diagram.

### Existing source

`results/phase5/reliability_diagram_tess_vs_gaia.png`

**Action for Phase 7:** Serve this image directly. The frontend references it as a static asset.

---

## Data Category 5 — Dataset Overview Statistics (Page 2)

### What is needed

| Item | Value | Source |
|------|-------|--------|
| TESS total records after cleaning | 4,563 | `results/data_preparation_report.md` |
| TESS complete-case records | 4,046 | `results/ml_experiment_report.md` |
| TESS training rows | 3,236 | `results/ml_summary.json` |
| TESS test rows | 810 | `results/ml_summary.json` |
| TESS label 0 count | 1,885 | `results/ml_experiment_report.md` |
| TESS label 1 count | 2,161 | `results/ml_experiment_report.md` |
| Gaia total catalog sources | 500 | `results/final_label_strategy.md` |
| Gaia usable sources | 489 | `results/ml_summary.json` |
| Gaia label 0 count (proxy) | 363 | `results/ml_summary.json` |
| Gaia label 1 count (proxy) | 126 | `results/ml_summary.json` |
| VSX proxy agreement rate | 39.2% | `results/final_label_strategy.md` |
| TESS period median (training) | 2.07 days | `results/ml_experiment_report.md` |
| Gaia period median | 0.458 days | `results/ml_experiment_report.md` |
| TESS eclipse duration median | 0.079 | `results/ml_experiment_report.md` |
| Gaia eclipse duration median | 0.284 | `results/ml_experiment_report.md` |

**Action for Phase 7:** Extract these into a single `results/phase6_dataset_stats.json` for clean frontend consumption.

---

## Data Category 6 — Feature Distribution Data (Page 6 Visuals)

### What is needed

Period and eclipse duration distributions for TESS training set and Gaia test set, to produce the period histogram and eclipse-duration histogram.

### Existing sources

- `data/processed/tess_features.csv` — columns: tess_id, signal_id, period, prim_width_pf, tess_label
- `data/processed/gaia_features.csv` — columns: source_id, period_days, derived_primary_ecl_duration, gaia_label

**Action for Phase 7:** Pre-compute histogram bin data (counts per bin) from these CSVs and save to a JSON file. Do not expose raw data files to the frontend — compute summary statistics only.

**Suggested file to create in Phase 7:**

`results/phase6_distributions.json`

Format:
```json
{
  "period": {
    "tess_bins": [...],
    "tess_counts": [...],
    "gaia_bins": [...],
    "gaia_counts": [...]
  },
  "eclipse_duration": {
    "tess_bins": [...],
    "tess_counts": [...],
    "gaia_bins": [...],
    "gaia_counts": [...]
  }
}
```

---

## Data Category 7 — Experiment Comparison (Page 7)

### What is needed

A clean table comparing the three experiments. Already available in `results/phase5/phase5_metrics.csv`.

**Action for Phase 7:** Read directly from `phase5_metrics.csv`. No new file needed.

---

## Data Category 8 — Feature Importance (Page 3 or Page 6)

### What is needed

| Feature | Importance |
|---------|-----------|
| Eclipse duration | 66.9% |
| Period | 33.1% |

### Existing source

`results/ml_summary.json` — `feature_importances` key.

**Action for Phase 7:** Read from `ml_summary.json`. No new file needed.

---

## Summary: Files the Frontend Will Use

| File | Already exists? | Used for |
|------|----------------|----------|
| `results/phase5/phase5_metrics.csv` | Yes | Core metrics table, experiment comparison |
| `results/ml_summary.json` | Yes | Dataset counts, calibration bins, feature importances |
| `results/calibration_table.csv` | Yes | Phase 4 calibration detail |
| `results/phase5/reliability_diagram_tess_vs_gaia.png` | Yes | Reliability diagram image |
| `results/phase6_calibration_all.json` | **To create in Phase 7** | Combined calibration for all 5 evaluations |
| `results/phase6_dataset_stats.json` | **To create in Phase 7** | Dataset overview statistics |
| `results/phase6_distributions.json` | **To create in Phase 7** | Period and eclipse duration histogram data |

---

## Data the Frontend Does NOT Need

The following exist in the project but should not be exposed to the frontend:

- Raw data files: `data/raw/tess/`, `data/raw/gaia/` — never expose raw data
- Individual prediction rows: `tess_test_predictions.csv`, `gaia_predictions.csv` — 800+ rows not needed for display
- Period prediction files: `period_only_tess_predictions.csv`, etc. — same reason
- Internal reports: `data_validation_report.md`, `gaia_metadata_assessment.md`, etc. — internal documentation
- Model file: `ml/random_forest_tess.joblib` — not a frontend concern
- CLAUDE.md — internal instructions

---

## What Phase 7 Should Build

Based on this analysis, Phase 7 (website build) should:

1. Create three small JSON data files (`phase6_calibration_all.json`, `phase6_dataset_stats.json`, `phase6_distributions.json`) by reading the existing result files — these are the clean data layer the frontend reads from.
2. Build the frontend using those JSON files as the data source.
3. Serve the reliability diagram PNG as a static image asset.
4. Implement the nine pages described in `phase6_website_blueprint.md`.

No new experiments or model runs are needed for Phase 7.

---

*End of Website Data Requirements*
