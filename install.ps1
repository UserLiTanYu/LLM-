Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LLM SE Agent - 一键安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[错误] 未找到 Python，请先安装 Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] Python 已就绪: $(python --version)" -ForegroundColor Green

# 检查 Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "[错误] 未找到 Git，请先安装 Git" -ForegroundColor Red
    exit 1
}
Write-Host "[2/4] Git 已就绪" -ForegroundColor Green

# 克隆仓库
$repoDir = Join-Path (Get-Location) "LLM-"
if (-not (Test-Path $repoDir)) {
    Write-Host "[3/4] 克隆仓库..." -ForegroundColor Yellow
    git clone https://github.com/UserLiTanYu/LLM-.git
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 克隆失败，请检查网络或代理" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[3/4] 仓库已存在，跳过克隆" -ForegroundColor Yellow
}

Set-Location $repoDir

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    python -m venv venv
}
Write-Host "[4/4] 虚拟环境已就绪" -ForegroundColor Green

# 激活
. .\venv\Scripts\Activate.ps1

# 安装
pip install -e . -q
Write-Host "[完成] se-agent 已安装" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装成功！当前 shell 已激活环境。" -ForegroundColor Green
Write-Host ""
Write-Host "  设置密钥："
Write-Host '    $env:DEEPSEEK_API_KEY = "sk-你的key"'
Write-Host ""
Write-Host "  运行："
Write-Host "    se-agent --task generate --input 需求.md --output output/"
Write-Host "========================================" -ForegroundColor Cyan
