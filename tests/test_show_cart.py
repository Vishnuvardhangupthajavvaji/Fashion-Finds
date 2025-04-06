import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        #db.drop_all()

@pytest.fixture
def client(app):  # Add the decorator
    """Create a test client for the app."""
    return app.test_client()

def test_example(client):
    """Sample test case"""
    response = client.get('/')
    assert response.status_code == 200