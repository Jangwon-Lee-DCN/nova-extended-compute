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

"""Configuration for the OpenStack-FLYT pre-build integration."""

from oslo_config import cfg


flyt_group = cfg.OptGroup("flyt", title="Remote FLYT GPU integration")

OPTS = [
    cfg.BoolOpt("enabled", default=False),
    cfg.URIOpt("adapter_endpoint"),
    cfg.StrOpt("adapter_token", secret=True),
    cfg.FloatOpt("timeout", default=5.0, min=0.1),
    cfg.StrOpt("ca_file"),
]


def register_opts(conf):
    conf.register_group(flyt_group)
    conf.register_opts(OPTS, group=flyt_group)


def list_opts():
    return {flyt_group: OPTS}
