"""Tests for logslice.sample."""
import pytest
from logslice.sample import sample_records, sample_rate, every_nth

RECORDS = [{"id": i, "msg": f"log {i}"} for i in range(20)]


class TestSampleRecords:
    def test_returns_n_records(self):
        result = sample_records(RECORDS, 5, seed=42)
        assert len(result) == 5

    def test_all_results_from_source(self):
        result = sample_records(RECORDS, 5, seed=42)
        for r in result:
            assert r in RECORDS

    def test_n_larger_than_population(self):
        result = sample_records(RECORDS, 100)
        assert len(result) == len(RECORDS)

    def test_n_zero_returns_empty(self):
        assert sample_records(RECORDS, 0) == []

    def test_n_negative_returns_empty(self):
        assert sample_records(RECORDS, -1) == []

    def test_seed_reproducible(self):
        a = sample_records(RECORDS, 5, seed=7)
        b = sample_records(RECORDS, 5, seed=7)
        assert a == b

    def test_different_seeds_differ(self):
        a = sample_records(RECORDS, 5, seed=1)
        b = sample_records(RECORDS, 5, seed=2)
        assert a != b


class TestSampleRate:
    def test_rate_zero_returns_empty(self):
        assert sample_rate(RECORDS, 0.0) == []

    def test_rate_one_returns_all(self):
        assert sample_rate(RECORDS, 1.0) == RECORDS

    def test_rate_half_approx(self):
        result = sample_rate(RECORDS, 0.5, seed=42)
        assert 0 < len(result) < len(RECORDS)

    def test_seed_reproducible(self):
        a = sample_rate(RECORDS, 0.5, seed=99)
        b = sample_rate(RECORDS, 0.5, seed=99)
        assert a == b


class TestEveryNth:
    def test_every_1_returns_all(self):
        assert every_nth(RECORDS, 1) == RECORDS

    def test_every_2_returns_half(self):
        result = every_nth(RECORDS, 2)
        assert result == RECORDS[::2]

    def test_every_5(self):
        result = every_nth(RECORDS, 5)
        assert len(result) == 4
        assert result[0] == RECORDS[0]
        assert result[1] == RECORDS[5]

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            every_nth(RECORDS, 0)

    def test_empty_input(self):
        assert every_nth([], 2) == []
