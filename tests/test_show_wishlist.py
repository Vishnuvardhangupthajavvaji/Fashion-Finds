import warnings
import pytest
from flask import url_for
from app import create_app, db
from app.models import User, Product, Wishlist, Cart
from sqlalchemy.exc import SAWarning

# ✅ Suppress SQLAlchemy warnings
warnings.filterwarnings("ignore", category=SAWarning)

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_data(app):
    with app.app_context():
        # Avoid detached instance errors by using scoped session
        user = User.query.filter_by(email="testuser10@example.com").first()
        if not user:
            user = User(
                name="Test User",
                phone="9876543210",
                email="testuse10r@example.com",
                password="testpass",
                address="123 Street",
                state="TestState",
                city="TestCity",
                pincode="123456",
                role="customer"
            )
            db.session.add(user)
            db.session.commit()

        product = Product.query.filter_by(product_name="Test Product").first()
        if not product:
            product = Product(
                product_name="Test Product",
                product_picture="test.jpg",
                current_price=100.0,
                previous_price=150.0,
                description="Great Product",
                color="Red",
                rating=4,
                sale=False,
                discount=0,
                brand="TestBrand",
                category="Clothing"
            )
            db.session.add(product)
            db.session.commit()

        wishlist = Wishlist.query.filter_by(user_id=user.id, product_id=product.id).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user.id, product_id=product.id)
            db.session.add(wishlist)
            db.session.commit()

        return user.id, product.id  # ⚠️ Return IDs only

def test_move_to_cart(client, app, setup_data):
    user_id, product_id = setup_data  # Use IDs to avoid DetachedInstanceError

    # Simulate user login
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)

    response = client.post(f'/move_to_cart/{product_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first() is None
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        assert cart_item is not None
        assert cart_item.quantity == 1
