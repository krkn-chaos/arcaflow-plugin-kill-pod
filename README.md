# Chaos Engineering Kill Pod Plugin for Arcaflow

This plugin implements the Kill Pod scenario used by [redhat-chaos/krkn](https://github.com/redhat-chaos/krkn)
for Chaos Engineering experiments on Kubernetes.

## Testing

For testing this plugin you need a kubernets instance. Within CI we are using [KinD](https://kind.sigs.k8s.io/).

The test is going to read your kubeconfig file which defaults to `~/.kube/config`.

The code requires Python >= 3.9 in order to work.

```console
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
poetry run python -m coverage run -a -m unittest discover -s tests -v
poetry run python -m coverage html
```
