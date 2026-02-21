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
AG_TOOLS_PS1 = os.path.join(os.getcwd(), "ag_tools.ps1")
LOG_DIR = r"C:\develop\myllm\logs"

# 자가 진화 초기화
evo = EvolutionManager()

# 로그 설정 (매 새 실행마다 기존 로그 비우기 / 5MB 로테이션)
log_file = os.path.join(LOG_DIR, "bridge.log")
open(log_file, 'w', encoding='utf-8').close()

rotating_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
rotating_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        rotating_handler,
        logging.StreamHandler()
    ]
)

# --- [핵심 기능: 실행 유틸리티] ---

async def handle_error_and_evolve(update: Update, e: Exception, context_tag: str):
    """에러 발생 시 로그를 남기고 에이전트에게 자가 수정을 제안합니다."""
    error_msg = str(e)
    stack_trace = traceback.format_exc()
    
    # 텔레그램 제한(4096자)을 고려하여 최대 1000자까지만 출력하고 나머지는 생략
    safe_error_msg = error_msg[:1000] + "..." if len(error_msg) > 1000 else error_msg
    
    # 1. 실패 기록 저장
    evo.record_failure("RUNTIME_ERROR", error_msg, context_tag)
    logging.error(f"[{context_tag}] {error_msg}\n{stack_trace}")

    # 2. 사용자에게 알림 및 자가 진화 제안
    await update.message.reply_text(
        f"❌ **시스템 에러 감지**\n원인: `{safe_error_msg}`\n\n"
        "🤖 **자가 진화 루프 가동:** 이 에러의 패턴을 분석하고 `CRITICAL_LOGIC.md`에 복구 로직을 추가할까요? "
        "자가 수정을 원하신다면 `/ag reflect`를 입력해 주세요."
    )
    return True

async def run_reflection():
    """지난 실패를 분석하고 로직을 업데이트하는 회고 세션을 실행합니다."""
    prompt = r"""
    [SELF_REFLECTION_MODE]
    너는 시니어 아키텍트다. C:\develop\myllm\logs\failure_db.json 파일을 분석해라.
    1. 최근 발생한 에러 패턴(중복 실행, 포트 충돌, 타임아웃 등)을 찾아라.
    2. 이를 방지하기 위한 개선안을 docs/CRITICAL_LOGIC.md에 추가해라.
    3. 필요하다면 ag_tools.ps1 이나 bridge.py의 코드로 직접 수정해라.
    수정이 완료되면 어떤 점을 개선했는지 요약해서 보고해라.
    """
    return await run_gemini_cli(prompt, GEMINI_EXE, WORKSPACE_PATH)

# --- [핸들러 설정] ---

async def ag_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ag 로 시작하는 모든 명령을 처리합니다."""
    global WORKSPACE_PATH
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return
    
    try:
        args = context.args
        if not args:
            await update.message.reply_text("💡 **Antigravity 사용법:**\n/ag [질문] - 에이전트와 대화\n/ag load [경로] - 워크스페이스 로드\n/ag reflect - 자가 회고 및 최적화\n/ag status - 상태 확인")
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

        # 일반 에이전트 대화 및 자연어 작업 지시
        else:
            # prompt = " ".join(args)  # Launcher Mode에서는 프롬프트를 API로 전달하지 않음

            # 1. 먼저 API 서버(8045)가 살아있는지 조기 확인
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

            # 3. Antigravity Manager API를 통해 실행 (단순 호출)
            success, raw_res = await run_ag_api(AG_MANAGER_URL, "chat/completions", {
                "messages": [{"role": "user", "content": "launch"}]
            })
            
            if success:
                await update.message.reply_text("✅ **워크스페이스 로드 완료.** 에이전트 매니저 탭이 활성화되었습니다. 직접 입력을 통해 작업을 진행해 주세요.")
            else:
                await update.message.reply_text(f"❌ 실행 실패: {raw_res}")
                
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
    """전역 에러 핸들러: 핸들러 내에서 잡히지 않은 모든 에러( Conflict 등)를 포착합니다."""
    error_msg = str(context.error)
    evo.record_failure("GLOBAL_POLLING_ERROR", error_msg, "telegram_library_error")
    logging.error(f"⚠️ 전역 에러 발생: {error_msg}")

# --- [메인 실행부] ---

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 전역 에러 핸들러 등록
    application.add_error_handler(error_handler)
    
    # /ag 명령어 핸들러 (Antigravity 전용)
    application.add_handler(CommandHandler("ag", ag_command_handler))
    
    # 일반 텍스트 핸들러 (Gemini CLI 전용)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), default_message_handler))
    
    print(f"🚀 Bridge Online | Workspace: {WORKSPACE_PATH}")
    
    # 런타임 충돌 체크 (자가 치유 보강)
    conflict, pid = evo.check_for_conflicts()
    if conflict:
        logging.warning(f"⚠️ 중복 인스턴스 감지 (PID: {pid}). 시스템 클린업이 필요합니다.")
        # run_bridge.ps1에서 이미 처리하겠지만, 직접 실행 시를 위한 가드
    
    application.run_polling()
