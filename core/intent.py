import re


class IntentClassifier:
    """基于规则 + 关键词的意图分类器"""

    RULES = [
        ("order_query", r"快递|物流|发货|到哪|订单.*状态|什么时候.*到|查.*单|运单|跟踪"),
        ("after_sale", r"退款|退货|换货|退.*钱|售后|投诉|差评|坏了|质量|坑|骗"),
        ("product_inquiry", r"区别|哪个.*好|推荐|怎么.*用|规格|尺寸|颜色|材质|有没有|还有.*吗"),
        ("price_inquiry", r"多少钱|价格|优惠|便宜|打折|砍价|贵了"),
        ("greeting", r"你好|在吗|hi|hello|在不|亲在"),
    ]

    def classify(self, text: str) -> dict:
        for category, pattern in self.RULES:
            if re.search(pattern, text, re.IGNORECASE):
                return {"category": category, "confidence": 0.85}
        return {"category": "general", "confidence": 0.5}
