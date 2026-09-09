# Model-backed routing evaluation — 2026-09-09

V19 in docs/validation-matrix.md is red because the offline proxy is lexical. The description-only judge labels below are a separate measurement; they do not establish the host-routing or task gates in plan §2.8.

Method: two independent judge agents (claude-sonnet-5) each received ONLY the skill names + descriptions of one arm and the 120 prompts of
evals/corpus/eval-corpus.json (80 routing + 40 negatives) as id+text, with expected_skill and trap_class stripped, and labelled the single
skill a router would activate or null. Labels: evals/results/routing-model-{this-pack,adibirzu}.json. Scorer: scripts/eval/score_routing_model.py. Corpus expected names were remapped to the v2.1 merged skill set before scoring (see note_v2_1 in the corpus).

    this-pack    fired on OCI prompts 80/80 (100%) | exact expected skill 78/80 (98%) | fired on negatives 0/40
    adibirzu     fired on OCI prompts 60/80 (75%) | exact expected skill 2/80 (2%) | fired on negatives 0/40

Remaining misses in this pack (2/80): R02 (navigator vs tenancy-governance, "what is the OCI equivalent of an Azure resource group") and
R68 (dr-backup vs block-file-storage, "remove a boot volume backup policy") — both are defensible either way; left as-is to avoid tuning
descriptions to the corpus. adibirzu exact-match is not comparable (different skill taxonomy); its fired-rate on OCI prompts (60/80) is the
coverage comparison. Limits: single judge model, single run, descriptions only (no body), no host routing; reproduce by re-running the two
judge prompt in [evals/routing-judge-prompt.md](../evals/routing-judge-prompt.md) and `scripts/eval/score_routing_model.py`. The label files lack independently verifiable run IDs and model/date metadata; the judge attribution above is the recorded claim, not newly measured provenance.
