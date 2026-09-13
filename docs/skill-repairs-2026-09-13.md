# Skill repairs — September 13, 2026

The repair cycle found contradictory A1 pricing and authentication guidance,
unsafe scope changes after authorization errors, and a numeric false negative in
the task grader. Changes preserve all 37 skill names and descriptions, original
task prompts, fixture answers and historical scores.

## Changes and evidence

- **A1 planning:** distinguish service limits, public PAYG price bands, documented
  free allowances and actual usage. A larger provisioning limit cannot establish
  a zero bill. Oracle's [Always Free documentation](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
  states 1,500 OCPU-hours / 9,000 GB-hours; the September 13 public price API still
  returned a 3,000-hour zero-price CPU band. Both observations are retained. The
  worked example now computes 2 OCPUs / 12 GB without promising account charges.
- **Identity and scope:** remove alternate-principal probes, the claim that a 404
  identifies a machine principal, automatic administrator/root retries and advice
  to strip a compartment selector. Runtime-managed principals remain valid for
  unattended work. Error handling follows the selected identity and target;
  [Oracle's API error reference](https://docs.oracle.com/en-us/iaas/Content/API/References/apierrors.htm)
  retains 404 ambiguity and identifies 501 as nonretryable.
- **Governance:** preserve the user's Terraform workflow, assess specific CIS
  controls instead of declaring compliance from an account label, and distinguish
  free pricing from [Cloud Guard's paid-tenancy prerequisite](https://docs.oracle.com/en-us/iaas/Content/cloud-guard/using/prerequisites.htm).
  Blocked actions preserve the requested output contract. Reference examples are
  optional diagnostics, not mandatory discovery sweeps.
- **Task grading:** compare finite JSON numbers by value. `20.0` and `20` match;
  booleans, strings, nonfinite values, extra fields, reordered arrays and unequal
  numbers still fail. Evidence receipts and command checks remain required.
  Nineteen new regression tests cover these distinctions. Separately regrading
  the identical completed Zen observations changes only native T23; the original
  report remains untouched. This is evaluator correction, not measured model gain.
- **Installer diagnostics:** distinguish exhausted disk space, storage quota and
  permissions with fixed messages that disclose no private paths. Five regression
  cases retain generic handling for other I/O failures.
- **Instruction size:** replace duplicated untrusted-output prose in two skills
  with the essential constraints and a route to the shared contract. No token
  budget, validator threshold or routing description was relaxed.

## Validation

The [sanitized evidence](evidence/skill-repairs-2026-09-13.json) preserves report
and log hashes, separate numeric readjudication and targeted outcomes.

The complete repository suite passes **613 tests, three dependency warnings, in
36.09 seconds**. An earlier attempt hit `ENOSPC` (573 passes, two failures and
33 errors); its failure log is preserved. Temporary copies were compacted or
removed, then the entire suite was rerun successfully. A later run had 607 passes
and one generic installation-copy failure; its underlying I/O cause was not
captured. After the final corpus and installer changes, all 613 tests passed. Two historical replay
checks also failed in the initial scratch candidate because that archive lacked
Git history; they ran successfully in the complete checkout.

All **28 strict CI validator commands** passed on the completed changes, including
CLI-help lint, copy portability, reference and token budgets, script checks and
immutable historical-evidence replay. No thresholds or baseline exemptions were
changed.

An independent reader handled four realistic requests using the revised skills:
A1 budgeting without billing data, denied scoped quota reads, structured refusal
of an unavailable deletion and a six-hour instance-principal workload. It found
three additional contradictions, which were repaired; a follow-up confirmed
those corrections and preservation of the untrusted-output constraints. This
small qualitative review is development evidence, not a host comparison.

The generic skill-creator quick validator rejected the existing `compatibility`
frontmatter field. That optional field is supported by the [Agent Skills specification](https://agentskills.io/specification)
and the repository's strict frontmatter validator. It was retained; the generic
validator failure is not reported as a pass.

## Native OpenCode retest

A fresh installation had no symlinks and registered the same 37 skills. Three
known development cases ran once each on `opencode/mimo-v2.5-free`, with unchanged
source fingerprints throughout. T23 passed after activating monitoring. T39
returned prose around the required JSON without activating a skill; T37 activated
compute but also returned text outside the required JSON. Both retain strict
format failures: **one of three passed**. No parser relaxation or repeated attempt
was used to turn these failures green. Input hashes, completed-answer grading,
receipts and private archive hashes were checked offline.

This establishes one targeted pass and two unresolved host/model format failures.
It does not establish an improvement rate, a full task score or four-host parity.
No OCI command executed; the fixed observation and command-contract tools were
synthetic/inert. The official free endpoint was used without paid fallback.

After this retest, the final cross-check found the old administrator/root retry
instruction duplicated in error-corpus entry 45. That entry was corrected as well.
The user-lookup table was also aligned with its signer-ambiguity guidance.
The targeted host report therefore describes the preceding source state; the
exact tested patch and fingerprints are retained. It is not final-source model
certification. The installer error messages were then improved after another copy failure.
The final local suite and CI include these subsequent corrections.

## Remaining release criteria

The actual scheduled maintenance event (V24), missing live service access/data
(V25), qualifying current full-task evidence (V27) and original native-product
comparison (V28) remain open. The interrupted 27-pair Zen report is historical
after these source changes. Neither local test success nor a targeted regression
closes these four criteria. Visibility and licensing remain unchanged.
