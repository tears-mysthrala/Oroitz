# Release Checklist

This checklist is for the Phase 6 hardening & release preparation.

- [ ] Run full test suite on all platforms (Linux, macOS, Windows)
- [ ] Run performance benchmarks with canonical images (4 GB+)
- [ ] Confirm package builds (PyInstaller, wheel) for each platform
- [ ] Generate SBOM (CycloneDX)
- [ ] Run dependency vulnerability scan
- [ ] Validate installer and run smoke tests
- [ ] Publish release notes and update ADR list if needed
- [ ] Tag release candidate and open announcement PR
- [ ] Verify telemetry opt-in/out workflow in GUI/TUI
- [ ] Confirm documentation screenshots and guides are up-to-date
