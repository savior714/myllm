# Context Snapshot: myllm

이 문서는 프로젝트 `myllm`의 현재 개발 상태와 기술적 맥락을 요약합니다.

## Last Updated: 2026-02-21

## Tech Stack
- **Runtime**: Python 3.14 (64-bit)
- **Framework**: FastAPI (for Agent API), python-telegram-bot
- **OS**: Windows 11 Native
- **Shell**: PowerShell 7 (pwsh)
- **Monitoring**: psutil, logging, RotatingFileHandler

## Architecture Overview
프로젝트는 텔레그램을 통해 사용자의 명령을 수신하고, 이를 두 종류의 에이전트로 라우팅하는 브릿지 구조입니다.

1. **Routing Logic**: `bridge.py`에서 명령어를 분석하여 `/ag`는 Antigravity로, 일반 텍스트는 Gemini CLI로 보냅니다. `/ag <폴더명>` 또는 `/ag go` 시 `AG_DEVELOP_ROOT\<폴더명>`을 API에 `path`로 전달하여 해당 경로를 Antigravity CWD로 사용합니다.
2. **Zero-Touch / Fallback**: 지시 주입은 ESC → 포커스 단축키(기본 Ctrl+L) → 붙여넣기 → Enter 시퀀스로 검증. 실패 시 `AG_MISSION.md` 생성 및 클립보드 트리거, 필요 시 사용자에게 Ctrl+V 안내.
3. **Persistence & Recovery**: `EvolutionManager`가 포트 8045 및 Antigravity 프로세스 상태를 체크. `run_bridge.ps1` 마스터 초기화 시 기존 프로세스 종료 후 Launcher·브리지 재구축.
4. **Failure Database**: 런타임 에러는 `logs/failure_db.json`에 저장. `/ag reflect` 시 해당 내용을 stdin으로 Gemini에 전달해 회고. 브리지 재시작 시 `failure_db`는 `[]`로 리셋됩니다.

## Key Modules
- **`bridge.py`**: 메인 루프. 텔레그램 API 연결, 명령어 배분, path 전달 및 미션·클립보드 fallback.
- **`evolution_manager.py`**: 시스템 자가 진단, 에러 기록, 프로세스 충돌 관리.
- **`ag_api_server.py`**: Port 8045 Launcher API. `path` 수신 후 Antigravity를 해당 CWD로 기동.
- **`ag_tools.ps1`**: Windows GUI 조작 및 워크스페이스 로드 유틸리티.

## Current Focus
- 로그 관리 최적화 (RotatingFileHandler, 재시작 시 bridge.log 초기화·WARNING 이상만 파일 기록).
- 자가 진화 루프 안정화 (failure_db 리셋 정책, reflect 시 CWD·stdin 규칙).
- Develop 폴더 기반 기동 및 path 전달 흐름 문서화.
