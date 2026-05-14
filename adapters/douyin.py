import time
from typing import Dict, Any
from adapters.base import PlatformAdapter


class DouyinAdapter(PlatformAdapter):
    platform_name = "douyin"

    def parse_incoming(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        sender = raw_data.get("sender", {})
        return {
            "platform_uid": sender.get("uid", ""),
            "nickname": sender.get("nickname", ""),
            "content": raw_data.get("content", ""),
            "convo_id": raw_data.get("convo_id", ""),
            "timestamp": raw_data.get("timestamp", 0),
            "raw": raw_data,
        }

    def format_outgoing(self, text: str, convo_id: str) -> Dict[str, Any]:
        return {
            "type": "reply",
            "convo_id": convo_id,
            "content": text,
            "timestamp": int(time.time() * 1000),
        }
