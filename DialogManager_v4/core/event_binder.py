"""
DialogManager v4 - Event Binder

JSON定義イベントバインディングシステム
DESIGN.md準拠の宣言的イベント処理
"""

from typing import Dict, Any, Callable, List
from .debug_system import DebugSystem


class EventBinder:
    """JSON定義イベントバインディングシステム"""
    
    def __init__(self, debug: bool = True):
        self.event_mappings: Dict[str, str] = {}  # control.event -> action_name
        self.action_registry: Dict[str, Dict[str, Any]] = {}  # action_name -> action_def
        self.debug_system = DebugSystem("EventBinder") if debug else None
    
    def bind_events_from_json(self, events_def: Dict[str, str], actions_def: Dict[str, Dict[str, Any]]):
        """JSON定義からイベントバインディング設定"""
        if self.debug_system:
            self.debug_system.enter_context("bind_events_from_json", {
                "events_count": len(events_def),
                "actions_count": len(actions_def)
            })
        
        try:
            # イベントマッピング登録
            self.event_mappings.update(events_def)
            
            # アクション定義登録
            self.action_registry.update(actions_def)
            
            if self.debug_system:
                self.debug_system.log("SUCCESS", "Event binding completed")
                for event, action in events_def.items():
                    self.debug_system.log("BINDING", f"{event} -> {action}")
            
        except Exception as e:
            if self.debug_system:
                self.debug_system.error("Event binding failed", e)
            raise
        finally:
            if self.debug_system:
                self.debug_system.exit_context()
    
    def handle_event(self, control_id: str, event_type: str, event_data: Dict[str, Any] = None) -> Any:
        """イベント処理実行"""
        event_key = f"{control_id}.{event_type}"
        
        if self.debug_system:
            self.debug_system.enter_context("handle_event", {
                "event_key": event_key,
                "event_data": event_data
            })
        
        try:
            # イベントマッピング検索
            action_name = self.event_mappings.get(event_key)
            if not action_name:
                if self.debug_system:
                    self.debug_system.log("WARNING", f"No action bound to event: {event_key}")
                return None
            
            # アクション定義取得
            action_def = self.action_registry.get(action_name)
            if not action_def:
                if self.debug_system:
                    self.debug_system.log("ERROR", f"Action definition not found: {action_name}")
                return None
            
            if self.debug_system:
                self.debug_system.log("INFO", f"Executing action: {action_name}")
            
            # TODO: ActionEngineとの統合
            # result = action_engine.execute(action_def, context)
            
            return {"action": action_name, "result": "success"}
            
        except Exception as e:
            if self.debug_system:
                self.debug_system.error("Event handling failed", e)
            raise
        finally:
            if self.debug_system:
                self.debug_system.exit_context()
    
    def get_bound_events(self, control_id: str) -> List[str]:
        """特定コントロールにバインドされたイベント一覧取得"""
        bound_events = []
        prefix = f"{control_id}."
        
        for event_key in self.event_mappings.keys():
            if event_key.startswith(prefix):
                event_type = event_key[len(prefix):]
                bound_events.append(event_type)
        
        if self.debug_system:
            self.debug_system.log("INFO", f"Control {control_id} has {len(bound_events)} bound events")
        
        return bound_events
    
    def validate_bindings(self) -> List[str]:
        """イベントバインディングの妥当性検証"""
        errors = []
        
        if self.debug_system:
            self.debug_system.enter_context("validate_bindings")
        
        try:
            for event_key, action_name in self.event_mappings.items():
                # アクション存在チェック
                if action_name not in self.action_registry:
                    error = f"Action '{action_name}' not found for event '{event_key}'"
                    errors.append(error)
                    if self.debug_system:
                        self.debug_system.log("ERROR", error)
                
                # イベントキー形式チェック
                if '.' not in event_key:
                    error = f"Invalid event key format: '{event_key}' (should be 'control.event')"
                    errors.append(error)
                    if self.debug_system:
                        self.debug_system.log("ERROR", error)
            
            if self.debug_system:
                if errors:
                    self.debug_system.log("WARNING", f"Found {len(errors)} binding errors")
                else:
                    self.debug_system.log("SUCCESS", "All bindings are valid")
            
            return errors
            
        finally:
            if self.debug_system:
                self.debug_system.exit_context()
    
    def get_binding_summary(self) -> Dict[str, Any]:
        """バインディング状況のサマリー取得"""
        summary = {
            "total_events": len(self.event_mappings),
            "total_actions": len(self.action_registry),
            "events_by_control": {},
            "actions_by_type": {}
        }
        
        # コントロール別イベント集計
        for event_key in self.event_mappings.keys():
            if '.' in event_key:
                control_id = event_key.split('.')[0]
                summary["events_by_control"][control_id] = summary["events_by_control"].get(control_id, 0) + 1
        
        # アクションタイプ別集計
        for action_def in self.action_registry.values():
            action_type = action_def.get("type", "unknown")
            summary["actions_by_type"][action_type] = summary["actions_by_type"].get(action_type, 0) + 1
        
        return summary