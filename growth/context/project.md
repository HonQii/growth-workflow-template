# Project context and sources of truth

Project name: To fill in

Last verified: To fill in

Maintainer: To fill in

This is the project configuration entry point. Record references and necessary context rather than duplicating the full product specification.

## Product and resources

| Item | Current situation | Source and verification date |
| --- | --- | --- |
| Task the product solves | To confirm | To add |
| Product type and entry points | To confirm | To add |
| Current release status and available capabilities | To confirm; distinguish planned, implemented, and released | To add |
| Revenue model and pricing source | To confirm; noncommercial projects are supported | To add |
| Target regions and languages | To confirm | To add |
| Time, people, and spending limits per cycle | To confirm; record each separately | To add |
| Existing channels, content, users, or partnerships | To confirm | To add |

## Authoritative sources and delivery locations

Use actual project paths or URLs. Explicitly note missing sources; do not assume a `docs/` directory or a particular analytics service.

| Subject | Authoritative source or location | Owner / verification method |
| --- | --- | --- |
| Product capabilities, limitations, and release status | To fill in | To fill in |
| Technical event definitions and data collection | To fill in | To fill in |
| Payments, orders, or revenue records | To fill in / Not applicable | To fill in |
| Channel, search, or store data | To fill in / Unavailable | To fill in |
| Published website, store listing, or other public content | To fill in | To fill in |
| Official product-request tracker | To fill in | To fill in |
| Content and code validation commands / manual acceptance checks | To fill in | To fill in |
| Secure storage for credentials and raw data | Record only the location or access method, not secrets or personal data | To fill in |

## Publication and content constraints

- Capabilities that can be promised, with evidence: To confirm.
- Capabilities that cannot be promised or are not yet released: To confirm.
- Industry, platform, privacy, copyright, or professional review requirements: To confirm; include only applicable requirements and their sources.
- Content languages and localization requirements: To confirm.
- Publication channels, permissions, and authorized scope: To confirm.

## Open questions

| Gap | Decision or action it blocks | How to resolve it | Current status |
| --- | --- | --- | --- |

Prioritize gaps that would change the current action. Noncritical unknowns do not block independent work.

## Agent operating agreement

Record the person's actual instructions and supporting decisions. Unknown values do not grant authority. Existing authorization remains valid until changed.

| Setting | Project decision | Basis / last confirmed |
| --- | --- | --- |
| Goal delegated to the agent | To confirm; reference strategy | To add |
| Routine work the agent may execute | To confirm; distinguish collection, local edits, publication, outreach, and spending | To add |
| Decisions reserved for the person | To confirm | To add |
| Per-run time / cost limits and retry limits | To confirm | To add |
| Data collection cadence and source lag | To confirm by source | To add |
| Experiment review cadence or triggers | To confirm | To add |
| Context consolidation cadence | To confirm | To add |
| Workflow improvement review cadence | To confirm | To add |
| Project time zone | To confirm; retain source time zones in evidence | To add |
| Runner and schedule status | Not configured; record actual job reference after setup | To add |
| Concurrency | One writer per project; record how the runner serializes jobs | To add |
| Notification policy | Meaningful findings, completion, material failure, or required decisions; periodic summaries only if requested | To confirm |

The agent executes tools registered in `../scripts/README.md`, updates `current.md` after each run, and consolidates context at the agreed cadence. Documenting a schedule and installing it are separate actions.
