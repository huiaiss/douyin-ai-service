import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.message_handler import MessageHandler


class TestHandoff:
    @pytest.fixture
    def handler(self):
        return MessageHandler()

    def test_should_handoff_angry_user(self, handler):
        # 愤怒用户 + 要求人工
        assert handler._should_handoff("我要找人工客服！太差了！")

    def test_should_handoff_explicit_request(self, handler):
        assert handler._should_handoff("转人工")
        assert handler._should_handoff("人工客服")

    def test_should_not_handoff_normal(self, handler):
        assert not handler._should_handoff("这个什么时候发货")
        assert not handler._should_handoff("你好")

    def test_handoff_returns_escalated(self, handler):
        result = handler.process({
            "platform_uid": "douyin_test",
            "nickname": "测试用户",
            "content": "我要找人工客服，你们太差了",
            "convo_id": "test_handoff",
            "platform": "douyin",
        })
        assert result["handoff"] is True
        assert "人工" in result["reply"]
