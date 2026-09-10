# GCP inventory export

[unverified] No source credentials or functional gcloud installation used here. Bundle instances, machine_types and disks; remaining services are explicit coverage gaps.

```bash
gcloud compute instances list --project "$PROJECT" --limit 200 --format=json
gcloud compute machine-types describe "$MACHINE_TYPE" --zone "$ZONE" --project "$PROJECT" --format=json
gcloud compute disks list --project "$PROJECT" --limit 200 --format=json
```

Minimal IAM: Custom project role: compute.instances.list, compute.machineTypes.get, compute.disks.list. Project listing requires resourcemanager.projects.list only if discovery is authorized. Do not grant storage.objects.get.

The helper consumes an explicit JSON bundle with source_cloud, collected_at, scope.accounts,
scope.regions_scanned and scope.services_not_readable. Use native command response objects
under the documented bundle keys, or the common inventory schema. Preserve null unknowns.
Record every unread service and pagination token; never supply a truncated export as complete.
A CLI missing locally is not permission to simulate a successful cloud inventory.
The bundled fixture is labelled synthetic. Raw exports stay local and are not committed.

Sources (2026-09-10): https://cloud.google.com/sdk/gcloud/reference/compute/instances/list
