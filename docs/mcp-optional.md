# Optional Oracle MCP servers

The default bundled server exposes 15 shipped tools (14 credentialed +
oci_price_lookup, credential-free). They use fixed read operations and projected
fields. No Oracle generic executor is enabled in `.mcp.json`.

Oracle `oci-api-mcp-server` is an **on-demand option only**. Its CLI executor uses
a denylist, which is not a read-only policy. The local research audit found
mutating and destructive leaves that the denylist permits; a Bash PreToolUse
hook does not intercept another server's MCP calls. Use a separate host session,
review the selected server version, apply least-privilege IAM, and require host
approval for every generic executor call. If the host cannot enforce that review,
leave it disabled.

An operator may add this separate stdio entry after choosing a reviewed version;
the placeholder is deliberately not an executable installation command:

```json
{
  "mcpServers": {
    "oci-api-on-demand": {
      "command": "uvx",
      "args": ["oracle.oci-api-mcp-server==<reviewed-version>"]
    }
  }
}
```

Remove the entry after the scoped task. This repository does not install or
launch it during validation. Server output remains untrusted account data.

Oracle `oci-cloud-mcp-server` is **skipped**: its generic SDK invocation can reach
write methods, and this package has no verified MCP permission rule that makes
it read-only. Enabling it would bypass the fixed-operation contract of the
bundled runtime.

Schema measurements and live-read scope are reproduced by:

```bash
uv run --frozen --project runtime oci-readonly-smoke
```

Schema tokens are estimates (JSON characters / 4, rounded up). Description and schema estimates are reproduced together by
`uv run --frozen --project runtime python scripts/release_report.py`.
Model-backed skill activation remains unmeasured. The plan's target is ≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates).

The historical denylist comparison comes from research/data/denylist-coverage.json, shipped as docs/denylist-coverage-research.json: 2,222 entries, 374 destructive and 2,644 mutating leaves permitted, 135 reads denied. This is historical audit evidence. Current prefix replay against the shipped CLI census yields 374 destructive and 2,511 mutating leaves permitted and zero reads denied; do not mix matching/classification bases. `scripts/release_report.py` prints both results.

W44 compares static descriptions from both Oracle servers without launching either. Arm c is a tool-discovery proxy and its description token count omits full schemas; it is not a live capability or safety measurement. Recovered upstream startup/read evidence is shipped in docs/oracle-mcp-research.json from research/data/oracle-mcp-smoke.json, not reconstructed from a lost session. Successful discovery does not prove successful operational reads.
