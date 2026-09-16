# Contributing

Thanks for your interest in improving the DFT-ML Pipeline. This project welcomes
contributions from both the machine-learning and materials-science communities.

## Development setup

The project uses [uv](https://github.com/astral-sh/uv) for environment and
dependency management.

```bash
# Clone and enter the repository
git clone https://github.com/neweracy/CASTEP-ML-PIPELINE.git
cd CASTEP-ML-PIPELINE

# Install runtime + development dependencies
uv sync --extra dev

# (Optional) install pre-commit hooks
uv run pre-commit install
```

## Workflow

1. Create a feature branch off `main`:
   ```bash
   git checkout -b feature/short-description
   ```
2. Make your change, keeping commits focused and descriptive.
3. Run the quality gate locally before pushing:
   ```bash
   make check   # format + lint
   make test    # run the test suite
   ```
4. Open a pull request describing *what* changed and *why*, plus how you tested it.

## Coding standards

- **Formatting:** [Black](https://black.readthedocs.io/) (line length 88).
- **Linting:** [Ruff](https://docs.astral.sh/ruff/).
- **Types:** add type hints to new functions.
- **Docstrings:** Google-style docstrings for public functions and modules.
- **Units:** keep physical units explicit in names, docstrings, or comments
  (for example `energy_ev`, `distance_angstrom`).

## Scientific contributions

If you add or change DFT data:

- Use **consistent CASTEP settings** (functional, plane-wave cutoff, k-point
  sampling) across alloy and pure-element reference calculations. Formation
  energy is a small difference of large total energies, so inconsistent
  settings introduce systematic error.
- If you recompute the pure-element references, update `MU_TI` / `MU_AL` in
  `src/dft_ml_pipeline/config.py` and document the provenance.
- Follow the `Ti{n}Al{m}.castep` file-naming convention so the parser can infer
  composition automatically.
- Re-run `dft-parse` to regenerate the dataset and `dft-train` to refresh the
  model and figures.

## Reporting issues

Please open a GitHub issue with:

- what you expected to happen,
- what actually happened (including full error output),
- steps to reproduce, and
- your OS and Python version.
