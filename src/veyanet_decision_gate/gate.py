"""Core decision gate: routes classifier output to PASS / REVIEW / BLOCK."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ClassifierOutput, DecisionLabel, DecisionResult


@dataclass
class GateThresholds:
    """Threshold configuration for the decision gate.

    The gate applies the following priority order:

    1. **BLOCK**: ``unsafe_score >= block_threshold``
    2. **PASS**: ``safe_score >= pass_threshold``
    3. **REVIEW**: everything else (the uncertain middle ground)

    Args:
        pass_threshold: Minimum *safe* score required to grant PASS.
            Defaults to ``0.75``.
        block_threshold: Minimum *unsafe* score required to enforce BLOCK.
            Defaults to ``0.70``.
    """

    pass_threshold: float = 0.75
    block_threshold: float = 0.70

    def __post_init__(self) -> None:
        for name, val in [
            ("pass_threshold", self.pass_threshold),
            ("block_threshold", self.block_threshold),
        ]:
            if not (0.0 < val < 1.0):
                raise ValueError(f"{name} must be in (0, 1), got {val!r}")


class DecisionGate:
    """Supervised PASS / REVIEW / BLOCK uncertainty routing gate.

    The gate is intentionally decoupled from the classifier so that any
    implementation of a scorer can be plugged in — the gate only cares about
    the normalised safe/unsafe probabilities and the uncertainty estimate
    bundled in a :class:`~veyanet_decision_gate.models.ClassifierOutput`.

    Example::

        from veyanet_decision_gate import DecisionGate, GateThresholds

        gate = DecisionGate(GateThresholds(pass_threshold=0.80, block_threshold=0.75))
        output = ClassifierOutput(safe_score=0.90, unsafe_score=0.10, uncertainty=0.08)
        result = gate.route(output)
        print(result.label)   # DecisionLabel.PASS

    Args:
        thresholds: Optional :class:`GateThresholds` instance.  If *None* the
            defaults (pass=0.75, block=0.70) are used.
    """

    def __init__(self, thresholds: GateThresholds | None = None) -> None:
        self.thresholds = thresholds or GateThresholds()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, output: ClassifierOutput) -> DecisionResult:
        """Route *output* to a :class:`~veyanet_decision_gate.models.DecisionResult`.

        Decision priority:

        * **BLOCK** takes precedence — a high unsafe score overrides a
          moderate safe score.
        * **PASS** is granted when the safe score clears the pass threshold
          *and* the unsafe score has not triggered BLOCK.
        * **REVIEW** is the fallback for all uncertain cases.

        Args:
            output: Scores produced by the upstream classifier.

        Returns:
            A :class:`~veyanet_decision_gate.models.DecisionResult` with the
            chosen label, a confidence value, and a human-readable reason.
        """
        t = self.thresholds

        if output.unsafe_score >= t.block_threshold:
            return DecisionResult(
                label=DecisionLabel.BLOCK,
                confidence=output.unsafe_score,
                classifier_output=output,
                reason=(
                    f"Unsafe score {output.unsafe_score:.3f} >= "
                    f"block threshold {t.block_threshold:.3f}."
                ),
            )

        if output.safe_score >= t.pass_threshold:
            return DecisionResult(
                label=DecisionLabel.PASS,
                confidence=output.safe_score,
                classifier_output=output,
                reason=(
                    f"Safe score {output.safe_score:.3f} >= "
                    f"pass threshold {t.pass_threshold:.3f}."
                ),
            )

        # Uncertain region → human review required
        confidence = 1.0 - output.uncertainty
        return DecisionResult(
            label=DecisionLabel.REVIEW,
            confidence=confidence,
            classifier_output=output,
            reason=(
                f"Safe score {output.safe_score:.3f} < {t.pass_threshold:.3f} "
                f"and unsafe score {output.unsafe_score:.3f} < {t.block_threshold:.3f}; "
                f"uncertainty {output.uncertainty:.3f} — routing to human review."
            ),
        )
