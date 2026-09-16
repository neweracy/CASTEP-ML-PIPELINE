"""
Machine Learning Model Training for Ti-Al Formation Energy Prediction

This script trains a Gaussian Process Regression (GPR) model on DFT-calculated
formation energies and generates prediction curves with uncertainty quantification.
"""

import argparse
import logging
from pathlib import Path
from typing import Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, LeaveOneOut

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_dataset(filepath: str) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Load the DFT dataset from CSV file.

    Args:
        filepath: Path to the CSV file containing DFT data

    Returns:
        Tuple of (X features, y targets, full DataFrame)

    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        KeyError: If required columns are missing
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. Run parse_castep.py first."
        )

    logger.info(f"Loading dataset from {filepath}")
    df = pd.read_csv(filepath)

    # Validate required columns
    required_columns = ["Atomic_Fraction_Al", "Formation_Energy_eV_per_atom"]
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    # Extract features and target
    X = df[["Atomic_Fraction_Al"]].values
    y = df["Formation_Energy_eV_per_atom"].values

    logger.info(f"Loaded {len(df)} samples")
    logger.info(f"Composition range: {X.min():.3f} to {X.max():.3f}")
    logger.info(f"Formation energy range: {y.min():.4f} to {y.max():.4f} eV/atom")

    return X, y, df


def create_gpr_model(
    length_scale: float = 0.2,
    constant_value: float = 1.0,
    alpha: float = 1e-4,
    n_restarts: int = 10,
) -> GaussianProcessRegressor:
    """
    Create and configure a Gaussian Process Regressor.

    Args:
        length_scale: Initial RBF kernel length scale (controls smoothness)
        constant_value: Initial constant kernel value (output variance)
        alpha: Noise level in the training data (regularization)
        n_restarts: Number of random restarts for optimizer

    Returns:
        Configured but untrained GaussianProcessRegressor
    """
    kernel = C(constant_value, (1e-2, 1e2)) * RBF(
        length_scale=length_scale, length_scale_bounds=(1e-2, 1e1)
    )

    gp = GaussianProcessRegressor(
        kernel=kernel, n_restarts_optimizer=n_restarts, alpha=alpha, normalize_y=True
    )

    logger.info(f"Created GPR model with kernel: {kernel}")
    return gp


def evaluate_model(
    model: GaussianProcessRegressor, X: np.ndarray, y: np.ndarray
) -> dict:
    """
    Evaluate model performance using cross-validation and metrics.

    Args:
        model: Trained GPR model
        X: Training features
        y: Training targets

    Returns:
        Dictionary of evaluation metrics
    """
    # Predictions on training data
    y_pred, y_std = model.predict(X, return_std=True)

    # Calculate metrics
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    # Leave-one-out cross-validation (appropriate for small datasets)
    loo = LeaveOneOut()
    cv_scores = cross_val_score(model, X, y, cv=loo, scoring="neg_mean_absolute_error")
    cv_mae = -cv_scores.mean()

    metrics = {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "cv_mae": cv_mae,
        "mean_uncertainty": y_std.mean(),
    }

    logger.info("Model Evaluation:")
    logger.info(f"  R² Score: {r2:.4f}")
    logger.info(f"  MAE: {mae:.6f} eV/atom")
    logger.info(f"  RMSE: {rmse:.6f} eV/atom")
    logger.info(f"  CV MAE (LOO): {cv_mae:.6f} eV/atom")
    logger.info(f"  Mean uncertainty (σ): {y_std.mean():.6f} eV/atom")

    return metrics


def plot_results(
    X: np.ndarray,
    y: np.ndarray,
    X_pred: np.ndarray,
    y_pred: np.ndarray,
    sigma: np.ndarray,
    output_path: str = "formation_energy_curve.png",
    dpi: int = 300,
):
    """
    Generate and save the formation energy prediction plot.

    Args:
        X: Training composition values
        y: Training formation energies
        X_pred: Prediction composition values
        y_pred: Predicted formation energies
        sigma: Prediction standard deviations
        output_path: Path to save the figure
        dpi: Resolution for saved figure
    """
    plt.figure(figsize=(10, 6))

    # Plot DFT data points
    plt.scatter(X, y, color="crimson", label="DFT Data (CASTEP)", zorder=5, s=80, edgecolors='black', linewidth=1.5)

    # Plot GPR prediction
    plt.plot(X_pred, y_pred, "b-", label="GPR Surrogate Model", linewidth=2.5)

    # Plot 95% confidence interval
    plt.fill_between(
        X_pred.ravel(),
        y_pred - 1.96 * sigma,
        y_pred + 1.96 * sigma,
        alpha=0.25,
        color="blue",
        label="95% Confidence Interval",
    )

    # Formatting
    plt.xlabel("Aluminum Mole Fraction ($x$ in $Ti_{1-x}Al_x$)", fontsize=12)
    plt.ylabel("Formation Energy (eV/atom)", fontsize=12)
    plt.title("Ti-Al Formation Energy: DFT Calculations vs. GPR Model", fontsize=14, fontweight='bold')
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc='best', frameon=True, shadow=True)
    plt.tight_layout()

    # Save figure
    output_path = Path(output_path)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    logger.info(f"Saved plot to {output_path}")

    plt.show()


def save_model(
    model: GaussianProcessRegressor, filepath: str = "models/gpr_model.pkl"
):
    """
    Save the trained model to disk.

    Args:
        model: Trained GPR model
        filepath: Path to save the model
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, filepath)
    logger.info(f"Model saved to {filepath}")


def save_predictions(
    X_pred: np.ndarray,
    y_pred: np.ndarray,
    sigma: np.ndarray,
    filepath: str = "outputs/predictions.csv",
):
    """
    Save predictions and uncertainties to CSV.

    Args:
        X_pred: Prediction composition values
        y_pred: Predicted formation energies
        sigma: Prediction standard deviations
        filepath: Path to save predictions
    """
    df_pred = pd.DataFrame(
        {
            "Atomic_Fraction_Al": X_pred.ravel(),
            "Predicted_Formation_Energy_eV_per_atom": y_pred,
            "Uncertainty_eV_per_atom": sigma,
            "Lower_95CI": y_pred - 1.96 * sigma,
            "Upper_95CI": y_pred + 1.96 * sigma,
        }
    )

    filepath = Path(filepath)
    df_pred.to_csv(filepath, index=False)
    logger.info(f"Predictions saved to {filepath}")


def main():
    """Main training pipeline."""
    parser = argparse.ArgumentParser(
        description="Train GPR model for Ti-Al formation energy prediction"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/processed/alloy_ml_dataset.csv",
        help="Path to the DFT dataset CSV",
    )
    parser.add_argument(
        "--n-points",
        type=int,
        default=200,
        help="Number of prediction points along composition axis",
    )
    parser.add_argument(
        "--save-model",
        action="store_true",
        help="Save the trained model to disk",
    )
    parser.add_argument(
        "--save-predictions",
        action="store_true",
        help="Save predictions to CSV",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/formation_energy_curve.png",
        help="Output path for the plot",
    )

    args = parser.parse_args()

    # Load data
    try:
        X, y, df = load_dataset(args.dataset)
    except (FileNotFoundError, KeyError) as e:
        logger.error(f"Failed to load dataset: {e}")
        return 1

    # Create and train model
    logger.info("Training Gaussian Process Regressor...")
    gp = create_gpr_model()
    gp.fit(X, y)
    logger.info("Training complete!")
    logger.info(f"Optimized kernel: {gp.kernel_}")

    # Evaluate model
    metrics = evaluate_model(gp, X, y)

    # Generate predictions across composition range
    X_pred = np.linspace(0.0, 1.0, args.n_points).reshape(-1, 1)
    y_pred, sigma = gp.predict(X_pred, return_std=True)

    # Plot results
    plot_results(X, y, X_pred, y_pred, sigma, output_path=args.output)

    # Save model if requested
    if args.save_model:
        save_model(gp)

    # Save predictions if requested
    if args.save_predictions:
        save_predictions(X_pred, y_pred, sigma)

    logger.info("Pipeline complete!")
    return 0


if __name__ == "__main__":
    exit(main())
