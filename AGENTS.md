# Nova extended compute downstream contract

Read `/home/ubuntu/AGENTS.md` first. This repository owns downstream Nova
source changes and their unit/functional tests for compute-runtime and external
resource integrations. It does not own OpenStack service configuration,
immutable image construction, live topology, or FLYT server implementation.

- Keep `upstream` pointed at official OpenStack Nova and track its stable branch.
- Use `origin` for the maintained fork once that remote exists.
- Preserve non-FLYT Nova behavior and fail closed only for an explicitly
  FLYT-enabled Flavor.
- Integration code in Nova must remain narrow: request recognition, lifecycle
  hook invocation, managed-port attachment, and rollback. Policy, capacity,
  Neutron resource ownership, and session reconciliation belong to the
  external Adapter.
- Every downstream hook requires focused unit tests plus an exact upstream
  rebase/applicability check. Do not enable unfinished FLYT or KubeVirt paths by
  default.
