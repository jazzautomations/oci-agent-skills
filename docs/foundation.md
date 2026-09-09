# Foundation architecture

The Wave 3 package supersedes the earlier foundation-only snapshot. Current installation, measurements and release status are in [README](../README.md), [installation](install.md), [runtime configuration](../runtime/README.md), [audit](audit.md) and [evaluations](evals.md). There are no legacy content exemptions.

## Layers

Skills establish profile, region, compartment, decision criteria and recovery plans. Shared and local references load only when relevant. CLI discovery uses bounded catalog queries; the full inventory is not an always-resident prompt.

The Bash PreToolUse hook parses shell segments, inspects known OCI leaves and recognized plugin script invocations, and returns allow/ask/deny decisions. Script hashes bind the registry to guard metadata; unknown or modified scripts require review. The guard is advisory and cannot intercept arbitrary MCP servers or prove arbitrary program behavior. IAM remains the boundary. Profile/auth overrides are allowed; unknown OCI leaves and recognized opaque shell forms require review. Unrecognized commands return no decision and retain the host permission policy. Non-OCI rules are hand rules, not a measured confusion matrix.

Plugin scripts route OCI through scripts/lib/oci_ro.py or oci_ro.sh. The wrapper resolves installed snapshot paths, rejects unsafe flags and refuses non-allowlisted operations. OCI help inspection constructs fresh leaf-only help invocations and never executes example callbacks. Static script lint adds a check for direct CLI/SDK calls and opaque execution; it is not proof against arbitrary Python.

The bundled MCP exposes fixed scoped read operations. It has no generic CLI/SQL/SDK executor. Authentication caches expire on TTL or credential-file changes; an unauthorized read invalidates auth and retries that read once. SDK work runs in worker threads. Output projects allowed fields and reports provenance, count, truncation and completeness. Compartment ancestry checks use actual parent relationships, not OCID string prefixes. Cost scope and grouping are explicit; no cross-currency total is formed.

Untrusted-output cleaning flags rather than suppresses suspicious values. Control characters and length are bounded, and flags accompany the retained text. Instructions embedded in OCI values do not authorize scope changes, tool calls or shell execution. Unit fixtures test transformations; they do not establish live prompt-injection resistance.

## Reproduce

```bash
uv run --frozen --project runtime python scripts/release_report.py
uv run --frozen --project runtime oci-readonly-smoke
uv run --frozen --project runtime pytest -q tests
uv run --frozen --project runtime python scripts/ci/check_scripts_readonly.py
uv run --frozen --project runtime python scripts/inventory.py --scripts --examples --check
```

CLI inventory and offline example validation additionally need Python with pinned OCI CLI installed. The runtime environment intentionally does not include the CLI. CLI drift runs on the scheduled workflow; public documentation links are a nightly check. Creating hosted issues or running CI schedules was not part of local validation.

Always-resident planning floor: ≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates). This is a raw source-size estimate that excludes host framing. `release_report.py` prints it alongside `docs/context-measurement.json`, which measures the host framing separately. Readiness depends on the complete release matrix, not on this architecture description or a passing smoke test.
