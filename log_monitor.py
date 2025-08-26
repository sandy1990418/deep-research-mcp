#!/usr/bin/env python3
"""
MCP Server 日誌監控器 - 監控文件日誌
"""

import os
import time
import threading
from datetime import datetime
import subprocess

class LogFileMonitor:
    def __init__(self, log_file="mcp_server.log"):
        self.log_file = log_file
        self.stats = {
            "requests": 0,
            "tools": 0,
            "errors": 0,
            "last_activity": None
        }
        self.running = False
    
    def start_server_with_logging(self):
        """啟動帶日誌記錄的 MCP Server"""
        print("🚀 啟動帶日誌記錄的 MCP Server...")
        
        # 先清空舊的日誌文件
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        try:
            # 重定向輸出到日誌文件
            with open(self.log_file, 'w') as log_file:
                process = subprocess.Popen(
                    ["uv", "run", "main.py"],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            print(f"✅ Server 啟動成功 (PID: {process.pid})")
            print(f"📄 日誌文件: {self.log_file}")
            return process
            
        except Exception as e:
            print(f"❌ 啟動失敗: {e}")
            return None
    
    def monitor_log_file(self):
        """監控日誌文件"""
        print(f"👁️  開始監控日誌文件: {self.log_file}")
        
        # 等待日誌文件創建
        while not os.path.exists(self.log_file) and self.running:
            time.sleep(0.1)
        
        if not self.running:
            return
        
        # 使用 tail -f 的方式監控
        try:
            with open(self.log_file, 'r') as f:
                # 跳到文件末尾
                f.seek(0, 2)
                
                while self.running:
                    line = f.readline()
                    if line:
                        self.process_log_line(line.strip())
                        self.stats["last_activity"] = datetime.now()
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"❌ 日誌監控錯誤: {e}")
    
    def process_log_line(self, line):
        """處理日誌行"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 檢測工具調用
        if any(tool in line for tool in ["start_research", "analyze_content", "search_sources", "generate_report", "fact_check"]):
            print(f"[{timestamp}] 🔧 工具調用: {line}")
            self.stats["tools"] += 1
            self.stats["requests"] += 1
        
        # 檢測研究活動
        elif any(activity in line for activity in ["🔍", "✅", "📊", "Starting research", "Research completed"]):
            print(f"[{timestamp}] 📝 研究活動: {line}")
            self.stats["requests"] += 1
        
        # 檢測錯誤
        elif any(keyword in line.lower() for keyword in ["error", "exception", "failed", "traceback", "❌"]):
            print(f"[{timestamp}] ❌ 錯誤: {line}")
            self.stats["errors"] += 1
        
        # 檢測啟動信息
        elif "FastMCP" in line or "Starting MCP server" in line:
            print(f"[{timestamp}] 🚀 啟動: {line}")
        
        # 其他重要信息
        elif line and not line.isspace() and len(line) > 10:
            # 只顯示重要的日誌行
            if any(keyword in line for keyword in ["INFO", "WARNING", "ERROR", "HTTP", "POST", "GET"]):
                print(f"[{timestamp}] 📤 日誌: {line[:100]}...")
    
    def print_stats(self):
        """打印統計信息"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 Deep Research MCP Server - 日誌監控器")
        print("=" * 60)
        print(f"📊 統計信息:")
        print(f"   請求總數: {self.stats['requests']}")
        print(f"   工具調用: {self.stats['tools']}")  
        print(f"   錯誤次數: {self.stats['errors']}")
        
        if self.stats["last_activity"]:
            print(f"   最後活動: {self.stats['last_activity'].strftime('%H:%M:%S')}")
        
        print(f"\n📄 日誌文件: {self.log_file}")
        print("🎮 按 Ctrl+C 停止監控")
        print("\n📋 即時活動:")
        print("-" * 40)

def main():
    monitor = LogFileMonitor()
    
    # 啟動服務器
    server_process = monitor.start_server_with_logging()
    if not server_process:
        return
    
    monitor.running = True
    
    # 啟動監控線程
    monitor_thread = threading.Thread(target=monitor.monitor_log_file, daemon=True)
    monitor_thread.start()
    
    # 顯示統計信息
    monitor.print_stats()
    
    try:
        while monitor.running:
            time.sleep(2)
            
            # 檢查服務器是否還在運行
            if server_process.poll() is not None:
                print("❌ MCP Server 進程已停止")
                break
                
            # 定期更新統計顯示
            if monitor.stats["last_activity"]:
                last_activity_ago = datetime.now() - monitor.stats["last_activity"]
                if last_activity_ago.seconds < 5:  # 5秒內有活動就更新顯示
                    pass  # 已經在監控線程中打印了
    
    except KeyboardInterrupt:
        print("\n🛑 停止監控...")
    
    finally:
        monitor.running = False
        if server_process:
            server_process.terminate()
            server_process.wait()
        print("✅ 監控已停止")

if __name__ == "__main__":
    main()