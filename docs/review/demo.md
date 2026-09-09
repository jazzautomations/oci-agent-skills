# Five-minute technical walkthrough

Audience: engineers reviewing the package before public release. This is a
recorded component walkthrough, not a live agent task or cloud deployment.

## Before the meeting

Open the [review brief](README.md), [skills catalog](../skills.md) and
[recorded JSON](../evidence/review-demo.json). Use Python 3.13+ and `uv`.
From the repository or source ZIP root, install the locked runtime once:

```bash
uv sync --frozen --project runtime
```

Dependency setup can require package downloads. The walkthrough itself needs no
OCI credentials or service calls. It sets both OCI config selectors to an absent
file and removes inherited OCI environment selectors.

## 0:00–1:00 — scope before commands

Show `oci-networking` in the catalog and open its Scope check and Route sections.
Explain the intended request: “port 80 is open in the security list but the site
still times out from outside.” Show how the skill routes reachability rather
than claiming that a security rule alone proves the path is healthy.

This is a walkthrough of authored instructions. Do not describe it as a recorded
agent success or invent an instance, diagnosis or response.

## 1:00–3:30 — run the recorded component path

```bash
uv run --frozen --project runtime python scripts/review/demo.py --report /tmp/oci-review-demo.json
```

| Check | Observe | What it proves |
|---|---|---|
| Catalog | `compute instance list` requires `--compartment-id` | The shipped catalog exposes a required scope flag |
| Read classification | `allow` | The advisory classifier recognizes this read |
| Proposed write classification | `ask`, `executed: false` | The classifier requests review; no proposed command is executed |
| MCP stdio | 15 tools, `live: false`, invalid scope rejected | The actual server initializes and validates that input without valid config |

The guard receives JSON argv as text. It does not run those argv. This does not
test Claude's enforcement of a hook decision, IAM authorization or model behavior.
The report records hashes of the demo and its implementation inputs; compare them
before treating an older report as evidence for a changed tree.

## 3:30–5:00 — show the boundaries and ask for review

Open the [validation matrix](../validation-matrix.md). Point out the 22 passing
and six open gates, including routing, live prerequisites and host evaluation.
Ask the reviewer to choose one domain and identify a missing prerequisite,
incorrect API assumption or representative task to validate next.

If the walkthrough fails, retain the failed result and inspect that component.
Do not substitute a recorded success while presenting it as the current run.
Use the checked-in evidence only when clearly labelled as the dated previous run.

## Presenter notes in Portuguese

“Montei um conjunto de skills e ferramentas para agentes trabalharem com OCI com
escopo explícito e evidência verificável. Quero uma revisão técnica antes de
abrir o projeto. Vou mostrar como as peças funcionam e onde a validação ainda
está incompleta.”

“Essa demonstração inicial não chama a minha tenancy. Ela exercita o catálogo,
a classificação da guarda e o servidor MCP real. Depois queria escolher com vocês
um cenário representativo para testar o agente de ponta a ponta.”
