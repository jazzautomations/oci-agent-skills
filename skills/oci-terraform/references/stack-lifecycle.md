# Resource Manager
Source: research/08c §8.
A stack stores configuration source, variables and Terraform version; a job records an operation and result. Inspect stack metadata, recent jobs and the chosen job before obtaining any sensitive logs or state.
Create-plan-job creates OCI job state and can refresh remote reads; it remains a mutation proposal here. Its job history has no inverse deletion command. A failed plan must not be followed by apply.
For apply, explicitly bind the job to the approved plan job with the installed CLI's FROM_PLAN_JOB_ID path/strategy, then review the generated command and scope. Never substitute AUTO_APPROVED. [unverified] No plan, apply, destroy or provider upgrade was run.
Configuration-source updates, variable changes and provider upgrades invalidate a previous plan. Preserve the last known configuration and state, but do not promise a reverse apply can recover destroyed data.
