# Set up a project

Establish an evidence-based project context and an actionable first plan. Completing every field is not the goal. Setup does not automatically launch channels, publish content, or purchase traffic.

This file travels with `growth/` and is intended to be executed by an agent. The person provides goals, constraints, access, and reserved decisions. For an existing workspace, fill gaps and verify outdated information without resetting or replacing prior decisions.

## 1. Read the project before asking questions

Read the target project's repository rules, README, relevant product and release materials, and existing growth files. Inspect implementation or user-provided data where needed; a full codebase review is not required.

Fill in verifiable information in [project context](context/project.md):

- Who the product serves, the task it solves, and available entry points.
- Released versus planned capabilities, with supporting sources.
- Regions, languages, pricing or business model, and published-content locations.
- Available people, time, budget, and channel resources.
- Data sources, access status, publication rules, and acceptance checks.

Do not treat local implementation as a release or automatically request backend access or create accounts. Record conflicting sources and the unresolved question.

## 2. Ask only questions that determine the next action

Summarize what is confirmed, then group the critical missing inputs for this cycle. Usually prioritize:

1. What matters most now: validating demand, acquiring initial users, activation, return use, payment, or improving an existing channel?
2. How much time and money are available, and which constraints cannot change?
3. Which real users, channels, data, or product capabilities provide a starting point?

Do not repeat questions answered by materials or the conversation. Ask about audience, region, or channel preferences only when they affect the current choice. A full questionnaire is not a prerequisite.

Keep unanswered critical inputs marked "To confirm." Silence does not authorize a budget or publication. Continue work that does not depend on those answers.

## 3. Establish the current strategy

Register the authoritative strategy location in [project context](context/project.md). Use [growth strategy](context/strategy.md) as the default, or keep it as an index to an existing strategy when merging. Document at that authority:

- The current goal and its basis.
- The priority audience, demand trigger, and reason to choose the product.
- One or a few hypotheses that most need testing.
- The scope of active work in the first cycle and what is deferred.

Preserve established strategic choices. If evidence suggests a problem, propose a supported adjustment rather than silently changing positioning, pricing, or markets during setup.

Without user data, the first cycle may investigate demand or observe product use. It need not start with articles or advertising.

When direct evidence is limited, consider a bounded [problem-discovery run](workflow/problem-discovery.md). Select relevant source categories and record actual project sources in [channels](workflow/channels.md#problem-discovery-sources); do not enable all platforms or import another project's audience, findings, or numeric limits.

## 4. Make the goal observable

Complete [metric definitions](workflow/metrics.md) and the [baseline](context/baseline.md):

- Which outcomes indicate progress, with their units, windows, and sources.
- Whether collection is reliable; distinguish unverified events from true zero values.
- What can be compared directly and where cross-platform or audience gaps remain.
- Which manual observations offer limited but useful evidence when quantitative data is unavailable.

Do not require every project to use the same analytics platform. Do not invent metrics, industry benchmarks, or sample thresholds to fill fields.

## 5. Prepare the first cycle

Enable only the channels needed for this cycle in [channel workflows](workflow/channels.md). Follow the [experiment cycle](workflow/cycle.md) to create a first record in `output/experiments/`, such as `exp-001-first-validation.md`.

At minimum, describe the business question, hypothesis, concrete actions, expected deliverables, observation method, resource limits, stop or adjustment criteria, and the next review date or trigger.

Mark observation periods and thresholds as exploratory when their basis is uncertain. Keep the plan proposed if critical inputs are missing; its first step may be obtaining evidence. Reaching a date does not mean the sample is sufficient.

## 6. Configure agent operation

Complete the operating agreement in [project context](context/project.md): delegated work, reserved decisions, resource limits, time zone, collection and review cadence, context consolidation, and notification conditions. Reuse permissions already established rather than asking for them again.

Register actual scripts or connected tools in [scripts/README.md](scripts/README.md). The agent checks availability and executes authorized validation. Missing adapters are gaps, not working integrations. People supply access the agent cannot obtain or decisions it cannot infer.

For enabled SEO/ASO sources, follow [the adapter setup](scripts/README.md): preserve or create local configuration from the example, preserve or create `growth/.env` from `.env.example` for credential variables and external key paths, run configuration checks and authorized online checks, then reconcile a settled sample. Keep access unverified until real data is checked. All sample sources start disabled. When access is missing, use [the credential setup guide](scripts/credentials.md) to guide only the necessary account steps and then let the agent execute validation.

Initialize [current context](context/current.md) with the first plan, evidence readiness, blockers, and next action. Use [the agent loop](workflow/agent-loop.md) for the first authorized execution and subsequent runs.

Keep a desired schedule separate from an installed job. Configure an external runner only when requested. If scheduling is blocked, record what is missing and do not claim the process is automated.

Before completion, reconcile inherited calendar plans with evidence gates, verify consistent metric definitions and observable join keys, mark historical findings for revalidation, and record known concurrent changes in active experiments. Preserve original decisions and thresholds; unresolved conflicts belong in current context.

## 7. Check readiness

- [ ] Project context cites real sources, with unknowns recorded separately.
- [ ] The current goal and resource limits are clear, or gaps blocking the cycle are explicitly identified.
- [ ] Actual product capabilities are distinguished from public promises.
- [ ] First-cycle metrics are observable, or collection validation or manual observation is planned.
- [ ] Channels and first actions have a rationale; they were not all enabled because the template lists them.
- [ ] The first record is executable, or marked as preparing while critical inputs are pending.
- [ ] The new experiment is registered in the [output index](output/README.md).
- [ ] Published content, scripts, and data follow the project's validation and storage rules.
- [ ] The project's ignore rules allow plans and reviews to be committed while excluding personal raw data and secrets.

- [ ] The operating agreement states what the agent can do and when a person must decide.
- [ ] Tools have honest availability and validation status.
- [ ] Current context allows a fresh agent to resume and owns live readiness, blockers, and next actions.
- [ ] Authority and writeback mappings agree; indexes do not create second strategy or evidence records.
- [ ] Relative links and paths in prompts, tables, and code examples resolve after an independent copy or directory merge.
- [ ] Scheduling status reflects the actual runner, not just a planned cadence.

Record the status below. Copying files alone does not complete business setup or imply publication or spending.

## Project setup status

- Status: Not started / Preparing / Ready (choose one during setup)
- Last verified: To fill in
- First-cycle plan path: To fill in
- Acceptance record: Link to the dated setup run, including verified tools, missing inputs, and scheduling state at that time.
- Current readiness, unresolved inputs, next action, and runner status: Maintain in [current context](context/current.md), not duplicated here.

This section is setup acceptance as of the recorded date. Ready does not mean every source is connected or an experiment has succeeded; the run must state the accepted scope and limitations.

## Ready-to-use AI prompt

> Set up this project for agent operation using growth/SETUP.md. Read existing materials, fill verifiable context, register available tools, and establish the operating agreement from my instructions. Ask only about critical gaps. Prepare the first plan and handoff, then perform already authorized preparation. Preserve existing decisions and distinguish planned schedules from installed jobs.
