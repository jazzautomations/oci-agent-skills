# Data Pump movement

There is no OCI Data Pump command. Use expdp/impdp or DBMS_DATAPUMP with a separately reviewed database credential, dump directory/object destination and schema mapping. ADB uses DBMS_CLOUD credentials or an approved resource principal; OCI auth tokens are not console passwords.

Export can disclose data and writes dump objects; import writes database objects. Both are out of the read-only scripts. Before import review source/target versions, character sets, tablespaces, unsupported objects, remaps and a rollback schema. Check current ADB import exclusions and parallelism rather than copying a historical ECPU formula as universal. A Data Pump dump is a logical migration artifact, not evidence of physical RMAN recovery. Logs/dumps may contain PII and must stay outside the repository. End-to-end Data Pump remains [unverified].

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| `ORA-12541: TNS:no listener` | Wrong host/port, or the ADB is **STOPPED** | id 101 [unverified] |
