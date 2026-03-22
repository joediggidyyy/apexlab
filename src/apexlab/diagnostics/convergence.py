"""Convergence diagnostics for ApexLab."""

from __future__ import annotations

from typing import Optional


def summarize_history(history: list[float], *, tolerance: Optional[float] = None) -> dict[str, float | int | bool | None]:
	"""Summarize a scalar optimization history sequence."""

	if not history:
		return {
			"iterations": 0,
			"initial": None,
			"final": None,
			"best": None,
			"improved": False,
			"delta": None,
			"converged": None,
		}

	initial = float(history[0])
	final = float(history[-1])
	best = float(min(history))
	delta = float(final - initial)
	improved = bool(final <= initial)
	converged = None if tolerance is None else bool(abs(delta) <= float(tolerance) or (len(history) > 1 and abs(history[-1] - history[-2]) <= float(tolerance)))
	return {
		"iterations": int(len(history)),
		"initial": initial,
		"final": final,
		"best": best,
		"improved": improved,
		"delta": delta,
		"converged": converged,
	}
