"""Deterministic split utilities for ApexLab."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SplitResult:
	train_indices: list[int]
	test_indices: list[int]


def parse_test_size(test_size: str) -> tuple[str, float | int]:
	s = test_size.strip()
	if s == "":
		raise ValueError("test_size must not be empty")
	if s.isdigit():
		n = int(s)
		if n < 0:
			raise ValueError("test_size count must be >= 0")
		return "count", n
	p = float(s)
	if not (0.0 <= p <= 1.0):
		raise ValueError("test_size fraction must be between 0 and 1")
	return "fraction", p


def allocate_counts_proportionally(total_test: int, bucket_sizes: dict[str, int]) -> dict[str, int]:
	if total_test <= 0:
		return {k: 0 for k in bucket_sizes.keys()}
	total = sum(bucket_sizes.values())
	if total == 0:
		return {k: 0 for k in bucket_sizes.keys()}

	raw = {k: (bucket_sizes[k] / total) * total_test for k in bucket_sizes.keys()}
	base = {k: int(raw[k]) for k in bucket_sizes.keys()}
	remainder = int(total_test - sum(base.values()))
	if remainder <= 0:
		return base

	fracs = sorted(((k, raw[k] - base[k]) for k in bucket_sizes.keys()), key=lambda kv: (kv[1], kv[0]), reverse=True)
	for i in range(remainder):
		base[fracs[i % len(fracs)][0]] += 1
	return base


def split_indices(
	n_rows: int,
	*,
	test_size: float | int,
	seed: int,
	stratify: Optional[list[str]] = None,
) -> SplitResult:
	rng = random.Random(seed)
	total_test = int(round(test_size * n_rows)) if isinstance(test_size, float) else int(test_size)
	total_test = max(0, min(total_test, n_rows))

	if n_rows == 0:
		return SplitResult(train_indices=[], test_indices=[])

	if stratify is None:
		all_idx = list(range(n_rows))
		rng.shuffle(all_idx)
		test_idx = set(all_idx[:total_test])
		return SplitResult(
			train_indices=[i for i in range(n_rows) if i not in test_idx],
			test_indices=[i for i in range(n_rows) if i in test_idx],
		)

	if len(stratify) != n_rows:
		raise ValueError("stratify labels length must equal number of rows")

	buckets: dict[str, list[int]] = {}
	for i, label in enumerate(stratify):
		buckets.setdefault(str(label), []).append(i)

	bucket_sizes = {k: len(v) for k, v in sorted(buckets.items(), key=lambda kv: kv[0])}
	per_bucket_test = allocate_counts_proportionally(total_test, bucket_sizes)
	test_set: set[int] = set()

	for k in bucket_sizes.keys():
		idxs = list(buckets[k])
		rng.shuffle(idxs)
		take = min(per_bucket_test.get(k, 0), len(idxs))
		test_set.update(idxs[:take])

	if len(test_set) < total_test:
		remaining = [i for i in range(n_rows) if i not in test_set]
		rng.shuffle(remaining)
		test_set.update(remaining[: total_test - len(test_set)])
	elif len(test_set) > total_test:
		extra = list(test_set)
		rng.shuffle(extra)
		for i in extra[: len(test_set) - total_test]:
			test_set.remove(i)

	return SplitResult(
		train_indices=[i for i in range(n_rows) if i not in test_set],
		test_indices=[i for i in range(n_rows) if i in test_set],
	)
