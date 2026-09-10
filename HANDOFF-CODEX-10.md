# HANDOFF 10 → Codex — upstream fix for oracle/mcp: API-key auth fallback in the 10 typed OCI servers

Context: docs/upstream/oracle-mcp-issues.md (Issue 1) and research/03-oracle-mcp-smoke.md §"security_token_file". Ten servers
(oci-compute, oci-identity, oci-usage, oci-limits, oci-resource-search, oci-object-storage, oci-networking, oci-monitoring,
oci-logging, oci-cloud-guard) build a SecurityTokenSigner unconditionally and fail every tools/call on an API-key profile.
The three servers on oracle-mcp-common (oci-cloud, oci-api, oci-database) resolve auth correctly.

Work OUTSIDE this repo, in /root/projects/oracle-mcp-fork:
1. `gh repo fork oracle/mcp --clone=false --org jazzautomations` is NOT needed (user account): run `gh repo fork oracle/mcp --clone --fork-name mcp`
   into /root/projects/oracle-mcp-fork (if the fork exists already, clone it). Branch `fix/api-key-auth-fallback` from upstream main.
2. Read src/common (oracle-mcp-common) auth resolution and each of the 10 servers' client construction. Implement the smallest upstream-
   style change: resolve auth in this order — explicit OCI_AUTH env (api_key | security_token | instance_principal | resource_principal),
   else `security_token_file` present in the profile → SecurityTokenSigner, else API-key `oci.signer.Signer` from the profile, else
   instance principal; raise a clear error naming the missing config keys. Prefer reusing oracle-mcp-common if the servers can depend
   on it without a large diff; otherwise a tiny shared helper duplicated per server following their existing style (check CONTRIBUTING
   and the repo's lint/test conventions; match them exactly).
3. Add unit tests (mock config) covering the four paths per server (or one shared test module if the helper is shared). Run the repo's
   test/lint commands. Smoke-test 3 of the 10 servers live over stdio with the local DEFAULT API-key profile (read-only tools only:
   list_vcns, get_current_tenancy, list_services) using /root/projects/oci-agent-skills/research/mcp-smoke.py; record before/after in
   the PR body. Never mutate the tenancy.
4. Commit(s) with conventional messages, author = the git config user. Push the branch to the fork. Do NOT open the PR: write the
   ready-to-run command and the PR body (title, summary, root cause, fix, tests, smoke evidence, checklist per their CONTRIBUTING) to
   /root/projects/oracle-mcp-fork/PR-BODY.md. Also check whether oracle/mcp requires an Oracle Contributor Agreement (OCA) and note it.
5. Report in /root/projects/oci-agent-skills/CODEX-STATUS.md (do not touch other files in oci-agent-skills).
