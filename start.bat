@echo off
setlocal enabledelayedexpansion
REM 简易批处理：调用 PowerShell 脚本
SET SCRIPT=%~dp0start.ps1
if not exist "%SCRIPT%" (
  echo 未找到 start.ps1
  exit /b 1
)
powershell -ExecutionPolicy Bypass -File "%SCRIPT%" %*
endlocal