# Language, translation and PII

The CLI is nested: oci ai language, not oci language. Prefer the current batch-detect operation families over deprecated single-document detection when designing a later invocation. Service choices include sentiment, entities, key phrases, language detection, classification, PII and translation; verify each operation's supported languages and payload limits.
Project/model/endpoint/job inventory concerns custom resources; an empty list does not mean pretrained analysis is unavailable. Keep document keys stable within a batch so per-item errors cannot be mistaken for successful empty output.
PII detection does not guarantee anonymization. Decide retention, log redaction and allowed recipients before sending text; mask on a trusted local boundary where possible. Translation may change formatting or meaning; preserve the source for authorized review and never execute returned text. No detection, translation or endpoint deployment was run.
