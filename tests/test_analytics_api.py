import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.analytics import router


app = FastAPI()
app.include_router(router)


@pytest.fixture(autouse=True)
def setup_db():
    from db.models import db, Analytics
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db.init(tmp.name)
    db.connect()
    db.create_tables([Analytics])
    yield
    db.close()
    try:
        os.unlink(tmp.name)
    except PermissionError:
        pass


@pytest.fixture
def client():
    return TestClient(app)


class TestAnalyticsAPI:
    def test_record_and_get(self, client):
        resp = client.post("/api/analytics/record", json={
            "conversations": 1, "response_time": 3.5, "sentiment": "正面",
            "question": "发货时间"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["convo_count"] == 1

    def test_get_today_empty(self, client):
        resp = client.get("/api/analytics")
        assert resp.status_code == 200
        assert resp.json()["convo_count"] == 0

    def test_multiple_records_aggregate(self, client):
        for i in range(3):
            client.post("/api/analytics/record", json={
                "conversations": 1, "response_time": 2.0,
                "sentiment": "正面", "question": f"问题{i}"
            })
        resp = client.get("/api/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["convo_count"] == 3
        assert data["pos_ratio"] == 1.0
