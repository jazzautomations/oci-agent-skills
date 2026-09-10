# Cloud assessments and 26ai preparation — 2026-09-10

Scope: handoffs 11–13. No OCI provisioning, IAM changes, database SQL or source-cloud
account access. The cost-band correction was committed first, separately.

- FinOps: 56 scoped live reads in us-chicago-1, hashed resource references, explicit
  coverage gaps and no aggregate promised savings. The final metric/multi-attachment
  refinements have mocked regression evidence; resource types absent from this account
  remain unverified live. See the [sample](evidence/finops-sample-report.md).
- Migration: synthetic AWS inventory through normalization, live public list prices,
  comparable subsets and draft Core Landing Zone inputs. GCP/Azure adapters have local
  shape tests; no source credentials. See the [sample](evidence/migration-sample-report.md).
- 26ai: local dry-runs and fake-connection tests; scoped preflight advertises 26ai but
  SQLcl/driver setup and the database session remain pending. See [preflight](evidence/26ai-preflight.md).
- Freshness: two reads of all 12 official sources succeeded; the second matched the
  reviewed baseline. Price caches expire after 24 hours; a failed refresh is unknown.
  The daily workflow is configured; a manual hosted run passed. A scheduled invocation
  has not yet been observed. See [hosted evidence](evidence/cloud-freshness-hosted.json).

Validation: the full post-merge suite passed **450 tests**. Strict metadata, references, portability,
budgets, licenses, current-tree secret scan, read-only script registry, stencil, manifests
and fence lint pass. Both Claude plugin validators pass. CLI example resolution and the
9,145-command census match. New/changed skill fences were checked against CLI help.
The copy installer produces 37 skills without authoring files or symlinks before runtime
setup. Disk pressure required UV_LINK_MODE=symlink for temporary dependency installation;
the distributed package itself remains copied, with no symlinks.

Release gaps at the `2a6e9a9` handoff are recorded below. The subsequent
Classic scope repair and current semantic results are in [the evaluation guide](evals.md);
the historical V20 failure is retained here for provenance.

| Gate / prerequisite | Evidence | Owner |
|---|---|---|
| V20 negative routing | Seed 29 selected navigator for excluded historical OCI-C; 1/40 negative firings. Seed 17 has zero. Both recorded, no relabeling or threshold change. | Evaluation/routing maintainers |
| V22 history | Four pre-existing email matches in historical patch bodies; current-tree scan passes. No history rewrite. | Repository history owner |
| V25/V27/V28 | Prior scope/prerequisite and native host/behavioral evidence gaps remain; this feature build does not close them. | OCI operator / evaluation maintainers |
| 26ai integration | No live SQL, index, retrieval-quality or teardown evidence; install prerequisites and use a separately authorized dedicated DB. | Demo operator |

V19 selection accuracy is 96.25% and 95.00%, with 4/4 overlap pairs in both trials;
12/12 additional boundaries pass. See [current evaluation](evals.md). This is a development
benchmark, not a holdout or a native agent task score. The repository is not release-ready.
