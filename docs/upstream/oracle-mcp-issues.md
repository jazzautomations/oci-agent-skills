# Upstream issues for oracle/mcp (drafts)

Evidence: this repo's smoke harness run on 2026-09-08 against oracle/mcp @ e3cdae7 (2026-09-03), OCI CLI 3.91.0, one API-key
profile, one region. Reproduce with `python research/mcp-smoke.py` (build-only) or the commands in each issue. Post with:

```bash
gh issue create -R oracle/mcp --title "<title>" --body-file <file>
```

---

## Issue 1 — 10 typed OCI servers fail every tools/call with `'security_token_file'` when the profile uses API-key auth

**Servers affected:** oci-compute, oci-identity, oci-usage, oci-limits, oci-resource-search, oci-object-storage, oci-networking,
oci-monitoring, oci-logging, oci-cloud-guard (all 10 that do not depend on `oracle-mcp-common`). The 3 servers built on
`oracle-mcp-common` 0.1.3 (oci-cloud, oci-api, oci-database) and oci-pricing work with the same profile.

**Repro:** `~/.oci/config` DEFAULT profile with `user`, `fingerprint`, `key_file`, `tenancy`, `region` (standard API-key setup, no
`security_token_file`). Launch e.g. `uvx --from <path>/src/oci-networking-mcp-server oci-networking-mcp-server` over stdio, send
`initialize`, `tools/list`, then `tools/call list_vcns {"compartment_id": "<root>"}`.

**Observed:** `{"content":[{"type":"text","text":"Error calling tool 'list_vcns': 'security_token_file'"}],"isError":true}` for
every tool on all 10 servers. Startup and `tools/list` succeed, so the failure is only visible at first call.

**Cause:** these servers construct `oci.auth.signers.SecurityTokenSigner` from `config['security_token_file']` unconditionally and
never fall back to `oci.signer.Signer` (API key) or instance/resource principals. Feeding a dummy `security_token_file` proves
the absence of fallback: the request goes to the wire with `keyId="ST$not-a-real-token"` and is rejected.

**Suggested fix:** share the auth resolution already implemented in `oracle-mcp-common` (API key → session token → instance
principal → resource principal, selectable via `OCI_CLI_AUTH`/env), or at least branch on the presence of `security_token_file`.
A one-line error message naming the missing config key would also help users.

---

## Issue 2 — oci-database-mcp-server advertises 147 tools (~213k estimated schema tokens), which no MCP client can load

**Observed:** `tools/list` returns 147 tools (66 `list_*`, 74 `get_*`, plus others), a mechanical 1:1 mirror of
`oci.database.DatabaseClient`. Serialized schema ≈ 851 KB ≈ 212,873 tokens (chars/4 estimate, ±15%). For comparison, oci-cloud
exposes the whole SDK (321 clients) through 5 tools in ~1.3k tokens, and oci-api exposes the whole CLI in 2 tools (~721 tokens).

**Impact:** any host that loads the server's tool list into the model context either fails or spends the entire budget on
schemas; the server is effectively unusable without a client-side tool filter.

**Suggestion:** curate (≤ 20 task-level tools: ADB lifecycle, wallet, backups, DB systems, patches, Data Guard, work requests) and
route the long tail through a single `invoke_database_operation` tool with a name/arguments schema, as oci-cloud already does.

---

## Issue 3 — oci-api-mcp-server denylist is not a read-only boundary: it allows 374 destructive and 2,511 mutating CLI leaves

**Method:** replayed `oci-api-mcp-server`'s denylist (2,222 entries) against the complete OCI CLI 3.91.0 command tree
(9,145 leaf commands, enumerated from the installed CLI). Classification: destructive = delete/terminate/purge/detach/
bulk-delete and similar verbs; mutating = create/update/launch/attach/etc.

**Observed:** the denylist allows 374 destructive and 2,511 mutating leaves (e.g. many `delete`/`terminate` forms outside the
listed services) while denying 135 read-only leaves. Detailed replay artifact (JSON) available on request / in
`docs/evidence/denylist-coverage-research.json` of the reporting repo.

**Why it matters:** the server is presented as a guarded generic executor; users may assume "denylisted = safe". A verb/leaf-based
classifier (read allowlist first, then severity tiers with confirmation) is a stronger default than a hand-maintained denylist.

**Suggestion:** ship a read-only mode (`OCI_API_MCP_READ_ONLY=1`) that allowlists `list|get|search|head|summarize|describe`
leaves, and label the denylist as advisory in the README.
