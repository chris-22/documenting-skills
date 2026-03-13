<#
.SYNOPSIS
    Installs all global Windsurf skills (custom + marketplace).

.DESCRIPTION
    - Installs 5 custom skills via npx skills add (fallback: local copy)
    - Installs 2 marketplace skills with npx skills add
    - Requires: Node.js >= 18

.EXAMPLE
    .\install.ps1
#>

$ErrorActionPreference = "Stop"

# --- Configuration ---
$SKILLS_DIR = Join-Path $env:USERPROFILE ".agents\skills"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$REPO = "cga-97/documenting-skills"
$CUSTOM_SKILLS = @(
    "documenting-appian",
    "documenting-paas",
    "evaluating-skills",
    "liquibase-process-script",
    "wiki-html-publisher"
)
$MARKETPLACE_SKILLS = @(
    "anthropics/courses@skill-creator",
    "anthropics/courses@find-skills"
)
$ALL_SKILLS = $CUSTOM_SKILLS + @("skill-creator", "find-skills")

# --- Helper functions ---
function Write-Step($msg) {
    Write-Host "`n>> $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "   [OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "   [WARN] $msg" -ForegroundColor Yellow
}

# --- Check prerequisites ---
Write-Step "Checking prerequisites..."

try {
    $nodeVersion = & node --version 2>&1
    Write-Ok "Node.js $nodeVersion"
} catch {
    Write-Host "   [ERROR] Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

try {
    $gitVersion = & git --version 2>&1
    Write-Ok "Git $gitVersion"
} catch {
    Write-Warn "Git not found. Required for wiki-html-publisher."
}

try {
    $pythonVersion = & python --version 2>&1
    Write-Ok "Python $pythonVersion"
} catch {
    Write-Warn "Python not found. Required for HTML export scripts."
}

# --- Install custom skills via npx skills add ---
Write-Step "Installing custom skills via npx skills add..."

$npxFailed = @()
foreach ($skill in $CUSTOM_SKILLS) {
    try {
        Write-Host "   Installing $REPO@$skill..." -ForegroundColor Gray
        & npx skills add "$REPO@$skill" -g -y 2>&1 | Out-Null
        Write-Ok "$skill"
    } catch {
        Write-Warn "npx failed for $skill, using local copy..."
        $npxFailed += $skill
    }
}

# --- Fallback: copy skills that failed with npx ---
if ($npxFailed.Count -gt 0) {
    Write-Step "Copying skills that could not be installed with npx..."
    if (-not (Test-Path $SKILLS_DIR)) {
        New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null
    }
    foreach ($skill in $npxFailed) {
        $source = Join-Path $SCRIPT_DIR "skills\$skill"
        $destination = Join-Path $SKILLS_DIR $skill
        if (-not (Test-Path $source)) {
            Write-Warn "$source not found, skipping..."
            continue
        }
        if (Test-Path $destination) { Remove-Item -Recurse -Force $destination }
        Copy-Item -Recurse -Force $source $destination
        Write-Ok "$skill (local copy)"
    }
}

# --- Install marketplace skills ---
Write-Step "Installing marketplace skills..."

foreach ($skill in $MARKETPLACE_SKILLS) {
    try {
        Write-Host "   Installing $skill..." -ForegroundColor Gray
        & npx skills add $skill -g -y 2>&1 | Out-Null
        Write-Ok "$skill"
    } catch {
        Write-Warn "Could not install $skill. Try manually: npx skills add $skill -g -y"
    }
}

# --- Summary ---
Write-Step "Installation complete!"
Write-Host ""
Write-Host "Skills installed in: $SKILLS_DIR" -ForegroundColor White
Write-Host ""
Write-Host "Installed skills:" -ForegroundColor White
foreach ($skill in $ALL_SKILLS) {
    $check = if (Test-Path (Join-Path $SKILLS_DIR $skill)) { "[OK]" } else { "[MISSING]" }
    Write-Host "  $check $skill"
}
Write-Host ""
Write-Host ">> Restart Windsurf to load the new skills." -ForegroundColor Yellow
Write-Host ""
