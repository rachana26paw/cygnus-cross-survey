# Cygnus — Gaia Metadata Assessment

**Date:** 2026-09-30
**Stage:** Gaia Catalogue Retrieval and Label Verification
**Follows:** `results/data_validation_report.md`

---

## Overview

This report documents the retrieval and analysis of Gaia DR3 catalogue metadata for the
500 Gaia sources already present in `data/raw/gaia/epoch_photometry/`.

Four Gaia catalogue tables were queried programmatically via the Gaia Archive TAP service.
No Gaia epoch-photometry files were modified.

---

## 1. Files Saved

All retrieved data was saved to `data/raw/gaia/catalog/`.

| File | Contents | Rows |
|------|----------|------|
| `gaia_source_coords.csv` | RA, Dec, parallax, proper motion, G/BP/RP mean magnitudes | 500 |
| `gaia_vari_eclipsing_binary.csv` | Geometric model parameters: frequency (period), eclipse depths, model_type | 500 |
| `gaia_vari_classifier_result.csv` | Variability classifier result (class name + score) | 500 |
| `gaia_vari_summary.csv` | Pre-computed photometric statistics: mean, std, skewness, kurtosis, range, IQR, etc. | 500 |

---

## 2. Source ID Match Rate

All 500 source IDs returned a match in every Gaia catalogue table queried.

| Table | Expected | Matched | Missing |
|-------|----------|---------|---------|
| gaiadr3.gaia_source | 500 | 500 | 0 |
| gaiadr3.vari_eclipsing_binary | 500 | 500 | 0 |
| gaiadr3.vari_classifier_result | 500 | 500 | 0 |
| gaiadr3.vari_summary | 500 | 500 | 0 |

---

## 3. RA and Dec

RA and Dec are now available for all 500 Gaia sources from `gaiadr3.gaia_source`.

- RA range: 41.56 – 90.00 degrees
- Dec range: 35.51 – 51.49 degrees
- Proper motions (pmra, pmdec): available for all 500 sources

**Important observation:** The 500 Gaia sources are confined to a **single limited sky region**
(roughly the Auriga / Perseus area of the northern sky). The TESS catalog covers nearly the
entire sky. Only **69 of 4 584 TESS EBs** fall within this same RA/Dec region. This limits
the number of candidate overlapping objects in a cross-match to at most 69 pairs.

---

## 4. Period

Period is available for all 500 Gaia sources.

Gaia stores frequency (cycles per day) in `gaiadr3.vari_eclipsing_binary`.
Period in days = 1 / frequency.

| Statistic | Value |
|-----------|-------|
| Sources with period | 500 / 500 |
| Minimum period | 0.21 days |
| Maximum period | 196.1 days |
| Median period | 0.46 days |
| Mean period | 1.38 days |

The median Gaia period (0.46 days) is **very different** from the TESS median period
(2.21 days). This is discussed in Section 8.

**Period distribution:**

| Period range (days) | Sources |
|--------------------|---------|
| < 0.5 | 263 (52.6%) |
| 0.5 – 1 | 73 (14.6%) |
| 1 – 2 | 68 (13.6%) |
| 2 – 5 | 45 (9.0%) |
| 5 – 10 | 27 (5.4%) |
| 10 – 20 | 14 (2.8%) |
| > 20 | 10 (2.0%) |

---

## 5. Available Gaia EB-Related Columns

### 5a. gaiadr3.vari_eclipsing_binary (39 columns)

The most important columns:

| Column | Description |
|--------|-------------|
| `source_id` | Gaia DR3 identifier |
| `frequency` | Frequency of EB light curve (cycles/day); period = 1/frequency |
| `frequency_error` | Uncertainty on frequency |
| `model_type` | Type of geometric model fitted (**key classification proxy** — see Section 6) |
| `num_model_parameters` | Number of free parameters in the model |
| `global_ranking` | Quality of the EB model fit (0=worst, 1=best) |
| `derived_primary_ecl_depth` | Derived primary eclipse depth (magnitude) |
| `derived_secondary_ecl_depth` | Derived secondary eclipse depth (magnitude) |
| `derived_primary_ecl_duration` | Duration of primary eclipse (phase fraction) |
| `derived_secondary_ecl_duration` | Duration of secondary eclipse (phase fraction) |
| `geom_model_gaussian1_depth` | Depth of Gaussian 1 component in the fitted model |
| `geom_model_gaussian2_depth` | Depth of Gaussian 2 component in the fitted model |
| `geom_model_cosine_half_period_amplitude` | Amplitude of the ellipsoidal (sinusoidal) component |

Missing values:
- Primary eclipse parameters: 11 missing (2.2%)
- Secondary eclipse parameters: 36 missing (7.2%)
- Ellipsoidal component: 363 missing (72.6%) — because only 137 sources have an ellipsoidal component in their model

---

### 5b. gaiadr3.vari_classifier_result (5 columns)

| Column | Description |
|--------|-------------|
| `best_class_name` | Gaia variability class assigned (e.g., ECL) |
| `best_class_score` | Confidence score for that class assignment (0–1) |
| `classifier_name` | Which classifier was used |

**Finding:** ALL 500 sources have `best_class_name = 'ECL'` (Eclipsing).
This confirms they are all classified as eclipsing variables. However, this is a
**single category** — Gaia's variability classifier does not distinguish between
detached and contact EBs at this level.

Classifier score distribution:

| Score range | Sources | Interpretation |
|-------------|---------|----------------|
| 0.0 – 0.3 | 104 (20.8%) | Low confidence ECL classification |
| 0.3 – 0.5 | 71 (14.2%) | Below-median confidence |
| 0.5 – 0.9 | 259 (51.8%) | Moderate to good confidence |
| 0.9 – 1.0 | 66 (13.2%) | High confidence |

104 sources (21%) have ECL scores below 0.3. This means that for roughly 1 in 5 sources,
Gaia's own classifier was not confident they are eclipsing variables.

---

### 5c. gaiadr3.vari_summary — Statistical Features (68 columns)

This table provides **pre-computed photometric statistics** for all 500 sources.
These are extremely useful because they represent the exact same type of features
(std, skewness, etc.) that the validation report identified as unavailable from the
TESS catalog.

Key available features (all 500 non-null for G band):

| Column | What it measures | Missing |
|--------|-----------------|---------|
| `mean_mag_g_fov` | Mean G magnitude | 0 |
| `std_dev_mag_g_fov` | Standard deviation of G magnitude | 0 |
| `range_mag_g_fov` | Max − min G magnitude (amplitude) | 0 |
| `skewness_mag_g_fov` | Skewness of G magnitude distribution | 0 |
| `kurtosis_mag_g_fov` | Kurtosis of G magnitude distribution | 0 |
| `iqr_mag_g_fov` | Interquartile range of G magnitude | 0 |
| `mad_mag_g_fov` | Median absolute deviation | 0 |
| `abbe_mag_g_fov` | Abbe value (smoothness / autocorrelation measure) | 0 |
| `mean_mag_bp` / `std_dev_mag_bp` | BP band equivalents | 3 |
| `mean_mag_rp` / `std_dev_mag_rp` | RP band equivalents | 3 |

This resolves the earlier problem about std and skewness being unavailable from
the Gaia epoch photometry. They are pre-computed in `vari_summary`.

---

## 6. Classification / Model Fields — Unique Values

### model_type in gaiadr3.vari_eclipsing_binary

| model_type | Count | Median period (days) | What it means |
|-----------|-------|---------------------|---------------|
| TWOGAUSSIANS | 347 (69.4%) | 0.44 | Both eclipses fitted with Gaussians; no ellipsoidal component |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE1 | 91 (18.2%) | 0.38 | Both eclipses + sinusoidal variation on primary |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE2 | 26 (5.2%) | 1.03 | Both eclipses + sinusoidal variation on secondary |
| ONEGAUSSIAN | 16 (3.2%) | 1.71 | Only primary eclipse detected |
| ELLIPSOIDAL | 11 (2.2%) | 0.34 | No distinct eclipses; only sinusoidal (tidal deformation) variation |
| ONEGAUSSIAN_WITH_ELLIPSOIDAL | 9 (1.8%) | 0.79 | One eclipse + sinusoidal component |

**What model_type means physically (with caution):**

The `model_type` describes **which mathematical shape was used to fit the light curve**.
It does NOT directly label the system as EA (detached), EB (semi-detached), or EW (contact).

However, there is a physical correlation:
- ELLIPSOIDAL and ONEGAUSSIAN_WITH_ELLIPSOIDAL systems show sinusoidal variation without
  clear eclipse dips. This pattern typically occurs in **contact or near-contact systems**
  where stars are so close their shapes are deformed.
- TWOGAUSSIANS systems show two distinct eclipse dips. This pattern can occur in **detached
  (EA-type) or semi-detached (EB-type)** systems.
- TWOGAUSSIANS_WITH_ELLIPSOIDAL systems show both eclipse dips AND sinusoidal modulation.
  This typically indicates a **semi-detached or contact-like** system.

**Critical warning:** This correlation is imperfect. `model_type` is determined by a
fitting algorithm, not by physical measurement. A TWOGAUSSIANS fit does not prove a
detached system; it proves only that two eclipses could be fitted. The converse is also
true: an ELLIPSOIDAL fit does not prove contact.

### best_class_name in gaiadr3.vari_classifier_result

Only one category found across all 500 sources: `'ECL'` (Eclipsing).

Gaia's variability classifier assigns broad variability types (ECL, SOLAR_LIKE, RR_LYR,
CEPHEID, etc.), but does **not** distinguish subtypes within ECL.

**There is no EA/EB/EW field in the standard Gaia DR3 tables.**

---

## 7. Quality Assessment

### global_ranking (0=worst, 1=best)

| Statistic | Value |
|-----------|-------|
| Minimum | 0.40 |
| Mean | 0.54 |
| Maximum | 0.72 |
| Sources with ranking ≥ 0.7 | 4 (0.8%) |
| Sources with ranking < 0.5 | 141 (28.2%) |

No source has a global_ranking below 0.4, so the EB geometric model fit is at least
plausible for all 500 sources. However, only 4 sources achieve a ranking above 0.7.
The overall quality is moderate — the Gaia EB models are workable but not high-precision.

### Classifier score concern

175 of 500 sources (35%) have an ECL classification score below 0.5. This means Gaia's
own classifier was uncertain whether these are truly eclipsing variables for over one-third
of the sample. This is worth noting when defining the experiment: the Gaia "ground truth"
labels are themselves uncertain for a significant fraction of the sample.

---

## 8. Can Gaia Information Be Mapped to TESS morph_coeff Classes?

This section addresses the key scientific question directly: is the Gaia catalogue data
good enough to provide ground-truth labels equivalent to the TESS morph_coeff split?

### What TESS morph_coeff measures

morph_coeff is a continuous number (0–1) that measures the **shape** of the TESS light curve:
- Values near 0: sharp, narrow eclipse dips with a flat baseline. These are detached EBs.
- Values near 1: smooth, rounded light curves with no flat baseline. These are contact EBs.

The threshold morph_coeff < 0.5 = detached, ≥ 0.5 = contact is a reasonable simplification
but it is an approximation — the underlying quantity is continuous.

### What Gaia provides

Gaia provides:
- `model_type`: a fitting category that correlates with, but is not identical to, the
  detached/contact distinction
- `vari_classifier_result.best_class_name`: only "ECL" — no subtype
- No morph_coeff equivalent column
- No EA/EB/EW classification in the standard tables

### A potential mapping

The following approximate mapping could be considered, but is NOT proven equivalent:

| Gaia model_type | Proposed mapping | Reason |
|----------------|-----------------|--------|
| ELLIPSOIDAL | Contact / EW-like | No distinct eclipses; sinusoidal variation only |
| ONEGAUSSIAN_WITH_ELLIPSOIDAL | Contact-like | One eclipse + sinusoidal; close system |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE1 | Semi-detached / contact-like | Eclipses + sinusoidal |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE2 | Semi-detached / contact-like | Eclipses + sinusoidal |
| TWOGAUSSIANS | Detached / semi-detached | Two eclipses; no sinusoidal |
| ONEGAUSSIAN | Uncertain | Only primary visible |

Under this scheme:
- "Detached-like" (TWOGAUSSIANS + ONEGAUSSIAN): 363 sources (72.6%)
- "Contact-like" (all others with ellipsoidal component): 137 sources (27.4%)

This is an **unbalanced split** (72.6% vs. 27.4%). The TESS split is nearly equal
(2 214 vs. 2 354), so the Gaia sample is skewed.

### Why the mapping is not automatic

The label systems are different in three ways:

1. **Definition**: TESS morph_coeff is a continuous fit to the light curve shape. Gaia
   model_type is a categorical choice by a fitting algorithm.

2. **Measurement system**: TESS observes in a red-sensitive band. Gaia observes in a
   broad optical band. The measured light curve shapes differ.

3. **Period distribution**: TESS median period is 2.21 days; Gaia median is 0.46 days.
   The Gaia sample is dominated by very short-period contact systems. The distributions
   are fundamentally different. A model trained on TESS will be applied to a very different
   period distribution in Gaia.

### TESS morph_coeff < 0.5 ≠ TWOGAUSSIANS

These two criteria are NOT the same label. A star with morph_coeff = 0.48 (TESS "detached")
could perfectly well have a TWOGAUSSIANS_WITH_ELLIPSOIDAL fit in Gaia if it shows slight
sinusoidal modulation. The labels could disagree for a significant fraction of stars.

**Conclusion:** The Gaia catalogue data does not provide a label that is automatically
and provably equivalent to the TESS morph_coeff-based class. A mapping can be defined,
but it is an approximation that introduces label uncertainty. This uncertainty must be
documented if the mapping is adopted.

---

## 9. Period Distribution Mismatch — A Significant Concern

The Gaia sample is heavily biased toward **very short periods** (52.6% under 0.5 days).
The TESS training set has median period 2.21 days — five times longer.

This matters because:
- Very short-period EBs (< 0.5 days) are almost exclusively contact (EW-type) systems
- Longer-period EBs include detached (EA-type) and semi-detached (EB-type) systems
- A Random Forest trained on TESS (which spans the full EB distribution) will be evaluated
  predominantly on contact systems when applied to the Gaia sample
- The model may have low confidence on these short-period, contact-type objects because
  the training data proportions differ

This is not a reason to abandon the experiment, but it is a scientific fact that must
be stated clearly in any findings. It means the cross-survey confidence evaluation will
be biased by the Gaia sample's composition.

---

## 10. Summary: What Is Now Available

| Information | Status |
|-------------|--------|
| RA and Dec for all 500 Gaia sources | ✓ Retrieved |
| Period for all 500 Gaia sources | ✓ Retrieved (from frequency) |
| Geometric model type (model_type) | ✓ Retrieved — 6 categories |
| Gaia broad variability class | ✓ All = "ECL"; no subtype |
| Pre-computed statistics (std, skewness, etc.) | ✓ Retrieved from vari_summary |
| EA/EB/EW classification | ✗ Not available in standard Gaia DR3 tables |
| Direct morph_coeff equivalent | ✗ Does not exist in Gaia |

---

## 11. Decisions Required Before Proceeding

These are scientific decisions that cannot be made automatically. They must be made
explicitly before the ML pipeline is designed.

### Decision 1: How to define the Gaia ground-truth label

**Option A — Use model_type as a proxy**
Map ELLIPSOIDAL + WITH_ELLIPSOIDAL models → "contact-like", TWOGAUSSIANS + ONEGAUSSIAN → "detached-like".
This gives 363 vs. 137 sources (unbalanced). The mapping is approximate.

**Option B — Use a period-based threshold**
Short-period EBs (e.g., period < 0.5 days) are very likely contact systems; long-period systems are more likely detached.
This is statistically justified but ignores individual light-curve shape.

**Option C — Accept label uncertainty and measure only model confidence**
Rather than checking correctness against a label, measure only the distribution of
predicted probabilities from the TESS model when applied to Gaia sources. If the model
gives confident predictions for Gaia sources that look nothing like TESS training data,
that itself is a finding.

**Option D — Cross-match to an external EA/EB/EW catalogue**
The SIMBAD, VSX (AAVSO Variable Star Index), or GCVS catalogues contain EA/EB/EW
classifications for many known variable stars. Matching the 500 Gaia source_ids (via
coordinates) to these catalogues could provide traditional labels.

### Decision 2: Whether the period distribution mismatch is acceptable

The Gaia sample is dominated by short-period contact systems. The TESS training set is
not. Should the Gaia test set be trimmed to sources whose periods overlap better with
the TESS training distribution? Or should this imbalance be documented as part of the
experiment?

---

## 12. Recommended Next Steps

1. **Decide the Gaia labelling strategy** (Decision 1 above). The simplest scientifically
   defensible option is Option A (model_type mapping) documented explicitly as approximate.

2. **Perform the TESS–Gaia cross-match** using RA/Dec now available for all 500 Gaia sources.
   Only 69 TESS EBs are in the same sky region, so the actual number of overlapping stars
   is likely small (possibly zero after 2-arcsec matching), but this must be confirmed.

3. **Assess feature comparability** using the newly available vari_summary statistics.
   This table directly resolves the earlier concern about std and skewness:
   - Gaia has pre-computed: mean_mag_g_fov, std_dev_mag_g_fov, skewness_mag_g_fov, range_mag_g_fov
   - TESS has: Tmag (mean brightness), prim_depth_pf (amplitude proxy), period
   - The Gaia vari_summary statistics cannot be directly compared to TESS catalog parameters
     (different bands, different methods), but they CAN serve as Gaia-side features
     if TESS features are defined at the same conceptual level

4. **Do NOT begin cleaning or ML training** until Decision 1 is made.

---

## Summary Table

| Retrieval item | Result |
|----------------|--------|
| Sources matched in vari_eclipsing_binary | 500 / 500 |
| Sources with period | 500 / 500 |
| Sources with RA/Dec | 500 / 500 |
| Gaia EB subtype (EA/EB/EW) | Not available |
| Best available proxy for EB type | model_type (6 fitting categories) |
| Pre-computed statistics available | Yes — vari_summary provides mean, std, skewness, kurtosis, range, IQR for G, BP, RP |
| Classifier confirmation | All 500 confirmed ECL (eclipsing), but 35% with score < 0.5 |
| Period distribution bias | Yes — Gaia dominated by short-period contact systems |
| Sky coverage overlap | Limited — 69 TESS EBs in same region |
| Cross-match performed | Not yet |
| Ready for ML training | No — labelling decision required first |
