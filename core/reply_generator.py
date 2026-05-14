import random


class ReplyGenerator:
    """回复生成 + 同义改写 + 风格轮换"""

    STYLES = ["专业简洁", "亲切活泼", "正式稳重"]
    STYLE_PROMPTS = {
        "专业简洁": "使用专业且简洁的语气，直接回答问题。",
        "亲切活泼": "使用亲切、活泼、带一点可爱的语气，适当使用\"亲\"、\"呢\"、\"哦\"等词。",
        "正式稳重": "使用正式稳重的语气，用\"您\"称呼客户。",
    }

    REORDER_PATTERNS = [
        lambda t: t,
        lambda t: t.replace("哦~", "呢~") if "哦~" in t else t,
        lambda t: t.replace("亲", "亲爱的") if "亲" in t and "亲爱的" not in t else t,
    ]

    def __init__(self):
        self.current_style = "专业简洁"
        self._style_index = 0

    def rotate_style(self):
        self._style_index = (self._style_index + 1) % len(self.STYLES)
        self.current_style = self.STYLES[self._style_index]

    @property
    def style_prompt(self) -> str:
        return self.STYLE_PROMPTS[self.current_style]

    def rewrite(self, text: str) -> str:
        rule = random.choice(self.REORDER_PATTERNS)
        rewritten = rule(text)
        if rewritten == text:
            suffixes = ["~", "！", "，有问题随时联系我。"]
            if not rewritten.endswith(tuple(suffixes)):
                rewritten += random.choice(suffixes)
        return rewritten
