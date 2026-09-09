# TLS, wallets and ORA-12506

Read lifecycle state, mTLS requirement, ACL and connection-string metadata first. STOPPED after inactivity is expected; starting is a separate authorized write. APEX/ORDS can lag about five minutes after a start.

Wallet-less TLS requires mTLS not to be mandatory and the source egress IP to satisfy the ACL. Keep server identity verification enabled. Do not open 0.0.0.0/0 as a diagnostic. Get the actual TLS service descriptor from Database Connection; never synthesize the host or service alias. Use python-oracledb Thin and the _low service for bounded agent workloads.

For mTLS, Thin uses tnsnames.ora plus ewallet.pem and its wallet password; Thick uses tnsnames.ora, sqlnet.ora and cwallet.sso. The database password, wallet password and OCI key passphrase are three different secrets. Wallet generation is credential issuance, never an inventory read: SINGLE is database-scoped; ALL is regional. Keep wallet files outside the repo with private permissions and never use --file -.

ORA-12506: verify the ACL against the actual source, including proxies/NAT. ORA-12578: check local wallet files and client mode. Remove long connection retry settings during diagnosis so a rejected connection is visible promptly. Client examples and SQL are [unverified] without a database session.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| `ORA-12506: TNS:listener rejected connection based on service ACL filtering` | The ADB's **network ACL / private endpoint** rejects your source IP, or the wallet's service alias is not permitted | id 97 [unverified] |
| `ORA-12578: .*wallet file was not found or failed to open` | Wallet path wrong, `cwallet.sso` missing, or `TNS_ADMIN` not set to the unzipped wallet dir | id 98 [unverified] |
