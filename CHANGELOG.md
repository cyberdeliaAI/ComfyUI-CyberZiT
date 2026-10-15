# Changelog

All notable changes to ComfyUI-CyberZiT are documented in this file.

## [0.1.2] - 2026-10-15

### Fixed

- Reject unsupported model sampling types in all CyberZiT KSampler entries
  with a clear error. `ModelSamplingDiscreteFlow` and its subclasses remain
  supported.

### Added

- Regression tests for model compatibility, stable preset shifts and
  trajectories, and preservation of the model's shift setting.
- Contributor and security reporting guidance, plus Registry package exclusions.

### Changed

- Clarified model compatibility, fixed preset shifts, the standalone node's
  validation limits, and the relationship with ComfyUI's `simple` scheduler.
- Replaced unsupported calibration and final-jump claims with precise
  descriptions of the existing curves.
- Refreshed Cyberdelia branding and the project icon.

Preset shifts (`1.0`, `1.75`, and `3.0`), scheduler names, and generated sigma
values for supported workflows are unchanged. The standalone SIGMAS node
remains model-independent and cannot perform the KSampler model check.

## [0.1.1] - 2026-09-02

### Fixed

- Restored Python 3.10 compatibility by adding a fallback for `math.exp2`,
  which was introduced in Python 3.11.

### Changed

- Updated GitHub Actions to current Node.js 24-compatible releases.

## [0.1.0] - 2026-09-02

### Added

- CyberZiT Scheduler node for `SamplerCustomAdvanced`.
- `fast`, `balanced`, and `quality` presets.
- Optional detail adjustment on the standalone scheduler node.
- `cyberzit_fast`, `cyberzit`, `cyberzit_balanced`, and
  `cyberzit_quality` entries for the standard KSampler scheduler menu.
- Automated tests for schedule generation and ComfyUI registration.

[0.1.2]: https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/releases/tag/v0.1.2
[0.1.1]: https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/releases/tag/v0.1.0
