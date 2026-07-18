"""Tests for veyanet_decision_gate.gate (DecisionGate / GateThresholds)."""

import pytest

from veyanet_decision_gate import (
    ClassifierOutput,
    DecisionGate,
    DecisionLabel,
    GateThresholds,
)


# ---------------------------------------------------------------------------
# GateThresholds validation
# ---------------------------------------------------------------------------


class TestGateThresholdsValidation:
    def test_defaults_are_valid(self):
        t = GateThresholds()
        assert 0.0 < t.pass_threshold < 1.0
        assert 0.0 < t.block_threshold < 1.0

    @pytest.mark.parametrize("val", [0.0, 1.0, -0.1, 1.5])
    def test_pass_threshold_boundary_raises(self, val):
        with pytest.raises(ValueError):
            GateThresholds(pass_threshold=val)

    @pytest.mark.parametrize("val", [0.0, 1.0, -0.1, 1.5])
    def test_block_threshold_boundary_raises(self, val):
        with pytest.raises(ValueError):
            GateThresholds(block_threshold=val)

    def test_custom_thresholds_accepted(self):
        t = GateThresholds(pass_threshold=0.90, block_threshold=0.85)
        assert t.pass_threshold == pytest.approx(0.90)
        assert t.block_threshold == pytest.approx(0.85)


# ---------------------------------------------------------------------------
# DecisionGate routing
# ---------------------------------------------------------------------------


def _make_output(safe: float, unsafe: float, uncertainty: float = 0.2) -> ClassifierOutput:
    return ClassifierOutput(safe_score=safe, unsafe_score=unsafe, uncertainty=uncertainty)


class TestDecisionGateRouting:
    """Core routing logic tests with the default thresholds (pass=0.75, block=0.70)."""

    def setup_method(self):
        self.gate = DecisionGate()

    # -- PASS ------------------------------------------------------------------

    def test_high_safe_score_gives_pass(self):
        result = self.gate.route(_make_output(safe=0.85, unsafe=0.10))
        assert result.label is DecisionLabel.PASS

    def test_pass_exactly_at_threshold(self):
        result = self.gate.route(_make_output(safe=0.75, unsafe=0.10))
        assert result.label is DecisionLabel.PASS

    def test_pass_confidence_equals_safe_score(self):
        output = _make_output(safe=0.90, unsafe=0.05)
        result = self.gate.route(output)
        assert result.confidence == pytest.approx(output.safe_score)

    def test_pass_is_pass_property(self):
        result = self.gate.route(_make_output(safe=0.80, unsafe=0.10))
        assert result.is_pass
        assert not result.is_review
        assert not result.is_block

    # -- BLOCK -----------------------------------------------------------------

    def test_high_unsafe_score_gives_block(self):
        result = self.gate.route(_make_output(safe=0.10, unsafe=0.80))
        assert result.label is DecisionLabel.BLOCK

    def test_block_exactly_at_threshold(self):
        result = self.gate.route(_make_output(safe=0.20, unsafe=0.70))
        assert result.label is DecisionLabel.BLOCK

    def test_block_takes_priority_over_pass(self):
        # Both scores above their respective thresholds: BLOCK wins.
        result = self.gate.route(_make_output(safe=0.80, unsafe=0.75))
        assert result.label is DecisionLabel.BLOCK

    def test_block_confidence_equals_unsafe_score(self):
        output = _make_output(safe=0.15, unsafe=0.85)
        result = self.gate.route(output)
        assert result.confidence == pytest.approx(output.unsafe_score)

    def test_block_is_block_property(self):
        result = self.gate.route(_make_output(safe=0.10, unsafe=0.80))
        assert result.is_block
        assert not result.is_pass
        assert not result.is_review

    # -- REVIEW ----------------------------------------------------------------

    def test_uncertain_scores_give_review(self):
        result = self.gate.route(_make_output(safe=0.50, unsafe=0.40, uncertainty=0.90))
        assert result.label is DecisionLabel.REVIEW

    def test_review_when_safe_just_below_threshold(self):
        result = self.gate.route(_make_output(safe=0.74, unsafe=0.30))
        assert result.label is DecisionLabel.REVIEW

    def test_review_when_unsafe_just_below_threshold(self):
        result = self.gate.route(_make_output(safe=0.40, unsafe=0.69))
        assert result.label is DecisionLabel.REVIEW

    def test_review_confidence_is_one_minus_uncertainty(self):
        output = _make_output(safe=0.50, unsafe=0.40, uncertainty=0.70)
        result = self.gate.route(output)
        assert result.label is DecisionLabel.REVIEW
        assert result.confidence == pytest.approx(1.0 - output.uncertainty)

    def test_review_is_review_property(self):
        result = self.gate.route(_make_output(safe=0.50, unsafe=0.50, uncertainty=1.0))
        assert result.is_review
        assert not result.is_pass
        assert not result.is_block

    # -- Reason strings --------------------------------------------------------

    def test_pass_reason_mentions_threshold(self):
        result = self.gate.route(_make_output(safe=0.90, unsafe=0.05))
        assert "0.750" in result.reason or "pass" in result.reason.lower()

    def test_block_reason_mentions_threshold(self):
        result = self.gate.route(_make_output(safe=0.05, unsafe=0.90))
        assert "0.700" in result.reason or "block" in result.reason.lower()

    def test_review_reason_mentions_uncertainty(self):
        output = _make_output(safe=0.50, unsafe=0.40, uncertainty=0.99)
        result = self.gate.route(output)
        assert "uncertainty" in result.reason.lower() or "review" in result.reason.lower()

    # -- classifier_output is preserved ----------------------------------------

    def test_classifier_output_preserved_in_result(self):
        output = _make_output(safe=0.85, unsafe=0.10)
        result = self.gate.route(output)
        assert result.classifier_output is output


# ---------------------------------------------------------------------------
# Custom thresholds
# ---------------------------------------------------------------------------


class TestCustomThresholds:
    def test_strict_gate_downgrades_pass_to_review(self):
        gate = DecisionGate(GateThresholds(pass_threshold=0.95, block_threshold=0.90))
        # Score that would PASS with defaults
        result = gate.route(_make_output(safe=0.80, unsafe=0.05))
        assert result.label is DecisionLabel.REVIEW

    def test_lenient_gate_upgrades_to_pass(self):
        gate = DecisionGate(GateThresholds(pass_threshold=0.50, block_threshold=0.80))
        result = gate.route(_make_output(safe=0.55, unsafe=0.20))
        assert result.label is DecisionLabel.PASS

    def test_tight_block_threshold_blocks_moderate_unsafe(self):
        gate = DecisionGate(GateThresholds(pass_threshold=0.80, block_threshold=0.40))
        result = gate.route(_make_output(safe=0.30, unsafe=0.45))
        assert result.label is DecisionLabel.BLOCK
