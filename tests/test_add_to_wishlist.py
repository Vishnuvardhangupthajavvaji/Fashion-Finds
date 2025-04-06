import pytest
from flask import url_for
from app import db, create_app  # Import create_app, not app
from app.models import User, Product, Wishlist

@pytest.fixture
def client():
    app = create_app()  # Create a new app instance
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()

@pytest.fixture
def setup_user_and_product():
    user = User(
       
        name="Wishlist User",
        phone="9876543210",
        email="wishlist10@example.com",
        password="testpass",
        address="Test Address",
        state="Test State",
        city="Test City",
        pincode="000000",
        role="customer"
    )
    product = Product(
        
        product_name="Wishlist Product",
        product_picture="product.jpg",
        current_price=200.0,
        previous_price=250.0,
        description="Test Product Description",
        color="Black",
        category="Accessories"
    )
    db.session.add_all([user, product])
    db.session.commit()
    return user, product

def test_add_to_wishlist_success(client, setup_user_and_product):
    user, product = setup_user_and_product

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.post(f'/add_to_wishlist/{product.id}', follow_redirects=True)
    assert response.status_code == 200
    wishlist_entry = Wishlist.query.filter_by(user_id=user.id, product_id=product.id).first()
    assert wishlist_entry is not None

def test_add_to_wishlist_duplicate(client, setup_user_and_product):
    user, product = setup_user_and_product

    existing = Wishlist(user_id=user.id, product_id=product.id)
    db.session.add(existing)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.post(f'/add_to_wishlist/{product.id}', follow_redirects=True)
    assert response.status_code == 200
    wishlist_items = Wishlist.query.filter_by(user_id=user.id, product_id=product.id).all()
    assert len(wishlist_items) == 1
