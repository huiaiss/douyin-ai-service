from abc import ABC, abstractmethod
from typing import Dict, Any


class PlatformAdapter(ABC):
    """平台适配器抽象类"""
    platform_name: str = "base"

    @abstractmethod
    def parse_incoming(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析平台原始消息 → 统一 Message 格式"""
        ...

    @abstractmethod
    def format_outgoing(self, text: str, convo_id: str) -> Dict[str, Any]:
        """统一回复格式 → 平台可发送的格式"""
        ...
