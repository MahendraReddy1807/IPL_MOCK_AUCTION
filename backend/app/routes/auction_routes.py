"""Auction-related API routes."""
from flask import jsonify
from app.routes import api_bp
from app.services.auction_service import get_current_auction_state
from app.services.ai_service import determine_winner
from app.models.room import Room
from app.models.team import Team
from app.models.team_player import TeamPlayer
from app.models.player import Player
from app.models.team_rating import TeamRating


@api_bp.route('/auction/<room_code>/state', methods=['GET'])
def get_auction_state(room_code):
    """Get current auction state."""
    try:
        state = get_current_auction_state(room_code)
        
        player_data = None
        if state.current_player:
            player_data = {
                'id': state.current_player.id,
                'name': state.current_player.name,
                'role': state.current_player.role,
                'country': state.current_player.country,
                'base_price': state.current_player.base_price,
                'batting_score': state.current_player.batting_score,
                'bowling_score': state.current_player.bowling_score,
                'overall_score': state.current_player.overall_score,
                'is_overseas': state.current_player.is_overseas
            }
        
        # Get teams data for the room
        room = Room.query.filter_by(code=room_code).first()
        teams_data = []
        if room:
            teams = Team.query.filter_by(room_id=room.id).all()
            for team in teams:
                # Count squad size
                squad_size = TeamPlayer.query.filter_by(team_id=team.id).count()
                teams_data.append({
                    'team_id': team.id,
                    'team_name': team.team_name,
                    'logo_url': team.logo_url,
                    'username': team.username,
                    'initial_purse': team.initial_purse,
                    'purse_left': team.purse_left,
                    'squad_size': squad_size
                })
        
        return jsonify({
            'room_code': state.room_code,
            'current_player': player_data,
            'current_bid': state.current_bid,
            'highest_bidder': state.highest_bidder,
            'timer_remaining': state.timer_remaining,
            'auction_complete': state.auction_complete,
            'teams': teams_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500


@api_bp.route('/results/<room_code>', methods=['GET'])
def get_results(room_code):
    """Get auction results."""
    try:
        room = Room.query.filter_by(code=room_code).first()
        
        if not room:
            return jsonify({
                'error': True,
                'message': 'Room not found',
                'code': 'ROOM_NOT_FOUND'
            }), 404
        
        # Get all teams in the room
        teams = Team.query.filter_by(room_id=room.id).all()
        
        teams_data = []
        for team in teams:
            # Get team players
            team_players = TeamPlayer.query.filter_by(team_id=team.id).all()
            
            # Get playing XI
            playing_xi = []
            impact_player = None
            bench = []
            
            for tp in team_players:
                player = Player.query.get(tp.player_id)
                player_data = {
                    'id': player.id,
                    'name': player.name,
                    'role': player.role,
                    'country': player.country,
                    'overall_score': player.overall_score,
                    'price': tp.price
                }
                
                if tp.in_playing_xi:
                    playing_xi.append(player_data)
                else:
                    bench.append(player_data)
                
                if tp.is_impact_player:
                    impact_player = player_data
            
            # Get team rating
            team_rating = TeamRating.query.filter_by(team_id=team.id).first()
            rating_data = None
            if team_rating:
                rating_data = {
                    'overall_rating': team_rating.overall_rating,
                    'batting_rating': team_rating.batting_rating,
                    'bowling_rating': team_rating.bowling_rating,
                    'balance_score': team_rating.balance_score,
                    'bench_depth': team_rating.bench_depth,
                    'role_coverage': team_rating.role_coverage
                }
            
            teams_data.append({
                'team_id': team.id,
                'team_name': team.team_name,
                'logo_url': team.logo_url,
                'username': team.username,
                'purse_left': team.purse_left,
                'squad': playing_xi + bench,
                'playing_xi': playing_xi,
                'bench': bench,
                'impact_player': impact_player,
                'rating': rating_data
            })
        
        # Determine winner
        winner = determine_winner(room_code)
        winner_data = None
        if winner:
            winner_data = {
                'team_id': winner.id,
                'team_name': winner.team_name,
                'username': winner.username
            }
        
        return jsonify({
            'room_code': room_code,
            'teams': teams_data,
            'winner': winner_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500
