import pytest
from app import create_app, db
from app.models import Product

@pytest.fixture
def app():
    app = create_app()  # ✅ No argument passed here
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        #db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_products(app):
    product1 = Product(
        product_name="T-shirt",
        product_picture="tshirt.jpg",
        current_price=19.99,
        previous_price=29.99,
        description="A nice cotton t-shirt",
        color="Blue",
        rating=4,
        sale=True,
        discount=33,
        brand="Puma",
        category="Women"
    )
    product2 = Product(
        product_name="Sneakers",
        product_picture="sneakers.jpg",
        current_price=49.99,
        previous_price=69.99,
        description="Comfortable running shoes",
        color="Black",
        rating=5,
        sale=True,
        discount=28,
        brand="Adidas",
        category="Shoes"
    )
    db.session.add_all([product1, product2])
    db.session.commit()

def test_products_by_category(client, sample_products):
    response = client.get('/category/Women')
    assert response.status_code == 200
    assert b"T-shirt" in response.data
    assert b"Sneakers" not in response.data
