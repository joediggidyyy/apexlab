"""Statistical analysis utilities for ApexLab."""

from apexlab.analysis.compare import (
	cohens_d,
	compare_distributions,
	ks_two_sample,
	mann_whitney_u,
	summary_stats,
	welch_t_test,
)
from apexlab.analysis.regression import (
	logistic_fit,
	logistic_predict,
	logistic_predict_proba,
	ols_fit,
	ols_predict,
	prepare_design_matrix,
	sigmoid,
	summarize_coefficients,
)

__all__ = [
	"cohens_d",
	"compare_distributions",
	"ks_two_sample",
	"logistic_fit",
	"logistic_predict",
	"logistic_predict_proba",
	"mann_whitney_u",
	"ols_fit",
	"ols_predict",
	"prepare_design_matrix",
	"sigmoid",
	"summary_stats",
	"summarize_coefficients",
	"welch_t_test",
]
