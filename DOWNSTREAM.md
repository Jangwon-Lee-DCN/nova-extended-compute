# Nova extended compute

This repository is a downstream of OpenStack Nova for integrations that need
narrow changes inside Nova's server-create and compute-runtime boundaries.
The Python distribution remains `nova`; the repository and image use the
`nova-extended-compute` name to distinguish the maintained downstream source.

## Remotes and branch model

- `upstream`: official `https://opendev.org/openstack/nova.git`
- `origin`: the maintained fork, once created
- base branch: `stable/2026.1`
- integration branches: one reviewable feature branch per capability

## Current downstream capability

The FLYT hook recognizes only Flavors with `flyt:enabled=true`. It assigns the
instance UUID before normal network validation, asks the external
OpenStack–FLYT Adapter to create an operator-managed service port, appends that
port to Nova's ordinary network request, and reuses the UUID during instance
provisioning. Non-FLYT requests retain the upstream path. Multi-create for a
FLYT Flavor fails closed because one managed port maps to one instance.

Nova does not own FLYT policy, GPU capacity, session reconciliation, or the
service network. Those responsibilities remain in `openstack-flyt-adapter`.
OpenStack service configuration and immutable image packaging remain in their
respective authoritative repositories.

## Validation

Focused tests live in `nova/tests/unit/test_flyt.py`. The downstream image build
also compiles the installed Nova tree and asserts the integration anchors.
Before rebasing, run the focused unit test and the applicable upstream compute
API tests. FLYT and future KubeVirt paths remain disabled by default.
