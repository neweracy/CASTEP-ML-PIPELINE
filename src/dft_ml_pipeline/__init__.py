"""DFT-to-ML pipeline for Ti-Al alloy formation energy prediction.

This package extracts formation energies from CASTEP (Materials Studio) DFT
output files and trains a Gaussian Process Regression surrogate model to
predict formation energies across the full Ti-Al composition range with
calibrated uncertainty estimates.

Subpackages / modules
----------------------
config
    Physical constants (pure-element reference energies) and default paths.
parsing
    CASTEP output parsing and formation-energy calculation.
modeling
    Gaussian Process Regression training, evaluation, and visualization.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
