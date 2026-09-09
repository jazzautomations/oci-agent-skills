# Four-arm offline comparison — 2026-09-09

Reproduce: `uv run --frozen --project runtime python scripts/eval/head_to_head.py --json evals/results/head-to-head.json --markdown docs/head-to-head.md`.
Refresh competitor snapshots from the named research checkouts with the same command plus `--refresh-snapshots`. The shipped snapshots carry the original MIT/UPL notices. No competitor server is launched.

All arms receive identical unedited prompts, the same description matcher, one deterministic run, no model or temperature, and no placeholder substitution or tenancy access. Arm order is seeded and shuffled. Arm b retains every shipped skill, including its router. A domain crosswalk maps equivalent b routes; it is scoring-only and never enters selection. Arm c uses both servers' tool descriptions and scores discovery-interface choice; it does not prove correct API operation selection. That asymmetry is not averaged with skill routing. Bare has no descriptions, so it abstains: it is not a measurement of a bare model's knowledge.

| Arm | Routing proxy | Negative firing rate | Authored fence validity | Unconfirmed guard exposure | Resident token estimate |
|---|---:|---:|---:|---:|---:|
| This pack | 37.5% | 0.0% | 100.0% / 277 | 0/20 | 6386 |
| adibirzu skills | 13.8% | 0.0% | 14.0% / 114 | 20/20 | 4218 |
| Oracle API + Cloud tools | 6.2% | 0.0% | unmeasured (no authored fences) | 5/20 | 823 |
| Bare descriptor baseline | 0.0% | 0.0% | unmeasured (no authored fences) | 20/20 | 0 |

Order: c, b, d, a; seed 42. Token estimates use characters / 4 rounded up. Arm a includes actual serialized MCP schemas; arm c is a **description-only lower bound**, not a full schema floor. Arm b additionally ships a UserPromptSubmit router injection of approximately 1044 tokens per turn; the static matcher does not simulate it. Research's statement that b has no hook means no mutation guard: its prompt hook exists.

Guard exposure counts inert mutation fixtures that an available guard would allow or leave unprotected, five replays per case. Arm c measures only its CLI denylist; Terraform is outside its tool surface, and SDK invocation protection remains unmeasured. These are not executed mutations or agent confirmation behavior. The same authored-fence linter grades skill bodies and their directly referenced documents in both skill arms. The known forwarding wrapper spelling oci_cli is normalized to oci for syntax lint only; arbitrary wrapper chains are not interpreted. No authored output exists for c/d, so their command-validity metric is unmeasured, not fabricated as zero or perfect.

The raw JSON contains every routing, negative, task-retrieval and guard-replay result, plus per-case a-minus-d retrieval deltas for routing and tasks. A nonpositive delta is an offline review candidate; it cannot justify deleting a skill without a model-backed baseline. Behavioral task scores, generated-command validity, leakage and live injection remain unmeasured. V19 is red; V27 and the original live V28 cannot be established by this offline comparison. Owners: evaluation/routing maintainers for V19 and V28; Claude early-access provider plus evaluation maintainers for V27. The requested four-arm offline comparison is complete.
