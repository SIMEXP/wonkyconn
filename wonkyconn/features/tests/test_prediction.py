from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

import numpy as np
import pandas as pd
import pytest
from numpy.typing import NDArray

from wonkyconn.base import ConnectivityMatrix
from wonkyconn.features.age_sex_prediction import SiteRegressor, age_sex_scores, training_pipeline

subject_count = 192
feature_count = 4_096
random_state = 1

site_labels = np.array(["site-a", "site-b"] * (subject_count // 2))


@dataclass(frozen=True)
class Config:
    task: Literal["classification", "regression"]
    # How the target relates to the connectivity features:
    #   "random"          - labels are independent noise (nothing to learn)
    #   "predictable"     - a latent factor drives both features and labels
    #   "site-confounded" - the site drives both features and labels
    signal: Literal["random", "predictable", "site-confounded"]


@dataclass(frozen=True)
class Dataset:
    config: Config
    connectivity_data: NDArray[np.float32]
    labels: NDArray[np.float64] | NDArray[np.str_]


def sex(score: NDArray[np.float64]) -> NDArray[np.str_]:
    """Convert a continuous score to a binary sex label based on the mean."""
    return np.where(score > np.mean(score), "male", "female")


def age(score: NDArray[np.float64]) -> NDArray[np.float64]:
    """Convert a continuous score to an age label based on a linear transformation."""
    return 18.0 + (score - score.min()) / (score.max() - score.min()) * 62.0


@pytest.fixture(
    params=[
        pytest.param(Config(task="classification", signal="random"), id="classification-random"),
        pytest.param(Config(task="classification", signal="predictable"), id="classification-predictable"),
        pytest.param(Config(task="classification", signal="site-confounded"), id="classification-site-confounded"),
        pytest.param(Config(task="regression", signal="random"), id="regression-random"),
        pytest.param(Config(task="regression", signal="predictable"), id="regression-predictable"),
        pytest.param(Config(task="regression", signal="site-confounded"), id="regression-site-confounded"),
    ],
)
def dataset(request: pytest.FixtureRequest) -> Dataset:
    config: Config = request.param
    rng = np.random.default_rng(random_state)

    loadings = rng.normal(size=feature_count)

    connectivity_data: NDArray[np.float32]
    labels: NDArray[np.float64] | NDArray[np.str_]

    if config.signal == "site-confounded":
        latent = np.where(site_labels == "site-a", 1.0, -1.0)
    else:
        latent = rng.normal(size=subject_count)
    noise = rng.normal(scale=0.5, size=subject_count)

    func: Callable[[NDArray[np.float64]], NDArray[np.float64] | NDArray[np.str_]]
    match config.task:
        case "classification":
            func = sex
        case "regression":
            func = age

    match config.signal:
        case "random":
            labels = func(rng.normal(size=subject_count))
        case "predictable":
            labels = func(latent + noise)
        case "site-confounded":
            labels = func(latent)

    noise = rng.normal(scale=0.3, size=(subject_count, feature_count))
    connectivity_data = (np.outer(latent, loadings) + noise).astype(np.float32)
    return Dataset(
        config=config,
        connectivity_data=connectivity_data,
        labels=labels,
    )


@pytest.mark.parametrize(
    "sites",
    [
        pytest.param(None, id="without-site-correction"),
        pytest.param(site_labels, id="with-site-correction"),
    ],
)
def test_training_pipeline(
    dataset: Dataset,
    sites: NDArray[np.str_] | None,
) -> None:
    if dataset.config.task == "classification":
        expected_metrics = frozenset({"accuracy", "roc_auc"})
        primary_metric = "roc_auc"
        learnable_threshold = 0.8
        chance_ceiling = 0.65
    else:
        expected_metrics = frozenset({"mae", "r2"})
        primary_metric = "r2"
        learnable_threshold = 0.3
        chance_ceiling = 0.2

    summary = training_pipeline(
        dataset.connectivity_data,
        dataset.labels,
        task_type=dataset.config.task,
        n_splits=3,
        n_pca=5,
        n_jobs=1,
        random_state=random_state,
        sites=sites,
    )

    assert isinstance(summary, pd.DataFrame)
    assert set(summary.index) == expected_metrics
    assert list(summary.columns) == ["mean", "ci_lower", "ci_upper"]
    assert np.isfinite(summary.to_numpy()).all()
    assert (summary["ci_lower"] <= summary["mean"]).all()
    assert (summary["mean"] <= summary["ci_upper"]).all()

    score = float(summary.loc[primary_metric, "mean"])  # type: ignore[arg-type]

    if dataset.config.signal == "site-confounded":
        if sites is None:
            # Without correction the site confound is fully exploitable.
            assert score > learnable_threshold
        else:
            # Site-effect correction must strip the confound, dropping the
            # otherwise-perfect prediction back to chance level.
            assert score < chance_ceiling
    elif dataset.config.signal == "predictable":
        # Labels that carry signal should be recovered above the chance baseline.
        assert score > learnable_threshold
    else:
        # Random labels should not be recoverable above chance level.
        assert score < chance_ceiling


def test_age_sex_scores(tmp_path: Path) -> None:
    rng = np.random.default_rng(random_state)

    region_count = np.sqrt(feature_count).astype(int).item()

    matrices = []
    for i in range(subject_count):
        square = rng.normal(size=(region_count, region_count)).astype(np.float32)
        path = tmp_path / f"sub-{i}.tsv"
        np.savetxt(path, square + square.T, delimiter="\t")
        matrices.append(ConnectivityMatrix(path, metadata=dict()))

    ages = rng.uniform(18.0, 80.0, subject_count)
    genders = np.array(["m", "f"] * (subject_count // 2))
    sites = np.array(["site-a", "site-b"] * (subject_count // 2))

    scores = age_sex_scores(matrices, ages, genders, sites, n_splits=3, n_pca=5, n_jobs=1)
    assert len(scores) == 8
    assert all(np.isfinite(value) for value in scores.values())


def test_site_regressor_requires_two_sites() -> None:
    regressor = SiteRegressor(np.array(["site-a", "site-a"]))
    with pytest.raises(ValueError, match="at least two sites"):
        regressor.fit(pd.DataFrame(np.zeros((2, 3), dtype=np.float32)))
