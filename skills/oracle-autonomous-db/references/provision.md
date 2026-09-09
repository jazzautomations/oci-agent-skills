# Provisioning and Always Free

Confirm the home region from region subscriptions before considering Always Free. Recheck the current Always Free documentation: 26ai eligibility depends on the tenancy home region. The service has two free databases, 20 GB each and 30 sessions; it cannot supply private endpoints or Autonomous Data Guard. No restore/manual/long-term backup entitlement: do not present this as a DR target.

Use an explicit workload and version. CLI 3.91 help announces that DW and 23ai values stop being accepted in December 2026; use LH for a new lakehouse and verify 26ai availability first. DB_NAME starts with a letter, contains only alphanumerics and has at most 30 characters. Prefer an existing Vault secret over a password in argv. Do not combine a free-tier change with ACL/password/mTLS changes.

Creation, start, stop, update, wallet issuance and even create --opc-dry-run are proposals only in this repo. A dry-run flag is service-specific and does not authorize a request. Before creation capture the exact compartment, network exposure, entitlement and cleanup implications; deletion is irreversible for free data. The SKILL start example has a stop inverse, which still causes downtime.

Source: Oracle CLI 3.91 help and the dated Always Free documentation linked from SKILL.md. No ADB provisioned or SQL executed here.
