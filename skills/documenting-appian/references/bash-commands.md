# Shell Commands — Bash & PowerShell

Batch commands for running the full pipeline and BPMN diagrams.

## Contents
- [All scripts (sequential) — Bash](#all-scripts-sequential)
- [BPMN diagrams (batch) — Bash](#bpmn-diagrams-batch--legend)
- [Single process model — Bash](#single-process-model)
- [PowerShell (Windows)](#powershell-windows)

---

## All scripts (sequential)

```bash
# Auto-detect scripts dir: set $base to wherever the skill is installed
# Common locations: .agents/skills/documenting-appian/scripts (Windsurf)
#                   .github/skills/documenting-appian/scripts (legacy)
base="$(find . -path '*/documenting-appian/scripts/build_uuid_index.py' -printf '%h' -quit 2>/dev/null)"
[ -z "$base" ] && { echo "Error: documenting-appian scripts not found"; exit 1; }

# Phase A: Build UUID index (MUST run first)
python "$base/build_uuid_index.py"

# Phase B: Inventory + complexity metrics
python "$base/generate_inventory.py"

# Phase C: Site navigation
python "$base/generate_navigation.py"

# Phase D: Data model + Integrations
python "$base/parse_cdts.py"
python "$base/extract_integrations.py"

# Phase E: Security
python "$base/extract_role_maps.py"

# Phase F: Translations + Deployment
python "$base/extract_translations.py"
python "$base/generate_deployment.py"

# Phase G: Health analysis (dead code + expression references)
python "$base/analyze_health.py"

# Phase G: Validate documentation quality
python "$base/validate_docs.py"

# Optional: compare two exports (after re-export)
# python "$base/diff_exports.py" docs/_uuid-index-baseline.json docs/_uuid-index.json
```

## BPMN diagrams (batch) + legend

```bash
script="$base/pm2mermaid.py"
dir="docs/process-models"
mkdir -p "$dir"
python "$script" --legend --dir "$dir"
for f in processModel/*.xml; do
  python "$script" "$f" --dir "$dir" --legend
done
```

## Single process model

```bash
python "$base/pm2mermaid.py" processModel/<uuid>.xml --dir docs/process-models
```

---

## PowerShell (Windows)

### All scripts (sequential)

```powershell
# Auto-detect scripts dir
$base = (Get-ChildItem -Recurse -Filter "build_uuid_index.py" -Path . | Where-Object { $_.FullName -match 'documenting-appian[\\/]scripts' } | Select-Object -First 1).DirectoryName
if (-not $base) { Write-Error "Error: documenting-appian scripts not found"; exit 1 }

# Phase A: Build UUID index (MUST run first)
python "$base/build_uuid_index.py"

# Phase B: Inventory + complexity metrics
python "$base/generate_inventory.py"

# Phase C: Site navigation
python "$base/generate_navigation.py"

# Phase D: Data model + Integrations
python "$base/parse_cdts.py"
python "$base/extract_integrations.py"

# Phase E: Security
python "$base/extract_role_maps.py"

# Phase F: Translations + Deployment
python "$base/extract_translations.py"
python "$base/generate_deployment.py"

# Phase G: Health analysis (dead code + expression references)
python "$base/analyze_health.py"

# Phase G: Validate documentation quality
python "$base/validate_docs.py"

# Optional: compare two exports (after re-export)
# python "$base/diff_exports.py" docs/_uuid-index-baseline.json docs/_uuid-index.json
```

### BPMN diagrams (batch) + legend

```powershell
$s = "$base/pm2mermaid.py"
New-Item -ItemType Directory -Force -Path docs/process-models | Out-Null
python $s --legend --dir docs/process-models
Get-ChildItem processModel/*.xml | ForEach-Object { python $s $_.FullName --dir docs/process-models --legend }
```

### Single process model

```powershell
python "$base/pm2mermaid.py" processModel/<uuid>.xml --dir docs/process-models
```
