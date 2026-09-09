-- Read-only checksum of an existing application; no OCI calls.
-- CLI helpers use scripts/lib/oci_ro. [unverified: no SQL target here]
-- Preselect the authorized workspace and bind :app_id as NUMBER before invoking.
whenever sqlerror exit failure rollback
set define off
set serveroutput on size 100000
select version_no from apex_release;
declare
  l_files apex_t_export_files;
begin
  if :app_id is null or :app_id <= 0 or :app_id <> trunc(:app_id) then
    raise_application_error(-20001, 'A positive numeric app_id bind is required');
  end if;
  l_files := apex_export.get_application(
    p_application_id => :app_id, p_type => 'CHECKSUM-SH256', p_with_date => false);
  if l_files.count = 0 then
    raise_application_error(-20002, 'No checksum returned; drift is unknown');
  end if;
  for i in 1 .. l_files.count loop
    dbms_output.put_line(dbms_lob.substr(l_files(i).contents, 4000, 1));
  end loop;
end;
/
