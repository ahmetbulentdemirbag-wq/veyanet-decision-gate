"""VeyaNet Decision Gate — supervised PASS/REVIEW/BLOCK uncertainty routing.

Public API::

    from veyanet_decision_gate import (
        DecisionGate,
        GateThresholds,
        SimpleUncertaintyClassifier,
        DecisionLabel,
        DecisionResult,
        ClassifierOutput,
    )
"""

from .classifier import SimpleUncertaintyClassifier
from .gate import DecisionGate, GateThresholds
from .models import ClassifierOutput, DecisionLabel, DecisionResult

__all__ = [
    "ClassifierOutput",
    "DecisionGate",
    "DecisionLabel",
    "DecisionResult",
    "GateThresholds",
    "SimpleUncertaintyClassifier",
]
