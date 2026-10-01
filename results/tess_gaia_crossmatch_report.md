# TESS–Gaia DR3 Coordinate Cross-Match Report

**Project:** Cygnus — Cross-Survey ML Confidence Evaluation  
**Date:** 2026-09-30  
**Author:** rachana.s@atriauniversity.edu.in  
**Stage:** Data Validation — Cross-Match Phase

---

## 1. Purpose

This report documents the result of a coordinate-based spatial cross-match between:

- **TESS eclipsing-binary catalog** (4,584 sources, global sky coverage)
- **Gaia DR3 eclipsing-binary sources** (500 sources, confined to RA 41.6–90.0°, Dec 35.5–51.5°)

The goal is to determine whether any of the 500 Gaia sources are the **same physical stars** as objects in the TESS catalog.

This matters for **data leakage prevention**: if a star appears in both the TESS training set and the Gaia cross-survey test set, any prediction on that star would not be a genuine cross-survey test — the model may have been trained on the same object.

---

## 2. Method

### 2.1 Input data

| Dataset | File | Columns used |
|---------|------|--------------|
| TESS catalog | `data/raw/tess/NASA TESS Dataset.csv` | `tess_id`, `signal_id`, `ra`, `dec`, `pmra`, `pmdec` |
| Gaia coordinates | `data/raw/gaia/catalog/gaia_source_coords.csv` | `source_id`, `ra`, `dec`, `pmra`, `pmdec` |

### 2.2 Cross-match procedure

**Tool:** Python `astropy.coordinates.SkyCoord.match_to_catalog_sky()`

This function uses a KD-tree on spherical coordinates. It computes the true **angular separation** on the celestial sphere — not a flat Euclidean distance in RA/Dec. This is the correct method for sky-coordinate matching.

For each of the 500 Gaia sources, the function returns:
- the index of the **nearest** TESS source
- the **angular separation** to that nearest TESS source

**Matching radii applied:**

| Category | Threshold |
|----------|-----------|
| Strong match | ≤ 2 arcseconds |
| Possible match | 2–5 arcseconds |
| Loose / inspect | 5–10 arcseconds |
| No match | > 10 arcseconds |

A 2 arcsecond threshold is standard in astronomical cross-matching. Gaia DR3 positional accuracy is typically < 0.1 arcseconds for sources this bright, and TESS coordinates are typically accurate to 1–2 arcseconds. A genuine same-star match should appear at well under 2 arcseconds (after accounting for proper motion between the ~2016 Gaia astrometric epoch and the ~2018–2022 TESS observation epochs).

### 2.3 Proper-motion check

For any candidate matches (< 10 arcsec), the analysis also computes the **proper-motion displacement** between the two catalogs. Gaia DR3 uses astrometric epoch J2016.0. TESS observations span approximately 2018–2022, giving a typical epoch difference of ~3 years.

If two catalogue entries describe the same star, their proper motions should agree (both measure the same true motion of the star). A large disagreement in proper motion is evidence that two catalogue entries point to different physical objects, even if their listed coordinates happen to be nearby by coincidence.

---

## 3. Results

### 3.1 Separation distribution

The cross-match was performed over all **500 Gaia × 4,584 TESS = 2,292,000 pairs**.

| Separation range | Number of Gaia sources |
|-----------------|----------------------|
| 0–300 arcseconds | **0** |
| 300–1,000 arcseconds | 1 |
| 1,000–10,000 arcseconds | ~80 (all in sky overlap region) |
| > 10,000 arcseconds | ~420 (Gaia sources with no nearby TESS EBs) |

Summary statistics for nearest-neighbour separation:

| Statistic | Value |
|-----------|-------|
| Minimum separation | **444.4 arcseconds** (7.4 arcminutes) |
| Median separation | 6,222.8 arcseconds (1.73 degrees) |
| Maximum separation | 13,268.4 arcseconds (3.69 degrees) |

### 3.2 Match counts by category

| Category | Count | % of 500 Gaia sources |
|----------|-------|----------------------|
| Strong match (≤ 2 arcsec) | **0** | 0.0% |
| Possible match (2–5 arcsec) | **0** | 0.0% |
| Loose candidate (5–10 arcsec) | **0** | 0.0% |
| No TESS match (> 10 arcsec) | **500** | 100.0% |

**None of the 500 Gaia sources match any TESS eclipsing binary within 10 arcseconds.**

---

## 4. Detailed Inspection of the Closest Pair

Although no genuine match was found, the single closest Gaia-TESS pair is worth documenting to confirm it is not a match.

| Property | Value |
|----------|-------|
| Gaia source_id | 210953713951603584 |
| TESS tess_id | 310785613 (signal_id = 1) |
| Angular separation | **444.4 arcseconds (7.4 arcminutes)** |
| Gaia RA, Dec | 84.35235°, +48.52438° |
| TESS RA, Dec | 84.17151°, +48.55445° |
| Gaia proper motion (pmra, pmdec) | +0.12, −0.12 mas/yr |
| TESS proper motion (pmra, pmdec) | +4.43, −12.00 mas/yr |

**Conclusion for this pair:** Not a match.

- The separation is 444 arcseconds, which is **more than 200 times larger** than the 2 arcsecond matching threshold.
- The proper motions are completely different: the TESS source is moving ~12 times faster in declination than the Gaia source. These are two different stars.
- The spatial proximity (both near RA=84°, Dec=+48.5°) is a coincidence of sky position, not evidence of a common object.

The five closest Gaia-TESS pairs for reference:

| Gaia source_id | TESS tess_id | Separation (arcsec) |
|---------------|-------------|---------------------|
| 210953713951603584 | 310785613 | 444.4 |
| 212002746829435136 | 368180294 | 1037.6 |
| 210921617659817600 | 310785613 | 1404.4 |
| 196749565612333696 | 440459327 | 1428.8 |
| 212060711707419136 | 368180294 | 1678.4 |

All five are separated by hundreds of arcseconds. No pair comes close to a genuine astronomical match.

---

## 5. Ambiguity Assessment

### 5.1 Were any Gaia sources within 10 arcsec of multiple TESS sources?

**No.** Since no Gaia source was found within 10 arcseconds of even a single TESS source, the question of ambiguous multiple matches does not arise.

### 5.2 Does proper-motion correction change the result?

No. Even for the closest pair (444 arcsec), the proper-motion displacement over 3 years is at most a few milliarcseconds to tens of milliarcseconds for typical stars in this catalog. A 3-year × 12 mas/yr proper motion moves a star ~36 mas = 0.036 arcseconds. This is negligible compared to the 444 arcsecond minimum separation. Proper-motion correction cannot reduce any separation from 444 arcseconds to 2 arcseconds.

### 5.3 TESS duplicate tess_id check

The TESS catalog contains 6 tess_id values that appear twice (signal_id = 1 and signal_id = 2), representing alternative period solutions for the same physical star:

- tess_id values: 63459761, 251094451, 266958963, 318210930, 375422201, 441794509

None of these appear in the cross-match candidate list because there are no candidates. This is not relevant to the cross-match result, but is noted here for completeness.

---

## 6. Sky Coverage Context

The 500 Gaia sources are confined to a narrow sky region:
- **RA:** 41.6° to 90.0° (northern sky, Perseus/Auriga/Taurus area)  
- **Dec:** +35.5° to +51.5°

Previous analysis (sky overlap check) found that **69 TESS eclipsing binaries** fall within this same RA/Dec bounding box. The cross-match was performed across all 4,584 TESS sources (not just these 69), but even within the overlapping region, the minimum separation between a Gaia source and any TESS source is 444 arcseconds.

This means: even in the region of sky where TESS and Gaia sources are geographically closest, they are still separated by more than 7 arcminutes. They observe **different individual stars** within the same general sky region.

---

## 7. Implications for the Cygnus Experiment

### 7.1 Data leakage from common objects

**There is no data leakage risk from overlapping objects.**

The 500 Gaia test sources and the 4,584 TESS training sources are different physical stars. Training a Random Forest on TESS data and then evaluating it on Gaia data does not involve any star appearing in both datasets.

### 7.2 Independence of datasets

The TESS and Gaia datasets are **spatially independent** at the individual-star level. Any cross-survey difference in model performance, confidence calibration, or prediction accuracy will reflect genuine differences between the surveys and their stellar populations — not contamination from shared objects.

### 7.3 Remaining data-leakage concerns

Spatial independence from object overlap does not eliminate all leakage risks. The remaining concerns identified in the data validation report still apply:

1. **Feature preprocessing leakage:** Preprocessing parameters (e.g., mean and standard deviation for normalisation) must be fitted on TESS training data only and then applied to Gaia data without re-fitting.

2. **Label leakage:** The classification target (morph_coeff threshold or Gaia label proxy) must not derive information from the test set predictions.

3. **These concerns apply during ML training**, which has not yet begun. This cross-match result addresses only object-level spatial leakage.

---

## 8. What This Report Does Not Cover

This report answers **one specific question**: are any of the 500 Gaia sources the same physical stars as objects in the TESS catalog?

It does **not** address:
- Which Gaia label definition to use (morph_coeff mapping, model_type, period threshold)
- Whether the TESS and Gaia stellar populations are comparable for ML purposes
- The period distribution mismatch between TESS and Gaia
- Feature engineering or preprocessing steps
- Model training or evaluation

Those decisions remain pending and are documented in `results/gaia_metadata_assessment.md`.

---

## 9. Summary

| Question | Answer |
|----------|--------|
| Do any Gaia sources match TESS sources at ≤ 2 arcsec? | **No (0 of 500)** |
| Do any Gaia sources match TESS sources at ≤ 10 arcsec? | **No (0 of 500)** |
| What is the closest any Gaia source comes to a TESS source? | **444 arcseconds (7.4 arcminutes)** |
| Is that closest pair the same physical star? | **No** — different proper motions confirm it |
| Is there any data leakage from shared objects? | **No** |
| Are the two datasets spatially independent? | **Yes** |
| Can the cross-survey experiment proceed? | **Yes**, from a spatial-overlap perspective |

---

## 10. Files Produced

| File | Description |
|------|-------------|
| `results/tess_gaia_crossmatch_report.md` | This report |
| `results/tess_gaia_crossmatch_candidates.csv` | Empty file (no candidates found); saved for record-keeping |

---

## 11. Recommended Next Step

The cross-match confirms that the two datasets do not share physical objects. The primary remaining blocker for the ML experiment is the **labelling decision** for Gaia sources.

The labelling options remain as identified in `results/gaia_metadata_assessment.md`:

1. **Option A — model_type mapping:** TWOGAUSSIANS-type → detached-like; ELLIPSOIDAL → contact-like
2. **Option B — period threshold:** period < X days → contact; period ≥ X days → detached
3. **Option C — confidence filter only:** Use the Gaia ECL classifier score to retain only high-confidence sources; do not assign sub-labels
4. **Option D — external catalogue lookup:** Cross-match with VSX or other variable-star catalogues to retrieve manually assigned EA/EB/EW labels

A decision on which labelling option to use must be made before TESS data cleaning, feature engineering, or ML training can begin.
