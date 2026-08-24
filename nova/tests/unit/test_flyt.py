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

from unittest import mock

from nova import exception
from nova import flyt
from nova import test


class FlytIntegrationTest(test.NoDBTestCase):

    def setUp(self):
        super().setUp()
        self.flags(
            enabled=True,
            adapter_endpoint="https://adapter.invalid",
            adapter_token="development-service-token",
            group="flyt",
        )
        self.context = mock.Mock(project_id="project-1", user_id="user-1")
        self.flavor = mock.Mock(
            flavorid="flavor-1",
            name="flyt.small",
            extra_specs={"flyt:enabled": "true", "flyt:profile": "gpu-small"},
        )
        self.image = {
            "id": "image-1",
            "checksum": "checksum-1",
            "properties": {"flyt:injectable": "true"},
        }

    def test_enabled_requires_global_switch_and_flavor_property(self):
        self.assertTrue(flyt.enabled(self.flavor))
        self.flags(enabled=False, group="flyt")
        self.assertFalse(flyt.enabled(self.flavor))
        self.flags(enabled=True, group="flyt")
        self.flavor.extra_specs = {}
        self.assertFalse(flyt.enabled(self.flavor))

    @mock.patch.object(flyt, "_request")
    def test_prebuild_uses_default_network_when_az_is_omitted(self, request):
        request.return_value = {"port": {"id": "port-1"}}
        self.assertEqual(
            "port-1",
            flyt.prebuild(
                self.context, "instance-1", self.flavor, self.image, None
            ),
        )
        payload = request.call_args.args[2]
        self.assertEqual("default", payload["availability_zone"])
        self.assertEqual("instance-1", payload["instance_uuid"])

    @mock.patch.object(flyt, "_request")
    def test_prebuild_rejects_response_without_managed_port(self, request):
        request.return_value = {"eligible": True}
        self.assertRaises(
            exception.InvalidRequest,
            flyt.prebuild,
            self.context,
            "instance-1",
            self.flavor,
            self.image,
            "az1",
        )

    @mock.patch.object(flyt, "_request")
    def test_rollback_is_idempotent_at_nova_boundary(self, request):
        flyt.rollback("instance-1")
        request.assert_called_once_with(
            "DELETE",
            "https://adapter.invalid/v1/prebuild/instance-1",
            None,
        )

    def test_missing_adapter_configuration_fails_closed(self):
        self.flags(adapter_endpoint=None, group="flyt")
        self.assertRaises(
            exception.InvalidRequest,
            flyt.prebuild,
            self.context,
            "instance-1",
            self.flavor,
            self.image,
            "az1",
        )
