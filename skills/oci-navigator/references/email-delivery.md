Purpose: route "send email from OCI" correctly — the HTTPS data plane most guides miss, what is regional versus global, and why port 25 fails for reasons unrelated to Email Delivery.
Source: research/16 §B/§B.1; generated 2026-09-08; verified-on CLI 3.91.0

## 1. There are two planes, and the easy one is undocumented in most guides

`oci email` (11 subgroups, 46 ops) is the **control plane**: approved senders, domains, DKIM,
suppression list, return paths, IP pools. `oci email-data-plane` is a **2-op data plane** that
submits mail over HTTPS with ordinary IAM request signing — no SMTP credential, no port 465, no
port-25 problem. Any answer that opens with "create SMTP credentials" is teaching the harder path.

Live in this tenancy [live 2026-09-09], `configuration get-email` returns **both** endpoints —
`cell0.submit.email.<region>.oci.oraclecloud.com` (HTTPS) and
`smtp.email.<region>.oci.oraclecloud.com` — so the choice is real, not theoretical:

```bash
oci email configuration get-email --compartment-id ${COMPARTMENT_ID} --query "data" --output json
```

```bash
# MUTATING — not run in this repo; [shape-verified] against `oci email-data-plane email-submitted-response submit-email --help` on 3.91.0
# rollback: NONE — this is irreversible; a submitted message cannot be recalled
oci email-data-plane email-submitted-response submit-email --sender ${SENDER} --recipients '["${RECIPIENT}"]' --subject "test" --body-text "test"
```

## 2. Regional versus global — the single most common wrong answer

SMTP credentials are **global** IAM assets (`oci iam smtp-credential`, `create` needs `--user-id`
and `--description`; free trials cap two per user). Approved senders and the suppression list are
**regional**: a sender approved in Phoenix cannot send through Ashburn, and a Phoenix bounce does
not suppress in Ashburn. Run these once **per region** — a single-region answer is a wrong answer.

```bash
oci email sender list --compartment-id ${COMPARTMENT_ID} --limit 50 --query "data[].{email:\"email-address\",state:\"lifecycle-state\"}" --output json
```

```bash
oci email suppression list --compartment-id ${COMPARTMENT_ID} --limit 50 --query "data[].{email:\"email-address\",reason:reason}" --output json
```

`add` / `remove` on `sender`, `domain` and `email-return-path` are **resource locks**, not
membership operations — easy to misgenerate. Live here [2026-09-09]: `sender list` -> 0
(`opc-total-items: 0`, an empty body, not an error), `suppression list` -> empty,
`domain list` -> 1 — three separate reads, because none implies the others.

## 3. Facts to get right

- **Port 25 is blocked by tenancy age, not by Email Delivery.** Tenancies created after
  2021-06-23 cannot send outbound on TCP 25; the exemption is a service-limits request. It is a
  *Networking* release note, so the symptom has nothing to do with approved senders. Recommend
  465 (implicit TLS), know 587 works, expect 25 to fail.
- **Envelope-From must equal header-From**, and both must be an approved sender, or the message
  is rejected. Multiple From addresses each need approval and degrade DMARC alignment.
- **SPF is per region**: Americas `v=spf1 include:rp.oracleemaildelivery.com ~all`; EU uses
  `eu.rp.oracleemaildelivery.com`.
- **Suppression is automatic and silent.** Four soft bounces to one address within 24 hours adds
  it to the list. "Our retry loop killed our own deliverability" is a real diagnosis, and
  `email suppression list` filtered by address is the first command to run.
- **`421 4.3.0` / `Too many auth failures, try again later`** are IP throttles from repeated bad
  credentials or non-approved senders — an agent retry storm manufactures its own outage. Keep
  bounce rate under 2%.
- **Free-trial caps**: 200 emails/day, 10/minute, 2,000 approved senders, 2 SMTP credentials per
  user. Paid limits are not published on that page — read them, do not quote a number. The
  limits service name is **`email-delivery`**, not `email`; `--service-name email` returns
  400 `InvalidParameter` [live 2026-09-09]:

```bash
oci limits value list --compartment-id ${TENANCY_ID} --service-name email-delivery --limit 50 --query "data[].{name:name,value:value}" --output json
```

  Live here [2026-09-09]: `max-emails-day` 100, `sendrate` 10, `approved-sender-count` 10,
  `max-message-size` 2008192 — read the tenancy, never quote the doc page.

- **The DKIM selector that was actually applied appears only in the service log**, so DKIM
  debugging is `oci logging-search search-logs`, not `oci email`.

Docs (HTTP 200, 2026-09-08): https://docs.oracle.com/en-us/iaas/Content/Email/Concepts/overview.htm ·
https://docs.oracle.com/en-us/iaas/Content/Email/Concepts/troubleshooting.htm ·
https://docs.oracle.com/en-us/iaas/Content/Email/Tasks/configuresmtpconnection.htm
