"""Tests for the CASTEP parser and formation-energy calculation."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from dft_ml_pipeline import config
from dft_ml_pipeline.parsing import (
    DATASET_COLUMNS,
    build_dataset,
    extract_castep_fields,
    formation_energy_per_atom,
    parse_castep_directory,
    parse_composition_from_name,
)


class TestParseComposition:
    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("Ti14Al2.castep", (14, 2)),
            ("Ti8Al8.castep", (8, 8)),
            ("Ti15Al1.castep", (15, 1)),
            ("Ti16.castep", (16, 0)),
            ("Al32.castep", (0, 32)),
        ],
    )
    def test_parses_expected_counts(self, filename, expected):
        assert parse_composition_from_name(filename) == expected


class TestExtractFields:
    def test_extracts_last_enthalpy_and_ions(self):
        content = (
            "Total number of ions in cell =   16\n"
            "LBFGS: Final Enthalpy     = -1.00000000E+003 eV\n"
            "LBFGS: Final Enthalpy     = -2.00000000E+003 eV\n"
        )
        energy, atoms = extract_castep_fields(content)
        # The final (fully relaxed) enthalpy must be selected.
        assert energy == pytest.approx(-2000.0)
        assert atoms == 16

    def test_missing_fields_return_none(self):
        energy, atoms = extract_castep_fields("nothing useful here")
        assert energy is None
        assert atoms is None


class TestFormationEnergy:
    def test_pure_reference_gives_zero(self):
        # A cell made purely of reference atoms has zero formation energy.
        total = 16 * config.MU_TI
        assert formation_energy_per_atom(total, 16, 0) == pytest.approx(0.0, abs=1e-9)

    def test_known_value(self):
        e = formation_energy_per_atom(-100.0, 1, 1, mu_ti=-40.0, mu_al=-50.0)
        # (-100 - (-40 - 50)) / 2 = (-100 + 90) / 2 = -5.0
        assert e == pytest.approx(-5.0)

    def test_empty_cell_raises(self):
        with pytest.raises(ValueError):
            formation_energy_per_atom(-1.0, 0, 0)


class TestParseDirectory:
    def test_skips_mismatch_and_incomplete(self, castep_dir: Path):
        df = parse_castep_directory(castep_dir)
        # Ti14Al2 and Ti8Al8 are valid; Ti20Al2 mismatches; Ti1Al0 is pure/incomplete.
        # Rows are sorted by Al fraction, so Ti14Al2 (0.125) precedes Ti8Al8 (0.5).
        assert list(df["Structure"]) == ["Ti14Al2", "Ti8Al8"]

    def test_sorted_by_al_fraction(self, castep_dir: Path):
        df = parse_castep_directory(castep_dir)
        fractions = df["Atomic_Fraction_Al"].tolist()
        assert fractions == sorted(fractions)

    def test_columns_match_schema(self, castep_dir: Path):
        df = parse_castep_directory(castep_dir)
        assert list(df.columns) == DATASET_COLUMNS

    def test_missing_directory_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            parse_castep_directory(tmp_path / "does_not_exist")

    def test_build_dataset_writes_csv(self, castep_dir: Path, tmp_path: Path):
        out = tmp_path / "processed" / "dataset.csv"
        df = build_dataset(castep_dir, out)
        assert out.exists()
        assert len(df) == 2


class TestRealDataset:
    """Smoke test against the checked-in reference dataset, if present."""

    def test_reference_dataset_is_physical(self):
        import pandas as pd

        if not config.DATASET_PATH.exists():
            pytest.skip("Reference dataset not present.")
        df = pd.read_csv(config.DATASET_PATH)
        # Every parsed alloy should be thermodynamically stable (negative E_form).
        assert (df["Formation_Energy_eV_per_atom"] < 0).all()
        # Atom counts must be self-consistent.
        assert (df["n_Ti"] + df["n_Al"] == df["Total_Atoms"]).all()
        assert not math.isnan(df["Formation_Energy_eV_per_atom"].sum())
