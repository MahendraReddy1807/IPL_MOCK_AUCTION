"""Team-related API routes."""
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app.routes import api_bp
from app.services.team_service import configure_team as configure_team_service
from app.models.room import Room


UPLOAD_FOLDER = 'backend/uploads/logos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/teams/configure', methods=['POST'])
def configure_team():
    """Configure team details."""
    try:
        data = request.get_json()
        room_code = data.get('room_code')
        username = data.get('username')
        team_name = data.get('team_name')
        logo_url = data.get('logo_url', '')
        purse = data.get('purse')
        
        if not room_code:
            return jsonify({
                'error': True,
                'message': 'Room code is required',
                'code': 'MISSING_ROOM_CODE'
            }), 400
        
        if not username:
            return jsonify({
                'error': True,
                'message': 'Username is required',
                'code': 'MISSING_USERNAME'
            }), 400
        
        if not team_name or not team_name.strip():
            return jsonify({
                'error': True,
                'message': 'Team name cannot be empty',
                'code': 'INVALID_TEAM_NAME'
            }), 400
        
        if purse is None or purse <= 0:
            return jsonify({
                'error': True,
                'message': 'Purse must be a positive number',
                'code': 'INVALID_PURSE'
            }), 400
        
        # Get room
        room = Room.query.filter_by(code=room_code).first()
        if not room:
            return jsonify({
                'error': True,
                'message': 'Room not found',
                'code': 'ROOM_NOT_FOUND'
            }), 404
        
        # Configure team
        success, message, team = configure_team_service(room.id, username, team_name, purse, logo_url)
        
        if not success:
            return jsonify({
                'error': True,
                'message': message,
                'code': 'CONFIGURATION_FAILED'
            }), 400
        
        return jsonify({
            'success': True,
            'team_id': team.id,
            'team_name': team.team_name,
            'logo_url': team.logo_url,
            'purse': team.initial_purse
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500


@api_bp.route('/teams/upload-logo', methods=['POST'])
def upload_logo():
    """Upload team logo."""
    try:
        if 'logo' not in request.files:
            return jsonify({
                'error': True,
                'message': 'No file provided',
                'code': 'NO_FILE'
            }), 400
        
        file = request.files['logo']
        
        if file.filename == '':
            return jsonify({
                'error': True,
                'message': 'No file selected',
                'code': 'NO_FILE_SELECTED'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': True,
                'message': 'Invalid file type. Allowed: png, jpg, jpeg, gif',
                'code': 'INVALID_FILE_TYPE'
            }), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Return URL
        logo_url = f'/uploads/logos/{filename}'
        
        return jsonify({
            'success': True,
            'logo_url': logo_url
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e),
            'code': 'SERVER_ERROR'
        }), 500
