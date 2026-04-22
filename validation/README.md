# ApexLab Validation

<p align="center">
	<img src="../assets/apex_lab_logo.png" alt="ApexLab logo" width="176">
</p>

> Public validation packet and supporting figures for ApexLab's current external-reference alignment lane.

**Current published packet:** `APEXLAB_REFERENCE_VALIDATION_20260324`  
**Status:** Pass  
**Audience:** public reviewers, package consumers, and integration partners  
**Primary public surfaces:** Markdown summary, HTML summary, and detailed validation report

This directory is intentionally tracked and public so the ApexLab repository exposes its validation story directly in the project tree instead of burying it behind internal-only reporting surfaces.

## Current public artifacts

| Artifact | Format | Purpose |
| --- | --- | --- |
| [APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.md](./APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.md) | Markdown | concise public-facing synopsis of the current reference-alignment posture |
| [APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.html](./APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.html) | HTML | browser-friendly branded summary surface for quick review |
| [APEXLAB_REFERENCE_VALIDATION_REPORT_20260324.md](./APEXLAB_REFERENCE_VALIDATION_REPORT_20260324.md) | Markdown | detailed scientific write-up of the 2026-03-24 validation run |
| `projects/apexlab/logs/metrics/reference_validation_20260324.json` | JSON | canonical machine-readable artifact for the validation run |

## Validation outcome at a glance

- the statistical comparison helpers passed their declared tolerance checks
- the OLS lane matched the reference implementation to near machine precision
- the logistic lane passed its bounded agreement checks while preserving its non-convergence diagnostic
- the current packet is suitable for public repository visibility and reviewer inspection

## Companion figure panel

<p align="center">
	<img src="./canary_v1_dist.png" alt="Canary anomaly-score distribution on log-count scale" width="31%">
	<img src="./canary_v1_thresh.png" alt="Threshold impact analysis at the current operating point" width="31%">
	<img src="./canary_v1_test_nolog.png" alt="Canary anomaly-score distribution on linear-count scale" width="31%">
</p>

These figures provide the surrounding analytical context used by the current reference-validation write-up. They remain in the tracked validation lane so public readers can inspect the same visual evidence family cited by the detailed report.

## How to use this directory

1. Start with the [Markdown summary](./APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.md) for the shortest public read.
2. Open the [HTML summary](./APEXLAB_REFERENCE_VALIDATION_SUMMARY_20260324.html) for a polished browser-friendly view.
3. Use the [detailed report](./APEXLAB_REFERENCE_VALIDATION_REPORT_20260324.md) when you want the full methodological and interpretive context.

## Related public surfaces

- [ApexLab root README](../README.md)
- [Reference validation runner](../examples/reference_validation_run.py)
- [Evaluation demo](../examples/evaluation_demo.py)
