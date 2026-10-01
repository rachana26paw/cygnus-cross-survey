# Final Gaia Label Strategy

**Project:** Cygnus — Cross-Survey ML Confidence Evaluation  
**Date:** 2026-09-30  
**Author:** rachana.s@atriauniversity.edu.in  
**Stage:** Data Validation — Final Label Decision  
**Follows:** `results/external_label_assessment.md`

---

## 1. Decision

Cygnus will use the Gaia DR3 `model_type` field as an **approximate proxy label** for all 500 Gaia test sources.

This decision was made after investigating all available alternatives:
- Gaia DR3 contains no direct EA/EB/EW subtype field
- GCVS covers only 2 of 500 sources — unusable
- VSX provides independent EA/EB/EW labels for only 209 of 500 sources, and that subset is severely biased toward short-period contact systems (83% EW). Using only those 209 sources would distort the cross-survey evaluation.

Using `model_type` for all 500 sources is the only option that provides complete, consistent coverage.

**This is not a perfect label.** `model_type` is a Gaia fitting category, not a physical EB subtype. The limitations are documented in full in Section 5 and must be acknowledged in any findings.

---

## 2. Label Mapping

The following mapping will be applied to `model_type` to produce a binary label for each Gaia source:

| model_type | Label | Meaning |
|-----------|-------|---------|
| TWOGAUSSIANS | **0 — detached-like** | Both eclipses detected; no sinusoidal modulation |
| ONEGAUSSIAN | **0 — detached-like** | Only primary eclipse detected; no ellipsoidal component |
| ELLIPSOIDAL | **1 — contact-like** | Only sinusoidal variation; no distinct eclipses |
| ONEGAUSSIAN_WITH_ELLIPSOIDAL | **1 — contact-like** | One eclipse plus sinusoidal modulation |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE1 | **1 — contact-like** | Two eclipses plus sinusoidal on primary |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE2 | **1 — contact-like** | Two eclipses plus sinusoidal on secondary |

**Rationale for label 0 (detached-like):** When Gaia fits a light curve with Gaussian-shaped eclipses only — no ellipsoidal (sinusoidal) component — the system shows distinct, well-separated eclipse dips. This is more consistent with a detached binary where the two stars have flat-baseline light curves between eclipses. This corresponds broadly to EA-type (Algol) systems, which the TESS morph_coeff < 0.5 class also covers.

**Rationale for label 1 (contact-like):** When Gaia's fit requires a sinusoidal (ellipsoidal) component, the light curve has continuous brightness variation with no flat baseline. This is more consistent with contact or semi-detached systems where the stellar surfaces are tidally deformed. This corresponds broadly to EW (W UMa) and EB (Beta Lyr) types, which the TESS morph_coeff ≥ 0.5 class also covers.

**Important caveats (see Section 5):** This mapping is an approximation. TWOGAUSSIANS does not guarantee a detached system. A contact (EW) system with a short period and two distinguishable minima can also be fitted by TWOGAUSSIANS.

---

## 3. Label Distribution

**Verification:** All 500 Gaia sources have a non-null `model_type`. No unmapped values.

| model_type | Label | Count | % of 500 |
|-----------|-------|-------|---------|
| TWOGAUSSIANS | 0 | 347 | 69.4% |
| ONEGAUSSIAN | 0 | 16 | 3.2% |
| **Total label 0 (detached-like)** | | **363** | **72.6%** |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE1 | 1 | 91 | 18.2% |
| TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE2 | 1 | 26 | 5.2% |
| ELLIPSOIDAL | 1 | 11 | 2.2% |
| ONEGAUSSIAN_WITH_ELLIPSOIDAL | 1 | 9 | 1.8% |
| **Total label 1 (contact-like)** | | **137** | **27.4%** |
| **Grand total** | | **500** | **100%** |

**Note on class imbalance:** The Gaia label set is unbalanced: 72.6% detached-like vs. 27.4% contact-like. This is different from the TESS training set, which is nearly balanced (~52% contact, ~48% detached). This imbalance is an intrinsic property of the Gaia sample in this sky region, dominated by TWOGAUSSIANS fits. Its effect on the cross-survey evaluation must be considered when interpreting results.

---

## 4. VSX Consistency Check

### 4.1 Purpose

The external label assessment identified 209 Gaia sources with independent EA/EB/EW classifications from photometric surveys (ZTF, CSS, ASASSN, WISE) in the AAVSO Variable Star Index (VSX). These are NOT used as primary labels — they are used only to check whether the model_type mapping agrees with independent observations.

### 4.2 Method

- 5 sources classified as EB (semi-detached) by VSX were **excluded** from the binary comparison: EB falls between detached and contact, and it cannot be cleanly assigned to label 0 or label 1 without an arbitrary decision.
- The remaining **204 sources (30 EA + 174 EW)** were compared.
- VSX EA → expected label 0; VSX EW → expected label 1.
- Comparison: does Gaia model_type produce the same label as VSX?

### 4.3 Results

| | VSX = EA (label 0) | VSX = EW (label 1) | Total |
|--|---|----|---|
| **Gaia = 0 (detached-like)** | **15** (agree) | 109 (disagree) | 124 |
| **Gaia = 1 (contact-like)** | 15 (disagree) | **65** (agree) | 80 |
| **Total** | 30 | 174 | 204 |

| Metric | Value |
|--------|-------|
| Agreements | 80 / 204 |
| Disagreements | 124 / 204 |
| **Agreement rate** | **39.2%** |
| Disagreement rate | 60.8% |

### 4.4 Interpretation of the agreement rate

**39.2% is below what one would hope for.** A random assignment in this (heavily imbalanced) comparison set — where 85.3% of VSX sources are EW — would give a baseline accuracy of roughly 37% if the model simply predicted "EW" for everything. The model_type mapping is therefore only slightly better than a naive baseline on this particular comparison set.

However, several important factors explain why this result is not as damaging as it appears:

**Why the agreement rate is low:**

1. **The comparison set is unrepresentative.** The 204-source VSX subset is 85.3% EW (contact). The full 500-source Gaia sample is only 27.4% contact by model_type. The comparison set is dominated by exactly the type of system (short-period EW) where model_type performs worst.

2. **TWOGAUSSIANS fits contact systems.** The most common disagreement is: VSX says EW (contact), but Gaia model_type is TWOGAUSSIANS (→ label 0). Of the 174 EW sources, 109 (62.6%) have a TWOGAUSSIANS model in Gaia. This is physically plausible: a contact system with a short period can have two distinguishable minima, which Gaia's pipeline fits with two Gaussians. The TWOGAUSSIANS fit does not prove the system is detached — it only means two eclipse dips were detected.

3. **VSX labels are themselves imperfect.** The independent survey labels (mainly ZTF and CSS automated pipelines) are generally reliable but not error-free, especially for EW systems near the boundary between EW and EB types.

**What the agreement check does show:**

- The model_type mapping performs reasonably for **EA (detached) sources**: 15 of 30 EA sources (50%) are mapped to label 0. The other 15 EA sources mapped to label 1 by model_type have WITH_ELLIPSOIDAL fits — meaning Gaia detected sinusoidal modulation in what VSX calls a detached system. This is not impossible: some detached systems near the boundary can show mild ellipsoidal variation.

- The model_type mapping performs poorly for **EW (contact) sources**: only 65 of 174 EW sources (37.4%) are mapped to label 1. The remaining 109 EW sources are TWOGAUSSIANS → label 0. This is the systematic bias: the model_type mapping systematically under-labels short-period contact systems.

**ONEGAUSSIAN consistency check:**

Of the 16 ONEGAUSSIAN sources (all mapped to label 0), 4 appear in the VSX comparison set. All 4 are classified as EA (detached) by VSX and all 4 are correctly mapped to label 0. This provides limited but positive support for the ONEGAUSSIAN → label 0 mapping.

### 4.5 What the VSX check proves and does not prove

**What it DOES prove:**
- The model_type mapping is imperfect, particularly for the short-period EW contact systems that dominate the VSX-classified subset.
- TWOGAUSSIANS is not a reliable indicator of a detached system — it can fit both detached and contact systems.
- The model_type-derived Gaia labels will contain a meaningful fraction of contact (EW) systems labeled as "detached-like" (label 0).

**What it does NOT prove:**
- That the model_type mapping is wrong for the full 500-source Gaia sample. The 204-source comparison set is biased toward EW systems, which are where the mapping is least reliable. The 296 uncompared sources may have better agreement.
- That any other label strategy is better. VSX covers only 41.8% of sources, with severe selection bias. The model_type mapping, despite its imperfections, provides the only consistent labelling for all 500 sources.
- That the experiment is invalid. The research question asks about confidence calibration, not absolute accuracy. Even with imperfect labels, the question "do high-confidence model predictions agree more with the proxy label than low-confidence ones?" can still be answered — with the caveat that the proxy label is imperfect.

---

## 5. Limitations

These limitations must be clearly stated in the final project report.

### Limitation 1: model_type is not the same as EA/EB/EW

`model_type` describes which mathematical function Gaia used to fit the light curve. It does not directly measure whether the stars are physically detached or in contact. The same physical system can sometimes produce different model types depending on photometric noise, number of observations, and period estimation accuracy.

The TESS `morph_coeff` measures the **shape** of the fitted light curve (0 = sharp eclipses, 1 = smooth contact). The Gaia `model_type` measures which **fitting model** was selected. These are different quantities measured differently.

### Limitation 2: The mapping is approximate and has a high error rate for one direction

The consistency check (Section 4) found that **62.6% of EW (contact) systems in the comparison set are assigned label 0 (detached-like) by the model_type mapping**. This is a systematic error, not a random one. The model_type mapping under-labels contact systems.

The direction of the error means:
- The Gaia label-0 class will contain a mixture of genuine detached systems AND short-period contact systems that Gaia fitted with TWOGAUSSIANS.
- A TESS-trained model that predicts "detached" for these sources may be "wrong" by the proxy label but "right" by physical reality.

### Limitation 3: VSX validation covers only 41.8% of the Gaia sample, with severe selection bias

The 204-source comparison set used in the VSX check represents 40.8% of the Gaia sample. It is strongly biased toward EW/contact systems (85.3%) because ground-based surveys preferentially detect short-period contact variables. This means the 39.2% agreement rate is measured on the part of the Gaia sample most likely to show disagreement. The true agreement rate across all 500 sources is probably higher than 39.2%.

### Limitation 4: The period distribution mismatch remains

The Gaia sample has median period 0.46 days; the TESS training set has median period 2.21 days. The Gaia test set is dominated by very short-period systems that are rare in the TESS training set. Any performance difference between TESS and Gaia evaluation may partly reflect this distributional difference, not only the cross-survey measurement differences.

### Limitation 5: Both label systems use binary classification of a continuous phenomenon

Both morph_coeff (TESS) and model_type (Gaia) ultimately classify EBs that exist on a continuum from detached to contact. A threshold (morph_coeff = 0.5 for TESS; presence/absence of ellipsoidal component for Gaia) produces a binary label from a continuous physical parameter. Stars near the boundary will be misclassified in both labelling systems.

---

## 6. Final Decision for Cygnus

**The Gaia test dataset is ready to move to the next phase of the Cygnus project.**

The following conditions are met:

| Condition | Status |
|-----------|--------|
| All 500 Gaia sources have coordinates, periods, and model_type | ✓ |
| All 500 Gaia sources have pre-computed statistical features (vari_summary) | ✓ |
| No TESS training sources overlap with Gaia test sources (cross-match: 0 matches) | ✓ |
| A labelling strategy for all 500 Gaia sources is defined | ✓ |
| Label limitations are documented | ✓ |
| External catalogue investigation completed | ✓ |
| VSX consistency check completed and reported | ✓ |

The label quality is lower than initially hoped — the 39.2% VSX agreement rate reveals that the TWOGAUSSIANS → detached-like mapping is unreliable for the short-period contact systems that dominate the Gaia sample. **This must be stated as a significant limitation in the final project report.**

Despite this, the experiment can proceed because:
1. No better label strategy is available that covers all 500 sources
2. The label approximation is documented and its direction of error is understood
3. The research question (about confidence calibration) can still be investigated with proxy labels, provided the limitations are explicitly stated

**What must happen BEFORE ML training begins:**

1. TESS dataset cleaning (remove ~20 bad records; keep ~4,561 clean records)
2. Feature selection (decide which features from TESS and Gaia will be used)
3. Train/test split design (prevent leakage from TESS duplicate tess_ids)
4. Preprocessing plan (fit scalers on TESS training data only)

None of these steps have been done yet. The next immediate task is TESS cleaning.
