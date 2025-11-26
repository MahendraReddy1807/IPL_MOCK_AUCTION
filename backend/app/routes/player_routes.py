"""Player-related API routes."""
from flask import jsonify
from app.routes import api_bp
from app.models.player import Player


@api_bp.route('/players', methods=['GET'])
def get_players():
    """Get all players."""
    try:
        players = Player.query.all()
        
        return jsonify({
            'players': [{
                'id': p.id,
                'name': p.name,
                'role': p.role,
                'country': p.country,
                'base_price': p.base_price,
                'batting_score': p.batting_score,
                'bowling_score': p.bowling_score,
                'overall_score': p.overall_score,
                'is_overseas': p.is_overseas
            } for p in players]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500
