#!/usr/bin/env python3
"""
Deep Research MCP Server Monitoring Tool
Based on search results and best practices
"""

import asyncio
import json
import logging
import time
import psutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import signal
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp-monitor")

class MCPServerMonitor:
    """MCP Server Monitor"""
    
    def __init__(self):
        self.server_process = None
        self.is_running = False
        self.stats = {
            "start_time": None,
            "requests_handled": 0,
            "errors_occurred": 0,
            "memory_peak": 0,
            "cpu_peak": 0.0
        }
    
    def start_server(self):
        """Start MCP Server"""
        try:
            logger.info("Starting MCP Server...")
            
            self.server_process = subprocess.Popen(
                ["uv", "run", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            
            logger.info(f"MCP Server started with PID: {self.server_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP Server: {e}")
            return False
    
    def stop_server(self):
        """Stop MCP Server"""
        if self.server_process:
            logger.info("Stopping MCP Server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            
            self.is_running = False
            logger.info("MCP Server stopped")
    
    def get_server_stats(self):
        """Get server statistics"""
        if not self.server_process:
            return None
        
        try:
            # Get process information
            process = psutil.Process(self.server_process.pid)
            
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            # Update peak values
            memory_mb = memory_info.rss / 1024 / 1024
            if memory_mb > self.stats["memory_peak"]:
                self.stats["memory_peak"] = memory_mb
            
            if cpu_percent > self.stats["cpu_peak"]:
                self.stats["cpu_peak"] = cpu_percent
            
            uptime = datetime.now() - self.stats["start_time"] if self.stats["start_time"] else "N/A"
            
            return {
                "status": "running" if self.is_running else "stopped",
                "pid": self.server_process.pid,
                "uptime": str(uptime).split('.')[0],  # Remove microseconds
                "memory_mb": round(memory_mb, 2),
                "memory_peak_mb": round(self.stats["memory_peak"], 2),
                "cpu_percent": round(cpu_percent, 2),
                "cpu_peak": round(self.stats["cpu_peak"], 2),
                "threads": process.num_threads(),
                "connections": len(process.connections()) if hasattr(process, 'connections') else 0
            }
            
        except psutil.NoSuchProcess:
            return {"status": "not_found", "error": "Process not found"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def monitor_logs(self):
        """Monitor server log output"""
        if not self.server_process:
            return
        
        try:
            import select
            import fcntl
            import os
            
            # Set non-blocking read
            if self.server_process.stdout:
                fd = self.server_process.stdout.fileno()
                flag = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
                
                try:
                    line = self.server_process.stdout.readline()
                    if line:
                        log_line = line.strip()
                        logger.info(f"SERVER: {log_line}")
                        
                        # Analyze log content
                        line_lower = log_line.lower()
                        if "error" in line_lower or "exception" in line_lower:
                            self.stats["errors_occurred"] += 1
                        if any(keyword in line_lower for keyword in ["request", "tool", "start_research", "analyze", "generate"]):
                            self.stats["requests_handled"] += 1
                        if "ctx.info" in log_line or "ctx.error" in log_line:
                            self.stats["requests_handled"] += 1
                except IOError:
                    pass  # No data available
                    
            # Read stderr
            if self.server_process.stderr:
                fd = self.server_process.stderr.fileno()
                flag = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
                
                try:
                    line = self.server_process.stderr.readline()
                    if line:
                        log_line = line.strip()
                        logger.warning(f"SERVER ERROR: {log_line}")
                        self.stats["errors_occurred"] += 1
                except IOError:
                    pass  # No data available
                    
        except Exception as e:
            logger.error(f"Log monitoring error: {e}")
    
    def print_dashboard(self):
        """Print monitoring dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("Deep Research MCP Server - Live Monitor")
        print("=" * 60)
        
        stats = self.get_server_stats()
        if stats:
            print(f"Server Status: {stats['status'].upper()}")
            if stats['status'] == 'running':
                print(f"Process ID: {stats['pid']}")
                print(f"Uptime: {stats['uptime']}")
                print(f"Memory: {stats['memory_mb']} MB (Peak: {stats['memory_peak_mb']} MB)")
                print(f"CPU: {stats['cpu_percent']}% (Peak: {stats['cpu_peak']}%)")
                print(f"Threads: {stats['threads']}")
                print(f"Connections: {stats['connections']}")
            else:
                print(f"Error: {stats.get('error', 'Unknown')}")
        else:
            print("Server Status: NOT RUNNING")
        
        print(f"\nActivity Stats:")
        print(f"   Requests Handled: {self.stats['requests_handled']}")
        print(f"   Errors Occurred: {self.stats['errors_occurred']}")
        
        print(f"\nControls:")
        print(f"   Ctrl+C: Stop monitoring")
        print(f"   r: Restart server")
        print(f"   q: Quit")
        
        # Check server health status
        if stats and stats['status'] == 'running':
            health_issues = []
            if stats['memory_mb'] > 500:  # 500MB warning threshold
                health_issues.append(f"High memory usage: {stats['memory_mb']} MB")
            if stats['cpu_percent'] > 80:  # 80% CPU warning threshold
                health_issues.append(f"High CPU usage: {stats['cpu_percent']}%")
            
            if health_issues:
                print(f"\nHealth Warnings:")
                for issue in health_issues:
                    print(f"   {issue}")
            else:
                print(f"\nServer Health: GOOD")

async def interactive_monitor():
    """Interactive monitoring"""
    monitor = MCPServerMonitor()
    
    def signal_handler(signum, frame):
        print("\nShutting down monitor...")
        monitor.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server
    if not monitor.start_server():
        print("Failed to start server. Check logs.")
        return
    
    # Wait for server startup
    await asyncio.sleep(2)
    
    # Main monitoring loop
    while monitor.is_running:
        try:
            monitor.print_dashboard()
            
            # Monitor logs
            monitor.monitor_logs()
            
            # Check if server is still running
            if monitor.server_process.poll() is not None:
                logger.error("MCP Server process has stopped unexpectedly")
                break
            
            await asyncio.sleep(1)  # Update every second
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            await asyncio.sleep(1)
    
    monitor.stop_server()

def test_mcp_inspector():
    """Test MCP Inspector integration"""
    print("Testing MCP Inspector Integration")
    print("-" * 40)
    
    try:
        # Check if MCP Inspector is installed
        result = subprocess.run(
            ["npx", "@modelcontextprotocol/inspector", "--version"], 
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("MCP Inspector is available")
            print(f"Version: {result.stdout.strip()}")
            
            print("\nTo use MCP Inspector:")
            print("1. Run: npx @modelcontextprotocol/inspector")
            print("2. Configure server:")
            print("   Command: uv")
            print("   Args: run main.py")
            print(f"   Working Directory: {Path.cwd()}")
            
        else:
            print("MCP Inspector not found")
            print("Install with: npm install -g @modelcontextprotocol/inspector")
            
    except FileNotFoundError:
        print("Node.js/npm not found. Install Node.js first.")
    except subprocess.TimeoutExpired:
        print("Inspector check timed out")
    except Exception as e:
        print(f"Inspector check failed: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_mcp_inspector()
        elif command == "monitor":
            asyncio.run(interactive_monitor())
        elif command == "start":
            monitor = MCPServerMonitor()
            if monitor.start_server():
                print("MCP Server started successfully")
                print(f"PID: {monitor.server_process.pid}")
            else:
                print("Failed to start MCP Server")
        else:
            print(f"Unknown command: {command}")
    else:
        print("Deep Research MCP Server Monitor")
        print("=" * 40)
        print("Commands:")
        print("  python monitor.py test     - Test MCP Inspector")
        print("  python monitor.py monitor  - Start live monitoring")  
        print("  python monitor.py start    - Start server only")

if __name__ == "__main__":
    main()