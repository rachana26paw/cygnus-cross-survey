# Phase 6 — Website Content Blueprint

**Project:** Cygnus  
**Author:** rachana.s@atriauniversity.edu.in  
**Date:** 2026-09-30  
**Purpose:** Design guide for the future Cygnus website — not an implementation, but a content plan.

---

## Design Principle

The website should tell a **scientific story** to an intelligent visitor who is not necessarily an astronomer or ML expert.

The story flows in one direction:

**Question → Data → Method → Results → Interpretation → Conclusion**

Not every project phase needs its own page. The website should select the most important scientific information from all phases and present it as a unified narrative.

---

## Page Structure

---

### Page 1 — Home / Research Question

**Purpose:** Hook the visitor and state the question immediately.

**Content:**

- Project name: **CYGNUS**
- One-line subtitle: *"Investigating whether machine-learning confidence can be trusted across astronomical surveys."*
- The research question, displayed prominently:
  > "Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"
- One-paragraph project explanation (non-technical):
  > Machine-learning models produce a "confidence score" alongside their predictions. But when a model trained on data from one telescope is used on data from a different telescope, does that confidence score still mean what it seems to? Cygnus uses NASA TESS and ESA Gaia DR3 eclipsing binary data to investigate this question.
- Visual: a simple left-to-right flow diagram
  - TESS data → Train model → Evaluate on TESS → Apply to Gaia → Compare confidence

**What NOT to include here:** technical details, file names, phase numbers, methodology.

---

### Page 2 — The Data

**Purpose:** Explain the two datasets in plain language so the visitor understands what is being compared.

**Content:**

**What is an eclipsing binary?**
> An eclipsing binary is a pair of stars orbiting each other. When one star passes in front of the other as seen from Earth, the combined brightness dips — creating a distinctive light curve pattern. The shape of this pattern tells us about the type of binary.

**Two types:**
- Detached binaries (label 0): the two stars are well separated. Their light curve shows sharp, distinct eclipse dips.
- Contact binaries (label 1): the two stars are very close together or touching. Their light curve varies continuously and smoothly.

**NASA TESS:**
- What it is: a space telescope that observes stellar brightness continuously
- Data used: the TESS Eclipsing Binary catalog — 4,046 usable records after cleaning
- Each row: one eclipsing binary star with fitted orbital properties
- Labels: derived from `morph_coeff`, a continuous measure of light-curve shape

**ESA Gaia DR3:**
- What it is: a space mission that surveys more than a billion stars with high precision
- Data used: the Gaia DR3 variability eclipsing binary catalog — 489 usable records
- Each row: one eclipsing binary candidate with fitted light-curve model parameters
- Labels: derived from `model_type` (a proxy — see below)

**The label difference (important):**

Display as a side-by-side box:

| TESS labels | Gaia labels |
|-------------|-------------|
| Derived from a continuous light-curve shape parameter (morph_coeff) | Derived from the mathematical fitting model Gaia used (model_type) |
| A physically motivated measure of eclipse shape | A fitting category, not a direct physical classification |
| Used as the training target — treated as ground truth for the TESS experiment | Used as a proxy — imperfect, with 39.2% external cross-check agreement |
| Label meaning validated by physical intuition about EB types | Label meaning is an approximation |

**Call-out box for the visitor:**
> Gaia results in this project measure *agreement with proxy labels*, not physical ground-truth accuracy. This distinction is important for interpreting the findings.

**Visual suggestions:**
- Simple dataset size comparison (TESS: 4,046 vs Gaia: 489)
- Period distribution comparison: histogram or density plot showing TESS (wide range, median 2.07 days) vs Gaia (short-period dominated, median 0.46 days)

**What NOT to include:** raw data file names, internal column names, validation steps, every cleaning decision.

---

### Page 3 — How the Model Works

**Purpose:** Explain the method clearly enough that a visitor with basic ML knowledge can follow the logic.

**Content:**

**Features**

Only two features were usable for both surveys:

| Feature | What it measures | Why it matters |
|---------|-----------------|----------------|
| Orbital period | How long the two stars take to orbit each other (in days) | Related to the type of binary — contact systems tend to have shorter periods |
| Primary eclipse duration | How long the main eclipse lasts, as a fraction of the orbital period | A wide eclipse suggests a large, close-contact system; a narrow eclipse suggests a detached pair |

**Why only two features?**
> The two surveys use different instruments, different photometric bands, and different processing pipelines. Most candidate features either mean something different in each dataset or are simply not available from one of them. Only period (measured identically in both) and eclipse duration (measured in comparable units in both, despite distribution differences) could be scientifically justified.

**Feature distribution difference (important):**
> Eclipse durations are systematically different between surveys. TESS eclipse durations have a median of 0.079 (fraction of orbital period); Gaia's median is 0.284. This difference turns out to matter for the cross-survey transfer.

**The Model**

> A Random Forest classifier was used. This algorithm creates many decision trees and combines their votes. It was selected because it is well-suited to tabular data and because it produces calibrated probability estimates, which are needed to measure confidence.

**Training and testing:**
1. The Random Forest was trained on 3,236 TESS records (80% of the TESS dataset, split by star identity to prevent leakage).
2. It was tested on the remaining 810 TESS records it had never seen.
3. The same trained model — without any retraining — was then applied to 489 Gaia records.

**Why not retrain on Gaia?**
> The whole point of the experiment is to test what happens when the model crosses from one survey to another. Retraining would remove the cross-survey element.

**Visual suggestion:** a three-step diagram: Train on TESS (3,236 records) → Test on TESS (810 records) → Transfer to Gaia (489 records)

**What NOT to include:** Python code, scikit-learn parameters, file paths.

---

### Page 4 — What We Found

**Purpose:** Present the core results clearly and honestly. This is the central page of the website.

**Content:**

**Performance comparison — the key numbers:**

Display as a large, clean table or card layout:

| | TESS (held-out test) | Gaia (vs proxy labels) |
|-|---------------------|------------------------|
| **Accuracy** | **92.5%** | **32.5%** |
| **F1 score** | 92.5% | 26.4% |
| **Mean confidence** | 0.941 | 0.860 |
| **Calibration gap** | **+0.016** | **+0.535** |
| **Brier score** | **0.060** | **0.488** |

*Calibration gap = how much the mean confidence exceeds the accuracy. Larger = more overconfident.*

**Explain each metric in one line:**
- Accuracy: what fraction of predictions matched the label.
- Confidence: how sure the model said it was (averaged across all predictions).
- Calibration gap: if this is near zero, confidence ≈ accuracy. If positive, the model is overconfident.
- Brier score: how close were the predicted probabilities to the outcomes? (0 = perfect, ~0.25 = random)

**The most important finding — high-confidence predictions:**

Display as a highlighted comparison box:

| | Predictions with ≥ 90% confidence |
|-|-----------------------------------|
| **TESS** | 80.6% of all predictions — **96.6% correct** |
| **Gaia** | 48.3% of all predictions — **48.7% consistent with proxy labels** |

> On TESS, when the model was very confident, it was almost always right.  
> On Gaia, when the model was very confident, it was only about half right — barely better than guessing.

**Important note:** display clearly that Gaia numbers are against proxy labels, not physical truth.

**What NOT to include:** confusion matrices in raw form, class-level precision/recall breakdown, intermediate experiment numbers.

---

### Page 5 — Can We Trust the Confidence?

**Purpose:** Make "reliability" and "calibration" understandable. This page answers the research question directly.

**Content:**

**What does "confidence" mean?**
> Every prediction comes with a number between 50% and 100%. This is the model's way of saying "I am this sure about this classification." A well-calibrated model means a 90% confidence prediction is correct about 90% of the time.

**What does the reliability diagram show?**
> The reliability diagram plots the model's stated confidence (horizontal axis) against its actual accuracy (vertical axis). A perfect model would fall exactly on the diagonal.

Show the reliability diagram image (from `results/phase5/reliability_diagram_tess_vs_gaia.png`).

**Caption suggestion:**
> The TESS curve follows the diagonal closely — confidence and accuracy match well. The Gaia curve falls far below — the model says it is highly confident, but its agreement with proxy labels is much lower. In the 0.70–0.80 confidence bin, Gaia proxy-label agreement was only 10.2%.

**The Brier score in plain English:**

> A Brier score near **0.060** (TESS) means the model's probability estimates are very accurate.  
> A Brier score near **0.488** (Gaia) means the probability estimates are worse than simply assigning 50/50 to everything.  
> The Gaia Brier score is a direct measure that the numbers themselves — not just the classifications — should not be trusted.

**Confidence ≠ correctness:**

> A model can assign 95% confidence to a wrong answer. Confidence reflects how the model "sees" the input compared to its training data — not whether the answer is actually correct. When the training data and the new data come from different sources with different characteristics, confidence can become systematically misleading.

**What NOT to include:** mathematical Brier formula, technical calibration theory.

---

### Page 6 — Why Does It Happen?

**Purpose:** Explain the root causes honestly without overclaiming.

**Content:**

**Contributing factor 1 — Eclipse duration distributions differ**

> The eclipse duration feature has 66.9% importance in the model. TESS eclipse durations have a median of 0.079 (fraction of orbital period); Gaia's median is 0.284 — more than 3× wider. The model learned from TESS that wide eclipses mean "contact-like." When it sees Gaia's much wider eclipses, it classifies most Gaia sources as "contact-like" with high confidence — but this pattern from training may not hold across pipelines.

**Contributing factor 2 — Period distributions differ**

> Gaia's dataset is dominated by very short-period systems (66.9% have periods below 1 day). In the TESS training data, only 30.3% of sources have periods below 1 day. Short-period systems tend to be contact-type. The model saw relatively few of these in training, so its learned boundaries may not apply well to the Gaia period distribution.

**Contributing factor 3 — Proxy-label limitations**

> The Gaia labels used as the "answer key" are themselves imperfect. If the proxy labels are wrong in some cases, the model may actually be producing reasonable predictions that appear wrong only because the label we are checking against is incorrect. This makes it impossible to fully separate true model overconfidence from label noise.

**What the experiments found about these factors:**

> Removing eclipse duration entirely did not fix the problem — the calibration gap stayed at +0.530.  
> Restricting to sources where the period range overlaps better between surveys (period ≥ 1 day) gave only marginal improvement — calibration gap moved from +0.535 to +0.489.  
> None of the tested changes solved the cross-survey confidence problem.

**Key message:**

> No single cause explains the failure. The evidence points to a combination of factors that cannot be fully separated with the available data. This is a real scientific finding — understanding *why* cross-survey transfer fails is as important as knowing *that* it fails.

**Visual suggestion:** three small diagrams — eclipse duration distributions (TESS vs Gaia), period distributions (TESS vs Gaia), and a proxy-label accuracy chart showing the 39.2% VSX agreement rate.

---

### Page 7 — Experiments

**Purpose:** Show that the main finding was tested from multiple angles.

**Content:**

Three controlled experiments were run to test alternative explanations:

| Experiment | What was tested | What was found |
|------------|-----------------|----------------|
| **A. Two-feature model** (period + eclipse duration) | Baseline experiment | TESS calibration gap +0.016; Gaia calibration gap +0.535 |
| **B. Period-only model** | Is eclipse duration the main cause? | Removing it *increased* Gaia mean confidence (0.860 → 0.913). Gap barely changed (+0.530). TESS accuracy dropped to 76.2%. |
| **C. Period-range filter (≥ 1 day)** | Is the period mismatch the main cause? | 162 of 489 Gaia sources kept. Marginal improvement (gap +0.535 → +0.489). Model still severely overconfident. |

**Conclusion from experiments:**

> None of the tested changes eliminated the cross-survey confidence problem. The finding is robust to these variations.

**Visual suggestion:** a bar chart comparing calibration gaps across the five evaluation sets (3 Gaia, 2 TESS).

---

### Page 8 — Limitations and Scientific Care

**Purpose:** Show intellectual honesty. A scientifically sound project acknowledges what it cannot prove.

**Content:**

**Most important limitations:**

1. **Gaia proxy labels are imperfect.** The Gaia labels are derived from a fitting model, not direct physical classification. External cross-check shows 39.2% agreement with independent labels. Some apparent model errors on Gaia may be label errors.

2. **Only two features were available.** The comparison is limited to period and eclipse duration — the only features scientifically defensible across both surveys.

3. **Feature distributions differ substantially.** Eclipse durations and period ranges are markedly different between surveys, partly because the surveys covered different regions of the sky and used different selection criteria.

4. **Gaia sample size is 489 sources.** This is sufficient for a pilot study but not for fine-grained analysis.

5. **Eclipse duration measurements come from different processing pipelines.** Even though both columns measure the same concept, they were derived by different software on different data.

**What this project does NOT prove:**

- It does not prove that Random Forest is inherently unreliable.
- It does not prove that cross-survey transfer is always impossible.
- It does not prove that eclipse duration is the sole cause of the failure.
- Gaia "accuracy" numbers are not physical ground-truth accuracy.

---

### Page 9 — Final Finding

**Purpose:** Restate the answer to the research question clearly.

**Content:**

**Research question:**
> "Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"

**Finding:**

Display prominently:
> **Based on this experiment: No — the confidence scores were not reliable when the model was transferred to a different survey.**

**Supporting evidence (three bullet points):**
- On TESS: the model achieved 92.5% accuracy and a calibration gap of only +0.016. When it said 90%+ confidence, it was right 96.6% of the time.
- On Gaia: the calibration gap was +0.535. When it said 90%+ confidence, it matched proxy labels only 48.7% of the time.
- Three controlled experiments testing alternative explanations each produced at most marginal improvements — the confidence problem persists across tested variations.

**Broader implication:**
> This matters for real astronomy pipelines. If a scientist uses a model trained on one survey to classify objects from another survey, the model's confidence scores may be misleading guides for which predictions to trust. The findings suggest that cross-survey transfer should be validated carefully, not assumed.

---

## What Should NOT Appear on the Website

The following belong in internal development documentation only:

- Terminal commands and Python code
- File names and directory paths (`data/processed/...`, `ml/...`)
- Phase numbers (Phase 1, Phase 2, etc.)
- Column names (`prim_width_pf`, `morph_coeff`, `model_type`, `derived_primary_ecl_duration`)
- Every rejected feature with technical reasons
- Internal validation steps and cleaning decisions
- Intermediate experiment numbers not used in the final story
- CLAUDE.md rules and instructions
- Implementation history and debugging logs
- Unsupported scientific claims
- Claims of novelty ("first study", "state of the art")

---

## Notes on Tone

- Write for a visitor who knows some science but is not a specialist in variable star astronomy.
- Avoid jargon — when technical terms are necessary, define them immediately.
- Be honest about what is and is not proven.
- Never imply that the model "failed" due to some fault in Gaia — the finding is about cross-survey transfer, not about either instrument being wrong.
- Never suggest the conclusion is stronger than the evidence supports.

---

*End of Website Blueprint*
