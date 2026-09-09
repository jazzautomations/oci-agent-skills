# Perimeter: WAF, Network Firewall, ZPR

Verified 2026-09-09 against OCI CLI 3.91.0, `us-chicago-1`. Every list below ran; only
`waf protection-capability list` returned rows (the OWASP rule catalogue), the rest were empty.
Paths and flags are `[verified]`; non-empty WAF, firewall and ZPR bodies are `[shape-only]`.

## WAF (the current service, not the legacy `waas`)
Two resources: a **WebAppFirewallPolicy** (the rules) and a **WebAppFirewall** that binds the
policy to a load balancer (`backendType: LOAD_BALANCER`). Policy sections:
`requestAccessControl`, `requestRateLimiting`, `requestProtection` (the OWASP
protection-capability rule set, e.g. inspect the returned names rather than inferring attacks from numeric keys), `responseProtection`.

```bash
oci waf web-app-firewall-policy list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",s:"lifecycle-state"}'
oci waf web-app-firewall list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",lb:"load-balancer-id",p:"web-app-firewall-policy-id"}'
oci waf protection-capability list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{k:key,v:version,n:"display-name"}'
```

Posture questions worth asking of the output: is every internet-facing load balancer bound to
a WebAppFirewall at all; is `requestProtection` in `BLOCK` or only `CHECK`; is rate limiting
present. A policy that exists but is bound to nothing protects nothing — compare the
`web-app-firewall list` bindings against the load balancers Search returns.

## Network Firewall
A Palo Alto-based, VCN-inline L3–L7 firewall: a `network-firewall` in a dedicated subnet plus a
`network-firewall-policy` holding address, service and application lists, security rules,
decryption rules and optional IPS/threat logging. **Route tables must send traffic to the
firewall's private IP** or it sees nothing — an existing firewall is not evidence of inspection.

```bash
oci network-firewall network-firewall list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",s:"lifecycle-state",ip:"ipv4-address"}'
oci network-firewall network-firewall-policy list --compartment-id "$COMPARTMENT_ID" --limit 50 --query 'data.items[].{n:"display-name",s:"lifecycle-state"}'
oci network-firewall security-rule list --network-firewall-policy-id "$NETWORK_FIREWALL_POLICY_ID" --limit 50 --query 'data.items[].{n:name,a:action}'
```

Logs land in Logging as service logs: `networkfirewall` (categories `threat`, `traffic`) and
`waf` (category `all`). Reading them belongs to `oci-logging-audit`.

## ZPR — Zero Trust Packet Routing
ZPR enforces network intent by security attribute rather than by topology, tenancy-wide from
the root compartment. Three CLI groups on 3.91.0: `zpr configuration`, `zpr zpr-policy`,
`zpr work-request`.

```bash
oci zpr zpr-policy list --compartment-id "$TENANCY_ID" --limit 50 --query 'data.items[].{n:name,s:"lifecycle-state"}'
oci zpr configuration get --compartment-id "$TENANCY_ID" --query 'data.{s:"zpr-status",t:"time-created"}'
```

Two traps, both reproduced live: the catalog records **no required flag** for
`zpr configuration get`, but the API answers `MissingParameter` 400 `Missing Parameter`
without `--compartment-id`; and with the flag, a tenancy that never enabled ZPR answers
`NotAuthorizedOrNotFound` 404 `Authorization failed or requested resource not found`. The 400 identifies a missing argument. The generic 404 leaves enablement, permissions
and region unresolved; report that gap alongside the security-list and NSG findings.

## Where the perimeter finding actually lives
`0.0.0.0/0` on a security list or NSG is the finding this skill proves; WAF, Network Firewall
and ZPR are the compensating controls that decide how bad it is. Report them together: an open
port behind a blocking WAF is a different severity from the same port with no inspection at
all, and say which of the three you verified rather than assuming coverage.

Docs: https://docs.oracle.com/en-us/iaas/Content/WAF/home.htm ·
https://docs.oracle.com/en-us/iaas/Content/network-firewall/home.htm ·
https://docs.oracle.com/en-us/iaas/Content/zero-trust-packet-routing/home.htm
