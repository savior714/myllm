# 최신 변경점 정리 (myllm)

**기준일:** 2026-02-21  
**브랜치:** main (origin/main과 동기화, working tree clean)

---

## 1. 커밋 히스토리 요약

| 커밋 | 날짜 | 제목 |
|------|------|------|
| `a4cb247` | 2026-02-21 18:32 | Refactor bridge.py and enhance self-evolution with retry logic |
| `1b5ea5a` | 2026-02-21 18:00 | docs: 프로젝트 문서 추가 (README, CONTEXT_SNAPSHOT, NEXT_STEPS, TROUBLESHOOTING) |
| `a3b8937` | 2026-02-21 16:59 | Initial commit (Security Purge) |

---

## 2. 커밋별 변경 요약

### 2.1 a4cb247 – Refactor bridge.py and enhance self-evolution with retry logic

**목적:** 브릿지 리팩터링 및 CLI 재시도/자가 진화 강화.

**주요 변경:**
- **bridge.py**: 로직 정리, 재시도 및 복구 흐름 보강.
- **ag_api_server.py**: 66줄 수준 변경 (API/에이전트 연동 정비).
- **evolution_manager.py**: 67줄 수준 변경 (자가 진화·진단 로직 강화).
- **utils.py**: **3회 재시도 + 지수 백오프(2초)** 로직 추가 – `run_gemini_cli` 네트워크 타임아웃 대응.
- **docs/CRITICAL_LOGIC.md**: SSOT 반영 – CLI 재시도 정책, 메시지 슬라이싱, Self-Evolution(`/ag reflect`), System Vitals 등 명시.
- **docs/TROUBLESHOOTING.md**: 55줄 수준 보강.
- **run_bridge.ps1**: 17줄 수준 수정 (실행/초기화 흐름).
- **ag_tools.ps1**: 5줄 추가.
- **bridge.log**: 로그 파일 비우기(5134줄 삭제) – 로그 정리.
- **logs/failure_db.json**: 신규 – 실패 기록 DB (자가 회고용).

**결과:** CLI 안정성 향상, 자가 진화 및 장애 대응 로직이 SSOT와 문서에 반영됨.

---

### 2.2 1b5ea5a – docs: 프로젝트 문서 추가

**목적:** 프로젝트 문서 체계 구축.

**추가/수정 문서:**
- **README.md**: 프로젝트 소개, 기능, 구조, 설치, 사용법, 문서 링크.
- **docs/CONTEXT_SNAPSHOT.md**: Tech Stack, 아키텍처 개요, 핵심 모듈, 현재 포커스.
- **docs/NEXT_STEPS.md**: Immediate Tasks, Technical Debt, Future Ideas.
- **docs/TROUBLESHOOTING.md**: 초기 트러블슈팅 가이드.
- **docs/CRITICAL_LOGIC.md**: 16줄 추가 – SSOT 보강.

**결과:** 온보딩 및 유지보수용 문서 기반 마련.

---

### 2.3 a3b8937 – Initial commit (Security Purge)

**목적:** 민감 정보 제거 후 초기 코드베이스 커밋.

**포함 항목:**
- `.gemini/config.toml`, `.gemini/settings.json` – Gemini 설정.
- `.gitignore`, `.vscode/launch.json` – 개발 환경.
- **ag_api_server.py**, **bridge.py**, **evolution_manager.py** – 코어 모듈.
- **run_bridge.ps1**, **ag_tools.ps1** – 실행/도구 스크립트.
- **docs/CRITICAL_LOGIC.md** – SSOT 초안.
- **bridge.log** – 당시 로그(이후 a4cb247에서 비움).

**결과:** 공유 가능한 초기 저장소 상태 확립.

---

## 3. 현재 프로젝트 구조 (핵심만)

```
myllm-1/
├── ag_api_server.py      # Port 8045 Launcher API
├── bridge.py             # Telegram 라우팅 엔진
├── evolution_manager.py   # 자가 진단/진화, failure_db 관리
├── utils.py              # API/CLI 유틸, run_gemini_cli 재시도
├── run_bridge.ps1        # 브릿지 실행 스크립트
├── ag_tools.ps1          # GUI/워크스페이스 관리
├── README.md
├── docs/
│   ├── CRITICAL_LOGIC.md   # SSOT (필수 참조)
│   ├── CONTEXT_SNAPSHOT.md
│   ├── NEXT_STEPS.md
│   ├── TROUBLESHOOTING.md
│   └── LATEST_CHANGES.md   # 본 문서
└── logs/
    └── failure_db.json    # Self-Evolution용 실패 기록
```

---

## 4. SSOT에서 강제된 최신 규칙 (요약)

- **CLI 재시도:** `utils.run_gemini_cli` – 3회 재시도, 지수 백오프 2초.
- **메시지 길이:** 텔레그램 전송 시 4096자 한도 대비 슬라이싱(예: 최대 1000자).
- **Self-Evolution:** `/ag reflect` 시 `failure_db.json` 기반 분석 및 CRITICAL_LOGIC 반영.
- **System Vitals:** EvolutionManager가 포트 8045 및 Antigravity 프로세스 상태 점검.

---

## 5. 세션 중 변경 (문서 정리 시점 반영)

다음 내용은 커밋 이력 외에 논의·구현된 사항을 문서에 반영한 요약이다.

- **Develop 폴더 기반 기동**: `/ag <폴더명>` 또는 `/ag go` 시 브리지가 `path = AG_DEVELOP_ROOT\<폴더명>`(기본 `C:\develop\<폴더명>`)을 API에 전달. `ag_api_server.py`는 해당 `path`를 Antigravity 프로세스 CWD로 사용.
- **환경 변수**: `AG_DEVELOP_ROOT`(미설정 시 `C:\develop`), `AG_FOCUS_HOTKEY`(기본 `^l`). SSOT에 명시.
- **Zero-Touch 주입**: SendKeys 금지 원칙 유지. 검증된 시퀀스는 ESC → AG_FOCUS_HOTKEY → ^v → ENTER. PoC 검증용으로만 `FORCE_INJECT_POC=1` 시 예외 허용(§1.1).
- **미션·클립보드**: 자동 주입 실패 시 `AG_MISSION.md` 생성 및 클립보드 트리거; fallback 시에만 사용자에게 Ctrl+V 안내.
- **Self-Evolution**: `/ag reflect` 시 CWD는 브리지 프로젝트 루트(`_script_dir`), `failure_db.json` 내용을 stdin으로 Gemini CLI에 전달. 브리지 재시작 시 `failure_db.json`은 `[]`로 리셋되어 회고 과적 방지.
- **로그**: 브리지 재시작 시 `bridge.log` 초기화, 파일에는 WARNING 이상만 기록(RotatingFileHandler).
- **마스터 초기화**: `run_bridge.ps1` 실행 시 기존 `python.exe` 및 `Antigravity.exe` 강제 종료 후 Launcher(8045)와 브리지 재구축.
- **경로 오류**: "Path not in workspace"는 치명적 구성 오류로 분류, TROUBLESHOOTING에 대응 절차 추가.

---

## 6. 다음에 할 일 (NEXT_STEPS 기준)

- 에러 분석 엔진 강화 (`failure_db.json` 패턴 분류).
- pytest 기반 브릿지 명령 처리 검증.
- GUI 상태를 텔레그램으로 실시간 푸시 검토.

이 문서는 **최신 변경점 정리**용이며, 로직/아키텍처의 진실 원천은 **docs/CRITICAL_LOGIC.md**입니다.
