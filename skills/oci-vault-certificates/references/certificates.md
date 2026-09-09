# Certificates
Source: research/09b §21.
Certificate metadata and certificate bundles are separate APIs. Use certs-mgmt metadata to inspect current-version-summary.validity.time-of-validity-not-after without retrieving a private key or PEM bundle. Trust-anchor/CA expiry and leaf expiry are separate dependencies.
Imported certificates require a complete matching chain and private key through the service's protected import mechanism. Managed/internal CA renewal rules differ from imported external certificates. Check the consumer association and rollout behavior; a newly issued version does not prove every endpoint serves it.
cert_expiry.sh reads the earliest-expiring bounded metadata sample, reports counts and UTC expiry dates only, and returns nonzero for expiring/expired certificates, unknown dates or a full 100-row sample. It never fetches certificate bundles. Empty metadata is not proof of no certificates elsewhere.
For mTLS, inspect both client and server chains, name/SAN match, validity, trust roots and revocation behavior. [unverified] Renewal, private-key import and endpoint rollout were not performed.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| InvalidParameter | A body/query parameter value is invalid or malformed | id 2 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
