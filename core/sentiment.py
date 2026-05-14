import re
from api.llm import LLMRouter


class SentimentAnalyzer:
    """情绪分析：优先 LLM，回退正则"""

    NEGATIVE_RE = re.compile(r"差|坏|烂|投诉|退款|退货|坑|骗|气|垃圾|恶心|无语|太.*不|垃圾|假的")
    POSITIVE_RE = re.compile(r"好|棒|赞|满意|喜欢|谢谢|感谢|好评|不错|可以|行|OK")

    def __init__(self):
        self.llm = LLMRouter()

    VALID_SENTIMENTS = {"正面", "负面", "中性"}

    def analyze(self, text: str) -> str:
        if not text or not text.strip():
            return "中性"
        if self.llm._clients:
            result = self.analyze_llm(text)
            if result in self.VALID_SENTIMENTS:
                return result
        return self._regex_analyze(text)

    def analyze_llm(self, text: str) -> str:
        result = self.llm.chat(
            text,
            system="你是一个情绪分析助手。只回复一个词：正面、负面或中性。不要回复其他内容。",
            max_tokens=8,
        )
        return self._parse_llm_result(result)

    def _parse_llm_result(self, result: str) -> str:
        result = result.strip()
        if "负面" in result:
            return "负面"
        if "正面" in result:
            return "正面"
        if "中性" in result:
            return "中性"
        return result

    def _regex_analyze(self, text: str) -> str:
        if self.NEGATIVE_RE.search(text):
            return "负面"
        if self.POSITIVE_RE.search(text):
            return "正面"
        return "中性"
