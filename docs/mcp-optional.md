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

Schema tokens are estimates (JSON characters / 4, rounded up). Future skill
activation evaluations, not this runtime smoke, establish the final resident
budget. The plan's target is ≈6.3–6.5k tokens (≈3,020 descriptions + ≈3,300–3,500 MCP schemas, estimates).
