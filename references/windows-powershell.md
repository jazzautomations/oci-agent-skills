Purpose: run the OCI CLI from Windows PowerShell — install, quoting traps, bash→pwsh forms.
Source: research/16-oracle-runtimes-email-compliance.md §D; generated 2026-09-08; verified-on CLI 3.91.0

**No Windows host: every pwsh form below is `[unverified]` — a mechanical translation of a bash form
run or `--help`-checked on 3.91.0. Verify before use.**

## 1. Install

| Path | Command | When |
|---|---|---|
| MSI | github.com/oracle/oci-cli/releases | one CLI per box — **overwrites any existing version** [verified] |
| Installer script | `Set-ExecutionPolicy RemoteSigned` → TLS 1.2 on Server 2012/2016 → run `scripts/install/install.ps1` from the oci-cli repo | prompts for dir, Python, `PATH` entry [verified] |
| Manual venv | docs' manual method in a venv | the **only** way to keep multiple versions [verified] |

Docs: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm

Config: `%USERPROFILE%\.oci\config` (`$HOME\.oci\config` in pwsh); use **backslashes** in pathnames inside it,
including `key_file`. `OCI_CLI_CONFIG_FILE` and `OCI_CLI_SETTINGS` behave as on Linux. Auto-complete
works **only** in PowerShell and needs `RemoteSigned` [all verified,
https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliconfigure.htm].

## 2. Two quoting traps

1. **Backtick.** JMESPath uses `` `literal` `` for JSON literals; pwsh uses `` ` `` as its escape character,
   so in a **double-quoted** pwsh string backticks are eaten and the query silently wrong. Wrap
   `--query` in pwsh **single** quotes — literal, so `` ` `` and `$` survive.
2. **Hyphenated keys.** OCI returns kebab keys (`lifecycle-state`, `display-name`); JMESPath needs them
   double-quoted as identifiers. Single-quote the whole query in both shells so the `"` reaches JMESPath;
   escape an inner `'` in pwsh by doubling it (`''`), never `\`.

`--from-json` takes a URI, not a Windows path: `file://C:/path/x.json`, forward slashes. A bare
`C:\path\x.json` is rejected.

## 3. Bash → pwsh, ten forms

| # | bash | pwsh — all `[unverified]` |
|---|---|---|
| 1 | `--query 'data[].name'` | identical — single quotes safe in both |
| 2 | `--query "data[?key=='ORD'].name"` | `--query 'data[?key==''ORD''].name'` (double the inner quote) |
| 3 | ``--query 'data[?key==`ORD`].name'`` | same string, single-quoted — **never** double-quoted, the backticks vanish |
| 4 | ``--query 'data[?"lifecycle-state"==`RUNNING`]."display-name"' -c $C`` | same query, single-quoted; `$C` does **not** expand in single quotes — keep it outside |
| 5 | `export OCI_CLI_PROFILE=DEFAULT` | `$env:OCI_CLI_PROFILE = 'DEFAULT'` |
| 6 | `oci --config-file ~/.oci/config …` | `oci --config-file "$HOME\.oci\config" …` |
| 7 | `--from-json file:///home/u/x.json` | `--from-json file://C:/Users/u/x.json` |
| 8 | `oci … --output table \| head -20` | `oci … --output table \| Select-Object -First 20` |
| 9 | `oci … \| jq '.data[0].id'` | `(oci … \| ConvertFrom-Json).data[0].id` — no `jq` needed |
| 10 | `for r in $(oci … --raw-output); do …; done` | `foreach ($r in (oci … \| ConvertFrom-Json)) { … }` |

## 4. OCI Modules for PowerShell — not our path

`OCI.PSModules.<Service>` (Gallery; each needs `OCI.PSModules.Common`) read the **same
`~/.oci/config`** [unverified — search summaries;
https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/powershell.htm]. Versions are unrelated to CLI
versions (`OCI.PSModules` 122.x vs CLI 3.92.x) — never map one to the other. Answer in CLI: the corpus and guard
regexes are CLI-shaped; no safety model exists for cmdlets.
