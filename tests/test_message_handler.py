import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.message_handler import MessageHandler
from core.intent import IntentClassifier
from core.reply_generator import ReplyGenerator


class TestIntentClassifier:
    def test_order_intent(self):
        c = IntentClassifier()
        result = c.classify("我的快递到哪了？")
        assert result["category"] == "order_query"

    def test_refund_intent(self):
        c = IntentClassifier()
        result = c.classify("我要退款退货")
        assert result["category"] == "after_sale"

    def test_product_intent(self):
        c = IntentClassifier()
        result = c.classify("这个和那个有什么区别？")
        assert result["category"] == "product_inquiry"

    def test_greeting_intent(self):
        c = IntentClassifier()
        result = c.classify("你好在吗")
        assert result["category"] == "greeting"

    def test_general_fallback(self):
        c = IntentClassifier()
        result = c.classify("今天天气不错")
        assert result["category"] == "general"
        assert result["confidence"] == 0.5


class TestReplyGenerator:
    def test_rewrite_differs_from_original(self):
        g = ReplyGenerator()
        original = "亲，您的订单预计48小时内发货哦~"
        rewritten = g.rewrite(original)
        assert len(rewritten) > 0
        assert rewritten != original

    def test_style_rotation(self):
        g = ReplyGenerator()
        styles = set()
        for _ in range(10):
            g.rotate_style()
            styles.add(g.current_style)
        assert len(styles) >= 2

    def test_style_prompt_not_empty(self):
        g = ReplyGenerator()
        assert len(g.style_prompt) > 0


class TestMessageHandler:
    @pytest.fixture
    def handler(self):
        return MessageHandler()

    def test_process_order_query(self, handler):
        result = handler.process({
            "platform_uid": "douyin_test",
            "nickname": "测试用户",
            "content": "我的快递到哪里了",
            "convo_id": "test_001",
            "platform": "douyin",
        })
        assert "reply" in result
        assert len(result["reply"]) > 0
        assert result["intent"] == "order_query"

    def test_process_complaint_has_sentiment(self, handler):
        result = handler.process({
            "platform_uid": "douyin_test",
            "nickname": "测试用户",
            "content": "太差了！东西是坏的，我要投诉！",
            "convo_id": "test_002",
            "platform": "douyin",
        })
        assert "reply" in result
        assert result["sentiment"] == "负面"

    def test_process_greeting(self, handler):
        result = handler.process({
            "platform_uid": "douyin_test",
            "nickname": "测试用户",
            "content": "你好",
            "convo_id": "test_003",
            "platform": "douyin",
        })
        assert result["intent"] == "greeting"
        assert len(result["reply"]) > 0

    def test_process_returns_convo_id(self, handler):
        result = handler.process({
            "platform_uid": "douyin_test",
            "nickname": "测试用户",
            "content": "什么时候发货",
            "convo_id": "test_004",
            "platform": "douyin",
        })
        assert result["convo_id"] == "test_004"
