Purpose: get row-level cost and usage out of OCI, including the FOCUS export.
Source: research/09c B6, research/04b §20; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. Where the files actually are

They are **not in your tenancy**. Oracle drops them into an Oracle-owned Object Storage bucket
in namespace **`bling`**, in a bucket **whose name is your tenancy OCID**. That name is why
every listing here has to be redacted before it leaves the workspace.

Access needs a one-time cross-tenancy pair in the root compartment — an ordinary bucket policy
will not do it:

```
define tenancy usage-report as <Oracle's published usage-report tenancy OCID>
endorse group <group> to read objects in tenancy usage-report
```

The OCID is published verbatim in the Oracle docs page linked below; it is Oracle's reporting
tenancy, not yours, and not a secret. Copy it from the docs rather than from any command output.

## 2. Reading the bucket

```bash
oci os object list --namespace-name bling --bucket-name "$TENANCY_ID" --delimiter / --limit 20 --query 'prefixes' --profile "$PROFILE" --region "$REGION"
```

```bash
oci os object list --namespace-name bling --bucket-name "$TENANCY_ID" --prefix reports/cost-csv --limit 5 --query 'data[].[name,size]' --profile "$PROFILE" --region "$REGION"
```

```bash
oci os object get --namespace-name bling --bucket-name "$TENANCY_ID" --name "$OBJECT_NAME" --file ./cost.csv.gz --profile "$PROFILE" --region "$REGION"
```

Two top-level prefixes exist: `reports/` (the classic `cost-csv/` and `usage-csv/` files) and
**`FOCUS Reports/`**, the FinOps Open Cost & Usage Specification export, partitioned
`FOCUS Reports > YYYY > MM > DD` [verified, research/09c B6]. FOCUS is the better target for
cross-cloud tooling; the proprietary CSVs carry more OCI-specific columns.

Corrected listings returned both FOCUS and classic cost reports [verified, 2026-09-09].
The previous empty-result claim came from an incorrect JMESPath projection.

## 3. What the rows contain

- Cost CSVs carry `cost/*` columns, including `myCost` and `unitPrice`; usage CSVs carry
  `usage/*` consumption quantities. Both carry `tags/<namespace>.<key>` columns, which is the
  payoff for cost-tracking tags [verified, research/09c B6].
- Generated **every 6 hours**, one row per resource per hour, **retained one year**, and data
  can lag **up to 24 hours** — a report is never a real-time answer [doc, research/04b §20].
- Corrections arrive as **new rows** with `lineItem/iscorrection` set and
  `lineItem/backReference` pointing at the corrected line's `referenceNo`. Never diff two
  snapshots as if rows were mutable [doc].
- Files split at **1,000,000 records**: `...-00001.csv.gz`, then `-00002` [doc].

## 4. When there is nothing there

First inspect the raw response shape: `data` is an array and `prefixes` is its sibling.
Then distinguish failed reads from successful empty listings:

1. The `define`+`endorse` pair was never created — reads then fail as `NamespaceNotFound` or
   `BucketNotFound`, rather than a successful empty inventory.
2. Reports depend on metering history. Free account status alone does not prove that no
   report files exist; this reference tenancy has files.
3. The window predates the tenancy's first metered usage.

In all three, fall back to the Usage API, which answers from the metering service directly and
needs only `read usage-report`. Do not report "no spend" from an empty bucket.

## 5. Scheduled delivery instead of polling

`oci usage-api schedule` writes a recurring report into a bucket **you** own, with
`--result-location`, `--schedule-recurrences` and `--time-scheduled` all required on create
[verified, help]. That is a mutation and belongs to the user; the read side is
`schedule list` / `scheduled-run list`, which returned `[]` here [verified, executed].

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/usagereportsoverview.htm ·
https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/costanalysisoverview.htm
