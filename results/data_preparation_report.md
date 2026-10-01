# Cygnus Data Preparation Report

**Project:** Cygnus — Cross-Survey ML Confidence Evaluation  
**Date:** 2026-09-30  
**Author:** rachana.s@atriauniversity.edu.in  
**Stage:** Data Preparation — Phase 3  
**Follows:** `results/final_label_strategy.md`

---

## 1. Current Dataset Overview

### Raw files (unchanged)

| File | Location | Records | Description |
|------|----------|---------|-------------|
| NASA TESS Dataset.csv | `data/raw/tess/` | 4,584 rows × 28 columns | Pre-computed TESS EB catalog |
| 500 epoch-photometry CSVs | `data/raw/gaia/epoch_photometry/` | 500 files | One per Gaia source |
| gaia_source_coords.csv | `data/raw/gaia/catalog/` | 500 rows | RA, Dec, proper motion, mean magnitudes |
| gaia_vari_eclipsing_binary.csv | `data/raw/gaia/catalog/` | 500 rows | EB geometric model parameters, period (via frequency), eclipse parameters |
| gaia_vari_classifier_result.csv | `data/raw/gaia/catalog/` | 500 rows | Variability class (all ECL) and confidence score |
| gaia_vari_summary.csv | `data/raw/gaia/catalog/` | 500 rows | Pre-computed photometric statistics (mean, std, skewness, kurtosis, etc.) |

All raw files are **read-only** in this phase. No raw file has been modified.

### TESS dataset structure confirmed

28 columns:

`tess_id`, `signal_id`, `date_added`, `date_modified`, `source`, `ra`, `dec`, `pmra`, `pmdec`, `Tmag`, `bjd0`, `bjd0_uncert`, `period`, `period_uncert`, `morph_coeff`, `prim_width_pf`, `prim_depth_pf`, `prim_pos_pf`, `sec_width_pf`, `sec_depth_pf`, `sec_pos_pf`, `prim_width_2g`, `prim_depth_2g`, `prim_pos_2g`, `sec_width_2g`, `sec_depth_2g`, `sec_pos_2g`, `sectors`

---

## 2. TESS Cleaning

### Data quality issues verified

The following problems were identified by inspecting the actual data values:

**Issue 1: Records with `period = NaN`**

2 records have a completely missing period:

| tess_id | signal_id | period | morph_coeff |
|---------|-----------|--------|-------------|
| 233866651 | 1 | NaN | −1.000 |
| 430000969 | 1 | NaN | −1.000 |

Both records also have `morph_coeff = −1.000`. This combination indicates a **failed catalog fit** — the pipeline could not fit an orbital period or morphology to these light curves. Both values are sentinel flags (−1 = failed), not real measurements. These records cannot be used as training examples because the fundamental EB parameters are absent.

**Removal rule:** Remove records where `period` is NaN.  
**Records removed:** 2

---

**Issue 2: `morph_coeff` outside [0, 1]**

16 records have `morph_coeff` outside the valid range. After removing the 2 NaN-period records above, 14 additional records remain with out-of-range values:

- 2 records with `morph_coeff = −1.000` were already removed with the NaN period rule.
- 1 record with `morph_coeff = −0.005159` (nearly −1; another failed fit).
- 13 records with `morph_coeff` slightly above 1 (range: 1.002 to 1.073) — numerical overflow in the fitting pipeline.

The `morph_coeff` column is the classification target for this experiment. A value outside [0, 1] cannot be assigned a valid detached (0) or contact (1) label. Removing these records is the only scientifically sound option.

**Removal rule:** Remove records where `morph_coeff < 0` or `morph_coeff > 1` (after NaN-period removal).  
**Records removed:** 14

---

**Issue 3: `prim_depth_pf` values above 100**

5 records have physically impossible primary eclipse depths:

| tess_id | prim_depth_pf | morph_coeff | period |
|---------|--------------|-------------|--------|
| 67360334 | 27,771.6 | 0.274 | 3.428 |
| 57652994 | 2,268.9 | 0.367 | 4.279 |
| 175969976 | 1,941.7 | 0.479 | 6.698 |
| 30287190 | 348.8 | 0.237 | 3.124 |
| 299096773 | 146.0 | 0.406 | 7.407 |

Eclipse depth is a normalised fractional flux drop. A value of 1.0 means the star disappears completely during eclipse — the maximum physically possible value. Values of 146 to 27,771 are not physically meaningful and indicate either a measurement error in the original survey processing or a catastrophic fit failure. These records would introduce extreme outliers into the feature space and corrupt any ML model trained on them.

**Removal rule:** Remove records where `prim_depth_pf > 100`.  
**Records removed:** 5

---

### Cleaning summary

| Rule | Reason | Records removed |
|------|--------|-----------------|
| `period` is NaN | Failed fit; period is a required feature | 2 |
| `morph_coeff` outside [0, 1] | Cannot be labeled; sentinel or overflow value | 14 |
| `prim_depth_pf > 100` | Physically impossible; measurement or pipeline error | 5 |
| **Total removed** | | **21** |
| **Clean records retained** | | **4,563** |

**Note on overlap:** All 21 removed records had `tess_id` values that appear only once. None of the 6 tess_id duplicate pairs was partially removed. The 6 duplicate pairs (tess_ids with both signal_id=1 and signal_id=2) are fully intact in the cleaned dataset.

**Output file:** `data/processed/tess_clean.csv` — 4,563 rows × 29 columns (original 28 + `tess_label`)

---

### Remaining data quality notes

These issues are **known but not removed** because they are scientifically expected:

| Column | Missing in clean data | Why not removed |
|--------|----------------------|-----------------|
| `pmra`, `pmdec` | 147 (3.2%) | Not needed as ML features; expected for faint stars |
| `prim_depth_pf`, `prim_width_pf` | 517 (11.3%) | Fits failed for some sources; expected |
| `sec_depth_pf`, `sec_width_pf` | 2,084 (45.7%) | Many EBs have no detectable secondary eclipse — this is normal astronomy, not an error |

The secondary eclipse columns (`sec_*`) are missing for almost half the dataset. This is not a data error. Many eclipsing binaries (especially EA-type detached systems) show only a primary eclipse because the secondary star is too faint to produce a visible secondary dip. These columns **cannot be used as ML features** without introducing a severe selection bias.

---

## 3. Final TESS Label Distribution

**Label rule:** `morph_coeff < 0.5` → label 0 (detached-like); `morph_coeff ≥ 0.5` → label 1 (contact-like)

| Label | Meaning | morph_coeff range in data | Count | % |
|-------|---------|--------------------------|-------|---|
| **0 — detached-like** | Sharp eclipses, flat baseline | 0.002 to 0.500 | **2,209** | **48.4%** |
| **1 — contact-like** | Smooth, rounded light curve | 0.500 to 0.999 | **2,354** | **51.6%** |
| **Total** | | | **4,563** | **100%** |

The dataset is nearly balanced (48.4% vs 51.6%). This is a good property for a classification experiment.

**morph_coeff statistics by label:**

| Label | Min | Median | Max |
|-------|-----|--------|-----|
| 0 (detached) | 0.002 | 0.304 | 0.500 |
| 1 (contact) | 0.500 | 0.649 | 0.999 |

---

## 4. Gaia Dataset Used for Testing

All 500 Gaia sources are confirmed available with complete catalog metadata:

| Item | Coverage | Notes |
|------|----------|-------|
| model_type (proxy label) | 500 / 500 | Decision from `final_label_strategy.md` |
| Gaia proxy label (0 or 1) | 500 / 500 | 363 label-0, 137 label-1 |
| Period (from frequency) | 500 / 500 | Range: 0.209 to 196.1 days |
| RA / Dec coordinates | 500 / 500 | Used in completed cross-match |
| vari_summary statistics | 500 / 500 | Pre-computed mean, std, skewness, etc. |
| Derived eclipse parameters | 489 / 500 | 11 sources missing primary eclipse parameters |

**No Gaia file has been modified.** All 500 epoch-photometry files and all 4 catalog files remain as downloaded.

**Important reminders about Gaia labels (from `final_label_strategy.md`):**
- Gaia label 0 = detached-like: 363 sources (72.6%)
- Gaia label 1 = contact-like: 137 sources (27.4%)
- The Gaia sample is **more imbalanced** than TESS (72.6% vs 48.4% label-0).
- The proxy label is based on `model_type`, not a direct physical measurement.
- The 39.2% VSX agreement rate is a documented limitation.

---

## 5. Common Feature Investigation

For the cross-survey experiment to work, the **same type of information** must be available from both TESS and Gaia. A Random Forest trained on TESS features will later be applied to Gaia data. If the features mean different things in each survey, the model will produce unreliable results.

For each candidate feature, this section documents: what TESS provides, what Gaia provides, whether they are comparable, and the reason for the decision.

---

### Feature 1: Orbital Period

| | TESS | Gaia |
|--|------|------|
| **Column** | `period` | `frequency` → period = 1 / frequency |
| **Units** | Days | Days (after conversion) |
| **How derived** | Computed by TESS EB catalog pipeline from TESS light curve | Computed by Gaia EB variability pipeline from Gaia light curve |
| **Completeness** | 4,563 / 4,563 (100%) | 500 / 500 (100%) |
| **Min / Median / Max** | 0.049 / 2.208 / 314.6 days | 0.209 / 0.457 / 196.1 days |

**Are they comparable?**

Yes. Both TESS and Gaia measure the **orbital period of the same physical phenomenon** — how long one complete revolution of the two stars takes. The methods differ (different telescopes, different pipelines) but the physical quantity is the same, measured in the same units.

**Important caveat:** The period distributions are very different. TESS median period is 2.21 days; Gaia median is 0.46 days. This means the Gaia test set is dominated by short-period systems that are relatively rare in the TESS training set. A model trained on TESS period data will be evaluated on a very different period distribution when applied to Gaia.

**Decision: ACCEPTED.** Period is the primary shared feature for this experiment.

---

### Feature 2: Eclipse Duration (Phase Fraction)

| | TESS | Gaia |
|--|------|------|
| **Column** | `prim_width_pf` | `derived_primary_ecl_duration` |
| **Units** | Phase fraction (0–1) | Phase fraction (0–1) |
| **How derived** | Width of primary eclipse fitted to the phase-folded TESS light curve | Duration of primary eclipse derived from the fitted Gaussian model |
| **Completeness** | 4,046 / 4,563 (88.7%) | 489 / 500 (97.8%) |
| **Min / Median / Max** | 0.001 / 0.079 / 0.407 | 0.001 / 0.284 / 0.400 |

**Are they comparable?**

Potentially, with important caveats.

Both columns measure the same physical concept: **how long the eclipse lasts, expressed as a fraction of the orbital period**. A value of 0.1 means the eclipse lasts 10% of each orbit. Both are in the same units (dimensionless phase fraction, 0–1).

However, there are two concerns:

1. **Very different distributions.** TESS median eclipse width is 0.079 (7.9% of the orbit). Gaia median eclipse duration is 0.284 (28.4% of the orbit). This is a large difference. It likely reflects two things: (a) the Gaia sample is dominated by short-period contact systems, which genuinely have wider eclipses because the stars are close, and (b) potentially different fitting conventions between the TESS and Gaia pipelines.

2. **Suspicious maximum cap in Gaia.** In the Gaia data, the eclipse duration appears to hit a hard ceiling at exactly 0.400. The 75th and 95th percentiles are both exactly 0.4000, meaning over a quarter of Gaia sources have eclipse durations at or near this cap. This suggests the Gaia pipeline imposes a maximum allowed eclipse duration of 0.4 phase units. This is not an issue in the TESS data (TESS maximum is 0.407, which appears natural). If a significant fraction of Gaia sources are capped at 0.4, the information content of this feature for those sources is limited.

**Decision: CONDITIONALLY ACCEPTED.** Eclipse duration can be used as a second feature, but only if both of these conditions are met:
- The distribution difference is explicitly documented as a limitation
- The Gaia cap at 0.4 is noted in the report
- The feature is described as "approximately comparable" rather than "equivalent"

**Note:** Eclipse width also has high correlation with morph_coeff in TESS (|r| = 0.81). This is physically expected (wider eclipses → rounder light curves → higher morph_coeff), not a data leakage problem. But it means the model trained on TESS will rely heavily on this feature, making the accuracy of the cross-survey comparison sensitive to how well the two eclipse duration measurements agree.

---

### Feature 3: Mean Brightness

| | TESS | Gaia |
|--|------|------|
| **Column** | `Tmag` | `mean_mag_g_fov` in vari_summary |
| **Photometric band** | TESS band: ~600–1000 nm (red-sensitive) | Gaia G band: ~330–1050 nm (broad optical) |
| **Completeness** | 4,563 / 4,563 (100%) | 500 / 500 (100%) |
| **Range** | 2.28 – 17.65 mag | 10.81 – 20.04 mag |

**Are they comparable?**

No. TESS and Gaia use fundamentally different photometric systems. A star with Tmag = 12.0 will have a different G-band magnitude in Gaia because the two bandpasses weight different wavelengths differently. The absolute brightness values are not transferable between surveys. Feeding a model Tmag from TESS and G-band magnitude from Gaia would give the model meaningless numbers that happen to have the same column name.

**Decision: REJECTED.** Mean brightness cannot be used as a shared cross-survey feature.

---

### Feature 4: Eclipse Depth / Amplitude

| | TESS | Gaia |
|--|------|------|
| **Column** | `prim_depth_pf` | `derived_primary_ecl_depth` |
| **Units** | Fractional flux (0–1; depth of 0.1 = 10% brightness drop) | Magnitudes (log scale) |
| **Completeness** | 4,046 / 4,563 (88.7%) | 489 / 500 (97.8%) |

**Are they comparable?**

No. The two columns use different units (fractional flux vs. magnitudes). While a mathematical conversion exists (depth_flux = 1 − 10^(−depth_mag/2.5)), this would not solve the underlying problem: the two values are derived using different fitting pipelines in different photometric bands. The systematic offsets between the two measurements are unknown and could be substantial.

**Decision: REJECTED.** Eclipse depth cannot be used as a shared cross-survey feature in this form.

---

### Feature 5: Standard Deviation of Brightness

| | TESS | Gaia |
|--|------|------|
| **Column** | Not available from the TESS catalog | `std_dev_mag_g_fov` in vari_summary |

**Are they comparable?**

No. The TESS catalog contains pre-derived eclipse parameters, not raw light curve statistics. Computing standard deviation of TESS brightness would require downloading and reprocessing raw TESS light curve files, which is beyond the current dataset. Gaia has this pre-computed in vari_summary, but TESS does not.

**Decision: REJECTED** (TESS data unavailable).

---

### Feature 6: Skewness of Brightness Distribution

| | TESS | Gaia |
|--|------|------|
| **Column** | Not available from the TESS catalog | `skewness_mag_g_fov` in vari_summary |

**Decision: REJECTED** (same reason as standard deviation — not available from TESS catalog).

---

## 6. Features Selected for the Future ML Experiment

Based on the investigation above, the following features are selected for the cross-survey ML experiment:

| # | Feature name | TESS column | Gaia column | Completeness (TESS) | Completeness (Gaia) | Confidence |
|---|-------------|-------------|-------------|---------------------|---------------------|-----------|
| 1 | Period (days) | `period` | `1 / frequency` | 100% | 100% | High |
| 2 | Primary eclipse duration (phase fraction) | `prim_width_pf` | `derived_primary_ecl_duration` | 88.7% | 97.8% | Moderate |

**Target variable (not a feature):**
- TESS: `tess_label` (from `morph_coeff`): 0 = detached-like, 1 = contact-like
- Gaia: proxy label from `model_type`: 0 = detached-like, 1 = contact-like

### What to do about missing values in Feature 2

`prim_width_pf` is missing for 517 TESS records (11.3%). When this feature is used, these records will need to be handled. Two options:
- **Option A:** Train the model only on records that have both features complete (4,046 TESS records).
- **Option B:** Impute the missing values using the median of the training set.

Option A is cleaner scientifically. Option B retains more training data. This decision is deferred to the ML pipeline design.

### Why so few shared features?

This limitation has a specific cause: the TESS dataset is a **pre-computed catalog** that provides eclipse parameters derived from the light curve, not the raw light curve itself. The Gaia vari_summary table provides statistical measures of the raw photometry (standard deviation, skewness, etc.) that TESS simply did not publish in the catalog.

The only information that is genuinely available from both surveys at the same level of processing is the orbital period and the eclipse duration as a fraction of the orbital period.

This feature limitation is important for the experiment design. It must be clearly stated in the final report.

---

## 7. Features Rejected and Why

| Feature | TESS source | Gaia source | Reason for rejection |
|---------|------------|-------------|---------------------|
| Mean brightness | `Tmag` (T-band) | `mean_mag_g_fov` (G-band) | Different photometric bands; values not numerically transferable |
| Eclipse depth | `prim_depth_pf` (fractional flux) | `derived_primary_ecl_depth` (magnitudes) | Different units; different pipeline definitions |
| Secondary eclipse depth | `sec_depth_pf` | `derived_secondary_ecl_depth` | 45.7% missing in TESS; also different units |
| Secondary eclipse width | `sec_width_pf` | `derived_secondary_ecl_duration` | 45.7% missing in TESS |
| Standard deviation | Not available | `std_dev_mag_g_fov` | Not in TESS catalog; requires raw light curves |
| Skewness | Not available | `skewness_mag_g_fov` | Not in TESS catalog; requires raw light curves |
| Kurtosis | Not available | `kurtosis_mag_g_fov` | Not in TESS catalog; requires raw light curves |
| Amplitude (range) | Not available (same as std issue) | `range_mag_g_fov` | Not available in same form from TESS |
| `morph_coeff` | Classification TARGET | N/A | Must never be used as an input feature |
| Eclipse width 2G model | `prim_width_2g`, `sec_width_2g` | No equivalent in Gaia | Gaia uses a different model structure |

---

## 8. Data Leakage Checks

The following potential leakage risks have been investigated:

---

**Check 1 — `morph_coeff` used as both feature and label**

`morph_coeff` is the classification target. It has been converted into a binary label (`tess_label`) and must never appear in the input feature matrix. Status: **No leakage** — this is enforced by design. `morph_coeff` will be dropped from the feature set.

---

**Check 2 — Eclipse width columns as proxies for `morph_coeff`**

Eclipse width columns (prim_width_pf, sec_width_pf, prim_width_2g, sec_width_2g) have correlations of 0.81–0.84 with `morph_coeff`. This is physically expected: wider eclipses mean the stars overlap longer, which produces a rounder light curve (higher morph_coeff).

**Is this data leakage?** No. These columns are independently measured from the same light curve; they are not computed from `morph_coeff`. The high correlation reflects genuine astronomical physics.

**Is this a problem for the experiment?** It means the model will rely heavily on eclipse width to make predictions. This is fine for TESS internal performance. For the cross-survey application, it means the experiment's validity depends critically on whether TESS `prim_width_pf` and Gaia `derived_primary_ecl_duration` are truly comparable (see Section 5 for this assessment).

---

**Check 3 — Duplicate `tess_id` and train/test leakage**

6 tess_id values appear twice in the cleaned dataset (signal_id = 1 and 2). These are the same physical star observed with two different eclipse signals in the same photometric aperture.

If a naive random split is applied at the row level, the same physical star could appear in both training and test sets. This is data leakage because the model could implicitly recognise the star and classify it based on memory rather than features.

**Affected tess_ids:** 63459761, 251094451, 266958963, 318210930, 375422201, 441794509

**Solution:** Use a group-based train/test split (see Section 9). All rows sharing the same `tess_id` must be assigned to the same split.

---

**Check 4 — Gaia data entering TESS training**

The Gaia epoch photometry files and catalog files are stored separately in `data/raw/gaia/`. They will only be used as the cross-survey test set. No Gaia data will be included in the TESS training dataset.

Status: **No risk** — enforced by the experimental design.

---

**Check 5 — VSX external labels in training**

The 209 VSX independent labels were used only as a consistency check for the Gaia proxy labels (see `final_label_strategy.md`). They are not attached to the TESS dataset and will not be used in model training.

Status: **No risk.**

---

**Check 6 — Preprocessing statistics computed on the full dataset**

Any scaling or normalisation applied to the features must be **fitted only on the training portion** of the TESS data. The fitted parameters (e.g., mean and standard deviation for StandardScaler) must then be applied without re-fitting to the TESS test set and to the Gaia data.

If preprocessing were fitted on the full TESS dataset (including the test portion), information from the test set would leak into the training process.

Status: **Risk exists — will be enforced in implementation.** See Section 10.

---

**Check 7 — TESS–Gaia spatial overlap (from previous phase)**

The TESS–Gaia coordinate cross-match found **0 of 500 Gaia sources** within 10 arcseconds of any TESS source (documented in `tess_gaia_crossmatch_report.md`). The closest pair is 444.4 arcseconds apart and confirmed to be a different physical star by proper motion comparison.

Status: **No spatial overlap. No leakage risk from shared physical objects.**

---

## 9. Train/Test Split Design

### Requirement

The TESS training/test split must prevent the same astronomical object from appearing in both training and test sets. Because 6 tess_id values appear twice (signal_id = 1 and 2), a naive random row split would risk putting both signals from the same star into different folds.

### Proposed method: Group-based split on unique tess_id

**Step 1:** Extract the list of unique tess_id values.  
**Step 2:** Randomly assign 80% of the unique tess_ids to the training set and 20% to the test set, using a fixed random seed for reproducibility.  
**Step 3:** Select all rows where tess_id belongs to the training set → training data.  
**Step 4:** Select all rows where tess_id belongs to the test set → test data.

This guarantees that both signal_id = 1 and signal_id = 2 rows for the same tess_id always end up in the same fold.

In scikit-learn, this is implemented using `GroupShuffleSplit` or by manually splitting on the unique tess_id list before selecting rows.

### Expected split sizes

| | Unique tess_ids | Approximate rows |
|--|-----------------|-----------------|
| Training set (80%) | ~3,645 | ~3,649 |
| TESS test set (20%) | ~912 | ~913 |
| Gaia test set | 500 (separate, fixed) | 500 |

*(Exact row counts depend on which 6 duplicate tess_ids land in train vs. test.)*

### Why 80/20?

With 4,563 clean records, an 80/20 split gives about 3,649 training examples. This is sufficient for a Random Forest classifier without being overly small. A 70/30 split would also be reasonable; 80/20 is the conventional choice and gives more training data.

### Cross-survey evaluation

The Gaia dataset is **entirely separate** from the train/test split:
- The model is trained on TESS training data only.
- TESS test performance is evaluated on the TESS test split.
- Cross-survey performance is evaluated on the full 500 Gaia sources.
- No Gaia data is used to train or tune the model.

```
TESS data (4,563 rows)
        │
        ├── 80% → Training set (~3,649 rows)
        │         ↓
        │     Random Forest trained here
        │         ↓
        ├── 20% → TESS test set (~913 rows)
        │         ↓
        │     TESS internal evaluation
        │
GAIA data (500 rows, completely separate)
        ↓
    Cross-survey evaluation (same trained model, no retraining)
```

---

## 10. Preprocessing Plan

### Why preprocessing is needed

Both features (period and eclipse duration) are on very different scales and have different distributions. Period ranges from 0.05 to 314.6 days; eclipse duration ranges from 0.001 to 0.41 phase fraction. Without scaling, period would dominate any distance-based or regularisation-based calculation.

Random Forests are less sensitive to feature scale than linear models, but standardisation is still good practice for reproducibility and for any future model comparisons.

### Proposed preprocessing steps

**Step 1 — Drop excluded columns**

The following columns must be excluded from the feature matrix:
- `morph_coeff` (it is the target, not a feature)
- `tess_label` (the encoded target; must not appear as a feature)
- All identification columns: `tess_id`, `signal_id`, `ra`, `dec`, `pmra`, `pmdec`, `source`, `sectors`, `date_added`, `date_modified`
- Eclipse parameters that are not cross-survey compatible (see Section 7)

**Step 2 — Handle missing values in `prim_width_pf`**

If eclipse duration is included as Feature 2, 517 TESS records have missing `prim_width_pf`.

Options:
- **A (recommended):** Restrict training to records with complete data for all selected features. This gives 4,046 records — still a very large training set.
- **B:** Impute missing values using the median computed from the training set only (never from the full dataset or from the test set). Apply the same imputed value to the test set and Gaia data.

**Step 3 — Feature scaling**

Apply `StandardScaler` from scikit-learn to standardise each feature (subtract mean, divide by standard deviation).

**CRITICAL RULE:**
- Fit `StandardScaler` on the **training set only**.
- Apply (transform) the fitted scaler to the TESS test set without refitting.
- Apply (transform) the fitted scaler to the Gaia test set without refitting.

This ensures that information about the test set distributions does not influence the preprocessing. Fitting the scaler on the full dataset before splitting is a common mistake that inflates test performance.

**Step 4 — Log transformation of period (optional)**

Period has a highly skewed distribution (median 2.2 days, max 314.6 days). A log₁₀ transformation would make the distribution more symmetric and reduce the influence of a few very long-period systems. This is optional but recommended, and should be applied after the train/test split (with the log transformation treated as part of the preprocessing pipeline).

### Full preprocessing order

```
For each feature vector:

1. Select features: [period, prim_width_pf (optional)]
2. Handle missing prim_width_pf (impute with training median, or drop rows)
3. Apply log10 to period (optional)
4. StandardScaler fitted on training data → applied to all sets

Scalers are fitted ONCE on training data.
Scalers are applied (transform only) to TESS test and Gaia test.
```

---

## 11. Remaining Risks and Limitations

The following risks and limitations must be clearly acknowledged in the final project report:

**Risk 1: Only 1–2 shared features**

Only orbital period (and optionally eclipse duration) can be used as cross-survey features. This is a very small feature set. The classification performance on TESS alone may be reasonable with these features (period alone separates detached and contact systems to some extent), but the model will not be learning the full light curve shape information that would be available if raw light curves were included.

This is not a reason to abandon the experiment — it is an inherent limitation of using pre-computed catalogs rather than raw photometry.

**Risk 2: Eclipse duration distributions differ substantially**

TESS prim_width_pf median = 0.079; Gaia derived_primary_ecl_duration median = 0.284. This 3.6× difference in typical values reflects both the different EB populations in the two surveys and possibly different fitting conventions. When the Random Forest is applied to Gaia, the eclipse duration feature will be in a range it has rarely seen during training. This could reduce model confidence or accuracy on Gaia.

Additionally, over a quarter of Gaia sources have eclipse duration capped at exactly 0.400. This cap likely reflects a constraint in the Gaia fitting pipeline and is not present in the TESS data. The information content of eclipse duration for these capped sources is limited.

**Risk 3: Period distribution mismatch**

The Gaia sample is dominated by short-period contact systems (median 0.46 days), while TESS has a median of 2.21 days. Any model trained on TESS will be evaluated primarily on systems in a period range where the TESS training data is sparse. The model may produce lower confidence or systematically different predictions for very short-period systems — not because the cross-survey transfer failed, but simply because short-period EBs are rare in the training set.

**Risk 4: Gaia proxy labels have a documented 39.2% agreement with VSX**

The Gaia model_type labels used for evaluation are imperfect (see `final_label_strategy.md`). A prediction from the Random Forest that disagrees with the Gaia proxy label may be wrong, or it may be that the proxy label is wrong. This ambiguity cannot be fully resolved without better ground-truth labels.

**Risk 5: Small Gaia test set (500 sources)**

500 sources is small for evaluating confidence calibration across multiple confidence bins. Confidence curves (reliability diagrams) typically need hundreds to thousands of examples per bin to be stable. With 500 sources split across 5–10 confidence bins, some bins may have fewer than 50 examples, making the per-bin accuracy estimate unreliable.

---

## 12. Readiness for ML

### Pre-ML checklist

| Condition | Status |
|-----------|--------|
| Raw TESS data available and verified | ✓ |
| Raw Gaia data available and verified | ✓ |
| TESS data cleaned (21 invalid records removed) | ✓ |
| TESS labels defined (morph_coeff threshold applied) | ✓ |
| Gaia labels defined (model_type mapping) | ✓ (from `final_label_strategy.md`) |
| TESS–Gaia spatial overlap confirmed = 0 (no leakage) | ✓ (from `tess_gaia_crossmatch_report.md`) |
| Shared features identified and justified | ✓ |
| Feature limitations documented | ✓ |
| Leakage risks documented | ✓ |
| Train/test split strategy designed | ✓ |
| Preprocessing plan designed | ✓ |
| Cleaned TESS data saved to `data/processed/` | ✓ |

### Decision

**The data preparation phase is complete. The project is ready to move to ML training.**

The experiment is scientifically limited — only 1–2 genuinely shared features, imperfect Gaia proxy labels, and a substantial period distribution mismatch — but all these limitations are documented and understood. The research question ("can we trust the model's confidence scores?") can still be meaningfully investigated with this setup, provided the limitations are stated clearly in the final report.

**Immediate next steps:**

1. **Feature matrix construction** — create a clean `X_tess` (TESS features), `y_tess` (TESS labels), `X_gaia` (Gaia features), `y_gaia` (Gaia proxy labels).
2. **Group-based train/test split** — split TESS data by unique tess_id (80/20).
3. **Preprocessing** — fit StandardScaler on training data; transform all sets.
4. **Train Random Forest** — on TESS training data.
5. **Evaluate on TESS test set** — accuracy, precision, recall, F1, confusion matrix.
6. **Apply to Gaia** — predict class and confidence (predict_proba) for all 500 sources.
7. **Confidence calibration analysis** — compare predicted confidence with actual correctness.
