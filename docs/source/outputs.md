# Outputs

Wonkyconn writes a group-level a summary figure, metrics table, and DMN similarity tables to the output directory.

> [!NOTE]
> Grouping columns depend on the input dataset and appear in the output table.

## `metrics.png`

A visual summary of the group-level metrics (see [`metrics.tsv`](#metricstsv)).

## `metrics.tsv`

One row per group. Grouping fields are included as index columns.

- `seg` — Atlas segmentation group, when present.
- `feature` — HALFpipe feature group, when present.
- `atlas` — HALFpipe atlas group, when present.
- `median_absolute_qcfc` — Median absolute QC-FC correlation across edges.
- `percentage_significant_qcfc` — Percentage of edges with significant QC-FC correlation.
- `distance_dependence` — Correlation between QC-FC values and inter-node distance.
- `gcor` — Global correlation (mean and SEM across subjects).
- `dmn_similarity_mean` — Mean correlation of individual connectivity patterns with the DMN template.
- `dmn_similarity_std` — Standard deviation of DMN similarity across subjects.
- `dmn_vis_distance_vs_dmn_fpn` — Paired t-statistic comparing DMN-visual vs DMN-FPN mean connectivity distance.
- `confound_regression_percentage` — Estimated percentage of model DoF associated with confound regression.
- `motion_scrubbing_percentage` — Estimated percentage of model DoF associated with motion scrubbing.
- `nonsteady_states_detector_percentage` — Estimated percentage of model DoF associated with non-steady-state volume removal.
- `sex_auc` — AUC for sex classification from connectivity (with CI bounds).
- `sex_auc_ci_lower` — Lower confidence interval bound for sex AUC.
- `sex_auc_ci_upper` — Upper confidence interval bound for sex AUC.
- `sex_accuracy` — Accuracy for sex classification.
- `age_mae` — Mean absolute error for age prediction from connectivity (with CI bounds).
- `age_mae_ci_lower` — Lower confidence interval bound for age MAE.
- `age_mae_ci_upper` — Upper confidence interval bound for age MAE.
- `age_r2` — {math}`R^2` for age prediction.
- `gradients_similarity` — Similarity of group-level connectivity gradients to a reference.

> [!NOTE]
> In `--light-mode`, skipped age/sex and gradient metrics are left empty (`NaN`).

## `dmn_similarity_*.tsv`

Per-subject DMN similarity statistics, including within-network mean connectivity, standard deviation, and correlation with the DMN template for each Yeo 7 network.
