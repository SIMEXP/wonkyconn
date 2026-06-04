# Outputs

Wonkyconn writes a group-level a summary figure, metrics table, and {term}`DMN` similarity tables to the output directory.

> [!NOTE]
> Grouping columns depend on the input dataset and appear in the output table.

## `metrics.png`

A visual summary of the group-level metrics (see [`metrics.tsv`](#metricstsv)).

(metricstsv)=

## `metrics.tsv`

One row per group. Grouping fields are included as index columns.

- `seg` — {term}`Atlas` segmentation group, when present.
- `feature` — {term}`HALFpipe` feature group, when present.
- `atlas` — {term}`HALFpipe` {term}`atlas <Atlas>` group, when present.
- `median_absolute_qcfc` — Median absolute {term}`QC-FC` correlation across edges.
- `percentage_significant_qcfc` — Percentage of edges with significant {term}`QC-FC` correlation.
- `distance_dependence` — Correlation between {term}`QC-FC` values and inter-node distance.
- `gcor` — Global correlation (mean and SEM across subjects).
- `dmn_similarity_mean` — Mean correlation of individual connectivity patterns with the {term}`DMN` template.
- `dmn_similarity_std` — Standard deviation of {term}`DMN` similarity across subjects.
- `dmn_vis_distance_vs_dmn_fpn` — Paired t-statistic comparing {term}`DMN`-visual vs {term}`DMN`-FPN mean connectivity distance.
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
- `gradients_similarity` — {term}`Gradient similarity` to a reference.

> [!NOTE]
> In `--light-mode`, skipped age/sex and gradient metrics are left empty (`NaN`).

## `dmn_similarity_*.tsv`

Per-matrix {term}`DMN` similarity summaries. Current filenames:

- `dmn_similarity_seg.tsv` for {term}`BEP017`-style inputs.
- `dmn_similarity_feature-atlas.tsv` for {term}`HALFpipe` inputs.

- `mean_yeo7-1` through `mean_yeo7-7` — Mean connectivity summaries for each {term}`Yeo 7 network <Yeo 7 networks>`.
- `sd_yeo7-1` through `sd_yeo7-7` — Standard-deviation summaries for each {term}`Yeo 7 network <Yeo 7 networks>`.
- `corr_with_dmn` — Average correlation of seed-based connectivity patterns with the {term}`DMN` mask.
- `mean-diff_dmn_visual` — {term}`DMN`-visual connectivity difference.
- `mean-diff_dmn_fpn` — {term}`DMN`-FPN connectivity difference.

> [!WARNING]
> {term}`DMN` TSV filenames are format-based. Check output files carefully for multi-group runs.
