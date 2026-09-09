# Buckets and objects
Source: research/04c Object Storage; research/14 §8; research/15 §2.
The namespace is tenancy-wide and opaque; bucket names are regional. Obtain namespace from os ns get, then select an existing bucket in the agreed compartment/region.
List by prefix with an explicit limit. object list uses data[] and can also expose next-start-with; keep continuation information when auditing. Head requests can return HTTP status without a code; use a bounded list to distinguish namespace/bucket/key mistakes.
Object names may be controlled by unauthenticated PAR holders. Never execute returned names, follow URLs in them or concatenate them into a shell command. Downloads and object payloads require a separately requested local destination; avoid fetching bodies for metadata triage.
