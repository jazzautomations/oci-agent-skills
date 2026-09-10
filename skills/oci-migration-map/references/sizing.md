# Sizing and price evidence

| Signal | Translation | Boundary |
|---|---|---|
| x86 core count | One core per E5 OCPU; absent cores use vCPU/2 | CPU options and SMT must be validated |
| Arm vCPU | A2: two cores/OCPU; A1: one core/OCPU | Rebuild, binary compatibility and capacity review |
| Memory | Increase OCPU to satisfy <=64 GB/OCPU | E5 <=1049 GB; A2 <=946 GB in dated docs |
| EBS IOPS / throughput | Solve supported VPU tier 10..120 | Never clamp an impossible request to 120 |
| Missing IOPS/RAM/architecture | Unknown | Never derive from machine-type spelling |
| Oracle DB | Base DB or suitability-tested Autonomous | Engine, edition, HA and licensing required |

The implementation conservatively uses 10+ VPU. Lower Cost has separate limits and is not
inferred from the generic IOPS equation. UHP 30+ requires multipath and supported shapes.
Block volumes round up to the 50 GB minimum; sizes above 32 TB require redesign.
Formulas: min(GB*(1.5*VPU+45),2500*VPU) IOPS;
min(GB*(12*VPU+360)/1024,20*VPU+280) MB/s. Validate workload latency separately.

Price API: public OCI PAY_AS_YOU_GO bands via shared lib.pricing; snapshot always printed.
AWS compute: region/OS-specific official calculator feed, exact Instance Type.
Azure: Retail Prices API, exact SKU/region/meter, Consumption, matching OS; a partial page
or ambiguous meter yields unknown. GCP without a pricing key/export yields unknown.
No AWS bulk 480 MB download. No credentials are needed for the public feeds.
Only the same priced subset is comparable. A whole-estate percentage is not calculated.

Sources reviewed 2026-09-10:
https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm
https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm
https://www.oracle.com/cloud/price-list/
https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html
