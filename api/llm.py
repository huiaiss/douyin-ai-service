import logging
from config import Config

logger = logging.getLogger(__name__)

# Model name → provider mapping, built from config
MODEL_TO_PROVIDER: dict[str, str] = {}
PROVIDER_DEFAULT_MODEL: dict[str, str] = {}


def _build_mappings():
    MODEL_TO_PROVIDER[Config.PRIMARY_MODEL] = "deepseek"
    PROVIDER_DEFAULT_MODEL["deepseek"] = Config.PRIMARY_MODEL
    for model_name, provider, key, url in Config.FALLBACK_MODELS:
        if provider not in PROVIDER_DEFAULT_MODEL:
            PROVIDER_DEFAULT_MODEL[provider] = model_name
        MODEL_TO_PROVIDER[model_name] = provider


_build_mappings()


class LLMRouter:
    """LLM 路由：多模型调度 + 容灾降级"""

    def __init__(self):
        self._mock_responses: dict[str, str] = {}
        self._clients: dict[str, object] = {}
        self._init_clients()

    def _init_clients(self):
        from openai import OpenAI

        if Config.DEEPSEEK_API_KEY:
            self._clients["deepseek"] = OpenAI(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL,
            )
        if Config.QWEN_API_KEY:
            self._clients["qwen"] = OpenAI(
                api_key=Config.QWEN_API_KEY,
                base_url=Config.QWEN_BASE_URL,
            )
        if Config.KIMI_API_KEY:
            self._clients["kimi"] = OpenAI(
                api_key=Config.KIMI_API_KEY,
                base_url=Config.KIMI_BASE_URL,
            )

    def add_mock_response(self, prompt_contains: str, response: str):
        self._mock_responses[prompt_contains] = response

    def chat(
        self,
        user_message: str,
        system: str = "你是一个专业的抖音电商客服助手，请用中文回复。",
        model: str | None = None,
        mock: bool = False,
        use_real_api: bool = True,
        max_tokens: int = 1024,
    ) -> str:
        if mock or not use_real_api or not self._clients:
            for key, val in self._mock_responses.items():
                if key in user_message:
                    return val
            return self._mock_reply(user_message)

        target_model = model or Config.PRIMARY_MODEL
        target_provider = MODEL_TO_PROVIDER.get(target_model)

        # Build fallback chain: start with requested model, then others
        seen: set[str] = set()
        fallback_chain: list[tuple[str, str]] = []

        if target_provider and target_provider in self._clients:
            seen.add(target_provider)
            fallback_chain.append((target_provider, target_model))

        for model_name, provider, key, url in Config.FALLBACK_MODELS:
            if provider not in seen and provider in self._clients:
                seen.add(provider)
                fallback_chain.append((provider, model_name))

        for provider, model_name in fallback_chain:
            client = self._clients.get(provider)
            if not client:
                continue
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.7,
                    max_tokens=max_tokens,
                )
                return resp.choices[0].message.content
            except Exception:
                logger.warning("Provider %s failed, falling back", provider)
                continue

        return self._mock_reply(user_message)

    def _mock_reply(self, user_message: str) -> str:
        if "快递" in user_message or "物流" in user_message:
            return "您的订单目前正在运输中，预计1-3天内送达，请您耐心等待哦~"
        if "退货" in user_message or "退款" in user_message:
            return "您好，我们支持7天无理由退换货。请您在订单页面申请售后，我们会尽快为您处理。"
        if "发货" in user_message:
            return "亲，您的订单我们会在48小时内尽快发出，发货后会第一时间通知您~"
        return "感谢您的咨询，请问还有什么可以帮您的吗？"
