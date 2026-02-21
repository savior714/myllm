# Context Snapshot: myllm

이 문서는 프로젝트 `myllm`의 현재 개발 상태와 기술적 맥락을 요약합니다.

## 🕒 Last Updated: 2026-02-21

## 🛠 Tech Stack
- **Runtime**: Python 3.14 (64-bit)
- **Framework**: FastAPI (for Agent API), python-telegram-bot
- **OS**: Windows 11 Native
- **Shell**: PowerShell 7 (pwsh)
- **Monitoring**: psutil, logging, RotatingFileHandler

## 🏗 Architecture Overview
프로젝트는 텔레그램을 통해 사용자의 명령을 수신하고, 이를 두 종류의 에이전트로 라우팅하는 브릿지 구조입니다.

1. **Routing Logic**: `bridge.py`에서 명령어를 분석하여 `/ag`는 Antigravity로, 일반 텍스트는 Gemini CLI로 보냅니다.
2. **Persistence & Recovery**: `EvolutionManager`가 PID 관리 및 포트 상태를 체크하여 중복 실행을 방지하고 프로세스 생존을 보장합니다.
3. **Failure Database**: 모든 중요한 런타임 에러는 `logs/failure_db.json`에 저장되어 향후 자가 회고(`/ag reflect`)에 사용됩니다.

## 📍 Key Modules
- **`bridge.py`**: 메인 루프. 텔레그램 API 연결 및 명령어 배분.
- **`evolution_manager.py`**: 시스템 자가 진단, 에러 기록, 프로세스 충돌 관리.
- **`ag_api_server.py`**: Antigravity 에이전트 인터페이스.
- **`ag_tools.ps1`**: Windows GUI 조작 및 워크스페이스 로드 유틸리티.

## 🔍 Current Focus
- 로그 관리 최적화 (RotatingFileHandler 도입 완료).
- 자가 진화 루프를 통한 시스템 안정성 확보.
- 텔레그램 409 Conflict 에러 자동 복구 로직 강화.
