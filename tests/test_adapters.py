import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from adapters.douyin import DouyinAdapter


class TestDouyinAdapter:
    def test_parse_message(self):
        raw = {
            "type": "message",
            "sender": {"uid": "douyin_abc", "nickname": "测试买家"},
            "content": "这个商品什么时候发货？",
            "convo_id": "conv_001",
            "timestamp": 1778730000,
        }
        adapter = DouyinAdapter()
        msg = adapter.parse_incoming(raw)
        assert msg["platform_uid"] == "douyin_abc"
        assert msg["nickname"] == "测试买家"
        assert msg["content"] == "这个商品什么时候发货？"
        assert msg["convo_id"] == "conv_001"

    def test_format_reply(self):
        adapter = DouyinAdapter()
        formatted = adapter.format_outgoing(
            text="亲，48小时内发货哦~",
            convo_id="conv_001",
        )
        assert formatted["type"] == "reply"
        assert formatted["convo_id"] == "conv_001"
        assert "亲，48小时内发货哦~" in formatted["content"]
