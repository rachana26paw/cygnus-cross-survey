---
name: data-validation
description: Validate whether the NASA TESS and ESA Gaia DR3 datasets can support the Cygnus cross-survey machine-learning experiment. Use this skill before ML training, feature engineering, or model development.
---

# Cygnus Data Validation Skill

## Purpose

Determine whether the available TESS and Gaia DR3 data can support the Cygnus research experiment:

TESS
→ Random Forest
→ TESS evaluation

then:

same trained model
→ Gaia evaluation

The purpose of this skill is DATA VALIDATION.

Do not train the model while using this skill.

## Validation tasks

Check:

1. TESS dataset structure.
2. Gaia dataset structure.
3. Important columns.
4. Star/source identifiers.
5. TESS-Gaia cross-match feasibility.
6. Available labels.
7. Label compatibility.
8. Common or scientifically comparable features.
9. Missing values.
10. Duplicate records.
11. Data quality.
12. Data leakage risks.
13. Whether the current pilot dataset is sufficient.

## Important research rule

Do not assume that two features are comparable simply because they have similar names.

For every proposed common feature, explain:

- how it is obtained from TESS
- how it is obtained from Gaia
- whether the measurements are scientifically comparable

## Candidate features

Investigate:

- period
- mean brightness
- amplitude/variability
- standard deviation
- skewness

Only recommend features that can genuinely and consistently be obtained from both surveys.

## Labels

Determine exactly what labels/classifications are available.

Do not create labels by guessing.

Do not create negative examples artificially unless explicitly approved after scientific justification.

If valid labels are unavailable, report the problem instead of training a model.

## Gaia epoch photometry

Treat each Gaia source separately.

Do not mix observations from different source_ids.

Preserve:

- source_id
- observation time
- flux/magnitude
- measurement uncertainty
- relevant quality flags

## Data leakage

Check for:

- duplicate objects across train/test
- test information entering preprocessing
- Gaia information entering TESS training
- target-derived features
- accidental use of labels as features

The Gaia cross-survey evaluation must remain separate from model training.

## Output

When this skill is later used, create:

results/data_validation_report.md

The report should contain:

1. Dataset inventory
2. TESS assessment
3. Gaia assessment
4. Cross-match assessment
5. Label assessment
6. Feature compatibility
7. Missing data
8. Duplicate data
9. Data-quality issues
10. Data-leakage risks
11. Problems that must be solved
12. What is currently possible
13. Recommended next step

Do not train ML during validation.

Use simple language in the report.
