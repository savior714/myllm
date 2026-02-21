import logging
import asyncio
import os
import httpx
import json
import traceback
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from logging.handlers import RotatingFileHandler
from evolution_manager import EvolutionManager
from utils import run_gemini_cli, run_ag_api

# .env 파일 로드
load_dotenv()

# --- [설정 정보: .env 파일에서 로드] ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_CHAT_ID = int(os.getenv('ALLOWED_CHAT_ID', 0))
WORKSPACE_PATH = os.getenv('DEFAULT_WORKSPACE_PATH', r"C:\Users\savio")
GEMINI_EXE = os.getenv('GEMINI_EXE_PATH', r"C:\gemini-cli\gemini.cmd")
AG_MANAGER_URL = os.getenv('AG_MANAGER_URL', "http://127.0.0.1:8045/v1")
_script_dir = os.path.dirname(os.path.abspath(__file__))
AG_TOOLS_PS1 = os.path.join(_script_dir, "ag_tools.ps1")
LOG_DIR = os.path.join(_script_dir, "logs")
AG_MISSION_PATH = os.path.join(_script_dir, "AG_MISSION.md")
AG_MISSION_BODY = "README.md 내용을 읽고 현재 프로젝트 구조를 요약해서 텔레그램으로 보낼 준비를 해줘."
CLIPBOARD_TRIGGER = "@agent AG_MISSION.md 파일을 읽고 작업을 시작해."
DEVELOP_ROOT = os.getenv("AG_DEVELOP_ROOT", r"C:\develop")
os.makedirs(LOG_DIR, exist_ok=True)

# 자가 진화 초기화 (재시작 시 failure_db 초기화로 과적 방지)
evo = EvolutionManager()
try:
    with open(evo.failure_log, "w", encoding="utf-8") as f:
        f.write("[]")
except OSError:
    pass

# 로그 설정: 재실행 시 bridge.log 초기화, 파일에는 WARNING 이상만 기록(과적 방지)
log_file = os.path.join(LOG_DIR, "bridge.log")
open(log_file, 'w', encoding='utf-8').close()

rotating_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
rotating_handler.setLevel(logging.WARNING)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[rotating_handler, console_handler]
)

# --- [핵심 기능: 실행 유틸리티] ---

def _is_connection_error(e: Exception) -> bool:
    err = str(e).lower()
    return "8045" in err or "연결" in err or "connect" in err or "실행 중이지 않습니다" in err


async def handle_error_and_evolve(update: Update, e: Exception, context_tag: str):
    """에러 발생 시 로그를 남기고 에이전트에게 자가 수정을 제안합니다."""
    error_msg = str(e)
    stack_trace = traceback.format_exc()
    # 메시지 길이 제한(텔레그램 4096자): 연결 실패 시 500자, 그 외 1000자
    cap = 500 if _is_connection_error(e) else 1000
    safe_error_msg = (error_msg[:cap] + "...") if len(error_msg) > cap else error_msg

    evo.record_failure("RUNTIME_ERROR", error_msg, context_tag)
    logging.error(f"[{context_tag}] {error_msg}\n{stack_trace}")

    if _is_connection_error(e):
        await update.message.reply_text(
            f"**연결 실패**: `{safe_error_msg}`\n\n"
            "런처 서버(8045)가 켜져 있는지 확인하세요. `/ag reflect`로 진단할 수 있습니다."
        )
    else:
        await update.message.reply_text(
            f"**시스템 에러 감지**\n원인: `{safe_error_msg}`\n\n"
            "자가 수정을 원하시면 `/ag reflect`를 입력해 주세요."
        )
    return True

async def ensure_mission_and_clipboard() -> None:
    """미션 파일을 생성하고 클립보드에 트리거 문구를 복사합니다. SendKeys 대신 사용자 Ctrl+V로 주입."""
    try:
        with open(AG_MISSION_PATH, "w", encoding="utf-8") as f:
            f.write(AG_MISSION_BODY)
    except OSError:
        pass
    try:
        # PowerShell Set-Clipboard; 값 내 작은따옴표 이스케이프
        val = CLIPBOARD_TRIGGER.replace("'", "''")
        proc = await asyncio.create_subprocess_exec(
            "powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Value '{val}'",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
    except (asyncio.CancelledError, OSError):
        pass


async def run_reflection():
    """지난 실패를 분석하고 로직을 업데이트하는 회고 세션. failure_db 내용을 stdin으로 전달해 지능 복구."""
    path_failure_db = os.path.join(LOG_DIR, "failure_db.json")
    context_data: str | None = None
    try:
        if os.path.exists(path_failure_db):
            with open(path_failure_db, "r", encoding="utf-8") as f:
                context_data = f.read()
    except OSError:
        pass
    # 상대 경로만 사용해 Gemini CLI 워크스페이스 정책 내에서 접근하도록 유도.
    prompt = """
[SELF_REFLECTION_MODE]
너는 시니어 아키텍트다. stdin으로 전달된 실패 로그를 분석해라. (없으면 이 프로젝트의 logs/failure_db.json 을 읽어라.)
1. 최근 에러 패턴(중복 실행, 포트 충돌, 타임아웃, Tool execution denied 등)을 찾아라.
2. 개선안을 docs/CRITICAL_LOGIC.md 에 추가해라.
3. 필요 시 ag_tools.ps1, bridge.py 코드를 수정해라.
반드시 이 프로젝트 루트 내의 파일만 접근해라. 수정 완료 후 개선 요약을 보고해라.
"""
    # 회고 대상 파일(failure_db, CRITICAL_LOGIC, bridge 등)이 있는 브리지 프로젝트 루트를 cwd로 사용.
    return await run_gemini_cli(prompt, GEMINI_EXE, _script_dir, stdin_input=context_data)

# --- [핸들러 설정] ---

async def ag_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ag 로 시작하는 모든 명령을 처리합니다."""
    global WORKSPACE_PATH
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "**Antigravity 사용법:**\n"
                "/ag [폴더명] - c:\\develop 아래 폴더를 워크스페이스로 AG 기동 (예: /ag myllm-1)\n"
                "/ag go - 기본 경로로 기동\n"
                "/ag load [경로] - 워크스페이스 로드\n/ag reflect - 자가 회고\n/ag status - 상태 확인"
            )
            return

        sub_cmd = args[0].lower()

        # 특수 명령 처리: status
        if sub_cmd == "status" and len(args) == 1:
            success, res = await run_ag_api(AG_MANAGER_URL, "status")
            await update.message.reply_text(f"📊 **에이전트 상태:**\n{res}")
        
        # 특수 명령 처리: reflect (자가 회고)
        elif sub_cmd == "reflect":
            await update.message.reply_text("🧠 **시스템 자가 회고 및 최적화 세션 시작...**")
            success, res = await run_reflection()
            header = "✨ **회고 완료:**\n\n" if success else "❌ **회고 실패:**\n\n"
            await update.message.reply_text(header + res[:4000])

        # 특수 명령 처리: load
        elif sub_cmd == "load":
            path = args[1] if len(args) > 1 else WORKSPACE_PATH
            await update.message.reply_text(f"🚀 **Agent Manager 모드**로 전환 중: `{path}`")
            
            # 1. 플래그와 함께 Antigravity 실행 (ag_tools.ps1 호출)
            await asyncio.create_subprocess_exec('powershell.exe', '-File', AG_TOOLS_PS1, 'load', path)
            
            # 2. 8045 포트가 올라올 때까지 최대 10초 대기
            await update.message.reply_text("⏳ API 서버(8045) 활성화를 기다리는 중...")
            for i in range(10):
                await asyncio.sleep(1)
                success, _ = await run_ag_api(AG_MANAGER_URL, "status")
                if success:
                    await update.message.reply_text("✅ 에이전트 API 서버가 활성화되었습니다. 이제 대화가 가능합니다.")
                    return
            
            await update.message.reply_text("⚠️ GUI는 기동되었으나 8045 포트 응답이 없습니다. 수동으로 Agent Manager 탭을 확인해 주세요.")

        # 일반 에이전트 대화 및 자연어 작업 지시 (미션 파일 + 클립보드 트리거)
        else:
            await ensure_mission_and_clipboard()

            # 1. API 서버(8045) 조기 확인
            is_ready, _ = await run_ag_api(AG_MANAGER_URL, "status")
            
            if not is_ready:
                # 서버가 준비되지 않은 경우에만 GUI 기동 시도
                await update.message.reply_text("🖥 **Antigravity 에이전트 화면을 호출합니다...**")
                await asyncio.create_subprocess_exec('powershell.exe', '-File', AG_TOOLS_PS1, 'load', WORKSPACE_PATH)
                
                # 2. GUI 로딩 및 에이전트 준비 상태 체크 (최대 10초 대기)
                api_ready = False
                for i in range(10):
                    await asyncio.sleep(1)
                    success, _ = await run_ag_api(AG_MANAGER_URL, "status")
                    if success:
                        api_ready = True
                        break
                    
                if not api_ready:
                    await update.message.reply_text("⚠️ GUI는 기동되었으나 8045 포트 응답이 없습니다. 수동으로 에이전트 매니저 탭을 확인해 주세요.")
                    return
            else:
                # 이미 서버가 떠 있다면 포커싱만 수행 (ag_tools.ps1 load가 포커싱 포함)
                await update.message.reply_text("🖥 **이미 실행 중인 에이전트 화면으로 전환합니다...**")
                await asyncio.create_subprocess_exec('powershell.exe', '-File', AG_TOOLS_PS1, 'load', WORKSPACE_PATH)

            # 2. 런처 API로 기동 (폴더명 있으면 c:\develop\<폴더명>을 시작점으로 전달)
            launch_payload = {"messages": [{"role": "user", "content": "launch"}]}
            if args and args[0] not in ("go",):
                folder = args[0].replace("..", "").strip()
                if folder:
                    launch_payload["path"] = os.path.normpath(os.path.join(DEVELOP_ROOT, folder))
            success, raw_res = await run_ag_api(AG_MANAGER_URL, "chat/completions", launch_payload)

            if success:
                try:
                    data = json.loads(raw_res)
                    content = None
                    if data.get("choices") and len(data["choices"]) > 0:
                        content = data["choices"][0].get("message", {}).get("content")
                    remote_injected = data.get("remote_injected", False)
                    if content:
                        msg = f"**완료.** {content}"
                        if not remote_injected:
                            msg += "\n\n클립보드에 지시문이 복사되어 있습니다. 창에서 **Ctrl+V** 후 **Enter**로 실행하세요."
                        await update.message.reply_text(msg)
                    else:
                        await update.message.reply_text(
                            "**Antigravity를 기동했습니다.**" if remote_injected else
                            "**Antigravity를 기동했습니다.**\n\n클립보드에 지시문이 복사되어 있습니다. 창에서 **Ctrl+V** 후 **Enter**로 실행하세요."
                        )
                except (json.JSONDecodeError, KeyError, TypeError):
                    await update.message.reply_text("**Antigravity를 기동했습니다.**\n\n클립보드에 지시문이 복사되어 있습니다. 창에서 **Ctrl+V** 후 **Enter**로 실행하세요.")
            else:
                await update.message.reply_text(
                    f"실행 실패: {raw_res[:500]}\n\n"
                    "런처 서버(8045)가 켜져 있는지 확인하세요. `/ag reflect`로 진단할 수 있습니다."
                )
                
    except Exception as e:
        await handle_error_and_evolve(update, e, "ag_command_handler")

async def default_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ 로 시작하지 않는 모든 일반 메시지를 Gemini CLI로 처리합니다."""
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    user_text = update.message.text
    if not user_text:
        return

    try:
        # 사용자가 실수로 /ag 없이 '에이전트'라고 말할 경우를 위한 안내
        if any(kw in user_text.lower() for kw in ['에이전트', 'antigravity', '고쳐줘']):
            logging.info("에이전트 관련 키워드 감지됨. /ag 사용 권장.")

        await update.message.reply_text(f"🛠 **Gemini Vibe-Coding 수행 중... (Path: `{WORKSPACE_PATH}`)**")
        success, result = await run_gemini_cli(user_text, GEMINI_EXE, WORKSPACE_PATH)
        
        if not success:
            # result에 에러 메시지가 담겨있음
            await handle_error_and_evolve(update, Exception(result), "default_message_handler (Gemini CLI)")

        header = "✅ **작업 완료**\n\n" if success else "❌ **작업 실패**\n\n"
        await update.message.reply_text(header + result[:4000])
    except Exception as e:
        await handle_error_and_evolve(update, e, "default_message_handler")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """전역 에러 핸들러: Conflict(409) 시 스스로 종료하여 run_bridge.ps1 재시작으로 재로그인 유도."""
    error_msg = str(context.error)
    evo.record_failure("GLOBAL_POLLING_ERROR", error_msg, "telegram_library_error")
    logging.error(f"전역 에러 발생: {error_msg}")
    if "Conflict" in error_msg or "409" in error_msg:
        logging.warning("Telegram 409 Conflict 감지. 브리지 종료 후 run_bridge.ps1으로 재실행하세요.")
        raise SystemExit(1)

# --- [메인 실행부] ---

if __name__ == '__main__':
    if not BOT_TOKEN or not BOT_TOKEN.strip():
        print("BOT_TOKEN not set. Create .env with BOT_TOKEN=your_telegram_bot_token from https://t.me/BotFather")
        raise SystemExit(0)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 전역 에러 핸들러 등록
    application.add_error_handler(error_handler)
    
    # /ag 명령어 핸들러 (Antigravity 전용)
    application.add_handler(CommandHandler("ag", ag_command_handler))
    
    # 일반 텍스트 핸들러 (Gemini CLI 전용)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), default_message_handler))
    
    print(f"Bridge Online | Workspace: {WORKSPACE_PATH}")
    
    # 런타임 충돌 체크 (자가 치유 보강)
    conflict, pid = evo.check_for_conflicts()
    if conflict:
        logging.warning(f"중복 인스턴스 감지 (PID: {pid}). 시스템 클린업이 필요합니다.")
        # run_bridge.ps1에서 이미 처리하겠지만, 직접 실행 시를 위한 가드
    
    application.run_polling()
