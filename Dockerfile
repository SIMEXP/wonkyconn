FROM ghcr.io/prefix-dev/pixi:0.70.2 AS build

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

# Copy everything needed for the build upfront
COPY pixi.lock pyproject.toml LICENSE README.md ./
COPY wonkyconn/ ./wonkyconn/

# Install all dependencies and build the package in one go
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --environment wonkyconn --environment test --frozen

# Base runtime image
FROM ubuntu:rolling AS base

RUN useradd --create-home --shell /bin/bash --groups users wonkyconn
WORKDIR /home/wonkyconn
ENV HOME="/home/wonkyconn"

# Test environment
FROM base AS test

COPY --link --from=build /app/.pixi/envs/test /app/.pixi/envs/test
ENV PATH="/app/.pixi/envs/test/bin:$PATH"

# Production environment
FROM base AS wonkyconn

COPY --link --from=build /app/.pixi/envs/wonkyconn /app/.pixi/envs/wonkyconn
ENV PATH="/app/.pixi/envs/wonkyconn/bin:$PATH"

ENTRYPOINT ["wonkyconn"]
