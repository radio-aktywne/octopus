ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg git

# install poetry
COPY ./requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# create new environment
# see: https://jcristharif.com/conda-docker-tips.html
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emistream", "/bin/bash", "-c"]

# add poetry files
COPY ./emistream/pyproject.toml ./emistream/poetry.lock /tmp/emistream/
WORKDIR /tmp/emistream

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root && \
    rm -rf ~/.cache/pypoetry

# add source and necessary files
COPY ./emistream/src/ /tmp/emistream/src/
COPY ./emistream/LICENSE ./emistream/README.md /tmp/emistream/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emistream

ENV EMISTREAM_PORT=10000 \
    EMISTREAM_LIVE_HOST=localhost \
    EMISTREAM_LIVE_PORT=9000 \
    EMISTREAM_RECORDING_HOST=localhost \
    EMISTREAM_RECORDING_PORT=31000

EXPOSE 10000
EXPOSE 10000/udp

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "emistream", "emistream", "--port", "10000"]
