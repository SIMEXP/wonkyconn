# Usage

Wonkyconn runs group-level analyses on datasets with timeseries files and connectivity matrices.

## Run with Apptainer (recommended)

Build the latest container image (`edge`) or a specific tag available on [docker hub](https://hub.docker.com/r/halfpipe/wonkyconn/tags):

```bash
VERSION="edge" apptainer build wonkyconn-${VERSION}.sif docker://halfpipe/wonkyconn:${VERSION}
```

Run with explicit host-path bindings:

```bash
BIDS_DIR="/path/to/halfpipe/derivatives"
OUTPUT_DIR="/path/to/wonkyconn_output"
PHENOTYPES="/path/to/participants.tsv"
ATLAS_PATH="/path/to/atlas-Schaefer2018Combined_dseg.nii.gz"
SIF_IMG="/path/to/wonkyconn.sif"

apptainer run --contain --cleanenv \
    --bind ${BIDS_DIR} \
    --bind ${ATLAS_PATH} \
    --bind ${OUTPUT_DIR} \
    ${SIF_IMG} ${BIDS_DIR} ${OUTPUT_DIR} group \
    --phenotypes ${PHENOTYPES} \
    --atlas Schaefer2018Combined ${ATLAS_PATH}
```

> [!IMPORTANT]
>
> - Your `phenotype.tsv` file must include `participant_id`, `age`, and `gender` columns.
> - Wonkyconn expects the input folder to be named `derivatives/halfpipe`.
> - Mount every directory the container needs with `--bind`, for example `--bind /path/to/atlas:atlas`.
> - For `--atlas`, use the same atlas name used in HALFpipe, as shown in filenames such as `sub-xxx_task-xxx_feature-xxx_atlas-NAME_desc-correlation.tsv`.

## Textual user-interface

You can run wonkyconn with a textual user-interface, using the `--textual` flag, to select the input files and options interactively. This is useful for users who are new to the command line or want to explore the options before running the analysis.

First, you must install the optional dependencies:

```bash
pip install "wonkyconn[textual] @ git+https://github.com/HALFpipe/wonkyconn.git"
```

> [!WARNING]
> Requires an interactive terminal.

> [!WARNING]
> Current GUI supports one atlas entry. Use the CLI for multi-atlas runs.

## Command line interface

```{eval-rst}
.. argparse::
   :prog: wonkyconn
   :module: wonkyconn.run
   :func: global_parser
```
