'''import pytest
from flask import url_for
from app import create_app, db
from app.models import Product, User, Order, OrderItem

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost.localdomain",  # Needed for url_for
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        #db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def create_user():
    user = User(id=1,name="checkoutuser@example.com" email="test@example.com", password="hashed_password")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def create_products():
    product1 = Product(product_name="Shirt", price=50.0, quantity=10)
    product2 = Product(product_name="Pants", price=70.0, quantity=5)
    db.session.add_all([product1, product2])
    db.session.commit()
    return [product1, product2]

def test_checkout_with_items(app, client, create_user, create_products):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(create_user.id)  # Simulate login
        sess["cart"] = {
            str(create_products[0].id): 2,
            str(create_products[1].id): 1
        }

    with app.test_request_context():
        url = url_for("views.checkout")

    response = client.post(url, follow_redirects=True)
    assert response.status_code == 200
    assert b"Order placed successfully" in response.data

def test_checkout_with_empty_cart(app, client, create_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(create_user.id)
        sess["cart"] = {}

    with app.test_request_context():
        url = url_for("views.checkout")

    response = client.post(url, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your cart is empty" in response.data'''
