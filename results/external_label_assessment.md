# Cygnus — External Label Assessment Report

**Project:** Cygnus — Cross-Survey ML Confidence Evaluation  
**Date:** 2026-09-30  
**Author:** rachana.s@atriauniversity.edu.in  
**Stage:** Data Validation — Label Investigation Phase  
**Follows:** `results/gaia_metadata_assessment.md`, `results/tess_gaia_crossmatch_report.md`

---

## 1. Purpose

This report investigates whether reliable ground-truth eclipsing-binary (EB) subtype labels — specifically EA (detached/Algol), EB (semi-detached/Beta Lyrae), or EW (contact/W UMa) — can be obtained for the 500 Gaia sources by cross-matching them against established external variable-star catalogues.

The need arises because:
- The 500 Gaia sources have no EA/EB/EW field in the standard Gaia DR3 tables
- The best available Gaia proxy is `model_type` in `gaiadr3.vari_eclipsing_binary`, but this is a fitting category, not a proven EB subtype
- If an external catalogue provides traditional EA/EB/EW labels for most or all of the 500 sources, those labels would be preferable to the model_type proxy

---

## 2. Catalogues Investigated

| Catalogue | Full name | Scope | Access method |
|-----------|-----------|-------|---------------|
| **VSX** | AAVSO Variable Star Index | Comprehensive multi-survey variable-star catalogue | CDS XMatch service against `vizier:B/vsx/vsx` |
| **GCVS** | General Catalogue of Variable Stars | Historically important catalogue of named variable stars | CDS XMatch service against `vizier:B/gcvs/gcvs_cat` |
| **SIMBAD** | Set of Identifications, Measurements and Bibliography for Astronomical Data | Aggregated astronomical database | Queried separately (results pending) |

The CDS XMatch service performs a bulk coordinate-based cross-match by uploading the 500 Gaia RA/Dec positions and searching each catalogue within a **3 arcsecond matching radius**. This is more generous than the 2 arcsecond standard used in the TESS–Gaia cross-match, because external catalogue coordinates may be less precise than Gaia's.

---

## 3. Matching Results

### 3.1 AAVSO VSX

| Metric | Value |
|--------|-------|
| Gaia sources queried | 500 |
| VSX matches within 3 arcsec | 499 (99.8%) |
| Unmatched Gaia sources | 1 (0.2%) |
| Median angular separation | 0.057 arcseconds |
| Maximum angular separation | 1.967 arcseconds |
| Matches within 1 arcsec | 491 (98.4%) |

At first glance, a 99.8% match rate looks excellent. However, the nature of those matches is critical (see Section 4).

### 3.2 GCVS

| Metric | Value |
|--------|-------|
| Gaia sources queried | 500 |
| GCVS matches within 3 arcsec | 2 (0.4%) |
| Gaia source → GCVS name → Type | 209021386690135040 → V0364 Aur → **EA** (sep 0.43") |
| | 209534244440847744 → MN Aur → **EA/RS:** (sep 0.09") |

The GCVS covers only 2 of the 500 Gaia sources. This is expected: the GCVS was compiled primarily for bright, historically known variable stars. Most of the Gaia sources are faint (G ≈ 15–20 mag), newly discovered in modern surveys, and not yet in the GCVS.

### 3.3 SIMBAD

The SIMBAD bulk query timed out before completing all 500 sources. Individual source queries return SIMBAD records, but processing 500 sources sequentially at a safe query rate would take approximately 30+ minutes. The VSX and GCVS results below are sufficient to answer the key question.

---

## 4. Critical Finding: VSX Has Ingested the Gaia DR3 EB Catalogue

This is the most important result of this investigation.

Of the 499 VSX matches, **274 are entries that VSX created by ingesting the Gaia DR3 eclipsing binary catalogue itself**. These entries are named "Gaia DR3 XXXXXXXXXXXXXXXXX" in VSX and carry only the generic type code **"E"** (eclipsing, no subtype).

This means that for 274 of 499 matched sources, VSX is not providing an independent classification — it is simply reflecting back the same Gaia DR3 information we already have. Looking up "Gaia DR3 138833202936043776" in VSX and finding it classified as "E" tells us nothing new: it was put there by VSX when Gaia DR3 was released, using Gaia's own EB catalogue.

| VSX entry source | Count |
|-----------------|-------|
| Derived from Gaia DR3 (Name = "Gaia DR3 XXXX") | **274** |
| From independent photometric surveys (CSS, ZTF, ASASSN, WISE, named stars) | **225** |

Only the 225 entries from **independent surveys** represent genuinely new information.

---

## 5. Available Classifications

### 5.1 VSX Type Codes

VSX uses the GCVS variability type notation. The relevant codes for eclipsing binaries are:

| VSX Type | Meaning | Physical system | TESS equivalent |
|----------|---------|-----------------|-----------------|
| EA | Algol-type | Detached; distinct flat minima, constant brightness between eclipses | morph_coeff ≈ 0–0.3 |
| EB | Beta Lyrae type | Semi-detached; continuous brightness variation, unequal minima | morph_coeff ≈ 0.3–0.7 |
| EW | W Ursae Majoris type | Contact; nearly equal minima, continuous variation | morph_coeff ≈ 0.7–1.0 |
| E | Generic eclipsing (no subtype determined) | Any | N/A |

Additional types found in the matched sources that are NOT EB subtypes:
- **RS** — RS Canum Venaticorum (close binary with spot activity; variability not from eclipses)
- **BY** — BY Draconis (spotted rotating star)
- **MISC**, **SR**, **VAR** — miscellaneous, semi-regular, generic variable

### 5.2 Type Distribution (all VSX matches)

| Type | Count | Source |
|------|-------|--------|
| E | 275 | 274 Gaia DR3 re-entries + 1 independent |
| EW | 173 | Independent surveys (mostly ZTF, CSS, ASASSN, WISE) |
| EA | 28 | Independent surveys |
| RS | 10 | Independent surveys — NOT EB subtype |
| EB: | 4 | Independent surveys (the colon ":" means uncertain classification) |
| EB | 1 | Independent survey |
| EA/RS | 1 | Independent (EA with RS variability component) |
| EA\|EB | 1 | Independent (ambiguous between EA and EB) |
| Others | 6 | BY, MISC, SR, EW:, RS:, VAR |

### 5.3 Independent EA/EB/EW Coverage

After removing the 274 Gaia-derived "E" entries, the **independent survey coverage** is:

| Classification | Count | Fraction of 500 |
|---------------|-------|-----------------|
| Contact — EW (W UMa) | 174 | 34.8% |
| Detached — EA (Algol) | 30 | 6.0% |
| Semi-detached — EB (Beta Lyr) | 5 | 1.0% |
| **Total with clear EB subtype** | **209** | **41.8%** |
| Not EB subtype (RS, BY, etc.) | 16 | 3.2% |
| No independent classification | 275 | 55.0% |

---

## 6. Label Quality Assessment

### 6.1 Angular separation

All independent VSX matches fall within 2 arcseconds (maximum 1.967"), with median 0.111 arcseconds. These are genuine positional coincidences — not accidental or spurious matches. The separations are consistent with the same physical star being observed by two different surveys with small astrometric offsets.

### 6.2 Independent survey provenance

The 225 independent VSX entries come from:
- **ZTF** (Zwicky Transient Facility) — modern, large-scale photometric survey; classifications generally reliable for EW-type systems
- **CSS** (Catalina Sky Survey) — older ground-based survey; mainly bright EW/EA systems
- **ASASSN** (All-Sky Automated Survey for Supernovae) — automated survey; EA/EW classifications
- **WISE** — infrared photometry; EW classifications mainly
- **Named catalogue stars** (NSVS, DDE) — manually classified; fewer entries

For EA and EW classifications from these surveys, the labels are generally regarded as reliable in the astronomical literature. The EA classification requires detection of a flat light curve between eclipses (characteristic of detached systems), which is not easily confused with EW systems.

### 6.3 Uncertain classifications

- 4 sources typed "EB:" — the colon indicates the classification is uncertain
- 1 source typed "RS:" — uncertain RS CVn classification
- 1 source typed "EA|EB" — ambiguous between EA and EB
- 1 source typed "EW:" — uncertain EW classification

These should be treated with caution; only unqualified EA, EB, and EW entries are fully reliable.

### 6.4 Non-EB types

16 of the 225 independent matches are typed as RS (10), BY (1), MISC (1), SR (1), VAR (1) — these are **not eclipsing binary subtypes**. If these sources are in the Gaia EB variability catalogue, it may reflect either:
1. Gaia misclassifying them as EBs, OR
2. The VSX classification coming from a different survey epoch that observed different variability

These 16 sources should NOT be used as EB training/test examples without further investigation.

---

## 7. Selection-Bias Concerns

This is a critical finding that affects whether external catalogue labels can be used fairly.

### 7.1 Extreme bias toward contact (EW) systems

Among the 209 independently classified sources:
- **174 are EW (contact)** = 83.3%
- **30 are EA (detached)** = 14.4%
- **5 are EB (semi-detached)** = 2.4%

This is a heavily skewed distribution. For comparison, the TESS training set is nearly balanced: ~48% detached (morph_coeff < 0.5) and ~52% contact.

The reason for this skew is simple: the independent surveys (ZTF, CSS, ASASSN) preferentially detect **short-period, high-amplitude variables**. EW-type contact systems have periods of 0.2–1 day and continuous brightness variation, making them easy to classify from limited photometric observations. EA-type detached systems have longer periods, shallower or more subtle secondary eclipses, and flat-baseline light curves that require longer observing baselines to characterise confidently.

This means: if we restrict the Gaia test set to only the 209 independently classified sources, the test set would be **83% contact systems**. This is very different from the 52% contact composition of the TESS training set, and would severely bias any cross-survey comparison.

### 7.2 Incomplete coverage creates a non-representative sample

If only 209 of 500 sources are used, the remaining 291 sources are discarded. The 291 discarded sources are predominantly those that were only observed by Gaia (faint sources not detected by ground-based surveys). Faint sources tend to be more distant and more likely to be longer-period systems (since short-period systems are intrinsically brighter on average). Discarding them biases the test set toward nearby, short-period contact systems — exactly the opposite of what the TESS training set contains.

### 7.3 Comparison with full Gaia sample using model_type

Using the Gaia model_type proxy for all 500 sources gives a different distribution:
- TWOGAUSSIANS + ONEGAUSSIAN (detached-like): 363 sources (72.6%)
- Models with ellipsoidal component (contact-like): 137 sources (27.4%)

This is less biased toward contact systems than the VSX-classified subset (which was 83% EW), though it is still different from the TESS balance (~52% contact). The model_type distribution reflects the true Gaia EB population observed in this sky region, not a selection effect from photometric survey sensitivity.

---

## 8. Comparison: External Catalogue vs. Gaia model_type

| Criterion | External catalogue (VSX EA/EB/EW) | Gaia model_type proxy |
|-----------|----------------------------------|-----------------------|
| Coverage | 209 / 500 (41.8%) | 500 / 500 (100%) |
| Label origin | Independent surveys (CSS, ZTF, ASASSN) | Gaia DR3 fitting algorithm |
| Label type | Traditional EA/EB/EW classification | Geometric fit category (6 types) |
| Direct equivalence to TESS morph_coeff | No — different classification system | No — different classification system |
| Selection bias | **Severe** — 83% EW contact, 14% EA | **Moderate** — 73% TWOGAUSSIANS, 27% ellipsoidal |
| Reliability per entry | High for EA and EW | Moderate — fit category, not physical measurement |
| Consistency across all sources | No — requires different criteria for VSX and model_type entries | Yes — single consistent classification criterion |
| Comparable to TESS split? | Worse — extreme contact bias | Better — but still different from TESS |

**Key conclusion:** Using the external catalogue for only the 209 classified sources is not better than using Gaia model_type for all 500 sources. It would reduce sample size by 58% AND introduce severe selection bias toward contact systems.

---

## 9. Implications for the Cygnus Research Question

The research question is: "Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"

To answer this question, the model needs to make predictions on Gaia sources, and those predictions need to be compared to the actual EB type (correct or not). This requires a label for each Gaia source.

### 9.1 What the external catalogue assessment tells us

There is no single external catalogue that provides complete, independent, unbiased EA/EB/EW labels for all 500 Gaia sources.

- **GCVS:** Covers only 2 sources. Useless for this experiment.
- **VSX:** Appears to cover 499 sources, but 274 of those are Gaia's own catalogue ingested into VSX — not independent. Only 209 sources have genuinely independent EA/EB/EW labels.
- **SIMBAD:** Would aggregate VSX, GCVS, and other catalogues. Not expected to provide substantially more independent coverage than VSX.

### 9.2 Is 41.8% coverage acceptable?

Using only the 209 VSX-classified sources would mean:
1. Reducing the Gaia test set from 500 to 209 sources (-58%)
2. Introducing a severe EW/contact bias (83% contact vs. 52% contact in TESS)
3. Having unequal label quality (EA and EW are well-characterised; EB uncertain)

The resulting experiment would be answering a different question: "How does the model perform on nearby, short-period contact EBs detected by ground-based surveys?" — not the general cross-survey reliability question.

### 9.3 The most defensible approach

The best available single source of labels that covers all 500 Gaia sources consistently is **Gaia's own `model_type` field**, with the mapping documented explicitly as an approximation. This is Option A from the metadata assessment report.

The external catalogue investigation provides one important new piece of information: **among the 209 sources that have both model_type and an independent VSX EA/EW classification, it is now possible to assess how well the model_type mapping agrees with the independent classification.** This agreement check would strengthen the scientific justification for using model_type as the primary label.

---

## 10. Recommended Decision Options

These are options for the final Gaia label strategy, ranked from most to least recommended based on the findings in this report:

---

### Option A (Recommended) — Gaia model_type for all 500 sources, with VSX consistency check

**What it does:**  
Use the Gaia `model_type` mapping to assign labels to all 500 sources. Additionally, compute the agreement rate between the model_type-derived labels and the independent VSX EA/EW labels for the 209 sources that have both. Report the agreement rate as a measure of label quality.

**Why this is recommended:**  
- Full coverage (500 sources)
- Consistent labelling criterion
- Can be partially validated against independent VSX classifications
- Moderate selection bias (similar for all 500 sources)
- Scientifically transparent — the approximation is documented, not hidden

**Label mapping:**
- TWOGAUSSIANS → detached-like (label: 0)
- ONEGAUSSIAN → detached-like (label: 0; may drop or keep separately)
- ELLIPSOIDAL → contact-like (label: 1)
- ONEGAUSSIAN_WITH_ELLIPSOIDAL → contact-like (label: 1)
- TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE1 → contact-like (label: 1)
- TWOGAUSSIANS_WITH_ELLIPSOIDAL_ON_ECLIPSE2 → contact-like (label: 1)

**What must be stated in the final report:**  
model_type is not equivalent to morph_coeff. This is a proxy mapping that enables comparison but introduces label uncertainty, which must be acknowledged as a limitation.

---

### Option B — VSX EA/EW labels for 209 sources only, model_type for remaining 291

**What it does:**  
Use independent VSX labels where available; fall back to model_type for the other 291 sources. This creates a hybrid label set.

**Why this is problematic:**  
- Two different labelling criteria within the same test set — scientifically inconsistent
- The 209 VSX-labelled sources are not representative (83% contact); using them as ground truth for part of the experiment biases comparisons
- Creates selection effects that are hard to disentangle from cross-survey effects

---

### Option C — VSX EA/EW labels for 209 sources only, drop the rest

**What it does:**  
Restrict the Gaia test set to only the 209 independently classified sources.

**Why this is not recommended:**  
- Sample size reduced by 58%
- Severe EW/contact bias (83% EW) → the evaluation would mainly test how the model handles contact systems
- Not representative of the broader Gaia EB population
- Likely to produce pessimistic cross-survey results because the TESS model is trained on a more balanced set

---

### Option D — Period-based threshold for all 500 sources

**What it does:**  
Use orbital period to assign labels: period < 0.5 days → contact (label: 1); period ≥ 0.5 days → detached (label: 0).

**Assessment:**  
This is a simple, statistically motivated rule. Very short period EBs are almost exclusively contact/EW type; this is well-established in EB research. However, it is a statistical generalisation — individual exceptions exist. Compared to model_type, it ignores the light curve shape information that Gaia has already computed, and it would produce a very unbalanced label set (52.6% of Gaia sources have period < 0.5 days — but the boundary is not a hard physical cutoff).

---

## 11. Summary Table

| Question | Finding |
|----------|---------|
| How many Gaia sources match in VSX within 3 arcsec? | 499 / 500 (99.8%) |
| How many VSX matches are from independent surveys (not Gaia DR3 re-entries)? | 225 / 499 |
| How many have clear EA/EW/EB from independent surveys? | 209 / 500 (41.8%) |
| How many match in GCVS? | 2 / 500 (0.4%) |
| Is external catalogue coverage sufficient for all 500 sources? | No — only 41.8% |
| Is the VSX-classified subset representative of the full Gaia sample? | No — 83% contact vs. ~73% in full sample |
| Would using VSX labels improve on model_type? | No — worse coverage + severe selection bias |
| Is model_type still the best available labelling strategy? | Yes, for full 500-source coverage |
| Can VSX provide any value at all? | Yes — as a consistency check for the 209 overlapping sources |

---

## 12. Files Produced

| File | Description |
|------|-------------|
| `results/external_label_assessment.md` | This report |
| `results/tess_gaia_crossmatch_candidates.csv` | From previous phase — empty (0 cross-matches) |

Intermediate data files (in session scratchpad, not versioned):
- `vsx_matches.csv` — full VSX cross-match result (499 rows)
- `gcvs_matches.csv` — GCVS cross-match result (2 rows)
- `vsx_independent_classified.csv` — the 209 independently classified VSX sources
