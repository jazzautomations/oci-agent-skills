Purpose: choose an OCI principal and prove which one signs — the six `--auth` values, session lifecycle, env vars, identity probes.
Source: research/04a-cli-auth-ergonomics.md §1–2; generated 2026-09-08; verified-on CLI 3.91.0

## 1. The six `--auth` values

Exactly six in CLI 3.91.0, same values via `OCI_CLI_AUTH` [verified — `oci --help`, `cli_constants.py`].

| Value | Where it works | Credential source | Agent note |
|---|---|---|---|
| `api_key` (default) | anywhere | profile `user`, `tenancy`, `fingerprint`, `key_file`\|`key_content`, `pass_phrase` | long-lived; the only mode that survives an unattended run |
| `security_token` | workstation, Cloud Shell | `security_token_file` from `oci session authenticate` | expires ≤60 min — see §2 |
| `instance_principal` | OCI compute instance | instance metadata service + dynamic group + policy | no keys on disk; fails without a matching dynamic group |
| `instance_obo_user` | Cloud Shell, delegation | `delegation_token_file` | Cloud Shell default: instance principal on behalf of the signed-in user |
| `resource_principal` | Functions, Data Science, Data Flow | the RP env vars of §3 [verified — `cli_util.py:424-443`] | no keys on disk; RP vars must already be in the env [unverified] |
| `oke_workload_identity` | OKE pod | projected SA token [verified — `cli_constants.py:27-28`] | needs the flag **and** usually an explicit `--region`: no config file in the pod |

Companions: `--auth-purpose`; `--federation-endpoint`/`OCI_CLI_FEDERATION_ENDPOINT` for `instance_principal` [verified].

## 2. Session tokens (`security_token`)

| Step | Command | Notes |
|---|---|---|
| create | `oci session authenticate --region <r> [--profile-name N] [--tenancy-name T] [--no-browser] [--session-expiration-in-minutes N]` (dir `~/.oci/sessions`) | TTL **5–60 min, every realm, default 60** [verified — `OCI_CLI_UPST_TOKEN_MIN_TTL`/`OCI_CLI_UPST_TOKEN_MAX_TTL`] |
| probe | `oci session validate --local` | reads only the expiry claim — no network; cheapest liveness probe [verified] |
| renew | `oci session refresh` | no options; only inside the refreshable window, else re-run `authenticate` [verified] |
| move | `oci session export --output-file P` / `import --session-archive P` | the archive is a credential — never commit [verified] |
| end | `oci session terminate` | removes the profile **and its keys** [verified] |

**Rule.** Runs over ~50 min: use `api_key`, `instance_principal` or `resource_principal`; on `security_token`, gate every call with `oci session validate --local || oci session refresh`.

## 3. Principal env vars (9) — read out of the installed 3.91.0 [verified]

| Var | Feeds |
|---|---|
| `OCI_CLI_AUTH` | picks the mode (same values as `--auth`) |
| `OCI_CLI_SECURITY_TOKEN_FILE` | `security_token` token path |
| `OCI_CLI_DELEGATION_TOKEN_FILE` | `instance_obo_user` delegation token |
| `OCI_RESOURCE_PRINCIPAL_VERSION` | `1.1` or `2.2` — decides which other RP vars are read |
| `OCI_RESOURCE_PRINCIPAL_REGION` | region for the resource principal |
| version-specific RPST / private-key vars | RP token + key material [verified — `cli_util.py:424-443`] |
| `OCI_KUBERNETES_SERVICE_ACCOUNT_TOKEN_PATH` | OKE WI token on disk (default: projected SA path) |
| `OCI_KUBERNETES_SERVICE_ACCOUNT_TOKEN_STRING` | same, token inline |
| `OCI_CLI_FEDERATION_ENDPOINT` | federation endpoint for `instance_principal` |

Also `OCI_CLI_PROFILE`/`CONFIG_FILE`/`REGION` + per-key `OCI_CLI_TENANCY`/`USER`/`FINGERPRINT`/`KEY_FILE`/`KEY_CONTENT`/`PASSPHRASE` let an agent run with **no config file**; `OCI_CLI_AUTO_PROMPT` stays unset.

## 4. Detecting the active identity

No `oci whoami` exists. Six probes, cheapest first:

| # | Probe | Reads |
|---|---|---|
| 1 | `grep -E '^\[\|^(user\|tenancy\|security_token_file\|key_file)' ~/.oci/config` | offline: `security_token_file` + no `user` = session profile |
| 2 | `oci session validate --local` | offline: session alive or expired [verified] |
| 3 | `oci iam user get --user-id "$U" --query 'data.{name:name,mfa:"is-mfa-activated"}'` (`U` = profile `user`) | the human behind `api_key`/`security_token`; fails under instance/resource principals [verified live] |
| 4 | `oci iam region-subscription list --query 'data[].{region:"region-name",home:"is-home-region"}'` | any principal; also names the home region [verified live] |
| 5 | rerun one read with `--auth api_key`, then `--auth instance_principal` | the failing one is not configured |
| 6 | `oci --debug <cmd> 2>&1 \| head` | signer class + endpoint; definitive, but `--debug` leaks signing detail — forbidden by `redaction.md` |

Probe 3 under an instance principal fails `NotAuthorizedOrNotFound`: a 404-shaped "who am I" means no user on the principal, not a wrong tenancy.

## 5. Resolution order and traps

- Precedence: **flag > env var > config profile > `oci_cli_rc` default** [verified].
- `api_key` needs `user`, `tenancy`, `fingerprint`, `region` + `key_file`\|`key_content` [verified — `OCI_CONFIG_REQUIRED_VARS`]; optional `pass_phrase`, `security_token_file`, `delegation_token_file`.
- Loose perms on `~/.oci/config` or a key warn on stderr and pollute JSON parsing: fix with `oci setup repair-file-permissions --file P`; `OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING=True` silences it [verified].
- A `compartment-id` default in `~/.oci/oci_cli_rc` **silently changes the blast radius** of every later command. Read it before assuming tenancy root.
- Never agent-run: `oci setup bootstrap` (browser login, needs port 8181, **generates and uploads** an API key) and `oci setup instance-principal` (interactive, **mutates IAM** — dynamic group + policy; no browser) [verified — `setup --help`, each `--help`]. `setup keys` is safe but writes a private key — never into a repo.

## Links
[API key](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm) · [Sessions](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/clitoken.htm) · [Config](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliconfigure.htm) · [Instance princ.](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/callingservicesfrominstances.htm) · [Resource princ.](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm) · [OKE WI](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contenggrantingworkloadaccesstoresources.htm) (all 200, 2026-09-08)
