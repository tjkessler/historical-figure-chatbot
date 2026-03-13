import pytest
import os
import tempfile
import shutil

from fastapi.testclient import TestClient
from backend.main import app
from backend.db import init_db


@pytest.fixture(scope="module")
def client():

    # Use a temp DB for testing
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "chatbot.db")
    # Patch DB_PATH
    import backend.db
    backend.db.DB_PATH = db_path
    # Init DB
    init_db()
    with TestClient(app) as c:
        yield c
    shutil.rmtree(temp_dir)


def test_create_persona(client):

    data = {"name": "Test User", "era": "Test Era", "bio": "Test Bio"}
    resp = client.post("/api/personas/", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["name"] == data["name"]
    assert result["era"] == data["era"]
    assert result["bio"] == data["bio"]
    assert "id" in result


def test_get_personas(client):

    resp = client.get("/api/personas/")
    assert resp.status_code == 200
    personas = resp.json()
    assert isinstance(personas, list)
    assert any(p["name"] == "Test User" for p in personas)


def test_get_persona_by_id(client):

    # Get first persona
    resp = client.get("/api/personas/")
    persona_id = resp.json()[0]["id"]
    resp2 = client.get(f"/api/personas/{persona_id}")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == persona_id


def test_update_persona(client):

    resp = client.get("/api/personas/")
    persona = resp.json()[0]
    persona_id = persona["id"]
    update = {
        "name": "Updated Name",
        "era": persona["era"],
        "bio": persona["bio"]
    }
    resp2 = client.put(f"/api/personas/{persona_id}", json=update)
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "Updated Name"


def test_delete_persona(client):

    resp = client.get("/api/personas/")
    persona_id = resp.json()[0]["id"]
    resp2 = client.delete(f"/api/personas/{persona_id}")
    assert resp2.status_code == 200
    # Should not find it anymore
    resp3 = client.get(f"/api/personas/{persona_id}")
    assert resp3.status_code == 404
