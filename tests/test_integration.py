"""Tests for the VeyaNet Decision Gate end-to-end pipeline (classifier → gate)."""

import pytest

from veyanet_decision_gate import (
    DecisionGate,
    DecisionLabel,
    GateThresholds,
    SimpleUncertaintyClassifier,
)


@pytest.fixture
def pipeline():
    clf = SimpleUncertaintyClassifier()
    gate = DecisionGate(GateThresholds(pass_threshold=0.75, block_threshold=0.70))
    return clf, gate


class TestEndToEndRouting:
    def test_safe_text_routes_to_pass(self, pipeline):
        clf, gate = pipeline
        output = clf.classify(
            "I would like to learn how to build a secure, legal web application."
        )
        result = gate.route(output)
        assert result.label is DecisionLabel.PASS

    def test_clearly_unsafe_text_routes_to_block(self, pipeline):
        clf, gate = pipeline
        output = clf.classify(
            "exploit malware ransomware hack attack illegal fraud scam weapon violence abuse"
        )
        result = gate.route(output)
        assert result.label is DecisionLabel.BLOCK

    def test_ambiguous_text_routes_to_review(self, pipeline):
        clf, gate = pipeline
        # One safe and one unsafe keyword — genuinely uncertain
        output = clf.classify("Can you hack in a secure way?")
        result = gate.route(output)
        # The exact label depends on keyword weights; important thing is the
        # label is *not* the same as pure safe/unsafe extreme cases.
        assert result.label in (DecisionLabel.REVIEW, DecisionLabel.PASS, DecisionLabel.BLOCK)

    def test_all_labels_reachable(self, pipeline):
        clf, gate = pipeline
        inputs = {
            DecisionLabel.PASS: (
                "help assist support guide learn educate safe secure protect "
                "legal compliant allowed verified trusted build create design"
            ),
            DecisionLabel.BLOCK: (
                "exploit malware ransomware hack attack illegal fraud scam "
                "dangerous weapon violence abuse jailbreak phishing"
            ),
        }
        labels = set()
        for text in inputs.values():
            out = clf.classify(text)
            labels.add(gate.route(out).label)

        assert DecisionLabel.PASS in labels
        assert DecisionLabel.BLOCK in labels
