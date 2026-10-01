# Cygnus — Project Instructions

## 1. Project Identity

Project name:
Cygnus

Repository:
cygnus-cross-survey

Academic project title:
Evaluating the Reliability of Machine Learning Confidence for Variable-Star Classification Across Astronomical Surveys

Research question:
"Can we trust the confidence score given by an ML model when it classifies variable stars from a different astronomical survey?"

Domain:
Astronomy + Machine Learning

Primary astronomical focus:
Eclipsing binary stars

Primary surveys:
- NASA TESS
- ESA Gaia DR3

---

## 2. Project Goal

The project investigates whether machine-learning prediction confidence remains reliable when a model is applied to astronomical data from a different survey.

The intended experiment is:

TESS
→ data preparation
→ Random Forest
→ TESS test set
→ evaluate normal performance
→ same trained model
→ Gaia test data
→ compare predictions, correctness and confidence

IMPORTANT:
This experiment is only valid if TESS and Gaia can provide scientifically comparable features and valid labels.

Therefore, data validation must happen BEFORE ML training.

---

## 3. Current Development Stage

Current stage:

DATA VALIDATION

Do NOT start ML training until the data-validation stage confirms that the experiment is scientifically feasible.

Do not prematurely:
- train Random Forest
- build the API
- build the frontend
- create final prediction dashboards
- claim research results
- claim novelty

---

## 4. Dataset Structure

Raw data must remain unchanged.

Expected structure:

data/
├── raw/
│   ├── tess/
│   │   └── NASA TESS Dataset.csv
│   │
│   └── gaia/
│       └── epoch_photometry/
│           └── 500 Gaia epoch-photometry CSV files
│
└── processed/

Raw datasets must NEVER be overwritten.

Any cleaned, transformed, combined or feature-engineered dataset must be written to:

data/processed/

---

## 5. Known Dataset Context

The current TESS dataset is an object-level catalog containing approximately 4,584 records and approximately 28 columns.

It contains already-derived astronomical properties such as:
- TESS identifier
- signal identifier
- right ascension
- declination
- TESS magnitude
- period
- period uncertainty
- morphology coefficient
- primary/secondary eclipse widths
- primary/secondary eclipse depths
- sector information

The current Gaia dataset consists of approximately 500 individual epoch-photometry CSV files.

Each Gaia file represents one Gaia source and contains time-series photometric information including:
- source_id
- transit information
- observation times
- G-band flux/magnitude
- BP-band flux/magnitude
- RP-band flux/magnitude
- measurement uncertainties
- quality/rejection flags

These datasets are NOT assumed to be directly compatible.

The Gaia files were obtained for sources associated with Gaia DR3 eclipsing-binary data.

Do not automatically assume that all Gaia sources constitute a valid binary classification dataset.

---

## 6. Scientific Validation Rules

Before creating an ML dataset, verify:

1. TESS and Gaia source identifiers.
2. Whether objects can be cross-matched reliably.
3. Whether the labels are valid and comparable.
4. Whether the same or scientifically comparable features can be obtained from both surveys.
5. Missing values.
6. Duplicate observations.
7. Number of observations per source.
8. Data quality and measurement reliability.
9. Whether enough matched examples exist.
10. Whether the proposed experiment can be performed without data leakage.

Never invent labels.

Never create negative examples by guessing.

Never assume two features are equivalent only because they have similar names.

If a feature must be derived from time-series data, explain how it is calculated.

If the data are insufficient for the original experiment, stop and report the problem before changing the research question.

---

## 7. Candidate Common Features

Investigate whether the following can be obtained consistently from BOTH TESS and Gaia:

- period
- mean brightness
- amplitude / variability
- standard deviation
- skewness

Only use a feature in the final ML dataset if it is scientifically defensible and can be obtained consistently from both surveys.

Do not force the datasets to match.

---

## 8. Machine Learning

Primary model:

Random Forest Classifier

Optional baseline:

Logistic Regression

Do not introduce:
- deep learning
- transformers
- neural networks
- new ML algorithms

unless explicitly requested.

Use:

predict_proba()

when prediction confidence is required.

The model must not be trained on Gaia data for the main cross-survey experiment.

---

## 9. Evaluation

Evaluate ordinary classification performance using:

- confusion matrix
- accuracy
- precision
- recall
- F1 score

For the main research question, evaluate:

- predicted class
- prediction confidence
- actual correctness

The main question is whether high-confidence predictions are actually more likely to be correct.

Calibration/reliability analysis may be added after the basic experiment works.

Do not report invented or estimated results.

---

## 10. Data Leakage Rules

Strictly prevent data leakage.

Rules:

- Do not train on test data.
- Do not tune using the final test set.
- Do not use Gaia data to train the main cross-survey model.
- Do not calculate preprocessing parameters using the combined train + test data.
- Fit transformations only on the training data.
- Keep the cross-survey Gaia evaluation separate.

Document any decisions that could affect the validity of the experiment.

---

## 11. Research Integrity

Never fabricate:

- dataset columns
- labels
- measurements
- scientific findings
- model results
- URLs
- sources
- literature claims

Do not claim:
- "first study"
- "novel algorithm"
- "never done before"
- "state of the art"

unless the claim has been specifically verified from appropriate literature.

When something is uncertain:
1. identify the uncertainty
2. explain why it matters
3. verify it if possible
4. do not silently assume an answer

Distinguish between:
- documented facts
- analysis
- assumptions
- hypotheses
- experimental results

---

## 12. Coding Style

The project owner is still learning programming and machine learning.

Write understandable code.

Prefer:
- clear variable names
- simple functions
- readable logic
- comments for important scientific decisions
- reproducible scripts

Avoid unnecessary:
- abstractions
- complicated architecture
- clever one-line code
- unnecessary dependencies

Do not hide important scientific decisions inside code.

---

## 13. Project Structure

Maintain this structure:

cygnus-cross-survey/
├── CLAUDE.md
├── .claude/
│   └── skills/
│       └── data-validation/
│           └── SKILL.md
│
├── data/
│   ├── raw/
│   │   ├── tess/
│   │   └── gaia/
│   │       └── epoch_photometry/
│   └── processed/
│
├── ml/
├── experiments/
├── results/
├── backend/
├── frontend/
└── README.md

Do not move project components into a different architecture without explaining why.

---

## 14. Development Workflow

Before a major change:

1. Inspect the existing project.
2. Understand the relevant files.
3. Explain the intended change briefly.
4. Make the smallest useful change.
5. Run an appropriate test or validation.
6. Report what changed.
7. Report whether the test/validation passed.

Do not silently make major architectural or scientific changes.

If a scientific/data problem is discovered:
STOP and explain it before changing the research scope.

---

## 15. Current Priority

The current priority is:

1. Organize raw datasets.
2. Validate TESS dataset.
3. Validate Gaia dataset.
4. Determine valid labels.
5. Determine cross-match feasibility.
6. Determine common scientifically defensible features.
7. Produce data-validation report.
8. Decide whether the approved ML experiment is feasible.
9. Only then build the ML pipeline.

Current output:

results/data_validation_report.md

Do not train the Random Forest until validation is complete.

---

## 16. Communication Style

Explain things in simple English.

The project owner wants to understand what is being built, not simply receive generated code.

When reporting technical findings:
- state what was found
- explain why it matters
- state what should happen next

Keep explanations concise unless detailed reasoning is requested.

---

## 17. Final Quality Rule

When uncertain, inspect the actual data and documentation instead of guessing.

The scientific validity of the project is more important than completing a feature quickly.

Correctness > speed.

Reproducibility > convenience.

Scientific validity > making the experiment work artificially.