# Fusion and NetSuite health

Start with the user's product, account/environment, region/realm, identity provider, time window and failing action. Avoid collecting employee, financial or customer records when status and correlation IDs can establish the failing layer.
Fusion OCI APIs manage environment families/environments and related operational activities; business REST/SOAP APIs use Fusion application roles and endpoints. A refresh or masking activity is a mutation with data consequences. Do not execute it to repair a vague health symptom.
NetSuite has no generic OCI CLI service group in the 3.91 inventory. Route account/record tasks to its documented SuiteTalk/SuiteCloud application interfaces and authorized account roles. Do not substitute Fusion APIs or infer NetSuite account availability from an OCI compartment list.
Separate service incident, OCI work request, IdP authentication, application authorization, integration failure and client/network error. A successful metadata read proves only that layer. A useful escalation packet contains redacted timestamps, operation/error, correlation IDs and the affected boundary, with no session cookies, tokens or business payloads.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| NotFound | Wrong static path / wrong API version / typo'd service endpoint | id 14 [unverified] |
| NotAuthorizedOrNotFound | Deliberate ambiguity: missing resource OR missing policy OR wrong region OR wrong compartment | id 13 [unverified] |
