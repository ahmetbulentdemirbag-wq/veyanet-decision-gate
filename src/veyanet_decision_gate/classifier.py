"""Simple keyword-based uncertainty classifier for demo purposes.

The classifier scores text by scanning it for *unsafe* and *safe* indicator
phrases drawn from configurable word lists.  It does **not** require any
external ML libraries — the goal is a transparent, hackable baseline whose
routing behaviour can be understood and tested without a GPU or network
connection.

Scoring formula
---------------
Let ``u`` = number of unsafe keyword hits and ``s`` = number of safe keyword
hits.  A *hit* contributes a configurable *weight* (default 1.0 per keyword).

    raw_unsafe = sum of weights for matched unsafe keywords
    raw_safe   = sum of weights for matched safe keywords

These are converted to probabilities via a soft-max style normalisation:

    total       = raw_unsafe + raw_safe + epsilon   (epsilon avoids div/0)
    unsafe_prob = raw_unsafe / total
    safe_prob   = raw_safe   / total

When *neither* safe nor unsafe keywords are found the classifier returns equal
probabilities (0.5 / 0.5) and maximum uncertainty.

Uncertainty is computed as the binary entropy of the safe/unsafe distribution:

    H = -(p * log2(p) + q * log2(q))   where p=safe_prob, q=unsafe_prob
    uncertainty = H                     (normalised to [0, 1] since H ≤ 1)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .models import ClassifierOutput


# ---------------------------------------------------------------------------
# Default keyword lists
# ---------------------------------------------------------------------------

_DEFAULT_UNSAFE_KEYWORDS: List[Tuple[str, float]] = [
    # Harmful intent
    ("harm", 1.5),
    ("attack", 1.5),
    ("exploit", 1.5),
    ("malicious", 1.5),
    ("malware", 1.5),
    ("ransomware", 1.5),
    ("phishing", 1.5),
    ("fraud", 1.3),
    ("scam", 1.3),
    ("illegal", 1.2),
    ("banned", 1.0),
    ("prohibited", 1.0),
    ("dangerous", 1.0),
    ("threat", 1.0),
    ("weapon", 1.2),
    ("violence", 1.2),
    ("abuse", 1.2),
    ("inject", 1.0),
    ("bypass", 0.8),
    ("override", 0.6),
    ("jailbreak", 1.5),
    ("hack", 1.2),
    ("crack", 0.8),
    ("steal", 1.2),
    ("corrupt", 1.0),
    ("destroy", 1.0),
    ("poison", 1.0),
]

_DEFAULT_SAFE_KEYWORDS: List[Tuple[str, float]] = [
    ("help", 1.0),
    ("assist", 1.0),
    ("support", 1.0),
    ("guide", 1.0),
    ("learn", 1.0),
    ("educate", 1.0),
    ("improve", 1.0),
    ("safe", 1.5),
    ("secure", 1.2),
    ("protect", 1.2),
    ("legal", 1.2),
    ("compliant", 1.2),
    ("allowed", 1.0),
    ("permitted", 1.0),
    ("authorised", 1.0),
    ("authorized", 1.0),
    ("verified", 1.0),
    ("trusted", 1.0),
    ("friendly", 0.8),
    ("collaborate", 0.8),
    ("share", 0.6),
    ("create", 0.6),
    ("build", 0.6),
    ("design", 0.6),
]

_EPSILON = 1e-9


def _binary_entropy(p: float, q: float) -> float:
    """Compute binary entropy H(p, q) normalised to [0, 1]."""
    # H_max for a binary distribution is 1 bit (p=q=0.5)
    entropy = 0.0
    for x in (p, q):
        if x > 0.0:
            entropy -= x * math.log2(x)
    return min(entropy, 1.0)  # cap at 1 to avoid floating-point overshoot


@dataclass
class SimpleUncertaintyClassifier:
    """Keyword-based safe/unsafe scorer with uncertainty estimation.

    Args:
        unsafe_keywords: List of ``(keyword, weight)`` tuples that signal
            unsafe content.  Matching is case-insensitive substring search.
        safe_keywords: List of ``(keyword, weight)`` tuples that signal safe
            content.

    Example::

        from veyanet_decision_gate import SimpleUncertaintyClassifier

        clf = SimpleUncertaintyClassifier()
        out = clf.classify("I want to learn how to build a website safely.")
        print(out.safe_score, out.unsafe_score)
    """

    unsafe_keywords: List[Tuple[str, float]] = field(
        default_factory=lambda: list(_DEFAULT_UNSAFE_KEYWORDS)
    )
    safe_keywords: List[Tuple[str, float]] = field(
        default_factory=lambda: list(_DEFAULT_SAFE_KEYWORDS)
    )

    def classify(self, text: str) -> ClassifierOutput:
        """Classify *text* and return a :class:`~veyanet_decision_gate.models.ClassifierOutput`.

        Args:
            text: Raw input text to score.

        Returns:
            :class:`~veyanet_decision_gate.models.ClassifierOutput` with
            normalised safe/unsafe probabilities and an uncertainty score.
        """
        lowered = text.lower()

        raw_unsafe, unsafe_hits = self._score(lowered, self.unsafe_keywords)
        raw_safe, safe_hits = self._score(lowered, self.safe_keywords)

        total = raw_unsafe + raw_safe + _EPSILON
        unsafe_prob = raw_unsafe / total
        safe_prob = raw_safe / total

        # When no keywords match at all, treat as fully uncertain
        if raw_unsafe == 0.0 and raw_safe == 0.0:
            unsafe_prob = 0.5
            safe_prob = 0.5

        uncertainty = _binary_entropy(safe_prob, unsafe_prob)

        return ClassifierOutput(
            safe_score=round(safe_prob, 6),
            unsafe_score=round(unsafe_prob, 6),
            uncertainty=round(uncertainty, 6),
            metadata={
                "unsafe_hits": unsafe_hits,
                "safe_hits": safe_hits,
                "raw_unsafe": round(raw_unsafe, 4),
                "raw_safe": round(raw_safe, 4),
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score(
        lowered_text: str, keyword_weights: List[Tuple[str, float]]
    ) -> Tuple[float, Dict[str, float]]:
        """Return the cumulative weight and a hit map for *keyword_weights*."""
        total_weight = 0.0
        hits: Dict[str, float] = {}
        for keyword, weight in keyword_weights:
            if keyword in lowered_text:
                total_weight += weight
                hits[keyword] = weight
        return total_weight, hits
