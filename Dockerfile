FROM quay.io/centos/centos:stream8

RUN dnf -y module enable python39 && dnf --setopt=tsflags=nodocs -y install python39-3.9.7 python39-pip-20.2.4 && dnf clean all
RUN mkdir /app
ADD https://raw.githubusercontent.com/arcalot/arcaflow-plugin-template-python/main/LICENSE /app
COPY README.md /app/
COPY arcaflow_plugin_kill_pod.py /app
COPY poetry.lock pyproject.toml /app/
WORKDIR /app

RUN pip3 install --no-cache-dir poetry==1.2.2 && \
    poetry config virtualenvs.create false && \
    poetry install --only main

ENTRYPOINT ["python3", "/app/arcaflow_plugin_kill_pod.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugin-kill-pod"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Chaos Engineering Kill Pod Plugin for Arcaflow"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
