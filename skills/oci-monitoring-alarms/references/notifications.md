# Notifications and Events
Source: research/09b §11.
An ONS topic and its subscriptions are separate resources. Inspect subscription lifecycle and protocol without printing email addresses, webhook endpoints, PagerDuty secrets or confirmation links. Pending confirmation is not an active delivery path.
Alarm destinations are topic or other supported destination OCIDs, not raw webhook URLs. An HTTPS subscription must implement the expected handshake and delivery behavior; an arbitrary webhook URL is not automatically compatible.
Events rules select resource events and invoke actions. Their condition JSON is distinct from Monitoring MQL. Confirm event type, compartment and resource filters; do not create a rule to test a hypothesis.
Publishing to a topic, confirming a subscription or creating a rule can contact other people or run automation. These are proposals only. Route queue/streaming transport details to the owning integration skill.
