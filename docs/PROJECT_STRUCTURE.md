# Project structure

Overview of the repository layout for the DFT-ML pipeline.

```
.
├── src/dft_ml_pipeline/        # Installable Python package
│   ├── __init__.py             # Package metadata / version
│   ├── config.py               # Reference energies (MU_TI, MU_AL) + paths
│   ├── parsing.py              # CASTEP parsing + formation-energy calc (dft-parse)
│   └── modeling.py             # GPR training / evaluation / plotting (dft-train)
├── tests/                      # pytest suite
│   ├── conftest.py             # Synthetic CASTEP fixtures
│   ├── test_parsing.py
│   └── test_modeling.py
├── scripts/                    # Materials Studio automation (run inside MS)
│   ├── batch_run.py            # MaterialsScript (Python) batch driver
│   ├── batch_run.pl            # MaterialsScript (Perl) batch driver
│   └── README.md
├── data/
│   ├── raw/                    # CASTEP outputs (*.castep, *.geom, ...) — git ignored
│   └── processed/              # Generated ML dataset (CSV) — git ignored
├── models/                     # Trained models (*.pkl) — git ignored
├── outputs/                    # Figures and predictions — git ignored
├── structures/                 # DFT input structures (*.xsd) + base cells
├── docs/                       # Documentation (this folder)
├── pyproject.toml              # Packaging, dependencies, tool config
├── Makefile                    # Task shortcuts
├── .github/workflows/ci.yml    # Lint + test on push / PR
├── .pre-commit-config.yaml     # Local hooks (ruff, black, hygiene)
├── LICENSE                     # MIT
├── CITATION.cff                # How to cite
├── CONTRIBUTING.md
└── README.md
```

## Console entry points

Installing the package (`uv sync`) exposes two commands:

| Command | Module | Inputs | Outputs |
| --- | --- | --- | --- |
| `dft-parse` | `dft_ml_pipeline.parsing` | `data/raw/*.castep` | `data/processed/alloy_ml_dataset.csv` |
| `dft-train` | `dft_ml_pipeline.modeling` | `data/processed/alloy_ml_dataset.csv` | `outputs/formation_energy_curve.png`, `models/gpr_model.pkl`, `outputs/predictions.csv` |

Both accept `--help` for full options.

## Data flow

```
Materials Studio (scripts/) ──▶ data/raw/*.castep
                                     │  dft-parse
                                     ▼
                    data/processed/alloy_ml_dataset.csv
                                     │  dft-train
                                     ▼
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                             ▼
outputs/formation_energy_curve.png  models/gpr_model.pkl  outputs/predictions.csv
```

## Dataset schema (`alloy_ml_dataset.csv`)

| Column | Description |
| --- | --- |
| `Structure` | Structure identifier (e.g. `Ti12Al4`) |
| `Total_Atoms` | Number of atoms in the cell |
| `n_Ti`, `n_Al` | Atom counts per element |
| `Atomic_Fraction_Al` | Al mole fraction in `[0, 1]` |
| `Total_Energy_eV` | DFT total energy (final relaxed enthalpy) |
| `Formation_Energy_eV_per_atom` | Target property for ML |

## Predictions schema (`predictions.csv`)

| Column | Description |
| --- | --- |
| `Atomic_Fraction_Al` | Composition point |
| `Predicted_Formation_Energy_eV_per_atom` | GPR mean prediction |
| `Uncertainty_eV_per_atom` | Predictive standard deviation (σ) |
| `Lower_95CI`, `Upper_95CI` | 95% confidence bounds (±1.96σ) |
