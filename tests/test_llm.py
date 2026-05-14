import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from api.llm import LLMRouter


class TestLLMRouter:
    @pytest.fixture
    def router(self):
        return LLMRouter()

    def test_mock_reply_generation(self, router):
        router.add_mock_response("test-prompt", "这是测试回复")
        result = router.chat("test-prompt", mock=True)
        assert result == "这是测试回复"

    def test_mock_sentiment_analysis(self, router):
        router.add_mock_response("sentiment-prompt", "负面")
        result = router.chat("sentiment-prompt", mock=True)
        assert result == "负面"

    def test_mock_fallback_on_empty_api_key(self, router):
        result = router.chat("任何问题", use_real_api=False)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_system_prompt(self, router):
        result = router.chat(
            "用户消息",
            system="你是客服助手",
            mock=True
        )
        assert isinstance(result, str)
        assert len(result) > 0
