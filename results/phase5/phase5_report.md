# Phase 5 Report — ML Verification and Confidence Analysis

**Project:** Cygnus — Cross-Survey Eclipsing Binary Classification  
**Research question:** Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?  
**Author:** rachana.s@atriauniversity.edu.in  
**Date:** 2026-09-30  

---

## 1. Purpose

Phase 4 trained a Random Forest on NASA TESS eclipsing binary data and applied it unchanged to ESA Gaia DR3 data. The core finding was that the model assigned high confidence to Gaia predictions that were mostly wrong — the confidence score was severely misleading when applied across surveys.

Phase 5 investigates the *reasons* for that failure and asks:

1. Is the eclipse duration feature the root cause of the cross-survey failure?
2. Does restricting the comparison to a shared period range improve the result?
3. Do the Brier scores and reliability diagrams confirm the same picture as the calibration analysis?
4. What is the final scientific answer to the research question?

---

## 2. Experimental Setup

### 2.1 Data

| Dataset | Rows | Notes |
|---------|------|-------|
| TESS feature table (`tess_features.csv`) | 4,046 | period + prim_width_pf + tess_label |
| Gaia feature table (`gaia_features.csv`) | 489 | period_days + derived_primary_ecl_duration + gaia_label |
| TESS test predictions (Phase 4) | 810 | Held-out 20%, same split reused |
| Gaia predictions (Phase 4) | 489 | All Gaia, two-feature model |

**Important constraints (all enforced):**
- `morph_coeff` never used as a feature — it IS the TESS label source.
- `model_type` never used as a feature — it IS the Gaia proxy-label source.
- Gaia data never used in training.
- Gaia correctness is always "agreement with proxy labels" — NOT physical ground truth.

### 2.2 Label definitions

**TESS labels** (from `morph_coeff`):
- Label 0 = `morph_coeff` < 0.5 → detached-like eclipsing binary
- Label 1 = `morph_coeff` ≥ 0.5 → contact-like eclipsing binary

**Gaia proxy labels** (from `model_type`):
- Label 0 = TWOGAUSSIANS or ONEGAUSSIAN → detached-like
- Label 1 = ELLIPSOIDAL or any WITH_ELLIPSOIDAL variant → contact-like
- VSX cross-check agreement: 39.2% — documented limitation

### 2.3 Random Forest configuration (Phase 4 baseline and Experiment 1)

- `n_estimators=200`, `max_depth=None`, `min_samples_leaf=2`
- `class_weight='balanced'`, `random_state=42`
- Train/test split: `GroupShuffleSplit(test_size=0.2, random_state=42)` grouped by `tess_id`
- 80% train (3,236 rows), 20% test (810 rows)
- No feature scaling (Random Forest is scale-invariant)

---

## 3. Experiment 1 — Period-Only Model

### 3.1 Motivation

Phase 4 found that eclipse duration (`prim_width_pf`) had **66.9% feature importance**. The distributions are very different across surveys (TESS median 0.079, Gaia median 0.284, with a hard Gaia cap at 0.400). This means the model saw most Gaia sources as contact-like because of their wider eclipses, regardless of their actual class.

The period-only model tests whether removing eclipse duration — and therefore removing the main distribution mismatch — reduces the cross-survey overconfidence.

### 3.2 Results

| Metric | TESS test | Gaia (vs proxy) |
|--------|-----------|-----------------|
| Accuracy | 0.762 | 0.382 |
| F1 (weighted) | 0.762 | 0.367 |
| Mean confidence | 0.860 | 0.913 |
| Calibration gap | +0.098 | +0.530 |
| Brier score | 0.175 | 0.546 |

**Calibration by bin — TESS (period only):**

| Confidence bin | N | Accuracy |
|----------------|---|----------|
| 0.50–0.59 | 62 | 0.468 |
| 0.60–0.69 | 105 | 0.629 |
| 0.70–0.79 | 105 | 0.629 |
| 0.80–0.89 | 91 | 0.769 |
| 0.90–1.00 | 447 | 0.864 |

**Calibration by bin — Gaia (period only, vs proxy labels):**

| Confidence bin | N | Proxy accuracy |
|----------------|---|----------------|
| 0.50–0.59 | 29 | 0.379 |
| 0.60–0.69 | 34 | 0.412 |
| 0.70–0.79 | 34 | 0.529 |
| 0.80–0.89 | 41 | 0.415 |
| 0.90–1.00 | 351 | 0.362 |

### 3.3 Interpretation

Removing eclipse duration **made things worse for TESS** (accuracy dropped from 0.925 to 0.762) without meaningfully fixing the Gaia problem (proxy accuracy 0.325 → 0.382; calibration gap 0.535 → 0.530). Most importantly, **mean Gaia confidence increased to 0.913** — the model became *more* overconfident, not less. In the highest confidence bin (0.90–1.00), proxy-label accuracy was only 0.362.

This tells us that eclipse duration was not the sole cause of overconfidence — the underlying period distribution mismatch and the proxy-label imperfection also contribute substantially.

---

## 4. Experiment 2 — Phase 4 Two-Feature Baseline

Results reloaded from Phase 4 saved predictions (`tess_test_predictions.csv`, `gaia_predictions.csv`).

| Metric | TESS test | Gaia (vs proxy) |
|--------|-----------|-----------------|
| Accuracy | 0.9247 | 0.3252 |
| F1 (weighted) | 0.9247 | 0.2644 |
| Mean confidence | 0.9408 | 0.8603 |
| Calibration gap | +0.016 | +0.535 |
| Brier score | 0.0600 | 0.4877 |

**Calibration by bin — TESS (two features):**

| Confidence bin | N | Accuracy |
|----------------|---|----------|
| 0.50–0.59 | 19 | 0.579 |
| 0.60–0.69 | 25 | 0.720 |
| 0.70–0.79 | 52 | 0.673 |
| 0.80–0.89 | 61 | 0.885 |
| 0.90–1.00 | 653 | 0.966 |

**Calibration by bin — Gaia (two features, vs proxy labels):**

| Confidence bin | N | Proxy accuracy |
|----------------|---|----------------|
| 0.50–0.59 | 18 | 0.500 |
| 0.60–0.69 | 18 | 0.222 |
| 0.70–0.79 | 166 | 0.102 |
| 0.80–0.89 | 51 | 0.275 |
| 0.90–1.00 | 236 | 0.487 |

The two-feature model performs far better on TESS than the period-only model. The Brier score of 0.060 is close to a perfect classifier's theoretical minimum. On Gaia, the calibration gap is enormous (+0.535) and the highest confidence bin (0.90–1.00) achieves only 48.7% proxy-label accuracy — barely better than chance for a balanced binary task.

---

## 5. Experiment 3 — Period-Range-Filtered Gaia Evaluation

### 5.1 Scientific justification for the threshold

The threshold of **period ≥ 1.0 day** was chosen based on the following reasoning:

- Short-period eclipsing binaries (< 1 day) are almost exclusively contact or semi-contact systems (EW type). This is a known physical constraint: very short periods indicate stars that have nearly filled or overfilled their Roche lobes.
- In the TESS training data, only 30.3% of sources have periods below 1 day.
- In the Gaia dataset, 66.9% of sources have periods below 1 day — Gaia is dominated by the short-period contact regime.
- The period ≥ 1 day filter selects the range where both surveys contain a more comparable mixture of detached and contact systems.
- This threshold is physically motivated. It was **not** chosen or adjusted after seeing Gaia performance results.

### 5.2 Results

After filtering, 162 of 489 Gaia sources remain (period ≥ 1.0 day). The Phase 4 two-feature model was applied without any retraining.

| Metric | Full Gaia (Phase 4) | Gaia filtered (≥ 1 day) |
|--------|---------------------|--------------------------|
| N | 489 | 162 |
| Proxy accuracy | 0.325 | 0.383 |
| F1 (weighted) | 0.264 | 0.402 |
| Mean confidence | 0.860 | 0.872 |
| Calibration gap | +0.535 | +0.489 |
| Brier score | 0.488 | 0.501 |

**Calibration by bin — period-range-filtered Gaia:**

| Confidence bin | N | Proxy accuracy |
|----------------|---|----------------|
| 0.50–0.59 | 12 | 0.333 ⚠ low N |
| 0.60–0.69 | 6 | 0.333 ⚠ low N |
| 0.70–0.79 | 24 | 0.542 |
| 0.80–0.89 | 32 | 0.344 |
| 0.90–1.00 | 88 | 0.364 |

### 5.3 Interpretation

Filtering to the overlapping period range gives a small improvement in proxy accuracy (0.325 → 0.383) and F1 (0.264 → 0.402), and a modest reduction in calibration gap (+0.535 → +0.489). However, the model remains **severely overconfident**: in the highest confidence bin (0.90–1.00), proxy-label accuracy is only 0.364. The Brier score for the filtered set (0.501) is virtually the same as for the full set (0.488).

The improvement is insufficient to make the confidence scores trustworthy. Period-range filtering does not solve the cross-survey calibration problem.

---

## 6. Experiment 5 — Brier Scores

The Brier score measures how close predicted probabilities are to true outcomes. Range: 0 (perfect) to 1 (worst). A random classifier on a balanced two-class problem scores approximately 0.25.

| Experiment | Survey | Brier score | Interpretation |
|------------|--------|-------------|----------------|
| Phase 4 (period + ecl_dur) | TESS test | **0.0600** | Excellent — probabilities closely match outcomes |
| Phase 4 (period + ecl_dur) | Gaia (proxy) | **0.4877** | Very poor — worse than random |
| Period-only | TESS test | **0.1743** | Moderate — acceptable but weaker |
| Period-only | Gaia (proxy) | **0.5458** | Very poor — worse than random |
| Range-filtered (≥ 1 day) | Gaia (proxy) | **0.5008** | Very poor — worse than random |

The TESS Brier score of 0.060 with the two-feature model confirms very strong probability calibration on the training survey. All three Gaia evaluations produce Brier scores above 0.48 — worse than a classifier that simply assigns equal 50/50 probability to every prediction. This independently confirms the reliability diagram and calibration table findings.

---

## 7. Experiment 4 — Reliability Diagram

Saved to: `results/phase5/reliability_diagram_tess_vs_gaia.png`

The reliability diagram shows two panels side by side:
- **Left:** Phase 4 baseline (period + eclipse duration)
- **Right:** Experiment 1 (period only)

In both panels:
- The TESS line follows the perfect-calibration diagonal closely (especially in the high-confidence region).
- The Gaia line falls far below the diagonal. In the 0.70–0.80 confidence bin for the Phase 4 model, the actual proxy-label accuracy is only 0.102 — the model assigned 70–80% confidence to predictions that were correct only 10% of the time.
- This is the central visual finding: the model is systematically overconfident when applied to Gaia data.

---

## 8. Experiment 6 — Confidence Comparison Summary

| Experiment | Features | Survey | N | Accuracy | Mean conf | Calib gap | Brier |
|------------|----------|--------|---|----------|-----------|-----------|-------|
| Phase 4 | period + ecl_dur | TESS test | 810 | 0.925 | 0.941 | +0.016 | 0.060 |
| Phase 4 | period + ecl_dur | Gaia proxy | 489 | 0.325 | 0.860 | +0.535 | 0.488 |
| Exp 1 | period only | TESS test | 810 | 0.762 | 0.860 | +0.098 | 0.174 |
| Exp 1 | period only | Gaia proxy | 489 | 0.382 | 0.913 | +0.530 | 0.546 |
| Exp 3 | period + ecl_dur | Gaia ≥ 1 day | 162 | 0.383 | 0.872 | +0.489 | 0.501 |

Full table saved to: `results/phase5/phase5_metrics.csv`

---

## 9. Experiment 7 — Scientific Interpretation

### 9.1 Answer to the research question

**Research question:** Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?

**Answer:** No. The confidence scores produced by this model cannot be trusted when it is applied to Gaia data.

The evidence is consistent across all experiments:

1. **Calibration gap of +0.535 on Gaia** — the model's mean confidence exceeds its actual proxy-label accuracy by 53.5 percentage points.
2. **Highest confidence bin (0.90–1.00):** proxy-label accuracy only 48.7% — predictions the model made with near-certainty were correct barely half the time.
3. **Brier score of 0.488 on Gaia** — worse than a random 50/50 predictor. This means the predicted probabilities actively mislead rather than inform.
4. **Reliability diagram:** the Gaia line falls far below the perfect-calibration diagonal at every confidence level.
5. **Neither removing eclipse duration nor restricting the period range fixes the problem.** Calibration gaps remain above 0.48 in all Gaia variants.

### 9.2 Why does this happen?

Three compounding causes have been identified:

**Cause 1 — Feature distribution mismatch (eclipse duration)**  
TESS eclipse durations have a median of 0.079 phase fraction. Gaia eclipse durations have a median of 0.284 and are capped at 0.400 by the Gaia pipeline. The model learned to classify detached systems partly by their short eclipse durations. When it sees Gaia sources with much wider eclipses, it systematically predicts "contact-like" with high confidence — even for Gaia sources that the proxy labels call detached.

**Cause 2 — Period distribution mismatch**  
TESS training data has a median period of 2.07 days. Gaia is dominated by very short-period systems (median 0.458 days, with 66.9% below 1 day). These ultra-short systems are physically concentrated in the contact class, but the model's learned period boundary may not transfer well to a distribution so different from its training data. Restricting to periods ≥ 1 day helps only slightly, suggesting this is not the sole cause.

**Cause 3 — Proxy-label imperfection**  
The Gaia `model_type` labels are a proxy, not a true physical classification. The VSX cross-check found only 39.2% agreement. It is possible that some of the apparent Gaia "errors" reflect genuine label disagreements rather than model failures. However, even if some fraction of apparent errors are label noise, the calibration gap of +0.535 is far too large to be explained by label noise alone.

### 9.3 What the results do and do not mean

**What they mean:**  
- A model trained on TESS cannot be trusted to give reliable probability estimates when applied to Gaia.  
- High confidence from this model on Gaia data should not be interpreted as high certainty.  
- The cross-survey transfer fails for identifiable, physically interpretable reasons.

**What they do not mean:**  
- The results do not show that Random Forests are inherently unreliable — on TESS (training survey), performance and calibration are excellent.  
- The results do not prove that cross-survey transfer is impossible in general — they show it fails with these specific features and these specific datasets.  
- Gaia proxy-label "accuracy" figures are not physical classification accuracy. Some apparent errors may reflect disagreements between the TESS morphology classifier and the Gaia light-curve model, rather than fundamental model failure.

### 9.4 Limitations

1. **Gaia proxy labels are imperfect.** The model_type system achieves only 39.2% agreement with independent VSX labels. This means Gaia "accuracy" figures are a lower bound on true accuracy — but the calibration gap is large enough that proxy-label imperfection cannot explain it entirely.

2. **Small sample sizes in low-confidence bins.** Many calibration bins have fewer than 20 sources, making accuracy estimates in those bins unreliable. This is noted in the reliability diagram.

3. **Eclipse duration comparability.** The use of `prim_width_pf` (TESS) and `derived_primary_ecl_duration` (Gaia) as equivalent features was accepted as conditional. The large distribution gap suggests they may not be fully comparable across surveys.

4. **Gaia period-range filter.** Restricting to 162 sources (33% of Gaia data) reduces statistical power and may introduce selection bias into the subset evaluated.

---

## 10. Files Produced

| File | Description |
|------|-------------|
| `results/phase5/period_only_tess_predictions.csv` | 810 rows — period-only model, TESS test set |
| `results/phase5/period_only_gaia_predictions.csv` | 489 rows — period-only model, all Gaia |
| `results/phase5/period_range_gaia_predictions.csv` | 162 rows — two-feature model, Gaia period ≥ 1 day |
| `results/phase5/reliability_diagram_tess_vs_gaia.png` | Reliability diagrams, Phase 4 baseline and period-only |
| `results/phase5/phase5_metrics.csv` | Summary table of all 5 evaluation sets |
| `results/phase5/phase5_report.md` | This report |

---

## 11. Summary of Phase 5 Findings

The confidence scores produced by this Random Forest model cannot be trusted when it is applied to data from a different astronomical survey. Three controlled experiments — removing eclipse duration, filtering to a shared period range, and examining multiple confidence metrics (calibration gap, Brier score, reliability diagram) — all confirm the same conclusion. The model is near-perfectly calibrated on TESS but severely overconfident on Gaia across every confidence level.

This is the answer to the research question. It is a scientifically meaningful result: it shows that survey-specific measurement properties (eclipse duration distributions, period population biases) can cause a well-performing classifier to become systematically misleading when applied outside its training domain.

---

*End of Phase 5 Report*
