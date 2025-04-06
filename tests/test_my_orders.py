'''import pytest
from flask import url_for
from app import app as flask_app, db
from app.models import User, Order, OrderItem, Product

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.test_client() as client:
        with flask_app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def create_user():
    user = User(
        id=1,
        name="Test User",
        phone="1234567890",
        email="test@example.com",
        password="hashed_password",
        address="123 Test Lane",
        state="TestState",
        city="TestCity",
        pincode="123456",
        role="customer",
        approved=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def create_orders(create_user):
    order1 = Order(
        id=1,
        user_id=create_user.id,
        total_price=50.0,
        status="Pending",
        customer_name="John Doe",
        address_line_1="123 Test Street",
        state="TestState",
        city="TestCity",
        pincode="123456",
        mail="john@example.com"
    )
    order2 = Order(
        id=2,
        user_id=create_user.id,
        total_price=80.0,
        status="Shipped",
        customer_name="Jane Smith",
        address_line_1="456 Demo Ave",
        state="DemoState",
        city="DemoCity",
        pincode="654321",
        mail="jane@example.com"
    )
    db.session.add_all([order1, order2])
    db.session.commit()
    return [order1, order2]

@pytest.fixture
def create_order_items(create_orders):
    product1 = Product(id=1, product_name="T-Shirt", quantity=10)
    product2 = Product(id=2, product_name="Jeans", quantity=5)

    db.session.add_all([product1, product2])
    db.session.commit()

    order_item1 = OrderItem(order_id=create_orders[0].id, product_id=product1.id, quantity=2, unit_price=25.0, subtotal=50.0)
    order_item2 = OrderItem(order_id=create_orders[1].id, product_id=product2.id, quantity=1, unit_price=80.0, subtotal=80.0)

    db.session.add_all([order_item1, order_item2])
    db.session.commit()
    return [order_item1, order_item2]

def test_my_orders(client, create_user, create_orders, create_order_items):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(create_user.id)

    response = client.get(url_for('views.my_orders'))
    assert response.status_code == 200
    assert b"Pending" in response.data
    assert b"Shipped" in response.data
    assert b"T-Shirt" in response.data
    assert b"Jeans" in response.data'''
