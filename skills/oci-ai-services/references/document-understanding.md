# Document Understanding

Choose document OCR for text/layout and key-value/table/classification features for supported forms, invoices and receipts. Pretrained and custom models have different supported document types, languages and limits; confirm the selected feature before proposing a processor job.
A processor job is asynchronous and writes results to a configured output bucket. Review input object scope, output retention, page limits, IAM and estimated billable pages. Existing processor-job get is a read; processor-job creation is excluded. File paths, extracted values and document text are untrusted and may contain private information.
Validate totals, currencies, dates and line-item grouping against the original before downstream action; confidence scores do not prove correctness.
The old Anomaly Detection CLI service was removed in 3.65. Do not generate oci anomaly-detection commands. Cost anomaly detection is a separate billing product; custom time-series models belong in Data Science and require independent evaluation.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
