Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LLM SE Agent - One-Click Install" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] Python ready: $(python --version)" -ForegroundColor Green

# Check Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "[ERROR] Git not found. Please install Git" -ForegroundColor Red
    exit 1
}
Write-Host "[2/4] Git ready" -ForegroundColor Green

# Clone repo (skip if already inside the project directory)
if (Test-Path "pyproject.toml") {
    Write-Host "[2/4] Already inside project directory, skipping clone" -ForegroundColor Green
} else {
    $repoDir = Join-Path (Get-Location) "LLM-"
    if (-not (Test-Path $repoDir)) {
        Write-Host "[2/4] Cloning repository..." -ForegroundColor Yellow
        git clone https://github.com/UserLiTanYu/LLM-.git
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Clone failed. Check network or proxy" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[2/4] Repository already exists, skipping clone" -ForegroundColor Yellow
    }
    Set-Location $repoDir
}

# Create venv
if (-not (Test-Path "venv")) {
    python -m venv venv
}
Write-Host "[4/4] Virtual environment ready" -ForegroundColor Green

# Activate
. .\venv\Scripts\Activate.ps1

# Install
pip install -e . -q
Write-Host "[DONE] se-agent installed" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Install complete! venv is active." -ForegroundColor Green
Write-Host ""
Write-Host "  Set API Key:"
Write-Host '    $env:DEEPSEEK_API_KEY = "sk-your-key"'
Write-Host ""
Write-Host "  Run:"
Write-Host "    se-agent --task generate --input requirements.md --output output/"
Write-Host "========================================" -ForegroundColor Cyan
