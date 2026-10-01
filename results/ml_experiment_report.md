# Cygnus ML Experiment Report

**Project:** Cygnus — Cross-Survey ML Confidence Evaluation  
**Date:** 2026-09-30  
**Author:** rachana.s@atriauniversity.edu.in  
**Stage:** Phase 4 — ML Experiment  
**Follows:** `results/data_preparation_report.md`

---

## 1. Objective

**Research question:** "Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"

**Experiment design:**
1. Train a Random Forest classifier on NASA TESS eclipsing binary data to distinguish **detached-like** (label 0) from **contact-like** (label 1) systems.
2. Evaluate the trained model on a held-out TESS test set to establish baseline performance.
3. Apply the **same trained model, without any retraining**, to ESA Gaia DR3 eclipsing binary data.
4. Compare the model's confidence scores with its correctness on both surveys.
5. Determine whether high model confidence on Gaia data corresponds to a high probability of being correct.

---

## 2. Dataset Construction

### TESS

**Source file:** `data/processed/tess_clean.csv` (4,563 rows — cleaned in Phase 3)

**Feature selection:**  
Records were further restricted to those with both features available (complete cases):

| Filter | Records removed | Reason |
|--------|----------------|--------|
| Missing `prim_width_pf` | 517 | Eclipse width not fitted for all sources |
| **Final TESS feature dataset** | **4,046 records** | Saved to `data/processed/tess_features.csv` |

**Column `morph_coeff` explicitly excluded** from the feature matrix.  
It was used to construct the TESS label (`tess_label`) and must not appear as a model input.

**TESS label distribution in feature dataset:**

| Label | Meaning | Count | % |
|-------|---------|-------|---|
| 0 | Detached-like (morph_coeff < 0.5) | 1,885 | 46.6% |
| 1 | Contact-like (morph_coeff ≥ 0.5) | 2,161 | 53.4% |
| **Total** | | **4,046** | **100%** |

---

### Gaia

**Source file:** `data/raw/gaia/catalog/gaia_vari_eclipsing_binary.csv` (500 rows)

**Rows kept:** 489 of 500 (11 removed for missing `derived_primary_ecl_duration` or missing `gaia_label`)

**Column `model_type` explicitly excluded** from the feature matrix.  
It was used to construct the Gaia proxy label (`gaia_label`) and must not appear as a model input.

**Gaia proxy label distribution:**

| Label | Meaning | Count | % |
|-------|---------|-------|---|
| 0 | Detached-like (TWOGAUSSIANS, ONEGAUSSIAN) | 363 | 74.2% |
| 1 | Contact-like (all ELLIPSOIDAL variants) | 126 | 25.8% |
| **Total** | | **489** | **100%** |

*Note: These labels are proxy labels. See `results/final_label_strategy.md` for limitations.*

**Feature dataset saved to:** `data/processed/gaia_features.csv`

---

## 3. Features Used

Two features were selected based on the Phase 3 data preparation analysis.

### Feature 1: Orbital period (days)

| | TESS | Gaia |
|--|------|------|
| **Column** | `period` | `1 / frequency` from vari_eclipsing_binary |
| **Units** | Days | Days |
| **Definition** | Orbital period of the binary system | Same |
| **Missing in dataset** | 0 / 4,046 | 0 / 489 |
| **Status** | ACCEPTED | ACCEPTED |

Both surveys measure the same physical quantity in the same units. This is the most scientifically solid feature.

**Distribution:**

| Statistic | TESS training | Gaia test |
|-----------|--------------|-----------|
| Minimum | 0.049 days | 0.209 days |
| Median | 2.07 days | 0.458 days |
| Maximum | 314.6 days | 196.1 days |

The distributions are substantially different. Gaia is dominated by short-period contact systems; TESS spans a broader range.

---

### Feature 2: Primary eclipse duration (phase fraction)

| | TESS | Gaia |
|--|------|------|
| **Column** | `prim_width_pf` | `derived_primary_ecl_duration` |
| **Units** | Phase fraction (0–1) | Phase fraction (0–1) |
| **Definition** | Width of primary eclipse relative to orbital period | Duration of primary eclipse relative to orbital period |
| **Missing in dataset** | 517 / 4,563 (excluded via complete-cases) | 11 / 500 |
| **Status** | CONDITIONALLY ACCEPTED | CONDITIONALLY ACCEPTED |

Both columns measure how long the primary eclipse lasts as a fraction of the orbital period. They use the same units and conceptually the same definition. However, they are derived from different pipelines.

**Distribution (important caveat):**

| Statistic | TESS (prim_width_pf) | Gaia (ecl_duration) |
|-----------|---------------------|---------------------|
| Minimum | 0.001 | 0.001 |
| Median | **0.079** | **0.284** |
| Maximum | 0.407 | 0.400 |

The median Gaia eclipse duration (0.284) is 3.6× larger than the TESS median (0.079). This is a significant distribution mismatch documented as a limitation in Phase 3 (Risk 2). Gaia also appears to have a hard cap at 0.40 — over a quarter of Gaia sources have duration at or near 0.40.

**Feature importance (from trained Random Forest):**

| Feature | Importance |
|---------|-----------|
| prim_width_pf (eclipse duration) | **66.9%** |
| period | 33.1% |

Eclipse duration is the dominant feature. This means the model's cross-survey behaviour is heavily influenced by the distribution mismatch in this feature.

---

### Features not used (and why)

| Feature | Reason rejected |
|---------|----------------|
| `morph_coeff` | IS the TESS label — excluded by design |
| `model_type` | IS the Gaia proxy label source — excluded by design |
| `Tmag` / `mean_mag_g_fov` | Different photometric bands (TESS red vs Gaia broad optical) |
| `prim_depth_pf` / `derived_primary_ecl_depth` | Different units (fractional flux vs magnitudes) |
| `std_dev`, `skewness` | Not available from the TESS catalog |
| Secondary eclipse parameters | 45.7% missing in TESS |

---

## 4. Labels Used

### TESS labels (ground truth)

Rule: `morph_coeff < 0.5` → label 0 (detached-like); `morph_coeff ≥ 0.5` → label 1 (contact-like)

The morph_coeff is a continuous measure of light-curve shape from the TESS EB catalog pipeline. The 0.5 threshold is an approximation of the physical detached/contact boundary.

### Gaia labels (proxy)

Rule: mapping from `model_type` (see `results/final_label_strategy.md`)

`model_type` describes the mathematical fitting model Gaia used, not the physical EB subtype. The proxy labels have a documented 39.2% agreement with independent VSX catalogue classifications. The proxy labels are imperfect and this must be considered when interpreting Gaia results.

---

## 5. Train/Test Split

**Method:** `GroupShuffleSplit` from scikit-learn, grouping by `tess_id`  
**Ratio:** 80% training / 20% test  
**Random seed:** 42 (fixed for reproducibility)

**Why group-based:** 6 tess_id values appear twice in the dataset (with signal_id = 1 and 2). Without group splitting, the same physical star could appear in both training and test sets, creating data leakage.

**Result:**

| Set | Rows | Label 0 | Label 1 |
|-----|------|---------|---------|
| Training | 3,236 | 1,479 (45.7%) | 1,757 (54.3%) |
| TESS test | 810 | 406 (50.1%) | 404 (49.9%) |
| Gaia (separate) | 489 | 363 (74.2%) | 126 (25.8%) |

**Leakage check:** 0 tess_id values appear in both training and test sets. PASS.

---

## 6. Random Forest Configuration

```
RandomForestClassifier(
    n_estimators=200,        # 200 trees for stable probability estimates
    max_depth=None,          # trees grow to full depth
    min_samples_leaf=2,      # prevents single-sample leaves
    class_weight='balanced', # accounts for class imbalance in training
    random_state=42,         # fixed seed for reproducibility
    n_jobs=-1                # use all available CPU cores
)
```

**No feature scaling was applied.** Random Forest uses decision tree splits, which are invariant to monotonic transformations. StandardScaler would not change results and would add unnecessary complexity.

**No hyperparameter tuning was performed.** This is a baseline experiment. The default settings with 200 trees and min_samples_leaf=2 are reasonable starting points.

**Model saved to:** `ml/random_forest_tess.joblib`

---

## 7. TESS Test Results

### Classification performance

| Metric | Value |
|--------|-------|
| **Accuracy** | **92.5%** |
| Precision (weighted) | 92.5% |
| Recall (weighted) | 92.5% |
| F1 score (weighted) | **92.5%** |

### Per-class results

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Label 0 (detached) | 0.94 | 0.90 | 0.92 | 406 |
| Label 1 (contact) | 0.91 | 0.95 | 0.93 | 404 |

### Confusion matrix

| | Predicted 0 | Predicted 1 |
|--|------------|------------|
| **Actual 0** | **367** (correct) | 39 (wrong) |
| **Actual 1** | 22 (wrong) | **382** (correct) |

749 out of 810 test records classified correctly.

### Confidence statistics

| Statistic | Value |
|-----------|-------|
| Minimum | 0.514 |
| Mean | **0.941** |
| Median | **0.995** |
| Maximum | 1.000 |
| % with confidence ≥ 0.90 | 80.6% |
| % with confidence ≥ 0.80 | 88.1% |

The model is highly confident on TESS data. Over 80% of predictions have confidence ≥ 0.90.

### Calibration on TESS (confidence vs accuracy)

| Confidence bin | N | Correct | Accuracy |
|---------------|---|---------|---------|
| 0.50–0.59 | 19 | 11 | 57.9% ⚠ low N |
| 0.60–0.69 | 25 | 18 | 72.0% |
| 0.70–0.79 | 52 | 35 | 67.3% |
| 0.80–0.89 | 61 | 54 | 88.5% |
| **0.90–1.00** | **653** | **631** | **96.6%** |

**Calibration assessment:** The model is nearly well-calibrated on TESS. The mean confidence is 0.941 and the accuracy is 92.5%. The calibration gap is only +0.016 (the model is very slightly overconfident). For the dominant confidence range (≥ 0.90), accuracy is 96.6% — the high-confidence predictions are genuinely reliable on TESS.

---

## 8. Gaia Transfer Results

**Important reminder:** The model was not retrained on Gaia. The exact model trained on TESS was applied directly.

The TESS features `period` and `prim_width_pf` were mapped to the Gaia features `period_days` and `derived_primary_ecl_duration`. These are the same physical quantities but measured by different pipelines.

### Classification performance vs proxy labels

| Metric | Value |
|--------|-------|
| **Accuracy (vs proxy labels)** | **32.5%** |
| Precision (weighted, vs proxy) | 65.4% |
| Recall (weighted, vs proxy) | 32.5% |
| F1 score (weighted, vs proxy) | **26.4%** |

### Per-class results (vs proxy labels)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Label 0 (detached) | 0.79 | 0.12 | 0.21 | 363 |
| Label 1 (contact) | 0.26 | 0.90 | 0.41 | 126 |

### Confusion matrix (vs Gaia proxy labels)

| | Predicted 0 | Predicted 1 |
|--|------------|------------|
| **Proxy label 0** | 45 (correct) | **318** (wrong) |
| **Proxy label 1** | 12 (wrong) | **114** (correct) |

### Predicted label distribution

| | Count | % |
|--|-------|---|
| Predicted label 0 (detached) | 57 | 11.7% |
| Predicted label 1 (contact) | 432 | 88.3% |

**The model predicted "contact" for 88.3% of Gaia sources.** The Gaia proxy labels assign only 25.8% as contact (label 1). This is the central finding of the experiment.

### Confidence statistics

| Statistic | Value |
|-----------|-------|
| Minimum | 0.502 |
| Mean | **0.860** |
| Median | **0.872** |
| Maximum | 1.000 |
| % with confidence ≥ 0.90 | 48.3% |
| % with confidence ≥ 0.80 | 58.7% |

The model remains **highly confident** on Gaia data (mean confidence 0.860), even though its proxy-label accuracy is only 32.5%.

---

## 9. Confidence Analysis

This is the core analysis for the research question.

### Confidence distribution comparison

| Statistic | TESS test | Gaia |
|-----------|-----------|------|
| Mean confidence | 0.941 | 0.860 |
| Median confidence | 0.995 | 0.872 |
| Mean accuracy / proxy-accuracy | 0.925 | 0.325 |
| **Calibration gap** (confidence − accuracy) | **+0.016** | **+0.535** |

The model is nearly perfectly calibrated on TESS (gap +0.016). On Gaia, the calibration gap is +0.535 — the model's confidence is on average 53.5 percentage points higher than its actual proxy-label accuracy. This is severe overconfidence.

### Calibration table: confidence bin vs accuracy

| Confidence bin | TESS N | TESS acc. | Gaia N | Gaia proxy acc. |
|---------------|--------|-----------|--------|-----------------|
| 0.50–0.59 | 19 | 57.9% ⚠ | 18 | 50.0% ⚠ |
| 0.60–0.69 | 25 | 72.0% | 18 | 22.2% ⚠ |
| 0.70–0.79 | 52 | 67.3% | 166 | **10.2%** |
| 0.80–0.89 | 61 | 88.5% | 51 | **27.5%** |
| 0.90–1.00 | 653 | **96.6%** | 236 | **48.7%** |

*⚠ = fewer than 20 samples in bin; estimates unreliable.*

**Key observation:** In the 0.90–1.00 confidence range, TESS accuracy is 96.6%. In the same range for Gaia, proxy-label accuracy is 48.7% — barely better than random guessing (50%). The model's high confidence on Gaia does not correspond to being correct by proxy labels.

### Why the model predicts "contact" for most Gaia sources

The dominant feature is eclipse duration (`prim_width_pf`) at 66.9% importance. The model learned, from TESS data:

- **TESS training pattern:** eclipse duration < 0.10 → typically detached (label 0)
- **TESS training pattern:** eclipse duration > 0.20 → typically contact (label 1)

When applied to Gaia:
- Gaia eclipse duration median = 0.284 (vs TESS training median = 0.079)
- Over 75% of Gaia sources have eclipse duration > 0.15
- The model sees these wide eclipse durations as "contact-like" — because they are, by TESS standards

This creates a systematic prediction bias: the model overwhelmingly predicts "contact" for Gaia sources, with high confidence.

### Per-predicted-class confidence and accuracy

| Predicted label | Survey | N | Mean confidence | Proxy accuracy |
|----------------|--------|---|-----------------|----------------|
| 0 (detached) | TESS | 389 | 0.940 | 94.3% |
| 0 (detached) | Gaia | 57 | 0.790 | 78.9% |
| 1 (contact) | TESS | 421 | 0.942 | 90.7% |
| 1 (contact) | Gaia | 432 | 0.870 | 26.4% |

The model predicts label 1 (contact) for 432 Gaia sources with mean confidence 0.870 — but only 26.4% of those predictions match the proxy label.

For the small number (57) of Gaia sources predicted as label 0, proxy-label accuracy is 78.9% — noticeably better. This may reflect that the proxy label for detached-like systems is more reliable (TWOGAUSSIANS → label 0 performs well for true EA systems).

---

## 10. Calibration / Reliability Analysis

### What calibration means

A perfectly calibrated model would show accuracy = confidence in every bin. For example, among all predictions made with 80% confidence, exactly 80% should be correct.

### TESS calibration assessment

The TESS model is **well-calibrated** for the high-confidence range:

- Confidence 0.90–1.00: 80.6% of predictions, 96.6% accurate.
- Confidence gap: +0.016 (slightly overconfident, negligible in practice).
- The model's confidence scores are trustworthy on TESS data from the same survey.

### Gaia calibration assessment

The Gaia calibration is **severely broken** relative to proxy labels:

- Confidence 0.70–0.79: 166 predictions, only 10.2% match proxy labels.
- Confidence 0.80–0.89: 51 predictions, only 27.5% match proxy labels.
- Confidence 0.90–1.00: 236 predictions, only 48.7% match proxy labels.
- Calibration gap: +0.535 (model is massively overconfident on Gaia).

**Interpretation:** A high confidence score from this model, when applied to Gaia, provides no reliable guarantee of correctness by the proxy labels. Even at confidence 0.90–1.00, the model is wrong more than half the time by proxy labels.

### Caveat about the proxy labels

The low proxy-label accuracy on Gaia (32.5%) has two possible explanations:

1. **The model genuinely does not transfer well to Gaia** — because the feature distributions are different and the model predicts "contact" for most sources based on their wide eclipse durations.

2. **The proxy labels are incorrect** — the Gaia `model_type` proxy labels have a documented 39.2% agreement with VSX independent labels. In particular, many contact EW systems in Gaia are labeled 0 (detached-like) by the TWOGAUSSIANS proxy mapping, even though they are physically contact systems.

These two explanations are not mutually exclusive. Both are likely contributing. The proxy-label accuracy of 32.5% should be understood as **accuracy relative to an imperfect proxy**, not as a measure of how often the model is physically wrong.

What is clear is that **the model's confidence cannot be trusted as a reliable indicator of physical correctness when applied to Gaia.**

---

## 11. Limitations

### Limitation 1: Only two shared features

Only two features were available in comparable form from both surveys: orbital period and primary eclipse duration. This is a severely constrained feature set. A richer feature set (e.g., from raw light curves) would likely improve both TESS baseline performance and cross-survey transfer. The current results reflect the limitations of using pre-computed catalogs rather than raw photometry.

### Limitation 2: Eclipse duration distributions are very different

TESS median eclipse duration = 0.079; Gaia median = 0.284. The Gaia sources systematically have wider eclipses by TESS standards. This is the primary driver of the model's tendency to predict "contact" for Gaia. It is unclear how much of this difference is physical (different EB populations) versus pipeline convention (different fitting approaches).

### Limitation 3: Gaia proxy labels are imperfect (39.2% VSX agreement)

The Gaia labels used for evaluation are derived from model_type, which has a documented 39.2% agreement with independent VSX classifications. The proxy labels systematically under-label contact (EW) systems — 62.6% of VSX-classified EW systems are assigned label 0 by the model_type mapping. This means that when the model predicts "contact" for a Gaia source labeled "detached" by the proxy, the model may actually be physically correct.

### Limitation 4: Period distribution mismatch

Gaia median period = 0.46 days; TESS median = 2.21 days. The Gaia test set is dominated by very short-period systems that are rare in the TESS training set. Some of the model's poor cross-survey performance reflects this distributional difference, not only the cross-survey measurement differences.

### Limitation 5: Small Gaia sample (489 usable sources)

With 489 Gaia sources split across confidence bins, individual bins contain as few as 18 sources. Calibration estimates from small bins are unreliable. The Gaia calibration analysis should be interpreted with caution.

### Limitation 6: No hyperparameter optimisation

The Random Forest was trained with default-like settings (200 trees, no max_depth). The baseline results may not represent the best achievable performance. However, for the purpose of this experiment (investigating confidence calibration), hyperparameter tuning would not change the fundamental conclusion about cross-survey overconfidence.

### Limitation 7: Gaia eclipse duration cap at 0.40

Many Gaia sources have `derived_primary_ecl_duration` capped at exactly 0.40. This appears to be a pipeline constraint. Sources at the cap have limited information in this feature. The effect on model predictions is that any Gaia source with duration ≥ 0.40 will receive very similar predictions regardless of whether the true value is 0.40 or 0.80.

---

## 12. Leakage Checks

| Check | Status | Details |
|-------|--------|---------|
| `morph_coeff` in TESS features | PASS | Explicitly excluded; used only as label source |
| `model_type` in Gaia features | PASS | Explicitly excluded; used only as proxy label source |
| tess_id in both train and test | PASS | 0 shared tess_ids; GroupShuffleSplit verified |
| Gaia data in training | PASS | Gaia used only for evaluation after training |
| Preprocessing before split | PASS | No StandardScaler; complete-cases filter applied before split |
| VSX labels in training | PASS | VSX used only as consistency check (Phase 3); not in training |
| Spatial overlap (TESS–Gaia) | PASS | 0 matches within 10 arcsec (Phase 2 cross-match) |

No data leakage was detected.

---

## 13. Scientific Interpretation

### Direct answer to the research question

**"Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"**

**Based on this experiment: No — not in the same way as on the original survey.**

On TESS (the survey the model was trained on), the confidence scores are reliable. Predictions with confidence 0.90–1.00 are correct 96.6% of the time. The calibration gap is only +0.016.

On Gaia (the different survey), the same confidence scores are misleading. The model remains highly confident (mean 0.860) despite achieving only 32.5% proxy-label accuracy. Predictions with confidence 0.90–1.00 are correct only 48.7% of the time by proxy labels — barely better than random guessing.

The model does not know it is looking at a different survey. It makes confident predictions based on patterns it learned from TESS, without knowing that those patterns may not apply to Gaia.

### What drove the overconfidence

The key driver is the eclipse duration feature. The model learned, on TESS, that wide eclipses indicate contact systems. Most Gaia sources have wider eclipses than TESS (median 0.284 vs 0.079) — in the regime the model associates with contact systems. The model therefore predicts "contact" with high confidence for 88.3% of Gaia sources.

However, the Gaia proxy labels assign 74.2% of sources as "detached-like" (label 0). If the proxy labels are correct, the model is systematically mislabeling Gaia sources based on the eclipse duration distribution mismatch. If the proxy labels are wrong (as the VSX agreement suggests for contact EW systems), the model may be physically more correct than the numbers imply.

This ambiguity — between model error and proxy label error — is a genuine scientific limitation that cannot be resolved with the available data.

### What this means practically

A practitioner who trained a model on TESS and applied it to Gaia without knowing the survey differences would likely:
- Trust the high confidence scores (0.86 average)
- Report ~88% of Gaia sources as contact-like systems
- Believe the results are reliable because confidence is high

This experiment shows that such trust would be misplaced. The model's confidence reflects its certainty about the features it sees, not whether those features carry the same meaning in a different survey.

### The role of the proxy labels

The 32.5% proxy-label accuracy is not purely a measure of model failure. The proxy labels are themselves imperfect. A more accurate statement is: "Under the model_type proxy labelling scheme, the model agrees with 32.5% of Gaia proxy labels." How much of the disagreement reflects genuine model error vs proxy label error is unknown.

This is an inherent limitation of the Cygnus experimental design. A more reliable evaluation would require independent, high-quality EB subtype labels for the Gaia sources — which were not available.

---

## 14. Next Recommended Phase (Phase 5)

The following steps would extend and strengthen the experiment:

**Step A — Feature investigation with period only**  
Re-run the experiment using only `period` as a feature (rejecting eclipse duration entirely). This provides a cleaner single-feature baseline and isolates the effect of the eclipse duration mismatch. If a period-only model shows better cross-survey calibration, it confirms that eclipse duration is the problem.

**Step B — Period range filtering**  
Apply the model only to Gaia sources whose periods overlap with the TESS training distribution (e.g., period > 0.5 days). This tests whether the overconfidence is partly due to Gaia's dominance of very short periods where the TESS model has limited training data.

**Step C — Reliability diagram visualisation**  
Create a formal reliability diagram (calibration curve) plot for both TESS and Gaia, comparing the observed accuracy in each confidence bin to the diagonal perfect-calibration line. This is a standard way to communicate calibration results.

**Step D — Per-class confidence analysis**  
Investigate whether the model's confidence is better calibrated for label-0 (detached) predictions vs label-1 (contact) predictions on Gaia. The preliminary analysis (Section 9) suggests predictions of label-0 have 78.9% proxy accuracy vs 26.4% for label-1.

**Step E — Brier score**  
Calculate the Brier score (mean squared error of predicted probabilities) for both TESS and Gaia. The Brier score provides a single-number summary of calibration quality.

**Step F — Logistic Regression baseline**  
Train an optional Logistic Regression model (mentioned in CLAUDE.md as a baseline) for comparison. If it shows different calibration behaviour on Gaia, it reveals whether overconfidence is specific to Random Forest or a general cross-survey problem.

---

## Files Created in Phase 4

| File | Description |
|------|-------------|
| `data/processed/tess_features.csv` | TESS ML feature table (4,046 rows: tess_id, signal_id, period, prim_width_pf, tess_label) |
| `data/processed/gaia_features.csv` | Gaia ML feature table (489 rows: source_id, period, derived_primary_ecl_duration, gaia_label) |
| `ml/random_forest_tess.joblib` | Trained Random Forest model (joblib format) |
| `results/tess_test_predictions.csv` | TESS test predictions (810 rows: features, predicted label, probabilities, confidence, correct) |
| `results/gaia_predictions.csv` | Gaia predictions (489 rows: features, predicted label, probabilities, confidence, proxy_correct) |
| `results/calibration_table.csv` | Calibration bins comparison table |
| `results/ml_summary.json` | All key metrics in machine-readable JSON |
| `results/ml_experiment_report.md` | This report |
