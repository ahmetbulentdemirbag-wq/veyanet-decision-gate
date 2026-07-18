"""Tests for veyanet_decision_gate.classifier (SimpleUncertaintyClassifier)."""

import math

import pytest

from veyanet_decision_gate import ClassifierOutput, SimpleUncertaintyClassifier


@pytest.fixture
def clf():
    return SimpleUncertaintyClassifier()


# ---------------------------------------------------------------------------
# ClassifierOutput validation
# ---------------------------------------------------------------------------


class TestClassifierOutputValidation:
    @pytest.mark.parametrize("field,value", [
        ("safe_score", -0.1),
        ("safe_score", 1.1),
        ("unsafe_score", -0.1),
        ("unsafe_score", 1.1),
        ("uncertainty", -0.1),
        ("uncertainty", 1.1),
    ])
    def test_out_of_range_raises(self, field, value):
        kwargs = dict(safe_score=0.5, unsafe_score=0.5, uncertainty=0.5)
        kwargs[field] = value
        with pytest.raises(ValueError):
            ClassifierOutput(**kwargs)

    def test_valid_boundary_values(self):
        out = ClassifierOutput(safe_score=0.0, unsafe_score=0.0, uncertainty=0.0)
        assert out.safe_score == 0.0

        out = ClassifierOutput(safe_score=1.0, unsafe_score=1.0, uncertainty=1.0)
        assert out.safe_score == 1.0


# ---------------------------------------------------------------------------
# SimpleUncertaintyClassifier.classify
# ---------------------------------------------------------------------------


class TestClassifyScoring:
    def test_returns_classifier_output_instance(self, clf):
        result = clf.classify("hello world")
        assert isinstance(result, ClassifierOutput)

    def test_scores_in_range(self, clf):
        for text in ["", "hello", "attack malware hack"]:
            out = clf.classify(text)
            assert 0.0 <= out.safe_score <= 1.0
            assert 0.0 <= out.unsafe_score <= 1.0
            assert 0.0 <= out.uncertainty <= 1.0

    def test_unsafe_text_has_higher_unsafe_score(self, clf):
        out = clf.classify("I want to harm, attack and exploit malware vulnerabilities.")
        assert out.unsafe_score > out.safe_score

    def test_safe_text_has_higher_safe_score(self, clf):
        out = clf.classify("I want to learn and help build a secure, legal application.")
        assert out.safe_score > out.unsafe_score

    def test_empty_text_returns_equal_scores(self, clf):
        out = clf.classify("")
        assert out.safe_score == pytest.approx(0.5)
        assert out.unsafe_score == pytest.approx(0.5)

    def test_empty_text_has_maximum_uncertainty(self, clf):
        out = clf.classify("")
        # max binary entropy = 1.0 (p = q = 0.5)
        assert out.uncertainty == pytest.approx(1.0)

    def test_no_keyword_match_returns_equal_scores(self, clf):
        out = clf.classify("the quick brown fox jumps over the lazy dog")
        assert out.safe_score == pytest.approx(0.5)
        assert out.unsafe_score == pytest.approx(0.5)

    def test_case_insensitive_matching(self, clf):
        lower = clf.classify("i want to hack")
        upper = clf.classify("I WANT TO HACK")
        assert lower.unsafe_score == pytest.approx(upper.unsafe_score)

    def test_metadata_contains_hits(self, clf):
        out = clf.classify("I want to hack and exploit malware.")
        hits = out.metadata.get("unsafe_hits", {})
        assert "hack" in hits
        assert "exploit" in hits
        assert "malware" in hits

    def test_metadata_safe_hits(self, clf):
        out = clf.classify("Please help me learn to build a secure app.")
        hits = out.metadata.get("safe_hits", {})
        assert len(hits) > 0

    def test_uncertainty_decreases_with_more_signal(self, clf):
        ambiguous = clf.classify("please help")
        strong = clf.classify("help assist support guide learn educate build secure protect")
        # More clearly-safe text should have lower uncertainty
        assert strong.uncertainty <= ambiguous.uncertainty

    def test_scores_sum_to_one_approximately(self, clf):
        texts = [
            "I want to hack and attack",
            "I want to learn and build",
            "the quick brown fox",
        ]
        for text in texts:
            out = clf.classify(text)
            total = out.safe_score + out.unsafe_score
            assert total == pytest.approx(1.0, abs=1e-4), (
                f"Scores for {text!r} sum to {total}, not 1.0"
            )

    def test_high_unsafe_score_for_clearly_bad_text(self, clf):
        out = clf.classify(
            "exploit malware ransomware hack attack illegal fraud scam dangerous weapon violence"
        )
        assert out.unsafe_score > 0.85

    def test_high_safe_score_for_clearly_safe_text(self, clf):
        out = clf.classify(
            "help assist support guide learn educate improve safe secure protect legal "
            "compliant allowed permitted authorised verified trusted"
        )
        assert out.safe_score > 0.85


# ---------------------------------------------------------------------------
# Custom keyword lists
# ---------------------------------------------------------------------------


class TestCustomKeywords:
    def test_custom_unsafe_keyword_detected(self):
        clf = SimpleUncertaintyClassifier(
            unsafe_keywords=[("forbidden_word", 2.0)],
            safe_keywords=[],
        )
        out = clf.classify("This contains forbidden_word")
        assert out.unsafe_score > out.safe_score

    def test_custom_safe_keyword_detected(self):
        clf = SimpleUncertaintyClassifier(
            unsafe_keywords=[],
            safe_keywords=[("approved_word", 2.0)],
        )
        out = clf.classify("This contains approved_word")
        assert out.safe_score > out.unsafe_score

    def test_empty_keyword_lists_return_equal_scores(self):
        clf = SimpleUncertaintyClassifier(unsafe_keywords=[], safe_keywords=[])
        out = clf.classify("attack malware hack")
        assert out.safe_score == pytest.approx(0.5)
        assert out.unsafe_score == pytest.approx(0.5)
