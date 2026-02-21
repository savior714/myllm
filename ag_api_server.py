# C:\develop\myllm\ag_api_server.py
import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel
import subprocess
import os
import logging
import psutil

app = FastAPI(title="Antigravity Launcher API")

# 환경 설정 (비확장 변수 대신 직접 경로 사용 권장되나, %USERPROFILE% 유지)
AG_EXE = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Antigravity\Antigravity.exe")
WORKSPACE_PATH = r"C:\develop\myllm"

class ChatRequest(BaseModel):
    model: str = "antigravity-agent"
    messages: list

@app.get("/v1/status")
async def get_status():
    return {"status": "online", "mode": "launcher_only"}

@app.post("/v1/chat/completions")
async def handle_launch(payload: ChatRequest = Body(...)):
    """
    텔레그램 /ag 명령 시 Antigravity를 에이전트 모드로 실행만 합니다.
    잘못된 프롬프트 주입 시도로 인한 파일 생성 부작용을 원천 차단합니다.
    """
    try:
        # 이미 Antigravity가 실행 중인지 확인
        is_running = any("Antigravity" in p.info['name'] for p in psutil.process_iter(['name']))
        
        if is_running:
            # 이미 실행 중이면 추가 기동 없이 안내만 보냄
            return {
                "choices": [{
                    "message": {
                        "role": "assistant", 
                        "content": "🖥 Antigravity가 이미 실행 중입니다. 작업 중인 화면을 확인해 주세요."
                    }
                }]
            }

        # --agent 플래그를 사용하여 에이전트 매니저 모드로 기동
        # 주의: 사용자 EXE 경로 확인 결과 bin 폴더가 없으므로 루트 EXE 사용
        subprocess.Popen([AG_EXE, "--agent", WORKSPACE_PATH])
        return {
            "choices": [{
                "message": {
                    "role": "assistant", 
                    "content": "🚀 Antigravity 에이전트 매니저를 실행했습니다. PC 화면에서 작업을 이어가세요."
                }
            }]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8045)
