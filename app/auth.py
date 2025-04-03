from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import re
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db
from flask_mail import Message
from app import mail

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r'^\d{10}$'
    return re.match(pattern, phone) is not None

def send_reset_email(user, token):
    """Send a password reset email to the user"""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        'Password Reset Request',
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.

This link will expire in 1 hour.
'''
    mail.send(msg)


@auth_bp.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.homepage"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("views.homepage"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        address = request.form["address"]
        state = request.form["state"]
        city = request.form["city"]
        pincode = request.form["pincode"]
        role = request.form["role"]

        # Validation
        if not all([name, phone, email, password, confirm_password, address, state, city, pincode]):
            flash("All fields are required!", "danger")
            return render_template("registration.html")

        if not is_valid_email(email):
            flash("Invalid email format!", "danger")
            return render_template("registration.html")

        if not is_valid_phone(phone):
            flash("Invalid phone number! Please enter 10 digits.", "danger")
            return render_template("registration.html")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("registration.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return render_template("registration.html")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(
            name=name,
            phone=phone,
            email=email,
            password=hashed_password,
            address=address,
            state=state,
            city=city,
            pincode=pincode,
            role=role
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")

    return render_template("registration.html")

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a reset token
            token = user.generate_reset_token(current_app.config['SECRET_KEY'])

            # Send a reset email
            send_reset_email(user, token)

            flash("Password reset email sent. Please check your email.", "info")
            return redirect(url_for("auth.login"))
        else:
            flash("No account found with this email address.", "danger")
    
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Verify the token
    user = User.verify_reset_token(token, current_app.config['SECRET_KEY'])
    
    if not user:
        flash("Invalid or expired reset token. Please try again.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
        else:
            # Hash the new password before storing it
            user.password = generate_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            
            flash("Your password has been updated successfully!", "success")
            return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html")



@auth_bp.route("/update-password", methods=["GET", "POST"])
@login_required
def update_password():
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect!", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match!", "danger")
        else:
            current_user.password = generate_password_hash(new_password, method="pbkdf2:sha256")
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("views.homepage"))

    return render_template("update_password.html")


@auth_bp.route("/update-profile", methods=["GET", "POST"])
@login_required
def update_profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        state = request.form.get("state", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()

        if not all([name, phone, address, state, city, pincode]):
            flash("All fields are required!", "warning")
            return redirect(url_for("auth.update_profile"))

        current_user.name = name
        current_user.phone = phone
        current_user.address = address
        current_user.state = state
        current_user.city = city
        current_user.pincode = pincode

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating profile.", "danger")

        return redirect(url_for("views.homepage"))

    return render_template("update_profile.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for("auth.login"))


## ONLY FOR THE DELIVERY AGENT
@auth_bp.route("/delivery_dashboard")
@login_required
def delivery_dashboard():
    if current_user.role != 'delivery_agent':
        return redirect(url_for('views.homepage'))
    return render_template('delivery_dashboard.html')


@auth_bp.route("/order_info")
@login_required
def order_info():
    if current_user.role != 'delivery_agent':
        return redirect(url_for('views.homepage'))
    return render_template('order_info.html')
