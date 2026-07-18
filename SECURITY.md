# Security Policy

## Scope

This repository is a public demonstration package for VeyaNet Decision Gate. It contains no API keys, patient data, private datasets, credentials, backend services, protected VeyaNet core code, or production deployment configuration.

## Supported Use

The public demo may be viewed and evaluated as a browser-based decision-support prototype.

It must not be used as:

- a clinical diagnostic device,
- an autonomous medical decision system,
- a factory safety controller,
- an autonomous deployment authority,
- a replacement for human review,
- or a source of validated operational thresholds.

## Reporting Issues

For Build Week review, report issues through the repository issue tracker or the Devpost submission channel.

Do not post secrets, private patient information, private research material, API keys, credentials, or unpublished protected algorithm details in issues or pull requests.

## Protected Core Boundary

The protected VeyaNet algorithm is intentionally not included in this repository. The public prototype exposes only the final interface pattern:

```text
External output -> Uncertainty Formula -> Evidence Gap Resolver -> VeyaNet Result -> Human Review -> Audit
```

Only the final `1 / V / 0` result interface is demonstrated publicly.
