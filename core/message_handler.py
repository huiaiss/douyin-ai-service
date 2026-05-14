from typing import Dict, Any
from core.intent import IntentClassifier
from core.reply_generator import ReplyGenerator
from core.sentiment import SentimentAnalyzer
from core.knowledge_retriever import KnowledgeRetriever
from core.product_recommend import ProductRecommender
from api.llm import LLMRouter


class MessageHandler:
    """消息处理主流程：意图识别 → 情绪分析 → 知识检索/商品推荐 → LLM生成 → 改写"""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.reply_generator = ReplyGenerator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.knowledge_retriever = KnowledgeRetriever(load_model=False)
        self.product_recommender = ProductRecommender(load_model=False)
        self.llm = LLMRouter()

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        content = message.get("content", "")

        intent = self.intent_classifier.classify(content)
        sentiment = self.sentiment_analyzer.analyze(content)

        knowledge = self._retrieve_knowledge(content, intent["category"])

        products = []
        if intent["category"] in ("product_inquiry", "price_inquiry"):
            products = self._recommend_products(content)

        prompt = self._build_prompt(content, intent, sentiment, knowledge, products)

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

    def _retrieve_knowledge(self, content: str, category: str) -> list[dict]:
        if not self.knowledge_retriever._model:
            return []
        try:
            return self.knowledge_retriever.retrieve(content, top_k=2)
        except Exception:
            return []

    def _recommend_products(self, content: str) -> list[dict]:
        if not self.product_recommender._model:
            return []
        try:
            return self.product_recommender.recommend(content, top_k=3)
        except Exception:
            return []

    def _build_prompt(self, content: str, intent: dict, sentiment: str,
                      knowledge: list[dict], products: list[dict]) -> str:
        style = self.reply_generator.style_prompt
        base = f"""{style}
你是抖音电商客服。用户意图：{intent['category']}，情绪：{sentiment}。

用户消息：{content}
"""
        if knowledge:
            base += "\n相关知识：\n"
            for i, k in enumerate(knowledge, 1):
                base += f"{i}. {k['content']}\n"

        if products:
            base += "\n可推荐商品：\n"
            for i, p in enumerate(products, 1):
                base += f"{i}. {p['name']}（¥{p['price']}）- {p['description']}\n"

        base += "\n请生成一段简洁、自然、有帮助的回复。"
        if sentiment == "负面":
            base += "\n用户情绪不好，请优先安抚，然后解决问题。"
        return base
