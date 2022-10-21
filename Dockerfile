ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg git

WORKDIR /app/

# install poetry
COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r ./requirements.txt

# create new environment
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yaml ./environment.yaml
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda env create -f ./environment.yaml

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emistream", "/bin/bash", "-c"]

WORKDIR /app/emistream/

# add poetry files
COPY ./emistream/pyproject.toml ./emistream/poetry.lock ./

FROM base AS test

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main,test

# add source, tests and necessary files
COPY ./emistream/src/ ./src/
COPY ./emistream/tests/ ./tests/
COPY ./emistream/LICENSE ./emistream/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emistream

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "pytest"]
CMD []

FROM base AS production

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

# add source and necessary files
COPY ./emistream/src/ ./src/
COPY ./emistream/LICENSE ./emistream/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emistream

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENV EMISTREAM_HOST=0.0.0.0 \
    EMISTREAM_PORT=10000 \
    EMISTREAM_FUSION__HOST=localhost \
    EMISTREAM_FUSION__PORT=9000 \
    EMISTREAM_EMIRECORDER__HOST=localhost \
    EMISTREAM_EMIRECORDER__PORT=31000 \
    EMISTREAM_TIMEOUT=60

EXPOSE 10000
EXPOSE 10000/udp

ENTRYPOINT ["./entrypoint.sh", "emistream"]
CMD []
