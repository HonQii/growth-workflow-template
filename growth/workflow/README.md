# Workflow index

| Task | Start here | Expected output |
| --- | --- | --- |
| Execute a requested or scheduled run | [Agent operating loop](agent-loop.md) | Tool results, updated context, deliverables, and next action |
| Resume or consolidate context | `../context/current.md`, [agent loop](agent-loop.md) | Evidence-backed handoff |
| Execute or add an adapter | `../scripts/README.md` | Reproducible results with availability and coverage |
| Set up a project | `../context/project.md` | Product fact sources, resources, and critical gaps |
| Choose a goal and audience | `../context/strategy.md` | Testable hypotheses and selection rationale |
| Discover user problems or investigate product-improvement signals | [Problem discovery](problem-discovery.md), [source selection](channels.md#problem-discovery-sources) | Traceable task evidence, counterexamples, and bounded validation candidates |
| Assess data usability | [Metric definitions](metrics.md), `../context/baseline.md` | Definitions, validation status, and baseline |
| Start or adjust a channel | [Channel workflows](channels.md) | Path into the product, steps, deliverables, and observations |
| Plan and review a cycle | [Experiment cycle](cycle.md) | Experiment record, results, and next action |
| Save copy and public content | `../output/README.md` | Deliverables with supporting evidence and publication status |

Workflows define methods, `context/` holds project facts, and `output/` holds specific experiments and deliverables. Give each decision one authoritative location and reference it elsewhere.

Split channel instructions into separate files only when they need independent maintenance, then register them here. Do not create empty workflows for unused channels.
