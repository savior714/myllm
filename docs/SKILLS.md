# Cursor Skills (myllm)

프로젝트에 사용 중인 에이전트 스킬의 출처와 경로입니다.

## 경로

- **Cursor**: `.cursor/skills/`
  - 채팅에서 `@스킬이름` 또는 `@폴더명`으로 호출 가능.

## 출처

1. **antigravity-awesome-skills** (sickn33)
   - 저장소: https://github.com/sickn33/antigravity-awesome-skills
   - `.cursor/skills/` 루트에 873+ 스킬 폴더가 복사됨.
   - 카탈로그: 해당 repo의 `CATALOG.md`, `docs/BUNDLES.md` 참고.

2. **savior714/skills**
   - 저장소: https://github.com/savior714/skills
   - `.cursor/skills/savior714/` 아래에 복사됨.
   - 예: `create-rule`, `create-skill`, `update-cursor-settings`, `pytest_verification` 등.

## 업데이트 방법

스킬을 최신 상태로 다시 가져오려면:

```powershell
# awesome-skills (전체 덮어쓰기 시 주의)
git clone --depth 1 https://github.com/sickn33/antigravity-awesome-skills.git _tmp_awesome_skills
Copy-Item _tmp_awesome_skills\skills\* .cursor\skills -Recurse -Force
Remove-Item _tmp_awesome_skills -Recurse -Force

# savior714/skills
git clone --depth 1 https://github.com/savior714/skills.git _tmp_savior_skills
Copy-Item _tmp_savior_skills\* .cursor\skills\savior714 -Recurse -Force -Exclude .git
Remove-Item _tmp_savior_skills -Recurse -Force
```

## 참고

- Windows에서 antigravity-awesome-skills 공식 스킬은 symlink를 쓰므로, 복사 시 일부는 별도 파일로 들어갔을 수 있음. 문제 있으면 해당 repo의 Troubleshooting(Developer Mode / `core.symlinks=true`) 참고.
- SSOT: `docs/CRITICAL_LOGIC.md`.
