from __future__ import annotations

import importlib.util
import sys
from types import ModuleType
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
	sys.path.insert(0, str(SRC_ROOT))


def load_module_from_path(module_name: str, file_path: Path) -> ModuleType:
	spec = importlib.util.spec_from_file_location(module_name, file_path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Could not load module spec for {file_path}")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


simplex_module = load_module_from_path("apexlab_models_simplex_demo", SRC_ROOT / "apexlab" / "models" / "simplex.py")
diagnostics_module = load_module_from_path(
	"apexlab_diagnostics_convergence_demo",
	SRC_ROOT / "apexlab" / "diagnostics" / "convergence.py",
)

ApexRegressor = simplex_module.ApexRegressor
summarize_history = diagnostics_module.summarize_history


def main() -> None:
	x = np.array(
		[
			[1.0, 0.0, 0.0],
			[0.0, 1.0, 0.0],
			[0.0, 0.0, 1.0],
			[0.5, 0.3, 0.2],
			[0.2, 0.5, 0.3],
			[0.3, 0.2, 0.5],
		],
		dtype=float,
	)
	true_weights = np.array([0.6, 0.3, 0.1], dtype=float)
	y = x @ true_weights

	model = ApexRegressor(learning_rate=0.1, max_iter=4000, tol=1e-10).fit(x, y)
	predictions = model.predict(x)
	summary = summarize_history(model.history, tolerance=1e-12)

	print("ApexLab simplex regression demo")
	print(f"learned weights: {np.round(model.weights, 6).tolist()}")
	print(f"weight sum: {float(np.sum(model.weights)):.6f}")
	print(f"predictions: {np.round(predictions, 6).tolist()}")
	print(f"convergence summary: {summary}")


if __name__ == "__main__":
	main()
