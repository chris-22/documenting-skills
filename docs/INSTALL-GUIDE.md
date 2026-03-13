# Step-by-Step Installation Guide

Detailed guide for setting up skills in **Windsurf** or **VS Code with GitHub Copilot**.

> **Which IDE am I using?**
> - **Windsurf**: Follow sections 1–7 (native skill installation)
> - **VS Code + Copilot**: Jump directly to [section 8](#8-setup-in-vs-code-with-github-copilot)

---

## 1. Check prerequisites

Open a terminal (PowerShell on Windows, Terminal on macOS/Linux) and run:

```bash
# Check Node.js (required for npx skills)
node --version
# Expected: v18.x.x or higher

# Check Git
git --version

# Check Python (optional, for HTML export scripts)
python --version
# Expected: 3.8+
```

If you don't have Node.js, download it from [nodejs.org](https://nodejs.org/).

---

## 2. Install skills with `npx skills` (recommended)

All skills can be installed directly from this repo:

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

---

## 3. Alternative: Automated script

If you prefer to use the installer script:

```powershell
# Windows (PowerShell)
git clone https://github.com/cga-97/documenting-skills.git
cd documenting-skills
.\install.ps1
```

---

## 4. Alternative: Manual copy

If you can't use `npx skills`:

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

---

## 5. Verify installation

### List installed skills

```powershell
# Windows
Get-ChildItem "$env:USERPROFILE\.agents\skills" | Select-Object Name
```

```bash
# macOS / Linux
ls ~/.agents/skills/
```

You should see 7 folders:

```
documenting-appian/
documenting-paas/
evaluating-skills/
find-skills/
liquibase-process-script/
skill-creator/
wiki-html-publisher/
```

### Test in Windsurf

1. **Restart Windsurf** (close and reopen)
2. Open Cascade (chat panel)
3. Type: _"What skills do you have available?"_
4. Cascade should mention the installed skills in its response

---

## 6. Update skills

```bash
# Update all installed skills
npx skills update

# Or reinstall a specific skill
npx skills add cga-97/documenting-skills@documenting-paas -g -y
```

---

## 7. Uninstall a skill

```bash
# Remove a skill with npx
npx skills remove <skill-name>
```

Or manually delete its folder:

```powershell
# Windows
Remove-Item -Recurse "$env:USERPROFILE\.agents\skills\<skill-name>"
```

```bash
# macOS / Linux
rm -rf ~/.agents/skills/<skill-name>
```

Restart Windsurf after removing.

---

## Troubleshooting (Windsurf)

| Problem | Solution |
|---------|----------|
| `npx skills` not working | Verify Node.js ≥ 18 is installed: `node --version` |
| Skill not showing in Cascade | Restart Windsurf. Verify the folder is in `~/.agents/skills/` |
| Python error in scripts | Install Python 3.8+ and the package: `pip install markdown` |
| Permission denied (Windows) | Run PowerShell as administrator |
| Permission denied (Linux/macOS) | Use `chmod +x install.sh` before running |

---

## 8. Setup in VS Code with GitHub Copilot

If your version of VS Code or Copilot **does not support native skills** (agentskills.io), you can use the same knowledge through Copilot's native mechanisms: **Custom Instructions** and **Prompt Files**.

### 8a. Prerequisites (Copilot)

1. **VS Code** installed (recent version)
2. **GitHub Copilot** extension installed with active license
3. **GitHub Copilot Chat** extension installed

Verify in VS Code: `Extensions` (`Ctrl+Shift+X`) → search "GitHub Copilot".

### 8b. Enable Custom Instructions in VS Code

1. Open `Settings` (`Ctrl+,`)
2. Search: `copilot instructions`
3. Check **"Code Generation: Use Instruction Files"** (make sure it's enabled)

This allows Copilot Chat to automatically read `.github/copilot-instructions.md` from any project.

### 8c. Enable Prompt Files in VS Code

1. Open `Settings` (`Ctrl+,`)
2. Search: `copilot prompt files`
3. Set **"Chat: Prompt Files"** to **enabled**

This allows invoking prompt files from Copilot Chat by typing `#`.

### 8d. Option 1: Project-level setup

Copy the Copilot files from this repo to your project:

```powershell
# From your project root (PowerShell)
$REPO = "C:\Users\<your-user>\Desktop\documenting-skills"

# Copy copilot-instructions.md (project-level instructions)
New-Item -ItemType Directory -Force -Path ".\.github\prompts" | Out-Null
Copy-Item "$REPO\copilot\.github\copilot-instructions.md" ".\.github\copilot-instructions.md" -Force

# Copy prompt files (individual skills invokable with #)
Copy-Item -Recurse -Force "$REPO\copilot\.github\prompts\*" ".\.github\prompts\"
```

```bash
# From your project root (Bash)
REPO="$HOME/Desktop/documenting-skills"

mkdir -p .github/prompts
cp "$REPO/copilot/.github/copilot-instructions.md" .github/copilot-instructions.md
cp "$REPO"/copilot/.github/prompts/*.prompt.md .github/prompts/
```

Result in your project:

```
your-project/
├── .github/
│   ├── copilot-instructions.md        # Auto-loaded instructions for Copilot
│   └── prompts/
│       ├── document-project.prompt.md  # #document-project
│       ├── document-appian.prompt.md   # #document-appian
│       ├── liquibase-process.prompt.md # #liquibase-process
│       ├── publish-wiki.prompt.md      # #publish-wiki
│       └── audit-skill.prompt.md       # #audit-skill
```

### 8e. Option 2: User-level setup (global)

To have instructions active across **all** your projects:

1. Open VS Code Settings JSON (`Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)")
2. Add:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": "C:/Users/<your-user>/Desktop/documenting-skills/copilot/instructions/documenting-paas.md" },
    { "file": "C:/Users/<your-user>/Desktop/documenting-skills/copilot/instructions/liquibase-process.md" }
  ]
}
```

> Adjust the path according to where you cloned this repo.

### 8f. How to use Prompt Files

Once copied to your project, in **Copilot Chat** (`Ctrl+Shift+I` or side panel):

1. Type `#` in the chat
2. A list of available prompt files will appear:
   - **`#document-project`** → Generate technical documentation for the project
   - **`#document-appian`** → Document an Appian export
   - **`#liquibase-process`** → Generate Liquibase DML script
   - **`#publish-wiki`** → Publish Markdown to Wiki/HTML
   - **`#audit-skill`** → Audit an agent skill
3. Select one and add your message, for example:

```
#document-project Document this microservice
```

### 8g. Verify it works

1. Open a project that has `.github/copilot-instructions.md`
2. Open Copilot Chat
3. Type: `What custom instructions do you have for this project?`
4. Copilot should mention the conventions defined in the file

---

## Troubleshooting (Copilot)

| Problem | Solution |
|---------|----------|
| Prompt files don't appear with `#` | Verify `Chat: Prompt Files` is **enabled** in Settings |
| Copilot doesn't read `copilot-instructions.md` | Verify it's in `.github/copilot-instructions.md` (not another folder) and "Use Instruction Files" is enabled |
| `#` doesn't show options | Make sure you have the latest version of the Copilot Chat extension |
| Global instructions don't apply | Verify the path in `settings.json` — must be absolute with `/` (not `\`) |
