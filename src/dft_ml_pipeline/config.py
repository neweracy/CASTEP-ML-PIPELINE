"""Physical constants and default project paths.

Reference (chemical potential) energies
----------------------------------------
The pure-element reference energies below are the per-atom total energies of
the relaxed pure-element ground states, computed with the *same* CASTEP
settings used for the alloy structures (PBE functional, 420 eV plane-wave
cutoff, `TreatAsMetal = True`). Using consistent settings is essential: the
formation energy is a difference of large DFT total energies, so any mismatch
in functional or cutoff introduces a systematic error.

Provenance (derived from ``data/raw/``):

- **Ti**: ``LBFGS: Final Enthalpy = -2.55014268E+004 eV`` over 16 ions
  => ``-25501.4268 / 16 = -1593.839175 eV/atom``.
- **Al**: ``LBFGS: Final Enthalpy = -3.54870602E+003 eV`` over 32 ions
  => ``-3548.70602 / 32 = -110.897059 eV/atom``.

If you recompute the reference cells with different settings, update these
values (and re-run the parser) so that formation energies stay consistent.
"""

from __future__ import annotations

from pathlib import Path

# --- Pure-element reference energies (eV/atom) ---
MU_TI: float = -1593.839175  # Ti hcp ground state, PBE / 420 eV cutoff
MU_AL: float = -110.897059  # Al fcc ground state, PBE / 420 eV cutoff

# --- Default project paths (relative to the repository root) ---
# Resolve the repository root as three levels up from this file:
#   src/dft_ml_pipeline/config.py -> src/dft_ml_pipeline -> src -> <root>
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR: Path = PROJECT_ROOT / "data" / "processed"
DATASET_PATH: Path = PROCESSED_DATA_DIR / "alloy_ml_dataset.csv"

MODELS_DIR: Path = PROJECT_ROOT / "models"
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"

DEFAULT_MODEL_PATH: Path = MODELS_DIR / "gpr_model.pkl"
DEFAULT_PREDICTIONS_PATH: Path = OUTPUTS_DIR / "predictions.csv"
DEFAULT_FIGURE_PATH: Path = OUTPUTS_DIR / "formation_energy_curve.png"
