FROM quay.io/centos/centos:stream8

RUN dnf -y module install python39 && dnf -y install python39 python39-pip
RUN mkdir /app
ADD https://raw.githubusercontent.com/arcalot/arcaflow-plugins/main/LICENSE /app
ADD arcaflow_plugin_kill_pod.py /app
ADD requirements.txt /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/app/arcaflow_plugin_kill_pod.py"]
CMD []

LABEL org.opencontainers.image.source="https://github.com/arcalot/arcaflow-plugin-kill-pod"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-2.0-only"
LABEL org.opencontainers.image.vendor="Arcalot project"
LABEL org.opencontainers.image.authors="Arcalot contributors"
LABEL org.opencontainers.image.title="Chaos Engineering Kill Pod Plugin for Arcaflow"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
