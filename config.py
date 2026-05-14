import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = os.getenv("HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    WS_PORT = int(os.getenv("WS_PORT", "8765"))

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
    KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")

    # 模型配置
    PRIMARY_MODEL = "deepseek-chat"  # V4-Flash
    EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# Compute fallback list after class is fully defined
Config.FALLBACK_MODELS = [
    ("deepseek-chat", "deepseek", Config.DEEPSEEK_API_KEY, Config.DEEPSEEK_BASE_URL),
    ("qwen-max", "qwen", Config.QWEN_API_KEY, Config.QWEN_BASE_URL),
    ("moonshot-v1-8k", "kimi", Config.KIMI_API_KEY, Config.KIMI_BASE_URL),
]
