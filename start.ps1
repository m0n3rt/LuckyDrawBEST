Param(
    [switch]$NoBackend,
    [switch]$NoClient,
    [int]$Port = 8000,
    [string]$Python = "C:/Users/25703/AppData/Local/Programs/Python/Python312/python.exe"
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $MyInvocation.MyCommand.Path -Parent
Write-Host "[INFO] Root: $Root"

$VenvPath = Join-Path $Root '.venv'
$VenvPython = Join-Path $VenvPath 'Scripts/python.exe'

function Ensure-Venv {
    if (-not (Test-Path $VenvPython)) {
        Write-Host "[INFO] 创建虚拟环境 (.venv) 使用: $Python" -ForegroundColor Cyan
        & $Python -m venv $VenvPath
    } else {
        Write-Host "[INFO] 虚拟环境已存在" -ForegroundColor Green
    }
}

function Ensure-Dependencies {
    $Marker = Join-Path $VenvPath '.deps-installed'
    $ReqFile = Join-Path $Root 'backend/requirements.txt'
    if (-not (Test-Path $ReqFile)) {
        Write-Host "[WARN] 未找到后端依赖文件: $ReqFile" -ForegroundColor Yellow
        return
    }
    if (-not (Test-Path $Marker)) {
        Write-Host "[INFO] 安装依赖 ..." -ForegroundColor Cyan
        & $VenvPython -m pip install -r $ReqFile
        New-Item -ItemType File -Path $Marker -Force | Out-Null
    } else {
        Write-Host "[INFO] 跳过依赖安装 (已存在标记文件)" -ForegroundColor Green
    }
}

function Start-Backend {
    if ($NoBackend) { Write-Host "[INFO] 跳过后端启动"; return }
    Write-Host "[INFO] 启动后端 (端口: $Port)" -ForegroundColor Cyan
    Start-Process -FilePath $VenvPython -ArgumentList @('-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port',$Port,'--reload') -WorkingDirectory $Root -WindowStyle Normal
    Start-Sleep -Seconds 2
}

function Start-Client {
    if ($NoClient) { Write-Host "[INFO] 跳过客户端启动"; return }
    Write-Host "[INFO] 启动桌面客户端" -ForegroundColor Cyan
    Start-Process -FilePath $VenvPython -ArgumentList @('LuckyDrawBEST.py') -WorkingDirectory $Root -WindowStyle Normal
}

Write-Host "[STEP] 检查虚拟环境" -ForegroundColor Magenta
Ensure-Venv

Write-Host "[STEP] 安装依赖" -ForegroundColor Magenta
Ensure-Dependencies

Write-Host "[STEP] 启动服务" -ForegroundColor Magenta
Start-Backend
Start-Client

Write-Host "[DONE] 全部步骤完成。可访问 http://127.0.0.1:$Port/docs 查看后端。" -ForegroundColor Green
Write-Host "参数示例: powershell -ExecutionPolicy Bypass -File start.ps1 -NoClient" -ForegroundColor DarkGray