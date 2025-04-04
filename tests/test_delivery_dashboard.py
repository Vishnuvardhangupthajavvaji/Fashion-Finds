
import pytest
from app import db
from app.models import Order, DeliveryPerson

def test_dashboard(app,client):
    # Create a test delivery person
    with app.app_context():
        person = DeliveryPerson(name="John Doe", location="New York")
        db.session.add(person)
        db.session.commit()

        # Create test orders
        order1 = Order(customer_name = "test1",product_name = "phone",customer_location="New York", delivery_person_id=None, delivery_status="Pending")
        order2 = Order(customer_name = "test2",product_name = "tab",customer_location="New York", delivery_person_id=person.id, delivery_status="Delivered")
        db.session.add_all([order1, order2])
        db.session.commit()

        response = client.get(f"/delivery/dashboard/{person.id}")
        assert response.status_code == 200
        
        assert b"Delivered" in response.data  # Check if order status is shown

def test_update_status(app,client):
    # Create a test order
    with app.app_context():
        person = DeliveryPerson(name = "testupdate", location = "nizamabad")
        db.session.add(person)
        db.session.commit()

        order = Order(customer_name = "testupdate",product_name = "phoneuptade",customer_location="nizamabad", delivery_person_id=person.id, delivery_status="Pending")
        db.session.add(order)
        db.session.commit()
        

        assert Order.query.get(order.id) is not None, "order is not exit in test_update_status" 
        assert order.id is not None, "order id not exit"
        # Update status
        response = client.post(f"/delivery/update_status/{order.id}/Delivered", follow_redirects=True)
        assert response.status_code == 200

        # Check if status is updated
        updated_order = Order.query.get(order.id)
        assert updated_order.delivery_status == "Delivered"


def test_assign_delivery(app,client):
    with app.app_context():
        # Create test delivery person and order
        person = DeliveryPerson.query.order_by(id).first()
        order = Order(customer_name = "testassign",product_name = "phoneassign",customer_location="hyd")
        db.session.add_all([person, order])
        db.session.commit()

        assert DeliveryPerson.query.get(person.id) is not None, "person is not exit in test_update_status"
        assert Order.query.get(order.id) is not None, "order is not exit in test_assign_delivery" 
        assert order.id is not None, "order.id not exist"
        assert person.id is not None, "person.id is not exist"
        response = client.post(f"/delivery/assign_delivery/{order.id}/{person.id}", follow_redirects=True)
        
        print(f"order id {order.id} person id {person.id} {response.status_code}")
        assert response.status_code == 200

        # Check if order is assigned
        assigned_order = Order.query.get(order.id)
        assert assigned_order.delivery_person_id == person.id




















# import pytest
# from app import db
# from app.models import Order, DeliveryPerson

# @pytest.fixture
# def temp_delivery_person(app):
#     with app.app_context():
#         person = DeliveryPerson(name = "testvishnu",location = "hyd")
#         db.session.add(person)
#         db.session.commit()
#         yield person  
#         db.session.delete(person)
#         db.session.commit()


# @pytest.fixture
# def temp_order(app):
#     with app.app_context():
#         order = Order(customer_name = "Guptha", product_name = "phone", customer_location = "hyd")
#         db.session.add(order)
#         db.session.commit()
#         yield order
#         db.session.delete(order)
#         db.session.commit()



# def test_dashboard(app,client,temp_delivery_person):
#     assert DeliveryPerson.query.get(temp_delivery_person.id) is not None , "temp_delivery_person not exist"
#     person = temp_delivery_person

#     with app.app_context():
#         order1 = Order(customer_name = "order1", product_name = "product_order",customer_location="hyd", delivery_person_id=person.id, delivery_status="Delivered")
#         db.session.add(order1)
#         db.session.commit()
#         order1_id = order1.id

#     response = client.get(f"/delivery/dashboard/{person.id}")
#     assert response.status_code == 200

#     # assert fb"{order1_id}" in response.data  
#     assert b"Delivered" in response.data  

#     db.session.rollback()
#     db.session.delete(order1)
#     db.session.commit()
#     assert Order.query.get(order1_id) is None


# def test_update_status(client,temp_order):
    
#     response = client.post(f"/delivery/update_status/{temp_order.id}/Delivered", follow_redirects=True)
#     assert response.status_code == 302

#     updated_order = Order.query.get(temp_order.id)
#     assert updated_order.delivery_status == "Delivered"




# def test_assign_delivery(client,temp_delivery_person,temp_order):

#     response = client.post(f"/delivery/assign_delivery/{temp_order.id}/{temp_delivery_person.id}", follow_redirects=True)
#     assert response.status_code == 302

#     assigned_order = Order.query.get(temp_order.id)
#     assert assigned_order.delivery_person_id == temp_delivery_person.id
