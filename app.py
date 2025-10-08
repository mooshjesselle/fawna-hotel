from flask import Flask
from flask_wtf.csrf import CSRFProtect
from utils.extensions import db, login_manager, mail
from config import Config
from models import User  # Import models needed for init_db
import os
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Set FOOD_SERVICE_IPV4 from .env
    app.config['FOOD_SERVICE_IPV4'] = os.getenv('FOOD_SERVICE_IPV4')  # <-- add this
    
    # Configure session - using Flask's built-in session
    app.secret_key = app.config.get('SECRET_KEY', 'your_secret_key_here')
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Production settings
    if app.config.get('DATABASE_URL'):
        # Production settings for Render
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    else:
        # Development settings
        app.config['DEBUG'] = True
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'room_images')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    mail.init_app(app)
    csrf = CSRFProtect(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

app = create_app()

# Import routes after app is created to avoid circular imports
from blueprints.routes import *

if __name__ == '__main__':
    # Only run with debug=True in development
    debug_mode = not app.config.get('DATABASE_URL', False)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)