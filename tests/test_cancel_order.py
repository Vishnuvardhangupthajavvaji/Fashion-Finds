import pytest
from flask import url_for
from app import create_app, db
from app.models import Order, User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost.localdomain"  # Fix for url_for in tests
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
    user = User(
        
        name="Test User",
        phone="9999999999",
        email="test8@example.com",
        password="hashed_password",
        address="123 Test Lane",
        state="TestState",
        city="TestCity",
        pincode="123456",
        role="customer"
    )
    db.session.add(user)
    db.session.commit()
    return user




from datetime import datetime, timezone

@pytest.fixture
def create_order(create_user):
    order = Order(
        
        user_id=create_user.id,
        total_price=100.0,
        status="Pending",
        customer_name=create_user.name,
        address_line_1=create_user.address,
        state=create_user.state,
        city=create_user.city,
        pincode=create_user.pincode,
        mail=create_user.email,
        order_date=datetime.now(timezone.utc)  # optional, but explicit
    )
    db.session.add(order)
    db.session.commit()
    return order


def test_cancel_order_success(app, client, create_user, create_order):
    """Test that a user can successfully cancel their own order."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(create_user.id)  # Simulate login

    with app.test_request_context():
        url = url_for("views.cancel_order", order_id=create_order.id)

    response = client.post(url, follow_redirects=True)

    assert response.status_code == 200
    updated_order = Order.query.get(create_order.id)
    assert updated_order.status == "Cancelled"
