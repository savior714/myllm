# inspect_ag_ui.py - Antigravity UI 계층 덤프 (창 타이틀 기반, Electron 다중 프로세스 대응)
# 사용법: Antigravity 실행 후 실행. 출력에서 Edit/Document 등 입력창 선택자 확인.
# V2: inspect_ag_ui_v2.py 는 결과를 ag_ui_dump.txt 로 저장함.

def main() -> None:
    try:
        from pywinauto import Application

        app = Application(backend="uia").connect(title_re=".*Antigravity.*", timeout=5)
        dlg = app.window(title_re=".*Antigravity.*")

        print("=== Antigravity UI Hierarchy Dump ===")
        print("(Edit/Document 또는 채팅 입력창의 control_type, auto_id를 ag_api_server._ui_inject_sync에 반영)")
        print()
        dlg.print_control_identifiers()

    except Exception as e:
        print(f"진단 실패: {e}")
        print("Antigravity 창이 떠 있는지, 필요 시 관리자 권한으로 실행하세요.")


if __name__ == "__main__":
    main()
