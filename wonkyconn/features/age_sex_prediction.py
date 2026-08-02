from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

import numpy as np
import pandas as pd
from joblib import parallel_backend
from nilearn.connectome import sym_matrix_to_vec
from numpy.typing import NDArray
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.model_selection import StratifiedShuffleSplit, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

if TYPE_CHECKING:
    from ..base import ConnectivityMatrix


@dataclass
class SiteRegressor(BaseEstimator, TransformerMixin):
    sites: NDArray[np.str_]

    model: LinearRegression = field(default_factory=LinearRegression)

    def _get_dummies(self: SiteRegressor, X: pd.DataFrame) -> pd.DataFrame:  # noqa: N803
        """
        Convert site labels to dummy variables.

        Args:
            X: A DataFrame containing the site labels.

        Returns:
            A DataFrame with dummy variables for each site.
        """
        return pd.get_dummies(self.sites[X.index], drop_first=False, dtype=np.float32)

    def fit(self: SiteRegressor, X: pd.DataFrame, y: pd.DataFrame | None = None) -> SiteRegressor:  # noqa: N803
        """
        Fit the site regressor to the connectivity data.

        Args:
            connectivity_data_site: A 2D array where the first n_connectivity_features columns
            are connectivity features and the remaining columns are site dummy variables.
            y: Ignored. This parameter exists for compatibility with the scikit-learn API.

        Returns:
            self: Returns the instance itself.
        """
        fit_sites = np.asarray(self.sites[X.index])
        if np.unique(fit_sites).size < 2:
            raise ValueError("SiteRegressor requires at least two sites in the training data.")

        y = X

        # Estimate coefficients on the training fold only
        self.model.fit(self._get_dummies(X), y)
        return self

    def transform(self: SiteRegressor, X: pd.DataFrame) -> pd.DataFrame:  # noqa: N803
        """
        Transform the connectivity data by regressing out site effects.
        Args:
            connectivity_data_site: A 2D array where the first n_connectivity_features columns
            are connectivity features and the remaining columns are site dummy variables.

        Returns:
            A 2D array of connectivity features with site effects regressed out.
        """
        return X - self.model.predict(self._get_dummies(X))


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
    connectivity_data_frame = pd.DataFrame(connectivity_data, dtype=np.float32)

    if task_type == "classification":
        y_train = pd.Series(LabelEncoder().fit_transform(target_labels))  # pyright: ignore[reportArgumentType, reportCallIssue]
        estimator = LogisticRegression(max_iter=5000, solver="saga", l1_ratio=0.0, random_state=random_state)

        bins = y_train

        scoring_metrics = {"accuracy": "accuracy", "roc_auc": "roc_auc"}
    else:
        y_train = pd.Series(target_labels)
        estimator = Ridge(alpha=1.0)

        bins = pd.qcut(y_train, q=5, labels=False, duplicates="drop")

        scoring_metrics = {"mae": "neg_mean_absolute_error", "r2": "r2"}

    if sites is not None:
        data_frame = pd.DataFrame({"site": sites, "bins": bins})
        # Get unique row indices as combined bins
        bins = data_frame.groupby(data_frame.columns.tolist(), sort=False).ngroup()

    cv_strategy = StratifiedShuffleSplit(n_splits=n_splits, test_size=0.2, random_state=random_state)
    splits = list(cv_strategy.split(np.zeros(len(bins)), bins))

    steps: list[tuple[str, BaseEstimator]] = [
        ("imputer", SimpleImputer(strategy="median").set_output(transform="pandas")),
    ]

    if sites is not None:
        steps.append(("site_regression", SiteRegressor(sites)))

    steps.extend(
        [
            ("scaler", StandardScaler()),
            (
                "pca",
                PCA(
                    n_components=n_pca,
                    svd_solver="randomized",
                    random_state=random_state,
                ),
            ),
            ("estimator", estimator),
        ]
    )

    pipe = Pipeline(steps)
    with parallel_backend("threading", n_jobs=n_jobs):
        cv_results = cross_validate(
            pipe,
            connectivity_data_frame,
            y_train,
            cv=splits,
            scoring=scoring_metrics,
            n_jobs=n_jobs,
            error_score="raise",
        )

    scores_df = pd.DataFrame({k.replace("test_", ""): v for k, v in cv_results.items() if k.startswith("test_")})
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
        "age_mae": float(-age_summary.loc["mae", "mean"]),  # type: ignore[arg-type, operator]
        "age_mae_ci_lower": float(-age_summary.loc["mae", "ci_upper"]),  # type: ignore[arg-type, operator]
        "age_mae_ci_upper": float(-age_summary.loc["mae", "ci_lower"]),  # type: ignore[arg-type, operator]
        "age_r2": float(age_summary.loc["r2", "mean"]),  # type: ignore[arg-type]
    }
