"""API routes."""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them
from app.routes import room_routes, team_routes, player_routes, auction_routes
