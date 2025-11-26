"""Flask application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register socket events
    from app.events import socket_events

    # Import core models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from app.models import room, team, player, auction_player, team_rating, simple_user
        # Note: Additional models (user, achievement, trade, tournament, alliance, 
        # notification, auction_history) are available but not imported by default
        # to avoid relationship conflicts with the core spec models
        db.create_all()

    return app
