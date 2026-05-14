import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
from core.knowledge_retriever import KnowledgeRetriever


class FakeRetriever(KnowledgeRetriever):
    """Test retriever that returns pre-set embeddings instead of using real model"""

    def __init__(self):
        super().__init__(load_model=False)
        self._fake_embedding = None

    def set_embedding(self, vec):
        self._fake_embedding = np.asarray(vec, dtype=np.float32)

    def encode(self, text):
        return self._fake_embedding


class TestKnowledgeRetriever:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        from db.models import db, Knowledge
        db.init(":memory:")
        db.create_tables([Knowledge])
        Knowledge.create(
            category="物流", title="发货时间",
            content="一般订单在48小时内发货，节假日顺延。",
            embedding=np.array([1.0, 0.0, 0.0], dtype=np.float32).tobytes()
        )
        Knowledge.create(
            category="售后", title="退换货政策",
            content="支持7天无理由退换货，请在订单页面申请。",
            embedding=np.array([0.0, 1.0, 0.0], dtype=np.float32).tobytes()
        )
        Knowledge.create(
            category="物流", title="快递查询",
            content="您可以在订单详情页查看物流信息。",
            embedding=np.array([1.0, 0.1, 0.0], dtype=np.float32).tobytes()
        )
        yield
        db.close()

    @pytest.fixture
    def retriever(self):
        return FakeRetriever()

    def test_retrieve_top_match(self, retriever):
        retriever.set_embedding([1.0, 0.0, 0.0])
        results = retriever.retrieve("发货要多久", top_k=1)
        assert len(results) == 1
        assert results[0]["title"] == "发货时间"
        assert results[0]["score"] > 0.9

    def test_retrieve_multiple(self, retriever):
        retriever.set_embedding([1.0, 0.0, 0.0])
        results = retriever.retrieve("快递", top_k=3)
        assert len(results) == 3
        assert results[0]["score"] >= results[1]["score"]

    def test_retrieve_filters_by_category(self, retriever):
        retriever.set_embedding([0.0, 1.0, 0.0])
        results = retriever.retrieve("退款", top_k=3, category="售后")
        assert len(results) == 1
        assert results[0]["title"] == "退换货政策"

    def test_retrieve_low_score_filtered(self, retriever):
        retriever.set_embedding([-1.0, -1.0, -1.0])
        results = retriever.retrieve("完全不相关", top_k=3, min_score=0.3)
        assert len(results) == 0

    def test_retrieve_handles_empty_db(self, retriever):
        from db.models import Knowledge
        Knowledge.delete().execute()
        retriever.set_embedding([1.0, 0.0, 0.0])
        results = retriever.retrieve("测试", top_k=3)
        assert results == []
