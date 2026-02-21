# Troubleshooting Guide: myllm

## 1. Telegram Conflict (HTTP 409)
- **Symptom**: `telegram.error.Conflict` - bot unresponsive.
- **Fix**: Run `./run_bridge.ps1` to cleanly restart only the `bridge.py` instance without affecting Antigravity GUI.

## 2. API Connection Failure (Port 8045)
- **Symptom**: "/ag 명령 무응답", "Antigravity-Manager(8045)가 실행 중이지 않습니다".
- **Cause**: 런처 서버(ag_api_server.py)가 기동되지 않음. `psutil` 미설치 시 서버가 즉시 종료될 수 있음.
- **Fix**:
  1. `pip install psutil fastapi uvicorn python-dotenv` 실행 후, `python ag_api_server.py`로 런처를 수동 기동.
  2. 터미널에 `Uvicorn running on http://127.0.0.1:8045` 확인.
  3. 포트 검증: `Test-NetConnection -ComputerName 127.0.0.1 -Port 8045` (TcpTestSucceeded : True 여야 함).
  4. 그 후 텔레그램에서 `/ag` 재시도.
- **Antigravity가 여전히 뜨지 않을 때**: `%USERPROFILE%\AppData\Local\Programs\Antigravity\Antigravity.exe` (또는 `...\bin\antigravity.exe`) 경로에 파일이 실제로 존재하는지 확인. 경로가 바뀌었으면 `.env` 또는 `ag_api_server.py`의 `AG_EXE`를 수정.

## 3. Self-Evolution Loop
- **Symptom**: `/ag reflect` repeatedly tries to fix the same error.
- **Fix**: Manually review `CRITICAL_LOGIC.md` for contradictory rules or bugs.

## 4. Log Failure
- **Symptom**: `logs/` files not generating.
- **Fix**: Ensure `EvolutionManager` has write access to the project `logs/` directory (script-directory relative).

## 5. Path not in workspace / 잘못된 폴더에서 Antigravity 기동
- **Symptom**: "Path not in workspace" 오류, 또는 Antigravity가 의도한 프로젝트가 아닌 다른 경로에서 열림.
- **Cause**: API에 전달되는 `path`(또는 `DEFAULT_WORKSPACE_PATH`)가 Cursor/에이전트 워크스페이스와 일치하지 않음. `/ag reflect` 등 자가 진단 시 CWD가 브리지 프로젝트 루트가 아님.
- **Fix**:
  1. `/ag <폴더명>` 사용 시 `AG_DEVELOP_ROOT`이 실제 develop 루트인지 확인(예: `C:\develop`). `.env`에 `AG_DEVELOP_ROOT=C:\develop` 설정.
  2. 단일 프로젝트만 쓸 경우 `.env`의 `DEFAULT_WORKSPACE_PATH`를 해당 프로젝트 절대 경로로 설정.
  3. 회고·진단은 브리지 스크립트 디렉터리 기준 상대 경로만 사용하므로, 브리지를 프로젝트 루트에서 실행했는지 확인.
