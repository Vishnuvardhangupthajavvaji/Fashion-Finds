import pytest
from flask import session
from sqlalchemy import select
from app import create_app, db
from app.models import User, Product, Cart

# ✅ Setup Flask app and reset DB on each test
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.test'
    })

    with app.app_context():
        #db.drop_all()
        db.create_all()
        yield app
        db.session.remove()

# ✅ Create test client
@pytest.fixture
def client(app):
    return app.test_client()

# ✅ Seed fresh data for every test
import uuid
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def init_database(app):
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(
                name="Test User",
                phone="1234567890",
                email="test@example.com",
                password="password",
                address="123 Test Street",
                state="TestState",
                city="TestCity",
                pincode="123456",
                role="customer"
            )
            db.session.add(user)
            db.session.flush()  # assigns user.id

        product = Product.query.filter_by(product_name="Test Product").first()
        if not product:
            product = Product(
                product_name="Test Product",
                product_picture="test.jpg",
                current_price=100.0,
                previous_price=120.0,
                description="Test description",
                color="blue",
                rating=4,
                sale=False,
                discount=0,
                brand="TestBrand",
                category="Kids"
            )
            db.session.add(product)
            db.session.flush()  # assigns product.id

        db.session.commit()
        return {"user_id": user.id, "product_id": product.id}

def test_add_to_cart_logged_in(client, app, init_database):
    user_id = init_database["user_id"]
    product_id = init_database["product_id"]

    with client.session_transaction() as sess:
        sess['id'] = user_id

    response = client.post('/add_to_cart', json={'product_id': product_id})
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        with app.app_context():
            cart_item = db.session.scalar(
                select(Cart).where(
                    Cart.user_id == user_id,
                    Cart.product_id == product_id
                )
            )
            assert cart_item is not None
