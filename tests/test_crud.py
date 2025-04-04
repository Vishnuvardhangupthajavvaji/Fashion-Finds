from app import db
from app.models import Product
from bs4 import BeautifulSoup 
import io



def get_csrf_token(client, url):
    response = client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_exist = soup.find('input', {'name': 'csrf_token'})
    if csrf_exist:
        return csrf_exist['value']
    else:
        raise ValueError(f' CSRF token is missing in the given path {url}')


def login_admin(client):
    response = client.post('/auth/login', data={
        'email': 'admin@fashionfinds.com',
        'password': '123456'
    }, follow_redirects=True)
    
    assert b'Logout' in response.data or response.status_code == 200  # Adjust based on what your dashboard shows after login

    return response



# def test_add_product(client, app):
#     login_admin(client)  # <-- Make sure the admin is logged in

#     with app.app_context():
#         initial_count = Product.query.count()

#     response = client.get('/admin/add_products')
#     print(response.status_code)
#     print(response.headers)
#     csrf_token = get_csrf_token(client, '/admin/add_products')
#     dummy_file = (io.BytesIO(b'test file content'), "test_image.png")

#     data = {
#         'csrf_token': csrf_token,
#         'product_name': 'Test Product',
#         'current_price': 99.99,
#         'previous_price': 120.00,
#         'description': 'A sample product',
#         'category': 'Fashion',
#         'sale': 'y',
#         'discount': 10,
#         'brand': 'TestBrand',
#         'color': 'Red',
#         'product_picture': dummy_file,
#         'sizes-0-size': 'S',
#         'sizes-0-quantity': 5
#     }

#     response = client.post('/admin/add_products', data=data, content_type='multipart/form-data', follow_redirects=True)

#     assert b"added successfully" in response.data
#     assert response.status_code == 200

#     with app.app_context():
#         current_count = Product.query.count()
#         assert current_count == initial_count + 1



# def test_update_product(client, app):
#     login_admin(client)  # Ensure the admin is logged in

#     with app.app_context():
#         product = Product.query.order_by(Product.id.desc()).first()
#         assert product is not None
#         before_update = db.session.get(Product, product.id)
#         print(f"Before Update: {before_update.current_price}")

#     # Get CSRF token
#     csrf_token = get_csrf_token(client, f'/admin/update-item/{product.id}')

#     dummy_file = (io.BytesIO(b"test file content"), "test_image.png")

#     # Simulate POST form data
#     data = {
#         'csrf_token': csrf_token,
#         'product_name': 'test by vishnu',
#         'current_price': 800.00,
#         'previous_price': product.previous_price,
#         'description': product.description,
#         'category': product.category,
#         'sale': 'true' if product.sale else 'false',
#         'discount': product.discount,
#         'brand': product.brand,
#         'color': product.color,
#         'product_picture': dummy_file,
#         'sizes': ['S,5', 'M,3']  # Simulate updated sizes list
#     }

#     response = client.post(
#         f'/admin/update-item/{product.id}',
#         data=data,
#         content_type='multipart/form-data',
#         follow_redirects=True
#     )

#     assert response.status_code == 200
#     assert b"updated successfully" in response.data

#     with app.app_context():
#         updated_product = db.session.get(Product, product.id)
#         print(f"After Update: {updated_product.current_price}")
#         assert updated_product.product_name == 'test by vishnu'
#         assert updated_product.current_price == 800.00

def test_delete_product(client, app):
    login_admin(client)  # Ensure admin is logged in

    with app.app_context():
        initial_count = Product.query.count()
        product = product = Product.query.order_by(Product.id.desc()).first()
        assert product is not None
        product_id = product.id


    response = client.get(f"/admin/delete-item/{product_id}", follow_redirects=True)
    assert response.status_code == 200
    

    with app.app_context():
        deleted_product = db.session.get(Product, product_id)
        assert deleted_product is None
        assert Product.query.count() == initial_count - 1



# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\     old code    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\




# def test_add_product(client,app):
#     with app.app_context():
#         initial_count = Product.query.count()

#     csrf_token = get_csrf_token(client, '/admin/add_products')
#     dummy_file = (io.BytesIO(b'test file content'),"test_image.png")
#     response = client.post('/admin/add-product', data={
#         'csrf_token' : csrf_token,
#         'product_name': 'New Test Product',
#         'current_price': 99.99,
#         'previous_price': 120.00,
#         'description': 'A sample product',
#         'category': 'Fashion',
#         'quantity': 10,
#         # uncomment while executing this test, i commented because to check whether the test is working if i not provide the followling fields
#         # 'size_small': 5,
#         # 'size_medium': 3,
#         # 'size_large': 2,
#         'sale': True,
#         'product_picture' : dummy_file
#         },content_type = 'multipart/form-data',follow_redirects=True)

#     assert b"added successfully" in response.data
#     assert response.status_code == 200
#     with app.app_context():
#         current_count = Product.query.count()
#         assert current_count == initial_count + 1




# def test_update_product(client,app):
#     with app.app_context():
#         product = Product.query.first()
#         before_update = db.session.get(Product,product.id)
#         print(f"Before Update: {before_update.current_price}")
#         assert product is not None

#     csrf_token = get_csrf_token(client, f'/admin/update-item/{product.id}' )    

#     dummy_file = (io.BytesIO(b"test file content"),"test_image.png")


#     response = client.post(f'/admin/update-item/{product.id}', data={
#     'csrf_token': csrf_token,  
#     'product_name': 'test by vishnu',
#     'current_price': 800.00,  
#     'previous_price': product.previous_price,
#     'description': product.description,
#     'category': product.category,
#     'quantity': product.quantity,
#     'size_small': product.size_small,
#     'size_medium': product.size_medium,
#     'size_large': product.size_large,
#     'sale': product.sale,
#     'product_picture' : dummy_file
#     }, content_type='multipart/form-data',follow_redirects=True)

#     assert response.status_code == 200


#     with app.app_context():
#         updated_product = db.session.get(Product,product.id)
#         print(f"After Update: {updated_product.current_price}")
#         assert updated_product.product_name == 'test by vishnu'
#         assert updated_product.current_price == 800.00




# # Run delete after once executing this file, because i'm using the first product for both Update and Delete testing
# # before running Delete comment Update.
# # the CRUD testing completed yaay!!



# def test_delete_product(client,app):
#     with app.app_context():

#         initial_count = Product.query.count()
#         product = Product.query.first()
       
#         product_id = product.id
#         # product_id = 20     # check before running
    
#     response = client.get(f"/admin/delete-item/{product_id}")
#     assert response.status_code == 302  
#     with client.application.app_context():
#         deleted_product = db.session.get(Product, product_id)
#         assert Product.query.count() == initial_count - 1 
#         assert deleted_product is None

