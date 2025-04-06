'''import pytest
from flask import session
from app import create_app, db
from app.models import Product, Cart

# Disable all warnings
pytestmark = pytest.mark.filterwarnings("ignore")

@pytest.fixture
def app():
    """Configure test application with all required fields"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
    
    yield app

import pytest
from flask import session
from app import create_app, db
from app.models import Product, Cart, User  # Ensure User is imported

# Disable all warnings
pytestmark = pytest.mark.filterwarnings("ignore")

@pytest.fixture
def app():
    """Configure test application with all required fields"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
    
    yield app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def init_database(app):
    """Initialize database with complete test data"""
    with app.app_context():
        # Clear all tables
        db.session.query(Cart).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create test user (only if not exists)
        if not db.session.get(User, 1):
            user = User(id=1, email="test9@example.com", password="test123456")
            db.session.add(user)

        # Create test product
        product = Product(
            id=1,
            product_name="Test Product",
            product_picture="default.jpg",
            current_price=100.0,
            previous_price=120.0,
            description="Test description",
            color="red",
            category="electronics",
            rating=4,
            sale=False,
            discount=0
        )
        db.session.add(product)

        db.session.commit()

    yield 1  # Product ID

    with app.app_context():
        db.session.rollback()



def test_remove_from_cart_logged_out(client, init_database):
    """Test unauthorized access handling"""
    response = client.post("/cart/remove/1", follow_redirects=False)
    assert response.status_code in [302, 401, 404], f"Unexpected status: {response.status_code}"

def test_remove_nonexistent_product(client, init_database):
    """Test invalid product handling"""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    # Use a definitely non-existent product ID
    invalid_product_id = 999
    response = client.post(f"/cart/remove/{invalid_product_id}", follow_redirects=False)
    assert response.status_code in [404, 400, 302], f"Unexpected status: {response.status_code}"'''
