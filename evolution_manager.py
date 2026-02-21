# C:\develop\myllm\evolution_manager.py
import json
import os
import psutil
import socket
import logging
from datetime import datetime

class EvolutionManager:
    def __init__(self, root_path=r"C:\develop\myllm"):
        self.root_path = root_path
        self.logic_file = os.path.join(root_path, "docs", "CRITICAL_LOGIC.md")
        self.failure_log = os.path.join(root_path, "logs", "failure_db.json")
        self.log_dir = os.path.join(root_path, "logs")
        
        # 로그 폴더가 없으면 생성
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def check_vitals(self):
        """시스템의 현재 상태(Vitals)를 진단합니다."""
        vitals = {
            "timestamp": datetime.now().isoformat(),
            "port_8045": self._is_port_open(8045),
            "antigravity_running": self._is_process_running("Antigravity"),
            "workspace_accessible": os.path.exists(self.root_path),
            "obsidian_accessible": os.path.exists(r"C:\obsidian"),
            "conflict_detected": self.check_for_conflicts()[0]
        }
        return vitals

    def check_for_conflicts(self):
        """PID 파일 및 프로세스 목록을 통해 중복 실행 여부를 고성능으로 확인합니다."""
        pid_file = os.path.join(self.log_dir, "bridge.pid")
        current_pid = os.getpid()

        # 1. PID 파일 체크 (Fast Path) - Lock 방어 로직 추가
        if os.path.exists(pid_file):
            if os.access(pid_file, os.R_OK):
                try:
                    with open(pid_file, "r") as f:
                        old_pid = int(f.read().strip())
                    if old_pid != current_pid and psutil.pid_exists(old_pid):
                        proc = psutil.Process(old_pid)
                        if 'bridge.py' in " ".join(proc.cmdline()):
                            return True, old_pid
                except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
                    pass # PID 파일이 오염되었거나 권한이 없는 경우 Full Scan으로 이행

        # 2. 프로세스 전체 순회 (Deep Scan - Timeout 적용 및 최적화)
        import time
        start_time = time.time()
        for proc in psutil.process_iter(['pid', 'name']):
            if time.time() - start_time > 2.0:  # 2초 초과 시 스캔 중단 (Deadlock 방지)
                logging.warning("Process scan timeout exceeded (2s). Aborting deep scan.")
                break
            try:
                # 나 자신을 제외하고 python 프로세스만 골라 cmdline을 가져옴 (성능 향상)
                if proc.info['pid'] != current_pid and proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = " ".join(proc.cmdline() or [])
                    if 'bridge.py' in cmdline:
                        return True, proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False, None

    def save_pid(self):
        """현재 프로세스의 PID를 파일에 기록합니다."""
        pid_file = os.path.join(self.log_dir, "bridge.pid")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        logging.info(f"PID 기록 완료: {os.getpid()}")

    def _is_port_open(self, port):
        """로컬 포트 개방 여부 확인"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('127.0.0.1', port)) == 0

    def _is_process_running(self, name):
        """특정 프로세스 실행 여부 확인"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def record_failure(self, error_type, message, context=""):
        """실패 사례를 JSON 데이터베이스에 저장합니다."""
        failure_data = {
            "vitals": self.check_vitals(),
            "error_type": error_type,
            "message": message,
            "context": context
        }
        
        history = []
        if os.path.exists(self.failure_log):
            try:
                with open(self.failure_log, "r", encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append(failure_data)
        # 최근 50개의 실패 사례만 유지 (용량 관리)
        with open(self.failure_log, "w", encoding='utf-8') as f:
            json.dump(history[-50:], f, indent=4, ensure_ascii=False)
        
        logging.info(f"실패 기록 완료: {error_type}")

    def get_recent_failures(self, minutes=1):
        """최근 N분 내에 발생한 실패 기록을 반환합니다."""
        if not os.path.exists(self.failure_log):
            return []
            
        try:
            with open(self.failure_log, "r", encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            return []
            
        recent = []
        now = datetime.now()
        for entry in history:
            try:
                failure_time = datetime.fromisoformat(entry["vitals"]["timestamp"])
                if (now - failure_time).total_seconds() < (minutes * 60):
                    recent.append(entry)
            except (KeyError, ValueError):
                continue
        return recent

if __name__ == "__main__":
    # 단독 실행 시 진단 테스트
    manager = EvolutionManager()
    print(json.dumps(manager.check_vitals(), indent=4))
