# Obtain and configure SEO / ASO credentials

Official instructions checked on 2026-10-20. This guide is for the agent configuring a consuming project. Reuse existing access and configuration; enable only sources needed for the project's current work. Menu labels may change: follow the linked official instructions if the account UI differs.

## Agent handoff and checkpoints

1. Read `../context/project.md`, the tool registry, and existing non-secret configuration. Determine which property, app, or package is in scope, whether credentials already exist, and which person controls access. Inspect variable presence and file existence without printing secret contents.
2. Prepare or merge `growth/config.local.json` and `growth/.env` from their examples. Preserve existing values. Install optional authentication dependencies in the project's Python environment if needed; see [the executable setup](README.md#configure-once-per-project).
3. Guide the person through only the missing account steps below. The person handles sign-in, MFA, account-holder terms, and account actions the agent cannot perform. Continue other authorized preparation while waiting. Reuse existing authorization for routine setup; changes to permissions, resource creation, and report activation must stay within the person's actual delegation.
4. Ask for non-secret identifiers and the local paths where credential files were saved. Do not ask anyone to paste a private key, JSON credential contents, refresh token, or bearer token into chat. Have the person enter secret values directly in the local file or approved secret store.
5. Run local doctor, online doctor, then a small settled-date fetch. Diagnose the specific failure rather than requesting broader privileges by default. An online doctor success alone is not data acceptance.
6. Record the principal/key reference, resource scope, status, verification date, sample manifest, discrepancies, next step, and owner in the tool registry and current context. Record credential references, never credential contents. Mark the source Verified only after reconciling actual data.

## Which credential is needed?

| Source | Credential path supported by this template | Separate resource authorization | Fields to configure |
| --- | --- | --- | --- |
| SEO / Google Search Console | Google service-account JSON or user ADC; optionally a short-lived OAuth access token | Access to the exact Search Console property | `gsc.site_url`; Google environment variables |
| ASO / Google Play | Google service-account JSON or authorized user ADC; optionally a short-lived OAuth access token | Play Console bulk-report access to the developer's report bucket | `play.package_name`, `play.bucket`, `play.breakdown`; Google environment variables |
| ASO / Apple | App Store Connect team `.p8` key; optionally a short-lived JWT | Reporting role plus an active ONGOING Analytics Reports request | Numeric `apple.app_id`, `apple.report`; Apple environment variables |

These are owned-resource performance APIs. This setup does not provision keyword-volume, competitor-ranking, or advertising accounts. A public API key string is not the bearer credential accepted by these adapters.

## Local file layout and environment rules

Use `growth/.env` for credential variables and `growth/config.local.json` for source selection. Keep Google credential JSON and Apple `.p8` files outside the repository, for example in a project-specific directory under `~/.config/growth-credentials/`. On macOS/Linux, limit that directory to its owner and credential files to owner read/write. The example is a local storage convention, not a cloud account requirement.

```dotenv
# Example shape only: replace paths and identifiers locally; enable only needed sources.
GOOGLE_APPLICATION_CREDENTIALS=/absolute/private/path/google-reader.json
GROWTH_GOOGLE_ACCESS_TOKEN=
GROWTH_APPLE_KEY_ID=YOUR_KEY_ID
GROWTH_APPLE_ISSUER_ID=YOUR_ISSUER_ID
GROWTH_APPLE_PRIVATE_KEY_PATH=/absolute/private/path/AuthKey_YOUR_KEY_ID.p8
GROWTH_APPLE_ACCESS_TOKEN=
```

The script loads `growth/.env` automatically. Existing process variables win; blank file values are ignored. A nonempty bearer token takes precedence over refreshable credentials, so clear an old token from the runner when switching back to JSON or `.p8` authentication. Paths in this file may be quoted; `~` expands and relative paths resolve from the file's directory. `$VARIABLE` interpolation and shell commands are not evaluated.

When Google sources use different principals, run each with a separate external dotenv file using `--env-file /absolute/path/source.env`. Check inherited Google variables first: `--env-file` does not override them. One `fetch all` process uses one Google credential environment; it cannot independently select a GSC identity and a Play identity. Never broaden an account's access merely to make `all` convenient.

## Google credentials: choose the identity first

Prefer a suitable existing managed ADC identity when one is already available. For a local agent without one, a dedicated service account is a practical option if the organization permits downloaded keys. The two Google adapters can use the same JSON file while requesting their respective OAuth scopes, provided that identity has access to both resources. Google's credential discovery supports environment-selected files, local user ADC, and attached service identities. [ADC behavior](https://docs.cloud.google.com/docs/authentication/application-default-credentials)

### Create a service account and obtain its JSON key

1. In [Google Cloud Console](https://console.cloud.google.com/), select the intended project, or create one within the user's delegation. Open IAM & Admin > Service Accounts and create a named account such as `growth-reader`. Record its `NAME@PROJECT_ID.iam.gserviceaccount.com` email. Project IAM role assignment is optional here: do not grant Owner or Editor merely to read these product reports. Product authorization is configured separately below. [Service-account creation](https://docs.cloud.google.com/iam/docs/service-accounts-create)
2. Open that service account's Keys tab, add a new key, choose JSON, and create it. Save the downloaded file outside the repository. If organizational policy disables key creation, use an approved ADC route; do not weaken the policy as a setup shortcut. [Key creation instructions](https://docs.cloud.google.com/iam/docs/keys-create-delete)
3. Put its local path in `GOOGLE_APPLICATION_CREDENTIALS` in `growth/.env`. Leave `GROWTH_GOOGLE_ACCESS_TOKEN` empty and remove any unintended inherited token. The script obtains and refreshes access tokens; the person does not need to copy a token on each run. Downloaded JSON keys are reusable credentials, so an existing managed identity remains preferable where available. [ADC behavior](https://docs.cloud.google.com/docs/authentication/application-default-credentials)

The JSON key does not automatically grant Search Console or Play access. Complete the applicable product steps below. A Google Cloud project ID, an OAuth client ID, and an API key string cannot replace this JSON file.

## Google Search Console

1. Select the Google Cloud project associated with this credential. Under APIs & Services > Library, find and enable **Google Search Console API**. The adapter uses `https://www.googleapis.com/auth/webmasters.readonly`. [Official Python quickstart](https://developers.google.com/webmaster-tools/v1/quickstart/quickstart-python)
2. Open [Search Console](https://search.google.com/search-console) and select the intended verified property. If ownership is not yet verified, its owner must first complete an applicable verification method; a Domain property uses DNS verification. Do not silently create or select another property just because it is accessible. [Property verification](https://support.google.com/webmasters/answer/9008080?hl=en)
3. A property owner opens Settings > Users and permissions and adds the service-account email. For the user OAuth route, use the Google account that will sign in instead. Start with **Restricted** access for this read-only workflow. This recommendation follows from the documented read-permission requirement and the permission table allowing Restricted users to view Performance; verify the actual account with online doctor. Full or Owner access is not required for the current query adapter. [User permissions](https://support.google.com/webmasters/answer/7687615?hl=en), [API prerequisites](https://developers.google.com/webmaster-tools/v1/prereqs)
4. In `growth/config.local.json`, set `sources.gsc.enabled` to `true` and use the exact `site_url`: `sc-domain:example.com` for a Domain property, or the matching URL-prefix string such as `https://www.example.com/`. Preserve its protocol, host and path. Select dimensions and filters for the investigation. [Query property identifier](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
5. Agent: run `doctor gsc`, `doctor gsc --online`, and a settled-date `fetch gsc`. Record credential availability separately from property access and data reconciliation.


## Google Play Store Performance

1. Use the service-account email created above, or the human Google account chosen for OAuth. An authorized Play administrator opens [Play Console](https://play.google.com/console/) > Users and permissions > Invite new user and adds that identity. Google's bulk-report guide explicitly supports inviting a service-account email; it does not require signing in as that service account or checking its inbox. The adapter requests `https://www.googleapis.com/auth/devstorage.read_only`. [Report access guide](https://support.google.com/googleplay/android-developer/answer/6135870?hl=en)
2. Under **Account permissions**, grant **View app information and download bulk reports (read-only)**. This covers nonfinancial information and bulk downloads across the developer account's current and future apps. The app-only read permission is not equivalent. Explain this account-wide scope when arranging access; use manual exports if the owner does not permit it. Store Performance collection does not require the financial-data permission. [Permission definitions](https://support.google.com/googleplay/android-developer/answer/9844686?hl=en)
3. In Download reports > Statistics, choose the relevant app and locate **Copy Cloud Storage URI** by the section header. Take only the bucket component from the copied `gs://...` URI. For example, `gs://pubsite_prod_rev_0123456789/stats/...` yields `pubsite_prod_rev_0123456789`. Put this in `sources.play.bucket`, set the exact `package_name`, choose `country` or `traffic_source`, verify the report timezone, and enable the source. [Report location](https://support.google.com/googleplay/android-developer/answer/6135870?hl=en)
4. Agent: run `doctor play --online`, then fetch a settled month or a window within it. Verify the selected package and rows against the matching export. Missing recent files may reflect report availability rather than an invalid credential.

This adapter reads the developer's existing report bucket through the Cloud Storage JSON API. Do not create a new bucket, grant Storage Admin, or add Android Publisher / Play Developer Reporting API setup as prerequisites for this implementation. If an actual response identifies a disabled Cloud Storage API in a consumer project, address that specific project/service configuration. [Cloud Storage API](https://docs.cloud.google.com/storage/docs/json_api/v1)


## Google user OAuth / ADC alternative

Use this when the person already has product access and prefers interactive Google sign-in to a downloaded service-account key. The agent still performs routine local work; the person completes consent and MFA.

1. In the selected Cloud project's Google Auth platform, configure Branding and Audience. For an External app in Testing, add the intended login account as a test user. Under Data Access, include the read scopes for the sources being enabled. [Consent configuration](https://developers.google.com/workspace/guides/configure-oauth-consent)
2. Under Clients, create a **Desktop app** OAuth client and download its JSON outside the repository. This is OAuth client configuration, not a service-account key or ADC file. Do not point `GOOGLE_APPLICATION_CREDENTIALS` directly to this download. [OAuth client creation](https://developers.google.com/workspace/guides/create-credentials)
3. Use the installed Google Cloud CLI, or install it through the project's approved local tooling process. After checking for another project's existing ADC login, run the command below and let the person sign in with the identity authorized in Search Console and/or Play. This replaces the local ADC login, so do not silently overwrite unrelated credentials. `gcloud auth login` alone does not configure the ADC used by this script. [ADC login command](https://docs.cloud.google.com/sdk/gcloud/reference/auth/application-default/login)

```bash
gcloud auth application-default login \
  --client-id-file=/absolute/private/path/desktop-client.json \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/devstorage.read_only
```

Retain only the scopes needed: `webmasters.readonly` for GSC and `devstorage.read_only` for Play. A custom OAuth client is needed for the non-Cloud Search Console scope. After login, leave both Google variables blank in `growth/.env` and remove any shell/runner overrides. The library discovers the resulting local ADC file; on macOS/Linux its normal location is `~/.config/gcloud/application_default_credentials.json`. That file contains refresh credentials and must remain private. [ADC discovery](https://docs.cloud.google.com/docs/authentication/application-default-credentials)

For these scopes, an External OAuth app left in Testing receives refresh tokens that expire after seven days. Plan reauthentication or an approved longer-term setup before unattended use. Internal/production eligibility and verification depend on the audience and scopes; publishing is not a guaranteed verification bypass. [OAuth refresh-token expiration](https://developers.google.com/identity/protocols/oauth2#expiration)

The optional `GROWTH_GOOGLE_ACCESS_TOKEN` accepts an already-authorized short-lived OAuth token from the runner. It does not refresh itself and is not the normal setup path. Similarly, Apple bearer JWTs are optional; the standard `.p8` setup signs fresh tokens automatically.


## Apple App Store Connect Analytics

### 1. Confirm the app and API access

In [App Store Connect](https://appstoreconnect.apple.com/), choose the app, then General > App Information. Copy its numeric Apple ID into `sources.apple.app_id`; this is distinct from the Bundle ID and the developer Team ID. Choose `report: "discovery"` or `"downloads"`, verify the report timezone, and set `enabled: true`. [App information reference](https://developer.apple.com/help/app-store-connect/reference/app-information/app-information)

If API access is not enabled, the Account Holder opens Users and Access > Integrations, chooses App Store Connect API, requests access, and accepts Apple's terms. Approval is account-dependent; do not claim access exists while that request is pending. [API access instructions](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-api/)

### 2. Create or reuse the reporting team key

1. An Account Holder or Admin opens the API integration page and selects Team Keys.
2. Generate a named key for reporting with the **Sales and Reports** role. Use an existing suitable key if the account's credential policy permits it. This role is the routine download choice; enabling report generation is a separate Admin operation below. [Key setup](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-api/), [reporting roles](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports)
3. Download the private `.p8` key into the external credential directory. Apple allows this download once. If unavailable and no retained private key exists, an authorized account administrator must provision a replacement. Team keys cover the team's apps, even though this template queries only the configured app; do not describe the key as app-scoped. The template's signer expects a team key. [Key creation and download](https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api)
4. Copy the key's Key ID and the issuer identifier shown on the integration page into `GROWTH_APPLE_KEY_ID` and `GROWTH_APPLE_ISSUER_ID`. Set `GROWTH_APPLE_PRIVATE_KEY_PATH` to the downloaded file. The issuer identifier is not the app's numeric ID or developer Team ID. The script signs its own short-lived JWT; normally leave `GROWTH_APPLE_ACCESS_TOKEN` empty. [JWT identifiers](https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests)

### 3. Enable report generation once, using Admin access

An API key alone does not generate Analytics Reports. The agent first checks the app's existing requests and reuses an active ONGOING request. The routine `doctor apple --online` reports `report_setup_required` when one is missing or inactive. Creating a request needs an Admin key; the reporting key's role is intentionally insufficient. New reports may take 1-2 days to appear. [Report lifecycle](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports)

When report activation is within the user's delegation, the agent or account administrator performs this separate API setup operation:

- Read `GET /v1/apps/{app_id}/analyticsReportRequests` on `https://api.appstoreconnect.apple.com` and inspect all pages. Reuse an active ONGOING request; do not create duplicates.
- If no active request exists, authenticate the following POST with an Admin team-key JWT. Substitute the verified numeric app ID:

```http
POST https://api.appstoreconnect.apple.com/v1/analyticsReportRequests
Content-Type: application/json
Authorization: Bearer <ADMIN_JWT_CREATED_IN_MEMORY>
```

```json
{
  "data": {
    "type": "analyticsReportRequests",
    "attributes": {"accessType": "ONGOING"},
    "relationships": {
      "app": {"data": {"type": "apps", "id": "YOUR_NUMERIC_APP_ID"}}
    }
  }
}
```

A successful creation returns HTTP 201 and a request ID. Record that non-secret ID; use `sources.apple.request_id` when selection is ambiguous. This is an API setup recipe, not a shipped `data.py` subcommand or an App Store Connect UI switch. [Request endpoint and schema](https://developer.apple.com/documentation/appstoreconnectapi/post-v1-analyticsreportrequests)

An agent implementing the authorized one-off call can reuse `growth_data.auth.apple_token` for signing and `growth_data.core.HTTP` for transport in a separate process with the Admin credentials. Use `retry=False` for the POST; after a timeout or uncertain response, list requests again before deciding whether another POST is needed. Keep tokens out of terminal output and command arguments. Restore the routine Sales and Reports environment afterward; do not leave the runner configured with Admin access. Manage any temporary key according to the account's existing policy.

After report availability, the agent retries online doctor with the routine reporting key, then fetches a settled window. Historical ONE_TIME_SNAPSHOT access is a different operation and is not handled by the current fetch adapter.

## Validation and troubleshooting

Use the project's chosen Python interpreter. For the optional environment described in README:

```bash
growth/.venv/bin/python growth/scripts/data.py doctor gsc
growth/.venv/bin/python growth/scripts/data.py doctor gsc --online
growth/.venv/bin/python growth/scripts/data.py doctor play --online
growth/.venv/bin/python growth/scripts/data.py doctor apple --online
```

Run only the enabled source commands. Select a settled window, then run the corresponding `fetch SOURCE --start YYYY-MM-DD --end YYYY-MM-DD`. Those strings are date placeholders; replace them before execution. Reconcile several rows against a provider export or view with the same report, filters, dimensions and dates. Preserve reported missing coverage. Google and Apple report schemas and limits are linked in [sources.md](sources.md).

| Symptom | Agent checks and next step |
| --- | --- |
| `source_disabled` / `no_enabled_sources` | Confirm intended channels, then enable only those config entries; credentials alone do not enable collection. |
| `invalid_env` / `env_file_missing` | Check dotenv syntax or selected path without echoing values. Do not use multiline PEM/JSON in `.env`. |
| `missing_dependency` | Use the configured Python environment and install `requirements.txt` there. |
| `credentials_unavailable` | Check credential file existence/readability, chosen auth mode, inherited variables, and the ADC grant. A generic refresh failure may require reauthentication. |
| `http_401` | Check expired/revoked tokens or keys, matched Apple issuer/key/private-key values, and machine time. Replace externally managed expired tokens without printing them. |
| Google `http_403` | Verify the authenticated principal, exact resource grant and OAuth scope. For GSC also check API enablement/quota-project settings. For Play check bulk-report access; granting Cloud project Editor is not a substitute. |
| Apple `http_403` | Distinguish routine report access from Admin-only creation. Confirm role and account/API access before changing any permissions. |
| Apple `report_setup_required` | List requests; arrange authorized Admin activation if absent/inactive, then return to routine credentials. |
| Apple `report_unavailable` | Check the selected standard report, request ID, generation delay and retained date coverage. Repeatedly creating requests is not a fix. |
| Play `http_404` / partial missing month | Verify bucket, package, report breakdown and month against Download reports; check generation lag. No rows or missing objects are not proof of zero performance. |
| Play doctor fails but a known-object fetch succeeds | Doctor lists a narrow prefix; fetch reads known object paths. Document the difference between list access and object-read access rather than treating it as a metric failure. |
| `invalid_schema` / `source_mismatch` | Confirm export type, language, app identity and current official schema. Do not relabel incompatible data to make it parse. |
| Online doctor passes, fetch is partial | Account access can work while coverage, freshness or report integrity is incomplete. Keep validation status explicit. |

When rotating credentials, update the external file/reference, remove stale inherited tokens, rerun online doctor and a sample fetch, and record the validation date. Revoke old credentials only under the account owner's actual authorization and policy. Do not change business strategy merely because an access check failed.

## Ready-to-use agent prompt

> Configure this project's enabled SEO/ASO sources using growth/scripts/credentials.md. Inspect existing configuration and access first. Prepare local files and guide me through only the missing sign-in, account-owner and permission steps. Ask for identifiers and saved credential paths, not secret contents in chat. Reuse existing delegation, keep report activation separate from routine reads, then execute doctor and a settled sample fetch. Record verified access, data discrepancies and remaining blockers without fabricating successful setup.
