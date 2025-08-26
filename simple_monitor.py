#!/usr/bin/env python3
"""
簡單的 MCP Server 活動監控器
專門監控 JSON-RPC 通訊
"""

import subprocess
import json
import time
import threading
import sys
import os
from datetime import datetime

class SimpleMCPMonitor:
    def __init__(self):
        self.stats = {
            "requests": 0,
            "tools_called": 0,
            "errors": 0,
            "start_time": datetime.now()
        }
        self.server_process = None
        self.running = False
        
    def start_server(self):
        """啟動 MCP Server"""
        print("🚀 啟動 MCP Server...")
        try:
            self.server_process = subprocess.Popen(
                ["uv", "run", "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # 無緩衝
            )
            self.running = True
            print(f"✅ Server 啟動成功 (PID: {self.server_process.pid})")
            return True
        except Exception as e:
            print(f"❌ 啟動失敗: {e}")
            return False
    
    def monitor_output(self):
        """監控服務器輸出"""
        def read_stdout():
            while self.running and self.server_process:
                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        self.process_output_line(line.strip(), "STDOUT")
                except Exception as e:
                    print(f"讀取 stdout 錯誤: {e}")
                    break
        
        def read_stderr():
            while self.running and self.server_process:
                try:
                    line = self.server_process.stderr.readline()
                    if line:
                        self.process_output_line(line.strip(), "STDERR")
                except Exception as e:
                    print(f"讀取 stderr 錯誤: {e}")
                    break
        
        # 啟動讀取線程
        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        
        stdout_thread.start()
        stderr_thread.start()
        
        return stdout_thread, stderr_thread
    
    def process_output_line(self, line, source):
        """處理服務器輸出行"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 檢測 JSON-RPC 訊息
        if line.startswith('{') and 'method' in line:
            try:
                data = json.loads(line)
                method = data.get('method', 'unknown')
                print(f"[{timestamp}] 📨 RPC: {method}")
                self.stats["requests"] += 1
                
                if method.startswith('tools/'):
                    self.stats["tools_called"] += 1
                    print(f"[{timestamp}] 🔧 Tool called: {method}")
                    
            except json.JSONDecodeError:
                pass
        
        # 檢測錯誤
        elif any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'traceback']):
            print(f"[{timestamp}] ❌ ERROR ({source}): {line}")
            self.stats["errors"] += 1
        
        # 檢測我們的工具日誌
        elif any(keyword in line for keyword in ['🔍', '✅', '📊', '⚠️']):
            print(f"[{timestamp}] 📝 LOG: {line}")
        
        # 檢測啟動訊息
        elif "FastMCP" in line or "Starting MCP server" in line:
            print(f"[{timestamp}] 🚀 STARTUP: {line}")
        
        # 其他重要訊息
        elif line and not line.isspace():
            print(f"[{timestamp}] 📤 INFO: {line}")
    
    def print_stats(self):
        """打印統計信息"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        uptime = datetime.now() - self.stats["start_time"]
        uptime_str = str(uptime).split('.')[0]
        
        print("🔍 Deep Research MCP Server - 簡易監控器")
        print("=" * 60)
        print(f"📊 狀態: {'運行中' if self.running else '已停止'}")
        print(f"⏱️  運行時間: {uptime_str}")
        print(f"📨 接收請求: {self.stats['requests']}")
        print(f"🔧 工具調用: {self.stats['tools_called']}")
        print(f"❌ 錯誤次數: {self.stats['errors']}")
        
        if self.server_process:
            print(f"🆔 進程 ID: {self.server_process.pid}")
        
        print("\n🎯 即時日誌:")
        print("-" * 30)
    
    def send_test_request(self):
        """發送測試請求"""
        if not self.server_process or not self.running:
            return
        
        print("🧪 發送測試請求...")
        
        # MCP 初始化請求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            request_str = json.dumps(init_request) + "\\n"
            self.server_process.stdin.write(request_str)
            self.server_process.stdin.flush()
            print("✅ 測試請求已發送")
        except Exception as e:
            print(f"❌ 發送測試請求失敗: {e}")
    
    def run(self):
        """運行監控器"""
        if not self.start_server():
            return
        
        # 等待服務器啟動
        time.sleep(2)
        
        # 啟動監控線程
        self.monitor_output()
        
        # 顯示初始統計
        self.print_stats()
        
        print("🎮 控制選項:")
        print("  t - 發送測試請求")
        print("  s - 顯示統計")
        print("  q - 退出")
        
        try:
            while self.running:
                # 簡單的用戶輸入處理
                time.sleep(1)
                
                # 這裡可以添加更多監控邏輯
                if self.server_process and self.server_process.poll() is not None:
                    print("❌ MCP Server 進程意外終止")
                    break
                    
        except KeyboardInterrupt:
            print("\\n🛑 監控已停止")
        finally:
            self.stop()
    
    def stop(self):
        """停止監控和服務器"""
        self.running = False
        if self.server_process:
            print("🛑 正在停止服務器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ 服務器已停止")

def main():
    print("🔍 Deep Research MCP Server - 簡易監控器")
    print("專門監控 JSON-RPC 通訊和工具調用")
    print("=" * 50)
    
    monitor = SimpleMCPMonitor()
    
    try:
        monitor.run()
    except Exception as e:
        print(f"❌ 監控器錯誤: {e}")
        monitor.stop()

if __name__ == "__main__":
    main()