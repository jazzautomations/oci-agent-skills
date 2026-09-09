# Tagging: namespaces, defaults, cost tracking, tag-based IAM
Source: research/09c B3 and B7, research/04b §6b; verified-on OCI CLI 3.91.0, 2026-09-09.

## Three flavours, constantly conflated
| Flavour | Shape | Cost-trackable | Usable in IAM conditions |
|---|---|---|---|
| Free-form | `{"key":"value"}`, no schema, no IAM control | never | no |
| Defined | `namespace.key = value`, schema-controlled | yes | yes |
| System | applied by services, e.g. `orcl-cloud.free-tier-retained` | n/a | read-only |

Only **defined** tags can be marked cost-tracking or referenced in a policy condition. A
"tagging strategy" built on free-form tags cannot produce a chargeback report.

## The floor every tenancy already has
Executed live 2026-09-09 in the reference tenancy: `oci iam tag-namespace list` returned
exactly `Oracle-Tags`, and `oci iam tag list-cost-tracking` returned `Oracle-Tags.CreatedBy`.
Every OCI tenancy ships one cost-tracking tag applied by a tag default at tenancy creation,
so "who created this" is answerable before any custom namespace exists. Use it as the
fallback for a first showback report; the same run showed `CreatedBy` and `CreatedOn` as tag
defaults with `is-required: false`.

## Practices
1. `--is-required true` **with a placeholder value** beats a required tag with no default:
   the latter silently blocks resource creation for anyone who does not know the tag exists.
2. `--validator` (ENUM) is what stops `CostCenter` drifting into forty spellings.
3. Cost-tracking tags are capped per tenancy (10 by default) — treat the slots as a budget.
4. `retire` a namespace or key rather than deleting it; deletion is a long cascade.
5. `oci iam tag-default assemble-effective-tag-set --compartment-id <c>` answers "what will
   actually be stamped here" better than reading defaults compartment by compartment.

Bulk paths worth knowing before proposing one: `oci iam tag bulk-edit`,
`oci iam tag bulk-delete`, and
`oci iam tag import-standard-tags --standard-tag-namespace-name Oracle-Standard`. All three
are tenancy-wide mutations — inventory first, propose second.

## Tag-based access control (why tagging is a security control)
Defined tags are the only tags usable in IAM policy conditions. Two forms:
- on the **resource** — `Allow group DevOps to manage instance-family in compartment dev
  where target.resource.tag.Ops.Environment = 'dev'`
- on the **principal** — `Allow any-user to use instance-family in compartment dev where
  request.principal.group.tag.Ops.Team = target.resource.tag.Ops.Team`

State the caveat out loud before recommending either: a tag-based policy is only as strong
as the tag's immutability. Anyone who can update a resource's defined tags can move it
across the policy boundary, so tag-write must itself be restricted (`Allow group X to use
tag-namespaces in tenancy` is the lever). Writing those statements is `oci-iam-policy`'s job,
not this skill's.

For **network** segmentation Oracle now pushes Zero Trust Packet Routing rather than
tag-based IAM: `oci zpr` plus `oci security-attribute`. ZPR security attributes look like
tags but are a separate namespace type, and an active Security Attribute Namespace blocks
`terraform destroy` until it is retired — the most-reported ZPR operational surprise.

Docs: https://docs.oracle.com/en-us/iaas/Content/Tagging/Concepts/taggingoverview.htm ·
tag defaults: https://docs.oracle.com/en-us/iaas/Content/Tagging/Tasks/managingtagdefaults.htm ·
advanced policy: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policyadvancedfeatures.htm ·
ZPR: https://docs.oracle.com/en-us/iaas/Content/zero-trust-packet-routing/home.htm

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
| NoEtagMatch | Optimistic-concurrency `if-match` stale | id 23 [unverified] |
