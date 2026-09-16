# Materials Studio automation scripts

These scripts drive the **DFT data-generation** stage of the pipeline. They run
**inside BIOVIA Materials Studio** (via its scripting console), not through the
Python package in `src/`. They are kept here for provenance and reproducibility.

| Script | Language | Purpose |
| --- | --- | --- |
| `batch_run.py` | MaterialsScript (Python) | Batch geometry optimization of every structure in the `Structures` folder. |
| `batch_run.pl` | MaterialsScript (Perl) | Equivalent batch driver with explicit CASTEP settings (cutoff, stress, Mulliken analysis). |

## CASTEP settings

Both scripts use the baseline settings that define this study:

- Task: Geometry Optimization
- Functional: PBE
- Plane-wave cutoff: 420 eV
- Metallic system, full cell optimization

> **Important:** the pure-element reference calculations (`Al`, `Ti`) must use
> the *same* settings so that formation energies are consistent. See
> `src/dft_ml_pipeline/config.py` for the resulting reference energies.

## How to run

1. Open the project in Materials Studio.
2. Ensure the alloy structures live in a folder named `Structures`.
3. Open the script in the Materials Studio scripting console and run it.
4. Copy the resulting `*.castep` files into `data/raw/` for parsing with
   `dft-parse`.
