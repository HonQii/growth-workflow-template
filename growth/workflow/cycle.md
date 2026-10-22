# The experiment cycle: from hypothesis to next action

Keep a regular review cadence and choose actions based on the current question. Each project sets its cycle and budget. Weekly publication and proving an audience's superiority by a fixed week are not requirements.

This file defines experiment design and review. Agents execute individual runs using [agent-loop.md](agent-loop.md). An experiment may remain open across multiple runs; context consolidation and method improvements belong to the operating loop.

## 1. Choose the current question

Read the strategy, baseline, and unfinished experiments. Distinguish:

- Information gaps: User needs or reasons for choosing the product remain unclear.
- Measurement gaps: Key behavior cannot be reliably observed.
- Friction: Evidence shows users getting stuck at a particular step.
- Expansion opportunities: Repeated signals justify testing with more resources.

Choose a question that most affects the next investment and can yield information within budget. Observe multiple outcomes if useful, but keep the number of active changes interpretable.

For information gaps or reported friction, [problem discovery](problem-discovery.md) provides a bounded way to examine original accounts and existing approaches. A research run can complete without validating a product opportunity or creating a new experiment for every post.

Define entry conditions for the next action: usable evidence and a measurement contract before optimization, a verified effective date before observation, mature cohorts before retention review, and the original evidence thresholds before expansion. Calendar checkpoints trigger reviews, not mandatory changes or winners. Reconcile inherited weekly delivery plans with these conditions while preserving strategic thresholds and experiment history; stages need not form a universal linear funnel.

## 2. Record the experiment before execution

Use the format below. Bug fixes, factual corrections, and routine maintenance need not be framed as A/B experiments, but record their timing and potential impact.

Isolate variables where possible for causal comparisons. Without random assignment, document the comparison group, concurrent changes, and selection bias. A simple before-and-after comparison is not causal proof.

At publication, record the baseline and effective date; results remain pending until the observation window has elapsed. If later changes overlap the same pages, audience, or product path, record their dates and affected scope in the active experiment. Explain whether the original effect can still be separated; otherwise report the combined change descriptively, without attributing it to one variable.

## 3. Execute and observe

Complete deliverables using project and channel validation procedures. Record when changes actually go live or take effect. Drafted, submitted for review, and live are distinct states.

Set the observation period and time and spending limits at the start. If data is insufficient, extend, change methods, or stop. Reassess when resource limits are reached rather than waiting indefinitely for a sample. Every extension needs a new review date or trigger and a time or resource ceiling; it does not erase the original deadline or justify changing success thresholds.

## 4. Review and decide

Check data quality and comparability before interpreting results:

- **Continue observing:** Evidence is insufficient. State what is missing and the extension limit.
- **Adjust:** The hypothesis or execution has a correctable issue. Record the next change.
- **Expand:** Benefits and costs support more investment. State the scope and risks.
- **Stop:** A stopping condition is met, or the cost of further learning is too high.

Update changed strategy, baselines, or channel statuses while retaining the original experiment record. A negative finding can complete an experiment; output volume does not establish impact.

## Experiment record format

Save records in `growth/output/experiments/` from the project root, or its configured equivalent. Create the directory as needed. See [output/README.md](../output/README.md) for naming and status conventions.

```text
Experiment ID and title:
Owner:
Status: Proposed / Preparing / Running / Observing / Reviewed / Stopped
Record date:

Business question:
Hypothesis and supporting evidence:
Target audience, entry point, and use case:
Product facts and capability evidence:
Related strategy, metric definitions, and baseline:

Planned change:
Primary outcome and supporting metrics:
Control or comparison method:
Sample, observation period, decision thresholds, and rationale:
Alternative evidence or next action if data is insufficient:
Time / spending limits and stopping conditions:
Execution steps and delivery locations:

Actual effective date, version, and scope:
Changes or confounding factors during execution:
Observed sample, costs, and results:
Sources, measurement window, and missing data:
Supported conclusions:
What remains unknown:
Decision and rationale:
Next action, owner, and review date:
```

A review summary needs only facts, interpretation, decision, and next action. Do not guess results to fill the template. Fields describing events that have not happened should remain pending.
