# Development guidelines

Standards and workflow for contributing to the DFT-ML pipeline. For a plain
overview see the top-level `README.md`; for the file layout see
`docs/PROJECT_STRUCTURE.md`.

## Project overview

This project extracts formation energies from CASTEP DFT outputs for the Ti-Al
binary alloy system and trains a Gaussian Process Regression (GPR) surrogate
model to predict formation energies across the full composition range with
uncertainty estimates.

## Tech stack

- **Python**: >= 3.9
- **Package manager**: [uv](https://github.com/astral-sh/uv)
- **Core libraries**: pandas, numpy, scikit-learn, matplotlib, joblib
- **Tooling**: Black (format), Ruff (lint), pytest (test), pre-commit

## Code style

- Formatter: **Black** (line length 88).
- Linter: **Ruff** (see `[tool.ruff]` in `pyproject.toml`).
- Type hints on public functions; Google-style docstrings.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for constants.
- Keep physical units explicit (`energy_ev`, `distance_angstrom`).
- Comments explain *why*, not *what*; cite references for non-obvious science.

## Package layout

The importable package lives under `src/dft_ml_pipeline/`:

- **`config.py`** — pure-element reference energies and default paths.
- **`parsing.py`** — CASTEP parsing + formation-energy calculation (`dft-parse`).
- **`modeling.py`** — GPR training, evaluation, plotting (`dft-train`).

Materials Studio automation scripts live in `scripts/` (see `scripts/README.md`).

## Scientific context

- Software: CASTEP (Materials Studio)
- System: Ti-Al binary alloy
- Target: formation energy per atom (eV/atom)

### Reference energies

Defined in `src/dft_ml_pipeline/config.py`, derived from the pure-element
reference cells in `data/raw/` using the **same** CASTEP settings as the alloys:

```python
MU_TI = -1593.839175  # Ti.castep: -25501.4268 eV / 16 ions
MU_AL = -110.897059   # Al.castep: -3548.70602 eV / 32 ions
```

### Formation energy

```
E_form = (E_total - (n_Ti * MU_TI + n_Al * MU_AL)) / N_total
```

## Development workflow

```bash
uv sync --extra dev     # install everything
make parse              # data/raw -> data/processed/alloy_ml_dataset.csv
make train              # train GPR, save model + predictions + figure
make check              # format + lint + test
```

Run scripts directly for custom options:

```bash
uv run dft-parse --help
uv run dft-train --dataset data/processed/alloy_ml_dataset.csv --n-points 500
```

## Data-processing rules

### CASTEP parsing

1. Use the **last** `Final Enthalpy` value (the fully relaxed geometry).
2. Verify that the composition inferred from the file name matches the cell
   size; skip and warn on mismatch.
3. Skip pure-element reference cells (single element) — they define references,
   not data points.
4. Sort the output by Al fraction for stable, reproducible datasets.

### File naming

CASTEP files must follow `Ti{n}Al{m}.castep` so composition can be inferred
(for example `Ti8Al8.castep` -> 8 Ti + 8 Al atoms).

## Machine learning

- **Model**: Gaussian Process Regression with a Constant × RBF kernel.
- **Why GPR**: non-parametric, interpolates noise-free DFT points, and yields
  calibrated uncertainty — essential for small datasets and active learning.
- **Evaluation**: leave-one-out cross-validation (LOO CV) plus R², MAE, RMSE.
- **Reproducibility**: the model is seeded (`random_state=0`).
- Be cautious extrapolating beyond the training composition range; check the
  95% confidence band.

## Version control

- Track: source (`src/`, `tests/`), config, docs, structure inputs, scripts.
- Do **not** track: raw CASTEP outputs, generated datasets/figures/models
  (see `.gitignore`).
- Commit in focused units with descriptive messages.

## Testing

- Tests live in `tests/` and run with `pytest`.
- The parser is tested against synthetic CASTEP fixtures (`tests/conftest.py`);
  the modeling utilities are tested on a small in-memory dataset.
- CI (`.github/workflows/ci.yml`) runs lint, format check, and tests on
  Python 3.9 / 3.11 / 3.12.
