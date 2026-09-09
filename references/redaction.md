Purpose: what never leaves the workspace — redact these before they reach a file, log, commit, or chat.
Source: research/{04b-iam-security-cost-freetier,04c-core-services-pitfalls,08a-oracle-database-agents,08c-iac-terraform-rm-ansible,A4-audit-codex-catalog}.md; generated 2026-09-08; verified-on CLI 3.91.0

## Never write it down

| Value | Where it appears | Write instead |
|---|---|---|
| Full OCID (tenancy, compartment, user) | every `list`/`get` | `ocid1.<type>...redacted` |
| PAR `access-uri` | `os preauth-request create` response (shown once); a bearer credential | bucket, prefix, expiry |
| Secret bundle content | `secrets secret-bundle get`, base64 or decoded | secret name + stage |
| Wallets, private keys, API signing keys | ADB wallet zip, `~/.oci/*.pem` | the path, not the bytes |
| `data."ssh-metadata".command` | `bastion session get` | same string, OCID redacted |
| Instance metadata / `user_data` | `compute instance get`, cloud-init, `ssh_authorized_keys` | say it exists, not the body |
| Terraform/RM state, plan, job logs | `.tfstate`, `job get-job-tf-state` | resource types + counts |
| Session tokens, `Bearer ...`, passwords, api keys | `security_token` auth, headers, error bodies | `[redacted]` |

## Rules
- Redact on exit: `scripts/redact.py`, in `oci_ro`, rewrites OCIDs, `PRIVATE KEY` blocks, `Bearer`, `password|token|access-uri|api-key` pairs and PAR `/p/<secret>/n/` paths. Never add a second redactor.
- Never pass `--debug`; it leaks request-signing detail; `oci_ro` never injects it.
- Redaction is not a permission: never grant `read secret-bundles` (plaintext secret); `read secret-family` is metadata-only; `inspect policies` discloses policy text.
- Type + name + redacted OCID names a finding; a leak cannot be undone.

## Links
- [PARs](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingpreauthenticatedrequests.htm) · [Secrets](https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Tasks/managingsecrets.htm) (200, 2026-09-08)
