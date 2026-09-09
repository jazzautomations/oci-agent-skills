# Pagination, waiters and eventual consistency

Python SDK 2.185.0; the pagination helper and the compartment walk were run live on
2026-09-09 (`us-chicago-1`, 3 ACTIVE compartments). Waiter behaviour is `[verified-api]`
— signatures and exception classes introspected, no state transition was awaited.

## Contents
- Pagination
- Waiters
- Work requests
- Eventual consistency
- Other languages

## Pagination

```python
# All pages, one call; .data is a flat list                     [verified live]
res = oci.pagination.list_call_get_all_results(
        identity.list_compartments, config["tenancy"],
        compartment_id_in_subtree=True,   # whole tree, not just children
        access_level="ACCESSIBLE",        # skip what policy hides — avoids 404s
        lifecycle_state="ACTIVE")         # skip DELETED/DELETING
for c in res.data: ...

# Memory-safe streaming: "record" yields items, "response" yields one Response per page
for c in oci.pagination.list_call_get_all_results_generator(
        identity.list_compartments, "record", config["tenancy"],
        compartment_id_in_subtree=True):
    ...

# Bounded: (list_func, record_limit, page_size, *args)
oci.pagination.list_call_get_up_to_limit(identity.list_compartments, 50, 25, tenancy)

# Manual paging
page = None
while True:
    r = identity.list_compartments(tenancy, page=page)
    if not r.has_next_page:
        break
    page = r.next_page
```

**Traps.**
- `list_call_get_all_results` walks *every* page whatever `limit=` you pass, and materialises
  the whole result in memory. For `list_objects` or `list_instances` at tenancy scale use the
  generator, or `list_call_get_up_to_limit` when a cap is what you meant.
- `compartment_id_in_subtree=True` needs the **tenancy** OCID as `compartment_id`. Few APIs
  support it at all: inspect each method: support varies across services. Resource Search also has a
  supported-type coverage boundary; it is not a complete inventory.
- The root compartment is **not** in `list_compartments` output; append
  `identity.get_compartment(tenancy).data` if you need it.
- A short list with no error is the CLI's problem, not the SDK's — the truncation warning
  goes to stderr. In SDK code the equivalent bug is reading `.data` of one page and never
  looking at `has_next_page`.

## Waiters

```python
# 1. Field-state waiter                                        [verified-api]
resp = compute.get_instance(instance_id)
oci.wait_until(compute, resp, "lifecycle_state", "RUNNING",
               max_interval_seconds=30, max_wait_seconds=1200,
               succeed_on_not_found=False)
# signature: (client, response, property=None, state=None, max_interval_seconds=30,
#             max_wait_seconds=1200, succeed_on_not_found=False, **kwargs)

# MUTATING — [shape-verified] composite create + wait; propose only
# rollback: terminate only the newly created instance after reviewing data-loss consequences
from oci.core import ComputeClientCompositeOperations
ops = ComputeClientCompositeOperations(compute)
# ops.launch_instance_and_wait_for_state(details, wait_for_states=["RUNNING"])

# 3. Work-request waiter — services that return opc-work-request-id
wr = oci.work_requests.WorkRequestClient(config)
oci.wait_until(wr, wr.get_work_request(work_request_id), "status", "SUCCEEDED",
               max_wait_seconds=1800)
```

- `oci.waiter.MaximumWaitTimeExceeded` on timeout; `WaitUntilNotSupported` when the client
  has no matching `get_*` (corpus `115`).
- `succeed_on_not_found=True` is the correct flag when waiting for a **delete**; without it
  the waiter's own `get` raises 404 `NotAuthorizedOrNotFound` and you get a `ServiceError`
  from inside the waiter (corpus `114`).
- A timeout is not a failure. Re-`get` the resource before reporting one.
- `*ClientCompositeOperations` classes exist per service (Compute, ComputeManagement,
  Blockstorage, VirtualNetwork, ObjectStorage, WorkRequest and more).

## Work requests

Long-running control-plane operations return `opc-work-request-id` in the response headers.
When a wait "hangs", read the work request — `operation_type`, `status`, `percent_complete`,
plus `list_work_request_errors` and `list_work_request_logs` — not the resource. That is the
only place a service reports *why* a provisioning step stalled.

## Eventual consistency [unverified timing estimates]

| Surface | Lag | Consequence |
|---|---|---|
| IAM policies, groups, dynamic groups | ~60 s | a new policy 403s until it propagates |
| A just-created compartment | seconds | the next call can 404 |
| Resource Search | minutes | never use it to confirm a write you just made |

Retry 403/404 for a **bounded** window after a create, then stop. Never assert that a
resource is absent from one search result.

## Other languages `[unverified — vendor docs only]`

- Go has no helper: loop on `resp.OpcNextPage` until nil.
- Java: `listXxxRecordIterator(request)` / `listXxxResponseIterator(request)`.
- TypeScript: `listAllXxx(request)` async iterators.
- Java has `*AsyncClient` per service; .NET is Task-native; TypeScript is promise-native.
  Python has **no** async client (`any('Async' in x for x in dir(oci.identity))` is `False`,
  reproduced 2026-09-09) — wrap blocking calls in `run_in_executor`.
