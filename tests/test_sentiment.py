import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.sentiment import SentimentAnalyzer


class TestSentimentAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()

    def test_negative_regex(self, analyzer):
        assert analyzer.analyze("太差了，东西是坏的，我要退款") == "负面"

    def test_positive_regex(self, analyzer):
        assert analyzer.analyze("太棒了，我很满意，谢谢") == "正面"

    def test_neutral_regex(self, analyzer):
        assert analyzer.analyze("这个什么时候发货") == "中性"

    def test_negative_strong(self, analyzer):
        assert analyzer.analyze("垃圾东西，骗人的，气死我了") == "负面"

    def test_positive_gratitude(self, analyzer):
        assert analyzer.analyze("感谢客服耐心解答，好评") == "正面"

    def test_empty_message(self, analyzer):
        assert analyzer.analyze("") == "中性"

    def test_llm_response_parsing(self, analyzer):
        """测试 LLM 返回不同格式时的解析结果"""
        assert analyzer._parse_llm_result("正面") == "正面"
        assert analyzer._parse_llm_result("负面") == "负面"
        assert analyzer._parse_llm_result("中性") == "中性"
        assert analyzer._parse_llm_result("你的情绪是正面的") == "正面"
        assert analyzer._parse_llm_result("用户情绪负面") == "负面"
        # 无效结果返回原始值，由 analyze() 回退到正则
        result = analyzer._parse_llm_result("这是一段无关文本")
        assert result not in {"正面", "负面", "中性"}
