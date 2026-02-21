# Troubleshooting Guide: myllm

이 문서는 프로젝트 운영 및 개발 중 발생하는 일반적인 문제와 해결 방법을 다룹니다.

## 1. 텔레그램 봇 관련

### ⚠️ Conflict Error (HTTP 409)
- **증상**: 로그에 `telegram.error.Conflict` 기록되며 봇이 응답하지 않음.
- **원인**: 동일한 토큰으로 다른 인스턴스가 실행 중임.
- **해결**: 
  ```powershell
  # 기존 프로세스 정리
  ./run_bridge.ps1
  ```
  `run_bridge.ps1`은 실행 시 자동으로 기존 `bridge.py` 프로세스를 찾아 종료시킵니다.

## 2. Antigravity 에이전트 관련

### ⚠️ API 연결 실패 (Port 8045)
- **증상**: `/ag status` 명령 시 "API 서버 응답 대기 시간 초과" 발생.
- **원인**: Antigravity Manager가 기동되지 않았거나, 포트 충돌이 발생함.
- **해결**:
  1. `ag_tools.ps1`을 통해 GUI가 정상적으로 떴는지 확인.
  2. `netstat -ano | findstr :8045`로 포트 점유 여부 확인.
  3. 필요 시 `/ag load`를 다시 입력하여 재기동 시도.

## 3. 로그 및 파일 권한

### ⚠️ 로그 기록 실패
- **증상**: `logs` 폴더에 파일이 생성되지 않음.
- **원인**: 폴더 쓰기 권한 부족 또는 `EvolutionManager` 경로 설정 오류.
- **해결**: `logs` 폴더가 존재하지 않는 경우 `EvolutionManager`가 자동 생성하지만, 수동으로 `C:\develop\myllm\logs` 권한을 확인하십시오.

## 4. 자가 진화 (Reflect) 관련

### ⚠️ 수정 후 루프 발생
- **증상**: `/ag reflect` 후에 코드가 계속해서 같은 부분을 수정하려고 함.
- **원인**: 수정된 로직이 다시 에러를 유발하거나, `CRITICAL_LOGIC.md`가 업데이트되지 않음.
- **해결**: `docs/CRITICAL_LOGIC.md`의 내용을 직접 검토하고 모순된 규칙이 있는지 확인하십시오.
