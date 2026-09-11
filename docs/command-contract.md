# Check OCI command proposals without executing them

The optional command-contract helper checks an **inert string** against the
shipped OCI CLI 3.91.0 read catalog. It neither opens an OCI configuration nor
calls a service, runs a shell, invokes a command callback or executes the proposal.

Use it before presenting a command for execution:

```bash
uv run --frozen --project runtime python scripts/read_contract.py describe 'compute instance list'
uv run --frozen --project runtime python scripts/read_contract.py check 'oci compute instance list --compartment-id "$C" --limit 20 --query data'
```

`describe` supplies canonical required flags, declared aliases, enum choices and
whether a leaf actually supports `--limit`. `check` reports fixed diagnostic codes
without echoing parameter values. It checks known options, duplicate aliases,
required flags, 1–100-item bounds, no `--all`, compiled JMESPath and literal enums.
OCI's custom case-insensitive enum conversion is represented explicitly rather
than trusting Click's inherited `case_sensitive` attribute. Aliases are local to
the command's loaded metadata; prefer canonical names instead of assuming `-c`
works everywhere or importing personal CLI aliases into the catalog.

This avoids failures such as adding `--limit` to `audit event list`, inventing
`--max-items`, omitting an explicit compartment, or combining `--all` and
`--limit`. A time-scoped leaf without `--limit` must keep its explicit resource
and time scope; absence of that option is not permission to sweep an account.

## Optional MCP transport

An additional, separate server exposes exactly two offline tools:

- `describe_read_command`: inspect one read-command definition.
- `check_read_command`: check one proposed string; never execute it.

Rejected command proposals return MCP `isError: true` with fixed diagnostic
codes and `valid: false`. A successful tool invocation is not a substitute for
checking validity; the positive path returns `valid: true` and `isError: false`.

It is **not automatically registered** and does not replace or expand the
default 15-tool OCI server. Configure an MCP client to launch this fixed process,
using the absolute path to the installed copy:

```json
{
  "mcpServers": {
    "oci-command-contract": {
      "command": "uv",
      "args": [
        "run", "--frozen", "--project", "/path/to/plugin/runtime",
        "python", "/path/to/plugin/scripts/command_contract_server.py"
      ]
    }
  }
}
```

No authentication variables or account credentials are needed. OCI operational
tool permissions and IAM remain separate. A successful check is not approval to
execute a command and does not establish requested query meaning, response-field
existence, SDK callback constraints, authorization, resource scope, completeness
or cloud-workload success. Shell composition and substitutions are refused, but
this helper is not a replacement for a shell sandbox or the host's permissions.

For the checked workflow, instruct the agent to inspect uncertain leaves with
`describe_read_command`, submit **each final command** to `check_read_command`,
repair diagnostics and check again. If it edits a command after checking it, it
must check the edited string too. A tool call alone is insufficient: inspect
the returned `valid` field. Keep failures visible instead of presenting rejected
commands as finished work. This workflow is opt-in, not automatically imposed by
installing the default plugin.

## Reproducibility

`catalog/read-contracts.json` contains aliases and choices from installed Click
metadata and is bound to the shipped CLI catalog by SHA-256. Generate or check it
using Python from the pinned OCI CLI environment; only definitions are inspected:

```bash
python scripts/generate_read_contracts.py --check
```

The [checked task collector](../scripts/eval/checked_task_benchmark.py) provides
the same contract tools to both paired arms, requires observed checks of every
final proposed command, and retains original exact-answer grading. It corrects
native unqualified-skill handling only when a unique registered name and the
observed installed skill body establish ownership. Earlier reports remain
unchanged. This is a new intervention, not a retroactive score adjustment.
