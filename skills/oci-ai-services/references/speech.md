# Speech transcription and TTS

Use existing transcription-job and transcription-task metadata to distinguish queued, in-progress, failed and completed work. Inspect task failures individually; a parent completion does not certify every file. Match source format, sample rate, channels, language and model support before a future submission; do not assume diarization or timestamps exist for every model.
TTS has separate voice/model/format selection and a billable data plane. Voice inventory is not synthesis. Do not create jobs or produce audio as an authentication probe. A retry may create duplicate work and charges; record a stable local request identity and check existing work first.
Object Storage input/output access and service principal policy are separate from the caller's job inspection privileges. Audio and transcripts can be sensitive; output locations and recognized text must follow the shared redaction and untrusted-output rules.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
| SignUpRequired | Service not enabled for the tenancy (common on Gen-AI, some ADB features) | id 12 [unverified] |
