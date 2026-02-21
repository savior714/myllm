# Antigravity Telegram Vibe-Coding Bridge - Critical Logic (SSOT)

## Project: myllm (AI Agent Orchestration System)

### 1. 아키텍처 원칙 (Architecture Principles)
- **이중화 제어 (Dual-Agent Control)**:
    - **Gemini CLI**: 일반 시스템 명령(파일 작업, 검색 등)을 담당.
    - **Antigravity Agent**: 심층 코드 작업, 프로젝트 전체 구조 분석/리팩토링 담당.
- **통신 규격 (Communication Standard)**:
    - 에이전트 제어는 **127.0.0.1:8045** API를 최우선으로 함.
    - **GUI 직접 간섭(SendKeys 등)은 절대 금지**하며, API와 CLI 플래그를 통한 연동을 원칙으로 함.

### 2. 실행 환경 및 보안 정책 (Execution & Security)
- **허용 경로 (Trusted Path)**: `C:\Users\savio`, `C:\develop`, `C:\obsidian` 폴더를 신뢰 작업 영역으로 간주.
- **환경 제약**: **Windows 11 Native** 전용. 모든 스크립트는 **PowerShell 7** 및 **Python 3.14**를 기준으로 작성.
- **보안**: 텔레그램 `ALLOWED_CHAT_ID` 화이트리스트 기반 인증.

### 3. 장애 복구 및 기동 로직 (Failure Recovery & Startup)
- **에이전트 매니저 기동**: Antigravity 실행 시 최신 워크스페이스를 유지하며 기동함.
- **연결 대기 (Polling)**: API 서버(8045 포트)가 활성화될 때까지 최대 **10초간 폴링(Polling) 대기 루프**를 수행함.
- **포커스 기반 유지 (Persistence)**: `/ag` 명령 시 기존 프로세스를 **절대 강제 종료하지 않음**. 대신 `AppActivate`를 통해 이미 실행 중인 인스턴스에 포커스를 주어 효율성과 작업 연속성을 보장함.

### 4. 핵심 구성 파일
- `ag_api_server.py`: Port 8045에서 동작하는 FastAPI 기반 에이전트 브릿지.
- `bridge.py`: 텔레그램 명령 수신 및 에이전트/CLI 라우팅 엔진.
- `ag_tools.ps1`: GUI 제어 및 기동 유틸리티.

### 5. 오류 진단 가이드 (Diagnostic Guide)
모든 로그는 `C:\develop\myllm\logs` 폴더에 집중됨.

| 현상 | 확인할 로그 파일 | 예상 원인 및 조치 |
| --- | --- | --- |
| **에이전트 응답 없음** | `bridge.log` | API 서버 타임아웃 또는 텔레그램 토큰 오류 |
| **GUI 기동/포커스 실패** | `powershell.log` | Antigravity 프로세스 감지 오류 또는 권한 제약 |
| **API 연결 실패 (-1)** | `api_server.log` | 8045 포트 점유 충돌 또는 가상환경 라이브러리 미설치 |
| **파일 접근 거부** | `bridge.log` | `config.toml` 내 `allowed_paths` 설정 누락 |

### 6. 장애 복구 및 자가 진화 규칙 (Self-Evolution Rules)
1. **진단 (Diagnostic)**: 오류 발생 시 `EvolutionManager.check_vitals()`를 호출하여 포트 8045 상태와 Antigravity 프로세스 생존 여부를 즉각 확인한다.
2. **기록 (Logging)**: 모든 `ModuleNotFoundError`, `SyntaxWarning`, 런타임 에러는 `logs/failure_db.json`에 구조화된 데이터(JSON)로 기록하여 사후 분석을 가능케 한다.
3. **학습 (Learning)**: 에이전트는 주기적으로 에러 패턴을 분석한다. 특히 Windows 경로 인식 오류 방지를 위해 코드 수정 시 항상 Raw String(`r""`) 접두사 사용을 습관화하여 지식 베이스를 자가 업데이트한다.
4. **회고 주기 (`/ag reflect`)**: 사용자의 요청이나 정기 세션을 통해 실패 로그를 분석하고 복구 로직을 `CRITICAL_LOGIC.md`에 영구 기록한다.
5. **백업 원칙**: 자가 수정 시 원본 파일의 백업(`.bak`)을 생성하여 복구 가능성을 유지함.

### 7. 장애 복구 및 충돌 관리 정책 (Self-Healing)

#### [Telegram API Conflict (HTTP 409)]
- **증상**: `telegram.error.Conflict` 발생 ( terminated by other getUpdates request )
- **원인**: 이전 브리지 세션이 정상적으로 종료되지 않았거나, 동일 토큰으로 다중 인스턴스가 실행됨.
- **처방**: `Get-CimInstance`를 통해 동일 명령행(`bridge.py`)을 가진 프로세스를 찾아 `Stop-Process`로 강제 종료 후 재시작.
- **예방**: `run_bridge.ps1` 실행 시 항상 프리플라이트 체크(Cleanup)를 수행하도록 규정함.

#### [System Vitals Check]
- `EvolutionManager.check_vitals()`를 통해 주기적으로 포트 8045 및 프로세스 상태를 모니터링함.
- `conflict_detected` 플래그가 참일 경우 자가 진화 루프(`reflect`)를 통해 자동 복구를 시도함.

### 8. 해결된 케이스 연구 (Resolved Case Studies)
* **[2026-02-21] Telegram 409 Conflict 해결**: 다중 인스턴스 충돌 시 자가 치유 부팅 시퀀스(`run_bridge.ps1`)와 `EvolutionManager`의 프로세스 검색을 통해 중복 실행을 자동으로 정리하도록 설계됨.
