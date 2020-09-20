import logging
import math
from base64 import b64decode
from binascii import Error as Base64DecodingError
from pathlib import Path
from tempfile import NamedTemporaryFile

import bitmath
from urllib3.exceptions import MaxRetryError

import kubernetes.client as client
from kubernetes.client.rest import ApiException
from vim_adaptor.exceptions import VimConnectionError
from vim_adaptor.models.vims import KubernetesVim

logging.getLogger("urllib3.connection").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def get_resource_utilization(vim: KubernetesVim):

    config = client.Configuration()
    config.host = vim.url
    config.api_key = {"authorization": "Bearer " + vim.service_token}

    try:
        ca_cert = b64decode(vim.ccc, validate=True)
    except (Base64DecodingError, ValueError):
        raise VimConnectionError(
            "Error decoding the cluster CA certificate. "
            "Make sure it is a valid base64-encoded string."
        )

    # Write ca certificate to a temp file for urllib
    ca_cert_file = NamedTemporaryFile(mode="w+b", delete=False)
    ca_cert_file.write(ca_cert)
    ca_cert_file_path = Path(ca_cert_file.name)
    ca_cert_file.close()

    config.verify_ssl = True
    config.ssl_ca_cert = ca_cert_file_path

    try:
        api = client.CoreV1Api(client.ApiClient(config))

        cores_total = 0
        cores_used = 0
        memory_total = bitmath.MB()
        memory_used = bitmath.MB()

        # Aggregate available resources for all nodes
        for node in api.list_node().items:
            allocatable = node.status.allocatable
            cores_total += float(allocatable["cpu"])
            memory_total += bitmath.parse_string_unsafe(allocatable["memory"])

        # Aggregate resource requests for all containers in all pods (like `kubectl
        # describe nodes` does)
        for pod in api.list_pod_for_all_namespaces().items:
            for container in pod.spec.containers:
                resource_requests = container.resources.requests
                if resource_requests is not None:
                    if "cpu" in resource_requests:
                        cores_used += (
                            float(resource_requests["cpu"].replace("m", "")) / 1000
                        )
                    if "memory" in resource_requests:
                        memory_used += bitmath.parse_string_unsafe(
                            resource_requests["memory"]
                        )

        return {
            "cores": {"used": round(cores_used, 3), "total": cores_total},
            "memory": {
                "used": math.ceil(memory_used.value),
                "total": math.floor(memory_total.value),
            },
        }

    except (ApiException, MaxRetryError) as e:
        if isinstance(e, ApiException) and str(e).startswith("(401)"):
            raise VimConnectionError(
                "Authorization error. Please check the service token."
            )
        raise VimConnectionError(str(e))
    finally:
        # Remove the temporary ca certificate
        ca_cert_file_path.unlink()
