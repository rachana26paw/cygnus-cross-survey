# Cygnus — Data Validation Report

**Date:** 2026-09-30
**Stage:** Data Reconnaissance and Validation
**Status:** Completed — critical problems identified before any ML training

---

## 1. Dataset Inventory

| Item | Location | Records | Notes |
|------|----------|---------|-------|
| NASA TESS Eclipsing-Binary Catalog | `data/raw/tess/NASA TESS Dataset.csv` | 4 584 rows × 28 columns | Object-level catalog |
| Gaia DR3 Epoch Photometry | `data/raw/gaia/epoch_photometry/` | 500 files | One file per source |

---

## 2. TESS Dataset Assessment

### Structure

The TESS file is a **pre-computed catalog of eclipsing binary stars** identified in TESS light curves.
It does **not** contain raw light-curve data. Every row is a star that has already been classified as an eclipsing binary.

**Columns (28):**

| Column | Description |
|--------|-------------|
| `tess_id` | TESS Input Catalog identifier |
| `signal_id` | Signal number for this star (usually 1; occasionally 2 when two signals are detected) |
| `ra`, `dec` | Sky coordinates (degrees) |
| `pmra`, `pmdec` | Proper motion (mas/yr) — 147 missing values |
| `Tmag` | TESS magnitude (mean brightness) |
| `bjd0`, `bjd0_uncert` | Reference epoch and its uncertainty |
| `period`, `period_uncert` | Orbital period (days) and its uncertainty |
| `morph_coeff` | Morphology coefficient: **key quantity** (see below) |
| `prim_width/depth/pos_pf` | Primary eclipse width, depth, position (phase-folded fit) |
| `sec_width/depth/pos_pf` | Secondary eclipse parameters (phase-folded fit) |
| `prim_*/sec_*_2g` | Same parameters from a 2-Gaussian model fit |
| `sectors` | TESS observing sectors |
| `source` | Data origin (all: "Light Curve File (LCF)") |
| `date_added`, `date_modified` | Catalog timestamps |

### Key statistics

| Feature | Min | Median | Max | Missing |
|---------|-----|--------|-----|---------|
| Period (days) | 0.049 | 2.21 | 314.6 | 2 (0.0%) |
| Tmag | 2.28 | 10.34 | 17.65 | 0 |
| morph_coeff | −1.0 | 0.51 | 1.07 | 0 |
| prim_depth_pf | 0.000138 | 0.076 | 27 771 | 519 (11.3%) |
| sec_depth_pf | 0.000289 | 0.062 | 16.95 | 2 092 (45.6%) |

### Data quality problems in TESS

**Problem 1 — No class label column**
The dataset contains **only** eclipsing binaries. There is no column distinguishing "eclipsing binary" from "not an eclipsing binary". All 4 584 entries are already identified EBs.

This is the most critical problem. A Random Forest classifier needs at least **two classes**. With only one class present, a standard binary classification cannot be trained as originally envisioned.

*What this means for the experiment:* The original idea of classifying "is this star an eclipsing binary?" cannot be done with this dataset alone, because there are no non-EB examples. The classification target must be redefined (see Section 12).

---

**Problem 2 — morph_coeff values outside [0, 1]**
The morphology coefficient should range from 0 (detached EB, two separate stars) to 1 (contact EB, stars touching). However:
- 14 records have values slightly **above 1** (up to 1.073) — likely a numerical issue, not physically meaningful
- 2 records have value **−1.000** with `period = NaN` — these are sentinel values indicating a failed fit
- Together, 16 records (0.3%) have morph_coeff outside [0, 1]

---

**Problem 3 — prim_depth_pf extreme outliers**
Five records have primary eclipse depths greater than 100, with the largest being 27 771. Eclipse depth in normalised flux should be between 0 and 1. Values this large suggest measurement errors or unphysical fits for specific stars. These records need to be flagged or removed before training.

---

**Problem 4 — Secondary eclipse parameters: 45% missing**
`sec_depth_pf` and `sec_width_pf` are missing for 2 092 of 4 584 records (45.6%). This is expected astronomically — many eclipsing binaries do not show a detectable secondary eclipse — but it means these columns **cannot be used as ML features** without handling the missing values carefully.

---

**Problem 5 — 6 duplicate `tess_id` values**
Six TESS IDs appear twice in the catalog, each with `signal_id` = 1 and `signal_id` = 2. These are stars where two separate eclipsing signals were detected (e.g., a blended source containing two EB systems). There are **no true duplicates** — every (`tess_id`, `signal_id`) pair is unique. These are valid records but must not be split carelessly between training and test sets.

---

### The morph_coeff opportunity

Even though there is no EB vs. non-EB label, the **morph_coeff provides a natural classification target within EBs**:

| Class | morph_coeff range | Count | Meaning |
|-------|------------------|-------|---------|
| Detached EB | 0.0 – 0.5 | 2 214 | Two separate stars; clear eclipses |
| Contact/semi-contact EB | 0.5 – 1.0 | 2 354 | Stars nearly or fully touching |
| Problematic (outside [0,1]) | < 0 or > 1 | 16 | To be excluded |

This gives a roughly balanced two-class problem that is scientifically meaningful. The research question would then become: "Can an ML model trained on TESS to distinguish **detached vs. contact EBs** give trustworthy confidence scores when applied to Gaia data?"

---

## 3. Gaia Dataset Assessment

### Structure

Each of the 500 files contains the **epoch photometry** for one Gaia source.
Unlike TESS, this is **raw time-series data** — individual brightness measurements taken at different times. No pre-derived eclipse parameters are stored in these files.

**Columns (25):**

| Column | Description |
|--------|-------------|
| `source_id` | Gaia DR3 source identifier |
| `transit_id` | Individual observation identifier |
| `g_transit_time` | Time of G-band observation |
| `g_transit_flux`, `g_transit_flux_error` | G-band flux and its uncertainty |
| `g_transit_flux_over_error` | Signal-to-noise ratio |
| `g_transit_mag` | G-band magnitude |
| `bp_obs_time`, `bp_flux`, `bp_flux_error`, `bp_mag` | Blue-photometer band |
| `rp_obs_time`, `rp_flux`, `rp_flux_error`, `rp_mag` | Red-photometer band |
| `variability_flag_g_reject` | True if this G observation was flagged as bad |
| `variability_flag_bp_reject` | True if this BP observation was flagged as bad |
| `variability_flag_rp_reject` | True if this RP observation was flagged as bad |
| `g_other_flags`, `bp_other_flags`, `rp_other_flags` | Bitmask quality flags |
| `rejected_by_photometry` | True if the observation was rejected by the photometric pipeline |

### Key statistics

| Property | Value |
|----------|-------|
| Number of sources | 500 |
| Observations per source: minimum | 18 |
| Observations per source: maximum | 81 |
| Observations per source: mean | 41.9 |
| Total observations across all files | 20 947 |
| Files with ALL BP missing | 0 |
| Files with ALL RP missing | 0 |
| G-band rejection rate (sample) | ~4.3% |
| BP-band rejection rate (sample) | ~7.4% |
| RP-band rejection rate (sample) | ~7.2% |

### Data quality observations

- All 500 source IDs are unique. No duplicate sources.
- Every file has at least 18 observations — enough to compute basic statistics but not many.
- BP and RP data have individual missing observations within files (Gaia does not always observe all bands simultaneously). This is normal.
- The `g_other_flags` bitmask contains various quality indicators. The most common value is 1 (a routine flag). Observations with unusual flag values should be inspected carefully before deriving features.
- There are no files where all photometry is rejected.

### What labels do the Gaia sources have?

The 500 Gaia sources were selected because they appear in the **Gaia DR3 eclipsing binary variability catalogue**. They are all eclipsing binaries, but their **subtype** (detached/contact) is NOT stored in the epoch photometry files. That information lives in the separate Gaia DR3 variability catalogue table (`gaiadr3.vari_eclipsing_binaries`), which is not currently in the dataset.

**This is a critical gap.** Without the Gaia EB subtype labels, there is no way to check whether the model's predictions are correct — which is exactly what the research question asks.

---

## 4. Cross-Match Assessment

### Can TESS and Gaia sources be matched to the same stars?

TESS identifies stars by `tess_id` (a TESS Input Catalog number). Gaia identifies stars by `source_id` (a Gaia DR3 number). **These are different identifiers.** There is no Gaia source_id column in the TESS dataset.

To determine whether any TESS stars are the same physical objects as the 500 Gaia sources, a **coordinate-based cross-match** would be needed:
1. Obtain the RA and Dec for each Gaia source_id (from the Gaia DR3 main catalog or a catalogue query)
2. Match against TESS RA/Dec within a small angular radius (e.g., 2 arcsec), applying proper-motion corrections because TESS and Gaia observations were taken at different epochs

**Proper motion correction note:** TESS data span roughly 2018–present; Gaia DR3 astrometry is referenced to epoch 2016.0. For most stars the shift is small, but `pmra` and `pmdec` are present in TESS (though 147 values are missing) and can be used if needed.

**Why does cross-matching matter?** The experiment requires that TESS trains the model and Gaia provides an independent test. If some TESS training stars are actually the same physical objects as Gaia test stars, the independence assumption breaks down — this would be a data leakage risk.

*Current status:* Cross-match has NOT been performed. It is recommended as the next step after obtaining Gaia coordinates.

---

## 5. Label Assessment

### TESS labels

| Question | Answer |
|----------|--------|
| Is there a class/type column? | No |
| Are all records the same type? | Yes — all are eclipsing binaries |
| Can morph_coeff serve as a classification target? | Yes, if split into detached vs. contact |
| Are morph_coeff values reliable? | Mostly yes — 16 records need to be excluded |

### Gaia labels

| Question | Answer |
|----------|--------|
| Are the 500 sources confirmed EBs? | Yes (they come from the Gaia DR3 EB variability catalogue) |
| Is the EB subtype (detached/contact) stored in the epoch photometry files? | No |
| Can Gaia EB subtype be obtained? | Yes, from the Gaia DR3 variability catalogue — but it is not in the current dataset |
| Can we evaluate model correctness without subtype labels? | No |

**Conclusion:** Labels cannot be invented. The Gaia DR3 variability catalogue data must be obtained before the cross-survey evaluation can be performed.

---

## 6. Feature Compatibility

For each candidate feature, the table below explains how it is obtained from each survey and whether the measurements are truly comparable.

### Period

| | TESS | Gaia |
|--|------|------|
| **How obtained** | Directly stored in the `period` column. Pre-computed by the catalog pipeline from TESS light curves. | NOT stored in the epoch photometry files. Must be derived from time-series flux (e.g., Lomb-Scargle periodogram) OR fetched from the Gaia DR3 variability catalogue. |
| **Scientific comparability** | Potentially comparable — both measure the same physical quantity (orbital period). However, TESS periods are catalog-quality; Gaia periods derived from 18–81 sparse observations will be less precise and may fail for long-period systems. |
| **Recommended?** | Yes, as a feature — with caution about Gaia period quality for sparse data. Fetch from Gaia variability catalogue if possible, rather than deriving from epoch photometry. |

---

### Mean brightness

| | TESS | Gaia |
|--|------|------|
| **How obtained** | `Tmag` column. TESS bandpass is ~600–1000 nm (red-sensitive). | Mean of `g_transit_mag` per source. Gaia G band is ~330–1050 nm (broad optical). |
| **Scientific comparability** | **Not directly equivalent.** Both measure optical brightness but with different sensitivity curves and zero-point systems. The numbers will differ for the same star. They cannot be treated as the same feature. |
| **Recommended?** | Can be used as separate features (Tmag for TESS, mean G mag for Gaia), but the model must never be trained on Tmag and then asked to predict using mean G mag as if they are the same thing. |

---

### Amplitude / variability

| | TESS | Gaia |
|--|------|------|
| **How obtained** | `prim_depth_pf` gives the primary eclipse depth as a fraction of total flux (a proxy for amplitude). 519 missing values. Some extreme outliers. | Can be computed from epoch G-band flux: (max flux − min flux) / median flux. Or: standard deviation of g_transit_mag. |
| **Scientific comparability** | Different definitions and methods. TESS eclipse depth is derived from a fitted model. Gaia amplitude is a statistical measure of raw observations. They both relate to how much the brightness changes, but are not numerically equivalent. |
| **Recommended?** | Usable, but carefully. A normalised variability measure (e.g., amplitude / mean brightness) computed consistently from both surveys' data would be more defensible than mixing catalog eclipse depth from TESS with raw spread from Gaia. |

---

### Standard deviation of flux

| | TESS | Gaia |
|--|------|------|
| **How obtained** | **Not stored in the TESS catalog.** The catalog gives eclipse parameters, not raw flux values. Computing std would require re-downloading and reprocessing raw TESS light curves. | Straightforward: std of `g_transit_flux` per source file, after excluding rejected observations. |
| **Scientific comparability** | Cannot be obtained from the current TESS data without extra processing. |
| **Recommended?** | Not recommended with the current TESS dataset. |

---

### Skewness

| | TESS | Gaia |
|--|------|------|
| **How obtained** | **Not stored in the TESS catalog.** Same problem as std. | Can be computed from `g_transit_flux` per source file. |
| **Scientific comparability** | Cannot be obtained from the current TESS data. |
| **Recommended?** | Not recommended with the current TESS dataset. |

---

### Summary: recommended features

| Feature | Available from TESS? | Available from Gaia? | Use? |
|---------|---------------------|---------------------|------|
| Period | Yes (catalog) | Possible (derive or fetch) | Yes |
| Mean brightness | Yes (Tmag) | Yes (mean g_transit_mag) | Careful — different bands |
| Eclipse depth / amplitude | Partial (prim_depth_pf, 11% missing) | Derivable from epoch flux | Careful — different definitions |
| Std of flux | No (would need raw light curves) | Yes (derivable) | No |
| Skewness | No (would need raw light curves) | Yes (derivable) | No |
| morph_coeff | Yes (classification TARGET) | No (not in epoch files) | Target only — needs Gaia variability catalogue for labels |

---

## 7. Missing Data

### TESS missing values

| Column | Missing count | % missing | Action required |
|--------|--------------|-----------|-----------------|
| `pmra`, `pmdec` | 147 | 3.2% | Not used as ML features; minor issue |
| `period` | 2 | 0.0% | Remove these 2 rows before training |
| `prim_depth_pf` | 519 | 11.3% | Needs imputation or removal strategy |
| `sec_depth_pf` | 2 092 | 45.6% | Too many missing; likely unusable as a feature |
| `sec_width_pf` | 2 092 | 45.6% | Same |
| `prim_width_2g` | 613 | 13.4% | Needs handling |
| `sec_width_2g` | 1 964 | 42.8% | Too many missing |

Secondary eclipse parameters are missing for roughly half the dataset because many eclipsing binaries do not produce a detectable secondary eclipse. This is not a data error — it is an astronomical reality. Imputing these values would be scientifically unjustified.

### Gaia missing values

Within individual Gaia files, some BP and RP observations are missing (the telescopes do not always observe in all bands simultaneously). This is normal. The fraction of missing observations varies by file. After removing rejected observations, each source still has at least ~15 usable G-band measurements for feature derivation.

---

## 8. Duplicate Data

### TESS

- 6 `tess_id` values appear twice, each with a different `signal_id` (1 and 2). These are legitimate entries representing two eclipsing signals in the same photometric aperture. They must be kept together (both rows for the same tess_id should go to the same train/test split to avoid leakage).
- There are **0 true duplicates** at the (`tess_id`, `signal_id`) level.

### Gaia

- All 500 `source_id` values are unique. No duplicates.

---

## 9. Data-Quality Issues

| Issue | Dataset | Severity | Description |
|-------|---------|----------|-------------|
| No class label column | TESS | **Critical** | All records are EBs. Cannot train EB vs. non-EB classifier without adding non-EB data. |
| morph_coeff outside [0,1] | TESS | Moderate | 16 records, including 2 sentinel values of −1. Remove before training. |
| Extreme prim_depth_pf outliers | TESS | Moderate | 5 records with depth > 100; max = 27 771. Likely data errors. Remove or cap. |
| Missing secondary parameters | TESS | Low–Moderate | Scientifically expected; 45% missing. Cannot use these as features. |
| No EB subtype for Gaia | Gaia | **Critical** | Cannot evaluate model correctness without labels. |
| No period in Gaia epoch files | Gaia | Moderate | Must derive or fetch separately. |
| Sparse observations in some Gaia files | Gaia | Moderate | 1 source has only 18 obs; 67 have 20–30. Feature derivation quality will vary. |

---

## 10. Data-Leakage Risks

| Risk | Assessment |
|------|-----------|
| Gaia sources appearing in TESS training data | **Unknown until cross-match is performed.** If the same physical stars are in both datasets, the Gaia test set is not truly independent. |
| tess_id duplicates split across train/test | Risk if splitting naively. Both signal_id=1 and signal_id=2 for the same tess_id must stay in the same fold. |
| morph_coeff used as both feature AND target | If morph_coeff is the classification target, eclipse parameters derived FROM morph_coeff should not also be used as input features. |
| Preprocessing fitted on full dataset | Standard risk. All scalers, imputers, etc. must be fitted on training data only, then applied to test data. |
| Gaia data influencing TESS model training | Cannot happen with the current plan — Gaia data is kept separate. No risk currently. |

---

## 11. Problems That Must Be Solved

### Problem 1 (Critical) — No labels for a two-class problem

The TESS dataset has no non-EB examples. A binary "EB vs. not-EB" classifier cannot be trained.

**Solution options:**
- **Option A (Recommended within current scope):** Redefine the target as **detached vs. contact EB** using `morph_coeff`. This gives 2 214 vs. 2 354 examples — a near-balanced problem. After cleaning (removing 16 out-of-range records and 2 NaN-period records), ~4 550 usable training examples remain.
- **Option B:** Download additional TESS data for non-EB variable stars or non-variable stars. This would enable an "EB vs. non-EB" classifier but requires significant extra data collection.

---

### Problem 2 (Critical) — No Gaia EB subtype labels

The 500 Gaia sources have no subtype label in the current files. Without labels, model predictions cannot be verified as correct or incorrect, making the core research question unanswerable.

**Solution:** Download the Gaia DR3 eclipsing binary variability catalogue for these 500 source_ids. The table `gaiadr3.vari_eclipsing_binaries` (accessible via the Gaia Archive) contains the geometric model type for each source. This would provide the ground-truth label needed to assess model reliability.

---

### Problem 3 (Important) — Feature mismatch

The TESS catalog gives pre-derived eclipse parameters. The Gaia files give raw epoch photometry. Standard deviation and skewness cannot be computed from the TESS catalog without re-downloading raw TESS light curves.

**Solution:** Focus on features that CAN be obtained from both:
- Period (TESS: catalog; Gaia: variability catalogue or Lomb-Scargle)
- Mean brightness (with the understanding that TESS and Gaia use different photometric bands)
- Primary eclipse depth / amplitude (TESS: `prim_depth_pf`; Gaia: derived from epoch flux range)

---

### Problem 4 (Important) — TESS–Gaia cross-match not done

It is unknown whether any of the 500 Gaia sources are also in the TESS training set.

**Solution:** Perform a coordinate-based spatial cross-match using TESS RA/Dec and Gaia DR3 coordinates (must be queried separately). Any overlap must be removed from training.

---

### Problem 5 (Minor) — TESS data quality issues

16 out-of-range morph_coeff records and 5 extreme prim_depth_pf outliers need to be flagged and removed before training.

---

## 12. What Is Currently Possible

Given the data as it stands today, the following is possible **without any additional data collection:**

1. **Describe and characterise both datasets** — done in this report.
2. **Derive statistical features from all 500 Gaia sources** — mean G magnitude, amplitude, and possibly a rough period estimate from Lomb-Scargle periodogram.
3. **Clean the TESS dataset** — remove 16 bad morph_coeff records, 2 NaN-period records, and flag 5 extreme depth outliers.
4. **Define a feature set for TESS training** that uses only `period`, `Tmag`, and `prim_depth_pf` (the three features most likely to be comparable to Gaia-derived equivalents).

The following is **NOT possible without additional data:**

1. Training a meaningful classifier — no Gaia labels to evaluate correctness.
2. Cross-match — no Gaia coordinates in the current files.
3. Period derivation from Gaia epoch data — requires running a periodogram (computationally feasible but not yet done).
4. Answering the research question — depends on Gaia labels.

---

## 13. Recommended Next Steps

### Step 1 (Highest priority): Download Gaia DR3 variability catalogue data

Query the Gaia Archive for the 500 source_ids to retrieve:
- Geometric model type (EA = detached, EB = semi-detached, EW = contact)
- Orbital period (as computed by Gaia)
- Any additional EB parameters

This data is freely available from `https://gea.esac.esa.int/archive/` using an ADQL query on `gaiadr3.vari_eclipsing_binaries`.

This step resolves **Problem 2** (Gaia labels) and provides a Gaia-derived period to resolve part of **Problem 3** (feature mismatch).

---

### Step 2: Perform TESS–Gaia coordinate cross-match

Query Gaia DR3 for the coordinates of the 500 sources and match against TESS RA/Dec.

This resolves **Problem 4** (leakage risk) and tells us whether the datasets are truly independent.

---

### Step 3: Define a clean, comparable feature set

Based on what becomes available after Steps 1 and 2, define the exact features to use in both datasets. The current best candidates are:

| Feature | TESS source | Gaia source |
|---------|-------------|-------------|
| Period | `period` column | `gaiadr3.vari_eclipsing_binaries` |
| Mean brightness | `Tmag` | Mean of `g_transit_mag` |
| Amplitude | `prim_depth_pf` (after cleaning) | (max − min) of `g_transit_mag` |

These three features are available or derivable from both surveys, are scientifically related to eclipsing binary behaviour, and can be computed without requiring raw TESS light curves.

---

### Step 4: Clean the TESS dataset

Remove:
- 2 records with `period = NaN`
- 16 records with `morph_coeff` outside [0, 1]
- 5 records with `prim_depth_pf > 100`

Result: approximately 4 561 clean records, split roughly equally between detached (morph_coeff < 0.5) and contact (morph_coeff ≥ 0.5) EBs.

---

### Step 5 (Only after Steps 1–4 complete): Begin ML pipeline

Train a Random Forest classifier on TESS to distinguish detached vs. contact EBs.
Apply the trained model to Gaia sources and evaluate whether high-confidence predictions are actually correct.

**Do not begin this step until Gaia labels are obtained.**

---

## Summary

The proposed Cygnus experiment is **scientifically feasible in principle**, but **cannot be performed with the current dataset alone**. Two critical gaps must be filled first:

1. Gaia subtype labels (detached vs. contact EB) — needed to evaluate whether model predictions are correct
2. Gaia coordinates for cross-matching against TESS — needed to ensure the training and test sets are independent

Once those gaps are filled, a meaningful and scientifically defensible experiment can be run.
