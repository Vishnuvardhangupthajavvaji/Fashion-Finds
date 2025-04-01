# from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
# from .models import User, Product, ProductSize, Brand, db
# from flask_login import login_required
# from werkzeug.utils import secure_filename
# import os
# from .forms import ProductForm

# # Define the Blueprint
# admin = Blueprint('admin', __name__)

# # Ensure media folder exists for image uploads
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Root directory of the app
# UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "media")

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# ### ✅ Admin Dashboard Route
# @admin.route('/admin_dashboard')
# # @login_required
# def admin_dashboard():
#     if 'user_id' not in session:
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('auth.login'))
    
#     user = User.query.get(session['user_id'])
#     if user.role != 'admin':
#         return redirect(url_for('auth.home'))
    
#     total_users = User.query.count()
#     pending_approvals = User.query.filter_by(approved=False).count()
    
#     return render_template(
#         'admin_dashboard.html',
#         total_users=total_users,
#         pending_approvals=pending_approvals
#     )

# ### ✅ Add Products Route
# @admin.route('/add_products', methods=['GET', 'POST'])
# @login_required
# def add_products():
#     if 'user_id' not in session:
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('auth.login'))
    
#     user = User.query.get(session['user_id'])
#     if user.role != 'admin':
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('auth.home'))
    
#     form = ProductForm()

#     if request.method == "POST":
#         try:            
#             # Handle Image Upload
#             file = form.product_picture.data
#             if file:
#                 filename = secure_filename(file.filename)
#                 file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")  # Normalize path
#                 file.save(file_path)
#                 print(f"Image saved at: {file_path}")  # Debugging
#                 # Store only the filename in the database
#                 file_path = filename
#             else:
#                 file_path = None

#             # Create product
#             new_product = Product(
#                 product_name=form.product_name.data,
#                 product_picture=file_path,
#                 current_price=form.current_price.data,
#                 previous_price=form.previous_price.data,
#                 description=form.description.data,
#                 sale=form.sale.data,
#                 category=form.category.data,
#                 color=form.color.data,
#                 discount=form.discount.data,
#                 brand=form.brand.data
#             )

#             db.session.add(new_product)
#             db.session.commit()
#             print(f"Product added: {new_product.id}")  # Debugging

#             # Add product sizes
#             for size_form in form.sizes.data:
#                 new_size = ProductSize(
#                     product_id=new_product.id,
#                     size=size_form["size"],
#                     quantity=size_form["quantity"]
#                 )
#                 db.session.add(new_size)

#             db.session.commit()
#             flash(f"Product '{new_product.product_name}' added successfully!", "success")
#             return redirect(url_for('admin.view_products'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f"Product Not Added! Error: {str(e)}", "danger")
#             print("Error:", e)
    
#     return render_template("add_products.html", form=form)


# ### ✅ View Products Route
# @admin.route('/view_products')
# # @login_required
# def view_products():
#     if 'user_id' not in session:
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('auth.login'))
    
#     user = User.query.get(session['user_id'])
#     if user.role != 'admin':
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('auth.home'))
    
#     products = Product.query.all()
#     return render_template('view_products.html', products=products)


# @admin.route("/delete-item/<id>", methods=['GET','POST'])
# def delete_item(id):
#     try:
#         item_to_delete = Product.query.get(id)
#         # Delete associated sizes
#         ProductSize.query.filter_by(product_id=item_to_delete.id).delete()
#         # Delete the product image if it exists
#         if item_to_delete.product_picture:
#             image_path = os.path.join(UPLOAD_FOLDER, item_to_delete.product_picture)
#             if os.path.exists(image_path):
#                 os.remove(image_path)
#                 print(f"Deleted image: {image_path}")
#         # Delete the product from the database
#         db.session.delete(item_to_delete)
#         db.session.commit()
#         flash(f'{item_to_delete.product_name} deleted', "success")
#         return redirect('/admin/view_products')
#     except Exception as e:
#         print('Item not deleted', e)
#         flash('Item not deleted!!', "danger")
#     return redirect('/admin/view_products')


# @admin.route('/update-item/<int:product_id>', methods=['GET', 'POST'])
# def update_item(product_id):
#     product = Product.query.get_or_404(product_id)  # Fetch product from DB
#     form = ProductForm(obj=product)  # Pre-fill form with existing data

#     if request.method == "POST":
#         print(f"Before Update: {product.product_name}, {product.current_price}, {product.category}")

#         # Updating values
#         product.product_name = request.form.get("product_name")
#         product.current_price = float(request.form.get("current_price", product.current_price))
#         product.previous_price = float(request.form.get("previous_price", product.previous_price))
#         product.description = request.form.get("description")
#         product.category = request.form.get("category")
#         product.sale = request.form.get("sale") == "true"
#         product.discount = int(request.form.get("discount", product.discount))
#         product.brand = request.form.get("brand")
#         product.color = request.form.get("color")

#         # Handling image upload
#         if "product_picture" in request.files:
#             file = request.files["product_picture"]
#             if file.filename:  # Check if a new file was uploaded
#                 # Secure the filename
#                 filename = secure_filename(file.filename)
                
#                 # Define the file path
#                 file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
                
#                 # Save the new image
#                 file.save(file_path)
                
#                 # Delete the old image if it exists
#                 if product.product_picture:
#                     old_image_path = os.path.join(UPLOAD_FOLDER, product.product_picture)
#                     if os.path.exists(old_image_path):
#                         try:
#                             os.remove(old_image_path)
#                             print(f"Old image deleted: {old_image_path}")
#                         except Exception as e:
#                             print(f"Error deleting old image: {e}")
                
#                 # Update the product's image path
#                 product.product_picture = filename
#                 print(f"New image saved: {file_path}")

#         # Updating sizes
#         sizes_data = request.form.getlist("sizes")  # List of sizes from form
#         for size_data in sizes_data:
#             size, quantity = size_data.split(",")  # Assuming format: "M,5"
#             quantity = int(quantity)

#             existing_size = ProductSize.query.filter_by(product_id=product.id, size=size).first()
#             if existing_size:
#                 existing_size.quantity = quantity  # Update existing size
#             else:
#                 new_size = ProductSize(product_id=product.id, size=size, quantity=quantity)
#                 db.session.add(new_size)  # Add new size entry

#         try:
#             db.session.commit()
#             flash(f"{product.product_name} updated successfully!", "success")
#             return redirect(url_for("admin.view_products"))
#         except Exception as e:
#             db.session.rollback()
#             flash("Item Not Updated!!!", "danger")

#     return render_template("update_item.html", form=form, product=product)


# @admin.route('/media/<path:filename>')
# def get_image(filename):
#     print(f"Requesting file: {filename}")  # Debugging output
#     file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
#     print(f"Serving file from: {file_path}")  # Debugging output
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return "File not found", 404
#     return send_from_directory(UPLOAD_FOLDER, filename)


# @admin.route('/role_approval')
# def role_approval():
#     if 'user_id' not in session:
#         return redirect(url_for('auth.login'))
#     user = User.query.get(session['user_id'])
#     if user.role != 'admin':
#         return redirect(url_for('auth.home'))
#     users = User.query.filter_by(role='delivery_agent', approved=False).all()
#     return render_template('role_approval.html', users=users)

# @admin.route('/approve-user/<int:id>', methods=['POST'])
# def approve_user(id):
#     try:
#         user = User.query.get_or_404(id)
#         user.approved = True  # Make sure this field exists in your User model
#         db.session.commit()
#         return {"message": "User approved successfully"}, 200
#     except Exception as e:
#         print("Error approving user:", e)
#         return {"error": "Failed to approve user"}, 500

# @admin.route('/reject-user/<int:id>', methods=['POST'])
# def reject_user(id):
#     try:
#         user = User.query.get_or_404(id)
#         user.is_approved = False  # Make sure this field exists in your User model
#         db.session.commit()
#         return {"message": "User rejected successfully"}, 200
#     except Exception as e:
#         print("Error rejecting user:", e)
#         return {"error": "Failed to reject user"}, 500

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from .models import User, Product, ProductSize, Brand, db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .forms import ProductForm

# Define the Blueprint
admin = Blueprint('admin', __name__)

# Ensure media folder exists for image uploads
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Root directory of the app
UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "media")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

### ✅ Admin Dashboard Route
@admin.route('/admin_dashboard')
# @login_required
def admin_dashboard():
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if current_user.role != 'admin':
        return redirect(url_for('views.homepage'))
    
    total_users = User.query.count()
    pending_approvals = User.query.filter_by(approved=False).count()
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        pending_approvals=pending_approvals
    )

### ✅ Add Products Route
@admin.route('/add_products', methods=['GET', 'POST'])
@login_required
def add_products():
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('views.homepage'))
    
    form = ProductForm()

    if request.method == "POST":
        try:            
            # Handle Image Upload
            file = form.product_picture.data
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")  # Normalize path
                file.save(file_path)
                print(f"Image saved at: {file_path}")  # Debugging
                # Store only the filename in the database
                file_path = filename
            else:
                file_path = None

            # Create product
            new_product = Product(
                product_name=form.product_name.data,
                product_picture=file_path,
                current_price=form.current_price.data,
                previous_price=form.previous_price.data,
                description=form.description.data,
                sale=form.sale.data,
                category=form.category.data,
                color=form.color.data,
                discount=form.discount.data,
                brand=form.brand.data
            )

            db.session.add(new_product)
            db.session.commit()
            print(f"Product added: {new_product.id}")  # Debugging

            # Add product sizes
            for size_form in form.sizes.data:
                new_size = ProductSize(
                    product_id=new_product.id,
                    size=size_form["size"],
                    quantity=size_form["quantity"]
                )
                db.session.add(new_size)

            db.session.commit()
            flash(f"Product '{new_product.product_name}' added successfully!", "success")
            return redirect(url_for('admin.view_products'))

        except Exception as e:
            db.session.rollback()
            flash(f"Product Not Added! Error: {str(e)}", "danger")
            print("Error:", e)
    
    return render_template("add_products.html", form=form)


### ✅ View Products Route
@admin.route('/view_products')
# @login_required
def view_products():
    if not current_user.is_authenticated:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('views.homepage'))
    
    products = Product.query.all()
    return render_template('view_products.html', products=products)


@admin.route("/delete-item/<id>", methods=['GET','POST'])
def delete_item(id):
    try:
        item_to_delete = Product.query.get(id)
        # Delete associated sizes
        ProductSize.query.filter_by(product_id=item_to_delete.id).delete()
        # Delete the product image if it exists
        if item_to_delete.product_picture:
            image_path = os.path.join(UPLOAD_FOLDER, item_to_delete.product_picture)
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
        # Delete the product from the database
        db.session.delete(item_to_delete)
        db.session.commit()
        flash(f'{item_to_delete.product_name} deleted', "success")
        return redirect('/admin/view_products')
    except Exception as e:
        print('Item not deleted', e)
        flash('Item not deleted!!', "danger")
    return redirect('/admin/view_products')


@admin.route('/update-item/<int:product_id>', methods=['GET', 'POST'])
def update_item(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch product from DB
    form = ProductForm(obj=product)  # Pre-fill form with existing data

    if request.method == "POST":
        print(f"Before Update: {product.product_name}, {product.current_price}, {product.category}")

        # Updating values
        product.product_name = request.form.get("product_name")
        product.current_price = float(request.form.get("current_price", product.current_price))
        product.previous_price = float(request.form.get("previous_price", product.previous_price))
        product.description = request.form.get("description")
        product.category = request.form.get("category")
        product.sale = request.form.get("sale") == "true"
        product.discount = int(request.form.get("discount", product.discount))
        product.brand = request.form.get("brand")
        product.color = request.form.get("color")

        # Handling image upload
        if "product_picture" in request.files:
            file = request.files["product_picture"]
            if file.filename:  # Check if a new file was uploaded
                # Secure the filename
                filename = secure_filename(file.filename)
                
                # Define the file path
                file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
                
                # Save the new image
                file.save(file_path)
                
                # Delete the old image if it exists
                if product.product_picture:
                    old_image_path = os.path.join(UPLOAD_FOLDER, product.product_picture)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                            print(f"Old image deleted: {old_image_path}")
                        except Exception as e:
                            print(f"Error deleting old image: {e}")
                
                # Update the product's image path
                product.product_picture = filename
                print(f"New image saved: {file_path}")

        # Updating sizes
        sizes_data = request.form.getlist("sizes")  # List of sizes from form
        for size_data in sizes_data:
            size, quantity = size_data.split(",")  # Assuming format: "M,5"
            quantity = int(quantity)

            existing_size = ProductSize.query.filter_by(product_id=product.id, size=size).first()
            if existing_size:
                existing_size.quantity = quantity  # Update existing size
            else:
                new_size = ProductSize(product_id=product.id, size=size, quantity=quantity)
                db.session.add(new_size)  # Add new size entry

        try:
            db.session.commit()
            flash(f"{product.product_name} updated successfully!", "success")
            return redirect(url_for("admin.view_products"))
        except Exception as e:
            db.session.rollback()
            flash("Item Not Updated!!!", "danger")

    return render_template("update_item.html", form=form, product=product)


@admin.route('/media/<path:filename>')
def get_image(filename):
    print(f"Requesting file: {filename}")  # Debugging output
    file_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
    print(f"Serving file from: {file_path}")  # Debugging output
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return "File not found", 404
    return send_from_directory(UPLOAD_FOLDER, filename)


@admin.route('/role_approval')
def role_approval():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.role != 'admin':
        return redirect(url_for('views.homepage'))
    users = User.query.filter_by(role='delivery_agent', approved=False).all()
    return render_template('role_approval.html', users=users)

@admin.route('/approve-user/<int:id>', methods=['POST'])
def approve_user(id):
    try:
        user = User.query.get_or_404(id)
        user.approved = True  # Make sure this field exists in your User model
        db.session.commit()
        return {"message": "User approved successfully"}, 200
    except Exception as e:
        print("Error approving user:", e)
        return {"error": "Failed to approve user"}, 500

@admin.route('/reject-user/<int:id>', methods=['POST'])
def reject_user(id):
    try:
        user = User.query.get_or_404(id)
        user.is_approved = False  # Make sure this field exists in your User model
        db.session.commit()
        return {"message": "User rejected successfully"}, 200
    except Exception as e:
        print("Error rejecting user:", e)
        return {"error": "Failed to reject user"}, 500
