# Install the foundation

Python 3.13+, `uv`, and OCI CLI 3.91.0 are the reproducible baseline. OCI credentials
are needed only when calling credentialed tools. The bundled MCP exposes
15 shipped tools (14 credentialed + oci_price_lookup, credential-free).

| Host | Skill discovery | Shell protection |
| --- | --- | --- |
| Claude Code | Native plugin `skills/` | Advisory Bash PreToolUse hook |
| Codex | Plugin manifest or copied `.agents/skills` | **UNGUARDED**; no automatic PreToolUse equivalent in this adapter |
| Gemini CLI | Copied `.gemini/skills` | **UNGUARDED** |
| Cursor | Copied `.cursor/skills` | **UNGUARDED** |
| OpenCode v2 | Copied `.opencode/skills` | **UNGUARDED** |
| Generic MCP client | Explicit stdio server configuration | Fixed read-only tools; host shell protection is separate |

Run from this repository, choosing an absent or empty target outside it:

```bash
bash installers/install.sh --target /tmp/oci-plugin --host claude --copy-shared
claude --plugin-dir /tmp/oci-plugin
```

An unguarded host requires the explicit flag; omission exits non-zero before any
files are copied:

```bash
bash installers/install.sh --target /tmp/oci-codex --host codex --copy-shared --i-accept-unguarded
```

The installer copies the selected project configuration and skills, never links.
`--host all` creates adapters for all four unguarded hosts and also requires the
flag. `--copy-shared` materializes shared reference files under each skill's
`references/shared-<name>` and rewrites the shared paths. Research, vendor trees,
virtual environments, credentials and the placeholder template are excluded.
Existing nonempty targets are preserved. Before running the installed runtime:

```bash
find /tmp/oci-plugin -type l
```

That copied tree contains no symlinks. Starting `uv` can subsequently create
virtual-environment symlinks; private research in the source checkout also contains
pre-existing links. The source checkout is not claimed to pass literal `find . -type l`.

For Codex, launch with `codex --sandbox read-only` where appropriate. This limits
filesystem writes, **not OCI network writes**; IAM remains the actual boundary.
A manual preflight is available, but does not enforce a subsequent shell command:

```bash
printf '%s\n' '["oci","compute","instance","list"]' | python3 scripts/guard_oci.py --stdin-argv
```

Read tools are fixed and scoped. They have no generic CLI, SQL, or SDK executor.
Follow [runtime configuration](../runtime/README.md) for region, authentication,
and compartment allowlists. The main MCP launcher expands `${CLAUDE_PLUGIN_ROOT}`;
the Codex launcher anchors `cwd: "."` to the installed plugin root. Host launch
configurations are tested from unrelated workspaces with bogus credentials:

```bash
uv run --frozen --project runtime pytest -q tests/test_packaging.py tests/test_installer.py
```

The W08a marketplace has three entries, all with hooks and MCP, and no `skills[]`
yet. Database/DevOps subset selection and strict content validation are W08b;
these entries currently resolve the same foundation. Manifest license metadata
follows the planned Apache-2.0 release, but the protected root LICENSE remains
MIT and per-skill licenses are missing. Publication remains blocked on that
content-owner correction; this handoff does not relicense existing material.
