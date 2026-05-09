@echo off
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
echo [1/3] Python 已就绪

REM 创建虚拟环境
if not exist "venv\" (
    python -m venv venv
    echo [2/3] 虚拟环境创建完成
) else (
    echo [2/3] 虚拟环境已存在，跳过
)

REM 激活并安装
call venv\Scripts\activate.bat
pip install -e . -q
echo [3/3] se-agent 安装完成

echo.
echo ========================================
echo   安装成功！
echo.
echo   使用前请设置 API Key：
echo     $env:DEEPSEEK_API_KEY = "sk-你的key"
echo.
echo   然后运行：
echo     se-agent --task generate --input 需求.md --output output/
echo ========================================
