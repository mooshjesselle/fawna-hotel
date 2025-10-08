from flask import Flask
from flask_wtf.csrf import CSRFProtect
from utils.extensions import db, login_manager, mail
from utils.database.config import Config
from models import User  # Import models needed for init_db
import os
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from blueprints.api_routes import api

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Set FOOD_SERVICE_IPV4 from .env
    app.config['FOOD_SERVICE_IPV4'] = os.getenv('FOOD_SERVICE_IPV4')  # <-- add this
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem for server-side sessions
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key
    Session(app)
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'room_images')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Mobile App API
    app.register_blueprint(api)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    mail.init_app(app)
    csrf = CSRFProtect(app)
    
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

app = create_app()

# Import routes after app is created to avoid circular imports
from blueprints.routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)