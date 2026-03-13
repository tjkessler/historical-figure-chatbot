import pytest
from fastapi.testclient import TestClient
import os


os.environ["LLM_PROVIDER"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["HUGGINGFACE_API_TOKEN"] = ""
os.environ["HUGGINGFACE_MODEL"] = ""


from backend.main import app
from backend.db import init_db


@pytest.fixture(scope="module")
def client():

    # Use a temp DB for testing
    import os, tempfile, shutil
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "chatbot.db")
    import backend.db
    backend.db.DB_PATH = db_path
    init_db()
    with TestClient(app) as c:
        yield c
    shutil.rmtree(temp_dir)


def test_chat_with_custom_persona(client):

    data = {
        "persona": "custom",
        "message": "What is your philosophy of life?",
        "custom_bio": "A wise philosopher who values knowledge and kindness.",
        "history": [
            {"role": "user", "message": "Hello!"},
            {"role": "bot", "message": "Greetings, seeker of wisdom."}
        ]
    }
    resp = client.post("/api/chat/", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert "prompt" in result
    assert result["response"].startswith("[LLM integration not configured") or result["response"].startswith("[LLM error")
    assert "philosophy" in result["prompt"].lower()


def test_chat_with_persona_id(client):

    # Create a persona
    persona_data = {"name": "Test Persona", "era": "Test Era", "bio": "Test Bio"}
    resp = client.post("/api/personas/", json=persona_data)
    assert resp.status_code == 200
    persona_id = resp.json()["id"]
    chat_data = {
        "persona": str(persona_id),
        "message": "Tell me about your era.",
        "history": []
    }
    resp2 = client.post("/api/chat/", json=chat_data)
    assert resp2.status_code == 200
    result = resp2.json()
    assert "prompt" in result
    assert result["response"].startswith("[LLM integration not configured") or result["response"].startswith("[LLM error")
    assert "test era" in result["prompt"].lower()


def test_chat_invalid_persona_id(client):

    chat_data = {
        "persona": "999999",
        "message": "Hello?"
    }
    resp = client.post("/api/chat/", json=chat_data)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Persona not found"


def test_chat_custom_persona_missing_bio(client):

    chat_data = {
        "persona": "custom",
        "message": "Hi"
    }
    resp = client.post("/api/chat/", json=chat_data)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Custom bio is required for custom persona"
