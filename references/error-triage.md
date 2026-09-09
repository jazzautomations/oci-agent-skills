Purpose: recognise an OCI failure from its text alone — which envelope, which field to branch on, whether to retry — and route to the corpus entry with the fix.
Source: research/14-error-corpus.md §1, §3, §15, §16, §17; generated 2026-09-08; verified-on CLI 3.91.0.

## Contents
1. Envelope triage — the four output shapes
2. Regex quick-reference — dispatcher discriminators
3. Decision tree — status to next action
4. The 401 / 403 / 404 ladder
5. Retryability + `error-corpus.json` (125 entries)

## 1. Envelope triage

Four shapes. Only tier 4 carries an `opc-request-id`, and only part of it is retryable [verified — reproduced].

| Tier | Prefix | Meaning -> action |
|---|---|---|
| 1 | `Usage: oci ...` + `Error: Missing option(s)` | click rejected the args pre-HTTP -> fix locally, no retry |
| 2 | `ERROR:` + `+Config Errors+` table | `~/.oci/config` wrong -> fix it, no retry |
| 3 | `RequestException: {` | never left the host; `"target_service":"CLI"` + `"request_endpoint": null` -> check region, DNS, egress, proxy |
| 4 | `ServiceError: {` | the service answered -> parse the JSON, then §3 |

Tier-4 fields, by priority:

| Field | Why |
|---|---|
| `code` | machine identity — branch on this, not `message` |
| `status` | disambiguates same-named codes (`InvalidParameter` is 400 *and* 404) |
| `target_service` | which service doc / policy verb applies |
| `operation_name` | snake_case op -> permission + API ref page |
| `request_endpoint` | the region actually used |
| `opc-request-id` | only handle Support can act on — capture BEFORE retrying |

## 2. Regex quick-reference

Highest-value discriminators. `envelope_regexes` (12 keys) holds envelope shapes
only; the rest are per-entry `regex` fields across the 125 entries:

```
^ServiceError:\s*\{ -> service error, parse JSON
^RequestException:\s*\{ -> never left the host
^Usage: oci .+\nError: Missing option\(s\) -> local usage bug
^ERROR: Could not find config file at (.+)$ -> config missing
^ERROR: Profile '([^']+)' not found -> profile missing
^ERROR: No security_token_file was found in config -> wrong auth mode
This CLI session has expired -> oci session refresh
FileNotFoundError: \[Errno 2\].*\.pem -> key_file path wrong
(?i)out of host capacity -> vary AD/FD/shape, do NOT retry
User-rate limit exceeded -> backoff + jitter
^│ Error: (\d{3})-(\w+), (.*)$ -> terraform provider
^ORA-(\d{5}): -> DB-side, no opc-request-id
"code": null.*"status": 404 -> HEAD op, branch on status
```

Message text is not a stable contract; regex only when `code` is null/absent.

## 3. Decision tree

```
1. Starts with "ServiceError:"?
   NO -> "RequestException:" -> transport/region/proxy: check region, egress
     -> "Usage: oci" -> local usage. Fix args. Never retry
     -> "ERROR:"/"+Config Errors+" -> credentials/profile
     -> "ORA-" -> database-side
     -> "│ Error: NNN-Code" -> Terraform provider
     -> silence/hang -> prompt in a non-TTY
   YES -> parse JSON, capture opc-request-id FIRST, then:
2. 401 -> credentials, clock skew, region subscription. NEVER a policy fix
3. 403 -> NotAllowed = wrong region (IAM writes are home-region-only)
          NotAuthorized = drop the offending field
4. 404 -> run the 5-step NAONF ladder (§4). Never say "does not exist"
5. 409 -> IncorrectState/ExternalServerIncorrectState = wait + retry
          Conflict/ResourceLocked/InvalidatedRetryToken/AlreadyExists = no retry
6. 429 -> backoff with full jitter, reduce concurrency
7. 500 -> /out of host capacity/i: vary AD/FD/shape
          else backoff, then escalate with opc-request-id
8. 503 -> backoff; check ocistatus.oraclecloud.com
9. 400 -> QuotaExceeded? `oci limits quota list` (self-fixable)
          LimitExceeded? `oci limits value list` (support ticket)
          else fix the request; do NOT retry
```

## 4. The 401 / 403 / 404 ladder

| Status / code | Means | Fix |
|---|---|---|
| `401 NotAuthenticated` | "I don't know who you are" — never policy | bad credentials (classic: `key_file` points at the *public* key), clock skew > 5 min, bad `Authorization` header, or region not subscribed |
| `403 NotAuthorized` | passed the resource check, failed on a *field* | strip it (usually `definedTags` or `compartmentId`) |
| `403 NotAllowed` | wrong region for an IAM write | re-issue in the home region |
| `404 NotAuthorizedOrNotFound` | ambiguous by design: "absent" and "invisible" merged so callers can't enumerate | ladder below |

Ladder, in order: **1** OCID well-formed? `not-an-ocid` to `oci iam compartment get` returns NAONF/404, not `InvalidParameter` [verified — reproduced], so a NAONF proves nothing about existence — validate `ocid1\.<type>\.oc[0-9]+\.[a-z0-9-]*\..+` client-side. **2** Region mismatch — read `request_endpoint`. **3** Compartment mismatch (`list` returns empty, `get` NAONF). **4** Policy — map `operation_name` to a permission (Policy Reference). **5** Principal scoping: a dynamic-group principal can read compartments yet fail tenancy-level Identity calls (`list_compartments` OK, `list_users` NAONF) [unverified — community].

**Rule:** never report "does not exist" on a bare NAONF. Say "not found *or* not visible to this principal in this region/compartment", and name the checks run.

## 5. Retryability and the corpus

Backoff-retry ONLY on `429`, all `5xx`, and `409 IncorrectState` / `409 ExternalServerIncorrectState`. Everything else is `Retry: No`; retrying a NAONF or `InvalidParameter` is token burn. Carve-out: the Python SDK's retry config treats `400 QuotaExceeded` / `400 LimitExceeded` as retryable — a concurrent teardown can clear them.

`references/error-corpus.json` holds **125 entries** (`entry_count` agrees), each `{id, section, service, code, signal, http_status, regex, cause, fix, urls, verified, retryable}`, plus the 12-key `envelope_regexes` map. Skills cite failure modes by `id`. Regenerate:

```bash
cp research/data/error-corpus.json references/ && python3 -m json.tool references/error-corpus.json >/dev/null
```

Not in the corpus (no safe read-only repro): Streaming, Functions, Data Flow, Gen-AI; WAF/LB 5xx bodies; Vault/KMS crypto endpoints; Email SMTP.

- https://docs.oracle.com/en-us/iaas/Content/API/References/apierrors.htm (200, 2026-09-08)
- https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/policyreference.htm (200, 2026-09-08)
