# build poetry
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-buildbase:0.4.2 as build

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
COPY arcaflow_plugin_kill_pod.py /app
COPY README.md /app/

RUN python3.9 -m pip install poetry \
 # FIX per https://github.com/python-poetry/poetry/issues/5977
 && python3.9 -m poetry add certifi \
 && python3.9 -m poetry config virtualenvs.create false \
 && python3.9 -m poetry install --without dev \
 && python3.9 -m poetry export -f requirements.txt --output requirements.txt --without-hashes

# run tests
# FIXME cannot execute tests without injecting the cluster kubeconfig
#COPY tests /app/tests
#RUN pip3 install coverage
#RUN python3.9 -m coverage run tests/test_arcaflow_plugin_kill_pod.py
#RUN python3.9 -m coverage html -d /htmlcov --omit=/usr/local/*

#final image
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-osbase:0.4.2

WORKDIR /app

COPY --from=build /app/requirements.txt /app/
COPY --from=build /htmlcov /htmlcov/
COPY LICENSE /app/
COPY README.md /app/
COPY arcaflow_plugin_kill_pod.py /app

RUN python3.9 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "arcaflow_plugin_kill_pod.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/redhat-chaos/arcaflow-plugin-kill-pod"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Chaos Engineering Kill Pod Plugin for Arcaflow"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
