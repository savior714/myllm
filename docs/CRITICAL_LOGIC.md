# Antigravity Telegram Vibe-Coding Bridge - Critical Logic (SSOT)

## Project: myllm

### 1. Architecture Principles
- **Dual-Agent**: Gemini CLI for system commands, Antigravity Agent for deep code work.
- **Launcher Mode**: Telegram bridge only acts as a GUI launcher via `--agent`. No direct prompt injection (API/CLI).
- **No GUI Automation**: `SendKeys` is strictly forbidden to prevent crashes.

### 2. Execution & Security
- **Paths**: `C:\Users\savio`, `C:\develop`, `C:\obsidian`
- **Env**: Windows 11 Native, PowerShell 7, Python 3.14
- **Security**: Telegram `ALLOWED_CHAT_ID` whitelist.

### 3. Process Management (Self-Healing)
- **GUI Protection**: `Antigravity.exe` is protected. Only `bridge.py` instances are killed during 409 Conflict.
- **Duplicate Prevention**: `ag_api_server.py` checks for existing GUI sessions via `psutil`.

### 4. Core Files
- `ag_api_server.py`: Port 8045 Launcher API.
- `bridge.py`: Telegram routing engine.
- `ag_tools.ps1`: GUI management script.
- `utils.py`: Reusable utilities (API, CLI).

### 5. Diagnostics & Recovery (`logs/`)
- Logs focus on `bridge.log` (Telegram) and `api_server.log` (Port 8045).
- **Self-Evolution (`/ag reflect`)**: Errors are saved to `failure_db.json`.
- **System Vitals**: `EvolutionManager` checks port 8045 and Antigravity process health to manage automatic recovery.

### 6. Communication Reliability
- **Message Slicing**: Error logs sent to Telegram must be truncated (e.g., max 1000 characters) to avoid the 4096 character limit (`BadRequest: Message is too long`).
- **CLI Routing Stability**: `utils.py`의 `run_gemini_cli`는 빈번한 네트워크 타임아웃(`GaxiosError`, `AbortError`)에 대비하여 **3회 재시도(Retry Loop) 및 지수 백오프/대기(2초)** 로직을 강제합니다.
