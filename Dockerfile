# build poetry
FROM quay.io/centos/centos:stream8 as poetry
RUN dnf -y module install python39 && dnf -y install python39 python39-pip
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
COPY arcaflow_plugin_kill_pod.py /app
COPY README.md /app/

RUN python3.9 -m pip install poetry \
 && python3.9 -m poetry config virtualenvs.create false \
 && python3.9 -m poetry install --without dev \
 && python3.9 -m poetry export -f requirements.txt --output requirements.txt --without-hashes

# run tests
COPY tests /app/tests

# FIXME -- Tests do not currently pass
#RUN mkdir /htmlcov
#RUN pip3 install coverage
#RUN python3 -m coverage run tests/test_arcaflow_plugin_kill_pod.py
#RUN python3 -m coverage html -d /htmlcov --omit=/usr/local/*

#final image
FROM quay.io/centos/centos:stream8
RUN dnf -y module install python39 && dnf -y install python39 python39-pip
WORKDIR /app

COPY --from=poetry /app/requirements.txt /app/
#COPY --from=poetry /htmlcov /htmlcov/
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
