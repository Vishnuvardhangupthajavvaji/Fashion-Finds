
# from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash, json, send_from_directory
# from app.models import Product, Brand, Cart, Wishlist, User, Order, OrderItem, ProductSize
# from app import db
# from flask_login import login_required
# import random, string, os

# views = Blueprint('views', __name__)

# # Define UPLOAD_FOLDER for image uploads
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Root directory of the app
# UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "media")

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# @views.route('/')
# def homepage():
#     products_list = Product.query.all()  
#     return render_template('home.html', products=products_list)

# @views.route('/media/<path:filename>')
# def get_image(filename):
#     print(f"Requesting file: {filename}")  
#     file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
#     print(f"Serving file from: {file_path}")  
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return "File not found", 404
#     return send_from_directory(UPLOAD_FOLDER, filename)



# @views.route('/category/<string:category_name>')
# def products_by_category(category_name):
#     products = Product.query.filter_by(category=category_name).all()
#     return render_template('category.html', products=products, category_name=category_name)


# ### updated cart 
# @login_required
# @views.route('/cart')
# def show_cart():
#     if 'user_id' not in session:
#         return render_template("cart.html")

#     user_id = session['user_id']
#     cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(Cart.user_id == user_id).all()
    
#     total_mrp = sum(cart.quantity * product.previous_price for cart, product in cart_items)
#     total_discount = sum(cart.quantity * product.discount for cart, product in cart_items if product.discount)
#     total_amount = int(total_mrp - total_discount)  # Ensure final amount is an integer
    
#     return render_template("cart.html", cart_items=cart_items, total_mrp=total_mrp, total_discount=total_discount, total_amount=total_amount)

# @views.route('/add_to_cart/<int:product_id>', methods=['POST'])
# def add_to_cart(product_id):
#     if 'user_id' not in session:
#         return render_template("cart.html")

#     product = Product.query.get_or_404(product_id)
#     user_id = session['user_id']

#     cart_item = Cart.query.filter_by(user_id=user_id, product_id=product.id).first()
#     if cart_item:
#         cart_item.quantity += 1
#     else:
#         new_cart_item = Cart(user_id=user_id, product_id=product.id, quantity=1)
#         db.session.add(new_cart_item)

#     db.session.commit()
#     flash("Product added to cart!", "success")
#     return redirect(url_for('views.show_cart'))

# @views.route('/remove_from_cart/<int:product_id>', methods=['POST'])
# def remove_from_cart(product_id):
#     if 'user_id' not in session:
#         return render_template("cart.html")

#     user_id = session['user_id']
#     cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
#     if cart_item:
#         db.session.delete(cart_item)
#         db.session.commit()
#         flash("Product removed from cart!", "success")
#     else:
#         flash("Product not found in cart!", "danger")

#     return redirect(url_for('views.show_cart'))


# @views.route('/move_to_cart/<int:product_id>', methods=['POST'])
# def move_to_cart(product_id):
#     if 'user_id' not in session:
#         return render_template("cart.html")

#     user_id = session['user_id']

#     # Check if item exists in wishlist
#     wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
#     if wishlist_item:
#         # Move item to cart
#         cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
#         if cart_item:
#             cart_item.quantity += 1  # Increase quantity if already exists
#         else:
#             new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
#             db.session.add(new_cart_item)

#         # Remove from wishlist
#         db.session.delete(wishlist_item)
#         db.session.commit()

#         flash("Item moved to cart!", "success")
#     else:
#         flash("Item not found in wishlist!", "danger")

#     return redirect(url_for('views.show_wishlist'))


# @views.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
# def update_cart_quantity(product_id):
#     if 'user_id' not in session:
#         return jsonify({"success": False, "error": "Login required"}), 403

#     user_id = session['user_id']
#     new_quantity = int(request.form.get('quantity', 1))

#     cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
#     if cart_item:
#         cart_item.quantity = new_quantity
#         db.session.commit()

#     total_mrp = sum(cart.quantity * product.previous_price for cart, product in db.session.query(Cart, Product).join(Product).filter(Cart.user_id == user_id).all())
#     total_discount = sum(cart.quantity * product.discount for cart, product in db.session.query(Cart, Product).join(Product).filter(Cart.user_id == user_id).all() if product.discount)
#     total_amount = int(total_mrp - total_discount)

#     return jsonify({"success": True, "total_amount": total_amount})

# ### this button code that add cart to wishlist

# @views.route('/move_to_wishlist/<int:product_id>', methods=['POST'])
# def move_to_wishlist(product_id):
#     if 'user_id' not in session:
#         return render_template("wishlist.html")

#     user_id = session['user_id']

#     # Check if item exists in cart
#     cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
#     if cart_item:
#         # Check if item already exists in wishlist
#         wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
#         if not wishlist_item:
#             new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
#             db.session.add(new_wishlist_item)

#         # Remove from cart
#         db.session.delete(cart_item)
#         db.session.commit()

#         flash("Item moved to wishlist!", "success")
#     else:
#         flash("Item not found in cart!", "danger")

#     return redirect(url_for('views.show_cart'))

# ### Updated wishlist

# @views.route('/wishlist')
# def show_wishlist():
#     if 'user_id' not in session:
#         return render_template("wishlist.html")

#     wishlist = db.session.query(Wishlist, Product).join(Product, Wishlist.product_id == Product.id)\
#         .filter(Wishlist.user_id == session['user_id']).all()
    
#     wishlist_items = [{"wishlist": item[0], "product": item[1]} for item in wishlist]
#     return render_template('wishlist.html', wishlist_items=wishlist_items)

# @views.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
# def wishlist_add(product_id):
#     if 'user_id' not in session:
#         return render_template("wishlist.html")

#     existing_item = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
#     if not existing_item:
#         new_wishlist_item = Wishlist(user_id=session['user_id'], product_id=product_id)
#         db.session.add(new_wishlist_item)
#         db.session.commit()
    
#     return redirect(url_for('views.show_wishlist'))


# @views.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
# def remove_from_wishlist(product_id):
#     if 'user_id' not in session:
#         return render_template("wishlist.html")

#     wishlist_item = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
#     if wishlist_item:
#         db.session.delete(wishlist_item)
#         db.session.commit()
#         flash("Product removed from wishlist!", "success")
#     else:
#         flash("Product not found in wishlist!", "danger")
    
#     return redirect(url_for('views.show_wishlist'))


# @views.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('query', '').strip()
#     category_name = request.args.get('category', '').strip()
#     # brand_name = request.args.get('brand', '').strip()
#     min_price = request.args.get('min_price', type=float)
#     max_price = request.args.get('max_price', type=float)
#     color = request.args.get('color', '').strip()

#     # Start filtering products
#     search_query = Product.query

#     if query:
#         search_query = search_query.filter(
#             (Product.product_name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
#         )
#     if category_name:
#         search_query = search_query.filter(Product.category.ilike(f"%{category_name}%"))
#     # if brand_name:
#         # search_query = search_query.join(Brand).filter(Brand.name.ilike(f"%{brand_name}%"))
#     if color:
#         search_query = search_query.filter(Product.color.ilike(f"%{color}%"))
#     if min_price is not None:
#         search_query = search_query.filter(Product.current_price >= min_price)
#     if max_price is not None:
#         search_query = search_query.filter(Product.current_price <= max_price)

#     search_results = search_query.all()

#     categories = db.session.query(Product.category).distinct()
#     # brands = Brand.query.all()
#     colors = db.session.query(Product.color).distinct()  # Fetch unique colors

#     return render_template(
#         'search_results.html',
#         products=search_results,
#         query=query,
#         category=category_name,
#         # brand=brand_name,
#         min_price=min_price,
#         max_price=max_price,
#         color=color,
#         categories=[c[0] for c in categories],
#         # brands=brands,
#         colors=[c[0] for c in colors]  # Pass colors correctly
#     )





# #suggested Product code
# @views.route('/product/<int:product_id>')
# def product_info(product_id):
#     product = Product.query.get_or_404(product_id)

#     # Fetch product sizes (if available)
#     sizes = ProductSize.query.filter_by(product_id=product.id).all()

#     # Fetch 4 completely random products (excluding the current product)
#     suggested_products = Product.query.filter(Product.id != product.id).order_by(db.func.random()).limit(4).all()

#     return render_template("product_details.html", product=product, sizes=sizes, suggested_products=suggested_products)



# # @views.route('/checkout')
# # def checkout():
# #     cart_items = session.get('cart', [])
# #     if not cart_items:
# #         return render_template('checkout.html', cart_items=[], subtotal=0, shipping=0, tax=0, total=0)

# #     subtotal = sum(item['price'] for item in cart_items)
# #     shipping = 50 if subtotal > 0 else 0
# #     tax = round(subtotal * 0.05, 2)
# #     total = subtotal + shipping + tax

# #     return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, tax=tax, total=total)



# @views.route('/checkout', methods=['GET', 'POST'])
# # @login_required
# def checkout():
#     user_id = session.get('user_id')
#     if not user_id:
#         flash('You must be logged in to proceed!', 'danger')
#         return redirect(url_for('views.login'))

#     cart_items_db = Cart.query.filter_by(user_id=user_id).all()
#     if not cart_items_db:
#         flash('Your cart is empty!', 'danger')
#         return redirect(url_for('views.cart'))

#     cart_items = []
#     subtotal = 0
#     for cart_item in cart_items_db:
#         product = Product.query.get(cart_item.product_id)
#         if product:
#             cart_items.append({
#                 'id': cart_item.product_id,
#                 'name': product.product_name,
#                 'price': product.current_price,
#                 'quantity': cart_item.quantity
#             })
#             subtotal += product.current_price * cart_item.quantity

#     shipping = 40
#     tax = subtotal * 0.05  # 5% tax
#     total = subtotal + shipping + tax

#     return render_template(
#         'checkout.html',
#         cart_items=cart_items,
#         subtotal=round(subtotal, 2),
#         shipping=round(shipping, 2),
#         tax=round(tax, 2),
#         total=round(total, 2)
#     )

# @views.route('/place_order', methods=['POST'])
# # @login_required
# def place_order():
#     user_id = session.get('user_id')
#     if not user_id:
#         flash('You must be logged in to place an order!', 'danger')
#         return redirect(url_for('views.login'))

#     user = User.query.get(user_id)
#     if not user:
#         flash('User not found!', 'danger')
#         return redirect(url_for('views.login'))

#     address_line_1 = request.form.get('address_line_1')
#     state = request.form.get('state')
#     city = request.form.get('city')
#     pincode = request.form.get('pincode')
#     firstname = request.form.get('firstname')
#     lastname = request.form.get('lastname')
#     email = request.form.get('email')

#     cart_items_db = Cart.query.filter_by(user_id=user_id).all()
#     if not cart_items_db:
#         flash('Your cart is empty!', 'danger')
#         return redirect(url_for('views.checkout'))

#     new_order = Order(
#         user_id=user_id,
#         customer_name=f"{firstname} {lastname}",
#         address_line_1=address_line_1,
#         state=state,
#         city=city,
#         pincode=pincode,
#         total_price=0,
#         status="Pending",
#         mail=email
#     )
#     db.session.add(new_order)
#     db.session.commit()
    
#     total_price = 0
#     for cart_item in cart_items_db:
#         product = Product.query.get(cart_item.product_id)
#         if not product:
#             flash(f"Product with ID {cart_item.product_id} not found.", 'danger')
#             continue

#         total_cost = product.current_price * cart_item.quantity
#         total_price += total_cost

#         order_item = OrderItem(
#             order_id=new_order.id,
#             product_id=cart_item.product_id,
#             quantity=cart_item.quantity,
#             unit_price=product.current_price,
#             subtotal=total_cost
#         )
#         db.session.add(order_item)
        
#         product.count -= cart_item.quantity

#     new_order.total_price = total_price
    
#     Cart.query.filter_by(user_id=user_id).delete()
#     db.session.commit()

#     return jsonify({"success": True})

# @views.route('/my_orders')
# # @login_required
# def my_orders():
#     user_id = session.get('user_id')
#     if not user_id:
#         flash('You must be logged in to view your orders!', 'danger')
#         return redirect(url_for('views.login'))

#     orders = Order.query.filter_by(user_id=user_id).all()
#     orders_with_items = []
#     for order in orders:
#         order_items = OrderItem.query.filter_by(order_id=order.id).all()
#         items_data = [{'name': item.product.product_name, 'quantity': item.quantity} for item in order_items]

#         orders_with_items.append({
#             'id': order.id,
#             'status': order.status,
#             'total_price': order.total_price,
#             'order_items': items_data
#         })

#     return render_template('my_orders.html', orders=orders_with_items)

# @views.route('/order/<int:order_id>', methods=['GET'])
# # @login_required
# def view_order_items(order_id):
#     order = Order.query.get(order_id)
#     if not order or order.user_id != session.get('user_id'):
#         flash('Order not found!', 'danger')
#         return redirect(url_for('views.my_orders'))

#     order_items = OrderItem.query.filter_by(order_id=order.id).all()
#     return render_template('view_order.html', order=order, order_items=order_items)


# @views.route('/cancel_order/<int:order_id>', methods=['POST'])
# # @login_required
# def cancel_order(order_id):
#     user_id = session.get('user_id')
#     if not user_id:
#         flash('You must be logged in to cancel orders!', 'danger')
#         return redirect(url_for('views.login'))

#     order = Order.query.get_or_404(order_id)
#     if order.user_id != user_id:
#         flash('You can only cancel your own orders.', 'danger')
#         return redirect(url_for('views.my_orders'))

#     order.status = 'Cancelled'
    
#     order_items = OrderItem.query.filter_by(order_id=order_id).all()
#     for order_item in order_items:
#         product = Product.query.get(order_item.product_id)
#         product.count += order_item.quantity

#     db.session.commit()
#     return redirect(url_for('views.my_orders'))


# @views.route('/faqs', methods=['GET', 'POST'])
# def faqs():
#     return render_template('faqs.html')

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash, send_from_directory
from app.models import Product, Cart, Wishlist, User, Order, OrderItem,ProductSize
from app import db
from flask_login import login_required
import os

views = Blueprint('views', __name__)

# Define UPLOAD_FOLDER for image uploads
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Root directory of the app
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "media")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@views.route('/')
def homepage():
    products_list = Product.query.all()  
    return render_template('home.html', products=products_list)

@views.route('/media/<path:filename>')
def get_image(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_from_directory(UPLOAD_FOLDER, filename)

@views.route('/category/<string:category_name>')
def products_by_category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html', products=products, category_name=category_name)



#suggested Product code
@views.route('/product/<int:product_id>')
def product_info(product_id):
    product = Product.query.get_or_404(product_id)

    # Fetch product sizes (if available)
    sizes = ProductSize.query.filter_by(product_id=product.id).all()

    # Fetch 4 completely random products (excluding the current product)
    suggested_products = Product.query.filter(Product.id != product.id).order_by(db.func.random()).limit(4).all()

    return render_template("product_details.html", product=product, sizes=sizes, suggested_products=suggested_products)


@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category_name = request.args.get('category', '').strip()
    # brand_name = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    color = request.args.get('color', '').strip()

    # Start filtering products
    search_query = Product.query

    if query:
        search_query = search_query.filter(
            (Product.product_name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
        )
    if category_name:
        search_query = search_query.filter(Product.category.ilike(f"%{category_name}%"))
    # if brand_name:
        # search_query = search_query.join(Brand).filter(Brand.name.ilike(f"%{brand_name}%"))
    if color:
        search_query = search_query.filter(Product.color.ilike(f"%{color}%"))
    if min_price is not None:
        search_query = search_query.filter(Product.current_price >= min_price)
    if max_price is not None:
        search_query = search_query.filter(Product.current_price <= max_price)

    search_results = search_query.all()

    categories = db.session.query(Product.category).distinct()
    # brands = Brand.query.all()
    colors = db.session.query(Product.color).distinct()  # Fetch unique colors

    return render_template(
        'search_results.html',
        products=search_results,
        query=query,
        category=category_name,
        # brand=brand_name,
        min_price=min_price,
        max_price=max_price,
        color=color,
        categories=[c[0] for c in categories],
        # brands=brands,
        colors=[c[0] for c in colors]  # Pass colors correctly
    )


### Updated Cart - Only for logged-in users
from flask_login import current_user
@views.route('/cart')
@login_required
def show_cart():
    user_id = current_user.id  # Get the user ID directly from current_user (handled by flask_login)

    # Fetch cart items specific to the logged-in user
    cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id)\
        .filter(Cart.user_id == user_id).all()

    # Ensure if the cart is empty, show an appropriate message
    if not cart_items:
        flash("Your cart is empty!", "info")

    # Calculate total MRP, discount, and amount for the cart items
    total_mrp = sum(cart.quantity * product.current_price for cart, product in cart_items)
    total_discount = sum(cart.quantity * product.discount for cart, product in cart_items if product.discount)
    total_amount = int(total_mrp - total_discount)  # Ensure final amount is an integer
    print(f"total_amount : {total_amount}")
    # Pass the correct cart data and calculation results to the template
    return render_template(
        "cart.html", 
        cart_items=cart_items, 
        total_mrp=total_mrp, 
        total_discount=total_discount, 
        total_amount=total_amount
    )


@views.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = current_user.id  # Use current_user to get user_id instead of session

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product.id, quantity=1)
        db.session.add(new_cart_item)

    db.session.commit()
    flash("Product added to cart!", "success")
    return redirect(url_for('views.show_cart'))


@views.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    user_id = current_user.id  # Use current_user to get user_id instead of session
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Product removed from cart!", "success")
    else:
        flash("Product not found in cart!", "danger")

    return redirect(url_for('views.show_cart'))


@views.route('/move_to_cart/<int:product_id>', methods=['POST'])
@login_required
def move_to_cart(product_id):
    user_id = current_user.id  # Use current_user to get user_id instead of session

    # Check if item exists in wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if wishlist_item:
        # Move item to cart
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1  # Increase quantity if already exists
        else:
            new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
            db.session.add(new_cart_item)

        # Remove from wishlist
        db.session.delete(wishlist_item)
        db.session.commit()

        flash("Item moved to cart!", "success")
    else:
        flash("Item not found in wishlist!", "danger")

    return redirect(url_for('views.show_wishlist'))


@views.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
@login_required
def update_cart_quantity(product_id):
    user_id = current_user.id  
    new_quantity = int(request.form.get('quantity', 1))

    # Fetch the cart item
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity = new_quantity
        db.session.commit()

    # Fetch updated cart details
    cart_items = db.session.query(Cart, Product).join(Product).filter(Cart.user_id == user_id).all()

    # Ensure all values are initialized to avoid 'undefined' issues
    total_price = sum(cart.quantity * product.current_price for cart, product in cart_items)
    total_discount = sum(cart.quantity * (product.discount or 0) for cart, product in cart_items)  # Handle None discount
    total_amount = int(total_price - total_discount)

    return jsonify({
        "success": True,
        "total_mrp": total_price,
        "discount_mrp": total_discount,
        "total_amount": total_amount
    })


@views.route('/wishlist')
@login_required
def show_wishlist():
    user_id = current_user.id  # Use current_user to get user_id instead of session
    wishlist = db.session.query(Wishlist, Product).join(Product, Wishlist.product_id == Product.id)\
        .filter(Wishlist.user_id == user_id).all()
    
    wishlist_items = [{"wishlist": item[0], "product": item[1]} for item in wishlist]
    return render_template('wishlist.html', wishlist_items=wishlist_items)


@views.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
@login_required
def wishlist_add(product_id):
    user_id = current_user.id  # Use current_user to get user_id instead of session
    existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not existing_item:
        new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(new_wishlist_item)
        db.session.commit()
    
    return redirect(url_for('views.show_wishlist'))


# @views.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
# @login_required
# def remove_from_wishlist(product_id):
#     user_id = current_user.id  # Use current_user to get user_id instead of session
#     wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
#     print(f"wishlist_item : {wishlist_item}, user_id : {user_id}, product_id : {product_id}")
#     if wishlist_item:
#         db.session.delete(wishlist_item)
#         db.session.commit()
#         flash("Product removed from wishlist!", "success")
#     else:
#         flash("Product not found in wishlist!", "danger")
    
#     return redirect(url_for('views.show_wishlist'))

@views.route('/move_to_wishlist/<int:product_id>', methods=['POST'])
@login_required
def move_to_wishlist(product_id):
    user_id = current_user.id  # Use current_user to get user_id instead of session
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    print(f"wishlist_item : {wishlist_item}, user_id : {user_id}, product_id : {product_id}")
    if wishlist_item:
        db.session.add(wishlist_item)
        db.session.commit()
        flash("Product moved to wishlist!", "success")
    else:
        flash("Product not found in wishlist!", "danger")
    
    return redirect(url_for('views.show_wishlist'))


@views.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = current_user.id  # Use current_user.id instead of session
    cart_items_db = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items_db:
        flash('Your cart is empty!', 'danger')
        return redirect(url_for('views.cart'))

    cart_items = []
    subtotal = 0
    discount = 45  # Apply the discount if applicable

    for cart_item in cart_items_db:
        product = Product.query.get(cart_item.product_id)
        if product:
            cart_items.append({
                'id': cart_item.product_id,
                'name': product.product_name,
                'price': product.current_price,  # Ensure this value is correct
                'quantity': cart_item.quantity
            })
            subtotal += product.current_price * cart_item.quantity
    print(cart_items)
    # Get total_amount from query parameters if passed, otherwise use the calculated subtotal
    total_amount = request.args.get('total_amount', type=float)

    if total_amount is None:
        total_amount = subtotal

    # Recalculate based on total_amount
    tax = total_amount * 0.05  # 5% tax
    shipping = 40
    total = total_amount - discount + shipping + tax  # Apply discount correctly

    print(f"Subtotal: {subtotal}, Discount: {discount}, Tax: {tax}, Shipping: {shipping}, Total: {total}")

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=round(subtotal, 2),
        discount=round(discount, 2),
        shipping=round(shipping, 2),
        tax=round(tax, 2),
        total=round(total, 2)
    )


@views.route('/place_order', methods=['POST'])
@login_required
def place_order():
    user_id = current_user.id
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('views.login'))

    address_line_1 = request.form.get('address_line_1')
    state = request.form.get('state')
    city = request.form.get('city')
    pincode = request.form.get('pincode')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')

    cart_items_db = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items_db:
        flash('Your cart is empty!', 'danger')
        return redirect(url_for('views.checkout'))

    # Create a new order (without a product_id in the Order table)
    if( len(firstname) or len(lastname) ):
        new_order = Order(
            user_id=user_id,
            customer_name=f"{firstname} {lastname}",
            address_line_1=address_line_1,
            state=state,
            city=city,
            pincode=pincode,
            total_price=0,
            status="In Transit",
            mail=email
        )
    else :
        new_order = Order(
            user_id=user_id,
            customer_name=user.name,
            address_line_1= user.address,
            state= user.state,
            city= user.city,
            pincode= user.pincode,
            total_price=0,
            status="In Transit",
            mail= user.email
        )
    print(f" firstname : {len(firstname)}")
    db.session.add(new_order)
    db.session.commit()  # Commit to get the new order ID

    total_price = 0
    for cart_item in cart_items_db:
        product = Product.query.get(cart_item.product_id)
        total_cost = product.current_price * cart_item.quantity
        total_price += total_cost

        # Create OrderItem for each cart item (link the OrderItem to the new order)
        order_item = OrderItem(
            order_id=new_order.id,  # Link the OrderItem to the new order
            product_id=cart_item.product_id,  # Correctly set the product_id here
            quantity=cart_item.quantity,
            unit_price=product.current_price,
            subtotal=total_cost
        )
        db.session.add(order_item)

        # Reduce the product count based on quantity
        # product.count -= cart_item.quantity

    # Update the total price in the Order (based on OrderItems)
    new_order.total_price = total_price
    db.session.commit()  # Commit the changes for Order and OrderItems

    # Empty the cart
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"success": True})

@views.route('/my_orders')
@login_required
def my_orders():

    orders = Order.query.filter_by(user_id=current_user.id).all()
    orders_with_items = []
    for order in orders:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        items_data = [{'name': item.product.product_name, 'quantity': item.quantity} for item in order_items]

        orders_with_items.append({
            'id': order.id,
            'status': order.status,
            'total_price': order.total_price,
            'order_items': items_data
        })

    return render_template('my_orders.html', orders=orders_with_items)

@views.route('/order/<int:order_id>', methods=['GET'])
@login_required
def view_order_items(order_id):
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id :
        # print(not order, order.user_id , current_user.id )
        flash('Order not found!', 'danger')
        return redirect(url_for('views.my_orders'))

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    return render_template('view_order.html', order=order, order_items=order_items)


@views.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    user_id = current_user.id
    order = Order.query.get_or_404(order_id)
    if order.user_id != user_id:
        flash('You can only cancel your own orders.', 'danger')
        return redirect(url_for('views.my_orders'))

    order.status = 'Cancelled'
    
    # order_items = OrderItem.query.filter_by(order_id=order_id).all()
    # for order_item in order_items:
    #     product = Product.query.get(order_item.product_id)
    #     product.quantity += order_item.quantity

    db.session.commit()
    return redirect(url_for('views.my_orders'))


@views.route('/faqs', methods=['GET', 'POST'])
def faqs():
    return render_template('faqs.html')