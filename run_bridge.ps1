# C:\develop\myllm\run_bridge.ps1
$VENV_PYTHON = "C:\develop\myllm\venv\Scripts\python.exe"

# 1. API 서버(8045)가 꺼져 있다면 백그라운드에서 실행
if (!(Get-NetTCPConnection -LocalPort 8045 -ErrorAction SilentlyContinue)) {
    Write-Host "🌐 API Wrapper 서버를 가동합니다..." -ForegroundColor Cyan
    Start-Process $VENV_PYTHON -ArgumentList "C:\develop\myllm\ag_api_server.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}
else {
    Write-Host "✅ API 서버(8045)가 이미 실행 중입니다." -ForegroundColor Green
}

# 2. 텔레그램 브리지 실행
Write-Host "🚀 Telegram Vibe Bridge를 실행합니다..." -ForegroundColor Green
& $VENV_PYTHON "C:\develop\myllm\bridge.py"
