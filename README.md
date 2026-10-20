# Growth Workflow Template

An agent-operated workspace for product growth: agents execute tools, evaluate evidence, run experiments, consolidate context, improve workflows, and produce deliverables. People set goals, constraints, and delegated authority. It does not prescribe an industry, platform, business model, or acquisition channel.

## Add it to an existing project

The initializer requires Python 3.9 or later and uses only the standard library. From this repository, run:

```bash
python3 scripts/init.py /absolute/path/to/your-project
```

The script copies only `growth/` into the target project. It excludes local configuration, data snapshots, credentials in the documented local paths, caches, and symlinks. It does not copy Git history, install dependencies, or fill in business facts. The target project must already exist; the script refuses to overwrite an existing `growth/` path.

Then open an AI coding assistant in the **target project** and ask:

> Initialize this project's growth workspace using growth/SETUP.md. Read existing materials first, fill in verifiable information, then ask about critical gaps that affect the first cycle. Preserve existing business decisions and prepare an actionable first plan.

[SETUP.md](growth/SETUP.md) establishes the agent operating agreement as well as the project context. People can review its inputs and decisions without executing routine commands themselves.

If the project already has a `growth/` directory, compare it with the template and merge missing fields or methods. Preserve existing strategy, experiments, and deliverables.

## Use it as a standalone growth repository

Maintainers can enable **Template repository** in the GitHub repository settings. After creating a separate repository with **Use this template**, configure the project directly using [SETUP.md](growth/SETUP.md). There is no need to run the copy script again.

If the product code lives in another repository, record its path or URL in the project context. Mark inaccessible sources as pending access.

## Structure

```text
growth/
├── README.md           Workspace entry point and file index
├── SETUP.md            Project setup, questions, and readiness checks
├── AGENTS.md           AI collaboration rules
├── template.json       Template source and version
├── context/            Durable memory, current handoff, strategy, and baselines
├── workflow/           Agent operating loop, channels, metrics, and experiments
├── scripts/            Agent CLI, SEO/ASO adapters, schemas, and source references
└── output/             Run records, experiments, and deliverables
scripts/init.py          Copy the template into an existing project
tests/                   Offline data contracts, copying, and overwrite protection
```

See the [workspace guide](growth/README.md) for file responsibilities. Unfilled fields are expected project inputs, not missing implementation.

## Agent operation

The agent resumes from [current context](growth/context/current.md), executes registered scripts or connected tools, assesses evidence, advances authorized tasks, and saves a run record. It periodically consolidates context and improves methods from evidence using [the operating loop](growth/workflow/agent-loop.md).

Collection, experiment review, context consolidation, and workflow improvement may have different cadences. Configure them in the project's operating agreement. An external agent runner provides scheduling; copying this repository does not install an automation.

The [agent data CLI](growth/scripts/README.md) includes configuration/access checks, Search Console queries, Apple Analytics and Google Play report retrieval/import, and compatible-period comparisons. Configuration and snapshots belong to each project. Adapters have offline validation; live account access must be verified in the consuming project. The agent executes them and uses their manifests for context summaries and workflow improvements.

Use the [credential setup guide](growth/scripts/credentials.md) for Search Console, Google Play, and Apple account steps. It separates the person's sign-in and account actions from the agent's local configuration and verification.

## Everyday use

In a project using this template, you can ask an AI assistant to:

- "Run the growth operating loop: collect due data with available tools, advance authorized work, update context, and record supported workflow improvements."
- "Review this experiment. Separate observed facts, possible explanations, and missing evidence."
- "Check whether this cycle's copy matches the product's actual capabilities and channel requirements."

Setup is not required for every cycle. Update the relevant files when capabilities, resources, or business goals change. Revisit the relevant SETUP steps when key assumptions change substantially.

## Versions and upgrades

The source and version are recorded in [growth/template.json](growth/template.json). After copying, the project maintains its own files; template changes do not sync automatically.

Compare the original and target versions, then selectively merge workflow improvements. Do not overwrite `context/`, existing experiments, or published content. Review project customizations before updating its version record. When releasing the template, update the version and date and describe migration impacts in the release notes.

The current content is a locally prepared `0.3.2`. The version file does not imply that a Git tag or GitHub Release has been created.

For upgrades from 0.2.0, merge `growth/scripts/`, `growth/config.example.json`, and `growth/.gitignore`; preserve existing project configuration and context. New adapters are disabled by default. The initializer now excludes local runtime files when copying.

For upgrades from 0.3.0, merge the updated CLI and authentication modules plus `growth/scripts/growth_data/environment.py` and `growth/.env.example`. Existing runner variables and JSON key identifiers remain supported; the optional project `.env` now loads automatically. Preserve existing `.env` and configuration files.

For upgrades from 0.3.1, add `growth/scripts/credentials.md` and merge the setup/index links. This documentation update does not change credential loading or require regenerating existing keys.

## Maintenance and validation

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

Keep reusable methods in the template repository. Product-specific information, accounts, exports, credentials, and experiment findings belong in the projects using it.
