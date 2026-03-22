from apexlab.datasets.split import split_indices


def test_split_indices_is_deterministic() -> None:
    result_a = split_indices(20, test_size=0.2, seed=1337)
    result_b = split_indices(20, test_size=0.2, seed=1337)
    assert result_a == result_b
    assert len(result_a.test_indices) == 4
    assert len(result_a.train_indices) == 16


def test_split_indices_supports_stratification() -> None:
    labels = ["a"] * 8 + ["b"] * 8
    result = split_indices(16, test_size=4, seed=7, stratify=labels)
    test_labels = [labels[i] for i in result.test_indices]
    assert len(result.test_indices) == 4
    assert sorted(test_labels).count("a") == 2
    assert sorted(test_labels).count("b") == 2
