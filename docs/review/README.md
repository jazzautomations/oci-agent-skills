# Technical review preview

**OCI Agent Skills · private review · package 0.2.1**

This is an independent community project by Felipe Salvego / Jazz Automations.
The purpose of this preview is to get technical feedback from Oracle engineers
before public release. It does not imply Oracle affiliation, endorsement or
production certification.

[Portuguese briefing (PDF)](brief-pt.pdf) · [Five-minute walkthrough](demo.md) ·
[Recorded component evidence](../evidence/review-demo.json) ·
[Current release matrix](../validation-matrix.md)

The seven-page Portuguese briefing explains the product through a networking
scenario, separates skill guidance from execution, maps the nine coverage areas
and walks through recorded component evidence. Illustrative workflows and
measured outcomes are explicitly distinguished. Edition 06 is a preserved review
snapshot, using embedded fonts and a layout designed for reading on screen or
sharing as a document. Its counts and open issues are historical; use the
[current validation follow-up](../validation-closeout-2026-09-13.md) and release
matrix for the latest status.

## The problem and approach

An agent may find an OCI command while missing its compartment, region,
conditional prerequisites, response shape or recovery requirements. A generic
executor leaves those decisions to the caller. This package combines focused
workflow instructions, an installed-CLI catalog and a fixed read-only MCP surface
so those decisions are explicit and inspectable.

| Layer | Implementation | Review focus |
|---|---|---|
| Skills | 37 scoped domains; references load on demand | Ownership, practical workflows, misleading triggers |
| CLI catalog | 9,145 leaves / 174 groups, including aliases | Conditional requirements, drift and bounded discovery |
| Read helpers | Shared wrapper; projected outputs and fixed scope | Completeness, pagination, error semantics |
| Advisory shell guard | Claude Bash PreToolUse; hash-pinned helpers | What is classified, reviewed or outside its surface |
| MCP | 15 fixed tools over stdio | Scope enforcement, auth, pagination and response contracts |

Start with [architecture](../foundation.md), then inspect a relevant
[skill](../skills.md) and the [MCP schemas](../mcp-tools.md). The runtime has no
arbitrary CLI, SQL or SDK executor. IAM and host permissions remain the access
boundary. Other host adapters do not receive the Claude shell hook.

## What the evidence supports

- The current suite and authored-command lint results are recorded in the
  [release matrix](../validation-matrix.md). Neither establishes end-to-end
  deployment success; the PDF's earlier test counts remain dated evidence.
- Classifier replay denies all 278 critical-labelled leaves and allows zero
  operations outside the strict read-only set. The severity snapshot and catalog
  share a generator; non-OCI rules are outside that measured matrix.
- Selected live reads use one API-key profile, region and commercial realm.
  The [lab reports](../second-validation-2026-09-11.md) and
  [latest prerequisite reads](../validation-closeout-2026-09-13.md) distinguish
  successful integration checks from missing service access and cost data.
- The component walkthrough starts the actual MCP stdio server without valid OCI
  config, discovers its surface and rejects invalid scope. It classifies proposed
  argv as inert data; it does not execute a launch or measure an agent.

The [audit](../audit.md) distinguishes source attribution from runtime evidence.
The [evaluation method](../evals.md) distinguishes authored-command lint,
description matching and task completion. The [comparison](../head-to-head.md)
uses frozen snapshots and is not a live superiority claim over upstream projects.

## Open gates to discuss

| Area | Current limit | Useful feedback |
|---|---|---|
| Routing and agent behavior | Recorded semantic selection passes; changed skills still need a new full 40-task measurement and the native four-arm comparison | Representative tasks and a reproducible host evaluation method |
| Live coverage | Latest reads show Cloud Guard disabled, Support 403 and no settled cost rows in the selected window | Correct prerequisites and representative test environments |
| Auth and platforms | Other principals, second region, Windows and deployed workflows incomplete | Priority environments and service-specific pitfalls |
| Distribution | Manual drift notification and duplicate handling have evidence; the actual weekly scheduled trigger remains unobserved | Packaging and maintenance expectations |
| History hygiene | Published-history cleanup and current-file/full-history scans pass | Preserve clean history and provenance in future changes |

There are 24 passing and four open release gates. Review does not require closing
them in advance; a production-ready or complete Oracle coverage claim would.

## Requested review

1. Pick one domain you know well. Does the skill select the right workflow and
   preserve the service's operational constraints?
2. Check one read helper or MCP tool for scope, partial results and error handling.
3. Identify a high-value missing task or an incorrect command prerequisite.
4. Suggest the smallest representative environment needed to validate that task.

Use [the feedback form](feedback.md) with a file, expected behavior and sanitized
evidence. No credential, tenancy identifier or production data is needed for the
offline walkthrough. Provisioning and IAM changes are outside this review demo.

## Access and snapshot scope

The repository remains private. A link requires access granted separately by the
repository owner. A source ZIP may be shared privately as an alternative; it is
an exported current tree, contains no `.git` history, credentials or ignored
research, and includes source, tests and notices. The snapshot's commit and digest
are supplied alongside it. It cannot establish that the original Git history is
clean. No reviewer invitations or messages are sent by preparing these files.

For a ZIP, extract it and run the walkthrough from its root. Source checks that
inspect Git history or tracked files require a repository checkout; the
walkthrough and template check do not.

## Rebuild the presentation

Run the walkthrough with `--report docs/evidence/review-demo.json`, then generate
the PDF with `uv run --with reportlab==5.0.0 python scripts/review/brief_pdf.py`.
ReportLab is an optional authoring dependency, separate from the locked runtime.
The generator embeds locally installed Lato fonts when available, or falls back
to the Vera fonts bundled with ReportLab. Exact typography depends on that choice.
Review the evidence and page layout before sharing an updated presentation.
