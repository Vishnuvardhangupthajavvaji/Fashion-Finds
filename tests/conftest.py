import pytest
from app import create_app,db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()



# python -m pytest tests\test_delivery_dashboard.py