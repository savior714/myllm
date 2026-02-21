import asyncio
import os
import httpx

async def run_gemini_cli(
    prompt: str,
    gemini_exe: str,
    workspace_path: str,
    max_retries: int = 3,
    stdin_input: str | bytes | None = None,
):
    """Gemini CLI 호출. stdin_input이 있으면 실패 로그 등 컨텍스트를 stdin으로 전달(reflect 지능 복구)."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    inp: bytes | None = None
    if stdin_input is not None:
        inp = stdin_input.encode("utf-8") if isinstance(stdin_input, str) else stdin_input

    for attempt in range(max_retries):
        try:
            process = await asyncio.create_subprocess_exec(
                "cmd.exe", "/c", gemini_exe,
                prompt,
                "--yolo",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace_path,
                env=env,
            )
            stdout, stderr = await process.communicate(input=inp)
            
            try:
                out = stdout.decode('utf-8')
            except UnicodeDecodeError:
                out = stdout.decode('cp949', errors='ignore')
                
            try:
                err = stderr.decode('utf-8')
            except UnicodeDecodeError:
                err = stderr.decode('cp949', errors='ignore')
            
            result = out if process.returncode == 0 else (out + "\n" + err)
            
            # GaxiosError 등이 발생했으나 프로세스가 0이 아닌 코드를 반환하거나
            # 에러 문자열에 특정 키워드가 있는 경우 재시도
            if process.returncode != 0 and ("GaxiosError" in result or "AbortError" in result):
                if attempt < max_retries - 1:
                    await asyncio.sleep(2) # 재시도 전 대기
                    continue
            
            return (process.returncode == 0, result)
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue
            return (False, f"Gemini 실행 오류: {str(e)}")
            
    return (False, "Gemini 실행 최대 재시도 횟수 초과.")

async def run_ag_api(ag_manager_url: str, endpoint: str, data: dict = None):
    """Antigravity Manager API(Port 8045)를 호출합니다."""
    url = f"{ag_manager_url}/{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            if data:
                response = await client.post(url, json=data, timeout=60.0)
            else:
                response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                return True, response.text
            return False, f"API 오류 ({response.status_code}): {response.text}"
        except httpx.ConnectError:
            return False, "Antigravity-Manager(8045)가 실행 중이지 않습니다. 런처 서버를 확인하세요. (python ag_api_server.py)"
        except Exception as e:
            return False, f"Antigravity 연결 실패: {str(e)}"
