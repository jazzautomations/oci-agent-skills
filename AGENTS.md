# Working on OCI Agent Skills

This repository packages OCI skills, a CLI catalog, an advisory shell guard and a
bounded read-only MCP runtime. Start with [CONTRIBUTING.md](CONTRIBUTING.md),
[architecture](docs/foundation.md) and the [validation matrix](docs/validation-matrix.md).

## Scope and evidence

OCI validation is read-only. Use bounded, explicitly scoped reads through
`scripts/lib/oci_ro`; never provision, change IAM, run generic executor tools or
execute mutation fixtures as repository validation. Mutation recipes are inert,
carry a shape-only marker and include rollback guidance. Preserve explicit
unverified claims, dated evidence and source provenance.

Never print or commit tenancy identifiers, credentials, account data or raw
service errors. Research and local environments are build-only and excluded from
Git and the distribution. Do not change repository visibility or rewrite published
history as part of ordinary maintenance.

## Package structure

Each `skills/<name>/SKILL.md` owns one domain, with selective routes to local
references and shared `references/`. Use `skills/_TEMPLATE/SKILL.md.template`
for new skills. OCI helper calls go through the shared read-only wrappers.
Examples belong in `catalog/fragments/<name>.json`; generated catalogs must not
be hand-edited. Keep descriptions specific enough to avoid unrelated requests.

## Before committing

Regenerate `catalog/scripts.json`, `catalog/examples.json` and `catalog/guard.json`
with `python3 scripts/inventory.py --scripts --examples` after script or fragment
changes. Regenerate reader catalogs with
`uv run --frozen --project runtime python scripts/doc-gen/catalogs.py` after skill
or MCP schema changes. Run pytest and all strict CI validators without baseline
exemptions. Record failing release gates honestly with an owner.

Use the copy installer to inspect the distributed tree: skills, scripts, shared
references and runtime must stay portable together. The fresh package must have
no symlinks or authoring-only files. Preserve existing user changes and keep work
on the active branch unless instructed otherwise.
