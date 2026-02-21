# myllm: Antigravity Telegram Vibe-Coding Bridge

**myllm**은 텔레그램을 통해 **Antigravity Agent**와 **Gemini CLI**를 원격으로 제어하고, 프로젝트를 관리할 수 있게 해주는 개인용 AI 에이전트 오케스트레이션 시스템입니다.

## 🚀 Key Features

- **Dual-Agent Control**: 일반 시스템 작업은 `Gemini CLI`가, 심층 코드 분석 및 수정은 `Antigravity Agent`가 담당합니다.
- **Self-Evolution**: 시스템 에러 발생 시 실패 패턴을 분석하고 `CRITICAL_LOGIC.md`를 통해 스스로를 강화합니다.
- **Telegram Interface**: 언제 어디서나 메시지로 개발 작업을 지시하고 결과를 보고받을 수 있습니다.
- **System Vitals Monitoring**: 포트 8045 상태 및 워크스페이스 접근성을 실시간으로 체크합니다.

## 🛠 Project Structure

- `bridge.py`: 텔레그램 명령 수신 및 에이전트 라우팅 엔진.
- `evolution_manager.py`: 시스템 상태 진단 및 에러 기록, 자가 진화 로직 관리.
- `ag_api_server.py`: Antigravity 에이전트와 통신하는 FastAPI 서버.
- `run_bridge.ps1`: 시스템 초기화 및 브릿지 실행 스크립트.
- `docs/CRITICAL_LOGIC.md`: 시스템의 **Single Source of Truth (SSOT)** 문서.

## 📥 Installation & Setup

1. **Environment**: Windows 11 Native, Python 3.14, PowerShell 7.
2. **Requirements**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configuration**: `.env` 파일을 생성하고 아래 항목을 설정합니다.
   - `BOT_TOKEN`: 텔레그램 봇 토큰
   - `ALLOWED_CHAT_ID`: 허용된 사용자 ID
   - `DEFAULT_WORKSPACE_PATH`: 기본 작업 경로

## 🎮 Usage

- `/ag [메시지]`: Antigravity 에이전트에게 코드 작업 지시.
- `/ag reflect`: 시스템 실패 로그 분석 및 로직 최적화.
- `/ag status`: 에이전트 및 시스템 상태 확인.
- `[일반 텍스트]`: Gemini CLI를 이용한 빠른 시스템 명령 실행.

## 📜 Documentation

- [CRITICAL_LOGIC.md](docs/CRITICAL_LOGIC.md): 핵심 아키텍처 및 복구 규칙.
- [CONTEXT_SNAPSHOT.md](docs/CONTEXT_SNAPSHOT.md): 현재 프로젝트 상태 요약.
- [NEXT_STEPS.md](docs/NEXT_STEPS.md): 향후 개발 로드맵.
