# Review a saved plan
Source: research/08c §3.
Review the exact saved plan artifact and its configuration revision. A plan can contain plaintext sensitive values even when terminal output hides them; keep the binary and JSON local with restrictive permissions and do not commit them.
plan_summary.py accepts local plan JSON (from terraform show -json, prepared separately). It lists every delete and both replacement action orders, plus changes to IAM/network/data resource types. It emits only sanitized resource addresses/types and action counts, never before/after values, outputs or variables. It never invokes Terraform or OCI.
A zero-delete summary is not approval: review cost, IAM reach, public endpoints, encryption, backup retention, unknown values, drift, import/move actions and provider changes. Replacement order create/delete versus delete/create affects outage risk. Do not use -target to hide unrelated changes.
Apply only the exact reviewed saved plan after authorization. Never use -auto-approve or AUTO_APPROVED as a shortcut. Replanning can change actions and invalidates prior review.
