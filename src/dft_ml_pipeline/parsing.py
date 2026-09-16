"""Parse CASTEP output files and compute Ti-Al formation energies.

The parser scans a directory for ``*.castep`` files, extracts the fully
relaxed total energy and the number of ions in the cell, infers the
composition from the file name (``Ti{n}Al{m}.castep``), and computes the
formation energy per atom relative to the pure-element references defined in
:mod:`dft_ml_pipeline.config`.

Formation energy
----------------
.. math::

    E_\\mathrm{form} = \\frac{E_\\mathrm{total}
        - (n_\\mathrm{Ti}\\,\\mu_\\mathrm{Ti} + n_\\mathrm{Al}\\,\\mu_\\mathrm{Al})}
        {N_\\mathrm{total}}

where :math:`\\mu_i` are the per-atom reference energies and
:math:`N_\\mathrm{total} = n_\\mathrm{Ti} + n_\\mathrm{Al}`.
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from . import config

logger = logging.getLogger(__name__)

# --- Regular expressions for CASTEP output fields ---
# Matches e.g. "LBFGS: Final Enthalpy     = -2.55014268E+004 eV"
_ENERGY_PATTERN = re.compile(r"LBFGS:\s+Final Enthalpy\s+=\s+([-.\dE+]+)\s+eV")
# Matches e.g. "Total number of ions in cell =   16"
_TOTAL_ATOMS_PATTERN = re.compile(r"Total number of ions in cell\s*=\s*(\d+)")
# Composition tokens embedded in the file name, e.g. "Ti14Al2"
_TI_PATTERN = re.compile(r"Ti(\d+)")
_AL_PATTERN = re.compile(r"Al(\d+)")

# Column order for the exported dataset (kept stable for downstream tooling).
DATASET_COLUMNS = [
    "Structure",
    "Total_Atoms",
    "n_Ti",
    "n_Al",
    "Atomic_Fraction_Al",
    "Total_Energy_eV",
    "Formation_Energy_eV_per_atom",
]


@dataclass(frozen=True)
class StructureRecord:
    """A single parsed CASTEP structure and its derived quantities."""

    Structure: str
    Total_Atoms: int
    n_Ti: int
    n_Al: int
    Atomic_Fraction_Al: float
    Total_Energy_eV: float
    Formation_Energy_eV_per_atom: float


def parse_composition_from_name(filename: str) -> tuple[int, int]:
    """Infer the Ti and Al atom counts from a CASTEP file name.

    Args:
        filename: File name such as ``"Ti14Al2.castep"``.

    Returns:
        Tuple ``(n_ti, n_al)``. A missing element token is treated as zero.
    """
    ti_match = _TI_PATTERN.search(filename)
    al_match = _AL_PATTERN.search(filename)
    n_ti = int(ti_match.group(1)) if ti_match else 0
    n_al = int(al_match.group(1)) if al_match else 0
    return n_ti, n_al


def extract_castep_fields(content: str) -> tuple[float | None, int | None]:
    """Extract the final total energy and ion count from CASTEP file content.

    The *last* ``Final Enthalpy`` value is used because it corresponds to the
    fully relaxed geometry at the end of the optimization.

    Args:
        content: Full text of a ``.castep`` file.

    Returns:
        Tuple ``(final_energy_eV, total_atoms)``; either element may be
        ``None`` if the corresponding field was not found.
    """
    energy_matches = _ENERGY_PATTERN.findall(content)
    final_energy = float(energy_matches[-1]) if energy_matches else None

    atoms_match = _TOTAL_ATOMS_PATTERN.search(content)
    total_atoms = int(atoms_match.group(1)) if atoms_match else None

    return final_energy, total_atoms


def formation_energy_per_atom(
    total_energy_ev: float,
    n_ti: int,
    n_al: int,
    mu_ti: float = config.MU_TI,
    mu_al: float = config.MU_AL,
) -> float:
    """Compute the formation energy per atom (eV/atom).

    Args:
        total_energy_ev: DFT total energy of the alloy cell (eV).
        n_ti: Number of Ti atoms.
        n_al: Number of Al atoms.
        mu_ti: Ti reference energy (eV/atom).
        mu_al: Al reference energy (eV/atom).

    Returns:
        Formation energy per atom in eV/atom.

    Raises:
        ValueError: If the cell contains no atoms.
    """
    n_total = n_ti + n_al
    if n_total == 0:
        raise ValueError("Cannot compute formation energy for an empty cell.")
    return (total_energy_ev - (n_ti * mu_ti + n_al * mu_al)) / n_total


def parse_castep_file(filepath: Path) -> StructureRecord | None:
    """Parse a single ``.castep`` file into a :class:`StructureRecord`.

    Args:
        filepath: Path to the ``.castep`` file.

    Returns:
        A :class:`StructureRecord`, or ``None`` if the file is incomplete or
        the composition inferred from the name does not match the cell size.
    """
    filepath = Path(filepath)
    n_ti, n_al = parse_composition_from_name(filepath.name)

    content = filepath.read_text(encoding="utf-8", errors="ignore")
    final_energy, total_atoms = extract_castep_fields(content)

    if final_energy is None or total_atoms is None:
        logger.warning(
            "%s: missing energy or ion count (calculation may be incomplete).",
            filepath.name,
        )
        return None

    if (n_ti + n_al) != total_atoms:
        logger.warning(
            "%s: composition (%d+%d) does not match cell size (%d); skipping.",
            filepath.name,
            n_ti,
            n_al,
            total_atoms,
        )
        return None

    e_form = formation_energy_per_atom(final_energy, n_ti, n_al)
    return StructureRecord(
        Structure=filepath.stem,
        Total_Atoms=total_atoms,
        n_Ti=n_ti,
        n_Al=n_al,
        Atomic_Fraction_Al=n_al / total_atoms,
        Total_Energy_eV=final_energy,
        Formation_Energy_eV_per_atom=e_form,
    )


def parse_castep_directory(directory: Path) -> pd.DataFrame:
    """Parse every ``.castep`` file in a directory into a tidy DataFrame.

    Only the mixed Ti-Al alloy cells are included in the dataset. Pure-element
    reference cells (file names that resolve to a single element) are skipped,
    since their energies define the references rather than data points.

    Args:
        directory: Directory containing ``.castep`` files.

    Returns:
        DataFrame sorted by ``Atomic_Fraction_Al`` with columns
        :data:`DATASET_COLUMNS`.

    Raises:
        FileNotFoundError: If ``directory`` does not exist.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Input directory not found: {directory}")

    records: list[StructureRecord] = []
    castep_files = sorted(directory.glob("*.castep"))
    logger.info("Found %d .castep file(s) in %s", len(castep_files), directory)

    for filepath in castep_files:
        n_ti, n_al = parse_composition_from_name(filepath.name)
        # Skip pure-element reference cells (only one element present).
        if n_ti == 0 or n_al == 0:
            logger.info("%s: pure-element reference cell, skipping.", filepath.name)
            continue

        record = parse_castep_file(filepath)
        if record is not None:
            records.append(record)

    if not records:
        logger.warning("No valid alloy structures parsed from %s", directory)
        return pd.DataFrame(columns=DATASET_COLUMNS)

    df = pd.DataFrame([asdict(r) for r in records], columns=DATASET_COLUMNS)
    df = df.sort_values(by="Atomic_Fraction_Al").reset_index(drop=True)
    logger.info("Parsed %d valid alloy structure(s).", len(df))
    return df


def build_dataset(input_dir: Path, output_path: Path) -> pd.DataFrame:
    """Parse CASTEP files and write the ML-ready dataset to CSV.

    Args:
        input_dir: Directory containing ``.castep`` files.
        output_path: Destination CSV path (parent directories are created).

    Returns:
        The parsed DataFrame that was written to disk.
    """
    df = parse_castep_directory(input_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Dataset written to %s (%d rows).", output_path, len(df))
    return df


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse CASTEP outputs and build the Ti-Al formation-energy dataset.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=config.RAW_DATA_DIR,
        help="Directory containing .castep files (default: data/raw).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.DATASET_PATH,
        help="Output CSV path (default: data/processed/alloy_ml_dataset.csv).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the parser."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    args = _build_arg_parser().parse_args(argv)

    try:
        df = build_dataset(args.input_dir, args.output)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1

    if df.empty:
        logger.error("No structures parsed; dataset is empty.")
        return 1

    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
