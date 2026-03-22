import numpy as np
import pytest

from apexlab.models.simplex import ApexRegressor


def test_apex_regressor_fit_enforces_simplex_constraints() -> None:
    rng = np.random.default_rng(42)
    x = rng.normal(size=(120, 3))
    w_true = np.array([0.2, 0.5, 0.3])
    y = x @ w_true + rng.normal(scale=0.01, size=120)

    model = ApexRegressor(learning_rate=0.1, max_iter=800, tol=1e-9)
    model.fit(x, y)

    assert model.weights is not None
    assert np.isclose(np.sum(model.weights), 1.0, atol=1e-6)
    assert np.all(model.weights >= -1e-10)


def test_apex_regressor_predict_requires_fit() -> None:
    model = ApexRegressor()
    x = np.zeros((5, 3))

    with pytest.raises(ValueError):
        model.predict(x)
