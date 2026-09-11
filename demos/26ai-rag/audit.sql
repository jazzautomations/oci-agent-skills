-- MUTATING — explicit ADMIN setup on a dedicated demo database only.
-- Rollback: NOAUDIT POLICY RAG_DEMO_ACCESS BY RAGMCP; DROP AUDIT POLICY RAG_DEMO_ACCESS.
-- Does not grant audit, DDL or data-write privileges to the agent identity.
-- https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/adb-audit.html
DECLARE n NUMBER;
BEGIN
  SELECT COUNT(*) INTO n FROM audit_unified_policies WHERE policy_name='RAG_DEMO_ACCESS';
  IF n=0 THEN
    EXECUTE IMMEDIATE 'CREATE AUDIT POLICY RAG_DEMO_ACCESS ACTIONS SELECT ON RAGAPP.DOC_TAB, INSERT ON RAGAPP.DOC_TAB';
  END IF;
END;
/
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/AUDIT-Unified-Auditing.html
AUDIT POLICY RAG_DEMO_ACCESS BY RAGMCP
/
