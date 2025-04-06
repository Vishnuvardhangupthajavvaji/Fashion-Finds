'''import pytest
from app import create_app, db
from app.models import User, Product, Cart, Order, OrderItem

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            #db.drop_all()

@pytest.fixture
def setup_user():
    user = User(
        
        name="Test User",
        phone="1234567890",
        email="testplaceorder8@example.com",
        password="testpass",
        address="123 Test Street",
        state="Test State",
        city="Test City",
        pincode="123456",
        role="customer",
        approved=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def setup_products():
    product = Product(
        product_name="Shirt",
        product_picture="shirt.jpg",
        current_price=100.0,
        previous_price=120.0,
        category="Men",
        color="Blue",
        rating=4,
        sale=True,
        discount=20,
        brand="FashionBrand",
        description="A stylish blue shirt"
    )
    db.session.add(product)
    db.session.commit()
    return product



@pytest.fixture
def setup_cart(setup_user, setup_products):
    cart_item = Cart(
        user_id=setup_user.id,
        product_id=setup_products.id,
        quantity=2
    )
    db.session.add(cart_item)
    db.session.commit()
    return cart_item


def test_place_order(client, setup_user, setup_products, setup_cart):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(setup_user.id)

    response = client.post('/place_order', data={
        "address_line_1": "123 Main St",
        "state": "Test State",
        "city": "Test City",
        "pincode": "123456",
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@example.com"
    })

    assert response.status_code == 200
    assert response.get_json()["success"] is True

    order = Order.query.filter_by(user_id=setup_user.id).first()
    assert order is not None
    assert order.total_price == 200.0

    item = OrderItem.query.filter_by(order_id=order.id).first()
    assert item.quantity == 2

    product = Product.query.get(setup_products.id)
    assert product.quantity == 48

    assert Cart.query.filter_by(user_id=setup_user.id).count() == 0'''
