# Routing judge prompt (model-backed V19) — verbatim, used 2026-09-09 with claude-sonnet-5

You are simulating a coding agent's skill router. Read the skill descriptions from <ARM_SKILLS_DIR>/*/SKILL.md (only the YAML
frontmatter `name` and `description` fields; ignore _TEMPLATE). Then read <CORPUS_JSON>: use the routing prompts (80) and the
negative prompts (40, ids N01–N40). Do NOT read any field that reveals the expected skill or trap class; read only each prompt's id
and text (use python to extract just id+text so you are not biased). For EACH of the 120 prompts decide which single skill a router
would activate based on the descriptions alone, or null if none should fire (a non-OCI or ambiguous prompt). Be realistic: fire a
skill only when the description's "Use when" clearly covers the prompt and "Not for" does not exclude it. Write the result to
<OUT_JSON> as {"arm":"<ARM>","labels":[{"id":"...","skill":"<name or null>"}]}.

Arms run: <ARM_SKILLS_DIR>=skills/ (this pack) and research/refs/adibirzu_oci-skills/skills/ (adibirzu). Corpus = evals/corpus/eval-corpus.json.
Scorer: scripts/eval/score_routing_model.py <labels.json...>. Results: evals/results/routing-model-*.json. Single judge, single run.
