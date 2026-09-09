# Data Science

Map project → notebook session, job/job run, model catalog version and model deployment. A catalog model is an artifact; a deployment is billable serving capacity, and a notebook is compute. Inventory is not evidence of endpoint predictions, model quality or safety.
Review image/environment digest, dependency lock, model serializer risks, input/output schema and runtime identity before any execution. Model artifacts and notebooks are executable content: do not load pickle, run notebook cells or import downloaded packages merely to inspect metadata.
Network diagnosis separates subnet routing/DNS, resource-principal IAM, Object Storage access and model-deployment endpoint authentication. Invocation is a billable operation and may expose data, even if HTTP POST returns only predictions.
For a rollout, use approved synthetic inputs and a canary endpoint, compare error rate/latency/quality, then propose traffic changes. Preserve the previous model and routing until acceptance. Deactivation and deletion have different recovery and cost effects; state changes were not exercised here.
