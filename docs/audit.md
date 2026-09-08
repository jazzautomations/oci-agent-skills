# Audit synthesis and provenance

Reviewed 2026-09-08. Original research inspected the repositories below and produced
local notes, command inventories and MCP stdio results. This document records the
decisions reused in the package. Private research transcripts and unredacted smoke
output are deliberately excluded from distribution.

## Reference repositories

| Source | Useful contribution | Decision in this package |
| --- | --- | --- |
| [adibirzu/oci-skills](https://github.com/adibirzu/oci-skills), commit `a4fbf70fd26d1a1c820261a7d4761ebb55457c84` | Scoped context, plan review, CLI-help verification, domain breadth | Reuse design ideas; author smaller skills and verify our own examples. No mandatory router hook or broad safety claims based on command-name heuristics |
| [marcocanto/oci-support-request-skill](https://github.com/marcocanto/oci-support-request-skill), commit `be4dcf27eafea066e2ba95924aee2ebd1b808864` | Exact command argument arrays, bounded inspection, metadata projection, conditional changes | Use fixed read operations, explicit scope and projected output |
| [araidon/oci-skills](https://github.com/araidon/oci-skills) | Diagram generation from concise specs and reusable assets | Keep diagramming outside the initial runtime; prefer code-generated artifacts over huge inline image payloads |
| [cvranjith/arch-diagram-skill](https://github.com/cvranjith/arch-diagram-skill) | Architecture review and reproducible visual deliverables | Use architecture/ownership decisions; do not copy a personal workspace wholesale |
| [oci-ai-architects/claude-code-oci-ai-architect-skills](https://github.com/oci-ai-architects/claude-code-oci-ai-architect-skills) | AI and architecture topic discovery | Treat prose as research leads; validate syntax, names and product availability separately |
| [Oreo-Tech/oci-mcp](https://github.com/Oreo-Tech/oci-mcp) | Task-oriented inventory and compartment scoping | Do not import its mixed read/action tool surface; fixed read adapter instead |
| [jasonwilbur/oci-pricing-mcp](https://github.com/jasonwilbur/oci-pricing-mcp) | Cached pricing and explicit cost-calculator workflows | Document pricing as a separate current-data problem; do not ship stale price claims |
| [oracle/mcp](https://github.com/oracle/mcp), commit `e3cdae7fad817173ef62882f4d04b6baa32f0be2` | Shared auth, API discovery, typed schemas and server implementations | Depend on `oracle-mcp-common==0.1.3`; expose a smaller fixed read subset with consistent bounds |

These are idea/provenance relationships, not a claim that upstream code was merged
or that every upstream feature was reimplemented. Runtime dependencies retain their
own licenses. New package code/instructions were authored for this repository.

## Findings that changed implementation

**Authentication was inconsistent across the Oracle servers.** Some typed servers
assumed a session-token file even when an API-key profile was selected. The shared
authentication library supports multiple modes, so the adapter depends on it rather
than reproducing individual server factories. Only API-key auth was exercised live;
the existence of library support does not count as a live principal-auth test.

**Pagination and output limits were not uniform.** Some implementations consumed all
pages, others treated page size as an overall result limit, and others omitted
continuation information. The new tools issue one bounded page and report count,
truncation and cursor explicitly. Metadata/user data/tags are excluded by field
projection. Tests cover unexpected page shapes and actual cursor continuation.

**Broad command execution is not a read-only boundary.** Operation-name denylists
and descriptive hints cannot establish the behavior of arbitrary commands. This
adapter has no generic executor and exposes only reviewed SDK reads. No mutation
or dangerous-command reproduction was needed for validation.

**Tool discovery and successful operational reads are different tests.** Recovered
upstream smoke results showed successful initialize/tools-list for Compute, Identity,
Usage and Limits while their attempted reads returned errors. Those results are not
reported as successful integrations. The new adapter passed the actual reads for
these domains. Upstream Database/Load Balancer/Cloud/API/Pricing had some successful
reads in the recovered evidence; this is historical evidence, not a current blanket
compatibility guarantee.

**Command paths are surprisingly nonuniform.** Budgets use
`budgets budget budget list`, database systems use `db system list`, and available
Resource Manager Terraform versions use `resource-manager stack list-terraform-versions`.
The help validator found and corrected a new example typo during this build. The
catalog records installed syntax instead of extrapolating resource names.

**The CLI can return successful empty output.** Some list commands intentionally
emit nothing when the result is empty. The live checker distinguishes that successful
case from a failed process, malformed nonempty output or HTTP access error. It also
removes `OCI_CLI_AUTO_PROMPT` entirely for noninteractive checks, because mere presence
enables prompting even with a text value of `False`.

**One large database schema is expensive agent context.** The recovered Database
server advertised 147 tools; the new runtime has nine focused tools. Database SQL,
APEX delivery and other product control planes remain separate workflows instead
of automatically loading every integration into each conversation.

## What remains outside validation

The regenerated CLI/SDK catalog measures the installed distribution, not all public
or private Oracle APIs. It does not certify that every method works in every realm,
region, license or account. Original broad research tracks about certification
objectives, every SDK language's runnable recipes and exhaustive managed-service
deployment patterns were unfinished; their unverified scope is documented in
[the product map](oracle-product-map.md) and [SDK guide](sdk-and-devops.md).

This release makes that research useful through bounded working tools, operational
skills and explicit coverage. It does not claim to be the best possible package,
an exhaustive Oracle inventory or an independently certified security product.
