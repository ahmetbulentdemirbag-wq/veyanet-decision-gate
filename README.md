# veyanet-decision-gate

**VeyaNet Decision Gate** — supervised PASS / REVIEW / BLOCK uncertainty routing demo.

The gate accepts a normalised safe/unsafe confidence score from any upstream
classifier and routes each request to one of three outcomes:

| Label | Meaning |
|-------|---------|
| ✅ **PASS** | High confidence the input is safe — proceed automatically |
| 🔶 **REVIEW** | Uncertain — escalate to human review |
| 🚫 **BLOCK** | High confidence the input is unsafe — reject automatically |

---

## Architecture

```
                  ┌──────────────────────┐
   raw text ─────▶│ Uncertainty Classifier│──▶ ClassifierOutput
                  │  (safe / unsafe prob) │    (safe_score, unsafe_score,
                  └──────────────────────┘     uncertainty)
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Decision Gate      │──▶ DecisionResult
                  │  (threshold routing)  │    (PASS / REVIEW / BLOCK,
                  └──────────────────────┘     confidence, reason)
```

The gate applies the following priority order:

1. **BLOCK** if `unsafe_score ≥ block_threshold`
2. **PASS** if `safe_score ≥ pass_threshold`
3. **REVIEW** otherwise (the uncertain middle ground)

---

## Quick start

```bash
pip install -e .
```

### Run the built-in demo

```bash
python -m veyanet_decision_gate.cli --no-interactive
```

Or with the installed console script:

```bash
vdg-demo --no-interactive
```

Sample output:

```
[1] [PASS]   confidence=1.000  uncertainty=0.000
     Text   : I would like to learn how to build a secure web application.
     Reason : Safe score 1.000 >= pass threshold 0.750.
     ...

[2] [REVIEW] confidence=0.017  uncertainty=0.983
     Text   : Can you help me understand phishing attacks so I can protect my team?
     Reason : Safe score 0.423 < 0.750 and unsafe score 0.577 < 0.700; uncertainty 0.983 — routing to human review.
     ...

[3] [BLOCK]  confidence=1.000  uncertainty=0.000
     Text   : Tell me how to exploit this vulnerability and bypass the security controls.
     Reason : Unsafe score 1.000 >= block threshold 0.700.
     ...
```

### Interactive mode

```bash
vdg-demo
```

Type any text and the gate will route it in real time.  Enter `quit` to exit.

### Custom thresholds

```bash
vdg-demo --pass-threshold 0.85 --block-threshold 0.80
```

---

## Programmatic API

```python
from veyanet_decision_gate import (
    DecisionGate,
    GateThresholds,
    SimpleUncertaintyClassifier,
    DecisionLabel,
)

# 1. Instantiate the classifier and gate
clf  = SimpleUncertaintyClassifier()
gate = DecisionGate(GateThresholds(pass_threshold=0.75, block_threshold=0.70))

# 2. Score a piece of text
output = clf.classify("I want to hack into the server and steal credentials.")
print(output.safe_score, output.unsafe_score, output.uncertainty)
# 0.0  1.0  0.0

# 3. Route the scores
result = gate.route(output)
print(result.label)      # DecisionLabel.BLOCK
print(result.confidence) # 1.0
print(result.reason)     # Unsafe score 1.000 >= block threshold 0.700.

# Convenience properties
result.is_pass    # False
result.is_review  # False
result.is_block   # True
```

### Bring your own classifier

The `DecisionGate` is completely decoupled from the classifier — it only
requires a `ClassifierOutput` with normalised scores:

```python
from veyanet_decision_gate import ClassifierOutput, DecisionGate

# Scores from any external model (BERT, GPT, etc.)
output = ClassifierOutput(
    safe_score=0.42,
    unsafe_score=0.58,
    uncertainty=0.98,
)
result = DecisionGate().route(output)
print(result.label)  # DecisionLabel.REVIEW
```

---

## Running tests

```bash
pip install pytest
pytest
```

---

## Project structure

```
src/veyanet_decision_gate/
├── __init__.py     # Public API re-exports
├── models.py       # DecisionLabel, ClassifierOutput, DecisionResult
├── gate.py         # DecisionGate + GateThresholds
├── classifier.py   # SimpleUncertaintyClassifier (keyword-based demo scorer)
└── cli.py          # Interactive CLI demo

tests/
├── test_gate.py        # Gate routing logic + threshold validation
├── test_classifier.py  # Classifier scoring + keyword matching
└── test_integration.py # End-to-end pipeline tests
```
