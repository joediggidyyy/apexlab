from apexlab.diagnostics.convergence import summarize_history


def test_summarize_history_reports_progress() -> None:
    result = summarize_history([1.0, 0.5, 0.25], tolerance=1.0)
    assert result["iterations"] == 3
    assert result["initial"] == 1.0
    assert result["final"] == 0.25
    assert result["best"] == 0.25
    assert result["improved"] is True
    assert result["converged"] is True
