# VeyaNet Decision Gate

VeyaNet Decision Gate is a small working prototype for OpenAI Build Week. It presents VeyaNet as a final supervised decision gate, not as an exposed internal algorithm.

The demo accepts hospital, factory, or project-state signals and routes the output through an uncertainty pipeline. The visible VeyaNet result is:

- `1 = PASS`: proceed with monitored execution.
- `V = REVIEW`: hold the action, collect missing evidence, and keep human review locked.
- `0 = BLOCK`: stop the action and escalate with an audit record.

## Live Demo

After GitHub Pages is enabled, the public demo URL should be:

```text
https://ahmetbulentdemirbag-wq.github.io/veyanet-decision-gate/
```

## Run Locally

Open `index.html` in a browser.

No build step, server, API key, package install, or backend is required.

## Video Preparation

The YouTube narration draft is included at:

- `presentation/VeyaNet_Decision_Gate_YouTube_Narration.txt`

The visual slide deck and source architecture images were prepared as companion video assets. They are not required for the live browser demo.

## What This Prototype Demonstrates

This project does not attempt to build a full hospital automation system, factory controller, or complete VeyaNet core in the hackathon window. It demonstrates the reusable decision-safety pattern:

1. A source system produces an output.
2. The output is mapped into a shared decision packet.
3. An uncertainty formula calculates a bounded uncertainty index.
4. Evidence gaps and repair actions are generated.
5. VeyaNet returns only the final `1 / V / 0` result.
6. `V` and `0` paths remain under human review.
7. The audit ledger records the decision route.

## Scenario Modes

- **Hospital Automation**: clinical output is routed to PASS, REVIEW, or BLOCK without claiming autonomous diagnosis.
- **Factory Line**: sensor drift and maintenance signals are routed before operational action.
- **Project Rescue**: repo, build, README, and demo readiness are assessed before submission.

## Reference Architecture Concepts

The live demo includes reference architecture cards for:

- Integrated VeyaNet decision pipeline schema
- GitOps / Kubernetes deployment flow
- PostgreSQL client/server data backbone
- Agentic loop workflow
- Physical facility or operational zone mapping

These are context adapters. They do not expose protected VeyaNet core logic.

## Future Algorithm Hook

The current MVP uses a transparent deterministic scoring formula so the demo works immediately. The same interface can later connect to the protected VeyaNet algorithm:

```text
External output -> Uncertainty Formula -> Evidence Gap Resolver -> VeyaNet Result -> Human Review -> Audit
```

Only the final VeyaNet result needs to remain public. The proprietary core can remain behind the gate.

## Safety Boundary

This prototype is a decision-support and workflow-routing demo. It is not a clinical diagnostic device, medical automation system, factory safety controller, or autonomous deployment authority.

## Authorship

ORŞİT MÜHRÜ  
Dr. Ahmet Bülent Demirbağ  
ORCID: 0000-0002-9349-1464  
https://orcid.org/0000-0002-9349-1464
