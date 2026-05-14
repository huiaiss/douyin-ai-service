import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from db.models import Customer, Conversation, Message, Knowledge, Product, Order, Analytics


class TestModels:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        from db.models import db
        db.init(":memory:")
        db.create_tables([
            Customer, Conversation, Message,
            Knowledge, Product, Order, Analytics
        ])
        yield
        db.close()

    def test_create_customer(self):
        c = Customer.create(platform_uid="douyin_123", nickname="测试用户")
        assert c.id == 1
        assert c.platform_uid == "douyin_123"
        assert c.order_count == 0

    def test_create_conversation_with_messages(self):
        c = Customer.create(platform_uid="douyin_456", nickname="买家A")
        convo = Conversation.create(customer=c, platform="douyin", status="active")
        msg = Message.create(convo=convo, role="user", content="我的快递到哪了")
        assert msg.convo_id == convo.id
        assert convo.customer.nickname == "买家A"

    def test_knowledge_embedding_storage(self):
        import numpy as np
        emb = np.random.randn(384).astype(np.float32)
        k = Knowledge.create(
            category="商品知识", title="退换货政策",
            content="7天无理由退换", embedding=emb.tobytes()
        )
        stored = np.frombuffer(k.embedding, dtype=np.float32)
        assert stored.shape == (384,)

    def test_product_with_tags(self):
        p = Product.create(
            name="测试商品", description="好用的商品",
            price=99.0, tags='["热销","新品"]'
        )
        import json
        assert json.loads(p.tags) == ["热销", "新品"]

    def test_order_relation(self):
        c = Customer.create(platform_uid="douyin_789", nickname="买家B")
        o = Order.create(customer=c, order_no="20240514001", status="已发货", amount=199.0)
        assert o.customer.nickname == "买家B"

    def test_analytics_aggregation(self):
        Analytics.create(
            date="2026-05-14", convo_count=10, avg_response=3.5,
            pos_ratio=0.8, top_questions='["发货时间","退换货"]'
        )
        today = Analytics.get(Analytics.date == "2026-05-14")
        assert today.convo_count == 10
