from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

analysis = importlib.import_module("apexlab.analysis")
utc_now_iso = importlib.import_module("apexlab.evaluation.reports").utc_now_iso

cohens_d = analysis.cohens_d
compare_distributions = analysis.compare_distributions
ks_two_sample = analysis.ks_two_sample
logistic_fit = analysis.logistic_fit
mann_whitney_u = analysis.mann_whitney_u
ols_fit = analysis.ols_fit
welch_t_test = analysis.welch_t_test


def _to_float(value: Any) -> float:
    if value is None:
        return float("nan")
    return float(value)


def _probability_correlation(values_a: np.ndarray, values_b: np.ndarray) -> float:
    if values_a.size == 0 or values_b.size == 0:
        return 0.0
    if np.allclose(values_a, values_a[0]) and np.allclose(values_b, values_b[0]):
        return 1.0
    corr = np.corrcoef(values_a, values_b)[0, 1]
    return float(corr)


def _build_logistic_reference() -> LogisticRegression:
    try:
        return LogisticRegression(C=np.inf, solver="lbfgs", max_iter=20000)
    except Exception:
        return LogisticRegression(C=1e9, solver="lbfgs", max_iter=20000)


def validate_statistical_tests() -> dict[str, Any]:
    sample_a = [0.11, 0.17, 0.21, 0.29, 0.35, 0.39, 0.44, 0.52, 0.57, 0.61]
    sample_b = [0.63, 0.68, 0.72, 0.79, 0.81, 0.85, 0.89, 0.93, 0.97, 1.02]

    apex_mw = mann_whitney_u(sample_a, sample_b)
    scipy_mw = stats.mannwhitneyu(sample_a, sample_b, alternative="two-sided", method="asymptotic")

    apex_ks = ks_two_sample(sample_a, sample_b)
    scipy_ks = stats.ks_2samp(sample_a, sample_b, alternative="two-sided", method="asymp")
    scipy_ks_stat = float(getattr(scipy_ks, "statistic"))
    scipy_ks_p = float(getattr(scipy_ks, "pvalue"))

    apex_welch = welch_t_test(sample_a, sample_b)
    scipy_welch = stats.ttest_ind(sample_b, sample_a, equal_var=False)
    scipy_welch_stat = float(getattr(scipy_welch, "statistic"))
    scipy_welch_p = float(getattr(scipy_welch, "pvalue"))

    apex_d = cohens_d(sample_a, sample_b)
    pooled_var = (((len(sample_a) - 1) * np.var(sample_a, ddof=1)) + ((len(sample_b) - 1) * np.var(sample_b, ddof=1))) / float(len(sample_a) + len(sample_b) - 2)
    reference_d = (np.mean(sample_b) - np.mean(sample_a)) / np.sqrt(pooled_var)

    deltas = {
        "mann_whitney_stat": abs(_to_float(apex_mw["u_statistic"]) - float(scipy_mw.statistic)),
        "mann_whitney_p": abs(_to_float(apex_mw["p_value"]) - float(scipy_mw.pvalue)),
        "ks_stat": abs(_to_float(apex_ks["d_statistic"]) - scipy_ks_stat),
        "ks_p": abs(_to_float(apex_ks["p_value"]) - scipy_ks_p),
        "welch_t": abs(_to_float(apex_welch["t_statistic"]) - scipy_welch_stat),
        "welch_p": abs(_to_float(apex_welch["p_value"]) - scipy_welch_p),
        "cohens_d": abs(_to_float(apex_d["cohens_d"]) - float(reference_d)),
    }

    thresholds = {
        "mann_whitney_stat": 1e-9,
        "mann_whitney_p": 5e-2,
        "ks_stat": 1e-9,
        "ks_p": 5e-2,
        "welch_t": 1e-9,
        "welch_p": 5e-2,
        "cohens_d": 1e-9,
    }
    checks = {key: bool(value <= thresholds[key]) for key, value in deltas.items()}

    return {
        "status": "pass" if all(checks.values()) else "fail",
        "sample_sizes": {"n_a": len(sample_a), "n_b": len(sample_b)},
        "apex": {
            "mann_whitney_u": apex_mw,
            "ks_two_sample": apex_ks,
            "welch_t_test": apex_welch,
            "cohens_d": apex_d,
        },
        "reference": {
            "mann_whitney_u": {"statistic": float(scipy_mw.statistic), "p_value": float(scipy_mw.pvalue)},
            "ks_two_sample": {"statistic": scipy_ks_stat, "p_value": scipy_ks_p},
            "welch_t_test": {"statistic": scipy_welch_stat, "p_value": scipy_welch_p},
            "cohens_d": {"statistic": float(reference_d)},
        },
        "deltas": deltas,
        "thresholds": thresholds,
        "checks": checks,
        "notes": [
            "P-value comparisons use loose tolerances because ApexLab intentionally uses scipy-free approximations.",
            "Statistic deltas are expected to be exact or near-exact for these chosen fixtures.",
        ],
    }


def validate_ols() -> dict[str, Any]:
    x = np.asarray([
        [1.0, 0.5],
        [2.0, 1.5],
        [3.0, 1.0],
        [4.0, 2.0],
        [5.0, 2.5],
        [6.0, 3.0],
    ])
    y = 2.5 + (1.75 * x[:, 0]) - (0.4 * x[:, 1])

    apex = ols_fit(x.tolist(), y.tolist())
    reference = LinearRegression().fit(x, y)
    reference_coefficients = [float(reference.intercept_)] + [float(value) for value in reference.coef_.tolist()]
    reference_predictions = reference.predict(x)

    deltas = {
        "coefficients_max_abs": float(np.max(np.abs(np.asarray(apex["coefficients"]) - np.asarray(reference_coefficients)))),
        "predictions_max_abs": float(np.max(np.abs(np.asarray(apex["predictions"]) - np.asarray(reference_predictions)))),
    }
    thresholds = {
        "coefficients_max_abs": 1e-9,
        "predictions_max_abs": 1e-9,
    }
    checks = {key: bool(value <= thresholds[key]) for key, value in deltas.items()}

    return {
        "status": "pass" if all(checks.values()) else "fail",
        "apex": apex,
        "reference": {
            "coefficients": reference_coefficients,
            "predictions": reference_predictions.astype(float).tolist(),
        },
        "deltas": deltas,
        "thresholds": thresholds,
        "checks": checks,
    }


def validate_logistic() -> dict[str, Any]:
    x = np.asarray([
        [0.0, 0.1],
        [0.5, 0.2],
        [1.0, 0.4],
        [1.5, 0.8],
        [2.0, 1.2],
        [2.5, 1.4],
        [3.0, 1.8],
        [3.5, 2.0],
        [4.0, 2.2],
        [4.5, 2.5],
    ])
    y = np.asarray([0, 0, 0, 0, 0, 1, 1, 1, 1, 1], dtype=int)

    apex = logistic_fit(x.tolist(), y.tolist(), learning_rate=0.15, max_iter=12000, tol=1e-8)
    reference_model = _build_logistic_reference()
    reference_model.fit(x, y)
    reference_probabilities = reference_model.predict_proba(x)[:, 1]
    reference_predictions = reference_model.predict(x)
    reference_coefficients = [float(reference_model.intercept_[0])] + [float(value) for value in reference_model.coef_[0].tolist()]

    apex_probabilities = np.asarray(apex["probabilities"], dtype=float)
    apex_predictions = np.asarray(apex["predictions"], dtype=int)

    deltas = {
        "accuracy_abs": abs(float(apex["metrics"]["accuracy"]) - float(np.mean(reference_predictions == y))),
        "prediction_agreement": float(np.mean(apex_predictions == reference_predictions)),
        "probability_mae": float(np.mean(np.abs(apex_probabilities - reference_probabilities))),
        "probability_corr": _probability_correlation(apex_probabilities, reference_probabilities),
        "coefficient_sign_match": bool(np.all(np.sign(np.asarray(apex["coefficients"])) == np.sign(np.asarray(reference_coefficients)))),
    }
    thresholds = {
        "accuracy_abs": 5e-2,
        "prediction_agreement": 0.9,
        "probability_mae": 0.12,
        "probability_corr": 0.98,
        "coefficient_sign_match": True,
    }
    checks = {
        "accuracy_abs": bool(deltas["accuracy_abs"] <= thresholds["accuracy_abs"]),
        "prediction_agreement": bool(deltas["prediction_agreement"] >= thresholds["prediction_agreement"]),
        "probability_mae": bool(deltas["probability_mae"] <= thresholds["probability_mae"]),
        "probability_corr": bool(deltas["probability_corr"] >= thresholds["probability_corr"]),
        "coefficient_sign_match": bool(deltas["coefficient_sign_match"] == thresholds["coefficient_sign_match"]),
    }

    return {
        "status": "pass" if all(checks.values()) else "fail",
        "apex": apex,
        "reference": {
            "coefficients": reference_coefficients,
            "probabilities": reference_probabilities.astype(float).tolist(),
            "predictions": reference_predictions.astype(int).tolist(),
            "accuracy": float(np.mean(reference_predictions == y)),
        },
        "deltas": deltas,
        "thresholds": thresholds,
        "checks": checks,
        "notes": [
            "Logistic coefficient magnitudes may differ because optimizers are different; validation emphasizes probability quality, agreement, and sign consistency.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run ApexLab reference validation against scipy/sklearn baselines.")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "logs" / "metrics", help="Directory to write the validation summary JSON")
    parser.add_argument("--stem", default="reference_validation", help="Output filename stem for the validation summary")
    args = parser.parse_args(argv)

    statistical = validate_statistical_tests()
    ols = validate_ols()
    logistic = validate_logistic()

    sections = {
        "statistical_tests": statistical,
        "ols": ols,
        "logistic": logistic,
    }
    overall_pass = all(section.get("status") == "pass" for section in sections.values())
    payload = {
        "generated_at_utc": utc_now_iso(),
        "task": "reference_validation",
        "status": "pass" if overall_pass else "fail",
        "sections": sections,
        "summary": {
            "passed_sections": [name for name, section in sections.items() if section.get("status") == "pass"],
            "failed_sections": [name for name, section in sections.items() if section.get("status") != "pass"],
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.out_dir / f"{args.stem}.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    print("ApexLab reference validation run")
    print(f"overall status: {payload['status']}")
    for name, section in sections.items():
        print(f"- {name}: {section['status']}")
        if "deltas" in section:
            print(f"  deltas: {section['deltas']}")
    print(f"validation summary: {output_path}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
