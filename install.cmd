@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   LLM SE Agent - 一键安装脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
echo [1/4] Python 已就绪

REM 检查 Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Git，请先安装 Git
    pause
    exit /b 1
)

REM 克隆仓库（如果不在项目目录内）
set REPO_DIR=LLM-
if not exist "%REPO_DIR%\" (
    echo [2/4] 克隆仓库...
    git clone https://github.com/UserLiTanYu/LLM-.git
    if errorlevel 1 (
        echo [错误] 克隆失败，请检查网络连接
        pause
        exit /b 1
    )
) else (
    echo [2/4] 仓库已存在，跳过克隆
)
cd /d "%REPO_DIR%"

REM 创建虚拟环境
if not exist "venv\" (
    python -m venv venv
    echo [3/4] 虚拟环境创建完成
) else (
    echo [3/4] 虚拟环境已存在，跳过
)

REM 激活并安装
call venv\Scripts\activate.bat
pip install -e . -q
echo [4/4] se-agent 安装完成

echo.
echo ========================================
echo   安装成功！
echo.
echo   使用前请设置 API Key：
echo     PowerShell: $env:DEEPSEEK_API_KEY = "sk-你的key"
echo     CMD:        set DEEPSEEK_API_KEY=sk-你的key
echo.
echo   然后运行：
echo     se-agent --task generate --input 需求.md --output output/
echo ========================================
pause
