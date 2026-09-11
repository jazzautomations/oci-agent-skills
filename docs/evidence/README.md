# Evidence index

These reports retain their measurement date and scope. Moving them into this
directory does not rerun a probe. Generated reports may include historical source
paths; those paths identify the original measurement rather than current links.

| Report | Scope |
|---|---|
| [Review demo](review-demo.json) | Offline catalog, inert command classification and actual MCP stdio checks; implementation input hashes |
| [Release matrix](validation-matrix.json) | Structured V1–V28 outcomes and owners |
| [Service prerequisites](service-prerequisites-2026-09-11.json) | Seven selected read operations, no mutations, and 582 local tests |
| [Offline follow-up](offline-followup-checks-2026-09-11.json) | 577 tests, inference-free default gate, historical regression and separate cost accounting |
| [Task repair final checks](task-repair-final-checks-2026-09-11.json) | Earlier dated regressions, offline examples and explicit generic-validator incompatibility |
| [Checked-task summary](checked-task-summary-2026-09-11.json) | Opt-in paired scores, actual tool counts, timings and cumulative known costs |
| [Release metrics](release-metrics.json) | Counts, classifier replay and context estimates |
| [CLI reads](validation-cli.json) | Selected live reads and syntax-only examples |
| [Helper scripts](validation-scripts.json) | Live script probes, failures and missing prerequisites |
| [Helper diagnostics](helper-diagnostics.json) | Revalidated posture checks and scoped service error codes |
| [MCP smoke](validation-mcp.json) | Selected bundled tool reads |
| [Offline examples](validation-examples-offline.json) | Command-shape checks without OCI calls |
| [Public links](validation-links.json) | Dated documentation URL checks |
| [Guard severity](guard-severity-matrix.json) | Classifier replay over a frozen severity snapshot |
| [Context measurement](context-measurement.json) | Host framing measurement and estimate boundaries |
| [Plugin discovery](plugin-host-discovery.json) | Recorded host tool registration |
| [Oracle MCP research](oracle-mcp-research.json) | Archived upstream discovery and operational results |
| [Denylist research](denylist-coverage-research.json) | Historical matching and classification results |
| [Certification research](certification-coverage-research.json) | Historical taxonomy mapping; not a certification claim |
| [Final audit findings](final-audit-findings.json) | Original findings; consult the current matrix for resolution |

Evaluation result files remain under [evals/results](../../evals/results).
The [semantic-selection trials](../../evals/results/semantic.json) and
[scope regressions](../../evals/results/semantic-boundaries.json) contain current
input-bound model evidence. [Development trials](../../evals/results/semantic-development.json)
retain the failed iterations. The [investigation](../semantic-routing.md) explains
why the lexical proxy was replaced and what these component tests cannot prove.
Regenerate current release evidence outside the checkout with
`uv run --frozen --project runtime python scripts/ci/release_gate.py`; review its
diffs before replacing a report. Never convert failed or unavailable probes into
successful empty results.
