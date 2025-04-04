
from app.models import Product


def test_products_count(client,app):
    with app.app_context():
        product = Product.query.all()
        assert len(product) > 0
        


def test_admin_page(client):
    response = client.get('/admin/')
    assert response.status_code == 200


def test_add_product_page(client):
    response = client.get('/admin/add-product')
    assert response.status_code == 200


def test_view_products_page(client):
    response = client.get('/admin/view-products')
    assert response.status_code == 200

def test_update_item_page(client,app):
    with app.app_context():
        product = Product.query.first()
        assert product is not None
    response = client.get(f'/admin/update-item/{product.id}')
    assert response.status_code == 200

