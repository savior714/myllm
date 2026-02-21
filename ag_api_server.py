import uvicorn
from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
import subprocess
import os
import logging

# 로그 설정 (C:\develop\myllm\logs\api_server.log)
LOG_FILE = r"C:\develop\myllm\logs\api_server.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

app = FastAPI(title="Antigravity Manager API Wrapper")

# 모든 요청/응답 기록을 위한 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"요청 수신: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"응답 발신: 상태코드 {response.status_code}")
    return response

# 워크스페이스 및 실행 파일 경로 설정
AG_EXE = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Antigravity\Antigravity.exe")
WORKSPACE_PATH = r"C:\develop\myllm"

class ChatRequest(BaseModel):
    model: str = "antigravity-agent"
    messages: list
    stream: bool = False

@app.get("/v1/status")
async def get_status():
    """브리지가 서버의 생존 여부를 확인할 때 사용합니다."""
    return {"status": "online", "message": "Antigravity API Wrapper is active and listening on port 8045."}

@app.post("/v1/chat/completions")
async def handle_chat(payload: ChatRequest = Body(...)):
    """텔레그램 명령을 받아 Antigravity GUI를 제어합니다."""
    # messages 리스트가 비어있는지 확인하는 안전장치 추가
    if not payload.messages:
        return {"error": "No messages provided."}
        
    user_prompt = payload.messages[-1]["content"]
    
    # 1. Antigravity 실행
    # --agent 플래그는 존재하지 않으므로 제거하고 워크스페이스 경로만 전달함
    try:
        # Popen을 사용하여 비동기적으로 실행 (API 응답은 즉시 반환)
        subprocess.Popen([AG_EXE, WORKSPACE_PATH])
        return {
            "choices": [{
                "message": {
                    "role": "assistant", 
                    "content": f"명령을 수신했습니다: '{user_prompt}'. Antigravity GUI(Agent Manager)에서 작업을 시작합니다."
                }
            }]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 127.0.0.1:8045 포트로 서버 기동
    uvicorn.run(app, host="127.0.0.1", port=8045)
