#!/usr/bin/env python3
"""
Stdio wrapper for Parliament MCP server.
This starts the HTTP server and provides a stdio interface for VS Code.
"""

import asyncio
import json
import sys
import subprocess
import os
import signal
import requests
from typing import Optional

SERVER_URL = "http://localhost:8080/mcp/"  # Note the trailing slash

class StdioMCPWrapper:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        
    async def start_server(self):
        """Start the HTTP MCP server with suppressed output"""
        # Suppress server output to avoid VS Code parsing issues
        devnull = open(os.devnull, 'w')
        
        self.server_process = subprocess.Popen([
            "/workspace/.venv/bin/python", 
            "-m", "parliament_mcp.mcp_server.main"
        ], 
        cwd="/workspace",
        stdout=devnull,
        stderr=devnull,
        env={**os.environ, "ENVIRONMENT": "local"}
        )
        
        # Wait for server to be ready
        for _ in range(30):  # 30 seconds timeout
            try:
                response = requests.get("http://localhost:8080/healthcheck", timeout=1)
                if response.status_code == 200:
                    break
            except:
                pass
            await asyncio.sleep(1)
        else:
            raise Exception("Server failed to start")
    
    async def handle_stdio(self):
        """Handle stdio communication"""
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                # Read line from stdin
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                # Parse JSON-RPC message
                try:
                    message = json.loads(line)
                    
                    # Forward to HTTP server
                    response = requests.post(
                        SERVER_URL,
                        json=message,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        timeout=30
                    )
                    
                    # Handle response
                    if response.status_code == 200:
                        if response.headers.get("Content-Type", "").startswith("application/json"):
                            result = response.json()
                            print(json.dumps(result), flush=True)
                        else:
                            # Handle non-JSON response
                            error_response = {
                                "jsonrpc": "2.0",
                                "id": message.get("id"),
                                "error": {
                                    "code": -32603,
                                    "message": f"Server returned non-JSON response: {response.status_code}"
                                }
                            }
                            print(json.dumps(error_response), flush=True)
                    else:
                        # HTTP error
                        error_response = {
                            "jsonrpc": "2.0", 
                            "id": message.get("id"),
                            "error": {
                                "code": -32603,
                                "message": f"HTTP error {response.status_code}: {response.text}"
                            }
                        }
                        print(json.dumps(error_response), flush=True)
                    
                except json.JSONDecodeError as e:
                    # Invalid JSON input, ignore silently or send error
                    continue
                except requests.RequestException as e:
                    # Network error
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id") if 'message' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Network error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                except Exception as e:
                    # Other error
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id") if 'message' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
            except KeyboardInterrupt:
                break
            except Exception:
                break
    
    def cleanup(self):
        """Clean up server process"""
        if self.server_process:
            try:
                # Terminate gracefully
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.server_process.kill()
                self.server_process.wait()
    
    async def run(self):
        """Main entry point"""
        try:
            await self.start_server()
            await self.handle_stdio()
        finally:
            self.cleanup()

async def main():
    wrapper = StdioMCPWrapper()
    
    # Handle signals for clean shutdown
    def signal_handler():
        wrapper.cleanup()
        
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
        
    await wrapper.run()

if __name__ == "__main__":
    asyncio.run(main())
