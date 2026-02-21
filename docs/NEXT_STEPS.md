# Next Steps: myllm

프로젝트의 안정성 향상과 기능 확장을 위한 향후 작업 로드맵입니다.

## 🚀 Immediate Tasks
- [ ] **에러 분석 엔진 강화**: `failure_db.json`의 데이터를 기반으로 한 에러 패턴 분류 정교화.
- [ ] **자동화 테스트 확충**: `pytest`를 통한 브릿지 명령어 처리 로직 검증.
- [ ] **GUI 상태 연동**: Antigravity GUI의 현재 진행 상태를 텔레그램으로 실시간 푸시하는 기능.

## 🛠 Technical Debt & Improvements
- [ ] **비동기 가드 로직 강화**: 모든 외부 프로세스 호출에 대한 타임아웃 처리 정밀화.
- [ ] **로그 가독성 개선**: 텔레그램으로 전달되는 로그 메시지의 마크다운 포맷팅 최적화.
- [ ] **멀티 유저 지원 검토**: 현재 단일 챗 ID 기반에서 다중 사용자 권한 관리 체계로 확장 고려.

## 💡 Future Ideas
- **Voice Control**: 텔레그램 음성 메시지를 텍스트로 변환하여 명령 실행.
- **Mobile Optimized UI**: 텔레그램 버튼 리모컨을 통한 주요 기능 원클릭 제어.
- **Agent Collaboration**: 복수의 Antigravity 에이전트를 생성하여 협업 모델 구축.
