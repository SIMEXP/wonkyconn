# Installation

Use the container unless you need a development install.

## Container installation

Build the latest container image (`halfpipe/wonkyconn:edge`) or a specific tag available on [docker hub](https://hub.docker.com/r/halfpipe/wonkyconn/tags).

[Apptainer](https://apptainer.org/docs/user/latest/) (**recommended**):

```bash
apptainer build wonkyconn-edge.simg docker://halfpipe/wonkyconn:edge
```

> [!tip]
> Apptainer was formerly known as Sinfularity. If you have an older version of Singularity, you can use the same command but replace `apptainer` with `singularity`.

[Docker](https://docs.docker.com/):

```bash
docker pull halfpipe/wonkyconn:edge
```

## Source installation

Install from Git:

```bash
pip install git+https://github.com/HALFpipe/wonkyconn.git
```

Install a specific tag:

```bash
pip install "wonkyconn @ git+https://github.com/HALFpipe/wonkyconn.git@26.02.0-alpha"
```
