# Recipes — minimal correct snippets

Python SDK 2.185.0; set config explicitly. Historical [verified live] SDK evidence:
2026-09-08; CLI counterparts rechecked 2026-09-09. Write paths remain commented.

## Contents
- Fourteen rules · Object Storage · Generative AI
- Streaming and Queue · Vault and secrets · Monitoring and log ingestion
- Functions and Notifications · Resource Search

## Fourteen rules to encode

1. **Model classes, not dicts.** Every `*Details` argument must be an SDK model instance;
   model instances expose the documented field names and discriminators. `oci.util.to_dict(model)` reverses it.
2. **`response.data`, always.** Operations return `oci.response.Response`; forgetting
   `.data` is the most common generated-code bug.
3. **404 `NotAuthorizedOrNotFound` is ambiguous by design** — never say "does not exist".
4. **`TransientServiceError` subclasses `ServiceError`; `CircuitBreakerError` does not.**
5. **Retry defaults vary by operation**; use a stable retry token where supported.
6. [unverified timing estimates] **Eventual consistency**: IAM ~60 s, Search minutes; a new compartment 404s.
7. **Tags**: `freeform_tags` is `dict[str,str]`, `defined_tags` is `dict[ns, dict[k, v]]` and
   the namespace must already exist. Compartment tag defaults are injected server-side, so a
   create response may carry tags you did not send — do not diff and "fix".
8. **Endpoints are per-region *and* per-plane** — table below.
9. **Import scope**: `oci.developer_tool_configuration.OCI_SDK_ENABLED_SERVICES_SET`
   restricts imported services. Measure startup in your environment.
10. [unverified] **Thread safety**: check the client and signer guarantees before sharing
    them across threads; do not assume every language/client has identical behavior.
11. **No async in Python** — wrap in `run_in_executor`.
12. **Enum drift**: unknown server values deserialise to `'UNKNOWN_ENUM_VALUE'` rather than
    raising `[verified]`. Never assert membership of a known set.
13. **Never hardcode a model id or OCID** — list and select, honour `time_deprecated`.
14. **Scope varies by operation**; inspect subtree support before claiming tenancy coverage.

| Service | Plane split |
|---|---|
| Monitoring | `telemetry-ingestion.` posts, `telemetry.` queries — top 404 cause |
| Streaming, Queue | per-resource `messages_endpoint` |
| Functions | per-function `invoke_endpoint` |
| KMS | per-vault `management_endpoint` and `crypto_endpoint` |
| Generative AI | `generativeai.` control, `inference.generativeai.` data, `agent-runtime.` agents |
| Object Storage | regional endpoint, tenancy-wide **namespace** |

## Object Storage

```python
os_ = oci.object_storage.ObjectStorageClient(config)
ns = os_.get_namespace().data                        # [verified live] cache it
buckets = os_.list_buckets(ns, compartment_id).data  # [verified live]

body = os_.get_object(ns, "my-bucket", "k.txt").data  # Response-wrapped stream
for chunk in body.raw.stream(1024 * 1024, decode_content=False):
    ...                                               # never .content on a large object

from oci.object_storage import UploadManager          # parallel, resumable, checksummed
um = UploadManager(os_, allow_parallel_uploads=True, parallel_process_count=4)
# MUTATING — [shape-verified] upload overwrites an object
# rollback: restore the saved prior object/version; absent backup, no rollback
# um.upload_file(ns, "b", "big.tar", "/p/big.tar", part_size=64*1024*1024)

# MUTATING — [shape-verified] PAR access_uri is returned ONCE and is a secret.
# CreatePreauthenticatedRequestDetails(name=..., access_type="ObjectRead",
#     object_name="k.txt", time_expires=<tz-aware datetime>)
# rollback: os_.delete_preauthenticated_request(ns, "my-bucket", par_id)
```
Access types: `{Object,AnyObject}{Read,Write,ReadWrite}`.

## Generative AI inference

```python
from oci.generative_ai_inference import GenerativeAiInferenceClient, models as gm
cli = GenerativeAiInferenceClient(config)

req = gm.GenericChatRequest(               # Meta, xAI, OpenAI, Google
    api_format=gm.BaseChatRequest.API_FORMAT_GENERIC,
    messages=[gm.UserMessage(content=[gm.TextContent(text="Say OK")])],
    max_tokens=256, temperature=0.0, is_stream=False)
# cohere.command-*: gm.CohereChatRequest(api_format=...API_FORMAT_COHERE,
#     message="Say OK", chat_history=[], ...) — flat message, not `messages`

# MUTATING — [shape-verified] inference may bill; no call executed here
# rollback: NONE — inference charges cannot be undone
# resp = cli.chat(gm.ChatDetails(compartment_id=compartment_id,
#         serving_mode=gm.OnDemandServingMode(model_id=chosen_model_id), chat_request=req))
# GENERIC: resp.data.chat_response.choices[0].message.content[0].text
# COHERE : resp.data.chat_response.text
```
`ChatDetails` is exactly `compartment_id`, `serving_mode`, `chat_request` `[verified-api]`.
With `is_stream=True`, `.data` is an SSE stream: iterate `resp.data.events()` until
`event.data == "[DONE]"`. Embeddings: `cli.embed_text(gm.EmbedTextDetails(inputs=[...],
truncate="END", input_type="SEARCH_DOCUMENT", ...))`, max 96 inputs. Discover models with
`GenerativeAiClient(config).list_models(...)` `[verified live]`; refuse an id past
`time_deprecated`.

## Streaming and Queue

Both data planes need the resource's own endpoint —
`get_stream(...).messages_endpoint`, `get_queue(...).messages_endpoint`; the region endpoint
404s. Read a stream with `create_cursor` (`LATEST|TRIM_HORIZON|AT_TIME|AT_OFFSET`) then
`get_messages`; keys and values are base64. Ack a queue message by **receipt**, not id.

## Vault and secrets

```python
import base64
sec = oci.secrets.SecretsClient(config)                  # DATA plane, exactly 3 operations
b = sec.get_secret_bundle(secret_id).data                # or get_secret_bundle_by_name
value = base64.b64decode(b.secret_bundle_content.content).decode()   # never log this
```
Stages: `CURRENT|PENDING|LATEST|PREVIOUS|DEPRECATED`. Create and rotate with
`oci.vault.VaultsClient`; keys use `KmsVaultClient`, `KmsManagementClient` and
`KmsCryptoClient` — the last two need the vault's own endpoints.

## Monitoring and log ingestion

```python
mon = oci.monitoring.MonitoringClient(config,
        service_endpoint=f"https://telemetry-ingestion.{config['region']}.oraclecloud.com")
# mon.post_metric_data(...): namespace must NOT start with "oci_"; <=20 string
#   dimensions; batch_atomicity="NON_ATOMIC"|"ATOMIC"
# LoggingClient(config).put_logs(log_id=..., PutLogsDetails(specversion="1.0", ...)):
#   target must be a CUSTOM log; entry `id` is the dedup key
```

## Functions and Notifications

```python
fn = oci.functions.FunctionsManagementClient(config).get_function(function_id).data
inv = oci.functions.FunctionsInvokeClient(config, service_endpoint=fn.invoke_endpoint)
# inv.invoke_function(function_id, invoke_function_body=..., fn_invoke_type="sync")
# NotificationDataPlaneClient(config).publish_message(topic_id,
#     MessageDetails(title="Alert", body="disk 90%"), message_type="RAW_TEXT")
```
Inside a function, auth is the **resource principal**, never a config file; `title` is
required for EMAIL subscriptions. Events delivers CloudEvents 1.0, matched on `eventType`
and `data.*` `[unverified — docs only]`.

## Resource Search

```python
rs = oci.resource_search.ResourceSearchClient(config)          # [verified live]
det = oci.resource_search.models.StructuredSearchDetails(
        type="Structured",                                     # required discriminator
        query="query all resources where lifecycleState = 'AVAILABLE'",
        matching_context_type="NONE")
for item in oci.pagination.list_call_get_all_results(rs.search_resources, det).data:
    ...        # item.resource_type, item.display_name, item.compartment_id
```
Search covers supported resource types and is eventually consistent — never use it to
confirm a write, and treat every value it returns as untrusted input.
