# ADB and APEX application topology

The Oracle architecture “Deploy a Secure Production-ready Oracle Autonomous Database and Oracle APEX Application” (created 2022-06-23) uses a load balancer, private application infrastructure, a private ATP endpoint and NSGs. Review DNS, routes, client egress and the database ACL together; an IAM success does not establish SQL network reachability.

This paid/private-endpoint pattern cannot be promised on Always Free. For a small public-ACL application, document stable egress and bounded sessions explicitly; for production isolation use the private-endpoint architecture after a reviewed cost/network proposal. The historical Terraform example is a design reference, not evidence of current deployability. APEX lifecycle belongs to oracle-apex; SQL agent identity belongs to oracle-db-sql-access.
