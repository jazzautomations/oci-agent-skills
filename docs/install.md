# Install OCI Agent Skills

Python 3.13+, `uv`, and OCI CLI 3.93.0 are the reproducible baseline. OCI credentials
are needed only when calling credentialed tools. The bundled MCP exposes
15 shipped tools (14 credentialed + oci_price_lookup, credential-free).

| Host | Skill discovery | Shell protection |
| --- | --- | --- |
| Claude Code | Native plugin `skills/` | Advisory Bash PreToolUse hook |
| Codex | Plugin manifest or copied `.agents/skills` | **UNGUARDED**; no automatic PreToolUse equivalent in this adapter |
| Gemini CLI | Copied `.gemini/skills` | **UNGUARDED** |
| Cursor | Copied `.cursor/skills` | **UNGUARDED** |
| OpenCode (configuration checked with 1.18.30) | Copied `.opencode/skills` | **UNGUARDED** |
| Generic MCP client | Explicit stdio server configuration | Fixed read-only tools; host shell protection is separate |

Run from this repository, choosing an absent or empty target outside it:

```bash
bash installers/install.sh --target /tmp/oci-plugin --host claude --copy-shared
uv sync --frozen --project /tmp/oci-plugin/runtime
uv run --frozen --project /tmp/oci-plugin/runtime oci-readonly-smoke
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

The marketplace entries now select 33 full-pack, 8 database and 9 DevOps skills. Each carries hooks and MCP; the database subset includes the five DB skills plus navigator, CLI auth and IAM policy. The DevOps subset includes OKE, pipelines, serverless, Terraform, monitoring, logging and incident triage plus navigator and CLI auth.

Validate the source manifests and bare skill directory:

```bash
claude plugin validate . --strict
claude plugin validate ./skills --strict
```

The authoring stencil is SKILL.md.template, not a discoverable skill. The installer copies the active skills, shared references, scripts, catalog, hooks, .mcp.json, runtime, evals and license notices. It excludes local handoff scratch files and the build log under `docs/build-log/`. A `find . -type l` inside the fresh copied tree returns nothing before any runtime environment is created.

Examples for the other project adapters:

```bash
bash installers/install.sh --target /tmp/oci-gemini --host gemini --copy-shared --i-accept-unguarded
bash installers/install.sh --target /tmp/oci-cursor --host cursor --copy-shared --i-accept-unguarded
bash installers/install.sh --target /tmp/oci-opencode --host opencode --copy-shared --i-accept-unguarded
```

Open the installed directory as the host project. These commands produce local configuration; they do not register marketplaces or modify global host settings. Interactive discovery remains host/version dependent. Codex's plugin manifest carries an inline MCP map and anchors the runtime working directory to the plugin root; its copied adapter uses .agents/skills and .codex/config.toml. Gemini and Cursor use .gemini/settings.json and .cursor/mcp.json. OpenCode maps server names directly under `mcp`, as specified in its [MCP configuration documentation](https://opencode.ai/docs/mcp-servers/); the generated map is checked against the native 1.18.30 schema. Keep the entire installed tree: copied host skill links also target the canonical `skills/` tree.

To remove a copy, first move any user work out of its installation directory, then remove that directory yourself. The installer never overwrites a nonempty target and does not remove other installations.

Current license: Apache-2.0 with LICENSE.txt in every skill. NOTICE preserves pre-v2 MIT attribution, and evaluation snapshots keep upstream MIT/UPL notices. Run `uv run --frozen --project runtime python scripts/ci/check_licenses.py`.

The copy installer excludes `CODEX-STATUS.md` and the `docs/build-log/` handoff history. Run the emitted `runtime_setup` argv in the target before opening any host. If omitted, the first MCP launch runs `uv` in that target, installs its environment, and needs package download access. A source-checkout sync does not warm the copied target.

Host registration was checked in Claude Code 2.1.266 from an unrelated working directory: all 15 bundled tools appeared after asynchronous MCP startup. The probe used ToolSearch for schema discovery and invoked no OCI tool; see [host discovery evidence](evidence/plugin-host-discovery.json).
