"""
基礎監控類別
所有監控腳本的基類，提供通用功能
"""

import os
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class BaseMonitor(ABC):
    """所有監控腳本的基類"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化監控器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.status_dir = Path('reports/status_history')
        self.status_dir.mkdir(parents=True, exist_ok=True)
    
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        載入 YAML 檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            解析後的資料字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.logger.warning(f"檔案不存在: {file_path}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"YAML 解析錯誤: {e}")
            return {}
    
    def save_yaml(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        儲存資料為 YAML 檔案
        
        Args:
            data: 要儲存的資料
            file_path: 檔案路徑
            
        Returns:
            是否成功
        """
        try:
            # 確保目錄存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            self.logger.error(f"儲存 YAML 失敗: {e}")
            return False
    
    def load_json(self, file_path: str) -> Dict[str, Any]:
        """
        載入 JSON 檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            解析後的資料字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"檔案不存在: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析錯誤: {e}")
            return {}
    
    def save_json(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        儲存資料為 JSON 檔案
        
        Args:
            data: 要儲存的資料
            file_path: 檔案路徑
            
        Returns:
            是否成功
        """
        try:
            # 確保目錄存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"儲存 JSON 失敗: {e}")
            return False
    
    def get_status_file_path(self, identifier: str) -> Path:
        """
        取得狀態檔案路徑
        
        Args:
            identifier: 識別符（如學校名稱或平台名稱）
            
        Returns:
            狀態檔案路徑
        """
        safe_name = identifier.replace(' ', '_').replace('/', '_')
        return self.status_dir / f"{safe_name}_status.json"
    
    def load_saved_status(self, identifier: str) -> Dict[str, Any]:
        """
        載入已儲存的狀態
        
        Args:
            identifier: 識別符
            
        Returns:
            狀態字典
        """
        status_file = self.get_status_file_path(identifier)
        if status_file.exists():
            return self.load_json(str(status_file))
        return {}
    
    def save_status(self, identifier: str, status: Dict[str, Any]) -> bool:
        """
        儲存狀態
        
        Args:
            identifier: 識別符
            status: 狀態字典
            
        Returns:
            是否成功
        """
        status['last_updated'] = datetime.now().isoformat()
        status_file = self.get_status_file_path(identifier)
        return self.save_json(status, str(status_file))
    
    def detect_changes(self, old_status: Dict[str, Any], new_status: Dict[str, Any]) -> bool:
        """
        偵測狀態變更
        
        Args:
            old_status: 舊狀態
            new_status: 新狀態
            
        Returns:
            是否有變更
        """
        # 移除時間戳記後比較
        old_copy = {k: v for k, v in old_status.items() if k != 'last_updated'}
        new_copy = {k: v for k, v in new_status.items() if k != 'last_updated'}
        
        return old_copy != new_copy
    
    def send_notification(self, message: Dict[str, Any]) -> bool:
        """
        發送通知
        
        Args:
            message: 通知訊息
            
        Returns:
            是否成功
        """
        try:
            # 這裡可以整合現有的 notifications/alert_system.py
            self.logger.info(f"通知: {message}")
            
            # TODO: 整合實際的通知系統
            # from notifications.alert_system import send_alert
            # send_alert(message)
            
            return True
        except Exception as e:
            self.logger.error(f"發送通知失敗: {e}")
            return False
    
    @abstractmethod
    def run(self) -> bool:
        """
        執行監控（子類別必須實作）
        
        Returns:
            是否成功
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"

