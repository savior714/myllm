# Antigravity Telegram Vibe-Coding Bridge - Critical Logic (SSOT)

## Project: myllm

### 1. Architecture Principles
- **Dual-Agent**: Gemini CLI for system commands, Antigravity Agent for deep code work.
- **Launcher Mode**: Telegram bridge only acts as a GUI launcher via `--agent`. No direct prompt injection (API/CLI).
- **No GUI Automation**: `SendKeys` is strictly forbidden to prevent crashes.
- **Minimum Trigger (미션 파일 + 클립보드)**: 지시가 자동 주입되지 않을 때, 브리지는 `AG_MISSION.md`를 생성하고 클립보드에 트리거 문구를 복사한다. fallback 시에만 사용자에게 Ctrl+V 안내.
- **원격 우선주의**: 사용자 수동 개입을 요구하는 응답(예: "붙여넣기 하세요")은 장애로 간주한다. **Zero-Touch 주입**: 검증된 시퀀스는 **{ESC} -> AG_FOCUS_HOTKEY(^l) -> ^v -> {ENTER}**. ESC로 포커스 초기화 후 Ctrl+L로 입력창 점유. 기본 `^l`은 `AG_FOCUS_HOTKEY`로 변경 가능.
- **§1.1 Temporary Exception for Pipeline Verification (PoC)**: When the environment variable `FORCE_INJECT_POC=1` is set, `SendKeys`-based command injection is **exceptionally** allowed for E2E pipeline validation only. Purpose: verify that the Antigravity IDE + Telegram bridge pipeline can deliver a zero-touch command. After verification, remove the flag and restore strict isolation. Managed via `ag_api_server.py` only when the flag is set.

### 2. Execution & Security
- **Paths**: `C:\Users\savio`, `C:\develop`, `C:\obsidian`
- **Env**: Windows 11 Native, PowerShell 7, Python 3.14
- **Security**: Telegram `ALLOWED_CHAT_ID` whitelist.
- **Develop 폴더 기반 기동**: 사용자가 "develop 아래 폴더 목록 알려줘" 등으로 워크스페이스 후보를 확인한 뒤, **`/ag <폴더명>`** 또는 **`/ag go`** 로 해당 폴더에서 Antigravity를 기동한다. 브리지는 `path`를 API에 전달하며, 기본 루트는 **`AG_DEVELOP_ROOT`**(미설정 시 `C:\develop`)이다. 즉 `path = AG_DEVELOP_ROOT\<폴더명>`(예: `C:\develop\myllm-1`). API(`ag_api_server.py`)는 이 `path`를 Antigravity 프로세스의 **CWD**로 사용한다.

### 3. Process Management (실행 보장 및 Conflict 해소)
- **실행 보장 정책**: `port_8045`가 true여도 실제 앱 기동에 실패하면 프로세스 리스트를 신뢰하지 말고, **OS 레벨 강제 재시작**을 수행한다. 런처(`ag_api_server.py`)는 "이미 실행 중" 체크 없이 **항상 기동 명령을 전달**하여 유령 상태(거짓 양성)를 방지한다.
- **Conflict 자동 해소**: 텔레그램 409 에러 감지 시 `bridge.py`는 스스로 종료하고, `run_bridge.ps1`에 의해 재실행되어 재로그인되도록 유도한다.
- **마스터 초기화**: `run_bridge.ps1` 실행 시 기존 `python.exe` 및 `Antigravity.exe`를 강제 종료한 뒤 Launcher(8045)와 브리지를 깨끗하게 재구축한다.

### 4. Core Files
- `ag_api_server.py`: Port 8045 Launcher API.
- `bridge.py`: Telegram routing engine.
- `ag_tools.ps1`: GUI management script.
- `utils.py`: Reusable utilities (API, CLI).

### 5. Diagnostics & Recovery (`logs/`)
- Logs focus on `bridge.log` (Telegram) and `api_server.log` (Port 8045). 브리지 재시작 시 `bridge.log`는 초기화되고, `failure_db.json`은 `[]`로 리셋되어 회고 과적을 방지한다.
- **Self-Evolution (`/ag reflect`)**: Errors are saved to `failure_db.json`. 회고 시 CWD는 브리지 프로젝트 루트(`_script_dir`)로 고정, 상대 경로만 사용. 회고 입력은 `failure_db` 내용을 stdin으로 Gemini CLI에 전달한다.
- **System Vitals**: `EvolutionManager` checks port 8045 and Antigravity process health to manage automatic recovery.
- **경로 관리 원칙**: (1) 자가 진단·도구 실행은 프로젝트 루트(CWD) 기준, 절대 경로 지양. (2) GUI 주입 실패 시 클립보드 Fallback 즉시 활성화. (3) "Path not in workspace"는 치명적 구성 오류로 분류, CWD 재설정.

### 6. Communication Reliability
- **Message Slicing**: Error logs sent to Telegram must be truncated (e.g., max 1000 characters) to avoid the 4096 character limit (`BadRequest: Message is too long`).
- **CLI Routing Stability**: `utils.py`의 `run_gemini_cli`는 빈번한 네트워크 타임아웃(`GaxiosError`, `AbortError`)에 대비하여 **3회 재시도(Retry Loop) 및 지수 백오프/대기(2초)** 로직을 강제합니다.
