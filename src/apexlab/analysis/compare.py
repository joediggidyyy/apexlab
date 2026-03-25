"""Two-sample statistical comparison helpers for ApexLab."""

from __future__ import annotations

import math
from typing import Any, Sequence


def _normal_cdf(value: float) -> float:
	return 0.5 * (1.0 + math.erf(float(value) / math.sqrt(2.0)))


def _coerce_float_list(values: Sequence[float | int | str], *, name: str) -> list[float]:
	if not values:
		raise ValueError(f"{name} must not be empty")
	out: list[float] = []
	for index, value in enumerate(values, start=1):
		try:
			out.append(float(value))
		except Exception as exc:
			raise ValueError(f"Could not parse numeric value in {name} at position {index}: {value!r}") from exc
	return out


def _median(values: list[float]) -> float:
	ordered = sorted(values)
	n = len(ordered)
	mid = n // 2
	if n % 2 == 1:
		return float(ordered[mid])
	return float((ordered[mid - 1] + ordered[mid]) / 2.0)


def _quartiles(values: list[float]) -> tuple[float, float]:
	ordered = sorted(values)
	n = len(ordered)
	mid = n // 2
	if n % 2 == 0:
		lower = ordered[:mid]
		upper = ordered[mid:]
	else:
		lower = ordered[:mid]
		upper = ordered[mid + 1 :]
	if not lower:
		lower = ordered
	if not upper:
		upper = ordered
	return float(_median(lower)), float(_median(upper))


def _sample_variance(values: list[float]) -> float:
	if len(values) < 2:
		return 0.0
	mean = sum(values) / float(len(values))
	return float(sum((value - mean) ** 2 for value in values) / float(len(values) - 1))


def summary_stats(values: Sequence[float | int | str]) -> dict[str, float | int]:
	parsed = _coerce_float_list(values, name="values")
	ordered = sorted(parsed)
	q1, q3 = _quartiles(ordered)
	variance = _sample_variance(ordered)
	return {
		"n": int(len(ordered)),
		"mean": float(sum(ordered) / float(len(ordered))),
		"median": float(_median(ordered)),
		"min": float(ordered[0]),
		"max": float(ordered[-1]),
		"variance": float(variance),
		"std": float(math.sqrt(variance)),
		"q1": float(q1),
		"q3": float(q3),
		"iqr": float(q3 - q1),
	}


def rank_values(values: Sequence[float]) -> list[float]:
	indexed = sorted(enumerate(values), key=lambda item: item[1])
	ranks = [0.0] * len(indexed)
	position = 0
	while position < len(indexed):
		end = position + 1
		while end < len(indexed) and indexed[end][1] == indexed[position][1]:
			end += 1
		average_rank = ((position + 1) + end) / 2.0
		for tie_index in range(position, end):
			original_index = indexed[tie_index][0]
			ranks[original_index] = float(average_rank)
		position = end
	return ranks


def mann_whitney_u(sample_a: Sequence[float | int | str], sample_b: Sequence[float | int | str]) -> dict[str, Any]:
	a = _coerce_float_list(sample_a, name="sample_a")
	b = _coerce_float_list(sample_b, name="sample_b")
	combined = a + b
	ranks = rank_values(combined)
	n_a = len(a)
	n_b = len(b)
	rank_sum_a = float(sum(ranks[:n_a]))
	rank_sum_b = float(sum(ranks[n_a:]))
	u_a = rank_sum_a - (n_a * (n_a + 1) / 2.0)
	u_b = rank_sum_b - (n_b * (n_b + 1) / 2.0)
	u_stat = float(min(u_a, u_b))
	mu = float(n_a * n_b) / 2.0
	n_total = n_a + n_b
	tie_counts: dict[float, int] = {}
	for value in combined:
		tie_counts[value] = tie_counts.get(value, 0) + 1
	tie_term = sum(count ** 3 - count for count in tie_counts.values() if count > 1)
	variance_term = ((n_total + 1.0) - (tie_term / float(n_total * (n_total - 1)))) if n_total > 1 else 0.0
	sigma = math.sqrt((n_a * n_b / 12.0) * variance_term) if variance_term > 0 else 0.0
	if sigma > 0:
		z_score = (u_stat - mu + 0.5) / sigma
		p_value = max(0.0, min(1.0, 2.0 * (1.0 - _normal_cdf(abs(z_score)))))
	else:
		z_score = 0.0
		p_value = 1.0
	return {
		"test": "mann_whitney_u",
		"statistic": float(u_stat),
		"u_statistic": float(u_stat),
		"u_a": float(u_a),
		"u_b": float(u_b),
		"z_score": float(z_score),
		"p_value": float(p_value),
		"n_a": int(n_a),
		"n_b": int(n_b),
		"interpretation": "Lower p-values indicate stronger evidence that the two samples differ in rank distribution.",
		"notes": "Uses average-rank tie handling and a normal-approximation p-value without scipy.",
	}


def ks_two_sample(sample_a: Sequence[float | int | str], sample_b: Sequence[float | int | str]) -> dict[str, Any]:
	a = sorted(_coerce_float_list(sample_a, name="sample_a"))
	b = sorted(_coerce_float_list(sample_b, name="sample_b"))
	n_a = len(a)
	n_b = len(b)
	i = j = 0
	d_stat = 0.0
	for value in sorted(set(a + b)):
		while i < n_a and a[i] <= value:
			i += 1
		while j < n_b and b[j] <= value:
			j += 1
		cdf_a = i / float(n_a)
		cdf_b = j / float(n_b)
		d_stat = max(d_stat, abs(cdf_a - cdf_b))
	effective_n = (n_a * n_b) / float(n_a + n_b)
	if effective_n > 0:
		lam = (math.sqrt(effective_n) + 0.12 + (0.11 / math.sqrt(effective_n))) * d_stat
		series = 0.0
		for k in range(1, 101):
			term = ((-1) ** (k - 1)) * math.exp(-2.0 * (lam ** 2) * (k ** 2))
			series += term
			if abs(term) < 1e-10:
				break
		p_value = max(0.0, min(1.0, 2.0 * series))
	else:
		p_value = 1.0
	return {
		"test": "ks_two_sample",
		"statistic": float(d_stat),
		"d_statistic": float(d_stat),
		"p_value": float(p_value),
		"n_a": int(n_a),
		"n_b": int(n_b),
		"interpretation": "Higher KS D values indicate stronger separation between empirical distributions.",
		"notes": "Uses the two-sample KS asymptotic series approximation without scipy.",
	}


def cohens_d(sample_a: Sequence[float | int | str], sample_b: Sequence[float | int | str]) -> dict[str, Any]:
	a = _coerce_float_list(sample_a, name="sample_a")
	b = _coerce_float_list(sample_b, name="sample_b")
	n_a = len(a)
	n_b = len(b)
	mean_a = sum(a) / float(n_a)
	mean_b = sum(b) / float(n_b)
	var_a = _sample_variance(a)
	var_b = _sample_variance(b)
	pooled_num = ((n_a - 1) * var_a) + ((n_b - 1) * var_b)
	pooled_den = float(max(1, n_a + n_b - 2))
	pooled_std = math.sqrt(pooled_num / pooled_den) if pooled_num > 0 else 0.0
	effect = 0.0 if pooled_std == 0.0 else float((mean_b - mean_a) / pooled_std)
	magnitude = abs(effect)
	if magnitude < 0.2:
		bucket = "negligible"
	elif magnitude < 0.5:
		bucket = "small"
	elif magnitude < 0.8:
		bucket = "medium"
	else:
		bucket = "large"
	return {
		"test": "cohens_d",
		"statistic": float(effect),
		"cohens_d": float(effect),
		"p_value": None,
		"effect_bucket": bucket,
		"n_a": int(n_a),
		"n_b": int(n_b),
		"interpretation": "Signed effect size where positive values indicate sample_b trends higher than sample_a.",
		"notes": "Uses pooled standard deviation and standard Cohen's d magnitude bands.",
	}


def welch_t_test(sample_a: Sequence[float | int | str], sample_b: Sequence[float | int | str]) -> dict[str, Any]:
	a = _coerce_float_list(sample_a, name="sample_a")
	b = _coerce_float_list(sample_b, name="sample_b")
	n_a = len(a)
	n_b = len(b)
	mean_a = sum(a) / float(n_a)
	mean_b = sum(b) / float(n_b)
	var_a = _sample_variance(a)
	var_b = _sample_variance(b)
	term_a = var_a / float(n_a)
	term_b = var_b / float(n_b)
	denominator = math.sqrt(term_a + term_b) if (term_a + term_b) > 0 else 0.0
	t_stat = 0.0 if denominator == 0.0 else float((mean_b - mean_a) / denominator)
	if term_a == 0.0 and term_b == 0.0:
		degrees_of_freedom = float(max(0, n_a + n_b - 2))
	else:
		numerator = (term_a + term_b) ** 2
		denom = 0.0
		if n_a > 1:
			denom += (term_a ** 2) / float(n_a - 1)
		if n_b > 1:
			denom += (term_b ** 2) / float(n_b - 1)
		degrees_of_freedom = 0.0 if denom == 0.0 else float(numerator / denom)
	p_value = max(0.0, min(1.0, 2.0 * (1.0 - _normal_cdf(abs(t_stat)))))
	return {
		"test": "welch_t_test",
		"statistic": float(t_stat),
		"t_statistic": float(t_stat),
		"degrees_of_freedom": float(degrees_of_freedom),
		"p_value": float(p_value),
		"n_a": int(n_a),
		"n_b": int(n_b),
		"interpretation": "Signed t statistic where positive values indicate sample_b has a higher mean than sample_a.",
		"notes": "Uses Welch-Satterthwaite degrees of freedom and a normal-approximation p-value without scipy.",
	}


def _direction_label(label_a: str, label_b: str, mean_a: float, mean_b: float) -> str:
	if mean_b > mean_a:
		return f"{label_b}_mean_gt_{label_a}_mean"
	if mean_b < mean_a:
		return f"{label_b}_mean_lt_{label_a}_mean"
	return f"{label_b}_mean_eq_{label_a}_mean"


def _separation_label(effect_bucket: str) -> str:
	if effect_bucket == "negligible":
		return "weak"
	if effect_bucket == "small":
		return "modest"
	if effect_bucket == "medium":
		return "moderate"
	return "strong"


def compare_distributions(
	sample_a: Sequence[float | int | str],
	sample_b: Sequence[float | int | str],
	*,
	label_a: str = "lane_a",
	label_b: str = "lane_b",
) -> dict[str, Any]:
	a = _coerce_float_list(sample_a, name="sample_a")
	b = _coerce_float_list(sample_b, name="sample_b")
	summary_a = summary_stats(a)
	summary_b = summary_stats(b)
	mw = mann_whitney_u(a, b)
	ks = ks_two_sample(a, b)
	welch = welch_t_test(a, b)
	effect = cohens_d(a, b)
	direction = _direction_label(label_a, label_b, float(summary_a["mean"]), float(summary_b["mean"]))
	separation = _separation_label(str(effect["effect_bucket"]))
	tiny_sample = min(len(a), len(b)) < 5
	caution = " because sample counts are small, interpret the inferential results cautiously" if tiny_sample else ""
	interpretation = (
		f"{label_b} shows {'higher' if float(summary_b['mean']) > float(summary_a['mean']) else 'lower' if float(summary_b['mean']) < float(summary_a['mean']) else 'similar'} "
		f"central tendency than {label_a}, with a {effect['effect_bucket']} effect size and {separation} distributional separation{caution}."
	)
	return {
		"labels": {"a": label_a, "b": label_b},
		"samples": {"n_a": int(len(a)), "n_b": int(len(b))},
		"summary": {"a": summary_a, "b": summary_b},
		"tests": {
			"mann_whitney_u": mw,
			"ks_two_sample": ks,
			"welch_t_test": welch,
		},
		"effect_size": {"cohens_d": effect},
		"direction": direction,
		"interpretation": interpretation,
	}
