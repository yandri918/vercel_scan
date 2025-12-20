"""Minimal Flask API for Vercel - Auth + Product Passport."""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


def create_app():
    """Create Flask app for Vercel."""
    # Set template folder
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app = Flask(__name__, template_folder=template_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.product import product_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp)
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'AgriSensa API is running',
            'endpoints': {
                'login': '/api/auth/simple-login',
                'register': '/api/auth/simple-register',
                'activities': '/api/auth/activities',
                'product': '/product/<batch_id>'
            }
        })
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})
    
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database initialized")
        except Exception as e:
            app.logger.warning(f"Database init failed: {e}")
    
    return app
