# ag_api_server.py (런처 + Zero-Touch: 단축키+클립보드 주입. Electron 깊은 Pane 구조 회피)
import asyncio
import os
import subprocess
import time
import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Antigravity Launcher API")

AG_EXE = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Antigravity\Antigravity.exe")
# 프로세스 CWD 고정: Antigravity가 c:\develop 하위를 보도록. .env의 DEFAULT_WORKSPACE_PATH로 덮어쓸 수 있음.
WORKSPACE_PATH = os.getenv("DEFAULT_WORKSPACE_PATH", r"C:\develop")
REMOTE_MISSION_TEXT = "@agent AG_MISSION.md 파일을 읽고 작업을 시작해."
# Antigravity 입력창 포커스 단축키. 앱 단축키에 맞게 변경 가능 (예: Ctrl+I).
FOCUS_INPUT_HOTKEY = os.getenv("AG_FOCUS_HOTKEY", "^l")


def _ui_inject_sync(mission_text: str) -> bool:
    """
    검증된 Surgical Sequence: ESC로 포커스 초기화 -> Ctrl+L로 입력창 점유 -> Ctrl+V -> Enter.
    원격 Zero-Touch 주입의 정공법.
    """
    try:
        from pywinauto import Application
        from pywinauto.keyboard import send_keys

        app = Application(backend="uia").connect(title_re=".*Antigravity.*", timeout=10)
        dlg = app.window(title_re=".*Antigravity.*")
        dlg.set_focus()
        time.sleep(1)

        clip_val = mission_text.replace("'", "''")
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Value '{clip_val}'"],
            capture_output=True,
            timeout=5,
            check=False,
        )

        send_keys("{ESC}")
        time.sleep(0.5)
        send_keys(FOCUS_INPUT_HOTKEY)
        time.sleep(1)
        send_keys("^v")
        time.sleep(0.5)
        send_keys("{ENTER}")
        return True
    except Exception:
        return False


class ChatRequest(BaseModel):
    model: str = "antigravity-agent"
    messages: list = []
    path: str | None = None


@app.get("/v1/status")
async def get_status():
    return {"status": "online", "mode": "launcher_remote"}


@app.post("/v1/chat/completions")
async def handle_launch(payload: ChatRequest | None = Body(None)):
    """
    기동 후 pywinauto로 입력창 강제 주입(Zero-Touch). 실패 시 클립보드 백업 안내.
    """
    try:
        target_path = None
        if payload and getattr(payload, "path", None):
            p = payload.path.strip()
            if os.path.isdir(p):
                target_path = p
        if target_path is None:
            target_path = WORKSPACE_PATH
        if not os.path.isdir(target_path):
            target_path = os.path.expanduser("~")
        subprocess.Popen(
            [AG_EXE, "--agent", target_path],
            cwd=target_path,
        )
        await asyncio.sleep(8)

        injected = await asyncio.to_thread(_ui_inject_sync, REMOTE_MISSION_TEXT)
        if injected:
            content = "원격 미션 하달 완료."
            remote_injected = True
        else:
            content = "직접 주입 실패, 클립보드 백업 모드 가동."
            remote_injected = False

        return {
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "remote_injected": remote_injected,
        }
    except Exception as e:
        return {
            "choices": [{"message": {"role": "assistant", "content": f"직접 주입 실패, 클립보드 백업 모드 가동. ({e!s})"}}],
            "remote_injected": False,
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8045)
