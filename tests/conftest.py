"""Shared pytest fixtures for the DFT-ML pipeline test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

# Minimal synthetic CASTEP output snippets containing only the fields the
# parser reads. Energies/ion counts are chosen to be easy to reason about.
CASTEP_TI14AL2 = """\
 +-------------------------------------------------+
                         Total number of ions in cell =   16
 ...
 LBFGS: finished iteration     3 with enthalpy= -1.00000000E+003 eV
 LBFGS: Final Enthalpy     = -2.00000000E+003 eV
"""

CASTEP_TI8AL8 = """\
                         Total number of ions in cell =   16
 LBFGS: Final Enthalpy     = -1.50000000E+003 eV
"""

# Composition token (Ti20Al2 -> 22 atoms) disagrees with the cell size (16).
CASTEP_MISMATCH = """\
                         Total number of ions in cell =   16
 LBFGS: Final Enthalpy     = -1.00000000E+003 eV
"""

# No "Final Enthalpy" line -> represents an incomplete calculation.
CASTEP_INCOMPLETE = """\
                         Total number of ions in cell =   16
 Calculation did not converge.
"""


@pytest.fixture
def castep_dir(tmp_path: Path) -> Path:
    """Create a directory of synthetic .castep files for parser tests."""
    (tmp_path / "Ti14Al2.castep").write_text(CASTEP_TI14AL2, encoding="utf-8")
    (tmp_path / "Ti8Al8.castep").write_text(CASTEP_TI8AL8, encoding="utf-8")
    (tmp_path / "Ti20Al2.castep").write_text(CASTEP_MISMATCH, encoding="utf-8")
    (tmp_path / "Ti1Al0.castep").write_text(CASTEP_INCOMPLETE, encoding="utf-8")
    # A non-castep file that must be ignored by the directory scan.
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    return tmp_path
