import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# def test_update_cart_quantity_success(app, client):
#     product_id = 10
#     new_quantity = 3

#     class FakeProduct:
#         def __init__(self):
#             self.current_price = 100
#             self.discount = 10
#             self.id = product_id

#     class FakeCart:
#         def __init__(self):
#             self.quantity = 1
#             self.product_id = product_id
#             self.user_id = 1

#     fake_product = FakeProduct()
#     fake_cart = FakeCart()

#     user = MagicMock()
#     user.id = 1
#     user.is_authenticated = True

#     with app.app_context():
#         with patch('flask_login.utils._get_user', return_value=user), \
#              patch('app.views.request') as mock_request, \
#              patch('app.views.Cart.query') as mock_cart_query, \
#              patch('app.views.db') as mock_db, \
#              patch('app.views.Product') as mock_product:

#             # Mock request form
#             mock_request.form.get.return_value = str(new_quantity)

#             # Mock Cart.query.filter_by().first() to return the cart item
#             mock_cart_query.filter_by.return_value.first.return_value = fake_cart

#             # Mock db.session.query(...).join(...).filter(...).all() to return cart-product tuple
#             mock_db.session.query.return_value.join.return_value.filter.return_value.all.return_value = [
#                 (fake_cart, fake_product)
#             ]

#             response = client.post(f'/update_cart_quantity/{product_id}', data={'quantity': new_quantity})

#             # Set updated quantity manually for assertion
#             fake_cart.quantity = new_quantity

#             assert response.status_code == 200
#             json_data = response.get_json()

#             assert json_data["success"] is True
#             assert json_data["total_mrp"] == 300  # 3 * 100
#             assert json_data["discount_mrp"] == 30  # 3 * 10
#             assert json_data["total_amount"] == 270  # 300 - 30

def test_update_cart_quantity_success(app, client):
    product_id = 10
    new_quantity = 3

    class FakeProduct:
        def __init__(self):
            self.current_price = 100
            self.discount = 10
            self.id = product_id

    class FakeCart:
        def __init__(self):
            self.quantity = 1
            self.product_id = product_id
            self.user_id = 1

    fake_product = FakeProduct()
    fake_cart = FakeCart()

    user = MagicMock()
    user.id = 1
    user.is_authenticated = True

    with app.app_context():
        with patch('flask_login.utils._get_user', return_value=user), \
             patch('app.views.Cart.query') as mock_cart_query, \
             patch('app.views.db') as mock_db, \
             patch('app.views.Product') as mock_product:

            # Mock request form directly in the client.post call
            response = client.post(f'/update_cart_quantity/{product_id}', data={'quantity': new_quantity})

            # Mock Cart.query.filter_by().first() to return the cart item
            mock_cart_query.filter_by.return_value.first.return_value = fake_cart

            # Mock db.session.query(...).join(...).filter(...).all() to return cart-product tuple
            mock_db.session.query.return_value.join.return_value.filter.return_value.all.return_value = [
                (fake_cart, fake_product)
            ]

            # Set updated quantity manually for assertion
            fake_cart.quantity = new_quantity

            assert response.status_code == 200
            json_data = response.get_json()

            assert json_data["success"] is True
            assert json_data["total_mrp"] == 300  # 3 * 100
            assert json_data["discount_mrp"] == 30  # 3 * 10
            assert json_data["total_amount"] == 270  # 300 - 30