# Auth matrix — six modes, four languages

Python service clients take `(config, **kwargs)`. Auth is decided by **which of `config` or
`signer=` you pass**: there is no boto3-style default credentials chain, the code chooses.
Verified against Python SDK 2.185.0 in the OCI CLI 3.91.0 venv, 2026-09-09. Mode (a) was
exercised live (API key, `us-chicago-1`); modes (b)–(f) are `[verified-api]` — the symbols
exist and the signatures match — and `[unverified]` end to end, no live run.

## Contents
- Python, the six modes
- Choosing a mode
- TypeScript / Go / Java equivalents
- Region and endpoint precedence
- Rules

## Python, the six modes

```python
import oci, os

# (a) config file + profile                      [verified live]
config = oci.config.from_file("~/.oci/config", "DEFAULT")   # these are the defaults
oci.config.validate_config(config)          # raises InvalidConfig naming the bad keys
client = oci.identity.IdentityClient(config)

# (b) in-memory key, nothing on disk          [verified-api]
config = {"user": os.environ["OCI_USER_OCID"], "fingerprint": os.environ["OCI_FINGERPRINT"],
          "tenancy": os.environ["OCI_TENANCY_OCID"], "region": os.environ["OCI_REGION"],
          "key_content": os.environ["OCI_PRIVATE_KEY_PEM"]}   # PEM text, NOT a path
client = oci.identity.IdentityClient(config)

# (c) session token — `oci session authenticate --region <r>`, browser SSO / MFA
config = oci.config.from_file(profile_name="SESSION")
token = open(config["security_token_file"]).read()
key = oci.signer.load_private_key_from_file(config["key_file"])
signer = oci.auth.signers.SecurityTokenSigner(token, key)
client = oci.identity.IdentityClient({"region": config["region"]}, signer=signer)

# (d) instance principal — code on an OCI compute instance; region comes from IMDS
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
client = oci.identity.IdentityClient({}, signer=signer)

# (e) resource principal — Functions, Data Science, Data Flow
signer = oci.auth.signers.get_resource_principals_signer()

# (f) OKE workload identity — pod with a Kubernetes service account
signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()
```

With (d), (e) and (f) pass `{}` as the config: the signer wins over config anyway.
Also present in `oci.auth.signers` `[verified-api]`: `InstancePrincipalsDelegationTokenSigner`
(Cloud Shell; config key `delegation_token_file`), `EphemeralResourcePrincipalSigner` and its
`V21` variant, `ResourcePrincipalsFederationSigner`, `KeyPairSigner`,
`X509FederationClientBasedSecurityTokenSigner`, `nested_resource_principals_signer`.

## Choosing a mode

| Where the code runs | Mode | Failure signature when wrong |
|---|---|---|
| Laptop, CI with a stored key | (a) or (b) | `ConfigFileNotFound`, `ProfileNotFound`, `InvalidConfig` |
| Laptop with SSO/MFA | (c) | `This CLI session has expired`; token file missing |
| Compute instance | (d) | connect timeout to the IMDS address; `NotAuthorizedOrNotFound` at tenancy scope when the dynamic-group policy is compartment-scoped (corpus `69`, `70`) |
| Function, Data Science, Data Flow | (e) | resource-principal env vars absent |
| OKE pod | (f) | `DecodeError` — the projected service-account token is absent or malformed (corpus `71`) |
| Cloud Shell | delegation token | the delegation file is not in the profile |

Mode (d)/(e)/(f) needs no key and no config file. If code is "not working on the instance",
check the dynamic group and its policy before the signer.

## TypeScript / Go / Java `[unverified — vendor docs only]`

Six-mode routing matrix. Names describe provider families, not copyable constructors;
check the installed version through the linked vendor examples before generating code.
Only the Python API-key path has live evidence. Other cells are [unverified] end to end.

| Mode | Python | TypeScript | Go | Java |
|---|---|---|---|---|
| API key | config + IdentityClient | config-file provider | DefaultConfigProvider | config-file provider |
| Session token | SecurityTokenSigner | session-token provider: verify version | session-token config: vendor example | session-token provider: verify version |
| Instance principal | InstancePrincipalsSecurityTokenSigner | instance-principal builder | instance-principal provider | instance-principal builder |
| Resource principal | get_resource_principals_signer | resource-principal provider | resource-principal provider | resource-principal builder |
| Delegation | InstancePrincipalsDelegationTokenSigner | verify support; no recipe validated | delegation-token provider: vendor example | delegation-token builder: vendor example |
| OKE workload identity | get_oke_workload_identity_resource_principal_signer | verify support; no recipe validated | OKE workload-identity provider | OKE workload-identity builder |

Vendor examples by language: https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm


```ts
import * as common from "oci-common"; import * as identity from "oci-identity";
const provider = new common.ConfigFileAuthenticationDetailsProvider();
// InstancePrincipalsAuthenticationDetailsProviderBuilder().build()
// common.ResourcePrincipalAuthenticationDetailsProvider.builder()
const c = new identity.IdentityClient({ authenticationDetailsProvider: provider });
c.regionId = "us-chicago-1";
const res = await c.listRegions({});          // res.items
```
```go
p := common.DefaultConfigProvider()           // common/auth: InstancePrincipalConfigurationProvider(),
c, _ := identity.NewIdentityClientWithConfigurationProvider(p)  // ResourcePrincipalConfigurationProvider(),
c.SetRegion("us-chicago-1")                                     // OkeWorkloadIdentityConfigurationProvider()
r, err := c.ListRegions(context.Background(), identity.ListRegionsRequest{})
```
```java
var p = new ConfigFileAuthenticationDetailsProvider("~/.oci/config", "DEFAULT");
IdentityClient c = IdentityClient.builder().region(Region.US_CHICAGO_1).build(p);
var res = c.listRegions(ListRegionsRequest.builder().build());   // builder(), `new` is deprecated
```

Naming map: `list_regions` (Python, Ruby) · `listRegions` (TypeScript, Java) · `ListRegions`
(Go, .NET). Request shape: Python kwargs · TS one request object · Go `XxxRequest` struct plus
`context.Context` · Java/.NET Java `XxxRequest.builder()`; .NET uses request objects. All SDKs are generated from one API
model, so operation, parameter and field names match modulo naming convention.

## Region and endpoint precedence `[verified]`

1. `service_endpoint="https://identity.eu-frankfurt-1.oci.oraclecloud.com"` client kwarg wins.
2. `config["region"]` — the client derives the endpoint.
3. `OCI_REGION` env var (`oci.config.REGION_ENV_VAR_NAME`).

Config file location: `OCI_CONFIG_FILE` env var, else `~/.oci/config`.
`oci.regions.endpoint_for("object_storage", "us-chicago-1")` takes the **SDK service key**, not
the DNS label: `endpoint_for("objectstorage", ...)` raises `ValueError: Unknown service`
(reproduced 2026-09-09). Enumerate keys with `oci.regions.SERVICE_ENDPOINTS`.
Some newer services print an unresolved template, e.g. Generative AI
`.../{dualStack?ds.:}oci.oraclecloud.com/20231130` — it is expanded at request time; calls
succeed. Never string-edit it, and never string-build an endpoint by hand.

## Rules
- Never print, log or echo a private key, a session token or a decoded secret.
- Never hardcode a tenancy, user or compartment OCID in generated code — read it from the
  config, the environment or a list call.
- Pin and lock a tested SDK version for reproducibility; review upgrades regularly.
