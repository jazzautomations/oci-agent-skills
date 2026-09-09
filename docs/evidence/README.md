# Evidence index

These reports retain their measurement date and scope. Moving them into this
directory does not rerun a probe. Generated reports may include historical source
paths; those paths identify the original measurement rather than current links.

| Report | Scope |
|---|---|
| [Release matrix](validation-matrix.json) | Structured V1–V28 outcomes and owners |
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
Regenerate current release evidence outside the checkout with
`uv run --frozen --project runtime python scripts/ci/release_gate.py`; review its
diffs before replacing a report. Never convert failed or unavailable probes into
successful empty results.
