# Vulnerability Scanning (VSS) and Data Safe

Verified 2026-09-09 against OCI CLI 3.91.0, `us-chicago-1`. Both services are free; both
returned empty here, so success bodies are `[shape-only]` and command paths are `[verified]`.

## VSS — the command paths research got wrong
Research 09b §27 lists `host scan-recipe list`, `host scan-target list`,
`host scan-result list`, `vulnerability list` and marks them `[unverified]`. **None of those
leaves exists on 3.91.0.** The real tree, walked with `--help`:

```
vulnerability-scanning
  host      scan {recipe,target,result{agent,cis-benchmark,endpoint-protection,port}}
            vulnerability {list,get,list-impacted-hosts,export-csv}
  container scan {recipe,target,result}
  vulnerability, work-request, work-request-error, work-request-log-entry
```

```bash
oci vulnerability-scanning host vulnerability list --compartment-id "$COMPARTMENT_ID" --limit 50 --severity CRITICAL --query 'data.items[].{cve:"cve-reference",sev:severity,hosts:"host-count",t:"time-last-detected"}'
oci vulnerability-scanning host vulnerability list-impacted-hosts --host-vulnerability-id "$HOST_VULNERABILITY_ID" --limit 50 --query 'data.items[].{i:"instance-id",s:severity}'
oci vulnerability-scanning host scan target list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",r:"host-scan-recipe-id",s:"lifecycle-state"}'
oci vulnerability-scanning host scan recipe list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",s:"lifecycle-state"}'
oci vulnerability-scanning host scan result cis-benchmark list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{i:"instance-id",f:"failed-count",t:"time-finished"}'
oci vulnerability-scanning container scan result list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{r:"repository",sev:"highest-problem-severity"}'
```

Reading the results: a **host scan recipe** (CIS benchmark + OS package CVE + optional port
scan) or a **container scan recipe** (OCIR repositories) is bound by a **target** to a
compartment or an explicit resource set. No target means no scanning — an empty
`vulnerability list` with zero targets is a *finding* ("no coverage"), not a clean bill.
Host scanning also needs the Vulnerability Scanning agent plugin enabled on the instance.
`--severity` accepts `NONE|LOW|MEDIUM|HIGH|CRITICAL`; sort with
`--sort-by name|severity|impactedHosts|firstDetected|lastDetected`.

## Data Safe
Register a target database, then run: **security assessment** (config drift vs Oracle/CIS
baselines), **user assessment** (over-privileged accounts), **activity auditing**, **sensitive
data discovery**, **data masking**, and **SQL Firewall** on 23ai. Free for Oracle databases in
OCI up to 1M audit records per target per month.

```bash
oci data-safe target-database list --compartment-id "$COMPARTMENT_ID" --compartment-id-in-subtree true --limit 50 --query 'data[].{n:"display-name",t:"database-type",s:"lifecycle-state"}'
oci data-safe security-assessment list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data[].{n:"display-name",t:"triggered-by",s:"lifecycle-state"}'
oci data-safe user-assessment list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data[].{n:"display-name",t:"triggered-by"}'
oci data-safe audit-trail list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{t:"target-id",s:status,st:"lifecycle-state"}'
```

Onboarding order matters and explains most 404s: enable Data Safe **in the region**, register
the target (needs reachability — private endpoint, on-prem connector, or ADB direct), then
assessments run on a weekly schedule after the first one. Comparing two assessments is
`security-assessment get-security-assessment-comparison`.

## The empty-output trap, both services
With nothing registered, these list commands print **nothing at all** and exit 0 — no `[]`,
no envelope `[verified live for data-safe target-database list]`. An empty stdout means
"no rows in this compartment and region", never "nothing to worry about". Say which
compartments and regions you read, and whether the service is onboarded at all.

Docs: https://docs.oracle.com/en-us/iaas/scanning/home.htm ·
https://docs.oracle.com/en-us/iaas/data-safe/index.html
