# run_bridge.ps1 (마스터 초기화: 유령 상태 해소 후 Launcher + Bridge 재구축)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ScriptDir "venv\Scripts\python.exe"
if (Test-Path $VenvPython) { $VENV_PYTHON = $VenvPython } else { $VENV_PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source; if (-not $VENV_PYTHON) { $VENV_PYTHON = "py"; $PY_ARG = "-3" } }
$AG_API = Join-Path $ScriptDir "ag_api_server.py"
$BRIDGE = Join-Path $ScriptDir "bridge.py"

# 1. 모든 Python 프로세스 강제 종료 (브리지, API 서버 초기화로 유령/409 해소)
taskkill /f /im python.exe /t 2>$null
# 2. 유령 상태 Antigravity 강제 종료 (새로 뜰 수 있도록)
taskkill /f /im Antigravity.exe /t 2>$null
Write-Host "모든 관련 프로세스를 초기화했습니다. 환경을 재구축합니다..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# 3. API 서버(8045) 백그라운드 기동
Write-Host "Antigravity Launcher 서버를 가동합니다..." -ForegroundColor Cyan
$apiArgs = if ($PY_ARG) { @($PY_ARG, $AG_API) } else { @($AG_API) }
Start-Process $VENV_PYTHON -ArgumentList $apiArgs -WindowStyle Hidden
Start-Sleep -Seconds 2

# 4. 텔레그램 브리지 실행
Write-Host "MyLLM Telegram Vibe Bridge를 실행합니다..." -ForegroundColor Green
if ($PY_ARG) { & $VENV_PYTHON $PY_ARG $BRIDGE } else { & $VENV_PYTHON $BRIDGE }
