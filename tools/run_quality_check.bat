@echo off
setlocal
pushd "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_quality_check.ps1" %*
set "exit_code=%ERRORLEVEL%"
popd
exit /b %exit_code%
