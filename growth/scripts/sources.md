# SEO / ASO source contracts

Official documentation checked on 2026-10-20. These references describe provider contracts; offline implementation tests are not evidence of live project access. Re-check relevant documentation when a schema or authorization behavior changes.

| Source | Official reference | Implementation consequence |
| --- | --- | --- |
| Search Console | [Search Analytics query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query), [performance-data extraction](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data) | Query each day using final data, exact property, selected dimensions and filters; paginate 25,000-row responses. PT dates and provider aggregation are preserved. Top-row and privacy limits prevent a guarantee of exhaustive detailed data. |
| Google credentials | [google-auth user guide](https://google-auth.readthedocs.io/en/latest/user-guide.html) | ADC is optional; scopes and access to the selected resource must both be valid. |
| Apple report lifecycle | [Download analytics reports](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports) | Discover the app's existing request, then report, instances and all segments. Admin setup is separate; supported read roles include Admin, Sales and Reports, and Finance. Initial generation can take 1-2 days. |
| Apple authentication | [Generate API tokens](https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests) | Team-key ES256 signing uses issuer, key ID, audience and a short expiry. |
| Apple discovery | [App Store Discovery and Engagement](https://developer.apple.com/documentation/analytics-reports/app-store-discovery-and-engagement) | Standard daily event counts and unique counts have different aggregation properties; Get engagement is not a verified install. Report completeness is normally within three days. Search includes Search Ads. |
| Apple downloads | [App downloads](https://developer.apple.com/documentation/analytics-reports/app-download) | Preserve download type, including first-time downloads, redownloads and updates. Normal completeness is within two days. |
| Apple corrections | [Data completeness and corrections](https://developer.apple.com/documentation/analytics-reports/data-completeness-corrections) | A newer processing date replaces all records for the corresponding event date. Never merge those date partitions across instances. Fetch retained later instances as well, because old dates can be corrected. |
| Apple integrity | [Segment attributes](https://developer.apple.com/documentation/appstoreconnectapi/analyticsreportsegment/attributes-data.dictionary) | Check returned byte size and MD5 when provided; download URLs remain transient. |
| Google Play | [Download monthly reports](https://support.google.com/googleplay/android-developer/answer/6135870?hl=en) | Fetch the current Store Performance export under `stats/store_performance/`, by package, month and country/traffic-source breakdown. Exports can lag 3-7 days. Parse the documented fields and supported encodings; do not use retired retained-installer exports. |
| GCS retrieval | [Objects.get](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/get), [Objects.list](https://docs.cloud.google.com/storage/docs/json_api/v1/objects/list) | Read metadata then download the pinned generation with `alt=media`; scope doctor listing to the configured package prefix. |

For credential creation, account permissions and first-run activation, use [the credential setup guide](credentials.md). It cites the official account-management and authentication instructions alongside each step.

## Interpretation boundaries

The implementation retains report dimensions instead of inventing a shared cross-store funnel. Apple unique users cannot be summed into period uniques. Play comparison totals are sums of daily observations, not unique people over a week. GSC page/query breakdowns are not substitutes for property totals. Ratios and average positions need the appropriate denominator; zero and unavailable values have different meanings.

The configured Apple/Play timezone is explicit and must be verified for the actual report. Scripts do not shift date-only rows between timezones or infer account settings from a machine clock. Source lags are conservatively flagged, not guarantees against later corrections.

## Live acceptance checklist for an enabled source

- Record the exact configured property/app/package, report, dimensions, filters and timezone.
- Confirm read access with online doctor, then fetch a small settled window.
- Reconcile dates and several metric rows with the matching provider export/view and identical scope.
- Check raw and normalized artifact hashes, schema, missing dates, suppression and report revisions.
- Repeat retrieval to verify replacement semantics; investigate changes rather than adding snapshots together.
- Compare two equivalent periods only after resolving coverage limits. Record acceptance evidence or the unresolved discrepancy in the project tool registry.
