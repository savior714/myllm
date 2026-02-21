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
            "obsidian_accessible": os.path.exists(r"C:\obsidian")
        }
        return vitals

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

if __name__ == "__main__":
    # 단독 실행 시 진단 테스트
    manager = EvolutionManager()
    print(json.dumps(manager.check_vitals(), indent=4))
