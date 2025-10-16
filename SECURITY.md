# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x (pre-release) | Yes – security fixes will land on the default branch and upcoming tags. |
| Future stable releases | To be defined alongside the first stable release. |

## Reporting a Vulnerability

Please report potential security issues privately so we can investigate and release a fix before public disclosure.

1. Prefer opening a private advisory at <https://github.com/tears-mysthrala/Oroitz/security/advisories/new>.
2. If GitHub advisories are unavailable, email the maintainers at `tearsmysthrala@gmail.com` with the subject line `Oroitz Security Report`.
3. Include as much detail as possible (steps to reproduce, affected components, impact, suggested mitigations).

Avoid filing public GitHub issues for security problems.

## Disclosure Process

- We aim to acknowledge new reports within three business days.
- We will coordinate on remediation, provide a target fix timeline, and request a CVE if appropriate.
- Once a fix is available, we will publish release notes and credit reporters who opt in to recognition.

## Scope

Security bugs in the following areas fall under this policy:

- Core engine orchestration, adapters, and bindings under the `volwrap` namespace.
- GUI and TUI applications, including their packaging scripts.
- CLI utilities and workflow orchestration logic.

Dependencies managed by third parties (such as Volatility 3) are out of direct scope, but we will help route findings when possible.

## Hardening Guidance

- Keep your environment patched and updated before running memory forensics workloads.
- Validate provenance for memory captures, symbol files, and plugins before ingesting them.
- Disable telemetry and analytics features if regulations require fully offline execution.
