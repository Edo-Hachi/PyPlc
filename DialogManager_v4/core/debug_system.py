"""
DialogManager v4 - Debug System

統合デバッグシステム（Gemini推奨アーキテクチャ）
階層化ログ・性能測定・コンテキスト管理
"""

import time
from typing import Dict, List, Any, Optional
from contextlib import nullcontext


class DebugSystem:
    """v4統合デバッグシステム（Gemini推奨）"""
    
    def __init__(self, component: str, level: str = "INFO"):
        self.component = component
        self.level = level
        self.indent = 0
        self.context_stack: List[str] = []
        
    def enter_context(self, name: str, data: Optional[Dict] = None):
        """コンテキスト開始（階層化ログ）"""
        self.context_stack.append(name)
        self.log("CONTEXT", f">>> {name}", data)
        self.indent += 1
        
    def exit_context(self, name: Optional[str] = None):
        """コンテキスト終了"""
        if self.context_stack:
            context_name = self.context_stack.pop()
            self.indent = max(0, self.indent - 1)
            self.log("CONTEXT", f"<<< {context_name}")
            
    def log(self, level: str, message: str, data: Any = None):
        """階層化ログ出力"""
        indent = "  " * self.indent
        context = " -> ".join(self.context_stack) if self.context_stack else ""
        prefix = f"[{level}][{self.component}]"
        if context:
            prefix += f"[{context}]"
            
        print(f"{prefix} {indent}{message}")
        if data:
            self._print_data(data, self.indent + 1)
            
    def _print_data(self, data, indent_level):
        """データの階層表示"""
        indent = "  " * indent_level
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"[DATA] {indent}{k}: {v}")
        else:
            print(f"[DATA] {indent}{data}")
            
    def error(self, message: str, exception: Optional[Exception] = None):
        """エラーログ"""
        self.log("ERROR", message)
        if exception:
            self.log("ERROR", f"Exception: {str(exception)}")
            
    def measure_time(self, operation_name: str):
        """性能測定コンテキストマネージャー"""
        class TimeContext:
            def __init__(self, debug_system, name):
                self.debug_system = debug_system
                self.name = name
                self.start_time = None
                
            def __enter__(self):
                self.start_time = time.perf_counter()
                self.debug_system.log("PERF", f"Starting: {self.name}")
                return self
                
            def __exit__(self, *args):
                elapsed = time.perf_counter() - self.start_time
                self.debug_system.log("PERF", f"Completed: {self.name} ({elapsed:.4f}s)")
                
        return TimeContext(self, operation_name)