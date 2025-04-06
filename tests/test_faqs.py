import pytest
from app import create_app,db
import json

@pytest.fixture
def app():
    app=create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield app
@pytest.fixture
def client(app):
    return app.test_client()

def test_faqs_get(client):
    response = client.get('/faqs')
    assert response.status_code == 200
    assert b"Frequently Asked Questions" in response.data

def test_faqs_post(client):
    data = {
        "question": "Do you ship internationally?",
        "answer": "Yes, we do!"
    }
    response = client.post('/faqs', data=json.dumps(data), content_type='application/json')
    assert response.status_code in (200, 201)
