# inspect_ag_ui_v2.py - 창 타이틀 기반 Antigravity UI 덤프 (Electron 다중 프로세스 대응)
# 사용법: Antigravity 실행 후, 관리자 권한 터미널에서 python inspect_ag_ui_v2.py
# 결과: ag_ui_dump.txt 에 UI 계층이 저장됨. child_window 선택자 확정에 사용.

import sys
import time

def main() -> None:
    try:
        from pywinauto import Application

        print("Antigravity 창을 찾는 중...")
        app = Application(backend="uia").connect(title_re=".*Antigravity.*", timeout=5)
        dlg = app.window(title_re=".*Antigravity.*")
        dlg.set_focus()
        print("연결 성공. UI 구조를 분석합니다...")
        time.sleep(1)

        with open("ag_ui_dump.txt", "w", encoding="utf-8") as f:
            old_stdout = sys.stdout
            sys.stdout = f
            try:
                dlg.print_control_identifiers()
            finally:
                sys.stdout = old_stdout
        print("분석 완료: ag_ui_dump.txt 파일이 생성되었습니다.")

    except Exception as e:
        print(f"진단 실패: {e}")
        print("팁: 터미널을 관리자 권한으로 실행했는지, Antigravity 창이 떠 있는지 확인하세요.")


if __name__ == "__main__":
    main()
