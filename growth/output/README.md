# Experiments and deliverables

Create subdirectories only when needed:

| Location | Contents |
| --- | --- |
| `experiments/` | Plans, execution changes, and reviews for each experiment; use the format in `../workflow/cycle.md` |
| `runs/` | Agent executions: tool outcomes, decisions, context updates, and workflow changes |
| `research/` | Dated source ledgers, search logs, task evidence, counterexamples, and candidate revisions; use `../workflow/problem-discovery.md` |
| `content/<channel>/` | Unpublished copy, asset descriptions, and publication records |

Use a stable identifier and short topic for experiment filenames, such as `exp-001-onboarding.md`. Record dates inside the file. When a release has its own lifecycle, follow the project's version naming convention.

## Current experiment index

Register new experiments here and update their status when it changes. Do not prefill invented results.

| Experiment | Status | Main question | Next review date or trigger |
| --- | --- | --- | --- |

## Problem-discovery research

Use a unique descriptive name such as `research/problem-signals-YYYYMMDD-topic.md`, or the project's existing research convention. Keep one investigation's scope, actual queries and coverage, deidentified evidence records, duplicate handling, failed reads, supporting and contradicting cases, candidate tasks, and next decision together. Link to the relevant experiment and run rather than copying their full history.

Retain original URLs or authorized internal references, dates with provenance, and reading completeness. Distinguish source observations from interpretation and untested product fit. Store no identifiable personal raw data here. Use the project's existing feedback system for feedback records; research notes only summarize and reference it. Add new research notes to the project's output index when created; the template contains no completed studies.

## Copy or asset records

For each deliverable, record:

- Project, channel, target audience, and desired action.
- Related experiment or maintenance task.
- Supporting product facts, asset sources, and applicable industry rules.
- Status: Draft / Awaiting review / Submitted / Published / Superseded. Omit inapplicable states.
- Actual publication location, effective date, and validation evidence. Do not mark future actions as complete.

Read language, review, and validation requirements from `../context/project.md`. Do not assume multiple languages or a particular platform format.

## Retention and updates

- Maintain published content in the project's designated authoritative location. Keep publication records or clearly labeled historical snapshots here, not a second maintained copy.
- When copy is replaced, note the new location. Preserve each experiment's original hypothesis, thresholds, and later adjustments.
- Summarize findings at the evidence or strategy authority registered in `../context/project.md`; update `baseline.md` / `strategy.md` as indexes when applicable. Link to the experiment rather than duplicating numbers or decisions across files.
- Follow the project's storage and access rules for raw exports. Keep secrets and person-level data out of these records. Configure ignore and cleanup rules before adding a local export directory.

## Agent run records

Use a unique stable ID such as `run-YYYYMMDDTHHMMSSZ.md`. Resume the same record for an interrupted execution rather than creating a second apparent execution. Link the latest record from `../context/current.md`.

```text
Run ID / trigger / scheduled window:
Started / finished / project time zone:
Status: Running / Completed / Partial / Blocked
Goal and delegated scope:
Prior run / experiments resumed:
Tools executed, parameters, and result manifests:
Actual data coverage / completeness / failures:
Observations and supported interpretations:
Actions completed and output paths:
External action receipts or uncertain outcomes:
Context updates and supporting evidence:
Workflow changes: prior behavior, evidence, change, validation or trial condition:
Experiment updates and remaining uncertainty:
Time / cost used where observable:
Decision needed, if any:
Next action, owner, and review date or trigger:
User notification and reason, if applicable:
```

Keep this record concise and link to artifacts rather than including raw tool dumps. A failed source may leave a run partial while independent work succeeds. Record that distinction. Preserve previous runs; the current-context summary is the compact entry point.
