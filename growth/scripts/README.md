# Agent tools and data adapters

The agent runs these tools, checks evidence quality, and writes supported conclusions to context and run records. People supply missing access or business decisions. All commands below run from the product repository root; the scripts also resolve their default configuration and storage correctly from other working directories.

## Project tool registry

| Tool / source | Implementation / acceptance boundary | Command | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |
| Configuration / access | Implemented; project acceptance tracked in current context | `python3 growth/scripts/data.py doctor all` | Local config; `--online` adds read-only access checks | JSON result; online success is narrower than data validation |
| Search Console | Implemented; project acceptance tracked in current context | `python3 growth/scripts/data.py fetch gsc --start DATE --end DATE` | Property read access and Google credentials | Daily query snapshots and normalized rows |
| Apple Analytics | Implemented; project acceptance tracked in current context | `python3 growth/scripts/data.py fetch apple --start DATE --end DATE` | Active ONGOING report request and Apple credentials | Standard daily discovery or downloads report, revised by event date |
| Google Play | Implemented; project acceptance tracked in current context | `python3 growth/scripts/data.py fetch play --start DATE --end DATE` | Private report bucket read access and Google credentials | Monthly Store Performance exports, filtered to event dates |
| Local report import | Implemented; offline fixtures validated | `python3 growth/scripts/data.py import apple|play ...` | Supported complete English report export | Same normalized schema and immutable snapshots |
| Period comparison | Implemented; offline fixtures validated | `python3 growth/scripts/data.py compare --before MANIFEST --after MANIFEST` | Compatible snapshots with adequate coverage | Changes at each original dimension group |

This registry describes adapter implementation and acceptance requirements. Maintain live project access and next actions in `context/current.md`; retain dated validation evidence in baselines and runs. Mark project access verified only after checking real account data against the matching provider view or export. An offline fixture is not live-account verification. Source-level results remain independent in `fetch all`; a failed source cannot become an empty success.

## Configure once per project

Start with [credential application and setup](credentials.md) when access is missing. It covers account roles, console steps, downloaded files, OAuth alternatives, Apple report activation, and the agent/person handoff.

1. Copy [config.example.json](../config.example.json) to `growth/config.local.json` if it does not already exist. Fill the stable project ID and only relevant sources; set their `enabled` fields to `true`. Preserve existing configuration.
2. Verify the exact Search Console property, Apple app ID, or Play package and report bucket. Verify each report's timezone against the project source; example timezones are starting values, not discovery of account settings. GSC dates use `America/Los_Angeles`.
3. Copy [.env.example](../.env.example) to `growth/.env` if it does not exist. Fill only the required credential variables or external file paths. Existing runner/shell variables take precedence. Never put credentials in JSON configuration, CLI arguments, the run record, or Git; keep private-key and credential JSON files outside the repository.
4. Run local `doctor`, then `doctor --online` when account access is available. Fetch a settled window and reconcile a small sample with the provider. Record source scope, date, manifest, and discrepancies in the authoritative evidence record referenced by `context/baseline.md`; update live access readiness and next action only in `context/current.md`.

Python 3.9+ is required. Import, comparison, local doctor, and supplied bearer-token authentication use the standard library. Google ADC and Apple team-key signing need the optional dependencies. If the project has no suitable Python environment, the agent can create one locally:

```bash
python3 -m venv growth/.venv
growth/.venv/bin/python -m pip install -r growth/scripts/requirements.txt
growth/.venv/bin/python growth/scripts/data.py doctor all
```

Use that environment's Python for subsequent calls. The initializer installs nothing.

### Environment file

The CLI automatically loads this workspace's `growth/.env`, independent of the working directory. A missing default file is allowed when the runner supplies credentials or existing ADC is available. Blank example values are ignored, so unused settings do not disable ADC discovery. Existing process variables, including explicitly empty ones, are never overwritten. This also means an inherited bearer token takes priority over key credentials loaded from the file; unset that token in the runner when switching authentication methods.

Supported variables are `GOOGLE_APPLICATION_CREDENTIALS`, `GROWTH_GOOGLE_ACCESS_TOKEN`, `GROWTH_APPLE_KEY_ID`, `GROWTH_APPLE_ISSUER_ID`, `GROWTH_APPLE_PRIVATE_KEY_PATH`, and `GROWTH_APPLE_ACCESS_TOKEN`. Other assignments are ignored. The loader supports single-line `KEY=VALUE`, optional `export`, literal single/double quotes, full-line comments, and whitespace-prefixed inline comments. It does not execute shell commands, expand `$VARIABLES`, process escape sequences, or accept multiline values. Put JSON and PEM contents in external files rather than inline values. Malformed files return a sanitized error without printing values.

Paths loaded from the file expand `~`; relative credential paths resolve from the `.env` directory. Environment variables already supplied by the runner retain their original values. Root `.env` files are not searched automatically. To explicitly use one or a runner-managed dotenv file, put the global option before the command:

```bash
python3 growth/scripts/data.py --env-file /absolute/path/to/project/.env doctor all --online
```

An explicitly selected missing file is an error. `--config` selects only JSON configuration and does not change dotenv discovery. `compare` does not load credentials or read an environment file. No dotenv dependency or shell `source` command is needed.

### Google authentication

Use Application Default Credentials with the source's required read scope, or inject a short-lived `GROWTH_GOOGLE_ACCESS_TOKEN` through the runner. For a supported credential file, `GOOGLE_APPLICATION_CREDENTIALS` references its external path. Do not assume ADC created for a different API has the necessary scope. The script refreshes ADC tokens when needed; externally supplied tokens must be renewed externally.

- GSC: `https://www.googleapis.com/auth/webmasters.readonly`. Enable the Search Console API for the credential project and grant the principal access to the exact property.
- Play: `https://www.googleapis.com/auth/devstorage.read_only`. Grant report access through the account's supported Play Console arrangement. GCS scopes alone do not grant access to its private bucket.

An `all` run using one externally supplied Google token requires both scopes and both permissions. Otherwise use separate source runs with the corresponding credential environment. Neither flow creates accounts or changes permissions. See [the authentication and API references](sources.md).

### Apple authentication and report setup

Use an App Store Connect **team** API key: set `GROWTH_APPLE_KEY_ID`, `GROWTH_APPLE_ISSUER_ID`, and `GROWTH_APPLE_PRIVATE_KEY_PATH` in `growth/.env` or the runner. The path points to an external `.p8` file. For compatibility, `key_id` and `issuer_id` in local JSON config remain fallbacks when their environment variables are empty or absent. The script signs short-lived ES256 JWTs. Alternatively inject `GROWTH_APPLE_ACCESS_TOKEN`; token creation and renewal then belong to the runner.

Select `report: "discovery"` or `"downloads"`. The adapter accepts standard report names, including the `Standard` suffix, and rejects Detailed exports. Optional `request_id` and `report_id` resolve ambiguous selections; they must belong to the configured app and supported standard report.

An authorized admin must first enable an ONGOING Analytics Reports request. If absent or inactive, `doctor --online` and `fetch` return `report_setup_required`; they do not issue a creation request. First report generation is asynchronous. Setup, historical ONE_TIME_SNAPSHOT requests, and remote writes are outside this CLI. See [Apple's request workflow](https://developer.apple.com/documentation/appstoreconnectapi/downloading-analytics-reports).

## Execute and inspect

```bash
# Config checks only; does not claim live access.
python3 growth/scripts/data.py doctor all
# Narrow read-only online checks for each enabled source.
python3 growth/scripts/data.py doctor all --online

# Illustrative settled windows; select dates appropriate to the actual run.
python3 growth/scripts/data.py fetch gsc --start 2026-09-01 --end 2026-09-07
python3 growth/scripts/data.py fetch apple --start 2026-09-01 --end 2026-09-07
python3 growth/scripts/data.py fetch play --start 2026-09-01 --end 2026-09-07
python3 growth/scripts/data.py fetch all --start 2026-09-01 --end 2026-09-07

# Import every segment of ONE Apple instance in the same call.
python3 growth/scripts/data.py import apple --start 2026-09-01 --end 2026-09-07 --processing-date 2026-09-10 --file /path/to/segment.csv.gz
python3 growth/scripts/data.py import play --start 2026-09-01 --end 2026-09-07 --file /path/to/store_performance.csv

python3 growth/scripts/data.py compare --before /path/to/earlier/manifest.json --after /path/to/later/manifest.json
```

Repeat `--file` for segments or nonoverlapping monthly exports. Apple instances may cover only a few event dates; importing one instance does not establish a full week. Use live `fetch` to assemble revisions across instances. Local imports cannot verify that all provider segments were supplied. Do not mix old and corrected exports: import one complete revision, or fetch again. Unknown schemas and conflicting duplicate rows fail explicitly. Exact duplicate rows are collapsed.

For another configuration file, place the global option before the command: `python3 growth/scripts/data.py --config /path/to/config.json doctor all`. The output still belongs to this copy's `growth/.local-data/`. `--help` is available at the top level and each subcommand.

Supported imports are Apple standard daily discovery/downloads and Play Store Performance `country` or `traffic_source`. The parser accepts comma or tab separators, UTF-8 (optional BOM), BOM-marked UTF-16, and gzip. Localized headers, Apple Sales and Trends, Detailed reports, and arbitrary dashboard CSVs require a separate adapter; they are not guessed into the same schema.

## Result and storage contract

Every operation emits JSON to stdout. Help uses ordinary terminal help. Exit codes:

| Status | Exit | Meaning |
| --- | --- | --- |
| `ok` | 0 | The requested operation succeeded within its stated scope and limitations |
| `partial` | 2 | Some requested data or comparability is missing, suppressed, immature, or failed |
| `unavailable` | 3 | Disabled source, missing access/setup/dependency, or unavailable provider |
| `error` | 1 | Invalid configuration, input, schema, integrity, or other failed operation |

`ok` does not mean a provider's dataset is exhaustive or a hypothesis is validated. Local doctor explicitly returns `access_verified: false`. A successful empty query has `row_count: 0`; a fetch failure has `row_count: null` and an error code. Missing-date lists do not synthesize zero rows. A recent window receives `partial` under conservative lag checks; Apple also checks each event date's processing revision. Missing whole Play months retain successfully read months with `partial` and month-level errors.

Fetch/import results contain `definition` (identity, report, dimensions, timezone, filters, aggregation), requested window, observed coverage, extraction time, limitations, provenance, artifact hashes, and paths. Raw exports and `rows.json` are saved alongside `manifest.json` under `growth/.local-data/<source>/<unique-run>/`. Raw filenames are opaque; manifest provenance identifies Play object generations and Apple date revisions without signed URLs. GSC raw responses plus the definition reconstruct the daily query parameters.

Each snapshot is independent. Re-running creates a replacement candidate, never an additive batch. Choose one relevant snapshot per source/window/report for a review. **Do not sum all files from the snapshot directory.** A comparison takes two explicit manifests and verifies normalized-file hashes. It requires the same project, source, identity, filters, timezone, dimensions, aggregation, equal-length nonoverlapping windows, and successful daily coverage. Missing group-days yield null changes rather than inferred zeros. It excludes Apple unique counts, reports Play daily-count sums without a period-unique rate, and derives GSC CTR/position from the appropriate counts.

The copied [ignore rules](../.gitignore) exclude local config, snapshots, virtual environments, caches, environment files, and `.p8` keys. The initializer also excludes these paths and source symlinks when copying. Other externally named credential files must remain outside the repository. Local evidence is not backed up by Git: agree a retention/access policy and preserve needed snapshots before cleanup. There is no automatic deletion.

Network calls use HTTPS, 30-second request timeouts, at most two retries for transient failures, and a 200-request budget per source. Downloads are capped at 50 MiB per response and 256 MiB per source run; decompressed imports are capped at 50 MiB each. Authenticated requests cannot redirect or forward credentials to another host. Provider error bodies and signed URLs are not emitted. A budget or atomic Apple/GSC failure does not publish an incomplete dataset; successful independent sources can still finish. Narrow large queries or use provider exports when limits are reached.

## Write evidence back into the workflow

Follow the operating loop linked from the [workspace rules](../AGENTS.md), using the project's actual workflow paths. Record the actual command, window, status, manifest paths and relevant caveats in `output/runs/`. Compare compatible snapshots, explain missing coverage, then update `context/baseline.md` and the compact `context/current.md` handoff. Change `workflow/` only when a run supplies evidence for the change. The CLI performs deterministic collection and arithmetic; the agent owns interpretation, context consolidation, and experiment decisions.

These adapters cover owned-property performance. They do not supply competitor intelligence, market keyword volume, independent ASO keyword ranks, a technical SEO crawler, or user-level attribution across web and stores. Enable additional sources only for a concrete project question. No recurring job is installed by these scripts.

## Maintenance

Implementation modules live in [growth_data/](growth_data/): `core.py` (transport/config/snapshots), `auth.py`, `environment.py` (project dotenv loading), `reports.py` (schemas), `providers.py`, and `compare.py`. Dependencies are in [requirements.txt](requirements.txt); official references and collection limits are in [sources.md](sources.md).

In the template source repository run `python3 -m unittest discover -s tests -v`. Tests use synthetic exports and mocked provider calls, including pagination, access failure, correction replacement, schema mismatch, incomplete months, comparison guards, and use after copying. No account is connected by the test suite. Validate a real sample before marking a project source Verified.
