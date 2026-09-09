# Arm d

Bare: no descriptions or authored examples. Abstention baseline, not a bare model session.

## Source fairness rules

1. Identical prompt text, identical model, identical `--runs`, identical temperature per arm.
   Prompts are never re-tuned per arm; a prompt that only works with our vocabulary is a
   rigged prompt and must be rewritten in §2 instead.
2. Arms b, c, d get the **same** placeholder substitution and the same tenancy profile.
3. Every arm is scored by the same graders. Graders may not name a skill, a file path or a
   `references/` filename — only observable behaviour (command text, presence of a flag,
   absence of an OCID, whether a mutation ran).
4. Arm c has no skill layer, so `tool_used: Skill` is meaningless there — routing accuracy
   for arm c is scored on **tool selection** instead (did it call the right MCP tool), and
   that asymmetry is reported, never averaged away.
5. Run order is randomised across arms to keep tenancy-state drift from correlating with arm.


## Offline adaptation
Identical deterministic matcher and prompts, one run, no model/temperature, no tenancy or placeholder substitution. No competitor code executes. Seeded randomized arm order. Behavioral metrics remain unmeasured.
