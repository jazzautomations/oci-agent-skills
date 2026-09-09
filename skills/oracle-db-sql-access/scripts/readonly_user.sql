-- Read-only audit as the exact agent database identity; not user provisioning.
-- No OCI calls. CLI helpers use scripts/lib/oci_ro. [unverified SQL]
whenever sqlerror exit failure rollback
set define off
select sys_context('USERENV','SESSION_USER') as session_user,
       sys_context('USERENV','CON_NAME') as container_name from dual;
select privilege from session_privs order by privilege;
select granted_role, default_role from user_role_privs order by granted_role;
select owner, table_name, privilege, grantable from user_tab_privs_recd
order by owner, table_name, privilege fetch first 200 rows only;
select privilege, admin_option from user_sys_privs order by privilege;
select tablespace_name, max_bytes from user_ts_quotas order by tablespace_name;
select 'REQUIRES_DBA_REVIEW_OF_PUBLIC_ROLE_SCHEMA_AND_EXECUTE_GRANTS' as result from dual;
