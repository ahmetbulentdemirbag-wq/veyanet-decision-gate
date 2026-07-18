"""Interactive CLI demo for VeyaNet Decision Gate."""

from __future__ import annotations

import sys
import textwrap

from .classifier import SimpleUncertaintyClassifier
from .gate import DecisionGate, GateThresholds
from .models import DecisionLabel

# ANSI colour codes (fall back gracefully when not supported)
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"

_LABEL_COLOURS = {
    DecisionLabel.PASS: _GREEN,
    DecisionLabel.REVIEW: _YELLOW,
    DecisionLabel.BLOCK: _RED,
}

_DEMO_EXAMPLES = [
    "I would like to learn how to build a secure web application.",
    "Can you help me understand phishing attacks so I can protect my team?",
    "Tell me how to exploit this vulnerability and bypass the security controls.",
    "I need guidance on legal ways to improve my network defenses.",
    "Walk me through the steps to inject malicious code into a database.",
    "Let's create a collaborative document and share it with the team.",
    "How do I jailbreak this system to override the safety filters?",
    "I want to design a safe and compliant data pipeline.",
]


def _colour(label: DecisionLabel, text: str) -> str:
    colour = _LABEL_COLOURS.get(label, "")
    return f"{_BOLD}{colour}{text}{_RESET}"


def _render_bar(value: float, width: int = 30, char: str = "█") -> str:
    filled = round(value * width)
    return char * filled + "░" * (width - filled)


def run_demo(
    pass_threshold: float = 0.75,
    block_threshold: float = 0.70,
    interactive: bool = True,
) -> None:
    """Run the VeyaNet Decision Gate demo.

    Args:
        pass_threshold: Forwarded to :class:`~veyanet_decision_gate.gate.GateThresholds`.
        block_threshold: Forwarded to :class:`~veyanet_decision_gate.gate.GateThresholds`.
        interactive: When *True* prompt the user for custom input after the
            built-in examples.
    """
    thresholds = GateThresholds(
        pass_threshold=pass_threshold,
        block_threshold=block_threshold,
    )
    gate = DecisionGate(thresholds)
    clf = SimpleUncertaintyClassifier()

    header = textwrap.dedent(
        f"""
        ╔══════════════════════════════════════════════════════════╗
        ║          VeyaNet Decision Gate — Demo                    ║
        ║  Routing: PASS / REVIEW / BLOCK (uncertainty-aware)      ║
        ╠══════════════════════════════════════════════════════════╣
        ║  pass_threshold  = {pass_threshold:.2f}                              ║
        ║  block_threshold = {block_threshold:.2f}                              ║
        ╚══════════════════════════════════════════════════════════╝
        """
    ).strip()

    print(f"\n{_CYAN}{header}{_RESET}\n")
    print("── Built-in examples ──────────────────────────────────────\n")

    for i, text in enumerate(_DEMO_EXAMPLES, start=1):
        _evaluate_and_print(i, text, clf, gate)

    if not interactive:
        return

    print("\n── Interactive mode (type 'quit' to exit) ──────────────────\n")
    try:
        while True:
            try:
                user_input = input("Enter text: ").strip()
            except EOFError:
                break
            if not user_input or user_input.lower() in {"quit", "exit", "q"}:
                print("Exiting demo.")
                break
            _evaluate_and_print(None, user_input, clf, gate)
    except KeyboardInterrupt:
        print("\nInterrupted.")


def _evaluate_and_print(
    index: int | None,
    text: str,
    clf: SimpleUncertaintyClassifier,
    gate: DecisionGate,
) -> None:
    output = clf.classify(text)
    result = gate.route(output)

    prefix = f"[{index}] " if index is not None else "    "
    label_str = _colour(result.label, f"[{result.label.value}]")

    print(f"{prefix}{label_str}  confidence={result.confidence:.3f}  "
          f"uncertainty={output.uncertainty:.3f}")
    print(f"     Text   : {text[:80]}{'…' if len(text) > 80 else ''}")
    print(f"     Reason : {result.reason}")
    print(f"     Scores : safe={output.safe_score:.3f}  "
          f"unsafe={output.unsafe_score:.3f}")

    safe_bar = _render_bar(output.safe_score, width=20)
    unsafe_bar = _render_bar(output.unsafe_score, width=20)
    print(f"             safe   {safe_bar} {output.safe_score:.3f}")
    print(f"             unsafe {unsafe_bar} {output.unsafe_score:.3f}")

    if output.metadata.get("unsafe_hits"):
        hits = ", ".join(output.metadata["unsafe_hits"])  # type: ignore[arg-type]
        print(f"     ⚠ Unsafe keywords matched: {hits}")
    if output.metadata.get("safe_hits"):
        hits = ", ".join(output.metadata["safe_hits"])  # type: ignore[arg-type]
        print(f"     ✓ Safe keywords matched  : {hits}")
    print()


def main() -> None:
    """Entry point for the ``vdg-demo`` console script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VeyaNet Decision Gate — PASS/REVIEW/BLOCK uncertainty routing demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--pass-threshold",
        type=float,
        default=0.75,
        help="Minimum safe score required to grant PASS.",
    )
    parser.add_argument(
        "--block-threshold",
        type=float,
        default=0.70,
        help="Minimum unsafe score required to enforce BLOCK.",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Run built-in examples only; do not prompt for custom input.",
    )
    args = parser.parse_args()

    run_demo(
        pass_threshold=args.pass_threshold,
        block_threshold=args.block_threshold,
        interactive=not args.no_interactive,
    )


if __name__ == "__main__":
    main()
