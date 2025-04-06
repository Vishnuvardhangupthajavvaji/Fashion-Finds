from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from .models import User, Product, ProductSize,  db, Order
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
            # for size_form in form.sizes.data:
            #     new_size = ProductSize(
            #         product_id=new_product.id,
            #         size=size_form["size"],
            #         quantity=size_form["quantity"]
            #     )
            #     db.session.add(new_size)

            for size_form in form.sizes.data:
                if size_form["single_quantity"] == 0:
                    new_size = ProductSize(
                        product_id=new_product.id,
                        size=size_form["size"],
                        quantity=size_form["quantity"]
                    )
                else:
                    new_size = ProductSize(
                        product_id=new_product.id,
                        size=size_form["size"],
                        quantity=size_form["single_quantity"]
                    )

                db.session.add(new_size)

            db.session.commit()

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
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

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
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                # Delete the old image *before* saving the new one
                if product.product_picture and product.product_picture != filename:
                    old_image_path = os.path.join(UPLOAD_FOLDER, product.product_picture)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                            print(f"Old image deleted: {old_image_path}")
                        except Exception as e:
                            print(f"Error deleting old image: {e}")

                # Save the new image
                file.save(file_path)
                if os.path.exists(file_path):
                    print(f"File confirmed saved: {file_path}")
                else:
                    print(f"File save failed: {file_path}")

                product.product_picture = filename
                print(f"New image assigned: {filename}")

        # Updating sizes
        # sizes_data = request.form.getlist("sizes")
        # for size_data in sizes_data:
        #     size, quantity = size_data.split(",")
        #     quantity = int(quantity)
        #     existing_size = ProductSize.query.filter_by(product_id=product.id, size=size).first()
        #     if existing_size:
        #         existing_size.quantity = quantity
        #     else:
        #         new_size = ProductSize(product_id=product.id, size=size, quantity=quantity)
        #         db.session.add(new_size)

        try:    
            ProductSize.query.filter_by(product_id=product.id).delete()  # Remove old sizes

            for size_form in form.sizes.data:
                if size_form["single_quantity"] == 0:  
                    new_size = ProductSize(
                        product_id=product.id,
                        size=size_form["size"],
                        quantity=size_form["quantity"]
                    )
                else:
                    new_size = ProductSize(
                        product_id=product.id,
                        size=size_form["size"],
                        quantity=size_form["single_quantity"]
                    )

                db.session.add(new_size)

            db.session.commit()
            flash(f"{product.product_name} updated successfully!", "success")
            return redirect("/admin/view_products")
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")
            flash('Item Not Updated!!!', "danger")


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


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\        graphs          \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@admin.route("/visualisation")
def visualisation():
    return redirect(url_for("admin.inventory"))
    return render_template("Visualisation.html")

from plotly import graph_objects as go
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import pandas as pd

@admin.route('/order_status')
def order_status():
    # Check if current user is admin
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('views.homepage'))


    # Query to count orders by status
    order_stats = (db.session.query(Order.status, db.func.count(Order.id).label('count'))
                  .group_by(Order.status)
                  .all())
    
    # Extract labels and values
    labels = [stat[0] for stat in order_stats]
    values = [stat[1] for stat in order_stats]

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut style
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        marker=dict(
            colors=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'],  # Custom colors
            line=dict(color='#FFFFFF', width=2)
        )
    )])

    # Update layout
    fig.update_layout(
        title='Order Status Distribution',
        title_x=0.5,  # Center title
        showlegend=True,
        annotations=[dict(
            text='Orders',
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )]
    )

    # Convert to JSON
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return render_template('visualisation.html', graphJSON=graphJSON)


@admin.route('/user_types')
@login_required
def user_types():
    try:
        # Check if current user is admin
        if current_user.role != 'admin':
            return redirect(url_for('views.homepage'))

        # Query to count users by role
        user_type_data = (db.session.query(User.role, db.func.count(User.id).label('count'))
                         .group_by(User.role)
                         .all())
        
        # Extract roles and counts
        roles = [row[0] for row in user_type_data]
        counts = [row[1] for row in user_type_data]

        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=roles,
            y=counts,
            text=counts,  # Show values on top
            textposition='auto',
            marker=dict(
                color=['#FF6B6B', '#4ECDC4', '#45B7D1'],  # Custom colors
                line=dict(color='#FFFFFF', width=2)
            ),
            hovertemplate='<b>Role</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
        )])

        # Update layout
        fig.update_layout(
            title='User Role Distribution',
            title_x=0.5,  # Center title
            xaxis_title='User Roles',
            yaxis_title='Number of Users',
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            showlegend=False
        )

        # Add gridlines (corrected properties)
        fig.update_xaxes(gridcolor='lightgrey')
        fig.update_yaxes(gridcolor='lightgrey', gridwidth=1)

        # Convert to JSON
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return render_template('visualisation.html', graphJSON=graphJSON)

    except Exception as e:
        return render_template('visualisation.html', error=str(e))
    


@admin.route('/order_location')
@login_required
def order_location():
    try:
        # Check if current user is admin (assuming this is an admin-only view)
        if current_user.role != 'admin':
            return redirect(url_for('views.homepage'))

        # Query to count orders by state
        order_location_data = (db.session.query(Order.state, db.func.count(Order.id).label('count'))
                              .group_by(Order.state)
                              .all())
        
        # Extract states and counts
        states = [row[0] for row in order_location_data]
        counts = [row[1] for row in order_location_data]

        # Create horizontal bar chart
        fig = go.Figure(data=[go.Bar(
            x=counts,
            y=states,
            orientation='h',
            text=counts,  # Show values on bars
            textposition='auto',
            marker=dict(
                color='#4ECDC4',  # Single color for all bars
                line=dict(color='#FFFFFF', width=1)
            ),
            hovertemplate='<b>State</b>: %{y}<br><b>Orders</b>: %{x}<extra></extra>'
        )])

        # Update layout
        fig.update_layout(
            title='Order Distribution by State',
            title_x=0.5,  # Center title
            xaxis_title='Number of Orders',
            yaxis_title='States',
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            height=max(400, len(states) * 30),  # Dynamic height based on number of states
            showlegend=False
        )

        # Add gridlines
        fig.update_xaxes(gridcolor='lightgrey', gridwidth=1)
        fig.update_yaxes(gridcolor='lightgrey', gridwidth=1)

        # Convert to JSON
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return render_template('visualisation.html', graphJSON=graphJSON)

    except Exception as e:
        return render_template('visualisation.html', error=str(e))
  

@admin.route('/revenue')
@login_required
def revenue():
    try:
        # Check if current user is admin
        if current_user.role != 'admin':
            return redirect(url_for('views.homepage'))

        # Fetch completed orders (Delivered)
        revenue_data = (db.session.query(Order.order_date, Order.total_price)
                        .filter(Order.status == 'Delivered')
                        .order_by(Order.order_date)
                        .all())

        if not revenue_data:
            return "No completed order data found in the database"

        print(f"revenue_data : {revenue_data}")

        # Convert to DataFrame
        df = pd.DataFrame(revenue_data, columns=['order_date', 'total_price'])

        print(f"df : {df}")

        # Convert order_date to datetime and remove time (keep only Year-Month-Day)
        df['order_date'] = pd.to_datetime(df['order_date']).dt.date

        # Group by date and sum total_price
        df = df.groupby('order_date', as_index=False)['total_price'].sum()

        print(f"df grouped : {df}")

        # Ensure total_price is numeric and print to verify
        df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')
        print(f"total_price values: {df['total_price'].tolist()}")

        # Convert to lists for explicit data passing
        x_values = df['order_date'].tolist()
        y_values = df['total_price'].tolist()

        # Plot Line Chart with explicit data and hovertemplate on trace
        fig = go.Figure(data=go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            hovertemplate='<b>Date</b>: %{x}<br><b>Revenue (₹)</b>: %{y:,.2f}<extra></extra>'  # Moved here
        ))
        fig.update_layout(
            title="Revenue Over Time",
            xaxis_title="Date",
            yaxis_title="Revenue (₹)",
            xaxis=dict(tickformat="%Y-%m-%d"),
            yaxis=dict(
                range=[0, max(y_values) * 1.1],
                tickformat=",.0f",
                tickmode="auto",
                dtick=500
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_x=0.5,
            # height=600,
            # width=1000,
            # hovermode="x unified"  # Enhanced hover behavior
        )

        fig.update_xaxes(gridcolor='lightgrey', gridwidth=1)
        fig.update_yaxes(gridcolor='lightgrey', gridwidth=1)

        # Convert to JSON and print for debugging
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        # Safely extract and print y-values from graphJSON
        graph_data = json.loads(graphJSON)
        if graph_data and 'data' in graph_data and len(graph_data['data']) > 0:
            y_values_from_json = graph_data['data'][0].get('y', 'No y-values found')
            print(f"graphJSON y-values: {y_values_from_json[:10] if isinstance(y_values_from_json, list) else y_values_from_json}...")
        else:
            print("Error: No data found in graphJSON")
        return render_template('visualisation.html', graphJSON=graphJSON)

    except Exception as e:
        print(e)
        return render_template('visualisation.html', error=str(e))
    
@admin.route("/inventory")
def inventory():

    try:
        # Check if current user is admin
        if current_user.role != 'admin':
            return redirect(url_for('views.homepage'))

        # Query to count users by role
        # user_type_data = (db.session.query(User.role, db.func.count(User.id).label('count'))
        #                  .group_by(User.role)
        #                  .all())
        product_types = (db.session.query(Product.category, db.func.count(Product.id).label('count'))
                         .group_by(Product.category)
                         .all())
        
        # Extract roles and counts
        category = [row[0] for row in product_types]
        counts = [row[1] for row in product_types]

        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=category,
            y=counts,
            text=counts,  # Show values on top
            textposition='auto',
            marker=dict(
                color=['#FF6B6B', '#4ECDC4', '#45B7D1'],  # Custom colors
                line=dict(color='#FFFFFF', width=2)
            ),
            hovertemplate='<b>Role</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
        )])

        # Update layout
        fig.update_layout(
            title='Fashion Finds Inventory',
            title_x=0.5,  # Center title
            xaxis_title='category',
            yaxis_title='Number of Products',
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            showlegend=False
        )

        # Add gridlines (corrected properties)
        fig.update_xaxes(gridcolor='lightgrey')
        fig.update_yaxes(gridcolor='lightgrey', gridwidth=1)

        # Convert to JSON
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return render_template('visualisation.html', graphJSON=graphJSON)

    except Exception as e:
        return render_template('visualisation.html', error=str(e))
    
