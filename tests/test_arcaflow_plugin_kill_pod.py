import random
import re
import string
import threading
import unittest

from arcaflow_plugin_sdk import plugin
from kubernetes import client
from kubernetes.client import (ApiException, V1Container, V1ObjectMeta, V1Pod,
                               V1PodSpec, V1SeccompProfile,
                               V1SecurityContext, V1Capabilities)

import arcaflow_plugin_kill_pod


class KillPodTest(unittest.TestCase):
    def test_serialization(self):
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.KillPodConfig(
                namespace_pattern=re.compile(".*"), name_pattern=re.compile(".*")
            ),
            self.fail,
        )
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.PodKillSuccessOutput(pods={}),
            self.fail,
        )
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.PodErrorOutput(error="Hello world!"),
            self.fail,
        )

    def test_not_enough_pods(self):
        name = "".join(random.choices(string.ascii_lowercase, k=8))
        output_id, output_data = arcaflow_plugin_kill_pod.kill_pods(
            arcaflow_plugin_kill_pod.KillPodConfig(
                namespace_pattern=re.compile("^default$"),
                name_pattern=re.compile("^unit-test-" + re.escape(name) + "$"),
            )
        )
        if output_id != "error":
            self.fail("Not enough pods did not result in an error.")
        print(output_data.error)

    def test_kill_pod(self):
        with arcaflow_plugin_kill_pod.setup_kubernetes(None) as cli:
            core_v1 = client.CoreV1Api(cli)
            pod = core_v1.create_namespaced_pod("default", V1Pod(
                metadata=V1ObjectMeta(
                    generate_name="test-",
                ),
                spec=V1PodSpec(
                        security_context=V1SecurityContext(
                                    run_as_non_root=True,
                                    run_as_group=3000,
                                    run_as_user=2000
                                ),
                        containers=[
                            V1Container(
                                name="test",
                                image="alpine",
                                tty=True,
                                security_context=V1SecurityContext(
                                    run_as_non_root=True,
                                    seccomp_profile=V1SeccompProfile(type="RuntimeDefault"),
                                    allow_privilege_escalation=False,
                                    capabilities=V1Capabilities(drop=["ALL"])
                                )
                            )
                        ]
                    )
                )
            )
            pods = arcaflow_plugin_kill_pod._find_pods(core_v1, None,
                                namespace_pattern=re.compile("^default$"),
                                name_pattern=re.compile(
                                "^" + re.escape(pod.metadata.name) + "$"
                            ))
            print("pods " + str(pods))
            while len(pods) == 0:
                pods = arcaflow_plugin_kill_pod._find_pods(core_v1, None, namespace_pattern=re.compile("^default$"),
                            name_pattern=re.compile(
                            "^" + re.escape(pod.metadata.name) + "$"
                    ))
                print("pods " + str(pods))

            def remove_test_pod():
                try:
                    core_v1.delete_namespaced_pod(
                        pod.metadata.name, pod.metadata.namespace
                    )
                except ApiException as e:
                    if e.status != 404:
                        raise

            self.addCleanup(remove_test_pod)

            output_id, output_data = arcaflow_plugin_kill_pod.kill_pods(
                arcaflow_plugin_kill_pod.KillPodConfig(
                    namespace_pattern=re.compile("^default$"),
                    name_pattern=re.compile("^" + re.escape(pod.metadata.name) + "$"),
                )
            )

            if output_id == "error":
                self.fail(output_data.error)
            self.assertIsInstance(
                output_data, arcaflow_plugin_kill_pod.PodKillSuccessOutput
            )
            out: arcaflow_plugin_kill_pod.PodKillSuccessOutput = output_data
            self.assertEqual(1, len(out.pods))
            pod_list = list(out.pods.values())

            self.assertEqual(pod.metadata.name, pod_list[0].name)

            try:
                core_v1.read_namespaced_pod(pod_list[0].name, pod_list[0].namespace)
                self.fail("Killed pod is still present.")
            except ApiException as e:
                if e.status != 404:
                    self.fail("Incorrect API exception encountered: {}".format(e))


class WaitForPodTest(unittest.TestCase):
    def test_serialization(self):
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.WaitForPodsConfig(
                namespace_pattern=re.compile(".*"), name_pattern=re.compile(".*")
            ),
            self.fail,
        )
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.WaitForPodsConfig(
                namespace_pattern=re.compile(".*"), label_selector="app=nginx"
            ),
            self.fail,
        )
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.PodWaitSuccessOutput(pods=[]),
            self.fail,
        )
        plugin.test_object_serialization(
            arcaflow_plugin_kill_pod.PodErrorOutput(error="Hello world!"),
            self.fail,
        )

    def test_timeout(self):
        name = "watch-test-" + "".join(random.choices(string.ascii_lowercase, k=8))
        output_id, output_data = arcaflow_plugin_kill_pod.wait_for_pods(
            arcaflow_plugin_kill_pod.WaitForPodsConfig(
                namespace_pattern=re.compile("^default$"),
                name_pattern=re.compile("^" + re.escape(name) + "$"),
                timeout=1,
            )
        )
        self.assertEqual("error", output_id)

    def test_watch(self):
        with arcaflow_plugin_kill_pod.setup_kubernetes(None) as cli:
            core_v1 = client.CoreV1Api(cli)
            name = "watch-test-" + "".join(random.choices(string.ascii_lowercase, k=8))

            def create_test_pod():
                core_v1.create_namespaced_pod("default", V1Pod(
                    metadata=V1ObjectMeta(
                        name=name
                    ),
                    spec=V1PodSpec(
                        security_context=V1SecurityContext(
                                    run_as_non_root=True,
                                    run_as_group=3000,
                                    run_as_user=2000
                                ),
                        containers=[
                            V1Container(
                                name="test",
                                image="alpine",
                                tty=True,
                                security_context=V1SecurityContext(
                                    run_as_non_root=True,
                                    seccomp_profile=V1SeccompProfile(type="RuntimeDefault"),
                                    allow_privilege_escalation=False,
                                    capabilities=V1Capabilities(drop=["ALL"])
                                )
                            )
                        ]
                    ),
                    )
                )

            def remove_test_pod():
                try:
                    core_v1.delete_namespaced_pod(name, "default")
                except ApiException as e:
                    if e.status != 404:
                        raise

            self.addCleanup(remove_test_pod)

            t = threading.Timer(10, create_test_pod)
            t.start()

            output_id, output_data = arcaflow_plugin_kill_pod.wait_for_pods(
                arcaflow_plugin_kill_pod.WaitForPodsConfig(
                    namespace_pattern=re.compile("^default$"),
                    name_pattern=re.compile("^" + re.escape(name) + "$"),
                    timeout=60,
                )
            )
            self.assertEqual("success", output_id)


if __name__ == '__main__':
    unittest.main()
