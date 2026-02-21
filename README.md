# myllm: Antigravity Telegram Vibe-Coding Bridge

**myllm**은 텔레그램을 통해 **Antigravity Agent**와 **Gemini CLI**를 원격으로 제어하고, 프로젝트를 관리할 수 있게 해주는 개인용 AI 에이전트 오케스트레이션 시스템입니다.

## Key Features

- **Dual-Agent Control**: 일반 시스템 작업은 `Gemini CLI`가, 심층 코드 분석 및 수정은 `Antigravity Agent`가 담당합니다.
- **Self-Evolution**: 시스템 에러 발생 시 실패 패턴을 분석하고 `CRITICAL_LOGIC.md`를 통해 스스로를 강화합니다.
- **Telegram Interface**: 언제 어디서나 메시지로 개발 작업을 지시하고 결과를 보고받을 수 있습니다.
- **System Vitals Monitoring**: 포트 8045 상태 및 워크스페이스 접근성을 실시간으로 체크합니다.
- **Develop 폴더 기반 기동**: `C:\develop` 아래 폴더를 지정해 해당 경로에서 Antigravity를 기동할 수 있습니다.

## Project Structure

- `bridge.py`: 텔레그램 명령 수신 및 에이전트 라우팅 엔진.
- `evolution_manager.py`: 시스템 상태 진단 및 에러 기록, 자가 진화 로직 관리.
- `ag_api_server.py`: Antigravity 에이전트와 통신하는 FastAPI 서버(포트 8045).
- `run_bridge.ps1`: 마스터 초기화(기존 프로세스 종료 후 Launcher·브리지 재구축) 및 브릿지 실행.
- `docs/CRITICAL_LOGIC.md`: 시스템의 **Single Source of Truth (SSOT)** 문서.

## Installation & Setup

1. **Environment**: Windows 11 Native, Python 3.14, PowerShell 7.
2. **Requirements**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configuration**: `.env` 파일을 생성하고 아래 항목을 설정합니다.
   - `BOT_TOKEN`: 텔레그램 봇 토큰
   - `ALLOWED_CHAT_ID`: 허용된 사용자 ID
   - `DEFAULT_WORKSPACE_PATH`: 기본 작업 경로(미지정 시 Antigravity CWD 후보)
   - `AG_DEVELOP_ROOT`: develop 기반 경로 루트(미설정 시 `C:\develop`)
   - `AG_FOCUS_HOTKEY`: 입력창 포커스 단축키(기본 `^l`, Ctrl+L)

## Usage

- **`/ag [폴더명]`** 또는 **`/ag go`**: `AG_DEVELOP_ROOT\<폴더명>`(또는 마지막 사용 폴더)에서 Antigravity를 기동. 브리지가 해당 `path`를 API에 전달하여 CWD로 사용합니다.
- **`/ag [메시지]`**: Antigravity 에이전트에게 코드 작업 지시. 미션 파일(`AG_MISSION.md`) 생성 및 클립보드 트리거는 자동 주입 실패 시 fallback으로 동작합니다.
- **`/ag reflect`**: `logs/failure_db.json` 기반 실패 로그 분석 및 로직 최적화(회고 시 CWD는 브리지 프로젝트 루트).
- **`/ag status`**: 에이전트 및 시스템 상태 확인.
- **`[일반 텍스트]`**: Gemini CLI를 이용한 빠른 시스템 명령 실행.

## Documentation

- [CRITICAL_LOGIC.md](docs/CRITICAL_LOGIC.md): 핵심 아키텍처 및 복구 규칙(SSOT).
- [LATEST_CHANGES.md](docs/LATEST_CHANGES.md): 최신 변경점 정리.
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): 장애 대응 가이드.
- [CONTEXT_SNAPSHOT.md](docs/CONTEXT_SNAPSHOT.md): 현재 프로젝트 상태 요약.
- [NEXT_STEPS.md](docs/NEXT_STEPS.md): 향후 개발 로드맵.
- [SKILLS.md](docs/SKILLS.md): Cursor 스킬 출처 및 경로.
