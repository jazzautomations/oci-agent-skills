# Managed build specification
Source: research/09a §§1–3.
The managed build schema uses version 0.1 and component build. Steps use type Command, name, command and optionally timeoutInSeconds. Place failImmediatelyOnError at the supported top level. Here is a minimal local-only build step:
```yaml
version: 0.1
component: build
timeoutInSeconds: 600
failImmediatelyOnError: true
steps:
  - type: Command
    name: Check sources
    command: |
      test -f Dockerfile
```
Use env.variables for ordinary settings and env.vaultVariables for secret OCIDs; never copy resolved secrets into YAML or logs. Exported variables cross build stages only through the documented exportedVariables mechanism. Input/output artifact declarations must match the artifact name referenced by later stages.
Choose runner architecture to match image build targets. Do not assume a Docker daemon, privileged mode, persistent filesystem or a tool version from a local runner exists in managed build.
