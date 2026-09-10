# AWS inventory export

AWS response skeletons were checked in prior research with CLI 1.46.1; no AWS account was read. Check local --help before executing. Include S3/CloudWatch exports separately; Cost Explorer can charge per request.

```bash
aws ec2 describe-instances --region "$REGION" --max-items 200
aws ec2 describe-instance-types --region "$REGION" --max-items 200
aws ec2 describe-volumes --region "$REGION" --max-items 200
aws rds describe-db-instances --region "$REGION" --max-items 100
aws ec2 describe-vpcs --region "$REGION" --max-items 100
aws ec2 describe-subnets --region "$REGION" --max-items 200
aws elbv2 describe-load-balancers --region "$REGION" --max-items 100
```

Minimal IAM: ec2:DescribeInstances, ec2:DescribeInstanceTypes, ec2:DescribeVolumes, ec2:DescribeVpcs, ec2:DescribeSubnets, rds:DescribeDBInstances, elasticloadbalancing:DescribeLoadBalancers. These Describe actions require Resource *; add only the services actually assessed. No S3 GetObject or secret access.

The helper consumes an explicit JSON bundle with source_cloud, collected_at, scope.accounts,
scope.regions_scanned and scope.services_not_readable. Use native command response objects
under the documented bundle keys, or the common inventory schema. Preserve null unknowns.
Record every unread service and pagination token; never supply a truncated export as complete.
A CLI missing locally is not permission to simulate a successful cloud inventory.
The bundled fixture is labelled synthetic. Raw exports stay local and are not committed.

Sources (2026-09-10): https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html
