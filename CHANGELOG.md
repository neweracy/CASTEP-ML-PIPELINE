# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Installable `dft_ml_pipeline` package (`src/` layout) with `config`,
  `parsing`, and `modeling` modules.
- Console entry points `dft-parse` and `dft-train`.
- `pytest` test suite with synthetic CASTEP fixtures.
- GitHub Actions CI (lint, format check, tests) on Python 3.9, 3.11, and 3.12.
- Pre-commit configuration (ruff, black, hygiene hooks).
- Project documentation: `README`, `CONTRIBUTING`, `CODE_OF_CONDUCT`,
  `CITATION.cff`, `SECURITY`, and issue/PR templates.
- MIT `LICENSE`.

### Changed
- Refactored the CASTEP parser to match the modeling code quality (docstrings,
  type hints, logging, a `StructureRecord` dataclass, and pure functions).
- Reorganized Materials Studio batch scripts under `scripts/` and DFT input
  structures under `structures/`.
- Rewrote the README and reconciled `docs/` with the package layout.

### Fixed
- Standardized the aluminum reference energy to the verified value
  `-110.897059 eV/atom` (derived from `data/raw/Al.castep`), resolving a
  discrepancy across the documentation.

## [0.1.0] - 2026-09-16

### Added
- Initial DFT-to-ML pipeline: CASTEP parsing, formation-energy calculation, and
  Gaussian Process Regression surrogate model with uncertainty quantification.

[Unreleased]: https://github.com/neweracy/CASTEP-ML-PIPELINE/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/neweracy/CASTEP-ML-PIPELINE/releases/tag/v0.1.0
