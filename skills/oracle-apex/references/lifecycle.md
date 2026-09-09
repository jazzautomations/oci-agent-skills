# Workspace, schema and upgrade lifecycle

Establish hosting first: managed ADB, customer-managed APEX/ORDS, or the hosted evaluation workspace. A workspace maps to one or more database schemas; an application has its own ID and parsing schema. APEX repository users and database users are separate identities. ADB ADMIN cannot be a workspace schema.

Read apex-details and connection-urls from the selected ADB; do not hardcode versions or construct URLs. For managed upgrades, an authorized instance administrator can inspect APEX_INSTANCE_ADMIN.GET_PARAMETER for UPGRADE_STATUS, UPGRADE_DEFERRED, UPGRADE_VERSION and UPGRADE_DATE. Do not deploy during RUNNING. Reading lifecycle AVAILABLE alone does not prove ORDS/APEX ready after a restart.

Workspace creation uses APEX_INSTANCE_ADMIN.ADD_WORKSPACE and schema/user provisioning, not an OCI workspace command. APEX_UTIL.CREATE_USER does not create a DB login. All setup and upgrade changes are proposals only here. oracleapex.com is for evaluation/learning and restricts instance administration; do not promise the ADB admin workflow there. SQL and UI lifecycle remain [unverified].
