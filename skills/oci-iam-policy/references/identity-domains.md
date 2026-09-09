Purpose: tell the two IAM control planes apart, reach the domain endpoint, and read federation, SCIM, MFA and sign-on configuration.
Source: research/04b-iam-security-cost-freetier.md §8, §14; live reads 2026-09-09 on OCI CLI 3.91.0.
Federation depth is a named gap in this build: everything marked `[unverified]` below was not exercised against a federated tenancy.

## Contents
1 which world am I in · 2 the CLI split · 3 endpoint discovery · 4 federation and SCIM `[unverified]` · 5 MFA and sign-on · 6 pitfalls · 7 links

## 1. Which world am I in

`oci iam domain list --compartment-id <tenancy-ocid>` [verified live] returns one row per
identity domain. A populated result means an identity-domains tenancy; an empty result or an
error means a legacy, non-domains tenancy where only `oci iam` applies. The `Default` domain
holds the initial administrator user and group and the default policy granting `Administrators`
`manage all-resources in tenancy`; it cannot be deleted. Domain types (SKUs, e.g. `free`) differ
in features and object limits.

## 2. The CLI split

| | `oci iam` | `oci identity-domains` |
|---|---|---|
| Owns | users, groups, identity domains, compartments, **policies**, tagging | resources *within* one domain: users, groups, dynamic resource groups, identity providers |
| Endpoint | regional IAM control plane; home region for writes | per domain, `https://<domainURL>/admin/v1/` — pass `--endpoint` |
| Naming | `dynamic-group`, `network-sources` | `dynamic-resource-group`, `network-perimeter` |

The rule that decides routing: **policies, compartments and dynamic groups always go through
`oci iam`.** User and group lifecycle in a non-default domain goes through `oci identity-domains`
with `--endpoint`. A policy that grants a non-default domain's group still uses `oci iam policy`,
with the subject written `group MyDomain/AI-Agent-Readers`.

## 3. Endpoint discovery

The domain URL comes from the domain record itself; never build it from a template. Read it with
`oci iam domain list --compartment-id <tenancy-ocid> --limit 20 --query 'data[].url'`, then pass
that value as `--endpoint`. It is a tenancy-identifying string: treat it as evidence to redact
before writing it down.

## 4. Federation and SCIM `[unverified]`

- List identity providers with `--all`, never `--limit` (pitfall 1):

```bash
oci identity-domains identity-providers list --endpoint "$DOMAIN_URL" --all --query 'data.resources[].{name:"partner-name",enabled:enabled}' --profile "$PROFILE" --region "$REGION"
```

  On the reference tenancy this returned only the built-in local providers
  (`Username-Password`, the OTP factors); **no SAML or OIDC provider was configured, so the
  federated fields — assertion attributes, request bindings, signing certificates, JIT
  provisioning — were never populated and remain unverified.**
- SCIM is the shape of the whole `identity-domains` API (`resources[]`, `total-results`,
  `items-per-page`, `start-index`), not a separate command tree. Inbound SCIM provisioning from
  an external IdP and outbound provisioning to an application are configured as *apps*
  (`oci identity-domains apps list --endpoint <domainURL>`); the app-side provisioning payloads
  were not exercised here. `[unverified]`
- Domain groups read the same way: `oci identity-domains groups list --endpoint "$DOMAIN_URL"
  --limit 50 --query 'data.resources[].{name:"display-name"}'` [verified live].
- Group membership synchronised by SCIM still needs an `oci iam` policy naming
  `group <domain>/<group>` before it grants anything. Federation alone authorises nothing.

## 5. MFA and sign-on

- `oci identity-domains authentication-factor-setting get --endpoint <domainURL>
  --authentication-factor-setting-id AuthenticationFactorSettings` [verified live] returns the
  domain's factor configuration; the singleton id is the literal string
  `AuthenticationFactorSettings`.
- `oci iam authentication-policy get --compartment-id <tenancy-ocid>` [verified live] returns the
  legacy tenancy password policy — a different object from the domain's password policy
  (`oci identity-domains password-policies list`).
- Sign-on policies, their rules and conditions live under `oci identity-domains policy`, `rule`
  and `condition`. `[unverified]` — no sign-on policy existed to read.
- A domain-level MFA setting and the IAM condition `request.user.mfaTotpVerified='true'` are
  independent controls. The condition gates one policy statement; the domain setting gates the
  sign-in. Requiring one does not imply the other.

## 6. Pitfalls

1. `oci identity-domains identity-providers list --limit N` aborts client-side with
   `TypeError: object of type 'int' has no len()` on OCI CLI 3.91.0 [verified live 2026-09-09].
   `--all` and `--count N` both work. Use `--all` for this collection.
2. `--endpoint` is mandatory for every `identity-domains` call; without it the CLI targets the
   regional IAM plane and the operation fails or reads the wrong object.
3. `dynamic-group` (iam) and `dynamic-resource-group` (identity-domains) are the same concept
   under two names. Policy still says `dynamic-group`.
4. Several `identity-domains` list calls print nothing at all on an empty collection rather than
   an empty array — absence of output is not an error.
5. Domain user and group writes are still home-region-bound like every other IAM write.

## 7. Links

- Identity domains overview: https://docs.oracle.com/en-us/iaas/Content/Identity/domains/overview.htm
- Identity Domains API: https://docs.oracle.com/en-us/iaas/api/#/en/identity-domains/
- CLI command reference: https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/identity-domains.html
