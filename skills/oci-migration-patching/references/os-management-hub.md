# OS Management Hub and Ksplice

The old oci os-management group was removed in CLI 3.65; use os-management-hub. Distinguish managed instances/groups, software sources, lifecycle stages/environments, profiles, management stations and scheduled jobs.
An empty managed-instance list means no visible registered instances, not no running hosts. Check Oracle Cloud Agent plugin, registration/profile, dynamic-group policy, source reachability and management-station health before patch diagnosis. Agent onboarding, inventory refresh and source changes are mutations.
Build a patch proposal from available updates, errata, source version, application compatibility, reboot requirements and a representative canary. Schedule bounded batches in an approved maintenance window with stop thresholds and service health checks. Ksplice eligibility and kernel/userspace coverage are specific; do not guarantee reboot-free completion.
Compartment-wide update-all-packages-in-compartment and install-all-windows-updates-in-compartment have a broad blast radius without an individual target OCID. Never execute them from a vague fleet request.
Rollback may require boot/recovery image, package compatibility and application/database recovery; package downgrade is not universally safe. Capture prechange versions, recovery access and backup evidence before approval. No patch or reboot was attempted.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
