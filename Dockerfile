FROM ghcr.io/prefix-dev/pixi:0.70.2 AS build

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies before the package itself to leverage caching
WORKDIR /app
COPY pixi.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --environment wonkyconn --environment test --frozen --skip wonkyconn

# Note that PATH gets hard-coded. Remove it and re-apply in final image
RUN pixi shell-hook --environment wonkyconn --as-is | grep --invert-match PATH > /shell-hook.sh
RUN pixi shell-hook --environment test --as-is | grep --invert-match PATH > /test-shell-hook.sh

# Finally, install the package
COPY LICENSE README.md /app/
COPY wonkyconn/ /app/wonkyconn/
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --environment wonkyconn --environment test --frozen

# base version
FROM ubuntu:rolling AS base

RUN useradd --create-home --shell /bin/bash --groups users wonkyconn
WORKDIR /home/wonkyconn
ENV HOME="/home/wonkyconn"

# test version
FROM base AS test

COPY --link --from=build /app/.pixi/envs/test /app/.pixi/envs/test
RUN --mount=type=bind,from=build,source=/test-shell-hook.sh,target=/shell-hook.sh \
    cat /shell-hook.sh >> "${HOME}/.bashrc"
ENV PATH="/app/.pixi/envs/test/bin:$PATH"

# production version
FROM base AS wonkyconn

COPY --link --from=build /app/.pixi/envs/wonkyconn /app/.pixi/envs/wonkyconn
RUN --mount=type=bind,from=build,source=/shell-hook.sh,target=/shell-hook.sh \
    cat /shell-hook.sh >> "${HOME}/.bashrc"
ENV PATH="/app/.pixi/envs/wonkyconn/bin:$PATH"

ENTRYPOINT ["wonkyconn"]
