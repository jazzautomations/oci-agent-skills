# Pre-authenticated requests
Source: research/04c Object Storage; research/14 §8.
A PAR is a bearer credential, independent of a consumer's OCI login. Choose the narrowest object/prefix and read/write mode for the actual sharing request; set an explicit expiry.
The access URI appears only at creation. Never record it in a repository, report or console log. List metadata to diagnose expiry and deletion; this cannot recover a lost URI.
Renewal requires a new PAR and consumer migration. Revoke only the specific PAR after authorization, with acknowledgement that the previous URL cannot be restored. A public bucket is not a substitute for a narrowly scoped PAR.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| plain `404` HTML/XML, no envelope | PAR expired or was deleted | id 81 [unverified] |
| ObjectNotFound | Key typo, or wrong `--namespace` | id 77 [unverified] |
