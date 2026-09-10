-- MUTATING — not run in this repo. ADMIN prelude in a NEW dedicated demo database.
-- Supply :app_password and :mcp_password as private binds via setup.py --admin.
-- Rollback: DROP USER RAGMCP CASCADE; DROP USER RAGAPP CASCADE (irreversible).
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/load_onnx_model_cloud.html
DECLARE n NUMBER;
BEGIN
  SELECT COUNT(*) INTO n FROM all_users WHERE username='RAGAPP';
  IF n=0 THEN EXECUTE IMMEDIATE 'CREATE USER RAGAPP IDENTIFIED BY "' || REPLACE(:app_password,'"','""') || '"'; END IF;
END;
/
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/load_onnx_model_cloud.html
GRANT DB_DEVELOPER_ROLE, CREATE MINING MODEL TO RAGAPP
/
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/utl_to_chunks-dbms_vector_chain.html
GRANT EXECUTE ON SYS.DBMS_VECTOR TO RAGAPP
/
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/utl_to_chunks-dbms_vector_chain.html
GRANT EXECUTE ON SYS.DBMS_VECTOR_CHAIN TO RAGAPP
/
-- https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/manage-users-create.html
ALTER USER RAGAPP QUOTA 100M ON DATA
/
-- https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/sqlcl-mcp-server-tools.html
DECLARE n NUMBER;
BEGIN
  SELECT COUNT(*) INTO n FROM all_users WHERE username='RAGMCP';
  IF n=0 THEN EXECUTE IMMEDIATE 'CREATE USER RAGMCP IDENTIFIED BY "' || REPLACE(:mcp_password,'"','""') || '"'; END IF;
END;
/
-- https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/sqlcl-mcp-server-tools.html
GRANT CREATE SESSION TO RAGMCP
/
