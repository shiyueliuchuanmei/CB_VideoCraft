# VideoCraft 后端启动脚本
# 使用独立安装的 Python 3.11

$PYTHON_PATH = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
$PIP_PATH = "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts\pip.exe"
$WORKSPACE = "$env:USERPROFILE\.stepclaw\workspace\video-craft\backend"

Write-Host "🐍 Python路径: $PYTHON_PATH" -ForegroundColor Cyan
Write-Host "📦 pip路径: $PIP_PATH" -ForegroundColor Cyan
Write-Host "📁 工作目录: $WORKSPACE" -ForegroundColor Cyan
Write-Host ""

# 切换到后端目录
Set-Location $WORKSPACE

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "🔧 创建虚拟环境..." -ForegroundColor Yellow
    & $PYTHON_PATH -m venv .venv
}

# 激活虚拟环境
Write-Host "🚀 激活虚拟环境..." -ForegroundColor Green
& .venv\Scripts\Activate.ps1

# 检查依赖是否已安装
if (-not (Test-Path ".venv\Lib\site-packages\fastapi")) {
    Write-Host "📥 安装依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 初始化数据库（如果不存在）
if (-not (Test-Path "videocraft.db")) {
    Write-Host "🗄️ 初始化数据库..." -ForegroundColor Yellow
    python init_db.py
}

Write-Host ""
Write-Host "✅ 环境准备完成！" -ForegroundColor Green
Write-Host ""
Write-Host "启动命令:" -ForegroundColor Cyan
Write-Host "  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Write-Host ""

# 启动服务
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
