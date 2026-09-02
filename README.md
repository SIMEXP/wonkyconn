[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/HALFpipe/wonkyconn/main.svg)](https://results.pre-commit.ci/latest/github/HALFpipe/wonkyconn/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/wonkyconn/badge/?version=latest)](https://wonkyconn.readthedocs.io/en/latest/?badge=latest)

# wonkyconn

Wonkyconn evaluates residual motion and analytic quality in group-level fMRI connectomes and creates visualization reports to compare the generated metrics.

The project is based on the code of [`SIMEXP/fmriprep-denoise-benchmark`](https://github.com/SIMEXP/fmriprep-denoise-benchmark) and the publication by [Wang et al. 2024](http://dx.doi.org/10.1371/journal.pcbi.1011942).

**We are official at Beta stage and welcome user feedback!**

## Quick start

Fetch the most recent stable release:

```bash
apptainer build wonkyconn-26.9.0b0.sif docker://halfpipe/wonkyconn:26.9.0b0
```

Fetch the container matching the main branch:

```bash
apptainer build wonkyconn-edge.sif docker://halfpipe/wonkyconn:edge
```

See the [documentation](https://wonkyconn.readthedocs.io/) for usage, methods, and outputs.

## Textual GUI (optional)

- Install: `pip install "wonkyconn[textual]`
- Launch: `wonkyconn --textual`
- The CLI is required for headless batch jobs or multi-atlas runs.

> [!WARNING]
>
> - The textual UI requires an interactive terminal (TTY) if you are running Wonkyconn inside a non-interactive terminal (e.g., HPC batch job), use the CLI with `--textual`.
> - Current GUI supports one atlas entry. Use the CLI for multi-atlas runs.
