# documenting-skills

Collection of **AI skills** for IDE assistants. Compatible with **Windsurf (Cascade)** and **VS Code (GitHub Copilot)**.

- **Windsurf**: native installation as global skills (auto-triggered by context)
- **VS Code + Copilot**: usage via Custom Instructions and Prompt Files (`.github/copilot-instructions.md` and `.github/prompts/`)

---

## Prerequisites

| Requirement | Windsurf | VS Code + Copilot | Purpose |
|-------------|----------|-------------------|---------|
| [Windsurf](https://windsurf.com/) | Required | — | IDE with native skills |
| [VS Code](https://code.visualstudio.com/) | — | Required | IDE with Copilot |
| [GitHub Copilot](https://github.com/features/copilot) | — | Required | AI extension |
| [Node.js](https://nodejs.org/) ≥ 18 | Required | Optional | Skills CLI (`npx skills`) |
| [Git](https://git-scm.com/) ≥ 2.30 | Required | Required | Wiki publishing |
| [Python](https://www.python.org/) ≥ 3.8 | Optional | Optional | HTML export scripts |

> **Note**: Python is only required if you use `documenting-appian`, `documenting-paas`, or `wiki-html-publisher`.

---

## Installation on Windsurf

### Option A: Install with `npx skills` (recommended)

All skills can be installed directly using the repo URL:

```bash
# Custom skills (from this repo)
npx skills add cga-97/documenting-skills@documenting-appian -g -y
npx skills add cga-97/documenting-skills@documenting-paas -g -y
npx skills add cga-97/documenting-skills@evaluating-skills -g -y
npx skills add cga-97/documenting-skills@liquibase-process-script -g -y
npx skills add cga-97/documenting-skills@wiki-html-publisher -g -y

# Marketplace skills
npx skills add anthropics/courses@skill-creator -g -y
npx skills add anthropics/courses@find-skills -g -y
```

> **Install all at once** (full copy-paste):
> ```bash
> npx skills add cga-97/documenting-skills@documenting-appian cga-97/documenting-skills@documenting-paas cga-97/documenting-skills@evaluating-skills cga-97/documenting-skills@liquibase-process-script cga-97/documenting-skills@wiki-html-publisher anthropics/courses@skill-creator anthropics/courses@find-skills -g -y
> ```

Restart Windsurf to load the new skills.

### Option B: Automated script

```powershell
git clone https://github.com/cga-97/documenting-skills.git
cd documenting-skills
.\install.ps1
```

### Option C: Manual copy

If you prefer not to use `npx skills`, clone the repo and copy the folders:

```powershell
# Windows (PowerShell)
git clone https://github.com/cga-97/documenting-skills.git
$SKILLS_DIR = "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse -Force .\documenting-skills\skills\* "$SKILLS_DIR\"
```

```bash
# macOS / Linux
git clone https://github.com/cga-97/documenting-skills.git
cp -r ./documenting-skills/skills/* ~/.agents/skills/
```

Restart Windsurf after copying.

---

## Usage in VS Code with GitHub Copilot

If your version of VS Code / Copilot **does not support native skills** (agentskills.io), you can leverage the same knowledge through Copilot's native mechanisms:

### Mechanism 1: Custom Instructions (project-level)

Copilot Chat automatically reads `.github/copilot-instructions.md` from each repository. This is equivalent to having skills "always active" for that project.

#### How to use

1. Copy the `copilot/` folder from this repo to your project:

```powershell
# From your project root
Copy-Item -Recurse "<path-to-documenting-skills>\copilot\.github" ".\.github" -Force
```

2. This creates `.github/copilot-instructions.md` in your project with consolidated skill instructions.

3. Copilot Chat will read them automatically in every conversation.

> **Note**: Enable in VS Code: `Settings > GitHub Copilot > Chat > Code Generation: Instructions` → check `Use Instruction Files`.

### Mechanism 2: Prompt Files (reusable, per task)

Prompt Files are prompt templates you can invoke from Copilot Chat with `#`. They are the closest equivalent to an individual skill.

#### How to use

1. Copy the prompt files from this repo to your project:

```powershell
Copy-Item -Recurse "<path-to-documenting-skills>\copilot\.github\prompts" ".\.github\prompts" -Force
```

2. Enable the feature in VS Code:
   - `Settings > GitHub Copilot > Chat > Prompt Files` → **enabled**

3. In Copilot Chat, type `#` and select the prompt file you need:
   - `#document-project` → Generate technical documentation (equivalent to `documenting-paas`)
   - `#document-appian` → Document an Appian export (equivalent to `documenting-appian`)
   - `#liquibase-process` → Generate Liquibase DML script (equivalent to `liquibase-process-script`)
   - `#publish-wiki` → Publish Markdown to Wiki/HTML (equivalent to `wiki-html-publisher`)
   - `#audit-skill` → Audit an agent skill (equivalent to `evaluating-skills`)

### Mechanism 3: User-level instructions (global, all projects)

To have instructions active across **all** your projects without copying files:

1. Open VS Code Settings (`Ctrl+,`)
2. Search for `github.copilot.chat.codeGeneration.instructions`
3. Add entries pointing to local instruction files:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": "C:/Users/<your-user>/documenting-skills/copilot/instructions/documenting-paas.md" },
    { "file": "C:/Users/<your-user>/documenting-skills/copilot/instructions/liquibase-process.md" }
  ]
}
```

### Comparison: Windsurf Skills vs Copilot

| Concept | Windsurf (Cascade) | VS Code (GitHub Copilot) |
|---------|-------------------|--------------------------|
| Auto-triggered by context | `~/.agents/skills/SKILL.md` | `.github/copilot-instructions.md` |
| Individual skill on demand | Agent triggers automatically | Prompt File: `#prompt-name` |
| User-level instructions | `~/.agents/skills/` | `settings.json` → `codeGeneration.instructions` |
| Project-level instructions | `.windsurf/skills/` | `.github/copilot-instructions.md` |
| Helper scripts | `skills/<name>/scripts/` | Run manually or ask Copilot |
| Assets / templates | `skills/<name>/assets/` | Reference from prompt file |

---

## Skills Catalog

| # | Skill | Installation | Extra Requirements |
|---|-------|-------------|-------------------|
| 1 | [`documenting-appian`](#1-documenting-appian) | `npx skills add cga-97/documenting-skills@documenting-appian -g -y` | Python ≥ 3.8 |
| 2 | [`documenting-paas`](#2-documenting-paas) | `npx skills add cga-97/documenting-skills@documenting-paas -g -y` | Python 3.x + pip `markdown` |
| 3 | [`evaluating-skills`](#3-evaluating-skills) | `npx skills add cga-97/documenting-skills@evaluating-skills -g -y` | None |
| 4 | [`liquibase-process-script`](#4-liquibase-process-script) | `npx skills add cga-97/documenting-skills@liquibase-process-script -g -y` | None |
| 5 | [`wiki-html-publisher`](#5-wiki-html-publisher) | `npx skills add cga-97/documenting-skills@wiki-html-publisher -g -y` | Python 3.x + pip `markdown`, Git |
| 6 | [`find-skills`](#6-find-skills) | `npx skills add anthropics/courses@find-skills -g -y` | None |
| 7 | [`skill-creator`](#7-skill-creator) | `npx skills add anthropics/courses@skill-creator -g -y` | None |

---

## Usage Guide per Skill

### 1. documenting-appian

Generates comprehensive technical documentation for Appian applications from XML exports (`application_files/`).

**Triggers when you say:**
- _"Document this Appian application"_
- _"Generate the object inventory from the export"_
- _"Create BPMN diagrams for the process models"_
- _"Run a health check on the export"_
- _"Analyze dead code"_

**Example:**
```
Prompt: "Document the Appian project in application_files/"
```

**Output:** `docs/` folder with inventory, architecture, data model, integrations, security, deployment, health analysis, and Mermaid diagrams (BPMN, ER, sequence, state, C4, etc.).

---

### 2. documenting-paas

Generates technical documentation for enterprise projects (Java, Quarkus, Spring Boot, Kogito/BAMOE).

**Triggers when you say:**
- _"Document this project"_
- _"Generate the technical documentation"_
- _"Document the REST APIs"_
- _"Create architecture diagrams"_
- _"Document the BPMN process"_

**Example:**
```
Prompt: "Document the my-example-microservice microservice"
```

**Output:** Documentation in 7 phases: Discovery, Architecture, Data Model, Integrations, BPMN, Security/Deployment, and publishing (Wiki + HTML).

---

### 3. evaluating-skills

Audits any agent skill against the official agentskills.io specification.

**Triggers when you say:**
- _"Audit the documenting-paas skill"_
- _"Evaluate the quality of this skill"_
- _"Review the triggering of my skills"_
- _"Does this skill follow best practices?"_

**Example:**
```
Prompt: "Audit the documenting-appian skill"
```

**Output:** Structured report with findings by severity (frontmatter, body, scripts, triggering, evals) and a prioritized action plan.

---

### 4. liquibase-process-script

Generates Liquibase-formatted SQL DML scripts to register new processes in the `process_paas` schema.

**Triggers when you say:**
- _"Add a new process"_
- _"Generate the DML script for a process"_
- _"Create the insert script for MyProcess X"_

**Example:**
```
Prompt: "Add a new process called Invoice Management with entity INVM"
```

**Output:** File `src/main/resources/dml/NNN-insert-<entity>-<slug>.sql` with idempotent INSERTs and rollback.

---

### 5. wiki-html-publisher

Publishes Markdown documents to GitHub Wiki and generates standalone HTML files with rendered Mermaid diagrams.

**Triggers when you say:**
- _"Publish the documentation to the wiki"_
- _"Generate an HTML from this markdown"_
- _"Export the docs to HTML"_
- _"Push docs to GitHub Wiki"_

**Example:**
```
Prompt: "Publish docs/ARCHITECTURE.md to the repo wiki"
```

**Output:** GitHub Wiki page + standalone HTML file with rendered Mermaid.

---

### 6. find-skills

Discovers and searches skills from the open agentskills.io ecosystem.

**Triggers when you say:**
- _"Is there a skill for testing?"_
- _"Find a deployment skill"_
- _"How can I do X?"_ (if X might have a skill)

**Example:**
```
Prompt: "Find a skill for generating changelogs"
```

**Useful commands:**
```bash
npx skills find <query>      # Search for skills
npx skills add <package> -g  # Install globally
npx skills check             # Check for updates
npx skills update            # Update all
```

---

### 7. skill-creator

Guide for creating new skills that extend Cascade/Claude capabilities.

**Triggers when you say:**
- _"Create a new skill for X"_
- _"I want to make a skill that does Y"_
- _"Update this skill"_

**Example:**
```
Prompt: "Create a skill for generating integration tests automatically"
```

---

## Skill Structure

```
my-skill/
├── SKILL.md          # Main file (YAML frontmatter + Markdown instructions)
├── assets/           # Templates, configs, static files
├── scripts/          # Executable scripts (Python, Bash, PowerShell)
├── references/       # Reference documentation
└── evals/            # Test cases to validate the skill
```

The `SKILL.md` file has this structure:

```yaml
---
name: my-skill
description: >
  Description indicating when the skill should be triggered.
  Includes positive and negative triggers.
compatibility: "Environment requirements (e.g., Python 3.x)"
---

# Skill Title

## Step-by-step instructions
...
```

---

## FAQ

### Where are skills stored on my machine?

```
# Global (user-level)
~/.agents/skills/<skill-name>/

# Local (project-level) — alternative
<project>/.windsurf/skills/<skill-name>/
```

### How do I update skills?

```bash
# Update all installed skills
npx skills update

# Or reinstall a specific skill
npx skills add cga-97/documenting-skills@documenting-paas -g -y
```

### How do I create a new skill?

1. Ask Cascade: _"Create a new skill for X"_ (triggers `skill-creator`)
2. Or manually: `npx skills init my-new-skill`

### Can custom skills be published to agentskills.io?

Yes. Create a public GitHub repo with the skill structure and register it at [skills.sh](https://skills.sh/).

### Can I have project-local skills?

Yes. Create a `.windsurf/skills/<name>/SKILL.md` folder inside the project. It will only be active when you open that workspace.

### Do skills consume tokens?

Yes, the `SKILL.md` content is loaded into context when triggered. That's why skills should be concise (recommended < 500 lines).

---

## Contributing

1. Create a branch `feature/<skill-name>` or `fix/<skill-name>`
2. Add/modify the skill in `skills/`
3. Open a PR to `main`
4. Once merged, update with `npx skills update` or reinstalls the modified skill

---

## License

Marketplace skills (`find-skills`, `skill-creator`) have their own licenses.
