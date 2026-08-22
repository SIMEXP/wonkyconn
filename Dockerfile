FROM ghcr.io/prefix-dev/pixi:0.70.2 AS build

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app
COPY pixi.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --environment wonkyconn --environment test --frozen

# Extract shell hooks and remove PATH (will be set in final stages)
RUN pixi shell-hook --environment wonkyconn --as-is | grep -v PATH > /wonkyconn-hook.sh
RUN pixi shell-hook --environment test --as-is | grep -v PATH > /test-hook.sh

# Install the package
COPY LICENSE README.md ./
COPY wonkyconn/ ./wonkyconn/
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --environment wonkyconn --environment test --frozen

# Base image
FROM ubuntu:rolling AS base

RUN useradd --create-home --shell /bin/bash --groups users wonkyconn
WORKDIR /home/wonkyconn
ENV HOME="/home/wonkyconn"

# Test image
FROM base AS test

COPY --link --from=build /app/.pixi/envs/test /app/.pixi/envs/test
RUN cat /wonkyconn-hook.sh >> /dev/null && \
    echo 'source /app/.pixi/envs/test/bin/activate' >> "${HOME}/.bashrc"
ENV PATH="/app/.pixi/envs/test/bin:$PATH"

# Production image
FROM base AS wonkyconn

COPY --link --from=build /app/.pixi/envs/wonkyconn /app/.pixi/envs/wonkyconn
RUN echo 'source /app/.pixi/envs/wonkyconn/bin/activate' >> "${HOME}/.bashrc"
ENV PATH="/app/.pixi/envs/wonkyconn/bin:$PATH"

ENTRYPOINT ["wonkyconn"]
