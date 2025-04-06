'''import pytest
from flask import session
from sqlalchemy import select
from app import create_app, db
from app.models import User, Product, Wishlist, Cart

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.test'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


def test_move_to_cart(client, app):
    with app.app_context():
        # Create test user
        user = User(
            name="Test User",
            phone="1234567890",
            email="movetest10@example.com",
            password="password",
            address="Test Address",
            state="Test State",
            city="Test City",
            pincode="123456",
            role="customer"
        )
        db.session.add(user)
        db.session.flush()  # Assign user.id without commit

        # Create test product
        product = Product(
            product_name="Move Test Product",
            product_picture="img.jpg",
            current_price=50.0,
            previous_price=60.0,
            description="desc",
            color="red",
            rating=4,
            sale=False,
            discount=0,
            brand="BrandX",
            category="Men"
        )
        db.session.add(product)
        db.session.flush()  # Assign product.id without commit

        # Add item to wishlist
        wishlist_item = Wishlist(user_id=user.id, product_id=product.id)
        db.session.add(wishlist_item)
        db.session.commit()

    # Simulate login using Flask-Login compatible session
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    # Call the move_to_cart route
    response = client.post(f'/move_to_cart/{product.id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        # Item should be removed from wishlist
        wishlist_check = Wishlist.query.filter_by(user_id=user.id, product_id=product.id).first()
        assert wishlist_check is None

        # Item should be added to cart
        cart_check = Cart.query.filter_by(user_id=user.id, product_id=product.id).first()
        assert cart_check is not None
        assert cart_check.quantity == 1'''
