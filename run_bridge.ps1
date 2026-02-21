# C:\develop\myllm\run_bridge.ps1
$VENV_PYTHON = "C:\develop\myllm\venv\Scripts\python.exe"

# 1. API 서버(8045)가 꺼져 있다면 백그라운드에서 실행
if (!(Get-NetTCPConnection -LocalPort 8045 -ErrorAction SilentlyContinue)) {
    Write-Host "🌐 Antigravity Launcher 서버를 가동합니다..." -ForegroundColor Cyan
    Start-Process $VENV_PYTHON -ArgumentList "C:\develop\myllm\ag_api_server.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}
else {
    Write-Host "✅ Launcher 서버(8045)가 이미 대기 중입니다." -ForegroundColor Green
}

# 2. 중복된 bridge.py 프로세스만 정밀 타격 (Antigravity는 제외)
Write-Host "🧹 기존 브리지 프로세스 점검 및 청소 중..." -ForegroundColor Yellow
$old_bridge = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' and CommandLine like '%bridge.py%'"
if ($old_bridge) {
    Write-Host "⚠️ 기존 브리지(Python)만 종료하고 재시작합니다." -ForegroundColor Yellow
    $old_bridge | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 1
}

# 3. 텔레그램 브리지 실행
Write-Host "🚀 MyLLM Telegram Vibe Bridge를 실행합니다..." -ForegroundColor Green
& $VENV_PYTHON "C:\develop\myllm\bridge.py"
