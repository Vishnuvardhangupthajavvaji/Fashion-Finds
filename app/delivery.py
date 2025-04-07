from flask import Blueprint,render_template,flash,url_for,redirect,current_app,request,session
from .models import Order,User,Product,OrderItem
from . import db
from flask_login import current_user,login_required
from flask_mail import Message

delivery_bp = Blueprint('delivery',__name__)

from datetime import datetime
from flask_mail import Message # type: ignore
from . import mail


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication




def send_email(user, order, token):
    print("send_email function called")
    print(user, order, token)
    # rating_url = url_for(
    #     "delivery.customer_review",
    #     user_id=user.id,
    #     order_id=order.id,
    #     token=token,
    #     _external=True,
    # )
    rating_url = url_for(
    "delivery.customer_review",
    user_id=user.id,
    order_id=order.order_id,
    token=token,
    _external=True,
)

    product = Product.query.get_or_404(order.product_id)
    orders = Order.query.get_or_404(order.order_id)
    sender_email = 'vishnujavvaji19@gmail.com'
    sender_password = 'aiun nsnp auvd nrbt'
    receiver_email = user.email
    subject = 'Rate the Product'
    body = f"Hello {orders.customer_name}, \n\nYour order : {product.product_name} with ID {order.id} has been successfully delivered. Thank you for choosing us!\n\nTo rate the delivered products click : {rating_url}\n\nBest regards,\nYour Delivery Team\n\n"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Authentication error. Please check your email and password.")
    except Exception as e:
        print(f"An error occurred: {e}")


@delivery_bp.route('/customer_review/<int:user_id>/<int:order_id>/<token>', methods=['GET', 'POST'])
def customer_review(user_id, order_id, token):
    user = User.query.get_or_404(user_id)
    order = Order.query.get_or_404(order_id)
    
    # Fetch all order items for this order, including the related products
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    if not order_items:
        flash("No items found in this order.", "danger")
        return redirect(url_for('delivery.some_other_route'))  # Adjust redirect as needed

    # Extract products from order items
    products = [item.product for item in order_items]

    if request.method == 'POST' and token:
        # Check if the order has already been rated
        if getattr(order, 'has_rated', False):  # Use getattr to avoid AttributeError if has_rated is missing
            flash("This order has already been rated.", "warning")
            return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

        # Process ratings for each product
        for product in products:
            rating_key = f'rating_{product.id}'  # Unique form field name per product
            try:
                rating = int(request.form.get(rating_key, 0))
                if rating < 1 or rating > 5:
                    flash(f"Rating for {product.product_name} must be between 1 and 5.", "danger")
                    return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))
                
                # Update product rating
                if product.rating > 0:
                    product.rating = round((product.rating + rating) / 2.0, 1)
                else:
                    product.rating = rating
            except ValueError:
                flash(f"Invalid rating value for {product.product_name}.", "danger")
                return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

        # Mark the order as rated
        order.has_rated = True  # Add this attribute to the Order model if not already present
        db.session.commit()
        flash("Customer Review Successful!", "success")
        return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

    # For GET request, render the template with the list of products
    return render_template('customer_review.html', user=user, order=order, products=products, token=token)


@delivery_bp.route('/dashboard')
@login_required
def dashboard():
    # person = User.query.get(id)
    person = current_user
    if not person:
        return "User not found", 404  # Handle non-existent users
    
    available_orders = Order.query.filter_by(city=person.city, delivery_person_id=None).all()
    delivered_orders = Order.query.filter_by(status="Delivered", delivery_person_id=person.id).all()
    assigned_orders = Order.query.filter(Order.delivery_person_id == person.id, Order.status != "Delivered").all()

    return render_template('delivery_dashboard.html', person=person, new_orders=available_orders, assigned_orders=assigned_orders, delivered=delivered_orders)



@delivery_bp.route("/delivery_agents_info")
@login_required
def delivery_agents_info():
    # agents = User.query.filter_by(role = "delivery_agent").all()
    
    from collections import defaultdict

    agents = User.query.filter(User.role == "delivery_agent", User.approved == 1).all()

    agents_by_city = defaultdict(list)
    for agent in agents:
        agents_by_city[agent.city].append(agent)

    # for city, agent_list in agents_by_city.items():
    #     print(f"City: {city}")
    #     for agent in agent_list:
    #         print(f" - {agent.name} (ID: {agent.id})")

    order = defaultdict(list)
    orders = Order.query.all()
    for o in orders:
        order[o.delivery_person_id].append(o)

    return render_template("delivery_agents_info.html",agents=agents_by_city, orders = order)


@delivery_bp.route("/update_status/<int:order_id>/<status>", methods=['GET', 'POST'])
@login_required
def update_status(order_id, status):
    
    order = Order.query.get(order_id)
    order_item=OrderItem.query.filter_by(order_id=order_id).first()

    if order:
        try:
            order.status = status
            if status == "Delivered":
                order.delivery_date = datetime.now()
                user = User.query.filter_by(email=order.mail).first()
                token = user.generate_reset_token(current_app.config['SECRET_KEY'])
                send_email(user, order_item, token)
            db.session.commit()
            return redirect(f'/delivery/dashboard')
        except Exception as e:
            print(e)
            flash("Something went wrong!!!, please try again!!", "danger")
            return redirect(f'/delivery/dashboard')
    else:
        return "no order exist", 400


@delivery_bp.route('/assign_delivery/<int:order_id>', methods=['GET','POST'])
@login_required
def assign_delivery(order_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.role != 'delivery_agent':
        print(f"current_user : {current_user.role}")
        return redirect(url_for('views.homepage'))

    try:
        order = Order.query.get(order_id)
        person = current_user
        if order and person:
            order.delivery_person_id = person.id
            order.status = "Accepted"
            db.session.commit()
            flash(f"you are assigned to {order.customer_name}'s order","success")

            return redirect(f"/delivery/dashboard")
        else:
            return "order not exist", 400
    except Exception as e:
        print(f"////////////////////////////////////\n{e}")
        return f"{e}",400




# @delivery_bp.route('/customer_review/<int:user_id>/<int:order_id>/<token>', methods=['GET', 'POST'])
# def customer_review(user_id, order_id, token):
#     user = User.query.get_or_404(user_id)
#     order = Order.query.get_or_404(order_id)
#     product = Product.query.get_or_404(order.product_id)

#     if request.method == 'POST' and token:
#         try:
#             rating = int(request.form.get('rating', 0))
#         except ValueError:
#             flash("Invalid rating value.", "danger")
#             return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

#         if rating < 1 or rating > 5:
#             flash("Rating must be between 1 and 5.", "danger")
#             return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

#         if product.rating > 0:
#             product.rating = round((product.rating + rating) / 2.0, 1)
#         else:
#             product.rating = rating

#         order.has_rated = True
#         db.session.commit()
#         flash("Customer Review Successful!", "success")

#         return redirect(url_for('delivery.customer_review', user_id=user_id, order_id=order_id, token=token))

#     return render_template('customer_review.html', user=user, order=order, token=token)

