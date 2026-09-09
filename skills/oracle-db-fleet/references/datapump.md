# Data Pump movement

There is no OCI Data Pump command. Use expdp/impdp or DBMS_DATAPUMP with a separately reviewed database credential, dump directory/object destination and schema mapping. ADB uses DBMS_CLOUD credentials or an approved resource principal; OCI auth tokens are not console passwords.

Export can disclose data and writes dump objects; import writes database objects. Both are out of the read-only scripts. Before import review source/target versions, character sets, tablespaces, unsupported objects, remaps and a rollback schema. Check current ADB import exclusions and parallelism rather than copying a historical ECPU formula as universal. A Data Pump dump is a logical migration artifact, not evidence of physical RMAN recovery. Logs/dumps may contain PII and must stay outside the repository. End-to-end Data Pump remains [unverified].
