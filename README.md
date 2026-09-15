# DFT-ML Pipeline for Ti-Al Alloys

A Python pipeline for processing CASTEP DFT calculations and preparing machine learning datasets to predict formation energies in Ti-Al binary alloy systems.

## Overview

This project automates the extraction of formation energy data from CASTEP (Materials Studio) output files and prepares clean datasets for machine learning models.

### What It Does
1. Parses `.castep` files from DFT calculations
2. Extracts total energies and atomic compositions
3. Calculates formation energies per atom
4. Generates ML-ready CSV datasets

## Quick Start

### Prerequisites
- Python ≥3.9
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install dependencies
uv sync

# Or with dev tools (Jupyter, pytest, etc.)
uv sync --extra dev
```

### Usage

```bash
# Parse CASTEP files and generate dataset
uv run python parse_castep.py
```

This will:
- Read all `.castep` files from `./ML_Data/`
- Extract energies and compositions
- Calculate formation energies
- Save results to `alloy_ml_dataset.csv`

## Project Structure

```
.
├── parse_castep.py           # Main CASTEP parser
├── BatchRun.py              # Materials Studio batch processing
├── ML_Data/                 # CASTEP output files
│   ├── Ti15Al1.castep
│   ├── Ti14Al2.castep
│   └── ...
├── STRUCTURES/              # DFT input structures
├── Al_BASE_STRUCTURE/       # Pure Al reference
├── Ti_BASE_STRUCTURE/       # Pure Ti reference
├── alloy_ml_dataset.csv    # Generated dataset (git ignored)
├── pyproject.toml          # Python project config
└── CLAUDE.md               # Development guidelines
```

## Scientific Background

### Formation Energy

The formation energy quantifies the thermodynamic stability of an alloy relative to its pure constituents:

```
E_form = (E_total - Σ n_i μ_i) / N_total
```

Where:
- `E_total`: Total DFT energy of the alloy
- `n_i`: Number of atoms of element i
- `μ_i`: Chemical potential (energy per atom of pure element i)
- `N_total`: Total number of atoms

### Reference Energies (eV/atom)
- **Ti**: -1593.839175 eV/atom
- **Al**: -110.830296 eV/atom

These are computed from DFT calculations of pure element ground states.

## Dataset Format

The generated CSV contains:

| Column | Description |
|--------|-------------|
| `Structure` | Structure identifier (e.g., Ti12Al4) |
| `Total_Atoms` | Total number of atoms in cell |
| `n_Ti` | Number of Ti atoms |
| `n_Al` | Number of Al atoms |
| `Atomic_Fraction_Al` | Al concentration (0-1) |
| `Total_Energy_eV` | DFT total energy (eV) |
| `Formation_Energy_eV_per_atom` | Formation energy (eV/atom) |

## Development

### Code Formatting

```bash
# Auto-format code
uv run black .

# Lint code
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add dev dependency
uv add --dev package-name
```

### File Naming Convention

CASTEP files must follow this pattern for automatic parsing:
```
Ti{n}Al{m}.castep
```

Examples:
- `Ti15Al1.castep` → 15 Ti atoms, 1 Al atom
- `Ti8Al8.castep` → 8 Ti atoms, 8 Al atoms

## Next Steps

### Machine Learning Pipeline
- [ ] Feature engineering (descriptors beyond composition)
- [ ] Train regression models (RF, XGBoost, NN)
- [ ] Cross-validation and error analysis
- [ ] Hyperparameter optimization
- [ ] Convex hull visualization
- [ ] Uncertainty quantification

### Data Expansion
- [ ] More compositions across Ti-Al phase space
- [ ] Different crystal structures (HCP, BCC, FCC)
- [ ] Temperature-dependent properties
- [ ] Integration with phonon calculations

## Troubleshooting

### Parsing Issues

**Error: Composition mismatch**
```
Warning: Ti14Al2.castep composition (14+2) does not match N (16).
```
- **Cause**: Filename doesn't match actual structure
- **Fix**: Rename file to match composition or check DFT input

**Error: No energy found**
```
None values for final_energy
```
- **Cause**: CASTEP calculation incomplete or failed
- **Fix**: Check `.castep` file for "LBFGS: Final Enthalpy" line

## Citation

If you use this code, please cite:
```bibtex
@software{dft_ml_pipeline,
  title={DFT-ML Pipeline for Ti-Al Alloys},
  author={Your Name},
  year={2026}
}
```

## License

[Your chosen license]

## Contact

[Your contact information]
