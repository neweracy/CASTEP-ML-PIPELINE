"""Gaussian Process Regression surrogate for Ti-Al formation energies.

This module trains a Gaussian Process Regressor (GPR) on the DFT-derived
formation energies, evaluates it with leave-one-out cross-validation
(appropriate for small datasets), and produces a prediction curve with a 95%
confidence band across the full composition range.

GPR is chosen deliberately: it is non-parametric, interpolates the (noise-free)
DFT points closely, and provides calibrated uncertainty estimates that flag
where additional DFT calculations would be most valuable.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import ConstantKernel as C
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_score

from . import config

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = ["Atomic_Fraction_Al"]
TARGET_COLUMN = "Formation_Energy_eV_per_atom"


def load_dataset(filepath: Path) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Load and validate the DFT dataset.

    Args:
        filepath: Path to the dataset CSV.

    Returns:
        Tuple ``(X, y, dataframe)`` where ``X`` has shape ``(n, 1)``.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        KeyError: If required columns are missing.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. Run the parser first "
            "(e.g. `dft-parse` or `make parse`)."
        )

    logger.info("Loading dataset from %s", filepath)
    df = pd.read_csv(filepath)

    required = set(FEATURE_COLUMNS) | {TARGET_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    x = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df[TARGET_COLUMN].to_numpy(dtype=float)

    logger.info("Loaded %d samples", len(df))
    logger.info("Composition range: %.3f to %.3f", x.min(), x.max())
    logger.info("Formation energy range: %.4f to %.4f eV/atom", y.min(), y.max())
    return x, y, df


def create_gpr_model(
    length_scale: float = 0.2,
    constant_value: float = 1.0,
    alpha: float = 1e-4,
    n_restarts: int = 10,
) -> GaussianProcessRegressor:
    """Create and configure a Gaussian Process Regressor.

    Args:
        length_scale: Initial RBF length scale (controls smoothness).
        constant_value: Initial constant-kernel value (output variance).
        alpha: Noise level added to the diagonal (regularization).
        n_restarts: Number of optimizer restarts for the marginal likelihood.

    Returns:
        A configured but untrained :class:`GaussianProcessRegressor`.
    """
    kernel = C(constant_value, (1e-2, 1e2)) * RBF(
        length_scale=length_scale, length_scale_bounds=(1e-2, 1e1)
    )
    model = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=n_restarts,
        alpha=alpha,
        normalize_y=True,
        random_state=0,
    )
    logger.info("Created GPR model with kernel: %s", kernel)
    return model


def evaluate_model(
    model: GaussianProcessRegressor, x: np.ndarray, y: np.ndarray
) -> dict[str, float]:
    """Evaluate a trained model with in-sample metrics and leave-one-out CV.

    Args:
        model: A fitted GPR model.
        x: Training features.
        y: Training targets.

    Returns:
        Dictionary of metrics: ``mae``, ``rmse``, ``r2``, ``cv_mae``,
        ``mean_uncertainty``.
    """
    y_pred, y_std = model.predict(x, return_std=True)

    metrics = {
        "mae": float(mean_absolute_error(y, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, y_pred))),
        "r2": float(r2_score(y, y_pred)),
        "mean_uncertainty": float(y_std.mean()),
    }

    # Leave-one-out CV is the realistic generalization estimate for tiny data.
    if len(y) > 2:
        cv_scores = cross_val_score(
            model, x, y, cv=LeaveOneOut(), scoring="neg_mean_absolute_error"
        )
        metrics["cv_mae"] = float(-cv_scores.mean())
    else:
        metrics["cv_mae"] = float("nan")

    logger.info("Model evaluation:")
    logger.info("  R2 score:            %.4f", metrics["r2"])
    logger.info("  MAE:                 %.6f eV/atom", metrics["mae"])
    logger.info("  RMSE:                %.6f eV/atom", metrics["rmse"])
    logger.info("  CV MAE (LOO):        %.6f eV/atom", metrics["cv_mae"])
    logger.info("  Mean uncertainty s:  %.6f eV/atom", metrics["mean_uncertainty"])
    return metrics


def predict_curve(
    model: GaussianProcessRegressor, n_points: int = 200
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Predict formation energies across the full composition range.

    Args:
        model: A fitted GPR model.
        n_points: Number of evenly spaced composition points in ``[0, 1]``.

    Returns:
        Tuple ``(x_pred, y_pred, sigma)``.
    """
    x_pred = np.linspace(0.0, 1.0, n_points).reshape(-1, 1)
    y_pred, sigma = model.predict(x_pred, return_std=True)
    return x_pred, y_pred, sigma


def plot_results(
    x: np.ndarray,
    y: np.ndarray,
    x_pred: np.ndarray,
    y_pred: np.ndarray,
    sigma: np.ndarray,
    output_path: Path = config.DEFAULT_FIGURE_PATH,
    dpi: int = 300,
    show: bool = False,
) -> Path:
    """Plot DFT points, the GPR curve, and its 95% confidence band.

    Args:
        x: Training composition values.
        y: Training formation energies.
        x_pred: Prediction composition values.
        y_pred: Predicted formation energies.
        sigma: Prediction standard deviations.
        output_path: Path to save the figure.
        dpi: Resolution of the saved figure.
        show: If ``True``, display the plot interactively.

    Returns:
        The path the figure was saved to.
    """
    if not show:
        # Use a non-interactive backend so plotting works headless (CI, servers).
        matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.scatter(
        x,
        y,
        color="crimson",
        label="DFT data (CASTEP)",
        zorder=5,
        s=80,
        edgecolors="black",
        linewidth=1.5,
    )
    plt.plot(x_pred, y_pred, "b-", label="GPR surrogate model", linewidth=2.5)
    plt.fill_between(
        x_pred.ravel(),
        y_pred - 1.96 * sigma,
        y_pred + 1.96 * sigma,
        alpha=0.25,
        color="blue",
        label="95% confidence interval",
    )
    plt.xlabel("Aluminum mole fraction ($x$ in $Ti_{1-x}Al_{x}$)", fontsize=12)
    plt.ylabel("Formation energy (eV/atom)", fontsize=12)
    plt.title(
        "Ti-Al formation energy: DFT calculations vs. GPR model",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="best", frameon=True, shadow=True)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    logger.info("Saved plot to %s", output_path)

    if show:
        plt.show()
    plt.close()
    return output_path


def save_model(
    model: GaussianProcessRegressor, filepath: Path = config.DEFAULT_MODEL_PATH
) -> Path:
    """Serialize a trained model to disk with joblib."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, filepath)
    logger.info("Model saved to %s", filepath)
    return filepath


def save_predictions(
    x_pred: np.ndarray,
    y_pred: np.ndarray,
    sigma: np.ndarray,
    filepath: Path = config.DEFAULT_PREDICTIONS_PATH,
) -> Path:
    """Write predictions and 95% confidence bounds to CSV."""
    df_pred = pd.DataFrame(
        {
            "Atomic_Fraction_Al": x_pred.ravel(),
            "Predicted_Formation_Energy_eV_per_atom": y_pred,
            "Uncertainty_eV_per_atom": sigma,
            "Lower_95CI": y_pred - 1.96 * sigma,
            "Upper_95CI": y_pred + 1.96 * sigma,
        }
    )
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_pred.to_csv(filepath, index=False)
    logger.info("Predictions saved to %s", filepath)
    return filepath


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train a GPR model for Ti-Al formation-energy prediction.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=config.DATASET_PATH,
        help="Path to the DFT dataset CSV.",
    )
    parser.add_argument(
        "--n-points",
        type=int,
        default=200,
        help="Number of prediction points along the composition axis.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.DEFAULT_FIGURE_PATH,
        help="Output path for the plot.",
    )
    parser.add_argument(
        "--save-model", action="store_true", help="Save the trained model to disk."
    )
    parser.add_argument(
        "--save-predictions", action="store_true", help="Save predictions to CSV."
    )
    parser.add_argument(
        "--show", action="store_true", help="Display the plot interactively."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the training pipeline."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    args = _build_arg_parser().parse_args(argv)

    try:
        x, y, _ = load_dataset(args.dataset)
    except (FileNotFoundError, KeyError) as exc:
        logger.error("Failed to load dataset: %s", exc)
        return 1

    logger.info("Training Gaussian Process Regressor...")
    model = create_gpr_model()
    model.fit(x, y)
    logger.info("Training complete. Optimized kernel: %s", model.kernel_)

    evaluate_model(model, x, y)

    x_pred, y_pred, sigma = predict_curve(model, n_points=args.n_points)
    plot_results(x, y, x_pred, y_pred, sigma, output_path=args.output, show=args.show)

    if args.save_model:
        save_model(model)
    if args.save_predictions:
        save_predictions(x_pred, y_pred, sigma)

    logger.info("Pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
