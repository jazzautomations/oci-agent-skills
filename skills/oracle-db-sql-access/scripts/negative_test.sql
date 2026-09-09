-- Read-only risk report: no INSERT, CREATE, DROP or executable negative probes.
-- scripts/lib/oci_ro is the CLI-only wrapper; this file makes no OCI calls.
-- [unverified SQL] Real denial testing needs a separately approved isolated clone.
whenever sqlerror exit failure rollback
set define off
select privilege as unexpected_session_privilege
from session_privs where privilege <> 'CREATE SESSION' order by privilege;
select owner, table_name, privilege as unexpected_object_privilege
from user_tab_privs_recd where privilege not in ('READ', 'SELECT')
order by owner, table_name, privilege fetch first 200 rows only;
select granted_role as role_requiring_review from user_role_privs order by granted_role;
select 'NOT_CERTIFIED_READ_ONLY: ISOLATED_DENIAL_TEST_NOT_EXECUTED' as result from dual;
