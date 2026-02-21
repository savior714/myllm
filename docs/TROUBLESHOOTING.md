# Troubleshooting Guide: myllm

## 1. Telegram Conflict (HTTP 409)
- **Symptom**: `telegram.error.Conflict` - bot unresponsive.
- **Fix**: Run `./run_bridge.ps1` to cleanly restart only the `bridge.py` instance without affecting Antigravity GUI.

## 2. API Connection Failure (Port 8045)
- **Symptom**: "API 서버 응답 대기 시간 초과".
- **Fix**: 
  1. Check if GUI started properly via `ag_tools.ps1`.
  2. Verify port with `netstat -ano | findstr :8045`.
  3. Retry `/ag load`.

## 3. Self-Evolution Loop
- **Symptom**: `/ag reflect` repeatedly tries to fix the same error.
- **Fix**: Manually review `CRITICAL_LOGIC.md` for contradictory rules or bugs.

## 4. Log Failure
- **Symptom**: `logs/` files not generating.
- **Fix**: Ensure `EvolutionManager` has proper write access to `C:\develop\myllm\logs`.
