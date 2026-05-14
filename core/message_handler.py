import re
from typing import Dict, Any
from core.intent import IntentClassifier
from core.reply_generator import ReplyGenerator
from api.llm import LLMRouter


class MessageHandler:
    """消息处理主流程：意图识别 → 情绪分析 → LLM生成 → 改写"""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.reply_generator = ReplyGenerator()
        self.llm = LLMRouter()

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        content = message.get("content", "")

        intent = self.intent_classifier.classify(content)
        sentiment = self._basic_sentiment(content)
        prompt = self._build_prompt(content, intent, sentiment)

        raw_reply = self.llm.chat(prompt, mock=(not self.llm._clients))

        self.reply_generator.rotate_style()
        final_reply = self.reply_generator.rewrite(raw_reply)

        return {
            "reply": final_reply,
            "intent": intent["category"],
            "sentiment": sentiment,
            "convo_id": message.get("convo_id", ""),
            "platform_uid": message.get("platform_uid", ""),
        }

    def _basic_sentiment(self, text: str) -> str:
        if re.search(r"差|坏|烂|投诉|退款|退货|坑|骗|气|垃圾|恶心|无语", text):
            return "负面"
        if re.search(r"好|棒|赞|满意|喜欢|谢谢|感谢|好评|不错", text):
            return "正面"
        return "中性"

    def _build_prompt(self, content: str, intent: dict, sentiment: str) -> str:
        style = self.reply_generator.style_prompt
        base = f"""{style}
你是抖音电商客服。用户意图：{intent['category']}，情绪：{sentiment}。

用户消息：{content}

请生成一段简洁、自然、有帮助的回复。"""
        if sentiment == "负面":
            base += "\n用户情绪不好，请优先安抚，然后解决问题。"
        return base
