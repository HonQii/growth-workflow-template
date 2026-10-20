# Metric definitions and validation

Define business metrics here and reference the project's existing events or data tables. Actual values belong in `../context/baseline.md`; cycle-specific targets belong in experiment records.

## User and business paths

Describe the product's actual paths and branches, such as reaching users with a need, intent, obtaining value, repeat use, payment, and referral. Keep only applicable steps.

- The same action may have several entry points. Account for both free and paid paths.
- In B2B products, accounts, users, and payers may differ. One-time transactions do not require subscription retention definitions.
- Downloads, registrations, clicks, and successful feature execution may be proxies. Explain their relationship to business value.

## Metric dictionary

| Metric | Business question | Numerator / denominator or formula | Unit and deduplication key | Sequence and time window | Source and validation status |
| --- | --- | --- | --- | --- | --- |

For each metric in use, also specify:

- Cohort entry point and inclusion / exclusion rules, including internal, test, or repeated actions.
- Platform, channel, version, region, and time zone.
- Event, data table, or manual observation source; collection validation date and evidence.
- Status: Undefined / Defined but unverified / Verified / Partially observable / Not applicable.
- Interpretation limits: A click indicates intent, an order does not establish payment, and an active subscription does not establish continued use.

"Users who completed / users who started" is a funnel conversion rate only within the same cohort, sequence, and window. Do not mix it with sitewide event counts. Measure task success by task and user activation by user or account; do not combine them into one metric.

## Cross-platform attribution

| Path | Observable portion | Basis for connecting steps | Missing portion | Supported conclusions |
| --- | --- | --- | --- | --- |

Distinguish direct attribution, aggregate comparisons, and unattributable activity. Do not assemble web clicks, store installs, and product use into a per-user funnel without evidence that those steps can be connected.

## Usage rules

- Choose a small set of metrics that answers the current question. A universal north-star metric is not required for every project.
- Match return-use windows to actual need frequency. Distinguish reopening from obtaining value again.
- For payment, state the authoritative revenue source and treatment of refunds and costs. A client-side success message is not a complete financial record.
- If collection is unreliable, plan validation or explicitly use alternatives such as interviews or manual observation. Missing data is not evidence of channel failure.
