"""Minimal Flask API for Vercel - Auth only."""
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
    """Create minimal Flask app for Vercel."""
    app = Flask(__name__)
    
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
    
    # Register only auth blueprint
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'AgriSensa Auth API is running',
            'endpoints': {
                'login': '/api/auth/simple-login',
                'register': '/api/auth/simple-register',
                'activities': '/api/auth/activities',
                'users': '/api/auth/users-list'
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
