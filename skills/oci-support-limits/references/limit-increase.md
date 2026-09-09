Purpose: build, submit and track one limit-increase request without inventing a field.
Source: research/12 A5–A6; verified-on CLI 3.91.0, us-chicago-1, 2026-09-09.

## 1. Surface

`oci limits-increase` has three subtrees: `item`, `limits-increase-request`, `question`.
The request subtree exposes `cancel`, `create`, `delete`, `get`, `list`, `patch` (adds comments)
and `update` [verified] — wider than older write-ups assume, so "withdraw my pending request" and
"add a comment" are both offerable. `oci limits-increase item` adds `cancel`, `get`, `list` for
the individual items inside a request.

Use this surface, not `oci support incident create --problem-type LIMIT`, for a normal limit
raise; the incident path is the legacy/edge route (research/12 A5).

## 2. Phases

**0. Eligibility.** `support validation-response validate-user`. A 403 `AUTHZ_FAILED` in the home
region means the tenancy cannot file anything — stop before building a payload.

**1. Detect.** Resolve service name, `scope-type` and the current value, then read headroom.
Report `used`/`available` and name the AD each figure belongs to.

**2. Decide.** Dynamic limit, or `available > 0`? Say so and ask whether a request is still
wanted. A limit increase is not the fix for a compartment quota or a policy denial.

**3. Questionnaire.** `limits-increase question list --service-name <svc> --limit-name <lim>`.
Ask each returned question verbatim. An empty `items` array is a **normal answer** — on this
tenancy `--service-name compute` returned `{"data": {"items": []}}` [verified] — never invent
questions to fill it.

**4. Payload.** Generate the skeleton from the installed CLI, never a hardcoded template:
`oci limits-increase limits-increase-request create --generate-full-command-json-input`.
Verified shape [verified, 2026-09-09]: top-level `compartmentId`, `displayName`, `justification`,
`freeformTags`/`definedTags`, and `limitsIncreaseItemRequests[]` with
`{serviceName, limitName, scope, region, value, questionnaireResponse[{id, questionResponse}]}`.
Note the asymmetry: the CLI flag is `--items`, the JSON key is `limitsIncreaseItemRequests`.
Validate before showing it: the requested `value` is numeric and strictly greater than the
confirmed current value; `scope` is the catalog's value (for an AD limit, the *logical AD*, not
the literal string `AD`); the endpoint region and the target region are tracked separately.

**5. Approval gate.** Render display name, justification, service, limit, target region, scope,
current value **and its source** (`oci` vs user-provided), requested value, questionnaire answers,
subscription and tags. Require explicit confirmation; re-approve from scratch if any field moves.

**6. Submit and track.** Never pass `--wait-for-state`: a request can sit `IN_PROGRESS` for days,
so creation and polling are separate actions. Capture the OCID, read it back with `get`.
Never auto-retry a failed `create` — it may already have reached the service; preserve the
`opc-request-id` and re-read first. Lifecycle enum:
`ACCEPTED|IN_PROGRESS|SUCCEEDED|CANCELED|PARTIALLY_SUCCEEDED|FAILED` [verified].
**Surface `PARTIALLY_SUCCEEDED` explicitly** — a multi-item request had some items approved and
some denied; reporting it as success is a lie.

## 3. Reads

```bash
oci limits-increase limits-increase-request list --compartment-id "$TENANCY_ID" --limit 20 --query 'data.items[].{id:id,name:"display-name",state:"lifecycle-state"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci limits-increase limits-increase-request get --id "$REQUEST_ID" --query 'data.{state:"lifecycle-state",items:"limits-increase-item-requests"}' --profile "$PROFILE" --region "$REGION"
```

```bash
oci limits-increase item list --compartment-id "$TENANCY_ID" --limit 20 --query 'data.items[].{state:"lifecycle-state",limit:"limit-name"}' --profile "$PROFILE" --region "$REGION"
```

Both list fences returned `[]` live on this tenancy 2026-09-09 [verified] — an empty backlog, not
an error.

## 4. Writes (all `[shape-verified]`, none executed here)

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: oci limits-increase limits-increase-request cancel --id "$REQUEST_ID" --profile "$PROFILE" --region "$REGION"
oci limits-increase limits-increase-request create --compartment-id "$TENANCY_ID" --display-name "$REQUEST_NAME" --justification "$JUSTIFICATION" --items file://items.json --query 'data.id' --profile "$PROFILE" --region "$REGION"
```

```bash
# MUTATING — not run in this repo; [shape-verified] against CLI 3.91.0 --help
# rollback: NONE — a comment cannot be unposted; the request itself is withdrawn with `cancel`
oci limits-increase limits-increase-request patch --id "$REQUEST_ID" --items file://comment.json --query 'data."lifecycle-state"' --profile "$PROFILE" --region "$REGION"
```

Subscription-scoped requests additionally need
`Allow group <g> to READ organizations-assigned-subscription in tenancy`, Government Cloud
tenancies cannot use this flow at all, and subscribed-region limits have their own procedure
(research/12 A5 [doc]).

Docs (HTTP 200, 2026-09-09):
https://docs.oracle.com/en-us/iaas/Content/General/service-limits/create-request.htm ·
https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm
