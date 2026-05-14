import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from api.knowledge import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)


@pytest.fixture(autouse=True)
def setup_db():
    from db.models import db, Knowledge
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db.init(tmp.name)
    db.connect()
    db.create_tables([Knowledge])
    yield
    db.close()
    try:
        os.unlink(tmp.name)
    except PermissionError:
        pass


@pytest.fixture
def client():
    return TestClient(app)


class TestKnowledgeAPI:
    def test_create_knowledge(self, client):
        resp = client.post("/api/knowledge", json={
            "category": "物流", "title": "发货时间",
            "content": "一般订单在48小时内发货"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "发货时间"
        assert data["id"] == 1

    def test_list_knowledge(self, client):
        client.post("/api/knowledge", json={
            "category": "物流", "title": "发货", "content": "48小时"
        })
        client.post("/api/knowledge", json={
            "category": "售后", "title": "退货", "content": "7天无理由"
        })
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_filter_by_category(self, client):
        client.post("/api/knowledge", json={
            "category": "物流", "title": "发货", "content": "48小时"
        })
        client.post("/api/knowledge", json={
            "category": "售后", "title": "退货", "content": "7天无理由"
        })
        resp = client.get("/api/knowledge?category=物流")
        assert len(resp.json()) == 1
        assert resp.json()[0]["category"] == "物流"

    def test_update_knowledge(self, client):
        client.post("/api/knowledge", json={
            "category": "物流", "title": "发货", "content": "48小时"
        })
        resp = client.put("/api/knowledge/1", json={
            "title": "发货时间更新", "content": "24小时内发货"
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "发货时间更新"

    def test_delete_knowledge(self, client):
        client.post("/api/knowledge", json={
            "category": "物流", "title": "发货", "content": "48小时"
        })
        resp = client.delete("/api/knowledge/1")
        assert resp.status_code == 200
        resp2 = client.get("/api/knowledge")
        assert len(resp2.json()) == 0

    def test_get_nonexistent(self, client):
        resp = client.get("/api/knowledge/999")
        assert resp.status_code == 404

    def test_create_invalid(self, client):
        resp = client.post("/api/knowledge", json={
            "title": "missing category"
        })
        assert resp.status_code == 422
