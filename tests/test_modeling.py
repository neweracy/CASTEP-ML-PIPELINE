"""Tests for the GPR modeling utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from dft_ml_pipeline.modeling import (
    create_gpr_model,
    evaluate_model,
    load_dataset,
    plot_results,
    predict_curve,
    save_model,
    save_predictions,
)


@pytest.fixture
def toy_data() -> tuple[np.ndarray, np.ndarray]:
    """A small, smooth composition/energy relationship for fitting."""
    x = np.array([0.0625, 0.125, 0.25, 0.5, 0.75]).reshape(-1, 1)
    y = np.array([-0.055, -0.098, -0.165, -0.317, -0.257])
    return x, y


@pytest.fixture
def fitted_model(toy_data):
    x, y = toy_data
    model = create_gpr_model()
    model.fit(x, y)
    return model, x, y


def _write_csv(path: Path, x: np.ndarray, y: np.ndarray) -> None:
    import pandas as pd

    pd.DataFrame(
        {"Atomic_Fraction_Al": x.ravel(), "Formation_Energy_eV_per_atom": y}
    ).to_csv(path, index=False)


class TestLoadDataset:
    def test_loads_features_and_target(self, tmp_path, toy_data):
        x, y = toy_data
        csv = tmp_path / "data.csv"
        _write_csv(csv, x, y)
        x_loaded, y_loaded, df = load_dataset(csv)
        assert x_loaded.shape == (5, 1)
        assert y_loaded.shape == (5,)
        assert len(df) == 5

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_dataset(tmp_path / "missing.csv")

    def test_missing_column_raises(self, tmp_path):
        import pandas as pd

        csv = tmp_path / "bad.csv"
        pd.DataFrame({"Atomic_Fraction_Al": [0.1, 0.2]}).to_csv(csv, index=False)
        with pytest.raises(KeyError):
            load_dataset(csv)


class TestModel:
    def test_fit_interpolates_training_points(self, fitted_model):
        model, x, y = fitted_model
        y_pred = model.predict(x)
        # GPR with low noise should closely reproduce noise-free DFT points.
        assert np.allclose(y_pred, y, atol=1e-2)

    def test_evaluate_returns_expected_metrics(self, fitted_model):
        model, x, y = fitted_model
        metrics = evaluate_model(model, x, y)
        assert {"mae", "rmse", "r2", "cv_mae", "mean_uncertainty"} <= metrics.keys()
        assert metrics["r2"] > 0.99

    def test_predict_curve_shape_and_range(self, fitted_model):
        model, _, _ = fitted_model
        x_pred, y_pred, sigma = predict_curve(model, n_points=50)
        assert x_pred.shape == (50, 1)
        assert y_pred.shape == (50,)
        assert sigma.shape == (50,)
        assert x_pred.min() == pytest.approx(0.0)
        assert x_pred.max() == pytest.approx(1.0)
        assert (sigma >= 0).all()

    def test_reproducible_with_seed(self, toy_data):
        x, y = toy_data
        m1 = create_gpr_model()
        m1.fit(x, y)
        m2 = create_gpr_model()
        m2.fit(x, y)
        assert np.allclose(m1.predict(x), m2.predict(x))


class TestPersistence:
    def test_save_model_and_predictions(self, fitted_model, tmp_path):
        model, _, _ = fitted_model
        x_pred, y_pred, sigma = predict_curve(model, n_points=20)

        model_path = save_model(model, tmp_path / "model.pkl")
        pred_path = save_predictions(
            x_pred, y_pred, sigma, tmp_path / "predictions.csv"
        )
        assert model_path.exists()
        assert pred_path.exists()

    def test_plot_saves_figure_headless(self, fitted_model, tmp_path):
        model, x, y = fitted_model
        x_pred, y_pred, sigma = predict_curve(model, n_points=20)
        fig_path = plot_results(
            x, y, x_pred, y_pred, sigma, output_path=tmp_path / "curve.png"
        )
        assert fig_path.exists()
        assert fig_path.stat().st_size > 0
