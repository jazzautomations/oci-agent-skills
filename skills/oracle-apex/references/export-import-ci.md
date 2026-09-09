# Export, import and drift

For APEXlang pin APEX/SQLcl 26.1-compatible versions and the project compiler metadata .apex/apexlang.json. Use the deployed SQLcl help to confirm syntax. Standard export is the source-control artifact; Full can include environment/runtime data. Static files and supporting objects require explicit inclusion decisions.

Export with apex export -applicationid <id> -exptype APEXLANG -dir <reviewed-dir>; validate with apex validate -input <dir> in an offline SQLcl /nolog session. -force deletes the target directory: never add it automatically. Without -force, deployments/default.json is merged, so check retained overrides. APEXlang import is whole-app and requires a REST-enabled schema; use SQL format for page-level delivery.

Import runs application/supporting SQL and may replace an existing app. Review workspace, parsing schema, app ID/alias, authentication, environment URLs and supporting-object choices before approval. Clear sticky APEX_APPLICATION_INSTALL state before setting target remaps. Preserve the previous app export and a separate schema/data rollback; reimport cannot undo arbitrary supporting DDL.

Web Credential secrets are omitted from exports. Rebind them from a CI secret store after a reviewed import; do not commit secret restoration scripts with values. SQLcl 26.1 project export changes directory layout, so distinguish that mechanical move from functional drift.

apex_drift.sql uses CHECKSUM-SH256, independent of app IDs, with an already selected workspace and numeric :app_id bind. Compare checksums across the same export options/version and preserve an unknown result if permissions fail. No export, import, SQL or UI operation was run here.
