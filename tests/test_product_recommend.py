import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
from core.product_recommend import ProductRecommender


class FakeRecommender(ProductRecommender):
    def __init__(self):
        super().__init__(load_model=False)
        self._fake_embedding = None

    def set_embedding(self, vec):
        self._fake_embedding = np.asarray(vec, dtype=np.float32)

    def encode(self, text):
        return self._fake_embedding


class TestProductRecommender:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        from db.models import db, Product
        db.init(":memory:")
        db.create_tables([Product])
        Product.create(
            name="无线蓝牙耳机", description="降噪蓝牙耳机，续航24小时",
            price=199.0, category="数码", tags='["热销","新品"]',
            embedding=np.array([1.0, 0.0, 0.0], dtype=np.float32).tobytes()
        )
        Product.create(
            name="手机壳", description="硅胶防摔手机壳，多色可选",
            price=29.9, category="配件", tags='["热销"]',
            embedding=np.array([0.0, 1.0, 0.0], dtype=np.float32).tobytes()
        )
        Product.create(
            name="蓝牙运动耳机", description="运动款蓝牙耳机，防水防汗",
            price=149.0, category="数码", tags='["运动","新品"]',
            embedding=np.array([0.9, 0.05, 0.0], dtype=np.float32).tobytes()
        )
        yield
        db.close()

    @pytest.fixture
    def recommender(self):
        return FakeRecommender()

    def test_recommend_semantic_match(self, recommender):
        recommender.set_embedding([1.0, 0.0, 0.0])
        results = recommender.recommend("蓝牙耳机", top_k=2)
        assert len(results) == 2
        assert results[0]["name"] == "无线蓝牙耳机"
        assert results[0]["score"] > 0.9

    def test_recommend_filters_by_category(self, recommender):
        recommender.set_embedding([1.0, 0.0, 0.0])
        results = recommender.recommend("耳机", top_k=3, category="数码")
        assert len(results) == 2
        assert all(r["category"] == "数码" for r in results)

    def test_recommend_filters_by_max_price(self, recommender):
        recommender.set_embedding([1.0, 0.0, 0.0])
        results = recommender.recommend("耳机", top_k=3, max_price=180.0)
        assert len(results) == 2  # 149 and 29.9, not 199
        assert all(r["price"] <= 180.0 for r in results)

    def test_recommend_returns_all_fields(self, recommender):
        recommender.set_embedding([1.0, 0.0, 0.0])
        results = recommender.recommend("耳机", top_k=1)
        assert results[0]["name"] == "无线蓝牙耳机"
        assert results[0]["price"] == 199.0
        assert results[0]["description"]
        assert results[0]["tags"]
