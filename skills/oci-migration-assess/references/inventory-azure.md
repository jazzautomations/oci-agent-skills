# AZURE inventory export

[unverified] No Azure account or az CLI used here. These list commands may return the full selected subscription; bound the exported file and disclose scope. Bundle vms, vm_sizes and disks; supply architecture from resource SKU capabilities, not a name guess.

```bash
az vm list --subscription "$SUBSCRIPTION" --output json
az vm list-sizes --location "$LOCATION" --subscription "$SUBSCRIPTION" --output json
az disk list --subscription "$SUBSCRIPTION" --output json
```

Minimal IAM: Custom role, restricted to the selected subscription/resource groups: Microsoft.Compute/virtualMachines/read, Microsoft.Compute/locations/vmSizes/read, Microsoft.Compute/disks/read. No DataActions. Do not add keys/list/action.

The helper consumes an explicit JSON bundle with source_cloud, collected_at, scope.accounts,
scope.regions_scanned and scope.services_not_readable. Use native command response objects
under the documented bundle keys, or the common inventory schema. Preserve null unknowns.
Record every unread service and pagination token; never supply a truncated export as complete.
A CLI missing locally is not permission to simulate a successful cloud inventory.
The bundled fixture is labelled synthetic. Raw exports stay local and are not committed.

Sources (2026-09-10): https://learn.microsoft.com/en-us/cli/azure/vm?view=azure-cli-latest
