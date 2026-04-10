# VideoCraft 开发环境启动脚本 (Windows PowerShell)
# 一键启动前后端服务

Write-Host "🚀 启动 VideoCraft 开发环境..." -ForegroundColor Green

# 获取项目根目录
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

# 创建必要的目录
Write-Host "📁 创建必要的目录..."
New-Item -ItemType Directory -Path "$PROJECT_ROOT\backend\uploads" -Force | Out-Null
New-Item -ItemType Directory -Path "$PROJECT_ROOT\backend\logs" -Force | Out-Null

# 检查环境变量文件
if (-not (Test-Path "$PROJECT_ROOT\.env")) {
    Write-Host "⚠️  未找到 .env 文件，使用 .env.example 创建..." -ForegroundColor Yellow
    Copy-Item "$PROJECT_ROOT\.env.example" "$PROJECT_ROOT\.env"
    Write-Host "请编辑 .env 文件配置豆包 API Key" -ForegroundColor Yellow
}

# 启动后端
Write-Host "🔧 启动后端服务..." -ForegroundColor Cyan
Set-Location "$PROJECT_ROOT\backend"

# 创建虚拟环境（如果不存在）
if (-not (Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..."
    python -m venv venv
}

# 激活虚拟环境
& .\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装后端依赖..."
pip install -q -r requirements.txt

# 启动后端服务
Write-Host "启动后端服务 (http://localhost:8000)..."
$BACKEND_JOB = Start-Job -ScriptBlock {
    Set-Location $args[0]
    & .\venv\Scripts\Activate.ps1
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
} -ArgumentList "$PROJECT_ROOT\backend"

# 等待后端启动
Start-Sleep -Seconds 3

# 检查后端是否启动成功
if ($BACKEND_JOB.State -eq "Failed") {
    Write-Host "❌ 后端服务启动失败" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 后端服务已启动" -ForegroundColor Green

# 启动前端
Write-Host "🎨 启动前端服务..." -ForegroundColor Cyan
Set-Location "$PROJECT_ROOT\frontend"

# 安装依赖（如果 node_modules 不存在）
if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..."
    npm install
}

# 启动前端服务
Write-Host "启动前端服务 (http://localhost:5173)..."
$FRONTEND_JOB = Start-Job -ScriptBlock {
    Set-Location $args[0]
    npm run dev
} -ArgumentList "$PROJECT_ROOT\frontend"

# 等待前端启动
Start-Sleep -Seconds 5

# 检查前端是否启动成功
if ($FRONTEND_JOB.State -eq "Failed") {
    Write-Host "❌ 前端服务启动失败" -ForegroundColor Red
    Stop-Job $BACKEND_JOB
    exit 1
}

Write-Host "✅ 前端服务已启动" -ForegroundColor Green

# 输出访问信息
Write-Host ""
Write-Host "🎉 VideoCraft 开发环境启动成功！" -ForegroundColor Green
Write-Host ""
Write-Host "📱 前端地址: http://localhost:5173"
Write-Host "🔌 后端地址: http://localhost:8000"
Write-Host "📚 API 文档: http://localhost:8000/docs"
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Yellow

# 等待用户输入
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # 检查任务状态
        if ($BACKEND_JOB.State -eq "Failed") {
            Write-Host "后端服务异常退出" -ForegroundColor Red
            break
        }
        if ($FRONTEND_JOB.State -eq "Failed") {
            Write-Host "前端服务异常退出" -ForegroundColor Red
            break
        }
    }
}
finally {
    Write-Host "`n正在停止服务..." -ForegroundColor Yellow
    Stop-Job $BACKEND_JOB -ErrorAction SilentlyContinue
    Stop-Job $FRONTEND_JOB -ErrorAction SilentlyContinue
    Remove-Job $BACKEND_JOB -ErrorAction SilentlyContinue
    Remove-Job $FRONTEND_JOB -ErrorAction SilentlyContinue
    Write-Host "服务已停止" -ForegroundColor Green
}
