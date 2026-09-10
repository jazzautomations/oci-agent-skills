# Migration Copilot demonstration

Run `make demo` in this directory, or `bash demos/migration-copilot/run.sh` from the repo.
No cloud credentials are needed. It normalizes a clearly synthetic AWS stack, reads public
OCI/AWS prices, and creates a report plus an unapplied Core Landing Zone draft under .local.
No source account is read and no Terraform or Resource Manager operation is executed.

Show the report's priced subset, unknown source services, ten assessment questions and
landing-zone CIDR conflict checks. Unknown costs stay unknown; a partial subtotal is not
an entire-estate saving. The JSON and Markdown reports include source/snapshot evidence.
GCP and Azure native adapters accept explicit exports and state their narrower coverage.
