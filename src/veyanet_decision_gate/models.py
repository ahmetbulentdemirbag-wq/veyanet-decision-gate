"""Data models for VeyaNet Decision Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class DecisionLabel(str, Enum):
    """Routing decision produced by the gate."""

    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass
class ClassifierOutput:
    """Raw output from an uncertainty classifier.

    Attributes:
        safe_score: Probability that the input is safe (0–1).
        unsafe_score: Probability that the input is unsafe (0–1).
        uncertainty: Entropy-derived uncertainty in [0, 1].
            Higher values mean the classifier is less confident.
        metadata: Optional key/value bag for extra signal (e.g. matched keywords).
    """

    safe_score: float
    unsafe_score: float
    uncertainty: float
    metadata: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, val in [
            ("safe_score", self.safe_score),
            ("unsafe_score", self.unsafe_score),
            ("uncertainty", self.uncertainty),
        ]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {val!r}")


@dataclass
class DecisionResult:
    """Final routing decision returned by :class:`DecisionGate`.

    Attributes:
        label: One of PASS, REVIEW, or BLOCK.
        confidence: Confidence in the chosen label (0–1).
        classifier_output: The underlying classifier scores.
        reason: Human-readable explanation of the decision.
    """

    label: DecisionLabel
    confidence: float
    classifier_output: ClassifierOutput
    reason: str

    @property
    def is_pass(self) -> bool:
        return self.label is DecisionLabel.PASS

    @property
    def is_review(self) -> bool:
        return self.label is DecisionLabel.REVIEW

    @property
    def is_block(self) -> bool:
        return self.label is DecisionLabel.BLOCK
