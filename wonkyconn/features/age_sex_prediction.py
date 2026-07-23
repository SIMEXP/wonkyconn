from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

import numpy as np
import pandas as pd
from joblib import parallel_backend  # type: ignore[import-not-found]
from nilearn.connectome import sym_matrix_to_vec  # type: ignore[import-not-found]
from numpy.typing import NDArray
from sklearn.decomposition import PCA  # type: ignore[import-not-found]
from sklearn.impute import SimpleImputer  # type: ignore[import-not-found]
from sklearn.linear_model import LogisticRegression, Ridge  # type: ignore[import-not-found]
from sklearn.metrics import (  # type: ignore[import-not-found]
    accuracy_score,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedShuffleSplit  # type: ignore[import-not-found]
from sklearn.pipeline import Pipeline  # type: ignore[import-not-found]
from sklearn.preprocessing import LabelEncoder, StandardScaler  # type: ignore[import-not-found]

if TYPE_CHECKING:
    from ..base import ConnectivityMatrix


def regress_site(
    X_train: NDArray[np.float32],
    X_test: NDArray[np.float32],
    site_train: NDArray[np.str_],
    site_test: NDArray[np.str_],
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """Regress out site effects from the training and test data."""

    train_site = pd.get_dummies(site_train, drop_first=True, dtype=float)
    test_site = pd.get_dummies(site_test, drop_first=True, dtype=float)

    test_site = test_site.reindex(
        columns=train_site.columns,
        fill_value=0.0,
    )

    design_train = np.column_stack([np.ones(len(train_site)), train_site.to_numpy()])

    design_test = np.column_stack([np.ones(len(test_site)), test_site.to_numpy()])

    beta_train, *_ = np.linalg.lstsq(design_train, X_train, rcond=None,)
    beta_test, *_ = np.linalg.lstsq(design_test, X_test, rcond=None,)
    X_train_corr = X_train - design_train[:, 1:] @ beta_train[1:, :]
    X_test_corr = X_test - design_test[:, 1:] @ beta_test[1:, :]

    return X_train_corr, X_test_corr


def training_pipeline(
    connectivity_data: NDArray[np.float32],
    target_labels: NDArray[np.float64] | NDArray[np.str_],
    task_type: str,
    n_splits: int,
    n_pca: int,
    n_jobs: int = 4,
    random_state: int = 1,
    sites: NDArray[np.str_] | None = None,
) -> pd.DataFrame:
    """Runs a cross-validation pipeline for age or sex prediction.

    Args:
        connectivity_data: Vectorized connectivity matrix.
        target_labels: Target vector (ages or genders).
        task_type (str): Type of task ('classification' or 'regression').
        n_splits (int): Number of repetitions for cross-validation.
        n_pca (int): Number of principal components to extract.
        n_jobs (int): Number of cores for parallel calculation.
        random_state (int): Seed for reproducibility.
        sites (NDArray[np.str_] | None): Site labels for the data.

    Returns:
        pd.DataFrame: Statistics (mean, 95% CI) of the scores obtained.
    """
    connectivity_data = np.asarray(connectivity_data, dtype=np.float32, order="C")

    if task_type == "classification":
        y = LabelEncoder().fit_transform(target_labels)
        estimator = LogisticRegression(max_iter=5000, solver="saga", penalty="l2", n_jobs=n_jobs, random_state=random_state)
        cv_strategy = StratifiedShuffleSplit(n_splits=n_splits, test_size=0.2, random_state=random_state)
        scoring_metrics = ["accuracy", "roc_auc"]
        splits = cv_strategy.split(connectivity_data, y)

    else:
        y = np.asarray(target_labels)
        estimator = Ridge(alpha=1.0)

        bins = pd.qcut(y, q=5, labels=False, duplicates="drop")
        cv_strategy = StratifiedShuffleSplit(n_splits=n_splits, test_size=0.2, random_state=random_state)
        splits = list(cv_strategy.split(np.zeros_like(bins), bins))

        scoring_metrics = ["mae", "r2"]

    pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=n_pca, svd_solver="randomized", random_state=random_state)),
            ("estimator", estimator),
        ]
    )

    scores = {metric: [] for metric in scoring_metrics}

    with parallel_backend("threading", n_jobs=n_jobs):
        for train_idx, test_idx in splits:
            X_train = connectivity_data[train_idx]
            X_test = connectivity_data[test_idx]

            y_train = y[train_idx]
            y_test = y[test_idx]

            if sites is not None:
                X_train, X_test = regress_site(
                    X_train,
                    X_test,
                    sites[train_idx],
                    sites[test_idx],
                )

            pipe.fit(X_train, y_train)
            y_pred = pipe.predict(X_test)

            if task_type == "classification":
                scores["accuracy"].append(accuracy_score(y_test, y_pred))

                y_prob = pipe.predict_proba(X_test)[:, 1]

                scores["roc_auc"].append(roc_auc_score(y_test, y_prob))

            else:
                scores["mae"].append(mean_absolute_error(y_test, y_pred))

                scores["r2"].append(r2_score(y_test, y_pred))

    scores_df = pd.DataFrame(scores)

    summary = scores_df.agg(["mean"]).T
    summary["ci_lower"] = scores_df.quantile(0.025)
    summary["ci_upper"] = scores_df.quantile(0.975)

    return summary


def age_sex_scores(
    connectivity_matrices: List[ConnectivityMatrix],
    ages: NDArray[np.float64],
    genders: NDArray[np.str_],
    sites: NDArray[np.str_] | None,
    n_splits: int,
    n_pca: int,
    n_jobs: int = 4,
    random_state: int = 42,
) -> Dict[str, float]:
    """Computes age and sex prediction scores via connectivity.

    Args:
        connectivity_matrices (List[ConnectivityMatrix]): List of matrix objects.
        ages: Vector of subject ages.
        genders: Vector of subject genders.
        sites: Vector of subject sites.
        n_splits (int): Number of splits for cross-validation.
        n_pca (int): Number of PCA components.
        n_jobs (int): Number of joblib threads.
        random_state (int): Random seed.

    Returns:
        Dict[str, float]: Dictionary containing AUC, Accuracy, MAE, and R2.
    """
    loaded_mats = np.asarray([cm.load() for cm in connectivity_matrices], dtype=np.float32)
    connectivity_features = sym_matrix_to_vec(loaded_mats, discard_diagonal=True)

    sex_summary = training_pipeline(
        connectivity_features,
        genders,
        task_type="classification",
        n_splits=n_splits,
        n_pca=n_pca,
        n_jobs=n_jobs,
        random_state=random_state,
        sites=sites,
    )

    age_summary = training_pipeline(
        connectivity_features,
        ages,
        task_type="regression",
        n_splits=n_splits,
        n_pca=n_pca,
        n_jobs=n_jobs,
        random_state=random_state,
        sites=sites,
    )

    return {
        "sex_auc": float(sex_summary.loc["roc_auc", "mean"]),  # type: ignore[arg-type]
        "sex_auc_ci_lower": float(sex_summary.loc["roc_auc", "ci_lower"]),  # type: ignore[arg-type]
        "sex_auc_ci_upper": float(sex_summary.loc["roc_auc", "ci_upper"]),  # type: ignore[arg-type]
        "sex_accuracy": float(sex_summary.loc["accuracy", "mean"]),  # type: ignore[arg-type]
        "age_mae": float(age_summary.loc["mae", "mean"]),  # type: ignore[arg-type, operator]
        "age_mae_ci_lower": float(age_summary.loc["mae", "ci_lower"]),  # type: ignore[arg-type, operator]
        "age_mae_ci_upper": float(age_summary.loc["mae", "ci_upper"]),  # type: ignore[arg-type, operator]
        "age_r2": float(age_summary.loc["r2", "mean"]),  # type: ignore[arg-type]
    }
