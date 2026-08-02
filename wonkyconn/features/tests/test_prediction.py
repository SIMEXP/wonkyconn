from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import pytest
from numpy.typing import NDArray

from wonkyconn.base import ConnectivityMatrix
from wonkyconn.features.age_sex_prediction import SiteRegressor, age_sex_scores, training_pipeline

subject_count = 128
feature_count = 4_096
random_state = 1

Task = Literal["classification", "regression"]

# Alternating site assignment reused both for confounded data generation and for
# the ``sites`` parametrization below, so the two stay perfectly aligned.
site_labels = np.array(["site-a", "site-b"] * (subject_count // 2))


@dataclass(frozen=True)
class Config:
    task: Task
    is_predictable: bool = False
    # When True, the site drives both the features and the labels, so the target
    # is only predictable while the site effect is present in the features.
    is_site_confounded: bool = False


@dataclass(frozen=True)
class Dataset:
    config: Config
    connectivity_data: NDArray[np.float32]
    target_labels: NDArray[np.float64] | NDArray[np.str_]


@pytest.fixture(
    params=[
        pytest.param(Config(task="classification", is_predictable=False), id="binary-random-labels"),
        pytest.param(Config(task="classification", is_predictable=True), id="binary-predictable-labels"),
        pytest.param(Config(task="regression", is_predictable=False), id="continuous-random-labels"),
        pytest.param(Config(task="regression", is_predictable=True), id="continuous-predictable-labels"),
        pytest.param(Config(task="classification", is_site_confounded=True), id="binary-site-confounded-labels"),
        pytest.param(Config(task="regression", is_site_confounded=True), id="continuous-site-confounded-labels"),
    ],
)
def dataset(request: pytest.FixtureRequest) -> Dataset:
    config: Config = request.param

    rng = np.random.default_rng(random_state)

    labels: NDArray[np.float64] | NDArray[np.str_]
    if config.is_site_confounded:
        # Site drives the features (via ``site_code``) and the labels together,
        # so the target is recoverable only until the site effect is removed.
        site_code = np.where(site_labels == "site-a", 1.0, -1.0)
        loadings = rng.normal(size=feature_count)
        connectivity_data = (
            np.outer(site_code, loadings) + rng.normal(scale=0.3, size=(subject_count, feature_count))
        ).astype(np.float32)
        match config.task:
            case "classification":
                labels = np.where(site_labels == "site-a", "male", "female")
            case "regression":
                labels = np.where(site_labels == "site-a", 30.0, 60.0) + rng.normal(scale=2.0, size=subject_count)
    else:
        latent = rng.normal(size=subject_count)
        loadings = rng.normal(size=feature_count)
        connectivity_data = (np.outer(latent, loadings) + rng.normal(scale=0.3, size=(subject_count, feature_count))).astype(
            np.float32
        )
        noise = rng.normal(scale=0.5, size=subject_count)
        match config.task:
            case "classification":
                score = latent + noise
                labels = np.where(score > np.median(score), "male", "female")
                if not config.is_predictable:
                    rng.shuffle(labels)
            case "regression":
                raw = (latent + noise) if config.is_predictable else (noise + noise)
                # Rescale to a plausible age range.
                labels = 18.0 + (raw - raw.min()) / (raw.max() - raw.min()) * 62.0

    return Dataset(
        config=config,
        connectivity_data=connectivity_data,
        target_labels=labels,
    )


@pytest.mark.parametrize(
    "sites",
    [
        pytest.param(None, id="without-sites"),
        pytest.param(site_labels, id="with-sites"),
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
        dataset.target_labels,
        task_type=dataset.config.task,
        n_splits=3,
        n_pca=5,
        n_jobs=1,
        random_state=42,
        sites=sites,
    )

    assert isinstance(summary, pd.DataFrame)
    assert set(summary.index) == expected_metrics
    assert list(summary.columns) == ["mean", "ci_lower", "ci_upper"]
    assert np.isfinite(summary.to_numpy()).all()
    assert (summary["ci_lower"] <= summary["mean"]).all()
    assert (summary["mean"] <= summary["ci_upper"]).all()

    score = float(summary.loc[primary_metric, "mean"])  # type: ignore[arg-type]

    if dataset.config.is_site_confounded:
        if sites is None:
            # Without correction the site confound is fully exploitable.
            assert score > learnable_threshold
        else:
            # Site-effect correction must strip the confound, dropping the
            # otherwise-perfect prediction back to chance level.
            assert score < chance_ceiling
    elif dataset.config.is_predictable:
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
