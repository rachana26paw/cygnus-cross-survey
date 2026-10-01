# Phase 6 — Final Scientific Results

**Project:** Cygnus — Cross-Survey Eclipsing Binary Classification  
**Research question:** "Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"  
**Author:** rachana.s@atriauniversity.edu.in  
**Date:** 2026-09-30  

---

## 1. Phase-by-Phase Summary

### Phase 0 — Project Setup

**What was done:** Defined the research question, established the project directory structure, set coding standards and scientific integrity rules in CLAUDE.md.

**Why necessary:** The experiment requires clear separation between training and test data, between surveys, and between features and labels. Setting these rules at the start prevents contamination later.

**Important fact:** The research question has one very specific focus — not whether a model is accurate, but whether its *confidence score* is reliable across surveys.

**Appears on website:** Only indirectly — the research question and project overview.

---

### Phase 1 — Data Reconnaissance

**What was done:** Inspected the TESS catalog CSV and the 500 individual Gaia epoch-photometry files. Mapped available columns, identified identifiers, and located summary files.

**Why necessary:** The datasets come from different space missions with completely different formats. The structure had to be understood before any validation could begin.

**Important fact:** The Gaia data arrived as 500 per-source epoch-photometry files plus a catalog CSV. The epoch files contain raw photometric time series; the catalog contains pre-computed variability statistics. A later retrieval step obtained four catalog-level Gaia CSVs (`gaia_vari_eclipsing_binary.csv`, `gaia_vari_classifier_result.csv`, `gaia_vari_summary.csv`, `gaia_source.csv`) which provided all the features and labels needed without processing the epoch files.

**Appears on website:** Brief mention in the Data section — that both datasets were carefully inspected before any analysis.

---

### Phase 2 — Data Validation

**What was done:** Cross-matched TESS and Gaia sources by sky position; investigated available Gaia labels; assessed external label sources (VSX, GCVS); made the final Gaia label decision.

**Why necessary:** The experiment is only scientifically valid if the labels are meaningful and if there is no positional overlap between the TESS training data and the Gaia test data.

**Important facts:**
- **Cross-match result:** 0 of 500 Gaia sources match any TESS source within 10 arcseconds (minimum separation 444 arcseconds). No spatial data leakage.
- **External labels:** VSX provides independent EA/EB/EW labels for 209 of 500 Gaia sources, but that subset is 83% EW-type — heavily biased. Using only 209 sources would distort the experiment.
- **Label decision:** Use Gaia `model_type` as a proxy label for all 500 sources. This is the only option that provides complete coverage.
- **VSX agreement:** 39.2% — low, because many EW contact systems in Gaia have a TWOGAUSSIANS fit (two detectable eclipses) and are mapped to label 0 by the proxy scheme. This is a documented limitation.

**Appears on website:** The cross-match result (no leakage) and the proxy-label explanation are essential website content.

---

### Phase 3 — Data Preparation

**What was done:** Cleaned the TESS dataset; defined TESS labels; investigated which features could be shared between TESS and Gaia; designed the train/test split; documented data leakage risks.

**Why necessary:** The model can only use features that are genuinely available from both surveys in comparable form. Features cannot be used that would encode the label or that differ fundamentally between surveys.

**Important facts:**
- **TESS cleaned:** 4,563 records (4,584 − 21 removed: 2 NaN period, 14 morph_coeff out-of-range, 5 depth > 100%).
- **Features accepted:** `period` (fully comparable, same units) and `prim_width_pf` / `derived_primary_ecl_duration` (conditionally comparable — same units and concept, but different distributions and different pipelines).
- **Features rejected:** Different photometric bands (TESS vs Gaia); eclipse depth in incompatible units; secondary eclipse parameters (45.7% missing); statistics not available from the TESS catalog.
- **TESS labels:** `morph_coeff < 0.5` → detached-like (label 0); `morph_coeff ≥ 0.5` → contact-like (label 1).
- **Split design:** Group-based split on `tess_id` to prevent a star with two signal entries appearing in both train and test.

**Appears on website:** Feature explanation (period, eclipse duration), why features were limited to two, label definitions.

---

### Phase 4 — ML Experiment

**What was done:** Built the ML feature datasets, trained a Random Forest on TESS, evaluated on held-out TESS data, applied the same model to all 489 usable Gaia sources, compared confidence with correctness.

**Why necessary:** This is the core experiment. A model that is overconfident when transferred to a new survey would give misleading results in real deployment.

**Important facts:** See Section 5 (Final Results Table).

**Appears on website:** All core results, confidence comparison, reliability analysis — the most important section.

---

### Phase 5 — ML Verification

**What was done:** Three controlled experiments tested whether the calibration failure could be explained by (a) the eclipse duration feature, (b) the period distribution mismatch, or (c) both. Brier scores and a reliability diagram were produced.

**Why necessary:** If the calibration failure could be eliminated by removing one feature, the research finding would be much simpler. The verification experiments test whether the result is robust.

**Important facts:**
- Removing eclipse duration (period-only model) did not fix the Gaia overconfidence. Calibration gap remained +0.530.
- Restricting Gaia to period ≥ 1 day (162 of 489 sources) gave only marginal improvement. Calibration gap reduced from +0.535 to +0.489 — still severe.
- Brier scores on all Gaia variants (0.488–0.546) were worse than a random predictor (~0.25 on balanced data).
- The reliability diagram shows the Gaia curve falling far below the perfect-calibration line at every confidence level.

**Appears on website:** The three experiments, the reliability diagram, and the Brier score comparison.

---

### Phase 6 — Final Scientific Interpretation

**What was done:** Integrated all findings into one coherent scientific story. Created the website blueprint and data requirements.

**Why necessary:** The project has multiple phases of evidence that together support a single research conclusion. Phase 6 ensures that conclusion is stated precisely, without overclaiming.

**Appears on website:** The final scientific finding and its limitations.

---

## 2. The Data

### TESS

NASA's Transiting Exoplanet Survey Satellite (TESS) observes continuous light curves for stars across the sky. The TESS Eclipsing Binary catalog contains derived properties for confirmed or candidate eclipsing binary stars, including fitted orbital periods, eclipse shapes, and a morphology coefficient.

**Dataset used:** 4,563 records (after cleaning). Further restricted to 4,046 records with both features available (complete cases).

**One row represents:** One eclipsing binary star observed by TESS, described by its fitted orbital properties.

**TESS labels:** Derived from `morph_coeff`, a continuous value (0–1) that measures the shape of the light curve.
- Label 0 (detached-like): `morph_coeff` < 0.5 — stars with sharp, well-separated eclipse dips; 1,885 records (46.6%)
- Label 1 (contact-like): `morph_coeff` ≥ 0.5 — stars with smoothly varying light curves; 2,161 records (53.4%)

These labels were derived from observed light-curve properties, not spectroscopic confirmation. They are scientifically reasonable but are not perfect physical classifications.

### Gaia

ESA's Gaia mission observes stars astrometrically and photometrically. The Gaia DR3 variability catalogue includes a sub-catalogue of eclipsing binary candidates with fitted light-curve model parameters.

**Dataset used:** 489 records (500 in catalog; 11 removed for missing eclipse duration).

**One row represents:** One eclipsing binary candidate in Gaia DR3, described by fitted light-curve model parameters.

**Gaia proxy labels:** Derived from `model_type`, which describes the mathematical model Gaia used to fit the light curve. This is not a direct physical subtype classification.

| model_type | Proxy label | Meaning |
|-----------|------------|---------|
| TWOGAUSSIANS | 0 (detached-like) | Two distinct eclipse dips |
| ONEGAUSSIAN | 0 (detached-like) | Only primary eclipse detected |
| ELLIPSOIDAL + variants | 1 (contact-like) | Sinusoidal modulation present |

**Why these are proxy labels:** The mapping from `model_type` to physical EB subtype is an approximation. A contact (EW) system can sometimes produce a TWOGAUSSIANS fit if both eclipses are visible. External cross-check with VSX shows only 39.2% agreement. Gaia results in this project therefore measure *agreement with proxy labels*, not physical ground-truth accuracy.

**Why Gaia epoch files were not used as independent samples:** Each of the 500 Gaia files contains dozens to hundreds of individual photometric observations of the *same* star. Treating each observation as a separate source would be wrong — one star is one source. The relevant features (period, eclipse duration) are object-level properties derived from the full light curve, not per-observation values. The catalog CSV files provided all required object-level properties without needing to process the epoch files.

---

## 3. The Features

### Feature 1: Orbital period (days)

The orbital period is how long it takes the two stars to complete one orbit around each other. It is measured in days.

- **TESS source:** Fitted period from the TESS EB catalog (`period` column).
- **Gaia source:** Derived as 1/frequency from `gaia_vari_eclipsing_binary.csv`.
- **Comparability:** Fully comparable. Both measure the same physical quantity in the same units.

**Distribution difference (important):** TESS training data median = 2.07 days. Gaia median = 0.458 days. Gaia is dominated by very short-period systems — 66.9% of Gaia sources have periods below 1 day. In the TESS training data, only 30.3% do. This period bias affects the cross-survey transfer.

### Feature 2: Primary eclipse duration (phase fraction)

The primary eclipse duration measures how long the main eclipse lasts, expressed as a fraction of the orbital period (0 = no eclipse, 1 = always in eclipse).

- **TESS source:** `prim_width_pf` — fitted eclipse width from the TESS pipeline.
- **Gaia source:** `derived_primary_ecl_duration` — derived eclipse duration from the Gaia pipeline.
- **Comparability:** Conditionally comparable. Same units and conceptually the same definition, but different fitting pipelines.

**Distribution difference (critical):** TESS median = 0.079. Gaia median = 0.284 (3.6× larger). Gaia also has a hard upper cap at 0.400 — over a quarter of Gaia sources are at or near 0.400. The Random Forest learned to classify TESS systems partly by their short eclipse durations. When it sees Gaia systems with much wider eclipses, it systematically predicts "contact-like" with high confidence.

**Feature importance in the trained model:** Eclipse duration 66.9%, period 33.1%.

### Why other features were rejected

The following reasons explain why only two features were used:

1. **Different photometric bands:** TESS observes in near-infrared; Gaia uses three optical bands. Magnitudes and brightness statistics from different bands are not directly comparable.
2. **Incompatible units for eclipse depth:** TESS depth is in fractional flux; Gaia depth is in magnitudes — these are not the same thing.
3. **Missing data in TESS catalog:** Statistics such as standard deviation and skewness are not available from the TESS EB catalog (only available from the Gaia variability summary).
4. **Target-derived features:** `morph_coeff` (the TESS label source) and `model_type` (the Gaia proxy-label source) cannot be used as input features.
5. **High missing rate:** Secondary eclipse parameters are missing for 45.7% of TESS records.

---

## 4. The ML Model

### Why Random Forest?

Random Forest is a well-established ensemble classifier that is robust to outliers, handles class imbalance well with `class_weight='balanced'`, and does not require feature scaling. It also provides class probabilities via `predict_proba()`, which are needed to measure confidence. It was selected as an appropriate, interpretable baseline — not as the best possible model.

### How it was trained

A Random Forest with 200 decision trees was trained on the TESS training set (3,236 records). No feature scaling was applied. No hyperparameter tuning was performed — this is a baseline experiment.

### TESS train/test split

The 4,046 TESS complete-case records were split 80%/20% using `GroupShuffleSplit` with groups defined by `tess_id`.

**Why group splitting was necessary:** Six stars appear twice in the dataset (with two different signal identifiers). Without grouping, the same physical star could appear in both training and test sets, creating data leakage. The group split ensures all entries for a given star go to the same partition.

**Result:** 3,236 training rows, 810 test rows. Verified: 0 tess_id values in both sets.

### Why Gaia was not used for training

The research question asks whether confidence is reliable when the model is transferred to a *different* survey. If Gaia data were included in training, there would be no meaningful transfer — the model would already have seen Gaia's distribution during training. The entire experiment depends on the model being trained only on TESS.

### Why the same model was applied to Gaia

The design is deliberately one-directional: train on TESS, apply to Gaia without retraining. This simulates a real scenario where a model built for one survey's data is then used on data from a different instrument.

---

## 5. Final Results Table

### Primary experiment (Phase 4): period + eclipse duration

| Metric | TESS test set | Gaia (vs proxy labels) |
|--------|--------------|------------------------|
| N | 810 | 489 |
| Accuracy | **92.5%** | **32.5%** |
| F1 (weighted) | 92.5% | 26.4% |
| Mean confidence | 0.941 | 0.860 |
| Calibration gap | **+0.016** | **+0.535** |
| Brier score | **0.060** | **0.488** |

*Calibration gap = mean confidence − accuracy. Positive = overconfident.*  
*Gaia accuracy = agreement with proxy labels, NOT physical ground truth.*

### High-confidence comparison (confidence 0.90–1.00)

| Survey | N in bin | Accuracy |
|--------|----------|----------|
| TESS | 653 | **96.6%** |
| Gaia (vs proxy) | 236 | **48.7%** |

On TESS: the model assigned confidence ≥ 0.90 to 80.6% of its predictions, and was right 96.6% of the time.  
On Gaia: the model assigned confidence ≥ 0.90 to 48.3% of its predictions, but was consistent with proxy labels only 48.7% of the time — barely better than random.

---

## 6. Phase 5 Experiment Comparison

| Experiment | Survey | N | Accuracy | Mean conf | Calib gap | Brier |
|------------|--------|---|----------|-----------|-----------|-------|
| Phase 4: period + ecl_dur | TESS test | 810 | 0.925 | 0.941 | +0.016 | 0.060 |
| Phase 4: period + ecl_dur | Gaia proxy | 489 | 0.325 | 0.860 | +0.535 | 0.488 |
| Exp 1: period only | TESS test | 810 | 0.762 | 0.860 | +0.098 | 0.174 |
| Exp 1: period only | Gaia proxy | 489 | 0.382 | 0.913 | +0.530 | 0.546 |
| Exp 3: period ≥ 1 day (2-feat) | Gaia proxy | 162 | 0.383 | 0.872 | +0.489 | 0.501 |

**What each experiment was testing and what it found:**

**A. Phase 4 (period + eclipse duration):** The main experiment. Eclipse duration has 66.9% feature importance; TESS and Gaia eclipse durations have very different distributions. Result: model works well on TESS, severely overconfident on Gaia.

**B. Experiment 1 (period only):** Tests whether eclipse duration is the *cause* of the overconfidence. If so, removing it should improve Gaia calibration. Result: removing eclipse duration *worsened* TESS accuracy (92.5% → 76.2%) and *increased* Gaia mean confidence (0.860 → 0.913) while barely changing the calibration gap (+0.535 → +0.530). Eclipse duration is a contributing factor but is not the sole cause.

**C. Experiment 3 (period ≥ 1 day, two features):** Tests whether the period distribution mismatch (Gaia dominated by short-period contact systems that TESS rarely trained on) is the primary cause. Restricts comparison to 162 Gaia sources in a range better represented by TESS training data. Result: marginal improvement — proxy accuracy 0.325 → 0.383, calibration gap +0.535 → +0.489. The model remains severely overconfident. Period mismatch is a contributing factor but is not the sole cause.

**Overall:** No single tested factor explains the calibration failure. The problem appears to be caused by a combination of feature distribution differences, period population differences, and proxy-label imperfection.

---

## 7. Confidence — What It Means and Why It Can Be Misleading

**Confidence** is the probability the model assigns to its chosen prediction. For a binary classifier, it ranges from 0.5 (minimum, because the model always picks the more likely class) to 1.0 (complete certainty).

In a well-calibrated model, a confidence of 0.90 means the prediction is correct about 90% of the time.

**On TESS:** confidence behaved reliably — the reliability diagram shows the TESS curve close to the perfect calibration line. High confidence generally meant high correctness.

**On Gaia:** confidence did NOT reliably indicate correctness relative to proxy labels. The model said "I am 90–100% confident" for 48.3% of Gaia predictions, but was consistent with proxy labels only 48.7% of the time in that bin. The reliability diagram shows the Gaia curve far below the calibration line at every confidence level.

**Key distinction:** Confidence and correctness are separate things. A model can be very confident about a prediction that turns out to be wrong. This is especially likely when the model is applied to data from a different source than it was trained on.

---

## 8. Brier Score

The Brier score measures how close a model's predicted probabilities are to the actual outcomes. Lower is better.

- Score of **0** = predicted probabilities matched outcomes perfectly.
- Score of **~0.25** = a random classifier assigning 50% probability to everything on a balanced dataset.
- Score above 0.25 means the predicted probabilities are actively misleading.

| Evaluation | Brier score | Interpretation |
|------------|-------------|----------------|
| Phase 4 — TESS | **0.060** | Excellent |
| Phase 4 — Gaia | **0.488** | Worse than random |
| Period-only — Gaia | **0.546** | Worse than random |
| Period ≥ 1 day — Gaia | **0.501** | Worse than random |

Every tested Gaia variant produces a Brier score nearly twice the random baseline. This is independent confirmation that the predicted probabilities are unreliable on Gaia — the numbers themselves (not just the classifications) should not be trusted.

---

## 9. Reliability Diagram

The reliability diagram plots predicted confidence (x-axis) against observed accuracy (y-axis). A perfectly calibrated model lies on the diagonal.

The diagram at `results/phase5/reliability_diagram_tess_vs_gaia.png` shows two panels:

**Panel 1 (Phase 4 baseline):**
- TESS curve is close to the diagonal — confidence ≈ accuracy at every level.
- Gaia curve falls far below the diagonal. In the 0.70–0.79 confidence bin, proxy-label agreement is only 10.2%.

**Panel 2 (Period-only model):**
- TESS curve shifts down slightly (lower accuracy as expected with a weaker model), still roughly calibrated.
- Gaia curve remains far below the diagonal, with proxy-label agreement of only 36.2% in the 0.90–1.00 bin.

**Important:** The y-axis for Gaia measures agreement with proxy labels — not physical correctness. Even so, the gap between confidence and agreement is large enough to be a clear scientific finding.

---

## 10. Final Scientific Answer

### One-sentence version

The model's confidence scores were reliable on the survey it was trained on (TESS) but became severely unreliable when the same model was applied to data from a different survey (Gaia), based on comparison with available Gaia proxy labels.

### Short academic version

A Random Forest classifier trained on NASA TESS eclipsing binary data demonstrated good accuracy (92.5%) and near-perfect calibration (Brier score 0.060, calibration gap +0.016) on held-out TESS data. When transferred to ESA Gaia DR3 data without retraining, the model's confidence became unreliable: proxy-label accuracy fell to 32.5%, the calibration gap increased to +0.535, and the Brier score rose to 0.488 — worse than a random predictor. Predictions made with ≥ 90% confidence on Gaia were consistent with proxy labels only 48.7% of the time, compared with 96.6% on TESS. Controlled experiments removing eclipse duration or restricting the period range each produced marginal improvements that left the model severely overconfident. The confidence failure is attributed to a combination of feature distribution differences between surveys, period population differences, and the known imperfection of the Gaia proxy labels. These factors cannot be fully separated with the available data.

### Beginner-friendly version

The project asked: when a machine-learning model is trained on data from one telescope and then used on data from a different telescope, can we trust how confident it says it is?

The answer found here is: no, not reliably.

The model worked well on data from TESS — when it said it was 95% confident, it was correct about 95% of the time. But when the same model was applied to Gaia data without any retraining, its confidence stopped matching its correctness. It often said it was 90–100% confident about predictions that turned out to be wrong about half the time (based on the best available Gaia labels).

This matters because in real astronomy, if a scientist uses a model's confidence score to decide which predictions to trust, they might make wrong decisions based on confidence scores that do not mean what they appear to mean.

---

## 11. Limitations

### Priority 1 — Most important

**Gaia proxy labels are imperfect.** The Gaia `model_type` proxy labels have a documented 39.2% agreement with independent VSX classifications. Some apparent "model errors" on Gaia may reflect label disagreements rather than model failures. However, even accounting for this, the calibration gap of +0.535 is far too large to be explained by label noise alone.

**Only two features were available.** Period and eclipse duration were the only features that could be derived from both surveys in comparable form. With more features, a different model might have performed differently — but these are the features that could be scientifically justified.

### Priority 2 — Important caveats

**Eclipse-duration measurements come from different pipelines.** TESS `prim_width_pf` and Gaia `derived_primary_ecl_duration` are conceptually the same quantity (eclipse width as a fraction of orbital period) but were derived by different software from different photometric data. The observed distribution difference (medians 0.079 vs 0.284) may partly reflect pipeline differences rather than purely physical differences.

**Gaia is dominated by short-period contact systems.** 66.9% of Gaia sources have periods below 1 day — a regime the TESS training data represents less well. This introduces a distribution shift that contributes to the cross-survey failure but cannot be fully separated from other causes.

**Small bins in the reliability diagram.** Several confidence bins (0.50–0.59, 0.60–0.69) contain fewer than 20 Gaia sources, making accuracy estimates in those bins unreliable.

**Gaia sample size is only 489 sources.** This is sufficient for a pilot experiment but too small for fine-grained calibration analysis.

### What this project does NOT prove

- This project does not prove that Random Forest is inherently unreliable.
- This project does not prove that cross-survey transfer is generally impossible.
- This project does not prove that the Gaia proxy labels are correct and the model is wrong.
- This project does not prove that any one specific factor (eclipse duration, period range, or proxy labels) is the sole cause of the calibration failure.
- The Gaia results measure agreement with proxy labels — they are not a direct measure of physical classification accuracy.

---

## 12. Scientific Consistency Checklist

Before publication or website deployment, verify:

- [x] Gaia proxy accuracy is never described as physical ground truth.
- [x] Eclipse duration distribution mismatch is described as a *contributing factor*, not the sole cause.
- [x] Random Forest is not described as inherently unreliable.
- [x] Cross-survey transfer is not described as generally impossible.
- [x] Confidence and correctness are consistently kept distinct.
- [x] TESS and Gaia results are clearly labelled throughout.
- [x] The research question is unchanged.
- [x] All numbers match the experiment files (verified against `results/phase5/phase5_metrics.csv` and `results/ml_summary.json`).
- [x] No unsupported scientific claims introduced.

---

*End of Phase 6 Final Results*
