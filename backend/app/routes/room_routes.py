"""Room-related API routes."""
from flask import request, jsonify
from app.routes import api_bp
from app.services.room_service import create_room as create_room_service, join_room as join_room_service, get_room_participants
from app.models.room import Room
from app.models.simple_user import User


@api_bp.route('/rooms/create', methods=['POST'])
def create_room():
    """Create a new auction room."""
    try:
        data = request.get_json()
        host_username = data.get('host_username')
        
        if not host_username or not host_username.strip():
            return jsonify({
                'error': True,
                'message': 'Username cannot be empty',
                'code': 'INVALID_USERNAME'
            }), 400
        
        # Create room
        room = create_room_service(host_username)
        
        return jsonify({
            'success': True,
            'room_code': room.code,
            'host_username': host_username,
            'status': room.status
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500


@api_bp.route('/rooms/join', methods=['POST'])
def join_room():
    """Join an existing auction room."""
    try:
        data = request.get_json()
        room_code = data.get('room_code')
        username = data.get('username')
        
        if not room_code:
            return jsonify({
                'error': True,
                'message': 'Room code is required',
                'code': 'MISSING_ROOM_CODE'
            }), 400
        
        if not username or not username.strip():
            return jsonify({
                'error': True,
                'message': 'Username cannot be empty',
                'code': 'INVALID_USERNAME'
            }), 400
        
        # Join room
        success, message, user = join_room_service(room_code, username)
        
        if not success:
            return jsonify({
                'error': True,
                'message': message,
                'code': 'JOIN_FAILED'
            }), 400
        
        # Get room details
        room = Room.query.filter_by(code=room_code).first()
        participants = get_room_participants(room_code)
        
        return jsonify({
            'success': True,
            'room_code': room_code,
            'username': username,
            'status': room.status,
            'participants': [p.username for p in participants]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500


@api_bp.route('/rooms/<code>', methods=['GET'])
def get_room(code):
    """Get room details."""
    try:
        room = Room.query.filter_by(code=code).first()
        
        if not room:
            return jsonify({
                'error': True,
                'message': 'Room not found',
                'code': 'ROOM_NOT_FOUND'
            }), 404
        
        participants = get_room_participants(code)
        
        return jsonify({
            'room_code': room.code,
            'status': room.status,
            'host_username': room.host_username,
            'min_users': room.min_users,
            'max_users': room.max_users,
            'participants': [p.username for p in participants],
            'participant_count': len(participants)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500
