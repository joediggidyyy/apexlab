"""Comparison-report builders for ApexLab."""

from __future__ import annotations

from typing import Any

from apexlab.evaluation.reports import utc_now_iso


def _as_dict(value: Any) -> dict[str, Any]:
	return value if isinstance(value, dict) else {}


def _first_significant_p_value(tests: dict[str, Any], *, alpha: float = 0.05) -> float | None:
	for payload in tests.values():
		if not isinstance(payload, dict):
			continue
		p_value = payload.get("p_value")
		if isinstance(p_value, (int, float)) and float(p_value) <= float(alpha):
			return float(p_value)
	return None


def _derive_compare_flags(comparison: dict[str, Any]) -> dict[str, Any]:
	labels = _as_dict(comparison.get("labels"))
	samples = _as_dict(comparison.get("samples"))
	summary = _as_dict(comparison.get("summary"))
	tests = _as_dict(comparison.get("tests"))
	effect = _as_dict(_as_dict(comparison.get("effect_size")).get("cohens_d"))
	summary_a = _as_dict(summary.get("a"))
	summary_b = _as_dict(summary.get("b"))
	mean_a = float(summary_a.get("mean", 0.0))
	mean_b = float(summary_b.get("mean", 0.0))
	label_a = str(labels.get("a", "sample_a"))
	label_b = str(labels.get("b", "sample_b"))
	effect_bucket = str(effect.get("effect_bucket", "")).strip().lower()
	ks_payload = _as_dict(tests.get("ks_two_sample"))
	welch_payload = _as_dict(tests.get("welch_t_test"))
	small_sample = int(samples.get("n_a", 0)) < 5 or int(samples.get("n_b", 0)) < 5
	significant_p = _first_significant_p_value(tests)
	ks_stat = float(ks_payload.get("statistic", 0.0)) if ks_payload else 0.0
	welch_stat = float(welch_payload.get("statistic", 0.0)) if welch_payload else 0.0
	mean_delta = float(mean_b - mean_a)
	consistent_directionality = True
	if mean_delta != 0.0 and welch_payload:
		consistent_directionality = (mean_delta > 0.0 and welch_stat >= 0.0) or (mean_delta < 0.0 and welch_stat <= 0.0)
	recommendation = (
		f"{label_b} should be treated as materially different from {label_a} for the validated metric surface."
		if significant_p is not None or effect_bucket in {"medium", "large"}
		else f"{label_b} and {label_a} should be treated as broadly similar unless later evidence strengthens the separation signal."
	)
	return {
		"small_sample_caution": bool(small_sample),
		"p_value_supports_difference": bool(significant_p is not None),
		"distribution_separation_detected": bool(ks_stat >= 0.3 or (ks_payload and float(ks_payload.get("p_value", 1.0)) <= 0.05)),
		"practical_effect_present": bool(effect_bucket in {"small", "medium", "large"}),
		"strong_effect": bool(effect_bucket == "large"),
		"consistent_directionality": bool(consistent_directionality),
		"primary_signal": (
			"strong_effect"
			if effect_bucket == "large"
			else "significant_p_value"
			if significant_p is not None
			else "descriptive_difference"
		),
		"recommended_action": recommendation,
	}


def build_compare_report(
	comparison: dict[str, Any],
	*,
	generated_at_utc: str | None = None,
	inputs: dict[str, Any] | None = None,
	context: dict[str, Any] | None = None,
	code: dict[str, Any] | None = None,
) -> dict[str, Any]:
	comparison_payload = dict(comparison)
	flags = _derive_compare_flags(comparison_payload)
	effect = _as_dict(_as_dict(comparison_payload.get("effect_size")).get("cohens_d"))
	samples = _as_dict(comparison_payload.get("samples"))
	labels = _as_dict(comparison_payload.get("labels"))
	report_generated_at = generated_at_utc or utc_now_iso()
	interpretation_summary = str(comparison_payload.get("interpretation", "")).strip()
	interpretation = {
		"summary": interpretation_summary,
		"direction": comparison_payload.get("direction"),
		"effect_bucket": effect.get("effect_bucket"),
		"recommended_action": flags.get("recommended_action"),
	}
	return {
		"generated_at_utc": report_generated_at,
		"task": "compare",
		"identity": {
			"report_type": "comparison",
			"schema_version": "1.0",
			"generated_at_utc": report_generated_at,
		},
		"context": dict(context or {}),
		"inputs": {
			"label_a": labels.get("a"),
			"label_b": labels.get("b"),
			"n_a": samples.get("n_a"),
			"n_b": samples.get("n_b"),
			**dict(inputs or {}),
		},
		"metrics": {
			"n_a": samples.get("n_a"),
			"n_b": samples.get("n_b"),
			"direction": comparison_payload.get("direction"),
			"effect_bucket": effect.get("effect_bucket"),
			"cohens_d": effect.get("cohens_d"),
		},
		"comparison": comparison_payload,
		"interpretation": interpretation,
		"flags": flags,
		"code": {
			"producer": "apexlab.evaluation.compare_report.build_compare_report",
			**dict(code or {}),
		},
	}
