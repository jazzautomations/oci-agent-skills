# API Gateway
Source: research/09a §23.
A gateway supplies a network endpoint; a deployment defines a path prefix, routes, methods, policies and backends. Diagnose the full request path after the deployment prefix, HTTP method, authentication policy and selected backend before editing routes.
For HTTP backends, verify DNS, TLS trust, route/security reachability and backend timeout. For Functions backends, verify the function OCID/region and gateway service permission to invoke it. Never invoke a function merely to test access without authorization for its effects.
A 404 can mean no route matched; a 504 can mean an unreachable or slow backend. Check gateway access/execution logs through oci-logging-audit with a bounded window and redaction. Do not solve TLS failures by disabling certificate verification.
[unverified] JWT, CORS, usage-plan and deployment-specification JSON were not executed. Review issuer/audience, preflight methods, approved origins, rate limits and backend semantics before proposing a complete replacement deployment specification.
