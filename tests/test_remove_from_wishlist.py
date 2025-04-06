import pytest
from flask import url_for
from app import db, create_app  # ✅ Import create_app instead of app
from app.models import User, Product, Wishlist

@pytest.fixture
def app_instance():
    app = create_app()  # ✅ Create the app instance
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture
def setup_user_and_wishlist():
    user = User(
        
        name="Test User",
        phone="1234567890",
        email="test@example.com",
        password="test123",
        address="123 Street",
        state="State",
        city="City",
        pincode="123456",
        role="customer"
    )
    db.session.add(user)

    product = Product(
       
        product_name="Test Product",
        product_picture="test.jpg",
        current_price=100.0,
        previous_price=150.0,
        description="Test Desc",
        color="Red",
        category="Shoes"
    )
    db.session.add(product)
    db.session.commit()

    wishlist = Wishlist(user_id=user.id, product_id=product.id)
    db.session.add(wishlist)
    db.session.commit()

    return user, product

def test_remove_from_wishlist(client, setup_user_and_wishlist):
    user, product = setup_user_and_wishlist

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.post(f'/remove_from_wishlist/{product.id}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Product removed from wishlist!' in response.data
    assert Wishlist.query.filter_by(user_id=user.id, product_id=product.id).first() is None

def test_remove_from_wishlist_nonexistent(client, setup_user_and_wishlist):
    user, product = setup_user_and_wishlist

    Wishlist.query.delete()
    db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.post(f'/remove_from_wishlist/{product.id}', follow_redirects=True)

    assert response.status_code == 200
    assert b'Product not found in wishlist!' in response.data
