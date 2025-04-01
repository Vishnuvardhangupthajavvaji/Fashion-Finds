from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = "V123@rku"  # Change this to a secure secret key in production

    # Database Configuration
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'vkumar080@rku.ac.in'  # Update with your email
    app.config['MAIL_PASSWORD'] = 'oqpj npkl jyxh hijh'   # Update with your app password
    app.config['MAIL_DEFAULT_SENDER'] = 'vkumar080@rku.ac.in'

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = "auth.login"  # Redirect to login page if user is not logged in

    # User Loader Function
    from app.models import User  # Import User model after db initialization to avoid circular imports

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import routes after db initialization to avoid circular imports
    from app.auth import auth_bp
    from app.admin import admin
    from app.views import views

    # Register blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")

    with app.app_context():
        db.create_all()

    return app