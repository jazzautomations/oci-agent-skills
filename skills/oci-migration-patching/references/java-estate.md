# Java estate and GraalVM

JMS spans three CLI groups: jms for fleet/runtime usage, jms-utils for analysis/configuration, and jms-java-downloads for releases/licenses/download mechanisms. Do not substitute fleet lifecycle for JVM or application health.
Basic discovery and advanced analysis/remote management have different entitlements. Check the user's subscription and OCI workload eligibility against current Oracle terms before claiming availability or price. GraalVM distribution rights and Java SE support entitlement are distinct; no legal/license conclusion is inferred from inventory.
Runtime usage depends on installed plugins and observation windows. A missing runtime is not proof of no Java, and a vulnerable version finding needs application-owner validation.
Download tokens/URLs are credentials and may be tenancy-scoped. Do not create tokens or run migration/crypto/performance analysis as a read-only probe. Review compatibility, startup flags, JNI/native libraries, TLS providers and representative application tests before a Java upgrade; preserve the previous runtime and routing for rollback.

## Diagnostic signals

Source: research/14 error corpus, retained in `references/error-corpus.json`; match status and code before message text. The source verification label is preserved per row.

| Error string / pattern | What to distinguish | Corpus evidence |
|---|---|---|
| ExternalServerIncorrectState | A customer-owned server (DB agent, on-prem host, Exadata) is unreachable/misbehaving | id 19 [unverified] |
| IncorrectState | Resource is mid-transition (`PROVISIONING`, `TERMINATING`, `UPDATING`) | id 18 [unverified] |
