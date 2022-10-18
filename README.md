# Chaos Engineering Kill Pod Plugin for Arcaflow

This plugin implements the Kill Pod scenario used by redhat-chaos/krkn for
Chaos Engineering experiments on Kubernetes.

## Testing

For testing this plugin you need a kubernets instance. Within CI we are using [KinD](https://kind.sigs.k8s.io/).

The test is going to read your kubeconfig file which defaults to `~/.kube/config`.

```console
pip install coverage
pip install -r requirements.txt
python -m coverage run -a -m unittest discover -s tests -v
python -m coverage html
```
