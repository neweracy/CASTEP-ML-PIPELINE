# DFT-ML Pipeline Project Guidelines

## Project Overview
This project processes CASTEP DFT calculation outputs for Ti-Al alloys and prepares datasets for machine learning models to predict formation energies.

## Tech Stack
- **Python**: >=3.9
- **Package Manager**: uv (modern, fast Python package manager)
- **Key Libraries**: pandas, numpy, scikit-learn, matplotlib, seaborn

## Code Style & Standards

### Python Code Style
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff
- Follow PEP 8 conventions
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes

### Naming Conventions
- **Files**: `snake_case.py`
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### Comments
- Use comments to explain *why*, not *what*
- Document non-obvious scientific calculations with references if applicable
- Include units in variable names or comments for physical quantities (e.g., `energy_ev`, `distance_angstrom`)

## Project Structure

### Directories
- **ML_Data/**: Raw CASTEP output files (.castep, .geom, .bands, etc.)
- **STRUCTURES/**: Input structure files for DFT calculations
- **Al_BASE_STRUCTURE/**, **Ti_BASE_STRUCTURE/**: Base crystal structures

### Key Files
- **parse_castep.py**: Main parser to extract DFT data and calculate formation energies
- **BatchRun.py**: Batch processing script for Materials Studio
- **alloy_ml_dataset.csv**: Generated ML-ready dataset (not tracked in git)

## Scientific Context

### DFT Calculations
- Software: CASTEP (Materials Studio)
- System: Ti-Al binary alloy system
- Target property: Formation energy per atom (eV/atom)

### Reference Energies
```python
MU_TI = -1593.839175  # eV/atom for pure Ti
MU_AL = -110.830296   # eV/atom for pure Al
```

### Formation Energy Formula
```
E_form = (E_total - (n_Ti * MU_TI + n_Al * MU_AL)) / N_total
```

## Development Workflow

### Environment Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Running Scripts
```bash
# Parse CASTEP files
uv run python parse_castep.py

# Run with specific Python version
uv run --python 3.9 python parse_castep.py
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

## File Handling Rules

### Input Files (Track in Git)
- Python scripts (*.py)
- Structure input files (*.cell, *.param)
- Base structures (*.xsd in BASE_STRUCTURE folders)
- Configuration files (pyproject.toml, .gitignore, CLAUDE.md)

### Output Files (Do NOT Track)
- CASTEP outputs (*.castep, *.castep_bin, *.geom, *.bands, *.cst_esp)
- Generated datasets (*.csv)
- Temporary/auxiliary files (*.trjaux, *.kptaux)
- Virtual environments (.venv/)

## Data Processing Guidelines

### CASTEP Parsing
1. Always extract the **last** "Final Enthalpy" value (fully relaxed structure)
2. Verify composition from filename matches total atoms in output
3. Skip files with composition mismatches (log warning)
4. Sort output by atomic fraction for consistency

### ML Dataset Requirements
- **Features**: Composition (n_Ti, n_Al, atomic_fraction_Al), structure identifier
- **Target**: Formation energy per atom (eV/atom)
- **Format**: CSV with headers
- **Validation**: Ensure no NaN values, check energy ranges are physical

## Error Handling

### Common Issues
1. **Filename parsing fails**: Ensure structure files follow `Ti{n}Al{m}.castep` format
2. **Energy not found**: Check CASTEP completed successfully (look for "Final Enthalpy")
3. **Composition mismatch**: Verify filename reflects actual structure

### Validation Checks
- Total atoms = n_Ti + n_Al
- Formation energies should be negative for stable phases
- Energy values in reasonable range (-1 to 1 eV/atom typically)

## Machine Learning Notes

### Next Steps (Not Yet Implemented)
- Feature engineering (local atomic environments, symmetry descriptors)
- Model training (Random Forest, Gradient Boosting, Neural Networks)
- Cross-validation and hyperparameter tuning
- Prediction uncertainty quantification
- Visualization of convex hull

### Data Considerations
- Small dataset: Use cross-validation carefully
- Physical constraints: Formation energies must respect thermodynamic limits
- Extrapolation: Model valid only within training composition range

## Best Practices

1. **Always validate parsed data** before ML training
2. **Document scientific assumptions** in code comments
3. **Keep units explicit** in variable names or docstrings
4. **Version control**: Commit frequently with descriptive messages
5. **Testing**: Verify parsing on known structures before batch processing
6. **Reproducibility**: Fix random seeds for ML models

## Resources

### Materials Studio / CASTEP
- CASTEP output files contain comprehensive calculation details
- Final Enthalpy = converged total energy after geometry optimization
- "Total number of ions" = total atoms in simulation cell

### Python Environment
- Use `uv` for all package management (faster than pip)
- Pin dependencies in pyproject.toml for reproducibility
- Use `uv.lock` to ensure exact versions across environments
