# TLS, wallets and ORA-12506

Read lifecycle state, mTLS requirement, ACL and connection-string metadata first. STOPPED after inactivity is expected; starting is a separate authorized write. APEX/ORDS can lag about five minutes after a start.

Wallet-less TLS requires mTLS not to be mandatory and the source egress IP to satisfy the ACL. Keep server identity verification enabled. Do not open 0.0.0.0/0 as a diagnostic. Get the actual TLS service descriptor from Database Connection; never synthesize the host or service alias. Use python-oracledb Thin and the _low service for bounded agent workloads.

For mTLS, Thin uses tnsnames.ora plus ewallet.pem and its wallet password; Thick uses tnsnames.ora, sqlnet.ora and cwallet.sso. The database password, wallet password and OCI key passphrase are three different secrets. Wallet generation is credential issuance, never an inventory read: SINGLE is database-scoped; ALL is regional. Keep wallet files outside the repo with private permissions and never use --file -.

ORA-12506: verify the ACL against the actual source, including proxies/NAT. ORA-12578: check local wallet files and client mode. Remove long connection retry settings during diagnosis so a rejected connection is visible promptly. Client examples and SQL are [unverified] without a database session.
