"""Team management service."""
import os
from werkzeug.utils import secure_filename
from app import db
from app.models.team import Team
from app.models.team_player import TeamPlayer
from app.models.player import Player


def configure_team(room_id, username, team_name, purse, logo_url=None):
    """
    Configure team details for a user in a room.
    
    Args:
        room_id: ID of the room
        username: Username of the team owner
        team_name: Name of the team
        purse: Starting purse amount
        logo_url: Optional URL/path to team logo
        
    Returns:
        tuple: (success: bool, message: str, team: Team or None)
    """
    # Validate team name
    if not team_name or not team_name.strip():
        return False, "Team name cannot be empty", None
    
    # Validate purse amount
    if not isinstance(purse, (int, float)) or purse <= 0:
        return False, "Purse must be a positive number", None
    
    # Check if team already exists for this user in this room
    existing_team = Team.query.filter_by(room_id=room_id, username=username).first()
    if existing_team:
        # Update existing team
        existing_team.team_name = team_name.strip()
        existing_team.logo_url = logo_url
        existing_team.initial_purse = purse
        existing_team.purse_left = purse
        db.session.commit()
        return True, "Team updated successfully", existing_team
    
    # Create new team
    team = Team(
        room_id=room_id,
        username=username,
        team_name=team_name.strip(),
        logo_url=logo_url,
        initial_purse=purse,
        purse_left=purse
    )
    
    db.session.add(team)
    db.session.commit()
    
    return True, "Team configured successfully", team


def upload_logo(file, upload_folder='uploads/logos'):
    """
    Upload and store team logo file.
    
    Args:
        file: File object from request
        upload_folder: Directory to store uploaded files
        
    Returns:
        tuple: (success: bool, message: str, file_path: str or None)
    """
    if not file:
        return False, "No file provided", None
    
    # Validate file has a filename
    if file.filename == '':
        return False, "No file selected", None
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create upload directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename to avoid collisions
    import uuid
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    try:
        # Save file
        file.save(file_path)
        return True, "Logo uploaded successfully", file_path
    except Exception as e:
        return False, f"Failed to upload logo: {str(e)}", None


def update_purse(team_id, amount):
    """
    Update team's remaining purse.
    
    Args:
        team_id: ID of the team
        amount: New purse amount
        
    Returns:
        tuple: (success: bool, message: str, team: Team or None)
    """
    team = Team.query.get(team_id)
    if not team:
        return False, "Team not found", None
    
    # Validate amount
    if not isinstance(amount, (int, float)) or amount < 0:
        return False, "Purse amount must be non-negative", None
    
    team.purse_left = amount
    db.session.commit()
    
    return True, "Purse updated successfully", team


def add_player_to_team(team_id, player_id, price):
    """
    Add a player to a team's squad.
    
    Args:
        team_id: ID of the team
        player_id: ID of the player
        price: Purchase price of the player
        
    Returns:
        tuple: (success: bool, message: str, team_player: TeamPlayer or None)
    """
    # Verify team exists
    team = Team.query.get(team_id)
    if not team:
        return False, "Team not found", None
    
    # Verify player exists
    player = Player.query.get(player_id)
    if not player:
        return False, "Player not found", None
    
    # Check if player already in team
    existing = TeamPlayer.query.filter_by(team_id=team_id, player_id=player_id).first()
    if existing:
        return False, "Player already in team", None
    
    # Create team player record
    team_player = TeamPlayer(
        team_id=team_id,
        player_id=player_id,
        price=price
    )
    
    db.session.add(team_player)
    
    # Deduct from purse
    team.purse_left -= price
    
    db.session.commit()
    
    return True, "Player added to team successfully", team_player


def get_team_squad(team_id):
    """
    Get all players in a team's squad.
    
    Args:
        team_id: ID of the team
        
    Returns:
        list: List of Player objects
    """
    team = Team.query.get(team_id)
    if not team:
        return []
    
    # Get all team players
    team_players = TeamPlayer.query.filter_by(team_id=team_id).all()
    
    # Extract player objects
    players = [tp.player for tp in team_players]
    
    return players
