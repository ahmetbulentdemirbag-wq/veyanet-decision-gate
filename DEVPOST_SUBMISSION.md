# Devpost Submission Draft

## Project Title

VeyaNet Decision Gate

## Suggested Track

Work & Productivity

Alternative if the demo is framed mainly as repo/build triage: Developer Tools.

## One-Line Summary

VeyaNet Decision Gate turns operational outputs into supervised `PASS / REVIEW / BLOCK` decisions so uncertain cases are routed to evidence collection and human review instead of autonomous action.

## Short Description

Modern AI and automation systems produce outputs quickly, but not every output should move directly into action. VeyaNet Decision Gate is a lightweight working prototype that receives hospital, factory, or project-state signals and classifies the route as `1 = PASS`, `V = REVIEW`, or `0 = BLOCK`.

The demo keeps VeyaNet as a final result gate. The protected core is not exposed. A deterministic uncertainty formula powers the MVP so the prototype can run immediately in the browser. When uncertainty is high, the system creates a resolution queue, keeps the human review lock active, and records the decision path in an audit ledger.

## What It Does

- Shows three scenarios: Hospital Automation, Factory Line, and Project Rescue.
- Calculates a bounded uncertainty index from evidence, signal agreement, confidence, severity, audit quality, and human impact.
- Displays only the final VeyaNet result: `PASS`, `REVIEW`, or `BLOCK`.
- Routes uncertain outputs to evidence collection and human review.
- Shows a pipeline view with threshold calibration, negative control, audit ledger, revision loop, Q/V time-series, and early warning.
- Includes reference architecture cards for clinical systems, PostgreSQL, GitOps/Kubernetes, agentic loops, and physical operations.

## How It Uses Codex / GPT-5.6

Codex was used to narrow the project scope into a Build Week-sized MVP, implement the browser prototype, prepare the GitHub Pages-ready package, draft the README, and create the YouTube presentation deck and narration script.

Before final submission, add the required `/feedback` Codex Session ID from the session where the main prototype work was completed.

## Public Links To Fill

```text
Live demo:
https://ahmetbulentdemirbag-wq.github.io/veyanet-decision-gate/

Code repository:
https://github.com/ahmetbulentdemirbag-wq/veyanet-decision-gate

YouTube demo:
https://www.youtube.com/watch?v=YOUR_VIDEO_ID

Codex /feedback Session ID:
PASTE_SESSION_ID_HERE
```

## Demo Video Outline

1. State the problem: systems produce outputs, but outputs are not always safe decisions.
2. Show the `1 / V / 0` gate: PASS, REVIEW, BLOCK.
3. Run the browser demo with Hospital, Factory, and Project scenarios.
4. Show how `V = REVIEW` creates evidence tasks and keeps human review locked.
5. Show the integrated pipeline schema.
6. Close with the safety boundary: this is decision support, not autonomous clinical or industrial control.

## Safety Boundary

This is a decision-support and workflow-routing prototype. It is not a medical device, clinical diagnostic system, factory safety controller, or autonomous deployment authority.

## Suggested Tags

AI, Codex, decision support, uncertainty, audit logging, workflow automation, human-in-the-loop, DevOps, healthcare safety, operations
