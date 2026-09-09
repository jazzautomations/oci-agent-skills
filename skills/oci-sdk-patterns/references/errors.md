# Errors, retries, circuit breaker, timeouts

Reproduced live on 2026-09-09 against Python SDK 2.185.0 (`DEFAULT`, `us-chicago-1`) unless
tagged otherwise. Ids in backticks are `references/error-corpus.json` entries.

## Contents
- ServiceError fields
- The exception family
- opc-request-id
- Retries
- Circuit breaker
- Timeouts
- Handler skeleton

## ServiceError fields `[verified live]`

```python
try:
    identity.get_compartment("ocid1.compartment.oc1..<redacted>")
except oci.exceptions.ServiceError as e:
    e.status             # 404
    e.code               # 'NotAuthorizedOrNotFound'
    e.message            # 'Authorization failed or requested resource not found.'
    e.request_id         # opc-request-id — log this, Support asks for it first
    e.target_service     # 'identity'
    e.operation_name     # 'get_compartment'
    e.timestamp          # tz-aware datetime
    e.client_version     # 'Oracle-PythonSDK/2.185.0'
    e.request_endpoint   # full URL
    e.api_reference_link
```

Branch on `status` and `code`, never on `message` — message text is not a contract. For
HEAD-shaped operations there is no response body, so `code` is `None`: branch on `status`
only (corpus `75`). 404 `NotAuthorizedOrNotFound` is ambiguous **by design**: report "not
found *or* not visible to this principal", never "does not exist" (corpus `13`).

## The exception family `[verified-api]`

| Class | When | Note |
|---|---|---|
| `ServiceError` | any 4xx/5xx with a body | corpus `111` |
| `TransientServiceError` | 429/5xx after retries are spent | **subclasses** `ServiceError` |
| `CircuitBreakerError` (`circuitbreaker`) | breaker open | **not** a `ServiceError` — a bare `except ServiceError` misses it |
| `ConfigFileNotFound`, `ProfileNotFound`, `InvalidConfig` | before any request | corpus `112`, `113` |
| `InvalidKeyFilePath`, `InvalidPrivateKey`, `MissingPrivateKeyPassphrase` | key material | never log the key |
| `RequestException`, `ConnectTimeout` | transport, DNS, proxy, bogus region | request completion may be unknown; corpus `116` |
| `MaximumWaitTimeExceeded`, `WaitUntilNotSupported` | waiters | corpus `115` |
| `MissingEndpointForNonRegionalServiceClientError` | non-regional client without an endpoint | pass `service_endpoint` |
| `MultipartUploadError`, `ChecksumVerificationError`, `CompositeOperationError` | Object Storage, composite ops | |

Reproduced live: `ConfigFileNotFound`, `ProfileNotFound`, and `InvalidConfig` whose message
is a dict of the offending keys, e.g. `{'key_file': 'missing', 'tenancy': 'malformed'}`.
Call `oci.config.validate_config(config)` before constructing a client and the failure names
the field instead of surfacing as a signing error later.

Other languages `[unverified]`: Java `com.oracle.bmc.model.BmcException`
(`getStatusCode()`, `getServiceCode()`, `getOpcRequestId()`), corpus `118`; Go
`ServiceError` with `Code()`, `Message()`, `GetOpcRequestID()` plus
`common.IsNetworkError(err)`, corpus `119`. A version-mismatch complaint usually means the
client is too old for a new field or enum — upgrade before believing in a server bug
(corpus `120`).

## opc-request-id `[verified live]`

```python
r = identity.list_regions()
r.request_id                  # three '/'-separated segments
r.headers["opc-request-id"]   # the same value
r.status                      # 200
identity.list_regions(opc_request_id="my-trace-id")   # supply your own for correlation
```
Every operation accepts `opc_request_id`; every `Response` and every `ServiceError` carries
one. Log it on **every** failure. A missing request ID alone does not prove the request never reached OCI.

## Retries `[verified]`

The client docstring says there is no default retry strategy. The generated operation code
disagrees: `if retry_strategy is None: retry_strategy = retry.DEFAULT_RETRY_STRATEGY`. The inspected operations
**do** retry by default; inspect each operation before assuming this globally —
`ExponentialBackOffWithDecorrelatedJitterRetryStrategy`, 8 attempts, 600 s budget, base 1 s,
exponent 2, ≤30 s between calls; it retries timeouts, connection errors, 409 `IncorrectState`,
409 `LockConflict`, 429 and every 5xx except 501.

```python
from oci.retry import RetryStrategyBuilder, NoneRetryStrategy, DEFAULT_RETRY_STRATEGY
strategy = (RetryStrategyBuilder()
            .add_max_attempts(max_attempts=5)
            .add_total_elapsed_time(total_elapsed_time_seconds=120)
            .add_service_error_check(service_error_retry_on_any_5xx=True,
                                     service_error_retry_config={429: [], 409: ["IncorrectState"]})
            .get_retry_strategy())
client = oci.identity.IdentityClient(config, retry_strategy=strategy)   # client level
client.list_regions(retry_strategy=NoneRetryStrategy())                 # per-op override wins
```
Env kill switch: `OCI_SDK_DEFAULT_RETRY_ENABLED`. **Never retry a non-idempotent create
without `opc_retry_token=<uuid>`** when the operation supports it; reuse the same token across retries. On 429 the
SDK has already retried; serialise and add jitter rather than raising the attempt count
(corpus `26`).

## Circuit breaker `[verified]`

`DEFAULT_CIRCUIT_BREAKER_STRATEGY`: `failure_threshold=10`, `recovery_timeout=30` s; trips on
409 `IncorrectState`/`LockConflict`, 429, 500, 502, 503, 504. Most clients enable it.

```python
from oci.circuit_breaker import CircuitBreakerStrategy, NoCircuitBreakerStrategy
cb = CircuitBreakerStrategy(failure_threshold=3, recovery_timeout=10, name="my-client")
client = oci.identity.IdentityClient(config, circuit_breaker_strategy=cb)
client = oci.identity.IdentityClient(config, circuit_breaker_strategy=NoCircuitBreakerStrategy())
```

## Timeouts `[verified]`

`timeout=` is a float or a `(connect, read)` tuple; defaults are 10 s connect, 60 s read.
Raise the read timeout for large object GETs: `ObjectStorageClient(config, timeout=(10, 300))`.

## Handler skeleton

```python
from oci.exceptions import ServiceError, RequestException
from circuitbreaker import CircuitBreakerError

try:
    resp = client.get_thing(thing_id)
except CircuitBreakerError:          # NOT a ServiceError
    log.error("breaker open; back off")
    raise
except ServiceError as e:            # TransientServiceError lands here too
    log.error("%s %s op=%s rid=%s", e.status, e.code, e.operation_name, e.request_id)
    if e.status == 404:
        raise LookupError("not found or not visible to this principal") from e
    raise
except RequestException as e:        # transport failure; completion may be unknown
    log.error("transport failure: %s", e)
    raise
```
