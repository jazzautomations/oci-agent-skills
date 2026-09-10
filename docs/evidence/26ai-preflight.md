# 26ai preflight — 2026-09-10

Read-only, explicitly scoped to the configured profile and `us-chicago-1`. No database
was created and no SQL or model inference ran. Account identifiers and raw responses
are excluded from this report.

| Check | Observed |
|---|---|
| oci | 3.91.0 |
| java | openjdk version "21.0.12" 2026-07-21 |
| sql | missing |
| oracledb | missing |
| Advertised database versions | 19c, 23ai, 26ai |
| GenAI catalog | Bounded sample of 50 entries; active state can coexist with a past retirement date |
| GenAI limits | Read succeeded; usable inference quota remains a prerequisite |

Version listing is not a capacity reservation or proof of provisioning eligibility.
Recheck the model ID, retirement date and usable quota in the target region immediately
before the optional Select AI setup. No model in this sample is selected automatically.

Pending: install the documented SQLcl and Python prerequisites in the demo environment,
then run the separately authorized database session, SQL/index/load/query validation
and confirmed cleanup. Fake-connection tests establish local behavior only.
