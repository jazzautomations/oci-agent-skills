Purpose: one card per OCI CLI service group — where to start reading and the one trap that wastes a session. Index, not manual.
Source: research/{04b-iam-security-cost-freetier, 04c-core-services-pitfalls, 09a-devops-ci-oke-containers, 09b-observability-sre-netsec-ops, 11-database-management-fleet-opsi}.md + research/data/{cli-ops-per-service, cli-leaves}.json; generated 2026-09-08; verified-on CLI 3.91.0.

Top 40 groups by leaf count. Read a row as `oci <group> <path>`; `-c` = `--compartment-id`. Every path verified with `--help` on 3.91.0; cmdref `…/cmdref/<group>.html` (200, 14 sampled).

| Group (leaves) | Start-here reads | The one gotcha |
|---|---|---|
| `db` 535 | `system list -c` · `patch list by-database --database-id` | `by-database` is a subcommand, not a flag; `database restore` marks none of `--latest/--timestamp/--database-scn` required yet needs one `[unverified]` |
| `database-management` 434 | `managed-database list -c` · `diagnosability managed-database list-alert-logs` | `-with-password` variants put the password in argv; use `named-credential` |
| `data-safe` 374 | `target-database list -c` · `security-assessment list -c` · `alert-summary list-alerts -c` | no `alert list`: listing is `alert-summary list-alerts`; `alert` has only `get` + mutations (09b §25 is stale) |
| `identity-domains` 330 | `users list` · `groups list` · `apps list` | SCIM: needs top-level `--endpoint <domain URL>`; `list` sits on the plural noun |
| `network` 273 | `vcn list -c` · `subnet list --vcn-id` · `drg-route-rule list --drg-route-table-id` | `update` replaces whole collections: route rules, security-list rules, NSG ids |
| `opsi` 239 | `database-insights list` · `host-insights list` · `operations-insights-warehouses list` | enrollment is per resource: an empty list says nothing; cross-check `oci db` |
| `devops` 229 | `project list -c` · `build-run list --project-id` · `work-request-error list --work-request-id` | the first build stage's `--stage-predecessor-collection` is the PIPELINE OCID |
| `log-analytics` 202 | `namespace list -c` · `entity list -c --namespace-name` · `query search --query-string --sub-system` | LQL is not the Logging search language; ingest bills/GB |
| `fleet-apps-management` 197 | `fleet-collection list-fleets` · `fleet get --fleet-id` · `compliance get --fleet-id` | paths run four deep with a repeated middle segment |
| `data-integration` 192 | `workspace list -c` · `application list --workspace-id` · `task-run list --workspace-id --application-key` | a workspace bills while ACTIVE; `stop` it |
| `data-science` 185 | `project list -c` · `notebook-session list -c` · `model-deployment list -c` | notebook sessions bill while ACTIVE, no auto-stop; `deactivate` them |
| `os-management-hub` 179 | `managed-instance list` · `software-source list` · `scheduled-job list` | patch via a RECURRING `scheduled-job` on a group, not per instance |
| `cloud-guard` 165 | `configuration get -c` · `problem list -c` · `security-zone-collection list-security-zones -c` | a never-enabled tenancy answers 404 NotAuthorizedOrNotFound |
| `goldengate` 161 | `deployment list -c` · `connection list -c` | deployments bill per OCPU-hour while ACTIVE; see `lifecycle-sub-state` |
| `data-catalog` 149 | `catalog list -c` · `data-asset list --catalog-id` · `entity list --catalog-id --data-asset-key` | child nouns key off parent *keys*, not OCIDs |
| `iam` 145 | `availability-domain list -c` · `compartment list -c` · `policy list -c` | `compartment list` is one level — add `--compartment-id-in-subtree true` |
| `compute` 144 | `instance list -c` · `instance list-vnics --instance-id` · `shape list -c` | `shape list` repeats per AD and includes shapes you have no limit for |
| `bds` 131 | `instance list -c` · `instance list-patches --bds-instance-id` · `bds-cluster-version list` | empty = zero bytes at exit 0, not JSON; `bds-capacity-report create` is a read |
| `oda` 119 | `instance list -c` · `management skill list --oda-instance-id` | 95 of 119 leaves are content plane; `instance stop` drops live conversations |
| `marketplace-publisher` 111 | `listing-collection list-listings -c` · `listing-revision-collection list-listing-revisions --listing-id` | resource `list` sits on the `*-collection` noun and repeats it; `get`/`create`/`update` on the bare noun |
| `stack-monitoring` 110 | `resource search -c` · `metric-extension list` | metric-extension SQL/OS bodies run on the host; `publish` arms them fleet-wide |
| `jms` 109 | `fleet list` · `installation-site-summary list-installation-sites --fleet-id` · `java-release list` | reads hang off `*-summary list-*`; 45 of 70 need `--fleet-id` (`fleet`, `java-release`, `java-family` do not) |
| `generative-ai` 103 | `model-collection list-models -c` · `endpoint-collection list-endpoints -c` | no `model list`; chat/embed live in `generative-ai-inference` |
| `network-firewall` 95 | `network-firewall list -c` · `network-firewall-policy list -c` · `security-rule list --network-firewall-policy-id` | it sees nothing until route tables aim at its private IP |
| `database-migration` 89 | `migration list -c` · `job list --migration-id` · `connection list -c` | `assessment-summary list-assessments` takes `-c`; the `assessor-*` and `assessment-object-*` nouns take `--assessment-id` |
| `fleet-software-update` 86 | `fsu-collection-summary list -c` · `fsu-cycle-summary list -c` · `fsu-job-summary list --fsu-action-id` | `list` is on the `*-summary` noun, `get` on the bare noun |
| `dbtools` 81 | `connection list -c` · `private-endpoint list -c` | `create-*` takes `--user-password-secret-id` (Vault OCID), never a password |
| `resource-manager` 81 | `stack list -c` · `job list --stack-id` · `stack get-stack-tf-state --stack-id --file` | that state file carries provider secrets — see `redaction.md` |
| `dbmulticloud` 79 | `oracle-db-azure-connector list -c` · `oracle-db-azure-vault list -c` | one noun per provider × object — pick by provider |
| `fs` 74 | `file-system list` / `mount-target list` (`-c --availability-domain`) · `snapshot list --file-system-id` | AD-scoped: a wrong AD gives an empty list, not an error |
| `fusion-apps` 74 | `fusion-environment-family list -c` · `fusion-environment list -c` · `scheduled-activity list --fusion-environment-id` | children key off `--fusion-environment-id`, never `-c` |
| `rover` 73 | `node list -c` · `standalone-cluster list -c` · `shape list -c` | `device` nests three deep (`device diagnostics bundle`); `bundle get` needs `--file` |
| `waas` 73 | `waas-policy list -c` · `certificate list -c` · `access-rule list --waas-policy-id` | legacy edge WAF; the current one is `oci waf`, bound to an LB |
| `media-services` 66 | `media-workflow-job list` · `media-workflow list-system` | every noun has `delete` *and* `remove`; jobs bill per output minute |
| `mysql` 66 | `db-system list -c` · `backup list -c` | `heatwave-cluster` and `maintenance-event` nest under `db-system` |
| `ocvs` 66 | `sddc list -c` · `cluster list` · `esxi-host list` | `sddc` is legacy, `cluster` current; `esxi-host create` is a term commitment |
| `ai-vision` 65 | `project-collection list-projects` · `model-collection list-models` | listing sits on `*-collection`; `analyze-*` is inference |
| `api-gateway` 64 | `gateway list -c` · `deployment list -c` · `api list -c` | `--specification` is the whole route table, replaced wholesale; `add-lock` → 409s |
| `bv` 64 | `volume list -c` · `boot-volume list -c --availability-domain` · `volume-backup-policy list` | one policy per volume; unassigned = no backups at all |
| `kms` 62 | `management vault list -c` · `management key list -c --endpoint <ep>` · `management key-version list --key-id` | no `kms vault list`; only it needs no `--endpoint` |

Not carded (small by leaves, high traffic): `os`, `ce`, `lb`/`nlb`, `monitoring`, `logging`, `bastion`, `limits`, `artifacts`, `ons`, `audit` — enumerate them from `catalog/index.json`; shared failure modes in `cross-service-pitfalls.md`.
