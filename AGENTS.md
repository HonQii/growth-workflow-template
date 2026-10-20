# Template maintenance rules

This repository maintains a reusable growth workflow. Read README.md first and distinguish template maintenance from growth work for a specific project.

- Keep industry, region, language, business model, channels, tools, and paths configurable when changing shared methods.
- Do not fill the template with the maintainer's product data, credentials, strategy, or release status.
- `growth/SETUP.md` is copied with the template. Project setup and execution rules are in `growth/AGENTS.md`.
- When the user explicitly asks to configure a specific project in a standalone repository created from this template, fill in that project's context. Source-template maintenance rules must not block authorized project setup.
- The initializer only copies files. It must refuse to overwrite an existing growth directory or symbolic link. Do not modify the target project's root AGENTS.md, Git configuration, or existing files.
- Run `python3 -m unittest discover -s tests -v` after changes to copying behavior. For documentation changes, check relative links and usability after an independent copy.
- Register new template files in growth/README.md. Update growth/template.json when changing the template version.
