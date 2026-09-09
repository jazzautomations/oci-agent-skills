-- Read-only metadata only. No OCI calls; scripts/lib/oci_ro applies to CLI helpers.
-- Run in the already selected database/schema. [unverified: no SQL target here]
-- Missing V$ privileges stop the script; do not elevate automatically.
whenever sqlerror exit failure rollback
set define off
select sys_context('USERENV','SESSION_USER') as session_user,
       sys_context('USERENV','CON_NAME') as container_name from dual;
select name, value from v$parameter
where name in ('compatible', 'vector_memory_size') order by name;
select table_name, column_name, data_type
from user_tab_columns where data_type = 'VECTOR'
order by table_name, column_name fetch first 100 rows only;
select index_name, table_name, index_type, index_subtype, status
from user_indexes where index_type = 'VECTOR'
order by index_name fetch first 100 rows only;
select model_name, mining_function, algorithm from user_mining_models
order by model_name fetch first 100 rows only;
select object_name, procedure_name from all_procedures
where owner = 'SYS' and object_name in ('DBMS_VECTOR','DBMS_VECTOR_CHAIN','DBMS_HYBRID_VECTOR')
order by object_name, procedure_name fetch first 100 rows only;
