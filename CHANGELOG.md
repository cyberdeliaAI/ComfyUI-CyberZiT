# Changelog

All notable changes to ComfyUI-CyberZiT are documented in this file.

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

[0.1.1]: https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/releases/tag/v0.1.0
