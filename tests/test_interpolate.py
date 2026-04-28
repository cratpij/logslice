import pytest
from logslice.interpolate import fill_forward, fill_backward, fill_constant, fill_linear


# ---------------------------------------------------------------------------
# fill_forward
# ---------------------------------------------------------------------------

class TestFillForward:
    def test_carries_last_value_forward(self):
        records = [{"v": 1}, {"v": None}, {"v": None}]
        out = fill_forward(records, "v")
        assert [r["v"] for r in out] == [1, 1, 1]

    def test_no_previous_value_leaves_none(self):
        records = [{"v": None}, {"v": 5}]
        out = fill_forward(records, "v")
        assert out[0]["v"] is None
        assert out[1]["v"] == 5

    def test_missing_key_filled_once_seen(self):
        records = [{"x": 1}, {"v": 10}, {"x": 2}]
        out = fill_forward(records, "v")
        assert out[2]["v"] == 10

    def test_does_not_mutate_original(self):
        records = [{"v": 3}, {"v": None}]
        fill_forward(records, "v")
        assert records[1]["v"] is None

    def test_empty_input(self):
        assert fill_forward([], "v") == []


# ---------------------------------------------------------------------------
# fill_backward
# ---------------------------------------------------------------------------

class TestFillBackward:
    def test_propagates_next_value_backward(self):
        records = [{"v": None}, {"v": None}, {"v": 7}]
        out = fill_backward(records, "v")
        assert [r["v"] for r in out] == [7, 7, 7]

    def test_no_following_value_leaves_none(self):
        records = [{"v": 5}, {"v": None}]
        out = fill_backward(records, "v")
        assert out[1]["v"] is None

    def test_does_not_mutate_original(self):
        records = [{"v": None}, {"v": 9}]
        fill_backward(records, "v")
        assert records[0]["v"] is None

    def test_empty_input(self):
        assert fill_backward([], "v") == []


# ---------------------------------------------------------------------------
# fill_constant
# ---------------------------------------------------------------------------

class TestFillConstant:
    def test_fills_none_with_constant(self):
        records = [{"v": None}, {"v": 2}]
        out = list(fill_constant(records, "v", 0))
        assert out[0]["v"] == 0
        assert out[1]["v"] == 2

    def test_fills_missing_key(self):
        records = [{"x": 1}]
        out = list(fill_constant(records, "v", "default"))
        assert out[0]["v"] == "default"

    def test_does_not_mutate_original(self):
        records = [{"v": None}]
        list(fill_constant(records, "v", 99))
        assert records[0]["v"] is None

    def test_empty_input(self):
        assert list(fill_constant([], "v", 0)) == []


# ---------------------------------------------------------------------------
# fill_linear
# ---------------------------------------------------------------------------

class TestFillLinear:
    def test_interpolates_single_gap(self):
        records = [{"v": 0.0}, {"v": None}, {"v": 2.0}]
        out = fill_linear(records, "v")
        assert out[1]["v"] == pytest.approx(1.0)

    def test_interpolates_multi_gap(self):
        records = [{"v": 0.0}, {"v": None}, {"v": None}, {"v": 3.0}]
        out = fill_linear(records, "v")
        assert out[1]["v"] == pytest.approx(1.0)
        assert out[2]["v"] == pytest.approx(2.0)

    def test_leading_gap_untouched(self):
        records = [{"v": None}, {"v": 5.0}]
        out = fill_linear(records, "v")
        assert out[0]["v"] is None

    def test_trailing_gap_untouched(self):
        records = [{"v": 5.0}, {"v": None}]
        out = fill_linear(records, "v")
        assert out[1]["v"] is None

    def test_does_not_mutate_original(self):
        records = [{"v": 0.0}, {"v": None}, {"v": 2.0}]
        fill_linear(records, "v")
        assert records[1]["v"] is None

    def test_empty_input(self):
        assert fill_linear([], "v") == []
