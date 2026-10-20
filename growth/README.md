# Project growth workspace

Template version and source: [template.json](template.json)

This is an agent-operated workspace connecting project facts, growth hypotheses, tool execution, and experiment results. It supports different products and business models without prescribing channels, regions, languages, subscription models, or usage frequency.

## Operating model

People set goals, constraints, and delegation. Agents execute tools, assess evidence, advance authorized work, and maintain context, workflows, and outputs using [the agent loop](workflow/agent-loop.md). External agent tools trigger recurring runs; this directory does not schedule itself.

## Getting started

Start with [SETUP.md](SETUP.md) for the reading order, critical questions, first plan, and readiness checks. Complete the files in this order:

1. Fill in [project context](context/project.md), preferring references to existing materials. Mark unknowns as "To confirm." Missing budget or data does not mean a budget or value of zero.
2. Define the current goal, priority audience, and most important hypotheses in [growth strategy](context/strategy.md).
3. Complete [metric definitions](workflow/metrics.md) and the [evidence baseline](context/baseline.md). Distinguish available data, unverified collection, and unobservable steps.
4. Enable only the channels needed for this cycle in [channel workflows](workflow/channels.md), then follow the [experiment cycle](workflow/cycle.md).

Complete what can be verified first. If key facts are missing, the first action may be an interview, manual observation, obtaining data, or validating collection. Content production, advertising, and development are not mandatory starting points.

## File responsibilities

| File or directory | Contents | Update when |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | AI collaboration scope, evidence, and delivery rules | Collaboration constraints change |
| [SETUP.md](SETUP.md) | Project setup and readiness status | First setup or key assumptions change |
| [template.json](template.json) | Template source and version | A template upgrade has been merged |
| [context/current.md](context/current.md) | Compact current understanding and next-run handoff | After runs; consolidate at the agreed cadence |
| [workflow/agent-loop.md](workflow/agent-loop.md) | Agent execution, writeback, and method improvement | The operating method changes |
| [config.example.json](config.example.json) | Non-secret source configuration starter; copy locally before enabling sources | Source selection changes |
| [.env.example](.env.example) | Credential variable starter; copy to ignored `.env` and keep key files external | Authentication requirements change |
| [.gitignore](.gitignore) | Copied exclusions for configuration, evidence, credentials and runtime files | Local storage conventions change |
| [scripts/data.py](scripts/data.py) | Agent CLI for doctor, fetch, import and compare | Executable capabilities change |
| [scripts/growth_data/](scripts/growth_data/) | Transport, authentication, source adapters, parsers and comparisons | Data contracts change |
| [scripts/requirements.txt](scripts/requirements.txt) | Optional authentication dependencies | Supported dependency versions change |
| [scripts/credentials.md](scripts/credentials.md) | Credential acquisition, permissions, configuration and guided validation | Account setup or provider authorization steps change |
| [scripts/sources.md](scripts/sources.md) | Official contracts, limits and live acceptance criteria | Provider behavior or validation changes |
| [scripts/README.md](scripts/README.md) | Tool registry, availability, and adapter contract | Tools or access change |
| [context/project.md](context/project.md) | Project, resources, product sources, publication and content constraints | Capabilities, resources, markets, or sources change |
| [context/strategy.md](context/strategy.md) | Audience, value proposition, business hypotheses, current goal, and change criteria | Strategic decisions change |
| [context/baseline.md](context/baseline.md) | Dated data snapshots with scope and sources | New data becomes available; append a snapshot |
| [workflow/README.md](workflow/README.md) | Task-based workflow index | Workflows are added or removed |
| [workflow/cycle.md](workflow/cycle.md) | Hypothesis, execution, observation, review, and next decision | The method changes |
| [workflow/metrics.md](workflow/metrics.md) | Business metrics mapped to data sources | Definitions, collection, or validation status change |
| [workflow/channels.md](workflow/channels.md) | Selected channels, execution steps, and paths into the product | Channel status, steps, or platform requirements change |
| [output/README.md](output/README.md) | Storage rules for experiments, copy, reviews, and raw data | Delivery conventions change |

Product specifications, code, prices, and release status come from the sources listed in `context/project.md`. Record growth decisions here without creating a second product specification. Maintain published content only in its authoritative location.

## Everyday use

Start from `context/current.md` and follow `workflow/agent-loop.md`. Run registered tools directly, record actual results, and leave a durable handoff. Improve workflow steps only when evidence supports the change. The included data CLI supports SEO/ASO retrieval, report import, and comparisons; consult the tool registry and verify configured project access before execution.

Run only the investigations that available resources support. Each review should answer what is known, what remains unknown, and what is most useful to do next. Return use, revenue, and referrals can be observed in parallel; products need not follow one universal funnel.

Register new files in this table or the relevant workflow index. Maintain current rules in place. Append historical experiment results and retain the original hypothesis; do not present thresholds chosen afterward as decisions made in advance.

## Copying and upgrades

Copy this entire directory into another project as `growth/`. Keep only relevant fields. Unused channels do not need files.

Each project maintains its own copy. Review template differences and adopt relevant improvements without overwriting project facts, experiment records, or published deliverables. Merge into an existing `growth/` directory selectively rather than replacing it.
