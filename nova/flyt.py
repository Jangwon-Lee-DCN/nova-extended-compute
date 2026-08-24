# Copyright 2026 Soongsil University
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Fail-closed client for pre-scheduling FLYT service-port creation."""

from __future__ import annotations

import ssl
import urllib.error
import urllib.request

from oslo_log import log as logging
from oslo_serialization import jsonutils

import nova.conf
from nova import exception


CONF = nova.conf.CONF
LOG = logging.getLogger(__name__)


def enabled(flavor):
    return (
        CONF.flyt.enabled and
        flavor.extra_specs.get("flyt:enabled", "").lower() == "true"
    )


def prebuild(context, instance_uuid, flavor, image, availability_zone):
    endpoint = _endpoint("/v1/prebuild")
    properties = {
        key: value for key, value in image.get("properties", {}).items()
        if isinstance(key, str) and isinstance(value, str)
    }
    payload = {
        "instance_uuid": instance_uuid,
        "project_id": context.project_id,
        "user_id": context.user_id,
        "availability_zone": availability_zone or "default",
        "flavor": {
            "id": flavor.flavorid,
            "name": flavor.name,
            "extra_specs": dict(flavor.extra_specs),
        },
        "image": {
            "id": image.get("id") or image.get("image_id"),
            "checksum": image.get("checksum") or "catalog-lookup-required",
            "properties": properties,
        },
    }
    value = _request("POST", endpoint, payload)
    port = value.get("port")
    port_id = port.get("id") if isinstance(port, dict) else None
    if not isinstance(port_id, str) or not port_id:
        raise exception.InvalidRequest(
            reason="FLYT Adapter returned no managed Neutron port"
        )
    return port_id


def rollback(instance_uuid):
    try:
        _request("DELETE", _endpoint(f"/v1/prebuild/{instance_uuid}"), None)
    except exception.InvalidRequest:
        LOG.exception(
            "Failed to roll back FLYT pre-build port for %s", instance_uuid
        )


def _endpoint(path):
    if not CONF.flyt.adapter_endpoint or not CONF.flyt.adapter_token:
        raise exception.InvalidRequest(reason="FLYT Adapter is not configured")
    return CONF.flyt.adapter_endpoint.rstrip("/") + path


def _request(method, url, payload):
    body = None if payload is None else jsonutils.dumps(payload).encode()
    request = urllib.request.Request(
        url, data=body, method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CONF.flyt.adapter_token}",
        },
    )
    context = ssl.create_default_context(cafile=CONF.flyt.ca_file or None)
    try:
        with urllib.request.urlopen(
            request, timeout=CONF.flyt.timeout, context=context
        ) as response:
            raw = response.read(1024 * 1024)
            return jsonutils.loads(raw) if raw else {}
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        raise exception.InvalidRequest(
            reason=f"FLYT Adapter request failed: {error}"
        ) from error
